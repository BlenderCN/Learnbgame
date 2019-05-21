bl_info = {
	"name": "Bayonetta Wmb Format",
	"author": "Qing Guo",
	"blender": (2, 72, 0),
	"location": "File > Import-Export",
	"description": "Import Bayonetta mesh data.",
	"warning": "",
	"category": "Learnbgame"
}

# To support reload properly, try to access a package var,
# if it's there, reload everything
if "bpy" in locals():
	import importlib
	if "wmb_importer" in locals():
		importlib.reload(wmb_importer)
		
import os
import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import (CollectionProperty, StringProperty, BoolProperty, EnumProperty, FloatProperty)
		
class ImportWmb(bpy.types.Operator, ImportHelper):
	"""Load a Bayonetta wmb mesh file."""
	bl_idname = "import_mesh.wmb"
	bl_label = "Import Bayonetta Wmb"
	bl_options = {'UNDO'}

	files = CollectionProperty(name="File Path",
						  description="File path used for importing the Bayonetta mesh file",
						  type=bpy.types.OperatorFileListElement)

	directory = StringProperty()

	filename_ext = ".wmb"
	filter_glob = StringProperty(default="*.wmb", options={'HIDDEN'})

	def execute(self, context):
		paths = [os.path.join(self.directory, name.name)
				 for name in self.files]
		if not paths:
			paths.append(self.filepath)

		from . import wmb_importer
		
		for path in paths:
			wmb_importer.import_wmb(path)

		return {'FINISHED'}

def menu_func_import(self, context):
	self.layout.operator(ImportWmb.bl_idname, text="Bayonetta Mesh (.wmb)")
		
def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_import.append(menu_func_import)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == '__main__':
	register()