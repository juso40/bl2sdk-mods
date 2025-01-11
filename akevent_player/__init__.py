from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, cast

import blimgui

"""
We need to import blimgui first, as it adds imgui_bundle to the path.
"""
from imgui_bundle import icons_fontawesome_4 as icons
from imgui_bundle import imgui, imgui_md
from mods_base import ENGINE, build_mod, get_pc, hook, keybind
from unrealsdk import find_all, find_object, hooks, unreal

if TYPE_CHECKING:
    from collections.abc import Callable

    from common import AkEvent, WillowPlayerController


class State:
    imgui_show: ClassVar[bool] = False
    ak_index: ClassVar[int] = -1
    ak_events: ClassVar[list[str]] = []
    copy_paste_buffer: ClassVar[str] = ""


@keybind("Open AkEvent Player", "F1")
def _toggle() -> None:
    if State.imgui_show:
        blimgui.close_window()
        State.imgui_show = False
    else:
        blimgui.set_draw_callback(end_scene)
        blimgui.create_window("Inventory Editor")
        update_ak_events()
        State.imgui_show = True


def update_ak_events() -> None:
    State.ak_index = -1
    State.ak_events = [ENGINE.PathName(x) for x in find_all("AkEvent")]
    State.copy_paste_buffer = ""


@hook("WillowGame.WillowPlayerController:WillowClientShowLoadingMovie", hooks.Type.POST)
def on_start_load(
    _obj: unreal.UObject,
    args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    if args.MovieName is None:
        return
    if State.imgui_show:
        cast("Callable", _toggle).callback()
    State.ak_index = -1


@hook("WillowGame.WillowPlayerController:WillowClientDisableLoadingMovie")
def on_end_load(
    _obj: unreal.UObject,
    _args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    State.ak_index = -1


def end_scene() -> None:
    if not State.imgui_show:
        return
    flags = imgui.WindowFlags_.no_decoration | imgui.WindowFlags_.no_move | imgui.WindowFlags_.no_saved_settings  # type: ignore
    viewport = imgui.get_main_viewport()
    imgui.set_next_window_pos(viewport.pos)
    imgui.set_next_window_size(viewport.size)
    imgui.begin(
        "AkEvent Player",
        flags=flags,
    )
    imgui.push_item_width(-1)
    imgui_md.render("# AkEvent Player")
    imgui.text("Copy the name from below to use in your code.")
    imgui.text(icons.ICON_FA_COPY)
    imgui.same_line()
    imgui.input_text(
        "##AkEventCopyPaste",
        State.copy_paste_buffer,
        imgui.InputTextFlags_.read_only,  # type: ignore
    )

    clicked, State.ak_index = imgui.list_box(
        "##AkEvents",
        State.ak_index,
        State.ak_events,
        int(imgui.get_content_region_avail()[1] // imgui.get_frame_height()) - 1,
    )
    imgui.pop_item_width()
    if clicked:
        State.copy_paste_buffer = State.ak_events[State.ak_index]
        cast("WillowPlayerController", get_pc()).PlayAkEvent(
            cast("AkEvent", find_object("AkEvent", State.copy_paste_buffer)),
        )

    imgui.end()


mod = build_mod(
    keybinds=[_toggle],
    hooks=[on_start_load, on_end_load],
)
