from mods_base import Library, build_mod

from .structs import Rotator, Vector
from .umath import (
    clamp,
    distance,
    dot_product,
    euler_rotate_vector_2d,
    get_axes,
    look_at,
    magnitude,
    normalize,
    rotator_to_vector,
    round_to_multiple,
    square_distance,
    vector_to_rotator,
    world_to_screen,
)

__all__ = [
    "Rotator",
    "Vector",
    "clamp",
    "distance",
    "dot_product",
    "euler_rotate_vector_2d",
    "get_axes",
    "look_at",
    "magnitude",
    "normalize",
    "rotator_to_vector",
    "round_to_multiple",
    "square_distance",
    "vector_to_rotator",
    "world_to_screen",
]


__version__: str
__version_info__: tuple[int, ...]


mod = build_mod(cls=Library, hooks=[])
