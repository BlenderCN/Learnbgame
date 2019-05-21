bl_info = {
	"name"        : "Lego Racers 2 .MD2",
	"author"      : "Irup at Rock Raiders United, with help from Will Kirby's LibLR2",
	"blender"     : (2, 74, 0),
	"location"    : "File > Import-Export",
	"description" : "Imports or exports an .MD2 model compatible with Lego Racers 2.",
	"category"    : "Import-Export"
}

if 'bpy' in locals():
    import importlib
    if 'import_lr2' in locals():
        importlib.reload(import_lr2)
    if 'export_lr2' in locals():
        importlib.reload(export_lr2)

import os
import bpy

from bpy.props import (
	CollectionProperty,
	StringProperty	,
	BoolProperty	  ,
	EnumProperty	  ,
	FloatProperty	 ,
)
from bpy_extras.io_utils import (
	ImportHelper			  ,
	ExportHelper			  ,
	orientation_helper_factory,
	axis_conversion		   ,
)
class ImportLR2(bpy.types.Operator, ImportHelper):
	"""Import a Lego Racers 2 .MD2 file"""
	bl_idname  = 'import_mesh.lr2'
	bl_label   = 'Import Lego Racers 2 .MD2'
	bl_options = {'UNDO'}
	files = CollectionProperty(
		name	    = "File Path",
		description = "File path used for finding the .MD2 file.",
		type	    = bpy.types.OperatorFileListElement
	)
	directory	= StringProperty()
	filename_ext = ".md2"
	filter_glob  = StringProperty(default="*.md2", options={'HIDDEN'})
	
	md2_open_bitmaps = BoolProperty(
		name        = 'Find and open bitmaps',
		description = 'Opens relevant images from the "game data" directory, if the model file is loaded from there.',
		default     = True,
	)
	
	def execute(self, context):
		paths = [os.path.join(self.directory, name.name) for name in self.files]
		keywords = {
			'open_bitmaps': self.md2_open_bitmaps,
		}
		if not paths: paths.append(self.filepath)
		from . import import_lr2
		for path in paths:
			import_lr2.open_lr2(path, **keywords)
		return {'FINISHED'}
		
class ExportLR2(bpy.types.Operator, ExportHelper):
	"""Export a Lego Racers 2 .MD2 file"""
	bl_idname = "export_mesh.lr2"
	bl_label = "Export Lego Racers 2 .MD2"

	filename_ext = ".md2"
	filter_glob = StringProperty(default="*.md2", options={'HIDDEN'})
	
	md2_version = EnumProperty(
		name        = 'Version',
		#description = 'Keep this at default (MDL2) if unsure. For testing purposes.',
		description = 'For future support.',
		items       = (
			('MDL2', 'MDL2', ''),
			#('MDL1', 'MDL1', ''),
			#('MDL0', 'MDL0', ''),
		)
	)
	
	md2_distance_fades = BoolProperty(
		name        = 'Fade',
		description = 'Makes the model fade at a far distance.',
		default     = False,
	)

	def execute(self, context):
		from . import export_lr2
		keywords = {
			'version': self.md2_version,
			'distance_fades': self.md2_distance_fades,
		}
		export_lr2.write_lr2(self.filepath, **keywords)
		return {'FINISHED'}
		
def menu_func_import(self, context):
	self.layout.operator(ImportLR2.bl_idname, text="Lego Racers 2 (.md2)")
def menu_func_export(self, context):
	self.layout.operator(ExportLR2.bl_idname, text="Lego Racers 2 (.md2)")
def register():
	bpy.utils.register_class(ImportLR2)
	bpy.utils.register_class(ExportLR2)
	bpy.types.INFO_MT_file_import.append(menu_func_import)
	bpy.types.INFO_MT_file_export.append(menu_func_export)
def unregister():
	bpy.utils.unregister_class(ImportLR2)
	bpy.utils.unregister_class(ExportLR2)
	bpy.types.INFO_MT_file_import.remove(menu_func_import)
	bpy.types.INFO_MT_file_export.remove(menu_func_export)
if __name__ == "__main__": register()