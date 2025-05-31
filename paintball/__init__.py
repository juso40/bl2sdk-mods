import contextlib
from random import choice
from typing import Any

from mods_base import ENGINE, build_mod, hook, options
from unrealsdk import construct_object, find_object, load_package, logging, make_struct, unreal
from unrealsdk.hooks import Block, Type, prevent_hooking_direct_calls

colors = [
    (200, -5, -5, 100),  # Red
    (-5, 200, -5, 100),  # Green
    (-5, -5, 200, 100),  # Blue
    (200, 200, -5, 100),  # Yellow
    (-5, 200, 200, 100),  # Cyan
    (200, -5, 200, 100),  # Magenta
]
decal_map = {}

replace_particles = options.BoolOption(
    "Confetti Particles",
    True,
    description="Replace the explosion particles with confetti particles.",
)


def make_paintball_mic(decal: unreal.UObject) -> None:
    new_decals = []
    decal_map[decal._path_name()] = new_decals
    for i in range(0, 5):
        new_decal = construct_object(
            cls=decal.Class,
            outer=decal.Outer,
            template_obj=decal.Class.ClassDefaultObject,
            name=f"{decal.Name}_Paintball_{i}",
            flags=0x400004000,
        )
        with unreal.notify_changes():
            new_decal.Parent = decal
        new_decal.ObjectArchetype = decal.ObjectArchetype
        new_decal.ObjectFlags |= 0x4000

        new_decals.append(unreal.WeakPointer(new_decal))
        (
            r,
            g,
            b,
            a,
        ) = colors[i]
        col = make_struct("LinearColor", R=r, G=g, B=b, A=a)
        new_decal.SetVectorParameterValue("DecalTint", col)
        new_decal.SetVectorParameterValue("Color", col)


def set_varying(varying: unreal.UObject) -> None:
    color = choice(colors)
    r, g, b, a = color
    col = make_struct("LinearColor", R=r, G=g, B=b, A=a)
    varying.SetVectorParameterValue(
        "Color_Multiplier",
        col,
    )
    for param in varying.VectorParameterValues:
        if param.ParameterName == "Color_Multiplier":
            param.ParameterValueCurve.InterpMethod = 0
            break


@hook("Engine.DecalComponent:SetDecalMaterial", Type.PRE)
def spawn_decal(
    obj: unreal.UObject,
    args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None | tuple[type[Block], Any] | type[Block]:
    mic = args.NewDecalMaterial
    if mic.Class.Name == "MaterialInstanceTimeVarying":
        set_varying(mic)
        return None

    if mic._path_name() not in decal_map:
        make_paintball_mic(mic)

    paintball_decal = choice(decal_map[mic._path_name()])()
    if paintball_decal is None:
        logging.error(f"Failed to get paintball decal for {mic._path_name()}")
        return None
    obj.DecalMaterial = paintball_decal
    return Block


@hook("Engine.Emitter:SetTemplate", Type.PRE)
def set_emitter_template(
    obj: unreal.UObject,
    args: unreal.WrappedStruct,
    _ret: Any,
    _func: unreal.BoundFunction,
) -> None | tuple[type[Block], Any] | type[Block]:
    if not replace_particles.value:
        return None
    if "FX_WEP_Explosions.Particles" in str(args.NewTemplate):
        with prevent_hooking_direct_calls():
            obj.SetTemplate(find_object("ParticleSystem", "FX_ENV_Misc.Particles.Part_Confetti"), args.bDestroyOnFinish)
        return Block
    return None


def on_enable() -> None:
    load_package("SanctuaryAir_Dynamic")
    find_object("ParticleSystem", "FX_ENV_Misc.Particles.Part_Confetti").ObjectFlags |= 0x4000
    ENGINE.GetCurrentWorldInfo().ForceGarbageCollection(True)


def on_disable() -> None:
    with contextlib.suppress(ValueError):
        find_object("ParticleSystem", "FX_ENV_Misc.Particles.Part_Confetti").ObjectFlags &= ~0x4000


mod = build_mod(
    on_enable=on_enable,
    on_disable=on_disable,
    options=[replace_particles],
)
