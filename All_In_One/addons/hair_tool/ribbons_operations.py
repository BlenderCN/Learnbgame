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
from os import path
from .helper_functions import link_child_to_collection, unlink_from_scene, add_driver
from mathutils import Vector
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty


def uvMeshRibbonTransform(hairMesh, curveHairRibbon):
    # print('UV transform method')
    imgBackup = None
    for area in bpy.context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            if area.spaces.active.image:
                imgBackup = area.spaces.active.image
    uvBoxes = len(curveHairRibbon.hair_settings.hair_uv_points)
    last_hair_settings = bpy.context.scene.last_hair_settings
    if uvBoxes == 0:  # if no uv box, then initialize with empty or last used
        curveHairRibbon.hair_settings.hair_uv_points.clear()
        if len(last_hair_settings.hair_uv_points) == 0:  # set to defaults 00 11
            last_hair_settings.hair_uv_points.add()
            last_hair_settings.hair_uv_points[-1].start_point = [0, 1]
            last_hair_settings.hair_uv_points[-1].end_point = [1, 0]
        for uvPair in last_hair_settings.hair_uv_points:
            curveHairRibbon.hair_settings.hair_uv_points.add()
            curveHairRibbon.hair_settings.hair_uv_points[-1].start_point = uvPair.start_point
            curveHairRibbon.hair_settings.hair_uv_points[-1].end_point = uvPair.end_point
    # ipdb.set_trace()
    # old way (befor braids)
    meCurv = curveHairRibbon.to_mesh(bpy.context.depsgraph, False, calc_undeformed=False)
    meCurv.uv_layers.new(name='HairTool_UV')  # for vert veights and colors helper layer add secpnd uv's
    me = hairMesh.data  # will write bmesh from curves to this output mesh hair
    if len(me.uv_layers) == 0:
        me.uv_layers.new(name='UVMap')
    if 'HairTool_UV' not in me.uv_layers.keys():
        me.uv_layers.new(name='HairTool_UV')  # for vert veights and colors helper layer add secpnd uv's

    bm = bmesh.new()
    # bm.from_mesh(meCurv)
    bm.from_mesh(meCurv)
    bm.faces.ensure_lookup_table()
    bm.loops.layers.uv.verify()

    uv_layer = bm.loops.layers.uv[0]
    # bm.faces.layers.tex.verify()  # currently blender needs both layers.
    uvBoxes = len(curveHairRibbon.hair_settings.hair_uv_points)
    for f in bm.faces:
        BoxIndex2x = f.material_index
        uvRectIndex = divmod(BoxIndex2x, uvBoxes)[1]
        x1, y1 = curveHairRibbon.hair_settings.hair_uv_points[uvRectIndex].start_point
        x2, y2 = curveHairRibbon.hair_settings.hair_uv_points[uvRectIndex].end_point
        for l in f.loops:
            x, y = l[uv_layer].uv
            xOut = y * (x2 - x1) + x1  # rot -90, scale , translate
            yOut = -x * (y1 - y2) + y1
            if BoxIndex2x != uvRectIndex:  # DONE: flipping x
                xOut = -xOut + x1 + x2
            l[uv_layer].uv = xOut, yOut

    uv_layer2 = bm.loops.layers.uv['HairTool_UV']  # rotate second uv (help uvs)
    for f in bm.faces:
        for l in f.loops:
            x, y = l[uv_layer2].uv
            l[uv_layer2].uv = y, x  # rot -90
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bm.to_mesh(me)
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    bpy.ops.mesh.select_all(action='SELECT')
    me.update()
    if imgBackup:
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.spaces.active.image = imgBackup


class HT_OT_CurvesUVRefresh(bpy.types.Operator):
    bl_label = "Curve Ribbon UV Refresh"
    bl_idname = "object.curve_uv_refresh"
    bl_description = "Refresh material on curve ribbons to latest uv transformation"
    bl_options = {"REGISTER", "UNDO"}

    Seed: IntProperty(name="Noise Seed", default=1, min=1, max=1000)

    def execute(self, context):
        selectedCurve = context.active_object
        self.uvCurveRefresh(selectedCurve, self.Seed)
        return {"FINISHED"}

    @staticmethod
    def attachMaterial(obj, uvBoxes, RandomFlipX):
        uvBoxes = len(obj.hair_settings.hair_uv_points)

        '''Add count materals slots to obj'''
        matName = "CurveRibbon"
        last_hair_settings = bpy.context.scene.last_hair_settings
        lastMat = last_hair_settings.material  # cant use it cos MappingNode can't be instanced - so use copy instead
        if len(obj.material_slots) == 0 or obj.material_slots[0].material == None:
            hair_node_groups = ['Saturate', 'Lerp', 'HairShaderMain', 'HairParameters', 'AnisoSpec']
            if lastMat:
                firstMat = lastMat.copy()
            else:  # else create new and store last mat
                nodes_for_update = []
                for node_gr in bpy.data.node_groups:
                    for node in node_gr.nodes:
                        if node.type == 'GROUP' and node.node_tree.name in hair_node_groups:
                            nodes_for_update.append(node)
                filepath = path.dirname(__file__)+"\hair_lib.blend"
                if 'HairMatAniso' not in bpy.data.materials.keys():
                    with bpy.data.libraries.load(filepath) as (data_from, data_to):
                        data_to.materials = [mat_name for mat_name in data_from.materials if mat_name == 'HairMatAniso']
                        data_to.node_groups = [node_name for node_name in data_from.node_groups if node_name in hair_node_groups]
                        imported_gr_names = [node_name for node_name in data_from.node_groups if node_name in hair_node_groups] #stores names
                        data_to.images = data_from.images
                #replace old node groups
                #DONE: fix light drivers
                #DONE: remove old node groups?
                for node in nodes_for_update:
                    if node.node_tree.name in imported_gr_names:
                        node.node_tree = data_to.node_groups[imported_gr_names.index(node.node_tree.name)]
                for orig_node_name, imported_node_gr in zip(imported_gr_names, data_to.node_groups):
                    imported_node_gr.name = orig_node_name
                nodes_to_remove = [nod_gr for nod_gr in bpy.data.node_groups if nod_gr.users == 0]
                for nod_gr in nodes_to_remove:
                    bpy.data.node_groups.remove(nod_gr)
                firstMat = bpy.data.materials['HairMatAniso']

                if 'HairAnisoLight' not in bpy.data.objects.keys():
                    lamp_data = bpy.data.lights.new(name="HairAnisoLight", type='POINT')
                    lamp_object = bpy.data.objects.new(name="HairAnisoLight", object_data=lamp_data)
                    lamp_object.location.z = 2
                    bpy.context.scene.collection.objects.link(lamp_object)
                else:
                    lamp_object = bpy.data.objects['HairAnisoLight']

                light_aniso = bpy.data.objects['HairAnisoLight']
                mat_light_pos_node = bpy.data.node_groups['AnisoSpec'].nodes['Combine XYZ']  # setting node for direction vector from light_aniso to surface
                add_driver(mat_light_pos_node.inputs['X'], light_aniso, 'default_value', 'location.x')
                add_driver(mat_light_pos_node.inputs['Y'], light_aniso, 'default_value', 'location.y')
                add_driver(mat_light_pos_node.inputs['Z'], light_aniso, 'default_value', 'location.z')
                uvHairPoints = obj.hair_settings.hair_uv_points

                last_hair_settings.material = bpy.data.materials['HairMatAniso']
                # uvHairPoints.add() #override default one
                # last_hair_settings.hair_uv_points.add()
                last_hair_settings.hair_uv_points[-1].start_point = uvHairPoints[-1].start_point  = [0.325604, 0.933343]
                last_hair_settings.hair_uv_points[-1].end_point = uvHairPoints[-1].end_point = [0.468694, 0.062035]

            if len(obj.material_slots) == 0:  # make sure first slot is assigned
                obj.data.materials.append(firstMat)
            elif obj.material_slots[0].material == None:
                obj.material_slots[0].material = firstMat
        else:
            firstMat = obj.material_slots[0].material

        last_hair_settings.material = obj.material_slots[0].material
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
        imgNodes = [img for img in firstMat.node_tree.nodes if img.type == "TEX_IMAGE"]  # link maping node to img
        for img in imgNodes:
            links.new(mappingNode.outputs[0], img.inputs[0])
        while len(obj.material_slots) > 1:
            oldMat = obj.data.materials[-1]
            obj.data.materials.pop(update_data=True)
            if oldMat.users == 0:
                bpy.data.materials.remove(oldMat)

        count = uvBoxes * RandomFlipX
        for i in range(1, count):  # duplicate first mat to rest of slots
            obj.data.materials.append(firstMat.copy())  # else add new slot with material duplicate
            if i + 1 > uvBoxes:
                uvRectIndex = divmod(i, uvBoxes)[1]
                obj.data.materials[-1].name = obj.data.materials[uvRectIndex].name + '_Mirrored'

    @staticmethod
    def uvCurveRefresh(curveHairRibbon, uvSeed=1, force_uv_reset=False):
        print('UV transform method')
        if "ArrayPlaceholder" not in curveHairRibbon.modifiers.keys():
            array = curveHairRibbon.modifiers.new(type="ARRAY", name="ArrayPlaceholder")
            array.count = 1
        uvBoxes = len(curveHairRibbon.hair_settings.hair_uv_points)
        last_hair_settings = bpy.context.scene.last_hair_settings
        if uvBoxes == 0:  # if no uv box, then initialize with empty or last used
            curveHairRibbon.hair_settings.hair_uv_points.clear()
            if len(last_hair_settings.hair_uv_points) == 0:  # set to defaults 00 11
                last_hair_settings.hair_uv_points.add()
                last_hair_settings.hair_uv_points[-1].start_point = [0, 1]
                last_hair_settings.hair_uv_points[-1].end_point = [1, 0]
            for uvPair in last_hair_settings.hair_uv_points:
                curveHairRibbon.hair_settings.hair_uv_points.add()
                curveHairRibbon.hair_settings.hair_uv_points[-1].start_point = uvPair.start_point
                curveHairRibbon.hair_settings.hair_uv_points[-1].end_point = uvPair.end_point
            if force_uv_reset:
                curveHairRibbon.hair_settings.hair_uv_points.clear()
                curveHairRibbon.hair_settings.hair_uv_points.add()
                curveHairRibbon.hair_settings.hair_uv_points[-1].start_point = [0, 1]
                curveHairRibbon.hair_settings.hair_uv_points[-1].end_point = [1, 0]
        addon_prefs = bpy.context.preferences.addons['hair_tool'].preferences
        RandomFlipX = 2 if addon_prefs.flipUVRandom else 1
        HT_OT_CurvesUVRefresh.attachMaterial(curveHairRibbon, uvBoxes, RandomFlipX)  # twice the materials for flippig
        uvBoxes = len(curveHairRibbon.hair_settings.hair_uv_points)

        for i, mat in enumerate(curveHairRibbon.data.materials):
            if 'Mapping' not in mat.node_tree.nodes.keys():
                mappingNode = mat.node_tree.nodes.new('ShaderNodeMapping')
            else:
                mappingNode = mat.node_tree.nodes['Mapping']
            mappingNode.vector_type = 'POINT'
            uvRectIndex = divmod(i, uvBoxes)[1]

            x1, y1 = curveHairRibbon.hair_settings.hair_uv_points[uvRectIndex].start_point
            x2, y2 = curveHairRibbon.hair_settings.hair_uv_points[uvRectIndex].end_point

            if i+1 <= uvBoxes:
                mappingNode.translation = Vector((x1, y1, 0))
                mappingNode.rotation[2] = 1.5708  # 90deg
                mappingNode.scale = Vector((y2-y1, x1-x2, 1))
            else:  # use filipped x transform
                mappingNode.translation = Vector((x2, y1, 0))
                mappingNode.rotation[2] = 1.5708  # 90deg
                mappingNode.scale = Vector((y2 - y1,  x2 - x1, 1))

        curveHairRibbon.hair_settings.uv_seed = uvSeed
        np.random.seed(uvSeed)
        curveData = curveHairRibbon.data
        for i, spline in enumerate(curveData.splines):
            spline.material_index = divmod(i+np.random.randint(uvBoxes*RandomFlipX), uvBoxes*RandomFlipX)[1]  # get mat list next mat in loop


class HT_OT_GenerateRibbons(bpy.types.Operator):
    bl_label = "Add ribbons"
    bl_idname = "object.generate_ribbons"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add ribbon to curve profile"

    strandResU: IntProperty(name="Segments U", default=3, min=1, max=5, description="Additional subdivision perpendicular to strand length")
    strandResV: IntProperty(name="Segments V", default=2, min=1, max=5, description="Subdivisions along strand length")
    strandWidth: FloatProperty(name="Strand Width", default=0.5, min=0.0, soft_max=10)
    strandPeak: FloatProperty(name="Strand protrusion", default=0.4, min=0.0, soft_max=1,
                              description="Describes curvature of ribbon. 0 - gives flat ribbon")
    strandUplift: FloatProperty(name="Strand uplift", default=-0.2, min=-1, soft_max=1, description="Moves whole ribbon up or down")
    alignToSurface: BoolProperty(name="Align tilt", description="Align tilt to Surface", default=False)
    skipInitProps: BoolProperty(name="skip Init Props", description="skip Init Props", default=False, options={'HIDDEN'})

    diagonal = 0
    # @classmethod
    # def poll(cls, context):  #breaks undo
    #     return context.active_object.type == 'CURVE'  # bpy.context.scene.render.engine == "CYCLES"


    @staticmethod
    def remove_unused_bevel():
        all_bevel_objs = [obj for obj in bpy.data.objects if obj.name.startswith('bevelCurve')]
        used_bevel_objs = [obj.data.bevel_object for obj in bpy.data.objects if obj.type == 'CURVE' and obj.data.bevel_object]
        for obj in all_bevel_objs:
            if obj not in used_bevel_objs:
                bpy.data.objects.remove(obj, do_unlink=True)

    def invoke(self, context, event):
        self.remove_unused_bevel()
        if context.active_object.type != 'CURVE':
            self.report({'INFO'}, 'Select curve object first')
            return {"CANCELLED"}
        hairCurve = context.active_object
        self.diagonal = math.sqrt(pow(hairCurve.dimensions[0], 2) + pow(hairCurve.dimensions[1], 2) +
                                  pow(hairCurve.dimensions[2], 2))  # to normalize some values
        if self.diagonal < 0.0001:
            self.diagonal = 1
        if hairCurve.ribbon_settings:  # use init settings if  they are != defaults, else use stored values
            self.strandResU = hairCurve.ribbon_settings.strandResU
            self.strandResV = hairCurve.ribbon_settings.strandResV
            self.strandWidth = hairCurve.ribbon_settings.strandWidth
            self.strandPeak = hairCurve.ribbon_settings.strandPeak
            self.strandUplift = hairCurve.ribbon_settings.strandUplift
            
        return self.execute(context)

    def execute(self, context):
        hairCurve = context.active_object
        pointsCo = []
        if self.diagonal < 0.0001:
            self.diagonal = 1
        # print("diagonal is :" + str(diagonal))
        # unitsScale = 1 #context.scene.unit_settings.scale_length
        strandWidth = self.strandWidth / 10  # * self.diagonal
        for i in range(self.strandResV + 1):
            x = 2 * i / self.strandResV - 1  # normalise and map from -1 to 1
            # **self.strandWidth to mantain proportion while changing widht
            pointsCo.append((x * strandWidth, ((1 - x * x) * self.strandPeak + self.strandUplift) * strandWidth, 0))
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
        # hairCurve.data.show_normal_face = False
        if self.skipInitProps is False:
            hairCurve.ribbon_settings.strandResU = self.strandResU
            hairCurve.ribbon_settings.strandResV = self.strandResV
            hairCurve.ribbon_settings.strandWidth = self.strandWidth
            hairCurve.ribbon_settings.strandPeak = self.strandPeak
            hairCurve.ribbon_settings.strandUplift = self.strandUplift
        if self.alignToSurface:
            bpy.ops.object.curves_align_tilt(onlySelection=False)

        return {"FINISHED"}


class HT_OT_CurvesToRibbons(bpy.types.Operator):
    bl_label = "Curve ribbons to mesh ribbons"
    bl_idname = "object.curve_edit"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = 'Convert curve to mesh object'

    def invoke(self, context, event):
        curveHairRibbon = context.active_object
        if curveHairRibbon.type != "CURVE":
            self.report({'INFO'}, 'You need to select curve ribbon object first')
            return {"CANCELLED"}
        if curveHairRibbon.data.bevel_object is None and curveHairRibbon.data.bevel_depth == 0:
            self.report({'INFO'}, 'Curve does not have bevel profile. Cancelling!')
            return {"CANCELLED"}
        return self.execute(context)

    @staticmethod
    def copyMaterialFromCurveToMesh(CurveParent, MeshChild):
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
        meshMats = MeshChild.data.materials
        if len(CurveParent.data.materials) == 0:
            return
        
        def has_mat_users(mat): #cos  mat.users seems broken (not refereshed)
            for obj in bpy.data.objects:
                for slot in obj.material_slots:
                    if slot.material == mat:
                        return True
            return False

        while len(meshMats) > 1:  # remove redundant mats above 1
            oldMat = meshMats[-1]
            meshMats.pop()
            # if oldMat.users == 0:
            if not has_mat_users(oldMat):
                bpy.data.materials.remove(oldMat)
        for f in MeshChild.data.polygons:
            f.material_index = 0
        if meshMats:
            # if meshObj has already mat assigned, then skip tweaking it (but check if it is not same as curve mat)
            if meshMats[0] is not None and meshMats[0].name == CurveParent.data.materials[0].name:
                meshMats[0] = CurveParent.data.materials[0].copy()
            elif meshMats[0] is None:  # if empty slot, then assign mat to it
                meshMats[0] = CurveParent.data.materials[0].copy()
        elif len(meshMats) == 0:  # no slots - then add new
            meshMats.append(CurveParent.data.materials[0].copy())
        mat = meshMats[0]
        if 'Mapping' in mat.node_tree.nodes.keys():
            mappingNode = mat.node_tree.nodes['Mapping']
            mappingNode.vector_type = 'TEXTURE'
            mappingNode.translation = Vector((0, 0, 0))
            mappingNode.rotation = Vector((0, 0, 0))
            mappingNode.scale = Vector((1, 1, 1))

    def createMeshFromCurve(self, parentCurve):
        meshFromCurve = parentCurve.to_mesh(bpy.context.depsgraph, False, calc_undeformed=False)
        meshObjFromCurve = bpy.data.objects.new(parentCurve.name + "mesh", meshFromCurve)
        link_child_to_collection(parentCurve, meshObjFromCurve)
        meshObjFromCurve.select_set(True)
        bpy.context.view_layer.objects.active = meshObjFromCurve
        meshObjFromCurve.use_fake_user = False
        meshObjFromCurve.hair_settings.hair_mesh_parent = parentCurve.name
        parentCurve.hair_settings.hair_curve_child = meshObjFromCurve.name
        meshObjFromCurve.matrix_world = parentCurve.matrix_world
        unlink_from_scene(parentCurve)
        parentCurve.use_fake_user = True

        # this for braids -> if curv hair have curve deform modifier, then assign this mod  to generated mesh braids
        self.curve_deform_braid(parentCurve, meshObjFromCurve)
        uvMeshRibbonTransform(meshObjFromCurve, parentCurve)
        self.copyMaterialFromCurveToMesh(parentCurve, meshObjFromCurve)

    @staticmethod
    def curve_deform_braid(parentCurve, meshObjFromCurve):
        # this for braids -> if curv hair have curve deform modifier, then assign this mod  to generated mesh braids
        parent_curv_mod_curv_deform = [mod for mod in parentCurve.modifiers if mod.type == 'CURVE']
        if len(parent_curv_mod_curv_deform) > 0:
            mesh_mod_curv_deform = [mod for mod in meshObjFromCurve.modifiers if mod.type == 'CURVE']
            if len(mesh_mod_curv_deform) > 0:
                mesh_mod_curv_deform[0].object = parent_curv_mod_curv_deform[0].object
            else:
                mod = meshObjFromCurve.modifiers.new("CurveDeform", 'CURVE')
                mod.object = parent_curv_mod_curv_deform[0].object
                mod.deform_axis = 'NEG_Z'

    def execute(self, context):
        curveHairRibbon = context.active_object
        mode = curveHairRibbon.mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        if curveHairRibbon.hair_settings.hair_curve_child == '':  # no child mesh, then create new one
            self.createMeshFromCurve(curveHairRibbon)
        else:  # else switch to editing child hair mesh obj and transfer spline changes to mesh
            if curveHairRibbon.hair_settings.hair_curve_child in bpy.data.objects.keys():
                mesh_hair_child = bpy.data.objects[curveHairRibbon.hair_settings.hair_curve_child]
                if mesh_hair_child.name not in context.scene.objects.keys():  # link mesh obj to scene
                    link_child_to_collection(curveHairRibbon, mesh_hair_child)
                    mesh_hair_child.hide_viewport = False
                    mesh_hair_child.use_fake_user = False
                    context.view_layer.objects.active = mesh_hair_child
                    uvMeshRibbonTransform(mesh_hair_child, curveHairRibbon)
                    curveHairRibbon.use_fake_user = True
                    unlink_from_scene(curveHairRibbon)
                    mesh_hair_child.select_set(True)
                    bpy.context.view_layer.objects.active = mesh_hair_child
                    mesh_hair_child.matrix_world = curveHairRibbon.matrix_world
                    mesh_hair_child.hair_settings.hair_mesh_parent = curveHairRibbon.name  # set parent in just in case curve name was changed
                    bpy.context.scene.update()
                    self.curve_deform_braid(curveHairRibbon, mesh_hair_child)
                    self.copyMaterialFromCurveToMesh(curveHairRibbon, mesh_hair_child)
                else:  # was already in scene, probbably cos source was duplicated? create new one
                    self.createMeshFromCurve(curveHairRibbon)
            else:
                self.createMeshFromCurve(curveHairRibbon)
        bpy.ops.object.mode_set(mode=mode, toggle=False)
        return {"FINISHED"}


class HT_OT_RibbonsToCurve(bpy.types.Operator):
    bl_label = "Mesh ribbons to curve ribbons"
    bl_idname = "object.ribbon_edit"
    bl_description = "Revert hair mesh to curve object type"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selected_mesh_hair = context.active_object
        mode = selected_mesh_hair.mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        if selected_mesh_hair.type == "MESH":
            if selected_mesh_hair.hair_settings.hair_mesh_parent:  # switch to spline hair obj
                if selected_mesh_hair.hair_settings.hair_mesh_parent in bpy.data.objects.keys():
                    curve_hair = bpy.data.objects[selected_mesh_hair.hair_settings.hair_mesh_parent]
                    if curve_hair.name not in bpy.context.scene.objects.keys():
                        link_child_to_collection(selected_mesh_hair, curve_hair)
                    else:  # possibly already linked becaouse mesh ribbon was duplicated, then duplicate source curve too
                        curve_hair = curve_hair.copy()  # copies dupli_group property(empty), but group property is empty (users_group = None)
                        selected_mesh_hair.hair_settings.hair_mesh_parent = curve_hair.name
                        curve_hair.data = curve_hair.data.copy()
                        curve_hair.select_set(True)
                        link_child_to_collection(selected_mesh_hair, curve_hair)
                    curve_hair.matrix_world = selected_mesh_hair.matrix_world
                    curve_hair.use_fake_user = False
                    selected_mesh_hair.use_fake_user = True
                    unlink_from_scene(selected_mesh_hair)  # hide mesh object
                    bpy.context.view_layer.objects.active = curve_hair
                    curve_hair.hair_settings.hair_curve_child = selected_mesh_hair.name  # set child in just in case curve name was changed
        bpy.ops.object.mode_set(mode=mode, toggle=False)

        return {"FINISHED"}


class HT_OT_EditRibbonProfile(bpy.types.Operator):
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
                bpy.context.scene.collection.objects.link(bevelObj)
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = bevelObj
            bevelObj.select_set(True)
            bpy.context.scene.update()
            bpy.ops.view3d.view_selected()
            bpy.ops.object.editmode_toggle()
            self.report({'INFO'}, 'Editing curve Profile was successful')
        return {"FINISHED"}


class HT_OT_DuplicateRibbonProfile(bpy.types.Operator):
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


class HT_OT_CloseRibbonProfile(bpy.types.Operator):
    bl_label = "Close curve Profile"
    bl_idname = "object.ribbon_close_profile"
    bl_description = "Hide curve Profile object (unlink it from scene)"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):  # make selection only false, if obj mode
        obj = context.active_object
        return obj and obj.type == 'CURVE' and obj.data.bevel_object is None

    def execute(self, context):
        bevelObj = context.active_object
        if bevelObj.type != 'CURVE':
            self.report({'INFO'}, 'Object is not Curve!')
            return {"CANCELLED"}  # skip non bevel obj
        for obj in context.scene.objects:
            if obj.type == 'CURVE':
                if obj.data.bevel_object is not None:
                    bevelObj.use_fake_user = True
                    unlink_from_scene(bevelObj)
                    self.report({'INFO'}, 'Closing curve Profile '+bevelObj.name+' was successful')

        return {"FINISHED"}
