# Copyright (C) 2019 Enikeishik <enikeishik@gmail.com>.
# All rights reserved.
#
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
#
# Custom Set Origin idea belongs to Shane Ambler
# https://gist.github.com/sambler
# sambler/set_origin.py
# https://gist.github.com/sambler/d3c7f40854f1c2ecb510a49bebcb1ece
#


bl_info = {
    "name": "Origin to select",
    "description": "Moves origin of selected object into selected part (v/e/f) of object",
    "author": "enikeishik",
    "blender": (2, 80, 0),
    "category": "Learnbgame",
    "location": "VIEW3D > Edit Mode > Mesh > Move origin to select",
}


import bpy


class OriginToSelect(bpy.types.Operator):
    """Origin of selected moving script"""
    bl_idname = "mesh.origin_to_select"
    bl_label = "Move origin to select"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                cursor3d_location = bpy.context.scene.cursor_location.copy()
                
                ctx = bpy.context.copy()
                ctx['area'] = area
                ctx['region'] = area.regions[-1]
                bpy.ops.view3d.snap_cursor_to_selected(ctx)
                
                bpy.ops.object.mode_set(mode='OBJECT')
                
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                
                bpy.context.scene.cursor_location = cursor3d_location
                
                bpy.ops.object.mode_set(mode='EDIT')
                
                break
        
        return {'FINISHED'}


class CustomSetOriginOperator(bpy.types.Operator):
    bl_idname = 'object.custom_set_origin'
    bl_label = 'Custom set origin operator'

    centre = bpy.props.StringProperty(default='')

    def execute(self, context):
        if self.centre == 'ORIGIN_TO_SELECT':
            OriginToSelect.execute(self, context)
        else:
            return bpy.ops.object.origin_set(type=self.centre)
        return {'FINISHED'}


class CustomSetOriginMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_custom_set_origin"
    bl_label = "Custom set origin"
    
    def draw(self, context):
        layout = self.layout
        layout.operator(CustomSetOriginOperator.bl_idname, text='Origin to select (Face/Edge/Vertex)').centre = 'ORIGIN_TO_SELECT'
        layout.operator(CustomSetOriginOperator.bl_idname, text='Geometry to Origin').centre = 'GEOMETRY_ORIGIN'
        layout.operator(CustomSetOriginOperator.bl_idname, text='Origin to Geometry').centre = 'ORIGIN_GEOMETRY'
        layout.operator(CustomSetOriginOperator.bl_idname, text='Origin to 3D Cursor').centre = 'ORIGIN_CURSOR'
        layout.operator(CustomSetOriginOperator.bl_idname, text='Origin to Center of Mass (Surface)').centre = 'ORIGIN_CENTER_OF_MASS'
        layout.operator(CustomSetOriginOperator.bl_idname, text='Origin to Center of Mass (Volume)').centre = 'ORIGIN_CENTER_OF_VOLUME'


def menu_func(self, context):
    self.layout.operator(OriginToSelect.bl_idname)


def register():
    bpy.utils.register_class(OriginToSelect)
    bpy.utils.register_class(CustomSetOriginOperator)
    bpy.utils.register_class(CustomSetOriginMenu)
    
    bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)
    
    wm = bpy.context.window_manager
    win_keymaps = wm.keyconfigs.user.keymaps.get('Object Non-modal')
    if win_keymaps:
        # disable standard set origin keymap
        for kmi in win_keymaps.keymap_items:
            if kmi.idname == 'object.origin_set':
                kmi.active = False
                break
        
        # add a keymap for our set origin operator
        kmi = win_keymaps.keymap_items.new('wm.call_menu', 'C', 'PRESS', ctrl=True, alt=True, shift=True)
        setattr(kmi.properties, 'name', CustomSetOriginMenu.bl_idname)


def unregister():
    wm = bpy.context.window_manager
    win_keymaps = wm.keyconfigs.user.keymaps.get('Object Non-modal')
    if win_keymaps:
        for kmi in win_keymaps.keymap_items:
            # re-enable standard set origin
            if kmi.idname == 'object.origin_set':
                kmi.active = True
            # remove our custom set origin
            if kmi.idname == 'wm.call_menu' and getattr(kmi.properties, 'name') == CustomSetOriginMenu.bl_idname:
                win_keymaps.keymap_items.remove(kmi)
    
    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
    
    bpy.utils.unregister_class(CustomSetOriginMenu)
    bpy.utils.unregister_class(CustomSetOriginOperator)
    bpy.utils.unregister_class(OriginToSelect)


if __name__ == "__main__":
    register()
