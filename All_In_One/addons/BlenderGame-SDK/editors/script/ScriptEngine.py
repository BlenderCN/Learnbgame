import bpy
import ctypes
import ATOM_Types
import ATOM_Editor

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

class ScriptEngine(ATOM_Types.Module):

    def __init__(self):
        pass

class ReloadScript(Operator):
    bl_idname = "ATOM.reload_scripts"
    bl_label = "RELOAD_SCRIPTS"

    def invoke(self, context):
        
        engine = ATOM_Editor.getEngineInstance()
        bin_path = context.window_manager.ATOM_io_Proprties.project_folder

        if not engine == None:
            
            if isfile(bin_path) and isfile(bin_path[:-3] + "tmp"):
                if not engine.getScriptsHandle() == 0:
                    engine.unload_scripts()
                    os.remove(bin_path)
                    os.rename(bin_path[:-3] + "tmp", bin_path)
                    engine.load_scripts(bin_path)
                
