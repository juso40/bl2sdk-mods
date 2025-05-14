import argparse
from unrealsdk import find_all, find_object
from contextlib import suppress


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


def find_subparsers_action(parser: argparse.ArgumentParser) -> argparse._SubParsersAction | None:
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


def get_pathname_suggestions(parser: argparse.ArgumentParser, incomplete: str) -> list[str]:
    choices = []
    for action in parser._actions:
        # skip subparsers action (not a regular positional argument)
        if isinstance(action, argparse._SubParsersAction):
            continue
        # positional actions have no option_strings
        if action.metavar == "PathName" and not action.option_strings:
            if incomplete.strip() == "":
                choices.extend(x._path_name() for x in find_all("Package"))
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
                    for package in find_all("Package", exact=False):
                        if package._path_name().startswith(incomplete_outer):
                            choices.append(package._path_name())
                else:
                    for package in find_all("Package", exact=False):
                        if package.Outer == outer and package._path_name().startswith(incomplete):
                            choices.append(package._path_name())
                    for x in find_all("Object", exact=False):
                        if x.Outer == outer and x._path_name().startswith(incomplete):
                            choices.append(x._path_name())
    return choices


def update_suggestions(text: str, parsers: dict[str, argparse.ArgumentParser]) -> list[str]:
    words, incomplete = parse_input(text)
    # Suggest top-level commands if none typed
    if not words:
        if incomplete:
            return [cmd for cmd in parsers if cmd.startswith(incomplete)]
        return list(parsers.keys())

    # Identify the top-level command
    first = words[0]
    if first not in parsers:
        # Partial or unknown top-level command
        if incomplete:
            return [cmd for cmd in parsers if cmd.startswith(first)]
        return []

    current_parser = parsers[first]

    # Traverse nested subparsers based on typed words
    for w in words[1:]:
        sub_action = find_subparsers_action(current_parser)
        if sub_action and w in sub_action.choices:
            current_parser = sub_action.choices[w]
        else:
            break

    # If the last word is an option expecting a value, suggest its choices
    last_word = words[-1]
    if last_word.startswith("-"):
        action = get_action_for_option(current_parser, last_word)
        if action and action.choices:
            if incomplete:
                return [str(choice) for choice in action.choices if str(choice).startswith(incomplete)]
            return [str(choice) for choice in action.choices]

    # Collect available subcommands, options, and positional choices
    subcommands = get_subcommands(current_parser)
    options = get_options(current_parser)
    path_name_suggestions = get_pathname_suggestions(current_parser, incomplete)
    # Exclude options already used in the input
    used_flags = {t for t in words if t.startswith("-")}
    options = [opt for opt in options if opt not in used_flags]
    positional_choices = get_positional_choices(current_parser)

    suggestions = []
    if incomplete == "":
        # At a word boundary, suggest all possible next tokens
        suggestions = subcommands + options + positional_choices + path_name_suggestions
    elif incomplete.startswith("-"):
        suggestions = [opt for opt in options if opt.startswith(incomplete)]
    else:
        suggestions = [sub for sub in subcommands if sub.startswith(incomplete)]
        suggestions += [choice for choice in positional_choices if choice.startswith(incomplete)]
        suggestions += path_name_suggestions

    return list(set(suggestions))
