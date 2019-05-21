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

bl_info = {
    "name": "Sharp from uv isles",
    "author": "Andy Davies (metalliandy) & Fredrik Hansson",
    "version": (1,0,1),
    "blender": (2, 5, 8),
    "api": 38019,
    "location": "UV/Image editor> UVs > Sharp from UV isles",
    "description": "Marks sharp edges based on UV isle borders",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}
    
"""
About this script:-
This script enables the marking of all UV island borders as sharp. (Use the EdgeSplit modifier to view)

Usage:-
Activate the script via the "Add-Ons" tab under the user preferences.
The Sharp from UV isles can then be accessed via UV/Image Editor> UVs> Sharp from UV isles.

This script is a modified version of the Seams from UV isles script by Fredrik Hansson, and as such I do not claim to have written the code. I only changed the seams to sharp edges.

Related Links:-
http://www.metalliandy.com
http://blenderartists.org/forum/newthread.php?do=postthread&f=48

Thanks to:-
Fredrik Hansson
Dealga McArdle (zeffii) - http://www.digitalaphasia.com

Version history:-
v1.01 - Revised indentation
v1.0 - Initial conversion.

"""

import bpy

def main(context):
    obj = context.active_object
    mesh = obj.data

    if not obj or obj.type != 'MESH':
        print("no active Mesh")
        return 
    if not mesh.uv_textures.active:
        print("no active UV Texture")
        return 

    bpy.ops.object.mode_set(mode='OBJECT')

    uvtex = mesh.uv_textures.active.data
    
    wrap_q = [1,2,3,0]
    wrap_t = [1,2,0]
    edge_uvs = {}

    for i,uvface in enumerate(uvtex):
        f = mesh.faces[i]
        f_uv = [(round(uv[0], 6), round(uv[1], 6)) for uv in uvface.uv]
        f_vi = [vertices for vertices in f.vertices]
        for i, key in enumerate(f.edge_keys):
            if len(f.vertices) == 3:
                uv1, uv2 = f_uv[i], f_uv[wrap_t[i]]
                vi1, vi2 = f_vi[i], f_vi[wrap_t[i]]
            else: # quad
                uv1, uv2 = f_uv[i], f_uv[wrap_q[i]]
                vi1, vi2 = f_vi[i], f_vi[wrap_q[i]]
                    
            if vi1 > vi2:
                vi1,uv1,uv2 = vi2,uv2,uv1
            
            edge_uvs.setdefault(key, []).append((uv1, uv2))

    for ed in mesh.edges:
        if(len(set(edge_uvs[ed.key])) > 1):
            ed.use_edge_sharp = 1	

    bpy.ops.object.mode_set(mode='EDIT')

class UvIsleSharpOperator(bpy.types.Operator):
    bl_idname = "mesh.sharp_from_uv_isles"
    bl_label = "Sharp from UV isles"
    bl_options = {'REGISTER', 'UNDO'}

#   def poll(self, context):
#	obj = context.active_object
#	return (obj and obj.type == 'MESH')

    def execute(self, context):
        main(context)
        return {'FINISHED'}
	

def menu_func(self, context):
    self.layout.operator(UvIsleSharpOperator.bl_idname)

def register():
    bpy.utils.register_module(__name__)
    bpy.types.IMAGE_MT_uvs.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.IMAGE_MT_uvs.remove(menu_func)

if __name__ == "__main__":
    register()