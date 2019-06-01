
import os
import shutil
import base64
import bpy.path
from bpy.props import BoolProperty
from bpy_extras.io_utils import ExportHelper
from xml.dom.minidom import Document
from .export_mesh import ExportMesh
from mathutils import Vector
from . import export_material

from . import utils


class TowerEngineSceneExporter(bpy.types.Operator, ExportHelper):
	bl_idname		   = "export_tes.tes"
	bl_label			= "Export"
	bl_options		  = {'PRESET'}
	
	filename_ext = ".tes"
	

	limit_export_prop = BoolProperty(name = "Limit to selection",
									description = "Export selection only",
									default = True)
	
	include_mat_prop = BoolProperty(name = "Include Materials in Scene file",
									description = "Keep materials globally in Scene file instead in every Mesh file that uses a specific material.",
									default = True)
	
	pack_tex_prop = BoolProperty(name = "Pack Textures in Files",
									description = "Include Texture Images directly into .tem/.tes files instead of copying and linking the URL",
									default = False)
	
	save_cubemaps_prop = BoolProperty(name = "Save Cube Maps",
									description = "Include Cube Maps of the current scene",
									default = True)
	
	
	
	
	def execute(self, context):
		self.directory = os.path.dirname(self.filepath)
		self.file_basename = os.path.basename(self.filepath)
		
		self.__collect_data()
		self.__save()
		return {'FINISHED'}




	def __collect_data(self):
		# collect objects
		self.objects = dict()
		
		for obj in bpy.data.objects:
			if(self.limit_export_prop == True and obj.select == False):
				continue
			
			self.objects[obj.name] = obj;
			
		
		# collect meshes
		self.meshes = dict()		
		for obj in self.objects.values():
			if obj.type == "MESH" and not obj.towerengine.disable_mesh:
				mesh = obj.data
				self.meshes[mesh.name] = mesh
			
		
		# collect materials	
		if self.include_mat_prop:
			self.materials = dict()
			self.mesh_exclude_materials = set()
			for mesh in self.meshes.values():
				for material in mesh.materials:
					if material == None:
						continue
					self.materials[material.name] = material
					self.mesh_exclude_materials.add(material.name)
				
				
		# collect cubemaps
		self.cubemaps = dict()
		self.scene_cubemap = None
		if self.save_cubemaps_prop:			
			for texture_slot in bpy.context.scene.world.texture_slots.values():
				if texture_slot == None:
					continue
				
				tex = texture_slot.texture
				
				if tex.type != "ENVIRONMENT_MAP":
					continue
				
				if tex.image == None:
					continue
				
				self.cubemaps[tex.name] = tex				
				
				if texture_slot.use_map_horizon:
					self.scene_cubemap = tex.name
		
				
		return
	
	
	
	def __save(self):
		self.__save_assets()
		
		self.xml_doc = Document()
		self.xml_root = self.xml_doc.createElement("tscene")
		self.xml_doc.appendChild(self.xml_root)
		
		self.__save_assets_xml()
		self.__save_objects_xml()
		self.__save_scene_xml()
		
		scene_file = open(self.filepath, 'w')
		scene_file.write(self.xml_doc.toprettyxml(indent="  "))
		scene_file.close()
		
		
	def __save_assets_xml(self):
		assets_node = self.xml_doc.createElement("assets")
		
		if self.include_mat_prop:
			for material_name in self.materials.keys():
				material_node = export_material.create_node(self.xml_doc, self.materials[material_name], self.directory, os.path.join(self.assets_subdir, "materials"), self.pack_tex_prop)
				assets_node.appendChild(material_node)
		
		for mesh_name in self.meshes.keys():
			mesh_node = self.xml_doc.createElement("mesh")
			mesh_node.setAttribute("name", mesh_name)
			
			data_node = self.xml_doc.createElement("data")
			data_node.setAttribute("file", self.saved_mesh_files[mesh_name])
			mesh_node.appendChild(data_node)
			
			assets_node.appendChild(mesh_node)
			
		for cubemap_name in self.cubemaps.keys():
			cubemap_node = self.xml_doc.createElement("cubemap")
			cubemap_node.setAttribute("name", cubemap_name)
			
			data_node = self.xml_doc.createElement("data")
			data_node.setAttribute("file", self.saved_cubemap_files[cubemap_name])
			cubemap_node.appendChild(data_node)
			
			assets_node.appendChild(cubemap_node)
			
		self.xml_root.appendChild(assets_node)
		
	def __save_objects_xml(self):
		objects_node = self.xml_doc.createElement("objects")
			
		object_save_functions = {
			"MESH": self.__save_mesh_object_xml,
			"LAMP": self.__save_lamp_object_xml,
			"EMPTY" : self.__save_empty_object_xml
		}
		
		for obj_name, obj in self.objects.items():
			obj_node = None
			
			try:
				obj_node = object_save_functions[obj.type](obj)
			except KeyError:
				print("Exporting objects of type \"" + obj.type + "\" is not supported")
				continue
				
			if obj_node is not None:
				obj_node.setAttribute("name", obj_name)
				if hasattr(obj, "towerengine"):
					obj_node.setAttribute("tag", obj.towerengine.tag)
					
					for attribute in obj.towerengine.attributes:
						attr_node = self.xml_doc.createElement("attribute")
						attr_node.setAttribute("name", attribute.name)
						attr_node.setAttribute("value", attribute.value)
						obj_node.appendChild(attr_node)
						
						
				objects_node.appendChild(obj_node)
				
		
		self.xml_root.appendChild(objects_node)
		
		
	def __save_scene_xml(self):
		scene_node = self.xml_doc.createElement("scene")
		
		if self.scene_cubemap is not None:
			scene_node.setAttribute("sky_cubemap", self.scene_cubemap)
			
		self.xml_root.appendChild(scene_node)
		
		
	
	def __save_mesh_object_xml(self, obj):
		if obj.towerengine.disable_mesh:
			return None

		obj_node = self.xml_doc.createElement("mesh")
		
		obj_node.appendChild(self.__create_transform_node_xml(obj.matrix_world))
		
		mesh_asset_node = self.xml_doc.createElement("mesh_asset")
		mesh_asset_node.setAttribute("asset", obj.data.name)
		obj_node.appendChild(mesh_asset_node)
		
		if obj.rigid_body:
			obj_node.appendChild(self.__save_rigid_body_xml(obj))
		
		return obj_node


	def __save_rigid_body_xml(self, obj):
		rigid_body = obj.rigid_body

		rigid_body_node = self.xml_doc.createElement("rigid_body")

		collision_shape_node = self.__save_collision_shape_xml(obj)
		rigid_body_node.appendChild(collision_shape_node)

		mass = rigid_body.mass
		if rigid_body.type == "PASSIVE":
			mass = 0.0
		rigid_body_node.setAttribute("mass", str(mass))

		group = 0
		for i in range(0, 20):
			if rigid_body.collision_groups[i]:
				group |= (1 << i)
		rigid_body_node.setAttribute("group", str(group))

		return rigid_body_node


	def __save_collision_shape_xml(self, obj, compound_child=False):
		rigid_body = obj.rigid_body

		if obj.towerengine.compound_shape and not compound_child:
			collision_shape_node = self.xml_doc.createElement("collision_shape")
			collision_shape_node.setAttribute("type", "compound")
			for child in obj.children:
				child_node = self.__save_collision_shape_xml(child, True)
				if child_node is not None:
					collision_shape_node.appendChild(child_node)

		elif rigid_body.collision_shape == "MESH" and not compound_child:
			collision_shape_node = self.xml_doc.createElement("collision_shape")
			collision_shape_node.setAttribute("type", "mesh")

		elif rigid_body.collision_shape == "CONVEX_HULL" and not compound_child:
			collision_shape_node = self.xml_doc.createElement("collision_shape")
			collision_shape_node.setAttribute("type", "convex")

		elif rigid_body.collision_shape == "BOX":
			collision_shape_node = self.xml_doc.createElement("collision_shape")
			collision_shape_node.setAttribute("type", "box")

			bounds = utils.bound_box_minmax(obj.bound_box)
			half_extents_node = self.xml_doc.createElement("half_extents")
			half_extents_node.setAttribute("x", str((bounds[1][0] - bounds[0][0]) * 0.5))
			half_extents_node.setAttribute("y", str((bounds[1][2] - bounds[0][2]) * 0.5))
			half_extents_node.setAttribute("z", str((bounds[1][1] - bounds[0][1]) * 0.5))
			collision_shape_node.appendChild(half_extents_node)

		elif not compound_child:
			collision_shape_node = self.xml_doc.createElement("collision_shape")
			print(
				"Collision Shape type " + rigid_body.collision_shape + " is currently not supported. Using mesh instead.")
			collision_shape_node.setAttribute("type", "mesh")

		else:
			return None

		if compound_child:
			collision_shape_node.appendChild(self.__create_transform_node_xml(obj.matrix_local))

		return collision_shape_node


	
	def __save_lamp_object_xml(self, obj):
		obj_node = None
		lamp = obj.data
		matrix = obj.matrix_world
		
		if lamp.type == "POINT":
			obj_node = self.xml_doc.createElement("point_light")
		
			obj_node.appendChild(self.__create_vector_node_xml("position", matrix[0][3], matrix[2][3], -matrix[1][3]))
			
			distance_node = self.xml_doc.createElement("distance")
			distance_node.setAttribute("v", str(lamp.distance))
			obj_node.appendChild(distance_node)
			
			color_node = self.__create_color_node_xml("color", lamp.color[0] * lamp.energy, lamp.color[1] * lamp.energy, lamp.color[2] * lamp.energy)
			obj_node.appendChild(color_node)
			
		elif lamp.type == "SUN":
			obj_node = self.xml_doc.createElement("dir_light")
			
			direction = matrix.to_3x3() * Vector((0.0, 0.0, 1.0))
			direction.normalize()
			obj_node.appendChild(self.__create_vector_node_xml("direction", direction.x, direction.z, -direction.y))
			
			color_node = self.__create_color_node_xml("color", lamp.color[0] * lamp.energy, lamp.color[1] * lamp.energy, lamp.color[2] * lamp.energy)
			obj_node.appendChild(color_node)
		
		else:
			print("Lamp Object " + obj.name + " could not be exported. Only POINT and SUN lamps are supported.")
		
		return obj_node
	
	
	def __save_empty_object_xml(self, obj):
		name = "empty"
		if obj.towerengine.object_type == "REFLECTION_PROBE":
			name = "reflection_probe"
		obj_node = self.xml_doc.createElement(name)
		obj_node.appendChild(self.__create_transform_node_xml(obj.matrix_world))
		obj_node.appendChild(self.__create_delta_transform_node_xml(obj))
		return obj_node
	
	
	def __create_transform_node_xml(self, matrix):
		transform_node = self.xml_doc.createElement("transform")
		transform_node.appendChild(self.__create_vector_node_xml("position", matrix[0][3], matrix[2][3], -matrix[1][3]))
		transform_node.appendChild(self.__create_vector_node_xml("basis_x", matrix[0][0], matrix[0][2], -matrix[0][1]))
		transform_node.appendChild(self.__create_vector_node_xml("basis_y", matrix[2][0], matrix[2][2], -matrix[2][1]))
		transform_node.appendChild(self.__create_vector_node_xml("basis_z", -matrix[1][0], -matrix[1][2], matrix[1][1]))
		return transform_node

	def __create_delta_transform_node_xml(self, obj):
		node = self.xml_doc.createElement("delta_transform")
		node.appendChild(self.__create_vector_node_xml("position", obj.delta_location.x, obj.delta_location.z, -obj.delta_location.y))
		node.appendChild(self.__create_vector_node_xml("rotation", obj.delta_rotation_euler.x, obj.delta_rotation_euler.z, -obj.delta_rotation_euler.y))
		node.appendChild(self.__create_vector_node_xml("scale", obj.delta_scale.x, obj.delta_scale.z, -obj.delta_scale.y))
		return node
	
	def __create_vector_node_xml(self, name, x, y, z):
		node = self.xml_doc.createElement(name)
		node.setAttribute("x", str(x))
		node.setAttribute("y", str(y))
		node.setAttribute("z", str(z))
		return node
	
	def __create_color_node_xml(self, name, r, g, b):
		node = self.xml_doc.createElement(name)
		node.setAttribute("r", str(r))
		node.setAttribute("g", str(g))
		node.setAttribute("b", str(b))
		return node
	
	
	def __save_assets(self):
		self.assets_subdir = self.file_basename + "_assets"
		self.assets_dir = os.path.join(self.directory, self.assets_subdir)
		
		try:
			os.makedirs(self.assets_dir)
		except OSError as e:
			print(str(e))
		
		self.__save_meshes()
		self.__save_cubemaps()
	
	
	
	def __save_meshes(self):
		self.saved_mesh_files = dict()
		
		if self.include_mat_prop != True:
			self.mesh_exclude_materials = None
		
		for mesh_name, mesh in self.meshes.items():
			export_mesh = ExportMesh()
			export_mesh.add_mesh(mesh)
			
			mesh_file = os.path.join(self.assets_dir, mesh_name + ".tem")
			
			export_mesh.save(mesh_file, self.pack_tex_prop, self.mesh_exclude_materials)
			
			self.saved_mesh_files[mesh_name] = os.path.relpath(mesh_file, self.directory)
			
	def __save_cubemaps(self):
		self.saved_cubemap_files = dict()
		
		for cubemap_name, tex in self.cubemaps.items():
			original_file = tex.image.filepath
			file_extension = original_file.split(".")[-1]
			tex_file = os.path.join(self.assets_dir, "cubemap_" + cubemap_name + "." + file_extension)
			try:
				shutil.copy(bpy.path.abspath(original_file), tex_file)
			except OSError as e:
				print(str(e))
			except IOError as e:
				print(str(e))
			self.saved_cubemap_files[cubemap_name] = os.path.relpath(tex_file, self.directory)


def menu_func(self, context):
	self.layout.operator(TowerEngineSceneExporter.bl_idname, text="TowerEngine Scene (.tes)")

def register():
	bpy.utils.register_class(TowerEngineSceneExporter)
	bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
	bpy.types.INFO_MT_file_export.remove(menu_func)
	bpy.utils.unregister_class(TowerEngineSceneExporter)
