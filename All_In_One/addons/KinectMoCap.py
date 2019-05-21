bl_info = {
    "name": "Kinect MoCap",
    "category": "Object",
    "author": "Pete Dring",
    "version": (1,0),
}

import bpy, threading
from bpy.props import (StringProperty, IntProperty, PointerProperty, BoolProperty)
from bpy.types import (PropertyGroup)

class KinectMoCapSettings(PropertyGroup):
    
    def enable_mo_cap(self, context):
        self.trigger()
            
    def trigger(self):
        if self.enabled:
            try:
                bpy.ops.get_kinect_coordinates()
            except:
                self.enabled = False
            threading.Timer(1 / self.fps, self.trigger).start()
    
    server = StringProperty(
        name = "Host",
        description = "Kinect server host or IP",
        default = "127.0.0.1" 
    )
    
    port = IntProperty(
        name = "Port",
        description = "Kinect server port",
        default = 3456
    )
    
    fps = IntProperty(
        name = "FPS",
        description = "Frame rate",
        default = 1,
        min = 1,
        max = 30
    )
    
    enabled = BoolProperty(
        name = "Enabled",
        description = "Motion capture enabled",
        default = False,
        update = enable_mo_cap
    )

class KinectMoCapUI(bpy.types.Panel):
    bl_idname = "SCENE_PT_kinect"
    bl_label = "Kinect Motion Capture"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        k = scene.kinect

        # Create a simple row.
        layout.label(text="Kinect server:")
        row = layout.row()
        row.prop(k, "server")
        row.prop(k, "port")
        
        row = layout.row()
        row.operator("object.get_kinect_coordinates")
        
        row = layout.row()
        row.label(text="Client:")
        row.prop(k, "fps")
        row.prop(k, "enabled")
        

class KinectMoCap(bpy.types.Operator):
    bl_idname = "scene.get_kinect_coordinates"
    bl_label = "Get Kinect joint data"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    def execute(self, context):
        k = context.scene.kinect
        
        import socket
        
        print("Get joint data")
        server = (k.server, k.port)
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.sendto(b"GetJoints", server)
        
        data = str(client.recv(4096))
        
        lines = data.split("\n")
        for line in lines:
            name, x, y, z = line.split(" ")
            print(name + " is at " + str((x,y,z)))

        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(KinectMoCapSettings)
    bpy.types.Scene.kinect = PointerProperty(type=KinectMoCapSettings)
    bpy.utils.register_class(KinectMoCap)
    bpy.utils.register_class(KinectMoCapUI)
    print("Registered")

def unregister():
    bpy.utils.unregister_class(KinectMoCap)
    bpy.utils.unregister_class(KinectMoCapUI)
    bpy.utils.unregister_class(KinectMoCapSettings)
    del bpy.types.Scene.kinect
    
register()