# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy, bmesh, os, sys, inspect, webbrowser
from mathutils import Vector, Euler
from bpy.props import *
from bpy.types import PropertyGroup, UIList, Panel, Operator, Menu, Header
sys.path.append(os.path.dirname(__file__))
from bpy.utils import previews
from LF_utils import *
from LF_materials import *
from LF_custom_functions import *


bl_info = {
	"name":        "Flares Wizard (Free)",
	"description": "Add Lens flares",
	"author":      "Monaime Zaim (CodeOfArt.com)",
	"version":     (1, 1, 4),
	"blender":     (2, 7, 8),
	"wiki_url": "http://codeofart.com/flares-wizard/",
    "tracker_url": "http://codeofart.com/flares-wizard/",
	"location":    "View 3D > Tool Shelf",
	"category":    "3D View"
	}
addonFolder = inspect.getfile(inspect.currentframe())[0:-len("__init__.py")]
elementsFolder = os.path.join(addonFolder, "elements")
presetsFolder = os.path.join(addonFolder, "presets")
previewsFolder = os.path.join(addonFolder, "presets","Preview")
preview_collections = {}

          
######  Functions ########


# Generate LF previews
def flare_previews():
    LF_previews = preview_collections["LF_previews"]   

    enum_items = []
    if os.path.exists(previewsFolder):
        image_paths = []
        for fn in os.listdir(previewsFolder):
            if fn.lower().endswith(".png") or fn.lower().endswith(".jpg"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(previewsFolder, name)
            thumb = LF_previews.load(filepath, filepath, 'IMAGE')
            enum_items.append((name, name, "", thumb.icon_id, i))  

    return enum_items

# Create a new lens flare 
def Create_BLF_SYS():
    add_custom_functions()        
    
    scn = bpy.context.scene
    cam = scn.camera
    target = scn.objects.active
    BLF_name = Get_PROP_Name('BLF_SYS')
    
    #main controller
    main_cont = add_flare_object('empty', Get_OB_Name('Controller'), BLF_name, 'Lens Flare', cam)
    main_cont.constraints.new('COPY_LOCATION')
    main_cont.constraints[0].target = target
        
    # Properties
    add_prop(main_cont, 'intensity', 0.5, 0.0, 10.0, 'Global Intensity')
    add_prop(main_cont, 'scale', 1.0, 0.1, 10000.0, 'Global scale')
    add_prop(main_cont, 'layer', 0, 0, 0, '')
    add_prop(main_cont, 'opstacles', [], 0.0, 1.0, '')
    add_prop(main_cont, 'ops_samples', 16, 5, 64, 'Smoothness of the intensity transition, high value may slow down the viewport')
    add_prop(main_cont, 'ops_distance', 0.1, 0.001, 5.0, 'When the obstacle is near this distance will start to affect the lense flare')
    add_prop(main_cont, 'blk_min', 0.0, 0.0, 0.9, 'Minimum value')
    add_prop(main_cont, 'blk_seed', 1, 1, 10000, 'Random seed')
    add_prop(main_cont, 'blk_randomize', 0.0, 0.0, 1.0, 'Randomization factor')        
    add_prop(main_cont, 'blk_delay', 6, 2, 96, 'Frames between blinks')        
    add_prop(main_cont, 'in_3D_space', 0.0, 0.0, 1.0, "move the lens flare in 3d space, (0=in front of the camera, 1=target's position)")        
    add_prop(main_cont, 'z_offset', 1.0, 1.0, 100.0, "Increase the distance between the Elements to eliminate the transparency artifacts.")        
                   
    # Pivot
    pivot = add_flare_object('empty', Get_OB_Name('Pivot'), BLF_name, '', cam)
    pivot.location.z = -cam.data.lens/cam.data.sensor_width 
    pivot.constraints.new('COPY_LOCATION')
    pivot.constraints.new('LIMIT_DISTANCE')   
    pivot.constraints[1].target = cam      
    pivot.constraints[1].distance = cam.data.lens/cam.data.sensor_width
    pivot.constraints[1].limit_mode = 'LIMITDIST_ONSURFACE' 
        
    # Pivot Properties
    add_prop(pivot, 'x', 0.0, -2.0, 2.0, 'X location, 0 = the center of the camera')    
    add_prop(pivot, 'y', 0.0, -2.0, 2.0, 'Y location, 0 = the center of the camera')
    add_prop(pivot, 'intensity2', 0.0, 0.0, 1.0, '')
    add_prop(pivot, 'camera_visibility', 1.0, 0.0, 1.0, '' )
               
    #Helper object
    helper =  add_flare_object('empty', Get_OB_Name('Helper'), BLF_name, '', cam)
    helper.lock_location[0] = True
    helper.lock_location[1] = True         
       
    # Helper Drivers    
    # z axis driver
    driver = helper.driver_add("location", 2)
    add_transform_var(driver, 'Local_Z_pos', main_cont, 'LOC_Z', 'LOCAL_SPACE' )    
    driver.driver.expression = 'Local_Z_pos'
    
    # In camera checker
    cam_vis =  add_flare_object('empty', Get_OB_Name('cam_vis_check'), BLF_name, '', cam)
    cam_vis.constraints.new('LIMIT_DISTANCE')
    cam_vis.constraints[0].target = cam      
    cam_vis.constraints[0].distance = cam.data.lens/cam.data.sensor_width
    cam_vis.constraints[0].limit_mode = 'LIMITDIST_ONSURFACE' 
        
    # Proprties
    add_prop(cam_vis, 'x', 1.0, 0.0, 1000000.0, '')
    add_prop(cam_vis, 'y', 1.0, 0.0, 1000000.0, '')    
    add_prop(cam_vis, 'distance', 5.0, 0.001, 10000.0, 'Fade out distance')   
            
    # In camera Drivers
    # x axis driver
    driver = cam_vis.driver_add("location", 0)
    add_transform_var(driver, 'main', main_cont, 'LOC_X', 'LOCAL_SPACE' )
    driver.driver.expression = 'main'
    
    # y axis driver
    driver = cam_vis.driver_add("location", 1)
    add_transform_var(driver, 'main', main_cont, 'LOC_Y', 'LOCAL_SPACE' )
    driver.driver.expression = 'main'           
    
    # z axis driver
    driver = cam_vis.driver_add("location", 2)
    add_transform_var(driver, 'main', main_cont, 'LOC_Z', 'LOCAL_SPACE' )
    driver.driver.expression = 'main'
    
    # Limit distance driver
    driver = cam_vis.driver_add("constraints[0].distance")
    add_distance_var(driver, 'target_dist', main_cont, cam)
    add_distance_var(driver, 'helper_dist', helper, cam)
    add_prop_var(driver, 'focal', 'OBJECT', cam, 'data.lens')  
    add_prop_var(driver, 'lens', 'OBJECT', cam, 'data.sensor_width')
    add_transform_var(driver, 'Z_scale', cam, 'SCALE_Z', 'WORLD_SPACE')   
    driver.driver.expression = '(target_dist*Z_scale*focal/lens/max(0.01,helper_dist))'
    
    # X frame
    driver = cam_vis.driver_add('["x"]')
    add_prop_var(driver, 'resolution_x', 'SCENE', scn, 'render.resolution_x')
    add_prop_var(driver, 'resolution_y', 'SCENE', scn, 'render.resolution_y')
    driver.driver.expression = '0.5 if (resolution_x > resolution_y) else resolution_x/(resolution_y*2)'
    
    # Y frame
    driver = cam_vis.driver_add('["y"]')    
    add_prop_var(driver, 'resolution_x', 'SCENE', scn, 'render.resolution_x')
    add_prop_var(driver, 'resolution_y', 'SCENE', scn, 'render.resolution_y')
    driver.driver.expression = '0.5 if (resolution_y > resolution_x) else resolution_y/(resolution_x*2)'
    
    # Pivot Drivers    
    # x axis driver
    driver = pivot.driver_add("location", 0)
    add_prop_var(driver, 'x', 'OBJECT', pivot, '["x"]')
    driver.driver.expression = 'x'
    
    # y axis driver
    driver = pivot.driver_add("location", 1)
    add_prop_var(driver, 'y', 'OBJECT', pivot, '["y"]')
    driver.driver.expression = 'y'
    
    # Intensity driver
    driver = pivot.driver_add('["intensity2"]')
    add_prop_var(driver, 'fac', 'OBJECT', main_cont, '["intensity"]')
    add_prop_var(driver, 'cam_vis', 'OBJECT', pivot, '["camera_visibility"]')        
    driver.driver.expression = 'fac'
    
    driver = pivot.driver_add('["camera_visibility"]')
    add_prop_var(driver, 'x2', 'OBJECT', cam_vis, '["x"]')
    add_prop_var(driver, 'y2', 'OBJECT', cam_vis, '["y"]')
    add_transform_var(driver, 'x', cam_vis, 'LOC_X', 'LOCAL_SPACE')
    add_transform_var(driver, 'y', cam_vis, 'LOC_Y', 'LOCAL_SPACE')
    add_prop_var(driver, 'dis', 'OBJECT', cam_vis, '["distance"]')   
    driver.driver.expression = '1 if (abs(x)<x2 and abs(y)<y2) else max(0,(1-(abs(x)-x2)/(dis/10))) if abs(x)>x2 else max(0,(1-(abs(y)-y2)/(dis/10))) if abs(y)>y2 else 0'    
    
        
    # Update UI list
    item = scn.flare_group.coll.add()
    item.name = 'Lens flare' 
    item.object = main_cont.name
    item.pivot = pivot.name
    item.helper = helper.name
    item.cam_vis = cam_vis.name
    item.flare = BLF_name
    item.cam_vis = cam_vis.name
    item.visibility, item.opstacles = (False,False)
    item.color = [1.0,1.0,1.0,1.0]
    scn.flare_group.index = len(scn.flare_group.coll) -1
    
# Create new simple element
def Create_Simple_Element():
    add_custom_functions()
    scn = bpy.context.scene
    cam = scn.camera
    coll, index = get_flare_group()
    flare = coll[index]['flare']
        
    if len(coll)>0:
        target = scn.objects[coll[index]['object']]
        pivot = scn.objects[coll[index]['pivot']]
        helper = scn.objects[coll[index]['helper']]
        # Element controller
        ele_cont =  add_flare_object('empty', Get_OB_Name('Element_controller'), flare, '', cam)
        ele_cont.constraints.new('LIMIT_DISTANCE')   
        ele_cont.constraints[0].target = cam      
        ele_cont.constraints[0].distance = cam.data.lens/cam.data.sensor_width
        ele_cont.constraints[0].limit_mode = 'LIMITDIST_ONSURFACE'
        # properties
        add_prop(ele_cont, 'offset', 0.0, -1000.0, 1000.0, 'offset')  
                     
        # Controller's Drivers
        # x axis driver
        driver = ele_cont.driver_add("location", 0)
        add_transform_var(driver, 'main', target, 'LOC_X', 'LOCAL_SPACE')
        driver.driver.expression = 'main'        
        
        # y axis driver
        driver = ele_cont.driver_add("location", 1)
        add_transform_var(driver, 'main', target, 'LOC_Y', 'LOCAL_SPACE')
        driver.driver.expression = 'main'
                
        # z axis driver
        driver = ele_cont.driver_add("location", 2)
        add_transform_var(driver, 'main', target, 'LOC_Z', 'LOCAL_SPACE')
        add_prop_var(driver, 'Z', 'OBJECT', target, '["in_3D_space"]')
        add_prop_var(driver, 'offset', 'OBJECT', ele_cont, '["offset"]')
        add_prop_var(driver, 'Z_offset', 'OBJECT', target, '["z_offset"]')
        driver.driver.expression = 'main-(Z*offset) if Z == 0 else main-(Z*(Z_offset*offset))'
        
        # Limit distance driver
        driver = ele_cont.driver_add("constraints[0].distance")
        add_distance_var(driver, 'target_dist', target, cam)
        add_distance_var(driver, 'helper_dist', helper, cam)
        add_prop_var(driver, 'focal', 'OBJECT', cam, 'data.lens')                
        add_prop_var(driver, 'lens', 'OBJECT', cam, 'data.sensor_width')
        add_transform_var(driver, 'Z_scale', cam, 'SCALE_Z', 'WORLD_SPACE')                                
        
        offset = calc_ele_offs('simple')+(0.0001) if calc_ele_offs('simple')>0 else 0.0001
        ele_cont['offset'] = offset
        
        driver.driver.expression = 'target_dist*Z_scale*((focal/lens)+'+ str(offset)+')/max(0.01,helper_dist)'   
        
        # Limit distance driver (influence) 
        driver = ele_cont.driver_add("constraints[0].influence")
        add_prop_var(driver, 'Z', 'OBJECT', target, '["in_3D_space"]')
        driver.driver.expression = '1-Z'   
        
        # The Element
        element =  add_flare_object('plane', Get_OB_Name('Simple_Element'), flare, Get_OB_Name('Simple_Element'), cam, hide = False)       
              
        # properties        
        add_prop(element, 'pos', 0.0, -5.0, 5.0, "Position of the element, 0 = Target's posoition, 1 = Pivot's position")           
        add_prop(element, 'x', 0.0, -2.0, 2.0, 'X location offset')
        add_prop(element, 'y', 0.0, -2.0, 2.0, 'Y location offset')
        add_prop(element, 'lock_y', 0.0, 0.0, 1.0, 'Lock Y location offset')
        add_prop(element, 'rotation', 0, 0,  360, 'Rotation in degrees')
        add_prop(element, 'scale', 1.0, 0.0,  10.0, 'Scale of the element')
        add_prop(element, 'scale_x', 1.0, 0.0,  5.0, 'X scale')
        add_prop(element, 'scale_y', 1.0, 0.0,  5.0, 'Y scale')
        add_prop(element, 'ele_type', 'simple', 0.0,  1.0, '')
        add_prop(element, 'controller', ele_cont.name, 0.0,  1.0, '')
        add_prop(element, 'intensity', 1.0, 0.0,  10000.0, 'Intensity')
        # ray visibility
        set_ray_visibility(element)
        
        # drivers
        
        # Location
        # x axis driver
        driver = element.driver_add("location", 0)
        add_transform_var(driver, 'main', ele_cont, 'LOC_X', 'LOCAL_SPACE')
        add_transform_var(driver, 'pivot', pivot, 'LOC_X', 'LOCAL_SPACE')
        add_prop_var(driver, 'pos', 'OBJECT', element, '["pos"]')                 
        add_prop_var(driver, 'x', 'OBJECT', element, '["x"]')                 
        driver.driver.expression = '((1-pos)*(main+x))+ (pivot*pos)'        
        
        # y axis driver
        driver = element.driver_add("location", 1)
        add_transform_var(driver, 'main', ele_cont, 'LOC_Y', 'LOCAL_SPACE')
        add_transform_var(driver, 'pivot', pivot, 'LOC_Y', 'LOCAL_SPACE')
        add_prop_var(driver, 'pos', 'OBJECT', element, '["pos"]')                 
        add_prop_var(driver, 'y', 'OBJECT', element, '["y"]')                 
        add_prop_var(driver, 'lock_y', 'OBJECT', element, '["lock_y"]')                 
        driver.driver.expression = '((1-(pos*(1-lock_y)))*(main+y))+ (pivot*(pos*(1-lock_y)))'
                
        # z axis driver
        driver = element.driver_add("location", 2)
        add_transform_var(driver, 'main', ele_cont, 'LOC_Z', 'LOCAL_SPACE')
        driver.driver.expression = 'main'
        
        # Rortation
        driver = element.driver_add("rotation_euler", 2)
        add_prop_var(driver, 'rotation', 'OBJECT', element, '["rotation"]') 
        driver.driver.expression = 'radians(rotation)'
        
        # Scale
        # x axis
        driver = element.driver_add("scale", 0)
        add_prop_var(driver, 'x', 'OBJECT', element, '["scale_x"]') 
        add_prop_var(driver, 'scale', 'OBJECT', element, '["scale"]')
        add_prop_var(driver, 'global_scale', 'OBJECT', target, '["scale"]')
        driver.driver.expression = 'x * scale * global_scale'
        
        # y axis
        driver = element.driver_add("scale", 1)
        add_prop_var(driver, 'y', 'OBJECT', element, '["scale_y"]') 
        add_prop_var(driver, 'scale', 'OBJECT', element, '["scale"]')
        add_prop_var(driver, 'global_scale', 'OBJECT', target, '["scale"]')
        driver.driver.expression = 'y * scale * global_scale'
        
        # Constrains
        element.constraints.new('TRACK_TO')
        element.constraints[0].target = target
        element.constraints[0].track_axis = 'TRACK_X'
        element.constraints[0].owner_space = 'LOCAL'
        element.constraints[0].target_space = 'LOCAL'
        element.constraints[0].influence = 0.0
        
        element.constraints.new('LIMIT_ROTATION')
        element.constraints[1].owner_space = 'LOCAL'
        element.constraints[1].use_limit_x = True
        element.constraints[1].use_limit_y = True
        
        # Update UI list
        item = scn.element_group.coll.add()
        item.name = element[get_active_flare()]
        item.object = element.name
        item.type = element['ele_type']
        item.cont = ele_cont.name
        scn.element_group.index = len(scn.element_group.coll) -1
        
                
        # Add a material
        SimElementMat(element, os.path.join(elementsFolder, 'glow.jpg'))
        
        # driver for intensity
        material = get_active_material()        
        driver = material['Emission'].inputs[1].driver_add("default_value")
        add_prop_var(driver, 'fac', 'OBJECT', element, '["intensity"]') 
        add_prop_var(driver, 'glob', 'OBJECT', pivot, '["intensity2"]')
        driver.driver.expression = 'fac * glob'
# Add ghosts element
def Create_Ghost_Element():
    add_custom_functions()
    scn = bpy.context.scene
    cam = scn.camera
    coll, index = get_flare_group()
    flare = coll[index]['flare']
        
    if len(coll)>0:
        target = scn.objects[coll[index]['object']]
        pivot = scn.objects[coll[index]['pivot']]
        helper = scn.objects[coll[index]['helper']]
        # Element controller
        ele_cont =  add_flare_object('empty', Get_OB_Name('Element_controller'), flare, '', cam)
        ele_cont.constraints.new('LIMIT_DISTANCE')   
        ele_cont.constraints[0].target = cam      
        ele_cont.constraints[0].distance = cam.data.lens/cam.data.sensor_width
        ele_cont.constraints[0].limit_mode = 'LIMITDIST_ONSURFACE'
        # properties
        add_prop(ele_cont, 'offset', 0.0, -1000.0, 1000.0, 'offset') 
                     
        # Controller's Drivers
        # x axis driver
        driver = ele_cont.driver_add("location", 0)
        add_transform_var(driver, 'main', target, 'LOC_X', 'LOCAL_SPACE')
        driver.driver.expression = 'main'        
        
        # y axis driver
        driver = ele_cont.driver_add("location", 1)
        add_transform_var(driver, 'main', target, 'LOC_Y', 'LOCAL_SPACE')
        driver.driver.expression = 'main'
                
        # z axis driver
        driver = ele_cont.driver_add("location", 2)
        add_transform_var(driver, 'main', target, 'LOC_Z', 'LOCAL_SPACE')
        add_prop_var(driver, 'Z', 'OBJECT', target, '["in_3D_space"]')
        add_prop_var(driver, 'offset', 'OBJECT', ele_cont, '["offset"]')
        add_prop_var(driver, 'Z_offset', 'OBJECT', target, '["z_offset"]')
        driver.driver.expression = 'main-(Z*offset) if Z == 0 else main-(Z*(Z_offset*offset))'
               
        # Limit distance driver
        driver = ele_cont.driver_add("constraints[0].distance")
        add_distance_var(driver, 'target_dist', target, cam)
        add_distance_var(driver, 'helper_dist', helper, cam)
        add_prop_var(driver, 'focal', 'OBJECT', cam, 'data.lens')                
        add_prop_var(driver, 'lens', 'OBJECT', cam, 'data.sensor_width')
        add_transform_var(driver, 'Z_scale', cam, 'SCALE_Z', 'WORLD_SPACE')                
                
        offset = calc_ele_offs('ghost') +(0.01) if calc_ele_offs('ghost')>0 else 0.01
        ele_cont['offset'] = offset
        
        driver.driver.expression = 'target_dist*Z_scale*((focal/lens)+'+ str(offset)+')/max(0.01,helper_dist)'
        
        # Limit distance driver (influence) 
        driver = ele_cont.driver_add("constraints[0].influence")
        add_prop_var(driver, 'Z', 'OBJECT', target, '["in_3D_space"]')
        driver.driver.expression = '1-Z'    
        
        # The Element
        element =  add_flare_object('plane', Get_OB_Name('Ghost_Element'), flare, Get_OB_Name('Ghost_Element'), cam, hide = False)       
              
        # properties        
        add_prop(element, 'pos', 0.3, -5.0, 5.0, "Position of the element, 0 = Target's posoition, 1 = Pivot's position")           
        add_prop(element, 'x', 0.0, -2.0, 2.0, 'X location offset')
        add_prop(element, 'y', 0.0, -2.0, 2.0, 'Y location offset')
        add_prop(element, 'lock_y', 0.0, 0.0, 1.0, 'Lock Y location offset')
        add_prop(element, 'rotation', 0, 0,  360, 'Rotation in degrees')
        add_prop(element, 'scale', 0.3, 0.0,  10.0, 'Scale of the element')
        add_prop(element, 'scale_x', 1.0, 0.0,  5.0, 'X scale')
        add_prop(element, 'scale_y', 1.0, 0.0,  5.0, 'Y scale')
        add_prop(element, 'ele_type', 'ghost', 0.0,  1.0, '')
        add_prop(element, 'controller', ele_cont.name, 0.0,  1.0, '')
        add_prop(element, 'intensity', 1.0, 0.0,  10000.0, 'Intensity')
        add_prop(element, 'count', 1, 5,  99, 'Total number of ghosts')
        add_prop(element, 'distance', 0.3, 0.01,  10.0, 'Distance between ghosts')
        add_prop(element, 'random_scale', 0.0, 0.0,  1.0, 'Randomize the scale')
        add_prop(element, 'scale_seed', 1, 1,  10000, 'Random seed')
        add_prop(element, 'outline', 0.0, 0.0,  2.0, 'Outline thickness')
        
        # ray visibility
        set_ray_visibility(element)
        
        # drivers
        
        # Location
        # x axis driver
        driver = element.driver_add("location", 0)
        add_transform_var(driver, 'main', ele_cont, 'LOC_X', 'LOCAL_SPACE')
        add_transform_var(driver, 'pivot', pivot, 'LOC_X', 'LOCAL_SPACE')
        add_prop_var(driver, 'pos', 'OBJECT', element, '["pos"]')                 
        add_prop_var(driver, 'x', 'OBJECT', element, '["x"]')                 
        driver.driver.expression = '((1-pos)*(main+x))+ (pivot*pos)'        
        
        # y axis driver
        driver = element.driver_add("location", 1)
        add_transform_var(driver, 'main', ele_cont, 'LOC_Y', 'LOCAL_SPACE')
        add_transform_var(driver, 'pivot', pivot, 'LOC_Y', 'LOCAL_SPACE')
        add_prop_var(driver, 'pos', 'OBJECT', element, '["pos"]')
        add_prop_var(driver, 'lock_y', 'OBJECT', element, '["lock_y"]')                 
        add_prop_var(driver, 'y', 'OBJECT', element, '["y"]')                 
        driver.driver.expression = '((1-(pos*(1-lock_y)))*(main+y))+ (pivot*(pos*(1-lock_y)))'
                
        # z axis driver
        driver = element.driver_add("location", 2)
        add_transform_var(driver, 'main', ele_cont, 'LOC_Z', 'LOCAL_SPACE')
        driver.driver.expression = 'main'
        
        # Rortation
        driver = element.driver_add("rotation_euler", 2)
        add_prop_var(driver, 'rotation', 'OBJECT', element, '["rotation"]') 
        driver.driver.expression = 'radians(rotation)'
        
        # Scale
        # x axis
        driver = element.driver_add("scale", 0)
        add_prop_var(driver, 'x', 'OBJECT', element, '["scale_x"]') 
        add_prop_var(driver, 'min', 'OBJECT', element, '["random_scale"]') 
        add_prop_var(driver, 'seed', 'OBJECT', element, '["scale_seed"]') 
        add_prop_var(driver, 'scale', 'OBJECT', element, '["scale"]')
        add_prop_var(driver, 'global_scale', 'OBJECT', target, '["scale"]')
        driver.driver.expression = 'x * scale*randomize(1-min,seed)*global_scale'
        
        # y axis
        driver = element.driver_add("scale", 1)
        add_prop_var(driver, 'y', 'OBJECT', element, '["scale_y"]')
        add_prop_var(driver, 'min', 'OBJECT', element, '["random_scale"]') 
        add_prop_var(driver, 'seed', 'OBJECT', element, '["scale_seed"]') 
        add_prop_var(driver, 'scale', 'OBJECT', element, '["scale"]')
        add_prop_var(driver, 'global_scale', 'OBJECT', target, '["scale"]')
        driver.driver.expression = 'y * scale*randomize(1-min,seed)*global_scale'
        
        # Constrains
        element.constraints.new('LIMIT_ROTATION')
        element.constraints[0].owner_space = 'LOCAL'
        element.constraints[0].use_limit_x = True
        element.constraints[0].use_limit_y = True
        
        # Update UI list
        item = scn.element_group.coll.add()
        item.name = element[get_active_flare()]
        item.object = element.name
        item.type = element['ele_type']
        item.cont = ele_cont.name
        scn.element_group.index = len(scn.element_group.coll) -1
        
                
        # Add a material
        GhostElementMat(element, os.path.join(elementsFolder, 'circle_smooth.jpg'))
        item.ghosts_count = 5
        
        # driver for intensity
        material = get_active_material()        
        driver = material['Emission'].inputs[1].driver_add("default_value")
        add_prop_var(driver, 'fac', 'OBJECT', element, '["intensity"]') 
        add_prop_var(driver, 'glob', 'OBJECT', pivot, '["intensity2"]')
        driver.driver.expression = 'fac * glob'
        
        # driver for texture coordinates
        # x scale        
        driver = material['Mapping'].driver_add("scale", 0)
        add_prop_var(driver, 'bord', 'OBJECT', element, '["outline"]') 
        driver.driver.expression = 'bord+1'
        
        # y scale        
        driver = material['Mapping'].driver_add("scale", 1)
        add_prop_var(driver, 'bord', 'OBJECT', element, '["outline"]') 
        driver.driver.expression = 'bord+1'
        
        # x location        
        driver = material['Mapping'].driver_add("translation", 0)
        add_prop_var(driver, 'bord', 'OBJECT', element, '["outline"]') 
        driver.driver.expression = '-bord/2'
        
        # y location
        driver = material['Mapping'].driver_add("translation", 1)
        add_prop_var(driver, 'bord', 'OBJECT', element, '["outline"]') 
        driver.driver.expression = '-bord/2'

# Create new lens_dirt element
def Create_Lens_Dirt_Element():
    add_custom_functions()
    scn = bpy.context.scene
    cam = scn.camera
    coll, index = get_flare_group()
    flare = coll[index]['flare']
        
    if len(coll)>0:
        target = scn.objects[coll[index]['object']]
        pivot = scn.objects[coll[index]['pivot']]
        helper = scn.objects[coll[index]['helper']]
        # Element controller
        ele_cont =  add_flare_object('empty', Get_OB_Name('Element_controller'), flare, '', cam)
        ele_cont.constraints.new('LIMIT_DISTANCE')   
        ele_cont.constraints[0].target = cam      
        ele_cont.constraints[0].distance = cam.data.lens/cam.data.sensor_width
        ele_cont.constraints[0].limit_mode = 'LIMITDIST_ONSURFACE'
        # properties
        add_prop(ele_cont, 'offset', 0.0, -1000.0, 1000.0, 'offset')  
                     
        # Controller's Drivers
        # x axis driver
        driver = ele_cont.driver_add("location", 0)
        add_transform_var(driver, 'main', target, 'LOC_X', 'LOCAL_SPACE')
        driver.driver.expression = 'main'        
        
        # y axis driver
        driver = ele_cont.driver_add("location", 1)
        add_transform_var(driver, 'main', target, 'LOC_Y', 'LOCAL_SPACE')        
        driver.driver.expression = 'main'
                
        # z axis driver
        driver = ele_cont.driver_add("location", 2)
        add_transform_var(driver, 'main', target, 'LOC_Z', 'LOCAL_SPACE')        
        driver.driver.expression = 'main'
        
        # Limit distance driver
        driver = ele_cont.driver_add("constraints[0].distance")
        add_distance_var(driver, 'target_dist', target, cam)
        add_distance_var(driver, 'helper_dist', helper, cam)
        add_prop_var(driver, 'focal', 'OBJECT', cam, 'data.lens')                
        add_prop_var(driver, 'lens', 'OBJECT', cam, 'data.sensor_width')
        add_transform_var(driver, 'Z_scale', cam, 'SCALE_Z', 'WORLD_SPACE')                                
        
        offset = calc_ele_offs('lens_dirt')-(0.0001) if calc_ele_offs('lens_dirt') != 0 else -0.0001
        ele_cont['offset'] = offset
        
        driver.driver.expression = 'target_dist*Z_scale*((focal/lens)+'+ str(offset)+')/max(0.01,helper_dist)'   
        
        # The Element
        element =  add_flare_object('plane', Get_OB_Name('Lens_Dirt_Element'), flare, Get_OB_Name('Lens_Dirt_Element'), cam, hide = False)       
              
        # properties       
        add_prop(element, 'ele_type', 'lens_dirt', 0.0,  1.0, '')
        add_prop(element, 'controller', ele_cont.name, 0.0,  1.0, '')
        add_prop(element, 'intensity', 1.0, 0.0,  10000.0, 'Intensity')
        add_prop(element, 'scale', 1.0, 0.0,  10.0, 'Scale of the texture')
        # ray visibility
        set_ray_visibility(element)
        
        # drivers
        
        # Location
        # x axis driver
        driver = element.driver_add("location", 0)
        driver.driver.expression = '0'        
        
        # y axis driver
        driver = element.driver_add("location", 1)
        driver.driver.expression = '0'
                
        # z axis driver
        driver = element.driver_add("location", 2)
        add_transform_var(driver, 'main', ele_cont, 'LOC_Z', 'LOCAL_SPACE')
        driver.driver.expression = 'main'
        
        # scale        
        # scale x
        driver = element.driver_add("scale", 0)
        add_prop_var(driver, 'resolution_x', 'SCENE', scn, 'render.resolution_x')
        add_prop_var(driver, 'resolution_y', 'SCENE', scn, 'render.resolution_y')
        add_prop_var(driver, 'focal', 'OBJECT', cam, 'data.lens')
        add_prop_var(driver, 'lens', 'OBJECT', cam, 'data.sensor_width')
        add_transform_var(driver, 'Z', ele_cont, 'LOC_Z', 'LOCAL_SPACE')
        driver.driver.expression = str(10/3) +'*(Z/(focal/lens)) if (resolution_x > resolution_y) else (resolution_x/(resolution_y*2))*(Z/(focal/lens))*20/3'
        
        # scale y 
        driver = element.driver_add("scale", 1)
        add_prop_var(driver, 'resolution_x', 'SCENE', scn, 'render.resolution_x')
        add_prop_var(driver, 'resolution_y', 'SCENE', scn, 'render.resolution_y')
        add_prop_var(driver, 'focal', 'OBJECT', cam, 'data.lens')
        add_prop_var(driver, 'lens', 'OBJECT', cam, 'data.sensor_width')
        add_transform_var(driver, 'Z', ele_cont, 'LOC_Z', 'LOCAL_SPACE')            
        driver.driver.expression = str(10/3) +'*(Z/(focal/lens)) if (resolution_y > resolution_x) else (resolution_y/(resolution_x*2))*(Z/(focal/lens))*20/3'
             
        # Constrains        
        element.constraints.new('LIMIT_ROTATION')
        element.constraints[0].owner_space = 'LOCAL'
        element.constraints[0].use_limit_x = True
        element.constraints[0].use_limit_y = True
        element.constraints[0].use_limit_z = True
        
        # Update UI list
        item = scn.element_group.coll.add()
        item.name = element[get_active_flare()]
        item.object = element.name
        item.type = element['ele_type']
        item.cont = ele_cont.name
        scn.element_group.index = len(scn.element_group.coll) -1
        
                
        # Add a material
        LensElementMat(element, os.path.join(elementsFolder, 'lens_dirt_4.jpg'), os.path.join(elementsFolder, 'glow.jpg'))
       
        # driver for intensity
        material = get_active_material()        
        driver = material['Emission'].inputs[1].driver_add("default_value")
        add_prop_var(driver, 'fac', 'OBJECT', element, '["intensity"]') 
        add_prop_var(driver, 'glob', 'OBJECT', pivot, '["intensity2"]')
        driver.driver.expression = 'fac * glob'
        
        # drivers for texture coordinates
        # x scale
        driver = material['Mapping.001'].driver_add("scale", 0)
        add_prop_var(driver, 'scale_x', 'OBJECT', element, '["scale"]') 
        driver.driver.expression = 'scale_x'
        
        # y scale
        driver = material['Mapping.001'].driver_add("scale", 1)
        add_prop_var(driver, 'scale_y', 'OBJECT', element, '["scale"]') 
        driver.driver.expression = 'scale_y'
        
        # x location
        driver = material['Mapping.001'].driver_add("translation", 0)
        add_prop_var(driver, 'scale', 'OBJECT', element, '["scale"]')
        add_transform_var(driver, 'x', ele_cont, 'LOC_X', 'LOCAL_SPACE')
        add_transform_var(driver, 'X_scale', cam, 'SCALE_X', 'WORLD_SPACE')  
        driver.driver.expression = '0.5-x*scale*X_scale'
        
        # y location
        driver = material['Mapping.001'].driver_add("translation", 1)
        add_prop_var(driver, 'scale', 'OBJECT', element, '["scale"]')
        add_transform_var(driver, 'y', ele_cont, 'LOC_Y', 'LOCAL_SPACE')
        add_transform_var(driver, 'Y_scale', cam, 'SCALE_Y', 'WORLD_SPACE') 
        driver.driver.expression = '0.5-y*scale*Y_scale'
        
# Create new star element
def Create_Star_Element():
    add_custom_functions()
    scn = bpy.context.scene
    cam = scn.camera
    coll, index = get_flare_group()
    flare = coll[index]['flare']
        
    if len(coll)>0:
        target = scn.objects[coll[index]['object']]
        pivot = scn.objects[coll[index]['pivot']]
        helper = scn.objects[coll[index]['helper']]
        # Element controller
        ele_cont =  add_flare_object('empty', Get_OB_Name('Element_controller'), flare, '', cam)
        ele_cont.constraints.new('LIMIT_DISTANCE')   
        ele_cont.constraints[0].target = cam      
        ele_cont.constraints[0].distance = cam.data.lens/cam.data.sensor_width
        ele_cont.constraints[0].limit_mode = 'LIMITDIST_ONSURFACE'
        # properties
        add_prop(ele_cont, 'offset', 0.0, -1000.0, 1000.0, 'offset')  
                     
        # Controller's Drivers
        # x axis driver
        driver = ele_cont.driver_add("location", 0)
        add_transform_var(driver, 'main', target, 'LOC_X', 'LOCAL_SPACE')
        driver.driver.expression = 'main'        
        
        # y axis driver
        driver = ele_cont.driver_add("location", 1)
        add_transform_var(driver, 'main', target, 'LOC_Y', 'LOCAL_SPACE')
        driver.driver.expression = 'main'
                
        # z axis driver
        driver = ele_cont.driver_add("location", 2)
        add_transform_var(driver, 'main', target, 'LOC_Z', 'LOCAL_SPACE')
        add_prop_var(driver, 'Z', 'OBJECT', target, '["in_3D_space"]')
        add_prop_var(driver, 'offset', 'OBJECT', ele_cont, '["offset"]')
        add_prop_var(driver, 'Z_offset', 'OBJECT', target, '["z_offset"]')
        driver.driver.expression = 'main-(Z*offset) if Z == 0 else main-(Z*(Z_offset*offset))'
        
        
        # Limit distance driver
        driver = ele_cont.driver_add("constraints[0].distance")
        add_distance_var(driver, 'target_dist', target, cam)
        add_distance_var(driver, 'helper_dist', helper, cam)
        add_prop_var(driver, 'focal', 'OBJECT', cam, 'data.lens')                
        add_prop_var(driver, 'lens', 'OBJECT', cam, 'data.sensor_width')
        add_transform_var(driver, 'Z_scale', cam, 'SCALE_Z', 'WORLD_SPACE')                                
        
        offset = calc_ele_offs('star') +(0.021) if calc_ele_offs('star')>0 else 0.021
        ele_cont['offset'] = offset
        
        driver.driver.expression = 'target_dist*Z_scale*((focal/lens)+'+ str(offset)+')/max(0.01,helper_dist)'
        
        # Limit distance driver (influence) 
        driver = ele_cont.driver_add("constraints[0].influence")
        add_prop_var(driver, 'Z', 'OBJECT', target, '["in_3D_space"]')
        driver.driver.expression = '1-Z'    
        
        # The Element
        element =  add_flare_object('plane', Get_OB_Name('Star_Element'), flare, Get_OB_Name('Star_Element'), cam, hide = False)       
        
        # moving the verts = new origin location
        bm = bmesh.new()
        me = element.data
        bm.from_mesh(me)
        for v in bm.verts:
            v.co.y += 1.15
            bm.to_mesh(me)
        bm.free()
        
        # adding shape keys
        element.shape_key_add(name = 'Base', from_mix = False)
        element.shape_key_add(name = 'offset')
        bm = bmesh.new()
        me = element.data
        bm.from_mesh(me)
        for v in bm.verts:
            v.co.y -= 1.0
            bm.to_mesh(me)            
        bm.to_mesh(me)            
        bm.free()
          
                      
        # properties        
        add_prop(element, 'pos', 0.0, -5.0, 5.0, "Position of the element, 0 = Target's posoition, 1 = Pivot's position")           
        add_prop(element, 'x', 0.0, -2.0, 2.0, 'X location offset')
        add_prop(element, 'y', 0.0, -2.0, 2.0, 'Y location offset')
        add_prop(element, 'streaks_offset', 0.0, 0.0, 1.0, 'Streaks offset along the local Y axis')
        add_prop(element, 'rotation', 0, 0,  360, 'Rotation in degrees')
        add_prop(element, 'scale', 0.5, 0.0,  10.0, 'Scale of the element')
        add_prop(element, 'scale_x', 0.1, 0.0,  5.0, 'X scale')
        add_prop(element, 'scale_y', 1.5, 0.0,  10.0, 'Y scale')
        add_prop(element, 'ele_type', 'star', 0.0,  1.0, '')
        add_prop(element, 'controller', ele_cont.name, 0.0,  1.0, '')
        add_prop(element, 'intensity', 1.0, 0.0,  10000.0, 'Intensity')
        add_prop(element, 'count', 5, 1, 200, 'Total number of streaks')
        add_prop(element, 'angle', 360, 15, 360, 'Angle in degrees')
        add_prop(element, 'random_scale', 0.0, 0.0,  1.0, 'Randomize the scale')
        add_prop(element, 'scale_seed', 1, 1,  10000, 'Random seed')
        add_prop(element, 'color_scale', 1.0, -1.0, 2.0, 'Scale of colors along the streaks')
        add_prop(element, 'color_position', 0.0, -1.0, 1.0, 'Position of the colors')
        
        # ray visibility
        set_ray_visibility(element)
        
        # drivers
        
        # Location
        # x axis driver
        driver = element.driver_add("location", 0)
        add_transform_var(driver, 'main', ele_cont, 'LOC_X', 'LOCAL_SPACE')
        add_transform_var(driver, 'pivot', pivot, 'LOC_X', 'LOCAL_SPACE')
        add_prop_var(driver, 'pos', 'OBJECT', element, '["pos"]')                 
        add_prop_var(driver, 'x', 'OBJECT', element, '["x"]')                 
        driver.driver.expression = '((1-pos)*(main+x))+ (pivot*pos)'        
        
        # y axis driver
        driver = element.driver_add("location", 1)
        add_transform_var(driver, 'main', ele_cont, 'LOC_Y', 'LOCAL_SPACE')
        add_transform_var(driver, 'pivot', pivot, 'LOC_Y', 'LOCAL_SPACE')
        add_prop_var(driver, 'pos', 'OBJECT', element, '["pos"]')                 
        add_prop_var(driver, 'y', 'OBJECT', element, '["y"]')                 
        driver.driver.expression = '((1-pos)*(main+y))+ (pivot*pos)'
                
        # z axis driver
        driver = element.driver_add("location", 2)
        add_transform_var(driver, 'main', ele_cont, 'LOC_Z', 'LOCAL_SPACE')
        driver.driver.expression = 'main'
        
        # Rortation
        driver = element.driver_add("rotation_euler", 2)
        add_prop_var(driver, 'rotation', 'OBJECT', element, '["rotation"]') 
        driver.driver.expression = 'radians(rotation)'
        
        # Scale
        # x axis
        driver = element.driver_add("scale", 0)
        add_prop_var(driver, 'x', 'OBJECT', element, '["scale_x"]') 
        add_prop_var(driver, 'scale', 'OBJECT', element, '["scale"]')
        add_prop_var(driver, 'min', 'OBJECT', element, '["random_scale"]') 
        add_prop_var(driver, 'seed', 'OBJECT', element, '["scale_seed"]')
        add_prop_var(driver, 'global_scale', 'OBJECT', target, '["scale"]') 
        driver.driver.expression = 'x * scale*randomize(1-min,seed)*global_scale'
        
        # y axis
        driver = element.driver_add("scale", 1)
        add_prop_var(driver, 'y', 'OBJECT', element, '["scale_y"]') 
        add_prop_var(driver, 'scale', 'OBJECT', element, '["scale"]')
        add_prop_var(driver, 'min', 'OBJECT', element, '["random_scale"]') 
        add_prop_var(driver, 'seed', 'OBJECT', element, '["scale_seed"]')
        add_prop_var(driver, 'global_scale', 'OBJECT', target, '["scale"]') 
        driver.driver.expression = 'y * scale*randomize(1-min,seed)*global_scale'
        
        # driver for the shape key
        driver = element.data.shape_keys.key_blocks['offset'].driver_add('value')
        add_prop_var(driver, 'fac', 'OBJECT', element, '["streaks_offset"]') 
        driver.driver.expression = 'fac'        
        
        # Constrains
        element.constraints.new('LIMIT_ROTATION')
        element.constraints[0].owner_space = 'LOCAL'
        element.constraints[0].use_limit_x = True
        element.constraints[0].use_limit_y = True
        
        # Update UI list
        item = scn.element_group.coll.add()
        item.name = element[get_active_flare()]
        item.object = element.name
        item.type = element['ele_type']
        item.cont = ele_cont.name        
        scn.element_group.index = len(scn.element_group.coll) -1
        
                
        # Add a material
        StarElementMat(element, os.path.join(elementsFolder, 'ray1.jpg'), os.path.join(elementsFolder, 'RGB2.jpg'))
        item.streaks_count = 5
        
        # driver for intensity
        material = get_active_material()        
        driver = material['Emission'].inputs[1].driver_add("default_value")
        add_prop_var(driver, 'fac', 'OBJECT', element, '["intensity"]') 
        add_prop_var(driver, 'glob', 'OBJECT', pivot, '["intensity2"]')
        driver.driver.expression = 'fac * glob'
        # drivers for the mapping
        # y scale
        driver = material['Mapping'].driver_add("scale", 1)
        add_prop_var(driver, 'fac', 'OBJECT', element, '["color_scale"]') 
        driver.driver.expression = 'fac'
        # y position
        driver = material['Mapping'].driver_add("translation", 1)
        add_prop_var(driver, 'fac', 'OBJECT', element, '["color_position"]') 
        driver.driver.expression = 'fac'
        
# Create new background element
def Create_BG_Element():
    add_custom_functions()
    scn = bpy.context.scene
    cam = scn.camera
    coll, index = get_flare_group()
    flare = coll[index]['flare']
        
    if len(coll)>0:
        target = scn.objects[coll[index]['object']]
        pivot = scn.objects[coll[index]['pivot']]
        
        # Element controller
        ele_cont =  add_flare_object('empty', Get_OB_Name('Element_controller'), flare, '', cam)
        
        # properties
        add_prop(ele_cont, 'z_offset', 10.0, 1.0, 10000.0, 'Z offset')  
                     
        # Controller's Drivers
        # x axis driver
        driver = ele_cont.driver_add("location", 0)        
        driver.driver.expression = '0'        
        
        # y axis driver
        driver = ele_cont.driver_add("location", 1)
        driver.driver.expression = '0'
                
        # z axis driver
        driver = ele_cont.driver_add("location", 2)
        add_prop_var(driver, 'offset', 'OBJECT', ele_cont, '["z_offset"]')
        driver.driver.expression = 'offset*-1'           
        
        # The Element
        element =  add_flare_object('plane', Get_OB_Name('background_Element'), flare, Get_OB_Name('background_Element'), cam, hide = False)       
              
        # properties       
        add_prop(element, 'ele_type', 'background', 0.0,  1.0, '')
        add_prop(element, 'controller', ele_cont.name, 0.0,  1.0, '')
        add_prop(element, 'intensity', 1.0, 0.0,  1.0, 'Transparency of the background')
                
        # ray visibility
        set_ray_visibility(element)
        
        # drivers
        
        # Location
        # x axis driver
        driver = element.driver_add("location", 0)
        driver.driver.expression = '0'        
        
        # y axis driver
        driver = element.driver_add("location", 1)
        driver.driver.expression = '0'
                
        # z axis driver
        driver = element.driver_add("location", 2)
        add_transform_var(driver, 'main', ele_cont, 'LOC_Z', 'LOCAL_SPACE')
        driver.driver.expression = 'main'
        
        # scale        
        # scale x
        driver = element.driver_add("scale", 0)
        add_prop_var(driver, 'resolution_x', 'SCENE', scn, 'render.resolution_x')
        add_prop_var(driver, 'resolution_y', 'SCENE', scn, 'render.resolution_y')
        add_prop_var(driver, 'focal', 'OBJECT', cam, 'data.lens')
        add_prop_var(driver, 'lens', 'OBJECT', cam, 'data.sensor_width')
        add_transform_var(driver, 'Z', ele_cont, 'LOC_Z', 'LOCAL_SPACE')        
        driver.driver.expression = str(10/3) +'*(Z/(focal/lens)) if (resolution_x > resolution_y) else (resolution_x/(resolution_y*2))*(Z/(focal/lens))*20/3'
        
        # scale y 
        driver = element.driver_add("scale", 1)
        add_prop_var(driver, 'resolution_x', 'SCENE', scn, 'render.resolution_x')
        add_prop_var(driver, 'resolution_y', 'SCENE', scn, 'render.resolution_y')
        add_prop_var(driver, 'focal', 'OBJECT', cam, 'data.lens')
        add_prop_var(driver, 'lens', 'OBJECT', cam, 'data.sensor_width')
        add_transform_var(driver, 'Z', ele_cont, 'LOC_Z', 'LOCAL_SPACE') 
        driver.driver.expression = str(10/3) +'*(Z/(focal/lens)) if (resolution_y > resolution_x) else (resolution_y/(resolution_x*2))*(Z/(focal/lens))*20/3'
             
        # Constrains        
        element.constraints.new('LIMIT_ROTATION')
        element.constraints[0].owner_space = 'LOCAL'
        element.constraints[0].use_limit_x = True
        element.constraints[0].use_limit_y = True
        element.constraints[0].use_limit_z = True
        
        # Update UI list
        item = scn.element_group.coll.add()
        item.name = element[get_active_flare()]
        item.object = element.name
        item.type = element['ele_type']
        item.cont = ele_cont.name
        scn.element_group.index = len(scn.element_group.coll) -1
        
                
        # Add a material
        BackgroundElementMat(element, os.path.join(elementsFolder, 'black_BG.jpg'))
       
        # driver for intensity
        material = get_active_material()        
        driver = material['Mix Shader'].inputs[0].driver_add("default_value")
        add_prop_var(driver, 'fac', 'OBJECT', element, '["intensity"]')        
        driver.driver.expression = 'fac'
        
# Duplicate element
def duplicate_element(element):
    scn = bpy.context.scene
    obj = scn.objects  
    element = obj[element]
    element_mat = element.material_slots[0].material.node_tree.nodes
    type = element['ele_type']    
    coll, index = get_element_group()    
    if type == 'simple':
        Create_Simple_Element()
        duplicate = obj[get_active_element()]
        duplicate_mat = get_active_material()                
        duplicate['pos'] = element['pos']           
        duplicate['x'] = element['x']
        duplicate['y'] = element['y']
        duplicate['lock_y'] = element['lock_y']
        duplicate['rotation'] = element['rotation']
        duplicate['scale'] = element['scale']
        duplicate['scale_x'] = element['scale_x']
        duplicate['scale_y'] = element['scale_y']      
        duplicate['intensity'] = element['intensity']
        duplicate.constraints[0].influence = element.constraints[0].influence        
        
        duplicate_mat['Mix.001'].inputs[0].default_value  =  element_mat['Mix.001'].inputs[0].default_value     
        duplicate_mat['Mix'].inputs[2].default_value  =  element_mat['Mix'].inputs[2].default_value     
        duplicate_mat['Mix'].inputs[0].default_value  =  element_mat['Mix'].inputs[0].default_value     
        duplicate_mat['Image Texture'].image  =  element_mat['Image Texture'].image 
    elif type == 'ghost':
        count = element['count']
        ramp_count = len(element_mat['ColorRamp'].color_ramp.elements)
        Create_Ghost_Element()
        duplicate = obj[get_active_element()]
        duplicate_mat = get_active_material()                
        duplicate['pos'] = element['pos']           
        duplicate['x'] = element['x']
        duplicate['y'] = element['y']
        duplicate['lock_y'] = element['lock_y']
        duplicate['rotation'] = element['rotation']
        duplicate['scale'] = element['scale']
        duplicate['scale_x'] = element['scale_x']
        duplicate['scale_y'] = element['scale_y']      
        duplicate['intensity'] = element['intensity']
        duplicate['random_scale'] = element['random_scale']
        duplicate['scale_seed'] = element['scale_seed']
        duplicate['distance'] = element['distance']
        duplicate['count'] = element['count']
        duplicate['outline'] = element['outline']
        coll, index = get_element_group()
        coll[index].ghosts_count = count
        
        duplicate_mat['Mix.001'].inputs[0].default_value  =  element_mat['Mix.001'].inputs[0].default_value     
        duplicate_mat['Mix'].inputs[0].default_value  =  element_mat['Mix'].inputs[0].default_value     
        duplicate_mat['Mix.004'].inputs[1].default_value  =  element_mat['Mix.004'].inputs[1].default_value     
        duplicate_mat['Mix.004'].inputs[2].default_value  =  element_mat['Mix.004'].inputs[2].default_value     
        duplicate_mat['Mix.003'].inputs[0].default_value  =  element_mat['Mix.003'].inputs[0].default_value     
        duplicate_mat['Image Texture'].image  =  element_mat['Image Texture'].image     
        duplicate_mat['Image Texture.001'].image  =  element_mat['Image Texture.001'].image
        duplicate_mat['ColorRamp'].color_ramp.interpolation  =  element_mat['ColorRamp'].color_ramp.interpolation
        ramp_count2 = len(duplicate_mat['ColorRamp'].color_ramp.elements)
        if ramp_count > ramp_count2:
            for j in range(ramp_count-ramp_count2):
                duplicate_mat['ColorRamp'].color_ramp.elements.new(0.0)
        elif ramp_count < ramp_count2:
            for j in range(ramp_count2-ramp_count):
                duplicate_mat['ColorRamp'].color_ramp.elements.remove(duplicate_mat['ColorRamp'].color_ramp.elements[j])                    
            
        for i in range(ramp_count): 
            duplicate_mat['ColorRamp'].color_ramp.elements[i].color  =  element_mat['ColorRamp'].color_ramp.elements[i].color
            duplicate_mat['ColorRamp'].color_ramp.elements[i].position  =  element_mat['ColorRamp'].color_ramp.elements[i].position
    elif type == 'star':
        count = element['count']
        Create_Star_Element()
        duplicate = obj[get_active_element()]
        duplicate_mat = get_active_material()                
        duplicate['pos'] = element['pos']           
        duplicate['x'] = element['x']
        duplicate['y'] = element['y']
        duplicate['streaks_offset'] = element['streaks_offset']
        duplicate['rotation'] = element['rotation']
        duplicate['scale'] = element['scale']
        duplicate['scale_x'] = element['scale_x']
        duplicate['scale_y'] = element['scale_y']      
        duplicate['intensity'] = element['intensity']
        duplicate['random_scale'] = element['random_scale']
        duplicate['scale_seed'] = element['scale_seed']
        duplicate['angle'] = element['angle']
        duplicate['count'] = element['count']
        duplicate['color_position'] = element['color_position']
        duplicate['color_scale'] = element['color_scale']
        coll, index = get_element_group()
        coll[index].streaks_count = count
        
        duplicate_mat['Mix.001'].inputs[0].default_value  =  element_mat['Mix.001'].inputs[0].default_value     
        duplicate_mat['Mix'].inputs[0].default_value  =  element_mat['Mix'].inputs[0].default_value         
        duplicate_mat['Mix'].inputs[2].default_value  =  element_mat['Mix'].inputs[2].default_value          
        duplicate_mat['Mix.002'].inputs[0].default_value  =  element_mat['Mix.002'].inputs[0].default_value          
        duplicate_mat['Image Texture'].image  =  element_mat['Image Texture'].image
        duplicate_mat['Hue Saturation Value'].inputs[0].default_value  =  element_mat['Hue Saturation Value'].inputs[0].default_value
    elif type == 'lens_dirt':
        Create_Lens_Dirt_Element()
        duplicate = obj[get_active_element()]
        duplicate_mat = get_active_material()
        duplicate['intensity'] = element['intensity']
        duplicate['scale'] = element['scale']
        
        duplicate_mat['Mix.001'].inputs[0].default_value  =  element_mat['Mix.001'].inputs[0].default_value
        duplicate_mat['Mix'].inputs[2].default_value  =  element_mat['Mix'].inputs[2].default_value     
        duplicate_mat['Mix'].inputs[0].default_value  =  element_mat['Mix'].inputs[0].default_value
        duplicate_mat['Image Texture'].image  =  element_mat['Image Texture'].image
        duplicate_mat['ColorRamp'].color_ramp.elements[1].position  =  element_mat['ColorRamp'].color_ramp.elements[1].position
    elif type == 'background':
        Create_BG_Element()
        duplicate = obj[get_active_element()]
        duplicate_mat = get_active_material()
        ele_cont = obj[element['controller']]
        dupli_cont = obj[duplicate['controller']]
        duplicate['intensity'] = element['intensity']
        dupli_cont['z_offset'] = ele_cont['z_offset']
        
        duplicate_mat['Image Texture'].image  =  element_mat['Image Texture'].image                
        duplicate_mat['Image Texture'].image_user.frame_duration  =  element_mat['Image Texture'].image_user.frame_duration                
        duplicate_mat['Image Texture'].image_user.frame_start  =  element_mat['Image Texture'].image_user.frame_start               
        duplicate_mat['Image Texture'].image_user.frame_offset  =  element_mat['Image Texture'].image_user.frame_offset
        
# Duplicate Lens Flare
def duplicate_lens_flare():
    scn = bpy.context.scene
    obj = scn.objects
    coll, index = get_flare_group()
    name = coll[index].name
    color = coll[index].color
    intensity = obj[coll[index].object]['intensity']
    scale = obj[coll[index].object]['scale']
    elements = get_flare_elements()
    Create_BLF_SYS()
    coll, index = get_flare_group()
    coll[index].color = color
    coll[index].name = name
    obj[coll[index].object]['intensity'] = intensity   
    obj[coll[index].object]['scale'] = scale   
    for element in elements:
        duplicate_element(element.name)
        
# Save lens flare                  
def save_lens_flare(flare_file):
    scn = bpy.context.scene
    obj = scn.objects
    coll, index = get_flare_group()
    color = color_to_string(coll[index].color)
    intensity = obj[coll[index].object]['intensity']
    scale = obj[coll[index].object]['scale']
    elements = get_flare_elements()
    flare = get_active_flare()
    flare_name = obj[get_active_cont()][flare]
    
    
    with open(flare_file, 'w') as file:
        file.write('Create_BLF_SYS()\n')
        file.write('coll, index = get_flare_group()\n')
        file.write('controller = get_active_cont()\n')
        file.write('obj[controller][get_active_flare()] = '+'"'+ flare_name +'"'+ '\n')
        file.write('coll[index].color = '+ color + '\n')
        file.write("obj[coll[index].object]['intensity'] = "+ str(intensity) + '\n')
        file.write("obj[coll[index].object]['scale'] = "+ str(scale) + '\n')
        file.write('coll[index].name = '+'"'+ flare_name +'"'+ '\n')
        for element in elements:
            element_mat = element.material_slots[0].material.node_tree.nodes 
            if element['ele_type'] == 'simple':
                file.write('Create_Simple_Element()\n')
                file.write('duplicate = obj[get_active_element()]\n')
                file.write('duplicate_mat = get_active_material()\n')
                file.write("duplicate['pos'] = " + str(element['pos'])+ '\n')
                file.write("duplicate['x'] = " + str(element['x'])+ '\n')
                file.write("duplicate['y'] = " + str(element['y'])+ '\n')
                file.write("duplicate['lock_y'] = " + str(element['lock_y'])+ '\n')
                file.write("duplicate['rotation'] = " + str(element['rotation'])+ '\n')
                file.write("duplicate['scale'] = " + str(element['scale'])+ '\n')
                file.write("duplicate['scale_x'] = " + str(element['scale_x'])+ '\n')
                file.write("duplicate['scale_y'] = " + str(element['scale_y'])+ '\n')
                file.write("duplicate['intensity'] = " + str(element['intensity'])+ '\n')
                file.write("duplicate.constraints[0].influence = " + str(element.constraints[0].influence)+ '\n')
                file.write("duplicate_mat['Mix.001'].inputs[0].default_value  =  " + str(element_mat['Mix.001'].inputs[0].default_value)+ '\n')
                file.write("duplicate_mat['Mix'].inputs[2].default_value  =  " + color_to_string(element_mat['Mix'].inputs[2].default_value)+ '\n')     
                file.write("duplicate_mat['Mix'].inputs[0].default_value  =  " + str(element_mat['Mix'].inputs[0].default_value)+ '\n')                  
                file.write("image = load_image('"+element_mat['Image Texture'].image.name+"')"+ '\n')                  
                file.write("duplicate_mat['Image Texture'].image  =  bpy.data.images[ image ]"+ '\n')
                
            elif element['ele_type'] == 'ghost':
                file.write('Create_Ghost_Element()\n')
                file.write('coll, index = get_element_group()\n')
                file.write('duplicate = obj[get_active_element()]\n')
                file.write('duplicate_mat = get_active_material()\n')
                file.write("duplicate['pos'] = " + str(element['pos'])+ '\n')
                file.write("duplicate['x'] = " + str(element['x'])+ '\n')
                file.write("duplicate['y'] = " + str(element['y'])+ '\n')
                file.write("duplicate['lock_y'] = " + str(element['lock_y'])+ '\n')
                file.write("duplicate['rotation'] = " + str(element['rotation'])+ '\n')
                file.write("duplicate['scale'] = " + str(element['scale'])+ '\n')
                file.write("duplicate['scale_x'] = " + str(element['scale_x'])+ '\n')
                file.write("duplicate['scale_y'] = " + str(element['scale_y'])+ '\n')
                file.write("duplicate['intensity'] = " + str(element['intensity'])+ '\n')                
                file.write("duplicate['outline'] = " + str(element['outline'])+ '\n')                
                file.write("duplicate['random_scale'] = " + str(element['random_scale'])+ '\n')                
                file.write("duplicate['scale_seed'] = " + str(element['scale_seed'])+ '\n')                
                file.write("coll[index].ghosts_count = " + str(element['count'])+ '\n')                
                file.write("duplicate['distance'] = " + str(element['distance'])+ '\n')                
                file.write("duplicate_mat['Mix.001'].inputs[0].default_value  =  " + str(element_mat['Mix.001'].inputs[0].default_value)+ '\n')
                file.write("duplicate_mat['Mix.004'].inputs[1].default_value  =  " + color_to_string(element_mat['Mix.004'].inputs[1].default_value)+ '\n')     
                file.write("duplicate_mat['Mix.004'].inputs[2].default_value  =  " + color_to_string(element_mat['Mix.004'].inputs[2].default_value)+ '\n')     
                file.write("duplicate_mat['Mix.003'].inputs[0].default_value  =  " + str(element_mat['Mix.003'].inputs[0].default_value)+ '\n')     
                file.write("duplicate_mat['Mix'].inputs[0].default_value  =  " + str(element_mat['Mix'].inputs[0].default_value)+ '\n')                  
                file.write("image = load_image('"+element_mat['Image Texture'].image.name+"')"+ '\n')                  
                file.write("duplicate_mat['Image Texture'].image  =  bpy.data.images[image]"+ '\n')    
                file.write("duplicate_mat['Image Texture.001'].image  =  bpy.data.images[image]"+ '\n')    
                ramp_count = len(element_mat['ColorRamp'].color_ramp.elements)
                if ramp_count > 2:
                    for j in range(ramp_count-2):
                        file.write("duplicate_mat['ColorRamp'].color_ramp.elements.new(0.0)"+ '\n')
                elif ramp_count < 2:
                    for j in range(2-ramp_count):
                        file.write("duplicate_mat['ColorRamp'].color_ramp.elements.remove(duplicate_mat['ColorRamp'].color_ramp.elements["+str(j)+"])"+ '\n')        
                
                for i in range(ramp_count): 
                    file.write("duplicate_mat['ColorRamp'].color_ramp.elements["+str(i)+"].color  =  "+ color_to_string(element_mat['ColorRamp'].color_ramp.elements[i].color)+ '\n')
                    file.write("duplicate_mat['ColorRamp'].color_ramp.elements["+str(i)+"].position  =  "+ str(element_mat['ColorRamp'].color_ramp.elements[i].position) + '\n')
                    
            elif element['ele_type'] == 'star':
                file.write('Create_Star_Element()\n')
                file.write('coll, index = get_element_group()\n')
                file.write('duplicate = obj[get_active_element()]\n')
                file.write('duplicate_mat = get_active_material()\n')
                file.write("duplicate['pos'] = " + str(element['pos'])+ '\n')
                file.write("duplicate['x'] = " + str(element['x'])+ '\n')
                file.write("duplicate['y'] = " + str(element['y'])+ '\n')
                file.write("duplicate['streaks_offset'] = " + str(element['streaks_offset'])+ '\n')
                file.write("duplicate['rotation'] = " + str(element['rotation'])+ '\n')
                file.write("duplicate['scale'] = " + str(element['scale'])+ '\n')
                file.write("duplicate['scale_x'] = " + str(element['scale_x'])+ '\n')
                file.write("duplicate['scale_y'] = " + str(element['scale_y'])+ '\n')
                file.write("duplicate['intensity'] = " + str(element['intensity'])+ '\n')                
                file.write("duplicate['random_scale'] = " + str(element['random_scale'])+ '\n')                
                file.write("duplicate['scale_seed'] = " + str(element['scale_seed'])+ '\n')                
                file.write("coll[index].streaks_count = " + str(element['count'])+ '\n')                
                file.write("duplicate['angle'] = " + str(element['angle'])+ '\n')                
                file.write("duplicate['color_position'] = " + str(element['color_position'])+ '\n')                
                file.write("duplicate['color_scale'] = " + str(element['color_scale'])+ '\n')                
                file.write("duplicate_mat['Mix.001'].inputs[0].default_value  =  " + str(element_mat['Mix.001'].inputs[0].default_value)+ '\n')
                file.write("duplicate_mat['Mix'].inputs[2].default_value  =  " + color_to_string(element_mat['Mix'].inputs[2].default_value)+ '\n')     
                file.write("duplicate_mat['Mix'].inputs[0].default_value  =  " + str(element_mat['Mix'].inputs[0].default_value)+ '\n')          
                file.write("image1 = load_image('"+element_mat['Image Texture'].image.name+"')"+ '\n')                  
                file.write("image2 = load_image('"+element_mat['Image Texture.001'].image.name+"')"+ '\n')                  
                file.write("duplicate_mat['Image Texture'].image  =  bpy.data.images[image1]"+ '\n')
                file.write("duplicate_mat['Image Texture.001'].image  =  bpy.data.images[image2]"+ '\n')
                file.write("duplicate_mat['Mix.002'].inputs[0].default_value  =  " + str(element_mat['Mix.002'].inputs[0].default_value)+ '\n')                  
                file.write("duplicate_mat['Hue Saturation Value'].inputs[0].default_value  =  " + str(element_mat['Hue Saturation Value'].inputs[0].default_value)+ '\n')
                
            elif element['ele_type'] == 'lens_dirt':
                file.write('Create_Lens_Dirt_Element()\n')
                file.write('duplicate = obj[get_active_element()]\n')
                file.write('duplicate_mat = get_active_material()\n')         
                file.write("duplicate['scale'] = " + str(element['scale'])+ '\n')               
                file.write("duplicate['intensity'] = " + str(element['intensity'])+ '\n')                
                
                file.write("duplicate_mat['Mix.001'].inputs[0].default_value  =  " + str(element_mat['Mix.001'].inputs[0].default_value)+ '\n')
                file.write("duplicate_mat['Mix'].inputs[2].default_value  =  " + color_to_string(element_mat['Mix'].inputs[2].default_value)+ '\n')     
                file.write("duplicate_mat['Mix'].inputs[0].default_value  =  " + str(element_mat['Mix'].inputs[0].default_value)+ '\n')                  
                file.write("image1 = load_image('"+element_mat['Image Texture'].image.name+"')"+ '\n')                  
                file.write("image2 = load_image('"+element_mat['Image Texture.001'].image.name+"')"+ '\n')                  
                file.write("duplicate_mat['Image Texture'].image  =  bpy.data.images[image1]"+ '\n')                      
                file.write("duplicate_mat['Image Texture.001'].image  =  bpy.data.images[image2]"+ '\n')                      
                file.write("duplicate_mat['ColorRamp'].color_ramp.elements[1].position  =  "+ str(element_mat['ColorRamp'].color_ramp.elements[1].position) + '\n')
                
            elif element['ele_type'] == 'background':
                file.write('Create_BG_Element()\n')
                file.write('duplicate = obj[get_active_element()]\n')
                file.write('duplicate_mat = get_active_material()\n')
                file.write('cont = obj[duplicate["controller"]]' +'\n')                     
                file.write("duplicate['intensity'] = " + str(element['intensity'])+ '\n')                
                file.write("cont['z_offset'] = " + str(obj[element['controller']]['z_offset'])+ '\n')
                file.write("image = load_image('"+element_mat['Image Texture'].image.name+"')"+ '\n')                  
                file.write("duplicate_mat['Image Texture'].image  =  bpy.data.images[image]"+ '\n')                                      
                        
                
                
# Load lens flare                  
def load_lens_flare(flare_file):
    scn = bpy.context.scene
    obj = scn.objects
    
    with open(flare_file, 'r') as file:
        line = file.readline()
        while (line != ""):
            exec(line)
            line = file.readline()               
    
        
# Add custom python functions for drivers
def add_custom_functions():        
    if 'LF_custom_functions.py' not in bpy.data.texts.keys():
        text = bpy.data.texts.load(os.path.join(addonFolder, 'LF_custom_functions.py'))
        exec(text.as_string())
        text.use_module = True
# Load Image
def load_image(image_name):
    image = image_name      
    if image_name not in bpy.data.images.keys():
        if os.access(os.path.join(elementsFolder, image_name), os.F_OK):
            bpy.ops.image.open(filepath = os.path.join(elementsFolder, image_name))
            image = image_name
        else:
            bpy.ops.image.open(filepath = os.path.join(elementsFolder, 'glow.jpg'))
            image = 'glow.jpg'
            print('File "' + image_name + '" not found, replaced with ' + '"glow.jpg"')
            print('Tip: make sure that all the nessecary images are inside the elements folder')
    return image         
        
# color to string
def color_to_string(color):
    col = str(Vector(color))
    col = col.replace('>', '')
    col = col.replace('<', '')
    col = col.replace('(', '((')
    col = col.replace(')', '))')
    return col

       

# Get object name
def Get_OB_Name(name):
    if bpy.data.objects.get(name) is None:
        return name
    i = 1
    while bpy.data.objects.get(name + str(i)) is not None:
        i += 1
    return name + str(i)

# Get property name
def Get_PROP_Name(name):
    Newname = name
    NotFound = True        
    i = 1
    while NotFound:
        for ob in bpy.data.objects:
            if Newname in ob.keys():
                Newname = name + str(i)
                i += 1
            else:
                NotFound = False    
    return Newname
#Get active materiale
def get_active_material():
    scn = bpy.context.scene
    obj = scn.objects    
    element = obj[get_active_element()]
    material = element.material_slots[0].material.node_tree.nodes
    return material

# Get element groupe
def get_element_group():
    coll = bpy.context.scene.element_group.coll
    index = bpy.context.scene.element_group.index    
    return (coll, index)
# Get flare groupe
def get_flare_group():
    coll = bpy.context.scene.flare_group.coll
    index = bpy.context.scene.flare_group.index   
    return (coll, index)
# Get opstacles groupe
def get_opstacles_group():
    coll = bpy.context.scene.opstacles_group.coll
    index = bpy.context.scene.opstacles_group.index   
    return (coll, index)

# get the selected objects and the active object
def get_sel_ob():
    sel_ob = bpy.context.selected_objects
    act_ob = bpy.context.active_object
    return (sel_ob, act_ob)

# restore selected objects and the active object
def restore_selection(sel_ob, act_ob):     
    bpy.ops.object.select_all(action = 'DESELECT')
    for ob in sel_ob:
        ob.select = True
    bpy.context.scene.objects.active = act_ob  

# Delete lens flare
def deleteFlare():
    coll, index = get_flare_group()
    obj = bpy.data.objects
    materials = []
    meshes = []
    
    if len(coll) >0:
        flare = coll[index]['flare']
        for ob in obj:
            if flare in ob.keys():
                if ob.type == 'MESH':
                    mesh = ob.data
                    material = None
                    if len(ob.material_slots) > 0:
                        material = ob.material_slots[0].material                       
                    if mesh not in meshes:
                        meshes.append(mesh)
                    if (material not in materials) and (material != None):
                        materials.append(material)                        
                bpy.context.scene.objects.unlink(ob)
                bpy.data.objects.remove(ob)
        if len(materials) > 0:
            for mat in materials:
                if hasattr(mat, 'users'):
                    if mat.users == 0:
                        bpy.data.materials.remove(mat)
        if len(meshes) > 0:
            for me in meshes:
                if me.users == 0:
                    bpy.data.meshes.remove(me)                                
        coll.remove(index)
        if index >0:
            bpy.context.scene.flare_group.index = (index - 1)        

# Delete lens flare element 
def deleteElement():
    coll, index = get_element_group()
    obj = bpy.data.objects
    material = None
    mesh = None    
    
    if len(coll) >0:
        type = coll[index].type
        object = coll[index].object
        cont = coll[index].cont
        if type == 'ghost' or type == 'star':
            for ob in obj:
                if object+'_Dupli' in ob.name:
                    bpy.context.scene.objects.unlink(ob)
                    bpy.data.objects.remove(ob)                               
        
        
        if obj.get(object) is not None:
            if len(obj[object].material_slots) > 0:
                material = obj[object].material_slots[0].material
            mesh = obj[object].data           
            bpy.context.scene.objects.unlink(obj[object])
            bpy.data.objects.remove(obj[object])    
                    
                        
        if material != None:
            if material.users == 0:
                bpy.data.materials.remove(material)
        if mesh != None:
            if mesh.users == 0:    
                bpy.data.meshes.remove(mesh)
        if obj.get(cont) is not None:
            bpy.context.scene.objects.unlink(obj[cont])
            bpy.data.objects.remove(obj[cont])
        coll.remove(index)        
                
        if index >0:
            bpy.context.scene.element_group.index = (index - 1)  

# Delete opstacle
def deleteOpstacle():
    coll, index = get_opstacles_group()
    if len(coll) >0:            
        list = []
        obj = bpy.context.scene.objects
        cont = obj[get_active_cont()]
        for i in cont['opstacles']:
            list.append(i)        
        list.remove(coll[index].name)   
        cont['opstacles'] = list
        coll.remove(index)
        if len(coll) >0 and index >0:        
                bpy.context.scene.opstacles_group.index = (index - 1)  
    
# add flare opstacle
def add_opstacle():
    obj = bpy.context.scene.objects
    selected = bpy.context.selected_objects
    cont = obj[get_active_cont()]
    mesh_list = cont['opstacles']
    new_mesh_list = []
    for i in mesh_list:
        new_mesh_list.append(i)
    for ob in selected:
        if ob.type == 'MESH' and 'IS_BLF' not in ob.keys():
            if ob.name not in new_mesh_list:                
                new_mesh_list.append(ob.name)        
                # Update UI list
                item = bpy.context.scene.opstacles_group.coll.add()
                item.name = ob.name 
                item.flare = get_active_flare()
                bpy.context.scene.opstacles_group.index = len(bpy.context.scene.opstacles_group.coll) -1
    obj[get_active_cont()]['opstacles'] = new_mesh_list           
    
# Get active flare
def get_active_flare():
    coll, index = get_flare_group()
    if len(coll)>0:
        return coll[index]["flare"]
    else:
        return ""
    
# get active flare controller
def get_active_cont():
    coll, index = get_flare_group()
    if len(coll)>0:
        return coll[index]["object"]
    else:
        return ""    
        
# Get active element
def get_active_element():
    coll, index = get_element_group()
    if len(coll)>0:
        return coll[index]["object"]
    else:
        return ""
    
# Get Flare elements
def get_flare_elements():
    elements = []
    if get_active_flare() != '':
        flare = get_active_flare()           
    for ob in bpy.context.scene.objects:
        if (flare in ob.keys()) and 'ele_type'in ob.keys():
            elements.append(ob)
    return elements


# calculate elements offset
def calc_ele_offs(type):
    list = [0.0]
    for ob in bpy.data.objects:
        if 'offset' in ob.keys() and 'IS_BLF' in ob.keys():
            list.append(float(ob['offset']))
    if type == 'lens_dirt':
        return min(list)
           
    return max(list)        
            
    
    
# Get ghosts duplis
def get_ghost_duplis():
    scn = bpy.context.scene
    coll, index = get_element_group()
    element = coll[index].object
    list = []
    for ob in scn.objects:
        if element+'_Dupli' in ob.name:
            list.append(ob.name)
    return list

# Show all elements
def show_all_elements():
    elements = get_flare_elements()
    for element in elements:
        element.hide = False
    if len(elements) > 0:
        elements[0].animation_data.drivers[0].driver.expression = elements[0].animation_data.drivers[0].driver.expression
           
        
# Hide all elements
def hide_all_elements():
    elements = get_flare_elements()
    for element in elements:
        element.hide = True
    if len(elements) > 0:
        elements[0].animation_data.drivers[0].driver.expression = elements[0].animation_data.drivers[0].driver.expression    
        
# solo selected element
def solo_selected_element():
    obj = bpy.context.scene.objects
    elements = get_flare_elements()
    coll, index = get_element_group()
    if len(coll) > 0:
        active_element = obj[coll[index].object]        
        for element in elements:
            element.hide = True
        active_element.hide = False 
    if len(elements) > 0:
        elements[0].animation_data.drivers[0].driver.expression = elements[0].animation_data.drivers[0].driver.expression                     
    
    
# update elements
def update_lists(self,context):
    scn = context.scene
    obj = scn.objects
    coll, index = get_flare_group()
    if len(coll)>0:        
        flare = get_active_flare()
        cont  = obj[get_active_cont()]
        if flare != "" and 'element_group' in context.scene.keys():        
            del scn["element_group"]        
            for ob in obj:
                if ('ele_type' in ob.keys()) and (flare in ob.keys()):
                    item = bpy.context.scene.element_group.coll.add()
                    item.name = ob[flare] 
                    item.object = ob.name
                    item.type = ob['ele_type']
                    if ob['ele_type'] == 'ghost':
                        item.ghosts_count = ob['count']
                    elif ob['ele_type'] == 'star':
                        item.streaks_count = ob['count']                    
                    item.cont = ob['controller']
            bpy.context.scene.element_group.index =0
        if flare != "" and 'opstacles_group' in context.scene.keys():
            del scn["opstacles_group"]
            if len(cont['opstacles']) > 0:
                for ob in cont['opstacles']:
                    item = bpy.context.scene.opstacles_group.coll.add()
                    item.name = ob
                    item.flare = flare
                bpy.context.scene.element_group.index =0
                
        # Select the target
        bpy.ops.object.select_all(action = 'DESELECT')
        target =  cont.constraints[0].target
        if target != None:
            target.select = True        
            obj.active = target
            
    return None

def update_elements():
    scn = bpy.context.scene
    obj = scn.objects
    coll, index = get_flare_group()
    if len(coll)>0:
        flare = get_active_flare()
        if flare != "" and 'element_group' in bpy.context.scene.keys():
            del scn["element_group"] 
            for ob in obj:
                if ('ele_type' in ob.keys()) and (flare in ob.keys()):
                    item = bpy.context.scene.element_group.coll.add()
                    item.name = ob[flare] 
                    item.object = ob.name
                    item.type = ob['ele_type']
                    if ob['ele_type'] == 'ghost':
                        item.ghosts_count = ob['count']
                    elif ob['ele_type'] == 'star':
                        item.streaks_count = ob['count'] 
                    item.cont = ob['controller']
            bpy.context.scene.element_group.index =0
        
# Update Color
def update_elements_color(self,context):
    obj = bpy.context.scene.objects
    flare = get_active_flare()
    coll, index = get_flare_group()
    target = obj[coll[index].object].constraints[0].target
    for e in get_flare_elements():
        e.material_slots[0].material.node_tree.nodes['Mix.001'].inputs[2].default_value = coll[index].color
    if coll[index].copy_to_lamp:
        if target != None and target.type == 'LAMP':
            target.data.color[0] = coll[index].color[0]
            target.data.color[1] = coll[index].color[1]
            target.data.color[2] = coll[index].color[2]
            if hasattr(target.data.node_tree, 'nodes'):
                for node in target.data.node_tree.nodes:
                    if node.type == 'EMISSION':
                        node.inputs[0].default_value = coll[index].color
                                      
    return None  

# Update Intensity
def update_intensity(self,context):
    obj = bpy.context.scene.objects
    coll, index = get_flare_group()
    target = obj[coll[index]['object']]
    ops_target = target.constraints[0].target
    pivot = obj[coll[index]['pivot']]
    visibility, opstacles, blinking = coll[index].visibility, coll[index].opstacles, coll[index].blinking
    driver = pivot.animation_data.drivers[2].driver
    if visibility:
        if opstacles:
            if blinking:
                driver.expression = "fac * cam_vis * Hit('"+ops_target.name + "','"+target.name+"')*blink('"+target.name+"')"                 
            else:
                driver.expression = "fac * cam_vis * Hit('"+ops_target.name + "','"+target.name+"')"
        elif blinking:
            if opstacles:
                driver.expression = "fac * cam_vis * Hit('"+ops_target.name + "','"+target.name+"')*blink('"+target.name+"')"                 
            else:
                driver.expression = "fac * cam_vis * blink('"+target.name+"')"                
        else:
            driver.expression = 'fac * cam_vis'
    elif opstacles:
        if visibility:
            driver.expression = "fac * Hit('"+ops_target.name + "','"+target.name+"')* cam_vis"
        elif visibility and blinking:
            driver.expression = "fac * Hit('"+ops_target.name + "','"+target.name+"')*blink('"+target.name+"')* cam_vis"                 
        elif blinking:
            driver.expression = "fac * Hit('"+ops_target.name + "','"+target.name+"')*blink('"+target.name+"')"                     
                
        else:
            driver.expression = "fac * Hit('"+ops_target.name + "','"+target.name+"')"                      
    elif blinking:
        if visibility:
            driver.expression = "fac * blink('"+target.name+"')* cam_vis"
        elif visibility and opstacles:
            driver.expression = "fac * Hit('"+ops_target.name + "','"+target.name+"')*blink('"+target.name+"')* cam_vis"                
        elif opstacles:
            driver.expression = "fac * Hit('"+ops_target.name + "','"+target.name+"')*blink('"+target.name+"')"                     
        else:
            driver.expression = "fac *blink('"+target.name+"')"                     
                    
    else:
        driver.expression = 'fac'    
    return None

# Update flare name
def update_flare_name(self,context):
    obj = bpy.context.scene.objects
    coll, index = get_flare_group()
    if 'object' in coll[index].keys():
        target = obj[coll[index].object] 
        flare = coll[index].flare
        target[flare] = coll[index].name
    return None

# Update element name
def update_element_name(self,context):
    obj = bpy.context.scene.objects
    if len(context.scene.element_group.coll)>0 and len(context.scene.flare_group.coll)>0:
        coll, index = get_element_group()
        coll1, index1 = get_flare_group()
        if ('object' in coll[index].keys()) and ('flare' in coll1[index1].keys()):
            target = obj[coll[index].object]
            flare = coll1[index1].flare
            target[flare] = coll[index].name
    return None
# Updat ghost element
def update_ghost_element(self, context):
    old_count = len(get_ghost_duplis())
    scn = bpy.context.scene
    obj = scn.objects
    coll, index = get_element_group()
    target = obj[get_active_cont()]
    coll1, index1 = get_flare_group()
    pivot = obj[coll1[index1]['pivot']]
    element = obj[coll[index].object]
    type = element['ele_type']
    count = coll[index].ghosts_count
    if type == 'ghost':        
        if count > old_count+1:        
            for n in range(old_count+1,count):
                mesh = element.data
                dupli = bpy.data.objects.new(element.name+'_Dupli'+str(n), mesh)            
                dupli.parent = scn.camera
                dupli.location = Vector((0, 0, 0))
                dupli.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
                dupli.hide_select = True
                scn.objects.link(dupli)
                dupli[get_active_flare()] = ''
                dupli['IS_BLF'] = ''
                dupli.draw_type = 'WIRE'
                set_ray_visibility(dupli)
                
                # drivers
                
                # Location
                # x axis driver
                driver = dupli.driver_add("location", 0)
                add_transform_var(driver, 'main', obj[coll[index].cont], 'LOC_X', 'LOCAL_SPACE')
                add_transform_var(driver, 'pivot', pivot, 'LOC_X', 'LOCAL_SPACE')
                add_prop_var(driver, 'pos', 'OBJECT', element, '["pos"]')                 
                add_prop_var(driver, 'dis', 'OBJECT', element, '["distance"]')                 
                add_prop_var(driver, 'x', 'OBJECT', element, '["x"]')                 
                driver.driver.expression = '((1-(pos+(dis *'+ str(n)+')))*(main+x))+ (pivot*(pos+(dis*'+str(n)+')))'        
                
                # y axis driver
                driver = dupli.driver_add("location", 1)
                add_transform_var(driver, 'main', obj[coll[index].cont], 'LOC_Y', 'LOCAL_SPACE')
                add_transform_var(driver, 'pivot', pivot, 'LOC_Y', 'LOCAL_SPACE')
                add_prop_var(driver, 'pos', 'OBJECT', element, '["pos"]')                 
                add_prop_var(driver, 'dis', 'OBJECT', element, '["distance"]')
                add_prop_var(driver, 'lock_y', 'OBJECT', element, '["lock_y"]')                 
                add_prop_var(driver, 'y', 'OBJECT', element, '["y"]')                 
                driver.driver.expression = '((1-(pos+(dis *'+ str(n)+'))*(1-lock_y))*(main+y))+ (pivot*(pos+(dis*'+str(n)+'))*(1-lock_y))'                
                        
                # z axis driver
                driver = dupli.driver_add("location", 2)
                add_transform_var(driver, 'main', obj[coll[index].cont], 'LOC_Z', 'LOCAL_SPACE')
                add_prop_var(driver, 'Z', 'OBJECT', target, '["z_offset"]')
                add_prop_var(driver, 'space', 'OBJECT', target, '["in_3D_space"]')
                driver.driver.expression = 'main+' +str(n*0.0001) + ' if space == 0 else main+' +str(n*0.0001) + '*Z'
                
                # Rortation
                driver = dupli.driver_add("rotation_euler", 2)
                add_prop_var(driver, 'rotation', 'OBJECT', element, '["rotation"]') 
                driver.driver.expression = 'radians(rotation)'
                
                # Scale
                # x axis
                driver = dupli.driver_add("scale", 0)
                add_prop_var(driver, 'x', 'OBJECT', element, '["scale_x"]') 
                add_prop_var(driver, 'min', 'OBJECT', element, '["random_scale"]') 
                add_prop_var(driver, 'seed', 'OBJECT', element, '["scale_seed"]')                  
                add_prop_var(driver, 'scale', 'OBJECT', element, '["scale"]')
                add_prop_var(driver, 'global_scale', 'OBJECT', target, '["scale"]')
                driver.driver.expression = "x * scale*global_scale*randomize(1-min,seed+"+str(n)+")"
                
                # y axis
                driver = dupli.driver_add("scale", 1)
                add_prop_var(driver, 'y', 'OBJECT', element, '["scale_y"]')
                add_prop_var(driver, 'min', 'OBJECT', element, '["random_scale"]') 
                add_prop_var(driver, 'seed', 'OBJECT', element, '["scale_seed"]')          
                add_prop_var(driver, 'scale', 'OBJECT', element, '["scale"]')
                add_prop_var(driver, 'global_scale', 'OBJECT', target, '["scale"]')
                driver.driver.expression = "y * scale*global_scale*randomize(1-min,seed+"+str(n)+")"
                # driver for visibility
                driver = dupli.driver_add("hide")
                add_prop_var(driver, 'visibility', 'OBJECT', element, 'hide') 
                driver.driver.expression = 'visibility'
        elif count < old_count+1:
            for n in range(count, old_count+1):
                obj.unlink(obj[element.name+'_Dupli'+str(n)])
                bpy.data.objects.remove(bpy.data.objects[element.name+'_Dupli'+str(n)])    
            
        element['count']  = count
    return None

# Updat star element
def update_star_element(self, context):
    old_count = len(get_ghost_duplis())
    scn = bpy.context.scene
    obj = scn.objects
    coll, index = get_element_group()
    target = obj[get_active_cont()]
    coll1, index1 = get_flare_group()
    pivot = obj[coll1[index1]['pivot']]
    element = obj[coll[index].object]
    type = element['ele_type']
    count = coll[index].streaks_count
    if type == 'star':        
        if count > old_count+1:        
            for n in range(old_count+1,count):
                mesh = element.data
                dupli = bpy.data.objects.new(element.name+'_Dupli'+str(n), mesh)            
                dupli.parent = scn.camera
                dupli.location = element.location
                dupli.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
                dupli.hide_select = True
                scn.objects.link(dupli)
                dupli[get_active_flare()] = ''
                dupli['IS_BLF'] = ''
                dupli.draw_type = 'WIRE'
                set_ray_visibility(dupli)
                
                # drivers
                
                # Location
                # x axis driver
                driver = dupli.driver_add("location", 0)
                add_transform_var(driver, 'main', obj[coll[index].cont], 'LOC_X', 'LOCAL_SPACE')
                add_transform_var(driver, 'pivot', pivot, 'LOC_X', 'LOCAL_SPACE')
                add_prop_var(driver, 'pos', 'OBJECT', element, '["pos"]')                 
                add_prop_var(driver, 'x', 'OBJECT', element, '["x"]')                 
                driver.driver.expression = '((1-pos)*(main+x))+(pivot*pos)'        
                
                # y axis driver
                driver = dupli.driver_add("location", 1)
                add_transform_var(driver, 'main', obj[coll[index].cont], 'LOC_Y', 'LOCAL_SPACE')
                add_transform_var(driver, 'pivot', pivot, 'LOC_Y', 'LOCAL_SPACE')
                add_prop_var(driver, 'pos', 'OBJECT', element, '["pos"]')                 
                add_prop_var(driver, 'y', 'OBJECT', element, '["y"]')                 
                driver.driver.expression = '((1-pos)*(main+y))+(pivot*pos)'
                        
                # z axis driver
                driver = dupli.driver_add("location", 2)
                add_transform_var(driver, 'main', obj[coll[index].cont], 'LOC_Z', 'LOCAL_SPACE')
                add_prop_var(driver, 'Z', 'OBJECT', target, '["z_offset"]')
                add_prop_var(driver, 'space', 'OBJECT', target, '["in_3D_space"]')
                driver.driver.expression = 'main+' +str(n*0.0001) + ' if space == 0 else main+' +str(n*0.0001) + '*Z'
                
                # Rortation
                driver = dupli.driver_add("rotation_euler", 2)
                add_prop_var(driver, 'rotation', 'OBJECT', element, '["rotation"]') 
                add_prop_var(driver, 'angle', 'OBJECT', element, '["angle"]') 
                add_prop_var(driver, 'count', 'OBJECT', element, '["count"]') 
                driver.driver.expression = 'radians(rotation)+(radians(angle)/count)*'+ str(n)
                
                # Scale
                # x axis
                driver = dupli.driver_add("scale", 0)
                add_prop_var(driver, 'x', 'OBJECT', element, '["scale_x"]') 
                add_prop_var(driver, 'min', 'OBJECT', element, '["random_scale"]') 
                add_prop_var(driver, 'seed', 'OBJECT', element, '["scale_seed"]')                  
                add_prop_var(driver, 'scale', 'OBJECT', element, '["scale"]')
                add_prop_var(driver, 'global_scale', 'OBJECT', target, '["scale"]')
                driver.driver.expression = "x * scale*global_scale*randomize(1-min,seed+"+str(n)+")"
                
                # y axis
                driver = dupli.driver_add("scale", 1)
                add_prop_var(driver, 'y', 'OBJECT', element, '["scale_y"]')
                add_prop_var(driver, 'min', 'OBJECT', element, '["random_scale"]') 
                add_prop_var(driver, 'seed', 'OBJECT', element, '["scale_seed"]')          
                add_prop_var(driver, 'scale', 'OBJECT', element, '["scale"]')
                add_prop_var(driver, 'global_scale', 'OBJECT', target, '["scale"]')
                driver.driver.expression = "y * scale*global_scale*randomize(1-min,seed+"+str(n)+")"
                # driver for visibility
                driver = dupli.driver_add("hide")
                add_prop_var(driver, 'visibility', 'OBJECT', element, 'hide') 
                driver.driver.expression = 'visibility'
        elif count < old_count+1:
            for n in range(count, old_count+1):
                obj.unlink(obj[element.name+'_Dupli'+str(n)])
                bpy.data.objects.remove(bpy.data.objects[element.name+'_Dupli'+str(n)])    
            
        element['count']  = count
        element.animation_data.drivers[0].driver.expression = element.animation_data.drivers[0].driver.expression          
    
    return None

# Load lens flare from preview
def load_update_preview(self, context):
    scn = context.scene
    if scn.get('LF_previews') != None:        
        flare = scn.LF_previews
        sel, act = get_sel_ob()
        filename, file_extension = os.path.splitext(flare)
        if bpy.context.scene.objects.active == None :
            print("No active object in the scene.")
        elif bpy.context.scene.objects.active.type == 'CAMERA' :
            print("Can't add a lens flare to camera.")
        elif bpy.context.scene.camera == None :
            print("No camera in the scene.")
        elif not os.access(os.path.join(presetsFolder, filename + '.lf'),os.F_OK):
                print('File "' + filename + '.lf' +  '" not found')                                   
        else:
            load_lens_flare(os.path.join(presetsFolder, filename + '.lf'))
            restore_selection(sel, act)
    return None        

# Find malfunctions and try to fix them
def scan_and_repair():
    scn = bpy.context.scene
    obj = scn.objects
    coll, index = get_flare_group()   
    
    print('----------------Start scan----------------')
    # 1- is there any missing parts in the lens flares ?
    def get_ex_flares():
        flares = []
        for ob in obj:
            for f in ob.keys():
                if 'BLF_SYS' in f:
                    if f not in flares:
                        flares.append(f)
        return flares 
                   
    def get_flare_objs(flare):
        objs = []
        for ob in obj:
            if flare in ob.keys():
                objs.append(ob.name)
        return objs

    def find_broken_flares():
        broken_flares = []
        found  = False
        for flare in get_ex_flares():
            for name in ['Controller', 'Pivot', 'Helper', 'cam_vis_check']:
                for ob in get_flare_objs(flare):
                    if name in ob:
                        found = True
                if not found :
                    if flare not in broken_flares:
                        broken_flares.append(flare)
                found = False                
        return broken_flares
    
    def find_flare_index(flare):
        ind = -1
        for f in range(len(coll)):
            if coll[f]['flare'] == flare:
                ind = f
        return ind
        

    def delete_flare(flare):
        materials = []
        meshes = []
        for ob in obj:
            if flare in ob.keys():
                if ob.type == 'MESH':
                    mesh = ob.data
                    if len(ob.material_slots) > 0:
                        material = ob.material_slots[0].material
                    if mesh not in meshes:
                        meshes.append(mesh)
                    if material not in materials:
                        materials.append(material)                        
                bpy.context.scene.objects.unlink(ob)
                bpy.data.objects.remove(ob)
        if len(materials) > 0:
            for mat in materials:
                bpy.data.materials.remove(mat)
        if len(meshes) > 0:
            for me in meshes:
                bpy.data.meshes.remove(me)
        ind = find_flare_index(flare)        
        if ind != -1:
            coll.remove(ind)
            if len(bpy.context.scene.flare_group.coll)>0:
                bpy.context.scene.flare_group.index = 0
    
    def get_elements():
        elements = []
        for ob in obj:            
            if 'ele_type' in ob.keys():
                elements.append(ob)
        return elements        

    def get_elements_controllers():
        controllers = []
        for ob in obj:            
            if 'Element_controller' in ob.name:
                controllers.append(ob.name)
        return controllers                    
                
    def find_broken_flares():
        elements = get_elements()
        broken_flares = []
        found  = False
        for flare in get_ex_flares():
            for name in ['Controller', 'Pivot', 'Helper', 'cam_vis_check']:
                for ob in get_flare_objs(flare):
                    if name in ob:
                        found = True
                if not found :
                    if flare not in broken_flares:
                        broken_flares.append(flare)
                found = False                
        return broken_flares   
             
    # remove broken flares
    def remove_broken_flares():
        if len(find_broken_flares()) > 0:
            broken = find_broken_flares()
            print(str(len(broken)) + ' Broken flares found -> Missing parts')
            for f in broken:
                delete_flare(f)
                print('Broken flare "'+ f+ '" -> Deleted')
        else:
            print('No broken flares -> OK')
    
    # remove broken elements
    def remove_broken_elements():
        
        elements =  get_elements()
        conts = get_elements_controllers()
        broken_elements = []
        if len(conts)> len(elements):
            conts2 = []
            for e in elements:
                conts2.append(e['controller'])            
            for c in conts:
                if c not in conts2:
                    if obj.get(c) is not None:                    
                        bpy.context.scene.objects.unlink(obj[c])
                        bpy.data.objects.remove(bpy.data.objects[c])                    
                        print('"' + c+ '" not a part of any element -> Deleted' )
        elif len(conts) < len(elements):
            conts = get_elements_controllers()        
            for e in elements:
                if e['controller'] not in conts:
                    broken_elements.append(e)               
            if len(broken_elements) > 0:
                for ele in broken_elements:
                    name = ele.name
                    type = ele['ele_type']
                    material = None
                    mesh = None 
                    if type == 'ghost' or  type == 'star':
                        for ob in obj:
                            if name+'_Dupli' in ob.name:
                                bpy.context.scene.objects.unlink(ob)
                                bpy.data.objects.remove(ob)
                    if obj.get(ele.name) is not None:
                        if len(ele.material_slots) > 0:
                            material = ele.material_slots[0].material
                        mesh = ele.data           
                        bpy.context.scene.objects.unlink(ele)
                        bpy.data.objects.remove(ele)
                        print('Element "' + name + '" do not have a controller -> Deleted')                           
                    if material != None:
                        if material.users == 0:
                            bpy.data.materials.remove(material)
                    if mesh != None:
                        if mesh.users == 0:    
                            bpy.data.meshes.remove(mesh)                  
        else:print('No broken elements -> OK')
        
    remove_broken_flares()    
    remove_broken_elements()
    remove_broken_elements()    
    if len(bpy.context.scene.flare_group.coll)>0:
        bpy.context.scene.flare_group.index = 0
    
                                                        
                    
                    
                    
    
        
    
    
   

      
        
###### Classes ########

# Groups for the UI lists
# lens flare
class Flare(PropertyGroup):
    object = StringProperty()
    pivot = StringProperty()
    helper = StringProperty()
    cam_vis = StringProperty()
    flare = StringProperty()
    cam_vis = StringProperty()
    name = StringProperty(update = update_flare_name)
    color = FloatVectorProperty(size = 4,subtype='COLOR',default=[1.0,1.0,1.0,1.0], min = 0.0, max = 1.0, update = update_elements_color, description = "Global color")
    visibility = BoolProperty(default = False, update = update_intensity, description = "When the Flare is no longer visible by the camera will fade out")
    opstacles = BoolProperty(default = False, update = update_intensity, description = "Enable using the obstacle detection feature")
    blinking = BoolProperty(default = False, update = update_intensity, description = "Enable the blinking system")
    copy_to_lamp = BoolProperty(default = False, update = update_elements_color, description = "The lamp will get the color of the Lens flare")
        
   
class FlareGroup(PropertyGroup):
    coll = CollectionProperty(type=Flare)
    index = IntProperty(update = update_lists )
    
# elements    
class Elements(PropertyGroup):
    object = StringProperty()
    type = StringProperty()
    name = StringProperty(update = update_element_name)
    cont = StringProperty()
    ghosts_count = IntProperty(default = 5, min = 1, max = 99, description = 'Total number of ghosts', update = update_ghost_element)
    streaks_count = IntProperty(default = 5, min = 1, max = 199, description = 'Total number of streaks', update = update_star_element)
        
class ElementGroup(PropertyGroup):
    coll = CollectionProperty(type=Elements)
    index = IntProperty(default = 0)
# opstacles
class Opstacles(PropertyGroup):
    flare = StringProperty()
    name = StringProperty()
    
class OpstaclesGroup(PropertyGroup):
    coll = CollectionProperty(type=Opstacles)
    index = IntProperty(default = 0)    

###### Operators #######

# Create a new lens flare systeme    
class CreateLensFlare(Operator):
    bl_idname = "flare.create_lens_flare"
    bl_label = "Create lens flare"
    bl_description = "Create a new Lens Flare on active object."

    def execute(self, context):
        sel, act = get_sel_ob()
        if bpy.context.scene.objects.active == None :
            self.report({'WARNING'}, "No active object in the scene.")
        elif bpy.context.scene.objects.active.type == 'CAMERA' :
            self.report({'WARNING'}, "Can't add a lens flare to camera.")
        elif bpy.context.scene.camera == None :
            self.report({'WARNING'}, "No camera in the scene.")    
        else:
             Create_BLF_SYS()
             restore_selection(sel, act)
        return {'FINISHED'}

# Create new simple element   
class CreateSimpleElement(Operator):
    bl_idname = "flare.create_simple_element"
    bl_label = "Create simple element"
    bl_description = "Create a new simple element on active Lens Flare."
    def execute(self, context):
        sel, act = get_sel_ob()
        Create_Simple_Element()
        restore_selection(sel, act)
        return {'FINISHED'} 
# Create new ghost element   
class CreateGhostElement(Operator):
    bl_idname = "flare.create_ghost_element"
    bl_label = "Create ghost element"
    bl_description = "Create a new ghost element on active Lens Flare."
    def execute(self, context):
        sel, act = get_sel_ob()
        Create_Ghost_Element()
        restore_selection(sel, act)
        return {'FINISHED'}
# Create new lens_dirt element   
class CreateLensDirtElement(Operator):
    bl_idname = "flare.create_lens_dirt_element"
    bl_label = "Create lens_dirt element"
    bl_description = "Create a new lens dirt element on active Lens Flare."
    def execute(self, context):
        sel, act = get_sel_ob()
        Create_Lens_Dirt_Element()
        restore_selection(sel, act)
        return {'FINISHED'}
# Create new star element   
class CreateStarElement(Operator):
    bl_idname = "flare.create_star_element"
    bl_label = "Create star element"
    bl_description = "Create a new star element on active Lens Flare."
    def execute(self, context):
        sel, act = get_sel_ob()
        Create_Star_Element()
        restore_selection(sel, act)
        return {'FINISHED'}             
# Create new background element   
class CreateBackgroundElement(Operator):
    bl_idname = "flare.create_bg_element"
    bl_label = "Create Background element"
    bl_description = "Create a new background element on active Lens Flare."
    def execute(self, context):
        sel, act = get_sel_ob()
        Create_BG_Element()
        restore_selection(sel, act)
        return {'FINISHED'}    
    
# Add opstacle to the list   
class AddOpstacle(Operator):
    bl_idname = "flare.add_opstacle"
    bl_label = "Add Opstacles"
    bl_description = "Add opstacle."
    def execute(self, context):
        add_opstacle()
        return {'FINISHED'} 
        
# Delete lens flare
class DeleteLensFlare(Operator):
    bl_idname = "flare.delete_lens_flare"
    bl_label = "Delete Lens Flare"
    bl_description = "Delete this Lens Flare."
        
    def execute(self, context):
        deleteFlare()
        update_elements()
        return {"FINISHED"}    
    
# Delete lens flare element
class DeleteFlareElement(Operator):
    bl_idname = "flare.delete_flare_element"
    bl_label = "Delete Flare Element"
    bl_description = "Delete this element."
        
    def execute(self, context):
        deleteElement()
        return {"FINISHED"}

# Delete opstacle
class DeleteOpstacle(Operator):
    bl_idname = "flare.delete_opstacle"
    bl_label = "Delete opstacle"
    bl_description = "Remove selected."
        
    def execute(self, context):
        deleteOpstacle()
        return {"FINISHED"}
    
# Duplicate element
class DuplicateElement(Operator):
    bl_idname = "flare.duplicate_element"
    bl_label = "Duplicate"
    bl_description = "Duplicate selected."
        
    def execute(self, context):
        coll, index = get_element_group()
        if len(coll) == 0:
            self.report({'WARNING'}, "Nothing to duplicate.")                
        else:
            sel, act = get_sel_ob()
            element = get_active_element()        
            duplicate_element(element = element)
            restore_selection(sel, act)
        return {"FINISHED"} 
    
# Duplicate Lens Flare
class DuplicateFlare(Operator):
    bl_idname = "flare.duplicate_lens_flare"
    bl_label = "Duplicate"
    bl_description = "Duplicate selected Lens Flare."
        
    def execute(self, context):
        coll, index = get_flare_group()
        if bpy.context.scene.objects.active == None :
            self.report({'WARNING'}, "No active object in the scene.")
        elif bpy.context.scene.objects.active.type == 'CAMERA' :
            self.report({'WARNING'}, "Can't add a lens flare to camera.")
        elif len(coll) == 0:
            self.report({'WARNING'}, "Nothing to duplicate.")                
        else:
            sel, act = get_sel_ob()
            duplicate_lens_flare()
            restore_selection(sel, act)
        return {"FINISHED"}

# save lens flare
class SaveFlare(Operator):
    bl_idname = "flare.save"
    bl_label = "Save"
    bl_description = "Save selected lens flare."
    filepath = StringProperty(subtype="FILE_PATH")    
        
    def execute(self, context):        
        coll, index = get_flare_group()     
        if len(coll) > 0:
            if not self.filepath.endswith('.lf'):
                self.filepath = self.filepath + '.lf'            
            save_lens_flare(self.filepath)          
        return {'FINISHED'}
    
    def invoke(self, context, event):
        coll, index = get_flare_group()
        if len(coll) > 0:            
            flare = coll[index].name
            self.filepath = presetsFolder + os.sep + flare + '.lf'
            context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}  
    
    
# load lens flare
class LoadFlare(Operator):
    bl_idname = "flare.load"
    bl_label = "Load"
    bl_description = "Load lens flare."
    filepath = StringProperty(subtype="FILE_PATH")
    
    def execute(self, context):
        sel, act = get_sel_ob()
        filename, file_extension = os.path.splitext(self.filepath)
        file = os.path.basename(filename)
        if bpy.context.scene.objects.active == None :
            self.report({'WARNING'}, "No active object in the scene.")
        elif bpy.context.scene.objects.active.type == 'CAMERA' :
            self.report({'WARNING'}, "Can't add a lens flare to camera.")
        elif bpy.context.scene.camera == None :
            self.report({'WARNING'}, "No camera in the scene.")
        elif file_extension != '.lf':
            if not os.access(os.path.join(presetsFolder, file + '.lf'),os.F_OK):
                print(filename)
                self.report({'WARNING'}, 'File "' + file + '.lf' +  '" not found')
                
            else:
                load_lens_flare(os.path.join(presetsFolder, file + '.lf'))
                restore_selection(sel, act)                                    
        else:
            load_lens_flare(self.filepath)
            restore_selection(sel, act)          
        return {'FINISHED'}
    
    def invoke(self, context, event):
        self.filepath = presetsFolder + os.sep
        context.window_manager.fileselect_add(self)        
        return {'RUNNING_MODAL'}       
                        
     
# Select Image    
class SelectImage(Operator):
    bl_idname = "flare.select_image"
    bl_label = "Select an image"
    bl_description = "Select an image."
    
    def avail_images(self,context):
        items = [(str(i),x.name,x.name) for i,x in enumerate(bpy.data.images)]
        return items
    
    select_images = EnumProperty(items = avail_images, name = "Available Images")
       
    def execute(self,context):                 
        element =context.scene.objects[get_active_element()]
        material = get_active_material()
        image_texture = material['Image Texture']
        image_texture.image = bpy.data.images[int(self.select_images)]
        if element['ele_type'] == 'ghost':
            image_texture2 = material['Image Texture.001']
            image_texture2.image = bpy.data.images[int(self.select_images)]            
        return {'FINISHED'}           

# Open Image    
class OpenImage(Operator):
    bl_idname = "flare.open_image"
    bl_label = "Open an image"
    bl_description = "Open an image."     
    filepath = StringProperty(subtype="FILE_PATH")
        
    def execute(self, context):
        element = context.scene.objects[get_active_element()]
        material = get_active_material()
        image_texture = material['Image Texture']        
        filename, file_extension = os.path.splitext(self.filepath)
        extensions = ['.png', '.jpg', '.jpeg', '.bmp','.targa', '.avi', '.mp4', '.ogg', '.flv', '.mov', '.mpeg', '.wmv']
        if file_extension.lower() not in extensions:
            self.report({'WARNING'}, os.path.basename(self.filepath) + ' : ' + 'Is not an image or movie file.')
        elif os.path.basename(self.filepath) in bpy.data.images.keys():
                image_texture.image = bpy.data.images[os.path.basename(self.filepath)]                                    
        else:
            bpy.ops.image.open(filepath = self.filepath)
            image_texture.image = bpy.data.images[os.path.basename(self.filepath)]        
            if element['ele_type'] == 'ghost':
                image_texture2 = material['Image Texture.001']
                image_texture2.image = bpy.data.images[os.path.basename(self.filepath)]        
            
        return {'FINISHED'}
    
    def invoke(self, context, event):
        self.filepath = elementsFolder + os.sep
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
# Open elements folder    
class OpenElementsFolder(Operator):
    bl_idname = "flare.open_elements_folder"
    bl_label = "Open elements folder"
    bl_description = "Open the folder containing the elements."
    
    def execute(self, context):
        webbrowser.open(elementsFolder)
        return {'FINISHED'}
    
# Open presets folder    
class OpenPresetsFolder(Operator):
    bl_idname = "flare.open_presets_folder"
    bl_label = "Open presets folder"
    bl_description = "Open the folder containing the presets."
    
    def execute(self, context):
        webbrowser.open(presetsFolder)
        return {'FINISHED'}
    
# Open the Manual   
class OpenManual(Operator):
    bl_idname = "flare.open_manual"
    bl_label = "Open the manual"
    bl_description = "Open the Manual."
    
    def execute(self, context):
        webbrowser.open(os.path.join(addonFolder, 'Manual.pdf'))
        return {'FINISHED'}        
    
# move flare to selected layer
class MoveToLayer(Operator):
    bl_idname = "flare.move_to_layer"
    bl_label = "Move to layer"
    bl_description = "Move the active lens flare to the selected layer."
    
    def execute(self, context):
        scn = bpy.context.scene
        obj = scn.objects
        coll, index = get_flare_group()
        flare = coll[index].flare
        cont = coll[index].object
        
        for ob in obj:
            if flare in ob.keys():
                ob.layers = obj[cont].layers    
        
        return {'FINISHED'}
    
# Scan and fix            
class ScanAndFix(Operator):
    bl_idname = "flare.fix"
    bl_label = "Fix"
    bl_description = "Find Broken parts and delete them."
    
    def execute(self, context):
        scan_and_repair()
        return {'FINISHED'}
    
# Show all elements
class ShowAllElements(Operator):
    bl_idname = "flare.show_all_elements"
    bl_label = "Show all"
    bl_description = "Show all elements."
    
    def execute(self, context):
        show_all_elements()
        return {'FINISHED'} 
    
# Hide all elements
class HideAllElements(Operator):
    bl_idname = "flare.hide_all_elements"
    bl_label = "Hide all"
    bl_description = "Hide all elements."
    
    def execute(self, context):
        hide_all_elements()
        return {'FINISHED'}
    
# Solo selected element
class SoloSelectedElement(Operator):
    bl_idname = "flare.solo_element"
    bl_label = "Solo"
    bl_description = "Solo selected element."
    
    def execute(self, context):
        solo_selected_element()
        return {'FINISHED'} 
    
# Remove unused images
class RemoveUnusedImages(Operator):
    bl_idname = "flare.remove_unused_images"
    bl_label = "Remove unused images"
    bl_description = "Remove 0 user images."
    
    def execute(self, context):
        images = bpy.data.images
        for image in images:
            if image.users == 0:
                images.remove(image)
        return {'FINISHED'}
    
# Remove unused meshes
class RemoveUnusedMeshes(Operator):
    bl_idname = "flare.remove_unused_meshes"
    bl_label = "Remove unused meshes"
    bl_description = "Remove 0 user meshes."
    
    def execute(self, context):
        meshes = bpy.data.meshes
        for mesh in meshes:
            if mesh.users == 0:
                meshes.remove(mesh)
        return {'FINISHED'}
    
# Remove unused materials
class RemoveUnusedMaterials(Operator):
    bl_idname = "flare.remove_unused_materials"
    bl_label = "Remove unused materials"
    bl_description = "Remove 0 user materials."
    
    def execute(self, context):
        materials = bpy.data.materials
        for material in materials:
            if material.users == 0:
                materials.remove(material)
        return {'FINISHED'}                                   
    
            
    
    
    
######## the UI ##########

# UI list draw (Flares)
class SCENE_UL_flare(UIList):
   
   def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
       row = layout.row()
       row.prop(item, "name", text="", emboss=False, icon = "MOD_PARTICLES")
            
# UI list draw (Elements)
class SCENE_UL_element(UIList):
   
   def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
       obj = bpy.data.objects       
       row = layout.row()
       row.prop(item, "name", text="", emboss=False)
       row = layout.row()
       row.alignment = 'RIGHT'
       row.prop(obj[item.object], "hide", text="", emboss=False)
       
# UI list draw (Opstacles)       
class SCENE_UL_opstacles(UIList):
   
   def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
       row = layout.row()
       row.enabled = False       
       row.prop(item, "name", text="", emboss=False)
       
# Special menu add flare
class AddFlare(Menu):
    bl_idname = "flare.add_flare_menu"
    bl_label = "Specials"
    bl_description = "Add lens flare."

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        layout.label("Add Lens Flare", icon = "NEW")        
        layout.separator()
        layout.operator("flare.create_lens_flare", text='New', icon = "PLUS")
        layout.operator("flare.load", text='Load', icon = "LOAD_FACTORY")
        layout.template_icon_view(scn, "LF_previews", show_labels=True)
          
       
# Special menu add element
class AddElement(Menu):
    bl_idname = "flare.add_element_menu"
    bl_label = "Specials"
    bl_description = "Add element."

    def draw(self, context):
        layout = self.layout
        layout.label("Add element", icon = "NEW")        
        layout.separator()
        layout.operator("flare.create_simple_element", text='Simple', icon = "SOLID")
        layout.operator("flare.create_ghost_element", text='Ghosts', icon = "GHOST_ENABLED")
        layout.operator("flare.create_star_element", text='Star', icon = "SOLO_OFF")
        layout.operator("flare.create_lens_dirt_element", text='Lens dirt', icon = "FREEZE")
        layout.operator("flare.create_bg_element", text='Background', icon = "MATPLANE")
        
# Special menu element settings
class ElementSettings(Menu):
    bl_idname = "flare.element_settings_menu"
    bl_label = "Specials"
    bl_description = "Element extra settings."

    def draw(self, context):
        layout = self.layout        
        layout.operator("flare.duplicate_element", icon = "ROTATECOLLECTION")
        layout.separator()
        layout.operator("flare.show_all_elements", icon = "VISIBLE_IPO_ON")
        layout.operator("flare.hide_all_elements", icon = "VISIBLE_IPO_OFF")
        layout.operator("flare.solo_element", icon = "VISIBLE_IPO_ON")
        
# Special menu lens flare settings
class FlaretSettings(Menu):
    bl_idname = "flare.flare_settings_menu"
    bl_label = "Specials"
    bl_description = "Flare extra settings."

    def draw(self, context):
        layout = self.layout        
        layout.operator("flare.duplicate_lens_flare", icon = "ROTATECOLLECTION")        
        layout.operator("flare.save", icon = "SAVE_COPY")

# Special menu files shortcuts
class FlareShortcuts(Menu):
    bl_idname = "flare.files_shortcuts"
    bl_label = "Specials"
    bl_description = "Shortcuts."        
   
    def draw(self, context):
        layout = self.layout                
        layout.operator("flare.open_elements_folder", icon = 'IMASEL')
        layout.operator("flare.open_presets_folder", icon = 'FILESEL')
        layout.operator("flare.open_manual" ,icon = 'QUESTION')
                
# Special menu cleanup
class FlareCleanup(Menu):
    bl_idname = "flare.cleanup"
    bl_label = "Specials"
    bl_description = "Cleanup."        
   
    def draw(self, context):
        layout = self.layout
        layout.operator("flare.fix", text = 'Fix (Experimental)', icon = 'ERROR' )
        layout.separator()        
        layout.operator("flare.remove_unused_images", icon = 'IMAGE_DATA' )        
        layout.operator("flare.remove_unused_meshes", icon = 'OUTLINER_DATA_MESH' )        
        layout.operator("flare.remove_unused_materials", icon = 'MATERIAL_DATA' )  
        
# Extras Panel
class ExtrasPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Lens Flares"
    bl_label = "Extra options"
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}
    def draw(self, context):
        scn = context.scene
        layout = self.layout
        box = layout.box()
        row = box.row()        
        row.menu("flare.files_shortcuts" , text = 'Shortcuts', icon = "FILE_FOLDER")
        row.menu("flare.cleanup" , text = 'Cleanup', icon = "PREFERENCES")
                
       
# Lens Flares Panel
class LensFlaresPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Lens Flares"
    bl_label = "Lens Flares"
    bl_context = "objectmode"
    
        
    def draw(self, context):
        layout = self.layout        
        scn = context.scene        
        coll, index = get_flare_group()
        if len(coll)>0:
            target = scn.objects[coll[index]['object']]
            pivot = scn.objects[coll[index]['pivot']]
            cam_vis = scn.objects[coll[index]['cam_vis']]
        
        row = layout.row()
        row.template_list("SCENE_UL_flare", "coll", scn.flare_group, "coll", scn.flare_group, "index", rows = 2)
        col = row.column(align=True)
        col.menu("flare.add_flare_menu", icon='ZOOMIN', text="")
        col.operator("flare.delete_lens_flare", icon='ZOOMOUT', text="")
        col.menu("flare.flare_settings_menu", icon="DOWNARROW_HLT", text="")
        
        if len(coll)>0:                
            column_flow = layout.column_flow()           
            row = column_flow.row()
            row.prop(scn, "flare_setings",
            icon="DOWNARROW_HLT" if scn.flare_setings else "RIGHTARROW",
            icon_only=True, emboss=False)
            row.label(text='General settings')
            if scn.flare_setings:
                col = column_flow.column()                
                col.prop(target, '["intensity"]', text = "Intensity")         
                col.prop(target, '["scale"]', text = "Scale")         
                col.prop(target, '["in_3D_space"]', text = "In 3D space")
                if target["in_3D_space"] >0:
                    col.prop(target, '["z_offset"]', text = "Z offset")                    
                row = column_flow.row()
                row.prop(target.constraints[0], "target", text="Target", emboss=True)
                row = column_flow.row(align = True)
                row.prop(coll[index], "color", text = "Global Color")
                if target.constraints[0].target !=None:
                    if target.constraints[0].target.type == 'LAMP':
                        row.prop(coll[index], "copy_to_lamp", text = '', icon = 'OUTLINER_OB_LAMP')
                              
            column_flow = layout.column_flow()
            row = column_flow.row()
            row.prop(scn, "pivot_setings",
            icon="DOWNARROW_HLT" if scn.pivot_setings else "RIGHTARROW",
            icon_only=True, emboss=False)
            row.label(text='Pivot point')
            if scn.pivot_setings:    
                col = column_flow.column()
                col.prop(pivot.constraints[0], "target", text = "Target")
                row = col.row(align = True)
                row.enabled = pivot.constraints[0].target == None
                row.prop(pivot, '["x"]', text = "X position")
                row.prop(pivot, '["y"]', text = "Y position")
                
            column_flow = layout.column_flow()
            row = column_flow.row()
            row.prop(scn, "LF_layers",
            icon="DOWNARROW_HLT" if scn.LF_layers else "RIGHTARROW",
            icon_only=True, emboss=False)
            row.label(text='Layers')
            if scn.LF_layers:    
                row = column_flow.row()
                row.alignment = 'LEFT'
                row.label(' Select a layer     ')
                row.template_layers(target, "layers", pivot, "layers", target['layer'])
                row = column_flow.row()
                row.alignment = 'LEFT'
                row.label(' Move to selected')
                row.operator("flare.move_to_layer", icon = 'SCREEN_BACK')
            
            column_flow = layout.column_flow()
            row = column_flow.row()
            row.prop(scn, "use_visibility",
            icon="DOWNARROW_HLT" if scn.use_visibility else "RIGHTARROW",
            icon_only=True, emboss=False)
            row.prop(coll[index], "visibility", text = "Visibility to camera")
            if scn.use_visibility:    
                col = column_flow.column()
                col.prop(cam_vis, '["distance"]', text = 'Distance')
                
            column_flow = layout.column_flow()
            row = column_flow.row()
            row.prop(scn, "use_opstacles",
            icon="DOWNARROW_HLT" if scn.use_opstacles else "RIGHTARROW",
            icon_only=True, emboss=False)
            row.prop(coll[index], "opstacles", text = "Use obstacles")
            if scn.use_opstacles:
                row = column_flow.row()
                row.template_list("SCENE_UL_opstacles", "coll", scn.opstacles_group, "coll", scn.opstacles_group, "index", rows = 2)
                col = row.column(align=True)
                col.operator("flare.add_opstacle", icon='ZOOMIN', text="")
                col.operator("flare.delete_opstacle", icon='ZOOMOUT', text="")
                col = column_flow.column()                
                col.prop(target, '["ops_distance"]', text = "Distance")                
                col.prop(target, '["ops_samples"]', text = "Steps")
                 
            column_flow = layout.column_flow()
            row = column_flow.row()
            row.prop(scn, "use_blinking",
            icon="DOWNARROW_HLT" if scn.use_blinking else "RIGHTARROW",
            icon_only=True, emboss=False)
            row.prop(coll[index], "blinking", text = "Blinking")
            if scn.use_blinking:
                col = column_flow.column()
                col.prop(target, '["blk_delay"]', text = "Delay")          
                col.prop(target, '["blk_min"]', text = "Min")
                col = column_flow.column(align = True)
                col.prop(target, '["blk_randomize"]', text = "Randomize")
                col.prop(target, '["blk_seed"]', text = "Seed")      
              

            
# Lens Flare Elements            
class LensFlaresElements(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Lens Flares"
    bl_label = "Lens Flare Elements"
    bl_context = "objectmode"
    @classmethod
    def poll(self, context):
        return len(context.scene.flare_group.coll)>0
    
    def draw(self, context):        
        scn = context.scene        
        layout = self.layout           
        row = layout.row()
        row.template_list("SCENE_UL_element", "coll", scn.element_group, "coll", scn.element_group, "index", rows = 2)
        col = row.column(align=True)
        col.menu("flare.add_element_menu", icon="ZOOMIN", text="")
        col.operator("flare.delete_flare_element", icon='ZOOMOUT', text="")
        col.menu("flare.element_settings_menu", icon="DOWNARROW_HLT", text="")        
        
        if get_active_element() !="":
            coll, index = get_element_group()
            element = scn.objects[get_active_element()]
            cont = scn.objects[get_active_cont()]
            material = get_active_material()            
            
            if element['ele_type']== 'simple':
                column_flow = layout.column_flow()
                row = column_flow.row()
                row.prop(scn, "material",
                icon="DOWNARROW_HLT" if scn.material else "RIGHTARROW",
                icon_only=True, emboss=False)
                row.label(text='Material & texture')
                if scn.material:
                    row  = column_flow.row()                    
                    row.prop(material['Mix.001'].inputs[0], "default_value", text = "Use Global Color")
                    row  = column_flow.row(align = True)
                    row.prop(material['Mix'].inputs[2], "default_value", text = "")
                    row.prop(material['Mix'].inputs[0], "default_value", text = "Fac")
                    row = column_flow.row()
                    row.prop(element, '["intensity"]', text = "Intensity")
                    row  = column_flow.row(align = True)
                    row.operator_menu_enum("flare.select_image", "select_images", text = "", icon = "IMAGE_COL")
                    row.prop(material['Image Texture'].image, "name", text = "")
                    row.operator("flare.open_image", text = "", icon = "FILESEL")
                    row = column_flow.row()
                column_flow = layout.column_flow()
                row = column_flow.row()
                row.prop(scn, "transforms",
                icon="DOWNARROW_HLT" if scn.transforms else "RIGHTARROW",
                icon_only=True, emboss=False)
                row.label(text='Transforms')
                if scn.transforms:    
                    col = column_flow.column(align = True)
                    col.prop(element, '["pos"]', text = "Position")
                    row = col.row(align = True)
                    row.prop(element, '["x"]', text = "X")
                    row.prop(element, '["y"]', text = "Y")
                    col.prop(element, '["lock_y"]', text = "Lock Y")
                    col = column_flow.column(align = True)
                    col.prop(element, '["rotation"]', text = "Rotation")
                    col.prop(element.constraints[0], "influence", text = "Track the target", slider = True)
                    col = column_flow.column(align = True)
                    col.prop(element, '["scale"]', text = "Scale")
                    row = col.row(align = True)
                    row.prop(element, '["scale_x"]', text = "X")
                    row.prop(element, '["scale_y"]', text = "Y")    
                
            elif element['ele_type']== 'ghost':
                column_flow = layout.column_flow()
                row = column_flow.row()
                row.prop(scn, "material",
                icon="DOWNARROW_HLT" if scn.material else "RIGHTARROW",
                icon_only=True, emboss=False)
                row.label(text='Material & texture')
                if scn.material:                    
                    row  = column_flow.row()               
                    row.prop(material['Mix.001'].inputs[0], "default_value", text = "Use Global Color")
                    col = column_flow.column(align = True)
                    row  = col.row(align = True)
                    row.prop(material['Mix.004'].inputs[1], "default_value", text = "")
                    row.prop(material['Mix.004'].inputs[2], "default_value", text = "")
                    col.prop(material['Mix'].inputs[0], "default_value", text = "Fac")                    
                    box = layout.box()
                    col = box.column()                    
                    col.template_color_ramp(material['ColorRamp'], "color_ramp", expand=False)
                    row = column_flow.row()
                    row.prop(element, '["intensity"]', text = "Intensity")
                    row  = column_flow.row(align = True)
                    row.operator_menu_enum("flare.select_image", "select_images", text = "", icon = "IMAGE_COL")
                    row.prop(material['Image Texture'].image, "name", text = "")
                    row.operator("flare.open_image", text = "", icon = "FILESEL")
                    col = column_flow.column(align = True)
                    col.prop(material['Mix.003'].inputs[0], "default_value", text = "Outline opacity")
                    col.prop(element, '["outline"]', text = "Outline thickness")
                    row  = column_flow.row()
                column_flow = layout.column_flow()
                row = column_flow.row()
                row.prop(scn, "transforms",
                icon="DOWNARROW_HLT" if scn.transforms else "RIGHTARROW",
                icon_only=True, emboss=False)
                row.label(text='Transforms')
                if scn.transforms:                                  
                    col = column_flow.column(align = True)
                    col.prop(element, '["pos"]', text = "Position")
                    row = col.row(align = True)
                    row.prop(element, '["x"]', text = "X")
                    row.prop(element, '["y"]', text = "Y")
                    col.prop(element, '["lock_y"]', text = "Lock Y")
                    col = column_flow.column(align = True)
                    col.prop(element, '["rotation"]', text = "Rotation")
                    col = column_flow.column(align = True)
                    col.prop(element, '["scale"]', text = "Scale")
                    row = col.row(align = True)
                    row.prop(element, '["scale_x"]', text = "X")
                    row.prop(element, '["scale_y"]', text = "Y")
                    col = column_flow.column(align = True)
                    col.prop(element, '["random_scale"]', text = 'Random scale')
                    col.prop(element, '["scale_seed"]', text = 'Seed')
                    row  = column_flow.row()
                column_flow = layout.column_flow()
                row = column_flow.row()
                row.prop(scn, "specials",
                icon="DOWNARROW_HLT" if scn.specials else "RIGHTARROW",
                icon_only=True, emboss=False)
                row.label(text='Special settings')
                if scn.specials:                    
                    row = column_flow.row()
                    row.prop(coll[index], "ghosts_count", text = 'Number')
                    row = column_flow.row()
                    row.prop(element, '["distance"]', text = 'Distance')    
            elif element['ele_type']== 'lens_dirt':
                column_flow = layout.column_flow()
                row = column_flow.row()
                row.prop(scn, "material",
                icon="DOWNARROW_HLT" if scn.material else "RIGHTARROW",
                icon_only=True, emboss=False)
                row.label(text='Element settings')
                if scn.material:
                    row  = column_flow.row()               
                    row.prop(material['Mix.001'].inputs[0], "default_value", text = "Use Global Color")    
                    row  = column_flow.row(align = True)
                    row.prop(material['Mix'].inputs[2], "default_value", text = "")
                    row.prop(material['Mix'].inputs[0], "default_value", text = "Fac")
                    row = column_flow.row()
                    row.prop(element, '["intensity"]', text = "Intensity")
                    row  = column_flow.row(align = True)
                    row.operator_menu_enum("flare.select_image", "select_images", text = "", icon = "IMAGE_COL")
                    row.prop(material['Image Texture'].image, "name", text = "")
                    row.operator("flare.open_image", text = "", icon = "FILESEL")
                    col = column_flow.column(align = True)
                    col.prop(element, '["scale"]', text = "Dirt size")
                    col.prop(material['ColorRamp'].color_ramp.elements[1], "position", text = "Smoothness")    
            elif element['ele_type']== 'star':
                column_flow = layout.column_flow()
                row = column_flow.row()
                row.prop(scn, "material",
                icon="DOWNARROW_HLT" if scn.material else "RIGHTARROW",
                icon_only=True, emboss=False)
                row.label(text='Material & texture')
                if scn.material:                    
                    row  = column_flow.row()                              
                    row.prop(material['Mix.001'].inputs[0], "default_value", text = "Use Global Color")
                    row  = column_flow.row(align = True)
                    row.prop(material['Mix'].inputs[2], "default_value", text = "")
                    row.prop(material['Mix'].inputs[0], "default_value", text = "Fac")
                    row = column_flow.row()
                    row.prop(element, '["intensity"]', text = "Intensity")
                    row  = column_flow.row(align = True)
                    row.operator_menu_enum("flare.select_image", "select_images", text = "", icon = "IMAGE_COL")
                    row.prop(material['Image Texture'].image, "name", text = "")
                    row.operator("flare.open_image", text = "", icon = "FILESEL")
                    col = column_flow.column(align = True)
                    col.prop(material['Mix.002'].inputs[0], "default_value", text = "Color variation")
                    col.prop(material['Hue Saturation Value'].inputs[0], "default_value", text = "Hue")
                    col.prop(element, '["color_scale"]', text = "Scale")
                    col.prop(element, '["color_position"]', text = "Position")                    
                    row = column_flow.row()
                column_flow = layout.column_flow()
                row = column_flow.row()
                row.prop(scn, "transforms",
                icon="DOWNARROW_HLT" if scn.transforms else "RIGHTARROW",
                icon_only=True, emboss=False)
                row.label(text='Transforms')
                if scn.transforms:                    
                    col = column_flow.column(align = True)
                    col.prop(element, '["pos"]', text = "Position")
                    row = col.row(align = True)
                    row.prop(element, '["x"]', text = "X")
                    row.prop(element, '["y"]', text = "Y")
                    col.prop(element, '["streaks_offset"]', text = "Streaks offset")
                    col = column_flow.column(align = True)
                    col.prop(element, '["rotation"]', text = "Rotation")                    
                    col = column_flow.column(align = True)
                    col.prop(element, '["scale"]', text = "Scale")
                    row = col.row(align = True)
                    row.prop(element, '["scale_x"]', text = "X")
                    row.prop(element, '["scale_y"]', text = "Y")
                    col = column_flow.column(align = True)
                    col.prop(element, '["random_scale"]', text = 'Random scale')
                    col.prop(element, '["scale_seed"]', text = 'Seed')
                column_flow = layout.column_flow()
                row = column_flow.row()
                row.prop(scn, "specials",
                icon="DOWNARROW_HLT" if scn.specials else "RIGHTARROW",
                icon_only=True, emboss=False)
                row.label(text='Special settings')
                if scn.specials:                  
                    row = column_flow.row()
                    row.prop(coll[index], "streaks_count", text = 'Number')
                    row = column_flow.row()
                    row.prop(element, '["angle"]', text = 'Angle')
            elif element['ele_type']== 'background':
                column_flow = layout.column_flow()
                row = column_flow.row()
                row.prop(scn, "material",
                icon="DOWNARROW_HLT" if scn.material else "RIGHTARROW",
                icon_only=True, emboss=False)
                row.label(text='Element settings')
                if scn.material:
                    row  = column_flow.row()               
                    row.prop(element, '["intensity"]', text = "Opacity")
                    row  = column_flow.row(align = True)
                    row.operator_menu_enum("flare.select_image", "select_images", text = "", icon = "IMAGE_COL")
                    row.prop(material['Image Texture'].image, "name", text = "")
                    row.operator("flare.open_image", text = "", icon = "FILESEL")
                    row  = column_flow.row()                             
                    row.prop(scn.objects[element['controller']], '["z_offset"]', text = "Offset")
                    col  = column_flow.column(align = True)
                    image = material['Image Texture']
                    col.enabled = (image.image.source == 'MOVIE') or (image.image.source == 'SEQUENCE')
                    col.prop(image.image_user, 'frame_duration', text = "Frames")
                    col.prop(image.image_user, 'frame_start', text = "Start frame")
                    col.prop(image.image_user, 'frame_offset', text = "Offset frames")     
                     
######## register  #########    


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.flare_group = PointerProperty(type=FlareGroup)
    bpy.types.Scene.element_group = PointerProperty(type=ElementGroup)
    bpy.types.Scene.opstacles_group = PointerProperty(type=OpstaclesGroup)
    bpy.types.Scene.flare_setings = BoolProperty(default=False)
    bpy.types.Scene.pivot_setings = BoolProperty(default=False)
    bpy.types.Scene.material = BoolProperty(default=False)
    bpy.types.Scene.transforms = BoolProperty(default=False)
    bpy.types.Scene.specials = BoolProperty(default=False)
    bpy.types.Scene.use_visibility = BoolProperty(default=False)
    bpy.types.Scene.use_opstacles = BoolProperty(default=False)
    bpy.types.Scene.use_blinking = BoolProperty(default=False)
    bpy.types.Scene.LF_layers = BoolProperty(default=False)
    
    pcoll = previews.new()     
    preview_collections["LF_previews"] = pcoll
    bpy.types.Scene.LF_previews = EnumProperty(items=flare_previews(), update=load_update_preview)

       

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.flare_group
    del bpy.types.Scene.element_group
    del bpy.types.Scene.opstacles_group
    del bpy.types.Scene.flare_setings
    del bpy.types.Scene.pivot_setings
    del bpy.types.Scene.material
    del bpy.types.Scene.transforms
    del bpy.types.Scene.specials
    del bpy.types.Scene.use_visibility
    del bpy.types.Scene.use_opstacles
    del bpy.types.Scene.use_blinking
    del bpy.types.Scene.LF_layers
    
    for pcoll in preview_collections.values():
        previews.remove(pcoll)
    preview_collections.clear()

    del bpy.types.Scene.LF_previews
    
    


if __name__ == "__main__":
    register()

   
