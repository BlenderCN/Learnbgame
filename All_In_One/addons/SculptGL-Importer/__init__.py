# MIT License
# 
# Copyright (c) 2018 3DI70R
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# all file format information gathered from
# https://github.com/stephomi/sculptgl/blob/master/src/files/ExportSGL.js

import bpy
import struct
import bmesh
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty

bl_info = {
    "name": "SculptGL .sgl format",
    "author": "3DI70R",
    "version": (1, 0, 0),
    "blender": (2, 77, 0),
    "location": "File > Import-Export",
    "description": "Import SGL mesh, colors and PBR data",
    "warning": "",
    "category": "Learnbgame",
}

triangleIndex = 4294967295

def readInt(file):
    return struct.unpack("I", file.read(4))[0]
    
def readFloat(file):
    return struct.unpack("f", file.read(4))[0]

def readArray(file, count, func):
    result = []
    
    for i in range(count):
        result.append(func(file))
    
    return result

def readVertex(file):
	x = readFloat(file)
	y = readFloat(file)
	z = readFloat(file)
	return [x, -z, y]

def skip(file, count):
	file.seek(count, os.SEEK_CUR)

def distinct(seq):
  seen = set()
  return [x for x in seq if x not in seen and not seen.add(x)]

def readFile(filePath):
    
    result = {}
    meshes = []
    
    result["meshes"] = meshes
    
    with open(filePath, "rb") as f:
        
        result["version"] = readInt(f)
        
        result["showGrid"] = readInt(f)
        result["showSymmetryLine"] = readInt(f)
        result["showContour"] = readInt(f)
        
        result["projectionType"] = readInt(f)
        result["mode"] = readInt(f)
        result["fov"] = readFloat(f)
        result["usePivot"] = readInt(f)
        
        meshCount = readInt(f)
        
        for i in range(meshCount):
            
            mesh = {}
            
            mesh["shaderType"] = readInt(f)
            mesh["matcap"] = readInt(f)
            mesh["showWireframe"] = readInt(f)
            mesh["flatShading"] = readInt(f) != 0
            mesh["opacity"] = readInt(f)
            
            mesh["position"] = readArray(f, 3, readFloat)
            mesh["matrix"] = readArray(f, 16 ,readFloat)
            mesh["scale"] = readFloat(f)
            
            vertexCount = readInt(f)
            mesh["vertices"] = readArray(f, vertexCount, lambda file: readVertex(file))
            
            colorCount = readInt(f)
            mesh["colors"] = readArray(f, colorCount, lambda file: readArray(file, 3, readFloat))
            
            materialCount = readInt(f)
            mesh["materials"] = readArray(f, materialCount, lambda file: readArray(file, 3, readFloat))
            
            faceCount = readInt(f)
            mesh["faces"] = readArray(f, faceCount, lambda file: readArray(file, 4, readInt))

            uvCount = readInt(f)
            mesh["uv"] = readArray(f, uvCount, lambda file: readArray(file, 2, readFloat))

            faceUvCount = readInt(f)
            mesh["face_uv"] = readArray(f, faceUvCount, lambda file: readArray(file, 4, readInt))

            meshes.append(mesh)

        return result
    
def createSglMesh(sgl):
    scene = bpy.context.scene

    for i, sglMesh in enumerate(sgl["meshes"]):
        
        name = "SGLMesh" + str(i)

        scale = sglMesh["scale"]
        position = sglMesh["position"]
        
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        obj.scale = (scale, scale, scale)

        scene.objects.link(obj)
        scene.objects.active = obj

        bm = bmesh.new()
        vertices = []
        
        colorLayer = bm.loops.layers.color.new("Color")
        pbrLayer = bm.loops.layers.color.new("PBR")
        uvLayer = bm.loops.layers.uv.new("UV")
        
        sglColors = sglMesh["colors"]
        sglMaterials = sglMesh["materials"]
        sglUv = sglMesh["uv"]
        sglFaceUv = sglMesh["face_uv"]

        for v in sglMesh["vertices"]:
            vertices.append(bm.verts.new(v))
            
        bm.verts.index_update()
        smooth = not sglMesh["flatShading"]
            
        for faceIndex, f in enumerate(sglMesh["faces"]):

            if f[3] == triangleIndex:
                faceVertices = (vertices[f[0]], vertices[f[1]], vertices[f[2]])
            else:
                faceVertices = (vertices[f[0]], vertices[f[1]], vertices[f[2]], vertices[f[3]])

			# SculptGL can write glitchy face with duplicate vertices
            faceVertices = distinct(faceVertices)

            if len(faceVertices) >= 3:
                face = bm.faces.new(faceVertices)
                face.smooth = smooth
                
                for loopIndex, l in enumerate(face.loops):
                    vertId = l.vert.index
                    l[colorLayer] = sglColors[vertId]
                    l[pbrLayer] = sglMaterials[vertId]

                    if len(sglUv) != 0:
                        l[uvLayer].uv = sglUv[sglFaceUv[faceIndex][loopIndex]]
            
        bm.to_mesh(bpy.context.object.data)  
        bm.free()
        
        mesh.calc_normals()

class ImportSGL(Operator, ImportHelper):

    bl_idname = "file.sgl"
    bl_label = "Import SGL"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".sgl"
    filter_glob = StringProperty(default="*.sgl", options={'HIDDEN'})

    def execute(self, context):
        createSglMesh(readFile(self.filepath))
        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportSGL.bl_idname, text="SculptGL (.sgl)")


def register():
    bpy.utils.register_class(ImportSGL)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
   bpy.utils.unregister_class(ImportSGL)
   bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
