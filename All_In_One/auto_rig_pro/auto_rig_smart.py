import bpy, bmesh, math, bpy_extras, blf
from bpy_extras import *
from math import degrees, pi
import mathutils
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from . import auto_rig_datas, auto_rig
from operator import itemgetter

import gpu, bgl
from gpu_extras.batch import *
import gpu_extras

#custom icons
import os
import bpy.utils.previews
from bpy.app.handlers import persistent




print ("\n Starting Auto-Rig Pro: Smart... \n")

blender_version = bpy.app.version_string

# Global vars
handles=[None]
#current_vertex_size = bpy.context.preferences.themes[0].view_3d.vertex_size



##########################  CLASSES  ##########################

class ARP_temp_data:
    current_vertex_size = None
    

arp_temp_data = ARP_temp_data()

class ARP_OT_pick_object(bpy.types.Operator):
      
    #tooltip
    """Get the selected object"""
    
    bl_idname = "id.smart_pick_object"
    bl_label = "smart_pick_object"
    bl_options = {'UNDO'}   
    
    op_prop : bpy.props.StringProperty(name = "Pick")
    
    @classmethod
    def poll(cls, context):       
        return (context.active_object != None)

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        
        if context.active_object.type != 'MESH':       
            self.report({'ERROR'}, "Select a mesh object")
            return{'FINISHED'}
        
        try:        
            
            _pick_object(self.op_prop)      
                       
        finally:
            context.preferences.edit.use_global_undo = use_global_undo         
        return {'FINISHED'}

class ARP_OT_facial_setup(bpy.types.Operator):
      
    #tooltip
    """Setup the facial markers (Mirror mode only)"""
    
    bl_idname = "id.facial_setup"
    bl_label = "facial_setup"
    bl_options = {'UNDO'}    
    
    @classmethod
    def poll(cls, context):
        if context.scene.arp_smart_sym:
            if bpy.data.objects.get("arp_facial_setup") == None:
                return True     

        return False
    

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False        
  
        try:          
            _facial_setup()         
          
                       
        finally:
            context.preferences.edit.use_global_undo = use_global_undo         
        return {'FINISHED'}
        
class ARP_OT_cancel_facial_setup(bpy.types.Operator):
      
    #tooltip
    """Cancel the facial markers setup"""
    
    bl_idname = "id.cancel_facial_setup"
    bl_label = "cancel_facial_setup"
    bl_options = {'UNDO'}       

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False        
  
        try:          
            _cancel_facial_setup()            
                       
        finally:
            context.preferences.edit.use_global_undo = use_global_undo         
        return {'FINISHED'}


class ARP_OT_restore_markers(bpy.types.Operator):
      
    #tooltip
    """Restore the markers position from the previous session"""
    
    bl_idname = "id.restore_markers"
    bl_label = "restore_markers"
    bl_options = {'UNDO'}       

  
    
    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False        
  
        try:          
            _restore_markers()          
            update_sym(self,context)
                       
        finally:
            context.preferences.edit.use_global_undo = use_global_undo         
        return {'FINISHED'}


class ARP_OT_turn(bpy.types.Operator):
      
    #tooltip
    """Turn the character to face the camera"""
    
    bl_idname = "id.turn"
    bl_label = "turn"
    bl_options = {'UNDO'}   
    
    action : bpy.props.StringProperty()
  
    @classmethod
    def poll(cls, context):
        return (context.active_object != None)

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False      
        
  
        try:          
            _turn(context, self.action)         
          
                       
        finally:
            context.preferences.edit.use_global_undo = use_global_undo         
        return {'FINISHED'}


class ARP_OT_set_front_view(bpy.types.Operator):
      
    #tooltip
    """Select the character meshes objects then click it to quicky place the reference bones on the character"""
    
    bl_idname = "id.set_front_view"
    bl_label = "set_front_view"
    bl_options = {'UNDO'}   
    
  
    @classmethod
    def poll(cls, context):
        if context.active_object != None:
            if context.active_object.type == 'MESH':
                return True

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False      
        scene = context.scene   
        
        # Units Warning
        unit_system = bpy.context.scene.unit_settings           
        message = "Scene unit scale not set to 1.0! May give inaccurate results"
        if unit_system.system != 'None':
            if round(unit_system.scale_length, 3) != 1.0:
                self.report({"WARNING"},message.upper())
                
        
        
        # check - is it in local view mode?
        # local view removed from Blender 2.8? Disable it for now
        """
        if context.space_data.lock_camera_and_layers == False:
            layers_disp = [lay for lay in context.space_data.layers]            
            context.space_data.lock_camera_and_layers = True
            context.scene.update()
            for i, layer in enumerate(layers_disp):
                context.scene.layers[i] = layer
        """ 

        
        #check - are they all meshes?
        selection = context.selected_objects
        
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                self.report({'ERROR'}, "Select meshes only")
                return{'FINISHED'} 
            
        #add a 'arp_body_mesh' tag to the objects
        for obj in context.selected_objects:
            obj['arp_body_mesh'] = 1
        
        #duplicate,apply modifiers, merge       
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
        bpy.ops.object.convert(target='MESH')       
        bpy.ops.object.join()   
        context.active_object.name = "body_temp"
        del context.active_object['arp_body_mesh']  

        #disable X Mirror
        bpy.context.active_object.data.use_mirror_x = False
        bpy.context.active_object.data.use_mirror_topology = False

        #hide visibility
        for obj in bpy.data.objects:
            # is object in context?
            found=False
            for i in bpy.context.view_layer.objects:
                if i == obj:
                    found=True
                    break
            if found:               
                if not obj.select_get():
                    obj.hide_viewport = True
                
        #hide from selection
        for obj in selection:
            obj.hide_select = True      
  
        try:
            
            _set_front_view()           
          
                       
        finally:
            context.preferences.edit.use_global_undo = use_global_undo         
        return {'FINISHED'}
        
    
        
        

    

class ARP_OT_match_ref_only(bpy.types.Operator):
      
    #tooltip
    """Click it to aumatically find the reference bones position"""
    
    bl_idname = "id.match_ref_only"
    bl_label = "match_ref_only"
    bl_options = {'UNDO'}   
    
  
    @classmethod
    def poll(cls, context):
        return (context.active_object != None)

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        scene = context.scene
    

        try:
          
            _match_ref()           
            
                       
        finally:
            context.preferences.edit.use_global_undo = use_global_undo         
        return {'FINISHED'}

class ARP_OT_go_detect(bpy.types.Operator):
      
    #tooltip
    """Start the automatic detection"""
    
    bl_idname = "id.go_detect"
    bl_label = "go_detect"
    bl_options = {'UNDO'}   
    
    arm_angle : bpy.props.FloatProperty(default = 0.0)
    fingers_detection_success_l : bpy.props.BoolProperty(default=True)
    fingers_detection_success_r : bpy.props.BoolProperty(default=True)
    error_during_auto_detect : bpy.props.BoolProperty(default=False)
  
    @classmethod
    def poll(cls, context):
        return (context.active_object != None)

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False    
        self.error_during_auto_detect = False
        
        scene = context.scene   
        
        # Save the collections visibility for backup
        collections_visibility = {}
        for col in bpy.data.collections:
            collections_visibility[col.name] = col.hide_viewport
        
        # -- Initial checks
        # is the eyeball object set when facial rig is on?
        if (bpy.data.objects.get('arp_facial_setup')) and (scene.arp_eyeball_name == "" or bpy.data.objects.get(scene.arp_eyeball_name) == None):
            self.report({'ERROR'}, "Eyeball object undefined or does not exist!")
            return{'FINISHED'}
        
        else:           
            # Reveal temp mesh object
            temp_obj = bpy.data.objects.get("body_temp")
            if temp_obj:
                temp_obj.hide_viewport = False      
        
            #Check if all facial setup verts are on the surface mesh
            if bpy.data.objects.get("arp_facial_setup"):
                scene = bpy.context.scene   
                b_name = scene.arp_body_name
                rig_name = bpy.context.active_object.name
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                set_active_object("arp_facial_setup")
        
                arp_facial_setup = bpy.data.objects["arp_facial_setup"]             
                arp_facial_setup.location[1] = -bpy.data.objects[b_name].dimensions[1] * 40
                
                mid_verts=[16, 15, 1, 0, 25, 26]
                #make planar
                for vert in arp_facial_setup.data.vertices:
                    vert.co[1] = 0.0                    
                    # make sure to center mid vertices
                    if vert.index in mid_verts:
                        vert.co[0] = 0.0            
            
                if len(arp_facial_setup.modifiers) > 0:
                    arp_facial_setup.modifiers.remove(arp_facial_setup.modifiers[0])
                
                bpy.context.scene.update()
                shrinkwrap(arp_facial_setup, bpy.data.objects[b_name], Vector((0, 1, 0)))               
                
                for vert in arp_facial_setup.data.vertices:
                    if vert.co[1] == 0.0:
                        arp_facial_setup.location[1] = 0.0
                        #make planar
                        for vert in arp_facial_setup.data.vertices:
                            vert.co[1] = 0.0
                        self.report({'ERROR'}, "Some facial markers verts are out of the mesh surface.")
                        return{'FINISHED'}
        
            # check if an object named 'rig' already exists in the scene, that is not the auto rig pro armature. If so rename it
            rig = bpy.data.objects.get("rig")
            if rig:
                if rig.type == "ARMATURE":
                    if rig.data.bones.get("c_traj") == None:
                        rig.name = "rig_old"
        
            # check if the rig is appended in the scene
            if bpy.data.objects.get("rig") == None:
                rig_add = bpy.data.objects.get("rig_add")
                if rig_add: 
                    bpy.data.objects.remove(rig_add, do_unlink=True)
                    
                auto_rig._append_arp('human')
            
            
            # -- Start detecting!               
            # Create a parent for temp objects
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.empty_add(type='PLAIN_AXES', radius = 1, view_align=True, location=(0,0,0), rotation=(0, 0, 0))  
            bpy.context.active_object.name = "arp_temp_detection"
            bpy.ops.object.select_all(action='DESELECT')
            
                
            try:    
                
                # save the view 3d params
                pivot_type = bpy.context.scene.tool_settings.transform_pivot_point
                
                # Restore user define vertex sizes
                if arp_temp_data.current_vertex_size:
                    bpy.context.preferences.themes[0].view_3d.vertex_size = arp_temp_data.current_vertex_size
            
                # unsimplify, subsurf needed for fingers detection
                simplify_value = scene.render.use_simplify          
                scene.render.use_simplify = False           
            
                # clear selection
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                
                
                # make sure to display the armature collection to operate on it. Only do it for
                # the first collection, since the visibility of one collection is prioritzed among other hidden ones
                rig_parent_collections = get_parent_collections(bpy.data.objects['rig'].users_collection[0])
                for col in rig_parent_collections:
                    col.hide_viewport = False
                        
                #unfreeze character selection
                bpy.data.objects[context.scene.arp_body_name].hide_select = False           
                bpy.data.objects['rig'].hide_select = False
                bpy.data.objects['rig'].hide_viewport = False
                
                # go                
                _auto_detect(self)  
                
                if not self.error_during_auto_detect:
                    set_active_object("rig")
                    
                    #set to 3 spine bones
                    bpy.context.active_object.rig_spine_count = 3
                    auto_rig.set_spine(bottom=False)
                    
                    #simplify, subsurf is slowing down
                    simplify_ss_level = bpy.context.scene.render.simplify_subdivision
                    bpy.context.scene.render.simplify_subdivision = 0
                    scene.render.use_simplify = True    
                    
                    _match_ref(self)
                
                    #restore subsurf simplify to user value
                    bpy.context.scene.render.simplify_subdivision = simplify_ss_level
                
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.id.cancel_and_delete_markers()              
                _delete_detected()          
                
                # Display the ref bones layer only
                set_active_object("rig")    

                bpy.ops.object.mode_set(mode='EDIT')            
                bpy.context.active_object.data.use_mirror_x = True
            
                    #display armaturelayer 17 only
                _layers = bpy.context.active_object.data.layers
                    #must enabling one before disabling others
                _layers[17] = True  
                for i in range(0,31):
                    if i != 17:
                        _layers[i] = False 
                        
                # turn on XRays
                bpy.context.active_object.show_in_front = True

                #restore simplify
                bpy.context.scene.render.use_simplify = simplify_value
                
                # restore the view 3d params
                bpy.context.scene.tool_settings.transform_pivot_point = pivot_type
                
                # send an info message if the fingers detection failed
                if not self.fingers_detection_success_l or not self.fingers_detection_success_r:
                    str = "Fingers detection failed. Try moving the wrist marker closer to the fingers, change the Voxel Precision or Finger Thickness values."
                    self.report({'WARNING'}, str)                   
                    return {'FINISHED'}
                           
            finally:
            
                print("--Execute finally instructions...")
                                
                if self.error_during_auto_detect:
                    # Delete markers
                    try:
                        bpy.ops.id.cancel_and_delete_markers()
                    except:
                        pass                    
                        
                    # Restore scene collections
                    for collec in bpy.data.collections:
                        collec.hide_viewport = collections_visibility[collec.name]
                
                # Delete temps objects
                if not bpy.context.scene.arp_debug_mode:
                    if bpy.data.objects.get("arp_temp_detection"):
                        auto_rig.delete_children(bpy.data.objects["arp_temp_detection"], "OBJECT")
                        
                context.preferences.edit.use_global_undo = use_global_undo      
                
            print("Error during detection?", self.error_during_auto_detect) 
            return {'FINISHED'}
            
            
# main draw function


            
            
class ARP_OT_markers_fx(bpy.types.Operator):
      
    #tooltip
    """Markers FX"""
    
    bl_idname = "id.markers_fx"
    bl_label = "markers_fx" 
    
    active : bpy.props.BoolProperty()   
    
    
    def __init__(self):
        # circles shape parameters
        self.num_segments = 64
        self.radius = 20
        self.radius_dot = 2
        self.radius_outline = self.radius + 2
        # color
        self.circle_color = (0.0, 0.9, 0.5, 0.3)
        self.border_color = (0.5, 0.9, 0.5, 0.6)
        self.center_color = (1, 1, 1, 1)
        
        # internal vars         
        self.shader = None
        self.batch = None
        self.shader_outline = None
        self.batch_outline = None
        self.shader_center = None
        self.batch_center = None
        
        self.region = None
        self.region_3d = None
        self.mouse_x = None
        self.mouse_y = None
        self.hotspot_selectable_marker = None
        self.has_select_marker = ""
        self.mouse_select = None
        
    def draw(self, context):  
        # update datas
        if bpy.data.objects.get('arp_markers'):
                    
            self.hotspot_selectable_marker = None
            
            for obj in bpy.data.objects['arp_markers'].children:
                object_loc_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(self.region, self.region_3d, obj.matrix_world.translation, default=None)
                
                if object_loc_2d == None:
                    continue
                    
                _x = object_loc_2d[0]
                _y = object_loc_2d[1]               

                vertices = ()
                vertices_dot = ()
                vertices_outline = ()
                indices_outline = ()            

                # generate shapes vertices
                for i in range(0, self.num_segments):
                    t = 2 * 3.1415926 * i / self.num_segments
                    
                    # 1.main circle    
                    co_x = _x + math.sin(t) * self.radius
                    co_y = _y + math.cos(t) * self.radius
                    vertices += ((co_x, co_y),) 
                    
                    # 2.outline circle    
                    co_x_out = _x + math.sin(t) * self.radius_outline
                    co_y_out = _y + math.cos(t) * self.radius_outline
                    vertices_outline += ((co_x, co_y),) 
                    vertices_outline += ((co_x_out, co_y_out),) 
                    
                        # loop the circle at the end
                    if i == (self.num_segments-1):
                        vertices_outline += (vertices_outline[0], vertices_outline[1])
                    
                    indices_outline += ((i*2, i*2+1, i*2+2),(i*2+1, i*2+2, i*2+3))   
                    
                    # 3.center circle
                    co_x_dot = _x + math.sin(t) * self.radius_dot
                    co_y_dot = _y + math.cos(t) * self.radius_dot   
                    vertices_dot += ((co_x_dot, co_y_dot),)                             
                
                # Disk batch and shader
                # modes: POINTS, TRIS, TRI_FAN, LINES. Warning, LINES_ADJ do not work
                # main circle
                self.shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
                self.batch = batch_for_shader(self.shader, 'TRI_FAN', {"pos": vertices})

                # center circle
                self.shader_center = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
                self.batch_center = batch_for_shader(self.shader_center, 'TRI_FAN', {"pos": vertices_dot})

                # outline circle
                self.shader_outline = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
                self.batch_outline = batch_for_shader(self.shader_outline, 'TRIS', {"pos": vertices_outline}, indices = indices_outline)
                
                # Highlight the selected marker/mouse over
                final_color = self.circle_color 
                border_final_color = self.border_color
                
                if self.mouse_x:
                    is_in_hotspot = bool((Vector((_x, _y)) - Vector((self.mouse_x, self.mouse_y))).magnitude < 22)
                    if is_in_hotspot:
                        self.hotspot_selectable_marker = obj.name
                    if bpy.context.active_object == obj or is_in_hotspot:                       
                        # change color
                        final_color = ()
                        for i in range(0,3):
                            final_color += (self.circle_color[i]+0.4,)
                        final_color += (self.circle_color[3]-0.2,)# alpha
                        
                        border_final_color = ()
                        for i in range(0,3):
                            border_final_color += (self.border_color[i]+0.4,)
                        border_final_color += (self.circle_color[3]+0.4,)# alpha
                        
                # Render
                # main circle
                self.shader.bind()
                self.shader.uniform_float("color", final_color)
                bgl.glEnable(bgl.GL_BLEND)
                self.batch.draw(self.shader)
                bgl.glDisable(bgl.GL_BLEND)
                
                # outline circle
                self.shader_outline.bind()
                self.shader_outline.uniform_float("color", border_final_color)#self.border_color)
                bgl.glEnable(bgl.GL_BLEND)
                #glfwWindowHint(GLFW_SAMPLES, 4)
                self.batch_outline.draw(self.shader_outline)
                bgl.glDisable(bgl.GL_BLEND)
                
                # dot circle
                self.shader_center.bind()
                self.shader_center.uniform_float("color", self.center_color) 
                self.batch_center.draw(self.shader_center)
    
    
        
    def modal(self, context, event):

        # enable constant update for mouse-over evaluation function
        if context.area:
            context.area.tag_redraw()
            
        # annoying, clicking in a empty space in 2.8 can deselect everything
        # workaround to ensure selection by selecting again 
        if self.has_select_marker != "":
            marker_obj = bpy.data.objects.get(self.has_select_marker)
            if marker_obj:
                if marker_obj.select_get() == False:
                    if context.mode == "OBJECT":
                        bpy.ops.object.select_all(action='DESELECT')
                        set_active_object(self.has_select_marker)   
                        self.has_select_marker = ""
            
        # end operator
        if bpy.data.objects.get('arp_markers') is None or self.active == False or context.scene.arp_quit:
            if bpy.context.scene.arp_debug_mode:
                print('End Markers FX')
            try:
                bpy.types.SpaceView3D.draw_handler_remove(handles[0], 'WINDOW') 
            except:
                if bpy.context.scene.arp_debug_mode:
                    print('Handler already removed')
                pass
            
            return {'FINISHED'}
        
        self.mouse_x = event.mouse_region_x
        self.mouse_y = event.mouse_region_y     
        
        
        if event.type == self.mouse_select and context.mode == "OBJECT":
            if self.hotspot_selectable_marker:
                bpy.ops.object.select_all(action='DESELECT')
                set_active_object(self.hotspot_selectable_marker)               
                self.has_select_marker = self.hotspot_selectable_marker
                
                
        return {'PASS_THROUGH'}
        
        
    def execute(self, context): 
    
        # get mouse select button
        self.mouse_select = 'LEFTMOUSE'
        
        if get_mouse_select() == 'RIGHT':
            self.mouse_select = 'RIGHTMOUSE'          
        
        args = (self, context)  
        #first remove previous session handler if any   
        try:            
            bpy.types.SpaceView3D.draw_handler_remove(handles[0], 'WINDOW') 
        except:
            if bpy.context.scene.arp_debug_mode:
                print('No handlers to remove already removed')  
            pass
                
        if self.active == True: 
            if bpy.context.scene.arp_debug_mode:
                print('Start Markers FX')           
            
            handles[0] = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_3_args, args, 'WINDOW', 'POST_PIXEL')            
            context.window_manager.modal_handler_add(self)
            
            return {'RUNNING_MODAL'}    
        
        return{'CANCELLED'}
        
    def draw_callback_3_args(self, op, context):
        self.region = context.region
        self.region_3d = context.space_data.region_3d
        self.draw(self)
        
        
                
class ARP_OT_add_marker(bpy.types.Operator):
      
    #tooltip
    """Add the a marker to help auto-detection"""
    
    bl_idname = "id.add_marker"
    bl_label = "add_marker"
    bl_options = {'UNDO'}   
    
    first_mouse_x : bpy.props.IntProperty()
    first_value : bpy.props.FloatProperty()

    body_part : bpy.props.StringProperty(name="Body Part")
    body_width : bpy.props.FloatProperty()
    body_height : bpy.props.FloatProperty()

    
    @classmethod
    def poll(cls, context):
        return (context.active_object != None)
        
    def __init__(self):
        self.mouse_select = None
        self.mouse_deselect = None

    # First create the markers objects
    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        try:        
            _add_marker(self.body_part, True)           
            
        finally:
            context.preferences.edit.use_global_undo = use_global_undo         
        return {'FINISHED'}
        
        
        
    # Then keep them movable
    def modal(self, context, event):
        context.area.tag_redraw()       
    
        if event.type == 'MOUSEMOVE':
            delta = self.first_mouse_x - event.mouse_x
            
            _region = bpy.context.region
            _region_3d = bpy.context.space_data.region_3d
            context.active_object.location = bpy_extras.view3d_utils.region_2d_to_location_3d(_region, _region_3d, (event.mouse_region_x, event.mouse_region_y), bpy.context.active_object.location)
            
            #limits
            if context.scene.arp_smart_sym:
                if context.active_object.location[0] < 0 or self.body_part=="neck" or self.body_part == "root" or self.body_part == "chin":
                    context.active_object.location[0] = 0
                
            if context.active_object.location[0] > self.body_width/2:
                context.active_object.location[0] = self.body_width/2
                
            if context.active_object.location[2] > self.body_height:
                context.active_object.location[2] = self.body_height
                
            if context.active_object.location[2] < 0:
                context.active_object.location[2] = 0
    
        
        elif event.type == self.mouse_select or event.type == self.mouse_deselect:           
            if not context.scene.arp_smart_sym:
                sym_marker = bpy.data.objects.get(context.active_object.name + "_sym")
                if sym_marker:                  
                    final_mat = sym_marker.matrix_world
                    sym_marker.constraints[0].influence = 0.0
                
                    sym_marker.matrix_world = final_mat
            
            return {'FINISHED'}

        elif event.type in {self.mouse_deselect, 'ESC'}:         
            #context.active_object.location.x = self.first_value
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}
        
    def invoke(self, context, event):
        self.execute(context)
            
        #first time launch
        # get mouse selection from user pref
        self.mouse_deselect = 'RIGHTMOUSE'
        self.mouse_select = 'LEFTMOUSE'
        if get_mouse_select() == 'RIGHT':
            self.mouse_select = 'RIGHTMOUSE'
            self.mouse_deselect = 'LEFTMOUSE'           
            
        if self.body_part == 'neck':
            #bpy.ops.id.markers_fx(active=False)#close previous model if already running (when opening new blend file while markers still active)
            bpy.ops.id.markers_fx(active=True)
            #bpy.context.space_data.show_manipulator = False
        
        self.body_width = bpy.data.objects[bpy.context.scene.arp_body_name].dimensions[0]
        self.body_height = bpy.data.objects[bpy.context.scene.arp_body_name].dimensions[2]
    
        if context.active_object:
            self.first_mouse_x = event.mouse_x
            self.first_value = context.active_object.location.x
            
            context.window_manager.modal_handler_add(self)          
            
            
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active object, could not finish")
            return {'CANCELLED'}

class ARP_OT_auto_detect(bpy.types.Operator):
      
    #tooltip
    """Select the body mesh then click it to try to automatically find the reference bones location. It will add an empty marker at each bone location"""
    
    bl_idname = "id.auto_detect"
    bl_label = "auto_detect"
    bl_options = {'UNDO'}   
    
    @classmethod
    def poll(cls, context):
        return (context.active_object != None)

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        try:
            try:
                #check if an editable mesh is selected
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.object.mode_set(mode='OBJECT')           
            except TypeError:
                self.report({'ERROR'}, "Please select the body object")
                return{'FINISHED'}          
            
            
            _auto_detect(self)      

            bpy.data.objects[context.scene.arp_body_name].hide_select = False
            bpy.data.objects['rig'].hide_select = False
            bpy.data.objects['rig'].hide_viewport = False
                       
        finally:
            context.preferences.edit.use_global_undo = use_global_undo         
        return {'FINISHED'}

class ARp_OT_delete_detected(bpy.types.Operator):
      
    #tooltip
    """Delete the detected markers"""
    
    bl_idname = "id.delete_detected"
    bl_label = "delete_detected"
    bl_options = {'UNDO'}   
    
    @classmethod
    def poll(cls, context):
        return (context.active_object != None)

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        try:
            try:
                bpy.data.objects["auto_detect_loc"]                      
            except KeyError:
                self.report({'ERROR'}, "No markers found")
                return{'FINISHED'}
                       
            _delete_detected()        
                       
        finally:
            context.preferences.edit.use_global_undo = use_global_undo         
        return {'FINISHED'}
    
class ARP_OT_cancel_and_delete_markers(bpy.types.Operator):
      
    #tooltip
    """Cancel the smart detection and delete the markers"""
    
    bl_idname = "id.cancel_and_delete_markers"
    bl_label = "cancel_and_delete_markers"
    bl_options = {'UNDO'}   
    
    @classmethod
    def poll(cls, context):
        return (context.active_object != None)

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        try:
            try:
                bpy.data.objects["arp_markers"]                      
            except KeyError:
                self.report({'ERROR'}, "No markers found")
                return{'FINISHED'}
            #save current mode
            current_mode = context.mode
            active_obj = context.active_object
        
            bpy.ops.object.mode_set(mode='OBJECT')
            
            #unfreeze character selection and restore visibility
            for obj in bpy.data.objects:
                if not 'rig_add' in obj.name:
                    obj.hide_viewport = False
                if obj.parent != None:
                    if obj.parent.name != "rig_ui" or '_char_name' in obj.name:
                        obj.hide_select = False
                else:
                    obj.hide_select = False 

                if obj.name == "char_grp" or obj.name == "char1_grp":
                    obj.hide_select = True
            
                #delete the 'arp_body_mesh' tag from objects
                if len(obj.keys()) > 0:
                    if 'arp_body_mesh' in obj.keys():
                        del obj['arp_body_mesh']
                    
            if bpy.data.objects.get('rig') != None:             
                bpy.data.objects['rig'].hide_viewport = False
                
            _cancel_and_delete_markers()
            
            
            #restore current mode
            try:
                set_active_object(active_obj.name)
            except:
                pass
                #restore saved mode    
            if current_mode == 'EDIT_ARMATURE':
                current_mode = 'EDIT'
        
            try:
                bpy.ops.object.mode_set(mode=current_mode)
            except:
                pass
    
                       
        finally:
            context.preferences.edit.use_global_undo = use_global_undo         
        return {'FINISHED'}
    
    
 ##########################  FUNCTIONS  ##########################

    # extra functions -------------------------------------------------------------  
def get_mouse_select():   
    active_kc = bpy.context.preferences.keymap.active_keyconfig
    active_pref = bpy.context.window_manager.keyconfigs[active_kc].preferences    
    return getattr(active_pref, 'select_mouse', 'LEFT')

    
def shrinkwrap(source_obj, target_obj, ray_dir):
    depsgraph = bpy.context.depsgraph
    
    for vert in source_obj.data.vertices:
        ori = source_obj.matrix_world @ vert.co 
        obj_eval = depsgraph.objects.get(target_obj.name, None)  
        if obj_eval:
            success, hit, normal, index = obj_eval.ray_cast(ori, ray_dir)
            if hit:
                vert.co = source_obj.matrix_world.inverted() @ hit


                                
def tolerance_check(source, target, axis, tolerance, x_check, side):
    if source[axis] <= target + tolerance and source[axis] >= target - tolerance:
        #left side only  
        if x_check:     
            if side == ".l":
                if source[0] > 0:
                    return True
            if side == ".r":
                if source[0] < 0:
                    return True
        else:           
            return True    
            
       
        
def tolerance_check_2(source, target, axis, axis2, tolerance, side):
    if source[axis] <= target[axis] + tolerance and source[axis] >= target[axis] - tolerance:
        if source[axis2] <= target[axis2] + tolerance and source[axis2] >= target[axis2] - tolerance:
            #one side only
            if side == ".l":
                if source[0] > 0:
                    return True
            if side == ".r":
                if source[0] < 0:
                    return True     
            
def tolerance_check_3(source, target, tolerance, x_check, side):
    if source[0] <= target[0] + tolerance and source[0] >= target[0] - tolerance:
        if source[1] <= target[1] + tolerance and source[1] >= target[1] - tolerance:
            if source[2] <= target[2] + tolerance and source[2] >= target[2] - tolerance:
                #left side only
                if x_check:
                    if side == ".l":
                        if source[0] > 0:
                            return True
                    if side == ".r":
                        if source[0] < 0:
                            return True
                else:
                    return True    
        
def cross(a, b):
    c = Vector((a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0]))
    return c
    
def get_line_plane_intersection(planeNormal, planePoint, rayDirection, rayPoint, epsilon=1e-6): 
    ndotu = planeNormal.dot(rayDirection)
    if abs(ndotu) < epsilon:
        raise RuntimeError("no intersection or line is within plane")
 
    w = rayPoint - planePoint
    si = -planeNormal.dot(w) / ndotu
    Psi = w + si @ rayDirection + planePoint
    return Psi
    
def clear_selection():
    bpy.ops.mesh.select_all(action='DESELECT')

def clear_object_selection():
    bpy.ops.object.select_all(action='DESELECT')
    
def set_active_object(object_name): 
    bpy.data.objects[object_name].select_set(state=True)
    bpy.context.view_layer.objects.active = bpy.data.objects[object_name]
    
     
def _pick_object(prop):
    if prop == "eyeball":
        bpy.context.scene.arp_eyeball_name = bpy.context.active_object.name
    
def _cancel_facial_setup():
    
    # Hide meshes objects
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.name != "body_temp":
            obj.hide_viewport = True
            obj.hide_select = True
            
    # Reveal temp mesh object
    temp_obj = bpy.data.objects.get("body_temp")
    if temp_obj:
        temp_obj.hide_viewport = False      
            
    # Restore user define vertex sizes  
    if arp_temp_data.current_vertex_size:       
        bpy.context.preferences.themes[0].view_3d.vertex_size = arp_temp_data.current_vertex_size
    
    # remove the arp_facial_setup mesh
    bpy.data.objects.remove(bpy.data.objects["arp_facial_setup"], do_unlink = True) 
        
    #center front view
    if bpy.data.objects.get(bpy.context.scene.arp_body_name):
        print("Center view")
        body_t = bpy.data.objects[bpy.context.scene.arp_body_name]
        body_t.hide_select = False
        bpy.ops.object.select_all(action='DESELECT')
        set_active_object(body_t.name)
    
        bpy.ops.view3d.view_axis(type='FRONT')
        try:
            bpy.ops.view3d.view_selected(use_all_regions=False)
        except:
            print("Invalid region, could not view selected")
    
        bpy.ops.object.select_all(action='DESELECT')
        body_t.hide_select = True
        
    set_active_object(bpy.data.objects["arp_markers"].children[0].name)
     
def _facial_setup():

    # Reveal meshes objects for eyeballs selection
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_viewport = False
            obj.hide_select = False
            
    # Hide temp mesh object
    temp_obj = bpy.data.objects.get("body_temp")
    if temp_obj:
        temp_obj.hide_viewport = True           
        
    addon_directory = os.path.dirname(os.path.abspath(__file__))        
    filepath = addon_directory + "/" + "facial_setup.blend"
    
    # load the objects data in the file
    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        data_to.objects = data_from.objects
    
    # add the objects in the scene
    for obj in data_to.objects:
        if obj is not None:
            bpy.context.scene.collection.objects.link(obj)          
            
    bpy.ops.object.select_all(action='DESELECT')
    set_active_object('arp_facial_setup')
    obj = bpy.data.objects['arp_facial_setup']
    
    # Make big vertices
    arp_temp_data.current_vertex_size = bpy.context.preferences.themes[0].view_3d.vertex_size
    bpy.context.preferences.themes[0].view_3d.vertex_size = 8
    print("Assigned vertices size")
    
    # set pos and scale
    if bpy.data.objects.get("chin_loc") != None:#retro compatibility
        chin_loc = bpy.data.objects["chin_loc"].location
    else:
        chin_loc = bpy.data.objects["neck_loc"].location
    obj.location[2] = chin_loc[2]
    
    body = bpy.data.objects[bpy.context.scene.arp_body_name]
    body_height = body.dimensions[2]
    head_height = body_height - chin_loc[2]
    
    obj.dimensions[2] =head_height
    obj.scale = [obj.scale[2]*0.55, obj.scale[2]*0.55, obj.scale[2]*0.55]
    
    bpy.ops.view3d.view_selected(use_all_regions=False)

    bpy.ops.object.mode_set(mode='EDIT')
    
    

     
def _restore_markers():
    scene = bpy.context.scene
    
    # Mirror state
    val_bool = True
    for item in scene.arp_markers_save:
        if item.name == "mirror_state":
            val = item.location[0]
            val_bool = True
            if val == 0:
                val_bool = False
                
    scene.arp_smart_sym = val_bool
    
    
    # Body markers
    for item in scene.arp_markers_save: 
        if item.name != "mirror_state":
            if not "sym_loc" in item.name:# ensure retro-compatibility, names changed
                if bpy.data.objects.get(item.name) == None: 
                    #create it if does not exist                
                    _add_marker(item.name.replace("_loc", ""), False)
                    
                bpy.data.objects[item.name].location = item.location
        
        
            
    # Facial markers
    if len(scene.arp_facial_markers_save) > 0:
        _facial_setup()
        bpy.ops.object.editmode_toggle()#must switch to object mode to update the datas
        
        for item in scene.arp_facial_markers_save:
            facial_setup = bpy.data.objects["arp_facial_setup"]
            facial_setup.data.vertices[item.id].co = facial_setup.matrix_world.inverted() @ item.location
            
    
        bpy.ops.object.editmode_toggle()

            
    #enable markers fx
    try:
        bpy.types.SpaceView3D.draw_handler_remove(handles[0], 'WINDOW')
        if bpy.context.scene.arp_debug_mode:
            print('Removed handler')
    except:
        if bpy.context.scene.arp_debug_mode:
            print('No handler to remove')
        pass
    bpy.ops.id.markers_fx(active=True)
    
    
    
def get_parent_collections(target):
    # return the list of all parent collections to the specified target collection
    # with a recursive function. A sub-function is used, string based, to ease the process
    
    def get_parent_collections_string(target_name):
        parent_collections = ""
        found = None
        
        for collec in bpy.data.collections:
            for child in collec.children:
                if child.name == target_name:
                    print("found", collec.name)  
                    parent_collections += collec.name + ","        
                    parent_collections += get_parent_collections_string(collec.name)
                
        return parent_collections
    

    string_result = get_parent_collections_string(target.name)
    to_list = [bpy.data.collections[i] for i in string_result[:-1].split(",")]
    
    return to_list
    
    meshes_data = []
    
    for child in children:
        # store the mesh data for removal afterward
        if child.data:
            if not child.data.name in meshes_data:
                meshes_data.append(child.data.name)
                
        bpy.data.objects.remove(child, do_unlink=True, do_id_user=True, do_ui_user=True)
        
    for data_name in meshes_data:
        current_mesh = bpy.data.meshes.get(data_name)
        if current_mesh:                    
            bpy.data.meshes.remove(current_mesh, do_unlink=True, do_id_user=True, do_ui_user=True)
        
        
    bpy.data.objects.remove(passed_node, do_unlink = True)
            
            
    
#-- start create_hand_plane()
def create_hand_plane(_bound_up, _bound_top, _bound_bot, _bound_left, _bound_right, body_height, angle1, hand_offset, body, angle2):

    bpy.ops.object.mode_set(mode='OBJECT')        

    bpy.ops.mesh.primitive_plane_add(size=1, view_align=False, enter_editmode=True, location=(0.0, 0.0, _bound_up + (body_height)), rotation=(0, 0, 0))
    bpy.context.active_object.name = "plane_matrix" 
    #disable X Mirror
    bpy.context.active_object.data.use_mirror_x = False
    
    bpy.ops.mesh.select_all(action='DESELECT')
    mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
    
    mesh.verts.ensure_lookup_table() #debug_mode
    # index: 0 bot right, 1 up right, 2 bot left, 3 up left
    mesh.verts[0].co[0] = _bound_bot
    mesh.verts[0].co[1] = _bound_right
    mesh.verts[1].co[0] = _bound_top
    mesh.verts[1].co[1] = _bound_right
    mesh.verts[2].co[0] = _bound_bot
    mesh.verts[2].co[1] = _bound_left
    mesh.verts[3].co[0] = _bound_top
    mesh.verts[3].co[1] = _bound_left
    
    # rotate it according to hand rotation
     #enlarge borders safe
    bpy.ops.mesh.select_all(action='SELECT') 
    
    bpy.ops.transform.resize(value=(1.2, 1.2, 1.2), constraint_axis=(True, True, False), orient_type='GLOBAL', mirror=False, proportional='DISABLED')
    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
    hand_offset[0] = bpy.context.active_object.location[0]
    hand_offset[1] = bpy.context.active_object.location[1]
    hand_offset[2] = bpy.context.active_object.location[2]
    
        #Y rotate
    """
    bpy.ops.object.mode_set(mode='EDIT') 
    bpy.context.scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER'
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.rotate(value=angle2, axis=(0, 1, 0), constraint_axis=(False, True, False), constraint_orientation='LOCAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.00168535)
    """

        #Z rotate               
    bpy.context.active_object.rotation_euler[2] = -angle1 * 0.8
    """
        #X rotate for better handling of thumb extreme rotation
    bpy.ops.object.editmode_toggle()
    bpy.context.scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER'
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.rotate(value=-0.174533, axis=(-1, -2.22045e-016, -4.93038e-032), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.00528934)
    bpy.ops.object.editmode_toggle()
    """
    
    #subdivide it 
    bpy.ops.object.mode_set(mode='OBJECT')      
    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.context.active_object.modifiers["Subsurf"].subdivision_type = 'SIMPLE'
    bpy.context.active_object.modifiers["Subsurf"].levels = 7
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")
    
    #get edge length
    edge_dist = 0.0
    bpy.ops.object.editmode_toggle()
    
    mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
    mesh.edges.ensure_lookup_table()
    edge_dist = mesh.edges[0].calc_length()
    bpy.ops.object.editmode_toggle()
    
    #shrink on body
    bpy.ops.object.modifier_add(type='SHRINKWRAP')
    bpy.context.active_object.modifiers["Shrinkwrap"].target = bpy.data.objects['arp_hand_aligned']
    bpy.context.active_object.modifiers["Shrinkwrap"].wrap_method = 'PROJECT'
    bpy.context.active_object.modifiers["Shrinkwrap"].use_negative_direction = True
    bpy.context.active_object.modifiers["Shrinkwrap"].use_project_z = True 
    
    
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap")
    
    #delete upper part
    bpy.ops.object.editmode_toggle()
    mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
    bpy.ops.mesh.select_all(action='DESELECT')

    
    mesh.verts.ensure_lookup_table() 
    for v in mesh.verts:        
        if tolerance_check(v.co, 0.0, 2, body_height/5, False):      
            v.select = True                
    bpy.ops.mesh.delete(type='VERT')
    
    #check for distorted grid (no space between thumb/palm)
    bpy.ops.mesh.select_all(action='DESELECT')
    mesh.edges.ensure_lookup_table() 
    for e in mesh.edges:
        if e.calc_length() > edge_dist * 11:
            for face in e.link_faces:
                face.select = True
    
    bpy.ops.mesh.delete(type='FACE')
    
    
    
#-- end create_hand_plane()    
    

def copy_list(list1, list2):
    for pikwik in range(0, len(list1)):
        list2[pikwik] = list1[pikwik]
        
        
def _turn(context, action):

    body = bpy.data.objects[bpy.context.scene.arp_body_name]
    
    wise = 1
    
    if action == 'positive':
        wise = 1
    else:
        wise = -1
    
    bpy.ops.object.select_all(action='DESELECT')
    
    #restore selection visibility
    body.hide_select = False
    body_objects = []
    for obj in bpy.data.objects:
        if len(obj.keys()) > 0:
            if 'arp_body_mesh' in obj.keys():
                body_objects.append(obj)
                obj.hide_viewport = False
                obj.hide_select = False
                set_active_object(obj.name)
                print('selected', obj.name)
                
    set_active_object(body.name)
    
    #rotate from world origin
    bpy.context.scene.cursor.location = [0.0,0.0,0.0]
    bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
    
    bpy.ops.transform.rotate(value=-math.pi/2*wise, orient_axis='Z', constraint_axis=(False, False, True), orient_type='GLOBAL', mirror=False, proportional='DISABLED')
    
    bpy.context.scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER'

    bpy.ops.object.select_all(action='DESELECT')
    set_active_object(body.name)
    #apply rotation
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    
    #hide from selection
    body.hide_select = True
    for obj in body_objects:
        obj.hide_select = True
        obj.hide_viewport = True
        
    set_active_object('arp_markers')
    bpy.ops.object.select_all(action='DESELECT')    
    

def create_empty_loc(radii, pos1, name):

    bpy.ops.object.empty_add(type='PLAIN_AXES', radius = radii, view_align=True, location=(pos1), rotation=(0, 0, 0))  
    # rename it     
    bpy.context.active_object.name = name + "_auto"
    # parent it
    bpy.context.active_object.parent = bpy.data.objects["auto_detect_loc"]
    
def vectorize3(list):
    return Vector((list[0], list[1], list[2]))

def init_selection(active_bone):
    try:
        bpy.ops.armature.select_all(action='DESELECT')
    except:
        pass
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='DESELECT')
    if (active_bone != "null"):
        bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[active_bone].bone #set the active bone for mirror
    bpy.ops.object.mode_set(mode='EDIT')
    
def mirror_hack():
    revert = False
    if not bpy.context.active_object.data.use_mirror_x:
        bpy.context.active_object.data.use_mirror_x = True
        revert = True
        
    # Update the mirrored side, hacky   
    bpy.ops.transform.translate(value=(0, 0, 0), orient_type='NORMAL', proportional='DISABLED')
    
    if revert:
        bpy.context.active_object.data.use_mirror_x = False
   
def get_edit_bone(name):
    if bpy.context.active_object.data.edit_bones.get(name):
        return bpy.context.active_object.data.edit_bones[name]
    else:
        return None

def get_object(name):
    if bpy.data.objects.get(name) != None:
        return bpy.data.objects[name]
    else:
        return None
    
    # CLASS FUNCTIONS -------------------------------------------------------------   
    
def _match_ref(self):
    
    print('\nMatching the reference bones...')
    
    scene = bpy.context.scene   
    b_name = scene.arp_body_name
    rig_name = bpy.context.active_object.name
    found_picker = False
    
    # Unparent first meshes from the armature if any    
    if len(bpy.context.active_object.children) > 0:         
        for child in bpy.context.active_object.children:
            if "rig_ui" in child.name and child.type == "EMPTY":
                found_picker = True
            if child.type == "MESH":
                child_mat = child.matrix_world.copy()
                child.parent = None
                # keep transforms
                child.matrix_world = child_mat
            
    
    #scale the rig object according to the character height
    fac = 1
    if found_picker:
        fac = 35
        
    bpy.context.active_object.dimensions[2] = bpy.data.objects[b_name].dimensions[2] * fac
    bpy.context.active_object.scale[1] = bpy.context.active_object.scale[2] 
    bpy.context.active_object.scale[0] = bpy.context.active_object.scale[2]
    
    print("    Applying the facial if any...")
    #Apply the facial markers modifiers if any  
    if bpy.data.objects.get("arp_facial_setup") != None:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        set_active_object("arp_facial_setup")       
        arp_facial_setup = bpy.data.objects["arp_facial_setup"]
        arp_facial_setup.location[1] += -bpy.data.objects[b_name].dimensions[1] * 40        
        
        #make planar
        for vert in arp_facial_setup.data.vertices:
            vert.co[1] = 0.0
        
        #add shrinkwrap mod     
        if len(arp_facial_setup.modifiers) > 0:
            arp_facial_setup.modifiers.remove(arp_facial_setup.modifiers[0])
        mod = arp_facial_setup.modifiers.new("shrinkwrap", 'SHRINKWRAP')
        mod.target = bpy.data.objects[b_name]
        mod.wrap_method = 'PROJECT'
        mod.use_project_x = False
        mod.use_project_y = True
        mod.use_project_z = False
        mod.use_positive_direction = True
        mod.use_negative_direction = False              
        
        
        bpy.ops.object.convert(target='MESH')
        
        #eyeball loc
        eyeb = bpy.data.objects[scene.arp_eyeball_name]
        eyeb.hide_viewport = False
        set_active_object(eyeb.name)
        bpy.ops.object.mode_set(mode='EDIT')
        # make sure to unhide all verts
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
            #find the vert the more on the left
        left_vert = None
        _mesh = bmesh.from_edit_mesh(eyeb.data)
        for vert in _mesh.verts:
            if left_vert == None:
                left_vert = vert
            else:
                if vert.co[0] > left_vert.co[0]:
                    left_vert = vert
        
        left_vert.select = True     

        bpy.ops.mesh.select_linked(delimit=set())   
        bpy.context.scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER'
        bpy.ops.view3d.snap_cursor_to_selected()
        
        
        
        eyeball_loc = bpy.context.scene.cursor.location.copy()
        
        bpy.ops.object.mode_set(mode='OBJECT')
        eyeb.hide_viewport = True
        set_active_object(rig_name)
        
    
        
        

    #Start matching the bones coords to auto_loc coords
    bpy.ops.object.mode_set(mode='EDIT')        
        
    #display all layers
    _layers = bpy.context.active_object.data.layers 
    for i in range(0,31):   
        _layers[i] = True 
    
    sides = [".l", ".r"]
    side = ".l"
    
    rig_matrix_world_inv = bpy.data.objects["rig"].matrix_world.inverted()
    rig_matrix = bpy.data.objects["rig"].matrix_world
    
    used_sides = [".l"]
    
    #enable x-axis mirror edit or not
    if scene.arp_smart_sym:
        bpy.context.active_object.data.use_mirror_x = True
    else:
        bpy.context.active_object.data.use_mirror_x = False
        used_sides.append(".r")
    
    for used_side in used_sides:
        print("\n    matching feet", used_side, "...")
        # FOOT
        init_selection("foot_ref"+used_side)
        foot = get_edit_bone("foot_ref"+used_side)   
        foot.head = rig_matrix_world_inv @ get_object("ankle_loc" + used_side + "_auto").location
        foot.tail = rig_matrix_world_inv @ get_object("toes_start" + used_side +  "_auto").location
        bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')
        if scene.arp_smart_sym:
            mirror_hack()
    
        init_selection("toes_ref"+used_side)
        toes_ref = get_edit_bone("toes_ref"+used_side)   
        toes_ref.head = rig_matrix_world_inv @ get_object("toes_start" + used_side + "_auto").location
        toes_ref.tail = rig_matrix_world_inv @ get_object("toes_end" + used_side + "_auto").location
        bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')
        if scene.arp_smart_sym:
            mirror_hack()
    
            
        foot_dir = scene.arp_foot_dir_l
        if used_side == ".r":
            foot_dir = scene.arp_foot_dir_r     
    
        init_selection("foot_bank_01_ref"+used_side)
        foot_bank_01_ref = get_edit_bone("foot_bank_01_ref"+used_side)
        bank_right = get_object("bank_left_loc" + used_side + "_auto").location  
        foot_bank_01_ref.head = rig_matrix_world_inv @ bank_right
        foot_bank_01_ref.tail = foot_bank_01_ref.head + (foot_dir.normalized() * get_edit_bone('foot_ref'+used_side).length*0.2)
        if scene.arp_smart_sym:
            mirror_hack()
    
        init_selection("foot_bank_02_ref"+used_side)
        foot_bank_02_ref = get_edit_bone("foot_bank_02_ref"+used_side)
        bank_left = get_object("bank_right_loc" + used_side +"_auto").location  
        foot_bank_02_ref.head = rig_matrix_world_inv @ bank_left
        foot_bank_02_ref.tail = foot_bank_02_ref.head + (foot_dir.normalized() * get_edit_bone('foot_ref'+used_side).length*0.2)
        
        if scene.arp_smart_sym:
            mirror_hack()
    
        init_selection("foot_heel_ref"+used_side)
        foot_heel_ref = get_edit_bone("foot_heel_ref"+used_side)
        heel_auto = get_object("bank_mid_loc" + used_side + "_auto").location
        foot_heel_ref.head = rig_matrix_world_inv @ heel_auto
        foot_heel_ref.tail = foot_heel_ref.head + (foot_dir.normalized() * get_edit_bone('foot_ref'+used_side).length*0.2)
        if scene.arp_smart_sym:
            mirror_hack()
    
        toes_end_auto = get_object("toes_end" + used_side + "_auto").location 
        heel_auto = get_object("bank_mid_loc" + used_side + "_auto").location
        foot_length = (toes_end_auto - heel_auto).magnitude
        
        """
        print("    matching toes", used_side + "...")
            # toes fingers
        toes_list=["toes_pinky", "toes_ring", "toes_middle", "toes_index", "toes_thumb"]
        foot_bank_01_ref = get_edit_bone("foot_bank_01_ref"+used_side)
        foot_bank_02_ref = get_edit_bone("foot_bank_02_ref"+used_side)
        toes_ref = get_edit_bone("toes_ref"+used_side)
    
        foot_dir = rig_matrix_world_inv @ (toes_end_auto - heel_auto)
        
        #Disable mirror for toes, not selection based
        bpy.context.active_object.data.use_mirror_x = False
    
        _sides = ['.l', '.r']
    
        for _side in _sides:
            foot_bank_01_ref = get_edit_bone("foot_bank_01_ref"+_side)
            foot_bank_02_ref = get_edit_bone("foot_bank_02_ref"+_side)
            toes_ref = get_edit_bone("toes_ref"+_side)
                
            if _side == '.r':
                foot_dir[0] *= -1
            
            for t in range(0,5):
                max = 4
                if t == 4:
                    max = 3 #thumb has less phalanges
                for p in range (1,max):         
                    bone = get_edit_bone(toes_list[t] + str(p) + "_ref" + _side)                
                    
                    bone.head = (foot_bank_01_ref.head + ((foot_bank_02_ref.head - foot_bank_01_ref.head) * t) / 5)
                    bone.head += foot_dir * 0.75 + (((foot_dir * 0.25) * p) / max)          
                    bone.head[2] = toes_ref.head[2]
                    
                    #if last phalanges              
                    if p == max-1:
                        bone.tail = bone.head + ((foot_dir * 0.25) /max)                    
                        
        bpy.ops.armature.select_all(action='DESELECT')
        """
        
        
        if scene.arp_smart_sym:
            bpy.context.active_object.data.use_mirror_x = True
    
                
        print("    matching legs", used_side, "...")
        # LEGS
        init_selection("thigh_ref"+used_side)
        thigh_ref = get_edit_bone("thigh_ref"+used_side)
        knee_auto = get_object("knee_loc" + used_side + "_auto").location  
        thigh_ref.tail = rig_matrix_world_inv @ knee_auto
        thigh_ref.head = rig_matrix_world_inv @ get_object("leg_loc" + used_side + "_auto").location    

            # make sure the knee is pointing forward for IK
        median_point =  (get_edit_bone("foot_ref" + used_side).head + get_edit_bone("thigh_ref" + used_side).head)*0.5
        
        if bpy.context.scene.arp_debug_mode:
            print("    Knee median point:", median_point[1])
            print("    Current thigh tail:",  get_edit_bone("thigh_ref" + used_side).tail[1])
        
        if get_edit_bone("thigh_ref" + used_side).tail[1] > median_point[1]:
            if bpy.context.scene.arp_debug_mode:
                print("    The knee is pointing backward, change that")
                
            get_edit_bone("thigh_ref" + used_side).tail[1] = median_point[1] + (median_point[1] - get_edit_bone("thigh_ref" + used_side).tail[1])*0.1
        
        if scene.arp_smart_sym:
            mirror_hack()
        
        if get_edit_bone("bot_bend_ref" + used_side):
            init_selection("bot_bend_ref"+used_side)
            bot_bend_ref = get_edit_bone("bot_bend_ref"+used_side)
            bot_auto = get_object("bot_empty_loc" + used_side + "_auto").location  
            bot_bend_ref.head = rig_matrix_world_inv @ bot_auto

            bot_bend_ref.tail = bot_bend_ref.head + (rig_matrix_world_inv @ vectorize3([0, foot_length/4, 0]))
                    
            if scene.arp_smart_sym:
                mirror_hack()
        
            if used_side == ".l":# one side only affect both
                #disable it by default
                auto_rig._disable_limb(self, bpy.context)
            
            
    #display all layers again           
    for i in range(0,31):   
        _layers[i] = True 
    
    
    # SPINE
    print("\n    matching spine...")
    init_selection("root_ref.x")
    root_ref = get_edit_bone("root_ref.x")
    root_auto = get_object("root_loc_auto").location  
    root_ref.head = rig_matrix_world_inv @ root_auto
    root_ref.tail = rig_matrix_world_inv @ get_object("spine_01_loc_auto").location
    
    init_selection("spine_01_ref.x")
    spine_01_ref = get_edit_bone("spine_01_ref.x")   
    spine_01_ref.tail = rig_matrix_world_inv @ get_object("spine_02_loc_auto").location
    
    init_selection("spine_02_ref.x")
    spine_02_ref = get_edit_bone("spine_02_ref.x")   
    spine_02_ref.tail = rig_matrix_world_inv @ get_object("neck_loc_auto").location 
    
    init_selection("neck_ref.x")
    neck_ref = get_edit_bone("neck_ref.x")
    neck_ref.head = rig_matrix_world_inv @ get_object("neck_loc_auto").location
    neck_ref.tail = rig_matrix_world_inv @ get_object("head_loc_auto").location
    
    init_selection("head_ref.x")
    head_ref = get_edit_bone("head_ref.x")
    head_ref.tail = rig_matrix_world_inv @ get_object("head_end_loc_auto").location
    
    # no more breasts in the default armature, generated on the fly
    """
    init_selection("breast_01_ref"+side)
    breast_01_ref = get_edit_bone("breast_01_ref"+side)
    breast_01_ref.head = rig_matrix_world_inv @ get_object("breast_01_loc_auto").location
    spine_02_ref = get_edit_bone("spine_02_ref.x")   
    breast_01_ref.tail = breast_01_ref.head + (vectorize3([0,0,(spine_02_ref.tail[2]-spine_02_ref.head[2])*0.3]))
    mirror_hack()
    
    init_selection("breast_02_ref"+side)
    breast_02_ref = get_edit_bone("breast_02_ref"+side)
    breast_02_ref.head = rig_matrix_world_inv @ get_object("breast_02_loc_auto").location
    spine_02_ref = get_edit_bone("spine_02_ref.x")   
    breast_02_ref.tail = breast_02_ref.head + vectorize3([0,0,(spine_02_ref.tail[2]-spine_02_ref.head[2])*0.3])
    mirror_hack()
    """
    
    for used_side in used_sides:
        print("\n    matching arms", used_side, "...")
        # ARMS
            # shoulder
        init_selection("shoulder_ref"+used_side)
        shoulder_ref = get_edit_bone("shoulder_ref"+used_side)   
        shoulder_ref.head = rig_matrix_world_inv @ get_object("shoulder_base_loc" + used_side + "_auto").location
        shoulder_ref.tail = rig_matrix_world_inv @ get_object("shoulder_loc" + used_side + "_auto").location        
        if scene.arp_smart_sym:
            mirror_hack()
        
            #arm
        init_selection("arm_ref"+used_side)
        arm_ref = get_edit_bone("arm_ref"+used_side)       
        arm_ref.tail = rig_matrix_world_inv @ get_object("elbow_loc" + used_side + "_auto").location
        if scene.arp_smart_sym:
            mirror_hack()
    
            #forearm
        init_selection("forearm_ref"+used_side)
        forearm_ref = get_edit_bone("forearm_ref"+used_side)       
        forearm_ref.tail = rig_matrix_world_inv @ get_object("hand_loc" + used_side + "_auto").location
        if scene.arp_smart_sym:
            mirror_hack()
            
            #hand
        init_selection("hand_ref"+used_side)
        hand_ref = get_edit_bone("hand_ref"+used_side)
    
                #check if fingers are detected
        if scene.arp_fingers_to_detect != 'NONE' and get_object("middle_bot" + used_side + "_auto") != None:
            hand_ref.tail = hand_ref.head + (rig_matrix_world_inv @ get_object("middle_bot" + used_side + "_auto").location - hand_ref.head)*0.6
            
        else:
            forearm_ref = get_edit_bone("forearm_ref"+used_side)
            hand_ref.tail = hand_ref.head + ((forearm_ref.tail - forearm_ref.head)/3)
        
            #hand roll  
            # get hand/x-axis angle
        hand_vec = hand_ref.y_axis
        hand_vec[1] = 0     
    
    
        # get the hand "normal" according to the pinky/index roots and place the cursor above to calculate the hand roll
        left_pos = None
        right_pos = None
    
        if bpy.data.objects.get("pinky_root" + used_side + "_auto"):
            left_pos = bpy.data.objects["pinky_root" + used_side + "_auto"].location
        elif bpy.data.objects.get("ring_root" + used_side + "_auto"):
            left_pos = bpy.data.objects["ring_root" + used_side + "_auto"].location
        
        if bpy.data.objects.get("index_root" + used_side + "_auto"):
            right_pos = bpy.data.objects["index_root" + used_side + "_auto"].location       
        
        
    
        if left_pos and right_pos:          
            hand_loc = bpy.data.objects["hand_loc" + used_side + "_auto"].location          
            hand_normal = cross(left_pos-right_pos, hand_loc-right_pos).normalized()
            if (used_side == ".r"):
                hand_normal *= -1           
            cursor_loc = hand_loc + vectorize3(hand_normal) * bpy.context.active_object.dimensions[0]               
            bpy.context.scene.cursor.location = cursor_loc          
            bpy.ops.armature.calculate_roll(type='CURSOR')          
            
        else:       
            bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')
            
        
        if scene.arp_smart_sym:
            mirror_hack()
    
        
        # FINGERS --------------------------------------------
        print("    matching fingers", used_side, "...")
        
        select_hands= ['hand_ref' + used_side]
        if len(used_sides) == 1:# set opposite side too if mirror is enabled
            select_hands.append('hand_ref.r')
        
        for hname in select_hands:
            # setting fingers is based on the current selected bone
            init_selection(hname)
                    
            # If fingers to detect is set to 1
            if scene.arp_fingers_to_detect == '1':
                auto_rig.set_fingers(False, True, False, False, False)
                        
            # If fingers to detect is set to 2
            if scene.arp_fingers_to_detect == '2':
                auto_rig.set_fingers(True, True, False, False, False)       
                
            # If fingers to detect is set to 4, enable all fingers but pinky
            if scene.arp_fingers_to_detect == '4':
                auto_rig.set_fingers(True, True, True, True, False) 
                
            #If fingers to detect is set to 5, enable all fingers
            if scene.arp_fingers_to_detect == '5':
                auto_rig.set_fingers(True, True, True, True, True)
        
        
        # make list of fingers bones
        finger_bones = []        
        init_selection("hand_ref" + used_side)
        bpy.ops.armature.select_similar(type='CHILDREN')
    
        for bone in bpy.context.active_object.data.edit_bones:
            if bone.select and bone.name != "hand_ref"+used_side:
                finger_bones.append(bone.name)  

        bpy.ops.armature.select_all(action='DESELECT')
        
        def get_saved_bone(bone_name):
            for b in scene.arp_fingers_init_transform:
                if b.name == bone_name:
                    return b
                    
            return None
            
        #reset fingers transforms if it's the second time the button is pressed
        if len(scene.arp_fingers_init_transform) > 0:
            for bone_name in finger_bones:
                current_bone = get_edit_bone(bone_name)
                try:
                    b = get_saved_bone(bone_name)
                    if b != None:
                        current_bone.head = b.head
                        current_bone.tail = b.tail
                        current_bone.roll = b.roll                          
                except:
                    pass
        
        #save initial fingers transform in the property collection if it's the first time the button is pressed
        for bone_name in finger_bones:
            current_bone = get_edit_bone(bone_name)
            # is the bone already saved?
            b = get_saved_bone(bone_name)
            # no, save it
            if b == None:
                item = scene.arp_fingers_init_transform.add()       
                item.name = bone_name  
                item.head = current_bone.head
                item.tail = current_bone.tail
                item.roll = current_bone.roll
        
    

            #root
        fingers = ["thumb", "index", "middle", "ring", "pinky"]    
            
        fingers_root = ["index1_base_ref"+used_side, "middle1_base_ref"+used_side, "ring1_base_ref"+used_side, "pinky1_base_ref"+used_side]
        
        found_fingers_loc = False
        
        if scene.arp_fingers_to_detect != 'NONE':
           
            auto_root = ["index_root" +  used_side + "_auto", "middle_root" + used_side + "_auto", "ring_root" + used_side + "_auto", "pinky_root" + used_side + "_auto"]
            
            #front view for correct roll from view
            bpy.ops.view3d.view_axis(type='FRONT')
            
            for i in range(0, len(fingers_root)):
                #if the detection marker exists
                if bpy.data.objects.get(auto_root[i]) != None:
                    
                    found_fingers_loc = True
                    
                    init_selection(fingers_root[i]) 
                    bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[fingers_root[i]].bone    
                    root_ref = get_edit_bone(fingers_root[i])
                    root_ref.head = rig_matrix_world_inv @ get_object(auto_root[i]).location
                    root_ref.tail = rig_matrix_world_inv @ get_object(fingers[i+1]+"_bot" + used_side + "_auto").location
                                    
                    
                    bpy.ops.object.mode_set(mode='POSE')
                    bpy.ops.pose.select_all(action='DESELECT')
                    bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[fingers_root[i]].bone
                    bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones["hand_ref" + used_side].bone
                    bpy.ops.object.mode_set(mode='EDIT')                
                    bpy.ops.armature.calculate_roll(type='ACTIVE') 
                
                    
                    if scene.arp_smart_sym:
                        mirror_hack()               
            
            
            for f in range(0,5):
                bpy.ops.armature.select_all(action='DESELECT')          
                
                
                #if the detection marker exists
                if bpy.data.objects.get(fingers[f]+"_bot" + used_side + "_auto") != None:
                
                    found_fingers_loc = True
                    
                    #bot
                    init_selection(fingers[f]+"1_ref"+used_side)         
                    finger_bot = get_edit_bone(fingers[f]+"1_ref"+used_side)
                    
                    if f != 0: #not thumb   
                        finger_bot.head = rig_matrix_world_inv @ get_object(fingers[f]+"_bot" + used_side + "_auto").location
                        finger_bot.tail = rig_matrix_world_inv @ get_object(fingers[f]+"_phal_2" + used_side + "_auto").location                                        
                        
                        # roll
                        bpy.ops.object.mode_set(mode='POSE')
                        bpy.ops.pose.select_all(action='DESELECT')
                        bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[fingers[f]+"1_ref"+used_side].bone
                        bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones["hand_ref" + used_side].bone
                        bpy.ops.object.mode_set(mode='EDIT')                
                        bpy.ops.armature.calculate_roll(type='ACTIVE') 
                                                        
                    
                    else:# thumb
                        finger_bot.head = rig_matrix_world_inv @ get_object(fingers[f]+"_root" + used_side + "_auto").location
                        finger_bot.tail = rig_matrix_world_inv @ get_object(fingers[f]+"_phal_2" + used_side + "_auto").location
                        bpy.ops.armature.calculate_roll(type='GLOBAL_NEG_Y')
                    
                    if scene.arp_smart_sym:
                        mirror_hack()
                    
                    #phal1
                    init_selection(fingers[f] + "2_ref" + used_side)
                    finger_phal_1 = get_edit_bone(fingers[f] + "2_ref" + used_side)
                    finger_phal_1.tail = rig_matrix_world_inv @ get_object(fingers[f] + "_phal_1" + used_side + "_auto").location
                                    
                    # roll
                    if f != 0: #not thumb
                                    
                        bpy.ops.object.mode_set(mode='POSE')
                        bpy.ops.pose.select_all(action='DESELECT')
                        bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[fingers[f]+"2_ref"+used_side].bone
                        bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones["hand_ref" + used_side].bone
                        bpy.ops.object.mode_set(mode='EDIT')                
                        bpy.ops.armature.calculate_roll(type='ACTIVE') 
                        
                    
                    else:# thumb
                        bpy.ops.armature.calculate_roll(type='GLOBAL_NEG_Y')
                    
                    if scene.arp_smart_sym:
                        mirror_hack()       
                    
                    
                    #phal2
                    init_selection(fingers[f]+"3_ref"+used_side)
                    finger_phal_2 = get_edit_bone(fingers[f]+"3_ref"+used_side)
                    finger_phal_2.tail = rig_matrix_world_inv @ get_object(fingers[f]+"_top" + used_side + "_auto").location
                    
                    # roll              
                    if f != 0: #not thumb
                                    
                        bpy.ops.object.mode_set(mode='POSE')
                        bpy.ops.pose.select_all(action='DESELECT')
                        bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones[fingers[f]+"3_ref"+used_side].bone
                        bpy.context.active_object.data.bones.active = bpy.context.active_object.pose.bones["hand_ref" + used_side].bone
                        bpy.ops.object.mode_set(mode='EDIT')                
                        bpy.ops.armature.calculate_roll(type='ACTIVE') 
                        
                    else:
                        bpy.ops.armature.calculate_roll(type='GLOBAL_NEG_Y')
                        
                    if scene.arp_smart_sym:
                        mirror_hack()       
                    
                    
                    
                
        if scene.arp_fingers_to_detect == 'NONE' or not found_fingers_loc:#no finger detection case      
                  
            
            # Offset all finger bones close the hand bone
                # calculate offset vector
            rig_scale = bpy.data.objects["rig"].scale[0]
            offset_vec = (get_edit_bone("hand_ref" + used_side).tail - get_edit_bone("index1_base_ref"+used_side).head)*rig_scale   

            for b in finger_bones:
                get_edit_bone(b).select = True
          
            bpy.ops.object.mode_set(mode='POSE') 
            bpy.ops.object.mode_set(mode='EDIT')           
            bpy.ops.transform.translate(value=(offset_vec), constraint_axis=(False, False, False), orient_type='GLOBAL', mirror=True, proportional='DISABLED')
            
            bpy.ops.armature.select_all(action='DESELECT')
            
    
    # FACIAL
    #Smart facial bones if any
    
    if bpy.data.objects.get("arp_facial_setup"):
        print("\n    matching smart facial...")
        #disable x-axis mirror edit
        bpy.context.active_object.data.use_mirror_x = False
        facial_markers = auto_rig_datas.facial_markers
        
        #enable ears and facial
        suffix, found_base = auto_rig.get_limb_suffix(".l", "ears")
        if not found_base:
            auto_rig.set_ears(2, side_arg=".l")     
        if not get_edit_bone("c_jawbone.x"):
            # make sure the head_ref bone is selected before setting the facial
            get_edit_bone("head_ref.x").select = True
            auto_rig.set_facial(True)
        #print(br)
        #match
        for _side in sides:
            for bone in facial_markers:
                e_bone = None       
                if bone[-2:] == ".x":                   
                    e_bone = get_edit_bone(bone[:-2]+"_ref"+".x")
                else:
                    e_bone = get_edit_bone(bone+"_ref"+_side)
                    
                if e_bone:
                    e_bone_vec = e_bone.tail - e_bone.head
                    v_index = facial_markers[bone]
                    vert_loc = arp_facial_setup.matrix_world @ arp_facial_setup.data.vertices[v_index].co
                
                    if _side == ".r":
                        vert_loc[0] *= -1
                        
                    if 'eyelid' in bone:
                        _eyeball_loc = eyeball_loc.copy()
                        if _side == ".r":
                            _eyeball_loc[0] = -abs(eyeball_loc[0])
                        else:
                            _eyeball_loc[0] = abs(eyeball_loc[0])
                            
                        e_bone.head = rig_matrix_world_inv @ _eyeball_loc
                        e_bone.tail = rig_matrix_world_inv @ vert_loc
                        
                    elif 'ear_01' in bone:
                        vert_ear2 = arp_facial_setup.matrix_world @ arp_facial_setup.data.vertices[facial_markers['ear_02']].co
                        if _side == ".r":
                            vert_ear2[0] *= -1
                        
                        mid = (vert_ear2 + vert_loc)*0.5
                        e_bone.head = rig_matrix_world_inv @ vert_loc                   
                        e_bone.tail = rig_matrix_world_inv @ mid 
                        
                                        
                    elif 'ear_02' in bone:
                        vert_ear1 = arp_facial_setup.matrix_world @ arp_facial_setup.data.vertices[facial_markers['ear_01']].co 
                        if _side == ".r":
                            vert_ear1[0] *= -1
                        mid = (vert_ear1 + vert_loc)*0.5
                        e_bone.head = rig_matrix_world_inv @ mid                    
                        e_bone.tail = rig_matrix_world_inv @ vert_loc 
                    else:               
                        e_bone.head = rig_matrix_world_inv @ vert_loc
                        e_bone.tail = e_bone.head + e_bone_vec
                        
                    if 'chin_0' in bone or 'cheek_inflate' in bone:#push back chin
                        push_vec = (e_bone.head - e_bone.tail)
                        e_bone.head += push_vec*0.5
                        e_bone.tail += push_vec*0.5
            
            
            #eyebrow master
            eyebrow_full = get_edit_bone("eyebrow_full_ref"+_side)
            eybrow_02 = get_edit_bone("eyebrow_02_ref"+_side)
            eyebrow_full.head = eybrow_02.tail + (eybrow_02.tail - eybrow_02.head) * 2
            eyebrow_full.tail = eyebrow_full.head + (eybrow_02.tail - eybrow_02.head)
            
            #main eyelids
            if _side == ".r":
                _eyeball_loc[0] = -abs(eyeball_loc[0])
            else:
                _eyeball_loc[0] = abs(eyeball_loc[0])
                
            eyeball_loc_final = rig_matrix_world_inv @ _eyeball_loc
            
                
                #top
            eyelid_top = get_edit_bone("eyelid_top_ref"+_side)              
            eyelid_top.head = eyeball_loc_final
            eyelid_top.tail = get_edit_bone("eyelid_top_02_ref"+_side).tail
            eyelid_top.tail[0] = eyelid_top.head[0]
            eyelid_top.roll = math.radians(180)
            
                #bottom
            eyelid_bot = get_edit_bone("eyelid_bot_ref"+_side)              
            eyelid_bot.head = eyeball_loc_final
            eyelid_bot.tail = get_edit_bone("eyelid_bot_02_ref"+_side).tail
            eyelid_bot.tail[0] = eyelid_bot.head[0]
            eyelid_bot.roll = math.radians(180)
            
            #eye offset
            eye_offset = get_edit_bone("eye_offset_ref"+_side)
            eye_offset.head = eyeball_loc_final
            eye_offset.tail = eyelid_bot.tail
            eye_offset.tail[2] = eye_offset.head[2]
            
            #lips corner mini
            lips_corner = get_edit_bone("lips_smile_ref"+_side)
            lips_cm = get_edit_bone("lips_corner_mini_ref" + _side)
            lips_cm.head = lips_corner.head
            lips_cm.tail = lips_corner.head + (lips_corner.tail - lips_corner.head)*0.5
        
        
        #END for _side in sides
        
        #nose 01 tweak
        nose_01 = get_edit_bone("nose_01_ref.x")
        nose_01.head[1] = ((rig_matrix_world_inv @ _eyeball_loc)[1] + nose_01.tail[1])*0.5
        nose_01.tail = nose_01.head + (nose_01.tail - nose_01.head)*0.3
        
        #nose 02        
        nose_02 = get_edit_bone("nose_02_ref.x")    
        nose_02.head = nose_01.tail
        nose_02.tail = nose_02.head + (nose_01.tail - nose_01.head)
        
        #nose 03 tweak
        nose_03 = get_edit_bone("nose_03_ref.x")    
        transf_vec = nose_03.head - nose_03.tail
        nose_03.head += transf_vec*0.5
        nose_03.tail += transf_vec*0.5
        
        #lips roll      
        lips_roll_t = get_edit_bone("lips_roll_top_ref.x")
        lips_top = get_edit_bone("lips_top_ref.x")      
        initial_vec = lips_roll_t.tail - lips_roll_t.head
        mid_vec = (nose_02.tail + lips_top.head) * 0.5
        lips_roll_t.head = mid_vec
        lips_roll_t.tail = initial_vec + lips_roll_t.head
        
        lips_roll_b = get_edit_bone("lips_roll_bot_ref.x")
        lips_bot = get_edit_bone("lips_bot_ref.x")      
        initial_vec = lips_roll_b.tail - lips_roll_b.head
        mid_vec = (get_edit_bone("chin_01_ref.x").head + lips_bot.head) * 0.5
        lips_roll_b.head = mid_vec
        lips_roll_b.head[1] = lips_roll_t.head[1]
        lips_roll_b.tail = initial_vec + lips_roll_b.head
            
        #jaw
        jaw_bone = get_edit_bone("jaw_ref.x")
        head_ref = get_edit_bone("head_ref.x")
        chin_02_ref = get_edit_bone("chin_02_ref.x")
        jaw_bone.head = head_ref.head + (head_ref.tail - head_ref.head)*0.2 + (chin_02_ref.head - head_ref.head)*0.2
        jaw_bone.tail = chin_02_ref.head
        
        #teeth-tong
        teeth_tong = ["teeth_top_ref.l", "teeth_top_ref.x", "teeth_top_ref.r", "teeth_bot_ref.l", "teeth_bot_ref.x", "teeth_bot_ref.r", "tong_01_ref.x", "tong_02_ref.x", "tong_03_ref.x"]      
        nose_lips_point = (lips_top.head + nose_01.tail)*0.5
        transf_vec = nose_lips_point - (get_edit_bone("teeth_top_ref.x").tail)
        transf_vec +=  (jaw_bone.head - lips_top.head)*0.2
        
        for bone in teeth_tong:
            if not "tong" in bone or 'tong_03' in bone:
                get_edit_bone(bone).head += transf_vec
                get_edit_bone(bone).tail += transf_vec
            else:
                get_edit_bone(bone).head += transf_vec
                
                
        
    #END if arp_facial_setup
    
    else:
        print("\n    matching default facial...")
        
        # Disable facial bones for now
        auto_rig.set_facial(False)      
        
        """
        #Select facial bones
        bpy.ops.armature.select_all(action='DESELECT')

        for b in auto_rig_datas.facial_ref:     
            if b[-2:] == ".x":
                if get_edit_bone(b) != None:
                    get_edit_bone(b).select = True
            else:               
                for side in [".l", ".r"]:
                    if get_edit_bone(b + side) != None:
                        get_edit_bone(b + side).select = True
            
        bpy.ops.object.mode_set(mode='POSE') 
        bpy.ops.object.mode_set(mode='EDIT')            
        

        # Offset all facial bones close the head ref bone
            # calculate offset vector
        rig_scale = bpy.data.objects["rig"].scale[0]
        head_ref = get_edit_bone("head_ref.x")
        head_length = head_ref.tail[2] - head_ref.head[2]
        offset_pos = get_edit_bone("neck_ref.x").tail + vectorize3([0,-head_length*2,0])
        offset_vec = (offset_pos - get_edit_bone("nose_01_ref.x").head)
        
        #jawbone height
        if bpy.data.objects.get("chin_loc"):        
            offset_vec[2] = (rig_matrix_world_inv @ bpy.data.objects["chin_loc"].location)[2] - get_edit_bone("jaw_ref.x").tail[2]
        
        offset_vec *= rig_scale         

        #apply offset
        bpy.ops.transform.translate(value=(offset_vec), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=True, proportional='DISABLED')
        
        #check Use Chin for skinning
        scene.arp_bind_chin = True
    
        # Disable facial bones for now
        auto_rig.set_facial(False)      
        """
    
    
    #display layer 17 only          
    for i in range(0,31):
        if i != 17:
            _layers[i] = False 
    
    
        
    print("\n    matching end.")
    bpy.ops.armature.select_all(action='DESELECT')

    
        
    
def _add_marker(name, enable_mirror):
    
    body = bpy.data.objects[bpy.context.scene.arp_body_name]
    body_height = body.dimensions[2]
    scaled_radius = 0.01#body_height/20
    
    #apply mesh rotation
    set_active_object(body.name)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    bpy.ops.object.mode_set(mode='OBJECT')
    
    # create an empty parent for the markers
    #if it already exists, don't create it
    if not bpy.data.objects.get("arp_markers"):     
        bpy.ops.object.empty_add(type='PLAIN_AXES', radius = scaled_radius, view_align=False, location=(0,0,0), rotation=(0, 0, 0))   
        bpy.context.active_object.name = "arp_markers"
    
    # create the marker if not exists already
    if bpy.data.objects.get(name+"_loc"): #it already exists
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects[name+"_loc"].select_set(state=1)
        set_active_object(name+"_loc")
    else:
        #create it
        bpy.ops.object.empty_add(type='PLAIN_AXES', radius = scaled_radius, view_align=False, location=(0,0,0), rotation=(0, 0, 0))  
        bpy.context.active_object.empty_display_type = 'CIRCLE'
        bpy.context.active_object.empty_display_size = 0.01   
        # rename it     
        bpy.context.active_object.name = name + "_loc"
        # parent it
        bpy.context.active_object.parent = bpy.data.objects["arp_markers"]
        #enable xray
        bpy.context.active_object.show_in_front = True
        
        
        if name == "shoulder" or name == "hand" or name == "foot":
            # add limit constraint          
            cns = bpy.context.active_object.constraints.new('LIMIT_LOCATION')
            cns.use_min_x = True
            cns.use_transform_limit = True          
            
            # create mirror markers with constraint
            bpy.ops.object.empty_add(type='PLAIN_AXES', radius = scaled_radius, view_align=False, location=(0,0,0), rotation=(0, 0, 0))  
            bpy.context.active_object.empty_display_type = 'CIRCLE'
            bpy.context.active_object.empty_display_size = scaled_radius
            
            # rename it     
            bpy.context.active_object.name = name + "_loc_sym"
            
            # parent it
            bpy.context.active_object.parent = bpy.data.objects["arp_markers"]
            
            #enable xray
            bpy.context.active_object.show_in_front = True
            
            #add mirror constraint          
            cns = bpy.context.active_object.constraints.new('COPY_LOCATION')
            cns.target = bpy.data.objects[name+"_loc"]
            cns.invert_x = True
            
            if enable_mirror == False:
                cns.influence = 0.0
            
            #add limit constraint           
            cns = bpy.context.active_object.constraints.new('LIMIT_LOCATION')
            cns.use_max_x = True
            cns.use_transform_limit = True          
                
            
            #select back the main empty
            set_active_object(name+"_loc")
            
    # markers specific options
    if bpy.context.scene.arp_smart_sym:
        if name == "neck" or name == "root" or name == "chin":
            bpy.context.active_object.lock_location[0] = True
    
def clamp_max(value, max):
    if value > max:
        return max
    else:
        return value    
       
          
def _auto_detect(self):     
    
    scene = bpy.context.scene
    print("\nAuto-Detecting... \n")

    #get character mesh name
    body = bpy.data.objects[scene.arp_body_name]
    
    #apply transforms
    bpy.ops.object.select_all(action='DESELECT')
    set_active_object(body.name)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    #remove shape keys if any
    try:
        bpy.ops.object.shape_key_remove(all=True)
    except:
        pass

    
    #get its dimension
    body_width = body.dimensions[0]
    body_height = body.dimensions[2]
    body_depth = body.dimensions[1]
    
    hand_offset = [0,0,0]

    # create an empty group for the auto detected empties
        #delete existing if any
    for obj in bpy.data.objects:
        if obj.type == 'EMPTY':         
            if 'auto_detect_loc' in obj.name:
                if len(obj.children) == 0:              
                    bpy.data.objects.remove(obj, do_unlink=True)
                    
                    
    _delete_detected()      
    
        # create it
    bpy.ops.object.empty_add(type='PLAIN_AXES', radius = 0.01, view_align=True, location=(0,0,0), rotation=(0, 0, 0))   
    bpy.context.active_object.name = "auto_detect_loc"
    bpy.context.active_object.parent = bpy.data.objects["arp_temp_detection"]
    bpy.ops.object.select_all(action='DESELECT')

    # ARMS DETECTION -----------------------------------------------------------------------------------------------------------
    
    # get the loc guides    
    hand_loc_l = bpy.data.objects["hand_loc"]
    hand_loc_r = bpy.data.objects["hand_loc_sym"]   
    
    wrist_bound_front_l = None
    wrist_bound_back_l = None
    wrist_bound_front_r = None
    wrist_bound_back_r = None
    hand_empty_loc_l = None
    hand_empty_loc_r = None
    
    hand_markers = [hand_loc_l]
    
    if not scene.arp_smart_sym:
        hand_markers.append(hand_loc_r)
    
    # iterate on left and right sides
    for side_idx, hand_marker in enumerate(hand_markers):
    
        
        if side_idx == 0:
            print('\n[Left arm detection...]')      
        if side_idx == 1:
            print('\n[Right arm detection...]')     
            
        set_active_object(body.name)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='EDIT')
        #check for hidden vertices, can't be accessed if hidden
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        #get the mesh (in edit mode only)
        mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
        
        # HAND DETECTION ----------
    
        if bpy.context.scene.arp_debug_mode:
            print("    Find hands boundaries...\n")     
        
        print("    Find wrist...\n")

        #find wrist center and bounds by raycast
        wrist_bound_back = None
        my_tree = BVHTree.FromBMesh(mesh)       
    
        ray_origin = hand_marker.location + vectorize3([0, -body_depth, 0])
        ray_dir = vectorize3([0, body_depth*4, 0])
        
        hit, normal, index, distance = my_tree.ray_cast(ray_origin, ray_dir, ray_dir.magnitude)   
        
        if hit == None or distance < 0.001:     
            print('    Could not find wrist front, marker out of mesh') 
        else:   
            wrist_bound_front = hit[1]
            have_hit = True
            last_hit = hit
            #iterate if multiples faces layers
            while have_hit:
                have_hit = False
                hit, normal, index, distance = my_tree.ray_cast(last_hit+vectorize3([0,0.001,0]), ray_dir, ray_dir.magnitude) 
                if hit != None:                     
                    have_hit = True
                    last_hit = hit
                    
            wrist_bound_back = last_hit[1]
        

        if wrist_bound_back == None:        
            self.report({'ERROR'}, "Could not find the wrist, marker out of mesh?")
            self.error_during_auto_detect = True
            return
            
        hand_loc_x = hand_marker.location[0]
        hand_loc_y = wrist_bound_back + ((wrist_bound_front - wrist_bound_back)*0.4)
        hand_loc_z = hand_marker.location[2]    
        
        # Sides naming handling
        suff = ""
        side = ".l"     
        if side_idx == 0:
            hand_empty_loc_l = [hand_loc_x, hand_loc_y, hand_loc_z]
        if side_idx == 1:
            hand_empty_loc_r = [hand_loc_x, hand_loc_y, hand_loc_z]
            suff = "_sym"
            side = ".r"
    
    
        # ARMS -------
        
        print("    Find arms...\n")
        
        shoulder_loc = bpy.data.objects["shoulder_loc"+suff]    
        shoulder_front = None
        shoulder_back = None
        
        if bpy.context.scene.arp_debug_mode:
            print("    Find shoulders...\n")    
    
        ray_origin = shoulder_loc.location + vectorize3([0, -body_depth*2, 0])
        ray_dir = vectorize3([0, body_depth*4, 0])
        
        hit, normal, index, distance = my_tree.ray_cast(ray_origin, ray_dir, ray_dir.magnitude)   
        
        if hit == None or distance < 0.001:     
            print('    Could not find shoulder, marker out of mesh?') 
        else:   
            shoulder_front = hit[1]
            have_hit = True
            last_hit = hit
            #iterate if multiples faces layers
            while have_hit:
                have_hit = False
                hit, normal, index, distance = my_tree.ray_cast(last_hit+vectorize3([0,0.001,0]), ray_dir, ray_dir.magnitude) 
                if hit != None:                     
                    have_hit = True
                    last_hit = hit
                    
            shoulder_back = last_hit[1]
        
        
        
        shoulder_empty_loc = [shoulder_loc.location[0], shoulder_back + (shoulder_front-shoulder_back)*0.4, shoulder_loc.location[2]]       
        
        # Shoulder_base
        shoulder_base_loc = [shoulder_empty_loc[0]/4, shoulder_empty_loc[1], shoulder_empty_loc[2]]
       
        
        # Elbow
        _hand_empty_loc = hand_empty_loc_l
        if side_idx == 1:
            _hand_empty_loc = hand_empty_loc_r
            
        elbow_empty_loc = [(shoulder_empty_loc[0] + _hand_empty_loc[0])/2, 0, (shoulder_empty_loc[2] + _hand_empty_loc[2])/2]
         
         
            # Find the elbow boundaries
            
        if bpy.context.scene.arp_debug_mode:
            print("    Find elbow boundaries...\n")
            
        clear_selection()
        elbow_selection = []
        has_selected_v = False
        sel_rad = body_width / 20
        
        while has_selected_v == False:
            for v in mesh.verts:    
                if tolerance_check_2(v.co, elbow_empty_loc, 0, 2, sel_rad, side):
                    v.select = True  
                    has_selected_v = True  
                    elbow_selection.append(v.index)
                    
            if has_selected_v == False:
                sel_rad *= 2            
               
        
        elbow_back = -1000
        elbow_front = 1000
        
        for ve in elbow_selection:        
            mesh.verts.ensure_lookup_table() 
            vert_y = mesh.verts[ve].co[1]        
            #front    
            if vert_y < elbow_front:
                elbow_front = vert_y
            # back
            if vert_y > elbow_back:
                elbow_back = vert_y        
         
        elbow_empty_loc[1] = elbow_back + (elbow_front - elbow_back)*0.3        
        elbow_center = elbow_empty_loc.copy()
        elbow_center[1] = elbow_back + (elbow_front - elbow_back)*0.5
        
        # create the empties       
        bpy.ops.object.mode_set(mode='OBJECT')      
            
        create_empty_loc(0.04, shoulder_empty_loc, "shoulder_loc" + side)
        create_empty_loc(0.04, shoulder_base_loc, "shoulder_base_loc" + side)
        create_empty_loc(0.04, elbow_empty_loc, "elbow_loc" + side)
        bpy.ops.object.select_all(action='DESELECT')

    
                
        # FINGERS DETECTION ---------------------------------------------------------------------------------------------
        
        print("    Find fingers...\n")  

        # Initialize the hand rotation by creating a new hand mesh horizontally aligned
        #find the arm angle
        
        shoulder_pos = bpy.data.objects["shoulder_loc"+suff].location   
        
        # Opposite angle for the right side
        fac=1
        if side_idx == 1:
            fac = -1
        
        # X angle
        arm_angle = Vector((hand_marker.location - shoulder_pos)).angle(Vector((1*fac,0,0)))                
            
        # Z forearm angle
        hand_loc_temp = _hand_empty_loc.copy()
        hand_loc_temp[2] = 0        
        elbow_center[2] = 0
    
        forearm_angle_z = Vector((vectorize3(hand_loc_temp) - vectorize3(elbow_center))).angle(Vector((1*fac,0,0)))
    
        if bpy.context.scene.arp_debug_mode:
            print('      Arm Angle:', math.degrees(arm_angle))
            print('      Arm Angle Z:', math.degrees(forearm_angle_z))
            
        self.arm_angle = math.degrees(arm_angle)
                
    
        body.hide_select = False
        bpy.ops.object.mode_set(mode='OBJECT')
        set_active_object(body.name)
        
        bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')      
        
        bpy.context.active_object.name = 'arp_hand_aligned'         
        
        bpy.context.active_object.parent = bpy.data.objects["arp_temp_detection"]
        
        
        # create a selection helper transform
        rot_fac = 1
        if side_idx == 1:
            rot_fac = -1
        bpy.ops.mesh.primitive_plane_add(size=1, view_align=True, enter_editmode=False, location= hand_marker.location , rotation=(0, arm_angle*rot_fac, -forearm_angle_z*rot_fac))     
        bpy.context.active_object.name = "arp_hand_transform"       
        bpy.context.active_object.parent = bpy.data.objects["arp_temp_detection"]
        hand_transf = bpy.data.objects["arp_hand_transform"]
        matrix_sel = hand_transf.matrix_world
        
        set_active_object("arp_hand_aligned")
        
                
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
        
        # select the hand according to the selection helper
        for v in mesh.verts:    
            if side_idx == 0:
                if (matrix_sel.inverted() @ v.co)[0] < 0.0:             
                    v.select = True
            if side_idx == 1:
                if (matrix_sel.inverted() @ v.co)[0] > 0.0:             
                    v.select = True
        
        
        
        # delete other verts
            
        bpy.ops.mesh.delete(type='VERT')
        
        if bpy.context.scene.arp_debug_mode:
            print("    Remesh...")
            # Remesh
        bpy.ops.object.mode_set(mode='OBJECT')
        mod = bpy.context.active_object.modifiers.new('remesh', 'REMESH')
        mod.mode = 'SMOOTH'
        
        # it's best to set the remesh definition according the the mesh dimensions
        if bpy.context.active_object.dimensions[0] < (body_width/3):# generally, t-pose
            remesh_def = bpy.context.scene.arp_smart_remesh - 2
        else:# a-pose
            remesh_def = bpy.context.scene.arp_smart_remesh
        
    
        mod.octree_depth = remesh_def
        mod.use_remove_disconnected = True
        mod.threshold = 0.032
        
        bpy.ops.object.convert(target='MESH')
        
        
            # select the closest point to the wrist marker
        if bpy.context.scene.arp_debug_mode:
            print("    Select closest point to the wrist")
        bpy.ops.object.mode_set(mode='EDIT')
        obj = bpy.context.active_object
        mesh = obj.data
        size = len(mesh.vertices)
        kd = mathutils.kdtree.KDTree(size)
    
        for vi, v in enumerate(mesh.vertices):
            kd.insert(v.co, vi)
        
        kd.balance()    
        
        co, index, dist = kd.find(_hand_empty_loc)
        
        if index:
            b_mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
            b_mesh.verts.ensure_lookup_table() 
            b_mesh.verts[index].select = True
        else:
            print("Too low poly, could not find the wrist vertices")
            scene.arp_fingers_to_detect = 'NONE'
            
        bpy.ops.mesh.select_linked(delimit=set())
        bpy.ops.mesh.select_all(action='INVERT')    
        
        bpy.ops.mesh.delete(type='VERT')    
    
            #save current pivot mode
        pivot_mod = bpy.context.scene.tool_settings.transform_pivot_point
        
            #change for cursor      
        bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        bpy.context.scene.cursor.location = shoulder_pos
    
        bpy.ops.mesh.select_all(action='SELECT')
            #rotate the hand to horizontal  
        bpy.ops.transform.rotate(value=arm_angle*rot_fac, orient_axis='Y', constraint_axis=(False, False, False), orient_type='GLOBAL', mirror=False, proportional='DISABLED')
     
    
        if scene.arp_fingers_to_detect != 'NONE' :
        
            print("    Detecting fingers", side, "...")
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            bpy.ops.object.select_all(action='DESELECT')    
            set_active_object('hand_loc'+suff)
            
            #rotate the marker horizontal
            bpy.ops.transform.rotate(value=arm_angle*rot_fac, orient_axis='Y', constraint_axis=(False, False, False), orient_type='GLOBAL', mirror=False, proportional='DISABLED')
          
            set_active_object('arp_hand_aligned')
            bpy.ops.object.mode_set(mode='EDIT')
            
            # smooth a little
            bpy.ops.mesh.select_all(action='SELECT')    
            bpy.ops.mesh.vertices_smooth(repeat=6, factor=1.0)
            
            
            bpy.ops.mesh.select_all(action='DESELECT')  
            bpy.ops.object.mode_set(mode='OBJECT')
            hand_obj = bpy.data.objects["arp_hand_aligned"]

            p_coords=[]

            if bpy.data.objects.get("arp_part_verts"):
                bpy.data.objects.remove(bpy.data.objects["arp_part_verts"], do_unlink=True)
                
            print("\n    Generating particles...")
            # create the particles
            if len(hand_obj.particle_systems) != 0:
                hand_obj.modifiers.remove(hand_obj.modifiers[0])
                
            hand_obj.modifiers.new("part", type='PARTICLE_SYSTEM')
            bpy.context.scene.update()
            hand_obj_eval = bpy.context.depsgraph.objects.get(hand_obj.name, None)
            if hand_obj_eval:
                ps = hand_obj_eval.particle_systems[0]
            else:
                print("Error, could not evaluate the hand_obj object in depsgraph")
            settings = ps.settings
            settings.frame_start = 0
            settings.frame_end = 0
            settings.count = 1600
            settings.emit_from = 'VOLUME'
            settings.distribution = 'JIT'
            settings.physics_type = 'NO'    
            settings.render_type = 'HALO'
            settings.display_size = 0.005
            settings.lifetime = 100000          
            
            # update
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.object.mode_set(mode='OBJECT')
            ps = hand_obj_eval.particle_systems[0]             
            
            # bake to vertices
            bpy.ops.mesh.primitive_plane_add(size=100, view_align=True, enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0))
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.delete(type='VERT')
            bpy.context.active_object.name = "arp_part_verts"
            arp_part_verts = bpy.data.objects["arp_part_verts"]

                # create verts
            b_mesh = bmesh.from_edit_mesh(bpy.context.active_object.data) 
                
                # store the particles loc       
            for p in ps.particles:              
                b_mesh.verts.new(p.location)
            
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            
                # delete particles
            hand_obj.modifiers.remove(hand_obj.modifiers[0]) 
                
                # merge to main object
            bpy.ops.object.select_all(action='DESELECT')
            set_active_object("arp_part_verts")
            
            set_active_object(hand_obj.name)
            bpy.ops.object.join()
            
            print("    Centering particles...")

            bpy.ops.object.mode_set(mode='EDIT')

            b_mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)

            my_tree = BVHTree.FromBMesh(b_mesh)
            
            ray_dir_z = Vector((0,0,100))
            ray_dir_x = Vector((100,0,0))
            ray_dir_y = Vector((0,100,0))

            b_mesh.verts.ensure_lookup_table()
            
            bpy.data.objects["arp_hand_transform"].location = [0,0,0]
                
            bpy.context.scene.update()
            matrix_sel1 = bpy.data.objects["arp_hand_transform"].matrix_world
            
            # 2 engines
            centering_engine = 1
            dist_fac = 1
            
            # No centering engine for 1 finger detection. Only raycast detection.
            if bpy.context.scene.arp_fingers_to_detect == '1':              
                centering_engine = -1
            
            if centering_engine == 0:

                for vert in b_mesh.verts:
                    if vert.select:
                        
                        for iter in range(0,10):
                        
                            hit_x = None
                            hit_negx = None
                            hit_y = None
                            hit_negy = None
                            hit_z = None
                            hit_negz = None
                            
                            ray_origin = vert.co          
                            
                            hit, normal, index, distance = my_tree.ray_cast(ray_origin, ray_dir_x, 100000) 
                            if hit != None:
                                hit_x = hit
                            
                            hit, normal, index, distance = my_tree.ray_cast(ray_origin,-ray_dir_x, 100000) 
                            if hit != None:
                                hit_negx = hit
                                
                            hit, normal, index, distance = my_tree.ray_cast(ray_origin,ray_dir_y, 100000) 
                            if hit != None:
                                hit_y = hit
                                
                            hit, normal, index, distance = my_tree.ray_cast(ray_origin,-ray_dir_y, 100000) 
                            if hit != None:
                                hit_negy = hit
                                
                            hit, normal, index, distance = my_tree.ray_cast(ray_origin,ray_dir_z, 100000) 
                            if hit != None:
                                hit_z = hit
                                
                            hit, normal, index, distance = my_tree.ray_cast(ray_origin,-ray_dir_z, 100000) 
                            if hit != None:
                                hit_negz = hit
                               
                            if hit_x != None and hit_y != None and hit_z != None and hit_negx != None and hit_negy != None and hit_negz != None: 
                                x_magn = (hit_x - hit_negx).magnitude
                                y_magn = (hit_y - hit_negy).magnitude
                                z_magn = (hit_z - hit_negz).magnitude
                                
                                x = (hit_x + hit_negx)/2              
                                y = (hit_y + hit_negy)/2              
                                z = (hit_z + hit_negz)/2             
                                
                                bigger = ""
                                
                                if x_magn > y_magn and x_magn > z_magn:
                                    bigger = "x"
                                if y_magn > x_magn and y_magn > z_magn:
                                    bigger = "y"
                                if z_magn > x_magn and z_magn > y_magn:
                                    bigger = "z"                            
                                
                                                 
                                if bigger == "x":       
                                    if y_magn > dist_fac * (bpy.context.active_object.dimensions[1]/bpy.context.scene.arp_finger_thickness):
                                        # delete the vert in the palm
                                        b_mesh.verts.remove(vert)
                                        break
                                    else:   
                                        # others are centered
                                        vert.co = Vector((vert.co[0], y[1], z[2]))
                                if bigger == "y":     
                                    if y_magn > dist_fac * (bpy.context.active_object.dimensions[1]/bpy.context.scene.arp_finger_thickness):
                                        # delete the vert in the palm
                                        b_mesh.verts.remove(vert)
                                        break
                                    else:
                                        # others are centered
                                        vert.co = Vector((x[0], vert.co[1], z[2]))
                                    
                                if bigger == "z":
                                     # try to get rid of the vertices in the palm
                                    vert.co = Vector((x[0],y[1],vert.co[2]))
                                    
                            else:
                                # vert too close to the surface, delete it
                                b_mesh.verts.remove(vert)
                                break
                                
                        
            if centering_engine == 1:
                
                # Build the KD Tree used to find the nearest vert to a given one
                size = len(b_mesh.verts)
                kd = mathutils.kdtree.KDTree(size)
                    
                for vi, v in enumerate(b_mesh.verts):
                    kd.insert(v.co, vi)
                        
                kd.balance() 

                
                def filter_vert_search(_index):    
                    searched_vert = b_mesh.verts[_index]
                    return len(searched_vert.link_edges) > 0 and _index != vert.index

                vert_to_del = []            
                        
                
                for vert in b_mesh.verts:    
                    for iter in range(0, 7):
                        if vert.select and not vert in vert_to_del:           
                            
                            # look for the nearest vert on mesh and get his normal
                            pos, idx, dist = kd.find(vert.co, filter=filter_vert_search)
                            
                            if pos != None:
                                v_norm = b_mesh.verts[idx].normal
                              
                                # Cast a ray from this vert, normal direction
                                hit, normal, index, distance = my_tree.ray_cast(pos -v_norm*0.0001, -v_norm, 100000) 
                                if hit != None:             
                                 
                                    vert.co = (hit + pos)/2
                                    
                                    # delete verts in the palm
                                    y_dir = matrix_sel1 @ Vector((0,1,0))
                                    y_ndir = matrix_sel1 @ Vector((0,-1,0))
                                    #x_dir = matrix_sel1 @ Vector((1,0,0))
                                    #x_ndir = matrix_sel1 @ Vector((-1,0,0))
                                
                                    y_hit, y_normal, y_index, y_distance = my_tree.ray_cast(vert.co, y_dir, 100000) 
                                    ny_hit, ny_normal, ny_index, ny_distance = my_tree.ray_cast(vert.co, y_ndir, 100000) 
                                    
                                    #x_hit, x_normal, x_index, x_distance = my_tree.ray_cast(vert.co, x_dir, 100000) 
                                    #nx_hit, nx_normal, nx_index, nx_distance = my_tree.ray_cast(vert.co, x_ndir, 100000)
                                    
                                    if y_hit and ny_hit:# and x_hit and nx_hit:
                                        y_magn = y_distance + ny_distance
                                        #x_magn = x_distance + nx_distance
                                        
                                        dist_max = dist_fac * (bpy.context.active_object.dimensions[1]/bpy.context.scene.arp_finger_thickness)
                                        
                                        if y_magn > dist_max:# and x_magn > dist_max:
                                            vert_to_del.append(vert)                        
                                
                                
                            else:
                                # invalid, no close vert could be found                             
                                vert_to_del.append(vert)                
                                        
                        
                
                for vert in vert_to_del:   
                    b_mesh.verts.remove(vert)   
                
                
            
            
            # Remove double to get a smooth distribution of the vertices            
            bpy.context.active_object.data.update() 
            bpy.ops.mesh.remove_doubles(threshold=bpy.context.active_object.dimensions[0]/40)
            
            def get_index(list, value):
                # return the index of a vertice from its position
                for _i, j in enumerate(list):
                    if j == value:
                        return _i
                        
            # Separate the longer finger tip vertice as a new vert, if fingers to detect == 1 or 2
            if bpy.context.scene.arp_fingers_to_detect == '1' or bpy.context.scene.arp_fingers_to_detect == '2':
                b_mesh.verts.ensure_lookup_table()
                vert_coords1 = []
                for vert in b_mesh.verts:
                    vert_coords1.append(Vector((vert.co[0], vert.co[1], vert.co[2])))
                
                # Get the longer finger tip             
                coords_sorted1 = sorted(vert_coords1, reverse=True, key=itemgetter(0))
                if side_idx == 1:
                    coords_sorted1 = sorted(vert_coords1, reverse=False, key=itemgetter(0))     
                
                # Copy the vert (original is deleted after)
                new_vert = b_mesh.verts.new(coords_sorted1[0])
                new_vert.select = True
            
                
            if bpy.context.scene.arp_debug_mode:        
                print("\n    Creating edges...")
    
            
            
            hand_obj = bpy.data.objects[bpy.context.active_object.name]

            # separate the dots into a new object
            if bpy.data.objects.get("arp_part_verts") == None:
                bpy.ops.object.mode_set(mode='EDIT')
                
                try:
                    bpy.ops.mesh.separate(type="SELECTED")
                    bpy.ops.object.mode_set(mode='OBJECT')
                    current_obj = bpy.context.active_object.name
                    bpy.ops.object.select_all(action='DESELECT')
                    set_active_object(current_obj+".001")
                    bpy.context.active_object.name = "arp_part_verts"
                    
                except:# Error, no vertices have been generated. Probably due to wrong fingers detection amount (look for 5 fingers for mittens or box gloves instead of 1...)
                    print("    Fingers detection on side", side, "failed, particle generation failed. Probably due to wrong fingers detection parameters (look for 5 fingers instead of 1...)")
                    if side_idx == 0:
                        self.fingers_detection_success_l = False
                    if side_idx == 1:
                        self.fingers_detection_success_r = False
                
                
                
                
            else:
                set_active_object("arp_part_verts")
            
            if (self.fingers_detection_success_l and side_idx == 0) or (self.fingers_detection_success_r and side_idx == 1):
                obj = bpy.context.active_object

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')        

                bpy.ops.mesh.delete(type='EDGE_FACE')
                bpy.ops.mesh.select_all(action='DESELECT')

                b_mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
                b_mesh.verts.ensure_lookup_table() 
            
                fingers_total = int(bpy.context.scene.arp_fingers_to_detect)
        
                restrict_edgify_half_hand = False
            
                if fingers_total <= 2:
                    restrict_edgify_half_hand = True
                
                # Build the vertices coords list (centered verts cloud, if more than 2 fingers to detect)
                vert_coords = []
                b_mesh.verts.ensure_lookup_table()
                for vert in b_mesh.verts:
                    vert_coords.append(matrix_sel1.inverted() @ Vector((vert.co[0], vert.co[1], vert.co[2])))             
                
                # Get the longer finger tip
                    # Sort the list by X values to get the right boundary vert          
                coords_sorted = sorted(vert_coords, reverse=True, key=itemgetter(0))
                if side_idx == 1:
                    coords_sorted = sorted(vert_coords, reverse=False, key=itemgetter(0))
                    
                    # Get the index in the actual vert list     
                vert_tip = get_index(vert_coords, coords_sorted[0])
                
                if bpy.context.scene.arp_debug_mode:
                    print("    vert_tip", vert_tip, coords_sorted[0])
                    
                bpy.ops.mesh.select_all(action='DESELECT')          
                b_mesh.verts[vert_tip].select = True
                
                first_finger_tip = vert_tip
                
                if bpy.context.scene.arp_debug_mode:
                    print("    Found first finger vert", vert_tip)

                # Create edges between verts    
                    
                    # Build the KD Tree used to find the nearest vert to a given one
                size = len(b_mesh.verts)
                kd = mathutils.kdtree.KDTree(size)
                    
                for vert_tip, v in enumerate(b_mesh.verts):
                    kd.insert(v.co, vert_tip)
                        
                kd.balance() 
            
                def get_connected_vert(vert=None, exclude=None):
                    sel_edge = 0
                    if len(vert.link_edges) > 1:
                        if vert.link_edges[sel_edge].verts[0] == exclude or vert.link_edges[sel_edge].verts[1] == exclude:
                            sel_edge = 1
                    
                    if vert.link_edges[sel_edge].verts[0] != vert:
                        return vert.link_edges[sel_edge].verts[0]
                    else:
                        return vert.link_edges[sel_edge].verts[1]
                    
                # Edgify function -----------------------------------------------------
                def edgify(starting_vert):    
                    
                    
                    count = 0
                    dist_max = bpy.context.active_object.dimensions[0]/10
                    angle_max = 50
                    current_vert = starting_vert
                    draw_segment = True     
                    edge_dir = "to_root"
                    tip_index = None
                    root_index = None           
                    
                            
                    while draw_segment:         
                        
                        def filter_vert_search(_index):
                            searched_vert = b_mesh.verts[_index]
                            if side_idx == 0:
                                dir_compare1 = searched_vert.co[0] < current_vert.co[0]
                                dir_compare2 = searched_vert.co[0] > current_vert.co[0]
                            if side_idx == 1:# reverse the direction for the right side
                                dir_compare1 = searched_vert.co[0] > current_vert.co[0]
                                dir_compare2 = searched_vert.co[0] < current_vert.co[0]
                            
                            if len(searched_vert.link_edges) == 0 and _index != current_vert.index and ((edge_dir == "to_root" and dir_compare1) or (edge_dir == "to_tip" and dir_compare2)):
                                
                                if current_vec != None: 
                                    fac = 1
                                    if edge_dir == "to_tip":
                                        fac = 1
                                        
                                    vec_angle = (fac * current_vec).angle(searched_vert.co - current_vert.co)
                                                            
                                    if vec_angle < math.radians(angle_max):
                                    
                                        return True
                                    else:
                                        return False
                                else:
                                    return True
                            else:
                                return False
                                
                        def filter_vert_search_2(_index):
                            searched_vert = b_mesh.verts[_index]
                            if side_idx == 0:
                                dir_compare1 = searched_vert.co[0] < current_vert.co[0]
                                dir_compare2 = searched_vert.co[0] > current_vert.co[0]
                            if side_idx == 1:# reverse the direction for the right side
                                dir_compare1 = searched_vert.co[0] > current_vert.co[0]
                                dir_compare2 = searched_vert.co[0] < current_vert.co[0]
                                
                            if len(searched_vert.link_edges) == 0 and _index != current_vert.index and _index != first_iter_vert and ((edge_dir == "to_root" and dir_compare1) or (edge_dir == "to_tip" and dir_compare2)):
                                
                                if current_vec != None:
                                
                                    fac = 1
                                    if edge_dir == "to_tip":
                                        fac = 1
                                        
                                    vec_angle = (fac * current_vec).angle(searched_vert.co - current_vert.co)
                                                            
                                    if vec_angle < math.radians(angle_max):
                                        return True
                                    else:
                                        return False
                                else:
                                    return True
                            else:
                                return False
                            
                        # calculate previous edge vector for angle check
                        current_vec = None
                        if len(current_vert.link_edges) > 0:
                            vert2 = get_connected_vert(current_vert, current_vert)
                            current_vec = current_vert.co - vert2.co
                                             
                        # find nearest vert  
                            # 2 iteration: if the second angle is lower, choose this one
                            # 1st
                        pos, idx, dist = kd.find(current_vert.co, filter=filter_vert_search)
                        
                        
                            # 2nd
                        if idx != None and current_vec != None:
                            first_iter_vert = idx                   
                            
                            vec1_angle = current_vec.angle(pos - current_vert.co)
                            
                            pos2, idx2, dist2 = kd.find(current_vert.co, filter=filter_vert_search_2)   
                            
                            if pos2 != None:
                                vec2_angle = current_vec.angle(pos2 - current_vert.co)
                                angle_diff = math.degrees(vec1_angle) - math.degrees(vec2_angle)
                                if dist2 < dist_max and angle_diff > 5:
                                    # valid vertices, choose this one
                                    
                                    # take into account the non chosen vert as a new edge if it's closer
                                    if dist2 > dist:
                                        count += 1
                                        #print("Adding 1 additional edge count")
                                        
                                    invalid_verts.append(idx)
                                    pos, idx, dist = pos2, idx2, dist2
                                    
                                    
                                
                                
                        chosen_vert = None
                        shortest_dist = None     
                        
                                    
                        if pos != None:
                            continue_edge = False
                            
                            if not restrict_edgify_half_hand:
                                if dist < dist_max:
                                    continue_edge = True
                                    
                            if restrict_edgify_half_hand: 
                                if side_idx == 0:
                                    if dist < dist_max and pos[0] > (coords_sorted[0][0] + coords_sorted[len(coords_sorted)-1][0])/2:
                                        continue_edge = True
                                if side_idx == 1:
                                    if dist < dist_max and pos[0] < (coords_sorted[0][0] + coords_sorted[len(coords_sorted)-1][0])/2:
                                        continue_edge = True
                                
                            if continue_edge:       
                                      
                                v_index = idx            
                                chosen_vert = v_index                  
                                
                                if chosen_vert!= None:  
                                    # Create edge
                                    b_mesh.verts.ensure_lookup_table() 
                                    b_mesh.verts[chosen_vert].select = True
                                    
                                    b_mesh.edges.new((b_mesh.verts[chosen_vert], current_vert))
                                    current_vert = b_mesh.verts[chosen_vert]
                                    count += 1
                                    
                            else:# reached the end of the segment
                                if edge_dir == "to_root":
                                    edge_dir = "to_tip"
                                    
                                    root_index = current_vert.index
                                    current_vert = starting_vert
                                else:                       
                                    draw_segment = False
                                    tip_index = current_vert.index
                                    
                        else:# reached the end of the segment
                            if edge_dir == "to_root":
                                edge_dir = "to_tip"
                            
                                root_index = current_vert.index
                                current_vert = starting_vert
                            else:                       
                                draw_segment = False
                                tip_index = current_vert.index
                          
                    
                    return count, root_index, tip_index

                # Vertice filter search function -------------------------------------------------------
                finger_thickness = bpy.context.active_object.dimensions[1]/20
                
                def search_left_only(_index):
                    searched_vert = b_mesh.verts[_index]
                    dir_compare = (searched_vert.co)[0] > (root_vert.co)[0]
                    if side_idx == 1:
                        dir_compare = (searched_vert.co)[0] < (root_vert.co)[0]
                        
                    return len(searched_vert.link_edges) == 0 and _index != current_vert.index and (searched_vert.co)[1] > (current_vert.co)[1]+finger_thickness and dir_compare and not _index in invalid_verts

                def search_right_only(_index):
                    searched_vert = b_mesh.verts[_index]
                    return len(searched_vert.link_edges) == 0 and _index != current_vert.index and (searched_vert.co)[1] < (current_vert.co)[1]-finger_thickness and not _index in invalid_verts        

                def search_up_only(_index):
                    searched_vert = b_mesh.verts[_index]
                    dir_compare = (searched_vert.co)[0] < (current_vert.co)[0]
                    if side_idx == 1:
                        dir_compare = (searched_vert.co)[0] > (current_vert.co)[0]
                    
                    return _index != current_vert.index and dir_compare and not _index in invalid_verts# and len(searched_vert.link_edges) == 0

                #---------------------------------------------------------------------------------------  
               
                invalid_verts = []  
                
                # Start processing, first finger (longer)           
                
                found_first_finger = False
                current_vert = b_mesh.verts[first_finger_tip]   
                auto_align_phalanges = False
                hand_pos_vec = Vector((bpy.data.objects["hand_loc"+suff].location[0], (wrist_bound_back+wrist_bound_front)/2, bpy.data.objects["hand_loc"+suff].location[2]))
                
                if fingers_total <= 2:
                    auto_align_phalanges = True
                
                if auto_align_phalanges:        
                    root_pos = (current_vert.co + hand_pos_vec) * 0.5               
                    root_vert = b_mesh.verts.new(root_pos)  
                    b_mesh.verts.index_update()
                    
                    last_vert = current_vert
                    cast_object = bpy.data.objects["arp_hand_aligned"]  
                    # create verts and edges aligned toward the wrist
                    for y in range(1,3):
                        finger_vec = (root_pos- current_vert.co)
                        vloc = current_vert.co + (finger_vec/3.5) * y
                        
                        # Find the Z pos
                        have_hit_top = have_hit_bot = False
                        ray_dir = Vector((0,0,1000000))
                        ori = Vector((vloc[0], vloc[1], vloc[2] + 2000))
                        offset = bpy.context.active_object.dimensions[2]*0.005
                        while not have_hit_top: 
                            cast_object_eval = bpy.context.depsgraph.objects.get(cast_object.name, None)
                            sucess1, hit_top, normal, index = cast_object_eval.ray_cast(ori, -ray_dir, distance=ray_dir.magnitude)
                            if not sucess1:# there's a hole in the mesh, offset the Y position
                                
                                ori[1] += bpy.context.active_object.dimensions[1]*0.0001                                    
                            else:   
                                have_hit_top = True
                                while not have_hit_bot: 
                                    success2, hit_bot, normal, index = cast_object_eval.ray_cast(hit_top + Vector((0,0, -offset)), -ray_dir, distance=ray_dir.magnitude)
                                    if not success2:# there's a hole in the mesh, offset the Y position
                                        hit_top[1] += bpy.context.active_object.dimensions[1]*0.0001
                                                
                                    else:
                                        vloc[2] = (hit_top[2] + hit_bot[2])*0.5
                                        have_hit_bot = True
                        
                        # Create the vert                   
                        new_vert = b_mesh.verts.new(vloc)
                        b_mesh.verts.index_update()
                        # Create edge
                        b_mesh.edges.new((last_vert, new_vert))
                        last_vert = new_vert
                        
                    # Final edge
                    b_mesh.edges.new((last_vert, root_vert))
                    b_mesh.verts.ensure_lookup_table()
                    
                    
                    root_idx = root_vert.index
                    tip_idx = first_finger_tip
                
                    found_first_finger = True
                    if bpy.context.scene.arp_debug_mode:
                        print("Found first finger", root_vert.index)
                        
                
                iterate = 0
                while not found_first_finger:
                    
                    edge_count, root_idx, tip_idx = edgify(b_mesh.verts[first_finger_tip]) 
                    
                    if edge_count < 5:
                        if bpy.context.scene.arp_debug_mode:
                            print("    Could not edgify the first finger, try again...")
                        # Find another close vert
                        invalid_verts.append(root_idx)
                        invalid_verts.append(first_finger_tip)
                        pos, idx, dist = kd.find(b_mesh.verts[first_finger_tip].co, filter=search_up_only)
                        
                        if idx != None:
                            first_finger_tip = idx
                        # Fail to find, exit detection
                        if idx == None or iterate > 79:                     
                            print("    Fingers detection on side", side, "failed")
                            if side_idx == 0:
                                self.fingers_detection_success_l = False
                            if side_idx == 1:
                                self.fingers_detection_success_r = False
                            
                            #bpy.context.scene.arp_fingers_to_detect = "NONE"
                            break
                    else:
                        found_first_finger = True
                        if bpy.context.scene.arp_debug_mode:
                            print("    Found first finger", root_idx)
                
                    iterate += 1            
                
                    
                go_upper = True
                go_lower = True         
                
            if (self.fingers_detection_success_l and side_idx == 0) or (self.fingers_detection_success_r and side_idx == 1):
                b_mesh.verts.ensure_lookup_table()
            
            
                # Finger list format: ("name", tip index, root index, tip coords, root coords)
                
                fingers_list = [("finger0", tip_idx, root_idx, b_mesh.verts[tip_idx].co.copy(), b_mesh.verts[root_idx].co.copy())]

                
                if fingers_total <= 2:
                    go_upper = False
                    go_lower = False
                    
                # Find upper tips
                if bpy.context.scene.arp_debug_mode:
                    if go_upper:
                        print("\n    Going up")                 
                
                go_upper_count = 0
                current_vert = b_mesh.verts[tip_idx]
                root_vert = b_mesh.verts[root_idx]


                while go_upper:
                    go_upper_count += 1
                    pos, idx, dist = kd.find(current_vert.co, filter=search_left_only)

                    if idx != None:        
                        b_mesh.verts[idx].select = True
                       # Edgify
                        edge_count, root_idx, tip_idx = edgify(b_mesh.verts[idx])
                        if edge_count < 4:
                            if bpy.context.scene.arp_debug_mode:
                                print("    Finger", go_upper_count, "is invalid finger, not enough edges detected")
                            invalid_verts.append(idx)
                            invalid_verts.append(root_idx)
                        else:
                            if bpy.context.scene.arp_debug_mode:
                                print("    Found finger", go_upper_count, tip_idx)  
                            
                            fingers_list.append(("finger"+str(go_upper_count), tip_idx, root_idx, b_mesh.verts[tip_idx].co.copy(), b_mesh.verts[root_idx].co.copy()))
                            current_vert = b_mesh.verts[tip_idx]
                            root_vert = b_mesh.verts[root_idx]
                            
                    else:
                        go_upper = False
                        
                     # if found all fingers, exit
                    if len(fingers_list) == fingers_total:
                        go_upper = False
                        go_lower = False

                    
                                        
                # Go Lower
                if bpy.context.scene.arp_debug_mode:
                    if go_lower:
                        print("\n    Going down")                   
                
                go_lower_count = 0
                    # iterate lower
                while go_lower:
                    current_vert = b_mesh.verts[first_finger_tip]
                    go_lower_count += 1
                    pos, idx, dist = kd.find(current_vert.co, filter=search_right_only)   
                   
                    if idx != None:        
                        b_mesh.verts[idx].select = True
                        
                       # Edgify
                        edge_count, root_idx, tip_idx = edgify(b_mesh.verts[idx])
                        
                        if edge_count < 5:
                            bpy.ops.mesh.select_all(action='DESELECT')
                            b_mesh.verts[idx].select = True
                            bpy.ops.mesh.select_linked(delimit=set())
                            bpy.ops.mesh.delete(type='EDGE_FACE')
                            
                            if bpy.context.scene.arp_debug_mode:
                                print("    Finger", go_lower_count, "is invalid finger, not enough edges detected")
                        
                        else:
                            if bpy.context.scene.arp_debug_mode:
                                print("    Found finger", go_lower_count, tip_idx)          
                            
                            fingers_list.append(("finger"+str(go_lower_count), tip_idx, root_idx, b_mesh.verts[tip_idx].co.copy(), b_mesh.verts[root_idx].co.copy()))
                            current_vert = b_mesh.verts[tip_idx]
                                            
                    else:
                        go_lower = False
                           
                    if go_lower_count > 30:
                        go_lower = False
                    
                    # if found all fingers, exit
                    if len(fingers_list) == fingers_total:
                        go_lower = False
                
                
                # Delete vertices not connected to edges withing the fingers thickness value to avoid issues
                def find_connected_verts(_index):
                    searched_vert = b_mesh.verts[_index]    
                    if (searched_vert.co - vert.co).magnitude < finger_thickness:
                        if len(searched_vert.link_edges) > 0:
                            return True
                        
                    return False
                
                b_mesh.verts.ensure_lookup_table()
                
                for vert in b_mesh.verts:   
                    if len(vert.link_edges) == 0:
                        pos, idx, dist = kd.find(vert.co, filter=find_connected_verts)
                        if idx != None and not idx in invalid_verts:
                            invalid_verts.append(vert.index)
                            if bpy.context.scene.arp_debug_mode:
                                print("    APPENDING INVALID", vert.index)
                
                # If some fingers haven't been found yet, try again, it's probably the thumb wich is in a tricky place
                
                        
                while len(fingers_list) < fingers_total:
                    print("\n    Look for the thumb...")
                    # Look for the bottom vert not linked to edge
                    bot_bound = None
                    thumb_tip = None
                    
                    if fingers_total != 2:
                        for vert in b_mesh.verts:
                            if not vert.index in invalid_verts:
                                
                                if len(vert.link_edges) == 0:
                                    coord = vert.co.copy()        
                                    
                                    if bot_bound == None:
                                        bot_bound = coord[1]
                                        thumb_tip = vert
                                    else:
                                        thumb_tip_coord = thumb_tip.co.copy()
                                        
                                        if coord[1] < bot_bound:
                                            if (coord[0] > thumb_tip_coord[0] and side_idx == 0) or (coord[0] < thumb_tip_coord[0] and side_idx == 1):                
                                                bot_bound = coord[1]
                                                thumb_tip = vert
                    
                    if fingers_total == 2:
                        for vert in b_mesh.verts:
                            if not vert.index in invalid_verts:
                                
                                if len(vert.link_edges) == 0:
                                    coord = vert.co.copy()        
                                    
                                    if thumb_tip == None:                                       
                                        thumb_tip = vert
                                    else:
                                        thumb_tip_coord = thumb_tip.co.copy()                                       
                                        
                                        if coord[1] < thumb_tip_coord[1]:                                           
                                            thumb_tip = vert
                                        
                    if thumb_tip:   
                        bpy.ops.mesh.select_all(action='DESELECT')

                        thumb_tip.select = True
                        restrict_edgify_half_hand = False
                        edge_count, root_idx, tip_idx = edgify(thumb_tip)
                        
                        if edge_count < 3:
                            if bpy.context.scene.arp_debug_mode:
                                print("    Thumb is invalid finger, not enough edges detected") 
                            invalid_verts.append(root_idx)
                        else:
                            if bpy.context.scene.arp_debug_mode:
                                print("    Found thumb", tip_idx)
                            fingers_list.append(("thumb", tip_idx, root_idx, b_mesh.verts[tip_idx].co.copy(), b_mesh.verts[root_idx].co.copy()))
                                
                    else:
                        print("    Fingers detection on side", side, "failed")
                        if side_idx == 0:
                            self.fingers_detection_success_l = False
                        if side_idx == 1:
                            self.fingers_detection_success_r = False
                        #bpy.context.scene.arp_fingers_to_detect = "NONE"
                        break
                
                
                
                if (self.fingers_detection_success_l and side_idx == 0) or (self.fingers_detection_success_r and side_idx == 1):        
                    
                    print("    Fingers", side, "have been fully detected")
                    # Re order from top to bottom, based on Y position and make sure the smaller X value is the thumb
                    fingers_list = sorted(fingers_list, reverse=True, key=lambda x: x[3][1])   

                    if fingers_total != 2:
                        if side_idx == 0:
                            fingers_x_sort = sorted(fingers_list, reverse=False, key=lambda x: x[3][0])
                        if side_idx == 1:# revert order for the right side
                            fingers_x_sort = sorted(fingers_list, reverse=True, key=lambda x: x[3][0])


                        thumb_index = fingers_list.index(fingers_x_sort[0])
                        fingers_list.pop(thumb_index)
                        fingers_list.insert(len(fingers_list), fingers_x_sort[0])

                    
                    # Rename the fingers according to the sorted list
                    fingers_names = ["pinky", "ring", "middle", "index", "thumb"]
                    
                        # if 4 fingers only to detect, remove the pinky
                    if fingers_total <= 4:
                        fingers_names.pop(0)
                    if fingers_total <= 2:                      
                        fingers_names.pop(0)
                        fingers_names.pop(0)
                    if fingers_total == 1:  
                        fingers_names.pop(1)
                    print(fingers_names)
                                
                    for fi, name in enumerate(fingers_names):
                        #print(fingers_list[fi][0])
                        fingers_list[fi] = (name, fingers_list[fi][1], fingers_list[fi][2], fingers_list[fi][3], fingers_list[fi][4])
                        
                    
                    """
                    print("\nFinger sorted")
                    for finger in fingers_list:
                        print(finger)
                    """

                    
                    # Ensure the tip vert reaches the tip mesh surface
                    for fi, finger in enumerate(fingers_list):
                        vert_idx = finger[1]
                        current_vert = b_mesh.verts[vert_idx]
                        vert2 = get_connected_vert(current_vert, current_vert)
                        ray_dir = vert2.co - current_vert.co
                        hand_obj_eval = bpy.context.depsgraph.objects.get(hand_obj.name, None)
                        hit, loc, norm, face = hand_obj_eval.ray_cast(current_vert.co, -ray_dir)
                        if hit:
                            current_vert.co = loc
                            # update the fingers list
                            fingers_list[fi] = (fingers_list[fi][0], fingers_list[fi][1], fingers_list[fi][2], loc, fingers_list[fi][4])
                                    
                    
                    # resample at a higher rate for better phalanges position               
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.subdivide(smoothness=0)    
                    if fingers_total <= 2:
                        bpy.ops.mesh.subdivide(smoothness=0)    
                    b_mesh.verts.ensure_lookup_table()
                    
                    """
                    if side_idx == 1:
                        bpy.ops.mesh.select_all(action='DESELECT')
                        b_mesh.verts[fingers_list[1][1]].select = True
                        print(br)
                    """
                    
                    # get the fingers length
                    fingers_length = []
                    b_mesh.edges.ensure_lookup_table() 
                    
                    for fi, finger in enumerate(fingers_list):
                        current_vert = b_mesh.verts[finger[1]]
                        previous_vert = None
                        total_length = 0.0
                        progress = True
                        start = True                    
                        
                        
                        while progress:
                            if len(current_vert.link_edges) > 1 or start == True:# break the loop if the end is reached                         
                            
                                new_vert = get_connected_vert(vert=current_vert, exclude=previous_vert)
                                previous_vert = current_vert
                                current_vert = new_vert
                                
                                total_length += (previous_vert.co-current_vert.co).magnitude     
                                start = False
                                
                            else:
                                progress = False
                                
                                fingers_length.append(total_length)           
                    
                    if bpy.context.scene.arp_debug_mode:
                        print("\n    Fingers length:")
                        for fi in fingers_length:
                            print("    ", fi)
                        
                    # Place the phalanges
                    print("    Phalanges...")
                    phalanges_pos = []
                         
                        # find the phalanges pos
                    for fi, finger in enumerate(fingers_list):
                        current_vert = b_mesh.verts[finger[1]]
                        previous_vert = None
                        current_length = 0.0
                        total_length = fingers_length[fi]
                        progress = True
                        start = True
                        found_phal_1 = False
                        found_phal_2 = False
                        
                        while progress:
                            
                            if len(current_vert.link_edges) > 1 or start == True:# break the loop if the end is reached                         
                            
                                new_vert = get_connected_vert(vert=current_vert, exclude=previous_vert)
                                previous_vert = current_vert
                                current_vert = new_vert                             
                                
                                current_length += (previous_vert.co-current_vert.co).magnitude     
                                start = False
                                
                                if current_length >= total_length/3 and found_phal_1 == False:
                                    found_phal_1 = True
                                    phalanges_pos.append((finger[0], current_vert.co.copy()))                           
                                    
                               
                                if current_length >= (total_length/3)*2 and found_phal_2 == False:
                                    found_phal_2 = True                
                                    progress = False
                                    if not finger[0] == "thumb":  
                                        phalanges_pos.append((finger[0], current_vert.co.copy()))
                                        
                                    else:# for the thumb, the root is the 2nd phalange
                                        phalanges_pos.append((finger[0], finger[4]))                
                                
                            else:
                                progress = False
                                fingers_length.append(total_length)
                            
                
                    
                    # Place the fingers master root
                    print("\n    Root positions...")
                    fingers_root_list = []
                    
                        #make wrist bounds thinner      
                    wrist_bound_back = wrist_bound_back + (wrist_bound_front-wrist_bound_back)*0.3
                    wrist_bound_front = wrist_bound_front + (wrist_bound_back-wrist_bound_front)*0.3
                    
                    for fi, finger in enumerate(fingers_list):
                        if finger[0] != "thumb":
                            pos = hand_pos_vec + (finger[4] - hand_pos_vec)*0.3     
                            pos[1] = (finger[4][1] + (wrist_bound_back + (wrist_bound_front-wrist_bound_back)*fi/4))/2
                        else:
                            pos = (finger[4] + hand_pos_vec)*0.5        
                                
                        fingers_root_list.append((finger[0]+"_root", pos))
                    
                    # Refine pass 1: smoothen the wrist-fingers root distance       
                    average_dist = 0.0
                    count = 0
                    for fi, finger in enumerate(fingers_list):
                        if finger[0] == "pinky" or finger[0] == "ring" or finger[0] == "middle" or finger[0] == "index":
                            average_dist += (hand_pos_vec - fingers_list[fi][4]).magnitude
                            count += 1
                            
                    if len(fingers_list) > 2:                   
                        average_dist /= count               
                    else:   
                        average_dist = (fingers_list[0][4] - hand_pos_vec).magnitude
                    
                        # dict storing the root original pos and reposition vec
                    root_move_vec = {}
                    
                    for fi, finger in enumerate(fingers_list):
                        if finger[0] != "thumb":
                            dir = (fingers_list[fi][4] - hand_pos_vec).normalized()
                            pos = hand_pos_vec + dir * average_dist * 0.9# 0.9 to move them back a little, they're generally too forward    
                            root_move_vec[finger[0]] = (fingers_list[fi][4], pos - fingers_list[fi][4])
                            fingers_list[fi] = (fingers_list[fi][0], fingers_list[fi][1], fingers_list[fi][2], fingers_list[fi][3], pos)
                        
                    
                    
                    # Refine pass 2: re-position the phalanges
                    for fi in range(0, len(phalanges_pos), 2):                      
                        finger_name = phalanges_pos[fi+1][0]
                        if finger_name != "thumb":
                            phal1_pos = phalanges_pos[fi+1][1]
                            phal1_vec = root_move_vec[finger_name][0] - phal1_pos
                            d = (root_move_vec[finger_name][1].magnitude)*0.4
                            d = clamp_max(d, phal1_vec.magnitude)
                            phal1_pos = phal1_pos + phal1_vec.normalized()*d
                            
                            # update the phalange list
                            phalanges_pos[fi+1] = (phalanges_pos[fi+1][0], phal1_pos)
                    
                    
                    
                    
                    # Create an empty for detected position
                    print("    Create empties loc...")
                    bpy.ops.object.mode_set(mode='OBJECT')

                    for f_i, finger in enumerate(fingers_list):
                        # tip
                        create_empty_loc(0.02, finger[3], finger[0] + "_top"+side)      
                        
                        # root
                        create_empty_loc(0.02, finger[4], finger[0] + "_bot"+side)          
                        
                        # master root
                        create_empty_loc(0.02, fingers_root_list[f_i][1], fingers_root_list[f_i][0]+side)           
                    
                    for fi in range(0, len(phalanges_pos), 2):
                    
                        # phalange 1
                        create_empty_loc(0.02, phalanges_pos[fi][1], phalanges_pos[fi][0] + "_phal_1"+side)     
                        
                        if "middle" in phalanges_pos[fi+1][0]:
                            if bpy.context.scene.arp_debug_mode:
                                print("    Passed value:", phalanges_pos[fi+1][1])
                        #phalange 2
                        create_empty_loc(0.02, phalanges_pos[fi+1][1], phalanges_pos[fi+1][0] + "_phal_2"+side)
                    
        
            # --End if scene.arp_fingers_to_detect != 'NONE'
            
            bpy.ops.object.mode_set(mode='OBJECT')  
            
            #rotate the empties back to original coords
            bpy.context.scene.cursor.location = shoulder_pos        
            bpy.ops.object.select_all(action='DESELECT')    
        
            for obj in bpy.data.objects["auto_detect_loc"].children:
                if ("pinky" in obj.name or "ring" in obj.name or "middle" in obj.name or "index" in obj.name or "thumb" in obj.name) and side in obj.name:
                    set_active_object(obj.name)
                    
            # rotate back the marker to original coords
            set_active_object('hand_loc'+suff)          
            bpy.ops.transform.rotate(value=-arm_angle*rot_fac, orient_axis='Y', constraint_axis=(False, False, False), orient_type='GLOBAL', mirror=False, proportional='DISABLED')                
    
        bpy.ops.object.mode_set(mode='OBJECT')
        
        create_empty_loc(0.04, _hand_empty_loc, "hand_loc"+side)    
        
        #delete arp_hand_aligned
        bpy.data.objects.remove(bpy.data.objects["arp_hand_aligned"], do_unlink=True)   
    
        # delete arp_part_verts objects
        if bpy.data.objects.get("arp_part_verts"):
            bpy.data.objects.remove(bpy.data.objects["arp_part_verts"], do_unlink=True)
        
        # delete the selection helper
        if bpy.data.objects.get("arp_hand_transform"):
            bpy.data.objects.remove(bpy.data.objects["arp_hand_transform"], do_unlink=True)
            
        
    
    
    # Legs detection -------------------------------------------------------------------------
        
    foot_loc_l = bpy.data.objects["foot_loc"]
    foot_loc_r = bpy.data.objects["foot_loc_sym"]
    
    foot_markers = [foot_loc_l]
    
    if not scene.arp_smart_sym:
        foot_markers.append(foot_loc_r)
    

    for side_idx, foot_marker in enumerate(foot_markers):
    
        if side_idx == 0:
            print('\n[Left foot detection...]')     
        if side_idx == 1:
            print('\n[Right foot detection...]')        
            
        side = ".l"
        if side_idx == 1:
            side = ".r"
    
        set_active_object(body.name)        
        bpy.ops.object.mode_set(mode='EDIT')    

        #select vertices around the foot_loc 
        selected_index = []
        mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
        
        
        for v in mesh.verts:        
            compare_x = v.co[0] > 0
            if side_idx == 1:
                compare_x = v.co[0] < 0
            if v.co[2] <= foot_marker.location[2] and compare_x:
                v.select = True
                selected_index.append(v.index)  

        
            
        bound_back = -10000.0
        bound_front = 10000.0       
    
        #find the boundaries        
        print("    Find foot boundaries...")
        
        clear_selection()
    
        for vi in selected_index:
            mesh.verts.ensure_lookup_table()
            vert_y = mesh.verts[vi].co[1]           
            #back    
            if vert_y > bound_back:
                bound_back = vert_y
            #front
            if vert_y < bound_front:
                bound_front = vert_y        
            
   
        
        print("    Find toes...")
                 
        # Toes top
        bound_toes_top = 0.0

        #find the toes height
        
        for vi in selected_index:
            mesh.verts.ensure_lookup_table()  
            #find the toes end vertices
            vert_co = mesh.verts[vi].co     
            vert_z = mesh.verts[vi].co[2]
            
            if tolerance_check(vert_co, bound_front, 1, body_depth / 7, True, side):            
                if vert_z > bound_toes_top:
                    bound_toes_top = vert_z
                    mesh.verts[vi].select = True
        
        #raycast for foot direction
        my_tree = BVHTree.FromBMesh(mesh)               
        
        side_fac = 1    
        if side_idx == 1:
            side_fac= -1        
            
        ray_origin = vectorize3([0, bound_back + (bound_front-bound_back)*0.8, bound_toes_top*0.5]) + vectorize3([body_width*2*side_fac,0.0,0.0])
                    
        ray_dir = vectorize3([-body_width*4*side_fac, 0, 0])
        
        have_hit = False
        iterate = 0     
        
        while have_hit == False:    
            hit, normal, index, distance = my_tree.ray_cast(ray_origin, ray_dir, ray_dir.magnitude)
            
            new_origin = vectorize3([ray_origin[0], ray_origin[1], ray_origin[2]*0.5])
                        
            if hit != None:
            
                compare_x = hit[0] < 0
                if side_idx == 1:
                    compare_x = hit[0] > 0
                    
                if compare_x:
                    ray_origin = new_origin
                    if bpy.context.scene.arp_debug_mode:
                        print("Iterating foot ray...")
                        
                    if iterate > 60:                        
                        self.report({'ERROR'}, "Could not find the feet, are they on the ground?")
                        self.error_during_auto_detect = True
                        return
                else:
                    have_hit = True
                    hit_front = hit
                    last_hit = hit  
            else:
                ray_origin = new_origin
                if bpy.context.scene.arp_debug_mode:
                    print("Iterating foot ray...")
                if iterate > 60:                        
                    self.report({'ERROR'}, "Could not find the feet, are they on the ground?")
                    self.error_during_auto_detect = True
                    return
                        
            iterate += 1
                                
                
        if bpy.context.scene.arp_debug_mode:
            print('    ray foot origin', ray_origin)
            print('    ray hit front', hit_front)
        
        while have_hit:#iterate if multiple polygons layers
            have_hit = False
            hit, normal, index, distance = my_tree.ray_cast(last_hit+vectorize3([-0.001 * side_fac,0,0]), ray_dir, ray_dir.magnitude)
            if hit != None:
            
                #left or right side only
                compare_x = hit[0] > 0
                if side_idx == 1:
                    compare_x = hit[0] < 0
                    
                if compare_x:
                    last_hit = hit
                    have_hit = True
            
        hit_back = last_hit 
        
        if bpy.context.scene.arp_debug_mode:
            print('    ray hit back', hit_back)
            
        hit_center = (hit_back+hit_front)/2
        
        print("    Find ankle...\n")
                    
        # Ankle    
        clear_selection()
        
        ray_origin = vectorize3([foot_marker.location[0], 0, foot_marker.location[2]]) + vectorize3([0, -body_width*2, 0])
        ray_dir = vectorize3([0, body_width*4, 0])
        hit_front = None
        last_hit = None
        have_hit = False
        
        while not have_hit: 
            hit, normal, index, distance = my_tree.ray_cast(ray_origin, ray_dir, ray_dir.magnitude)    
            if hit == None:             
                self.error_during_auto_detect = True
                self.report({'ERROR'}, 'Could not find the ankle, marker out of mesh?')
                return
        
            else:
                have_hit = True
                hit_front = hit
                last_hit = hit  
                
        while have_hit:#iterate if multiple polygons layers
            have_hit = False
            hit, normal, index, distance = my_tree.ray_cast(last_hit+vectorize3([0, 0.001, 0]), ray_dir, ray_dir.magnitude)
            if hit != None:         
                last_hit = hit
                have_hit = True
                
        hit_back = last_hit 
    
        if bpy.context.scene.arp_debug_mode:
            print('    ray hit back', hit_back)
        
        hit_center_ankle = (hit_back+hit_front)/2       
      
        ankle_empty_loc = [foot_marker.location[0], hit_center_ankle[1], foot_marker.location[2]]
        ankle_endfoot_dist = (vectorize3([ankle_empty_loc[0], bound_front, ankle_empty_loc[2]]) - vectorize3(ankle_empty_loc)).magnitude
    
    
        if bpy.context.scene.arp_debug_mode:
            print("    Find bank bones...\n")
        # Bank bones
        clear_selection()
        foot_bot_selection = [] 
        for v in mesh.verts:    
            if tolerance_check(v.co, 0.0, 2, body_height / 60, True, side):
                v.select = True    
                foot_bot_selection.append(v.index)            
    

        bpy.ops.object.mode_set(mode='OBJECT')  
        
        foot_dir = vectorize3([hit_center[0] - ankle_empty_loc[0], hit_center[1] - ankle_empty_loc[1], 0])
        
        if side == ".l":
            scene.arp_foot_dir_l = foot_dir
        if side == ".r":
            scene.arp_foot_dir_r = foot_dir
    
        #find the bank bones in foot direction space
            #create temp empty object for the coord space calculation
        angle = (vectorize3([0,-1,0]).angle(foot_dir))
        bpy.ops.object.empty_add(type='PLAIN_AXES', radius = 1, view_align=True, location=(0,0,0), rotation=(0, 0, angle*side_fac)) 
        # rename it     
        bpy.context.active_object.name = "foot_dir_space"
        foot_dir_matrix = bpy.data.objects['foot_dir_space'].matrix_world
        
        set_active_object(body.name)
        bpy.ops.object.mode_set(mode='EDIT')    
    
    
        #select vertices around the foot_loc    
        mesh = bmesh.from_edit_mesh(bpy.context.active_object.data) 
        foot_back = [0,-10000.0,0]          
        foot_left = [10000.0,0,0]
        
        if side_idx == 1:
            foot_left = [-10000.0,0,0]
            
        foot_right = [0,0,0]
    
        #find the boundaries in foot dir space          
        clear_selection()
        
        for vi in foot_bot_selection:
            mesh.verts.ensure_lookup_table()
            vert_co = mesh.verts[vi].co @ foot_dir_matrix       
            
            #back    
            if vert_co[1] > foot_back[1]:
                foot_back = vert_co             
            #left
            compare_x = vert_co[0] < foot_left[0]
            if side_idx == 1:
                compare_x = vert_co[0] > foot_left[0]           
            if compare_x:
                foot_left = vert_co
                
            #right
            compare_negx = vert_co[0] > foot_right[0]
            if side_idx == 1:
                compare_negx = vert_co[0] < foot_right[0]           
            if compare_negx:            
                foot_right = vert_co                
                
        bank_right_loc = [foot_left[0], foot_back[1], 0]
        bank_left_loc = [foot_right[0], foot_back[1], 0]
        bank_mid_loc = [(foot_left[0] + foot_right[0])/2, foot_back[1], 0]      
                
        bank_right_loc = vectorize3(bank_right_loc) @ foot_dir_matrix.inverted()
        bank_left_loc = vectorize3(bank_left_loc) @ foot_dir_matrix.inverted()
        bank_mid_loc = vectorize3(bank_mid_loc) @ foot_dir_matrix.inverted()
        
    
        bpy.ops.object.mode_set(mode='OBJECT')  
        
        toes_end_loc = vectorize3(ankle_empty_loc) + (foot_dir.normalized() * ankle_endfoot_dist)
        toes_end_loc[2] = 0
        toes_start_loc = vectorize3(ankle_empty_loc) + (toes_end_loc-vectorize3(ankle_empty_loc))*0.7
        toes_start_loc[2] = bound_toes_top*0.5
    
        # create empty location   
        foot_dict = {'ankle_loc':[ankle_empty_loc, "ankle_loc"], 'bank_left_loc':[bank_left_loc,"bank_left_loc"],'bank_right_loc':[bank_right_loc, "bank_right_loc"],'bank_mid_loc':[bank_mid_loc,"bank_mid_loc"],'toes_end':[toes_end_loc,"toes_end"],'toes_start':[toes_start_loc,"toes_start"]}

        for key, value in foot_dict.items():
            create_empty_loc(0.04, value[0], value[1]+side)
            
                
        bpy.ops.object.select_all(action='DESELECT')
        set_active_object('foot_dir_space')
        bpy.ops.object.delete(use_global=False)

    
    # ROOT POSITION --------------------------------------------------------------------------------------------
    
    print("Find root position...\n")
    
        # get the loc guides
    root_marker = bpy.data.objects["root_loc"]
    set_active_object(body.name)
    bpy.ops.object.mode_set(mode='EDIT')
    mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
    
    #select vertices in the overlapping sphere
    
    hips_back = None
    hips_front = None   
    hips_right = None
    hips_left = None
    
    my_tree = BVHTree.FromBMesh(mesh)   
    
    # Find position by raycast
        # Front / Back
    ray_origin = vectorize3([root_marker.location[0], 0, root_marker.location[2]]) + vectorize3([0, -body_width*2, 0])
    ray_dir = vectorize3([0, body_width*4, 0])  
    last_hit = None
    have_hit = False
    
    while not have_hit: 
        hit, normal, index, distance = my_tree.ray_cast(ray_origin, ray_dir, ray_dir.magnitude)    
        if hit == None:     
            self.error_during_auto_detect = True
            self.report({'ERROR'}, 'Could not find the root pos, marker out of mesh?')
            return
            
        else:
            have_hit = True
            hips_front = hit
            last_hit = hit  
            
    while have_hit:#iterate if multiple polygons layers
        have_hit = False
        hit, normal, index, distance = my_tree.ray_cast(last_hit+vectorize3([0, 0.001, 0]), ray_dir, ray_dir.magnitude)
        if hit != None:         
            last_hit = hit
            have_hit = True
            
    hips_back = last_hit    
    
    
    
    # Surface method
        #select vertices in the overlapping sphere
    root_selection = [] 
    clear_selection()       
    base_dist = body_width / 15
    r_dist = base_dist  
    vert_sel = []   
    hips_bound_right = None
    hips_bound_left = None
    
    has_selected = False
    
    while not has_selected:
        for v in mesh.verts:    
            if tolerance_check_2(v.co, root_marker.location, 0, 2, r_dist, ".l"):               
                vert_sel.append(v)
                has_selected = True
                if hips_bound_right == None:
                    hips_bound_right = v.co[0]
                if v.co[0] > hips_bound_right:
                    hips_bound_right = v.co[0]
        r_dist += base_dist
        
    has_selected = False
    
    while not has_selected:
        for v in mesh.verts:    
            if tolerance_check_2(v.co, root_marker.location, 0, 2, r_dist, ".r"):               
                vert_sel.append(v)
                has_selected = True
                if hips_bound_left == None:
                    hips_bound_left = v.co[0]
                if v.co[0] < hips_bound_left:
                    hips_bound_left = v.co[0]   
                    
        r_dist += base_dist                 
        
        
    
    found_boundary = False
    while not found_boundary:       
        found_boundary = True
        for vert in vert_sel:
            for edge in vert.link_edges:
                for v in edge.verts:
                    if not v in vert_sel and v.co[0] > vert.co[0]:
                        if tolerance_check(v.co, root_marker.location[2], 2, body_width / 15, True, ".l"):
                            vert_sel.append(v)                          
                            found_boundary = False
                            if v.co[0] > hips_bound_right:
                                hips_bound_right = v.co[0]
                                
    found_boundary = False
    while not found_boundary:       
        found_boundary = True
        for vert in vert_sel:
            for edge in vert.link_edges:
                for v in edge.verts:
                    if not v in vert_sel and v.co[0] < vert.co[0]:
                        if tolerance_check(v.co, root_marker.location[2], 2, body_width / 15, True, ".r"):
                            vert_sel.append(v)                          
                            found_boundary = False
                            if v.co[0] < hips_bound_left:
                                hips_bound_left = v.co[0]                           
                                
    
    hips_right = Vector((hips_bound_right, (hips_back[1]+hips_front[1])/2, root_marker.location[2]))
    hips_left = Vector((hips_bound_left, (hips_back[1]+hips_front[1])/2, root_marker.location[2]))
    
    if scene.arp_smart_sym:
        hips_left = Vector((-hips_bound_right, (hips_back[1]+hips_front[1])/2, root_marker.location[2]))
    
    root_empty_loc = [root_marker.location[0], (hips_back[1]+hips_front[1])/2, root_marker.location[2]]
    
    
     # Legs detection --------------------------------------------------------------------------------------------
    for side_idx, foot_marker in enumerate(foot_markers):   
        if side_idx == 0:
            print('\n[Left leg detection...]')      
        if side_idx == 1:
            print('\n[Right leg detection...]')     
        
        side = ".l" 
        hips_side = hips_right
        ankle_empty_loc = bpy.data.objects["ankle_loc.l_auto"].location
        if side_idx == 1:
            hips_side = hips_left
            ankle_empty_loc = bpy.data.objects["ankle_loc.r_auto"].location
            side = ".r"
            
        leg_empty_loc = [(hips_side[0])/2, root_empty_loc[1], root_empty_loc[2]]
        knee_empty_loc = [(leg_empty_loc[0] + ankle_empty_loc[0])/2, 0, (leg_empty_loc[2] + ankle_empty_loc[2])/2]
        bot_empty_loc = [leg_empty_loc[0], -hips_front[1], leg_empty_loc[2]]
         
        # find the knee boundaries
        
        if bpy.context.scene.arp_debug_mode:
            print("    Find knee boundaries...\n")
        
        set_active_object(body.name)
        bpy.ops.object.mode_set(mode='EDIT')
        mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
            
        clear_selection()
        knee_selection = []     
        has_selected_knee = False
        sel_dist = body_height / 25
            
        while has_selected_knee == False:
            for vb in mesh.verts:    
                if tolerance_check(vb.co, knee_empty_loc[2], 2, sel_dist, True, side):
                    vb.select = True    
                    knee_selection.append(vb.index)
                    has_selected_knee = True
                    
            sel_dist *= 2        
    

        knee_back = -10000
        knee_front = 10000
        knee_left = 10000
        knee_right = -10000
        
        for vk in knee_selection:        
            mesh.verts.ensure_lookup_table() #debug_mode           
            vert_y = mesh.verts[vk].co[1]   
            vert_x = mesh.verts[vk].co[0]
                
            #front    
            if vert_y < knee_front:
                knee_front = vert_y
            # back
            if vert_y > knee_back:
                knee_back = vert_y      
            # left
            if vert_x < knee_left:
                knee_left = vert_x  
            # right
            if vert_x > knee_right:
                knee_right = vert_x 
         
        knee_empty_loc[1] = knee_back + (knee_front - knee_back)*0.75
        knee_empty_loc[0] = knee_left + (knee_right - knee_left)*0.5

        bpy.ops.object.mode_set(mode='OBJECT')
            
        create_empty_loc(0.04, root_empty_loc, "root_loc")
        create_empty_loc(0.04, leg_empty_loc, "leg_loc"+side)
        create_empty_loc(0.04, knee_empty_loc, "knee_loc"+side)
        create_empty_loc(0.04, bot_empty_loc, "bot_empty_loc"+side)
    
    
    # SPINE POSITION ---------------------------------------------------------
        
    print("\nFind neck...\n")
    
        # Neck
    neck_loc = bpy.data.objects["neck_loc"]
    set_active_object(body.name)
    bpy.ops.object.mode_set(mode='EDIT')
    mesh = bmesh.from_edit_mesh(bpy.context.active_object.data)
    
    #select vertices in the overlapping neck sphere    
    neck_selection = []    
    clear_selection() 
    
    has_selected_neck = False
    sel_dist = body_height / 25
        

    while has_selected_neck == False:
        for vb in mesh.verts:    
            if tolerance_check_2(vb.co, neck_loc.location, 0, 2, sel_dist, ".l"):
                vb.select = True    
                neck_selection.append(vb.index)
                has_selected_neck = True
                
        sel_dist *= 2        

    
    # find the neck bounds    
    if bpy.context.scene.arp_debug_mode:
        print("    Find neck boundaries...\n")  

    ray_origin = Vector((neck_loc.location[0],-body_depth*2, neck_loc.location[2]))
    ray_dir = vectorize3([0,body_depth*4,0])    
    
    hit, normal, index, distance = my_tree.ray_cast(ray_origin, ray_dir, ray_dir.magnitude) 
    
    if distance == None or distance < 0.001:
        print('    Could not find neck pos, marker out of mesh?')       
    else:
        neck_front = hit
        have_hit = True
        last_hit = hit
        #iterate if multiples faces layers
        while have_hit:
            have_hit = False
            hit, normal, index, distance = my_tree.ray_cast(last_hit+vectorize3([0,0.001,0]), ray_dir, ray_dir.magnitude) 
            if hit != None:                     
                have_hit = True
                last_hit = hit
                
        neck_back = last_hit
    
            
    neck_empty_loc = [neck_loc.location[0], neck_back[1] + (neck_front[1]-neck_back[1])*0.45, neck_loc.location[2]] 
     

    

    # Spine 01  
    my_tree = BVHTree.FromBMesh(mesh)
    vec =  (neck_loc.location - root_marker.location)*1/3
    ray_origin = root_marker.location + vec + vectorize3([0,-body_depth*2,0])
    ray_dir = vectorize3([0,body_depth*4,0])
    
    hit, normal, index, distance = my_tree.ray_cast(ray_origin, ray_dir, ray_dir.magnitude) 
    if distance == None or distance < 0.001:
        print('    Could not find spine 01 front, marker out of mesh?')
    
    else:
        spine_01_front = hit
        have_hit = True
        last_hit = hit
        #iterate if multiples faces layers
        while have_hit:
            have_hit = False
            hit, normal, index, distance = my_tree.ray_cast(last_hit+vectorize3([0,0.001,0]), ray_dir, ray_dir.magnitude) 
            if hit != None:                     
                have_hit = True
                last_hit = hit
                
        spine_01_back = last_hit
        
    spine_01_empty_loc = spine_01_front + (spine_01_back-spine_01_front)*0.65
    
    
    # Spine 02
    vec =  (neck_loc.location - root_marker.location)*2/3
    ray_origin = root_marker.location + vec + vectorize3([0,-body_depth*2,0])
    ray_dir = vectorize3([0,body_depth*4,0])
    
    hit, normal, index, distance = my_tree.ray_cast(ray_origin, ray_dir, ray_dir.magnitude) 
    if distance == None or distance < 0.001:
        print('    Could not find spine 02 front, marker out of mesh')      
    else:
        spine_02_front = hit
        have_hit = True
        last_hit = hit
        #iterate if multiples faces layers
        while have_hit:
            have_hit = False
            hit, normal, index, distance = my_tree.ray_cast(last_hit+vectorize3([0,0.001,0]), ray_dir, ray_dir.magnitude) 
            if hit != None:                     
                have_hit = True
                last_hit = hit
                
        spine_02_back = last_hit
            
    spine_02_empty_loc = spine_02_front + (spine_02_back-spine_02_front)*0.65
    
    # Breast    
    print("Find breast...\n")
    
    #select vertices near spine02
    spine_02_selection = []    
    clear_selection() 
    has_selected_spine_02 = False
    sel_dist = body_height / 17
    
    while has_selected_spine_02 == False:
        for vb in mesh.verts:    
            if tolerance_check_2(vb.co, spine_02_empty_loc, 0, 2, sel_dist, ".l"):
                vb.select = True    
                spine_02_selection.append(vb.index)
                has_selected_spine_02 = True
                
        sel_dist *= 2


    # find the spine 02 front bound
    spine_02_back = -1000
    spine_02_front = 1000
    
    if bpy.context.scene.arp_debug_mode:
        print("    Find breast boundaries...\n")
    
    for vs in spine_02_selection:        
        mesh.verts.ensure_lookup_table()
        vert_y = mesh.verts[vs].co[1]        
        #front    
        if vert_y < spine_02_front:
            spine_02_front = vert_y
         #back    
        if vert_y > spine_02_back:
            spine_02_back = vert_y  
    
    
    breast_01_loc = [shoulder_pos[0]/2, spine_02_front, spine_02_empty_loc[2]] 
    breast_02_loc = [shoulder_pos[0]/2, breast_01_loc[1] + (shoulder_pos[1]-breast_01_loc[1])*0.4, spine_02_empty_loc[2]+ (shoulder_pos[2]-spine_02_empty_loc[2])*0.5]     
    
    print("Find spine 01...\n")
    
    #head   
    chin_loc = None
    xpos = 0
    
        #retro compatibility, chin was not defined in earlier versions
    if bpy.data.objects.get("chin_loc") != None:
        chin_loc = bpy.data.objects["chin_loc"]
        
    if chin_loc == None:
        head_height = neck_empty_loc[2] + (body_height - neck_empty_loc[2])*0.25
    else:
        head_height = chin_loc.location[2] + (body_height - chin_loc.location[2])*0.1
        xpos = chin_loc.location[0] 
    
    
    ray_origin = Vector((xpos,-body_depth*2, head_height))
    ray_dir = vectorize3([0,body_depth*4,0])    
    
    hit, normal, index, distance = my_tree.ray_cast(ray_origin, ray_dir, ray_dir.magnitude) 
    
    if distance == None or distance < 0.001:
        print('    Could not find head pos, marker out of mesh?')       
    else:
        head_front = hit
        have_hit = True
        last_hit = hit
        #iterate if multiples faces layers
        while have_hit:
            have_hit = False
            hit, normal, index, distance = my_tree.ray_cast(last_hit+vectorize3([0,0.001,0]), ray_dir, ray_dir.magnitude) 
            if hit != None:                     
                have_hit = True
                last_hit = hit
                
        head_back = last_hit
    
    
    head_empty_loc = [chin_loc.location[0], head_back[1] + (head_front[1] - head_back[1]    )*0.3, head_height]
    
    # disable raycast,  
    
    # get the head top by raycast   
    head_top = None
    ray_dir = Vector((0, body_depth*4, 0))
    ray_ori = Vector((chin_loc.location[0], -body_depth*2, body_height))
    ray_offset = (body_height-head_height)/100
    have_hit = False
    ray_count = 0
    #print("Ray dir,", ray_dir)
    #print("Ray origin", ray_ori)   
    
    
    while not have_hit and ray_count < 400:
        ray_count += 1
        hit1, normal, index, distance = my_tree.ray_cast(ray_ori - Vector((0,0,ray_offset))*ray_count, ray_dir, ray_dir.magnitude )
        
        if hit1 != None:
            have_hit = True
        
    
    if have_hit:
        if hit1[2] >= head_height:
            head_top = hit1
            #print("Found head top by raycast")
        else:       
            #print("Head top by raycast is below the neck, disabling raycast")
            head_top = Vector((0, 0, body_height))
            print("")
    else:       
        #print("Raycast failed, head top is the body height")
        head_top = Vector((chin_loc.location[0], 0, body_height))
        
    
    
    head_end_empty_loc = [chin_loc.location[0], head_empty_loc[1], head_top[2]]
    
    
    # create the empties       
    bpy.ops.object.mode_set(mode='OBJECT')
    create_empty_loc(0.04, neck_empty_loc, "neck_loc")
    create_empty_loc(0.04, spine_01_empty_loc, "spine_01_loc")
    create_empty_loc(0.04, spine_02_empty_loc, "spine_02_loc")
    create_empty_loc(0.04, head_end_empty_loc, "head_end_loc")
    create_empty_loc(0.04, head_empty_loc, "head_loc")
    create_empty_loc(0.04, breast_01_loc, "breast_01_loc")
    create_empty_loc(0.04, breast_02_loc, "breast_02_loc")

   
    
    #restore the pivot mode
    bpy.context.scene.tool_settings.transform_pivot_point = pivot_mod


    # END - UPDATE VIEW --------------------------------------------------
    bpy.ops.transform.translate(value=(0, 0, 0))
    
    if bpy.context.scene.arp_debug_mode:
        print("End Auto-Detection.\n")
    
    
    
#-- end _auto_detect()     
    
def _delete_detected():
    clear_object_selection()
    if bpy.data.objects.get('auto_detect_loc') != None:
        bpy.data.objects["auto_detect_loc"].select_set(state=1)
        bpy.context.view_layer.objects.active = bpy.data.objects["auto_detect_loc"]
        
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        bpy.ops.object.delete()
        bpy.data.objects["auto_detect_loc"].select_set(state=1)
        
        bpy.ops.object.delete()
    
def _cancel_and_delete_markers():
    scene = bpy.context.scene
    
    # Save all markers position for later restore
        # Clear it first
        # Clear the bone collection
    if len(scene.arp_markers_save) > 0:
        i = len(scene.arp_markers_save)
        while i >= 0:          
            scene.arp_markers_save.remove(i)
            i -= 1
            
    if len(scene.arp_facial_markers_save) > 0:
        i = len(scene.arp_facial_markers_save)
        while i >= 0:          
            scene.arp_facial_markers_save.remove(i)
            i -= 1
            
    # Restore user define vertex sizes  
    if arp_temp_data.current_vertex_size:       
        bpy.context.preferences.themes[0].view_3d.vertex_size = arp_temp_data.current_vertex_size
    
    # Store in property
    for obj in bpy.data.objects['arp_markers'].children:
        item = scene.arp_markers_save.add()     
        item.name = obj.name 
        item.location = obj.location
        if bpy.context.scene.arp_debug_mode:
            print("Saving marker:", item.name)
        
    # Add the mirror state
    item = scene.arp_markers_save.add()     
    item.name = "mirror_state"
    ms = 1
    if not scene.arp_smart_sym:
        ms = 0
    item.location = [ms, ms, ms]
    
        
    if bpy.data.objects.get("arp_facial_setup") != None:
        arp_facial = bpy.data.objects["arp_facial_setup"]
        for vert in arp_facial.data.vertices:
            item = scene.arp_facial_markers_save.add()
            item.id = vert.index 
            
            item.location = arp_facial.matrix_world @ vert.co
            
    
    clear_object_selection()
    bpy.data.objects["arp_markers"].select_set(state=1)
    bpy.context.view_layer.objects.active = bpy.data.objects["arp_markers"] 
    bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
    bpy.ops.object.delete()
    bpy.data.objects["arp_markers"].select_set(state=1)
    
    if bpy.data.objects.get('body_temp'):
        bpy.data.objects["body_temp"].select_set(state=1)
    if bpy.data.objects.get('arp_facial_setup'):
        bpy.data.objects["arp_facial_setup"].select_set(state=1)
    bpy.ops.object.delete()
    

    

def _set_front_view():
    bpy.context.scene.arp_body_name = bpy.context.view_layer.objects.active.name
    
    try:
        bpy.context.space_data.overlay.show_relationship_lines= False
    except:
        pass
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    #get character mesh name
    body = bpy.data.objects[bpy.context.scene.arp_body_name]    
    
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(state=1)
    bpy.context.view_layer.objects.active = body
    #remove parent if any
    #body.parent = None
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    #apply transforms
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    bpy.ops.object.mode_set(mode='EDIT')
    
    # set to vertex selection mode
    bpy.ops.mesh.select_mode(type="VERT")
    
    # remove double
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.mesh.remove_doubles(threshold=1e-006)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # remove any armature modifier
    if len(body.modifiers) > 0:
        for modifier in bpy.context.active_object.modifiers:
            if modifier.type == 'ARMATURE':                 
                bpy.ops.object.modifier_remove(modifier=modifier.name)
                
        
    
    #center front view
    bpy.ops.view3d.view_axis(type='FRONT')
    bpy.ops.view3d.view_selected(use_all_regions=False)
    bpy.ops.object.empty_add(type='PLAIN_AXES', radius = 0.01, view_align=False, location=(0,0,0), rotation=(0, 0, 0))   
    bpy.context.active_object.name = "arp_markers"
    bpy.ops.object.select_all(action='DESELECT')
    
    #set ortho
    bpy.context.space_data.region_3d.view_perspective = 'ORTHO'
    
    #freeze character selection
    bpy.data.objects[bpy.context.scene.arp_body_name].hide_select = True
    if bpy.data.objects.get('rig') != None:
        bpy.data.objects['rig'].hide_select = True
        bpy.data.objects['rig'].hide_viewport = True
        
    
        

def update_sym(self,context):   
    
    # Mirror the markers or not
    if bpy.data.objects.get("arp_markers") != None: 
        if len(bpy.data.objects["arp_markers"].children) > 0:
            for child in bpy.data.objects["arp_markers"].children:
                # symmetrical markers
                if "_sym" in child.name:
                    if len(child.constraints) > 0:
                        # lock mirror
                        if context.scene.arp_smart_sym:
                            child.constraints[0].influence = 1.0
        
                        # unlock mirror
                        else:
                            final_mat = child.matrix_world
                            child.constraints[0].influence = 0.0
                            child.matrix_world = final_mat
                # center markers
                if "chin" in child.name or "neck" in child.name or "root" in child.name:
                    # lock x-axis
                    if context.scene.arp_smart_sym:
                        child.lock_location[0] = True
                        child.location[0] = 0.0
                    
                    # unlock x-axis
                    else:
                        child.lock_location[0] = False
                        
    # Smart facial not yet support in non-mirror mode. Disable when mirror is off.
    if not context.scene.arp_smart_sym:
        if bpy.data.objects.get("arp_facial_setup") != None:
            _cancel_facial_setup()


@persistent
# Function called when loading a new file, to revert unwanted changes
# i.e vertex sizes may have been changed
def revert_arp_changes(scene):  
    if arp_temp_data.current_vertex_size:       
        bpy.context.preferences.themes[0].view_3d.vertex_size = arp_temp_data.current_vertex_size
        
        
# COLLECTION PROPERTIES DEFINITION
class bone_transform(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(name="Bone name", default="")
    head : bpy.props.FloatVectorProperty(name="Head Position", default=(0.0, 0.0, 0.0), subtype='TRANSLATION', size=3)
    tail : bpy.props.FloatVectorProperty(name="Tail Position", default=(0.0, 0.0, 0.0), subtype='TRANSLATION', size=3)
    roll : bpy.props.FloatProperty(name="Head Position", default=0.0)
    
class markers_transform(bpy.types.PropertyGroup):
    location : bpy.props.FloatVectorProperty(name="Position", default=(0.0,0.0,0.0), subtype='TRANSLATION', size=3)
    
    
class facial_markers_transform(bpy.types.PropertyGroup):
    location : bpy.props.FloatVectorProperty(name="Position", default=(0.0,0.0,0.0), subtype='TRANSLATION', size=3)
    id : bpy.props.IntProperty(name="Vertex Id")

# END FUNCTIONS

###########  UI PANEL  ###################

class ARP_PT_proxy_utils_ui(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ARP" 
    bl_label = "Auto-Rig Pro: Smart"
    bl_idname = "id_auto_rig_detect"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    # panel visibility conditions   
    def poll(cls, context):
        if context.mode == 'POSE' or context.mode == 'OBJECT' or context.mode == 'EDIT_ARMATURE' or context.mode == 'EDIT_MESH':
            return True
        else:
            return False
        
    #draw
    def draw(self, context):
        global custom_icons
        layout = self.layout
        scene = context.scene
        col = layout.column(align=False)
        
        button_state = 0
        
        #BUTTONS      

        if bpy.data.objects.get("arp_markers"):         
            button_state = 1
            
            if bpy.data.objects.get("neck_loc"):                
                button_state = 2
            
            if bpy.data.objects.get("chin_loc"):                    
                button_state = 3        
                
            if bpy.data.objects.get("shoulder_loc"):                    
                button_state = 4
            
            if bpy.data.objects.get("hand_loc"):            
                button_state = 5
            
            if bpy.data.objects.get("root_loc"):            
                button_state = 6
            
            if bpy.data.objects.get("foot_loc"):                
                button_state = 7
            
            if bpy.data.objects.get("arp_facial_setup"):                    
                button_state = 8    
        
                
        if button_state == 0:
            layout.operator("id.set_front_view", text="Get Selected Objects")
        
        if button_state == 1:    
            col = layout.column(align=True)
            split=col.split(align=True)
            #row.alignment = 'LEFT'
            split.label(text="Turn:")
            btn = split.operator("id.turn", text="", icon_value=custom_icons["rotate"].icon_id)
            btn.action = "negative"
            btn = split.operator("id.turn", text="", icon_value=custom_icons["rotate_inv"].icon_id)
            btn.action = "positive"
            props = layout.operator("id.add_marker", text="Add Neck", icon='PLUS') 
            props.body_part = "neck"        
        
            
        if button_state == 2:    
            props = layout.operator("id.add_marker", text="Add Chin", icon='PLUS') 
            props.body_part = "chin"    
            
        if button_state == 3:    
            props = layout.operator("id.add_marker", text="Add Shoulders", icon='PLUS') 
            props.body_part = "shoulder"    
        if button_state == 4:    
            props = layout.operator("id.add_marker", text="Add Wrists", icon='PLUS') 
            props.body_part = "hand"   
        if button_state == 5:    
            props = layout.operator("id.add_marker", text="Add Spine Root", icon='PLUS') 
            props.body_part = "root" 
        if button_state == 6:
            props = layout.operator("id.add_marker", text="Add Ankles", icon='PLUS') 
            props.body_part = "foot"

        

        if button_state > 6:            
            layout.label(text="Fingers Detection:")         
            layout.prop(scene, "arp_fingers_to_detect", text="")
            col = layout.column(align=True)
            if bpy.context.scene.arp_fingers_to_detect != "NONE":
                col.enabled = True
            else:
                col.enabled = False
            col.prop(scene, "arp_smart_remesh", slider=True)
            col.prop(scene, "arp_finger_thickness", slider=True)
                        
            layout.separator()
            
            layout.operator("id.facial_setup", text="Facial Setup")
            
            if button_state == 8:
                
                layout.label(text="Eyeball Object:")
                row = layout.row(align=True)                    
                row.prop_search(scene, "arp_eyeball_name", bpy.data, "objects", text="")
                op = row.operator("id.smart_pick_object", text="", icon='EYEDROPPER')
                op.op_prop = "eyeball"
                layout.operator("id.cancel_facial_setup", text="Cancel Facial")
            
            layout.operator("id.go_detect", text="Go!", icon='MOD_PARTICLES') 
            layout.separator() 
        
        
        if button_state > 0:
            
            layout.prop(scene, "arp_smart_sym")
            col = layout.column(align=True)
            #if button_state <= 7:
            
            col.operator("id.restore_markers", text="Restore Last Session", icon='RECOVER_LAST')
            col.operator("id.cancel_and_delete_markers", text="Cancel and Delete Markers", icon='PANEL_CLOSE')
            
        
        layout.separator() 
        
      

@persistent
def cleanup(dummy):
    try:
        bpy.types.SpaceView3D.draw_handler_remove(handles[0], 'WINDOW') 
        if bpy.context.scene.arp_debug_mode:
            print('Removed handler')
    except:
        if bpy.context.scene.arp_debug_mode:
            print('No handler to remove')
    
#enable markers fx if any markers already in the scene when loading the file
@persistent
def enable_markers_fx(dummy):
    if bpy.data.objects.get('arp_markers') is not None: 
        if len(bpy.data.objects['arp_markers'].children) > 0:
            print('Markers already in scene, enable Markers FX')            
            bpy.ops.id.markers_fx(active=True)
            
            
    
bpy.app.handlers.load_pre.append(cleanup)
bpy.app.handlers.load_post.append(enable_markers_fx)

###########  REGISTER  ##################
custom_icons = None
classes = (ARP_OT_pick_object, ARP_OT_facial_setup, ARP_OT_cancel_facial_setup, ARP_OT_restore_markers, ARP_OT_turn, ARP_OT_set_front_view, ARP_OT_match_ref_only, ARP_OT_go_detect, ARP_OT_markers_fx, ARP_OT_add_marker, ARP_OT_auto_detect, ARp_OT_delete_detected, ARP_OT_cancel_and_delete_markers, ARP_PT_proxy_utils_ui, bone_transform, markers_transform, facial_markers_transform)



def register():   
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls) 
        
    global custom_icons
    custom_icons = bpy.utils.previews.new()    
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    custom_icons.load("rotate", os.path.join(icons_dir, "rotate.png"), 'IMAGE')
    custom_icons.load("rotate_inv", os.path.join(icons_dir, "rotate_inv.png"), 'IMAGE')
    
    bpy.types.Scene.arp_body_name  = bpy.props.StringProperty(name="Body name", description = "Get the body object name")   
    bpy.types.Scene.arp_fingers_to_detect = bpy.props.EnumProperty(items=(('5', 'Find 5 Fingers', '5 fingers detection, from the thumb to the pinky'), ('4', 'Find 4 Fingers', '4 fingers detection, from the thumb to the ring'), ('2', 'Find 2 Fingers', '2 fingers detection, mitten like, thumb and index'), ('1', 'Find 1 Fingers', '1 fingers detection, mitten like, index only'),('NONE', 'Skip Fingers', 'No fingers detection, manual placement')), description = "How many fingers should be found on this model", name = "Fingers detection")   
    bpy.types.Scene.arp_fingers_init_transform = bpy.props.CollectionProperty(type=bone_transform)
    bpy.types.Scene.arp_quit = bpy.props.BoolProperty(name="Quit", default=False)
    bpy.types.Scene.arp_markers_save = bpy.props.CollectionProperty(type=markers_transform)
    bpy.types.Scene.arp_facial_markers_save = bpy.props.CollectionProperty(type=facial_markers_transform)
    bpy.types.Scene.arp_smart_sym = bpy.props.BoolProperty(name="Mirror", default=True, update=update_sym, description="Mirror the left (character's left side) markers and bones position to the right side")
    bpy.types.Scene.arp_foot_dir_l = bpy.props.FloatVectorProperty(name="Left Foot Direction", subtype='DIRECTION', default=(0,0,0))
    bpy.types.Scene.arp_foot_dir_r = bpy.props.FloatVectorProperty(name="Right Foot Direction", subtype='DIRECTION', default=(0,0,0))
    bpy.types.Scene.arp_eyeball_name  = bpy.props.StringProperty(name="Eyeball object name", description = "Eyeball object name")
    bpy.types.Scene.arp_smart_remesh  = bpy.props.IntProperty(name="Voxel Precision", description = "Voxel resolution for the fingers detection. Should generally not be modified, unless it gives wrong fingers detection.", default=9, soft_min=7, soft_max=10)
    bpy.types.Scene.arp_finger_thickness  = bpy.props.IntProperty(name="Finger Thickness", description = "Increase this value if the detected fingers roots position are wrong, if they go too much inward the palm", default=3, min=2, max=9)
    
    bpy.app.handlers.load_pre.append(revert_arp_changes)
    
def unregister():   
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)   
        
    global custom_icons
    bpy.utils.previews.remove(custom_icons)

    del bpy.types.Scene.arp_body_name   
    del bpy.types.Scene.arp_fingers_to_detect
    del bpy.types.Scene.arp_fingers_init_transform
    del bpy.types.Scene.arp_quit
    del bpy.types.Scene.arp_markers_save
    del bpy.types.Scene.arp_facial_markers_save
    del bpy.types.Scene.arp_smart_sym
    del bpy.types.Scene.arp_foot_dir_l
    del bpy.types.Scene.arp_foot_dir_r
    del bpy.types.Scene.arp_eyeball_name
    del bpy.types.Scene.arp_smart_remesh
    del bpy.types.Scene.arp_finger_thickness
    
    bpy.app.handlers.load_pre.remove(revert_arp_changes)


    