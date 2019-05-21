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
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ##### END GPL LICENSE BLOCK #####


#//////////////////////////////// - AUTHORS YO - ///////////////////////////
#Original Author - Eclectiel
#Previous Updators - patmo141, chichiri
#Blender 2.7x Maintainer - Crocadillian

#This states the metadata for the plugin
bl_info = {
    "name": "Surf",
    "author": "Crocadillian, Eclectiel, patmo141, chichiri",
    "version": (0,75),
    "blender": (2, 7, 0),
    "api": 39347,
    "location": "3D View > Object Mode > Tools > Grease Pencil",
    #"description": "Easily sketch meshes with grease pencil and metaballs",
    #In case i add a few quick tools for quickly applying mesh data to splines, I wanted to expand the description :3
    "description": "Sketch and generate meshes with the grease pencil",
    "warning": "Beta",
    "wiki_url": "",
    "category": "Learnbgame"
}



#This imports various items from the Python API for use in the script
import bpy, bmesh, time
from math import *
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty

#Just variable definitions
mball_definition = 2
mball_wire_resolution = 0.1
degree_per_radian = 0.0174532925

def Update_StrokeSize(self, context):
    
    if bpy.context.scene.ASKETCH_live_update is not False:
    
        # Create an array to store all found objects
        strokes_to_select = []
        strokes_to_make_active = []
        
        if bpy.context.active_object.name.find(".SKO") != -1:
            strokes_to_make_active.append(bpy.context.active_object)
        
        # Find all the Stroke Objects in the scene
        for stroke in bpy.context.selected_objects:
            if stroke.name.find(".SKO") != -1:
                
                strokes_to_select.append(stroke)
            
                # Find the Curve
                stroke_size = float(self.ASKETCH_stroke_size)
                central_size = float(self.ASKETCH_stroke_central_size)
                
                stroke_curve_name = stroke.name.replace(".SKO", ".SKC")
                FocusObject(stroke_curve_name)
                curve_data = bpy.context.object.data  
                
                # Call the Set Curve Radius class
                bpy.ops.object.editmode_toggle()
                ASKETCH_SetStrokeRadius(curve_data, stroke_size, central_size)
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.select_all(action='DESELECT') 
                  
        # Re-select all stored objects         
        for strokeEnd in strokes_to_select:
            bpy.ops.object.select_pattern(pattern=strokeEnd.name)
             
        for strokeActive in strokes_to_make_active:
            bpy.ops.object.select_pattern(pattern=strokeActive.name)
            bpy.context.scene.objects.active = strokeActive
                
    return None


def Update_StrokeDensity(self, context):
    
    if bpy.context.scene.ASKETCH_live_update is not False:
    
        # Create an array to store all found objects
        strokes_to_select = []
        strokes_to_make_active = []
        
        if bpy.context.active_object.name.find(".SKO") != -1:
            strokes_to_make_active.append(bpy.context.active_object)
            
        # Find all the Stroke Objects in the scene
        for stroke in bpy.context.selected_objects:
            if stroke.name.find(".SKO") != -1:
                
                strokes_to_select.append(stroke)
            
                # Find the Curve
                stroke.modifiers["Array"].relative_offset_displace = [self.ASKETCH_stroke_element_offset, 0, 0]
                  
        # Re-select all stored objects         
        for strokeEnd in strokes_to_select:
            bpy.ops.object.select_pattern(pattern=strokeEnd.name)
            
        for strokeActive in strokes_to_make_active:
            bpy.ops.object.select_pattern(pattern=strokeActive.name)
            bpy.context.scene.objects.active = strokeActive
            
                
    return None

def Update_Normalise(self, context):
    
    if bpy.context.scene.ASKETCH_live_update is not False:
    
        # Create an array to store all found objects
        strokes_to_select = []
        strokes_to_make_active = []
        
        if bpy.context.active_object.name.find(".SKO") != -1:
            strokes_to_make_active.append(bpy.context.active_object)
        
        
        # Find all the Stroke Objects in the scene
        for stroke in bpy.context.selected_objects:
            if stroke.name.find(".SKO") != -1:
                
                strokes_to_select.append(stroke)
                
                # Change the internal values of the object
                stroke.ASKETCH_stroke_size = 1
                stroke.ASKETCH_stroke_element_offset = 1
                stroke.ASKETCH_stroke_central_size = 1
            
                # Find the Curve
                stroke.modifiers["Array"].relative_offset_displace = [1, 0, 0]
                stroke_curve_name = stroke.name.replace(".SKO", ".SKC")
                FocusObject(stroke_curve_name)
                curve_data = bpy.context.object.data  
                
                # Call the Set Curve Radius class
                bpy.ops.object.editmode_toggle()
                ASKETCH_SetStrokeRadius(curve_data, 1, 1)
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.select_all(action='DESELECT')  
                
                  
        # Re-select all stored objects         
        for strokeEnd in strokes_to_select:
            bpy.ops.object.select_pattern(pattern=strokeEnd.name)
            
        for strokeActive in strokes_to_make_active:
            bpy.ops.object.select_pattern(pattern=strokeActive.name)
            bpy.context.scene.objects.active = strokeActive
        
    return {"FINISHED"}
    
def Update_XMirror(self, context):
    
    if bpy.context.scene.ASKETCH_live_update is not False:

        # Create an array to store all found objects
        strokes_to_select = []
        strokes_to_make_active = []
        
        if bpy.context.active_object.name.find(".SKO") != -1:
            strokes_to_make_active.append(bpy.context.active_object)
        
        
        # Find all the Stroke Objects in the scene
        for stroke in bpy.context.selected_objects:
            if stroke.name.find(".SKO") != -1: 
                if stroke.ASKETCH_x_mirror_on is True:
                    
                    # Add the mirror modifier
                    FocusObject(stroke.name)
                    
                    bpy.ops.object.modifier_add(type='MIRROR')
                    
                    stroke.modifiers['Mirror'].use_X = True
                    
                else:
                    FocusObject(stroke.name)
                    
                    scene = bpy.context.scene
                    mod_types = {'MIRROR'}
                    
                    # Get an array of the active modifiers in the stroke
                    mod_active = [mod.show_viewport for mod in stroke.modifiers]
            
                    # THANKS BLENDER ARTISTS USER CoDEmannX for this code!
                    for mod in stroke.modifiers:
                        if mod.type not in mod_types:
                            mod.show_viewport = False
            
                    me = stroke.to_mesh(scene, False, 'PREVIEW')
            
                    for mod, active in zip(stroke.modifiers, mod_active):
                        if mod.type in mod_types:
                            stroke.modifiers.remove(mod)
                        else:
                            mod.show_viewport = active
        
                    # Note: this only swaps the object's data, but doesn't remove the original mesh
                    stroke.data = me
                    
        
        # Find all the Stroke Objects in the scene
        for stroke in bpy.context.selected_objects:
            if stroke.name.find(".SKO") != -1: 
                print("We're updating!")
                
    return None    
    
def Update_MergeElements(self, context):
        
    if bpy.context.scene.ASKETCH_live_update is not False:
        
        # Create an array to store all found objects
        strokes_to_select = []
        strokes_to_make_active = []
        
        if bpy.context.active_object.name.find(".SKO") != -1:
            strokes_to_make_active.append(bpy.context.active_object)
            

        # Find all the Stroke Objects in the scene
        for stroke in bpy.context.selected_objects:
            if stroke.name.find(".SKO") != -1: 
                
                FocusObject(stroke.name)
                stroke.modifiers['Array'].use_merge_vertices = stroke.ASKETCH_connect_elements
                stroke.modifiers['Array'].use_merge_vertices_cap = stroke.ASKETCH_connect_elements
                stroke.modifiers['Array'].merge_threshold = 1.0
        
        
        # Re-select all stored objects         
        for strokeEnd in strokes_to_select:
            bpy.ops.object.select_pattern(pattern=strokeEnd.name)
            
        for strokeActive in strokes_to_make_active:
            bpy.ops.object.select_pattern(pattern=strokeActive.name)
            bpy.context.scene.objects.active = strokeActive
            
    return None
                
    
def Update_CurveObject(self, context):
    
    if bpy.context.scene.ASKETCH_live_update is not False:

        # Create an array to store all found objects
        strokes_to_select = []
        strokes_to_make_active = []
        
        if bpy.context.active_object.name.find(".SKO") != -1:
            strokes_to_make_active.append(bpy.context.active_object)
        
        
        # Find all the Stroke Objects in the scene
        for stroke in bpy.context.selected_objects:
            if stroke.name.find(".SKO") != -1: 
                if stroke.ASKETCH_object_curve is True:
                    
                    FocusObject(stroke.name)
                    
                    #modifiers = object.modifiers
                    #for modifier in object.modifiers:
                    #    if (modifier.type == Blender.Modifier.Types.SUBSURF):
                    #        object.modifiers.remove(modifier)
                    #        object.makeDisplayList()
                    
                    scene = bpy.context.scene
                    mod_types = {'ARRAY'}
                    
                    # Get an array of the active modifiers in the stroke
                    mod_active = [mod.show_viewport for mod in stroke.modifiers]
            
                    # THANKS BLENDER ARTISTS USER CoDEmannX for this code!
                    for mod in stroke.modifiers:
                        if mod.type not in mod_types:
                            mod.show_viewport = False
            
                    me = stroke.to_mesh(scene, False, 'PREVIEW')
            
                    for mod, active in zip(stroke.modifiers, mod_active):
                        if mod.type in mod_types:
                            stroke.modifiers.remove(mod)
                        else:
                            mod.show_viewport = active
        
                    # Note: this only swaps the object's data, but doesn't remove the original mesh
                    stroke.data = me
                    
                            
                else:
                    FocusObject(stroke.name)
                    
                    bpy.ops.object.modifier_add(type='ARRAY')
                    
                    if stroke.ASKETCH_connect_elements is True:
                        stroke.modifiers['Array'].use_merge_vertices = True
                        
                    stroke.modifiers['Array'].use_merge_vertices_cap = True
                    stroke.modifiers['Array'].merge_threshold = 1.0
            
            
                    # Modifies the Array attributes
                    stroke.modifiers["Array"].relative_offset_displace = [self.ASKETCH_stroke_element_offset, 0, 0]
                    stroke.modifiers["Array"].fit_type = "FIT_CURVE"
                    
                    stroke_curve_name = stroke.name.replace(".SKO", ".SKC")
                    FocusObject(stroke_curve_name)
                    
                    stroke.modifiers["Array"].curve = bpy.context.scene.objects.active
                    
                    # Push the modifier to the top of the stack
                    FocusObject(stroke.name)
                    bpy.ops.object.modifier_move_up(modifier="Array")
                    bpy.ops.object.modifier_move_up(modifier="Array")
                    bpy.ops.object.modifier_move_up(modifier="Array")
                    bpy.ops.object.modifier_move_up(modifier="Array")
                              
                    
                            
        # Re-select all stored objects         
        for strokeEnd in strokes_to_select:
            bpy.ops.object.select_pattern(pattern=strokeEnd.name)
            
        for strokeActive in strokes_to_make_active:
            bpy.ops.object.select_pattern(pattern=strokeActive.name)
            bpy.context.scene.objects.active = strokeActive
            
    return None
    
def Update_LockTransform(self, context):
    
    if bpy.context.scene.ASKETCH_live_update is not False:
        
        # Create an array to store all found objects
        strokes_to_select = []
        strokes_to_make_active = []
        
        if bpy.context.active_object.name.find(".SKO") != -1:
            strokes_to_make_active.append(bpy.context.active_object)
        
        
        # Find all the Stroke Objects in the scene
        for stroke in bpy.context.selected_objects:
            if stroke.name.find(".SKO") != -1: 
                
                if self.ASKETCH_lock_transform is True:
                    bpy.data.objects[stroke.name].lock_location[0] = True
                    bpy.data.objects[stroke.name].lock_location[1] = True
                    bpy.data.objects[stroke.name].lock_location[2] = True
                    
                if self.ASKETCH_lock_transform is False:
                    bpy.data.objects[stroke.name].lock_location[0] = False
                    bpy.data.objects[stroke.name].lock_location[1] = False
                    bpy.data.objects[stroke.name].lock_location[2] = False
                
        # Re-select all stored objects         
        for strokeEnd in strokes_to_select:
            bpy.ops.object.select_pattern(pattern=strokeEnd.name)
            
        for strokeActive in strokes_to_make_active:
            bpy.ops.object.select_pattern(pattern=strokeActive.name)
            bpy.context.scene.objects.active = strokeActive
            
    return None     
    
def Update_TwistMode(self,context):
    
    if bpy.context.scene.ASKETCH_live_update is not False:
        
        # Create an array to store all found objects
        strokes_to_select = []
        strokes_to_make_active = []
        
        if bpy.context.active_object.name.find(".SKO") != -1:
            strokes_to_make_active.append(bpy.context.active_object)
        
        
        # Find all the Stroke Objects in the scene
        for stroke in bpy.context.selected_objects:
            if stroke.name.find(".SKO") != -1: 
                
                # Store the stroke
                strokes_to_select.append(stroke)
                
                # Obtain the ENUM
                selected_object = int(self.ASKETCH_twist_mode)
                
                # Get the curve instead
                stroke_curve_name = stroke.name.replace(".SKO", ".SKC")
                FocusObject(stroke_curve_name)
                
                # Tangent
                if selected_object == 1:
                    bpy.context.active_object.data.twist_mode = 'TANGENT'
                    
                # Minimum
                if selected_object == 2:
                    bpy.context.active_object.data.twist_mode = 'MINIMUM'
                    
                # Z-Up
                if selected_object == 3:
                    bpy.context.active_object.data.twist_mode = 'Z_UP'
                    
                bpy.ops.object.select_all(action='DESELECT') 
                    
        # Re-select all stored objects         
        for strokeEnd in strokes_to_select:
            bpy.ops.object.select_pattern(pattern=strokeEnd.name)
            
        for strokeActive in strokes_to_make_active:
            bpy.ops.object.select_pattern(pattern=strokeActive.name)
            bpy.context.scene.objects.active = strokeActive
            
    return None     

def Update_TwistTilt(self, context):
    
    if bpy.context.scene.ASKETCH_live_update is not False:
    
        # Create an array to store all found objects
        strokes_to_select = []
        strokes_to_make_active = []
        
        if bpy.context.active_object.name.find(".SKO") != -1:
            strokes_to_make_active.append(bpy.context.active_object)
        
        # Find all the Stroke Objects in the scene
        for stroke in bpy.context.selected_objects:
            if stroke.name.find(".SKO") != -1:
                
                # Add it in the array so it can be re-selected later
                strokes_to_select.append(stroke)
                
                tilt_increment = (self.ASKETCH_tilt - self.ASKETCH_tilt_old) * degree_per_radian

                stroke_curve_name = stroke.name.replace(".SKO", ".SKC")
                FocusObject(stroke_curve_name)
                curve_data = bpy.context.object.data
                
                # Change the point tilt
                #ASKETCH_SetStrokeTilt(curve_data, self.ASKETCH_tilt)
                for checkPoints in bpy.data.curves[curve_data.name].splines[0].bezier_points:
                    checkPoints.tilt = tilt_increment + checkPoints.tilt
                    
                self.ASKETCH_tilt_old = self.ASKETCH_tilt
                
                bpy.ops.object.select_all(action='DESELECT') 

        # Re-select all stored objects         
        for strokeEnd in strokes_to_select:
            bpy.ops.object.select_pattern(pattern=strokeEnd.name)
             
        for strokeActive in strokes_to_make_active:
            bpy.ops.object.select_pattern(pattern=strokeActive.name)
            bpy.context.scene.objects.active = strokeActive
            
    return None     

def Update_NormaliseTilt(self, context):
    
    if bpy.context.scene.ASKETCH_live_update is not False:
    
        # Create an array to store all found objects
        strokes_to_select = []
        strokes_to_make_active = []
        
        if bpy.context.active_object.name.find(".SKO") != -1:
            strokes_to_make_active.append(bpy.context.active_object)
        
        # Find all the Stroke Objects in the scene
        for stroke in bpy.context.selected_objects:
            if stroke.name.find(".SKO") != -1:
                
                # Add it in the array so it can be re-selected later
                strokes_to_select.append(stroke)

                stroke_curve_name = stroke.name.replace(".SKO", ".SKC")
                FocusObject(stroke_curve_name)
                curve_data = bpy.context.object.data
                
                # Change the point tilt
                #ASKETCH_SetStrokeTilt(curve_data, self.ASKETCH_tilt)
                for checkPoints in bpy.data.curves[curve_data.name].splines[0].bezier_points:
                    checkPoints.tilt = 0
                    
                # Cheap way of forcing the object to redraw
                bpy.ops.object.editmode_toggle()
                
                self.ASKETCH_tilt = 0.0
                self.ASKETCH_tilt_old = 0.0
                
                bpy.ops.object.editmode_toggle()
                
                bpy.ops.object.select_all(action='DESELECT') 

        # Re-select all stored objects         
        for strokeEnd in strokes_to_select:
            bpy.ops.object.select_pattern(pattern=strokeEnd.name)
             
        for strokeActive in strokes_to_make_active:
            bpy.ops.object.select_pattern(pattern=strokeActive.name)
            bpy.context.scene.objects.active = strokeActive
            
    return None 

def Update_ObjectOrigin(self, context):
    
    if bpy.context.scene.ASKETCH_live_update is not False:
    
        # Create an array to store all found objects
        strokes_to_select = []
        strokes_to_make_active = []
        
        if bpy.context.active_object.name.find(".SKO") != -1:
            strokes_to_make_active.append(bpy.context.active_object)
        
        # Find all the Stroke Objects in the scene
        for stroke in bpy.context.selected_objects:
            if stroke.name.find(".SKO") != -1:
                
                # Add it in the array so it can be re-selected later
                strokes_to_select.append(stroke)
                
                selected_item = int(self.ASKETCH_origin_point)
                
                print("Going to UpdateObjectOrigin")
                ASKETCH_SetObjectOrigin(self, selected_item, context)
                
                bpy.ops.object.select_all(action='DESELECT') 

        # Re-select all stored objects         
        for strokeEnd in strokes_to_select:
            bpy.ops.object.select_pattern(pattern=strokeEnd.name)
             
        for strokeActive in strokes_to_make_active:
            bpy.ops.object.select_pattern(pattern=strokeActive.name)
            bpy.context.scene.objects.active = strokeActive
            
    return None 

def Update_OriginUpdate(self, context):
    
    if bpy.context.scene.ASKETCH_live_update is not False:
    
        # Create an array to store all found objects
        strokes_to_select = []
        strokes_to_make_active = []
        
        if bpy.context.active_object.name.find(".SKO") != -1:
            strokes_to_make_active.append(bpy.context.active_object)
        
        # Find all the Stroke Objects in the scene
        for stroke in bpy.context.selected_objects:
            if stroke.name.find(".SKO") != -1:
                
                if self.SCENE_origin_update is True:
                    
                    # Add it in the array so it can be re-selected later
                    strokes_to_select.append(stroke)
                    
                    FocusObject(stroke.name)
                    enum = int(bpy.context.active_object.ASKETCH_origin_point)
                    print("Rawr")
                
                    print("Going to UpdateObjectOrigin")
                    ASKETCH_SetObjectOrigin(stroke, enum, context)
                    
                    bpy.ops.object.select_all(action='DESELECT') 

        # Re-select all stored objects         
        for strokeEnd in strokes_to_select:
            bpy.ops.object.select_pattern(pattern=strokeEnd.name)
             
        for strokeActive in strokes_to_make_active:
            bpy.ops.object.select_pattern(pattern=strokeActive.name)
            bpy.context.scene.objects.active = strokeActive
            
    return None 
                    

#///////////////// - ADDITIONAL PROPERTY DEFINITIONS - ///////////////////////////
bpy.types.Object.ASKETCH_stroke_size  = bpy.props.FloatProperty(
    name = "Stroke Size", 
    description = "Change the stroke size",
    update = Update_StrokeSize,
    default = 1, soft_min = 0.25, soft_max = 3, min = 0.1, max = 10)
bpy.types.Scene.SCENE_stroke_size  = bpy.props.FloatProperty(
    name = "Stroke Size", 
    description = "Change the stroke size",
    default = 1, soft_min = 0.25, soft_max = 3, min = 0.1, max = 10)
        
bpy.types.Object.ASKETCH_stroke_element_offset = bpy.props.FloatProperty(
    name = "Stroke Density", 
    description = "Change the space between elements along the curve.  Smaller numbers = Denser curve.  WARNING - Dont use on a value below 0.5 when Merge Elements is active.",
    update = Update_StrokeDensity, 
     default = 1, soft_min = 0.25, soft_max = 3, min = 0.1, max = 3)
bpy.types.Scene.SCENE_stroke_element_offset = bpy.props.FloatProperty(
    name = "Stroke Density", 
    description = "Change the space between elements along the curve.  Smaller numbers = Denser curve.  WARNING - Dont use on a value below 0.5 when Merge Elements is active.",
    default = 1, soft_min = 0.25, soft_max = 3, min = 0.1, max = 3)
    
bpy.types.Object.ASKETCH_stroke_central_size  = bpy.props.FloatProperty(
    name = "Midpoint Scale", 
    description = "Change the scale of the brush at the center of the stroke",
    update = Update_StrokeSize,
    default = 1, soft_min = 0.25, soft_max = 10, min = 0.1, max = 15)
bpy.types.Scene.SCENE_stroke_central_size  = bpy.props.FloatProperty(
    name = "Midpoint Scale", 
    description = "Change the scale of the brush at the center of the stroke",
    default = 1, soft_min = 0.25, soft_max = 10, min = 0.1, max = 15)
    
    
bpy.types.Object.ASKETCH_twist_mode = bpy.props.EnumProperty(
    name="Twist Mode",
    items=(
       ('1', 'Tangent', 'Use the tangent to calculate twist.'),
       ('2', 'Minimum', 'Use the least twist over the entire curve'),
       ('3', 'Z-Up', 'Use the Z-Axis to calculate the curve twist at each point'),
    ),
    update = Update_TwistMode)
    
bpy.types.Object.ASKETCH_tilt = bpy.props.FloatProperty(
    name = "Tilt", 
    description = "Rotate the stroke across the curve", 
    update = Update_TwistTilt,
    default = 0.0, soft_min = 0.0, soft_max = 360, min = 0.0, max = 360)
bpy.types.Object.ASKETCH_tilt_old = bpy.props.FloatProperty(
    name = "TiltOld", 
    description = "Rotate the stroke across the curve", 
    default = 0.0, soft_min = 0.0, soft_max = 360, min = 0.0, max = 360)
 
bpy.types.Object.ASKETCH_smooth = bpy.props.FloatProperty(
    name = "Smooth", 
    description = "Sets how much tilt smoothing is performed",
    #update = Update_TwistSmooth, 
    default = 0, soft_min = 0, soft_max = 20, min = 0, max = 20)
    
    
    
bpy.types.Object.ASKETCH_origin_point = bpy.props.EnumProperty(
    name="Set Object Origin",
    items=(
       ('1', 'Dont Set Origin', 'Leaves the origin to its original position'),
       ('2', 'Origin to Centre of Mass', 'Sets the origin using the objects centre of mass.'),
       ('3', 'Origin to Start of Curve', 'Sets the origin to the start of the curve'),
       ('4', 'Origin to End of Curve', 'Sets the origin to the end of the curve'),
    ),
    update = Update_ObjectOrigin)
    
bpy.types.Scene.SCENE_origin_point = bpy.props.EnumProperty(
    name="Set Scene Origin",
    items=(
       ('1', 'Origin to Active Object', 'Sets the origin to the active objects origin.'),
       ('2', 'Origin to Cursor', 'Sets the origin to the current cursor location'),    
       ('3', 'Origin to Centre of Mass', 'Sets the origin using the objects centre of mass.'),
       ('4', 'Origin to Start of Curve', 'Sets the origin to the start of the curve'),
       ('5', 'Origin to End of Curve', 'Sets the origin to the end of the curve'),
    ),)
    
    
bpy.types.Scene.SCENE_origin_update = bpy.props.BoolProperty(
    name = "Update Origin", 
    description = "Keeps the origin updated whenever the curve is changed",
    update = Update_OriginUpdate, 
    default = False)
    
    
    
    
bpy.types.Scene.ASKETCH_live_update = bpy.props.BoolProperty(
    name = "Edit Selected Objects", 
    description = "Updates every selected object when Sketch Settings are changed", 
    default = False)

   
   
bpy.types.Object.ASKETCH_x_mirror_on = bpy.props.BoolProperty(
    name = "X Mirror", 
    description = "Mirror the stroke across the X axis", 
    update = Update_XMirror,
    default = False)
bpy.types.Scene.SCENE_x_mirror_on = bpy.props.BoolProperty(
    name = "X Mirror", 
    description = "Mirror the stroke across the X axis", 
    default = False)
    
bpy.types.Object.ASKETCH_connect_elements = bpy.props.BoolProperty(
    name = "Merge Elements", 
    description = "Merges the ends of objects together to create a connected, seamless mesh",
    update = Update_MergeElements, 
    default = False)
bpy.types.Scene.SCENE_connect_elements = bpy.props.BoolProperty(
    name = "Merge Elements", 
    description = "Merges the ends of objects together to create a connected, seamless mesh", 
    default = False)
    
bpy.types.Object.ASKETCH_object_curve = bpy.props.BoolProperty(
    name = "Curve Object", 
    description = "Bends a singular instance of the mesh along a curve",
    update = Update_CurveObject, 
    default = False)
bpy.types.Scene.SCENE_object_curve = bpy.props.BoolProperty(
    name = "Curve Object", 
    description = "Bends a singular instance of the mesh along a curve", 
    default = False)

bpy.types.Object.ASKETCH_lock_transform = bpy.props.BoolProperty(
    name = "Lock Transform", 
    description = "Prevents generated curve from moving if ticked",
    update = Update_LockTransform, 
    default = False)
bpy.types.Scene.SCENE_lock_transform = bpy.props.BoolProperty(
    name = "Lock Transform", 
    description = "Prevents generated curve from moving if ticked", 
    default = False)



bpy.types.Scene.ASKETCH_brush_object = bpy.props.StringProperty(
    name = "Brush", 
    description = "Name of the object used as brush", 
    default = "None")
    
bpy.types.Scene.ASKETCH_start_cap = bpy.props.StringProperty(
    name = "Start Cap", 
    description = "Name of the object used as brush", 
    default = "None")
    
bpy.types.Scene.ASKETCH_end_cap = bpy.props.StringProperty(
    name = "End Cap", 
    description = "Name of the object used as brush", 
    default = "None")

default_brush_name = "A_SK_brush_default"



# P - I don't understand what these do???
# Neither do I...
#//////////////////////////////// - MYSTERY ENTITY 01 - ////////////////////////////////

def ASKETCH_default_brush_object(self): return default_brush_name
bpy.types.Object.ASKETCH_default_brush_object = property(ASKETCH_default_brush_object)

def ASKETCH_brush_object(self): return default_brush_name
bpy.types.Object.ASKETCH_brush_object = property(ASKETCH_brush_object)


def ASKETCH_mball_stroke_definition(self): return mball_definition
bpy.types.Object.ASKETCH_mball_stroke_definition = property(ASKETCH_mball_stroke_definition)

def ASKETCH_mball_wire_resolution(self): return mball_wire_resolution
bpy.types.Object.ASKETCH_mball_wire_resolution = property(ASKETCH_mball_wire_resolution)



#//////////////////////////// - MYSTERY ENTITY 02 - ////////////////////////////////

#check if the default brush is already there:
#This code tries to manipulate data on registration, and Blender doesn't like that.  BROKEN!
#defaultb_there = False  
#for ob in bpy.data.objects:
#    if(ob.name == 'AS_Brush_Default'):
#        defaultb_there = True
        
#if not, then we add it:
#if(defaultb_there == False):
#    bpy.ops.mesh.primitive_uv_sphere_add()
#    bpy.data.objects[-1].name = 'AS_Brush_Default'




#///////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////


#//////////////////// - USER INTERFACE PANELS - /////////////////////////////
class View3DPanel():
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
#Generates the UI panel inside the 3D view
class VIEW3D_PT_tools_ASKETCH_create(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Create Sketch"
    bl_category = "Grease Pencil"

    
    #def poll(self, context):
        #return context.active_object != None

    def draw(self, context):
        layout = self.layout
        
        scn = context.scene
        ob = context.object

        #layout.label(text="Add/Edit/Delete")
        col_ad = layout.column(align=True)
        col_ad.alignment = 'EXPAND'  
        row_ad = col_ad.row(align=True)
        row_ad.operator("gpencil.asketch_stroke_draw", text="Add Stroke")
        row_ad.operator("object.asketch_delete_strokes", text="Delete Stroke")
        
        row_ad = col_ad.row(align=True)
        row_ad.operator("object.asketch_stroke_editmode", text="Edit Stroke")
        row_ad.operator("gpencil.asketch_clear_data", text="Clear Grease Strokes")
        
        layout.separator()
        
        col_brush = layout.column(align=True)
        col_brush.alignment = 'EXPAND'
        row_brush = col_brush.row(align=True)
        #split = layout.split()
        #col = split.column()
        #col.label(text="Target:")
        #col.prop(md, "target", text="")
        
        row_brush.prop(scn, "ASKETCH_brush_object")
        row_brush.operator("object.asketch_set_brush_object", text="", icon="FORWARD")
        row_brush.operator("object.asketch_clear_brush_object", text="", icon="X")
        col_brush.separator()
        
        row_brush = col_brush.row(align=True)
        row_brush.prop(scn, "ASKETCH_start_cap")
        row_brush.operator("object.asketch_set_start_cap", text="", icon="FORWARD")
        row_brush.operator("object.asketch_clear_start_cap", text="", icon="X")
        col_brush.separator()
        
        row_brush = col_brush.row(align=True)
        row_brush.prop(scn, "ASKETCH_end_cap")
        row_brush.operator("object.asketch_set_end_cap", text="", icon="FORWARD")
        row_brush.operator("object.asketch_clear_end_cap", text="", icon="X")
        #row_brush.prop(md, "bpy.context.scene.ASKETCH_brush_object", text="Rawr")
        
        # row_update = layout.column(align=True)
        # row_update.prop(scn, "ASKETCH_live_update_new")
        
        
#Generates the UI panel inside the 3D view
class VIEW3D_PT_tools_ASKETCH_edit_settings(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Sketch Settings"
    bl_category = "Grease Pencil"

    def draw(self, context):
        layout = self.layout
        
        scn = context.scene
        ob = context.object
        
        row_edit = layout.column(align=True)
        row_edit.alignment = 'EXPAND'
        row_edit = layout.column(align=True)
        row_edit.prop(scn, "ASKETCH_live_update")
        
        row_edit.separator()
        
        if context.scene.ASKETCH_live_update is True and context.active_object.name.find(".SKO") != -1:
            row_edit.prop(ob, "ASKETCH_stroke_size", slider = True)
            row_edit.prop(ob, "ASKETCH_stroke_element_offset", slider = True)
            row_edit.prop(ob, "ASKETCH_stroke_central_size", slider = True)
            row_edit.operator("object.asketch_normalise_options", text="Normalise")
        
            row_edit.separator()
            
            col_origin = layout.row(align=True)
            col_origin.alignment = 'EXPAND'
            col_origin.prop(ob, "ASKETCH_origin_point", text = "", icon = "CURSOR")
            col_origin.prop(scn, "SCENE_origin_update", text="", toggle = True, icon = "ALIGN", icon_only = True)
            
            col_origin.separator()
         
            layout.label(text="Stroke Options")
            col_edit = layout.row(align=True)
            row_edit= col_edit.row(align=True)
            row_edit.alignment = 'EXPAND'
            row_edit.prop(ob, "ASKETCH_x_mirror_on")
            row_edit.prop(ob, "ASKETCH_connect_elements")
            row_edit = layout.row(align=True)
            row_edit.prop(ob, "ASKETCH_object_curve")
            row_edit.prop(ob, "ASKETCH_lock_transform")
            
            layout.separator()
            
            col_align = layout.column(align=True)
            col_align.alignment = 'EXPAND'
            row_align = col_align.row(align=True)
            #row_align.label(text="Curve Tilt")
            #row_align.separator()
            row_align.prop(ob, "ASKETCH_tilt", slider=True)
            
            #row_align = col_align.row(align=True)
            #row_align.prop(ob, 'ASKETCH_smooth', slider=True)   
            
            row_align = col_align.row(align=True)
            row_align.prop(ob, "ASKETCH_twist_mode", text = "", icon = "MAN_ROT")
            row_align.operator("object.asketch_normalise_tilt", text="Normalise Tilt")   
            
            
            
        else:
            row_edit.prop(scn, "SCENE_stroke_size", slider = True)
            row_edit.prop(scn, "SCENE_stroke_element_offset", slider = True)
            row_edit.prop(scn, "SCENE_stroke_central_size", slider = True)
            row_edit.operator("object.asketch_normalise_options", text="Normalise")
            
            row_edit.separator()
            
            col_origin = layout.row(align=True)
            col_origin.alignment = 'EXPAND'
            col_origin.prop(scn, "SCENE_origin_point", text = "", icon = "CURSOR")
            col_origin.prop(scn, "SCENE_origin_update", text="", toggle = True, icon = "ALIGN", icon_only = True)
        
            col_origin.separator()
         
            layout.label(text="Stroke Options")
            col_edit = layout.row(align=True)
            row_edit= col_edit.row(align=True)
            row_edit.alignment = 'EXPAND'
            row_edit.prop(scn, "SCENE_x_mirror_on")
            row_edit.prop(scn, "SCENE_connect_elements")
            row_edit = layout.row(align=True)
            row_edit.prop(scn, "SCENE_object_curve")
            row_edit.prop(scn, "SCENE_lock_transform")
     
        
        layout.separator()
        
        
        
# Generates the UI panel inside the 3D view
class VIEW3D_PT_tools_ASKETCH_Convert(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Convert Sketch"
    bl_category = "Grease Pencil"

    def draw(self, context):
        layout = self.layout
        
        scn = context.scene
        ob = context.object
        
        col_convert = layout.column(align=True)
        col_convert.alignment = 'EXPAND'

        #row_convert = col_convert.row(align=True)
        #row_convert.label(text="Convert Using Metaballs")
        #col_convert.separator()
        
        #row_convert = col_convert.row(align=True)
        #row_convert.operator("object.asketch_strokes_to_metaballs", text="Step 1")
        #row_convert.operator("object.asketch_metaballs_rename", text="Step 2")
        #row_convert.operator("object.asketch_metaballs_to_mesh", text="Step 3")
        #col_convert.separator()
        
        row_convert= col_convert.column(align=True)
        row_convert.operator("object.asketch_strokes_to_meshes", text="Convert to Mesh")
        #row_convert.operator("object.asketch_strokes_to_meshes", text="Convert using Boolean")
        col_convert.separator()
        
        
        row_vis = layout.column(align=True)
        row_vis.alignment = 'EXPAND'
        #row_vis.label(text="Visibility")
        #row_vis.operator("object.asketch_toggle_mesh_visibility", text="Toggle Mesh Visibility")
        #row_vis.separator()
       
        
def DuplicateObject(target, targetLocation):
    
    #### Select and make target active
    bpy.ops.object.select_all(action='DESELECT')  
    bpy.context.scene.objects.active = bpy.data.objects[target.name]
    bpy.ops.object.select_pattern(pattern=target.name)
    
    # Duplicate the object
    bpy.ops.object.duplicate_move()
    
    # Now switch the active object to the duplicate
    target = bpy.context.active_object
    target.location = targetLocation.location
    
    
def FocusObject(targetName):
    
    #### Select and make target active
    bpy.ops.object.select_all(action='DESELECT')  
    bpy.context.scene.objects.active = bpy.data.objects[targetName]
    bpy.ops.object.select_pattern(pattern=targetName) 
    

class VIEW3D_PT_tools_ASKETCH_editmode(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "curve_edit"
    bl_label = "Arrays Sketching"
    bl_category = "Grease Pencil" 

    @classmethod    
    def poll(self, context):
        return context.active_object

    def draw(self, context):
        layout = self.layout
        
        ob = context.object
        
        col = layout.column(align=True)
        col.operator("object.asketch_stroke_editmode_exit", text="Return to Object Mode")
        col.separator()
        col.label(text="Stroke Tools")
        col.operator("object.asketch_stroke_smooth_size", text="Smooth Size")
        
   
        
#//////////////////////////////// - Normalise UI - //////////////////////////
class ASKETCH_normalise_options(bpy.types.Operator):
    """Resets the stroke option variables back to default settings.  Useful if you need to sketch using the initial properties of the brush."""
    
    bl_idname = "object.asketch_normalise_options"
    bl_label = "Normalise Settings"
    
    def execute(self, context):
        print(self)
        
        self.ASKETCH_stroke_size = 1;
        self.ASKETCH_stroke_element_offset = 1;
        self.ASKETCH_stroke_central_size = 1;
        
        Update_Normalise(self, context)
        
        return {'FINISHED'}
    
class ASKETCH_normalise_tilt(bpy.types.Operator):
    """Resets the stroke option variables back to default settings.  Useful if you need to sketch using the initial properties of the brush."""
    
    bl_idname = "object.asketch_normalise_tilt"
    bl_label = "Normalise Tilt"
    
    def execute(self, context):
        print(self)
        
        self.ASKETCH_tilt = 0.0
        self.ASKETCH_tilt_old = 0.0
        
        Update_NormaliseTilt(self, context)
        
        return {'FINISHED'}
        

        
#//////////////////////////////// - GPencil Management - ///////////////////////////
class GPencil_Clear_Data(bpy.types.Operator):
    """Clears the Grease Pencil data currently displayed"""
    bl_idname = "gpencil.asketch_clear_data"
    bl_label = "Array Sketch Clear GPencil"
    bl_options = {'REGISTER', 'UNDO'}
    
    #This code was graciously pinched from the Sculpt Tools addon :D
    
    #@classmethod
    #def poll(cls, context):
    #    return context.active_object is not None

    def execute(self, context):
        if not context.scene.grease_pencil == None:
            context.scene.grease_pencil.clear()
        for obj in context.scene.objects:
            if not context.scene.objects[obj.name].grease_pencil == None:
                context.scene.objects[obj.name].grease_pencil.clear() 
        return {'FINISHED'}
    
    
#//////////////////////////////// - Set Curve Data - ///////////////////////////
def ASKETCH_SetStrokeRadius(curveData, strokeSize, centralSize):
        
    # Get brush point data
    points = bpy.data.curves[curveData.name].splines[0].bezier_points
    central_point = int(len(points)/2)
    
    bpy.ops.curve.select_all(action="DESELECT") 
    bpy.ops.curve.de_select_first()  
    #this selects the first point because it is a toggle function (becuase we have deselected everything, )
    bpy.ops.curve.de_select_last()  
    bpy.ops.curve.radius_set(radius = strokeSize)
        
    #Patrick's Version
    bpy.ops.curve.select_all(action = "DESELECT")
    points[int(len(points)/2)].select_control_point = True
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.editmode_toggle()  #I'm not sure if toggling in/out of editmode is still necessary for selected points to update. but I'm not risking it :-)
        
    #from the above, just the middle point should have been selected, so now we can set the flatten radius
    bpy.ops.curve.radius_set(radius = strokeSize * centralSize)
    
    #now that the first, middle and last have their radii set appropriately, smooth out the points ibnetween by....
    bpy.ops.curve.select_all(action="INVERT")  #selecing everything but the middle
    bpy.ops.curve.de_select_first()  #deselecting the first
    bpy.ops.curve.de_select_last()   #deselecting the last (remember they were selected at this point and this operator toggles)
    bpy.ops.curve.smooth_radius()  #do we need to specify any iterations here?
    bpy.ops.curve.select_all(action="DESELECT")
    
    
def ASKETCH_SetStrokeTilt(curveData, strokeTilt):
        
    # Get brush point data
    points = bpy.data.curves[curveData.name].splines[0].bezier_points
    central_point = int(len(points)/2)
    
    bpy.ops.curve.select_all(action="DESELECT") 
    bpy.ops.curve.de_select_first()  
    bpy.ops.curve.de_select_last()  

        
    for checkPoints in bpy.data.curves[curveData.name].splines[0].bezier_points:
        checkPoints.tilt = strokeTilt #+ checkPoints.tilt
        
    #Patrick's Version
    bpy.ops.curve.select_all(action = "DESELECT")
    points[int(len(points)/2)].select_control_point = True
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.editmode_toggle()
    
    bpy.ops.curve.select_all(action="INVERT") 
    bpy.ops.curve.de_select_first() 
    bpy.ops.curve.de_select_last()  
    bpy.ops.curve.smooth_radius()
    bpy.ops.curve.select_all(action="DESELECT")
    
    
    
    
#//////////////////////////////// - OBJECT ORIGIN- ////////////////////////////////
    
def ASKETCH_SetObjectOrigin(object, enum, context):
    
    print("Inside ASKETCH_SetObjectOrigin")
        
    # Set to COM
    if enum == 2:
        print("Setting to COM")
        
        # Enter the curve!
        stroke_curve_name = object.name.replace(".SKO", ".SKC")
        FocusObject(stroke_curve_name)
        curve_data = bpy.context.object.data
        
        # Select everything
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.select_all(action="SELECT")
        bpy.ops.curve.de_select_first()
        
        # Saves the current cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
        previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
        
        # Snap the cursor
        bpy.ops.view3D.snap_cursor_to_selected()
        bpy.ops.curve.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        # Temporarily remove the Copy Location Constraint
        FocusObject(stroke_curve_name)
        bpy.ops.object.constraints_clear()
        
        # Now give the curve the same location as the object
        FocusObject(stroke_curve_name)
        bpy.context.object.location = object.location
        
        # Set the origin
        bpy.ops.object.origin_set(type ='ORIGIN_CURSOR')
        
        # Move the object to the curve
        FocusObject(object.name)
        bpy.context.object.location = bpy.data.objects[stroke_curve_name].location
        
        # Now just re-apply the constraint!
        FocusObject(stroke_curve_name)
        bpy.ops.object.constraint_add(type='COPY_LOCATION')
        bpy.data.objects[stroke_curve_name].constraints["Copy Location"].target = object
        
        # Restore the original cursor location
        bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
        
        
    # Set to Curve Start
    elif enum == 3:
        print("Setting to First")
        
        # Enter the curve!
        stroke_curve_name = object.name.replace(".SKO", ".SKC")
        FocusObject(stroke_curve_name)
        curve_data = bpy.context.object.data
        
        # Only select the beginning curve point
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.select_all(action="DESELECT")
        bpy.ops.curve.de_select_first() 
        
        # Saves the current cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
        previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
        
        # Snap the cursor
        bpy.ops.view3D.snap_cursor_to_selected()
        bpy.ops.curve.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        # Temporarily remove the Copy Location Constraint
        FocusObject(stroke_curve_name)
        bpy.ops.object.constraints_clear()
        
        # Now give the curve the same location as the object
        FocusObject(stroke_curve_name)
        bpy.context.object.location = object.location
        
        # Set the origin
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        # Move the object to the curve
        FocusObject(object.name)
        bpy.context.object.location = bpy.data.objects[stroke_curve_name].location
        
        # Now just re-apply the constraint!
        FocusObject(stroke_curve_name)
        bpy.ops.object.constraint_add(type='COPY_LOCATION')
        bpy.data.objects[stroke_curve_name].constraints["Copy Location"].target = object
        
        # Restore the original cursor location
        bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
        
                
    # Set to Curve End
    elif enum == 4:
        print("Setting to Last")
        
        # Enter the curve!
        stroke_curve_name = object.name.replace(".SKO", ".SKC")
        FocusObject(stroke_curve_name)
        curve_data = bpy.context.object.data
        
        # Only select the beginning curve point
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.select_all(action="DESELECT")
        bpy.ops.curve.de_select_last() 
        
        # Saves the current cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
        previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
        
        # Snap the cursor and set the origin!
        bpy.ops.view3D.snap_cursor_to_selected()
        bpy.ops.curve.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        # Temporarily remove the Copy Location Constraint
        FocusObject(stroke_curve_name)
        bpy.ops.object.constraints_clear()
        
        # Now give the curve the same location as the object
        FocusObject(stroke_curve_name)
        bpy.context.object.location = object.location
        
        # Set the origin
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        # Move the object to the curve
        FocusObject(object.name)
        bpy.context.object.location = bpy.data.objects[stroke_curve_name].location
        
        # Now just re-apply the constraint!
        FocusObject(stroke_curve_name)
        bpy.ops.object.constraint_add(type='COPY_LOCATION')
        bpy.data.objects[stroke_curve_name].constraints["Copy Location"].target = object
        
        # Restore the original cursor location
        bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
          
        
        
def ASKETCH_SetSceneOrigin(curve, enum, active_object_name, context):
        
    # Set to Active Object
    if enum == 1: 
        print("Changing origin to object")
        
        # Select the object by name and change the location
        if active_object_name is not "None":
            
            # Focus the curve
            FocusObject(curve.name)
            
            #Obtains the current cursor location and previous 3 cursor locations.
            cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
            previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
        
            bpy.data.scenes[bpy.context.scene.name].cursor_location = bpy.context.scene.objects[active_object_name].location
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            
            bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
            
        
    # Set to Cursor
    elif enum == 2:
        print("Changing origin to cursor")
        
        # Focus the curve
        FocusObject(curve.name)
        
        # Save the previous cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
        previous_cursor_loc = bpy.context.scene.cursor_location 
        
        # Set the origin
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        #FocusObject(stroke_curve_name)
        #dbpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        
        # Restore the original cursor location
        bpy.context.scene.cursor_location = previous_cursor_loc
        
        
    # Set to COM
    elif enum == 3:
        print("Changing origin to COM")
        
        # Focus the curve
        FocusObject(curve.name)
        curve_data = bpy.context.object.data
        
        # Select everything
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.select_all(action="SELECT")
        
        # Save the previous cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
        previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
        
        # Snap the cursor
        bpy.ops.view3D.snap_cursor_to_selected()
        bpy.ops.curve.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        # Set the origin
        bpy.ops.object.origin_set(type ='ORIGIN_CURSOR')
        
        # Restore the original cursor location
        bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
        
        
    # Set to Curve Start
    elif enum == 4:
        print("Changing origin to Start")
        
        # Focus the curve
        FocusObject(curve.name)
        curve_data = bpy.context.object.data
        
        # Only select the beginning curve point
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.select_all(action="DESELECT")
        bpy.ops.curve.de_select_first() 
        
        # Save the previous cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
        previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
        
        # Snap the cursor
        bpy.ops.view3D.snap_cursor_to_selected()
        bpy.ops.curve.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        # Set the origin
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        # Restore the original cursor location
        bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
        
    # Set to Curve End
    elif enum == 5:
        print("Changing origin to End")
        
        # Focus the curve
        FocusObject(curve.name)
        curve_data = bpy.context.object.data
        
        # Only select the beginning curve point
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.select_all(action="DESELECT")
        bpy.ops.curve.de_select_last() 
        
        # Save the previous cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
        previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
        
        # Snap the cursor and set the origin!
        bpy.ops.view3D.snap_cursor_to_selected()
        bpy.ops.curve.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        # Set the origin
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        # Restore the original cursor location
        bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
          

#//////////////////////////////// - DRAW STROKE - ////////////////////////////////

# Draw the Stroke
class ASKETCH_StrokeDraw(bpy.types.Operator):
    """Creates the stroke object using a grease stroke or selected curve, and provided brushes and cap settings"""
    bl_idname = "gpencil.asketch_stroke_draw"
    bl_label = "Array Sketch Stroke Draw"
    
    
# For some reason this doesn't work, just leave it out....
# //////////////////// - FIX ME SOMEHOW PLEASE - /////////////////////
    #stroke_size = bpy.props.FloatProperty(name="Stroke Size", description="Size of the stroke", default = stroke_size)
    #stroke_central_size = bpy.props.FloatProperty(name="Stroke Central Size", description="Size of the middle of the stroke", default = stroke_central_size)
    #dddstroke_elements_offset = bpy.props.FloatProperty(name="Stroke Elements Distance", description="Distance between elements of the stroke", default = stroke_elements_offset)
    
    
        
    #this just adds some string text to the current object name and then increases an index so that we can keep track of our strokes
    def append_stroke_number(self, partial_name):
        n = 1
        while True:
            name_stroke_obj = partial_name + ".SKO" + str(n)
            name_stroke_curve = partial_name + ".SKC" + str(n)
            
            if (not name_stroke_obj in bpy.data.objects and not name_stroke_curve in bpy.data.objects):
                break
            n += 1
        
        return name_stroke_curve
    
    
    
    #Class Method is used to activate the poll definition, which can be used to disable a functiom
    @classmethod
    def poll(cls, context):

        return context.scene.ASKETCH_brush_object != "None"
        
        #return context.active_object.name.find(".SKO") != -1 or context.active_object.name.find(".SKO") != -1:
        #return context.active_object is not None and context.active_object.mode == 'OBJECT' and context.active_object.type == 'MESH'
    
    
    # The main function body
    def execute(self, context):
        
        selection_count = len(bpy.context.selected_objects)
        use_curve = False
        print("-"*40)
        continue_process = True
        smooth_curve = True
        
        while continue_process:
            # If theres an active, unselected object, use the data in the scene and just select the object
            if selection_count == 0:
                
                print("DRAW STROKE: Found active object, creating curve")
                
                if bpy.context.gpencil_data is None:
                    self.report({'WARNING'}, 
                    'No grease pencil data found or curve selected.  Start drawing!')
                    continue_process = False
                    return {'FINISHED'}
                        
                bpy.ops.object.select_all(action='DESELECT')                # Deselect everything
                bpy.ops.gpencil.convert(type='CURVE')                       # Convert the active grease pencil to Curve
                bpy.ops.gpencil.active_frame_delete()                   # Clear GPencil Data
                
                continue_process = False
            
        
            # If there are both selected and active objects, use the active object to retrieve data
            elif selection_count >= 1:           
                        
                print("DRAW STROKE: Found selections and active object, creating curve")
        
                if bpy.context.active_object.type == 'CURVE':
                    stroke_obj_name = bpy.context.active_object.name
        
                    if (stroke_obj_name.find(".SKC") == -1):
                        print("Using a curve for the Stroke Object!")
                        print("Rawr?")
            
                        use_curve = True
                        smooth_curve = False
                        continue_process = False
                    
                    else:
                        self.report({'WARNING'}, 
                        'Array Sketch Selected.  Select a normal curve to begin')
                        return {'FINISHED'}
        
                elif bpy.context.gpencil_data is None:
                    self.report({'WARNING'}, 
                    'No grease pencil data found or curve selected.  Start drawing!')
                    continue_process = False
                    return {'FINISHED'}
                
                else:
                    # Grab the Gpencil data from the selected and active object
                    gpencil_target = bpy.context.gpencil_data 
            
                    bpy.ops.object.select_all(action='DESELECT')        # Deselect everything
                    bpy.context.scene.grease_pencil = gpencil_target    # Switch GPencil Data
                    bpy.ops.gpencil.convert(type='CURVE')     # Convert the active grease pencil
                    bpy.ops.gpencil.active_frame_delete()               # Clear GPencil Data
                    
                    continue_process = False

            else:
                self.report({'WARNING'}, "Something broke. :C")
                continue_process = False
                return {'FINISHED'}
        
        # The curve is now selected but not active.  Were gonna make it active!
        for obj in bpy.context.selected_objects:
            obj.name = "ASKETCH Curve"
            bpy.context.scene.objects.active = obj
            
        # Keep a location of the curve object
        curve_obj = bpy.context.object
        
        # Checking active object :3
        #print("-"*40)
        #print("Object Focus:")
        #print(bpy.context.object.name)
        #print("-"*40)
        
        ## Enter Edit Mode
        bpy.ops.object.editmode_toggle()
        
        ## Select all points in the curve and set the radius
        bpy.ops.curve.select_all(action="SELECT")
        
        # Set the radius of the curve
        bpy.ops.curve.radius_set(radius=1)
        
        curve_data = bpy.context.object.data                # Obtain curve data
        
        if (smooth_curve) :
            bpy.ops.curve.spline_type_set(type="BEZIER")
            bpy.ops.curve.handle_type_set(type="AUTOMATIC") # Change curve spline + handle types
        
        bpy.data.curves[curve_data.name].use_stretch = True
  
        #here i updated to to .show_handles and .show_normal_face
        # Hides the handles and other details that are unnecessary for this plugin
        bpy.data.curves[curve_data.name].show_handles = False
        bpy.data.curves[curve_data.name].show_normal_face = False
        bpy.data.curves[curve_data.name].use_path = True

        #I added .use_deform_bounds = True becuase it is false by default and that was causing me great trouble
        bpy.data.curves[curve_data.name].use_deform_bounds = True
        
        # smoothsmoothsmoothsmoothsmooth
        if (smooth_curve):
            print("Smoothing Curve")
            bpy.ops.curve.smooth()
            bpy.ops.curve.smooth()
            bpy.ops.curve.smooth()
            bpy.ops.curve.smooth()
            bpy.ops.curve.smooth()
            bpy.ops.curve.smooth()
        
        # Sets a location for the active object and object data
        stroke_curve_obj = bpy.context.active_object
        stroke_curve_data = bpy.context.active_object.data
        
        # Clear all animation keyframes generates from the GPencil conversion
        stroke_curve_data.animation_data_clear()
        
        stroke_curve_obj.name = self.append_stroke_number("ASKETCH Curve")
        
        
        #### Inflate stroke.
        ASKETCH_SetStrokeRadius(stroke_curve_data, self.stroke_size, self.stroke_central_size)
        
        bpy.ops.object.editmode_toggle()            #Exit Edit Modee
        
        
        ### Set curve's interpolation to "Cardinal"
        stroke_curve_obj.data.splines[0].radius_interpolation = "CARDINAL"
        
        
        #### Set Curve's origin to the position of the main object's origin.
        
        #Obtains the current cursor location and previous 3 cursor locations.
        #cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
        
        # This is extracting the float array of the current cursor locaion
        #previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
        
        # Select the object by name and change the location
        #if self.main_object is not None:
        #    bpy.ops.object.select_pattern(pattern=stroke_curve_obj.name)
        #    bpy.context.scene.objects.active = bpy.context.scene.objects[stroke_curve_obj.name]
            
        #    bpy.data.scenes[bpy.context.scene.name].cursor_location = self.main_object.location
        #   bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            
        #    bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
            
        #If no object is selected, place the origin point where the cursor is.
        #else:
        #    bpy.ops.object.select_pattern(pattern=stroke_curve_obj.name)
        #    bpy.context.scene.objects.active = bpy.context.scene.objects[stroke_curve_obj.name]
        #    
        #    bpy.data.scenes[bpy.context.scene.name].cursor_location = cursor_loc
        #    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        
        
        selected_origin = int(self.origin_point)
        
        print("-"*40)
        print(selected_origin)
        print("Active Object:")
        print(self.main_object)
        print("-"*40)
        
            
        # More origin changes here, or it will break :P
        if self.main_object is not None:
            if self.main_object.name.find(".SKO"):
                
                ASKETCH_SetSceneOrigin(stroke_curve_obj, selected_origin, "None", context)
                
            else:
                ASKETCH_SetSceneOrigin(stroke_cudrve_obj, selected_origin, self.main_object.name, context)
            
        else:
            ASKETCH_SetSceneOrigin(stroke_curve_obj, selected_origin, "None", context)
            
            
        #Now duplicate yoself.
        DuplicateObject(self.brush_object, stroke_curve_obj)
        
        stroke_brush_obj = bpy.context.active_object
        stroke_brush_obj.name = stroke_curve_obj.name.replace(".SKC", ".SKO", 2)    
        FocusObject(stroke_brush_obj.name)
        
            
        ### Add Array modifier to the brush-object and make it follow the curve
        if self.curve_object is False:
            print("Curve Object Not Active")
            bpy.ops.object.modifier_add(type='ARRAY')
            
            if self.connect_elements:
                print("Merge Elements Active")
                stroke_brush_obj.modifiers['Array'].use_merge_vertices = True
                stroke_brush_obj.modifiers['Array'].use_merge_vertices_cap = True
                stroke_brush_obj.modifiers['Array'].merge_threshold = 1.0
            
            
            # Modifies the Array attributes
            stroke_brush_obj.modifiers["Array"].relative_offset_displace = [self.stroke_elements_offset, 0, 0]
            stroke_brush_obj.modifiers["Array"].fit_type = "FIT_CURVE"
            stroke_brush_obj.modifiers["Array"].curve = stroke_curve_obj
            
            # If theres going to be a start
            
            # ?????????????????
            if bpy.context.scene.ASKETCH_start_cap != "None":
               stroke_brush_obj.modifiers["Array"].start_cap = bpy.data.objects[self.brush_start_cap]
            
            if bpy.context.scene.ASKETCH_end_cap != "None":
                stroke_brush_obj.modifiers["Array"].end_cap = bpy.data.objects[self.brush_end_cap]

        # Adds and modifies the Curve attributes
        FocusObject(stroke_brush_obj.name)
        
        bpy.ops.object.modifier_add(type='CURVE') 
        stroke_brush_obj.modifiers["Curve"].object = stroke_curve_obj
            
            
        #### Add Mirror modifier if activated
        if self.mirror_x_on is True:
            bpy.ops.object.modifier_add(type='MIRROR')
            
            #If an object is selected, mirror it through that
            if self.main_object is not None:
                stroke_brush_obj.modifiers["Mirror"].mirror_object = self.main_object
        
        
        # Make sure the curve is selected
        FocusObject(stroke_curve_obj.name)
        
        # Now lock the location
        bpy.ops.object.constraint_add(type='COPY_LOCATION')
        stroke_curve_obj.constraints["Copy Location"].target = stroke_brush_obj

        
        ## Lock movement of the stroke's object and curve.
        if self.lock_transform is True:
            bpy.data.objects[stroke_brush_obj.name].lock_location[0] = True
            bpy.data.objects[stroke_brush_obj.name].lock_location[1] = True
            bpy.data.objects[stroke_brush_obj.name].lock_location[2] = True
            
            bpy.data.objects[stroke_curve_obj.name].lock_location[0] = True
            bpy.data.objects[stroke_curve_obj.name].lock_location[1] = True
            bpy.data.objects[stroke_curve_obj.name].lock_location[2] = True
        
        
        ## Set main object as active.
        if self.main_object is not None:
            bpy.ops.object.select_pattern(pattern=self.main_object.name)
            bpy.context.scene.objects.active = self.main_object
            
        # Set the curve mesh as the selected and active object
        FocusObject(stroke_brush_obj.name)
        
        # Turn off auto-updating until the variables have been passed
        bpy.context.scene.ASKETCH_live_update = False
        
        # Now set the current custom variables to the new object
        stroke_brush_obj.ASKETCH_x_mirror_on = self.mirror_x_on
        stroke_brush_obj.ASKETCH_connect_elements = self.connect_elements
        stroke_brush_obj.ASKETCH_object_curve = self.curve_object
        stroke_brush_obj.ASKETCH_lock_transform = self.lock_transform
        
        stroke_brush_obj.ASKETCH_stroke_size = self.stroke_size
        stroke_brush_obj.ASKETCH_stroke_central_size = self.stroke_central_size
        stroke_brush_obj.ASKETCH_stroke_element_offset = self.stroke_elements_offset
        
        bpy.context.scene.ASKETCH_live_update = True
        
        if selected_origin is 1 or selected_origin is 2:
            stroke_brush_obj.ASKETCH_origin_point = "1"
            
        elif selected_origin is 3:
            stroke_brush_obj.ASKETCH_origin_point = "2"
            
        elif selected_origin is 4:
            stroke_brush_obj.ASKETCH_origin_point = "3"
            
        elif selected_origin is 5:
            stroke_brush_obj.ASKETCH_origin_point = "4"
            
        print(int(selected_origin))
        print(int(stroke_brush_obj.ASKETCH_origin_point))
            
        # Hide the curve to keep the appearance of geometry clean.
        # stroke_curve_obj.hide = True
        
        
    def invoke(self, context, event):
        
        self.main_object = bpy.context.object   
        
        ##-------------------------------------------------------------------------------------------
        # Checks with each object provided to see if it exists.  If it doesnt, it brings up a warning
        # and stops the code from commencing any further
        
        if bpy.data.objects.get(bpy.context.scene.ASKETCH_brush_object) is not None:
            self.brush_object = bpy.context.scene.objects[bpy.context.scene.ASKETCH_brush_object]

        else:
            self.report({'WARNING'}, 
            'Brush Object given does not exist, please use a name of an object that exists! :3')
            return {'FINISHED'}
        
        #print(bpy.context.scene.ASKETCH_start_cap)
        #print(self.main_object.name)
        
        if bpy.context.scene.ASKETCH_start_cap != "None":
            
            if bpy.data.objects.get(bpy.context.scene.ASKETCH_start_cap) is not None:
                self.brush_start_cap = bpy.context.scene.ASKETCH_start_cap
                
            else:
                self.report({'WARNING'}, 
                'Start Cap given does not exist, please use a name of an object that exists or use nothing at all! :3')
                return {'FINISHED'}
            
        if bpy.context.scene.ASKETCH_end_cap != "None":
            
            if bpy.data.objects.get(bpy.context.scene.ASKETCH_end_cap) is not None:
                self.brush_end_cap = bpy.context.scene.ASKETCH_end_cap
                
            else:
                self.report({'WARNING'}, 
                'End Cap given does not exist, please use a name of an object that exists or use nothing at all! :3')
                return {'FINISHED'}
            
        cheap_check = False     
        print("-"*40)
        
        if bpy.context.selected_objects is not None and bpy.context.active_object is not None:
            if bpy.context.object.name.find(".SKO") != -1 and context.scene.ASKETCH_live_update is True:
                print("Using object content")
                
                cheap_check = True
                self.mirror_x_on = bpy.context.object.ASKETCH_x_mirror_on
                self.connect_elements = bpy.context.object.ASKETCH_connect_elements
                self.curve_object = bpy.context.object.ASKETCH_object_curve
                self.lock_transform = bpy.context.object.ASKETCH_lock_transform
                
                self.stroke_size = bpy.context.object.ASKETCH_stroke_size
                self.stroke_central_size = bpy.context.object.ASKETCH_stroke_central_size
                self.stroke_elements_offset = bpy.context.object.ASKETCH_stroke_element_offset
                self.origin_point = bpy.context.object.ASKETCH_origin_point
        
        if cheap_check is not True:
            print("Using scene content")
            self.mirror_x_on = bpy.context.scene.SCENE_x_mirror_on
            self.connect_elements = bpy.context.scene.SCENE_connect_elements
            self.curve_object = bpy.context.scene.SCENE_object_curve
            self.lock_transform = bpy.context.scene.SCENE_lock_transform
        
            self.stroke_size = bpy.context.scene.SCENE_stroke_size
            self.stroke_central_size = bpy.context.scene.SCENE_stroke_central_size
            self.stroke_elements_offset = bpy.context.scene.SCENE_stroke_element_offset
            self.origin_point = bpy.context.scene.SCENE_origin_point
        
        self.execute(context)
        
        
        return {"FINISHED"}


# Enter "Stroke-Editmode"
class ASKETCH_Stroke_Editmode(bpy.types.Operator):
    """Enter the edit mode of the stroke object"""
    bl_idname = "object.asketch_stroke_editmode"
    bl_label = "Array Sketch Stroke Editmode"
    
    @classmethod
    def poll(cls, context):
        
        # Fail test is used to ensure that if any object selected is a Curve object, Edit Stroke cant be used.
        fail_test = True
        
        for obj in context.selected_objects:
            if obj.name.find(".SKO") == -1:
                fail_test = False
        
        return fail_test
    
    def execute(self, context):
        stroke_obj_name = bpy.context.object.name
        
        if (stroke_obj_name.find(".SKO") != -1):
            name_to_query = bpy.context.object.name.replace(".SKO", ".SKC")
            
            if bpy.context.scene.objects[name_to_query]:
                bpy.ops.object.select_pattern(pattern=name_to_query)
                bpy.context.scene.objects.active = bpy.context.scene.objects[name_to_query]
                bpy.ops.object.editmode_toggle()
                
        return {"FINISHED"}
                

#--------------- EXIT EDIT MODE -----------------------------------
class ASKETCH_Stroke_EditmodeExit(bpy.types.Operator):
    """Exit edit mode for the stroke object"""
    bl_idname = "object.asketch_stroke_editmode_exit"
    bl_label = "Array Sketch Stroke Exit Editmode"
    
    def execute(self, context):
        
        #Toggle out of edit mode
        bpy.ops.object.editmode_toggle()
        stroke_curve = bpy.context.object
        bpy.ops.object.select_all(action='DESELECT')

        #Find the .SKC equivalent
        stroke_object_name = stroke_curve.name.replace(".SKC", ".SKO")
        FocusObject(stroke_object_name)
        stroke = bpy.context.object
        
        #print(stroke_object_name)
            
        #If it's in the scene objects, select it.
        if bpy.context.scene.objects[stroke_object_name]:
                
                #FocusObject(stroke.name)
                
                print("-"*40)
                print("Am i really here? 0___0")
                print("-"*40)
                
                # If the cursor needs updating, grab the object and update it.
                if context.scene.SCENE_origin_update is True:
                    
                    #FocusObject(stroke.name)
                    enum = int(bpy.context.object.ASKETCH_origin_point)
                    print("Rawr")
                    
                    print("-"*40)
                    print("Going to object origin!")
                    print(int(stroke.ASKETCH_origin_point))
                    print(int(3.4))
                    print("-"*40)
                    
                    print("Going to UpdateObjectOrigin")
                    ASKETCH_SetObjectOrigin(stroke, enum, context)
                    
                    bpy.ops.object.select_all(action='DESELECT') 
        
        #splitted_name = bpy.context.object.name.split(".SKC")
        #main_object_name = splitted_name[0]
        #main_object_name = bpy.context.object.parent.name
        
        #if bpy.context.scene.objects[main_object_name]:
        #    bpy.ops.object.select_pattern(pattern=main_object_name)
        #    bpy.context.scene.objects.active = bpy.context.scene.objects[main_object_name]
    
    
    def invoke (self, context, event):
        self.execute(context)
        
        return {"FINISHED"}


#--------------- TOGGLE EDIT MODE -----------------------------------
class ASKETCH_Stroke_EditmodeToggle(bpy.types.Operator):
    bl_idname = "gpencil.asketch_stroke_editmode_toggle"
    bl_label = "Array Sketch Stroke Editmode Toggle"
    
    
    def execute(self, context):
        if self.stroke_obj.name.find(".SKO") != -1:
            deformer_curve_name = self.stroke_obj.name.replace(".SKO", ".SKC")
            
            if deformer_curve_name in bpy.data.objects:
                curve = bpy.data.objects[deformer_curve_name]
                #curve.data.restrict_view = False
                
                # Not sure if this will work
                FocusObject(deformer_curve_name)
                
                #bpy.ops.object.select_pattern(pattern=deformer_curve_name)
                #bpy.context.scene.objects.active = bpy.context.scene.objects[deformer_curve_name]
                
                bpy.ops.object.editmode_toggle()
                
        elif self.stroke_obj.name.find(".SKC") != -1:
            if bpy.context.edit_object == self.stroke_obj:
                bpy.ops.object.editmode_toggle()
            
            #bpy.data.objects[self.stroke_obj.name].restrict_view = True
            
            #splitted_name = bpy.context.object.name.split(".SKC")
            #main_object_name = splitted_name[0]
            main_object_name = bpy.context.object.parent.name
            
            if main_object_name in bpy.data.objects:
                
                #Also not sure if this will work
                FocusObject(main_object_name)
                
                #bpy.ops.object.select_pattern(pattern=main_object_name)
                #bpy.context.scene.objects.active = bpy.context.scene.objects[main_object_name]
            
    
    def invoke (self, context, event):
        self.stroke_obj = bpy.context.object
        self.execute(context)
        
        return {"FINISHED"}
        

#--------------- SET BRUSH OBJECT -----------------------------------
class ASKETCH_SetBrushObject(bpy.types.Operator):
    """Sets the brush object to the active object in the 3D View.  Stroke objects cannot be used."""
    bl_idname = "object.asketch_set_brush_object"
    bl_label = "Array Sketch Set Brush Object"
    
    def execute(self, context):
        bpy.context.scene.ASKETCH_brush_object = bpy.context.active_object.name
        
        
    def invoke (self, context, event):
        self.execute(context)
        
        return {"FINISHED"}
    
#--------------- SET START CAP -----------------------------------
class ASKETCH_SetStartCap(bpy.types.Operator):
    """Sets the object that marks the beginning of the curve using the active object in the 3D View.  Deleting the original object will also remove the cap from the stroke until converted."""
    bl_idname = "object.asketch_set_start_cap"
    bl_label = "Array Sketch Set Start Cap"
    
    def execute(self, context):
        bpy.context.scene.ASKETCH_start_cap = bpy.context.active_object.name
        
        
    def invoke (self, context, event):
        self.execute(context)
        
        return {"FINISHED"}
    
    
#--------------- SET END CAP -----------------------------------
class ASKETCH_SetEndCap(bpy.types.Operator):
    """Sets the object that marks the end of the curve using the active object in the 3D View.  Deleting the original object will also remove the cap from the stroke until converted."""
    bl_idname = "object.asketch_set_end_cap"
    bl_label = "Array Sketch Set End Cap"
    
    def execute(self, context):
        bpy.context.scene.ASKETCH_end_cap = bpy.context.active_object.name
        
        
    def invoke (self, context, event):
        self.execute(context)
        
        return {"FINISHED"}
    
    
#--------------- CLEAR BRUSH OBJECT -----------------------------------
class ASKETCH_ClearBrushObject(bpy.types.Operator):
    """Clears the currently chosen object"""
    bl_idname = "object.asketch_clear_brush_object"
    bl_label = "Array Sketch Set Brush Object"
    
    def execute(self, context):
        bpy.context.scene.ASKETCH_brush_object = "None"
        
        
    def invoke (self, context, event):
        self.execute(context)
        
        return {"FINISHED"}
    
    
#--------------- CLEAR START CAP -----------------------------------
class ASKETCH_ClearStartCap(bpy.types.Operator):
    """Clears the currently chosen object"""
    bl_idname = "object.asketch_clear_start_cap"
    bl_label = "Array Sketch Set Start Cap"
    
    def execute(self, context):
        bpy.context.scene.ASKETCH_start_cap = "None"
        
        
    def invoke (self, context, event):
        self.execute(context)
        
        return {"FINISHED"}
    
    
#--------------- CLEAR END CAP -----------------------------------
class ASKETCH_ClearEndCap(bpy.types.Operator):
    """Clears the currently chosen object"""
    bl_idname = "object.asketch_clear_end_cap"
    bl_label = "Array Sketch Set End Cap"
    
    def execute(self, context):
        bpy.context.scene.ASKETCH_end_cap = "None"
        
        
    def invoke (self, context, event):
        self.execute(context)
        
        return {"FINISHED"}



#--------------- DELETE SELECTED STROKES-----------------------------------
# Delete selected strokes (or last grease pencil stroke)
class ASKETCH_DeleteStrokes(bpy.types.Operator):
    """Deletes the selected strokes."""
    bl_idname = "object.asketch_delete_strokes"
    bl_label = "Array Sketch Delete Strokes"
    
    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            return obj.name.find(".SKO") != -1 or obj.name.find(".SKO") != -1
    
    def object_type(self, obj):
        if (obj.name.find(".SKO") != -1):
            obj_type = "stroke_object"
        elif (obj.name.find(".SKC") != -1):
            obj_type = "stroke_curve"
        else:
            obj_type = "main_object"
        
        return obj_type
    
    
    def delete_stroke(self, stroke_object):
        #if (stroke_object.grease_pencil):
        #    if (stroke_object.grease_pencil.layers[0]):
        #        gp_layers = stroke_object.grease_pencil.layers
        #        l = None
        #        for l in gp_layers:
        #            if l.active:
        #                break
        #        
        #        if (l.active_frame):
        #            if (len(l.active_frame.strokes) > 0):
        #                bpy.ops.gpencil.active_frame_delete()
                    
        
        if (self.object_type(stroke_object) == "stroke_object"):
            stroke_object_name = stroke_object.name
            stroke_curve_name = stroke_object_name.replace(".SKO", ".SKC")
            
            bpy.ops.object.select_pattern(pattern=stroke_curve_name)
            bpy.ops.object.select_pattern(pattern=stroke_object_name, extend=True)
            bpy.context.scene.objects.active = bpy.data.objects[stroke_object_name]
            bpy.ops.object.delete()
            
    
    def execute(self, context):
        #if (bpy.context.object.parent != None):
        #    main_object_name = bpy.context.object.parent.name
        
        # Get selected objects
        strokes_to_delete = []
        print("Selected Objects:")
        print(len(bpy.context.selected_objects))
        
        for stroke in bpy.context.selected_objects:
            if stroke.name.find(".SKO") != -1:
                strokes_to_delete.append(stroke)
        
        print("Objects in Delete Queue:")
        print(len(strokes_to_delete))
        
        for stroke in strokes_to_delete:
            print("Deleting Stroke:")
            print(stroke.name)
            
            FocusObject(stroke.name)
            
            self.delete_stroke(stroke)
        
        # Theres a potential bug here, keep an eye out.
        splitted_name = strokes_to_delete[0].name.split(".SKO")
        main_object_name = splitted_name[0]
        
        if main_object_name in bpy.data.objects:
            bpy.ops.object.select_pattern(pattern=main_object_name)
            bpy.context.scene.objects.active = bpy.data.objects[main_object_name]
        
        return {"FINISHED"}
        



#--------------- SMOOTH CURVE RADIUS-----------------------------------
# Smooth Curve Radius using control points
class ASKETCH_StrokeSmoothSize(bpy.types.Operator):
    bl_idname = "object.asketch_stroke_smooth_size"
    bl_label = "Array Sketch Smooth Stroke Size"
    
    
    def execute(self, context):
        if(context.active_object.type == 'CURVE' and context.mode == 'EDIT_CURVE'):
            bpy.ops.curve.select_all(action="INVERT")
            bpy.ops.curve.smooth_radius()
            bpy.ops.curve.select_all(action="INVERT")

        
    def invoke (self, context, event):
        self.execute(context)
        
        return {"FINISHED"}
    
    
#--------------- Strokes to Meshes-----------------------------------
# Convert strokes to meshes.
class ASKETCH_StrokesToMeshes(bpy.types.Operator):
    """Converts the stroke object to a mesh"""
    bl_idname = "object.asketch_strokes_to_meshes"
    bl_label = "Array Sketch Stroke To Meshes"
    
    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            return obj.name.find(".SKO") != -1 or obj.name.find(".SKO") != -1
    
    
    def execute(self, context):
        
        scene = bpy.context.scene

        # Get selected objects
        strokes_to_convert = []
        print("Selected Objects:")
        print(len(bpy.context.selected_objects))
        
        for stroke in bpy.context.selected_objects:
            if stroke.name.find(".SKO") != -1:
                strokes_to_convert.append(stroke)
        
        print("Objects in Convert Queue:")
        print(len(strokes_to_convert))
        
        for stroke in strokes_to_convert:
            print("Converting Stroke:")
            print(stroke.name)
            
            #Just select the curve now
            FocusObject(stroke.name)
            
            mod_types = {'ARRAY', 'CURVE', 'MIRROR'}
            mod_active = [mod.show_viewport for mod in stroke.modifiers]
            
            # THANKS BLENDER ARTISTS USER CoDEmannX for this code!
            for mod in stroke.modifiers:
                if mod.type not in mod_types:
                    mod.show_viewport = False
            
            me = stroke.to_mesh(scene, True, 'PREVIEW')
            
            for mod, active in zip(stroke.modifiers, mod_active):
                if mod.type in mod_types:
                   stroke.modifiers.remove(mod)
                else:
                    mod.show_viewport = active
        
            # Note: this only swaps the object's data, but doesn't remove the original mesh
            stroke.data = me
            
            # Now find and delete the corresponding curve
            stroke_curve_name = stroke.name.replace(".SKO", ".SKC")
            FocusObject(stroke_curve_name)
            bpy.ops.object.delete()
                
            # Rename the curve to remove it from being considered an Object Sketch
            FocusObject(stroke.name)
            stroke.name = "ASKETCH Object"
            
        
        
        return {"FINISHED"}
    

#--------------- CONVERT STEP 1-----------------------------------
# Convert strokes to metaballs.
class ASKETCH_StrokesToMetaballs(bpy.types.Operator):
    """Converts all currently selected strokes to a combined mesh, using metaballs.  PLEASE NOTE - Press each step button in succession to fully convert the object.  This may take a few minutes to complete."""
    bl_idname = "object.asketch_strokes_to_metaballs"
    bl_label = "Array Sketch Stroke To Metaballs"
    
    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            return obj.name.find(".SKO") != -1 or obj.name.find(".SKO") != -1
    
    def create_metaball(self, point, mball_radius, mball_name):
        
            #Add the ball type metaball
            bpy.ops.object.metaball_add(type='BALL', view_align=False, enter_editmode=False, location=(point.co), rotation=(0, 0, 0))
            mball_object = bpy.context.object
            mball_object.name = mball_name
            
            #bpy.data.objects[mball_object.name].parent = self.main_object
            bpy.data.objects[mball_object.name].location += self.main_object.location
            
            mball = bpy.data.metaballs[mball_object.data.name]
            mball.resolution = 1
            mball.elements[0].radius = mball_radius * 2
            mball.elements[0].stiffness = self.mballs_stiffness
            return mball_object
    
    def execute(self, context):
        #### Be sure that all strokes and their curves are visible
        for obj in bpy.data.objects:
            if (obj.name.find(self.main_object.name + ".SKO") != -1 or obj.name.find(self.main_object.name + ".SKC") != -1):
                bpy.data.objects[obj.name].hide = False
        
        
        #### If there was a baked mesh, delete it.
        baked_mesh_name = self.main_object.name + ".SKME"
        
        if baked_mesh_name in bpy.data.objects:
            bpy.data.objects[baked_mesh_name].hide = False
            
            bpy.ops.object.select_pattern(pattern=baked_mesh_name)
            bpy.context.scene.objects.active = bpy.data.objects[baked_mesh_name]
            
            bpy.ops.object.delete()
            
            bpy.ops.object.select_pattern(pattern=self.main_object.name)
            bpy.context.scene.objects.active = bpy.data.objects[self.main_object.name]
        
        
        bpy.ops.object.select_pattern(pattern=self.main_object.name)
        bpy.context.scene.objects.active = self.main_object
        
        
        #### Get all curves that will be converted to metaballs, and duplicate and mirror the ones that should be mirrored.
        all_strokes_curves = []
        for obj in bpy.data.objects:
            if obj.name.find(".SKC") != -1:
                mirrored_curve = False
                stroke_brush_name = obj.name.replace(".SKC", ".SKO")
                for mod in bpy.data.objects[stroke_brush_name].modifiers:
                    if mod.type == "MIRROR" and mod.use_x == True:
                        mirrored_curve = True
                                    
                bpy.ops.object.select_pattern(pattern=obj.name)
                bpy.context.scene.objects.active = bpy.data.objects[obj.name]
                
                bpy.ops.object.duplicate_move()
                bpy.ops.object.editmode_toggle()
                bpy.ops.curve.select_all(action='SELECT')
                bpy.ops.curve.subdivide()
                bpy.ops.curve.subdivide()
                bpy.ops.object.editmode_toggle()
                
                bpy.context.object.name = "A_SK_TEMP_CURVE"
                
                # Append the first duplicate.
                all_strokes_curves.append(bpy.context.object)
                
                if mirrored_curve:
                    bpy.ops.object.duplicate_move()
                    bpy.ops.transform.mirror(proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, constraint_axis=(True, False, False), constraint_orientation='GLOBAL')
                    bpy.ops.object.transform_apply(scale=True)
                    
                    bpy.context.object.name = "A_SK_TEMP_CURVE"
                    
                    # Append the mirrored duplicate
                    all_strokes_curves.append(bpy.context.object)
                
        #### Create the Metaball object for each curve and set its properties.
        strokes_total_time = 0
        curves_count = 1
        mballs_num = 1
        all_mballs = []
        for curve_obj in all_strokes_curves:
            bpy.ops.object.select_pattern(pattern = curve_obj.name)
            bpy.context.scene.objects.active = bpy.data.objects[curve_obj.name]
            
            pts = bpy.data.objects[curve_obj.name].data.splines[0].bezier_points
            
            
            mballs_count = 0
            mballs_start_time = time.time()
            first_pt = True
            for p in pts:
                # Radius of the metaball not less than the minimum wire resolution
                if p.radius < self.stroke_wire_resolution:
                    mball_radius = self.ball_brush_size / 2 * self.mballs_size_compensation * self.stroke_wire_resolution*2
                else:
                    mball_radius = self.ball_brush_size / 2 * self.mballs_size_compensation * p.radius*2
                
                
                new_mball_created = False
                if first_pt:
                    mball_object = self.create_metaball(p, mball_radius, self.final_mesh_name + str(mballs_num))
                    
                    new_mball_created = True
                    
                    first_pt = False
                else:
                    prev_mball = bpy.data.metaballs[prev_mball_object.data.name]
                    prev_pt_loc = prev_pt.co
                    
                    pts_difs = [prev_pt_loc[0] - p.co[0], prev_pt_loc[1] - p.co[1], prev_pt_loc[2] - p.co[2]]
                    pts_distance = abs(sqrt(pts_difs[0] * pts_difs[0] + pts_difs[1] * pts_difs[1] + pts_difs[2] * pts_difs[2]))
                    
                    # Checks if the distance between the previous point with a metaball and the actual point is long enough to "deserve" a new metaball.
                    if ((prev_mball.elements[0].radius * self.ball_brush_size + mball_radius) / self.stroke_definition < pts_distance + mball_radius / 10):
                        mball_object = self.create_metaball(p, mball_radius,  self.final_mesh_name + str(mballs_num))
                        new_mball_created = True
                        
                        
                if new_mball_created:
                    #mball_object.data.threshold = 0
                    mball_object.data.elements[0].hide = True
                    
                    all_mballs.append(mball_object)
                    
                    prev_mball_object = mball_object
                    prev_pt = p
                    
                    mballs_num += 1
                    mballs_count += 1
            
            
            stroke_time = time.time() - mballs_start_time
            strokes_total_time += stroke_time
            print("DONE " + str(curves_count) + " strokes of " + str(len(all_strokes_curves)))
            #print("Metaballs: " + str(mballs_count) + "  Time: " + str(time.time() - mballs_start_time) + "Points: " + str(len(pts)))
            print(".............................................. total time: " + str(int(strokes_total_time)) + " seconds")
            print("")
            
            curves_count += 1       
        
        
        bpy.ops.object.select_pattern(pattern= self.main_object.name)
        bpy.context.scene.objects.active = self.main_object
    
    def invoke (self, context, event):
        self.main_object = bpy.context.object
        self.ball_brush_size = 1
        self.mballs_stiffness = 2
        self.mballs_size_compensation = 0.9
        self.stroke_definition = bpy.context.object.ASKETCH_mball_stroke_definition
        self.stroke_wire_resolution = bpy.context.object.ASKETCH_mball_wire_resolution
        
        self.final_mesh_name = self.main_object.name + ".SKMB"
        
        self.x_mirror_on = bpy.context.scene.ASKETCH_x_mirror_on
        
        self.execute(context)
        
        return {"FINISHED"}


#--------------- CONVERT STEP 2-----------------------------------
# Metaballs rename
class ASKETCH_MetaballsRename(bpy.types.Operator):
    """Converts all currently selected strokes to a combined mesh, using metaballs.  PLEASE NOTE - Press each step button in succession to fully convert the object.  This may take a few minutes to complete."""
    bl_idname = "object.asketch_metaballs_rename"
    bl_label = "Array Sketch Metaballs Rename"
    
    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            return obj.name.find(".SKO") != -1 or obj.name.find(".SKO") != -1

    
    def execute(self, context):
        renamed_mballs_count = 1
        for mb in self.metaballs_objects:
            mb.data.elements[0].hide = False
            mb.name = self.final_mesh_name
            
        print("Meshing metaballs...")
        bpy.data.objects[self.final_mesh_name].data.resolution = self.stroke_wire_resolution
        bpy.data.objects[self.final_mesh_name].data.threshold = 0.6
        
        
        bpy.ops.object.select_pattern(pattern= self.main_object.name)
        bpy.context.scene.objects.active = self.main_object
        
    
    def invoke (self, context, event):
        self.main_object = bpy.context.object
        self.stroke_wire_resolution = bpy.context.object.ASKETCH_mball_wire_resolution
        self.final_mesh_name = self.main_object.name + ".SKMB"
        
        self.metaballs_objects = []
        
        for ob in bpy.data.objects:
            if ob.name.find(self.final_mesh_name) != -1:
                self.metaballs_objects.append(ob)
            
        self.execute(context)
        
        return {"FINISHED"}
            
            
#--------------- CONVERT STEP 3-----------------------------------
# Convert metaballs to mesh.
class ASKETCH_MetaballsToMesh(bpy.types.Operator):
    """Converts all currently selected strokes to a combined mesh, using metaballs.  PLEASE NOTE - Press each step button in succession to fully convert the object.  This may take a few minutes to complete."""
    bl_idname = "object.asketch_metaballs_to_mesh"
    bl_label = "Array Sketch Metaballs To Mesh"
    
    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            return obj.name.find(".SKO") != -1 or obj.name.find(".SKO") != -1
    
    def execute(self, context):
        if not self.starting_from_fixed_mesh:
            print("STAGE 1 of 4: Converting to Mesh...")
            start_time = time.time()
            bpy.ops.object.select_pattern(pattern= self.metaballs_object.name)
            bpy.context.scene.objects.active = self.metaballs_object
            
            bpy.ops.object.convert(target='MESH', keep_original = False)
            print("DONE... Time: " + str(time.time() - start_time) + " seconds")
            print("Preparing next stage...")
            print("")
            
                
            mesh_object = bpy.context.selected_objects[0]
            bpy.context.scene.objects.active = mesh_object
            
            
            #### Setting mesh's origin.
            cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
            previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
            
            bpy.ops.object.select_pattern(pattern= mesh_object.name)
            bpy.context.scene.objects.active = bpy.context.scene.objects[mesh_object.name]
            
            bpy.data.scenes[bpy.context.scene.name].cursor_location = self.main_object.location
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            
            bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
            
            
            #### Make it child of the main object
            mesh_object.name = self.main_object.name + ".SKMTMP"
            mesh_object.parent = self.main_object
            mesh_object.location = [0, 0, 0]
            
            
            #### Delete metaballs
            for obj in bpy.data.objects:
                if obj.name.find(self.main_object.name + ".SKMB") != -1:
                    bpy.ops.object.select_pattern(pattern= obj.name)
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.delete()
            
            #### Delete all temporal curves.
            for obj in bpy.data.objects:
                if obj.name.find("A_SK_TEMP_CURVE") != -1:
                    bpy.ops.object.select_pattern(pattern= obj.name)
                    bpy.context.scene.objects.active = bpy.data.objects[obj.name]
                    bpy.ops.object.delete()
        else:
            mesh_object = bpy.data.objects[self.temp_mesh.name]
            print("STAGE 1 of 4: Converting to Mesh...")
            print("Already converted. Preparing next stage...")
            print("")
        
        
        #### Cleaning mesh result.
        ####################################
        FocusObject(mesh_object.name)
        #bpy.ops.object.select_pattern(pattern = mesh_object.name)
        #bpy.context.scene.objects.active = mesh_object
        
        #### Check if the mesh has non-manifold areas.
        #ISSUE LINE HEAR!
        print("--------------------------Current Object----------------------")
        print(self)
        print(dir(self))
        
        print("--------------------------Current Context----------------------")
        print(context)
        print(dir(context))
        
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_non_manifold()
        bpy.ops.object.editmode_toggle()
        
        is_non_manifold = False
        for v in bpy.data.objects[mesh_object.name].data.vertices:
            if v.select:
                is_non_manifold = True
                break
        
        
        #### If the resulting mesh is non-manifold do the mesh optimizations.
        if not is_non_manifold:
            #### To keep temporarily a copy of the non-decimated mesh.
            non_decimated_object = bpy.context.object
            bpy.ops.object.duplicate_move()
            
            
            # Decimate.
            print("STAGE 2 of 4: Decimating...")
            start_time = time.time()
            bpy.ops.object.modifier_add(type='DECIMATE')
            bpy.context.object.modifiers["Decimate"].ratio = 0.02
            bpy.ops.object.convert(target='MESH', keep_original = False)
            print("STAGE DONE... Time: " + str(time.time() - start_time) + " seconds")
            print("Preparing next stage...")
            print("")
            
            # Tris to Quads.
            print("STAGE 3 of 4: Making all Quads...")
            start_time = time.time()
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.tris_convert_to_quads()
            bpy.ops.mesh.tris_convert_to_quads()
            bpy.ops.object.editmode_toggle()
            
            # One level of Subdivision.
            bpy.ops.object.modifier_add(type='SUBSURF')
            bpy.context.object.modifiers["Subsurf"].levels = 1
            bpy.ops.object.convert(target='MESH', keep_original = False)
            print("DONE... Time: " + str(time.time() - start_time) + " seconds")
            print("Preparing next stage...")
            print("")
            
            # Smooth shading for faces
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.faces_shade_smooth()
            bpy.ops.object.editmode_toggle()
            
            # Shrinkwrap and smooth results to the non-decimated mesh.
            print("STAGE 4 of 4: Fitting...")
            start_time = time.time()
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.context.object.modifiers["Shrinkwrap"].wrap_method = "PROJECT"
            bpy.context.object.modifiers["Shrinkwrap"].use_negative_direction = True
            bpy.context.object.modifiers["Shrinkwrap"].use_positive_direction = True
            bpy.context.object.modifiers["Shrinkwrap"].cull_face = 'FRONT' 
                        
            bpy.context.object.modifiers["Shrinkwrap"].target = non_decimated_object
            bpy.ops.object.convert(target='MESH', keep_original = False)
            print("DONE... Time: " + str(time.time() - start_time) + " seconds")
            print("")
            
            # Add Multires
            bpy.ops.object.modifier_add(type='MULTIRES')
            bpy.context.object.modifiers["Multires"].show_only_control_edges = True
            
            
            #### Name the resulting mesh.
            bpy.context.object.name = self.main_object.name + ".SKME"
            
            
            #### Apply the material of the main object to the new mesh
            if len(bpy.data.objects[self.main_object.name].material_slots) > 0:
                bpy.ops.object.material_slot_add()
                bpy.data.objects[bpy.context.object.name].material_slots[0].material = bpy.data.objects[self.main_object.name].materials[0].material
            
            
            #### Delete non-decimated mesh
            bpy.ops.object.select_pattern(pattern= non_decimated_object.name)
            bpy.context.scene.objects.active = non_decimated_object
            bpy.ops.object.delete()
        else:
            print("WARNING: There are non-manifold areas in the resulting mesh")
            print("(To solve this fix the non-manifold areas (now selected) and then press STEP 3 again")
        
        
        #### Select main object.
        bpy.ops.object.select_pattern(pattern= self.main_object.name)
        bpy.context.scene.objects.active = self.main_object
        
        
        #### Hide all strokes
        for obj in bpy.data.objects:
            if obj.name.find(self.main_object.name + ".SKO") != -1 or obj.name.find(self.main_object.name + ".SKC") != -1:
                bpy.data.objects[obj.name].hide = True
        
        
        
    def invoke (self, context, event):
        #### Check if the resulting mesh with non-manifold areas is selected, to change selection to main object.
        if bpy.context.object.name.find(".SKMTMP") != -1:
            self.main_object = bpy.context.object.parent
            self.final_mesh_name = self.main_object.name + ".SKMB"
            
            bpy.ops.object.select_pattern(pattern= self.main_object.name)
            bpy.context.scene.objects.active = self.main_object
        else:
            self.main_object = bpy.context.object
            self.final_mesh_name = self.main_object.name + ".SKMB"
        
        #### Check if there is a Metaballs object
        if self.main_object.name + ".SKMB" in bpy.data.objects:
            self.metaballs_object = bpy.data.objects[self.main_object.name + ".SKMB"]
            
        
        #### Check if there is a previous (not decimated) mesh.
        self.starting_from_fixed_mesh = False
        if self.main_object.name + ".SKMTMP" in bpy.data.objects:
            self.starting_from_fixed_mesh = True
            self.temp_mesh = bpy.data.objects[self.main_object.name + ".SKMTMP"]
            
        
        self.execute(context)
        
        return {"FINISHED"}


#---------------TOGGLE STROKES/BAKED MESH-----------------------------------
# Toggle visibility between Strokes and "baked" Mesh object.
class ASKETCH_ToggleMeshVisibility(bpy.types.Operator):
    bl_idname = "object.asketch_toggle_mesh_visibility"
    bl_label = "Array Sketch Smooth Stroke Size"
    
    
    def execute(self, context):
        mesh_obj_name = self.main_object.name + ".SKME"
        
        if mesh_obj_name in bpy.data.objects:
            if (bpy.data.objects[mesh_obj_name].hide == True):
                bpy.data.objects[mesh_obj_name].hide = False
                
                for obj in bpy.data.objects:
                    if (obj.name.find(self.main_object.name + ".SKO") != -1 or obj.name.find(self.main_object.name + ".SKC") != -1):
                        bpy.data.objects[obj.name].hide = True
            else:
                bpy.data.objects[mesh_obj_name].hide = True
                
                for obj in bpy.data.objects:
                    if (obj.name.find(self.main_object.name + ".SKO") != -1 or obj.name.find(self.main_object.name + ".SKC") != -1):
                        bpy.data.objects[obj.name].hide = False
        else:
            for obj in bpy.data.objects:
                if (obj.name.find(self.main_object.name + ".SKO") != -1 or obj.name.find(self.main_object.name + ".SKC") != -1):
                    bpy.data.objects[obj.name].hide = False
            
            bpy.ops.object.select_pattern(pattern= self.main_object.name)
            bpy.context.scene.objects.active = self.main_object
            
        
    def invoke (self, context, event):
        if bpy.context.object.name.find(".SKME") != -1:
            self.main_object = bpy.data.objects[bpy.context.object.name.split(".SKME")[0]]
            
            bpy.ops.object.select_pattern(pattern= self.main_object.name)
            bpy.context.scene.objects.active = self.main_object
        else:
            self.main_object = bpy.context.object
            
        self.execute(context)
        
        return {"FINISHED"}
    
    


#//////////////////////// - REGISTER/UNREGISTER DEFINITIONS - ////////////////////////

def register():
    bpy.utils.register_module(__name__) 

    #kc = bpy.context.window_manager.keyconfigs.addon
    #km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
    #keymap_item_stroke_draw = km.keymap_items.new("gpencil.asketch_stroke_draw","G","PRESS", key_modifier="D")
    #keymap_item_delete_strokes = km.keymap_items.new("object.asketch_delete_strokes","F","PRESS")
    #keymap_item_stroke_smooth_size = km.keymap_items.new("object.asketch_stroke_smooth_size","Y","PRESS")
    #keymap_item_stroke_editmode = km.keymap_items.new("gpencil.asketch_stroke_editmode_toggle","TAB","PRESS", key_modifier="D")
    

def unregister():
    bpy.utils.unregister_module(__name__) 
    
    #kc = bpy.context.window_manager.keyconfigs.addon
    #km = kc.keymaps["3D View"]
    #for kmi in km.keymap_items:
    #    if kmi.idname == 'wm.call_menu':
    #        if kmi.properties.name == "GPENCIL_OT_ASKETCH_stroke_draw":
    #            km.keymap_items.remove(kmi)
    #            print('a')
    #        elif kmi.properties.name == "OBJECT_OT_ASKETCH_delete_strokes":
    #            km.keymap_items.remove(kmi)
    #            print('a')
    #        elif kmi.properties.name == "OBJECT_OT_ASKETCH_stroke_smooth_size":
    #            km.keymap_items.remove(kmi)
    #            print('a')
    #        elif kmi.properties.name == "OBJECT_OT_ASKETCH_stroke_editmode":
    #            km.keymap_items.remove(kmi)
    #            print('a')
    #       else:
    #            continue
            
            
            
#//////////////////////////////// - SPACEBAR SEARCH- ////////////////////////////////

if __name__ == "__main__":
    register()

