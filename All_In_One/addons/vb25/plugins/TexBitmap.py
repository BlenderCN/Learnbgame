'''

  V-Ray/Blender

  http://vray.cgdo.ru

  Author: Andrey M. Izrantsev (aka bdancer)
  E-Mail: izrantsev@cgdo.ru

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

  All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.

'''


''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils   import *
from vb25.shaders import *
from vb25.ui      import ui
from vb25.uvwgen  import *


TYPE= 'TEXTURE'
ID=   'TexBitmap'

NAME= 'Bitmap'
DESC= "Image texture"


def add_properties(rna_pointer):
	class VRayImage(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(VRayImage)

	class BitmapBuffer(bpy.types.PropertyGroup):
		filter_type= EnumProperty(
			name= "Filter type",
			description= "Filter type",
			items= (
				('NONE',   "None",        "None"),
				('MIPMAP', "Mip-Map",     "Mip-map filtering"),
				('AREA',   "Area",        "Summed area filtering")
			),
			default= 'NONE'
		)

		color_space= EnumProperty(
			name= "Color space",
			description= "Color space",
			items= (
				('LINEAR', "Linear",          ""), # 0
				('GAMMA',  "Gamma corrected", ""),
				('SRGB',   "sRGB",            "")
			),
			default= 'SRGB'
		)

		interpolation= EnumProperty(
			name= "Interpolation",
			description= "Interpolation",
			items= (
				('BILINEAR', "Bilinear", ""), # 0
				('BICUBIC',  "Bicubic",  ""),
			),
			default= 'BILINEAR'
		)

		filter_blur= FloatProperty(
			name= "Blur",
			description= "Filter blur",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 1.0,
			default= 1.0
		)

		gamma= FloatProperty(
			name= "Gamma",
			description= "Gamma",
			min= 0.0,
			max= 100.0,
			soft_min= 0.0,
			soft_max= 10.0,
			precision= 4,
			default= 1.0
		)

		use_input_gamma= BoolProperty(
			name= "Use \"Input gamma\"",
			description= "Use \"Input gamma\" from \"Color mapping\" settings",
			default= True
		)

		gamma_correct= BoolProperty(
			name= "Invert gamma",
			description= "Correct \"Color mapping\" gamma (set image gamma = 1 / cm_gamma)",
			default= False
		)

		allow_negative_colors= BoolProperty(
			name= "Allow negative colors",
			description= "If false negative colors will be clamped",
			default= False
		)

		use_data_window= BoolProperty(
			name= "Use data window",
			description= "Use the data window information in OpenEXR files",
			default= True
		)
	bpy.utils.register_class(BitmapBuffer)

	bpy.types.Image.vray= PointerProperty(
		name= "V-Ray Image Settings",
		type=  VRayImage,
		description= "V-Ray image settings"
	)

	VRayImage.BitmapBuffer= PointerProperty(
		name= "BitmapBuffer",
		type=  BitmapBuffer,
		description= "BitmapBuffer settings"
	)



'''
  OUTPUT
'''
def write_BitmapBuffer(bus):
	FILTER_TYPE= {
		'NONE':   0,
		'MIPMAP': 1,
		'AREA':   2,
	}
	COLOR_SPACE= {
		'LINEAR': 0,
		'GAMMA':  1,
		'SRGB':   2,
	}
	INTERPOLATION= {
		'BILINEAR': 0,
		'BICUBIC':  1,
	}

	ofile= bus['files']['textures']
	scene= bus['scene']

	slot=    bus['mtex']['slot']
	texture= bus['mtex']['texture']

	VRayScene=    scene.vray
	SettingsColorMapping= VRayScene.SettingsColorMapping

	VRaySlot=     texture.vray_slot
	VRayTexture=  texture.vray
	BitmapBuffer= texture.image.vray.BitmapBuffer

	filename= get_full_filepath(bus, texture.image, texture.image.filepath)

	bitmap_name= 'IM' + clean_string(texture.image.name)

	# Check if already exported
	if not append_unique(bus['cache']['bitmap'], bitmap_name):
		return bitmap_name

	ofile.write("\nBitmapBuffer %s {" % bitmap_name)
	ofile.write("\n\tfile= \"%s\";" % filename)
	ofile.write("\n\tcolor_space= %i;" % COLOR_SPACE[BitmapBuffer.color_space])
	ofile.write("\n\tinterpolation= %i;" % INTERPOLATION[BitmapBuffer.interpolation])
	ofile.write("\n\tallow_negative_colors= %i;" % BitmapBuffer.allow_negative_colors)
	ofile.write("\n\tfilter_type= %d;" % FILTER_TYPE[BitmapBuffer.filter_type])
	ofile.write("\n\tfilter_blur= %.3f;" % BitmapBuffer.filter_blur)
	ofile.write("\n\tuse_data_window= %i;" % BitmapBuffer.use_data_window)

	if BitmapBuffer.use_input_gamma:
		ofile.write("\n\tgamma= %s;" % p(SettingsColorMapping.input_gamma))
	else:
		ofile.write("\n\tgamma= %s;" % a(scene, BitmapBuffer.gamma))

	if texture.image.source == 'SEQUENCE':
		ofile.write("\n\tframe_sequence = 1;")
		sequence_frame = 0  # Init sequence frame to use in animation frame

		# Repeat type check
		if texture.image_user.use_cyclic:
			sequence_frame = (scene.frame_current-texture.image_user.frame_offset+texture.image_user.frame_start)%texture.image_user.frame_duration # movie start + current frame - offset
		else:
			sequence_length   = texture.image_user.frame_duration # Crop the sequence duration
			sequence_duration = sequence_length-texture.image_user.frame_start
			sequence_start    = texture.image_user.frame_start
			sequence_offset   = texture.image_user.frame_offset

			# Before sequence start in animation, it takes the first frame
			if scene.frame_current < sequence_offset:
				sequence_frame = sequence_start

			# After the last sequence frame played, it takes the last frame for the rest of the animation
			if scene.frame_current > sequence_duration+sequence_offset:
				sequence_frame = sequence_length

			# Inside the sequence range it uses the exact sequence frame
			if (scene.frame_current >= sequence_offset and scene.frame_current <= sequence_offset+sequence_duration):
				sequence_frame = sequence_start+scene.frame_current-sequence_offset

		ofile.write("\n\tframe_number= %s;" % a(scene,sequence_frame))
	ofile.write("\n}\n")

	return bitmap_name


def write(bus):
	TILE= {
		'NOTILE': 0,
		'TILEUV': 1,
		'TILEU':  2,
		'TILEV':  3,
	}

	scene= bus['scene']
	ofile= bus['files']['textures']

	slot=     bus['mtex']['slot']
	texture=  bus['mtex']['texture']
	tex_name= bus['mtex']['name']

	VRayTexture= texture.vray
	VRaySlot=    texture.vray_slot

	if not texture.image:
		ob_prefix = "Object: %s => " % bus['node']['object'].name if 'object' in bus['node'] else ""
		debug(scene, "%sTexture: %s => Image file is not set!" % (ob_prefix, texture.name), error= True)
		return None

	bitmap= write_BitmapBuffer(bus)

	uvwgen= write_uvwgen(bus)

	ofile.write("\nTexBitmap %s {" % tex_name)
	ofile.write("\n\tbitmap= %s;" % bitmap)
	ofile.write("\n\tuvwgen= %s;" % uvwgen)
	ofile.write("\n\ttile= %d;" % TILE[VRayTexture.tile])
	PLUGINS['TEXTURE']['TexCommon'].write(bus)
	ofile.write("\n}\n")

	return tex_name
