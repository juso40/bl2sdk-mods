from __future__ import annotations
from typing import TYPE_CHECKING, cast

from mods_base import options
from unrealsdk import find_object

if TYPE_CHECKING:
    from common import AkEvent

ping_duration = options.SliderOption(
    "Ping Duration",
    5.0,
    0.5,
    20.0,
    0.5,
    False,
    description="How long the ping should be displayed in seconds.",
)


def get_ak_event_by_name(name: str) -> AkEvent:
    path_name = {
        "Ak_Play_UI_HUD_FastTravel_Request": "Ake_UI.UI_HUD.Ak_Play_UI_HUD_FastTravel_Request",
        "Ak_Play_UI_HUD_Token_Unlocked": "Ake_UI.UI_HUD.Ak_Play_UI_HUD_Token_Unlocked",
        "Ak_Play_UI_Shield_Confirm": "Ake_UI.UI_Shields.Ak_Play_UI_Shield_Confirm",
    }.get(name, "")
    return cast("AkEvent", find_object("AkEvent", path_name))


ping_sfx = options.SpinnerOption(
    "Ping Sound",
    "Ak_Play_UI_Shield_Confirm",
    [
        "None",
        "Ak_Play_UI_HUD_FastTravel_Request",
        "Ak_Play_UI_HUD_Token_Unlocked",
        "Ak_Play_UI_Shield_Confirm",
    ],
    wrap_enabled=True,
)

ping_color_1 = options.NestedOption(
    "Your Ping Color",
    children=[
        options.SliderOption("Text R", value=103, min_value=0, max_value=255),
        options.SliderOption("Text G", value=215, min_value=0, max_value=255),
        options.SliderOption("Text B", value=255, min_value=0, max_value=255),
        options.SliderOption("Text A", value=180, min_value=0, max_value=255),
        options.SliderOption("Background R", value=0, min_value=0, max_value=255),
        options.SliderOption("Background G", value=0, min_value=0, max_value=255),
        options.SliderOption("Background B", value=0, min_value=0, max_value=255),
        options.SliderOption("Background A", value=200, min_value=0, max_value=255),
    ],
)


ping_color_2 = options.NestedOption(
    "Ping Color 2",
    children=[
        options.SliderOption("Text R", value=255, min_value=0, max_value=255),
        options.SliderOption("Text G", value=204, min_value=0, max_value=255),
        options.SliderOption("Text B", value=0, min_value=0, max_value=255),
        options.SliderOption("Text A", value=180, min_value=0, max_value=255),
        options.SliderOption("Background R", value=0, min_value=0, max_value=255),
        options.SliderOption("Background G", value=0, min_value=0, max_value=255),
        options.SliderOption("Background B", value=0, min_value=0, max_value=255),
        options.SliderOption("Background A", value=200, min_value=0, max_value=255),
    ],
)

ping_color_3 = options.NestedOption(
    "Ping Color 3",
    children=[
        options.SliderOption("Text R", value=20, min_value=0, max_value=255),
        options.SliderOption("Text G", value=255, min_value=0, max_value=255),
        options.SliderOption("Text B", value=169, min_value=0, max_value=255),
        options.SliderOption("Text A", value=180, min_value=0, max_value=255),
        options.SliderOption("Background R", value=0, min_value=0, max_value=255),
        options.SliderOption("Background G", value=0, min_value=0, max_value=255),
        options.SliderOption("Background B", value=0, min_value=0, max_value=255),
        options.SliderOption("Background A", value=200, min_value=0, max_value=255),
    ],
)

ping_color_4 = options.NestedOption(
    "Ping Color 4",
    children=[
        options.SliderOption("Text R", value=204, min_value=0, max_value=255),
        options.SliderOption("Text G", value=83, min_value=0, max_value=255),
        options.SliderOption("Text B", value=250, min_value=0, max_value=255),
        options.SliderOption("Text A", value=180, min_value=0, max_value=255),
        options.SliderOption("Background R", value=0, min_value=0, max_value=255),
        options.SliderOption("Background G", value=0, min_value=0, max_value=255),
        options.SliderOption("Background B", value=0, min_value=0, max_value=255),
        options.SliderOption("Background A", value=200, min_value=0, max_value=255),
    ],
)
