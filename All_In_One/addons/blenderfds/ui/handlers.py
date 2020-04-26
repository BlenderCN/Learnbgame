"""BlenderFDS, Blender handlers"""

import bpy, sys
from blenderfds.lib import fds_surf, version

@bpy.app.handlers.persistent
def load_post(self):
    """This function is run after each time a Blender file is loaded"""
    # Check file format version
    version.check_file_version(bpy.context)
    # Init FDS default materials
    if not fds_surf.has_predefined(): bpy.ops.material.bf_set_predefined()
    # Init metric units
    for scene in bpy.data.scenes: scene.unit_settings.system = 'METRIC'

@bpy.app.handlers.persistent
def save_pre(self):
    """This function is run before each time a Blender file is saved"""
    # Set file format version
    version.set_file_version(bpy.context)
