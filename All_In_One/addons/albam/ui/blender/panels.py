import bpy

from albam.registry import albam_registry

@albam_registry.blender_panel()
class ALBAM_PT_ImportExportPanel(bpy.types.Panel):
    bl_label = "Albam"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Albam"

    def draw(self, context):  # pragma: no cover
        scn = context.scene
        layout = self.layout
        layout.operator('albam_import.item', text='Import')
        layout.operator('albam_export.item', text='Export')
