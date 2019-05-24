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
    "name": "Presets for Render Stamp Panel",
    "author": "Satish Goda (iluvblender on BA, satishgoda@gmail.com)",
    "version": (0, 1),
    "blender": (2, 6, 5),
    "location": "Properties Editor -> Render Context -> Stamp panel",
    "description": "Prepend presets for the Stamp Panel in Render Properties Editor",
    "warning": "",
    "category": "Learnbgame",
}

"""Prepend presets for the Stamp Panel in Render Properties Editor"""

import bpy

from bl_operators.presets import AddPresetBase
from bpy.types import Operator, Menu


class RENDER_MT_stamp_presets(Menu):
    bl_label = "Render Stamp Presets"
    preset_subdir = "render/stamp"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


menus = []
menus.append(RENDER_MT_stamp_presets)


class AddPresetRenderStamp(AddPresetBase, Operator):
    '''Add Render Stamp Preset'''
    bl_idname = "render.stamp_preset_add"
    bl_label = "Add Render Stamp Preset"
    preset_menu = "RENDER_MT_stamp_presets"


    preset_values = [
        'bpy.context.window.screen.scene.render.use_stamp_time',
        'bpy.context.window.screen.scene.render.use_stamp_date',
        'bpy.context.window.screen.scene.render.use_stamp_frame',
        'bpy.context.window.screen.scene.render.use_stamp_camera',
        'bpy.context.window.screen.scene.render.use_stamp_lens',
        'bpy.context.window.screen.scene.render.use_stamp_scene',
        'bpy.context.window.screen.scene.render.use_stamp_note',
        'bpy.context.window.screen.scene.render.use_stamp_marker',
        'bpy.context.window.screen.scene.render.use_stamp_filename',
        'bpy.context.window.screen.scene.render.use_stamp_sequencer_strip',
        'bpy.context.window.screen.scene.render.use_stamp_render_time',
        'bpy.context.window.screen.scene.render.stamp_note_text',
        'bpy.context.window.screen.scene.render.use_stamp',
        'bpy.context.window.screen.scene.render.stamp_font_size',
        'bpy.context.window.screen.scene.render.stamp_foreground',
        'bpy.context.window.screen.scene.render.stamp_background',
    ]

    preset_subdir = "render/stamp"

    def pre_cb(self, context):
        self.preset_defines = []


presets = []
presets.append(AddPresetRenderStamp)


def _draw(self, context, menu, op_preset):
    layout = self.layout

    row = layout.row(align=True)
    row.menu(menu.__qualname__, text=menu.bl_label)
    row.operator(op_preset, text="", icon="ZOOMIN")
    row.operator(op_preset, text="", icon="ZOOMOUT").remove_active = True


def render_stamp_prepend_draw(self, context):
    _draw(self, context,
            bpy.types.RENDER_MT_stamp_presets,
            "render.stamp_preset_add"
        )


panels = {}
panels[bpy.types.RENDER_PT_stamp] = render_stamp_prepend_draw


def register():
    for menu in menus:
        bpy.utils.register_class(menu)

    for preset in presets:
        bpy.utils.register_class(preset)

    for panel, drawFunc in panels.items():
        panel.prepend(drawFunc)


def unregister():
    for menu in menus:
        bpy.utils.unregister_class(menu)

    for preset in presets:
        bpy.utils.unregister_class(preset)

    for panel, drawFunc in panels.items():
        panel.remove(drawFunc)


if __name__ == "__main__":
    register()
