import bpy
from llvmlite import ir
from . compute_node import ComputeNode

class SeparateVectorNode(bpy.types.Node, ComputeNode):
    bl_idname = "cn_SeparateVectorNode"
    bl_label = "Separate Vector"

    def init(self, context):
        self.inputs.new("cn_VectorSocket", "Vector", "vector")
        self.outputs.new("cn_FloatSocket", "X", "x")
        self.outputs.new("cn_FloatSocket", "Y", "y")
        self.outputs.new("cn_FloatSocket", "Z", "z")

    def create_llvm_ir(self, builder, vector):
        x = builder.extract_value(vector, 0)
        y = builder.extract_value(vector, 1)
        z = builder.extract_value(vector, 2)
        return builder, x, y, z
