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
        
#------------------------------------------------------------------
#   Texture
#------------------------------------------------------------------

class FbxFileTexture(FbxObject):
    propertyTemplate = ( 
"""
        PropertyTemplate: "FbxFileTexture" {
            Properties70:  {
                P: "TextureTypeUse", "enum", "", "",0
                P: "Texture alpha", "Number", "", "A",1
                P: "CurrentMappingType", "enum", "", "",0
                P: "WrapModeU", "enum", "", "",0
                P: "WrapModeV", "enum", "", "",0
                P: "UVSwap", "bool", "", "",0
                P: "PremultiplyAlpha", "bool", "", "",1
                P: "Translation", "Vector", "", "A",0,0,0
                P: "Rotation", "Vector", "", "A",0,0,0
                P: "Scaling", "Vector", "", "A",1,1,1
                P: "TextureRotationPivot", "Vector3D", "Vector", "",0,0,0
                P: "TextureScalingPivot", "Vector3D", "Vector", "",0,0,0
                P: "CurrentTextureBlendMode", "enum", "", "",1
                P: "UVSet", "KString", "", "", "default"
                P: "UseMaterial", "bool", "", "",0
                P: "UseMipMap", "bool", "", "",0
            }
        }
""")

    def __init__(self, subtype=''):
        FbxObject.__init__(self, 'Texture', subtype, 'TEXTURE')        
        self.template = self.parseTemplate('Texture', FbxFileTexture.propertyTemplate)
        self.isModel = True 
        self.image = None

    """    
    def parseNodes(self, pnodes):
        rest = []
        for pnode in pnodes:
            if pnode.key == 'Media':
                self.image = nodeFromName(pnode.values[0])
            else:
                rest.append(pnode)
        return  FbxObject.parseNodes(self, rest)     
    """

    def make(self, tex):
        FbxObject.make(self, tex)
        img = tex.image
        if img:
            self.image = fbx.nodes.images[img.name].make(img)
            fbx.nodes.images[img.name].makeOOLink(self)
            
        self.setMulti([
            ("Type", "TextureVideoClip"),
            ("Version", 202),          
            ("TextureName", "Texture::%s" % self.name),
            ("Media", "Video::%s" % self.image.name),
            ("Filename", self.image.get("Filename")),           
            ("RelativeFilename", self.image.get("RelativeFilename")),
            ("ModelUVTranslation", (0,0)),           
            ("ModelUVScaling", (1,1)),
            ("Texture_Alpha_Source", "None"),       
            ("Cropping", (0,0)),
        ])
        

    def writeHeader(self, fp):   
        FbxObject.writeHeader(self, fp)            


    def build2(self):
        tex = fbx.data[self.id]
        
        type = self.get("Type")
        texname = self.get("TextureName")
        imgname = nameName(self.get("Media"))
        filename = self.get("Filename")
        relativeFilename = self.get("RelativeFilename")
        _ = self.get("ModelUVTranslation")
        _ = self.get("ModelUVScaling")
        _ = self.get("Texture_Alpha_Source")
        cropping = self.get("Cropping")
        
        links = self.getBChildLinks('IMAGE')
        for link in links:
            node = link.child
            if node.name == imgname:
                tex.image = fbx.data[node.id]

        return self


