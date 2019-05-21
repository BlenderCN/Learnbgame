import bpy
from . node_base import NodeBase

class InputNode(bpy.types.Node, NodeBase):
    bl_idname = "cn_InputNode"
    bl_label = "Input Node"

    def init(self, context):
        self.outputs.new("cn_FloatSocket", "Input 1", "in1")
        self.outputs.new("cn_FloatSocket", "Input 2", "in2")
