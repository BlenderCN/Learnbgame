import bpy
from . node_base import NodeBase

class OutputNode(bpy.types.Node, NodeBase):
    bl_idname = "cn_OutputNode"
    bl_label = "Output Node"

    def init(self, context):
        self.inputs.new("cn_FloatSocket", "Output 1", "out1")
        self.inputs.new("cn_VectorSocket", "Output 2", "out2")
        self.inputs.new("cn_ObjectSocket", "Output 3", "out3")
