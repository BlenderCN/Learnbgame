# -*- coding: utf-8 -*-

import bpy
import json
import imp
import shutil
import os
import random
import datetime
import webbrowser
import addon_utils
import platform
import subprocess
import mathutils
import math
import struct
from struct import unpack

# my modils
from .edit_db import task
from .edit_db import log

class G(object):
	# animatic
	name_text = 'Animatic_data'
	name_scene = 'Animatic'
	shot_name = 'Shot.001'
	
	# text data block
	content_of_location = 'content_of_location'

class functional:
	def __init__(self):
		self.db_task = task()
		self.db_log = log()
		self.actions_file_name = 'actions.blend'
		self.actions_python_file_name = '.rig_export_actions.py'
		self.current_task_text = 'current_task'
		
		self.img_extensions = {
			'BMP': '.bmp',
			'IRIS': '.rgb',
			'PNG': '.png',
			'JPEG': '.jpg',
			'DPX': '.dpx',
			'CINEON' : '.cin',
			'HDR' : '.hdr',
			'TARGA': '.tga',
			'TARGA_RAW': '.tga',
			'OPEN_EXR_MULTILAYER': '.exr',
			'OPEN_EXR': '.exr',
			'TIFF': '.tif',
			'AVI_JPEG': '',
			'AVI_RAW': '',
			'H264': '',
			'FFMPEG': '',
			'THEORA': '',
			'XVID': ''
			}
			
		self.preview_img_name = self.db_task.blend_service_images['preview_img_name']
		self.bg_image_name = self.db_task.blend_service_images['bg_image_name']
		self.service_images = [self.preview_img_name, self.bg_image_name]
		
	def look(self, project_name, task_data):
		# get file_path
		result = self.db_task.get_final_file_path(project_name, task_data)
		if not result[0]:
			return(False, result[1])
			
		open_path = result[1]
		
		if not open_path:
			return(False, 'Not Saved Version!')
			
		# get tmp_file_path
		tmp_path = self.db_task.tmp_folder
		tmp_file_name = task_data['task_name'].replace(':','_', 2) + '_' + hex(random.randint(0, 1000000000)).replace('0x', '') + task_data['extension']
		tmp_file_path = os.path.join(tmp_path, tmp_file_name)
		
		# copy to tmp
		shutil.copyfile(open_path, tmp_file_path)
		
		bpy.ops.wm.open_mainfile(filepath = tmp_file_path)
		
		return(True, 'Ok')
		
	def look_activity(self, project_name, task_data, activity, action):
		# get file_path
		if action == 'publish':
			asset_data = {}
			asset_data['path'] = task_data['asset_path']
			asset_data['type'] = task_data['asset_type']
			asset_data['id'] = task_data['asset_id']
			asset_data['name'] = task_data['asset']
			
			result = self.db_task.get_publish_file_path(project_name, asset_data, activity)
			if not result[0]:
				return(False, result[1])
		elif action == 'final':
			w_task_data = {}
			w_task_data.update(task_data)
			
			w_task_data['activity'] = activity
			
			result = self.db_task.get_final_file_path(project_name, w_task_data)
			if not result[0]:
				return(False, result[1])
		
		open_path = result[1]
		
		if not open_path:
			return(False, 'Not Saved Version!')
			
		# get tmp_file_path
		tmp_path = self.db_task.tmp_folder
		tmp_file_name = task_data['task_name'].replace(':','_', 2) + '_' + hex(random.randint(0, 1000000000)).replace('0x', '') + task_data['extension']
		tmp_file_path = os.path.join(tmp_path, tmp_file_name)
		
		# copy to tmp
		shutil.copyfile(open_path, tmp_file_path)
		
		bpy.ops.wm.open_mainfile(filepath = tmp_file_path)
		
		
		# *** load Physics Cache Dir
		# -- get src_dir_path
		version_dir = os.path.dirname(open_path)
		src_cache_dir_name = 'blendcache_' + task_data['asset']
		src_dir_path = os.path.normpath(os.path.join(version_dir, src_cache_dir_name))
		
		# -- get dst_dir_path
		dst_dir_name = 'blendcache_' + tmp_file_name.replace('.blend', '')
		dst_dir_path = os.path.normpath(os.path.join(tmp_path, dst_dir_name)) 
		
		# -- copy
		if os.path.exists(src_dir_path):
			shutil.copytree(src_dir_path, dst_dir_path)
		
		return(True, 'Ok')
		
	def look_version(self, project_name, task_data, version):
		# get file_path
		result = self.db_task.get_version_file_path(project_name, task_data, version)
		if not result[0]:
			return(False, result[1])
			
		open_path = result[1]
		
		if not open_path:
			return(False, 'Not Saved Version!')
			
		# get tmp_file_path
		tmp_path = self.db_task.tmp_folder
		tmp_file_name = task_data['task_name'].replace(':','_', 2) + '_' + hex(random.randint(0, 1000000000)).replace('0x', '') + task_data['extension']
		tmp_file_path = os.path.join(tmp_path, tmp_file_name)
		
		# copy to tmp
		shutil.copyfile(open_path, tmp_file_path)
		
		bpy.ops.wm.open_mainfile(filepath = tmp_file_path)
		
		return(True, open_path)
		
	def clear_deleted(self, context):
		for ob in bpy.data.objects:
			if ob.name.split('.')[0] == 'deleted':
				for scene in bpy.data.scenes:
					if ob.name in scene.objects.keys():
						scene.objects.unlink(ob)
				bpy.data.objects.remove(ob, do_unlink=True)
	
	def open_change_status(self,project, current_task, task_dict): # task_dict = dict{task_name:{'task': task_data, 'input': input_task_data}, ... }
		change_statuses = [(current_task, 'work'),]
		
		for task_name in task_dict:
			if task_dict[task_name]['task']['status'] == 'work':
				change_statuses.append((task_dict[task_name]['task'], 'pause',))
		
		result = self.db_task.change_work_statuses(project, change_statuses)
		if not result[0]:
			return(False, result[1])
			
		return(True, result[1]) # result[1] - dict {task_name : new_status, ...}
	
	def open_make_text_datablock(self): # not used
		pass
	
	def open_file(self, project_name, task_data):
		result = self.db_task.get_final_file_path(project_name, task_data)
		if not result[0]:
			return(False, result[1])
		
		open_path = result[1]
		
		if not open_path:
			return(False, 'Not Saved Version!')
		
		# get tmp_file_path
		tmp_path = self.db_task.tmp_folder
		tmp_file_name = task_data['task_name'].replace(':','_', 2) + '_' + hex(random.randint(0, 1000000000)).replace('0x', '') + task_data['extension']
		tmp_file_path = os.path.join(tmp_path, tmp_file_name)
		
		# copy to tmp
		shutil.copyfile(open_path, tmp_file_path)
		
		bpy.ops.wm.open_mainfile(filepath = tmp_file_path)
		
		return(True, open_path)
	
	def open_source_file(self, project_name, task_data, open_task_data):
		# test extension
		if task_data['extension'] != open_task_data['extension']:
			return(False, 'Invalid Extension!')
		
		# get path
		result = self.db_task.get_final_file_path(project_name, open_task_data)
		if not result[0]:
			return(False, result[1])
		
		open_path = result[1]
		
		if not open_path:
			return(False, 'Not Saved Version!')
		
		# get tmp_file_path
		tmp_path = self.db_task.tmp_folder
		tmp_file_name = task_data['task_name'].replace(':','_', 2) + '_' + hex(random.randint(0, 1000000000)).replace('0x', '') + task_data['extension']
		tmp_file_path = os.path.join(tmp_path, tmp_file_name)
		
		# copy to tmp
		shutil.copyfile(open_path, tmp_file_path)
		
		bpy.ops.wm.open_mainfile(filepath = tmp_file_path)
		return(True, 'ok!')
	
	def load_source_file(self, context, project_name, task_data, open_task_data):
		# test extension
		if task_data['extension'] != open_task_data['extension']:
			return(False, 'Invalid Extension!')
		
		# get path
		result = self.db_task.get_final_file_path(project_name, open_task_data)
		if not result[0]:
			return(False, result[1])
		
		open_path = result[1]
		
		if not open_path:
			return(False, 'Not Saved Version!')
		
		# LOAD
		if open_task_data['asset_type'] == 'obj':
			mesh = None
			with bpy.data.libraries.load(open_path, link=False) as (data_src, data_dst):
				for name in data_src.meshes:
					if name == open_task_data['asset']:
						data_dst.meshes.append(name)
						mesh = name
						break
				
			if mesh:
				ob = bpy.data.objects.new(open_task_data['asset'], bpy.data.meshes[mesh])
				context.scene.objects.link(ob)
			else:
				return(False, 'Not Found Source Mesh!')
				
		elif open_task_data['asset_type'] == 'char':
			group_list = []
			
			with bpy.data.libraries.load(open_path, link=False) as (data_src, data_dst):
				for name in data_src.groups:
					if open_task_data['asset'] in name:
						group_list.append(name)
						
				data_dst.groups = group_list
			
			if group_list:
				for grp in group_list:
					#grp = bpy.data.groups[group]
					for ob in grp.objects:
						if not ob.name in context.scene.objects.keys():
							context.scene.objects.link(ob)
							
			else:
				return(False, 'Not Found Source Groups!')
		
		return(True, 'ok!')
	
	def open_version(self):  # not used  -- > look_version
		pass
	
	def open_from_input(self):
		pass
	
	def open_current_file(self, project_name, task_data):
		# get current path
		current_path = os.path.normpath(bpy.data.filepath)
		
		# make random name
		if not bpy.data.filepath:
			tmp_path = os.path.normpath(self.db_task.tmp_folder)
			
			print(os.path.dirname(current_path))
			print(tmp_path)
			
			if os.path.dirname(current_path) != tmp_path:
				# get tmp_file_path
				tmp_file_name = task_data['task_name'].replace(':','_', 2) + '_' + hex(random.randint(0, 1000000000)).replace('0x', '') + task_data['extension']
				tmp_file_path = os.path.join(tmp_path, tmp_file_name)
				# save_as to tmp
				bpy.ops.wm.save_as_mainfile(filepath = tmp_file_path, check_existing = True)
			else:
				#return(False, 'Yes')
				pass
		
		return(True, 'Ok')
	
	def open_from_input_version(self): # not used
		pass
	
	def push(self, project, task_data, comment, current_content_data):
		# ****** SAVE TO TMP
		# get file path
		tmp_path = self.db_task.tmp_folder
		path = bpy.data.filepath
		
		# -- get tmp path
		save_tmp_path = None
		if task_data['task_type'] not in ['location', 'animation_shot', 'tech_anim', 'simulation_din', 'render', 'composition']:
			if os.path.normpath(os.path.dirname(path)) != os.path.normpath(tmp_path):
				# resave
				# -- new path
				save_name = task_data['task_name'].replace(':','_', 2) + '_' + hex(random.randint(0, 1000000000)).replace('0x', '') + task_data['extension']
				save_tmp_path = os.path.join(tmp_path, save_name)
			else:
				save_tmp_path = path
		else:
			save_tmp_path = path
				
		# -- save to tmp
		bpy.ops.wm.save_as_mainfile(filepath = save_tmp_path, check_existing = True)
		
		### ****** PRE PUSH ****** by ASSET_TYPE ******
		if task_data['asset_type'] in ['obj', 'char']:
			bpy.ops.file.make_paths_absolute()
			
			if task_data['activity'] == 'model':
				for ob in bpy.data.objects:
					#print(ob.name)
					new_name = ob.name.replace('.','_')
					ob.name = new_name
			
		# -- save to tmp 
		bpy.ops.wm.save_as_mainfile(filepath = save_tmp_path, check_existing = True)
		
		# ****** COPY to ACtTIVITY
		result = self.db_task.get_new_file_path(project, task_data)
		if not result[0]:
			return(False, result[1])
		new_dir_path, new_file_path = result[1]
		
		# -- make version folder
		if not os.path.exists(new_dir_path):
			os.mkdir(new_dir_path)
		
		# -- copy file
		shutil.copyfile(save_tmp_path, new_file_path)
		
		# ****** LOG
		logs_keys = {
		'activity': task_data['activity'],
		'task_name': task_data['task_name'],
		'action': 'push',
		'comment': comment,
		'version': os.path.basename(new_dir_path),
		'artist': task_data['artist']
		}
		
		result = self.db_log.notes_log(project, logs_keys, task_data['asset_id'])
		if not result[0]:
			return(False, result[1])
		
		print('3'*20)
			
		### ****** POST PUSH ****** by ASSET_TYPE ******
		if task_data['asset_type'] == 'location':
			json_path = os.path.join(task_data['asset_path'], self.db_task.additional_folders['meta_data'], self.db_task.location_position_file)
			
			if not os.path.exists(json_path):
				with open(json_path, 'w') as f:
					jsn = json.dump({}, f)
			'''				
			with open(json_path, 'r') as read:
				save_dict = json.load(read)
			'''
			save_dict = {}
							
			# get lists (all_objects, meshes)
			all_objects_list = bpy.data.objects.keys()
			content_asset_list = {}
			for task_name in current_content_data:
				content_asset_list[current_content_data[task_name][1]['asset']] = current_content_data[task_name][1]['asset_type']
				
			for obj_name in all_objects_list:
				asset_name = obj_name.split('.')[0]
				if asset_name in content_asset_list:
					obj = bpy.data.objects[obj_name]
					if obj.dupli_group:
						save_dict[obj_name] = (obj.location[:], obj.rotation_euler[:], obj.scale[:], obj.dupli_group.name, content_asset_list[asset_name])
					else:
						save_dict[obj_name] = (obj.location[:], obj.rotation_euler[:], obj.scale[:], obj.dupli_group, content_asset_list[asset_name])
			'''
			# old
			for task_name in current_content_data:
				obj_name = current_content_data[task_name][0]['name']
				if obj_name in bpy.data.objects.keys():
					obj = bpy.data.objects[obj_name]
					save_dict[obj_name] = (obj.location[:], obj.rotation_euler[:], obj.scale[:])
				else:
					continue
			'''	
			# save data
			with open(json_path, 'w') as f:
				jsn = json.dump(save_dict, f, sort_keys=True, indent=4)
				
		elif task_data['asset_type'] in ['shot_animation', 'film']:
			if task_data['task_type'] == 'animation_shot':
				json_path = os.path.join(task_data['asset_path'], self.db_task.additional_folders['meta_data'], self.db_task.location_position_file)
				
				if not os.path.exists(json_path):
					with open(json_path, 'w') as f:
						jsn = json.dump({}, f)
						
				print(current_content_data)
				#return(False, 'Ok!')
						
				# content list
				content_asset_list = {}
				if current_content_data:
					for key in current_content_data:
						if current_content_data[key][0]['type'] != 'location':
							content_asset_list[current_content_data[key][0]['name']] = current_content_data[key][0]['type']
				
				# -- content list from text data block
				if G.content_of_location in bpy.data.texts:
					text = bpy.data.texts[G.content_of_location].as_string()
					if text:
						content_data = json.loads(text)
						for key in content_data:
							if content_data[key][0]['type'] != 'location':
								content_asset_list[content_data[key][0]['name']] = content_data[key][0]['type']
				
				# get position
				save_dict = {}
				for obj_name in bpy.data.objects.keys():
					asset_name = obj_name.split('.')[0]
					if asset_name in content_asset_list:
						obj = bpy.data.objects[obj_name]
						if obj.dupli_group:
							save_dict[obj_name] = (obj.location[:], obj.rotation_euler[:], obj.scale[:], obj.dupli_group.name, content_asset_list[asset_name])
						else:
							save_dict[obj_name] = (obj.location[:], obj.rotation_euler[:], obj.scale[:], obj.dupli_group, content_asset_list[asset_name])
							
				# save data
				with open(json_path, 'w') as f:
					jsn = json.dump(save_dict, f, sort_keys=True, indent=4)
			
			
			elif task_data['task_type'] in ['animatic', 'film']:
				# get comments
				try:
					text = bpy.data.texts[G.name_text]
				except:
					return(False, 'No text data block!')
				try:
					data = json.loads(text.as_string())
				except:
					return(False, 'No dictonary!')
					
				if 'shot_data' in data.keys():
					shot_data = data['shot_data']
					
					for name in shot_data:
						if not 'id' in shot_data[name].keys():
							continue
						if 'comment' in shot_data[name].keys():
							comment = shot_data[name]['comment']
						else:
							comment = ''
							
						keys = {
						'id': shot_data[name]['id'],
						'type': shot_data[name]['type'],
						'comment': comment
						}
						#
						result = self.db_log.edit_asset_data_by_id( project, keys)
						if not result[0]:
							print(name,'save comment:', result[1])
							
			elif task_data['task_type'] in ['simulation_din', 'render']:
				# this_file_name
				this_path = bpy.context.blend_data.filepath
				this_file_name = os.path.basename(this_path)
				tmp_path = os.path.dirname(this_path)
				
				# get src_physics_dir
				physics_dir_name = 'blendcache_' + this_file_name.replace('.blend', '')
				src_physics_dir = os.path.normpath(os.path.join(tmp_path, physics_dir_name))
				
				# get dst_physics_dir
				dst_physics_dir = os.path.normpath(os.path.join(new_dir_path, ('blendcache_' + task_data['asset'])))
				
				# copy dir
				if os.path.exists(src_physics_dir):
					print('**** Copy Physics!!!')
					shutil.copytree(src_physics_dir, dst_physics_dir)
				else:
					return(False, ('No Copy Physics! No found cache files!!!'))
			
						
		return(True, new_file_path)
		
	def get_push_logs(self, project_name, task_data):
		# get all logs
		result = self.db_log.read_log(project_name, task_data['asset_id'], task_data['activity'])
		if not result[0]:
			return(False, result[1])
		
		push_logs = []
		for row in result[1]:
			if row['action'] == 'push':
				row = dict(row)
				dt = row['date_time']
				data = str(dt.year) + '/' + str(dt.month) + '/' + str(dt.day) + '/' + str(dt.hour) + ':' + str(dt.minute)
				row['date_time'] = data
				push_logs.append(row)
				
		return(True, push_logs)

	def get_sketch_file_path(self, project_name, task_data):
		img_path = None
		
		# get final file path
		result = self.db_task.get_final_file_path(project_name, task_data)
		if not result[0]:
			return(False, result[1])
			
		self.final_file_path = result[1]
		self.asset_path = result[2]
		
		# -- get publish folder path
		activity_dir_name = self.db_task.activity_folder[task_data['asset_type']]['sketch']
		
		publish_dir = os.path.normpath(os.path.join(self.asset_path, self.db_task.publish_folder_name))
		if not os.path.exists(publish_dir):
			return(False, 'in func.get_sketch_file_path - Not Publish Folder!')
		
		publish_activity_dir = os.path.normpath(os.path.join(publish_dir, activity_dir_name))
		if not os.path.exists(publish_activity_dir):
			return(False, 'in func.get_sketch_file_path - Not Publish Activity Folder!')
			
		print(publish_activity_dir)
		
		# -- tiff file path
		#img_file_name = os.path.basename(self.final_file_path).replace(task_data['extension'], '.png')
		png_img_file_name = task_data['asset'] + '.png'
		tiff_img_file_name = task_data['asset'] + '.tiff'
		
		png_img_path = os.path.normpath(os.path.join(publish_activity_dir, png_img_file_name))
		tiff_img_path = os.path.normpath(os.path.join(publish_activity_dir, tiff_img_file_name))
		
		img_path = None
		if os.path.exists(png_img_path):
			img_path = png_img_path
		elif os.path.exists(tiff_img_path):
			img_path = tiff_img_path
		else:
			return(False, 'in func.get_sketch_file_path - Not Found Img Path!')
		
		'''
		if not os.path.exists(img_path):
			return(False, 'in func.get_sketch_file_path - Not Found Img Path!')
		'''
		return(True, img_path)
		
	def look_sketch(self, project_name, task_data):
		# get publish dir
		pablish_dir = os.path.join(task_data['asset_path'], self.db_task.publish_folder_name)
		if not os.path.exists(pablish_dir):
			return(False, ('Publish Not Found!: ' + pablish_dir))
			
		# get activity dir
		activity_dir = os.path.join(pablish_dir, self.db_task.activity_folder[task_data['asset_type']]['sketch'])
		if not os.path.exists(activity_dir):
			return(False, ('Publish/Activity Not Found!: ' + activity_dir))
			
		# get file_path
		file_path = os.path.join(activity_dir, (task_data['asset'] + '.png'))
		if not os.path.exists(file_path):
			return(False, ('Sketch File Not Found!: ' + file_path))
			
		webbrowser.open(file_path)
		
		return(True, 'Ok!')
		
	### ********* MODEL PANEL ******************************
	def model_rename_by_asset(self, context, current_task):
		this_ob = bpy.context.object
		this_mesh = this_ob.data
		
		ls = bpy.data.meshes
		for mesh in ls:
			if mesh.name == current_task['asset']:
				mesh.name = 'old_' + current_task['asset']
				break
		ls = bpy.data.objects
		for ob in ls:
			if ob.name == current_task['asset']:
				ob.name = 'old_' + current_task['asset']
				break
		
		this_mesh.name = current_task['asset']
		this_ob.name = current_task['asset']
		
		return(True, 'Ok')
	
	### ********* CHAT ******************************
	def chat_run(self, current_project, current_user, current_task):
		home_dir = os.path.expanduser('~')
		json_path = os.path.normpath(os.path.join(home_dir, '.blend_chat.json'))
		
		data = {'current_project':current_project, 'current_user':current_user, 'current_task':current_task}
		with open(json_path, 'w') as f:
			jsn = json.dump(data, f, sort_keys=True, indent=4)
			
		# run chat
		file_dir = None
		for modul in addon_utils.modules():
			#print(modul.__name__)
			if modul.__name__ in ['lineyka_b3d' , 'lineyka-b3d', 'lineyka-b3d-master']:
				file_dir = os.path.dirname(modul.__file__)
				break
		
		file_path = os.path.normpath(os.path.join(file_dir, 'lineyka_chat_run.py'))
		
		if platform.system() == 'Linux':
			cmd = 'chmod +x \"' + file_path + '\"'
			os.system(cmd)
		
		#cmd = 'python \"' + file_path + '\"'
		#cmd = 'start python \"%s\"' % file_path
		#os.system(cmd)
		cmd = 'python \"%s\"' % file_path
		subprocess.Popen(cmd, shell = True)
			
		return(True, 'Ok!')
		
		
	### ********* CONTENT LOCATIONS ************************
	def get_content_data(self, project_name, task_tupl, all_assets_data_by_name = False):
		if not task_tupl['input']:
			return(True, None)
		
		# *** GET INPUT_TASK_LIST
		if task_tupl['input']['task_type'] == 'service':
			if task_tupl['input']['input']:
				input_task_list = json.loads(task_tupl['input']['input'])
			else:
				return(True, None)
		
		else:
			result = self.db_task.get_list(project_name, task_tupl['task']['asset_id'])
			if not result[0]:
				return(False, result[1])
			all_tasks_list = result[1]
			all_task_data = {}
			for data in all_tasks_list:
				all_task_data[data['task_name']] = data
		
			# get input task
			input_task = task_tupl['input']
			while input_task['task_type'] != 'service':
				if not input_task['input']:
					#break
					return(True, None)
				input_task = all_task_data[input_task['input']]
			
			input_task_list = json.loads(input_task['input'])
			
		# *** GET CURRENT CONTENT DATA
		return_data = {}
		
		# get asset data
		if not all_assets_data_by_name:
			result = self.db_task.get_name_data_dict_by_all_types(project_name)
			if result[0]:
				all_assets_data_by_name = result[1]
		
		# get content data
		if all_assets_data_by_name:
			for task_name in input_task_list:
				asset_name = task_name.split(':')[0]
				if asset_name == task_tupl['task']['asset']:
					continue
				asset_data = dict(all_assets_data_by_name[asset_name])
				task_data = None
				res = self.db_task.get_list(project_name, asset_data['id'])
				if res[0]:
					for row in res[1]:
						if row['task_name'] == task_name:
							task_data = dict(row)
							break
				else:
					#print(res[1])
					continue
				return_data[task_name] = (asset_data, task_data)
					
		# get task_data  self.db_task.get_list(project_name, asset_id)
		
		return(True, return_data)
	
	
	def location_get_content_data(self, project_name, task_list):
		asset_list = []
		for task_name in task_list:
			asset_list.append(task_name.split(':')[0])
		
		# get asset data
		return_data = {}
		result = self.db_task.get_name_data_dict_by_all_types(project_name)
		if result[0]:
			for key in task_list:
				asset_data = dict(result[1][key.split(':')[0]])
				task_data = None
				res = self.db_task.get_list(project_name, asset_data['id'])
				if res[0]:
					for row in res[1]:
						if row['task_name'] == key:
							task_data = dict(row)
							break
				else:
					#print(res[1])
					continue
				return_data[key] = (asset_data, task_data)
					
		# get task_data  self.db_task.get_list(project_name, asset_id)
		
		return(return_data)
		
	def get_content_list(self, project_name, task_tupl):
		# get all task list by asset
		result = self.db_task.get_list(project_name, task_tupl['task']['asset_id'])
		if not result[0]:
			print(result[1])
			return(None)
		all_tasks_list = result[1]
		all_task_data = {}
		for data in all_tasks_list:
			all_task_data[data['task_name']] = data
		
		# get input task
		input_task = task_tupl['input']
		
		while input_task['task_type'] != 'service':
			if not input_task['input']:
				#break
				return(None)
				
			input_task = all_task_data[input_task['input']]
			
		input_task_list = json.loads(input_task['input'])
			
		#print('*'*250, input_task['task_name'], input_task['task_type'])
		
		
		return(input_task_list)
		
	def location_load_exists(self, context, project_name, data, c_task_data):
		# -- get position data
		json_path = os.path.join(c_task_data['asset_path'], self.db_task.additional_folders['meta_data'], self.db_task.location_position_file)
		data_dict = None
		if os.path.exists(json_path):
			with open(json_path, 'r') as read:
				data_dict = json.load(read)
		else:
			return(False, ('Not Found ' + self.db_task.location_position_file))
		
		''' old
		for key in data:
			if not data[key][0]['name'] in data_dict.keys():
				continue
			result = self.location_load_obj_type(context, project_name, data[key], c_task_data)
			if not result[0]:
				print('WARNING', result[1])
		'''
		
		# get content list
		all_objects_list = bpy.data.objects.keys()
		content_list = {}
		for key in data:
			content_list[data[key][0]['name']] = data[key]
			
		for key in data_dict:
			asset_name = key.split('.')[0]
			if asset_name in content_list:
				task_data = content_list[asset_name][1]
				# --------- LOAD OBJ ---------
				if task_data['asset_type'] == 'obj':
					# -- test mesh exists
					if not asset_name in bpy.data.meshes.keys():
						# -- make link mesh
						# -- -- get publish dir
						publish_dir = os.path.join(task_data['asset_path'], self.db_task.publish_folder_name)
						if not os.path.exists(publish_dir):
							return(False, 'in func.location_load_exists - Not Publish Folder!')
						# -- -- get activity_dir
						activity_dir = os.path.join(publish_dir, self.db_task.activity_folder[task_data['asset_type']][task_data['activity']])
						if not os.path.exists(activity_dir):
							return(False, 'in func.location_load_exists - Not Publish/Activity Folder!')
						# -- -- get file_path
						file_path = os.path.join(activity_dir, (asset_name + task_data['extension']))
						if not os.path.exists(file_path):
							#print(file_path)
							return(False, 'Publish/File Not Found!')
							
						#  -- -- link
						dir_ = os.path.join(file_path, 'Mesh')
						bpy.ops.wm.link(directory= dir_, filename = asset_name, link = True)
					
					mesh = bpy.data.meshes[asset_name]
					
					# -- test obj exists
					if key in all_objects_list:
						# -- -- remove obj
						for scene in bpy.data.scenes:
							try:
								scene.objects.unlink(bpy.data.objects[key])
							except:
								continue
							bpy.data.objects.remove(bpy.data.objects[key], do_unlink=True)
								
					# -- make object
					obj = bpy.data.objects.new(key, mesh)
					bpy.context.scene.objects.link(obj)
					
					# -- position object
					obj.location[:] = data_dict[key][0]
					obj.rotation_euler[:] = data_dict[key][1]
					obj.scale[:] = data_dict[key][2]
					
				# --------- LOAD CHAR ---------
				elif task_data['asset_type'] == 'char':
					if not key in all_objects_list:
						ob = bpy.data.objects.new(key, None)
					else:
						ob = bpy.data.objects[key]
					# exists group
					if not data_dict[key][3] in bpy.data.groups:
						# -- make link mesh
						# -- -- get publish dir
						publish_dir = os.path.join(task_data['asset_path'], self.db_task.publish_folder_name)
						if not os.path.exists(publish_dir):
							return(False, 'in func.location_load_exists - Not Publish Folder!')
						# -- -- get activity_dir
						activity_dir = os.path.join(publish_dir, self.db_task.activity_folder[task_data['asset_type']][task_data['activity']])
						if not os.path.exists(activity_dir):
							return(False, 'in func.location_load_exists - Not Publish/Activity Folder!')
						# -- -- get file_path
						file_path = os.path.join(activity_dir, (asset_name + task_data['extension']))
						if not os.path.exists(file_path):
							#print(file_path)
							return(False, 'Publish/File Not Found!')
								
						with bpy.data.libraries.load(file_path, link=True) as (data_src, data_dst):
							#groups_list = []
							texts_list = []
							'''
							for name in data_src.groups:
								if asset_name in name:
									groups_list.append(name)
							'''	
							for name in data_src.texts:
								if asset_name in name:
									texts_list.append(name)
										
							data_dst.groups = [data_dict[key][3]]
							data_dst.texts = texts_list
							
					group = bpy.data.groups[data_dict[key][3]]
					ob.dupli_group = group
					ob.dupli_type = 'GROUP'
					if not ob.name in context.scene.objects.keys():
						context.scene.objects.link(ob)
							
					# -- position object
					ob.location[:] = data_dict[key][0]
					ob.rotation_euler[:] = data_dict[key][1]
					ob.scale[:] = data_dict[key][2]
					
		return(True, 'Ok!')
		
	### ********* LOAD CONTENT --------------------------------------------------
	'''	
	def location_load_content(self, context, project_name, c_data, task_data):
		result = None
		if c_data[0]['type'] == 'obj':
			result = self.location_load_obj_type(context, project_name, c_data, task_data)
		elif c_data[0]['type'] == 'char':
			result = self.location_load_char_type(context, project_name, c_data)
		return(result)
		
	def location_load_obj_type(self, context, project_name, c_data, task_data):
		# get publish dir
		pablish_dir = os.path.join(c_data[0]['path'], self.db_task.publish_folder_name)
		if not os.path.exists(pablish_dir):
			print(pablish_dir)
			return(False, 'Publish Not Found!')
			
		# get activity dir
		activity_dir = os.path.join(pablish_dir, self.db_task.activity_folder[c_data[0]['type']][c_data[1]['activity']])
		if not os.path.exists(activity_dir):
			print(activity_dir)
			return(False, 'Publish/Activity Not Found!')
			
		# get file_path
		file_path = os.path.join(activity_dir, (c_data[0]['name'] + c_data[1]['extension']))
		if not os.path.exists(file_path):
			print(file_path)
			return(False, 'Publish/File Not Found!')
			
		# LINK OBJECT
		dir_ = os.path.join(file_path, 'Mesh')
		obj_name = c_data[0]['name']
		
		#bpy.ops.wm.link(directory= dir_, filename=obj_name, link = True)
		
		# -- make object
		# -- -- remove exists object
		if obj_name in bpy.data.objects.keys():
			for scene in bpy.data.scenes:
				try:
					scene.objects.unlink(bpy.data.objects[obj_name])
				except:
					continue
			bpy.data.objects.remove(bpy.data.objects[obj_name])
			
		# -- -- rename exists mesh
		if obj_name in bpy.data.meshes.keys():
			new_name = 'removed_' + obj_name
			i = 0
			while new_name in bpy.data.meshes.keys():
				new_name = new_name.split('.')[0] + str(i)
				i+=1
				
			bpy.data.meshes[obj_name].name = new_name
		
		# -- -- LINK
		bpy.ops.wm.link(directory= dir_, filename=obj_name, link = True)
			
		# -- -- make object
		if not obj_name in bpy.data.meshes.keys():
			return(False, 'Mesh Not Found!')
		me = bpy.data.meshes[obj_name]
		obj = bpy.data.objects.new(obj_name, me)
		bpy.context.scene.objects.link(obj)
		
		# POSITION OBJECT
		# -- get position data
		json_path = os.path.join(task_data['asset_path'], self.db_task.additional_folders['meta_data'], self.db_task.location_position_file)
			
		if os.path.exists(json_path):
			with open(json_path, 'r') as read:
				data_dict = json.load(read)
				if obj_name in data_dict.keys():
					obj.location[:] = data_dict[obj_name][0]
					obj.rotation_euler[:] = data_dict[obj_name][1]
					obj.scale[:] = data_dict[obj_name][2]
		else:
			print('Not Exixts json_path', '\n', json_path)
		
		return(True, 'Ok!')
	
	def location_load_char_type(self, context, project_name, c_data):
		return(False, 'procedure Load_Char in the development of')
	'''
	### ********* ADD COPY CONTENT --------------------------------------------------
	
	def location_add_copy(self, context, project_name, c_data, task_data, Global, link = True):
		#
		G.link = link
		#print('Epte!!!')
		result = None
		if c_data[1]['asset_type'] == 'obj':
			result = self.location_copy_obj_type(context, project_name, c_data, task_data)
		elif c_data[1]['asset_type'] == 'char':
			group_list = self.location_get_group_list(context, project_name, c_data)
			if not group_list:
				return(False, 'No groups to download!')
			elif len(group_list) == 1:
				result = self.location_copy_char_type(context, c_data[1], group_list)
			else:
				Global.downloadable_group_panel = (c_data[1], group_list)
				return(False, 'Select a variant!')
		return(result)
		
	def location_copy_obj_type(self, context, project_name, c_data, location_task_data):
		task_data = c_data[1]
		asset_name = task_data['asset']
		if not asset_name in bpy.data.meshes.keys():
			# -- make link mesh
			# -- -- get publish dir
			publish_dir = os.path.join(task_data['asset_path'], self.db_task.publish_folder_name)
			if not os.path.exists(publish_dir):
				return(False, 'in func.location_load_exists - Not Publish Folder!')
			# -- -- get activity_dir
			activity_dir = os.path.join(publish_dir, self.db_task.activity_folder[task_data['asset_type']][task_data['activity']])
			if not os.path.exists(activity_dir):
				return(False, 'in func.location_load_exists - Not Publish/Activity Folder!')
			# -- -- get file_path
			file_path = os.path.join(activity_dir, (asset_name + task_data['extension']))
			if not os.path.exists(file_path):
				print(file_path)
				return(False, 'Publish/File Not Found!')
				
			#  -- -- link
			dir_ = os.path.join(file_path, 'Mesh')
			bpy.ops.wm.link(directory= dir_, filename = asset_name, link = G.link)
			
		# get mesh
		try:
			mesh = bpy.data.meshes[asset_name]
		except:
			return(False, 'Mesh Not Found!')
		# get objects
		all_objects_list = bpy.data.objects.keys()
		objects_list = []
		for obj_name in all_objects_list:
			if obj_name.split('.')[0] == c_data[1]['asset']:
				objects_list.append(obj_name)
		
		# -- get object name
		obj_correct_name = None
		# -- --
		if not c_data[1]['asset'] in objects_list:
			obj_correct_name = c_data[1]['asset']
		else:
			copy_name = c_data[1]['asset'] + '.001'
			while copy_name in objects_list:
				num = int(copy_name.split('.')[1])
				num +=1
				num_str = str(num)
				copy_name = c_data[1]['asset'] + '.' + '0'*(3 - len(num_str)) + num_str
				
			obj_correct_name = copy_name
			
		# -- make objects
		copy_obj = bpy.data.objects.new(obj_correct_name, mesh)
		bpy.context.scene.objects.link(copy_obj)
		
		# -- position object
		json_path = os.path.join(location_task_data['asset_path'], self.db_task.additional_folders['meta_data'], self.db_task.location_position_file)
			
		if os.path.exists(json_path):
			with open(json_path, 'r') as read:
				data_dict = json.load(read)
				if obj_correct_name in data_dict.keys():
					copy_obj.location[:] = data_dict[obj_correct_name][0]
					copy_obj.rotation_euler[:] = data_dict[obj_correct_name][1]
					copy_obj.scale[:] = data_dict[obj_correct_name][2]
		else:
			print('Not Exixts json_path', '\n', json_path)
		
		return(True, 'Ok')
		
	def location_get_group_list(self, context, project_name, c_data):
		# get groups list
		task_data = c_data[1]
		asset_name = task_data['asset']
		
		#if not asset_name in bpy.data.meshes.keys():
		
		# -- make link mesh
		# -- -- get publish dir
		publish_dir = os.path.join(task_data['asset_path'], self.db_task.publish_folder_name)
		if not os.path.exists(publish_dir):
			return(False, 'in func.location_load_exists - Not Publish Folder!')
		# -- -- get activity_dir
		try:
			activity_dir = os.path.join(publish_dir, self.db_task.activity_folder[task_data['asset_type']][task_data['activity']])
		except:
			print('#'*250)
			print('*** task_name ',task_data['task_name'])
			print('*** asset_type ',task_data['asset_type'])
			print('*** activity ',task_data['activity'])
			return(False, 'fuck! in location_get_group_list / get activity_dir')
			
		if not os.path.exists(activity_dir):
			return(False, 'in func.location_load_exists - Not Publish/Activity Folder!')
		# -- -- get file_path
		file_path = os.path.join(activity_dir, (asset_name + task_data['extension']))
		if not os.path.exists(file_path):
			print(file_path)
			return(False, 'Publish/File Not Found!')
				
		#with bpy.data.libraries.load(file_path, link=True) as (data_src, data_dst):
		with bpy.data.libraries.load(file_path, link=False) as (data_src, data_dst):
			group_list = []
			
			for name in data_src.groups:
				if asset_name in name:
					group_list.append(name)
		
		return(group_list)
	
	def location_copy_char_type(self, context, task_data, groups_list):
		# get groups list
		asset_name = task_data['asset']
		
		#if not asset_name in bpy.data.meshes.keys(): ### ?????
		
		# -- make link mesh
		# -- -- get publish dir
		publish_dir = os.path.join(task_data['asset_path'], self.db_task.publish_folder_name)
		if not os.path.exists(publish_dir):
			return(False, 'in func.location_load_exists - Not Publish Folder!')
		# -- -- get activity_dir
		activity_dir = os.path.join(publish_dir, self.db_task.activity_folder[task_data['asset_type']][task_data['activity']])
		if not os.path.exists(activity_dir):
			return(False, 'in func.location_load_exists - Not Publish/Activity Folder!')
		# -- -- get file_path
		file_path = os.path.join(activity_dir, (asset_name + task_data['extension']))
		if not os.path.exists(file_path):
			print(file_path)
			return(False, 'Publish/File Not Found!')
				
		with bpy.data.libraries.load(file_path, link = G.link) as (data_src, data_dst):
		#with bpy.data.libraries.load(file_path, link=False) as (data_src, data_dst):
			#groups_list = []
			texts_list = []
			'''
			for name in data_src.groups:
				if asset_name in name:
					groups_list.append(name)
			'''	
			for name in data_src.texts:
				if asset_name in name:
					texts_list.append(name)
						
			data_dst.groups = groups_list
			data_dst.texts = texts_list
			
		scene = context.scene
		for group in data_dst.groups:
			if G.link:
				ob = bpy.data.objects.new(group.name, None)
				ob.dupli_group = group
				ob.dupli_type = 'GROUP'
				scene.objects.link(ob)
			else:
				ob = bpy.data.objects.new(group.name, None)
				scene.objects.link(ob)
				for obj in group.objects:
					obj.parent = ob
					scene.objects.link(obj)
		
		
		return(True, 'ok!')
	
	### ********* REMOVE CONTENT --------------------------------------------------
	
	def location_clear_content(self, context, project_name, c_data):
		result = None
		if c_data[0]['type'] == 'obj':
			result = self.location_clear_obj_type(context, project_name, c_data)
		elif c_data[0]['type'] == 'char':
			result = self.location_clear_char_type(context, project_name, c_data)
		return(result)
		
	def location_clear_obj_type(self, context, project_name, c_data):
		#return(False, 'Remove_Obj')
		
		asset_name = c_data[0]['name']
		
		for ob in bpy.data.objects:
			if ob.name.split('.')[0] == asset_name:
				for scene in bpy.data.scenes:
					try:
						scene.objects.unlink(bpy.data.objects[ob.name])
					except:
						continue
				bpy.data.objects.remove(bpy.data.objects[ob.name], do_unlink=True)
				
				
		for mesh in bpy.data.meshes:
			if mesh.name.split('.')[0] == asset_name:
				# rename mesh
				new_name = 'removed_' + mesh.name
				'''
				i = 0
				while new_name in bpy.data.meshes.keys():
					new_name = new_name.split('.')[0] + str(i)
					i+=1
				'''
				mesh.name = new_name
		
		return(True, 'Ok!')
		
	def location_clear_char_type(self, context, project_name, c_data):
		asset_name = c_data[0]['name']
		
		for ob in bpy.data.objects:
			proxy_name = (ob.name + '_proxy')
			if proxy_name in bpy.data.objects.keys():
				proxy = bpy.data.objects[proxy_name]
			else:
				proxy = None
			if asset_name == ob.name.split('.')[0]:
				for scene in bpy.data.scenes:
					# object
					if ob.name in scene.objects.keys():
						scene.objects.unlink(ob)
					# proxy
					if proxy and proxy_name in scene.objects.keys():
						scene.objects.active = proxy
						bpy.ops.object.mode_set(mode = 'OBJECT')
						scene.objects.unlink(proxy)
				
				bpy.data.objects.remove(ob, do_unlink=True)
				if proxy:
					bpy.data.objects.remove(proxy, do_unlink=True)
					
		for grp in bpy.data.groups:
			#name = grp.name
			if asset_name == grp.name.split('.')[0]:
				bpy.data.groups.remove(grp, do_unlink=True)
			
		return(True, 'Ok!')
		
	### ********* ANIMATIC ------------------------------------------------------------
	
	def make_this_animatic(self, context):
		# exists Animatic scene
		scene_exists = False
		scenes = bpy.data.scenes.keys()
		if G.name_scene in scenes:
			scene_exists = True
		
		# add text data_block
		texts = bpy.data.texts.keys()
		data = {}
		
		if not G.name_text in texts:
			# -- add text data block
			text = bpy.data.texts.new(G.name_text)
			data['animatic_scene'] = G.name_scene
			text.write(json.dumps(data, sort_keys=True, indent=4))
			
		else:
			text = bpy.data.texts[G.name_text]
			try:
				data = json.loads(text.as_string())
			except:
				data = {}
			if not data:
				data = {}
			data['animatic_scene'] = G.name_scene
			text.clear()
			text.write(json.dumps(data, sort_keys=True, indent=4))
		
		# rename scene
		if not scene_exists:
			bpy.context.scene.name = G.name_scene
		else:
			return(False, (G.name_scene + '  already exists!'))
			
		return(True, 'epte!')
		
	def add_shot(self, context, shot_name, time):
		frame = context.scene.frame_current
		scene = context.scene
		# add marker
		#marker = context.scene.timeline_markers.new(shot_name, frame = context.scene.frame_current)
		
		# ********** SCENE
		# -- scene
		new_scene = bpy.data.scenes.new(shot_name)
		# -- frame start - end
		new_scene.frame_start = 1
		new_scene.frame_end = time
		
		# -- grease pencil
		pen = bpy.data.grease_pencil.new(shot_name)
		if "draw_mode" in pen:
			pen.draw_mode = 'VIEW'
		else:
			new_scene.tool_settings.gpencil_stroke_placement_view3d = 'VIEW'
		pen.layers.new('GP_Layer')
		pen.layers.active_index = 0
		new_scene.grease_pencil = pen
		new_scene.tool_settings.grease_pencil_source = 'SCENE'
		
		# -- camera
		if not shot_name in bpy.data.cameras.keys():
			cam = bpy.data.cameras.new(shot_name)
		else:
			cam = bpy.data.cameras[shot_name]
		ob_cam = bpy.data.objects.new(shot_name, cam)
		new_scene.objects.link(ob_cam)
		# -- -- edit cam
		ob_cam.rotation_euler[0] = 1.570796
		ob_cam.location[1] = -6
		ob_cam.location[2] = 1.7
		ob_cam.data.type = 'ORTHO'
		# -- -- edit scene
		new_scene.camera = ob_cam
			
		# -- bg
		bg_name = shot_name + '.bg'
		bg = bpy.data.meshes.new(bg_name)
		ob_bg = bpy.data.objects.new(bg_name, bg)
		new_scene.objects.link(ob_bg)
		verts = ((-3, 0, 3.4), (3, 0, 3.4), (3, 0, 0), (-3, 0, 0))
		edges = ((0,1), (1,2), (2,3), (3,0))
		faces = ((0,1,2,3),)
		bg.from_pydata(verts, edges, faces)
		# -- -- bg material
		mat_name = 'Material.BG'
		if not mat_name in bpy.data.materials.keys():
			mat = bpy.data.materials.new(mat_name)
			mat.diffuse_color = (1,1,1)
			mat.diffuse_intensity = 1.0
			mat.specular_intensity = 0.0
			mat.diffuse_shader = 'LAMBERT'
		else:
			mat = bpy.data.materials[mat_name]
		bg.materials.append(mat)
		
		# **************** scene to secuence_editor
		channel = 0
		try:
			for seq in scene.sequence_editor.sequences:
				if seq.channel > channel:
					channel = seq.channel
			channel = channel +1
		except:
			channel = 1
		'''	
		try:
			sequence = scene.sequence_editor.sequences.new_scene(shot_name, new_scene, channel, frame)
		except:
			bpy.ops.sequencer.scene_strip_add(frame_start=frame, channel=channel, replace_sel=True, overlap=False, scene=shot_name)
		'''
		if not scene.sequence_editor:
			scene.sequence_editor_create()
		sequence = scene.sequence_editor.sequences.new_scene(shot_name, new_scene, channel, frame)
		
		return(True, 'Ok!')
		
	def create_assets(self, context, action, set_of_tasks, group, project_name, series):
		good_types = ['SCENE', 'IMAGE', 'MOVIE', 'MOVIECLIP']
		
		# get comments
		try:
			text = bpy.data.texts[G.name_text]
		except:
			return(False, 'No text data block!')
		try:
			data = json.loads(text.as_string())
		except:
			return(False, 'No dictonary!')
			
		if 'shot_data' in data.keys():
			shot_data = data['shot_data']
		else:
			shot_data = {}
			
		# get selected sequences
		animatic_scene = bpy.data.scenes[G.name_scene]
		shots = {}
		
		for seq in animatic_scene.sequence_editor.sequences_all:
			if not seq.type in good_types:
				continue
			# get exists asset
			if seq.name in shot_data.keys():
				if 'id' in shot_data[seq.name].keys():
					if shot_data[seq.name]['id']:
						print('*'*5, 'asset ', seq.name, ' already exists!')
						continue
			if action == 'all':
				shots[seq.name] = seq
			elif action == 'selected':
				if seq.select:
					shots[seq.name] = seq
		
		if not shots:
			return(False, 'No selected sequences!')
		
		# get exists assets list
		'''
		result = self.db_task.get_list_by_all_types(project_name)
		if result[0]:
			for row in result[1]:
				if row['name'] in shots.keys():
					#print('asset by name: ', row['name'], ' already exists!')
					del shots[row['name']]
		'''
		
		# create assets
		asset_keys = []
		# -- create assets_keys_list
		for shot_name in shots:
			keys = {}
			keys['name'] = shot_name
			keys['group'] = group
			keys['type'] = 'shot_animation'
			keys['series'] = series
			if shot_name in shot_data.keys():
				keys['comment'] = shot_data[shot_name]['comment']
			keys['set_of_tasks'] = set_of_tasks
			asset_keys.append(keys)
		
		# -- create assets
		result = self.db_task.create(project_name, 'shot_animation', asset_keys)
		if not result[0]:
			return(False, result[1])
		
		for name in result[1].keys():
			asset_path = result[1][name]['path']
			# write shot_data
			shot_data[name] = dict(result[1][name])
			# create meta_data
			meta_data_folder = os.path.normpath(os.path.join(asset_path, self.db_task.additional_folders['meta_data']))
			if not os.path.exists(meta_data_folder):
				os.mkdir(meta_data_folder)
			meta_data_path = os.path.normpath(os.path.join(meta_data_folder, self.db_task.meta_data_file))
			# -- get meta_data
			shot_sequence = context.scene.sequence_editor.sequences_all[name]
			shot_scene = bpy.data.scenes[name]
			frame_start = shot_scene.frame_start + shot_sequence.frame_offset_start + shot_sequence.animation_offset_start
			duration = shot_sequence.frame_final_duration
			# -- write
			if os.path.exists(meta_data_path):
				with open(meta_data_path, 'r') as read:
					Data = json.load(read)
					Data['frame_start'] = frame_start
					Data['duration'] = duration
					Data['resolution_x'] = animatic_scene.render.resolution_x
					Data['resolution_y'] = animatic_scene.render.resolution_y
					read.close()
			else:
				Data = {
					'frame_start': frame_start,
					'duration': duration,
					'resolution_x': animatic_scene.render.resolution_x,
					'resolution_y': animatic_scene.render.resolution_y,
					}
			# -- -- write
			with open(meta_data_path, 'w') as f:
				jsn = json.dump(Data, f, sort_keys=True, indent=4)
				f.close()
			
			# export shot_video
			animatic_folder = os.path.normpath(os.path.join(asset_path, self.db_task.activity_folder['shot_animation']['animatic']))
			if not os.path.exists(animatic_folder):
				os.mkdir(animatic_folder)
			self.export_shot_video(context, animatic_folder, name, shot_sequence = shot_sequence)
			
		# -- write shot_data
		data['shot_data'] = shot_data
		text.clear()
		text.write(json.dumps(data, sort_keys=True, indent=4))
		
		return(True, 'ok!')
		
	def render_animatic_shots_to_asset(self, context, action, project_name, series):
		good_types = ['SCENE', 'IMAGE', 'MOVIE', 'MOVIECLIP']
		
		# get comments
		try:
			text = bpy.data.texts[G.name_text]
		except:
			return(False, 'No text data block!')
		try:
			data = json.loads(text.as_string())
		except:
			return(False, 'No dictonary!')
			
		if 'shot_data' in data.keys():
			shot_data = data['shot_data']
		else:
			shot_data = {}
			
		# get selected sequences
		animatic_scene = bpy.data.scenes[G.name_scene]
		shots = {}
		
		for seq in animatic_scene.sequence_editor.sequences_all:
			if not seq.type in good_types:
				continue
			# get exists asset
			if seq.name in shot_data.keys():
				if 'id' in shot_data[seq.name].keys():
					if not shot_data[seq.name]['id']:
						continue
				else:
					continue
			else:
				continue
				
			if action == 'all':
				shots[seq.name] = seq
			elif action == 'selected':
				if seq.select:
					shots[seq.name] = seq
		
		if not shots:
			return(False, 'No selected sequences!')
			
		for name in shots:
			asset_path = shot_data[name]['path']
			# create meta_data
			meta_data_folder = os.path.normpath(os.path.join(asset_path, self.db_task.additional_folders['meta_data']))
			if not os.path.exists(meta_data_folder):
				os.mkdir(meta_data_folder)
			meta_data_path = os.path.normpath(os.path.join(meta_data_folder, self.db_task.meta_data_file))
			# -- get meta_data
			shot_sequence = shots[name]
			shot_scene = bpy.data.scenes[name]
			frame_start = shot_scene.frame_start + shot_sequence.frame_offset_start + shot_sequence.animation_offset_start
			duration = shot_sequence.frame_final_duration
			# -- write
			if os.path.exists(meta_data_path):
				with open(meta_data_path, 'r') as read:
					Data = json.load(read)
					Data['frame_start'] = frame_start
					Data['duration'] = duration
					Data['resolution_x'] = animatic_scene.render.resolution_x
					Data['resolution_y'] = animatic_scene.render.resolution_y
					read.close()
			else:
				Data = {
					'frame_start': frame_start,
					'duration': duration,
					'resolution_x': animatic_scene.render.resolution_x,
					'resolution_y': animatic_scene.render.resolution_y,
					}
			# -- -- write
			with open(meta_data_path, 'w') as f:
				jsn = json.dump(Data, f, sort_keys=True, indent=4)
				f.close()
				
			# export shot_video
			animatic_folder = os.path.normpath(os.path.join(asset_path, self.db_task.activity_folder['shot_animation']['animatic']))
			if not os.path.exists(animatic_folder):
				os.mkdir(animatic_folder)
			self.export_shot_video(context, animatic_folder, name, shot_sequence = shot_sequence)
			
		return(False, 'Be!')
		
	def input_to_scene_shots_data(self, context, project_name):
		if G.name_scene in bpy.data.scenes.keys():
			animatic_scene = bpy.data.scenes[G.name_scene]
		else:
			return
		
		# sequences
		if not animatic_scene.sequence_editor:
			return
		sequences = animatic_scene.sequence_editor.sequences_all
		data = {}
		shot_data = {}
		# text data block
		if G.name_text in bpy.data.texts.keys():
			text = bpy.data.texts[G.name_text]
			try:
				data = json.loads(text.as_string())
			except:
				pass
		else:
			text = bpy.data.texts.new(G.name_text)
		
		result = self.db_task.get_list_by_type(project_name, 'shot_animation')
		if result[0]:
			for row in result[1]:
				if row['name'] in sequences.keys():
					shot_data[row['name']] = dict(row)
		
		data['shot_data'] = shot_data
		text.clear()
		text.write(json.dumps(data, sort_keys=True, indent=4))
		
		
	def export_animatic_video_to_asset(self, context, project, task_data):
		# get folder
		result = self.db_task.get_final_file_path(project, task_data)
		if not result[0]:
			return(False, result[1])
		folder = os.path.dirname(result[1])
		
		animatic_scene = bpy.data.scenes[G.name_scene]
		# to animatic scene
		if context.screen:
			context.screen.scene = animatic_scene
		
		self.edit_scene_data(context)
		path = os.path.normpath(os.path.join(folder, (G.name_scene + '.avi')))
		animatic_scene.render.filepath = bpy.path.abspath(path)
		# render
		bpy.ops.render.opengl(animation = True, sequencer = True)
		
		print(result, folder)
		
		
	def export_shot_video(self, context, animatic_folder, name, shot_sequence = None):
		scene = context.scene
		scene_start = scene.frame_start
		scene_end = scene.frame_end
		
		self.edit_scene_data(context)
		
		# get start / end
		start = shot_sequence.frame_start + shot_sequence.frame_offset_start
		end = start + shot_sequence.frame_final_duration - 1
		
		if end < scene_start:
			return()
		if start > scene_end:
			return()
		if end > scene_end:
			end = scene_end
		if start < scene_start:
			start = scene_start
			
		# edit scene data
		scene.frame_start = start
		scene.frame_end = end
		scene.render.filepath = os.path.normpath(os.path.join(animatic_folder, (name + '.avi')))
		
		# render
		bpy.ops.render.opengl(animation = True, sequencer = True)
		
		# return scene data
		scene.frame_start = scene_start
		scene.frame_end = scene_end
		

	def edit_scene_data(self, context):
		# edit scene data
		context.scene.render.display_mode = 'WINDOW'
		context.scene.render.image_settings.file_format = 'H264'
		context.scene.render.image_settings.color_mode = 'RGB'
		context.scene.render.ffmpeg.format = 'AVI'
		context.scene.render.ffmpeg.codec = 'H264'
		context.scene.render.ffmpeg.video_bitrate = 6000
		context.scene.render.ffmpeg.audio_codec = 'MP3'
		context.scene.render.ffmpeg.audio_bitrate = 128
		
	def animatic_import_playblast_to_select_sequence(self, context, project_name, task_data, action):
		# get shot_data
		try:
			text_data = json.loads(bpy.data.texts[G.name_text].as_string())
		except:
			return(False, ('Problem in \"' + G.name_text + '\"'))
			
		if 'shot_data' in text_data.keys():
			shot_data = text_data['shot_data']
		else:
			shot_data = {}
		
		# get selected sequence
		if not context.scene.sequence_editor:
			return(False, 'No Sequence Editor!')
			
		seq = context.scene.sequence_editor.active_strip
		if not seq:
			return(False, 'No Active Sequence!')
		
		# test exists playblast
		if not seq.name in shot_data:
			return(False, 'No Playblast!')
		else:
			if not 'path' in shot_data[seq.name]:
				return(False, 'No Playblast!')
				
		# edit task_data
		w_task_data = {}
		w_task_data['asset_type'] = 'shot_animation'
		w_task_data['activity'] = 'pleyblast_sequence'
		w_task_data['asset_id'] = shot_data[seq.name]['id']
		w_task_data['extension'] = '.avi'
		w_task_data['asset_path'] = shot_data[seq.name]['path']
		w_task_data['asset'] = shot_data[seq.name]['name']
		
		# get playblast_path
		if action == 'final':
			result = self.db_task.get_final_file_path(project_name, w_task_data)
			if not result[0]:
				return(False, result[1])
			playblast_path = result[1]
			if not playblast_path:
				return(False, 'No Playblast!')
		else:
			result = self.db_task.get_version_file_path(project_name, w_task_data, action)
			if not result[0]:
				return(False, result[1])
			playblast_path = result[1]
			if not playblast_path:
				return(False, 'No Playblast!')
			
		if seq.type == 'SCENE':
			# save data
			frame_start = seq.frame_start
			frame_offset_start = seq.frame_offset_start
			frame_final_duration = seq.frame_final_duration
			channel = seq.channel
			shot_name = seq.name
			
			seq_data = text_data['shot_data'][seq.name]['old_sequence_data'] = {}
			seq_data['type'] = seq.type
			seq_data['scene_name'] = seq.scene.name
			seq_data['frame_start'] = frame_start
			seq_data['frame_offset_start'] = frame_offset_start
			seq_data['frame_final_duration'] = frame_final_duration
			
			text = bpy.data.texts[G.name_text]
			text.clear()
			text.write((json.dumps(text_data, sort_keys=True, indent=4)))
			
			# remove sequence
			context.scene.sequence_editor.sequences.remove(seq)
			
			# make new sequence
			context.scene.sequence_editor.sequences.new_movie(shot_name, playblast_path, channel, (frame_start + frame_offset_start))
			
		elif seq.type == 'MOVIE':
			save_path = None
			if 'old_sequence_data' in text_data['shot_data'][seq.name].keys():
				pass
			else:
				# save data
				frame_start = seq.frame_start
				frame_offset_start = seq.frame_offset_start
				frame_final_duration = seq.frame_final_duration
								
				seq_data = text_data['shot_data'][seq.name]['old_sequence_data'] = {}
				seq_data['type'] = seq.type
				seq_data['filepath'] = seq.filepath
				seq_data['frame_start'] = frame_start
				seq_data['frame_offset_start'] = frame_offset_start
				seq_data['frame_final_duration'] = frame_final_duration
				
				text = bpy.data.texts[G.name_text]
				text.clear()
				text.write((json.dumps(text_data, sort_keys=True, indent=4)))
			
			seq.filepath = playblast_path
			
		else:
			# save data
			frame_start = seq.frame_start
			frame_offset_start = seq.frame_offset_start
			frame_final_duration = seq.frame_final_duration
			channel = seq.channel
			shot_name = seq.name
			
			seq_data = text_data['shot_data'][seq.name]['old_sequence_data'] = {}
			seq_data['type'] = seq.type
			
			text = bpy.data.texts[G.name_text]
			text.clear()
			text.write((json.dumps(text_data, sort_keys=True, indent=4)))
			
			# remove sequence
			context.scene.sequence_editor.sequences.remove(seq)
			
			# make new sequence
			context.scene.sequence_editor.sequences.new_movie(shot_name, playblast_path, channel, (frame_start + frame_offset_start))
		
		return(True, 'Ok!')
		
	def playblast_read_log(self, context, project_name):
		# get shot_data
		try:
			text_data = json.loads(bpy.data.texts[G.name_text].as_string())
		except:
			return(False, ('Problem in \"' + G.name_text + '\"'))
			
		if 'shot_data' in text_data.keys():
			shot_data = text_data['shot_data']
		else:
			shot_data = {}
		
		# get selected sequence
		if not context.scene.sequence_editor:
			return(False, 'No Sequence Editor!')
			
		seq = context.scene.sequence_editor.active_strip
		if not seq:
			return(False, 'No Active Sequence!')
		
		# test exists playblast
		if not seq.name in shot_data:
			return(False, 'No Playblast!')
		else:
			if not 'path' in shot_data[seq.name]:
				return(False, 'No Playblast!')
				
		task_data = {}
		task_data['asset'] = shot_data[seq.name]['name']
		task_data['asset_id'] = shot_data[seq.name]['id']
		task_data['asset_path'] = shot_data[seq.name]['path']
		task_data['asset_type'] = shot_data[seq.name]['type']
		
		result = self.db_log.playblast_read_log(project_name, task_data)
		return(result)
	
	def animatic_return(self, context, project_name, task_data):
		# get shot_data
		try:
			text_data = json.loads(bpy.data.texts[G.name_text].as_string())
		except:
			return(False, ('Problem in \"' + G.name_text + '\"'))
			
		if 'shot_data' in text_data.keys():
			shot_data = text_data['shot_data']
		else:
			shot_data = {}
		
		# get selected sequence
		if not context.scene.sequence_editor:
			return(False, 'No Sequence Editor!')
			
		seq = context.scene.sequence_editor.active_strip
		if not seq:
			return(False, 'No Active Sequence!')
		
		# tests
		if seq.type == 'SCENE':
			return(False, 'This is Animatic!')
			
		if not seq.name in shot_data.keys():
			return(False, 'This is Animatic!')
		else:
			if not 'old_sequence_data' in shot_data[seq.name].keys():
				return(False, 'This is Animatic!')
				
			else:
				old_data = shot_data[seq.name]['old_sequence_data']
				
		if not old_data['type'] in ['MOVIE','SCENE']:
			return(False, 'Can not load the Animatic!')
			
		# load animatic
		if old_data['type'] == 'SCENE':
			channel = seq.channel
			shot_name = seq.name
			if old_data['scene_name'] in bpy.data.scenes.keys():
				shot_scene = bpy.data.scenes[old_data['scene_name']]
			else:
				return(False, ('No Found Scene: \"' + old_data['scene_name'] + '\"!'))
			
			# remove sequence
			context.scene.sequence_editor.sequences.remove(seq)
			
			# new sequence
			seq = context.scene.sequence_editor.sequences.new_scene(shot_name, shot_scene, channel, old_data['frame_start'])
			seq.frame_offset_start = old_data['frame_offset_start']
			seq.frame_final_duration = old_data['frame_final_duration']
			
		elif old_data['type'] == 'MOVIE' and seq.type == 'MOVIE':
			# edit sequence
			seq.filepath = old_data['filepath']
			#seq.frame_offset_start = old_data['frame_offset_start']
			#seq.frame_final_duration = old_data['frame_final_duration']
		# 
		return(False, 'Ok!')
	
	### ********* Animation *********
	
	def reload_animatic(self, context, project_name, task_data):
		offset = self.db_task.farme_offset
		scene = context.scene
		asset_path = task_data['asset_path']
		# get meta_data path
		meta_data_folder = os.path.normpath(os.path.join(asset_path, self.db_task.additional_folders['meta_data']))
		if not os.path.exists(meta_data_folder):
			return(False, 'Not Found The meta_data folder!')
		meta_data_path = os.path.normpath(os.path.join(meta_data_folder, self.db_task.meta_data_file))
		# read meta_data
		if os.path.exists(meta_data_path):
			with open(meta_data_path, 'r') as read:
				Data = json.load(read)
				scene.frame_start = Data['frame_start'] + offset
				scene.frame_end = Data['frame_start'] + Data['duration'] - 1 + offset
				scene.render.resolution_x = Data['resolution_x']
				scene.render.resolution_y = Data['resolution_y']
				read.close()
		else:
			print('*** Not Found MetaData File!')
		
		# *** Reload Animatik ***
		if 	task_data['task_type'] in ["render", 'composition']:
			return(True, 'Ok!')
		
		# -- get animatic_path
		animatic_path = os.path.normpath(os.path.join(asset_path, self.db_task.activity_folder['film']['animatic'], (task_data['asset'] + '.avi')))
		
		if os.path.exists(animatic_path):
			if not scene.sequence_editor:
				scene.sequence_editor_create()
				
			# Clear Sequence Editor
			for seq in scene.sequence_editor.sequences_all:
				scene.sequence_editor.sequences.remove(seq)
			
			# MOVIE
			if not task_data['asset'] in scene.sequence_editor.sequences_all.keys():
				try:
					scene.sequence_editor.sequences.new_movie(task_data['asset'], animatic_path, 1, scene.frame_start)
				except:
					print('No Openned Animatic!!!')
			
			else:
				sequence = scene.sequence_editor.sequences[task_data['asset']]
				sequence.filepath = animatic_path
				sequence.frame_start = scene.frame_start
				
			# SOUND
			sound_name = (task_data['asset'] + '.sound')
			if not sound_name in scene.sequence_editor.sequences_all.keys():
				try:
					scene.sequence_editor.sequences.new_sound(sound_name, animatic_path, 2, scene.frame_start)
				except:
					print('No Openned Animatic!!!')
			
			else:
				sequence = scene.sequence_editor.sequences[sound_name]
				if 'filepath' in sequence:
					sequence.filepath = animatic_path
				else:
					sequence.sound.filepath = animatic_path
				sequence.frame_start = scene.frame_start
		
		else:
			print('*** Not Found Animatic!')
				
		return(True, 'Ok!')
		
	def reload_start_end_resolution(self, context, project_name, task_data):
		offset = self.db_task.farme_offset
		scene = context.scene
		asset_path = task_data['asset_path']
		# get meta_data path
		meta_data_folder = os.path.normpath(os.path.join(asset_path, self.db_task.additional_folders['meta_data']))
		if not os.path.exists(meta_data_folder):
			return(False, 'Not Found The meta_data folder!')
		meta_data_path = os.path.normpath(os.path.join(meta_data_folder, self.db_task.meta_data_file))
		# read meta_data
		if os.path.exists(meta_data_path):
			with open(meta_data_path, 'r') as read:
				Data = json.load(read)
				scene.frame_start = Data['frame_start'] + offset
				scene.frame_end = Data['frame_start'] + Data['duration'] - 1 + offset
				scene.render.resolution_x = Data['resolution_x']
				scene.render.resolution_y = Data['resolution_y']
				read.close()
				
		return(True, 'Ok!')
		
	def load_reload_location(self, context, project_name, current_content_data):
		# get input_task_list
		location_input_task_list = []
		location_task_data = None
		for task_name in current_content_data:
			if current_content_data[task_name][0]['type'] == 'location':
				location_task_data = current_content_data[task_name][1]
		
		if not location_task_data:
			return(False, '*Not Input Tasks!')

		# get 
		result = self.db_task.get_list(project_name, location_task_data['asset_id'])
		if not result[0]:
			return(False, result[1])
		
		for row in result[1]:
			'''
			if row['task_name'] == location_task_data['input']:
				location_input_task_list = json.loads(row['input'])
				break
			'''
			try:
				input = json.loads(row['input'])
			except Exception as e:
				print('*'*10, row['input'], e)
				continue
			if input:
				for task_name in input:
					if not task_name.split(':')[0] == row['asset'] and not task_name in location_input_task_list:
						location_input_task_list.append(task_name)
		#print('#'*10, location_input_task_list)

		if not location_input_task_list:
			return(False, '**Not Input Tasks!')
			
		# get loacation content data
		location_content_data = self.location_get_content_data(project_name, location_input_task_list)
		
		# load location
		result = self.location_load_exists(context, project_name, location_content_data, location_task_data)
		if not result[0]:
			return(False, result[1])
			
		# ceate text data block  G.content_of_location
		if not G.content_of_location in bpy.data.texts.keys():
			text = bpy.data.texts.new(G.content_of_location)
		else:
			text = bpy.data.texts[G.content_of_location]
		text.clear()
		text.write((json.dumps(location_content_data, sort_keys=True, indent=4)))
		
		return(True, 'Ok!')
		
	def load_exists_shot_animation_content(self, context, project_name, current_content_data, task_data):
		# get shot_anim_content_data
		if not current_content_data:
			return(False, 'Not Content!')
		
		content_data = {}
		for key in current_content_data:
			content_data[key] = current_content_data[key]
		
		# -- from
		if G.content_of_location in bpy.data.texts.keys():
			text = bpy.data.texts[G.content_of_location]
			data = None
			try:
				data = json.loads(text.as_string())
			except:
				pass
			if data:
				for key in data:
					#current_content_data[key] = data[key]
					content_data[key] = data[key]
		
		# load exists
		result = self.location_load_exists(context, project_name, content_data, task_data)
		if not result[0]:
			return(False, result[1])
		'''	
		# Load Shot Camera
		result = self.db_log.camera_read_log(project_name, task_data)
		if not result[0]:
			print('WARNING!', result[1])
		else:
			res = self.load_current_shot_camera(context, project_name, task_data, result[1], 'last')
			if not res[0]:
				print('WARNING!', res[1])
		'''
		return(True, 'Ok!')
		
	def add_object_to_group_of_camera(self, context, task_data, action):
		name = 'camera.' + task_data['asset']
		
		# GROUP
		group = None
		if not name in bpy.data.groups.keys():
			group = bpy.data.groups.new(name)
		else:
			group = bpy.data.groups[name]
		
		if action == 'add':
			# ADD objects
			execution = False
			for ob in bpy.data.objects:
				if ob.select:
					execution = True
					if ob.name not in group.objects.keys():
						group.objects.link(ob)

			if not execution:
				return(False, 'Not selected objects!')
				
		elif action == 'unlink':
			# ADD objects
			execution = False
			for ob in bpy.data.objects:
				if ob.select:
					execution = True
					if ob.name in group.objects.keys():
						group.objects.unlink(ob)

			if not execution:
				return(False, 'Not selected objects!')
				
		return(True, 'Ok!')
		
	def push_current_shot_camera(self, context, project_name, task_data, comment):
		from .push_camera import file_data
		name = '.push_camera_action.py'
		
		# ******* GET DATA *******
		# -- this path
		this_path = context.blend_data.filepath
		# -- save path
		w_task_data = {}
		w_task_data.update(task_data)
		
		w_task_data['activity'] = 'camera'
		result = self.db_task.get_new_file_path(project_name, w_task_data)
		if not result[0]:
			return(False, result[1])
		# -- -- make version dir
		version_dir = result[1][0]
		if not os.path.exists(result[1][0]):
			os.mkdir(version_dir)
		save_path = result[1][1]
		# -- link objects list
		# -- -- group name
		group_name = 'camera.' + task_data['asset']
		# -- -- actions
		actions = {}
		for ob in bpy.data.groups[group_name].objects:
			if ob.animation_data:
				action_name = ob.animation_data.action.name
				actions[ob.name] = action_name
				
		actions = json.dumps(actions)
		# start / end
		start = str(context.scene.frame_start)
		end = str(context.scene.frame_end)
		
		# make string of data
		#data = "{'this_path': \'" + this_path + "\', 'save_path': \'" + save_path + "\', 'group': \'" + group_name + "\', 'actions': " + actions + ",'start': " + start + ", 'end': " + end + "}"
		if platform.system() == 'Windows':
			data = "{'this_path': %s, 'save_path': %s, 'group': \'%s\', 'actions': %s, 'start': %s, 'end': %s}" % (os.path.normpath(this_path.encode('unicode-escape')), os.path.normpath(save_path.encode('unicode-escape')), group_name, actions, start, end)
		else:
			data = "{'this_path': \'%s\', 'save_path': \'%s\', 'group': \'%s\', 'actions': %s,  'start': %s, 'end': %s}" % (this_path, save_path, group_name, actions, start, end)
		
		# ******* SAVE ******* 
		bpy.ops.wm.save_as_mainfile(filepath = this_path, check_existing = True)
		
		# ******* RUN ******* 
		home = os.path.expanduser('~')
		path = os.path.join(home, self.db_task.init_folder, name)
		
		with open(path, 'w') as f:
			f.write(file_data % data)
		
		cmd = 'blender -b --python ' + path
		proc = subprocess.Popen(cmd, shell = True)
		proc.wait()
		
		# ******* LOG *******
		version = os.path.basename(version_dir)
		log = self.db_log.camera_notes_log(project_name, task_data, comment, version)
		if not log[0]:
			return(False, log[1])
		
		return(True, 'Ok!')
		
	def load_current_shot_camera(self, context, project_name, task_data, logs_list, action): # action - last or num
		# get path
		path = None
		log_version = None
		if action != 'last':
			for log in logs_list:
				if log['version'] == action:
					log_version = log['version']
		else:
			log_version = logs_list[len(logs_list) - 1]['version']
			
		path = os.path.join(task_data['asset_path'], self.db_task.activity_folder[task_data['asset_type']]['camera'], log_version, (task_data['asset'] + task_data['extension']))
		path = os.path.normpath(path)
		
		if not os.path.exists(path):
			return(False, ('No found file: ' + path))
			
		# load camera
		# -- load meta_data
		meta_data_name = 'camera_meta_data'
		
		with bpy.data.libraries.load(path, link=False) as (data_src, data_dst):
			texts_list = []
			for name in data_src.texts:
				if meta_data_name == name:
					texts_list.append(name)
		
			data_dst.texts = texts_list
			
		if not texts_list:
			return(False, ('No data.texts[\"camera_meta_data\"] in file: ' + path))
			
		text = bpy.data.texts[meta_data_name]
		cam_data = json.loads(text.as_string())
		
		group_name = cam_data['group']
		group_actions = cam_data['actions']
		
		# -- remove old camera
		cam_group = None
		if group_name in bpy.data.groups.keys():
			cam_group = bpy.data.groups[group_name]
			
		if cam_group:
			for ob in cam_group.objects:
				ob_name = ob.name
				# remove objects
				for scene in bpy.data.scenes:
					if ob.name in scene.objects.keys():
						scene.objects.active = ob
						bpy.ops.object.mode_set(mode='OBJECT')
						scene.objects.unlink(ob)
				try:
					bpy.data.objects.remove(ob, do_unlink = True)
				except:
					ob.name = 'deleted'
				
				# remove action
				if ob_name in group_actions:
					action_name = group_actions[ob_name]
					if action_name in bpy.data.actions.keys():
						action = bpy.data.actions[action_name]
						action.name = action_name + '.removed'
						try:
							bpy.data.actions.remove(action, do_unlink = True)
						except:
							pass
						
			# remove group
			bpy.data.groups.remove(cam_group, do_unlink = True)
					
		# -- load camera
		actions = group_actions

		# get list actions
		list_actions = []
		for key in actions:
			list_actions.append(actions[key])
			
		# link group
		with bpy.data.libraries.load(path, link=False) as (data_src, data_dst):
			data_dst.groups = [group_name]
			data_dst.actions = list_actions

		for ob in bpy.data.groups[group_name].objects:
			# link ob to scene
			bpy.context.scene.objects.link(ob)
			
			# append action
			if not ob.name in actions.keys():
				continue
			if not ob.animation_data:
				ob.animation_data_create()
			ob.animation_data.action = bpy.data.actions[actions[ob.name]]
		
		# set start / end frame
		context.scene.frame_start = cam_data['start']
		context.scene.frame_end = cam_data['end']
		
		# -- -- remove text
		bpy.data.texts.remove(text, do_unlink = True)
		
		return(True, 'Ok!')
		
	def active_shot_camera(self, context, task_data):
		# get cam name
		cam_name = 'camera.' + task_data['asset']
		
		# get cam
		if cam_name in bpy.data.objects.keys():
			cam = bpy.data.objects[cam_name]
		
		# set cam
		if context.area.type == 'VIEW_3D':
			context.scene.camera = cam
			context.space_data.show_only_render = True
			bpy.ops.view3d.viewnumpad(type = 'CAMERA')
			context.scene.update()
		else:
			return(False, 'Current area is not the \"VIEW_3D\"!')
			
		return(True, 'Ok!')
		
	def make_playblast(self, context, project_name, task_data, comment):
		# get render path
		w_task_data = {}
		w_task_data.update(task_data)
		
		w_task_data['activity'] = 'pleyblast_sequence'
		w_task_data['extension'] = '.avi'
		result = self.db_task.get_new_file_path(project_name, w_task_data)
		
		if not result[0]:
			return(False, result[1])
			
		# -- -- make version dir
		version_dir = result[1][0]
		if not os.path.exists(result[1][0]):
			os.mkdir(version_dir)
		save_path = result[1][1]
		
		# set render options
		context.scene.render.image_settings.file_format = 'H264'
		context.scene.render.image_settings.color_mode = 'RGB'
		context.scene.render.ffmpeg.format = 'AVI'
		context.scene.render.ffmpeg.codec = 'H264'
		context.scene.render.ffmpeg.video_bitrate = 6000
		context.scene.render.ffmpeg.audio_codec = 'MP3'
		context.scene.render.ffmpeg.audio_bitrate = 128
		context.scene.render.filepath = save_path
		
		# render
		bpy.ops.render.opengl(animation=True, sequencer=False)
		
		# ******* LOG *******
		version = os.path.basename(version_dir)
		log = self.db_log.playblast_notes_log(project_name, w_task_data, comment, version)
		if not log[0]:
			return(False, log[1])
		
		return(True, 'Ok!')
		
	# mesh cache
	def get_sampled_frames(self, start, end, sampling):
		return [math.modf(start + x * sampling) for x in range(int((end - start) / sampling) + 1)]

	def shot_animation_export_point_cache(self, context, project_name, task_data, action, sampling = 1, world_space = False, rot_x90 = False):
		# *** export Action
		from .rig_export_one_action import file_data
		
		# get ob_list
		# -- get asset list
		assets_list = []
		assets_data_list = {}
		objects_data = []
		
		sc = context.scene
		apply_modifiers = True
		mat_x90 = mathutils.Matrix.Rotation(-math.pi/2, 4, 'X')
		#start = sc.frame_start
		start = 1
		end = sc.frame_end
		sampletimes = self.get_sampled_frames(start, end, sampling)
		sampleCount = len(sampletimes)
		
		if action == 'select':
			sel_objects_list = []
			for ob in bpy.data.objects:
				if ob.select:
					asset_name = ob.name.split('.')[0]
					if not asset_name in assets_list and asset_name in bpy.data.texts.keys():
						assets_list.append(asset_name)
		
		elif action == 'all':
			# get content list
			file_name = self.db_task.location_position_file
			dir_name = self.db_task.additional_folders['meta_data']
			path = os.path.join(task_data['asset_path'], dir_name, file_name)
			path = os.path.normpath(path)
			if not os.path.exists(path):
				return(False, ('Not Found ' + path + '!'))
				
			with open(path, 'r') as f:
				jsn = json.load(f)
				
			for key in jsn:
				if jsn[key][3]:
					asset_name = jsn[key][3].split('.')[0]
					if not asset_name in assets_list and asset_name in bpy.data.texts.keys():
						assets_list.append(asset_name)
						
		elif action == 'this_asset':
			assets_list = [task_data['asset']]
		
		else:
			return(False, 'incorrect action!')
			
		if not assets_list:
			return(False, 'Not Characters!')
			
		# get assets_data_list
		result = self.db_task.get_name_data_dict_by_all_types(project_name)
		if not result[0]:
			return(False, (result[1] + ' ***'))
		else:
			assets_data_list = result[1]
			
		# get mesh data (ob, path)
		for asset_name in assets_list:
			# *** export Action
			for ob in context.scene.objects:
				if ob.name.split('.')[0] == asset_name:
					action = None
					if ob.type == 'ARMATURE':
						print('rig: ', ob.name)
						if ob.animation_data:
							action = ob.animation_data.action
							action.name = asset_name + '.Action'
							#actions[ob.name] = action.name
							
							#actions = json.dumps(actions)
							
							# -- get this_path and save_path
							this_path = context.blend_data.filepath
							result = self.db_task.get_new_cache_file_path(project_name, task_data, action.name, activity = 'actions', extension = '.blend')
							if not result[0]:
								return(False, result[1])
							save_path = result[1][1]
							
							print('path: ', save_path)
							
							# -- make string of data
							#data = "{'this_path': \'" + this_path + "\', 'save_path': \'" + save_path + "\', 'action': \'" + action.name + "\'}"
							if platform.system() == 'Windows':
								data = "{'this_path': %s, 'save_path': %s, 'action': \'%s\'}" % (os.path.normpath(this_path.encode('unicode-escape')), os.path.normpath(save_path.encode('unicode-escape')), action.name)
							else:
								data = "{'this_path': \'%s\', 'save_path': \'%s\', 'action': \'%s\'}" % (this_path, save_path, action.name)
							
							# -- save this file
							bpy.ops.wm.save_as_mainfile(filepath = this_path, check_existing = True)
							
							# -- run script
							home = os.path.expanduser('~')
							path = os.path.join(home, self.db_task.init_folder, self.actions_python_file_name)
							
							with open(path, 'w') as f:
								f.write(file_data % data)
							
							cmd = 'blender -b --python ' + path
							proc = subprocess.Popen(cmd, shell = True)
							proc.wait()
			# ***
			
			# get group list
			group_list = []
			for group_name in bpy.data.groups.keys():
				if asset_name in group_name:
					group_list.append(group_name)
			
			# get objects
			text = bpy.data.texts[asset_name]
			data = json.loads(text.as_string())
			try:
				output_mesh_list = data['output_cache']
			except:
				return(False, ('for \"' + asset_name + '\" not found \"output cache\" list!'))
			
			# get objects data
			for ob_name in output_mesh_list:
				ob_data = {}
				for group_name in group_list:
					if ob_name in bpy.data.groups[group_name].objects.keys():
						# get object
						ob_data['ob'] = (group_name, ob_name)
						# get cache path
						if action == 'this_asset':
							cache_dir_name = ob_name
						else:
							cache_dir_name = asset_name + '_' + ob_name
						result = self.db_task.get_new_cache_file_path(project_name, task_data, cache_dir_name)
						if not result[0]:
							return(False, result[1])
						ob_data['cache_path'] = result[1][1]
						# Create the header
						ob = bpy.data.groups[group_name].objects[ob_name]
						me = ob.to_mesh(sc, apply_modifiers, 'PREVIEW')
						vertCount = len(me.vertices)
						headerFormat='<12siiffi'
						headerStr = struct.pack(headerFormat, b'POINTCACHE2\0', 1, vertCount, start, sampling, sampleCount)
						ob_data['headerStr'] = headerStr
						ob_data['vertCount'] = vertCount
						ob_data['Vertices'] = []
						ob_data['good_mesh'] = True
						
						objects_data.append(ob_data)
						break
			
			
		
		for frame in sampletimes:
			sc.frame_set(int(frame[1]), frame[0])  # stupid modf() gives decimal part first!
			for ob_data in objects_data:
				ob = bpy.data.groups[ob_data['ob'][0]].objects[ob_data['ob'][1]]
				me = ob.to_mesh(sc, apply_modifiers, 'PREVIEW')
				# test good mesh
				if not ob_data['good_mesh']:
					continue
				if len(me.vertices) != ob_data['vertCount']:
					ob_data['good_mesh'] = False
					continue
				
				# transform matrix
				if world_space:
					me.transform(ob.matrix_world)
				if rot_x90:
					me.transform(mat_x90)
				
				# get vertex
				for v in me.vertices:
					thisVertex = struct.pack('<fff', float(v.co[0]), float(v.co[1]), float(v.co[2]))
					ob_data['Vertices'].append(thisVertex)
		
		for ob_data in objects_data:
			file = open(ob_data['cache_path'], "wb")
			file.write(ob_data['headerStr'])
			
			for thisVertex in ob_data['Vertices']:
				file.write(thisVertex)
			
			file.flush()
			file.close()
			
		
		return(True, 'Ok!')
		
		#ob = bpy.data.groups['miss.Base'].objects['Sphere']
		
		# get filepath
		
		'''
		### debug
		ob = context.active_object
		filepath = '/home/vofka/cache.blend.pc2'
		return(False, 'Ok!')
		### debug
		
		# get other
		mat_x90 = mathutils.Matrix.Rotation(-math.pi/2, 4, 'X')
		sc = context.scene
		start = sc.frame_start
		end = sc.frame_end
		apply_modifiers = True
		me = ob.to_mesh(sc, apply_modifiers, 'PREVIEW')
		vertCount = len(me.vertices)
		sampletimes = self.get_sampled_frames(start, end, sampling)
		sampleCount = len(sampletimes)
		
		# Create the header
		headerFormat='<12siiffi'
		headerStr = struct.pack(headerFormat, b'POINTCACHE2\0',
					1, vertCount, start, sampling, sampleCount)

		file = open(filepath, "wb")
		file.write(headerStr)

		for frame in sampletimes:
			sc.frame_set(int(frame[1]), frame[0])  # stupid modf() gives decimal part first!
			me = ob.to_mesh(sc, apply_modifiers, 'PREVIEW')

			if len(me.vertices) != vertCount:
				file.close()
				try:
					os.remove(filepath)
				except:
					empty = open(filepath, 'w')
					empty.write('DUMMIFILE - export failed\n')
					empty.close()
				return(False, 'Export failed. Vertexcount of Object is not constant')

			
			if props.world_space:
				me.transform(ob.matrix_world)
			if props.rot_x90:
				me.transform(mat_x90)
			
			for v in me.vertices:
				thisVertex = struct.pack('<fff', float(v.co[0]), float(v.co[1]), float(v.co[2]))
				file.write(thisVertex)

		file.flush()
		file.close()
		'''
		
	### ********* Rig ********
	def create_empty_group(self, context, task_data, name):
		group_name = task_data['asset'] + '.' + name
		# test exists name
		if group_name in bpy.data.groups.keys():
			return(False, ('Group with name \"' + name + '\" already exists!'))
			
		grp = bpy.data.groups.new(group_name)
		
		return(True, name)
		
	def add_objects_to_group(self, context, group_name):
		if group_name == '--select group--':
			return(False, 'Not Selected Group!')
		
		group = bpy.data.groups[group_name]
		
		for ob in bpy.data.objects:
			if ob.select:
				if ob.name not in group.objects.keys():
					group.objects.link(ob)
		
		return(True, 'Ok!')
		
	def unlink_objects_from_group(self, context, group_name):
		if group_name == '--select group--':
			return(False, 'Not Selected Group!')
			
		group = bpy.data.groups[group_name]
		
		for ob in bpy.data.objects:
			if ob.select:
				if ob.name in group.objects.keys():
					group.objects.unlink(ob)
	
		return(True, 'Ok!')
		
	def add_object_to_cache_passport(self, context, action, task_data):
		text_name = task_data['asset']
		if action == 'output':
			dict_name = 'output_cache'
		elif action == 'input':
			dict_name = 'input_cache'
		else:
			return(False, 'epte!')
		
		text = None
		data = {}
		if not text_name in bpy.data.texts.keys():
			text = bpy.data.texts.new(text_name)
			data[dict_name] = []
		
		else:
			text = bpy.data.texts[text_name]
			try:
				data = json.loads(text.as_string())
			except:
				pass
			
		if not dict_name in data.keys():
			data[dict_name] = []
		
		exist = None
		for ob in bpy.data.objects:
			if ob.select and ob.type == 'MESH':
				if not ob.name in data[dict_name]:
					data[dict_name].append(ob.name)
					exist = True
		
		if not exist:
			return(False, 'Not Selected Objects!')
		else:
			text.clear()
			text.write(json.dumps(data, sort_keys=True, indent=4))
		
		return(True, 'Ok!')
		
	def remove_object_frome_cache_passport(self, context, action, task_data):
		text_name = task_data['asset']
		if action == 'output':
			dict_name = 'output_cache'
		elif action == 'input':
			dict_name = 'input_cache'
		else:
			return(False, 'epte!')
		
		text = None
		data = None
		if text_name in bpy.data.texts.keys():
			text = bpy.data.texts[text_name]
		else:
			return(False, 'Not Exists Passports!')
		
		try:
			data = json.loads(text.as_string())
		except:
			return(False, 'Not Exists Passport!')
		
		exist = None
		for ob in bpy.data.objects:
			if ob.select and ob.name in data[dict_name]:
				data[dict_name].remove(ob.name)
				exist = True
		
		if not exist:
			return(False, 'Not Selected Objects!')
		else:
			text.clear()
			text.write(json.dumps(data, sort_keys=True, indent=4))
		
		return(True, 'Ok!')
		
	def select_object_frome_cache_passport(self, context, action, task_data):
		text_name = task_data['asset']
		if action == 'output':
			dict_name = 'output_cache'
		elif action == 'input':
			dict_name = 'input_cache'
		else:
			return(False, 'epte!')
		
		text = None
		data = None
		if text_name in bpy.data.texts.keys():
			text = bpy.data.texts[text_name]
		else:
			return(False, 'Not Exists Passports!')
		
		try:
			data = json.loads(text.as_string())
		except:
			return(False, 'Not Exists Passport! *')
		if not dict_name in data.keys():
			return(False, 'Not Exists Passport! **')
			
		for ob in bpy.data.objects:
			ob.select = False
		
		exist = False
		for ob in bpy.data.objects:
			if ob.name in data[dict_name]:
				ob.select = True
				exist = True
				
		if not exist:
			return(False, 'Passport empty!')
						
		return(True, 'Ok!')
		
	def rig_export_pc2_point_cache(self, context, task_data, version_name, sampling = 1, world_space = False, rot_x90 = False, extension = '.pc2'):
		# get version path
		activity_path = os.path.join(task_data['asset_path'], self.db_task.activity_folder[task_data['asset_type']]['cache'])
		activity_path = os.path.normpath(activity_path)
		if not os.path.exists(activity_path):
			try:
				os.mkdir(activity_path)
			except:
				return(False, 'not created of activity directory!')
				
		version_path = os.path.normpath(os.path.join(activity_path, version_name))
		if not os.path.exists(version_path):
			os.mkdir(version_path)
			pass
		
		# *** export Action
		from .rig_export_actions import file_data
		# -- get actions list
		actions = {}
		for ob in bpy.data.objects:
			action = None
			if ob.type == 'ARMATURE':
				if ob.animation_data:
					action = ob.animation_data.action
					action.name = ob.name + '.Action'
					actions[ob.name] = action.name
		actions = json.dumps(actions)
		
		# -- get this_path and save_path
		this_path = context.blend_data.filepath
		save_path = os.path.join(version_path, self.actions_file_name)
		
		# -- make string of data
		if platform.system() == 'Windows':
			data = "{'this_path': %s, 'save_path': %s, 'actions': %s}" % (os.path.normpath(this_path.encode('unicode-escape')), os.path.normpath(save_path.encode('unicode-escape')), actions)
		else:
			data = "{'this_path': \'%s\', 'save_path': \'%s\', 'actions': %s}" % (this_path, save_path, actions)
		
		# -- save this file
		bpy.ops.wm.save_as_mainfile(filepath = this_path, check_existing = True)
		
		# -- run script
		home = os.path.expanduser('~')
		path = os.path.join(home, self.db_task.init_folder, self.actions_python_file_name)
		
		with open(path, 'w') as f:
			f.write(file_data % data)
		
		cmd = 'blender -b --python ' + path
		proc = subprocess.Popen(cmd, shell = True)
		proc.wait()
		# ***
		
		# get obj_list
		res = self.get_cache_list('output_cache', task_data['asset'])
		if not res[0]:
			return(False, res[1])
		ob_list = res[1]
		
		# get cache
		sc = context.scene
		apply_modifiers = True
		mat_x90 = mathutils.Matrix.Rotation(-math.pi/2, 4, 'X')
		start = sc.frame_start
		end = sc.frame_end
		sampletimes = self.get_sampled_frames(start, end, sampling)
		sampleCount = len(sampletimes)
		
		objects_data = []
		
		for ob_name in ob_list:
			ob_data = {}
			if ob_name in bpy.data.objects.keys():
				# get object
				ob_data['ob'] = ob_name
				# get cache path
				cache_path = os.path.join(version_path, (ob_name + extension))
				cache_path = os.path.normpath(cache_path)
				ob_data['cache_path'] = cache_path
				# Create the header
				ob = bpy.data.objects[ob_name]
				me = ob.to_mesh(sc, apply_modifiers, 'PREVIEW')
				vertCount = len(me.vertices)
				headerFormat='<12siiffi'
				headerStr = struct.pack(headerFormat, b'POINTCACHE2\0', 1, vertCount, start, sampling, sampleCount)
				ob_data['headerStr'] = headerStr
				ob_data['vertCount'] = vertCount
				ob_data['Vertices'] = []
				ob_data['good_mesh'] = True
				
				objects_data.append(ob_data)
				
		
		for frame in sampletimes:
			sc.frame_set(int(frame[1]), frame[0])  # stupid modf() gives decimal part first!
			for ob_data in objects_data:
				ob = bpy.data.objects[ob_data['ob']]
				me = ob.to_mesh(sc, apply_modifiers, 'PREVIEW')
				# test good mesh
				if not ob_data['good_mesh']:
					continue
				if len(me.vertices) != ob_data['vertCount']:
					ob_data['good_mesh'] = False
					continue
				
				# transform matrix
				if world_space:
					me.transform(ob.matrix_world)
				if rot_x90:
					me.transform(mat_x90)
				
				# get vertex
				for v in me.vertices:
					thisVertex = struct.pack('<fff', float(v.co[0]), float(v.co[1]), float(v.co[2]))
					ob_data['Vertices'].append(thisVertex)
		
		for ob_data in objects_data:
			file = open(ob_data['cache_path'], "wb")
			file.write(ob_data['headerStr'])
			
			for thisVertex in ob_data['Vertices']:
				file.write(thisVertex)
			
			file.flush()
			file.close()
					
		return(True, 'cache added!')
		
	def rig_get_versions_list_point_cache(self, context, task_data):
		# get version path
		activity_path = os.path.join(task_data['asset_path'], self.db_task.activity_folder[task_data['asset_type']]['cache'])
		activity_path = os.path.normpath(activity_path)
		if not os.path.exists(activity_path):
			return(False, 'not cache activity directory!')
		
		versions_list = []
		for directory in os.listdir(activity_path):
			path = os.path.normpath(os.path.join(activity_path, directory))
			if os.path.isdir(path):
				versions_list.append(directory)
		if versions_list:
			return(True, versions_list)
		else:
			return(False, 'No found versions!')
		
	def rig_clear_pc2_point_cache(self, context, task_data):
		# remove actions
		for ob in bpy.data.objects:
			if ob.type == 'ARMATURE':
				if ob.animation_data:
					action = ob.animation_data.action
					if action:
						action.use_fake_user = False
						action.name = 'removed'
						ob.animation_data.action = None
		
		# get input cache obj list
		text_name = task_data['asset']
		dict_name = 'input_cache'
				
		text = None
		data = {}
		input_cache_objects = []
		
		if not text_name in bpy.data.texts.keys():
			return(False, 'No Found Input_Cache List!')
		else:
			text = bpy.data.texts[text_name]
			try:
				data = json.loads(text.as_string())
				input_cache_objects = data[dict_name]
			except:
				return(False, 'No Found Input_Cache List! *')
		
		all_ob_list = bpy.data.objects.keys()
		for obj_name in input_cache_objects:
			# get obj
			if obj_name in all_ob_list:
				obj = bpy.data.objects[obj_name]
			else:
				continue
			
			# get modif
			if dict_name in obj.modifiers.keys():
				modif = obj.modifiers[dict_name]
			else:
				continue
			
			obj.modifiers.remove(modif)
			
		return(True, 'cache removed')
		
	def rig_import_pc2_point_cache(self, context, task_data, version_name, extension = '.pc2'):
		# get version dir path
		activity_path = os.path.join(task_data['asset_path'], self.db_task.activity_folder[task_data['asset_type']]['cache'])
		activity_path = os.path.normpath(activity_path)
		if not os.path.exists(activity_path):
			return(False, 'no found activity directory!')
				
		version_path = os.path.normpath(os.path.join(activity_path, version_name))
		if not os.path.exists(version_path):
			return(False, 'no found version directory!')
			
		# *** import Actions
		armatures = []
		for ob in bpy.data.objects:
			if ob.type == 'ARMATURE':
				armatures.append(ob)
		
		path = os.path.join(version_path, self.actions_file_name)
		
		if os.path.exists(path):
			with bpy.data.libraries.load(path, link=False) as (data_src, data_dst):
				list_actions = data_src.actions
				data_dst.actions = list_actions
				
			for rig in armatures:
				#action_name = (ob.name + '.Action')
				for action in list_actions:
					if action.name == (rig.name + '.Action'):
						#action = bpy.data.actions[action_name]
						action.use_fake_user = True
						if not rig.animation_data:
							rig.animation_data_create()
						else:
							if rig.animation_data.action:
								rig.animation_data.action.use_fake_user = False
								rig.animation_data.action.name = 'removed'
						rig.animation_data.action = action
		# ***
		
		# get input cache obj list
		text_name = task_data['asset']
		dict_name = 'input_cache'
				
		text = None
		data = {}
		input_cache_objects = []
		
		if not text_name in bpy.data.texts.keys():
			return(False, 'No Found Input_Cache List!')
		else:
			text = bpy.data.texts[text_name]
			try:
				data = json.loads(text.as_string())
				input_cache_objects = data[dict_name]
			except:
				return(False, 'No Found Input_Cache List! *')
		
		all_ob_list = bpy.data.objects.keys()
		for obj_name in input_cache_objects:
			# get obj
			if obj_name in all_ob_list:
				obj = bpy.data.objects[obj_name]
			else:
				continue
			
			# load cache
			cache_path = os.path.join(version_path, (obj_name + extension))
			cache_path = os.path.normpath(cache_path)
			if not os.path.exists(cache_path):
				print(('*** No found Cache: ' + obj_name))
				continue
			
			# -- make constraint
			if not dict_name in obj.modifiers.keys():
				modif = obj.modifiers.new(dict_name, type = 'MESH_CACHE')
			else:
				modif = obj.modifiers[dict_name]
			modif.cache_format = 'PC2'
			modif.filepath = cache_path
			
			# -- -- get start frame
			file = open(cache_path, 'rb')
			headerFormat = '<12ciiffi'
			header = unpack(headerFormat, file.read(32))
			
			#numPoints = header[13]
			startFrame = int(header[14])
			#sampleRate = header[15]
			#numSamples = header[16]
			
			modif.frame_start = startFrame
			modif.deform_mode = 'INTEGRATE'
			
		return(True, 'Ok!')
		
	### ********* TECH ANIM ********
	def load_char_to_tech_anim(self, context, project_name, asset_data, task_data):
		# get group list
		result = self.get_group_list(project_name, asset_data, 'model')
		if not result[0]:
			return(False, result[1])
		
		if not result[1]:
			return(False, 'No Found Groups!')
		elif len(result[1]) == 1:
			group_name = result[1][0]
			file_path = result[2]
		elif len(result[1]) > 1:
			return(True, result[1], result[2])
		
		# load group
		if not os.path.exists(file_path):
			return(False, 'Not File Path!')
		self.load_char_group(context, file_path, task_data, group_name, link = False)
		
		return(True, 'Ok!')
		
	def clear_char_from_tech_anim(self, context, project_name, asset_data):
		# get group
		group = None
		for group_name in bpy.data.groups.keys():
			if asset_data['name'] in group_name:
				group = bpy.data.groups[group_name]
				
		if not group:
			return(False, 'No Found Group!')
			
		# clear objects
		for ob in group.objects:
			if ob.type == 'MESH':
				mesh = ob.data
				mesh.name = 'removed'
				for scene in bpy.data.scenes:
					scene.objects.unlink(ob)
				group.objects.unlink(ob)
				ob.parent = None
				ob.name = 'removed'
				try:
					bpy.data.objects.remove(ob, do_unlink=True)
				except:
					pass
		# clear group
		bpy.data.groups.remove(group, do_unlink=True)
		
		# clear root
		if asset_data['name'] in bpy.data.objects:
			empty = bpy.data.objects[asset_data['name']]
			for scene in bpy.data.scenes:
				scene.objects.unlink(empty)
			try:
				bpy.data.objects.remove(empty, do_unlink=True)
			except:
				pass
		
		return(False, 'Ok!')
		
	def load_obj_to_tech_anim(self, context, project_name, asset_data, task_data, link = False):
		# get group list
		result = self.db_task.get_publish_file_path(project_name, asset_data, 'model')
		if not result[0]:
			return(False, result[1])
			
		file_path = result[1]
		
		action = None
		
		with bpy.data.libraries.load(file_path, link=link) as (data_src, data_dst):
			if asset_data['name'] in data_src.groups:
				data_dst.groups = [asset_data['name']]
				action = 'group'
			
			elif asset_data['name'] in data_src.meshes:
				data_dst.meshes = [asset_data['name']]
				action = 'mesh'
			
		
		if action == 'group':
			ob = bpy.data.objects.new(asset_data['name'], None)
			group = bpy.data.groups[asset_data['name']]
			ob.dupli_group = group
			ob.dupli_type = 'GROUP'
			if not ob.name in context.scene.objects.keys():
				context.scene.objects.link(ob)
			return(True, 'Ok!')
			
		elif action == 'mesh':
			me = bpy.data.meshes[asset_data['name']]
			ob = bpy.data.objects.new(asset_data['name'], me)
			if not ob.name in context.scene.objects.keys():
				context.scene.objects.link(ob)
			return(True, 'Ok!')
			
		else:
			return(False, 'No Found Object!')
		
	def get_position_at_tech_anim(self, context, project_name, task_data):
		# get current asset
		ob = context.object
		if not ob:
			return(False, 'No Selected Group!')
		
		# get content_list
		result = self.get_shot_animation_content(project_name, task_data)
		if not result[0]:
			return(False, result[1])
		
		data = {}
		name = ob.name
		for key in result[1]:
			if key.split('.')[0] == name:
				data[key] = result[1][key]
				
		if not data:
			parent = ob.parent
			if parent:
				name = parent.name
			else:
				return(False, 'The selected object is not a Group! **')
				
			for key in result[1]:
				if key.split('.')[0] == name:
					data[key] = result[1][key]
				
		if not data:
			return(False, 'The selected object is not a Group! ***')
		
		return(True, (data, name))
		
	def tech_anim_get_versions_list(self, context, task_data):
		ob = context.object
		
		if ob:
			result = self.db_task.get_versions_list_of_cache_by_object(task_data, ob.name.split('.')[0])
			if not result[0]:
				return(False, result[1])
			else:
				return(result)
			
		else:
			return(False, 'No Selected Object!')
		
	def tech_anim_import_version_cache(self, context, ob_name, file_path, make_modifier = False):
		# 
		ob_name = ob_name.split('.')[0]
		
		if not ob_name in bpy.data.objects.keys():
			return(False, ('No Object with name:' + ob_name))
			
		ob = bpy.data.objects[ob_name]
		
		if not 'input_cache' in ob.modifiers.keys():
			if not make_modifier:
				return(False, ('This object has no modifier: \"' + 'input_cache' + '\"'))
			else:
				modif = ob.modifiers.new('input_cache', type = 'MESH_CACHE')
				modif.cache_format = 'PC2'
			
		modif = ob.modifiers['input_cache']
		
		modif.filepath = file_path
		
		# get start frame
		file = open(file_path, 'rb')
		headerFormat = '<12ciiffi'
		header = unpack(headerFormat, file.read(32))
		
		#numPoints = header[13]
		startFrame = int(header[14])
		#sampleRate = header[15]
		#numSamples = header[16]
		
		modif.frame_start = startFrame
		modif.deform_mode = 'INTEGRATE'
		
		dir_path = os.path.dirname(file_path)
		version = os.path.basename(dir_path)
		
		return(True, ('loaded cache version: ' + version))
		
	def tech_anim_export_point_cache(self, context, project_name, task_data, content_assets_list, action, sampling = 1, world_space = False, rot_x90 = False):
		# start data
		sc = context.scene
		apply_modifiers = True
		mat_x90 = mathutils.Matrix.Rotation(-math.pi/2, 4, 'X')
		#start = sc.frame_start
		start = 1
		end = sc.frame_end
		sampletimes = self.get_sampled_frames(start, end, sampling)
		sampleCount = len(sampletimes)
		
		assets_list = []
		current_mesh = context.object
		single_cache_path = False
		
		if action in ['select', 'mesh']:
			select_list = []
			for ob in bpy.data.objects:
				if ob.select:
					name = ob.name.split('.')[0]
					if name in content_assets_list.keys():
						if not name in assets_list:
							assets_list.append(name)
					elif ob.parent:
						name = ob.parent.name.split('.')[0]
						if name in content_assets_list.keys():
							if not name in assets_list:
								assets_list.append(name)
		
			
		elif action == 'all':
			for group in bpy.data.groups:
				name = group.name.split('.')[0]
				if name in content_assets_list.keys():
					if not name in assets_list:
						assets_list.append(name)
		else:
			return(False, 'incorrect action!')
			
		if not assets_list:
			return(False, 'Not Characters!')
			
		print(assets_list)
		
		# get mesh data (ob, path)
		objects_data = []
		for asset_name in assets_list:
			asset_objects = []
			for group in bpy.data.groups:
				if group.name.split('.')[0] == asset_name:
					for ob_name in group.objects.keys():
						###
						if action == 'mesh':
							if ob_name != current_mesh.name:
								continue
						if ob_name in asset_objects:
							continue
						else:
							asset_objects.append(ob_name)
						###
						ob_data = {}
						# get object
						ob_data['ob'] = (group.name, ob_name)
						# get cache path
						#cache_dir_name = asset_name + '_' + ob_name
						cache_dir_name = ob_name.split('.')[0]
						result = self.db_task.get_new_cache_file_path(project_name, task_data, cache_dir_name)
						if not result[0]:
							return(False, result[1])
						ob_data['cache_path'] = result[1][1]
						if action == 'mesh':
							single_cache_path = ob_data['cache_path']
						# Create the header
						ob = bpy.data.groups[group.name].objects[ob_name]
						me = ob.to_mesh(sc, apply_modifiers, 'PREVIEW')
						vertCount = len(me.vertices)
						headerFormat='<12siiffi'
						headerStr = struct.pack(headerFormat, b'POINTCACHE2\0', 1, vertCount, start, sampling, sampleCount)
						ob_data['headerStr'] = headerStr
						ob_data['vertCount'] = vertCount
						ob_data['Vertices'] = []
						ob_data['good_mesh'] = True
						
						objects_data.append(ob_data)
					'''
					if action != 'mesh':
						break
					'''
			
		for frame in sampletimes:
			sc.frame_set(int(frame[1]), frame[0])  # stupid modf() gives decimal part first!
			for ob_data in objects_data:
				ob = bpy.data.groups[ob_data['ob'][0]].objects[ob_data['ob'][1]]
				me = ob.to_mesh(sc, apply_modifiers, 'PREVIEW')
				# test good mesh
				if not ob_data['good_mesh']:
					continue
				if len(me.vertices) != ob_data['vertCount']:
					ob_data['good_mesh'] = False
					continue
				
				# transform matrix
				if world_space:
					me.transform(ob.matrix_world)
				if rot_x90:
					me.transform(mat_x90)
				
				# get vertex
				for v in me.vertices:
					thisVertex = struct.pack('<fff', float(v.co[0]), float(v.co[1]), float(v.co[2]))
					ob_data['Vertices'].append(thisVertex)
		
		for ob_data in objects_data:
			file = open(ob_data['cache_path'], "wb")
			file.write(ob_data['headerStr'])
			
			for thisVertex in ob_data['Vertices']:
				file.write(thisVertex)
			
			file.flush()
			file.close()
			
		if action == 'mesh':
			return(True, single_cache_path)
		else:
			return(True, 'Cache Created!')
		
		
		#return(False, 'Ok!')
		

	### ********* SIMULATION *********
	
	def get_full_content_list(self, context, all_assets_data_by_name, project_name, task_data, content_data):
		content_list = {}
		
		# *** get content
		file_name = self.db_task.location_position_file
		dir_name = self.db_task.additional_folders['meta_data']
		
		#   *** FROM Shot_Animation
		path = os.path.join(task_data['asset_path'], dir_name, file_name)
		path = os.path.normpath(path)
		if not os.path.exists(path):
			return(content_list)
			
		with open(path, 'r') as f:
			jsn = json.load(f)
			
		#   *** FROM Loacation
		# -- get location asset path
		location_asset_path = None
		for key in content_data:
			if content_data[key][0]['type'] == 'location':
				location_asset_path = content_data[key][0]['path']
				
		# -- get data_file path
		data_path = False
		if location_asset_path and os.path.exists(location_asset_path):
			data_path = os.path.join(location_asset_path, dir_name, file_name)
			data_path = os.path.normpath(data_path)
			if not os.path.exists(data_path):
				data_path = False
		
		# -- get data
		if data_path:
			with open(data_path, 'r') as f:
				location_content = json.load(f)
				
			if location_content:
				for key in location_content:
					if not key in jsn:
						jsn[key] = location_content[key]
						
		#print('*** ', location_asset_path)
		#print('*** ', data_path)
		#print('*** ', json.dumps(location_content, sort_keys = 1, indent = 4))
			
		char_list = {}
		obj_list = {}
		
		for key in jsn:
			if '_proxy' in key:
				continue
			if jsn[key][4] == 'char':
				char_list[key] = {}
				char_list[key]['position'] = (jsn[key][0], jsn[key][1], jsn[key][2])
				char_list[key]['current_group'] = jsn[key][3]
				
				# get asset_data
				asset_name = key.split('.')[0]
				if asset_name in all_assets_data_by_name.keys():
					asset_data = all_assets_data_by_name[asset_name]
					
					# get din_rig publish
					result = self.db_task.get_publish_file_path(project_name, asset_data, 'din_rig')
					char_list[key]['din_rig_path'] = ''
					if result[0]:
						din_pablish_path = result[1]
						with bpy.data.libraries.load(din_pablish_path, link=False) as (data_src, data_dst):
							if jsn[key][3]:
								if (jsn[key][3] + '.din') in data_src.groups:
									char_list[key]['din_rig_path'] = din_pablish_path
					
					# get model publish
					result = self.db_task.get_publish_file_path(project_name, asset_data, 'model')
					char_list[key]['model_path'] = ''
					if result[0]:
						with bpy.data.libraries.load(result[1], link=False) as (data_src, data_dst):
							if jsn[key][3]:
								if jsn[key][3] in data_src.groups:
									char_list[key]['model_path'] = result[1]
					
			
			
			elif jsn[key][4] == 'obj':
				obj_list[key] = {}
				obj_list[key]['position'] = (jsn[key][0], jsn[key][1], jsn[key][2])
				obj_list[key]['current_group'] = jsn[key][3]
				
				# get asset_data
				asset_name = key.split('.')[0]
				if asset_name in all_assets_data_by_name.keys():
					asset_data = all_assets_data_by_name[asset_name]
					
					# get model publish
					result = self.db_task.get_publish_file_path(project_name, asset_data, 'model')
					if result[0]:
						obj_list[key]['model_path'] = result[1]
					else:
						obj_list[key]['model_path'] = ''
				
		content_list['char_list'] = char_list
		content_list['obj_list'] = obj_list
		
		return(content_list)
		
	def scene_add_copy_of_obj(self, context, data, task_data):
		for key in data:
			if key in context.scene.objects.keys():
				print(('All ready exists: ' + key))
				continue
			
			# asset name
			asset_name = key.split('.')[0]
			
			if not data[key]['model_path']:
				print(('No \"model_path\": ' + key))
				continue
				
			path = data[key]['model_path']
			current_group = data[key]['current_group']
			
			if not current_group:
				with bpy.data.libraries.load(path, link=True) as (data_src, data_dst):
					# texts
					texts = []
					for text in data_src.texts:
						if asset_name in text:
							texts.append(text)
							if text in bpy.data.texts.keys():
								bpy.data.texts.remove(bpy.data.texts[text], do_unlink=True)
					if texts:
						data_dst.texts = texts
						
					if asset_name in data_src.meshes:
						meshes = [asset_name]
						data_dst.meshes = meshes
						
					else:
						print(('No Found \"Mesh\" for: ' + key))
						continue
				
				# make ob
				me = bpy.data.meshes[asset_name]
				ob = bpy.data.objects.new(key, me)
				context.scene.objects.link(ob)
				
				# position
				ob.location = data[key]['position'][0]
				ob.rotation_euler = data[key]['position'][1]
				ob.scale = data[key]['position'][2]
				
		
		return(True, 'Ok!')
		
	def scene_add_copy_of_char(self, context, data, task_data):
		for key in data:
			if key in context.scene.objects.keys():
				print(('All ready exists: ' + key))
				continue
			
			# asset name
			asset_name = key.split('.')[0]
			
			if data[key]['din_rig_path']:
				path = data[key]['din_rig_path']
				din_group = data[key]['current_group'] + '.din'
				if not din_group in bpy.data.groups:
					with bpy.data.libraries.load(path, link=False) as (data_src, data_dst):
						# texts
						texts = []
						for text in data_src.texts:
							if asset_name in text:
								texts.append(text)
								if text in bpy.data.texts.keys():
									bpy.data.texts.remove(bpy.data.texts[text], do_unlink=True)
						if texts:
							data_dst.texts = texts
						
						# din_group
						if din_group in data_src.groups:
							data_dst.groups = [din_group]
					
					# make root ob
					root_ob = bpy.data.objects.new(key, None)
					if not root_ob.name in context.scene.objects.keys():
						context.scene.objects.link(root_ob)
					group = bpy.data.groups[din_group]
					
					# get exists armature
					armature_exists = False
					for ob in group.objects:
						# -- set use_fake_user
						ob.use_fake_user = True
						# -- arm exists
						if ob.type == 'ARMATURE':
							armature_exists = ob
							break
							
					if armature_exists:
						for ob in group.objects:
							context.scene.objects.link(ob)
							if ob.type == 'ARMATURE':
								ob.parent = root_ob
								pass
					else:
						for ob in group.objects:
							context.scene.objects.link(ob)
							ob.parent = root_ob
							
					# append Action
					if armature_exists:
						# get path
						action_name = asset_name + '.Action'
						result = self.db_task.get_final_cache_file_path(task_data, action_name, activity = 'actions', extension = '.blend')
						if result[0]:
							path = result[1]
							with bpy.data.libraries.load(path, link=False) as (data_src, data_dst):
								if action_name in data_src.actions:
									data_dst.actions = [action_name]
									
							if not armature_exists.animation_data:
								armature_exists.animation_data_create
							else:
								old_action = armature_exists.animation_data.action
								if old_action:
									old_action.name = 'removed'
									old_action.use_fake_user = False
							new_action = bpy.data.actions[action_name]
							new_action.use_fake_user = True
							armature_exists.animation_data.action = new_action
					
					# load Cache
					for ob in group.objects:
						# rename objects
						old_name = ob.name
						new_name = asset_name + '_' + old_name
						ob.name = new_name
						
						# get file path
						result = self.db_task.get_final_cache_file_path(task_data, ob.name)
						if result[0]:
							file_path = result[1]
							# import cache
							result = self.tech_anim_import_version_cache(context, ob.name, file_path, make_modifier = True)
							print(result[1])
						else:
							print(('*** No Found Cache for obj: ' + ob.name))
					
				
				else:
					root_ob = bpy.data.objects.new(key, None)
					group = bpy.data.groups[din_group]
					root_ob.dupli_group = group
					root_ob.dupli_type = 'GROUP'
					if not root_ob.name in context.scene.objects.keys():
						context.scene.objects.link(root_ob)
						
				# position
				root_ob.location = data[key]['position'][0]
				root_ob.rotation_euler = data[key]['position'][1]
				root_ob.scale = data[key]['position'][2]
				
				
			elif data[key]['model_path']:
				path = data[key]['model_path']
				current_group = data[key]['current_group']
				
				if not current_group in bpy.data.groups:
					with bpy.data.libraries.load(path, link=False) as (data_src, data_dst):
						# texts
						texts = []
						for text in data_src.texts:
							if asset_name in text:
								texts.append(text)
								if text in bpy.data.texts.keys():
									bpy.data.texts.remove(bpy.data.texts[text], do_unlink=True)
						if texts:
							data_dst.texts = texts
						
						# din_group
						if current_group in data_src.groups:
							data_dst.groups = [current_group]
							
					root_ob = bpy.data.objects.new(key, None)
					group = bpy.data.groups[current_group]
					root_ob.dupli_group = group
					root_ob.dupli_type = 'GROUP'
					if not root_ob.name in context.scene.objects.keys():
						context.scene.objects.link(root_ob)
						
					# load Cache
					for ob in group.objects:
						# rename objects
						old_name = ob.name
						new_name = asset_name + '_' + old_name
						ob.name = new_name
						
						# get file path
						result = self.db_task.get_final_cache_file_path(task_data, new_name)
						if result[0]:
							file_path = result[1]
							# import cache
							result = self.tech_anim_import_version_cache(context, new_name, file_path, make_modifier = True)
							print(result[1])
						else:
							print(('*** No Found Cache for obj: ' + ob.name))
					
				else:
					root_ob = bpy.data.objects.new(key, None)
					group = bpy.data.groups[current_group]
					root_ob.dupli_group = group
					root_ob.dupli_type = 'GROUP'
					if not root_ob.name in context.scene.objects.keys():
						context.scene.objects.link(root_ob)
						
				# position
				root_ob.location = data[key]['position'][0]
				root_ob.rotation_euler = data[key]['position'][1]
				root_ob.scale = data[key]['position'][2]
			
			else:
				return(False, 'Is Nowhere Current Group!')
		
		return(True, 'Ok!')
		
	
	def convert_instance_original(self, context, simulation_content_list, action):
		ob = context.object
		if not ob:
			return(False, 'No Selected Objects!')
		ob_name = ob.name
		
		if action == 'to_original':
			# get data
			ob_data = None
			if ob.name in simulation_content_list['char_list'].keys():
				ob_data = simulation_content_list['char_list'][ob.name]
			elif ob.name in simulation_content_list['obj_list'].keys():
				ob_data = simulation_content_list['obj_list'][ob.name]
			else:
				return(False, 'This object is not a Instance!')
			
			if ob_data['din_rig_path']:
				# group
				group = bpy.data.groups[(ob_data['current_group'] + '.din')]
				
				# exists original
				if not ob.dupli_group:
					return(False, 'This is Original!')
					
				# -- exists original
				for obj in group.objects:
					if obj.name in context.scene.objects.keys():
						return(False, 'Original Already Exists!')
				
				# remove instance object
				for scene in bpy.data.scenes:
					scene.objects.unlink(ob)
				ob.name = 'removed'
				bpy.data.objects.remove(ob, do_unlink=True)
				
				# make original
				root_ob = bpy.data.objects.new(ob_name, None)
				if not root_ob.name in context.scene.objects.keys():
					context.scene.objects.link(root_ob)
				
				for obj in group.objects:
					context.scene.objects.link(obj)
					obj.use_fake_user = True
					obj.parent = root_ob
					
				# position
				root_ob.location = ob_data['position'][0]
				root_ob.rotation_euler = ob_data['position'][1]
				root_ob.scale = ob_data['position'][2]
				
				
			elif ob_data['model_path']:
				# group
				group = bpy.data.groups[ob_data['current_group']]
				
				# exists original
				if not ob.dupli_group:
					return(False, 'This is Original!')
					
				# -- exists original
				for obj in group.objects:
					if obj.name in context.scene.objects.keys():
						return(False, 'Original Already Exists!')
				
				# remove instance object
				for scene in bpy.data.scenes:
					scene.objects.unlink(ob)
				ob.name = 'removed'
				bpy.data.objects.remove(ob, do_unlink=True)
				
				# make original
				root_ob = bpy.data.objects.new(ob_name, None)
				if not root_ob.name in context.scene.objects.keys():
					context.scene.objects.link(root_ob)
				
				for obj in group.objects:
					context.scene.objects.link(obj)
					obj.parent = root_ob
					
				# position
				root_ob.location = ob_data['position'][0]
				root_ob.rotation_euler = ob_data['position'][1]
				root_ob.scale = ob_data['position'][2]
				
			else:
				return(False, 'Epte!')
				
		elif action == 'to_instance':
			# get data
			ob_data = None
			ob_name = ob.name
			if ob.name in simulation_content_list['char_list'].keys():
				ob_data = simulation_content_list['char_list'][ob.name]
			elif ob.name in simulation_content_list['obj_list'].keys():
				ob_data = simulation_content_list['obj_list'][ob.name]
			else:
				return(False, 'This object is not a Root!')
				
			# exists instance
			if ob.dupli_group:
				return(False, 'This is Instance!')
				
			if ob_data['din_rig_path']:
				# -- unparent content
				group_name = ob_data['current_group'] + '.din'
				group = bpy.data.groups[group_name]
				for obj in group.objects:
					obj.location = (0,0,0)
					obj.rotation_euler = (0,0,0)
					obj.scale = (1,1,1)
					obj.parent = None
					obj.use_fake_user = True
					for scene in bpy.data.scenes:
						scene.objects.unlink(obj)
				
				# remove root
				for scene in bpy.data.scenes:
					scene.objects.unlink(ob)
				ob.name = 'removed'
				bpy.data.objects.remove(ob, do_unlink=True)
				
				# make instance
				root_ob = bpy.data.objects.new(ob_name, None)
				#group = bpy.data.groups[current_group]
				root_ob.dupli_group = group
				root_ob.dupli_type = 'GROUP'
				if not root_ob.name in context.scene.objects.keys():
					context.scene.objects.link(root_ob)
					
				# position
				root_ob.location = ob_data['position'][0]
				root_ob.rotation_euler = ob_data['position'][1]
				root_ob.scale = ob_data['position'][2]
			
			
			elif ob_data['model_path']:
				# remove original
				# -- unparent content
				group_name = ob_data['current_group']
				group = bpy.data.groups[group_name]
				for obj in group.objects:
					obj.location = (0,0,0)
					obj.rotation_euler = (0,0,0)
					obj.scale = (1,1,1)
					obj.parent = None
					for scene in bpy.data.scenes:
						scene.objects.unlink(obj)
				# -- remove root
				for scene in bpy.data.scenes:
					scene.objects.unlink(ob)
				ob.name = 'removed'
				bpy.data.objects.remove(ob, do_unlink=True)
				
				# make instance
				root_ob = bpy.data.objects.new(ob_name, None)
				#group = bpy.data.groups[current_group]
				root_ob.dupli_group = group
				root_ob.dupli_type = 'GROUP'
				if not root_ob.name in context.scene.objects.keys():
					context.scene.objects.link(root_ob)
					
				# position
				root_ob.location = ob_data['position'][0]
				root_ob.rotation_euler = ob_data['position'][1]
				root_ob.scale = ob_data['position'][2]
				
		
		return(True, 'Ok!')
		
	def scene_clear_of_obj(self, context, ob_data):
		for key in ob_data:
			if not key in context.scene.objects.keys():
				print(('No Found Object: ' + key))
				continue
			
			# asset name
			asset_name = key.split('.')[0]
			
			current_group = ob_data[key]['current_group']
			ob = bpy.data.objects[key]
			me = ob.data
			
			if not current_group:
				for scene in bpy.data.scenes:
					if key in scene.objects.keys():
						scene.objects.unlink(ob)
						
				me.name = 'removed'
				ob.name = 'removed'
				
				try:
					bpy.data.objects.remove(ob, do_unlink=True)
				except:
					print(('Failed to remove a: ' + key))
		
		return(True, 'Ok!')
		
	def scene_clear_of_char(self, context, ob_data):
		for key in ob_data:
			if not key in context.scene.objects.keys():
				print(('No Found Object: ' + key))
				continue
			
			# asset name
			asset_name = key.split('.')[0]
			
			if ob_data[key]['din_rig_path']:
				ob = bpy.data.objects[key]
				if ob.dupli_group:
					# remove instance object
					for scene in bpy.data.scenes:
						scene.objects.unlink(ob)
					ob.name = 'removed'
					bpy.data.objects.remove(ob, do_unlink=True)
				else:
					# remove original
					# -- unparent content
					group_name = ob_data[key]['current_group'] + '.din'  ## <<<
					group = bpy.data.groups[group_name]
					for obj in group.objects:
						obj.location = (0,0,0)
						obj.rotation_euler = (0,0,0)
						obj.scale = (1,1,1)
						obj.parent = None
						for scene in bpy.data.scenes:
							scene.objects.unlink(obj)
					# -- remove root
					for scene in bpy.data.scenes:
						scene.objects.unlink(ob)
					ob.name = 'removed'
					bpy.data.objects.remove(ob, do_unlink=True)
				
			elif ob_data[key]['model_path']:
				ob = bpy.data.objects[key]
				if ob.dupli_group:
					# remove instance object
					for scene in bpy.data.scenes:
						scene.objects.unlink(ob)
					ob.name = 'removed'
					bpy.data.objects.remove(ob, do_unlink=True)
				else:
					# remove original
					# -- unparent content
					group_name = ob_data[key]['current_group'] ## <<<
					group = bpy.data.groups[group_name]
					for obj in group.objects:
						obj.location = (0,0,0)
						obj.rotation_euler = (0,0,0)
						obj.scale = (1,1,1)
						obj.parent = None
						for scene in bpy.data.scenes:
							scene.objects.unlink(obj)
					# -- remove root
					for scene in bpy.data.scenes:
						scene.objects.unlink(ob)
					ob.name = 'removed'
					bpy.data.objects.remove(ob, do_unlink=True)
		
		
		return(True, 'Ok!')
		
	### ********* TEXTURES
	def get_textures_path(self, context, task_data):
		activity_path = os.path.normpath(os.path.join(task_data['asset_path'], self.db_task.activity_folder[task_data['asset_type']]['textures']))
		if not os.path.exists(activity_path):
			return(False, activity_path)
		
		return(True, activity_path)
	
	def open_images(self, context, application, filepath):
		
		#cmd = application +  ' \"' + filepath + '\"'
		#cmd = 'start %s \"%s\"' % (application, filepath)
		#os.system(cmd)
		
		cmd = '%s \"%s\"' % (application, filepath)
		subprocess.Popen(cmd, shell = True)
		
		return(True, 'Ok!')
	
	def pack_images(self, context, task_data, action):
		if action == 'pack':
			for img in bpy.data.images:
				if img.name in self.service_images:
					continue
				# get current path
				current_path = img.filepath_from_user()
				'''
				if os.path.splitext(current_path)[1] != '.tif':
					return(False, ('Edit Only TIFF format'))
				'''
				if img.filepath:
					img.save()
					img.pack()
					
		elif action == 'unpack':
			for img in bpy.data.images:
				if img.name in self.service_images:
					continue
				# get current path
				current_path = img.filepath_from_user()
				
				'''
				if os.path.splitext(current_path)[1] != '.tif':
					return(False, ('Edit Only TIFF format'))
				'''
				if img.packed_file:
					# file_name
					file_name = img.name.replace(' ', '_').replace(self.img_extensions[img.file_format], '') + self.img_extensions[img.file_format]
					
					# activity_path
					activity_path = os.path.normpath(os.path.join(task_data['asset_path'], self.db_task.activity_folder[task_data['asset_type']]['textures']))
					if not os.path.exists(activity_path):
						return(False, activity_path)
						
					# unpack
					img.unpack()
					img.save()
					
					# filepath
					filepath = os.path.join(activity_path, file_name)
					
					if current_path != filepath:
						shutil.copyfile(current_path, filepath)
						img.filepath = filepath
					
					# unpack
					#img.filepath = filepath
					img.reload()
					
		elif action == 'save_to_activity':
			for img in bpy.data.images:
				if img.name in self.service_images:
					continue
				
				current_path = img.filepath_from_user()
				
				'''
				if os.path.splitext(current_path)[1] != '.tif':
					return(False, ('Edit Only TIFF format'))
				'''
				
				# file_name
				file_name = img.name.replace(' ', '_').replace(self.img_extensions[img.file_format], '') + self.img_extensions[img.file_format]
				
				# activity_path
				activity_path = os.path.normpath(os.path.join(task_data['asset_path'], self.db_task.activity_folder[task_data['asset_type']]['textures']))
				if not os.path.exists(activity_path):
					os.mkdir(activity_path)
					
				# save
				if img.packed_file:
					img.unpack()
				
				try:
					img.save()
				except:
					print(img.name, '*** save trouble!!!!')
					continue
				
				# filepath
				filepath = os.path.join(activity_path, file_name)
				
				if current_path != filepath:
					shutil.copyfile(current_path, filepath)
					img.filepath = filepath
				
				img.reload()
				#img.update()
				
		elif action == 'reload':
			for img in bpy.data.images:
				img.update()
		
		return(True, 'Ok!')
		
	def convert_image_format(self, context, task_data, action):
		if action == 'tif_to_png':
			for img in bpy.data.images:
				img.reload()
				if img.name in self.service_images:
					continue
				elif not img.users:
					continue
				elif not img.filepath:
					print(img.name + ' *** No filepath!')
					continue
				elif not img.file_format in ['TIFF', 'BMP', 'TARGA', 'TARGA_RAW']:
					print(img.name + ' *** No TIFF!')
					continue
				
				# get current path
				current_path = img.filepath_from_user()
				
				# edit img name
				img.name = img.name.replace(self.img_extensions[img.file_format], '')
				
				# get png path
				activity_path = os.path.normpath(os.path.join(task_data['asset_path'], self.db_task.activity_folder[task_data['asset_type']]['textures']))
				if not os.path.exists(activity_path):
					os.mkdir(activity_path)
				file_name = img.name.replace(' ', '_').replace(self.img_extensions[img.file_format], '') + '.png'
				filepath = os.path.join(activity_path, file_name)
				
				# save
				img.save()
				
				# make png
				cmd = '\"' + self.db_task.convert_exe + '\" \"' + current_path + '\" -flatten \"' + filepath + '\"'
				try:
					#os.system(cmd)
					subprocess.Popen(cmd, shell = True)
				except:
					return(False, ('Do not Convert to .png: ' + img.name))
				
				img.filepath = filepath
				img.file_format = 'PNG'
				img.reload()
		
		elif action == 'png_to_tif':
			for img in bpy.data.images:
				img.reload()
				if img.name in self.service_images:
					continue
				elif not img.users:
					continue
				elif not img.filepath:
					print(img.name + ' *** No filepath!')
					continue
				# get current path
				current_path = img.filepath_from_user()
				if os.path.splitext(current_path)[1] != '.png':
					print(img.name + ' *** No PNG!')
					continue
				
				# edit img name
				img.name = img.name.replace(self.img_extensions[img.file_format], '')
				
				# get tif path
				activity_path = os.path.normpath(os.path.join(task_data['asset_path'], self.db_task.activity_folder[task_data['asset_type']]['textures']))
				if not os.path.exists(activity_path):
					os.mkdir(activity_path)
				file_name = img.name.replace(' ', '_').replace(self.img_extensions[img.file_format], '') + '.tif'
				filepath = os.path.join(activity_path, file_name)
				
				#if not os.path.exists(filepath):
				# save
				img.save()
				
				# make tiff
				cmd = '\"' + self.db_task.convert_exe + '\" \"' + current_path + '\"  \"' + filepath + '\"'
				try:
					#os.system(cmd)
					subprocess.Popen(cmd, shell = True)
				except:
					return(False, ('Do not Convert to .png: ' + img.name))
				
				img.filepath = filepath
				img.file_format = 'TIFF'
				img.reload()
				
		
		return(True, 'Ok!')
		
	def switch_image_format(self, context, task_data, action): # for [location, animation_shot, din_simulation, render]
		if action == 'tif_to_png':
			for img in bpy.data.images:
				img.reload()
				if img.name in self.service_images:
					continue
				elif not img.users:
					continue
				elif not img.filepath:
					print(img.name + ' *** No filepath!')
					continue
				elif not img.file_format in ['TIFF', 'BMP', 'TARGA', 'TARGA_RAW']:
					print(img.name + ' *** No TIFF!')
					continue
				
				# get current path
				current_path = img.filepath_from_user()
				
				# get png path
				activity_path = os.path.dirname(current_path)
				'''
				activity_path = os.path.normpath(os.path.join(task_data['asset_path'], self.db_task.activity_folder[task_data['asset_type']]['textures']))
				if not os.path.exists(activity_path):
					os.mkdir(activity_path)
				'''
				
				# edit img name
				img.name = img.name.replace(self.img_extensions[img.file_format], '')
				
				file_name = img.name.replace(' ', '_').replace(self.img_extensions[img.file_format], '') + '.png'
				filepath = os.path.join(activity_path, file_name)
				
				# save
				img.save()
				
				if not os.path.exists(filepath):
					# make png
					cmd = '\"' + self.db_task.convert_exe + '\" \"' + current_path + '\" -flatten \"' + filepath + '\"'
					try:
						#os.system(cmd)
						subprocess.Popen(cmd, shell = True)
					except:
						return(False, ('Do not Convert to .png: ' + img.name))
				
				img.filepath = filepath
				img.file_format = 'PNG'
				img.reload()
				img.update()
				
		elif action == 'png_to_tif':
			for img in bpy.data.images:
				img.reload()
				if img.name in self.service_images:
					continue
				elif not img.users:
					continue
				elif not img.filepath:
					print(img.name + ' *** No filepath!')
					continue
				# get current path
				current_path = img.filepath_from_user()
				if os.path.splitext(current_path)[1] != '.png':
					print(img.name + ' *** No PNG!')
					continue
				
				# get tif path
				activity_path = os.path.dirname(current_path)
				'''
				activity_path = os.path.normpath(os.path.join(task_data['asset_path'], self.db_task.activity_folder[task_data['asset_type']]['textures']))
				if not os.path.exists(activity_path):
					os.mkdir(activity_path)
				'''
				
				# edit img name
				img.name = img.name.replace(self.img_extensions[img.file_format], '')
				
				file_name = img.name.replace(' ', '_').replace(self.img_extensions[img.file_format], '') + '.tif'
				filepath = os.path.join(activity_path, file_name)
				
				'''
				# save
				img.save()
				
				if not os.path.exists(filepath):
					# make tiff
					cmd = '\"' + self.db_task.convert_exe + '\" \"' + current_path + '\"  \"' + filepath + '\"'
					try:
						#os.system(cmd)
						subprocess.Popen(cmd, shell = True)
					except:
						return(False, ('Do not Convert to .png: ' + img.name))
				'''
				if os.path.exists(filepath):
					img.filepath = filepath
					img.file_format = 'TIFF'
					img.reload()
					img.update()
				
		return(True, 'Ok!')
	
	### ********* UTILITS *************
	def current_task_text_data_block(self, context, task_data):
		current_task_text = None
		if not self.current_task_text in bpy.data.texts.keys():
			current_task_text = bpy.data.texts.new(self.current_task_text)
		else:
			current_task_text = bpy.data.texts[self.current_task_text]
			
		data = {}
		data['task_data'] = task_data
			
		current_task_text.clear()
		current_task_text.write(json.dumps(data, sort_keys=True, indent=4))
		
		return(True, 'Ok!')
	
	
	def load_char_group(self, context, char_file_path, task_data, group_name, link = True, texts = True):
		asset_name = group_name.split('.')[0]
		#
		with bpy.data.libraries.load(char_file_path, link=link) as (data_src, data_dst):
			#groups_list = []
			if texts:
				texts_list = []
				for name in data_src.texts:
					if asset_name in name:
						texts_list.append(name)
				data_dst.texts = texts_list
			
			data_dst.groups = [group_name]
			
		# create root
		if not asset_name in bpy.data.objects.keys():
			ob = bpy.data.objects.new(asset_name, None)
		else:
			ob = bpy.data.objects[asset_name]
			
		if not ob.name in context.scene.objects.keys():
			context.scene.objects.link(ob)
		
		# link objects
		group = bpy.data.groups[group_name]
		for obj in group.objects:
			# -- link obj
			old_ob_name = obj.name
			new_ob_name = asset_name + '_' + old_ob_name
			obj.name = new_ob_name
			if not obj.name in context.scene.objects.keys():
				context.scene.objects.link(obj)
			obj.parent = ob
			
			# load cache
			cache_path = self.db_task.get_final_cache_file_path(task_data, new_ob_name)
			if not cache_path[0]:
				print((asset_name + ':' + old_ob_name), ' - No Found Cache File!')
				continue
				
			# -- make constraint
			modif = obj.modifiers.new('input_cache', type = 'MESH_CACHE')
			modif.cache_format = 'PC2'
			modif.filepath = cache_path[1]
			
			# -- -- get start frame
			file = open(cache_path[1], 'rb')
			headerFormat = '<12ciiffi'
			header = unpack(headerFormat, file.read(32))
			
			#numPoints = header[13]
			startFrame = int(header[14])
			#sampleRate = header[15]
			#numSamples = header[16]
			
			modif.frame_start = startFrame
			modif.deform_mode = 'INTEGRATE'
			
	def get_group_list(self, project_name, asset_data, activity):
		# get task_data
		result = self.db_task.get_list(project_name, asset_data['id'])
		if not result[0]:
			return(False, result[1])
			
		task_data = None
		for task in result[1]:
			if task['activity'] == activity:
				task_data = task
				break
		
		asset_name = asset_data['name']
		
		# -- make link mesh
		# -- -- get publish dir
		publish_dir = os.path.join(asset_data['path'], self.db_task.publish_folder_name)
		if not os.path.exists(publish_dir):
			return(False, 'in func.location_load_exists - Not Publish Folder!')
		# -- -- get activity_dir
		activity_dir = os.path.join(publish_dir, self.db_task.activity_folder[asset_data['type']][task_data['activity']])
		if not os.path.exists(activity_dir):
			return(False, 'in func.location_load_exists - Not Publish/Activity Folder!')
		# -- -- get file_path
		file_path = os.path.join(activity_dir, (asset_name + task_data['extension']))
		if not os.path.exists(file_path):
			print(file_path)
			return(False, 'Publish/File Not Found!')
				
		with bpy.data.libraries.load(file_path, link=True) as (data_src, data_dst):
			group_list = []
			
			for name in data_src.groups:
				if asset_name in name:
					group_list.append(name)
		
		return(True, group_list, file_path)
	
	def get_input_service_task(self, project_name, task_tupl):
		# get all task list by asset
		result = self.db_task.get_list(project_name, task_tupl['task']['asset_id'])
		if not result[0]:
			return(None, result[1])
		all_tasks_list = result[1]
		all_task_data = {}
		for data in all_tasks_list:
			all_task_data[data['task_name']] = data
		
		# get input task
		input_task = task_tupl['input']
		
		while input_task['task_type'] != 'service':
			if not input_task['input']:
				#break
				return(None, 'Not Input Service Task!')
				
			input_task = all_task_data[input_task['input']]
			
		return(True, input_task)
	
	def get_shot_animation_content(self, project_name, task_data, action = 'all'):
		# get content list
		file_name = self.db_task.location_position_file
		dir_name = self.db_task.additional_folders['meta_data']
		path = os.path.join(task_data['asset_path'], dir_name, file_name)
		path = os.path.normpath(path)
		if not os.path.exists(path):
			return(False, ('Not Found ' + path + '!'))
			
		with open(path, 'r') as f:
			jsn = json.load(f)
		
		if action == 'char_assets':
			result = self.db_task.get_list_by_type(project_name, 'char')
			if not result[0]:
				return(False, result[1])
			asset_by_name_data = {}
			for data in result[1]:
				asset_by_name_data[data['name']] = data
			
			assets_list = {}
			for key in jsn:
				if jsn[key][3]:
					asset_name = jsn[key][3].split('.')[0]
					if not asset_name in assets_list:
						assets_list[asset_name] = asset_by_name_data[asset_name]
						
			return(True, assets_list)
			
		elif action == 'obj_assets':
			result = self.db_task.get_list_by_type(project_name, 'obj')
			if not result[0]:
				return(False, result[1])
			asset_by_name_data = {}
			for data in result[1]:
				asset_by_name_data[data['name']] = data
			
			assets_list = {}
			for key in jsn:
				asset_name = key.split('.')[0]
				if asset_name in asset_by_name_data:
					if not asset_name in assets_list:
						assets_list[asset_name] = asset_by_name_data[asset_name]
						
			return(True, assets_list)
					
		elif action == 'all':
			return(True, jsn)
			
	
	def get_cache_list(self, list_name, asset_name):
		text_name = asset_name
		dict_name = list_name
				
		text = None
		data = {}
		cache_objects = []
		
		if not text_name in bpy.data.texts.keys():
			return(False, 'No Found Input_Cache List!')
		else:
			text = bpy.data.texts[text_name]
			try:
				data = json.loads(text.as_string())
				cache_objects = data[dict_name]
			except:
				return(False, 'No Found Input_Cache List! *')
				
		return(True, cache_objects)
		
	### *********
	
