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
from vb25.utils import *
from vb25.ui import ui


TYPE= 'SETTINGS'

ID=   'SettingsOutput'

NAME= 'Output'
DESC= "Output options"

PARAMS= (
)


def add_properties(rna_pointer):
	class SettingsOutput(bpy.types.PropertyGroup):
		img_format = EnumProperty(
			name= "Type",
			description= "Output image format",
			items= (
				('PNG',   "PNG",       "PNG"),
				('JPG',   "JPEG",      "Jpeg"),
				('TIFF',  "Tiff",      "Tiff"),
				('TGA',   "TGA",       "Targa"),
				('SGI',   "SGI",       "SGI"),
				('EXR',   "OpenEXR",   "OpenEXR"),
				('VRIMG', "VRayImage", "V-Ray Image format"),
			),
			default= 'PNG'
		)

		color_depth = EnumProperty(
			name= "Color depth",
			description= "Сolor depth",
			items= (
				('32', "32", "32 bit"),
				('16', "16", "16 bit"),
				('8',  "8",  "8 bit"),
			),
			default= '32'
		)

		img_noAlpha= BoolProperty(
			name= "No alpha",
			description= "Don't write the alpha channel to the final image",
			default= False
		)

		img_separateAlpha= BoolProperty(
			name= "Separate alpha",
			description= "Write the alpha channel to a separate file",
			default= False
		)

		img_file= StringProperty(
			name= "File name",
			description= "Render file name (Variables: %C - camera name; %S - scene name; %F - blend file name)",
			default= "%F_%C"
		)

		img_dir= StringProperty(
			name= "Path",
			description= "Render file directory (Variables: %C - camera name; %S - scene name; %F - blend file name)",
			subtype= 'DIR_PATH',
			default= "//render_%F/"
		)

		img_file_needFrameNumber= BoolProperty(
			name= "Add frame number",
			description= "Add frame number to the image file name",
			default= True
		)

		relements_separateFolders= BoolProperty(
			name= "Separate folders",
			description= "Save render channels in separate folders",
			default= False
		)

		relements_separateFiles = BoolProperty(
			name = "Separate Files",
			description = "Save render channels in separate files",
			default = True
		)
	bpy.utils.register_class(SettingsOutput)

	rna_pointer.SettingsOutput= PointerProperty(
		name= NAME,
		type= SettingsOutput,
		description= DESC
	)



def write(bus):
	COMPRESSION= {
		'NONE':  1,
		'PXR24': 6,
		'ZIP':   4,
		'PIZ':   5,
		'RLE':   2,
	}

	ofile=  bus['files']['scene']
	scene=  bus['scene']

	VRayScene=      scene.vray
	VRayExporter=   VRayScene.exporter
	VRayDR=         VRayScene.VRayDR
	SettingsOutput= VRayScene.SettingsOutput

	wx= int(scene.render.resolution_x * scene.render.resolution_percentage * 0.01)
	wy= int(scene.render.resolution_y * scene.render.resolution_percentage * 0.01)

	ofile.write("\nSettingsOutput SettingsOutput {")
	if VRayExporter.auto_save_render:
		ofile.write("\n\timg_file= \"%s\";" % bus['filenames']['output_filename'])
		ofile.write("\n\timg_dir= \"%s/\";" % bus['filenames']['output'])

	if SettingsOutput.img_format == 'EXR':
		if not SettingsOutput.relements_separateFiles:
			ofile.write("\n\timg_rawFile=1;")

	ofile.write("\n\timg_noAlpha= %d;" % SettingsOutput.img_noAlpha)
	ofile.write("\n\timg_separateAlpha= %d;" % SettingsOutput.img_separateAlpha)
	ofile.write("\n\timg_width= %s;" % wx)
	ofile.write("\n\timg_height= %s;" % (wx if VRayScene.VRayBake.use else wy))
	ofile.write("\n\timg_file_needFrameNumber= %d;" % SettingsOutput.img_file_needFrameNumber)
	ofile.write("\n\tanim_start= %d;" % scene.frame_start)
	ofile.write("\n\tanim_end= %d;" % scene.frame_end)
	ofile.write("\n\tframe_start= %d;" % scene.frame_start)
	ofile.write("\n\tframes_per_second= %.3f;" % 1.0)
	ofile.write("\n\tframes= %d-%d;" % (scene.frame_start, scene.frame_end))
	ofile.write("\n\tframe_stamp_enabled= %d;" % 0)
	ofile.write("\n\tframe_stamp_text= \"%s\";" % ("V-Ray/Blender 2.0 | V-Ray Standalone %%vraycore | %%rendertime"))
	ofile.write("\n\trelements_separateFolders= %d;" % SettingsOutput.relements_separateFolders)
	ofile.write("\n\trelements_divider= \".\";")
	ofile.write("\n}\n")

	ofile.write("\nSettingsEXR SettingsEXR {")
	ofile.write("\n\tcompression= %i;" % COMPRESSION[scene.render.image_settings.exr_codec])
	ofile.write("\n\tbits_per_channel=%s;" % SettingsOutput.color_depth)
	ofile.write("\n}\n")

	ofile.write("\nSettingsTIFF SettingsTIFF {")
	ofile.write("\n\tbits_per_channel=%s;" % SettingsOutput.color_depth)
	ofile.write("\n}\n")

	ofile.write("\nSettingsSGI SettingsSGI {")
	ofile.write("\n\tbits_per_channel=%s;" % SettingsOutput.color_depth)
	ofile.write("\n}\n")

	ofile.write("\nSettingsJPEG SettingsJPEG {")
	ofile.write("\n\tquality=%d;" % scene.render.image_settings.quality)
	ofile.write("\n}\n")

	ofile.write("\nSettingsPNG SettingsPNG {")
	ofile.write("\n\tcompression=%d;" % (int(scene.render.image_settings.quality / 10) if scene.render.image_settings.quality < 90 else 9))
	ofile.write("\n\tbits_per_channel=%s;" % (SettingsOutput.color_depth if SettingsOutput.color_depth in ['8','16'] else '16'))
	ofile.write("\n}\n")
