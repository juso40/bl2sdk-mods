from argparse import Namespace

from mods_base import command


@command("obj")
def obj_cmd(_arg: Namespace) -> None:
    pass

cmd_parser = obj_cmd.parser.add_subparsers(dest="command", required=True)
obj_cmd.parser.add_argument(
    "command",
    type=str,
    choices=["dump", "classess", "refs"],
    help="Command to execute",
)

obj_dump = cmd_parser.add_parser(
    "dump",
    help="Dump the object to a file",
)
obj_dump.add_argument(
    "Object",
    metavar="PathName",
)

obj_classes=cmd_parser.add_parser(
    "classes",
    help="List all classes",
)

obj_refs=cmd_parser.add_parser(
    "refs",
    help="List all references to the object",
)
obj_refs.add_argument(
    "Name=PathName",
    metavar="PathName",
)
