from argparse import Namespace

from mods_base import command


@command("stat", description="Show statistics on screen", add_help=False)
def stat_cmd(_arg: Namespace) -> None:
    pass
stat_cmd.add_argument(
    "option",
    type=str,
    choices=["fps", "unit", "levels"],
)
