from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from mods_base import build_mod, hook
from unrealsdk import unreal
from unrealsdk.hooks import Block, Type

from . import commands, console

if TYPE_CHECKING:
    from common import Canvas, Console


@hook("Engine.Console:Open.InputKey", Type.PRE)
def input_key(
    obj: unreal.UObject,
    args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> type[Block] | None:
    console = cast("Console", obj)

    if args.Event == 1 and (args.Key not in ["BackSpace", "Delete", "Down", "Up", "Left", "Right", "Tab"] or not console.bCtrl):
        commands.update_suggestions(console.TypedStr)
        return None

    if not args.Event in (0, 2):
        return None

    match args.Key:
        case "BackSpace":
            if not console.bCtrl:
                return None
            console.TypedStr, console.TypedStrPos = commands.ctrl_backspace(console.TypedStr, console.TypedStrPos)
            return Block
        case "Delete":
            if not console.bCtrl:
                return None
            console.TypedStr, console.TypedStrPos = commands.ctrl_delete(console.TypedStr, console.TypedStrPos)
            return Block
        case "Down":
            if not console.bCtrl:
                return None
            commands.suggestions_change(1)
            return Block
        case "Up":
            if not console.bCtrl:
                return None
            commands.suggestions_change(-1)
            return Block
        case "Left":
            if not console.bCtrl:
                return None
            console.TypedStrPos = commands.ctrl_left(console.TypedStr, console.TypedStrPos)
            return Block
        case "Right":
            if not console.bCtrl:
                return None
            console.TypedStrPos = commands.ctrl_right(console.TypedStr, console.TypedStrPos)
            return Block
        case "Tab":
            commands.accept_suggestion(console)
            return Block

    return None


@hook("Engine.Console:Open.PostRender_Console", Type.POST_UNCONDITIONAL)
def post_render_console(
    obj: unreal.UObject,
    args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None:
    console.draw(
        cast("Console", obj),
        cast("Canvas", args.Canvas),
        commands.Commands.suggestions,
        commands.Commands.suggestion_index,
    )


mod = build_mod()
