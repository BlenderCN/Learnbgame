import bpy
import os
import cqtc_bpy
from cqtc_operator import CqtcOperator

scene_prefix = "tx"
scene_border_suffix = "Borde"
global_scale_x = 1920
global_scale_y = global_scale_x * (1080/1920)

camera_position_z = 10
camera_ortho_scale = global_scale_x

light_position_z  = 10
bgr_position_z = -0.1

marquee_margin_x = (global_scale_x / 4)

class CreateSubtitleOperator(CqtcOperator):
	bl_idname = "subtitle.create"
	bl_label = "Crear subitulos"
	bl_options = {"REGISTER", "UNDO"}
	
	def execute(self, context):
		error = self.validate_data(context) 
		if error:
			return self.return_error(error)
		
		font_has_border = context.scene.subtitle.font_has_border
		if font_has_border:
			txt_border_object = self.create_subtitle(context, is_border_bgr=True)
			txt_text_object = self.create_subtitle(context, is_border_over=True)
			txt_border_object.location.y = txt_text_object.location.y
		else:
			self.create_subtitle(context)
		
		context.scene.subtitle.scene_name = ""
		context.scene.subtitle.text = ""
		
		return {"FINISHED"}
	
	
	def create_subtitle(self, context, is_border_bgr=False, is_border_over=False):
		text_scene, txt_object = self.create_subtitle_scene(context, is_border_bgr, is_border_over)
		self.create_scene_strip(context, text_scene)
		
		return txt_object
	

	def validate_data(self, context):
		scene_names = [ self.get_scene_name(context) ]
		font_has_border = context.scene.subtitle.font_has_border
		if font_has_border:
			scene_names.append(self.get_border_scene_name(scene_names[0]))
		
		for scene_name in scene_names:
			if scene_name in bpy.data.scenes:
				return "Ya existe una escena llamada " + scene_name
		
		text = context.scene.subtitle.text
		if (scene_name == "" or text == ""):
			return "Debe indicar el nombre de la escena y el texto del subtítulo."
		
		font_path = context.scene.subtitle.font_path
		if font_path != "" and not os.path.isfile(font_path):
			return "No se ha encontrado el fichero " + font_path
		
		is_marquee = context.scene.subtitle.is_marquee
		position = context.scene.subtitle.position
		if is_marquee and (position not in ["bottom", "top", "center"]):
			return "Las marquesinas solo pueden colocarse Arriba, Abajo o en el Centro"
		
		fullscreen_width = context.scene.subtitle.fullscreen_width
		if fullscreen_width and (position not in ["bottom", "top", "center"]):
			return "Los subtítulos de ancho 100% solo pueden colocarse Arriba, Abajo o en el Centro"
	
		
	def create_subtitle_scene(self, context, is_border_bgr, is_border_over):
		current_scene = context.scene
		
		scene_name = self.get_scene_name(context)
		if is_border_bgr:
			scene_name = self.get_border_scene_name(scene_name)
		
		text = context.scene.subtitle.text
		position = context.scene.subtitle.position
		is_marquee = context.scene.subtitle.is_marquee
		fullscreen_width = context.scene.subtitle.fullscreen_width
		font_path = context.scene.subtitle.font_path
		if is_border_bgr:
			font_color = context.scene.subtitle.font_border_color
		else:
			font_color = context.scene.subtitle.font_color
		font_size = context.scene.subtitle.font_size
		font_bevel_depth = context.scene.subtitle.font_bevel_depth
		if is_border_bgr:
			font_bevel_depth += context.scene.subtitle.font_border_size
		font_spacing = context.scene.subtitle.font_spacing
		create_bgr = not is_border_over and context.scene.subtitle.create_bgr
		bgr_color = context.scene.subtitle.bgr_color
		bgr_alpha = context.scene.subtitle.bgr_alpha / 100
		width = context.scene.subtitle.width / 100
		internal_margin = context.scene.subtitle.internal_margin
		external_margin = context.scene.subtitle.external_margin
		
		text_scene = bpy.data.scenes.new(scene_name)
		text_scene.render.alpha_mode = "TRANSPARENT"
		text_scene.render.resolution_percentage = 100
		context.screen.scene = text_scene
		
		old_area_type = context.area.type
		context.area.type = "VIEW_3D"
		
		bpy.ops.object.text_add()		
		txt_object = context.object
		
		if font_path != "":
			font = bpy.data.fonts.load(font_path)
			txt_object.data.font = font
		
		txt_object.data.size = font_size
		txt_object.data.space_line = font_spacing
		txt_object.data.body = text
		txt_object.data.bevel_depth = font_bevel_depth
		
		font_material = cqtc_bpy.create_material("font_material", font_color, (1,1,1), 1)
		txt_object.data.materials.append(font_material)
		
		if not is_marquee:
			if ("right" in position):
				txt_object.data.align_x = "RIGHT"
			elif ("left" in position):
				txt_object.data.align_x = "LEFT"
			else:
				txt_object.data.align_x = "CENTER"
		
			context.scene.update()
			
			max_text_width = width * global_scale_x - (external_margin * 2) - (internal_margin * 2)
			text_width = min(txt_object.dimensions.x, max_text_width)
			if text_width == max_text_width:
				txt_object.data.text_boxes[0].width = text_width
				txt_position_x = -(text_width/2)
			else:
				if ("right" in position):
					txt_position_x = +(text_width/2)
				elif ("left" in position):
					txt_position_x = -(text_width/2)
				else:
					txt_position_x = 0
				
			txt_object.location = txt_position_x, 0, 0
			
		else:
			txt_object.data.align_x = "CENTER"
			txt_object.location = 0, 0, 0
			context.scene.update()
			text_width = txt_object.dimensions.x
		
		context.scene.update()
	
		if not is_marquee:
			if fullscreen_width:
				bgr_dimensions_x = global_scale_x
			else:
				bgr_dimensions_x = text_width + (2 * internal_margin)
		
		else:
			bgr_dimensions_x = text_width + (2 * internal_margin)
			bgr_dimensions_x += (2 * global_scale_x) + (2 * marquee_margin_x)
			
		bgr_dimensions_y = txt_object.dimensions.y + (2 * internal_margin)
		
		if create_bgr:	
			bpy.ops.mesh.primitive_plane_add(location=(0,0,bgr_position_z))
			bgr_object = context.object
			bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
			
			bgr_material = cqtc_bpy.create_material("bgr_material", bgr_color, (1,1,1), bgr_alpha)
			bgr_object.show_transparent = True
			bgr_object.data.materials.append(bgr_material)
			
			bgr_dimensions_z = bgr_object.dimensions.z
			bgr_object.dimensions = bgr_dimensions_x, bgr_dimensions_y, bgr_dimensions_z
		
		delta_x = 0
		delta_y = 0
		if ("top" in position):
			delta_y = (global_scale_y / 2 - (external_margin * 2)) - (bgr_dimensions_y / 2)
		
		if ("bottom" in position):
			delta_y = -((global_scale_y / 2 - (external_margin * 2)) - (bgr_dimensions_y / 2))
		
		if ("right" in position):
			delta_x = (global_scale_x / 2 - (external_margin * 2)) - (bgr_dimensions_x / 2)
		
		if ("left" in position):
			delta_x = -((global_scale_x / 2 - (external_margin * 2)) - (bgr_dimensions_x / 2))
		
		if not is_marquee:
			txt_object.location.x += delta_x
			txt_object.location.y += delta_y
			if create_bgr:
				bgr_object.location.x += delta_x
				bgr_object.location.y += delta_y
		
		bpy.ops.object.camera_add()
		camera = context.object
		camera.location.z = camera_position_z
		camera.data.type = "ORTHO"
		
		if not is_marquee:
			camera.data.ortho_scale = camera_ortho_scale
		else:
			text_scene.render.resolution_x = bgr_dimensions_x
			text_scene.render.resolution_y = bgr_dimensions_y
			camera.data.ortho_scale = bgr_dimensions_x
		
		lamp_data = bpy.data.lamps.new(name="New Lamp", type="SUN")
		lamp_object = bpy.data.objects.new(name="New Lamp", object_data=lamp_data)
		text_scene.objects.link(lamp_object)
		lamp_object.location = (0, 0, light_position_z)
		lamp_object.data.energy = 1
		
		context.scene.update()
		
		error_y = (txt_object.bound_box[0][1] + txt_object.bound_box[2][1]) / 2
		txt_object.location.y -= error_y
		
		context.area.type = old_area_type
		context.screen.scene = current_scene
		
		return text_scene, txt_object
	
	
	def create_scene_strip(self, context, text_scene):
		if not context.scene.subtitle.create_strip:
			return
		
		scene_name = context.scene.subtitle.scene_name
		strip_channel = context.scene.subtitle.strip_channel
		strip_length = context.scene.subtitle.strip_length
		is_marquee = context.scene.subtitle.is_marquee
		current_frame = context.screen.scene.frame_current
		
		if context.scene.sequence_editor is None:
			context.scene.sequence_editor_create()
		
		start_frame = current_frame
		final_frame = start_frame + strip_length
		
		available_channel = cqtc_bpy.get_available_channel_in_position(context, start_frame, final_frame, start_channel=strip_channel)
		text_strip = context.scene.sequence_editor.sequences.new_scene(scene_name, text_scene, available_channel, start_frame)
			
		text_strip.blend_type = "ALPHA_OVER"
		text_strip.frame_final_end = final_frame
		
		if is_marquee:
			text_strip.use_translation = True
			position = context.scene.subtitle.position
			external_margin = context.scene.subtitle.external_margin
			
			size_x = text_strip.scene.render.resolution_x
			size_y = text_strip.scene.render.resolution_y
			
			if position == "center":
				text_strip.transform.offset_y = (global_scale_y - (size_y / 2) - (global_scale_y / 2))
			elif position == "top":
				text_strip.transform.offset_y = (global_scale_y - size_y) - external_margin
			elif position == "bottom":
				text_strip.transform.offset_y = external_margin
			
			text_strip.transform.keyframe_insert("offset_x", index=-1, frame=start_frame)
			cqtc_bpy.set_keyframe_interpolation_type(context, text_strip, "transform.offset_x", start_frame, "LINEAR")
			text_strip.transform.offset_x = -(size_x - global_scale_x)
			text_strip.transform.keyframe_insert("offset_x", index=-1, frame=final_frame)
			cqtc_bpy.set_keyframe_interpolation_type(context, text_strip, "transform.offset_x", final_frame, "LINEAR")
	
	
	def get_scene_name(self, context):
		return scene_prefix + context.scene.subtitle.scene_name

	
	def get_border_scene_name(self, scene_name):
		return scene_name + scene_border_suffix
