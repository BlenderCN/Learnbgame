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


# class Project_Properties(PropertyGroup):
    
#     edit_mode               = EnumProperty(         name        = "Edit mode",
#                                                     description = "Set which mode to edit on.",
#                                                     default     = "DEBUG",
#                                                     items       = [ ("DEBUG",   "debug",   "Adds features for dubuging"),
#                                                                     ("RELEASE", "release", "Edit for release version.")])

class lol(bpy.types.PropertyGroup):
    
    lol = bpy.props.IntProperty(name = "lol",
                                default = 2)
                                
def register():
    bpy.utils.register_module(__name__)

    for i in dir(sys.modules[__name__]):
        member = getattr(sys.modules[__name__], i)
        if inspect.isclass(member):
            if issubclass(member, PropertyGroup):
                print("ok")
                exec("bpy.types.WindowManager.{0} = PointerProperty(type={0})".format(i))
        

def unregister():
    bpy.utils.unregister_module(__name__)

    for i in dir(sys.modules[__name__]):
        member = getattr(sys.modules[__name__], i)
        if inspect.isclass(member):
            if issubclass(member, PropertyGroup):
                exec("del bpy.types.WindowManager.%s"%i)