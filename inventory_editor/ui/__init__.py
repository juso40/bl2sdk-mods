from collections.abc import Callable

from imgui_bundle import imgui, imgui_ctx

from . import editor, inventory


def draw() -> None:
    flags = (
        imgui.WindowFlags_.no_decoration.value
        | imgui.WindowFlags_.no_move.value
        | imgui.WindowFlags_.no_saved_settings.value
    )
    viewport = imgui.get_main_viewport()
    imgui.set_next_window_pos(viewport.pos)
    imgui.set_next_window_size(viewport.size)

    with imgui_ctx.begin(
        "Inventory Editor",
        flags=flags,
    ):
        h_space, v_space = imgui.get_content_region_avail()
        with imgui_ctx.begin_child(
            "Inventory",
            imgui.ImVec2(h_space / 2, v_space),
            child_flags=imgui.ChildFlags_.borders.value,
        ):
            call_with_title("Backpack", inventory.draw)
        imgui.same_line()
        with imgui_ctx.begin_child(
            "Editor",
            imgui.ImVec2(h_space / 2, v_space),
            child_flags=imgui.ChildFlags_.borders.value,
        ):
            call_with_title("Editor", editor.draw)


def call_with_title(title: str, child_func: Callable[[], None]) -> None:
    """Calls the given function in a child region with a text and separator above it."""
    imgui.text(title)
    imgui.separator()
    child_func()
