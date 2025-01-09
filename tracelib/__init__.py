from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING, cast

from mods_base import Library, build_mod, get_pc
from unrealsdk import construct_object, find_all, make_struct, unreal

import uemath

if TYPE_CHECKING:
    from common import Actor, Object, WillowPlayerController, WillowWeapon

__version__: str
__version_info__: tuple[int, ...]


def magic_trace_weapon() -> WillowWeapon:
    @cache
    def create_gun() -> unreal.WeakPointer[WillowWeapon]:
        weapons = list(find_all("WillowWeapon"))
        default = weapons[0]
        template = weapons[1]

        weap = cast(
            "WillowWeapon",
            construct_object(
                cls="WillowWeapon",
                template_obj=template,
                outer=default.Outer,
                name="MagicTraceWeapon",
            ),
        )
        return unreal.WeakPointer(weap)

    if (wp := create_gun())():
        return cast("WillowWeapon", wp())
    create_gun.cache_clear()
    return cast("WillowWeapon", create_gun()())


def trace_from_player_pov(debug_trace: bool = False) -> Actor.ImpactInfo:
    """Returns the ImpactInfo of the current trace, starting from the players pov."""
    pc = cast("WillowPlayerController", get_pc())
    try:
        trace_start: Object.Vector = cast("Object.Vector", make_struct("Vector"))
        trace_start.X = pc.Pawn.Location.X
        trace_start.Y = pc.Pawn.Location.Y
        trace_start.Z = pc.Pawn.Location.Z + pc.Pawn.EyeHeight
    except AttributeError:
        trace_start: Object.Vector = pc.Location

    forward = uemath.Vector(pc.Rotation) * 50
    trace_start = (uemath.Vector(trace_start) + forward).to_ue_vector()
    trace_end = (uemath.Vector(trace_start) + forward * 10000000).to_ue_vector()

    return trace(trace_start, trace_end, debug_trace=debug_trace)


def trace(start: Object.Vector, end: Object.Vector, debug_trace: bool = False) -> Actor.ImpactInfo:
    """Returns the ImpactInfo of the trace from start to end."""
    trace_info = magic_trace_weapon().CalcWeaponFire(
        StartTrace=start,
        EndTrace=end,
        bTestTrace=True,
    )[0]
    if debug_trace:
        # Draw a debug line from start to end
        (pc := cast("WillowPlayerController", get_pc())).DrawDebugLine(
            LineStart=start,
            LineEnd=end,
            R=255,
            G=0,
            B=0,
            bPersistentLines=True,
            Lifetime=10.0,
        )
        # Debug Draw From Start to Hit Location
        pc.DrawDebugLine(
            LineStart=trace_info.StartTrace,
            LineEnd=trace_info.HitLocation,
            R=0,
            G=255,
            B=0,
            bPersistentLines=True,
            Lifetime=10.0,
        )
        # Debug Draw Start Trace
        pc.DrawDebugSphere(
            Center=trace_info.StartTrace,
            Radius=50,
            Segments=32,
            R=0,
            G=255,
            B=0,
            bPersistentLines=True,
            Lifetime=10.0,
        )
        # Debug Draw Hit Location
        pc.DrawDebugSphere(
            Center=trace_info.HitLocation,
            Radius=50,
            Segments=32,
            R=0,
            G=0,
            B=255,
            bPersistentLines=True,
            Lifetime=10.0,
        )
        # Debug Draw Hit Normal
        pc.DrawDebugLine(
            LineStart=trace_info.HitLocation,
            LineEnd=(
                n := (uemath.Vector(trace_info.HitLocation) + uemath.Vector(trace_info.HitNormal) * 200).to_ue_vector()
            ),
            R=0,
            G=0,
            B=255,
            bPersistentLines=True,
            Lifetime=10.0,
        )
        pc.DrawDebugCone(
            Origin=n,
            Direction=(-uemath.Vector(trace_info.HitNormal)).to_ue_vector(),
            Length=100,
            AngleWidth=0.25,
            AngleHeight=0.25,
            NumSides=256,
            DrawColor=cast("Object.Color", make_struct("Color", R=0, G=0, B=255, A=255)),
            bPersistentLines=True,
            Lifetime=10.0,
        )

    return trace_info


mod = build_mod(
    cls=Library,
)
