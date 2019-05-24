#
# Copyright 2011 David Simon <david.mike.simon@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be awesome,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/
#

bl_info = {
  "name": "Auto Lighting",
  "author": "David Mike Simon",
  "version": (0, 1),
  "blender": (2, 5, 6),
  "api": 33713,
  "location": "View3D > Properties panel > Display tab",
  "description": "Allows you to view materials even if there are no lamps in your scene. Does not affect rendering.",
  "warning": "",
  "category": "Learnbgame",
}

import bpy, bgl

def draw_callback(self, context):
  print("FOO")

class AutoLighting(bpy.types.Operator):
    bl_idname = "view3d.auto_lighting"
    bl_label = "Auto Lighting"
    bl_description = "Toggle the presence of automatic lights in this scene"
    
    @classmethod
    def poll(cls, context):
        return True
    
    def modal(self, context, event):
        # removal of callbacks when operator is called again
        if context.screen.auto_lighting == -1:
            context.screen.auto_lighting = 0
            context.region.callback_remove(self.handle)
            return {'FINISHED'}
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            if context.screen.auto_lighting == 0 or context.screen.auto_lighting == -1:
                # operator is called for the first time, start everything
                print("Auto Lighting Enabled")
                context.screen.auto_lighting = 1
                context.window_manager.modal_handler_add(self)
                self.handle = context.region.callback_add(draw_callback, (self, context), 'POST_VIEW')
                return {'RUNNING_MODAL'}
            else:
                # operator is called again, stop displaying
                print("Auto Lighting Disabled")
                context.screen.auto_lighting = -1
                return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, can't run operator")
            return {'CANCELLED'}

#### REGISTER

def menu_func(self, context):
    col = self.layout.column(align=True)
    col.operator(AutoLighting.bl_idname, text=AutoLighting.bl_label)
    self.layout.separator()

def register():
    bpy.types.Screen.auto_lighting = bpy.props.IntProperty(name='Auto Lighting')
    bpy.types.VIEW3D_PT_view3d_display.prepend(menu_func)

def unregister():
    del bpy.types.Screen.auto_lighting
    bpy.types.VIEW3D_PT_view3d_display.remove(menu_func)

if __name__ == "__main__":
  register()
