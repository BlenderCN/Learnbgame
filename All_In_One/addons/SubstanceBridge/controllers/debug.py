import bpy


# -----------------------------------------------------------------------------
# Function Debug, show many proporties
# -----------------------------------------------------------------------------
class DebugShow(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "debug.sbs_data"
    bl_label = "A function to show many substance data debug"

    def execute(self, context):
        scn = context.scene

        # Substance Variable
        sbs_name = scn.sbs_project_settings.prj_name
        sbs_path_spp = scn.sbs_project_settings.path_spp
        sbs_meshs_name = scn.sbs_project_settings.meshs_name

        print("Substance Project : ", sbs_name)
        print("Link spp file : ", sbs_path_spp)
        for obj in bpy.data.objects:
            if obj.get('substance_project') is not None:
                print("List mesh : ", obj.name)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(DebugShow)


def unregister():
    bpy.utils.unregister_class(DebugShow)
