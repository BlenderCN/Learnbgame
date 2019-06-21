#!/usr/bin/env python

"""TechArts3D tmo file importer for blender 2.78
"""

import os
import bpy
from math import radians
from mathutils import Matrix, Vector
from io_scene_tso_tmo.io.tmo import TMOFile

def matrix_scale(v):
	m = Matrix.Identity(4)
	m[0][0] = v[0] # x
	m[1][1] = v[1] # y
	m[2][2] = v[2] # z
	return m

def import_tmo(tmo, sample):

	def import_pose():
		b_object = bpy.data.objects['Armature']
		b_object.select = True

		scene = bpy.context.scene
		# scene.objects.link(b_object)
		scene.objects.active = b_object

		# 辞書を作る
		sample_nodemap = {}
		for node in sample.nodes:
			sample_nodemap[node.name] = node

		nodemap = {}
		for node in tmo.nodes:
			nodemap[node.name] = node

		# directx行列からblender行列に変換
		# TODO: node側でやるべき
		for node in sample.nodes:
			m = Matrix(node.transform)
			m.transpose()
			node.b_transform = m

		for node in tmo.nodes:
			m = Matrix(node.transform)
			m.transpose()
			node.b_transform = m

		# 親を代入
		# TODO: node側でやるべき
		for node in tmo.nodes:
			if node.parent_name != '':
				node.parent = nodemap[node.parent_name]
			else:
				node.parent = None

		bpy.ops.object.mode_set(mode="POSE")

		b_pose = b_object.pose
		for p_bone in b_pose.bones:
			sample_node = sample_nodemap[p_bone.name]
			if not sample_node:
				continue

			node = nodemap[p_bone.name]
			if not node:
				continue

			# bpy: 親でscaleしているboneをrotateするとshearになってしまうのでscaleを継承しない設定にする
			# in tso_import: bone.use_inherit_scale = False

			# ここで親scaleを反映させる

			# 親scaleを得る
			if node.parent:
				parent_scale = matrix_scale(node.parent.b_world_coordinate().to_scale())
			else:
				parent_scale = Matrix.Identity(4)

			p_bone.matrix_basis = sample_node.b_transform.inverted() * node.b_transform * parent_scale

	import_pose()

def import_tmofile(source_file, sample_file):
	tmo = TMOFile()
	tmo.load(source_file)

	sample = TMOFile()
	sample.load(sample_file)

	import_tmo(tmo, sample)

if __name__ == "__main__":
	from time import time

	start_time = time()
	# source_file = os.path.join(os.environ['HOME'], "resources/base-tpo1.tmo")
	source_file = os.path.join(os.environ['HOME'], "resources/5.tmo")
	sample_file = os.path.join(os.environ['HOME'], "resources/base-defo.tmo")
	import_tmofile(source_file, sample_file)

	end_time = time()
	print('tmo import time:', end_time - start_time)

