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
    'name': 'sire_o',
    'author': '',
    'version': (0, 1, 9),
    'blender': (2, 6, 3),
    'api': 47593,
    'location': 'View3D > Tool Shelf',
    'description': '',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Mesh' }

# ------ ------
import bpy
import bmesh
from bpy.props import PointerProperty, CollectionProperty, EnumProperty, StringProperty, IntProperty, FloatProperty, BoolProperty
from mathutils import Matrix, Vector
from math import degrees, tan, radians

# ------ ------
def edit_mode_out():
    bpy.ops.object.mode_set(mode = 'OBJECT')

def edit_mode_in():
    bpy.ops.object.mode_set(mode = 'EDIT')

def get_adj_v_(list_):
        tmp = {}
        for i in list_:
                try:             tmp[i[0]].append(i[1])
                except KeyError: tmp[i[0]] = [i[1]]
                try:             tmp[i[1]].append(i[0])
                except KeyError: tmp[i[1]] = [i[0]]
        return tmp

def median_point_(bme, list_):
    tmp = Vector()
    for vi in list_:
        v = (bme.verts[vi].co).copy()
        tmp += v
    return tmp / len(list_)

def is_loop_(list_fl):
    return True if len(list_fl) == 0 else False

def a_rot(ang, rp, axis, q):
    return (Matrix.Rotation(ang, 3, axis) * (q - rp)) + rp

def sort_list_(loop, list_0, list_fl):
    if loop:
        list_1 = f_2(list_0[0][0], list_0)
        del list_1[-1]
        return list_1
    else:
        list_1 = f_1(list_fl[0], list_0, list_fl[1])
        return list_1

def f_1(frst, list_, last):      # edge chain
    fi = frst
    tmp = [frst]
    while list_ != []:
        for i in list_:
            if i[0] == fi:
                tmp.append(i[1])
                fi = i[1]
                list_.remove(i)
            elif i[1] == fi:
                tmp.append(i[0])
                fi = i[0]
                list_.remove(i)
        if tmp[-1] == last:
            break
    return tmp

def f_2(frst, list_):      # edge loop
    fi = frst
    tmp = [frst]
    while list_ != []:
        for i in list_:
            if i[0] == fi:
                tmp.append(i[1])
                fi = i[1]
                list_.remove(i)
            elif i[1] == fi:
                tmp.append(i[0])
                fi = i[0]
                list_.remove(i)
        if tmp[-1] == frst:
            break
    return tmp

def f3_(bme, list_, no, opp_):
    p = (bme.verts[list_[0]].co).copy()
    p1 = (bme.verts[list_[1]].co).copy()
    return a_rot(radians(90), p, p - p1, p + (no * opp_))

def f4_(bme, list_, no, opp_):
    p = (bme.verts[list_[-1]].co).copy()
    p1 = (bme.verts[list_[-2]].co).copy()
    return a_rot(radians(90), p, p - p1, p - (no * opp_))

def get_direction_(bme, list_):
    n = len(list_)
    for i in range(n):
        p = (bme.verts[list_[i]].co).copy()
        p1 = (bme.verts[list_[(i - 1) % n]].co).copy()
        p2 = (bme.verts[list_[(i + 1) % n]].co).copy()
        ang = round(degrees((p - p1).angle((p - p2), any)))
        if ang == 0 or ang == 180:
            continue
        elif ang != 0 or ang != 180:
            return(((p - p1).cross((p - p2))).normalized())
            break

def get_no_(bme, dict_0):
    for i in dict_0.items():
        if len(i[1]) < 2:
            pass
        else:
            p = (bme.verts[i[0]].co).copy()
            p1 = (bme.verts[i[1][0]].co).copy()
            p2 = (bme.verts[i[1][1]].co).copy()
            ang = round(degrees((p - p1).angle((p - p2), any)))
            if ang == 0 or ang == 180:
                continue
            elif ang != 0 or ang != 180:
                return(((p - p1).cross((p - p2))).normalized())
                break

# ------ ------ scale
def scale_(bme, b, opp, list_1, loop):

    no = get_direction_(bme, list_1)
    opp = -opp if b == True else opp

    list_2 = list_1[:]
    dict_0 = {}

    n = len(list_1)
    for i in range(n):
        p = (bme.verts[list_1[i]].co).copy()
        p1 = (bme.verts[list_1[(i - 1) % n]].co).copy()
        p2 = (bme.verts[list_1[(i + 1) % n]].co).copy()
        bme.verts[list_1[i]].select_set(0)
        vec1 = p - p1
        vec2 = p - p2
        ang = vec1.angle(vec2)
        adj = opp / tan(ang * 0.5)
        h = (adj ** 2 + opp ** 2) ** 0.5
        if round(degrees(ang)) == 180 or round(degrees(ang)) == 0.0:
            dict_0[list_1[i]] = a_rot(radians(90), p, vec1, p - (no * opp))
        else:
            dict_0[list_1[i]] = a_rot(-radians(90), p, ((p - (vec1.normalized() * adj)) - (p - (vec2.normalized() * adj))), p - (no * h))

    if loop == True:
        n1 = len(list_2)
    elif loop == False:      # path == True
        n1 = len(list_2) - 1
        aa = f3_(bme, list_1, no, opp)
        bb = f4_(bme, list_1, no, opp)

    for k in list_1:
        bme.verts[k].co = dict_0[k]

    if loop == False:
        bme.verts[list_2[0]].co = aa
        bme.verts[list_2[-1]].co = bb

# ------ ------- inset
def inset_(bme, opp, b, list_1, loop):

    no = get_direction_(bme, list_1)
    opp = -opp if b == True else opp

    list_2 = list_1[:]
    list_3 = []

    n = len(list_1)
    for i in range(n):
        p = (bme.verts[list_1[i]].co).copy()
        p1 = (bme.verts[list_1[(i - 1) % n]].co).copy()
        p2 = (bme.verts[list_1[(i + 1) % n]].co).copy()
        vec1 = p - p1
        vec2 = p - p2
        ang = vec1.angle(vec2)
        adj = opp / tan(ang * 0.5)
        h = (adj ** 2 + opp ** 2) ** 0.5
        if round(degrees(ang)) == 180 or round(degrees(ang)) == 0.0:
            bme.verts.new(a_rot(radians(90), p, vec1, p - (no * opp)))
            bme.verts.index_update()
            list_3.append(bme.verts[-1].index)
        else:
            bme.verts.new(a_rot(-radians(90), p, ((p - (vec1.normalized() * adj)) - (p - (vec2.normalized() * adj))), p - (no * h)))
            bme.verts.index_update()
            list_3.append(bme.verts[-1].index)

    if loop == True:
        n1 = len(list_2)
    elif loop == False:      # path == True
        n1 = len(list_2) - 1
        bme.verts[list_3[0]].co = f3_(bme, list_1, no, opp)
        bme.verts[list_3[-1]].co = f4_(bme, list_1, no, opp)

    for j in range(n1):
        bme.faces.new([ bme.verts[list_2[j]], bme.verts[list_2[(j + 1) % n]], bme.verts[list_3[(j + 1) % n]], bme.verts[list_3[j]] ])
        bme.faces.index_update()

    return list_3

# ------ ------ rotate
def rotate_(bme, list_0, pivot, ax, b, ang):

    ang = -ang if b == True else ang

    list_1 = [[v.index for v in e.verts] for e in bme.edges if e.select and e.is_valid]
    dict_0 = get_adj_v_(list_1)

    no = get_no_(bme, dict_0)

    if ax == 'x':
        axis = Vector(( 1.0, 0.0, 0.0))
    elif ax == 'y':
        axis = Vector(( 0.0, 1.0, 0.0))
    elif ax == 'z':
        axis = Vector(( 0.0, 0.0, 1.0))
    elif ax == 'nn':
        axis = no
    elif ax == 'ar':
        if len(so_buf.list_axis) == 0:
            axis = Vector(( 0.0, 0.0, 1.0))
        elif len(so_buf.list_axis) != 0:
            q1 = (bme.verts[so_buf.list_axis[0]].co).copy()
            q2 = (bme.verts[so_buf.list_axis[1]].co).copy()
            axis = (q2 - q1).normalized()

    if pivot == 'ori':
        rp = Vector(( 0.0, 0.0, 0.0))
    elif pivot == 'mdp':
        rp = median_point_(bme, list_0)
    elif pivot == 'par':
        if len(so_buf.list_pivot) == 0:
            rp = Vector(( 0.0, 0.0, 0.0))
        elif len(so_buf.list_pivot) != 0:
            rp = (bme.verts[so_buf.list_pivot[0]].co).copy()

    dict_1 = {}
    for vi in list_0:
        q = (bme.verts[vi].co).copy()
        dict_1[vi] = a_rot(radians(ang), rp, axis, q)

    for j in dict_1:
        bme.verts[j].co = dict_1[j]

# ------ ------ extrude
def extrude_(bme, list_0, list_1, ea, b):

    ea = -ea if b == True else ea

    dict_1 = {}
    for vi in list_0:
        p = (bme.verts[vi].co).copy()
        dict_1[vi] = []
        dict_1[vi].append(vi)
        bme.verts.new(p - (so_buf.list_1[0] * ea))

        bme.verts.index_update()
        dict_1[vi].append(bme.verts[-1].index)

    for ek in list_1:
        bme.faces.new([bme.verts[dict_1[ek[0]][0]], bme.verts[dict_1[ek[1]][0]], bme.verts[dict_1[ek[1]][1]], bme.verts[dict_1[ek[0]][1]]])
        bme.faces.index_update()

    return dict_1

# ------ ------ rotate 1
def rotate_1(bme, list_1, pivot, ax, b, ang):

    no = get_direction_(bme, list_1)
    ang = -ang if b == True else ang

    if ax == 'x':
        axis = Vector(( 1.0, 0.0, 0.0))
    elif ax == 'y':
        axis = Vector(( 0.0, 1.0, 0.0))
    elif ax == 'z':
        axis = Vector(( 0.0, 0.0, 1.0))
    elif ax == 'nn':
        axis = no
    elif ax == 'ar':
        if len(so_buf.list_axis) == 0:
            axis = Vector(( 0.0, 0.0, 1.0))
        elif len(so_buf.list_axis) != 0:
            q1 = (bme.verts[so_buf.list_axis[0]].co).copy()
            q2 = (bme.verts[so_buf.list_axis[1]].co).copy()
            axis = (q2 - q1).normalized()

    if pivot == 'ori':
        rp = Vector(( 0.0, 0.0, 0.0))
    elif pivot == 'mdp':
        rp = median_point_(bme, list_1)
    elif pivot == 'par':
        if len(so_buf.list_pivot) == 0:
            rp = Vector(( 0.0, 0.0, 0.0))
        elif len(so_buf.list_pivot) != 0:
            rp = (bme.verts[so_buf.list_pivot[0]].co).copy()

    dict_0 = {}
    for vi in list_1:
        q = (bme.verts[vi].co).copy()
        dict_0[vi] = a_rot(radians(ang), rp, axis, q)

    for j in dict_0:
        bme.verts[j].co = dict_0[j]

# ------ ------ extrude 1
def extrude_1(bme, list_1, ea, b, loop):

    list_3 = list_1[:]
    no = get_direction_(bme, list_1)
    ea = -ea  if b == True else ea
    list_2 = []

    n = len(list_1)
    for i in range(n):
        p = (bme.verts[list_1[i]].co).copy()
        bme.verts.new(p - (no * ea))
        bme.verts.index_update()
        list_2.append(bme.verts[-1].index)

    for k in range(n if loop == True else (n - 1)):
        bme.faces.new([ bme.verts[list_3[k]], bme.verts[list_3[(k + 1) % n]], bme.verts[list_2[(k + 1) % n]], bme.verts[list_2[k]] ])

    return list_2

# ------ property group 0 ------
class so_p_group0(bpy.types.PropertyGroup):
    i = IntProperty( name = '', default = 0, min = 0, max = 100, step = 1 )
    en = EnumProperty( items =( ('opt0', 'I', ''), ('opt1', 'M', '') ), name = 'Mode', default = 'opt0' )
    en0 = EnumProperty( items =( ('s', 'Scale', ''), ('i', 'Inset', ''), ('r', 'Rotate', ''), ('e', 'Extrude', '') ), name = 'Mode', default = 's' )
    en_ax = EnumProperty( items =( ('x', 'X', ''), ('y', 'Y', ''), ('z', 'Z', ''), ('nn', 'Normal', ''), ('ar', 'Arbitrary', '') ), name = '', default = 'ar' )
    en_p = EnumProperty( items =( ('ori', 'Origin', ''), ('mdp', 'Median Point', ''), ('par', 'Arbitrary', '') ), name = '', default = 'par' )
    br = BoolProperty( name = 'Rotation Settings:', default = False)

# ------ property group 1 ------
class so_p_group1(bpy.types.PropertyGroup):
    d = FloatProperty( name = '', default = 0.04, min = -100.0, max = 100.0, step = 1, precision = 3 )
    ang = FloatProperty( name = '', default = 15.0, min = -360.0, max = 360.0, step = 1, precision = 3 )
    en1 = EnumProperty( items =( ('in', 'In', ''), ('out', 'Out', '')), name = '', default = 'in' )
    en2 = EnumProperty( items =( ('cw', 'Clockwise', ''), ('ccw', 'Counterclockwise', '')), name = '', default = 'cw' )
    na = StringProperty( name = '', default = '')
    template_list_controls = StringProperty( default = '', options = {"HIDDEN"} )

# ------ ------
class so_buf():
    i = 0
    name = ''
    list_axis = []
    list_pivot = []
    list_0 = []
    list_1 = []

# ------ panel 0 ------
class so_p0(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_idname = 'so_p0_id'
    bl_label = 'SIRE Outline'
    bl_context = 'mesh_edit'
    #bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        en = context.scene.so_custom_props.en      # mode
        en0 = context.scene.so_custom_props.en0      # functions
        en_ax = context.scene.so_custom_props.en_ax      # axis
        en_p = context.scene.so_custom_props.en_p      # pivot
        br = context.scene.so_custom_props.br

        layout = self.layout
        layout.prop(context.scene.so_custom_props, 'en', expand = False)
        if en == 'opt0':
            box = layout.box()
            box.prop(context.scene.so_custom_props, 'br', toggle = False)
            if br == True:
                row = box.split(0.80, align = True)
                row.prop(context.scene.so_custom_props, 'en_ax', text = 'Axis')
                if en_ax == 'ar':
                    row.operator('so.op2_id', text = 'Store')
                row1 = box.split(0.80, align = True)
                row1.prop(context.scene.so_custom_props, 'en_p', text = 'Pivot')
                if en_p == 'par':
                    row1.operator('so.op3_id', text = 'Store')
            row2 = layout.row(align = True)
            row2.operator('so.op4_id', text = 'Scale')
            row2.operator('so.op5_id', text = 'Inset')
            row2.operator('so.op6_id', text = 'Rotate')
            row2.operator('so.op7_id', text = 'Extrude')
        elif en == 'opt1':
            layout.prop(context.scene.so_custom_props, 'en0', expand = True)
            if en0 == 'r':
                box = layout.box()
                row_ = box.split(0.80, align = True)
                row_.prop(context.scene.so_custom_props, 'en_ax', text = 'Axis')
                if en_ax == 'ar':
                    row_.operator('so.op2_id', text = 'Store')
                row_a = box.split(0.80, align = True)
                row_a.prop(context.scene.so_custom_props, 'en_p', text = 'Pivot')
                if en_p == 'par':
                    row_a.operator('so.op3_id', text = 'Store')
            row = layout.row(align = False)
            row.template_list( context.scene, 'so_custom_collection_',  context.scene.so_custom_props, 'i', prop_list = 'template_list_controls', rows = 1, maxrows = 10)
            col = row.column(align = True)
            col.operator('so.op0_id', text = '', icon = 'ZOOMIN')
            col.operator('so.op1_id', text = '', icon = 'ZOOMOUT')
            col.operator('so.op9_id', text = '', icon = 'CANCEL')
            
            layout.operator('so.op8_id', text = 'Apply')

# ------ operator 0 ------ add item from collection
class so_op0(bpy.types.Operator):
    bl_idname = 'so.op0_id'
    bl_label = '....'

    def execute(self, context):
        en0 = context.scene.so_custom_props.en0
        collection_ = context.scene.so_custom_collection_

        if en0 == 's':
            so_buf.name = 'Scale'
        elif en0 == 'i':
            so_buf.name = 'Inset'
        elif en0 == 'r':
            so_buf.name = 'Rotate'
        elif en0 == 'e':
            so_buf.name = 'Extrude'

        collection_.add()
        so_buf.i += 1
        collection_[-1].name = '{}'.format(so_buf.i) + so_buf.name
        collection_[-1].na = so_buf.name

        collection_[-1].template_list_controls = 'ang:en2' if en0 == 'r' else 'd:en1'
        return {'FINISHED'}

# ------ operator 1 ------ remove item from collection
class so_op1(bpy.types.Operator):
    bl_idname = 'so.op1_id'
    bl_label = '....'

    def execute(self, context):
        collection_ = context.scene.so_custom_collection_
        collection_.remove(so_buf.i - 1)
        if so_buf.i != 0:
            so_buf.i -= 1
        return {'FINISHED'}

# ------ operator 2 ------ get axis
class so_op2(bpy.types.Operator):
    bl_idname = 'so.op2_id'
    bl_label = '....'

    def execute(self, context):
        edit_mode_out()
        ob_act = context.active_object
        bme = bmesh.new()
        bme.from_mesh(ob_act.data)
        so_buf.list_axis[:] = []      # list clear
        so_buf.list_axis = [v.index for v in bme.verts if v.select]
        bme.to_mesh(ob_act.data)
        edit_mode_in()
        bpy.ops.mesh.select_all(action = 'DESELECT')
        return {'FINISHED'}

# ------ operator 3 ------ get pivot point
class so_op3(bpy.types.Operator):
    bl_idname = 'so.op3_id'
    bl_label = '....'

    def execute(self, context):
        edit_mode_out()
        ob_act = context.active_object
        bme = bmesh.new()
        bme.from_mesh(ob_act.data)
        so_buf.list_pivot[:] = []      # list clear
        so_buf.list_pivot = [v.index for v in bme.verts if v.select]
        bme.to_mesh(ob_act.data)
        edit_mode_in()
        bpy.ops.mesh.select_all(action = 'DESELECT')
        return {'FINISHED'}

# ------ operator 4 ------ scale
class so_op4(bpy.types.Operator):
    bl_idname = 'so.op4_id'
    bl_label = 'Scale'
    bl_options = {'REGISTER', 'UNDO'}

    opp = FloatProperty( name = '', default = 0.04, min = 0.0, max = 100.0, step = 1, precision = 3 )
    b = BoolProperty( name = '', default = False )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label('Scale amount:')
        row = box.split(0.80, align = True)
        row.prop(self, 'opp')
        row.prop(self, 'b', text = 'In', toggle = True)

    def execute(self, context):
        b = self.b
        opp = self.opp

        edit_mode_out()
        ob_act = context.active_object
        bme = bmesh.new()
        bme.from_mesh(ob_act.data)

        list_0 = [[v.index for v in e.verts] for e in bme.edges if e.select and e.is_valid]
        dict_0 = get_adj_v_(list_0)
        list_tmp = [i for i in dict_0 if (len(dict_0[i]) > 2)]
        list_fl = [i for i in dict_0 if (len(dict_0[i]) == 1)]

        if len(list_0) < 2:
            self.report({'INFO'}, 'At least two edges must be selected.')
            edit_mode_in()
            return {'CANCELLED'}
        elif len(list_0) != 0:
            if len(list_tmp) != 0:
                self.report({'INFO'}, 'Multiple edge chains not supported')
                edit_mode_in()
                return {'CANCELLED'}
            elif len(list_tmp) == 0:
                if len(list_fl) > 2:
                    self.report({'INFO'}, 'Select only one edge chain or edge loop')
                    edit_mode_in()
                    return {'CANCELLED'}
                elif len(list_fl) <= 2:
                    loop = is_loop_(list_fl)
                    list_1 = sort_list_(loop, list_0, list_fl)
                    no = get_direction_(bme, list_1)
                    if no == None:
                        self.report({'INFO'}, 'Angle between selected edges equal to 0 or 180 unable to calculate direction.')
                        edit_mode_in()
                        return {'CANCELLED'}
                    elif no != None:
                        scale_(bme, b, opp, list_1, loop)

        bme.to_mesh(ob_act.data)
        edit_mode_in()
        return {'FINISHED'}

# ------ operator 5 ------ inset
class so_op5(bpy.types.Operator):
    bl_idname = 'so.op5_id'
    bl_label = 'Inset'
    bl_options = {'REGISTER', 'UNDO'}

    opp = FloatProperty( name = '', default = 0.04, min = 0.0, max = 100.0, step = 1, precision = 3 )
    b = BoolProperty( name = '', default = False )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label('Inset amount:')
        row = box.split(0.80, align = True)
        row.prop(self, 'opp')
        row.prop(self, 'b', text = 'In', toggle = True)

    def execute(self, context):
        b = self.b
        opp = self.opp

        edit_mode_out()
        ob_act = context.active_object
        bme = bmesh.new()
        bme.from_mesh(ob_act.data)

        list_0 = [[v.index for v in e.verts] for e in bme.edges if e.select and e.is_valid]
        dict_0 = get_adj_v_(list_0)
        list_tmp = [i for i in dict_0 if (len(dict_0[i]) > 2)]
        list_fl = [i for i in dict_0 if (len(dict_0[i]) == 1)]

        if len(list_0) < 2:
            self.report({'INFO'}, 'At least two edges must be selected.')
            edit_mode_in()
            return {'CANCELLED'}
        elif len(list_0) != 0:
            if len(list_tmp) != 0:
                self.report({'INFO'}, 'Multiple edge chains not supported')
                edit_mode_in()
                return {'CANCELLED'}
            elif len(list_tmp) == 0:
                if len(list_fl) > 2:
                    self.report({'INFO'}, 'Select only one edge chain or edge loop')
                    edit_mode_in()
                    return {'CANCELLED'}
                elif len(list_fl) <= 2:
                    loop = is_loop_(list_fl)
                    list_1 = sort_list_(loop, list_0, list_fl)
                    no = get_direction_(bme, list_1)
                    if no == None:
                        self.report({'INFO'}, 'Angle between selected edges equal to 0 or 180 unable to calculate direction.')
                        edit_mode_in()
                        return {'CANCELLED'}
                    elif no != None:
                        tmp = inset_(bme, opp, b, list_1, loop)

        list_usel = [bme.edges[e.index].select_set(0) for e in bme.edges if e.select]
        del list_usel

        list_sel = [bme.verts[vi].select_set(1) for vi in tmp]
        del list_sel

        bme.to_mesh(ob_act.data)
        edit_mode_in()
        return {'FINISHED'}

# ------ operator 6 ------ rotate
class so_op6(bpy.types.Operator):
    bl_idname = 'so.op6_id'
    bl_label = 'Rotate'
    bl_options = {'REGISTER', 'UNDO'}

    ang = FloatProperty( name = '', default = 5.0, min = 0.0, max = 360.0, step = 1, precision = 3 )
    b = BoolProperty( name = '', default = False )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label('Rotation angle:')
        row = box.split(0.60, align = True)
        row.prop(self, 'ang')
        row.prop(self, 'b', text = 'Clockwise', toggle = True)

    def execute(self, context):
        b = self.b
        ang = self.ang
        ax = context.scene.so_custom_props.en_ax
        pivot = context.scene.so_custom_props.en_p

        edit_mode_out()
        ob_act = context.active_object
        bme = bmesh.new()
        bme.from_mesh(ob_act.data)

        list_0 = [v.index for v in bme.verts if v.select and v.is_valid]

        if len(list_0) == 0:
            self.report({'INFO'}, 'Nothing selected unable to continue.')
            edit_mode_in()
            return {'CANCELLED'}
        elif len(list_0) != 0:
            if ax == 'ar':
                if len(so_buf.list_axis) == 0:
                    self.report({'INFO'}, 'No axis or pivot point stored in memory unable to continue.')
                    edit_mode_in()
                    return {'CANCELLED'}
                else:
                    rotate_(bme, list_0, pivot, ax, b, ang)
            elif ax != 'ar':
                rotate_(bme, list_0, pivot, ax, b, ang)

        bme.to_mesh(ob_act.data)
        edit_mode_in()
        return {'FINISHED'}

# ------ operator 7 ------ extrude
class so_op7(bpy.types.Operator):
    bl_idname = 'so.op7_id'
    bl_label = 'Extrude'
    bl_options = {'REGISTER', 'UNDO'}
    
    b = BoolProperty( name = '', default = False )
    ea = FloatProperty( name = '', default = 0.04, min = 0.0, max = 100.0, step = 1, precision = 3 )
    
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label('Extrude amount:')
        row = box.split(0.80, align = True)
        row.prop(self, 'ea')
        row.prop(self, 'b', text = 'In', toggle = True)

    def execute(self, context):
        b = self.b
        ea = self.ea

        edit_mode_out()
        ob_act = context.active_object
        bme = bmesh.new()
        bme.from_mesh(ob_act.data)

        list_0 = [v.index for v in bme.verts if v.select and v.is_valid]

        if len(list_0) == 0:
            self.report({'INFO'}, 'No outline selected')
            edit_mode_in()
            return {'CANCELLED'}
        elif len(list_0) != 0:
            list_1 = [[v.index for v in e.verts] for e in bme.edges if e.select and e.is_valid]
            dict_0 = get_adj_v_(list_1)
            so_buf.list_1[:] = []
            so_buf.list_1.append(get_no_(bme, dict_0))
            if so_buf.list_1[0] == None:
                self.report({'INFO'}, 'Angle Error')
                edit_mode_in()
                return {'CANCELLED'}
            else:
                tmp = extrude_(bme, list_0, list_1, ea, b)

        list_usel = [bme.edges[e.index].select_set(0) for e in bme.edges if e.select]
        del list_usel
        for i in tmp:
            bme.verts[tmp[i][1]].select_set(1)

        bme.to_mesh(ob_act.data)
        edit_mode_in()
        return {'FINISHED'}

# ------ operator 8 ------
class so_op8(bpy.types.Operator):
    bl_idname = 'so.op8_id'
    bl_label = 'Go'
    bl_options = {'REGISTER', 'UNDO'}

    n = IntProperty( name = '', default = 1, min = 1, max = 100, step = 1 )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.split(0.60, align = True)
        row.label('Number of iterations:')
        row.prop(self, 'n')

    def execute(self, context):
        n = self.n
        collection_ = context.scene.so_custom_collection_

        edit_mode_out()
        ob_act = context.active_object
        bme = bmesh.new()
        bme.from_mesh(ob_act.data)

        list_0 = [[v.index for v in e.verts] for e in bme.edges if e.select and e.is_valid]
        dict_0 = get_adj_v_(list_0)
        list_tmp = [i for i in dict_0 if (len(dict_0[i]) > 2)]
        list_fl = [i for i in dict_0 if (len(dict_0[i]) == 1)]

        if len(list_0) < 2:      # check for empty list
            self.report({'INFO'}, 'At least two edges must be selected.')
            edit_mode_in()
            return {'CANCELLED'}
        elif len(list_0) != 0:
            if len(list_tmp) != 0:      # check if any of the vertices has more than two neighbors
                self.report({'INFO'}, 'Multiple edge chains not supported')
                edit_mode_in()
                return {'CANCELLED'}
            elif len(list_tmp) == 0:
                if len(list_fl) > 2:
                    self.report({'INFO'}, 'Select only one edge chain or edge loop')
                    edit_mode_in()
                    return {'CANCELLED'}
                elif len(list_fl) <= 2:
                    loop = is_loop_(list_fl)
                    list_1 = sort_list_(loop, list_0, list_fl)
                    no = get_direction_(bme, list_1)
                    if no == None:
                        self.report({'INFO'}, 'Angle between selected edges equal to 0 or 180 unable to calculate direction.')
                        edit_mode_in()
                        return {'CANCELLED'}
                    elif no != None:
                        for i in range(n):
                            for j in collection_:
                                if j.na == 'Scale':
                                    scale_(bme, True if j.en1 == 'in' else False, j.d, list_1, loop)
                                elif j.na == 'Inset':
                                    t = inset_(bme, j.d, True if j.en1 == 'in' else False, list_1, loop)
                                    list_1[:] = []
                                    list_1.extend(t)
                                elif j.na == 'Rotate':
                                    rotate_1(bme, list_1, context.scene.so_custom_props.en_p, context.scene.so_custom_props.en_ax, True if j.en2 == 'cw' else False, j.ang)
                                elif j.na == 'Extrude':
                                    t1 = extrude_1(bme, list_1, j.d, True if j.en1 == 'in' else False, loop)
                                    list_1[:] = []
                                    list_1.extend(t1)

        bme.to_mesh(ob_act.data)
        edit_mode_in()
        return {'FINISHED'}

# ------ operator 9 ------ remove item from collection
class so_op9(bpy.types.Operator):
    bl_idname = 'so.op9_id'
    bl_label = '....'

    def execute(self, context):
        for i in context.scene.so_custom_collection_:
            n = len(context.scene.so_custom_collection_)
            context.scene.so_custom_collection_.remove(n-1)

        so_buf.i = 0
        return {'FINISHED'}

# ------ ------
class_list = [ so_p0, so_p_group0, so_p_group1, so_op0, so_op1, so_op2, so_op3, so_op4, so_op5, so_op6, so_op7, so_op8, so_op9 ]
               
# ------ register ------
def register():
    for c in class_list:
        bpy.utils.register_class(c)

    bpy.types.Scene.so_custom_props = PointerProperty(type = so_p_group0)
    bpy.types.Scene.so_custom_collection_ = CollectionProperty(type = so_p_group1)

# ------ unregister ------
def unregister():
    for c in class_list:
        bpy.utils.unregister_class(c)

    for k in ['so_custom_props', 'so_custom_collection_']:
        if k in bpy.context.scene:
            del bpy.context.scene[k]

# ------ ------
if __name__ == "__main__":
    register()