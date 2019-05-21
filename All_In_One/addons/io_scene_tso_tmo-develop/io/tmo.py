#!/usr/bin/env python

"""TechArts3D tmo format
"""

from struct import pack, unpack
from mathutils import Matrix, Vector
from io_scene_tso_tmo import turned_nodes

def read_cstring(file):
	byt = b''
	while True:
		c = file.read(1)
		if c == b'\x00':
			break
		byt += c
	str = byt.decode('cp932')
	return str

def read_int(file):
	return unpack('<i', file.read(4))[0]

def read_matrix4(file):
	return [ unpack('<4f', file.read(16)) for i in range(4) ]

def read_vector3(file):
	return unpack('<3f', file.read(12))

def read_vector2(file):
	return unpack('<2f', file.read(8))

class TMONode(object):
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
		# print("tmo node name:{} parent_name:{}".format(self.name, self.parent_name))

	def b_world_coordinate(self):
		node = self
		m = Matrix.Identity(4)
		while node:
			m = node.b_transform * m
			node = node.parent

		return m

class TMOFile(object):
	def __init__(self):
		self.nodes = []

	def load(self, source_file):
		with open(source_file, 'rb') as file:
			magic =  file.read(4)
			if magic != b'TMO1':
				raise ValueError('File is not TMO')

			header = file.read(8)
			opt0 = read_int(file)
			opt1 = read_int(file)

			nodes_count = read_int(file)
			del self.nodes[:]
			for i in range(nodes_count):
				node = TMONode()
				node.read(file)
				self.nodes.append(node)

			drop = read_int(file)
			# motionでなくposeとして扱う
			matrices_count = read_int(file)
			for i in range(matrices_count):
				node = self.nodes[i]
				m = read_matrix4(file)
				node.transform = turned_nodes.turned_matrix4(m, node.name)

			# footer = file.read(4)


if __name__ == "__main__":
	import os
	from time import time

	start_time = time()

	source_file = os.path.join(os.environ['HOME'], "resources/5.tmo")
	tmo = TMOFile()
	tmo.load(source_file)

	end_time = time()
	print('tmo load time:', end_time - start_time)
