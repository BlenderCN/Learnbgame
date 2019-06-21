'''# ##### BEGIN GPL LICENSE BLOCK #####
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

bl_info = {
	"name": "Ogive",
	"author": "Julien Duroure",
	"version": (1, 0),
	"blender": (2, 5, 6),
	"api": 35969,
	"location": "View3D > Add > Mesh > Ogive",
	"description": "Adds Ogive",
	"warning": "",
	"wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/Add_Mesh/Add_Ogive",
	"tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=26779",
	"category": "Learnbgame",
}

'''
import bpy
from math import *
from bpy.props import FloatProperty, BoolProperty, IntProperty
from bpy_extras.object_utils import object_data_add
from mathutils import Vector

def get_y_circle(x,o,r):
	return sqrt(abs(-x*x-o*o+2*x*o+r*r))

def add_object(self, context):
	width  = self.width
	height = self.height
	step   = self.step
	half   = self.half

	O_1_x = (height*height-width*width)/(2*width)
	O_1_y = 0
	r_1   = sqrt((O_1_x + width)*(O_1_x + width))

	O_2_x = -O_1_x
	O_2_y = 0
	r_2   = r_1

	vertices = []
	edges   = []
	faces   = []

	circle1  = []
	circle2  = []

	screw = width / (step-1)
	for i in range(0,step):
	
		#circle1
		x = -width+i*screw
		y = get_y_circle(x,O_1_x,r_1)
		circle1.append([x,y,0.0])

		#circle2
		x = i*screw
		y = get_y_circle(x,O_2_x,r_2)
		if i != 0:
			circle2.append([x,y,0])
		
		
	vertices = circle1
	if half == False:
		vertices.extend(circle2)

	for it in range(0,len(vertices)):
		if it != len(vertices)-1:
			edges.append([it,it+1])

	name = 'Ogive'
	mesh = bpy.data.meshes.new(name=name)
	mesh.from_pydata(vertices, edges, faces)
	mesh.update()
	object = bpy.data.objects.new(name, mesh)
	bpy.context.scene.objects.link(object)
	object.select = True
	bpy.context.scene.objects.active = object


class OBJECT_OT_add_ogive(bpy.types.Operator):
	"""Add an Ogive"""
	bl_idname = "mesh.add_ogive"
	bl_label = "Add Ogive"
	bl_description = "Create a new Mesh Ogive"
	bl_options = {'REGISTER', 'UNDO'}

	width  = FloatProperty(name='width',description='width', default=4.0,subtype='DISTANCE',unit='LENGTH')
	height = FloatProperty(name='height',description='height', default=6.0,subtype='DISTANCE',unit='LENGTH')
	step   = IntProperty(name='step',description='step', default=15,min=2)
	half   = BoolProperty(name='half ( for screw )',description='set only half ogive, for screw')
	

	def execute(self, context):

		add_object(self, context)

		return {'FINISHED'}


# Registration

def add_ogive_button(self, context):
	self.layout.operator(
		OBJECT_OT_add_ogive.bl_idname,
		text="Add Ogive",
		icon="PLUGIN")


def register():
	bpy.utils.register_class(OBJECT_OT_add_ogive)
	bpy.types.INFO_MT_mesh_add.append(add_ogive_button)


def unregister():
	bpy.utils.unregister_class(OBJECT_OT_add_ogive)
	bpy.types.INFO_MT_mesh_add.remove(add_ogive_button)


if __name__ == '__main__':
	register()
