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

# Module: converter.py
# Description: converts between mdc_file and blender_scene.

from .mdc_file import *
from .blender_scene import *

class Converter:

    def blenderSceneToMdcFile(blenderScene):

        mdcFile = MDCFile()

        # find out which frames are base frames
        baseFrames = []
        baseFrames.append(0) # first frame is always a base frame

        for i in range(1, blenderScene.numFrames):

            baseFrameFound = False

            for j in range(0, len(blenderScene.objects)):

                if baseFrameFound == True:
                    break

                frameVerts = blenderScene.objects[j].verts[i]
                baseFrameVerts = blenderScene.objects[j].verts[baseFrames[-1]]

                for k in range(0, len(frameVerts)):

                    oldPos = baseFrameVerts[k]
                    newPos = frameVerts[k]

                    canEncode = MDCXyznCompressed.canEncode(oldPos, newPos)

                    if canEncode == False:
                        baseFrameFound = True
                        break

            if baseFrameFound == True:
                baseFrames.append(i)

        # frameBaseFrames, frameCompFrames - these are common to all surfaces
        frameBaseFrames = []
        frameBaseFrameIndex = 0
        frameCompFrames = []
        frameCompFrameIndex = 0
        for i in range(0, len(baseFrames)):

            baseFrame = baseFrames[i]
            if i + 1 >= len(baseFrames):
                nextBaseFrame = blenderScene.numFrames # imaginary base frame
            else:
                nextBaseFrame = baseFrames[i + 1]

            # first is always manual
            frameBaseFrames.append(MDCFrameBaseFrame(frameBaseFrameIndex))
            frameCompFrames.append(MDCFrameCompFrame(-1))
            for j in range(baseFrame + 1, nextBaseFrame):

                frameBaseFrames.append(MDCFrameBaseFrame(frameBaseFrameIndex))
                frameCompFrames.append(MDCFrameCompFrame(frameCompFrameIndex))
                frameCompFrameIndex += 1

            frameBaseFrameIndex += 1

        # we have everything we need, now let's fill in the data

        # surfaces
        for i in range(0, len(blenderScene.objects)):

            surface = MDCSurface()

            # frameBaseFrames
            surface.frameBaseFrames = frameBaseFrames

            # frameCompFrames
            surface.frameCompFrames = frameCompFrames

            # xyznCompressed
            for j in range(0, blenderScene.numFrames):

                if surface.frameCompFrames[j].index == -1:
                    baseFrame = j
                    continue

                compFrameVerts = []

                baseFrameVerts = blenderScene.objects[i].verts[baseFrame]
                baseFrameNormals = blenderScene.objects[i].normals[baseFrame]

                frameVerts = blenderScene.objects[i].verts[j]
                frameNormals = blenderScene.objects[i].normals[j]

                for k in range(0, len(frameVerts)):

                    oldPos = baseFrameVerts[k]
                    newPos = frameVerts[k]

                    delta_x = newPos[0] - oldPos[0]
                    delta_y = newPos[1] - oldPos[1]
                    delta_z = newPos[2] - oldPos[2]
                    delta = (delta_x, delta_y, delta_z)

                    oldNormal = baseFrameNormals[k]
                    newNormal = frameNormals[k]

                    delta_nx = newNormal[0]
                    delta_ny = newNormal[1]
                    delta_nz = newNormal[2]

                    delta_n = (delta_nx, delta_ny, delta_nz)

                    ofsVec = MDCXyznCompressed.encode(delta, delta_n)
                    xyznc = MDCXyznCompressed(ofsVec)
                    compFrameVerts.append(xyznc)

                surface.xyznCompressed.append(compFrameVerts)

            # xyzns
            for j in range(0, blenderScene.numFrames):

                if surface.frameCompFrames[j].index != -1:
                    continue

                baseFrameVerts = []

                frameVerts = blenderScene.objects[i].verts[j]
                frameNormals = blenderScene.objects[i].normals[j]

                for k in range(0, len(frameVerts)):

                    xyz = frameVerts[k]
                    n = frameNormals[k]

                    xyz1, xyz2, xyz3, normal \
                    = MDCXyzn.encode(xyz[0], xyz[1], xyz[2], n[0], n[1], n[2])
                    xyzn = MDCXyzn(xyz1, xyz2, xyz3, normal)
                    baseFrameVerts.append(xyzn)

                surface.xyzns.append(baseFrameVerts)

            # st
            for j in range(0, len(blenderScene.objects[i].uvMap)):

                s = blenderScene.objects[i].uvMap[j][0]
                t = 1 - blenderScene.objects[i].uvMap[j][1] # switch top/bottom

                surface.st.append(MDCSt(s, t))

            # shaders
            for j in range(0, len(blenderScene.objects[i].materialNames)):

                materialName = Util.prepare_name( \
                                   blenderScene.objects[i].materialNames[j], \
                                   '\x00', \
                                    MDCShader.nameLen)
                surface.shaders.append(MDCShader(materialName))

            # triangles
            for j in range(0, len(blenderScene.objects[i].faces)):

                # switch order
                i1 = blenderScene.objects[i].faces[j][2]
                i2 = blenderScene.objects[i].faces[j][1]
                i3 = blenderScene.objects[i].faces[j][0]

                surface.triangles.append(MDCTriangle(i1, i2, i3))

            # header
            ident = MDCSurfaceHeader.ident
            name = Util.prepare_name(blenderScene.objects[i].name, \
                                     '\x00', \
                                     MDCSurfaceHeader.nameLen)
            flags = 0
            numCompFrames = len(surface.xyznCompressed)
            numBaseFrames = len(surface.xyzns)
            numShaders = len(surface.shaders)
            numVerts = len(surface.xyzns[0])
            numTriangles = len(surface.triangles)

            ofsTriangles = 0 + struct.calcsize(MDCSurfaceHeader.format)

            ofsShaders = ofsTriangles + \
                                 numTriangles * \
                                 struct.calcsize(MDCTriangle.format)

            ofsSt = ofsShaders + \
                            numShaders * \
                            struct.calcsize(MDCShader.format)

            ofsXyzns = ofsSt + \
                               numVerts * \
                               struct.calcsize(MDCSt.format)

            ofsXyznCompressed = ofsXyzns + \
                                        (numBaseFrames * numVerts) * \
                                        struct.calcsize(MDCXyzn.format)

            ofsFrameBaseFrames = ofsXyznCompressed + \
                                         (numCompFrames * numVerts) * \
                                         struct.calcsize(MDCXyznCompressed.format)

            ofsFrameCompFrames = ofsFrameBaseFrames + \
                                         (numBaseFrames + numCompFrames) * \
                                         struct.calcsize(MDCFrameBaseFrame.format)

            ofsEnd = ofsFrameCompFrames + \
                             (numBaseFrames + numCompFrames) * \
                             struct.calcsize(MDCFrameCompFrame.format)

            surface.header = MDCSurfaceHeader(ident, name, flags, \
                                              numCompFrames, numBaseFrames, \
                                              numShaders, numVerts, \
                                              numTriangles, ofsTriangles, \
                                              ofsShaders, ofsSt, ofsXyzns, \
                                              ofsXyznCompressed, \
                                              ofsFrameBaseFrames, \
                                              ofsFrameCompFrames, \
                                              ofsEnd)

            mdcFile.surfaces.append(surface)

        # tags
        for i in range(0, blenderScene.numFrames):

            frameTags = []

            for j in range(0, len(blenderScene.tags)):

                blenderTag = blenderScene.tags[j]

                x, y, z, yaw, pitch, roll \
                = BlenderTag.decodeLocRot(blenderTag.locRot[i])

                x, y, z, anglesX, anglesY, anglesZ \
                = MDCTag.encode(x, y, z, yaw, pitch, roll)

                mdcTag = MDCTag(x, y, z, anglesX, anglesY, anglesZ)

                frameTags.append(mdcTag)

            mdcFile.tags.append(frameTags)

        # tagNames
        for i in range(0, len(blenderScene.tags)):

            name = Util.prepare_name(blenderScene.tags[i].name, \
                                     '\x00', \
                                     MDCTagname.nameLen)
            tagName = MDCTagname(name)
            mdcFile.tagNames.append(tagName)

        # frames: minBound, maxBound, radius
        for i in range(0, blenderScene.numFrames):

            minX, minY, minZ = [MDCXyzn.floatMax] * 3
            maxX, maxY, maxZ = [MDCXyzn.floatMin] * 3

            for blenderObject in blenderScene.objects:

                frameVerts = blenderObject.verts[i]

                for vert in frameVerts:

                    minX, minY, minZ = min(vert[0], minX), \
                                       min(vert[1], minY), \
                                       min(vert[2], minZ)
                    maxX, maxY, maxZ = max(vert[0], maxX), \
                                       max(vert[1], maxY), \
                                       max(vert[2], maxZ)

            centerX = minX + ((maxX - minX) / 2)
            centerY = minY + ((maxY - minY) / 2)
            centerZ = minZ + ((maxZ - minZ) / 2)
            radius = Util.calcDistance((centerX, centerY, centerZ), \
                                       (minX, minY, minZ))

            frameName = Util.prepare_name(blenderScene.frameNames[i], \
                                         '\x00', \
                                         MDCFrame.nameLen)

            # TODO localOrigin is always 0?
            frame = MDCFrame(minX, minY, minZ, \
                             maxX, maxY, maxZ, \
                             0, 0, 0, \
                             radius,
                             frameName)

            mdcFile.frames.append(frame)

        # header
        ident = MDCFileHeader.ident
        version = MDCFileHeader.version
        name = Util.prepare_name(blenderScene.name, '\x00', \
                                 MDCFileHeader.nameLen)
        flags = 0

        numFrames = len(mdcFile.frames)
        numTags = len(mdcFile.tagNames)
        numSurfaces = len(mdcFile.surfaces)
        numSkins = 0

        ofsFrames = 0 + struct.calcsize(MDCFileHeader.format)

        ofsTagNames = ofsFrames + \
                              numFrames * \
                              struct.calcsize(MDCFrame.format)

        ofsTags = ofsTagNames + \
                          numTags * \
                          struct.calcsize(MDCTagname.format)

        ofsSurfaces = ofsTags + \
                              (numFrames * numTags) * \
                              struct.calcsize(MDCTag.format)

        surfacesSize = 0
        for i in range(0, len(mdcFile.surfaces)):
            surfacesSize += mdcFile.surfaces[i].header.ofsEnd
        ofsEnd = ofsSurfaces + surfacesSize

        mdcFile.header = MDCFileHeader(ident, version, name, flags, numFrames, \
                                       numTags, numSurfaces, numSkins, \
                                       ofsFrames, ofsTagNames, ofsTags, \
                                       ofsSurfaces, ofsEnd)

        return mdcFile


    def mdcFileToBlenderScene(mdcFile):

        sceneName = Util.cleanup_string(mdcFile.header.name)
        blenderScene = BlenderScene(sceneName)

        # numFrames
        blenderScene.numFrames = mdcFile.header.numFrames

        # frameNames and frameOrigins
        for i in range(0, mdcFile.header.numFrames):

            frameName = Util.cleanup_string(mdcFile.frames[i].name)
            blenderScene.frameNames.append(frameName)
            blenderScene.frameOrigins.append((mdcFile.frames[i].localOrigin[0], \
                                              mdcFile.frames[i].localOrigin[1], \
                                              mdcFile.frames[i].localOrigin[2]))

        # tags
        for i in range(0, mdcFile.header.numTags):

            tagName = Util.cleanup_string(mdcFile.tagNames[i].name)
            blenderTag = BlenderTag(tagName)
            blenderScene.tags.append(blenderTag)

        for i in range(0, mdcFile.header.numFrames):

            for j in range(0, mdcFile.header.numTags):

                mdcTag = mdcFile.tags[i][j]
                blenderTag = blenderScene.tags[j]

                x, y, z, yaw, pitch, roll = MDCTag.decode(mdcTag.xyz[0], \
                                                          mdcTag.xyz[1], \
                                                          mdcTag.xyz[2], \
                                                          mdcTag.angles[0], \
                                                          mdcTag.angles[1], \
                                                          mdcTag.angles[2])

                locRot = BlenderTag.encodeLocRot(x, y, z, yaw, pitch, roll)
                blenderTag.locRot.append(locRot)

        # objects
        for i in range(0, mdcFile.header.numSurfaces):

            surface = mdcFile.surfaces[i]

            objectName = Util.cleanup_string(surface.header.name)
            blenderObject = BlenderObject(objectName)

            # verts, normals
            for j in range(0, mdcFile.header.numFrames):

                frameVerts = []
                frameNormals = []

                baseFrameIndex = surface.frameBaseFrames[j].index

                # frame is compressed
                if surface.frameCompFrames[j].index >= 0:

                    compFrameIndex = surface.frameCompFrames[j].index

                    for k in range(0, surface.header.numVerts):

                        # calc v_base
                        xyzn = surface.xyzns[baseFrameIndex][k]

                        v_base_x, v_base_y, v_base_z, \
                        n_base_x, n_base_y, n_base_z \
                        = MDCXyzn.decode(xyzn.xyz[0], xyzn.xyz[1], xyzn.xyz[2], \
                                         xyzn.normal)

                        # calc v_delta
                        xyznc = surface.xyznCompressed[compFrameIndex][k]
                        v_delta_x, v_delta_y, v_delta_z, nx, ny, nz \
                        = MDCXyznCompressed.decode(xyznc.ofsVec)

                        # v = v_localOrigin + v_base + v_delta
                        x = mdcFile.frames[j].localOrigin[0] + v_base_x + v_delta_x
                        y = mdcFile.frames[j].localOrigin[1] + v_base_y + v_delta_y
                        z = mdcFile.frames[j].localOrigin[2] + v_base_z + v_delta_z
                        v = (x , y, z)

                        frameVerts.append(v)

                        # normal
                        frameNormals.append((nx, ny, nz))

                # frame is not compressed
                else:

                    for k in range(0, surface.header.numVerts):

                        # calc v_base
                        xyzn = surface.xyzns[baseFrameIndex][k]

                        v_base_x, v_base_y, v_base_z, \
                        nx, ny, nz, \
                        = MDCXyzn.decode(xyzn.xyz[0], xyzn.xyz[1], xyzn.xyz[2], \
                                         xyzn.normal)

                        # calc v_delta
                        v_delta_x = 0
                        v_delta_y = 0
                        v_delta_z = 0

                        # v = v_localOrigin + v_base + v_delta
                        x = mdcFile.frames[j].localOrigin[0] + v_base_x + v_delta_x
                        y = mdcFile.frames[j].localOrigin[1] + v_base_y + v_delta_y
                        z = mdcFile.frames[j].localOrigin[2] + v_base_z + v_delta_z
                        v = (x , y, z)

                        frameVerts.append(v)

                        # normal
                        frameNormals.append((nx, ny, nz))

                blenderObject.verts.append(frameVerts)
                blenderObject.normals.append(frameNormals)

            # uvMap
            for j in range(0, surface.header.numVerts):

                u = surface.st[j].st[0]
                v = 1 - surface.st[j].st[1] # switch top/bottom

                blenderObject.uvMap.append((u, v))

            # faces
            for j in range(0, surface.header.numTriangles):

                # switch order
                i1 = surface.triangles[j].indexes[2]
                i2 = surface.triangles[j].indexes[1]
                i3 = surface.triangles[j].indexes[0]

                blenderObject.faces.append((i1, i2, i3))

            # materialNames
            for j in range(0, surface.header.numShaders):

                name = Util.cleanup_string(surface.shaders[j].name)
                blenderObject.materialNames.append(name)

            # save object
            blenderScene.objects.append(blenderObject)

        return blenderScene
