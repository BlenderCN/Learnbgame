bl_info = {
	"name": "Modifier Empties",
	"author": "Kenetics",
	"version": (0, 2),
	"blender": (2, 80, 0),
	"location": "View 3D > Add Menu > Modifier Empties",
	"description": "Adds modifiers to selected objects and creates empties to control the modifiers.",
	"warning": "Modifier Empties can only be added in Object mode",
	"wiki_url": "",
	"category": "Learnbgame",
}

import bpy
from bpy.props import EnumProperty, IntProperty, FloatVectorProperty, BoolProperty, FloatProperty, StringProperty
from math import pi

def createEmpty(context, name, location, rotation, scale, parent=None):
	"""Creates empty with name, location, and rotation"""
	empty = context.blend_data.objects.new(name, None)
	
	if parent is not None:
		empty.parent = parent
		empty.matrix_parent_inverse = parent.matrix_world.inverted()
	
	empty.location = location
	empty.rotation_euler = rotation
	empty.scale = scale
	context.collection.objects.link(empty)
	return empty


class ME_OT_AddRadialArrayEmptyOperator(bpy.types.Operator):
	"""Adds an empty controlled radial array to all selected objects."""
	bl_idname = "object.me_ot_add_radial_array_empty"
	bl_label = "Add Radial Array Empty"
	bl_options = {'REGISTER','UNDO'}

	# Properties
	array_count : IntProperty(
		name="Array count",
		description="Total amount of objects",
		default=2,
		min=1
	)
	
	use_cursor_loc : BoolProperty(
		name="Use 3D cursor location",
		description="If on, sets empty at 3D cursor, else uses active object's location",
		default=False
	)
	
	location_modify : FloatVectorProperty(
		name = "Translation",
		description="Modfies empty's location",
		subtype='XYZ'
	)
	
	set_axis : EnumProperty(
		items=[
			("0","X","X axis","COLOR_RED",0),
			("1","Y","Y axis","COLOR_GREEN",1),
			("2","Z","Z axis","COLOR_BLUE",2)
			],
		name="Spin Axis",
		description="Axis which the array modifier spins around",
		default="2"
	)
	
	scale_modify : FloatVectorProperty(
		name = "Scale Relative",
		description="Modfies empty's relative scale",
		default=(1.0,1.0,1.0),
		subtype='XYZ'
	)
	
	make_parent : BoolProperty(
		name="Parent empty",
		description="If on, sets object as empty's parent.'",
		default=True
	)
	
	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.mode == 'OBJECT'

	def execute(self, context):
		active_obj = context.active_object
		axis = int(self.set_axis)
		array_count = self.array_count
		use_cursor_loc = self.use_cursor_loc
		
		# Copy loc, rot, and scale so source doesn't get changed
		empty_location = context.scene.cursor.location.copy() if use_cursor_loc else active_obj.location.copy()
		empty_location += self.location_modify
		
		empty_rotation = active_obj.rotation_euler.copy()
		empty_rotation[axis] += 0 if array_count == 1 else (pi*2)/array_count
		
		empty_scale = active_obj.scale.copy()
		for i in range(0,3):
			empty_scale[i] *= self.scale_modify[i]
		
		empty_name = active_obj.name + "ArrayEmpty"
		
		parent = None
		if self.make_parent:
			parent = active_obj
		
		empty = createEmpty(context, empty_name, empty_location, empty_rotation, empty_scale, parent)
		
		#bpy.context.scene.update()
		context.scene.update()
		
		for obj in context.selected_objects:
			array_mod = obj.modifiers.new("EmptyOffsetArray", "ARRAY")
			array_mod.offset_object = empty
			array_mod.use_object_offset = True
			array_mod.use_relative_offset = False
			array_mod.count = array_count
		
		return {'FINISHED'}


class ME_OT_AddArrayEmptyOperator(bpy.types.Operator):
	"""Adds an empty controlled array to all selected objects."""
	bl_idname = "object.me_ot_add_array_empty"
	bl_label = "Add Array Empty"
	bl_options = {'REGISTER','UNDO'}

	# Properties
	array_count : IntProperty(
		name="Array count",
		description="Total amount of objects",
		default=2,
		min=1
	)
	
	use_cursor_loc : BoolProperty(
		name="Use 3D cursor location",
		description="If on, sets empty at 3D cursor, else uses active object's location",
		default=False
	)
	
	location_modify : FloatVectorProperty(
		name = "Translation",
		description="Modfies empty's location",
		subtype='XYZ'
	)
	
	rotation_modify : FloatVectorProperty(
		name = "Rotation",
		description="Modfies empty's rotation",
		subtype='EULER',
		unit='ROTATION'
	)
	
	scale_modify : FloatVectorProperty(
		name = "Scale Relative",
		description="Modfies empty's relative scale",
		default=(1.0,1.0,1.0),
		subtype='XYZ'
	)
	
	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.mode == 'OBJECT'

	def execute(self, context):
		active_obj = context.active_object
		array_count = self.array_count
		use_cursor_loc = self.use_cursor_loc
		
		# Copy active_obj's attributes or they will be modified too
		empty_location = context.scene.cursor.location.copy() if use_cursor_loc else active_obj.location.copy()
		empty_location += self.location_modify
		
		empty_rotation = active_obj.rotation_euler.copy()
		empty_scale = active_obj.scale.copy()
		for i in range(0,3):
			empty_rotation[i] += self.rotation_modify[i]
			empty_scale[i] *= self.scale_modify[i]
		
		empty_name = active_obj.name + "ArrayEmpty"
		empty = createEmpty(context, empty_name, empty_location, empty_rotation, empty_scale)
		
		for obj in context.selected_objects:
			array_mod = obj.modifiers.new("EmptyOffsetArray", "ARRAY")
			array_mod.offset_object = empty
			array_mod.use_object_offset = True
			array_mod.use_relative_offset = False
			array_mod.count = array_count
		
		return {'FINISHED'}


class ME_OT_AddMirrorEmptyOperator(bpy.types.Operator):
	"""Adds an empty controlled mirror to all selected objects."""
	bl_idname = "object.me_ot_add_mirror_empty"
	bl_label = "Add Mirror Empty"
	bl_options = {'REGISTER','UNDO'}

	# Properties
	use_x : BoolProperty(
		name="X",
		description="Use X axis",
		default=True
	)

	use_y : BoolProperty(
		name="Y",
		description="Use Y axis",
		default=False
	)
	
	use_z : BoolProperty(
		name="Z",
		description="Use Z axis",
		default=False
	)
	
	clipping : BoolProperty(
		name="Clipping",
		description="Use clipping",
		default=False
	)
	
	use_cursor_loc : BoolProperty(
		name="Use 3D cursor location",
		description="If on, sets empty at 3D cursor, else uses active object's location",
		default=False
	)
	
	location_modify : FloatVectorProperty(
		name = "Translation",
		description="Modfies empty's location",
		subtype='XYZ'
	)
	
	rotation_modify : FloatVectorProperty(
		name = "Rotation",
		description="Modfies empty's rotation",
		subtype='EULER',
		unit='ROTATION'
	)
	
	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.mode == 'OBJECT'

	def execute(self, context):
		active_obj = context.active_object
		use_cursor_loc = self.use_cursor_loc
		
		# Copy active_obj's attributes or they will be modified too
		empty_location = context.scene.cursor.location.copy() if use_cursor_loc else active_obj.location.copy()
		empty_location += self.location_modify
		
		empty_rotation = active_obj.rotation_euler.copy()
		
		empty_scale = active_obj.scale.copy()
		
		for i in range(0,3):
			empty_rotation[i] += self.rotation_modify[i]
		
		empty_name = active_obj.name + "MirrorEmpty"
		empty = createEmpty(context, empty_name, empty_location, empty_rotation, empty_scale)
		
		for obj in context.selected_objects:
			mirror_mod = obj.modifiers.new("EmptyOffsetMirror", "MIRROR")
			mirror_mod.mirror_object = empty
			mirror_mod.use_axis[0] = self.use_x
			mirror_mod.use_axis[1] = self.use_y
			mirror_mod.use_axis[2] = self.use_z
			mirror_mod.use_clip = self.clipping
		
		return {'FINISHED'}
	
		
		
class ME_OT_AddCastEmptyOperator(bpy.types.Operator):
	"""Adds an empty controlled cast to all selected objects."""
	bl_idname = "object.me_ot_add_cast_empty"
	bl_label = "Add Cast Empty"
	bl_options = {'REGISTER','UNDO'}

	cast_type_items = (
		('SPHERE',"Sphere","Sphere shape",'META_BALL',0),
		('CYLINDER',"Cylinder","Cylinder shape",'META_CAPSULE',1),
		('CUBOID',"Cuboid","Cuboid shape",'META_CUBE',2)
	)
	
	#cast_types = tuple( i[0] for i in cast_type_items )
	
	# Properties
	use_x : BoolProperty(
		name="X",
		description="Use X axis",
		default=True
	)

	use_y : BoolProperty(
		name="Y",
		description="Use Y axis",
		default=True
	)
	
	use_z : BoolProperty(
		name="Z",
		description="Use Z axis",
		default=True
	)
	
	cast_type : EnumProperty(
		items=cast_type_items,
		name="Type",
		description="Cast shape",
		default='SPHERE'
	)
	
	factor : FloatProperty(
		name="Factor",
		description="How much of the effect should be applied",
		default=0.5
	)
	
	radius : FloatProperty(
		name="Radius",
		description="Only deform vertices within this distance from the center of the effect (leave as 0 for infinite.)"
	)
	
	use_radius_as_size : BoolProperty(
		name="Use radius as size",
		description="Use radius as size of projection shape",
		default=False
	)
	
	size : FloatProperty(
		name="Size",
		description="Size of projection shape (leave as 0 for auto)"
	)
	
	use_transform : BoolProperty(
		name="Use transform",
		description="Use empty's transform",
		default=True
	)
	
	use_cursor_loc : BoolProperty(
		name="Use 3D cursor location",
		description="If on, sets empty at 3D cursor, else uses active object's location",
		default=False
	)
	
	location_modify : FloatVectorProperty(
		name = "Translation",
		description="Modfies empty's location",
		subtype='XYZ'
	)
	
	rotation_modify : FloatVectorProperty(
		name = "Rotation",
		description="Modfies empty's rotation",
		subtype='EULER',
		unit='ROTATION'
	)
	
	scale_modify : FloatVectorProperty(
		name = "Scale Relative",
		description="Modfies empty's scale",
		subtype='XYZ',
		default=(1.0,1.0,1.0)
	)
	
	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.mode == 'OBJECT'

	def execute(self, context):
		active_obj = context.active_object
		use_cursor_loc = self.use_cursor_loc
		
		# Setup empty
		# Copy active_obj's attributes or they will be modified too
		empty_location = context.scene.cursor.location.copy() if use_cursor_loc else active_obj.location.copy()
		empty_location += self.location_modify
		
		empty_rotation = active_obj.rotation_euler.copy()
		
		empty_scale = active_obj.scale.copy()
		
		for i in range(0,3):
			empty_rotation[i] += self.rotation_modify[i]
			empty_scale[i] *= self.scale_modify[i]
		
		empty_name = active_obj.name + "CastEmpty"
		empty = createEmpty(context, empty_name, empty_location, empty_rotation, empty_scale)
		
		# Setup modifiers
		for obj in context.selected_objects:
			cast_mod = obj.modifiers.new("EmptyOffsetCast", "CAST")
			cast_mod.object = empty
			cast_mod.use_x = self.use_x
			cast_mod.use_y = self.use_y
			cast_mod.use_z = self.use_z
			cast_mod.cast_type = self.cast_type
			cast_mod.factor = self.factor
			cast_mod.radius = self.radius
			cast_mod.size = self.size
			cast_mod.use_radius_as_size = self.use_radius_as_size
			cast_mod.use_transform = self.use_transform
		
		return {'FINISHED'}
		
		
class ME_OT_AddSimpleDeformEmptyOperator(bpy.types.Operator):
	"""Adds an empty controlled simple deform to all selected objects."""
	bl_idname = "object.me_ot_add_simple_deform_empty"
	bl_label = "Add Simple Deform Empty"
	bl_options = {'REGISTER','UNDO'}

	deform_type_items = (
		('TWIST',"Twist","Rotate around the Z axis of the modifier space",'MOD_SCREW',0),
		('BEND',"Bend","Bend the mesh over the Z axis of the modifier space",'MOD_SIMPLEDEFORM',1),
		('TAPER',"Taper","Linearly scale along Z axis of the modifier space",'MESH_CONE',2),
		('STRETCH',"Stretch","Stretch the object along the Z axis of the modifier space",'FULLSCREEN_ENTER',3)
	)
	
	# Properties
	deform_method : EnumProperty(
		items=deform_type_items,
		name="Deform Method",
		description="Method of how object will be deformed",
		default='TWIST'
	)
	
	use_x : BoolProperty(
		name="X",
		description="Allow deformation along the X axis",
		default=True
	)

	use_y : BoolProperty(
		name="Y",
		description="Allow deformation along the Y axis",
		default=True
	)
	
	angle : FloatProperty(
		name="Angle/Factor",
		description="Angle/Factor of deformation",
		default=0.785398
	)
	
	limits : FloatVectorProperty(
		name="Limits",
		description="Lower/Upper limits for deform",
		min=0,
		max=1.0,
		size=2,
		default=(0.0,1.0)
	)
	
	use_cursor_loc : BoolProperty(
		name="Use 3D cursor location",
		description="If on, sets empty at 3D cursor, else uses active object's location",
		default=False
	)
	
	location_modify : FloatVectorProperty(
		name = "Translation",
		description="Modfies empty's location",
		subtype='XYZ'
	)
	
	rotation_modify : FloatVectorProperty(
		name = "Rotation",
		description="Modfies empty's rotation",
		subtype='EULER',
		unit='ROTATION'
	)
	
	scale_modify : FloatVectorProperty(
		name = "Scale Relative",
		description="Modfies empty's scale",
		subtype='XYZ',
		default=(1.0,1.0,1.0)
	)
	
	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.mode == 'OBJECT'

	def execute(self, context):
		active_obj = context.active_object
		use_cursor_loc = self.use_cursor_loc
		
		# Setup empty
		# Copy active_obj's attributes or they will be modified too
		empty_location = context.scene.cursor.location.copy() if use_cursor_loc else active_obj.location.copy()
		empty_location += self.location_modify
		
		empty_rotation = active_obj.rotation_euler.copy()
		
		empty_scale = active_obj.scale.copy()
		
		for i in range(0,3):
			empty_rotation[i] += self.rotation_modify[i]
			empty_scale[i] *= self.scale_modify[i]
		
		empty_name = active_obj.name + "SimpleDeformEmpty"
		empty = createEmpty(context, empty_name, empty_location, empty_rotation, empty_scale)
		
		# Setup modifiers
		for obj in context.selected_objects:
			deform_mod = obj.modifiers.new("EmptyOffsetSimpleDeform", "SIMPLE_DEFORM")
			deform_mod.origin = empty
			deform_mod.lock_x = not self.use_x
			deform_mod.lock_y = not self.use_y
			deform_mod.deform_method = self.deform_method
			deform_mod.limits = self.limits
			deform_mod.angle = self.angle
		
		return {'FINISHED'}
		
		
class ME_OT_AddBentArrayEmptyOperator(bpy.types.Operator):
	"""Adds an empty controlled radial array to all selected objects."""
	bl_idname = "object.me_ot_add_bent_array_empty"
	bl_label = "Add Bent Array Empty"
	bl_options = {'REGISTER','UNDO'}

	# Properties
	array_count : IntProperty(
		name="Array count",
		description="Total amount of objects",
		default=2,
		min=1
	)
	
	use_cursor_loc : BoolProperty(
		name="Use 3D cursor location",
		description="If on, sets empty at 3D cursor, else uses active object's location",
		default=False
	)
	
	location_modify : FloatVectorProperty(
		name = "Translation",
		description="Modfies empty's location",
		subtype='XYZ'
	)
	
	set_axis : EnumProperty(
		items=[
			("0","X","X axis","COLOR_RED",0),
			("1","Y","Y axis","COLOR_GREEN",1),
			("2","Z","Z axis","COLOR_BLUE",2)
			],
		name="Spin Axis",
		description="Axis which the array modifier spins around",
		default="2"
	)
	
	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.mode == 'OBJECT'

	def execute(self, context):
		active_obj = context.active_object
		axis = int(self.set_axis)
		array_count = self.array_count
		use_cursor_loc = self.use_cursor_loc
		relative_offset_displace = (0.0, 0.0, 0.0)
		
		# Copy loc, rot, and scale so source doesn't get changed
		empty_location = context.scene.cursor.location.copy() if use_cursor_loc else active_obj.location.copy()
		empty_location += self.location_modify
		
		empty_rotation = active_obj.rotation_euler.copy()
		if axis == 0:
			empty_rotation[0]-=(pi/2)
			empty_rotation[2]+=(pi/2)
		elif axis == 1:
			empty_rotation[0]+=(pi/2)
		else:
			empty_rotation[2]+=(pi/2)
		
		empty_scale = active_obj.scale.copy()
		
		empty_name = active_obj.name + "BentArrayEmpty"
		empty = createEmpty(context, empty_name, empty_location, empty_rotation, empty_scale)
		
		if axis == 0 or axis == 2:
			relative_offset_displace = (0.0, 1.0, 0.0)
		else:
			relative_offset_displace = (1.0, 0.0, 0.0)
		
		for obj in context.selected_objects:
			array_mod = obj.modifiers.new("Array", "ARRAY")
			array_mod.relative_offset_displace = relative_offset_displace
			array_mod.use_merge_vertices = True
			array_mod.merge_threshold = 0.001
			array_mod.count = array_count
			deform_mod = obj.modifiers.new("EmptyOffsetBentDeform", "SIMPLE_DEFORM")
			deform_mod.origin = empty
			deform_mod.deform_method = 'BEND'
			deform_mod.angle = 2*pi
		
		return {'FINISHED'}	


class ME_OT_AddQuickHookEmptyOperator(bpy.types.Operator):
	"""Adds Hook modifier to each selected object and creates an empty to control them."""
	bl_idname = "object.me_ot_add_quick_hook_empty"
	bl_label = "Add Quick Hook Empty"
	bl_options = {'REGISTER','UNDO'}
	
	# Properties
	parent_empty : BoolProperty(
		name="Parent Empty to Active",
		description="Make the active object parent of hook empty",
		default=True
	)

	vertex_group_name : StringProperty(
		name="Vertex Group Name",
		description="Name of Quick Hook vertex group",
		default="Quick Hook"
	)

	@classmethod
	def poll(cls, context):
		return context.active_object is not None and context.mode == 'OBJECT'

	def execute(self, context):
		active_obj = context.active_object
		quick_hook_name = active_obj.name + "_QuickHookEmpty"
		quick_hook_loc = active_obj.location.copy()
		quick_hook_rot = active_obj.rotation_euler.copy()
		quick_hook_scale = active_obj.scale.copy()
		quick_hook_parent = None
		if self.parent_empty:
			quick_hook_parent = active_obj
		# create QuickHook Empty
		quick_hook_empty = createEmpty(context, quick_hook_name, quick_hook_loc, quick_hook_rot, quick_hook_scale, quick_hook_parent)
		for obj in context.selected_objects:
			# make "QuickHook" vertex group for selected objects
			vg = obj.vertex_groups.new(name=self.vertex_group_name)
			# add selected vertices of selected objects to QuickHook vertex group
			verts = [v.index for v in obj.data.vertices if v.select]
			if len(verts):
				vg.add(verts, 1.0, 'ADD')
			# add hook modifier to selected objects
			hook_mod = obj.modifiers.new("QuickHook", "HOOK")
			# add vertex group to modifier
			hook_mod.vertex_group = vg.name
			# add QuickHook object to modifier
			hook_mod.object = quick_hook_empty
		return {'FINISHED'}


# Menus
class ME_MT_AddModifierEmptyMenu(bpy.types.Menu):
	bl_idname = "ME_MT_add_modifier_empty_menu"
	bl_label = "Modifier Empty"

	def draw(self, context):
		layout = self.layout
		layout.operator(ME_OT_AddArrayEmptyOperator.bl_idname, icon="MOD_ARRAY")
		layout.operator(ME_OT_AddRadialArrayEmptyOperator.bl_idname, icon="MOD_ARRAY")
		layout.operator(ME_OT_AddBentArrayEmptyOperator.bl_idname, icon="MOD_ARRAY")
		layout.operator(ME_OT_AddMirrorEmptyOperator.bl_idname, icon="MOD_MIRROR")
		layout.operator(ME_OT_AddCastEmptyOperator.bl_idname, icon="MOD_CAST")
		layout.operator(ME_OT_AddSimpleDeformEmptyOperator.bl_idname, icon="MOD_SIMPLEDEFORM")
		layout.operator(ME_OT_AddQuickHookEmptyOperator.bl_idname, icon="HOOK")


def add_modifier_empty_menu(self, context):
	self.layout.menu(ME_MT_AddModifierEmptyMenu.bl_idname, icon="MODIFIER")
	

classes = ( 
	ME_OT_AddRadialArrayEmptyOperator,
	ME_OT_AddArrayEmptyOperator,
	ME_OT_AddMirrorEmptyOperator,
	ME_OT_AddCastEmptyOperator,
	ME_OT_AddSimpleDeformEmptyOperator,
	ME_OT_AddBentArrayEmptyOperator,
	ME_OT_AddQuickHookEmptyOperator,
	ME_MT_AddModifierEmptyMenu
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.VIEW3D_MT_add.append(add_modifier_empty_menu)

def unregister():
	bpy.types.VIEW3D_MT_add.remove(add_modifier_empty_menu)
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)

if __name__ == "__main__":
	register()

