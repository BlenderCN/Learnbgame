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

#
bl_info = {
    'name': 'Object align',
    'author': '',
    'version': (0, 0, 0),
    'blender': (2, 5, 8),
    'api': 37809,
    'location': '',
    'description': '',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Mesh' }

#
import bpy
from bpy.props import EnumProperty, PointerProperty, FloatProperty, BoolProperty
from mathutils import Vector
from math import *


class oa_p_group0(bpy.types.PropertyGroup):

    t = EnumProperty( items =( ('opt0', 'location', ''),
                               ('opt1', 'rotation', ''),
                               ('opt2', 'scale', '') ),
                      name = 'test',
                      default = 'opt0' )


def list_clear_(l):
    l[:] = []
    return l

def init_props():
    bpy.context.scene.my_custom_props.t = 'opt0'

def rad_(d):
        return d * pi / 180


class oa_buf():
    msg_type = ''
    msg = ''
    list_0 = []

#
class oa_p0(bpy.types.Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Object align'
    bl_context = 'objectmode'
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.my_custom_props, 't', expand = True)
        spl = layout.split(2/3)
        spl.label('Store data :')
        spl.operator('oa.op0_id', text = 'object')
        row = layout.row(align = True)
        row.operator('oa.op1_id', text = 'x')
        row.operator('oa.op2_id', text = 'y')
        row.operator('oa.op3_id', text = 'z')
        spl = layout.split(0.80)
        spl.operator('oa.op4_id', text = 'Custom')
        spl.operator('oa.hp_id', text = '?')

#
class oa_msg_popup(bpy.types.Operator, oa_buf):

    bl_idname = 'oa.msg_id'
    bl_label = ''

    def draw(self, context):
        if self.msg_type == 'Error :':
            self.t = 'ERROR'
        else:
            self.t = 'NONE'
                
        layout = self.layout
        row = layout.split(0.25)
        row.label(self.msg_type, icon = self.t)
        row.label(self.msg)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)

#
class oa_h_popup(bpy.types.Operator):

    bl_idname = 'oa.hp_id'
    bl_label = ''

    def draw(self, context):
        layout = self.layout
        layout.label(text = 'Select original object and click Select Object button.')
        layout.label(text = 'Select objects that you want to align.')
        layout.label(text = 'Use x, y, z, or custom to align them.')
        layout.label(text = 'If using custom select axis with checkbox first.')
    
    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)

#
class oa_op0(bpy.types.Operator):

    bl_idname = 'oa.op0_id'
    bl_label = ''
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        list_clear_(oa_buf.list_0)
        for ob_sel in bpy.context.selected_objects:
            oa_buf.list_0.append(ob_sel)
            ob_sel.select = False
        return {'FINISHED'}

#
class oa_op1(bpy.types.Operator):

    bl_idname = 'oa.op1_id'
    bl_label = 'x'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        c_prop = context.scene.my_custom_props.t
        if len(oa_buf.list_0) == 0:
            oa_buf.msg_type = 'Error :'
            oa_buf.msg = 'No object selected'
            bpy.ops.oa.msg_id('INVOKE_DEFAULT')
            return 'CANCELLED'
        else:
            for ob_sel in bpy.context.selected_objects:
                if c_prop == 'opt0':
                    ob_sel.location.x = oa_buf.list_0[0].location.x
                elif c_prop == 'opt1':
                    ob_sel.rotation_euler.x = oa_buf.list_0[0].rotation_euler.x
                elif c_prop == 'opt2':
                    ob_sel.scale.x = oa_buf.list_0[0].scale.x
            return {'FINISHED'}

#
class oa_op2(bpy.types.Operator):

    bl_idname = 'oa.op2_id'
    bl_label = 'y'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        c_prop = context.scene.my_custom_props.t
        if len(oa_buf.list_0) == 0:
            oa_buf.msg_type = 'Error :'
            oa_buf.msg = 'No object selected'
            bpy.ops.oa.msg_id('INVOKE_DEFAULT')
            return 'CANCELLED'
        else:
            for ob_sel in bpy.context.selected_objects:
                if c_prop == 'opt0':
                    ob_sel.location.y = oa_buf.list_0[0].location.y
                elif c_prop == 'opt1':
                    ob_sel.rotation_euler.y = oa_buf.list_0[0].rotation_euler.y
                elif c_prop == 'opt2':
                    ob_sel.scale.y = oa_buf.list_0[0].scale.y
            return {'FINISHED'}

#
class oa_op3(bpy.types.Operator):

    bl_idname = 'oa.op3_id'
    bl_label = 'z'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        c_prop = context.scene.my_custom_props.t
        if len(oa_buf.list_0) == 0:
            oa_buf.msg_type = 'Error :'
            oa_buf.msg = 'No object selected'
            bpy.ops.oa.msg_id('INVOKE_DEFAULT')
            return 'CANCELLED'
        else:
            for ob_sel in bpy.context.selected_objects:
                if c_prop == 'opt0':
                    ob_sel.location.z = oa_buf.list_0[0].location.z
                elif c_prop == 'opt1':
                    ob_sel.rotation_euler.z = oa_buf.list_0[0].rotation_euler.z
                elif c_prop == 'opt2':
                    ob_sel.scale.z = oa_buf.list_0[0].scale.z
            return {'FINISHED'}

#
class oa_op4(bpy.types.Operator):

    bl_idname = 'oa.op4_id'
    bl_label = 'Custom:'
    bl_options = {'REGISTER', 'UNDO'}

    x_ = y_ = z_ = FloatProperty( default = 0.0, min = -100.0, max = 100.0, step = 1, precision = 3 )
    rx_ = ry_ = rz_ = FloatProperty( default = 0.0, min = -360.0, max = 360.0, step = 1, precision = 3 )
    b_x = b_y = b_z = BoolProperty()

    def execute(self, context):
        c_prop = context.scene.my_custom_props.t
        for ob_sel in bpy.context.selected_objects:
                
                if c_prop == 'opt0':
                    if self.b_x == True:
                        ob_sel.location = Vector((self.x_, ob_sel.location.y, ob_sel.location.z))
                    if self.b_y == True:
                        ob_sel.location = Vector((ob_sel.location.x, self.y_, ob_sel.location.z))
                    if self.b_z == True:
                        ob_sel.location = Vector((ob_sel.location.x, ob_sel.location.y, self.z_))
                elif c_prop == 'opt1':
                    if self.b_x == True:
                        ob_sel.rotation_euler = Vector((rad_(self.rx_), ob_sel.rotation_euler.y, ob_sel.rotation_euler.z))
                    if self.b_y == True:
                        ob_sel.rotation_euler = Vector((ob_sel.rotation_euler.x, rad_(self.ry_), ob_sel.rotation_euler.z))
                    if self.b_z == True:
                        ob_sel.rotation_euler = Vector((ob_sel.rotation_euler.x, ob_sel.rotation_euler.y, rad_(self.rz_)))
                elif c_prop == 'opt2':
                    if self.b_x == True:
                        ob_sel.scale = Vector((self.x_, ob_sel.scale.y, ob_sel.scale.z))
                    if self.b_y == True:
                        ob_sel.scale = Vector((ob_sel.scale.x, self.y_, ob_sel.scale.z))
                    if self.b_z == True:
                        ob_sel.scale = Vector((ob_sel.scale.x, ob_sel.scale.y, self.z_))
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width = 200)

    def draw(self, context):
        c_prop = context.scene.my_custom_props.t
        layout = self.layout

        row = layout.split(0.25)
        row.prop(self, 'b_x', text = 'x')
        if c_prop == 'opt1':
            row.prop(self, 'rx_')
        else:
            row.prop(self, 'x_')

        row = layout.split(0.25)
        row.prop(self, 'b_y', text = 'y')
        if c_prop == 'opt1':
            row.prop(self, 'ry_')
        else:
            row.prop(self, 'y_')

        row = layout.split(0.25)
        row.prop(self, 'b_z', text = 'z')
        if c_prop == 'opt1':
            row.prop(self, 'rz_')
        else:
            row.prop(self, 'z_')


class_list = [ oa_p0, oa_op0, oa_op1, oa_op2, oa_op3, oa_op4, oa_h_popup, oa_msg_popup, oa_p_group0 ]


def register():
    for c in class_list:
        bpy.utils.register_class(c)

    bpy.types.Scene.my_custom_props = PointerProperty(type = oa_p_group0)
    init_props()

#
def unregister():
    for c in class_list:
        bpy.utils.unregister_class(c)

    del bpy.context.scene['my_custom_props']

#
if __name__ == "__main__":
    register()