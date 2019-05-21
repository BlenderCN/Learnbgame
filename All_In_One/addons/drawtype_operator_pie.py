# -*- coding: utf8 -*-
# python
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
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {"name": "Drawtype Operator Pie",
           "author": "CDMJ",
           "version": (3, 0, 0),
           "blender": (2, 80, 0),
           "location": "",
           "description": "Drawtype per object changing in 3d View",
           "warning": "Not usable in TexPaint mode",
           "category": "Learnbgame",
           }







import bpy
from bpy.types import Menu

#operators

class VIEW3D_OT_toggle_view(bpy.types.Operator):
    """Toggle Render Only"""
    bl_idname = "object.toggle_view"
#bpy.context.space_data.overlay.show_overlays = False

    bl_label = "Toggle Render Only"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):

        scene = context.scene


        #new code

        if bpy.context.space_data.overlay.show_overlays == False:
            bpy.context.space_data.overlay.show_overlays = True
        else:
            bpy.context.space_data.overlay.show_overlays = False  #toggle render only

        return {'FINISHED'}

#wire draw
class OBJECT_OT_wire_frame(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.wire_frame"
    bl_label = "Object to Wire"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        bpy.context.object.display_type = 'WIRE'
        return {'FINISHED'}

#solid draw
class OBJECT_OT_solid_draw(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.solid_draw"
    bl_label = "Object to Solid"
# bpy.context.object.display_type = 'SOLID'
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        bpy.context.object.display_type = 'SOLID'
        return {'FINISHED'}

#textured
class OBJECT_OT_tex_draw(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.tex_draw"
    bl_label = "Object to Texture"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        bpy.context.object.display_type = 'TEXTURED'
        return {'FINISHED'}

#wire draw toggle test
class OBJECT_OT_wire_toggle(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.wire_toggle"
    bl_label = "Toggle Wire"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        if bpy.context.object.display_type == 'SOLID':
            bpy.context.object.display_type = 'WIRE'
        elif bpy.context.object.display_type == 'WIRE':
            bpy.context.object.display_type = 'SOLID'
        else:
            bpy.context.object.display_type = 'WIRE'
        return {'FINISHED'}




#------------------------------------#pie
class VIEW3D_PIE_drawtypes(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "DRAW TYPE"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        #pie.operator("render.render", text='one')

        pie.operator("object.toggle_view", text='Render Only', icon='RENDERLAYERS')
        pie.operator("object.solid_draw", text='Solid', icon='SNAP_VOLUME')
        pie.operator("object.tex_draw", text='Textured', icon='TEXTURE')
        pie.operator("object.wire_toggle", text='Wire Toggle', icon='SNAP_FACE')

_CLASSES = (
    VIEW3D_OT_toggle_view,
    OBJECT_OT_wire_frame,
    OBJECT_OT_solid_draw,
    OBJECT_OT_tex_draw,
    OBJECT_OT_wire_toggle,
    VIEW3D_PIE_drawtypes
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)

    km_list = ['3D View']
    for i in km_list:
        sm = bpy.context.window_manager
        km = sm.keyconfigs.default.keymaps[i]
        kmi = km.keymap_items.new('wm.call_menu_pie', 'Z', 'PRESS', ctrl=True, shift=True)
        kmi.properties.name = "VIEW3D_PIE_drawtypes"

def unregister():
    for cls in _CLASSES:
        bpy.utils.unregister_class(cls)

    km_list = ['3D View']
    for i in km_list:
        sm = bpy.context.window_manager
        km = sm.keyconfigs.default.keymaps[i]
        for kmi in (kmi for kmi in km.keymap_items \
                            if (kmi.idname == "VIEW3D_PIE_drawtypes")):
            km.keymap_items.remove(kmi)








if __name__ == "__main__":
    register()
    
