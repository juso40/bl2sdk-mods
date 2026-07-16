from __future__ import annotations

from collections.abc import Iterable
from contextlib import suppress
from typing import TYPE_CHECKING, cast

from mods_base import ENGINE
from unrealsdk import find_all, make_struct, unreal

if TYPE_CHECKING:
    from common import (
        MaterialInterface,
        Object,
        StaticMesh,
        StaticMeshCollectionActor,
        StaticMeshComponent,
        WillowGameEngine,
    )

    make_vector = Object.Vector.make_struct
    make_rotator = Object.Rotator.make_struct

    ENGINE = cast(WillowGameEngine, ENGINE)

else:
    make_vector = make_struct
    make_rotator = make_struct


def set_materials(sm_component: unreal.UObject, materials: list[unreal.UObject|None] | None) -> None:
    if materials is None:
        return
    sm_component.Materials = materials
    sm_component.ForceUpdate(False)


def get_materials(sm_component: StaticMeshComponent | None) -> list[MaterialInterface]:
    if not sm_component or not sm_component.Materials:
        return []
    return list(sm_component.Materials)


def set_scale(sm_component: StaticMeshComponent, scale: float) -> None:
    sm_component.SetScale(scale)
    sm_component.ForceUpdate(False)


def get_scale(sm_component: StaticMeshComponent) -> float:
    return sm_component.Scale


def set_scale3d(sm_component: StaticMeshComponent, scale3d: Iterable[float]) -> None:
    x, y, z = scale3d
    sm_component.Scale3D = make_vector("Vector", X=x, Y=y, Z=z)
    sm_component.ForceUpdate(False)


def get_scale3d(sm_component: StaticMeshComponent) -> tuple[float, float, float]:
    scale3d = sm_component.Scale3D
    return scale3d.X, scale3d.Y, scale3d.Z


def set_rotation(sm_component: StaticMeshComponent, rotator: Iterable[int]) -> None:
    pitch, yaw, roll = rotator
    sm_component.Rotation = make_rotator("Rotator", Pitch=pitch, Yaw=yaw, Roll=roll)
    sm_component.ForceUpdate(False)


def get_rotation(sm_component: StaticMeshComponent) -> tuple[int, int, int]:
    rotation = sm_component.Rotation
    return rotation.Pitch, rotation.Yaw, rotation.Roll


def set_location(sm_component: StaticMeshComponent, position: Iterable[float]) -> None:
    x, y, z = position
    sm_component.CachedParentToWorld.WPlane.X = x
    sm_component.CachedParentToWorld.WPlane.Y = y
    sm_component.CachedParentToWorld.WPlane.Z = z
    sm_component.ForceUpdate(False)
    sm_component.SetComponentRBFixed(True)


def get_location(sm_component: StaticMeshComponent) -> tuple[float, float, float]:
    location = sm_component.CachedParentToWorld.WPlane
    return location.X, location.Y, location.Z


def instantiate(static_mesh: StaticMesh | None) -> StaticMeshComponent | None:
    if static_mesh is None:
        return None

    world_info = ENGINE.GetCurrentWorldInfo()
    sm_component = world_info.MyEmitterPool.GetFreeStaticMeshComponent(True)
    if sm_component is None:
        return None

    collection_actor = cast(list["StaticMeshCollectionActor"], find_all("StaticMeshCollectionActor"))
    if not collection_actor:
        return None

    sm_component.SetStaticMesh(static_mesh, True)
    sm_component.SetBlockRigidBody(True)
    sm_component.SetActorCollision(True, True, True)
    sm_component.SetTraceBlocking(True, True)
    collection_actor[-1].AttachComponent(sm_component)

    return sm_component


def destroy(sm_component: StaticMeshComponent | None) -> None:
    if sm_component is None:
        return
    with suppress(Exception):
        sm_component.DetachFromAny()
