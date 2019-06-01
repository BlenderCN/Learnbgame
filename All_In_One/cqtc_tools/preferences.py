import bpy.props
import bpy.types

class CqtcToolsPreferences(bpy.types.AddonPreferences):
	bl_idname = __package__
	
	set_new_scenes_in_current_frame = bpy.props.BoolProperty(
		name="Añadir escenas en el frame actual",
		description="Mover escenas al frame actual cuando se añaden",
		default=False
	)
	
	auto_use_sequence_for_new_scenes = bpy.props.BoolProperty(
		name="Marcar 'usar secuencia'",
		description="Marcar 'usar secuencia' al añadir una escena",
		default=False
	)
	use_sequence_for_new_scenes_pattern = bpy.props.StringProperty(
		name="Patrón",
		description="Marcar 'usar secuencia' para las escenas que cumplan el patrón",
		default="^e.*"
	)
	
	uncheck_use_overwrite_proxy = bpy.props.BoolProperty(
		name="Desmarcar 'Sobreescribir proxy'",
		description="Desmarca la opción 'Sobreescribir' del proxy para las nuevas tiras",
		default=False
	)
	
	auto_proxy_settings_for_new_movies = bpy.props.BoolProperty(
		name="Configurar proxy",
		description="Configurar proxy al añadir una película",
		default=False
	)
	proxy_quality_for_new_movies = bpy.props.IntProperty(
		name="Calidad",
		description="Calidad proxy al añadir una película",
		default=10
	)
	proxy_size_for_new_movies = bpy.props.EnumProperty(
		name="Tamaño",
		description="Tamaño proxy al añadir una película",
		items=[
			( "25",  "25%",  "25"),
			( "50",  "50%",  "50"),
			( "75",  "75%",  "75"),
			("100", "100%", "100"),
		]
	)
	
	auto_blend_for_new_sequences = bpy.props.BoolProperty(
		name="Cambiar tipo de fundido",
		description="Cambiar tipo de fundido al añadir una strip",
		default=False
	)
	
	blend_type_items = [(opt.identifier, opt.name, opt.description, opt.icon, opt.value)
		for opt in bpy.types.Sequence.bl_rna.properties['blend_type'].enum_items]
	
	blend_type_for_new_sequences = bpy.props.EnumProperty(
		name="Tipo de fundidos",
		description = "Tipo de fundido para nuevas strips",
		items=blend_type_items
	)
	
	def draw(self, context):
		layout = self.layout
		
		layout.label("Configuración automática para nuevas tiras")
		split = layout.split()
		
		self.draw_option(layout, "set_new_scenes_in_current_frame")
		
		self.draw_option(layout,
			"auto_use_sequence_for_new_scenes",
			["use_sequence_for_new_scenes_pattern"]
		)
		
		self.draw_option(layout, "uncheck_use_overwrite_proxy")
		
		self.draw_option(layout,
			"auto_proxy_settings_for_new_movies",
			["proxy_quality_for_new_movies", "proxy_size_for_new_movies"]
		)
		self.draw_option(layout,
			"auto_blend_for_new_sequences",
			["blend_type_for_new_sequences"]
		)
	
	def draw_option(self, layout, bool_prop, setting_props=[]):
		split = layout.split()
		split.column().prop(self, bool_prop)
		
		if not getattr(self, bool_prop):
			return
		
		for setting_prop in setting_props:
			split.column().prop(self, setting_prop)
	