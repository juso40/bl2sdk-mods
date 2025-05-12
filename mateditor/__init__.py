from __future__ import annotations

from typing import ClassVar

from mods_base import build_mod, keybind

import blimgui
from mateditor.ui import draw

IMGUI_SHOW: bool = False


class State:
    imgui_show: ClassVar[bool] = False


@keybind("Open mateditor", "F5")
def _toggle() -> None:
    if State.imgui_show:
        blimgui.close_window()
        State.imgui_show = False
    else:
        blimgui.set_draw_callback(draw)
        blimgui.create_window("mateditor")
        State.imgui_show = True

mod = build_mod(keybinds=[_toggle])