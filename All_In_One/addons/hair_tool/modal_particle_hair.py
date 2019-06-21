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
from .ribbons_operations import HT_OT_CurvesUVRefresh
from mathutils import Vector, kdtree, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
from .resample2d import  interpol_Catmull_Rom
from .particle_hair import HT_OT_RibbonsFromParticleHairChild
from .hair_curve_helpers import HT_OT_EmbedRoots,  HT_OT_CurvesTiltAlign,  HT_OT_CurvesTiltSmooth
import bgl
import gpu
from .hair_curve_helpers import get_obj_mesh_bvht
from gpu_extras.batch import batch_for_shader

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
shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
EVAL_PARTICLE_OBJ = None #hold proper hair_keys.co
PARTICLE_CO = [(0, 0, 0)] #for faster drawing postpixel


def draw_callback_px(self, context):
    global EVAL_PARTICLE_OBJ
    particleObj = EVAL_PARTICLE_OBJ 
    # particleObj = bpy.context.active_object.
    settings_modal = bpy.context.active_object.modal_hair
    if particleObj is None or settings_modal.runModalHair is False or settings_modal.drawStrands is False:
        return
    partsysMod = particleObj.particle_systems.active  # use last
    if partsysMod is None:
        return
    global shader
    #strands_points.append(np.einsum('ij,aj->ai', mat, points_to_vec)) #mat times point list
    strands_points = []
    averageCoord = Vector((0, 0, 0))
    for particle in partsysMod.particles:  # for strand point
        strands_points.append([particleObj.matrix_world @ hair_key.co.xyz for hair_key in particle.hair_keys])
        averageCoord += strands_points[-1][0] #use rotts for average
    averageCoord = averageCoord/len(strands_points)
    g_rv3d = context.region_data
    camera_pos = g_rv3d.view_matrix.inverted().translation
    camDistance = camera_pos - averageCoord
    length = camDistance.length_squared
    maxRange = 1 - (particleObj.modal_hair.drawOffset / length) / 20
    color = particleObj.modal_hair.draw_color
    bgl.glLineWidth(2)
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glEnable(bgl.GL_DEPTH_TEST)
    bgl.glDepthRange(0, maxRange)
    
    
    batch = batch_for_shader(shader, 'LINES', {"pos": PARTICLE_CO})
    shader.bind()
    shader.uniform_float("color", (color[0], color[1], color[2], color[3]))
    batch.draw(shader)
    # restore opengl defaults
    bgl.glDepthRange(0, 1)
    bgl.glDisable(bgl.GL_DEPTH_TEST)
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)

handle = []

def drawHair(context):
    if context.active_object.modal_hair.runModalHair:
        if handle:
            bpy.types.SpaceView3D.draw_handler_remove(handle[0], 'WINDOW')
        args = (ModalHairSettings, bpy.context)  # u can pass arbitrary class as first param  Instead of (self, context)
        handle[:] = [bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_VIEW')]
    else:
        if handle:
            bpy.types.SpaceView3D.draw_handler_remove(handle[0], 'WINDOW')
            handle[:] = []


class ParticleModalSettings(bpy.types.PropertyGroup):
    def reset_tilt_run(self, context):
        particleObj  = context.active_object
        partsysMod = particleObj.particle_systems.active  # use first
        targetCurve_name = partsysMod.name  #from 'modal_hair_refresh'
        context.view_layer.objects.active = bpy.data.objects[targetCurve_name]
        bpy.ops.object.curves_reset_tilt()
        context.view_layer.objects.active = particleObj
        self['resetTilt'] = False
        self['smoothTiltStrength'] = 0
        self.alignToSurface = False

    def smooth_tilt_check(self, context):
        if not self.alignToSurface:
            self['smoothTiltStrength'] = 0
        else:
            self.run_update(context)

    def run_update(self, context):
        #do some fake operation to force model hair update
        global FORCE_UPDATE
        FORCE_UPDATE = True

    def update_width(self, context):
        part_name = context.active_object.particle_systems.active.name
        if part_name in context.scene.objects.keys():
            obj = bpy.data.objects[part_name]
            if obj.type !='CURVE':
                return
            back_active = context.view_layer.objects.active
            context.view_layer.objects.active = obj
            if obj.ribbon_settings:  # use init settings if  they are != defaults, else use stored values
                strandResU = obj.ribbon_settings.strandResU
                strandResV = obj.ribbon_settings.strandResV
                strandPeak = obj.ribbon_settings.strandPeak
                strandUplift = obj.ribbon_settings.strandUplift
                bpy.ops.object.generate_ribbons(strandResU=strandResU, strandResV=strandResV,
                                                strandWidth=self.strand_width, strandPeak=strandPeak,
                                                strandUplift=strandUplift)
            else:
                bpy.ops.object.generate_ribbons(strandWidth=self.strand_width, alignToSurface=False)
            context.view_layer.objects.active = back_active

    with_children: BoolProperty(name="Generate children",
                                 description="Generate children hairs (require at least three parent strands)", default=False, update=run_update)
    use_parent_strands: BoolProperty(name="Include Parent Strands",
                                      description="Include parent strands when generating hair cards", default=False, update=run_update)
    embed: BoolProperty(name="Embed Roots", description="Embed hair roots inside source surface geometry", default=False, update=run_update)
    embedValue: FloatProperty(name="Embed Roots Depth", description="Embed curve ribbons roots depth", default=0, min=0, max=10, update=run_update)
    t_in_y: IntProperty(name="Strand Segments", default=5, min=2, max=20, update=run_update)
    smooth_curves: IntProperty(name="Strand Smoothing", default=0, min=0, max=6, update=run_update)
    hairType: bpy.props.EnumProperty(name="Hair Type", default="NURBS",
                                      items=(("NURBS", "Nurbs", ""),
                                             ("POLY", "Poly", "")), update=run_update)
    alignToSurface: BoolProperty(name="Tilt aligning", description="Enable interactive aligning curve ribbons to target surface",
                                  default=False, update=run_update)
    smoothTiltStrength: IntProperty(name="Tilt smoothing strength", description="Enable tilt smoothing \n Works only when \'Tilt Aligning\' is enabled",
                                     default=0, min=0, max=5, update=smooth_tilt_check)
    resetTilt: BoolProperty(name="Reset tilt", description="Reset curve ribbon tilt", default=False, update=reset_tilt_run)
    childCount: IntProperty(name="Child count", default=100, min=10, soft_max=3000, update=run_update)
    PlacementJittering: FloatProperty(name="Placement Jittering/Face", description="Placement Jittering/Face \n"
                                                                                    "Helps even out particle distribution \n"
                                                                                    "0 = automatic", default=0, min=0, max=100, subtype='PERCENTAGE', update=run_update)
    lenSeed: IntProperty(name="Length Seed", default=1, min=1, max=1000, update=run_update)
    RandomizeLengthPlus: FloatProperty(name="Increase length randomly", description="Increase length randomly",
                                        default=0, min=0, max=1, subtype='PERCENTAGE', update=run_update)
    RandomizeLengthMinus: FloatProperty(name="Decrease length randomly", description="Decrease length randomly",
                                         default=0, min=0, max=1, subtype='PERCENTAGE', update=run_update)

    strand_width: FloatProperty(name="Strand width", description="Strand width", default=0.5, min=0.0, soft_max=10, update=update_width)



class ModalHairSettings(bpy.types.PropertyGroup):
    def modalHairCheck(self, context):
        if context.mode == 'PARTICLE':
            particle_id = context.active_object.particle_systems.active_index
            while len(self.particle_system_modal_settings) < particle_id+1:
                self.particle_system_modal_settings.add()
            drawHair(context)
            bpy.ops.object.modal_hair_refresh('INVOKE_DEFAULT') #seemsSmoother
            global FORCE_UPDATE
            FORCE_UPDATE = True
        else:
            self['runModalHair'] = False

    runModalHair: BoolProperty(name="Interactive Curve Ribbons", description="Create and run interactive updates on curve ribbons hair", default=False, update=modalHairCheck)
    particle_system_modal_settings: bpy.props.CollectionProperty(type=ParticleModalSettings)

    drawStrands: BoolProperty(name="Draw Parent Strands", description="Draw orange overlay on top of parent strands", default=False)
    drawOffset: bpy.props.FloatProperty(name="Parent Strand Draw Offset", description="Parent Strand Draw Offset", min=0.0, max=1.0, default=0.5, subtype='FACTOR')
    draw_color: bpy.props.FloatVectorProperty(name="Color", description="Color", default=(0.8, 0.4, 0.0, 1), subtype='COLOR', size=4, max=1, min=0)


    
class  HT_PT_ModalParticleHair_Panel(bpy.types.Panel):
    bl_label = "Modal Hair Tool"
    bl_idname = "hair_tool_modal"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hair Tool'
    bl_context = "particlemode"


    def draw(self, context):
        modal_hair_settings = context.active_object.modal_hair
        particle_id = context.active_object.particle_systems.active_index
        layout = self.layout
        box = layout.box()
        if len(modal_hair_settings.particle_system_modal_settings) < particle_id +1:
            box.operator('particles.create_settings')
        else:
            particle_modal_settings = modal_hair_settings.particle_system_modal_settings[particle_id]
            box.label(text="Interactive curve ribbons hair:")
            box.prop(modal_hair_settings, 'runModalHair', icon = "PARTICLEMODE")

            col = box.column(align=True)
            col.prop(particle_modal_settings, 'hairType')
            col.prop(particle_modal_settings, 't_in_y')
            col.prop(particle_modal_settings, 'strand_width')
            row = box.row(align=True)
            row.prop(particle_modal_settings, 'embed', icon_only=True, icon="MOD_SCREW", emboss=False)
            row.prop(particle_modal_settings, 'embedValue',icon="MOD_SCREW")
            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(particle_modal_settings, 'alignToSurface', icon_only=False, icon="SNAP_NORMAL")
            row.prop(particle_modal_settings, 'resetTilt', icon_only=False, icon="BLANK1", emboss=True)
            row = col.row(align=True)
            row.prop(particle_modal_settings, 'smoothTiltStrength')
            box.prop(particle_modal_settings, 'smooth_curves', icon_only=False, icon="MOD_SMOOTH")
            row = box.row(align=True)
            row.prop(modal_hair_settings, 'drawStrands', icon_only=True, icon="PARTICLE_PATH", emboss=True)
            row.prop(modal_hair_settings, 'drawOffset')
            row.prop(modal_hair_settings, 'draw_color', text='')
            row = box.row(align=True)
            row.prop(particle_modal_settings, 'with_children')
            if particle_modal_settings.with_children:
                row.prop(particle_modal_settings, 'use_parent_strands')
                col = box.column(align=True)
                col.prop(particle_modal_settings, 'childCount')
                col.prop(particle_modal_settings, 'PlacementJittering')
                col.prop(particle_modal_settings, 'lenSeed')
                col.prop(particle_modal_settings, 'RandomizeLengthPlus')
                col.prop(particle_modal_settings, 'RandomizeLengthMinus')



last_operation=None

ignore_list = ignored_operators = [
        "bpy.ops.object.embed_roots",
        "bpy.ops.object.curves_smooth",
        "bpy.ops.object.generate_ribbons",
        "bpy.ops.object.transform_apply",
        "bpy.ops.object.curves_align_tilt",
        "bpy.ops.object.curves_smooth_tilt",
        "bpy.ops.object.modal_hair_refresh",
    ]
FORCE_UPDATE = False
IGNORED_OPERATORS_NAMES = [
    'OBJECT_OT_modal_hair_refresh',
    'WM_OT_radial_control',
    'PARTICLE_OT_select_all']


class HT_OT_ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "object.modal_hair_refresh"
    bl_label = "Modal Timer Operator"
    bl_options = {"REGISTER", "UNDO"}

    particleObj = None

    def create_hair(self,context):
        '''Do this on init() once'''

        particleObj = self.particleObj 
        partsysMod = particleObj.particle_systems.active  # use first
        # self.sourceSurface_BVHT = BVHTree.FromObject(particleObj, context.depsgraph) #only for chair with children - calculate in once on init
        hair_name = partsysMod.name
        if hair_name not in bpy.data.objects.keys():
            curveData = bpy.data.curves.new(partsysMod.name + '_curve', type='CURVE')
            curveObj = bpy.data.objects.new(hair_name, curveData)
            curveObj.matrix_world = particleObj.matrix_world
            context.scene.collection.objects.link(curveObj)
            # curveObj.select_set(True)
            # curveObj.data.show_normal_face = False
            curveObj.data.dimensions = '3D'
            curveObj.targetObjPointer = particleObj.name  # store source surface for snapping oper
            self.curveObj = curveObj
            self.hair_ribbon_update(context)
        else:
            curveObj = bpy.data.objects[hair_name]
        self.curveObj = curveObj

        if not curveObj.data.bevel_object:
            backup_active = context.view_layer.objects.active
            context.view_layer.objects.active = curveObj
            bpy.context.scene.update()
            bpy.ops.object.generate_ribbons(strandResU=3, strandResV=2,
                                        strandWidth=0.5, strandPeak=0.3,
                                        strandUplift=-0.2, alignToSurface=False)
            HT_OT_CurvesUVRefresh.uvCurveRefresh(curveObj)
            context.view_layer.objects.active = backup_active


    def particle_hair_to_points_with_children(self,context):
        partsysMod = self.particleObj.particle_systems.active  # use last
        particle_id = self.particleObj.particle_systems.active_index  # use last
        particle_modal_settings = context.active_object.modal_hair.particle_system_modal_settings[particle_id]  # cos using self.particleObj gives random settings...
        diagonal = self.diagonal
        particle_count = len(partsysMod.particles)
        if particle_count==0: #require more that three strands
            return self.particle_hair_to_points(context)
        pointsList_hair = []


        coords = []
        global PARTICLE_CO #cache strands for drawing
        strands_len = len(partsysMod.particles[0].hair_keys) - 1
        for strand in partsysMod.particles:  # for strand point
            pointsList_hair.append([hair_key.co for hair_key in strand.hair_keys])  # DONE: exclude duplicates if first strand[0] in list already
            if context.active_object.modal_hair.drawStrands:
                for i, point in enumerate(strand.hair_keys):  # create p1,p2,  p2,p3,  p3,p4
                    if i == 0 or i == strands_len:
                        coords.append((point.co[0], point.co[1], point.co[2]))
                    else:
                        coords.extend([(point.co[0], point.co[1], point.co[2]), (point.co[0], point.co[1], point.co[2])])
            else:
                coords = [(0, 0, 0)]
        PARTICLE_CO = coords

        if particle_count == 1: #create two fake strands so that barycentric works
            pointsList_hair.append([x.xyz+Vector((0.01*diagonal, 0, 0)) for x in pointsList_hair[0]])
            pointsList_hair.append([x.xyz+Vector((0 ,0.01*diagonal, 0)) for x in pointsList_hair[0]])
        elif particle_count == 2: #create one fake strands so that barycentric works
            pointsList_hair.append([x.xyz+Vector((0.01*diagonal, 0, 0)) for x in pointsList_hair[0]])

        #TODO: damm it is slow - 0.3 sec - on 3333 particle mesh (while doing sinterpol is just 0.02 sec)
        #FIXED: it was here cos particles woudl fail on duplicates.... Fixed by removing duplis in init
        # pointsList_uniq = []
        # [pointsList_uniq.append(x) for x in pointsList_hair if x not in pointsList_uniq]  # removing doubles (can cause zero size tris)
        pointsList_uniq = pointsList_hair
        
        # same_point_count cos barycentric transform requires it
        pointsList = interpol_Catmull_Rom(pointsList_uniq, particle_modal_settings.t_in_y, uniform_spacing=False, same_point_count=True)  # just gives smoother result on borders
        searchDistance = 100 *diagonal
        parentRoots = [strand[0] for strand in pointsList]  # first point of roots
        # create nnew Part Sytem with uniform points
        pointsChildRoots = HT_OT_RibbonsFromParticleHairChild.createUniformParticleSystem(
            context, particle_modal_settings.childCount, particle_modal_settings.PlacementJittering)  # return child part roots positions

        kd = kdtree.KDTree(len(parentRoots))
        for i, root in enumerate(parentRoots):
            kd.insert(root, i)
        kd.balance()
        sourceSurface_BVHT = self.sourceSurface_BVHT
        childStrandsPoints = []  # will contain strands with child points
        childStrandRootNormals = []
        seed(a=particle_modal_settings.lenSeed, version=2)
        for i, childRoot in enumerate(pointsChildRoots):  # for each child find it three parents and genereate strands by barycentric transform
            snappedPoint, normalChildRoot, rootHitIndex, distance = sourceSurface_BVHT.find_nearest(childRoot, searchDistance)
            childStrandRootNormals.append(normalChildRoot)
            threeClosestParentRoots = kd.find_n(childRoot, 3)  # find three closes parent roots
            rootTri_co, ParentRootIndices, distances = zip(*threeClosestParentRoots)  # split it into 3 arrays
            sourceTri_BVHT = BVHTree.FromPolygons(rootTri_co, [(0, 1, 2)], all_triangles=True)  # [0,1,2] - polygon == vert indices list
            childRootSnapped, normalChildProjected, index, distance = sourceTri_BVHT.find_nearest(childRoot, searchDistance)  # snap generated child to parent triangle ares \normals are sometimes flipped
            childRootSnapped2, normalChildProjected2, index2, distance2 = sourceSurface_BVHT.find_nearest(childRootSnapped, searchDistance)  # this gives ok normals always

            lenWeight = 1 + uniform(-particle_modal_settings.RandomizeLengthMinus, particle_modal_settings.RandomizeLengthPlus)
            rotQuat = normalChildProjected2.rotation_difference(normalChildRoot)
            translationMatrix = Matrix.Translation(childRoot)
            rotMatrixRot = rotQuat.to_matrix().to_4x4()
            mat_sca = Matrix.Scale(lenWeight, 4)
            transformMatrix = translationMatrix @ rotMatrixRot
            strandPoints = []
            # for childRootSnapped points transform them from parent root triangles to parent next segment triangle t1,t2,t3
            # and compensate child snapping to root triangle from before
            for j, (t1, t2, t3) in enumerate(zip(pointsList[ParentRootIndices[0]], pointsList[ParentRootIndices[1]], pointsList[ParentRootIndices[2]])):
                pointTransformed = barycentric_transform(childRootSnapped, rootTri_co[0], rootTri_co[1], rootTri_co[2], Vector(t1), Vector(t2), Vector(t3))
                childInterpolatedPoint = transformMatrix @ mat_sca @ (pointTransformed - childRootSnapped)  # rotate child strand to original pos (from before snapt)
                strandPoints.append(childInterpolatedPoint)
            childStrandsPoints.append(strandPoints)
        if particle_modal_settings.use_parent_strands:
            childStrandsPoints.extend(pointsList)
        return childStrandsPoints


    def particle_hair_to_points(self,context):
        partsysMod = self.particleObj.particle_systems.active  # use last
        particle_id = self.particleObj.particle_systems.active_index  # use last
        particle_modal_settings = context.active_object.modal_hair.particle_system_modal_settings[particle_id]
        extendList = []

        coords = []
        global PARTICLE_CO
        strands_len = len(partsysMod.particles[0].hair_keys) - 1
        for strand in partsysMod.particles:  # for strand point
            extendList.append([hair_key.co for hair_key in strand.hair_keys]) #not much gain from np: 2 x 0.001sec  only
            if context.active_object.modal_hair.drawStrands:
                for i, point in enumerate(strand.hair_keys):  # create p1,p2,  p2,p3,  p3,p4
                    if i == 0 or i == strands_len:
                        coords.append((point.co[0], point.co[1], point.co[2]))
                    else:
                        coords.extend([(point.co[0], point.co[1], point.co[2]), (point.co[0], point.co[1], point.co[2])])
            else:
                coords = [(0, 0, 0)]
        PARTICLE_CO = coords
        
        splinesPointsList = []
        if len(extendList) > 0:
            splinesPointsList.extend(interpol_Catmull_Rom(extendList, particle_modal_settings.t_in_y, uniform_spacing=False, same_point_count=True))
        return splinesPointsList


    def hair_ribbon_update(self, context):
        particle_id = self.particleObj.particle_systems.active_index  # use last
        particle_modal_settings = context.active_object.modal_hair.particle_system_modal_settings[particle_id]
        curveData = self.curveObj.data
        splinesPointsList = self.particle_hair_to_points_with_children(context) if particle_modal_settings.with_children else self.particle_hair_to_points(context)
        if len(splinesPointsList) == 0:
            return
            
        splinePointsNpOnes = np.ones((len(splinesPointsList), particle_modal_settings.t_in_y, 4), dtype=np.float32)  # 4 coord x,y,z ,1
        splinePointsNpOnes[:, :, :-1] = splinesPointsList  # fill x,y,z - exept last row (1)- for size
        #fix strands point count
        spline_count = len(curveData.splines)
        if spline_count>0:
            strand_len_diff = len(curveData.splines[0].points) - particle_modal_settings.t_in_y
            if strand_len_diff > 0:  # delete last point in loop
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                backup_active = context.view_layer.objects.active
                context.view_layer.objects.active = self.curveObj
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.curve.select_tips(roots=False)
                for i in range(strand_len_diff - 1):
                    bpy.ops.curve.select_more()
                bpy.ops.curve.delete(type='VERT')
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                # context.view_layer.objects.active = particleObj #wont work cos we use depsgraph evel obje here, 
                context.view_layer.objects.active = backup_active
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
                first_spline_radius = np.zeros(particle_modal_settings.t_in_y, dtype=np.float16)
                first_spline_tilt = np.zeros(particle_modal_settings.t_in_y, dtype=np.float16)
                curveData.splines[0].points.foreach_get('radius', first_spline_radius)
                curveData.splines[0].points.foreach_get('tilt', first_spline_tilt)
            for i in range(-spline_count_diff):
                polyline = curveData.splines.new(particle_modal_settings.hairType)
                polyline.points.add(particle_modal_settings.t_in_y - 1)
                if spline_count > 0: #set radii from example first spline
                    polyline.points.foreach_set('radius', first_spline_radius)
                    polyline.points.foreach_set('tilt', first_spline_tilt)
                if particle_modal_settings.hairType == 'NURBS':
                    polyline.order_u = 3
                    polyline.resolution_u = self.curveObj.data.resolution_u
                    polyline.use_endpoint_u = True
            HT_OT_CurvesUVRefresh.uvCurveRefresh(self.curveObj, self.curveObj.hair_settings.uv_seed)

        for polyline, splinePoints in zip(curveData.splines,splinePointsNpOnes):
            polyline.points.foreach_set("co", splinePoints.ravel())
        
        curveData.update_tag()
        backup_active  = context.view_layer.objects.active
        context.view_layer.objects.active = self.curveObj
        if particle_modal_settings.embedValue > 0:
            HT_OT_EmbedRoots.embed_strands_roots(context, self.curveObj, self.sourceSurface_BVHT_world,  embed=particle_modal_settings.embedValue, onlySelection=False)
            # bpy.ops.object.embed_roots(onlySelection=False,  )
        if particle_modal_settings.smooth_curves > 0:
            bpy.ops.object.curves_smooth(onlySelection=False,  smooth = particle_modal_settings.smooth_curves)
        if particle_modal_settings.alignToSurface is True:
            HT_OT_CurvesTiltAlign.align_curve_tilt(context, self.curveObj, self.sourceSurface_BVHT_world, resetTilt=True, onlySelection=False)
            # bpy.ops.object.curves_align_tilt(onlySelection=False, resetTilt = True)
            if particle_modal_settings.smoothTiltStrength > 0:
                HT_OT_CurvesTiltSmooth.run_smooth_titl(context, self.curveObj, strength=particle_modal_settings.smoothTiltStrength, onlySelection=False)
                # bpy.ops.object.curves_smooth_tilt(onlySelection=False, strength=modal_hair_settings.smoothTiltStrength)
        context.view_layer.objects.active = backup_active
    
        
    def finish(self,context):
        context.active_object.modal_hair.runModalHair = False
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    def modal(self, context, event):
        global IGNORED_OPERATORS_NAMES
        global FORCE_UPDATE
        if event.type in { 'ESC'}:
            self.finish(context)
            return {'CANCELLED'}

        elif event.type == 'TIMER':
            global last_operation
            if context.mode != 'PARTICLE':
                self.finish(context)
                return {'CANCELLED'}
            oper = context.active_operator
            if FORCE_UPDATE or (oper and oper != last_operation and oper.bl_idname not in IGNORED_OPERATORS_NAMES):
                if FORCE_UPDATE:
                    FORCE_UPDATE = False
                else:
                    # print(oper.bl_idname)
                    last_operation = oper
                partsysMod = self.particleObj.particle_systems.active  # use first
                if partsysMod.name not in bpy.data.objects.keys():
                    self.create_hair(context)
                self.curveObj = bpy.data.objects[partsysMod.name]
                # print('Updating hair!')
                self.hair_ribbon_update(context)
        elif event.ctrl and event.type == 'Z' and event.value == 'RELEASE':
            self.hair_ribbon_update(context)

        if not context.active_object.modal_hair.runModalHair:
            return {'FINISHED'}
        return {'PASS_THROUGH'}


    def invoke(self, context, event):
        depsgraph = bpy.context.depsgraph
        ob = bpy.context.active_object
        obj_eval = depsgraph.objects.get(ob.name, None)

        particleObj = self.particleObj = obj_eval
        global EVAL_PARTICLE_OBJ
        EVAL_PARTICLE_OBJ = obj_eval
        # particleObj = self.particleObj = context.active_object
        self.diagonal = diagonal = pow(particleObj.dimensions[0], 2) + pow(particleObj.dimensions[1], 2) + \
            pow(particleObj.dimensions[2], 2)  # diagonal -to normalize some values
        self.sourceSurface_BVHT = BVHTree.FromObject(particleObj, context.depsgraph)  # only for chair with children - calculate in once on init
        self.sourceSurface_BVHT_world = get_obj_mesh_bvht(particleObj, context.depsgraph, applyModifiers=True, world_space=True)

        partsysMod = self.particleObj.particle_systems.active  # use last
        diagonal = self.diagonal

        #find and add to ignore list particles with same root
        # pointsList_hair = []
        # ignore_list = []
        # for i,particle in enumerate(partsysMod.particles):  # for strand point
        #     if particle.hair_keys[0] not in pointsList_hair:
        #         pointsList_hair.append(particle.hair_keys[0])  # DONE: exclude duplicates if first strand[0] in list already
        #     else:
        #         ignore_list.append(i)
        # self.particle_duplicates_ids = ignore_list
        bpy.ops.particle.select_all(action='SELECT')
        bpy.ops.particle.remove_doubles()
        bpy.ops.particle.select_all(action='DESELECT')


        self.create_hair(context)
        self._timer = context.window_manager.event_timer_add(0.2, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}



class HT_OT_CreateModalSettings(bpy.types.Operator):
    bl_label = "Create Settings"
    bl_idname = "particles.create_settings"
    bl_description = "Create particle settings for interactive combing"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        modal_hair_settings = context.active_object.modal_hair
        particle_id = context.active_object.particle_systems.active_index
        part_settings_count = len(modal_hair_settings.particle_system_modal_settings)
        diff = part_settings_count - (particle_id+1)
        if diff<0: # idx is bigger that settings count, so add settings
            for i in range(-diff):
                modal_hair_settings.particle_system_modal_settings.add()
        elif diff>0:
            for i in range(diff):
                modal_hair_settings.particle_system_modal_settings.remove(len(modal_hair_settings.particle_system_modal_settings)-1)

        return {"FINISHED"}








