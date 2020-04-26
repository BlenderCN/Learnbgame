import bpy

#change cam slot
class VCacheChangeCam(bpy.types.Operator):
    bl_idname = "vcache.change_cam"
    bl_label = ""
    bl_description = "Change Scene Cache Camera"
    bl_options = {'REGISTER', 'UNDO'}
    
    cam = bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, context):
        scn=bpy.context.scene
        chk=0
        for ob in scn.objects:
            if ob.type=='CAMERA':
                chk=1
        return chk==1
    
    def execute(self, context):
        scn=bpy.context.scene
        scn.vcache_camera=self.cam
        self.report({'INFO'}, "Scene Camera : "+self.cam)
        return {'FINISHED'}