from imgui_bundle import imgui

from inventory_editor.backpack import player_inventory

add_item_combo: int = 0
items: list[str] = [
    "WillowWeapon",
    "WillowShield",
    "WillowUsableItem",
    "WillowArtifact",
    "WillowClassMod",
    "WillowGrenadeMod",
    "WillowMissionItem",
    "WillowUsableCustomizationItem",
]


def draw() -> None:
    """Draws the inventory content in the current child region."""
    global add_item_combo

    clicked, add_item_combo = imgui.combo(
        "##AddItemCombo",
        current_item=add_item_combo,
        items=items,
    )
    imgui.same_line()
    if imgui.button("Add Item"):
        player_inventory.add_item(items[add_item_combo])
    if imgui.is_item_hovered():
        imgui.set_tooltip(
            "Adds an item of the selected type to your inventory.\n"
            "You will need to manually select the new item in the list below.\n"
            "New items are named 'None' until you select parts for them.",
        )

    imgui.separator()
    if imgui.button("Refresh Inventory", size=(-1, 0)):
        player_inventory.update()
    if imgui.is_item_hovered():
        imgui.set_tooltip(
            "Refreshes the inventory list.\n"
            "This is done automatically when you open the editor or backpack.\n"
            "You should only need to manually refresh if you drop items while in the backpack menu.",
        )

    imgui.push_item_width(-1)
    clicked, player_inventory.index = imgui.list_box(
        "##Backpack",
        current_item=player_inventory.index,
        items=player_inventory.data_readable,
        height_in_items=int(
            (imgui.get_content_region_avail()[1] // imgui.get_frame_height()) * 1.25,
        )
        - 1,
    )
    if clicked:
        player_inventory.on_select_item()
    imgui.text(f"Click any item to edit it. Current Item: {player_inventory.item_readable}")
