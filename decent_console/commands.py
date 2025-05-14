from __future__ import annotations

import re
from argparse import ArgumentParser
from typing import TYPE_CHECKING, ClassVar, cast

from mods_base import mod_list
from mods_base.command import ArgParseCommand, rlm

from . import builtins, suggestions

if TYPE_CHECKING:
    from common import Console


class Commands:
    argparse_commands: ClassVar[list[ArgumentParser]] = [rlm.parser]
    suggestions: ClassVar[list[str]] = []
    suggestion_index: int = 0


ArgParseCommand.__post_init__ = lambda self: Commands.argparse_commands.append(self.parser)
for mod in mod_list.mod_list:
    for cmd in mod.commands:
        Commands.argparse_commands.append(cast(ArgParseCommand, cmd).parser)

for cmd in builtins.commands:
    Commands.argparse_commands.append(cmd.parser)


def ctrl_backspace(text: str, cursor: int) -> tuple[str, int]:
    if cursor == 0:
        return text, cursor

    before = text[:cursor]
    after = text[cursor:]

    # Remove trailing spaces first
    before = re.sub(r"\s+$", "", before)
    new_cursor = len(before)

    # Remove the "word" before the cursor (including punctuation)
    match = re.search(r"[\w]+|[^\w\s]", before[::-1])  # Look backwards
    if match:
        length_to_delete = match.end()
        final_cursor = new_cursor - length_to_delete
        new_text = before[:final_cursor] + after
        return new_text, final_cursor
    return before + after, new_cursor


def ctrl_delete(text: str, cursor: int) -> tuple[str, int]:
    if cursor >= len(text):
        return text, cursor

    before = text[:cursor]
    after = text[cursor:]

    # Remove leading whitespace
    after = re.sub(r"^\s+", "", after)

    # Remove the next "word" (including punctuation)
    match = re.match(r"[\w]+|[^\w\s]", after)
    if match:
        length_to_delete = match.end()
        after = after[length_to_delete:]

    new_text = before + after
    return new_text, cursor


def get_tokens(text: str) -> list[tuple[str, int, int]]:
    pattern = re.compile(r"\s+|[\w]+|[^\w\s]")  # Whitespace | Word | Punctuation
    return [(m.group(), m.start(), m.end()) for m in pattern.finditer(text)]


def ctrl_left(text: str, cursor: int) -> int:
    if cursor == 0:
        return 0

    tokens = get_tokens(text[:cursor])
    for tok, start, end in reversed(tokens):
        if end < cursor:
            if not tok.isspace():
                return start
        elif start < cursor and not tok.isspace():
            return start
    return 0


def ctrl_right(text: str, cursor: int) -> int:
    if cursor >= len(text):
        return len(text)

    tokens = get_tokens(text[cursor:])
    offset = cursor
    for tok, _start, end in tokens:
        if not tok.isspace():
            return offset + end
    return len(text)


def update_suggestions(text: str) -> None:

    _sugg = suggestions.update_suggestions(text, {x.prog: x for x in Commands.argparse_commands})
    Commands.suggestions = _sugg


def accept_suggestion(console: Console) -> None:
    if not Commands.suggestions:
        return
    
    if Commands.suggestion_index >= len(Commands.suggestions):
        Commands.suggestion_index = 0
        return
    
    completion_suggestion = Commands.suggestions[Commands.suggestion_index]

    text = console.TypedStr
    parts = text.split(" ")
    parts[-1] = completion_suggestion
    curr_text = " ".join(parts)

    
    console.SetInputText(curr_text)
    console.TypedStrPos = len(console.TypedStr)

    update_suggestions(curr_text)


def suggestions_change(direction: int) -> None:
    if not Commands.suggestions:
        return
    if direction == 1:
        Commands.suggestion_index += 1
        if Commands.suggestion_index >= len(Commands.suggestions):
            Commands.suggestion_index = 0
    elif direction == -1:
        Commands.suggestion_index -= 1
        if Commands.suggestion_index < 0:
            Commands.suggestion_index = len(Commands.suggestions) - 1
