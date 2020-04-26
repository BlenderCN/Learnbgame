import bpy
from llvmlite import ir
from . compute_node import ComputeNode

class ObjectTransformsNode(bpy.types.Node, ComputeNode):
    bl_idname = "cn_ObjectTransformsNode"
    bl_label = "Object Transforms"

    def init(self, context):
        self.inputs.new("cn_ObjectSocket", "Object", "object")
        self.outputs.new("cn_VectorSocket", "Location", "location")
        self.outputs.new("cn_VectorSocket", "Scale", "scale")

    def create_llvm_ir(self, builder, object_p):
        vector_type = ir.ArrayType(ir.FloatType(), 3)
        pointer_value = builder.ptrtoint(object_p, ir.IntType(64))
        zero = ir.IntType(64)(0)
        is_not_zero = builder.icmp_unsigned("!=", pointer_value, zero)
        with builder.if_else(is_not_zero) as (then, otherwise):
            with then:
                then_block = builder.block
                object = builder.load(object_p)
                _location = builder.extract_value(object, 1)
                _scale = builder.extract_value(object, 3)
            with otherwise:
                else_block = builder.block
                _default_location = vector_type([0, 0, 0])
                _default_scale = vector_type([1, 1, 1])

        location = builder.phi(vector_type)
        location.add_incoming(_location, then_block)
        location.add_incoming(_default_location, else_block)

        scale = builder.phi(vector_type)
        scale.add_incoming(_scale, then_block)
        scale.add_incoming(_default_scale, else_block)

        return builder, location, scale
