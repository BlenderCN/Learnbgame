# vertex_color_from_z_height.py

import bpy  
import random  
from mathutils import Color, Vector  
  
def remap(current, lower_old, upper_old, lower_new, upper_new):  
    '''   
    Remaps one range of values to another range of values, types must be float 
         
    arguments   :   Description 
    ---------------------------------------------------------- 
    current     :   Value to fit within the destination range 
    lower_old   :   Lowest value of the original range 
    upper_old   :   Highest value of the original range 
    lower_new   :   Lowest value of the destination range 
    upper_new   :   Highest value of the destination range 
         
    '''  
  
    # type checking, if any of the arguments are not float then return None.  
    lcheck = current, lower_old, upper_old, lower_new, upper_new  
    lstr = "current", "lower_old", "upper_old", "lower_new", "upper_new"  
      
    for i in range(len(lcheck)):  
        if lcheck[i].__class__ is not float:   
            print(lstr[i], "is not a float")  
            return None  
      
    # before calculations we can deal with some possible errors  
    if current <= lower_old: return lower_new  
    if current >= upper_old: return upper_new  
        
    # reusing a nicely coded Vector math utility :)        
    old_min = Vector((0.0, 0.0, lower_old))    
    old_max = Vector((0.0, 0.0, upper_old))    
    new_min = Vector((0.0, 0.0, lower_new))    
    new_max = Vector((0.0, 0.0, upper_new))    
        
    # calculate spread, fast and saves room!     
    spread_old = (old_max-old_min).length    
    spread_new = (new_max-new_min).length    
    factor_remap = spread_new / spread_old    
        
    current_vector = Vector((0.0, 0.0, current))    
    remap_temp = (current_vector-old_min).length    
    remapped = (remap_temp * factor_remap) + new_min[2]    
          
    # clamp output when rounding creates values beyond new range  
    if remapped < lower_new: return lower_new    
    if remapped > upper_new: return upper_new    
    
    # value seems alright!      
    return remapped


def create_vertex_color_map():
    # Find upper and lower z values.  
    # there are many ways to skin this cat, but i'm going to be lazy  
    z_list = []  
    for i in bpy.context.active_object.data.vertices:  
        z_list.append(i.co.z)  
          
    z_list = sorted(z_list)  
      
    lower_old = z_list[0]  
    upper_old = z_list[len(z_list)-1]  
    lower_new = 0.0  
    upper_new = 1.0  


    my_object = bpy.context.active_object.data
    vert_list = my_object.vertices
    color_map = my_object.vertex_colors.new()

    i = 0
    for poly in my_object.polygons:
        for idx in poly.loop_indices:
            loop = my_object.loops[idx]
            v = loop.vertex_index
            zheight = vert_list[v].co.z  
            remap_1 = remap(zheight, lower_old, upper_old, lower_new, upper_new) 

            color_map.data[i].color = Color((remap_1, remap_1, remap_1))
            i += 1

    