#!/usr/bin/env python

"""TechArts3D tso file importer for blender 2.78
"""

import os
import bpy
from math import radians
from mathutils import Matrix, Vector
from io_scene_tso_tmo.io.tso import TSOFile
from io_scene_tso_tmo.utils.heap import Heap

world_scale = 0.25

def assign_world_scale_rotation(b_object):
	# object scale
	b_object.scale[0] = world_scale # x
	b_object.scale[1] = world_scale # y
	b_object.scale[2] = world_scale # z

	# object rotation
	b_object.rotation_mode = 'AXIS_ANGLE'
	b_object.rotation_axis_angle[0] = radians(+90) # angle
	b_object.rotation_axis_angle[1] = 1 # x-axis
	b_object.rotation_axis_angle[2] = 0 # y-axis
	b_object.rotation_axis_angle[3] = 0 # z-axis

def import_tso(tso, dirname):

	def detect_armature():
		found = None
		for ob in bpy.context.selected_objects:
			if ob.type == 'ARMATURE':
				found = ob
				break
		return found

	def import_armature():
		# objectがないと失敗するのでpoll
		if bpy.ops.object.mode_set.poll():
			bpy.ops.object.mode_set(mode="OBJECT")

		b_armature = bpy.data.armatures.new('Armature')
		b_armature.show_axes = True  # 座標軸
		b_object = bpy.data.objects.new(b_armature.name, b_armature)
		b_object.select = True
		b_object.show_x_ray = True  # 透視

		# object scale
		b_object.scale[0] = world_scale # x
		b_object.scale[1] = world_scale # y
		b_object.scale[2] = world_scale # z

		# object rotation
		b_object.rotation_mode = 'AXIS_ANGLE'
		b_object.rotation_axis_angle[0] = radians(+90) # angle
		b_object.rotation_axis_angle[1] = 1 # x-axis
		b_object.rotation_axis_angle[2] = 0 # y-axis
		b_object.rotation_axis_angle[3] = 0 # z-axis

		scene = bpy.context.scene
		scene.objects.link(b_object)
		scene.objects.active = b_object

		bpy.ops.object.mode_set(mode="EDIT")
		nodemap = {}
		for t_node in tso.nodes:
			b_bone = b_armature.edit_bones.new(t_node.name)
			b_armature.edit_bones.active = b_bone

			# directx行列からblender行列に変換
			# TODO: node側でやるべき
			m = Matrix(t_node.transform)
			m.transpose()
			t_node.b_transform = m

			# 親を代入
			# TODO: node側でやるべき
			if t_node.parent_name != '':
				t_node.parent = nodemap[t_node.parent_name]
				b_bone.parent = nodemap[t_node.parent_name].b_bone
				# b_bone.use_connect = True
			else:
				t_node.parent = None
				b_bone.parent = None

			b_bone.tail.y = 0.25
			b_bone.matrix = t_node.b_world_coordinate()

			# print("bone {} head:{} roll:{}".format(b_bone.name, b_bone.head, b_bone.roll))

			# b_bone.use_inherit_rotation = False

			# bpy: 親でscaleしているboneをrotateするとshearになってしまうのでscaleを継承しない設定にする
			b_bone.use_inherit_scale = False

			# b_bone.use_local_location = False
			# b_bone.use_relative_parent = False

			t_node.b_bone = b_bone
			nodemap[t_node.name] = t_node

		return b_object

	def import_mesh(t_mesh):
		v_heap = Heap()
		node_i_heap = Heap()
		spec_heap = Heap()

		faces = []
		uv_faces = []
		uv_specs = []
		material_indices = []
		weits = []
		
		# objectがないと失敗するのでpoll
		if bpy.ops.object.mode_set.poll():
			bpy.ops.object.mode_set(mode="OBJECT")

		for sub in t_mesh.sub_meshes:
			ccw = False
			va = None
			vb = None
			vc = None
			a = -1
			b = -1
			c = -1
			
			material_index = spec_heap.append(sub.spec)

			for v in sub.vertices:
				ccw = not ccw
				va, vb, vc = vb, vc, v
				a, b, c = b, c, v_heap.append(( v.co, v.no ))

				if b != c:
					# v is new vertex
					for sw in v.skin_weights:
						i, w = sw
						node_idx = sub.bone_indices[i]
						weits.append(( c, node_i_heap.append(node_idx), w ))
		
				if a == -1:
					continue

				if a == b or b == c or c == a:
					continue

				if ccw:
					faces.append(( a, b, c ))
					uv_faces.append(( va.uv, vb.uv, vc.uv ))
				else:
					faces.append(( a, c, b ))
					uv_faces.append(( va.uv, vc.uv, vb.uv ))

				uv_specs.append(sub.spec)
				material_indices.append(material_index)

		# print("len faces {}".format(len(faces)))

		b_mesh = bpy.data.meshes.new(t_mesh.name)
		b_object = bpy.data.objects.new(b_mesh.name, b_mesh)
		b_object.select = True

		# assign_world_scale_rotation(b_object)

		scene = bpy.context.scene
		scene.objects.link(b_object)
		scene.objects.active = b_object

		b_mesh.vertices.add(len(v_heap.ary))
		for i, ( co, no ) in enumerate(v_heap.ary):
			b_mesh.vertices[i].co = co
			b_mesh.vertices[i].normal = no

		b_mesh.polygons.add(len(faces))
		b_mesh.loops.add(len(faces)*3)
		for i, ( a, b, c ) in enumerate(faces):
			loop_start = i*3
			b_mesh.polygons[i].loop_start = loop_start
			b_mesh.polygons[i].loop_total = 3
			b_mesh.loops[loop_start + 0].vertex_index = a
			b_mesh.loops[loop_start + 1].vertex_index = b
			b_mesh.loops[loop_start + 2].vertex_index = c

		b_mesh.uv_textures.new()

		uv_tex_polys = b_mesh.uv_textures.active.data[:]
		# print("len uv_tex_polys {}".format(len(uv_tex_polys)))

		for i, spec in enumerate(uv_specs):
			sub = tso.sub_scripts[spec]
			uv_tex_polys[i].image = sub.b_color_texture.image

		uv_loops = b_mesh.uv_layers.active.data[:]
		# print("len uv_loops {}".format(len(uv_loops)))

		for i, ( a, b, c ) in enumerate(uv_faces):
			loop_start = i*3
			uv_loops[loop_start + 0].uv = a
			uv_loops[loop_start + 1].uv = b
			uv_loops[loop_start + 2].uv = c

		# create materials
		for spec in spec_heap.ary:
			sub = tso.sub_scripts[spec]
			b_mesh.materials.append(sub.b_material)

		for i, material_idx in enumerate(material_indices):
			b_mesh.polygons[i].use_smooth = True
			b_mesh.polygons[i].material_index = material_idx

		# create vertex_groups
		v_groups = []
		for node_idx in node_i_heap.ary:
			node = tso.nodes[node_idx]
			node.v_group = b_object.vertex_groups.new(node.name)
			v_groups.append(node.v_group)

		for (c, i, w) in weits:
			v_groups[i].add([c], w, 'REPLACE')

		b_mesh.validate()
		b_mesh.update()

		return b_object

	# .tso に埋め込まれた shader 'TAToonshade_050.cgfx' を書き出す
	# 実際には使われない
	for scr in tso.scripts:
		print("write scr name:{}".format(scr.name))
		scr_realpath = os.path.join(dirname, scr.name)
		with open(scr_realpath, 'wt', encoding='cp932') as file:
			for line in scr.lines:
				file.write(line)
				file.write("\n")

	# .tso に埋め込まれた shader config を書き出す
	for sub in tso.sub_scripts:
		print("write sub name:{} path:{}".format(sub.name, sub.path))
		sub_realpath = os.path.join(dirname, sub.name)
		with open(sub_realpath, 'wt', encoding='cp932') as file:
			for line in sub.lines:
				file.write(line)
				file.write("\n")

	# for image.save_render
	image_settings = bpy.context.scene.render.image_settings
	image_settings.file_format = 'PNG'

	# texture file を読み込んで b_texture を作る
	# 辞書を作る {name: b_texture}
	b_texmap = {}
	for tex in tso.textures:
		print("tex name:{} path:{}".format(tex.name, tex.path))
		path = tex.path.strip('"')
		basename, extname = os.path.splitext(path)
		filename = basename + '.png'
		tex_realpath = os.path.join(dirname, filename)

		b_image = bpy.data.images.new(filename, tex.width, tex.height, alpha=True)
		b_image.use_fake_user = True
		b_image.pixels = tex.data_pixels()

		# save image as .png
		b_image.save_render(tex_realpath)

		# reload
		# b_image = bpy.data.images.load(tex_realpath)
		# b_image.name = filename
		b_image.filepath = tex_realpath
		b_image.source = 'FILE'

		b_tex = bpy.data.textures.new(tex.name, 'IMAGE')
		b_tex.use_fake_user = True
		b_tex.image = b_image

		b_texmap[tex.name] = b_tex

	# b_material b_texture_slot を作る
	for sub in tso.sub_scripts:
		# print("sub name:{} path:{}".format(sub.name, sub.path))
		sub_realpath = os.path.join(dirname, sub.name)
		b_mat = bpy.data.materials.new(sub.name)

		# diffuse
		b_mat.diffuse_color = (1.0, 1.0, 1.0)
		b_mat.diffuse_intensity = 0.8

		# ambient
		b_mat.ambient = 0.6

		# emission
		b_mat.emit = 0.0

		# specular
		b_mat.specular_color = (0.0, 0.0, 0.0)
		b_mat.specular_hardness = 5.0

		# alpha
		b_mat.use_transparency = True
		b_mat.alpha = 0.0
		b_mat.specular_alpha = 0.0

		sub.b_material = b_mat
		sub.b_color_texture = b_texmap[sub.map['ColorTex']]
		sub.b_shade_texture = b_texmap[sub.map['ShadeTex']]

		b_texslot = b_mat.texture_slots.add()
		b_texslot.texture = sub.b_color_texture
		b_texslot.use = True
		b_texslot.texture_coords = 'UV'

		# diffuse and alpha
		b_texslot.use_map_color_diffuse = True
		b_texslot.use_map_alpha = True

	def create_armature_modifier(b_mesh_object, b_armature_object):
		if b_armature_object is None:
			return
		armature_name = b_armature_object.name
		b_mod = b_mesh_object.modifiers.new(armature_name, 'ARMATURE')
		b_mod.object = b_armature_object

	# TODO: armatureの扱いをuiで選択できるように

	# 既存のarmatureを使う場合
	b_armature_object = detect_armature()

	if b_armature_object is None:
		# tso.nodesをimportしてarmatureを作成する場合
		b_armature_object = import_armature()

	b_object = bpy.data.objects.new(os.path.basename(dirname), None)
	b_object.select = True

	assign_world_scale_rotation(b_object)

	scene = bpy.context.scene
	scene.objects.link(b_object)
	scene.objects.active = b_object

	for t_mesh in reversed(tso.meshes):
		b_mesh_object = import_mesh(t_mesh)
		b_mesh_object.parent = b_object
		create_armature_modifier(b_mesh_object, b_armature_object)

def import_tsofile(source_file):
	dirname, extname = os.path.splitext(source_file)
	print("os.makedirs path:{}".format(dirname))
	os.makedirs(dirname, 0o755, True)

	tso = TSOFile()
	tso.load(source_file)

	import_tso(tso, dirname)

if __name__ == "__main__":
	from time import time

	start_time = time()
	source_file = os.path.join(os.environ['HOME'], "resources/mod1.tso")
	# source_file = os.path.join(os.environ['HOME'], "resources/N0010BC1_A00.tso")
	import_tsofile(source_file)

	end_time = time()
	print('tso import time:', end_time - start_time)
