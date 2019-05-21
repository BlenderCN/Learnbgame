import bpy
import bmesh
from math import sqrt
from . properties import * 



        ######################################
        ####    DISPLAY TEXT FONCTIONS    ####
        ######################################  
        
          
def editInfo():        
    show_text = bpy.context.window_manager.show_text
    show_text.updated_edt_text[:] = []                                      
    label_color = show_text.label_color
    value_color = show_text.value_color
    CR = "Carriage return"         
    
    ob = bpy.context.object
    me = ob.data
    bm = bmesh.from_edit_mesh(me)
    
    quads = tris = ngons = 0
    ngons_to_tris = 0             
    
    for f in bm.faces:                
        v = len(f.verts)
        if v == 3: # tris
            tris += 1
            if show_text.display_color_enabled:
                f.material_index = 2
        elif v == 4: # quads
            quads += 1 
            if show_text.display_color_enabled:
                f.material_index = 0 
        elif v > 4: # ngons
            ngons += 1            
            V = len(f.verts) - 2 # nomber of tris in ngons
            ngons_to_tris += V # get total tris of total ngons 
            if show_text.display_color_enabled:  
                f.material_index = 1 
                
    bmesh.update_edit_mesh(me)
    
    if show_text.faces_count_edt:        
        show_text.updated_edt_text.extend([CR, ("Faces: ", label_color), (str(len(bm.faces)), value_color)]) 
    if show_text.tris_count_edt:
        show_text.updated_edt_text.extend([CR, ("Tris: ", label_color), (str(tris + quads*2 + ngons_to_tris), value_color)]) 
    if show_text.ngons_count_edt:
        show_text.updated_edt_text.extend([CR, ("Ngons: ", label_color), (str(ngons), value_color)]) 
    if show_text.verts_count_edt:
        show_text.updated_edt_text.extend([CR, ("Vertex: ", label_color), (str(len(bm.verts)), value_color)])
    
        
        

def trisCount():   
    quads = tris = ngons = 0
    ngons_to_tris = 0
    
    ob = bpy.context.active_object 
    for p in ob.data.polygons:
        count = p.loop_total
        if count == 3:
            tris += 1                    
        elif count == 4:
            quads += 1
        elif count > 4:
            ngons += 1 
            V = count - 2  
            ngons_to_tris += V 
    tris_count = str(tris + quads*2 + ngons_to_tris)
    
    return tris_count

def ngonsCount():   
    ngons = 0   
    ob = bpy.context.active_object 
    for p in ob.data.polygons:
        count = p.loop_total
        if count > 4:
            ngons += 1 
            
    return str(ngons)
            
            
def objInfo():
    show_text = bpy.context.window_manager.show_text
    show_text.updated_obj_text[:] = [] 
    label_color = show_text.label_color
    value_color = show_text.value_color
    name_color = show_text.name_color
    CR = "Carriage return"
    quads = tris = ngons = 0
    ngons_to_tris = 0  
    ob = bpy.context.active_object 
    
    if len(bpy.context.selected_objects) >= 2 and show_text.multi_obj_enabled:
        for obj in bpy.context.selected_objects: 
            bpy.context.scene.objects.active = bpy.data.objects[obj.name]                        
            show_text.updated_obj_text.extend([CR, (obj.name, name_color)])
                    
            if show_text.faces_count_obj:
                faces = len(bpy.context.active_object.data.polygons)
                show_text.updated_obj_text.extend([(" F ", label_color), (str(faces) + ",", value_color)])
            if show_text.tris_count_obj:
                show_text.updated_obj_text.extend([(" T ", label_color), (trisCount() + ",", value_color)])   
            if show_text.ngons_count_obj:
                show_text.updated_obj_text.extend([(" Ng ", label_color), (ngonsCount() + ",", value_color)])
            if show_text.verts_count_obj:
                verts = len(bpy.context.active_object.data.vertices)
                show_text.updated_obj_text.extend([(" V ", label_color), (str(verts), value_color)])            
    
    else:                 
        if show_text.faces_count_obj:
            faces = len(bpy.context.active_object.data.polygons)
            show_text.updated_obj_text.extend([CR, ("Faces: ", label_color), (str(faces), value_color)]) 
        if show_text.tris_count_obj:
            show_text.updated_obj_text.extend([CR, ("Tris: ", label_color), (trisCount(), value_color)]) 
        if show_text.ngons_count_obj:
            show_text.updated_obj_text.extend([CR, ("Ngons: ", label_color), (ngonsCount(), value_color)])
        if show_text.verts_count_obj:
                verts = len(bpy.context.active_object.data.vertices)
                show_text.updated_obj_text.extend([CR, ("Vertex: ", label_color), (str(verts), value_color)])



def sculptInfo():  
    sculpt_text = []
    show_text = bpy.context.window_manager.show_text
    label_color = show_text.label_color
    value_color = show_text.value_color
    CR = "Carriage return"     
    tool_settings = bpy.context.scene.tool_settings
    Detail_Size = tool_settings.sculpt.detail_size
    if hasattr(bpy.context.tool_settings.sculpt, 'constant_detail_resolution'):
        Constant_Detail = tool_settings.sculpt.constant_detail_resolution
    else:
        Constant_Detail = tool_settings.sculpt.constant_detail 
    
    if(hasattr(tool_settings.sculpt, 'detail_percent')):
        Detail_Percent = tool_settings.sculpt.detail_percent
    active_brush = bpy.context.tool_settings.sculpt.brush.name            
    detail_refine = tool_settings.sculpt.detail_refine_method
    Detail_Type = tool_settings.sculpt.detail_type_method
    
    if bpy.context.sculpt_object.use_dynamic_topology_sculpting:
        if show_text.refine_method:                                     
            if tool_settings.sculpt.detail_type_method == 'RELATIVE':
                sculpt_text.extend([CR, (detail_refine.lower() + ": ", label_color), (str(round(Detail_Size, 2)) + " px", value_color)])
            elif tool_settings.sculpt.detail_type_method == 'CONSTANT':
                sculpt_text.extend([CR, (detail_refine.lower() + ": ", label_color), (str(round(Constant_Detail, 2)) + " %", value_color)])
            elif tool_settings.sculpt.detail_type_method == 'BRUSH':
                sculpt_text.extend([CR, (detail_refine.lower() + ": ", label_color), (str(round(Detail_Percent, 2)) + " %", value_color)])                 
        if show_text.detail_type:
            sculpt_text.extend([CR, (Detail_Type.lower(), label_color)])
            
    if show_text.brush_radius:
        sculpt_text.extend([CR, ("Radius: ", label_color), (str(tool_settings.unified_paint_settings.size) + " px", value_color)])

    if show_text.brush_strength:
        sculpt_text.extend([CR, ("Strenght: ", label_color), (str(round(bpy.data.brushes[active_brush].strength, 3)), value_color)])

    if show_text.symmetry_use:
        
        if tool_settings.sculpt.use_symmetry_x and tool_settings.sculpt.use_symmetry_y and tool_settings.sculpt.use_symmetry_z:
            sculpt_text.extend([CR, ("Symmetry: ", label_color), ("X, Y, Z", value_color)])
        elif tool_settings.sculpt.use_symmetry_x and tool_settings.sculpt.use_symmetry_y:
            sculpt_text.extend([CR, ("Symmetry: ", label_color), ("X, Y", value_color)])
        elif tool_settings.sculpt.use_symmetry_x and tool_settings.sculpt.use_symmetry_z:
            sculpt_text.extend([CR, ("Symmetry: ", label_color), ("X, Z", value_color)])
        elif tool_settings.sculpt.use_symmetry_y and tool_settings.sculpt.use_symmetry_z:
            sculpt_text.extend([CR, ("Symmetry: ", label_color), ("Y, Z", value_color)])
        elif tool_settings.sculpt.use_symmetry_x:
            sculpt_text.extend([CR, ("Symmetry: ", label_color), ("X", value_color)])
        elif tool_settings.sculpt.use_symmetry_y:
            sculpt_text.extend([CR, ("Symmetry: ", label_color), ("Y", value_color)])
        elif tool_settings.sculpt.use_symmetry_z:
            sculpt_text.extend([CR, ("Symmetry: ", label_color), ("Z", value_color)])
        else:
            sculpt_text.extend([CR, ("Symmetry: ", label_color), ("OFF", value_color)]) 
             
    return sculpt_text  
            
            
            
def renderInfo(): 
    render_text = []   
    show_text = bpy.context.window_manager.show_text
    label_color = show_text.label_color
    value_color = show_text.value_color
    CR = "Carriage return" 

    if show_text.rder_reso:
        reso_x = bpy.context.scene.render.resolution_x
        reso_y = bpy.context.scene.render.resolution_y
        render_text.extend([CR, ("Resolution: ", label_color), (str(reso_x) + " x " + str(reso_y), value_color)])
    if show_text.rder_f_range:
        f_start = bpy.context.scene.frame_start 
        f_end = bpy.context.scene.frame_end
        f_step = bpy.context.scene.frame_step
        render_text.extend([CR, ("Frame_start: ", label_color), (str(f_start), value_color), CR, ("Frame end: ", label_color), (str(f_end), value_color), CR, ("Frame step: ", label_color), (str(f_step), value_color)])
    if show_text.rder_f_rate:
        f_rate = bpy.context.scene.render.fps
        render_text.extend([CR, ("Frame rate: ", label_color), (str(f_rate) + " fps", value_color)])
    if show_text.rder_sample:
        r_sample = bpy.context.scene.cycles.samples
        r_p_sample = bpy.context.scene.cycles.preview_samples 
        render_text.extend([CR, ("Render samples: ", label_color), (str(r_sample), value_color), CR, ("Preview samples: ", label_color), (str(r_p_sample), value_color)])
    
    return render_text



def sceneInfo(): 
    scene_text = []   
    show_text = bpy.context.window_manager.show_text
    label_color = show_text.label_color
    value_color = show_text.value_color
    CR = "Carriage return" 
    
    if show_text.obj_count:
        obj_count = []
        for obj in bpy.context.selected_objects:
            obj_count.append(obj)
        scene_text.extend([CR, ("Count obj: ", label_color), (str(len(obj_count)), value_color)])
    if show_text.cam_dist:
        obj_list = []  # we store the loacation vector of each object
        for item in bpy.context.selected_objects:
            obj_list.append(item.location)
        if len(obj_list) == 2:
            distance = sqrt( (obj_list[0][0] - obj_list[1][0])**2 + (obj_list[0][1] - obj_list[1][1])**2 + (obj_list[0][2] - obj_list[1][2])**2)
            scene_text.extend([CR, ("Distance: ", label_color), (str(round(distance, 3)), value_color)])
    if show_text.current_frame:
        frame = bpy.context.scene.frame_current
        scene_text.extend([CR, ("Current frame: ", label_color), (str(frame), value_color)])
    if bpy.context.active_object.type == 'CAMERA':
        if show_text.cam_focal:
            focal = bpy.context.object.data.lens
            scene_text.extend([CR, ("Cam focal: ", label_color), (str(round(focal, 3)), value_color)])
    
    return scene_text
 



        #######################################
        ####    DISPLAY COLOR FONCTIONS    ####
        #######################################
        
        
def setupScene():
    bpy.ops.object.mode_set(mode='OBJECT')
    for slots in bpy.context.active_object.material_slots:
        bpy.ops.object.material_slot_remove() # remove all materials slots   
    bpy.ops.object.mode_set(mode='EDIT')

   
def createMat():
    show_text = bpy.context.window_manager.show_text
    if bpy.context.space_data.use_matcap:
        show_text.matcap_enabled = True
        bpy.context.space_data.use_matcap = False
                            
    # create new material        
    mat_A = bpy.data.materials.new("Quads")
    mat_A.diffuse_color = (0.865, 0.865, 0.865)

    mat_B = bpy.data.materials.new("Ngons")
    mat_B.diffuse_color = (1, 0, 0)
    
    mat_C = bpy.data.materials.new("Tris")
    mat_C.diffuse_color = (1, 1, 0)
    
    ob = bpy.context.active_object
    me = ob.data
    mat_list = [mat_A, mat_B, mat_C]
    for mat in mat_list:
        me.materials.append(mat) # assign materials

       
def restoreMat():
    setupScene()
    mat_A = bpy.data.materials['Quads']

    mat_B = bpy.data.materials['Ngons']
    
    mat_C = bpy.data.materials['Tris']
    
    ob = bpy.context.active_object
    me = ob.data
    mat_list = [mat_A, mat_B, mat_C]
    for mat in mat_list:
        me.materials.append(mat)
