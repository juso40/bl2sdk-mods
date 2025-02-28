from __future__ import annotations

from functools import partial
from math import sqrt
from typing import TYPE_CHECKING, Any, cast

import unrealsdk
from legacy_compat.unrealsdk import KeepAlive
from mods_base import Game, get_pc
from networking.decorators import host, targeted
from unrealsdk import make_struct, unreal
from unrealsdk.unreal import WeakPointer

from coroutines import TickCoroutine, Time, WaitForSeconds, WaitWhile, start_coroutine_tick

if TYPE_CHECKING:
    from common import AkEvent, IScreenParticle, Object, WillowPlayerController


def _wait_for_pawn_on_ground(pc: WeakPointer[WillowPlayerController]) -> bool:
    if _pc := pc():
        return _pc.IsPaused() or _pc.Pawn is None or not _pc.Pawn.IsOnGroundOrShortFall()
    return True


class DashConf:
    DASH_SOUND1: str = "Ake_Wep_SMGs.SMG_Tediore.Ak_Play_Wep_SMG_Tediore_Shot_Release"
    DASH_SOUND2: str = "Ake_Wep_Sniper_Rifle.Sniper_Hyperion.Ak_Play_Wep_Sniper_Hyperion_Reload_Back"

    SCREEN_PARTICLE: str = "FX_INT_Screen.Particles.Char_Assassin.Part_Assassin_Screen_Dash"
    b_dash_particles = True


class DashData:
    first_dash = False
    second_dash = False
    dash_cooldown = 0.0
    dash_duration = 0.0
    dash_dir: tuple[float, float, float] = (0, 0, 0)


PLAYER_DASH_DATA: dict[int, DashData] = {}


def wants_to_dash(
    obj: unreal.UObject,
    _args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    pc = cast("WillowPlayerController", obj.Outer)
    if not pc.Pawn:
        return

    # Only allow dash while in air
    if not pc.Pawn.IsOnGroundOrShortFall():
        server_dash()
    return


@host.message
def server_dash() -> None:
    pc = cast("WillowPlayerController", server_dash.sender.Owner)
    dash(pc)


@targeted.message
def dash_particles() -> None:
    if DashConf.b_dash_particles:
        add_screen_particles(cast("WillowPlayerController", get_pc()))


def dash(pc: WillowPlayerController) -> None:
    pri = pc.PlayerReplicationInfo
    dash_data = PLAYER_DASH_DATA.get(pri.PlayerID)
    if (dash_data := PLAYER_DASH_DATA.get(pri.PlayerID)) is None:
        dash_data = DashData()
        PLAYER_DASH_DATA[pri.PlayerID] = dash_data

    pawn = pc.Pawn
    x, y = pawn.Acceleration.X, pawn.Acceleration.Y
    mag = sqrt(x**2 + y**2)
    if mag == 0:  # No directional input, so don't dash
        return

    def impl() -> None:
        dash_particles(pc.PlayerReplicationInfo)

        pawn.PlayAkEvent(cast("AkEvent", unrealsdk.find_object("AkEvent", DashConf.DASH_SOUND1)))
        pawn.PlayAkEvent(cast("AkEvent", unrealsdk.find_object("AkEvent", DashConf.DASH_SOUND2)))
        dash_data.dash_duration = 0.15
        dash_data.dash_dir = ((x / mag) * 6500, (y / mag) * 6500, 0.0)
        start_coroutine_tick(coroutine_tick_dash(WeakPointer(pc), dash_data))

    if not dash_data.first_dash:  # Dash once
        dash_data.first_dash = True
        dash_data.dash_cooldown = 1.5  # Dash cooldown starts after initial dash
        impl()
        start_coroutine_tick(coroutine_tick_cooldown(WeakPointer(pc), dash_data))
    elif not dash_data.second_dash and dash_data.dash_duration <= 0:  # Dash the second time after first dash is done
        dash_data.second_dash = True
        impl()


def coroutine_tick_cooldown(pc: WeakPointer[WillowPlayerController], dash_data: DashData) -> TickCoroutine:
    yield WaitForSeconds(dash_data.dash_cooldown)  # Wait for dash cooldown
    yield WaitWhile(partial(_wait_for_pawn_on_ground, pc))  # Reset once the player is on ground
    dash_data.dash_cooldown = 0
    dash_data.first_dash = False
    dash_data.second_dash = False
    return None


def coroutine_tick_dash(pc: WeakPointer[WillowPlayerController], dash_data: DashData) -> TickCoroutine:
    while True:
        # Wait for pause menu to close
        yield WaitWhile(lambda: get_pc().IsPaused())
        dash_data.dash_duration -= Time.delta_time
        if not (_pc := pc()):  # the pc is invalid
            return None
        pawn = _pc.Pawn
        x, y, z = dash_data.dash_dir
        pawn.Velocity = cast("Object.Vector", make_struct("Vector", X=x, Y=y, Z=z))

        # Break this coroutine if our dash duration is over
        if dash_data.dash_duration <= 0:
            dash_data.dash_duration = 0
            remove_screen_particles(_pc.PlayerReplicationInfo)
            _x, _y = pawn.Velocity.X, pawn.Velocity.Y
            mag = sqrt(_x**2 + _y**2)
            pawn.Velocity = cast(
                "Object.Vector",
                make_struct(
                    "Vector",
                    X=(_x / mag) * 200,
                    Y=(_y / mag) * 200,
                    Z=-10,
                ),
            )  # Slight Downward velocity because of TPS
            return None


def add_screen_particles(pc: WillowPlayerController) -> None:
    if Game.get_current() == Game.TPS:
        return
    particle_params = cast(
        "IScreenParticle.ScreenParticleInitParams",
        make_struct(
            "ScreenParticleInitParams",
            Template=unrealsdk.find_object("ParticleSystem", DashConf.SCREEN_PARTICLE),
            ScreenParticleModifiers=[],
            TemplateScreenParticleMaterial=None,
            MatParamName="",
            bHideWhenFinished=True,
            ParticleTag="",
            ContentDims=make_struct("Vector2D", X=16, Y=9),
            ParticleDepth=20,
            ScalingMode=4,
            StopParamsOT=make_struct("ScreenParticleParamOverTime"),
            bOnlyOwnerSee=True,
        ),
    )
    pc.ShowScreenParticle(particle_params)


@targeted.message
def remove_screen_particles() -> None:
    if Game.get_current() == Game.TPS:
        return
    if DashConf.b_dash_particles:
        get_pc().HideScreenParticle(unrealsdk.find_object("ParticleSystem", DashConf.SCREEN_PARTICLE), "", False)


def enable() -> None:
    # ToDo: find hook or way to make it work for Krieg in Buzax Rampage mode
    unrealsdk.hooks.add_hook(
        "WillowGame.WillowPlayerInput:SprintPressed",
        unrealsdk.hooks.Type.PRE,
        "EternalDashInput",
        wants_to_dash,
    )
    if Game.get_current() == Game.TPS:
        return
    if DashConf.b_dash_particles:
        unrealsdk.load_package("GD_Assassin_Streaming_SF")
        KeepAlive(unrealsdk.find_object("ParticleSystem", DashConf.SCREEN_PARTICLE))


def disable() -> None:
    unrealsdk.hooks.remove_hook(
        "WillowGame.WillowPlayerInput:SprintPressed",
        unrealsdk.hooks.Type.PRE,
        "EternalDashInput",
    )


def enable_dash_particle(val: bool) -> None:
    DashConf.b_dash_particles = val
    if val:
        unrealsdk.load_package("GD_Assassin_Streaming_SF")
        KeepAlive(unrealsdk.find_object("ParticleSystem", DashConf.SCREEN_PARTICLE))
