from __future__ import annotations

from importlib import import_module
from pathlib import Path
from pkgutil import iter_modules

from mods_base.command import ArgParseCommand

commands: list[ArgParseCommand] = []

builtins = Path(__file__).resolve().parent
for _, module_name, _ in iter_modules([builtins]):
    module = import_module(f"{__package__}.{module_name}")
    for attr_name in dir(module):
        attribute = getattr(module, attr_name)
        if isinstance(attribute, ArgParseCommand):
            commands.append(attribute)
# https://github.com/ikrima/gamedevguide/blob/master/docs/ue4guide/gameplay-programming/useful-console-commands/udk-console-commands.md