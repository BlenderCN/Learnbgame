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
from bpy.props import EnumProperty, FloatProperty, BoolProperty, IntProperty, StringProperty
import math
import numpy as np
from mathutils import kdtree
from mathutils.bvhtree import BVHTree
from .helper_functions import calc_power
from collections import defaultdict

# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb


class SelectRootTip(bpy.types.Operator):
    bl_label = "Select tips/roots"
    bl_idname = "curve.select_tips"
    bl_description = "Select tips/roots"
    bl_options = {"REGISTER", "UNDO"}

    Randomize = BoolProperty(name="Randomize selection", description="Randomize strand length", default=False)
    roots = BoolProperty(name="Roots", description="Roots", default=False)
    extend = BoolProperty(name="Extend", description="Extend selection", default=False)
    seed = IntProperty(name="Seed", default=2, min=1, max=20)
    percentage = IntProperty(name="Percentage", description="Selection percent", default=50, min=0,
                                   max=100, subtype='PERCENTAGE')

    def check(self, context): #DONE: can prop panel be fixed/refreshed when using f6 prop popup
        return True

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'extend')
        layout.prop(self, 'Randomize')

        if self.Randomize:
            layout.prop(self, 'seed')
            layout.prop(self, 'percentage')

    def execute(self, context):
        selectedCurves = context.active_object
        if selectedCurves.type != 'CURVE':
            self.report({'INFO'}, 'Works only on curves')
            return {"CANCELLED"}
        if not self.extend:
            bpy.ops.curve.select_all(action='DESELECT')

        index = 0 if self.roots else -1
        curveData = selectedCurves.data
        for polyline in curveData.splines:  # for strand point
            if polyline.type == 'NURBS' or polyline.type == 'POLY':
                if not polyline.points[index].hide:
                    polyline.points[index].select = True
            else:
                if not polyline.bezier_points[index].select:
                    polyline.bezier_points[index].select = True
        if self.Randomize:
            bpy.ops.curve.select_random(percent=100-self.percentage, seed=self.seed, action='DESELECT')
        return {"FINISHED"}



class SelectNextPrev(bpy.types.Operator):
    bl_label = "Select netx/previous"
    bl_idname = "curve.select_next"
    bl_description = "Select next/previous"
    bl_options = {"REGISTER", "UNDO"}

    previous = BoolProperty(name="Previous", description="Select Next/Previous point", default=False)
    extend = BoolProperty(name="Extend", description="Extend selection", default=False)

    def execute(self, context):
        selectedCurves = context.active_object
        if selectedCurves.type != 'CURVE':
            self.report({'INFO'}, 'Works only on curves')
            return {"CANCELLED"}

        curveData = selectedCurves.data
        for polyline in curveData.splines:  # for strand point
            length = len(polyline.points) if polyline.type == 'NURBS' or polyline.type == 'POLY' else len(polyline.bezier_points)
            if polyline.type == 'NURBS' or polyline.type == 'POLY':
                for i,point in enumerate(polyline.points):
                    if not point.hide and point.select:
                        next_p = max(min(i+1,length-1),0)
                        prev_p = max(min(i-1,length-1),0)
                        index = prev_p if self.previous else next_p
                        if not self.extend:
                            point.select = False
                        polyline.points[index].select = True
                        break
            else:
                for i,point in enumerate(polyline.bezier_points):
                    if not point.hide and point.select:
                        next_p = max(min(i+1,length-1),0)
                        prev_p = max(min(i-1,length-1),0)
                        index = prev_p if self.previous else next_p
                        if not self.extend:
                            point.select = False
                        polyline.bezier_points[index].select = True
                        break
        return {"FINISHED"}


# for custom ui curve mapping panel - wont work in f6 props
def myNodeTree():
    if 'HairToolCurveTmp' not in bpy.data.node_groups:
        ng = bpy.data.node_groups.new('HairToolCurveTmp', 'ShaderNodeTree')
        ng.fake_user = True
    return bpy.data.node_groups['HairToolCurveTmp'].nodes

def myCurveData():
    nt = myNodeTree()
    if "RGB Curves" not in nt.keys():
        nt.new('ShaderNodeRGBCurve')
    return myNodeTree()["RGB Curves"]

class CurvesTaperRadius(bpy.types.Operator):
    bl_label = "Taper Curve"
    bl_idname = "object.curve_taper"
    bl_description = "Taper Curve radius over length"
    bl_options = {"REGISTER", "UNDO"}

    MainRadius = FloatProperty(name="Main Radius", description="Main Radius", default=1, min=0, max=10)
    RootRadius = FloatProperty(name="Root Radius", description="Root Radius Taper", default=1, min=0, max=1, subtype='PERCENTAGE')
    RootRadiusFalloff = FloatProperty(name="Root Radius falloff", description="Radius falloff over strand length", default=0,
                                      min=-1, max=1, subtype='PERCENTAGE')
    TipRadius = FloatProperty(name="Tip Radius", description="Tip Radius Taper", default=0, min=0, max=1, subtype='PERCENTAGE')
    TipRadiusFalloff = FloatProperty(name="Tip Radius falloff", description="Radius falloff over strand length", default=0,
                                     min=-1, max=1, subtype='PERCENTAGE')
    onlySelection = BoolProperty(name="Only Selected", description="Affect only selected points", default=False)

    def invoke(self, context, event):  # make selection only false, if obj mode
        particleObj = context.active_object

        if particleObj.mode == 'EDIT':
            self.onlySelection = True
        elif particleObj.mode == 'OBJECT':
            self.onlySelection = False
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        # self.layout.template_curve_mapping(bpy.data.node_groups['HairToolCurveTmp'].nodes["RGB Curves"], "mapping")
        layout.prop(self, 'MainRadius')
        col = layout.column(align=True)
        col.prop(self, 'RootRadius')
        col.prop(self, 'RootRadiusFalloff')
        col = layout.column(align=True)
        col.prop(self, 'TipRadius')
        col.prop(self, 'TipRadiusFalloff')
        layout.prop(self, 'onlySelection')

    def execute(self, context):
        # myCurveData()
        Curve = context.active_object
        if Curve.type != 'CURVE':
            self.report({'INFO'}, 'Use operator on curve type object')
            return {"CANCELLED"}
        cpowRoot = calc_power(-self.RootRadiusFalloff)
        cpowTip = calc_power(-self.TipRadiusFalloff)
        radius_list_to_len =  defaultdict(list) # spline len : radius list

        curveData = Curve.data
        for polyline in curveData.splines:  # for strand point
            if polyline.type == 'NURBS' or polyline.type == 'POLY':
                if self.onlySelection:
                    selection_test = [0] * len(polyline.points)
                    polyline.points.foreach_get('select', selection_test)
                    if not any(selection_test): continue 
                points = polyline.points
            else:
                if self.onlySelection:
                    selection_test = [0] * len(polyline.points)
                    polyline.bezier_points.foreach_get('select_control_point', selection_test)
                    if not any(selection_test): continue 
                points = polyline.bezier_points
            curveLength = len(points)
            if curveLength not in radius_list_to_len.keys():
                for j in range(curveLength):  # for strand point
                    RadFallof = math.pow(j / curveLength, cpowRoot)
                    RadFallof_tip = math.pow((curveLength-1-j) / curveLength, cpowTip)
                    RadMIx = self.RootRadius *  (1 - RadFallof) +  RadFallof
                    RadMIx_tip = self.TipRadius *  (1 - RadFallof_tip) +  RadFallof_tip
                    radius_list_to_len[curveLength].append(self.MainRadius * RadMIx_tip * RadMIx)  # apply fallof
            if polyline.type == 'NURBS' or polyline.type == 'POLY':
                polyline.points.foreach_set('radius', radius_list_to_len[curveLength])
            else:
                polyline.bezier_points.foreach_set('radius', radius_list_to_len[curveLength])
        Curve.data.update_tag()
        context.area.tag_redraw()
        return {"FINISHED"}


class CurvesTiltAlign(bpy.types.Operator):
    bl_label = "Align curve tilt "
    bl_idname = "object.curves_align_tilt"
    bl_description = "Align curve tilt so that it is aligned to target object surface"
    bl_options = {"REGISTER", "UNDO"}

    onlySelection = BoolProperty(name="Only Selected", description="Affect only selected points", default=True)
    resetTilt = BoolProperty(name="Reset Tilt", description="Reset Tilt before aligning it to surface", default=False)

    def invoke(self, context, event):  # make selection only false, if obj mode
        particleObj = context.active_object
        if particleObj.mode == 'EDIT':
            self.onlySelection = True
        elif particleObj.mode == 'OBJECT':
            self.onlySelection = False
        return self.execute(context)

    @staticmethod
    def find_nearest(p, bvht_tree, searchDistance):
        hitpoint, norm, face_index, distance = bvht_tree.find_nearest(p, searchDistance)  # max_dist = 10
        # hit, hitpoint, norm, face_index = obj.closest_point_on_mesh(p, 10)  # max_dist = 10
        vecP = hitpoint - p
        v = vecP.dot(norm)
        return hitpoint, norm, face_index, distance, v < 0.0  # v<0 = = is inside volume?

    @staticmethod
    def angle_signed(vA, vB, vN):  # angle betwen a - b, is vN space
        a = vA.normalized()
        b = vB.normalized()
        adotb = a.dot(b)  # not sure why but cos(x) goes above 1, and below -1   if a= -b
        if a.dot(b) > 1:
            adotb = 1
        elif a.dot(b) < -1:
            adotb = -1
        angle = math.acos(adotb)
        cross = a.cross(b)
        if vN.dot(cross) < 0:  # // Or > 0
            angle = -angle
        return angle

    @staticmethod
    def get_tangents(me, index, is_last):
        selected_vert = me.vertices[index]
        if is_last:
            prev = me.vertices[index - 3]
            tangent = selected_vert.co - prev.co
        else:
            nextVert = me.vertices[index + 3]
            tangent = nextVert.co - selected_vert.co
        return tangent.normalized()

    def resetTiltFunction(self, curveData):
        for i, polyline in enumerate(curveData.splines):  # for strand point
            if polyline.type == 'NURBS' or polyline.type == 'POLY':
                if self.onlySelection:
                    selection_test = [0] * len(polyline.points)
                    polyline.points.foreach_get('select', selection_test)
                    if not any(selection_test): continue  # if not even one pointis selected
                polyline.points.foreach_set('tilt', [0] * len(polyline.points))
            else:
                if self.onlySelection:
                    selection_test = [0] * len(polyline.bezier_points)
                    polyline.bezier_points.foreach_get('select_control_point', selection_test)
                    if not any(selection_test): continue  # if not even one point is selected
                polyline.bezier_points.foreach_set('tilt', [0] * len(polyline.bezier_points))
                # points = polyline.bezier_points

    def execute(self, context):
        snapTargetName = context.active_object.targetObjPointer
        if snapTargetName not in bpy.data.objects.keys():
            self.report({'INFO'}, 'No target to snap to')
            return {"CANCELLED"}
        snapTarget = bpy.data.objects[snapTargetName]
        Curve = context.active_object
        if not Curve.type == 'CURVE':
            self.report({'INFO'}, 'Use operator on curve type object')
            return {"CANCELLED"}
        snapTarget.data.transform(snapTarget.matrix_world)

        if Curve.mode == 'EDIT':  # to make transfrom() work in edit mode
            bpy.ops.object.mode_set(mode="OBJECT")
            Curve.data.transform(Curve.matrix_world)
            bpy.ops.object.mode_set(mode="EDIT")
        else:
            Curve.data.transform(Curve.matrix_world)
        if self.resetTilt:
            self.resetTiltFunction(Curve.data)
        curveBevelObj = Curve.data.bevel_object  # backup
        context.active_object.data.bevel_object = None  # zero out to prevent changing default one
        curveResU = Curve.data.resolution_u  # backup

        bpy.ops.object.generate_ribbons(strandResV=2, strandResU=curveResU,strandWidth=0.01, strandPeak=0, skipInitProps = True)  # for temp curve for tangent and normals
        # bpy.ops.object.generate_ribbons(strandResV=2, strandResU=12,strandWidth=0.01, strandPeak=0)  # for temp curve for tangent and normals
        # Curve.data.update_tag()
        # context.area.tag_redraw()
        # context.scene.update()
        meFromCurve = Curve.to_mesh(context.scene, True, 'PREVIEW')
        meshVertCount = len(meFromCurve.vertices)
        kdMeshFromCurve = kdtree.KDTree(meshVertCount)
        for i, v in enumerate(meFromCurve.vertices):
            kdMeshFromCurve.insert(v.co, i)
        kdMeshFromCurve.balance()
        curveData = Curve.data

        snapTarget_BVHT_tree = BVHTree.FromObject(snapTarget, context.scene)  # render eg use subsurf render settin
        unitsScale = context.scene.unit_settings.scale_length
        searchDistance = 10 / unitsScale
        angleFlipFix = [-2 * math.pi, -math.pi, 2 * math.pi, math.pi]
        for i, polyline in enumerate(curveData.splines):  # for strand point
            pointsNumber = len(polyline.bezier_points) if polyline.type == 'BEZIER' else len(polyline.points)
            if polyline.type == 'NURBS' or polyline.type == 'POLY':
                if self.onlySelection:
                    test = np.zeros(pointsNumber, dtype=np.bool)
                    polyline.points.foreach_get('select', test)
                    if not any(test): continue  # if not even one pointis selected
                points = polyline.points
            else:
                if self.onlySelection:
                    test = np.zeros(pointsNumber, dtype=np.bool)
                    polyline.bezier_points.foreach_get('select_control_point', test)
                    if not any(test): continue  # if not even one point is selected
                points = polyline.bezier_points
              # helper for tangetnt function (to detect last point on cuve)
            prevAngle = 0
            corrective_angles = np.zeros(pointsNumber, dtype=np.float16)
            current_tilt = np.zeros(pointsNumber, dtype=np.float16)
            points.foreach_get('tilt', current_tilt)

            for j, curvePoint in enumerate(points):  # for strand point
                pointOnMeshLoc, normSnapTarget, face_index, distance, isInside = \
                    self.find_nearest(curvePoint.co.xyz, snapTarget_BVHT_tree, searchDistance)

                # get vertex closest to spline point (for normal) from temp spline representation
                co, index, dist = kdMeshFromCurve.find(curvePoint.co.xyz)
                curveNormal = meFromCurve.vertices[index].normal

                vecSurfaceHit = curvePoint.co.xyz - pointOnMeshLoc
                if isInside:  # if curve point is outside snapSurface flip it
                    vecSurfaceHit *= -1

                # vecSurfaceHit = normSnapTarget * -1  # less accurate but faster...
                if index+3<meshVertCount: #for last spline just use prvevangle
                    tangent = self.get_tangents(meFromCurve, index, j == pointsNumber - 1)  # for bezier we can gets handles for tanget
                    biTangentCurve = tangent.cross(curveNormal)
                    vectSurfHitProjected90 = tangent.cross(vecSurfaceHit)
                    vectSurfHitProjectedToTangent = vectSurfHitProjected90.cross(tangent)
                    # angle = biTangentCurve.angle(vectSurfHitProjectedToTangent)  #unsigned angle 0 - 180
                    angle = self.angle_signed(biTangentCurve, vectSurfHitProjectedToTangent,
                                              tangent) - math.pi / 2  # a,b, vN  - signed -180 to 180
                    if j > 1 and abs(prevAngle - angle) > math.pi / 2:  # try fixing random flips in ribbons surface
                        fix = [fix_angle for fix_angle in angleFlipFix if abs(prevAngle - fix_angle - angle) < math.pi / 2]
                        if len(fix) > 0:
                            angle += fix[0]
                    corrective_angles[j] = angle
                    prevAngle = angle
                else:
                    corrective_angles[j] = prevAngle
            current_tilt = current_tilt + corrective_angles
            if pointsNumber >= 4:
                current_tilt[1] = (current_tilt[2] + current_tilt[3]) / 2
                current_tilt[0] = (current_tilt[1] + current_tilt[2]) / 2
            elif pointsNumber == 3:
                current_tilt[0] = (current_tilt[1] + current_tilt[2]) / 2
            points.foreach_set('tilt', current_tilt.ravel())  # in radians
            # manually smooth first two points cos they are usually broken

        bpy.data.meshes.remove(meFromCurve)
        Curve.data.bevel_object = curveBevelObj  # restore old bevel obj
        snapTarget.data.transform(snapTarget.matrix_world.inverted())
        if Curve.mode == 'EDIT':  # to make transfrom() work in edit mode
            bpy.ops.object.mode_set(mode="OBJECT")
            Curve.data.transform(Curve.matrix_world.inverted())
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            bpy.ops.object.mode_set(mode="EDIT")
        else:
            Curve.data.transform(Curve.matrix_world.inverted())
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        return {"FINISHED"}

class EmbedRoots(bpy.types.Operator):
    bl_label = "Embed Roots"
    bl_idname = "object.embed_roots"
    bl_description = "Embed Roots into target mesh"
    bl_options = {"REGISTER", "UNDO"}

    embed = FloatProperty(name="Embed roots", description="Radius for bezier curve", default=0, min=0, max=10)
    onlySelection = BoolProperty(name="Only Selected", description="Affect only selected points", default=False)

    def invoke(self, context, event):  # make selection only false, if obj mode
        particleObj = context.active_object
        if particleObj.mode == 'EDIT':
            self.onlySelection = True
        elif particleObj.mode == 'OBJECT':
            self.onlySelection = False
        return self.execute(context)

    def execute(self, context):
        Curve = context.active_object
        if not Curve.type == 'CURVE':
            self.report({'INFO'}, 'Use operator on curve type object')
            return {"CANCELLED"}
        snapTargetName = context.active_object.targetObjPointer
        if snapTargetName not in bpy.data.objects.keys():
            self.report({'INFO'}, 'No target to snap to')
            return {"CANCELLED"}
        snapTarget = bpy.data.objects[snapTargetName]
        diagonal = math.sqrt(pow(snapTarget.dimensions[0], 2) + pow(snapTarget.dimensions[1], 2) + pow(snapTarget.dimensions[2], 2))  # to normalize some values
        searchDistance = 100 * diagonal
        embed = self.embed * 0.04 * diagonal

        snapTarget.data.transform(snapTarget.matrix_world)
        Curve.data.transform(Curve.matrix_world)

        sourceSurface_BVHT = BVHTree.FromObject(snapTarget, context.scene)
        for i, polyline in enumerate(Curve.data.splines):  # for strand point
            if self.onlySelection:
                selection_test = [0] * len(polyline.points)
                polyline.points.foreach_get('select', selection_test)
                if not any(selection_test): continue  # if not even one pointis selected
            if polyline.type == 'NURBS' or polyline.type == 'POLY':
                points = polyline.points
            else:
                points = polyline.bezier_points
            snappedPoint, normalChildRoot, rootHitIndex, distance = sourceSurface_BVHT.find_nearest(points[0].co.xyz, searchDistance)
            diff = points[0].co.xyz - points[1].co.xyz
            diff.normalize()
            normalWeight = abs(diff.dot(normalChildRoot))
            points[0].co.xyz += (diff * 0.8 * normalWeight - normalChildRoot * (1 - normalWeight)) * embed  # do childStrandRootNormal to move it more into mesh surface

        Curve.data.transform(Curve.matrix_world.inverted())
        snapTarget.data.transform(snapTarget.matrix_world.inverted())

        return {"FINISHED"}


class CurvesTiltRandomize(bpy.types.Operator):
    bl_label = "Randomize curve tilt"
    bl_idname = "object.curves_randomize_tilt"
    bl_description = "Change curve tilt, can be used for currly hair"
    bl_options = {"REGISTER", "UNDO"}

    onlySelection = BoolProperty(name="Only Selected", description="Affect only selected points", default=True)
    # resetTilt = BoolProperty(name="Reset Tilt", description="Reset Tilt before aligning it to surface", default=True)
    tilt = FloatProperty(name="Tilt Angle", description="Add unifrom tilt to strands", default=1.5, min=0,
                                   max=100, step=145, subtype='ANGLE')
    tiltMixFalloff = FloatProperty(name="Tilt falloff", description="Change braid tilt over strand length", default=0,
                                   min=0, max=1, subtype='PERCENTAGE')
    uniform_tilt = FloatProperty(name="Uniform", description="Make the hair tilt uniform across whole strand length", default=0, min=0,
                                     max=1, subtype='PERCENTAGE')
    randomDirection = BoolProperty(name="Random Direction", description="When false hair will twist only clockwise", default=False)
    noise_ammount = FloatProperty(name="Randomize", description="Tilt randomization strength", default=0.5, min=0,
                                   max=1, subtype='PERCENTAGE')
    Seed = IntProperty(name="Noise Seed", default=1, min=1, max=500)

    def invoke(self, context, event):  # make selection only false, if obj mode
        particleObj = context.active_object
        if particleObj.mode == 'EDIT':
            self.onlySelection = True
        elif particleObj.mode == 'OBJECT':
            self.onlySelection = False
        return self.execute(context)

    def execute(self, context):
        Curve = context.active_object
        if not Curve.type == 'CURVE':
            self.report({'INFO'}, 'Use operator on curve type object')
            return {"CANCELLED"}

        np.random.seed(self.Seed)
        spline_count = len(Curve.data.splines)
        randTiltList = np.random.rand(spline_count)
        cpow = calc_power(self.tiltMixFalloff)
        randDir = np.ones(spline_count, dtype=np.int)
        if self.randomDirection:
            randDir = np.random.choice([1,-1],spline_count)
        for i, polyline in enumerate(Curve.data.splines):  # for strand point
            if polyline.type == 'NURBS' or polyline.type == 'POLY':
                points = polyline.points
            else:
                points = polyline.bezier_points
            pointsNumber = len(points)
            if self.onlySelection:
                if polyline.type == 'NURBS' or polyline.type == 'POLY':
                    points = [point for point in points if point.select]
                else:  # bezier
                    points = [point for point in points if point.select_control_point]
            for j, curvePoint in enumerate(points):  # for strand point
                strand_Fallof = math.pow(j / pointsNumber, cpow)
                uniform_factor  = randTiltList[i] * self.noise_ammount + 1*(1-self.noise_ammount)
                randomizedAngle = self.tilt *randDir[i]* (uniform_factor *  (strand_Fallof * (1 - self.uniform_tilt) + self.uniform_tilt))
                curvePoint.tilt += randomizedAngle  # in radians
        return {"FINISHED"}

interpolation_items = (("LINEAR", "Linear", ""),
                       ("BSPLINE", "Bspline", ""),
                       ("CARDINAL", "Cardinal", ""))

class CurvesSmooth(bpy.types.Operator):
    '''np didnt improve situation much'''
    bl_label = "Smooth curve"
    bl_idname = "object.curves_smooth"
    bl_description = "Smooth curve points"
    bl_options = {"REGISTER", "UNDO"}

    onlySelection = BoolProperty(name="Only Selected", description="Affect only selected points", default=True)
    smooth = IntProperty(name="Smooth iterations", default=1, min=0, max=20)
    advanced = BoolProperty(name="Advanced Options", description="Advanced Options (ony available when Only Selection is disabled)", default=False)
    nurbs_order = IntProperty(name="Nurbs Order", default=3, min=2, max=6)
    tilt_interpols = bpy.props.EnumProperty(name="Tilt Interpolation", default="BSPLINE", items=interpolation_items)
    radius_interpol = bpy.props.EnumProperty(name="Radius Interpolation", default="BSPLINE", items=interpolation_items)

    def check(self, context):  # DONE: can prop panel be fixed/refreshed when using f6 prop popup
        return True

    @staticmethod
    def smooth3d(splines_points, selection_mask=None):
        '''Smooth by averging a[n-1]+ a[n]+ a[n+1]/3 - by x,y,z,1 axis'''
        if len(selection_mask)>0:
            for points, selection in zip(splines_points, selection_mask):
                sel_points = points[selection]
                sel_points[1:-1,:]=(sel_points[ 2:,:] + sel_points[:-2,:] + 4*sel_points[1:-1,:])/6
                points[selection]=sel_points
        else:
            for points in splines_points:
                points[1:-1, :] = (points[2:, :] + points[:-2, :] + 4*points[1:-1, :]) / 6

    def draw(self, context):
        Curve = context.active_object
        active_spline_type = Curve.data.splines[0].type
        layout = self.layout
        box = layout.box()
        box.label("Curve Smooth")
        box.prop(self, 'onlySelection')
        box.prop(self, 'smooth')
        if not self.onlySelection:
            box.prop(self, 'advanced')
            if self.advanced:
                col = box.column(align=True)
                if active_spline_type == 'NURBS':
                    col.prop(self, 'nurbs_order')
                elif active_spline_type == 'BEZIER':
                    col.prop(self, 'tilt_interpols')
                    col.prop(self, 'radius_interpol')

    def invoke(self, context, event):  # make selection only false, if obj mode
        Curve = context.active_object
        if not Curve.type == 'CURVE':
            self.report({'INFO'}, 'Use operator on curve type object')
            return {"CANCELLED"}
        if Curve.mode == 'EDIT':
            self.onlySelection = True
        elif Curve.mode == 'OBJECT':
            self.onlySelection = False
        self.nurbs_order = Curve.data.splines[0].order_u
        return self.execute(context)

    def execute(self, context):
        Curve = context.active_object
        splines_points = []
        splines_sel_points = []
        for polyline in Curve.data.splines:
            pointCount =len(polyline.points)
            points = np.zeros(pointCount*4, dtype=np.float32) #x,y,z,1
            polyline.points.foreach_get('co', points)
            points.shape = (pointCount,4)
            splines_points.append(points)
            if self.onlySelection is True:
                selection = np.zeros(pointCount, dtype=np.bool) #x,y,z,1
                polyline.points.foreach_get('select', selection)
                splines_sel_points.append(selection)
        for i in range(self.smooth):
            self.smooth3d(splines_points,splines_sel_points)
        for polyline, new_points in zip(Curve.data.splines,splines_points):
            polyline.points.foreach_set('co', new_points.ravel())
        Curve.data.update_tag()
        context.area.tag_redraw()


        if not self.onlySelection and self.advanced:
            active_spline_type = Curve.data.splines[0].type
            for polyline in Curve.data.splines:  # foreach dont work
                if polyline.type == 'NURBS' and active_spline_type == 'NURBS':
                    polyline.order_u = self.nurbs_order
                elif polyline.type == 'BEZIER' and active_spline_type == 'BEZIER':
                    polyline.tilt_interpolation = self.tilt_interpols
                    polyline.radius_interpolation = self.radius_interpols

        return {"FINISHED"}

class CurvesTiltSmooth(bpy.types.Operator):
    bl_label = "Smooth tilt"
    bl_idname = "object.curves_smooth_tilt"
    bl_description = "Smooth curve tilt"
    bl_options = {"REGISTER", "UNDO"}

    onlySelection = BoolProperty(name="Only Selected", description="Affect only selected points", default=True)
    strength = IntProperty(name="Smooth strength", default=3, min=0, max=10)

    def invoke(self, context, event):  # make selection only false, if obj mode
        particleObj = context.active_object
        if particleObj.mode == 'EDIT':
            self.onlySelection = True
        elif particleObj.mode == 'OBJECT':
            self.onlySelection = False
        return self.execute(context)

    @staticmethod
    def smooth(points, box_pts):
        len_y = len(points)
        smoothed = []
        for i in range(len(points)):
            low = max(0, i - box_pts)
            hi = min(len_y, i + box_pts)
            divide = hi - low
            smoothed.append(np.sum(points[low:hi]) / divide)  # average
        return smoothed

    @staticmethod
    def smooth1d(splines_points, selection_mask=None):
        '''Smooth by averging a[n-1]+ a[n]+ a[n+1]/3 - by x,y,z,1 axis'''
        if len(selection_mask) > 0:
            for points, selection in zip(splines_points, selection_mask):
                sel_points = points[selection]
                sel_points[1:-1] = (sel_points[2:] + sel_points[:-2] + 4 * sel_points[1:-1]) / 6
                points[selection] = sel_points
        else:
            for points in splines_points:
                points[1:-1] = (points[2:] + points[:-2] + 4 * points[1:-1]) / 6

    def execute(self, context):
        Curve = context.active_object
        if not Curve.type == 'CURVE':
            self.report({'INFO'}, 'Use operator on curve type object')
            return {"CANCELLED"}

        Curve = context.active_object
        splines_points = []
        splines_sel_points = []
        for polyline in Curve.data.splines:
            pointCount = len(polyline.points)
            points = np.zeros(pointCount, dtype=np.float32)  # x,y,z,1
            polyline.points.foreach_get('tilt', points)
            splines_points.append(points)
            if self.onlySelection is True:
                selection = np.zeros(pointCount, dtype=np.bool)  # x,y,z,1
                polyline.points.foreach_get('select', selection)
                splines_sel_points.append(selection)
        for i in range(self.strength):
            self.smooth1d(splines_points, splines_sel_points)
        for polyline, new_points in zip(Curve.data.splines, splines_points):
            polyline.points.foreach_set('tilt', new_points.ravel())
        Curve.data.update_tag()
        context.area.tag_redraw()
        return {"FINISHED"}


class CurvesTiltReset(bpy.types.Operator):
    bl_label = "Reset curve tilt"
    bl_idname = "object.curves_reset_tilt"
    bl_description = "Reset curve tilt"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        Curve = context.active_object
        if not Curve.type == 'CURVE':
            self.report({'INFO'}, 'Use operator on curve type object')
            return {"CANCELLED"}

        for polyline in Curve.data.splines:  # just nurbs and polyline
            curveTiltList = np.zeros(len(polyline.points), dtype= np.float16)
            polyline.points.foreach_set('tilt', curveTiltList)
        Curve.data.update_tag()
        return {"FINISHED"}


class CurvesRadiusSmooth(bpy.types.Operator):
    bl_label = "Smooth radius"
    bl_idname = "object.curves_smooth_radius"
    bl_description = "Smooth curve radius"
    bl_options = {"REGISTER", "UNDO"}

    onlySelection = BoolProperty(name="Only Selected", description="Affect only selected points", default=True)
    strength = IntProperty(name="Smooth strength", default=3, min=1, max=10)

    def invoke(self, context, event):  # make selection only false, if obj mode
        particleObj = context.active_object
        if particleObj.mode == 'EDIT':
            self.onlySelection = True
        elif particleObj.mode == 'OBJECT':
            self.onlySelection = False
        return self.execute(context)

    @staticmethod
    def smooth(y, box_pts):
        len_y = len(y)
        smoothed = []
        for i in range(len(y)):
            low = max(0, i - box_pts)
            hi = min(len_y, i + box_pts)
            smoothed.append(np.sum(y[low:hi]) / (hi - low))  # average
        return smoothed

    def execute(self, context):
        Curve = context.active_object
        if not Curve.type == 'CURVE':
            self.report({'INFO'}, 'Use operator on curve type object')
            return {"CANCELLED"}

        for i, polyline in enumerate(Curve.data.splines):  # for strand point
            if polyline.type == 'NURBS' or polyline.type == 'POLY':
                points = polyline.points
            else:
                points = polyline.bezier_points
            if self.onlySelection:
                if polyline.type == 'NURBS' or polyline.type == 'POLY':
                    points = [point for point in points if point.select]
                else:  # bezier
                    points = [point for point in points if point.select_control_point]
            curveRadiusList = [curvePoint.radius for curvePoint in points]
            smoothedRaadius = self.smooth(curveRadiusList, self.strength)
            for j, curvePoint in enumerate(points):  # for strand point
                curvePoint.radius = smoothedRaadius[j]
        return {"FINISHED"}

