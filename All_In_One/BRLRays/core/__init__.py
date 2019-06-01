# Blender 2.5 Ray Trace BRL-CAD Add-On

# Authors:
# Morning Star

"""Main RTRender extension class definition"""

# System libs
import os
import sys
import threading
#import multiprocessing
#import time
#import subprocess
#import array
#import math
#import mathutils

# Blender libs
import bpy
#import bgl
import bl_ui
#from bpy.app.handlers import persistent

# Framework libs
#...

# Exporter libs
#...

def _register_elm(elm, required=False):
  try:
    elm.COMPAT_ENGINES.add('RayTrace_RENDER')

  except:
    if required:
      MtsLog('Failed to add RayTrace to ' + elm.__name__)

# Add standard Blnder Interface elemets
_register_elm(bl_ui.properties_render.RENDER_PT_render,required=True)
_register_elm(bl_ui.properties_render.RENDER_PT_dimensions, required=True)
_register_elm(bl_ui.properties_render.RENDER_PT_output, required=True)
_register_elm(bl_ui.properties_render.RENDER_PT_stamp)

_register_elm(bl_ui.properties_render_layer.RENDERLAYER_PT_layers)

_register_elm(bl_ui.properties_scene.SCENE_PT_scene, required=True)
_register_elm(bl_ui.properties_scene.SCENE_PT_audio)
_register_elm(bl_ui.properties_scene.SCENE_PT_physics)
_register_elm(bl_ui.properties_scene.SCENE_PT_keying_sets)
_register_elm(bl_ui.properties_scene.SCENE_PT_keying_set_paths)
_register_elm(bl_ui.properties_scene.SCENE_PT_unit)
_register_elm(bl_ui.properties_scene.SCENE_PT_color_management)
_register_elm(bl_ui.properties_scene.SCENE_PT_rigid_body_world)
_register_elm(bl_ui.properties_scene.SCENE_PT_custom_props)

_register_elm(bl_ui.properties_world.WORLD_PT_context_world, required=True)
_register_elm(bl_ui.properties_world.WORLD_PT_preview)

_register_elm(bl_ui.properties_material.MATERIAL_PT_preview)

_register_elm(bl_ui.properties_data_lamp.DATA_PT_context_lamp)


# compatible() copied from blnder repository (netrender)
def compatible(mod):
  mod = getattr(bl_ui, mod)

  for member in dir(mod):
    subclass = getattr(mod, member)
    _register_elm(subclass)

  del mod

compatible("properties_data_camera")
compatible("properties_data_mesh")
compatible("properties_data_speaker")
compatible("properties_particle")

@RayTraceAddon.addon_register_class
class RENDERENGINE_RayTrace(bpy.types.RenderEngine):
  '''
  RayTrace Engine Exporter/Integration class
  '''

  bl_idname = 'RAYTRACE_RENDER'
  bl_label = 'RayTrace'
  bl_use_preview = True

  render_lock = threading.Lock()
  preferences = None

  def render(seld, scene):
    '''
    scene: bpy.types.Scene

    Export the given scene to RayTrace.

    Returns None
    '''






