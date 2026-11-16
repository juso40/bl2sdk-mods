from mods_base import Library, build_mod

from .animations import AnimationSet
from .notifies import AnimationNotify, NotifyCallback, NotifyContext, notify_hook
from .playback import NodePlayback, Playback, SlotPlayback
from .sequence import AnimationSequence, AnimNotifyClass

__all__ = [
    "AnimNotifyClass",
    "AnimationNotify",
    "AnimationSequence",
    "AnimationSet",
    "NodePlayback",
    "NotifyCallback",
    "NotifyContext",
    "Playback",
    "SlotPlayback",
]


mod = build_mod(cls=Library, hooks=[notify_hook])
