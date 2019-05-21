# BEGIN GPL BLOCK    
#    Batch renders around selection to create turntable frames
#    Copyright (C) 2017  Mark Fitzgibbon
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# END GPL BLOCK
bl_info = {
	"name":"Automatic Turntable",
	"description":"Automatically focus camera to rotate around a selected object in a scene",
	"version":(0,3,1),
	"blender":(2,78,0),
	"support":"TESTING",
	"category":"Render",
	"location":"Render",
	"author":"Mark Fitzgibbon"
}
#Python imports
import mathutils
from math import radians

#Blender Imports
import bpy
from bpy.props import IntProperty, FloatProperty, StringProperty

#Local imports
from . import BoundingBox
from . import RadialPoints

addons_keymap = []

def fitCameraToBox(camera, box, margin = 0.0):
	data_cam = bpy.data.cameras[camera.name]
	focal = data_cam.lens

	#Get X, Y, and Z bounding box lengths	
	box_width_x = box.getAxisLength(0)
	box_width_y = box.getAxisLength(1)
	box_height = box.getAxisLength(2)
	
	sensorWidth = data_cam.sensor_width
	sensorHeight = data_cam.sensor_height

	obj_dst = lambda n, m: ( (focal * n*1000 )/m)/1000 * (1+margin) + max(box_width_x, box_width_y)/2
	
	#Determine necessary radii for fitting the whole image in
	cam_radius_h = obj_dst(box_height, sensorHeight) 
	cam_radius_w = obj_dst(max(box_width_x, box_width_y), sensorWidth) 

	##Return the furthest (and best fitting) radius
	return max(cam_radius_h, cam_radius_w)

class Turntable:

	def __init__(self, camera, filepath="//render_out",iterations=1, increments=90 ):
		self.iterations=iterations
		self.increments=increments
		self.camera=camera	#Object of camera (eg bpy.data.objects)
		self.filepath=filepath
		self.camera_rotation = (90, 0, 0)

		#Set target center
		self.box = BoundingBox.BoundingBox(bpy.context.selected_objects)
		self.orbit = RadialPoints.CircularPositioning(self.box.midpoint)

		#Set Radius and starting angle
		self.orbit.tt_circular_coords = [fitCameraToBox(self.camera, self.box, 0), 270]	#Angle 270 should translate to a Front view

		#List of all camera position/rotation comos in order
		self.camera_atlas = []
		flag = self.iterations
		while(flag > 0):
			posit = self.orbit.getPointXYZ()	#Location of camera
			rotat = (radians(self.camera_rotation[0]), radians(self.camera_rotation[1]), radians(self.camera_rotation[2]))
			self.camera_atlas.append([posit, rotat])
			self.orbit.addToAngle(self.increments)
			self.camera_rotation = (self.camera_rotation[0], self.camera_rotation[1], self.camera_rotation[2] + increments)
			flag -= 1

	def initializeCamera(self):
		#Activate requested camera if it isn't
		if self.camera is not bpy.context.scene.camera:
			bpy.context.scene.camera = self.camera

		bpy.context.scene.camera.location[2] = self.box.midpoint[2]

	def setToIndexAndRender(self, index = 0):
		#Set position and rotation of camera to position on list at index
		self.camera.location = mathutils.Vector(self.camera_atlas[index][0])
		self.camera.rotation_euler = self.camera_atlas[index][1]

		bpy.data.scenes[bpy.context.scene.name].render.filepath = self.filepath + format(index+1, '03d')
		bpy.ops.render.render( write_still=True )

	def renderAllPositions(self):
		self.initializeCamera()
		index = 0
		for cpos in self.camera_atlas:
			self.setToIndexAndRender(index)
			index += 1

class AutomaticTurntableOperator(bpy.types.Operator):
	bl_idname = "render.automatic_turntable"
	bl_label = "Automatic Turntable Renders"
	bl_options = {'REGISTER', 'UNDO'}

	#Number of renders to take
	iterations = IntProperty(
		name= "Iterations",
		min = 1,
		default = 1)
	#Angle between iterations
	increments = FloatProperty(
		name ="Increments",
		min = 0,
		max = 360,
		default = 90
		)
	#Space between most extreme edge and edge of image
	margin = FloatProperty(
		name = "Margin",
		min = 0,
		max = 1,
		default = 0
		)
	#String name of camera
	camera = StringProperty(
		name="Camera"
		)
	#Filepath locaton to save renders
	filepath = StringProperty(
		name="File Path")

	def invoke(self, context, event):
		actScene = bpy.context.scene
		self.camera =actScene.camera.name
		self.filepath = bpy.data.scenes[actScene.name].render.filepath
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		box = BoundingBox.BoundingBox(bpy.context.selected_objects)
		ttb=Turntable(bpy.data.objects[self.camera], self.filepath, self.iterations, self.increments)
		ttb.renderAllPositions()
		bpy.data.scenes[bpy.context.scene.name].render.filepath =  self.filepath
		return {'FINISHED'}

def addToRenderMenu(self, context):
	self.layout.operator(
		AutomaticTurntableOperator.bl_idname,
		text = "Automatic Turntable"
		)

def register():
	bpy.utils.register_class(AutomaticTurntableOperator)
	bpy.types.INFO_MT_render.append(addToRenderMenu)

def unregister():
	bpy.utils.unregister_class(AutomaticTurntableOperator)
	bpy.types.INFO_MT_render.remove(addToRenderMenu)

if __name__ == "__main__":
	register()