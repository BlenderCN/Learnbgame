import bpy
from bpy.props import *
from bpy.types import PropertyGroup

bpy.mammothComponentsLoaded = False
bpy.mammothComponentsLayout = {}
bpy.mammothRegisteredComponents = {}

# TODO:
def listMammothLayers(self, context):
	return [
		('default', "Default", ""),
		('ui', "UI", "")
	]

# TODO:
def listRenderLayers(self, context):
	return [
		('all', "All", ""),
		('default', "Default", ""),
		('ui', "UI", "")
	]

def load():
	# build our component property groups
	for key, attributes in bpy.mammothComponentsLayout.items():
		name = "mammoth_component_%s" % key
		
		# build the component dictionary
		# by default, all objects will have all components
		# use this switch to denote whether the object
		# _actually_ has the component or not
		attribute_dict = {"internal___active": BoolProperty(default=False)}
		for attribute in attributes:
			# specialize the inputs
			subtype = 'NONE'
			if 'subtype' in attribute:
				subtype = attribute['subtype']
			unit = 'NONE'
			if 'units' in attribute:
				unit = attribute['units']

			# TODO: more attribute types
			if attribute['type'] == 'int':
				attribute_dict[attribute['name']] = IntProperty(name=attribute['name'], subtype=subtype)
			elif attribute['type'] == 'float':
				attribute_dict[attribute['name']] = FloatProperty(name=attribute['name'], subtype=subtype, unit=unit)
			elif attribute['type'] == 'bool':
				attribute_dict[attribute['name']] = BoolProperty(name=attribute['name'], subtype=subtype)
			elif attribute['type'] == 'string':
				attribute_dict[attribute['name']] = StringProperty(name=attribute['name'], subtype=subtype)
			elif attribute['type'] == 'ivec2':
				attribute_dict[attribute['name']] = IntVectorProperty(name=attribute['name'], size=2, subtype=subtype)
			elif attribute['type'] == 'ivec3':
				attribute_dict[attribute['name']] = IntVectorProperty(name=attribute['name'], size=3, subtype=subtype)
			elif attribute['type'] == 'ivec4':
				attribute_dict[attribute['name']] = IntVectorProperty(name=attribute['name'], size=4, subtype=subtype)
			elif attribute['type'] == 'vec2':
				attribute_dict[attribute['name']] = FloatVectorProperty(name=attribute['name'], size=2, subtype=subtype, unit=unit)
			elif attribute['type'] == 'vec3':
				attribute_dict[attribute['name']] = FloatVectorProperty(name=attribute['name'], size=3, subtype=subtype, unit=unit)
			elif attribute['type'] == 'vec4':
				attribute_dict[attribute['name']] = FloatVectorProperty(name=attribute['name'], size=4, subtype=subtype, unit=unit)
			elif attribute['type'] == 'colour':
				attribute_dict[attribute['name']] = FloatVectorProperty(name=attribute['name'], subtype='COLOR', default=(1.0, 1.0, 1.0, 1.0), size=4, min=0, max=1)
			else:
				raise TypeError('Unsupported Mammoth attribute type \'%s\' for %s on %s' % (attribute['type'], attribute['name'], key))
		
		# build the component type
		compType = type(name, (PropertyGroup,), attribute_dict)
		
		# register it with blender (and python)
		bpy.utils.register_class(compType)
		setattr(bpy.types.Object, name, PointerProperty(type=compType))
		
		# store it for later
		bpy.mammothRegisteredComponents[key] = compType

	# add data to the built-in components
	setattr(bpy.types.Object, "mammoth_use_transform", BoolProperty(name="Use Transform", default=True))
	setattr(bpy.types.Object, "mammoth_layer", EnumProperty(name="Layer", items=listMammothLayers))

	setattr(bpy.types.Camera, "mammoth_render_order", IntProperty(name="Render Order", default=0))
	setattr(bpy.types.Camera, "mammoth_clear_flags", EnumProperty(name="Clear Flags", items=(
		('none', "None", "Don't clear"),
		('colour', "Colour", "Only clear colour"),
		('depth', "Depth", "Only clear depth"),
		('both', "Both", "Clear both colour and depth")
	), default='both'))
	setattr(bpy.types.Camera, "mammoth_viewport_min", FloatVectorProperty(name="Viewport Min", size=2, min=0.0, max=1.0, default=(0.0, 0.0)))
	setattr(bpy.types.Camera, "mammoth_viewport_max", FloatVectorProperty(name="Viewport Max", size=2, min=0.0, max=1.0, default=(1.0, 1.0)))
	setattr(bpy.types.Camera, "mammoth_render_layers", EnumProperty(name="Render Layers", items=listRenderLayers))

	bpy.mammothComponentsLoaded = True

	print("loaded components:")
	print(bpy.mammothComponentsLayout)

def unload():
	# unregister our components
	try:
		for key, value in bpy.mammothRegisteredComponents.items():
			name = "mammoth_component_%s" % key
			delattr(bpy.types.Object, name)
			bpy.utils.unregister_class(value)
		delattr(bpy.types.Object, "mammoth_use_transform")
		delattr(bpy.types.Object, "mammoth_layer")
		delattr(bpy.types.Camera, "mammoth_render_order")
		delattr(bpy.types.Camera, "mammoth_clear_flags")
		delattr(bpy.types.Camera, "mammoth_viewport_min")
		delattr(bpy.types.Camera, "mammoth_viewport_max")
		delattr(bpy.types.Camera, "mammoth_render_layers")
	except UnboundLocalError:
		pass
	bpy.mammothComponentsLayout = {}
	bpy.mammothRegisteredComponents = {}
	bpy.mammothComponentsLoaded = False

def loadLayout(path):
		import os
		if os.path.splitext(path)[1] == '.json':
			with open(bpy.path.abspath(path)) as definition_file:
				import json
				bpy.mammothComponentsLayout = json.load(definition_file)
		else:
			print('Definitions must be .json files!')
		print(bpy.mammothComponentsLayout)