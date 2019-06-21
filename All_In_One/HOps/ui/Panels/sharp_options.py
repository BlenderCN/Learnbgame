import bpy
from bpy.types import Panel

from ... preferences import get_preferences


class HOPS_PT_sharp_options(Panel):
    bl_label = 'Sharp Options'
    bl_space_type = 'VIEW_3D'
    bl_category = 'HardOps'
    bl_region_type = 'UI'


    def draw(self, context):
        layout = self.layout
        preference = get_preferences()

        column = layout.column(align=True)

        row = column.row(align=True)
        row.prop(preference, 'sharp_use_crease', text='Apply crease')
        row.prop(preference, 'sharp_use_bweight', text='Apply bweight')

        row = column.row(align=True)
        row.prop(preference, 'sharp_use_seam', text='Apply seam')
        row.prop(preference, 'sharp_use_sharp', text='Apply sharp')

        column.separator()

        row = column.row(align=True)
        # XXX: set sharpness ot should be fed a param rather then being 3 ot's
        row.operator('hops.set_sharpness_30', text='30')
        row.operator('hops.set_sharpness_45', text='45')
        row.operator('hops.set_sharpness_60', text='60')

        column.prop(preference, 'sharpness', text='Sharpness')
