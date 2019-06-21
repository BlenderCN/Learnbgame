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
from itertools import chain
from pynodes_framework import base, group, category, parameter, idref
import database, generator, typedesc
from util import classproperty


class ModifierNodeSocket(bpy.types.NodeSocket, base.NodeSocket):
    bl_idname = "ModifierNodeSocket"
    parameter_types = typedesc.modifier_parameter_types


class ModifierNodeTree(bpy.types.NodeTree, group.NodeGroupTree):
    bl_idname = "ModifierNodeTree"
    bl_icon = 'MODIFIER'
    bl_label = "Modifier"
    socket_type = ModifierNodeSocket

    def update(self):
        #group.NodeGroupTree.update(self)

        database.tag_update(self)


# poll function to check the node space tree type
def poll_space_type(context):
    space = context.space_data
    if not (space.type == 'NODE_EDITOR' and space.tree_type == ModifierNodeTree.bl_idname):
        return False
    return True

# poll function to check a node tree
def poll_node_tree(node_tree):
    if not (node_tree and isinstance(node_tree, ModifierNodeTree)):
        return False
    return True

# poll function to check the node space tree editable instance
def poll_space_edit(context):
    space = context.space_data
    if not (space.type == 'NODE_EDITOR' and poll_node_tree(space.edit_tree)):
        return False
    return True


class ModifierNode(base.Node):
    socket_type = ModifierNodeSocket

    @classmethod
    def register(cls):
        mod_name = getattr(cls, 'modifier', None)
        if mod_name is None:
            return
        mod = generator._modifiers[mod_name]
        for param in mod.parameters:
            typedesc.define_node_params(cls, param.name, param.typedesc, param.is_output, param.default, param.metadata)

    @classmethod
    def poll(cls, node_tree):
        return poll_node_tree(node_tree)

    def find_socket(self, identifier, is_output):
        for socket in (self.outputs if is_output else self.inputs):
            if socket.identifier == identifier:
                return socket
        return None

    # Default compile function uses class attribute 'modifier'
    # and automatically assigns values from node sockets properties
    def compile(self, compiler):
        mod_inst = compiler.modifier(self.modifier, self.name)

        for param in mod_inst.modifier.parameters:
            if not param.is_output:
                value = getattr(self.socket_data(), param.name, None)
                if value is not None:
                    prop = self.socket_data().bl_rna.properties.get(param.name, None)
                    mod_inst.parameter(param.name, param.typedesc, prop, value)

            socket = self.find_socket(param.name, param.is_output)
            if socket is not None:
                compiler.map_socket(mod_inst, param.name, socket)


mod_node_item = category.NodeCategorizer(ModifierNodeTree)

def register():
    ModifierNodeTree.register_class()
    bpy.utils.register_class(ModifierNodeSocket)

def unregister():
    ModifierNodeTree.unregister_class()
    bpy.utils.unregister_class(ModifierNodeSocket)
