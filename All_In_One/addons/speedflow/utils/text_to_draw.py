import bpy
import bgl
import blf
from math import degrees
from .fonctions import get_addon_preferences


def draw_text_callback_mpm(self, context):
    MPM = context.window_manager.MPM
 
    if MPM.bevel_enabled:
        draw_text_array_mpm(self, bevel_text(self), keys_text())
 
    elif MPM.tubify_enabled:
        draw_text_array_mpm(self, tubify_text(self), keys_text())
 
    elif MPM.symmetrize_enabled:
        draw_text_array_mpm(self, symmetrize_text(self), keys_text())
 
    elif MPM.subsurf_enabled:
        draw_text_array_mpm(self, subsurf_text(self), keys_text())  
 
    elif MPM.rotate_enabled:
        draw_text_array_mpm(self, rotate_text(self), keys_text())    
 
    elif MPM.mirror_enabled:
        draw_text_array_mpm(self, mirror_text(self), keys_text())        
 
    elif MPM.solidify_enabled:
        draw_text_array_mpm(self, solidify_text(self), keys_text())     
 
    elif MPM.array_enabled:
        draw_text_array_mpm(self, array_text(self), keys_text())
 
    elif MPM.boolean_enabled:
        draw_text_array_mpm(self, boolean_text(self), keys_text())


def draw_text_array_mpm(self, text, key_text):
    font_id = 0
    x_offset = 0
    y_offset = 0
    text_size = get_addon_preferences().text_size
    line_height = (blf.dimensions(font_id, "M")[1] * 1.45)
    first_line_width = 0
    overlap = bpy.context.user_preferences.system.use_region_overlap
    t_panel_width = 0
    if overlap:
        for region in bpy.context.area.regions:
            if region.type == 'TOOLS':
                t_panel_width = region.width
    width = bpy.context.region.width
    line_color = get_addon_preferences().text_color
    text_size = get_addon_preferences().text_size
    text_shadow = get_addon_preferences().text_shadow
    shadow_color = get_addon_preferences().shadow_color
    shadow_alpha = get_addon_preferences().shadow_alpha
    shadow_x = get_addon_preferences().offset_shadow_x
    shadow_y = get_addon_preferences().offset_shadow_y
    text_pos_x = get_addon_preferences().text_pos_x
    text_pos_y = get_addon_preferences().text_pos_y
    
    for command in text[:5]:
        if len(command) == 3:
            Text, Color, Size = command
            blf.size(font_id, Size, 72)
            text_width, text_height = blf.dimensions(font_id, Text)
            first_line_width += text_width
            
    text_line_count = text.count("Carriage return") + 1
    x = min(text_pos_x + t_panel_width + 20, width - first_line_width - 20)
    y = min((line_height + text_size)*text_line_count + text_pos_y, bpy.context.region.height - 15)    
    for command in text:
        if len(command) == 3:
            Text, Color, Size = command
            bgl.glColor3f(*Color)
            blf.size(font_id, Size, 72)
            text_width, text_height = blf.dimensions(font_id, Text)
            if text_shadow:
                blf.enable(0, blf.SHADOW)
                blf.shadow_offset(0, shadow_x, shadow_y)
                blf.shadow(0, 3, shadow_color[0], shadow_color[1], shadow_color[2], shadow_alpha)
            blf.position(font_id, (x + x_offset), (y + y_offset), 0)
            blf.draw(font_id, Text)
            x_offset += text_width

        else:
            x_offset = 0
            if command == "line":
                y_offset -= 20
                bgl.glLineWidth(text_size*0.075)
                bgl.glColor3f(*line_color)
                bgl.glEnable(bgl.GL_BLEND)
                bgl.glBegin(bgl.GL_LINES)
                bgl.glVertex2f(int(x + x_offset), int(y + y_offset))
                bgl.glVertex2f(int(x + x_offset + first_line_width), int(y + y_offset))
                bgl.glEnd()
                bgl.glLineWidth(1)
                bgl.glDisable(bgl.GL_BLEND)
                bgl.glColor3f(0, 0, 0)
            
            else:
                y_offset -= line_height + text_size
 
    keys_size = get_addon_preferences().keys_size
    line_count = key_text.count("Carriage return")        
    x_offset = 0
    y_offset = 0
    blf.size(font_id, keys_size, 72)
    line_height = (blf.dimensions(font_id, "M")[1] * 2)
    pos_x = 80 + t_panel_width
    pos_y = line_height*line_count + 70
 
    for command in key_text:
        if len(command) == 2:
            Text, Color = command
            bgl.glColor3f(*Color)
            text_width, text_height = blf.dimensions(font_id, Text)
            if text_shadow:
                blf.enable(0, blf.SHADOW)
                blf.shadow_offset(0, shadow_x, shadow_y)
                blf.shadow(0, 3, shadow_color[0], shadow_color[1], shadow_color[2], shadow_alpha)
            blf.position(font_id, (pos_x + x_offset), (pos_y + y_offset), 0)
            blf.draw(font_id, Text)
            x_offset += text_width
 
        else:
            x_offset = 0
            y_offset -= line_height
            
    if text_shadow:
        blf.disable(0, blf.SHADOW)


#Array

def get_axis_offset(self, modifier):
    MPM = bpy.context.window_manager.MPM
    index = 0  
    for i in range(3):
        if self.relative_offset_enabled:
            if modifier.relative_offset_displace[i] != 0:
                index = i
        else:
            if modifier.constant_offset_displace[i] != 0:
                index = i
    return index
            
        
def array_text(self):
    array_text = []
    MPM = bpy.context.window_manager.MPM
    text_color = get_addon_preferences().text_color
    color_1 = get_addon_preferences().text_color_1
    color_2 = get_addon_preferences().text_color_2
    text_size = get_addon_preferences().text_size
    CR = "Carriage return"
 
    if MPM.array_name:
 
        modifier = bpy.context.object.modifiers[MPM.array_name]
        axis = [" X ", " Y ", " Z "]
        
        if self.choose_start:
            array_text.extend([CR, ("Select the Start Cap" , text_color, int(text_size*2.25)), "line"])
        
        elif self.choose_end:
            array_text.extend([CR, ("Select the End Cap" , text_color, int(text_size*2.25)), "line"])
            
        elif self.choose_profile:
            array_text.extend([CR, ("Select the profile" , text_color, int(text_size*2.25)), "line"])
        
        else:
            index = get_axis_offset(self, modifier)
            if self.action_enabled == 'offset':
                if self.input:
                    array_text.extend([CR, ("Curve offset: " if self.on_curve else "Array offset  :", text_color, int(text_size*2.25)), (self.input, color_1, int(text_size*3)), "line"])
                    array_text.extend([CR, ("Press ", text_color, text_size), ("ENTER", color_1, text_size), (" to assign the value", text_color, text_size)]) 
                else:
                    array_text.extend([CR, ("Curve offset: " if self.on_curve else "Array offset  :", text_color, int(text_size*2.25)), (str(round(modifier.relative_offset_displace[index], 3)) if self.relative_offset_enabled else str(round(modifier.constant_offset_displace[index], 3)), color_1, int(text_size*3)), "line"])
            else:
                if self.input:
                    array_text.extend([CR, ("Array On Curve      " if self.on_curve else "Array ", text_color, int(text_size*2.25)), ("" if self.on_curve else "Count : ", text_color, int(text_size*1.75)), ("" if self.on_curve else self.input, color_1, int(text_size*3)),("" if modifier.show_viewport else " Hidden", (1, 0, 0), int(text_size*2.25)), "line"])
                    array_text.extend([CR, ("Press ", text_color, text_size), ("ENTER", color_1, text_size), (" to assign the value", text_color, text_size)])
                else:
                    array_text.extend([CR, ("Array On Curve      " if self.on_curve else "Array ", text_color, int(text_size*2.25)), ("" if self.on_curve else "Count : ", text_color, int(text_size*1.75)), ("" if self.on_curve else str(modifier.count), color_1, int(text_size*3)),("" if modifier.show_viewport else " Hidden", (1, 0, 0), int(text_size*2.25)), "line"])

            array_text.extend([CR, ("Active Array           : ", text_color, text_size), (axis[index], color_2, int(text_size*1.25)),(" -  ", text_color, text_size), (MPM.array_name, color_1, text_size)])
            if not self.on_curve:
                array_text.extend([CR, ("Count          (", text_color, text_size), (" S ", color_1, text_size), (")     :  ", text_color, text_size), (str(modifier.count), color_2, int(text_size*1.25))])
            array_text.extend([CR, ("Offset          (", text_color, text_size), (" D ", color_1, text_size), (")    :  ", text_color, text_size), (str(round(modifier.relative_offset_displace[index], 3)) if self.relative_offset_enabled else str(round(modifier.constant_offset_displace[index], 3)), color_2, int(text_size*1.25))]) 
            if not self.on_curve:
                array_text.extend([CR, ("Offset type  (", text_color, text_size), (" F ", color_1, text_size),(")     :  ", text_color, text_size), ("Relative" if self.relative_offset_enabled else "Constant", color_2, int(text_size*1.25))])
            if self.on_curve: 
                array_text.extend([CR, ("Select Profile          (", text_color, text_size), (" P ", color_1, text_size), (")", text_color, text_size)])
                array_text.extend([CR, ("Select Start Cap     (", text_color, text_size), (" E ", color_1, text_size), (")", text_color, text_size)])
                array_text.extend([CR, ("Select End Cap       (", text_color, text_size), (" R ", color_1, text_size), (")", text_color, text_size)])
                array_text.extend([CR, ("Change direction    (", text_color, text_size), ("X ", color_1, text_size),(",", text_color, text_size),("Y", color_1, text_size),(" or ", text_color, text_size),("Z ", color_1, text_size), (")", text_color, text_size)])
                

            array_text.extend([CR, ("Add Array    ( ", text_color, text_size), ("Shift", color_1, text_size),(" + ", text_color, text_size),("X", color_1, text_size),(",", text_color, text_size),("Y", color_1, text_size),(" or ", text_color, text_size),("Z", color_1, text_size), (" )", text_color, text_size)])
    else:
        array_text.extend([CR, ("No Array", text_color, int(text_size*2.25)), "line"])
 
    return array_text


#Bevel
def bevel_text(self):
    bevel_text = []
    MPM = bpy.context.window_manager.MPM
    text_color = get_addon_preferences().text_color
    color_1 = get_addon_preferences().text_color_1
    color_2 = get_addon_preferences().text_color_2
    text_size = get_addon_preferences().text_size
    CR = "Carriage return"
    modifier = bpy.context.active_object.modifiers["Bevel"]
    
    if self.action_enabled == 'width':
        if self.input:
            bevel_text.extend([CR, ("Bevel ", text_color, int(text_size*2.25)), ("Weight: " if (MPM.bevel_weight_enabled and not MPM.keep_bevel_weight) else "Width: ", text_color, int(text_size*1.75)), (self.input, color_1, int(text_size*3)),("" if modifier.show_viewport else " Hidden", (1, 0, 0), int(text_size*2.25)), "line"])
            bevel_text.extend([CR, ("Press ", text_color, text_size), ("ENTER", color_1, text_size), (" to assign the value", text_color, text_size)]) 
        else:
            bevel_text.extend([CR, ("Bevel ", text_color, int(text_size*2.25)), ("Weight: " if (MPM.bevel_weight_enabled and not MPM.keep_bevel_weight) else "Width: ", text_color, int(text_size*1.75)), (str(round(bpy.context.active_object.data.edges[self.edge_index].bevel_weight, 2)) if (MPM.bevel_weight_enabled and not MPM.keep_bevel_weight) else str(round(modifier.width, 2)), color_1, int(text_size*3)),("" if modifier.show_viewport else " Hidden", (1, 0, 0), int(text_size*2.25)), "line"])
    elif self.action_enabled == 'segments':
        bevel_text.extend([CR, ("Segments ", text_color, int(text_size*2.25)), (str(self.input) if self.input else str(modifier.segments), color_1, int(text_size*3)), "line"])
        if self.input:
            bevel_text.extend([CR, ("Press ", text_color, text_size), ("ENTER", color_1, text_size), (" to assign the value", text_color, text_size)])  

    elif self.action_enabled == 'profile':
        bevel_text.extend([CR, ("Profile ", text_color, int(text_size*2.25)), (str(self.input) if self.input else str(round(modifier.profile, 2)), color_1, int(text_size*3)), "line"])
        if self.input:
            bevel_text.extend([CR, ("Press ", text_color, text_size), ("ENTER", color_1, text_size), (" to assign the value", text_color, text_size)])  
 

    bevel_text.extend([CR, ("Segments          (", text_color, text_size), (" S ", color_1, text_size), (")    :  ", text_color, text_size), (str(modifier.segments), color_2, int(text_size*1.25))])
    bevel_text.extend([CR, ("Profile                (", text_color, text_size), (" D ", color_1, text_size), (")   :  ", text_color, text_size), (str(round(modifier.profile, 2)), color_2, int(text_size*1.25))])
    bevel_text.extend([CR, ("Subdiv mode     (", text_color, text_size), (" F ", color_1, text_size), (")    :  ", text_color, text_size), ("ON" if MPM.subdiv_mode else "OFF", color_2, int(text_size*1.25))])
    bevel_text.extend([CR, ("Limit Method     (", text_color, text_size), (" C ", color_1, text_size), (")    :  ", text_color, text_size), (str(modifier.limit_method), color_2, int(text_size*1.25))])

    
    return bevel_text


#Boolean
def boolean_text(self):
    boolean_text = []
    MPM = bpy.context.window_manager.MPM
    text_color = get_addon_preferences().text_color
    color_1 = get_addon_preferences().text_color_1
    color_2 = get_addon_preferences().text_color_2
    text_size = get_addon_preferences().text_size
    CR = "Carriage return"
    modifier = bpy.context.object.modifiers[MPM.boolean_name]
 
    if MPM.boolean_name:
        boolean_text.extend([CR, ("Boolean : ", text_color, int(text_size*2.25)), (modifier.operation.lower(), color_1, int(text_size*2)),("" if modifier.show_viewport else " Hidden", (1, 0, 0), int(text_size*2.25)),  "line"])
        boolean_text.extend([CR, ("Union (", text_color, text_size),(" S ", color_1, text_size), (") ", text_color, text_size), ("Difference (", text_color, text_size),(" D ", color_1, text_size), (") ", text_color, text_size), ("Intersect (", text_color, text_size),("  F  ", color_1, text_size), (") ", text_color, text_size)])  
        boolean_text.extend([CR, ("Boolean Name         :    ", text_color, text_size),(MPM.boolean_name, color_2, int(text_size*1.25))]) 
 
    else:
        boolean_text.extend([CR, ("No Boolean", text_color, int(text_size*2.25)), "line"])
 
    return boolean_text


#Mirror
def mirror_text(self):
    mirror_text = []
    MPM = bpy.context.window_manager.MPM
    text_color = get_addon_preferences().text_color
    color_1 = get_addon_preferences().text_color_1
    color_2 = get_addon_preferences().text_color_2
    text_size = get_addon_preferences().text_size
    mirror = bpy.context.active_object.modifiers[MPM.mirror_name]
    CR = "Carriage return"
 
    if MPM.mirror_name: 
        if mirror.use_x and mirror.use_z and mirror.use_y:  
            text_axis = "X, Y, Z"
        elif mirror.use_x and mirror.use_y :
            text_axis = "X, Y"
        elif mirror.use_x and mirror.use_z :
            text_axis = "X, Z"
        elif mirror.use_y and mirror.use_z :
            text_axis = "Y, Z" 
        elif mirror.use_x :
            text_axis = "X"
        elif mirror.use_y :
            text_axis = "Y"
        elif mirror.use_z :
            text_axis = "Z"
        else:
            text_axis = "No axis"
 
        mirror_text.extend([CR, (MPM.mirror_name + "  :  ", text_color, int(text_size*2.25)), (text_axis, color_1, int(text_size*3)),("" if mirror.show_viewport else " Hidden", (1, 0, 0), int(text_size*2.25)), "line"])  
        mirror_text.extend([CR, ("Add/Remove Axis (", text_color, text_size), (" Shift", color_1, text_size), ("/", text_color, text_size), ("Alt", color_1, text_size), (" + ", text_color, text_size), ("Axis", color_1, text_size), (")", text_color, text_size)])   
        if mirror.mirror_object:
            mirror_text.extend([CR, ("Ref Object            (", text_color, text_size), (" S ", color_1, text_size), (")  : ", text_color, text_size), (mirror.mirror_object.name, color_2, int(text_size*1.25))])
        else:
            mirror_text.extend([CR, ("Add Ref Object     (", text_color, text_size), (" S ", color_1, text_size), (")", text_color, text_size)]) 
        mirror_text.extend([CR, ("Merge                   (", text_color, text_size), (" D ", color_1, text_size), (") : ", text_color, text_size), (str(mirror.use_mirror_merge), color_2, int(text_size*1.25))])
        mirror_text.extend([CR, ("Clipping                 (", text_color, text_size), (" C ", color_1, text_size), (") : ", text_color, text_size), (str(mirror.use_clip), color_2, int(text_size*1.25))])
        
 
    else:
        mirror_text.extend([CR, ("No Mirror", text_color, int(text_size*2.25)), "line"])
 
    return mirror_text


#Rotate
def rotate_text(self):
    rotate_text = []
    text_color = get_addon_preferences().text_color
    color_1 = get_addon_preferences().text_color_1
    color_2 = get_addon_preferences().text_color_2
    text_size = get_addon_preferences().text_size
    CR = "Carriage return"
 
    if round(self.axis, 1) == 0 : 
        rotate_text.extend([CR, ("Rotate : ", text_color, int(text_size*2.25)), ("X ", color_1, int(text_size*3)), (str(round(degrees(bpy.context.object.rotation_euler[0]),1)).split(".")[0], color_2, int(text_size*3)), "line"])
 
    elif round(self.axis, 1) == 1 :
        rotate_text.extend([CR, ("Rotate : ", text_color, int(text_size*2.25)), ("Y ", color_1, int(text_size*3)), (str(round(degrees(bpy.context.object.rotation_euler[1]),1)).split(".")[0], color_2, int(text_size*3)), "line"])
 
    else :
        rotate_text.extend([CR, ("Rotate : ", text_color, int(text_size*2.25)), ("Z ", color_1, int(text_size*3)), (str(round(degrees(bpy.context.object.rotation_euler[2]),1)).split(".")[0], color_2, int(text_size*3)), "line"])
 
    rotate_text.extend([CR, ("Axis  (", text_color, text_size), (" X, Y, Z ", color_1, text_size), (")", text_color, text_size)])
    rotate_text.extend([CR, ("10     (", text_color, text_size), (" Shift ", color_1, text_size), (")", text_color, text_size)])
    rotate_text.extend([CR, ("5       (", text_color, text_size), (" Ctrl ", color_1, text_size), (")", text_color, text_size)])
 
    return rotate_text


#Solidify
def solidify_text(self):
    solidify_text = []
    text_color = get_addon_preferences().text_color
    color_1 = get_addon_preferences().text_color_1
    color_2 = get_addon_preferences().text_color_2
    text_size = get_addon_preferences().text_size
    CR = "Carriage return"
    modifier = bpy.context.object.modifiers["Solidify"]
    
    if self.input:
        solidify_text.extend([CR, ("Solidify : ", text_color, int(text_size*2.25)), (self.input, color_1, int(text_size*3)),("" if modifier.show_viewport else " Hidden", (1, 0, 0), int(text_size*2.25)), "line"])
        solidify_text.extend([CR, ("Press ", text_color, text_size), ("ENTER", color_1, text_size), (" to assign the value", text_color, text_size)])
    else:   
        solidify_text.extend([CR, ("Solidify : ", text_color, int(text_size*2.25)), (str(round(modifier.thickness, 2)), color_1, int(text_size*3)),("" if modifier.show_viewport else " Hidden", (1, 0, 0), int(text_size*2.25)), "line"])
    solidify_text.extend([CR, ("Even Offset   (", text_color, text_size), (" E ", color_1, text_size), (")  :      ", text_color, text_size), (str(modifier.use_even_offset), color_2, int(text_size*1.25))])
    solidify_text.extend([CR, ("Offset            (", text_color, text_size), (" O ", color_1, text_size), (")  :      ", text_color, text_size), (str(round(modifier.offset, 2)), color_2, int(text_size*1.25))])
    solidify_text.extend([CR, ("Fill Rim          (", text_color, text_size), (" R ", color_1, text_size), (")  :      ", text_color, text_size), (str(modifier.use_rim), color_2, int(text_size*1.25))])    
    solidify_text.extend([CR, ("Only Rim       (", text_color, text_size), (" T ", color_1, text_size), (")  :      ", text_color, text_size), (str(modifier.use_rim_only), color_2, int(text_size*1.25))])    
    solidify_text.extend([CR, ("Creases         (", text_color, text_size), (" C ", color_1, text_size), (")  :      ", text_color, text_size), (str(modifier.edge_crease_inner), color_2, int(text_size*1.25))])
 
    return solidify_text


#Subsurf
def subsurf_text(self):
    subsurf_text = []
    text_color = get_addon_preferences().text_color
    color_1 = get_addon_preferences().text_color_1
    color_2 = get_addon_preferences().text_color_2
    text_size = get_addon_preferences().text_size
    CR = "Carriage return"
    modifier = bpy.context.active_object.modifiers["Subsurf"]
 
    subsurf_text.extend([CR, ("Subsurf  :  ", text_color, int(text_size*2.25)), (str(round(modifier.levels, 2)), color_1, int(text_size*3)),("" if modifier.show_viewport else " Hidden", (1, 0, 0), int(text_size*2.25)), "line"])
    subsurf_text.extend([CR, ("Optimal Display (", text_color, text_size), (" S ", color_1, text_size), (") : ", text_color, text_size), (str(modifier.show_only_control_edges), color_2, int(text_size*1.25))])
    if(hasattr(bpy.context.user_preferences.system, 'opensubdiv_compute_type')):
        subsurf_text.extend([CR, ("Open subdiv      (", text_color, text_size), (" D ", color_1, text_size), (") : ", text_color, text_size), (str(modifier.use_opensubdiv), color_2, int(text_size*1.25))])
 
    return subsurf_text


#Symmetrize

def get_axis_symmetrize(self):
    axis = []
    if self.x_symmetrize:
        axis.append("X" if self.x_symmetrize == 1 else "-X")
    if self.y_symmetrize:
        axis.append("Y" if self.x_symmetrize == 1 else "-Y")
    if self.z_symmetrize:
        axis.append("Z" if self.x_symmetrize == 1 else "-Z")
    
    return axis
    
def symmetrize_text(self):
    symmetrize_text = []
    text_color = get_addon_preferences().text_color
    color_1 = get_addon_preferences().text_color_1
    color_2 = get_addon_preferences().text_color_2
    text_size = get_addon_preferences().text_size
    CR = "Carriage return"
    axis = get_axis_symmetrize(self) if get_axis_symmetrize(self) else ""
    if self.axis_value:
        symmetrize_text.extend([CR, ("Symmetrize ", text_color, int(text_size*2.25)), (self.axis_value.upper(), color_1, text_size*3), "line"])
        symmetrize_text.extend([CR, ("Click to choose side of symmetrize", text_color, text_size)])
    else:
        symmetrize_text.extend([CR, ("Symmetrize ", text_color, int(text_size*2.25)), (' '.join(axis), color_1, text_size*3), "line"])
        symmetrize_text.extend([CR, ("Select axis      ( ", text_color, text_size), ("X", color_1, text_size), (", ", text_color, text_size), ("Y", color_1, text_size), (", ", color_1, text_size), ("Z ", color_1, text_size),(")", text_color, text_size)])
        symmetrize_text.extend([CR, ("Add Axis          ( ", text_color, text_size), ("Shift", color_1, text_size), (" + ", text_color, text_size), ("axis ", color_1, text_size), (")", text_color, text_size)])
        symmetrize_text.extend([CR, ("Remove axis   ( ", text_color, text_size), ("Alt", color_1, text_size), (" + ", text_color, text_size), ("axis ", color_1, text_size), (")", text_color, text_size)])
 
    return symmetrize_text


#Tubify
def tubify_text(self):
    tubify_text = []
    text_color = get_addon_preferences().text_color
    color_1 = get_addon_preferences().text_color_1
    color_2 = get_addon_preferences().text_color_2
    text_size = get_addon_preferences().text_size
    CR = "Carriage return"
    act_obj = bpy.context.active_object
    
    if self.choose_profile:
        tubify_text.extend([CR, ("Select the profile" , text_color, int(text_size*2.25)), "line"])
    else:
        if self.input:
            if self.action_enabled == 'depth': 
                tubify_text.extend([CR, ("Tubify ", text_color, int(text_size*2.25)), ("Depth : ", text_color, int(text_size*1.75)), (self.input, color_1, int(text_size*3)), "line"])
            elif self.action_enabled == 'reso_u':
                tubify_text.extend([CR, ("Resolution ", text_color, int(text_size*2.25)), ("U : ", text_color, int(text_size*2.25)), (self.input, color_1, int(text_size*3)), "line"])
            elif self.action_enabled == 'reso_v':
                tubify_text.extend([CR, ("Resolution ", text_color, int(text_size*2.25)), ("V : ", text_color, int(text_size*2.25)), (self.input, color_1, int(text_size*3)), "line"])
            tubify_text.extend([CR, ("Press ", text_color, text_size), ("ENTER", color_1, text_size), (" to assign the value", text_color, text_size)])
            
        else:    
            if self.action_enabled == 'free':
                tubify_text.extend([CR, ("Free navigation ", text_color, int(text_size*2.25)), "line"])
            elif self.action_enabled == 'depth': 
                tubify_text.extend([CR, ("Tubify ", text_color, int(text_size*2.25)), ("Depth : ", text_color, int(text_size*1.75)), (str(round(act_obj.data.bevel_object.scale[0], 2)) if self.profile and act_obj.data.bevel_object else str(round(act_obj.data.bevel_depth, 2)), color_1, int(text_size*3)), "line"])
            elif self.action_enabled == 'reso_u':
                tubify_text.extend([CR, ("Resolution ", text_color, int(text_size*2.25)), ("U : ", text_color, int(text_size*2.25)), (str(round(act_obj.data.resolution_u, 2)), color_1, int(text_size*3)), "line"])
            elif self.action_enabled == 'reso_v':
                tubify_text.extend([CR, ("Resolution ", text_color, int(text_size*2.25)), ("V : ", text_color, int(text_size*2.25)), (str(round(act_obj.data.bevel_object.data.resolution_u, 2)) if self.profile else str(round(act_obj.data.bevel_resolution, 2)), color_1, int(text_size*3)), "line"])
        tubify_text.extend([CR, ("Tubify Depth        (", text_color, text_size), (" S ", color_1, text_size), (")      :    ", text_color, text_size), (str(round(act_obj.data.bevel_object.scale[0], 2)) if self.profile and act_obj.data.bevel_object else str(round(act_obj.data.bevel_depth, 2)), color_2, int(text_size*1.25))])               
        tubify_text.extend([CR, ("Resolution U        (", text_color, text_size), (" D ", color_1, text_size), (")     :    ", text_color, text_size), (str(round(act_obj.data.resolution_u, 2)), color_2, int(text_size*1.25))])
        tubify_text.extend([CR, ("Resolution V        (", text_color, text_size), (" F ", color_1, text_size), (")      :    ", text_color, text_size), (str(round(act_obj.data.bevel_object.data.resolution_u, 2)) if self.profile else str(round(act_obj.data.bevel_resolution, 2)), color_2, int(text_size*1.25))])
        if self.profile:
            tubify_text.extend([CR, ("Profile                   (", text_color, text_size), (" O ", color_1, text_size), (")     :    ", text_color, text_size), (str(act_obj.data.bevel_object.name), color_2, int(text_size*1.25))])

    return tubify_text


#Keys
def keys_text():
    MPM = bpy.context.window_manager.MPM
    keys_text = []
    text_color = get_addon_preferences().text_color
    color_1 = get_addon_preferences().text_color_1
    CR = "Carriage return"
    
    #Array 
    if MPM.array_enabled :
        keys_text.extend([CR, ("A         ", color_1), (": Apply Modifier", text_color)])
        keys_text.extend([CR, ("H         ", color_1), (": Hide Modifier", text_color)])
        keys_text.extend([CR, ("LEFT    ", color_1), (": Next Modifier", text_color)]) 
        keys_text.extend([CR, ("RIGHT  ", color_1), (": Previous Modifier", text_color)]) 
        keys_text.extend([CR, ("UP       ", color_1), (": Move Up", text_color)])
        keys_text.extend([CR, ("DOWN ", color_1), (": Move Down", text_color)])
        keys_text.extend([CR, ("DEL     ", color_1), (": Remove Modifier", text_color)]) 
        keys_text.extend([CR, ("ESC     ", color_1), (": Exit", text_color)])  

    #Bevel
    elif MPM.bevel_enabled:
        keys_text.extend([CR, ("A         ", color_1), (": Apply Modifier", text_color)])
        keys_text.extend([CR, ("R         ", color_1), (": Toggle bevel_weight/Modifier", text_color)])
        keys_text.extend([CR, ("G         ", color_1), (": Keep Wire Visible", text_color)])
        keys_text.extend([CR, ("H         ", color_1), (": Hide Modifier", text_color)])
        keys_text.extend([CR, ("UP       ", color_1), (": Move Up", text_color)])
        keys_text.extend([CR, ("DOWN ", color_1), (": Move Down", text_color)])
        keys_text.extend([CR, ("DEL     ", color_1), (": Remove Modifier", text_color)]) 
        keys_text.extend([CR, ("ESC     ", color_1), (": Exit", text_color)])    
    
    #Boolean    
    elif MPM.boolean_enabled :
        keys_text.extend([CR, ("A         ", color_1), (": Apply Modifier", text_color)])
        keys_text.extend([CR, ("R         ", color_1), (": Reverse Boolean", text_color)])
        keys_text.extend([CR, ("H         ", color_1), (": Hide Modifier", text_color)])
        keys_text.extend([CR, ("LEFT    ", color_1), (": Next Modifier", text_color)]) 
        keys_text.extend([CR, ("RIGHT  ", color_1), (": Previous Modifier", text_color)]) 
        keys_text.extend([CR, ("UP       ", color_1), (": Move Up", text_color)])
        keys_text.extend([CR, ("DOWN ", color_1), (": Move Down", text_color)])
        keys_text.extend([CR, ("DEL     ", color_1), (": Remove Modifier", text_color)]) 
        keys_text.extend([CR, ("ESC     ", color_1), (": Exit", text_color)])  
    
    #Mirror
    elif MPM.mirror_enabled  :
        keys_text.extend([CR, ("A         ", color_1), (": Apply Modifier", text_color)])
        keys_text.extend([CR, ("F         ", color_1), (": Add Modifier", text_color)])
        keys_text.extend([CR, ("H         ", color_1), (": Hide Modifier", text_color)])
        keys_text.extend([CR, ("LEFT    ", color_1), (": Next Modifier", text_color)]) 
        keys_text.extend([CR, ("RIGHT  ", color_1), (": Previous Modifier", text_color)]) 
        keys_text.extend([CR, ("UP       ", color_1), (": Move Up", text_color)])
        keys_text.extend([CR, ("DOWN ", color_1), (": Move Down", text_color)])
        keys_text.extend([CR, ("DEL     ", color_1), (": Remove Modifier", text_color)]) 
        keys_text.extend([CR, ("ESC     ", color_1), (": Exit", text_color)])  
    
    #Rotate
    elif MPM.rotate_enabled:  
        keys_text.extend([CR, ("  ESC", color_1), ("   : Exit", text_color)])     
    
    #Subsurf
    elif MPM.subsurf_enabled :
        keys_text.extend([CR, ("A         ", color_1), (": Apply Modifier", text_color)])
        keys_text.extend([CR, ("H         ", color_1), (": Hide Modifier", text_color)])
        keys_text.extend([CR, ("UP       ", color_1), (": Move Up", text_color)])
        keys_text.extend([CR, ("DOWN ", color_1), (": Move Down", text_color)])
        keys_text.extend([CR, ("DEL     ", color_1), (": Remove Modifier", text_color)])
        keys_text.extend([CR, ("ESC     ", color_1), (": Exit", text_color)])     
    
    #Solidify    
    elif MPM.solidify_enabled :
        keys_text.extend([CR, ("A         ", color_1), (": Apply Modifier", text_color)])
        keys_text.extend([CR, ("B         ", color_1), (": Add Bevel", text_color)])
        keys_text.extend([CR, ("S         ", color_1), (": Add Subsurf", text_color)])
        keys_text.extend([CR, ("H         ", color_1), (": Hide Modifier", text_color)])
        keys_text.extend([CR, ("UP       ", color_1), (": Move Up", text_color)])
        keys_text.extend([CR, ("DOWN ", color_1), (": Move Down", text_color)])
        keys_text.extend([CR, ("DEL     ", color_1), (": Remove Modifier", text_color)])
        keys_text.extend([CR, ("ESC     ", color_1), (": Exit", text_color)])     
    #Symmetrize    
    elif MPM.symmetrize_enabled:  
        keys_text.extend([CR, ("DEL     ", color_1), (": Remove Modifier", text_color)])  
        keys_text.extend([CR, ("ESC     ", color_1), (": Exit", text_color)])  
    
    #Tubify
    elif MPM.tubify_enabled:
        keys_text.extend([CR, ("A         ", color_1), (": Convert in Poly", text_color)])
        keys_text.extend([CR, ("G         ", color_1), (": Cyclic", text_color)])
        keys_text.extend([CR, ("Z         ", color_1), (": Select Profil", text_color)])
        keys_text.extend([CR, ("E         ", color_1), (": Add Edge Split Modifier", text_color)])
        keys_text.extend([CR, ("R         ", color_1), (": Toggle Spline Poly/Bezier", text_color)])
        keys_text.extend([CR, ("DEL     ", color_1), (": Remove Modifier", text_color)])  
        keys_text.extend([CR, ("ESC     ", color_1), (": Exit", text_color)])    
      
    return keys_text