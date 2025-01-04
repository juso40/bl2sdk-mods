from collections.abc import Callable
from functools import partial

from mods_base import ENGINE, UObject, build_mod, get_pc
from mods_base.keybinds import EInputEvent, keybind
from unrealsdk.unreal import WeakPointer

__version__: str
__version_info__: tuple[int, ...]


class PhotoModeState:
    pawn_backup: WeakPointer = WeakPointer()
    active_modifier: Callable[[int], None] | None = None


@keybind("Photo Mode", "P", description="Toggle photo mode")
def toggle_photo_mode() -> None:
    world_info: UObject = ENGINE.GetCurrentWorldInfo()
    pc: UObject = get_pc()
    # If we have a pawn backup, we are in photo mode
    if pawn := PhotoModeState.pawn_backup():
        PhotoModeState.pawn_backup = WeakPointer()  # invalidate the backup
        pc.Possess(pawn, True)
        pc.DisplayHUD()
        world_info.bPlayersOnly = False
        pc.Rotation.Roll = 0
        pc.SetFOV(pc.DefaultFOV)
    else:
        PhotoModeState.pawn_backup = WeakPointer(pc.Pawn)
        pc.Unpossess()
        pc.HideHUD()
        pc.ServerSpectate()
        world_info.bPlayersOnly = True


def camera_roll_modifier(val: int) -> None:
    get_pc().Rotation.Roll += val * 128


def camera_fov_modifier(val: int) -> None:
    fov: int = (pc := get_pc()).FOVAngle
    fov = max(min(fov + val, 180), 4)
    pc.SetFOV(fov)


def camera_speed_modifier(val: int) -> None:
    speed: float = (pc := get_pc()).SpectatorCameraSpeed
    speed = max(min(speed + val * 50, 10000), 50)
    pc.SpectatorCameraSpeed = speed


def _switch_modifier(event: EInputEvent, mod: Callable[[int], None]) -> None:
    match event:
        case EInputEvent.IE_Pressed:
            PhotoModeState.active_modifier = mod
        case EInputEvent.IE_Released:
            PhotoModeState.active_modifier = None


def _modifier(val: int) -> None:
    if PhotoModeState.active_modifier:
        PhotoModeState.active_modifier(val)


_switch_modifier_fov = partial(_switch_modifier, mod=camera_fov_modifier)
_switch_modifier_roll = partial(_switch_modifier, mod=camera_roll_modifier)
_switch_modifier_speed = partial(_switch_modifier, mod=camera_speed_modifier)


mod = build_mod(
    keybinds=[
        toggle_photo_mode,
        keybind("Modifier +", "MouseScrollUp", lambda: _modifier(1), is_rebindable=False),
        keybind("Modifier -", "MouseScrollDown", lambda: _modifier(-1), is_rebindable=False),
        keybind(
            "Camera Speed",
            "LeftShift",
            _switch_modifier_speed,
            is_rebindable=False,
            event_filter=None,
        ),
        keybind(
            "Camera Roll",
            "R",
            _switch_modifier_roll,
            is_rebindable=False,
            event_filter=None,
        ),
        keybind(
            "Camera FOV",
            "F",
            _switch_modifier_fov,
            is_rebindable=False,
            event_filter=None,
        ),
    ],
)
