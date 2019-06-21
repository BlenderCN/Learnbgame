import bpy
from bpy.props import EnumProperty
from .. extend_bpy_types import status_items
from .. utils.blender_ui import get_dpi_factor


class HOPS_OT_StatusHelperPopup(bpy.types.Operator):
    """
    Changes to SStatus of selected object.
    Used for workflow realignment.
    """
    bl_idname = "view3d.status_helper_popup"
    bl_label = "Status Override"

    status: EnumProperty(name="Status",
                         options={"SKIP_SAVE"}, items=status_items)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        self.status = context.active_object.hops.status
        return context.window_manager.invoke_props_dialog(self, width=300 * get_dpi_factor(force=False))

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "status", text="test", expand=True)

    def check(self, context):
        return True

    def execute(self, context):
        context.active_object.hops.status = self.status
        return {'FINISHED'}
