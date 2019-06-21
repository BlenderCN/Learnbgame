# Blender FLIP Fluid Add-on
# Copyright (C) 2019 Ryan L. Guy
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.props import (
        BoolProperty,
        IntProperty,
        StringProperty,
        PointerProperty
        )


class FlipFluidMaterialLibraryProperties(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Material.flip_fluid_material_library = PointerProperty(
                name="Flip Fluid Material Library Properties",
                description="",
                type=cls,
                )

        # Material Library Data
        cls.is_library_material = BoolProperty(default=False)
        cls.library_name = StringProperty(default="")
        cls.imported_name = StringProperty(default="")
        cls.data_block_id = StringProperty(default="-1")

        # Preset Library Data
        cls.is_preset_material = BoolProperty(default=False)
        cls.preset_identifier = StringProperty(default="")
        cls.preset_blend_identifier = StringProperty(default="")
        cls.is_fake_user_set_by_addon = BoolProperty(default=False)
        cls.skip_preset_unload = BoolProperty(default=False)
        

    @classmethod
    def unregister(cls):
        del bpy.types.Material.flip_fluid_material_library


    def activate(self, material_object, library_name):
        self.is_library_material = True
        self.library_name = library_name
        self.imported_name = material_object.name
        self.data_block_id = str(material_object.as_pointer())


    def deactivate(self):
        self.property_unset("is_library_material")
        self.property_unset("library_name")
        self.property_unset("imported_name")
        self.property_unset("data_block_id")


    def reinitialize_data_block_id(self, material_object):
        self.data_block_id = str(material_object.as_pointer())


    def is_original_data_block(self, material_object):
        return self.data_block_id == str(material_object.as_pointer())


def register():
    bpy.utils.register_class(FlipFluidMaterialLibraryProperties)


def unregister():
    bpy.utils.unregister_class(FlipFluidMaterialLibraryProperties)