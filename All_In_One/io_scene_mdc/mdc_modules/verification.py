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

# Module: verify.py
# Description: verifies data from mdcfile and blenderscene.

from .mdc_file import *
from .blender_scene import *

class Verify:

    def blenderScene(blenderScene):

        if blenderScene == None:
            return (False, "Could not find blender scene")

        # blenderScene.name
        nameLen = len(blenderScene.name)
        if nameLen <= 0:
            blenderScene.name = "BlenderScene"

        if nameLen > MDCFileHeader.nameLen:
            return (False, "Length of scene name out of bounds. Must be between {} and {}, found={}".format(0, MDCFileHeader.nameLen, nameLen))

        # blenderScene.numFrames
        if blenderScene.numFrames <= 0 or \
           blenderScene.numFrames > MDCFrame.maxFrames:
             return (False, "Number of frames out of bounds. Must be between {} and {}, found={}".format(0, MDCFrame.maxFrames, blenderScene.numFrames))

        # blenderScene.frameNames
        if blenderScene.numFrames != len(blenderScene.frameNames):
             return (False, "Number of frame names unequal number of frames, frameNames={}, numFrames={}".format(len(blenderScene.frameNames), blenderScene.numFrames))

        for frameName in blenderScene.frameNames:
            nameLen = len(frameName)
            if nameLen <= 0 or nameLen > MDCFrame.nameLen:
                return (False, "Framename out of bounds. Must be between {} and {}, found={}".format(0, MDCFrame.nameLen, nameLen))

        # blenderScene.frameOrigins
        if blenderScene.numFrames != len(blenderScene.frameOrigins):
            return (False, "Number of frames unequal number of frameOrigins, numFrames={}, frameOrigins={}".format(blenderScene.numFrames, len(blenderScene.frameOrigins)))

        # blenderScene.tags
        if len(blenderScene.tags) > MDCTag.maxTags:
            return (False, "Number of tags out of bounds. Must be between {} and {}, found={}".format(0, MDCTag.maxTags, len(blenderScene.tags)))

        # blenderTag.name
        for tag in blenderScene.tags:
            nameLen = len(tag.name)
            if nameLen <= 0 or nameLen > MDCTagname.nameLen:
             return (False, "Length of tag name out of bounds. Must be between {} and {}, found={}".format(0, MDCTagname.nameLen, nameLen))

        # blenderScene.objects
        objectsLen = len(blenderScene.objects)
        if objectsLen > MDCSurface.maxSurfaces:
            return (False, "Number of objects out of bounds. Must be between {} and {}, found={}".format(0, MDCSurface.maxSurfaces, objectsLen))

        for object in blenderScene.objects:

            # blenderObject.name
            nameLen = len(object.name)
            if nameLen <= 0 or nameLen > MDCSurfaceHeader.nameLen:
                return (False, "Object name out of bounds. Must be between {} and {}, found={}".format(0, MDCSurfaceHeader.nameLen, nameLen))

            # blenderObject.verts
            vertLen = len(object.verts)
            if vertLen != blenderScene.numFrames:
                return (False, "Could not read vertexes on all frames. Must be {}, found={}".format(blenderScene.numFrames, vertLen))

            frameVertLen = len(object.verts[0])
            if frameVertLen < 3 or frameVertLen > MDCXyzn.maxVerts:
                return (False, "Number of vertexes out of bounds. Must be between {} and {}, found={}".format(3, MDCXyzn.maxVerts, frameVertLen))

            for i in range(0, blenderScene.numFrames):

                frameVerts = object.verts[i]

                if len(frameVerts) != frameVertLen:
                    return (False, "Number of vertexes in frame={} does not match number of vertexes in first frame. Must be {}, found={}".format(i, frameVertLen, len(frameVerts)))

                for j in range(0, len(frameVerts)):

                    frameVert = frameVerts[j]
                    x = frameVert[0]
                    y = frameVert[1]
                    z = frameVert[2]

                    if x < MDCXyzn.floatMin or x > MDCXyzn.floatMax or \
                       y < MDCXyzn.floatMin or y > MDCXyzn.floatMax or \
                       z < MDCXyzn.floatMin or z > MDCXyzn.floatMax:
                        return (False, "Vertex xyz value out of bounds. Vertex={}, frame={}. Must be between floatMin={} and floatMax={}".format(j, i, MDCXyzn.floatMin, MDCXyzn.floatMax))

            # blenderObject.normals
            if len(object.normals) != vertLen:
                return (False, "Could not read vertex normals on all frames. Must be {}, found={}".format(vertLen, len(object.normals)))

            for i in range(0, len(object.normals)):

                frameNormals = object.normals[i]

                if len(frameNormals) != frameVertLen:
                    return (False, "Number of vertex normals does not match number of vertexes in frame {}. Must be {}, found={}".format(i, frameVertLen, len(frameNormals)))

            # blenderObject.uvMap
            if object.uvMap == None:
                return (False, "Could not find UV map for object '{}'.".format(object.name))

            if len(object.uvMap) != frameVertLen:
                return (False, "Not all or too many vertexes mapped into UV Map. Must be {}, found={}. MDC supports 1:1 mapping only.".format(frameVertLen, len(object.uvMap)))

            # blenderObject.faces
            facesLen = len(object.faces)
            if facesLen < 1 or facesLen > MDCTriangle.maxTriangles:
                return (False, "Number of faces out of bounds. Must be between {} and {}, found={}".format(1, MDCTriangle.maxTriangles, facesLen))

            # blenderObject.materialNames
            materialNamesLen = len(object.materialNames)

            if materialNamesLen <= 0:
                return (False, "Could not find material for object '{}'.".format(object.name))

            if materialNamesLen > MDCShader.maxShaders:
                return (False, "Number of shaders for object '{}' out of bounds. Must be between {} and {}, found={}".format(object.name, 0, MDCShader.maxShaders, materialNamesLen))

        return (True, "SUCCESS")


    def mdcFile(mdcFile):

        if mdcFile == None:
            return (False, "Could not find mdc file" )

        # mdcFile.header
        if mdcFile.header.ident != MDCFileHeader.ident:
            return (False, "Could not match header ident. Must be {}, found={}".format(MDCFileHeader.ident, mdcFile.header.ident))

        if mdcFile.header.version != MDCFileHeader.version:
            return (False, "Could not match header version. Must be {}, found={}".format(MDCFileHeader, mdcFile.header.version))

        if len(mdcFile.header.name) != MDCFileHeader.nameLen:
            return (False, "Length of header name out of bounds. Must be between {} and {}, found={}".format(0, MDCFileHeader.nameLen, len(mdcFile.header.name)))

        if mdcFile.header.numFrames <= 0 or \
           mdcFile.header.numFrames > MDCFrame.maxFrames:
            return (False, "Number of frames out of bounds. Must be between {} and {}, found={}".format(0, MDCFrame.maxFrames, mdcFile.header.numFrames))

        if mdcFile.header.numTags > MDCTag.maxTags:
            return (False, "Number of tags out of bounds. Must be between {} and {}, found={}".format(0, MDCTag.maxTags, mdcFile.header.numTags))

        if mdcFile.header.numSurfaces > MDCSurface.maxSurfaces:
            return (False, "Number of surfaces out of bounds. Must be between {} and {}, found={}".format(0, MDCSurface.maxSurfaces, mdcFile.header.numSurfaces))

        # mdcFile.frames
        if len(mdcFile.frames) != mdcFile.header.numFrames:
            return (False, "Number of frames does not match header. Must be {}, found={}".format(mdcFile.header.numFrames, len(mdcFile.frames)))

        for i in range (0, len(mdcFile.frames)):

            frame = mdcFile.frames[i]
            if len(frame.name) != MDCFrame.nameLen:
                return (False, "Frame name for frame {} out of bounds. Must be {}, found={}".format(i, MDCFrame.nameLen, len(frame.name)))

        # mdcFile.tagNames
        if len(mdcFile.tagNames) != mdcFile.header.numTags:
            return (False, "Number of tag names does not match header. Must be {}, found={}".format(mdcFile.header.numTags, len(mdcFile.tagNames)))

        for i in range(0, len(mdcFile.tagNames)):

            tagName = mdcFile.tagNames[i]
            if len(tagName.name) != MDCTagname.nameLen:
                return (False, "Tag name for frame {} out of bounds. Must be {}, found={}".format(i, MDCTagname.nameLen, len(tagName.name)))

        # mdcFile.tags
        for i in range(0, len(mdcFile.tags)):

            frameTags = mdcFile.tags[i]
            if len(frameTags) != mdcFile.header.numTags:
                return (False, "Number of tags in frame {} does not match header. Must be {}, found={}".format(i, mdcFile.header.numTags, len(frameTags)))

        # mdcFile.surfaces
        if len(mdcFile.surfaces) != mdcFile.header.numSurfaces:
            return (False, "Number of surfaces does not match header. Must be {}, found={}".format(mdcFile.header.numSurfaces, len(mdcFile.surfaces)))

        numBaseFrames = None
        numCompFrames = None
        for surface in mdcFile.surfaces:

            # surface.header
            if surface.header.ident != MDCSurfaceHeader.ident:
                return (False, "Could not match surface header ident. Must be {}, found={}".format(MDCSurfaceHeader.ident, surface.header.ident))

            if len(surface.header.name) != MDCSurfaceHeader.nameLen:
                return (False, "Length of surface header name out of bounds. Must be between {} and {}, found={}".format(0, MDCSurfaceHeader.nameLen, len(surface.header.name)))

            if surface.header.numCompFrames + surface.header.numBaseFrames \
               != mdcFile.header.numFrames:
                return (False, "Number of frames does not match number of comp and base frames. Must be {}, found={}".format(mdcFile.header.numFrames, surface.header.numCompFrames + surface.header.numBaseFrames))

            if numBaseFrames == None or numCompFrames == None:
                numBaseFrames = surface.header.numBaseFrames
                numCompFrames = surface.header.numCompFrames
            if numBaseFrames != surface.header.numBaseFrames or \
               numCompFrames != surface.header.numCompFrames:
                return (False, "Number of comp and base frames must be the same for all surfaces.")

            if surface.header.numShaders < 1 or \
               surface.header.numShaders > MDCShader.maxShaders:
                return (False, "Number of shaders out of bounds. Must be between {} and {}, found={}".format(0, MDCShader.maxShaders, surface.header.numShaders))

            if surface.header.numVerts < 3 or \
               surface.header.numVerts > MDCXyzn.maxVerts:
                return (False, "Number of verts out of bounds. Must be between {} and {}, found={}".format(3, MDCXyzn.maxVerts, surface.header.numVerts))

            if surface.header.numTriangles < 1 or \
               surface.header.numTriangles > MDCTriangle.maxTriangles:
                return (False, "Number of triangles out of bounds. Must be between {} and {}, found={}".format(1, MDCTriangle.maxTriangles, surface.header.numTriangles))

            # surface.triangles
            if len(surface.triangles) != surface.header.numTriangles:
                return (False, "Number of triangles does not match header. Must be {}, found={}".format(surface.header.numTriangles, len(surface.triangles)))

            # surface.shaders
            if len(surface.shaders) != surface.header.numShaders:
                return (False, "Number of shaders does not match header. Must be {}, found={}".format(surface.header.numShaders, len(surface.shaders)))

            for shader in surface.shaders:

                if len(shader.name) != MDCShader.nameLen:
                    return (False, "Length of shader name out of bounds. Must be between {} and {}, found={}".format(MDCShader.nameLen, len(shader.name)))

            # surface.st
            if len(surface.st) != surface.header.numVerts:
                return (False, "Number of vertexes does not match number of uv mapping. Must be {}, found={}".format(surface.header.numVerts, len(surface.st)))

            # surface.xyzns
            if len(surface.xyzns) != surface.header.numBaseFrames:
                return (False, "Number of base frames does not match header. Must be {}, found={}".format(surface.header.numBaseFrames, len(surface.xyzns)))

            for baseFrame in surface.xyzns:
                if len(baseFrame) != surface.header.numVerts:
                    return (False, "Number of vertexes in base frame does not match header. Must be {}, found={}".format(surface.header.numVerts, len(baseFrame)))

            # surface.xyznCompressed
            if len(surface.xyznCompressed) != surface.header.numCompFrames:
                return (False, "Number of comp frames does not match header. Must be {}, found={}".format(surface.header.numCompFrames, len(surface.xyznCompressed)))

            for compFrame in surface.xyznCompressed:
                if len(compFrame) != surface.header.numVerts:
                    return (False, "Number of vertexes in comp frame does not match header. Must be {}, found={}".format(surface.header.numVerts, len(compFrame)))

            # surface.frameBaseFrames
            if len(surface.frameBaseFrames) != mdcFile.header.numFrames:
                return (False, "Number of frameBaseFrames does not match header. Must be {}, found={}".format(mdcFile.header.numFrames, len(surface.frameBaseFrames)))

            # surface.frameCompFrames
            if len(surface.frameCompFrames) != mdcFile.header.numFrames:
                return (False, "Number of frameCompFrames does not match header. Must be {}, found={}".format(mdcFile.header.numFrames, len(surface.frameCompFrames)))

        return (True, "SUCCESS")