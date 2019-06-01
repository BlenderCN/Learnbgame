import bpy
from bpy.props import *
from llvmlite import ir
from ctypes import c_float

from . base_socket import BaseSocket

class FloatSocket(bpy.types.NodeSocket, BaseSocket):
    bl_idname = "cn_FloatSocket"
    ir_type = ir.FloatType()
    c_type = c_float

    value = FloatProperty(name = "Value")

    def draw_property(self, layout, text, node):
        layout.prop(self, "value", text = text)

    def draw_color(self, context, node):
        return (0.4, 0.4, 0.7, 1)

    def update_at_address(self, address):
        c_float.from_address(address).value = self.value

    def value_from_cvalue(self, cvalue):
        return cvalue.value
