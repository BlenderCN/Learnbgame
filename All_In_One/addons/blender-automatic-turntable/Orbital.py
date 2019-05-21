import bpy
import mathutils
from math import radians
from . import RadialPoints

class Orbital:
	'''Orbital class contains variables and functions for positioning and rotating camera around a model
		'''
	def __init__(self, box = None):
		self.TT_FILEPATH_ROOT = "/tmp\\"
		self.TT_FILEPATH_ITERATOR = "1"
		self.TT_FILEPATH_EXT  =".png"

		self.TT_ANGLE_INCREMENTS = 90
		self.TT_POSITION = (0.0, -5.0, 0.0)	#Camera should be in front (Neg-Y) of model

		self.TT_ROTATION_X = 90.0
		self.TT_ROTATION_Y = 0.0
		self.TT_ROTATION_Z = 0.0

		self.tt_orbit = RadialPoints.CircularPositioning()
		if box is not None:
			self.tt_orbit.tt_origin = box.midpoint 
		self.tt_iterations = 3

	def setToFrontview(self, camera):
		'''sets camera of choice to a directly front view position (assuming "Front" is theta=270 degrees)
			camera -- Camera object to be positioned
			'''
		#Move camera front and center
		camera.location = self.TT_POSITION
		camera.rotation_euler = (radians(self.TT_ROTATION_X), 0.0, 0.0)

		#reposition camera to fit selected items
		bpy.ops.view3d.camera_to_view_selected()
		camera.location = (camera.location[0], camera.location[1]+ (camera.location[1]*.1), camera.location[2])
		rads = self.tt_orbit.radiusToPoint(camera.location)
		self.tt_orbit.tt_circular_coords = [rads, 270]
		print("Orbiting around: " + str(self.tt_orbit.tt_origin) )

	def catchRender(self, camera):
		bpy.data.scenes['Scene'].render.filepath = self.TT_FILEPATH_ROOT + self.TT_FILEPATH_ITERATOR + self.TT_FILEPATH_EXT
		bpy.ops.render.render( write_still=True ) 
		self.TT_FILEPATH_ITERATOR = str(int(self.TT_FILEPATH_ITERATOR)+1)

	def setCameraToNextInc(self, camera  ):
		sampPos = self.tt_orbit.getPointXYZ()
		
		self.TT_ROTATION_Z = self.TT_ROTATION_Z + self.TT_ANGLE_INCREMENTS
		camera.rotation_euler = (radians(self.TT_ROTATION_X), 0.0, radians(self.TT_ROTATION_Z))
		
		#Set camera position
		self.tt_orbit.addToAngle(self.TT_ANGLE_INCREMENTS)
		sampPos = self.tt_orbit.getPointXYZ()
		camera.location= mathutils.Vector(sampPos)

	def renderOrbit(self, camera):
		'''Iterate tghrough radial steps and render at position
			camera -- Camera object to perform on
			'''
		#Removes first render jitter
		if camera is not bpy.context.scene.camera:
			print("Setting camera: " + camera)
			bpy.context.scene.camera = camera


		sampPos = self.tt_orbit.getPointXYZ()
		camera.location= mathutils.Vector(sampPos)

		while(self.tt_iterations >0):
			#Take render
			#print("Iteration #" + str(self.tt_iterations))
			self.catchRender(camera)
			self.tt_iterations -= 1
			if(self.tt_iterations is not 0):
				#Rotate camera
				self.setCameraToNextInc(camera)
			
	