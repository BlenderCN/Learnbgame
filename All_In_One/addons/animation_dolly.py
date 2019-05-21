bl_info = {
    'name': 'Dolly Camera Rig Controls',
    'author': 'Wayne Dixon  ',
    'version': (1,0),
    'blender': (2, 5, 9),
    'api': 39307,
    'location': 'View3D > Properties > 3 control panels',
    'warning': '',
    'description': 'Tools for controlling Dolly Camera Rig',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Animation'}



import bpy

class CameraRigSettings(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Camera Settings"


    @classmethod
    def poll(self, context):
        try:
           ob = context.active_object
           return (ob.name == "Camera_Dolly_Rig")
        except AttributeError:
           return 0

    def draw(self, context):
        layout = self.layout 
        arm = context.active_object.data
        pose_bones = context.active_object.pose.bones
        
        box = layout.box()
        col = box.column()
        row = col.row()
        
    # Camera Properties   

        cam = bpy.data.cameras['Camera_dolly']
        row.label("Camera Setup", 'SCRIPTWIN')
        col.label(text="Clipping:")
        col.prop(cam, "clip_start", text="Start")
        col.prop(cam, "clip_end", text="End")
        col.prop(cam, "type")
        
        col.prop(cam, "dof_object")
        col.prop(cam, "dof_distance")
        col.prop(cam, "show_limits")
        col.prop(cam, "show_title_safe")
        col.prop(cam, "show_passepartout")
        col.prop(cam, "passepartout_alpha")


class CameraLocation(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Camera location"       
    
    @classmethod
    def poll(self, context):
        try:
           ob = context.active_object
           return (ob.name == "Camera_Dolly_Rig")
        except AttributeError:
           return 0

    def draw(self, context):
        layout = self.layout 
        arm = context.active_object.data
        pose_bones = context.active_object.pose.bones
        
        box = layout.box()
        col = box.column()
        row = col.row() 
        #########################
        #New Section
        
        #Camera Location
        row.label("Camera Controls", 'CAMERA_DATA')
        col.label(text="Camera Location:")
        col.prop(pose_bones["Camera_CTRL"],'location', index=0,text="Loc X")
        col.prop(pose_bones["Camera_CTRL"],'location', index=1,text="Loc Y")
        col.prop(pose_bones["Camera_CTRL"],'location', index=2,text="Loc Z")
    
        #Camera Rotation
        col.label(text="Camera Rotation:")
        col.prop(pose_bones["Camera_CTRL"],'rotation_euler', index=0,text="Rot X")
        col.prop(pose_bones["Camera_CTRL"],'rotation_euler', index=1,text="Rot Y")
        col.prop(pose_bones["Camera_CTRL"],'rotation_euler', index=2,text="Rot Z")
        
        # Track to
        col.label(text="Tracking:")
        col.prop(pose_bones["Camera_CTRL"], '["track"]', text="Track to", slider=True)


class AimLocation(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Camera Aim"          
    
    @classmethod
    def poll(self, context):
        try:
           ob = context.active_object
           return (ob.name == "Camera_Dolly_Rig")
        except AttributeError:
           return 0

    def draw(self, context):
        layout = self.layout 
        arm = context.active_object.data
        pose_bones = context.active_object.pose.bones
        
        box = layout.box()
        col = box.column()
        row = col.row() 
        
        cam = bpy.data.cameras['Camera_dolly']
        #############
        #New Section
        
        #Camera Lens
        row.label("Camera Aim", 'CURSOR')
        col.label(text="Focal Length:")
        col.prop(cam, "lens", text="Angle")
        #Aim Location
        col.label(text="Aim Location:")
        col.prop(pose_bones["Camera_AIM"],'location', index=0,text="Loc X")
        col.prop(pose_bones["Camera_AIM"],'location', index=1,text="Loc Y")
        col.prop(pose_bones["Camera_AIM"],'location', index=2,text="Loc Z")
    
        #Aim Rotation
        col.label(text="Aim Rotation:")
        col.prop(pose_bones["Camera_AIM"],'rotation_euler', index=0,text="Rot X")
        col.prop(pose_bones["Camera_AIM"],'rotation_euler', index=1,text="Rot Y")
        col.prop(pose_bones["Camera_AIM"],'rotation_euler', index=2,text="Rot Z")
    
def register():
    bpy.utils.register_class(CameraRigSettings)
    bpy.utils.register_class(CameraLocation)
    bpy.utils.register_class(AimLocation)
    
    
def unregister():
    bpy.utils.unregister_class(CameraRigSettings)
    bpy.utils.unregister_class(CameraLocation)
    bpy.utils.unregister_class(AimLocation)

if __name__ == "__main__":
    register()
        
        

