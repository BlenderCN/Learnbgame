from operator import attrgetter
from cqtc_operator import CqtcOperator
import cqtc_path
import os.path

numbered_intro_file_template = "TF 0%i.jpg"
numbered_intro_n_file = "TF 0N.jpg"
numbered_intro_image_path = os.path.join(cqtc_path.addons_path, r"..\DIBUJOS")


class CreateNumberedIntroOperator(CqtcOperator):
	bl_idname = "numbered_intro.create"
	bl_label = "Create Numbered Intros"
	
	def execute(self, context):
		
		error = self.validate_data(context)
		if error:
			return self.return_error(error)
		
		transition_length = context.scene.numbered_intro.transition_length		
		selected_sequences = sorted([ seq for seq in context.selected_sequences if seq.type != "SOUND" ], key=attrgetter("frame_final_start"))
		
		for index, numerable_seq in enumerate(selected_sequences):
		
			channel = numerable_seq.channel
			last_frame_until_numerable_seq = -1
			for any_sequence in context.sequences:
				if (
					any_sequence.frame_final_start <= numerable_seq.frame_final_start \
					and last_frame_until_numerable_seq < any_sequence.frame_final_end <= numerable_seq.frame_final_start
				):
					last_frame_until_numerable_seq = any_sequence.frame_final_end
			
			if numerable_seq.frame_final_start == last_frame_until_numerable_seq:
				continue
			
			sequence_final_start_frame = (last_frame_until_numerable_seq + transition_length)
			adjustment = (sequence_final_start_frame - numerable_seq.frame_final_start)
			if adjustment != 0:
				move_to_right = (adjustment > 0)
				
				sequences_to_move = [ seq for seq in context.sequences if seq.frame_final_start >= numerable_seq.frame_final_start ]
				sequences_to_move = sorted(sequences_to_move, key=attrgetter("frame_final_end"), reverse=move_to_right)
				
				for sequence in sequences_to_move:
					try:
						if sequence.type in ("COLOR","IMAGE","MOVIE","SCENE","META","SOUND"):
							sequence.frame_start += adjustment	
						else:
							fcurve_data_path = "sequence_editor.sequences_all[\"%s\"]." % (sequence.name)
							fcurves = [fcurve for fcurve in context.scene.animation_data.action.fcurves if fcurve.data_path.startswith(fcurve_data_path)]
							for fcurve in fcurves:
								for keyframe_point in fcurve.keyframe_points:
									keyframe_point.co[0] += adjustment
									keyframe_point.handle_left[0] += adjustment
									keyframe_point.handle_right[0] += adjustment
							
					except AttributeError as ae:
						pass
			
			start_frame = last_frame_until_numerable_seq
			transition_end_frame = start_frame + int(transition_length/2)
			end_frame = numerable_seq.frame_final_start
			
			numbered_intro_number = context.scene.numbered_intro.next_number
			black_strip = context.scene.sequence_editor.sequences.new_effect(
				"TF Negro %i" % numbered_intro_number,
				"COLOR",
				channel,
				start_frame,
				frame_end=start_frame + 1
			)
			black_strip.color = (0,0,0)
			
			numbered_intro_full_path = self.get_numbered_intro_image_fullpath(numbered_intro_number)
			numbered_intro_strip = context.scene.sequence_editor.sequences.new_image(
				"TF Imagen %i" % numbered_intro_number,
				numbered_intro_full_path,
				channel,
				transition_end_frame
			)
			numbered_intro_strip.frame_final_end = end_frame
			
			wipe_strip = context.scene.sequence_editor.sequences.new_effect(
				"TF Transición %i" % numbered_intro_number,
				"WIPE",
				channel,
				start_frame,
				frame_end=transition_end_frame,
				seq1=black_strip,
				seq2=numbered_intro_strip
			)
				
			wipe_strip.transition_type = "CLOCK"
			wipe_strip.direction = "IN"
			
			context.scene.numbered_intro.next_number += 1
		
		return {"FINISHED"}
	
	
	def validate_data(self, context):
		selected_sequences = [ seq for seq in context.selected_sequences if seq.type != "SOUND" ]
		if len(selected_sequences) == 0:
			return "You should select at least one strip"
		
		next_number = context.scene.numbered_intro.next_number
		for numbered_intro_number in range(next_number, next_number + len(selected_sequences)):
			numbered_intro_full_path = self.get_numbered_intro_image_fullpath(numbered_intro_number)
			if not os.path.isfile(numbered_intro_full_path):
				return "%s: %s" % (self.translate("File not found"), numbered_intro_full_path)
	
	
	def get_numbered_intro_image_fullpath(self, numbered_intro_number):
		if numbered_intro_number < 10:
			numbered_intro_image = numbered_intro_file_template % numbered_intro_number
		else:
			numbered_intro_image = numbered_intro_n_file
		
		return os.path.join(numbered_intro_image_path, numbered_intro_image)
