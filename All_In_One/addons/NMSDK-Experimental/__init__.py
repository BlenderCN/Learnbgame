import bpy
from .BlenderExtensions import (NMSNodes, NMSEntities, NMSPanels,
                                NMSShaderNode, SettingsPanels)
from .addon_script import NMS_Export_Operator, NMS_Import_Operator

from .NMSDK import ImportSceneOperator, ImportMeshOperator

customNodes = NMSNodes()

bl_info = {
    "name": "No Man's Sky Development Kit",
    "author": "gregkwaste, monkeyman192",
    "version": (0, 9, 6),
    "blender": (2, 79, 0),
    "location": "File > Export",
    "description": "Create NMS scene structures and export to NMS File format",
    "warning": "",
    "wiki_url": "https://github.com/monkeyman192/NMSDK/wiki",
    "tracker_url": "https://github.com/monkeyman192/NMSDK/issues",
    "category": "Learnbgame",
}


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(NMS_Export_Operator.bl_idname,
                         text="Export to NMS XML Format ")


def menu_func_import(self, context):
    self.layout.operator(NMS_Import_Operator.bl_idname,
                         text="Import NMS SCENE.EXML")


def register():
    bpy.utils.register_class(NMS_Export_Operator)
    bpy.utils.register_class(NMS_Import_Operator)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    NMSPanels.register()
    NMSShaderNode.register()
    customNodes.register()
    NMSEntities.register()
    SettingsPanels.register()
    bpy.utils.register_class(ImportSceneOperator)
    bpy.utils.register_class(ImportMeshOperator)


def unregister():
    bpy.utils.unregister_class(NMS_Export_Operator)
    bpy.utils.unregister_class(NMS_Import_Operator)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    NMSPanels.unregister()
    NMSShaderNode.unregister()
    customNodes.unregister()
    NMSEntities.unregister()
    SettingsPanels.unregister()
    bpy.utils.unregister_class(ImportSceneOperator)
    bpy.utils.unregister_class(ImportMeshOperator)
