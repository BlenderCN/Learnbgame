
# Convert "bind camera to marker" to sequencer scene-strips

bl_info = {
    "name": "Camera Markers to Scene Strips",
    "description": "Converts Camera Bind-To-Markers to Scene Strips",
    "author": "tintwotin",
    "version": (1, 2),
    "blender": (2, 7, 9),
    "location": "VSE strip editor > Header > Add Menu: Marker Cameras",
    "wiki_url": "https://github.com/tin2tin/Camera-Markers-to-Scene-Strips/wiki",
    "tracker_url":"",
    "category": "Learnbgame"
}

import bpy

class SEQUENCE_OT_convert_cameras(bpy.types.Operator):
    """Converts 'Bind Camera To Markers' to Scene Strips"""
    bl_label = "Camera Markers"
    bl_idname = "sequencer.convert_cameras"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene=bpy.context.scene

        if not bpy.context.scene.sequence_editor: #create sequence, if missing
            bpy.context.scene.sequence_editor_create()   

        marker_camera=[]
        marker_frame=[]
        marker_name=[] 
        cam_marker=[]
        cnt=0       
        mi=bpy.context.scene.timeline_markers.items()
        for marker in scene.timeline_markers: #find the cameras and their frame

            if marker.camera:   
                cam_marker.insert(cnt,[marker.frame, marker.camera.name])#mi[cnt][0]])                           
                cnt+=1    

        if len(cam_marker)==0:         # cancel if no cameras
            return {'CANCELLED'}

        cam_marker=sorted(cam_marker,key=lambda mark: mark[0]) # Sort the markers after frame nr.

        #add cameras to sequencer
        cnt=0 # counter        
        for i in cam_marker:                     
            cf = cam_marker[cnt][0]
            addSceneIn = cf

            if cnt<len(cam_marker)-1: # find out frame
                addSceneOut = cam_marker[cnt+1][0]
            else:    
                addSceneOut = addSceneIn +151 #last clip extented 30 fps*5 frames + an ekstra frame for the hack. 
                bpy.context.scene.frame_end=addSceneIn +150 # extent preview area or add scene strip may fail

            addSceneChannel = 1          # attempt to add in this channel - if full, strips will be moved upwards
            addSceneTlStart = cf        

            # Hack: adding a scene strip will make a hard cut one frame before preview area end.
            bpy.context.scene.frame_end=bpy.context.scene.frame_end+1 
            
            # add scene strip in current scene at in and out frame numbers
            newScene=bpy.context.scene.sequence_editor.sequences.new_scene(cam_marker[cnt][1], bpy.context.scene, addSceneChannel, addSceneTlStart)
            newScene.scene_camera = bpy.data.objects[cam_marker[cnt][1]]
            newScene=bpy.context.scene.sequence_editor.sequences_all[newScene.name]
            newScene.animation_offset_start = addSceneIn
            newScene.frame_final_end = addSceneOut
            newScene.frame_start = cf  
            cnt+=1

            # Hack: remove the extra frame again of the preview area.             
            bpy.context.scene.frame_end=bpy.context.scene.frame_end-1

        return {'FINISHED'}

def panel_append(self, context):
    self.layout.operator(SEQUENCE_OT_convert_cameras.bl_idname)

def register():
    bpy.utils.register_class(SEQUENCE_OT_convert_cameras)
    bpy.types.SEQUENCER_MT_add.append(panel_append) # add to "add" vse header menu

def unregister():
    bpy.utils.unregister_class(SEQUENCE_OT_convert_cameras)
    bpy.types.SEQUENCER_MT_add.remove(panel_append)

if __name__ == "__main__":
    register() 

#unregister()     
