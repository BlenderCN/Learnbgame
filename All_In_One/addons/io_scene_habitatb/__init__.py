# ##### BEGIN LICENSE BLOCK #####
#
# This program is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0
# https://creativecommons.org/licenses/by-nc-sa/3.0/
#
# Copyright (C) Dummiesman, Yethiel 2017
#
# ##### END LICENSE BLOCK #####


bl_info = {
    "name": "HabitatB - Re-Volt File Formats",
    "author": "Dummiesman, Yethiel",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "File > Import-Export",
    "description": "Import and export Re-Volt files",
    "warning": "",
    "wiki_url": "https://github.com/Dummiesman/HabitatB/wiki",
    "support": 'COMMUNITY',
    "category": "Learnbgame",
}


import bpy
import bmesh
import types
import imp
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        StringProperty,
        CollectionProperty,
        IntVectorProperty,
        PointerProperty
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )
from . import io_ops, helpers, ui, parameters, const

from bpy_extras.io_utils import ImportHelper, ExportHelper, axis_conversion

# Completely reload the addon when hitting F8:
locals_copy = dict(locals())
for var in locals_copy:
    tmp = locals_copy[var]
    if isinstance(tmp, types.ModuleType) and tmp.__package__ == "io_scene_habitatb":
      print ("Reloading: %s"%(var))
      imp.reload(tmp)

# object properties for all rv objects
class RevoltObjectProperties(bpy.types.PropertyGroup):
    rv_type = EnumProperty(name = "Type", items = (("NONE", "None", "None"), 
                                                ("MESH", "Mesh (.prm)", "Mesh"), 
                                                #("OBJECT", "Object (.fob)", "Object"), 
                                                #("INSTANCE", "Instance (.fin)", "Instance"), 
                                                ("WORLD", "World (.w)", "World"),
                                                ("NCP", "Collision (.ncp)", "Collision (NCP)"),
                                                #("HULL", "Hull (.hul)", "Hull"),
                                                ))
    # this is for setting the object type (mesh, w, ncp, fin, ...)
    object_type = EnumProperty(name = "Object type", items = const.object_types)
    # this is the flags layer for meshes
    flags = IntVectorProperty(name = "Flags", size = 16)
    texture = IntProperty(name = "Texture") # deprecated, could be removed since textures are saved per-face now
    # this is for fin and fob file entries: each object can have unique settings. 
    # fin files have predefined settings
    flag1_long = IntProperty(get = lambda s: helpers.get_flag_long(s, 0), set = lambda s,v: helpers.set_flag_long(s, v, 0))
    flag2_long = IntProperty(get = lambda s: helpers.get_flag_long(s, 4), set = lambda s,v: helpers.set_flag_long(s, v, 4))
    flag3_long = IntProperty(get = lambda s: helpers.get_flag_long(s, 8), set = lambda s,v: helpers.set_flag_long(s, v, 8))
    flag4_long = IntProperty(get = lambda s: helpers.get_flag_long(s, 12), set = lambda s,v: helpers.set_flag_long(s, v, 12))
    # these flags can be set for objects other than the mentioned type (export .w to ncp, export prm as part of .w)
    export_as_ncp = BoolProperty(name = "Additionally export as NCP (.ncp)")
    export_as_w = BoolProperty(name = "Additionally export as World (.w)")
    use_tex_num = BoolProperty(name = "Keep texture number from mesh.")

class RevoltMeshProperties(bpy.types.PropertyGroup):
    face_material = EnumProperty(name = "Material", items = const.materials, get = helpers.get_face_material, set = helpers.set_face_material)
    face_texture = IntProperty(name = "Texture", get = helpers.get_face_texture, set = helpers.set_face_texture)
    face_double_sided = BoolProperty(name = "Double sided", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_DOUBLE), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_DOUBLE))
    face_translucent = BoolProperty(name = "Translucent", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_TRANSLUCENT), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_TRANSLUCENT))
    face_mirror = BoolProperty(name = "Mirror", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_MIRROR), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_MIRROR))
    face_additive = BoolProperty(name = "Additive blending", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_TRANSL_TYPE), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_TRANSL_TYPE))
    face_texture_animation = BoolProperty(name = "Texture animation", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_TEXANIM), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_TEXANIM))
    face_no_envmapping = BoolProperty(name = "No EnvMapping (.PRM)", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_NOENV), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_NOENV))
    face_envmapping = BoolProperty(name = "EnvMapping (.W)", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_ENV), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_ENV))
    face_cloth = BoolProperty(name = "Cloth effect (.prm)", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_CLOTH), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_CLOTH))
    face_skip = BoolProperty(name = "Do not export", get = lambda s: bool(helpers.get_face_property(s) & const.FACE_SKIP), set = lambda s,v: helpers.set_face_property(s, v, const.FACE_SKIP))


# add menu entries
# PRM
def menu_func_export_prm(self, context):
    self.layout.operator(io_ops.ExportPRM.bl_idname, text="Re-Volt PRM (.prm, .m)")

def menu_func_import_prm(self, context):
    self.layout.operator(io_ops.ImportPRM.bl_idname, text="Re-Volt PRM (.prm, .m)")

# NCP
def menu_func_import_ncp(self, context):
    self.layout.operator(io_ops.ImportNCP.bl_idname, text="Re-Volt NCP (.ncp)")

def menu_func_export_ncp(self, context):
    self.layout.operator(io_ops.ExportNCP.bl_idname, text="Re-Volt NCP (.ncp)")

# W
def menu_func_import_w(self, context):
    self.layout.operator(io_ops.ImportW.bl_idname, text="Re-Volt World (.w)")

def menu_func_export_w(self, context):
    self.layout.operator(io_ops.ExportW.bl_idname, text="Re-Volt World (.w)")

# POS
def menu_func_import_pos(self, context):
    self.layout.operator(io_ops.ImportPOS.bl_idname, text="Re-Volt Position Nodes (.pan)")

def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import_prm)
    bpy.types.INFO_MT_file_import.append(menu_func_import_ncp)
    bpy.types.INFO_MT_file_import.append(menu_func_import_w)
    bpy.types.INFO_MT_file_import.append(menu_func_import_pos)
    bpy.types.INFO_MT_file_export.append(menu_func_export_prm)
    bpy.types.INFO_MT_file_export.append(menu_func_export_ncp)
    bpy.types.INFO_MT_file_export.append(menu_func_export_w)

    #bpy.types.Scene.ui_properties = bpy.props.PointerProperty(type=ui.UIProperties)

    bpy.types.Object.revolt = PointerProperty(type = RevoltObjectProperties)
    bpy.types.Mesh.revolt = PointerProperty(type = RevoltMeshProperties)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import_prm)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_ncp)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_w)
    bpy.types.INFO_MT_file_import.remove(menu_func_import_pos)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_ncp)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_w)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_prm)

    # del bpy.types.Scene.ui_properties

    del bpy.types.Object.revolt
    del bpy.types.Mesh.revolt


if __name__ == "__main__":
    register()
