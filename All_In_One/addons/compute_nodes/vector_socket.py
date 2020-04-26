import bpy
from bpy.props import *
from llvmlite import ir
from mathutils import Vector
from ctypes import Structure, c_float

from . base_socket import BaseSocket

class VectorSocket(bpy.types.NodeSocket, BaseSocket):
    bl_idname = "cn_VectorSocket"
    ir_type = ir.ArrayType(ir.FloatType(), 3)
    c_type = c_float * 3

    value = FloatVectorProperty(name = "Value", size = 3, subtype = "XYZ")

    def draw_property(self, layout, text, node):
        col = layout.column(align = True)
        col.label(text)
        col.prop(self, "value", text = "")

    def draw_color(self, context, node):
        return (0.2, 0.2, 0.8, 1)

    def update_at_address(self, address):
        c_float.from_address(address + 0).value = self.value.x
        c_float.from_address(address + 4).value = self.value.y
        c_float.from_address(address + 8).value = self.value.z

    def value_from_cvalue(self, cvalue):
        return Vector((cvalue[0], cvalue[1], cvalue[2]))
