import bpy

class Bind_Marker(bpy.types.Operator):
    bl_idname = "bind_marker.bind_marker"
    bl_label = "Bind Marker"
    bl_description = "Makes this camera the active camera on your current frame"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        frame = scene.frame_current
        camera = context.camera
        
        for marker in scene.timeline_markers:
            if marker.name == camera.name:
                scene.timeline_markers.remove(marker)
       
        for marker in scene.timeline_markers:
            if marker.frame == frame:
                scene.timeline_markers.remove(marker)
        
        marker = scene.timeline_markers.new(camera.name,frame=frame)
        scene.camera = context.object
        marker.camera = context.object
        
        return {"FINISHED"}
        