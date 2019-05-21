# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import os
import struct

import bpy
import csv
import mathutils
from mathutils import Vector, Euler
from math import radians
from bpy import *
from bpy_extras.image_utils import load_image
from bpy_extras.io_utils import unpack_list, unpack_face_list
from bpy_extras.mesh_utils import ngon_tessellate

'''
This file is a reboot of the AC3D import script that is used to import .ac format file into blender.

The original work carried out by Willian P Gerano was used to learn Python and Blender, but inherent issues and a desire to do better has prompted a complete re-write

Reference to the .ac format is found here:
http://www.inivis.com/ac3d/man/ac3dfileformat.html

Some noted points that are important for consideration:
 - AC3D appears to use Left Handed axes, but with Y oriented "Up". Blender uses Right Handed axes, the import does provide a rotation matrix applied to the world object that corrects this, so "Up" in the AC file appears as "Up" in blender - it's configurable, so you can change how it rotates...
 - AC3D supports only one texture per surface. This is a UV texture map, so it's imported as such in blender
 - Blender's Materials can have multiple textures per material - so a material + texure in AC3D requires a distinct and unique material in blender (more of an issue for the export routine)
 - AC3D supports individual face twosidedness, blender's twosidedness is per-object
TODO: Add setting so that .AC file is brought in relative to the 3D cursor

'''

DEBUG = True

def TRACE(message):
	if DEBUG:
		print(message)

class AcMat:
	'''
	Container class that defines the material properties of the .ac MATERIAL
	'''
	def __init__(self, name, rgb, amb, emis, spec, shi, trans, import_config):
		if name == "":
			name = "Default"
		self.name = name			# string
		self.rgb = rgb				# [R,G,B]
		self.amb = amb				# [R,G,B]
		self.emis = emis			# [R,G,B]
		self.spec = spec			# [R,G,B]
		self.shi = shi				# integer
		self.trans = trans			# float

		self.bmat_keys = {}			# dictionary list of blender materials
		self.bmat_keys.setdefault(None)
		self.bl_material = None		# untextured material
		self.import_config = import_config

	def make_blender_mat(self, bl_mat):
		bl_mat.specular_shader = 'PHONG'
		bl_mat.diffuse_color = self.rgb
		bl_mat.ambient = (self.amb[0] + self.amb[1] + self.amb[2]) / 3.0
		if self.import_config.use_amb_as_mircol:
				bl_mat.mirror_color = self.amb
		bl_mat.emit = (self.emis[0] + self.emis[1] + self.emis[2]) / 3.0
		if self.import_config.use_emis_as_mircol:
				bl_mat.mirror_color = self.emis
		bl_mat.specular_color = self.spec
		bl_mat.specular_intensity = 1.0

		acMin = 0.0
		acMax = 128.0
		blMin = 1.0
		blMax = 511.0
		acRange = (acMax - acMin)  
		blRange = (blMax - blMin)  
		bl_mat.specular_hardness = int(round((((float(self.shi) - acMin) * blRange) / acRange) + blMin, 0))

		bl_mat.alpha = 1.0 - self.trans
		if bl_mat.alpha < 1.0:
			bl_mat.use_transparency = self.import_config.use_transparency
			bl_mat.transparency_method = self.import_config.transparency_method
		
		return bl_mat

	'''
	looks for a matching blender material (optionally with a texture), adds it if it doesn't exist
	'''
	def get_blender_material(self, texrep, tex_name=''):
		bl_mat = None
		tex_slot = None
		if tex_name == '':
			bl_mat = self.bl_material
			if bl_mat == None:
				bl_mat = bpy.data.materials.new(self.name)
				bl_mat = self.make_blender_mat(bl_mat)

				self.bl_material = bl_mat
		else:
			if (tex_name+str(texrep[0])+'-'+str(texrep[1])) in self.bmat_keys:
				bl_mat = self.bmat_keys[tex_name+str(texrep[0])+'-'+str(texrep[1])]
			else:
				bl_mat = bpy.data.materials.new(self.name)
				bl_mat = self.make_blender_mat(bl_mat)
				bl_mat.use_face_texture = True
				bl_mat.use_face_texture_alpha = True
				
				tex_slot = bl_mat.texture_slots.add()
				tex_slot.texture = self.get_blender_texture(tex_name, texrep)
				tex_slot.texture_coords = 'UV'
				tex_slot.alpha_factor = 1.0
				tex_slot.use_map_alpha = True
				tex_slot.use = True
				tex_slot.uv_layer = 'UVMap'
				tex_slot.texture.repeat_x = texrep[0]
				tex_slot.texture.repeat_y = texrep[1]
				self.bmat_keys[tex_name+str(texrep[0])+'-'+str(texrep[1])] = bl_mat
		return bl_mat

	'''
	looks for the image in blender, adds it if it doesn't exist, returns the image to the callee
	'''
	def get_blender_image(self, tex_name):
		bl_image = None
		if tex_name in bpy.data.images:
			bl_image = bpy.data.images[tex_name]
		else:
			found = False
			base_name = bpy.path.basename(tex_name)
			for path in [ tex_name,
										os.path.join(self.import_config.importdir, tex_name),
										os.path.join(self.import_config.importdir, base_name) ]:
				if os.path.exists(path):
					found = True

					try:
						bl_image = bpy.data.images.load(path)
					except:
						TRACE("Failed to load texture: {0}".format(tex_name))
			
			if not found:
				TRACE("Failed to locate texture: {0}".format(tex_name))

		return bl_image

	'''
	looks for the blender texture, adds it if it doesn't exist
	'''
	def get_blender_texture(self, tex_name, texrep):
		bl_tex = None
		if tex_name in bpy.data.textures and bpy.data.textures[tex_name].repeat_x == texrep[0] and bpy.data.textures[tex_name].repeat_y == texrep[1]:
			bl_tex = bpy.data.textures[tex_name]
		else:
			bl_tex = bpy.data.textures.new(tex_name, 'IMAGE')
			bl_tex.image = self.get_blender_image(tex_name)
			bl_tex.use_preview_alpha = True
			
		return bl_tex

class AcObj:
	'''
	Container class for a .ac OBJECT
	'''
	def __init__(self, ob_type, ac_file, import_config, parent = None):
		self.type = ob_type			# Type of object
		self.ac_parent = parent		# reference to the parent object (if the object is World, then this should be None)
		self.name = ''				# name of the object
		self.data = ''				# custom data
		self.tex_name = ''			# texture name (filename of texture)
		self.texrep = [1,1]			# texture repeat
		self.texoff = [0,0]			# texture offset
		self.location = [0,0,0]			# translation location of the center relative to the parent object
		self.rotation = mathutils.Matrix(([1,0,0],[0,1,0],[0,0,1]))	# 3x3 rotational matrix for vertices
		self.url = ''				# url of the object (??!)
		self.crease = 61			# crease angle for smoothing
		self.vert_list = []				# list of Vector(X,Y,Z) objects
		self.surf_list = []			# list of attached surfaces
		self.face_list = []			# flattened surface list
		self.surf_face_list = []    # list of surfs that is faces, no edges
		self.edge_list = []			# spare edge list (handles poly lines etc)
		self.face_mat_list = []		# flattened surface material index list
		self.children = []			
		self.bl_mat_dict = {}		# Dictionary of ac_material index/texture pair to blender mesh material index

		self.bl_obj = None			# Blender object
		self.import_config = import_config

		self.tokens =	{
						'numvert':	self.read_vertices,
						'numsurf':	self.read_surfaces,
						'name':		self.read_name,
						'data':		self.read_data,
						'kids':		self.read_children,
						'loc':		self.read_location,
						'rot':		self.read_rotation,
						'texture':	self.read_texture,
						'texrep':	self.read_texrep,
						'texoff':	self.read_texoff,
						'subdiv':	self.read_subdiv,
						'crease':	self.read_crease
						}

		self.read_ac_object(ac_file)

	'''
	Read the object lines and dump them into this object, making hierarchial attachments to parents
	'''
	def read_ac_object(self, ac_file):
		bDone = False
		while not bDone:
			line = ac_file.readline()
			if line == '':
				break
			toks = line.strip().split()
			if len(toks)>0:
				if toks[0] in self.tokens.keys():
					bDone = self.tokens[toks[0]](ac_file,toks)
				else:
					bDone = True

	def read_vertices(self, ac_file, toks):
		vertex_count = int(toks[1])
		for n in range(vertex_count):
			line = ac_file.readline()
			line = line.strip().split()
			self.vert_list.append(self.import_config.global_matrix * Vector([float(x) for x in line]))

	def read_surfaces(self, ac_file, toks):
		surf_count = int(toks[1])

		for n in range(surf_count):
			line = ac_file.readline()
			if line=='':
				break

			line = line.strip().split()
			if line[0] == 'SURF':
				surf = AcSurf(line[1], ac_file, self.import_config)
				if( surf.flags.type != 0 or len(surf.refs) > 2):
					self.surf_list.append(surf)
				else:
					TRACE("Ignoring surface (vertex-count: {0})".format(len(surf.refs)))					

	def read_name(self, ac_file, toks):
		self.name=toks[1].strip('"')
		return False

	def read_data(self, ac_file, toks):
		line = ac_file.readline()
		self.data=line[:int(toks[1])]
		return False

	def read_location(self, ac_file, toks):
		self.location=(self.import_config.global_matrix * Vector([float(x) for x in toks[1:4]]))
		return False

	def read_rotation(self, ac_file, toks):
		self.rotation = mathutils.Matrix(([float(x) for x in toks[1:4]], [float(x) for x in toks[4:7]], [float(x) for x in toks[7:10]]))
#		TODO check
#		rotation = mathutils.Matrix(( [float(x) for x in toks[1:4]],
#		                              [float(x) for x in toks[4:7]],
#		                              [float(x) for x in toks[7:10]] )).to_quaternion()
#		rotation.axis = self.import_config.global_matrix * rotation.axis
#		self.rotation = rotation.to_matrix()
		return False

	def read_texture(self, ac_file, toks):
		self.tex_name=toks[1].strip('"')
		return False

	def read_texrep(self, ac_file, toks):
		self.texrep[0]=int(float(toks[1]))
		self.texrep[1]=int(float(toks[2]))
		return False

	def read_texoff(self, ac_file, toks):
		self.texoff=toks[1:2]
		return False

	def read_subdiv(self, ac_file, toks):
		self.subdiv=int(toks[1])
		return False

	def read_crease(self, ac_file, toks):
		self.crease=float(toks[1])
		return False

	def read_children(self, ac_file, toks):
		num_kids = int(toks[1])
		for n in range(num_kids):
			line = ac_file.readline()
			if line == '':
				break			
			line = line.strip().split()
			self.children.append(AcObj(line[1].strip('"'), ac_file, self.import_config, self))
		# This is assumed to be the last thing in the list of things to read
		# returning True indicates to cease parsing this object
		return True
	

	'''
	This function does the work of creating an object in blender and configuring it correctly
	'''
	def create_blender_object(self, ac_matlist, str_pre, bLevelLinked):

		if self.type == 'world':
			self.name = self.import_config.ac_name
			self.rotation = self.import_config.global_matrix
		me = None
		if self.type == 'group':
			# Create an empty object
			self.bl_obj = bpy.data.objects.new(self.name, None)

		if self.type == 'poly':
			meshname = self.name+".mesh"
			if len(self.data)>0:
				meshname = self.data
			me = bpy.data.meshes.new(meshname)
			self.bl_obj = bpy.data.objects.new(self.name, me)

		# setup parent object
		if self.ac_parent:
			self.bl_obj.parent = self.ac_parent.bl_obj

		# make sure we have something to work with
		if self.vert_list and me:

			me.use_auto_smooth = self.import_config.use_auto_smooth
			me.auto_smooth_angle = radians(self.crease)
			two_sided_lighting = False
			has_uv = False
			for surf in self.surf_list:
				surf_edges = surf.get_edges()
				surf_face = surf.get_faces()

				for line in surf_edges:
					self.edge_list.append(line)

				if surf.flags.type == 0:
					# test for invalid face (ie, >4 vertices)
					if len(surf.refs) < 3:
						# not bringing in faces (assumed that there are none in a poly-line)
						TRACE("Ignoring surface (vertex-count: {0})".format(len(surf.refs)))
					else:
						# If one surface is twosided, they all will be...
						two_sided_lighting |= surf.flags.two_sided

						has_uv |= len(surf.uv_refs) > 0

						self.face_list.append(surf_face)
						self.surf_face_list.append(surf)
						
						# Material index is 1 based, the list we built is 0 based
						ac_material = ac_matlist[surf.mat_index]
						bl_material = ac_material.get_blender_material(self.texrep, self.tex_name)

						if bl_material == None:
							TRACE("Error getting material {0} '{1}'".format(surf.mat_index, self.tex_name))

						fm_index = 0
						if not bl_material.name in me.materials:
							me.materials.append(bl_material)
							fm_index = len(me.materials)-1
						else:
							for mat in me.materials:
								if mat == bl_material:
									continue
								fm_index += 1
							if fm_index > len(me.materials):
								TRACE("Failed to find material index")
								fm_index = 0
						self.face_mat_list.append(fm_index)
				else:
					# treating as a polyline (nothing more to do)
					pass

			me.from_pydata(self.vert_list, self.edge_list, self.face_list);

			y=0	
			for no, poly in enumerate(me.polygons):
				if self.surf_face_list[no].flags.shaded == True:
					poly.use_smooth = True
				else:
					poly.use_smooth = False
				y= y+1			

			
			if has_uv:
				uvtex = me.uv_textures.new()
				if uvtex:
					uvtexdata = me.uv_layers.active.data[:]
					
					uv_pointer = 0
					for i, face in enumerate(self.face_list):
						surf = self.surf_face_list[i]
						
						if len(surf.uv_refs) >= 3:

							for vert_index in range(len(surf.uv_refs)):
								uvtexdata[uv_pointer+vert_index].uv = surf.uv_refs[vert_index]
							if len(self.tex_name):
								# we do the check here to allow for import of UV without texture
								surf_material = me.materials[self.face_mat_list[i]]
								uvtex.data[i].image = surf_material.texture_slots[0].texture.image
							uv_pointer += len(surf.uv_refs)
			
			me.show_double_sided = two_sided_lighting
			self.bl_obj.show_transparent = self.import_config.display_transparency

		if self.bl_obj:
			self.bl_obj.rotation_euler = self.rotation.to_euler()

			self.bl_obj.location = self.location
			
			self.import_config.context.scene.objects.link(self.bl_obj)
# There's a bug somewhere - this ought to work....
			self.import_config.context.scene.objects.active = self.bl_obj
#			bpy.ops.object.origin_set('ORIGIN_GEOMETRY', 'MEDIAN')
			

		TRACE("{0}+-{1} ({2})".format(str_pre, self.name, self.data))

		# Add any children
		str_pre_new = ""
		bUseLink = True
		for obj in self.children:
			if bLevelLinked:
				str_pre_new = str_pre + "| "
			else:
				str_pre_new = str_pre + "  "

			if self.children.index(obj) == len(self.children)-1:
				bUseLink = False

			obj.create_blender_object(ac_matlist, str_pre_new, bUseLink)


		if me:
#			me.calc_normals()
			me.validate()
			me.update(calc_edges=True)


class AcSurf:
	class AcSurfFlags:
		def __init__(self, flags):
			self.type = 0		# Surface Type: 0=Polygon, 1=closedLine, 2=Line
			self.shaded = False
			self.two_sided = False
			i = int(flags,16)

			self.type = i & 0xF
			i = i >> 4
			if i&1:
				self.shaded = True
			if i&2:
				self.two_sided = True

	'''
	Container class for surface definition within a parent object
	'''
	def __init__(self, flags, ac_file, import_config):
		self.flags = self.AcSurfFlags(flags)			# surface flags
		self.mat_index = 0				# default material
		self.refs = []				# list of indexes into the parent objects defined vertexes with defined UV coordinates 
		self.uv_refs = []
		self.tokens =	{
						'mat':	self.read_surf_material,
						'refs':	self.read_surf_refs,
						}

		self.import_config = import_config
		self.read_ac_surfaces(ac_file)

	def read_ac_surfaces(self, ac_file):
		surf_done=False
		while not surf_done:
			line = ac_file.readline()
			if line=='':
				break
			toks = line.split()
			if len(toks)>0:
				if toks[0] in self.tokens.keys():
					surf_done = self.tokens[toks[0]](ac_file,toks)
				else:
					surf_done = True
			
	def read_surf_material(self, ac_file, tokens):
		self.mat_index = int(tokens[1])
		return False
	
	def read_surf_refs(self, ac_file, tokens):
		num_refs = int(tokens[1])
		for n in range(num_refs):
			line = ac_file.readline()
			line = line.strip().split()
		
			self.refs.append(int(line[0]))
			self.uv_refs.append([float(x) for x in line[1:3]])
		return True

	def get_faces(self):
		# convert refs and surface type to faces
		surf_faces = []
		# make sure it's a face type polygon and that there's the right number of vertices
		if self.flags.type == 0 and len(self.refs) > 2:
			surf_faces = self.refs
		return surf_faces

	def get_edges(self):
		# convert refs and surface type to edges
		surf_edges = []
		if self.flags.type != 0:
			# poly-line
			mainline = []
			mainline.extend(self.refs)
			surf_edges.append(mainline)

			if self.flags.type == 1:
				# closed poly-line
				surf_edges.append([self.refs[len(self.refs)-1], self.refs[0]])
		return surf_edges

class ImportConf:
	def __init__(
			self,
			operator,
			context,
			filepath,
			global_matrix,
			use_transparency,
			transparency_method,
			use_auto_smooth,
			use_emis_as_mircol,
			use_amb_as_mircol,
			display_transparency,
			display_textured_solid,
			):
		# Stuff that needs to be available to the working classes (ha!)
		self.operator = operator
		self.context = context
		self.global_matrix = global_matrix
		self.use_transparency = use_transparency
		self.transparency_method = transparency_method
		self.use_auto_smooth = use_auto_smooth
		self.use_emis_as_mircol = use_emis_as_mircol
		self.use_amb_as_mircol = use_amb_as_mircol
		self.display_transparency = display_transparency
		self.display_textured_solid = display_textured_solid

		# used to determine relative file paths
		self.importdir = os.path.dirname(filepath)
		self.ac_name = os.path.split(filepath)[1]
		TRACE("Importing {0}".format(self.ac_name))
	
class ImportAC3D:
	def __init__(
			self,
			operator,
			context,
			filepath="",
			use_image_search=False,
			global_matrix=None,
			use_transparency=True,
			transparency_method='Z_TRANSPARENCY',
			use_auto_smooth=True,
			use_emis_as_mircol=True,
			use_amb_as_mircol=False,
			display_transparency=True,
			display_textured_solid=False,
			):

		self.import_config = ImportConf(
										operator,
										context,
										filepath,
										global_matrix,
										use_transparency,
										transparency_method,
										use_auto_smooth,
										use_emis_as_mircol,
										use_amb_as_mircol,
										display_transparency,
										display_textured_solid,
										)


		self.tokens = 	{
						'MATERIAL':		self.read_material,
						'OBJECT':		self.read_object,
						}
		self.oblist = []
		self.matlist = []

		operator.report({'INFO'}, "Attempting import: {file}".format(file=filepath))

		# Check to make sure we're working with a valid AC3D file
		ac_file = open(filepath, 'r')
		self.header = ac_file.readline().strip()
		if len(self.header) != 5:
			operator.report({'ERROR'},"Invalid file header length: {0}".format(self.header))
			ac_file.close()
			return None

		#pull out the AC3D file header
		AC3D_header = self.header[:4]
		AC3D_ver = self.header[4:5]
		if AC3D_header != 'AC3D':
			operator.report({'ERROR'},"Invalid file header: {0}".format(self.header))
			ac_file.close()
			return None

		self.read_ac_file(ac_file)

		ac_file.close()

		self.create_blender_data()

		# Display as either textured solid (transparency only works in one direction) or as textureless solids (transparency works)
		for bl_screen in bpy.data.screens:
			for bl_area in bl_screen.areas:
				for bl_space in bl_area.spaces:
					if bl_space.type == 'VIEW_3D':
						bl_space.show_textured_solid = self.import_config.display_textured_solid


		return None

	'''
	Simplifies the reporting of errors to the user
	'''
	def report_error(self, message):
		TRACE(message)
		self.import_config.operator.report({'ERROR'},message)

	'''
	read our validated .ac file
	'''
	def read_ac_file(self, ac_file):
		reader = csv.reader(ac_file, delimiter=' ', skipinitialspace=True)
		try:
			for row in reader:
				# See if this is a valid token and pass the file handle and the current line to our function
				if row[0] in self.tokens.keys():
					self.tokens[row[0]](ac_file,row)
				else:
					self.report_error("invalid token: {tok} ({ln})".format(tok=row[0], ln=row))				
		except csv.Error(e):
			self.report_error('AC3D import error, line %d: %s' % (reader.line_num, e))

	'''
	Take the passed in line and interpret as a .ac material
	'''
	def read_material(self, ac_file, line):

		# MATERIAL %s rgb %f %f %f  amb %f %f %f  emis %f %f %f  spec %f %f %f  shi %d  trans %f
		self.matlist.append(AcMat(line[1],
						[float(x) for x in line[3:6]],
						[float(x) for x in line[7:10]],
						[float(x) for x in line[11:14]],
						[float(x) for x in line[15:18]],
						float(line[19]), # it should be int but float seems to be used sometimes
						float(line[21]),
						self.import_config,
						))

	'''
	Read the Object definition (including child objects)
	'''
	def read_object(self, ac_file, line):
		# OBJECT %s
		self.oblist.append(AcObj(line[1], ac_file, self.import_config))

	'''
	Reads the data imported from the file and creates blender data
	'''
	def create_blender_data(self):

		# go through the list of objects
		bUseLink = True
		for obj in self.oblist:
			if self.oblist.index(obj) == len(self.oblist)-1:
				bUseLink = False
			obj.create_blender_object(self.matlist, "", bUseLink)

