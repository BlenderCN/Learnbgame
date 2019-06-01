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


TYPE= 'GEOMETRY'
ID=   'GeomDisplacedMesh'

NAME= 'Displace'
DESC= "Displace settings."

PARAMS= (
	'displacement_amount',
	'displacement_shift',
	'water_level',
	'use_globals',
	'view_dep',
	'edge_length',
	'max_subdivs',
	'keep_continuity',
	'map_channel',
	'use_bounds',
	'min_bound',
	'max_bound',
	'resolution',
	'precision',
	'tight_bounds',
	'filter_texture',
	'filter_blur'
)

def add_properties(rna_pointer):
	class GeomDisplacedMesh(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(GeomDisplacedMesh)

	rna_pointer.GeomDisplacedMesh= PointerProperty(
		name= "GeomDisplacedMesh",
		type=  GeomDisplacedMesh,
		description= "GeomDisplacedMesh texture slot settings"
	)

	GeomDisplacedMesh.use= BoolProperty(
		name= "Override displacement settings",
		description= "Override material displacement settings",
		default= False
	)

	GeomDisplacedMesh.type= EnumProperty(
		name= "Type",
		description= "Displacement type",
		items= (
			('2D',  "2D",     "2D displacement."),
			('NOR', "Normal", "Normal displacement."),
			('3D',  "Vector", "Vector displacement.")
		),
		default= 'NOR'
	)

	GeomDisplacedMesh.amount_type= EnumProperty(
		name= "Amount type",
		description= "Displacement amount type",
		items= (
			('MULT', "Multiply", "Multiply material amount."),
			('OVER', "Override", "Override material amount.")
		),
		default= 'OVER'
	)

	GeomDisplacedMesh.displacement_amount= FloatProperty(
		name= "Amount",
		description= "Displacement amount",
		min= -100.0,
		max= 100.0,
		soft_min= -0.1,
		soft_max= 0.1,
		precision= 5,
		default= 0.02
	)

	GeomDisplacedMesh.amount_mult= FloatProperty(
		name= "Mult",
		description= "Displacement amount multiplier",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 2.0,
		precision= 3,
		default= 1.0
	)

	GeomDisplacedMesh.displacement_shift= FloatProperty(
		name="Shift",
		description="",
		min=-100.0,
		max=100.0,
		soft_min=-1.0,
		soft_max=1.0,
		precision=4,
		default=0.0
	)

	GeomDisplacedMesh.water_level= FloatProperty(
		name="Water level",
		description="",
		min=-1000.0, max=1000.0, soft_min=-1.0, soft_max=1.0,
		default=-1.0
	)

	GeomDisplacedMesh.use_globals= BoolProperty(
		name= "Use globals",
		description= "If true, the global displacement quality settings will be used",
		default= True
	)

	GeomDisplacedMesh.view_dep= BoolProperty(
		name= "View dependent",
		description= "Determines if view-dependent tesselation is used",
		default= True
	)

	GeomDisplacedMesh.edge_length= FloatProperty(
		name= "Edge length",
		description= "Determines the approximate edge length for the sub-triangles",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 4
	)

	GeomDisplacedMesh.max_subdivs= IntProperty(
		name= "Max subdivs",
		description= "Determines the maximum subdivisions for a triangle of the original mesh",
		min= 0,
		max= 2048,
		soft_min= 0,
		soft_max= 1024,
		default= 256
	)

	GeomDisplacedMesh.keep_continuity= BoolProperty(
		name= "Keep continuity",
		description= "If true, the plugin will attempt to keep the continuity of the displaced surface",
		default= False
	)

	GeomDisplacedMesh.map_channel= IntProperty(
		name= "Map channel",
		description= "The mapping channel to use for vector and 2d displacement",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 1
	)

	GeomDisplacedMesh.use_bounds= BoolProperty(
		name= "Use bounds",
		description= "If true, the min/max values for the displacement texture are specified by the min_bound and max_bound parameters; if false, these are calculated automatically",
		default= False
	)

	# GeomDisplacedMesh.min_bound= FloatVectorProperty(
	# 	name= "Min bound",
	# 	description= "The lowest value for the displacement texture",
	# 	subtype= 'COLOR',
	# 	min= 0.0,
	# 	max= 1.0,
	# 	soft_min= 0.0,
	# 	soft_max= 1.0,
	# 	default= (0,0,0)
	# )

	# GeomDisplacedMesh.max_bound= FloatVectorProperty(
	# 	name= "Max bound",
	# 	description= "The biggest value for the displacement texture",
	# 	subtype= 'COLOR',
	# 	min= 0.0,
	# 	max= 1.0,
	# 	soft_min= 0.0,
	# 	soft_max= 1.0,
	# 	default= (1,1,1)
	# )

	GeomDisplacedMesh.min_bound= FloatProperty(
		name= "Min bound",
		description= "The lowest value for the displacement texture",
		min= -1.0,
		max=  1.0,
		soft_min= -1.0,
		soft_max=  1.0,
		default= 0.0
	)

	GeomDisplacedMesh.max_bound= FloatProperty(
		name= "Max bound",
		description= "The biggest value for the displacement texture",
		min= -1.0,
		max=  1.0,
		soft_min= -1.0,
		soft_max=  1.0,
		default= 1.0
	)

	GeomDisplacedMesh.resolution= IntProperty(
		name= "Resolution",
		description= "Resolution at which to sample the displacement map for 2d displacement",
		min= 1,
		max= 100000,
		soft_min= 1,
		soft_max= 2048,
		default= 256
	)

	GeomDisplacedMesh.precision= IntProperty(
		name= "Precision",
		description= "Increase for curved surfaces to avoid artifacts",
		min= 0,
		max= 100,
		soft_min= 0,
		soft_max= 10,
		default= 8
	)

	GeomDisplacedMesh.tight_bounds= BoolProperty(
		name= "Tight bounds",
		description= "When this is on, initialization will be slower, but tighter bounds will be computed for the displaced triangles making rendering faster",
		default= False
	)

	GeomDisplacedMesh.filter_texture= BoolProperty(
		name= "Filter texture",
		description= "Filter the texture for 2d displacement",
		default= False
	)

	GeomDisplacedMesh.filter_blur= FloatProperty(
		name= "Blur",
		description= "The amount of UV space to average for filtering purposes. A value of 1.0 will average the whole texture",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 0.001
	)


def write(bus):
	ofile= bus['files']['nodes']
	scene= bus['scene']

	ob=    bus['node']['object']
	me=    bus['node']['geometry']

	VRayScene= scene.vray
	VRayExporter= VRayScene.exporter

	if not (bus['node'].get('displacement_slot') and VRayExporter.use_displace):
		return

	slot= bus['node']['displacement_slot']

	VRaySlot=            slot.texture.vray_slot
	GeomDisplacedMesh=   VRaySlot.GeomDisplacedMesh
	displacement_amount= GeomDisplacedMesh.displacement_amount

	VRayObject=                 ob.vray
	ObjectDisplacementOverride= VRayObject.GeomDisplacedMesh

	displace_name= 'D'+me
	if ObjectDisplacementOverride.use:
		displace_name= get_name(ob, prefix='DOB')
		GeomDisplacedMesh= ObjectDisplacementOverride

	if not append_unique(bus['cache']['displace'], displace_name):
		return displace_name

	ofile.write("\nGeomDisplacedMesh %s {" % displace_name)
	ofile.write("\n\tmesh= %s;" % me)
	ofile.write("\n\tdisplacement_tex_float= %s;" % bus['node']['displacement_texture'])
	ofile.write("\n\tdisplacement_tex_color= %s;" % bus['node']['displacement_texture'])
	if GeomDisplacedMesh.type == '2D':
		ofile.write("\n\tdisplace_2d= 1;")
	elif GeomDisplacedMesh.type == '3D':
		ofile.write("\n\tvector_displacement= 1;")
	else:
		ofile.write("\n\tdisplace_2d= 0;")
		ofile.write("\n\tvector_displacement= 0;")
	for param in PARAMS:
		if param == 'displacement_amount':
			if ob.vray.GeomDisplacedMesh.use:
				if GeomDisplacedMesh.amount_type == 'OVER':
					value= GeomDisplacedMesh.displacement_amount
				else:
					value= GeomDisplacedMesh.amount_mult * displacement_amount
			else:
				value= displacement_amount
		elif param in ('min_bound', 'max_bound'):
			value= "Color(%.3f,%.3f,%.3f)" % (tuple([getattr(GeomDisplacedMesh, param)]*3))
		else:
			value= getattr(GeomDisplacedMesh, param)
		ofile.write("\n\t%s= %s;" % (param, a(scene,value)))
	ofile.write("\n}\n")

	bus['node']['geometry']= displace_name


def influence(context, layout, slot):
	wide_ui= context.region.width > ui.narrowui

	VRaySlot= slot.texture.vray_slot

	GeomDisplacedMesh= VRaySlot.GeomDisplacedMesh

	layout.label(text="Geometry:")

	split= layout.split()
	col= split.column()
	ui.factor_but(col, VRaySlot, 'map_displacement', 'displacement_mult', "Displace")
	if wide_ui:
		col= split.column()
	col.active= VRaySlot.map_displacement
	col.prop(GeomDisplacedMesh, 'type')
	col.prop(GeomDisplacedMesh, 'displacement_amount', slider=True)
