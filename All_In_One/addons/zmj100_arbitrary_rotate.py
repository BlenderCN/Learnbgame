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
    'name': 'arbitrary rotate',
    'author': '',
    'version': (0, 1, 2),
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
from bpy.props import FloatProperty
from mathutils import Matrix
from math import radians

# ------ ------
def edit_mode_out():
    bpy.ops.object.mode_set(mode = 'OBJECT')

def edit_mode_in():
    bpy.ops.object.mode_set(mode = 'EDIT')

def get_mesh_data_():
    edit_mode_out()
    ob_act = bpy.context.active_object
    tmp = ob_act.data
    edit_mode_in()
    return tmp

def list_clear_(l):
    l[:] = []
    return l

# ------ ------
class a_buf():
    list_0 = []
    list_1 = []
    msg_type = ''
    msg = ''

# ------ ------
def f_(me, ang):

    p1 = (me.vertices[a_buf.list_0[0]].co).copy()
    p2 = (me.vertices[a_buf.list_0[1]].co).copy()
    rp = (me.vertices[a_buf.list_1[0]].co).copy()
    axis = p2 - p1
    mtrx = Matrix.Rotation(radians(-ang), 3, axis)

    for v in me.vertices:
        if v.select:
            q = (v.co).copy()
            a = q - rp
            b = mtrx * a
            c = b + rp
            v.co = c

# ------ panel 0 ------
class a_p0(bpy.types.Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_idname = 'a_p0_id'
    bl_label = 'Arbitrary Rotate'
    bl_context = 'mesh_edit'

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label('Store data :')
        row = box.row(align = False)
        row_sp = row.split(0.55)
        row_sp.operator('a.op0_id', text = 'Rotation axis')
        row_sp.operator('a.op1_id', text = 'Pivot point')
        row1 = layout.split(0.80)
        row1.operator('a.op2_id', text = 'Rotate')
        row1.operator('a.op4_id', text = '?')

# ------ operator 0 ------
class a_op0(bpy.types.Operator):

    bl_idname = 'a.op0_id'
    bl_label = ''
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        me = get_mesh_data_()
        list_clear_(a_buf.list_0)
        for v in me.vertices:
            if v.select:
                a_buf.list_0.append(v.index)
                bpy.ops.mesh.select_all(action = 'DESELECT')
        return {'FINISHED'}

# ------ operator 1 ------
class a_op1(bpy.types.Operator):

    bl_idname = 'a.op1_id'
    bl_label = ''
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        me = get_mesh_data_()
        list_clear_(a_buf.list_1)
        for v in me.vertices:
            if v.select:
                a_buf.list_1.append(v.index)
                bpy.ops.mesh.select_all(action = 'DESELECT')
        return {'FINISHED'}

# ------ operator 2 ------
class a_op2(bpy.types.Operator):

    bl_idname = 'a.op2_id'
    bl_label = 'Arbitrary Rotate'
    bl_options = {'REGISTER', 'UNDO'}

    ang = FloatProperty( name = '', default = 0.0, min = -360.0, max = 360.0, step = 100, precision = 3 )

    def draw(self, context):
        layout = self.layout
        layout.label('Rotation angle:')
        layout.prop(self, 'ang', slider = True)

    def execute(self, context):

        ang = self.ang

        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data

        if len(a_buf.list_0) == 2 and len(a_buf.list_1) == 1:
            f_(me, ang)
        else:
            a_buf.msg_type = 'Error :'
            a_buf.msg = 'No rotation axis or pivot point stored in memory.'
            bpy.ops.a.msg_id('INVOKE_DEFAULT')
            edit_mode_in()
            return {'CANCELLED'}
        edit_mode_in()
        return {'FINISHED'}

# ------ operator 3 ------
class a_op3(bpy.types.Operator):

    bl_idname = 'a.op3_id'
    bl_label = ''

    def draw(self, context):
        layout = self.layout
        layout.label('To use:')
        layout.label('Select two vertices or edge that you want to use as rotation axis')
        layout.label('and click Rotation axis button to store data.')
        layout.label('Select vertex that you want to use as pivot point')
        layout.label('and click Pivot point button to store data.')
        layout.label('Select vertices that you want to rotate and click Rotate button.')
        layout.label('Adjust angle with Rotation Angle slider.')
        layout.label('')
    
    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width = 400)

# ------ operator 4 ------
class a_op4(bpy.types.Operator):
    bl_idname = 'a.op4_id'
    bl_label = ''

    def execute(self, context):
        bpy.ops.a.op3_id('INVOKE_DEFAULT')
        return {'FINISHED'}

# ------ ------
class a_msg_popup(bpy.types.Operator, a_buf):

    bl_idname = 'a.msg_id'
    bl_label = ''

    def draw(self, context):
        if self.msg_type == 'Error :':
            self.t = 'ERROR'
        else:
            self.t = 'NONE'
                
        layout = self.layout
        row = layout.split(0.20)
        row.label(self.msg_type, icon = self.t)
        row.label(self.msg)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width = 400)

# ------ ------
class_list = [ a_p0, a_op0, a_op1, a_op2, a_op3, a_op4, a_msg_popup ]

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