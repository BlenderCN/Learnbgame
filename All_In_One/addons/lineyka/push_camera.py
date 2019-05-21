

file_data = '''
# -*- coding: utf-8 -*-
import bpy
import json
import platform

input_data = %s

# this_path, save_path, group_name, actions

def push():
	scene = bpy.context.scene
	
	if platform.system() == 'Windows':
		this_path = str(input_data['this_path'], "utf-8")
		save_path = str(input_data['save_path'], "utf-8")
		group_name = input_data['group']
		actions = input_data['actions']
	else:
		this_path = input_data['this_path']
		save_path = input_data['save_path']
		group_name = input_data['group']
		actions = input_data['actions']
	
	# get list actions
	list_actions = []
	for key in actions:
		list_actions.append(actions[key])
		
	# link group
	with bpy.data.libraries.load(this_path, link=False) as (data_src, data_dst):
		data_dst.groups = [group_name]
		data_dst.actions = list_actions

	for ob in bpy.data.groups[group_name].objects:
		# link ob to scene
		scene.objects.link(ob)
		
		# append action
		if not ob.name in actions.keys():
			continue
		if not ob.animation_data:
			ob.animation_data_create()
		ob.animation_data.action = bpy.data.actions[actions[ob.name]]
		
	# text data block
	tname = 'camera_meta_data'
	text = bpy.data.texts.new(tname)
	meta_data = {}
	meta_data['group'] = input_data['group']
	meta_data['actions'] = input_data['actions']
	meta_data['start'] = input_data['start']
	meta_data['end'] = input_data['end']
	
	text.write(json.dumps(meta_data, sort_keys=True, indent=4))

	# -- save
	bpy.ops.wm.save_as_mainfile(filepath = save_path, check_existing = True)

push()

'''