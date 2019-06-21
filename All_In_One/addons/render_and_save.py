#addon in development DONT USE IT, just for learning proposes
bl_info = {
    "name": "Render and Save",
    "category": "Learnbgame",
}

import bpy

#bpy.ops.wm.context_set_enum(data_path="area.type", value="IMAGE_EDITOR")
#bpy.ops.render.view_show("INVOKE_SCREEN")
#bpy.ops.render.render()

class RenderAndSave(bpy.types.Operator):
    """Render image and save it"""
    bl_idname = "render.save"
    bl_label = "Render an image and save it"
    bl_options = {'REGISTER',}
    
    def execute(self, context):
        rd = bpy.ops.render
        rd.view_show("INVOKE_SCREEN")
        rd.render()
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(RenderAndSave)
    
def unregister():
    bpy.utils.unregister_class(RenderAndSave)
    
if __name__ == "__main__":
    register()