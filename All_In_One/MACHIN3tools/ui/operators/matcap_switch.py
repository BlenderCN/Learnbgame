import bpy
from ... utils.registration import get_prefs
from ... utils import MACHIN3 as m3


class MatcapSwitch(bpy.types.Operator):
    bl_idname = "machin3.matcap_switch"
    bl_label = "Matcap Switch"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        shading = context.space_data.shading
        return shading.type == "SOLID" and shading.light == "MATCAP"

    def execute(self, context):
        shading = context.space_data.shading
        matcap1 = get_prefs().switchmatcap1
        matcap2 = get_prefs().switchmatcap2

        if matcap1 and matcap2 and "NOT FOUND" not in [matcap1, matcap2]:
            if shading.studio_light == matcap1:
                shading.studio_light = matcap2

            elif shading.studio_light == matcap2:
                shading.studio_light = matcap1

            else:
                shading.studio_light = matcap1

        return {'FINISHED'}
