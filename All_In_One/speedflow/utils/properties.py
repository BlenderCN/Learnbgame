import bpy
from bpy.props import BoolProperty, StringProperty

class ModalPieMenuCollectionGroup(bpy.types.PropertyGroup):
    
    meshes_list = {}
    
    solidify_enabled = BoolProperty(
            default=False
            )
    
    bevel_enabled = BoolProperty(
            default=False
            )
    
    subdiv_mode = BoolProperty(
            default=True
            )
    
    bevel_weight_enabled = BoolProperty(
            default=False
            )
    
    keep_bevel_weight = BoolProperty(
            default=False
            )
    
    symmetrize_enabled = BoolProperty(
            default=False
            )
    
    subsurf_enabled = BoolProperty(
            default=False
            )
    
    mirror_enabled = BoolProperty(
            default=False
            )
    
    mirror_name = StringProperty()
    
    tubify_enabled = BoolProperty(
            default=False
            )
    
    rotate_enabled = BoolProperty(
            default=False
            )
    
    array_enabled = BoolProperty(
            default=False
            )
            
    array_name = StringProperty()
    
    boolean_enabled = BoolProperty(
            default=False
            )    
            
    boolean_name = StringProperty()