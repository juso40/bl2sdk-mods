from mods_base import Library, ObjectFlags, build_mod, get_pc, hook
from unrealsdk import find_all
from unrealsdk.hooks import Type
from unrealsdk.unreal import UObject

from . import commandline, options

mod = build_mod(
    cls=Library, options=[options.quick_mode, options.character_button, options.save_id]
)
mod.load_settings()

character_arg = commandline.get_character_arg()


@hook("WillowGame.WillowGameViewportClient:Tick", Type.POST_UNCONDITIONAL, immediately_enable=True)
def hook_skip_to_main_menu(_1, _2, _3, _4) -> None:  # noqa: ANN001
    for obj in find_all("WillowGame.WillowGFxMoviePressStart"):
        if obj.ObjectFlags & (0x400 | 0x200):
            continue
        if options.quick_mode.value:
            obj.BeginStartupProcess()
        else:
            obj.DoDlcEnumeration()
            obj.DownloadPatcherFiles()
            obj.DoSparkAuthentication()
            obj.DoStartupDeviceSelection()
            obj.CreateSession()
            obj.ContinueToMenu()

    hook_skip_to_main_menu.disable()


@hook("WillowGame.FrontendGFxMovie:Start", Type.POST_UNCONDITIONAL)
def hook_start_game(obj: UObject, _2, _3, _4) -> None:  # noqa: ANN001
    obj.LaunchSaveGame(get_pc().GetCurrentPlaythrough())
    hook_start_game.disable()


@hook("WillowGame.WillowPlayerController:ConditionalLoadDefaultSaveGame")
def hook_load_character(obj: UObject, _2, _3, _4) -> None:  # noqa: ANN001
    save_id_arg: int | None = None

    if character_arg is not None:
        save_id_arg = commandline.save_id_for_character_arg(character_arg)
    else:
        save_id_arg = options.save_id.value

    if save_id_arg is not None:
        obj.SetProfileSettingInt(116, save_id_arg)
        hook_start_game.enable()

    hook_load_character.disable()


if character_arg == "":
    hook_start_game.enable()
elif character_arg is not None:
    hook_load_character.enable()
elif options.save_id.value == options.UniqueSaveID.LastCharacter:
    hook_start_game.enable()
elif options.save_id.value != options.UniqueSaveID.NoCharacter:
    hook_load_character.enable()
