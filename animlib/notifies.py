import traceback
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Literal, cast

from mods_base import hook
from unrealsdk import find_object, logging
from unrealsdk.hooks import Block, Type

if TYPE_CHECKING:
    from common import Actor, AnimNodeSequence, AnimNotify, AnimNotify_PawnMaterialParam, SkeletalMeshComponent
    from unrealsdk.unreal import BoundFunction

    from .sequence import AnimationSequence

# I really hope I didn't miss any AnimNotify Classes!
type AnimNotifyClass = Literal[
    "AnimNotify",
    "AnimNotify_Sound",
    "AnimNotify_Kismet",
    "AnimNotify_Rumble",
    "AnimNotify_Trails",
    "AnimNotify_Script",
    "AnimNotify_AkEvent",
    "AnimNotify_Footstep",
    "AnimNotify_Scripted",
    "AnimNotify_ViewShake",
    "AnimNotify_ForceField",
    "AnimNotify_CustomEvent",
    "AnimNotify_DialogEvent",
    "AnimNotify_UseBehavior",
    "AnimNotify_CameraEffect",
    "AnimNotify_SoundSpatial",
    "AnimNotify_EnableHandIK",
    "AnimNotify_PlayFaceFXAnim",
    "AnimNotify_EnableHeadLookAt",
    "AnimNotify_PawnMaterialParam",
    "AnimNotify_PlayParticleEffect",
    "AnimNotify_ClothingMaxDistanceScale",
]


@dataclass(frozen=True)
class AnimationNotify:
    """Describe a detached snapshot of one named animation cue."""

    name: str
    time: float
    duration: float
    path: str

    @property
    def unreal(self) -> AnimNotify:
        """Resolve the underlying native AnimNotify object."""
        return cast("AnimNotify", find_object("AnimNotify", self.path))


@dataclass(frozen=True)
class NotifyContext:
    """Describe the sequence, cue and current engine playback invocation."""

    sequence: AnimationSequence
    notify: AnimationNotify
    owner: Actor
    node: AnimNodeSequence

    @property
    def component(self) -> SkeletalMeshComponent:
        """Return the skeletal component evaluating this cue."""
        return self.node.SkelComponent


type NotifyCallback = Callable[[NotifyContext], None]


@dataclass(frozen=True)
class _Callback:
    sequence: AnimationSequence
    name: str
    callback: NotifyCallback


# This concrete script-event marker has no effect when its owned PRE hook blocks it.
CALLBACK_NOTIFY_CLASS: Final = "AnimNotify_PawnMaterialParam"
_callbacks: dict[str, _Callback] = {}


def register_callback(
    notify: AnimationNotify,
    sequence: AnimationSequence,
    callback: NotifyCallback,
) -> None:
    """Associate one owned marker with its Python callback."""
    _callbacks[notify.path] = _Callback(sequence, notify.name, callback)


def unregister_callback(path: str) -> None:
    """Remove a callback when its native notify is removed."""
    _callbacks.pop(path, None)


# The exact hook path narrows the SDK's generic UObject callback signature.
@hook(f"Engine.{CALLBACK_NOTIFY_CLASS}:Notify", Type.PRE)  # pyright: ignore[reportArgumentType]
def notify_hook(
    obj: AnimNotify_PawnMaterialParam,
    args: AnimNotify_PawnMaterialParam.Notify.args,
    _ret: object,
    _func: BoundFunction,
) -> type[Block] | None:
    """Dispatch owned markers while leaving stock material notifies untouched."""
    registration = _callbacks.get(obj._path_name())
    if registration is None:
        return None
    try:
        node = args.AnimSeqInstigator
        if node is not None and node.AnimSeq is not None and node.AnimSeq._path_name() == registration.sequence.path:
            registration.callback(
                NotifyContext(
                    registration.sequence,
                    registration.sequence.get_notify(registration.name),
                    cast("Actor", args.Owner),
                    node,
                ),
            )
    except Exception:  # noqa: BLE001
        logging.error(f"AnimLib: notify callback failed\n{traceback.format_exc()}")
    return Block
