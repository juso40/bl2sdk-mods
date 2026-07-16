from __future__ import annotations

from collections.abc import Iterable
from contextlib import suppress
from typing import TYPE_CHECKING, cast

from mods_base import get_pc
from unrealsdk import find_all, find_class, find_object, make_struct, unreal

if TYPE_CHECKING:
    from common import (
        AttributeInitializationDefinition,
        BaseBalanceDefinition,
        BlackMarketDefinition,
        InteractiveObjectBalanceDefinition,
        InteractiveObjectDefinition,
        MaterialInterface,
        Object,
        PopulationOpportunityPoint,
        WillowInteractiveObject,
        WillowPlayerController,
        WillowPopulationMaster,
        WillowPopulationOpportunityPoint,
        WillowVendingMachine,
        WillowVendingMachineBlackMarket,
    )

    make_vector = Object.Vector.make_struct
    make_rotator = Object.Rotator.make_struct
    make_attribute_initialization_data = AttributeInitializationDefinition.AttributeInitializationData.make_struct

else:
    make_vector = make_struct
    make_rotator = make_struct
    make_attribute_initialization_data = make_struct


def _is_instance_of(uobject: unreal.UObject, class_name: str) -> bool:
    return bool(uobject and uobject.Class == find_class(class_name))


def set_materials(_iobject: unreal.UObject, _materials: list[MaterialInterface] | None) -> None:
    # The MapEditor sometimes exports incorrect materials for IOs; ignore to avoid crashes.
    return


def set_scale(iobject: WillowInteractiveObject, scale: float) -> None:
    iobject.DrawScale = scale


def get_scale(iobject: WillowInteractiveObject) -> float:
    return iobject.DrawScale


def set_scale3d(iobject: WillowInteractiveObject, scale3d: Iterable[float]) -> None:
    x, y, z = scale3d
    iobject.DrawScale3D = make_vector("Vector", X=x, Y=y, Z=z)
    iobject.ForceUpdateComponents()


def get_scale3d(iobject: WillowInteractiveObject) -> tuple[float, float, float]:
    scale_3d = iobject.DrawScale3D
    return scale_3d.X, scale_3d.Y, scale_3d.Z


def set_rotation(iobject: WillowInteractiveObject, rotator: Iterable[int]) -> None:
    pitch, yaw, roll = rotator
    iobject.Rotation = make_rotator("Rotator", Pitch=pitch, Yaw=yaw, Roll=roll)
    iobject.ForceUpdateComponents()


def get_rotation(iobject: WillowInteractiveObject) -> tuple[int, int, int]:
    rotation = iobject.Rotation
    return rotation.Pitch, rotation.Yaw, rotation.Roll


def set_location(iobject: WillowInteractiveObject, position: Iterable[float]) -> None:
    x, y, z = position
    iobject.Location = make_vector("Vector", X=x, Y=y, Z=z)
    iobject.ForceUpdateComponents()


def get_location(iobject: WillowInteractiveObject) -> tuple[float, float, float]:
    location = iobject.Location
    return location.X, location.Y, location.Z


def instantiate(
    io_definition: InteractiveObjectDefinition | BaseBalanceDefinition | None,
) -> WillowInteractiveObject | None:
    if io_definition is None:
        return None

    pc = cast("WillowPlayerController", get_pc())
    pop_master = cast(list["WillowPopulationMaster"], find_all("WillowPopulationMaster"))
    if not pop_master:
        return None

    is_balance_def = _is_instance_of(io_definition, "InteractiveObjectBalanceDefinition")
    if is_balance_def:
        io_definition = cast("InteractiveObjectBalanceDefinition", io_definition)
        iobject = cast(
            "WillowInteractiveObject",
            pop_master[-1].SpawnPopulationControlledActor(
                io_definition.DefaultInteractiveObject.InteractiveObjectClass,
                None,
                "",
                pc.Location,
                make_rotator("Rotator", Pitch=0, Yaw=0, Roll=0),
            ),
        )
    else:
        iobject = cast(
            "WillowInteractiveObject",
            pop_master[-1].SpawnPopulationControlledActor(
                io_definition.InteractiveObjectClass,
                None,
                "",
                pc.Location,
                make_rotator("Rotator", Pitch=0, Yaw=0, Roll=0),
            ),
        )

    if pc.GetCurrentPlaythrough() != 2:
        will_pop = cast(list["WillowPopulationOpportunityPoint"], find_all("WillowPopulationOpportunityPoint"))[1:]
        pop = cast(list["PopulationOpportunityPoint"], find_all("PopulationOpportunityPoint"))[1:]
        regions = pop if len(pop) > len(will_pop) else will_pop
        region_game_stage = max(
            pc.GetGameStageFromRegion(region.GameStageRegion) for region in regions if region.GameStageRegion
        )
    else:
        region_game_stage = max(
            pawn_candidate.GetGameStage() for pawn_candidate in find_all("WillowPlayerPawn") if pawn_candidate.Arms
        )

    iobject.SetGameStage(region_game_stage)
    iobject.SetExpLevel(region_game_stage)
    iobject.PostBeginPlay()

    if is_balance_def:
        io_definition = cast("BaseBalanceDefinition", io_definition)
        grade_index = io_definition.SelectGradeIndex(region_game_stage, 0)
        iobject.InitializeBalanceDefinitionState(io_definition, grade_index)
        io_definition.SetupInteractiveObjectLoot(iobject, grade_index)
        iobject.InitializeFromDefinition(io_definition.DefaultInteractiveObject, False)

        if _is_instance_of(iobject, "WillowVendingMachine") or _is_instance_of(
            iobject,
            "WillowVendingMachineBlackMarket",
        ):
            _initialize_vending_machine(cast("WillowVendingMachine | WillowVendingMachineBlackMarket", iobject))
    else:
        io_definition = cast("InteractiveObjectDefinition", io_definition)
        iobject.InitializeFromDefinition(io_definition, False)

    return iobject


def destroy(iobject: WillowInteractiveObject | None) -> None:
    if iobject is None:
        return
    with suppress(Exception):
        set_location(iobject, (-9999999, -9999999, -9999999))
        set_scale(iobject, 0)
        iobject.Destroyed()


def _initialize_vending_machine(iobject: WillowVendingMachine | WillowVendingMachineBlackMarket) -> None:
    vending_name = iobject.InteractiveObjectDefinition._path_name().lower()

    if "health" in vending_name:
        iobject.ShopType = 2
    elif "ammo" in vending_name:
        iobject.ShopType = 1
    else:
        iobject.ShopType = 0

    gamestage = cast(
        "AttributeInitializationDefinition",
        find_object(
            "AttributeInitializationDefinition",
            "GD_Population_Shopping.Balance.Init_FeaturedItem_GameStage",
        ),
    )
    if "seraph" in vending_name:
        iobject.FixedItemCost = 120
        iobject.FixedFeaturedItemCost = 50
        iobject.FormOfCurrency = 2
        markup = None
        awesome = None
    elif "torgue" in vending_name:
        iobject.FixedItemCost = -1
        iobject.FixedFeaturedItemCost = 613
        iobject.FormOfCurrency = 4
        markup = cast(
            "AttributeInitializationDefinition",
            find_object(
                "AttributeInitializationDefinition",
                "GD_Iris_TorgueTokenVendor.CommerceMarkup",
            ),
        )
        gamestage = cast(
            "AttributeInitializationDefinition",
            find_object(
                "AttributeInitializationDefinition",
                "GD_Iris_TorgueTokenVendor.Balance.Init_FeaturedItem_GameStage",
            ),
        )
        awesome = None
    else:
        iobject.FixedItemCost = -1
        iobject.FixedFeaturedItemCost = -1
        iobject.FormOfCurrency = 0
        markup = cast(
            "AttributeInitializationDefinition",
            find_object(
                "AttributeInitializationDefinition",
                "GD_Economy.VendingMachine.Init_MarkupCalc_P1",
            ),
        )
        awesome = cast(
            "AttributeInitializationDefinition",
            find_object(
                "AttributeInitializationDefinition",
                "GD_Population_Shopping.Balance.Init_FeaturedItem_AwesomeLevel",
            ),
        )

    iobject.bOverrideFormOfCurrency = True

    if _is_instance_of(iobject, "WillowVendingMachine"):
        iobject.CommerceMarkup = make_attribute_initialization_data(
            "AttributeInitializationData",
            BaseValueConstant=1,
            BaseValueAttribute=None,
            InitializationDefinition=markup,
            BaseValueScaleConstant=1,
        )
        iobject.InventoryConfigurationName = "Inventory"
        iobject.FeaturedItemCommerceMarkup = make_attribute_initialization_data(
            "AttributeInitializationData",
            BaseValueConstant=(int("torgue" in vending_name)),
            BaseValueAttribute=None,
            InitializationDefinition=markup,
            BaseValueScaleConstant=1,
        )
        iobject.FeaturedItemConfigurationName = "FeaturedItem"
        iobject.FeaturedItemGameStage = make_attribute_initialization_data(
            "AttributeInitializationData",
            BaseValueConstant=int(awesome is None),
            BaseValueAttribute=None,
            InitializationDefinition=gamestage,
            BaseValueScaleConstant=1,
        )
        iobject.FeaturedItemAwesomeLevel = make_attribute_initialization_data(
            "AttributeInitializationData",
            BaseValueConstant=0,
            BaseValueAttribute=None,
            InitializationDefinition=awesome,
            BaseValueScaleConstant=1,
        )

    iobject.ResetInventory()

    if "blackmarket" in vending_name:
        iobject.ShopType = 3
        iobject.DefinitionData = cast(
            "BlackMarketDefinition",
            find_object(
                "BlackMarketDefinition",
                "GD_BlackMarket.BlackMarket.MarketDef_BlackMarket",
            ),
        )
        iobject.FixedItemCost = 0
        iobject.FixedFeaturedItemCost = 0
