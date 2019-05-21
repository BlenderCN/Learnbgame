bl_info = {
	"name": "Importjson",
	"author": "Your Name Here",
	"version": (1, 0),
	"blender": (2, 75, 0)
	}

import json
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty


import bpy

def read_settings_data_testing(context, filepath):
	print("running read_settings_data...")
	f = open(filepath, 'r', encoding='utf-8')
	#data = f.read()
	data = json.load(f)
	f.close()
	for obj in data['Objects']:
		print(obj['Name'])
	# print(objs)
	# settings = []
	# for line in f:
	# 	# settings.append(f.readline())
	# 	settings.append(line.split(" ", 1)[0])
	# # print(settings)
	# f.close()

	return {'FINISHED'}


class ImportBrenderSettingsJSON(Operator, ImportHelper):
	"""This appears in the tooltip of the operator and in the generated docs"""
	bl_idname = "import_brend.settings_data_json"  # important since its how bpy.ops.import_brend.settings_data is constructed
	bl_label = "Import Brender Settings JSON"

	# ImportHelper mixin class uses this
	filename_ext = ".json"

	filter_glob = StringProperty(
			default="*.json",
			options={'HIDDEN'},
			maxlen=255,  # Max internal buffer length, longer would be clamped.
			)


	def execute(self, context):
		scene = context.scene
		# myaddon = scene.my_addon
		return read_settings_data_testing(context, self.filepath)

		# return{'FINISHED'}



def register():
	bpy.utils.register_class(ImportBrenderSettingsJSON)


def unregister():
	bpy.utils.unregister_class(ImportBrenderSettingsJSON)


if __name__ == "__main__":
	register()