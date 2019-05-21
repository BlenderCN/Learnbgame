import bpy
from bpy.props import *
from .. base_socket_types import ExternalDataFlowSocket
from .. dependencies import AttributeDependency

class ObjectSocket(ExternalDataFlowSocket, bpy.types.NodeSocket):
    bl_idname = "en_ObjectSocket"
    data_type = "Object"
    color = (0, 0, 0, 1)

    value: PointerProperty(type = bpy.types.Object,
        update = ExternalDataFlowSocket.external_data_changed)

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