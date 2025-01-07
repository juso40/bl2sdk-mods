from __future__ import annotations

import math as m
from collections.abc import Iterator
from typing import TYPE_CHECKING, cast

import unrealsdk

import uemath.structs.rotators as r
from uemath.constants import RADIANS_TO_URU
from uemath.umath import clamp

if TYPE_CHECKING:
    from uemath.uetypes import UERotator, UEVector  # type: ignore

Scalar = float | int
Sequence3 = tuple[Scalar, Scalar, Scalar] | list[Scalar]
type Rot = r.Rotator | tuple[int, int, int]
type Vec3 = "Vector" | tuple[Scalar, Scalar, Scalar]


class Vector:
    """Wrapper Class for UE3 Vector Structs and their math operations."""

    def __init__(
        self,
        data: UEVector | UERotator | Vector | Sequence3 | r.Rotator | None = None,
        *,
        x: float | None = None,
        y: float | None = None,
        z: float | None = None,
    ) -> None:
        """Initialize a Vector from a sequence of 3 scalars, or from a UE3 Vector or Rotator.

        If data is an UE3 Rotator it will be converted to a normalized Vector.
        Optional Parameters x, y, and z can be used to override the values from data.
        """
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        if data is not None:
            if isinstance(data, list | tuple):
                self.x, self.y, self.z = data
            elif isinstance(data, r.Rotator):
                x, y, z = data.to_vector()
            elif isinstance(data, Vector):
                self.x = data.x
                self.y = data.y
                self.z = data.z
            else:
                try:
                    # Try to get the values from a UE3 Vector
                    self.x = data.X
                    self.y = data.Y
                    self.z = data.Z
                except AttributeError:
                     # Try to get the values from a UE3 Rotator
                    vec: Vector = cast("Vector", r.Rotator(data).to_vector())
                    self.x = vec.x
                    self.y = vec.y
                    self.z = vec.z
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if z is not None:
            self.z = z

    def __add__(self, other: Vec3) -> Vector:
        """Add another vector to this one."""
        if isinstance(other, Vector):
            return Vector((self.x + other.x, self.y + other.y, self.z + other.z))
        if isinstance(other, list | tuple):
            return Vector((self.x + other[0], self.y + other[1], self.z + other[2]))
        raise TypeError(f"Cannot add {type(other)} to Vector.")

    def __radd__(self, other: Vec3) -> Vector:
        """Add another vector to this one."""
        return self + other

    def __sub__(self, other: Vec3) -> Vector:
        """Subtract another vector from this one."""
        if isinstance(other, Vector):
            return Vector((self.x - other.x, self.y - other.y, self.z - other.z))
        if isinstance(other, list | tuple):
            return Vector((self.x - other[0], self.y - other[1], self.z - other[2]))
        raise TypeError(f"Cannot subtract {type(other)} from Vector.")

    def __rsub__(self, other: Vec3) -> Vector:
        """Subtract this vector from another one."""
        if isinstance(other, Vector):
            return Vector((other.x - self.x, other.y - self.y, other.z - self.z))
        if isinstance(other, list | tuple):
            return Vector((other[0] - self.x, other[1] - self.y, other[2] - self.z))
        raise TypeError(f"Cannot subtract Vector from {type(other)}.")

    def __mul__(self, other: Scalar | Vec3) -> Vector:
        """Multiply this vector by a scalar or do a cross product with another vector."""
        if isinstance(other, float | int):
            return Vector((self.x * other, self.y * other, self.z * other))
        if isinstance(other, Vector):
            return self.cross(other)
        if isinstance(other, list | tuple):
            return self.cross(Vector(other))
        raise TypeError(f"Cannot multiply Vector by {type(other)}.")

    def __rmul__(self, other: Scalar | Vec3) -> Vector:
        """Multiply this vector by a scalar or do a cross product with another vector."""
        if isinstance(other, float | int):
            return self * other
        if isinstance(other, Vector):
            return other.cross(self)
        if isinstance(other, list | tuple):
            return Vector(other).cross(self)
        raise TypeError(f"Cannot multiply Vector by {type(other)}.")

    def __matmul__(self, other: Vec3) -> float:
        """Do a dot product with another vector."""
        if isinstance(other, Vector):
            return self.dot(other)
        if isinstance(other, list | tuple):
            return self.dot(Vector(other))
        raise TypeError(f"Cannot dot Vector with {type(other)}.")

    def __rmatmul__(self, other: Vec3) -> float:
        """Do a dot product with another vector."""
        if isinstance(other, Vector):
            return other.dot(self)
        if isinstance(other, list | tuple):
            return Vector(other).dot(self)
        raise TypeError(f"Cannot dot Vector with {type(other)}.")

    def __truediv__(self, other: Scalar) -> Vector:
        """Divide this vector by a scalar."""
        return Vector((self.x / other, self.y / other, self.z / other))

    def __rtruediv__(self, other: Scalar) -> Vector:
        """Divide this vector by a scalar."""
        if isinstance(other, float | int):
            return self / other
        raise TypeError(f"Cannot divide {type(other)} by Vector.")

    def __eq__(self, other: Vec3) -> bool:
        """Check if this vector is equal to another."""
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y and self.z == other.z
        return self.x == other[0] and self.y == other[1] and self.z == other[2]

    def __ne__(self, other: Vec3) -> bool:
        """Check if this vector is not equal to another."""
        return not self == other

    def __str__(self) -> str:
        """Return a string representation of this vector."""
        return f"Vector({self.x}, {self.y}, {self.z})"

    def __repr__(self) -> str:
        """Return a string representation of this vector."""
        return self.__str__()

    def __getitem__(self, item: int) -> float:
        """Return the value of this vector at the given index."""
        return (self.x, self.y, self.z)[item]

    def __setitem__(self, key: int, value: float) -> None:
        """Set the value of this vector at the given index."""
        vals = [self.x, self.y, self.z]
        vals[key] = value
        self.x, self.y, self.z = vals

    def __iter__(self) -> Iterator[float]:
        """Return an iterator for this vector."""
        return iter((self.x, self.y, self.z))

    def __len__(self) -> int:
        """Return the length of this vector."""
        return 3

    def __hash__(self) -> int:
        """Return a hash of this vector."""
        return hash((self.x, self.y, self.z))

    def __bool__(self) -> bool:
        """Return if this vector is truthy."""
        return bool(self.x or self.y or self.z)

    def __neg__(self) -> Vector:
        """Return the negative of this vector."""
        return Vector((-self.x, -self.y, -self.z))

    def to_rotator(self, to_tuple: bool = False) -> Rot:
        """Convert a normalized Vector to a Rotator.

        This can be used to convert a look direction to a rotation. Roll is always 0.
        """
        nvec = self.normalized
        pitch = m.atan2(nvec.z, m.sqrt(nvec.x * nvec.x + nvec.y * nvec.y)) * RADIANS_TO_URU
        yaw = m.atan2(nvec.y, nvec.x) * RADIANS_TO_URU
        roll = 0

        tup = (int(pitch), int(yaw), roll)
        return tup if to_tuple else r.Rotator(tup)

    def to_tuple(self) -> tuple[float, float, float]:
        """Return a tuple representation of this vector."""
        return self.x, self.y, self.z

    def to_ue_vector(self) -> UEVector:
        """Return a UE3 Vector representation of this vector."""
        return cast("UEVector", unrealsdk.make_struct("Vector", X=self.x, Y=self.y, Z=self.z))

    @property
    def magnitude(self) -> float:
        """Return the magnitude of this vector."""
        return m.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    @property
    def magnitude_squared(self) -> float:
        """Return the magnitude squared of this vector."""
        return self.x * self.x + self.y * self.y + self.z * self.z

    @property
    def normalized(self) -> Vector:
        """Return a normalized copy of this vector."""
        return Vector(
            (self.x / self.magnitude, self.y / self.magnitude, self.z / self.magnitude),
        )

    def normalize(self) -> Vector:
        """Return this vector normalized."""
        mag = self.magnitude
        if mag == 0:
            return self
        self.x /= mag
        self.y /= mag
        self.z /= mag
        return self

    def dot(self, other: Vector) -> float:
        """Return the dot product of this vector and another."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vector) -> Vector:
        """Return the cross product of this vector and another."""
        return Vector(
            (
                self.y * other.z - self.z * other.y,
                self.z * other.x - self.x * other.z,
                self.x * other.y - self.y * other.x,
            ),
        )

    def distance(self, other: Vector) -> float:
        """Return the distance between this vector and another."""
        return (self - other).magnitude

    def distance_squared(self, other: Vector) -> float:
        """Return the distance squared between this vector and another."""
        return (self - other).magnitude_squared

    def angle(self, other: Vector) -> float:
        """Return the angle between this vector and another."""
        return m.acos(clamp(self.normalized.dot(other.normalized), -1, 1)) * RADIANS_TO_URU

    def rotate_towards(self, target: Vector, max_rotation_delta: float = 360) -> Vector:
        """Rotate this vector towards another vector by a maximum amount per step.

        :param target: The target vector to rotate towards.
        :param max_rotation_delta: The maximum angle in radians allowed for this rotation.
        """
        angle = self.angle(target)
        if angle == 0:
            return self
        return self.rotate(
            self.cross(target).normalized,
            min(angle, max_rotation_delta),
        )

    def rotate(self, axis: Vector, angle: float) -> Vector:
        """Rotate this vector around an axis by an angle in radians.

        See https://en.wikipedia.org/wiki/Rodrigues%27_rotation_formula
        :param axis: The axis to rotate around.
        :param angle: The angle to rotate by. In radians.
        """
        axis.normalize()
        sin = m.sin(angle)
        cos = m.cos(angle)
        return self * cos + axis.cross(self) * sin + axis * axis.dot(self) * (1 - cos)

    def lerp(self, other: Vector, alpha: float) -> Vector:
        """Return a linear interpolation between this vector and another.

        :param other: The other vector to interpolate towards.
        :param alpha: The amount to interpolate by.
        """
        return self + (other - self) * alpha

    def rotate_around(self, origin: Vector, rotation: Rot) -> Vector:
        """Rotate this vector around an origin by a rotation.

        :param origin: The origin to rotate around.
        :param rotation: The rotation to rotate by.
        """
        rotation = r.Rotator(rotation)
        offset = self - origin
        x, y, z = rotation.get_axes()
        return offset.x * x + offset.y * y + offset.z * z + origin
