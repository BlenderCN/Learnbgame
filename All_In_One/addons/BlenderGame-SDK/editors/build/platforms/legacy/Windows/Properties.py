import bpy
import ATOM_Types
import ctypes

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


class Windows_Target_Properties(PropertyGroup):
    
    id                  = IntProperty(      default     = getUniqueID(),
                                            min         = 0)
    
    name                = StringProperty(   name        = "Name",
                                            default     = "Windows")

    architecture        = EnumProperty(     name        = "Architecture",
                                            description = "For which cpu architecture build",
                                            default     = "X86",
                                            items       = [ ("X86", "x86", 1),
                                                        ("X64", "x64", 2)])
    
    max_package_size    = IntProperty(      name        = "Max package size",
                                            description = "Maximum size (in bytes) of data package",
                                            default     = 1024,
                                            min         = 1)
    
    compression_level   = IntProperty(      name        = "Compression level of the package files",
                                            description = "Compressing files saves space on disk but is longer to load on ram due to decompression, set 0 for no compression",
                                            default     = 0,
                                            max         = 10)
    
    shadow_map_cache = BoolProperty(        name        = "Cache shadow map",
                                            description = "Caching shadow map for static lights avoids rendering shadows depth map",
                                            default     = True)

    GI_cache         = BoolProperty(        name        = "Cache global illumination datas",
                                            description = "Chaching global illumination for static mesh avoids revoxelizing the scene but takes space on disk",
                                            default     = False)

    company_name     = StringProperty(      name        = "Company name",
                                            default     = "")

    product_name     = StringProperty(      name        = "Product name",
                                            default     = "$(PROJECT_NAME)")

    icon             = StringProperty(      name        = "Icon",
                                            description = "Icon of the executable"
                                            default     = "$(PROJECT_ICON)")

    include_redist   = BoolProperty(        name        = "Include redistribualbes",
                                            description = "Add all necessary redistribualbes in the output folder",
                                            default     = False)

def register():
    pass
    #bpy.utils.register_module(__name__)

    # if not hasattr(bpy.types.WindowManager, "PlatformWindows_Properties"):
    #     bpy.types.WindowManager.Windows_Properties = PointerProperty(type=PlatformWindows_Properties)

def unregister():
    pass
    #bpy.utils.unregister_module(__name__)

    # if hasattr(bpy.types.WindowManager, "PlatformWindows_Properties"):
    #     del bpy.types.WindowManager.Windows_Properties