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
from bpy.props import *
import math
import mathutils

# VIEW
class OP_View(bpy.types.Operator):
	bl_idname="wm.view_widget"
	bl_label="view_widget"

	def execute(self,context):
		for area in bpy.context.screen.areas:
			if area.type == 'VIEW_3D':
				print("------")
				#area.spaces[0].region_3d.view_perspective = 'ORTHO'
				#bpy.ops.view3d.viewnumpad('EXEC_DEFAULT')
		return {'FINISHED'}

	def invoke(self,context,event):
		print("invoke me!")
		return self.execute(self,context,event)

class OP_MY_Utils_Xplode(bpy.types.Operator):
	bl_idname="object.xplode"
	bl_label="xplode"		
	bl_description="Separate each face of mesh"

	def build(self,face):
		face = face.vertices
		if len(face) == 3:
			v0 = self.vertices[face[0]].co
			v1 = self.vertices[face[1]].co
			v2 = self.vertices[face[2]].co

			vertices = [v0,v1,v2]
		else:
			v0 = self.vertices[face[0]].co
			v1 = self.vertices[face[1]].co
			v2 = self.vertices[face[2]].co
			v3 = self.vertices[face[3]].co

			vertices = [v0,v1,v2,v3]

		new = []
		for vertice in vertices:
			new.append(self.matrix*vertice)

		edges = []
		if len(face) == 3:
			faces = [[0,1,2]]
		else:
			faces = [[0,1,2,3]]

		mesh = bpy.data.meshes.new("x")
		mesh.from_pydata(new,edges,faces)
		mesh.update()

		ob = bpy.data.objects.new("x",mesh)

		center = ob.data.polygons[0].center

		bpy.context.scene.objects.link(ob)
		self.names.append(ob.name)

	def execute(self,context):
		self.object = bpy.context.object
		self.vertices = self.object.data.vertices
		self.faces = self.object.data.polygons
		self.matrix = self.object.matrix_local.copy()
		self.names = []

		if self.object.type == 'MESH':
			for face in self.faces:
				self.build(face)
		bpy.context.scene.objects.unlink(self.object)

		# Set Origin
		for name in self.names:
			bpy.ops.object.select_pattern(pattern=name)
			bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
		return {'FINISHED'}

