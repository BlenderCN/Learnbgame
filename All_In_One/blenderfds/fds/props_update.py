"""BlenderFDS, update FDS props"""

import bpy
from blenderfds.types import *
from blenderfds.types.extensions import update_ob_bf_namelist_idname

# List all bf_namelist.enumproperty_item except for empty ones
def _get_items(bpy_type):
    return sorted([bf_namelist.enumproperty_item \
        for bf_namelist in bf_namelists \
        if bf_namelist.bpy_type == bpy_type \
        and bf_namelist.enumproperty_item])

bpy.types.Object.bf_namelist_idname = bpy.props.EnumProperty(  # link each object to related BFNamelist
    name="Namelist", description="Type of FDS namelist",
    items=_get_items(bpy.types.Object), default="bf_obst", update=update_ob_bf_namelist_idname) # now items are updated
    
bpy.types.Material.bf_namelist_idname = bpy.props.EnumProperty( # link each material to related BFNamelist
    name="Namelist", description="Type of FDS namelist",
    items=_get_items(bpy.types.Material), default="bf_surf") # now items are updated
    
