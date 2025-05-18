import argparse
import difflib
import os
from collections.abc import Iterable
from contextlib import suppress
from dataclasses import dataclass

from unrealsdk import find_all, find_object


@dataclass
class Suggestion:
    command: str
    description: str = ""


def fuzzy_match(incomplete: str, choices: Iterable[str]) -> list[str]:
    if not incomplete:
        return list(choices)
    return difflib.get_close_matches(
        incomplete,
        choices,
        n=20,
        cutoff=0.2,
    )


def parse_input(text: str) -> tuple[list[str], str]:
    """Parse the input text into completed tokens and an incomplete token (if any)."""
    if not text or text.isspace():
        return [], ""
    tokens = text.split()
    if text.endswith(" "):
        words = tokens
        incomplete = ""
    else:
        words = tokens[:-1]
        incomplete = tokens[-1]
    return words, incomplete


def find_subparsers_action(
    parser: argparse.ArgumentParser,
) -> argparse._SubParsersAction | None:
    """Return the subparsers action from the parser if present."""
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action
    return None


def get_subcommands(parser: argparse.ArgumentParser) -> list[str]:
    """Get a list of subcommand names (choices) for the parser."""
    action = find_subparsers_action(parser)
    if action:
        return list(action.choices.keys())
    return []


def get_options(parser: argparse.ArgumentParser) -> list[str]:
    """Get a list of option strings (flags) for the parser."""
    opts = []
    for action in parser._actions:
        for opt in action.option_strings:
            opts.append(opt)
    # return unique option strings
    return list(set(opts))


def get_positional_choices(parser: argparse.ArgumentParser) -> list[str]:
    """Get choices for any positional arguments with defined choices."""
    choices = []
    for action in parser._actions:
        # skip subparsers action (not a regular positional argument)
        if isinstance(action, argparse._SubParsersAction):
            continue
        if action.metavar:
            choices.append(action.metavar)
        # positional actions have no option_strings
        if not action.option_strings and action.choices:
            choices.extend([str(c) for c in action.choices])
    return choices


def get_action_for_option(parser: argparse.ArgumentParser, option: str) -> argparse.Action | None:
    """Find the argparse action corresponding to a given option string."""
    for action in parser._actions:
        if option in action.option_strings:
            return action
    return None


def path_name_choices(template: str, incomplete: str) -> list[str]:
    choices: list[str] = []
    if incomplete.strip() == "":
        choices.extend(x._path_name() for x in find_all("Package", exact=False))
    else:
        incomplete_outer = incomplete
        if incomplete:
            incomplete_outer = incomplete.rsplit(".", maxsplit=1)[0]

        outer = None
        with suppress(ValueError):
            outer = find_object("Object", incomplete_outer)
        if outer is None:
            with suppress(ValueError):
                outer = find_object("Package", incomplete_outer)

        if outer is None:  # we need a package first
            choices.extend(
                fuzzy_match(
                    incomplete,
                    {package._path_name() for package in find_all("Package", exact=False)},
                ),
            )
        else:
            choices.extend(
                fuzzy_match(
                    incomplete,
                    {package._path_name() for package in find_all("Package", exact=False) if package.Outer == outer},
                ),
            )

    return [f"{template.replace('$PathName', choice)}" for choice in choices]


def class_name_choices(template: str, incomplete: str) -> list[str]:
    choices: list[str] = []
    if incomplete.strip() == "":
        choices.extend(x._path_name() for x in find_all("Class"))
    else:
        choices.extend(
            fuzzy_match(
                incomplete,
                {cls._path_name() for cls in find_all("Class", exact=False)},
            ),
        )

    return [template.replace("$ClassName", choice) for choice in choices]


def property_name_choices(template: str, incomplete: str, line: str) -> list[str]:
    words = line.split()

    uobj = None
    for word in words:
        with suppress(ValueError):
            uobj = find_object("Object", word)
            break
    if uobj is None:
        return []

    choices = fuzzy_match(incomplete, {prop.name for prop in uobj._properties()})
    return [template.replace("$PropertyName", choice) for choice in choices]


def fix_template_metavars(choices: list[str], incomplete: str, line: str) -> list[str]:
    fixed_choices: list[str] = []
    for choice in choices:
        common_prefix = len(os.path.commonprefix([choice, incomplete]))

        incomplete = incomplete[common_prefix:]
        if "$PathName" in choice:
            fixed_choices.extend(path_name_choices(choice, incomplete))
        elif "$ClassName" in choice:
            fixed_choices.extend(class_name_choices(choice, incomplete))
        elif "$PropertyName" in choice:
            fixed_choices.extend(property_name_choices(choice, incomplete, line))
        else:
            fixed_choices.append(choice)

    return fixed_choices



def find_matching_parser(
    text: str,
    parsers: dict[str, argparse.ArgumentParser],
) -> tuple[argparse.ArgumentParser | None, str]:
    """Find the parser or subparser that parses most of the input text and returns the remaining non matched text."""
    words, incomplete = parse_input(text)
    if not words:
        return None, incomplete

    current_parser = None
    # Check if the first word is a top-level command
    first = words[0]
    if first in parsers:
        current_parser = parsers[first]
        words = words[1:]
    else:
        return None, (" ".join(words) if words else "") + " " + incomplete

    # Traverse nested subparsers based on typed words
    for w in words:
        sub_action = find_subparsers_action(current_parser)
        if sub_action and w in sub_action.choices:
            current_parser = sub_action.choices[w]
            words = words[1:]
        else:
            break

    return current_parser, (" ".join(words) if words else "") + " " + incomplete


def update_suggestions(text: str, parsers: dict[str, argparse.ArgumentParser]) -> list[Suggestion]:
    current_parser, unparsed = find_matching_parser(text, parsers)
    words, incomplete = parse_input(unparsed)
    base_line = text[: len(text) - len(incomplete)]

    # No matching parser: suggest top-level commands
    if current_parser is None:
        matches = fuzzy_match(incomplete, parsers.keys())
        return [
            Suggestion(command=f"{base_line}{match}", description=parsers[match].description or "") for match in matches
        ]
    # Check if the last word is an option expecting a value
    if words:
        last_word = words[-1]
        if last_word.startswith("-"):
            action = get_action_for_option(current_parser, last_word)
            if action and action.choices:
                choices = fuzzy_match(incomplete, [str(c) for c in action.choices])
                return [Suggestion(command=f"{base_line}{c}", description=action.help or "") for c in choices]

    # Gather suggestions from parser
    subcommands = get_subcommands(current_parser)
    options = get_options(current_parser)
    used_flags = {w for w in words if w.startswith("-")}
    options = [opt for opt in options if opt not in used_flags]
    positional_choices = fix_template_metavars(get_positional_choices(current_parser), incomplete, text)

    # Decide what we're completing
    if incomplete == "":
        tokens = subcommands + options + positional_choices
    elif incomplete.startswith("-"):
        tokens = options
    else:
        tokens = subcommands + positional_choices

    matches = fuzzy_match(incomplete, tokens)
    suggestions: list[Suggestion] = []
    for match in matches:
        full = f"{base_line}{match}"
        desc = current_parser.description or ""
        # If it's a subcommand, find its help
        if match in subcommands:
            sub_action = find_subparsers_action(current_parser)
            if sub_action and match in sub_action.choices:
                desc = sub_action.choices[match].description or ""

        # If it's an option, find its help
        if match.startswith("-"):
            action = get_action_for_option(current_parser, match)
            if action and action.help:
                desc = action.help

        suggestions.append(Suggestion(command=full, description=desc))

    return suggestions
