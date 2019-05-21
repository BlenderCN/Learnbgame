
"""tmo import operator
"""

import os
import bpy
from bpy_extras.io_utils import ImportHelper
from io_scene_tso_tmo import tmo_import

class TmoImportOperator(bpy.types.Operator, ImportHelper):
	bl_idname = "import_scene.tmo"

	bl_label = "Import TMO"

	filename_ext = ".tmo"
	filter_glob = bpy.props.StringProperty(default="*.tmo", options={'HIDDEN'})

	def execute(self, context):
		source_file = self.properties.filepath
		ref_file = os.path.dirname(__file__) + "/resources/base-defo.tmo"
		tmo_import.import_tmofile(source_file, ref_file)
		return {'FINISHED'}

