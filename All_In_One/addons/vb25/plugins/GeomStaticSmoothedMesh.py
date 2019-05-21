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
  along with this program.	If not, see <http://www.gnu.org/licenses/>.

  All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.

'''


''' Blender modules '''
import bpy
from bpy.props import *

''' vb modules '''
from vb25.utils import *
from vb25.ui import ui


TYPE= 'GEOMETRY'
ID=	  'GeomStaticSmoothedMesh'

NAME= 'Subdivision'
DESC= "Subdivision surface settings."

PARAMS= (
	'use_globals',
	'view_dep',
	'edge_length',
	'max_subdivs',
	'static_subdiv',
)

def add_properties(rna_pointer):
	class GeomStaticSmoothedMesh(bpy.types.PropertyGroup):
		pass
	bpy.utils.register_class(GeomStaticSmoothedMesh)

	rna_pointer.GeomStaticSmoothedMesh= PointerProperty(
		name= "GeomStaticSmoothedMesh",
		type=  GeomStaticSmoothedMesh,
		description= "GeomStaticSmoothedMesh texture slot settings"
	)

	GeomStaticSmoothedMesh.use= BoolProperty(
		name= "Override displacement settings",
		description= "Override material displacement settings",
		default= False
	)

	GeomStaticSmoothedMesh.use_globals= BoolProperty(
		name= "Use globals",
		description= "If true, the global displacement quality settings will be used",
		default= True
	)

	GeomStaticSmoothedMesh.view_dep= BoolProperty(
		name= "View dependent",
		description= "Determines if view-dependent tesselation is used",
		default= True
	)

	GeomStaticSmoothedMesh.edge_length= FloatProperty(
		name= "Edge length",
		description= "Determines the approximate edge length for the sub-triangles",
		min= 0.0,
		max= 100.0,
		soft_min= 0.0,
		soft_max= 10.0,
		precision= 3,
		default= 4
	)

	GeomStaticSmoothedMesh.max_subdivs= IntProperty(
		name= "Max subdivs",
		description= "Determines the maximum subdivisions for a triangle of the original mesh",
		min= 0,
		max= 2048,
		soft_min= 0,
		soft_max= 1024,
		default= 256
	)

	GeomStaticSmoothedMesh.static_subdiv= BoolProperty(
		name= "Static subdivision",
		description= "True if the resulting triangles of the subdivision algorithm will be inserted into the rayserver as static geometry",
		default= False
	)



def write(bus):
	ofile= bus['files']['nodes']
	scene= bus['scene']

	ob=	   bus['node']['object']
	me=	   bus['node']['geometry']
	
	VRayScene= scene.vray
	VRayExporter= VRayScene.exporter

	if not VRayExporter.use_displace:
		return
		
	VRayObject= ob.vray
	GeomStaticSmoothedMesh= VRayObject.GeomStaticSmoothedMesh

	slot= None
	if bus['node'].get('displacement_slot'):
		slot= bus['node']['displacement_slot']
		if slot:
			VRaySlot=	slot.texture.vray_slot
			VRayObject= ob.vray

			GeomDisplacedMesh=	        VRaySlot.GeomDisplacedMesh
			ObjectDisplacementOverride= VRayObject.GeomDisplacedMesh

			# Keep original amount from texture
			displacement_amount= GeomDisplacedMesh.displacement_amount

	if GeomStaticSmoothedMesh.use:
		subdiv_name= 'SBDV'+me
		if slot and ObjectDisplacementOverride.use:
			subdiv_name= get_name(ob, prefix='SBDVDOB')
			GeomDisplacedMesh= ObjectDisplacementOverride

		if not append_unique(bus['cache']['displace'], subdiv_name):
			return subdiv_name

		ofile.write("\nGeomStaticSmoothedMesh %s {" % subdiv_name)
		ofile.write("\n\tmesh= %s;" % me)
		if slot:
			ofile.write("\n\tdisplacement_tex_float= %s;" % bus['node']['displacement_texture'])
			ofile.write("\n\tdisplacement_tex_color= %s;" % bus['node']['displacement_texture'])
			if ObjectDisplacementOverride.use:
				if ObjectDisplacementOverride.amount_type == 'OVER':
					displacement_amount= ObjectDisplacementOverride.displacement_amount
				else:
					displacement_amount*= ObjectDisplacementOverride.amount_mult
			ofile.write("\n\tdisplacement_amount= %s;" % a(scene, displacement_amount))
			for param in ('displacement_shift',
						  'keep_continuity',
						  'water_level',
						  'use_bounds',
						  'min_bound',
						  'max_bound'):
				if param in ('min_bound', 'max_bound'):
					value= "Color(%.3f,%.3f,%.3f)" % (tuple([getattr(GeomDisplacedMesh, param)]*3))
				else:
					value= getattr(GeomDisplacedMesh, param)
				ofile.write("\n\t%s= %s;" % (param, a(scene,value)))

		for param in PARAMS:
			value= getattr(GeomStaticSmoothedMesh, param)
			ofile.write("\n\t%s= %s;" % (param, a(scene,value)))

		ofile.write("\n}\n")

		bus['node']['geometry']= subdiv_name


def influence(context, layout, slot):
	pass
