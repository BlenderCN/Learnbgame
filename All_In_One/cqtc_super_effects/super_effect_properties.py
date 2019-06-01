import bpy.ops
import bpy.props
import bpy.types
from .effects import *
from . import templates
from cqtc_operator import CqtcOperator

effect_list = [
	NoEffect("no_effect"),
	FadeEffect("fade"),
	IrisInEffect("iris_in"),
	IrisOutEffect("iris_out"),
	ClockEffect("clock"),
	ClockAntiEffect("clock_anti"),
	SlideDownEffect("slide_down"),
	SlideUpEffect("slide_up"),
	SlideRightEffect("slide_right"),
	SlideLeftEffect("slide_left"),
	DoubleHorizontalSlideOpenEffect("double_horizontal_slide_open"),
	DoubleHorizontalSlideCloseEffect("double_horizontal_slide_close"),
	DoubleVerticalSlideOpenEffect("double_vertical_slide_open"),
	DoubleVerticalSlideCloseEffect("double_vertical_slide_close"),
]

plain_properties = [
	"name",
	"effect_type",
	"effect_length_type",
	"effect_length",
	"effect_length_percentage",
	"apply_to_sound",
	"overlap_sound",
	"delay_image",
	"speed_factor",
	"sound_file",
	"reverse_out_effect",
	"mirror_horizontal_out_effect",
	"mirror_vertical_out_effect",
	"image_alignment_margin",
	"image_alignment"
]

animatable_properties = [
	"position_x",
	"position_y",
	"zoom",
	"opacity",
	"offset_x",
	"offset_y",
	"blur_x",
	"blur_y",
	"rotation"
]

excluded_from_template_properties = ["image_alignment", "image_alignment_margin"]

def get_super_effect_template_options(scene, context):
	default_group = "Otros"
	default_group_icon = "FORCE_VERTIX"
	groups_info = [
		("ES Pantalla partida ", "E/S Pant. Partida", "SPLITSCREEN"),
		("ES Esquina ", "E/S Esquinas", "MOD_ARRAY"),
		("ES Empujar ", "E/S Empujar", "SCREEN_BACK"),
		("ES ", "E/S Otras", "IPO"),
		("TR ", "Transiciones", "NLA"),
		("FI ", "Fijos", "PAUSE"),
		("JC ", "Juan Carlos", "MOD_PARTICLES"),
	]
	options = []
	group_index = 0
	for group_info in groups_info:
		group = group_info[0]
		group_title = group_info[1]
		group_icon = group_info[2]
		group_options = sorted([ opt for opt in context.scene.super_effect.template_options
			if (opt[0].startswith(group) and opt not in options) ], key=lambda opt: opt[0])
		
		if not len(group_options):
			continue
		
		options.append(('', group_title, group_title, group_icon, group_index))
		options += group_options
		group_index += 1
	
	default_group_options = [ opt for opt in context.scene.super_effect.template_options if opt not in options ]
	if len(context.scene.super_effect.template_options) != len(default_group_options):
		options.append(('', default_group, default_group, default_group_icon, group_index))
	
	options += default_group_options
	
	clean_options = []
	last_group_pattern = ''
	for option in options:
		clean_option = option
		is_group = (option[0] == '')
		if is_group:
			group_pattern = [group_info[0] for group_info in groups_info if group_info[1] == option[1]]
			if len(group_pattern):
				last_group_pattern = group_pattern[0]
			else:
				last_group_pattern = ''
		elif last_group_pattern:
			clean_name = option[1][len(last_group_pattern):].capitalize()
			clean_option = (
				option[0],
				clean_name[0].upper() + clean_name[1:],
				option[2]
			)
		
		clean_options.append(clean_option)
	
	return clean_options


def load_template(self, context):
	bpy.ops.super_effect.load_template()


class ModifyPropertyItemsOperator(CqtcOperator):
	bl_idname = "super_effect.modify_property"
	bl_label = "Modificar propiedad"
	operation = bpy.props.StringProperty(name="Operación", description="add | remove")
	property_name = bpy.props.StringProperty(name="Propiedad", description="Nombre de la propiedad")
	index_to_remove = bpy.props.IntProperty(name="Índice del elemento", description="Índice del elemento a eliminar")
	
	def execute(self, context):
		items_property_name = "%s_items" % self.property_name
		if items_property_name not in dir(context.scene.super_effect):
			return self.return_error("La propiedad '%s' no existe" % items_property_name)
		
		if self.operation.lower() == "add":
			self.__add_property_item(context, items_property_name)
		elif self.operation.lower() == "remove":
			self.__remove_property_item(context, items_property_name)
		
		return {"FINISHED"}
	
	
	def __add_property_item(self, context, items_property_name):
		collection = getattr(context.scene.super_effect, items_property_name)
		collection.add()
		collection_length = len(collection)
		if collection_length == 2:
			collection[1].position_in_percentage = context.scene.super_effect.effect_length_percentage
			collection[1].interpolation_type = collection[0].interpolation_type
			collection[1].value = collection[0].value
		elif collection_length > 2:
			collection[-1].position_in_percentage = collection[-2].position_in_percentage
			collection[-1].interpolation_type = collection[-2].interpolation_type
			collection[-1].value = collection[-2].value
	
	
	def __remove_property_item(self, context, items_property_name):
		getattr(context.scene.super_effect, items_property_name).remove(self.index_to_remove)


def get_property_enabled_callback(property_name):
	enabled_property_name = "%s_enabled" % property_name
	items_property_name = "%s_items" % property_name
	
	def property_enabled_callback(self, context):
		if enabled_property_name not in dir(context.scene.super_effect):
			print("Property '%s' not found" % enabled_property_name)
			return
		
		is_enabled = getattr(context.scene.super_effect, enabled_property_name)
		collection = getattr(context.scene.super_effect, items_property_name)
		
		is_enabled_and_empty = (is_enabled and not len(collection))
		if is_enabled_and_empty:
			collection.add()
	
	return property_enabled_callback


class SuperEffectIntegerPropertyItem(bpy.types.PropertyGroup):
	position_in_percentage = bpy.props.FloatProperty(name="Posición", description = "Posición del valor en porcentaje", default=0, min=0, max=100, step=1, subtype="PERCENTAGE")
	
	value = bpy.props.IntProperty(name="Valor de la propiedad", default=0, min=-10000, max=10000, step=5)
	
	interpolation_type_items = [(opt.identifier, opt.name, opt.description, opt.icon, index) for index, opt 
			in enumerate(bpy.types.GRAPH_OT_interpolation_type.bl_rna.properties['type'].enum_items)]
			
	interpolation_type = bpy.props.EnumProperty(
		name="Interpolación",
		description="Tipo de interpolación del keyframe",
		default = "BEZIER",
		items=interpolation_type_items
	)


class SuperEffectPositiveFloatPropertyItem(bpy.types.PropertyGroup):
	position_in_percentage = bpy.props.FloatProperty(name="Posición", description = "Posición del valor en porcentaje", default=0, min=0, max=100, step=1, subtype="PERCENTAGE")
	
	value = bpy.props.FloatProperty(name="Valor de la propiedad", default=1, min=-0, max=100, step=1)
	
	interpolation_type_items = [(opt.identifier, opt.name, opt.description, opt.icon, index) for index, opt 
			in enumerate(bpy.types.GRAPH_OT_interpolation_type.bl_rna.properties['type'].enum_items)]
			
	interpolation_type = bpy.props.EnumProperty(
		name="Interpolación",
		description="Tipo de interpolación del keyframe",
		default = "BEZIER",
		items=interpolation_type_items
	)


class SuperEffectFactorPropertyItem(bpy.types.PropertyGroup):
	position_in_percentage = bpy.props.FloatProperty(name="Posición", description = "Posición del valor en porcentaje", default=0, min=0, max=100, step=1, subtype="PERCENTAGE")
	
	value = bpy.props.FloatProperty(name="Valor de la propiedad", default=1, min=-0, max=1, step=0.1, subtype="FACTOR")
	
	interpolation_type_items = [(opt.identifier, opt.name, opt.description, opt.icon, index) for index, opt 
			in enumerate(bpy.types.GRAPH_OT_interpolation_type.bl_rna.properties['type'].enum_items)]
			
	interpolation_type = bpy.props.EnumProperty(
		name="Interpolación",
		description="Tipo de interpolación del keyframe",
		default = "BEZIER",
		items=interpolation_type_items
	)


class SuperEffectProperties(bpy.types.PropertyGroup):
	
	effect_type = bpy.props.EnumProperty(
			name = "Efecto",
			description = "Tipo de efecto de la transición",
			default = effect_list[0].effect_key,
			items = [ (e.effect_key, e.name, e.description) for e in effect_list ]
		)
	
	config_expanded = bpy.props.BoolProperty(name="Configuración", default=True)
	
	effect_length_type = bpy.props.EnumProperty(
			name = "Tipo Duración",
			description = "Tipo de duración de la transición (frames o %)",
			default = "FRAMES",
			items = [
				("FRAMES", "En Frames", "Duración medida en frames"),
				("PERCENTAGE", "En Porcentaje", "Duración medida en porcentaje de la tira")
			]
		)
	
	effect_length = bpy.props.IntProperty(name="Duración del efecto", default=22, min=1, max=10000, step=5)
	effect_length_percentage = bpy.props.FloatProperty(name="Duración del efecto (%)", default=10, min=1, max=100, step=5, subtype="PERCENTAGE")
	
	apply_to_sound = bpy.props.BoolProperty(name="Aplicar al sonido", default=True)
	overlap_sound = bpy.props.BoolProperty(name="Superponer el sonido", default=False)
	
	color = bpy.props.FloatVectorProperty(name="Color", subtype="COLOR", default=(0.0, 0.0, 0.0), min=0.0, max=1.0, description="color picker")
	
	delay_image = bpy.props.IntProperty(name="Retrasar la imagen (frames)", default=0, min=0, max=500, step=1)
	speed_factor = bpy.props.FloatProperty(name="Velocidad", default=1, min=0, max=500, step=1)
	sound_file = bpy.props.StringProperty(name="Sonido", subtype="FILE_PATH", description="Sonido para añadir en loop")
	
	position_x_enabled = bpy.props.BoolProperty(name="Activar Posición X", default=False, update=get_property_enabled_callback("position_x"))
	position_x_items = bpy.props.CollectionProperty(name="Valores Posición X", type=SuperEffectIntegerPropertyItem)
	
	position_y_enabled = bpy.props.BoolProperty(name="Activar Posición Y", default=False, update=get_property_enabled_callback("position_y"))
	position_y_items = bpy.props.CollectionProperty(name="Valores Posición Y", type=SuperEffectIntegerPropertyItem)
	
	zoom_enabled = bpy.props.BoolProperty(name="Activar Zoom", default=False, update=get_property_enabled_callback("zoom"))
	zoom_items = bpy.props.CollectionProperty(name="Valores Zoom", type=SuperEffectPositiveFloatPropertyItem)
	
	opacity_enabled = bpy.props.BoolProperty(name="Activar Opacidad", default=False, update=get_property_enabled_callback("opacity"))
	opacity_items = bpy.props.CollectionProperty(name="Valores Opacidad", type=SuperEffectFactorPropertyItem)
	
	offset_x_enabled = bpy.props.BoolProperty(name="Activar Offset X", default=False, update=get_property_enabled_callback("offset_x"))
	offset_x_items = bpy.props.CollectionProperty(name="Valores Offset X", type=SuperEffectIntegerPropertyItem)
	
	offset_y_enabled = bpy.props.BoolProperty(name="Activar Offset Y", default=False, update=get_property_enabled_callback("offset_y"))
	offset_y_items = bpy.props.CollectionProperty(name="Valores Offset Y", type=SuperEffectIntegerPropertyItem)
	
	rotation_enabled = bpy.props.BoolProperty(name="Activar Rotación", default=False, update=get_property_enabled_callback("rotation"))
	rotation_items = bpy.props.CollectionProperty(name="Valores Rotación", type=SuperEffectIntegerPropertyItem)
	
	blur_x_enabled = bpy.props.BoolProperty(name="Activar Desenfoque X", default=False, update=get_property_enabled_callback("blur_x"))
	blur_x_items = bpy.props.CollectionProperty(name="Valores Desenfoque X", type=SuperEffectIntegerPropertyItem)
	
	blur_y_enabled = bpy.props.BoolProperty(name="Activar Desenfoque Y", default=False, update=get_property_enabled_callback("blur_y"))
	blur_y_items = bpy.props.CollectionProperty(name="Valores Desenfoque Y", type=SuperEffectIntegerPropertyItem)
	
	reverse_out_effect = bpy.props.BoolProperty(name="Invertir Efecto de Salida", default=True)
	mirror_horizontal_out_effect = bpy.props.BoolProperty(name="Voltear Horizontal Efecto de Salida", default=False)
	mirror_vertical_out_effect = bpy.props.BoolProperty(name="Voltear Vertical Efecto de Salida", default=False)
	
	image_alignment = bpy.props.EnumProperty(
			name = "Alinear Imágenes pequeñas",
			description = "Alineación de imágenes menores de 1920x1080",
			items = [
				("center", "Centro", "Imágenes centradas"),
				("bottom", "Abajo", "Imágenes alineadas con el borde inferior"),
				("top", "Arriba", "Imágenes alineadas con el borde superior"),
				("left", "Izquierda", "Imágenes alineadas con el borde izquierdo"),
				("right", "Derecha", "Imágenes alineadas con el borde derecho"),
				("bottom_left", "Abajo Izquierda", "Imágenes alineadas con la esquina inferior izquierda"),
				("bottom_right", "Abajo Derecha", "Imágenes alineadas con la esquina inferior derecha"),
				("top_left", "Arriba Izquierda", "Imágenes alineadas con la esquina superior izquierda"),
				("top_right", "Arriba Derecha", "Imágenes alineadas con la esquina superior derecha"),
			]
		)
	image_alignment_margin = bpy.props.IntProperty(name="Margen para imágenes", default=0, min=-1920, max=1920, step=10)
	
	template_expanded = bpy.props.BoolProperty(name="Plantillas", default=True)
	
	template = bpy.props.EnumProperty(
			name = "Plantillas",
			description = "Plantillas guardadas por el usuario",
			items = get_super_effect_template_options,
			update = load_template
		)
	
	new_template_name = bpy.props.StringProperty(name="Nombre", description="Nombre para la nueva plantilla")
	override_template = bpy.props.BoolProperty(name="Sobreescribir Plantilla", default=False)
	
	template_data = templates.load_templates()
	template_options = [ (tmpl["name"], tmpl["name"], "Plantilla personalizada") for tmpl_index, tmpl in enumerate(template_data) ]
	
	def get_effect(self):
		return [e for e in effect_list if e.effect_key == self.effect_type][0]
	
	def get_reversed_effect(self, effect):
		return [e for e in effect_list if e.effect_key == effect.reversed_effect][0]
	
	def is_transform_required(self):
		return ( \
			self.position_x_enabled or \
			self.position_y_enabled or \
			self.zoom_enabled or \
			self.offset_x_enabled or \
			self.offset_y_enabled or \
			self.rotation_enabled)
	
	def is_blur_required(self):
		return (self.blur_x_enabled or self.blur_y_enabled)
	
	def to_dict(self):
		dict_values = {
			"color": (self.color.r, self.color.g, self.color.b),
		}
		
		for plain_property in plain_properties:
			try:
				dict_values[plain_property] = getattr(self, plain_property)
			except Exception as e: # TODO
				print(plain_property, e)
		
		for animatable_property in animatable_properties:
			enabled_property_name = "%s_enabled" % animatable_property
			dict_values[enabled_property_name] = getattr(self, enabled_property_name)
			
			item_dict_array = []
			items_property_name = "%s_items" % animatable_property
			item_collection = getattr(self, items_property_name)
			for item in item_collection:
				item_dict_array.append({
					"value": item.value,
					"position_in_percentage": item.position_in_percentage,
					"interpolation_type": item.interpolation_type,
				})
			
			dict_values[items_property_name] = item_dict_array
		
		return dict_values
	
	def from_dict(self, dict_values):
		for plain_property in plain_properties:
			if plain_property not in excluded_from_template_properties:
				setattr(self, plain_property, dict_values[plain_property])
		
		self.color.r = dict_values["color"][0]
		self.color.g = dict_values["color"][1]
		self.color.b = dict_values["color"][2]
		
		for animatable_property in animatable_properties:
			enabled_property_name = "%s_enabled" % animatable_property
			setattr(self, enabled_property_name, dict_values[enabled_property_name])
			
			items_property_name = "%s_items" % animatable_property
			item_collection = getattr(self, items_property_name)
			item_collection.clear()
			for item in dict_values[items_property_name]:
				item_collection.add()
				item_collection[-1].value = item["value"]
				item_collection[-1].position_in_percentage = item["position_in_percentage"]
				item_collection[-1].interpolation_type = item["interpolation_type"]
		
		return self
