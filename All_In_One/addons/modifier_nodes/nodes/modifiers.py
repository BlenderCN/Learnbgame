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
from bpy.props import *
from itertools import chain
from mod_node import *
from typedesc import update_socket_value


@mod_node_item("Modifiers")
class ModifierNode_array(bpy.types.Node, ModifierNode):
    bl_idname = "ModifierNode_array"
    bl_label = "Array"

    modifier = "array"

    _fit_type_items = [(item.identifier, item.name, item.description) for item in bpy.types.ArrayModifier.bl_rna.properties['fit_type'].enum_items]

    def _fit_type_update(node, context):
        fit_type = node.fit_type
        if fit_type == 'FIXED_COUNT':
            unused_sockets = {'fit_length', 'curve'}
        elif fit_type == 'FIT_LENGTH':
            unused_sockets = {'count', 'curve'}
        elif fit_type == 'FIT_CURVE':
            unused_sockets = {'count', 'fit_length'}
        else:
            unused_sockets = {'count', 'fit_length', 'curve'}

        for socket in chain(node.inputs, node.outputs):
            socket.enabled = (socket.identifier not in unused_sockets)

        update_socket_value(node, context)

    fit_type = EnumProperty(name="Fit Type", description="Array length calculation method",
                            items=_fit_type_items, default="FIXED_COUNT", update=_fit_type_update)

    def update(self):
        self._fit_type_update(None)

    def draw_buttons(self, context, layout):
        layout.prop(self, "fit_type")


def register():
    bpy.utils.register_class(ModifierNode_array)

def unregister():
    bpy.utils.unregister_class(ModifierNode_array)
