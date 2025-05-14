from argparse import Namespace

from mods_base import command


@command("exit", description="Exits the game")
def exit_cmd(_arg: Namespace) -> None:
    pass


