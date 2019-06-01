import bpy
from bpy.props import *
from .. base_socket_types import InternalDataFlowSocket
from .. dependencies import AttributeDependency

class BooleanSocket(InternalDataFlowSocket, bpy.types.NodeSocket):
    bl_idname = "en_BooleanSocket"
    data_type = "Boolean"
    color = (0, 0, 0, 1)

    value: BoolProperty(name = "Value", default = 0.0,
        update = InternalDataFlowSocket.internal_data_changed)

    def draw_property(self, layout, text, node):
        layout.prop(self, "value", text = text)

    def get_value(self):
        return self.value

    def get_property(self):
        return self.value

    def set_property(self, value):
        self.value = value

    def get_dependencies(self):
        yield AttributeDependency(self, "value")