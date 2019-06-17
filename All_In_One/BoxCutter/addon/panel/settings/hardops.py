import bpy

from bpy.types import Panel


class BC_PT_hardops_settings(Panel):
    bl_label = 'HardOps'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BoxCutter'
    bl_parent_id = 'BC_PT_settings'
    bl_options = {'DEFAULT_CLOSED'}


    @classmethod
    def poll(cls, context):
        hops = hasattr(context.window_manager, 'Hard_Ops_material_options')
        return hops and context.region.type == 'UI'


    def draw(self, context):
        layout = self.layout

        wm = context.window_manager
        hops = wm.Hard_Ops_material_options if hasattr(wm, 'Hard_Ops_material_options') else False
        if hops:
            layout.separator()
            layout.label(text='HOps Slice Material')

            row = layout.row()
            row.prop_search(hops, 'active_material', bpy.data, 'materials', text='')
