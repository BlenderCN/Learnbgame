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
ID=   'GeomStaticMesh'

NAME= 'Mesh'
DESC= "Mesh settings."

PARAMS= (
	'dynamic_geometry',
)


def add_properties(rna_pointer):
	class GeomStaticMesh(bpy.types.PropertyGroup):
		dynamic_geometry = BoolProperty(
			name        = "Dynamic geometry",
			description = "Instead of copying the mesh many times in the BSP tree, only the bounding box will be present many times and ray intersections will occur in a separate object space BSP tree",
			default     =  False
		)
		use_for_ptex = BoolProperty(
			name        = "Use For PTex",
			description = "Turn this option on if this object will be used with PTex",
			default     =  False
		)
	bpy.utils.register_class(GeomStaticMesh)

	rna_pointer.GeomStaticMesh= PointerProperty(
		name= "V-Ray Satic Mesh",
		type=  GeomStaticMesh,
		description= "V-Ray static mesh settings"
	)


def write_mesh_hex(bus):
	ofile=   bus['files']['geometry'][0]
	scene=   bus['scene']
	ob=      bus['node']['object']
	me=      bus['node']['mesh']
	me_name= bus['node']['mesh_name']

	GeomStaticMesh= ob.data.vray.GeomStaticMesh
	
	face_attr = 'faces' if 'faces' in dir(me) else 'polygons'

	face_tri= (0,1,2,2,3,0)
	
	ofile.write("\nGeomStaticMesh %s {" % me_name)

	ofile.write("\n\tvertices= interpolate((%d, ListVectorHex(\""%(scene.frame_current))
	for v in me.vertices:
		for c in v.co:
			ofile.write(HexFormat(c))
	ofile.write("\")));")

	ofile.write("\n\tfaces= interpolate((%d, ListIntHex(\""%(scene.frame_current))
	for f in getattr(me, face_attr):
		if len(f.vertices) == 4:
			for i in face_tri:
				ofile.write(HexFormat(f.vertices[i]))
		else:
			for v in f.vertices:
				ofile.write(HexFormat(v))
	ofile.write("\")));")

	ofile.write("\n\tface_mtlIDs= ListIntHex(\"")
	for f in getattr(me, face_attr):
		if len(f.vertices) == 4:
			ofile.write(HexFormat(f.material_index + 1))
			ofile.write(HexFormat(f.material_index + 1))
		else:
			ofile.write(HexFormat(f.material_index + 1))
	ofile.write("\");")

	ofile.write("\n\tnormals= interpolate((%d, ListVectorHex(\""%(scene.frame_current))
	for f in getattr(me, face_attr):
		if len(f.vertices) == 4:
			vertices= face_tri
		else:
			vertices= (0,1,2)

		for v in vertices:
			if f.use_smooth:
				for c in me.vertices[f.vertices[v]].normal:
					ofile.write(HexFormat(c))
			else:
				for c in f.normal:
					ofile.write(HexFormat(c))
	ofile.write("\")));")

	ofile.write("\n\tfaceNormals= ListIntHex(\"")
	k= 0
	for f in getattr(me, face_attr):
		if len(f.vertices) == 4:
			vertices= 6
		else:
			vertices= 3

		for v in range(vertices):
			ofile.write(HexFormat(k))
			k+= 1
	ofile.write("\");")


	def edge_visibility(k, ev):
		if k == 9:
			ofile.write(HexFormat(int(ev, 2)))
			return 0, ""
		return k + 1, ev

	ofile.write("\n\tedge_visibility= ListIntHex(\"")

	k= 0
	ev= ""
	if len(getattr(me, face_attr)) < 5:
		for f in getattr(me, face_attr):
			if len(f.vertices) == 4:
				ev+= "011011"
			else:
				ev+= "111"
		edge_visibility(k, ev)
	else:
		k= 0;
		for f in getattr(me, face_attr):
			if len(f.vertices) == 4:
				ev+= "011"
				k, ev = edge_visibility(k, ev)
				ev+= "011"
				k, ev = edge_visibility(k, ev)
			else:
				ev+= "111"
				k, ev = edge_visibility(k, ev)
		if k:
			edge_visibility(k, ev)
	ofile.write("\");")

	uv_textures = me.tessface_uv_textures if 'tessface_uv_textures' in dir(me) else me.uv_textures

	if len(uv_textures):
		ofile.write("\n\tmap_channels= List(")

		for uv_texture_idx,uv_texture in enumerate(uv_textures):
			if uv_texture_idx:
				ofile.write(",")

			uv_layer_index= get_uv_layer_id(bus['uvs'], uv_texture.name)

			ofile.write("\n\t\t// %s"%(uv_texture.name))
			ofile.write("\n\t\tList(%d,ListVectorHex(\""%(uv_layer_index))

			for face in uv_texture.data:
				for uv in face.uv:
					ofile.write(HexFormat(uv[0]))
					ofile.write(HexFormat(uv[1]))
					ofile.write(HexFormat(0.0))

			ofile.write("\"),ListIntHex(\"")

			k= 0
			for face in uv_texture.data:
				if len(face.uv) == 4:
					for i in face_tri:
						ofile.write(HexFormat(k+i))
					k+= 4
				else:
					for i in (0,1,2):
						ofile.write(HexFormat(k+i))
					k+= 3
			ofile.write("\"))")

		ofile.write(");")

	for param in PARAMS:
		value= getattr(GeomStaticMesh, param)
		ofile.write("\n\t%s= %s;"%(param, a(scene, value)))

	ofile.write("\n}\n")


def write(bus):
	scene= bus['scene']
	ob=    bus['node']['object']

	VRayScene= scene.vray
	VRayExporter= VRayScene.exporter
	
	debug(scene,
		  "Frame {0}: Mesh: \033[0;32m{1:<32}\033[0m".format(scene.frame_current, color(ob.data.name, 'green')),
		  newline= VRayExporter.debug)

	write_mesh_hex(bus)
