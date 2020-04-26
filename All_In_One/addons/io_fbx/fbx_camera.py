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
#   Camera
#------------------------------------------------------------------

class FbxCamera(FbxNodeAttribute):
    propertyTemplate = (
"""    
        PropertyTemplate: "FbxCamera" {
            Properties70:  {
                P: "Color", "ColorRGB", "Color", "",0.8,0.8,0.8
                P: "Position", "Vector", "", "A",0,0,-50
                P: "UpVector", "Vector", "", "A",0,1,0
                P: "InterestPosition", "Vector", "", "A",0,0,0
                P: "Roll", "Roll", "", "A",0
                P: "OpticalCenterX", "OpticalCenterX", "", "A",0
                P: "OpticalCenterY", "OpticalCenterY", "", "A",0
                P: "BackgroundColor", "Color", "", "A",0.63,0.63,0.63
                P: "TurnTable", "Number", "", "A",0
                P: "DisplayTurnTableIcon", "bool", "", "",0
                P: "UseMotionBlur", "bool", "", "",0
                P: "UseRealTimeMotionBlur", "bool", "", "",1
                P: "Motion Blur Intensity", "Number", "", "A",1
                P: "AspectRatioMode", "enum", "", "",0
                P: "AspectWidth", "double", "Number", "",320
                P: "AspectHeight", "double", "Number", "",200
                P: "PixelAspectRatio", "double", "Number", "",1
                P: "FilmOffsetX", "Number", "", "A",0
                P: "FilmOffsetY", "Number", "", "A",0
                P: "FilmWidth", "double", "Number", "",0.816
                P: "FilmHeight", "double", "Number", "",0.612
                P: "FilmAspectRatio", "double", "Number", "",1.33333333333333
                P: "FilmSqueezeRatio", "double", "Number", "",1
                P: "FilmFormatIndex", "enum", "", "",0
                P: "PreScale", "Number", "", "A",1
                P: "FilmTranslateX", "Number", "", "A",0
                P: "FilmTranslateY", "Number", "", "A",0
                P: "FilmRollPivotX", "Number", "", "A",0
                P: "FilmRollPivotY", "Number", "", "A",0
                P: "FilmRollValue", "Number", "", "A",0
                P: "FilmRollOrder", "enum", "", "",0
                P: "ApertureMode", "enum", "", "",2
                P: "GateFit", "enum", "", "",0
                P: "FieldOfView", "FieldOfView", "", "A",25.1149997711182
                P: "FieldOfViewX", "FieldOfViewX", "", "A",40
                P: "FieldOfViewY", "FieldOfViewY", "", "A",40
                P: "FocalLength", "Number", "", "A",34.8932762167263
                P: "CameraFormat", "enum", "", "",0
                P: "UseFrameColor", "bool", "", "",0
                P: "FrameColor", "ColorRGB", "Color", "",0.3,0.3,0.3
                P: "ShowName", "bool", "", "",1
                P: "ShowInfoOnMoving", "bool", "", "",1
                P: "ShowGrid", "bool", "", "",1
                P: "ShowOpticalCenter", "bool", "", "",0
                P: "ShowAzimut", "bool", "", "",1
                P: "ShowTimeCode", "bool", "", "",0
                P: "ShowAudio", "bool", "", "",0
                P: "AudioColor", "Vector3D", "Vector", "",0,1,0
                P: "NearPlane", "double", "Number", "",10
                P: "FarPlane", "double", "Number", "",4000
                P: "AutoComputeClipPanes", "bool", "", "",0
                P: "ViewCameraToLookAt", "bool", "", "",1
                P: "ViewFrustumNearFarPlane", "bool", "", "",0
                P: "ViewFrustumBackPlaneMode", "enum", "", "",2
                P: "BackPlaneDistance", "Number", "", "A",4000
                P: "BackPlaneDistanceMode", "enum", "", "",1
                P: "ViewFrustumFrontPlaneMode", "enum", "", "",2
                P: "FrontPlaneDistance", "Number", "", "A",10
                P: "FrontPlaneDistanceMode", "enum", "", "",1
                P: "LockMode", "bool", "", "",0
                P: "LockInterestNavigation", "bool", "", "",0
                P: "BackPlateFitImage", "bool", "", "",0
                P: "BackPlateCrop", "bool", "", "",0
                P: "BackPlateCenter", "bool", "", "",1
                P: "BackPlateKeepRatio", "bool", "", "",1
                P: "BackgroundAlphaTreshold", "double", "Number", "",0.5
                P: "ShowBackplate", "bool", "", "",1
                P: "BackPlaneOffsetX", "Number", "", "A",0
                P: "BackPlaneOffsetY", "Number", "", "A",0
                P: "BackPlaneRotation", "Number", "", "A",0
                P: "BackPlaneScaleX", "Number", "", "A",1
                P: "BackPlaneScaleY", "Number", "", "A",1
                P: "Background Texture", "object", "", ""
                P: "FrontPlateFitImage", "bool", "", "",1
                P: "FrontPlateCrop", "bool", "", "",0
                P: "FrontPlateCenter", "bool", "", "",1
                P: "FrontPlateKeepRatio", "bool", "", "",1
                P: "Foreground Opacity", "double", "Number", "",1
                P: "ShowFrontplate", "bool", "", "",1
                P: "FrontPlaneOffsetX", "Number", "", "A",0
                P: "FrontPlaneOffsetY", "Number", "", "A",0
                P: "FrontPlaneRotation", "Number", "", "A",0
                P: "FrontPlaneScaleX", "Number", "", "A",1
                P: "FrontPlaneScaleY", "Number", "", "A",1
                P: "Foreground Texture", "object", "", ""
                P: "DisplaySafeArea", "bool", "", "",0
                P: "DisplaySafeAreaOnRender", "bool", "", "",0
                P: "SafeAreaDisplayStyle", "enum", "", "",1
                P: "SafeAreaAspectRatio", "double", "Number", "",1.33333333333333
                P: "Use2DMagnifierZoom", "bool", "", "",0
                P: "2D Magnifier Zoom", "Number", "", "A",100
                P: "2D Magnifier X", "Number", "", "A",50
                P: "2D Magnifier Y", "Number", "", "A",50
                P: "CameraProjectionType", "enum", "", "",0
                P: "OrthoZoom", "double", "Number", "",1
                P: "UseRealTimeDOFAndAA", "bool", "", "",0
                P: "UseDepthOfField", "bool", "", "",0
                P: "FocusSource", "enum", "", "",0
                P: "FocusAngle", "double", "Number", "",3.5
                P: "FocusDistance", "double", "Number", "",200
                P: "UseAntialiasing", "bool", "", "",0
                P: "AntialiasingIntensity", "double", "Number", "",0.77777
                P: "AntialiasingMethod", "enum", "", "",0
                P: "UseAccumulationBuffer", "bool", "", "",0
                P: "FrameSamplingCount", "int", "Integer", "",7
                P: "FrameSamplingType", "enum", "", "",1
            }
        }
""")

    def __init__(self):
        FbxNodeAttribute.__init__(self, "Camera", 'CAMERA', "Camera")
        self.template = self.parseTemplate('CameraAttribute', FbxCamera.propertyTemplate)
        self.isObjectData = True
        self.camera = None

    def make(self, ob):
        self.camera = ob.data
        
        self.setProps([
            ("InterestPosition", (0,0,-1)),
            ("AspectHeight", 180.0),
            ("FilmWidth", 1.088000136),
            ("FilmAspectRatio", 1.7777),
            ("ApertureMode", 1),
            ("FieldOfView", 49.13434),
            ("NearPlane", 0.1),
            ("FarPlane", 100),
            ("FocusDistance", 5),
        ])
        FbxNodeAttribute.make(self, ob.data)
        self.setMulti([
            ("Position", (0,0,-50)),
            ("Up", (0,1,0)),
            ("LookAt", (0,0,-1)),
            ("ShowInfoOnMoving", 1),
            ("ShowAudio", 0),
            ("AudioColor", (0,1,0)),
            ("CameraOrthoZoom", 1),
        ])
        

    def build3(self):
        cam = fbx.data[self.id]
        return cam

#------------------------------------------------------------------
#   Camera Switcher
#------------------------------------------------------------------

class FbxCameraSwitcher(FbxNodeAttribute):
    propertyTemplate = (
"""    
        PropertyTemplate: "FbxCameraSwitcher" {
            Properties70:  {
                P: "Camera Index", "Integer", "", "A",0
            }
        }
""")

    def __init__(self):
        FbxNodeAttribute.__init__(self, "CameraSwitcher", "CameraSwitcher", 'EMPTY')
        self.template = self.parseTemplate('NodeAttribute', FbxCameraSwitcher.propertyTemplate)


    def make(self, ob):
        self.setProps([
            ("Camera Index", 0),
        ])
        FbxNodeAttribute.make(self, ob.data)
        self.setMulti([
        ])
  
  
class FbxCameraSwitcher(CModel):
    propertyTemplate = (
"""    
        PropertyTemplate: "FbxCameraSwitcher" {
		Properties70:  {
			P: "ScalingMin", "Vector3D", "Vector", "",1,1,1
			P: "Show", "bool", "", "",0
			P: "DefaultAttributeIndex", "int", "Integer", "",0
			P: "Visibility Inheritance", "Visibility Inheritance", "", "",0
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
        CModel.__init__(self, "CameraSwitcher", "CameraSwitcher", 'EMPTY')
        self.template = self.parseTemplate('Model', FbxCameraSwitcher.propertyTemplate)


    def make(self, ob):
        self.setProps([
        ])
        FbxNodeAttribute.make(self, ob.data)
        self.setMulti([
		("Version", 232),
		("Shading", W),
		("Culling", "CullingOff"),
        ])
  
 