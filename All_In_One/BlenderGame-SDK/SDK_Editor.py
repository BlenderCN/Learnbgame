import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       FloatVectorProperty,
                       IntVectorProperty,
                       BoolVectorProperty,
                       CollectionProperty)
                       
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       Property,
                       AddonPreferences)

import sys, os
import utils
import bpy
import bgl
from OpenGL.GL import*
from OpenGL.GL.framebufferobjects import * 
import inspect
import numpy
from ctypes import *
import time
import ATOM_Types
import config

class ATOM_Engine(bpy.types.RenderEngine):

    bl_idname = "ATOM_ENGINE"
    bl_label = "ATOM"
    bl_use_preview = True

    def __init__(self):
        print("ok")
    def draw_viewport(self, context):
        pass
        
    def view_update(self, context):
        self.draw_viewport(context)

    def view_draw(self, context):
        self.draw_viewport(context)

    def tag_redraw():
        pass

################# DEBUG FEATURES ##################

if config.DEBUG:
    
    class ReloadBinaries(Operator):
        
        bl_idname = "wm.reload_binaries"
        bl_label = "RELOAD_BINARIES"

        def execute(self, context):
            print("ok")
            # global modules

            # for i in modules:
            #     if hasattr(i, "reloadBinary"):
            #         i.reloadBinary()

            return {"FINISHED"}

###################################################

def unregister():

    klass = utils.checkRegister("ATOM")

    spaces = []

    if not klass == None:

        if bpy.context.scene.render.engine == "ATOM_ENGINE":
            for area in bpy.context.screen.areas:
                if area.type == "VIEW_3D":
                    for space in area.spaces:
                        if space.type == "VIEW_3D":
                            if space.viewport_shade == "RENDERED":
                                spaces.append(space)
                                space.viewport_shade = "SOLID"
   
        bpy.utils.unregister_module(__name__)

        for space in spaces:
            space.viewport_shade = "RENDERED"

def register():

    bpy.utils.register_module(__name__)