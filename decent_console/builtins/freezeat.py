from argparse import Namespace

from mods_base import command


@command("freezeat", description="Toggle freezing the camera at the current location", add_help=False)
def freeze_at_cmd(_arg: Namespace) -> None:
    pass
freeze_at_cmd.add_argument(
    "here",
    nargs="?",
    type=str,
    choices=["here"],
)
