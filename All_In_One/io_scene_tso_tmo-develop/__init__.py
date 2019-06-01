bl_info = {
	"name": "TechArts3D tso format and tmo format",
	"category": "Learnbgame",
}

import bpy
from io_scene_tso_tmo import tso_import_op, tmo_import_op, tso_export_op

def menu_func_import(self, context):
    self.layout.operator(tso_import_op.TsoImportOperator.bl_idname, text="TechArts3D tso (.tso)")
    self.layout.operator(tmo_import_op.TmoImportOperator.bl_idname, text="TechArts3D tmo (.tmo)")

def menu_func_export(self, context):
    self.layout.operator(tso_export_op.TsoExportOperator.bl_idname, text="TechArts3D tso (.tso)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

