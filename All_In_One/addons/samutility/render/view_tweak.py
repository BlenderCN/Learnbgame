"""
Operator to tweak viewport quicker
"""

import bpy


##Only render
#Alt+Shift+Z toggle Only Render

class SAMT_VIEW3D_OT_show_only_render(bpy.types.Operator):
    bl_idname = "samutils.show_only_render"
    bl_label = "Show Only Render"

    def execute(self, context):

        space = bpy.context.space_data
        space.show_only_render = not space.show_only_render

        return {"FINISHED"}




#Alt+Shift+C toggle Lock Cam to view

class SAMT_VIEW3D_OT_lock_camera_to_view(bpy.types.Operator):
    bl_idname = "samutils.lock_cam_to_view"
    bl_label = "Lock camera to view"

    def execute(self, context):

        #TODO (only if in view is in cam else, detect view)
        space = bpy.context.space_data
        space.lock_camera = not space.lock_camera

        return {"FINISHED"}

#Ctrl+Alt+Shift+Z (all classic modifiers) go material

class SAMT_VIEW3D_OT_material_mode(bpy.types.Operator):
    bl_idname = "samutils.material_mode"
    bl_label = "Go To material mode"

    def execute(self, context):

        space = bpy.context.space_data
        if space.viewport_shade == 'MATERIAL':
            space.viewport_shade = 'SOLID'
        else:
            space.viewport_shade = 'MATERIAL'

        return {"FINISHED"}
