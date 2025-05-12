from imgui_bundle import imgui, imgui_ctx

from .popups import draw_save_modal, draw_usage_modal


def draw() -> None:
    save_file_modal: bool = False
    usage_modal: bool = False
    with imgui_ctx.begin_menu("File") as file_menu:
        if file_menu.visible and imgui.menu_item_simple("Save To File"):
            save_file_modal = True
    with imgui_ctx.begin_menu("Help") as help_menu:
        if help_menu.visible and imgui.menu_item_simple("Usage"):
            usage_modal = True

    if save_file_modal:
        imgui.open_popup("Save File")
    with imgui_ctx.begin_popup_modal(
        name="Save File",
        flags=imgui.WindowFlags_.always_auto_resize.value,
    ) as save_modal:
        if save_modal.visible:
            draw_save_modal()
            
    if usage_modal:
        imgui.open_popup("Usage")
    with imgui_ctx.begin_popup_modal(
        name="Usage",
        flags=imgui.WindowFlags_.always_auto_resize.value,
    ) as usage_popup_modal:
        if usage_popup_modal.visible:
            draw_usage_modal()
