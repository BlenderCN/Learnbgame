import bpy
from .. utils.operators import get_selection


# To make this really awesome, you need to scale the decals according to the target decal
# also, projected decals need to be unprojected and reprojected

class DecalReplace(bpy.types.Operator):
    bl_idname = "machin3.decal_replace"
    bl_label = "MACHIN3: Decal Replace"

    def execute(self, context):

        sel = get_selection()
        if sel is not None:
            target, decals = sel
            decal_replace(target, decals)
        else:
            self.report({'ERROR'}, "Select two or more decals: the decal(s) to be replaced and the decal to replace them with!")

        return {'FINISHED'}


def decal_replace(target, decals):
    targetmat = target.material_slots[0].material
    for decal in decals:
        decal.material_slots[0].material = targetmat

        # we are also changing the obj name to make sure export or other things depended on decal name keep working as expected
        decal.name = target.name
