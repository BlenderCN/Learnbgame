# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import math
import mathutils

class OPP_Factory():
	bl_idname = "op_factory"

	def get_vertices(self,object):

		loop = object.data.edge_loops_from_edges()
		lst = loop[0][:4]
		v0 = object.data.vertices[lst[0]].co
		v1 = object.data.vertices[lst[1]].co
		v2 = object.data.vertices[lst[2]].co
		v3 = object.data.vertices[lst[3]].co
		
		return [v0,v1,v2,v3]

	def build_mesh(self,object,name,container):
		mesh = bpy.data.meshes.new(name)
		mesh.from_pydata(container.vertices,container.edges,container.faces)
		mesh.update()

		if object == None:
			object = bpy.data.objects.new(name,mesh)
			bpy.context.scene.objects.link(object)

		else:
			object.data = mesh

		object.show_wire = True


class OP_Find_Contour(OPP_Factory,bpy.types.Operator):
	bl_idname="object.arx_find_contour"
	bl_label = "Find Contour"

	def test(self,edge1,edge2):
		e1 = edge1[0]
		e2 = edge1[1]
		
		f1 = edge2[0]
		f2 = edge2[1]

		if e1 == f1:
			if e2 == f2:
				return True
			else:
				if e2 == f1 and e1 == f2:
					return True
				else:
					return False
			
	def invoke(self,context,event):
		object = bpy.context.object
		faces = object.data.polygons
		vertices = object.data.vertices
		edges = object.data.edges

		all_face_edges = []
		for face in faces:
			edges = face.edge_keys
			all_face_edges.extend(edges)

		i = 0 
		dupli = []
		for edge in all_face_edges:
			j = 0
			for other in all_face_edges:
				r = self.test(edge,other)
				if r and j != i:
					dupli.append(edge)
				j += 1
			i += 1

		contour = []
		for edge in all_face_edges:
			yes = True
			for item in dupli:
				r = self.test(edge,item)
				if r : yes = False
			if yes : contour.append(edge)
		
		vert = []
		for v in vertices:
			vert.append([v.co[0],v.co[1],v.co[2]])

		faces = []
		build_object = True
		if build_object:
			mesh = bpy.data.meshes.new("contour")
			mesh.from_pydata(vert,contour,faces)

			object = bpy.data.objects.new("contour",mesh)
			bpy.context.scene.objects.link(object)

		
		return {'FINISHED'}

