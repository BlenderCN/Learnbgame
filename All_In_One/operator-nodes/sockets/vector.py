import bpy
from bpy.props import *
from .. base_socket_types import InternalDataFlowSocket
from .. dependencies import AttributeDependency

class VectorSocket(InternalDataFlowSocket, bpy.types.NodeSocket):
    bl_idname = "en_VectorSocket"
    data_type = "Vector"
    color = (0, 0, 0, 1)

    value: FloatVectorProperty(name = "Value", default = [0.0, 0.0, 0.0], subtype = "XYZ",
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