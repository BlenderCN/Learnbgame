# wahooney_copy_mirror_uvs.py Copyright (C) 2009-2010, Keith "Wahooney" Boshoff
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****

'''
HISTORY

0.3
  * changed operation method to be more intuitive, uv face selection is now used instead of mesh face selection.


'''

bl_info = {
    'name': 'Copy UVs from Mirror',
    'author': 'Keith (Wahooney) Boshoff',
    'version': (0, 3, 0),
    'blender': (2, 5, 7),
    'location': 'UVs > Copy UVs from Mirror',
    'url': 'http://www.wahooney.net/',
    'description': 'Copies the mirror side UVs to the current uv face selection',
    'category': 'UV'}

import bpy
from bpy.props import *

# function checks if two vectors are similar, within an error threshold
def vecSimilar(v1, v2, error):
    return abs(v2.x - v1.x) < error and abs(v2.y - v1.y) < error and abs(v2.z - v1.z) < error	

# copy uv coordinates from one uv face to another
def copyUVs(mesh, src, dst, axis, error):
    
    # cycle through the source vertices
    for i, v in enumerate(src.vertices):
        
        # get the uv coordinate of the current uv face vertex
        if i == 0:
            uv = mesh.uv_textures.active.data[src.index].uv1
        elif i == 1:
            uv = mesh.uv_textures.active.data[src.index].uv2
        elif i == 2:
            uv = mesh.uv_textures.active.data[src.index].uv3
        elif i == 3:
            uv = mesh.uv_textures.active.data[src.index].uv4
            
        co = mesh.vertices[v].co.copy()
        
        # cycle through the destination vertices
        for ii, vv in enumerate(dst.vertices):
            coo = mesh.vertices[vv].co.copy()
            
            if axis == 'X':
                coo.x = -coo.x
            elif axis == 'Y':
                coo.y = -coo.y
            elif axis == 'Z':
                coo.z = -coo.z
            
            # find the vertex that is on the axis-mirror side of the object and assign the uv's to it
            if vecSimilar(co, coo, error):
                if ii == 0:
                    mesh.uv_textures.active.data[dst.index].uv1 = uv
                elif ii == 1:
                    mesh.uv_textures.active.data[dst.index].uv2 = uv
                elif ii == 2:
                    mesh.uv_textures.active.data[dst.index].uv3 = uv
                elif ii == 3:
                    mesh.uv_textures.active.data[dst.index].uv4 = uv
                        
def main(context, operator):
    obj = context.active_object
    mesh = obj.data
    
    error = operator.properties.error
    axis = operator.properties.axis
    
    is_editmode = (obj.mode == 'EDIT')
    if is_editmode:
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
    if not mesh.uv_textures.active:
        return
        
    faces = []
    
    uvs = mesh.uv_textures.active.data
    
    # cycle through the mesh faces
    for idx, f_uv in enumerate(uvs):
    
        # continue if the mesh face isn't selected (should be invisible in uv editor)
        f_dst = mesh.faces[idx]
        
        if not f_dst.select:
            continue
            
        # see if the whole uv face is selected
        selected = 0
        
        for uv in f_uv.select_uv:
            if (uv): selected += 1
        
        # continue if the whole uv face isn't selected
        if selected != len(f_uv.uv):
            continue
            
        count = len(f_dst.vertices)
        
        for f_src in mesh.faces:
            if f_src.index == f_dst.index:
                continue
            
            if count != len(f_src.vertices):
                continue
                
            dst = f_dst.center
            src = f_src.center
            
            # test if the vertices x values are the same sign, continue if they are
            if (dst.x > 0 and src.x > 0) or (dst.x < 0 and src < 0):
                continue
            
            # axis invert source
            if axis == 'X':
                src.x = -src.x
            elif axis == 'Y':
                src.y = -src.z
            elif axis == 'Z':
                src.z = -src.z
            
            if vecSimilar(dst, src, error):
                copyUVs(mesh, f_src, f_dst, axis, error)
                
    for f_dst in faces:
        f_dst.select = True
                    
    mesh.update()
    
    if is_editmode:
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

class CopyMirrorUVs(bpy.types.Operator):
    ''''''
    bl_idname = "uv.copy_mirror_uvs"
    bl_label = "Copy UVs from Mirror"
    bl_options = {'REGISTER', 'UNDO'}

    axis = EnumProperty(items=(
                        ('X', "X", "Mirror Along X axis"),
                        ('Y', "Y", "Mirror Along Y axis"),
                        ('Z', "Z", "Mirror Along Z axis")),
                name="Axis",
                description="Mirror Axis",
                default='X')
                
    error = FloatProperty(name="Error1", description="Error threshold",
            default=0.001,
            min=0.0,
            max=100.0,
            soft_min=0.0,
            soft_max=1.0)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH')

    def execute(self, context):
        main(context, self)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(CopyMirrorUVs.bl_idname)

def register():
    bpy.utils.register_module(__name__)
    bpy.types.IMAGE_MT_uvs.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.IMAGE_MT_uvs.remove(menu_func)

if __name__ == "__main__":
    register()