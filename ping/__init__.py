from mods_base import CoopSupport, build_mod, get_pc
from mods_base.keybinds import keybind
from networking import add_network_functions, broadcast
from unrealsdk import make_struct, unreal

import tracelib
import uemath
from coroutines import PostRenderCoroutine, Time, start_coroutine_post_render

__version__: str
__version_info__: tuple[int, ...]

colors = {
    0: [255, 0, 0],
    1: [0, 255, 0],
    2: [0, 0, 255],
    3: [255, 255, 0],
}


def ping_coroutine(location: list[float], color: list[int], name: str) -> PostRenderCoroutine:
    r, g, b = color
    duration = 10.0
    world_pos = uemath.Vector(location).to_ue_vector()
    while True:
        yield None
        canvas: unreal.UObject = yield  # type: ignore
        pc = get_pc()

        loc = uemath.Vector(pc.Pawn.Location)
        loc.z += pc.Pawn.EyeHeight
        screen_pos = canvas.Project(world_pos)

        _, text_size_x, text_size_y = canvas.TextSize(name, 1, 1)
        canvas.SetDrawColor(r, g, b, 255)
        canvas.SetBGColor(0, 0, 0, 180)
        canvas.SetPos(screen_pos.X - text_size_x, screen_pos.Y - text_size_y)
        canvas.DrawTextWithBG(name)

        duration -= Time.unscaled_delta_time
        if duration <= 0:
            break


@broadcast.json_message
def ping_location(*, location: list[float], color: list[int], name: str) -> None:
    pc = get_pc()
    r, g, b = color
    x, y, z = location
    pc.DrawDebugSphere(
        Center=make_struct("Vector", X=x, Y=y, Z=z),
        Radius=20,
        Segments=12,
        R=int(r),
        G=int(g),
        B=int(b),
        bPersistentLines=True,
        Lifetime=10.0,
    )
    start_coroutine_post_render(ping_coroutine(location, color, name))


def color_by_player() -> list[int]:
    player_id: int = get_pc().PlayerReplicationInfo.PlayerID
    return colors[player_id % len(colors)]


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
    coop_support=CoopSupport.ClientSide,
)
add_network_functions(mod)
