
# P r e v i z   C a m e r a   T o o l s
#
#           Version: 0.4

# About:
# Previz Camera Tools sets up the Video Editor to control the
# camera selection in the 3D View on frame updates. Which makes
# it possible to edit the clip timings on the same screen and
# at the same time as editing cameras and everything else in
# the 3D Viewport.

# Run the script:
# 1. Run the script in the text-editor.
# 2. Find the functions in the bottom of the right-hand-side
#    properties menu of the 3D View.

# Functions:
# "Walk Navigation" (native Blender function) will give f.p.s. 
# camera control. Shortcuts: q,w,e,a,s,d
# 
# "Add Camera to View" by Rockbard will turn the view port
# into a camera. Shortcut: Ctrl+Shift+Num_0
# 
# "Cycle Cameras" by CoDEmanX will cycle between cameras. 
# Shortcuts: Ctrl+Shift+Left/Right arrow.
# 
# "Camera Renamer" shows current camera and allows to rename it.
#
# "Add Camera to Sequencer" will add a scene strip
# in the Sequencer with the current camera starting from the
# current frame.

# "Link Sequencer to 3D View" will link the 
# framenumber and switch cameras in the 3D View. So playing 
# the sequencer will play the sequence in the 3D View. So 
# the camera work of the 3d scene can be edited instantly. 

# NB.: 
# - Jitter in the Sequencer playback means hit "Refresh Sequencer" button. 
# - Only scene strips are supported for showing in 3D Viewport in the sequencer. 
# - And only cameras from the current scene can be shown in 3d View. 
#   (This is a limitation of Blender. There is only one scene pr. 
#   Screen) 

# Ideas for more functions(out of my current coding skills): 
#   Buttons(two): Set in and out points 
#   Checkbox: Select Strip/Seq cam updated = Select Camera & update 3D View

# API trouble:
#   Suggest API feature to access local scenes in Sequencer

bl_info = {
    "name": "Previz Camera Tools",
    "author": "Tin2tin, CoDEmanX and Rockbard",
    "version": (0, 2),
    "blender": (2, 79, 0),
    "location": "View3D > N-Toolbar",
    "description": "Various Previz Tools linked to the Sequencer",
    "warning": "",
    "wiki_url": "https://github.com/tin2tin/PrevizCameraTools/",
    "category": "Learnbgame"
}

import bpy
import mathutils
from mathutils import Matrix


# ------------------------------------------------------------------------
#     Make Previz panel
# ------------------------------------------------------------------------

class PrevizMakerPanel(bpy.types.Panel) :
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_label = "Previz Camera Tools"

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon="SEQUENCE")    

    def draw(self, context) :
        layout = self.layout      
        TheCol = layout.column(align = (True))  # , icon="NLA")
        scene = context.scene 
        view = context.space_data      
        
        TheCol.prop(scene, "make_Previz_LinkSequencer", icon = "LINK_AREA")  
        TheCol.separator() 
        TheCol.operator("view3d.walk", text = "Walk Navigation") 
        #TheCol.prop(context.space_data, "lens", text = "View Lens") # Lens for user perspective        
        TheCol.separator()           
        TheCol= TheCol.column(align=True)               
        TheCol.operator("object.add_cam_to_view", text = "Add Camera", icon='CAMERA_DATA')#, icon='CAMERA_DATA') 
        TheCol.separator()  
        TheCol.operator("view3d.make_previz", text = "Add Strip to Sequencer", icon="SEQ_SEQUENCER")                        
        TheCol.separator()        
        TheCol.prop(context.scene.camera, 'name', text='')#, icon='OBJECT_DATAMODE')                       
        TheCol.prop(context.scene.camera.data, "lens") 
        TheCol.prop(context.scene.camera.data, "dof_distance", text="DoF Distance") 
        TheCol.prop(context.scene.camera.data, "dof_object", text="") 
        TheCol.prop(context.scene.camera.data.gpu_dof, "fstop")              
        TheCol.prop_menu_enum(context.scene.camera.data, "show_guide")  
        TheCol.separator() 
        TheCol= TheCol.column(align=True) 
                             
        TheCol.operator("view3d.cycle_cameras", text = "Cycle Cameras", icon="FILE_REFRESH")          
        TheCol.prop(context.scene, 'active_camera', text='', icon='CAMERA_DATA') # Camera drop down menu  
        #TheCol.separator() 
                # check if bool property is enabled
        if (context.scene.make_Previz_LinkSequencer == True):
            syncSceneLength()
            attachAsHandler()
        else:
            detachAsHandler() 
            
            # Select strip for select Cam test
#        if bpy.context.scene.sequence_editor.active_strip.scene_camera.name != "Camera": # for selecting cameras through strips
#            print("hello")                         

class MakePreviz(bpy.types.Operator) :
    """Adds current camera scene strip with to Sequencer"""
    bl_idname = "view3d.make_previz"
    bl_label = "Add Previz"
    bl_options = {'REGISTER',"UNDO"}

    def invoke(self, context, event) :
        addSceneStripInOut()
        return {"FINISHED"}

# ------------------------------------------------------------------------
#     Add Cam To View by Dmitry aka Rockbard
# ------------------------------------------------------------------------

class AddCamToView(bpy.types.Operator):
    """Adds dynamic brush(es) and canvas in one click"""
    bl_idname = "object.add_cam_to_view"
    bl_label = "Add Camera to View"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        # Setting variables
        context = bpy.context
        scene = context.scene
        active = bpy.context.scene.objects.active
        selected = bpy.context.selected_objects
        
        #getting status of view
        #print(bpy.context.space_data.region_3d.is_perspective)
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        if space.region_3d.view_perspective == 'CAMERA':
                            return {'FINISHED'}
        
        #getting  vieport focal lens
        area = bpy.context.area
        old_type = area.type
        area.type = 'VIEW_3D'
        focal = bpy.context.space_data.lens
        area.type = old_type
        dofObject= bpy.data.cameras[bpy.context.scene.camera.name].dof_object
        dofDistance= bpy.data.cameras[bpy.context.scene.camera.name].dof_distance 
        gpu_dofFstop= bpy.data.cameras[bpy.context.scene.camera.name].gpu_dof.fstop      
        
        # Adding camera
        bpy.ops.object.camera_add()
        
        #setting focal length
        bpy.context.object.data.lens = focal

        #Setting as active camera                
        currentCameraObj = bpy.data.objects[bpy.context.active_object.name]
        scene.camera = currentCameraObj

        #setting focal length
        active_cam = bpy.context.scene.camera
        bpy.data.cameras[active_cam.name].lens = focal
                
        bpy.data.cameras[active_cam.name].dof_distance = dofDistance
                
        bpy.data.cameras[active_cam.name].dof_object = dofObject

        bpy.data.cameras[active_cam.name].gpu_dof.fstop = gpu_dofFstop                
        
        #setting sensor
        bpy.context.object.data.sensor_width = 55

        #camera to view
        bpy.ops.view3d.camera_to_view()    
                        
        # Range mapping focus to locZ
        def translate(value, leftMin, leftMax, rightMin, rightMax):
            # Figure out how 'wide' each range is
            leftSpan = leftMax - leftMin
            rightSpan = rightMax - rightMin

            # Convert the left range into a 0-1 range (float)
            valueScaled = float(value - leftMin) / float(leftSpan)

            # Convert the 0-1 range into a value in the right range.
            x = rightMin + (valueScaled * rightSpan)
            return(x)

        locZ = float("%.1f" % translate(focal,13,45,0.1,0.7))

        #fit canera to viewport
        def viewFrom(screen):
    
            for obj in screen.areas:
                if (obj.type == 'VIEW_3D'):
                    return obj
            return None

        v3d = viewFrom(bpy.context.screen)
        r3d = v3d.spaces[0].region_3d

        r3d.view_camera_offset = (0,0)
        r3d.view_camera_zoom = 29.13
        
        #Move camera backwards on local axis
        #ob = bpy.context.scene.objects.active
        #loc = Matrix.Translation((0.0, 0.0, locZ*22))
        #ob.matrix_basis *= loc
                        
        # Deselecting all
        bpy.ops.object.select_all(action='DESELECT')

        # Selecting previously selected object and making it active
        bpy.context.scene.objects.active = active
        
        #if something was selected, select it again
        try:
            if len(selected) != 0:
                active.select = True
        except AttributeError:
            pass    
        #camera off
        #bpy.ops.view3d.viewnumpad(type='CAMERA')

        # Unchecking "Lock camera"
        bpy.context.space_data.lock_camera = False
        
        return {'FINISHED'}

class LockCameraToggle(bpy.types.Operator):
    """Adds dynamic brush(es) and canvas in one click"""
    bl_idname = "object.lock_cam_toggle"
    bl_label = "Lock Camera Toggle"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # Lock camera to View toggle
        bpy.context.space_data.lock_camera = not bpy.context.space_data.lock_camera
       

        return {'FINISHED'}

# ------------------------------------------------------------------------
#     Camera Drop Down menu 
# ------------------------------------------------------------------------

def update(scene, context):
    scene.camera = bpy.data.objects[scene.active_camera]

def get_camera_list(scene, context):
    """Return a list of all cameras in the current scene."""
    items = []
    
    for obj in scene.objects:
        if obj.type == 'CAMERA':
            items.append((obj.name, obj.name, ""))
    
    return items


# ------------------------------------------------------------------------
#     3D Viewport-Cameras to Sequencer
# ------------------------------------------------------------------------

        #update at frame change
def syncSceneLength(*pArgs):
    scn = bpy.context.scene
    seq = scn.sequence_editor
    cf = scn.frame_current
    for i in seq.sequences:    
        try:
            if i.type == "SCENE": #Must be OpenGL strip            
                if (i.frame_final_start <= cf
                and i.frame_final_end > cf
                and i.scene.name==bpy.context.scene.name #Only if current scene in scene-strip
                and not i.mute): #Must be unmute strip
     
                    for area in bpy.context.screen.areas:
                        if area.type == 'VIEW_3D': 
                            # Avoid Camera Local View                        


                            bpy.context.scene.camera = bpy.data.objects[i.scene_camera.name] # Select camera as view
                            area.spaces.active.region_3d.view_perspective = 'CAMERA' # Use camera view            
                        
        except AttributeError:
                pass
  
#Set 3D View to Global. Cameras can't be switched in local.      
def set3dViewGlobal():
    for region in area.regions:
        if region.type == 'WINDOW':
            override = {'area': area, 'region': region} #override context
            bpy.ops.view3d.localview(override) #switch to global view  
            
            
# ------------------------------------------------------------------------
#     Un/link Cameras from Video Editing
# ------------------------------------------------------------------------                        

        #setup update at frame change
def attachAsHandler():
    for f in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(f)
    bpy.app.handlers.frame_change_pre.append(syncSceneLength)
    
def detachAsHandler():
    bpy.app.handlers.frame_change_pre.clear()    


# ------------------------------------------------------------------------
#     Add Camera as Scene strip in Sequencer
# ------------------------------------------------------------------------

def addSceneStripInOut():
        if not bpy.context.scene.sequence_editor:
            bpy.context.scene.sequence_editor_create()   
        scn = bpy.context.scene
        seq = scn.sequence_editor
        cf = scn.frame_current
        # Use current frame for insert position.
        addSceneIn = cf
        addSceneOut = cf+100
        addSceneChannel = 2
        addSceneTlStart = cf        
        newScene=bpy.context.scene.sequence_editor.sequences.new_scene('Scene', bpy.context.scene, addSceneChannel, addSceneTlStart)
        bpy.context.scene.sequence_editor.sequences_all[newScene.name].scene_camera = bpy.data.objects[bpy.context.scene.camera.name]
        bpy.context.scene.sequence_editor.sequences_all[newScene.name].animation_offset_start = addSceneIn
        bpy.context.scene.sequence_editor.sequences_all[newScene.name].frame_final_end = addSceneOut
        bpy.context.scene.sequence_editor.sequences_all[newScene.name].frame_start = cf   
        
# ------------------------------------------------------------------------
#     Cycle Cameras by CoDEmanX
# ------------------------------------------------------------------------             

class VIEW3D_OT_cycle_cameras(bpy.types.Operator):
    """Cycle through available cameras"""
    bl_idname = "view3d.cycle_cameras"
    bl_label = "Cycle Cameras"
    bl_options = {'REGISTER', 'UNDO'}
   

    direction = bpy.props.EnumProperty(
        name="Direction",
        items=(
            ('FORWARD', "Forward", "Next camera (alphabetically)"),
            ('BACKWARD', "Backward", "Previous camera (alphabetically)"),
        ),
        default='FORWARD'
    )

    def execute(self, context):
        scene = context.scene
        cam_objects = [ob for ob in bpy.data.objects if ob.type == 'CAMERA']

        if len(cam_objects) == 0:
            return {'CANCELLED'}

        try:
            idx = cam_objects.index(scene.camera)
            new_idx = (idx + 1 if self.direction == 'FORWARD' else idx - 1) % len(cam_objects)
        except ValueError:
            new_idx = 0

        context.scene.camera = cam_objects[new_idx]
        return {'FINISHED'}


# ------------------------------------------------------------------------
#     Register/Unregister
# ------------------------------------------------------------------------ 

# register/unregister addon classes
addon_keymaps = []

def register() :
    bpy.utils.register_class(AddCamToView)
    bpy.utils.register_class(LockCameraToggle) 
       
    bpy.utils.register_class(MakePreviz)
    bpy.utils.register_class(PrevizMakerPanel)
    bpy.types.Scene.make_Previz_LinkSequencer = bpy.props.BoolProperty \
      (
        name = " Link Sequencer to 3D View",
        description = "Sequencer controls Cameras of 3D View during frame updates",
        default = False
      )

    # Register Camera Drop Down Menu
    bpy.types.Scene.active_camera = bpy.props.EnumProperty(
        name='Cameras',
        description='Select Camera:',
        items=get_camera_list,
        update=update
    )         
      
    # Register Cycle Cameras by CoDEmanX     
    bpy.utils.register_module(__name__)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(VIEW3D_OT_cycle_cameras.bl_idname, 'RIGHT_ARROW', 'PRESS', ctrl=True, shift=True)
        kmi.properties.direction = 'FORWARD'
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(VIEW3D_OT_cycle_cameras.bl_idname, 'LEFT_ARROW', 'PRESS', ctrl=True, shift=True)
        kmi.properties.direction = 'BACKWARD'
        addon_keymaps.append((km, kmi))  
 
        # Register Add Camera to View by Dmitry aka Rockbard      
        km = wm.keyconfigs.addon.keymaps.new(
            name="Window", space_type='EMPTY', region_type='WINDOW')
        kmi = km.keymap_items.new(
            "object.add_cam_to_view", type='NUMPAD_0', value='PRESS', ctrl=True, shift=True)
        kmi = km.keymap_items.new(
            "object.lock_cam_toggle", type='L', value='PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))   

def unregister() :
    bpy.utils.unregister_class(MakePreviz)
    bpy.utils.unregister_class(PrevizMakerPanel)
    del bpy.types.Scene.make_Previz_LinkSequencer

    # Unegister Cycle Cameras by CoDEmanX
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.utils.unregister_module(__name__)

    # Unegister Add Camera to View by Dmitry aka Rockbard    
    bpy.utils.unregister_class(AddCamToView)
    bpy.utils.unregister_class(LockCameraToggle)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()   
    
    # Unregister Camera Drop Down Menu
    del bpy.types.Scene.active_camera     
    

if __name__ == "__main__" :
    register()

#unregister()
