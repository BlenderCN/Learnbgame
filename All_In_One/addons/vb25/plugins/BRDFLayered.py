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
import vb25.texture

from vb25.utils import *
from vb25.ui import ui
from vb25.plugins import *


TYPE= 'BRDF'
ID=   'BRDFLayered'
PID=   200 # BRDFLayered must be last
MAIN_BRDF= True

NAME= "BRDFLayered"
UI=   "Layered"
DESC= "BRDFLayered"

PARAMS= (
	'brdfs',
	'weights',
	'transparency',
	'transparency_tex',
	'transparency_tex_mult',
	'additive_mode',
	'channels',
)


def add_properties(rna_pointer):
	class VRayBRDF(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(VRayBRDF)

	class BRDFLayered(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(BRDFLayered)

	rna_pointer.BRDFLayered= PointerProperty(
		name= "BRDFLayered",
		type=  BRDFLayered,
		description= "V-Ray BRDFLayered settings"
	)

	# brdfs
	BRDFLayered.brdfs= CollectionProperty(
		name= "BRDFs",
		type=  VRayBRDF,
		description= "Material shaders collection"
	)

	BRDFLayered.brdf_selected= IntProperty(
		name= "Selected BRDF",
		description= "Selected BRDF",
		default= -1,
		min= -1,
		max= 100
	)

	brdfs= gen_menu_items(PLUGINS['BRDF'], none_item= False)

	VRayBRDF.type= EnumProperty(
		name= "BRDF Type",
		description= "BRDF type",
		items= (tuple(brdfs)),
		default= brdfs[4][0] # BRDFDiffuse
	)

	VRayBRDF.use= BoolProperty(
		name= "",
		description= "Use BRDF",
		default= True
	)

	# weights List()
	VRayBRDF.weight= FloatVectorProperty(
		name= "Weight",
		description= "Weight",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (1.0,1.0,1.0)
	)

	VRayBRDF.weight_tex= StringProperty(
		name= "Weight texture",
		description= "Weight texture",
		default= ""
	)


	# transparency
	BRDFLayered.transparency= FloatVectorProperty(
		name= "Transparency",
		description= "",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0,0,0)
	)

	# transparency_tex
	BRDFLayered.transparency_tex= StringProperty(
		name= "Transparency",
		description= "",
		default= ""
	)

	BRDFLayered.map_transparency_tex= BoolProperty(
		name= "transparency tex",
		description= "",
		default= False
	)

	# transparency_tex_mult
	BRDFLayered.transparency_tex_mult= FloatProperty(
		name= "transparency tex mult",
		description= "",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# additive_mode
	BRDFLayered.additive_mode= BoolProperty(
		name= "Additive \"shellac\" mode",
		description= "Additive \"shellac\" blending mode",
		default= False
	)

	# channels List()

	return VRayBRDF



'''
  OUTPUT
'''
def mapto(bus, BRDFPlugin= None):
	scene= bus['scene']
	ma=    bus['material']['material']

	defaults= {}
	defaults['normal']=       ("AColor(0.0,0.0,0.0,1.0)", 0, 'NONE')
	defaults['displacement']= ("AColor(0.0,0.0,0.0,1.0)", 0, 'NONE')

	return defaults


def write(bus, VRayBRDF= None, base_name= None):
	ofile= bus['files']['materials']
	scene= bus['scene']

	material=     bus['material']['material']
	VRayMaterial= material.vray

	brdf_name= "%s%s%s" % (ID, get_name(material, prefix='MA'), bus['material']['orco_suffix'])
	if base_name:
		brdf_name= "%s%s%s" % (base_name, ID, bus['material']['orco_suffix'])
	if VRayBRDF:
		brdf_name+= clean_string(VRayBRDF.name)

	BRDFLayered= getattr(VRayBRDF, 'BRDFLayered') if VRayBRDF else getattr(VRayMaterial, 'BRDFLayered')

	if not BRDFLayered.brdfs:
		return bus['defaults']['brdf']

	brdfs=   []
	weights= []
	for i,brdf in enumerate(BRDFLayered.brdfs):
		brdfs.append(PLUGINS['BRDF'][brdf.type].write(bus, brdf, base_name= "%s%.2i" % (brdf_name,i)))

		weight_param= None
		if brdf.weight_tex:
			weight_param= vb25.texture.write_subtexture(bus, brdf.weight_tex)
		else:
			weight_param= "W%sI%i"%(brdfs[i],i)
			ofile.write("\nTexAColor %s {" % (weight_param))
			ofile.write("\n\ttexture= %s;" % ("AColor(%.3f,%.3f,%.3f,1.0)" % tuple(brdf.weight)))
			ofile.write("\n}\n")

		if weight_param is not None:
			weights.append(weight_param)
		else:
			weights.append("TEDefaultBlend")

	if len(brdfs) == 1:
		return brdfs[0]

	ofile.write("\nBRDFLayered %s {" % brdf_name)
	ofile.write("\n\tbrdfs= List(%s);" % ','.join(brdfs))
	ofile.write("\n\tweights= List(%s);" % ','.join(weights))
	ofile.write("\n\ttransparency= %s;" % p(BRDFLayered.transparency))
	ofile.write("\n\tadditive_mode= %s;" % p(BRDFLayered.additive_mode))
	ofile.write("\n}\n")

	return brdf_name



'''
  GUI
'''
def influence(context, layout, slot):
	wide_ui= context.region.width > ui.narrowui

	VRaySlot= slot.texture.vray_slot

def gui(context, layout, BRDFLayered, material= None):
	wide_ui= context.region.width > ui.narrowui

	row= layout.row()
	row.template_list("VRayListUse", "",
					  BRDFLayered, 'brdfs',
					  BRDFLayered, 'brdf_selected',
					  rows = 3)

	col= row.column()
	sub= col.row()
	subsub= sub.column(align=True)
	subsub.operator('vray.brdf_add',    text="", icon="ZOOMIN")
	subsub.operator('vray.brdf_remove', text="", icon="ZOOMOUT")
	sub= col.row()
	subsub= sub.column(align=True)
	subsub.operator("vray.brdf_up",   icon='MOVE_UP_VEC',   text="")
	subsub.operator("vray.brdf_down", icon='MOVE_DOWN_VEC', text="")

	split= layout.split()
	col= split.column()
	col.prop(BRDFLayered, 'additive_mode')

	layout.label(text="Transparency:")
	split= layout.split()
	row= split.row(align=True)
	row.prop(BRDFLayered, 'transparency', text="")
	if not wide_ui:
		row= split.column()
	row.prop_search(BRDFLayered, 'transparency_tex',
					bpy.data, 'textures',
					text= "")
	if BRDFLayered.transparency_tex:
		row.prop(BRDFLayered, 'transparency_tex_mult', text="Mult")

	# col.prop(BRDFLayered, 'channels')

	if BRDFLayered.brdf_selected >= 0:
		layout.separator()

		brdf= BRDFLayered.brdfs[BRDFLayered.brdf_selected]

		if wide_ui:
			split= layout.split(percentage=0.2)
		else:
			split= layout.split()
		col= split.column()
		col.label(text="Name:")
		if wide_ui:
			col= split.column()
		row= col.row(align=True)
		row.prop(brdf, 'name', text="")

		if wide_ui:
			split= layout.split(percentage=0.2)
		else:
			split= layout.split()
		col= split.column()
		col.label(text="Type:")
		if wide_ui:
			col= split.column()
		col.prop(brdf, 'type', text="")

		if wide_ui:
			split= layout.split(percentage=0.2)
		else:
			split= layout.split()
		col= split.column()
		col.label(text="Weight:")
		if wide_ui:
			col= split.row(align=True)
		else:
			col= col.column(align=True)
		col.prop(brdf, 'weight', text="")
		col.prop_search(brdf, 'weight_tex',
						bpy.data, 'textures',
						text= "")

		layout.separator()

		box = layout.box()
		box.active = brdf.use

		rna_pointer= getattr(brdf, brdf.type)
		if rna_pointer:
			plugin= PLUGINS['BRDF'].get(brdf.type)
			if plugin:
				plugin.gui(context, box, rna_pointer)
