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
COLOR_SUGGESTION_HIGHLIGHT = (87, 255, 87, 255)  # RGB + Alpha
COLOR_DESCRIPTION = (140, 140, 140, 255)  # RGB + Alpha
COLOR_DESCRIPTION_HIGHLIGHT = (255, 255, 255, 255)  # RGB + Alpha
PADDING = 14
PADDING_BORDER = 2
CONSOLE_PREFIX = "(>"

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
        descriptions = [f"Command from History {i}" for i in range(len(suggestions))]
        selected = console.HistoryCur
    else:
        suggestions = [cmd.command for cmd in commands.Commands.suggestions]
        descriptions = [cmd.description.replace("\n", " ")[:240] for cmd in commands.Commands.suggestions]
        selected = commands.Commands.suggestion_index

    # The x and y position where we want to start drawing the suggestions box
    suggestions_x, suggestions_y = canvas.StrLen(CONSOLE_PREFIX, 0, 0)[1], canvas.ClipY * 0.75 + 5

    # split our commands and descriptions into only the few that are visible
    visible_suggestions, visible_selection = get_visible_suggestions_split(suggestions, selected)
    visible_descriptions, _ = get_visible_suggestions_split(descriptions, selected)
    # if we have no suggestions, we don't need to draw anything
    if not visible_suggestions:
        return

    # calculate the max width that a suggestion and its description can take
    width_longest_suggestion = max(canvas.StrLen(suggestion, 0, 0)[1] for suggestion in visible_suggestions)
    max_x = (
        width_longest_suggestion
        + max(canvas.StrLen(description, 0, 0)[1] for description in visible_descriptions)
        + PADDING
    )

    draw_background_box(console, canvas, max_x, len(visible_suggestions))

    max_x = max(canvas.StrLen(suggestion, 0, 0)[1] for suggestion in visible_suggestions)
    canvas.SetPos(suggestions_x, suggestions_y + 2)
    canvas.Font = canvas.GetDefaultCanvasFont()
    for i, (suggestion, description) in enumerate(zip(visible_suggestions, visible_descriptions, strict=False)):
        draw_suggestion_prepare_next(
            canvas,
            suggestion,
            description,
            i == visible_selection,
            suggestions_x,
            suggestions_x + PADDING + width_longest_suggestion,
        )


def draw_suggestion_prepare_next(
    canvas: Canvas,
    suggestion: str,
    description: str,
    highlight: bool,
    x_text: float,
    x_description: float,
) -> None:
    canvas.SetDrawColor(*(COLOR_SUGGESTIONS if not highlight else COLOR_SUGGESTION_HIGHLIGHT))
    canvas.SetBGColor(0, 0, 0, 0)
    canvas.DrawTextWithBG(suggestion)

    canvas.CurX = x_description
    canvas.SetDrawColor(*COLOR_DESCRIPTION if not highlight else COLOR_DESCRIPTION_HIGHLIGHT)
    canvas.DrawTextWithBG(description, False)

    _, _x, y = canvas.StrLen(suggestion, 0, 0)
    canvas.CurX = x_text
    canvas.CurY += y


def draw_background_box(
    console: Console,
    canvas: Canvas,
    max_x: float,
    num_suggestions: int,
) -> None:
    _, str_len_x, str_len_y = canvas.StrLen(CONSOLE_PREFIX, 0, 0)
    canvas.SetPos(str_len_x - PADDING_BORDER - PADDING, canvas.ClipY * 0.75 + PADDING_BORDER)
    canvas.DrawTile(
        console.DefaultTexture_White,
        max_x + 4 + PADDING * 2,
        str_len_y * num_suggestions + PADDING_BORDER + PADDING,
        0,
        0,
        32,
        32,
        lcol(0, 255, 0, 255),
    )

    canvas.SetPos(str_len_x - PADDING, canvas.ClipY * 0.75 + PADDING_BORDER)
    canvas.DrawTile(
        console.DefaultTexture_White,
        max_x + PADDING * 2,
        str_len_y * num_suggestions + PADDING,
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
