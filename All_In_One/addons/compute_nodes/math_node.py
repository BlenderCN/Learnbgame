import bpy
from bpy.props import *
from llvmlite import ir
from . compute_node import ComputeNode

operation_items = [
    ("ADD", "Add", "", "NONE", 0),
    ("SUBTRACT", "Subtract", "", "NONE", 1),
    ("MULTIPLY", "Multiply", "", "NONE", 2),
    ("DIVIDE", "Divide", "", "NONE", 3),
    ("SIN", "Sin", "", "NONE", 4)
]

class FloatMathNode(bpy.types.Node, ComputeNode):
    bl_idname = "cn_FloatMathNode"
    bl_label = "Float Math"

    def propChanged(self, context):
        self.id_data.update()

    operation = EnumProperty(name = "Operation", items = operation_items, update = propChanged)

    def init(self, context):
        self.inputs.new("cn_FloatSocket", "A", "a")
        self.inputs.new("cn_FloatSocket", "B", "b")
        self.outputs.new("cn_FloatSocket", "Result", "result")

    def draw(self, layout):
        layout.prop(self, "operation", text = "")

    def create_llvm_ir(self, builder, a, b):
        op = self.operation
        out_name = "result"

        zero = ir.Constant(ir.FloatType(), 0)
        if op == "ADD":
            result = builder.fadd(a, b, name = out_name)
        elif op == "SUBTRACT":
            result = builder.fsub(a, b, name = out_name)
        elif op == "MULTIPLY":
            result = builder.fmul(a, b, name = out_name)
        elif op == "DIVIDE":
            is_not_zero = builder.fcmp_ordered("!=", b, zero, name = "is_not_zero")
            with builder.if_else(is_not_zero) as (then, otherwise):
                with then:
                    then_block = builder.block
                    normal_result = builder.fdiv(a, b)
                with otherwise:
                    else_block = builder.block
                    zero_result = zero

            result = builder.phi(ir.FloatType(), name = out_name)
            result.add_incoming(normal_result, then_block)
            result.add_incoming(zero_result, else_block)
        elif op == "SIN":
            f_type = ir.FunctionType(ir.FloatType(), [ir.FloatType()])
            f = ir.Function(builder.module, f_type, "llvm.sin.f32")
            result = builder.call(f, [a], name = out_name)

        return builder, result
