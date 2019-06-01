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
from math import  pow
from random import uniform, seed
import numpy as np
from .ribbons_operations import CurvesUVRefresh
from mathutils import Vector, kdtree, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
from .resample2d import interpol
from .particle_hair import RibbonsFromParticleHairChild
import bgl
# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb

# def handleHandlers():
#     modal_hair_settings = bpy.context.scene.modal_hair
#
#     if modal_hair_settings.runModalHair:
#         if (hair_modal not in bpy.app.handlers.scene_update_post):
#             global last_time
#             last_time = time.time()
#             bpy.app.handlers.scene_update_post.append(hair_modal)
#             print('starting hair_modal')
#     else:
#         remList = []
#         for h in bpy.app.handlers.scene_update_post:
#             if h == hair_modal:  #or h.__name__ == "hair_modal"
#                 remList.append(h)
#         for h in remList:
#             bpy.app.handlers.scene_update_post.remove(h)
#             print('finishing hair_modal')

def draw_callback_px(self, context):
    particleObj = bpy.context.active_object
    if particleObj is None or bpy.context.scene.modal_hair.runModalHair is False or bpy.context.scene.modal_hair.drawStrands is False:
        return
    partsysMod = particleObj.particle_systems.active  # use last
    if partsysMod is None:
        return
    #strands_points.append(np.einsum('ij,aj->ai', mat, points_to_vec)) #mat times point list
    strands_points = []
    averageCoord = Vector((0, 0, 0))
    for particle in partsysMod.particles:  # for strand point
        strands_points.append([particleObj.matrix_world * hair_key.co.xyz for hair_key in particle.hair_keys])
        averageCoord += strands_points[-1][0] #use rotts for average
    averageCoord = averageCoord/len(strands_points)
    g_rv3d = context.region_data
    camera_pos = g_rv3d.view_matrix.inverted().translation
    camDistance = camera_pos - averageCoord
    length = camDistance.length_squared
    maxRange = 1 - (bpy.context.scene.modal_hair.drawOffset / length) / 20

    bgl.glLineWidth(2)
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glEnable(bgl.GL_DEPTH_TEST)
    bgl.glDepthRange(0, maxRange)
    bgl.glColor4f(1, 0.5, 0, 0.5)
    for strand in strands_points:
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for point in strand:
            bgl.glVertex3f(point[0], point[1], point[2])
        bgl.glEnd()
    # restore opengl defaults
    bgl.glDepthRange(0, 1)
    bgl.glDisable(bgl.GL_DEPTH_TEST)
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

handle = []

def drawHair():
    if bpy.context.scene.modal_hair.runModalHair:
        if handle:
            bpy.types.SpaceView3D.draw_handler_remove(handle[0], 'WINDOW')
        args = (ModalHairSettings, bpy.context)  # u can pass arbitrary class as first param  Instead of (self, context)
        handle[:] = [bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_VIEW')]
    else:
        if handle:
            bpy.types.SpaceView3D.draw_handler_remove(handle[0], 'WINDOW')
            handle[:] = []


class ModalHairSettings(bpy.types.PropertyGroup):
    def modalHairCheck(self,context):
        drawHair()
        bpy.ops.object.modal_hair_refresh('INVOKE_DEFAULT') #seemsSmoother
        # handleHandlers()

    def reset_tilt_run(self, context):
        particleObj  = context.active_object
        partsysMod = particleObj.particle_systems.active  # use first
        targetCurve_name = partsysMod.name  #from 'modal_hair_refresh'
        context.scene.objects.active = bpy.data.objects[targetCurve_name]
        bpy.ops.object.curves_reset_tilt()
        context.scene.objects.active = particleObj
        self['resetTilt'] = False
        self['smoothTiltStrength'] = 0
        self.alignToSurface = False

    def smooth_tilt_check(self, context):
        if not self.alignToSurface:
            self['smoothTiltStrength'] = 0

    runModalHair = BoolProperty(name="Interactive Curve Ribbons", description="Create and run interactive updates on curve ribbons hair", default=False, update=modalHairCheck)
    embed = BoolProperty(name="Embed Roots", description="Embed hair roots inside source surface geometry", default=False)
    with_children = BoolProperty(name="Generate children", description="Generate children hairs (require at least three parent strands)", default=False)
    embedValue = FloatProperty(name="Embed Roots Depth", description="Embed curve ribbons roots depth", default=0, min=0, max=10)
    t_in_y = IntProperty(name="Strand Segments", default=5, min=2, max=20)
    smooth_curves = IntProperty(name="Strand Smoothing", default=0, min=0, max=6)
    hairType = bpy.props.EnumProperty(name="Hair Type", default="NURBS",
                                      items=(("NURBS", "Nurbs", ""),
                                             ("POLY", "Poly", "")))
    alignToSurface = BoolProperty(name="Tilt aligning", description="Enable interactive aligning curve ribbons to target surface", default=False)
    smoothTiltStrength = IntProperty(name="Tilt smoothing strength", description="Enable tilt smoothing \n Works only when \'Tilt Aligning\' is enabled",
                                     default=0, min=0, max=5, update=smooth_tilt_check)
    resetTilt = BoolProperty(name="Reset tilt", description="Reset curve ribbon tilt", default=False, update=reset_tilt_run)
    childCount = IntProperty(name="Child count", default=100, min=10, soft_max=2000)
    PlacementJittering = FloatProperty(name="Placement Jittering/Face", description="Placement Jittering/Face \n"
                                                                                    "Helps even out particle distribution \n"
                                                                                    "0 = automatic", default=0, min=0, max=100, subtype='PERCENTAGE')
    lenSeed = IntProperty(name="Length Seed", default=1, min=1, max=1000)
    RandomizeLengthPlus = FloatProperty(name="Increase length randomly", description="Increase length randomly", default=0, min=0, max=1, subtype='PERCENTAGE')
    RandomizeLengthMinus = FloatProperty(name="Decrease length randomly", description="Decrease length randomly", default=0, min=0, max=1, subtype='PERCENTAGE')

    drawStrands = BoolProperty(name="Draw Parent Strands", description="Draw orange overlay on top of parent strands", default=False)
    drawOffset = bpy.props.FloatProperty(name="Parent Strand Draw Offset", description="Parent Strand Draw Offset", min=0.0, max=1.0, default=0.5, subtype='FACTOR')

class VIEW3D_PT_Hair_Panel(bpy.types.Panel):
    bl_label = "Modal Hair Tool"
    bl_idname = "hair_tool_modal"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Tools"
    bl_context = "particlemode"


    def draw(self, context):
        modal_hair_settings = context.scene.modal_hair
        layout = self.layout
        box = layout.box()
        box.label("Interactive curve ribbons hair:")
        box.prop(modal_hair_settings, 'runModalHair', icon = "PARTICLEMODE")
        box.prop(modal_hair_settings, 'hairType')
        box.prop(modal_hair_settings, 't_in_y')
        row = box.row(align=True)
        row.prop(modal_hair_settings, 'embed', icon_only=True, icon="MOD_SCREW", emboss=False)
        row.prop(modal_hair_settings, 'embedValue',icon="MOD_SCREW")
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(modal_hair_settings, 'alignToSurface', icon_only=False, icon="SNAP_NORMAL")
        row.prop(modal_hair_settings, 'resetTilt', icon_only=False, icon="BLANK1", emboss=True)
        row = col.row(align=True)
        row.prop(modal_hair_settings, 'smoothTiltStrength')
        box.prop(modal_hair_settings, 'smooth_curves', icon_only=False, icon="MOD_SMOOTH")
        row = box.row(align=True)
        row.prop(modal_hair_settings, 'drawStrands', icon_only=True, icon="PARTICLE_PATH", emboss=True)
        row.prop(modal_hair_settings, 'drawOffset')
        box.prop(modal_hair_settings, 'with_children')
        if modal_hair_settings.with_children:
            col = box.column(align=True)
            col.prop(modal_hair_settings, 'childCount')
            col.prop(modal_hair_settings, 'PlacementJittering')
            col.prop(modal_hair_settings, 'lenSeed')
            col.prop(modal_hair_settings, 'RandomizeLengthPlus')
            col.prop(modal_hair_settings, 'RandomizeLengthMinus')



last_operation=[]

def get_undo_stack2(context):  #whene using deletin it triggers update twice....
    bpy.ops.ui.reports_to_textblock()  #write info report to 'Recent Reports.txt'
    if len( bpy.data.texts['Recent Reports'].lines)>1:
        lastReport  = bpy.data.texts['Recent Reports'].lines[-2].body
    else:
        lastReport = []
    bpy.data.texts.remove(bpy.data.texts['Recent Reports'])
    ctx = get_info_area_context()
    area_type = not ctx and context.area.type
    args = []  # to force Correct context
    if ctx:
        args.append(ctx)
    else:  #if no info area in window switch to info
        context.area.type = 'INFO'
    bpy.ops.info.select_all_toggle(*args)
    bpy.ops.info.report_delete(*args)
    if area_type:
        context.area.type = area_type
    return lastReport

def get_info_area_context():
    area = None
    for a in bpy.context.screen.areas:
        if a.type == 'INFO':
            area = a
            break

    if not area:
        return None

    return {
        "area": area,
        "window": bpy.context.window,
        "screen": bpy.context.screen
    }

ignore_list = ignored_operators = [
        "bpy.ops.object.embed_roots",
        "bpy.ops.object.curves_smooth",
        "bpy.ops.object.generate_ribbons",
        "bpy.ops.object.curves_align_tilt",
        "bpy.ops.object.curves_smooth_tilt",
        "bpy.ops.object.modal_hair_refresh",
    ]
    
def get_undo_stack(context): #seems faster than copy to text editor (breaks ctrl+c sometimes...)
    ctx = get_info_area_context()
    area_type = not ctx and context.area.type

    args = []       #to force Correct context
    if ctx:
        args.append(ctx)
    else:
        context.area.type = 'INFO'
    clipboardBack = context.window_manager.clipboard
    bpy.ops.info.select_all_toggle(*args)
    bpy.ops.info.report_copy(*args)
    text = context.window_manager.clipboard
    if not text:
        bpy.ops.info.select_all_toggle(*args)
        bpy.ops.info.report_copy(*args)
    bpy.ops.info.report_delete(*args)
    # bpy.ops.info.select_all_toggle(*args)
    if area_type:
        context.area.type = area_type
    text = context.window_manager.clipboard
    report= text.splitlines()
    context.window_manager.clipboard = clipboardBack
    if len(report)==0:
        return ""
    global ignore_list
    for ignore in ignore_list:
        if report[-1].startswith(ignore):
            return ""
    return report[-1]

class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "object.modal_hair_refresh"
    bl_label = "Modal Timer Operator"
    bl_options = {"REGISTER", "UNDO"}

    particleObj = None

    def create_hair(self,context):
        '''Do this on init() once'''
        particleObj = self.particleObj = context.active_object
        partsysMod = particleObj.particle_systems.active  # use first
        self.sourceSurface_BVHT = BVHTree.FromObject(particleObj, context.scene) #only for chair with children - calculate in once on init
        hair_name = partsysMod.name
        if hair_name not in bpy.data.objects.keys():
            curveData = bpy.data.curves.new(partsysMod.name + '_curve', type='CURVE')
            curveObj = bpy.data.objects.new(hair_name, curveData)
            curveObj.matrix_world = particleObj.matrix_world
            context.scene.objects.link(curveObj)
            curveObj.select = True
            curveObj.data.show_normal_face = False
            curveObj.data.dimensions = '3D'
            curveObj.targetObjPointer = particleObj.name  # store source surface for snapping oper
            self.curveObj = curveObj
            self.hair_ribbon_update(context)
        else:
            curveObj = bpy.data.objects[hair_name]
        self.curveObj = curveObj

        if not curveObj.data.bevel_object:
            context.scene.objects.active = curveObj
            bpy.context.scene.update()
            bpy.ops.object.generate_ribbons(strandResU=3, strandResV=2,
                                        strandWidth=0.5, strandPeak=0.3,
                                        strandUplift=-0.2, alignToSurface=False)
            CurvesUVRefresh.uvCurveRefresh(curveObj)
            context.scene.objects.active = particleObj


    def particle_hair_to_points_with_children(self,context):
        modal_hair_settings = context.scene.modal_hair
        particleObj = self.particleObj
        partsysMod = particleObj.particle_systems.active  # use last
        pointsList_hair = []
        # context.scene.update()
        diagonal = pow(particleObj.dimensions[0], 2) + pow(particleObj.dimensions[1], 2) + pow(particleObj.dimensions[2], 2)  # diagonal -to normalize some values
        if len(partsysMod.particles)==0: #require more that three strands
            return self.particle_hair_to_points(context)
        for particle in partsysMod.particles:  # for strand point
            pointsList_hair.append([hair_key.co for hair_key in particle.hair_keys])  # DONE: exclude duplicates if first strand[0] in list already
        if len(partsysMod.particles) == 1: #create two fake strands so that barycentric works
            pointsList_hair.append([x.xyz+Vector((0.01*diagonal, 0, 0)) for x in pointsList_hair[0]])
            pointsList_hair.append([x.xyz+Vector((0 ,0.01*diagonal, 0)) for x in pointsList_hair[0]])
        elif len(partsysMod.particles) == 2: #create one fake strands so that barycentric works
            pointsList_hair.append([x.xyz+Vector((0.01*diagonal, 0, 0)) for x in pointsList_hair[0]])

        pointsList_uniq = []
        [pointsList_uniq.append(x) for x in pointsList_hair if x not in pointsList_uniq]  # removing doubles (can cause zero size tris)

        # constantLen cos barycentric transform requires it
        pointsList = interpol(pointsList_uniq, modal_hair_settings.t_in_y, uniform=True, constantLen=True)  # just gives smoother result on borders
        searchDistance = 100 *diagonal
        parentRoots = [strand[0] for strand in pointsList]  # first point of roots
        # create nnew Part Sytem with uniform points
        pointsChildRoots = RibbonsFromParticleHairChild.createUniformParticleSystem(context, modal_hair_settings.childCount, modal_hair_settings.PlacementJittering)  # return child part roots positions

        kd = kdtree.KDTree(len(parentRoots))
        for i, root in enumerate(parentRoots):
            kd.insert(root, i)
        kd.balance()
        sourceSurface_BVHT = self.sourceSurface_BVHT
        childStrandsPoints = []  # will contain strands with child points
        childStrandRootNormals = []
        seed(a=modal_hair_settings.lenSeed, version=2)
        for i, childRoot in enumerate(pointsChildRoots):  # for each child find it three parents and genereate strands by barycentric transform
            snappedPoint, normalChildRoot, rootHitIndex, distance = sourceSurface_BVHT.find_nearest(childRoot, searchDistance)
            childStrandRootNormals.append(normalChildRoot)
            threeClosestParentRoots = kd.find_n(childRoot, 3)  # find three closes parent roots
            rootTri_co, ParentRootIndices, distances = zip(*threeClosestParentRoots)  # split it into 3 arrays
            sourceTri_BVHT = BVHTree.FromPolygons(rootTri_co, [(0, 1, 2)], all_triangles=True)  # [0,1,2] - polygon == vert indices list
            childRootSnapped, normalChildProjected, index, distance = sourceTri_BVHT.find_nearest(childRoot, searchDistance)  # snap generated child to parent triangle ares \normals are sometimes flipped
            childRootSnapped2, normalChildProjected2, index2, distance2 = sourceSurface_BVHT.find_nearest(childRootSnapped, searchDistance)  # this gives ok normals always

            lenWeight = 1 + uniform(-modal_hair_settings.RandomizeLengthMinus, modal_hair_settings.RandomizeLengthPlus)
            rotQuat = normalChildProjected2.rotation_difference(normalChildRoot)
            translationMatrix = Matrix.Translation(childRoot)
            rotMatrixRot = rotQuat.to_matrix().to_4x4()
            mat_sca = Matrix.Scale(lenWeight, 4)
            transformMatrix = translationMatrix * rotMatrixRot
            strandPoints = []
            # for childRootSnapped points transform them from parent root triangles to parent next segment triangle t1,t2,t3
            # and compensate child snapping to root triangle from before
            for j, (t1, t2, t3) in enumerate(zip(pointsList[ParentRootIndices[0]], pointsList[ParentRootIndices[1]], pointsList[ParentRootIndices[2]])):
                pointTransformed = barycentric_transform(childRootSnapped, rootTri_co[0], rootTri_co[1], rootTri_co[2], Vector(t1), Vector(t2), Vector(t3))
                childInterpolatedPoint = transformMatrix * mat_sca * (pointTransformed - childRootSnapped)  # rotate child strand to original pos (from before snapt)
                strandPoints.append(childInterpolatedPoint)
            childStrandsPoints.append(strandPoints)
        return childStrandsPoints


    def particle_hair_to_points(self,context):
        modal_hair_settings = context.scene.modal_hair
        particleObj = self.particleObj
        partsysMod = particleObj.particle_systems.active  # use last
        splinesPointsList = []
        extendList = []
        for strand in partsysMod.particles:  # for strand point
            extendList.append([hair_key.co for hair_key in strand.hair_keys])
        if len(extendList) > 0:
            splinesPointsList.extend(interpol(extendList, modal_hair_settings.t_in_y, uniform=False, constantLen=True))
        return splinesPointsList


    def hair_ribbon_update(self, context):
        modal_hair_settings = context.scene.modal_hair
        particleObj = self.particleObj
        curveData = self.curveObj.data
        if modal_hair_settings.with_children is True:
            splinesPointsList = self.particle_hair_to_points_with_children(context)
        else:
            splinesPointsList = self.particle_hair_to_points(context)

        if len(splinesPointsList)==0:
            return

        splinePointsNpOnes = np.ones((len(splinesPointsList), modal_hair_settings.t_in_y, 4), dtype=np.float32)  # 4 coord x,y,z ,1
        splinePointsNpOnes[:, :, :-1] = splinesPointsList  # fill x,y,z - exept last row (1)- for size
        #fix strands point count
        spline_count = len(curveData.splines)
        if spline_count>0:
            strand_len_diff = len(curveData.splines[0].points) - modal_hair_settings.t_in_y
            if strand_len_diff > 0:  # delete last point in loop
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                context.scene.objects.active = self.curveObj
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.curve.select_tips(roots=False)
                for i in range(strand_len_diff - 1):
                    bpy.ops.curve.select_more()
                bpy.ops.curve.delete(type='VERT')
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                context.scene.objects.active = particleObj
                bpy.ops.object.mode_set(mode='PARTICLE_EDIT', toggle=False)
            elif strand_len_diff < 0:
                for polyline in curveData.splines:
                    polyline.points.add(-strand_len_diff)

        # fix strands count
        spline_count_diff = spline_count - len(splinePointsNpOnes)
        if spline_count_diff > 0:
            for i in reversed(range(spline_count_diff)):
                curveData.splines.remove(curveData.splines[-i-1])
        elif spline_count_diff < 0:
            if spline_count>0:
                first_spline_radius = np.zeros(modal_hair_settings.t_in_y, dtype=np.float16)
                first_spline_tilt = np.zeros(modal_hair_settings.t_in_y, dtype=np.float16)
                curveData.splines[0].points.foreach_get('radius', first_spline_radius)
                curveData.splines[0].points.foreach_get('tilt', first_spline_tilt)
            for i in range(-spline_count_diff):
                polyline = curveData.splines.new(modal_hair_settings.hairType)
                polyline.points.add(modal_hair_settings.t_in_y - 1)
                if spline_count > 0: #set radii from example first spline
                    polyline.points.foreach_set('radius', first_spline_radius)
                    polyline.points.foreach_set('tilt', first_spline_tilt)
                if modal_hair_settings.hairType == 'NURBS':
                    polyline.order_u = 3
                    polyline.resolution_u = self.curveObj.data.resolution_u
                    polyline.use_endpoint_u = True
            CurvesUVRefresh.uvCurveRefresh(self.curveObj, self.curveObj.hair_settings.uv_seed)

        for polyline, splinePoints in zip(curveData.splines,splinePointsNpOnes):
            polyline.points.foreach_set("co", splinePoints.ravel())
        curveData.update_tag()
        context.scene.objects.active = self.curveObj
        if modal_hair_settings.embedValue > 0:
            bpy.ops.object.embed_roots(onlySelection=False,  embed = modal_hair_settings.embedValue)
        if modal_hair_settings.smooth_curves > 0:
            bpy.ops.object.curves_smooth(onlySelection=False,  smooth = modal_hair_settings.smooth_curves)
        if modal_hair_settings.alignToSurface is True:
            bpy.ops.object.curves_align_tilt(onlySelection=False, resetTilt = True)
            if modal_hair_settings.smoothTiltStrength > 0:
                bpy.ops.object.curves_smooth_tilt(onlySelection=False, strength=modal_hair_settings.smoothTiltStrength)
        context.scene.objects.active = self.particleObj

    def finish(self,context):
        context.scene.modal_hair.runModalHair = False
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    def modal(self, context, event):
        if event.type in { 'ESC'}:
            self.finish(context)
            return {'CANCELLED'}

        elif event.type == 'TIMER':
            global last_operation
            if context.mode != 'PARTICLE':
                self.finish(context)
                return {'CANCELLED'}
            undo_stack = get_undo_stack(context)
            if undo_stack != last_operation and undo_stack!="":
                last_operation = undo_stack
                partsysMod = self.particleObj.particle_systems.active  # use first
                if partsysMod.name not in bpy.data.objects.keys():
                    self.create_hair(context)
                self.curveObj = bpy.data.objects[partsysMod.name]
                self.hair_ribbon_update(context)
                # print("Updating modal particle")
        elif event.ctrl and event.type == 'Z' and event.value == 'RELEASE':
            self.hair_ribbon_update(context)

        if context.scene.modal_hair.runModalHair is False:
            return {'FINISHED'}
        return {'PASS_THROUGH'}


    def invoke(self, context, event):
        self.create_hair(context)
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.35, context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}







