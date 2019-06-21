import bpy
import BuildTool
import config

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

global BUILD_PLATFORMS

class ATOMBuildTool(AddonPreferences):
    
    bl_idname = ""

    company = StringProperty(   name        = "Company",
                                description = "Name of the company to include in the release",
                                default     = "")

    def draw(self, context):
        
        layout = self.layout
        layout.prop(self, "company")

class BuildOutputItem(PropertyGroup):
    
    platform            =   EnumProperty(   name        = "Platform",
                                            description = "For which platform to build",
                                            default     = config.DEFAULT_PLATFORM,
                                            items       = BUILD_PLATFORMS)

    id                  =   IntProperty(    name        = "ID",
                                            default     = 0,
                                            min         = 0)

class RegisterPlatforms(Operator):
    
    bl_idname = "wm.register_platforms"
    bl_label  = "Register PLatforms"

    def execute(self, context):
        bpy.utils.register_class(BuildOutputItem)
        return {"FINISHED"}

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

