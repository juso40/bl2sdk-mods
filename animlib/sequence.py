import math
from typing import TYPE_CHECKING, cast
from uuid import uuid4

from mods_base import ObjectFlags
from unrealsdk import construct_object, find_object, make_struct

from .notifies import (
    CALLBACK_NOTIFY_CLASS,
    AnimationNotify,
    AnimNotifyClass,
    NotifyCallback,
    register_callback,
    unregister_callback,
)
from .playback import NodePlayback, SlotPlayback, _play_in_slot, _play_on_node

if TYPE_CHECKING:
    from common import (
        AkEvent,
        AnimNodeSequence,
        AnimNodeSlot,
        AnimNotify,
        AnimSequence,
        SkeletalMeshComponent,
        WillowAnimDefinition,
        WillowPawn,
        WillowPlayerPawn,
    )

    from .animations import AnimationSet

    make_anim_notify_event = AnimSequence.AnimNotifyEvent.make_struct
else:
    make_anim_notify_event = make_struct


class AnimationSequence:
    """Wrap one clip belonging to an AnimationSet."""

    def __init__(self, animations: AnimationSet, clip: str, path: str) -> None:
        """Bind the wrapper to one existing child sequence."""
        self.animations = animations
        self.clip = clip
        self.path = path
        self._notify_names: dict[str, str] = {}
        self._body_definitions: dict[tuple[float, float, bool], str] = {}

    @property
    def unreal(self) -> AnimSequence:
        """Resolve the native AnimSequence game object."""
        return cast("AnimSequence", find_object("AnimSequence", self.path))

    @property
    def length(self) -> float:
        """Return the sequence duration in animation-local seconds."""
        return self.unreal.SequenceLength

    @property
    def notifies(self) -> tuple[AnimationNotify, ...]:
        """Return detached snapshots of all nonempty native notify entries."""
        result = []
        for entry in self.unreal.Notifies:
            notify = entry.Notify
            if notify is not None:
                path = notify._path_name()
                result.append(
                    AnimationNotify(
                        self._notify_names.get(path, str(notify.Name)),
                        entry.Time,
                        entry.Duration,
                        path,
                    ),
                )
        return tuple(result)

    def get_notify(self, name: str) -> AnimationNotify:
        """Return a named cue snapshot or raise KeyError when absent."""
        for notify in self.notifies:
            if notify.name == name:
                return notify
        raise KeyError(f"{self.clip!r} has no notify named {name!r}")

    def _copied_entries(self, *, exclude: str | None = None) -> list[AnimSequence.AnimNotifyEvent]:
        return [
            make_anim_notify_event(
                "AnimNotifyEvent",
                Time=entry.Time,
                Notify=entry.Notify,
                Duration=entry.Duration,
            )
            for entry in self.unreal.Notifies
            if entry.Notify is None or entry.Notify._path_name() != exclude
        ]

    def add_notify(
        self,
        name: str,
        time: float,
        notify_class: AnimNotifyClass,
        *,
        duration: float = 0.0,
        **properties: object,
    ) -> AnimationNotify:
        """Construct and insert a native notify configured with Unreal properties.

        Time is animation-local seconds.
        Existing names are refused rather than silently replaced.
        """
        if any(notify.name == name for notify in self.notifies):
            raise ValueError(f"Notify already exists: {name}")
        length = self.length
        if not math.isfinite(time) or not (0.0 <= time < length):
            raise ValueError(f"Notify time must be within [0, {length}) seconds")
        if not math.isfinite(duration) or duration < 0.0 or time + duration > length:
            raise ValueError("Notify duration must be nonnegative and remain within the sequence")
        sequence = self.unreal
        notify = cast(
            "AnimNotify",
            construct_object(
                cls=notify_class,
                outer=sequence,
                name=f"AnimNotify_{uuid4().hex}",
                flags=ObjectFlags.ALLOW_CROSS_PACKAGE_REFERENCES,
            ),
        )
        if notify is None:
            raise RuntimeError(f"Could not construct {notify_class}")
        for key, value in properties.items():
            setattr(notify, key, value)
        entries = self._copied_entries()
        entries.append(
            make_anim_notify_event(
                "AnimNotifyEvent",
                Time=time,
                Notify=notify,
                Duration=duration,
            ),
        )
        entries.sort(key=lambda entry: entry.Time)
        sequence.Notifies = entries
        path = notify._path_name()
        self._notify_names[path] = name
        return AnimationNotify(name, time, duration, path)

    def add_ak_event(
        self,
        name: str,
        time: float,
        event: str | AkEvent,
        *,
        bone: str = "None",
        follow_actor: bool = True,
    ) -> AnimationNotify:
        """Add a native AkEvent cue using an already loaded event or its exact path."""
        if isinstance(event, str):
            event = cast("AkEvent", find_object("AkEvent", event))
        return self.add_notify(
            name,
            time,
            "AnimNotify_AkEvent",
            AkEvent=event,
            BoneName=bone,
            bFollowActor=follow_actor,
        )

    def on_notify(self, name: str, time: float, callback: NotifyCallback) -> AnimationNotify:
        """Add a notify callback back to python."""
        notify = self.add_notify(
            name,
            time,
            CALLBACK_NOTIFY_CLASS,
            ScalarParameterInterpArray=[],
        )
        register_callback(notify, self, callback)
        return notify

    def remove_notify(self, name: str) -> None:
        """Remove one named native entry and its Python callback registration."""
        notify = self.get_notify(name)
        self.unreal.Notifies = self._copied_entries(exclude=notify.path)
        unregister_callback(notify.path)
        self._notify_names.pop(notify.path, None)

    def clear_notifies(self) -> None:
        """Remove all native entries and callback registrations from this sequence."""
        notifies = self.notifies
        self.unreal.Notifies = []
        for path in self._notify_names.keys() | {notify.path for notify in notifies}:
            unregister_callback(path)
        self._notify_names.clear()

    def play_on_node(  # noqa: PLR0913
        self,
        component: SkeletalMeshComponent,
        node: str | AnimNodeSequence,
        *,
        rate: float = 1.0,
        loop: bool = False,
        start_time: float = 0.0,
        override: bool = False,
    ) -> NodePlayback | None:
        """Play on an existing sequence node and return a weak playback handle.

        A unique node name or a live native node selects the target. Busy nodes
        return None unless override is enabled. Graph weights remain unchanged.
        """
        return _play_on_node(
            self,
            component,
            node,
            rate=rate,
            loop=loop,
            start_time=start_time,
            override=override,
        )

    def play_in_slot(  # noqa: PLR0913
        self,
        component: SkeletalMeshComponent,
        slot: str | AnimNodeSlot,
        *,
        rate: float = 1.0,
        blend_in: float = 0.25,
        blend_out: float = 0.25,
        loop: bool = False,
        override: bool = False,
    ) -> SlotPlayback | None:
        """Play in an existing ordinary slot and return a weak playback handle.

        A unique slot name or a live native slot selects the target. Special-move
        slots require their native lifecycle API instead of this generic path.
        """
        return _play_in_slot(
            self,
            component,
            slot,
            rate=rate,
            blend_in=blend_in,
            blend_out=blend_out,
            loop=loop,
            override=override,
        )

    def play_arms(  # noqa: PLR0913
        self,
        pawn: WillowPlayerPawn,
        *,
        rate: float = 1.0,
        blend_in: float = 0.25,
        blend_out: float = 0.25,
        loop: bool = False,
        override: bool = False,
    ) -> float:
        """Attach the owning set and play through the pawn's first-person custom slot.

        Return the animations duration result. Zero means playback was refused.
        """
        arms = pawn.Arms
        if arms is None:
            raise ValueError("The pawn has no first-person arms")
        self.animations.attach(arms)
        return pawn.PlayArmAnimation(
            self.unreal.SequenceName,
            Rate=rate,
            BlendInTime=blend_in,
            BlendOutTime=blend_out,
            bLoop=loop,
            bOverride=override,
        )

    def stop_arms(self, pawn: WillowPlayerPawn, *, blend_out: float = 0.25) -> bool:
        """Stop this sequence only when it occupies the first-person custom slot."""
        arms = pawn.Arms
        if arms is None:
            return False
        slot = cast("AnimNodeSlot | None", arms.FindAnimNode("CustomAnimSlot"))
        if slot is None:
            return False
        node = slot.GetCustomAnimNodeSeq()
        if node is None or node.AnimSeq is None or node.AnimSeq._path_name() != self.path:
            return False
        slot.StopCustomAnim(blend_out)
        return True

    def _body_definition(self, *, blend_in: float, blend_out: float, loop: bool) -> WillowAnimDefinition:
        key = (blend_in, blend_out, loop)
        if key in self._body_definitions:
            return cast("WillowAnimDefinition", find_object("WillowAnimDefinition", self._body_definitions[key]))
        definition = cast(
            "WillowAnimDefinition",
            construct_object(
                cls="WillowGame.WillowAnimDefinition",
                outer=find_object("Package", "Transient"),
                name=f"AnimLib_Body_{uuid4().hex}",
                flags=ObjectFlags.KEEP_ALIVE | ObjectFlags.ALLOW_CROSS_PACKAGE_REFERENCES,
            ),
        )
        definition.AnimSet = self.animations.unreal
        definition.AnimName = self.unreal.SequenceName
        definition.PlayRate = 1.0
        definition.BlendInTime = blend_in
        definition.BlendOutTime = blend_out
        definition.EndingCondition = 3 if loop else 2  # EC_Loop or EC_OnBlendOut.
        definition.BlendPerBone = False
        definition.bReverseAnimSearchOrder = True
        definition.DisableAnimSequenceNotifies = False
        definition.bAllowLeftHandIK = False
        self._body_definitions[key] = definition._path_name()
        return definition

    def play_body(  # noqa: PLR0913
        self,
        pawn: WillowPawn,
        *,
        rate: float = 1.0,
        blend_in: float = 0.12,
        blend_out: float = 0.18,
        loop: bool = False,
        override: bool = False,
    ) -> float:
        """Attach the bank and request a local full-body special move.

        Return zero when the body slot is occupied unless override is enabled.
        Otherwise return the native PlayLocal result. Native interruption rules
        still apply. Blend settings belong to a cached, immutable move definition.
        """
        moves = pawn.SMComponent
        if moves is None:
            raise ValueError("The pawn has no body special-move component")
        slot = moves.GetSMNode()
        if slot is None:
            raise ValueError("The pawn has no initialized body special-move node")
        body = slot.SkelComponent
        if body is None or body.SkeletalMesh is None:
            raise ValueError("The body special-move node has no initialized skeletal mesh")
        if not override and (moves.IsPlayingAny() or slot.bIsPlayingCustomAnim):
            return 0.0
        self.animations.attach(body)
        definition = self._body_definition(blend_in=blend_in, blend_out=blend_out, loop=loop)
        # Omitted SDK optional arguments are zeroed rather than using native defaults.
        return moves.PlayLocal(definition, PlayRateScale=rate, Duration=0.0)

    def stop_body(self, pawn: WillowPawn, *, interrupted: bool = True) -> bool:
        """Stop only this sequence wrapper's active local body move.

        Native teardown releases its IK holds and applies the engine's blend-out
        policy. Other sequences and native move definitions remain untouched.
        The attached bank is retained for explicit caller cleanup.
        """
        moves = pawn.SMComponent
        if moves is None:
            return False
        slot = moves.GetSMNode()
        if slot is None:
            return False
        definition = slot.GetCurrentAnimDef()
        if definition is None or definition._path_name() not in self._body_definitions.values():
            return False
        if not slot.IsPlaying(definition):
            return False
        moves.StopLocal(definition, bInterrupted=interrupted)
        return True
