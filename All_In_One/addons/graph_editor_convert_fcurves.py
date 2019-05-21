# ##### BEGIN GPL LICENSE BLOCK #####
#
#  graph_editor_convert_fcurves.py
#  Toggle Samples/Keyframes F-Curve mode
#  Copyright (C) 2015 Quentin Wenger
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



bl_info = {"name": "F-Curve Samples/Keyframes conversion",
           "description": "Toggle Samples/Keyframes F-Curve mode",
           "author": "Quentin Wenger (Matpi)",
           "version": (1, 0),
           "blender": (2, 75, 0),
           "location": "Graph Editor > Channel Menu",
           "warning": "",
           "wiki_url": "",
           "tracker_url": "",
           "category": "Animation"
           }

import bpy


class GRAPH_MT_convert_to_samples(bpy.types.Operator):
    bl_idname = "action.convert_to_samples"
    bl_label = "Samples from Keyframes"

    @classmethod
    def poll(cls, context):
        if (context.active_object and
            context.active_object.select and
            context.active_object.animation_data and
            context.active_object.animation_data.action):
            
            action = context.active_object.animation_data.action
            for fcurve in action.fcurves:
                if fcurve.select and not fcurve.hide:
                    if len(fcurve.sampled_points) == 0:
                        return True

        return False

    def execute(self, context):
        action = context.active_object.animation_data.action

        for fcurve in action.fcurves:
            if fcurve.select and not fcurve.hide:
                fcurve.convert_to_samples(*action.frame_range)
        
        return {'FINISHED'}

class GRAPH_MT_convert_to_keyframes(bpy.types.Operator):
    bl_idname = "action.convert_to_keyframes"
    bl_label = "Keyframes from Samples"

    @classmethod
    def poll(cls, context):
        if (context.active_object and
            context.active_object.select and
            context.active_object.animation_data and
            context.active_object.animation_data.action):
            
            action = context.active_object.animation_data.action
            for fcurve in action.fcurves:
                if fcurve.select and not fcurve.hide:
                    if len(fcurve.sampled_points) != 0:
                        return True

        return False

    def execute(self, context):
        action = context.active_object.animation_data.action

        for fcurve in action.fcurves:
            if fcurve.select and not fcurve.hide:
                fcurve.convert_to_keyframes(*action.frame_range)
        
        return {'FINISHED'}


class ConvertSubMenu(bpy.types.Menu):
    bl_idname = "GRAPH_MT_convert_submenu"
    bl_label = "Convert to"

    @classmethod
    def poll(cls, context):
        if (context.active_object and
            context.active_object.select and
            context.active_object.animation_data and
            context.active_object.animation_data.action):
            
            action = context.active_object.animation_data.action
            for fcurve in action.fcurves:
                if fcurve.select and not fcurve.hide:
                    return True

        return False
    
    def draw(self, context):
        layout = self.layout

        layout.operator("action.convert_to_samples")
        layout.operator("action.convert_to_keyframes")


def displaySubMenu(self, context):
    layout = self.layout
    layout.menu("GRAPH_MT_convert_submenu")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.GRAPH_MT_channel.append(displaySubMenu)

def unregister():
    bpy.types.GRAPH_MT_channel.remove(displaySubMenu)
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
