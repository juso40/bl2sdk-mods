from typing import cast

from mods_base import CoopSupport, ValueOption, build_mod, get_pc
from mods_base.keybinds import keybind
from networking import add_network_functions, broadcast
from unrealsdk import find_object, unreal

import tracelib
import uemath
from coroutines import PostRenderCoroutine, Time, start_coroutine_post_render
from ping import settings
from uemath.umath import clamp

__version__: str
__version_info__: tuple[int, ...]

colors = {
    0: settings.ping_color_1,
    1: settings.ping_color_2,
    2: settings.ping_color_3,
    3: settings.ping_color_4,
}


def ping_coroutine(location: list[float], color: list[int], name: str) -> PostRenderCoroutine:
    duration = settings.ping_duration.value
    world_pos = uemath.Vector(location).to_ue_vector()
    text_color = color[:4]
    bg_color = color[4:]
    while True:
        yield None
        canvas: unreal.UObject = yield  # type: ignore
        pc = get_pc()

        loc = uemath.Vector(pc.Pawn.Location)
        loc.z += pc.Pawn.EyeHeight
        screen_pos = canvas.Project(world_pos)
        x = clamp(screen_pos.X, 0, canvas.SizeX - 1)
        y = clamp(screen_pos.Y, 0, canvas.SizeY - 1)
        if screen_pos.Z > 1:
            x = 0 if x > canvas.SizeX / 2 else canvas.SizeX - 1

        _, text_size_x, text_size_y = canvas.TextSize(name, 1, 1)
        canvas.Font = find_object("Font", "UI_Fonts.Font_Hud_Medium")
        canvas.SetDrawColor(*text_color)
        canvas.SetBGColor(*bg_color)
        canvas.SetPos(x - text_size_x / 2, y - text_size_y / 2)
        canvas.DrawTextWithBG(name)

        duration -= Time.unscaled_delta_time
        if duration <= 0:
            break


@broadcast.json_message
def ping_location(*, location: list[float], color: list[int], name: str) -> None:
    start_coroutine_post_render(ping_coroutine(location, color, name))


def color_by_player() -> list[int]:
    player_id: int = get_pc().PlayerReplicationInfo.PlayerID
    return [x.value for x in cast(list[ValueOption], colors[player_id % len(colors)].children)]


@keybind("Ping", "Q", description="Ping")
def ping_callback() -> None:
    impact_info = tracelib.trace_from_player_pov(debug_trace=False)

    hit_location = impact_info.HitLocation
    ping_location(
        location=[hit_location.X, hit_location.Y, hit_location.Z],
        color=color_by_player(),
        name=get_pc().PlayerReplicationInfo.PlayerName,
    )


mod = build_mod(
    keybinds=[
        ping_callback,
    ],
    options=[
        settings.ping_duration,
        settings.ping_color_1,
        settings.ping_color_2,
        settings.ping_color_3,
        settings.ping_color_4,
    ],
    coop_support=CoopSupport.ClientSide,
)
add_network_functions(mod)
