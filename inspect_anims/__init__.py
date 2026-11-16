from typing import TYPE_CHECKING, Any, cast

from mods_base import build_mod, get_pc, hook, keybind
from unrealsdk import hooks

from animlib import AnimationNotify, AnimationSequence, AnimationSet, NotifyContext

from .inspects import cancel_inspect, inspect_for_weapon, loaded_animations

if TYPE_CHECKING:
    from common import WillowPlayerController, WillowWeapon
    from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct

__all__ = ["AnimationNotify", "AnimationSequence", "AnimationSet", "NotifyContext"]


@hook("WillowGame.WillowWeapon:PlayReloadAnim", hook_type=hooks.Type.PRE)
@hook("WillowGame.WillowWeapon:PlayWeaponEquip", hook_type=hooks.Type.PRE)
@hook("WillowGame.WillowWeapon:PlayWeaponPutDown", hook_type=hooks.Type.PRE)
@hook("WillowGame.WillowPlayerController:StartFire", hook_type=hooks.Type.PRE)
@hook("WillowGame.WillowPlayerController:MeleeAttack", hook_type=hooks.Type.PRE)
@hook("WillowGame.WillowPlayerController:Behavior_Melee", hook_type=hooks.Type.PRE)
@hook("WillowGame.WillowPlayerController:StartActionSkill", hook_type=hooks.Type.PRE)
@hook("WillowGame.WillowPlayerController:ClientThrowGrenade", hook_type=hooks.Type.PRE)
def _stop_inspect(
    _obj: UObject,
    _args: WrappedStruct,
    _ret: Any,
    _func: BoundFunction,
) -> None:
    cancel_inspect(blend_out=0.15)


@keybind("Inspect weapon", "B")
def play_inspect() -> None:
    pc = cast("WillowPlayerController | None", get_pc())
    if pc is None:
        return
    pawn = pc.GetWillowPlayerPawn()
    if pawn is None or not pawn.IsFirstPerson():
        return
    arms = pawn.Arms
    if arms is None or arms.SkeletalMesh is None:
        return
    slot = arms.FindAnimNode("CustomAnimSlot")
    if slot is None or slot.bIsPlayingCustomAnim:
        return
    inspect_for_weapon(pawn, cast("WillowWeapon|None", pawn.Weapon))


def on_disable() -> None:
    animations = loaded_animations()
    pc = cast("WillowPlayerController | None", get_pc())
    if animations is None or pc is None:
        return
    pawn = pc.GetWillowPlayerPawn()
    if pawn is None or pawn.Arms is None:
        return
    for sequence in animations.sequences.values():
        sequence.stop_arms(pawn, blend_out=0.0)
    animations.detach(pawn.Arms)


mod = build_mod(
    keybinds=[play_inspect],
    hooks=[_stop_inspect],
    on_disable=on_disable,
)
