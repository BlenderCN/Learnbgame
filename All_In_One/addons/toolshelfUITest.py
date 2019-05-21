import bpy

# Meta information.
bl_info = {
	"name": "Serial Communication",
	"author": "James",
	"version": (1, 0),
	"blender": (2, 79),
	"location": "Object > Serial",
	"description": "Add Serial",
	"warning": "",
	"support": "TESTING",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Object"
}

 
# Operation.
class CreateSerial(bpy.types.Operator):

	bl_idname = "object.create_serial"  # Access the class by bpy.ops.object.create_serial.
	bl_label = "Start Serial"
	bl_description = "Add Serial Object"
	bl_options = {'REGISTER', 'UNDO'}
	 
	# Input property-------------------
	# xyz vector values.：

	
	'''
	#TEMPLATING
	# Select box.
	select_box = bpy.props.EnumProperty(
		name = "Select box",
		description = "Set select box",
		# [(ID, name, description)]
		items = [('3D_CURSOR', "3D cursor", "Locate on 3D cursor"),
				('ORIGIN', "origin", "Locate on origin")]
	)
	# A check box.
	check_box = bpy.props.BoolProperty(
		name = "Check box",
		description = "Set check box"
	)
	# xyz check box.
	xyz_check_box = bpy.props.BoolVectorProperty(
		name = "XYZ check box",
		description = "Set XYZ check box",
		default = [True, True, False],
		subtype = "XYZ" # Set xyz check box
	)
	'''
	# -----------------------------------------
 
	# Execute function.
	def execute(self, context):
		
		#context.scene.[varname] to access vars from tool shelf.

		#self.[varname] to access vars from this class above.
		'''
		bpy.ops.mesh.primitive_ico_sphere_add()
		active_obj = context.active_object
		# Input before execute on the left tool shelf.
		active_obj.scale = active_obj.scale * context.scene.float_input
		# Input after execute on the left below panel.
		active_obj.location = active_obj.location + self.float_vector_input # 
		'''
		print("Executed CreateSerial class")
		return {'FINISHED'}
 

class StopSerial(bpy.types.Operator):

	bl_idname = "object.stop_serial"  # Access the class by bpy.ops.object.create_serial.
	bl_label = "Stop Serial"
	bl_description = "Close Serial Port"
	bl_options = {'REGISTER', 'UNDO'}
	 

	def execute(self, context):
		print("Executed Stop Serial class")
		return {'FINISHED'}


# Menu setting.
class CreateSerialPanel(bpy.types.Panel):
	bl_label = "CREATE Serial"
	bl_idname = "create_serial" # class ID.
	bl_space_type = "VIEW_3D"	# Menu accessible from 3D viewport
	bl_region_type = "TOOLS" 	# Menu lives in the left tool shelf.
	bl_category = "Serial" 		# Create new tab for Serial!
	bl_context = (("objectmode"))
	 
	# Menu and input:
	def draw(self, context):
		obj = context.object
		scene = context.scene

		layout = self.layout

		row = layout.row()
		row.label("Serial Port")
		row.prop(scene, "serial_port") # Input button for bpy.types.Scene.float_input.

		row = layout.row()
		row.label("Baud Rate")
		row.prop(scene, "serial_baud")

		row = layout.row()
		row.label("Separator")
		row.prop(scene, "serial_separator")

		row = layout.row()
		row.label("Read Until")
		row.prop(scene, "serial_read_until")

		#No need for box at this time
		#box = layout.box()
		#box.label("Box menu")
		#box.operator("object.select_all").action = 'TOGGLE' # Select all button.
		#box.operator("object.select_random") # Random select button.
		# Execute button for CreateSerial.

		layout.operator(CreateSerial.bl_idname)
		layout.operator(StopSerial.bl_idname)
 
def register():
	bpy.utils.register_module(__name__)
	# bpy.types.Scene~　＝　To show the input in the left tool shelf, store "bpy.props.~".
	#   In draw() in the subclass of Panel, access the input value by "context.scene".
	#   In execute() in the class, access the input value by "context.scene.float_input".
	bpy.types.Scene.serial_port = bpy.props.StringProperty(
		name = "Serial Port",
		description = "Set test float",
		default = "COM4"
	)

	bpy.types.Scene.serial_baud =  bpy.props.IntProperty(
		name = "Baud Rate",
		description = "Set Baud Rate",
		default = 9600
	)

	bpy.types.Scene.serial_separator = bpy.props.StringProperty(
		name = "Data Separator",
		description = "What character separates your incoming data?",
		default = ","
	)

	bpy.types.Scene.serial_read_until = bpy.props.StringProperty(
		name = "Read Until character",
		description = "What character delimits a new data block?",
		default = "\n"
	)

	print("This add-on was activated.")
 
def unregister():
	del bpy.types.Scene.serial_port
	bpy.utils.unregister_module(__name__)
	print("This add-on was deactivated.")
 
if __name__ == "__main__":
	register()