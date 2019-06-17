import bpy
from bpy.props import (StringProperty, 
                       BoolProperty, 
                       FloatVectorProperty,
                       FloatProperty,
                       EnumProperty,
                       IntProperty)

from .primitives import (UpdateMetaballs,
                        ClippingMerge)

from .remesh_decimate import HideRemeshSmooth

from .lattice import (HideLattice, 
                      LatticeInterpolation)

import os


##------------------------------------------------------  
#
# Funtions
#
##------------------------------------------------------  

def get_addon_preferences():
    addon_name = os.path.basename(os.path.dirname(os.path.abspath(__file__).split("utils")[0]))
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[addon_name].preferences 
    
    return addon_prefs
#------------------------------------------------------------------------------------------
# Object ref mirror
#------------------------------------------------------------------------------------------
bpy.types.WindowManager.ref_obj = bpy.props.StringProperty()

#------------------------------------------------------------------------------------------
# Options 
#------------------------------------------------------------------------------------------

            
bpy.types.WindowManager.detail_size = bpy.props.FloatProperty(min = 0.01, max = 300, default = 20)


#------------------------------------------------------------------------------------------
# Extract Mask
#------------------------------------------------------------------------------------------
bpy.types.WindowManager.extract_cut_delete = EnumProperty(
        items=(('extract', "Extract", "Extract"),
               ('cut', "Cut", "Cut"),
               ('duplicate', "Duplicate", "Duplicate"),
               ('remove', "Remove", "Remove")),
               default='extract'
               )

               
bpy.types.WindowManager.add_solidify = BoolProperty(
    name="Add Solidify",
    description="Add Solidify to the extracted object",
    default=True)

bpy.types.WindowManager.comeback_in_sculpt_mode = BoolProperty(
    name="Comme Back in Sculpt mode",
    description="Comme Back in Sculpt mode",
    default=True)
    
bpy.types.WindowManager.apply_solidify = BoolProperty(
        default=True,
        description="Apply Solidify"
        )    

bpy.types.WindowManager.update_dyntopo = BoolProperty(
        default=True,
        description="Update Dyntopo"
        ) 
                
bpy.types.WindowManager.rim_only = BoolProperty(
    name="Rim Only",
    description="Rim Only",
    default=False) 
    
bpy.types.WindowManager.solidify_thickness = bpy.props.FloatProperty(min = 0.01, max = 300, default = 0.1)

bpy.types.WindowManager.solidify_offset = bpy.props.FloatProperty(min = -1, max = 1, default = 0)


#------------------------------------------------------------------------------------------
# GP Lines
#------------------------------------------------------------------------------------------
bpy.types.WindowManager.gp_solidify_thickness = bpy.props.FloatProperty(min = 0.01, max = 300, default = 0.1)

bpy.types.WindowManager.gp_solidify_offset = bpy.props.FloatProperty(min = -1, max = 1, default = 0.5)

bpy.types.WindowManager.use_clipping = BoolProperty(
        default=False,
        description="Use Clipping/Merger for the mirror modifier",
        update = ClippingMerge
        ) 
  
#------------------------------------------------------------------------------------------
# Quick Pose
#------------------------------------------------------------------------------------------
bpy.types.WindowManager.use_mask = BoolProperty(
    name="Use Mask",
    description="Use Mask",
    default=True) 
#------------------------------------------------------------------------------------------
# BBOX
#------------------------------------------------------------------------------------------
bpy.types.WindowManager.bbox_bevel = bpy.props.FloatProperty(min = 0, max = 100, default = 0.1)
bpy.types.WindowManager.bbox_depth = bpy.props.FloatProperty(min = 0, max = 100, default = 1)
bpy.types.WindowManager.bbox_offset = bpy.props.FloatProperty(min = -100, max = 100, default = -0.1)


bpy.types.WindowManager.bbox_apply_solidify = BoolProperty(
        default=True,
        description="Apply solidify"
        ) 
        
bpy.types.WindowManager.bbox_convert = BoolProperty(
        default=False,
        description="Convert to Dyntopo"
        )  

bpy.types.WindowManager.smooth_result = BoolProperty(
        default=False,
        description="Smooth the object"
        )                 
#------------------------------------------------------------------------------------------
# Primitives
#------------------------------------------------------------------------------------------
bpy.types.WindowManager.origin = BoolProperty(
        default=False,
        description="Place the object at the origin of the Scene"
        )      

bpy.types.WindowManager.add_mirror = BoolProperty(
        default=False,
        description="Add Mirror"
        )    

bpy.types.WindowManager.primitives_parenting = BoolProperty(
        default=False,
        description="Make the new object children to the active object"
        )  
#------------------------------------------------------------------------------------------
# Metaballs
#------------------------------------------------------------------------------------------
bpy.types.WindowManager.metaballs_pos_neg = bpy.props.EnumProperty(
        items = (('positive', "Positive", ""),
                 ('negative', "Negative", "")),
                 default = 'positive',
                 update = UpdateMetaballs
                 )   
              
#------------------------------------------------------------------------------------------
# Curves
#------------------------------------------------------------------------------------------
bpy.types.WindowManager.bbox = BoolProperty(
        default=False,
        description="Add Solidify"
        ) 

bpy.types.WindowManager.direct_cut = BoolProperty(
        default=False,
        description="Cut Directly the mesh"
        ) 

bpy.types.WindowManager.direct_rebool = BoolProperty(
        default=False,
        description="Directly Rebool"
        ) 

bpy.types.WindowManager.create_lathe = BoolProperty(
        default=False,
        description="Create Lathe"
        ) 
        
bpy.types.Scene.obj1 = bpy.props.StringProperty()
                        

#------------------------------------------------------------------------------------------
# Skin
#------------------------------------------------------------------------------------------

        
bpy.types.WindowManager.skin_mirror = BoolProperty(
        default=False,
        description="Add Mirror"
        ) 
        
#------------------------------------------------------------------------------------------
# Remesh
#------------------------------------------------------------------------------------------

        
bpy.types.WindowManager.hide_remesh_smooth = BoolProperty(
        default=True,
        description="Hide Remesh and smooth",
        update = HideRemeshSmooth
        ) 
        
        
bpy.types.WindowManager.apply_remesh = BoolProperty(
        default=False,
        description="Apply Remesh"
        )  
#------------------------------------------------------------------------------------------
# Lattice
#------------------------------------------------------------------------------------------         
bpy.types.WindowManager.copy_orientation = BoolProperty(
    name="Copy orientation",
    description="Copy the orientation of the active Object",
    default=False)

bpy.types.WindowManager.hide_lattice = BoolProperty(
        default=True,
        description="Hide Lattice on selected objects",
        update = HideLattice
        )  
           
bpy.types.WindowManager.lattice_u = bpy.props.IntProperty(min = 2, max = 100, default = 2)  
bpy.types.WindowManager.lattice_v = bpy.props.IntProperty(min = 2, max = 100, default = 2) 
bpy.types.WindowManager.lattice_w = bpy.props.IntProperty(min = 2, max = 100, default = 2)           

bpy.types.WindowManager.lattice_interp = bpy.props.EnumProperty(
        items = (('KEY_LINEAR', 'linear', ""),
                ('KEY_BSPLINE', 'bspline', ""),
                ('KEY_CATMULL_ROM', 'catmull_rom', ""),
                ('KEY_CARDINAL', 'cardinal', "")),
                default = 'KEY_BSPLINE',
                update = LatticeInterpolation
                )
            
#------------------------------------------------------------------------------------------
# Show/Hide
#------------------------------------------------------------------------------------------
bpy.types.WindowManager.show_primitives = BoolProperty(
        default=True,
        description="Show/Hide Primitives"
        )  

bpy.types.WindowManager.show_extract = BoolProperty(
        default=False,
        description="Show/Hide Extract"
        )  
 
bpy.types.WindowManager.show_symmetrize  = BoolProperty(
        default=False,
        description="Show/Hide Symmetrize Tools"
        )  
       
bpy.types.WindowManager.show_remesh = BoolProperty(
        name="Add Solidify",
        description="Add Solidify to the extracted object",
        default=False)              

bpy.types.WindowManager.show_lattice = BoolProperty(
        name="Add Lattice",
        description="Add Lattice to selected objects",
        default=False)              

bpy.types.WindowManager.show_quickpose = BoolProperty(
        name="Quick Pose",
        description="Show/Hide Quick Pose Tools",
        default=False)  