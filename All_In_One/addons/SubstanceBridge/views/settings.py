import bpy

# Import all variable setup
from ..models.paths import SbsModelsSetup


# -----------------------------------------------------------------------------
# Settings for this addons
# -----------------------------------------------------------------------------
class SubstanceSettings(bpy.types.AddonPreferences):
    bl_idname = "SubstanceBridge"

    # All software path.
    path_painter = SbsModelsSetup.path_painter

    def draw(self, context):
        layout = self.layout
        layout.label(text="Substance Path.")

        row = layout.row(align=False)
        row.prop(self, "path_painter")
        # row.operator("substance.check", text="Check").path = self.path_painter
        # layout.prop(self, "path_batchtools")
        # layout.prop(self, "path_designer")


def register():
    bpy.utils.register_class(SubstanceSettings)


def unregister():
    bpy.utils.unregister_class(SubstanceSettings)
