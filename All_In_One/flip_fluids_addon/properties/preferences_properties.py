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
        StringProperty,
        FloatProperty,
        CollectionProperty,
        EnumProperty
        )

from ..ui import helper_ui
from ..utils import version_compatibility_utils as vcu


class FLIPFluidGPUDevice(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        cls.name = StringProperty()
        cls.description = StringProperty()
        cls.score = FloatProperty()


    @classmethod
    def unregister(cls):
        pass


class FLIPFluidAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__.split(".")[0]

    enable_helper = BoolProperty(
                name="Enable Helper Toolbox",
                description="Enable the FLIP Fluid helper menu in the 3D view toolbox."
                    " This menu contains operators to help with workflow and simulation setup.",
                default=True,
                update=lambda self, context: self._update_enable_helper(context),
                options={'HIDDEN'},
                )
    exec(vcu.convert_attribute_to_28("enable_helper"))

    selected_gpu_device = EnumProperty(
                name="GPU Compute Device",
                description="Device that will be used for GPU acceleration features",
                items=lambda self, context=None: self._get_gpu_device_enums(context),
                )
    exec(vcu.convert_attribute_to_28("selected_gpu_device"))

    gpu_devices = CollectionProperty(type=FLIPFluidGPUDevice)
    exec(vcu.convert_attribute_to_28("gpu_devices"))

    is_gpu_devices_initialized = BoolProperty(False)
    exec(vcu.convert_attribute_to_28("is_gpu_devices_initialized"))


    def _update_enable_helper(self, context):
        if self.enable_helper:
            try:
                helper_ui.register()
            except:
                pass
        else:
            try:
                helper_ui.unregister()
            except:
                pass


    def draw(self, context):
        column = self.layout.column(align=True)

        split = column.split()
        column_left = split.column(align=True)
        column_right = split.column()

        helper_column = column_left.column()
        helper_column.prop(self, "enable_helper")
        helper_column.separator()
        helper_column.separator()

        column_left.label(text="User Settings:")
        column_left.operator("flip_fluid_operators.preferences_import_user_data", icon="IMPORT")
        column_left.operator("flip_fluid_operators.preferences_export_user_data", icon="EXPORT")
        column_left.separator()
        column_left.separator()

        column_left.label(text="Info:")
        column_left.operator(
                "flip_fluid_operators.check_for_updates", 
                text="Check for Updates", 
                icon="WORLD"
            )
        column_left.separator()


    def _get_gpu_device_enums(self, context=None):
        device_enums = []
        for d in self.gpu_devices:
            device_enums.append((d.name, d.name, d.description))
        return device_enums



def load_post():
    id_name = __name__.split(".")[0]
    preferences = vcu.get_blender_preferences(bpy.context).addons[id_name].preferences
    if not preferences.enable_helper:
        helper_ui.unregister()


def register():
    bpy.utils.register_class(FLIPFluidGPUDevice)
    bpy.utils.register_class(FLIPFluidAddonPreferences)


def unregister():
    bpy.utils.unregister_class(FLIPFluidGPUDevice)
    bpy.utils.unregister_class(FLIPFluidAddonPreferences)
