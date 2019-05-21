import bpy
import os
from . import templates

default_font = r"c:\windows\Fonts\CURLZ___.TTF"
if not os.path.isfile(default_font):
	default_font = r"c:\windows\Fonts\Curlz_MT.ttf"

default_font_size = 150
default_font_bevel_depth = 0
default_font_spacing = 0.7
default_internal_margin = 25
default_external_margin = 45

def get_subtitle_template_options(scene, context):
	return sorted(context.scene.subtitle.template_options, key= lambda opt : opt[0].lower())

def load_template(self, context):
	bpy.ops.subtitle.load_template()

def set_create_bgr_if_fullscreen_width(self, context):
	if context.scene.subtitle.fullscreen_width:
		context.scene.subtitle.create_bgr = True

def set_fullscreen_width_if_not_create_bgr(self, context):
	if not context.scene.subtitle.create_bgr:
		context.scene.subtitle.fullscreen_width = False

class SubtitlesProperties(bpy.types.PropertyGroup):
	scene_name = bpy.props.StringProperty(name="Nombre escena", description="Nombre de la escena")
	text = bpy.props.StringProperty(name="Texto", description="Texto")
	config_expanded = bpy.props.BoolProperty(name="Configuración", default=True)
	
	position = bpy.props.EnumProperty(
			name = "Posición",
			description = "Posición de los subtítulos",
			items = [
				("center", "Centro", "Centrado"),
				("top", "Arriba", "En la parte superior"),
				("bottom", "Abajo", "En la parte inferior"),
				("left", "Izquierda", "En la parte izquierda"),
				("right", "Derecha", "En la parte derecha"),
				("top_left", "Arriba Izquierda", "En la parte superior izquierda"),
				("top_right", "Arriba Derecha", "En la parte superior derecha"),
				("bottom_left", "Abajo Izquierda", "En la parte inferior izquierda"),
				("bottom_right", "Abajo Derecha", "En la parte inferior derecha"),
			]
		)
	
	is_marquee = bpy.props.BoolProperty(name="Marquesina", default=False)
	fullscreen_width = bpy.props.BoolProperty(name="Ancho 100%", default=False, update=set_create_bgr_if_fullscreen_width)
	font_path = bpy.props.StringProperty(name="Fuente", subtype="FILE_PATH", description="Fuente", default=default_font)
	font_color = bpy.props.FloatVectorProperty(name="Color texto", subtype="COLOR", default=(0.0, 0.0, 0.0), min=0.0, max=1.0)
	font_size = bpy.props.IntProperty(name="Tamaño", default=default_font_size, min=1, max=500, step=1)
	font_bevel_depth = bpy.props.FloatProperty(name="Nivel negrita", default=default_font_bevel_depth, min=0, max=5, step=0.5)
	
	font_has_border = bpy.props.BoolProperty(name="Borde", default=False)
	font_border_size = bpy.props.FloatProperty(name="Tamaño del borde", default=0, min=0, max=5, step=0.5)
	font_border_color = bpy.props.FloatVectorProperty(name="Color del borde", subtype="COLOR", default=(1.0, 1.0, 1.0), min=0.0, max=1.0)
	
	font_spacing = bpy.props.FloatProperty(name="Espaciado", default=default_font_spacing, min=0, max=2, step=0.1)
	width = bpy.props.FloatProperty(name="Ancho", default=90.0, min=0, max=100, step=10, precision=2, subtype="PERCENTAGE")
	internal_margin = bpy.props.IntProperty(name="Margen interior", default=default_internal_margin, min=0, max=1000, step=1)
	external_margin = bpy.props.IntProperty(name="Margen exterior", default=default_external_margin, min=0, max=1000, step=1)
	
	font_expanded = bpy.props.BoolProperty(name="Fuente", default=True)
	
	create_bgr = bpy.props.BoolProperty(name="Fondo", default=True, update=set_fullscreen_width_if_not_create_bgr)
	bgr_color = bpy.props.FloatVectorProperty(name="Color fondo", subtype="COLOR", default=(1.0, 1.0, 1.0), min=0.0, max=1.0)
	bgr_alpha = bpy.props.FloatProperty(name="Opacidad fondo", default=75.0, min=0, max=100, step=5, precision=2, subtype="PERCENTAGE")
	
	create_strip = bpy.props.BoolProperty(name="Crear strip", default=True)
	strip_channel = bpy.props.IntProperty(name="Canal del Strip", default=1, min=1, max=20, step=1)
	strip_length = bpy.props.IntProperty(name="Longitud del Strip", default=100, min=1, max=2000, step=20)
	
	template_expanded = bpy.props.BoolProperty(name="Plantillas", default=True)
	
	template = bpy.props.EnumProperty(
			name = "Plantillas",
			description = "Plantillas guardadas por el usuario",
			items = get_subtitle_template_options,
			update = load_template
		)
	
	new_template_name = bpy.props.StringProperty(name="Nombre plantilla", description="Nombre para la nueva plantilla")
	override_template = bpy.props.BoolProperty(name="Sobreescribir Plantilla", default=False)
		
	template_data = templates.load_templates()
	template_options = [ (tmpl["name"], tmpl["name"], "Plantilla personalizada") for tmpl in template_data ]
	
	def to_dict(self):
		return {
			"scene_name": self.scene_name,
			"text": self.text,
			"position": self.position,
			"is_marquee": self.is_marquee,
			"fullscreen_width": self.fullscreen_width,
			"font_path": self.font_path,
			"font_color": (self.font_color.r, self.font_color.g, self.font_color.b),
			"font_size": self.font_size,
			"font_bevel_depth": self.font_bevel_depth,
			"font_has_border": self.font_has_border,
			"font_border_size": self.font_border_size,
			"font_border_color": (self.font_border_color.r, self.font_border_color.g, self.font_border_color.b),
			"font_spacing": self.font_spacing,
			"create_bgr": self.create_bgr,
			"bgr_color": (self.bgr_color.r, self.bgr_color.g, self.bgr_color.b),
			"bgr_alpha": self.bgr_alpha,
			"width": self.width,
			"internal_margin": self.internal_margin,
			"external_margin": self.external_margin,
			"create_strip": self.create_strip,
			"strip_channel": self.strip_channel,
			"strip_length": self.strip_length,
		}
	
	
	def from_dict(self, tmpl):
		if self.scene_name == "":
			self.scene_name = tmpl["scene_name"]
			
		if self.text == "":
			self.text = tmpl["text"]
			
		self.position = tmpl["position"]
		self.is_marquee = tmpl["is_marquee"] if "is_marquee" in tmpl else False
		self.fullscreen_width = tmpl["fullscreen_width"] if "fullscreen_width" in tmpl else False
		self.font_path = tmpl["font_path"]
		self.font_color.r = tmpl["font_color"][0]
		self.font_color.g = tmpl["font_color"][1]
		self.font_color.b = tmpl["font_color"][2]
		self.font_size = tmpl["font_size"]
		self.font_bevel_depth = tmpl["font_bevel_depth"] if "font_bevel_depth" in tmpl else default_font_bevel_depth
		self.font_has_border = tmpl["font_has_border"] if "font_has_border" in tmpl else False
		self.font_border_size = tmpl["font_border_size"] if "font_border_size" in tmpl else 0
		self.font_border_color.r = tmpl["font_border_color"][0] if "font_border_color" in tmpl else 1
		self.font_border_color.g = tmpl["font_border_color"][1] if "font_border_color" in tmpl else 1
		self.font_border_color.b = tmpl["font_border_color"][2] if "font_border_color" in tmpl else 1
		self.font_spacing = tmpl["font_spacing"]
		self.create_bgr = tmpl["create_bgr"]
		self.bgr_color.r = tmpl["bgr_color"][0]
		self.bgr_color.g = tmpl["bgr_color"][1]
		self.bgr_color.b = tmpl["bgr_color"][2]
		self.bgr_alpha = tmpl["bgr_alpha"]
		self.width = tmpl["width"]
		self.internal_margin = tmpl["internal_margin"]
		self.external_margin = tmpl["external_margin"]
		self.create_strip = tmpl["create_strip"]
		self.strip_channel = tmpl["strip_channel"]
		self.strip_length = tmpl["strip_length"]
	
	
	def test(self):
		test_scene_prefix = "Rjv"
		single_line_width = 90
		multi_line_width = 40
		
		length = bpy.context.scene.subtitle.strip_length
		prueba_data = [
			["Centro", "Prueba centro", "center", length, False, False, False, 0, (0,0,0)],
			
			["Arriba",    "Prueba arriba",    "top", 0, False, False, False, 0, (0,0,0)],
			["Abajo",     "Prueba abajo",     "bottom", 0, False, False, False, 0, (0,0,0)],
			["Izquierda", "Prueba izquierda", "left", 0, False, False, False, 0, (0,0,0)],
			["Derecha",   "Prueba derecha",   "right", length, False, False, False, 0, (0,0,0)],
			
			["ArribaIzq", "Prueba arriba izq", "top_left", 0, False, False, False, 0, (0,0,0)],
			["ArribaDch", "Prueba arriba dch", "top_right", 0, False, False, False, 0, (0,0,0)],
			["AbajoIzq",  "Prueba abajo izq",  "bottom_left", 0, False, False, False, 0, (0,0,0)],
			["AbajoDch",  "Prueba abajo dch",  "bottom_right", length, False, False, False, 0, (0,0,0)],
			
			["MarquesinaArriba",  "Prueba marquesina arriba",  "top", 0, True, False, False, 0, (0,0,0)],
			["MarquesinaCentro",  "Prueba marquesina centro",  "center", 0, True, False, False, 0, (0,0,0)],
			["MarquesinaAbajo",   "Prueba marquesina abajo",   "bottom", length, True, False, False, 0, (0,0,0)],
			
			["CentroSinAjustar", "Prueba centro sin ajustar", "center", 0, False, False, False, 0, (0,0,0)],
			["ArribaSinAjustar", "Prueba arriba sin ajustar", "top", 0, False, False, False, 0, (0,0,0)],
			["AbajoSinAjustar",  "Prueba abajo sin ajustar",  "bottom", length, False, False, False, 0, (0,0,0)],
			
			["CentroBorde", "Prueba centro", "center", length, False, False, True, 2, (1,0,0)],
		]
		
		bpy.context.screen.scene.frame_current = 1
		for prueba in prueba_data:
			bpy.context.scene.subtitle.scene_name = test_scene_prefix + prueba[0]
			bpy.context.scene.subtitle.text = prueba[1]
			bpy.context.scene.subtitle.position = prueba[2]
			bpy.context.scene.subtitle.is_marquee = prueba[4]
			bpy.context.scene.subtitle.fullscreen_width = prueba[5]
			bpy.context.scene.subtitle.font_has_border = prueba[6]
			bpy.context.scene.subtitle.font_border_size = prueba[7]
			bpy.context.scene.subtitle.font_border_color.r = prueba[8][0]
			bpy.context.scene.subtitle.font_border_color.g = prueba[8][1]
			bpy.context.scene.subtitle.font_border_color.b = prueba[8][2]
			bpy.context.scene.subtitle.width = single_line_width
			bpy.ops.subtitle.create()
			bpy.context.screen.scene.frame_current += prueba[3]
		
		for prueba in prueba_data:
			is_marquee = prueba[4]
			fullscreen_width = prueba[5]
			if is_marquee or fullscreen_width:
				continue
			
			bpy.context.scene.subtitle.scene_name = test_scene_prefix + prueba[0] + "ML"
			bpy.context.scene.subtitle.text = prueba[1] + " multi línea bla bla bla bla"
			bpy.context.scene.subtitle.position = prueba[2]
			bpy.context.scene.subtitle.is_marquee = False
			bpy.context.scene.subtitle.fullscreen_width = False
			bpy.context.scene.subtitle.font_has_border = prueba[6]
			bpy.context.scene.subtitle.font_border_size = prueba[7]
			bpy.context.scene.subtitle.font_border_color.r = prueba[8][0]
			bpy.context.scene.subtitle.font_border_color.g = prueba[8][1]
			bpy.context.scene.subtitle.font_border_color.b = prueba[8][2]
			bpy.context.scene.subtitle.width = multi_line_width
			bpy.ops.subtitle.create()
			bpy.context.screen.scene.frame_current += prueba[3]

		bpy.context.screen.scene.frame_current = 1
