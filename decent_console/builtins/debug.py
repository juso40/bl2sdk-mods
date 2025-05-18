from argparse import Namespace

from mods_base import command


@command("analyzeoctree", description="Outputs information about the octree.", add_help=False)
def freeze_at_cmd(_arg: Namespace) -> None:
    pass


freeze_at_cmd.add_argument(
    "option",
    nargs="?",
    type=str,
    choices=["VERBOSE"],
)


@command("cancelmatinee", description="cancelmatinee [param] Skips current matinee; parameter is the number of seconds into the matinee the player must be before the command will work.", add_help=False)
def cancel_matinee_cmd(_arg: Namespace) -> None:
    pass

@command("confighash", description="Displays configuration information", add_help=False)
def config_hash_cmd(_arg: Namespace) -> None:
    pass

@command("configmem", description="Displays memory information", add_help=False)
def config_mem_cmd(_arg: Namespace) -> None:
    pass

@command("dumpmaterialstats", description=r"Dumps material stats to '<Game>\WillowGame\Logs'", add_help=False)
def dump_material_stats_cmd(_arg: Namespace) -> None:
    pass

@command("dumpshaderstats", description=r"Dumps shader stats to '<Game>\WillowGame\Logs'", add_help=False)
def dump_shader_stats_cmd(_arg: Namespace) -> None:
    pass

@command("exec", description="Executes the contents (other console commands) of the specified file.", add_help=False)
def exec_cmd(_arg: Namespace) -> None:
    pass

@command("gamever", description="Displays the game version", add_help=False)
def game_ver_cmd(_arg: Namespace) -> None:
    pass

@command("memorysplit", description="Outputs information about how memory is split between various resources.", add_help=False)
def memory_split_cmd(_arg: Namespace) -> None:
    pass

@command("particlemeshusage", description=" Outputs info about the amount of static meshes used with particles systems.", add_help=False)
def particle_mesh_usage_cmd(_arg: Namespace) -> None:
    pass

@command("showmiplevels", description="Toggles the use of solid colors in place of lightmaps to visualize mip levels.", add_help=False)
def show_mip_levels_cmd(_arg: Namespace) -> None:
    pass