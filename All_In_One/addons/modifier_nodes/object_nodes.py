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

# <pep8 compliant>

import bpy
from bpy.types import Panel, Operator
import database
from pynodes_framework.idref import bpy_register_idref, bpy_unregister_idref, IDRefProperty, draw_idref


class ModifierGenerateOperator(Operator):
    """ Generate an object's modifier stack using nodes """
    bl_idname = "modifier_nodes.generate"
    bl_label = "Generate"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        ob = context.object
        if not (ob and ob.type == 'MESH' and ob.data):
            return False
        return True

    def execute(self, context):
        ob = context.object

        return {'FINISHED'}


class ModifierNodesPanel(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "modifier"
    bl_label = "Modifier Nodes"
    bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        if context.object is None:
            return False
        return True

    def draw(self, context):
        layout = self.layout

        draw_idref(layout, context.object, "modifier_node_tree")
        layout.operator("modifier_nodes.generate")


def register():
    bpy.utils.register_class(ModifierGenerateOperator)
    bpy.utils.register_class(ModifierNodesPanel)

    def poll_modifier_node_tree(self, node_tree):
        return node_tree.bl_idname == 'ModifierNodeTree'

    def update_modifier_node_tree(self, context):
        database.sync_object(self, force=True)

    bpy_register_idref(bpy.types.Object, "modifier_node_tree", 
        IDRefProperty(name="Modifier Nodes", description="Node tree defining modifiers", idtype='NODETREE', options={'FAKE_USER'}, update=None, poll=poll_modifier_node_tree))

def unregister():
    bpy_unregister_idref(bpy.types.Object, "modifier_node_tree")
    bpy.utils.unregister_class(ModifierNodesPanel)
    bpy.utils.unregister_class(ModifierGenerateOperator)
