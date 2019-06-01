#!/usr/bin/python3
#
# io_scene_s3d
#
# Copyright (C) 2011 Steven J Thompson
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from .BinaryFile import BinaryFile

class S3DFile(BinaryFile):

    def loadImage(self, tex, textures, imageId):
        imageName = textures[imageId]

        # XXX: This use of try/except is messy.

        ## try the same directory as the s3d file
        try:
            image = bpy.data.images.load(self.getDirectory() + imageName)
            imageFound = True
        except:
            imageFound = False

        if imageFound is False:
            ## try the Data/Textures directory based on the user defined Jack Claw Data variable
            try:
                image = bpy.data.images.load(bpy.context.window_manager.jcdata + "Textures" + self.getFileSystemSlash() + imageName)
                imageFound = True
            except:
                pass

        if imageFound is False:
            ## try the Data/Textures/Cubemaps directory based on the user defined Jack Claw Data variable
            try:
                image = bpy.data.images.load(bpy.context.window_manager.jcdata + "Textures" + self.getFileSystemSlash() + "Cubemaps" + self.getFileSystemSlash() + imageName)
                imageFound = True
            except:
                pass

        if imageFound is True:
            print("Image loaded from: " + str(image.filepath))
            tex.image = image
            return True
        else:
            print("Could not load image id: " + str(imageName))
            return False

    def open(self, path, switchGLSL, removeDoubles):

        ####################
        ## S3D file
        ####################

        self.openFile(path, "rb")

        file_type = self.readFromFile("c", 4)

        version = self.readFromFile("i", 1)[0]
        print("S3D file version: " + str(version))

        textureCount = self.readFromFile("H", 1)[0]
        materialCount = self.readFromFile("H", 1)[0]
        objectCount = self.readFromFile("H", 1)[0]
        lightCount = self.readFromFile("H", 1)[0]
        helperCount = self.readFromFile("H", 1)[0]

        if version <= 7:
            foo = self.readFromFile("H", 1)[0]
        else:
            boneid = self.readFromFile("i", 1)[0]

        textures = []
        materials = []

        ## for all the textures in the file
        for t in range(textureCount):

            ## read texture filename
            textureName = self.readFromFile("str")

            ## put the texture into the textures list
            textures.append(textureName)
            
            texId = self.readFromFile("L", 1)
            texStartFrame = self.readFromFile("H", 1)[0]
            texFrameChangeTime = self.readFromFile("H", 1)[0]
            texDynamic = self.readFromFile("B", 1)

        ## for all the materials in the file
        for m in range(materialCount):

            ## read material name
            materialName = self.readFromFile("str")

            ## get the details of the material texture
            materialTextureBase = self.readFromFile("h", 1)[0]
            materialTextureBase2 = self.readFromFile("h", 1)[0]
            materialTextureBump = self.readFromFile("h", 1)[0]
            materialTextureReflection = self.readFromFile("h", 1)[0]

            if version >= 14:
                materialTextureDistortion = self.readFromFile("h", 1)[0]

            materialColour = self.readFromFile("f", 3)
            materialSelfIllum = self.readFromFile("f", 3)
            materialSpecular = self.readFromFile("f", 3)
            materialSpecularSharpness = self.readFromFile("f", 1)[0]

            materialDoubleSided = self.readFromFile("B", 1)
            materialWireframe = self.readFromFile("B", 1)

            materialReflectionTexgen = self.readFromFile("i", 1)

            ## materialAlphaBlendType. When 0 do not use image alpha, when 2 use image alpha.
            materialAlphaBlendType = self.readFromFile("i", 1)[0]

            materialTransparency = self.readFromFile("f", 1)

            if version >= 12:
                materialGlow = self.readFromFile("f", 1)

            if version >= 13:
                materialScrollSpeed = self.readFromFile("f", 2)
                materialScrollStart = self.readFromFile("B", 1)

            if materialTextureBase2 >= 0:
                tlayer = self.readFromFile("f", 2)
            
            if materialTextureReflection >= 0:
                tlayer = self.readFromFile("f", 2)

            mat = bpy.data.materials.new(materialName)
            mat.diffuse_color[0] = materialColour[0]
            mat.diffuse_color[1] = materialColour[1]
            mat.diffuse_color[2] = materialColour[2]

            mat.specular_color[0] = materialSpecular[0]
            mat.specular_color[1] = materialSpecular[1]
            mat.specular_color[2] = materialSpecular[2]

            if materialTextureBase != -1:
                tex = bpy.data.textures.new("diffuse", type = 'IMAGE')
                texSlot = mat.texture_slots.add()
                texSlot.texture = tex
                texSlot.texture_coords = 'UV'

                imageLoaded = self.loadImage(tex, textures, materialTextureBase)
            else:
                imageLoaded = False

            if imageLoaded == True and materialAlphaBlendType == 2:
                ## set material to use transparency
                mat.use_transparency = True
                mat.alpha = 0

                ## set the texture to use the alpha as transparency
                texSlot.use_map_alpha = True

            if materialTextureReflection != -1:
                tex = bpy.data.textures.new("reflection", type = 'IMAGE')
                texSlot = mat.texture_slots.add()
                texSlot.texture = tex
                texSlot.use_map_color_diffuse = False
                texSlot.use_map_color_spec = True
                texSlot.texture_coords = 'REFLECTION'

                self.loadImage(tex, textures, materialTextureReflection)

            ## append material name to the materials list
            materials.append(mat)

        ## for all the objects in the file
        for o in range(objectCount):

            objectName = self.readFromFile("str")
            objectParent = self.readFromFile("str")

            materialIndex = self.readFromFile("H", 1)[0]

            ## object position
            objectPositionX = self.readFromFile("f", 1)[0]
            ## Y and Z need to be swapped.
            objectPositionZ = self.readFromFile("f", 1)[0]
            objectPositionY = self.readFromFile("f", 1)[0]

            ## object rotation
            objectRotationX = self.readFromFile("f", 1)[0]
            objectRotationY = self.readFromFile("f", 1)[0]
            objectRotationZ = self.readFromFile("f", 1)[0]
            objectRotationW = self.readFromFile("f", 1)[0]

            ## object scale
            objectScaleX = self.readFromFile("f", 1)[0]
            ## Y and Z need to be swapped.
            objectScaleZ = self.readFromFile("f", 1)[0]
            objectScaleY = self.readFromFile("f", 1)[0]

            objectNoCollision = self.readFromFile("B", 1)
            objectNoRender = self.readFromFile("B", 1)

            if version >= 11:
                objectLightObject = self.readFromFile("B", 1)

            objectVertexAmount = self.readFromFile("H", 1)[0]
            objectFaceAmount = self.readFromFile("H", 1)[0]

            if version >= 10:
                objectLOD = self.readFromFile("B", 1)

            if version >= 7:
                objectWeights = self.readFromFile("B", 1)

            ## Create new mesh in Blender for this object
            mesh = bpy.data.meshes.new(name = str(objectName))

            ## Create new object in Blender for this object
            obj = bpy.data.objects.new(str(objectName), mesh)

            ## Add this object to the Blender scene
            base = bpy.context.scene.objects.link(obj)

            if ":" in objectName:
                objectType = objectName.split(":")[1]
                if objectType == "Collision":
                    ## draw collision mesh objects as wireframes
                    obj.draw_type = 'WIRE'

            ## Set the object location
            obj.location = (objectPositionX, objectPositionY, objectPositionZ)

            ## Set the object scale
            obj.scale = (objectScaleX, objectScaleY, objectScaleZ)

            ## Set the object rotation
            obj.rotation_mode = 'QUATERNION'
            obj.rotation_quaternion = (objectRotationW, objectRotationX, objectRotationY, objectRotationZ)

            vertex = []
            faces = []
            uvTex = []

            ## For all the vertex in the object
            for n in range(objectVertexAmount):
                vertexPosition = self.readFromFile("f", 3)
                vertexNormal = self.readFromFile("f", 3)
                vertexTextureCoords = self.readFromFile("f", 2)
                vertexTextureCoords2 = self.readFromFile("f", 2)

                ## store vertex data
                ## y and z are swapped due to differences between which axis is 'up' between Blender and Storm3D
                vertex.append((vertexPosition[0], vertexPosition[2], vertexPosition[1]))

                ## store texture coord data
                uvTex.append((vertexTextureCoords[0], -(vertexTextureCoords[1])))

            ## For all the faces in the object
            for n in range(objectFaceAmount):
                face = self.readFromFile("H", 3)
                faces.append(face)

            bonesList = {}
            if objectWeights == True:
                ## For all the weights in the object
                for n in range(objectVertexAmount):
                    bone1 = str(self.readFromFile("i", 1)[0])
                    bone2 = str(self.readFromFile("i", 1)[0])
                    weight1 = self.readFromFile("B", 1)
                    weight2 = self.readFromFile("B", 1)

                    ## Create the vertex group if it does not already exist.
                    if obj.vertex_groups.get(bone1) == None:
                        obj.vertex_groups.new(bone1)

                    ## Put the vertex data into the dictionary.
                    if bone1 in bonesList:
                        if weight1 in bonesList[bone1]:
                            bonesList[bone1][weight1].append(n)
                        else:
                            bonesList[bone1][weight1] = [n]
                    else:
                        bonesList[bone1] = {}

            ## Send data to the mesh in Blender
            mesh.from_pydata(vertex, [], faces)
            mesh.update()

            ## Put weight data into the vertex groups
            for b in bonesList.keys():
                for w in bonesList[b].keys():
                    obj.vertex_groups[b].add(bonesList[b][w], (w / 100), 'REPLACE')

            bpy.context.scene.objects.active = obj
            bpy.ops.mesh.uv_texture_add()
            uv = obj.data.uv_textures.active
            faces = obj.data.faces

            for face, i in enumerate(uv.data):
                i.uv1 = uvTex[faces[face].vertices[0]]
                i.uv2 = uvTex[faces[face].vertices[1]]
                i.uv3 = uvTex[faces[face].vertices[2]]


            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action = 'DESELECT')
            bpy.ops.mesh.select_non_manifold()
            bpy.ops.mesh.mark_seam(clear = False)
            if removeDoubles == True:
                bpy.ops.mesh.remove_doubles()
            bpy.ops.mesh.select_all(action = 'SELECT')
            bpy.ops.mesh.normals_make_consistent()
            bpy.ops.mesh.select_all(action = 'DESELECT')
            bpy.ops.object.mode_set(mode = 'OBJECT')

            if switchGLSL == True:
                ## Set GLSL shading
                bpy.context.scene.game_settings.material_mode = 'GLSL'

            ## Set all the 3d viewports to textured
            for a in bpy.context.screen.areas:
                if a.type == 'VIEW_3D':
                    a.spaces.active.viewport_shade = 'TEXTURED'

            ## Set the material in Blender
            mesh.materials.append(materials[materialIndex])

        if (objectCount > 0):
            bpy.ops.object.select_all(action = 'SELECT')
            bpy.ops.object.shade_smooth()
            bpy.ops.object.select_all(action = 'DESELECT')

        ## for all the lights in the file
        for l in range(lightCount):
            lightName = self.readFromFile("str")
            lightParentName = self.readFromFile("str")

            lightType = self.readFromFile("i", 1)
            lightLensflareIndex = self.readFromFile("i", 1)
            lightColour = self.readFromFile("f", 3)
            lightPosition = self.readFromFile("f", 3)
            lightDirection = self.readFromFile("f", 3)

            lightConeInner = self.readFromFile("f", 1)
            lightConeOuter = self.readFromFile("f", 1)
            lightMultiplier = self.readFromFile("f", 1)
            lightDecay = self.readFromFile("f", 1)

            lightKeyframeEndtime = self.readFromFile("i", 1)

            lightPoskeyAmount = self.readFromFile("B", 2)
            lightDirkeyAmount = self.readFromFile("B", 2)
            lightLumkeyAmount = self.readFromFile("B", 2)
            lightConekeyAmount = self.readFromFile("B", 2)

        ## for all the helpers in the file
        for h in range(helperCount):
            helpName = self.readFromFile("str")
            helpParentName = self.readFromFile("str")

            helpType = self.readFromFile("i", 1)
            helpPosition = self.readFromFile("f", 3)
            helpOther = self.readFromFile("f", 3)
            helpOther2 = self.readFromFile("f", 3)

            helpKeyframeEndtime = self.readFromFile("i", 1)

            helpPoskeyAmount = self.readFromFile("B", 2)
            helpO1keyAmount = self.readFromFile("B", 2)
            helpO2keyAmount = self.readFromFile("B", 2)

        ## Close the S3D file
        self.closeFile()

    def getObjectsOfType(self, objType):
        objectList = []
        for o in bpy.data.objects:
            if o.type == objType:
                objectList.append(bpy.data.objects[o.name])
        return objectList

    def write(self, path):

        ####################
        ## S3D file
        ####################

        ## Create and open the target S3D file
        self.openFile(path, "wb")

        file_type = "S3D0"
        version = 14
        self.writeToFile("s", file_type, False)
        self.writeToFile("i", version)

        allTextures = bpy.data.textures
        textures = 0
        for t in allTextures:
            if t.type == 'IMAGE':
                textures += 1

        self.writeToFile("H", textures)

        materials = bpy.data.materials
        self.writeToFile("H", len(materials))

        objects = self.getObjectsOfType('MESH')
        self.writeToFile("H", len(objects))

        lights = 0
        self.writeToFile("H", lights)

        num_hel = 0
        self.writeToFile("H", num_hel)

        boneid = 0
        self.writeToFile("i", boneid)

        texturesIdList = []
        for t in allTextures:
            if t.type == 'IMAGE':

                if t.image != None:
                    textureFileName = t.image.filepath.split(self.getFileSystemSlash())[-1]
                else:
                    ## the file name cannot be blank
                    textureFileName = 'none'

                ## textureName
                self.writeToFile("s", textureFileName)

                texturesIdList.append(textureFileName)

                ## texId
                self.writeToFile("L", 0)

                ## texStartFrame
                self.writeToFile("H", 0)

                ## texFrameChangeTime
                self.writeToFile("H", 0)

                ## texDynamic
                self.writeToFile("B", 0)

        materialsIdList = []
        for m in materials:

            ## write material name
            self.writeToFile("s", m.name)

            materialsIdList.append(m.name)

            texSlot = m.texture_slots[0]

            ## materialTextureBase
            if texSlot != None and bpy.data.textures[texSlot.name].type == 'IMAGE' and bpy.data.textures[texSlot.name].image != None:
                textureBase = bpy.data.textures[texSlot.name].image.filepath.split(self.getFileSystemSlash())[-1]
                textureId = texturesIdList.index(textureBase)
            else:
                textureId = -1
            self.writeToFile("h", textureId)

            ## materialTextureBase2
            materialTextureBase2 = -1
            self.writeToFile("h", materialTextureBase2)

            ## materialTextureBump
            self.writeToFile("h", -1)

            ## materialTextureReflection
            materialTextureReflection = -1
            self.writeToFile("h", materialTextureReflection)

            if version >= 14:
                ## materialTextureDistortion
                self.writeToFile("h", -1)

            ## materialColour
            self.writeToFile("f", m.diffuse_color[0])
            self.writeToFile("f", m.diffuse_color[1])
            self.writeToFile("f", m.diffuse_color[2])

            ## materialSelfIllum
            self.writeToFile("f", 0.0)
            self.writeToFile("f", 0.0)
            self.writeToFile("f", 0.0)

            ## materialSpecular
            self.writeToFile("f", m.specular_color[0])
            self.writeToFile("f", m.specular_color[1])
            self.writeToFile("f", m.specular_color[2])

            ## materialSpecularSharpness
            self.writeToFile("f", 1.0)

            ## materialDoubleSided
            self.writeToFile("B", 0)

            ## materialDoubleWireframe
            self.writeToFile("B", 0)

            ## materialReflectionTexgen
            self.writeToFile("i", 0)

            ## materialAlphaBlendType

            ## set the alpha type based on the setting in Blender
            if m.use_transparency == True:
                materialAlphaBlendType = 2
            else:
                materialAlphaBlendType = 0
            self.writeToFile("i", materialAlphaBlendType)

            ## materialTransparency
            self.writeToFile("f", 0.0)

            if version >= 12:
                ## materialGlow
                self.writeToFile("f", 0.0)

            if version >= 13:
                ## materialScrollSpeed
                self.writeToFile("f", 0.0)
                self.writeToFile("f", 0.0)

                ## materialScrollStart
                self.writeToFile("B", 0)

            if materialTextureBase2 >= 0:
                self.writeToFile("f", 1.0)
                self.writeToFile("f", 1.0)

            if materialTextureReflection >= 0:
                self.writeToFile("f", 1.0)
                self.writeToFile("f", 1.0)

        for o in objects:
            bpy.context.scene.objects.active = o
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action = 'SELECT')
            bpy.ops.mesh.quads_convert_to_tris()
            bpy.ops.mesh.flip_normals()
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.transform_apply(rotation = True)

            ## Convert UV seams to edge sharps
            for e in o.data.edges:
                e.use_edge_sharp = e.use_seam

            ## Use a edge split modifier to split the seams/sharps
            edgeSplit = o.modifiers.new(name = 'EdgeSplit', type = 'EDGE_SPLIT')
            edgeSplit.use_edge_angle = False
            bpy.ops.object.modifier_apply(apply_as = 'DATA', modifier = edgeSplit.name)

            ## objectName
            self.writeToFile("s", o.name)
            ## objectParent
            self.writeToFile("s", "")

            ## materialIndex
            materialId = materialsIdList.index(o.material_slots[0].name)
            self.writeToFile("H", materialId)

            ## object position
            self.writeToFile("f", o.location[0])
            ## Y and Z need to be swapped.
            self.writeToFile("f", o.location[2])
            self.writeToFile("f", o.location[1])

            ## object rotation
            self.writeToFile("f", o.rotation_quaternion[1])
            self.writeToFile("f", o.rotation_quaternion[3])
            self.writeToFile("f", o.rotation_quaternion[2])
            self.writeToFile("f", o.rotation_quaternion[0])

            ## object scale
            self.writeToFile("f", o.scale[0])
            ## Y and Z need to be swapped.
            self.writeToFile("f", o.scale[2])
            self.writeToFile("f", o.scale[1])

            ## objectNoCollision
            self.writeToFile("B", 0)
            ## objectNoRender
            self.writeToFile("B", 0)
            ## objectLightObject
            self.writeToFile("B", 0)

            vertex = o.data.vertices
            faces = o.data.faces

            ## objectVertexAmount
            self.writeToFile("H", len(vertex))
            ## objectFaceAmount
            self.writeToFile("H", len(faces))

            ## objectLOD
            self.writeToFile("B", 0)

            ## objectWeights
            if len(o.vertex_groups) > 0:
                objectWeights = 1
            else:
                objectWeights = 0
            self.writeToFile("B", objectWeights)

            vertexUVs = []

            for v in vertex:
                vertexUVs.append(v)

            ## If there is no UVs, then automatically generate some.
            if len(o.data.uv_textures) == 0:
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.uv.unwrap(method = 'ANGLE_BASED', fill_holes = True, correct_aspect = True)
                bpy.ops.object.mode_set(mode = 'OBJECT')

            for i, face in enumerate(o.data.uv_textures.active.data):
                vertexUVs[faces[i].vertices[0]] = face.uv1
                vertexUVs[faces[i].vertices[1]] = face.uv2
                vertexUVs[faces[i].vertices[2]] = face.uv3

            for i, v in enumerate(vertex):
                ## vertexPosition
                self.writeToFile("f", v.co[0])
                self.writeToFile("f", v.co[2])
                self.writeToFile("f", v.co[1])

                ## vertexNormal
                self.writeToFile("f", v.normal[0])
                self.writeToFile("f", v.normal[1])
                self.writeToFile("f", v.normal[2])

                ## vertexTextureCoords
                self.writeToFile("f", vertexUVs[i][0])
                self.writeToFile("f", -(vertexUVs[i][1]))

                ## vertexTextureCoords2
                self.writeToFile("f", 0.1)
                self.writeToFile("f", -0.1)

            for fa in faces:
                ## face index
                self.writeToFile("H", fa.vertices[0])
                self.writeToFile("H", fa.vertices[1])
                self.writeToFile("H", fa.vertices[2])

            if objectWeights == True:
                for v in vertex:

                    if len(v.groups) > 0:
                        vertexGroupName = o.vertex_groups[v.groups[0].group].name

                        ## Check if the bones have already have been renamed by B3D importing. Split to get the id if required.
                        if ":" in vertexGroupName:
                            vertexGroupId = vertexGroupName.split(":")[1]
                        else:
                            vertexGroupId = vertexGroupName

                        boneVertexGroup = int(vertexGroupId)
                        boneVertexWeight = int(v.groups[0].weight * 100)
                    else:
                        boneVertexGroup = 0
                        boneVertexWeight = 0

                    ## bone1
                    bone1 = self.writeToFile("i", boneVertexGroup)
                    ## bone2
                    bone2 = self.writeToFile("i", boneVertexGroup)
                    ## weight1
                    weight1 = self.writeToFile("B", boneVertexWeight)
                    ## weight2
                    weight2 = self.writeToFile("B", boneVertexWeight)


            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action = 'SELECT')
            bpy.ops.mesh.flip_normals()
            bpy.ops.object.mode_set(mode = 'OBJECT')

        ## Close the S3D file
        self.closeFile()
