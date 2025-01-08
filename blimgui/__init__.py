import site
from collections.abc import Callable
from pathlib import Path
from typing import Any

from mods_base.hook import Type, hook
from unrealsdk import unreal

site.addsitedir(str(Path(__file__).parent.absolute() / "dist"))

# git clone https://github.com/pthom/imgui_bundle.git
# cd imgui_bundle
# py -V:3.13-32 -m pip install -v . -t "./dist"
# monkey patched pyglet.gl.win32.py:32 to never use WGL_ARB_pixel_format

from imgui_bundle import hello_imgui, imgui, immapp
from imgui_bundle import icons_fontawesome_4 as icons
from mods_base import Library, build_mod, options
from mods_base.keybinds import keybind

__version__: str
__version_info__: tuple[int, ...]

DRAW_FUN = Callable[[], None]
WINDOW = None
IMPL = None

size_x = options.HiddenOption("size_x", 1280)
size_y = options.HiddenOption("size_y", 720)

ALL_THEMES = [
    hello_imgui.ImGuiTheme_.darcula_darker,
    hello_imgui.ImGuiTheme_.darcula,
    hello_imgui.ImGuiTheme_.imgui_colors_classic,
    hello_imgui.ImGuiTheme_.imgui_colors_dark,
    hello_imgui.ImGuiTheme_.imgui_colors_light,
    hello_imgui.ImGuiTheme_.material_flat,
    hello_imgui.ImGuiTheme_.photoshop_style,
    hello_imgui.ImGuiTheme_.gray_variations,
    hello_imgui.ImGuiTheme_.gray_variations_darker,
    hello_imgui.ImGuiTheme_.microsoft_style,
    hello_imgui.ImGuiTheme_.cherry,
    hello_imgui.ImGuiTheme_.light_rounded,
    hello_imgui.ImGuiTheme_.so_dark_accent_blue,
    hello_imgui.ImGuiTheme_.so_dark_accent_yellow,
    hello_imgui.ImGuiTheme_.so_dark_accent_red,
    hello_imgui.ImGuiTheme_.black_is_black,
    hello_imgui.ImGuiTheme_.white_is_white,
]

ALL_THEMES_NAMES = [theme.name for theme in ALL_THEMES]


def style_ui(_option: options.SpinnerOption | None = None, val: str = "") -> None:
    """
    Apply the selected theme to the UI.

    :return: None
    """
    if not WINDOW:
        return
    theme = ALL_THEMES[ALL_THEMES_NAMES.index(val or imgui_theme.value)]
    hello_imgui.apply_theme(theme)


imgui_theme = options.SpinnerOption(
    "Theme",
    ALL_THEMES_NAMES[0],
    ALL_THEMES_NAMES,
    wrap_enabled=True,
    on_change=style_ui,
)


def update() -> None:
    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("File", True):
            clicked_quit, selected_quit = imgui.menu_item("Quit", "Cmd+Q", False, True)
            if clicked_quit:
                close_window()
            imgui.end_menu()
        imgui.end_main_menu_bar()

    imgui.begin("Hello World", True)
    imgui.text("This is a text!" + icons.ICON_FA_HEART)
    imgui.text_colored((0.2, 1.0, 0.0, 1.0), "Colored Text, wow!")

    imgui.end()


ACTIVE_CALLBACK = update


def create_window(
    caption: str,
    width: int | options.HiddenOption = size_x,
    height: int | options.HiddenOption = size_y,
) -> None:
    global should_close  # noqa: PLW0603
    should_close = False
    _x = width if isinstance(width, int) else width.value
    _y = height if isinstance(height, int) else height.value
    immapp.manual_render.setup_from_runner_params(
        runner_params=immapp.RunnerParams(
            fps_idling=hello_imgui.FpsIdling(fps_idle=0.0, enable_idling=False),
            callbacks=hello_imgui.RunnerCallbacks(
                show_gui=ACTIVE_CALLBACK,
            ),
            app_window_params=hello_imgui.AppWindowParams(
                window_title=caption,
                window_geometry=hello_imgui.WindowGeometry(size=(_x, _y)),
            ),
        ),
        add_ons_params=None,
    )
    style_ui()


should_close = False


def close_window() -> None:
    global should_close  # noqa: PLW0603
    should_close = True


def set_draw_callback(callback: DRAW_FUN) -> None:
    """
    Set the given callable as active callback each draw tick.

    :param callback: Reference to the callable.
    :return: None
    """
    global ACTIVE_CALLBACK  # noqa: PLW0603
    ACTIVE_CALLBACK = callback


@hook("WillowGame.WillowGameViewportClient:Tick", Type.POST_UNCONDITIONAL, immediately_enable=True)
def _on_tick(
    _obj: unreal.UObject,
    _args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    if hello_imgui.is_using_hello_imgui():
        immapp.manual_render.render()
        if should_close:
            hello_imgui.get_runner_params().app_shall_exit = True
            immapp.manual_render.tear_down()


@keybind("Test Window", "F1")
def test_window() -> None:
    if hello_imgui.is_using_hello_imgui():
        close_window()
        return
    create_window("Test Window")
    global ACTIVE_CALLBACK  # noqa: PLW0603
    ACTIVE_CALLBACK = update


mod = build_mod(
    cls=Library,
    options=[
        size_x,
        size_y,
        imgui_theme,
    ],
    hooks=[
        _on_tick,
    ],
    keybinds=[
        test_window,
    ],
)
