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
#   Lamp
#------------------------------------------------------------------

class FbxLight(FbxNodeAttribute):
    propertyTemplate = (
"""    
        PropertyTemplate: "FbxLight" {
            Properties70:  {
                P: "Color", "Color", "", "A",1,1,1
                P: "LightType", "enum", "", "",0
                P: "CastLightOnObject", "bool", "", "",1
                P: "DrawVolumetricLight", "bool", "", "",1
                P: "DrawGroundProjection", "bool", "", "",1
                P: "DrawFrontFacingVolumetricLight", "bool", "", "",0
                P: "Intensity", "Number", "", "A",100
                P: "InnerAngle", "Number", "", "A",0
                P: "OuterAngle", "Number", "", "A",45
                P: "Fog", "Number", "", "A",50
                P: "DecayType", "enum", "", "",0
                P: "DecayStart", "Number", "", "A",0
                P: "FileName", "KString", "", "", ""
                P: "EnableNearAttenuation", "bool", "", "",0
                P: "NearAttenuationStart", "Number", "", "A",0
                P: "NearAttenuationEnd", "Number", "", "A",0
                P: "EnableFarAttenuation", "bool", "", "",0
                P: "FarAttenuationStart", "Number", "", "A",0
                P: "FarAttenuationEnd", "Number", "", "A",0
                P: "CastShadows", "bool", "", "",0
                P: "ShadowColor", "Color", "", "A",0,0,0
                P: "AreaLightShape", "enum", "", "",0
                P: "LeftBarnDoor", "Float", "", "A",20
                P: "RightBarnDoor", "Float", "", "A",20
                P: "TopBarnDoor", "Float", "", "A",20
                P: "BottomBarnDoor", "Float", "", "A",20
                P: "EnableBarnDoor", "Bool", "", "A",0
            }
        }
""")        

    def __init__(self):
        FbxNodeAttribute.__init__(self, "Light", 'LAMP', "Light")
        self.template = self.parseTemplate('LampAttribute', FbxLight.propertyTemplate)
        self.isObjectData = True
        self.lamp = None
            

    def make(self, ob):
        self.lamp = ob.data
        
        FbxNodeAttribute.make(self, ob.data)
        self.setProps([
        ])
        self.setMulti([
            ("GeometryVersion", 124),
        ])
        

    def build3(self):
        lamp = fbx.data[self.id]
        return lamp
        

