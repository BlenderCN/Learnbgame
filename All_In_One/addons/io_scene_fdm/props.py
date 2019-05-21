import bpy, math
from rna_prop_ui import rna_idprop_ui_prop_get

class ClickableProperties(bpy.types.PropertyGroup):
	action = bpy.props.EnumProperty(
		name = "Action",
		description = "Action triggered on click",
		items = [
			('property-toggle', "Toggle", "property-toggle"),
			('property-assign', "Assign", "property-assign")
		],
		default = 'property-toggle',
		options = {'HIDDEN'}
	)
	prop = bpy.props.StringProperty(
		name = "Property",
		description = "Property modified by action",
		options = {'HIDDEN'}
	)

class FuselageProperties(bpy.types.PropertyGroup):
	empty_weight = bpy.props.FloatProperty(
		name = "Empty weight",
		description = "Total empty weight (without any fuel, cargo, etc.)",
		subtype = 'UNSIGNED',
		min = 0,
		options = {'HIDDEN'}
	)
	ixx = bpy.props.FloatProperty(
		name = "ixx",
		description = "Moment of inertia arround x-axis",
		subtype = 'UNSIGNED',
		min = 0,
		options = {'HIDDEN'}
	)
	iyy = bpy.props.FloatProperty(
		name = "iyy",
		description = "Moment of inertia arround y-axis",
		subtype = 'UNSIGNED',
		min = 0,
		options = {'HIDDEN'}
	)
	izz = bpy.props.FloatProperty(
		name = "izz",
		description = "Moment of inertia arround z-axis",
		subtype = 'UNSIGNED',
		min = 0,
		options = {'HIDDEN'}
	)

class StrutProperties(bpy.types.PropertyGroup):
	"""
	Struts properties are defined per strut (=mesh) whereas gear properties
	get defined inside the individual instantiated object
	"""
	spring_coeff = bpy.props.FloatProperty(
		name = "Spring coefficient",
		description = "Spring constant from Hooke's law (Static load/strut displacement = N/m)",
		subtype = 'UNSIGNED',
		min = 0,
		options = {'HIDDEN'}
	)
	damping_coeff = bpy.props.FloatProperty(
		name = "Damping coefficient",
		description = "Damping coefficient (Force proportional to strut displacement rate on compression = N/m/s)",
		subtype = 'UNSIGNED',
		min = 0,
		options = {'HIDDEN'}
	)
	damping_coeff_squared = bpy.props.BoolProperty(
		name = "Square damping",
		description = "Enable squared damping",
		options = {'HIDDEN'}
	)
	damping_coeff_rebound = bpy.props.FloatProperty(
		name = "Rebound damping coefficient",
		description = "Damping coefficient (Force proportional to strut displacement rate on rebound = N/m/s)",
		subtype = 'UNSIGNED',
		min = 0,
		options = {'HIDDEN'}
	)
	damping_coeff_rebound_squared = bpy.props.BoolProperty(
		name = "Square rebound damping",
		description = "Enable squared rebound damping",
		options = {'HIDDEN'}
	)

class GearProperties(bpy.types.PropertyGroup):
	"""
	Landing gear properties. See StrutProperties for properties of associated
	strut.
	"""
	brake_group = bpy.props.EnumProperty(
		name = "Brake group",
		description = "Brake group (Set to None for gears without brake)",
		items = [
			('LEFT', "Left", "Left"),
			('RIGHT', "Right", "Right"),
			('CENTER', "Center", "Center"),
			('NOSE', "Nose", "Nose"),
			('TAIL', "Tail", "Tail"),
			('NONE', "None", "None")
		],
		default = 'NONE',
		options = {'HIDDEN'}
	)
	steering_type = bpy.props.EnumProperty(
		name = "Steering",
		description = "Set steerability of gear",
		items = [
			('STEERABLE', 'Steerable', 'Steerable'),
			('FIXED', 'Fixed', 'Fixed (Steering disabled)'),
			('CASTERED', 'Castered', 'Castered (Free rotation)')
		],
		default = 'FIXED',
		options = {'HIDDEN'}
	)
	max_steer = bpy.props.FloatProperty(
		name = "Max steering",
		description = "Maximum steering angle (negative inverts steering)",
		subtype = 'ANGLE',
		unit = 'ROTATION',
		default = math.radians(60),
		min = math.radians(-360),
		max = math.radians(360),
		soft_min = math.radians(-80),
		soft_max = math.radians(80),
		options = {'HIDDEN'}
	)
	rotate_parent = bpy.props.StringProperty(
		name = "Rotate parent",
		description = "(Parent) object rotated while steering instead of this object",
		options = {'HIDDEN'}
	)

class TankProperties(bpy.types.PropertyGroup):
	"""
	Properties for tanks containing consumable liquids and gases (fuel, oxygen,
	etc.)
	"""
	content = bpy.props.EnumProperty(
		name = 'Content',
		description='Type of content.',
		items = [
			('FUEL', "Fuel", "Fuel consumed by the engines."),
			('OXYGEN', "Oxygen", "Liquid oxygen consumable by the crew.")
		],
		default = 'FUEL',
		options = {'HIDDEN'}
	)
	capacity = bpy.props.FloatProperty(
		name = "Capacity",
		description = "Tank capacity [m³ for Fuel, l (dm³) for Oxygen]",
		subtype = 'UNSIGNED',
		min = 0,
		options = {'HIDDEN'}
	)
	unusable = bpy.props.FloatProperty(
		name = "Unusable",
		description = "Unusable tank capacity [%]",
		subtype = 'UNSIGNED',
		min = 0,
		max = 50,
		options = {'HIDDEN'}
	)
	level = bpy.props.FloatProperty(
		name = "Fill level",
		description = "Current fill level [%]",
		subtype = 'UNSIGNED',
		min = 0,
		max = 100,
		options = {'HIDDEN'}
	)


class MeshProperties(bpy.types.PropertyGroup):
	strut = bpy.props.PointerProperty(
		type = StrutProperties,
		name = "Strut",
		description = "Landing gear strut settings (if type == STRUT)"
	)

# ------------------------------------------------------------------------------
properties = {
	'DEFAULT': {},
	'FUSELAGE': {
		'/surface-positions/elevator-pos-norm': [-1, 1],
		'/surface-positions/rudder-pos-norm': [-1, 1],
		'/surface-positions/left-aileron-pos-norm': [-1, 1],
		'/surface-positions/right-aileron-pos-norm': [-1, 1],
		'/surface-positions/flap-pos-norm': [0, 1],
	},
	'STRUT': {
		'gear/position-norm': [0, 1],
		'gear/steering-norm': [-1, 1]
	},
	'WHEEL': {},
	'PICKABLE': {},
	'CONSUMABLE': {},
}

def _onTypeChange(self, context):
	ob = self.id_data
	for cat, props in properties.items():
		if cat == self.type:
			for prop, dom in props.items():
				ob[prop] = 0.0
				prop_ui = rna_idprop_ui_prop_get(ob, prop, create=True)
				prop_ui['min'] = float(dom[0])
				prop_ui['max'] = float(dom[1])
		else:
			# remove values from other categories
			for prop in props.keys():
				try:	del ob[prop]
				except:		pass
				try: del ob['_RNA_UI'][prop]
				except: pass

class ObjectProperties(bpy.types.PropertyGroup):
	type = bpy.props.EnumProperty(
		name = 'Object Type',
		description='Type for object in Flightgear',
		items = [
			('DEFAULT', "Default", "Object with no special handling."),
			('FUSELAGE', "Fuselage", "The fuselage of the plane. Should be centered around center of gravity."),
			('STRUT', "Landing Gear Strut", "Can be rotated while steering and is moved up and down according to compression. Needs at least on wheel as child."),
			('WHEEL', "Wheel", "Is rotated according to speed while taxiing around. Has to be child of a Landing Gear Strut."),
			('PICKABLE', "Clickable", "A clickable button, switch etc."),
			('TANK', "Tank", "Tank containing liquid or gas (eg. fuel, oxygen, etc.).")
		],
		default='DEFAULT',
		options = {'HIDDEN'},
		update = _onTypeChange
	)
	
	clickable = bpy.props.PointerProperty(
		type = ClickableProperties,
		name = "Clickable",
		description = "Clickable Settings (if type == PICKABLE)"
	)
	fuselage = bpy.props.PointerProperty(
		type = FuselageProperties,
		name = "Fuselage",
		description = "Fuselage Settings (if type == FUSELAGE)"
	)
	gear = bpy.props.PointerProperty(
		type = GearProperties,
		name = "Gear",
		description = "Landing gear settings (if type == STRUT)"
	)
	tank = bpy.props.PointerProperty(
		type = TankProperties,
		name = "Tank",
		description = "Tank settings (if type == CONSUMABLE)"
	)

def register():
	bpy.types.Object.fgfs = bpy.props.PointerProperty(
		type = ObjectProperties,
		name = "Flightgear",
		description = "Flightgear Settings"
	)
	bpy.types.Mesh.fgfs = bpy.props.PointerProperty(
		type = MeshProperties,
		name = "Flightgear",
		description = "Flightgear Settings"
	)

if __name__ == "__main__":
	register()
