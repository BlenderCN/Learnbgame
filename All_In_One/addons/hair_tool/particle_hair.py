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
import bmesh
import math
from bpy_extras import view3d_utils
from math import sqrt, pow
from random import uniform, seed
import numpy as np
from .ribbons_operations import HT_OT_CurvesUVRefresh
from mathutils import noise, Vector, kdtree, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
from bpy.props import EnumProperty, FloatProperty, BoolProperty, IntProperty, StringProperty
from .resample2d import interpol_Catmull_Rom
from .helper_functions import calc_power
# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb
 #DONE: fix active particle
 #DONE: mask support
 #DONE: Fix matrix world
 #DONE: Addo noise..
 #NOPE: Support uniform and non even len interpol? Or just leave it to resample oper?

class HT_OT_RibbonsFromParticleHairChild(bpy.types.Operator):
    bl_label = "Ribbons from particle hair with children"
    bl_idname = "object.ribbons_from_ph_child"
    bl_description = "Generate Ribbons from particle hair with custom made child strands generator. \n" \
                     "It gives more uniform child distribution compared to build in child particles."
    bl_options = {"REGISTER", "UNDO", "PRESET", 'USE_EVAL_DATA'}

    # extend: BoolProperty(name="Append", description="Appends new curves to already existing Particle hair strands", default=True)
    # override_segments: BoolProperty(name="Resample strands", description="Force using strands segments parameter", default=False)
    t_in_y: IntProperty(name="Strand Segments", default=5, min=2, max=20)
    childCount: IntProperty(name="Child count", default=100, min=10, max=2000)
    hairType: bpy.props.EnumProperty(name="Hair Type", default="NURBS",
                                      items=(("BEZIER", "Bezier", ""),
                                             ("NURBS", "Nurbs", ""),
                                             ("POLY", "Poly", "")))
    Seed: IntProperty(name="Noise Seed", default=1, min=1, max=1000)
    PlacementJittering: FloatProperty(name="Placement Jittering/Face", description="Placement Jittering/Face \n"
                                                                                    "Helps even out particle distribution \n"
                                                                                    "0 = automatic", default=0, min=0, max=100, subtype='PERCENTAGE')

    embed: FloatProperty(name="Embed roots", description="Radius for bezier curve", default=0, min=0, max=10)
    # embedTips: FloatProperty(name="Embed tips", description="Radius for bezier curve", default=0, min=0, max=10)

    noiseFalloff: FloatProperty(name="Noise falloff", description="Noise influence over strand lenght", default=0, min=-1, max=1, subtype='PERCENTAGE')
    freq: FloatProperty(name="Noise freq", default=0.5, min=0.0, max=5.0)
    noiseAmplitude: FloatProperty(name="Noise Amplitude", default=0.5, min=0.0, max=10.0)

    lenSeed: IntProperty(name="Length Seed", default=1, min=1, max=1000)
    RandomizeLengthPlus: FloatProperty(name="Increase length randomly", description="Increase length randomly", default=0, min=0, max=1, subtype='PERCENTAGE')
    RandomizeLengthMinus: FloatProperty(name="Decrease length randomly", description="Decrease length randomly", default=0, min=0, max=1, subtype='PERCENTAGE')

    generateRibbons: BoolProperty(name="Generate Ribbons", description="Generate Ribbons on curve", default=True)
    strandResU: IntProperty(name="Segments U", default=3, min=1, max=5, description="Additional subdivision along strand length")
    strandResV: IntProperty(name="Segments V", default=2, min=1, max=5, description="Subdivisions perpendicular to strand length ")
    strandWidth: FloatProperty(name="Strand Width", default=0.5, min=0.0, max=10)
    strandPeak: FloatProperty(name="Strand peak", default=0.4, min=0.0, max=1,
                               description="Describes how much middle point of ribbon will be elevated")
    strandUplift: FloatProperty(name="Strand uplift", default=0.0, min=-1, max=1, description="Moves whole ribbon up or down")
    alignToSurface: BoolProperty(name="Align tilt", description="Align tilt to Surface", default=False)

    RadiusFalloff: FloatProperty(name="Radius falloff", description="Radius falloff over strand lenght", default=0,  min=-1, max=1, subtype='PERCENTAGE')
    TipRadius: FloatProperty(name="Tip Radius", description="Tip Radius", default=0, min=0,  max=1, subtype='PERCENTAGE')

    Clumping: FloatProperty(name="Clumping", description="Clumping", default=0, min=0,  max=1, subtype='PERCENTAGE')
    ClumpingFalloff: FloatProperty(name="Clumping Falloff", description="Clumping Falloff", default=0,  min=-1, max=1, subtype='PERCENTAGE')
    Radius: FloatProperty(name="Radius", description="Radius for bezier curve", default=1, min=0, max=100)




    def check(self, context):  # DONE: can prop panel be fixed/refreshed when using f6 prop popup
        return True

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Curves from Particle Hair Settings:")
        box.prop(self, 'embed')
        # box.prop(self, 'embedTips')
        box.prop(self, 'hairType')
        box.prop(self, 't_in_y')
        box.prop(self, 'childCount')
        box.prop(self, 'PlacementJittering')

        box.label(text="Noise:")
        col = box.column(align=True)
        col.prop(self, 'Seed')
        col.prop(self, 'noiseFalloff')
        col.prop(self, 'noiseAmplitude')
        col.prop(self, 'freq')
        col = box.column(align=True)
        col.prop(self, 'lenSeed')
        col.prop(self, 'RandomizeLengthPlus')
        col.prop(self, 'RandomizeLengthMinus')

        box.prop(self, 'generateRibbons')
        if self.generateRibbons:
            col = box.column(align=True)
            col.prop(self, 'strandResU')
            col.prop(self, 'strandResV')
            col.prop(self, 'strandWidth')
            col.prop(self, 'strandPeak')
            col.prop(self, 'strandUplift')
            col.prop(self, 'alignToSurface')
        else:
            col.prop(self, 'Radius')
            col.prop(self, 'RadiusFalloff')
            col.prop(self, 'TipRadius')
            col.prop(self, 'Clumping')
            col.prop(self, 'ClumpingFalloff')


    @staticmethod
    def createUniformParticleSystem(context, childCount, PlacementJittering, Seed=1):
        particleObj = context.active_object
        index = particleObj.particle_systems.active_index
        partsysMod = particleObj.particle_systems[index]
        tempParticleMod = particleObj.modifiers.new("HairTemp", 'PARTICLE_SYSTEM')
        partsysUniform = tempParticleMod.particle_system.settings
        partsysUniform.name = 'HairFromCurves'
        partsysUniform.count = childCount
        partsysUniform.use_emit_random = False
        partsysUniform.use_even_distribution = True
        partsysUniform.emit_from = 'FACE'
        partsysUniform.physics_type = 'NO'
        partsysUniform.frame_start = 0
        partsysUniform.frame_end = 0
        partsysUniform.lifetime = 500
        partsysUniform.distribution = "JIT"
        partsysUniform.jitter_factor = 1
        partsysUniform.userjit = PlacementJittering*2
        tempParticleMod.particle_system.seed = Seed
        tempParticleMod.particle_system.vertex_group_density = partsysMod.vertex_group_density

        partsysUniform.use_modifier_stack = True

        bpy.context.scene.update()

        depsgraph = bpy.context.depsgraph
        particleObj_eval = depsgraph.objects.get(particleObj.name, None)
        tempParticleMod_eval = particleObj_eval.modifiers["HairTemp"]


        particleObjMatWorldInv = particleObj.matrix_world.inverted()
        childParticles = [particleObjMatWorldInv @ particle.location for particle in tempParticleMod_eval.particle_system.particles]
        particleObj.modifiers.remove(tempParticleMod)
        particleObj.particle_systems.active_index = index
        return childParticles


    def execute(self, context):
        depsgraph = bpy.context.depsgraph
        ob = bpy.context.active_object
        obj_eval = depsgraph.objects.get(ob.name, None)

        # particleObj = context.active_object
        particleObj = obj_eval
        if bpy.context.active_object.particle_systems is None:  # create new one
            self.report({'INFO'}, 'No active Particle Hair System found!')
            return {"CANCELLED"}
        index = particleObj.particle_systems.active_index
        psys_active = particleObj.particle_systems[index]
        if psys_active.settings.type != 'HAIR':  # create new one
            self.report({'INFO'}, 'Active Particle System is not Hair type! Cancelling')
            return {"CANCELLED"}
        pointsList_hair = []
        context.scene.update()
        if len(psys_active.particles) == 0:  # require more that three strands
            self.report({'INFO'}, 'Active Particle System has zero strands! Cancelling')
            return {"CANCELLED"}
        diagonal = sqrt(pow(particleObj.dimensions[0], 2) + pow(particleObj.dimensions[1], 2) + pow(particleObj.dimensions[2], 2))  # to normalize some values
        for particle in psys_active.particles:  # for strand point
            pointsList_hair.append([hair_key.co for hair_key in particle.hair_keys])  # DONE: exclude duplicates if first strand[0] in list already
        if len(psys_active.particles) == 1: #create two fake strands so that barycentric works
            pointsList_hair.append([x.xyz+Vector((0.01*diagonal, 0, 0)) for x in pointsList_hair[0]])
            pointsList_hair.append([x.xyz+Vector((0 ,0.01*diagonal, 0)) for x in pointsList_hair[0]])
        elif len(psys_active.particles) == 2: #create one fake strands so that barycentric works
            pointsList_hair.append([x.xyz+Vector((0.01*diagonal, 0, 0)) for x in pointsList_hair[0]])
        pointsList_uniq = []
        [pointsList_uniq.append(x) for x in pointsList_hair if x not in pointsList_uniq]  #removing doubles (can cause zero size tris)

        #same_point_count cos barycentric transform requires it
        pointsList = interpol_Catmull_Rom(pointsList_uniq, self.t_in_y, uniform_spacing=True, same_point_count=True)  # just gives smoother result on borders

        searchDistance = 100 * diagonal
        parentRoots = [strand[0] for strand in pointsList]  # first point of roots
    #create nnew Part Sytem with uniform points
        pointsChildRoots = self.createUniformParticleSystem(context,self.childCount, self.PlacementJittering, self.Seed)  # return child part roots positions

        kd = kdtree.KDTree(len(parentRoots))
        for i, root in enumerate(parentRoots):
            kd.insert(root, i)
        kd.balance()
        sourceSurface_BVHT = BVHTree.FromObject(particleObj, context.depsgraph)
        childStrandsPoints = []  #will contain strands with child points
        childStrandRootNormals = []
        length_ver_group_index = -1
        vertex_group_length_name = psys_active.vertex_group_length
        if vertex_group_length_name:  # calc weight based on root point
            length_ver_group_index = particleObj.vertex_groups[vertex_group_length_name].index
        particleObjMesh = particleObj.to_mesh(context.depsgraph, apply_modifiers=True, calc_undeformed=False)
        seed(a=self.lenSeed, version=2)
        embed = self.embed * 0.04 * diagonal
        cpow = calc_power(self.noiseFalloff)
        cpowClump = calc_power(self.ClumpingFalloff)
        noiseFalloff = [pow(i / self.t_in_y, cpow) for i in range(self.t_in_y)]
        ClumpFalloff = [pow((i+1) / self.t_in_y, cpowClump) for i in range(self.t_in_y)]

        for i,childRoot in enumerate(pointsChildRoots):  #for each child find it three parents and genereate strands by barycentric transform
            snappedPoint, normalChildRoot, rootHitIndex, distance = sourceSurface_BVHT.find_nearest(childRoot, searchDistance)
            childStrandRootNormals.append(normalChildRoot)
            threeClosestParentRoots = kd.find_n(childRoot, 3) #find three closes parent roots
            rootTri_co, ParentRootIndices, distances = zip(*threeClosestParentRoots)  #split it into 3 arrays
            sourceTri_BVHT = BVHTree.FromPolygons(rootTri_co,[(0,1,2)],all_triangles=True)  # [0,1,2] - polygon == vert indices list
            childRootSnapped, normalChildProjected, index, distance = sourceTri_BVHT.find_nearest(childRoot, searchDistance) #snap generated child to parent triangle ares \normals are sometimes flipped
            childRootSnapped2, normalChildProjected2, index2, distance2 = sourceSurface_BVHT.find_nearest(childRootSnapped, searchDistance) #this gives ok normals always

            lenWeight = 1
            if length_ver_group_index != -1:  # if vg exist
                averageWeight = 0
                for vertIndex in particleObjMesh.polygons[rootHitIndex].vertices: #DONE: check if work on mesh with modifiers
                    for group in particleObjMesh.vertices[vertIndex].groups:
                        if group.group == length_ver_group_index:
                            averageWeight += group.weight
                            break
                lenWeight = averageWeight / len(particleObjMesh.polygons[rootHitIndex].vertices)
            ranLen=uniform(-self.RandomizeLengthMinus, self.RandomizeLengthPlus)
            lenWeight*=(1+ranLen)
            # diff = childRoot - childRootSnapped
            # mat_loc = Matrix.Translation(childRootSnapped)
            # matTriangleSpaceInv = mat_loc #* rotMatrix
            # matTriangleSpaceInv.invert()
            rotQuat = normalChildProjected2.rotation_difference(normalChildRoot)
            translationMatrix = Matrix.Translation(childRoot)
            rotMatrixRot = rotQuat.to_matrix().to_4x4()
            mat_sca = Matrix.Scale(lenWeight, 4)
            transformMatrix = translationMatrix @ rotMatrixRot
            strandPoints = []
            #for childRootSnapped points transform them from parent root triangles to parent next segment triangle t1,t2,t3
            # and compensate child snapping to root triangle from before
            for j,(t1,t2,t3) in enumerate(zip(pointsList[ParentRootIndices[0]],pointsList[ParentRootIndices[1]],pointsList[ParentRootIndices[2]])):
                pointTransformed = barycentric_transform(childRootSnapped,rootTri_co[0],rootTri_co[1],rootTri_co[2], Vector(t1), Vector(t2), Vector(t3))
                childInterpolatedPoint = transformMatrix@mat_sca@(pointTransformed-childRootSnapped) #rotate child strand to original pos (from before snapt)
                #do noise
                noise.seed_set(self.Seed + i)  # add seed per strand/ring ?
                noiseVectorPerStrand = noise.noise_vector(childInterpolatedPoint * self.freq / diagonal,
                                                          noise_basis ='PERLIN_ORIGINAL') * noiseFalloff[j] * self.noiseAmplitude * diagonal / 10
                # childInterpolatedPoint += noiseVectorPerStrand

                #do clumping
                diff = Vector(t1) - childInterpolatedPoint  # calculate distance to parent strand (first strand from trio)
                # point += noiseVectorPerStrand * noiseFalloff[j] * self.noiseAmplitude * diagonal / 10
                # childClumped = childInterpolatedPoint + ClumpFalloff[j] * self.Clumping * diff + noiseVectorPerStrand * (1-ClumpFalloff[j])
                childClumped = childInterpolatedPoint + ClumpFalloff[j] * self.Clumping * diff + noiseVectorPerStrand * (1-ClumpFalloff[j]* self.Clumping)
                # childClumped = childInterpolatedPoint + noiseVectorPerStrand

                strandPoints.append(childClumped)
            # embeding roots
            diff = strandPoints[0] - strandPoints[1]
            diff.normalize()
            normalWeight = abs(diff.dot(normalChildRoot))
            strandPoints[0] += (diff*normalWeight - normalChildRoot*(1-normalWeight)) * embed  # do childStrandRootNormal to move it more into mesh surface
            childStrandsPoints.append(strandPoints)

        bpy.data.meshes.remove(particleObjMesh)
        # create the Curve Datablock
        curveData = bpy.data.curves.new(particleObj.name+'_curve', type='CURVE')

        splinePointsNp = np.array(childStrandsPoints, dtype=np.float32)
        if self.hairType != 'BEZIER':
            splinePointsNpOnes = np.ones((len(childStrandsPoints), self.t_in_y, 4), dtype=np.float32)  # 4 coord x,y,z ,1
            splinePointsNpOnes[:, :, :-1] = splinePointsNp
            splinePointsNp = splinePointsNpOnes
        for strandPoints in splinePointsNp:  # for strand point
            curveLength = len(strandPoints)
            polyline = curveData.splines.new(self.hairType)
            if self.hairType == 'BEZIER':
                polyline.bezier_points.add(curveLength - 1)
            elif self.hairType == 'POLY' or self.hairType == 'NURBS':
                polyline.points.add(curveLength - 1)
            if self.hairType == 'NURBS':
                polyline.order_u = 3  # like bezier thing
                polyline.use_endpoint_u = True

            if self.hairType == 'BEZIER':
                # polyline.bezier_points.co = (x, y, z)
                polyline.bezier_points.foreach_set("co", strandPoints.ravel())
                polyline.bezier_points.foreach_set('handle_left_type','AUTO')
                polyline.bezier_points.foreach_set('handle_right_type','AUTO')
            else:
                polyline.points.foreach_set("co", strandPoints.ravel())
                # polyline.points[i].co = (x, y, z, 1)
        curveData.resolution_u = self.strandResU
        curveData.dimensions = '3D'
        # create Object
        curveOB = bpy.data.objects.new(particleObj.name+'_curve', curveData)
        curveOB.matrix_world = particleObj.matrix_world
        scn = context.scene
        scn.collection.objects.link(curveOB)
        curveOB.targetObjPointer = particleObj.name  # store source surface for snapping oper
        context.view_layer.objects.active = curveOB
        curveOB.select_set(True)
        # curveOB.data.show_normal_face = False
        if self.generateRibbons:
            bpy.ops.object.generate_ribbons(strandResU=self.strandResU, strandResV=self.strandResV,
                                            strandWidth=self.strandWidth, strandPeak=self.strandPeak,
                                            strandUplift=self.strandUplift, alignToSurface=self.alignToSurface)
            HT_OT_CurvesUVRefresh.uvCurveRefresh(curveOB)
            context.view_layer.objects.active = particleObj
        else:
            curveData.fill_mode = 'FULL'
            curveData.bevel_depth = 0.004 * diagonal
            curveData.bevel_resolution = 2
            bpy.ops.object.curve_taper(TipRadiusFalloff=self.RadiusFalloff, TipRadius=self.TipRadius, MainRadius=self.Radius)
        return {"FINISHED"}



class HT_OT_ParticleHairToCurves(bpy.types.Operator):
    bl_label = "Particle Hair to Curves"
    bl_idname = "object.hair_to_curves"
    bl_description = "Convert active Hair particle system to curves. "
    bl_options = {"REGISTER", "UNDO", 'USE_EVAL_DATA'} #fixes operator on redo


    # embed: FloatProperty(name="Embed roots", description="Embed roots", default=0, min=0, max=10)
    # embedTip: FloatProperty(name="Embed tips", description="Embed tips", default=0, min=0, max=10)
    hairType: bpy.props.EnumProperty(name="Hair Type", default="NURBS",
                                      items=(("BEZIER", "Bezier", ""),
                                             ("NURBS", "Nurbs", ""),
                                             ("POLY", "Poly", "")))
    particleHairRes: IntProperty(name="Hair Res", description="How many points output curve will build off", default=2,
                                  min=0, soft_max=6)
    strandResU: IntProperty(name="Segments U", default=3, min=1, max=5, description="Additional subdivision along strand length")
    strandResV: IntProperty(name="Segments V", default=2, min=1, max=5, description="Subdivisions perpendicular to strand length ")
    strandWidth: FloatProperty(name="Strand Width", default=0.5, min=0.0, soft_max=10)
    strandPeak: FloatProperty(name="Strand peak", default=0.4, min=0.0, max=1, description="Describes how much middle point of ribbon will be elevated")
    strandUplift: FloatProperty(name="Strand uplift", default=0.0, min=-1, max=1, description="Moves whole ribbon up or down")

    alignToSurface: BoolProperty(name="Align tilt", description="Align tilt to Surface", default=False)

    generateRibbons: BoolProperty(name="Generate Ribbons", description="Generate Ribbons on curve", default=False)
    Seed: IntProperty(name="UV Seed", default=1, min=1, soft_max=1000)

    def check(self, context):  # DONE: can prop panel be fixed/refreshed when using f6 prop popup
        return True

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Curve from Particle Hair Settings:")
        # box.prop(self, 'embed')
        # box.prop(self, 'embedTips')
        box.prop(self, 'particleHairRes')
        box.prop(self, 'hairType')
        box.prop(self, 'generateRibbons')
        col = box.column(align=True)

        if self.generateRibbons:
            col.prop(self, 'strandResU')
            col.prop(self, 'strandResV')
            col.prop(self, 'strandWidth')
            col.prop(self, 'strandPeak')
            col.prop(self, 'strandUplift')
            col.prop(self, 'Seed')
            col.prop(self, 'alignToSurface')


    def execute(self, context):
        depsgraph = bpy.context.depsgraph
        ob = bpy.context.active_object
        obj_eval = depsgraph.objects.get(ob.name, None)

        particleObj = obj_eval
        partsysMod = None
        for mod in particleObj.modifiers:
            if mod.type == 'PARTICLE_SYSTEM':  #  and mod.show_viewport use first visible
                if particleObj.particle_systems.active.name == mod.particle_system.name:
                    if mod.particle_system.settings.type == "HAIR":
                        partsysMod = mod  # use first
                        break
        if partsysMod is None:
            self.report({'INFO'}, 'No active Particle Hair System found')
            return {"CANCELLED"}
        # partsysMod.particle_system.settings.draw_step = self.particleHairRes
        partsysMod.particle_system.settings.display_step = self.particleHairRes
        context.scene.render.hair_subdiv = 1
        
        bpy.ops.object.modifier_convert(modifier=partsysMod.name)
        newObj = context.active_object
        me = newObj.data
        bm = bmesh.new()  # create an empty BMesh
        bm.from_mesh(me)
        diagonal = math.sqrt(pow(particleObj.dimensions[0], 2) + pow(particleObj.dimensions[1], 2) + pow(particleObj.dimensions[2],
                                                                                                         2))  # to normalize some values
        sourceSurface_BVHT = BVHTree.FromObject(particleObj, context.depsgraph)
        
        bm.to_mesh(me)
        bm.free()
        newObj.data.transform(particleObj.matrix_world.inverted())  # cos modifier_convert above, applays loc,rot, scale so revert it
        newObj.matrix_world = particleObj.matrix_world
        bpy.ops.object.convert(target='CURVE')
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.spline_type_set(type=self.hairType)

        if self.hairType == 'NURBS':
            for polyline in context.active_object.data.splines:
                polyline.order_u = 3  # like bezier thing
                polyline.use_endpoint_u = True
        bpy.ops.object.editmode_toggle()

        newObj.data.dimensions = '3D'
        newObj.data.fill_mode = 'FULL'
        newObj.data.bevel_resolution = 2
        newObj.data.resolution_u = self.strandResU
        if self.generateRibbons:
            # particleObj.targetObjPointer = newObj.name  # for child storing
            newObj.targetObjPointer = particleObj.name  # for snapping purpouse
            bpy.ops.object.generate_ribbons(strandResU=self.strandResU, strandResV=self.strandResV,
                                            strandWidth=self.strandWidth, strandPeak=self.strandPeak,
                                            strandUplift=self.strandUplift, alignToSurface=self.alignToSurface)
            HT_OT_CurvesUVRefresh.uvCurveRefresh(newObj)

        partsysMod.show_viewport = False

        return {"FINISHED"}


def getObjectMassCenter(context, obj):
    local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
    global_bbox_center = obj.matrix_world * local_bbox_center
    region = context.region
    rv3d = context.space_data.region_3d
    return view3d_utils.location_3d_to_region_2d(region, rv3d, global_bbox_center)  # 3d coords to 2d reg

def particleHairFromPoints(self, context, particleObj, pointsList, extend=False):
    ''' Particle system only works on equal len strands. No api for hair_keys with ++ point, or --'''
    partsysMod = None
    context.view_layer.objects.active = particleObj

    for mod in particleObj.modifiers:
        if mod.type == 'PARTICLE_SYSTEM':  # use first visible
            if particleObj.particle_systems.active.name == mod.particle_system.name:
                partsysMod = particleObj.particle_systems.active  # use last
                mod.show_viewport = True
                extendList = []
                if extend and mod.particle_system.settings.type == "HAIR":
                    for strand in partsysMod.particles:  # for strand point
                        extendList.append([hair_key.co for hair_key in strand.hair_keys])
                    # ipdb.set_trace()
                    if len(extendList) > 0:
                        pointsList.extend(interpol_Catmull_Rom(extendList, len(pointsList[0]), uniform_spacing=False, same_point_count=True))
                bpy.ops.particle.edited_clear()  # toogle editability
                break
    if partsysMod is None:  # create new one
        self.report({'INFO'}, 'No active Particle Hair System found! Adding new one')
        particleObj.modifiers.new("Hair_From_Curves", 'PARTICLE_SYSTEM')
        partsysMod = particleObj.particle_systems[-1]
        partsysMod.name = 'HairFromCurves'
    # Create new settings
    partsysMod.settings.type = 'HAIR'
    partsysMod.settings.emit_from = 'FACE'
    partsysMod.settings.use_strand_primitive = True

    hair_len = len(pointsList[0])-1
    partsysMod.settings.hair_step = hair_len  # == HAIR_KEY NUMB
    partsysMod.settings.count = len(pointsList)
    partsysMod.settings.display_step = max(math.floor(math.log(len(pointsList[0]), 2)), 2) + 1
    bpy.ops.particle.particle_edit_toggle()
    # bpy.context.scene.update()
    for i, points in enumerate(pointsList):  # for strand point
        partsysMod.particles[i].location = points[0]
        for j, point in enumerate(points):  # for strand point
            partsysMod.particles[i].hair_keys[j].co = Vector(point)
            
    bpy.ops.particle.select_all(action='SELECT')

    bpy.ops.particle.rekey(keys_number=len(pointsList[0])) #fixes jumping bug
    weights = [i / hair_len for i in range(hair_len ,-1, -1)]
    for particle in partsysMod.particles:
        particle.hair_keys.foreach_set('weight', weights)
    bpy.ops.particle.select_all(action='DESELECT')

     #sticks the attached curves to head surface
    bpy.ops.particle.disconnect_hair(all=True)
    bpy.ops.particle.connect_hair(all=True)

    bpy.ops.particle.particle_edit_toggle()
    

class HT_OT_ParticleHairFromCurves(bpy.types.Operator):
    bl_label = "Particle Hair from Curves"
    bl_idname = "object.hair_from_curves"
    bl_description = "Creates particle hair strands from Curves object. \n" \
                     "Two objects need to be selected: one mesh and one curve type"
    bl_options = {"REGISTER", "UNDO", 'USE_EVAL_DATA'}

    extend: BoolProperty(name="Append", description="Appends new curves to already existing Particle hair strands", default=True)

    def invoke(self, context, event):
        particleObj = context.active_object
        if particleObj.type != 'MESH':
            self.report({'INFO'}, 'Select mesh object first')
            return {"CANCELLED"}
        return self.execute(context)


    def execute(self, context):
        meshObj = [obj for obj in context.selected_objects if obj.type == 'MESH']
        curveObjs = [obj for obj in context.selected_objects if obj.type == 'CURVE']
        if len(meshObj) == 0 or len(curveObjs) == 0:
            self.report({'INFO'}, 'Select one mesh and one curve object')
            return {"CANCELLED"}
        particleObj = meshObj[0]
        for curveObj in curveObjs:
            #wtf undo won't work without this .... extend - if disablend, and then enabled breaks appending old hair (old hair co are all null)
            # bpy.context.scene.update()
            curveData = curveObj.data
            curveData.transform(particleObj.matrix_world.inverted()@curveObj.matrix_world) #to make it go into particle obj space
            pointsList = []
            for polyline in curveData.splines:  # for strand point
                if polyline.type == 'NURBS' or polyline.type == 'POLY':
                    pointsList.append([point.co.xyz for point in polyline.points])
                else:
                    pointsList.append([point.co.xyz for point in polyline.bezier_points])
            curveData.transform(curveObj.matrix_world.inverted() @ particleObj.matrix_world)
            first_strand_len = len(pointsList[0])
            if not all(len(strand) == first_strand_len for strand in pointsList):
                averLen = int((len(pointsList[0]) + len(pointsList[1])) / 2)  # assume at least two splines?
                pointsList = interpol_Catmull_Rom(pointsList, averLen, uniform_spacing=False)
            matchFound = False
            for i,particleSystem in enumerate(particleObj.particle_systems):
                if particleSystem.name == curveObj.name:
                    particleObj.particle_systems.active_index = i
                    matchFound = True
                    break
            if not matchFound: #No matched Particle Hair System found! Adding new one
                particleObj.modifiers.new(curveObj.name, 'PARTICLE_SYSTEM')
                partsysMod = particleObj.particle_systems[-1]
                partsysMod.name = curveObj.name
                particleObj.particle_systems.active = partsysMod
                # particleObj.particle_systems.update()
            particleHairFromPoints(self,context, particleObj, pointsList, extend = self.extend)
        #do some nonsense - edit - quit particle edit undo - to fix jumping particle hairs. Soo ugly
        # bpy.ops.ed.undo_push()        #     # bpy.context.scene.update()
        # #MAKES crash on operator redo
        # bpy.ops.ed.undo()
        # bpy.ops.ed.redo()
        return {"FINISHED"}



class HT_OT_ParticleHairFromGPencil(bpy.types.Operator):
    bl_label = "Particle hair from GPencile"
    bl_idname = "object.particle_from_gp"
    bl_description = "Convert Grease Pencil strokes to Particle hair, \n" \
                     "and attach them to selected mesh object"
    bl_options = {"REGISTER", "UNDO"}

    hairType: bpy.props.EnumProperty(name="Hair Type", default="NURBS",
                                      items=(("BEZIER", "Bezier", ""),
                                             ("NURBS", "Nurbs", ""),
                                             ("POLY", "Poly", "")))
    t_in_y: IntProperty(name="Strand Segments", default=4, min=3, max=20)
    offsetFalloff: FloatProperty(name="Offset Falloff", description="Noise influence over strand lenght", default=0,
                                 min=-1, max=1, subtype='PERCENTAGE')
    offsetAbove: FloatProperty(name="Offset Strands", description="Offset strands above surface", default=0.2,
                                min=0.01, max=5.0)
    useVertWeight: BoolProperty(name="Use Vertex Weight", description="Use Vertex Weight for modulating particle offset", default=False)
    extend: BoolProperty(name="Append", description="Appends new curves to already existing Particle hair strands", default=False)

    def invoke(self, context, event):
        particleObj = context.active_object
        if particleObj.type != 'MESH':
            self.report({'INFO'}, 'Select mesh object first')
            return {"CANCELLED"}

        return self.execute(context)

    def execute(self, context):
        particleObj = context.active_object
        matInvHairObj = particleObj.matrix_world.inverted()
        addon_prefs = bpy.context.preferences.addons['hair_tool'].preferences
        if context.scene.GPSource:  # true == use scene gp
            if bpy.context.scene.grease_pencil and bpy.context.scene.grease_pencil.layers.active:
                if len(bpy.context.scene.grease_pencil.layers.active.active_frame.strokes) > 0:
                    strokes = bpy.context.scene.grease_pencil.layers.active.active_frame.strokes
                    bpy.context.scene.grease_pencil.layers.active.hide = addon_prefs.hideGPStrokes
                else:
                    self.report({'INFO'}, 'Scene has no grease pencil strokes for conversion to curves!')
                    return {"CANCELLED"}
            else:
                self.report({'INFO'}, 'Scene has no active grease pencil strokes for conversion to curves!')
                return {"CANCELLED"}
        else:  # false  == use object gp
            if particleObj:
                if particleObj.grease_pencil and particleObj.grease_pencil.layers.active:
                    if len(particleObj.grease_pencil.layers.active.active_frame.strokes) > 0:
                        strokes = particleObj.grease_pencil.layers.active.active_frame.strokes
                        particleObj.grease_pencil.layers.active.hide = addon_prefs.hideGPStrokes
                    else:
                        self.report({'INFO'}, 'Object has no grease pencil strokes for conversion to curves!')
                        return {"CANCELLED"}
                else:
                    self.report({'INFO'}, 'Selected object has no active grease pencil strokes! Try enabling \'Use scene GP\' ')
                    return {"CANCELLED"}
            else:
                self.report({'INFO'}, 'No object was selected, so no active grease pencil strokes found! Try selecting object with GP')
                return {"CANCELLED"}

        bm = bmesh.new()  # create an empty BMesh
        bm.from_mesh(particleObj.data)
        sourceSurface_BVHT = BVHTree.FromBMesh(bm)
        bm.free()
        sourceSurface_BVHT_mod = BVHTree.FromObject(particleObj, context.depsgraph) # to get smoother result when using subdiv

        VGIndex = particleObj.vertex_groups.active_index
        # activeVertexGroup = context.active_object.vertex_groups[VGIndex]
        diagonal = math.sqrt(pow(particleObj.dimensions[0], 2) + pow(particleObj.dimensions[1], 2) + pow(particleObj.dimensions[2], 2))/4  # to normalize some values
        searchDistance = 100 * diagonal
        pointsList = []
        if VGIndex != -1:
            self.report({'INFO'}, 'Active object has no active vertex group found!')
        if len(strokes)==0:
            self.report({'INFO'}, 'No GP strokes found!')
        for stroke in strokes:
            pointsList.append([matInvHairObj@point.co for point in stroke.points])
        pointsInterpolated = interpol_Catmull_Rom(pointsList, self.t_in_y, uniform_spacing=True, same_point_count=True)

        cpow = calc_power(self.offsetFalloff)
        strandLen = len(pointsInterpolated[0])
        pointsList = [[] for x in range(len(pointsInterpolated))]

        for i,points in enumerate(pointsInterpolated):  # for strand point
            weight = 1
            if self.useVertWeight:  #calc weight based on root point
                snappedPoint, normalSourceSurf, index, distance = sourceSurface_BVHT.find_nearest(points[0], searchDistance) #search dist = 100
                if VGIndex != -1: #if vg exist
                    averageWeight = 0
                    for vertIndex in particleObj.data.polygons[index].vertices:
                        # ipdb.set_trace()
                        for group in particleObj.data.vertices[vertIndex].groups:
                            if group.group == VGIndex:
                                averageWeight += group.weight
                                break
                    weight = averageWeight / len(particleObj.data.polygons[index].vertices)
            for j, point in enumerate(points):
                if sourceSurface_BVHT:
                    snappedPoint, normalSourceSurf, index, distance = sourceSurface_BVHT_mod.find_nearest(Vector(point),searchDistance)
                    noiseFalloff = math.pow(j / strandLen, cpow)
                    offsetAbove = Vector(point) + self.offsetAbove * normalSourceSurf * noiseFalloff * weight * diagonal
                    pointsList[i].append(offsetAbove)
        particleHairFromPoints(self, context, particleObj, pointsList,extend=self.extend)

        return {"FINISHED"}
