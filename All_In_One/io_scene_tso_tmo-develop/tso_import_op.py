
"""tso import operator
"""

import bpy
from bpy_extras.io_utils import ImportHelper
from io_scene_tso_tmo import tso_import

class TsoImportOperator(bpy.types.Operator, ImportHelper):
	bl_idname = "import_scene.tso"

	bl_label = "Import TSO"

	filename_ext = ".tso"
	filter_glob = bpy.props.StringProperty(default="*.tso", options={'HIDDEN'})

	def execute(self, context):
		source_file = self.properties.filepath
		tso_import.import_tsofile(source_file)
		return {'FINISHED'}

