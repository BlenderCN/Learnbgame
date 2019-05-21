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

import bpy

from . import fbx
from .fbx_basic import *
from .fbx_props import *
from .fbx_model import *
from . import fbx_material

#------------------------------------------------------------------
#   Geometry
#------------------------------------------------------------------

class FbxGeometryBase(FbxObject):
    propertyTemplate = (
"""
""")

    def __init__(self, subtype, btype):
        FbxObject.__init__(self, 'Geometry', subtype, btype)
        self.normalLayers = []
        self.uvLayers = []
        self.materialLayers = []
        self.textureLayers = []
        self.shapeKeys = {}
        self.blendDeformers = {}
        self.hastex = False
        self.materials = []
        

    def parseNodes(self, pnodes):
        rest = []
        for pnode in pnodes:
            if pnode.key == 'Layer' : 
                pass
            elif pnode.key == 'LayerElementNormal' : 
                self.normalLayers.append( FbxLayerElementNormal().parse(pnode) )
            elif pnode.key == 'LayerElementUV' : 
                self.uvLayers.append( FbxLayerElementUV().parse(pnode) )
            elif pnode.key == 'LayerElementMaterial' : 
                self.materialLayers.append( FbxLayerElementMaterial().parse(pnode) )
            elif pnode.key == 'LayerElementTexture' : 
                self.textureLayers.append( FbxLayerElementTexture().parse(pnode) )  
            else:
                rest.append(pnode)

        return FbxObject.parseNodes(self, rest)

    
    def make(self, rna, ob=None, matfaces=None):        
        FbxObject.make(self, rna)
        #if not hasattr(rna, "materials") or not rna.materials.items():
        if not hasattr(rna, "materials"):        
            return self
        
        tn = 0
        layer = DummyLayer()
        self.materialLayers.append(FbxLayerElementMaterial().make(layer, 0, rna.materials, matfaces))
        
        for mn,mat in enumerate(rna.materials):
            if mat:
                parent = fbx.nodes.objects[ob.name]
                fbx.nodes.materials[mat.name].makeOOLink(parent)
                self.materials.append(mat)
                
                for mtex in mat.texture_slots:
                    if mtex and mtex.texture:
                        tex = mtex.texture
                        if tex and tex.type == 'IMAGE':
                            self.hastex = True

        self.textureLayers.append(FbxLayerElementTexture().make(layer, 0, self.hastex))            
        return self


    def addDefinition(self, definitions):     
        FbxObject.addDefinition(self, definitions)
        for node in self.shapeKeys.values():
            node.addDefinition(definitions)
        for node in self.blendDeformers.values():
            node.addDefinition(definitions)

                                
    def writeFooter(self, fp):
        if (self.normalLayers or 
            self.uvLayers or 
            self.materialLayers or 
            self.textureLayers):
            for layer in self.normalLayers:
                layer.writeFbx(fp)
            for layer in self.uvLayers:
                layer.writeFbx(fp)
            for layer in self.materialLayers:
                layer.writeFbx(fp)
            for layer in self.textureLayers:
                layer.writeFbx(fp)

            fp.write(
                '        Layer: 0 {\n' +
                '            Version: 100\n')
            if self.normalLayers:
                self.writeLayerElement(fp, "LayerElementNormal")
            if self.uvLayers:
                self.writeLayerElement(fp, "LayerElementUV")
            if self.materialLayers:
                self.writeLayerElement(fp, "LayerElementMaterial")
            if self.textureLayers:
                self.writeLayerElement(fp, "LayerElementTexture")
            fp.write('        }\n')

        FbxObject.writeFooter(self, fp)         
        for node in self.shapeKeys.values():
            node.writeFbx(fp)
        for node in self.blendDeformers.values():
            node.writeFbx(fp)


    def writeLayerElement(self, fp, type):
        fp.write(
            '            LayerElement:  {\n' +
            '                Type: "%s"\n' % type +
            '                TypedIndex: 0\n' +
            '            }\n')
                

    def writeLinks(self, fp):
        FbxObject.writeLinks(self, fp)
        for node in self.shapeKeys.values():
            node.writeLinks(fp)
        for node in self.blendDeformers.values():        
            node.writeLinks(fp)
    
    
    def build(self, rna):
        for node in self.uvLayers:
            node.build(rna)
        for node in self.materialLayers:
            node.build(rna)
        for node in self.textureLayers:
            node.build(rna)                
        return rna


#------------------------------------------------------------------
#   Layers
#------------------------------------------------------------------


class DummyLayer():
    def __init__(self):
        self.name = "Dummy"

    
class FbxLayerElement(FbxStuff):
    def __init__(self, ftype):
        FbxStuff.__init__(self, ftype)
        self.index = 0
        self.setMulti([
            ("Version", 101),
            ("Name", None),
            ("MappingInformationType", "NoMappingInformation"),
            ("ReferenceInformationType", "Direct")
        ])


    def parse(self, pnode):
        self.index = pnode.values[0]
        return self.parseNodes(pnode.values[1:])
        
        
    def make(self, layer, index):
        self.index = index
        self.setMulti([
            ("Name", layer.name),
        ])
        

    def writeHeader(self, fp):
        fp.write('        %s: %d { \n' % (self.ftype, self.index))


    def build(self, me, layer):
        layer.name = self.get("Name")
        return
        
#------------------------------------------------------------------
#   Normal Layer
#------------------------------------------------------------------

class FbxLayerElementNormal(FbxLayerElement):

    def __init__(self):
        FbxLayerElement.__init__(self, 'LayerElementNormal')
        self.normals = CArray("Normals", float, 3)


    def parseNodes(self, pnodes):
        rest = []        
        for pnode in pnodes:
            if pnode.key == 'Normals':
                self.normals.parse(pnode)
            else:
                rest.append(pnode)
        return FbxLayerElement.parseNodes(self, rest)

        
    def make(self, layer, index, faces):
        FbxLayerElement.make(self, layer, index)
        self.setMulti([
            ("MappingInformationType", "ByPolygonVertex"),
            ("ReferenceInformationType", "Direct")
        ])
        if fbx.usingMakeHuman:
            normals = [f.normal for f in faces]
        else:
            normals = [b2f(f.normal) for f in faces for vn in f.vertices]
        self.normals.make(normals)
        return self
        
        
    def writeHeader(self, fp):
        FbxLayerElement.writeHeader(self, fp)
        self.normals.writeFbx(fp)


#------------------------------------------------------------------
#   UV Layer
#------------------------------------------------------------------

class FbxLayerElementUV(FbxLayerElement):

    def __init__(self):
        FbxLayerElement.__init__(self, 'LayerElementUV')
        self.vertices = CArray("UV", float, 2)
        self.faces = CArray("UVIndex", int, 1)


    def parseNodes(self, pnodes):
        rest = []        
        for pnode in pnodes:
            if pnode.key == 'UV':
                self.vertices.parse(pnode)
            elif pnode.key == 'UVIndex':
                self.faces.parse(pnode)
            else:
                rest.append(pnode)
        return FbxLayerElement.parseNodes(self, rest)

        
    def make(self, layer, index, faces):
        FbxLayerElement.make(self, layer, index)
        self.setMulti([
            ("MappingInformationType", "ByPolygonVertex"),
            ("ReferenceInformationType", "IndexToDirect")
        ])
        if fbx.usingMakeHuman:
            verts = layer.data
        else:
            verts = [list(data.uv) for data in layer.data]
        self.vertices.make(verts)
        self.faces.make(faces)
        return self
        
        
    def writeHeader(self, fp):
        FbxLayerElement.writeHeader(self, fp)
        self.vertices.writeFbx(fp)
        self.faces.writeFbx(fp)


    def build(self, me):
        uvtex = me.uv_textures.new()
        uvloop = me.uv_layers[-1]
        FbxLayerElement.build(self, me, uvtex)
        for fn,vn in enumerate(self.faces.values):            
            uvloop.data[fn].uv = self.vertices.values[vn]
        return


#------------------------------------------------------------------
#   Material Layer
#------------------------------------------------------------------

class FbxLayerElementMaterial(FbxLayerElement):

    def __init__(self):
        FbxLayerElement.__init__(self, 'LayerElementMaterial')
        self.materials = CArray("Materials", int, 1)
                
                
    def parseNodes(self, pnodes):        
        rest = []
        for pnode in pnodes:
            if pnode.key == 'Materials':
                self.materials.parse(pnode)
            else:
                rest.append(pnode)
        return FbxLayerElement.parseNodes(self, rest)
        
        
    def make(self, layer, index, mats, faces):
        FbxLayerElement.make(self, layer, index)
        if len(mats) == 1:
            self.setMulti([
                ("MappingInformationType", "AllSame"),
                ("ReferenceInformationType", "IndexToDirect")
            ])
            self.materials.make([0])
        else:
            self.setMulti([
                ("MappingInformationType", "ByPolygon"),
                ("ReferenceInformationType", "IndexToDirect")
            ])
            self.materials.make(faces)
        return self


    def writeHeader(self, fp):
        FbxLayerElement.writeHeader(self, fp)
        self.materials.writeFbx(fp)


    def build(self, me):
        pass
        #FbxLayerElement.build(self, me, layer)


#------------------------------------------------------------------
#   Texture Layer
#------------------------------------------------------------------

class FbxLayerElementTexture(FbxLayerElement):

    def __init__(self):
        FbxLayerElement.__init__(self, 'LayerElementTexture')
        self.setMulti([
            ("BlendMode", "Translucent"),
            ("TextureAlpha", 1.0)
        ])
        self.hastex = False


    def make(self, layer, index, hastex):
        self.hastex = hastex
        FbxLayerElement.make(self, layer, index)
        if hastex:
            self.setMulti([
                ("MappingInformationType", "ByPolygonVertex"),
                ("ReferenceInformationType", "IndexToDirect"),
            ])
        else:
            self.setMulti([
                ("MappingInformationType", "NoMappingInformation"),
                ("ReferenceInformationType", "IndexToDirect"),
                ("BlendMode", "Translucent"),
                ("TextureAlpha", 1.0)
            ])
        return self        


    def build(self, me):
        pass
        #FbxLayerElement.build(self, me, layer)
