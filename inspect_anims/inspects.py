from importlib.resources import as_file, files
from typing import TYPE_CHECKING, cast

from mods_base import get_pc
from unrealsdk import find_object, logging

from animlib import AnimationSet

if TYPE_CHECKING:
    from common import WillowPlayerController, WillowPlayerPawn, WillowWeapon


WEAPON_CLIPS = {
    "Rifle": "1st_Person_AssaultRifle/Inspect",
    "SMG": "1st_Person_SMG/Inspect",
    "Pistol": "1st_Person_Pistol/Inspect",
    "SniperRifle": "1st_Person_SniperRifle/Inspect",
    "Shotgun": "1st_Person_Shotgun/Inspect",
    "RocketLauncher": "1st_Person_RocketLauncher/Inspect",
    "Unarmed": "1st_Person_Unarmed/Inspect",
}
CLIPS = tuple(WEAPON_CLIPS.values())

_animations: AnimationSet | None = None


def cancel_inspect(*, blend_out: float = 0.10) -> bool:
    """Stop a loaded inspection on the local pawn without loading assets."""
    animations = loaded_animations()
    pc = cast("WillowPlayerController | None", get_pc())
    if animations is None or pc is None:
        return False

    pawn = pc.GetWillowPlayerPawn()
    if pawn is None:
        return False

    for sequence in animations.sequences.values():  # noqa: SIM110
        if sequence.stop_arms(pawn, blend_out=blend_out):
            return True

    return False


def inspect_for_weapon(pawn: WillowPlayerPawn, weapon: WillowWeapon | None) -> None:
    hold_name = "Unarmed" if weapon is None else weapon.GetBodyWeaponHoldName()
    # manufacturer = weapon.GetManufacturer().Name
    #
    try:
        if get_animations()[WEAPON_CLIPS[hold_name]].play_arms(pawn) <= 0.0:
            logging.warning("the arms animation slot refused inspect")
    except KeyError:
        logging.dev_warning(f"Could not find any inspect AnimSequence for weapontype: {hold_name}")
    except (OSError, ValueError, RuntimeError) as error:
        logging.error(f"could not play inspect: {error}")


def _load_animations() -> AnimationSet:
    resource = files(__package__).joinpath("assets", "Anims.glb")

    with as_file(resource) as asset_path:
        return AnimationSet(
            asset_path,
            skin="Hands_Soldier",
            scene="Scene",
            clips=CLIPS,
            sample_rate=60.0,
            umodel=True,
        )


def get_animations() -> AnimationSet:
    """Create and configure the example set on first use, then reuse it."""
    global _animations  # noqa: PLW0603
    if _animations is None:
        animations = _load_animations()

        # Prepare the custom animation sequence notifies
        animations["1st_Person_Unarmed/Inspect"].add_notify(
            name="ARInspect",
            time=0.25,
            notify_class="AnimNotify_DialogEvent",
            EventTag=find_object(
                "GearboxDialogEventTag",
                "GD_Dialog_Player.VOBD_PL_Events.VOBD_PL_CO_Enter_CoOp_Game",
            ),
        )
        animations["1st_Person_AssaultRifle/Inspect"].add_notify(
            name="ARInspect",
            time=0.2,
            notify_class="AnimNotify_DialogEvent",
            EventTag=find_object(
                "GearboxDialogEventTag",
                "GD_Dialog_Player.VOBD_PL_Events.VOBD_PL_UI_Equip_Powerful_Loot",
            ),
        )
        animations["1st_Person_SMG/Inspect"].add_notify(
            name="SMGInspect",
            time=0.0,
            notify_class="AnimNotify_DialogEvent",
            EventTag=find_object(
                "GearboxDialogEventTag",
                "GD_Dialog_Player.VOBD_PL_Events.VOBD_PL_UI_Equip_Powerful_Loot",
            ),
        )

        pistol_inspect = animations["1st_Person_Pistol/Inspect"]
        pistol_inspect.add_ak_event(
            "PistolTwirl",
            0.40,
            "Ake_Wep_Pistols.Reloads.Ak_Play_Wep_Pistol_Twirl",
        )
        pistol_inspect.add_ak_event(
            "PistolSlap",
            0.80,
            "Ake_Obj_Pickup.Obj_Pickup_Equip.Ak_Play_Obj_Pickup_Equip_Rifle",
        )
        pistol_inspect.add_notify(
            "PistolInspectDialog",
            0.0,
            "AnimNotify_DialogEvent",
            EventTag=find_object("GearboxDialogEventTag", "GD_Dialog_Player.VOBD_PL_Events.VOBD_PL_PVP_Duel_Instigate"),
        )

        shotgun_inspect = animations["1st_Person_Shotgun/Inspect"]
        shotgun_inspect.add_ak_event(
            "ShotgunTwirl",
            0.50,
            "Ake_Wep_Pistols.Reloads.Ak_Play_Wep_Pistol_Twirl",
        )
        shotgun_inspect.add_notify(
            "ShotgunInspectDialog",
            0.0,
            "AnimNotify_DialogEvent",
            EventTag=find_object(
                "GearboxDialogEventTag",
                "GD_Dialog_Player.VOBD_PL_Events.VOBD_PL_UI_Equip_Powerful_Loot",
            ),
        )

        sniper_inspect = animations["1st_Person_SniperRifle/Inspect"]
        sniper_inspect.add_ak_event(
            "SniperSlap",
            2.75,
            "Ake_Obj_Pickup.Obj_Pickup_Equip.Ak_Play_Obj_Pickup_Equip_Rifle",
        )

        launcher_inspect = animations["1st_Person_RocketLauncher/Inspect"]
        launcher_inspect.add_ak_event(
            "LauncherEquip",
            2.9,
            "Ake_Obj_Pickup.Obj_Pickup.Ak_Play_Obj_Pickup_Rocket_Launcher",
        )
        launcher_inspect.add_notify(
            "LauncherDiag",
            0.0,
            "AnimNotify_DialogEvent",
            EventTag=find_object(
                "GearboxDialogEventTag",
                "GD_Dialog_Player.VOBD_PL_Events.VOBD_PL_UI_Equip_Powerful_Loot",
            ),
        )

        _animations = animations
    return _animations


def loaded_animations() -> AnimationSet | None:
    """Return the existing set without loading assets during mod shutdown."""
    return _animations
