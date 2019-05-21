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
    'name': 'face_inset_fillet',
    'author': '',
    'version': (0, 1, 2),
    'blender': (2, 6, 2),
    'api': 44645,
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
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty
from math import tan, cos, degrees, radians, sin
from mathutils import Matrix

# ------ ------
def edit_mode_out():
    bpy.ops.object.mode_set(mode = 'OBJECT')

def edit_mode_in():
    bpy.ops.object.mode_set(mode = 'EDIT')

def a_rot(ang, rp, axis, q):
    mtrx = Matrix.Rotation(ang, 3, axis)
    tmp = q - rp
    tmp1 = mtrx * tmp
    tmp2 = tmp1 + rp
    return tmp2

# ------ ------
def f_(bme, list_0, opp, adj1, n_, out, radius, en0):

    for fi in list_0:
        f = bme.faces[fi]
        list_2 = [v.index for v in f.verts]
        dict_0 = {}
        list_1 = []
        n = len(list_2)
        for i in range(n):
            dict_0[i] = []
            p = (bme.verts[ list_2[i] ].co).copy()
            p1 = (bme.verts[ list_2[(i - 1) % n] ].co).copy()
            p2 = (bme.verts[ list_2[(i + 1) % n] ].co).copy()
            dict_0[i].append(bme.verts[list_2[i]])
            vec1 = p - p1
            vec2 = p - p2
            ang = vec1.angle(vec2)
            adj = opp / tan(ang * 0.5)
            h = (adj ** 2 + opp ** 2) ** 0.5
            if round(degrees(ang)) == 180 or round(degrees(ang)) == 0.0:
                if out == True:
                    p3 = p + ((f.normal).normalized() * opp)
                else:
                    p3 = p - ((f.normal).normalized() * opp)
                bme.verts.new()
                p6 = a_rot(radians(90), p, vec1, p3)
                list_1.append(p6)
            else:
                p3 = p - (vec1.normalized() * adj)
                p4 = p - (vec2.normalized() * adj)
                if out == True:
                    p5 = p + ((f.normal).normalized() * h)
                else:
                    p5 = p - ((f.normal).normalized() * h)
                p6 = a_rot(-radians(90), p, (p3 - p4), p5)
                list_1.append(p6)

        list_2 = []
        n1_ = len(list_1)
        for j in range(n1_):
            q = list_1[j]
            q1 = list_1[(j - 1) % n1_]
            q2 = list_1[(j + 1) % n1_]
            vec1_ = q - q1
            vec2_ = q - q2
            ang_ = vec1_.angle(vec2_)
            if round(degrees(ang_)) == 180 or round(degrees(ang_)) == 0.0:
                bme.verts.new()
                bme.verts[-1].co = q
                bme.verts.index_update()
                list_2.append(bme.verts[-1])
                dict_0[j].append(bme.verts[-1])
            else:
                opp_ = adj1
                if radius == False:
                    h_ = adj1 * (1 / cos(ang_ * 0.5))
                    d = adj1
                elif radius == True:
                    h_ = opp_ / sin(ang_ * 0.5)
                    d = opp_ / tan(ang_ * 0.5)

                q3 = q - (vec1_.normalized() * d)
                q4 = q - (vec2_.normalized() * d)

                rp_ = q - ((q - ((q3 + q4) * 0.5)).normalized() * h_)
                axis_ = vec1_.cross(vec2_)
                vec3_ = rp_ - q3
                vec4_ = rp_ - q4
                rot_ang = vec3_.angle(vec4_)
                list_3 = []
                for o in range(n_ + 1):
                    q5 = a_rot((rot_ang * o / n_), rp_, axis_, q4)
                    bme.verts.new()
                    bme.verts[-1].co = q5
                    bme.verts.index_update()
                    dict_0[j].append(bme.verts[-1])
                    list_3.append(bme.verts[-1])
                list_3.reverse()
                list_2.extend(list_3)

        if out == False:
            bme.faces.new(list_2)

        n2_ = len(dict_0)
        for o in range(n2_):
            list_a = dict_0[o]
            list_b = dict_0[(o + 1) % n2_]
            bme.faces.new( [ list_a[0], list_b[0], list_b[-1], list_a[1] ] )
            bme.faces.index_update()

        


        if en0 == 'opt0':
            for k in dict_0:
                if len(dict_0[k]) > 2:
                    bme.faces.new(dict_0[k])
                    bme.faces.index_update()
        if en0 == 'opt1':
            for k_ in dict_0:
                q_ = dict_0[k_][0]
                dict_0[k_].pop(0)
                n3_ = len(dict_0[k_])
                for kk in range(n3_ - 1):
                    bme.faces.new( [ dict_0[k_][kk], dict_0[k_][(kk + 1) % n3_], q_ ] )
                    bme.faces.index_update()

            


# ------ panel 0 ------
class fif_p00(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_idname = 'fif_p0_id'
    bl_label = 'Face Inset Fillet'
    bl_context = 'mesh_edit'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.operator('fif.op00_id', text = 'Inset Fillet')

# ------ operator 0 ------
class fif_op00(bpy.types.Operator):
    bl_idname = 'fif.op00_id'
    bl_label = 'Face Inset Fillet'
    bl_options = {'REGISTER', 'UNDO'}

    opp = FloatProperty( name = '', default = 0.04, min = 0, max = 100.0, step = 1, precision = 3 )      # inset amount
    n_ = IntProperty( name = '', default = 4, min = 1, max = 100, step = 1 )      # number of sides
    adj1 = FloatProperty( name = '', default = 0.04, min = 0.00001, max = 100.0, step = 1, precision = 3 )
    out = BoolProperty( name = 'Out', default = False )
    radius = BoolProperty( name = 'Radius', default = False )
    
    en0 = EnumProperty( items =( ('opt0', 'Type 1', ''), ('opt1', 'Type 2', '') ), name = '', default = 'opt0' )


    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(self, 'en0', text = 'Corner type')

        row0 = box.row(align = True)
        row0.prop(self, 'out')
        row0.prop(self, 'radius')
        row = box.split(0.40, align = True)
        row.label('Inset amount:')
        row.prop(self, 'opp')
        row1 = box.split(0.60, align = True)
        row1.label('Number of sides:')
        row1.prop(self, 'n_', slider = True)
        row2 = box.split(0.40, align = True)
        if self.radius == True:
            row2.label('Radius:')
        else:
            row2.label('Distance:')
        row2.prop(self, 'adj1')

    def execute(self, context):
        opp = self.opp
        n_ = self.n_
        adj1 = self.adj1
        out = self.out
        radius = self.radius
        en0 = self.en0

        edit_mode_out()
        ob_act = context.active_object
        edit_mode_in()
        
        bme = bmesh.from_edit_mesh(ob_act.data)
        
        list_0 = [ f.index for f in bme.faces if f.select and f.is_valid ]

        if len(list_0) == 0:
            self.report({'INFO'}, 'No faces selected.')
            edit_mode_out()
            return {'CANCELLED'}
        elif len(list_0) != 0:
            f_(bme, list_0, opp, adj1, n_, out, radius, en0)

            bpy.ops.mesh.delete(type = 'ONLY_FACE')

        return {'FINISHED'}

# ------ ------
class_list = [ fif_op00, fif_p00 ]

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