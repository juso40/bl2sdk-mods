from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from common import Canvas, Console

COLOR_SUGGESTIONS = (87, 148, 87, 255)  # RGB + Alpha
COLOR_SUGGESTION_HIGHLIGHT = (32, 220, 111, 255)  # RGB + Alpha

MAX_SUGGESTIONS = 12

def draw(console: Console, canvas: Canvas, suggestions: list[str], selected: int) -> None:
    if not suggestions:
        return

    # prepare the suggestions area below the console input
    _, str_len_x, str_len_y = canvas.StrLen("(>", 0, 0)
    suggestions_x, suggestions_y = str_len_x, canvas.ClipY * 0.75 + 5
   
    canvas.SetPos(suggestions_x, suggestions_y)
    canvas.Font = canvas.GetDefaultCanvasFont()
    visible_suggestions, visible_selection = get_visible_suggestions_split(suggestions, selected)
    for i, suggestion in enumerate(visible_suggestions):
        draw_suggestion_prepare_next(canvas, suggestion, i == visible_selection)


def draw_suggestion_prepare_next(canvas: Canvas, suggestion: str, highlight: bool) -> None:
    canvas.SetDrawColor(*(COLOR_SUGGESTIONS if not highlight else COLOR_SUGGESTION_HIGHLIGHT))
    canvas.DrawTextWithBG(suggestion)
    _, x, y = canvas.StrLen(suggestion, 0, 0)
    canvas.CurX -= x
    canvas.CurY += y


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