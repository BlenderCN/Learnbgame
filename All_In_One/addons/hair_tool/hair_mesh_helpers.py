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
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty
from .helper_functions import calc_power
# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb


class GenerateWeight(bpy.types.Operator):
    bl_label = "Add ribbon weights"
    bl_idname = "object.ribbon_weight"
    bl_description = "Add vertex weights to ribbons mesh"
    bl_options = {"REGISTER", "UNDO"}

    createNewVC = BoolProperty(name="Add new VColor", description="Adds new vertex color layer instead of overriding active one", default=False)
    gradientFalloff = FloatProperty(name="Gradient Falloff", description="Gradient Falloff", default=0,
                                    min=-1, max=1, subtype='PERCENTAGE')
    def execute(self, context):
        ribbonMesh = context.active_object
        if len(ribbonMesh.data.uv_layers)<2:
            self.report({'INFO'}, 'No second UV channel found!')
            return {"CANCELLED"}
        mesh = ribbonMesh.data
        if not ribbonMesh.vertex_groups or self.createNewVC:
            ribbonMesh.vertex_groups.new('gradient')
        if self.createNewVC:
            vg = ribbonMesh.vertex_groups[-1]
        else:
            vg = ribbonMesh.vertex_groups.active
        vertUV = {}
        cpow = calc_power(self.gradientFalloff)
        for face in mesh.polygons:
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                uv_coords = mesh.uv_layers['HairTool_UV'].data[loop_idx].uv
                vertUV[vert_idx]= (uv_coords.x, uv_coords.y)
        selected_verts = [v for v in mesh.vertices if v.select]
        verts = selected_verts if mesh.use_paint_mask_vertex else mesh.vertices
        for vert in verts:
            x,y = vertUV[vert.index]
            weight = abs(max(min(1-y, 1), 0))  # d over box height
            w2 = math.pow(weight, cpow)
            vg.add([vert.index],w2 , "REPLACE")
        if self.createNewVC:
            ribbonMesh.vertex_groups.active = ribbonMesh.vertex_groups[-1]
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        return {"FINISHED"}

class GenerateVerColorGradient(bpy.types.Operator):
    bl_label = "Add vertex colors gradient to ribbons"
    bl_idname = "object.ribbon_vert_color_grad"
    bl_description = "Add vertex color gradient to ribbons"
    bl_options = {"REGISTER", "UNDO"}

    createNewVC = BoolProperty(name="Add new VColor", description="Adds new vertex color layer instead of overriding active one", default=False)
    gradientFalloff = FloatProperty(name="Gradient Falloff", description="Gradient Falloff", default=0,
                                  min=-1, max=1, subtype='PERCENTAGE')

    def execute(self, context):
        ribbonMesh = context.active_object
        if len(ribbonMesh.data.uv_layers)<2:
            self.report({'INFO'}, 'No second UV channel found!')
            return {"CANCELLED"}
        mesh = ribbonMesh.data
        if not mesh.vertex_colors or self.createNewVC:
            mesh.vertex_colors.new("Gradient")

        # color_layer = mesh.vertex_colors["Col"]
        # or you could avoid using the color_layer name
        if self.createNewVC:
            color_layer = mesh.vertex_colors[-1]
        else:
            color_layer = mesh.vertex_colors.active
        cpow = calc_power(self.gradientFalloff)
        selected_faces = [f for f in mesh.polygons if f.select]
        faces = selected_faces if mesh.use_paint_mask_vertex else mesh.polygons
        for face in faces:
            for loop_idx in face.loop_indices:
                x,y = mesh.uv_layers['HairTool_UV'].data[loop_idx].uv
                col = abs(max(min(y, 1), 0))
                col2 = math.pow(col, cpow)
                if bpy.app.version > (2, 79, 0):
                    color_layer.data[loop_idx].color = [col2,col2,col2,1]
                else:
                    color_layer.data[loop_idx].color = [col2,col2,col2]
        if self.createNewVC:
            mesh.vertex_colors.active = mesh.vertex_colors[-1]
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        return {"FINISHED"}

class GenerateVerColorRandom(bpy.types.Operator):
    bl_label = "Add random vertex colors per ribbon"
    bl_idname = "object.ribbon_vert_color_random"
    bl_description = "Makes each ribbon vertex color unique"
    bl_options = {"REGISTER", "UNDO"}

    Seed = IntProperty(name="Noise Seed", default=1, min=1, max=1000)
    mergeSimilar = BoolProperty(name="Merge Similar", description="Merge Simila", default=False)
    createNewVC = BoolProperty(name="Add new VColor", description="Adds new vertex color layer instead of overriding active one", default=False)


    def execute(self, context):
        np.random.seed(self.Seed)
        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)  # Go to edit mode
        bpy.ops.mesh.select_all(action="DESELECT")  # unselect everything

        bm = bmesh.from_edit_mesh(obj.data)  # load mesh
        bm.faces.ensure_lookup_table()

        if self.createNewVC or not obj.data.vertex_colors:
            obj.data.vertex_colors.new("Random Color")

        if self.createNewVC:
            color_layer =bm.loops.layers.color[-1]
        else:
            color_layer =bm.loops.layers.color.active

        faceIslandsList = []
        faces = bm.faces

        while faces:
            faces[0].select_set(True)  # select 1st face
            bpy.ops.mesh.select_linked()  # select all linked faces makes a full loop
            faceIslandsList.append([f for f in faces if f.select])
            bpy.ops.mesh.hide(unselected=False)  # hide the detected loop
            faces = [f for f in bm.faces if not f.hide]  # update faces

        bpy.ops.mesh.reveal()  # unhide all faces
        islandColor = {} #dictt will contain faceCount : Color pairs
        for facesIsland in faceIslandsList: # face islands list
            if self.mergeSimilar:
                islandFaceCount = len(facesIsland)
                if islandFaceCount in islandColor.keys():
                    random_color = islandColor[islandFaceCount]
                else:
                    random_color = np.random.random_sample(3).tolist()
                    islandColor[islandFaceCount] = random_color  #asign faceCount : Color"
            else:
                random_color = np.random.random_sample(3).tolist()
            if bpy.app.version > (2, 79, 0):
                for face in facesIsland: #island faces
                    for loop in face.loops:
                            loop[color_layer] = random_color+[1]
            else:
                for face in facesIsland: #island faces
                    for loop in face.loops:
                            loop[color_layer] = random_color

        bm.free()  # free and prevent further access
        if self.createNewVC:
            obj.data.vertex_colors.active = obj.data.vertex_colors[-1]
        self.report({'INFO'}, 'Vertex colors have been generated')
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        return {"FINISHED"}

