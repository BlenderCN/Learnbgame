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


@mod_node_item("Math")
class ModifierNode_scalar_math(bpy.types.Node, ModifierNode):
    bl_idname = "ModifierNode_scalar_math"
    bl_label = "Math"

    modifier = "scalar_math"

    _operation_items = [
        ("ADD",     "Add",          ""),
        ("SUB",     "Subtract",     ""),
        ("MUL",     "Multiply",     ""),
        ("DIV",     "Divide",       ""),
        ("SIN",     "Sine",         ""),
        ("COS",     "Cosine",       ""),
        ("TAN",     "Tangent",      ""),
        ("ASIN",    "Arcsine",      ""),
        ("ACOS",    "Arccosine",    ""),
        ("ATAN",    "Arctangent",   ""),
        ("ATAN2",   "Arctangent2",  ""),
        ("POW",     "Power",        ""),
        ("LOG",     "Logarithm",    ""),
        ("ROUND",   "Round",        ""),
        ("FLOOR",   "Floor",        ""),
        ("CEIL",    "Ceil",         ""),
        ("GREATER", "Greater",      ""),
        ("LESS",    "Less",         ""),
        ("MIN",     "Min",          ""),
        ("MAX",     "Max",          ""),
        ]

    def _operation_update(node, context):
        binary_ops = {'ADD', 'SUB', 'MUL', 'DIV', 'ATAN2', 'POW', 'LOG', 'MIN', 'MAX'}
        unary_ops = {'SIN', 'COS', 'TAN', 'ASIN', 'ACOS', 'ATAN', 'ROUND', 'FLOOR', 'CEIL'}
        compare_ops = {'GREATER', 'LESS'}

        op = node.operation
        if op in binary_ops:
            used_sockets = {'a', 'b', 'rf'}
        elif op in unary_ops:
            used_sockets = {'a', 'rf'}
        elif op in compare_ops:
            used_sockets = {'a', 'b', 'rb'}
        else:
            used_sockets = set()

        names = {
            'a'  : 'Value',
            'b'  : 'Value',
            'rf' : 'Result',
            'rb' : 'Result',
            }
        if op == 'pow':
            names['b'] = 'Exponent'
        elif op == 'log':
            names['b'] = 'Base'

        for socket in chain(node.inputs, node.outputs):
            socket.enabled = (socket.identifier in used_sockets)
            socket.name = names[socket.identifier]

        update_socket_value(node, context)

    operation = EnumProperty(name="Operation", description="Operation combining the input values",
                             items=_operation_items, default="ADD", update=_operation_update)

    def update(self):
        self._operation_update(None)

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation")


@mod_node_item("Math")
class ModifierNode_vector_math(bpy.types.Node, ModifierNode):
    bl_idname = "ModifierNode_vector_math"
    bl_label = "Vector Math"

    modifier = "vector_math"

    _operation_items = [
        ("ADD",         "Add",          ""),
        ("SUB",         "Subtract",     ""),
        ("MUL",         "Multiply",     ""),
        ("DIV",         "Divide",       ""),
        ("SEPARATE",    "Separate",     ""),
        ("COMBINE",     "Combine",      ""),
        ("DOT",         "Dot",          ""),
        ("CROSS",       "Cross",        ""),
        ("LENGTH",      "Length",       ""),
        ("DISTANCE",    "Distance",     ""),
        ]

    def _operation_update(node, context):
        op = node.operation
        if op in {'DOT', 'DISTANCE'}:
            used_sockets = {'a', 'b', 'rf'}
        elif op in {'LENGTH'}:
            used_sockets = {'a', 'rf'}
        elif op in {'ADD', 'SUB', 'MUL', 'DIV', 'CROSS'}:
            used_sockets = {'a', 'b', 'rv'}
        elif op in {'SEPARATE'}:
            used_sockets = {'a', 'rx', 'ry', 'rz'}
        elif op in {'COMBINE'}:
            used_sockets = {'x', 'y', 'z', 'rv'}
        else:
            used_sockets = set()

        for socket in chain(node.inputs, node.outputs):
            socket.enabled = (socket.identifier in used_sockets)

        update_socket_value(node, context)

    operation = EnumProperty(name="Operation", description="Operation combining the input values",
                             items=_operation_items, default="ADD", update=_operation_update)

    def update(self):
        self._operation_update(None)

    def draw_buttons(self, context, layout):
        layout.prop(self, "operation")


def register():
    bpy.utils.register_class(ModifierNode_scalar_math)
    bpy.utils.register_class(ModifierNode_vector_math)

def unregister():
    bpy.utils.unregister_class(ModifierNode_scalar_math)
    bpy.utils.unregister_class(ModifierNode_vector_math)
