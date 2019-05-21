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
    'name': 'reflect',
    'author': '',
    'version': (0, 0, 6),
    'blender': (2, 6, 1),
    'api': 43085,
    'location': 'View3D > Tool Shelf',
    'description': '',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Mesh' }

# ------ ------
import bpy, time
from bpy.props import EnumProperty, PointerProperty, BoolProperty
from mathutils import Matrix
from mathutils.geometry import intersect_line_plane

# ------ ------
def edit_mode_out():
    bpy.ops.object.mode_set(mode = 'OBJECT')

def edit_mode_in():
    bpy.ops.object.mode_set(mode = 'EDIT')

def m_mirror(arg):
    if arg == 'xy':
        return[ [ 1, 0,  0 ],
                [ 0, 1,  0 ],
                [ 0, 0, -1 ] ]
    elif arg == 'xz':
        return[ [ 1,  0, 0 ],
                [ 0, -1, 0 ],
                [ 0,  0, 1 ] ]
    elif arg == 'yz':
        return[ [ -1, 0, 0 ],
                [  0, 1, 0 ],
                [  0, 0, 1 ] ]
    elif arg == 'o':
        return[ [ -1,  0,  0 ],
                [  0, -1,  0 ],
                [  0,  0, -1 ] ]
    else:
        pass

def get_mesh_data_():
    edit_mode_out()
    ob_act = bpy.context.active_object
    me = ob_act.data
    edit_mode_in()
    return me

def list_clear_(l):
    l[:] = []
    return l

def faces_copy_(me, dict_1):
    list_f = [ f.index for f in me.faces if f.select ]
    for fi in list_f:
        list_v = list(me.faces[fi].vertices[:])
        len_ = len(list_v)
        tmp = []
        for vi in list_v:
            tmp.append(dict_1[vi])
        tmp.reverse()
        me.faces.add(1)
        if len_ == 3:
            me.faces[-1].vertices = tmp
        elif len_ == 4:
            me.faces[-1].vertices_raw = tmp
    me.update(calc_edges = True)

def faces_copy_1(me, dict_1, n):
    list_f = [ f.index for f in me.faces if f.select ]
    
    for j in range(n):
        for fi in list_f:
            list_v = list(me.faces[fi].vertices[:])
            len_ = len(list_v)
            tmp = []
            for vi in list_v:
                tmp.append(dict_1[vi][j])
            tmp.reverse()
            me.faces.add(1)
            if len_ == 3:
                me.faces[-1].vertices = tmp
            elif len_ == 4:
                me.faces[-1].vertices_raw = tmp
    me.update(calc_edges = True)

def edge_copy_(me, dict_1):
    list_e = [ e.key for e in me.edges if e.select ]
    for i in list_e:
        me.edges.add(1)
        me.edges[-1].vertices = [dict_1[i[0]], dict_1[i[1]] ]

def edge_copy_1(me, dict_1, n):
    list_e = [ e.key for e in me.edges if e.select ]
    for i in list_e:
        for j in range(n):
            me.edges.add(1)
            me.edges[-1].vertices = [ dict_1[i[0]][j], dict_1[i[1]][j] ]

# ------ ------
class ref_buf():
    list_0 = []

# ------ ------
class ref_p_group0(bpy.types.PropertyGroup):

    en0 = EnumProperty( items =( ('opt0', 'Local', ''),
                               ('opt1', 'Global', '') ),
                        name = 'Orientation',
                        default = 'opt0' )

    b = BoolProperty( name = 'Copy', default = False)
    arb = BoolProperty( name = 'Mirror arbitrary', default = False)

# ------ mirror ------
def f_(me, list_0, arg, context, ob_act):

    cen0 = context.scene.ref_custom_props.en0
    cb = context.scene.ref_custom_props.b
    
    dict_0 = {}
    dict_1 = {}

    if cb == False:
        for vi in list_0:
            p = (me.vertices[vi].co).copy()
            mtrx = Matrix(m_mirror(arg))

            if cen0 == 'opt0':
                p3 = mtrx * p
            elif cen0 == 'opt1':
                p1 = ob_act.matrix_world * p
                p2 = mtrx * p1
                p3 = (ob_act.matrix_world).inverted() * p2

            dict_0[vi] = p3

        for j in dict_0:
            me.vertices[j].co = dict_0[j]

    elif cb == True:
        for vi in list_0:
            p = (me.vertices[vi].co).copy()
            mtrx = Matrix(m_mirror(arg))

            if cen0 == 'opt0':
                p3 = mtrx * p
            elif cen0 == 'opt1':
                p1 = ob_act.matrix_world * p
                p2 = mtrx * p1
                p3 = (ob_act.matrix_world).inverted() * p2

            me.vertices.add(1)
            me.vertices[-1].co = p3
            me.vertices[-1].select = False
            dict_1[vi] = me.vertices[-1].index

        edge_copy_(me, dict_1)
        faces_copy_(me, dict_1)

# ------ mirror arbitrary ------
def f_1(me, list_0, list_1):

    dict_1 = {vi: [] for vi in list_1}

    for fi in list_0:
        f = me.faces[fi]
        for vi in list_1:
            v = (me.vertices[vi].co).copy()
            p = v + ((f.normal).copy() * 0.1)
            pp = (me.vertices[f.vertices[0]].co).copy()
            pn = (f.normal).copy()
            p1 =  intersect_line_plane(v, p, pp, pn)
            d = (p1 - v).length
            p2 = p1 + ((f.normal).copy() * d)
            me.vertices.add(1)
            me.vertices[-1].co = p2
            me.vertices[-1].select = False
            dict_1[vi].append(me.vertices[-1].index)

    n = len(list_0)
    edge_copy_1(me, dict_1, n)
    faces_copy_1(me, dict_1, n)

# ------ panel 0 ------
class ref_p0(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_idname = 'ref_p0_id'
    bl_label = 'Mirror'
    bl_context = 'mesh_edit'

    def draw(self, context):

        cen0 = context.scene.ref_custom_props.en0
        carb = context.scene.ref_custom_props.arb

        layout = self.layout
        layout.prop(context.scene.ref_custom_props, 'arb')

        if carb == False:
            layout.prop(context.scene.ref_custom_props, 'en0', expand = False)
            layout.prop(context.scene.ref_custom_props, 'b')
            row = layout.row(align = True)
            row.operator('ref.op0_id', text = 'x')
            row.operator('ref.op1_id', text = 'y')
            row.operator('ref.op2_id', text = 'z')
            row.operator('ref.op3_id', text = 'origin')
        elif carb == True:
            row = layout.split(0.60)
            row.label('Store data:')
            row.operator('ref.op4_id', text = 'face')
            row1 = layout.split(0.80)
            row1.operator('ref.op5_id', text = 'Mirror')
            row1.operator('ref.op6_id', text = '?')

# ------ operator 0 ------ mirror_x
class ref_op0(bpy.types.Operator):
    bl_idname = 'ref.op0_id'
    bl_label = 'Mirror'
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout

    def execute(self, context):

        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data

        list_0 = [v.index for v in me.vertices if v.select]

        if len(list_0) == 0:
            self.report({'INFO'}, 'Nothing selected can not continue.')
            edit_mode_in()
            return {'CANCELLED'}
        else:
            arg = 'yz'
            f_(me, list_0, arg, context, ob_act)
            edit_mode_in()
            return {'FINISHED'}

# ------ operator 1 ------ mirror_y
class ref_op1(bpy.types.Operator):
    bl_idname = 'ref.op1_id'
    bl_label = 'Mirror'
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout

    def execute(self, context):

        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data

        list_0 = [v.index for v in me.vertices if v.select]

        if len(list_0) == 0:
            self.report({'INFO'}, 'Nothing selected can not continue.')
            edit_mode_in()
            return {'CANCELLED'}
        else:
            arg = 'xz'
            f_(me, list_0, arg, context, ob_act)
            edit_mode_in()
            return {'FINISHED'}

# ------ operator 2 ------ mirror_z
class ref_op2(bpy.types.Operator):
    bl_idname = 'ref.op2_id'
    bl_label = 'Mirror'
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout

    def execute(self, context):

        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data

        list_0 = [v.index for v in me.vertices if v.select]

        if len(list_0) == 0:
            self.report({'INFO'}, 'Nothing selected can not continue.')
            edit_mode_in()
            return {'CANCELLED'}
        else:
            arg = 'xy'
            f_(me, list_0, arg, context, ob_act)
            edit_mode_in()
            return {'FINISHED'}

# ------ operator 3 ------ mirror_o
class ref_op3(bpy.types.Operator):
    bl_idname = 'ref.op3_id'
    bl_label = 'Mirror'
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout

    def execute(self, context):

        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data

        list_0 = [v.index for v in me.vertices if v.select]

        if len(list_0) == 0:
            self.report({'INFO'}, 'Nothing selected can not continue.')
            edit_mode_in()
            return {'CANCELLED'}
        else:
            arg = 'o'
            f_(me, list_0, arg, context, ob_act)
            edit_mode_in()
            return {'FINISHED'}

# ------ operator 4 ------
class ref_op4(bpy.types.Operator):

    bl_idname = 'ref.op4_id'
    bl_label = ''

    def execute(self, context):
        me = get_mesh_data_()
        list_clear_(ref_buf.list_0)
        for f in me.faces:
            if f.select:
                ref_buf.list_0.append(f.index)
                bpy.ops.mesh.select_all(action = 'DESELECT')
        return {'FINISHED'}

# ------ operator 5 ------ mirror_arb
class ref_op5(bpy.types.Operator):
    bl_idname = 'ref.op5_id'
    bl_label = 'Mirror'
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout

    def execute(self, context):
        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data

        list_0 = ref_buf.list_0
        list_1 = [v.index for v in me.vertices if v.select]
            
        if len(list_0) == 0:
                self.report({'INFO'}, 'No faces stored in memory unable to continue.')
                edit_mode_in()
                return {'CANCELLED'}
        elif len(list_1) == 0:
                self.report({'INFO'}, 'Nothing selected unable to continue.')
                edit_mode_in()
                return {'CANCELLED'}
        else:
            f_1(me, list_0, list_1)

        edit_mode_in()
        return {'FINISHED'}

# ------ operator 6 ------
class ref_op6(bpy.types.Operator):
    bl_idname = 'ref.op6_id'
    bl_label = ''

    def draw(self, context):
        layout = self.layout
        layout.label('To use:')

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width = 400)

# ------ operator 7 ------
class ref_op7(bpy.types.Operator):
    bl_idname = 'ref.op7_id'
    bl_label = ''

    def execute(self, context):
        bpy.ops.ref.op6_id('INVOKE_DEFAULT')
        return {'FINISHED'}

# ------ ------
class_list = [ ref_p0, ref_op0, ref_op1, ref_op2, ref_op3, ref_op4, ref_op5, ref_op6, ref_op7, ref_p_group0 ]
               
# ------ register ------
def register():
    for c in class_list:
        bpy.utils.register_class(c)
    bpy.types.Scene.ref_custom_props = PointerProperty(type = ref_p_group0)

# ------ unregister ------
def unregister():
    for c in class_list:
        bpy.utils.unregister_class(c)
    del bpy.context.scene['ref_custom_props']

# ------ ------
if __name__ == "__main__":
    register()