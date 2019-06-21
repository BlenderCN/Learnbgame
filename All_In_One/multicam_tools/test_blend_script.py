import sys
import os
import bpy

blend_dir = os.path.dirname(bpy.data.filepath)
mod_dir = os.path.split(blend_dir)[0]
if mod_dir not in sys.path:
   sys.path.append(mod_dir)
   
import multicam_tools
import imp
if multicam_tools.get_is_registered():
    multicam_tools.unregister()
    imp.reload(multicam_tools)
multicam_tools.register()
