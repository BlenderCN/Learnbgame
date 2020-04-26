"""BlenderFDS, FDS SURF routines"""

import bpy

predefined = ("INERT", "OPEN", "MIRROR")

def has_predefined():
    """Check predefined materials"""
    return set(predefined) <= set(bpy.data.materials.keys())

def set_predefined(context):
    """Set BlenderFDS predefined materials/bcs"""
    value = """
&SURF ID='INERT'  RGB=204,204,51 FYI='Predefined SURF' /
&SURF ID='OPEN'   RGB=51,204,204 FYI='Predefined SURF' TRANSPARENCY=.2 /
&SURF ID='MIRROR' RGB=51,51,204  FYI='Predefined SURF' /
    """
    context.scene.from_fds(context, value)
