import math
from math import radians

class CircularPositioning:
	def __init__(self, orig = (0.0, 0.0, 0.0)):
		self.tt_circular_coords = [0.0, 0.0] 
		self.tt_origin = orig

	def radiusToPoint(self, xyzTuple = (0, 0, 0)):
		if (self.tt_origin == xyzTuple):
			#Radius is zero
			return 0
		#r^2 = (x-h)^2 + (y-j)^2
		rSquared = math.pow((xyzTuple[0] - self.tt_origin[0]), 2) + math.pow((xyzTuple[1] - self.tt_origin[1]), 2)
		return math.sqrt(rSquared)

	def getRadius(self):
		return self.tt_circular_coords[0]

	def getPointXYZ(self):
		xPos = self.tt_circular_coords[0] * math.cos(radians(self.tt_circular_coords[1]))
		yPos = self.tt_circular_coords[0] * math.sin(radians(self.tt_circular_coords[1]))
		zPos = self.tt_origin[2]
		return (xPos, yPos, zPos)

	def addToAngle(self, theta):
		angle = self.tt_circular_coords[1] + theta

		while angle >= 360:
			angle = angle - 360
		while angle < 0:
			angle = angle + 360
		self.tt_circular_coords[1] =  angle

	def angleToPoint(self, xyzTuple = (0,0,0)):
		pass



class SphericalPositioning:
	#Framework for future improvements
	def __init__(self):
		self.tt_spherical_coords = (0.0, 0.0, 0.0) 
		self.tt_origin = (0.0, 0.0, 0.0)

	def radiusToPoint(self, xyzTuple = (0,0,0)):
		if (self.tt_origin == xyzTuple):
			#Radius is zero
			return 0
		rSquared = math.pow((xyzTuple[0] - self.tt_origin[0]), 2) + math.pow((xyzTuple[1] - self.tt_origin[1]), 2)+ math.pow((xyzTuple[2] - self.tt_origin[2]), 2)
		return math.sqrt(rSquared)

