'''# -*- coding: utf-8 -*-

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
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# ------ ------
bl_info = {
    'name': 'face_inset_zmj100',
    'author': '',
    'version': (0, 1, 2),
    'blender': (2, 6, 2),
    'api': 44541,
    'location': 'View3D > Tool Shelf',
    'description': '',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Mesh' }
'''
# ------ ------
import bpy
import bmesh
from bpy.props import FloatProperty, BoolProperty
from mathutils import Matrix
from math import tan, degrees, radians

# ------ ------
def edit_mode_out():
    bpy.ops.object.mode_set(mode = 'OBJECT')

def edit_mode_in():
    bpy.ops.object.mode_set(mode = 'EDIT')

def redraw_():
    edit_mode_out()
    edit_mode_in()

# ------ ------
class fi_buf():
    list_tmp = []

# ------ ------
def f_(bme, list_0, opp, b_):

    if b_ == True:
        opp = -opp

    for fi in list_0:
        f = bme.faces[fi]
        fno = f.normal
        list_fvi = [v.index for v in f.verts]
        n_ = len(list_fvi)
        list_3 = []
        list_4 = []
        for i in range(n_):
            p = (bme.verts[ list_fvi[i] ].co).copy()
            p1 = (bme.verts[ list_fvi[(i - 1) % n_] ].co).copy()
            p2 = (bme.verts[ list_fvi[(i + 1) % n_] ].co).copy()
            vec1 = p - p1
            vec2 = p - p2
            ang = vec1.angle(vec2)
            adj = opp / tan(ang * 0.5)
            h = (adj ** 2 + opp ** 2) ** 0.5
            if round(degrees(ang)) == 180:
                axis = vec1
                rp = p
                mtrx = Matrix.Rotation(radians(90), 3, axis)
                p3 = p - (fno.normalized() * opp)
                a = p3 - rp
                b = mtrx * a
                c = b + rp
                bme.verts.new()
                bme.verts[-1].co = c
                bme.verts.index_update()
                list_3.append(bme.verts[-1].index)
                list_4.append(bme.verts[-1])
            else:
                p3 = p - (vec1.normalized() * adj)
                p4 = p - (vec2.normalized() * adj)
                axis = p3 - p4
                rp = p
                mtrx = Matrix.Rotation(-radians(90), 3, axis)
                p5 = p - (fno.normalized() * h)
                a = p5 - rp
                b = mtrx * a
                c = b + rp
                bme.verts.new()
                bme.verts[-1].co = c
                bme.verts.index_update()
                list_3.append(bme.verts[-1].index)
                list_4.append(bme.verts[-1])

        n1 = len(list_fvi)
        for k in range(n1):
            bme.faces.new( [ bme.verts[list_fvi[k]], bme.verts[list_fvi[(k + 1) % n1]], bme.verts[list_3[(k + 1) % n1]], bme.verts[list_3[k]] ] )
            bme.faces.index_update()

        if b_ == False:
            bme.faces.new(list_4)
            bme.faces.index_update()
            fi_buf.list_tmp.append(bme.faces[-1])

# ------ panel 0 ------
class fi_p0_id(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
#    bl_idname = 'fi_p0_id'
    bl_label = 'Face Inset'
    bl_context = 'mesh_edit'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.operator('fi.op0_id', text = 'Inset')

# ------ operator 0 ------
class fi_op0_id(bpy.types.Operator):
    bl_idname = 'fi.op0_id'
    bl_label = 'Face Inset'
    bl_options = {'REGISTER', 'UNDO'}

    opp = FloatProperty( name = '', default = 0.04, min = 0.0, max = 100.0, step = 1, precision = 3 )
    b_ = BoolProperty( name = 'Out', default = False )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH' and context.mode == 'EDIT_MESH')
		
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label('Inset amount:')
        row = box.split(0.80, align = True)
        row.prop(self, 'opp')
        row.prop(self, 'b_', toggle = True)

    def execute(self, context):
        opp = self.opp
        b_ = self.b_

        edit_mode_out()
        ob_act = context.active_object
        edit_mode_in()
        
        bme = bmesh.from_edit_mesh(ob_act.data)
        list_0 = [f.index for f in bme.faces if f.select and f.is_valid]
        
        if len(list_0) == 0:
            self.report({'INFO'}, 'No faces selected please select face.')
            bme.faces.index_update()	
            return {'FINISHED'}

        elif len(list_0) != 0:
            f_(bme, list_0, opp, b_)
            bpy.ops.mesh.delete(type = 'ONLY_FACE')

            if b_ == False:
                for f in fi_buf.list_tmp:
                    f.select_set(1)
    
                fi_buf.list_tmp[:] = []
                redraw_()

        return {'FINISHED'}

# ------ ------
class_list = [ fi_p0_id, fi_op0_id ]
               
# ------ register ------
def register():
    for c in class_list:
        bpy.utils.register_class(c)

# ------ unregister ------
def unregister():
    for c in class_list:
        bpy.utils.unregister_class(c)

# ------ ------
if __name__ == "__main__":
    register()