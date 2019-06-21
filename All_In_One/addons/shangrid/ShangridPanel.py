'''
Created on 2016/10/22

@author: take
'''
import bpy
import shangrid.ShangridOp

class ShangridToolPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

class ShangridControlPanel(ShangridToolPanel,bpy.types.Panel):
    bl_idname="DATA_PT_shangrid_control"
    bl_label = "Shangrid"
    bl_category = "Shangrid"

    def __init__(self):
        pass

    @classmethod
    def poll(cls, context):
#         obj = context.object
#         return (obj and obj.type in {'MESH'})
        return True

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "shangrid_selected_only")
        layout.operator("system.shangrid_start")
        layout.operator("system.shangrid_update_selected")
#         layout.operator("system.shangrid_stop")
        layout.separator()