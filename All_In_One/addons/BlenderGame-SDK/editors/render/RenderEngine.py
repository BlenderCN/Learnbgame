import bpy
import ATOM_Types
import ctypes
import os
from . import config

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
                       AddonPreferences,
                       RenderEngine)


__BIN_PATH = config.BINARY

class ATOM_render_engine(RenderEngine):

    if config.DEBUG:

        def reload_binaries(self, context):
            
            if os.path.isfile(__BIN_PATH) and isfile(__BIN_PATH[:-3] + "tmp"):
                if not self.binary == None:
                    ctypes.windll.kernel32.FreeLibrary(self.binary._handle)
                    os.remove(__BIN_PATH)
                    os.rename(__BIN_PATH[:-3] + "tmp", __BIN_PATH)
                    self.binary = ctypes.cdll.LoadLibrary(__BIN_PATH)
                
                    for window in context.window_manager.windows:
                        for area in window.screen.areas:
                            if area.type == 'VIEW_3D':
                                area.tag_redraw()
                                
    def __init__(self):
        
        self.binary = None

        if os.path.isfile(__BIN_PATH):
            self.binary = ctypes.cdll.LoadLibrary(__BIN_PATH)

        elif isfile(__BIN_PATH[:-3] + "tmp") and config.DEBUG:
            os.rename(__BIN_PATH[:-3] + "tmp", __BIN_PATH)
            self.binary = ctypes.cdll.LoadLibrary(__BIN_PATH)

# def register():

# def unregister():
    

