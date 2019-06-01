# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Copyright (C) 2017 JOSECONSCO
# Created by JOSECONSCO

import bpy
import math
import numpy as np
from bpy.props import EnumProperty, FloatProperty, BoolProperty, IntProperty, StringProperty
from .resample2d import get2dInterpol, interpol, get_strand_proportions
# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb


class CurvesResample(bpy.types.Operator):
    bl_label = "Curve resample"
    bl_idname = "object.curve_resample"
    bl_description = "Change ammount of points on curve"
    bl_options = {"REGISTER", "UNDO"}

    hairType = bpy.props.EnumProperty(name="Output Curve Type", default="NURBS",
                                      items=(("BEZIER", "Bezier", ""),
                                             ("NURBS", "Nurbs", ""),
                                             ("POLY", "Poly", "")))
    # bezierRes = IntProperty(name="Bezier resolution", default=3, min=1, max=12)
    t_in_y = IntProperty(name="Strand Segments", default=8, min=3, max=20)
    uniformPointSpacing = BoolProperty(name="Uniform spacing", description="Distribute stand points with uniform spacing", default=False)
    equalPointCount = BoolProperty(name="Equal point count", description="Give all cures same points count \n"
                                                                       "If disabled shorter curves will have less points", default=False)
    onlySelection = BoolProperty(name="Only Selected", description="Affect only selected points", default=False)

    def invoke(self, context, event):
        particleObj = context.active_object
        if particleObj.mode == 'EDIT':
            self.onlySelection = True
        elif particleObj.mode == 'OBJECT':
            self.onlySelection = False
        Curve = context.active_object
        if not Curve.type == 'CURVE':
            self.report({'INFO'}, 'Use operator on curve type object')
            return {"CANCELLED"}
        self.input_spline_type = Curve.data.splines[0].type
        self.hairType =  self.input_spline_type  #hair type  - output spline
        if self.input_spline_type == 'NURBS':
            self.nurbs_order = Curve.data.splines[0].order_u
        if len(Curve.data.splines) > 0:  # do get initnial value for resampling t
            polyline = Curve.data.splines[0]  # take first spline len for resampling
            if polyline.type == 'NURBS' or polyline.type == 'POLY':
                self.t_in_y = len(polyline.points)
            else:
                self.t_in_y = len(polyline.bezier_points)
        self.bezierRes = Curve.data.resolution_u

        return self.execute(context)

    def execute(self, context):
        curveObj = context.active_object
        if curveObj.type != 'CURVE':
            self.report({'INFO'}, 'Works only on curves')
            return {"CANCELLED"}
        pointsList = []
        pointsRadius = []
        pointsTilt = []
        selectedSplines = []

        if self.onlySelection:
            for polyline in curveObj.data.splines:
                if polyline.type == 'NURBS' or polyline.type == 'POLY':
                    if any(point.select==True for point in polyline.points):
                        selectedSplines.append(polyline)
                else:
                    if any(point.select_control_point == True for point in polyline.bezier_points):
                        selectedSplines.append(polyline)
            if not selectedSplines:
                selectedSplines = curveObj.data.splines
        else:
            selectedSplines = curveObj.data.splines

        for polyline in selectedSplines:  # for strand point
            if polyline.type == 'NURBS' or polyline.type == 'POLY':
                points = polyline.points
            else:
                points = polyline.bezier_points
            if len(points)>1: #skip single points
                pointsList.append([point.co.to_3d() for point in points])
                pointsRadius.append([point.radius for point in points])
                pointsTilt.append([point.tilt for point in points])
        backup_mat_indices = [spline.material_index for spline in selectedSplines]
        interpolRad = []
        interpolTilt = []
        # ipdb.set_trace()
        splinePointsList = interpol(pointsList, self.t_in_y, self.uniformPointSpacing, constantLen=self.equalPointCount)
        if self.equalPointCount: # each output spline will have same point count
            t_ins_y = [i / (self.t_in_y - 1) for i in range(self.t_in_y)]

            for radii, tilts in zip(pointsRadius, pointsTilt):  # per strand
                t_rad = [i / (len(radii) - 1) for i in range(len(radii))]
                interpolRad.append(np.interp(t_ins_y, t_rad, radii))  # first arg len() = out len
                interpolTilt.append(np.interp(t_ins_y, t_rad, tilts))  # first arg len() = out len
        else: # shorter output splines will have less points
            NormalizedStrandsLength = get_strand_proportions(pointsList)
            for radii, tilts, strandLen in zip(pointsRadius, pointsTilt, NormalizedStrandsLength):  # per strand
                # t_Normalized = max(round((self.t_in_y-1) * strandLen), 2)
                t_Normalized = max(math.ceil((self.t_in_y - 1) * strandLen), 2) + 1
                t_ins_Normalized = [i / (t_Normalized - 1) for i in range(int(t_Normalized))]
                t_rad = [[i / (len(radii) - 1) for i in range(len(radii))]]
                interpolRad.append(np.interp(t_ins_Normalized, t_rad[0], radii))  # first arg len() = out len
                interpolTilt.append(np.interp(t_ins_Normalized, t_rad[0], tilts))  # first arg len() = out len

        curveData = curveObj.data
        # spline_type =
        if self.onlySelection:
            for spline in selectedSplines:
                curveData.splines.remove(spline)
        else:
            curveData.splines.clear()

        newSplines = []
        for k, splinePoints in enumerate(splinePointsList):  # for each strand/ring
            curveLenght = len(splinePoints)
            polyline = curveData.splines.new(self.hairType)
            newSplines.append(polyline)
            if self.hairType == 'BEZIER':
                polyline.bezier_points.add(curveLenght - 1)
            elif self.hairType == 'POLY' or self.hairType == 'NURBS':
                polyline.points.add(curveLenght - 1)
            if self.hairType == 'NURBS':
                if self.input_spline_type == 'NURBS':
                    polyline.order_u = self.nurbs_order
                else:
                    polyline.order_u = 3  #like bezier thing
                polyline.use_endpoint_u = True
            np_splinePointsOnes = np.ones((len(splinePoints), 4), dtype=np.float32)  # 4 coord x,y,z ,1
            np_splinePointsOnes[:,:3] = splinePoints
            np_interpol_Rad = np.array(interpolRad[k], dtype=np.float16)
            np_interpol_Tilt = np.array(interpolTilt[k], dtype=np.float16)
            if self.hairType == 'BEZIER':
                polyline.bezier_points.foreach_set('co' , np_splinePointsOnes[:,:3])
                polyline.bezier_points.foreach_set('radius' , np_interpol_Rad)
                polyline.bezier_points.foreach_set('tilt',np_interpol_Tilt)
                polyline.bezier_points.foreach_set('handle_left_type', 'AUTO')
                polyline.bezier_points.foreach_set('handle_right_type', 'AUTO')
            else:
                polyline.points.foreach_set('co', np_splinePointsOnes.ravel())
                polyline.points.foreach_set('radius', np_interpol_Rad)
                polyline.points.foreach_set('tilt', np_interpol_Tilt)

        curveData.resolution_u = self.bezierRes
        # bpy.ops.object.curve_uv_refresh()
        for backup_mat,newSpline in zip(backup_mat_indices, newSplines):
            newSpline.material_index = backup_mat
        return {"FINISHED"}
