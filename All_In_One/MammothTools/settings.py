import bpy
from bpy.props import *
from bpy.types import PropertyGroup

from . import components

class MammothComponents(PropertyGroup):
	def definitions_path_updated(self, context):
		components.unload()
		components.loadLayout(self.definitions_path)
		components.load()
		
	definitions_path = StringProperty(
		name="definitions_path",
		description="Path to the component descriptions file",
		default="*.json",
		options={'HIDDEN'},
		maxlen=1024,
		subtype='FILE_PATH',
		update=definitions_path_updated
	)