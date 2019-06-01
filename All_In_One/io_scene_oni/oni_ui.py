from bpy_extras.io_utils import (
	ExportHelper,
	ImportHelper,
	)
from bpy.props import (
	BoolProperty,
	CollectionProperty,
	EnumProperty,
	FloatProperty,
	FloatVectorProperty,
	IntProperty,
	StringProperty,
	PointerProperty,
	)
from bpy.types import (
	Operator,
	PropertyGroup,
	Panel,
	Armature,
	Bone,
	Mesh,
	Material,
	Action,
	Group,
	UIList,
	Scene
	)
from bpy.utils import (
	register_class,
	unregister_class,
	)
import io_scene_oni

###############################################################################
class OniImportOperator(Operator, ImportHelper):
	""" Load a Oni .dat file """
	bl_idname = 'import_scene.oni'
	bl_label = 'Import Oni'
	bl_description = 'Import from Oni data file (.dat)'
	bl_options = {'PRESET'}
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'

	filepath = StringProperty(
		subtype='FILE_PATH',
		options={'HIDDEN', }
		)

	filename_ext = StringProperty(
		default='.dat',
		options={'HIDDEN', }
		)

	filter_glob = StringProperty(
		default='*.dat',
		options={'HIDDEN', }
		)

	use_extended_normal_handling = BoolProperty(
		name='Extended Normal Handling',
		description='adds extra vertices if normals are different',
		default=False,
		)

	def draw(self, blender_context):
		layout = self.layout
		box = layout.box()
		box.label('Object Processing:', icon='OBJECT_DATAMODE')
		box.prop(self, 'use_extended_normal_handling', icon='SPEAKER')

	def execute(self, blender_context):
		""" start executing """
		Scene.oni_props.gdf = self.filepath
		return {"FINISHED"}

	def invoke(self, blender_context, event):
		blender_context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL', }

	@staticmethod
	def menu_func(cls, blender_context):
		cls.layout.operator(
			OniImportOperator.bl_idname,
			text='Oni (.dat)',
			)


###############################################################################

class DialogOperator(Operator):
	bl_idname = "object.dialog_operator"
	bl_label = "Simple Dialog Operator"
	
	my_float = FloatProperty(name="Some Floating Point")
	my_bool = BoolProperty(name="Toggle Option")
	my_string = StringProperty(name="String Value")
	
	def execute(self, context):
		message = "Popup Values: %f, %d, '%s'" % \
		(self.my_float, self.my_bool, self.my_string)
		self.report({'INFO'}, message)
		return {'FINISHED'}
	
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)

class OniPanel(Panel):
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_idname = "VIEW3D_PT_test_1"
	bl_label = "Oni Importer"

	x = StringProperty(
			name="GDFolder",
			description="Path to ONI GameDataFolder",
			maxlen = 1024,
			default = "123")
	
	@classmethod
	def poll(cls, context):
		return (context.object is not None)
	
	def draw(self, context):
		layout = self.layout		
		obj = context.object

		row = layout.row()
		row.prop(self, "x")
		#row.prop(OniProperties, "gdf")

		"""
		#for x in OniProperties:
		#	print(x)
		print(OniProperties)
		print(OniProperties.gdf)
		

		row.label(text="GDFolder: ")
		#row.operator("import_scene.oni", text="Change")
		row = layout.row()
		row.label(text=Scene.oni_props.gdf)

		row = layout.row()
		row.label(text="Files: ")
		row = layout.row()
		row.template_ID(context.scene.objects, "active")

		row = layout.row()
		row.label(text="Meshes: ")
		row = layout.row()
		row.template_ID(context.scene.objects, "active")
	
		row = layout.row()
		row.operator("object.dialog_operator")
		"""


###############################################################################
class OniProperties(PropertyGroup):
	@classmethod
	def register(cls):
		cls.gdf = StringProperty(
			name="GDFolder",
			description="Path to ONI GameDataFolder",
			maxlen = 1024,
			default = "")

		Scene.oni_props = PointerProperty(type=cls, name="Oni", description="Oni Settings")

	@classmethod
	def unregister(cls):
		del Scene.oni_props

###############################################################################

def register():
	register_class(OniProperties)
	register_class(DialogOperator)
	register_class(OniPanel)

def unregister():
	unregister_class(OniPanel)
	unregister_class(DialogOperator)
	unregister_class(OniProperties)