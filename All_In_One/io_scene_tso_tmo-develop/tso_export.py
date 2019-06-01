#!/usr/bin/env python

"""TechArts3D tso file exporter for blender 2.78
"""

from itertools import groupby
import os
import shutil
import bpy
from io_scene_tso_tmo.io.tso import TSOFile, TSONode, TSOMesh, TSOSubMesh, Vertex, TSOSubScript, TSOTexture
from io_scene_tso_tmo.utils.heap import Heap
from io_scene_tso_tmo.utils.partition import Partition
from io_scene_tso_tmo.utils.tristrip import stripify

def export_tso(tso, sample, dirname):
	"""tsoにbpy sceneを書き出す

	tso: 書き出しtso
	sample: 参照tso
	"""
	tso.scripts = sample.scripts

	sample_sub = sample.sub_scripts[0]

	def detect_armature():
		found = None
		for ob in bpy.context.selected_objects:
			if ob.type == 'ARMATURE':
				found = ob
				break
		return found

	def export_armature(b_armature, b_object):
		t_nodes = []

		# map name to t_node
		# t_node.path を作るために必要
		t_nodemap = {}

		for b_bone in b_armature.bones:
			print("  b_bone name:{}".format(b_bone.name))

			t_node = TSONode()
			t_node.name = b_bone.name

			b_parent = b_bone.parent

			if b_parent is None:
				t_node.b_transform = b_bone.matrix_local
				t_node.path = '|' + b_bone.name
			else:
				t_node.b_transform = b_parent.matrix_local.inverted() * b_bone.matrix_local
				t_node.path = t_nodemap[b_parent.name].path + '|' + b_bone.name

			print("  t_node path:{}".format(t_node.path))

			t_nodes.append(t_node)
			t_nodemap[t_node.name] = t_node

		for t_node in t_nodes:
			# blender行列からdirectx行列に変換
			m = t_node.b_transform
			m.transpose()
			t_node.transform = m

		tso.nodes = t_nodes

	b_armature_object = detect_armature()

	if b_armature_object is None:
		tso.nodes = sample.nodes
	else:
		b_armature = b_armature_object.data
		export_armature(b_armature, b_armature_object)

	def add_texture(tex):
		print("  tex name:{}".format(tex.name))
		name = tex.name

		for t_tex in tso.textures:
			if t_tex.name == name:
				return {'EXISTS'}

		if tex.type != 'IMAGE':
			return {'FAILED'}

		t_tex = TSOTexture()
		t_tex.name = tex.name
		t_tex.path = '"' + tex.image.name + '"'
		t_tex.width, t_tex.height = tex.image.size
		t_tex.depth = tex.image.channels
		t_tex.pixels_data(tex.image.pixels)

		tso.textures.append(t_tex)

	def add_material(mat):
		print("  mat name:{}".format(mat.name))
		name = mat.name

		for i, sub in enumerate(tso.sub_scripts):
			if sub.name == name:
				return i

		# shader configを得る
		shader_path = os.path.join(dirname, name)
		# なければsample configを書き込む
		if not os.path.exists(shader_path):
			sample_sub.write_shader_file(shader_path)

		# idx of tso.sub_scripts
		spec = len(tso.sub_scripts)

		t_sub = TSOSubScript()
		t_sub.name = name
		# t_sub.path = path
		# set sub.lines and sub.map
		t_sub.read_shader_file(shader_path)

		tso.sub_scripts.append(t_sub)

		name = t_sub.map['ColorTex']
		i = bpy.data.textures.find(name)
		if i != -1:
			tex = bpy.data.textures[i]
			add_texture(tex)

		name = t_sub.map['ShadeTex']
		i = bpy.data.textures.find(name)
		if i != -1:
			tex = bpy.data.textures[i]
			add_texture(tex)

		return spec

	def triangulate(me):
		import bmesh
		bm = bmesh.new()
		bm.from_mesh(me)
		bmesh.ops.triangulate(bm, faces=bm.faces)
		bm.to_mesh(me)
		bm.free()

	def export_mesh(me, b_object):
		print("me name:{} #polygons:{} #vertices:{}".format(me.name, len(me.polygons), len(me.vertices)))

		for poly in me.polygons:
			if poly.loop_total != 3:
				return {'FAILED'} # raise

		# map ob.vertex_groups to tso.nodes
		nodemap = {}
		for i, node in enumerate(tso.nodes):
			nodemap[node.name] = i

		for v_group in ob.vertex_groups:
			if v_group.name not in nodemap:
				return {'FAILED'} # raise

		group_node_indices = []
		for v_group in ob.vertex_groups:
			group_node_indices.append(nodemap[v_group.name])

		uv_loops = me.uv_layers.active.data[:]

		t_mesh = TSOMesh()
		t_mesh.name = me.name

		tso.meshes.append(t_mesh)

		# このmeshで使ってるmat
		mat_idx_heap = Heap()
		# map mat_idx to idx of tso.sub_scripts
		specmap = {}

		for poly in me.polygons:
			mat_idx_heap.append(poly.material_index)

		for mat_idx in mat_idx_heap.ary:
			mat = me.materials[mat_idx]
			specmap[mat_idx] = add_material(mat)

		# sub_scripts (= materials) とtextures は完了

		# sub meshを作る

		# face (= poly) をspec (= material_index) でわけわけ
		func_mat_idx = lambda poly: poly.material_index
		sorted_polygons = sorted(me.polygons, key=func_mat_idx)
		for mat_idx, polygons in groupby(sorted_polygons, key=func_mat_idx):
			mat = me.materials[mat_idx]
			print("  mat name:{}".format(mat.name))

			"""
			# v idx をあつめる
			v_indices = set()
			for poly in polygons:
				loops = [me.loops[poly.loop_start + i] for i in range(3)]
				v_indices |= {loop.vertex_index for loop in loops}

			vertices = [me.vertices[i] for i in v_indices]

			# 使ってるv group idx をあつめる
			v_groups = set()
			for v in vertices:
				v_groups |= {g.group for g in v.groups}

			if (len(v_groups) > 16):
				print("  len v group:{}".format(len(v_groups)))
			"""

			poly_combs = []
			for i in range(len(me.polygons)):
				poly_combs.append(None)

			# 1. combinationを計算

			# create bone combination set
			comb_set = set()
			for poly in polygons:
				# create bone combination
				loop_start = poly.loop_start
				v_groups = []
				for i in range(3):
					loop = me.loops[loop_start + i]
					v = me.vertices[loop.vertex_index]
					for g in v.groups:
						v_groups.append(g.group)

				# sort and uniq
				comb = tuple(sorted(set(v_groups)))
				comb_set.add(comb)

				# map poly idx to comb
				#   poly.index: idx of me.polygons
				poly_combs[poly.index] = comb

			# NOTE: polygons have been terminated

			partition = Partition(comb_set, len(ob.vertex_groups))
			partition.run()

			print("len palettes:{}".format(len(partition.palettes)))
			print("palattes:{}".format(partition.palettes))

			palette_poly_indices = []
			for i in range(len(partition.palettes)):
				palette_poly_indices.append([])

			# face (= poly) をsub_mesh (= palette) でわけわけ
			for poly_idx, comb in enumerate(poly_combs):
				if comb is None:
					continue
				palette_idx = partition.comb_palette_map[comb]
				palette_poly_indices[palette_idx].append(poly_idx)

			for palette_idx, palette in enumerate(partition.palettes):
				sub_mesh = TSOSubMesh()
				a_heap = Heap()

				# mat_idx: idx of me.materials
				sub_mesh.spec = specmap[mat_idx]

				# element of palette: idx of ob.vertex_groups
				group_indices = {}
				for i, group in enumerate(palette):
					group_indices[group] = i

					sub_mesh.bone_indices.append(group_node_indices[group])

				triangles = []
				for poly_idx in palette_poly_indices[palette_idx]:
					poly = me.polygons[poly_idx]
					loop_start = poly.loop_start
					triangle = []
					for i in range(3):
						loop = me.loops[loop_start + i]
						v = me.vertices[loop.vertex_index]
						a = Vertex()
						co = v.co; a.co = (co.x, co.y, co.z)
						no = v.normal; a.no = (no.x, no.y, no.z)
						uv = uv_loops[loop_start + i].uv; a.uv = (uv.x, uv.y)
						for g in v.groups:
							a.skin_weights.append((group_indices[g.group], g.weight))

						triangle.append(a_heap.append(a))

					triangles.append(triangle)
					# tuple_triangle = tuple(triangle)
					# triangles.append(tuple_triangle)

				strip, = stripify(triangles, stitchstrips=True)
				ary = a_heap.ary
				sub_mesh.vertices = [ary[i] for i in strip]
				print("  sub spec:{} #bone_indices:{} #vertices:{}".format(sub_mesh.spec, len(sub_mesh.bone_indices), len(sub_mesh.vertices)))

				t_mesh.sub_meshes.append(sub_mesh)

	# 選択中のmeshを得る
	for ob in bpy.context.selected_objects:
		if ob.type != 'MESH':
			continue

		me = ob.data
		triangulate(me)
		export_mesh(me, ob)


def export_tsofile(dest_file, sample_file):
	"""tsoにbpy sceneを書き出す

	dest_file: 書き出しtso filename 新規 or 更新
	sample_file: 参照tso filename

	dest_fileとsample_fileは同じでも良い
	"""
	dirname, extname = os.path.splitext(dest_file)
	print("os.makedirs path:{}".format(dirname))
	os.makedirs(dirname, 0o755, True)

	tso = TSOFile()

	sample = TSOFile()
	sample.load(sample_file)

	export_tso(tso, sample, dirname)

	tso.save(dest_file)

if __name__ == "__main__":
	from time import time

	start_time = time()
	dest_file = "blend1.tso"
	sample_file = os.path.join(os.environ['HOME'], "resources/mod1.tso")

	export_tsofile(dest_file, sample_file)
	end_time = time()
	print('tso export time:', end_time - start_time)
