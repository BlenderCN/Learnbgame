# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Mitsuba Add-On
# --------------------------------------------------------------------------
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENSE BLOCK *****

from .. import MitsubaAddon


class MitsubaNodeManager:
    locked = True

    @staticmethod
    def lock():
        MitsubaNodeManager.locked = True

    @staticmethod
    def unlock():
        MitsubaNodeManager.locked = False


## For storing of registered node types
class MitsubaNodeTypes:
    node_types = []
    plugin_nodes = {}

    @staticmethod
    def register(nt):
        MitsubaAddon.addon_register_class(nt)
        MitsubaNodeTypes.node_types.append(nt)

        for plugin in nt.plugin_types:
            if plugin != 'undefined' and plugin not in MitsubaNodeTypes.plugin_nodes:
                MitsubaNodeTypes.plugin_nodes.update({plugin: nt})
            else:
                print("Undefined or duplicate plugin: %s -- %s" % (plugin, nt.bl_idname))

        return nt

    @staticmethod
    def items():
        return MitsubaNodeTypes.node_types


class mitsuba_node:
    custom_inputs = []
    custom_outputs = []
    shader_type_compat = {'OBJECT'}
    plugin_types = {'undefined'}

    #This node is only for the Mitsuba node-tree
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'MitsubaShaderNodeTree'

    def set_from_dict(self, ntree, params):
        print("Unimplemented: %s" % self.__class__.__name__)
        print("Plugin types: %s" % self.plugin_types)

    def default_values(self, context):
        pass

    def update_visibility(self, context):
        pass

    def init(self, context):
        for socket in self.custom_outputs:
            self.outputs.new(socket['type'], socket['name'])

        for socket in self.custom_inputs:
            self.inputs.new(socket['type'], socket['name'])

        self.default_values(context)
        self.update_visibility(context)

    def get_input_socket(self, name):
        for input_socket in self.inputs:
            if input_socket.name == name:
                return input_socket

        return None


## For storing of registered socket types
class MitsubaSocketTypes:
    socket_types = {}

    @staticmethod
    def register(st):
        MitsubaAddon.addon_register_class(st)
        MitsubaSocketTypes.socket_types[st.bl_idname] = st
        return st

    @staticmethod
    def get(socket_type):
        return MitsubaSocketTypes.socket_types.get(socket_type, None)

    @staticmethod
    def items():
        return MitsubaSocketTypes.socket_types
