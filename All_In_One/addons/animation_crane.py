bl_info = {
    'name': 'Crane Camera Rig Controls',
    'author': 'Wayne Dixon  ',
    'version': (1,0),
    'blender': (2, 5, 9),
    'api': 39307,
    'location': 'View3D > Properties > 3 control panels',
    'warning': '',
    'description': 'Tools for controlling Crane Camera Rig',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Animation'}

import bpy

class CameraCraneLocation(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Camera Location"

    @classmethod
    def poll(self, context):
        try:
           ob = context.active_object
           return (ob.name == "Camera_Crane_Rig")
        except AttributeError:
           return 0

    def draw(self, context):
        layout = self.layout 
        arm = context.active_object.data
        pose_bones = context.active_object.pose.bones

        box = layout.box()
        col = box.column()
        row = col.row()
        
        row.label("Crane Controls", 'CAMERA_DATA')
        #Crane arm stuff
        col.label(text="Crane Arm:")
        col.prop(pose_bones["pivot_height"], 'scale', index=1, text="Pivot Height")
        col.prop(pose_bones["crane_arm"], 'scale', index=1, text="Arm length")
        col.prop(pose_bones["crane_arm"],'rotation_euler', index=0,text="Rot X")
        col.prop(pose_bones["crane_arm"],'rotation_euler', index=2,text="Rot Z")

        #Camera Location
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

class CraneAimLocation(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Camera Aim"

    @classmethod
    def poll(self, context):
        try:
           ob = context.active_object
           return (ob.name == "Camera_Crane_Rig")
        except AttributeError:
           return 0

    def draw(self, context):
        layout = self.layout 
        arm = context.active_object.data
        pose_bones = context.active_object.pose.bones

        box = layout.box()
        col = box.column()
        row = col.row()
        
        row.label("Crane Aim", 'CURSOR')

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


class CameraCraneSetup(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Camera Settings"
    
    @classmethod
    def poll(self, context):
        try:
           ob = context.active_object
           return (ob.name == "Camera_Crane_Rig")
        except AttributeError:
           return 0

    def draw(self, context):
        layout = self.layout 
        arm = context.active_object.data
        pose_bones = context.active_object.pose.bones
        
        box = layout.box()
        col = box.column()
        row = col.row()
        
        row.label("Camera Setup", 'SCRIPTWIN')


        # Camera Properties
        cam = bpy.data.cameras['Camera_crane']
        col.label(text="Clipping:")
        col.prop(cam, "clip_start", text="Start")
        col.prop(cam, "clip_end", text="End")
        col.prop(cam, "type")
        col.prop(cam, "lens", text="Angle")
        col.prop(cam, "dof_object")
        col.prop(cam, "dof_distance")
        col.prop(cam, "show_limits")
        col.prop(cam, "show_title_safe")
        col.prop(cam, "show_passepartout")
        col.prop(cam, "passepartout_alpha")
        
              
def register():
    bpy.utils.register_class(CameraCraneSetup)
    bpy.utils.register_class(CameraCraneLocation)
    bpy.utils.register_class(CraneAimLocation)
    
    
def unregister():
    bpy.utils.unregister_class(CameraCraneSetup)
    bpy.utils.unregister_class(CameraCraneLocation)
    bpy.utils.unregister_class(CraneAimLocation)

if __name__ == "__main__":
    register()

