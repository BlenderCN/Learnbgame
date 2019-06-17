import bpy
from ... utils.material import set_match_material_enum


class UpdateMatchMaterials(bpy.types.Operator):
    bl_idname = "machin3.update_match_materials"
    bl_label = "MACHIN3: Update Match Materials"
    bl_description = "Update list of Materials, that can be matched.\nRED: The currently selected material can not be matched anymore"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        set_match_material_enum()

        return {'FINISHED'}
