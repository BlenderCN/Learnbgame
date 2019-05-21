import bpy
from rna_prop_ui import rna_idprop_ui_prop_get

# property object for DialogOperator
ob_prop = None

def template_propbox(layout, label, icon = 'NONE'):
	col = layout.column(align=True)
	box = col.box()
	box.label(label, icon)
	return col.box()

def box_error(layout, text):
	box = layout.box()
	box.label(text, 'ERROR')

def box_info(layout, text):
	box = layout.box()
	box.label(text, 'INFO')

class EnableAnimationOperator(bpy.types.Operator):
	bl_idname = "fdm.enable_animation"
	bl_label = "Enable animation"

	driver_id = bpy.props.IntProperty()
	set_target = bpy.props.BoolProperty(default = False)
	invert_val = bpy.props.BoolProperty(default = False)

	def execute(self, context):
		ob = context.active_object

		driver = ob.animation_data.drivers[self.driver_id]
		modifiers = driver.modifiers
		keep = 1 if self.invert_val else 0
		while len(modifiers) > keep:
			modifiers.remove(modifiers[0])
		modifiers[0].mode = 'POLYNOMIAL'
		modifiers[0].poly_order = 1
		modifiers[0].coefficients[0] = 1
		modifiers[0].coefficients[1] = -1

		driver = driver.driver
		driver.type = 'SUM'

		var = driver.variables[0]
		var.type = 'SINGLE_PROP'

		target = var.targets[0]
		target.id_type = 'OBJECT'

		global ob_prop
		target.id = ob_prop if self.set_target else None

		return {'FINISHED'}

class SelectKeyframeOperator(bpy.types.Operator):
	bl_idname = "fdm.select_keyframe"
	bl_label = "Select keyframe"

	driver_id = bpy.props.IntProperty()
	key_id = bpy.props.IntProperty()

	def execute(self, context):
		ob = context.active_object

		driver = ob.animation_data.drivers[self.driver_id]
		num_points = len(driver.keyframe_points)
		if self.key_id >= num_points:
			driver.keyframe_points.add(self.key_id - num_points + 1)

			for i in range(num_points, self.key_id):
				driver.keyframe_points[i].co = [-1, 0]

		driver.keyframe_points[self.key_id].co = [
			self.key_id,
			ob.path_resolve(driver.data_path)[ driver.array_index ]
		]
		driver.keyframe_points[self.key_id].interpolation = 'LINEAR'

		if		( len(driver.keyframe_points) == 2
			 and driver.keyframe_points[0].co[0] == 0
			 and driver.keyframe_points[1].co[0] == 1 ):
			var = driver.driver.variables[0]

			global ob_prop
			var.targets[0].id = ob_prop

		return {'FINISHED'}

class DialogOperator(bpy.types.Operator):
	bl_idname = "fdm.dialog_select_prop"
	bl_label = "Select Property"

	def getProperties(self, context):
		return [(p, p, p) for p in ob_prop.keys() if p[0] == '/']

	prop = bpy.props.EnumProperty(items = getProperties)
	new_prop = bpy.props.StringProperty()
	is_bool = bpy.props.BoolProperty(default = False)

	driver_id = bpy.props.IntProperty()

	def draw(self, context):
		layout = self.layout
		layout.prop(self, 'prop', "Use")
		layout.label("or")
		layout.prop(self, 'new_prop', "Create new")

	def execute(self, context):
		ob = context.active_object
		prop = self.prop
		global ob_prop

		if len(self.new_prop) > 0:
			prop = self.new_prop
			if prop[0] != '/':
				prop = '/' + prop

			# Create property
			ob_prop[prop] = True if self.is_bool else 0.0

			# Limit to [0, 1]
			prop_ui = rna_idprop_ui_prop_get(ob_prop, prop, create=True)
			prop_ui['soft_min'] = False if self.is_bool else 0.0
			prop_ui['soft_max'] = True if self.is_bool else 1.0

		driver = ob.animation_data.drivers[self.driver_id].driver
		driver.type = 'SUM'

		var = driver.variables[0]
		var.type = 'SINGLE_PROP'

		target = var.targets[0]
		target.id_type = 'OBJECT'
		target.id = ob_prop
		target.data_path = '["' + prop + '"]'

		return {'FINISHED'}

	def invoke(self, context, event):
		return bpy.context.window_manager.invoke_props_dialog(self)

def layoutDefault(layout, ob, ctx):
	pass

def layoutAnimations(layout, ob, ctx):
	if not ob.animation_data:
		return

	box = template_propbox(layout, "Animations", 'ANIM')

	global ob_prop
	if not ob_prop:
		box.label("No (parent) object of type Fuselage!", 'ERROR')
		return

	axis_names = ['X', 'Y', 'Z']

	for driver_id, driver in enumerate(ob.animation_data.drivers):
		text = "Animation: "
		use_keyframes = True
		if driver.data_path == 'rotation_euler':
			icon = 'MAN_ROT'
			text += "Rotate "
		elif driver.data_path == 'location':
			icon = 'MAN_TRANS'
			text += "Translate "
		elif driver.data_path == 'scale':
			icon = 'MAN_SCALE'
			text += "Scale "
		elif driver.data_path == 'hide':
			icon = 'VISIBLE_IPO_ON'
			text += "Hide "
			use_keyframes = False
		else:
			print('Driver type ' + driver.data_path + ' not supported yet!')
			continue
		text += axis_names[ driver.array_index ]
		box.label(text, icon)

		if driver.driver.type != 'SUM':
			op_enable = box.operator(
				'fdm.enable_animation',
				icon = 'ANIM',
				text = "Enable animation"
			)
			op_enable.driver_id = driver_id
			op_enable.invert_val = driver.data_path == 'hide'

			# Target object is set after all keyframes are valid. We do not use key
			# frames so we need to manually set the target object.
			op_enable.set_target = not use_keyframes
			continue

		variables = driver.driver.variables
		if len(variables) > 1:
			box_error(box, "Warning: more than one variable!")

		if use_keyframes:
			num_keys = len(driver.keyframe_points)

			start_point = driver.keyframe_points[0] if num_keys > 0 else None
			end_point = driver.keyframe_points[1] if num_keys > 1 else None

			start_valid = start_point and start_point.co[0] == 0
			end_valid = end_point and end_point.co[0] == 1

			row = box.row(align=True)
			row.label("Endpoints")

			ob_props = row.operator(
				'fdm.select_keyframe',
				icon = 'FILE_TICK' if start_valid else 'KEY_HLT',
				text = "Start"
			)
			ob_props.driver_id = driver_id
			ob_props.key_id = 0

			ob_props = row.operator(
				'fdm.select_keyframe',
				icon = 'FILE_TICK' if end_valid else 'KEY_HLT',
				text = "End"
			)
			ob_props.driver_id = driver_id
			ob_props.key_id = 1

		var = variables[0]
		if var.type != 'SINGLE_PROP':
			continue

		target = var.targets[0]
		if target.id_type != 'OBJECT' or not target.id:
			continue

		row = box.row(align=True)
		if len(target.data_path):
			row.prop(target.id, target.data_path)

		op_sel = row.operator(
			'fdm.dialog_select_prop',
			icon = 'FILE_FOLDER',
			text = "Select property" if not len(target.data_path) else ""
		)
		op_sel.driver_id = driver_id
		op_sel.is_bool = driver.data_path == 'hide'

def layoutClickable(layout, ob, ctx):
	props = ob.fgfs.clickable

	layout.prop(props, 'action')
	layout.prop(props, 'prop')

def layoutFuselage(layout, ob, ctx):
	props = ob.fgfs.fuselage

	layout.label("Weights [kg]")
	layout.prop(props, 'empty_weight')

	layout.label("Moments of inertia [kg*m²]")
	col = layout.column(align=True)
	col.prop(props, 'ixx')
	col.prop(props, 'iyy')
	col.prop(props, 'izz')

def layoutStrut(layout, ob, ctx):
	strut = ob.data.fgfs.strut
	gear = ob.fgfs.gear

	num_wheels = len([o for o in ob.children if o.fgfs.type == 'WHEEL'])
	if not num_wheels:
		box_error(layout, "No wheels attached! (At least one is needed)")
	else:
		box_info(layout, str(num_wheels) + " wheels attached.")

	instance_info = "(" + str(ob.data.users) + " instances)"

	box = template_propbox(layout, "Strut Options " + instance_info)
	box.label("Static compression [N*m⁻¹]")
	row = box.row(align=True)
	row.alignment = 'LEFT'
	row.prop(strut, 'spring_coeff', text = "Rate")

	unit_damping = "[N*m⁻¹*s⁻¹]"
	unit_damping_sq = "[N*m⁻²*s⁻²]"

	if strut.damping_coeff_squared:
		unit = unit_damping_sq
	else:
		unit = unit_damping

	box.label("Damping (compression) " + unit)
	row = box.row(align=True)
	row.alignment = 'LEFT'
	row.prop(strut, 'damping_coeff', text = "Rate")
	row.prop(strut, 'damping_coeff_squared', text = "Square",
																					 toggle = True)

	if strut.damping_coeff_rebound_squared:
		unit = unit_damping_sq
	else:
		unit = unit_damping

	box.label("Damping (rebound) " + unit)
	row = box.row(align=True)
	row.alignment = 'LEFT'
	row.prop(strut, 'damping_coeff_rebound', text = "Rate")
	row.prop(strut, 'damping_coeff_rebound_squared', text = "Square",
																									 toggle = True)

	box = template_propbox(layout, "Gear Options")
	box.prop(gear, 'brake_group')
	box.prop(gear, 'steering_type')
	if gear.steering_type == 'STEERABLE':
		box.prop(gear, 'max_steer')
		box.prop_search(gear, 'rotate_parent', ctx.scene, "objects")

def layoutLight(layout, ob, ctx):
	pass

def layoutTank(layout, ob, ctx):
	tank = ob.fgfs.tank

	box = template_propbox(layout, "Tank: " + ob.name)
	box.prop(tank, 'content')

	if tank.content == 'FUEL':
		unit = "[m³]"
	else:
		unit = "[l (dm³)]"

	col = box.column(align=True)
	col.prop(tank, 'capacity', text = "Capacity " + unit)
	col.prop(tank, 'unusable', text = "Unusable [%]")
	col.prop(tank, 'level', text = "Fill level [%]")

# assign layouts to types
layouts = {
	'DEFAULT': layoutDefault,
	'PICKABLE': layoutClickable,
	'FUSELAGE': layoutFuselage,
	'STRUT': layoutStrut,
	'WHEEL': layoutDefault,
	'TANK': layoutTank,
}

class FlightgearPanel(bpy.types.Panel):
	bl_label = "Flightgear"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "object"

	@classmethod
	def poll(self, context):
		if context.object and context.object.type in ['MESH', 'EMPTY', 'LAMP']:
			return True

	def draw(self, context):
		layout = self.layout
		ob = context.active_object

		# Get object containing all properties for animations
		global ob_prop
		ob_prop = ob
		while ob_prop and ob_prop.fgfs.type != 'FUSELAGE':
			ob_prop = ob_prop.parent

		if ob.type == 'LAMP':
			pass
		else:
			layout.prop(ob.fgfs, 'type')
			layouts[ob.fgfs.type](layout, ob, context)
			layoutAnimations(layout, ob, context)
