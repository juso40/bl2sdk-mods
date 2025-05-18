from argparse import Namespace

from mods_base import command


@command("obj", add_help=False)
def obj_cmd(_arg: Namespace) -> None:
    pass


cmd_parser = obj_cmd.parser.add_subparsers(dest="command", required=True)
obj_cmd.parser.add_argument(
    "command",
    type=str,
)

obj_dump = cmd_parser.add_parser(
    "dump",
    description="Dump all variable values for the specified object",
    add_help=False,
)
obj_dump.add_argument(
    "Object",
    type=str,
    metavar="$PathName",
)

obj_classes = cmd_parser.add_parser(
    "classes",
    description="Obj Classes (Shows all classes)",
    add_help=False,
)

obj_refs = cmd_parser.add_parser(
    "refs",
    description="Name=<ObjectName> Class=<OptionalObjectClass> Lists referencers of the specified object",
    add_help=False,
)
obj_refs.add_argument(
    "Name",
    type=str,
    metavar="Name=$PathName",
)

obj_list = cmd_parser.add_parser(
    "list",
    description="Obj List <Class=ClassName> <Type=MetaClass> <Outer=OuterObject> <Package=InsidePackage> <Inside=InsideObject>",
    add_help=False,
)
obj_list.add_argument(
    "Class",
    nargs="?",
    type=str,
    metavar="Class=$ClassName",
)

obj_list.add_argument(
    "Type",
    nargs="?",
    type=str,
    metavar="Type=$ClassName",
)
obj_list.add_argument(
    "Outer",
    nargs="?",
    type=str,
    metavar="Outer=$PathName",
)
obj_list.add_argument(
    "Package",
    nargs="?",
    type=str,
    metavar="Package=$PathName",
)
obj_list.add_argument(
    "Inside",
    nargs="?",
    type=str,
    metavar="Inside=$PathName",
)

obj_dependencies = cmd_parser.add_parser(
    "dependencies",
    description="Obj Dependencies <Class=ClassName> <Type=MetaClass> <Outer=OuterObject> <Package=InsidePackage> <Inside=InsideObject>",
    add_help=False,
)
obj_dependencies.add_argument(
    "Package",
    nargs="?",
    type=str,
    metavar="Package=$PathName",
)

obj_garbage = cmd_parser.add_parser(
    "garbage",
    description="Collect and purge garbage",
    add_help=False,
)

obj_hash = cmd_parser.add_parser(
    "hash",
    description="Show object hashing information",
    add_help=False,
)

obj_flags = cmd_parser.add_parser(
    "flags",
    description="Show object flags",
    add_help=False,
)
obj_flags.add_argument(
    "Name",
    type=str,
    metavar="$PathName",
)