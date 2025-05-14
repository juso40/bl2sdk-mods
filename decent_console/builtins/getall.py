from argparse import Namespace

from mods_base import command


@command("getall", add_help=False)
def getall_cmd(_arg: Namespace) -> None:
    pass


getall_cmd.add_argument(
    "ClassName",
    type=str,
    choices=["$ClassName"],
)

getall_cmd.add_argument(
    "PropertyName",
    type=str,
    choices=["$PropertyName"],
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
    choices=["Outer=$PathName"],
)
