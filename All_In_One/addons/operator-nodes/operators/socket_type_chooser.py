import bpy
from bpy.props import *
from .. sockets import get_data_flow_socket_classes
from .. callback import execute_callback

class ChooseSocketTypeOperator(bpy.types.Operator):
    bl_idname = "en.choose_socket_type"
    bl_label = "Choose Socket Type"
    bl_property = "selected_data_type"

    def get_items(self, context):
        items = []
        for cls in get_data_flow_socket_classes():
            items.append((cls.bl_idname, cls.data_type, ""))
        return items

    selected_data_type: EnumProperty(items = get_items)
    callback: StringProperty()

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"CANCELLED"}

    def execute(self, context):
        execute_callback(self.callback, self.selected_data_type)
        return {"FINISHED"}