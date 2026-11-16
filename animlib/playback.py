from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, cast
from weakref import WeakValueDictionary

from unrealsdk import find_class
from unrealsdk.unreal import WeakPointer

if TYPE_CHECKING:
    from common import AnimNode, AnimNodeSequence, AnimNodeSlot, SkeletalMeshComponent

    from .sequence import AnimationSequence


def _belongs(component: SkeletalMeshComponent, node: AnimNode) -> bool:
    root = component.Animations
    if root is None or node.SkelComponent != component:
        return False
    if root == node:
        return True
    _, candidates = root.FindAllAnimNodes([], str(node.NodeName))
    return node in candidates


def _target(component: SkeletalMeshComponent, target: str | AnimNode, class_name: str) -> AnimNode:
    if component.SkeletalMesh is None or component.Animations is None:
        raise ValueError("The component has no initialized skeletal animation graph")
    if isinstance(target, str):
        _, candidates = component.Animations.FindAllAnimNodes([], target)
        if len(candidates) != 1:
            raise ValueError(f"Animation node {target!r} must resolve uniquely, found {len(candidates)}")
        node = candidates[0]
    else:
        node = target
    if not node.Class._inherits(find_class(class_name)):
        raise TypeError(f"The playback target must be a {class_name}")
    if not _belongs(component, node):
        raise ValueError("The playback node does not belong to the component's current graph")
    pending = [node]
    visited = set()
    special_move_class = find_class("GearboxFramework.AnimNodeSpecialMoveBlend")
    while pending:
        current = pending.pop()
        path = current._path_name()
        if path in visited:
            continue
        visited.add(path)
        if current.Class._inherits(special_move_class):
            raise ValueError("Special-move nodes require native lifecycle playback such as play_body()")
        pending.extend(current.ParentNodes)
    return node


def _lookup(sequence: AnimationSequence, component: SkeletalMeshComponent, *, reverse: bool) -> None:
    found = component.FindAnimSequence(sequence.unreal.SequenceName, bReverseSearchOrder=reverse)
    if found is None or found._path_name() != sequence.path:
        raise ValueError(f"The target's animation search does not resolve this exact sequence: {sequence.clip!r}")


class Playback[T: AnimNode](ABC):
    """Observe one playback request through weak component and node references.

    Dropping a handle does not stop playback. A newer successful AnimLib request on
    the same target supersedes the older handle. External restarts of the same
    native sequence on the same node cannot be distinguished without game hooks.
    """

    def __init__(self, sequence: AnimationSequence, component: SkeletalMeshComponent, node: T, duration: float) -> None:
        self.sequence = sequence
        self.duration = duration
        self._component = WeakPointer(component)
        self._node = WeakPointer(node)
        self._root = WeakPointer(component.Animations)
        self._keys = [(component._path_name(), node._path_name())]
        self._finished = False

    @property
    def component(self) -> SkeletalMeshComponent:
        """Resolve the target component or raise ReferenceError after destruction."""
        component = self._component()
        if component is None:
            raise ReferenceError("The animation playback component is no longer alive")
        return component

    @property
    def node(self) -> T:
        """Resolve the target node or raise ReferenceError after destruction."""
        node = self._node()
        if node is None:
            raise ReferenceError("The animation playback node is no longer alive")
        return node

    @property
    def is_playing(self) -> bool:
        """Report native playback while the original graph, node and clip still match.

        Native playing state does not imply nonzero blend weight or a visible pose.
        Once an ended or replaced target is observed, the handle stays inactive.
        """
        component = self._component()
        node = self._node()
        if self._finished:
            return False
        if component is None or node is None or component.Animations != self._root():
            self._finish()
            return False
        if not _belongs(component, node):
            self._finish()
            return False
        current = self._sequence_node()
        if (
            current is None
            or not current.bPlaying
            or current.AnimSeq is None
            or current.AnimSeq._path_name() != self.sequence.path
        ):
            self._finish()
            return False
        return True

    def _claim(self) -> None:
        for key in self._keys:
            previous = _active.get(key)
            if previous is not None:
                previous._finish()
            _active[key] = self

    def _finish(self) -> None:
        self._finished = True
        for key in self._keys:
            if _active.get(key) is self:
                del _active[key]

    @abstractmethod
    def _sequence_node(self) -> AnimNodeSequence | None:
        """Resolve the sequence node for this request without selecting another target."""

    @abstractmethod
    def stop(self) -> bool:
        """Request stopping only while this handle still matches active playback."""


_active: WeakValueDictionary[tuple[str, str], Playback] = WeakValueDictionary()


class NodePlayback(Playback["AnimNodeSequence"]):
    """Control playback directly on an existing sequence node."""

    def _sequence_node(self) -> AnimNodeSequence:
        return self.node

    def stop(self) -> bool:
        """Stop the matching timeline while leaving pose and blend policy to the graph."""
        if not self.is_playing:
            return False
        self.node.StopAnim()
        self._finish()
        return True


class SlotPlayback(Playback["AnimNodeSlot"]):
    """Control one ordinary slot request and its selected custom sequence child."""

    def __init__(
        self,
        sequence: AnimationSequence,
        component: SkeletalMeshComponent,
        node: AnimNodeSlot,
        duration: float,
    ) -> None:
        super().__init__(sequence, component, node, duration)
        child = node.GetCustomAnimNodeSeq()
        self._child = WeakPointer(child)
        if child is not None:
            self._keys.append((component._path_name(), child._path_name()))

    def _sequence_node(self) -> AnimNodeSequence | None:
        slot = self.node
        if not slot.bIsPlayingCustomAnim:
            return None
        child = slot.GetCustomAnimNodeSeq()
        return child if child is not None and child == self._child() else None

    def stop(self, *, blend_out: float = 0.25) -> bool:
        """Blend out this matching custom-slot request without touching other slots."""
        if not self.is_playing:
            return False
        self.node.StopCustomAnim(blend_out)
        self._finish()
        return True


def _play_on_node(  # noqa: PLR0913
    sequence: AnimationSequence,
    component: SkeletalMeshComponent,
    node: str | AnimNodeSequence,
    *,
    rate: float,
    loop: bool,
    start_time: float,
    override: bool,
) -> NodePlayback | None:
    """Start a clip on an existing sequence node and return its weak playback handle."""
    _target(component, node, "Engine.AnimNodeSequence")
    sequence.animations.attach(component)
    target = cast("AnimNodeSequence", _target(component, node, "Engine.AnimNodeSequence"))
    if target.bPlaying and not override:
        return None
    _lookup(sequence, component, reverse=target.bReverseAnimSeqSearchOrder)
    target.SetAnim(sequence.unreal.SequenceName)
    if target.AnimSeq is None or target.AnimSeq._path_name() != sequence.path:
        raise RuntimeError("The native sequence node did not bind the requested sequence")
    target.PlayAnim(bLoop=loop, InRate=rate, StartTime=start_time)
    playback = NodePlayback(sequence, component, target, target.GetAnimPlaybackLength())
    if not playback.is_playing:
        return None
    playback._claim()
    return playback


def _play_in_slot(  # noqa: PLR0913
    sequence: AnimationSequence,
    component: SkeletalMeshComponent,
    slot: str | AnimNodeSlot,
    *,
    rate: float,
    blend_in: float,
    blend_out: float,
    loop: bool,
    override: bool,
) -> SlotPlayback | None:
    """Start a clip in an existing ordinary slot and return its weak playback handle."""
    _target(component, slot, "Engine.AnimNodeSlot")
    sequence.animations.attach(component)
    target = cast("AnimNodeSlot", _target(component, slot, "Engine.AnimNodeSlot"))
    if target.bIsPlayingCustomAnim and not override:
        return None
    _lookup(sequence, component, reverse=target.bReverseAnimSeqSearchOrder)
    duration = target.PlayCustomAnim(
        sequence.unreal.SequenceName,
        Rate=rate,
        BlendInTime=blend_in,
        BlendOutTime=blend_out,
        bLooping=loop,
        bOverride=override,
        StartTime=0.0,
        EndTime=0.0,
    )
    if duration <= 0.0:
        return None
    playback = SlotPlayback(sequence, component, target, duration)
    child = target.GetCustomAnimNodeSeq()
    if child is None or child.AnimSeq is None or child.AnimSeq._path_name() != sequence.path:
        raise RuntimeError("The native slot did not bind the requested sequence")
    if not playback.is_playing:
        return None
    playback._claim()
    return playback
