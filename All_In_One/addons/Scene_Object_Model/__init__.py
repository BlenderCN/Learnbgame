bl_info = {
	"name": "Scene Object Model format (.som)",
	"author": "John´s Project",
	"version": (0, 2),
	"blender": (2, 57, 0),
	"location": "File > Import-Export > Scene Object Model (.som) ",
	"description": "Import-Export Scene Object Model",
	"warning": "",
	"wiki_url": "",
	"category": "Learnbgame",
}

if "bpy" in locals():
	import importlib
	if "import_som" in locals():
		importlib.reload(import_som)
	if "export_som" in locals():
		importlib.reload(export_som)
else:
	import bpy

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper


class SOMImporter(bpy.types.Operator):
	"""Load Scene Object Model data"""
	bl_idname = "import_model.som"
	bl_label = "Import SOM"
	bl_options = {'UNDO'}

	filepath = StringProperty(
			subtype='FILE_PATH',
			)
	filter_glob = StringProperty(default="*.som", options={'HIDDEN'})

	def execute(self, context):
		from . import import_som
		import_som.read(self.filepath)
		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		wm.fileselect_add(self)
		return {'RUNNING_MODAL'}


class SOMExporter(bpy.types.Operator, ExportHelper):
	"""Save Scene Object Model data"""
	bl_idname = "export_model.som"
	bl_label = "Export SOM"

	filename_ext = ".som"
	filter_glob = StringProperty(default="*.som", options={'HIDDEN'})

	apply_modifiers = BoolProperty(
			name="Apply Modifiers",
			description="Use transformed Model data from each object",
			default=False,
			)

	def execute(self, context):
		from . import export_som
		export_som.write(self.filepath,
						 self.apply_modifiers
						 )

		return {'FINISHED'}


def menu_import(self, context):
	self.layout.operator(SOMImporter.bl_idname, text="Scene Object Model (.som)")


def menu_export(self, context):
	self.layout.operator(SOMExporter.bl_idname, text="Scene Object Model (.som)")


def register():
	bpy.utils.register_module(__name__)

	bpy.types.INFO_MT_file_import.append(menu_import)
	bpy.types.INFO_MT_file_export.append(menu_export)


def unregister():
	bpy.utils.unregister_module(__name__)

	bpy.types.INFO_MT_file_import.remove(menu_import)
	bpy.types.INFO_MT_file_export.remove(menu_export)

if __name__ == "__main__":
	register()
