import os
import bpy
import shutil
import base64
from . import export_material
from abc import ABC, abstractmethod


class MeshConverter(ABC):
	def __init__(self):
		self.meshes = dict()
		self.materials = dict()

		self.exclude_materials = None

		super(MeshConverter, self).__init__()


	@abstractmethod
	def _add_material(self, material):
		pass

	def _finish_materials(self):
		pass

	@abstractmethod
	def _add_vertex(self, vertex, uv, normal):
		pass

	@abstractmethod
	def _add_triangle(self, vertices, material):
		pass

	def _finish(self):
		pass


	def add_mesh(self, mesh):
		self.meshes[mesh.name] = mesh

		for material in mesh.materials:
			if material is None:
				continue
			self.materials[material.name] = material


	def execute(self):
		current_vertex_id = 0

		for material in self.materials.values():
			if self.exclude_materials is not None:
				if material.name in exclude_materials:
					continue
			self._add_material(material)

		self._finish_materials()

		for mesh in self.meshes.values():
			if mesh.towerengine.vertices_only:
				for vertex in mesh.vertices:
					self.__add_vertex(vertex, (0.0, 0.0), vertex.normal)
					current_vertex_id += 1
			else:
				face_vertex_id = dict()
				vertex_id = dict()
				vertex_uv = dict()
				vertex_normal = dict()
				mesh.update(False, True)

				if mesh.tessface_uv_textures.active is not None:
					uv_layer = mesh.tessface_uv_textures.active.data
				else:
					uv_layer = None

				for face in mesh.tessfaces:
					face_vertex_id[face] = dict()

					for i in range(len(face.vertices)):
						vertex = face.vertices[i]
						vertex_found = False

						if vertex not in vertex_id:
							vertex_id[vertex] = list()
							vertex_uv[vertex] = list()
							vertex_normal[vertex] = list()

						if face.use_smooth:
							normal = mesh.vertices[vertex].normal
						else:
							normal = face.normal

						if uv_layer is not None:
							uv = uv_layer[face.index].uv[i]
						else:
							uv = (0.0, 0.0)

						for j in range(len(vertex_id[vertex])):
							if vertex_uv[vertex][j][0] == uv[0] and vertex_uv[vertex][j][1] == uv[1] and \
											vertex_normal[vertex][j] == normal:  # might be wrong
								face_vertex_id[face][i] = vertex_id[vertex][j]
								vertex_found = True
								break
						if vertex_found:
							continue

						vertex_id[vertex].append(current_vertex_id)
						vertex_uv[vertex].append(uv)
						vertex_normal[vertex].append(normal)
						face_vertex_id[face][i] = current_vertex_id
						current_vertex_id += 1
						vertex = mesh.vertices[vertex]

						self._add_vertex(vertex, uv, normal)

				for face in mesh.tessfaces:
					material_name = None
					if len(mesh.materials) != 0:
						if mesh.materials[face.material_index] is not None:
							material_name = mesh.materials[face.material_index].name

					if len(face.vertices) >= 3:
						self._add_triangle([face_vertex_id[face][0], face_vertex_id[face][1], face_vertex_id[face][2]], material_name)

					if len(face.vertices) >= 4:
						self._add_triangle([face_vertex_id[face][2], face_vertex_id[face][3], face_vertex_id[face][0]], material_name)

		self._finish()