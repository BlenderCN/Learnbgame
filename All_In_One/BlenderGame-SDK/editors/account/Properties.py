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


class ATOM_io_Proprties(PropertyGroup):

    project_folder  =   StringProperty( name        = "Project folder",
                                        description = "Root folder for project files",
                                        subtype     = "DIR_PATH")
                                        
def register():
    print(__name__)
    bpy.utils.register_module(__name__)

    if not hasattr(bpy.types.WindowManager, "ATOM_io_properties"):
        bpy.types.WindowManager.ATOM_io_Proprties = PointerProperty(type=ATOM_io_Proprties)

def unregister():
    bpy.utils.unregister_module(__name__)

    if hasattr(bpy.types.WindowManager, "ATOM_io_properties"):
        del bpy.types.WindowManager.ATOM_io_Proprties