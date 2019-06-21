'''
Created on 2016/10/23

@author: take
'''

import bpy
import shangrid.ShangridCore

class ShangridStartOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "system.shangrid_start"
    bl_label = "Start Shangrid"

    def execute(self, context):
        obj=context.active_object
        if obj.type!='MESH':
            return{'FINISHED'}
#         context.scene.shangrid.start(obj)
        selectedOnly=False
        if context.mode=='EDIT_MESH':
            selectedOnly=context.scene.shangrid_selected_only
        bpy.Shangrid.start(obj,selectedOnly)
        return {'FINISHED'}


class ShangridUpdateSelectedOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "system.shangrid_update_selected"
    bl_label = "Update Selected"

    def execute(self, context):
        obj=context.active_object
        if obj.type!='MESH':
            return{'FINISHED'}
#         context.scene.shangrid.start(obj)
        selectedOnly=False
        if context.mode=='EDIT_MESH':
            selectedOnly=context.scene.shangrid_selected_only
        bpy.Shangrid.updateSelected(obj,selectedOnly)
        return {'FINISHED'}

class ShangridStopOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "system.shangrid_stop"
    bl_label = "Stop Shangrid"

    def execute(self, context):
        bpy.Shangrid.stop()
#         context.scene.shangrid.stop()
        return {'FINISHED'}