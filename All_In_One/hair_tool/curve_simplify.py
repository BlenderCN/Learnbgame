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
# Based on Blenders builtin Curve simplify addon modified by JOSECONSCO

"""
This script simplifies Curve objects and animation F-Curves.
"""
# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb

import bpy

 
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        )
from mathutils import Vector
from math import (
        sin,
        pow,
        )
from numpy import interp


# ### Curves OPERATOR ###
class CURVE_OT_csimplify(bpy.types.Operator):
    bl_idname = "object.curve_simplify"
    bl_label = "Simplify Curves"
    bl_description = "Simplify Curves"
    bl_options = {'REGISTER', 'UNDO'}


    SplineTypes = [
                ('INPUT', 'Input', 'Same type as input spline'),
                ('NURBS', 'Nurbs', 'NURBS'),
                ('BEZIER', 'Bezier', 'BEZIER'),
                ('POLY', 'Poly', 'POLY')]
    output = EnumProperty(
                name="Output splines",
                description="Type of splines to output",
                items=SplineTypes
                )
    error = FloatProperty(
                name="Error",
                description="Maximum allowed distance error in Blender Units",
                min=0, max=10,
                default=0.0, precision=2
                )
    # onlySelection = BoolProperty(name="Only Selected", description="Affect only selected points", default=True)


    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'CURVE')

    def execute(self, context):
        self.main(context, context.active_object)
        # bpy.ops.object.curve_uv_refresh()
        return {'FINISHED'}

    # get binomial coefficient
    def binom(self,n, m):
        b = [0] * (n + 1)
        b[0] = 1
        for i in range(1, n + 1):
            b[i] = 1
            j = i - 1
            while j > 0:
                b[j] += b[j - 1]
                j -= 1
        return b[m]

    # get nth derivative of order(len(verts)) bezier curve
    def getDerivative(self,verts, t, nth):
        order = len(verts) - 1 - nth
        QVerts = []

        if nth:
            for i in range(nth):
                if QVerts:
                    verts = QVerts
                derivVerts = []
                for i in range(len(verts) - 1):
                    derivVerts.append(verts[i + 1] - verts[i])
                QVerts = derivVerts
        else:
            QVerts = verts

        if len(verts[0]) == 3:
            point = Vector((0, 0, 0))
        if len(verts[0]) == 2:
            point = Vector((0, 0))

        for i, vert in enumerate(QVerts):
            point += self.binom(order, i) * pow(t, i) * pow(1 - t, order - i) * vert
        deriv = point

        return deriv

    # get curvature from first, second derivative
    def getCurvature(self,deriv1, deriv2):
        if deriv1.length == 0:  # in case of points in straight line
            curvature = 0
            return curvature
        curvature = (deriv1.cross(deriv2)).length / pow(deriv1.length, 3)
        return curvature

    # ### Ramer-Douglas-Peucker algorithm ###

    # get altitude of vert
    def altitude(self,point1, point2, pointn):
        edge1 = point2 - point1
        edge2 = pointn - point1
        if edge2.length == 0:
            altitude = 0
            return altitude
        if edge1.length == 0:
            altitude = edge2.length
            return altitude
        alpha = edge1.angle(edge2)
        altitude = sin(alpha) * edge2.length
        return altitude

    # iterate through verts
    def iterate(self,points, newVerts, error):
        new = []
        for newIndex in range(len(newVerts) - 1):
            bigVert = 0
            alti_store = 0
            for i, point in enumerate(points[newVerts[newIndex] + 1: newVerts[newIndex + 1]]):
                alti = self.altitude(points[newVerts[newIndex]], points[newVerts[newIndex + 1]], point)
                if alti > alti_store:
                    alti_store = alti
                    if alti_store >= error:
                        bigVert = i + 1 + newVerts[newIndex]
            if bigVert:
                new.append(bigVert)
        if new == []:
            return False
        return new

    # get SplineVertIndices to keep
    def simplify_RDP(self,splineVerts):
        # main vars
        error = self.error/100

        # set first and last vert
        newVerts = [0, len(splineVerts) - 1]

        # iterate through the points
        new = 1
        while new is not False:
            new = self.iterate(splineVerts, newVerts, error)
            if new:
                newVerts += new
                newVerts.sort()
        return newVerts

    # ### CURVE GENERATION ###

    # set bezierhandles to auto
    def setBezierHandles(self,newCurve):
        # Faster:
        for spline in newCurve.data.splines:
            for p in spline.bezier_points:
                p.handle_left_type = 'AUTO'
                p.handle_right_type = 'AUTO'

    # get array of new coords for new spline from vertindices
    def vertsToPoints(self,newVerts, splineVerts, splineType):
        # main vars
        newPoints = []

        # array for BEZIER spline output
        if splineType == 'BEZIER':
            for v in newVerts:
                newPoints += splineVerts[v].to_tuple()

        # array for nonBEZIER output
        else:
            for v in newVerts:
                newPoints += (splineVerts[v].to_tuple())
                if splineType == 'NURBS':
                    newPoints.append(1)  # for nurbs w = 1
                else:  # for poly w = 0
                    newPoints.append(0)
        return newPoints

    # ### MAIN OPERATIONS ###

    def main(self, context, curve):
        output = self.output
        # onlySelection = options[2]

        pointsList = []
        pointsRadius = []
        pointsTilt = []
        # go through splines
        backup_mat_indices = [spline.material_index for spline in curve.data.splines]
        for spline in curve.data.splines:
            if len(spline.points) > 1 or len(spline.bezier_points) > 1:  # skip single points
                # check what type of spline to create
                if output == 'INPUT':
                    splineType = spline.type
                else:
                    splineType = output

                # get vec3 list to simplify
                if spline.type == 'BEZIER':
                    splineVerts = [splineVert.co for splineVert in spline.bezier_points.values()]

                else:
                    splineVerts = [splineVert.co.to_3d() for splineVert in spline.points.values()]
                pointsRadius.append([point.radius for point in spline.points])
                pointsTilt.append([point.tilt for point in spline.points])

                # simplify spline according to mode
                newVerts = self.simplify_RDP(splineVerts)

                # convert indices into vectors3D
                newPoints = self.vertsToPoints(newVerts, splineVerts, splineType)
                pointsList.append(newPoints)

        interpolRad = []
        interpolTilt = []

        # ipdb.set_trace()
        for radii, tilts, points in zip(pointsRadius, pointsTilt, pointsList):  # pointsList - after interpolation
            if splineType == 'BEZIER':
                pLen = int(len(points) * 0.33)  # after interpolaiton strand len, will give radii len and tilts len
            else:
                pLen = int(len(points) * 0.25)  # after interpolaiton strand len, will give radii len and tilts len
            t_ins = [i / (pLen - 1) for i in range(pLen)]
            t_rad = [[i / (len(radii) - 1) for i in range(len(radii))]]

            interpolRad.append(interp(t_ins, t_rad[0], radii))  # first arg len() = out len
            interpolTilt.append(interp(t_ins, t_rad[0], tilts))  # first arg len() = out len

        resolution_u = curve.data.resolution_u
        curve.data.splines.clear()
        for i, newPoints in enumerate(pointsList):
            # create new spline
            newSpline = curve.data.splines.new(type=splineType)

            # put newPoints into spline according to type
            if splineType == 'BEZIER':
                newSpline.bezier_points.add(int(len(newPoints) * 0.33))
                newSpline.bezier_points.foreach_set('co', newPoints)
                newSpline.bezier_points.foreach_set('tilt', interpolTilt[i].tolist())
                newSpline.bezier_points.foreach_set('radius', interpolRad[i].tolist())
            else:
                newSpline.points.add(int(len(newPoints) * 0.25 - 1))
                newSpline.points.foreach_set('co', newPoints)
                newSpline.points.foreach_set('tilt', interpolTilt[i].tolist())
                newSpline.points.foreach_set('radius', interpolRad[i].tolist())

            if splineType == 'NURBS':
                newSpline.order_u = 3  # like bezier thing
                newSpline.use_endpoint_u = True

        curve.data.resolution_u = resolution_u
        for i,newSpline in enumerate(curve.data.splines): #restore mat to new splines
            newSpline.material_index = backup_mat_indices[i]
        # set bezierhandles to auto
        self.setBezierHandles(curve)
        return



