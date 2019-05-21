bl_info = {
	"name"       : "Attention To Detail .MD2 model import/export",
	"author"     : "Irup at Rock Raiders United, with help from Will Kirkby's LibLR2 and epicabsol's DromeEd.",
	"blender"    : (2, 74, 0),
	"location"   : "File > Import-Export",
	"description": "Imports or exports an .MD2 model compatible with Attention To Detail games.",
	"category"	 : "Import-Export"
}

if 'bpy' in locals():
	import importlib
	if 'import_atd' in locals(): importlib.reload(import_atd)
	if 'export_atd' in locals(): importlib.reload(export_atd)

import os
import bpy

from bpy.props import (
	CollectionProperty,
	StringProperty	  ,
	BoolProperty	  ,
	EnumProperty	  ,
	FloatProperty	  ,
)
from bpy_extras.io_utils import (
	ImportHelper			  ,
	ExportHelper			  ,
	orientation_helper_factory,
	axis_conversion		      ,
)
class ImportATD(bpy.types.Operator, ImportHelper):
	"""Import an Attention To Detail .MD2 file"""
	bl_idname  = 'import_mesh.atd'
	bl_label   = 'Import Attention To Detail .MD2'
	bl_options = {'UNDO'}
	files = CollectionProperty(
		name		= "File Path",
		description = "File path used for finding the .MD2 file.",
		type		= bpy.types.OperatorFileListElement
	)
	directory	= StringProperty()
	filename_ext = ".md2"
	filter_glob  = StringProperty(default="*.md2", options={'HIDDEN'})
	
	md2_usebitmaps = BoolProperty(
		name		= 'Find and open bitmaps',
		description = 'Opens relevant images from the "game data" directory, if the model file is loaded from there.',
		default	    = True,
	)
	md2_usetext = BoolProperty(
		name		= 'Load model settings',
		description = 'Generate a text object to preserve model settings, like shading',
		default	    = True,
	)
	
	def execute(self, context):
		paths = [os.path.join(self.directory, name.name) for name in self.files]
		keywords = {
			'usebitmaps': self.md2_usebitmaps,
			'use_text'  : self.md2_usetext,
		}
		if not paths: paths.append(self.filepath)
		from . import import_atd
		for path in paths:
			import_atd.open_atd(path, **keywords)
		return {'FINISHED'}
		
class ExportATD(bpy.types.Operator, ExportHelper):
	"""Export an Attention To Detail .MD2 file"""
	bl_idname = "export_mesh.atd"
	bl_label = "Export Attention To Detail .MD2"

	filename_ext = ".md2"
	filter_glob = StringProperty(default="*.md2", options={'HIDDEN'})
	
	md2_version = EnumProperty(
		name		= 'Version',
		description = 'Keep this at default (MDL2) if unsure. For testing purposes',
		items	    = (
			('MDL2', 'MDL2', ''),
			('MDL1', 'MDL1', ''),
			('MDL0', 'MDL0', ''),
		)
	)
	
	md2_usetext = BoolProperty(
		name		= 'Use model settings',
		description = 'Use the model text object for options including shading',
		default	    = True,
	)

	def execute(self, context):
		from . import export_atd
		keywords = {
			'version' : self.md2_version,
			'use_text': self.md2_usetext,
		}
		export_atd.write_atd(self.filepath, **keywords)
		return {'FINISHED'}
		
def menu_func_import(self, context):
	self.layout.operator(ImportATD.bl_idname, text="Attention To Detail (.md2)")
def menu_func_export(self, context):
	self.layout.operator(ExportATD.bl_idname, text="Attention To Detail (.md2)")
def register():
	bpy.utils.register_class(ImportATD)
	bpy.utils.register_class(ExportATD)
	bpy.types.INFO_MT_file_import.append(menu_func_import)
	bpy.types.INFO_MT_file_export.append(menu_func_export)
def unregister():
	bpy.utils.unregister_class(ImportATD)
	bpy.utils.unregister_class(ExportATD)
	bpy.types.INFO_MT_file_import.remove(menu_func_import)
	bpy.types.INFO_MT_file_export.remove(menu_func_export)
if __name__ == "__main__": register()