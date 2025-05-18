from argparse import Namespace

from mods_base import command


@command(
    "set",
    description="Set the property for a given object or complete class. set <object> <attribute> <value>",
    add_help=False,
)
def set_cmd(_arg: Namespace) -> None:
    pass


set_cmd.add_argument("Object", type=str, help="The object to set the property on.", metavar="$PathName|$ClassName")
set_cmd.add_argument("Property", type=str, help="The property to set.", metavar="$PropertyName")
set_cmd.add_argument("Value", help="The value to set the property to.")
