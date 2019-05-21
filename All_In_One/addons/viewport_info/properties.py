import bpy
from . operator import updateTextProperties

class viewportInfoCollectionGroup(bpy.types.PropertyGroup):
    
    updated_edt_text = []    
    updated_obj_text = []
    update_toggle_mode = bpy.props.StringProperty()
    obj_pre = []
       
      
    vp_info_display_panel = bpy.props.BoolProperty(
        name="",
        description="Display selected options in the viewport",
        default=False)
    
    vp_info_enabled = bpy.props.BoolProperty(
        description="Switch enabled/desable",
        default=False,
        update=updateTextProperties)
        
    # EDIT PROPERTIES
    edt_use = bpy.props.BoolProperty(
        name="Edit mode",
        description="Display of the information in edit mode",
        default=True,
        update=updateTextProperties)
    edt_options = bpy.props.BoolProperty(
        name="",
        description="Options of the edit mode",
        default=False)    
    tris_count_edt = bpy.props.BoolProperty(
        name="Tris count",
        default=True,
        update=updateTextProperties)
    verts_count_edt = bpy.props.BoolProperty(
        name="Vertex count",
        default=False,
        update=updateTextProperties) 
    faces_count_edt = bpy.props.BoolProperty(
        name="Faces count",
        default=False,
        update=updateTextProperties)
    ngons_count_edt = bpy.props.BoolProperty(
        name="Ngons count",
        default=True,
        update=updateTextProperties)
    edt_corner = bpy.props.EnumProperty(
        items=(('1', "Top L", ""),
               ('2', "Top R", ""),
               ('3', "Bot L", ""),
               ('4', "Bot R", "")),                                         
        default='1',
        name=" ")  
    edt_pos_x = bpy.props.IntProperty(name="Pos X", 
        default=29, 
        min=0, max=500)                                            
    edt_pos_y = bpy.props.IntProperty(name="Pos Y", 
        default=75, 
        min=0, max=500)
            
    # OBJECT PROPERTIES
    obj_use = bpy.props.BoolProperty(
        name="Object mode",
        description="Display of the information in object mode",
        default=True,
        update=updateTextProperties)
    obj_options = bpy.props.BoolProperty( 
        name="",  
        description="Options of the object mode",
        default=False)    
    tris_count_obj = bpy.props.BoolProperty(
        name="Tris count",
        default=True, 
        update=updateTextProperties)
    verts_count_obj = bpy.props.BoolProperty(
        name="Vertex count",
        default=False, 
        update=updateTextProperties) 
    faces_count_obj = bpy.props.BoolProperty(
        name="Face count",
        default=False, 
        update=updateTextProperties)
    ngons_count_obj = bpy.props.BoolProperty(
        name="Ngon count",
        default=True, 
        update=updateTextProperties)
    obj_corner = bpy.props.EnumProperty(
        items=(('1', "Top L", ""),
               ('2', "Top R", ""),
               ('3', "Bot L", ""),
               ('4', "Bot R", "")),                                         
        default='1',
        name=" ")
    multi_obj_enabled = bpy.props.BoolProperty(
        name="Multi object",
        description="Display the options for every selected objects",
        default=True,
        update=updateTextProperties)
    obj_pos_x = bpy.props.IntProperty(
        name="Pos X", 
        default=29, 
        min=0, max=500)                                            
    obj_pos_y = bpy.props.IntProperty(
        name="Pos Y", 
        default=75, 
        min=0, max=500)
           
    # SCULPT PROPERTIES
    sculpt_use = bpy.props.BoolProperty(
        name="Sculpt mode",
        description="Display of the information in sculpt mode",
        default=True, 
        update=updateTextProperties)
    sculpt_options = bpy.props.BoolProperty(
        name="",
        description="Options of the sculpt mode",
        default=False)
    refine_method = bpy.props.BoolProperty(
        name="Detail refine method",
        default=True, 
        update=updateTextProperties)
    detail_type = bpy.props.BoolProperty(
        name="Detail type method",
        default=True, 
        update=updateTextProperties)
    brush_radius = bpy.props.BoolProperty(
        name="Brush radius",
        default=True, 
        update=updateTextProperties)
    brush_strength = bpy.props.BoolProperty(
        name="Brush strenght",
        default=True, 
        update=updateTextProperties)
    symmetry_use = bpy.props.BoolProperty(
        name="Symetry axis",
        default=True, 
        update=updateTextProperties)
    sculpt_corner = bpy.props.EnumProperty(
        items=(('1', "Top L", ""),
               ('2', "Top R", ""),
               ('3', "Bot L", ""),
               ('4', "Bot R", "")),                                         
        default='1',
        name=" ")
    sculpt_pos_x = bpy.props.IntProperty(name="Pos X", 
        default=29, 
        min=0, max=500)                                            
    sculpt_pos_y = bpy.props.IntProperty(name="Pos Y", 
        default=75, 
        min=0, max=500)
            
    # RENDER PROPERTIES
    rder_use = bpy.props.BoolProperty(
        name="Render",
        description="Display of the information of the render",
        default=False,
        update=updateTextProperties)
    rder_options = bpy.props.BoolProperty(
        name="",
        description="Options of the render",
        default=False)
    rder_reso = bpy.props.BoolProperty(
        name="Resolution",
        default=True,
        update=updateTextProperties)
    rder_f_range = bpy.props.BoolProperty(
        name="Frame range", 
        description="Display Start frame, End frame and Frame step", 
        default=True,
        update=updateTextProperties)
    rder_f_rate = bpy.props.BoolProperty(
        name="Frame rate",
        default=True,
        update=updateTextProperties)
    rder_sample = bpy.props.BoolProperty(
        name="Sampling", 
        description="Display render and preview samples", 
        default=True,
        update=updateTextProperties) 
    rder_corner = bpy.props.EnumProperty(
        items=(('1', "Top L", ""),
               ('2', "Top R", ""),
               ('3', "Bot L", ""),
               ('4', "Bot R", "")),                                         
        default='2',
        name=" ") 
    rder_pos_x = bpy.props.IntProperty(
        name="Pos X", 
        default=29, 
        min=0, max=500)                                            
    rder_pos_y = bpy.props.IntProperty(
        name="Pos Y", 
        default=75, 
        min=0, max=500)
        
    # SCENE PROPERTIES
    scn_use = bpy.props.BoolProperty(
        name="Scene",
        description="Display of the information of the scene",
        default=False,
        update=updateTextProperties)
    scn_options = bpy.props.BoolProperty(
        name="",
        description="Options of the scene",
        default=False)
    obj_count = bpy.props.BoolProperty(
        name="Object count",
        default=True,
        update=updateTextProperties)
    cam_dist = bpy.props.BoolProperty(
        name="Distance between objects",
        default=True,
        update=updateTextProperties)
    current_frame = bpy.props.BoolProperty(
        name="Current frame",
        default=True,
        update=updateTextProperties)
    cam_focal = bpy.props.BoolProperty(
        name="Focal camera",
        default=True,
        update=updateTextProperties)
    scn_corner = bpy.props.EnumProperty(
        items=(('1', "Top L", ""),
               ('2', "Top R", ""),
               ('3', "Bot L", ""),
               ('4', "Bot R", "")),                                         
        default='4',
        name=" ") 
    scn_pos_x = bpy.props.IntProperty(
        name="Pos X", 
        default=29, 
        min=0, max=500)                                            
    scn_pos_y = bpy.props.IntProperty(
        name="Pos Y", 
        default=75, 
        min=0, max=500)
        
    # CUSTOM TEXT PROPERTIES
    options_use = bpy.props.BoolProperty(
        name="Options",
        description="Size and color text",
        default=False)
    text_font_size = bpy.props.IntProperty(
        name="Font",
        description="Font size", 
        default=18, 
        min=10, max=50)
    name_color = bpy.props.FloatVectorProperty(
        name="Name", 
        default=(0.7, 1.0, 0.7), 
        min=0, max=1, 
        subtype='COLOR')
    label_color = bpy.props.FloatVectorProperty(
        name="Label",
        default=(0.65, 0.8, 1.0),         
        min=0, max=1, 
        subtype='COLOR')
    value_color = bpy.props.FloatVectorProperty(
        name="Value", 
        default=(0.9, 0.9, 0.9), 
        min=0, max=1, 
        subtype='COLOR')
    
    # DISPLAY COLOR PROPERTIES    
    display_color_enabled = bpy.props.BoolProperty(
        name="Mesh check enabled",
        description="Display faces color",
        default=False)
    active_shade = bpy.props.StringProperty()
    matcap_enabled = bpy.props.BoolProperty(
        name="Mesh check matcap",
        description="Define if matcap enabled or disabled",
        default=False)    
    save_mat = []
    update_mode_enabled = bpy.props.BoolProperty(
        default=False)

    # SELECTION TRIS/NGONS PROPERTIES
    select_mode = bpy.props.StringProperty()   
    
