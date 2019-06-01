import math
import copy
class Vector2D:
	def __init__(self, x, y):
		self.x = x
		self.y = y

	#pre: !isZero
	def normalize(self):
		length = self.getLength()

		self.x /= length
		self.y /= length

	def getLength(self):
		return math.sqrt((self.x*self.x) + (self.y*self.y))

	#pre: !isZero
	def CwAngleWith(self, other):
		a = copy.deepcopy(self)
		b = copy.deepcopy(other)
		a.normalize()
		b.normalize()
		"""
		dot = min( max(a.x*b.x + a.y*b.y, -1), 1)
		return math.acos(dot)
		"""
		#angle from -1(left) to 1(right)
		return -math.atan2(
			a.x*b.y-a.y*b.x,
			a.x*b.x+a.y*b.y)/math.pi

	def isZero(self):
		return self.getLength() == 0

	def __sub__(a, b):
		if isinstance(b, Vector2D):
			return Vector2D(a.x-b.x, a.y-b.y)
		elif isinstance(b, Point2D):
			return Point2D(a.x-b.x, a.y-b.y)
		else:
			return Vector2D(a.x-b, a.y-b)

	def __add__(a, b):
		if isinstance(b, Vector2D):
			return Vector2D(a.x+b.x, a.y+b.y)
		elif isinstance(b, Point2D):
			return Point2D(a.x+b.x, a.y+b.y)
		else:
			return Vector2D(a.x+b, a.y+b)

	def __mul__(a, b):
		return Vector2D(a.x*b, a.y*b)

	def __truediv__(a, b):
		return Vector2D(a.x/b, a.y/b)

	def __str__(self):
		return "(Vector2D x:{} y:{})".format(self.x, self.y)

class Point2D:
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def translate(vector):
		self.x += vector.x
		self.y += vector.y

	def __add__(a, b):
		return Point2D(a.x+b.x, a.y+b.y)

	def __sub__(a, b):
		if isinstance(b, Vector2D):
			return Point2D(a.x-b.x, a.y-b.y)	
		else:
			return Vector2D(a.x-b.x, a.y-b.y)

	def __str__(self):
		return "(Point2D x:{} y:{})".format(self.x, self.y)

