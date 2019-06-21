

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
		action = input_data['action']
	else:
		this_path = input_data['this_path']
		save_path = input_data['save_path']
		action = input_data['action']
	
	# get list actions
	list_actions = [action]
	
	# link group
	with bpy.data.libraries.load(this_path, link=False) as (data_src, data_dst):
		data_dst.actions = list_actions
		
	for action in bpy.data.actions:
		action.use_fake_user = True

	# -- save
	bpy.ops.wm.save_as_mainfile(filepath = save_path, check_existing = True)

push()

'''