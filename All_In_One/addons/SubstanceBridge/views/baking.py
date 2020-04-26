import bpy


# -----------------------------------------------------------------------------
# Baking panel
# -----------------------------------------------------------------------------
class BakingSubstancePanel(bpy.types.Panel):
    bl_label = "Baking"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Substances"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout

        name = "Baking map"
        layout.operator("substance.painter_export", name).project = False


def register():
    bpy.utils.register_class(BakingSubstancePanel)


def unregister():
    bpy.utils.unregister_class(BakingSubstancePanel)
