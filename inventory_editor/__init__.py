from __future__ import annotations

from typing import Any, ClassVar

from mods_base import build_mod, hook, keybind
from unrealsdk import unreal

import blimgui
from inventory_editor.backpack import player_inventory
from inventory_editor.ui import draw


class State:
    imgui_show: ClassVar[bool] = False


@keybind("Open Inventory Editor", "F4")
def _toggle() -> None:
    if State.imgui_show:
        blimgui.close_window()
        State.imgui_show = False
    else:
        blimgui.set_draw_callback(draw)
        blimgui.create_window("Inventory Editor")
        State.imgui_show = True


@hook("WillowGame.WillowPlayerController:ShowStatusMenu")
def on_show_status_menu(
    _obj: unreal.UObject,
    _args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    """Resets the cached inventory data upon opening the players status menu as he might drop items."""
    player_inventory.update()


@hook("WillowGame.WillowPlayerController:WillowClientShowLoadingMovie")
def on_start_load(
    _obj: unreal.UObject,
    args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    """Disable the inventory editor when loading a new map in case the user forgot to close it."""
    if args.MovieName is None:
        return
    if State.imgui_show:
        _toggle.callback()  # type: ignore
    player_inventory.reset()


@hook("WillowGame.WillowPlayerController:WillowClientDisableLoadingMovie")
def on_end_load(
    _obj: unreal.UObject,
    _args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    """Update the cached inventory data upon loading a new map."""
    player_inventory.update()


mod = build_mod(
    hooks=[
        on_show_status_menu,
        on_start_load,
        on_end_load,
    ],
)
