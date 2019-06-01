import cqtc_bpy
import math

global_scale_x = 1920
global_scale_y = int(global_scale_x * (1080/1920))		
effectable_strip_types = ["COLOR","IMAGE","MOVIE","SCENE","TRANSFORM","CROSS","GAUSSIAN_BLUR","SPEED","META"]
transitionable_strip_types = ["COLOR","IMAGE","MOVIE","SCENE","TRANSFORM","CROSS","GAUSSIAN_BLUR","SPEED","META"]
sound_capable_strip_types = ["COLOR","IMAGE","MOVIE","TRANSFORM","CROSS","GAUSSIAN_BLUR","SPEED"]
speedable_not_sound_strip_types = ["MOVIE","SCENE","TRANSFORM","CROSS","GAUSSIAN_BLUR","META"]

def get_rotation_values_fn(item, previous):
	item_value = item.value
	if abs(item_value) <= 360:
		return [-item_value]
	
	if previous is None:
		value = (item_value % 360) + (360 if item_value >= 360 else 0)
		return [-value]
	
	previous_value = previous.value
	
	current_value = item_value
	values = []
	
	full_increments = (abs(item_value - previous_value) // 360)
	initial_partial_increment = ((item_value - previous_value) % 360 != 0)
	
	is_first_step_bigger_than_360 = abs(previous_value - math.copysign(360, item_value)) > 360
	remove_one_increment = (not initial_partial_increment)
	if remove_one_increment:
		full_increments -= 1
	
	if is_first_step_bigger_than_360:
		full_increments -= 1
	
	inc_range = range(full_increments)
	#print("\n", full_increments, initial_partial_increment, is_first_step_bigger_than_360, list(inc_range))
	for inc in inc_range:
		if inc > 0 or (not initial_partial_increment and previous_value != 0 and not is_first_step_bigger_than_360):
			values.append(0)
		values.append(-math.copysign(360, item_value))
	
	values.append(0)
	value = math.copysign((item_value % 360) + (360 if abs(item_value % 360) == 0 else 0), item_value)
	values.append(-value)
	
	return values

		
class SuperEffectCreator():
	
	def create(self, context, operation_type, add_color_to_transition=False):
		error = self.__validate_global(context, operation_type)
		if error:
			return error
		
		for sequence in context.selected_sequences.copy():
			cqtc_bpy.unselect_children(sequence)
			image_alignment = context.scene.super_effect.image_alignment
			image_alignment_margin = context.scene.super_effect.image_alignment_margin
			cqtc_bpy.align_image(context, sequence, image_alignment, image_alignment_margin)
		
		is_second_in_or_out = False
		for in_or_out in ["IN", "OUT"]:
			if (in_or_out in operation_type):
				error = self.__create_in_or_out_effect(context, in_or_out, is_second_in_or_out)
				if error:
					return error
					
				is_second_in_or_out = True
		
		if (operation_type == "TRANSITION"):
			error = self.__create_transition(context, add_color_to_transition)
			if error:
				return error
	
	
	def __validate_global(self, context, operation_type):
		is_effect_length_percentage_over_limit = (operation_type == "IN_OUT" 
			and context.scene.super_effect.effect_length_type == "PERCENTAGE"
			and context.scene.super_effect.effect_length_percentage > 50)
		
		if is_effect_length_percentage_over_limit:
			return "No se puede crear un efecto de Entrada y Salida con más del 50% de porcentage de duración"
	
	
	def __validate_in_or_out_effect(self, context, is_in):

		selected_not_sound_sequences = [s for s in context.selected_sequences if s.type in effectable_strip_types]
		if len(selected_not_sound_sequences) == 0:
			return "Debes seleccionar al menos una strip que no sea de tipo sonido"
		
		effect_length = context.scene.super_effect.effect_length
		delay_image = context.scene.super_effect.delay_image
		if context.scene.super_effect.effect_length_type == "FRAMES":
			min_length = effect_length
			if is_in:
				min_length += delay_image
				
			for sequence in selected_not_sound_sequences:
				if sequence.frame_final_duration < min_length:
					return "La strip " + sequence.name + " es más corta de lo necesario para añdir el efecto"
			
		selected_sound_capable_sequences = [s for s in context.selected_sequences if s.type in sound_capable_strip_types]
		selected_sound_sequences = [s for s in context.selected_sequences if s.type == "SOUND"]
		if len(selected_sound_sequences) > len(selected_sound_capable_sequences):
			return "No puedes seleccionar más strips de sonido que strips de imagen, vídeo o transform"

		for selected_sound_sequence in selected_sound_sequences:
			not_sound_sequence_matches = [ nss for nss in selected_sound_capable_sequences \
				if (nss.frame_final_start == selected_sound_sequence.frame_final_start \
					or nss.frame_final_end == selected_sound_sequence.frame_final_end)]
					
			if len(not_sound_sequence_matches) == 0:
				return "La strip de sonido " + selected_sound_sequence.name + " no corresponde con ninguna strip de imagen, vídeo o transform"
	
	
	def __validate_transition(self, context):
		selected_not_sound_sequences = [s for s in context.selected_sequences if s.type in transitionable_strip_types]
		if len(selected_not_sound_sequences) != 2:
			return "Debes seleccionar dos (y SOLO dos) strips que no sean de sonido"
			
		selected_sound_sequences = [s for s in context.selected_sequences if s.type == "SOUND"]
		if len(selected_sound_sequences) > 2:
			return "Puedes seleccionar dos strips de sonido como máximo"
			
		for selected_sound_sequence in selected_sound_sequences:
			selected_sound_capable_sequences = [s for s in context.selected_sequences if s.type in sound_capable_strip_types]
			not_sound_sequence_matches = [ nss for nss in selected_sound_capable_sequences \
				if (nss.frame_final_start == selected_sound_sequence.frame_final_start \
					and nss.frame_final_end == selected_sound_sequence.frame_final_end)]
					
			if len(not_sound_sequence_matches) == 0:
				return "La strip de sonido " + selected_sound_sequence.name + " no corresponde con ninguna strip de imagen, vídeo"
			
		if context.scene.super_effect.effect_length_type == "PERCENTAGE":
			return "No se puede añadir una transición con una duración de tipo porcentaje"
		
		strip_tmp_1 = selected_not_sound_sequences[0]
		strip_tmp_2 = selected_not_sound_sequences[1]
		if (strip_tmp_1.frame_final_start == strip_tmp_2.frame_final_start and strip_tmp_1.frame_final_end == strip_tmp_2.frame_final_end):
			return "Para añadir una transición las tiras no pueden estar en la misma posición"
	
	
	def __validate_transition_without_color(self, context, seq1, seq2, seq1_sound, seq2_sound):
		if seq1.frame_final_end < seq2.frame_final_start:
			return "Para añadir una transición sin color intermedio las tiras deben solaparse o ser consecutivas"
			
		if seq1.frame_final_end == seq2.frame_final_start:
			effect_length = context.scene.super_effect.effect_length
			return cqtc_bpy.overlap_strips(context, effect_length, seq1, seq2, seq1_sound, seq2_sound)
	
	
	def __validate_transition_with_color(self, seq1, seq2):
		if seq1.frame_final_end > seq2.frame_final_start:
			return "Para añadir una transición con color intermedio las tiras no pueden solaparse"
	
	
	def __create_in_or_out_effect(self, context, in_or_out, is_second_in_or_out):
		is_in = (in_or_out == "IN")
		error = self.__validate_in_or_out_effect(context, is_in)
		if error:
			return error

		effect = context.scene.super_effect.get_effect()
		if (not is_in) and context.scene.super_effect.reverse_out_effect:
			effect = context.scene.super_effect.get_reversed_effect(effect)
		
		selected_sequences = context.selected_sequences.copy()			
		for sequence in selected_sequences:
			self.__create_in_or_out_strip_effect(context, effect, is_in, sequence, is_second_in_or_out)
			
			if not is_second_in_or_out:
				self.__create_in_or_out_strip_sound_effect(context, sequence)
						
	
	def __create_in_or_out_strip_sound_effect(self, context, sequence):
		sound_file = context.scene.super_effect.sound_file
		if not sound_file:
			return
		
		if sequence.type not in sound_capable_strip_types:
			return
		
		sound_strip = context.scene.sequence_editor.sequences.new_sound(sequence.name + "_SonidoEfecto", sound_file, -1, sequence.frame_final_start)
		sound_strip.select = False
		
		sound_final_frame = sound_strip.frame_final_end
		while sound_final_frame < sequence.frame_final_end:
			sound_strip = context.scene.sequence_editor.sequences.new_sound(sequence.name + "_SonidoEfecto", sound_file, -1, sound_final_frame + 1)					
			sound_strip.select = False
			sound_final_frame = sound_strip.frame_final_end
			
		if sound_strip.frame_final_end > sequence.frame_final_end:
			sound_strip.frame_final_end = sequence.frame_final_end
	
	
	def __create_in_or_out_strip_effect(self, context, effect, is_in, sequence, is_second_in_or_out):

		if not is_second_in_or_out:
			sequence = self.__add_speed_strip(context, sequence)
		
		delay_image = context.scene.super_effect.delay_image
		effect_length = context.scene.super_effect.effect_length \
			if context.scene.super_effect.effect_length_type == "FRAMES" \
			else int(context.scene.super_effect.effect_length_percentage * sequence.frame_final_duration / 100)
		
		if is_in:
			start_frame = sequence.frame_final_start
			final_frame = sequence.frame_final_start + effect_length
				
		else:
			start_frame = sequence.frame_final_end - effect_length
			final_frame = sequence.frame_final_end
		
		if context.scene.super_effect.apply_to_sound:
			self.__apply_effect_sound_transition(sequence, start_frame, final_frame, effect_length, is_in)
		
		if sequence.type in effectable_strip_types:
			animatable_properties_info = [ (sequence, sequence, "blend_alpha", "opacity", {}) ]
			self.__set_animatable_properties(context, animatable_properties_info, is_in, start_frame, final_frame)
			
			original_sequence = sequence
			sequence = self.__add_transform_strip(context, sequence, start_frame, final_frame, is_in)
			sequence = self.__add_blur_strip(context, sequence, start_frame, final_frame, is_in)
			
			color_final_frame = final_frame
			if is_in:
				 color_final_frame += delay_image
				 
			channel = cqtc_bpy.get_available_channel_in_position(context, start_frame, color_final_frame, sequence.channel)
			color_strip = effect.create_color_strip(context, channel, start_frame, color_final_frame, original_sequence.name)
			
			seq1 = color_strip if is_in else sequence
			seq2 = sequence if is_in else color_strip
			if is_in:
				 original_sequence.frame_offset_start += delay_image
				 
			channel = cqtc_bpy.get_available_channel_in_position(context, start_frame, final_frame, channel)
			effect_strip = effect.create_effect_strip(context, channel, start_frame, final_frame, seq1, seq2, original_sequence.name)
		
			original_sequence.select = False
			sequence.select = True
	
	
	def __create_transition(self, context, add_color_to_transition):
		error = self.__validate_transition(context)
		if error:
			return error
		
		selected_not_sound_sequences = [s for s in context.selected_sequences if s.type in transitionable_strip_types]
		strip_tmp_1 = selected_not_sound_sequences[0]
		strip_tmp_2 = selected_not_sound_sequences[1]
		
		is_seq1_before_seq2 = (strip_tmp_1.frame_final_start < strip_tmp_2.frame_final_start)
		seq1 = strip_tmp_1 if is_seq1_before_seq2 else strip_tmp_2
		seq2 = strip_tmp_2 if is_seq1_before_seq2 else strip_tmp_1
		
		(seq1_sound, seq2_sound) = self.__get_transition_sound_sequences(context, seq1, seq2)
		
		if add_color_to_transition:
			return self.__create_transition_with_color(context, seq1, seq2, seq1_sound, seq2_sound)
		
		else:
			return self.__create_transition_without_color(context, seq1, seq2, seq1_sound, seq2_sound)
	
	
	def __create_transition_without_color(self, context, seq1, seq2, seq1_sound, seq2_sound):
		error = self.__validate_transition_without_color(context, seq1, seq2, seq1_sound, seq2_sound)
		if error:
			return error
			
		start_frame = seq2.frame_final_start
		final_frame = seq1.frame_final_end
		
		seq1 = self.__add_blur_strip(context, seq1, start_frame, final_frame, is_in=False)
		seq1 = self.__add_transform_strip(context, seq1, start_frame, final_frame, is_in=False)
		seq2 = self.__add_blur_strip(context, seq2, start_frame, final_frame, is_in=True)
		seq2 = self.__add_transform_strip(context, seq2, start_frame, final_frame, is_in=True)
		
		effect = context.scene.super_effect.get_effect()
		
		max_channel = max([s.channel for s in context.selected_sequences])
		channel = cqtc_bpy.get_available_channel_in_position(context, start_frame, final_frame, max_channel)
		effect_strip = effect.create_effect_strip(context, channel, start_frame, final_frame, seq1, seq2)
						
		if context.scene.super_effect.apply_to_sound:
			self.__apply_overlapped_sound_transition(context, seq1_sound, seq2_sound, start_frame, final_frame)
	
	
	def __create_transition_with_color(self, context, seq1, seq2, seq1_sound, seq2_sound):
		error = self.__validate_transition_with_color(seq1, seq2)
		if error:
			return error
	
		effect_length = context.scene.super_effect.effect_length
		half_effect_length = int(effect_length / 2)
		
		start_frame = seq1.frame_final_end - half_effect_length
		final_frame = seq2.frame_final_start + half_effect_length
		delay_image = context.scene.super_effect.delay_image
		effect = context.scene.super_effect.get_effect()

		seq1 = self.__add_blur_strip(context, seq1, start_frame, seq1.frame_final_end, is_in=False)
		seq1 = self.__add_transform_strip(context, seq1, start_frame, seq1.frame_final_end, is_in=False)
		seq2 = self.__add_blur_strip(context, seq2, seq2.frame_final_start, final_frame, is_in=True)
		seq2 = self.__add_transform_strip(context, seq2, seq2.frame_final_start, final_frame, is_in=True)

		color_channel = cqtc_bpy.get_available_channel_in_position(context, start_frame, final_frame + delay_image, max(seq1.channel, seq2.channel))
		color_strip = effect.create_color_strip(context, color_channel, start_frame, final_frame + delay_image)
		
		seq1_effect = effect if not context.scene.super_effect.reverse_out_effect \
			else context.scene.super_effect.get_reversed_effect(effect)
		
		channel = cqtc_bpy.get_available_channel_in_position(context, start_frame, seq1.frame_final_end, color_channel)
		effect_strip = seq1_effect.create_effect_strip(context, channel, start_frame, seq1.frame_final_end, seq1, color_strip)
		
		channel = cqtc_bpy.get_available_channel_in_position(context, seq2.frame_final_start, final_frame + delay_image, color_channel)
		effect_strip = effect.create_effect_strip(context, channel, seq2.frame_final_start, final_frame + delay_image, color_strip, seq2)
		
		seq2.frame_offset_start += delay_image
		
		if context.scene.super_effect.apply_to_sound:
			self.__apply_consecutive_sound_transition(seq1_sound, seq2_sound, start_frame, final_frame, half_effect_length)
	
	
	def __add_speed_strip(self, context, sequence):
		is_speed_required = (context.scene.super_effect.speed_factor != 1)
		if not is_speed_required:
			return sequence
	
		speed_factor = context.scene.super_effect.speed_factor
		sequence_to_return = sequence

		if sequence.type in speedable_not_sound_strip_types:
			(sequence, sequence_to_return) = self.__create_or_get_existing_effect_strip(sequence, context, "SPEED", "_Speed")
			sequence.use_default_fade = False
			sequence.speed_factor = speed_factor
			
			if speed_factor > 0:
				original_sequence = sequence
				tmp_sequence = sequence
				while "input_1" in dir(original_sequence) and original_sequence.input_1 is not None:
					tmp_sequence = tmp_sequence.input_1
					if tmp_sequence.type in ["MOVIE","SCENE","META"]:
						original_sequence = tmp_sequence
				
				sequence_new_length = (original_sequence.frame_final_duration / speed_factor)
				original_sequence.frame_final_end = (original_sequence.frame_final_start + sequence_new_length)
			
		elif sequence.type == "SOUND":
			sequence.pitch = speed_factor
			if speed_factor > 0:
				sequence_new_length = (sequence.frame_final_duration / speed_factor)
				sequence.frame_final_end = (sequence.frame_final_start + sequence_new_length)
			
		return sequence_to_return
	
	
	def __add_transform_strip(self, context, sequence, start_frame, final_frame, is_in):
		is_transform_required = context.scene.super_effect.is_transform_required()
		if not is_transform_required:
			return sequence

		selected_keyframes = cqtc_bpy.deselect_selected_keyframe_points(context)
		(sequence, sequence_to_return) = self.__create_or_get_existing_effect_strip(sequence, context, "TRANSFORM", "_Transform")
		
		sequence.use_uniform_scale = True
		sequence.use_translation = True
		
		is_small_image = (sequence.type == "IMAGE" 
			and len(sequence.elements) > 0
			and (
				sequence.elements[0].orig_width != context.scene.render.resolution_x
				or sequence.elements[0].orig_height != context.scene.render.resolution_y
			)
		)
		if is_small_image:
			# TODO OUT offset_x / offset_y effect on small images
			base_offset_x = sequence.transform.offset_x
			base_offset_y = sequence.transform.offset_y
		else:
			base_offset_x = 0
			base_offset_y = 0
		
		get_offset_x_values_fn = lambda item, previous : [(base_offset_x + (global_scale_x * item.value / 100))]
		get_offset_y_values_fn = lambda item, previous : [(base_offset_y + (global_scale_y * item.value / 100))]
		
		animatable_properties_info = [
			(sequence, sequence, "translate_start_x", "position_x", {"is_horizontal_mirrorable"}),
			(sequence, sequence, "translate_start_y", "position_y", {"is_vertical_mirrorable"}),
			(sequence, sequence, "scale_start_x", "zoom", {}),
			(sequence, sequence, "blend_alpha", "opacity", {}),
			(sequence, sequence.transform, "offset_x", "offset_x", {"is_horizontal_mirrorable": True, "get_values_fn": get_offset_x_values_fn }),
			(sequence, sequence.transform, "offset_y", "offset_y", {"is_vertical_mirrorable": True, "get_values_fn": get_offset_y_values_fn }),
			(sequence, sequence, "rotation_start", "rotation", { "get_values_fn": get_rotation_values_fn })
		]
		self.__set_animatable_properties(context, animatable_properties_info, is_in, start_frame, final_frame)
		
		cqtc_bpy.select_keyframe_points(context, selected_keyframes)
		
		return sequence_to_return
	
	
	def __add_blur_strip(self, context, sequence, start_frame, final_frame, is_in):
		is_blur_required = context.scene.super_effect.is_blur_required()
		if not is_blur_required:
			return sequence
		
		selected_keyframes = cqtc_bpy.deselect_selected_keyframe_points(context)
		(sequence, sequence_to_return) = self.__create_or_get_existing_effect_strip(sequence, context, "GAUSSIAN_BLUR", "_Blur")
		
		animatable_properties_info = [
			(sequence, sequence, "size_x", "blur_x", {}),
			(sequence, sequence, "size_y", "blur_y", {}),
			(sequence, sequence, "blend_alpha", "opacity", {}) 
		]
		self.__set_animatable_properties(context, animatable_properties_info, is_in, start_frame, final_frame)
		
		cqtc_bpy.select_keyframe_points(context, selected_keyframes)
		
		return sequence_to_return
	
	
	def __apply_effect_sound_transition(self, seq_sound, start_frame, final_frame, effect_length, is_in):
		initial_volume = 0 if is_in else 1
		final_volume = 1 if is_in else 0
			
		if seq_sound.type == "SOUND":
			volume_start_frame = start_frame
			volume_final_frame = final_frame

			cqtc_bpy.animate_volume(seq_sound, initial_volume, final_volume, volume_start_frame, volume_final_frame)

		elif seq_sound.type == "SCENE":
			if is_in:
				volume_start_frame = 1
				volume_final_frame = effect_length + 1
			else:
				volume_start_frame = seq_sound.scene.frame_end - effect_length
				volume_final_frame = seq_sound.scene.frame_end
			
			cqtc_bpy.animate_volume(seq_sound, initial_volume, final_volume, volume_start_frame, volume_final_frame)
	
	
	def __apply_consecutive_sound_transition(self, seq1_sound, seq2_sound, start_frame, final_frame, half_effect_length):
		if seq1_sound is not None:
			if seq1_sound.type == "SOUND":
				seq1_volume_start_frame = start_frame
				seq1_volume_final_frame = seq1_sound.frame_final_end
			elif seq1_sound.type == "SCENE":
				seq1_volume_start_frame = seq1_sound.scene.frame_end - half_effect_length
				seq1_volume_final_frame = seq1_sound.scene.frame_end
			
			cqtc_bpy.animate_volume(seq1_sound, 1, 0, seq1_volume_start_frame, seq1_volume_final_frame)
				
		if seq2_sound is not None:
			if seq2_sound.type == "SOUND":
				seq2_volume_start_frame = seq2_sound.frame_final_start
				seq2_volume_final_frame = final_frame
			elif seq2_sound.type == "SCENE":
				seq2_volume_start_frame = 1
				seq2_volume_final_frame = half_effect_length + 1
			
			cqtc_bpy.animate_volume(seq2_sound, 0, 1, seq2_volume_start_frame, seq2_volume_final_frame)
	
	
	def __apply_overlapped_sound_transition(self, context, seq1_sound, seq2_sound, start_frame, final_frame):
		if context.scene.super_effect.overlap_sound:
		
			effect_length = (final_frame - start_frame)
			if seq1_sound is not None:
				if seq1_sound.type == "SOUND":
					seq1_volume_start_frame = start_frame
					seq1_volume_final_frame = final_frame
				elif seq1_sound.type == "SCENE":
					seq1_volume_start_frame = seq1_sound.scene.frame_end - effect_length
					seq1_volume_final_frame = seq1_sound.scene.frame_end
			
			if seq2_sound is not None:
				if seq2_sound.type == "SOUND":
					seq2_volume_start_frame = start_frame
					seq2_volume_final_frame = final_frame
				elif seq2_sound.type == "SCENE":
					seq2_volume_start_frame = 1
					seq2_volume_final_frame = 1 + effect_length
				
		else:
			effect_length = (final_frame - start_frame)
			half_effect_length = int(effect_length / 2)
			medium_frame = start_frame + half_effect_length
			
			if seq1_sound is not None:
				if seq1_sound.type == "SOUND":
					seq1_volume_start_frame = start_frame
					seq1_volume_final_frame = medium_frame
				elif seq1_sound.type == "SCENE":
					seq1_volume_start_frame = seq1_sound.scene.frame_end - effect_length
					seq1_volume_final_frame = seq1_sound.scene.frame_end - half_effect_length
				
			if seq2_sound is not None:
				if seq2_sound.type == "SOUND":
					seq2_volume_start_frame = medium_frame
					seq2_volume_final_frame = final_frame
				elif seq2_sound.type == "SCENE":
					seq2_volume_start_frame = half_effect_length
					seq2_volume_final_frame = effect_length
				
		
		if seq1_sound is not None:
			cqtc_bpy.animate_volume(seq1_sound, 1, 0, seq1_volume_start_frame, seq1_volume_final_frame)
		
		if seq2_sound is not None:
			cqtc_bpy.animate_volume(seq2_sound, 0, 1, seq2_volume_start_frame, seq2_volume_final_frame)
	
	
	def __create_or_get_existing_effect_strip(self, sequence, context, effect_type, effect_name_suffix):
		sequence.blend_type = "ALPHA_OVER"
		
		is_effect_strip = (sequence.type == effect_type)
		if is_effect_strip:
			return sequence, sequence
		
		is_effect_strip_child =  False
		tmp_sequence = sequence
		while "input_1" in dir(tmp_sequence):
			tmp_sequence = tmp_sequence.input_1
			is_effect_strip_child = (tmp_sequence is not None and tmp_sequence.type == effect_type)
			if is_effect_strip_child:
				break
		
		if is_effect_strip_child:
			sequence_to_return = sequence
			sequence = tmp_sequence
			
		else:
			original_sequence = sequence
			channel = cqtc_bpy.get_available_channel_in_position(context, original_sequence.frame_final_start, original_sequence.frame_final_end, original_sequence.channel)
			sequence = context.scene.sequence_editor.sequences.new_effect(
					original_sequence.name + effect_name_suffix,
					effect_type,
					channel,
					original_sequence.frame_final_start,
					original_sequence.frame_final_end,
					original_sequence)
			
			sequence.blend_type = "ALPHA_OVER"
			
			original_sequence.select = False
			sequence_to_return = sequence
			
		return sequence, sequence_to_return
	
	
	def __get_transition_sound_sequences(self, context, seq1, seq2):
		seq1_sound = None
		seq2_sound = None
		selected_soundable_sequences = [s for s in context.selected_sequences if s.type in ["SOUND", "SCENE"] ]
		for selected_soundable_sequence in selected_soundable_sequences:
			if (selected_soundable_sequence.frame_final_start == seq1.frame_final_start \
				and selected_soundable_sequence.frame_final_end == seq1.frame_final_end):
				seq1_sound = selected_soundable_sequence
			
			if (selected_soundable_sequence.frame_final_start == seq2.frame_final_start \
				and selected_soundable_sequence.frame_final_end == seq2.frame_final_end):
				seq2_sound = selected_soundable_sequence

		return (seq1_sound, seq2_sound)
	
	
	def __set_animatable_properties(self, context, animatable_properties_info, is_in, start_frame, final_frame):
		delay_image = context.scene.super_effect.delay_image
		if is_in:
			start_frame += delay_image
			final_frame += delay_image
		
		for sequence, obj, seq_attr, super_effect_prop, options in animatable_properties_info:
			is_horizontal_mirrorable = "is_horizontal_mirrorable" in options
			is_vertical_mirrorable = "is_vertical_mirrorable" in options
			get_values_fn = options["get_values_fn"] if "get_values_fn" in options else lambda item, previous : [item.value]
			
			self.__set_animatable_property(context,
				sequence,
				obj,
				seq_attr,
				super_effect_prop,
				start_frame,
				final_frame,
				is_in,
				is_horizontal_mirrorable=is_horizontal_mirrorable,
				is_vertical_mirrorable=is_vertical_mirrorable,
				get_values_fn=get_values_fn)
	
	
	def __set_animatable_property(self,
		context,
		sequence,
		obj,
		seq_attr,
		super_effect_prop,
		start_frame,
		final_frame,
		is_in,
		is_vertical_mirrorable=False,
		is_horizontal_mirrorable=False,
		get_values_fn=lambda item, previous : [item.value]
	):
		is_property_enabled = getattr(context.scene.super_effect, "%s_enabled" % super_effect_prop)
		if not is_property_enabled:
			return
		
		super_effect = context.scene.super_effect
		is_in_frames = (super_effect.effect_length_type == "FRAMES")
		is_reversed = ((not is_in) and super_effect.reverse_out_effect)
		is_horizontal_mirrored = (is_horizontal_mirrorable and (not is_in) and super_effect.mirror_horizontal_out_effect)
		is_vertical_mirrored = (is_vertical_mirrorable and(not is_in) and super_effect.mirror_vertical_out_effect)
		is_mirrored = (is_horizontal_mirrored or is_vertical_mirrored)
				
		property_items = getattr(super_effect, "%s_items" % super_effect_prop)
		property_items_length = len(property_items)
		if is_reversed:
			property_items = list(reversed(property_items))
		
		previous_item = None
		previous_position = None
		for item_index, property_item in enumerate(property_items):
			values = get_values_fn(property_item, previous_item)
			if is_mirrored:
				values = [-value for value in values]
			
			if property_items_length < 2:
				setattr(obj, seq_attr, values[-1])
				continue
			
			if is_in_frames:
				effect_length_in_frames = super_effect.effect_length
			else:
				effect_length_in_frames = (sequence.frame_final_duration * super_effect.effect_length_percentage / 100)
			
			position_in_frames = int(effect_length_in_frames * property_item.position_in_percentage / 100)
			
			if is_in or not is_reversed:
				position = start_frame + position_in_frames
				interpolation_type = property_item.interpolation_type
			else:
				position = final_frame - position_in_frames
				interpolation_type = (property_items[item_index+1].interpolation_type if (item_index < property_items_length - 1) else None)
			
			if len(values) > 1:
				last_previous_position = previous_position
				cqtc_bpy.set_keyframe_interpolation_type(context, sequence, seq_attr, last_previous_position, "LINEAR")
					
				for value_index, value in enumerate(values[:-1]):
					if value == 0:
						extra_value_position = last_previous_position + 1
					else:
						total_length = (position - last_previous_position)
						pending_steps = ((len(values) - (value_index - 1)) // 2)
						current_step = (total_length // pending_steps) if pending_steps > 0 else total_length
						
						extra_value_position = last_previous_position + current_step
						
					setattr(obj, seq_attr, value)
					obj.keyframe_insert(seq_attr, index=-1, frame=extra_value_position)
					interpolation_type = (previous_item.interpolation_type if (value_index == (len(values) - 2)) else "LINEAR")
					cqtc_bpy.set_keyframe_interpolation_type(context, sequence, seq_attr, extra_value_position, interpolation_type)
					
					last_previous_position = extra_value_position
			
			setattr(obj, seq_attr, values[-1])
			obj.keyframe_insert(seq_attr, index=-1, frame=position)
			
			cqtc_bpy.set_keyframe_interpolation_type(context, sequence, seq_attr, position, interpolation_type)
			
			previous_item = property_item
			previous_position = position
