import bpy
from llvmlite import ir
from . compute_node import ComputeNode

class CombineVectorNode(bpy.types.Node, ComputeNode):
    bl_idname = "cn_CombineVectorNode"
    bl_label = "Combine Vector"

    def init(self, context):
        self.inputs.new("cn_FloatSocket", "X", "x")
        self.inputs.new("cn_FloatSocket", "Y", "y")
        self.inputs.new("cn_FloatSocket", "Z", "z")
        self.outputs.new("cn_VectorSocket", "Vector", "vector")

    def create_llvm_ir(self, builder, x, y, z):
        vector_p = builder.alloca(self.outputs[0].ir_type)
        vector = builder.load(vector_p)
        vector = builder.insert_value(vector, x, 0)
        vector = builder.insert_value(vector, y, 1)
        vector = builder.insert_value(vector, z, 2)
        return builder, vector
