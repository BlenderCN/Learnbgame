'''
BEGIN GPL LICENSE BLOCK
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
END GPL LICENCE BLOCK
'''

bl_info = {
    'name': 'Move origin to selected',
    'author': '',
    'version': (0, 0, 1),
    'blender': (2, 6, 7),
    'location': '3d view > space bar > Origin Move to Selected',
    'description': 'in edit mode, sets object origin to the median of selected verts/edges/faces',
    'wiki_url': '',
    'tracker_url': '',
    'category': '3D View'}

import bpy

class MoveOrigin(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.origin_to_selected"
    bl_label = "Origin Move To Selected"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.mode == 'EDIT'

    def execute(self, context):
        saved_location = bpy.context.scene.cursor_location.copy()
        bpy.ops.view3d.snap_cursor_to_selected()
                
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')  
        bpy.context.scene.cursor_location = saved_location
        
        bpy.ops.object.mode_set(mode = 'EDIT')
        return {'FINISHED'}


def register():
    bpy.utils.register_class(MoveOrigin)


def unregister():
    bpy.utils.unregister_class(MoveOrigin)


if __name__ == "__main__":
    register()
