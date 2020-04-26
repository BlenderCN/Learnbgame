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
import vb25.texture

from vb25.utils import *
from vb25.ui import ui


TYPE      = 'BRDF'
ID        = 'BRDFHair3'
PID       =  8
MAIN_BRDF =  True

NAME   = 'BRDFHair3'
UI     = "Hair"
DESC   = "Hair material"

PARAMS = (
	'overall_color',
	'transparency',
	'diffuse_color',
	'diffuse_amount',
	'primary_specular',
	'primary_specular_amount',
	'primary_glossiness',
	'secondary_specular',
	'secondary_specular_amount',
	'secondary_glossiness',
	'secondary_lock_to_transmission',
	'transmission',
	'transmission_amount',
	'transmission_glossiness_length',
	'transmission_glossiness_width',
	'opaque_for_shadows',
	'opaque_for_gi',
	'simplify_for_gi',
	'use_cached_gi',
)


def add_properties(rna_pointer):
	class BRDFHair3(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(BRDFHair3) 

	rna_pointer.BRDFHair3= PointerProperty(
		name= "BRDFHair3",
		type=  BRDFHair3,
		description= "V-Ray BRDFHair3 settings"
	)

	# overall_color
	BRDFHair3.overall_color= FloatVectorProperty(
		name= "Overall Color",
		description= "Overall color multiplier",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0.9,0.9,0.9)
	)

	# transparency
	BRDFHair3.transparency= FloatVectorProperty(
		name= "Transparency",
		description= "Controls the transparency of the material where white is opaque and black is fully transparent",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0,0,0)
	)

	# diffuse_color
	BRDFHair3.diffuse_color= FloatVectorProperty(
		name= "Diffuse Color",
		description= "Diffuse hair color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0.01,0.01,0.01)
	)

	# diffuse_amount
	BRDFHair3.diffuse_amount= FloatProperty(
		name= "Diffuse Amount",
		description= "Multiplier for the diffuse color",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# primary_specular
	BRDFHair3.primary_specular= FloatVectorProperty(
		name= "Primary Specular",
		description= "Primary specular color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0.2,0.2,0.2)
	)

	# primary_specular_amount
	BRDFHair3.primary_specular_amount= FloatProperty(
		name= "Primary Specular Amount",
		description= "Multiplier for the primary specular color",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# primary_glossiness
	BRDFHair3.primary_glossiness= FloatProperty(
		name= "Primary Glossiness",
		description= "Primary glossiness",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.8
	)

	# secondary_specular
	BRDFHair3.secondary_specular= FloatVectorProperty(
		name= "Secondary Specular",
		description= "Secondary specular color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0.2,0.2,0.2)
	)

	# secondary_specular_amount
	BRDFHair3.secondary_specular_amount= FloatProperty(
		name= "Secondary Specular Amount",
		description= "Multiplier for the secondary specular color",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# secondary_glossiness
	BRDFHair3.secondary_glossiness= FloatProperty(
		name= "Secondary Glossiness",
		description= "Secondary glossiness",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.5
	)

	# secondary_lock_to_transmission
	BRDFHair3.secondary_lock_to_transmission= BoolProperty(
		name= "Lock To Transmission",
		description= "true to derive the secondary specular color from the transmission color",
		default= True
	)

	# transmission
	BRDFHair3.transmission= FloatVectorProperty(
		name= "Transmission",
		description= "Transmission color",
		subtype= 'COLOR',
		min= 0.0,
		max= 1.0,
		soft_min= 0.0,
		soft_max= 1.0,
		default= (0.2,0.2,0.2)
	)

	# transmission_amount
	BRDFHair3.transmission_amount= FloatProperty(
		name= "Transmission Amount",
		description= "Multiplier for the transmission color",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 1
	)

	# transmission_glossiness_length
	BRDFHair3.transmission_glossiness_length= FloatProperty(
		name= "Transmission Glossiness Length",
		description= "Transmission glossiness along strand length",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.8
	)

	# transmission_glossiness_width
	BRDFHair3.transmission_glossiness_width= FloatProperty(
		name= "Transmission Glossiness Width",
		description= "Transmission glossiness across strand width",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.8
	)

	# opaque_for_shadows
	BRDFHair3.opaque_for_shadows= BoolProperty(
		name= "Opaque For Shadows",
		description= "true to always compute the material as opaque for shadow rays",
		default= False
	)

	# opaque_for_gi
	BRDFHair3.opaque_for_gi= BoolProperty(
		name= "Opaque For GI",
		description= "true to always compute the material as opaque for GI rays",
		default= False
	)

	# simplify_for_gi
	BRDFHair3.simplify_for_gi= BoolProperty(
		name= "Simplify For GI",
		description= "true to use a simpler and less precise representation of the BRDF for GI rays",
		default= False
	)

	# use_cached_gi
	BRDFHair3.use_cached_gi= BoolProperty(
		name= "Use Cached GI",
		description= "true to use the light cache/irradiance map; false to always use brute force GI for the hair",
		default= True
	)



def mapto(bus, BRDFLayered = None):
	return {}


def write(bus, VRayBRDF = None, base_name = None):
	ofile = bus['files']['materials']
	scene = bus['scene']

	ma    = bus['material']['material']

	brdf_name = "%s%s%s" % (ID, get_name(ma, prefix='MA'), bus['material']['orco_suffix'])
	if base_name:
		brdf_name = "%s%s%s" % (base_name, ID, bus['material']['orco_suffix'])
	if VRayBRDF:
		brdf_name += clean_string(VRayBRDF.name)

	BRDFHair3 = getattr(VRayBRDF, ID) if VRayBRDF else ma.vray.BRDFHair3

	ofile.write("\n%s %s {"%(ID,brdf_name))
	for param in PARAMS:
		if param == 'overall_color' and not VRayBRDF:
			value = ma.diffuse_color
		else:
			value = getattr(BRDFHair3,param)
		ofile.write("\n\t%s=%s;"%(param, a(scene,value)))
	ofile.write("\n}\n")

	return brdf_name


def gui(context, layout, BRDFHair3, material = None):
	wide_ui = context.region.width > ui.narrowui

	split = layout.split()
	col = split.column()
	if material:
		col.prop(material, 'diffuse_color', text = "Overall Color")
	else:
		col.prop(BRDFHair3, 'overall_color')
	if wide_ui:
		col = split.column()
	col.prop(BRDFHair3, 'transparency')

	layout.label(text = "Diffuse:")
	split = layout.split()
	col = split.column()
	col.prop(BRDFHair3, 'diffuse_color', text = "")
	if wide_ui:
		col = split.column()
	col.prop(BRDFHair3, 'diffuse_amount', text = "Amount")

	layout.label(text = "Primary specular:")
	split = layout.split()
	col = split.column()
	col.prop(BRDFHair3, 'primary_specular', text = "")
	if wide_ui:
		col = split.column()
	col.prop(BRDFHair3, 'primary_specular_amount', text = "Amount")
	col.prop(BRDFHair3, 'primary_glossiness', text = "Glossiness")

	layout.label(text = "Secondary specular:")
	split = layout.split()
	col = split.column()
	col.prop(BRDFHair3, 'secondary_specular', text = "")
	col.prop(BRDFHair3, 'secondary_lock_to_transmission')
	if wide_ui:
		col = split.column()
	col.prop(BRDFHair3, 'secondary_specular_amount', text = "Amount")
	col.prop(BRDFHair3, 'secondary_glossiness', text = "Glossiness")

	layout.label(text = "Transmission:")
	split = layout.split()
	col = split.column()
	col.prop(BRDFHair3, 'transmission', text = "")
	col.prop(BRDFHair3, 'transmission_amount', text = "Amount")
	if wide_ui:
		col = split.column()
	col.prop(BRDFHair3, 'transmission_glossiness_length', text = "Length")
	col.prop(BRDFHair3, 'transmission_glossiness_width', text = "Width")

	layout.label(text = "Options:")
	split = layout.split()
	col = split.column()
	col.prop(BRDFHair3, 'opaque_for_shadows')
	col.prop(BRDFHair3, 'opaque_for_gi')
	if wide_ui:
		col = split.column()
	col.prop(BRDFHair3, 'simplify_for_gi')
	col.prop(BRDFHair3, 'use_cached_gi')
