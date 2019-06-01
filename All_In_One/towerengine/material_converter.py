
import os
import bpy
import shutil
import base64
import itertools
from abc import ABC, abstractmethod

class MaterialConverter(ABC):
	def __init__(self):
		super(MaterialConverter, self).__init__()

	@abstractmethod
	def _create_default_material(self, name,
								 base_color_tex, base_color,
								 metal_rough_reflect_tex, metallic, roughness, reflectance,
								 normal_tex,
								 bump_tex, bump_depth,
								 emission_tex, emission_color,
								 cast_shadow):
		pass

	@abstractmethod
	def _create_simple_forward_material(self, name,
										color_tex, color, alpha,
										blend_mode):
		pass

	@abstractmethod
	def _create_refraction_material(self, name,
									color_tex, color,
									edge_color,
									normal_tex):
		pass


	def execute(self, material):
		if material.towerengine.mat_type == "DEFAULT":
			self.execute_default_material(material)
		elif material.towerengine.mat_type == "SIMPLE_FORWARD":
			self.execute_simple_forward_material(material)
		elif material.towerengine.mat_type == "REFRACTION":
			self.execute_refraction_material(material)
		else:
			self.execute_default_material(material)


	def execute_default_material(self, material):
		base_color_tex = metal_rough_reflect_tex = normal_tex = bump_tex = emission_tex = None
		bump_depth = 0.0

		for tex_slot, towerengine_tex_slot in itertools.zip_longest(material.texture_slots,
																	material.towerengine_texture_slots):
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


		self._create_default_material(name=material.name,
									  base_color_tex=base_color_tex, base_color=material.diffuse_color,
									  metal_rough_reflect_tex=metal_rough_reflect_tex, metallic=material.towerengine.metallic,
									  roughness=material.towerengine.roughness, reflectance=material.towerengine.reflectance,
									  normal_tex=normal_tex,
									  emission_tex=emission_tex, emission_color=material.diffuse_color * material.emit,
									  bump_tex=bump_tex, bump_depth=bump_depth,
									  cast_shadow=material.use_cast_shadows)


	def execute_simple_forward_material(self, material):
		tex = None

		for tex_slot in material.texture_slots:
			if tex_slot is None:
				continue
			texture = tex_slot.texture
			if texture.type != 'IMAGE':
				continue

			if tex_slot.use_map_color_diffuse:
				tex = texture

		a = 1.0
		if material.use_transparency:
			a = material.alpha

		self._create_simple_forward_material(name=material.name,
											 color_tex=tex, color=material.diffuse_color, alpha=a,
											 blend_mode=material.towerengine.blend_mode)


	def execute_refraction_material(self, material):
		tex = None
		normal_tex = None

		for tex_slot in material.texture_slots:
			if tex_slot is None:
				continue
			texture = tex_slot.texture
			if texture.type != 'IMAGE':
				continue

			if tex_slot.use_map_color_diffuse:
				tex = texture
			if tex_slot.use_map_normal:
				normal_tex = texture


		self._create_refraction_material(name=material.name,
										 color_tex = tex, color=material.diffuse_color,
										 edge_color=material.towerengine.refraction_edge_color,
										 normal_tex=normal_tex)

