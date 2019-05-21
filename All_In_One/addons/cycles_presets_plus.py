# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "Presets for Cycles Rendering Engine",
    "author": "Satish Goda (iluvblender on BA, satishgoda@gmail.com)",
    "version": (0, 1),
    "blender": (2, 6, 5),
    "location": "Properties Editor, Render Context",
    "description": "Prepend presets for some of the Cycles Panels",
    "warning": "",
    "category": "Learnbgame"
}

"""Cycles Render Properties Editor Sampling Presets"""

import bpy

from bl_operators.presets import AddPresetBase
from bpy.types import Operator, Menu


class CyclesPresetsPlusMenuBase(Menu):
    preset_operator = "script.execute_preset"
    COMPAT_ENGINES = {'CYCLES'}
    draw = Menu.draw_preset


class CYCLES_MT_sampling_presets(CyclesPresetsPlusMenuBase):
    bl_label = "Sampling Presets"
    preset_subdir = "cycles/sampling"


class CYCLES_MT_performance_presets(CyclesPresetsPlusMenuBase):
    bl_label = "Performance Presets"
    preset_subdir = "cycles/performance"


menus = []
menus.append(CYCLES_MT_sampling_presets)
menus.append(CYCLES_MT_performance_presets)


class AddPresetSampling(AddPresetBase, Operator):
    '''Add a Sampling Preset'''
    bl_idname = "render.cycles_sampling_preset_add"
    bl_label = "Add Sampling Preset"
    preset_menu = "CYCLES_MT_sampling_presets"

    preset_defines = [
        "cycles = bpy.context.scene.cycles"
    ]

    preset_values = [
        "cycles.progressive",
        "cycles.seed",
        "cycles.sample_clamp",
        "cycles.samples",
        "cycles.preview_samples",
    ]

    preset_subdir = "cycles/sampling"


class AddPresetPerformance(AddPresetBase, Operator):
    '''Add a Performance Preset'''
    bl_idname = "render.cycles_performance_preset_add"
    bl_label = "Add Performance Preset"
    preset_menu = "CYCLES_MT_performance_presets"

    preset_defines = [
        "cycles = bpy.context.scene.cycles"
    ]

    preset_values = [
        "cycles.debug_bvh_type",
        "cycles.debug_use_spatial_splits",
        "cycles.use_cache",
        "cycles.preview_start_resolution",
        "cycles.use_progressive_refine",
    ]

    preset_subdir = "cycles/performance"


presets = []
presets.append(AddPresetSampling)
presets.append(AddPresetPerformance)

def _draw(self, context, menu, op_preset):
    layout = self.layout

    row = layout.row(align=True)
    row.menu(menu.__qualname__, text=menu.bl_label)
    row.operator(op_preset, text="", icon="ZOOMIN")
    row.operator(op_preset, text="", icon="ZOOMOUT").remove_active = True


def cycles_panel_sampling_prepend_draw(self, context):
    _draw(self, context,
            bpy.types.CYCLES_MT_sampling_presets,
            "render.cycles_sampling_preset_add"
        )

def cycles_panel_performance_prepend_draw(self, context):
    _draw(self, context,
            bpy.types.CYCLES_MT_performance_presets,
            "render.cycles_performance_preset_add"
        )

panels = {}
panels[bpy.types.CyclesRender_PT_sampling] = cycles_panel_sampling_prepend_draw
panels[bpy.types.CyclesRender_PT_performance] = cycles_panel_performance_prepend_draw

def register():
    print ("Registering stuff in " + __name__)
    for menu in menus:
        bpy.utils.register_class(menu)

    for preset in presets:
        bpy.utils.register_class(preset)

    for panel, drawFunc in panels.items():
        panel.prepend(drawFunc)


def unregister():
    print ("UnRegistering stuff in " + __name__)

    for menu in menus:
        bpy.utils.unregister_class(menu)

    for preset in presets:
        bpy.utils.unregister_class(preset)

    for panel, drawFunc in panels.items():
        panel.remove(drawFunc)


if __name__ == "__main__":
    register()

