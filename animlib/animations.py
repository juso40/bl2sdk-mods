from collections.abc import Mapping, Sequence
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, cast
from uuid import uuid4

import meshloader
from unrealsdk import find_object

from .sequence import AnimationSequence

if TYPE_CHECKING:
    from common import AnimSet, SkeletalMesh, SkeletalMeshComponent


class AnimationSet:
    """Load selected GLB clips into one AnimSet.

    Construction creates native assets. The selected source skin supplies the track
    layout unless an explicit mesh requests strict binding.
    """

    def __init__(  # noqa: PLR0913
        self,
        source: str | Path,
        *,
        skin: str,
        scene: str,
        clips: Sequence[str],
        scale: float = 100.0,
        sample_rate: float = 60.0,
        umodel: bool = True,
        mesh: str | SkeletalMesh | None = None,
    ) -> None:
        """Create the native set and wrap each selected clip without starting playback."""
        native = cast(
            "AnimSet",
            meshloader.load_animations(
                source,
                f"AnimSet_{uuid4().hex}",
                skin=skin,
                scene=scene,
                clips=clips,
                scale=scale,
                sample_rate=sample_rate,
                umodel=umodel,
                mesh=mesh,
                sequence_names={clip: f"Clip_{index}" for index, clip in enumerate(clips)},
            ),
        )
        self.path = native._path_name()
        self._sequences: dict[str, AnimationSequence] = {
            str(sequence.SequenceName): AnimationSequence(self, str(sequence.SequenceName), sequence._path_name())
            for sequence in native.Sequences
        }

    @property
    def unreal(self) -> AnimSet:
        """Resolve the underlying AnimSet game object."""
        return cast("AnimSet", find_object("AnimSet", self.path))

    @property
    def sequences(self) -> Mapping[str, AnimationSequence]:
        """Return a read-only mapping from clip names to wrappers."""
        return MappingProxyType(self._sequences)

    def __getitem__(self, clip: str) -> AnimationSequence:
        """Return one sequence by its clip name."""
        return self._sequences[clip]

    def attach(self, component: SkeletalMeshComponent) -> None:
        """Append this set once while preserving every other component AnimSet."""
        sets = list(component.AnimSets)
        if any(item is not None and item._path_name() == self.path for item in sets):
            return
        sets.append(self.unreal)
        component.AnimSets = sets
        component.UpdateAnimations()

    def detach(self, component: SkeletalMeshComponent) -> None:
        """Remove this AnimSet from the given SkeletalMeshComponent's AnimSets array."""
        sets = list(component.AnimSets)
        remaining = [item for item in sets if item is None or item._path_name() != self.path]
        if len(remaining) != len(sets):
            component.AnimSets = remaining
            component.UpdateAnimations()
