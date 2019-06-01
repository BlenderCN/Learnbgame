#    This file is part of Korman.
#
#    Korman is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Korman is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Korman.  If not, see <http://www.gnu.org/licenses/>.

import abc
import bpy
from bpy.props import *
from collections import OrderedDict

from .node_core import *

class PlasmaDeprecatedNode(PlasmaNodeBase):
    @abc.abstractmethod
    def upgrade(self):
        raise NotImplementedError()


class PlasmaVersionedNode(PlasmaNodeBase):
    def init(self, context):
        self.version = self.latest_version

    @property
    @abc.abstractmethod
    def latest_version(self):
        raise NotImplementedError()

    @classmethod
    def register(cls):
        cls.version = IntProperty(name="Node Version", default=1, options=set())

    @abc.abstractmethod
    def upgrade(self):
        raise NotImplementedError()


class PlasmaRespCommandSocket(PlasmaNodeSocketBase, bpy.types.NodeSocket):
    bl_color = (0.451, 0.0, 0.263, 1.0)


class PlasmaResponderCommandNode(PlasmaDeprecatedNode, bpy.types.Node):
    bl_category = "LOGIC"
    bl_idname = "PlasmaResponderCommandNode"
    bl_label = "Responder Command"

    input_sockets = OrderedDict([
        ("whodoneit", {
            "text": "Condition",
            "type": "PlasmaRespCommandSocket",
        }),
    ])

    output_sockets = OrderedDict([
        ("msg", {
            "link_limit": 1,
            "text": "Message",
            "type": "PlasmaMessageSocket",
        }),
        ("trigger", {
            "text": "Trigger",
            "type": "PlasmaRespCommandSocket",
        }),
        ("reenable", {
            "text": "Local Reenable",
            "type": "PlasmaEnableMessageSocket",
        }),
    ])

    def _find_message_sender_node(self, parentCmdNode=None):
        if parentCmdNode is None:
            parentCmdNode = self
        else:
            if self == parentCmdNode:
                self._whine("responder tree is circular")
                return None

        if parentCmdNode.bl_idname == "PlasmaResponderStateNode":
            return parentCmdNode
        elif parentCmdNode.bl_idname == "PlasmaResponderCommandNode":
            # potentially a responder wait command... let's see if the message can wait
            if parentCmdNode != self:
                cmdMsgNode = parentCmdNode.find_output("msg")
                if cmdMsgNode is not None and cmdMsgNode.has_callbacks:
                    return cmdMsgNode

            # can't wait on this command/message, so go up the tree...
            grandParentCmdNode = parentCmdNode.find_input("whodoneit")
            if grandParentCmdNode is None:
                self._whine("orphaned responder command")
                return None
            return self._find_message_sender_node(grandParentCmdNode)
        else:
            self._whine("unexpected command node type '{}'", parentCmdNode.bl_idname)
            return None


    def upgrade(self):
        senderNode = self._find_message_sender_node()
        if senderNode is None:
            return

        msgNode = self.find_output("msg")
        if msgNode is not None:
            senderNode.link_output(msgNode, "msgs", "sender")
        else:
            self._whine("command node does not send a message?")

        if self.find_output("reenable") is not None:
            tree = self.id_data
            enableMsgNode = tree.nodes.new("PlasmaEnableMsgNode")
            enableMsgNode.cmd = "kEnable"
            if msgNode.has_callbacks:
                msgNode.link_output(enableMsgNode, "msgs", "sender")
            else:
                senderNode.link_output(enableMsgNode, "msgs", "sender")

            fromSocket = enableMsgNode.find_output_socket("receivers")
            for link in self.find_output_socket("reenable").links:
                if not link.is_valid:
                    continue
                tree.links.new(link.to_socket, fromSocket)

@bpy.app.handlers.persistent
def _upgrade_node_trees(dummy):
    for tree in bpy.data.node_groups:
        if tree.bl_idname != "PlasmaNodeTree":
            continue

        # ensure node sockets match what we expect
        for node in tree.nodes:
            node.update()
        nuke = []
        # upgrade to new node types/linkages
        for node in tree.nodes:
            if isinstance(node, PlasmaDeprecatedNode):
                node.upgrade()
                nuke.append(node)
            elif isinstance(node, PlasmaVersionedNode):
                node.upgrade()
        # toss deprecated nodes
        for node in nuke:
            tree.nodes.remove(node)
bpy.app.handlers.load_post.append(_upgrade_node_trees)
