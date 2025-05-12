from __future__ import annotations

import random
from collections.abc import Iterable
from functools import lru_cache
from traceback import print_exc
from typing import TYPE_CHECKING, cast

from unrealsdk import find_all, find_object, make_struct, unreal

if TYPE_CHECKING:
    from common import MaterialInstanceConstant, Object, Texture

    make_linear_color = Object.LinearColor.make_struct

else:
    make_linear_color = make_struct


class Materials:
    selected: MaterialInstanceConstantProxy | None = None

    @staticmethod
    @lru_cache(maxsize=1)
    def all_materials(search: str) -> list[str]:
        return [m.PathName(m) for m in find_all("MaterialInstanceConstant") if search.lower() in m.PathName(m).lower()]

    @staticmethod
    def select(material_name: str) -> bool:
        try:
            Materials.selected = MaterialInstanceConstantProxy(
                find_object("MaterialInstanceConstant", material_name),
                material_name,
            )
            return True
        except AttributeError:
            print_exc()
            return False


class Texture2D:
    search: str = ""
    index: int = 0

    backup: unreal.UObject | None = None
    texture_parameter: str = ""

    @staticmethod
    @lru_cache(maxsize=1)
    def all_textures(search: str) -> list[str]:
        return [t.PathName(t) for t in find_all("Texture2D") if search.lower() in t.PathName(t).lower()]


class MaterialInstanceConstantProxy:
    def __init__(
        self,
        material_instance_constant: unreal.UObject,
        path_name: str = "",
    ) -> None:
        self.material_instance_constant: MaterialInstanceConstant = cast(
            "MaterialInstanceConstant",
            material_instance_constant,
        )
        self.path_name = path_name or material_instance_constant.PathName(
            material_instance_constant,
        )
        self.vector_parameters: dict[str, tuple[float, float, float, float]] = {}
        self.scalar_parameters: dict[str, float] = {}
        self.texture_parameters: dict[str, str] = {}
        self.update_parameters()

    def parents(self) -> list[unreal.UObject]:
        """Index -1 is the root parent. Index 0 is the object itself."""
        parent: unreal.UObject = self.material_instance_constant
        parents: list[unreal.UObject] = [parent]
        try:
            while parent.Parent:
                parent = parent.Parent
                parents.append(parent)
        except AttributeError:
            pass  # The final parent is a Material, which has no parent
        return parents

    def update_vector_parameters(self) -> None:
        parents = self.parents()

        for expression in parents[-1].Expressions:
            if expression and expression.Class.Name == "MaterialExpressionVectorParameter":
                # Just add any default value for now. Most skins overwrite them anyway.
                self.vector_parameters[expression.ParameterName] = (1.0, 1.0, 1.0, 1.0)

        # Walk from root to our material and update all VectorParameters
        for material in parents[::-1]:
            if material.Class.Name == "Material" or not material.VectorParameterValues:
                continue
            for param in material.VectorParameterValues:
                p_val = param.ParameterValue
                self.vector_parameters[param.ParameterName] = (
                    p_val.R,
                    p_val.G,
                    p_val.B,
                    p_val.A,
                )

    def update_scalar_parameters(self) -> None:
        parents = self.parents()

        for expression in parents[-1].Expressions:
            if expression and expression.Class.Name == "MaterialExpressionScalarParameter":
                # Just add any default value for now. Most skins overwrite them anyway.
                self.scalar_parameters[expression.ParameterName] = 1.0

        # Walk from root to our material and update all ScalarParameters
        for material in parents[::-1]:
            if material.Class.Name == "Material" or not material.ScalarParameterValues:
                continue
            for param in material.ScalarParameterValues:
                self.scalar_parameters[param.ParameterName] = material.GetScalarParameterValue(param.ParameterName, 0)[
                    1
                ]

    def update_texture_parameters(self) -> None:
        parents = self.parents()

        for expression in parents[-1].Expressions:
            if expression and expression.Class.Name == "MaterialExpressionTextureSampleParameter2D":
                # Just add any default value for now. Most skins overwrite them anyway.
                self.texture_parameters[expression.ParameterName] = ""

        # Walk from root to our material and update all TextureParameters
        for material in parents[::-1]:
            if material.Class.Name == "Material" or not material.TextureParameterValues:
                continue
            for param in material.TextureParameterValues:
                self.texture_parameters[param.ParameterName] = param.ParameterValue

    def update_parameters(self) -> None:
        self.texture_parameters = {}
        self.vector_parameters = {}
        self.scalar_parameters = {}
        self.update_texture_parameters()
        self.update_vector_parameters()
        self.update_scalar_parameters()

    def randomize_parameters(
        self,
        locked_parameters: Iterable[str] | None = None,
    ) -> None:
        if locked_parameters is None:
            locked_parameters = []

        for parameter_name in self.vector_parameters:
            if parameter_name not in locked_parameters:
                if "color" in parameter_name.lower():
                    r = random.random() * 2.55
                    g = random.random() * 2.55
                    b = random.random() * 2.55
                    a = random.random() * 2.55
                else:
                    r = random.random() * 20
                    g = random.random() * 20
                    b = random.random() * 20
                    a = random.random() * 20
                self.set_vector_parameter_value(parameter_name, (r, g, b, a))

        for parameter_name in self.scalar_parameters:
            if parameter_name not in locked_parameters:
                self.set_scalar_parameter_value(parameter_name, random.random() * 10)

        for parameter_name in self.texture_parameters:
            if parameter_name not in locked_parameters:
                textures = Texture2D.all_textures("")
                if not textures:
                    return
                texture = random.choice(textures)
                self.set_texture_parameter_value(parameter_name, texture)

        self.update_parameters()

    def set_texture_parameter_value(
        self,
        parameter_name: str,
        parameter_value: str | unreal.UObject | None,
    ) -> None:
        if not Materials.selected:
            return
        if isinstance(parameter_value, str):
            parameter_value = find_object("Texture2D", parameter_value)
        parameter_value = cast("Texture", parameter_value)
        Materials.selected.material_instance_constant.SetTextureParameterValue(
            parameter_name,
            parameter_value,
        )

    def get_texture_parameter_value(self, parameter_name: str) -> unreal.UObject | None:
        if not Materials.selected:
            return None
        return Materials.selected.material_instance_constant.GetTextureParameterValue(parameter_name, None)[1]

    def set_vector_parameter_value(
        self,
        parameter_name: str,
        parameter_value: tuple[float, float, float, float],
    ) -> None:
        if not Materials.selected:
            return
        r, g, b, a = parameter_value
        Materials.selected.material_instance_constant.SetVectorParameterValue(
            parameter_name,
            make_linear_color(
                "LinearColor",
                False,  # type: ignore
                R=r,
                G=g,
                B=b,
                A=a,
            ),
        )

    def set_scalar_parameter_value(
        self,
        parameter_name: str,
        parameter_value: float,
    ) -> None:
        if not Materials.selected:
            return
        Materials.selected.material_instance_constant.SetScalarParameterValue(
            parameter_name,
            parameter_value,
        )
