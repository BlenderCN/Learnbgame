# ## BEGIN GPL LICENSE BLOCK ##
#
#   Copyright (C) 2017 Diego Gangl
#   <diego@sinestesia.co>
#
#   Copyright (C) 2017 Emmanuel Boyer
#
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 2
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ## END GPL LICENSE BLOCK ##

""" BlackBody Reference Addon """

import bpy
from bpy.props import (StringProperty, FloatProperty,
                       IntProperty, CollectionProperty)

bl_info = {
    'name': 'BlackBody Reference',
    'description': 'Adds a panel with a searchable list of Blackbody values',
    'author': 'Diego Gangl, Emmanuel Boyer',
    'version': (1, 0, 0),
    'blender': (2, 75, 0),
    'location': 'Nodes',
    'warning': '',
    'wiki_url': '',
    "category": "Learnbgame",
}


# -----------------------------------------------------------------------------
# VALUES
# -----------------------------------------------------------------------------

class BBREF_PROP_Value(bpy.types.PropertyGroup):
    name = StringProperty(
        name='Name',
        description='Material name')

    value = FloatProperty(
        name='IOR Value',
        precision=5,
        description='The Blackbody value for the selected item')


def build_BlackbodyRef_list():
    """ Fill the list with Blackbody values """

    def add(val):
        item = bpy.context.window_manager.BBRef.add()
        item.name = val[0]
        item.value = val[1]

    # BEGIN List of Blackbody values
    BlackbodyRef_list = [
        ('Match Flame', 1700),
        ('Candel Flame', 1850),
        ('Sunset', 1850),
        ('Std Incandescent Lamp', 2400),
        ('Soft Incandescent Lamp', 2550),
        ('Soft Fluorescent or LED', 2700),
        ('Warm Fluorescent or LED', 3000),
        ('Studio Lamp Photofloods', 3200),
        ('Studio "CP" Light', 3350),
        ('Moonlight', 4150),
        ('Horizon Daylight', 5000),
        ('Fluorescent or CFL Lamp', 5000),
        ('Vertical Daylight', 5500),
        ('Electronic Flash', 6000),
        ('Clear Blue Sky', 15000)]
    # END List of Blackbody values

    [add(val) for val in BlackbodyRef_list]


# -----------------------------------------------------------------------------
# OPERATOR
# -----------------------------------------------------------------------------

class BBREF_OT_AddNode(bpy.types.Operator):
    bl_idname = 'bbref.add_value_node'
    bl_label = 'Add value as node'
    bl_description = 'Add Blackbody as a value node'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        try:
            return context.active_object.active_material.use_nodes
        except (AttributeError, IndexError):
            return False

    def execute(self, context):

        wm = context.window_manager
        item = wm.BBRef[wm.BBRef_index]

        nodes = context.active_object.active_material.node_tree.nodes
        node = nodes.new('ShaderNodeBlackbody')
        node.label = item.name + ' Blackbody'
        node.location = 100, 100
        node.inputs[0].default_value = item.value


        return {'FINISHED'}


# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------


class BBREF_UIL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(0.75)
            split.label(text=item.name, translate=False)
            split.label(text='{:.3f}'.format(item.value), translate=False)


class BBREF_PT_MainPanel(bpy.types.Panel):
    bl_label = "Blackbody Reference"
    bl_idname = "BBREF_PT_MainPanel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        space_node = context.space_data
        return space_node is not None and space_node.node_tree is not None

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager

        layout.template_list('BBREF_UIL_List', '', wm,
                             'BBRef', wm, 'BBRef_index')

        layout.operator('bbref.add_value_node')


# -----------------------------------------------------------------------------
# Register
# -----------------------------------------------------------------------------

def register():
    bpy.utils.register_class(BBREF_PROP_Value)
    bpy.utils.register_class(BBREF_OT_AddNode)

    wm = bpy.types.WindowManager
    wm.BBRef = CollectionProperty(type=BBREF_PROP_Value)
    wm.BBRef_index = IntProperty(name='IOR Reference Index', default=0)

    if len(bpy.context.window_manager.BBRef) == 0:
        build_BlackbodyRef_list()

    bpy.utils.register_class(BBREF_UIL_List)
    bpy.utils.register_class(BBREF_PT_MainPanel)


def unregister():
    wm = bpy.types.WindowManager

    del wm.BBRef
    del wm.BBRef_index

    bpy.utils.unregister_class(BBREF_UIL_List)
    bpy.utils.unregister_class(BBREF_PT_MainPanel)
    bpy.utils.unregister_class(BBREF_PROP_Value)
    bpy.utils.unregister_class(BBREF_OT_AddNode)


if __name__ == "__main__":
    register()
