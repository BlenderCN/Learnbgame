
import bpy
from . import types
from . import operators
from . import ui
from . import preferences
from . import selector
from . import parse_xr


def menu_import_object(self, context):
    self.layout.operator(operators.OperatorImportObject.bl_idname, text='S.T.A.L.K.E.R. Object')


def register():
    bpy.utils.register_class(preferences.StalkerImportObjectPreferences)
    bpy.utils.register_class(types.StalkerObjectProperties)
    types.StalkerObjectProperties.bpy_type.stalker = bpy.props.PointerProperty(type=types.StalkerObjectProperties)
    bpy.utils.register_class(types.StalkerMeshProperties)
    types.StalkerMeshProperties.bpy_type.stalker = bpy.props.PointerProperty(type=types.StalkerMeshProperties)
    bpy.utils.register_class(types.StalkerMaterialProperties)
    types.StalkerMaterialProperties.bpy_type.stalker = bpy.props.PointerProperty(type=types.StalkerMaterialProperties)
    bpy.utils.register_class(operators.OperatorImportObject)
    bpy.types.INFO_MT_file_import.append(menu_import_object)
    bpy.utils.register_class(ui.StalkerObjectPanel)
    selector.create_selector(parse_xr.parse_shaders, 'engine_shader', 'es', 'Shader')
    selector.create_selector(parse_xr.parse_shaders_xrlc, 'compiler_shader', 'cs', 'Compiler')
    selector.create_selector(parse_xr.parse_game_materials, 'game_material', 'gm', 'Game_Material')
    bpy.utils.register_class(ui.StalkerMaterialPanel)


def unregister():
    bpy.utils.unregister_class(ui.StalkerMaterialPanel)
    bpy.utils.unregister_class(ui.StalkerObjectPanel)
    selector.unregister_selector()
    selector.operatorsList = []
    selector.menusList = []
    bpy.types.INFO_MT_file_import.remove(menu_import_object)
    bpy.utils.unregister_class(operators.OperatorImportObject)
    del types.StalkerMaterialProperties.bpy_type.stalker
    bpy.utils.unregister_class(types.StalkerMaterialProperties)
    del types.StalkerMeshProperties.bpy_type.stalker
    bpy.utils.unregister_class(types.StalkerMeshProperties)
    del types.StalkerObjectProperties.bpy_type.stalker
    bpy.utils.unregister_class(types.StalkerObjectProperties)
    bpy.utils.unregister_class(preferences.StalkerImportObjectPreferences)
