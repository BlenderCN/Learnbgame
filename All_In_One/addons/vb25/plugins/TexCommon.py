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


TYPE= 'TEXTURE'
ID=   'TexCommon'

NAME= 'Common texture setings'
DESC= "Common V-Ray Texture settings."

PARAMS= (
)


def update_blender_mapping_type(self, context):
	if not hasattr(context, 'texture_slot'):
		return
	if not context.texture_slot:
		return
	if self.texture_coords == 'WORLD':
		return
	context.texture_slot.texture_coords = self.texture_coords


def add_properties(rna_pointer):
	rna_pointer.name= StringProperty(
		name= "V-Ray Texture name",
		description= "V-Ray texture name for internal usage",
		subtype= 'NONE',
		options= {'HIDDEN'},
		default= ""
	)

	rna_pointer.texture_coords= EnumProperty(
		name= "Coords",
		description= "Image texure placement type",
		items= (
			('ORCO',  "Object", "Generated coordinates."),
			('UV',    "UV",     "Mesh UV coordinates."),
			('WORLD', "World",  "World coordinates."),
		),
		default= 'ORCO',
		update= update_blender_mapping_type
	)

	rna_pointer.mapping= EnumProperty(
		name= "Projection",
		description= "Generated projection type",
		items= (
			('FLAT',   "Flat",        "Planar projection."),
			('CUBE',   "Cube",        "Cubic projection."),
			('SPHERE', "Sphere",      "Spherical projection."),
			('TUBE',   "Tube",        "Cylindrical projection."),
			('BALL',   "Ball",        "Ball projection."),
			('TRI',    "Triplanar",   "Triplanar projection."),
			('PERS',   "Perspective", "Perspective projection."),
		),
		default= 'FLAT'
	)

	rna_pointer.environment_mapping= EnumProperty(
		name= "Projection",
		description= "Generated projection type",
		items= (
			('SCREEN',  "Screen",      "Planar projection."),
			('CUBIC',   "Cube",        "Cubic projection."),
			('SPHERE',  "Sphere",      "Spherical projection."),
			('TUBE',    "Tube",        "Cylindrical projection."),
			('ANGULAR', "Angular",     "Angular projection."),
			('MBALL',   "Mirror ball", "Mirror ball projection."),
		),
		default= 'SPHERE'
	)

	rna_pointer.object= StringProperty(
		name= "Mapping Object",
		description= "Object to use for mapping generation",
		subtype= 'NONE',
		options= {'HIDDEN'},
		default= ""
	)

	rna_pointer.tile= EnumProperty(
		name= "Tile",
		description= "Tile type",
		items= (
			('NOTILE', "No tile", "No tiling."),
			('TILEUV', "Tile UV", "Tile in UV."),
			('TILEU',  "Tile U",  "Tile in U."),
			('TILEV',  "Tile V",  "Tile in V."),
		),
		default= 'TILEUV'
	)

	rna_pointer.remove_alpha= BoolProperty(
		name= "Remove alpha",
		description= "Reset alpha channel",
		default= False
	)

	# use_3d_mapping
	rna_pointer.use_3d_mapping= BoolProperty(
		name= "Use 3D mapping",
		description= "Use 3D mapping",
		default= True
	)

	# wrap
	rna_pointer.wrap= BoolProperty(
		name= "Wrap",
		description= "",
		default= True
	)

	# alpha_from_intensity
	rna_pointer.alpha_from_intensity= BoolProperty(
		name= "Alpha from intensity",
		description= "If true, the resulting alpha is the color intensity; otherwise the alpha is taken from the bitmap alpha",
		default= False
	)

	# invert
	rna_pointer.invert= BoolProperty(
		name= "Invert",
		description= "If true, the resulting texture color will be inverted",
		default= False
	)

	# invert_alpha
	rna_pointer.invert_alpha= BoolProperty(
		name= "Invert alpha",
		description= "If true and invert is on, the resulting texture alpha will be inverted too. If false, just the color will be inverted",
		default= True
	)

	# color_mult
	# rna_pointer.color_mult= FloatVectorProperty(
	# 	name= "Color mult",
	# 	description= "A multiplier for the texture color",
	# 	subtype= 'COLOR',
	# 	min= 0.0,
	# 	max= 1.0,
	# 	soft_min= 0.0,
	# 	soft_max= 1.0,
	# 	default= (1,1,1)
	# )
	rna_pointer.color_mult= FloatProperty(
		name= "Color mult",
		description= "A multiplier for the texture color",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 2.0,
		default= 1.0
	)

	# color_offset
	# rna_pointer.color_offset= FloatVectorProperty(
	# 	name= "Color offset",
	# 	description= "An additional offset for the texture color",
	# 	subtype= 'COLOR',
	# 	min= 0.0,
	# 	max= 1.0,
	# 	soft_min= 0.0,
	# 	soft_max= 1.0,
	# 	default= (0,0,0)
	# )
	rna_pointer.color_offset= FloatProperty(
		name= "Color offset",
		description= "An additional offset for the texture color",
		min= -1.0,
		max=  1.0,
		soft_min= -1.0,
		soft_max= 1.0,
		default= 0.0
	)

	# alpha_mult
	rna_pointer.alpha_mult= FloatProperty(
		name= "Alpha mult",
		description= "A multiplier for the texture alpha",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 2.0,
		default= 1.0
	)

	# alpha_offset
	rna_pointer.alpha_offset= FloatProperty(
		name= "Alpha offset",
		description= "An additional offset for the texture alpha",
		min= -1.0,
		max=  1.0,
		soft_min= -1.0,
		soft_max= 1.0,
		default= 0
	)

	# nouvw_color
	rna_pointer.nouvw_color= FloatVectorProperty(
		name= "No UV color",
		description= "The color when there are no valid uvw coordinates",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0.5,0.5,0.5)
	)

	# uvwgen
	rna_pointer.uvwgen= StringProperty(
		name= "UVW generator",
		description= "UVW generator",
		default= ""
	)

	# placement_type
	rna_pointer.placement_type= EnumProperty(
		name= "Placement type",
		description= "Image texure placement type",
		items= (
			('FULL', "Full",  "The whole texture is valid."),
			('CROP', "Crop",  "Crop texture."),
			('PLACE',"Place", "Place texture."),
		),
		default= 'FULL'
	)

	# u
	rna_pointer.u= FloatProperty(
		name= "U",
		description= "U coordinate of the valid texture sector",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	# v
	rna_pointer.v= FloatProperty(
		name= "V",
		description= "V coordinate of the valid texture sector",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	# w
	rna_pointer.w= FloatProperty(
		name= "W",
		description= "Width of the valid texture sector",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# h
	rna_pointer.h= FloatProperty(
		name= "H",
		description= "Height of the valid texture sector",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# jitter
	rna_pointer.jitter= FloatProperty(
		name= "Jitter",
		description= "Amount of random placement variation",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)

	# tile_u
	rna_pointer.tile_u= FloatProperty(
		name        = "Tile U",
		description = "Tile in U",
		min         = 0.0,
		max         = 1000.0,
		soft_min    = 1,
		soft_max    = 20.0,
		default     = 1.0
	)
	rna_pointer.mirror_u= BoolProperty(
		name= "Mirror U",
		description= "Mirror in U",
		default= False
	)

	# tile_v
	rna_pointer.tile_v= FloatProperty(
		name        = "Tile V",
		description = "Tile in V",
		min         = 0.0,
		max         = 1000.0,
		soft_min    = 1.0,
		soft_max    = 20.0,
		default     = 1.0
	)

	rna_pointer.mirror_v= BoolProperty(
		name= "Mirror V",
		description= "Mirror in V",
		default= False
	)

	# uv_noise_on
	rna_pointer.uv_noise_on= BoolProperty(
		name= "Use",
		description= "If true the noise is enabled",
		default= 0
	)

	# uv_noise_animate
	rna_pointer.uv_noise_animate= BoolProperty(
		name= "Animate",
		description= "If true the noise is animated",
		default= False
	)

	# uv_noise_amount
	rna_pointer.uv_noise_amount= FloatProperty(
		name= "Amount",
		description= "UV noise amount",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# uv_noise_levels
	rna_pointer.uv_noise_levels= FloatProperty(
		name= "Levels",
		description= "UV noise iterations",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# uv_noise_size
	rna_pointer.uv_noise_size= FloatProperty(
		name= "Size",
		description= "UV noise size",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# un_noise_phase
	rna_pointer.un_noise_phase= FloatProperty(
		name= "Phase",
		description= "UV noise phase",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0
	)



'''
  OUTPUT
'''
def write(bus):
	PLACEMENT_TYPE= {
		'FULL':  0,
		'CROP':  1,
		'PLACE': 2,
	}
	TILE= {
		'NOTILE': (0,0),
		'TILEUV': (1,1),
		'TILEU':  (1,0),
		'TILEV':  (0,1),
	}

	ofile= bus['files']['textures']
	scene= bus['scene']

	slot=    bus['mtex']['slot']
	texture= bus['mtex']['texture']

	VRayTexture= texture.vray
	VRaySlot=    texture.vray_slot

	if VRayTexture.type not in ('TexFalloff'):
		ofile.write("\n\tplacement_type= %i;" % PLACEMENT_TYPE[VRayTexture.placement_type])
		ofile.write("\n\ttile_u= %d;\n\ttile_v= %d;" % TILE[VRayTexture.tile])
		ofile.write("\n\tu= %s;" % a(scene, VRayTexture.u))
		ofile.write("\n\tv= %s;" % a(scene, VRayTexture.v))
		ofile.write("\n\tw= %s;" % a(scene, VRayTexture.w))
		ofile.write("\n\th= %s;" % a(scene, VRayTexture.h))
		ofile.write("\n\tjitter= %s;" % a(scene, VRayTexture.jitter))
		ofile.write("\n\tuv_noise_on= %s;" % a(scene, VRayTexture.uv_noise_on))
		ofile.write("\n\tuv_noise_animate= %s;" % a(scene, VRayTexture.uv_noise_animate))
		ofile.write("\n\tun_noise_phase= %s;" % a(scene, VRayTexture.un_noise_phase))
		ofile.write("\n\tuv_noise_amount= %s;" % a(scene, VRayTexture.uv_noise_amount))
		ofile.write("\n\tuv_noise_levels= %s;" % a(scene, VRayTexture.uv_noise_levels))
		ofile.write("\n\tuv_noise_size= %s;" % a(scene, VRayTexture.uv_noise_size))

	ofile.write("\n\tinvert= %s;" % a(scene, VRayTexture.invert))
	ofile.write("\n\tcolor_mult= %s;" % a(scene, mathutils.Color([VRayTexture.color_mult]*3)))
	ofile.write("\n\tcolor_offset= %s;" % a(scene, mathutils.Color([VRayTexture.color_offset]*3)))
	ofile.write("\n\tinvert_alpha= %s;" % a(scene, VRayTexture.invert_alpha))
	ofile.write("\n\talpha_mult= %s;" % a(scene, VRayTexture.alpha_mult))
	ofile.write("\n\talpha_offset= %s;" % a(scene, VRayTexture.alpha_offset))
	ofile.write("\n\talpha_from_intensity= %s;" % a(scene, VRayTexture.alpha_from_intensity))
	ofile.write("\n\tnouvw_color= %s;" % a(scene, VRayTexture.nouvw_color))

	if texture.type == 'VRAY':
		if hasattr(VRayTexture, VRayTexture.type):
			TexPlugin= getattr(VRayTexture, VRayTexture.type)

			if hasattr(TexPlugin, 'wrap'):
				ofile.write("\n\twrap= %s;" % a(scene, VRayTexture.wrap))

			if hasattr(TexPlugin, 'use_3d_mapping'):
				ofile.write("\n\tuse_3d_mapping= %s;" % a(scene, VRayTexture.use_3d_mapping))



'''
  GUI
'''
class VRAY_TP_Mapping(ui.VRayTexturePanel, bpy.types.Panel):
	bl_label       = "Mapping"
	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		if not ui.engine_poll(cls, context):
			return False

		tex= context.texture
		if not tex:
			return False

		if tex.type == 'VRAY':
			if tex.vray.type != 'NONE' and tex.vray.type not in PURE_PROCEDURAL:
				return True

		if tex.type == 'IMAGE':
			if tex.image:
				return True

		return False

	def draw(self, context):
		wide_ui= context.region.width > ui.narrowui
		layout= self.layout

		idblock = ui.context_tex_datablock(context)

		ob=   context.object
		sce=  context.scene

		slot= getattr(context, 'texture_slot', None)
		tex=  slot.texture if slot else context.texture

		VRayTexture= tex.vray
		VRaySlot=    tex.vray_slot

		TexPlugin= getattr(VRayTexture, VRayTexture.type) if tex.type == 'VRAY' else None

		if issubclass(type(idblock), bpy.types.Material):
			if wide_ui:
				layout.prop(VRayTexture, 'texture_coords', expand=True)
			else:
				layout.prop(VRayTexture, 'texture_coords')

			if VRayTexture.texture_coords == 'UV':
				if slot:
					split= layout.split(percentage=0.3)
					split.label(text="Layer:")
					if ob and ob.type == 'MESH':
						split.prop_search(slot,    'uv_layer',
										  ob.data, 'uv_textures',
										  text="")
					else:
						split.prop(slot, 'uv_layer', text="")
			elif VRayTexture.texture_coords == 'ORCO':
				split= layout.split(percentage=0.3)
				split.label(text="Projection:")
				split.prop(VRayTexture, 'mapping', text="")
				split= layout.split(percentage=0.3)
				split.label(text="Object:")
				split.prop_search(VRayTexture, 'object',
								  sce,         'objects',
								  text="")

			if slot:
				split= layout.split()
				col= split.column()
				col.label(text="Offset:")
				if wide_ui:
					sub= col.row()
				else:
					sub= col.column()
				sub.prop(slot, 'offset', text="")

				split= layout.split()
				col= split.column()
				col.label(text="Scale:")
				if wide_ui:
					sub= col.row()
				else:
					sub= col.column()
				sub.prop(slot, 'scale', text="")

			layout.separator()

			split= layout.split()
			col= split.column()
			col.prop(VRaySlot, 'texture_rot')
			if wide_ui:
				col= split.column()
			col.prop(VRayTexture, 'jitter')

			layout.separator()

			split= layout.split()
			col= split.column()
			if TexPlugin:
				if hasattr(TexPlugin, 'use_3d_mapping') or hasattr(TexPlugin, 'wrap'):
					layout.separator()
				if hasattr(TexPlugin, 'use_3d_mapping'):
					col.prop(VRayTexture, 'use_3d_mapping')
				if wide_ui:
					col= split.column()
				if hasattr(TexPlugin, 'wrap'):
					col.prop(VRayTexture, 'wrap')

			box= layout.box()
			box.prop(VRayTexture, 'uv_noise_on', text= "UV noise")
			if VRayTexture.uv_noise_on:
				split= box.split()
				split.active= VRayTexture.uv_noise_on
				col= split.column()
				col.prop(VRayTexture, 'uv_noise_animate')
				col.prop(VRayTexture, 'un_noise_phase')
				if wide_ui:
					col= split.column()
				col.prop(VRayTexture, 'uv_noise_amount')
				col.prop(VRayTexture, 'uv_noise_levels')
				col.prop(VRayTexture, 'uv_noise_size')

		elif issubclass(type(idblock), bpy.types.World):
			split= layout.split(percentage=0.3)
			split.label(text="Projection:")
			split.prop(VRayTexture, 'environment_mapping', text="")

			layout.label(text="Rotation:")
			split= layout.split()
			col= split.column()
			col.prop(VRaySlot, 'texture_rotation_h', slider= True, text="Horizontal")
			col.prop(VRaySlot, 'texture_rotation_v', slider= True, text="Vertical")
			#col.prop(VRaySlot, 'texture_rotation_w', slider= True, text="X")

		elif issubclass(type(idblock), bpy.types.Lamp):
			split= layout.split(percentage=0.3)
			split.label(text="Projection:")
			split.prop(VRayTexture, 'environment_mapping', text="")

			layout.label(text="Rotation:")
			split= layout.split()
			col= split.column()
			col.prop(VRaySlot, 'texture_rotation_h', slider= True, text="Horizontal")
			col.prop(VRaySlot, 'texture_rotation_v', slider= True, text="Vertical")
			#col.prop(VRaySlot, 'texture_rotation_w', slider= True, text="X")



class VRAY_TP_Tiling(ui.VRayTexturePanel, bpy.types.Panel):
	bl_label       = "Tiling"
	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		if not ui.engine_poll(cls, context):
			return False

		tex= context.texture
		if not tex:
			return False

		if tex.type == 'VRAY':
			if tex.vray.type != 'NONE' and tex.vray.type not in PURE_PROCEDURAL:
				return True

		if tex.type == 'IMAGE':
			if tex.image:
				return True

		return False

	def draw(self, context):
		wide_ui= context.region.width > ui.narrowui
		layout= self.layout

		idblock = ui.context_tex_datablock(context)

		ob=   context.object
		sce=  context.scene

		slot= getattr(context, 'texture_slot', None)
		tex=  slot.texture if slot else context.texture

		VRayTexture= tex.vray
		VRaySlot=    tex.vray_slot

		TexPlugin= getattr(VRayTexture, VRayTexture.type) if tex.type == 'VRAY' else None

		if wide_ui:
			layout.prop(VRayTexture, 'tile', expand=True)
		else:
			layout.prop(VRayTexture, 'tile')

		if VRayTexture.tile != 'NOTILE':
			split = layout.split()
			col= split.column()
			col.label(text="Tile:")
			sub= col.row(align=True)
			sub_u= sub.row()
			sub_u.active= VRayTexture.tile in ('TILEUV','TILEU')
			sub_u.prop(VRayTexture, 'tile_u', text='U')
			sub_v= sub.row()
			sub_v.active= VRayTexture.tile in ('TILEUV','TILEV')
			sub_v.prop(VRayTexture, 'tile_v', text='V')

			if wide_ui:
				col= split.column()

			col.label(text="Mirror:")
			sub= col.row(align=True)
			sub_u= sub.row()
			sub_u.active= VRayTexture.tile in ('TILEUV','TILEU')
			sub_u.prop(VRayTexture, 'mirror_u', text='U')
			sub_v= sub.row()
			sub_v.active= VRayTexture.tile in ('TILEUV','TILEV')
			sub_v.prop(VRayTexture, 'mirror_v', text='V')

		layout.separator()

		if wide_ui:
			layout.prop(VRayTexture, 'placement_type', expand=True)
		else:
			layout.prop(VRayTexture, 'placement_type')

		if VRayTexture.placement_type not in ('FULL'):
			split = layout.split()
			col= split.column()
			col.label(text="Crop Minimum:")
			sub= col.row(align=True)
			sub.prop(VRayTexture, 'u')
			sub.prop(VRayTexture, 'v')
			if wide_ui:
				col= split.column()
			col.label(text="Crop Maximum:")
			sub= col.row(align=True)
			sub.prop(VRayTexture, 'w')
			sub.prop(VRayTexture, 'h')


class VRAY_TP_Common(ui.VRayTexturePanel, bpy.types.Panel):
	bl_label       = "Common"
	COMPAT_ENGINES = {'VRAY_RENDER','VRAY_RENDER_PREVIEW'}

	@classmethod
	def poll(cls, context):
		if not ui.engine_poll(cls, context):
			return False

		tex= context.texture
		if not tex:
			return False

		if tex.type == 'VRAY':
			if tex.vray.type != 'NONE' and tex.vray.type not in PURE_PROCEDURAL:
				return True

		if tex.type == 'IMAGE':
			if tex.image:
				return True

		return False

	def draw(self, context):
		wide_ui= context.region.width > ui.narrowui
		layout= self.layout

		slot= getattr(context, 'texture_slot', None)
		tex=  slot.texture if slot else context.texture

		VRayTexture= tex.vray

		TexPlugin= getattr(VRayTexture, VRayTexture.type) if tex.type == 'VRAY' else None

		split= layout.split()
		col= split.column()
		col.label(text="Color:")
		sub= col.column(align= True)
		sub.prop(VRayTexture, 'color_mult', text="Mult", slider= True)
		sub.prop(VRayTexture, 'color_offset', text="Offset", slider= True)
		col.prop(VRayTexture, 'invert')
		# col.prop(VRayTexture, 'nouvw_color', text="")
		if wide_ui:
			col= split.column()
		col.label(text="Alpha:")
		sub= col.column(align= True)
		sub.prop(VRayTexture, 'alpha_mult', text="Mult", slider= True)
		sub.prop(VRayTexture, 'alpha_offset', text="Offset", slider= True)
		sub= col.column()
		sub.active= VRayTexture.invert
		sub.prop(VRayTexture, 'invert_alpha')
		# col.prop(VRayTexture, 'remove_alpha')
		col.prop(VRayTexture, 'alpha_from_intensity')

		# layout.separator()
		# layout.operator("vray.bake_procedural", icon= 'TEXTURE')


def GetRegClasses():
	return (
		VRAY_TP_Mapping,
		VRAY_TP_Tiling,
		VRAY_TP_Common,
	)


def register():
	for regClass in GetRegClasses():
		bpy.utils.register_class(regClass)


def unregister():
	for regClass in GetRegClasses():
		bpy.utils.unregister_class(regClass)
