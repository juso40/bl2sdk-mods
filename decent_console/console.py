from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING, cast

from unrealsdk import make_struct

from . import commands

if TYPE_CHECKING:
    from common import Canvas, Console, Object

    make_linear_color = Object.LinearColor.make_struct
else:
    make_linear_color = make_struct


class ESuggestionMode(Enum):
    NONE = auto()
    HISTORY = auto()
    SUGGESTIONS = auto()


COLOR_SUGGESTIONS = (87, 148, 87, 255)  # RGB + Alpha
COLOR_SUGGESTION_HIGHLIGHT = (32, 220, 111, 255)  # RGB + Alpha
PADDING = 14

MAX_SUGGESTIONS = 12


def lcol(r: int, g: int, b: int, a: int) -> Object.LinearColor:
    return make_linear_color(
        "LinearColor",
        False,  # type: ignore
        R=r,
        G=g,
        B=b,
        A=a,
    )


def draw(console: Console, canvas: Canvas, mode: ESuggestionMode) -> None:
    if mode == ESuggestionMode.NONE:
        return

    if mode == ESuggestionMode.HISTORY:
        suggestions = cast(list[str], console.History)
        selected = console.HistoryCur
    else:
        suggestions = commands.Commands.suggestions
        selected = commands.Commands.suggestion_index

    # prepare the suggestions area below the console input
    _, str_len_x, _str_len_y = canvas.StrLen("(>", 0, 0)
    suggestions_x, suggestions_y = str_len_x, canvas.ClipY * 0.75 + 5

    visible_suggestions, visible_selection = get_visible_suggestions_split(suggestions, selected)
    if not visible_suggestions:
        return
    draw_background_box(console, canvas, visible_suggestions)

    canvas.SetPos(suggestions_x, suggestions_y+2)
    canvas.Font = canvas.GetDefaultCanvasFont()
    for i, suggestion in enumerate(visible_suggestions):
        draw_suggestion_prepare_next(canvas, suggestion, i == visible_selection)


def draw_suggestion_prepare_next(canvas: Canvas, suggestion: str, highlight: bool) -> None:
    canvas.SetDrawColor(*(COLOR_SUGGESTIONS if not highlight else COLOR_SUGGESTION_HIGHLIGHT))
    canvas.SetBGColor(0, 0, 0, 0)
    canvas.DrawTextWithBG(suggestion)
    _, x, y = canvas.StrLen(suggestion, 0, 0)
    canvas.CurX -= x
    canvas.CurY += y


def draw_background_box(console: Console, canvas: Canvas, visible_suggestions: list[str]) -> None:
    max_x = max(canvas.StrLen(suggestion, 0, 0)[1] for suggestion in visible_suggestions)
    _, str_len_x, str_len_y = canvas.StrLen("(>", 0, 0)
    canvas.SetPos(str_len_x - 2 - PADDING, canvas.ClipY * 0.75 + 2)
    canvas.DrawTile(
        console.DefaultTexture_White,
        max_x + 4 + PADDING * 2,
        str_len_y * len(visible_suggestions) + 2 + PADDING,
        0,
        0,
        32,
        32,
        lcol(0, 255, 0, 255),
    )

    canvas.SetPos(str_len_x - PADDING, canvas.ClipY * 0.75 + 2)
    canvas.DrawTile(
        console.DefaultTexture_White,
        max_x + PADDING * 2,
        str_len_y * len(visible_suggestions) + PADDING,
        0,
        0,
        32,
        32,
        lcol(0, 0, 0, 255),
    )


def get_visible_suggestions_split(suggestions: list[str], selected: int) -> tuple[list[str], int]:
    # Get the visible suggestions and the selected index
    if len(suggestions) > MAX_SUGGESTIONS:
        start = max(0, selected - MAX_SUGGESTIONS // 2)
        end = min(len(suggestions), start + MAX_SUGGESTIONS)
        visible_suggestions = suggestions[start:end]
        selected_index = selected - start
    else:
        visible_suggestions = suggestions
        selected_index = selected

    return visible_suggestions, selected_index
