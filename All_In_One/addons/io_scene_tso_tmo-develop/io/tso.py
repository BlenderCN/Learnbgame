#!/usr/bin/env python

"""TechArts3D tso file format
"""

import os
import re
import numpy as np
from struct import pack, unpack, unpack_from
from mathutils import Matrix, Vector
from io_scene_tso_tmo import turned_nodes

def read_cstring(file):
	bytes = b''
	while True:
		c = file.read(1)
		if c == b'\x00':
			break
		bytes += c
	str = bytes.decode('cp932')
	return str

def read_int(file):
	return unpack('<i', file.read(4))[0]

def read_matrix4(file):
	return [ unpack('<4f', file.read(16)) for i in range(4) ]

def read_vector3(file):
	return unpack('<3f', file.read(12))

def read_vector2(file):
	return unpack('<2f', file.read(8))


def write_cstring(file, value):
	bytes = value.encode('cp932')
	file.write(bytes)
	file.write(b'\x00')

def write_int(file, value):
	file.write(pack('<i', value))

def write_float(file, value):
	file.write(pack('<f', value))

def write_matrix4(file, value):
	# assert len(value) == 4
	for row in value:
		# assert len(row) == 4
		file.write(pack('<4f', *row))

def write_vector3(file, value):
	file.write(pack('<3f', *value))

def write_vector2(file, value):
	file.write(pack('<2f', *value))


class TSONode(object):

	def __init__(self):
		self.name = None
		self.parent_name = None
		self.path = None
		self.transform = None

		self.parent = None
		self.b_transform = None

	def read(self, file):
		path = read_cstring(file)

		names = path.rsplit('|', 2)
		self.name = names[-1]
		self.parent_name = names[-2]
		self.path = path
		# print("tso node name:{} parent_name:{}".format(self.name, self.parent_name))

	def write(self, file):
		write_cstring(file, self.path)

	def b_world_coordinate(self):
		node = self
		m = Matrix.Identity(4)
		while node:
			m = node.b_transform * m
			node = node.parent

		return m

class TSOTexture(object):
	def __init__(self):
		self.name = None
		self.path = None
		self.width = 0
		self.height = 0
		self.depth = 0
		self.data = None

	def read(self, file):
		self.name = read_cstring(file)
		self.path = read_cstring(file)
		width, height, depth = unpack('<3i', file.read(12))
		self.width = width
		self.height = height
		self.depth = depth
		buf = file.read(width * height * depth)
		ary = []
		for i in range(0, len(buf), 4):
			ary.append(buf[i + 2])
			ary.append(buf[i + 1])
			ary.append(buf[i + 0])
			ary.append(buf[i + 3])
		self.data = bytes(ary)

	def write(self, file):
		write_cstring(file, self.name)
		write_cstring(file, self.path)
		write_int(file, self.width)
		write_int(file, self.height)
		write_int(file, self.depth)
		buf = self.data
		ary = []
		for i in range(0, self.width * self.height * self.depth, 4):
			ary.append(buf[i + 2])
			ary.append(buf[i + 1])
			ary.append(buf[i + 0])
			ary.append(buf[i + 3])
		file.write(bytes(ary))

	def data_pixels(self):
		ary = np.frombuffer(self.data, dtype=np.uint8)
		linear_shape = ary.shape

		# BGRA to RGBA
		ary = np.reshape(ary, (-1, 4))
		ary = ary[:, [2,1,0,3]]
		ary = np.reshape(ary, linear_shape)

		# uint8 to float32
		return ary.astype(np.float32) / 255.0  # 0..1

	def pixels_data(self, pixels):
		ary = np.asarray(pixels, dtype=np.float32) * 255.0
		ary = ary.astype(np.uint8)
		linear_shape = ary.shape

		# RGBA to BGRA
		ary = np.reshape(ary, (-1, 4))
		ary = ary[:, [2,1,0,3]]
		ary = np.reshape(ary, linear_shape)

		self.data = ary.tobytes()


class TSOScript(object):
	def __init__(self):
		self.name = None
		self.lines = []

	def read(self, file):
		self.name = read_cstring(file)
		lines_count = read_int(file)
		del self.lines[:]
		for x in range(lines_count):
			line = read_cstring(file)
			self.lines.append(line)

	def write(self, file):
		write_cstring(file, self.name)
		write_int(file, len(self.lines))
		for line in self.lines:
			write_cstring(file, line)

class TSOSubScript(object):
	def __init__(self):
		self.name = None
		self.path = 'cgfxShader'
		self.lines = []
		self.map = {}

		self.b_material = None
		self.b_color_texture = None
		self.b_shade_texture = None

		self.changes = set()

	def update_lines(self):
		"""map to lines
		"""
		if len(self.changes) == 0:
			return {'NOT_CHANGED'}

		template = "{} {} = {}"
		new_lines = []
		for line in self.lines:
			type, name, value = re.split(r'[= ]+', str(line).strip(), 2)
			if name in self.changes:
				value = self.map[name] # update
				line = template.format(type, name, value)

			new_lines.append(line)

		self.lines = new_lines
		self.changes.clear()

	def update_map(self):
		"""lines to map
		"""
		self.map.clear()
		for line in self.lines:
			type, name, value = re.split(r'[= ]+', str(line).strip(), 2)
			self.map[name] = value

	def update_value(self, name, value):
		if self.map[name] == value:
			return {'NOT_CHANGED'}

		self.map[name] = value
		self.changes.add(name)

	def read_shader_file(self, path):
		"""shader設定としてtextfileを読み込む
		"""
		with open(path, 'rt') as file:
			del self.lines[:]
			for line in file:
				self.lines.append(line.strip())

		self.update_map()

	def write_shader_file(self, path):
		"""shader設定としてtextfileを書き込む
		"""
		self.update_lines()

		with open(path, 'wt') as file:
			for line in self.lines:
				file.write(line)
				file.write('\n')

	def read(self, file):
		self.name = read_cstring(file)
		self.path = read_cstring(file)
		lines_count = read_int(file)
		del self.lines[:]
		for x in range(lines_count):
			line = read_cstring(file)
			self.lines.append(line)

		self.update_map()

	def write(self, file):
		self.update_lines()

		write_cstring(file, self.name)
		write_cstring(file, self.path)
		write_int(file, len(self.lines))
		for line in self.lines:
			write_cstring(file, line)

class Vertex(object):
	def __init__(self):
		self.co = None
		self.no = None
		self.uv = None
		self.skin_weights = []

	def __eq__(self, other):
		return self.co == other.co and self.no == other.no and self.uv == other.uv

	def __hash__(self):
		return hash((self.co, self.no, self.uv))

	def read(self, file):
		self.co = read_vector3(file)
		self.no = read_vector3(file)
		self.uv = read_vector2(file)

		skin_weights_count = read_int(file)
		del self.skin_weights[:]
		for i in range(skin_weights_count):
			skin_weight = unpack('if', file.read(8))
			self.skin_weights.append(skin_weight)

	def write(self, file):
		write_vector3(file, self.co)
		write_vector3(file, self.no)
		write_vector2(file, self.uv)

		write_int(file, len(self.skin_weights))
		for i, w in self.skin_weights:
			write_int(file, i)
			write_float(file, w)

class TSOSubMesh(object):
	def __init__(self):
		self.spec = None
		self.bone_indices = []
		self.vertices = []

	def read(self, file):
		self.spec = read_int(file)

		bone_indices_count = read_int(file)
		del self.bone_indices[:]
		for i in range(bone_indices_count):
			bone_idx = read_int(file)
			self.bone_indices.append(bone_idx)

		vertices_count = read_int(file)
		del self.vertices[:]
		for i in range(vertices_count):
			v = Vertex()
			v.read(file)
			self.vertices.append(v)

	def write(self, file):
		write_int(file, self.spec)

		write_int(file, len(self.bone_indices))
		for bone_idx in self.bone_indices:
			write_int(file, bone_idx)

		write_int(file, len(self.vertices))
		for v in self.vertices:
			v.write(file)

class TSOMesh(object):
	def __init__(self):
		self.name = None
		self.sub_meshes = []

	def read(self, file):
		self.name = read_cstring(file)
		self.m = read_matrix4(file)
		self.unknown1 = read_int(file)

		sub_meshes_count, = unpack('<i', file.read(4))
		del self.sub_meshes[:]
		for sub_mesh_idx in range(sub_meshes_count):
			sub_mesh = TSOSubMesh()
			sub_mesh.read(file)
			self.sub_meshes.append(sub_mesh)

	def write(self, file):
		write_cstring(file, self.name)
		m = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
		write_matrix4(file, m)
		unknown1 = 1
		write_int(file, unknown1)

		write_int(file, len(self.sub_meshes))
		for sub_mesh in self.sub_meshes:
			sub_mesh.write(file)

class TSOFile(object):
	def __init__(self):
		self.nodes	= []
		self.textures	= []
		self.scripts	= []
		self.sub_scripts	= []
		self.meshes	= []

	def load(self, source_file):
		with open(source_file, 'rb') as file:
			magic = file.read(4)
			if magic != b'TSO1':
				raise ValueError('File is not TSO')

			nodes_count = read_int(file)
			del self.nodes[:]
			for i in range(nodes_count):
				node = TSONode()
				node.read(file)
				self.nodes.append(node)

			matrices_count = read_int(file)
			for i in range(matrices_count):
				node = self.nodes[i]
				m = read_matrix4(file)
				node.transform = turned_nodes.turned_matrix4(m, node.name)

			textures_count = read_int(file)
			del self.textures[:]
			for i in range(textures_count):
				texture = TSOTexture()
				texture.read(file)
				self.textures.append(texture)

			scripts_count = read_int(file)
			del self.scripts[:]
			for i in range(scripts_count):
				script = TSOScript()
				script.read(file)
				self.scripts.append(script)

			sub_scripts_count = read_int(file)
			del self.sub_scripts[:]
			for i in range(sub_scripts_count):
				sub_script = TSOSubScript()
				sub_script.read(file)
				self.sub_scripts.append(sub_script)

			meshes_count = read_int(file)
			del self.meshes[:]
			for mesh_idx in range(meshes_count):
				mesh = TSOMesh()
				mesh.read(file)
				self.meshes.append(mesh)

	def save(self, dest_file):
		with open(dest_file, 'wb') as file:
			file.write(b'TSO1')

			write_int(file, len(self.nodes))
			for node in self.nodes:
				node.write(file)

			write_int(file, len(self.nodes))
			for node in self.nodes:
				m = turned_nodes.turned_matrix4(node.transform, node.name)
				write_matrix4(file, m)

			write_int(file, len(self.textures))
			for texture in self.textures:
				texture.write(file)

			write_int(file, len(self.scripts))
			for script in self.scripts:
				script.write(file)

			write_int(file, len(self.sub_scripts))
			for sub_script in self.sub_scripts:
				sub_script.write(file)

			write_int(file, len(self.meshes))
			for mesh in self.meshes:
				mesh.write(file)


if __name__ == "__main__":
	import os
	from time import time

	start_time = time()

	source_file = os.path.join(os.environ['HOME'], "resources/N0010BC1_A00.tso")
	tso = TSOFile()
	tso.load(source_file)

	end_time = time()
	print('tso load time:', end_time - start_time)

	start_time = time()

	dest_file = os.path.join(os.environ['HOME'], "resources/out.tso")
	tso.save(dest_file)

	end_time = time()
	print('tso save time:', end_time - start_time)
