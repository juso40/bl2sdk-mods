from imgui_bundle import imgui, immapp

from mateditor.materials import Materials


@immapp.static(number_items=16, search="", index=-1)
def draw() -> None:
    static = draw
    imgui.push_item_width(-1)
    imgui.text("Search:")
    _, static.search = imgui.input_text("##Search", static.search, 32)
    material_names = Materials.all_materials(static.search)
    listbox_clicked, static.index = imgui.list_box(
        "##Materials",
        static.index,
        material_names,
        static.number_items,
    )
    if listbox_clicked:
        Materials.select(material_names[static.index])
    imgui.text("Number of Materials shown:")
    _, static.number_items = imgui.slider_int("##Number of Materials", static.number_items, 1, 32)
    imgui.pop_item_width()
