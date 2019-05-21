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
import numpy as np
from mathutils import Vector
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty

# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb


def uvMeshRibbonTransform(hairMesh, curveHairRibbon):
    # print('UV transform method')
    imgBackup = None
    for area in bpy.context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            if area.spaces.active.image:
                imgBackup = area.spaces.active.image
    uvBoxes = len(curveHairRibbon.hair_settings.hair_uv_points)
    if uvBoxes==0: #if no uv box, then initialize with empty or last used
        curveHairRibbon.hair_settings.hair_uv_points.clear()
        if len(bpy.context.scene.last_hair_settings.hair_uv_points)==0: #set to defaults 00 11
            bpy.context.scene.last_hair_settings.hair_uv_points.add()
            bpy.context.scene.last_hair_settings.hair_uv_points[-1].start_point = [0,1]
            bpy.context.scene.last_hair_settings.hair_uv_points[-1].end_point = [1,0]
        for uvPair in  bpy.context.scene.last_hair_settings.hair_uv_points:
            curveHairRibbon.hair_settings.hair_uv_points.add()
            curveHairRibbon.hair_settings.hair_uv_points[-1].start_point = uvPair.start_point
            curveHairRibbon.hair_settings.hair_uv_points[-1].end_point = uvPair.end_point
    # ipdb.set_trace()
    #old way (befor braids)
    # meCurv = curveHairRibbon.to_mesh(bpy.context.scene, False, 'PREVIEW')
    # meCurv.uv_textures.new('HairTool_UV')  # for vert veights and colors helper layer add secpnd uv's
    me = hairMesh.data  # will write bmesh from curves to this output mesh hair
    me.uv_textures.new('HairTool_UV')  # for vert veights and colors helper layer add secpnd uv's

    bm = bmesh.new()
    # bm.from_mesh(meCurv)
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    bm.loops.layers.uv.verify()

    uv_layer = bm.loops.layers.uv.active
    # bm.faces.layers.tex.verify()  # currently blender needs both layers.
    uvBoxes = len(curveHairRibbon.hair_settings.hair_uv_points)
    for f in bm.faces:
        BoxIndex2x=f.material_index
        uvRectIndex = divmod(BoxIndex2x, uvBoxes)[1]
        x1, y1 = curveHairRibbon.hair_settings.hair_uv_points[uvRectIndex].start_point
        x2, y2 = curveHairRibbon.hair_settings.hair_uv_points[uvRectIndex].end_point
        for l in f.loops:
            x, y = l[uv_layer].uv
            xOut = y * (x2 - x1) + x1  # rot -90, scale , translate
            yOut = -x * (y1 - y2) + y1
            if BoxIndex2x!=uvRectIndex: #DONE: flipping x
                xOut = -xOut + x1 + x2
            l[uv_layer].uv = xOut, yOut

    uv_layer2 = bm.loops.layers.uv[1] #rotate second uv (help uvs)
    for f in bm.faces:
        for l in f.loops:
            x, y = l[uv_layer2].uv
            l[uv_layer2].uv = y, x # rot -90
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bm.to_mesh(me)
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    bpy.ops.mesh.select_all(action='SELECT')
    me.update()
    if imgBackup:
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.spaces.active.image = imgBackup


class CurvesUVRefresh(bpy.types.Operator):
    bl_label = "Curve Ribbon UV Refresh"
    bl_idname = "object.curve_uv_refresh"
    bl_description = "Refresh material on curve ribbons to latest uv transformation"
    bl_options = {"REGISTER", "UNDO"}

    Seed = IntProperty(name="Noise Seed", default=1, min=1, max=1000)

    def execute(self, context):
        selectedCurve = context.active_object
        self.uvCurveRefresh(selectedCurve,self.Seed)
        return {"FINISHED"}

    @staticmethod
    def attachMaterial(obj, uvBoxes , RandomFlipX):
        count = uvBoxes * RandomFlipX
        '''Add count materals slots to obj'''
        matName="CurveRibbon"
        if bpy.context.scene.render.engine == 'BLENDER_RENDER':
            bpy.context.scene.render.engine = 'CYCLES'

        lastMat =bpy.context.scene.last_hair_settings.material #cant use it cos MappingNode can't be instanced - so use copy instead
        if len(obj.material_slots)==0 or obj.material_slots[0].material==None:
            if lastMat:
                firstMat = lastMat.copy()
            else: #else create new and store last mat
                firstMat = bpy.data.materials.new(name=matName)
                firstMat.diffuse_color = (0.6, 0.6, 0.6)
                if bpy.context.scene.render.engine == 'CYCLES':
                    firstMat.use_nodes = True
            if len(obj.material_slots) == 0:  #make sure first slot is assigned
                obj.data.materials.append(firstMat)
            elif obj.material_slots[0].material==None:
                obj.material_slots[0].material =firstMat
        else:
            firstMat = obj.material_slots[0].material

        bpy.context.scene.last_hair_settings.material = obj.material_slots[0].material
        firstMat.use_nodes = True
        links = firstMat.node_tree.links

        if 'Mapping' not in firstMat.node_tree.nodes.keys():
            mappingNode = firstMat.node_tree.nodes.new('ShaderNodeMapping')
            mappingNode.location = -500, 200
        else:
            mappingNode = firstMat.node_tree.nodes['Mapping']

        if 'Texture Coordinate' not in firstMat.node_tree.nodes.keys():
            textCo = firstMat.node_tree.nodes.new('ShaderNodeTexCoord')
        else:
            textCo = firstMat.node_tree.nodes['Texture Coordinate']
        textCo.location = mappingNode.location[0]-200, mappingNode.location[1]
        links.new(textCo.outputs['UV'], mappingNode.inputs[0])
        imgNodes = [img for img in firstMat.node_tree.nodes if img.type =="TEX_IMAGE"]    #link maping node to img
        for img in imgNodes:
            links.new(mappingNode.outputs[0], img.inputs[0])
        while len(obj.material_slots)>1:
            oldMat=obj.data.materials[-1]
            obj.data.materials.pop()
            if oldMat.users == 0:
                bpy.data.materials.remove(oldMat)
        for i in range(1,count):  #duplicate first mat to rest of slots
            obj.data.materials.append(firstMat.copy()) #else add new slot with material duplicate
            if i + 1 > uvBoxes:
                uvRectIndex = divmod(i, uvBoxes)[1]
                obj.data.materials[-1].name = obj.data.materials[uvRectIndex].name + '_Mirrored'

    @staticmethod
    def uvCurveRefresh(curveHairRibbon, uvSeed=1, force_uv_reset = False):
        # print('UV transform method')
        if "ArrayPlaceholder" not in curveHairRibbon.modifiers.keys():
            array=bpy.context.object.modifiers.new(type="ARRAY", name="ArrayPlaceholder")
            array.count=1
        uvBoxes = len(curveHairRibbon.hair_settings.hair_uv_points)
        if uvBoxes == 0: # if no uv box, then initialize with empty or last used
            curveHairRibbon.hair_settings.hair_uv_points.clear()
            if len(bpy.context.scene.last_hair_settings.hair_uv_points) == 0:  # set to defaults 00 11
                bpy.context.scene.last_hair_settings.hair_uv_points.add()
                bpy.context.scene.last_hair_settings.hair_uv_points[-1].start_point = [0, 1]
                bpy.context.scene.last_hair_settings.hair_uv_points[-1].end_point = [1, 0]
            for uvPair in bpy.context.scene.last_hair_settings.hair_uv_points:
                curveHairRibbon.hair_settings.hair_uv_points.add()
                curveHairRibbon.hair_settings.hair_uv_points[-1].start_point = uvPair.start_point
                curveHairRibbon.hair_settings.hair_uv_points[-1].end_point = uvPair.end_point
            if force_uv_reset:
                curveHairRibbon.hair_settings.hair_uv_points.clear()
                curveHairRibbon.hair_settings.hair_uv_points.add()
                curveHairRibbon.hair_settings.hair_uv_points[-1].start_point = [0, 1]
                curveHairRibbon.hair_settings.hair_uv_points[-1].end_point =  [1, 0]
        addon_prefs = bpy.context.user_preferences.addons['hair_tool'].preferences
        RandomFlipX = 2 if addon_prefs.flipUVRandom else 1
        uvBoxes = len(curveHairRibbon.hair_settings.hair_uv_points)
        CurvesUVRefresh.attachMaterial(curveHairRibbon, uvBoxes , RandomFlipX) #twice the materials for flippig

        for i,mat in enumerate(curveHairRibbon.data.materials):
            if 'Mapping' not in mat.node_tree.nodes.keys():
                mappingNode = mat.node_tree.nodes.new('ShaderNodeMapping')
            else:
                mappingNode=mat.node_tree.nodes['Mapping']
            mappingNode.vector_type = 'POINT'
            uvRectIndex = divmod(i , uvBoxes)[1]

            x1, y1 = curveHairRibbon.hair_settings.hair_uv_points[uvRectIndex].start_point
            x2, y2 = curveHairRibbon.hair_settings.hair_uv_points[uvRectIndex].end_point

            if i+1 <= uvBoxes:
                mappingNode.translation = Vector((x1,y1,0))
                mappingNode.rotation[2]= 1.5708  #90deg
                mappingNode.scale = Vector((y2-y1,x1-x2,1))
            else: #use filipped x transform
                mappingNode.translation = Vector((x2, y1, 0))
                mappingNode.rotation[2] = 1.5708  # 90deg
                mappingNode.scale = Vector((y2 - y1,  x2 - x1, 1))

        curveHairRibbon.hair_settings.uv_seed = uvSeed
        np.random.seed(uvSeed)
        curveData = curveHairRibbon.data
        for i,spline in enumerate(curveData.splines):
            spline.material_index = divmod(i+np.random.randint(uvBoxes*RandomFlipX) , uvBoxes*RandomFlipX)[1] #get mat list next mat in loop


class GenerateRibbons(bpy.types.Operator):
    bl_label = "Add ribbons"
    bl_idname = "object.generate_ribbons"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add ribbon to curve profile"

    strandResU = IntProperty(name="Segments U", default=3, min=1, max=5, description="Additional subdivision perpendicular to strand length")
    strandResV = IntProperty(name="Segments V", default=2, min=1, max=5, description="Subdivisions along strand length")
    strandWidth = FloatProperty(name="Strand Width", default=0.5, min=0.0, max=20)
    strandPeak = FloatProperty(name="Strand protrusion", default=0.4, min=0.0, max=1,
                               description="Describes curvature of ribbon. 0 - gives flat ribbon")
    strandUplift = FloatProperty(name="Strand uplift", default=-0.2, min=-1, max=1, description="Moves whole ribbon up or down")
    alignToSurface = BoolProperty(name="Align tilt", description="Align tilt to Surface", default=False)
    skipInitProps = BoolProperty(name="skip Init Props", description="skip Init Props", default=False)

    diagonal  = 0
    # @classmethod
    # def poll(cls, context):  #breaks undo
    #     return context.active_object.type == 'CURVE'  # bpy.context.scene.render.engine == "CYCLES"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, 'strandResU')
        col.prop(self, 'strandResV')
        col.prop(self, 'strandWidth')
        col.prop(self, 'strandPeak')
        col.prop(self, 'strandUplift')
        col.prop(self, 'alignToSurface')

    @staticmethod
    def remove_unused_bevel():
        all_bevel_objs = [obj for obj in bpy.data.objects if obj.name.startswith('bevelCurve')]
        used_bevel_objs = [obj.data.bevel_object for obj in bpy.data.objects if obj.type == 'CURVE' and obj.data.bevel_object]
        for obj in all_bevel_objs:
            if obj not in used_bevel_objs:
                bpy.data.objects.remove(obj, do_unlink=True)

    def invoke(self,context, event):
        self.remove_unused_bevel()
        if context.active_object.type != 'CURVE':
            self.report({'INFO'}, 'Select curve object first')
            return {"CANCELLED"}
        hairCurve = context.active_object
        # unitsScale = 1 #context.scene.unit_settings.scale_length
        # self.diagonal = math.sqrt(pow(hairCurve.dimensions[0], 2) + pow(hairCurve.dimensions[1], 2) + pow(hairCurve.dimensions[2], 2))  # to normalize some values
        self.diagonal = math.sqrt(pow(hairCurve.dimensions[0], 2) + pow(hairCurve.dimensions[1], 2) + pow(hairCurve.dimensions[2], 2))  # to normalize some values
        if self.diagonal < 0.0001:
            self.diagonal = 1
        if hairCurve.ribbon_settings: #use init settings if  they are != defaults, else use stored values
            self.strandResU   = hairCurve.ribbon_settings.strandResU
            self.strandResV   =  hairCurve.ribbon_settings.strandResV
            self.strandWidth  = hairCurve.ribbon_settings.strandWidth
            self.strandPeak   =  hairCurve.ribbon_settings.strandPeak
            self.strandUplift =  hairCurve.ribbon_settings.strandUplift
        return  self.execute(context)


    def execute(self, context):
        hairCurve = context.active_object
        pointsCo = []
        if self.diagonal < 0.0001:
            self.diagonal = 1
        # print("diagonal is :" + str(diagonal))
        # unitsScale = 1 #context.scene.unit_settings.scale_length
        strandWidth = self.strandWidth / 10  * self.diagonal
        for i in range(self.strandResV + 1):
            x = 2 * i / self.strandResV - 1  # normalise and map from -1 to 1
            pointsCo.append((x * strandWidth , ((1 - x * x) * self.strandPeak + self.strandUplift) * strandWidth  , 0))  # **self.strandWidth to mantain proportion while changing widht
        # create the Curve Datablock
        if hairCurve.data.bevel_object:
            curveBevelObj = hairCurve.data.bevel_object
            curveBevelObj.data.splines.clear()
            BevelCurveData = curveBevelObj.data
        else:
            BevelCurveData = bpy.data.curves.new('hairBevelCurve', type='CURVE')  # new CurveData
            BevelCurveData.dimensions = '2D'
            curveBevelObj = bpy.data.objects.new('bevelCurve', BevelCurveData)  # new object
            hairCurve.data.bevel_object = curveBevelObj
        bevelSpline = BevelCurveData.splines.new('POLY')  # new spline
        bevelSpline.points.add(len(pointsCo) - 1)
        for i, coord in enumerate(pointsCo):
            x, y, z = coord
            bevelSpline.points[i].co = (x, y, z, 1)
        curveBevelObj.use_fake_user = True

        hairCurve.data.resolution_u = self.strandResU
        hairCurve.data.use_auto_texspace = True
        hairCurve.data.use_uv_as_generated = True
        hairCurve.data.show_normal_face = False
        if self.skipInitProps is False:
            hairCurve.ribbon_settings.strandResU = self.strandResU
            hairCurve.ribbon_settings.strandResV = self.strandResV
            hairCurve.ribbon_settings.strandWidth = self.strandWidth
            hairCurve.ribbon_settings.strandPeak = self.strandPeak
            hairCurve.ribbon_settings.strandUplift = self.strandUplift
        if self.alignToSurface:
            bpy.ops.object.curves_align_tilt(onlySelection=False)

        return {"FINISHED"}


class CurvesToRibbons(bpy.types.Operator):
    bl_label = "Curve ribbons to mesh ribbons"
    bl_idname = "object.curve_edit"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = 'Convert curve to mesh object'


    def invoke(self,context, event):
        curveHairRibbon = context.active_object
        if curveHairRibbon.type != "CURVE":
            self.report({'INFO'}, 'You need to select curve ribbon object first')
            return {"CANCELLED"}
        if curveHairRibbon.data.bevel_object is None and curveHairRibbon.data.bevel_depth ==0:
            self.report({'INFO'}, 'Curve does not have bevel profile. Cancelling!')
            return {"CANCELLED"}
        return  self.execute(context)

    @staticmethod
    def copyMaterialFromCurveToMesh(CurveParent, MeshChild):
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
        meshMats =  MeshChild.data.materials
        if len(CurveParent.data.materials)==0:
            return
        while len(meshMats) > 1: #remove redundant mats above 1
            oldMat = meshMats[-1]
            meshMats.pop()
            if oldMat.users==0:
                bpy.data.materials.remove(oldMat)
        for f in MeshChild.data.polygons:
            f.material_index = 0
        if meshMats:
            if meshMats[0] is not None and meshMats[0].name == CurveParent.data.materials[0].name: #if meshObj has already mat assigned, then skip tweaking it (but check if it is not same as curve mat)
                meshMats[0] = CurveParent.data.materials[0].copy()
            elif meshMats[0] is None: #if empty slot, then assign mat to it
                meshMats[0] = CurveParent.data.materials[0].copy()
        elif len(meshMats)==0: #no slots - then add new
            meshMats.append(CurveParent.data.materials[0].copy())
        mat = meshMats[0]
        if 'Mapping' in mat.node_tree.nodes.keys():
            mappingNode = mat.node_tree.nodes['Mapping']
            mappingNode.vector_type = 'TEXTURE'
            mappingNode.translation = Vector((0, 0, 0))
            mappingNode.rotation = Vector((0, 0, 0))
            mappingNode.scale = Vector((0, 0, 0))


    def createMeshFromCurve(self,parentCurve,context):
        # meshFromCurve = parentCurve.to_mesh(bpy.context.scene, apply_modifiers=True, settings='PREVIEW')
        # meshObjFromCurve = bpy.data.objects.new(parentCurve.name + "mesh", meshFromCurve)
        for obj in context.scene.objects:
            if obj!=context.active_object:
                obj.select = False
        bpy.ops.object.convert(target='MESH', keep_original=True)
        meshObjFromCurve = context.active_object
        # bpy.context.scene.objects.link(meshObjFromCurve)
        # meshObjFromCurve.select = True
        # bpy.context.scene.objects.active = meshObjFromCurve
        meshObjFromCurve.use_fake_user = False
        meshObjFromCurve.hair_settings.hair_mesh_parent = parentCurve.name
        parentCurve.hair_settings.hair_curve_child = meshObjFromCurve.name
        meshObjFromCurve.matrix_world = parentCurve.matrix_world
        bpy.context.scene.objects.unlink(parentCurve)
        parentCurve.use_fake_user = True
        uvMeshRibbonTransform(meshObjFromCurve, parentCurve)
        self.copyMaterialFromCurveToMesh(parentCurve,meshObjFromCurve)

    def execute(self, context):
        curveHairRibbon = context.active_object
        mode = curveHairRibbon.mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        if curveHairRibbon.hair_settings.hair_curve_child == '':  # no child mesh, then create new one
            self.createMeshFromCurve(curveHairRibbon,context)
        else:  # else switch to editing child hair mesh obj and transfer spline changes to mesh
            if curveHairRibbon.hair_settings.hair_curve_child in bpy.data.objects.keys():
                childStripMeshObj = bpy.data.objects[curveHairRibbon.hair_settings.hair_curve_child]
                if childStripMeshObj.name not in context.scene.objects.keys(): #link mesh obj to scene
                    context.scene.objects.link(childStripMeshObj)
                    childStripMeshObj.hide = False
                    childStripMeshObj.use_fake_user = False
                    context.scene.objects.active = childStripMeshObj
                    uvMeshRibbonTransform(childStripMeshObj, curveHairRibbon)
                    curveHairRibbon.use_fake_user = True
                    context.scene.objects.unlink(curveHairRibbon)
                    childStripMeshObj.select = True
                    bpy.context.scene.objects.active = childStripMeshObj
                    childStripMeshObj.matrix_world = curveHairRibbon.matrix_world
                    childStripMeshObj.hair_settings.hair_mesh_parent = curveHairRibbon.name  # set parent in just in case curve name was changed
                    bpy.context.scene.update()
                    self.copyMaterialFromCurveToMesh(curveHairRibbon, childStripMeshObj)
                else: #was already in scene, probbably cos source was duplicated? create new one
                    self.createMeshFromCurve(curveHairRibbon,context)
            else:
                self.createMeshFromCurve(curveHairRibbon,context)
        bpy.ops.object.mode_set(mode=mode, toggle=False)
        return {"FINISHED"}


class RibbonsToCurve(bpy.types.Operator):
    bl_label = "Mesh ribbons to curve ribbons"
    bl_idname = "object.ribbon_edit"
    bl_description = "Revert hair mesh to curve object type"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):
        stripMeshObj = context.active_object
        mode = stripMeshObj.mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        if stripMeshObj.type == "MESH":
            if stripMeshObj.hair_settings.hair_mesh_parent:  # switch to spline hair obj
                if stripMeshObj.hair_settings.hair_mesh_parent in bpy.data.objects.keys():
                    splineHair = bpy.data.objects[stripMeshObj.hair_settings.hair_mesh_parent]
                    if splineHair.name not in bpy.context.scene.objects.keys():
                        context.scene.objects.link(splineHair)
                    else:  #possibly already linked becaouse mesh ribbon was duplicated, then duplicate source curve too
                        splineHair = splineHair.copy()  # copies dupli_group property(empty), but group property is empty (users_group = None)
                        stripMeshObj.hair_settings.hair_mesh_parent = splineHair.name
                        splineHair.data = splineHair.data.copy()
                        splineHair.select = True
                        context.scene.objects.link(splineHair)
                    splineHair.matrix_world = stripMeshObj.matrix_world
                    splineHair.use_fake_user = False
                    stripMeshObj.use_fake_user = True
                    context.scene.objects.unlink(stripMeshObj)  # hide mesh object
                    bpy.context.scene.objects.active = splineHair
                    splineHair.hair_settings.hair_curve_child = stripMeshObj.name  # set child in just in case curve name was changed
        bpy.ops.object.mode_set(mode=mode, toggle=False)

        return {"FINISHED"}


class EditRibbonProfile(bpy.types.Operator):
    bl_label = "Edit curve Profile"
    bl_idname = "object.ribbon_edit_profile"
    bl_description = "Edit curve Profile (link it to scene and put into edit mode)"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):  # make selection only false, if obj mode
        obj = context.active_object
        return obj and obj.type == 'CURVE' and obj.data.bevel_object

    def execute(self, context):
        Curve = context.active_object
        if not Curve.type == 'CURVE':
            self.report({'INFO'}, 'Use operator on curve type object')
            return {"CANCELLED"}
        bevelObj = bpy.context.object.data.bevel_object
        if bevelObj:
            if bevelObj.name not in context.scene.objects.keys():
                bpy.context.scene.objects.link(bevelObj)
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = bevelObj
            bevelObj.select= True
            bpy.context.scene.update()
            bpy.ops.view3d.view_selected()
            bpy.ops.object.editmode_toggle()
            self.report({'INFO'}, 'Editing curve Profile was successful')
        return {"FINISHED"}


class DuplicateRibbonProfile(bpy.types.Operator):
    bl_label = "Duplicate curve Profile"
    bl_idname = "object.ribbon_duplicate_profile"
    bl_description = "Duplicate curve Profile"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):  # make selection only false, if obj mode
        obj = context.active_object
        return obj and obj.type == 'CURVE' and obj.data.bevel_object

    def execute(self, context):
        Curve = context.active_object
        if not Curve.type == 'CURVE':
            self.report({'INFO'}, 'Use operator on curve type object')
            return {"CANCELLED"}
        bevelObj = bpy.context.object.data.bevel_object
        if bevelObj:
            new_obj = bevelObj.copy()
            new_obj.data = bevelObj.data.copy()
            new_obj.use_fake_user = True
            bpy.context.object.data.bevel_object = new_obj
            self.report({'INFO'}, 'Duplicating curve Profile was successful')
        return {"FINISHED"}


class CloseRibbonProfile(bpy.types.Operator):
    bl_label = "Close curve Profile"
    bl_idname = "object.ribbon_close_profile"
    bl_description = "Hide curve Profile object (unlink it from scene)"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):  # make selection only false, if obj mode
        obj = context.active_object
        return obj and obj.type == 'CURVE' and obj.data.bevel_object is None

    def execute(self, context):
        bevelObj =context.active_object
        if  bevelObj.type != 'CURVE':
            self.report({'INFO'}, 'Object is not Curve!')
            return {"CANCELLED"}#skip non bevel obj
        for obj in context.scene.objects:
            if obj.type=='CURVE':
                if obj.data.bevel_object is not None:
                    bpy.context.scene.objects.unlink(bevelObj)
                    self.report({'INFO'}, 'Closing curve Profile '+bevelObj.name+' was successful')

        return {"FINISHED"}

