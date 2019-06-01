import bpy
from bpy.props import *
from .. base_socket_types import InternalDataFlowSocket
from .. dependencies import AttributeDependency

class ColorSocket(InternalDataFlowSocket, bpy.types.NodeSocket):
    bl_idname = "en_ColorSocket"
    data_type = "Color"
    color = (0, 0, 0, 1)

    value: FloatVectorProperty(name = "Value", default = [0.0, 0.0, 0.0],
        subtype = "COLOR", soft_min = 0.0, soft_max = 1.0,
        update = InternalDataFlowSocket.internal_data_changed)

    def draw_property(self, layout, text, node):
        layout.column(align = True).prop(self, "value", text = text)

    def get_value(self):
        return self.value.copy()

    def get_property(self):
        return self.value.copy()

    def set_property(self, value):
        self.value = value

    def get_dependencies(self):
        yield AttributeDependency(self, "value")