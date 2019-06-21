import bpy


# -----------------------------------------------------------------------------
# Show many options
# -----------------------------------------------------------------------------
class MoreOptPanel(bpy.types.Panel):
    bl_label = "Options"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Substances"

    def draw(self, context):
        layout = self.layout

        icon = 'PREFERENCES'
        name = "Show Settings"
        layout.operator("sbs.settings", name, icon=icon)


def register():
    bpy.utils.register_class(MoreOptPanel)


def unregister():
    bpy.utils.unregister_class(MoreOptPanel)