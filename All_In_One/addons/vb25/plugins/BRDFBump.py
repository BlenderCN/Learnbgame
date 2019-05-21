'''

  V-Ray/Blender 2.5

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


TYPE= 'BRDF'
ID=   'BRDFBump'

NAME= 'Bump'
DESC= "V-Ray bump shader."

PARAMS= (
)

def add_properties(rna_pointer):
	class BRDFBump(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(BRDFBump)

	rna_pointer.BRDFBump= PointerProperty(
		name= "BRDFBump",
		type=  BRDFBump,
		description= "BRDFBump texture slot settings"
	)

	BRDFBump.map_type= EnumProperty(
		name= "Map type",
		description= "Normal map type",
		items= (
			('EXPLICIT', "Explicit Normal",   "."),
			('FROMBUMP', "From Bump",         "."),
			('WORLD',    "Normal (world)",    "."),
			('CAMERA',   "Normal (camera)",   "."),
			('OBJECT',   "Normal (object)",   "."),
			('TANGENT',  "Normal (tangent)" , "."),
			('BUMP',     "Bump",              "."),
		),
		default= 'BUMP'
	)

	BRDFBump.bump_tex_mult= FloatProperty(
		name= "Amount",
		description= "Bump amount",
		min= -100.0,
		max=  100.0,
		soft_min= -0.2,
		soft_max=  0.2,
		precision= 4,
		default= 0.02
	)

	BRDFBump.bump_shadows= BoolProperty(
		name= "Bump shadows",
		description= "Offset the surface shading point, in addition to the normal",
		default= False
	)

	BRDFBump.compute_bump_for_shadows= BoolProperty(
		name= "Transparent bump shadows",
		description= "True to compute bump mapping for shadow rays in case the material is transparent; false to skip the bump map for shadow rays (faster rendering)",
		default= True
	)



def write(bus, base_brdf = None, use_bump = False):
	MAP_TYPE= {
		'EXPLICIT': 6,
		'FROMBUMP': 5,
		'WORLD':    4,
		'CAMERA':   3,
		'OBJECT':   2,
		'TANGENT':  1,
		'BUMP'   :  0,
	}

	ofile = bus['files']['materials']
	scene = bus['scene']

	textures = bus['textures']
	slot     = bus['material'].get('bump_slot' if use_bump else 'normal_slot')
	uvwgen   = 'bump_uvwgen' if use_bump else 'normal_uvwgen'

	# if uvwgen not in bus['material']:
	# 	return base_brdf

	if base_brdf is None:
		base_brdf = bus['brdf']

	if slot and textures.get('bump' if use_bump else 'normal'):
		VRayTexture = slot.texture.vray
		VRaySlot    = slot.texture.vray_slot

		BRDFBump    = VRaySlot.BRDFBump

		# Check if normal mapping requested
		if BRDFBump.map_type == 'BUMP' and not use_bump:
			return base_brdf

		suffix = 'NO'
		mapto  = 'normal'
		if BRDFBump.map_type == 'BUMP': # Bump
			suffix = 'BUMP'
			mapto  = 'bump'

		brdf_name= "BRDFBump_%s_%s" % (base_brdf, suffix)

		ofile.write("\nBRDFBump %s {" % brdf_name)
		ofile.write("\n\tbase_brdf= %s;" % base_brdf)
		ofile.write("\n\tmap_type= %d;" % MAP_TYPE[BRDFBump.map_type])
		ofile.write("\n\tbump_tex_color= %s;" % textures[mapto])
		ofile.write("\n\tbump_tex_float= %s;" % textures[mapto])
		ofile.write("\n\tbump_tex_mult= %s;" % a(scene,BRDFBump.bump_tex_mult))
		if uvwgen in bus['material']:
		  ofile.write("\n\tnormal_uvwgen= %s;" % bus['material'][uvwgen])
		ofile.write("\n\tbump_shadows= %d;" % BRDFBump.bump_shadows)
		ofile.write("\n\tcompute_bump_for_shadows= %d;" % BRDFBump.compute_bump_for_shadows)
		ofile.write("\n}\n")

		return brdf_name

	return base_brdf



def influence(context, layout, slot):
	wide_ui= context.region.width > ui.narrowui

	VRaySlot= slot.texture.vray_slot
	BRDFBump= VRaySlot.BRDFBump

	layout.separator()

	layout.label(text="Bump / Normal:")

	split= layout.split()
	col= split.column()
	row= col.row(align=True)
	row.prop(VRaySlot, 'map_normal', text="")
	sub= row.row(align=True)
	sub.active= VRaySlot.map_normal
	sub.prop(VRaySlot, 'normal_mult', slider=True, text="Normal")
	sub.prop(VRaySlot, 'map_normal_invert', text="")

	if wide_ui:
		col= split.column()

	col.active= VRaySlot.map_normal
	col.prop(BRDFBump, 'map_type', text= "Type")
	col.prop(BRDFBump, 'bump_tex_mult', slider= True)
	col.prop(BRDFBump, 'bump_shadows')
	col.prop(BRDFBump, 'compute_bump_for_shadows')


def gui():
	pass


def draw():
	pass
