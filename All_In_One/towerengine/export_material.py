
import os
import bpy
import shutil
import base64
import itertools


def create_texture_node(pack_textures, path, tex_path, filename, texture, doc, node):
	file_extension = texture.image.filepath.split(".")[-1]
	if not pack_textures:
		tex_file = os.path.join(tex_path, filename + "." + file_extension)
		try:
			shutil.copy(texture.image.filepath_from_user(), tex_file)
		except OSError as e:
			print(str(e))
		except IOError as e:
			print(str(e))
		node.setAttribute("file", os.path.relpath(tex_file, path))
	else:
		with open(texture.image.filepath_from_user(), "rb") as image_file:
			image_data = image_file.read()
			image_base64 = base64.b64encode(image_data)
			image_text = doc.createTextNode(image_base64.decode("utf-8"))
			node.appendChild(image_text)
		node.setAttribute("image-extension", file_extension)



def create_default_material_node(doc, material, path, subpath, pack_textures = False):
	base_color_tex = metal_rough_reflect_tex = normal_tex = bump_tex = emission_tex = None
	bump_depth = 0.0

	for tex_slot, towerengine_tex_slot in itertools.zip_longest(material.texture_slots, material.towerengine_texture_slots):
		if not tex_slot:
			continue
		texture = tex_slot.texture
		if texture.type != 'IMAGE':
			continue

		if tex_slot.use_map_color_diffuse:
			base_color_tex = texture
		if tex_slot.use_map_normal:
			normal_tex = texture
		if tex_slot.use_map_displacement:
			bump_tex = texture
			bump_depth = tex_slot.displacement_factor
		if tex_slot.use_map_emit:
			emission_tex = texture

		if towerengine_tex_slot is not None:
			if towerengine_tex_slot.use_map_metal_rough_reflect:
				metal_rough_reflect_tex = texture


	if pack_textures == False and (base_color_tex is not None
									or metal_rough_reflect_tex is not None
									or normal_tex is not None
									or bump_tex is not None
									or emission_tex is not None):
		tex_path = os.path.join(path, subpath, material.name)
		try:
			os.makedirs(tex_path)
		except OSError as e:
			print(str(e))
	else:
		tex_path = None


	node = doc.createElement("material")
	node.setAttribute("name", material.name)
	node.setAttribute("type", "default")


	# base color

	node2 = doc.createElement("base_color")
	if base_color_tex is not None:
		create_texture_node(pack_textures, path, tex_path, "base_color", base_color_tex, doc, node2)
	else:
		node2.setAttribute("r", str(material.diffuse_color.r))
		node2.setAttribute("g", str(material.diffuse_color.g))
		node2.setAttribute("b", str(material.diffuse_color.b))
	node.appendChild(node2)



	# normal

	if normal_tex is not None:
		node2 = doc.createElement("normal")
		create_texture_node(pack_textures, path, tex_path, "normal", normal_tex, doc, node2)
		node.appendChild(node2)



	# metallic roughness reflectance

	node2 = doc.createElement("metal_rough_reflect")
	if metal_rough_reflect_tex is not None:
		create_texture_node(pack_textures, path, tex_path, "metal_rough_reflect", metal_rough_reflect_tex, doc, node2)
	else:
		node2.setAttribute("metallic", str(material.towerengine.metallic))
		node2.setAttribute("roughness", str(material.towerengine.roughness))
		node2.setAttribute("reflectance", str(material.towerengine.reflectance))
	node.appendChild(node2)



	# emission

	if material.emit > 0.0:
		node2 = doc.createElement("emission")
		if emission_tex is not None:
			create_texture_node(pack_textures, path, tex_path, "emission", emission_tex, doc, node2)
		else:
			node2.setAttribute("r", str(material.diffuse_color.r * material.emit))
			node2.setAttribute("g", str(material.diffuse_color.g * material.emit))
			node2.setAttribute("b", str(material.diffuse_color.b * material.emit))
		node.appendChild(node2)


	# bump

	if bump_tex is not None:
		node2 = doc.createElement("bump")
		create_texture_node(pack_textures, path, tex_path, "bump", bump_tex, doc, node2)
		node2.setAttribute("depth", str(bump_depth))
		node.appendChild(node2)



	# shadowing

	if not material.use_cast_shadows:
		node2 = doc.createElement("shadow")
		node2.setAttribute("cast", "0")
		node.appendChild(node2)

	return node


def create_simple_forward_material_node(doc, material, path, subpath, pack_textures = False):
	tex = None

	for tex_slot in material.texture_slots:
		if tex_slot == None:
			continue
		texture = tex_slot.texture
		if texture.type != 'IMAGE':
			continue

		if tex_slot.use_map_color_diffuse:
			tex = texture

	if pack_textures == False and tex != None:
		tex_path = os.path.join(path, subpath, material.name)
		try:
			os.makedirs(tex_path)
		except OSError as e:
			print(str(e))


	node = doc.createElement("material")
	node.setAttribute("name", material.name)
	node.setAttribute("type", "simple_forward")

	blend_mode = "alpha"
	if material.towerengine.blend_mode == "ALPHA":
		blend_mode = "alpha"
	elif material.towerengine.blend_mode == "ADD":
		blend_mode = "add"
	elif material.towerengine.blend_mode == "MULTIPLY":
		blend_mode = "multiply"
	node.setAttribute("blend_mode", blend_mode)

	node2 = doc.createElement("color")
	node2.setAttribute("r", str(material.diffuse_color.r * material.diffuse_intensity))
	node2.setAttribute("g", str(material.diffuse_color.g * material.diffuse_intensity))
	node2.setAttribute("b", str(material.diffuse_color.b * material.diffuse_intensity))

	a = 1.0
	if material.use_transparency:
		a = material.alpha
	node2.setAttribute("a", str(a))

	node.appendChild(node2);


	if tex != None:
		node2 = doc.createElement("tex")
		file_extension = tex.image.filepath.split(".")[-1]
		if pack_textures == False:
			tex_file = os.path.join(tex_path, "tex." + file_extension)
			try:
				shutil.copy(bpy.path.abspath(tex.image.filepath), tex_file)
			except OSError as e:
				print(str(e))
			except IOError as e:
				print(str(e))
			node2.setAttribute("file", os.path.relpath(tex_file, path))
		else:
			with open(bpy.path.abspath(tex.image.filepath), "rb") as image_file:
				image_data = image_file.read()
				image_base64 = base64.b64encode(image_data)
				image_text = doc.createTextNode(image_base64.decode("utf-8"))
				node2.appendChild(image_text)
			node2.setAttribute("image-extension", file_extension)

		node.appendChild(node2);

	return node




def create_refraction_material_node(doc, material, path, subpath, pack_textures = False):
	tex = None
	normal_tex = None

	for tex_slot in material.texture_slots:
		if tex_slot == None:
			continue
		texture = tex_slot.texture
		if texture.type != 'IMAGE':
			continue

		if tex_slot.use_map_color_diffuse:
			tex = texture
		if tex_slot.use_map_normal:
			normal_tex = texture

	if pack_textures == False and (tex != None or normal_tex != None):
		tex_path = os.path.join(path, subpath, material.name)
		try:
			os.makedirs(tex_path)
		except OSError as e:
			print(str(e))


	node = doc.createElement("material")
	node.setAttribute("name", material.name)
	node.setAttribute("type", "refraction")

	node2 = doc.createElement("color")
	node2.setAttribute("r", str(material.diffuse_color.r * material.diffuse_intensity))
	node2.setAttribute("g", str(material.diffuse_color.g * material.diffuse_intensity))
	node2.setAttribute("b", str(material.diffuse_color.b * material.diffuse_intensity))

	if tex != None:
		file_extension = tex.image.filepath.split(".")[-1]
		if pack_textures == False:
			tex_file = os.path.join(tex_path, "color." + file_extension)
			try:
				shutil.copy(bpy.path.abspath(tex.image.filepath), tex_file)
			except OSError as e:
				print(str(e))
			except IOError as e:
				print(str(e))
			node2.setAttribute("file", os.path.relpath(tex_file, path))
		else:
			with open(bpy.path.abspath(tex.image.filepath), "rb") as image_file:
				image_data = image_file.read()
				image_base64 = base64.b64encode(image_data)
				image_text = doc.createTextNode(image_base64.decode("utf-8"))
				node2.appendChild(image_text)
			node2.setAttribute("image-extension", file_extension)

		node.appendChild(node2)

	node.appendChild(node2);

	node2 = doc.createElement("edge_color")
	node2.setAttribute("r", str(material.towerengine.refraction_edge_color[0]))
	node2.setAttribute("g", str(material.towerengine.refraction_edge_color[1]))
	node2.setAttribute("b", str(material.towerengine.refraction_edge_color[2]))
	node2.setAttribute("a", str(material.towerengine.refraction_edge_color[3]))
	node.appendChild(node2)



	if normal_tex != None:
		node2 = doc.createElement("normal_tex")
		file_extension = normal_tex.image.filepath.split(".")[-1]
		if pack_textures == False:
			tex_file = os.path.join(tex_path, "normal." + file_extension)
			try:
				shutil.copy(bpy.path.abspath(normal_tex.image.filepath), tex_file)
			except OSError as e:
				print(str(e))
			except IOError as e:
				print(str(e))
			node2.setAttribute("file", os.path.relpath(tex_file, path))
		else:
			with open(bpy.path.abspath(normal_tex.image.filepath), "rb") as image_file:
				image_data = image_file.read()
				image_base64 = base64.b64encode(image_data)
				image_text = doc.createTextNode(image_base64.decode("utf-8"))
				node2.appendChild(image_text)
			node2.setAttribute("image-extension", file_extension)

		node.appendChild(node2)

	return node



def create_node(doc, material, path, subpath, pack_textures = False):
	if material.towerengine.mat_type == "DEFAULT":
		return create_default_material_node(doc, material, path, subpath, pack_textures)
	elif material.towerengine.mat_type == "SIMPLE_FORWARD":
		return create_simple_forward_material_node(doc, material, path, subpath, pack_textures)
	elif material.towerengine.mat_type == "REFRACTION":
		return create_refraction_material_node(doc, material, path, subpath, pack_textures)
	else:
		return create_default_material_node(doc, material, path, subpath, pack_textures)
