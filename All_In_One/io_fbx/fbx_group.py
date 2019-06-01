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
#   Group
#------------------------------------------------------------------

class CGroup(CModel):
    propertyTemplate = (
""" 
        PropertyTemplate: "FbxGroup" {
            Properties70:  {
                P: "RotationActive", "bool", "", "",1
                P: "InheritType", "enum", "", "",1
                P: "ScalingMax", "Vector3D", "Vector", "",0,0,0
                P: "DefaultAttributeIndex", "int", "Integer", "",0
                P: "MultiTake", "int", "Integer", "",1
                P: "ManipulationMode", "enum", "", "",0
                P: "ScalingPivotUpdateOffset", "Vector3D", "Vector", "",0,0,0
                P: "SetPreferedAngle", "Action", "", "",0
                P: "PivotsVisibility", "enum", "", "",1
                P: "RotationLimitsVisibility", "bool", "", "",0
                P: "LocalTranslationRefVisibility", "bool", "", "",0
                P: "RotationRefVisibility", "bool", "", "",0
                P: "RotationAxisVisibility", "bool", "", "",0
                P: "ScalingRefVisibility", "bool", "", "",0
                P: "HierarchicalCenterVisibility", "bool", "", "",0
                P: "GeometricCenterVisibility", "bool", "", "",0
                P: "ReferentialSize", "double", "Number", "",12
                P: "DefaultKeyingGroup", "int", "Integer", "",0
                P: "DefaultKeyingGroupEnum", "enum", "", "",0
                P: "Pickable", "bool", "", "",1
                P: "Transformable", "bool", "", "",1
                P: "CullingMode", "enum", "", "",0
                P: "ShowTrajectories", "bool", "", "",0
            }
        }
""")    

    def __init__(self):
        CModel.__init__(self, "Group", "Group", 'GROUP')
        self.template = self.parseTemplate('Group', FbxCameraSwitcher.propertyTemplate)


    def make(self, grp):
        self.setProps([
        ])
        CModel.make(self, grp)
        self.setMulti([
            ("Shading", U),
            ("Culling", "CullingOff"),
        ])
  
 