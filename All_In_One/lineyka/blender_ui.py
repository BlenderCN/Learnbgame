import bpy
import webbrowser
import json
import imp
import getpass
from functools import partial
import os
import shutil

# my modils
from .edit_db import studio
from .edit_db import artist
from .edit_db import task
from .edit_db import log
from .edit_db import chat
from .edit_db import group
from .edit_db import asset
from .edit_db import set_of_tasks

from .blender_func import functional

class G(object):
	# db objects
	db_studio = studio()
	db_artist = artist()
	db_task = task()
	db_log = log()
	db_chat = chat()
	db_group = group()
	db_asset = asset()
	db_set_of_tasks = set_of_tasks()
	
	# bf objects
	func = functional()
	
	# animatic
	name_text = 'Animatic_data'
	name_scene = 'Animatic'
	shot_name = 'Shot.001'
	#animatic_panel = False
	# other
	activate_task = None
	activate_reader_task = None
	current_content_data = None
	functional_panel = False
	read_func_panel = False
	look_version_panel = False
	camera_version_panel = False
	playblast_version_panel = False
	downloadable_group_panel = False
	tech_anim_group_panel = False
	rename_texts_panel = False
	tech_anim_set_position_panel = False
	tech_anim_version_cache_panel = False
	rig_version_technical_cache_panel = False
	removable_group_panel = False
	rename_group_panel = False
	outsource = False
	version = None
	preview_img = None
	preview_img_name = db_task.blend_service_images['preview_img_name']
	bg_image_name = db_task.blend_service_images['bg_image_name']
	#model_bg_image = 'Model_BG_Image'
	current_user = ''
	current_project = ''
	loaded_group_data = {}
	current_task = []
	working_task_list = []
	content_group_list = []
	versions_list = []
	camera_version_data_list = []
	playblast_version_data_list = []
	rig_version_technical_cache_list = []
	all_task_list = {}
	all_assets_data_by_name = {}
	tech_anim_obj_assets_list = (False, )
	tech_anim_char_assets_list = (False, )
	task_look_statuses = [
	'ready',
	'work',
	'pause',
	'recast',
	'checking',
	]
	work = 'work'
	read = 'read'
	user_text_name = 'current_task'
	'''
	task_using_types = [
	'sculpt',
	'model',
	'location_full',
	'location_for_anim',
	'animatic',
	'film',
	]
	'''
	group_list = [('--select group--',)*3] # groups of assets
	group_data_list = []
	set_of_tasks_list = [('--select Set_of_Tasks--',)*3]
	groups_list = [('--select group--',)*3] # groups of data bloks
	
	# load or open panel
	load_or_open_panel_group_list_vis = False
	load_or_open_panel_content_list_vis = False
	load_or_open_panel_content_list_of_group = None
	
	ext_dict = {}
	
	def get_ext_dict(self):
		G.ext_dict = {}
		result = G.db_studio.get_extension_dict()
		if result[0]:
			G.ext_dict = result[1]
	
	def get_user(self):
		result = G.db_artist.get_user(outsource = True)
		if result[0]:
			G.current_user = result[1][0]
			G.outsource = result[1][2]
			
	def get_task_list(self):
		# WORK LIST
		G.working_task_list = []
		result = G.db_task.get_task_list_of_artist(G.current_project, G.current_user)
		'''
		if not result[0]:
			G.task_list = []
			return(False, result[1])
		elif not result[1]:
			G.task_list = []
		elif len(result[1])== 0:
			G.task_list = []
		'''
		G.all_task_list = result[1]
		if result[0]:
			G.all_assets_data_by_name = result[2]
		for key in result[1]:
			if result[1][key]['task']['status'] in G.task_look_statuses:
				G.working_task_list.append(result[1][key]['task'])
				
		# READ LIST
		G.reader_task_list = []
		
		result, data = G.db_task.get_chek_list_of_artist(G.current_project, G.current_user)
		if result:
			G.reader_task_list = data
				
		return(True, 'Ok')
	
	# ----- group content -----
	
	def rebild_group_list(self):
		types_list = None
		if G.current_task:
			# get types list
			if G.current_task['asset_type'] in ['location']:
				types_list = ['char','obj']
			elif G.current_task['asset_type'] == 'film':
				types_list = ['shot_animation']
			else:
				types_list = ['char', 'obj']
		else:
			types_list = ['char', 'obj']
		
		# get group list
		result = G.db_group.get_by_type_list(G.current_project, types_list)
		
		# content group list
		G.loaded_group_data = {}
		zero_item = [('--select group--',)*3]
		if result[0]:
			groups_items = []
			G.group_data_list = result[1]
			for group in result[1]:
				if G.current_task and G.current_task['asset_type'] == 'film':
					if G.current_task['series'] != group['series']:
						continue
				groups_items.append((group['name'],)*3)
				G.loaded_group_data[group['name']] = group
			G.group_list = zero_item + groups_items
			set_group_list()
		else:
			print('\n','*'*25,'\n', result)
			
	def rebild_set_of_tasks_list(self):
		# get types list
		if G.current_task['asset_type'] in ['film']:
			types_list = ['shot_animation']
		else:
			types_list = ['shot_animation']
			
		G.set_of_tasks_list = [('--select Set_of_Tasks--',)*3]
			
		# get
		for asset_type in types_list:
			result = G.db_set_of_tasks.get_list_by_type(asset_type)
			if result[0]:
				for key in result[1].keys():
					G.set_of_tasks_list.append((key,)*3)
					
		set_set_of_tasks_list()
		
	def rebild_groups_list(self):
		G.groups_list = [('--select group--',)*3]
		
		for group_name in bpy.data.groups.keys():
			G.groups_list.append((group_name,)*3)
		
		set_groups_list()
				
			
	def get_content_list(self, group_name):
		content_list = []
		
		# get activity
		activity = None
		if G.loaded_group_data[group_name]['type'] == 'obj':
			activity = 'model'
		elif G.loaded_group_data[group_name]['type'] == 'char':
			activity = 'rig'
			
		# get assets list
		result = G.db_asset.get_list_by_group(G.current_project, G.loaded_group_data[group_name]['id'])
		if not result[0]:
			return(content_list)
		
		for asset in result[1]:
			# get task list
			task_list = G.db_task.get_list(G.current_project, asset['id'])
			if not task_list[0]:
				continue
			
			activity_tasks = []
			for task in task_list[1]:
				if task['activity'] == activity and task['status'] in G.db_asset.end_statuses:
					activity_tasks.append(task)
			
			for task in activity_tasks:
				if not task['input'] in activity_tasks:
					content_list.append(task)
					break
			
		return(content_list)
		

# ********** drop-down menu
def set_fields():
	bpy.types.Scene.lineyka_filter_by_name = bpy.props.StringProperty(name = 'Filter', update = None)
	
def set_activity_list():
	bpy.types.Scene.activity_enum = bpy.props.EnumProperty(items = [('--select activity--',)*3, ('model',)*3, ('rig',)*3], name = 'Activity', update = None)
	
def set_group_list():
	bpy.types.Scene.my_enum = bpy.props.EnumProperty(items = G.group_list, name = 'Groups', update = None)
	
def set_set_of_tasks_list():
	bpy.types.Scene.set_of_tasks_enum = bpy.props.EnumProperty(items = G.set_of_tasks_list, name = 'Set Of Tasks', update = None)

def set_groups_list():
	bpy.types.Scene.groups_enum = bpy.props.EnumProperty(items = G.groups_list, name = 'Groups:', update = None)
	
def set_tasks_list_type():
	type_list = [(G.work,G.work,G.work), (G.read,G.read,G.read)]
	bpy.types.Scene.tasks_list_type = bpy.props.EnumProperty(items = type_list, name = 'Type of List', update = None)
	
	
# ****** Panels ************
# ****** HELP
class Help(bpy.types.Panel):
	bl_idname = "lineyka.help_panel"
	bl_label = "Lineyka /// Help"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = 'Lineyka'
	layout = 'HELP'
	bl_options = {'DEFAULT_CLOSED'}
	
	def draw(self, context):
		layout = self.layout

		#layout.label("Help")
		col = layout.column(align=1)
		col.operator("lineyka.help",icon = 'QUESTION', text = 'Manual').action = 'manual'

# ****** SETTING
class Setting(bpy.types.Panel):
	bl_idname = "lineyka.setting_panel"
	bl_label = "Lineyka /// Setting"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = 'Lineyka'
	layout = 'SETTING'
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'setting_panel'

		#layout.label("Mesh Passport")
		col = layout.column(align=1)
		col.operator("lineyka.set_studio_folder",icon = 'NONE', text = 'Set Studio Folder').action = 'studio'
		col.operator("lineyka.set_studio_folder",icon = 'NONE', text = 'Set Tmp Folder').action = 'tmp'
		col.operator("lineyka.set_file_path",icon = 'NONE', text = 'Set Convert.exe path').action = 'convert'
		col.operator("lineyka.user_login", icon = 'NONE', text = "Login")
		col.operator("lineyka.user_registration", icon = 'NONE', text = "Registration")
		#col.operator("lineyka.edit_extensions_list", text = 'Edit Extensions list')

# ****** TASK_ LIST
class Tasks_Panel(bpy.types.Panel):
	bl_idname = "lineyka.task_list"
	bl_label = "Lineyka /// Task List"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = 'Lineyka'
	layout = 'TASKS'
	
	@classmethod
	def poll(self, context):
		if not G.current_user:
			G().get_user()
		if G.current_user:
			return True
		else:
			return False
    
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'task_list_panel'

		col = layout.column(align=0)
		col.label(('User: ' + G.current_user))
		col.label(('Project: ' + G.current_project))
		
		row = col.row(align = True)
		row.operator("lineyka.get_project",icon = 'NONE', text = '-- select project --')
		row.operator('lineyka.reload_task_list')
		
		layout.prop(context.scene, "tasks_list_type")
		
		if context.scene.tasks_list_type == G.work:
			col_tsk = layout.column(align=1)
			for task in G.working_task_list:
				task_data = task
				if task_data['extension'] != '.blend':
					continue
				if G.all_task_list[task_data['task_name']]['input']:
					task_data['input_activity'] = G.all_task_list[task_data['task_name']]['input']['activity']
				else:
					task_data['input_activity'] = ''
				icon = 'NONE'
				if task_data['status']== 'work':
					icon = 'PLUS'
				elif task_data['status']== 'recast':
					icon = 'AUTO'
				elif task_data['status']== 'checking':
					icon = 'LOCKED'
				
				row = col_tsk.row(align=True)
				if task_data['status']== 'checking':
					row.operator("lineyka.report",icon = icon, text = task_data['task_name']).action = ''
				else:
					row.operator("lineyka.task_distrib",icon = icon, text = task_data['task_name']).task_data = json.dumps(dict(task_data))
				# status_type
				#row.label(task_data['status'])
				row_ = row.row(align=True)
				row_.label(task_data['status'])
				row_.label(task_data['task_type'])
		
		elif context.scene.tasks_list_type == G.read:
			col = layout.column(align=1)
			for task_data in G.reader_task_list:
				if task_data['extension'] != '.blend':
					continue
				# get ICON
				icon = 'NONE'
				if task_data['status']== 'work':
					icon = 'PLUS'
				elif task_data['status']== 'recast':
					icon = 'AUTO'
				elif task_data['status']== 'checking':
					icon = 'LOCKED'
					
				# task row
				row = col.row(align=True)
				row.operator('lineyka.reader_task_distrib', text = task_data['task_name'], icon = icon).task_data = json.dumps(dict(task_data))
				row.label(task_data['status'])
				row.label(task_data['task_type'])

# ******** TASK_ DISTRIB
class DISTRIB_reader_task_panel(bpy.types.Panel):
	bl_label = 'Lineyka /// Task Operation:'
	bl_space_type = "VIEW_3D"
	#bl_region_type = "UI"
	bl_region_type = "TOOLS"
	bl_category = 'Lineyka'
	#layout = 'distrib_layout'
    
	@classmethod
	def poll(self, context):
		if G.activate_reader_task and context.scene.tasks_list_type == G.read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'task_operation_panel'
		row.operator("lineyka.help", icon = 'QUESTION', text = 'About Task Type').action = G.current_task['task_type']
		
		# task info data
		task_info = [
		('task name:',G.current_task['task_name']),
		('type:', G.current_task['task_type']),
		('activity:',G.current_task['activity']),
		#('input activity:', G.current_task['input_activity']),
		('status:',G.current_task['status']),
		('priority:',G.current_task['priority']),
		('price:',str(G.current_task['price']))
		]
		# task info layout
		col_info = layout.column(align=1)
		for key in task_info:
			row = col_info.row(align = 1)
			row.label(key[0])
			row.label(key[1])
			
		# BUTTONS
		row = layout.row()
		
		# look
		col = row.column(align=1)
		col.operator("lineyka.look", icon = 'NONE')
		col.operator("lineyka.look_version", icon = 'NONE').version = ''
		col.operator("lineyka.tz", icon = 'NONE')
		col.operator("lineyka.chat", icon = 'NONE')
		if 'sketch' in G.db_task.activity_folder[G.current_task['asset_type']].keys():
			col.operator("lineyka.look_sketch", icon = 'NONE')
			
		col = row.column(align=1)
		col.operator("lineyka.push", icon = 'NONE')
		col.operator("lineyka.accept_task", icon = 'NONE', text = 'Accept')
		col.operator("lineyka.to_rework_task", icon = 'NONE', text = 'To Rework')
		
class DISTRIB_reader_task_panel_sequence_editor(bpy.types.Panel):
	bl_label = 'Lineyka /// Task Operation:'
	bl_space_type = "SEQUENCE_EDITOR"
	bl_region_type = "UI"
	    
	@classmethod
	def poll(self, context):
		if G.activate_reader_task and context.scene.tasks_list_type == G.read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'task_operation_panel'
		row.operator("lineyka.help", icon = 'QUESTION', text = 'About Task Type').action = G.current_task['task_type']
		
		# task info data
		task_info = [
		('task name:',G.current_task['task_name']),
		('activity:',G.current_task['activity']),
		#('input activity:', G.current_task['input_activity']),
		('status:',G.current_task['status']),
		('priority:',G.current_task['priority']),
		('price:',str(G.current_task['price']))
		]
		# task info layout
		col_info = layout.column(align=1)
		for key in task_info:
			row = col_info.row(align = 1)
			row.label(key[0])
			row.label(key[1])
			
		# BUTTONS
		row = layout.row()
		
		# look
		col = row.column(align=1)
		col.operator("lineyka.look", icon = 'NONE')
		col.operator("lineyka.look_version", icon = 'NONE').version = ''
		col.operator("lineyka.tz", icon = 'NONE')
		col.operator("lineyka.chat", icon = 'NONE')
		if 'sketch' in G.db_task.activity_folder[G.current_task['asset_type']].keys():
			col.operator("lineyka.look_sketch", icon = 'NONE')
			
		col = row.column(align=1)
		col.operator("lineyka.push", icon = 'NONE')
		col.operator("lineyka.pass", icon = 'NONE', text = 'Accept')
		col.operator("lineyka.pass", icon = 'NONE', text = 'To Rework')
		

class DISTRIB_task_panel(bpy.types.Panel):
	bl_label = 'Lineyka /// Task Operation:'
	bl_space_type = "VIEW_3D"
	#bl_region_type = "UI"
	bl_region_type = "TOOLS"
	bl_category = 'Lineyka'
	#layout = 'distrib_layout'
	
	@classmethod
	def poll(self, context):
		if G.activate_task  and context.scene.tasks_list_type == G.work:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'task_operation_panel'
		row.operator("lineyka.help", icon = 'QUESTION', text = 'About Task Type').action = G.current_task['task_type']
		
		# task info data
		task_info = [
		('task name:',G.current_task['task_name']),
		('activity:',G.current_task['activity']),
		('input activity:', G.current_task['input_activity']),
		('status:',G.current_task['status']),
		('priority:',G.current_task['priority']),
		('price:',str(G.current_task['price']))
		]
		# task info layout
		col_info = layout.column(align=1)
		for key in task_info:
			row = col_info.row(align = 1)
			row.label(key[0])
			row.label(str(key[1]))
			
		# BUTTONS
		row = layout.row()
		
		# look
		col = row.column(align=1)
		col.operator("lineyka.look", icon = 'NONE')
		col.operator("lineyka.look_version", icon = 'NONE').version = ''
		col.operator("lineyka.tz", icon = 'NONE')
		col.operator("lineyka.chat", icon = 'NONE')
		if 'sketch' in G.db_task.activity_folder[G.current_task['asset_type']].keys():
			col.operator("lineyka.look_sketch", icon = 'NONE')
		
		# open
		col_open = row.column(align=1)
		col_open.operator("lineyka.open", icon = 'NONE').action = 'open'
		col_open.operator("lineyka.open_version", icon = 'NONE', text = 'Open Version').version = ''
		col_open.operator("lineyka.open", icon = 'NONE', text = 'Open From Input').action = 'from_input'
		col_open.operator("lineyka.open", icon = 'NONE', text = 'Current As Work').action = 'current'
	
	'''
	def invoke(self, context, event):
		context.scene.current_asset = G.current_task['asset']
		return{'FINISHED'}
	'''
		
# *********************** TASK_ FUNCTIONAL PANELS **************************************
# ********* ALL TASKS 
class FUNCTIONAL_tasks_wiew_3d(bpy.types.Panel):
	bl_label = 'Lineyka /// Task:'
	bl_space_type = "VIEW_3D"
	#bl_region_type = "UI"
	bl_region_type = "TOOLS"
	bl_category = 'Lineyka'
	#layout = 'distrib_layout'
    
	@classmethod
	def poll(self, context):
		#if G.functional_panel and not (G.current_task['task_type'] in G.task_using_types):
		if G.functional_panel:
			#G.activate_task = False
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'task_panel'
		row.operator("lineyka.help", icon = 'QUESTION', text = 'About Task Type').action = G.current_task['task_type']
		
		# task info data
		task_info = [
		('task name:',G.current_task['task_name']),
		('activity:',G.current_task['activity']),
		('input activity:',G.current_task['input_activity']),
		('status:',G.current_task['status']),
		('priority:',G.current_task['priority']),
		('price:',str(G.current_task['price'])),
		('task_type:',str(G.current_task['task_type']))
		]
		# task info layout
		col_info = layout.column(align=1)
		for key in task_info:
			row = col_info.row(align = 1)
			row.label(key[0])
			row.label(str(key[1]))
		
		row = layout.row()
		# tz chat
		col1 = row.column(align=1)
		col1.operator("lineyka.tz", icon = 'NONE')
		col1.operator("lineyka.chat", icon = 'NONE')
		if 'sketch' in G.db_task.activity_folder[G.current_task['asset_type']].keys():
			col1.operator("lineyka.look_sketch", icon = 'NONE')
		
		# push / report
		col2 = row.column(align=1)
		col2.operator("lineyka.push", icon = 'NONE')
		col2.operator("lineyka.report", icon = 'NONE', text = 'Send To Report').action = 'report'
		
		# open
		col_open = layout.column(align=1)
		col_open.operator("lineyka.open_version", icon = 'NONE', text = 'Open Version').version = ''
		col_open.operator("lineyka.open", icon = 'NONE', text = 'Open From Input').action = 'from_input'
		
class FUNCTIONAL_tasks_sequence_editor(bpy.types.Panel):
	bl_label = 'Lineyka /// Task:'
	bl_space_type = "SEQUENCE_EDITOR"
	bl_region_type = "UI"
	   
	@classmethod
	def poll(self, context):
		#if G.functional_panel and (G.current_task['task_type'] == 'animatic' or G.current_task['task_type'] == 'film'):
		if G.functional_panel:
			#G.activate_task = False
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'task_panel'
		row.operator("lineyka.help", icon = 'QUESTION', text = 'About Task Type').action = G.current_task['task_type']
		
		# task info data
		task_info = [
		('task name:',G.current_task['task_name']),
		('activity:',G.current_task['activity']),
		('input activity:',G.current_task['input_activity']),
		('status:',G.current_task['status']),
		('priority:',G.current_task['priority']),
		('price:',str(G.current_task['price'])),
		]
		# task info layout
		col_info = layout.column(align=1)
		for key in task_info:
			row = col_info.row(align = 1)
			row.label(key[0])
			row.label(key[1])
		
		row = layout.row()
		# tz chat
		col = row.column(align=1)
		col.operator("lineyka.tz", icon = 'NONE')
		col.operator("lineyka.chat", icon = 'NONE')
		if 'sketch' in G.db_task.activity_folder[G.current_task['asset_type']].keys():
			col.operator("lineyka.look_sketch", icon = 'NONE')
		
		# push / report
		col = row.column(align=1)
		col.operator("lineyka.push", icon = 'NONE')
		col.operator("lineyka.report", icon = 'NONE', text = 'Send To Report').action = 'report'
		
		# open
		col_open = layout.column(align=1)
		col_open.operator("lineyka.open_version", icon = 'NONE', text = 'Open Version').version = ''
		col_open.operator("lineyka.open", icon = 'NONE', text = 'Open From Input').action = 'from_input'
		
class FUNCTIONAL_load_open_panel(bpy.types.Panel):
	bl_label = 'Lineyka /// Load or Open from Source:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = 'Lineyka'
	bl_options = {'DEFAULT_CLOSED'}
	
	@classmethod
	def poll(self, context):
		if G.current_project and G.current_task:
			if G.current_task['asset_type'] in ['char', 'obj']:
				return(True)
			else:
				return(False)
		else:
			return(False)
		
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'load_or_open_source_panel'
		
		#layout.prop(context.scene, "my_enum")
		layout.prop(context.scene, "lineyka_filter_by_name")
		layout.operator('lineyka.load_group_list')
		
		col = layout.column(align = True)
		
		if G.load_or_open_panel_group_list_vis:
			for group in G.group_data_list:
				if context.scene.lineyka_filter_by_name \
					and (not context.scene.lineyka_filter_by_name.lower() in group['name'].lower()):
					continue
				else:
					row = col.row(align = True)
					row.label(group['name'])
					row.label('(' + group['type'] + ')')
					row.operator('lineyka.load_content_list_of_group').group_data = json.dumps(dict(group))
				
		if G.load_or_open_panel_content_list_vis:
			col.label(('Asset list of group: ' + G.load_or_open_panel_current_group['name'] + \
				' (' + G.load_or_open_panel_current_group['type'] + ')'))
			if G.current_task['asset_type'] == 'char':
				col.prop(context.scene, "activity_enum")
			col.label('__________')
			for task in G.load_or_open_panel_content_list_of_group:
				if context.scene.lineyka_filter_by_name \
					and (not context.scene.lineyka_filter_by_name.lower() in task['asset'].lower()):
					continue
				else:
					row = col.row(align = True)
					row.label(task['asset'])
					row.operator("lineyka.library_preview_image", icon = 'NONE').asset_name = task['asset']
					row.operator('lineyka.load_source_file', icon = 'NONE').task_data = json.dumps(dict(task))
					row.operator('lineyka.open_source_file', icon = 'NONE').task_data = json.dumps(dict(task))
			
		
		'''
		# Content of Group
		if G.current_task['asset_type'] == 'char':
			layout.prop(context.scene, "activity_enum")
		
		if context.scene.my_enum != '--select group--':
			layout.label(context.scene.my_enum)
			content_list = G().get_content_list(context.scene.my_enum)
			
			col = layout.column(align=1)
			for task in content_list:
				row = col.row()
				row.label(task['asset'])
				row.operator("lineyka.library_preview_image", icon = 'NONE').asset_name = task['asset']
				#row.operator('lineyka.library_load_asset', icon = 'NONE').task_data = json.dumps(dict(task))
				row.operator('lineyka.open_source_file', icon = 'NONE').task_data = json.dumps(dict(task))
		'''
				

# ********** ANIMATIC
class LINEYKA_animatic_panel(bpy.types.Panel):
	bl_idname = "lineyka.animatic_panel"
	bl_label = "Lineyka /// Animatic"
	bl_space_type = "SEQUENCE_EDITOR"
	bl_region_type = "UI"
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['animatic', 'film']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['animatic', 'film']
		BOOL = None
		if BOOL_read:
			BOOL = True
		elif BOOL_work:
			BOOL = True
		else:
			BOOL = False
			print('***', BOOL_read, BOOL_work, G.read_func_panel)
			
		if BOOL:
			if context.scene.name == G.name_scene:
				for area in bpy.context.screen.areas:
					if area.type == 'VIEW_3D':
						area.type = 'SEQUENCE_EDITOR'
						break
			else:
				for area in bpy.context.screen.areas:
					if area.type == 'SEQUENCE_EDITOR':
						space_data = area.spaces.active
						if space_data.view_type == 'PREVIEW':
							area.type = 'VIEW_3D'
							break
						else:
							#print(space_data.view_type)
							pass

			return(True)
		
		return(False)
	
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row()
		row.label(' ')
		row.operator('lineyka.help', icon = 'QUESTION').action = 'animatic_panel'
		
		row = layout.row()
		row.label('First of all!')
		row.operator("lineyka.animatic_start")
		
		col = layout.column(align = True)
		col.label('Add /// Remove:')
		col.operator("lineyka.add_shot")
		col.operator("lineyka.remove_shot", text = 'Delete Shot')
		col.operator('lineyka.rename_shot')
		
		col = layout.column(align = True)
		col.label('Go To:')
		col.operator("lineyka.go_to_animatic")
		col.operator("lineyka.go_to_shot")
		
		col = layout.column(align = True)
		col.label('Synchronization:')
		col.operator("lineyka.synchr_duration")
		col.operator("lineyka.sound_to_shot")
		col.operator('lineyka.sound_to_animatic')
		
		col = layout.column(align = True)
		col.label('Render:')
		col.operator("lineyka.render_animatic_shots", text = 'Render All').action = 'render_all'
		col.operator("lineyka.render_animatic_shots", text = 'Render By Shots').action = 'by_shots'
		col.operator("lineyka.render_animatic_shots", text = 'Render Selected Shots').action = 'selected_shots'
		col.operator("lineyka.render_animatic_shots", text = 'h.264 - All').action = 'h.264.render_all'
		col.operator("lineyka.render_animatic_shots", text = 'h.264 - By Shots').action = 'h.264.by_shots'
		col.operator("lineyka.render_animatic_shots", text = 'h.264 - Selected Shots').action = 'h.264.selected_shots'
		
class LINEYKA_animatic_to_shot_animation_panel(bpy.types.Panel):
	bl_idname = "lineyka.animatic_to_shot_animation_panel"
	bl_label = 'Lineyka /// To Shot Animation:'
	bl_space_type = "SEQUENCE_EDITOR"
	bl_region_type = "UI"
	   
	@classmethod
	def poll(self, context):
		#if G.functional_panel and (G.current_task['task_type'] == 'animatic' or G.current_task['task_type'] == 'film'):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['animatic', 'film']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['animatic', 'film']
		
		if BOOL_work and context.scene.name == G.name_scene:
			return True
		elif BOOL_read and context.scene.name == G.name_scene:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'animatic_to_shot_animation_panel'
		
		col = layout.column(align = True)
		col.label('Info of Shots:')
		col.operator('lineyka.animatic_add_comment')
		col.operator('lineyka.animatic_set_parent_shot')
		
		col = layout.column(align = True)
		col.label('Create Assets:')
		col.prop(context.scene, "my_enum")
		col.prop(context.scene, 'set_of_tasks_enum')
		col.operator('lineyka.animatic_create_assets', text = 'All').action = 'all'
		col.operator('lineyka.animatic_create_assets', text = 'From Selected Sequences').action = 'selected'
		
		col = layout.column(align = True)
		col.label('Render to Shot Animation:')
		col.operator('lineyka.render_animatic_shots_to_asset', text = 'Render All').action = 'all'
		col.operator('lineyka.render_animatic_shots_to_asset', text = 'Render Selected Shots').action = 'selected'
		

class LINEYKA_animatic_import_sequences(bpy.types.Panel):
	bl_idname = "lineyka.animatic_import_sequences"
	bl_label = 'Lineyka /// Reload Sequences:'
	bl_space_type = "SEQUENCE_EDITOR"
	bl_region_type = "UI"
	   
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['animatic', 'film']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['animatic', 'film']
		
		if BOOL_work and context.scene.name == G.name_scene:
			return True
		elif BOOL_read and context.scene.name == G.name_scene:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'animatic_import_sequences_panel'
		
		layout.label('Playblast:')
		row = layout.row(align = True)
		row.operator('lineyka.animatic_import_playblast_to_select_sequence', text = 'Load Final').action = 'final'
		row.operator('lineyka.animatic_import_playblast_to_select_sequence', text = 'Load Version').action = 'version'
		
		layout.label('Composition:')
		
		layout.label('Return Animatic:')
		layout.operator('lineyka.animatic_return')
		
class LINEYKA_animatic_playblast_version_panel(bpy.types.Panel):
	bl_idname = "lineyka.animatic_playblast_version_panel"
	bl_label = 'Lineyka /// Playblast Version:'
	bl_space_type = "SEQUENCE_EDITOR"
	bl_region_type = "UI"
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['animatic', 'film']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['animatic', 'film']
		
		if BOOL_work and context.scene.name == G.name_scene and G.playblast_version_panel:
			return True
		elif BOOL_read and context.scene.name == G.name_scene and G.playblast_version_panel:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'animatic_playblast_version_panel'
		
		col = layout.column()
		for data in G.playblast_version_data_list:
			row = col.row(align = True)
			for key in G.db_log.logs_keys:
				row.label(data[key[0]])
			row.operator('lineyka.animatic_import_playblast_to_select_sequence', text = 'load').action = data['version']
			
		layout.operator('lineyka.animatic_import_playblast_to_select_sequence', text = 'close').action = 'off'
		
		
# ********** MODEL
class FUNCTIONAL_model(bpy.types.Panel):
	bl_label = 'Lineyka /// Model:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
    
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['model', 'sculpt']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['model', 'sculpt']
		
		if BOOL_work:
			return True
		elif BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'model_panel'
		
		# sketch
		layout.label('Sketch')
		col = layout.column(align=1)
		col.operator("lineyka.load_sketch", icon = 'NONE', text = 'Sketch to Background').action = 'plane'
		
		col.label('Organize')
		col.operator("lineyka.model_rename_by_asset", icon = 'NONE', text = 'Rename by Asset')
		
# ********** TEXTURES
class FUNCTIONAL_textures(bpy.types.Panel):
	bl_label = 'Lineyka /// Textures:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	    
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['model', 'textures',]
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['model', 'textures',]
		
		if BOOL_work:
			return True
		elif BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'textures_panel'
		
		layout.operator("lineyka.load_sketch", icon = 'NONE', text = 'Load Sketch').action = 'plane'
		
		col = layout.column(align= True)
		col.operator("lineyka.pack_images", text = 'Save Images to Activity').action = 'save_to_activity'
		col.operator("lineyka.open_images")
		
		# sketch
		layout.label('Pack / Unpack')
		col = layout.column(align= True)
		col.operator("lineyka.pack_images", text = 'Pack Images').action = 'pack'
		col.operator("lineyka.pack_images", text = 'Unpack Images').action = 'unpack'
		
		layout.label('Switch Format')
		row = layout.row(align= True)
		row.operator("lineyka.switch_image_format", text = 'TIFF to PNG').action = 'tif_to_png'
		row.operator("lineyka.switch_image_format", text = 'PNG to TIFF').action = 'png_to_tif'
		
		layout.label('Convert Format')
		row = layout.row(align= True)
		row.operator("lineyka.convert_image_format", text = 'TIFF to PNG').action = 'tif_to_png'
		row.operator("lineyka.convert_image_format", text = 'PNG to TIFF').action = 'png_to_tif'
		
class FUNCTIONAL_textures_addition(bpy.types.Panel):
	bl_label = 'Lineyka /// Switch Textures:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_options = {'DEFAULT_CLOSED'}
	    
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['animation_shot', 'tech_anim', 'simulation_din', 'render']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['animation_shot', 'tech_anim', 'simulation_din', 'render']
		
		if BOOL_work:
			return True
		elif BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'switch_textures_panel'
		
		col = layout.column(align = True)
		col.label('Switch Format (all):')
		col.operator("lineyka.switch_image_format", text = 'TIFF to PNG').action = 'tif_to_png'
		col.operator("lineyka.switch_image_format", text = 'PNG to TIFF').action = 'png_to_tif'

		
# ********** GROUP (model, rig)
class FUNCTIONAL_group(bpy.types.Panel):
	bl_label = 'Lineyka /// Group:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
    
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['model', 'rig']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['model', 'rig']
		
		if BOOL_work:
			return True
		elif BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'group_panel'
		
		# group
		col = layout.column(align = True)
		col.label('Group:')
		col.operator('lineyka.create_empty_group')
		col.prop(context.scene, 'groups_enum')
		row = col.row(align = True)
		row.operator('lineyka.add_objects_to_group', text = 'Add select objects')
		row.operator('lineyka.unlink_objects_from_group', text = 'Unlink select objecs')
		
		layout.label('Edit Group:')
		
		col = layout.column(align = True)
		col.operator('lineyka.remove_group_panel', text = 'Remove Group').action = 'open'
		col.operator('lineyka.rename_group_panel', text = 'Rename Group to Din').action = 'open'
		
class FUNCTIONAL_removable_group(bpy.types.Panel):
	bl_label = 'Lineyka /// Removable Groups:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
    
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['model', 'rig']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['model', 'rig']
		
		if BOOL_work and G.removable_group_panel:
			return True
		elif BOOL_read and G.removable_group_panel:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		col = layout.column(align = True)
		for group in bpy.data.groups:
			col.operator('lineyka.remove_group', text = group.name).removable_group = group.name
			
		layout.operator('lineyka.remove_group_panel', text = 'Close').action = 'close'
		
class FUNCTIONAL_group_to_rename(bpy.types.Panel):
	bl_label = 'Lineyka /// Groups to Rename:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
    
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['model', 'rig']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['model', 'rig']
		
		if BOOL_work and G.rename_group_panel:
			return True
		elif BOOL_read and G.rename_group_panel:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		col = layout.column(align = True)
		for group in bpy.data.groups:
			if not '.din' in group.name:
				col.operator('lineyka.rename_group_to_din', text = group.name).name = group.name
			
		layout.operator('lineyka.rename_group_panel', text = 'Close').action = 'close'
		
		
# ********** RIG		
class FUNCTIONAL_rig(bpy.types.Panel):
	bl_label = 'Lineyka /// Rig:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
    
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['rig']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['rig']
		
		if BOOL_work:
			return True
		elif BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'rig_panel'
		
		col = layout.column(align = True)
		col.label('Initial content:')
		col.operator('lineyka.look_activity', text = 'Open Model Activity').action = json.dumps(('model','publish'))
		col.operator('lineyka.look_activity', text = 'Open Rig Activity').action = json.dumps(('rig','publish'))
		
		col = layout.column(align = True)
		col.label('Output Cache Passport:')
		col.operator('lineyka.add_object_to_cache_passport', text = 'Add objecs to OUTPUT cache').action = 'output'
		row = col.row(align = True)
		row.operator('lineyka.select_object_frome_cache_passport', text = 'Select').action = 'output'
		row.operator('lineyka.remove_object_frome_cache_passport', text = 'Remove').action = 'output'
		
		col = layout.column(align = True)
		col.label('Input Cache Passport:')
		col.operator('lineyka.add_object_to_cache_passport', text = 'Add objecs to INPUT cache').action = 'input'
		row = col.row(align = True)
		row.operator('lineyka.select_object_frome_cache_passport', text = 'Select').action = 'input'
		row.operator('lineyka.remove_object_frome_cache_passport', text = 'Remove').action = 'input'
		
		col = layout.column(align = True)
		col.label('Texts:')
		col.operator('lineyka.rename_texts_panel', text = 'Rename texts').action = 'on'
		
class FUNCTIONAL_technical_cache(bpy.types.Panel):
	bl_label = 'Lineyka /// Technical Cache:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_options = {'DEFAULT_CLOSED'}
	    
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['rig']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['rig']
		
		if BOOL_work:
			return True
		elif BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'technical_cache_panel'
		
		layout.operator('lineyka.look_activity', text = 'Open Rig Activity').action = json.dumps(('rig','final'))
		
		col = layout.column(align = True)
		#col.operator('lineyka.shot_animation_export_point_cache', text = 'Export Cache').action = 'this_asset'
		col.operator('lineyka.rig_export_point_cache')
		col.operator('lineyka.rig_import_point_cache', text = 'Import Cache').action = 'version'
		
		layout.operator('lineyka.rig_clear_point_cache')
		
class FUNCTIONAL_version_technical_cache(bpy.types.Panel):
	bl_label = 'Lineyka /// Version Cache:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	#bl_options = {'DEFAULT_CLOSED'}
	    
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.rig_version_technical_cache_panel
		BOOL_read = G.read_func_panel and G.rig_version_technical_cache_panel
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		col = layout.column(align = True)
		for version in G.rig_version_technical_cache_list:
			col.operator('lineyka.rig_import_point_cache', text = version).action = version
			
		layout.operator('lineyka.rig_import_point_cache', text = 'close').action = 'close'
		
		
class FUNCTIONAL_rename_texts_panel(bpy.types.Panel):
	bl_label = 'Lineyka /// Rename Texts:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
    
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.rename_texts_panel
		BOOL_read = G.read_func_panel and G.rename_texts_panel
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		col = layout.column(align = True)
		for name in bpy.data.texts.keys():
			row = col.row(align = True)
			row.label(name)
			row.operator('lineyka.rename_texts_action', text = 'rename').name = name
			
		col = layout.column()
		col.operator('lineyka.rename_texts_panel', text = 'Close Panel').action = 'off'
		

# ********** LOCATION
class FUNCTIONAL_location(bpy.types.Panel):
	bl_label = 'Lineyka /// Location Content:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['location', 'location_for_anim', 'location_full']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['location', 'location_for_anim', 'location_full']
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		'''
		# task info data
		task_info = [
		('task name:',G.current_task['task_name']),
		('activity:',G.current_task['activity']),
		('input activity:',G.current_task['input_activity']),
		('status:',G.current_task['status']),
		('priority:',G.current_task['priority']),
		('price:',str(G.current_task['price'])),
		#('task_type:',str(G.current_task['task_type']))
		]
		# task info layout
		col_info = layout.column(align=1)
		for key in task_info:
			row = col_info.row(align = 1)
			row.label(key[0])
			row.label(key[1])
		
		row = layout.row()
		# tz chat
		col1 = row.column(align=1)
		col1.operator("lineyka.tz", icon = 'NONE')
		col1.operator("lineyka.chat", icon = 'NONE')
		if 'sketch' in G.db_task.activity_folder[G.current_task['asset_type']].keys():
			col1.operator("lineyka.look_sketch", icon = 'NONE')
		
		# push / report
		col2 = row.column(align=1)
		col2.operator("lineyka.open_version", icon = 'NONE', text = 'Open Version').version = ''
		col2.operator("lineyka.open", icon = 'NONE', text = 'Open From Input').action = 'from_input'
		col2.operator("lineyka.push", icon = 'NONE')
		col2.operator("lineyka.report", icon = 'NONE', text = 'Send To Report').action = 'report'
		'''
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'location_content_panel'
		
		# content
		layout.label('Load Content:')
		layout.operator("lineyka.location_load_exists", icon = 'NONE', text = 'Load Exists')#.current_data = json.dumps(G.current_content_data)
		
		layout.label('Edit SELECTED:')
		row = layout.row(align = True)
		row.operator("lineyka.location_select_all_copies", text = 'select all').current_data = 'all'
		row.operator("lineyka.location_add_copy_sel", text = 'add copy')
		row.operator("lineyka.location_clear_sel_content", text = 'clear')
		row.operator("lineyka.location_remove_sel_content", text = 'remove')
		
		layout.label('Content List:')
		
		# -- get meshes_list
		meshes_list = bpy.data.meshes.keys()
		group_list = []
		for name in bpy.data.groups.keys():
			group_list.append(name.split('.')[0])
		
		col_char = layout.column(align=1)
		col_char.label('CHAR list:')
		col_obj = layout.column(align=1)
		col_obj.label('OBJ list:')
		
		for key in G.current_content_data:
			if G.current_content_data[key][0]['name'] == G.current_task['asset']:
				continue
			
			### CHAR
			if G.current_content_data[key][0]['type'] == 'char':
				col = col_char.column(align = True)
				col.label(G.current_content_data[key][0]['name'])
				row = col.row(align = True)
				if G.current_content_data[key][0]['name'] in group_list:
					row.operator("lineyka.location_add_copy", icon = 'NONE').current_data = json.dumps(G.current_content_data[key])
				else:
					row.operator("lineyka.location_add_copy", icon = 'NONE', text = 'Add new').current_data = json.dumps(G.current_content_data[key])
				
				# remove button
				row.operator("lineyka.location_select_all_copies", text = 'Select All').current_data = json.dumps(G.current_content_data[key])
				row.operator("lineyka.library_preview_image", icon = 'NONE').asset_name = G.current_content_data[key][0]['name']
				row.operator("lineyka.location_clear_content", icon = 'NONE', text = 'Clear').current_data = json.dumps(G.current_content_data[key])
				row.operator("lineyka.location_remove_content", icon = 'NONE', text = "Remove").current_data = json.dumps(G.current_content_data[key])
				
				#row.label(G.current_content_data[key][0]['name'])
			
			### OBJ
			if G.current_content_data[key][0]['type'] == 'obj':
				col = col_obj.column(align = True)
				col.label(G.current_content_data[key][0]['name'])
				row = col.row(align = True)
				if G.current_content_data[key][0]['name'] in meshes_list:
					row.operator("lineyka.location_add_copy", icon = 'NONE').current_data = json.dumps(G.current_content_data[key])
				else:
					row.operator("lineyka.location_add_copy", icon = 'NONE', text = 'Add new').current_data = json.dumps(G.current_content_data[key])
				
				# remove button
				row.operator("lineyka.location_select_all_copies", text = 'Select All').current_data = json.dumps(G.current_content_data[key])
				row.operator("lineyka.library_preview_image", icon = 'NONE').asset_name = G.current_content_data[key][0]['name']
				row.operator("lineyka.location_clear_content", icon = 'NONE', text = 'Clear').current_data = json.dumps(G.current_content_data[key])
				row.operator("lineyka.location_remove_content", icon = 'NONE', text = "Remove").current_data = json.dumps(G.current_content_data[key])
				
				#row.label(G.current_content_data[key][0]['name'])
			
		
		#layout.label((input_task_list + json.dumps(meshes_list)))
		
class FUNCTIONAL_downloadable_group_list(bpy.types.Panel):
	bl_label = 'Lineyka /// Downloadable Groups:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.downloadable_group_panel
		BOOL_read = G.read_func_panel and G.downloadable_group_panel
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		layout.label('Groups:')
		
		col = layout.column(align = True)
		for group_name in G.downloadable_group_panel[1]:
			col.operator('lineyka.location_add_copy_of_char', text = group_name).group_name = group_name
			
# 
class FUNCTIONAL_downloadable_group_list_SE(bpy.types.Panel):
	bl_label = 'Lineyka /// Downloadable Groups:'
	bl_space_type = "SEQUENCE_EDITOR"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.downloadable_group_panel
		BOOL_read = G.read_func_panel and G.downloadable_group_panel
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		layout.label('Groups:')
		
		col = layout.column(align = True)
		for group_name in G.downloadable_group_panel[1]:
			col.operator('lineyka.location_add_copy_of_char', text = group_name).group_name = group_name

# ********** Animation Shot
class FUNCTIONAL_playblast(bpy.types.Panel):
	bl_label = 'Lineyka /// Playblast:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	bl_options = {'DEFAULT_CLOSED'}
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['animation_shot', 'simulation_din', 'tech_anim', 'render']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['animation_shot', 'simulation_din', 'tech_anim', 'render']
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'playblast_panel'
		
		row = layout.row(align = True)
		row.operator('lineyka.active_shot_cam')
		row.operator('lineyka.make_playblast')
		
		
class FUNCTIONAL_animation_shot(bpy.types.Panel):
	bl_label = 'Lineyka /// Content:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['animation_shot']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['animation_shot']
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'content_panel'
		
		col = layout.column(align=1)
		col.operator('lineyka.reload_animatic')
		
		col = layout.column(align=1)
		col.label('Load Content:')
		col.operator('lineyka.load_exists_shot_animation_content', text = 'Load Exists')
		
		layout.label('Edit SELECTED:')
		row = layout.row(align = True)
		row.operator("lineyka.location_select_all_copies", text = 'select all').current_data = 'all'
		row.operator("lineyka.location_add_copy_sel", text = 'add copy')
		row.operator("lineyka.location_clear_sel_content", text = 'clear')
		row.operator("lineyka.location_remove_sel_content", text = 'remove')
		
		group_list = []
		for name in bpy.data.groups.keys():
			group_list.append(name.split('.')[0])
			
		col_loc = layout.column(align=1)
		col_loc.label('LOCATION:')
		col_char = layout.column(align=1)
		col_char.label('CHAR list:')
		col_obj = layout.column(align=1)
		col_obj.label('OBJ list:')
		
		#layout.operator('lineyka.make_playblast')
		
		if G.current_content_data:
			for key in G.current_content_data:
				if G.current_content_data[key][0]['name'] == G.current_task['asset']:
					continue
				
				### LOCATION
				if G.current_content_data[key][0]['type'] == 'location':
					row = col_loc.row(align = True)
					#row.label(G.current_content_data[key][0]['name'])
					row.operator("lineyka.load_reload_location", icon = 'NONE', text = 'Load / Reload Location')
					row.label(G.current_content_data[key][0]['name'])
				
				### CHAR
				elif G.current_content_data[key][0]['type'] == 'char':
					col = col_char.column(align = True)
					col.label(G.current_content_data[key][0]['name'])
					row = col.row(align = True)
					#link
					if G.current_content_data[key][0]['name'] in group_list:
						row.operator("lineyka.location_add_copy", icon = 'NONE').current_data = json.dumps(G.current_content_data[key])
					else:
						row.operator("lineyka.location_add_copy", icon = 'NONE', text = 'Link new').current_data = json.dumps(G.current_content_data[key])
					#append
					if G.current_content_data[key][0]['name'] in group_list:
						row.operator("lineyka.location_app_copy", icon = 'NONE').current_data = json.dumps(G.current_content_data[key])
					else:
						row.operator("lineyka.location_app_copy", icon = 'NONE', text = 'Add new').current_data = json.dumps(G.current_content_data[key])
					# remove button
					row.operator("lineyka.location_select_all_copies", text = 'select all').current_data = json.dumps(G.current_content_data[key])
					row.operator("lineyka.library_preview_image", icon = 'NONE').asset_name = G.current_content_data[key][0]['name']
					row.operator("lineyka.location_clear_content", icon = 'NONE', text = 'clear').current_data = json.dumps(G.current_content_data[key])
					row.operator("lineyka.location_remove_content", icon = 'NONE', text = 'Remove').current_data = json.dumps(G.current_content_data[key])
					
					#row.label(G.current_content_data[key][0]['name'])
					
				### OBJ
				elif G.current_content_data[key][0]['type'] == 'obj':
					col = col_obj.column(align = True)
					col.label(G.current_content_data[key][0]['name'])
					row = col.row(align = True)
					#link
					if G.current_content_data[key][0]['name'] in bpy.data.objects.keys():
						row.operator("lineyka.location_add_copy", icon = 'NONE').current_data = json.dumps(G.current_content_data[key])
					else:
						row.operator("lineyka.location_add_copy", icon = 'NONE', text = 'Link new').current_data = json.dumps(G.current_content_data[key])
					#append
					if G.current_content_data[key][0]['name'] in bpy.data.objects.keys():
						row.operator("lineyka.location_app_copy", icon = 'NONE').current_data = json.dumps(G.current_content_data[key])
					else:
						row.operator("lineyka.location_app_copy", icon = 'NONE', text = 'Add new').current_data = json.dumps(G.current_content_data[key])
					# remove button
					row.operator("lineyka.location_select_all_copies", text = 'select all').current_data = json.dumps(G.current_content_data[key])
					row.operator("lineyka.library_preview_image", icon = 'NONE').asset_name = G.current_content_data[key][0]['name']
					row.operator("lineyka.location_clear_content", icon = 'NONE', text = 'clear').current_data = json.dumps(G.current_content_data[key])
					row.operator("lineyka.location_remove_content", icon = 'NONE', text = 'Remove').current_data = json.dumps(G.current_content_data[key])
			
					#row.label(G.current_content_data[key][0]['name'])
					
# ********** TECH ANIM
class FUNCTIONAL_shot_animation_point_cache(bpy.types.Panel):
	bl_label = 'Lineyka /// Point Cache:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	bl_options = {'DEFAULT_CLOSED'}
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['tech_anim']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['tech_anim']
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'point_cache_panel'
		
		layout.label('Export (animation Rig):')
		row = layout.row(align = True)
		row.operator('lineyka.shot_animation_export_point_cache', text = 'From Selected Characters').action = 'select'
		row.operator('lineyka.shot_animation_export_point_cache', text = 'From All Characters').action = 'all'
		
		layout.label('Export (tech anim):')
		row = layout.row(align = True)
		row.operator('lineyka.tech_anim_export_point_cache', text = 'From Selected Characters').action = 'select'
		row.operator('lineyka.tech_anim_export_point_cache', text = 'From All Characters').action = 'all'
		
		layout.label('Import Version:')
		layout.operator('lineyka.tech_anim_import_version_cache', text = 'To Selected Obj').data = 'open_panel'
		
class FUNCTIONAL_tech_anim_load_char(bpy.types.Panel):
	bl_label = 'Lineyka /// Load Char:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	bl_options = {'DEFAULT_CLOSED'}
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['tech_anim']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['tech_anim']
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'load_char_panel'
		
		layout.label('Load:')
		
		assets_list = G.tech_anim_char_assets_list
		
		if assets_list[0]:
			for asset_name in assets_list[1]:
				row = layout.row()
				row.label(asset_name)
				if not asset_name in bpy.data.objects.keys():
					row.operator('lineyka.load_char_to_tech_anim', text = 'load').asset_data = json.dumps(dict(assets_list[1][asset_name]))
				else:
					row.operator('lineyka.clear_char_from_tech_anim', text = 'clear').asset_data = json.dumps(dict(assets_list[1][asset_name]))
		else:
			layout.label(assets_list[1])
			
		layout.label('Position:')
		layout.operator('lineyka.set_position_to_tech_anim')
		
class FUNCTIONAL_tech_anim_load_obj(bpy.types.Panel):
	bl_label = 'Lineyka /// Load Obj:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	bl_options = {'DEFAULT_CLOSED'}
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['tech_anim']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['tech_anim']
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'load_obj_panel'
		
		layout.label('Load:')
		
		assets_list = G.tech_anim_obj_assets_list
		
		if assets_list[0]:
			for asset_name in assets_list[1]:
				row = layout.row()
				row.label(asset_name)
				if not asset_name in bpy.data.objects.keys():
					row.operator('lineyka.load_obj_to_tech_anim', text = 'load').asset_data = json.dumps(dict(assets_list[1][asset_name]))
				else:
					row.operator('lineyka.location_clear_content', text = 'clear').current_data = json.dumps([dict(assets_list[1][asset_name]),{}])
					
		else:
			layout.label(assets_list[1])
			
		layout.label('Position:')
		layout.operator('lineyka.set_position_to_tech_anim')
			
class FUNCTIONAL_tech_anim_downloadable_group_list(bpy.types.Panel):
	bl_label = 'Lineyka /// Downloadable Groups:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.tech_anim_group_panel
		BOOL_read = G.read_func_panel and G.tech_anim_group_panel
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		col = layout.column(align = True)
		for group_name in G.tech_anim_group_list:
			if not group_name in bpy.data.groups.keys():
				col.operator('lineyka.tech_anim_load_group', text = group_name).data = group_name
			
		layout.operator('lineyka.tech_anim_load_group', text = 'close').data = 'close'
		
class FUNCTIONAL_tech_anim_version_cache_panel(bpy.types.Panel):
	bl_label = 'Lineyka /// Version Cache:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.tech_anim_version_cache_panel
		BOOL_read = G.read_func_panel and G.tech_anim_version_cache_panel
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		col = layout.column(align = True)
		for row in G.tech_anim_cache_versions_list:
			col.operator('lineyka.tech_anim_import_version_cache', text = row[0]).data = json.dumps((row[1], row[2]))
		
		layout.operator('lineyka.tech_anim_import_version_cache', text = 'close').data = 'close'
		
class FUNCTIONAL_tech_anim_set_position_as(bpy.types.Panel):
	bl_label = 'Lineyka /// Set Position As:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.tech_anim_set_position_panel
		BOOL_read = G.read_func_panel and G.tech_anim_set_position_panel
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		col = layout.column(align = True)
		for key in G.tech_anim_positions_list:
			col.operator('lineyka.tech_anim_set_position_action', text = key).data = json.dumps([G.tech_anim_positions_list[key], G.tech_current_ob])
			#col.label(key)
			
		layout.operator('lineyka.tech_anim_set_position_action', text = 'close').data = 'close'
		
		
# ********** SIMULATION
class FUNCTIONAL_render_scene_content(bpy.types.Panel):
	bl_label = 'Lineyka /// Load Input Activity:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
	bl_options = {'DEFAULT_CLOSED'}
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['render']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['render']
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
			
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'load_input_activity_panel'
		
		layout.operator('lineyka.look_activity', text = 'Open Shot Animation Activity').action = json.dumps(('shot_animation','publish'))
		layout.operator('lineyka.look_activity', text = 'Open Simulation Din Activity').action = json.dumps(('simulation_din','publish'))


class FUNCTIONAL_scene_char_content(bpy.types.Panel):
	bl_label = 'Lineyka /// Load Char:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
	bl_options = {'DEFAULT_CLOSED'}
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['simulation_din', 'render']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['simulation_din', 'render']
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'din_load_char_panel'
		
		layout.label('>> All:')
		
		col = layout.column(align = True)
		col.operator('lineyka.scene_add_copy_of_char', text = 'Load the Missing').data = json.dumps(G.simulation_content_list['char_list'])
		col.operator('lineyka.scene_clear_of_char', text = 'Clear All').data = json.dumps(G.simulation_content_list['char_list'])
		col.operator('lineyka.pass', text = 'Reload All')
		
		layout.label('>> Separately:')
		
		col = layout.column(align = True)
		for key in G.simulation_content_list['char_list']:
			row = col.row()
			row.label(key)
			if key in bpy.data.objects.keys():
				row.operator('lineyka.scene_clear_of_char', text = 'Clear').data = json.dumps({key: G.simulation_content_list['char_list'][key]})
			else:
				if G.simulation_content_list['char_list'][key]['din_rig_path']:
					row.operator('lineyka.scene_add_copy_of_char', text = 'Din Rig').data = json.dumps({key: G.simulation_content_list['char_list'][key]})
				elif G.simulation_content_list['char_list'][key]['model_path']:
					row.operator('lineyka.scene_add_copy_of_char', text = 'Model').data = json.dumps({key: G.simulation_content_list['char_list'][key]})
				else:
					row.label('not publish activity')
		
		layout.label('>> By Selected:')
		col = layout.column(align = True)
		col.operator('lineyka.convert_instance_original', text = 'Convert to Original').action = 'to_original'
		col.operator('lineyka.convert_instance_original', text = 'Convert to Instance').action = 'to_instance'
		
class FUNCTIONAL_scene_obj_content(bpy.types.Panel):
	bl_label = 'Lineyka /// Load Obj:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
	bl_options = {'DEFAULT_CLOSED'}
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['simulation_din', 'render']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['simulation_din', 'render']
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'din_load_obj_panel'
		
		layout.label('>> All:')
		
		col = layout.column(align = True)
		col.operator('lineyka.scene_add_copy_of_obj', text = 'Load the Missing').data = json.dumps(G.simulation_content_list['obj_list'])
		col.operator('lineyka.scene_clear_of_obj', text = 'Clear All').data = json.dumps(G.simulation_content_list['obj_list'])
		col.operator('lineyka.pass', text = 'Reload All')
		
		layout.label('>> Separately:')
		
		col = layout.column(align = True)
		for key in G.simulation_content_list['obj_list']:
			row = col.row()
			row.label(key)
			if key in bpy.data.objects.keys():
				row.operator('lineyka.scene_clear_of_obj', text = 'Clear').data = json.dumps({key: G.simulation_content_list['obj_list'][key]})
			else:
				row.operator('lineyka.scene_add_copy_of_obj', text = 'Model').data = json.dumps({key: G.simulation_content_list['obj_list'][key]})
				
		
class FUNCTIONAL_scene_point_cache(bpy.types.Panel):
	bl_label = 'Lineyka /// Point Cache:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
	bl_options = {'DEFAULT_CLOSED'}
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['simulation_din', 'render']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['simulation_din', 'render']
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'din_point_cache_panel'
		
		layout.label('Export :')
		col = layout.column(align = True)
		col.operator('lineyka.scene_export_point_cache', text = 'From Selected Characters').action = 'select'
		col.operator('lineyka.scene_export_point_cache', text = 'From Selected Mesh').action = 'mesh'
		
		layout.operator('lineyka.scene_replace_din_to_cache', text = 'Replace Din To Point Cache')
		
		layout.label('Import Version:')
		layout.operator('lineyka.tech_anim_import_version_cache', text = 'To Selected Obj').data = 'open_panel'

# ********** CONTENT LIBRARY
class FUNCTIONAL_location_library(bpy.types.Panel):
	bl_label = 'Lineyka /// Content Library:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
	bl_options = {'DEFAULT_CLOSED'}
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['location_for_anim', 'location_full', 'location', 'animation_shot']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['location_for_anim', 'location_full', 'location', 'animation_shot']
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'content_library_panel'
		
		#layout.prop(context.scene, "my_enum")
		layout.operator('lineyka.load_group_list')
		
		col = layout.column(align = True)
		
		if G.load_or_open_panel_group_list_vis:
			for group in G.group_data_list:
				row = col.row(align = True)
				row.label(group['name'])
				row.label('(' + group['type'] + ')')
				row.operator('lineyka.load_content_list_of_group').group_data = json.dumps(dict(group))
				
		if G.load_or_open_panel_content_list_vis:
			# get exists content
			exists_asset_list = []
			obgects_groups = bpy.data.objects.keys() + bpy.data.groups.keys()
			for name in obgects_groups:
				if not name.split('.')[0] in exists_asset_list:
					exists_asset_list.append(name.split('.')[0])
			
			# 
			col.label(('Asset list of group: ' + G.load_or_open_panel_current_group['name'] + \
				' (' + G.load_or_open_panel_current_group['type'] + ')'))
			col.label('__________')
			for task in G.load_or_open_panel_content_list_of_group:
				if task['asset'] in exists_asset_list:
					continue
				row = col.row(align = True)
				row.label(task['asset'])
				row.operator("lineyka.library_preview_image", icon = 'NONE').asset_name = task['asset']
				row.operator('lineyka.library_load_asset', icon = 'NONE').task_data = json.dumps(dict(task))

		'''
		if context.scene.my_enum != '--select group--':
			layout.label(context.scene.my_enum)
			content_list = G().get_content_list(context.scene.my_enum)
			
			# get exists content
			exists_asset_list = []
			obgects_groups = bpy.data.objects.keys() + bpy.data.groups.keys()
			for name in obgects_groups:
				if not name.split('.')[0] in exists_asset_list:
					exists_asset_list.append(name.split('.')[0])
			
			col = layout.column(align=1)
			for task in content_list:
				if task['asset'] in exists_asset_list:
					continue
				row = col.row()
				row.label(task['asset'])
				row.operator("lineyka.library_preview_image", icon = 'NONE').asset_name = task['asset']
				row.operator('lineyka.library_load_asset', icon = 'NONE').task_data = json.dumps(dict(task))
		'''

# ******************* CAMERA ************************************************
class FUNCTIONAL_edit_camera(bpy.types.Panel):
	bl_label = 'Lineyka /// Camera:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
	bl_options = {'DEFAULT_CLOSED'}
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.current_task['task_type'] in ['animation_shot', 'tech_anim', 'simulation_din', 'render']
		BOOL_read = G.read_func_panel and G.current_task['task_type'] in ['animation_shot', 'tech_anim', 'simulation_din', 'render']
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
			
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'camera_panel'
		
		col = layout.column(align = True)
		col.label('Current Shot Camera:')
		col.operator('lineyka.set_current_shot_camera')
		row = col.row(align = True)
		row.operator('lineyka.add_object_to_group_of_camera').action = 'add'
		row.operator('lineyka.add_object_to_group_of_camera', text = 'Unlink').action = 'unlink'
		
		row = col.row(align = True)
		row.operator('lineyka.push_current_shot_camera')
		row.operator('lineyka.open_camera_version_panel').action = 'on'
		
class FUNCTIONAL_camera_version_panel(bpy.types.Panel):
	bl_label = 'Lineyka /// Camera Versions:'
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
	
	@classmethod
	def poll(self, context):
		BOOL_work = G.functional_panel and G.camera_version_panel
		BOOL_read = G.read_func_panel and G.camera_version_panel
		
		if BOOL_work or BOOL_read:
			return True
		else:
			return False
			
	def draw(self, context):
		layout = self.layout
		
		# help
		row = layout.row(align = True)
		row.label(' ')
		row.operator("lineyka.help", icon = 'QUESTION').action = 'camera_version_panel'
				
		col = layout.column(align = True)
		row = col.row(align = True)
		for key in G.db_log.logs_keys:
			row.label(key[0])
		row.label('*'*3)
		for data in G.camera_version_data_list:
			row = col.row(align = True)
			for key in G.db_log.logs_keys:
				row.label(data[key[0]])
			row.operator('lineyka.load_current_shot_camera', text = 'load').action = data['version']
			
		layout.operator('lineyka.open_camera_version_panel', text = 'close').action = 'off'
			
		
# ******************* VERSION PANELS ****************************************
class VERSION_look(bpy.types.Panel):
	bl_label = 'Lineyka /// Versions of Activity:'
	bl_space_type = "VIEW_3D"
	#bl_region_type = "UI"
	bl_region_type = "TOOLS"
	bl_category = 'Lineyka'
	#layout = 'distrib_layout'
    
	@classmethod
	def poll(self, context):
		if G.look_version_panel:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		#result = G.func.get_push_logs(G.current_project, G.current_task)
		'''
		if not result[0]:
			G.look_version_panel = False
			print(result[1])
			return
		'''
		col = layout.column(align=1)
		
		row = col.row(align=1)
		row.label('date_time')
		row.label('task_name')
		row.label('artist')
		row.label('action')
		row.label('version')
		row.label('comment')
		row.label('***')
		
		#if not result[0]:
		if not G.versions_list:
			layout.label(result[1])
			layout.operator("lineyka.close_version", icon = 'NONE')
			return
			
		#for log in result[1]:
		for log in G.versions_list:
			row = col.row(align=1)
			row.label(log['date_time'])
			row.label(log['task_name'])
			row.label(log['artist'])
			row.label(log['action'])
			row.label(log['version'])
			row.label(log['comment'])
			if G.version == 'look':
				row.operator("lineyka.look_version", icon = 'NONE', text = 'look').version = log['version']
			elif G.version == 'open':
				row.operator("lineyka.open_version", icon = 'NONE', text = 'open').version = log['version']
				
		layout.operator("lineyka.close_version", icon = 'NONE')
				
class VERSION_look_in_sequence_editor(bpy.types.Panel):
	bl_label = 'Lineyka /// Versions of Activity:'
	bl_space_type = "SEQUENCE_EDITOR"
	bl_region_type = "UI"
	#layout = 'distrib_layout'
    
	@classmethod
	def poll(self, context):
		if G.look_version_panel:
			return True
		else:
			return False
        
	def draw(self, context):
		layout = self.layout
		#result = G.func.get_push_logs(G.current_project, G.current_task)
		'''
		if not result[0]:
			G.look_version_panel = False
			print(result[1])
			return
		'''
		col = layout.column(align=1)
		
		row = col.row(align=1)
		row.label('date_time')
		row.label('task_name')
		row.label('artist')
		row.label('action')
		row.label('version')
		row.label('comment')
		row.label('***')
		
		#if not result[0]:
		if not G.versions_list:
			layout.label(result[1])
			return
			
		#for log in result[1]:
		for log in G.versions_list:
			row = col.row(align=1)
			row.label(log['date_time'])
			row.label(log['task_name'])
			row.label(log['artist'])
			row.label(log['action'])
			row.label(log['version'])
			row.label(log['comment'])
			if G.version == 'look':
				row.operator("lineyka.look_version", icon = 'NONE', text = 'look').version = log['version']
			elif G.version == 'open':
				row.operator("lineyka.open_version", icon = 'NONE', text = 'open').version = log['version']
		
		layout.operator("lineyka.close_version", icon = 'NONE')
		
# ******* OPERATORS **********
class LINEYKA_help(bpy.types.Operator):
	bl_idname = "lineyka.help"
	bl_label = "Help"
	action = bpy.props.StringProperty()

	def execute(self, context):
		print('***** help')
		if self.action == 'manual':
			webbrowser.open_new_tab('https://sites.google.com/site/lineykamanual/home/blender_addon_for_artist_rus')
		# PANELS
		elif self.action == 'animatic_panel':
			webbrowser.open_new_tab('https://www.youtube.com/watch?v=rg377rzHiJA&list=PLaF5hl1yUd9Vh73dKS2hFhKydrJioejWJ')
		elif self.action == 'textures_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-type-textures-rus')
		elif self.action == 'location_content_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-type-location-rus')
		elif self.action == 'content_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-type-animation-shot-rus')
		elif self.action == 'task_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-rus')
		elif self.action == 'task_operation_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-operation-rus')
		elif self.action == 'task_list_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-list-rus')
		elif self.action == 'setting_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-setting-rus')
		elif self.action == 'animatic_to_shot_animation_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-type-animatic-film-rus')
		elif self.action == 'animatic_import_sequences_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-type-animatic-film-rus')
		elif self.action == 'animatic_playblast_version_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-type-animatic-film-rus')
		elif self.action == 'model_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-type-model-sculpt-rus')
		elif self.action == 'switch_textures_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-switch-textures-rus')
		elif self.action == 'group_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-group-rus')
		elif self.action == 'rig_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-type-rig-rus')
		elif self.action == 'technical_cache_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-type-rig-rus')
		elif self.action == 'playblast_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-playblast-rus')
		elif self.action == 'point_cache_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panels-task-type-tech-anim-rus')
		elif self.action == 'load_char_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panels-task-type-tech-anim-rus')
		elif self.action == 'load_obj_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-type-simulation-din-render-rus')
		elif self.action == 'load_input_activity_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-type-simulation-din-render-rus')
		elif self.action == 'din_load_char_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-type-simulation-din-render-rus')
		elif self.action == 'din_load_obj_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-type-simulation-din-render-rus')
		elif self.action == 'din_point_cache_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-task-type-simulation-din-render-rus')
		elif self.action == 'content_library_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-content-library-rus')
		elif self.action == 'camera_panel':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-camera-rus')
		elif self.action == 'camera_version_panel':
			webbrowser.open_new_tab('https://sites.google.com/site/lineykamanual/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-camera-versions-rus')
		elif self.action == 'load_or_open_source_panel':
			webbrowser.open_new_tab('https://sites.google.com/site/lineykamanual/home/blender_addon_for_artist_rus/blender-functional-panels-by-task-types-rus/blender-panel-load-or-open-source')
		# Task TYPES
		elif self.action == 'animatic':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-types-of-tasks-rus/blender-task-type-animatic-rus')
		elif self.action == 'film':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-types-of-tasks-rus/blender-task-type-film-rus')
		elif self.action == 'textures':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-types-of-tasks-rus/blender-task-type-textures-rus')
		elif self.action == 'sculpt':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-types-of-tasks-rus/blender-task-type-sculpt-model-rus')
		elif self.action == 'model':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-types-of-tasks-rus/blender-task-type-sculpt-model-rus')
		elif self.action == 'rig':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-types-of-tasks-rus/blender-task-type-rig')
		elif self.action == 'location':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-types-of-tasks-rus/blender-task-type-location-rus')
		elif self.action == 'animation_shot':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-types-of-tasks-rus/blender-task-type-animation-shot-rus')
		elif self.action == 'tech_anim':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-types-of-tasks-rus/blender-task-type-tech-anim-rus')
		elif self.action == 'simulation_din':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-types-of-tasks-rus/blender-task-type-simulation-din-rus')
		elif self.action == 'render':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-types-of-tasks-rus/blender-task-type-render-rus')
		elif self.action == 'composition':
			webbrowser.open_new_tab('http://www.lineyka.org.ru/home/blender_addon_for_artist_rus/blender-types-of-tasks-rus/blender-task-type-composition-rus')
		return{'FINISHED'}

class SET_studio_folder(bpy.types.Operator):
	bl_idname = "lineyka.set_studio_folder"
	bl_label = "Set Studio Folder"
	action = bpy.props.StringProperty()
	directory = bpy.props.StringProperty(subtype="DIR_PATH")
		
	def execute(self, context):
		G.activate_task = None
		G.working_task_list = []
		if self.action == 'studio':
			result = G.db_studio.set_studio(self.directory)
			if not result[0]:
				self.report({'WARNING'}, result[1])
			else:	
				self.report({'INFO'}, ('set studio folder: ' + self.directory))
		elif self.action == 'tmp':
			result = G.db_studio.set_tmp_dir(self.directory)
			if not result[0]:
				self.report({'WARNING'}, result[1])
			else:	
				self.report({'INFO'}, ('set tmp folder: ' + self.directory))
		return{'FINISHED'}
    
	def invoke(self, context, event):
		wm = context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
class SET_set_file_path(bpy.types.Operator):
	bl_idname = "lineyka.set_file_path"
	bl_label = "Set File Path"
	
	action = bpy.props.StringProperty()
	filepath = bpy.props.StringProperty(subtype="FILE_PATH")
	
	def execute(self, context):
		#self.report({'INFO'}, (self.filepath))
		#print('***\n', self.filepath)
		if self.action == 'convert':
			result = G.db_studio.set_convert_exe_path(self.filepath)
			if not result[0]:
				self.report({'WARNING'}, result[1])
			else:	
				self.report({'INFO'}, ('set convert_exe path: ' + self.filepath))
		return{'FINISHED'}
    
	def invoke(self, context, event):
		wm = context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
class USER_login(bpy.types.Operator):
	bl_idname = "lineyka.user_login"
	bl_label = "User Login"
	
	user_name = bpy.props.StringProperty(name="Nik Name:")
	password = bpy.props.StringProperty(name="Password", subtype = 'PASSWORD')
		
	def execute(self, context):
		G.activate_task = None
		G.working_task_list = []
		result = G.db_artist.login_user(self.user_name, self.password)
		if not result[0]:
				self.report({'WARNING'}, result[1])
		else:
			self.report({'INFO'}, (self.user_name + ' successfully logged in!'))
			G.current_user = self.user_name
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class USER_registration(bpy.types.Operator):
	bl_idname = "lineyka.user_registration"
	bl_label = "User Registration"
	
	nik_name = bpy.props.StringProperty(name="Nik Name:")
	password = bpy.props.StringProperty(name="Password", subtype = 'PASSWORD')
	user_name = getpass.getuser()
		
	def execute(self, context):
		G.activate_task = None
		G.working_task_list = []
		if not self.nik_name:
			self.report({'WARNING'}, 'Not Nik Name!')
			return{'FINISHED'}
		elif not self.password:
			self.report({'WARNING'}, 'Not Password!')
			return{'FINISHED'}
			
		data = {
		'nik_name': self.nik_name,
		'user_name': self.user_name,
		'password': self.password,
		'workroom': json.dumps([]),
		}
		# get user_level
		artists = G.db_artist.read_artist('all')
		if not artists[0]:
			data['level'] = 'root'
		else:
			data['level'] = 'user'
		# register user
		result = G.db_artist.add_artist(data)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		else:
			self.report({'INFO'}, (data['nik_name'] + ' successfully registered!'))
			G.current_user = self.nik_name
		
		# return
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class GET_project(bpy.types.Operator):
	bl_idname = "lineyka.get_project"
	bl_label = 'Get Progect'
	
	# get project list
	enum_list = []
	if G.db_studio.list_projects:
		project_list = G.db_studio.list_projects.keys()
	else:
		project_list = []
	for key in project_list:
		if G.db_studio.list_projects[key]['status'] == 'active':
			enum_list.append((key, key, key))
	property = bpy.props.EnumProperty(name="Project List:", items = enum_list)
	
	def execute(self, context):
		G.current_project = self.property
		result = G().get_task_list()
		if not result[0]:
			self.report({'WARNING'}, result[1])
		self.report({'INFO'}, ('selected project: ' + self.property))
		
		# rebild group list
		G().rebild_group_list()
		G.load_or_open_panel_content_list_vis = False
		
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
class Lineyka_load_group_list(bpy.types.Operator):
	bl_idname = "lineyka.load_group_list"
	bl_label = '--select group--'
	
	def execute(self, context):
		G.load_or_open_panel_group_list_vis = True
		G.load_or_open_panel_content_list_vis = False
		return{'FINISHED'}
	
class Lineyka_load_content_list_of_group(bpy.types.Operator):
	bl_idname = "lineyka.load_content_list_of_group"
	bl_label = '>>'
	
	group_data = bpy.props.StringProperty()
	
	def execute(self, context):
		group_data = json.loads(self.group_data)
		G.load_or_open_panel_content_list_of_group = G().get_content_list(group_data['name'])
		G.load_or_open_panel_current_group = group_data
		
		G.load_or_open_panel_group_list_vis = False
		G.load_or_open_panel_content_list_vis = True
		return{'FINISHED'}
	

class Lineyka_reload_task_list(bpy.types.Operator):
	bl_idname = "lineyka.reload_task_list"
	bl_label = 'Reload task List'
	
	@classmethod
	def poll(self, context):
		if G.current_project:
			return(True)
		return(False)
	
	def execute(self, context):
		result = G().get_task_list()
		if not result[0]:
			self.report({'WARNING'}, result[1])
		return{'FINISHED'}
		
class TASK_reader_distrib(bpy.types.Operator):
	bl_idname = "lineyka.reader_task_distrib"
	bl_label = "Load Task Data"
	
	task_data = bpy.props.StringProperty()

	def execute(self, context):
		# activate panels
		G.activate_reader_task = True
		G.activate_task = False
		
		# deactivate panels
		G.functional_panel = False
		G.look_version_panel = False
		G.camera_version_panel = False
		G.downloadable_group_panel = False
		G.rename_texts_panel = False
		G.read_func_panel = False
		
		G.playblast_version_panel = False
		G.tech_anim_group_panel = False
		G.tech_anim_set_position_panel = False
		G.tech_anim_version_cache_panel = False
		G.rig_version_technical_cache_panel = False
		G.removable_group_panel = False
		G.rename_group_panel = False
		
		# task data
		task_data = json.loads(self.task_data)
		G.current_task = task_data
		
		if G.activate_reader_task:
			self.report({'INFO'}, G.current_task['task_name'])
		else:
			self.report({'WARNING'}, 'not active_task')
		
		# -- Content Data
		task_tupl = G.all_task_list[G.current_task['task_name']]
		result, data = G.func.get_content_data(G.current_project, task_tupl, all_assets_data_by_name = G.all_assets_data_by_name)
		if result:
			G.current_content_data = data
		
		return{'FINISHED'}
		

class TASK_distrib(bpy.types.Operator):
	bl_idname = "lineyka.task_distrib"
	bl_label = "Load Task Data"
	task_data = bpy.props.StringProperty()

	def execute(self, context):
		# activate panels
		G.activate_task = True
		G.activate_reader_task = False
		
		# deactivate panels
		G.functional_panel = False
		G.look_version_panel = False
		G.camera_version_panel = False
		G.downloadable_group_panel = False
		G.rename_texts_panel = False
		G.read_func_panel = False
		
		G.playblast_version_panel = False
		G.tech_anim_group_panel = False
		G.tech_anim_set_position_panel = False
		G.tech_anim_version_cache_panel = False
		G.rig_version_technical_cache_panel = False
		G.removable_group_panel = False
		G.rename_group_panel = False
		
		# task data
		task_data = json.loads(self.task_data)
		G.current_task = task_data
		if G.activate_task:
			self.report({'INFO'}, G.current_task['task_name'])
		else:
			self.report({'WARNING'}, 'not active_task')
		
		# -- Content Data
		task_tupl = G.all_task_list[G.current_task['task_name']]
		result, data = G.func.get_content_data(G.current_project, task_tupl, all_assets_data_by_name = G.all_assets_data_by_name)
		if result:
			G.current_content_data = data
		'''
		if G.current_task['input']:
			input_task_list = G.all_task_list[G.current_task['task_name']]['input']['input']
			if input_task_list:
				try:
					input_task_list = json.loads(input_task_list)
					
				except:
					if G.current_task['asset_type'] in ['location', 'shot_animation']:
						result = G.func.get_content_list(G.current_project, G.all_task_list[G.current_task['task_name']])
						if result:
							G.current_content_data = G.func.location_get_content_data(G.current_project, result)
						else:
							G.current_content_data = None
				else:
					# -- get content data
					G.current_content_data = G.func.location_get_content_data(G.current_project, input_task_list)
					
			else:
				G.current_content_data = None
		'''
		
		# get versions list
		get_versions_list()
		
		return{'FINISHED'}
		
class LINEYKA_look_activity(bpy.types.Operator):
	bl_idname = "lineyka.look_activity"
	bl_label = "Look Activity"
	
	action = bpy.props.StringProperty()
	
	def execute(self, context):
		activity, action = json.loads(self.action)
		
		result = G.func.look_activity(G.current_project, G.current_task, activity, action)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		
		G.look_version_panel = False
		return{'FINISHED'}
		
class LINEYKA_look(bpy.types.Operator):
	bl_idname = "lineyka.look"
	bl_label = "Look"
	
	def execute(self, context):
		# READ
		if context.scene.tasks_list_type == G.read:
			G.read_func_panel = True
			# load group list
			G().rebild_group_list()
			G().rebild_set_of_tasks_list()
			G().rebild_groups_list()
			
		result = G.func.look(G.current_project, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			return{'FINISHED'}
		
		G.look_version_panel = False
		
		# READ
		if G.read_func_panel:
			open_func(context, result[1], read = True)
			
		
		return{'FINISHED'}
		
class LINEYKA_look_version(bpy.types.Operator):
	bl_idname = "lineyka.look_version"
	bl_label = "Look Version"
	
	version = bpy.props.StringProperty()
	
	def execute(self, context):
		# READ
		if context.scene.tasks_list_type == G.read:
			G.read_func_panel = True
			# load group list
			G().rebild_group_list()
			G().rebild_set_of_tasks_list()
			G().rebild_groups_list()
			
		if self.version:
			result = G.func.look_version(G.current_project, G.current_task, self.version)
			if not result[0]:
				self.report({'WARNING'}, result[1])
				return{'FINISHED'}
				
		else:
			pass
		G.version = 'look'
		G.look_version_panel = True
		
		# READ
		if G.read_func_panel:
			open_func(context, result[1], read = True)
		
		return{'FINISHED'}
		
class LINEYKA_open_version(bpy.types.Operator):
	bl_idname = "lineyka.open_version"
	bl_label = "Open Version"
	
	version = bpy.props.StringProperty()
	
	def execute(self, context):
		# load group list
		G().rebild_group_list()
		G().rebild_set_of_tasks_list()
		G().rebild_groups_list()
		
		if self.version:
			# open file
			result = G.func.look_version(G.current_project, G.current_task, self.version)
			if not result[0]:
				self.report({'WARNING'}, result[1])
				return{'FINISHED'}
				
			else:
				open_path = result[1]
			
			open_func(context, open_path)
			'''
			# change status
			if G.current_task['status'] != 'work':
				result = G.func.open_change_status(G.current_project, G.current_task, G.all_task_list)
				if not result[0]:
					self.report({'WARNING'}, result[1])
					return{'FINISHED'}
				else:
					G.current_task['status'] = 'work'
					# result[1] = dict {task_name : new_status, ...}
					for task_name in result[1]:
						G.all_task_list[task_name]['task']['status'] = result[1][task_name]
				
			# edit screen
			if G.current_task['task_type'] in ['animatic', 'film']:
				if bpy.context.window:
					bpy.context.window.screen = bpy.data.screens['Video Editing']
			elif G.current_task['task_type'] in ['animation_shot', 'tech_anim']:
				G.func.reload_animatic(context, G.current_project, G.current_task)
				if bpy.context.window:
					bpy.context.window.screen = bpy.data.screens['Animation']
				# get content list
				if G.current_task['task_type'] == 'tech_anim':
					G.tech_anim_char_assets_list = G.func.get_shot_animation_content(G.current_project, G.current_task, action = 'char_assets')
					G.tech_anim_obj_assets_list = G.func.get_shot_animation_content(G.current_project, G.current_task, action = 'obj_assets')
			elif G.current_task['task_type'] == 'simulation_din':
				G.simulation_content_list = G.func.get_full_content_list(context, G.all_assets_data_by_name, G.current_project, G.current_task)
				pass
			else:
				if bpy.context.window:
					bpy.context.window.screen = bpy.data.screens['Default']
			
			# show / hide panels
			G.activate_task = False
			G.functional_panel = True
			G.look_version_panel = False
			
			# load shots data
			if G.current_task['task_type'] in ['animatic', 'film']:
				G.func.input_to_scene_shots_data(context, G.current_project)
				
			# clear deleted
			G.func.clear_deleted(context)
			'''
		else:
			G.version = 'open'
			G.look_version_panel = True
				
		return{'FINISHED'}
		
class LINEYKA_open(bpy.types.Operator):
	bl_idname = "lineyka.open"
	bl_label = "Open"
	
	action = bpy.props.StringProperty()
	
	def execute(self, context):
		# load group list
		G().rebild_group_list()
		G().rebild_set_of_tasks_list()
		G().rebild_groups_list()
		
		open_path = False
		
		self.report({'INFO'}, self.action)
		if self.action == 'open':
			# open file
			result = G.func.open_file(G.current_project, G.current_task)
			if not result[0]:
				self.report({'WARNING'}, result[1])
				return{'FINISHED'}
			else:
				open_path = result[1]
				
		elif self.action == 'from_input':
			# get input_task_data
			input_task = G.all_task_list[G.current_task['task_name']]['input']
			
			# test extension
			if G.current_task['extension'] != input_task['extension']:
				report_text = 'extension of input_task are not ' + G.current_task['extension']
				self.report({'WARNING'}, report_text)
				return{'FINISHED'}
			
			# open file
			result = G.func.open_file(G.current_project, input_task)
			if not result[0]:
				self.report({'WARNING'}, result[1])
				return{'FINISHED'}
				
			else:
				open_path = result[1]
			
		elif self.action == 'current':
			# open file
			result = G.func.open_current_file(G.current_project, G.current_task)
			if not result[0]:
				self.report({'WARNING'}, result[1])
				return{'FINISHED'}
				
		open_func(context, open_path)
		'''
		# change status
		if G.current_task['status'] != 'work':
			result = G.func.open_change_status(G.current_project, G.current_task, G.all_task_list)
			if not result[0]:
				self.report({'WARNING'}, result[1])
				return{'FINISHED'}
			else:
				G.current_task['status'] = 'work'
				# result[1] = dict {task_name : new_status, ...}
				for task_name in result[1]:
					G.all_task_list[task_name]['task']['status'] = result[1][task_name]
		
		# edit screen
		if G.current_task['task_type'] in ['animatic', 'film']:
			if bpy.context.window:
				bpy.context.window.screen = bpy.data.screens['Video Editing']
		elif G.current_task['task_type']  in ['animation_shot', 'tech_anim']:
			G.func.reload_animatic(context, G.current_project, G.current_task)
			if bpy.context.window:
				bpy.context.window.screen = bpy.data.screens['Animation']
			# get content list
			if G.current_task['task_type'] == 'tech_anim':
				G.tech_anim_char_assets_list = G.func.get_shot_animation_content(G.current_project, G.current_task, action = 'char_assets')
				G.tech_anim_obj_assets_list = G.func.get_shot_animation_content(G.current_project, G.current_task, action = 'obj_assets')
		elif G.current_task['task_type'] == 'simulation_din':
			G.simulation_content_list = G.func.get_full_content_list(context, G.all_assets_data_by_name, G.current_project, G.current_task)
			
		else:
			if bpy.context.window:
				bpy.context.window.screen = bpy.data.screens['Default']
		
		# show / hide panels
		G.activate_task = False
		G.functional_panel = True
		G.look_version_panel = False
		
		# load shots data
		if G.current_task['task_type'] in ['animatic', 'film']:
			G.func.input_to_scene_shots_data(context, G.current_project)
			
		# clear deleted
		G.func.clear_deleted(context)
		'''
			
		return{'FINISHED'}
		
def open_func(context, open_path, read = False):
	
	# for Preview in textures type task
	#result = G.db_asset.get_project(G.current_project)
	
	# change status
	if G.current_task['status'] != 'work':
		result = G.func.open_change_status(G.current_project, G.current_task, G.all_task_list)
		if not result[0]:
			#self.report({'WARNING'}, result[1])
			return(False, result[1])
			#return{'FINISHED'}
		else:
			G.current_task['status'] = 'work'
			# result[1] = dict {task_name : new_status, ...}
			for task_name in result[1]:
				G.all_task_list[task_name]['task']['status'] = result[1][task_name]
	
	# edit screen
	if G.current_task['task_type'] in ['animatic', 'film']:
		G.func.input_to_scene_shots_data(context, G.current_project)
		if bpy.context.window:
			bpy.context.window.screen = bpy.data.screens['Video Editing']
			
	elif G.current_task['task_type']  in ['animation_shot']:
		G.func.reload_animatic(context, G.current_project, G.current_task)
		if bpy.context.window:
			bpy.context.window.screen = bpy.data.screens['Animation']
		# get content list
		
	elif G.current_task['task_type'] == 'tech_anim':
		G.func.reload_start_end_resolution(context, G.current_project, G.current_task)
		G.tech_anim_char_assets_list = G.func.get_shot_animation_content(G.current_project, G.current_task, action = 'char_assets')
		G.tech_anim_obj_assets_list = G.func.get_shot_animation_content(G.current_project, G.current_task, action = 'obj_assets')
		if bpy.context.window:
			bpy.context.window.screen = bpy.data.screens['Animation']
			
	elif G.current_task['task_type'] in ['simulation_din', 'render']:
		#G.func.reload_start_end_resolution(context, G.current_project, G.current_task)
		G.func.reload_animatic(context, G.current_project, G.current_task)
		G.simulation_content_list = G.func.get_full_content_list(context, G.all_assets_data_by_name, G.current_project, G.current_task, G.current_content_data)
		
		# load Physics Cache Dir
		if open_path:
			# -- get src_dir_path
			version_dir = os.path.dirname(open_path)
			src_cache_dir_name = 'blendcache_' + G.current_task['asset']
			src_dir_path = os.path.normpath(os.path.join(version_dir, src_cache_dir_name))
			
			# -- get dst_dir_path
			this_path = context.blend_data.filepath
			this_file_name = os.path.basename(this_path)
			tmp_path = os.path.dirname(this_path)
			dst_dir_name = 'blendcache_' + this_file_name.replace('.blend', '')
			dst_dir_path = os.path.normpath(os.path.join(tmp_path, dst_dir_name)) 
			
			# -- copy
			if os.path.exists(src_dir_path):
				shutil.copytree(src_dir_path, dst_dir_path)
		
	else:
		if bpy.context.window:
			bpy.context.window.screen = bpy.data.screens['Default']
	
	# show / hide panels
	G.activate_task = False
	G.look_version_panel = False
	if not read:
		G.functional_panel = True
	
	# clear deleted
	G.func.clear_deleted(context)
	
	# current_task text data block
	G.func.current_task_text_data_block(context, G.current_task)
	
	#print('8'*250)
	#print(json.dumps(G.current_task, sort_keys = 1, indent = 4))
	#print(json.dumps(G.current_content_data, sort_keys = 1, indent = 4))
	
	# MAKE TEXT DATA BLOCK for User applications
	user_text = None
	data = {}
	data['current_task'] = G.current_task
	data['activites'] = G.db_asset.activity_folder[G.current_task['asset_type']]
	data['activites'].update(G.db_asset.additional_folders)
	if not G.user_text_name in bpy.data.texts:
		user_text = bpy.data.texts.new(G.user_text_name)
		user_text.write(json.dumps(data, sort_keys=True, indent=4))
	else:
		user_text = bpy.data.texts[G.user_text_name]
		user_text.clear()
		user_text.write(json.dumps(data, sort_keys=True, indent=4))
	
	return(True, 'Ok!')
	
def get_versions_list():
	result = G.func.get_push_logs(G.current_project, G.current_task)
	
	if not result[0]:
		G.versions_list = []
	else:
		G.versions_list = result[1]
	
	return(True, 'Ok!')
		
class LINEYKA_tz(bpy.types.Operator):
	bl_idname = "lineyka.tz"
	bl_label = "TZ"
	
	def execute(self, context):
		if G.current_task['tz']:
			webbrowser.open_new_tab(G.current_task['tz'])
		else:
			self.report({'INFO'}, 'Not Link!')
		return{'FINISHED'}
		
class LINEYKA_chat(bpy.types.Operator):
	bl_idname = "lineyka.chat"
	bl_label = "Chat"
	
	def execute(self, context):
		result = G.func.chat_run(G.current_project, G.current_user, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		return{'FINISHED'}
		
class LINEYKA_push(bpy.types.Operator):
	bl_idname = "lineyka.push"
	bl_label = "Push"
	
	comment = bpy.props.StringProperty(name="Comment")
	
	def execute(self, context):
		if not self.comment:
			self.report({'WARNING'}, 'Not Comment!')
			return{'FINISHED'}
		
		result = G.func.push(G.current_project, G.current_task, self.comment, G.current_content_data)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		else:
			self.report({'INFO'}, ('push file: ' + result[1]))
			
		get_versions_list()
		
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_report(bpy.types.Operator):
	bl_idname = "lineyka.report"
	bl_label = "Send to Report?"
	
	action = bpy.props.StringProperty()
	
	@classmethod
	def poll(self, context):
		if G.current_task and G.current_task['task_type'] in ['animatic', 'film']:
			if context.scene.name != G.name_scene:
				return(False)
		
		return(True)
	
	def execute(self, context):
		if self.action == 'report':
			# *** PRE REPORT ***
			if G.current_task['asset_type'] in ['obj', 'char'] and G.current_task['task_type'] in ['model', 'rig']:
				res = G.db_task.get_final_file_path(G.current_project, G.current_task)
				if not res[0]:
					self.report({'WARNING'}, res[1])
					return{'FINISHED'}
				
				if G.current_task['asset_type'] == 'obj' and G.current_task['task_type'] == 'model':
					with bpy.data.libraries.load(res[1]) as (data_from, data_to):
						bool_ = False
						for mesh in data_from.meshes:
							if mesh == G.current_task['asset']:
								bool_ = True
								break
						if not bool_:
							self.report({'WARNING'}, 'Not MESH with the name %s!' % G.current_task['asset'])
							return{'FINISHED'}
						
				if G.current_task['asset_type'] == 'char':
					with bpy.data.libraries.load(res[1]) as (data_from, data_to):
						bool_ = False
						for group in data_from.groups:
							if group.split('.')[0] == G.current_task['asset']:
								bool_ = True
								break
							
						if not bool_:
							self.report({'WARNING'}, 'Not GROUP with the name %s!' % G.current_task['asset'])
							return{'FINISHED'}
			
			# get exists versions of activity
			if not G.versions_list:
				self.report({'WARNING'}, 'Not Exists Versions!')
				return{'FINISHED'}
			
			# change status in db
			result = G.db_task.change_work_statuses(G.current_project, [(G.current_task, 'checking')])
			if not result[0]:
				self.report({'WARNING'}, result[1])
			
			# change current status
			G.current_task['status'] = 'checking'
			
			# reload task list
			result = G().get_task_list()
			if not result[0]:
				self.report({'WARNING'}, result[1])
			
			# export animatic video
			if G.current_task['task_type'] in ['animatic', 'film']:
				G.func.export_animatic_video_to_asset(context, G.current_project, G.current_task)
			
			# close panel
			G.functional_panel = False
		
		else:
			self.report({'WARNING'}, 'the task at checkout!')
		
		
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_load_sketch(bpy.types.Operator):
	bl_idname = "lineyka.load_sketch"
	bl_label = "Sketch"
	
	action = bpy.props.StringProperty()
	
	def execute(self, context):
		# get img_file_path
		result  = G.func.get_sketch_file_path(G.current_project, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			return{'FINISHED'}
		
		img_path = result[1]
		
		if self.action == 'plane':
			#self.report({'INFO'}, self.action)
			
			if not G.bg_image_name in bpy.data.images.keys():
				img = bpy.data.images.load(img_path)
				img.name = G.bg_image_name
			else:
				img = bpy.data.images[G.bg_image_name]
				img.filepath = img_path
				
			outliner_area = None
			up = None
			for area in bpy.context.screen.areas:
				if area.type == 'VIEW_3D':
					space_data = area.spaces.active
					space_data.show_background_images = True
					bg = space_data.background_images.new()
					bg.image = img
					
				if area.type == 'OUTLINER':
					outliner_area = area
					
				if area.type == 'IMAGE_EDITOR':
					space_data = area.spaces.active
					space_data.image = img
					up = True
					
			if not up and outliner_area:
				outliner_area.type = 'IMAGE_EDITOR'
				space_data = outliner_area.spaces.active
				space_data.image = img

		return{'FINISHED'}
		
class LINEYKA_library_preview_image(bpy.types.Operator):
	bl_idname = "lineyka.library_preview_image"
	bl_label = "Preview"
	
	asset_name = bpy.props.StringProperty()
	
	def execute(self, context):
		#print(G.db_asset.path)
		#print(G.db_asset.preview_img_path)
		#print(self.asset_name)
		#return{'FINISHED'}
		img_path = os.path.join(G.db_asset.path, G.db_asset.preview_img_path, (self.asset_name + '.png'))
		if not os.path.exists(img_path):
			self.report({'WARNING'}, ('Not Image!! ' + img_path))
		else:
			#webbrowser.open(img_path)
			if not G.preview_img_name in bpy.data.images.keys():
				G.preview_img = bpy.data.images.load(img_path)
				G.preview_img.name = G.preview_img_name
			else:
				G.preview_img = bpy.data.images[G.preview_img_name]
				G.preview_img.filepath = img_path
			
			for area in bpy.context.screen.areas:
				if area.type == 'IMAGE_EDITOR':
					space_data = area.spaces.active
					space_data.image = G.preview_img
					break
			
		return{'FINISHED'}
		
class LINEYKA_library_load_asset(bpy.types.Operator):
	bl_idname = "lineyka.library_load_asset"
	bl_label = "Load"
	
	task_data = bpy.props.StringProperty()
	
	def execute(self, context):
		task_data = json.loads(self.task_data)
		
		# add to input
		# -- get service tasks
		#pre_input_data = G.all_task_list[G.current_task['task_name']]['input']
		result = G.func.get_input_service_task(G.current_project, G.all_task_list[G.current_task['task_name']])
		if not result[0]:
			self.report({'WARNING'}, result[1])
		pre_input_data = result[1]
		all_input_name = G.current_task['asset'] + ':all_input'
		# -- -- get final task data
		result = G.db_task.read_task(G.current_project, all_input_name, G.current_task['asset_id'],  'all')
		if not result[0]:
			self.report({'WARNING'}, result[1])
			return{'FINISHED'}
			
		all_input_data = result[1]
		
		'''
		print(pre_input_data['task_name'], all_input_data['task_name'])
		return{'FINISHED'}
		'''
		
		# -- add to input
		# -- -- all input
		result = G.db_task.service_add_list_to_input(G.current_project, all_input_data, [task_data])
		if not result[0]:
			self.report({'WARNING'}, result[1])
			return{'FINISHED'}
		# -- -- pre input
		if pre_input_data['task_name'] != all_input_name:
			result = G.db_task.service_add_list_to_input(G.current_project, pre_input_data, [task_data])
			if not result[0]:
				self.report({'WARNING'}, result[1])
				return{'FINISHED'}
			
		# load object
		result = G.func.location_add_copy(context, G.current_project, [[], task_data], G.current_task, G)
		if result[0]:
			self.report({'INFO'}, ('load ' + task_data['asset']))
		else:
			self.report({'WARNING'}, result[1])
		
		# reload input list
		# -- reload task list
		G().get_task_list()
		
		# -- reload G.current_content_data
		task_tupl = G.all_task_list[G.current_task['task_name']]
		result, data = G.func.get_content_data(G.current_project, task_tupl, all_assets_data_by_name = G.all_assets_data_by_name)
		if result:
			G.current_content_data = data
		
		return{'FINISHED'}
		
class LINEYKA_model_rename_by_asset(bpy.types.Operator):
	bl_idname = 'lineyka.model_rename_by_asset'
	bl_label = 'Rename by Asset'
	
	@classmethod
	def poll(self, context):
		if G.current_task['asset_type'] == 'obj':
			return True
		else:
			return False
	
	def execute(self, context):
		result = G.func.model_rename_by_asset(context, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			return{'FINISHED'}
			
		return{'FINISHED'}
		
class LINEYKA_close_version(bpy.types.Operator):
	bl_idname = "lineyka.close_version"
	bl_label = "close"
	
	def execute(self, context):
		G.look_version_panel = False
		return{'FINISHED'}
		
class LINEYKA_location_load_exists(bpy.types.Operator):
	bl_idname = "lineyka.location_load_exists"
	bl_label = "Are you sure?"
	
	#current_data = bpy.props.StringProperty()

	def execute(self, context):
		#current_data = json.loads(self.current_data)
		result = G.func.location_load_exists(context, G.current_project, G.current_content_data, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
'''		
class LINEYKA_location_load_content(bpy.types.Operator):
	bl_idname = "lineyka.location_load_content"
	bl_label = "Load"
	
	current_data = bpy.props.StringProperty()

	def execute(self, context):
		current_data = json.loads(self.current_data)
		result = G.func.location_load_content(context, G.current_project, current_data, G.current_task)
		if result[0]:
			self.report({'INFO'}, ('load ' + current_data[0]['name']))
		else:
			self.report({'WARNING'}, result[1])
		return{'FINISHED'}
'''

class LINEYKA_location_select_all_copies(bpy.types.Operator):
	bl_idname = "lineyka.location_select_all_copies"
	bl_label = "Select All"
	
	current_data = bpy.props.StringProperty()

	def execute(self, context):
		if self.current_data == 'all':
			if not G.current_content_data:
				self.report({'WARNING'}, 'Content No Found!')
				return{'FINISHED'}
			
			ob = context.object
			current_data = None
			for key in G.current_content_data:
				if ob.name.split('.')[0] == key.split(':')[0]:
					current_data = G.current_content_data[key]
			
			if not current_data:
				self.report({'WARNING'}, 'It can not be copied!')
				return{'FINISHED'}
		else:
			current_data = json.loads(self.current_data)
		
		for ob in bpy.data.objects:
			if ob.name.split('.')[0] == current_data[0]['name']:
				ob.select = True
				context.scene.objects.active = ob
			else:
				ob.select = False
		return{'FINISHED'}

class LINEYKA_location_add_copy(bpy.types.Operator):
	bl_idname = "lineyka.location_add_copy"
	bl_label = "Link Copy"
	
	current_data = bpy.props.StringProperty()

	def execute(self, context):
		current_data = json.loads(self.current_data)
		result = G.func.location_add_copy(context, G.current_project, current_data, G.current_task, G)
		if result[0]:
			self.report({'INFO'}, ('*** load ' + current_data[0]['name']))
		else:
			self.report({'WARNING'}, result[1])
		return{'FINISHED'}

class LINEYKA_location_app_copy(bpy.types.Operator):
	bl_idname = "lineyka.location_app_copy"
	bl_label = "Add Copy"
	
	current_data = bpy.props.StringProperty()

	def execute(self, context):
		current_data = json.loads(self.current_data)
		result = G.func.location_add_copy(context, G.current_project, current_data, G.current_task, G, link=False)
		if result[0]:
			self.report({'INFO'}, ('*** load ' + current_data[0]['name']))
		else:
			self.report({'WARNING'}, result[1])
		return{'FINISHED'}
	
class LINEYKA_location_add_copy_sel(bpy.types.Operator):
	bl_idname = "lineyka.location_add_copy_sel"
	bl_label = "Add Copy"
	
	#current_data = bpy.props.StringProperty()

	def execute(self, context):
		if not G.current_content_data:
			self.report({'WARNING'}, 'Content No Found!')
			return{'FINISHED'}
		
		ob = context.object
		current_data = None
		for key in G.current_content_data:
			if ob.name.split('.')[0] == key.split(':')[0]:
				current_data = G.current_content_data[key]
		
		if not current_data:
			self.report({'WARNING'}, 'It can not be copied!')
			return{'FINISHED'}
		
		result = G.func.location_add_copy(context, G.current_project, current_data, G.current_task, G)
		if result[0]:
			self.report({'INFO'}, ('*** load ' + current_data[0]['name']))
		else:
			self.report({'WARNING'}, result[1])
		return{'FINISHED'}
		
class LINEYKA_location_add_copy_of_char(bpy.types.Operator):
	bl_idname = "lineyka.location_add_copy_of_char"
	bl_label = "Add Copy of Char"
	
	group_name = bpy.props.StringProperty()

	def execute(self, context):
		result = G.func.location_copy_char_type(context, G.downloadable_group_panel[0], [self.group_name])
		if result[0]:
			self.report({'INFO'}, ('load ' + G.downloadable_group_panel[0]['asset']))
		else:
			self.report({'WARNING'}, result[1])
		
		G.downloadable_group_panel = False
		return{'FINISHED'}
		
class LINEYKA_location_clear_content(bpy.types.Operator):
	bl_idname = "lineyka.location_clear_content"
	bl_label = "Are You Sure?"
	
	current_data = bpy.props.StringProperty()

	def execute(self, context):
		current_data = json.loads(self.current_data)
		result = G.func.location_clear_content(context, G.current_project, current_data)
		if result[0]:
			self.report({'INFO'}, ('clear ' + current_data[0]['name']))
		else:
			self.report({'WARNING'}, result[1])
		return{'FINISHED'}
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
class LINEYKA_location_clear_sel_content(bpy.types.Operator):
	bl_idname = "lineyka.location_clear_sel_content"
	bl_label = "Are You Sure?"
	
	#current_data = bpy.props.StringProperty()

	def execute(self, context):
		if not G.current_content_data:
			self.report({'WARNING'}, 'Content No Found!')
			return{'FINISHED'}
		
		ob = context.object
		current_data = None
		for key in G.current_content_data:
			if ob.name.split('.')[0] == key.split(':')[0]:
				current_data = G.current_content_data[key]
		
		if not current_data:
			self.report({'WARNING'}, 'It can not be cleared!')
			return{'FINISHED'}
		
		result = G.func.location_clear_content(context, G.current_project, current_data)
		if result[0]:
			self.report({'INFO'}, ('clear ' + current_data[0]['name']))
		else:
			self.report({'WARNING'}, result[1])
		return{'FINISHED'}
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_location_remove_content(bpy.types.Operator):
	bl_idname = "lineyka.location_remove_content"
	#bl_label = "Remove"
	bl_label = "Are You Sure?"
	
	current_data = bpy.props.StringProperty()

	def execute(self, context):
		current_data = json.loads(self.current_data)
		result = G.func.location_clear_content(context, G.current_project, current_data)
		if result[0]:
			self.report({'INFO'}, ('remove ' + current_data[0]['name']))
		else:
			self.report({'WARNING'}, result[1])

		# remove from input task
		# task().service_remove_task_from_input(self, project_name, task_data, removed_tasks_list)
		# -- get service task
		service_task = G.all_task_list[G.current_task['task_name']]['input']
		if service_task['task_type'] != 'service':
			return{'FINISHED'}

		# -- service input
		if service_task['input']:
			service_input = json.loads(service_task['input'])

		# -- removed list
		removed_tasks_list = []
		for task_name in service_input:
			if task_name.split(':')[0] == current_data[0]['name']:
				# get c_task_data
				result = G.db_task.get_tasks_data_by_name_list(G.current_project, [task_name])
				if not result[0]:
					self.report({'WARNING'}, result[1])
					return{'FINISHED'}
				removed_tasks_list.append(result[1][task_name])
				break

		result = G.db_task.service_remove_task_from_input(G.current_project, service_task, removed_tasks_list)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			
		# reload input list
		# -- reload task list
		G().get_task_list()
		
		# -- reload G.current_content_data
		task_tupl = G.all_task_list[G.current_task['task_name']]
		result, data = G.func.get_content_data(G.current_project, task_tupl, all_assets_data_by_name = G.all_assets_data_by_name)
		if result:
			G.current_content_data = data
		
		return{'FINISHED'}
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
class LINEYKA_location_remove_sel_content(bpy.types.Operator):
	bl_idname = "lineyka.location_remove_sel_content"
	#bl_label = "Remove"
	bl_label = "Are You Sure?"
	
	def execute(self, context):
		if not G.current_content_data:
			self.report({'WARNING'}, 'Content No Found!')
			return{'FINISHED'}
		
		ob = context.object
		current_data = None
		for key in G.current_content_data:
			if ob.name.split('.')[0] == key.split(':')[0]:
				current_data = G.current_content_data[key]
		
		if not current_data:
			self.report({'WARNING'}, 'It can not be removed!')
			return{'FINISHED'}
		
		result = G.func.location_clear_content(context, G.current_project, current_data)
		if result[0]:
			self.report({'INFO'}, ('remove ' + current_data[0]['name']))
		else:
			self.report({'WARNING'}, result[1])
			
		#return{'FINISHED'}

		# remove from input task
		# task().service_remove_task_from_input(self, project_name, task_data, removed_tasks_list)
		# -- get service task
		service_task = G.all_task_list[G.current_task['task_name']]['input']
		if service_task['task_type'] != 'service':
			return{'FINISHED'}

		# -- service input
		if service_task['input']:
			service_input = json.loads(service_task['input'])

		# -- removed list
		removed_tasks_list = []
		for task_name in service_input:
			if task_name.split(':')[0] == current_data[0]['name']:
				# get c_task_data
				result = G.db_task.get_tasks_data_by_name_list(G.current_project, [task_name])
				if not result[0]:
					self.report({'WARNING'}, result[1])
					return{'FINISHED'}
				removed_tasks_list.append(result[1][task_name])
				break

		result = G.db_task.service_remove_task_from_input(G.current_project, service_task, removed_tasks_list)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			
		# reload input list
		# -- reload task list
		G().get_task_list()
		
		# -- reload G.current_content_data
		task_tupl = G.all_task_list[G.current_task['task_name']]
		result, data = G.func.get_content_data(G.current_project, task_tupl, all_assets_data_by_name = G.all_assets_data_by_name)
		if result:
			G.current_content_data = data
		
		return{'FINISHED'}
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_look_sketch(bpy.types.Operator):
	bl_idname = "lineyka.look_sketch"
	bl_label = "Look Sketch"
	
	#current_data = bpy.props.StringProperty()

	def execute(self, context):
		result = G.func.look_sketch(G.current_project, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		return{'FINISHED'}
		
# ****** ANIMATIC
class LINEYKA_animatic_start(bpy.types.Operator):
	bl_idname = "lineyka.animatic_start"
	bl_label = "Animatic Start"
		
	@classmethod
	def poll(self, context):
		if G.name_scene in bpy.data.scenes.keys():
			return(False)
		
		return(True)

	def execute(self, context):
		result = G.func.make_this_animatic(context)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		return{'FINISHED'}

class LINEYKA_add_shot(bpy.types.Operator):
	bl_idname = "lineyka.add_shot"
	bl_label = "Add Shot"
	
	shot_name = bpy.props.StringProperty()
	lenth_frame = bpy.props.FloatProperty()
	
	@classmethod
	def poll(self, context):
		scene = context.scene
		# **************** test current scene
		try:
			text = bpy.data.texts[G.name_text]
		except:
			return(False)
		try:
			data = json.loads(text.as_string())
		except:
			return(False)
		if bpy.context.scene.name != G.name_scene:
			return(False)
		'''		
		# **************** get lenth frame
		frame = scene.frame_current
		if frame > scene.frame_end or frame < scene.frame_start:
			return(False)
		# -- 
		markers = scene.timeline_markers
		G.frames = []
		last_frame = scene.frame_end
		for marker in markers:
			G.frames.append(marker.frame)
			if marker.frame > frame and marker.frame < last_frame:
				last_frame = marker.frame
		G.frames.sort()
		# -- get lenth
		G.lenth = last_frame - frame
		if scene.frame_current in G.frames:
			return(False)
		
		# **************** get shot_name 
		sequences = context.scene.sequence_editor.sequences_all
		min_num = 0
		for marker in sequences:
			try:
				num = int(marker.name.split('.')[1])
				#print('*'*25, num)
			except:
				continue
			else:
				if num >= min_num:
					min_num = num
				min_num = min_num + 1
					
		name_ = '0'*(3 - len(str(min_num))) + str(min_num)
		G.shot_name = 'Shot.' + name_
		'''
		return(True)
	
	def execute(self, context):
		# add shot
		if self.shot_name in G.all_assets_data_by_name:
			self.report({'WARNING'}, 'Asset witn name "%s" already exists! Series name should be different from the existing Asset!' % self.shot_name)
			return{'FINISHED'}
		result = G.func.add_shot(context, self.shot_name, self.lenth_frame)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		return{'FINISHED'}
	
	def invoke(self, context, event):
		scene = context.scene
		# **************** get lenth frame
		frame = scene.frame_current
		if frame > scene.frame_end or frame < scene.frame_start:
			return(False)
		# -- 
		markers = scene.timeline_markers
		G.frames = []
		last_frame = scene.frame_end
		for marker in markers:
			G.frames.append(marker.frame)
			if marker.frame > frame and marker.frame < last_frame:
				last_frame = marker.frame
		G.frames.sort()
		# -- get lenth
		G.lenth = last_frame - frame
		if scene.frame_current in G.frames:
			return(False)
		
		# **************** get shot_name
		if not context.scene.sequence_editor:
			context.scene.sequence_editor_create()
		sequences = context.scene.sequence_editor.sequences_all
		min_num = 1
		for marker in sequences:
			try:
				num = int(marker.name.split('.')[1])
				#print('*'*25, num)
			except:
				continue
			else:
				if num >= min_num:
					min_num = num
				min_num = min_num + 1
					
		name_ = '0'*(3 - len(str(min_num))) + str(min_num)
		#get group name
		group_name = 'sz'
		group_id = G.all_assets_data_by_name[G.current_task['asset']]['group']
		res, row = G.db_group.get_by_id(G.current_project, group_id)
		if not res:
			return False
		else:
			group_name = row['name']
		G.shot_name = '%s_%s_Shot.%s' % (group_name, G.current_task['asset'], name_)
		
		self.lenth_frame = G.lenth
		self.shot_name = G.shot_name
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_remove_shot(bpy.types.Operator):
	bl_idname = "lineyka.remove_shot"
	bl_label = "Delete the Shot and Asset of this Shot forever?"
	
	@classmethod
	def poll(self, context):
		if not G.name_scene in bpy.data.scenes.keys():
			return(False)
			
		if context.scene.name == G.name_scene:
			return(True)
		else:
			return(False)
	
	def execute(self, context):
		# Get Shot name
		scene = None
		try:
			scene = context.scene.sequence_editor.active_strip.scene
		except:
			pass
		if not scene:
			self.report({'WARNING'}, 'Not Selected Sequence!')
			return{'FINISHED'}
		name = scene.name
		
		# TEXT
		try:
			text = bpy.data.texts[G.name_text]
		except:
			self.report({'WARNING'}, 'No text data block!')
			return{'FINISHED'}
			
		try:
			data = json.loads(text.as_string())
		except:
			self.report({'WARNING'}, 'No dictonary!')
			return{'FINISHED'}
		
		shot_data = {}
		if 'shot_data' in data.keys():
			shot_data = data['shot_data']
			del shot_data[name]
			text.clear()
			text.write(json.dumps(data, sort_keys=True, indent=4))
			
		# SCENE
		bpy.data.scenes.remove(scene, do_unlink=True)
			
		# CAMERA
		if name in bpy.data.objects.keys():
			camera = bpy.data.objects[name]
			camera.name = name + '.removed'
			camera.data.name = name + '.removed'
			bpy.data.objects.remove(camera, do_unlink=True)
		
		# BG
		bg_name = (name + '.bg')
		if bg_name in bpy.data.objects.keys():
			bg = bpy.data.objects[bg_name]
			bg.name = bg_name + '.removed'
			bg.data.name = bg_name + '.removed'
			bpy.data.objects.remove(bg, do_unlink=True)
			
		# SEQUENCE
		#sequence = context.scene.sequence_editor.active_strip
		bpy.ops.sequencer.delete()
		
		# PENCIL
		if name in bpy.data.grease_pencil.keys():
			pen = bpy.data.grease_pencil[name]
			pen.clear()
			pen.name = name + '.removed'
			try:
				bpy.data.grease_pencil.remove(pen, do_unlink=True)
			except:
				pass
		
		# ASSET
		if name in G.all_assets_data_by_name:
			result = G.db_chat.remove_asset(G.current_project, G.all_assets_data_by_name[name])
			if not result[0]:
				self.report({'WARNING'}, result[1])
		
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_rename_shot(bpy.types.Operator):
	bl_idname = "lineyka.rename_shot"
	bl_label = "Rename Shot"
	
	new_name = bpy.props.StringProperty()
	
	@classmethod
	def poll(self, context):
		if not G.name_scene in bpy.data.scenes.keys():
			return(False)
			
		if context.scene.name == G.name_scene:
			return(True)
		else:
			return(False)
			
	def execute(self, context):
		# test changed name
		if self.new_name == self.old_name:
			self.report({'WARNING'}, 'The name is not changed!')
			return{'FINISHED'}
			
		if self.new_name in G.all_assets_data_by_name:
			self.report({'WARNING'}, 'Asset witn name "%s" already exists! Series name should be different from the existing Asset!' % self.new_name)
			return{'FINISHED'}
			
		# test op
		try:
			text = bpy.data.texts[G.name_text]
		except:
			self.report({'WARNING'}, 'No text data block!')
			return{'FINISHED'}
			
		try:
			data = json.loads(text.as_string())
		except:
			self.report({'WARNING'}, 'No dictonary!')
			return{'FINISHED'}
		
		shot_data = {}	
		if 'shot_data' in data.keys():
			shot_data = data['shot_data']
			if self.old_name in shot_data.keys():
				if 'id' in shot_data[self.old_name].keys():
						if shot_data[self.old_name]['id']:
							self.report({'WARNING'}, 'you can not rename an existing Asset!')
							return{'FINISHED'}
							
		# TEXT data block
		if shot_data and self.old_name in shot_data.keys():
			data_ = shot_data[self.old_name]
			del shot_data[self.old_name]
			shot_data[self.new_name] = data_
			# write text
			data['shot_data'] = shot_data
			text.clear()
			text.write(json.dumps(data, sort_keys=True, indent=4))
		
		# SCENE
		scene = None
		if self.old_name in bpy.data.scenes.keys():
			scene = bpy.data.scenes[self.old_name]
			scene.name = self.new_name
		
		# CAMERA
		if self.old_name in bpy.data.objects.keys():
			camera = bpy.data.objects[self.old_name]
			camera.name = self.new_name
			camera.data.name = self.new_name
				
		# BG
		bg_name = (self.old_name + '.bg')
		if bg_name in bpy.data.objects.keys():
			bg = bpy.data.objects[bg_name]
			bg.name = (self.new_name + '.bg')
			bg.data.name = (self.new_name + '.bg')
		
		# SEQUENCE
		sequence = context.scene.sequence_editor.active_strip
		sequence.name = self.new_name
				
		# PENCIL
		if self.old_name in bpy.data.grease_pencil.keys():
			pen = bpy.data.grease_pencil[self.old_name]
			pen.name = self.new_name
		
		return{'FINISHED'}
	
	def invoke(self, context, event):
		self.old_name = bpy.context.scene.sequence_editor.active_strip.name
		self.new_name = self.old_name
		return context.window_manager.invoke_props_dialog(self)
	
		
class LINEYKA_go_to_animatic(bpy.types.Operator):
	bl_idname = "lineyka.go_to_animatic"
	bl_label = "Go To Animatic"
	
	@classmethod
	def poll(self, context):
		if not G.name_scene in bpy.data.scenes.keys():
			return(False)
			
		if context.scene.name == G.name_scene:
			return(False)
			
		return True
	
	def execute(self, context):
		bpy.context.screen.scene = bpy.data.scenes[G.name_scene]
		return{'FINISHED'}
		
class LINEYKA_go_to_shot(bpy.types.Operator):
	bl_idname = "lineyka.go_to_shot"
	bl_label = "Go To Shot"
	
	@classmethod
	def poll(self, context):
		if not G.name_scene in bpy.data.scenes.keys():
			return(False)
			
		if context.scene.name == G.name_scene:
			return(True)
		else:
			return(False)
	
	def execute(self, context):
		scene = None
		try:
			scene = context.scene.sequence_editor.active_strip.scene
		except:
			pass
		if not scene:
			self.report({'WARNING'}, 'Not Selected Sequence!')
			return{'FINISHED'}
		
		bpy.context.screen.scene = scene
		return{'FINISHED'}		
	
		
class LINEYKA_synchr_duration(bpy.types.Operator):
	bl_idname = "lineyka.synchr_duration"
	bl_label = "Synchr Duration"
	
	@classmethod
	def poll(self, context):
		scene = context.scene
		# **************** test current scene
		if not G.name_scene in bpy.data.scenes.keys():
			return(False)
			
		if scene.name == G.name_scene:
			self.metod = 'from_animatic'
		else:
			self.metod = 'to_animatic'
			
		return(True)
	
	def execute(self, context):
		if self.metod == 'from_animatic':
			sequence = context.scene.sequence_editor.active_strip
			# test
			if sequence.frame_offset_start < 0:
				self.report({'WARNING'}, 'not to increase the LEFT!')
				return{'FINISHED'}
			# get left border
			left_trim = sequence.animation_offset_start + sequence.frame_offset_start
			duration = sequence.frame_final_duration
			start_frame = sequence.frame_start
			still_start = sequence.frame_still_start
			
			# test scene exists
			if sequence.name in bpy.data.scenes.keys():
				shot_scene = bpy.data.scenes[sequence.name]
			else:
				self.report({'WARNING'}, 'Shot_Scene Not Found!')
				return{'FINISHED'}
				
			# trim *** shot_scene ***
			if left_trim:
				shot_scene.frame_start = left_trim + 1
			elif sequence.frame_still_start:
				if (shot_scene.frame_start + 1) < sequence.frame_still_start:
					shot_scene.frame_start = 1
				else:
					shot_scene.frame_start = shot_scene.frame_start - sequence.frame_still_start
			shot_scene.frame_end = shot_scene.frame_start + duration - 1
			
			# *** edit sequence ***
			bpy.ops.sequencer.reload()
			# -- zero borders
			sequence.frame_offset_start = 0
			sequence.animation_offset_start = 0
			sequence.animation_offset_end = 0
			sequence.frame_offset_end = 0
			sequence.frame_still_start = 0
			# -- duration
			sequence.frame_final_duration = duration
			# -- start
			sequence.frame_start = start_frame + left_trim - still_start
			
			
		elif self.metod == 'to_animatic':
			shot_scene = context.scene
			animatic_scene = bpy.data.scenes[G.name_scene]
			if shot_scene.name in animatic_scene.sequence_editor.sequences_all.keys():
				sequence = animatic_scene.sequence_editor.sequences_all[shot_scene.name]
			else:
				self.report({'WARNING'}, 'Shot_Sequence Not Found!')
			# get duration
			duration = shot_scene.frame_end - shot_scene.frame_start  + 1
			
			#condition1 = sequence.animation_offset_start + sequence.frame_offset_start == shot_scene.frame_start
			condition2 = sequence.frame_final_duration == duration
			if condition2:
				pass
			else:
				# zero borders
				sequence.frame_offset_start = 0
				sequence.animation_offset_start = 0
				sequence.animation_offset_end = 0
				sequence.frame_offset_end = 0
				# duration
				sequence.frame_final_duration = duration
		
		self.report({'INFO'}, ('Synchronization ' + sequence.name))
		return{'FINISHED'}

class LINEYKA_sound_to_shot(bpy.types.Operator):
	bl_idname = "lineyka.sound_to_shot"
	bl_label = "Sound To Shot"
	
	@classmethod
	def poll(self, context):
		scene = context.scene
		# **************** test current scene
		try:
			text = bpy.data.texts[G.name_text]
		except:
			return(False)
		try:
			data = json.loads(text.as_string())
		except:
			return(False)
		if not G.name_scene in bpy.data.scenes.keys():
			return(False)
			
		if scene.name == G.name_scene:
			return(True)
		else:
			return(False)
		
	
	def execute(self, context):
		# 
		scene = context.scene
		# test seq editor
		if not scene.sequence_editor:
			self.report({'WARNING'}, 'Not Sequences!')
			return{'FINISHED'}
			
		# get selected sequences
		#selected = []
		sequences = {}
		sequences['sounds'] = {}
		sequences['scenes'] = []
		for seq in scene.sequence_editor.sequences_all:
			if seq.select:
				#selected.append(seq)
				if seq.type == 'SOUND':
					sequences['sounds'][seq.name] = {}
					# get soundtrack data
					sequences['sounds'][seq.name]['sequence'] = seq
					sequences['sounds'][seq.name]['frame_start'] = seq.frame_start
					sequences['sounds'][seq.name]['frame_final_duration'] = seq.frame_final_duration
					sequences['sounds'][seq.name]['frame_offset_start'] = seq.frame_offset_start
					sequences['sounds'][seq.name]['animation_offset_start'] = seq.animation_offset_start
					sequences['sounds'][seq.name]['animation_offset_end'] = seq.animation_offset_end
					sequences['sounds'][seq.name]['frame_offset_end'] = seq.frame_offset_end
					if 'filepath' in seq:
						sequences['sounds'][seq.name]['filepath'] = seq.filepath
					else:
						#sequences['sounds'][seq.name]['filepath'] = bpy.data.sounds[seq.name].filepath
						sequences['sounds'][seq.name]['filepath'] = seq.sound.filepath
				elif seq.type == 'SCENE':
					sequences['scenes'].append(seq)
					
		if not sequences['sounds']:
			self.report({'WARNING'}, 'not specified Soundtrack!')
			return{'FINISHED'}
		elif not sequences['scenes']:
			self.report({'WARNING'}, 'not specified Scenes!')
			return{'FINISHED'}
		
		#print(sequences)
		
		for sequence in sequences['scenes']:
			if not sequence.name in bpy.data.scenes.keys():
				print((sequence.name + ' scene not found!'))
				continue
			shot_scene = bpy.data.scenes[sequence.name]
			if not shot_scene.sequence_editor:
				shot_scene.sequence_editor_create()
				
			# get channel
			channel = 1
			for sequence in shot_scene.sequence_editor.sequences_all:
				if channel <= sequence.channel:
					channel = sequence.channel + 1
			
			# make sound tracks
			for name in sequences['sounds']:
				# -- make sound track
				filepath = sequences['sounds'][name]['filepath']
				# -- -- get start frame
				frame_start = sequences['sounds'][name]['frame_start']
				delta = sequence.frame_start - frame_start
				frame_start = 1 - delta
				
				if not name in shot_scene.sequence_editor.sequences_all.keys():
					sound_track = shot_scene.sequence_editor.sequences.new_sound(name, filepath, channel, frame_start)
				else:
					sound_track = shot_scene.sequence_editor.sequences[name]
					# zero offsets
					sound_track.frame_offset_start = 0
					sound_track.animation_offset_start = 0
					sound_track.animation_offset_end = 0
					sound_track.frame_offset_end = 0
					sound_track.frame_final_duration = 0
					# set start data
					sound_track.frame_start = frame_start
					if 'filepath' in sound_track:
						sound_track.filepath = filepath
					else:
						sound_track.sound.filepath = filepath
					
				# -- edit sound track
				sound_track.frame_offset_start = sequences['sounds'][name]['frame_offset_start']
				sound_track.animation_offset_start = sequences['sounds'][name]['animation_offset_start']
				sound_track.animation_offset_end = sequences['sounds'][name]['animation_offset_end']
				sound_track.frame_offset_end = sequences['sounds'][name]['frame_offset_end']
				sound_track.frame_final_duration = sequences['sounds'][name]['frame_final_duration']
		
		return{'FINISHED'}
		
class LINEYKA_sound_to_animatic(bpy.types.Operator):
	bl_idname = "lineyka.sound_to_animatic"
	bl_label = "Sound To Animatic"
	
	@classmethod
	def poll(self, context):
		scene = context.scene
		if not G.name_scene in bpy.data.scenes.keys():
			return(False)
			
		if scene.name == G.name_scene:
			return(False)
		else:
			return(True)
		
	def execute(self, context):
		scene = context.scene
		animatic_scene = bpy.data.scenes[G.name_scene]
		# test seq editor
		if not scene.sequence_editor:
			self.report({'WARNING'}, 'Not Sequences!')
			return{'FINISHED'}
		elif not animatic_scene.sequence_editor:
			self.report({'WARNING'}, 'Animatic Empty!')
			return{'FINISHED'}
		elif not scene.name in animatic_scene.sequence_editor.sequences_all.keys():
			self.report({'WARNING'}, 'This Shot is not in the Animatic!')
			return{'FINISHED'}
			
		# get selected SOUND sequences
		sequences = {}
		for seq in scene.sequence_editor.sequences_all:
			if seq.select:
				if seq.type == 'SOUND':
					sequences[seq.name] = {}
					# get soundtrack data
					sequences[seq.name]['sequence'] = seq
					sequences[seq.name]['frame_start'] = seq.frame_start
					sequences[seq.name]['frame_final_duration'] = seq.frame_final_duration
					sequences[seq.name]['frame_offset_start'] = seq.frame_offset_start
					sequences[seq.name]['animation_offset_start'] = seq.animation_offset_start
					sequences[seq.name]['animation_offset_end'] = seq.animation_offset_end
					sequences[seq.name]['frame_offset_end'] = seq.frame_offset_end
					if 'filepath' in seq:
						sequences[seq.name]['filepath'] = seq.filepath
					else:
						sequences[seq.name]['filepath'] = seq.sound.filepath
				else:
					continue
		print(sequences)
		
		# get shot_sequence
		shot_sequence = animatic_scene.sequence_editor.sequences_all[scene.name]
		
		for name in sequences:
			if not animatic_scene.sequence_editor:
				animatic_scene.sequence_editor_create()
				
			# get channel
			channel = 1
			for sequence in animatic_scene.sequence_editor.sequences_all:
				if channel <= sequence.channel:
					channel = sequence.channel + 1
				
			# -- make/edit sound track
			filepath = sequences[name]['filepath']
			# -- -- get start frame
			frame_start = sequences[name]['frame_start']
			'''
			delta = shot_sequence.frame_start - frame_start
			frame_start = 1 - delta
			'''
			frame_start = shot_sequence.frame_start + frame_start -1
			
			if not name in animatic_scene.sequence_editor.sequences_all.keys():
				sound_track = animatic_scene.sequence_editor.sequences.new_sound(name, filepath, channel, frame_start)
			else:
				sound_track = animatic_scene.sequence_editor.sequences[name]
				if 'filepath' in sound_track:
					sound_track.filepath = filepath
				else:
					sound_track.sound.filepath = filepath
				sound_track.frame_start = frame_start
				
			# -- edit sound track
			sound_track.frame_offset_start = sequences[name]['frame_offset_start']
			sound_track.animation_offset_start = sequences[name]['animation_offset_start']
			sound_track.animation_offset_end = sequences[name]['animation_offset_end']
			sound_track.frame_offset_end = sequences[name]['frame_offset_end']
			sound_track.frame_final_duration = sequences[name]['frame_final_duration']
		
		return{'FINISHED'}
		
class LINEYKA_render_animatic_shots(bpy.types.Operator):
	bl_idname = "lineyka.render_animatic_shots"
	bl_label = "Render Shots"
	
	action = bpy.props.StringProperty()
	
	directory = bpy.props.StringProperty(subtype="DIR_PATH")
	
	@classmethod
	def poll(self, context):
		if G.name_scene == context.scene.name:
			return(True)
		else:
			return(False)
	
	def execute(self, context):
		scene = context.scene
		# get scene_data
		scene_start = scene.frame_start
		scene_end = scene.frame_end
		good_types = ['SCENE', 'IMAGE', 'MOVIE', 'MOVIECLIP']
		
		if self.action == 'by_shots':
			# get list sequences
			shots = {}
			for seq in scene.sequence_editor.sequences_all:
				if seq.type in good_types:
					
					# get start / end
					start = seq.frame_start + seq.frame_offset_start
					end = start + seq.frame_final_duration - 1
					
					if end < scene_start:
						continue
					if start > scene_end:
						continue
					if end > scene_end:
						end = scene_end
					if start < scene_start:
						start = scene_start
						
					# edit scene data
					scene.frame_start = start
					scene.frame_end = end
					scene.render.filepath = os.path.normpath(os.path.join(self.directory, (seq.name + '.')))
					
					# render
					bpy.ops.render.opengl(animation = True, sequencer = True)
					
					print(seq.name, start, end, scene.render.filepath)
					
			# return scene data
			scene.frame_start = scene_start
			scene.frame_end = scene_end
			
		elif self.action == 'selected_shots':
			seq = scene.sequence_editor.active_strip
			
			if seq.type in good_types:
				# get start / end
				start = seq.frame_start + seq.frame_offset_start
				end = start + seq.frame_final_duration - 1
				
				if end < scene_start:
					return({'FINISHED'})
				if start > scene_end:
					return({'FINISHED'})
				if end > scene_end:
					end = scene_end
				if start < scene_start:
					start = scene_start
					
				# edit scene data
				scene.frame_start = start
				scene.frame_end = end
				scene.render.filepath = os.path.normpath(os.path.join(self.directory, (seq.name + '.')))
				
				# render
				bpy.ops.render.opengl(animation = True, sequencer = True)
				
				print(seq.name, start, end, scene.render.filepath)
					
		elif self.action == 'render_all':
			# edit scene data
			scene.render.filepath = os.path.normpath(os.path.join(self.directory, (scene.name + '.')))
			# render
			bpy.ops.render.opengl(animation = True, sequencer = True)
			
		elif self.action == 'h.264.render_all':
			# edit scene data
			self.edit_scene_data(context)
			
			# file_path
			scene.render.filepath = os.path.normpath(os.path.join(self.directory, (scene.name + '.avi')))
			
			# render
			bpy.ops.render.opengl(animation = True, sequencer = True)
			
		elif self.action == 'h.264.by_shots':
			# edit scene data
			self.edit_scene_data(context)
			
			# get list sequences
			shots = {}
			for seq in scene.sequence_editor.sequences_all:
				if seq.type in good_types:
					
					# get start / end
					start = seq.frame_start + seq.frame_offset_start
					end = start + seq.frame_final_duration - 1
					
					if end < scene_start:
						continue
					if start > scene_end:
						continue
					if end > scene_end:
						end = scene_end
					if start < scene_start:
						start = scene_start
						
					# edit scene data
					scene.frame_start = start
					scene.frame_end = end
					scene.render.filepath = os.path.normpath(os.path.join(self.directory, (seq.name + '.avi')))
					
					# render
					bpy.ops.render.opengl(animation = True, sequencer = True)
					
					print(seq.name, start, end, scene.render.filepath)
					
			# return scene data
			scene.frame_start = scene_start
			scene.frame_end = scene_end
		
		elif self.action == 'h.264.selected_shots':
			seq = scene.sequence_editor.active_strip
			
			if seq.type in good_types:
				self.edit_scene_data(context)
				
				# get start / end
				start = seq.frame_start + seq.frame_offset_start
				end = start + seq.frame_final_duration - 1
				
				if end < scene_start:
					return({'FINISHED'})
				if start > scene_end:
					return({'FINISHED'})
				if end > scene_end:
					end = scene_end
				if start < scene_start:
					start = scene_start
					
				# edit scene data
				scene.frame_start = start
				scene.frame_end = end
				scene.render.filepath = os.path.normpath(os.path.join(self.directory, (seq.name + '.avi')))
				
				# render
				bpy.ops.render.opengl(animation = True, sequencer = True)
				
				print(seq.name, start, end, scene.render.filepath)
				
			# return scene data
			scene.frame_start = scene_start
			scene.frame_end = scene_end
			
		return({'FINISHED'})
	
	def invoke(self, context, event):
		wm = context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
	def edit_scene_data(self, context):
		# edit scene data
		context.scene.render.image_settings.file_format = 'H264'
		context.scene.render.image_settings.color_mode = 'RGB'
		context.scene.render.ffmpeg.format = 'AVI'
		context.scene.render.ffmpeg.codec = 'H264'
		context.scene.render.ffmpeg.video_bitrate = 6000
		context.scene.render.ffmpeg.audio_codec = 'MP3'
		context.scene.render.ffmpeg.audio_bitrate = 128
		
class LINEYKA_render_animatic_shots_to_asset(bpy.types.Operator):
	bl_idname = "lineyka.render_animatic_shots_to_asset"
	bl_label = "Render Shots?"
	
	action = bpy.props.StringProperty()
	
	@classmethod
	def poll(self, context):
		if G.name_scene == context.scene.name:
			return(True)
		else:
			return(False)
	
	def execute(self, context):
		series = G.current_task['series']
		result = G.func.render_animatic_shots_to_asset(context, self.action, G.current_project, series)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		return({'FINISHED'})
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	
		
class LINEYKA_animatic_add_comment(bpy.types.Operator):
	bl_idname = "lineyka.animatic_add_comment"
	bl_label = "Comment"
	
	text_of_comment = bpy.props.StringProperty()
	
	@classmethod
	def poll(self, context):
		scene = context.scene
		if scene.name != G.name_scene:
			return(False)
		try:
			self.text = bpy.data.texts[G.name_text]
		except:
			return(False)
		try:
			self.data = json.loads(self.text.as_string())
		except:
			return(False)
		
		try:
			self.old_comment = self.data['shot_data'][scene.sequence_editor.active_strip.name]['comment']
		except:
			self.old_comment = '***'
		
		return(True)
	
	def execute(self, context):
		# read text data block
		if not 'shot_data' in self.data.keys():
			self.data['shot_data'] = {}
		if not context.scene.sequence_editor.active_strip.name in self.data['shot_data'].keys():
			self.data['shot_data'][context.scene.sequence_editor.active_strip.name] = {}
		self.data['shot_data'][context.scene.sequence_editor.active_strip.name]['comment'] = self.text_of_comment
		
		# write comment
		self.text.clear()
		self.text.write(json.dumps(self.data, sort_keys=True, indent=4))
		
		return({'FINISHED'})
		
	def invoke(self, context, event):
		self.text_of_comment = self.old_comment
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_animatic_set_parent_shot(bpy.types.Operator):
	bl_idname = "lineyka.animatic_set_parent_shot"
	bl_label = "Set Parent"
	
	@classmethod
	def poll(self, context):
		return(False)
	
	def execute(self, context):
		pass
		return({'FINISHED'})
		
class LINEYKA_animatic_create_assets(bpy.types.Operator):
	bl_idname = "lineyka.animatic_create_assets"
	bl_label = "Create Assets?"
	
	action = bpy.props.StringProperty()
	
	@classmethod
	def poll(self, context):
		scene = context.scene
		if scene.name != G.name_scene:
			return(False)
		else:
			return(True)
	
	def execute(self, context):
		set_of_tasks = context.scene.set_of_tasks_enum
		group = context.scene.my_enum
		
		if group == '--select group--':
			self.report({'WARNING'}, 'Not Selected Group!')
			return({'FINISHED'})
		elif set_of_tasks == '--select Set_of_Tasks--':
			self.report({'WARNING'}, 'Not Selected Set_of_Tasks!')
			return({'FINISHED'})
		series = G.current_task['series']
		result = G.func.create_assets(context, self.action, set_of_tasks, G.loaded_group_data[group]['id'], G.current_project, series)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		return({'FINISHED'})
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_animatic_import_playblast_to_select_sequence(bpy.types.Operator):
	bl_idname = "lineyka.animatic_import_playblast_to_select_sequence"
	bl_label = "Import Playblast"
	
	action = bpy.props.StringProperty()
	
	def execute(self, context):
		if self.action == 'final':
			result = G.func.animatic_import_playblast_to_select_sequence(context, G.current_project, G.current_task, self.action)
			if not result[0]:
				self.report({'WARNING'}, result[1])
		elif self.action == 'version':
			# get versions data
			result = G.func.playblast_read_log(context, G.current_project)
			if not result[0]:
				self.report({'WARNING'}, result[1])
				return{'FINISHED'}
			G.playblast_version_data_list = result[1]
			G.playblast_version_panel = True
		elif self.action == 'off':
			G.playblast_version_panel = False
		else:
			result = G.func.animatic_import_playblast_to_select_sequence(context, G.current_project, G.current_task, self.action)
			if not result[0]:
				self.report({'WARNING'}, result[1])
		
		return({'FINISHED'})
		
class LINEYKA_animatic_return(bpy.types.Operator):
	bl_idname = "lineyka.animatic_return"
	bl_label = "Return Animatic"
	
	def execute(self, context):
		result = G.func.animatic_return(context, G.current_project, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		return({'FINISHED'})		
		
# ******* Rig Operators *************
class LINEYKA_create_empty_group(bpy.types.Operator):
	bl_idname = "lineyka.create_empty_group"
	bl_label = "Create Empty Group"
	
	name = bpy.props.StringProperty()
	
	def execute(self, context):
		result = G.func.create_empty_group(context, G.current_task, self.name)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			G().rebild_groups_list()
		else:
			self.report({'INFO'}, ('created group: ' + result[1]))
			G().rebild_groups_list()
		return{'FINISHED'}
		
	def invoke(self, context, event):
		base_name = 'Base'
		if not base_name in bpy.data.groups.keys():
			self.name = base_name
		return context.window_manager.invoke_props_dialog(self)
		
#
class LINEYKA_add_objects_to_group(bpy.types.Operator):
	bl_idname = "lineyka.add_objects_to_group"
	bl_label = "Add select objects to Group?"
	
	def execute(self, context):
		group_name = context.scene.groups_enum
		result = G.func.add_objects_to_group(context, group_name)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			G().rebild_groups_list()
		else:
			self.report({'INFO'}, ('append to group: ' + group_name))
			G().rebild_groups_list()
		return{'FINISHED'}
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_remove_group_panel(bpy.types.Operator):
	bl_idname = "lineyka.remove_group_panel"
	bl_label = "Remove Group"
	
	action = bpy.props.StringProperty()
	
	def execute(self, context):
		if self.action == 'open':
			G.removable_group_panel = True
		elif self.action == 'close':
			G.removable_group_panel = False
		return{'FINISHED'}
		
class LINEYKA_remove_group(bpy.types.Operator):
	bl_idname = "lineyka.remove_group"
	bl_label = "Are You Sure?"
	
	removable_group = bpy.props.StringProperty(name = 'Removal Group:')
	
	def execute(self, context):
		if self.removable_group in bpy.data.groups.keys():
			group = bpy.data.groups[self.removable_group]
			bpy.data.groups.remove(group, do_unlink=True)
		else:
			self.report({}, ('No Found Group: ' + self.removable_group))
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_rename_group_panel(bpy.types.Operator):
	bl_idname = "lineyka.rename_group_panel"
	bl_label = "Rename Group"
	
	action = bpy.props.StringProperty()
	
	def execute(self, context):
		if self.action == 'open':
			G.rename_group_panel = True
		elif self.action == 'close':
			G.rename_group_panel = False
		return{'FINISHED'}
		
class LINEYKA_rename_group_to_din(bpy.types.Operator):
	bl_idname = "lineyka.rename_group_to_din"
	bl_label = "Are You Sure?"
	
	name = bpy.props.StringProperty(name = 'Group to rename:')
	
	def execute(self, context):
		if self.name in bpy.data.groups.keys():
			group = bpy.data.groups[self.name]
			old_name = group.name
			group.name = old_name + '.din'
		else:
			self.report({}, ('No Found Group: ' + self.name))
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
		
class LINEYKA_unlink_objects_from_group(bpy.types.Operator):
	bl_idname = "lineyka.unlink_objects_from_group"
	bl_label = "Unlink select objects from Group?"
	
	def execute(self, context):
		group_name = context.scene.groups_enum
		result = G.func.unlink_objects_from_group(context, group_name)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			G().rebild_groups_list()
		else:
			self.report({'INFO'}, ('unlink from group: ' + group_name))
			G().rebild_groups_list()
		return{'FINISHED'}
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_add_object_to_cache_passport(bpy.types.Operator):
	bl_idname = "lineyka.add_object_to_cache_passport"
	bl_label = "Add objects to cache passport?"
	
	action = bpy.props.StringProperty()
	
	def execute(self, context):
		result = G.func.add_object_to_cache_passport(context, self.action, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		else:
			self.report({'INFO'}, 'all right!')
		return{'FINISHED'}
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_remove_object_frome_cache_passport(bpy.types.Operator):
	bl_idname = "lineyka.remove_object_frome_cache_passport"
	bl_label = "Remove objects from cache passport?"
	
	action = bpy.props.StringProperty()
	
	def execute(self, context):
		result = G.func.remove_object_frome_cache_passport(context, self.action, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		else:
			self.report({'INFO'}, 'all right!')
		return{'FINISHED'}
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_select_object_frome_cache_passport(bpy.types.Operator):
	bl_idname = "lineyka.select_object_frome_cache_passport"
	bl_label = "Select objects from cache passport"
	
	action = bpy.props.StringProperty()
	
	def execute(self, context):
		result = G.func.select_object_frome_cache_passport(context, self.action, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		
		return{'FINISHED'}
		
class LINEYKA_rename_texts_panel(bpy.types.Operator):
	bl_idname = "lineyka.rename_texts_panel"
	bl_label = "Rename Texts"
	
	action = bpy.props.StringProperty()
	
	def execute(self, context):
		if self.action == 'on':
			G.rename_texts_panel = True
		else:
			G.rename_texts_panel = False
		return{'FINISHED'}
		
class LINEYKA_rename_texts_action(bpy.types.Operator):
	bl_idname = "lineyka.rename_texts_action"
	bl_label = "Rename"
	
	name = bpy.props.StringProperty()
	
	def execute(self, context):
		if self.name.split('.')[0] == G.current_task['asset']:
			self.report({'WARNING'}, 'name is already valid!')
			return{'FINISHED'}
		
		new_name = G.current_task['asset'] + '.' + self.name
		text = bpy.data.texts[self.name]
		text.name = new_name
		
		return{'FINISHED'}

# ******* Animation Operators *******

class LINEYKA_reload_animatic(bpy.types.Operator):
	bl_idname = "lineyka.reload_animatic"
	bl_label = "Reload Animatic"
	
	def execute(self, context):
		result = G.func.reload_animatic(context, G.current_project, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		return{'FINISHED'}
		
class LINEYKA_load_reload_location(bpy.types.Operator):
	bl_idname = "lineyka.load_reload_location"
	bl_label = "Are you sure?"
	
	def execute(self, context):
		result = G.func.load_reload_location(context, G.current_project, G.current_content_data)
		if result[0]:
			self.report({'INFO'}, 'load Location!')
		else:
			self.report({'WARNING'}, result[1])
		
		return{'FINISHED'}
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_load_exists_shot_animation_content(bpy.types.Operator):
	bl_idname = "lineyka.load_exists_shot_animation_content"
	bl_label = "Are you sure?"
	
	def execute(self, context):
		result = G.func.load_exists_shot_animation_content(context, G.current_project, G.current_content_data, G.current_task)
		if result[0]:
			self.report({'INFO'}, 'load Location!')
		else:
			self.report({'WARNING'}, result[1])
		
		return{'FINISHED'}
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		

class LINEYKA_set_current_shot_camera(bpy.types.Operator):
	bl_idname = "lineyka.set_current_shot_camera"
	bl_label = "Set current shot Camera"

	def execute(self, context):
		if context.object.type != 'CAMERA':
			self.report({'WARNING'}, 'Select a Camera!')
			return{'FINISHED'}
		
		name = 'camera.' + G.current_task['asset']
		if name in bpy.data.objects.keys():
			self.report({'WARNING'}, 'Camera already exists!')
			return{'FINISHED'}
		
		# CAMERA
		camera = context.object
		camera.name = name
		camera.show_name = True
		
		# GROUP
		group = None
		if not name in bpy.data.groups.keys():
			group = bpy.data.groups.new(name)
		else:
			group = bpy.data.groups[name]
			
		if not name in group.objects.keys():
			group.objects.link(camera)
		
		return{'FINISHED'}
		
class LINEYKA_add_object_to_group_of_camera(bpy.types.Operator):
	bl_idname = "lineyka.add_object_to_group_of_camera"
	bl_label = "Add Obj to group of Camera"
	
	action = bpy.props.StringProperty()

	def execute(self, context):
		result = G.func.add_object_to_group_of_camera(context, G.current_task, self.action)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		
		return{'FINISHED'}

class LINEYKA_push_current_shot_camera(bpy.types.Operator):
	bl_idname = "lineyka.push_current_shot_camera"
	bl_label = "Push current shot Camera"
	
	comment = bpy.props.StringProperty()

	def execute(self, context):
		if not self.comment :
			self.report({'WARNING'}, 'Not Comment!')
			return{'FINISHED'}
			
		result = G.func.push_current_shot_camera(context, G.current_project, G.current_task, self.comment)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			return{'FINISHED'}
			
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

class LINEYKA_load_current_shot_camera(bpy.types.Operator):
	bl_idname = "lineyka.load_current_shot_camera"
	bl_label = "Load Camera"
	
	action = bpy.props.StringProperty()
	
	def execute(self, context):
		result = G.func.load_current_shot_camera(context, G.current_project, G.current_task, G.camera_version_data_list, self.action)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		return{'FINISHED'}

class LINEYKA_open_camera_version_panel(bpy.types.Operator):
	bl_idname = "lineyka.open_camera_version_panel"
	bl_label = "Load version Camera"
	
	action = bpy.props.StringProperty()
	
	def execute(self, context):
		if self.action == 'on':
			# get versions data
			result = G.db_log.camera_read_log(G.current_project, G.current_task)
			if not result[0]:
				self.report({'WARNING'}, result[1])
				return{'FINISHED'}
			G.camera_version_data_list = result[1]
			G.camera_version_panel = True
		else:
			G.camera_version_panel = False
		return{'FINISHED'}

		
class LINEYKA_active_shot_cam(bpy.types.Operator):
	bl_idname = "lineyka.active_shot_cam"
	bl_label = "Shot Cam"
	
	def execute(self, context):
		result = G.func.active_shot_camera(context, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		return{'FINISHED'}
		
class LINEYKA_make_playblast(bpy.types.Operator):
	bl_idname = "lineyka.make_playblast"
	bl_label = "Make Playblast"
	
	comment = bpy.props.StringProperty()
	
	def execute(self, context):
		if not self.comment:
			self.report({'WARNING'}, 'No comments!')
			return{'FINISHED'}
		
		result = G.func.make_playblast(context, G.current_project, G.current_task, self.comment)
		if not result[0]:
			self.report({'WARNING'}, result[1]) 
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_shot_animation_export_point_cache(bpy.types.Operator):
	bl_idname = "lineyka.shot_animation_export_point_cache"
	bl_label = "Export Point Cache"
	
	action = bpy.props.StringProperty()
	
	rot_x90 = bpy.props.BoolProperty(name="Convert to Y-up",
		description="Rotate 90 degrees around X to convert to y-up",
		default=False,
		)
	world_space = bpy.props.BoolProperty(name="Export into Worldspace",
		description="Transform the Vertexcoordinates into Worldspace",
		default=False,
		)
	sampling = bpy.props.EnumProperty(name='Sampling',
		description='Sampling --> frames per sample (0.1 yields 10 samples per frame)',
		items=(('0.01', '0.01', ''),
			('0.05', '0.05', ''),
			('0.1', '0.1', ''),
			('0.2', '0.2', ''),
			('0.25', '0.25', ''),
			('0.5', '0.5', ''),
			('1', '1', ''),
			('2', '2', ''),
			('3', '3', ''),
			('4', '4', ''),
			('5', '5', ''),
			('10', '10', ''),
			),
		default='1',
		)

	def execute(self, context):
		sampl = float(self.sampling)
		result = G.func.shot_animation_export_point_cache(context, G.current_project, G.current_task, self.action, sampling = sampl, world_space = self.world_space, rot_x90 = self.rot_x90)
		if not result[0]:
			self.report({'WARNING'}, result[1])
	
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_tech_anim_export_point_cache(bpy.types.Operator):
	bl_idname = "lineyka.tech_anim_export_point_cache"
	bl_label = "Export Point Cache"
	
	action = bpy.props.StringProperty()
	rot_x90 = bpy.props.BoolProperty(name="Convert to Y-up",
		description="Rotate 90 degrees around X to convert to y-up",
		default=False,
		)
	world_space = bpy.props.BoolProperty(name="Export into Worldspace",
		description="Transform the Vertexcoordinates into Worldspace",
		default=False,
		)
	sampling = bpy.props.EnumProperty(name='Sampling',
		description='Sampling --> frames per sample (0.1 yields 10 samples per frame)',
		items=(('0.01', '0.01', ''),
			('0.05', '0.05', ''),
			('0.1', '0.1', ''),
			('0.2', '0.2', ''),
			('0.25', '0.25', ''),
			('0.5', '0.5', ''),
			('1', '1', ''),
			('2', '2', ''),
			('3', '3', ''),
			('4', '4', ''),
			('5', '5', ''),
			('10', '10', ''),
			),
		default='1',
		)

	def execute(self, context):
		ws = self.world_space
		sampl = float(self.sampling)
		
		result = G.func.tech_anim_export_point_cache(context, G.current_project, G.current_task, G.tech_anim_char_assets_list[1], self.action, sampling = sampl, world_space = ws, rot_x90 = self.rot_x90)
		if not result[0]:
			self.report({'WARNING'}, result[1])
	
		self.report({'INFO'}, result[1])
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_scene_export_point_cache(bpy.types.Operator):
	bl_idname = "lineyka.scene_export_point_cache"
	bl_label = "Export Point Cache"
	
	action = bpy.props.StringProperty()
	rot_x90 = bpy.props.BoolProperty(name="Convert to Y-up",
		description="Rotate 90 degrees around X to convert to y-up",
		default=False,
		)
	world_space = bpy.props.BoolProperty(name="Export into Worldspace",
		description="Transform the Vertexcoordinates into Worldspace",
		default=False,
		)
	sampling = bpy.props.EnumProperty(name='Sampling',
		description='Sampling --> frames per sample (0.1 yields 10 samples per frame)',
		items=(('0.01', '0.01', ''),
			('0.05', '0.05', ''),
			('0.1', '0.1', ''),
			('0.2', '0.2', ''),
			('0.25', '0.25', ''),
			('0.5', '0.5', ''),
			('1', '1', ''),
			('2', '2', ''),
			('3', '3', ''),
			('4', '4', ''),
			('5', '5', ''),
			('10', '10', ''),
			),
		default='1',
		)

	def execute(self, context):
		ws = self.world_space
		sampl = float(self.sampling)
		
		# get all_char_assets_list  
		all_char_assets_list = {}
		for key in G.simulation_content_list['char_list']:
			asset_name = key.split('.')[0]
			if not asset_name in all_char_assets_list.keys():
				all_char_assets_list[asset_name] = G.all_assets_data_by_name[asset_name]
				
		print(all_char_assets_list.keys())
		
		result = G.func.tech_anim_export_point_cache(context, G.current_project, G.current_task, all_char_assets_list, self.action, sampling = sampl, world_space = ws, rot_x90 = self.rot_x90)
		if not result[0]:
			self.report({'WARNING'}, result[1])
	
		self.report({'INFO'}, str(result[1]))
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_scene_replace_din_to_cache(bpy.types.Operator):
	bl_idname = "lineyka.scene_replace_din_to_cache"
	bl_label = "Export Point Cache"
	
	#action = bpy.props.StringProperty()
	rot_x90 = bpy.props.BoolProperty(name="Convert to Y-up",
		description="Rotate 90 degrees around X to convert to y-up",
		default=False,
		)
	world_space = bpy.props.BoolProperty(name="Export into Worldspace",
		description="Transform the Vertexcoordinates into Worldspace",
		default=False,
		)
	sampling = bpy.props.EnumProperty(name='Sampling',
		description='Sampling --> frames per sample (0.1 yields 10 samples per frame)',
		items=(('0.01', '0.01', ''),
			('0.05', '0.05', ''),
			('0.1', '0.1', ''),
			('0.2', '0.2', ''),
			('0.25', '0.25', ''),
			('0.5', '0.5', ''),
			('1', '1', ''),
			('2', '2', ''),
			('3', '3', ''),
			('4', '4', ''),
			('5', '5', ''),
			('10', '10', ''),
			),
		default='1',
		)

	def execute(self, context):
		current_ob = context.object
		if current_ob.type != 'MESH':
			self.report({'WARNING'}, ('this type: ' + current_ob.type + '  Only for \"MESH\" type!'))
			return{'FINISHED'}
		
		# get exists Physics Modifiers
		exists_modif = False
		for modif in current_ob.modifiers:
			if modif.type in ['ARMATURE','CLOTH', 'SOFT_BODY', 'DYNAMIC_PAINT']:
				exists_modif = True
				break
		if not exists_modif:
			self.report({'WARNING'}, 'No Found Physics Modifiers!')
			return{'FINISHED'}
		
		### ***** MAKE CACHE
		ws = self.world_space
		sampl = float(self.sampling)
		
		# get all_char_assets_list  
		all_char_assets_list = {}
		for key in G.simulation_content_list['char_list']:
			asset_name = key.split('.')[0]
			if not asset_name in all_char_assets_list.keys():
				all_char_assets_list[asset_name] = G.all_assets_data_by_name[asset_name]
				
		result = G.func.tech_anim_export_point_cache(context, G.current_project, G.current_task, all_char_assets_list, 'mesh', sampling = sampl, world_space = ws, rot_x90 = self.rot_x90)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			return{'FINISHED'}
			
		cache_path = result[1]
		if cache_path:
			### ***** DELETE CLOTH
			for modif in current_ob.modifiers:
				if modif.type in ['ARMATURE','CLOTH','MESH_CACHE','SOFT_BODY', 'DYNAMIC_PAINT']:
					current_ob.modifiers.remove(modif)
			
			### ***** LOAD CACHE
			result = G.func.tech_anim_import_version_cache(context, current_ob.name, cache_path, make_modifier = True)
			if not result[0]:
				self.report({'WARNING'}, result[1])
		
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		
class LINEYKA_tech_anim_import_version_cache(bpy.types.Operator):
	bl_idname = "lineyka.tech_anim_import_version_cache"
	bl_label = "Import Version Cache"
	
	data = bpy.props.StringProperty()

	def execute(self, context):
		if self.data == 'open_panel':
			# get cache version list
			G.tech_anim_cache_versions_list = {}
			result = G.func.tech_anim_get_versions_list(context, G.current_task)
			if not result[0]:
				self.report({'WARNING'}, result[1])
				return{'FINISHED'}
			G.tech_anim_cache_versions_list = result[1]
			# open panel
			G.tech_anim_version_cache_panel = True
			return{'FINISHED'}
		elif self.data == 'close':
			G.tech_anim_version_cache_panel = False
			return{'FINISHED'}
		
		ob_name, file_path = json.loads(self.data)
		result = G.func.tech_anim_import_version_cache(context, ob_name, file_path)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		
		self.report({'INFO'}, result[1])
		return{'FINISHED'}
		

class LINEYKA_load_char_to_tech_anim(bpy.types.Operator):
	bl_idname = "lineyka.load_char_to_tech_anim"
	bl_label = "Load"
	
	asset_data = bpy.props.StringProperty()

	def execute(self, context):
		asset_data = json.loads(self.asset_data)
		
		result = G.func.load_char_to_tech_anim(context, G.current_project, asset_data, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			
		if len(result) == 3:
			G.tech_anim_group_panel = True
			G.tech_anim_asset_data = asset_data
			G.tech_anim_group_list = result[1]
			G.tech_anim_file_path = result[2]
	
		return{'FINISHED'}


class LINEYKA_load_obj_to_tech_anim(bpy.types.Operator):
	bl_idname = "lineyka.load_obj_to_tech_anim"
	bl_label = "Load"
	
	asset_data = bpy.props.StringProperty()

	def execute(self, context):
		asset_data = json.loads(self.asset_data)
		
		result = G.func.load_obj_to_tech_anim(context, G.current_project, asset_data, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			
		return{'FINISHED'}
		
class LINEYKA_clear_char_from_tech_anim(bpy.types.Operator):
	bl_idname = "lineyka.clear_char_from_tech_anim"
	bl_label = "Clear"
	
	asset_data = bpy.props.StringProperty()

	def execute(self, context):
		asset_data = json.loads(self.asset_data)
		
		result = G.func.clear_char_from_tech_anim(context, G.current_project, asset_data)
		if not result[0]:
			self.report({'WARNING'}, result[1])
	
		return{'FINISHED'}
		

class LINEYKA_tech_anim_load_group(bpy.types.Operator):
	bl_idname = "lineyka.tech_anim_load_group"
	bl_label = "Load Group"
	
	data = bpy.props.StringProperty()

	def execute(self, context):
		if self.data == 'close':
			G.tech_anim_group_panel = False
			return{'FINISHED'}
			
		group_name  = self.data
		
		G.func.load_char_group(context, G.tech_anim_file_path, G.current_task, group_name, link = False)
		G.tech_anim_group_panel = False
		
		return{'FINISHED'}
		
		
# 
class LINEYKA_set_position_to_tech_anim(bpy.types.Operator):
	bl_idname = "lineyka.set_position_to_tech_anim"
	bl_label = "Set Position"
	
	def execute(self, context):
		result = G.func.get_position_at_tech_anim(context, G.current_project, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			return{'FINISHED'}
		
		G.tech_anim_positions_list = result[1][0]
		G.tech_current_ob = result[1][1]
		G.tech_anim_set_position_panel = True
		
		return{'FINISHED'}
		
#
class LINEYKA_tech_anim_set_position_action(bpy.types.Operator):
	bl_idname = "lineyka.tech_anim_set_position_action"
	bl_label = "Set Position"
	
	data = bpy.props.StringProperty()
	
	def execute(self, context):
		if self.data == 'close':
			G.tech_anim_set_position_panel = False
			return({'FINISHED'})
			
		data, ob_name = json.loads(self.data)
		
		ob = bpy.data.objects[ob_name]
		
		ob.location = data[0]
		ob.rotation_euler = data[1]
		ob.scale = data[2]
		
		
		return{'FINISHED'}


class LINEYKA_rig_export_point_cache(bpy.types.Operator):
	bl_idname = "lineyka.rig_export_point_cache"
	bl_label = "Export Cache"
	
	version_name = bpy.props.StringProperty()
	rot_x90 = bpy.props.BoolProperty(name="Convert to Y-up",
		description="Rotate 90 degrees around X to convert to y-up",
		default=False,
		)
	world_space = bpy.props.BoolProperty(name="Export into Worldspace",
		description="Transform the Vertexcoordinates into Worldspace",
		default=False,
		)
	sampling = bpy.props.EnumProperty(name='Sampling',
		description='Sampling --> frames per sample (0.1 yields 10 samples per frame)',
		items=(('0.01', '0.01', ''),
			('0.05', '0.05', ''),
			('0.1', '0.1', ''),
			('0.2', '0.2', ''),
			('0.25', '0.25', ''),
			('0.5', '0.5', ''),
			('1', '1', ''),
			('2', '2', ''),
			('3', '3', ''),
			('4', '4', ''),
			('5', '5', ''),
			('10', '10', ''),
			),
		default='1',
		)
	
	def execute(self, context):
		ws = self.world_space
		if not self.version_name:
			self.report({'WARNING'}, 'Not name of Version!')
			return{'FINISHED'}
		
		result = G.func.rig_export_pc2_point_cache(context, G.current_task, self.version_name, sampling = float(self.sampling), world_space = ws, rot_x90 = self.rot_x90)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			return({'FINISHED'})
			
		self.report({'INFO'}, result[1])
			
		return({'FINISHED'})
		
	def invoke(self, context, event):
		self.sampling = '1'
		return context.window_manager.invoke_props_dialog(self)

class LINEYKA_rig_import_point_cache(bpy.types.Operator):
	bl_idname = "lineyka.rig_import_point_cache"
	bl_label = "Importr Cache"
	
	action = bpy.props.StringProperty()
	
	def execute(self, context):
		if self.action == 'version':
			#result = (True, ['super'])
			result = G.func.rig_get_versions_list_point_cache(context, G.current_task)
			if not result[0]:
				self.report({'WARNING'}, result[1])
				G.rig_version_technical_cache_panel = False
				return({'FINISHED'})
				
			G.rig_version_technical_cache_list = result[1]
			
			G.rig_version_technical_cache_panel = True
			return({'FINISHED'})
			
		elif self.action == 'close':
			G.rig_version_technical_cache_panel = False
			return({'FINISHED'})
		
		result = G.func.rig_import_pc2_point_cache(context, G.current_task, self.action)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		
		self.report({'INFO'}, result[1])
		return({'FINISHED'})
		
class LINEYKA_rig_clear_point_cache(bpy.types.Operator):
	bl_idname = "lineyka.rig_clear_point_cache"
	bl_label = "Remove Cache"
	
	def execute(self, context):
		result = G.func.rig_clear_pc2_point_cache(context, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			
		self.report({'INFO'}, result[1])
		
		return({'FINISHED'})
		
class LINEYKA_scene_add_copy_of_char(bpy.types.Operator):
	bl_idname = "lineyka.scene_add_copy_of_char"
	bl_label = "Add Copy"
	
	data = bpy.props.StringProperty()

	def execute(self, context):
		data = json.loads(self.data)
		result = G.func.scene_add_copy_of_char(context, data, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		else:
			self.report({'INFO'}, result[1])
		
		return{'FINISHED'}
		
class LINEYKA_scene_add_copy_of_obj(bpy.types.Operator):
	bl_idname = "lineyka.scene_add_copy_of_obj"
	bl_label = "Add Copy"
	
	data = bpy.props.StringProperty()

	def execute(self, context):
		data = json.loads(self.data)
		result = G.func.scene_add_copy_of_obj(context, data, G.current_task)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		else:
			self.report({'INFO'}, result[1])
		
		return{'FINISHED'}
		
class LINEYKA_convert_instance_original(bpy.types.Operator):
	bl_idname = "lineyka.convert_instance_original"
	bl_label = "Convert"
	
	action = bpy.props.StringProperty()

	def execute(self, context):
		result = G.func.convert_instance_original(context, G.simulation_content_list, self.action)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		else:
			self.report({'INFO'}, result[1])
		
		return{'FINISHED'}
		
class LINEYKA_scene_clear_of_char(bpy.types.Operator):
	bl_idname = "lineyka.scene_clear_of_char"
	bl_label = "Clear"
	
	data = bpy.props.StringProperty()

	def execute(self, context):
		data = json.loads(self.data)
		result = G.func.scene_clear_of_char(context, data)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		else:
			self.report({'INFO'}, result[1])
		
		return{'FINISHED'}
		

class LINEYKA_scene_clear_of_obj(bpy.types.Operator):
	bl_idname = "lineyka.scene_clear_of_obj"
	bl_label = "Clear"
	
	data = bpy.props.StringProperty()

	def execute(self, context):
		data = json.loads(self.data)
		result = G.func.scene_clear_of_obj(context, data)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		else:
			self.report({'INFO'}, result[1])
		
		return{'FINISHED'}
		
# TEXTURES
class LINEYKA_pack_images(bpy.types.Operator):
	bl_idname = "lineyka.pack_images"
	bl_label = "Pack"
	
	action = bpy.props.StringProperty()
	
	def execute(self, context):
		result = G.func.pack_images(context, G.current_task, self.action)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		else:
			self.report({'INFO'}, result[1])
		return{'FINISHED'}
	
class LINEYKA_open_images(bpy.types.Operator):
	bl_idname = "lineyka.open_images"
	bl_label = "Open Images"
	
	my_item = [('-select application-',)*3]
	
	if not G.ext_dict:
		G().get_ext_dict()
	
	for key in G.ext_dict:
		my_item.append((G.ext_dict[key],)*3)
	
	open_by = bpy.props.EnumProperty(name = 'Open by:', items = tuple(my_item))
	
	filepath = bpy.props.StringProperty(subtype="FILE_PATH")
	
	def execute(self, context):
		if self.open_by == '-select application-':
			self.report({'WARNING'}, 'application is not selected!')
			return{'FINISHED'}
		result, comment = G.func.open_images(context, self.open_by, self.filepath)
		
		self.report({'INFO'}, self.filepath)
		return{'FINISHED'}
	
	def invoke(self, context, event):
		result, path = G.func.get_textures_path(context, G.current_task)
		if result:
			self.filepath = path + '/'
		else:
			self.filepath = G.current_task['asset_path']
		wm = context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
class LINEYKA_convert_image_format(bpy.types.Operator):
	bl_idname = "lineyka.convert_image_format"
	bl_label = "convert image format"
	
	action = bpy.props.StringProperty()
	
	def execute(self, context):
		result = G.func.convert_image_format(context, G.current_task, self.action)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		else:
			self.report({'INFO'}, result[1])
		return{'FINISHED'}
	

class LINEYKA_switch_image_format(bpy.types.Operator):
	bl_idname = "lineyka.switch_image_format"
	bl_label = "switch image format"
	
	action = bpy.props.StringProperty()
	
	def execute(self, context):
		result = G.func.switch_image_format(context, G.current_task, self.action)
		if not result[0]:
			self.report({'WARNING'}, result[1])
		else:
			self.report({'INFO'}, result[1])
		return{'FINISHED'}

		
class LINEYKA_accept_task(bpy.types.Operator):
	bl_idname = "lineyka.accept_task"
	bl_label = "Accept?"
	
	def execute(self, context):
		# accept
		result = G.db_task.readers_accept_task(G.current_project, G.current_task, G.current_user)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			return{'FINISHED'}
		
		# rebild task
		result = G().get_task_list()
		if not result[0]:
			self.report({'WARNING'}, result[1])
			return{'FINISHED'}
			
		G.activate_reader_task = False
			
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)


class LINEYKA_to_rework_task(bpy.types.Operator):
	bl_idname = "lineyka.to_rework_task"
	bl_label = "To Rework?"
	
	def execute(self, context):
		#accept in .db
		result = G.db_task.rework_task(G.current_project, G.current_task, current_user = G.current_user)
		if not result[0]:
			if result[1] == 'not chat!':
				self.report({'WARNING'}, result[1])
				
				# run chat
				result = G.func.chat_run(G.current_project, G.current_user, G.current_task)
				if not result[0]:
					self.report({'WARNING'}, result[1])
				
				return{'FINISHED'}
			
			self.report({'WARNING'}, result[1])
			return{'FINISHED'}
			
		# rebild task
		result = G().get_task_list()
		if not result[0]:
			self.report({'WARNING'}, result[1])
			return{'FINISHED'}
			
		G.activate_reader_task = False
		
		return{'FINISHED'}

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
		

class LINEYKA_edit_extensions_list(bpy.types.Operator):
	bl_idname = "lineyka.edit_extensions_list"
	bl_label = "Edit Extensions List"
	
	action = bpy.props.StringProperty(name="action:")
	extension = bpy.props.StringProperty(name="extension:")
	
	@classmethod
	def poll(self, context):
		return True
	
	def execute(self, context):
		if self.action == 'add':
			action = 'ADD'
		elif self.action == 'remove':
			action = 'REMOVE'
		else:
			action = self.action
		
		result, data = G.db_studio.edit_extension(self.extension, action)
		
		if not result:
			self.report({'WARNING'}, data)
		else:
			self.report({'INFO'}, data)
		
		return{'FINISHED'}
		
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	

class LINEYKA_open_source_file(bpy.types.Operator):
	bl_idname = "lineyka.open_source_file"
	bl_label = "Open"
	
	task_data = bpy.props.StringProperty()
	
	def execute(self, context):
		# get activity
		activity = None
		if G.current_task['asset_type'] == 'char':
			activity = context.scene.activity_enum
		elif G.current_task['asset_type'] == 'obj':
			activity = 'model'
			
		if activity == '--select activity--':
			self.report({'WARNING'}, 'Activity is not selected!')
			return{'FINISHED'}
		
		# open file
		load_task_data = json.loads(self.task_data)
		load_task_data['activity'] = activity
		result = G.func.open_source_file(G.current_project, G.current_task, load_task_data)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			return{'FINISHED'}
		
		self.report({'INFO'}, ('open '+ load_task_data['asset']))
		return{'FINISHED'}
	
class LINEYKA_load_source_file(bpy.types.Operator):
	bl_idname = "lineyka.load_source_file"
	bl_label = "Load"
	
	task_data = bpy.props.StringProperty()
	
	def execute(self, context):
		# get activity
		activity = None
		if G.current_task['asset_type'] == 'char':
			activity = context.scene.activity_enum
		elif G.current_task['asset_type'] == 'obj':
			activity = 'model'
			
		if activity == '--select activity--':
			self.report({'WARNING'}, 'Activity is not selected!')
			return{'FINISHED'}
		
		# open file
		load_task_data = json.loads(self.task_data)
		load_task_data['activity'] = activity
		result = G.func.load_source_file(context, G.current_project, G.current_task, load_task_data)
		if not result[0]:
			self.report({'WARNING'}, result[1])
			return{'FINISHED'}
		
		self.report({'INFO'}, activity)
		return{'FINISHED'}

# ****** PASS
class LINEYKA_pass(bpy.types.Operator):
	bl_idname = "lineyka.pass"
	bl_label = "Pass"
	
	@classmethod
	def poll(self, context):
		return False

	def execute(self, context):
		self.report({'INFO'}, 'Pass')
		return{'FINISHED'}
    
    
def register():
	bpy.utils.register_class(Help)
	bpy.utils.register_class(Setting)
	bpy.utils.register_class(LINEYKA_help)
	bpy.utils.register_class(SET_studio_folder)
	bpy.utils.register_class(SET_set_file_path)
	bpy.utils.register_class(Tasks_Panel)
	bpy.utils.register_class(TASK_distrib)
	bpy.utils.register_class(TASK_reader_distrib)
	bpy.utils.register_class(DISTRIB_task_panel)
	bpy.utils.register_class(DISTRIB_reader_task_panel)
	bpy.utils.register_class(DISTRIB_reader_task_panel_sequence_editor)
	bpy.utils.register_class(LINEYKA_pass)
	bpy.utils.register_class(USER_registration)
	bpy.utils.register_class(USER_login)
	bpy.utils.register_class(GET_project)
	bpy.utils.register_class(LINEYKA_look_sketch)
	bpy.utils.register_class(LINEYKA_library_preview_image)
	bpy.utils.register_class(LINEYKA_library_load_asset)
	bpy.utils.register_class(Lineyka_reload_task_list)
	#bpy.utils.register_class(LINEYKA_edit_extensions_list)
	bpy.utils.register_class(LINEYKA_open_source_file)
	bpy.utils.register_class(LINEYKA_load_source_file)
	bpy.utils.register_class(Lineyka_load_group_list)
	bpy.utils.register_class(Lineyka_load_content_list_of_group)
	# readers
	bpy.utils.register_class(LINEYKA_accept_task)
	bpy.utils.register_class(LINEYKA_to_rework_task)
	# look 
	bpy.utils.register_class(VERSION_look)
	bpy.utils.register_class(VERSION_look_in_sequence_editor)
	bpy.utils.register_class(LINEYKA_close_version)
	bpy.utils.register_class(LINEYKA_look)
	bpy.utils.register_class(LINEYKA_look_activity)
	bpy.utils.register_class(LINEYKA_look_version)
	# open
	bpy.utils.register_class(LINEYKA_open)
	bpy.utils.register_class(LINEYKA_open_version)
	# tz chat
	bpy.utils.register_class(LINEYKA_tz)
	bpy.utils.register_class(LINEYKA_chat)
	# task working
	bpy.utils.register_class(LINEYKA_push)
	bpy.utils.register_class(LINEYKA_report)
	bpy.utils.register_class(LINEYKA_load_sketch)
	bpy.utils.register_class(LINEYKA_model_rename_by_asset)
	# bpy.utils.register_class(LINEYKA_location_load_content)
	bpy.utils.register_class(LINEYKA_location_select_all_copies)
	bpy.utils.register_class(LINEYKA_location_add_copy)
	bpy.utils.register_class(LINEYKA_location_app_copy)
	bpy.utils.register_class(LINEYKA_location_add_copy_sel)
	bpy.utils.register_class(LINEYKA_location_add_copy_of_char)
	bpy.utils.register_class(LINEYKA_location_remove_content)
	bpy.utils.register_class(LINEYKA_location_remove_sel_content)
	bpy.utils.register_class(LINEYKA_location_clear_content)
	bpy.utils.register_class(LINEYKA_location_clear_sel_content)
	bpy.utils.register_class(LINEYKA_location_load_exists)
	bpy.utils.register_class(LINEYKA_create_empty_group)
	bpy.utils.register_class(LINEYKA_add_objects_to_group)
	bpy.utils.register_class(LINEYKA_remove_group_panel)
	bpy.utils.register_class(LINEYKA_rename_group_panel)
	bpy.utils.register_class(LINEYKA_rename_group_to_din)
	bpy.utils.register_class(LINEYKA_remove_group)
	bpy.utils.register_class(LINEYKA_unlink_objects_from_group)
	bpy.utils.register_class(LINEYKA_add_object_to_cache_passport)
	bpy.utils.register_class(LINEYKA_remove_object_frome_cache_passport)
	bpy.utils.register_class(LINEYKA_select_object_frome_cache_passport)
	bpy.utils.register_class(LINEYKA_rename_texts_panel)
	bpy.utils.register_class(LINEYKA_rename_texts_action)
	# animation
	bpy.utils.register_class(LINEYKA_reload_animatic)
	bpy.utils.register_class(LINEYKA_load_reload_location)
	bpy.utils.register_class(LINEYKA_load_exists_shot_animation_content)
	bpy.utils.register_class(LINEYKA_set_current_shot_camera)
	bpy.utils.register_class(LINEYKA_push_current_shot_camera)
	bpy.utils.register_class(LINEYKA_add_object_to_group_of_camera)
	bpy.utils.register_class(LINEYKA_load_current_shot_camera)
	bpy.utils.register_class(LINEYKA_open_camera_version_panel)
	bpy.utils.register_class(LINEYKA_make_playblast)
	bpy.utils.register_class(LINEYKA_shot_animation_export_point_cache)
	bpy.utils.register_class(LINEYKA_tech_anim_export_point_cache)
	bpy.utils.register_class(LINEYKA_active_shot_cam)
	bpy.utils.register_class(LINEYKA_tech_anim_import_version_cache)
	# functional panels
	bpy.utils.register_class(FUNCTIONAL_tasks_wiew_3d)
	bpy.utils.register_class(FUNCTIONAL_load_open_panel)
	bpy.utils.register_class(FUNCTIONAL_render_scene_content)
	bpy.utils.register_class(FUNCTIONAL_scene_char_content)
	bpy.utils.register_class(FUNCTIONAL_scene_obj_content)
	bpy.utils.register_class(FUNCTIONAL_scene_point_cache)
	bpy.utils.register_class(FUNCTIONAL_model)
	bpy.utils.register_class(FUNCTIONAL_textures)
	bpy.utils.register_class(FUNCTIONAL_group)
	bpy.utils.register_class(FUNCTIONAL_removable_group)
	bpy.utils.register_class(FUNCTIONAL_group_to_rename)
	bpy.utils.register_class(FUNCTIONAL_rig)
	bpy.utils.register_class(FUNCTIONAL_technical_cache)
	bpy.utils.register_class(FUNCTIONAL_version_technical_cache)
	bpy.utils.register_class(FUNCTIONAL_rename_texts_panel)
	bpy.utils.register_class(FUNCTIONAL_location)
	bpy.utils.register_class(FUNCTIONAL_downloadable_group_list)
	bpy.utils.register_class(FUNCTIONAL_downloadable_group_list_SE)
	bpy.utils.register_class(FUNCTIONAL_location_library)
	bpy.utils.register_class(FUNCTIONAL_edit_camera)
	bpy.utils.register_class(FUNCTIONAL_camera_version_panel)
	bpy.utils.register_class(FUNCTIONAL_animation_shot)
	bpy.utils.register_class(FUNCTIONAL_playblast)
	bpy.utils.register_class(FUNCTIONAL_shot_animation_point_cache)
	bpy.utils.register_class(FUNCTIONAL_tech_anim_version_cache_panel)
	bpy.utils.register_class(FUNCTIONAL_tech_anim_load_char)
	bpy.utils.register_class(FUNCTIONAL_tech_anim_downloadable_group_list)
	bpy.utils.register_class(FUNCTIONAL_tech_anim_set_position_as)
	bpy.utils.register_class(FUNCTIONAL_tech_anim_load_obj)
	bpy.utils.register_class(FUNCTIONAL_textures_addition)
	# animatic
	bpy.utils.register_class(FUNCTIONAL_tasks_sequence_editor)
	bpy.utils.register_class(LINEYKA_animatic_panel)
	bpy.utils.register_class(LINEYKA_animatic_to_shot_animation_panel)
	bpy.utils.register_class(LINEYKA_animatic_import_sequences)
	bpy.utils.register_class(LINEYKA_animatic_playblast_version_panel)
	bpy.utils.register_class(LINEYKA_sound_to_shot)
	bpy.utils.register_class(LINEYKA_sound_to_animatic)
	bpy.utils.register_class(LINEYKA_go_to_animatic)
	bpy.utils.register_class(LINEYKA_go_to_shot)
	bpy.utils.register_class(LINEYKA_synchr_duration)
	bpy.utils.register_class(LINEYKA_animatic_start)
	bpy.utils.register_class(LINEYKA_add_shot)
	bpy.utils.register_class(LINEYKA_remove_shot)
	bpy.utils.register_class(LINEYKA_rename_shot)
	bpy.utils.register_class(LINEYKA_render_animatic_shots)
	bpy.utils.register_class(LINEYKA_animatic_add_comment)
	bpy.utils.register_class(LINEYKA_animatic_set_parent_shot)
	bpy.utils.register_class(LINEYKA_animatic_create_assets)
	bpy.utils.register_class(LINEYKA_render_animatic_shots_to_asset)
	bpy.utils.register_class(LINEYKA_animatic_import_playblast_to_select_sequence)
	bpy.utils.register_class(LINEYKA_animatic_return)
	# tech_anim
	bpy.utils.register_class(LINEYKA_load_char_to_tech_anim)
	bpy.utils.register_class(LINEYKA_tech_anim_load_group)
	bpy.utils.register_class(LINEYKA_clear_char_from_tech_anim)
	bpy.utils.register_class(LINEYKA_set_position_to_tech_anim)
	bpy.utils.register_class(LINEYKA_tech_anim_set_position_action)
	bpy.utils.register_class(LINEYKA_load_obj_to_tech_anim)
	# rig
	bpy.utils.register_class(LINEYKA_rig_import_point_cache)
	bpy.utils.register_class(LINEYKA_rig_export_point_cache)
	bpy.utils.register_class(LINEYKA_rig_clear_point_cache)
	# simulation_render
	bpy.utils.register_class(LINEYKA_scene_add_copy_of_char)
	bpy.utils.register_class(LINEYKA_scene_add_copy_of_obj)
	bpy.utils.register_class(LINEYKA_convert_instance_original)
	bpy.utils.register_class(LINEYKA_scene_clear_of_char)
	bpy.utils.register_class(LINEYKA_scene_clear_of_obj)
	bpy.utils.register_class(LINEYKA_scene_export_point_cache)
	bpy.utils.register_class(LINEYKA_scene_replace_din_to_cache)
	# textures
	bpy.utils.register_class(LINEYKA_pack_images)
	bpy.utils.register_class(LINEYKA_convert_image_format)
	bpy.utils.register_class(LINEYKA_switch_image_format)
	bpy.utils.register_class(LINEYKA_open_images)
	
	# drop-down menu
	set_fields()
	set_activity_list()
	set_group_list()
	set_set_of_tasks_list()
	set_groups_list()
	set_tasks_list_type()
	
def unregister():
	bpy.utils.unregister_class(Help)
	bpy.utils.unregister_class(Setting)
	bpy.utils.unregister_class(LINEYKA_help)
	bpy.utils.unregister_class(SET_studio_folder)
	bpy.utils.unregister_class(SET_set_file_path)
	bpy.utils.unregister_class(Tasks_Panel)
	bpy.utils.unregister_class(TASK_distrib)
	bpy.utils.unregister_class(TASK_reader_distrib)
	bpy.utils.unregister_class(DISTRIB_task_panel)
	bpy.utils.unregister_class(DISTRIB_reader_task_panel)
	bpy.utils.unregister_class(DISTRIB_reader_task_panel_sequence_editor)
	bpy.utils.unregister_class(LINEYKA_pass)
	bpy.utils.unregister_class(USER_registration)
	bpy.utils.unregister_class(USER_login)
	bpy.utils.unregister_class(GET_project)
	bpy.utils.unregister_class(LINEYKA_look_sketch)
	bpy.utils.unregister_class(LINEYKA_library_preview_image)
	bpy.utils.unregister_class(LINEYKA_library_load_asset)
	bpy.utils.unregister_class(Lineyka_reload_task_list)
	#bpy.utils.unregister_class(LINEYKA_edit_extensions_list)
	bpy.utils.unregister_class(LINEYKA_open_source_file)
	bpy.utils.unregister_class(LINEYKA_load_source_file)
	bpy.utils.unregister_class(Lineyka_load_group_list)
	bpy.utils.unregister_class(Lineyka_load_content_list_of_group)
	# readers
	bpy.utils.unregister_class(LINEYKA_accept_task)
	bpy.utils.unregister_class(LINEYKA_to_rework_task)
	# look 
	bpy.utils.unregister_class(VERSION_look)
	bpy.utils.unregister_class(VERSION_look_in_sequence_editor)
	bpy.utils.unregister_class(LINEYKA_close_version)
	bpy.utils.unregister_class(LINEYKA_look)
	bpy.utils.unregister_class(LINEYKA_look_activity)
	bpy.utils.unregister_class(LINEYKA_look_version)
	# open
	bpy.utils.unregister_class(LINEYKA_open)
	bpy.utils.unregister_class(LINEYKA_open_version)
	# tz chat
	bpy.utils.unregister_class(LINEYKA_tz)
	bpy.utils.unregister_class(LINEYKA_chat)
	# task working
	bpy.utils.unregister_class(LINEYKA_push)
	bpy.utils.unregister_class(LINEYKA_report)
	bpy.utils.unregister_class(LINEYKA_load_sketch)
	bpy.utils.unregister_class(LINEYKA_model_rename_by_asset)
	# bpy.utils.unregister_class (LINEYKA_location_load_content)
	bpy.utils.unregister_class(LINEYKA_location_select_all_copies)
	bpy.utils.unregister_class(LINEYKA_location_add_copy)
	bpy.utils.unregister_class(LINEYKA_location_app_copy)
	bpy.utils.unregister_class(LINEYKA_location_add_copy_sel)
	bpy.utils.unregister_class(LINEYKA_location_add_copy_of_char)
	bpy.utils.unregister_class(LINEYKA_location_remove_content)
	bpy.utils.unregister_class(LINEYKA_location_remove_sel_content)
	bpy.utils.unregister_class(LINEYKA_location_clear_content)
	bpy.utils.unregister_class(LINEYKA_location_clear_sel_content)
	bpy.utils.unregister_class(LINEYKA_location_load_exists)
	bpy.utils.unregister_class(LINEYKA_create_empty_group)
	bpy.utils.unregister_class(LINEYKA_add_objects_to_group)
	bpy.utils.unregister_class(LINEYKA_remove_group_panel)
	bpy.utils.unregister_class(LINEYKA_rename_group_panel)
	bpy.utils.unregister_class(LINEYKA_rename_group_to_din)
	bpy.utils.unregister_class(LINEYKA_remove_group)
	bpy.utils.unregister_class(LINEYKA_unlink_objects_from_group)
	bpy.utils.unregister_class(LINEYKA_add_object_to_cache_passport)
	bpy.utils.unregister_class(LINEYKA_remove_object_frome_cache_passport)
	bpy.utils.unregister_class(LINEYKA_select_object_frome_cache_passport)
	bpy.utils.unregister_class(LINEYKA_rename_texts_panel)
	bpy.utils.unregister_class(LINEYKA_rename_texts_action)
	# animation
	bpy.utils.unregister_class(LINEYKA_reload_animatic)
	bpy.utils.unregister_class(LINEYKA_load_reload_location)
	bpy.utils.unregister_class(LINEYKA_load_exists_shot_animation_content)
	bpy.utils.unregister_class(LINEYKA_set_current_shot_camera)
	bpy.utils.unregister_class(LINEYKA_push_current_shot_camera)
	bpy.utils.unregister_class(LINEYKA_add_object_to_group_of_camera)
	bpy.utils.unregister_class(LINEYKA_load_current_shot_camera)
	bpy.utils.unregister_class(LINEYKA_open_camera_version_panel)
	bpy.utils.unregister_class(LINEYKA_make_playblast)
	bpy.utils.unregister_class(LINEYKA_shot_animation_export_point_cache)
	bpy.utils.unregister_class(LINEYKA_tech_anim_export_point_cache)
	bpy.utils.unregister_class(LINEYKA_active_shot_cam)
	bpy.utils.unregister_class(LINEYKA_tech_anim_import_version_cache)
	# functional panels
	bpy.utils.unregister_class(FUNCTIONAL_tasks_wiew_3d)
	bpy.utils.unregister_class(FUNCTIONAL_load_open_panel)
	bpy.utils.unregister_class(FUNCTIONAL_render_scene_content)
	bpy.utils.unregister_class(FUNCTIONAL_scene_char_content)
	bpy.utils.unregister_class(FUNCTIONAL_scene_obj_content)
	bpy.utils.unregister_class(FUNCTIONAL_scene_point_cache)
	bpy.utils.unregister_class(FUNCTIONAL_model)
	bpy.utils.unregister_class(FUNCTIONAL_textures)
	bpy.utils.unregister_class(FUNCTIONAL_textures_addition)
	bpy.utils.unregister_class(FUNCTIONAL_group)
	bpy.utils.unregister_class(FUNCTIONAL_removable_group)
	bpy.utils.unregister_class(FUNCTIONAL_group_to_rename)
	bpy.utils.unregister_class(FUNCTIONAL_rig)
	bpy.utils.unregister_class(FUNCTIONAL_technical_cache)
	bpy.utils.unregister_class(FUNCTIONAL_version_technical_cache)
	bpy.utils.unregister_class(FUNCTIONAL_rename_texts_panel)
	bpy.utils.unregister_class(FUNCTIONAL_location)
	bpy.utils.unregister_class(FUNCTIONAL_downloadable_group_list)
	bpy.utils.unregister_class(FUNCTIONAL_downloadable_group_list_SE)
	bpy.utils.unregister_class(FUNCTIONAL_location_library)
	bpy.utils.unregister_class(FUNCTIONAL_edit_camera)
	bpy.utils.unregister_class(FUNCTIONAL_camera_version_panel)
	bpy.utils.unregister_class(FUNCTIONAL_animation_shot)
	bpy.utils.unregister_class(FUNCTIONAL_playblast)
	bpy.utils.unregister_class(FUNCTIONAL_shot_animation_point_cache)
	bpy.utils.unregister_class(FUNCTIONAL_tech_anim_load_char)
	bpy.utils.unregister_class(FUNCTIONAL_tech_anim_version_cache_panel)
	bpy.utils.unregister_class(FUNCTIONAL_tech_anim_downloadable_group_list)
	bpy.utils.unregister_class(FUNCTIONAL_tech_anim_set_position_as)
	bpy.utils.unregister_class(FUNCTIONAL_tech_anim_load_obj)
	# animatic
	bpy.utils.unregister_class(LINEYKA_sound_to_shot)
	bpy.utils.unregister_class(LINEYKA_sound_to_animatic)
	bpy.utils.unregister_class(LINEYKA_animatic_to_shot_animation_panel)
	bpy.utils.unregister_class(LINEYKA_animatic_import_sequences)
	bpy.utils.unregister_class(LINEYKA_animatic_playblast_version_panel)
	bpy.utils.unregister_class(LINEYKA_go_to_animatic)
	bpy.utils.unregister_class(LINEYKA_go_to_shot)
	bpy.utils.unregister_class(LINEYKA_synchr_duration)
	bpy.utils.unregister_class(LINEYKA_animatic_panel)
	bpy.utils.unregister_class(LINEYKA_animatic_start)
	bpy.utils.unregister_class(LINEYKA_add_shot)
	bpy.utils.unregister_class(LINEYKA_remove_shot)
	bpy.utils.unregister_class(LINEYKA_rename_shot)
	bpy.utils.unregister_class(LINEYKA_render_animatic_shots)
	bpy.utils.unregister_class(FUNCTIONAL_tasks_sequence_editor)
	bpy.utils.unregister_class(LINEYKA_animatic_add_comment)
	bpy.utils.unregister_class(LINEYKA_animatic_set_parent_shot)
	bpy.utils.unregister_class(LINEYKA_animatic_create_assets)
	bpy.utils.unregister_class(LINEYKA_render_animatic_shots_to_asset)
	bpy.utils.unregister_class(LINEYKA_animatic_import_playblast_to_select_sequence)
	bpy.utils.unregister_class(LINEYKA_animatic_return)
	# tech_anim
	bpy.utils.unregister_class(LINEYKA_load_char_to_tech_anim)
	bpy.utils.unregister_class(LINEYKA_tech_anim_load_group)
	bpy.utils.unregister_class(LINEYKA_clear_char_from_tech_anim)
	bpy.utils.unregister_class(LINEYKA_set_position_to_tech_anim)
	bpy.utils.unregister_class(LINEYKA_tech_anim_set_position_action)
	bpy.utils.unregister_class(LINEYKA_load_obj_to_tech_anim)
	# rig
	bpy.utils.unregister_class(LINEYKA_rig_import_point_cache)
	bpy.utils.unregister_class(LINEYKA_rig_export_point_cache)
	bpy.utils.unregister_class(LINEYKA_rig_clear_point_cache)
	# simulation_render
	bpy.utils.unregister_class(LINEYKA_scene_add_copy_of_char)
	bpy.utils.unregister_class(LINEYKA_scene_add_copy_of_obj)
	bpy.utils.unregister_class(LINEYKA_convert_instance_original)
	bpy.utils.unregister_class(LINEYKA_scene_clear_of_char)
	bpy.utils.unregister_class(LINEYKA_scene_clear_of_obj)
	bpy.utils.unregister_class(LINEYKA_scene_export_point_cache)
	bpy.utils.unregister_class(LINEYKA_scene_replace_din_to_cache)
	# textures
	bpy.utils.unregister_class(LINEYKA_pack_images)
	bpy.utils.unregister_class(LINEYKA_convert_image_format)
	bpy.utils.unregister_class(LINEYKA_switch_image_format)
	bpy.utils.unregister_class(LINEYKA_open_images)
	
#register()
#unregister()
