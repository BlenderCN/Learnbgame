# ##### BEGIN LGPL LICENSE BLOCK #####
#
#  Copyright (C) 2018 Nikolai Janakiev
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this library; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END LGPL LICENSE BLOCK #####


import bpy
from mathutils import Color


def glass_material(diffuse_color=(0.28, 0.51, 0.8), specular_color=(0.55, 0.91, 1.0), ior=1.4):
	mat = bpy.data.materials.new('GlassMaterial')

	# Diffuse
	mat.diffuse_shader = 'LAMBERT'
	mat.diffuse_intensity = 1
	mat.diffuse_color = diffuse_color

	# Specular
	mat.specular_shader = 'TOON'
	mat.specular_intensity = 1
	mat.specular_toon_size = 0.2
	mat.specular_toon_smooth = 0
	mat.specular_color = specular_color

	# Shading
	mat.emit = 0.7

	# Transparency settings
	mat.use_transparency = True
	mat.transparency_method = 'RAYTRACE'
	mat.alpha = 0.1
	mat.raytrace_transparency.ior = ior
	mat.raytrace_transparency.depth = 3
	mat.raytrace_transparency.filter = 0
	mat.raytrace_transparency.falloff = 0.5
	mat.raytrace_transparency.depth_max = 2

	# Mirror settings
	mat.raytrace_mirror.use = True
	mat.raytrace_mirror.reflect_factor = 0.5
	mat.raytrace_mirror.fresnel = 2
	mat.raytrace_mirror.fresnel_factor = 1.25
	mat.raytrace_mirror.gloss_factor = 1

	return mat


def glossy_falloff_material(diffuse_color):
	mat = bpy.data.materials.new('GlossyFalloffMaterial')

	# Diffuse
	mat.diffuse_shader = 'LAMBERT'
	mat.use_diffuse_ramp = True
	mat.diffuse_ramp.elements[0].position = 0
	mat.diffuse_ramp.elements[1].position = 1
	mat.diffuse_ramp_input = 'NORMAL'
	mat.diffuse_ramp_blend = 'ADD'
	mat.diffuse_color = diffuse_color

	# Specular
	mat.specular_shader = 'TOON'
	mat.specular_toon_smooth = 0
	mat.specular_toon_size = 0.4

	return mat


def falloff_material_HSV(h, s=0.9, v=0.9):
	mat = bpy.data.materials.new('FalloffMaterial')

	diffuse_color = Color()
	diffuse_color.hsv = ((h % 1.0), s, v)

	# Diffuse
	mat.diffuse_shader = 'LAMBERT'
	mat.use_diffuse_ramp = True
	mat.diffuse_ramp_input = 'NORMAL'
	mat.diffuse_ramp_blend = 'ADD'
	mat.diffuse_ramp.elements[0].color = (1, 1, 1, 1)
	mat.diffuse_ramp.elements[1].color = (1, 1, 1, 0)
	mat.diffuse_color = diffuse_color
	mat.diffuse_intensity = 1.0

	# Specular
	mat.specular_intensity = 0.0

	# Shading
	mat.emit = 0.05
	mat.translucency = 0.2

	return mat


def falloff_material(diffuse_color, diffuse_intensity=1.0, emit=0.05, translucency=0.2):
	mat = bpy.data.materials.new('FalloffMaterial')

	# Diffuse
	mat.diffuse_shader = 'LAMBERT'
	mat.use_diffuse_ramp = True
	mat.diffuse_ramp_input = 'NORMAL'
	mat.diffuse_ramp_blend = 'ADD'
	mat.diffuse_ramp.elements[0].color = (1, 1, 1, 1)
	mat.diffuse_ramp.elements[1].color = (1, 1, 1, 0)
	mat.diffuse_color = diffuse_color
	mat.diffuse_intensity = diffuse_intensity

	# Specular
	mat.specular_intensity = 0.0

	# Shading
	mat.emit = emit
	mat.translucency = translucency

	return mat


def dark_glass_material(ior=1.3):
	mat = bpy.data.materials.new('DarkGlassMaterial')

	# Diffuse
	mat.diffuse_shader = 'LAMBERT'
	mat.diffuse_intensity = 1
	mat.diffuse_color = (0, 0, 0)

	# Specular
	mat.specular_intensity = 0.0

	# Transparency settings
	mat.use_transparency = True
	mat.transparency_method = 'RAYTRACE'
	mat.alpha = 0.0
	mat.raytrace_transparency.ior = ior

	return mat


def material(diffuse_color, diffuse_shader='LAMBERT', diffuse_intensity=0.9, emit=0.0):
	mat = bpy.data.materials.new('Material')

	# Diffuse
	mat.diffuse_shader = diffuse_shader
	mat.diffuse_intensity = diffuse_intensity
	mat.diffuse_color = diffuse_color

	# Specular
	mat.specular_intensity = 0

	mat.emit = emit

	return mat
