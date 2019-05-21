#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PySide import QtCore, QtGui, QtUiTools, QtSql
import os
import shutil
import webbrowser
import getpass
from functools import partial
import json
import random
import subprocess
import datetime
'''
import ui
import edit_db as db
'''
class G(object):
	pass

class lineyka_chat:
	
	#def chat_ui(self, root):
	def __init__(self, MW):
		G.MW = MW
		
		task_data = MW.current_task
		nik_name = MW.current_user
		project = MW.current_project
		
		# make widjet
		ui_path = MW.chat_main_path
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(ui_path)
		#file.open(QtCore.QFile.ReadOnly)
		window = G.MW.chatMain = loader.load(file, MW)
		file.close()
		
		# fill meta data
		window.setWindowTitle('Lineyka Chat')
		window.chat_nik_name_label.setText(nik_name)
		window.chat_asset_name_label.setText(task_data['asset'])
		window.chat_task_name_label.setText(task_data['task_name'].split(':')[1])
		
		# button connect
		window.close_button.clicked.connect(partial(MW.close_window, window))
		window.reload_button.clicked.connect(partial(self.chat_load_topics, window))
		window.chat_add_topic_button.clicked.connect(partial(self.chat_new_topic_ui, window))
		
		window.show()
		
		self.chat_load_topics(window)
		
		print(MW.chat_status)
		
		# edit read_status
		if G.MW.chat_status == 'manager':
			result = G.MW.db_chat.task_edit_rid_status_read(project, task_data, nik_name)
			if not result[0]:
				G.MW.message(result[1], 2)
				return
		
		
	def chat_load_topics(self, window):
		task_data = G.MW.current_task
		project_name = G.MW.current_project
		
		# read chat data
		topics = None
		result = G.MW.db_chat.read_the_chat(project_name, task_data['task_name'])
		if not result[0]:
			#G.MW.message(result[1], 2)
			pass
		else:
			topics = result[1]
		
		tool_box = window.chat_tool_box
		# clear tool box
		i = tool_box.count()
		while i > -1:
			try:
				tool_box.removeItem(i)
			except:
				pass
			i = i-1
		
		# size item
		tool_box.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
		
		if topics:
			for topic in topics:
				dt = topic['date_time']
				date = str(dt.year) + '/' + str(dt.month) + '/' + str(dt.day) + '/' + str(dt.hour) + ':' + str(dt.minute)
				header = topic['author'] + ' '*5 + date
				
				lines = json.loads(topic['topic'])
				
				topic_widget = QtGui.QFrame()
				v_layout = QtGui.QVBoxLayout()
				for key in lines:
					widget = QtGui.QFrame(parent = topic_widget)
					layout = QtGui.QHBoxLayout()
					# button
					if lines[key][1]:
						button = QtGui.QPushButton(QtGui.QIcon(lines[key][1]), '', parent = widget)
					else:
						button = QtGui.QPushButton('not Image', parent = widget)
					button.setIconSize(QtCore.QSize(100, 100))
					button.setFixedSize(100, 100)
					button.img_path = lines[key][0]
					button.clicked.connect(partial(self.chat_image_view_ui, button))
					layout.addWidget(button)
					
					# text field
					text_field = QtGui.QTextEdit(lines[key][2], parent = widget)
					text_field.setMaximumHeight(100)
					layout.addWidget(text_field)
					
					widget.setLayout(layout)
					#print(widget.sizeHint())
					
					v_layout.addWidget(widget)
				topic_widget.setLayout(v_layout)
							
				tool_box.addItem(topic_widget, header)
				
	def chat_new_topic_ui(self, window):
		# make widjet
		ui_path = G.MW.chat_add_topic_path
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(ui_path)
		#file.open(QtCore.QFile.ReadOnly)
		add_window = G.MW.chatAddTopic = loader.load(file, G.MW)
		file.close()
		
		# set modal window
		add_window.setWindowModality(QtCore.Qt.WindowModal)
		add_window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		
		# ****** add first line
		# H
		h_layout = QtGui.QHBoxLayout()
		line_frame = QtGui.QFrame(parent = add_window.new_topics_frame)
		# button
		button = QtGui.QPushButton('img', parent = line_frame)
		button.setFixedSize(100, 100)
		button.img_path = False
		h_layout.addWidget(button)
		# -- button connect
		button.clicked.connect(partial(self.chat_image_view_ui, button))
		button.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		addgrup_action = QtGui.QAction( 'Inser Image From Clipboard', add_window)
		addgrup_action.triggered.connect(partial(self.chat_add_img_to_line, button))
		button.addAction( addgrup_action )
		
		# text field
		text_field = QtGui.QTextEdit(parent = line_frame)
		#text_field = QtGui.QTextBrowser(parent = line_frame)
		text_field.setMaximumHeight(100)
		h_layout.addWidget(text_field)
		line_frame.setLayout(h_layout)
		# V
		v_layout = QtGui.QVBoxLayout()
		v_layout.addWidget(line_frame)
		add_window.new_topics_frame.setLayout(v_layout)
		
		# ****** append line data
		add_window.line_data = {}
		add_window.line_data['1'] = (button, text_field)
		
		# connect button
		add_window.cansel_button.clicked.connect(partial(G.MW.close_window, add_window))
		add_window.add_line_button.clicked.connect(partial(self.chat_add_line_to_message, add_window, v_layout))
		add_window.send_message_button.clicked.connect(partial(self.chat_new_topic_action, add_window, G.MW.chat_status))
		
		add_window.show()
		
		
	def chat_add_img_to_line(self, button):
		rand  = hex(random.randint(0, 1000000000)).replace('0x', '')
		img_path = os.path.join(G.MW.db_chat.tmp_folder, ('tmp_image_' + rand + '.png')).replace('\\','/')
		
		clipboard = QtGui.QApplication.clipboard()
		img = clipboard.image()
		if img:
			img.save(img_path)
		else:
			G.MW.message('Cannot Image!', 2)
			return(False, 'Cannot Image!')
			
		button.setIcon(QtGui.QIcon(img_path))
		button.setIconSize(QtCore.QSize(100, 100))
		button.setText('')
		button.img_path = img_path
		
		return(True, 'Ok!')
		
	def chat_image_view_ui(self, button):
		if not button.img_path:
			return
		# make widjet
		ui_path = G.MW.chat_img_viewer_path
		# widget
		loader = QtUiTools.QUiLoader()
		file = QtCore.QFile(ui_path)
		#file.open(QtCore.QFile.ReadOnly)
		img_window = G.MW.chatImgViewer = loader.load(file, G.MW)
		file.close()
		
		
		# SHOW IMAGE
		image = QtGui.QImage(button.img_path)
		img_window.setWindowTitle(button.img_path)
			
		img_window.image_label.setBackgroundRole(QtGui.QPalette.Base)
		img_window.image_label.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
		img_window.image_label.setScaledContents(True)
		
		img_window.image_label.setPixmap(QtGui.QPixmap.fromImage(image))
		
		# connect button
		img_window.cansel_button.clicked.connect(partial(G.MW.close_window, img_window))
		
		img_window.show()
    
				
	def chat_add_line_to_message(self, add_window, v_layout):
		# H
		h_layout = QtGui.QHBoxLayout()
		line_frame = QtGui.QFrame(parent = add_window.new_topics_frame)
		# button
		button = QtGui.QPushButton('img', parent = line_frame)
		button.setFixedSize(100, 100)
		button.img_path = False
		h_layout.addWidget(button)
		# -- button connect
		button.clicked.connect(partial(self.chat_image_view_ui, button))
		button.setContextMenuPolicy( QtCore.Qt.ActionsContextMenu )
		addgrup_action = QtGui.QAction( 'Inser Image From Clipboard', add_window)
		addgrup_action.triggered.connect(partial(self.chat_add_img_to_line, button))
		button.addAction( addgrup_action )
		
		# text field
		text_field = QtGui.QTextEdit(parent = line_frame)
		text_field.setMaximumHeight(100)
		h_layout.addWidget(text_field)
		line_frame.setLayout(h_layout)
		
		v_layout.addWidget(line_frame)
		
		# ****** append line data
		# -- get num
		numbers = []
		for key in add_window.line_data.keys():
			numbers.append(int(key))
		num = max(numbers) + 1
		add_window.line_data[str(num)] = (button, text_field)
		
	def chat_new_topic_action(self, add_window, status):
		task_data = G.MW.current_task
		nik_name = G.MW.current_user
		project = G.MW.current_project
		
		# get project
		result = G.MW.db_chat.get_project(project)
		if not result[0]:
			G.MW.message(result[1], 2)
			return
		
		# get color
		if status == 'manager' or status == 'manager_to_outsource':
			color = json.dumps(G.MW.db_chat.color_status['checking'])
		elif status == 'user' or status == 'user_outsource':
			color = json.dumps(G.MW.db_chat.color_status['work'])
		else:
			color = json.dumps(G.MW.db_chat.color_status['done'])
			
		message = {}
		line_data = add_window.line_data
		for key in line_data:
			# GET Img
			tmp_img_path = line_data[key][0].img_path
			
			if tmp_img_path and os.path.exists(tmp_img_path):
				icon_tmp_img_path = tmp_img_path.replace('.png', '_icon.png')
				
				# -- copy to img_path
				rand  = hex(random.randint(0, 1000000000)).replace('0x', '')
				img_path = os.path.normpath(os.path.join(G.MW.db_chat.chat_img_path, (task_data['task_name'].replace(':','_') + rand + '.png')))
				shutil.copyfile(tmp_img_path, img_path)
				
				# -- make icon
				icon_path = img_path.replace('.png', '_icon.png')
				cmd = G.MW.db_chat.convert_exe + ' \"' + tmp_img_path + '\" -resize 100 \"' + icon_tmp_img_path + '\"'
				
				os.system(cmd)
				shutil.copyfile(icon_tmp_img_path, icon_path)
				
				'''
				try:
					os.system(cmd)
				except:
					G.MW.message('in chat_new_topic_action - problems with conversion icon.png', 2)
					#return(False, 'in chat_new_topic_action - problems with conversion icon.png')
					return
				'''
			else:
				img_path = False
				icon_path = False
				
			# GET Text
			text = line_data[key][1].toPlainText()
			
			# append message
			message[key] = (img_path, icon_path, text)
		
		topic = json.dumps(message, sort_keys=True, indent=4)
		
		# save message 
		chat_keys = {
		'author':nik_name,
		'color':color,
		'topic':topic,
		'status':status
		}
		result = G.MW.db_chat.record_messages(project, task_data['task_name'], chat_keys)
		if not result[0]:
			G.MW.message(result[1], 2)
			return
		else:
			print(result[1])
			G.MW.close_window(add_window)
			self.chat_load_topics(G.MW.chatMain)
		
		# edit read_status
		if G.MW.chat_status == 'user':
			result = G.MW.db_chat.task_edit_rid_status_unread(project, task_data)
			if not result[0]:
				G.MW.message(result[1], 2)
				return
