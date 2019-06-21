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

from itertools import chain
import bpy
from mod_node import *
from pynodes_framework import group
from typedesc import *


@mod_node_item("Group")
class ModifierNode_group(bpy.types.Node, ModifierNode, group.NodeGroup):
    bl_idname = "ModifierNode_group"
    bl_label = "Group"

    def nodetree_poll(self, nodetree):
        return isinstance(nodetree, ModifierNodeTree)

    # specialized compile function
    def compile(self, compiler):
        interface_map = {}
        for socket in chain(self.inputs, self.outputs):
            is_output = socket.is_output
            node_param = self.find_node_parameter(socket)
            pass_type = node_datatype_typedesc[node_param.datatype]
            mod_inst = compiler.modifier("pass_%s" % pass_type.basetype, "%s_%s" % (self.name, socket.identifier))

            param_name = "out" if is_output else "in"

            if self.socket_data():
                # XXX use item default for outputs instead of socket property? (*should* be the same)
                value = getattr(self.socket_data(), socket.identifier, None)
                if value is not None:
                    prop = self.socket_data().bl_rna.properties.get(socket.identifier, None)
                    mod_inst.parameter(param_name, pass_type, prop, value)

            compiler.map_socket(mod_inst, param_name, socket)
            interface_map[socket.identifier] = mod_inst

        nodetree = self.nodetree
        if nodetree is not None:
            compiler.node_tree(nodetree, interface_map)


@mod_node_item("Group")
class ModifierNode_group_input(bpy.types.Node, ModifierNode, group.NodeGroupInput):
    bl_idname = "ModifierNode_group_input"
    bl_label = "Group Input"

    # specialized compile function
    def compile(self, compiler):
        for socket in self.outputs:
            mod_inst = compiler.interface_map.get(socket.identifier, None)
            if not mod_inst:
                continue
            compiler.map_socket(mod_inst, "out", socket)


@mod_node_item("Group")
class ModifierNode_group_output(bpy.types.Node, ModifierNode, group.NodeGroupOutput):
    bl_idname = "ModifierNode_group_output"
    bl_label = "Group Output"

    # specialized compile function
    def compile(self, compiler):
        for socket in self.inputs:
            mod_inst = compiler.interface_map.get(socket.identifier, None)
            if not mod_inst:
                continue

            value = getattr(self.socket_data(), socket.identifier, None)
            if value is not None:
                # convert struct objects into bpy path strings
                if isinstance(value, StructRNA):
                    value = idref.get_full_path(value)
                mod_inst.parameter("in", value)
            compiler.map_socket(mod_inst, "in", socket)


def register():
    bpy.utils.register_class(ModifierNode_group)
    bpy.utils.register_class(ModifierNode_group_input)
    bpy.utils.register_class(ModifierNode_group_output)

def unregister():
    bpy.utils.unregister_class(ModifierNode_group)
    bpy.utils.unregister_class(ModifierNode_group_input)
    bpy.utils.unregister_class(ModifierNode_group_output)
