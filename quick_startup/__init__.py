from mods_base import hook
from unrealsdk import find_all
from unrealsdk.hooks import Type
from mods_base import build_mod, Library


@hook("WillowGame.WillowGameViewportClient:Tick", Type.POST_UNCONDITIONAL, immediately_enable=True)
def hook_skip_to_main_menu(_1, _2, _3, _4) -> None:  # noqa: ANN001
    for obj in find_all("WillowGame.WillowGFxMoviePressStart"):
        if obj.ObjectFlags & (0x400 | 0x200):
            continue
        obj.DoDlcEnumeration()
        obj.DownloadPatcherFiles()
        obj.DoSparkAuthentication()
        obj.DoStartupDeviceSelection()
        obj.CreateSession()
        obj.ContinueToMenu()

    hook_skip_to_main_menu.disable()


mod = build_mod(cls=Library)
