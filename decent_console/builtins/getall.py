from argparse import Namespace

from mods_base import command


@command("getall", description="Returns the value property for all instantiated classes", add_help=False)
def getall_cmd(_arg: Namespace) -> None:
    pass


getall_cmd.add_argument(
    "ClassName",
    type=str,
    metavar="$ClassName",
)

getall_cmd.add_argument(
    "PropertyName",
    type=str,
    metavar="$PropertyName",
)

getall_cmd.add_argument(
    "Name=ObjectInstanceName",
    nargs="?",
    type=str,
)
getall_cmd.add_argument(
    "Outer=OuterObject",
    nargs="?",
    type=str,
    metavar="Outer=$PathName",
)
