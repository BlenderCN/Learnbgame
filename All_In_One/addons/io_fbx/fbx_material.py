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
#   Material
#------------------------------------------------------------------

class FbxSurfaceMaterial(FbxObject):
    propertyTemplates = {
        "Phong" : ( 
"""
        PropertyTemplate: "FbxSurfacePhong" {
            Properties70:  {
                P: "ShadingModel", "KString", "", "", "Phong"
                P: "MultiLayer", "bool", "", "",0
                P: "EmissiveColor", "Color", "", "A",0,0,0
                P: "EmissiveFactor", "Number", "", "A",1
                P: "AmbientColor", "Color", "", "A",0.2,0.2,0.2
                P: "AmbientFactor", "Number", "", "A",1
                P: "DiffuseColor", "Color", "", "A",0.8,0.8,0.8
                P: "DiffuseFactor", "Number", "", "A",1
                P: "Bump", "Vector3D", "Vector", "",0,0,0
                P: "NormalMap", "Vector3D", "Vector", "",0,0,0
                P: "BumpFactor", "double", "Number", "",1
                P: "TransparentColor", "Color", "", "A",0,0,0
                P: "TransparencyFactor", "Number", "", "A",0
                P: "DisplacementColor", "ColorRGB", "Color", "",0,0,0
                P: "DisplacementFactor", "double", "Number", "",1
                P: "VectorDisplacementColor", "ColorRGB", "Color", "",0,0,0
                P: "VectorDisplacementFactor", "double", "Number", "",1
                P: "SpecularColor", "Color", "", "A",0.2,0.2,0.2
                P: "SpecularFactor", "Number", "", "A",1
                P: "ShininessExponent", "Number", "", "A",20
                P: "ReflectionColor", "Color", "", "A",0,0,0
                P: "ReflectionFactor", "Number", "", "A",1
            }
        }
"""),

        "Lambert" : ( 
"""
        PropertyTemplate: "FbxSurfaceLambert" {
            Properties70:  {
                P: "ShadingModel", "KString", "", "", "Lambert"
                P: "MultiLayer", "bool", "", "",0
                P: "EmissiveColor", "Color", "", "A",0,0,0
                P: "EmissiveFactor", "Number", "", "A",1
                P: "AmbientColor", "Color", "", "A",0.2,0.2,0.2
                P: "AmbientFactor", "Number", "", "A",1
                P: "DiffuseColor", "Color", "", "A",0.8,0.8,0.8
                P: "DiffuseFactor", "Number", "", "A",1
                P: "Bump", "Vector3D", "Vector", "",0,0,0
                P: "NormalMap", "Vector3D", "Vector", "",0,0,0
                P: "BumpFactor", "double", "Number", "",1
                P: "TransparentColor", "Color", "", "A",0,0,0
                P: "TransparencyFactor", "Number", "", "A",0
                P: "DisplacementColor", "ColorRGB", "Color", "",0,0,0
                P: "DisplacementFactor", "double", "Number", "",1
                P: "VectorDisplacementColor", "ColorRGB", "Color", "",0,0,0
                P: "VectorDisplacementFactor", "double", "Number", "",1
            }
        }
"""),
    }
    
    propertyTemplate = propertyTemplates["Phong"]
    
    FbxShaders = {
        'LAMBERT' : 'Phong',
        'OREN_NAYAR' : 'Phong',
        'TOON' : 'Phong',
        'MINNAERT' : 'Phong',
        'FRESNEL' : 'Phong',      
    }
    
    BlenderShaders = {
        'Phong' : 'LAMBERT',
        'Lambert' : 'LAMBERT',
    }

    def __init__(self, subtype=''):
        FbxObject.__init__(self, 'Material', subtype, 'MATERIAL')        
        self.isModel = True        
        self.textures = []
        self.shader = "Lambert"


    def make(self, mat):
        FbxObject.make(self, mat)        
        self.shader = FbxSurfaceMaterial.FbxShaders[mat.diffuse_shader]
        self.propertyTemplate = FbxSurfaceMaterial.propertyTemplates[self.shader]
        self.template = self.parseTemplate('Material', self.propertyTemplate)   
        #print(self.shader)
        #print(self.template)
        
        for mtex in mat.texture_slots:
            if mtex:
                tex = mtex.texture
                if tex.type == 'NONE':
                    continue
                node = fbx.nodes.textures[tex.name]
                if tex.type == 'IMAGE':
                    channels = [
                        (mtex.use_map_diffuse, "DiffuseIntensity"),
                        (mtex.use_map_color_diffuse, "DiffuseColor"),
                        (mtex.use_map_alpha, "TransparencyFactor"),
                        (mtex.use_map_translucency, "Translucency"),

                        (mtex.use_map_specular, "SpecularFactor"),
                        (mtex.use_map_color_spec, "SpecularColor"),
                        (mtex.use_map_hardness, "ShininessExponent"),

                        (mtex.use_map_ambient, "Ambient"),
                        (mtex.use_map_emit, "Emit"),
                        (mtex.use_map_mirror, "Mirror"),
                        (mtex.use_map_raymir, "Ray Mirror"),

                        (mtex.use_map_normal, "Normal"),
                        (mtex.use_map_warp, "Warp"),
                        (mtex.use_map_displacement, "Displacement"),

                    ]
                    for use,ftype in channels:
                        if use:     
                            node.makeOPLink(self, ftype)

        self.setProps([
            ("ShadingModel", self.shader),
            ("MultiLayer", 0),

            ("DiffuseFactor", mat.diffuse_intensity),
            ("DiffuseColor", mat.diffuse_color),

            ("SpecularColor", mat.specular_color),
            ("SpecularFactor", mat.specular_intensity),
            ("ShininessExponent", mat.specular_hardness),
            ("TransparencyFactor", mat.alpha),
        ])
    
    
    def build3(self):
        mat = fbx.data[self.id]
        try:
            self.shader = self.get("ShadingModel")
        except KeyError:
            self.shader = "Phong"
        self.shader = self.shader.capitalize()
        mat.diffuse_shader = FbxSurfaceMaterial.BlenderShaders[self.shader]
        self.propertyTemplate = FbxSurfaceMaterial.propertyTemplates[self.shader]
        self.template = self.parseTemplate('Material', self.propertyTemplate)                
        
        mat.diffuse_intensity = 1
        mat.specular_intensity = 1

        if self.properties:
            mat.diffuse_color = self.getProp(["DiffuseColor","Diffuse"])
            mat.diffuse_intensity = self.getProp("DiffuseFactor")
            mat.alpha = self.getProp(["Opacity", "TransparencyFactor"])
            if self.shader == "Phong":
            	mat.specular_color = self.getProp(["SpecularColor","Specular"])
            	mat.specular_intensity = self.getProp("SpecularFactor")
            	mat.specular_hardness = self.getProp("ShininessExponent")

        links = self.getBChildLinks('TEXTURE')
        for link in links:
            tex = fbx.data[link.child.id]
            channel = link.channel
            mtex = mat.texture_slots.add()
            mtex.texture = tex
            mtex.texture_coords = 'UV'

            if channel in ["DiffuseIntensity", "DiffuseFactor"]:
                mtex.use_map_diffuse = True
            elif channel in ["Opacity", "TransparencyFactor"]:
                mtex.use_map_alpha = True
            elif channel == "Translucency":
                mtex.use_map_translucency = True

            elif channel in ["SpecularIntensity", "SpecularFactor"]:
                mtex.use_map_specular = True
            elif channel in ["SpecularColor","Specular"]:
                mtex.use_map_color_spec = True
            elif channel == "ShininessExponent":
                mtex.use_map_hardness = True
            
            elif channel == "Ambient":
                mtex.use_map_ambient= True
            elif channel == "Emit":
                mtex.use_map_emit = True
            elif channel == "Mirror":
                mtex.use_map_mirror = True
            elif channel == "Ray Mirror":
                mtex.use_map_raymir = True

            elif channel == "Normal":
                mtex.use_map_normal = True
                mtex.normal_map_space = 'TANGENT'
                if tex:
                    tex.use_normal_map = True
            elif channel == "Warp":
                mtex.use_map_warp = True
            elif channel == "Displacement":
                mtex.use_map_displacement = True
                
            if channel in ["DiffuseColor","Diffuse"]:
                mtex.use_map_color_diffuse = True
            else:
                mtex.use_map_color_diffuse = False

        return mat
