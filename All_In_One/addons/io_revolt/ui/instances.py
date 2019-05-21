import bpy
from ..common import *

class RevoltInstancesPanel(bpy.types.Panel):
    bl_label = "Instances"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Re-Volt"
    bl_options = {"DEFAULT_CLOSED"}

    # @classmethod
    # def poll(self, context):
    #     return context.object and len(context.selected_objects) >= 1 and context.object.type == "MESH"

    def draw_header(self, context):
        self.layout.label("", icon="OUTLINER_OB_GROUP_INSTANCE")

    def draw(self, context):
        view = context.space_data
        obj = context.object
        props = context.scene.revolt
        layout = self.layout

        layout.label("Instances: {}/1024".format(len([obj for obj in context.scene.objects if obj.revolt.is_instance])))
        layout.operator("helpers.select_by_data")
        col = layout.column(align=True)
        col.prop(props, "rename_all_name", text="")
        col.operator("helpers.rename_all_objects")
        col.operator("helpers.select_by_name")

        col = layout.column(align=True)
        col.operator("helpers.set_instance_property")
        col.operator("helpers.rem_instance_property")