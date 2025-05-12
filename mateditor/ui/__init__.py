from collections.abc import Callable

from imgui_bundle import imgui, imgui_ctx

from . import editor, materials, menubar


def draw() -> None:
    with imgui_ctx.begin_main_menu_bar() as main_menu_bar:
        if main_menu_bar.visible:
            menubar.draw()
        offset = imgui.get_window_height()
    io = imgui.get_io()
    imgui.set_next_window_size((io.display_size.x, io.display_size.y - offset), imgui.Cond_.always.value)
    imgui.set_next_window_pos((0, offset), imgui.Cond_.always.value)
    with imgui_ctx.begin(
        "Material Editor",
        flags=imgui.WindowFlags_.no_resize.value
        | imgui.WindowFlags_.no_decoration.value
        | imgui.WindowFlags_.no_collapse.value
        | imgui.WindowFlags_.no_move.value
        | imgui.WindowFlags_.no_title_bar.value,
    ):
        call_with_title("Materials", materials.draw)
        imgui.separator()
        call_with_title("Editor", editor.draw)


def call_with_title(title: str, child_func: Callable[[], None]) -> None:
    """Calls the given function in a child region with a text and separator above it."""
    imgui.text(title)
    imgui.separator()
    child_func()
