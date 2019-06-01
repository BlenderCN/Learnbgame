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


''' Python modules  '''
import math
import os
import subprocess
import sys
import tempfile
import time

''' Blender modules '''
import bpy

''' vb modules '''
from vb25.utils import *


def write_mesh_hq(ofile, sce, ob):
	timer= time.clock()

	debug(sce, "Generating HQ file (Frame: %i; File: %s)..." % (sce.frame_current,ofile.name))

	GeomMeshFile= ob.data.vray.GeomMeshFile

	me=  ob.to_mesh(sce, True, 'RENDER')
	dme= None

	if GeomMeshFile.animation and GeomMeshFile.add_velocity:
		if sce.frame_current != sce.frame_end:
			sce.frame_set(sce.frame_current+1)
			dme= ob.to_mesh(sce, True, 'RENDER')

	if GeomMeshFile.apply_transforms:
		me.transform(ob.matrix_world)
		if dme:
			dme.transform(ob.matrix_world)

	if dme:
		for v,dv in zip(me.vertices,dme.vertices):
			ofile.write("v=%.6f,%.6f,%.6f\n" % tuple(v.co))
			ofile.write("l=%.6f,%.6f,%.6f\n" % tuple([dc-c for c,dc in zip(v.co,dv.co)]))
	else:
		for vertex in me.vertices:
			ofile.write("v=%.6f,%.6f,%.6f\n" % tuple(vertex.co))
			ofile.write("l=0.0,0.0,0.0\n")

	face_attr = 'faces' if 'faces' in dir(me) else 'polygons'

	k= 0
	for face in getattr(me, face_attr):
		vert_order= (0,1,2,2,3,0)
		if len(face.vertices) == 4:
			ofile.write("f=%d,%d,%d;%d\n" % (face.vertices[0], face.vertices[1], face.vertices[2], face.material_index + 1))
			ofile.write("f=%d,%d,%d;%d\n" % (face.vertices[2], face.vertices[3], face.vertices[0], face.material_index + 1))
			ofile.write("fn=%i,%i,%i\n" % (k,k+1,k+2))
			ofile.write("fn=%i,%i,%i\n" % (k+3,k+4,k+5))
			k+= 6
		else:
			vert_order= (0,1,2)
			ofile.write("f=%d,%d,%d;%d\n" % (face.vertices[0], face.vertices[1], face.vertices[2], face.material_index + 1))
			ofile.write("fn=%i,%i,%i\n" % (k,k+1,k+2))
			k+= 3
		for v in vert_order:
			if face.use_smooth:
				ofile.write("n=%.6f,%.6f,%.6f\n" % tuple(me.vertices[face.vertices[v]].normal))
			else:
				ofile.write("n=%.6f,%.6f,%.6f\n" % tuple(face.normal))

	uv_textures = me.tessface_uv_textures if 'tessface_uv_textures' in dir(me) else me.uv_textures
	if len(uv_textures):
		uv_layer= uv_textures[0]
		k= 0
		for face in uv_layer.data:
			for i in range(len(face.uv)):
				ofile.write("uv=%.6f,%.6f,0.0\n" % (face.uv[i][0], face.uv[i][1]))
			if len(face.uv) == 4:
				ofile.write("uf=%i,%i,%i\n" % (k,k+1,k+2))
				ofile.write("uf=%i,%i,%i\n" % (k+2,k+3,k))
				k+= 4
			else:
				ofile.write("uf=%i,%i,%i\n" % (k,k+1,k+2))
				k+= 3
	ofile.write("\n")
	
	debug(sce, "Generating HQ file done [%.2f]" % (time.clock() - timer))


def generate_proxy(sce, ob, vrmesh, append=False):
	hq_file= tempfile.NamedTemporaryFile(mode='w', suffix=".hq", delete=False)
	write_mesh_hq(hq_file, sce, ob)
	hq_file.close()
	proxy_creator(hq_file.name, vrmesh, append)
	os.remove(hq_file.name)
