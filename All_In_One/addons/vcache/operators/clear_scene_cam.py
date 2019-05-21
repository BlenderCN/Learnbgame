import bpy

#clear scene cam
class VCacheChangeCam(bpy.types.Operator):
    bl_idname = "vcache.clear_cam"
    bl_label = ""
    bl_description = "Clear Scene Cache Camera"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return bpy.context.scene.vcache_camera!=''
    
    def execute(self, context):
        scn=bpy.context.scene
        scn.vcache_camera=''
        self.report({'INFO'}, "Scene Camera cleared ")
        return {'FINISHED'}