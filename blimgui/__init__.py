import site
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

site.addsitedir(str(Path(__file__).parent.absolute() / "dist"))

# git clone https://github.com/pthom/imgui_bundle.git
# cd imgui_bundle
# py -V:3.13-32 -m pip install -v . -t "./dist"
# monkey patched pyglet.gl.win32.py:32 to never use WGL_ARB_pixel_format

from imgui_bundle import imgui
from mods_base import Library, build_mod, options
from mods_base.keybinds import keybind
from unrealsdk import logging, unreal
from unrealsdk.hooks import Type, add_hook, remove_hook

if TYPE_CHECKING:
    import pyglet  # type: ignore
    from imgui_bundle.python_backends import pyglet_backend
    from pyglet import gl  # type: ignore


__version__: str
__version_info__: tuple[int, ...]

DRAW_FUN = Callable[[], None]
WINDOW = None
IMPL = None

size_x = options.HiddenOption("size_x", 1280)
size_y = options.HiddenOption("size_y", 720)


def create_window(
    caption: str,
    width: int | options.HiddenOption = size_x,
    height: int | options.HiddenOption = size_y,
    resizable: bool = True,
) -> None:
    """
    Create a new window with the given parameters. If a window already exists, rename only.

    :param caption: The caption of the window
    :param width: The width of the window
    :param height: The height of the window
    :param resizable: If True, window is resizable, else cannot be resized.
    :return: None
    """
    global WINDOW, IMPL  # noqa: PLW0603
    if not WINDOW and not IMPL:
        WINDOW = pyglet.window.Window(
            width=width if isinstance(width, int) else width.value,
            height=height if isinstance(height, int) else height.value,
            resizable=resizable,
            caption=caption,
            config=pyglet.gl.Config(),
        )
        gl.glClearColor(0.1, 0.1, 0.1, 1)
        imgui.create_context()
        IMPL = pyglet_backend.create_renderer(WINDOW)

        def on_resize(w: int, h: int) -> None:
            size_x.value = w
            size_y.value = h

        cast(pyglet.window.BaseWindow, WINDOW).push_handlers(on_resize)

    elif WINDOW:
        WINDOW.set_caption(caption=caption)


def close_window() -> bool:
    """
    Close the current window if any is open.

    :return: Bool, True if window successfully closed, else False
    """
    global WINDOW, IMPL, ACTIVE_CALLBACK  # noqa: PLW0603
    try:
        cast(pyglet_backend.PygletRenderer, IMPL).shutdown()
        cast(pyglet.window.BaseWindow, WINDOW).close()

        WINDOW = None
        IMPL = None
        ACTIVE_CALLBACK = update
        return True
    except Exception as e:  # noqa: BLE001
        logging.error(f"Error closing window: {e}")
        return False


def update() -> None:
    if imgui.begin_main_menu_bar():
        if imgui.begin_menu("File", True):
            clicked_quit, selected_quit = imgui.menu_item("Quit", "Cmd+Q", False, True)
            if clicked_quit:
                close_window()
            imgui.end_menu()
        imgui.end_main_menu_bar()

    imgui.begin("Hello World", True)
    imgui.text("This is a text!")
    imgui.text_colored((0.2, 1.0, 0.0, 1.0), "Colored Text, wow!")

    imgui.end()


def draw() -> None:
    """
    Calls the currently active callback function to update the rendered content in the new window.

    :return: None
    """
    if not WINDOW or not IMPL:
        return
    cast(pyglet_backend.PygletRenderer, IMPL).process_inputs()
    imgui.new_frame()
    ACTIVE_CALLBACK()
    if WINDOW:
        WINDOW.clear()
        imgui.render()
        cast(pyglet_backend.PygletRenderer, IMPL).render(imgui.get_draw_data())
    else:
        imgui.end_frame()


ACTIVE_CALLBACK = update


def set_draw_callback(callback: DRAW_FUN) -> None:
    """
    Set the given callable as active callback each draw tick.

    :param callback: Reference to the callable.
    :return: None
    """
    global ACTIVE_CALLBACK  # noqa: PLW0603
    ACTIVE_CALLBACK = callback


def _on_tick(
    _obj: unreal.UObject,
    _args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    draw()
    for w in pyglet.app.windows:
        w.switch_to()
        w.dispatch_events()
        w.dispatch_event("on_draw")
        w.flip()


def _import_pyglet(
    _obj: unreal.UObject,
    _args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    global pyglet, gl, pyglet_backend  # noqa: PLW0603
    import pyglet  # type: ignore
    from imgui_bundle.python_backends import pyglet_backend
    from pyglet import gl  # type: ignore

    remove_hook("WillowGame.FrontendGFxMovie:Start", Type.POST_UNCONDITIONAL, "blimgui_import_once")
    add_hook("WillowGame.WillowGameViewportClient:Tick", Type.POST_UNCONDITIONAL, "blimgui_tick", callback=_on_tick)


add_hook("WillowGame.FrontendGFxMovie:Start", Type.POST_UNCONDITIONAL, "blimgui_import_once", callback=_import_pyglet)


@keybind("Test Window", "F1")
def test_window() -> None:
    if WINDOW:
        close_window()
        return
    create_window("Test Window")
    global ACTIVE_CALLBACK  # noqa: PLW0603
    ACTIVE_CALLBACK = update


mod = build_mod(
    cls=Library,
    keybinds=[
        test_window,
    ],
)
