from mods_base import CoopSupport, Game, build_mod, options
from networking import add_network_functions

from bl2eternal.mechanics import dashing, glorykill


def on_dash_option_change(_option: options.BoolOption, value: bool) -> None:
    if value:
        dashing.enable()
    else:
        dashing.disable()


def on_glory_kill_option_change(_option: options.BoolOption, value: bool) -> None:
    if value:
        glorykill.enable()
    else:
        glorykill.disable()


DASH_OPTION = options.BoolOption(
    identifier="Dash",
    description="Enable dash.",
    value=True,
    on_change=on_dash_option_change,
)
GLORY_KILL_OPTION = options.BoolOption(
    identifier="Glory Kill",
    description="Enable glory kill.",
    value=True,
    on_change=on_glory_kill_option_change,
)
DASH_SCREEN_PARTICLE = options.BoolOption(
    identifier="Dash Screen Particle",
    value=Game.get_current() != Game.TPS,  # TPS doesn't have this
    description="Enable the screen particle effect when dashing.",
    is_hidden=Game.get_current() == Game.TPS,
    on_change=lambda _, v: dashing.enable_dash_particle(v),
)


def on_enable() -> None:
    if DASH_OPTION.value:
        dashing.enable()
    if GLORY_KILL_OPTION.value:
        glorykill.enable()


def on_disable() -> None:
    dashing.disable()
    glorykill.disable()


mod = build_mod(
    options=[DASH_OPTION, GLORY_KILL_OPTION, DASH_SCREEN_PARTICLE],
    on_enable=on_enable,
    on_disable=on_disable,
    coop_support=CoopSupport.RequiresAllPlayers,
)
add_network_functions(mod, network_functions=[dashing.server_dash, dashing.dash_particles, dashing.remove_screen_particles])