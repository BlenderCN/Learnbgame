import bpy
import logging


logging.getLogger(__name__)


class ActionManPanel(bpy.types.Panel):
    bl_category = "Action Man"
    bl_label = "Action Man"
    bl_idname = "FR_PT_panel"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        """Make sure there's an active action."""
        return context.object.animation_data.action is not None

    def draw(self, context):
        action = context.object.animation_data.action

        layout = self.layout

        row = layout.row()
        row.prop(action, "face_action")

        if not action.face_action:
            return

        row = layout.row()
        row.operator("action.clean")

        row = layout.row()
        row.separator()

        row = layout.row()
        row.prop_search(action, "target", bpy.data, "objects")
        target = bpy.data.armatures.get(action.target)
        if target is not None:
            if type(target) == bpy.types.Armature:
                row = layout.row()
                row.prop_search(action, "subtarget", target, "bones", text='Bone')

        row = layout.row()
        row.prop(action, "transform_channel")

        row = layout.row()
        row.label(text="Activation Range:")

        split = layout.split()
        col = split.column(align=True)
        col.prop(action, "activation_start", text="Start")
        col.prop(action, "activation_end", text="End")

        row = layout.row()
        row.separator()

        row = layout.row()
        row.operator("action.create_constraint", text="Create/Update Constraints")

        row = layout.row()
        row.operator("action.delete_useles_constraints")
