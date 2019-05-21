import bpy

#get cam for cam slot
class VCacheGetActiveCam(bpy.types.Operator):
    bl_idname = "vcache.get_active_cam"
    bl_label = ""
    bl_description = "Assign Active Camera to Scene Cache"
    bl_options = {'REGISTER', 'UNDO'}
    
    cam = bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, context):
        try:
            if bpy.context.active_object.type=='CAMERA':
                chk=1
            else:
                chk=0
        except:
            chk=0
        return chk==1
    
    def execute(self, context):
        scn=bpy.context.scene
        
        scn.vcache_camera=bpy.context.active_object.name
        self.report({'INFO'}, "Scene Camera : "+bpy.context.active_object.name)
        return {'FINISHED'}