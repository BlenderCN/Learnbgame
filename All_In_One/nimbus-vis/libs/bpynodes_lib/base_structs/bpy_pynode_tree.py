# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber
    

:synopsis:
    

:description:
    

:applications:
    
:see_also:
   
:license:
    see license.txt and EULA.txt 

"""

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#
from ..utils.io import IO
try:
    import bpy
    from bpy.props import *
except ImportError:
    IO.info("Unable to import bpy module. Setting bpy to None for non-blender environment")
    bpy = None

# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#

class CustomBlenderNodeTree(object):
    """
    The Base Node Graph system Blender
    """
    # bl_idname = ""
    # bl_label = ""
    # bl_icon = ""
    # bl_description='Base Node Graph Class'

    # Boolean Property to flag if this NodeTree has been saved once
    saved = BoolProperty()
    # Global Scene property #TODO: Convert to PointerProperty
    scene_name = bpy.props.StringProperty(
        name='Scene',
        description='The global scene used by this node tree (never none)'
    )

    @property
    def scene(self):
        """Returns the global scene this node tree is active in."""
        scene = bpy.data.scenes.get(self.scene_name)
        if scene is None:
            scene = bpy.data.scenes[0]
        return scene
