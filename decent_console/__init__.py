from __future__ import annotations

from time import time
from typing import TYPE_CHECKING, Any, ClassVar, cast

from mods_base import EInputEvent, build_mod, hook
from unrealsdk import unreal
from unrealsdk.hooks import Block, Type

from . import commands, console

if TYPE_CHECKING:
    from common import Canvas, Console


DEBOUNCE_TIME = 0.15  # seconds


class State:
    current_mode: ClassVar[console.ESuggestionMode] = console.ESuggestionMode.NONE
    last_input_time: ClassVar[float] = 0.0
    last_typed_str: ClassVar[str] = ""
    last_processed_str: ClassVar[str] = ""


def handle_ctrl_commands(console: Console, key: str) -> None | tuple[type[Block], bool]:
    match key:
        case "BackSpace":
            console.TypedStr, console.TypedStrPos = commands.ctrl_backspace(console.TypedStr, console.TypedStrPos)
        case "Delete":
            console.TypedStr, console.TypedStrPos = commands.ctrl_delete(console.TypedStr, console.TypedStrPos)
        case "Left":
            console.TypedStrPos = commands.ctrl_left(console.TypedStr, console.TypedStrPos)
        case "Right":
            console.TypedStrPos = commands.ctrl_right(console.TypedStr, console.TypedStrPos)
        case _:
            return None
    return Block, True


@hook("Engine.Console:Open.InputKey", Type.PRE)
def input_key(
    obj: unreal.UObject,
    args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None | tuple[type[Block], bool]:
    uconsole = cast("Console", obj)
    key = args.Key
    typed_str = uconsole.TypedStr

    # Give back controll to the game to allow Scroll up/down in the console history
    if typed_str.strip() == "" and key in ("Up", "Down") and State.current_mode != console.ESuggestionMode.SUGGESTIONS:
        State.current_mode = console.ESuggestionMode.HISTORY
        return None

    # Disable and clear current mode
    if key == "Escape" and State.current_mode != console.ESuggestionMode.NONE and args.Event == EInputEvent.IE_Released:
        ret = Block, True
        if uconsole.TypedStr == "" and State.current_mode == console.ESuggestionMode.HISTORY:
            ret = None
        State.current_mode = console.ESuggestionMode.NONE
        uconsole.TypedStr = ""
        uconsole.TypedStrPos = 0
        return ret
    # filter the relevant events
    if args.Event not in (EInputEvent.IE_Pressed, EInputEvent.IE_Repeat):
        return None

    if uconsole.bCtrl:
        return handle_ctrl_commands(uconsole, key)

    if State.current_mode != console.ESuggestionMode.SUGGESTIONS:
        return None
    # Handle suggestion input logic
    match key:
        case "Down":
            commands.suggestions_change(1)
        case "Up":
            commands.suggestions_change(-1)
        case "Tab":
            commands.accept_suggestion(uconsole)
        case _:
            return None

    return Block, True


@hook("Engine.Console:Open.InputKey", Type.POST_UNCONDITIONAL)
def input_key_post(
    obj: unreal.UObject,
    _args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    uconsole = cast("Console", obj)
    State.last_typed_str = uconsole.TypedStr
    State.last_input_time = time()


@hook("Engine.Console:Open.PostRender_Console", Type.POST_UNCONDITIONAL)
def post_render_console(
    obj: unreal.UObject,
    args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    uconsole = cast("Console", obj)
    if (
        time() - State.last_input_time > DEBOUNCE_TIME
        and State.last_typed_str != State.last_processed_str
        and State.current_mode == console.ESuggestionMode.SUGGESTIONS
    ):
        commands.update_suggestions(State.last_typed_str)
        State.last_processed_str = State.last_typed_str

    console.draw(
        uconsole,
        cast("Canvas", args.Canvas),
        State.current_mode,
    )


@hook("Engine.Console:Open.InputChar", Type.PRE)
def input_char(
    obj: unreal.UObject,
    args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> tuple[type[Block], bool] | None:
    uconsole = cast("Console", obj)
    if args.Unicode == "\x7f":  # block the □ (delete) character
        return Block, True
    if args.Unicode == " " and uconsole.bCtrl:
        State.current_mode = console.ESuggestionMode.SUGGESTIONS
        commands.update_suggestions(uconsole.TypedStr)
        return Block, True
    if args.Unicode not in ("\x1b", "\r"):  # Ignore escape and enter
        State.current_mode = console.ESuggestionMode.SUGGESTIONS
    return None

@hook("Engine.Console:Open.BeginState", Type.POST_UNCONDITIONAL)
def open_console(
    _obj: unreal.UObject,
    _args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    State.current_mode = console.ESuggestionMode.NONE

mod = build_mod()
