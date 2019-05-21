bl_info = {
    "name": "Dynamic Slideshow",
    "author": "Philipp (Hapit) Hemmer",
    "version": (0, 7),
    "blender": (2, 79, 0),
    "location": "View3D > Tool shelf > Slideshow (Tab)",
    "description": "Addon for creating dynamic slideshows. Inspired by a CG Cookie Tutorial, this addon creates cameras and sequences for a slideshow. It uses the 'images as planes' addon for adding pictures.",
    #"warning": "",
    "wiki_url": "https://github.com/hapit/blender_addon_dynamic_slideshow/wiki/Documentation",
    'tracker_url': 'https://github.com/hapit/blender_addon_dynamic_slideshow/issues',
    'support': 'COMMUNITY',
    "category": "Learnbgame"
}


import bpy, urllib.request, random
from math import sqrt
from bpy.props import IntProperty, BoolProperty, EnumProperty, FloatProperty, StringProperty, CollectionProperty
from bpy.app.handlers import persistent
from mathutils import Vector


################### Functions

def get_distance(obj1, obj2):
    """
    return: float. Distance of the two objects
    """
    l = []  # we store the loacation vector of each object
    l.append(obj1.location)
    l.append(obj2.location)
    
    distance = sqrt( (l[0][0] - l[1][0])**2 + (l[0][1] - l[1][1])**2 + (l[0][2] - l[1][2])**2)
    return distance

def get_first_free_vse_channel():
    if bpy.context.scene.sequence_editor == None:
        return 1
    else:
        first_free_channel = 1
        for seq in bpy.context.scene.sequence_editor.sequences:
            if first_free_channel <= seq.channel:
                first_free_channel = seq.channel + 1
        return first_free_channel

def is_vse_empty():
    if bpy.context.scene.sequence_editor == None:
        return True
    elif len(bpy.context.scene.sequence_editor.sequences) == 0:
        return True
    return False

def set_3d_viewport_shade(shade):
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.viewport_shade = shade

def set_all_mesh_draw_type(draw_type):
    for mesh_obj in bpy.context.scene.objects:
        if mesh_obj.type == 'MESH':
            mesh_obj.draw_type = draw_type

def get_sequences_for_frame():
    seq_list = []
    for seq in bpy.context.scene.sequence_editor.sequences:
        cur_frame = bpy.context.scene.frame_current
        if seq.frame_final_start <= cur_frame and seq.frame_final_end >= cur_frame and seq.type == 'SCENE':
            seq_list.append(seq)
    return seq_list

def get_sorted_scene_cameras_list():
    # list of all cameras in scene
    scene_cameras = []
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            scene_cameras.append(obj)
    scene_cameras.sort(key=lambda cam: cam.location.x+cam.delta_location.x)
    return scene_cameras

def has_multiple_cameras():
    cam_count = 0
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            cam_count += 1
            if cam_count > 1:
                return True
    return False

def has_camera_navigation():
    if not has_multiple_cameras():
        return False
    else:
        for cam in get_sorted_scene_cameras_list():
            if cam['picture_mesh'] == None or cam['picture_mesh'] == '':
                return False
    return True
    
def get_prev_camera():
    cameras = get_sorted_scene_cameras_list()
    current_cam = bpy.context.scene.camera
    last_cam = None
    for cam in cameras:
        if cam == current_cam:
            if last_cam == None:
                return current_cam
            else:
                return last_cam
        else:
            last_cam = cam
    return current_cam

def get_next_camera():
    cameras = get_sorted_scene_cameras_list()
    current_cam = bpy.context.scene.camera
    cam_found = False
    for cam in cameras:
        if cam_found:
            return cam
        if cam == current_cam:
            cam_found = True
    return current_cam

def is_draw_type_handling():
    return True

def move_action_on_x(action, x_movement):
    for fcurve in action.fcurves:
        for point in fcurve.keyframe_points:
            point.co.x += x_movement
            point.handle_left.x += x_movement
            point.handle_right.x += x_movement

def has_sequence():
    se = bpy.context.scene.sequence_editor
    if se == None:
        return False
    if len(se.sequences) == 0:
        return False
    return True

def select_single_object(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    bpy.context.scene.objects.active = obj

def set_sequence_active_for_camera(camera):
    se = bpy.context.scene.sequence_editor
    if se != None:
        for seq in se.sequences:
            if seq.scene_camera == camera:
                se.active_strip = seq
                break
        for area in bpy.context.screen.areas:
            if area.type == 'SEQUENCE_EDITOR':
                area.tag_redraw()

def get_effect_type(index):
    # retruns EffectCollection item
    scene = bpy.context.scene
    wm = bpy.context.window_manager
    
    if scene.ds_effect_types != None and len(scene.ds_effect_types) > 0:
        if wm.ds_effect_add_type == 'RANDOM':
            return scene.ds_effect_types[random.randrange(0,len(scene.ds_effect_types))]
        else: # CYCLIC
            return scene.ds_effect_types[index%len(scene.ds_effect_types)]
    else:
        new_effect = bpy.context.scene.ds_effect_types.add()
        new_effect.name = "Cross"
        return new_effect

def add_new_effect(effect_index, effect_channel, seq_start_frame, seq_end_frame, sequence1, sequence2):
    effect_item = get_effect_type(effect_index)
    effect_type = 'GAMMA_CROSS'
    
    if effect_item.effect_type == 'CROSS':
        effect_type = effect_item.cross_type
    elif effect_item.effect_type == 'WIPE':
        effect_type = 'WIPE'
    
    new_effect_sequence = bpy.context.scene.sequence_editor.sequences.new_effect(name=effect_item.name, type = effect_type, channel=effect_channel, frame_start=seq_start_frame, frame_end=seq_end_frame, seq1=sequence1, seq2=sequence2)
    if effect_type == 'WIPE':
        new_effect_sequence.transition_type = effect_item.wipe_type
        new_effect_sequence.direction = effect_item.direction
        new_effect_sequence.blur_width = effect_item.blur
        new_effect_sequence.angle = effect_item.angle

@persistent
def frame_change_handler(scene):
    if is_draw_type_handling() and has_sequence():
        set_all_mesh_draw_type('WIRE')
        for seq in get_sequences_for_frame():
            bpy.data.objects[seq.scene_camera['picture_mesh']].draw_type = 'TEXTURED'

################### Operators

class InitSceneOperator(bpy.types.Operator):
    """Init scene for slideshow"""
    bl_idname = "dyn_slideshow.init_scene"
    bl_label = "Init Scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.context.scene.cursor_location = (0.0, 0.0, 0.0)
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        
        bpy.context.space_data.viewport_shade = 'WIREFRAME'
        bpy.context.scene.game_settings.material_mode = 'GLSL'
        bpy.context.space_data.show_textured_solid = True
        bpy.ops.view3d.viewnumpad(type='TOP', align_active=False)

        # clean scene, remove everything
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete() 
        
        # N-Panel Screen Preview/Render
        bpy.context.scene.render.sequencer_gl_preview = 'SOLID'
        bpy.context.scene.render.use_sequencer_gl_textured_solid = True
        
        bpy.ops.object.camera_add(location=(0,0,2),rotation=(0,0,0))
        
        bpy.context.space_data.viewport_shade = 'SOLID'
        return {'FINISHED'}

def execute_init_cameras(self, context):
    cameraCount = 0
    cameraObj = None
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            cameraCount += 1
            cameraObj = obj
    
    if cameraCount == 1:
        select_single_object(cameraObj)
        bpy.context.scene.camera = cameraObj
        
        # list of all meshes in scene
        scene_meshes = []
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                scene_meshes.append(obj)
        
        # get image_plane under camera
        camera_image_mesh = None
        for mesh_obj in scene_meshes:
            if mesh_obj.type == 'MESH':
                if camera_image_mesh == None:
                    camera_image_mesh = mesh_obj
                elif get_distance(cameraObj, mesh_obj) < get_distance(cameraObj, camera_image_mesh):
                    camera_image_mesh = mesh_obj
                    
        scene_meshes.sort(key=lambda mesh: mesh.location.x)
        if is_draw_type_handling() and camera_image_mesh != None:
            camera_image_mesh.draw_type = 'TEXTURED'
        
        last_mesh = camera_image_mesh
        for mesh_obj in scene_meshes:
            if mesh_obj.type == 'MESH':
                if mesh_obj == camera_image_mesh:
                    print('image_plane already has first camera: '+str(mesh_obj))
                    cameraObj['picture_mesh'] = camera_image_mesh.name
                else:
                    camera_offset_x = mesh_obj.location.x - last_mesh.location.x
                    camera_offset_y = mesh_obj.location.y - last_mesh.location.y
                    
                    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate = {"linked":False})
                    newObj = bpy.context.active_object
                    
                    newObj.delta_location[0] += camera_offset_x
                    newObj.delta_location[1] += camera_offset_y
                    
                    newObj['picture_mesh'] = mesh_obj.name
                    
                    last_mesh = mesh_obj
                    
            else:
                print('ERROR: type is '+mesh_obj.type)
        
                
    else:
        msg = 'Please add and position camera in scene.'
        if cameraCount > 1:
            msg = 'More than one camera in scene.'
        self.report({'ERROR'}, msg)
        return False
    
    return True

def execute_init_sequences(self, context):
    wm = context.window_manager
    
    scene_sequence_name = 'scene'
    
    # variables
    channel_toggle = True
    channel_a = get_first_free_vse_channel()
    channel_b = channel_a + 1
    effect_channel = channel_b + 1
    seq_channel = channel_a
    sequence_index = 0
    effect_index = 0
    effect_count_on_seq = 1
    last_sequence = None
    
    # create sequences for each camera
    bpy.context.scene.sequence_editor_create()
    
    scene_cameras = get_sorted_scene_cameras_list()
    scene_cameras.sort(key=lambda camera: camera.location[0]+camera.delta_location[0])
    
    # resize scene length
    bpy.context.scene.frame_end = wm.ds_start_frame + len(scene_cameras)*wm.ds_sequence_length + (len(scene_cameras)-1)*wm.ds_effect_length
    
    for camera in scene_cameras:
        if sequence_index > 0:
            effect_index = sequence_index-1
        seq_start_frame = wm.ds_start_frame + sequence_index*wm.ds_sequence_length + effect_index*wm.ds_effect_length
        
        # toggle sequence channel
        if channel_toggle:
            seq_channel = channel_a
        else:
            seq_channel = channel_b
        channel_toggle = not channel_toggle
        
        new_sequence = bpy.context.scene.sequence_editor.sequences.new_scene(name=scene_sequence_name+'_'+str(camera.name), scene=bpy.context.scene, channel=seq_channel, frame_start=seq_start_frame)
        new_sequence.frame_final_duration = wm.ds_sequence_length + effect_count_on_seq * wm.ds_effect_length
        
        # set offset in strip
        seqDuration = new_sequence.frame_final_duration
        new_sequence.animation_offset_start = seq_start_frame
        new_sequence.frame_final_duration = seqDuration
        
        # move animation to strip frames
        if camera.animation_data != None:
            move_action_on_x(camera.animation_data.action, seq_start_frame)
        
        new_sequence.scene_camera = camera

        if last_sequence != None and wm.ds_effect_length > 0:
            add_new_effect(effect_index, effect_channel, seq_start_frame, seq_start_frame + wm.ds_effect_length, last_sequence, new_sequence)
        
        sequence_index = sequence_index+1
        effect_index = effect_index+1
        effect_count_on_seq = 2
        last_sequence = new_sequence

    new_sequence.frame_final_end = new_sequence.frame_final_end - wm.ds_effect_length + 1
    
    return True

class SetupSlideshowOperator(bpy.types.Operator):
    """Setup Slideshow"""
    bl_idname = "dyn_slideshow.setup_slideshow"
    bl_label = "Setup Slideshow"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # set shadeless and wire
        if is_draw_type_handling():
            for mesh_obj in bpy.context.scene.objects:
                if mesh_obj.type == 'MESH':
                    for mat_slot in mesh_obj.material_slots:
                        mat_slot.material.use_shadeless = True
                    mesh_obj.draw_type = 'WIRE'
                    if mesh_obj.location == Vector((0.0, 0.0, 0.0)):
                        mesh_obj.draw_type = 'SOLID'

        if not has_multiple_cameras():
            result1 = execute_init_cameras(self, context)
        else:
            result1 = True
        result2 = execute_init_sequences(self, context)
        if result1 and result2:
            return {'FINISHED'}
        else:
            return {'CANCELLED'}
    
    @classmethod
    def poll(cls, context):
        return not has_sequence()

class ActivateSecuenceCameraOperator(bpy.types.Operator):
    """Acivate sequence camera"""
    bl_idname = "dyn_slideshow.activate_sequence_camera"
    bl_label = "Activate camera from active sequence"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        wm = context.window_manager
        
        se = bpy.context.scene.sequence_editor
        print(se)
        if se == None:
            return {'CANCELLED'}
        act_seq = se.active_strip
        print(act_seq)
        if act_seq.type == 'SCENE':
#            if is_draw_type_handling():
#                bpy.data.objects[bpy.context.scene.camera['picture_mesh']].draw_type = 'WIRE'
            bpy.context.scene.camera = act_seq.scene_camera
            select_single_object(bpy.context.scene.camera)
#            if is_draw_type_handling():
#                bpy.data.objects[act_seq.scene_camera['picture_mesh']].draw_type = 'TEXTURED'
            bpy.context.scene.frame_current = act_seq.frame_start+wm.ds_effect_length
        return {'FINISHED'}
    
    @classmethod
    def poll(cls, context):
        se = bpy.context.scene.sequence_editor
        if se == None:
            return False
        act_seq = se.active_strip
        if act_seq == None:
            return False
        return act_seq.type == 'SCENE' and act_seq.scene_camera != None


class ActivateNextCameraOperator(bpy.types.Operator):
    """Acivate sequence camera"""
    bl_idname = "dyn_slideshow.activate_next_camera"
    bl_label = "Activate camera from active sequence"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if bpy.context.scene.camera == None:
            return {'CANCELLED'}
        if is_draw_type_handling():
            bpy.data.objects[bpy.context.scene.camera['picture_mesh']].draw_type = 'WIRE'
        next_camera = get_next_camera()
        bpy.context.scene.camera = next_camera
        set_sequence_active_for_camera(next_camera)
        select_single_object(bpy.context.scene.camera)
        
        if is_draw_type_handling():
            bpy.data.objects[bpy.context.scene.camera['picture_mesh']].draw_type = 'TEXTURED'
        return {'FINISHED'}
    
    @classmethod
    def poll(cls, context):
        return has_camera_navigation()

class ActivatePreviousCameraOperator(bpy.types.Operator):
    """Acivate previous camera"""
    bl_idname = "dyn_slideshow.activate_previous_camera"
    bl_label = "Activate previous camera"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if bpy.context.scene.camera == None:
            return {'CANCELLED'}
        if is_draw_type_handling():
            bpy.data.objects[bpy.context.scene.camera['picture_mesh']].draw_type = 'WIRE'
        prev_camera = get_prev_camera()
        bpy.context.scene.camera = prev_camera
        set_sequence_active_for_camera(prev_camera)
        select_single_object(bpy.context.scene.camera)
        
        if is_draw_type_handling():
            bpy.data.objects[bpy.context.scene.camera['picture_mesh']].draw_type = 'TEXTURED'
        return {'FINISHED'}
    
    @classmethod
    def poll(cls, context):
        return has_camera_navigation()

class AddEffectTypeOperator(bpy.types.Operator):
    """Add effect type"""
    bl_idname = "dyn_slideshow.add_effect_type"
    bl_label = "Add effect type"
    bl_options = {'REGISTER', 'UNDO'}
    
    type = EnumProperty(
        name="Effect type:",
        items=(('CROSS', 'Cross', ''),
               ('WIPE_SINGLE', 'Wipe-Single', ''),
               ('WIPE_DOUBLE', 'Wipe-Double', ''),
               ('WIPE_IRIS', 'Wipe-Iris', ''),
               ('WIPE_CLOCK', 'Wipe-Clock', '')),
        default='CROSS',
        )
    
    def execute(self, context):
        new_effect_type = context.scene.ds_effect_types.add()
        
        new_name = "Effect"
        if self.type == 'WIPE_SINGLE':
            new_effect_type.effect_type = 'WIPE'
            new_effect_type.wipe_type = 'SINGLE'
            new_name = "Wipe-Single"
        elif self.type == 'WIPE_DOUBLE':
            new_effect_type.effect_type = 'WIPE'
            new_effect_type.wipe_type = 'DOUBLE'
            new_name = "Wipe-Double"
        elif self.type == 'WIPE_IRIS':
            new_effect_type.effect_type = 'WIPE'
            new_effect_type.wipe_type = 'IRIS'
            new_name = "Wipe-Iris"
        elif self.type == 'WIPE_CLOCK':
            new_effect_type.effect_type = 'WIPE'
            new_effect_type.wipe_type = 'CLOCK'
            new_name = "Wipe-Clock"
        else:
            new_effect_type.effect_type = 'CROSS'
            new_effect_type.cross_type = 'GAMMA_CROSS'
            new_name = "Cross"
        
        counter = 1
        base_name = new_name
        while context.scene.ds_effect_types.find(new_name) >= 0:
            new_name = base_name + " #" + str(counter)
            counter += 1
        
        new_effect_type.name = new_name
        context.scene.ds_effect_type_index = len(context.scene.ds_effect_types) - 1
        
        return {'FINISHED'}


class RemoveEffectTypeOperator(bpy.types.Operator):
    """Remove effect type"""
    bl_idname = "dyn_slideshow.remove_effect_type"
    bl_label = "Remove effect type"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        context.scene.ds_effect_types.remove(bpy.context.scene.ds_effect_type_index)
        
        if context.scene.ds_effect_type_index == len(context.scene.ds_effect_types):
           context.scene.ds_effect_type_index = len(context.scene.ds_effect_types) - 1
        
        return {'FINISHED'}

class MoveEffectTypeOperator(bpy.types.Operator):
    """Move effect type"""
    bl_idname = "dyn_slideshow.move_effect_type"
    bl_label = "Move effect type"
    bl_options = {'REGISTER', 'UNDO'}
    
    type = EnumProperty(
        name="Effect type:",
        items=(('UP', 'Up', ''),
               ('DOWN', 'Down', '')),
        default='UP',
        )
    
    def execute(self, context):
        old_index = context.scene.ds_effect_type_index
        new_index = -1
        
        if self.type == 'UP':
            new_index = old_index - 1
        else:
            new_index = old_index + 1
        
        if new_index > -1 and new_index < len(context.scene.ds_effect_types):
            context.scene.ds_effect_types.move(old_index, new_index)
            context.scene.ds_effect_type_index = new_index
        
        return {'FINISHED'}


class ManualAddEffectsTypeOperator(bpy.types.Operator):
    """Manual add effects"""
    bl_idname = "dyn_slideshow.manual_add_effects"
    bl_label = "Manual add effects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        sequence_list = []
        effect_channel = 1
        effect_index = 0
        seq1 = None
        for sequ in context.scene.sequence_editor.sequences:
            if sequ.select ==True and (sequ.type == 'IMAGE' or sequ.type == 'META' or sequ.type == 'SCENE' or sequ.type == 'MOVIE' or sequ.type == 'MOVIECLIP'):
                if effect_channel <= sequ.channel:
                   effect_channel =  sequ.channel + 1
                sequence_list.append(sequ)
        
        print('')
        print('')
        for s in sequence_list:
            print(s.name)
            print(s.frame_final_start)
        sequence_list.sort(key=lambda sequ: sequ.frame_final_start)
        print('')
        print('')
        for s in sequence_list:
            print(s.name)
            print(s.frame_final_start)
            print(s.frame_final_end)
        print('')
        print('')
        
        for s in sequence_list:
            if seq1 != None:
                frame_start = s.frame_final_start
                frame_end = seq1.frame_final_end
                if frame_start < frame_end:
                    add_new_effect(effect_index, effect_channel, frame_start, frame_end, seq1, s)
                
                effect_index += 1
            seq1 = s
        
        return {'FINISHED'}

################ UI code

class SCENE_UL_ds_effect_collection(bpy.types.UIList):
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        self.use_filter_show = False
        ob = data
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                layout.prop(item, "name", text="", emboss=False)
            else:
                layout.label(text="", translate=False)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class EffectAddMenu(bpy.types.Menu):
    bl_label = "Effect Add Menu"
    bl_idname = "dyn_slideshow.effect_add_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("dyn_slideshow.add_effect_type", text='Cross').type = 'CROSS'
        layout.operator("dyn_slideshow.add_effect_type", text='Wipe-Single').type = 'WIPE_SINGLE'
        layout.operator("dyn_slideshow.add_effect_type", text='Wipe-Double').type = 'WIPE_DOUBLE'
        layout.operator("dyn_slideshow.add_effect_type", text='Wipe-Iris').type = 'WIPE_IRIS'
        layout.operator("dyn_slideshow.add_effect_type", text='Wipe-Clock').type = 'WIPE_CLOCK'

class EffectExtraMenu(bpy.types.Menu):
    bl_label = "Effect Extra Menu"
    bl_idname = "dyn_slideshow.effect_extra_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("dyn_slideshow.manual_add_effects", text='Manual add effects to VSE')

class EffectCollection(bpy.types.PropertyGroup):
    name = StringProperty(name='effect_name')
    
    effect_type = EnumProperty(
        name="Effect type:",
        items=(('CROSS', 'Cross', ''),
               ('WIPE', 'Wipe', '')),
        default='CROSS',
        )
    
    cross_type = EnumProperty(
        name="Cross type:",
        description="Select cross type.",
        items=(('GAMMA_CROSS', 'Gamma', ''),
               ('CROSS', 'Normal', '')),
        default='GAMMA_CROSS',
        )
    
    wipe_type = EnumProperty(
        name="Wipe type:",
        description="Select wipe type.",
        items=(('SINGLE', 'Single', ''),
               ('DOUBLE', 'Double', ''),
               ('IRIS', 'Iris', ''),
               ('CLOCK', 'Clock', '')),
        default='SINGLE',
        )
    
    direction = EnumProperty(
        name="Wipe direction:",
        items=(('OUT', 'Out', ''),
               ('IN', 'In', '')),
        default='OUT',
        )
    
    blur = FloatProperty(name='Blur Widht:', min=0.0, max=1.0, default=0.2)
    
    angle = FloatProperty(name='Angle:', min=-1.5708, max=1.5708, subtype='ANGLE', unit='ROTATION')

class DynamicSlideshowPanel(bpy.types.Panel):
    """UI panel for the Remesh and Boolean buttons"""
    bl_label = "Dyn. slideshow"
    bl_idname = "TOOLS_dynamic_slideshow"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Slideshow"

    def draw(self, context):
        layout = self.layout
        edit = context.user_preferences.edit
        wm = context.window_manager
        scene = context.scene
        
        layout.operator(InitSceneOperator.bl_idname, 'Init scene')
        
        if 'io_import_images_as_planes' in bpy.context.user_preferences.addons.keys():
            layout.operator('import_image.to_plane', ' Images as Planes', icon='TEXTURE')
        else:
            layout.label("Activate 'Images as Planes'")
                
        layout.separator()
        
        box = layout.box()
        box.prop(wm, 'ds_start_frame', text="Start frame")
        box.prop(wm, 'ds_sequence_length', text="Length")
        box.prop(wm, 'ds_effect_length', text="Effect length")
        
        
        if wm.ds_effect_length > 0:
            effect_box = box.box()
            if not wm.ds_expand_effect:
                effect_box.prop(wm, 'ds_expand_effect', icon='TRIA_RIGHT', icon_only=False, text='Effect settings', emboss=False)
            else:
                effect_box.prop(wm, 'ds_expand_effect', icon='TRIA_DOWN', icon_only=False, text='Effect settings', emboss=False)
                
                effect_box.row().prop(wm, "ds_effect_add_type", text="Effect add type", expand=True)
                
                row = effect_box.row()
                col = row.column()
                
                # UI_UL_list   SCENE_UL_ds_effect_collection
                col.template_list("SCENE_UL_ds_effect_collection", "ds_effect_collection", scene, "ds_effect_types", scene, "ds_effect_type_index", rows=3)
                
                col = row.column(align=True)
                col.menu("dyn_slideshow.effect_add_menu", icon='ZOOMIN', text="")
                col.operator("dyn_slideshow.remove_effect_type", icon='ZOOMOUT', text="")
                col.separator()
                
                col.operator("dyn_slideshow.move_effect_type", icon='TRIA_UP', text="").type = 'UP'
                col.operator("dyn_slideshow.move_effect_type", icon='TRIA_DOWN', text="").type = 'DOWN'
                col.separator()
                
                col.menu("dyn_slideshow.effect_extra_menu", icon='DOWNARROW_HLT', text="")
                if len(scene.ds_effect_types) > 0:
                    selected_effect = scene.ds_effect_types[scene.ds_effect_type_index]
                    effect_box.separator()
                    effect_box.prop(selected_effect, "name", text="Name")
                    effect_box.prop(selected_effect, "effect_type", text="Effect")
                    if selected_effect.effect_type == 'CROSS':
                        effect_box.prop(selected_effect, "cross_type", text="Type")
                    elif selected_effect.effect_type == 'WIPE':
                        effect_box.prop(selected_effect, "wipe_type", text="Transition")
                        effect_box.label("Direction:")
                        effect_box.row().prop(selected_effect, "direction", text="Direction", expand=True)
                        effect_box.prop(selected_effect, "blur", text="Blur Width:", slider=True)
                        if selected_effect.wipe_type == 'SINGLE' or selected_effect.wipe_type == 'DOUBLE':
                            effect_box.prop(selected_effect, "angle", text="Angle")
        
        box.operator(SetupSlideshowOperator.bl_idname, 'Setup slideshow')
        
        layout.separator()
        
        layout.label('Camera navigation:')
        layout.operator(ActivateSecuenceCameraOperator.bl_idname, 'Activate camera from active sequence')
        
        col = layout.row(align=True)
        col.operator(ActivatePreviousCameraOperator.bl_idname, 'Previous')
        col.operator(ActivateNextCameraOperator.bl_idname, 'Next')
        
#################

def register():
    bpy.utils.register_module(__name__)
    
    bpy.app.handlers.frame_change_pre.append(frame_change_handler)
    
    bpy.types.WindowManager.ds_sequence_length = IntProperty(min = 1, default = 100, description='Sequence length without effect length')
    bpy.types.WindowManager.ds_effect_length = IntProperty(min = 0, default = 25, description='Sequence effect length, added to sequence length')
    bpy.types.WindowManager.ds_start_frame = IntProperty(min = 1, default = 1, description='Frame the first sequence starts')
    
    bpy.types.WindowManager.ds_expand_effect = BoolProperty(default=False)
    
    bpy.types.WindowManager.ds_effect_add_type = EnumProperty(
        name="Effect add type",
        items=(('CYCLIC', 'Cyclic', ''),
               ('RANDOM', 'Random', '')),
        default='CYCLIC',
        )
    
    bpy.types.Scene.ds_effect_types = CollectionProperty(type=EffectCollection, name='Effect types:', description='Effect list for adding to VSE.')
    
    bpy.types.Scene.ds_effect_type_index = IntProperty(name='ds_effect_type_index')
    

def unregister():
    bpy.utils.unregister_module(__name__)
    
    bpy.app.handlers.frame_change_pre.remove(frame_change_handler)
    
    try:
        del bpy.types.WindowManager.ds_sequence_length
        del bpy.types.WindowManager.ds_effect_length
        del bpy.types.WindowManager.ds_start_frame
        del bpy.types.WindowManager.ds_expand_effect
        del bpy.types.WindowManager.ds_effect_add_type
        del bpy.types.Scene.ds_effect_types
        del bpy.types.Scene.ds_effect_type_index
        
    except:
        pass

if __name__ == "__main__":
    register()
