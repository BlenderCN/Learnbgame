bl_info = {
	"name": "Game To Blender Format",
	"author": "Qing Guo",
	"blender": (2, 76, 0),
	"location": "File > Import-Export",
	"description": "Import GTB files.",
	"warning": "",
	"category": "Learnbgame",
}

# To support reload properly, try to access a package var,
# if it's there, reload everything
if "bpy" in locals():
	import importlib
	if "gtb_importer" in locals():
		importlib.reload(gtb_importer)
		
import os
import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import (CollectionProperty, StringProperty, BoolProperty, EnumProperty, FloatProperty)
		
class ImportGTB(bpy.types.Operator, ImportHelper):
	"""Load a GTB mesh file."""
	bl_idname = "import_mesh.gtb"
	bl_label = "Import GTB model"
	bl_options = {'UNDO'}

	files = CollectionProperty(name="File Path",
						  description="File path used for importing the GTB mesh file",
						  type=bpy.types.OperatorFileListElement)

	directory = StringProperty()

	filename_ext = ".gtb"
	filter_glob = StringProperty(default="*.gtb", options={'HIDDEN'})
	armat_name = StringProperty(default="armat")

	bone_length = FloatProperty(
		name="Bone Length",
		description="Bone length for determining the position of the bone tail",
		min=0.0, max=1000.0,
		soft_min=0.0, soft_max=1000.0,
		default=10.0)
	
	def execute(self, context):
		path = os.path.join(self.directory, self.files[0].name)

		from . import gtb_importer
		if self.bone_length > 0:
			gtb_importer.BONE_LENGTH = self.bone_length
		gtb_importer.ARMAT_NAME = self.armat_name
		
		gtb_importer.import_gtb(path)

		return {'FINISHED'}

class ImportGTBA(bpy.types.Operator, ImportHelper):
	"""Load a GTB animation file."""
	bl_idname = "import_animation.gtb"
	bl_label = "Import GTB animation"
	bl_options = {'UNDO'}

	files = CollectionProperty(name="File Path",
						  description="File path used for importing the GTB animation file",
						  type=bpy.types.OperatorFileListElement)

	directory = StringProperty()

	filename_ext = ".gtba"
	filter_glob = StringProperty(default="*.gtba", options={'HIDDEN'})

	rotation_resample = BoolProperty(
		name="Resample Rotation",
		description="Resample Rotation using slerp to ensure 100% correctness.",
		default=True)
	
	def execute(self, context):
		armature = None
		for obj in context.selected_objects:
			if obj.get("bone_mapping"):
				armature = obj
				break
		
		if armature is None:
			self.report({'ERROR'}, "No GTB armature is selected!")
			return {'FINISHED'}
		
		path = os.path.join(self.directory, self.files[0].name)

		from . import gtba_importer
		gtba_importer.import_gtba(path, armature, self.rotation_resample)

		return {'FINISHED'}
	
def menu_func_import(self, context):
	self.layout.operator(ImportGTB.bl_idname, text="Game To Blender Mesh (.gtb)")
	self.layout.operator(ImportGTBA.bl_idname, text="Game To Blender Animation (.gtba)")
		
def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_import.append(menu_func_import)
	bpy.types.Action.target_user = bpy.props.StringProperty()
	
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_import.remove(menu_func_import)
	del bpy.types.Action.target_user

if __name__ == '__main__':
	register()