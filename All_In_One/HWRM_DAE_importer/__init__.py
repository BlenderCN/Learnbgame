# version 1.0.1
# added visual mesh option
# added split normals option
# added dock seg draw type option
# fixed image names
# fixed nav light names
# fixed dock parameter names

bl_info = {
	"name": "HWRM DAE importer",
	"author": "Dom2, DKesserich",
	"version": (1, 0, 1),
	"blender": (2, 76, 0),
	"location": "File > Import-Export > Dae",
	"description": "Import HWRM DAE files",
	"category": "Learnbgame",
}


if "bpy" in locals():
	print("bpy is in locals()")
	import imp
	if "import_dae" in locals():
		print("import_dae in locals(), attempting to reload...")
		imp.reload(import_dae)
	else:
		print("import_dae not in locals(), attempting to import...")
		from . import import_dae
else:
	print("bpy not in locals(), attempting to import import_dae...")
	from . import import_dae

import os
import bpy
import bpy_extras

class ImportDAE(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
	"""Import HWRM DAE"""
	bl_idname = "import_scene.dae"
	bl_label = "Import HWRM DAE"
	bl_options = {'UNDO'}

	filename_ext = ".dae"

	filter_glob = bpy.props.StringProperty(
			default="*.dae",
			options={'HIDDEN'},
			)
	files = bpy.props.CollectionProperty(
			name="File Path",
			type=bpy.types.OperatorFileListElement,
			)
	directory = bpy.props.StringProperty(
			subtype='DIR_PATH',
			)

	import_as_visual_mesh = bpy.props.BoolProperty(
			name="Import as visual mesh",
			description="Import LOD[0] only as visual mesh",
			default=False,
			)
			
	merge_goblins = bpy.props.BoolProperty(
			name="Merge goblins",
			description="Merge goblins into LOD[0] mesh",
			default=False,
			)

	use_smoothing = bpy.props.BoolProperty(
			name="Split normals",
			description="Sometimes splitting normals causes Crash To Desktop for unknown reasons. If you get CTD, try turning this off...",
			default=True,
			)
	
	dock_path_vis = bpy.props.EnumProperty(
            name="Display dock segments as ",
            items=(('CONE', "Cone", ""),
                   ('SPHERE', "Sphere", ""),
				   ('CUBE', "Cube", ""),
				   ('CIRCLE', "Circle", ""),
                   ('SINGLE_ARROW', "Single Arrow", ""),
				   ('ARROWS', "Arrows", ""),
				   ('PLAIN_AXES', "Plain Axes", ""),
                   ),
            default='SPHERE',
            )

	def execute(self, context):
		print("Executing HWRM DAE import")
		print(self.filepath)
		from . import import_dae # re-import, just in case!
		if self.import_as_visual_mesh:
			print("Importing visual mesh only...")
			import_dae.ImportLOD0(self.filepath, self.use_smoothing)
		else:
			import_dae.ImportDAE(self.filepath, self.use_smoothing, self.dock_path_vis, self.merge_goblins)
		return {'FINISHED'}

def menu_import(self, context):
	self.layout.operator(ImportDAE.bl_idname, text="HWRM DAE (.dae)")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_import.append(menu_import)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_import.remove(menu_import)

if __name__ == "__main__":
	register()
