from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from unrealsdk import unreal


class ItemDefinition:
    ItemDefinition: str = "ItemDefinition"
    BalanceDefinition: str = "BalanceDefinition"
    ManufacturerDefinition: str = "ManufacturerDefinition"
    ManufacturerGradeIndex: str = "ManufacturerGradeIndex"
    AlphaItemPartDefinition: str = "AlphaItemPartDefinition"
    BetaItemPartDefinition: str = "BetaItemPartDefinition"
    GammaItemPartDefinition: str = "GammaItemPartDefinition"
    DeltaItemPartDefinition: str = "DeltaItemPartDefinition"
    EpsilonItemPartDefinition: str = "EpsilonItemPartDefinition"
    ZetaItemPartDefinition: str = "ZetaItemPartDefinition"
    EtaItemPartDefinition: str = "EtaItemPartDefinition"
    ThetaItemPartDefinition: str = "ThetaItemPartDefinition"
    MaterialItemPartDefinition: str = "MaterialItemPartDefinition"
    PrefixItemNamePartDefinition: str = "PrefixItemNamePartDefinition"
    TitleItemNamePartDefinition: str = "TitleItemNamePartDefinition"
    GameStage: str = "GameStage"

    definitions: ClassVar[dict[str, list[str]]] = {
        "WillowUsableItem": ["UsableItemDefinition"],
        "WillowArtifact": ["ArtifactDefinition"],
        "WillowClassMod": [
            "ClassModDefinition",
            "CrossDLCClassModDefinition",
        ],
        "WillowGrenadeMod": ["GrenadeModDefinition"],
        "WillowMissionItem": ["MissionItemDefinition"],
        "WillowUsableCustomizationItem": ["UsableCustomizationItemDefinition"],
        "WillowShield": ["ShieldDefinition"],
    }


class WeaponDefinition:
    WeaponTypeDefinition: str = "WeaponTypeDefinition"
    BalanceDefinition: str = "BalanceDefinition"
    ManufacturerDefinition: str = "ManufacturerDefinition"
    ManufacturerGradeIndex: str = "ManufacturerGradeIndex"
    BodyPartDefinition: str = "BodyPartDefinition"
    GripPartDefinition: str = "GripPartDefinition"
    BarrelPartDefinition = "BarrelPartDefinition"
    SightPartDefinition: str = "SightPartDefinition"
    StockPartDefinition: str = "StockPartDefinition"
    ElementalPartDefinition: str = "ElementalPartDefinition"
    Accessory1PartDefinition: str = "Accessory1PartDefinition"
    Accessory2PartDefinition: str = "Accessory2PartDefinition"
    MaterialPartDefinition: str = "MaterialPartDefinition"
    PrefixPartDefinition: str = "PrefixPartDefinition"
    TitlePartDefinition: str = "TitlePartDefinition"
    GameStage: str = "GameStage"

    definitions: ClassVar[dict[str, list[str]]] = {
        "WillowWeapon": ["WeaponTypeDefinition"],
    }


@dataclass
class ItemData:
    ItemDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    ItemDefinition_Index: int = -1
    BalanceDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    BalanceDefinition_Index: int = -1
    ManufacturerDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    ManufacturerDefinition_Index: int = -1
    ManufacturerGradeIndex: int = 1
    AlphaItemPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    AlphaItemPartDefinition_Index: int = -1
    BetaItemPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    BetaItemPartDefinition_Index: int = -1
    GammaItemPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    GammaItemPartDefinition_Index: int = -1
    DeltaItemPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    DeltaItemPartDefinition_Index: int = -1
    EpsilonItemPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    EpsilonItemPartDefinition_Index: int = -1
    ZetaItemPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    ZetaItemPartDefinition_Index: int = -1
    EtaItemPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    EtaItemPartDefinition_Index: int = -1
    ThetaItemPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    ThetaItemPartDefinition_Index: int = -1
    MaterialItemPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    MaterialItemPartDefinition_Index: int = -1
    PrefixItemNamePartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    PrefixItemNamePartDefinition_Index: int = -1
    TitleItemNamePartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    TitleItemNamePartDefinition_Index: int = -1
    GameStage: int = 1


@dataclass
class WeaponData:
    WeaponTypeDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    WeaponTypeDefinition_Index: int = -1
    BalanceDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    BalanceDefinition_Index: int = -1
    ManufacturerDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    ManufacturerDefinition_Index: int = -1
    ManufacturerGradeIndex: int = 1
    BodyPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    BodyPartDefinition_Index: int = -1
    GripPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    GripPartDefinition_Index: int = -1
    BarrelPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    BarrelPartDefinition_Index: int = -1
    SightPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    SightPartDefinition_Index: int = -1
    StockPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    StockPartDefinition_Index: int = -1
    ElementalPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    ElementalPartDefinition_Index: int = -1
    Accessory1PartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    Accessory1PartDefinition_Index: int = -1
    Accessory2PartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    Accessory2PartDefinition_Index: int = -1
    MaterialPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    MaterialPartDefinition_Index: int = -1
    PrefixPartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    PrefixPartDefinition_Index: int = -1
    TitlePartDefinition: tuple[unreal.UObject | None, ...] = field(default_factory=tuple)
    TitlePartDefinition_Index: int = -1
    GameStage: int = 1
