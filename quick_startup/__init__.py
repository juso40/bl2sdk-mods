from mods_base import Library, build_mod, hook, options
from unrealsdk import find_all
from unrealsdk.hooks import Type

quick_mode = options.BoolOption(
    "Safe Mode",
    True,
    description="Starts the game once everything is loaded. If false, skipps everything.",
)
mod = build_mod(cls=Library, options=[quick_mode])
mod.load_settings()


@hook("WillowGame.WillowGameViewportClient:Tick", Type.POST_UNCONDITIONAL, immediately_enable=True)
def hook_skip_to_main_menu(_1, _2, _3, _4) -> None:  # noqa: ANN001
    for obj in find_all("WillowGame.WillowGFxMoviePressStart"):
        if obj.ObjectFlags & (0x400 | 0x200):
            continue
        if quick_mode.value:
            obj.BeginStartupProcess()
        else:
            obj.DoDlcEnumeration()
            obj.DownloadPatcherFiles()
            obj.DoSparkAuthentication()
            obj.DoStartupDeviceSelection()
            obj.CreateSession()
            obj.ContinueToMenu()

    hook_skip_to_main_menu.disable()
