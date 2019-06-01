import bpy
from bpy.app.handlers import persistent
import re

@persistent
def load_post_handler(scene):
	try:
		
		for scene in bpy.data.scenes:
			if "sequence_editor" in dir(scene) and scene.sequence_editor is not None:
				for seq in scene.sequence_editor.sequences:
					seq.cqtc_tools_is_new = False
				
	except Exception as e:
		print("Error cqtc_tools.handlers.load_post_handler:", e)

@persistent
def scene_update_post_handler(scene):
	if not scene.sequence_editor:
		return
	
	if not __package__ in bpy.context.user_preferences.addons:
		return
	
	new_sequences = [seq for seq in scene.sequence_editor.sequences if seq.cqtc_tools_is_new]
	if not len(new_sequences):
		return
	
	prefs = bpy.context.user_preferences.addons[__package__].preferences
	set_new_scenes_properties(new_sequences, prefs, scene)
	set_proxy_settings(new_sequences, prefs)
	set_blend_settings(new_sequences, prefs)
	
	for seq in new_sequences:
		seq.cqtc_tools_is_new = False


def set_new_scenes_properties(new_sequences, prefs, scene):
	scenes_in_current_frame = prefs.set_new_scenes_in_current_frame
	auto_use_sequences = prefs.auto_use_sequence_for_new_scenes
	if not scenes_in_current_frame and not auto_use_sequences:
		return
	
	new_scenes_seqs = [seq for seq in new_sequences if seq.type == "SCENE"]
	if scenes_in_current_frame:
		for scene_seq in new_scenes_seqs:
			scene_seq.frame_start = scene.frame_current
	
	if auto_use_sequences:
		scene_name_pattern = prefs.use_sequence_for_new_scenes_pattern
		new_matches_scenes = [seq for seq in new_scenes_seqs if re.match(scene_name_pattern, seq.name) ]
			
		for scene_seq in new_matches_scenes:
			scene_seq.use_sequence = True


def set_proxy_settings(new_sequences, prefs):
	auto_proxy = prefs.auto_proxy_settings_for_new_movies
	uncheck_use_overwrite_proxy = prefs.uncheck_use_overwrite_proxy
	if not auto_proxy:
		return
	
	new_proxyable_seqs = [seq for seq in new_sequences if seq.type == "MOVIE"]
	if not len(new_proxyable_seqs):
		return

	quality = prefs.proxy_quality_for_new_movies
	size = prefs.proxy_size_for_new_movies
	build_size_prop_name =  ("build_%s" % size)
	
	for sequence in new_proxyable_seqs:
		sequence.use_proxy = True
		sequence.proxy.quality = quality
		if uncheck_use_overwrite_proxy:
			sequence.proxy.use_overwrite = False
		
		if build_size_prop_name in dir(sequence.proxy):
			setattr(sequence.proxy, build_size_prop_name, True)


def set_blend_settings(new_sequences, prefs):
	auto_blend = prefs.auto_blend_for_new_sequences
	if auto_blend:
		new_blendable_seqs = [seq for seq in new_sequences if "blend_type" in dir(seq) ]
		for sequence in new_blendable_seqs:
			sequence.blend_type = prefs.blend_type_for_new_sequences
	

def register_handlers():
	bpy.types.Sequence.cqtc_tools_is_new = bpy.props.BoolProperty(default = True)
	
	remove_handlers()
	bpy.app.handlers.load_post.append(load_post_handler)
	bpy.app.handlers.scene_update_post.append(scene_update_post_handler)


def unregister_handlers():
	remove_handlers()


def remove_handlers():
	handlers = bpy.app.handlers.scene_update_post
	for handler in handlers:
		if ((" %s_scene_update_post_handler " % __package__) in str(handler)):
			handlers.remove(handler)
	
	handlers = bpy.app.handlers.load_post
	for handler in handlers:
		if ((" %s_scene_load_post_handler " % __package__) in str(handler)):
			handlers.remove(handler)
