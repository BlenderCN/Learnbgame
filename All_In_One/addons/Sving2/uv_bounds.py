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

import bpy


class UVtoBounds(bpy.types.Operator):
    '''Scale UV to Bounds'''
    bl_idname = "uv.to_bounds"
    bl_label = "Scale to bounds"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        uvs = obj.data.uv_textures.active
        return (uvs is not None)

    def execute(self, context):
        obj = context.active_object
        uv_name = obj.data.uv_textures.active.name

        # Toggle Edit mode
        is_editmode = (obj.mode == 'EDIT')
        if is_editmode:
            bpy.ops.object.mode_set(mode='OBJECT')

        uvs = obj.data.uv_textures[uv_name]

        u_points = []
        v_points = []

        for f in uvs.data:
            for u, v in f.uv:
                u_points.append(u)
                v_points.append(v)
        u_min = min(u_points)
        u_range = max(u_points) - u_min
        v_min = min(v_points)
        v_range = max(v_points) - v_min

        for f in uvs.data:
            for i in range(len(f.uv_raw)):
                if i % 2:
                    v = (f.uv_raw[i] - v_min) / v_range
                    f.uv_raw[i] = v
                else:
                    u = (f.uv_raw[i] - u_min) / u_range
                    f.uv_raw[i] = u

        if is_editmode:
            bpy.ops.object.mode_set(mode='EDIT')
        else:
            me.update_tag()
        return {'FINISHED'}
