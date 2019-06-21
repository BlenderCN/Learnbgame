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
import mathutils
from mathutils import Vector
from curve_to_even_mesh.bezierCurve import *

class BezierSegmentIterator:

	# Reference to the curve, this iterator belongs to
	curve = None
	# Index of the current segment
	index = 0

	def __init__(self, curve, index):
		self.curve = curve
		self.index = index

	# This function jumps to the next segments and returns
	# true if there is another segment, or false, if the
	# end of the curve has been reached. In this case it
	# jumps to the first segment
	def next(self):
		hasNextItem = self.hasNext()

		self.index += 1
		self.index %= self.curve.segmentCount()

		return hasNextItem

	# This function jumps to the previous segments and returns
	# true if there is another segment, or false, if the
	# beginning of the curve has been reached. In this case it
	# jumps to the last segment
	def previous(self):
		hasPreviousItem = self.hasPrevious()

		self.index += self.curve.segmentCount() - 1
		self.index %= self.curve.segmentCount()

		return hasPreviousItem

	# Returns true if this is not the last element
	def hasNext(self):
		return self.index != (self.curve.segmentCount() - 1)

	# Returns false if this is not the first element
	def hasPrevious(self):
		return self.index != 0

	# Returns the point of the bezier segment evaluated at t
	def pointAt(self, t):
		p1 = self.curve.pointAt(self.index, 0)
		p2 = self.curve.pointAt(self.index, 1)
		p3 = self.curve.pointAt(self.index, 2)
		p4 = self.curve.pointAt(self.index, 3)

		v1 = p2 - p1
		v2 = p3 - p2
		v3 = p4 - p3

		p1 += v1 * t
		p2 += v2 * t
		p3 += v3 * t

		v1 = p2 - p1
		v2 = p3 - p2

		p1 += v1 * t
		p2 += v2 * t

		return p1 + (p2 - p1) * t

	# Returns the tangent of the bezier segment evaluated at t
	# using the first derivative
	def tangentAt(self, t):
		# First let's calculate the points of the first derivative
		p1 = self.curve.pointAt(self.index, 1) - self.curve.pointAt(self.index, 0)
		p2 = self.curve.pointAt(self.index, 2) - self.curve.pointAt(self.index, 1)
		p3 = self.curve.pointAt(self.index, 3) - self.curve.pointAt(self.index, 2)

		v1 = p2 - p1
		v2 = p3 - p2

		p1 += v1 * t
		p2 += v2 * t

		return p1 + (p2 - p1) * t

	# Returns the normal of the bezier segment evaluated at t
	# using the first derivative and rotating it by 90°
	def normalAt(self, t):
		tan = self.tangentAt(t)

		# Rotate the normal along the Z-up axis
		normal = Vector((tan.y, -tan.x, tan.z))
		normal.normalize()

		return normal

	# Returns a length approximation of the curve, based on a
	# subdivision into streight lines
	def computeLength(self, segments):
		print("Segments: " + str(segments))
		length = 0.0
		a = self.pointAt(0.0)
		for i in range(1, segments + 1):
			b = self.pointAt(i / segments)
			length += (b - a).length
			a = b
		return length
