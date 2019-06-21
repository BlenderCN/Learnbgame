import bpy
from bpy.props import (
    StringProperty,
    EnumProperty,
)

from .utils.addon_updater import AddonUpdatorManager
from .utils.bl_class_registry import BlClassRegistry
from .utils import compatibility as compat


@BlClassRegistry()
class BLMQO_OT_CheckAddonUpdate(bpy.types.Operator):
    bl_idname = "import_scene.blmqo_check_addon_update"
    bl_label = "Check Update"
    bl_description = "Check Add-on Update"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, _):
        updater = AddonUpdatorManager.get_instance()
        updater.check_update_candidate()

        return {'FINISHED'}


@BlClassRegistry()
@compat.make_annotations
class BLMQO_OT_UpdateAddon(bpy.types.Operator):
    bl_idname = "import_scene.blmqo_update_addon"
    bl_label = "Update"
    bl_description = "Update Add-on"
    bl_options = {'REGISTER', 'UNDO'}

    branch_name = StringProperty(
        name="Branch Name",
        description="Branch name to update",
        default="",
    )

    def execute(self, _):
        updater = AddonUpdatorManager.get_instance()
        updater.update(self.branch_name)

        return {'FINISHED'}


def get_update_candidate_branches(_, __):
    updater = AddonUpdatorManager.get_instance()
    if not updater.candidate_checked():
        return []

    return [(name, name, "") for name in updater.get_candidate_branch_names()]


@BlClassRegistry()
@compat.make_annotations
class BLMQO_Preferences(bpy.types.AddonPreferences):
    bl_idname = "blender_mqo"

    # for add-on updater
    updater_branch_to_update = EnumProperty(
        name="branch",
        description="Target branch to update add-on",
        items=get_update_candidate_branches
    )

    def draw(self, _):
        layout = self.layout

        updater = AddonUpdatorManager.get_instance()

        layout.separator()

        if not updater.candidate_checked():
            col = layout.column()
            col.scale_y = 2
            row = col.row()
            row.operator(BLMQO_OT_CheckAddonUpdate.bl_idname,
                         text="Check 'blender-mqo' add-on update",
                         icon='FILE_REFRESH')
        else:
            row = layout.row(align=True)
            row.scale_y = 2
            col = row.column()
            col.operator(BLMQO_OT_CheckAddonUpdate.bl_idname,
                         text="Check 'blender-mqo' add-on update",
                         icon='FILE_REFRESH')
            col = row.column()
            if updater.latest_version() != "":
                col.enabled = True
                ops = col.operator(
                    BLMQO_OT_UpdateAddon.bl_idname,
                    text="Update to the latest release version (version: {})"
                    .format(updater.latest_version()),
                    icon='TRIA_DOWN_BAR')
                ops.branch_name = updater.latest_version()
            else:
                col.enabled = False
                col.operator(BLMQO_OT_UpdateAddon.bl_idname,
                             text="No updates are available.")

            layout.separator()
            layout.label(text="Manual Update:")
            row = layout.row(align=True)
            row.prop(self, "updater_branch_to_update", text="Target")
            ops = row.operator(
                BLMQO_OT_UpdateAddon.bl_idname, text="Update",
                icon='TRIA_DOWN_BAR')
            ops.branch_name = self.updater_branch_to_update

            layout.separator()
            if updater.has_error():
                box = layout.box()
                box.label(text=updater.error(), icon='CANCEL')
            elif updater.has_info():
                box = layout.box()
                box.label(text=updater.info(), icon='ERROR')
