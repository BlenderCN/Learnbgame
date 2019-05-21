import bpy
from bpy.props import *
from llvmlite import ir
from ctypes import c_float, c_void_p, c_size_t

from . base_socket import BaseSocket


class ObjectSocket(bpy.types.NodeSocket, BaseSocket):
    bl_idname = "cn_ObjectSocket"
    ir_type = ir.LiteralStructType([
                    ir.ArrayType(ir.IntType(8), 464),
                    ir.ArrayType(ir.FloatType(), 3),    # location
                    ir.ArrayType(ir.IntType(8), 24),
                    ir.ArrayType(ir.FloatType(), 3)     # scale
                ]).as_pointer()
    c_type = c_void_p

    value = PointerProperty(name = "Value", type = bpy.types.Object)

    def draw_property(self, layout, text, node):
        layout.prop_search(self, "value", bpy.context.scene, "objects", text = text)

    def draw_color(self, context, node):
        return (0.0, 0.0, 0.0, 1)

    def update_at_address(self, address):
        pointer = 0 if self.value is None else self.value.as_pointer()
        c_size_t.from_address(address).value = pointer

    def value_from_cvalue(self, cvalue):
        if cvalue.value is None:
            return None

        for object in bpy.data.objects:
            if object.as_pointer() == cvalue.value:
                return object

        raise Exception("cannot find object")
