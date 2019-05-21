#
# V-Ray/Blender
#
# http://vray.cgdo.ru
#
# Author: Andrey M. Izrantsev (aka bdancer)
# E-Mail: izrantsev@cgdo.ru
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.
#


# Blender modules
import bpy
from bpy.props import *

# V-Ray/Blender modules
from vb25.utils   import *
from vb25.ui      import ui
from vb25.plugins import *
from vb25.texture import *
from vb25.uvwgen  import *


TYPE = 'TEXTURE'
ID   = 'TexPtex'
PLUG = 'TexPtex'
PID  =  200

NAME = 'Ptex'
DESC = "VRay TexPtex texture"

PARAMS = (
	'ptex_file',
	'use_image_sequence',
	'image_number',
	'image_offset',
	'ifl_start_frame',
	'ifl_playback_rate',
	'ifl_end_condition',
	'filter_type',
	'width',
	'blur',
	'sharpness',
	'lerp',
	'reverse_vertices',
	'cache_size',
	'r_channel',
	'g_channel',
	'b_channel',
	'a_channel',
	'auto_color',
	'auto_alpha',
	'alpha_type',
	'color_space',
	'gamma',
	# 'vertices',
	# 'origFaces',
	# 'faces',
	# 'origFacesDegree',
	'color_gain',
	'color_offset',
)


def add_properties(rna_pointer):
	class TexPtex(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(TexPtex)

	rna_pointer.TexPtex = PointerProperty(
		name        = "TexPtex",
		type        =  TexPtex,
		description = "V-Ray TexPtex settings"
	)

	# ptex_file
	TexPtex.ptex_file = StringProperty(
		name        = "File",
		subtype     = 'FILE_PATH',
		description = "The Ptex texture file",
		default     = ""
	)

	# use_image_sequence
	TexPtex.use_image_sequence= IntProperty(
		name= "use image sequence",
		description= "",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 0
	)

	# image_number
	TexPtex.image_number= IntProperty(
		name= "image number",
		description= "",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 0
	)

	# image_offset
	TexPtex.image_offset= IntProperty(
		name= "image offset",
		description= "",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 0
	)

	# ifl_start_frame
	TexPtex.ifl_start_frame= IntProperty(
		name= "ifl start frame",
		description= "TODO: Tooltip",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 0
	)

	# ifl_playback_rate
	TexPtex.ifl_playback_rate= FloatProperty(
		name= "ifl playback rate",
		description= "TODO: Tooltip",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# ifl_end_condition
	TexPtex.ifl_end_condition= IntProperty(
		name= "ifl end condition",
		description= "Image file list (IFL) end condition: 0 - Loop; 1 - Ping Pong; 2 - Hold;",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 0
	)

	# filter_type
	TexPtex.filter_type = EnumProperty(
		name  = "Filter Type",
		description = "Type of filter used for the texture",
		items = (
			('0', '0', "0"),
			('1', '1', "1")
		),
		default = '0'
	)

	# width
	TexPtex.width= FloatProperty(
		name= "width",
		description= "width parameter used for filtering",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# blur
	TexPtex.blur= FloatProperty(
		name= "blur",
		description= "blur parameter used for filtering",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	# sharpness
	TexPtex.sharpness= FloatProperty(
		name= "sharpness",
		description= "Sharpness parameter for the general bicubic filter",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	# lerp
	TexPtex.lerp= BoolProperty(
		name= "lerp",
		description= "Interpolation between mipmap levels",
		default= False
	)

	# reverse_vertices
	TexPtex.reverse_vertices= BoolProperty(
		name= "reverse vertices",
		description= "Reverses the order of vertices",
		default= False
	)

	# cache_size
	TexPtex.cache_size= IntProperty(
		name= "cache size",
		description= "The size of the texture cache(in MB)",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 1
	)

	# r_channel
	TexPtex.r_channel= IntProperty(
		name= "r channel",
		description= "The index of the channel which will be used as a red channel",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 0
	)

	# g_channel
	TexPtex.g_channel= IntProperty(
		name= "g channel",
		description= "The index of the channel which will be used as a green channel",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 1
	)

	# b_channel
	TexPtex.b_channel= IntProperty(
		name= "b channel",
		description= "The index of the channel which will be used as a blue channel",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 2
	)

	# a_channel
	TexPtex.a_channel= IntProperty(
		name= "a channel",
		description= "The index of the channel which will be used as a alpha channel",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= -1
	)

	# auto_color
	TexPtex.auto_color= BoolProperty(
		name= "auto color",
		description= "Use automatic color channel selection",
		default= True
	)

	# auto_alpha
	TexPtex.auto_alpha= BoolProperty(
		name= "auto alpha",
		description= "Use automatic alpha channel selection",
		default= True
	)

	# alpha_type
	TexPtex.alpha_type= IntProperty(
		name= "alpha type",
		description= "Where to take the alpha from",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= -1
	)

	# color_space
	TexPtex.color_space = EnumProperty(
		name  = "Color Space",
		items = (
			('0', 'Linear',          "Linear"),
			('1', 'Gamma corrected', "Gamma corrected"),
			('2', 'sRGB',            "sRGB")
		),
		default = '1'
	)

	# gamma
	TexPtex.gamma= FloatProperty(
		name= "gamma",
		description= "TODO: Tooltip",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# vertices
	# origFaces
	# faces
	# origFacesDegree

	# color_gain
	TexPtex.color_gain= FloatVectorProperty(
		name= "Gain",
		description= "A multiplier for the texture color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (1,1,1)
	)

	# color_offset
	TexPtex.color_offset= FloatVectorProperty(
		name= "Offset",
		description= "An additional offset for the texture color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0,0,0)
	)


#
# Output
#
def write(bus):
	return None


#
# User Interface
#
class VRAY_PA_TexPtex(ui.VRayTexturePanel, bpy.types.Panel):
	bl_label       = "PTex [in progress...]"
	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		tex = context.texture
		return tex and tex.type == 'VRAY' and tex.vray.type == ID and ui.engine_poll(cls, context)

	def draw(self, context):
		wide_ui = context.region.width > ui.narrowui
		layout  = self.layout

		tex     = context.texture
		TexPtex = getattr(tex.vray, PLUG)

		split = layout.split()
		col = split.column()
		col.prop(TexPtex, 'ptex_file')
		col.prop(TexPtex, 'use_image_sequence')
		col.prop(TexPtex, 'image_number')
		col.prop(TexPtex, 'image_offset')
		col.prop(TexPtex, 'ifl_start_frame')
		col.prop(TexPtex, 'ifl_playback_rate')
		col.prop(TexPtex, 'ifl_end_condition')
		col.prop(TexPtex, 'filter_type')
		col.prop(TexPtex, 'width')
		col.prop(TexPtex, 'blur')
		col.prop(TexPtex, 'sharpness')
		col.prop(TexPtex, 'lerp')
		col.prop(TexPtex, 'reverse_vertices')
		col.prop(TexPtex, 'cache_size')

		split = layout.split()
		col = split.column()
		col.prop(TexPtex, 'r_channel')
		col.prop(TexPtex, 'g_channel')
		col.prop(TexPtex, 'b_channel')
		col.prop(TexPtex, 'a_channel')
		col.prop(TexPtex, 'auto_color')
		col.prop(TexPtex, 'auto_alpha')
		col.prop(TexPtex, 'alpha_type')
		col.prop(TexPtex, 'color_space')
		col.prop(TexPtex, 'gamma')

		split = layout.split()
		col = split.column()
		col.prop(TexPtex, 'color_gain')
		if wide_ui:
			col= split.column()
		col.prop(TexPtex, 'color_offset')


def GetRegClasses():
	return (
		VRAY_PA_TexPtex,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
