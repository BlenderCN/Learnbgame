# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 02:55:27 2019

@author: AsteriskAmpersand
"""

from ..fmod.FMod import FModel
import bpy
import bmesh
import array
import os
from pathlib import Path

class FModImporter():   
    @staticmethod
    def execute(fmodPath, import_textures):
        meshes = FModel(fmodPath).traditionalMeshStructure()
        for ix, mesh in enumerate(meshes):
            FModImporter.importMesh(ix, mesh, fmodPath, import_textures)
            
    @staticmethod
    def importMesh(ix,mesh, modelPath, import_textures):
        meshObjects = []
        bpy.ops.object.select_all(action='DESELECT')

        #Geometry
        blenderMesh, blenderObject = FModImporter.createMesh("FModMeshpart %03d"%(ix),mesh, modelPath)
        #Normals Handling
        FModImporter.setNormals(mesh["normals"],blenderMesh)
        #UVs
        #for ix, uv_layer in enumerate(meshpart["uvs"]):
        uvLayer = FModImporter.createTextureLayer("UV%d"%0, blenderMesh, mesh["uvs"])
        uvLayer.active = ix == 0
        if import_textures:
            FModImporter.importTextures(blenderObject, modelPath)
        blenderMesh.update()
        meshObjects.append(blenderObject)
        
    @staticmethod
    def createMesh(name, meshpart, modelPath):
        blenderMesh = bpy.data.meshes.new("%s"%(name))
        blenderMesh.from_pydata(meshpart["vertices"],[],meshpart["faces"])
        blenderMesh.update()
        blenderObject = bpy.data.objects.new("%s"%(name), blenderMesh)
        bpy.context.scene.objects.link(blenderObject)
        return blenderMesh, blenderObject
    
    @staticmethod
    def createTextureLayer(name, blenderMesh, uv):#texFaces):
        #if bpy.context.active_object.mode!='OBJECT':
        #    bpy.ops.object.mode_set(mode='OBJECT')
        blenderMesh.uv_textures.new(name)
        blenderMesh.update()
        blenderBMesh = bmesh.new()
        blenderBMesh.from_mesh(blenderMesh)
        uv_layer = blenderBMesh.loops.layers.uv[name]
        blenderBMesh.faces.ensure_lookup_table()
        for face in blenderBMesh.faces:
            for loop in face.loops:
                #BlenderImporterAPI.dbg.write("\t%d\n"%loop.vert.index)
                loop[uv_layer].uv = uv[loop.vert.index]
        blenderBMesh.to_mesh(blenderMesh)
        blenderMesh.update()
        return blenderMesh.uv_textures[name]
		
    @staticmethod
    def setNormals(normals, meshpart):
        meshpart.update(calc_edges=True)
        #meshpart.normals_split_custom_set_from_vertices(normals)
        
        clnors = array.array('f', [0.0] * (len(meshpart.loops) * 3))
        meshpart.loops.foreach_get("normal", clnors)
        meshpart.polygons.foreach_set("use_smooth", [True] * len(meshpart.polygons))
        
        #meshpart.normals_split_custom_set(tuple(zip(*(iter(clnors),) * 3)))
        meshpart.normals_split_custom_set_from_vertices(normals)
        #meshpart.normals_split_custom_set([normals[loop.vertex_index] for loop in meshpart.loops])
        meshpart.use_auto_smooth = True
        meshpart.show_edge_sharp = True
        
    @staticmethod
    def maximizeClipping():
        for a in bpy.context.screen.areas:
            if a.type == 'VIEW_3D':
                for s in a.spaces:
                    if s.type == 'VIEW_3D':
                        s.clip_end = 10**9

    @staticmethod
    def clearScene():
        for key in list(bpy.context.scene.keys()):
            del bpy.context.scene[key]
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete() 
        for i in bpy.data.images.keys():
            bpy.data.images.remove(bpy.data.images[i])
        return
    
    @staticmethod
    def importTextures(mesh, path):
        try:
            filepath = FModImporter.prayToGod(path)
            textureData = FModImporter.fetchTexture(filepath)
            FModImporter.assignTexture(mesh, textureData)
        except Exception as e:
            pass
            
    @staticmethod
    def assignTexture(meshObject, textureData):
        for uvLayer in meshObject.data.uv_textures:
            for uv_tex_face in uvLayer.data:
                uv_tex_face.image = textureData
        meshObject.data.update()
        
    @staticmethod
    def fetchTexture(filepath):
        if os.path.exists(filepath):
            return bpy.data.images.load(filepath)
        else:
            raise FileNotFoundError("File %s not found"%filepath)
        
    @staticmethod
    def prayToGod(path):
        modelPath = Path(path)
        candidates = [modelPath.parent,
                      *sorted([f for f in modelPath.parents[1].glob('**/*') if f.is_dir() and f>modelPath.parent]),
                      *sorted([f for f in modelPath.parents[1].glob('**/*') if f.is_dir() and f<modelPath.parent])
                        ]
        for directory in candidates:
            current = sorted(list(directory.rglob("*.png")))
            if current:
                current.sort()
                return current[0].resolve().as_posix()