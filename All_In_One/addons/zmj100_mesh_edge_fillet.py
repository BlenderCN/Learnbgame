# -*- coding: utf-8 -*-

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
    'name': 'edge fillet zmj100',
    'author': '',
    'version': (0, 2, 2),
    'blender': (2, 6, 1),
    'api': 43085,
    'location': 'View3D > Tool Shelf',
    'description': '',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Mesh' }

# ------ ------
import bpy
from bpy.props import FloatProperty, IntProperty, BoolProperty
from mathutils import Matrix
from math import cos, pi, degrees, sin, tan

# ------ ------
def edit_mode_out():
    bpy.ops.object.mode_set(mode = 'OBJECT')

def edit_mode_in():
    bpy.ops.object.mode_set(mode = 'EDIT')

def list_clear_(l):
    l[:] = []
    return l

def get_adj_v_(list_):
        tmp = {}
        for i in list_:
                try:             tmp[i[0]].append(i[1])
                except KeyError: tmp[i[0]] = [i[1]]
                try:             tmp[i[1]].append(i[0])
                except KeyError: tmp[i[1]] = [i[0]]
        return tmp

# ------ ------
class f_buf():
    an = 0

# ------ ------
def f_(me, list_0, adj, n, out, flip, e_mode, radius):

    dict_0 = get_adj_v_(list_0)
    list_1 = [[dict_0[i][0], i, dict_0[i][1]] for i in dict_0 if (len(dict_0[i]) == 2)][0]
    list_2 = []

    p_ = list_1[1]
    p = (me.vertices[list_1[1]].co).copy()
    p1 = (me.vertices[list_1[0]].co).copy()
    p2 = (me.vertices[list_1[2]].co).copy()

    vec1 = p - p1
    vec2 = p - p2

    ang = vec1.angle(vec2, any)
    f_buf.an = round(degrees(ang))

    # -- -- -- --
    if f_buf.an == 180 or f_buf.an == 0.0:
        if e_mode[1] == True:
            for e in me.edges:
                if e.select:
                    e.select = False

        elif e_mode[0] == True:
            me.vertices[list_1[0]].select = False
            me.vertices[list_1[1]].select = False
            me.vertices[list_1[2]].select = False
        return

    # -- -- -- --
    opp = adj

    if radius == False:
        h = adj * (1 / cos(ang * 0.5))
        adj_ = adj
    elif radius == True:
        h = opp / sin(ang * 0.5)
        adj_ = opp / tan(ang * 0.5)

    p3 = p - (vec1.normalized() * adj_)
    p4 = p - (vec2.normalized() * adj_)
    rp = p - ((p - ((p3 + p4) * 0.5)).normalized() * h)

    vec3 = rp - p3
    vec4 = rp - p4

    axis = vec1.cross(vec2)

    if out == False:
        if flip == False:
            rot_ang = vec3.angle(vec4)
        elif flip == True:
            rot_ang = vec1.angle(vec2)
    elif out == True:
        rot_ang = (2 * pi) - vec1.angle(vec2)

    for j in range(n + 1):
        new_angle = rot_ang * j / n
        mtrx = Matrix.Rotation(new_angle, 3, axis)
        if out == False:
            if flip == False:
                tmp = p4 - rp
                tmp1 = mtrx * tmp
                tmp2 = tmp1 + rp
            elif flip == True:
                p3 = p - (vec1.normalized() * opp)
                tmp = p3 - p
                tmp1 = mtrx * tmp
                tmp2 = tmp1 + p
        elif out == True:
            p4 = p - (vec2.normalized() * opp)
            tmp = p4 - p
            tmp1 = mtrx * tmp
            tmp2 = tmp1 + p

        me.vertices.add(1)
        me.vertices[-1].co = tmp2
        me.vertices[-1].select = False
        list_2.append(me.vertices[-1].index)
    
    if flip == True:
        list_1[1:2] = list_2
    else:
        list_2.reverse()
        list_1[1:2] = list_2

    list_clear_(list_2)

    n1 = len(list_1)
    for t in range(n1 - 1):
        me.edges.add(1)
        me.edges[-1].vertices = [list_1[t], list_1[(t + 1) % n1]]

    me.vertices[list_1[0]].select = False
    me.vertices[list_1[-1]].select = False

    if e_mode[1] == True:
        for e in me.edges:
            if e.select:
                e.select = False

        me.vertices.add(1)
        me.vertices[-1].co = p
        me.edges.add(1)
        me.edges[-1].vertices = [me.vertices[-1].index, p_]

    me.update(calc_edges = True)

# ------ panel 0 ------
class f_p0(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_idname = 'f_p0_id'                                                
    bl_label = 'Fillet'
    bl_context = 'mesh_edit'

    def draw(self, context):
        layout = self.layout
        
        row = layout.split(0.80)
        row.operator('f.op0_id', text = 'Fillet')
        row.operator('f.op1_id', text = '?')

# ------ operator 0 ------
class f_op0(bpy.types.Operator):
    bl_idname = 'f.op0_id'
    bl_label = 'Fillet'
    bl_options = {'REGISTER', 'UNDO'}

    adj = FloatProperty( name = '', default = 0.1, min = 0.00001, max = 100.0, step = 1, precision = 3 )
    n = IntProperty( name = '', default = 3, min = 1, max = 100, step = 1 )
    out = BoolProperty( name = 'Outside', default = False )
    flip = BoolProperty( name = 'Flip', default = False )
    radius = BoolProperty( name = 'Radius', default = False )
    
    def draw(self, context):
        layout = self.layout

        if f_buf.an == 180 or f_buf.an == 0.0:
            layout.label('Info:')
            layout.label('Angle equal to 0 or 180,')
            layout.label('can not fillet.')
        else:
            layout.prop(self, 'radius')
            if self.radius == True:
                layout.label('Radius:')
            elif self.radius == False:
                layout.label('Distance:')
            layout.prop(self, 'adj')
            layout.label('Number of sides:')
            layout.prop(self, 'n', slider = True)
            if self.n > 1:
                row = layout.row(align = False)
                row.prop(self, 'out')
                if self.out == False:
                    row.prop(self, 'flip')

    def execute(self, context):
        adj = self.adj
        n = self.n
        out = self.out
        flip = self.flip
        radius = self.radius

        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data
        list_0 = [list(e.key) for e in me.edges if e.select]
        e_mode = [i for i in bpy.context.tool_settings.mesh_select_mode]

        if len(list_0) != 2:
            self.report({'INFO'}, 'Two adjacent edges must be selected.')
            edit_mode_in()
            return {'CANCELLED'}
        else:
            if out == True:
                flip = False
            f_(me, list_0, adj, n, out, flip, e_mode, radius)

        edit_mode_in()
        bpy.ops.mesh.delete(type = 'VERT')
        return {'FINISHED'}

# ------ operator 1 ------
class f_op1(bpy.types.Operator):
    bl_idname = 'f.op1_id'
    bl_label = ''

    def draw(self, context):
        layout = self.layout
        layout.label('To use:')
        layout.label('Select two adjacent edges and press Fillet button.')
    
    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width = 400)

# ------ operator 2 ------
class f_op2(bpy.types.Operator):
    bl_idname = 'f.op2_id'
    bl_label = ''

    def execute(self, context):
        bpy.ops.f.op1_id('INVOKE_DEFAULT')
        return {'FINISHED'}

# ------ ------
class_list = [ f_op0, f_op1, f_op2, f_p0]

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