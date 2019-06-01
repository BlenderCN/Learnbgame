#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import platform
import json
import sqlite3
import datetime
import getpass
import random
import shutil

try:
	from .lineyka_publish import publish
except:
	from lineyka_publish import publish

class studio:
	'''
	self.set_studio(path) - 
	
	self.set_tmp_dir(path) - 
	
	self.get_studio() - 	
	'''
	def __init__(self):
		# 
		self.farme_offset = 100
		# studio
		self.studio_folder = False
		self.tmp_folder = False
		self.convert_exe = False
		self.init_path = False
		self.set_path = False
		self.share_dir = False
		self.projects_path = False  # path to .projects.db
		self.set_of_tasks_path = False  # path to .set_of_tasks.json
		self.artists_path = False # path to .artists.db
		self.workroom_path = False # path to .workroom_db
		self.statistic_path = False # path to .statistic.db
		self.list_projects = {} # a list of existing projects
		self.list_active_projects = []
		
		self.extensions = ['.blend', '.ma', '.tiff', '.ntp']
		self.setting_data = {
		'extension': {
			'.tiff':'krita',
			'.blend': 'blender',
			'.ntp': 'natron',
			'.ma': 'maya',
			'.ods':'libreoffice',
			}
		}
		
		self.publish_folder_name = 'publish'
		
		self.soft_data = None
		
		self.priority = ['normal', 'high', 'top', 'ultra']
		
		self.user_levels = ('user', 'extend_user', 'manager', 'root')
		self.manager_levels = ('manager', 'root')

		self.task_status = ('null','ready', 'ready_to_send', 'work', 'work_to_outsorce', 'pause', 'recast', 'checking', 'done', 'close')
		self.working_statuses = ('ready', 'ready_to_send', 'work', 'work_to_outsorce', 'pause', 'recast')
		self.end_statuses = ('done', 'close')
		
		self.color_status = {
		'null':(0.451000005, 0.451000005, 0.451000005),
		#'ready':(0.7627863884, 0, 1),
		'ready':(0.826, 0.249, 1),
		'ready_to_send':(0.9367088675, 0.2608556151, 0.4905878305),
		'work':(0.520749867, 0.7143493295, 0.8227847815),
		'work_to_outsorce':(0.2161512673, 0.5213058591, 0.8987341523),
		#'pause':(0.3417721391, 0.2282493114, 0.1557442695),
		'pause':(0.670, 0.539, 0.827),
		'recast':(0.8481012583, 0.1967110634, 0.1502964497),
		'checking':(1, 0.5872552395, 0.2531645298),
		'done':(0.175, 0.752, 0.113),
		#'close':(0.1645569652, 0.08450711519, 0.02499599569)
		'close':(0.613, 0.373, 0.195)
		}
		
		self.task_types = [
		# -- film
		'animatic',
		'film',
		#
		'sketch',
		'textures',
		# -- model
		'sculpt',
		'model',
		# -- rig
		'rig',
		# -- location,
		'specification',
		'location',
		#'location_full',
		#'location_for_anim',
		# -- animation
		'animation_shot',
		'tech_anim',
		'simulation_din',
		#'simulation_fluid',
		'render',
		'composition',
		]
		
		self.service_tasks = [
		'all',
		'pre',
		]
		
		self.asset_types = [
		#'animatic',
		'obj',
		'char',
		'location',
		'shot_animation',
		#'camera',
		#'shot_render',
		#'shot_composition',
		#'light',
		'film'
		]
		
		self.asset_types_with_series = [
		'animatic',
		'shot_animation',
		'camera',
		'shot_render',
		'shot_composition',
		'film'
		]
		
		self.asset_keys = [
		('name', 'text'),
		('group', 'text'),
		('path', 'text'),
		('type', 'text'),
		('series', 'text'),
		('priority', 'text'),
		('comment', 'text'),
		('content', 'text'),
		('id', 'text'),
		('status', 'text'),
		('parent', 'text') # {'name':asset_name, 'id': asset_id}
		]
		
		# constants (0 - 3 required parameters)
		self.tasks_keys = [
		('asset', 'text'),
		('activity', 'text'),
		('task_name', 'text'),
		('task_type', 'text'),
		('series', 'text'),
		('input', 'text'),
		('status', 'text'),
		('outsource', 'text'),
		('artist', 'text'),
		('planned_time', 'text'),
		('time', 'text'),
		('start', 'timestamp'),
		('end', 'timestamp'),
		('supervisor', 'text'),
		('approved_date', 'text'),
		('price', 'real'),
		('tz', 'text'),
		('chat_local', 'text'),
		('web_chat', 'text'),
		('workroom', 'text'),
		('readers', 'text'),
		('output', 'text'),
		('priority','text'),
		('asset_id', 'text'),
		('asset_type', 'text'),
		('asset_path', 'text'),
		('extension', 'text'),
		]
		
		self.workroom_keys = [
		('name', 'text'),
		('id', 'text')
		]
		
		# activity, task_name, action, date_time, comment, version, artist
		'''
		self.logs_keys = [
		('activity', 'text'),
		('task_name', 'text'),
		('action', 'text'),
		('date_time', 'timestamp'),
		('comment', 'text'),
		('version', 'text'),
		('artist', 'text')
		]
		'''
		# user_name, task_name, data_start, data_end, long_time, cost
		self.statistics_keys = [
		('project_name', 'text'),
		('task_name', 'text'),
		('data_start', 'timestamp'),
		('data_end', 'timestamp'),
		('long_time', 'text'),
		('cost', 'text'),
		('status', 'text')
		]
		# artist_name, user_name, email, phone, specialty, outsource = '' or '0'/'1'
		self.artists_keys = [
		('nik_name', 'text'),
		('user_name', 'text'),
		('password', 'text'),
		('date_time', 'timestamp'),
		('email', 'text'),
		('phone', 'text'),
		('specialty', 'text'),
		('outsource', 'text'),
		('workroom', 'text'),
		('level', 'text'),
		('share_dir', 'text'),
		('status', 'text')
		]
		self.chats_keys = [
		('date_time', 'timestamp'),
		('author', 'text'),
		('topic', 'text'),
		('color', 'text'),
		('status', 'text'),
		('reading_status', 'text')
		]
		
		self.projects_keys = [
		('name', 'text'),
		('assets_path', 'text'),
		('chat_img_path', 'text'),
		('chat_path', 'text'),
		('list_of_assets_path', 'text'),
		('path', 'text'),
		('preview_img_path', 'text'),
		('status', 'text'),
		('tasks_path', 'text'),
		]
		
		self.init_folder = '.lineyka'
		self.init_file = 'lineyka_init.json'
		self.set_file = 'user_setting.json'
		self.set_of_tasks_file = '.set_of_tasks.json'
		self.projects_file = '.projects.json'
		self.projects_db = '.projects.db'
		self.projects_t = 'projects'
		self.artists_db = '.artists.db'
		self.artists_t = 'artists'
		self.workroom_db = '.artists.db'
		self.workroom_t = 'workrooms'
		self.statistic_db = '.statistic.db'
		self.statistic_t = 'statistic'
		self.location_position_file = 'location_content_position.json'
		self.user_registr_file_name = 'user_registr.json'
		self.recycle_bin_name = '-Recycle_Bin-'
		
		# shot_animation
		self.meta_data_file = '.shot_meta_data.json'
		
		# 
		self.make_init_file()
		self.get_studio()
		
		# blender
		self.blend_service_images = {
			'preview_img_name' : 'Lineyka_Preview_Image',
			'bg_image_name' : 'Lineyka_BG_Image',
			}

	def make_init_file(self):
		home = os.path.expanduser('~')
		
		folder = os.path.normpath(os.path.join(home, self.init_folder))
		init_path = os.path.normpath(os.path.join(home, self.init_folder, self.init_file))
		set_path = os.path.normpath(os.path.join(folder, self.set_file))
		
		# make folder
		if not os.path.exists(folder):
			os.mkdir(folder)
		
		# make init_file
		if not os.path.exists(init_path):
			# make jason
			d = {'studio_folder': None, 'convert_exe': None}
			m_json = json.dumps(d, sort_keys=True, indent=4)
			# save
			data_fale = open(init_path, 'w')
			data_fale.write(m_json)
			data_fale.close()
			
		# make set_file
		if not os.path.exists(set_path):
			# make jason
			d = self.setting_data
			m_json = json.dumps(d, sort_keys=True, indent=4)
			# save
			data_fale = open(set_path, 'w')
			data_fale.write(m_json)
			data_fale.close()
			
		self.init_path = init_path
		self.set_path = set_path
		
	def set_studio(self, path):
		if not os.path.exists(path):
			return(False, "****** to studio path not Found!")
		
		home = os.path.expanduser('~')	
		init_path = os.path.join(home, self.init_folder, self.init_file).replace('\\','/')
		if not os.path.exists(init_path):
			return(False, "****** init_path not Found!")
		
		# write studio path
		try:
			with open(init_path, 'r') as read:
				data = json.load(read)
				data['studio_folder'] = path
				read.close()
		except:
			return(False, "****** in set_studio() -> init file  can not be read")

		try:
			with open(init_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, "****** in set_studio() ->  init file  can not be read")

		self.studio_folder = path
		
		# create projects_db
		projects_path = os.path.normpath(os.path.join(path, self.projects_db))
		if not os.path.exists(projects_path):
			conn = sqlite3.connect(projects_path)
			c = conn.cursor()
			conn.commit()
			conn.close()
		'''
		projects_path = os.path.join(path, self.projects_file)
		if not os.path.exists(projects_path):
			d = {}
			m_json = json.dumps(d, sort_keys=True, indent=4)
			# save
			data_fale = open(projects_path, 'w')
			data_fale.write(m_json)
			data_fale.close()
		'''
		self.projects_path = projects_path
		
		# create .set_of_tasks.json
		set_of_tasks_path = os.path.join(path, self.set_of_tasks_file)
		if not os.path.exists(set_of_tasks_path):
			d = {}
			m_json = json.dumps(d, sort_keys=True, indent=4)
			# save
			data_fale = open(set_of_tasks_path, 'w')
			data_fale.write(m_json)
			data_fale.close()
		self.set_of_tasks_path = set_of_tasks_path

		# create  artists
		artist_path = os.path.normpath(os.path.join(path, self.artists_db))
		if not os.path.exists(artist_path):
			conn = sqlite3.connect(artist_path)
			c = conn.cursor()
			'''
			names = (self.artists_t, )
			c.execute("CREATE TABLE ?(artist_name TEXT, user_name TEXT, email TEXT, phone TEXT, name TEXT, specialty TEXT)", names)
			'''
			'''
			string2 = "CREATE TABLE " + self.artists_t + " ("
			for i,key in enumerate(self.artists_keys):
				if i == 0:
					string2 = string2 + '\"' + key[0] + '\" ' + key[1]
				else:
					string2 = string2 + ', \"' + key[0] + '\" ' + key[1]
			string2 = string2 + ')'
			c.execute(string2)
			'''
			'''
			string = "CREATE TABLE " + self.artists_t + "(artist_name TEXT, user_name TEXT, email TEXT, phone TEXT, name TEXT, specialty TEXT)"
			c.execute(string)
			'''
			
			conn.commit()
			conn.close()
		self.artists_path = artist_path
		
		# create workroom
		self.workroom_path = artist_path

		# create  statistic
		statistic_path = os.path.join(path, self.statistic_db)
		if not os.path.exists(statistic_path):
			conn = sqlite3.connect(statistic_path)
			c = conn.cursor()
			'''
			names = (self.statistic_t, )
			c.execute("CREATE TABLE ?(task TEXT, user_name TEXT, data_start TEXT, data_end TEXT, long_time REAL, price REAL)", names)
			'''
			'''
			string = "CREATE TABLE " + self.statistic_t + "(task TEXT, user_name TEXT, data_start TEXT, data_end TEXT, long_time REAL, price REAL)"
			c.execute(string)
			'''
			
			conn.commit()
			conn.close()
		self.statistic_path = statistic_path
		'''		
		# fill self.extensions
		try:
			with open(self.set_path, 'r') as read:
				data = json.load(read)
				self.extensions = data['extension'].keys()
				read.close()
		except:
			print('in set_studio -> not read user_setting.json!')
			return(False, 'in set_studio -> not read user_setting.json!')
		'''	
		return(True, 'Ok')
		
	def set_tmp_dir(self, path):
		if not os.path.exists(path):
			return "****** to studio path not Found!"
		
		home = os.path.expanduser('~')	
		init_path = os.path.join(home, self.init_folder, self.init_file).replace('\\','/')
		if not os.path.exists(init_path):
			return "****** init_path not Found!"
		
		# write studio path
		try:
			with open(init_path, 'r') as read:
				data = json.load(read)
				data['tmp_folder'] = path
				read.close()
		except:
			return "****** init file  can not be read"

		try:
			with open(init_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return "****** init file  can not be read"

		self.tmp_folder = path
				
		return(True, 'Ok')
		
	def set_convert_exe_path(self, path):
		if not os.path.exists(path):
			return(False, "****** to convert.exe path not Found!")
		
		home = os.path.expanduser('~')
		init_path = os.path.join(home, self.init_folder, self.init_file).replace('\\','/')
		if not os.path.exists(init_path):
			return(False, "****** init_path not Found!")
		
		# write studio path
		try:
			with open(init_path, 'r') as read:
				data = json.load(read)
				data['convert_exe'] = os.path.normpath(path)
				read.close()
		except:
			return(False, "****** init file  can not be read")

		try:
			with open(init_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, "****** init file  can not be read")

		self.convert_exe = path
				
		return True, 'Ok'
		
	def set_share_dir(self, path):
		if not os.path.exists(path):
			return "****** to studio path not Found!"
		
		home = os.path.expanduser('~')	
		init_path = os.path.join(home, self.init_folder, self.init_file).replace('\\','/')
		if not os.path.exists(init_path):
			return "****** init_path not Found!"
		
		# write studio path
		try:
			with open(init_path, 'r') as read:
				data = json.load(read)
				data['share_folder'] = path
				read.close()
		except:
			return "****** init file  can not be read"

		try:
			with open(init_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return "****** init file  can not be read"

		#self.out_source_share_folder = path
				
		return True, 'Ok'
		
	def get_share_dir(self):
		# get lineyka_init.json
		home = os.path.expanduser('~')	
		init_path = os.path.join(home, self.init_folder, self.init_file).replace('\\','/')
		if not os.path.exists(init_path):
			return False, "****** init_path not Found!"
			
		# write studio path
		
		try:
			with open(init_path, 'r') as read:
				data = json.load(read)
				try:
					path = data['share_folder']
					self.share_dir = path
					return True, path
				except:
					return False, 'Not key \"share_folder\"'
				read.close()
		except:
			return False, '****** init file not Read!'
	
	def get_studio(self):
		if self.init_path == False:
			return(False, '****** in get_studio() -> init_path = False!')
		# write studio path
		try:
			with open(self.init_path, 'r') as read:
				data = json.load(read)
				#self.studio_folder = data['studio_folder']
				#self.tmp_folder = data['tmp_folder']
				read.close()
		except:
			return(False, "****** init file  can not be read")
		try:
			self.studio_folder = data['studio_folder']
			#print('studio: ', self.studio_folder)
		except:
			pass
		try:
			self.convert_exe = data['convert_exe']
		except:
			pass
		try:
			self.tmp_folder = data['tmp_folder']	
		except:
			pass
			
		# artists_path = False   statistic_path = False
		if self.studio_folder:
			if self.projects_path == False:
				path = os.path.normpath(os.path.join(self.studio_folder, self.projects_db))
				if os.path.exists(path):
					self.projects_path = path
			
			self.get_set_of_tasks_path()
			'''
			if not self.set_of_tasks_path:
				path = os.path.normpath(os.path.join(self.studio_folder, self.set_of_tasks_file))
				if os.path.exists(path):
					self.set_of_tasks_path = path
			'''
			if not self.artists_path:
				path = os.path.normpath(os.path.join(self.studio_folder, self.artists_db))
				if os.path.exists(path):
					self.artists_path = path
			if self.workroom_path == False:
				path = os.path.normpath(os.path.join(self.studio_folder, self.artists_db))
				if os.path.exists(path):
					self.workroom_path = path
			if self.statistic_path == False:
				path = os.path.normpath(os.path.join(self.studio_folder, self.statistic_db))
				if os.path.exists(path):
					self.statistic_path = path
					
		#print('artist path: ', self.artists_path)
		
		# get self.list_projects
		if self.projects_path:
			'''
			try:
				with open(self.projects_path, 'r') as read:
					self.list_projects = json.load(read)
					read.close()
			except:
				return False, "******studio.get_studio() -> .projects.json file  can not be read"
			'''
			self.get_list_projects()
			
		'''
		# get list_active_projects
		if self.list_projects:
			self.list_active_projects = []
			for key in self.list_projects:
				if self.list_projects[key]['status'] == 'active':
					self.list_active_projects.append(key)
		'''
				
		# fill self.extensions
		try:
			with open(self.set_path, 'r') as read:
				data = json.load(read)
				self.extensions = data['extension'].keys()
				self.soft_data = data['extension']
				read.close()
		except:
			return(False, 'in get_studio -> not read user_setting.json!')
		
		return True, [self.studio_folder, self.tmp_folder, self.projects_path, self.artists_path, self.statistic_path, self.list_projects, self.workroom_path]
		
	def get_list_projects(self):
		if not self.projects_path:
			return
		if not os.path.exists(self.projects_path):
			return
			
		# -- CONNECT  .db
		conn = sqlite3.connect(self.projects_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# -- EXISTS TABLE
		table = self.projects_t
		try:
			string = 'select * from ' + table
			c.execute(string)
		except:
			print('Not projects table!')
			pass
		
		else:
			list_projects = {}
			for row in c.fetchall():
				data = {}
				for key in dict(row).keys():
					print(key)
					if key == 'name':
						continue
					data[key] = row[key]
				list_projects[row['name']] = data
			
			self.list_projects = list_projects
		
		conn.close()
		
		# get list_active_projects
		if self.list_projects:
			self.list_active_projects = []
			for key in self.list_projects:
				if self.list_projects[key]['status'] == 'active':
					self.list_active_projects.append(key)
	
	def get_set_of_tasks_path(self):
		if not self.set_of_tasks_path:
			path = os.path.normpath(os.path.join(self.studio_folder, self.set_of_tasks_file))
			if os.path.exists(path):
				self.set_of_tasks_path = path

	# ****** SETTING ******
	# ------- EXTENSION -------------
	def get_extension_dict(self):
		extension_dict = {}
		
		home = os.path.expanduser('~')
		folder = os.path.join(home, self.init_folder)
		set_path = os.path.join(folder, self.set_file)
		
		if not os.path.exists(set_path):
			return(False, ('Not Path ' + set_path))
		
		with open(set_path, 'r') as read:
			extension_dict = json.load(read)['extension']
			
		return(True, extension_dict)
		
	def edit_extension_dict(self, key, path):
		extension_dict = {}
		
		home = os.path.expanduser('~')
		folder = os.path.join(home, self.init_folder)
		set_path = os.path.join(folder, self.set_file)
		
		if not os.path.exists(set_path):
			return(False, ('Not Path ' + set_path))
		
		with open(set_path, 'r') as read:
			data = json.load(read)
		
		data['extension'][key] = path
		
		with open(set_path, 'w') as f:
			jsn = json.dump(data, f, sort_keys=True, indent=4)
			f.close()
		
		return(True, 'Ok')
		
	def edit_extension(self, extension, action, new_extension = False):
		if not extension:
			return(False, 'Not Extension!')
			
		if not action in ['ADD', 'REMOVE', 'EDIT']:
			return(False, 'Incorrect Action!')
			
		# get file path
		home = os.path.expanduser('~')
		folder = os.path.join(home, self.init_folder)
		set_path = os.path.join(folder, self.set_file)
		
		if not os.path.exists(set_path):
			return(False, ('Not Path ' + set_path))
		
		# preparation extension
		if extension[0] != '.':
			extension = '.' + extension
			
		# read extensions
		with open(set_path, 'r') as read:
			data = json.load(read)
			
		if action == 'ADD':
			if not extension in data['extension'].keys():
				data['extension'][extension] = ''
			else:
				return(False, ('This Extension \"' + extension + '\" Already Exists!'))
		elif action == 'REMOVE':
			if extension in data['extension'].keys():
				del data['extension'][extension]
			else:
				return(False, ('This Extension \"' + extension + '\" Not Found!'))
		elif action == 'EDIT':
			if new_extension: 
				if extension in data['extension'].keys():
					value = data['extension'][extension]
					del data['extension'][extension]
					data['extension'][new_extension] = value
			else:
				return(False, 'Not New Extension!')
			
		with open(set_path, 'w') as f:
			jsn = json.dump(data, f, sort_keys=True, indent=4)
			f.close()
		
		return(True, 'Ok')
	
class project(studio):
	'''
	self.add_project(project_name, project_path, keys) - 

	self.get_project(project_name) - 
	
	'''
	def __init__(self):
		self.path = False # project folder path
		self.assets_path = False # .assets.db file path
		self.tasks_path = False # .tasks.db  file path
		self.chat_path = False # .chats.db file path
		self.list_of_assets_path = False # path to .list_of_assets.json
		self.chat_img_path = False # img to chat, folder path
		self.preview_img_path = False # preview img, folder path
		self.assets_list = False # # a list of existing assets
		self.status = False # status 
		
		# constans
		self.folders = {'assets':'assets', 'chat_img_folder':'.chat_images', 'preview_images': '.preview_images'}
		self.tasks_name_db = '.tasks.db'
		#self.assets_name = '.assets.json'
		self.assets_name = '.assets.db'
		self.chat_name_db = '.chats.db'
		self.list_of_assets_name = '.list_of_assets.json'
		#self.asset_t = 'assets'
		self.group_t = 'groups'
		self.tasks_t = 'tasks'
		self.logs_t = 'logs'
		studio.__init__(self)

	def add_project(self, project_name, project_path):
		# project_name, get project_path
		if project_path == '' and project_name == '':
			return(False, 'No options!')
			
		elif project_path == '':
			project_path = os.path.join(self.studio_folder, project_name)
			try:
				os.mkdir(project_path)
			except:
				return(False, ('Failed to create folder: ' + project_path))
			
		elif project_name == '':
			if not os.path.exists(project_path):
				return(False, ('Project Path: \'' + project_path + '\' Not Found!'))
			project_name = os.path.basename(project_path)
			
		# test by name 
		if project_name in self.list_projects.keys():
			return(False, "This project name already exists!")
		
		# path_encode
		if platform.system() == 'Windows':
			# windows
			project_path = str(project_path)
			path = os.path.normpath(project_path.encode('string-escape'))
		else:
			# linux
			path = project_path
			
		if not os.path.exists(path):
			text = '****** studio.project.add_project() -> ' +  path + ' not found'
			return False, text
		else:
			self.path = path
		
		'''
		# create assets json
		assets_path = os.path.join(path, self.assets_name)
		if not os.path.exists(assets_path):
			d = {}
			m_json = json.dumps(d, sort_keys=True, indent=4)
			# save
			data_fale = open(assets_path, 'w')
			data_fale.write(m_json)
			data_fale.close()
		self.assets_path = assets_path
		'''
		# create .list_of_assets.json
		self.list_of_assets_path = os.path.join(self.path, self.list_of_assets_name)
		if not os.path.exists(self.list_of_assets_path):
			d = {}
			m_json = json.dumps(d, sort_keys=True, indent=4)
			# save
			data_fale = open(self.list_of_assets_path, 'w')
			data_fale.write(m_json)
			data_fale.close()
		
		
		# create assets db
		self.assets_path = os.path.normpath(os.path.join(path, self.assets_name))
		if not os.path.exists(self.assets_path):
			conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			c = conn.cursor()
			'''			
			# -- table groups
			string = "CREATE TABLE " + self.group_t + "("
			for i,key in enumerate(self.group_keys):
				if i == 0:
					string = string + '\"' + key[0] + '\"' + ' ' + key[1]
				else:
					string = string + ', ' + '\"' + key[0] + '\"' + ' ' + key[1]
			string = string + ')'
			#print(string)
			c.execute(string)
			'''
			conn.commit()
			conn.close()
			
		
		# create tasks db
		self.tasks_path = os.path.join(path, self.tasks_name_db)
		if not os.path.exists(self.tasks_path):
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			c = conn.cursor()
			
			# -- table tasks
			#string = "CREATE TABLE " + self.tasks_t + "(Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, series text, task_name text, asset text, activity text, input text, status text, artist text, planned_time text, time text, start text, end text, supervisor text, approved_date text, price real, tz text, chat text)"
			#string = "CREATE TABLE " + self.tasks_t + "(Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL"
			string = "CREATE TABLE " + self.tasks_t + "("
			for i,key in enumerate(self.tasks_keys):
				if i == 0:
					string = string + key[0] + ' ' + key[1]
				else:
					string = string + ', ' + key[0] + ' ' + key[1]
			string = string + ')'
			#print(string)
			c.execute(string)
			
			# -- table logs
			string = "CREATE TABLE " + self.logs_t + "(activity text, task_name text, action text, date_time text, comment text, version text, artist text)"
			c.execute(string)
			
			conn.commit()
			conn.close()
		
		# create chat db
		self.chat_path = os.path.join(path, self.chat_name_db)
		if not os.path.exists(self.chat_path):
			conn = sqlite3.connect(self.chat_path)
			c = conn.cursor()
			
			conn.commit()
			conn.close()
			
		# create folders
		self.make_folders(self.path)
		# -- get chat_img_folder
		img_folder_path = os.path.join(self.path, self.folders['chat_img_folder'])
		if os.path.exists(img_folder_path):
			self.chat_img_path = img_folder_path
		else:
			self.chat_img_path = False
		# -- get preview_images
		preview_img_path = os.path.join(self.path, self.folders['preview_images'])	
		if os.path.exists(preview_img_path):
			self.preview_img_path = preview_img_path
		else:
			self.chat_img_path = False
		
		self.status = 'active'
		
		# create project
		# -- CREATE .projects.db
		projects_path = os.path.normpath(os.path.join(self.studio_folder, self.projects_db))
		if not os.path.exists(projects_path):
			conn = sqlite3.connect(projects_path)
			c = conn.cursor()
			conn.commit()
			conn.close()
		self.projects_path = projects_path
		
		# -- CONNECT  .db
		conn = sqlite3.connect(self.projects_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# -- EXISTS TABLE
		table = self.projects_t
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
									
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key in enumerate(self.projects_keys):
				if i == 0:
					string2 = string2 + '\"' + key[0] + '\" ' + key[1]
				else:
					string2 = string2 + ', \"' + key[0] + '\" ' + key[1]
			string2 = string2 + ')'
			c.execute(string2)
			
		# -- INSERT STRING
		string = "insert into " + table + " values"
		values = '('
		data = []
		for i, key in enumerate(self.projects_keys):
			if i< (len(self.projects_keys) - 1):
				values = values + '?, '
			else:
				values = values + '?'
			
			if key[0] == 'path':
				data.append(self.path)
			elif key[0] == 'assets_path':
				data.append(self.assets_path)
			elif key[0] == 'tasks_path':
				data.append(self.tasks_path)
			elif key[0] == 'chat_path':
				data.append(self.chat_path)
			elif key[0] == 'chat_img_path':
				data.append(self.chat_img_path)
			elif key[0] == 'preview_img_path':
				data.append(self.preview_img_path)
			elif key[0] == 'status':
				data.append(self.status)
			elif key[0] == 'list_of_assets_path':
				data.append(self.list_of_assets_path)
			elif key[0] == 'name':
				data.append(project_name)
					
		values = values + ')'
		data = tuple(data)
		string = string + values
		
		c.execute(string, data)
		#print('*'*200)
		#print(string)
		#print('*'*200)
		#print(data)
		
		conn.commit()
		conn.close()
		
		'''
		# write data
		try:
			with open(self.projects_path, 'r') as read:
				data = json.load(read)
				data[project_name] = {
				'path' : self.path,
				'assets_path' : self.assets_path,
				'tasks_path' : self.tasks_path,
				'chat_path' : self.chat_path,
				'chat_img_path' : self.chat_img_path,
				'preview_img_path' : self.preview_img_path,
				'status' : self.status,
				'list_of_assets_path' : self.list_of_assets_path
				} 
				read.close()
								
		except:
			return False, "****** studio.add_project -> .projects.json  can not be read"

		try:
			with open(self.projects_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return False, "****** studio.add_project -> .projects.json  can not be write"
		'''
		
		# create_recycle_bin
		result = group().create_recycle_bin(project_name)
		if not result[0]:
			return(False, result[1])
		
		return True, 'ok'
		
	def get_project(self, name):
		self.get_list_projects()
		
		if not name in self.list_projects.keys():
			return(False, "This project Not Found!")
		else:
			self.path = self.list_projects[name]['path']
			self.assets_path = self.list_projects[name]['assets_path']
			self.list_of_assets_path = self.list_projects[name]['list_of_assets_path']
			self.tasks_path = self.list_projects[name]['tasks_path']
			self.chat_path = self.list_projects[name]['chat_path']
			self.chat_img_path = self.list_projects[name]['chat_img_path']
			self.preview_img_path = self.list_projects[name]['preview_img_path']
			self.status = self.list_projects[name]['status']
				
		self.get_list_of_assets()
		return(True, (self.list_projects[name], self.assets_list))
		
	def get_list_of_assets(self):
		# self.assets_list - list of dictonary by self.asset_keys
		self.assets_list = []
		return(True, 'Ok')
	
	def rename_project(self, old_name, new_name):
		if not old_name in self.list_projects:
			return(False, ('in rename_project -> No such project: \"' + old_name + '\"'))
			
		result = self.get_project(old_name)
		if not result[0]:
			return(False, ('in rename_project -> ' + result[1]))
		
		'''
		try:
			with open(self.projects_path, 'r') as read:
				data = json.load(read)
				project_data = data[old_name]
				del data[old_name]
				data[new_name] = project_data
				read.close()
				
		except:
			return(False, 'Not Read \".projects.json\"!')
			
		try:
			with open(self.projects_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, 'Not Write \".projects.json\"!')
		'''
		
		# -- CONNECT  .db
		conn = sqlite3.connect(self.projects_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		table = self.projects_t
		string = 'UPDATE ' +  table + ' SET \"name\" = ? WHERE name = ?'
		data = (new_name, old_name)
		
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		return(True, 'Ok')
		
	def remove_project(self, name):
		if not name in self.list_projects:
			return(False, ('No such project: \"' + name + '\"'))
			
		result = self.get_project(name)
		if not result[0]:
			return(False, result[1])
			
		'''
		try:
			with open(self.projects_path, 'r') as read:
				data = json.load(read)
				del data[name]
				read.close()
		except:
			return(False, 'Not Read \".projects.json\"!')
			
		try:
			with open(self.projects_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, 'Not Write \".projects.json\"!')
		'''
		
		# -- CONNECT  .db
		conn = sqlite3.connect(self.projects_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		table = self.projects_t
		string = 'DELETE FROM ' +  table + ' WHERE name = ?'
		data = (name,)
		
		c.execute(string, data)
		conn.commit()
		conn.close()
			
		return(True, 'Ok')
		
	def edit_status(self, name, status):
		if not name in self.list_projects:
			return(False, ('in edit_status -> No such project: \"' + name + '\"'))
			
		result = self.get_project(name)
		if not result[0]:
			return(False, ('in edit_status -> ' + result[1]))
		
		'''
		try:
			with open(self.projects_path, 'r') as read:
				data = json.load(read)
				data[name]['status'] = status
				read.close()
		except:
			return(False, 'Not Read \".projects.json\"!')
			
		try:
			with open(self.projects_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, 'Not Write \".projects.json\"!')
		'''
		
		# -- CONNECT  .db
		conn = sqlite3.connect(self.projects_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		table = self.projects_t
		string = 'UPDATE ' +  table + ' SET \"status\" = ? WHERE name = ?'
		data = (status, name)
		
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		return(True, 'Ok')
		
	def make_folders(self, root):
		for f in self.folders:
			path = os.path.join(root, self.folders[f])
			if not os.path.exists(path):
				os.mkdir(path)
				#print '\n****** Created'
			else:
				return False, '\n****** studio.project.make_folders -> No Created'
	
class asset(project):
	'''
	studio.project.asset()
	
	self.activity_folder  - {activity_name : activity_folder, ... }
	
	add_asset(project_name, asset_name) - create folder: assets/asset_name; create activity folders assets/asset_name/...folders; write {asset_name:folder_full_path} in .assets.json; 
	
	get_asset(project_name, asset_name) - return ful path to asset_folder or False, fill self.task_list
	
	get_activity_path(project_name, asset_name, activity) - return full path of activity folder, or create activity folder, or return False
	
	get_final_file_path(project_name, asset_name, activity) - return full path to file of final version activity, or False
	
	get_new_file_path(project_name, asset_name, activity) - return 	new_dir_path, new_file_path, or False
	
	'''
	
	def __init__(self):
		self.asset_path = False # full path to asset folder
		self.asset_name = False
		self.activity_path = False
		self.task_list = False # task lists from this asset
		self.asset_group = False # the group of asset
		self.asset_type = False
		
		# constants
		#self.extension = '.ma'
		self.activity_folder = {
		#'animatic' : {
		'film':{
		'storyboard':'storyboard',
		'specification':'specification',
		'animatic':'animatic',
		'film':'film'
		},
		'obj':{
		'sketch':'sketch',
		'sculpt':'sculpt',
		'model':'03_model',
		'textures':'05_textures'
		},
		'char':{
		'sketch':'sketch',
		'face_blend':'10_face_blend',
		'sculpt':'sculpt',
		'model':'03_model',
		'rig':'08_rig',
		#'rig_face':'09_rig_face',
		#'rig_face_crowd':'09_rig_face_crowd',
		#'rig_hik':'08_rig_hik',
		#'rig_hik_face':'09_ri_hik_face',
		#'rig_low':'08_rig_low',
		'def_rig':'def_rig',
		'din_rig':'din_rig',
		'textures':'05_textures',
		'cache':'cache',
		},
		'location' : {
		'sketch':'sketch',
		'specification':'specification',
		'location_anim':'location_anim',
		'location':'location'
		},
		'shot_animation' : {
			'animatic':'animatic',
			'shot_animation':'shot_animation',
			'camera':'camera',
			'pleyblast_sequence':'pleyblast_sequence',
			'tech_anim': 'tech_anim',
			'simulation_din':'simulation_din',
			'render':'render',
			'composition':'composition',
			'cache':'cache',
			'actions':'actions',
			#'din_simulation':'din_simulation',
			#'fluid_simulation':'fluid_simulation',
		},
		'camera' : {'camera':'camera'},
		'shot_render' : {'shot_render':'shot_render'},
		'shot_composition' : {'shot_composition':'shot_composition'},
		'light' : {'light':'light'},
		#'film' : {'film':'film'},
		}
		
		self.additional_folders = {
		'meta_data':'00_common',
		}
		
		self.unchangeable_keys = ['id', 'type', 'path']
		#self.copied_asset = ['obj', 'char']
		self.copied_asset = {
			'obj':['obj', 'char'],
			'char':['char', 'obj']
			}
		self.copied_with_task = ['obj', 'char']
		
		# objects
		self.db_group = group()
		
		project.__init__(self)
		
	def add_asset(self, project_name, type_, group, asset_name, asset_path = ''):
		# group - clear name
		#
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		self.asset_name = asset_name.replace(' ', '_')
		self.asset_type = type_
		self.asset_group = group
		
		# create asset folder
		if asset_path == '':
			self.asset_path = os.path.join(self.path, self.folders['assets'],self.asset_group, self.asset_name)
			# create group folder
			group_dir = os.path.join(self.path, self.folders['assets'],self.asset_group)
			if not os.path.exists(group_dir):
				try:
					os.mkdir(group_dir)
				except:
					return False, '**** studio/project/asset.add_asset -> you can not create a folder \'assets/group\''
			# create root folder
			if not os.path.exists(self.asset_path):
				try:
					os.mkdir(self.asset_path)
				except:
					return False, '**** studio/project/asset.add_asset -> you can not create a folder \'assets/group/asset\''
		else:
			if os.path.exists(asset_path):
				self.asset_path = asset_path
			else:
				return False, '**** studio/project/asset.add_asset -> asset_path not found!'
					
		# create activity folders
		for activity in self.activity_folder:
			folder_path = os.path.join(self.asset_path, self.activity_folder[activity])
			if not os.path.exists(folder_path):
				os.mkdir(folder_path)
				
		# create additional folders  self.additional_folders
		for activity in self.additional_folders:
			folder_path = os.path.join(self.asset_path, self.additional_folders[activity])
			if not os.path.exists(folder_path):
				os.mkdir(folder_path)
		
		# write data in .assets.json // self.assets_path
		try:
			with open(self.assets_path, 'r') as read:
				data = json.load(read)
				data[self.asset_name] = [self.asset_group, self.asset_path, self.asset_type]
				read.close()
		except:
			return False, "****** studio.project.asset.add_asset -> .assets.json  can not be read"

		try:
			with open(self.assets_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
				return True, 'ok'
		except:
			return False, "****** studio.project.asset.add_asset -> .assets.json  can not be write"
			
	def get_asset(self, project_name, asset_name):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		with open(self.assets_path, 'r') as read:
			data = json.load(read)
			read.close()
			#if data[asset_name]:
			try:
				self.asset_type = data[asset_name][2]
				self.asset_group = data[asset_name][0]
				self.asset_path = data[asset_name][1]
				self.asset_name = asset_name
				
				# get tasks_list
				conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
				conn.row_factory = sqlite3.Row
				c = conn.cursor()
				table = '\"' + self.asset_name + ':' + self.tasks_t + '\"'
				string = 'select * from ' + table
				try:
					c.execute(string)
				except:
					self.task_list = []
					#print string
				else:
					rows = c.fetchall()
					conn.close()
					if len(rows) > 0:
						self.task_list = []
						for row in rows:
							self.task_list.append(row['task_name'])
									
				#return
				return self.asset_group, self.asset_path, self.task_list
			except:
				return False, 'Not Asset!'
				
	def get_activity_path(self, project_name, asset_name, activity):
		if not self.get_asset(project_name, asset_name)[0]:
			return False, '***'
		try:
			activity_folder = self.activity_folder[activity]
		except:
			return False, '****'
		activity_path = os.path.join(self.asset_path, activity_folder)
		if not os.path.exists(activity_path):
			try:
				os.mkdir(activity_path)
			except:
				return False, '*****'
		self.activity_path = activity_path
		return self.activity_path
	'''
	def get_final_file_path(self, project_name, asset_name, activity):
		activity_folder = self.get_activity_path(project_name, asset_name, activity)
		if not activity_folder[0]:
			return None
		# - get folder list
		folders_16 = os.listdir(activity_folder)
		folders = []
		
		if len(folders_16)==0:
			return None
		
		# - 16 to 10
		for obj_ in folders_16:
			folders.append(int(obj_, 16))
		
		# - sort/max
		folders.sort(reverse = True)
		max = folders[0]
		
		for obj_ in folders_16:
			if int(obj_, 16) == max:
				final_file = os.path.join(activity_folder, obj_, (asset_name + self.extension))
		if os.path.exists(final_file):
			return final_file
		else:
			return False
	
			
	def get_new_file_path(self, project_name, asset_name, activity):
		final_file = self.get_final_file_path(project_name, asset_name, activity)
		if not final_file:
			if final_file == None:
				new_dir_path = os.path.join(self.activity_path, '0000')
				new_file_path = os.path.join(new_dir_path, (asset_name + self.extension))
			else:
				return False
		else:
			ff_split = final_file.replace('\\','/').split('/')
			new_num_dec = int(ff_split[len(ff_split) - 2], 16) + 1
			new_num_hex = hex(new_num_dec).replace('0x', '')
			if len(new_num_hex)<4:
				for i in range(0, (4 - len(new_num_hex))):
					new_num_hex = '0' + new_num_hex
			new_dir_path = os.path.join(self.activity_path, new_num_hex)
			new_file_path = os.path.join(new_dir_path, (asset_name + self.extension))
				 
		return new_dir_path, new_file_path
	'''
	
	# **************** ASSET NEW  METODS ******************
	
	def create(self, project_name, asset_type, list_keys):  # create list assets from list asset_keys
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		result = self.get_list_by_all_types(project_name)
		'''
		print('*****', result)
		return(False, 'Epte!')
		'''
		assets = []
		ids = []
		if result[0]:
			for row in result[1]:
				assets.append(row['name'])
				ids.append(row['id'])
			
		# test asset_type
		if not asset_type in self.asset_types:
			return(False, 'Asset_Type is Not Valid!')
			
		# 
		tasks_of_assets = {}
		
		# -- CONNECT  .db
		try:
			# write group to db
			conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, 'Not .db connect!')
			
		# -- EXISTS TABLE
		table = asset_type
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
									
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key in enumerate(self.asset_keys):
				if i == 0:
					string2 = string2 + '\"' + key[0] + '\" ' + key[1]
				else:
					string2 = string2 + ', \"' + key[0] + '\" ' + key[1]
			string2 = string2 + ')'
			c.execute(string2)	
			
			
		# -- CREATE ASSETS
		make_assets = {}
		for keys in list_keys:
			# test name
			if (not 'name' in keys) or (keys['name'] == ''):
				conn.close()
				return(False,('not name!'))
				
			elif (not 'group' in keys) or (keys['group'] == ''):
				conn.close()
				return(False, ('\"' + keys['name'] + '\" not group'))
				
			# edit name
			if asset_type in ['shot_animation']:
				keys['name'] = keys['name'].replace(' ', '_')
			else:
				keys['name'] = keys['name'].replace(' ', '_').replace('.', '_')
				
			#while keys['name'] in assets:
			if keys['name'] in assets:
				#keys['name'] = keys['name'] + '01'
				conn.close()
				return(False, ('Name ' + '\"' + keys['name'] + '\" already exists!'))
		
			keys['name'] = keys['name'].replace(' ','_')
			keys['type'] = asset_type
			keys['status'] = 'active'
			
			if asset_type in self.asset_types_with_series and not keys['series']:
				conn.close()
				return(False, ('\"' + keys['name'] + '\" not series'))
		
			# get id			
			keys['id'] = str(random.randint(0, 1000000000))
			while keys['id'] in ids:
				keys['id'] = str(random.randint(0, 1000000000))
				
			# get priority
			if (not 'priority' in keys) or (keys['priority'] == ''):
				keys['priority'] = '0'
			
			# -- make folders
			asset_path = ''
			if not 'path' in keys.keys():
				keys['path'] = ''
			if keys['path'] == '':
				asset_path = os.path.join(self.path, self.folders['assets'],asset_type, keys['name'])
				# create group folder
				group_dir = os.path.join(self.path, self.folders['assets'],asset_type)
				if not os.path.exists(group_dir):
					try:
						os.mkdir(group_dir)
					except:
						conn.close()
						return(False, '**** studio/project/asset.create -> you can not create a folder \'assets/asset_type\'')
				# create root folder
				if not os.path.exists(asset_path):
					try:
						os.mkdir(asset_path)
					except:
						conn.close()
						return(False, '**** studio/project/asset.create -> you can not create a folder \'assets/asset_type/asset\'')
				#keys['path'] = asset_path
				
			else:
				if os.path.exists(keys['path']):
					asset_path = keys['path']
				else:
					conn.close()
					return(False, '**** studio/project/asset.create -> asset_path not found!')
			
			keys['path'] = asset_path
			
			# -- create activity folders
			for activity in self.activity_folder[asset_type]:
				folder_path = os.path.join(asset_path, self.activity_folder[asset_type][activity])
				if not os.path.exists(folder_path):
					os.mkdir(folder_path)
					
			# -- create additional folders  self.additional_folders
			for activity in self.additional_folders:
				folder_path = os.path.join(asset_path, self.additional_folders[activity])
				if not os.path.exists(folder_path):
					os.mkdir(folder_path)
		
			# create string
			string = "insert into " + table + " values"
			values = '('
			data = []
			for i, key in enumerate(self.asset_keys):
				if i< (len(self.asset_keys) - 1):
					values = values + '?, '
				else:
					values = values + '?'
				if key[0] in keys:
					data.append(keys[key[0]])
				else:
					if key[1] == 'real':
						data.append(0.0)
					elif key[1] == 'timestamp':
						data.append(datetime.datetime.now())
					else:
						data.append('')
						
			values = values + ')'
			data = tuple(data)
			string = string + values
			
			# add asset
			#print('\n', string, data)
			c.execute(string, data)
			
			# -------------------------- Make Tasks Data------------------------------ set_of_tasks
			
			# add service tasks ("final")
			final = {
				'asset':keys['name'],
				'asset_id': keys['id'],
				'asset_type': asset_type,
				'task_name': (keys['name'] + ':final'),
				'series': keys['series'],
				'status':'null',
				'task_type':'service',
			}
			
			this_asset_tasks = []
			# create service tasks ("all_input")
			all_input = {
				'asset':keys['name'],
				'asset_id': keys['id'],
				'asset_type': asset_type,
				'task_name': (keys['name'] + ':all_input'),
				'series': keys['series'],
				'status':'done',
				'task_type':'service',
				'input':'',
				#'output': json.dumps([final['task_name']])
				'output': '',
			}
			this_asset_tasks.append(all_input)
			
			# get list from set_of_tasks
			result = set_of_tasks().get(keys['set_of_tasks'])
			if result[0]:
				set_tasks = result[1]['sets']
				
				outputs = {}
				for task_ in set_tasks:
					# name
					name = task_['task_name']
					task_['task_name'] = keys['name'] + ':' + name
					
					# output
					task_['output'] = json.dumps([final['task_name']])
					
					# input
					input_ = task_['input']
					if  input_ == 'all':
						task_['input'] = all_input['task_name']
						# status
						task_['status'] = 'ready'
						# add to output all_input
						all_outputs = json.loads(all_input['output'])
						all_outputs.append(task_['task_name'])
						all_input['output'] = json.dumps(all_outputs)
						
					elif input_ == 'pre':
						task_['input'] = keys['name'] + ':pre_input:' + name
						# status
						task_['status'] = 'ready'
						# add service tasks ("pre_input" )
						pre_input = {
							'asset':keys['name'],
							'asset_id': keys['id'],
							'asset_type': asset_type,
							'task_name': task_['input'],
							'series': keys['series'],
							'status':'done',
							'task_type':'service',
							'input':'',
							#'output': json.dumps([final['task_name'], task_['task_name']])
							'output': json.dumps([task_['task_name']])
						}
						this_asset_tasks.append(pre_input)
					elif input_:
						task_['input'] = keys['name'] + ':' + input_
						# status
						task_['status'] = 'null'
						
						# outputs
						if task_['input'] in outputs.keys():
							outputs[task_['input']].append(task_['task_name'])
						else:
							outputs[task_['input']] = [task_['task_name'],]
						
						'''
						# outputs
						try:
							outputs[task_['input']].append(task_['task_name'])
						except:
							outputs[task_['input']] = task_['task_name']
						'''
						
					else:
						# status
						task_['status'] = 'ready'
						
					# price
					task_['price'] = task_['cost']
						
					# asset
					task_['asset'] = keys['name']
					task_['asset_id'] = keys['id']
					task_['asset_type'] = asset_type
					
					# series
					task_['series'] = keys['series']
					
					# readers
					task_['readers'] = "{}"
					
					# append task
					this_asset_tasks.append(task_)
					
				for task_ in this_asset_tasks:
					if task_['task_name'] in outputs:
						if task_['output']:
							task_outputs = json.loads(task_['output'])
							#task_outputs.append(outputs[task_['task_name']])
							task_outputs = task_outputs + outputs[task_['task_name']]
							task_['output'] = json.dumps(task_outputs)
						else:
							task_['output'] = json.dumps(outputs['task_name'])
			
			# set input of "final"
			final_input = []
			for task_ in this_asset_tasks:
				final_input.append(task_['task_name'])
			final['input'] = json.dumps(final_input)
			
			# append final to task list
			this_asset_tasks.append(final)
			
			# make tasks to asset
			copy = task()
			#result = copy.create_tasks_from_list(project_name, keys['name'], keys['id'], this_asset_tasks)
			result = copy.create_tasks_from_list(project_name, keys, this_asset_tasks)
			if not result[0]:
				conn.close()
				return(False, result[1])
			
			# append to tasks_of_assets {asset: tasks_list, ... }
			tasks_of_assets[keys['name']] = this_asset_tasks
			
			# make return data
			make_assets[keys['name']] = keys
		
		# CLOSE .db
		conn.commit()
		conn.close()
		
		'''
		# send to tasks create  # tasks_of_assets /home/renderberg/create_tasks.json
		with open('/home/renderberg/create_tasks.json', 'w') as f:
		#with open('C:/Users/vladimir/Documents/blender_area/create_tasks.json', 'w') as f:
			jsn = json.dump(tasks_of_assets, f, sort_keys=True, indent=4)
			f.close()
		'''
		
		return(True, make_assets)
		
	def remove_asset(self, project_name, asset_data):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# ******* TO RECICLE BIN
		# -- get recycle bin  data
		result = self.db_group.get_by_keys(project_name, {'type': 'all'})
		if not result[0]:
			return(False, ('in asset().remove_asset' + result[1]))
		recycle_bin_data = result[1][0]
		
		# -- edit  .db
		try:
			conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, 'in asset()remove_asset - Not .db connect!')
		
		table = asset_data['type']
		string = 'UPDATE ' +  table + ' SET \"group\" = ?, priority = ? WHERE id = ?'
		data = (recycle_bin_data['id'], '0', asset_data['id'])
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		# ******** DISCONNECT ARTISTS, READERS
		output_tasks = []
		output_tasks_name_list = []
		# Connect to db
		try:
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, 'in asset()remove_asset - Not .db connect!')
		# get tasks rows
		table = '\"' + asset_data['id'] + ':' + self.tasks_t + '\"'
		string = 'select * from ' + table
		c.execute(string)
		for row in c.fetchall():
			if not row['output']:
				print('*'*250, row['task_name'])
				continue
			for task_name in json.loads(row['output']):
				if task_name.split(':')[0] != row['asset']:
					output_tasks.append((row, task_name))
					output_tasks_name_list.append(task_name)
			if row['task_type'] == 'service':
				continue
			# -- -- get status
			new_status = 'null'
			if not row['input']:
				new_status = 'ready'
			# -- -- update .db
			string = 'UPDATE ' +  table + ' SET artist = ?, readers = ?, status = ? WHERE task_name = ?'
			data = ('', json.dumps([]),new_status, row['task_name'])
			c.execute(string, data)
			
		conn.commit()
		conn.close()
		
		# ******** DISCONNECT OUTPUTS
		# -- get output tasks dict
		result = task().get_tasks_data_by_name_list(project_name, output_tasks_name_list)
		if not result[0]:
			return(False, ('in asset().remove_asset -' + result[1]))
		output_tasks_data_dict = result[1]
		
		for key in output_tasks:
			if not key[1]:
				continue
			if output_tasks_data_dict[key[1]]['task_type'] == 'service':
				result = task().service_remove_task_from_input(project_name, output_tasks_data_dict[key[1]], [key[0]])
			else:
				print((output_tasks_data_dict[key[1]]['task_name'] + ' not service!'))
				continue
		
		return(True, 'Ok!')
	
	def copy_of_asset(self, project_name, new_group_name, new_asset_name, new_asset_type, set_of_tasks, data_of_source_asset):
		# edit name
		if new_asset_type in ['shot_animation']:
			new_asset_name = new_asset_name.replace(' ', '_')
		else:
			new_asset_name = new_asset_name.replace(' ', '_').replace('.', '_')
		
		
		# get group id
		result = self.db_group.get_by_name(project_name, new_group_name)
		if not result[0]:
			return(False, result[1])
		new_group_id = result[1]['id']
		
		# get list_keys
		old_path = data_of_source_asset['path']
		old_name = data_of_source_asset['name']
		old_type = data_of_source_asset['type']
		data_of_source_asset['set_of_tasks'] = set_of_tasks
		data_of_source_asset['type'] = new_asset_type
		data_of_source_asset['group'] = new_group_id
		data_of_source_asset['name'] = new_asset_name
		data_of_source_asset['path'] = ''
		
		list_keys = [data_of_source_asset]
		
		print(json.dumps(list_keys, sort_keys = True, indent = 4))
		
		# make asset
		result = self.create(project_name, new_asset_type, list_keys)
		if not result[0]:
			return(False, result[1])
			
		# copy activity files
		# -- copy meta data
		new_asset_data = result[1][new_asset_name]
		for key in self.additional_folders:
			src_activity_path = os.path.join(old_path, self.additional_folders[key])
			dst_activity_path = os.path.join(new_asset_data['path'], self.additional_folders[key])
			for obj in os.listdir(src_activity_path):
				src = os.path.join(src_activity_path, obj)
				dst = os.path.join(dst_activity_path, obj.replace(old_name, new_asset_name)) # + replace name 
				if os.path.isfile(src):
					shutil.copyfile(src, dst)
				elif os.path.isdir(src):
					shutil.copytree(src, dst)
		
		# -- copy activity version
		old_activites = self.activity_folder[old_type]
		activites = self.activity_folder[new_asset_type]
		for key in activites:
			# -- get activity dir
			if not key in old_activites:
				continue
			src_activity_dir = os.path.normpath(os.path.join(old_path, old_activites[key]))
			
			if not os.path.exists(src_activity_dir):
				continue
			
			versions = os.listdir(src_activity_dir)
			if not versions:
				continue
			
			# exceptions ['textures','cache']
			numbers = []
			int_hex = {}
			
			if key == 'textures' or (key == 'cache' and new_asset_type == 'char'):
				src_activity_path = src_activity_dir
				dst_activity_path = os.path.normpath(os.path.join(new_asset_data['path'], activites[key]))
				if not os.path.exists(dst_activity_path):
					os.mkdir(dst_activity_path)
				
			else:
				#numbers = []
				#int_hex = {}
				for version in versions:
					num = int(version, 16)
					numbers.append(num)
					int_hex[str(num)] = version
				
				# -- -- get version contents
				while not os.listdir(os.path.join(src_activity_dir, int_hex[str(max(numbers))])):
					numbers.remove(max(numbers))
				
				src_activity_path = os.path.normpath(os.path.join(old_path, old_activites[key], int_hex[str(max(numbers))]))
				dst_activity_path = os.path.normpath(os.path.join(new_asset_data['path'], activites[key], '0000'))
				
				# -- -- make new dirs
				if not os.path.exists(os.path.normpath(os.path.join(new_asset_data['path'], activites[key]))):
					os.mkdir(os.path.normpath(os.path.join(new_asset_data['path'], activites[key])))
				if not os.path.exists(dst_activity_path):
					os.mkdir(dst_activity_path)
			
			# -- -- copy content
			for obj in os.listdir(src_activity_path):
				src = os.path.normpath(os.path.join(src_activity_path, obj))
				dst = os.path.normpath(os.path.join(dst_activity_path, obj.replace(old_name, new_asset_name)))
				if os.path.isfile(src):
					shutil.copyfile(src, dst)
					#print(int_hex[str(max(numbers))], obj)
				elif os.path.isdir(src):
					shutil.copytree(src, dst)
					#print(int_hex[str(max(numbers))], obj)
		
		# copy preview image
		img_folder_path = os.path.normpath(os.path.join(self.path, self.folders['preview_images']))
		old_img_path = os.path.normpath(os.path.join(img_folder_path, (old_name + '.png')))
		old_img_icon_path = os.path.normpath(os.path.join(img_folder_path, (old_name + '_icon.png')))
		new_img_path = os.path.normpath(os.path.join(img_folder_path, (new_asset_name + '.png')))
		new_img_icon_path = os.path.normpath(os.path.join(img_folder_path, (new_asset_name + '_icon.png')))
		
		if os.path.exists(old_img_path):
			shutil.copyfile(old_img_path, new_img_path)
		if os.path.exists(old_img_icon_path):
			shutil.copyfile(old_img_icon_path, new_img_icon_path)
		
		return(True, 'Ok!')
	
	def get_list_by_type(self, project_name, asset_type):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# write series to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		try:
			table = asset_type
			str_ = 'select * from ' + table
			c.execute(str_)
			rows = c.fetchall()
			conn.close()
			return(True, rows)
		except:
			conn.close()
			return(True, [])
			
	def get_list_by_all_types(self, project_name):
		# get project
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# write series to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		assets_list = []
		for asset_type in self.asset_types:
			try:
				table = asset_type
				str_ = 'select * from ' + table
				c.execute(str_)
				rows = c.fetchall()
				for row in rows:
					assets_list.append(row)
			except:
				#print(('not found table from type: \" ' + asset_type + ' \"'))
				continue
		conn.close()
		return(True, assets_list)
	'''		
	def get_list_by_group(self, project_name, group_name):		
		# get group_type
		group_type = None
		copy = group()
		group_data = copy.get_by_name(project_name, group_name)
		if group_data[0]:
			group_type = group_data[1]['type']
		else:
			return(False, group_data[1])
		
		# get list by type
		list_by_type = self.get_list_by_type(project_name, group_type)
		if not list_by_type[0]:
			return(False, list_by_type[1])
				
		# get list by group
		list_by_group = []
		for row in list_by_type[1]:
			if row['group'] == group_name:
				list_by_group.append(row)
				
		return(True, list_by_group)
	'''
		
	def get_list_by_group(self, project_name, group_id):
		# get group_type
		group_type = None
		copy = group()
		group_data = copy.get_by_id(project_name, group_id)
		if group_data[0]:
			group_type = group_data[1]['type']
		else:
			return(False, group_data[1])
		
		all_list = []
		if group_type == 'all':
			list_by_type = self.get_list_by_all_types(project_name)
			if not list_by_type[0]:
				return(False, list_by_type[1])
			all_list = list_by_type[1]
		
		else:
			# get asset list by type
			list_by_type = self.get_list_by_type(project_name, group_type)
			if not list_by_type[0]:
				return(False, list_by_type[1])
			all_list = list_by_type[1]
		
		# get list by group
		list_by_group = []
		for row in all_list:
			if row['group'] == group_id:
				list_by_group.append(row)
				
		return(True, list_by_group)
	
	def get_name_list_by_type(self, project_name, asset_type):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# write series to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		try:
			table = asset_type
			str_ = 'select * from ' + table
			c.execute(str_)
			rows = c.fetchall()
			names = []
			for row in rows:
				names.append(row['name'])
			conn.close()
			return(True, rows)
		except:
			conn.close()
			return(True, [])
			
			
	def get_id_name_dict_by_type(self, project_name, asset_type):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# write series to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		try:
			table = asset_type
			str_ = 'select * from ' + table
			c.execute(str_)
			rows = c.fetchall()
			asset_id_name_dict = {}
			for row in rows:
				asset_id_name_dict[row['id']] = row['name']
			conn.close()
			return(True, asset_id_name_dict)
		except:
			conn.close()
			return(True, [])
			
	def get_name_data_dict_by_all_types(self, project_name):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# write series to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# get assets_list
		assets_list = []
		for asset_type in self.asset_types:
			try:
				table = asset_type
				str_ = 'select * from ' + table
				c.execute(str_)
				rows = c.fetchall()
				for row in rows:
					assets_list.append(row)
			except:
				#print(('in get_name_id_dict_by_all_types - not found table from type: \" ' + asset_type + ' \"'))
				continue
			
		# make dict
		assets_dict = {}
		for asset in assets_list:
			assets_dict[asset['name']] = asset
		
		conn.close()
		return(True, assets_dict)
			
	def get_by_name(self, project_name, asset_type, asset_name):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# write series to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		try:
			table = asset_type
			str_ = 'select * from ' + table + ' where \"name\" = ?'
			c.execute(str_, (asset_name,))
			row = c.fetchone()
			conn.close()
			return(True, row)
		except:
			conn.close()
			return(False, 'Not Asset With This Name!')
			
	
	def get_by_id(self, project_name, asset_type, asset_id):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# write series to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		try:
			table = asset_type
			str_ = 'select * from ' + table + ' where \"id\" = ?'
			c.execute(str_, (asset_id,))
			row = c.fetchone()
			conn.close()
			return(True, row)
		except:
			conn.close()
			return(False, 'Not Asset With This Name!')
			
	def edit_asset_data_by_name(self, project_name, keys): # required keys: 'name', 'type', unchangeable keys: 'type', 'id', 'path'
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# test Name Type
		if not 'name' in keys:
			return(False, 'Not Name!')
		elif not 'type' in keys:
			return(False, 'Not Type!')
			
		# write series to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# test table
		try:
			table = keys['type']
			com = 'select * from ' + table
			c.execute(com)
		except:
			conn.close()
			return(False, 'Not Asset With This Type!')
		
		# edit db
		data = []
		string = 'UPDATE ' +  table + ' SET '
		for key in keys:
			if not key in self.unchangeable_keys:
				string = string + ' \"' + key + '\" = ? ,'
				data.append(keys[key])
		# -- >>
		string = string + ' WHERE \"name\" = \"' + keys['name'] + '\"'
		string = string.replace(', WHERE', ' WHERE')
		
		c.execute(string, data)
		conn.commit()
		conn.close()
		return(True, 'Ok!')
		
	def edit_asset_data_by_id(self, project_name, keys): # required keys: 'id', 'type', unchangeable keys: 'type', 'id', 'path'
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# test Name Type
		if not 'id' in keys:
			return(False, 'Not id!')
		elif not 'type' in keys:
			return(False, 'Not Type!')
			
		# write series to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# test table
		try:
			table = keys['type']
			com = 'select * from ' + table
			c.execute(com)
						
			if 'name' in keys:
				rows = c.fetchall()
				for row in rows:
					if row['name'] == keys['name']:
						return(False, 'Overlap Name!')
			
		except:
			conn.close()
			return(False, 'Not Asset With This Type!')
			
		# edit db
		data = []
		string = 'UPDATE ' +  table + ' SET '
		for key in keys:
			if not key in self.unchangeable_keys:
				string = string + ' \"' + key + '\" = ? ,'
				data.append(keys[key])
		# -- >>
		string = string + ' WHERE \"id\" = \"' + keys['id'] + '\"'
		string = string.replace(', WHERE', ' WHERE')
		
		c.execute(string, data)
		conn.commit()
		conn.close()
		return(True, 'Ok!')
		
	def change_group_of_asset(self, project_name, asset_type, asset_name, new_group_id):
		keys = {
		'name': asset_name,
		'type': asset_type,
		'group': new_group_id,
		}
		
		result = self.edit_asset_data_by_name(project_name, keys)
		if not result[0]:
			return(False, result[1])
		else:
			return(True, 'Ok!')
			
	def rename_asset(self, project_name, asset_type, old_name, new_name):
		# get id by name
		result = self.get_by_name(project_name, asset_type, old_name)
		if not result[0]:
			return(False, result[1])
		
		# rename
		keys = {
		'name': new_name,
		'type': asset_type,
		'id': result[1]['id'],
		}
		
		result = self.edit_asset_data_by_id(project_name, keys)
		if not result[0]:
			return(False, result[1])
		else:
			return(True, 'Ok!')
			
	
	
class task(asset):
	'''
	studio.project.asset.task()
	
	KEYS (series text, task_name text, asset text, activity text, input text, status text, artist text, planned_time text, time text, start text, end text, supervisor text, approved_date text, price real, tz text, chat text)
	
	self.add_task(project_name, asset_name, {key:data, ...}) - add task in .tasks.db;; return: 'ok' - all right; False - ather errors; 'overlap' - the task has not been created, this task name already exists; 'not_project' - not project;  'not_asset' - ... ; 'required' - lacking data (first three values)
	
	self.edit_task(project_name, asset_name, {key:data, ...}) - edit data in .tasks.db;; return: 'ok' - all right, False - ather errors; 'not_project' - not project;  'not_asset' - ...
	
	self.read_task(project_name, task_name, [keys]) - return data (True/False, {key: data, ...}/error) ;; error: (not_project, not_task_name) 
	
	self.edit_status_to_output(project_name, task_name) - (run from edit_task() on status change for 'ready') ;; changes the status of the all outgoing tasks from 'null' to 'ready';; return (True/False, 'ok'/'ather comment')
		
	'''
	
	def __init__(self):
		self.variable_statuses = ('ready', 'ready_to_send', 'work', 'work_to_outsorce')
		
		self.change_by_outsource_statuses = {
		'to_outsource':{'ready':'ready_to_send', 'work':'ready_to_send'},
		'to_studio':{'ready_to_send':'ready', 'work_to_outsorce':'ready'},
		}
		
		self.db_workroom = workroom()
		#self.publish = lineyka_publish.publish()
		
		self.publish = publish(self)
		
		asset.__init__(self)
		
	# ************************ CHANGE STATUS ******************************** start
	
	@staticmethod
	def _input_to_end(task_data):
		if task_data['status'] == 'close':
			return(False)
		
		autsource = bool(int(task_data['outsource']))
				
		if autsource:
			return('ready_to_send')
		else:
			return('ready')
	
	def service_input_to_end(self, task_data, assets):
		new_status = False
		
		# get input_list
		input_list = json.loads(task_data['input'])
		if not input_list:
			return(True, new_status)
		
		# get status
		bool_statuses = []
		# --------------- fill end_statuses -------------
		
		# ****** connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		for task_name in input_list:
			try:
				asset_id = assets[task_name.split(':')[0]]['id']
			except:
				print(('in from_service_remove_input_tasks incorrect key: ' + task_name.split(':')[0] + ' in ' + task_name))
				continue
			
			table = '\"' + asset_id + ':' + self.tasks_t + '\"'
			
			string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
			try:
				c.execute(string)
				task_data = c.fetchone()
			except:
				conn.close()
				return(False, ('in from_service_remove_input_tasks can not read ', string))
				
			if task_data['status'] in self.end_statuses:
				bool_statuses.append(True)
			else:
				bool_statuses.append(False)
		
		conn.close()
		
		if False in bool_statuses:
			new_status = 'null'
		else:
			new_status = 'done'
			#self.this_change_to_end(self, project_name, task_data)
			
		return(True, new_status)
	
	def from_input_status(self, task_data, input_task_data):  # input_task_data = row{self.task_keys} or False
		# get task_outsource
		task_outsource = bool(int(task_data['outsource']))
		
		new_status = None
		# change status
		if input_task_data:
			if input_task_data['status'] in self.end_statuses:
				if not task_outsource:
					if task_data['status'] == 'null':
						new_status = 'ready'
				else:
					if task_data['status'] == 'null':
						new_status = 'ready_to_send'
			else:
				if task_data['status'] != 'close':
					new_status = 'null'
		else:
			if not task_data['status'] in self.end_statuses:
				if task_outsource:
					new_status = 'ready_to_send'
				else:
					new_status = 'ready'
		return(new_status)
		
	def this_change_from_end(self, project_name, task_data, assets = False): # ???
		# 
		from_end_list = []
		this_asset_type = task_data['asset_type']
		
		# ******* get output task list
		output_list = []
		try:
			output_list = json.loads(task_data['output'])
		except:
			pass
		
		if not output_list:
			return(True, 'Ok!')
		
		if not assets:
			# get assets dict
			result = self.get_name_data_dict_by_all_types(project_name)
			if not result[0]:
				return(False, result[1])
			assets = result[1]
		
		# ****** connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# ****** change status
		for task_name in output_list:
			try:
				asset_id = assets[task_name.split(':')[0]]['id']
			except:
				print(('in this_change_from_end incorrect key ' + task_name.split(':')[0] + ' in ' + task_name))
				continue
			table = '\"' + asset_id + ':' + self.tasks_t + '\"'
			
			string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
			try:
				c.execute(string)
				task_data = c.fetchone()
			except:
				conn.close()
				return(False, ('in this_change_from_end can not read ', string))
				#return(False, string)
				
			if task_data['status'] == 'close':
				continue
			elif task_data['asset_type'] == 'location' and this_asset_type != 'location':
				continue
			elif task_data['status'] == 'done':
				from_end_list.append(task_data)
				
			new_status = 'null'
			
			# edit readers
			readers = {}
			try:
				readers = json.loads(task_data['readers'])
			except:
				pass
			if readers:
				for key in readers:
					readers[key] = 0
				string = 'UPDATE ' +  table + ' SET  readers = ?, status  = ? WHERE task_name = ?'
				data = (json.dumps(readers), new_status, task_name)
			else:
				string = 'UPDATE ' +  table + ' SET  status  = ? WHERE task_name = ?'
				data = (new_status, task_name)
				
			c.execute(string, data)
	
		conn.commit()
		conn.close()
		
		# ****** edit from_end_list
		if from_end_list:
			for t_d in from_end_list:
				self.this_change_from_end(project_name, t_d)
		
		
		return(True, 'Ok!')
		
	def this_change_to_end(self, project_name, task_data, assets = False):
		# ******* get output task list
		output_list = []
		try:
			output_list = json.loads(task_data['output'])
		except:
			pass
		
		if not output_list:
			return(True, 'Ok!')
			
		# get assets dict
		if not assets:
			result = self.get_name_data_dict_by_all_types(project_name)
			if not result[0]:
				return(False, result[1])
			assets = result[1]
		
		# ****** connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		service_to_done = []
		# ****** change status
		for task_name in output_list:
			try:
				asset_id = assets[task_name.split(':')[0]]['id']
			except:
				print(('in this_change_to_end incorrect key: ' + task_name.split(':')[0] + ' in ' + task_name))
				continue
			table = '\"' + asset_id + ':' + self.tasks_t + '\"'
			
			string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
			try:
				c.execute(string)
				task_data_ = c.fetchone()
			except:
				conn.close()
				return(False, ('in this_change_to_end can not read ', string))
							
			# get new status
			if task_data_['task_type'] == 'service':
				result = self.service_input_to_end(task_data_, assets)
				if not result[0]:
					return(False, result[1])
				new_status = result[1]
				if new_status == 'done':
					service_to_done.append(task_data_)
			else:
				new_status = self._input_to_end(task_data_)
				
			if not new_status:
				continue
			
			string = 'UPDATE ' +  table + ' SET  status  = ? WHERE task_name = ?'
			data = (new_status, task_name)
			c.execute(string, data)
			
		conn.commit()
		conn.close()
		
		if service_to_done:
			for task in service_to_done:
				self.this_change_to_end(project_name, task, assets = assets)
		
		return(True, 'Ok!')
	'''	
	def from_service_remove_input_tasks(self, project_name, task_data, removed_tasks_list):
		# get input_list
		input_list = json.loads(task_data['input'])
		for task in removed_tasks_list:
			input_list.remove(task['task_name'])
			
		if not input_list:
			return(True, 'done')
			
		# get assets dict
		result = self.get_name_data_dict_by_all_types(project_name)
		if not result[0]:
			return(False, result[1])
		assets = result[1]
		
		bool_statuses = []
		# --------------- fill end_statuses -------------
		
		# ****** connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		for task_name in input_list:
			try:
				asset_id = assets[task_name.split(':')[0]]['id']
			except:
				print(('in from_service_remove_input_tasks incorrect key: ' + task_name.split(':')[0] + ' in ' + task_name))
				continue
			
			table = '\"' + asset_id + ':' + self.tasks_t + '\"'
			
			string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
			try:
				c.execute(string)
				task_data = c.fetchone()
			except:
				conn.close()
				return(False, ('in from_service_remove_input_tasks can not read ', string))
				
			if task_data['status'] in self.end_statuses:
				bool_statuses.append(True)
			else:
				bool_statuses.append(False)
		
		conn.close()
		
		if False in bool_statuses:
			new_status = 'null'
		else:
			new_status = 'done'
			
		return(True, new_status)
	'''
	# **************************** Task() File Path ************************************************
	
	def get_final_file_path(self, project_name, task_data):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		asset_path = task_data['asset_path']
		'''
		# *************** get asset path *******
		# write series to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		table = task_data['asset_type']
		asset_path = None
		
		# get path
		try:			
			com = 'select * from ' + table + ' WHERE id = ?'
			data = (task_data['asset_id'],)
			c.execute(com, data)
			row = c.fetchone()
			asset_path = row['path']
		except:
			conn.close()
			return(False, 'Not Asset With This Type!')
		
		
		if not asset_path:
			return(False, 'Not Asset Path!')
		'''
		
		folder_name = self.activity_folder[task_data['asset_type']][task_data['activity']]
		activity_path = os.path.normpath(os.path.join(asset_path, folder_name))
		
		if not os.path.exists(activity_path):
			try:
				os.mkdir(activity_path)
			except:
				print(activity_path)
				return(False, 'in task().get_final_file_path() Can not create activity dir!')
		
		# - get folder list
		folders_16 = os.listdir(activity_path)
		folders = []
		
		if len(folders_16)==0:
			return(True, None, asset_path)
		
		# - 16 to 10
		for obj_ in folders_16:
			folders.append(int(obj_, 16))
		'''
		for obj_ in folders_16:
			if int(obj_, 16) == max(folders):
				final_file = os.path.join(activity_path, obj_, (task_data['asset'] + task_data['extension']))
				break
		if os.path.exists(final_file):
			return(True, final_file, asset_path)
		else:
			return(True, None, asset_path)
		'''
		i = max(folders)
		while i > -1:
			hex_ = hex(i).replace('0x', '')
			num = 4 - len(hex_)
			hex_num = '0'*num + hex_
			
			final_file = os.path.join(activity_path, hex_num, (task_data['asset'] + task_data['extension']))
			if os.path.exists(final_file):
				return(True, final_file, asset_path)
			i = i-1
		
		return(True, None, asset_path)
		
	
	def get_version_file_path(self, project_name, task_data, version):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		asset_path = task_data['asset_path']
		'''
		# *************** get asset path *******
		# write series to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		table = task_data['asset_type']
		asset_path = None
		
		# get path
		try:			
			com = 'select * from ' + table + ' WHERE id = ?'
			data = (task_data['asset_id'],)
			c.execute(com, data)
			row = c.fetchone()
			asset_path = row['path']
		except:
			conn.close()
			return(False, 'Not Asset With This Type!')
		
		
		if not asset_path:
			return(False, 'Not Asset Path!')
		'''
		
		folder_name = self.activity_folder[task_data['asset_type']][task_data['activity']]
		activity_path = os.path.normpath(os.path.join(asset_path, folder_name))
		
		version_file = os.path.join(activity_path, version, (task_data['asset'] + task_data['extension']))
		
		if os.path.exists(version_file):
			return(True, version_file)
		else:
			return(False, 'Not Exists File!')
			
	def get_new_file_path(self, project_name, task_data):
		# get final file
		result = self.get_final_file_path(project_name, task_data)
		#final_file = None
		if not result[0]:
			return(False, result[1])
			
		final_file = result[1]		
		asset_path = result[2]
		
		# get activity path
		folder_name = self.activity_folder[task_data['asset_type']][task_data['activity']]
		activity_path = os.path.normpath(os.path.join(asset_path, folder_name))
		# make activity folder
		if not os.path.exists(activity_path):
			os.mkdir(activity_path)
		
		if final_file == None:
			new_dir_path = os.path.join(activity_path, '0000')
			new_file_path = os.path.join(new_dir_path, (task_data['asset'] + task_data['extension']))
			
		else:
			ff_split = final_file.replace('\\','/').split('/')
			new_num_dec = int(ff_split[len(ff_split) - 2], 16) + 1
			new_num_hex = hex(new_num_dec).replace('0x', '')
			if len(new_num_hex)<4:
				for i in range(0, (4 - len(new_num_hex))):
					new_num_hex = '0' + new_num_hex
			
			new_dir_path = os.path.join(activity_path, new_num_hex)
			new_file_path = os.path.join(new_dir_path, (task_data['asset'] + task_data['extension']))
		
		'''
		# make version dir
		if not os.path.exists(new_dir_path):
			os.mkdir(new_dir_path)
		'''
				 
		return(True, (new_dir_path, new_file_path))
		
	def get_publish_file_path(self, project_name, asset_data, activity):
		# get task_data
		result = self.get_list(project_name, asset_data['id'])
		if not result[0]:
			return(False, result[1])
			
		task_data = None
		for task in result[1]:
			if task['activity'] == activity:
				task_data = task
				break
				
		if not task_data:
			return(False, 'No Found Task with this activity!')
		
		# -- -- get publish dir
		publish_dir = os.path.join(asset_data['path'], self.publish_folder_name)
		if not os.path.exists(publish_dir):
			return(False, 'in func.location_load_exists - Not Publish Folder!')
		# -- -- get activity_dir
		activity_dir = os.path.join(publish_dir, self.activity_folder[asset_data['type']][task_data['activity']])
		if not os.path.exists(activity_dir):
			return(False, 'in func.location_load_exists - Not Publish/Activity Folder!')
		# -- -- get file_path
		file_path = os.path.join(activity_dir, (asset_data['name'] + task_data['extension']))
		if not os.path.exists(file_path):
			print(file_path)
			return(False, 'Publish/File Not Found!')
			
		return(True, file_path)
		
	
	# **************************** CACHE  ( file path ) ****************************
	def get_versions_list_of_cache_by_object(self, task_data, ob_name, activity = 'cache', extension = '.pc2'):
		asset_path = task_data['asset_path']
		
		folder_name = self.activity_folder[task_data['asset_type']][activity]
		activity_path = os.path.normpath(os.path.join(asset_path, folder_name))
		activity_path = os.path.normpath(activity_path)
		cache_dir_path = os.path.normpath(os.path.join(asset_path, folder_name, ob_name))
		
		if not os.path.exists(cache_dir_path):
			return(False, 'No Found Cache Directory!')
			
		# - get folders list
		folders_16 = os.listdir(cache_dir_path)
		dec_nums = []
		tech_anim_cache_versions_list = []
		
		if not folders_16:
			return(False, 'No Found Cache Versions!')
			
		for num in folders_16:
			dec_nums.append(int(num, 16))
			
		dec_nums.sort()
		
		for i in dec_nums:
			number = None
			for num in folders_16:
				if i == int(num, 16):
					number = num
					break
			path = os.path.join(cache_dir_path, number, (ob_name + extension))
			path = os.path.normpath(path)
			if number:
				if os.path.exists(path):
					tech_anim_cache_versions_list.append((str(i), ob_name, path))
				else:
					continue
				
		if tech_anim_cache_versions_list:
			return(True, tech_anim_cache_versions_list)
		else:
			return(False, 'No Found Cache Versions! *')
		
	
	def get_final_cache_file_path(self, task_data, cache_dir_name, activity = 'cache', extension = '.pc2'):
		asset_path = task_data['asset_path']
		
		folder_name = self.activity_folder[task_data['asset_type']][activity]
		activity_path = os.path.normpath(os.path.join(asset_path, folder_name))
		activity_path = os.path.normpath(activity_path)
		cache_dir_path = os.path.normpath(os.path.join(asset_path, folder_name, cache_dir_name))
		cache_dir_path = os.path.normpath(cache_dir_path)
		
		#print(cache_dir_path)
		
		if not os.path.exists(activity_path):
			os.mkdir(activity_path)
		if not os.path.exists(cache_dir_path):
			os.mkdir(cache_dir_path)
		
		# - get folder list
		folders_16 = os.listdir(cache_dir_path)
		folders = []
		
		if len(folders_16)==0:
			return(False, 'No Found Chache! *1')
		
		# - 16 to 10
		for obj_ in folders_16:
			folders.append(int(obj_, 16))
		
		i = max(folders)
		while i > -1:
			hex_ = hex(i).replace('0x', '')
			num = 4 - len(hex_)
			hex_num = '0'*num + hex_
			
			final_file = os.path.join(cache_dir_path, hex_num, (cache_dir_name + extension))
			if os.path.exists(final_file):
				return(True, final_file)
			i = i-1
		
		return(False, 'No Found Chache! *2')
		
	def get_new_cache_file_path(self, project_name, task_data, cache_dir_name, activity = 'cache', extension = '.pc2'):
		# get final file
		result = self.get_final_cache_file_path(task_data, cache_dir_name, activity = activity, extension = extension)
		#final_file = None
		if not result[0]:
			if result[1] == 'No Found Chache! *1' or result[1] == 'No Found Chache! *2':
				final_file = None
			else:
				return(False, result[1])
		else:
			final_file = result[1]
		asset_path = task_data['asset_path']
		
		# get activity path
		folder_name = self.activity_folder[task_data['asset_type']][activity]
		activity_path = os.path.normpath(os.path.join(asset_path, folder_name, cache_dir_name))
		
		# make activity folder
		if not os.path.exists(activity_path):
			os.mkdir(activity_path)
		
		if final_file == None:
			new_dir_path = os.path.join(activity_path, '0000')
			new_file_path = os.path.join(new_dir_path, (cache_dir_name + extension))
			
		else:
			ff_split = final_file.replace('\\','/').split('/')
			new_num_dec = int(ff_split[len(ff_split) - 2], 16) + 1
			new_num_hex = hex(new_num_dec).replace('0x', '')
			if len(new_num_hex)<4:
				for i in range(0, (4 - len(new_num_hex))):
					new_num_hex = '0' + new_num_hex
			
			new_dir_path = os.path.join(activity_path, new_num_hex)
			new_file_path = os.path.join(new_dir_path, (cache_dir_name + extension))
		
		
		# make version dir
		if not os.path.exists(new_dir_path):
			os.mkdir(new_dir_path)
		
				 
		return(True, (new_dir_path, new_file_path))
		
	def get_version_cache_file_path(self, project_name, task_data, version, cache_dir_name, activity = 'cache', extension = '.pc2'):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		asset_path = task_data['asset_path']
		
		folder_name = self.activity_folder[task_data['asset_type']][activity]
		activity_path = os.path.normpath(os.path.join(asset_path, folder_name, cache_dir_name))
		
		version_file = os.path.join(activity_path, version, (cache_dir_name + extension))
		
		if os.path.exists(version_file):
			return(True, version_file)
		else:
			return(False, 'Not Exists File!')
		
	# ************************ CHANGE STATUS ******************************** end
		
	def add_task(self, project_name, task_key_data):
		# other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# test exists ASSET  self.assets_list
		asset_name = task_key_data['asset']
		if not asset_name in self.assets_list:
			# self.print_log('')
			return False, 'not_asset'
			
		# test required parameters
		for i in range(0, 3):
			try:
				data = task_key_data[self.tasks_keys[i][0]]
			except:
				return False, 'required'
		#########		
		# get Autsource status
		# -- get artist
		outsource = None
		artist_name = task_key_data['artist']
		if artist_name:
			artist_data = artist().read_artist({'nik_name':artist_name})
			if artist_data[0]:
				if artist_data[1][0]['outsource'] == '1':
					outsource = True
		#########
				
		# set STATUS
		try:
			if task_key_data['input'] == '':
				######
				if outsource:
					task_key_data['status'] = "ready_to_send"
				else:
					task_key_data['status'] = "ready"
				######
			else:
				input_task_data = self.read_task(project_name, task_key_data['input'], ('status',))
				if input_task_data[0]:
					if input_task_data[1]['status'] == 'done':
						######
						if outsource:
							task_key_data['status'] = "ready_to_send"
						else:
							task_key_data['status'] = "ready"
						######
					else:
						task_key_data['status'] = "null"
				else:
					#'not_task_name'
					task_key_data['status'] = "null"
		except:
			######
			if outsource:
				task_key_data['status'] = "ready_to_send"
			else:
				task_key_data['status'] = "ready"
			######
				
		#
		table = '\"' + asset_name + ':' + self.tasks_t + '\"'
		string = "insert into " + table + " values"
		values = '('
		data = []
		for i, key in enumerate(self.tasks_keys):
			if i< (len(self.tasks_keys) - 1):
				values = values + '?, '
			else:
				values = values + '?'
			if key[0] in task_key_data:
				data.append(task_key_data[key[0]])
			else:
				if key[1] == 'real':
					data.append(0.0)
				elif key[1] == 'timestamp':
					data.append(None)
				else:
					data.append('')
					
		values = values + ')'
		data = tuple(data)
		string = string + values
		
		# write task to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# exists table
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			# unicum task_name test
			r = c.fetchall()
			for row in r:
				if row['task_name'] == task_key_data['task_name']:
					conn.close()
					return False, 'overlap'
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key in enumerate(self.tasks_keys):
				if i == 0:
					string2 = string2 + key[0] + ' ' + key[1]
				else:
					string2 = string2 + ', ' + key[0] + ' ' + key[1]
			string2 = string2 + ')'
			#print(string2)
			c.execute(string2)
		
		# add task
		c.execute(string, data)
		conn.commit()
		conn.close()
		return True, 'ok'
	
	def edit_task(self, project_name, task_key_data):
		# other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# test exists ASSET  asset
		asset_name = task_key_data['task_name'].split(':')[0]
		if not asset_name in self.assets_list:
			# self.print_log('')
			return False, 'not_asset'
		
		# test task_name
		try:
			task_name = (task_key_data['task_name'],)
		except:
			return False, 'not task_name'
			
		######     ==  COONNECT DATA BASE
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		table = '\"' + asset_name + ':' + self.tasks_t + '\"'
			
		######     == get current data
		command =  'SELECT * FROM ' + table + ' WHERE task_name = ?'
		c.execute(command, task_name)
		current_task_data = c.fetchone()
		#print('***** current name: ', current_task_data['artist'], 'new name:', task_key_data['artist'])
		
		#conn.close()
		#return
		######
			
		#########	 == get Autsource Status	
		# -- get artist
		outsource = None
		artist_name = None
		try:
			artist_name = task_key_data['artist']
		except:
			artist_name = current_task_data['artist']
		if artist_name:
			artist_data = artist().read_artist({'nik_name':artist_name})
			if artist_data[0]:
				if artist_data[1][0]['outsource'] == '1':
					outsource = True
		#########
		
		#########   == get Input Status
		input_status = None
		input_task_name = ''
		try:
			input_task_name = task_key_data['input']
		except:
			input_task_name = current_task_data['input']
		input_task_data = self.read_task(project_name, input_task_name, ['status'])
		if input_task_data[0]:
			input_status = input_task_data[1]['status']
		elif not input_task_data[0] and input_task_data[1] == 'not_task_name':
			input_status = 'done'
			
		
		######### self.working_statuses self.end_statuses
		
		# CHANGE STATUS
		try:
			task_key_data['status']
		except:
			pass
		else:
			if not (input_status in self.end_statuses):
				task_key_data['status'] = "null"
			elif task_key_data['status'] == "ready" and outsource:
				task_key_data['status'] = "ready_to_send"
			elif task_key_data['status'] == "work" and outsource:
				task_key_data['status'] = "work_to_outsorce"
			elif task_key_data['status'] == "work_to_outsorce" and not outsource:
				task_key_data['status'] = "work"
			elif task_key_data['status'] == "null" and (input_status in self.end_statuses) and outsource:
				task_key_data['status'] = "ready_to_send"
			elif task_key_data['status'] == "null" and (input_status in self.end_statuses) and (not outsource):
				task_key_data['status'] = "ready"
			# SET OUTPUT STATUS
			elif task_key_data['status'] in self.end_statuses:
				#print('w'*25, task_key_data['status'])
				self.edit_status_to_output(project_name, task_key_data['task_name'])
			
			if (current_task_data['status'] in self.end_statuses) and (task_key_data['status'] not in self.end_statuses):
				self.edit_status_to_output(project_name, task_key_data['task_name'], new_status = task_key_data['status'])
			
		# write task to db
		'''
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		c = conn.cursor()
		table = '\"' + asset_name + ':' + self.tasks_t + '\"'
		'''
		# edit db
		data_from_input_task = (False,)
		string = 'UPDATE ' +  table + ' SET '
		for key in task_key_data:
			if not key == 'task_name' or key == 'asset' or key == 'sctivity':
				if key == 'price':
					string = string + ' ' + key + ' = ' + str(task_key_data[key]) + ','
				else:
					if task_key_data[key] == None:
						string = string + ' ' + key + ' = null,'
					else:
						string = string + ' ' + key + ' = \"' + task_key_data[key] + '\",'
				'''
				elif key == 'status' and task_key_data['status'] == 'done':
					######
					continue
					self.edit_status_to_output(project_name, task_key_data['task_name'])
					string = string + ' ' + key + ' = \"' + task_key_data[key] + '\",'
				elif key == 'input':
					######
					continue
					data_from_input_task = self.read_task(project_name, task_key_data['input'], ('status',))
					string = string + ' ' + key + ' = \"' + task_key_data[key] + '\",'
				
				else:
					if task_key_data[key] == None:
						string = string + ' ' + key + ' = null,'
					else:
						string = string + ' ' + key + ' = \"' + task_key_data[key] + '\",'
				'''		
		######   == exchange key 'status'	from exchange input task
		'''
		if data_from_input_task[0]:
			if (data_from_input_task[1]['status'] == 'done') and (this_status == 'null'):
				string = string + ' status = \"ready\",'
			elif data_from_input_task[1]['status'] != 'done':
				string = string + ' status = \"null\",'
		'''
		######
		
		# -- >>
		string = string + ' WHERE task_name = \"' + task_key_data['task_name'] + '\"'
		string = string.replace(', WHERE', ' WHERE')
		#print(string)
		
		c.execute(string)
		conn.commit()
		conn.close()
		
		return(True, 'ok')
	
	def edit_status_to_output(self, project_name, task_name, new_status = None):
		asset_name = task_name.split(':')[0]
		table = '\"' + asset_name + ':' + self.tasks_t + '\"'
		data = (task_name,)
		string = 'SELECT * FROM ' + table + ' WHERE input = ?'
		
		try:
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		except:
			return(False, 'studio.project.asset.task.edit_status_to_output() -> the database can not be read!')
				
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		c.execute(string, data)
		rows = c.fetchall()
		
		for row in rows:
			#print row['task_name']
			# get artist_status
			'''
			if int(artist().read_artist({'nik_name':row['artist']})[1][0]['outsource']):
				print '###########################################', row['artist']
			'''
			if not new_status:
				if row['status'] == 'null':
					if artist().read_artist({'nik_name':row['artist']})[1][0]['outsource'] == '1':
						string2 = 'UPDATE ' +  table + ' SET status = \"ready_to_send\" WHERE task_name = \"' + row['task_name'] + '\"'
					else:	
						string2 = 'UPDATE ' +  table + ' SET status = \"ready\" WHERE task_name = \"' + row['task_name'] + '\"'
					c.execute(string2)
			elif new_status not in self.end_statuses and row['status'] != 'close':
				string2 = 'UPDATE ' +  table + ' SET status = \"null\" WHERE task_name = \"' + row['task_name'] + '\"'
				c.execute(string2)
			
		conn.commit()
		conn.close()
		
		return True, 'ok'
	'''
	def read_task(self, project_name, task_name, keys):
		if keys == 'all':
			new_keys = []
			for key in self.tasks_keys:
				new_keys.append(key[0])
			keys = new_keys
			
		# other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# read tasks
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		asset_name = task_name.split(':')[0]
		table = '\"' + asset_name + ':' + self.tasks_t + '\"'
		string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
		
		try:
			c.execute(string)
			row = c.fetchone()
		except:
			conn.close()
			#return(False, ('can_not_read_asset', string))
			return(False, string)
		conn.close()
		
		if not row:
			return(False, 'not_task_name')
				
		data = {}
		for key in keys:
			data[key] = row[key]
			
		return(True, data)
	'''
		
	'''	
	def change_status_by_open_task(self, project_name, task_name, artist):
		self.edit_task(self, project_name, {'task_name': task_name, 'status': 'work'})
	'''
	
	
	# **************** Task NEW  METODS ******************
	
	def create_tasks_from_list(self, project_name, asset_data, list_of_tasks):
		asset_name = asset_data['name']
		asset_id = asset_data['id']
		asset_path = asset_data['path']
		# Other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + asset_id + ':' + self.tasks_t + '\"'
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key in enumerate(self.tasks_keys):
				if i == 0:
					string2 = string2 + key[0] + ' ' + key[1]
				else:
					string2 = string2 + ', ' + key[0] + ' ' + key[1]
			string2 = string2 + ')'
			#print(string2)
			c.execute(string2)
			
		# Get exists_tasks
		exists_tasks = []
		str_ = 'select * from ' + table
		c.execute(str_)
		for row in c.fetchall():
			exists_tasks.append(row['task_name'])
		
		# Crete Tasks
		for task_keys in list_of_tasks:
			# ***************** tests *************
			try:
				if not task_keys['asset']:
					task_keys['asset'] = asset_name
				if not task_keys['asset_id']:
					task_keys['asset_id'] = asset_id
				if not task_keys['asset_path']:
					task_keys['asset_path'] = asset_path
			except:
				task_keys['asset'] = asset_name
				task_keys['asset_id'] = asset_id
				task_keys['asset_path'] = asset_path
				
			# task autsource
			task_keys['outsource'] = '0'
				
			# test task['Task_Name']
			try:
				if not task_keys['task_name']:
					conn.close()
					return(False, 'Not Task_Name!')
				else:
					if task_keys['task_name'] in exists_tasks:
						conn.close()
						return(False, (task_keys['task_name'] + ' already exists!'))
			except:
				conn.close()
				return(False, 'Not Task_Name!')
				
			# test task['Activity']
			if task_keys['task_type'] != 'service':
				try:
					if not task_keys['activity']:
						conn.close()
						return(False, 'activity!')
				except:
					conn.close()
					return(False, 'activity!')
			
			# ***************** tests end *************
			
			#
			string = "insert into " + table + " values"
			values = '('
			data = []
			for i, key in enumerate(self.tasks_keys):
				if i< (len(self.tasks_keys) - 1):
					values = values + '?, '
				else:
					values = values + '?'
				if key[0] in task_keys:
					data.append(task_keys[key[0]])
				else:
					if key[1] == 'real':
						data.append(0.0)
					elif key[1] == 'timestamp':
						data.append(None)
					else:
						data.append('')
						
			values = values + ')'
			data = tuple(data)
			string = string + values
			
			'''
			# write task to db
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
			'''
			
			# add task
			c.execute(string, data)
			
		conn.commit()
		conn.close()
		return(True, 'ok')
		
	def add_single_task(self, project_name, task_data):
		# Other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# set other data
		# -- priority
		try:
			if not task_data['priority']:
				task_data['priority'] = 'normal'
		except:
			task_data['priority'] = 'normal'
		# -- outsource
		task_data['outsource'] = '0'
		# -- workroom
		result = self.db_workroom.get_id_by_name(task_data['workroom'])
		if not result[0]:
			return(result[1])
		task_data['workroom'] = result[1]
		
		# get-set output task_name
		output_task_name = None
		if json.loads(task_data['output']):
			output_task_name = json.loads(task_data['output'])[0]
			task_data['output'] = json.dumps([output_task_name, (task_data['asset'] + ':final')])
		else:
			task_data['output'] = json.dumps([(task_data['asset'] + ':final')])
		
		# get table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
			
		# Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# ***************** get current task_status
		if not task_data['input']:
			task_data['status'] = 'ready'
		else:
			#get_input_string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
			get_input_string = 'SELECT * FROM ' + table
			#data = (task_data['input'],)
			#c.execute(get_input_string, data)
			c.execute(get_input_string)
			row = None
			#names = []
			for row_ in c.fetchall():
				#names.append(row_['task_name'])
				#print(row_)
				if task_data['task_name'] == row_['task_name']:
					conn.close()
					return(False, 'Thi Task_Name Already Exists!')
				if row_['task_name'] == task_data['input']:
					row = row_
			#print(row['status'])
			if row['status'] in self.end_statuses:
				task_data['status'] = 'ready'
			else:
				task_data['status'] = 'null'
				
			# ***************** add this task to output to input task
			input_task_data = dict(row)
			new_output_list = json.loads(input_task_data['output'])
			new_output_list.append(task_data['task_name'])
			input_task_data['output'] = json.dumps(new_output_list)
			#print(input_task_data['output'])
			
			new_output_string = string = 'UPDATE ' +  table + ' SET  output  = ? WHERE task_name = ?'
			data = (input_task_data['output'],input_task_data['task_name'])
			c.execute(new_output_string, data)
			
		# ***************** insert TASK_
		insert_string = "insert into " + table + " values"
		values = '('
		data = []
		for i, key in enumerate(self.tasks_keys):
			if i< (len(self.tasks_keys) - 1):
				values = values + '?, '
			else:
				values = values + '?'
			if key[0] in task_data:
				data.append(task_data[key[0]])
			else:
				if key[1] == 'real':
					data.append(0.0)
				elif key[1] == 'timestamp':
					data.append(None)
				else:
					data.append('')
			#print '>>> ', key[0], data[len(data) - 1]
					
		values = values + ')'
		data = tuple(data)
		insert_string = insert_string + values
		c.execute(insert_string, data)
		
		# ***************** To OUTPUTS 
		old_status = None
		output_row = None
		old_input = None
		if output_task_name:
			# get output_task_data
			get_output_string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
			data = (output_task_name,)
			c.execute(get_output_string, data)
			output_row = c.fetchone()
			old_status = output_row['status']
			old_input = output_row['input']
						
			# edit input,status to output_task
			string = 'UPDATE ' +  table + ' SET  input  = ?, status = ? WHERE task_name = ?'
			data = (task_data['task_name'],'null', output_task_name)
			c.execute(string, data)
			
			
			# edit output_list to old_input
			if old_input:
				old_input_row = None
				string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
				data = (old_input,)
				c.execute(string, data)
				old_input_row = c.fetchone()
				old_input_output = json.loads(old_input_row['output'])
				old_input_output.remove(output_task_name)
				# -- update
				string = 'UPDATE ' +  table + ' SET  output  = ? WHERE task_name = ?'
				data = (json.dumps(old_input_output), old_input)
				c.execute(string, data)
			
		conn.commit()
		conn.close()
			
		if old_input:
			# change status to output
			if (old_status != 'close') and (old_status in self.end_statuses):
				#print('change status')
				self.this_change_from_end(project_name, dict(output_row))
				
		return(True, 'Ok')
		
	def get_list(self, project_name, asset_id):
		task_list = []
		
		# Other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + asset_id + ':' + self.tasks_t + '\"'
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			task_list = c.fetchall()
		except:
			conn.close()
			return(False, 'Not Table!')
		
		conn.close()
		return(True, task_list)
		
	def get_tasks_data_by_name_list(self, project_name, task_name_list, assets_data = False):  # assets_data - dict{asset_name: {asset_data},...}
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		if not assets_data:
			result = self.get_name_data_dict_by_all_types(project_name)
			if not result[0]:
				return(False, ('in task().get_tasks_data_by_name_list ' + result[1]))
			else:
				assets_data = result[1]
		
		try:
			# Connect to db
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			conn.close()
			return(False, 'in task().get_tasks_data_by_name_list not connect to db')
		
		task_data_dict = {}
		for task_name in task_name_list:
			# read task
			if not task_name:
				continue
			
			table = '\"' + assets_data[task_name.split(':')[0]]['id'] + ':' + self.tasks_t + '\"'
			
			try:
				string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
				c.execute(string, (task_name,))
				task_data_dict[task_name] = dict(c.fetchone())
			except:
				conn.close()
				return(False, ('in task().get_tasks_data_by_name_list - Not Table! task - ' + task_name))
				
		conn.close()
		return(True, task_data_dict)
		
	def change_activity(self, project_name, task_data, new_activity):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		try:
			str_ = 'select * from ' + table
		except:
			conn.close()
			return(False, 'Not Table!')
			
		# edit db
		string = 'UPDATE ' +  table + ' SET  \"activity\"  = ? WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
				
		data = (new_activity,)
		
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		return(True, 'Ok!')
		
	def change_workroom(self, project_name, task_data, new_workroom):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# get new_workroom_id
		copy = workroom()
		result = copy.get_id_by_name(new_workroom)
		if not result[0]:
			return(False, result[1])
		new_workroom_id = result[1]
			
		# Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		try:
			str_ = 'select * from ' + table
		except:
			conn.close()
			return(False, 'Not Table!')
			
		# edit db
		string = 'UPDATE ' +  table + ' SET  \"workroom\"  = ? WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
				
		data = (new_workroom_id,)
		
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		return(True, new_workroom_id)
		
	def change_price(self, project_name, task_data, new_price):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		try:
			str_ = 'select * from ' + table
		except:
			conn.close()
			return(False, 'Not Table!')
			
		# edit db
		string = 'UPDATE ' +  table + ' SET  \"price\"  = ? WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
				
		data = (new_price,)
		
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		return(True, 'Ok!')
		
	def changes_without_a_change_of_status(self, key, project_name, task_data, new_data):
		changes_keys = [
		'activity',
		'task_type',
		'series',
		'price',
		'tz',
		'workroom',
		'extension'
		]
		if not key in changes_keys:
			return(False, 'This key invalid!')
			
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		try:
			str_ = 'select * from ' + table
		except:
			conn.close()
			return(False, 'Not Table!')
			
		# edit db
		string = 'UPDATE ' +  table + ' SET  \"' + key + '\"  = ? WHERE task_name = ?'
				
		data = (new_data, task_data['task_name'])
		
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		return(True, 'Ok!')
		
	def add_readers(self, project_name, task_data, add_readers_list):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		change_status = False
		readers_dict = {}
		
		try:
			# Connect to db
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, ('in task().add_readers Not Connect Table - path = ' + self.tasks_path))
			
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		string = 'select * from ' + table
		try:
			c.execute(string)
			# -- get old readers dict
			for row in c.fetchall():
				if row['task_name'] == task_data['task_name']:
					try:
						if json.loads(row['readers']):
							readers_dict = json.loads(row['readers'])
					except:
						pass
					if row['status'] == 'done':
						change_status = True
					break
		except:
			conn.close()
			return(False, ('in task().add_readers Not Table! - ' + table))
		
		###
		#print(add_readers_list)
		#return(False, '***')
		###
		
		for artist_name in add_readers_list:
			readers_dict[artist_name] = 0
			
		# edit .db
		if change_status:
			string = 'UPDATE ' +  table + ' SET  status  = ?, readers  = ? WHERE task_name = ?'
			data = ('checking', json.dumps(readers_dict), task_data['task_name'])
		else:
			string = 'UPDATE ' +  table + ' SET  readers  = ? WHERE task_name = ?'
			data = (json.dumps(readers_dict), task_data['task_name'])
		
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		# change output statuses
		self.this_change_from_end(project_name, task_data)
		
		return(True, readers_dict, change_status)
	
		
	def make_first_reader(self, project_name, task_data, nik_name):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		readers_dict = {}
		
		try:
			# Connect to db
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, ('in task().add_readers Not Connect Table - path = ' + self.tasks_path))
			
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		string = 'select * from ' + table
		try:
			c.execute(string)
			# -- get old readers dict
			for row in c.fetchall():
				if row['task_name'] == task_data['task_name']:
					try:
						readers_dict = json.loads(row['readers'])
					except:
						pass
					break
		except:
			conn.close()
			return(False, ('in task().add_readers Not Table! - ' + table))
		
		readers_dict['first_reader'] = nik_name
		
		# edit .db
		string = 'UPDATE ' +  table + ' SET  readers  = ? WHERE task_name = ?'
		data = (json.dumps(readers_dict), task_data['task_name'])
		
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		return(True, readers_dict)
	
	
	def remove_readers(self, project_name, task_data, remove_readers_list):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])

		change_status = False
		readers_dict = {}
		task_data = dict(task_data)
		
		try:
			# Connect to db
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, ('in task().remove_readers Not Connect Table - path = ' + self.tasks_path))
			
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		string = 'select * from ' + table
		try:
			c.execute(string)
			# -- get old readers dict
			for row in c.fetchall():
				if row['task_name'] == task_data['task_name']:
					try:
						readers_dict = json.loads(row['readers'])
					except:
						pass
					break
		except:
			conn.close()
			return(False, ('in task().remove_readers Not Table! - ' + table))
		
		# remove artists
		for artist_name in remove_readers_list:
			try:
				del readers_dict[artist_name]
			except:
				pass
			
		# get change status
		if task_data['status'] == 'checking':
			change_status = True
		if not readers_dict:
			change_status = False
		else:
			for artist_name in readers_dict:
				if readers_dict[artist_name] == 0:
					change_status = False
					break
		
		# edit db
		if change_status:
			string = 'UPDATE ' +  table + ' SET  status = ?, readers  = ? WHERE task_name = ?'
			data = ('done', json.dumps(readers_dict), task_data['task_name'])
		else:
			string = 'UPDATE ' +  table + ' SET  readers  = ? WHERE task_name = ?'
			data = (json.dumps(readers_dict), task_data['task_name'])
		
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		# change output statuses
		if change_status:
			result = self.this_change_to_end(project_name, task_data)
			if not result[0]:
				return(False, result[1])
		
		return(True, readers_dict, change_status)
		
	
	def change_artist(self, project_name, task_data, new_artist):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# --------------- edit Status ------------
		new_status = None
				
		# get artist outsource
		artist_outsource = False
		art = artist()
		if new_artist:
			result = art.read_artist({'nik_name':new_artist})
			if not result[0]:
				return(False, result[1])
			if result[1][0]['outsource']:
				artist_outsource = bool(int(result[1][0]['outsource']))
		else:
			new_artist = ''
			
		# get task_outsource
		task_outsource = False
		if task_data['outsource']:
			task_outsource = bool(int(task_data['outsource']))
		'''
		self.change_by_outsource_statuses = {
		'to_outsource':{'ready':'ready_to_send', 'work':'ready_to_send'},
		'to_studio':{'ready_to_send':'ready', 'work_to_outsorce':'ready'},
		}
		'''
		# get new status
		if task_data['status'] in self.variable_statuses:
			#print('****** in variable')
			if (not task_data['artist']) or (not task_outsource):
				#print('****** start not outsource')
				if artist_outsource:
					new_status = self.change_by_outsource_statuses['to_outsource'][task_data['status']]
				else:
					pass
					#print('****** artist not outsource')
			else:
				#print('****** start outsource')
				if not artist_outsource:
					new_status = self.change_by_outsource_statuses['to_studio'][task_data['status']]
				else:
					pass
					#print('****** artist outsource')
		else:
			pass
			#print('****** not in variable')
		
		# ------------- edit DB -----------------
		# Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		try:
			str_ = 'select * from ' + table
		except:
			conn.close()
			return(False, 'Not Table!')
			
		# edit db
		if new_status:
			string = 'UPDATE ' +  table + ' SET  \"artist\"  = ?, \"outsource\"  = ?, \"status\"  = ?  WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
			data = (new_artist, str(int(artist_outsource)), new_status)
		else:
			string = 'UPDATE ' +  table + ' SET  \"artist\"  = ?, \"outsource\"  = ?  WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
			data = (new_artist, str(int(artist_outsource)))
		
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		return(True, (new_status, str(int(artist_outsource))))
		
	def change_input(self, project_name, task_data, new_input):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		new_status = False
		
		# get task_outsource
		task_outsource = False
		if task_data['outsource']:
			task_outsource = bool(int(task_data['outsource']))
		
		# get old inputs tasks data
		old_input_task_data = None
		if task_data['input']:
			result = self.read_task(project_name, task_data['input'], task_data['asset_id'], 'all')
			if not result[0]:
				return(False, result[1])
			old_input_task_data = result[1]
		
		# get new inputs task data
		new_input_task_data = None
		if new_input:
			result = self.read_task(project_name, new_input, task_data['asset_id'], 'all')
			if not result[0]:
				return(False, result[1])
			new_input_task_data = result[1]
			new_input_status = new_input_task_data['status']
		
		# ???
		# change status
		new_status = self.from_input_status(task_data, new_input_task_data)
		if task_data['status'] in self.end_statuses and not new_status in self.end_statuses:
			self.this_change_from_end(project_name, task_data)
				
		# change outputs
		# -- in old input
		list_output_old = None
		if old_input_task_data:
			list_output_old = json.loads(old_input_task_data['output'])
			if task_data['task_name'] in list_output_old:
				list_output_old.remove(task_data['task_name'])
			list_output_old = json.dumps(list_output_old)
			
		# -- in new input
		list_output_new = None
		if new_input_task_data:
			if not new_input_task_data['output']:
				list_output_new = []
			else:
				list_output_new = json.loads(new_input_task_data['output'])
			list_output_new.append(task_data['task_name'])
			list_output_new = json.dumps(list_output_new)
				
		# edit db
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
		except:
			conn.close()
			return(False, 'Not Table!')
			
		# edit old_output
		string_old, data_old = None,None
		if list_output_old:
			string_old = 'UPDATE ' +  table + ' SET  \"output\"  = ? WHERE \"task_name\" = \"' + old_input_task_data['task_name'] + '\"'
			data_old = (list_output_old,)
			c.execute(string_old, data_old)
		
		# edit new_output
		string_new, data_new = None,None
		if list_output_new:
			# output
			string_new = 'UPDATE ' +  table + ' SET  \"output\"  = ? WHERE \"task_name\" = \"' + new_input_task_data['task_name'] + '\"'
			data_new = (list_output_new,)
			c.execute(string_new, data_new)
			# input
			string = 'UPDATE ' +  table + ' SET  \"input\"  = ? WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
			data = (new_input_task_data['task_name'],)
			c.execute(string, data)
		else:
			string = 'UPDATE ' +  table + ' SET  \"input\"  = ? WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
			data = ('',)
			c.execute(string, data)
			
		
		# edit status
		if new_status:
			string = 'UPDATE ' +  table + ' SET  \"status\"  = ? WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
			data = (new_status,)
			c.execute(string, data)
		
		conn.commit()
		conn.close()
		
		if list_output_old:
			old_input_task_data['output'] = list_output_old
		if list_output_new:
			new_input_task_data['output'] = list_output_new
		
		return(True, (new_status, old_input_task_data, new_input_task_data))
		
	def accept_task(self, project_name, task_data):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		#try:
		# remove readers
		readers = json.dumps({})
		
		string = 'UPDATE ' +  table + ' SET  readers = ?, status  = ? WHERE task_name = ?'
		data = (readers, 'done', task_data['task_name'])
		c.execute(string, data)
		conn.commit()
		conn.close()
		'''				
		except:
			conn.close()
			return(False, 'in accept_task - Not Edit Table!')
		'''	
		# -- publish
		#result = lineyka_publish.publish().publish(project_name, task_data)
		result = self.publish.publish(project_name, task_data)
		if not result[0]:
			return(False, result[1])
		
		# -- change output statuses
		result = self.this_change_to_end(project_name, task_data)
		if not result[0]:
			return(False, result[1])
		
		return(True, 'Ok!')
			
	def readers_accept_task(self, project_name, task_data, nik_name):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		change_status = True
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		
		
		# read .db
		string = 'SELECT * FROM ' +  table + ' WHERE task_name = ?'
		data = (task_data['task_name'],)
		c.execute(string, data)
		task_data = dict(c.fetchone())
		readers = json.loads(task_data['readers'])
		if nik_name in readers:
			readers[nik_name] = 1
		task_data['readers'] = json.dumps(readers)

		# get change_status
		for key in readers:
			if key == 'first_reader':
				continue
			elif readers[key] == 0:
				change_status = False
				break

		# update readers .db
		if change_status:
			string = 'UPDATE ' +  table + ' SET status  = ?, readers  = ? WHERE task_name = ?'
			data = ('done', task_data['readers'], task_data['task_name'])
			c.execute(string, data)
		else:
			string = 'UPDATE ' +  table + ' SET  readers  = ? WHERE task_name = ?'
			data = (task_data['readers'], task_data['task_name'])
			c.execute(string, data)
			
		conn.commit()
		conn.close()
		
		# change output statuses
		if change_status:
			# -- change output statuses
			result = self.this_change_to_end(project_name, task_data)
			if not result[0]:
				return(False, result[1])
		
		# -- publish
		#result = lineyka_publish.publish().publish(project_name, task_data)
		result = self.publish.publish(project_name, task_data)
		if not result[0]:
			return(False, result[1])
		
		return(True, 'Ok')
	
	def close_task(self, project_name, task_data):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		try:
			string = 'UPDATE ' +  table + ' SET  status  = ? WHERE task_name = ?'
			data = ('close', task_data['task_name'])
			c.execute(string, data)
			conn.commit()
			conn.close()
						
		except:
			conn.close()
			return(False, 'in accept_task - Not Edit Table!')
			
		result = self.this_change_to_end(project_name, task_data)
		if not result[0]:
			return(False, result[1])
		else:
			return(True, 'Ok!')
			
	def rework_task(self, project_name, task_data, current_user = False):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# get exists chat
		if current_user:
			exists_chat = False
			result = chat().read_the_chat(project_name, task_data['task_name'])
			if not result[0]:
				return(False, 'not chat!')
			
			delta = datetime.timedelta(minutes = 45)
			now_time = datetime.datetime.now()
			for topic in result[1]:
				if topic['author'] == current_user:
					if (now_time - topic['date_time']) <= delta:
						exists_chat = True
						break
						
			if not exists_chat:
				return(False, 'not chat!')
			
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		
		#try:
			
		# read .db
		string = 'SELECT * FROM ' +  table + ' WHERE task_name = ?'
		data = (task_data['task_name'],)
		c.execute(string, data)
		task_data = dict(c.fetchone())
		if task_data['readers']:
			readers = json.loads(task_data['readers'])
			for nik_name in readers:
				if nik_name == 'first_reader':
					continue
				readers[nik_name] = 0
			task_data['readers'] = json.dumps(readers)
		
		string = 'UPDATE ' +  table + ' SET  readers = ?, status  = ? WHERE task_name = ?'
		data = (task_data['readers'], 'recast', task_data['task_name'])
		c.execute(string, data)
		
		conn.commit()
		conn.close()
		
		'''				
		except:
			conn.close()
			return(False, 'in rework_task - Not Edit Table!')
		'''
			
		return(True, 'Ok!')
			
	def return_a_job_task(self, project_name, task_data):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# dict task_data
		task_data = dict(task_data)
		
		# get input_task_data
		input_task_name = task_data['input']
		input_task_data = False
		if input_task_name:
			result = self.read_task(project_name, input_task_name, task_data['asset_id'], 'all')
			if not result[0]:
				return(False, result[1])
			input_task_data = result[1]
		
		task_data['status'] = 'null'
		new_status = self.from_input_status(task_data, input_task_data)
				
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# Exists table
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		
		try:
			string = 'SELECT * FROM ' + table + 'WHERE task_name = ?'
			data = (task_data['task_name'],)
			c.execute(string, data)
			row = dict(c.fetchone())
			readers = {}
			try:
				readers = json.loads(row['readers'])
			except:
				pass
			for key in readers:
				if key == 'first_reader':
					continue
				readers[key] = 0
			row['readers'] = json.dumps(readers)
			
			string = 'UPDATE ' +  table + ' SET  readers = ?, status  = ? WHERE task_name = ?'
			data = (row['readers'], new_status, task_data['task_name'])
			c.execute(string, data)
			conn.commit()
			conn.close()
						
		except:
			conn.close()
			return(False, 'in return_a_job_task - Not Edit Table!')
		
		# -- change output statuses
		result = self.this_change_from_end(project_name, task_data)
		if not result[0]:
			return(False, result[1])
		else:
			return(True, new_status)
			
	def change_work_statuses(self, project_name, change_statuses):  # change_statuses - [(task_data, new_status), ...]
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		#return(False, json.dumps(change_statuses))
			
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		return_data = {}
		
		for data in change_statuses:
			task_data = data[0]
			new_status = data[1]
			# Exists table
			table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
			try:
				string = 'UPDATE ' +  table + ' SET  status  = ? WHERE task_name = ?'
				data = (new_status, task_data['task_name'])
				c.execute(string, data)
				return_data[task_data['task_name']] = new_status
			except:
				conn.close()
				return(False, 'in change_work_statuses - Not Edit Table!')
				
		conn.commit()
		conn.close()
		
		return(True, return_data)
				
	def read_task(self, project_name, task_name, asset_id, keys):
		if keys == 'all':
			new_keys = []
			for key in self.tasks_keys:
				new_keys.append(key[0])
			keys = new_keys
			
		# other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# read tasks
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		table = '\"' + asset_id + ':' + self.tasks_t + '\"'
		string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
		
		try:
			c.execute(string)
			row = c.fetchone()
		except:
			conn.close()
			#return(False, ('can_not_read_asset', string))
			return(False, string)
		conn.close()
		
		if not row:
			return(False, 'not_task_name')
				
		data = {}
		for key in keys:
			try:
				data[key] = row[key]
			except:
				pass
				print(('not key: ' + key + ' in ' + row['task_name']))
			
		return(True, data)
		
	def get_task_list_of_artist(self, project_name, nik_name):
		pass
		# get asset_list  get_name_data_dict_by_all_types
		#result = self.get_list_by_all_types(project_name)
		result = self.get_name_data_dict_by_all_types(project_name)
		if not result[0]:
			return(False, result[1])
		asset_list = result[1]
		
		# read tasks
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		task_list = []
		task_input_task_list = {}
		
		for asset_name in asset_list:
			if asset_list[asset_name]['status']== 'active':
				asset_id = asset_list[asset_name]['id']
				table = '\"' + asset_id + ':' + self.tasks_t + '\"'
				string = 'select * from ' + table + ' WHERE artist = ?'
				data = (nik_name,)
				try:
					c.execute(string, data)
					rows = c.fetchall()
					task_list = task_list + rows
				except:
					conn.close()
					return(False, string)
					
		for task in task_list:
			row = {}
			if task['input']:
				input_asset_id = asset_list[task['input'].split(':')[0]]['id']
				table = '\"' + input_asset_id + ':' + self.tasks_t + '\"'
				string = 'select * from ' + table + ' WHERE task_name = ?'
				data = (task['input'],)
				
				try:
					c.execute(string, data)
					row = c.fetchone()
					#task_input_task_list[task['task_name']] = {'task' : dict(task), 'input':dict(row)}
				except:
					conn.close()
					return(False, string)
			
			try:
				task_input_task_list[task['task_name']] = {'task' : dict(task), 'input':dict(row)}
			except:
				print('*'*250)
				print(task['task_name'], task['input'])
				print(row)
				continue
		conn.close()
		
		return(True, task_input_task_list, asset_list)
		
		
	def get_chek_list_of_artist(self, project_name, nik_name):
		# get all asset dict
		result = self.get_name_data_dict_by_all_types(project_name)
		if not result[0]:
			return(False, result[1])
		asset_list = result[1]
		
		# read tasks
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		task_list = []
		chek_list = []
		
		for asset_name in asset_list:
			if asset_list[asset_name]['status']== 'active':
				asset_id = asset_list[asset_name]['id']
				table = '\"' + asset_id + ':' + self.tasks_t + '\"'
				#string = 'select * from ' + table + ' WHERE status = ?'
				string = 'select * from ' + table
				data = ('checking',)
				try:
					#c.execute(string, data)
					c.execute(string)
					rows = c.fetchall()
					task_list = task_list + rows
				except:
					conn.close()
					return(False, string)
					
		for task in task_list:
			try:
				readers = json.loads(task['readers'])
			except:
				continue
			readers2 = {}
			try:
				readers2 = json.loads(task['chat_local'])
				#print(readers2)
			except:
				pass
			
			if nik_name in readers and task['status'] == 'checking':
				if readers[nik_name] == 0:
					if 'first_reader' in readers:
						if readers['first_reader'] == nik_name:
							chek_list.append(dict(task))
						elif readers[readers['first_reader']] == 1:
							chek_list.append(dict(task))
					else:
						chek_list.append(dict(task))
			elif nik_name in readers and nik_name in readers2 and readers2[nik_name] == 0:
				chek_list.append(dict(task))
			else:
				pass
				#print('epte!')
				
		return(True, chek_list)
		
	def service_add_list_to_input(self, project_name, task_data, input_task_list):
		task_data = dict(task_data)
		
		# other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# add input list
		# -- get_input_list
		overlap_list = []
		inputs = []
		done_statuses = []
		rebild_input_task_list = []
		for task in input_task_list:
			task = dict(task)
			# -- get inputs list
			if task_data['input']:
				ex_inputs = []
				try:
					ex_inputs = json.loads(task_data['input'])
				except:
					pass
				if task['task_name'] in ex_inputs:
					overlap_list.append(task['task_name'])
					continue
			inputs.append(task['task_name'])
			# -- get done statuses
			done_statuses.append(task['status'] in self.end_statuses)
			
			# edit outputs
			if task['output']:
				ex_outputs = []
				try:
					ex_outputs = json.loads(task['output'])
				except:
					pass
				ex_outputs.append(task_data['task_name'])
				task['output'] = json.dumps(ex_outputs)
			else:
				this_outputs = []
				this_outputs.append(task_data['task_name'])
				task['output'] = json.dumps(this_outputs)
				
			rebild_input_task_list.append(task)
			
		if not task_data['input']:
			task_data['input'] = json.dumps(inputs)
		else:
			ex_inputs = []
			try:
				ex_inputs = json.loads(task_data['input'])
			except:
				pass
			task_data['input'] = json.dumps(ex_inputs + inputs)
		
		# change status
		if task_data['status'] in self.end_statuses:
			if False in done_statuses:
				task_data['status'] = 'null'
				self.this_change_from_end(project_name, task_data)
		
		# edit db
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# -- -- edit Current Task
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		
		string = 'UPDATE ' +  table + ' SET  \"input\"  = ?, \"status\"  = ?  WHERE \"task_name\" = \"' + task_data['task_name'] + '\"'
		data = (task_data['input'], task_data['status'])
		c.execute(string, data)
		# debug
		#print('input: ', string, data)
		
		# -- -- edit Outputs Task
		append_task_name_list = []
		#for task in input_task_list:
		for task in rebild_input_task_list:
			#print(task['task_name'], task['output'])
			if not task['task_name'] in overlap_list:
				table = '\"' + task['asset_id'] + ':' + self.tasks_t + '\"'
				string = 'UPDATE ' +  table + ' SET  \"output\"  = ?  WHERE \"task_name\" = \"' + task['task_name'] + '\"'
				data = (task['output'],)
				c.execute(string, data)
				append_task_name_list.append(task['task_name'])
				# debug
				print('output: ', string, data)
		
		conn.commit()
		conn.close()
		return(True, (task_data['status'], append_task_name_list))
		
	def service_add_list_to_input_from_asset_list(self, project_name, task_data, asset_list):
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		# edit db
		# -- Connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# get task list
		final_tasks_list = []
		for asset in asset_list:
			if task_data['asset_type'] in ['location', 'shot_animation'] and asset['type'] in ['obj', 'char']:
				activity = None
				if asset['type'] == 'obj':
					activity = 'model'
				elif asset['type'] == 'char':
					activity = 'rig'
				
				# get all task data
				table = '\"' + asset['id'] + ':' + self.tasks_t + '\"'
				string = 'select * from ' + table
				try:
					c.execute(string)
				except:
					print(('Not exicute in service_add_list_to_input_from_asset_list -> ' + asset['name']))
					continue
				else:
					td_dict = {}
					rows = c.fetchall()
					for td in rows:
						td_dict[td['task_name']] = td
						
					for td in rows:
						if td['activity'] == activity:
							if not dict(td).get('input') or td_dict[td['input']]['activity'] != activity:
								final_tasks_list.append(td)
			
			else:
				task_name = (asset['name'] + ':final')
				
				table = '\"' + asset['id'] + ':' + self.tasks_t + '\"'
				string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
				try:
					c.execute(string)
					final_task = dict(c.fetchone())
					final_tasks_list.append(final_task)
				except:
					print(('not found task: ' + task_name))
		
		conn.close()
		
		result = self.service_add_list_to_input(project_name, task_data, final_tasks_list)
		if not result[0]:
			return(False, result[1])
		
		return(True, result[1])
		
	def service_remove_task_from_input(self, project_name, task_data, removed_tasks_list):
		if not self.tasks_path:
			result = self.get_project(project_name)
			if not result[0]:
				return(False, result[1])
		# get input_list
		input_list = json.loads(task_data['input'])
		# removed input list
		for task in removed_tasks_list:
			if task['task_name'] in input_list:
				input_list.remove(task['task_name'])
			else:
				print('warning! *** ', task['task_name'], ' not in ', input_list)
		
		# GET STATUS
		new_status = None
		old_status = task_data['status']
		
		# ****** connect to db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		assets = False
		if old_status == 'done' or not input_list:
			new_status = 'done'
		else:
			# get assets dict
			result = self.get_name_data_dict_by_all_types(project_name)
			if not result[0]:
				return(False, result[1])
			assets = result[1]
			
			bool_statuses = []
			
			for task_name in input_list:
				try:
					asset_id = assets[task_name.split(':')[0]]['id']
				except:
					print(('in from_service_remove_input_tasks incorrect key: ' + task_name.split(':')[0] + ' in ' + task_name))
					continue
				
				table = '\"' + asset_id + ':' + self.tasks_t + '\"'
				
				string = 'select * from ' + table + ' WHERE task_name = \"' + task_name + '\"'
				try:
					c.execute(string)
					inp_task_data = c.fetchone()
				except:
					conn.close()
					return(False, ('in from_service_remove_input_tasks can not read ' + string))
					
				if inp_task_data['status'] in self.end_statuses:
					bool_statuses.append(True)
				else:
					bool_statuses.append(False)
					
			if False in bool_statuses:
				new_status = 'null'
			else:
				new_status = 'done'
				
			
		# CHANGE output LIST
		for task in removed_tasks_list:
			
			output_list = False
			try:
				output_list = json.loads(task['output'])
			except:
				continue
			
			table = '\"' + task['asset_id'] + ':' + self.tasks_t + '\"'
			if output_list:
				try:
					output_list.remove(task_data['task_name'])
				except:
					# debug
					print('\n')
					print(output_list)
					print('in \"service_remove_task_from_input\" in output not ' + task_data['task_name'])
					continue
					
				string = 'UPDATE ' + table + ' SET output = ? WHERE task_name = ?'
				data = (json.dumps(output_list), task['task_name'])
				c.execute(string, data)
				# debug
				#print(task['task_name'],'CHANGE output LIST:\n', string, data)
					
		# CHANGE STATUS
		# CHANGE INPUT LIST
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		string = 'UPDATE ' + table + ' SET status = ?, input = ?  WHERE task_name = ?'
		data = (new_status, json.dumps(input_list), task_data['task_name'])
		c.execute(string, data)
		# debug
		#print(task_data['task_name'],'CHANGE INPUT LIST, STATUS:\n', string, data)
		
		conn.commit()
		conn.close()
		
		
		if old_status == 'done' and new_status == 'null':
			self.this_change_from_end(project_name, task_data, assets = assets)
		elif old_status == 'null' and new_status == 'done':
			self.this_change_to_end(project_name, task_data, assets = assets)
						
		return(True, (new_status, input_list))
		
	def service_change_task_in_input(self, project_name, task_data, removed_task_data, added_task_data):
		# other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		# debug	
		print(task_data['task_name'])
		print(removed_task_data['task_name'])
		print(added_task_data['task_name'])
		
		# remove task
		result = self.service_remove_task_from_input(project_name, task_data, [removed_task_data])
		if not result[0]:
			return(False, result[1])
		
		new_status, input_list = result[1]
		
		# edit task_data.input
		task_data = dict(task_data)
		#input_tasks = json.loads(task_data['input'])
		#input_tasks.remove(removed_task_data['task_name'])
		#task_data['input'] = json.dumps(input_tasks)
		task_data['input'] = json.dumps(input_list)
		task_data['status'] = new_status
		
		#print(json.dumps(task_data, sort_keys = True, indent = 4))
		#return(False, 'Epteeeee!')
		
		# add task
		result = self.service_add_list_to_input(project_name, task_data, [added_task_data])
		if not result[0]:
			return(False, result[1])
			
		return(True, result[1])
			
class log(task):
	'''
	notes_log(project_name, task_name, {key: data, ...}) 
	
	read_log(project_name, asset_name, {key: key_name, ...});; example: self.read_log(project, asset, {'activity':'rig_face', 'action':'push'});; return: (True, ({key: data, ...}, {key: data, ...}, ...))  or (False, comment)
	
	'''
	
	def __init__(self):
		self.logs_keys = [
		('version', 'text'),
		('date_time', 'timestamp'),
		('activity', 'text'),
		('task_name', 'text'),
		('action', 'text'),
		('artist', 'text'),
		('comment', 'text'),
		]
		
		self.camera_log_file_name = 'camera_logs.json'
		self.playblast_log_file_name = 'playblast_logs.json'
		
		self.log_actions = ['push', 'open', 'report','recast' , 'change_artist', 'close', 'done', 'return_a_job', 'send_to_outsource', 'load_from_outsource']
		
		task.__init__(self)
	
	def notes_log(self, project_name, logs_keys, asset_id):
		
		# other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# test task_name
		try:
			task_name = (logs_keys['task_name'],)
		except:
			return False, 'not task_name'
		
		# date time
		try:
			time = logs_keys['date_time']
		except:
			logs_keys['date_time'] = datetime.datetime.now()
		
		# open db
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		table = '\"' + asset_id + ':' + logs_keys['activity'] + ':logs\"'
		
		# exists and create table
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key in enumerate(self.logs_keys):
				if i == 0:
					string2 = string2 + key[0] + ' ' + key[1]
				else:
					string2 = string2 + ', ' + key[0] + ' ' + key[1]
			string2 = string2 + ')'
			c.execute(string2)
			
		# create string to add log
		string = "insert into " + table + " values"
		values = '('
		data = []
		for i, key in enumerate(self.logs_keys):
			if i< (len(self.logs_keys) - 1):
				values = values + '?, '
			else:
				values = values + '?'
			if key[0] in logs_keys:
				data.append(logs_keys[key[0]])
			else:
				if key[1] == 'real':
					data.append(0.0)
				elif key[1] == 'timestamp':
					data.append(None)
				else:
					data.append('')
					
		values = values + ')'
		data = tuple(data)
		string = string + values
		
		# add log
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		return(True, 'ok')
		
	def read_log(self, project_name, asset_id, activity):
		# other errors test
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		# read tasks
		conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# create string
		table = '\"' + asset_id + ':' + activity + ':logs\"'
		string = 'select * from ' + table
		
		rows = None
		
		try:
			c.execute(string)
			rows = c.fetchall()
		except:
			conn.close()
			return(False, 'can_not_read_logs!')
		'''
		c.execute(string)
		rows = c.fetchall()
		'''
		conn.close()
		return(True, rows)
		
	def get_push_logs(self, project_name, task_data):
		# get all logs
		result = self.read_log(project_name, task_data['asset_id'], task_data['activity'])
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
	
	# *** CAMERA LOGS ***
	def camera_notes_log(self, project_name, task_data, comment, version):
		logs_keys = {}
		tasks_keys = []
		for key in self.tasks_keys:
			tasks_keys.append(key[0])
		
		for key in self.logs_keys:
			if key[0] in tasks_keys:
				logs_keys[key[0]] = task_data[key[0]]
				
		logs_keys['comment'] = comment
		logs_keys['action'] = 'push_camera'
		dt = datetime.datetime.now()
		date = str(dt.year) + '/' + str(dt.month) + '/' + str(dt.day) + '/' + str(dt.hour) + ':' + str(dt.minute)
		logs_keys['date_time'] = date
		logs_keys['version'] = version
		
		path = os.path.join(task_data['asset_path'], self.additional_folders['meta_data'], self.camera_log_file_name)
		path = os.path.normpath(path)
		
		data = {}
		
		if os.path.exists(path):
			with open(path, 'r') as f:
				try:
					data = json.load(f)
				except:
					pass
		
		data[version] = logs_keys
		
		with open(path, 'w') as f:
			jsn = json.dump(data, f, sort_keys=True, indent=4)
		
		return(True, 'Ok!')
	
	def camera_read_log(self, project_name, task_data):
		path = os.path.join(task_data['asset_path'], self.additional_folders['meta_data'], self.camera_log_file_name)
		if not os.path.exists(path):
			return(False, 'No saved versions!')
			
		with open(path, 'r') as f:
			data = None
			try:
				data = json.load(f)
			except:
				return(False, ('problems with file versions: ' + path))
		
		nums = []
		sort_data = []
		for key in data:
			nums.append(int(key))
		nums.sort()
		
		for num in nums:
			key = '0'*(4 - len(str(num))) + str(num)
			sort_data.append(data[str(key)])
			
		return(True, sort_data)
		
	# *** PLAYBLAST LOGS ***
	def playblast_notes_log(self, project_name, task_data, comment, version):
		logs_keys = {}
		tasks_keys = []
		for key in self.tasks_keys:
			tasks_keys.append(key[0])
		
		for key in self.logs_keys:
			if key[0] in tasks_keys:
				logs_keys[key[0]] = task_data[key[0]]
				
		logs_keys['comment'] = comment
		logs_keys['action'] = 'playblast'
		dt = datetime.datetime.now()
		date = str(dt.year) + '/' + str(dt.month) + '/' + str(dt.day) + '/' + str(dt.hour) + ':' + str(dt.minute)
		logs_keys['date_time'] = date
		logs_keys['version'] = version
		
		path = os.path.join(task_data['asset_path'], self.additional_folders['meta_data'], self.playblast_log_file_name)
		path = os.path.normpath(path)
		
		data = {}
		
		if os.path.exists(path):
			with open(path, 'r') as f:
				try:
					data = json.load(f)
				except:
					pass
		
		data[version] = logs_keys
		
		with open(path, 'w') as f:
			jsn = json.dump(data, f, sort_keys=True, indent=4)
		
		return(True, 'Ok!')
	
	def playblast_read_log(self, project_name, task_data):
		path = os.path.join(task_data['asset_path'], self.additional_folders['meta_data'], self.playblast_log_file_name)
		if not os.path.exists(path):
			return(False, 'No saved versions!')
			
		with open(path, 'r') as f:
			data = None
			try:
				data = json.load(f)
			except:
				return(False, ('problems with file versions: ' + path))
		
		nums = []
		sort_data = []
		for key in data:
			nums.append(int(key))
		nums.sort()
		
		for num in nums:
			key = '0'*(4 - len(str(num))) + str(num)
			sort_data.append(data[str(key)])
			
		return(True, sort_data)
		
	
	def camera_get_push_logs(self, project_name, task_data):
		pass
		
class artist(studio):
	'''
	self.add_artist({key:data, ...}) - "nik_name", "user_name" - Required, add new artist in 'artists.db';; return - (True, 'ok') or (Fasle, comment) comments: 'overlap', 'not nik_name', 
	
	self.login_user(nik_name, password) - 
	
	self.read_artist({key:data, ...}) - "nik_name", - Required, returns full information, relevant over the keys ;; example: self.read_artist({'specialty':'rigger'});; return: (True, [{Data}, ...])  or (False, comment)
	
	self.edit_artist({key:data, ...}) - "nik_name", - Required, does not change the setting ;;
	
	self.get_user() - ;; return: (True, (nik_name, user_name)), (False, 'more than one user'), (False, 'not user') ;;
	
	self.add_stat(user_name, {key:data, ...}) - "project_name, task_name, data_start" - Required ;;
	
	self.read_stat(user_name, {key:data, ...}) - returns full information, relevant over the keys: (True, [{Data}, ...]) or (False, comment);; 
	
	self.edit_stat(user_name, project_name, task_name, {key:data, ...}) - 
	'''
	def __init__(self):
		studio.__init__(self)
		
	def add_artist(self, keys):
		# test nik_name
		try:
			nik_name = keys['nik_name']
			if not nik_name:
				return(False, 'not nik_name')
		except:
			return(False, 'not nik_name')
			
		# test user_name
		try:
			user_name = keys['user_name']
		except:
			return(False, 'not user_name')
		
		# create string
		table = self.artists_t
		string = "insert into " + table + " values"
		values = '('
		data = []
		for i, key in enumerate(self.artists_keys):
			if i< (len(self.artists_keys) - 1):
				values = values + '?, '
			else:
				values = values + '?'
			if key[0] in keys:
				data.append(keys[key[0]])
			else:
				if key[1] == 'real':
					data.append(0.0)
				elif key[1] == 'timestamp':
					data.append(datetime.datetime.now())
				else:
					data.append('')
					
		values = values + ')'
		data = tuple(data)
		string = string + values
		
		if not self.artists_path:
			self.get_studio()
		
		# write task to db
		conn = sqlite3.connect(self.artists_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# exists table
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			# unicum task_name test
			r = c.fetchall()
			for row in r:
				if row['nik_name'] == keys['nik_name']:
					conn.close()
					return(False, 'overlap')
				if row['user_name'] == keys['user_name']:
					string3 = 'UPDATE ' +  table + ' SET user_name = \"\" WHERE nik_name = \"' + row['nik_name'] + '\"'
					c.execute(string3)
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key in enumerate(self.artists_keys):
				if i == 0:
					string2 = string2 + key[0] + ' ' + key[1]
				else:
					string2 = string2 + ', ' + key[0] + ' ' + key[1]
			string2 = string2 + ')'
			'''
			# -- 
			print 'String 2: ', string2
			conn.close()
			return
			# --
			'''
			c.execute(string2)
		
		# add task
		c.execute(string, data)
		conn.commit()
		conn.close()
		return(True, 'ok')
			
	def read_artist(self, keys):
		# create string
		table = self.artists_t
		
		if not self.artists_path or (not os.path.exists(self.artists_path)):
			#print('artists_path:', self.artists_path)
			return(False, 'Not Artist Path')
		
		if keys == 'all':
			string = 'select * from ' + table		
		else:
			string = 'select * from ' + table + ' WHERE '
			for i,key in enumerate(keys):
				if i == 0:
					string = string + ' ' + key + ' = ' + '\"' + keys[key] + '\"'
				else:
					string = string + 'and ' + key + ' = ' + '\"' + keys[key] + '\"'
				
		#return string
		
		# read artists
		conn = sqlite3.connect(self.artists_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		'''
		c.execute(string)
		rows = c.fetchall()
		'''
		try:
			c.execute(string)
			rows = c.fetchall()
		except:
			conn.close()
			return(False, 'can_not_read_artists')
				
		conn.close()
		'''
		if not rows:
			return False, 'not_task_name'
		'''
		return(True, rows)
		
	def read_artist_of_workroom(self, workroom_id):
		# create string
		table = self.artists_t
		
		if not self.artists_path or (not os.path.exists(self.artists_path)):
			#print('artists_path:', self.artists_path)
			return(False, 'Not Artist Path')
			
		string = 'select * from ' + table
		
		try:
			# connect .db
			conn = sqlite3.connect(self.artists_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, 'in artist().read_artist_of_workroom Not Table Connect!')
			
		rows = c.execute(string)
		
		if not rows:
			conn.close()
			return(False, 'Not Artists!')
		
		artists_dict = {}
		for row in rows:
			try:
				workrooms = json.loads(row['workroom'])
			except:
				continue
			if workroom_id in workrooms:
				artists_dict[row['nik_name']] = dict(row)
			
		#c.close()
		conn.close()
		
		return(True, artists_dict)
		
		
	def login_user(self, nik_name, password):
		user_name = getpass.getuser()
		table = self.artists_t
		string = 'select * from ' + table + ' WHERE nik_name = \"' + nik_name + '\"'
		
		conn = sqlite3.connect(self.artists_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		c.execute(string)
		rows = c.fetchall()
		
		if len(rows)== 0:
			conn.close()
			return(False, 'not user')
			
		else:
			if password == rows[0]['password']:
				string2 = 'select * from ' + table + ' WHERE user_name = \"' + user_name + '\"'
				c.execute(string2)
				rows = c.fetchall()
				for row in rows:
					#print(row['nik_name'])
					string3 = 'UPDATE ' +  table + ' SET user_name = \'\' WHERE nik_name = \"' + row['nik_name'] + '\"'
					#print(string3)
					c.execute(string3)
					
				string4 = 'UPDATE ' +  table + ' SET user_name = \"' + user_name + '\" WHERE nik_name = \"' + nik_name + '\"'
				c.execute(string4)
				conn.commit()
				conn.close()
				return(True, (nik_name, user_name))
				
			else:
				conn.close()
				return(False, 'not password')
		
	def get_user(self, outsource = False):
		user_name = getpass.getuser()
		table = self.artists_t
		string = 'select * from ' + table + ' WHERE user_name = \"' + user_name + '\"'
		
		try:
			conn = sqlite3.connect(self.artists_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, 'Not Artist Table!')
		
		#return string
		'''
		c.execute(string)
		rows = c.fetchall()
		
		'''
		# read db
		try:
			c.execute(string)
			rows = c.fetchall()
		except:
			conn.close()
			return False, 'can_not_read_artists'
				
		conn.close()
		
		# conditions # return
		if len(rows)>1:
			return False, 'more than one user'
		elif len(rows)== 0:
			return False, 'not user'
		else:
			if not outsource:
				return True, (rows[0]['nik_name'], rows[0]['user_name'], None, rows[0])
			else:
				if rows[0]['outsource']:
					out_source = bool(int(rows[0]['outsource']))
				else:
					out_source = False
				return True, (rows[0]['nik_name'], rows[0]['user_name'], out_source, rows[0])
	
	def edit_artist(self, key_data):
		# test nik_name
		try:
			nik_name = (key_data['nik_name'],)
		except:
			return False, 'not nik_name'
			
		# write task to db
		conn = sqlite3.connect(self.artists_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		c = conn.cursor()
		
		table = self.artists_t
		# edit db
		data = []
		string = 'UPDATE ' +  table + ' SET '
		for key in key_data:
			if not key == 'nik_name':
				#print '*************', key, key_data[key], '\n'
				#string = string + ' ' + key + ' = \"' + key_data[key] + '\",'
				string = string + ' ' + key + ' = ? ,'
				data.append(key_data[key])
			
		# -- >>
		string = string + ' WHERE nik_name = \"' + key_data['nik_name'] + '\"'
		string = string.replace(', WHERE', ' WHERE')
		
		#print(string)
		#return(False, 'Be!')
		
		data = tuple(data)
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		return True, 'ok'
		
	def add_stat(self, user_name, keys):
		# test project_name
		try:
			project_name = keys['project_name']
		except:
			return False, 'not project_name'
		
		# test task_name
		try:
			task_name = keys['task_name']
		except:
			return False, 'not task_name'
		
		# test data_start
		try:
			data_start = keys['data_start']
		except:
			return False, 'not data_start'
		
		# create string
		table = '\"' + user_name + ':' + self.statistic_t + '\"'
		string = "insert into " + table + " values"
		values = '('
		data = []
		for i, key in enumerate(self.statistics_keys):
			if i< (len(self.statistics_keys) - 1):
				values = values + '?, '
			else:
				values = values + '?'
			if key[0] in keys:
				data.append(keys[key[0]])
			else:
				if key[1] == 'real':
					data.append(0.0)
				else:
					data.append('')
					
		values = values + ')'
		data = tuple(data)
		string = string + values
		
		# write task to db
		conn = sqlite3.connect(self.statistic_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# exists table
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			# unicum task_name test
			r = c.fetchall()
			for row in r:
				if row['task_name'] == keys['task_name']:
					conn.close()
					return False, 'overlap'
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key_ in enumerate(self.statistics_keys):
				if i == 0:
					string2 = string2 + key_[0] + ' ' + key_[1]
				else:
					string2 = string2 + ', ' + key_[0] + ' ' + key_[1]
			string2 = string2 + ')'
			#return string2
			c.execute(string2)
		
		# add task
		c.execute(string, data)
		conn.commit()
		conn.close()
		return True, 'ok'
	
	def read_stat(self, nik_name, keys):
		# create string
		table = '\"' + nik_name + ':' + self.statistic_t + '\"'
		
		if keys == 'all':
			string = 'select * from ' + table
		else:
			string = 'select * from ' + table + ' WHERE '
			for i,key in enumerate(keys):
				if key != 'nik_name':
					if i == 0:
						string = string + ' ' + key + ' = ' + '\"' + keys[key] + '\"'
					else:
						string = string + 'and ' + key + ' = ' + '\"' + keys[key] + '\"'
				
		#return string
				
		# read tasks
		conn = sqlite3.connect(self.statistic_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		'''	
		c.execute(string)
		rows = c.fetchall()
		'''
		try:
			c.execute(string)
			rows = c.fetchall()
		except:
			conn.close()
			return False, 'can_not_read_stat'
			
		conn.close()
		'''
		if not rows:
			return False, 'not_task_name'
		'''
						
		return True, rows
		
	def edit_stat(self, user_name, project_name, task_name, keys):
		# create string	
		table = '\"' + user_name + ':' + self.statistic_t + '\"'
		# edit db
		string = 'UPDATE ' +  table + ' SET '
		for key in keys:
			if (key != 'project_name') and (key != 'task_name'):
				string = string + ' ' + key + ' = \"' + keys[key] + '\",'
			
		# -- >>
		string = string + ' WHERE project_name = \"' + project_name + '\" and task_name = \"' + task_name + '\"'
		string = string.replace(', WHERE', ' WHERE')
		#return string
		
		# write task to db
		conn = sqlite3.connect(self.statistic_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		c = conn.cursor()
		'''
		c.execute(string)
		'''
		try:
			c.execute(string)
		except:
			conn.close()
			return False, 'can_not_execute_stat'
		
		conn.commit()
		conn.close()
		
		return True, 'ok'
		
class workroom(artist):
	def __init__(self):
		artist.__init__(self)
	
	def add(self, keys):
		# test name
		try:
			name = keys['name']
		except:
			return(False, 'not Name!')
			
		keys['id'] = str(random.randint(0, 1000000000))
		
		# connect to db
		if not self.workroom_path:
			self.get_studio()
			
		conn = sqlite3.connect(self.workroom_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# exists table, name, id
		table = self.workroom_t
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			# unicum workroom_name test
			r = c.fetchall()
			for row in r:
				if row['name'] == keys['name']:
					conn.close()
					return(False, 'overlap')
				elif row['id'] == keys['id']:
					keys['id'] = str(random.randint(0, 1000000000))
					
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key in enumerate(self.workroom_keys):
				if i == 0:
					string2 = string2 + key[0] + ' ' + key[1]
				else:
					string2 = string2 + ', ' + key[0] + ' ' + key[1]
			string2 = string2 + ")"
			c.execute(string2)
		
		# create string
		string = "insert into " + table + " values"
		values = "("
		data = []
		for i, key in enumerate(self.workroom_keys):
			if i< (len(self.workroom_keys) - 1) and (len(keys) > 1):
				values = values + '?, '
			else:
				values = values + '?'
			if key[0] in keys:
				data.append(keys[key[0]])
			else:
				if key[1] == 'real':
					data.append(0.0)
				elif key[1] == 'timestamp':
					data.append(datetime.datetime.now())
				else:
					data.append("")
					
		values = values + ")"
		data = tuple(data)
		string = string + values
		'''
		print(string, data)
		return(False, 'Be!')
		'''
		# add workroom
		c.execute(string, data)
		conn.commit()
		conn.close()
		return(True, 'ok')
		
	def get_list_workrooms(self, DICTONARY = False):
		table = self.workroom_t
		
		if not self.workroom_path or (not os.path.exists(self.workroom_path)):
			return(False, 'Not Found WorkRoom Data Base!')
		
		conn = sqlite3.connect(self.workroom_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		str_ = 'select * from ' + table
		try:
			c.execute(str_)
		except:
			return(False, 'WorkRoom Table Not Found!')
		# unicum workroom_name test
		rows = c.fetchall()
		return_data_0 = {}
		return_data_1 = []
		return_data_2 = {}
		for row in rows:
			#return_data['name'] = row['name']
			work_room_data = {}
			work_room_data_1 = {}
			work_room_data_2 = {}
			for key in row.keys():
				work_room_data_1[key] = row[key]
				#print(key)
				#continue
				if key != 'name':
					work_room_data[key] = row[key]
				if key != 'id':
					work_room_data_2[key] = row[key]
			return_data_0[row['name']] = work_room_data
			return_data_1.append(work_room_data_1)
			return_data_2[row['id']] = work_room_data_2
		
		conn.close()
		if not DICTONARY:
			return(True, return_data_1)
		elif DICTONARY == 'by_name':
			return(True, return_data_0)
		elif DICTONARY == 'by_id':
			return(True, return_data_2)
		elif DICTONARY == 'by_id_by_name':
			return(True, return_data_2, return_data_0)
		else:
			return(False, ('Incorrect DICTONARY: ' + DICTONARY))
	
	
	def get_name_by_id(self, id_):
		table = self.workroom_t
		
		if not self.workroom_path or (not os.path.exists(self.workroom_path)):
			return(False, 'Not Found WorkRoom Data Base!')
		
		conn = sqlite3.connect(self.workroom_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		str_ = 'select * from ' + table
		return_data = ''
		try:
			c.execute(str_)
			rows = c.fetchall()
			for row in rows:
				if row['id'] == id_:
					return_data = row['name']
					break
		except:
			conn.close()
			return(False, 'Table Not Found!')
			
		if return_data:
			conn.close()
			return(True, return_data)
		else:
			conn.close()
			return(False, 'Not workroom Id')
	
	def get_id_by_name(self, name):
		table = self.workroom_t
		
		if not self.workroom_path or (not os.path.exists(self.workroom_path)):
			return(False, 'Not Found WorkRoom Data Base!')
		
		conn = sqlite3.connect(self.workroom_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		str_ = 'select * from ' + table
		return_data = ''
		try:
			c.execute(str_)
			rows = c.fetchall()
			for row in rows:
				if row['name'] == name:
					return_data = row['id']
					break
		except:
			conn.close()
			return(False, 'Table Not Found!')
			
		if return_data:
			conn.close()
			return(True, return_data)
		else:
			conn.close()
			return(False, 'Not workroom Name')
			
	def name_list_to_id_list(self, name_list):
		table = self.workroom_t
		
		if not self.workroom_path or (not os.path.exists(self.workroom_path)):
			return(False, 'Not Found WorkRoom Data Base!')
		
		conn = sqlite3.connect(self.workroom_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		str_ = 'select * from ' + table
		return_data = []
		try:
			c.execute(str_)
			rows = c.fetchall()
			for row in rows:
				if row['name'] in name_list:
					return_data.append(row['id'])
		except:
			conn.close()
			return(False, 'Table Not Found!')
			
		if return_data:
			conn.close()
			return(True, return_data)
		else:
			conn.close()
			return(False, 'Not workroom Names')
			
	def id_list_to_name_list(self, id_list):
		table = self.workroom_t
		
		if not self.workroom_path or (not os.path.exists(self.workroom_path)):
			return(False, 'Not Found WorkRoom Data Base!')
		
		conn = sqlite3.connect(self.workroom_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		str_ = 'select * from ' + table
		return_data = []
		try:
			c.execute(str_)
			rows = c.fetchall()
			for row in rows:
				if row['id'] in id_list:
					return_data.append(row['name'])
		except:
			conn.close()
			return(False, 'Table Not Found!')
			
		if return_data:
			conn.close()
			return(True, return_data)
		else:
			conn.close()
			return(False, 'Not workrooms by list id')
			
	def rename_workroom(self, old_name, new_name):
		new_name = new_name.replace(' ', '_')
		
		if old_name == new_name:
			return(False, 'Match names!')
		
		result = self.get_id_by_name(old_name)
		if not result[0]:
			return(False, result[1])
			
		wr_id = result[1]
		
		# connect to db
		table = self.workroom_t
		
		print(old_name, new_name, wr_id, table)
		
		if not self.workroom_path or (not os.path.exists(self.workroom_path)):
			return(False, 'Not Found WorkRoom Data Base!')
		
		conn = sqlite3.connect(self.workroom_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# write data
		string = 'UPDATE ' + table + ' SET name = ? WHERE id = ?'
		data = (new_name, wr_id)
		c.execute(string, data)
		
		conn.commit()
		conn.close()
		
		return(True, 'Ok!')
		
	
class chat(task):
	'''
	self.record_messages(project_name, task_name, topic) - records topic to '.chats.db';; topic = dumps({line1:(img, img_icon, text), ...})
	
	self.read_the_chat(self, project_name, task_name, reverse = 0) - It returns a list of all messages for a given task;;
	'''
	def __init__(self):
		task.__init__(self)
	
	#def record_messages(self, project_name, task_name, author, color, topic, status, date_time = ''):
	def record_messages(self, project_name, task_name, input_keys):
		# test project
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		'''	
		# get date time
		if date_time == '' or type(date_time) != datetime.datetime:
			date_time = datetime.datetime.now()
		'''
		
		# create string  timestamp
		table = '\"' + task_name + '\"'
		string = "insert into " + table + " values("
		data = []
		for i, key in enumerate(self.chats_keys):
			# -- string
			if i == 0:
				string = string + '?'
			else:
				string = string + ',?'
			
			# -- data
			if key[0] in input_keys.keys():
				data.append(input_keys[key[0]])
			else:
				if key[1] == 'text':
					data.append('')
				elif key[1] == 'real':
					data.append(0.0)
				elif key[1] == 'timestamp':
					data.append(datetime.datetime.now())
				
			
		string = string + ')'
		data = tuple(data)
		
		# connect to self.chat_path
		conn = sqlite3.connect(self.chat_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		#conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# exists or create table
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key in enumerate(self.chats_keys):
				if i == 0:
					string2 = string2 + key[0] + ' ' + key[1]
				else:
					string2 = string2 + ', ' + key[0] + ' ' + key[1]
			string2 = string2 + ')'
			#return string2
			c.execute(string2)
	
		# add topic
		#print(string, data)
		#return
		c.execute(string, data)
		conn.commit()
		conn.close()
		return(True, 'ok')
	
	def read_the_chat(self, project_name, task_name, reverse = 0):
		# test project
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
		
		table = '\"' + task_name + '\"'
		
		# connect to self.chat_path
		'''
		conn = sqlite3.connect(self.chat_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		'''
		try:
			conn = sqlite3.connect(self.chat_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return False, '".chats.db" not Connect!'
		
		# read the topic
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			rows = c.fetchall()
			
		except:
			conn.close()
			return False, ('topic with name ' + table + ' not Found!')
		
		conn.close()
		
		return True, rows
		
	def task_edit_rid_status_unread(self, project_name, task_data):
		# test project
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
		data = (task_data['task_name'],)
		
		# connect db
		try:
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, 'in task_edit_rid_status_unread - not connect db!')
		
		# read-edit data
		c.execute(string, data)
		task_data = dict(c.fetchone())
		try:
			readers = json.loads(task_data['readers'])
			for nik_name in readers:
				readers[nik_name] = 0
			task_data['chat_local'] = json.dumps(readers)
		except:
			task_data['chat_local'] = json.dumps({})
			
		# write data
		string = 'UPDATE ' + table + 'SET chat_local = ? WHERE task_name = ?'
		data = (task_data['chat_local'], task_data['task_name'])
		c.execute(string, data)
		
		conn.commit()
		conn.close()
		
		return(True, 'Ok!')
	
	def task_edit_rid_status_read(self, project_name, task_data, nik_name):
		# test project
		result = self.get_project(project_name)
		if not result[0]:
			return(False, result[1])
			
		table = '\"' + task_data['asset_id'] + ':' + self.tasks_t + '\"'
		string = 'SELECT * FROM ' + table + ' WHERE task_name = ?'
		data = (task_data['task_name'],)
		
		# connect db
		try:
			conn = sqlite3.connect(self.tasks_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			return(False, 'in task_edit_rid_status_unread - not connect db!')
		
		# read-edit data
		c.execute(string, data)
		task_data = dict(c.fetchone())
		
		readers2 = {}
		try:
			readers2 = json.loads(task_data['chat_local'])
			readers2[nik_name] = 1
		except:
			readers2[nik_name] = 1
		task_data['chat_local'] = json.dumps(readers2)
		
		# write data
		string = 'UPDATE ' + table + 'SET chat_local = ? WHERE task_name = ?'
		data = (task_data['chat_local'], task_data['task_name'])
		c.execute(string, data)
		
		conn.commit()
		conn.close()
		
		return(True, 'Ok!')
	
	def edit_message(self, project_name, task_name, keys):
		pass
	
class set_of_tasks(studio):
	def __init__(self):
		# keys = ('asset_type', 'sets')
		
		self.set_of_tasks_keys = [
		'task_name',
		'input',
		'activity',
		'workroom',
		'tz',
		'cost',
		'standart_time',
		'task_type',
		'extension',
		]
		
		studio.__init__(self)
	
	def create(self, name, asset_type):
		# test data
		if name == '':
			return(False, 'Not Name!')
		
		# test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
		
		# read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
								
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
			
		# test exists of set
		if name in data.keys():
			return(False, 'This Set Already Exists!')
			
		# edit data
		data[name] = {}
		data[name]['asset_type'] = asset_type
		data[name]['sets'] = {}

		# write data
		try:
			with open(self.set_of_tasks_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				#print('data:', data)
				f.close()
		except:
			return(False, (self.set_of_tasks_path + "  can not be write"))
		
		return(True, 'ok')
	
	def get_list(self, path = False):
		if not path:
			# test exists path
			if not self.set_of_tasks_path:
				#self.get_set_of_tasks_path()
				self.get_studio()
				
			if not os.path.exists(self.set_of_tasks_path):
				return(False, (self.set_of_tasks_path + ' Not Found!'))
				
			# read data
			try:
				with open(self.set_of_tasks_path, 'r') as read:
					data = json.load(read)
					read.close()
			except:
				return(False, (self.set_of_tasks_path + " can not be read!"))
				
		else:
			if not os.path.exists(path):
				return(False, ('No Exists path: ' + path))
			# read data
			try:
				with open(path, 'r') as read:
					data = json.load(read)
					read.close()
			except:
				return(False, (self.set_of_tasks_path + " can not be read!"))
			
		return(True, data)
		
	def get_list_by_type(self, asset_type):
		result = self.get_list()
		if not result[0]:
			return(False, result[1])
		
		return_list = {}
		for key in result[1]:
			if result[1][key]['asset_type'] == asset_type:
				return_list[key] = result[1][key]
				
		return(True, return_list)
		
	def get_dict_by_all_types(self):
		result = self.get_list()
		if not result[0]:
			return(False, result[1])
		
		return_list = {}
		for key in result[1]:
			asset_type = result[1][key]['asset_type']
			if not asset_type in return_list:
				return_list[asset_type] = {}
			
			return_list[asset_type][key] = result[1][key]
				
		return(True, return_list)
	
	def get(self, name):
		# test data
		if name == '':
			return(False, 'Not Name!')
			
		# test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
			
		# read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
			
		if not name in data:
			return(False, ('Set with name \"' + name + '\" Not Found!'))
		
		return(True, data[name]) # list of dictionaries
			
	
	def remove(self, name):
		# test data
		if name == '':
			return(False, 'Not Name!')
			
		# test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
			
		# read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
			
		if not name in data:
			return(False, ('Set with name \"' + name + '\" Not Found!'))
		
		# del data
		del data[name]
		
		# write data
		try:
			with open(self.set_of_tasks_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				#print('data:', data)
				f.close()
		except:
			return(False, (self.set_of_tasks_path + "  can not be write"))
			
		return(True, 'ok')
	
	def rename(self, name, new_name):
		# test data
		if name == '' or new_name == '':
			return(False, 'Not Name!')
			
		# test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
			
		# read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
			
		# test exists of set
		if not name in data.keys():
			return(False, ('Set With Name \"' + name + '\" Not Found!'))
			read.close()
		
		# del data
		keys = data[name]
		del data[name]
		data[new_name] = keys
		
		# write data
		try:
			with open(self.set_of_tasks_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				#print('data:', data)
				f.close()
		except:
			return(False, (self.set_of_tasks_path + "  can not be write"))
			
		return(True, 'ok')
		
	def edit_asset_type(self, name, asset_type):
		# test data
		if name == '':
			return(False, 'Not Name!')
			
		# test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
			
		# read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
			
		# edit data
		data[name]['asset_type'] = asset_type
		
		# write data
		try:
			with open(self.set_of_tasks_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, (self.set_of_tasks_path + "  can not be write"))
		
		return(True, 'ok')
	
	def edit(self, name, keys):
		# test data
		if name == '':
			return(False, 'Not Name!')
		
		# test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
		
		# read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
								
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
		
		# test exists of set
		if not name in data.keys():
			return(False, ('Set With Name \"' + name + '\" Not Found!'))
			read.close()
		
		# edit data
		data[name]['sets'] = keys

		# write data
		try:
			with open(self.set_of_tasks_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, (self.set_of_tasks_path + "  can not be write"))
		
		return(True, 'ok')
		
	### ****************** Library
	
	def save_set_of_tasks_to_library(self, path):
		# Read Data
		## -- test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
		## -- read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
			
		# Write Data
		try:
			with open(path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, (path + "  can not be write"))
		
		return(True, 'ok')
		
	def load_set_of_tasks_from_library(self, load_data):
		# Read Data
		## -- test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
		## -- read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
		
		# Edit Data
		for key in load_data:
			data[key] = load_data[key]
		
		
		# Write Data
		try:
			with open(self.set_of_tasks_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, (self.set_of_tasks_path + "  can not be write"))
		
		return(True, 'ok')
		
	def copy_set_of_tasks(self, old_name, new_name):
		# Read Data
		## -- test exists path
		if not os.path.exists(self.set_of_tasks_path):
			return(False, (self.set_of_tasks_path + ' Not Found!'))
		## -- read data
		try:
			with open(self.set_of_tasks_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.set_of_tasks_path + " can not be read!"))
			
		# Edit Data
		data[new_name] = data[old_name]
		
		# Write Data
		try:
			with open(self.set_of_tasks_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				f.close()
		except:
			return(False, (self.set_of_tasks_path + "  can not be write"))
		
		return(True, 'Ok!')
		
class series(project):
	def __init__(self):
		self.series_keys = [
		('name', 'text'),
		('status','text'),
		('id', 'text'),
		]
		
		self.series_t = 'series'
		
		project.__init__(self)
		
	def create(self, project, name):
		result = self.get_project(project)
		if not result[0]:
			return(False, result[1])
			
		
		
		keys = {}
		keys['name'] = name
		keys['status'] = 'active'
		keys['id'] = str(random.randint(0, 1000000000))
		
		# create string
		table = self.series_t
		string = "insert into " + table + " values"
		values = '('
		data = []
		for i, key in enumerate(self.series_keys):
			if i< (len(self.series_keys) - 1):
				values = values + '?, '
			else:
				values = values + '?'
			if key[0] in keys:
				data.append(keys[key[0]])
			else:
				if key[1] == 'real':
					data.append(0.0)
				elif key[1] == 'timestamp':
					data.append(datetime.datetime.now())
				else:
					data.append('')
					
		values = values + ')'
		data = tuple(data)
		string = string + values
		
		# write series to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# exists table
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			# unicum task_name test
			r = c.fetchall()
			for row in r:
				if row['name'] == keys['name']:
					conn.close()
					return(False, 'overlap')
				elif row['id'] == keys['id']:
					keys['id'] = str(random.randint(0, 1000000000))
				
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key in enumerate(self.series_keys):
				if i == 0:
					string2 = string2 + key[0] + ' ' + key[1]
				else:
					string2 = string2 + ', ' + key[0] + ' ' + key[1]
			string2 = string2 + ')'
			'''
			# -- 
			print 'String 2: ', string2
			conn.close()
			return
			# --
			'''
			c.execute(string2)
		
		# add series
		c.execute(string, data)
		conn.commit()
		conn.close()
		return(True, 'ok')
	
	def get_list(self, project):
		result = self.get_project(project)
		if not result[0]:
			return(False, result[1])
		
		# write series to db
		try:
			conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			print(self.assets_path)
			return(False, ('Not Open .db' + self.assets_path))
		
		try:
			table = self.series_t
			str_ = 'select * from ' + table
			c.execute(str_)
			rows = c.fetchall()
			return(True, rows)
		except:
			conn.close()
			return(False, 'Not Table!')
			
		
	
	def get_by_name(self, project, name):
		result = self.get_project(project)
		if not result[0]:
			return(False, result[1])
		
		# write series to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		try:
			table = self.series_t
			str_ = 'select * from ' + table
			c.execute(str_)
			rows = c.fetchall()
			for row in rows:
				if row['name'] == name:
					return(True, row)
			return(False, 'Not Found Series!')
		except:
			conn.close()
			return(False, 'Not Table!')
	
	def get_by_id(self, project, id_):
		result = self.get_project(project)
		if not result[0]:
			return(False, result[1])
		
		# write series to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		try:
			table = self.series_t
			str_ = 'select * from ' + table
			c.execute(str_)
			rows = c.fetchall()
			for row in rows:
				if row['id'] == id_:
					return(True, row)
			return(False, 'Not Found Series!')
		except:
			conn.close()
			return(False, 'Not Table!')
	
	def rename(self, project, name, new_name):
		result = self.get_project(project)
		if not result[0]:
			return(False, result[1])
			
		# write task to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		table = self.series_t
		
		# test old name exists
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			r = c.fetchall()
			
			names = []
			for row in r:
				names.append(row['name'])
			
			if not name in names:
				conn.close()
				return(False, 'Old Name Not Exists!')
		
		except:
			conn.close()
			return(False, 'Not Table!')
		
		
		# edit db
		string = 'UPDATE ' +  table + ' SET  \"name\"  = ? WHERE \"name\" = \"' + name + '\"'
				
		data = (new_name,)
		'''
		print(string, data)
		conn.close()
		return(False, 'Be!')
		'''
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		return(True, 'ok')
	
	def stop(self, project, name):
		pass
	
	def start(self, project, name):
		pass
	
class group(project):
	def __init__(self):
		self.group_keys = [
		('name', 'text'),
		('type', 'text'),
		('series', 'text'),
		('comment', 'text'),
		('id', 'text'),
		]
		
		self.group_t = 'groups'
		
		project.__init__(self)
	
	def create(self, project, keys):
		result = self.get_project(project)
		if not result[0]:
			return(False, result[1])
			
		# test name
		if (not 'name' in keys) or (keys['name'] == ''):
			return(False, 'Not Name!')
			
		# test type
		# test name
		if (not 'type' in keys) or (keys['name'] == '') or (not keys['type'] in self.asset_types):
			return(False, 'Not Type!')
		
		# get id				
		keys['id'] = str(random.randint(0, 1000000000))
		
		# test series key
		if keys['type'] in self.asset_types_with_series:
			if 'series' in keys and keys['series'] == '':
				return(False, 'For This Type Must Specify a Series!')
			elif not 'series' in keys:
				return(False, 'Required For This Type of Key Series!')
		else:
			keys['series'] = ''
		
		# create string
		table = self.group_t
		string = "insert into " + table + " values"
		values = '('
		data = []
		for i, key in enumerate(self.group_keys):
			if i< (len(self.group_keys) - 1):
				values = values + '?, '
			else:
				values = values + '?'
			if key[0] in keys:
				data.append(keys[key[0]])
			else:
				if key[1] == 'real':
					data.append(0.0)
				elif key[1] == 'timestamp':
					data.append(datetime.datetime.now())
				else:
					data.append('')
					
		values = values + ')'
		data = tuple(data)
		string = string + values
		
		# write group to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		# exists table
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			# unicum task_name test
			r = c.fetchall()
			for row in r:
				if row['name'] == keys['name']:
					conn.close()
					return(False, 'overlap')
				elif row['id'] == keys['id']:
					keys['id'] = str(random.randint(0, 1000000000))
				
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key in enumerate(self.group_keys):
				if i == 0:
					string2 = string2 + key[0] + ' ' + key[1]
				else:
					string2 = string2 + ', ' + key[0] + ' ' + key[1]
			string2 = string2 + ')'
			'''
			# -- 
			print 'String 2: ', string2
			conn.close()
			return
			# --
			'''
			c.execute(string2)
		
		# add series
		#print(string, data)
		c.execute(string, data)
		conn.commit()
		conn.close()
		return(True, 'ok')
		
	def create_recycle_bin(self, project_name):
		'''
		result = self.get_studio()
		if not result[0]:
			return(False, (result[1] + ' in get studio'))
		
		result = self.get_project(project_name)
		if not result[0]:
			return(False, (result[1] + ' in get project'))
		'''
		# get group list
		result = self.get_list(project_name)
		if not result[0]:
			return(False, (result[1] + ' in get group list'))
		groups = result[1]
		
		all_group = False
		recycle_bin = False
		names = []
		id_s = []
		if groups:
			for group in groups:
				names.append(group['name'])
				id_s.append(group['id'])
				if group['name'] == self.recycle_bin_name:
					recycle_bin = group
				if group['type'] == 'all':
					all_group = group
				
		if not all_group:
			#print('Not ALL type')
			# rename
			if recycle_bin:
				#print('Exist RB name')
				# -- new name
				new_name = self.recycle_bin_name + hex(random.randint(0, 1000000000)).replace('0x','')
				while new_name in names:
					new_name = self.recycle_bin_name + hex(random.randint(0, 1000000000)).replace('0x','')
				# -- rename
				result = self.rename(project_name, self.recycle_bin_name, new_name)
				if not result[0]:
					return(False, result[1])
				
			# create group
			# -- keys
			keys = {
			'name':self.recycle_bin_name,
			'type': 'all',
			'comment':'removed assets'
			}
			# -- get id
			keys['id'] = hex(random.randint(0, 1000000000)).replace('0x','')
			while keys['id'] in id_s:
				keys['id'] = hex(random.randint(0, 1000000000)).replace('0x','')
			#print(keys)
			
			# -- create string
			table = self.group_t
			string = "insert into " + table + " values"
			values = '('
			data = []
			for i, key in enumerate(self.group_keys):
				if i< (len(self.group_keys) - 1):
					values = values + '?, '
				else:
					values = values + '?'
				if key[0] in keys:
					data.append(keys[key[0]])
				else:
					if key[1] == 'real':
						data.append(0.0)
					elif key[1] == 'timestamp':
						data.append(datetime.datetime.now())
					else:
						data.append('')
						
			values = values + ')'
			data = tuple(data)
			string = string + values
				
			# CONNECT to db
			conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
			
			# exists table
			try:
				str_ = 'select * from ' + table
				c.execute(str_)
			except:
				string2 = "CREATE TABLE " + table + " ("
				for i,key in enumerate(self.group_keys):
					if i == 0:
						string2 = string2 + key[0] + ' ' + key[1]
					else:
						string2 = string2 + ', ' + key[0] + ' ' + key[1]
				string2 = string2 + ')'
				# -- make table
				c.execute(string2)
							
			# -- create group
			c.execute(string, data)
			conn.commit()
			conn.close()
			
		else:
			#print('Exist RB!')
			if not recycle_bin:
				# -- rename
				result = self.rename(project_name, all_group['name'], self.recycle_bin_name)
				if not result[0]:
					return(False, (result[1] + 'in rename rcycle bin'))
			
		return(True, 'ok')
			
		
	def get_list(self, project, f = False): # f = [...] - filter of types
		result = self.get_project(project)
		if not result[0]:
			return(False, (result[1] + '***'))
		
		# write series to db
		try:
			conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
			conn.row_factory = sqlite3.Row
			c = conn.cursor()
		except:
			print(self.assets_path)
			return(False, ('Not Open .db' + self.assets_path))
		
		try:
			table = self.group_t
			str_ = 'select * from ' + table
			c.execute(str_)
			rows = c.fetchall()
			conn.close()
			if not f:
				return(True, rows)
			else:
				f_rows = []
				for row in rows:
					if row['type'] in f:
						f_rows.append(row)
				return(True, f_rows)
		except:
			string2 = "CREATE TABLE " + table + " ("
			for i,key in enumerate(self.group_keys):
				if i == 0:
					string2 = string2 + key[0] + ' ' + key[1]
				else:
					string2 = string2 + ', ' + key[0] + ' ' + key[1]
			string2 = string2 + ')'
			# -- make table
			try:
				c.execute(string2)
				conn.commit()
				conn.close()
				return(True, [])
			except:
				conn.close()
				return(False, 'Not found or created!')
							
		'''
		table = self.group_t
		str_ = 'select * from ' + table
		c.execute(str_)
		rows = c.fetchall()
		conn.close()
		return(True, rows)
		'''
	
	def get_groups_dict_by_id(self, project):
		result = self.get_list(project)
		if not result[0]:
			return(False, result[1])
		
		group_dict = {}
		for row in result[1]:
			group_dict[row['id']] = row
			
		return(True, group_dict)
	
	def get_by_keys(self, project, keys):
		result = self.get_project(project)
		if not result[0]:
			return(False, result[1])
		
		if len(keys) == 0:
			return(False, 'Not Keys!')
		
		# write series to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		try:
			data = []
			table = self.group_t
			string = 'select * from ' + table + ' WHERE '
			for i,key in enumerate(keys):
				if i == 0:
					string = string + ' ' + key + ' = ' + '?'
				else:
					string = string + 'and ' + key + ' = ' + '?'
				data.append(keys[key])	
			
			data = tuple(data)
			c.execute(string, data)
			rows = c.fetchall()
			conn.close()
			return(True, rows)
		
		except:
			conn.close()
			return(False, 'Not Table!')
		
	
	def get_by_name(self, project, name):
		rows = self.get_by_keys(project, {'name': name})
		if rows[0]:
			return(True, rows[1][0])
		else:
			return(False, rows[1])
	
	def get_by_id(self, project, id_):
		rows = self.get_by_keys(project, {'id': id_})
		if rows[0]:
			return(True, rows[1][0])
		else:
			return(False, rows[1])
	
	def get_by_series(self, project, series):
		rows = self.get_by_keys(project, {'series': series})
		if rows[0]:
			return(True, rows[1])
		else:
			return(False, rows[1])
	
	def get_by_type_list(self, project, type_list):
		result = self.get_project(project)
		if not result[0]:
			return(False, result[1])
		
		data = []
		for type_ in type_list:
			rows = self.get_by_keys(project, {'type':type_})
			if rows[0]:
				data = data + rows[1]
				
		return(True, data)
		
	def get_dict_by_all_types(self, project):
		result = self.get_project(project)
		if not result[0]:
			return(False, result[1])
		
		# get all group data
		result = self.get_list(project)
		if not result[0]:
			return(False, result[1])
		
		# make data
		data = {}
		for group in result[1]:
			if not group['type'] in data.keys():
				c_data = []
			else:
				c_data = data[group['type']]
			c_data.append(group)
			data[group['type']] = c_data
			
		return(True, data)
	
	def rename(self, project, name, new_name):
		result = self.get_project(project)
		if not result[0]:
			return(False, (result[1] + ' <in rename>'))
			
		# write task to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		table = self.group_t
		
		# test old name exists
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			r = c.fetchall()
			
			names = []
			for row in r:
				names.append(row['name'])
			
			if not name in names:
				conn.close()
				return(False, 'Old Name Not Exists!')
		
		except:
			conn.close()
			return(False, 'Not Table!')
		
						
		# edit db
		string = 'UPDATE ' +  table + ' SET  \"name\"  = ? WHERE \"name\" = \"' + name + '\"'
				
		data = (new_name,)
		'''
		print(string, data)
		conn.close()
		return(False, 'Be!')
		'''
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		return(True, 'ok')
		
	def edit_comment_by_name(self, project, name, comment):
		result = self.get_project(project)
		if not result[0]:
			return(False, result[1])
			
		# write task to db
		conn = sqlite3.connect(self.assets_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		
		table = self.group_t
		
		# test old name exists
		try:
			str_ = 'select * from ' + table
			c.execute(str_)
			r = c.fetchall()
			
			names = []
			for row in r:
				names.append(row['name'])
			
			if not name in names:
				conn.close()
				return(False, 'Name Not Exists!')
		
		except:
			conn.close()
			return(False, 'Not Table!')
			
		# edit db
		string = 'UPDATE ' +  table + ' SET  \"comment\"  = ? WHERE \"name\" = \"' + name + '\"'
				
		data = (comment,)
		'''
		print(string, data)
		conn.close()
		return(False, 'Be!')
		'''
		c.execute(string, data)
		conn.commit()
		conn.close()
		
		return(True, 'ok')
		
class list_of_assets(group):
	def __init__(self):
		self.list_of_assets_keys = [
		'asset_name',
		'asset_type',
		'set_of_tasks',
		]
		
		group.__init__(self)
		
	def save_list(self, project, group_name, rows): # rows = [{keys}, {keys}, ...]
		get_project = self.get_project(project)
		if not get_project[0]:
			return(False, get_project[1])
		
			# test data keys
		if group_name == '':
			return(False, 'Not Name!')
		
		# test exists path
		if not os.path.exists(self.list_of_assets_path):
			print(get_project[1][0])
			return(False, (self.list_of_assets_path + ' Not Found! ***'))
		
		# read data
		try:
			with open(self.list_of_assets_path, 'r') as read:
				data = json.load(read)
				read.close()
								
		except:
			return(False, (self.list_of_assets_path + " can not be read!"))
		
		'''
		# test exists of set
		if group_name in data.keys():
			return(False, 'This Set Already Exists!')
		'''
			
		# edit data
		data[group_name] = rows
		
		# write data
		try:
			with open(self.list_of_assets_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				#print('data:', data)
				f.close()
		except:
			return(False, (self.list_of_assets_path + "  can not be write"))
		
		return(True, 'ok')
		
	def get_list(self, project):
		get_project = self.get_project(project)
		if not get_project[0]:
			return(False, get_project[1])
			
		# test exists path
		if not os.path.exists(self.list_of_assets_path):
			return(False, (self.list_of_assets_path + ' Not Found!'))
		
		# read data
		try:
			with open(self.list_of_assets_path, 'r') as read:
				data = json.load(read)
				read.close()
								
		except:
			return(False, (self.list_of_assets_path + " can not be read!"))
			
		return(True, data)
		
	def get(self, project, group_name):
		get_project = self.get_project(project)
		if not get_project[0]:
			return(False, get_project[1])
			
		# test exists path
		if not os.path.exists(self.list_of_assets_path):
			return(False, (self.list_of_assets_path + ' Not Found!'))
		
		# read data
		try:
			with open(self.list_of_assets_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.list_of_assets_path + " can not be read!"))
		
		if group_name in data:
			return(True, data[group_name])
		else:
			return(False, ('list of assets for \"' + group_name + '\" not found!'))
		
		
	def remove(self, project, group_name):
		get_project = self.get_project(project)
		if not get_project[0]:
			return(False, get_project[1])
		
		# test exists path
		if not os.path.exists(self.list_of_assets_path):
			return(False, (self.list_of_assets_path + ' Not Found!'))
			
		# read data
		try:
			with open(self.list_of_assets_path, 'r') as read:
				data = json.load(read)
				read.close()
		except:
			return(False, (self.list_of_assets_path + " can not be read!"))
			
		if group_name in data:
			del data[group_name]
		else:
			return(False, ('list of assets for \"' + group_name + '\" not found!'))
			
		# write data
		try:
			with open(self.list_of_assets_path, 'w') as f:
				jsn = json.dump(data, f, sort_keys=True, indent=4)
				#print('data:', data)
				f.close()
		except:
			return(False, (self.list_of_assets_path + "  can not be write"))
			
		return(True, 'Ok')
		
		
	def create_assets(self, project, group):
		pass
	
