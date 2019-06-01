import cqtc_templates
import cqtc_panel

class SuperEffectPanel(cqtc_panel.CqtcPanel):
	bl_label = "Añadir Super Efectos"
	bl_idname = "SCENE_PT_super_effect"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"

	def draw_header(self, context):
		self.layout.label(" ", icon="PARTICLES")
	
	def draw(self, context):
		layout = self.layout
		scene = context.scene
				
		layout.row().prop(context.scene.super_effect, "template")
		
		split = layout.split(percentage=0.33)
		split.column().prop(context.scene.super_effect, "effect_length_type", text="")
		is_in_frames = (context.scene.super_effect.effect_length_type == "FRAMES")
		effect_length_propert = "effect_length" if is_in_frames else "effect_length_percentage"
		split.column().prop(context.scene.super_effect, effect_length_propert)
		layout.row().prop(context.scene.super_effect, "effect_type")
		
		split = layout.row().split(percentage=0.66)
		split.prop(context.scene.super_effect, "image_alignment")
		split.prop(context.scene.super_effect, "image_alignment_margin")
		
		self.draw_selected_sequences_info(layout, context)
		
		row = layout.row()
		split = row.split(percentage=0.66)
		x_col = split.column(align=True)
		col = x_col.row(align=True)
		col.scale_y = 1.5
		
		create_in_operator = col.operator("super_effect.create", text="Entrada", icon="FORWARD")
		create_in_operator.operation_type = "IN"
		
		create_out_operator = col.operator("super_effect.create", text="Salida", icon="BACK")
		create_out_operator.operation_type = "OUT"
		
		row = x_col.row(align=True)
		row.scale_y = 1.5
		create_ind_and_out_operator = row.operator("super_effect.create", text="Entrada y Salida", icon="SMOOTHCURVE")
		create_ind_and_out_operator.operation_type = "IN_OUT"
		
		col = split.column(align=True)
		row = col.row(align=True)
		row.scale_y = 1.5
		create_color_transition_operator = row.operator("super_effect.create", text="Transición SIN color", icon="SEQ_SEQUENCER")
		create_color_transition_operator.add_color_to_transition = False
		create_color_transition_operator.operation_type = "TRANSITION"
		
		row = col.row(align=True)
		row.scale_y = 1.5
		create_transition_operator = row.operator("super_effect.create", text="Transición CON color", icon="SEQ_SPLITVIEW")
		create_transition_operator.add_color_to_transition = True
		create_transition_operator.operation_type = "TRANSITION"
		
		cqtc_templates.draw_template_panel(self, context.scene.super_effect, "super_effect")
		
		row = layout.row()
		row.prop(context.scene.super_effect, "config_expanded",
			icon="TRIA_DOWN" if context.scene.super_effect.config_expanded else "TRIA_RIGHT",
			icon_only=False
		)
		if context.scene.super_effect.config_expanded:
			self.draw_animatable_prop(context, is_in_frames, "position_x")
			self.draw_animatable_prop(context, is_in_frames, "position_y")
			self.draw_animatable_prop(context, is_in_frames, "zoom")
			self.draw_animatable_prop(context, is_in_frames, "opacity")			
			self.draw_animatable_prop(context, is_in_frames, "offset_x")
			self.draw_animatable_prop(context, is_in_frames, "offset_y")
			self.draw_animatable_prop(context, is_in_frames, "rotation")
			self.draw_animatable_prop(context, is_in_frames, "blur_x")
			self.draw_animatable_prop(context, is_in_frames, "blur_y")
			
			split = layout.row().split()
			split.prop(context.scene.super_effect, "apply_to_sound")
			if context.scene.super_effect.apply_to_sound:
				split.prop(context.scene.super_effect, "overlap_sound")
			
			layout.row().prop(context.scene.super_effect, "reverse_out_effect")
			layout.row().prop(context.scene.super_effect, "mirror_horizontal_out_effect")
			layout.row().prop(context.scene.super_effect, "mirror_vertical_out_effect")
			
			layout.row().prop(context.scene.super_effect, "delay_image")
			layout.row().prop(context.scene.super_effect, "speed_factor")
			layout.row().prop(context.scene.super_effect, "sound_file")
			layout.row().prop(context.scene.super_effect, "color")
	
	
	def draw_animatable_prop(self, context, is_in_frames, property_name):
		layout = self.layout
		
		property_enabled_name = "%s_enabled" % property_name
		if property_enabled_name not in dir(context.scene.super_effect):
			print("Property '%s' not found" % property_enabled_name)
			
		property_items_name = "%s_items" % property_name
		if property_items_name not in dir(context.scene.super_effect):
			print("Property '%s' not found" % property_items_name)
		
		if not getattr(context.scene.super_effect, property_enabled_name):
			layout.row().prop(context.scene.super_effect, property_enabled_name)
			return
		
		property_items = getattr(context.scene.super_effect, property_items_name)
		property_items_length = len(property_items)
		if property_items_length < 2:
			self.draw_single_item_prop(context, property_name, property_enabled_name, property_items)
		else:
			self.multiple_item_prop(context, property_name, property_enabled_name, property_items)
	
	
	def draw_single_item_prop(self, context, property_name, property_enabled_name, property_items):
		layout = self.layout
		
		split = layout.split(percentage=0.25)
		split.column().prop(context.scene.super_effect, property_enabled_name)
		
		if len(property_items):
			split = split.column().split(0.8866)
			row = split.column().row()
			row.column().prop(property_items[0], "position_in_percentage")
			row.column().prop(property_items[0], "value", text="Valor")
		
		col = split.column()
		add_property_operator = col.operator("super_effect.modify_property", text="", icon="PLUS")
		add_property_operator.property_name = property_name
		add_property_operator.operation = "add"
	
	
	def multiple_item_prop(self, context, property_name, property_enabled_name, property_items):
		layout = self.layout
		
		layout.row().prop(context.scene.super_effect, property_enabled_name)
		split = layout.split(percentage=0.05)
		split.column()
		
		split = split.column().split(percentage=0.1)
		left_col = split.column()
		right_col = split.column()
		
		for item_index, item in enumerate(property_items):
			split = right_col.split(percentage=0.9)
			prop_col = split.column()
			prop_split = prop_col.split(percentage=0.8)
			
			row = prop_split.column().row()
			row.column().prop(item, "position_in_percentage")
			row.column().prop(item, "value", text="Valor")
			prop_split.column().prop(item, "interpolation_type", text="")
			
			prop_col = split.column()
			remove_property_operator = left_col.operator("super_effect.modify_property", text="", icon="X")
			remove_property_operator.property_name = property_name
			remove_property_operator.operation = "remove"
			remove_property_operator.index_to_remove = item_index
		
		add_property_operator = prop_col.operator("super_effect.modify_property", text="", icon="PLUS")
		add_property_operator.property_name = property_name
		add_property_operator.operation = "add"
