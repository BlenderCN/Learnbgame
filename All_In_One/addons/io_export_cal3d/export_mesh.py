import bpy
import mathutils

from . import mesh_classes
from . import armature_classes
from .mesh_classes import *
from .armature_classes import *


def create_cal3d_materials(cal3d_dirname, imagepath_prefix, xml_version):
	cal3d_materials = []
	for material in bpy.data.materials:
		material_index = len(cal3d_materials)
		material_name = material.name
		maps_filenames = []
		for texture_slot in material.texture_slots:
			if texture_slot:
				if texture_slot.texture:
					if texture_slot.texture.type == "IMAGE":
						imagename = bpy.path.basename(texture_slot.texture.image.filepath)
						filepath = os.path.abspath(bpy.path.abspath(texture_slot.texture.image.filepath))
						texturePath = os.path.join(cal3d_dirname, imagepath_prefix + imagename)
						if not os.path.exists(os.path.dirname(texturePath)):
							os.mkdir(os.path.dirname(texturePath))
						if os.path.exists(filepath):
							import shutil
							try:
								shutil.copy(filepath, texturePath)
								print("Copied texture to " + texturePath)
							except Exception as e:
								print("Error copying texture " + str(e))
						maps_filenames.append(imagepath_prefix + imagename)
						#maps_filenames.append(texture_slot.texture.image.filepath[2:]) #remove the double slash
		if len(maps_filenames) > 0:
			cal3d_material = Material(material_name, material_index, xml_version)
			cal3d_material.maps_filenames = maps_filenames
			cal3d_materials.append(cal3d_material)
	return cal3d_materials


def get_vertex_influences(vertex, mesh_obj, cal3d_skeleton, use_groups, use_envelopes, armature_obj):
	if not cal3d_skeleton:
		return []

	influences = []
	
	if use_groups:
		for group in vertex.groups:
			group_index = group.group
			group_name = mesh_obj.vertex_groups[group_index].name
			weight = group.weight
			if weight > 0.0001:
				for bone in cal3d_skeleton.bones:
					if (bone.name == group_name):
						influence = Influence(bone.index, weight)
						influences.append(influence)
						break

	# XXX BROKEN
	if False and use_envelopes and not (len(influences) > 0):
		for bone in armature_obj.data.bones:
			weight = bone.evaluate_envelope(armature_obj.matrix_world.copy().inverted() * (mesh_obj.matrix_world * vertex.co))
			if weight > 0:
				for cal3d_bone in cal3d_skeleton.bones:
					if bone.name == cal3d_bone.name:
						influence = Influence(cal3d_bone.index, weight)
						influences.append(influence)
						break

	return influences


def create_cal3d_mesh(scene, mesh_obj,
                      cal3d_skeleton,
                      cal3d_materials,
                      base_rotation_orig,
                      base_translation_orig,
                      base_scale,
                      xml_version,
					  use_groups, use_envelopes, armature_obj):

	mesh_matrix = mesh_obj.matrix_world.copy()

	mesh_data = mesh_obj.to_mesh(scene, False, "PREVIEW")
	mesh_data.transform(mesh_matrix)

	base_translation = base_translation_orig.copy()
	base_rotation = base_rotation_orig.copy()

	(mesh_translation, mesh_quat, mesh_scale) = mesh_matrix.decompose()
	mesh_rotation = mesh_quat.to_matrix()

	total_rotation = base_rotation.copy()
	total_translation = base_translation.copy()

	cal3d_mesh = Mesh(mesh_obj.name, xml_version)

	# currently 1 material per mesh

	blender_material = None
	if len(mesh_data.materials) > 0:
		blender_material = mesh_data.materials[0]
	
	cal3d_material_index = -1
	for cal3d_material in cal3d_materials:
		if (blender_material != None) and (cal3d_material.name == blender_material.name):
			cal3d_material_index = cal3d_material.index

	cal3d_submesh = SubMesh(cal3d_mesh, len(cal3d_mesh.submeshes),
	                        cal3d_material_index)
	cal3d_mesh.submeshes.append(cal3d_submesh)

	duplicate_index = len(mesh_data.vertices)

	for polygon in mesh_data.polygons:
		cal3d_vertex1 = None
		cal3d_vertex2 = None
		cal3d_vertex3 = None
		cal3d_vertex4 = None

		for loop_index, vertex_index in enumerate(polygon.vertices):
			duplicate = False
			cal3d_vertex = None
			uvs = []

			for uv_layer in mesh_data.uv_layers:
				uvs.append(uv_layer.data[polygon.loop_indices[loop_index]].uv)
					
			for uv in uvs:
				uv[1] = 1.0 - uv[1]
			
			for cal3d_vertex_iter in cal3d_submesh.vertices:
				if cal3d_vertex_iter.index == vertex_index:
					duplicate = True
					if len(cal3d_vertex_iter.maps) != len(uvs):
						break
					
					uv_matches = True
					for i in range(len(uvs)):
						if cal3d_vertex_iter.maps[i].u != uvs[i][0]:
							uv_matches = False
							break

						if cal3d_vertex_iter.maps[i].v != uvs[i][1]:
							uv_matches = False
							break
					
					if uv_matches:
						cal3d_vertex = cal3d_vertex_iter

					break

			if not cal3d_vertex:
				vertex = mesh_data.vertices[vertex_index]

				normal = vertex.normal.copy()
				normal *= base_scale
				normal.rotate(total_rotation)
				normal.normalize()

				coord = vertex.co.copy()
				coord = coord + total_translation
				coord *= base_scale
				coord.rotate(total_rotation)

				if duplicate:
					cal3d_vertex = Vertex(cal3d_submesh, duplicate_index,
					                      coord, normal)
					duplicate_index += 1

				else:
					cal3d_vertex = Vertex(cal3d_submesh, vertex_index,
					                      coord, normal)

										  
				cal3d_vertex.influences = get_vertex_influences(vertex,
						                                        mesh_obj,
				                                                cal3d_skeleton,
																use_groups, use_envelopes, armature_obj)
				for uv in uvs:
					cal3d_vertex.maps.append(Map(uv[0], uv[1]))

				cal3d_submesh.vertices.append(cal3d_vertex)

			if not cal3d_vertex1:
				cal3d_vertex1 = cal3d_vertex
			elif not cal3d_vertex2:
				cal3d_vertex2 = cal3d_vertex
			elif not cal3d_vertex3:
				cal3d_vertex3 = cal3d_vertex
			elif not cal3d_vertex4:
				cal3d_vertex4 = cal3d_vertex

		cal3d_face = Face(cal3d_submesh, cal3d_vertex1,
		                  cal3d_vertex2, cal3d_vertex3,
		                  cal3d_vertex4)
		cal3d_submesh.faces.append(cal3d_face)

	bpy.data.meshes.remove(mesh_data)

	return cal3d_mesh
