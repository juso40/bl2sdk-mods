from argparse import Namespace

from mods_base import command


@command("exit", description="Exits the game", add_help=False)
def exit_cmd(_arg: Namespace) -> None:
    pass


@command("showlog", description="Toggle the log window", add_help=False)
def showlog_cmd(_arg: Namespace) -> None:
    pass


@command("ListTextures", description="List all loaded textures", add_help=False)
def list_textures_cmd(_arg: Namespace) -> None:
    pass


@command(
    "ListUncachedStaticLightingInteractions",
    description="List all uncached static lighting interactions",
    add_help=False,
)
def list_uncached_static_lighting_interactions_cmd(_arg: Namespace) -> None:
    pass


@command("togglehud", description="Toggle the HUD", add_help=False)
def toggle_hud_cmd(_arg: Namespace) -> None:
    pass


@command("cls", description="Clear the console", add_help=False)
def cls_cmd(_arg: Namespace) -> None:
    pass


@command("flushlog", description="Flush Console log to file", add_help=False)
def flush_log_cmd(_arg: Namespace) -> None:
    pass


@command("mem", description="Show memory usage", add_help=False)
def mem_cmd(_arg: Namespace) -> None:
    pass


@command("sockets", description="In network play, shows a list of network sockets in use.", add_help=False)
def sockets_cmd(_arg: Namespace) -> None:
    pass


@command("fov", description="Set the field of view", add_help=False)
def fov_cmd(_arg: Namespace) -> None:
    pass


@command("say", description="Send a message to all players", add_help=False)
def say_cmd(_arg: Namespace) -> None:
    pass


@command("disconnect", description="Disconnect from the server", add_help=False)
def disconnect_cmd(_arg: Namespace) -> None:
    pass

@command("start", description="Open a new map, takes either URL or Package, fully commits", add_help=False)
def start_cmd(_arg: Namespace) -> None:
    pass

@command("open", description="Open a new map, takes either URL or Package", add_help=False)
def open_cmd(_arg: Namespace) -> None:
    pass

@command("streammap", description="Stream a new map, takes either URL or Package", add_help=False)
def streammap_cmd(_arg: Namespace) -> None:
    pass
