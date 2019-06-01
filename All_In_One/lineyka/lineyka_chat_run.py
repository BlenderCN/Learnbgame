#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PySide import QtCore, QtGui, QtUiTools, QtSql
import os
import json

import ui
import edit_db as db
import lineyka_chat

class MainWindow(QtGui.QMainWindow):
	def __init__(self, parent = None):
		path = os.path.dirname(ui.__file__)
		# chat
		self.message_window_path = os.path.join(path, "message_window.ui")
		self.chat_main_path = os.path.join(path, "chat_dialog.ui")
		self.chat_add_topic_path = os.path.join(path, "chat_add_topic.ui")
		self.chat_img_viewer_path = os.path.join(path, "chat_img_viewer.ui")
		
		# moduls
		self.db_studio = db.studio()
		self.db_artist = db.artist()
		self.db_task = db.task()
		self.db_log = db.log()
		self.db_chat = db.chat()
		
		# get data
		home_dir = os.path.expanduser('~')
		json_path = os.path.normpath(os.path.join(home_dir, '.blend_chat.json'))
		
		with open(json_path, 'r') as read:
			data_dict = json.load(read)
			
		self.chat_status = 'user'
		self.current_task = data_dict['current_task']
		self.current_user = data_dict['current_user']
		self.current_project = data_dict['current_project']
		
		print(data_dict)
		
		# create widget
		QtGui.QMainWindow.__init__(self, parent)
		self.setWindowTitle('Chat Message Window')
		
		self.textBox = QtGui.QTextEdit(parent = self)
		self.textBox.setReadOnly(True)
		self.setCentralWidget(self.textBox)
		
		'''
		# test text
		text = self.textBox.toPlainText()
		text = text + '\n' + '>>> ' + 'text.text'
		self.textBox.setPlainText(text)
		'''
		self.run_chat_ui()
		
	def run_chat_ui(self):
		chat_window = lineyka_chat.lineyka_chat(self)
		
		# test text
		text = self.textBox.toPlainText()
		text = text + '\n' + '>>> ' + str(chat_window)
		self.textBox.setPlainText(text)
		
	#*********************** UTILITS *******************************************
	def load_project_list(self): 
		enum_list = ['--select project--']
		project_list = self.db_studio.list_projects.keys()
		for key in project_list:
			if self.db_studio.list_projects[key]['status'] == 'active':
				enum_list.append(key)
		
		self.myWidget.project_box.addItems(enum_list)
	
	def load_nik_name(self):
		nik_name = 'Not User'
		result = self.db_artist.get_user()
		if result[0]:
			nik_name = result[1][0]
		
		self.myWidget.nik_name.setText(nik_name)
		G.current_user = nik_name
	
	def close_window(self, window):
		window.close()
	
	def clear_table(self, table = False):
		if not table:
			table = self.myWidget.task_list_table
		
		# -- clear table
		num_row = table.rowCount()
		num_column = table.columnCount()
		
		# old
		'''
		for i in range(0, num_row):
			for j in range(0, num_column):
				item = table.item(i, j)
				table.takeItem(i, j)

				table.removeCellWidget(i, j)
		'''
		
		# new
		table.clear()
		table.setColumnCount(0)
		table.setRowCount(0)
				
	
	def message(self, m, i):
		mBox = QtGui.QMessageBox()
		mBox.setText(m)
		#mBox.setStandardButtons( QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok )
		ok_button = mBox.addButton(QtGui.QMessageBox.Ok)
		cancel_button = mBox.addButton(QtGui.QMessageBox.Cancel)
    
		if i==1:
			mBox.setIcon(QtGui.QMessageBox.Information)
			mBox.setWindowTitle('information')
		elif i == 2:
			mBox.setIcon(QtGui.QMessageBox.Warning)
			mBox.setWindowTitle('epte!')
		elif i == 3:
			mBox.setIcon(QtGui.QMessageBox.Critical)
			mBox.setWindowTitle('fuck!')
		elif i == 0:
			mBox.setIcon(QtGui.QMessageBox.Question)
			mBox.setWindowTitle('tel me!')
    
		com = mBox.exec_()
		
		text = self.textBox.toPlainText()
		text = text + '\n' + '>>> ' + m
		self.textBox.setPlainText(text)
    
		if mBox.clickedButton() == ok_button:
			return(True)
		elif mBox.clickedButton() == cancel_button:
			return(False)
		
	
app = QtGui.QApplication(sys.argv)
mw = MainWindow()
mw.show()
app.exec_()