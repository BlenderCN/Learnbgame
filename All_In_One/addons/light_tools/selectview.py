import bpy


class ResetCamera(bpy.types.Operator):
    bl_idname = 'reset.camera_as_active'
    bl_label = "Reset Camera"

    bpy.data.scenes["Scene"].camera = bpy.data.objects["Camera"]
