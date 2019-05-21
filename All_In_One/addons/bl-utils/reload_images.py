import bpy


bl_info = {
    'name': "Reload Images",
    'description': "Reload all loaded images",
    'author': "miniukof",
    'version': (0, 0, 1),
    'blender': (2, 77, 0),
    'category': "System",
}


class ReloadImages(bpy.types.Operator):
    bl_description = "Reload all loaded images"
    bl_idname = "system.reload_images"
    bl_label = "Reload All Images"
    bl_options = {"REGISTER"}

    def execute(self, context):
        for img in bpy.data.images:
            img.reload()
        return{'FINISHED'}


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
