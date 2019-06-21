bl_info = {
	"name": "Skyrim hkx format",
	"category": "Learnbgame",
}

import bpy
from io_anim_hkx import hka_import_op, hka_export_op

def menu_func_import(self, context):
    self.layout.operator(hka_import_op.hkaImportOperator.bl_idname, text="Skyrim hkx (.hkx)")

def menu_func_export(self, context):
    self.layout.operator(hka_export_op.hkaExportOperator.bl_idname, text="Skyrim hkx (.hkx)")

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

