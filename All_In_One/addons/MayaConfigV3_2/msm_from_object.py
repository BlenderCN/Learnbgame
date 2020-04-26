bl_info = {
    "name": "msm_from_object",
    "author": "Way2Close",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "description": "Switches to object mode and changes mesh select mode",
    "category": "3D View"}

import bpy


class MsmFromObject(bpy.types.Operator):
    """Switches to object mode and changes mesh select mode"""
    bl_idname = "object.msm_from_object"
    bl_label = "msm_from_object"
    bl_options = {'REGISTER', 'UNDO'}

    mode : bpy.props.StringProperty(
        name = "mode",
        default = "vert"
    )
        
    def execute(self, context):    
        # msm_from_object

        if len(bpy.context.selected_objects) < 1:
            self.report({'WARNING'}, 'No object selected')
            return {'FINISHED'}

        if bpy.context.object.mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        if self.mode == 'vert':
            bpy.context.tool_settings.mesh_select_mode = (True, False, False)
        elif self.mode == 'edge':
            bpy.context.tool_settings.mesh_select_mode = (False, True, False)
        elif self.mode == 'face':
            bpy.context.tool_settings.mesh_select_mode = (False, False, True)

        return {'FINISHED'}
    
    
classes = (
    MsmFromObject,
)

register, unregister = bpy.utils.register_classes_factory(classes)
    

if __name__ == "__main__":
    register()
