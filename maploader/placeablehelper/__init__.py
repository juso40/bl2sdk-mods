from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast

from unrealsdk import find_object, logging, unreal
from unrealsdk.unreal import notify_changes

from maploader.placeablehelper import ai_pawn, interactive_objects, static_mesh

if TYPE_CHECKING:
    from common import (
        AIPawnBalanceDefinition,
        InteractiveObjectDefinition,
        MaterialInterface,
        StaticMesh,
        StaticMeshComponent,
        WillowInteractiveObject,
        WillowPawn,
    )

__all__ = ["CREATED_OBJECTS", "TAGGED_OBJECTS", "TaggedObject", "load_map", "unload_map"]

def find_object_or_none(class_name: str, path_name: str) -> unreal.UObject | None:
    try:
        return find_object(class_name, path_name)
    except ValueError:
        return None


@dataclass(slots=True)
class TaggedObject:
    path_name: str
    uclass: str
    tags: list[str]
    metadata: str
    _cached_uobj: unreal.WeakPointer[unreal.UObject] = field(default_factory=lambda: unreal.WeakPointer(None))

    @property
    def uobj(self) -> unreal.UObject | None:
        if self._cached_uobj and self._cached_uobj():
            return self._cached_uobj()
        uobj = find_object(self.uclass, self.path_name)
        self._cached_uobj = unreal.WeakPointer(uobj)
        return self._cached_uobj()


CREATED_OBJECTS: dict[str, list[str]] = {
    "StaticMeshComponent": [],
    "InteractiveObjectDefinition": [],
}

TAGGED_OBJECTS: dict[str, list[TaggedObject]] = {}


def load_map(map_data: dict[str, Any]) -> None:
    start_time = time.time()

    with notify_changes():
        load_ai_pawns(map_data)
        load_static_meshes(map_data)
        load_interactive_objects(map_data)

    logging.info(f"Loading map took {time.time() - start_time:.3f}s.")


def load_static_meshes(map_data: dict[str, Any]) -> None:
    cached_objects: dict[str, unreal.UObject] = {}

    creation_data: dict[str, Any] = map_data.get("Create", {})
    edit_data: dict[str, Any] = map_data.get("Edit", {})
    destruction_data: dict[str, Any] = map_data.get("Destroy", {})

    for obj, attrs in edit_data.get("StaticMeshComponent", {}).items():
        smc = cast("StaticMeshComponent", find_object_or_none("StaticMeshComponent", obj))
        _set_smc_attrs(smc=smc, attrs=attrs)

    for to_destroy in destruction_data.get("StaticMeshComponent", []):
        smc = cast("StaticMeshComponent", find_object_or_none("StaticMeshComponent", to_destroy))
        static_mesh.destroy(smc)

    for blueprint in creation_data.get("StaticMesh", []):
        for obj, attrs in blueprint.items():
            uobj = cast("StaticMesh|None", cached_objects.get(obj))
            if uobj is None:
                uobj = cast("StaticMesh", find_object_or_none("StaticMesh", obj))
                cached_objects[obj] = uobj

            smc = static_mesh.instantiate(uobj)
            if smc is None:
                continue
            CREATED_OBJECTS["StaticMeshComponent"].append(smc._path_name())
            _set_smc_attrs(smc=smc, attrs=attrs)


def load_ai_pawns(map_data: dict[str, Any]) -> None:
    cached_objects: dict[str, unreal.UObject] = {}
    creation_data: dict[str, Any] = map_data.get("Create", {})
    for blueprint in creation_data.get("AIPawnBalanceDefinition", []):
        for obj, attrs in blueprint.items():
            uobj = cast("AIPawnBalanceDefinition|None", cached_objects.get(obj))
            if uobj is None:
                uobj = cast("AIPawnBalanceDefinition", find_object_or_none("AIPawnBalanceDefinition", obj))
                cached_objects[obj] = uobj

            pawn = ai_pawn.instantiate(uobj)
            _set_pawn_attrs(pawn=pawn, attrs=attrs)


def load_interactive_objects(map_data: dict[str, Any]) -> None:
    cached_objects: dict[str, unreal.UObject] = {}

    creation_data: dict[str, Any] = map_data.get("Create", {})
    edit_data: dict[str, Any] = map_data.get("Edit", {})
    destruction_data: dict[str, Any] = map_data.get("Destroy", {})

    for obj, attrs in edit_data.get("InteractiveObjectDefinition", {}).items():
        iobj = cast("WillowInteractiveObject", find_object_or_none("Object", obj))
        _set_io_attrs(io=iobj, attrs=attrs)

    for to_destroy in destruction_data.get("InteractiveObjectDefinition", []):
        iobj = cast("WillowInteractiveObject", find_object_or_none("Object", to_destroy))
        interactive_objects.destroy(iobj)

    for blueprint in creation_data.get("InteractiveObjectDefinition", []):
        for obj, attrs in blueprint.items():
            uobj = cast("InteractiveObjectDefinition|None", cached_objects.get(obj))
            print("[MapLoader] Creating IO from:", obj)
            if uobj is None:
                uobj = cast("InteractiveObjectDefinition", find_object_or_none("Object", obj))
                cached_objects[obj] = uobj

            print("[MapLoader] Found IO definition:", uobj)
            iobject = interactive_objects.instantiate(uobj)
            if iobject is None:
                continue
            print("[MapLoader] Created IO instance:", iobject)
            CREATED_OBJECTS["InteractiveObjectDefinition"].append(iobject._path_name())
            _set_io_attrs(io=iobject, attrs=attrs)


def unload_map() -> None:
    start_time = time.time()
    for smc_path in CREATED_OBJECTS["StaticMeshComponent"]:
        smc = cast("StaticMeshComponent", find_object_or_none("StaticMeshComponent", smc_path))
        static_mesh.destroy(smc)

    for io_path in CREATED_OBJECTS["InteractiveObjectDefinition"]:
        io_obj = cast("WillowInteractiveObject", find_object_or_none("Object", io_path))
        interactive_objects.destroy(io_obj)

    CREATED_OBJECTS["InteractiveObjectDefinition"].clear()
    CREATED_OBJECTS["StaticMeshComponent"].clear()
    TAGGED_OBJECTS.clear()
    logging.info(f"Unloaded map in {time.time() - start_time:.3f}s.")


def _set_smc_attrs(smc: StaticMeshComponent | None, attrs: dict[str, Any]) -> None:
    if smc is None:
        return

    static_mesh.set_location(smc, attrs.get("Location", (0, 0, 0)))
    static_mesh.set_rotation(smc, attrs.get("Rotation", (0, 0, 0)))
    static_mesh.set_scale(smc, attrs.get("Scale", 1))
    static_mesh.set_scale3d(smc, attrs.get("Scale3D", (1, 1, 1)))

    materials = attrs.get("Materials")
    if materials is not None:
        materials = [find_object_or_none("MaterialInstanceConstant", material) for material in materials]
    static_mesh.set_materials(smc, materials)

    tagged_object = TaggedObject(
        path_name=smc._path_name(),
        uclass=smc.Class.Name,
        tags=attrs.get("Tags", []),
        metadata=attrs.get("Metadata", ""),
    )
    for tag in attrs.get("Tags", []):
        TAGGED_OBJECTS.setdefault(tag, []).append(tagged_object)


def _set_io_attrs(io: WillowInteractiveObject | None, attrs: dict[str, Any]) -> None:
    if io is None:
        return

    interactive_objects.set_location(io, attrs.get("Location", (0, 0, 0)))
    interactive_objects.set_rotation(io, attrs.get("Rotation", (0, 0, 0)))
    interactive_objects.set_scale(io, attrs.get("Scale", 1))
    interactive_objects.set_scale3d(io, attrs.get("Scale3D", (1, 1, 1)))

    # Materials on IO are broken anyways, skip parsing them
    materials = attrs.get("Materials")
    if materials is not None:
        materials = [
            cast("MaterialInterface", find_object_or_none("MaterialInstanceConstant", material)) for material in materials
        ]
    interactive_objects.set_materials(io, materials)

    tagged_object = TaggedObject(
        path_name=io._path_name(),
        uclass=io.Class.Name,
        tags=attrs.get("Tags", []),
        metadata=attrs.get("Metadata", ""),
    )
    for tag in attrs.get("Tags", []):
        TAGGED_OBJECTS.setdefault(tag, []).append(tagged_object)


def _set_pawn_attrs(pawn: WillowPawn | None, attrs: dict[str, Any]) -> None:
    if pawn is None:
        return

    ai_pawn.set_location(pawn, attrs.get("Location", (0, 0, 0)))
    ai_pawn.set_rotation(pawn, attrs.get("Rotation", (0, 0, 0)))
    ai_pawn.set_scale(pawn, attrs.get("Scale", 1))
    ai_pawn.set_scale3d(pawn, attrs.get("Scale3D", (1, 1, 1)))

    materials = attrs.get("Materials")
    if materials is not None:
        materials = [
            cast("MaterialInterface", find_object_or_none("MaterialInstanceConstant", material)) for material in materials
        ]
    ai_pawn.set_materials(pawn, materials)

    tagged_object = TaggedObject(
        path_name=pawn._path_name(),
        uclass=pawn.Class.Name,
        tags=attrs.get("Tags", []),
        metadata=attrs.get("Metadata", ""),
    )
    for tag in attrs.get("Tags", []):
        TAGGED_OBJECTS.setdefault(tag, []).append(tagged_object)
