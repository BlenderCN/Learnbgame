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

# Module: blender_scene.py
# Description: read/write blender scene via Blender API.

# TODO restruct

import bpy
import mathutils
import os

from .util import Util
from .options import ImportOptions, ExportOptions

'''
================================================================================
BlenderObject

Description: maps mdc surface data mainly.
================================================================================
'''

class BlenderObject:

    def __init__(self, name):

        self.name = name
        self.verts = []              # numFrames * numVerts
        self.normals = []            # numFrames * numVerts
        self.faces = []
        self.uvMap = []              # numVerts
        self.materialNames = []


    def readUVMap(mesh, verts, normals, faces):

        bpy.ops.object.mode_set(mode='OBJECT')

        uvLayer = mesh.uv_layers.active

        if uvLayer == None:
            return None

        if len(mesh.uv_layers) > 1:
            print("MDCExport Info: multiple uv layers found, using active layer.")

        uvMap = []
        mappedVerts = []

        for i in range(0, len(mesh.vertices)):
            uvMap.append(None)
            mappedVerts.append(None)

        originalUvMapLen = len(uvMap)

        # for each polygon check uv mapping of the vertices
        # no vertex should map to two different positions in the uvMap
        # if so, duplicate the vertex and modify the related face
        # this is because mdc supports only 1 to 1 mapping of each vertex
        # to uvMap
        for polygon in mesh.polygons:

            faceNum = polygon.index

            for loopIndex in polygon.loop_indices:

                loop = mesh.loops[loopIndex]

                vertexIndex = loop.vertex_index
                uvCoordinates = uvLayer.data[loop.index].uv

                if uvMap[vertexIndex] == None:

                    uvMap[vertexIndex] = uvCoordinates

                    uvMapIndex = vertexIndex
                    mappedVerts[vertexIndex] = []
                    mappedVerts[vertexIndex].append(uvMapIndex)

                else:

                    uvMapIndex = -1
                    mappings = mappedVerts[vertexIndex]

                    for i in range (0, len(mappings)):

                        index = mappings[i]
                        thisUvCoordinates = uvMap[index]

                        if thisUvCoordinates == uvCoordinates:

                            uvMapIndex = index
                            break

                    # create a new vert
                    if uvMapIndex == -1:

                        uvMap.append(uvCoordinates)

                        uvMapIndex = len(uvMap) - 1

                        mappedVerts[vertexIndex].append(uvMapIndex)

                        for frameNum in range(0, len(verts)):

                            # copy original location and normal to new index
                            frameVert = verts[frameNum][vertexIndex]
                            frameNormal = normals[frameNum][vertexIndex]

                            verts[frameNum].append(frameVert)
                            normals[frameNum].append(frameNormal)

                    # modify faces
                    oldVertexNum = vertexIndex
                    newVertexNum = uvMapIndex
                    if oldVertexNum != newVertexNum:

                        face = faces[faceNum]

                        if face[0] == oldVertexNum:
                            newFace = (newVertexNum, face[1], face[2])
                            faces[faceNum] = newFace
                        elif face[1] == oldVertexNum:
                            newFace = (face[0], newVertexNum, face[2])
                            faces[faceNum] = newFace
                        else:
                            newFace = (face[0], face[1], newVertexNum)
                            faces[faceNum] = newFace

        newVertexCount = len(uvMap) - originalUvMapLen
        if newVertexCount > 0:
            print("MDCExport Info: new vertices added to output .mdc for object: '" \
                  + str(mesh.name) + \
                  "', count=" + str(newVertexCount))

        for i in range(0, len(uvMap)):

            # this is ugly, isn't there a better way than casting?
            # the converter screws up the uv map data otherwise cause it
            # cannot handle Vectors from mathutils, and this mathutils
            # dependency should imo stay removed in the converter, putting
            # it into the converter would only further down the line would make
            # this neccessary for mdc_file, cause mdc_file at some point touches
            # Vectors during write (this can crash blender, at least mess up uvs)
            uvTupelCast = None

            if uvMap[i] == None:
                uvTupelCast = (0, 0)
                print("MDCExport Warning: not all vertices uv mapped. Found " \
                      "vertex '" + str(i) + "', for mesh '" \
                      + str(mesh.name) + "'. Setting to (0, 0) in uvMap.")
            else:
                uvCoords = uvMap[i]
                uvTupelCast = (uvCoords[0], uvCoords[1])

            uvMap[i] = uvTupelCast

        return uvMap


    def read(object, normalObjects, numFrames):

        blenderObject = BlenderObject(object.name)

        # prepare meshes
        bpy.context.scene.objects.active = object
        bpy.ops.object.modifier_add(type='TRIANGULATE')

        meshes = []
        for i in range(0, numFrames):

            bpy.context.scene.frame_set(i)
            mesh = object.to_mesh(bpy.context.scene, True, 'PREVIEW')
            meshes.append(mesh)

        # verts, normals
        invalidNormals = set() # temp fix, probably Blender API update required
        for i in range(0, numFrames):

            bpy.context.scene.frame_set(i)

            frameVerts = []
            frameNormals = []

            mesh = meshes[i]

            for vert in mesh.vertices:

                globalVert = object.matrix_world * vert.co
                frameVerts.append(globalVert)

                globalNormal = object.matrix_world * vert.normal
                globalNormal.normalize()
                frameNormals.append(globalNormal)

            # make an extra run for the user modelled vertex normals
            for normalObject in normalObjects:

                if normalObject.parent.name != object.name:
                    continue

                matrix_basis = normalObject.matrix_basis

                x = matrix_basis[0][2]
                y = matrix_basis[1][2]
                z = matrix_basis[2][2]
                normal = mathutils.Vector((x, y, z))
                normal.normalize()

                vertexIndex = normalObject.parent_vertices[0]

                # the user could have done a 'Remove Doubles', which leads to
                # object.parent_vertices[0] still having the old index, but
                # is no longer valid. Blender does not seem to clear \
                # parent-child relationship, so add a temp fix which checks \
                # if the vertex parent is still in bound and print a warning
                if vertexIndex < 0 or vertexIndex >= len(mesh.vertices):
                    invalidNormals.add(normalObject)
                else:
                    frameNormals[vertexIndex] = normal

            blenderObject.verts.append(frameVerts)
            blenderObject.normals.append(frameNormals)

        if len(invalidNormals) > 0:
            print("MDCExport Warning: some vertex normal objects no longer "\
                   "point to a valid vertex parent. This can be because of a "\
                   "previous 'Remove Doubles'. Make sure to check your vertex "\
                   "normal objects after export. No guarantee that this export "\
                   "will be successful. Some normals might be incorrect. "\
                   "Printing normal object names:")
            for invalidNormal in invalidNormals:
                print(invalidNormal.name)


        # assign first frame mesh for rest of operation
        mesh = meshes[0]

        # faces
        for face in mesh.polygons:

            faceIndexes = []

            for index in face.vertices:

                faceIndexes.append(index)

            blenderObject.faces.append(faceIndexes)

        # uvMap
        blenderObject.uvMap = BlenderObject.readUVMap(mesh, \
                                                      blenderObject.verts, \
                                                      blenderObject.normals, \
                                                      blenderObject.faces)

        # materialNames
        for slot in object.material_slots:

            blenderObject.materialNames.append(slot.name)

        # clean up
        bpy.ops.object.modifier_remove(modifier=object.modifiers[-1].name)

        for i in range(0, numFrames):

            bpy.data.meshes.remove(meshes[i])

        return blenderObject


'''
================================================================================
BlenderTag

Description: maps mdc tag. Tags are modelled by the user via an empty of type
'arrow'.
================================================================================
'''

class BlenderTag:

    def __init__(self, name):

        self.name = name
        self.locRot = []  # numFrames


    def encodeLocRot(x, y, z, yaw, pitch, roll):

        location = mathutils.Matrix.Translation((x, y, z))

        euler = mathutils.Euler((yaw, pitch, roll), 'XYZ')
        rotation = euler.to_matrix()

        locRot = location * rotation.to_4x4()

        return locRot


    def decodeLocRot(locRot):

        xyz = locRot.to_translation()
        x = xyz[0]
        y = xyz[1]
        z = xyz[2]

        angles = locRot.to_euler()
        yaw = angles[2]
        pitch = angles[1]
        roll = angles[0]

        return x, y, z, yaw, pitch, roll

'''
================================================================================
BlenderScene

Description: maps converted mdc data in blender. Holds references to all data
needed to read and write a scene via the blender API.
================================================================================
'''

class BlenderScene:

    frameName = "(from Blender)"

    def __init__(self, name):

        self.name = name
        self.numFrames = 0
        self.frameNames = []   # numFrames
        self.frameOrigins = [] # numFrames
        self.tags = []         # numTags
        self.objects = []      # numSurfaces


    def read(exportOptions):

        # settings to restore after operation
        restoreFrame = bpy.context.scene.frame_current

        # name
        sceneName = bpy.context.scene.name
        blenderScene = BlenderScene(sceneName)

        # numFrames
        blenderScene.numFrames = bpy.context.scene.frame_end + 1 \
                                 - bpy.context.scene.frame_start \

        # frameNames, frameOrigins
        for i in range(0, blenderScene.numFrames):

            blenderScene.frameNames.append(BlenderScene.frameName)
            blenderScene.frameOrigins.append((0, 0, 0))

        # choose tags, objects and normalObjects for export
        tags = []
        objects = []
        normalObjects = []

        if exportOptions.selection == True:
            objectList = bpy.context.selected_objects
        else:
            objectList = bpy.context.scene.objects

        for object in objectList:

            if object.type == 'EMPTY' and object.empty_draw_type == 'ARROWS':
                tags.append(object)

            if object.type == 'MESH':
                objects.append(object)

            if exportOptions.normalObjects == True and \
                object.type == 'EMPTY' and \
                object.empty_draw_type == 'SINGLE_ARROW' and \
                object.parent_type == 'VERTEX':
                   normalObjects.append(object)

        # tags
        for tag in tags:

            blenderTag = BlenderTag(tag.name)

            for i in range(0, blenderScene.numFrames):

                bpy.context.scene.frame_set(i)
                locRot = tag.matrix_basis.copy()
                blenderTag.locRot.append(locRot)

            blenderScene.tags.append(blenderTag)

        # objects
        for object in objects:

            blenderObject = BlenderObject.read(object, normalObjects, \
                                               blenderScene.numFrames)
            blenderScene.objects.append(blenderObject)

        # restore settings
        bpy.context.scene.frame_set(restoreFrame)

        return blenderScene


    def write(self, importOptions):

        # settings to restore after operation
        restoreScene = bpy.context.scene.name

        if importOptions.toNewScene == True:
            bpy.ops.scene.new()

        # objects
        for i in range(0, len(self.objects)):

            name = self.objects[i].name

            mesh = bpy.data.meshes.new(name)
            object = bpy.data.objects.new(name, mesh)
            object.location = (0,0,0)
            object.show_name = True

            # link object to scene and make active
            scene = bpy.context.scene
            scene.objects.link(object)
            scene.objects.active = object
            object.select = True

            # verts, faces
            mesh.from_pydata(self.objects[i].verts[0], [], \
                             self.objects[i].faces)
            mesh.update()

            # shape keys for animation
            shapeKey = object.shape_key_add(name=self.frameNames[0], \
                                            from_mix=False)
            mesh.shape_keys.use_relative = False

            for j in range(1, self.numFrames):

                verts = self.objects[i].verts[j]
                shapeKey = object.shape_key_add(name=self.frameNames[j], \
                                                from_mix=False)
                for k in range(0, len(object.data.vertices)):

                    x = verts[k][0]
                    y = verts[k][1]
                    z = verts[k][2]
                    shapeKey.data[k].co = (x, y, z)

            bpy.context.scene.objects.active = object
            bpy.context.object.active_shape_key_index = 0
            bpy.ops.object.shape_key_retime()

            for j in range(0, self.numFrames):

                mesh.shape_keys.eval_time = 10.0 * (j + 1)
                mesh.shape_keys.keyframe_insert('eval_time', frame=j)

            mesh.update()

            # uvMap
            mesh.uv_textures.new('UVMap')

            for polygon in mesh.polygons:
                for j in range(polygon.loop_start, polygon.loop_start + polygon.loop_total):
                    vertexIndex = mesh.loops[j].vertex_index
                    mesh.uv_layers['UVMap'].data[j].uv = \
                        self.objects[i].uvMap[vertexIndex]

            # materialNames and textures
            for j in range(0, len(self.objects[i].materialNames)):
                materialName = self.objects[i].materialNames[j]
                material = bpy.data.materials.new(materialName)
                mesh.materials.append(material)

                # add texture if possible
                textureSuccess = False
                textureName = importOptions.gamePath + "\\" + materialName

                # first try
                if os.path.isfile(textureName):
                    textureSuccess = True

                # second try
                if textureSuccess == False:
                    textureName = Util.swapAddFileExtension(textureName)
                    if os.path.isfile(textureName):
                        textureSuccess = True

                # third try
                if textureSuccess == False:
                    textureName = Util.swapAddFileExtension(textureName)
                    if os.path.isfile(textureName):
                        textureSuccess = True

                if textureSuccess == True:

                    texture = bpy.data.textures.new('Texture', 'IMAGE')
                    texture_slot = material.texture_slots.create(0)
                    texture_slot.uv_layer = 'UVMap'
                    texture_slot.use = True
                    texture_slot.texture_coords = 'UV'
                    texture_slot.texture = texture
                    image = bpy.data.images.load(textureName)
                    texture.image = image

            # update mesh with new data
            mesh.update(calc_edges=True)
            mesh.validate()

            # normals
            if importOptions.normals == "blender":
                pass # blender will calculate the normals

            elif importOptions.normals == "mdcObject":

                # add first frame
                verts = self.objects[i].verts[0]
                normals = self.objects[i].normals[0]

                addedNormals = []

                for j in range(0, len(normals)):

                    vert = verts[j]
                    normal = normals[j]

                    b3 = mathutils.Vector(normal)

                    # find orthogonal basis vectors
                    b2 = mathutils.Vector(Util.getOrthogonal(b3))
                    b1 = b2.cross(b3)

                    # normalize
                    b1.normalize()
                    b2.normalize()
                    b3.normalize()

                    # build transformation matrix
                    basis = mathutils.Matrix()
                    basis[0].xyz = b1
                    basis[1].xyz = b2
                    basis[2].xyz = b3
                    basis.transpose()
                    basis.translation = object.matrix_world * mathutils.Vector((0,0,0))

                    # draw an arrow from normal
                    normalObject = bpy.data.objects.new("empty", None)
                    bpy.context.scene.objects.link(normalObject)
                    normalObject.name = 'vertex_normal'
                    normalObject.empty_draw_type = 'SINGLE_ARROW'

                    # parent object to vertex
                    normalObject.parent = object
                    normalObject.parent_type = 'VERTEX'
                    normalObject.parent_vertices[0] = j

                    # add location and rotation
                    normalObject.matrix_basis = basis

                    normalObject.keyframe_insert('location', \
                                              frame=0, \
                                              group='LocRot')
                    normalObject.keyframe_insert('rotation_euler', \
                                              frame=0, \
                                              group='LocRot')

                    # move to another layer if needed
                    layer = [False]*20
                    layer[int(importOptions.normalsLayer) - 1] = True
                    normalObject.layers = layer

                    addedNormals.append(normalObject)

                # add other frames
                for j in range(1, self.numFrames):

                    verts = self.objects[i].verts[j]
                    normals = self.objects[i].normals[j]

                    for k in range(0, len(normals)):

                        vert = verts[k]
                        normal = normals[k]

                        b3 = mathutils.Vector(normal)

                        # find orthogonal basis vectors
                        b2 = mathutils.Vector(Util.getOrthogonal(b3))
                        b1 = b2.cross(b3)

                        # normalize
                        b1.normalize()
                        b2.normalize()
                        b3.normalize()

                        # build transformation matrix
                        basis = mathutils.Matrix()
                        basis[0].xyz = b1
                        basis[1].xyz = b2
                        basis[2].xyz = b3
                        basis.transpose()
                        basis.translation = object.matrix_world * mathutils.Vector((0,0,0))

                        normalObject = addedNormals[k]

                        normalObject.matrix_basis = basis

                        normalObject.keyframe_insert('location', \
                                                  frame=j, \
                                                  group='LocRot')
                        normalObject.keyframe_insert('rotation_euler', \
                                                  frame=j, \
                                                  group='LocRot')

            # possible other future options
            else:
                pass

            # set smooth shading as default
            bpy.ops.object.shade_smooth()

        # tags
        if len(self.tags) > 0:

            addedTags = []

            # add first frame
            for i in range(0, len(self.tags)):

                tag = self.tags[i]

                tagObject = bpy.data.objects.new("empty", None)
                bpy.context.scene.objects.link(tagObject)
                tagObject.name = tag.name
                tagObject.empty_draw_type = 'ARROWS'
                tagObject.rotation_mode = 'XYZ'
                tagObject.matrix_basis = tag.locRot[0]

                tagObject.keyframe_insert('location', \
                                          frame=0, \
                                          group='LocRot')
                tagObject.keyframe_insert('rotation_euler', \
                                          frame=0, \
                                          group='LocRot')

                addedTags.append(tagObject)

            # add other frames
            for i in range(1, self.numFrames):

                for j in range(0, len(self.tags)):

                    tag = self.tags[j]

                    tagObject = addedTags[j]
                    tagObject.matrix_basis = tag.locRot[i]

                    tagObject.keyframe_insert('location', \
                                              frame=i, \
                                              group='LocRot')
                    tagObject.keyframe_insert('rotation_euler', \
                                              frame=i, \
                                              group='LocRot')

        # frames
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = self.numFrames - 1

        # TODO frameOrigins

        # some final settings
        if importOptions.toNewScene == True:

            bpy.context.scene.name = self.name
            bpy.context.scene.game_settings.material_mode = 'GLSL'
            bpy.ops.object.lamp_add(type='HEMI')
            bpy.context.scene.frame_set(0)

        # restore settings
        bpy.context.screen.scene = bpy.data.scenes[restoreScene]
