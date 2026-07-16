from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, cast

from mods_base import ENGINE, get_pc
from unrealsdk import find_all, make_struct

if TYPE_CHECKING:
    from common import (
        Actor,
        AIPawnBalanceDefinition,
        MaterialInterface,
        Object,
        PopulationOpportunityPoint,
        WillowAIPawn,
        WillowGameEngine,
        WillowPawn,
        WillowPopulationMaster,
        WillowPopulationOpportunityPoint,
    )

    make_vector = Object.Vector.make_struct
    make_rotator = Object.Rotator.make_struct

    ENGINE = cast(WillowGameEngine, ENGINE)

else:
    make_vector = make_struct
    make_rotator = make_struct


def set_materials(ai_pawn: WillowPawn, materials: list[MaterialInterface] | None) -> None:
    if materials is None:
        return
    ai_pawn.Mesh.Materials = materials


def set_scale(ai_pawn: WillowPawn, scale: float) -> None:
    ai_pawn.Mesh.Scale = scale


def set_scale3d(ai_pawn: WillowPawn, scale3d: Iterable[float]) -> None:
    x, y, z = scale3d
    ai_pawn.Mesh.Scale3D = make_vector("Vector", X=x, Y=y, Z=z)
    ai_pawn.Mesh.ForceUpdate(True)


def set_rotation(ai_pawn: WillowPawn, rotator: Iterable[int]) -> None:
    pitch, yaw, roll = rotator
    ai_pawn.Mesh.Rotation = make_rotator("Rotator", Pitch=pitch, Yaw=yaw, Roll=roll)
    ai_pawn.Mesh.ForceUpdate(True)


def set_location(ai_pawn: WillowPawn, position: Iterable[float]) -> None:
    x, y, z = position
    ai_pawn.Location = make_vector("Vector", X=x, Y=y, Z=z)


def instantiate(ai_pawn_balance: AIPawnBalanceDefinition | None) -> WillowPawn | None:
    if ai_pawn_balance is None:
        return None

    pc = get_pc()
    pop_masters = cast(list["WillowPopulationMaster"], find_all("WillowPopulationMaster"))
    if not pop_masters:
        return None

    pawn = cast(
        "WillowAIPawn",
        pop_masters[-1].SpawnPopulationControlledActor(
            cast("Actor", ai_pawn_balance.AIPawnArchetype.Class),
            None,
            "",
            pc.Location,
            make_rotator("Rotator", Pitch=0, Yaw=0, Roll=0),
            ai_pawn_balance.AIPawnArchetype,
            False,
            False,
        ),
    )

    if pc.GetCurrentPlaythrough() != 2:
        will_pop = cast(
            list["WillowPopulationOpportunityPoint"],
            list(find_all("WillowPopulationOpportunityPoint"))[1:],
        )
        pop = cast(list["PopulationOpportunityPoint"], list(find_all("PopulationOpportunityPoint"))[1:])
        regions = pop if len(pop) > len(will_pop) else will_pop
        region_game_stage = max(
            pc.GetGameStageFromRegion(region.GameStageRegion) for region in regions if region.GameStageRegion
        )
    else:
        region_game_stage = max(
            pawn_candidate.GetGameStage() for pawn_candidate in find_all("WillowPlayerPawn") if pawn_candidate.Arms
        )

    pawn.SetGameStage(region_game_stage)
    pawn.SetExpLevel(region_game_stage)
    pawn.SetGameStageForSpawnedInventory(region_game_stage)
    pawn.SetAwesomeLevel(0)
    pawn.Controller.InitializeCharacterClass()
    pawn.Controller.RecalculateAttributeInitializedState()
    pawn.InitializeBalanceDefinitionState(ai_pawn_balance, -1)
    ai_pawn_balance.SetupPawnItemPoolList(pawn)
    pawn.AddDefaultInventory()

    ai_definition = pawn.MyWillowMind.GetAIDefinition()
    ai_definition.TargetSearchRadius = 12000

    return pawn
