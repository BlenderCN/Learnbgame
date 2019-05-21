# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
	'name': 'VDrift tools',
	'description': 'Import-Export to VDrift track files',
	'author': 'NaN, port of VDrift blender24 scripts',
	'version': (0, 9),
	'blender': (2, 6, 3),
	'location': 'File > Import-Export',
	'warning': '',
	'wiki_url': 'http://',
	'tracker_url': 'http://',
	'category': 'Import-Export'}

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy_extras.image_utils import load_image
from struct import Struct
from os import path
from mathutils import Vector, Matrix

class joe_vertex:
	bstruct = Struct('<fff')

	# read list of 3-tuples
	@staticmethod
	def read(num, file):
		values = []
		for i in range(num):
			data = file.read(joe_vertex.bstruct.size)
			v = joe_vertex.bstruct.unpack(data)
			values.append(v)
		return values

	# write a list of 3-tuples
	@staticmethod
	def write(values, file):
		for v in values:
			data = joe_vertex.bstruct.pack(v[0], v[1], v[2])
			file.write(data)


class joe_texcoord:
	bstruct = Struct('<ff')

	# read a list of 2-tuples
	@staticmethod
	def read(num, file):
		values = []
		for i in range(num):
			data = file.read(joe_texcoord.bstruct.size)
			v = joe_texcoord.bstruct.unpack(data)
			values.append((v[0], 1 - v[1]))
		return values

	# write a list of 2-tuples
	@staticmethod
	def write(values, file):
		for v in values:
			data = joe_texcoord.bstruct.pack(v[0], 1 - v[1])
			file.write(data)


class joe_face:
	__slots__ = 'vertex_index', 'normal_index', 'texture_index'
	bstruct = Struct('<3h3h3h')

	def __init__(self):
		self.vertex_index = [0, 0, 0]
		self.normal_index = [0, 0, 0]
		self.texture_index = [0, 0, 0]

	def load (self, file):
		data = file.read(joe_face.bstruct.size)
		v = joe_face.bstruct.unpack(data)
		self.vertex_index = [v[0], v[1], v[2]]
		self.normal_index = [v[3], v[4], v[5]]
		self.texture_index = [v[6], v[7], v[8]]
		return self

	def save(self, file):
		data = joe_face.bstruct.pack(
			self.vertex_index[0],self.vertex_index[1],self.vertex_index[2],
			self.normal_index[0],self.normal_index[1],self.normal_index[2],
			self.texture_index[0],self.texture_index[1],self.texture_index[2])
		file.write(data)


class joe_frame:
	__slots__ = 'num_vertices', 'num_normals', 'num_texcoords',\
				'faces', 'verts', 'texcoords', 'normals'
	bstruct = Struct('<3i')

	def __init__(self):
		self.num_vertices = 0
		self.num_texcoords = 0
		self.num_normals = 0
		self.faces = []
		self.verts = []
		self.texcoords = []
		self.normals = []

	def load(self, file):
		# header
		data = file.read(joe_frame.bstruct.size)
		v = joe_frame.bstruct.unpack(data)
		self.num_vertices = v[0]
		self.num_texcoords = v[1]
		self.num_normals = v[2]
		# mesh data
		self.verts = joe_vertex.read(self.num_vertices, file)
		self.normals = joe_vertex.read(self.num_normals, file)
		self.texcoords = joe_texcoord.read(self.num_texcoords, file)
		return self

	def save(self, file):
		# header
		data = joe_frame.bstruct.pack(self.num_vertices, self.num_texcoords, self.num_normals)
		file.write(data)
		# mesh data
		joe_vertex.write(self.verts, file)
		joe_vertex.write(self.normals, file)
		joe_texcoord.write(self.texcoords, file)

	def from_mesh(self, obj):
		mesh = obj.data
		if obj.matrix_world != Matrix.Identity(4):
			mesh = obj.data.copy()
			mesh.transform(obj.matrix_world)
		if not mesh.tessfaces:
			mesh.calc_tessface()
		normals = util.indexed_set()
		vertices = util.indexed_set()
		texcoords = util.indexed_set()
		# get vertices and normals
		mvertices = mesh.vertices
		mtexcoords = mesh.tessface_uv_textures[0].data
		for fi, f in enumerate(mesh.tessfaces):
			uv = mtexcoords[fi].uv_raw
			if f.vertices_raw[3] != 0:
				# split quad in two tris
				d0 = (Vector(mvertices[2].co) - Vector(mvertices[0].co)).length_squared
				d1 = (Vector(mvertices[3].co) - Vector(mvertices[1].co)).length_squared
				if d0 < d1:
					vi1, vi2 = (0, 1, 2), (2, 3, 0)
				else:
					vi1, vi2 = (1, 2, 3), (3, 0, 1)
				jf = joe_face()
				jf.vertex_index = [vertices.get(mvertices[f.vertices_raw[i]].co) for i in vi2]
				if f.use_smooth:
					jf.normal_index = [normals.get(mvertices[f.vertices_raw[i]].normal) for i in vi2]
				else:
					jf.normal_index = [normals.get(f.normal)] * 3
				jf.texture_index = [texcoords.get((uv[i * 2], uv[i * 2 + 1])) for i in vi2]
				self.faces.append(jf)
			else:
				vi1 = (0, 1, 2)
			jf = joe_face()
			jf.vertex_index = [vertices.get(mvertices[f.vertices_raw[i]].co) for i in vi1]
			if f.use_smooth:
				jf.normal_index = [normals.get(mvertices[f.vertices_raw[i]].normal) for i in vi1]
			else:
				jf.normal_index = [normals.get(f.normal)] * 3
			jf.texture_index = [texcoords.get((uv[i * 2], uv[i * 2 + 1])) for i in vi1]
			self.faces.append(jf)
		self.normals = normals.list
		self.verts = vertices.list
		self.texcoords = texcoords.list
		self.num_normals = len(self.normals)
		self.num_texcoords = len(self.texcoords)
		self.num_vertices = len(self.verts)
		return self

	# remove faces consisting less then 3 vertices
	def remove_degenerate_faces(self):
		faces = []
		for f in self.faces:
			vi = f.vertex_index
			if vi[0] != vi[1] and vi[1] != vi[2] and vi[0] != vi[2]:
				faces.append(f)
		self.faces = faces

	# blender only supports one normal per vertex
	def duplicate_verts_with_multiple_normals(self):
		face_vert = {}
		verts = []
		for f in self.faces:
			for i in range(3):
				vn = f.vertex_index[i], f.normal_index[i]
				if vn not in face_vert:
					verts.append(self.verts[f.vertex_index[i]])
					vi = len(verts) - 1
					f.vertex_index[i] = vi
					face_vert[vn] = vi
				else:
					f.vertex_index[i] = face_vert[vn]
		self.verts = verts

	# in blender 2.5 the last vertex index shall not be 0
	def swizzle_face_vertices(self):
		for f in self.faces:
			vi = f.vertex_index
			ni = f.normal_index
			ti = f.texture_index
			if vi[2] == 0:
				vi[0], vi[1], vi[2] = vi[2], vi[0], vi[1]
				ni[0], ni[1], ni[2] = ni[2], ni[0], ni[1]
				ti[0], ti[1], ti[2] = ti[2], ti[0], ti[1]

	def to_mesh(self, name, image):
		# cleanup joe
		self.remove_degenerate_faces()
		self.swizzle_face_vertices()
		self.duplicate_verts_with_multiple_normals()

		# new mesh
		mesh = bpy.data.meshes.new(name)
		mesh.vertices.add(len(self.verts))
		mesh.tessfaces.add(len(self.faces))

		# set vertices
		for i, v in enumerate(self.verts):
			mesh.vertices[i].co = v
		for f in self.faces:
			for i in range(3):
				mesh.vertices[f.vertex_index[i]].normal = self.normals[f.normal_index[i]]

		# set faces
		for i, f in enumerate(self.faces):
			mesh.tessfaces[i].vertices = (f.vertex_index[0], f.vertex_index[1], f.vertex_index[2], 0)
			mesh.tessfaces[i].use_smooth = True

		# set texture coordinates
		if self.num_texcoords == 0:
			print("Warning! Mesh has no texture coordinates.")
		else:
			mesh.tessface_uv_textures.new()
			for i, f in enumerate(self.faces):
				mf = mesh.tessface_uv_textures[0].data[i]
				mf.uv1 = self.texcoords[f.texture_index[0]]
				mf.uv2 = self.texcoords[f.texture_index[1]]
				mf.uv3 = self.texcoords[f.texture_index[2]]
				if (image): mf.image = image

		mesh.validate()
		mesh.update()
		object = bpy.data.objects.new(name, mesh)
		bpy.context.scene.objects.link(object)
		return object


class joe_obj:
	__slots__ = 'ident', 'version', 'num_faces', 'num_frames', 'frames'
	bstruct = Struct('<4i')

	def __init__(self):
		self.ident = 844121161
		self.version = 3
		self.num_faces = 0
		self.num_frames = 0
		self.frames = []

	def load(self, file):
		# header
		data = file.read(joe_obj.bstruct.size)
		v = joe_obj.bstruct.unpack(data)
		self.ident = v[0]
		self.version = v[1]
		self.num_faces = v[2]
		self.num_frames = v[3]
		# frames
		for i in range(self.num_frames):
			self.frames.append(joe_frame())
			for j in range(self.num_faces):
				self.frames[i].faces.append(joe_face().load(file))
			self.frames[i].load(file)
		return self

	def save(self, file):
		# header
		data = joe_obj.bstruct.pack(self.ident, self.version, self.num_faces, self.num_frames)
		file.write(data)
		# frames
		for i in range(self.num_frames):
			for j in range(self.num_faces):
				self.frames[i].faces[j].save(file)
			self.frames[i].save(file)

	def to_mesh(self, name, image, num_frames=1):
		frames = []
		if name.endswith('.joe'):
			name = name[:-4]
		for i in range(num_frames):
			bpy.context.scene.frame_set(i)
			frames.append(self.frames[i].to_mesh(name, image))
		return frames[0]

	def from_mesh(self, mesh_obj, num_frames=1):
		for i in range(num_frames):
			bpy.context.scene.frame_set(i)
			frame = joe_frame()
			frame.from_mesh(mesh_obj)
			self.frames.append(frame)
		self.num_frames = num_frames
		self.num_faces = len(self.frames[0].faces)
		return self


class joe_pack:
	version = b'JPK01.00'
	bstruct = Struct('<2i')

	def __init__(self):
		self.numobjs = 0
		self.maxstrlen = 0
		self.joe = {}
		self.list = {}
		self.images = {}
		self.surfaces = []

	@staticmethod
	def read(filename):
		# don't change call order
		jpk = joe_pack()
		jpk.load_list(filename)
		jpk.load_images(filename)
		try:
			jpk.load(filename)
		except:
			jpk.load_joes(filename)
		return jpk


	@staticmethod
	def write(filename, write_list, write_jpk):
		jpk = joe_pack().from_mesh()
		if write_jpk:
			jpk.save(filename)
		if write_list:
			jpk.save_list(filename)

	def to_mesh(self):
		trackobject.create_groups()
		for name, joe in self.joe.items():
			image = None
			trackobj = self.list.get(name)
			if trackobj:
				imagename = trackobj.values[1]
				image = self.images[imagename]
				obj = joe.to_mesh(name, image)
				trackobj.to_obj(obj)
			else:
				print(name + ' not imported. Not in list.txt.')

	def from_mesh(self):
		objlist = bpy.context.scene.objects
		trackobject.set_groups()
		for obj in objlist:
			if obj.type != 'MESH':
				continue
			if obj.name.startswith('~'):
				continue
			if not obj.data.tessfaces:
				obj.data.calc_tessface()
				if len(obj.data.tessfaces) == 0:
					print(obj.name + ' not exported. No faces.')
					continue
			if not obj.data.tessface_uv_textures:
				print(obj.name + ' not exported. No texture coordinates.')
				continue
			image = None
			if obj.data.tessface_uv_textures[0].data[0].image:
				image = obj.data.tessface_uv_textures[0].data[0].image
			else:
				for mat_slot in obj.material_slots:
					for mtex_slot in mat_slot.material.texture_slots:
						if mtex_slot and hasattr(mtex_slot.texture, 'image'):
							image =  mtex_slot.texture.image
							break
			if not image:
				print(obj.name + ' not exported. No texture linked.')
				continue
			objname = obj.name
			trackobj = trackobject().from_obj(obj, path.basename(image.filepath))
			# override obj name
			if len(trackobj.values[0]):
				objname = trackobj.values[0]
			# loader expects a joe file
			if not objname.endswith('.joe'):
				objname = objname + '.joe'
				trackobj.values[0] = objname
			self.list[objname] = trackobj
			self.joe[objname] = obj
			self.maxstrlen = max(self.maxstrlen, len(objname))
		self.numobjs = len(self.joe)
		return self

	# fallback if no jpk
	def load_joes(self, filename):
		dir = path.dirname(filename)
		for name in self.list:
			joe_path = path.join(dir, name)
			file = open(joe_path, 'rb')
			joe = joe_obj().load(file)
			self.joe[name] = joe

	def load(self, filename):
		file = open(filename, 'rb')
		# header
		version = file.read(len(joe_pack.version))
		if version != joe_pack.version:
			raise Exception(filename + ' unknown jpk version: ' + str(version) + ' expected: ' + str(joe_pack.version))
		data = file.read(joe_pack.bstruct.size)
		v = joe_pack.bstruct.unpack(data)
		self.numobjs = v[0]
		self.maxstrlen = v[1]
		# fat
		fat = []
		for i in range(self.numobjs):
			data = file.read(joe_pack.bstruct.size)
			v = joe_pack.bstruct.unpack(data)
			offset = v[0]
			length = v[1]
			data = file.read(self.maxstrlen)
			# strip trailing zeros
			for i in range(self.maxstrlen):
				if data[i] == 0:
					data = data[:i]
					break
			name = data.decode('ascii')
			fat.append((offset, length, name))
		# data
		for offset, length, name in fat:
			pos = file.tell()
			delta = offset - pos
			if delta < 0:
				print('Error reading: ', name, offset)
				return
			elif delta > 0:
				file.read(delta)
			joe = joe_obj().load(file)
			self.joe[name] = joe
		file.close()

	def save(self, filename):
		try:
			file = open(filename, 'rb+')
		except IOError:
			file = open(filename, 'wb')
		# header
		file.write(self.version)
		data = joe_pack.bstruct.pack(self.numobjs, self.maxstrlen)
		file.write(data)
		# allocate fat
		fat_offset = file.tell()
		for i in range(self.numobjs):
			data = joe_pack.bstruct.pack(0, 0)
			file.write(data)
			name = util.fillz('', self.maxstrlen)
			file.write(name.encode('ascii'))
		# write data / build fat
		fat = []
		for name, obj in self.joe.items():
			offset = file.tell()
			joe = joe_obj().from_mesh(obj)
			joe.save(file)
			length = file.tell() - offset
			fat.append((offset, length, name))
		# fill fat
		file.seek(fat_offset)
		for offset, length, name in fat:
			data = joe_pack.bstruct.pack(offset, length)
			file.write(data)
			name = util.fillz(name, self.maxstrlen)
			file.write(name.encode('ascii'))
		file.close()

	def load_list(self, filename):
		dir = path.dirname(filename)
		list_path = path.join(dir, 'list.txt')
		try:
			list_file = open(list_path)
		except IOError:
			print(list_path + ' not found.')
			return
		# read objects
		line = list_file.readline()
		while line != '':
			if not line.startswith('#') and '.joe' in line:
				object = trackobject()
				name = line.strip()
				line = object.read(name, list_file)
				self.list[object.values[0]] = object
			else:
				line = list_file.readline()
		if len(self.list) == 0:
			print('Failed to load list.txt.')
		list_file.close()

	def save_list(self, filename):
		dir = path.dirname(filename)
		list_path = path.join(dir, 'list.txt')
		file = open(list_path, 'w')
		file.write('17\n\n')
		i = 0
		for name, object in self.list.items():
			file.write('#entry ' + str(i) + '\n')
			object.write(file)
			i = i + 1
		file.close()

	def load_images(self, filename):
		dir = path.dirname(filename)
		for name, object in self.list.items():
			imagename = object.values[1]
			if imagename not in self.images:
				imagepath = path.join(dir, imagename)
				self.images[imagename] = load_image(imagepath)


class trackobject:
	names = ('model', 'texture', 'mipmap', 'lighting', 'skybox', 'blend',\
			'bump length', 'bump amplitude', 'drivable', 'collidable',\
			'non treaded', 'treaded', 'roll resistance', 'roll drag',\
			'shadow', 'clamp', 'surface')
	namemap = dict(zip(names, range(17)))

	@staticmethod
	def create_groups():
		trackobject.grp_surf = []
		trackobject.grp = {}
		for name in ('mipmap', 'nolighting', 'skybox', 'transparent',\
					'doublesided', 'collidable', 'shadow', 'clampu', 'clampv'):
			grp = bpy.data.groups.get(name)
			if grp == None:
				grp = bpy.data.groups.new(name)
				# need to link an object to group to make it visible
				obj = bpy.data.objects.get('0')
				if not obj:
					obj = bpy.data.objects.new('0', None)
				grp.objects.link(obj)
			trackobject.grp[name] = grp.objects

	@staticmethod
	def set_groups():
		trackobject.create_groups()
		trackobject.is_surf = []
		for grp in bpy.data.groups:
			if grp.name == 'mipmap':
				trackobject.is_mipmap = set(grp.objects)
			elif grp.name == 'nolighting':
				trackobject.is_nolighting = set(grp.objects)
			elif grp.name == 'skybox':
				trackobject.is_skybox = set(grp.objects)
			elif grp.name == 'transparent':
				trackobject.is_transparent = set(grp.objects)
			elif grp.name == 'doublesided':
				trackobject.is_doublesided = set(grp.objects)
			elif grp.name == 'collidable':
				trackobject.is_collidable = set(grp.objects)
			elif grp.name == 'shadow':
				trackobject.is_shadow = set(grp.objects)
			elif grp.name == 'clampu':
				trackobject.is_clampu = set(grp.objects)
			elif grp.name == 'clampv':
				trackobject.is_clampv = set(grp.objects)
			elif grp.name.startswith('surface'):
				trackobject.is_surf.append((grp.name.split('-')[-1], set(grp.objects)))

	def __init__(self):
		self.values = ['none', 'none', '1', '0', '0', '0',\
						'1.0', '0.0', '0', '0',\
						'1.0', '0.9', '1.0', '0.0',\
						'0', '0', '0']

	def read(self, name, list_file):
		i = 0
		self.values[i] = name
		while True:
			line = list_file.readline()
			if line == '' or '.joe' in line:
				return line
			elif line.startswith('#') or line.startswith('\n'):
				continue
			else:
				i = i + 1
				self.values[i] = line.strip()
		return line

	def write(self, list_file):
		for v in self.values:
			list_file.write(v + '\n')
		list_file.write('\n')

	def to_obj(self, object):
		object['model'] = self.values[0]
		object['texture'] = self.values[1]
		if self.values[2] == '1': trackobject.grp['mipmap'].link(object)
		if self.values[3] == '1': trackobject.grp['nolighting'].link(object)
		if self.values[4] == '1': trackobject.grp['skybox'].link(object)
		if self.values[5] == '1': trackobject.grp['transparent'].link(object)
		if self.values[5] == '2': trackobject.grp['doublesided'].link(object)
		if self.values[8] == '1' or self.values[9] == '1': trackobject.grp['collidable'].link(object)
		if self.values[14] == '1': trackobject.grp['shadow'].link(object)
		if self.values[15] == '1' or self.values[15] == '3': trackobject.grp['clampu'].link(object)
		if self.values[15] == '2' or self.values[15] == '3': trackobject.grp['clampv'].link(object)
		surfid = int(self.values[16])
		while surfid >= len(trackobject.grp_surf):
			surfnum = len(trackobject.grp_surf)
			surfname = 'surface-'+str(surfnum)
			grp = bpy.data.groups.get(surfname)
			if grp == None:
				grp = bpy.data.groups.new(surfname)
			trackobject.grp_surf.append(grp.objects)
		trackobject.grp_surf[surfid].link(object)
		return self

	# set from object
	def from_obj(self, object, texture):
		model = object.name
		self.values[0] = object.get('model', model)
		self.values[1] = object.get('texture', texture)
		self.values[2] = '1' if object in trackobject.is_mipmap else '0'
		self.values[3] = '1' if object in trackobject.is_nolighting else '0'
		self.values[4] = '1' if object in trackobject.is_skybox else '0'
		if object in trackobject.is_transparent: self.values[5] = '1'
		elif object in trackobject.is_doublesided: self.values[5] = '2'
		else: self.values[5] = '0'
		self.values[9] = '1' if object in trackobject.is_collidable else '0'
		self.values[14] = '1' if object in trackobject.is_shadow else '0'
		self.values[15] = '1' if object in trackobject.is_clampu else '0'
		if object in trackobject.is_clampv:
			self.values[15] = '2' if self.values[15] == '0' else '3'
		for name, grp in self.is_surf:
			if object in grp:
				self.values[16] = name
				break
		return self


class roads:
	@staticmethod
	def load(path):
		file = open(path, 'r')
		roadnum = int(file.readline())
		file.readline()
		for i in range(roadnum):
			roads.load_road(file, 'road.' + str(i))

	@staticmethod
	def save(path):
		file = open(path, 'w')
		meshes = []
		i = 0
		while 'road.' + str(i) in bpy.data.objects:
			obj = bpy.data.objects['road.' + str(i)]
			mesh = obj.data
			if obj.matrix_world != Matrix.Identity(4):
				mesh = obj.data.copy()
				mesh.transform(obj.matrix_world)
			meshes.append(mesh)
			i = i + 1
		file.write(str(len(meshes)) + '\n\n')
		for m in meshes:
			roads.save_road(file, m)

	@staticmethod
	def load_road(file, name):
		patchnum = int(file.readline())
		file.readline()
		# new mesh
		mesh = bpy.data.meshes.new(name)
		mesh.vertices.add(patchnum * 4 + 4)
		mesh.tessfaces.add(patchnum * 3)
		mesh.tessface_uv_textures.new()
		# parse road
		lines = [None] * 16
		for p in range(patchnum):
			# road is stored reversed
			for n in range(15, -1, -1):
				lines[n] = file.readline()
			file.readline()
			# vertices first row, other rows are interpolated on export
			for n in range(4):
				i = p * 4 + n
				xyz = [float(s) for s in lines[n].split()]
				mesh.vertices[i].co = (xyz[2], xyz[0], xyz[1])
			# faces
			for n in range(3):
				i = p * 3 + n
				vi = p * 4 + n
				mesh.tessfaces[i].vertices_raw = (vi, vi + 4, vi + 5, vi + 1)
				mesh.tessfaces[i].use_smooth = True
				u, v = 1 - n/3.0, float(p)
				mesh.tessface_uv_textures[0].data[i].uv_raw = (u, v, u, v + 1, u - 1/3.0, v + 1, u - 1/3.0, v)
		# last row
		for n in range(4):
			i = patchnum * 4 + n
			xyz = [float(s) for s in lines[n + 12].split()]
			mesh.vertices[i].co = (xyz[2], xyz[0], xyz[1])
		# new object
		mesh.validate()
		mesh.update(calc_tessface = True)
		object = bpy.data.objects.new(name, mesh)
		bpy.context.scene.objects.link(object)

	@staticmethod
	def save_road(file, mesh):
		if not mesh.tessfaces:
			mesh.calc_tessface()
		patchnum = int(len(mesh.vertices) / 4 - 1)
		#print('patches from facenum ' + str(len(mesh.tessfaces) / 3))
		#print('patches from vertnum ' + str(patchnum))
		road = [None] * 16 * patchnum
		if len(mesh.tessface_uv_textures) == 0 or len(mesh.tessface_uv_textures[0].data) == 0:
			raise NameError("Road mesh %s has no uv coordinates" % mesh.name)
		# get first, last patch rows from faces
		for i, f in enumerate(mesh.tessfaces):
			tf = mesh.tessface_uv_textures[0].data[i]
			for n in range(4):
				pointid = int(round(tf.uv_raw[2 * n] * 3))
				patchid = int(round(tf.uv_raw[2 * n + 1]))
				id = patchid * 16 + pointid
				if patchid < patchnum:
					road[id] = mesh.vertices[f.vertices[n]].co
				if patchid > 0:
					road[id - 4] = mesh.vertices[f.vertices[n]].co
		# debug
		#for i, p in enumerate(road):
		#	if p:
		#		file.write(str(i) + ' %.4f %.4f %.4f\n' % (p[1], p[2], p[0]))
		#	else:
		#		file.write(str(i) + '\n')
		# calculate middle rows
		for i in range(patchnum - 1):
			roads.attach_patches(road, i, i + 1)
		# closed/open road
		if (road[0] - road[-1]).length < 1E-3:
			roads.attach_patches(road, -1, 0)
		else:
			roads.set_middlerow(road, 0, 1)
			roads.set_middlerow(road, -1, 2)
		# write road
		file.write(str(patchnum) + '\n\n')
		for i in range(patchnum):
			for n in range(3, -1, -1):
				for m in range(4):
					p = road[i * 16 + n * 4 + m]
					file.write('%.4f %.4f %.4f\n' % (p[1], p[2], p[0]))
			file.write('\n')

	# p0: first patch index
	# p1: second patch index
	@staticmethod
	def attach_patches(road, p0, p1):
		r0 = p0 * 16
		r1 = p1 * 16
		for n in range(4):
			i0 = r0 + n
			i1 = r1 + n
			slope = (road[i1 + 12] - road[i0]).normalized()
			len0 = (road[i0 + 12] - road[i0]).length
			len1 = (road[i1 + 12] - road[i1]).length
			scale = min(len1, len0) / 3.0 #old: (len1 + len0) / 6.0
			road[i0 + 8] = road[i0 + 12] - slope * scale
			road[i1 + 4] = road[i1] + slope * scale

	# pi: patch index [0, patchnum)
	# ri: middle row index 1, 2
	@staticmethod
	def set_middlerow(road, pi, ri):
		scale = ri / 3
		for n in range(4):
			i = pi * 16 + n
			road[i + ri * 4] = road[i] + (road[i + 12] - road[i]) * scale


class track:
	@staticmethod
	def load(path):
		start_position = {}
		obj = track.get_info()
		file = open(path, 'r')
		for line in file:
			line = line.rstrip('\n')
			if not line: continue
			name, value = line.split(' = ', 1)
			# generic properties (as strings for now)
			if name in obj:
				#if value == 'on' or value == 'yes': value = True
				#elif value == 'off' or value == 'no': value = False
				#ob[name] = type(ob[name])(value)
				obj[name] = value
			# lap sequences (as strings for now)
			elif name.startswith('lap sequence '):
				road, patch, unused = value.split(',', 2)
				obj[name] = road.split('.', 1)[0] + ':' + patch.split('.', 1)[0]
			# start positions
			elif name.startswith('start position '):
				x, y, z = value.split(',', 2)
				track.get_box(name).location = (float(z), float(x), float(y))
			elif name.startswith('start orientation '):
				rad = 0.0174532925
				x, y, z = value.split(',', 2)
				x, y, z = float(x) * rad, float(y) * rad, float(z) * rad
				name = 'start position ' + name.rsplit(' ', 1)[1]
				track.get_box(name).rotation_euler = (z, x, y)
		file.close()

	@staticmethod
	def save(path):
		file = open(path, 'w')
		obj = track.get_info()
		lap_sequence = []
		for k, v in obj.items():
			if k.startswith('lap sequence'):
				lap_sequence.append((k, v))
			else:
				file.write(k + ' = ' + str(v) + '\n')
		file.write('lap sequences = ' + str(len(lap_sequence)) + '\n')
		for v in lap_sequence:
			name = v[0]
			road, patch = v[1].split(':', 1)
			file.write(name + ' = ' + road + ',' + patch + ',0\n')
		n = 0
		while True:
			name = 'start position ' + str(n)
			obj = bpy.data.objects.get(name)
			if not obj: break
			x, y, z = obj.location
			file.write('start position %s = %.4f,%.4f,%.4f\n' % (str(n), y, z, x))
			deg = 57.2957795
			x, y, z = obj.rotation_euler
			x, y, z = x * deg, y * deg, z * deg
			file.write('start orientation %s = %.2f,%.2f,%.2f\n' % (str(n), y, z, x))
			n = n + 1
		file.close()

	@staticmethod
	def get_info():
		obj = bpy.data.objects.get('track_info')
		if not obj:
			obj = bpy.data.objects.new('track_info', None)
			obj['cull faces'] = 'on'
			obj['vertical tracking skyboxes'] = 'no'
			obj['non-treaded friction coefficient'] = '1.0'
			obj['treaded friction coefficient'] = '0.9'
			bpy.context.scene.objects.link(obj)
		return obj;

	@staticmethod
	def get_box(name):
		obj = bpy.data.objects.get(name)
		if not obj:
			verts = [(1,-1,-1), (1,-1,1),(-1,-1,1),(-1,-1,-1),(1,1,-1),(1,1,1),(-1,1,1),(-1,1,-1)]
			edges = [(0,1),(1,2),(2,3),(3,7),(4,7),(5,6),(6,7),(0,3),(4,5),(1,5),(2,6),(0,4)]
			mesh = bpy.data.meshes.new("cube")
			mesh.from_pydata(verts, edges, [])
			obj = bpy.data.objects.new(name, mesh)
			bpy.context.scene.objects.link(obj)
			obj.scale = (2.0, 0.9, 0.5)
			obj.show_axis = True
		return obj


class util:
	# helper class to filter duplicates
	class indexed_set(object):
		def __init__(self):
			self.map = {}
			self.list = []
		def get(self, ob):
			# using float as key in dict
			fixed = tuple(round(n, 5) for n in ob)
			if not fixed in self.map:
				ni = len(self.list)
				self.map[fixed] = ni
				self.list.append(fixed)
			else:
				ni = self.map[fixed]
			return ni

	# fill trailing zeroes
	@staticmethod
	def fillz(str, strlen):
		return str + chr(0)*(strlen - len(str))


class export_joe(bpy.types.Operator, ExportHelper):
	bl_idname = 'export.joe'
	bl_label = 'Export JOE'
	filename_ext = '.joe'
	filter_glob = StringProperty(
			default='*.joe',
			options={'HIDDEN'})

	def __init__(self):
		try:
			self.object = bpy.context.selected_objects[0]
		except:
			self.object = None

	def execute(self, context):
		props = self.properties
		filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)
		if len(bpy.context.selected_objects[:]) != 1:
			raise NameError('Please select one object!')
		object = self.object
		if object.type != 'MESH':
			raise NameError('Selected object must be a mesh!')
		try:
			file = open(filepath, 'wb')
			joe = joe_obj().from_mesh(object)
			joe.save(file)
			file.close()
		finally:
			self.report({'INFO'},  object.name + ' exported')
		return {'FINISHED'}

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self);
		return {'RUNNING_MODAL'}


class import_joe(bpy.types.Operator, ImportHelper):
	bl_idname = 'import.joe'
	bl_label = 'Import JOE'
	filename_ext = '.joe'
	filter_glob = StringProperty(
		default='*.joe',
		options={'HIDDEN'})

	def execute(self, context):
		props = self.properties
		filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)
		try:
			image = None #load_image(filepath_img)
			file = open(filepath, 'rb')
			joe = joe_obj().load(file)
			joe.to_mesh(bpy.path.basename(filepath), image)
			file.close()
		finally:
			self.report({'INFO'},  filepath + ' imported')
		return {'FINISHED'}


class import_image(bpy.types.Operator, ImportHelper):
	bl_idname = 'import.image'
	bl_label = 'Import texture'
	filename_ext = '.png'
	filter_glob = StringProperty(
		default='*.png',
		options={'HIDDEN'})

	def execute(self, context):
		props = self.properties
		filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)
		image = load_image(filepath)
		if image == None:
			raise NameError('Failed to load image!')
		if len(bpy.context.selected_objects[:]) != 1:
			raise NameError('Please select one object!')
		object = bpy.context.selected_objects[0]
		if object.type != 'MESH':
			raise NameError('Selected object must be a mesh!')
		if len(object.data.tessfaces) == 0:
			object.data.calc_tessface()
		if len(object.data.tessfaces) == 0:
			raise NameError('Selected object has no faces!')
		if len(object.data.tessface_uv_textures) == 0:
			raise NameError('Selected object has no texture coordinates!')
		for mf in object.data.tessface_uv_textures[0].data:
			mf.image = image
		return {'FINISHED'}


class export_jpk(bpy.types.Operator, ExportHelper):
	bl_idname = 'export.jpk'
	bl_label = 'Export JPK'
	filename_ext = '.jpk'
	filter_glob = StringProperty(
			default='*.jpk',
			options={'HIDDEN'})
	export_list = BoolProperty(
			name='Export properties (list.txt)',
			description='Export track objects properties',
			default=True)
	export_jpk = BoolProperty(
			name='Export objects (objects.jpk)',
			description='Export track objects as JPK',
			default=True)

	def execute(self, context):
		props = self.properties
		filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)
		joe_pack.write(filepath, self.export_list, self.export_jpk)
		return {'FINISHED'}

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self);
		return {'RUNNING_MODAL'}


class import_jpk(bpy.types.Operator, ImportHelper):
	bl_idname = 'import.jpk'
	bl_label = 'Import JPK'
	filename_ext = '.jpk'
	filter_glob = StringProperty(
		default='*.jpk',
		options={'HIDDEN'})

	def execute(self, context):
		props = self.properties
		filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)
		jpk = joe_pack.read(filepath)
		jpk.to_mesh()
		return {'FINISHED'}


class import_joe_list(bpy.types.Operator, ImportHelper):
	bl_idname = 'import.list'
	bl_label = 'Import VDrift track objects'
	filename_ext = '.txt'
	filter_glob = StringProperty(
		default='*.txt',
		options={'HIDDEN'})

	def execute(self, context):
		props = self.properties
		filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)
		jpk = joe_pack.read(filepath)
		jpk.to_mesh()
		return {'FINISHED'}


class export_trk(bpy.types.Operator, ExportHelper):
	bl_idname = 'export.trk'
	bl_label = 'Export Vdrift roads'
	filename_ext = '.trk'
	filter_glob = StringProperty(
			default='*.trk',
			options={'HIDDEN'})

	def execute(self, context):
		props = self.properties
		filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)
		roads.save(filepath)
		return {'FINISHED'}

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self);
		return {'RUNNING_MODAL'}


class import_trk(bpy.types.Operator, ImportHelper):
	bl_idname = 'import.trk'
	bl_label = 'Import VDrift roads'
	filename_ext = '.trk'
	filter_glob = StringProperty(
		default='*.trk',
		options={'HIDDEN'})

	def execute(self, context):
		props = self.properties
		filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)
		roads.load(filepath)
		return {'FINISHED'}


class export_track(bpy.types.Operator, ExportHelper):
	bl_idname = 'export.track'
	bl_label = 'Export Vdrift track'
	filename_ext = '.txt'
	filter_glob = StringProperty(
			default='track.txt',
			options={'HIDDEN'})

	def execute(self, context):
		props = self.properties
		filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)
		track.save(filepath)
		return {'FINISHED'}

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self);
		return {'RUNNING_MODAL'}


class import_track(bpy.types.Operator, ImportHelper):
	bl_idname = 'import.track'
	bl_label = 'Import VDrift track'
	filename_ext = '.txt'
	filter_glob = StringProperty(
		default='track.txt',
		options={'HIDDEN'})

	def execute(self, context):
		props = self.properties
		filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)
		track.load(filepath)
		return {'FINISHED'}

def read_vec(str):
	return tuple(float(i) for i in (str.split('#', 1)[0]).split(','))

def load_suspension(cfg, wheel_name):
	name = wheel_name+'.double-wishbone'
	if name in cfg:
		s = cfg[name]
		ucf = read_vec(s['upper-chassis-front'])
		ucr = read_vec(s['upper-chassis-rear'])
		uh = read_vec(s['upper-hub'])
		lcf = read_vec(s['lower-chassis-front'])
		lcr = read_vec(s['lower-chassis-rear'])
		lh = read_vec(s['lower-hub'])
		verts = [ucf, uh, ucr, lcf, lh, lcr]
		edges = [(0,1), (1,2), (2,0), (3,4), (4,5), (5,3), (1,4)]
	else:
		name = wheel_name+'.macpherson-strut'
		if name in cfg:
			s = cfg[name]
			e = read_vec(s['strut-end'])
			t = read_vec(s['strut-top'])
			h = read_vec(s['hinge'])
			verts = [h, e, t]
			edges = [(0,1), (1,2)]
		else:
			name = wheel_name+'.hinge'
			s = cfg[name]
			hw = read_vec(s['wheel'])
			hb = read_vec(s['chassis'])
			verts = [hw, hb]
			edges = [(0,1)]
	mesh = bpy.data.meshes.new(name)
	mesh.from_pydata(verts, edges, [])
	obj = bpy.data.objects.new(name, mesh)
	bpy.context.scene.objects.link(obj)

def load_wheel(cfg, wheel_name):
	tp = read_vec(cfg[wheel_name]['position'])
	ts = read_vec(cfg[wheel_name+'.tire']['size'])
	tw = ts[0] * 0.001
	ta = ts[1] * 0.01
	tr = ts[2] * 0.5 * 0.0254 + tw * ta
	bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=tr, depth=tw, location=tp, rotation=(0.0, 1.5708, 0.0))
	load_suspension(cfg, wheel_name)

class import_car(bpy.types.Operator, ImportHelper):
	bl_idname = 'import.car'
	bl_label = 'Import VDrift car'
	filename_ext = '.car'
	filter_glob = StringProperty(
		default='*.car',
		options={'HIDDEN'})

	def execute(self, context):
		props = self.properties
		filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)
		try:
			from configparser import ConfigParser
			cfg = ConfigParser()
			cfg.read(filepath)
			load_wheel(cfg, 'wheel.fl')
			load_wheel(cfg, 'wheel.fr')
			load_wheel(cfg, 'wheel.rl')
			load_wheel(cfg, 'wheel.rr')

			filepath = path.join(path.dirname(filepath), 'body.joe')
			file = open(filepath, 'rb')
			joe = joe_obj().load(file)
			joe.to_mesh(bpy.path.basename(filepath), None)
			file.close()
		finally:
			self.report({'INFO'},  filepath + ' imported')
		return {'FINISHED'}


def menu_export_joe(self, context):
	self.layout.operator(export_joe.bl_idname, text = 'VDrift JOE (.joe)')


def menu_import_joe(self, context):
	self.layout.operator(import_joe.bl_idname, text = 'VDrift JOE (.joe)')


def menu_import_image(self, context):
	self.layout.operator(import_image.bl_idname, text = 'VDrift Texture (.png)')


def menu_export_jpk(self, context):
	self.layout.operator(export_jpk.bl_idname, text = 'VDrift JPK (.jpk)')


def menu_import_jpk(self, context):
	self.layout.operator(import_jpk.bl_idname, text = 'VDrift JPK (.jpk)')


def menu_import_joe_list(self, context):
	self.layout.operator(import_joe_list.bl_idname, text = 'VDrift Track Objects (list.txt)')


def menu_export_trk(self, context):
	self.layout.operator(export_trk.bl_idname, text = 'VDrift Roads (.trk)')


def menu_import_trk(self, context):
	self.layout.operator(import_trk.bl_idname, text = 'VDrift Roads (.trk)')


def menu_export_track(self, context):
	self.layout.operator(export_track.bl_idname, text = 'VDrift Track Info (track.txt)')


def menu_import_track(self, context):
	self.layout.operator(import_track.bl_idname, text = 'VDrift Track Info (track.txt)')


def menu_import_car(self, context):
	self.layout.operator(import_car.bl_idname, text = 'VDrift Car (.car)')


def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_export.append(menu_export_joe)
	bpy.types.INFO_MT_file_import.append(menu_import_joe)
	bpy.types.INFO_MT_file_import.append(menu_import_image)
	bpy.types.INFO_MT_file_export.append(menu_export_jpk)
	bpy.types.INFO_MT_file_import.append(menu_import_jpk)
	bpy.types.INFO_MT_file_export.append(menu_export_trk)
	bpy.types.INFO_MT_file_import.append(menu_import_trk)
	bpy.types.INFO_MT_file_export.append(menu_export_track)
	bpy.types.INFO_MT_file_import.append(menu_import_track)
	bpy.types.INFO_MT_file_import.append(menu_import_joe_list)
	bpy.types.INFO_MT_file_import.append(menu_import_car)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_export.remove(menu_export_joe)
	bpy.types.INFO_MT_file_import.remove(menu_import_joe)
	bpy.types.INFO_MT_file_import.remove(menu_import_image)
	bpy.types.INFO_MT_file_export.remove(menu_export_jpk)
	bpy.types.INFO_MT_file_import.remove(menu_import_jpk)
	bpy.types.INFO_MT_file_export.remove(menu_export_trk)
	bpy.types.INFO_MT_file_import.remove(menu_import_trk)
	bpy.types.INFO_MT_file_export.remove(menu_export_track)
	bpy.types.INFO_MT_file_import.remove(menu_import_track)
	bpy.types.INFO_MT_file_import.append(menu_import_joe_list)
	bpy.types.INFO_MT_file_import.append(menu_import_car)

if __name__ == '__main__':
	register()