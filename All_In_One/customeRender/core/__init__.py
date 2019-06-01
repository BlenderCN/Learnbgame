
import os, sys, threading

# Blender libs
import bpy, bl_ui 

# Framework libs
from extensions_framework import util as efutil

from .. import CustomeRenderAddon

from ..properties import (addonpref)

from ..ui import (addonpref )


@CustomeRenderAddon.addon_register_class
class RENDERENGINE_custome(bpy.types.RenderEngine):
    bl_idname           = 'CUSTOME_RENDER'
    bl_label            = 'Custome'
    bl_use_preview      = True

    render_lock = threading.Lock()
    
    def render(self, scene):
        if self is None or scene is None:
            print('ERROR: Scene is missing!')
            return
        
        with self.render_lock:    # just render one thing at a time
            if scene.name == 'preview':
                self.render_preview(scene)
                return
            print("Main Render")
            

    def render_preview(self, scene):
        print("Render Preview Initiated")
    
    
