from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, cast

from mods_base import ENGINE, build_mod, get_pc, hook
from networking import add_network_functions
from networking.decorators import host, targeted
from unrealsdk import find_enum, unreal
from unrealsdk.unreal import WeakPointer

from tweens import (
    Tween,
    circ_out,
    cubic_in_out,
    cubic_out,
    elastic_out,
    quad_out,
)
from uemath import Vector

if TYPE_CHECKING:
    from common import WillowGameEngine, WillowPlayerController, WillowPlayerPawn, WorldInfo

SLIDE_SPEED_DEFAULT: float = 2.2
CROUCHED_PCT_DEFAULT: float = 0.5


class State:
    do_slide_jump: ClassVar[bool] = False
    tweener: ClassVar[Tween] = Tween()
    horizontal_velocity: ClassVar[Vector] = Vector()


@dataclass
class PlayerSlideState:
    old_z: float
    is_sliding: bool


CLIENTS_SLIDE_STATES: dict[WeakPointer[WillowPlayerController], PlayerSlideState] = {}
OWN_SLIDE_STATE: PlayerSlideState = PlayerSlideState(old_z=0, is_sliding=False)

e_net_mode: WorldInfo.ENetMode = cast("WorldInfo.ENetMode", find_enum("ENetMode"))


def is_client() -> bool:
    return cast("WillowGameEngine", ENGINE).GetCurrentWorldInfo().NetMode == e_net_mode.NM_Client


def tween_slide(pc: WillowPlayerController) -> None:
    if State.tweener.is_running():
        State.tweener.kill()
    arms = pc.Pawn.Arms
    if not arms.Attachments:
        return
    State.tweener = Tween()
    t = State.tweener
    t.tween_property(
        arms.SkeletalMesh.RotOrigin,
        "Pitch",
        final_value=500,
        duration=0.2,
    ).from_current().transition(cubic_in_out)
    t.tween_property(
        arms.SkeletalMesh.RotOrigin,
        "Yaw",
        final_value=-200,
        duration=0.4,
    ).from_current().transition(quad_out)
    t.tween_property(
        arms.SkeletalMesh.RotOrigin,
        "Roll",
        final_value=-6300,
        duration=0.5,
    ).from_current().transition(cubic_out)
    t.tween_property(
        arms.SkeletalMesh.Origin,
        "X",
        final_value=30,
        duration=1.2,
    ).from_current().transition(elastic_out)
    t.tween_property(
        arms.SkeletalMesh.Origin,
        "Y",
        final_value=-14.5,
        duration=0.5,
    ).from_current().transition(circ_out)
    t.tween_property(
        arms.SkeletalMesh.Origin,
        "Z",
        final_value=-175,
        duration=0.5,
    ).from_current().transition(circ_out)
    t.set_parallel(True)
    t.start()


def tween_reset(pc: WillowPlayerController) -> None:
    if State.tweener.is_running():
        State.tweener.kill()
    arms = pc.Pawn.Arms
    if not arms.Attachments:
        return
    State.tweener = Tween()
    t = State.tweener
    State.tweener = Tween()
    t = State.tweener
    t.tween_property(
        arms.SkeletalMesh.RotOrigin,
        "Pitch",
        final_value=0,
        duration=0.5,
    ).from_current().transition(cubic_in_out)
    t.tween_property(
        arms.SkeletalMesh.RotOrigin,
        "Yaw",
        final_value=0,
        duration=0.4,
    ).from_current().transition(quad_out)
    t.tween_property(
        arms.SkeletalMesh.RotOrigin,
        "Roll",
        final_value=0,
        duration=0.3,
    ).from_current().transition(cubic_in_out)
    t.tween_property(
        arms.SkeletalMesh.Origin,
        "X",
        final_value=40,
        duration=0.4,
    ).from_current().transition(circ_out)
    t.tween_property(
        arms.SkeletalMesh.Origin,
        "Y",
        final_value=0,
        duration=0.6,
    ).from_current().transition(circ_out)
    t.tween_property(
        arms.SkeletalMesh.Origin,
        "Z",
        final_value=-167,
        duration=0.5,
    ).from_current().transition(circ_out)
    t.set_parallel(True)
    t.start()


@host.json_message
def server_set_slide_jump_velocity(vel_x: float, vel_y: float) -> None:
    pc = cast("WillowPlayerController", server_set_slide_jump_velocity.sender.Owner)
    pc.Pawn.Velocity.X = vel_x
    pc.Pawn.Velocity.Y = vel_y


@host.message
def server_exit_slide() -> None:
    pc = cast("WillowPlayerController", server_exit_slide.sender.Owner)
    pc.Pawn.CrouchedPct = CROUCHED_PCT_DEFAULT
    for player in CLIENTS_SLIDE_STATES.copy():
        if (_pc := player()) is None:
            CLIENTS_SLIDE_STATES.pop(player)
        elif _pc == pc:
            CLIENTS_SLIDE_STATES[player].is_sliding = False


def exit_slide(pc: WillowPlayerController) -> None:
    if not OWN_SLIDE_STATE.is_sliding:
        return
    OWN_SLIDE_STATE.is_sliding = False
    pc.Pawn.CrouchedPct = CROUCHED_PCT_DEFAULT
    server_exit_slide()
    tween_reset(pc)


@targeted.message
def client_exit_slide() -> None:
    exit_slide(cast("WillowPlayerController", get_pc()))


@host.message
def server_enter_slide() -> None:
    pc = cast("WillowPlayerController", server_enter_slide.sender.Owner)

    for player in CLIENTS_SLIDE_STATES.copy():
        if (_pc := player()) is None:
            CLIENTS_SLIDE_STATES.pop(player)
        elif _pc == pc:
            data = CLIENTS_SLIDE_STATES[player]
            data.is_sliding = True
            data.old_z = pc.Pawn.Location.Z
            break
    else:
        CLIENTS_SLIDE_STATES[unreal.WeakPointer(pc)] = PlayerSlideState(
            old_z=pc.Pawn.Location.Z,
            is_sliding=True,
        )

    pc.Pawn.CrouchedPct = SLIDE_SPEED_DEFAULT


def enter_slide(pc: WillowPlayerController) -> None:
    """The client wants to slide, sends the request to the server but can already start the vfx"""
    if OWN_SLIDE_STATE.is_sliding:
        return
    server_enter_slide()
    OWN_SLIDE_STATE.is_sliding = True
    OWN_SLIDE_STATE.old_z = pc.Pawn.Location.Z
    pc.Pawn.CrouchedPct = SLIDE_SPEED_DEFAULT
    tween_slide(pc)


def slide(
    pc: WillowPlayerController,
    slide_data: PlayerSlideState,
    delta_time: float,
) -> None:
    """Calculate the new speed of the player, has to be called every frame. Server Side only!"""
    # z_diff is the height difference between the current frame and the last frame in cm (Unreal units)
    z_diff: float = pc.Pawn.Location.Z - slide_data.old_z
    speed = pc.Pawn.CrouchedPct
    # We generally want to slow down over time, but if we are going up a slope, we want to slow down even more
    # Slididng down a slope should slightly increase the speed
    if z_diff < 0:  # We are going down a slope
        speed -= z_diff * 0.0005
    else:  # We are going up a slope or on flat ground
        speed -= delta_time * 0.7 + z_diff * 0.004

    slide_data.old_z = pc.Pawn.Location.Z
    pc.Pawn.CrouchedPct = speed
    if pc.pawn.CrouchedPct < CROUCHED_PCT_DEFAULT:
        client_exit_slide(pc.PlayerReplicationInfo)


def can_slide(pc: WillowPlayerController, pawn: WillowPlayerPawn) -> bool:
    accel = pawn.Acceleration
    return (
        OWN_SLIDE_STATE.is_sliding and bool(pc.bDuck) and pawn.IsOnGroundOrShortFall() and not (accel.X == 0.0 and accel.Y == 0.0)
    )


@hook("WillowGame.WillowPlayerInput:Jump")
def jump(
    obj: unreal.UObject,
    _args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    """If the client is sliding and wants to jump he stores his horizontal velocity and passes it later to the server"""
    if OWN_SLIDE_STATE.is_sliding:
        pc = cast("WillowPlayerController", obj.Outer)
        vel: Vector = Vector(pc.Pawn.Velocity)
        vel.z = 0
        State.horizontal_velocity = vel
        State.do_slide_jump = True


@hook("WillowGame.WillowPlayerController:PlayerWalking.PlayerMove")
def handle_move(
    obj: unreal.UObject,
    args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    pc = cast("WillowPlayerController", obj)
    pawn = cast("WillowPlayerPawn", pc.Pawn)

    # We most likely wont pass our slide exit conditions after pressing jump,
    # as that will cause the player to stand up
    # So we need to do the slide jump as one of the first things.
    if State.do_slide_jump:
        if pawn.IsOnGroundOrShortFall():
            pawn.DoJump(True)
        else:
            server_set_slide_jump_velocity(State.horizontal_velocity.x, State.horizontal_velocity.y)
            State.do_slide_jump = False
            return

    # Check our exit conditions
    if not can_slide(pc, pawn):
        exit_slide(pc)
        return

    if not is_client():
        # We are sliding
        for player in CLIENTS_SLIDE_STATES.copy():
            if (_pc := player()) is None:
                CLIENTS_SLIDE_STATES.pop(player)
            else:
                slide(_pc, CLIENTS_SLIDE_STATES[player], args.DeltaTime)
    else:
        slide(pc, OWN_SLIDE_STATE, args.DeltaTime)

    # After actually sliding, check if we are still fast enough to slide
    if pawn.CrouchedPct < CROUCHED_PCT_DEFAULT:
        exit_slide(pc)


@hook("WillowGame.WillowPlayerInput:DuckPressed")
def handle_duck(
    obj: unreal.UObject,
    _args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    """The Client should check itself if he wants to slide"""
    pc = cast("WillowPlayerController", obj.Outer)
    if pc.bInSprintState:
        enter_slide(pc)


mod = build_mod(
    hooks=[
        handle_move,
        handle_duck,
        jump,
    ],
)

add_network_functions(mod)
