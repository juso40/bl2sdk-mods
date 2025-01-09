from typing import Any, ClassVar

import unrealsdk
from mods_base import ENGINE, get_pc
from unrealsdk import unreal

BLACKLIST = [
    "bugmorph",
    "snowminion",
]


class GloryKill:
    HEALTH_THRESHOLD = 0.15  # less than 15% health required to be in glory kill state
    GLORY_KILL_AK_EVENT1 = "Ake_UI.UI_Shields.Ak_Play_UI_Shield_Roid_Buff_Hit"
    GLORY_KILL_AK_EVENT2 = "Ake_UI.UI_HUD.Ak_Play_UI_PVP_Duel_End"
    GLORY_KILL_MARKER1 = "FX_GOR_Particles.Particles.DeathFX.Part_FireDeath_Small"
    GLORY_KILL_MARKER2 = "FX_GOR_Particles.Particles.DeathFX.Part_ShockDeath_Large"
    GLORY_KILL_KILLED_PARTICLE = "FX_WEP_Explosions.Particles.Default.Part_ExplosiveExplosion_Small"
    glory_killed: ClassVar = set()
    glory_kill_state: ClassVar = {}


def get_emitter_pool() -> unreal.UObject:
    return ENGINE.GetCurrentWorldInfo().MyEmitterPool


def check_glory_kill_state(pawn: unreal.UObject) -> bool:
    if (
        pawn.GetHealth() > 0
        and pawn.GetMaxHealth() > 0
        and (pawn.GetHealth() / pawn.GetMaxHealth()) < GloryKill.HEALTH_THRESHOLD
    ):
        pawn_path_name = pawn.PathName(pawn)
        GloryKill.glory_kill_state.setdefault(pawn_path_name, 5)  # Stay 5 seconds in glory kill state
        return GloryKill.glory_kill_state[pawn_path_name] > 0  # Only first 5 seconds in glory kill state
    return False


def on_take_damage(
    obj: unreal.UObject,
    args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    if not check_glory_kill_state(obj):
        return

    pc = get_pc()
    instigator = args.InstigatedBy
    # We only allow Melee damage to kill Pawns in glory kill state
    if not (instigator == pc and "melee" in args.DamageType.Name.lower()):
        return

    # Store the location the Pawn was hit
    hit_loc = args.HitLocation
    hit_loc = (hit_loc.X, hit_loc.Y, hit_loc.Z)

    # Spawn the glory killed particle to the hit location
    get_emitter_pool().SpawnEmitter(
        unrealsdk.find_object("ParticleSystem", GloryKill.GLORY_KILL_KILLED_PARTICLE),
        hit_loc,
    )

    # Add the sound effects
    instigator = args.InstigatedBy
    instigator.PlayAkEvent(unrealsdk.find_object("AkEvent", GloryKill.GLORY_KILL_AK_EVENT1))
    instigator.PlayAkEvent(unrealsdk.find_object("AkEvent", GloryKill.GLORY_KILL_AK_EVENT2))

    # The instigator gains all it's health back for this glory kill.
    if instigator.Pawn:
        instigator.Pawn.SetHealth(instigator.Pawn.GetMaxHealth())

    # Add the killed Pawn to the set of killed Pawns to later increase the dropped loot.
    GloryKill.glory_killed.add(obj.PathName(obj))
    # Set health of Pawn to 1 to kill him with melee damage and not cause soft locks.
    obj.SetHealth(1)
    obj.SetShieldStrength(0)
    return


def enter_glory_kill_state(
    obj: unreal.UObject,
    _args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    if not check_glory_kill_state(obj.MyWillowPawn):
        return

    # Don't allow glory kills on blacklisted enemies
    enemy_name = obj.PathName(obj.MyWillowPawn.AIClass).lower()
    for blacklisted in BLACKLIST:
        if blacklisted in enemy_name:
            return

    get_emitter_pool().SpawnEmitterMeshAttachment(
        unrealsdk.find_object("ParticleSystem", GloryKill.GLORY_KILL_MARKER1),
        obj.MyWillowPawn.Mesh,
        "root",
    )
    get_emitter_pool.SpawnEmitterMeshAttachment(
        unrealsdk.find_object("ParticleSystem", GloryKill.GLORY_KILL_MARKER2),
        obj.MyWillowPawn.Mesh,
        "root",
    )


def drop_loot_on_death(
    obj: unreal.UObject,
    args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    try:
        GloryKill.glory_killed.remove(obj.PathName(obj))
        # Only drop additional loot if the Pawn got glory killed
        for _ in range(4):
            obj.DropLootOnDeath(args.Killer, args.DamageType, args.DamageTypeDefinition)
    except KeyError:
        pass


def tick_glory_states(
    _obj: unreal.UObject,
    args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    # Enemies will stay 5 seconds in glory kill state and then are immune to glory kills for 10 seconds
    for p, t in list(GloryKill.glory_kill_state.items()):
        GloryKill.glory_kill_state[p] = t - args.DeltaTime  # Decrease the glory kill state timer
        if t < -10:  # 10 seconds immunity to glory kill state
            del GloryKill.glory_kill_state[p]  # Remove if time is up


def enable() -> None:
    unrealsdk.hooks.add_hook(
        "WillowGame.WillowAIPawn:TakeDamage",
        unrealsdk.hooks.Type.PRE,
        "GloryKillTakeDamage",
        on_take_damage,
    )
    unrealsdk.hooks.add_hook(
        "WillowGame.WillowMind:NotifyAttackedBy",
        unrealsdk.hooks.Type.PRE,
        "GloryKillState",
        enter_glory_kill_state,
    )
    unrealsdk.hooks.add_hook(
        "WillowGame.WillowPawn:DropLootOnDeath",
        unrealsdk.hooks.Type.PRE,
        "GloryKillLoot",
        drop_loot_on_death,
    )
    unrealsdk.hooks.add_hook(
        "WillowGame.WillowPlayerController:PlayerTick",
        unrealsdk.hooks.Type.POST_UNCONDITIONAL,
        "GloryKillStateTick",
        tick_glory_states,
    )


def disable() -> None:
    unrealsdk.hooks.remove_hook(
        "WillowGame.WillowAIPawn:TakeDamage",
        unrealsdk.hooks.Type.PRE,
        "GloryKillTakeDamage",
    )
    unrealsdk.hooks.remove_hook(
        "WillowGame.WillowMind.NotifyAttackedBy",
        unrealsdk.hooks.Type.PRE,
        "GloryKillState",
    )
    unrealsdk.hooks.remove_hook(
        "WillowGame.WillowPawn.DropLootOnDeath",
        unrealsdk.hooks.Type.PRE,
        "GloryKillLoot",
    )
    unrealsdk.hooks.remove_hook(
        "WillowGame.WillowPlayerController.PlayerTick",
        unrealsdk.hooks.Type.POST_UNCONDITIONAL,
        "GloryKillStateTick",
    )
