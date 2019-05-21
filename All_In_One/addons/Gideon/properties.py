
import bpy
from bpy.props import (BoolProperty,
                       EnumProperty,
                       FloatProperty,
                       IntProperty,
                       StringProperty,
                       CollectionProperty,
                       PointerProperty)

#Gideon-Specific Lamp Settings
class GideonLampSettings(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Lamp.gideon = PointerProperty(
            name = "Gideon Lamp Settings",
            description = "Gideon Lamp Settings",
            type=cls,
            )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Lamp.gideon


#Gideon-Specific Material Settings
class GideonMaterialSettings(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Material.gideon = PointerProperty(
            name = "Gideon Material Settings",
            description = "Gideon Material Settings",
            type = cls,
            )
        cls.shader = StringProperty(
            name = "Shader",
            description = "Name of the shader function to use for this material",
            )
        cls.volume = StringProperty(
            name = "Volume Shader",
            description = "Name of the volume shader function to use for this material",
            )

    @classmethod
    def unregister(cls):
        del bpy.types.Material.gideon


class GideonSourceFileSettings(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name = "Source Name", default = "", subtype = 'FILE_PATH')
    external = bpy.props.BoolProperty(name = "External Source", default = False)

class GideonFunctionSettings(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name = "Function Name", default = "")
    intern_name = bpy.props.StringProperty(name = "Internal Function Name", default = "")

#Gideon-Specific Render Settings
class GideonRenderSettings(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.gideon = PointerProperty(
            name = "Gideon Render Settings",
            description = "Gideon Render Settings",
            type = cls
            )
        cls.entry_point = StringProperty(
            name = "Entry Point",
            description = "Function name that will be used as the entry point for the renderer program",
            default = "main"
            )

        cls.std_path = StringProperty(
            name = "Standard Path",
            description = "Directory containing the Gideon Standard Library",
            subtype = 'DIR_PATH',
            default = ""
            )

        cls.source_path = StringProperty(
            name = "Source Path",
            description = "Search path for external Gideon source files",
            subtype = 'DIR_PATH',
            default = ""
            )

        
        cls.sources = CollectionProperty(
            name = "Source Files",
            description = "Collection of source files that make up the gideon program",
            type = GideonSourceFileSettings
            )
        cls.active_source_index = IntProperty(
            name = "Active Source Index",
            default = -1,
            min = -1, max = 1000
            )
        
        cls.shader_list = CollectionProperty(
            name = "Material Functions",
            description = "List of externally visible material functions in the compiled renderer",
            type = GideonFunctionSettings
            )

        cls.entry_list = CollectionProperty(
            name = "Entry Points",
            description = "List of externally visible render entry point functions",
            type = GideonFunctionSettings
            )
        
    @classmethod
    def unregister(cls):
        del bpy.types.Scene.gideon

class SOURCE_LIST_OT_add(bpy.types.Operator):
    bl_idname = "gideon.add_source"
    bl_label = "Add Source File"
    bl_description = "Add source file"
    
    def invoke(self, context, event):
        g_scene = context.scene.gideon
        s = g_scene.sources.add()
        s.name = "source"
        
        g_scene.active_source_index = len(g_scene.sources)-1

        return {'FINISHED'}

class SOURCE_LIST_OT_del(bpy.types.Operator):
    bl_idname = "gideon.remove_source"
    bl_label = "Remove Source File"
    bl_description = "Remove source file"
    
    def invoke(self, context, event):
        g_scene = context.scene.gideon
        idx = g_scene.active_source_index
        
        if (idx >= 0):
            g_scene.sources.remove(idx)
            g_scene.active_source_index = -1
    
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SOURCE_LIST_OT_add)
    bpy.utils.register_class(SOURCE_LIST_OT_del)

    bpy.utils.register_class(GideonLampSettings)
    bpy.utils.register_class(GideonMaterialSettings)

    bpy.utils.register_class(GideonSourceFileSettings)
    bpy.utils.register_class(GideonFunctionSettings)
    bpy.utils.register_class(GideonRenderSettings)


def unregister():
    bpy.utils.unregister_class(SOURCE_LIST_OT_add)
    bpy.utils.unregister_class(SOURCE_LIST_OT_del)

    bpy.utils.unregister_class(GideonLampSettings)
    bpy.utils.unregister_class(GideonMaterialSettings)

    bpy.utils.unregister_class(GideonRenderSettings)
    bpy.utils.unregister_class(GideonMaterialFunctionSettings)
    bpy.utils.unregister_class(GideonSourceFileSettings)
