import bpy

bl_info = {
	"name": "advancedfx Blender Scripts",
	"author": "Dominik Tugend",
	"version": (1, 7, 1),
	"blender": (2, 80, 0),
	"location": "File > Import/Export",
	"description": "For inter-operation with HLAE.",
	#"warning": "",
	#"wiki_url": "",
	#"tracker_url": "",
	"category": "Learnbgame",
}

from . import utils, import_agr, import_cam, export_cam, import_bvh, export_bvh

classes = (
	import_bvh.BvhImporter,
	export_bvh.BvhExporter,
	import_cam.CamImporter,
	export_cam.CamExporter,
	import_agr.AgrImporter,
)

def menu_func_import_agr(self, context):
	self.layout.operator(import_agr.AgrImporter.bl_idname, text="HLAE afxGameRecord (.agr)")
	
def menu_func_import_cam(self, context):
	self.layout.operator(import_cam.CamImporter.bl_idname, text="HLAE Camera IO (.cam)")

def menu_func_export_cam(self, context):
	self.layout.operator(export_cam.CamExporter.bl_idname, text="HLAE Camera IO (.cam)")

def menu_func_import_bvh(self, context):
	self.layout.operator(import_bvh.BvhImporter.bl_idname, text="HLAE old Cam IO (.bvh)")

def menu_func_export_bvh(self, context):
	self.layout.operator(export_bvh.BvhExporter.bl_idname, text="HLAE old Cam IO (.bvh)")

def register():
	from bpy.utils import register_class
	for cls in classes:
		register_class(cls)
	
	bpy.types.TOPBAR_MT_file_import.append(menu_func_import_agr)
	bpy.types.TOPBAR_MT_file_import.append(menu_func_import_cam)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export_cam)
	bpy.types.TOPBAR_MT_file_import.append(menu_func_import_bvh)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export_bvh)

def unregister():
	from bpy.utils import unregister_class
	for cls in reversed(classes):
		unregister_class(cls)
	
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_bvh)
	bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_bvh)
	bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_agr)

if __name__ == "__main__":
	unregister()
	register()