
import os
import bpy
import shutil
import base64
from xml.dom.minidom import Document
from . import export_material

class ExportMesh:
	def __init__(self):
		self.meshes = dict()
		self.materials = dict()
	
	def add_mesh(self, mesh):
		self.meshes[mesh.name] = mesh
		
		for material in mesh.materials:
			if material is None:
				continue
			self.materials[material.name] = material

	@staticmethod
	def __append_vertex(string_list, vertex, uv, normal):
		string_list.append("v ")
		string_list.append(str(vertex.co.x))
		string_list.append(" ")
		string_list.append(str(vertex.co.z))
		string_list.append(" ")
		string_list.append(str(-vertex.co.y))
		string_list.append(" ")
		string_list.append(str(uv[0]))
		string_list.append(" ")
		string_list.append(str(uv[1]))
		string_list.append(" ")
		string_list.append(str(normal.x))
		string_list.append(" ")
		string_list.append(str(normal.z))
		string_list.append(" ")
		string_list.append(str(-normal.y))
		string_list.append("\n")

		
	def save(self, filepath, pack_textures, exclude_materials = None):
		doc = Document()
		root = doc.createElement("tmesh")
		root.setAttribute("version", "0.4")
		doc.appendChild(root)
		
		path = os.path.dirname(filepath)

		current_vertex_id = 0
		
		data_str_list = []
		
		for material in self.materials.values():
			if exclude_materials is not None:
				if material.name in exclude_materials:
					continue
			node = export_material.create_node(doc, material, path, os.path.basename(filepath) + "_tex", pack_textures)
			root.appendChild(node)

		for mesh in self.meshes.values():
			if mesh.towerengine.vertices_only:
				for vertex in mesh.vertices:
					self.__append_vertex(data_str_list, vertex, (0.0, 0.0), vertex.normal)
					current_vertex_id += 1
			else:
				face_vertex_id = dict()
				vertex_id = dict()
				#vertex_nodes = dict()
				vertex_uv = dict()
				vertex_normal = dict()
				mesh.update(False, True)

				if mesh.tessface_uv_textures.active is not None:
					uv_layer = mesh.tessface_uv_textures.active.data
				else:
					uv_layer = None


				for face in mesh.tessfaces: # Create Vertex Nodes from Face Vertices
						face_vertex_id[face] = dict()

						for i in range(len(face.vertices)): # All Vertices of Face
							vertex = face.vertices[i]
							vertex_found = False

							if vertex not in vertex_id:
								vertex_id[vertex] = list()
								#vertex_nodes[vertex] = list()
								vertex_uv[vertex] = list()
								vertex_normal[vertex] = list()

							if face.use_smooth:
								normal = mesh.vertices[vertex].normal
							else:
								normal = face.normal

							if uv_layer is not None:
								uv = uv_layer[face.index].uv[i]
							else:
								uv = [0.0, 0.0]

							for j in range(len(vertex_id[vertex])):
								if vertex_uv[vertex][j][0] == uv[0] and vertex_uv[vertex][j][1] == uv[1] and vertex_normal[vertex][j] == normal: # might be wrong
									face_vertex_id[face][i] = vertex_id[vertex][j]
									vertex_found = True
									break
							if vertex_found:
								continue


							vertex_id[vertex].append(current_vertex_id)
							#vertex_nodes[vertex].append(node)
							vertex_uv[vertex].append(uv)
							vertex_normal[vertex].append(normal)
							face_vertex_id[face][i] = current_vertex_id
							current_vertex_id += 1
							vertex = mesh.vertices[vertex]

							self.__append_vertex(data_str_list, vertex, uv, normal)

							'''
							node = doc.createElement("vertex")
							node.setAttribute("id", str(current_vertex_id))
							node.setAttribute("x", str(vertex.co.x))
							node.setAttribute("y", str(vertex.co.z))
							node.setAttribute("z", str(-vertex.co.y))
							node.setAttribute("u", str(uv[0]))
							node.setAttribute("v", str(uv[1]))
							node.setAttribute("nx", str(normal.x))
							node.setAttribute("ny", str(normal.z))
							node.setAttribute("nz", str(-normal.y))
							root.appendChild(node)
							'''



				for face in mesh.tessfaces:
					if len(face.vertices) >= 3:
						data_str_list.append("t ")

						for i in range(3):
							data_str_list.append(str(face_vertex_id[face][i]))
							data_str_list.append(" ")

						if len(mesh.materials) != 0:
							if mesh.materials[face.material_index] is not None:
								data_str_list.append(mesh.materials[face.material_index].name)

						data_str_list.append("\n")


						'''
						node = doc.createElement("triangle")
						node.setAttribute("mat", "$NONE")

						if len(mesh.materials) != 0:
							if mesh.materials[face.material_index] != None:
								node.setAttribute("mat", mesh.materials[face.material_index].name)

						for i in range(3):
							node2 = doc.createElement("vertex");	node2.setAttribute("id", str(face_vertex_id[face][i]));	node.appendChild(node2)

						root.appendChild(node)
						'''

					if len(face.vertices) >= 4:
						data_str_list.append("t ")

						for i in [2, 3, 0]:
							data_str_list.append(str(face_vertex_id[face][i]))
							data_str_list.append(" ")

						if len(mesh.materials) != 0:
							if mesh.materials[face.material_index] is not None:
								data_str_list.append(mesh.materials[face.material_index].name)

						data_str_list.append("\n")

						'''
						node = doc.createElement("triangle")
						node.setAttribute("mat", "$NONE")

						if len(mesh.materials) != 0:
							if mesh.materials[face.material_index] != None:
								node.setAttribute("mat", mesh.materials[face.material_index].name)

						for i in [2, 3, 0]:
							node2 = doc.createElement("vertex");	node2.setAttribute("id", str(face_vertex_id[face][i]));	node.appendChild(node2)

						root.appendChild(node)
						'''

			node = doc.createElement("mesh_data")
			node.appendChild(doc.createTextNode(''.join(data_str_list)))
			root.appendChild(node)

		f = open(filepath, 'w')
		f.write(doc.toprettyxml(indent="  "))
		f.close()


		
		
