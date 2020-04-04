bl_info = {
	"name": "Targetable Cameras and Lights",
	"author": "Kenetics",
	"version": (0, 2),
	"blender": (2, 80, 0),
	"location": "View3D > Add Menu",
	"description": "Adds targetable cameras and lights",
	"warning": "",
	"wiki_url": "",
	"category": "Learnbgame",
}

import bpy
from bpy.props import EnumProperty, IntProperty, FloatVectorProperty, BoolProperty, FloatProperty, StringProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add

# Helper Functions
def add_track_constraint(obj, target):
	track_constraint = obj.constraints.new('TRACK_TO')
	track_constraint.target = target
	track_constraint.track_axis = 'TRACK_NEGATIVE_Z'
	track_constraint.up_axis = 'UP_Y'

def create_empty_and_track_constraint(context, obj, target_name):
	"Adds empty, adds tracking constraint to obj, and returns the created empty"
	# Create target
	target = context.blend_data.objects.new(target_name, None)
	# Link target
	context.collection.objects.link(target)
	# Bind constraint to obj
	add_track_constraint(obj, target)
	
	# Return target
	return target

def deselect_all_objects(context):
	for obj in context.selected_objects:
		obj.select_set(False)


# Main Classes
class TCL_OT_add_target_camera(bpy.types.Operator):
	"""Adds a camera and target empty to the scene"""
	bl_idname = "object.tcl_ot_add_target_camera"
	bl_label = "Add Targetable Camera"
	bl_options = {'REGISTER','UNDO'}
	
	# Properties
	name : StringProperty(
		name="Name",
		description="Name for camera and camera target",
		default="TargetCamera"
	)
	
	use_cursor_loc : BoolProperty(
		name="Use 3D cursor location",
		description="If on, sets camera at 3D cursor, else sets at (0,0,0)",
		default=True
	)
	
	use_active_obj_loc : BoolProperty(
		name="Use active object location",
		description="If on, sets empty at active object, else sets at (0,0,0)",
		default=True
	)	
	
	cam_loc : FloatVectorProperty(
		name = "Camera Location",
		description="Modfies camera's location",
		subtype='XYZ'
	)
	
	target_loc : FloatVectorProperty(
		name = "Target Location",
		description="Modfies target's location",
		subtype='XYZ',
		default=(0,0,0)
	)

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		# Create camera
		cam_data = context.blend_data.cameras.new("TargetCamera")
		cam_obj = context.blend_data.objects.new(self.name, cam_data)
		
		cam_loc = context.scene.cursor.location.copy() + self.cam_loc if self.use_cursor_loc else self.cam_loc
		cam_obj.location = cam_loc
		
		context.collection.objects.link(cam_obj) # Active Collection
		
		# Create target
		target = create_empty_and_track_constraint(context, cam_obj, self.name + "Target")
		
		if self.use_active_obj_loc and context.active_object is not None:
			target_loc = context.active_object.location.copy() + self.target_loc
		else:
			target_loc = self.target_loc
		target.location = target_loc
		
		# Set Target as camera dof target
		cam_data.dof_object = target
		
		deselect_all_objects(context)
		cam_obj.select_set(True)
		target.select_set(True)
		context.view_layer.objects.active = cam_obj
		
		return {'FINISHED'}


class TCL_OT_add_target_light(bpy.types.Operator):
	"""Adds a light and target empty to the scene"""
	bl_idname = "object.tcl_ot_add_target_light"
	bl_label = "Add Targetable Light"
	bl_options = {'REGISTER','UNDO'}
	
	# Properties
	light_type : EnumProperty(
		items=[
			("SPOT","Spot","","LIGHT_SPOT",0),
			("AREA","Area","","LIGHT_AREA",1),
			("SUN","Sun","","LIGHT_SUN",2)
			],
		name="Light Type",
		description="Type of light to create",
		default="SPOT"
	)
	
	name : StringProperty(
		name="Name",
		description="Name for light and light target",
		default="TargetLight"
	)
	
	use_cursor_loc : BoolProperty(
		name="Use 3D cursor location",
		description="If on, sets camera at 3D cursor, else sets at (0,0,0)",
		default=True
	)
	
	use_active_obj_loc : BoolProperty(
		name="Use active object location",
		description="If on, sets empty at active object, else sets at (0,0,0)",
		default=True
	)
	
	light_loc : FloatVectorProperty(
		name = "Light Location",
		description="Modfies light's location",
		subtype='XYZ'
	)
	
	target_loc : FloatVectorProperty(
		name = "Target Location",
		description="Modfies target's location",
		subtype='XYZ',
		default=(0,0,0)
	)

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		# Create Light
		light_data = context.blend_data.lights.new("TargetLight", self.light_type)
		light_obj = context.blend_data.objects.new(self.name, light_data)
		# Set light location
		if self.use_cursor_loc:
			light_obj.location = context.scene.cursor.location.copy() + self.light_loc
		else:
			light_obj.location = self.light_loc
		# Link light
		context.collection.objects.link(light_obj)
		# Create target
		target = create_empty_and_track_constraint(context, light_obj, self.name + "Target")
		# Set target location
		if self.use_active_obj_loc and context.active_object is not None:
			target.location = context.active_object.location + self.target_loc
		else:
			target.location = self.target_loc
		
		deselect_all_objects(context)
		light_obj.select_set(True)
		target.select_set(True)
		context.view_layer.objects.active = light_obj
		
		return {'FINISHED'}


class TCL_OT_add_target_to_cameras_lights(bpy.types.Operator):
	"""Adds a track target empty to selected cameras/lights"""
	bl_idname = "object.tcl_ot_add_target_to_cameras_lights"
	bl_label = "Add Target to Selected Cameras/Lights"
	bl_options = {'REGISTER','UNDO'}
	
	# Properties
	name : StringProperty(
		name="Name",
		description="Name for camera/light target",
		default="Target"
	)
	
	set_camera_dof_target : BoolProperty(
		name="Set Camera DOF Target",
		description="If on, sets selected cameras' DOF target",
		default=True
	)
	
	use_cursor_loc : BoolProperty(
		name="Use 3D cursor location",
		description="If on, sets target at 3D cursor, else sets at (0,0,0)",
		default=True
	)
	
	location : FloatVectorProperty(
		name = "Target Location",
		description="Modfies target's location",
		subtype='XYZ',
		default=(0,0,0)
	)

	@classmethod
	def poll(cls, context):
		for obj in context.selected_objects:
			if obj.type == "CAMERA" or obj.type == "LIGHT":
				return True
		
		return False

	def execute(self, context):
		selected_cam_light_objs = tuple(obj for obj in context.selected_objects if obj.type == 'LIGHT' or obj.type == 'CAMERA')
		
		target = context.blend_data.objects.new(self.name, None)
		context.collection.objects.link(target)
		target.select_set(True)
		
		if self.use_cursor_loc:
			target.location = context.scene.cursor.location.copy() + self.location
		else:
			target.location = self.location
		
		# Bind constraint to lights
		for obj in selected_cam_light_objs:
			track_constraint = None
			
			for constraint in obj.constraints:
				if constraint.type == "TRACK_TO":
					track_constraint = constraint
					break
			
			if track_constraint is None:
				add_track_constraint(obj, target)
			else:
				track_constraint.target = target
			
			if self.set_camera_dof_target and obj.type == "CAMERA":
				obj.data.dof_object = target
		
		return {'FINISHED'}
	
	
class TCL_OT_select_linked_target(bpy.types.Operator):
	"""Selects targets of selected lights/cameras"""
	bl_idname = "object.tcl_ot_select_linked_target"
	bl_label = "Select Linked Camera/Light Targets"
	bl_options = {'REGISTER','UNDO'}
	
	#Properties
	extend : BoolProperty(
		name="Extend",
		description="If enabled, extends current selection.",
		default=True
	)
	
	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		if self.extend:
			selected_cam_light_objects = tuple(obj for obj in context.selected_objects if obj.type == 'CAMERA' or obj.type == 'LIGHT')
		else:
			selected_cam_light_objects = tuple(obj for obj in context.selected_objects if obj.type == 'CAMERA' or obj.type == 'LIGHT')
			for obj in context.selected_objects:
				obj.select_set(False)
		
		for obj in selected_cam_light_objects:
			track_constraint = None
			
			for constraint in obj.constraints:
				if constraint.type == "TRACK_TO":
					track_constraint = constraint
					break
			
			if track_constraint is not None and constraint.target is not None:
				constraint.target.select_set(True)
		
		return {'FINISHED'}


class TCL_OT_select_linked_target_cameras_lights(bpy.types.Operator):
	"""Selects cameras/lights of selected targets"""
	bl_idname = "object.tcl_ot_select_linked_target_cameras_lights"
	bl_label = "Select Linked Target Cameras/Lights"
	bl_options = {'REGISTER','UNDO'}
	
	#Properties
	extend : BoolProperty(
		name="Extend",
		description="If enabled, extends current selection.",
		default=True
	)
	
	select_type : EnumProperty(
		items=[
			("BOTH","Both","","",0),
			("CAMERA","Only Cameras","","OUTLINER_OB_CAMERA",1),
			("LIGHT","Only Lights","","OUTLINER_OB_LIGHT",2)
			],
		name="Select Type",
		description="Type of object to select",
		default="BOTH"
	)
	
	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		if self.select_type == "BOTH":
			scene_cam_light_objects = tuple(obj for obj in context.scene.objects if obj.type == 'CAMERA' or obj.type == 'LIGHT')
		elif self.select_type == "CAMERA":
			scene_cam_light_objects = tuple(obj for obj in context.scene.objects if obj.type == 'CAMERA')
		else:
			scene_cam_light_objects = tuple(obj for obj in context.scene.objects if obj.type == 'LIGHT')
		
		if self.extend:
			selected_objects = context.selected_objects
		else:
			selected_objects = tuple(context.selected_objects)
			for obj in selected_objects:
				obj.select_set(False)
		
		for obj in scene_cam_light_objects:
			for constraint in obj.constraints:
				if constraint.type == "TRACK_TO" and constraint.target in selected_objects:
					obj.select_set(True)
					break
		
		return {'FINISHED'}


# Menus
def add_target_light_menu(self, context):
    self.layout.operator_menu_enum(TCL_OT_add_target_light.bl_idname, 'light_type', text="Targetable Light", icon='OUTLINER_OB_LIGHT')

def add_target_camera_menu(self, context):
	self.layout.operator(TCL_OT_add_target_camera.bl_idname, text="Targetable Camera", icon='OUTLINER_OB_CAMERA')

def add_target_to_cameras_lights_button(self, context):
	self.layout.operator(TCL_OT_add_target_to_cameras_lights.bl_idname, icon="PIVOT_CURSOR")

def select_camera_light_target_button(self, context):
	self.layout.operator(TCL_OT_select_linked_target.bl_idname, icon="PIVOT_CURSOR")
	self.layout.operator(TCL_OT_select_linked_target_cameras_lights.bl_idname, icon="OUTLINER_OB_CAMERA")

def select_camera_light_target_button_specials(self, context):
	obj = context.object
	if (obj is not None) and (obj.type == "CAMERA" or context.active_object.type == "LIGHT"):
		self.layout.operator(TCL_OT_select_linked_target.bl_idname, icon="PIVOT_CURSOR")

classes = (
	TCL_OT_add_target_camera,
	TCL_OT_add_target_light,
	TCL_OT_add_target_to_cameras_lights,
	TCL_OT_select_linked_target,
	TCL_OT_select_linked_target_cameras_lights
)

# Register
def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	bpy.types.VIEW3D_MT_light_add.append(add_target_light_menu)
	bpy.types.VIEW3D_MT_camera_add.append(add_target_camera_menu)
	bpy.types.VIEW3D_MT_select_object.append(select_camera_light_target_button)
	bpy.types.VIEW3D_MT_object_context_menu.append(select_camera_light_target_button_specials)
	bpy.types.VIEW3D_MT_add.append(add_target_to_cameras_lights_button)

def unregister():
	bpy.types.VIEW3D_MT_add.remove(add_target_to_cameras_lights_button)
	bpy.types.VIEW3D_MT_object_context_menu.remove(select_camera_light_target_button_specials)
	bpy.types.VIEW3D_MT_select_object.remove(select_camera_light_target_button)
	bpy.types.VIEW3D_MT_camera_add.remove(add_target_camera_menu)
	bpy.types.VIEW3D_MT_light_add.remove(add_target_light_menu)
	
	for cls in classes[::-1]:
		bpy.utils.unregister_class(cls)

if __name__ == "__main__":
	register()
