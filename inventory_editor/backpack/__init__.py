from __future__ import annotations

from typing import TYPE_CHECKING, cast

import unrealsdk
from mods_base import get_pc

from . import parts

if TYPE_CHECKING:
    from common import Inventory, WillowGame, WillowInventory, WillowPlayerController, WillowWeaponTypes

WeaponData = parts.WeaponData
ItemData = parts.ItemData

EPlayerMark = cast("WillowInventory.PlayerMark", unrealsdk.find_enum("PlayerMark"))


class BackpackProxy:
    def __init__(self) -> None:
        self.index: int = -1  # current index of the selected item
        self.item: Inventory | None = None  # current selected item
        self.item_readable: str = ""  # current selected item name

        self.data: list[Inventory] = []  # cached backpack data
        self.data_readable: list[str] = []  # cached backpack data names

        self.item_data: parts.WeaponData | parts.ItemData = parts.WeaponData()

    def reset(self) -> None:
        """Resets the cached backpack data."""
        self.index = -1
        self.item = None
        self.item_readable = ""
        self.data = []
        self.data_readable = []

    def update(self) -> None:
        """Updates the cached backpack data."""
        self.reset()
        pc = cast("WillowPlayerController", get_pc())
        if not pc:
            return
        inventory_manager = pc.GetPawnInventoryManager()
        if not inventory_manager:
            return
        # Get all items in the backpack
        self.data = [item for item in inventory_manager.Backpack if item]
        # Get the names of all items in the backpack, append an invisible index to the end
        # else imguis ID system will not work properly if we encounter duplicate names
        self.data_readable = [f"{item.GetHumanReadableName()}##{i}" for i, item in enumerate(self.data)]

    def add_item(self, item_class: str) -> None:
        """Adds an item of the given class to the backpack."""
        pc = cast("WillowPlayerController", get_pc())
        if not pc:
            return
        inventory_manager = pc.GetPawnInventoryManager()
        if not inventory_manager:
            return
        if not item_class:
            return

        if item_class == "WillowWeapon":
            weap_def_data = cast(
                "WillowWeaponTypes.WeaponDefinitionData",
                unrealsdk.make_struct("WeaponDefinitionData"),
            )
            inventory_manager.ClientAddWeaponToBackpack(weap_def_data, EPlayerMark.PM_Standard, False)
        else:
            item = cast("WillowInventory", pc.Spawn(cast(type["WillowInventory"], unrealsdk.find_class(item_class))))
            item.Quantity = 1
            inventory_manager.AddInventoryToBackpack(item)
        self.update()

    def on_select_item(self) -> None:
        """Update cached item data upon selecting a new item from the backpack."""
        self.item = self.data[self.index]
        self.item_readable = self.data_readable[self.index].split("##")[0] or "Drop and pickup the item to see its name"
        if self.item.Class.Name == "WillowWeapon":
            self.item_data = parts.WillowWeapon.filter_allowed_parts(cast("WillowGame.WillowWeapon", self.item))
        else:
            self.item_data = parts.WillowItem.filter_allowed_parts(cast("WillowGame.WillowItem", self.item))

    def on_part_changed(self, part_attr: str, part: unrealsdk.unreal.UObject | None) -> None:
        """Calls the appropriate function to update the selected items parts."""
        if self.item is None:
            return

        if self.item.Class.Name == "WillowWeapon":
            self.on_weapon_part_changed(part_attr, part)
        else:
            self.on_item_part_changed(part_attr, part)
        self.item.DefinitionData.UniqueId = self.item.GenerateUniqueID()

    def on_weapon_part_changed(self, part_attr: str, part: unrealsdk.unreal.UObject | None) -> None:
        if self.item is None:
            return
        setattr(self.item.DefinitionData, part_attr, part)
        self.item_data = parts.WillowWeapon.filter_allowed_parts(cast("WillowGame.WillowWeapon", self.item))
        if self.item.DefinitionData.WeaponTypeDefinition:
            # Calling InitializeInternal on a weapon without a WeaponTypeDefinition will crash the game
            self.initialize_weapon()

    def on_item_part_changed(self, part_attr: str, part: unrealsdk.unreal.UObject | None) -> None:
        if self.item is None:
            return
        setattr(self.item.DefinitionData, part_attr, part)
        self.item_data = parts.WillowItem.filter_allowed_parts(cast("WillowGame.WillowItem", self.item))
        if self.item.DefinitionData.ItemDefinition:
            self.initialize_item()

    def initialize_weapon(self) -> None:
        if self.item is None:
            return
        self.item.DefinitionData.TitlePartDefinition = None
        self.item.DefinitionData.PrefixPartDefinition = None
        self.item.InitializeInternal(True)
        self.item.Unready(True)

        item_index = self.index
        self.update()
        self.index = item_index
        self.on_select_item()

    def initialize_item(self) -> None:
        if self.item is None:
            return
        self.item.DefinitionData.TitleItemNamePartDefinition = None
        self.item.DefinitionData.PrefixItemNamePartDefinition = None
        self.item.InitializeInternal(True)
        self.item.Unready(True)

        item_index = self.index
        self.update()
        self.index = item_index
        self.on_select_item()


player_inventory: BackpackProxy = BackpackProxy()
