bl_info = {
	"name": "Cani2D (.json)",
	"author": "Santtu Keskinen <laquendi@gmail.com>",
	"version": (0, 0, 2),
	"blender": (2, 6),
	"location": "File > Import-Export > Cani2D (.json) ",
	"description": "Export Cani2D geometry",
	"warning": "",
	"category": "Learnbgame"
}

if "bpy" in locals():
	import imp
	if "import_cani2d" in locals():
		imp.reload(import_cani2d)
	if "export_cani2d" in locals():
		imp.reload(export_cani2d)
else:
	import bpy

from bpy.props import StringProperty
	
class Cani2D_exporter(bpy.types.Operator):
	bl_idname = "export.cani2d"
	bl_label = "Export Cani2D"

	filepath = StringProperty(
			subtype='FILE_PATH',
			)

	def execute(self, context):
		from . import export_cani2d
		export_cani2d.write(self.filepath)

		return {'FINISHED'}
	
	def invoke(self, context, event):
		if not self.filepath:
			self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".json")
		wm = context.window_manager
		wm.fileselect_add(self)
		return {'RUNNING_MODAL'}
	

def menu_export(self, context):
	self.layout.operator(Cani2D_exporter.bl_idname, text="Cani2D (.json)")
	

def register():
	bpy.utils.register_module(__name__)
	
	#bpy.types.INFO_MT_file_import.append(menu_import)
	bpy.types.INFO_MT_file_export.append(menu_export)


def unregister():
	bpy.utils.unregister_module(__name__)

	#bpy.types.INFO_MT_file_import.remove(menu_import)
	bpy.types.INFO_MT_file_export.remove(menu_export)

if __name__ == "__main__":
	register()
