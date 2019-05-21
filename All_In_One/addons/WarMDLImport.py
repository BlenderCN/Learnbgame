# Copyright (c) 2011 Thomas Glamsch
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

import bpy
import string
import pdb
import time

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

dbg = False

bl_info = {
	"name": "Import WarCraft MDL (.mdl)",
	"description": "This addon allows you to import WarCraft MDL model files (.mdl).",
	"author": "Thomas 'CruzR' Glamsch",
	"version": (0, 2, 1),
	"blender": (2, 6, 3),
	#"api": ???,
	"location": "File > Import > WarCraft MDL (.mdl)",
	"warning": "Currently only the vertices and faces are imported, work in progress.",
	"wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/Import-Export/WarCraft_MDL",
	"tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=29552",
	"category": "Learnbgame"
}

# This is our abstract state machine
class StateMachine:

# @param handlers: Dictionary containing name => function pairs
# @param startState: The first state to call when starting
# @param endStates: State machine will end execution on these
	def __init__(self, parent, handlers={}, startState=None, endStates=[]):
		self.parent = parent
		self.handlers = handlers
		self.startState = startState
		self.endStates = endStates

# @param name: The name of the state to add
# @param handler: A function to handle the state
# @param endState: Bool whether this should be added to endStates
# @param startState: Bool whether this should be set as startState
	def add(self, name, handler, endState=False, startState=False):
		name = name.upper()
		if handler:
			self.handlers[name] = handler(self.parent)
		if endState:
			self.endStates.append(name)
			print(self.endStates)
		if startState:
			self.startState = name

# @param name: Name of the state which shall be set as startState
	def set_start(self, name):
		name = name.upper()
		if name in self.handlers:
			self.startState = name
		else:
			raise Exception("Error: set_start(): Unknown state: {}".format(name))

# @param cargo: Some kind of information to carry through the states
	def run(self, cargo={}):
		handler = self.handlers.get(self.startState)
		if not handler:
			raise Exception("InitError: Set startState before calling StateMachine.run()")
		if not self.endStates:
			raise Exception("InitError: There must be at least one endstate")
		
		while True:
			newState, cargo = handler.run(cargo)
			if newState.upper() in self.endStates:
				break
			else:
				handler = self.handlers[newState.upper()]

# All Handlers should be derived from BaseHandler.
# They all have to override the .run() function
# They should always call newState, cargo = BaseHandler.run(cargo)
# before doing anything else.
class BaseHandler:
	def __init__(self, parent):
		self.parent = parent
	
	def run(self, cargo):
		cargo['prev_handler'] = self.__class__.__name__
		print(cargo['prev_handler'])
		return 'SEARCH', cargo

# Our geosets are managed by this class
class GeosetManager:
	def __init__(self):
		self.vertices = [[]]
		self.normals = [[]]
		self.tvertices = [[]]
		self.faces = [[]]
		self.cnt = 0
		self.add_new = False
		
	def new_geoset(self):
		self.vertices.append([])
		self.normals.append([])
		self.tvertices.append([])
		self.faces.append([])
		self.cnt += 1
		self.add_new = False
	
	# @param li: List of data to be added to our geoset.
	# @param cont: Type of the data to be added. One of 'vertices', 'normals',
	# 'tvertices' and 'faces'.
	def append(self, li, cont):
		if cont == 'vertices':
			self.vertices[self.cnt].append(li)
		elif cont == 'normals':
			self.normals[self.cnt].append(li)
		elif cont == 'tvertices':
			self.tvertices[self.cnt].append(li)
		elif cont == 'faces':
			self.faces[self.cnt].append(li)
			self.add_new = True
	
	# @param li: List of data to be added to our geoset.
	# @param cont: Type of the data to be added. One of 'vertices', 'normals',
	# 'tvertices' and 'faces'.
	def extend(self, li, cont):
		if cont == 'vertices':
			self.vertices[self.cnt].extend(li)
		elif cont == 'normals':
			self.normals[self.cnt].extend(li)
		elif cont == 'tvertices':
			self.tvertices[self.cnt].extend(li)
		elif cont == 'faces':
			self.faces[self.cnt].extend(li)
			self.add_new = True

# This is our main handler.
class SEARCH(BaseHandler):
	def run(self, cargo):
		newState, cargo = BaseHandler.run(self, cargo)
		
		while True:
			cargo['last'] = current = self.parent.infile.readline()
			# Stop when end of the file is reached.
			if current == '' :
				newState = 'EOF'
				break
			# Skip comments.
			elif current.strip().startswith('//'):
				continue
			# If the line starts with a keyword from DataImporter.globalkeys,
			# start the appropiate handler.
			elif current.strip().split()[0] in self.parent.globalkeys:
				newState = current.strip().split()[0].upper()
				break
		
		return newState, cargo

# This handler just makes sure that our file has the correct MDL version.
class VERSION(BaseHandler):
	def run(self, cargo):
		cargo = BaseHandler.run(self, cargo)[1]
		if int(self.parent.infile.readline().strip().strip(',').split()[1]) != 800:
			raise Exception("This MDL Version is not supported!")
		return 'SEARCH', cargo

# This handler deals with the content inside a Geoset block.
class GEOSET(BaseHandler):
	def run(self, cargo):
		if dbg: pdb.set_trace()
		if cargo['prev_handler'] == 'SEARCH':
			if self.parent.mgr.add_new:
				self.parent.mgr.new_geoset()
			cargo['p'] = 1
		
		newState, cargo = BaseHandler.run(self, cargo)
		
		while cargo['p'] > 0:
			cargo['last'] = current = self.parent.infile.readline()
			current = current.strip()
			# We count the braces to find out when a Geoset block ends.
			if '{' in current: cargo['p'] += 1
			if '}' in current: cargo['p'] -= 1
			# If a line starts with an keyword from DataImporter.geosetkeys,
			# start the appropiate handler.
			if current.split()[0] in self.parent.geosetkeys:
				newState = current.split()[0].upper()
				break
	
		return newState, cargo

# This handler imports the vertices inside a Geoset block.
class VERTICES(BaseHandler):
	def run(self, cargo):
		cargo = BaseHandler.run(self, cargo)[1]
		# Get the number of vertices inside this Vertices block.
		for i in range(int(cargo['last'].strip().split()[1])):
			current = self.parent.infile.readline().strip().strip('{},;')
			# Divide with 20 to scale the model down.
			li = [float(n)/20 for n in current.split(', ')]
			self.parent.mgr.extend(li, 'vertices')
		return 'GEOSET', cargo

# This handler imports the vertex normals.
class NORMALS(BaseHandler):
	def run(self, cargo):
		cargo = BaseHandler.run(self, cargo)[1]
		# Get the number of normals inside this Normals block.
		for i in range(int(cargo['last'].strip().split()[1])):
			current = self.parent.infile.readline().strip().strip('{},;')
			li = [float(n) for n in current.split(', ')]
			self.parent.mgr.extend(li, 'normals')
		return 'GEOSET', cargo

# This handler imports the texture vertices (aka the UV layout).
class TVERTICES(BaseHandler):
	def run(self, cargo):
		cargo = BaseHandler.run(self, cargo)[1]
		# Get the number of vertices inside this Normals block.
		for i in range(int(cargo['last'].strip().split()[1])):
			current = self.parent.infile.readline().strip().strip('{},:')
			li = tuple(float(n) for n in current.split(', '))
			self.parent.mgr.append(li, 'tvertices')
		return 'GEOSET', cargo

# This handler imports the faces inside a Geoset block.
class FACES(BaseHandler):
	def run(self, cargo):
		cargo = BaseHandler.run(self, cargo)[1]
		# Faces is a strange construction. grps is the number of data blocks,
		# cnt the total amount of vertex indices.
		grps, cnt = [int(n) for n in cargo['last'].strip().split()[1:3]]
		li = []
		while len(li) < cnt:
			cargo['last'] = current = self.parent.infile.readline()
			if current.strip().startswith('Triangles'):
				for i in range(grps):
					li += [int(n) for n in self.parent.infile.readline().strip().strip('{},;').split(', ')]
		if dbg: print(len(li))
		for i in range(cnt):
			self.parent.mgr.append(li[i], 'faces')
			if i % 3 == 2: self.parent.mgr.append(li[i], 'faces')
		return 'GEOSET', cargo

# This handles the Model block
class MODEL(BaseHandler):
	def run(self, cargo):
		next, cargo = BaseHandler.run(self, cargo)
		# Store the model's name
		self.parent.model_info['name'] = cargo['last'].split()[1].strip('\"')
		# Count curled braces to stop loop when the block ends
		cargo['p'] = 1
		while cargo['p'] > 0:
			current = self.parent.infile.readline()
			if '{' in current: cargo['p'] += 1
			if '}' in current: cargo['p'] -= 1
			key = current.strip().split()[0]
			# Only two keys are interesting: 'BoundsRadius' & 'BlendTime'
			if key == 'BoundsRadius':
				self.parent.model_info[key] = float(current.strip().split()[1].strip(','))
			elif key == 'BlendTime':
				self.parent.model_info[key] = int(current.strip().split()[1].strip(','))
		return next, cargo

# This class initiates and starts the state machine and uses the gathered data
# to construct the model in Blender.
class DataImporter:
	infile = None
	globalkeys = ['Version', 'Model', 'Geoset']
	geosetkeys = ['Vertices', 'Normals', 'TVertices', 'Faces']
	mgr = GeosetManager()
	model_info = {}
	
	def run(self, filepath, context):
		start_time = time.time()
		print("Opening {}...".format(filepath))
		self.infile = open(filepath, 'r')
		m = StateMachine(parent=self)
		m.add('SEARCH', SEARCH, startState=True)
		m.add('VERSION', VERSION)
		m.add('MODEL', MODEL)
		m.add('GEOSET', GEOSET)
		m.add('VERTICES', VERTICES)
		m.add('NORMALS', NORMALS)
		m.add('TVERTICES', TVERTICES)
		m.add('FACES', FACES)
		m.add('EOF', None, endState=True)
		m.run()
		
		if dbg: pdb.set_trace()
		# Construct an own object for each geoset.
		for i in range(self.mgr.cnt + 1):
			# Create an object and link it to the scene.
			mesh = bpy.data.meshes.new("{name}{i}Mesh".format(name=self.model_info['name'], i=i))
			obj = bpy.data.objects.new("{name}{i}".format(name=self.model_info['name'], i=i), mesh)
			obj.location = (0.0, 0.0, 0.0)
			bpy.context.scene.objects.link(obj)
			# Construct the mesh from the gathered vertex and face data.
			mesh.vertices.add(len(self.mgr.vertices[i]) // 3)
			mesh.vertices.foreach_set('co', self.mgr.vertices[i])
			mesh.tessfaces.add(len(self.mgr.faces[i]) // 4)
			mesh.tessfaces.foreach_set('vertices', self.mgr.faces[i])
			# Create the UV layout.
			uvtex = mesh.tessface_uv_textures.new(name="uvtex{}".format(i))
			for n in range(len(self.mgr.faces[i]) // 4):
				face = self.mgr.faces[i][n * 4:n * 4 + 3]
				texface = uvtex.data[n]
				texface.uv1 = (self.mgr.tvertices[i][face[0]][0], 1 - self.mgr.tvertices[i][face[0]][1])
				texface.uv2 = (self.mgr.tvertices[i][face[1]][0], 1 - self.mgr.tvertices[i][face[1]][1])
				texface.uv3 = (self.mgr.tvertices[i][face[2]][0], 1 - self.mgr.tvertices[i][face[2]][1])
			# Set the normals
			mesh.vertices.foreach_set('normal', self.mgr.normals[i])
			mesh.update()
			if dbg: pdb.set_trace()
			# Delete the mesh and obj pointer to make sure we don't override
			# the just created object.
			del mesh
			del obj
		
		print("Script finished after {} seconds".format(time.time() - start_time))
		return {'FINISHED'}

# This is the import operator.
class ImportWarMDL(bpy.types.Operator, ImportHelper):
	'''Import from WarCraft MDL model format (.mdl)'''
	bl_idname = "import_mesh.warmdl"
	bl_label = "WarCraft MDL (.mdl)"
	
	filename_ext = ".mdl"
	
	filter_glob = StringProperty(
			default="*.mdl",
			options={'HIDDEN'}
			)
	
	@classmethod
	def poll(cls, context):
		return True
	
	def execute(self, context):
		di = DataImporter()
		return di.run(self.filepath, context)

def menu_func_export(self, context):
	self.layout.operator(ImportWarMDL.bl_idname, text="WarCraft MDL (.mdl)")

def register():
	bpy.utils.register_class(ImportWarMDL)
	bpy.types.INFO_MT_file_import.append(menu_func_export)

def unregister():
	bpy.utils.unregister_class(ImportWarMDL)
	bpy.types.INFO_MT_file_import.remove(menu_func_export)

if __name__ == "__main__":
	register()

	# test call
	bpy.ops.import_mesh.warmdl('INVOKE_DEFAULT')

