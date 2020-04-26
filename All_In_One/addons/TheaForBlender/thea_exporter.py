"""
.. module:: thea_exporter
   :platform: OS X, Windows, Linux
   :synopsis: XML class definitions responsible for writting scene into xml format

.. moduleauthor:: Grzegorz Rakoczy <grzegorz.rakoczy@solidiris.com>


"""

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
import subprocess
import os
import sys
import time
import struct
from random import random
import platform
from math import *
from TheaForBlender.thea_render_main import *
from . import thea_globals
import mathutils
import re
import numpy as np

if os.name == "nt":
    try:
        import winreg
    except:
        print ("Can't access windows registry")



#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Begin of Basic Class Definitions
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#

class UVPair:
    def __init__(self, u=0, v=0):
        self.u = u
        self.v = v


class Point3D:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

class TriangleIndex:
    def __init__(self, i=0, j=0, k=0):
        self.i=i
        self.j=j
        self.k=k

class Transform:
    '''Transformation matrix
    '''
    def __init__(self,
                 r11=1, r12=0, r13=0,
                 r21=0, r22=1, r23=0,
                 r31=0, r32=0, r33=1,
                 tx=0, ty=0, tz=0):
        self.r11=r11
        self.r12=r12
        self.r13=r13
        self.r21=r21
        self.r22=r22
        self.r23=r23
        self.r31=r31
        self.r32=r32
        self.r33=r33
        self.tx=tx
        self.ty=ty
        self.tz=tz

    def write(self,file, identifier="Frame"):
        '''Write Transform parameter

            :param file: file handler
            :type file: file
            :param identifier: Parameter name, default: Frame
            :type identifier: string
        '''
        if thea_globals.sectionFrame:
#            translist = (self.r11, self.r12, self.r13, self.tx, self.r21, self.r22, self.r23, self.ty, self.r31, self.r32, self.r33, self.tz)
            translist = ('<Parameter Name=\"./Section #0/Frame\" Type=\"Transform\" Value="%s %s %s %s %s %s %s %s %s %s %s %s"/>\n' % (self.r11, self.r12, self.r13, self.tx, self.r21, self.r22, self.r23, self.ty, self.r31, self.r32, self.r33, self.tz))
            thea_globals.sectionFrameTrans = translist
#            thea_globals.log.debug("Translist: %s" % thea_globals.sectionFrameTrans)
#            for i in translist:
#                thea_globals.log.debug("Translist: %s" % i)
        file.write('<Parameter Name="%s" Type="Transform" Value="%s %s %s %s %s %s %s %s %s %s %s %s"/>\n' %\
        (identifier,
         self.r11, self.r12, self.r13, self.tx,
         self.r21, self.r22, self.r23, self.ty,
         self.r31, self.r32, self.r33, self.tz))

PointList = []
UVList = []
IndexList = []

class Node:
    '''Animation node contain time and transform
    '''
    def __init__(self, time, frame):
        '''
        :param time: node time
        :type time: float
        :param frame: node transform
        :type frame: Transform

        '''
        self.time = time
        self.frame = frame


class InterpolatedMotion:
    '''Motion animation
    '''
    def __init__(self, duration=0):
        '''
        :param duration: Duration of the animation in seconds
        :type duration: float
        '''
        self.identifier = "Target Position Modifier"
        self.enabled = False
        self.nodesList = []
        self.duration = duration

    def addNode(self, time, frame):
        '''Adds node to nodeList list

            :param time: node start time
            :type time: float
            :param frame: transform for the current node
            :type frame: Transform
        '''
        node = Node(time, frame)
        self.nodesList.append(node)

    def write(self,file, identifier="Target Position Modifier"):
        '''Write Transform parameter

            :param file: file handler
            :type file: file
            :param identifier: Parameter name, default: Target Position Modifier
            :type identifier: string
        '''

        if self.enabled:
            file.write('<Object Identifier=\"%s\" Label=\"Interpolated Motion\" Name=\"\" Type=\"Position Modifier\">\n' % self.identifier)
            file.write('<Parameter Name=\"Duration\" Type=\"Real\" Value=\"%s\"/>\n' % self.duration)
            #file.write('<Parameter Name=\"Interpolation\" Type=\"String\" Value=\"Spline\"/>\n')
            file.write('<Parameter Name=\"Interpolation\" Type=\"String\" Value=\"Linear\"/>\n')
            file.write('<Parameter Name=\"Closed\" Type=\"Boolean\" Value=\"0\"/>\n')
            file.write('<Parameter Name=\"Periodic\" Type=\"Boolean\" Value=\"0\"/>\n')
            #file.write('<Parameter Name=\"Pre Transform\" Type=\"Transform\" Value=\"1 0 0 0 0 1 0 0 0 0 1 0 \"/>\n')
            #file.write('<Parameter Name=\"Post Transform\" Type=\"Transform\" Value=\"1 0 0 0 0 1 0 0 0 0 1 0 \"/>\n')
            i=0
            for n in self.nodesList:
                nodeName="./Node%s" % i
                #file.write('<Parameter Name=\"%s/Time\" Type=\"Real\" Value=\"%s\"/>\n' % (nodeName, i))
                file.write('<Parameter Name=\"%s/Time\" Type=\"Real\" Value=\"%s\"/>\n' % (nodeName, n.time))
                n.frame.write(file, identifier="%s/Frame" % nodeName)
                #file.write('<Parameter Name=\"%s/Key\" Type=\"Integer\" Value=\"%s\"/>\n' % (nodeName, i))
                file.write('<Parameter Name=\"%s/Key\" Type=\"Integer\" Value=\"%s\"/>\n' % (nodeName, n.time))
                i+=1
            file.write('</Object>\n')





#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// End of Basic Class Definitions
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Begin of Custom Curve List
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class Reflection90CurveList:
    '''Reflection 90 Curve List

    '''
    def __init__(self, CustomCurve, CustomCurveList ):
        '''
        :param filename: List of custom curve
        :type filename: string
        '''

        self.CustomCurve = CustomCurve
        self.CustomCurveList = CustomCurveList
        thea_globals.log.debug("Curve items: %s - %s" % (self.CustomCurve, self.CustomCurveList))

    def write(self, file, CustomCurve, CustomCurveList):
        '''Write curve list

            :param file: file handler
            :type file: file
            :param identifier: string
            :type identifier: string
        '''
        file.write('<Parameter Name=\"Custom Curve\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.CustomCurve else '0'))
        if self.CustomCurve:
            file.write('<Parameter Name=\"Reflectance Curve\" Type=\"Fixed 2-Byte List\" Value=\"91\">\n')
    #        for F in range(0, 91):
    #        for F in range(0, len(self.CustomCurveList)):
    #        for F in eval(self.CustomCurveList):
            for F in self.CustomCurveList.strip('[]').split(','):
    #            file.write('<F x=\"4694\"/>\n')
                file.write('<F x=\"%s\"/>\n' % F)
            file.write('</Parameter>\n')

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// End of Custom Curve List
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Begin of Texture Definitions
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Rgb Texture
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


class RgbTexture:
    ''' RGB Texture definition
    '''
    def __init__(self, red=0, green=0, blue=0):
        '''
        :param red: Red component
        :type red: float
        :param green: Green component
        :type green: float
        :param blue: Blue component
        :type blue: float
        '''
        self.red = red
        self.green = green
        self.blue = blue

    def r(self):
        return self.red
    def g(self):
        return self.green
    def b(self):
        return self.blue

    def write(self, file, identifier):
        '''Write RGB Texture object

            :param file: file handler
            :type file: file
            :param identifier: name
            :type identifier: string
        '''
        file.write('<Object Identifier="./%s/Constant Texture" Label="Constant Texture" Name="" Type="Texture">\n' % identifier)
        file.write('<Parameter Name="Color" Type="RGB" Value="%s %s %s"/>\n' % (self.red, self.green, self.blue))
        file.write('</Object>\n')

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Bitmap Texture
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class BitmapTexture:
    '''Bitmap Texture

    '''
    def __init__(self, filename):
        '''
        :param filename: file name of the texture
        :type filename: string
        '''
        self.bitmapFilename = filename
        self.projection = "UV"
        self.cameraMapName = False
        self.offsetX = 0
        self.offsetY = 0
        self.scaleX = 1
        self.scaleY = 1
        self.spatialX = 1
        self.spatialY = 1
        self.rotation = 0
#        CHANGED > Added repeat function
        self.repeat = True
        self.invert = False
        self.brightness = 1.0
        self.contrast = 1.0
        self.saturation = 1.0
        self.red = 1.0
        self.green = 1.0
        self.blue = 1.0
        self.gamma = 1.0
        self.clampMin = 0.0
        self.clampMax = 1.0
        self.UVChannel = 0
        self.Channel = 'RGB'


    def getFilename(self):
        '''get texture filename

            :return: filename
            :rtype: string
        '''
        return self.bitmapFilename

    def write(self, file, identifier):
        '''Write Bitmap Texture object

            :param file: file handler
            :type file: file
            :param identifier: name
            :type identifier: string
        '''
#         #print("texture: ", self.bitmapFilename, self.clampMin, self.clampMax)
        file.write('<Object Identifier="./%s/Bitmap Texture" Label="Bitmap Texture" Name="" Type="Texture">\n' % identifier)
        file.write('<Parameter Name="Filename" Type="String" Value="%s"/>\n' % os.path.abspath(bpy.path.abspath(self.bitmapFilename)))
        ##print("filename: ", os.path.abspath(bpy.path.abspath(self.bitmapFilename)))
        file.write('<Parameter Name="Projection" Type="String" Value="%s"/>\n' % self.projection)
        file.write('<Parameter Name="Camera" Type="String" Value="%s"/>\n' % self.cameraMapName)
        file.write('<Parameter Name="Offset X" Type="Real" Value="%s"/>\n' % self.offsetX)
        file.write('<Parameter Name="Offset Y" Type="Real" Value="%s"/>\n' % self.offsetY)
        file.write('<Parameter Name="Spatial Scale X" Type="Real" Value="%s"/>\n' % self.spatialX)
        file.write('<Parameter Name="Spatial Scale Y" Type="Real" Value="%s"/>\n' % self.spatialY)
        file.write('<Parameter Name="UV Scale X" Type="Real" Value="%s"/>\n' % self.scaleX)
        file.write('<Parameter Name="UV Scale Y" Type="Real" Value="%s"/>\n' % self.scaleY)
        file.write('<Parameter Name="Rotation" Type="Real" Value="%s"/>\n' % self.rotation)
#        CHANGED > Added repeat function
        file.write('<Parameter Name="Repeat" Type="Boolean" Value="%s"/>\n'% ('1' if self.repeat else '0'))
        file.write('<Parameter Name="UV Channel" Type="Integer" Value="%s"/>\n' % self.UVChannel)
        file.write('<Parameter Name="Invert" Type="Boolean" Value="%s"/>\n'% ('1' if self.invert else '0'))
        file.write('<Parameter Name="Saturation" Type="Real" Value="%s"/>\n' % self.saturation)
        file.write('<Parameter Name="Brightness" Type="Real" Value="%s"/>\n' % self.brightness)
        file.write('<Parameter Name="Contrast" Type="Real" Value="%s"/>\n' % self.contrast)
        file.write('<Parameter Name="Gamma" Type="Real" Value="%s"/>\n' % self.gamma)
        file.write('<Parameter Name="Red" Type="Real" Value="%s"/>\n' % self.red)
        file.write('<Parameter Name="Green" Type="Real" Value="%s"/>\n' % self.green)
        file.write('<Parameter Name="Blue" Type="Real" Value="%s"/>\n' % self.blue)
        file.write('<Parameter Name="Clamp Min" Type="Real" Value="%s"/>\n' % (self.clampMin/100))
        file.write('<Parameter Name="Clamp Max" Type="Real" Value="%s"/>\n' % (self.clampMax/100))
        file.write('<Parameter Name="Channel" Type="String" Value="%s"/>\n' % (self.Channel))

        file.write('</Object>\n')

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Blackbody Texture
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class BlackbodyTexture:
    def __init__(self, temperature=6500.0):
        self.temperature=temperature

    def write(self, file, identifier):
        file.write('<Object Identifier="./%s/Black Body Texture" Label="Black Body Texture" Name="" Type="Texture>\n' % identifier)
        file.write('<Parameter Name="Temperature" Type="Real" Value="%s"/>\n' % self.temperature)
        file.write('</Object>\n')

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Monolithic Texture
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class ThTexture:
    def __init__(self, texture):
        self.texture = texture
    def getType(self):
        return self.texture.getType()

    def write(self, file, identifier):
        if self.texture:
            self.texture.write(file, identifier)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// End of Texture Definitions
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Glossy BSDF
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class GlossyBSDF:
    '''Glossy material component
    '''
    def __init__(self):
        self.absorptionColor = RgbTexture(1,1,1)
        self.absorptionDensity = 0.0
        self.roughness=0.1
        self.roughnessTr=0
        self.roughnessTrEnable=False
        self.anisotropy=0
        self.rotation=0
        self.bump=1.0
        self.ior=1.5
        self.iorFilenameEnable = False
        self.iorFilename = ""
        self.kappa=0.0
        self.abbe=50.0
        self.abbeEnable=False
        self.iorSource = "Constant"
        self.enableDispersion=False
        self.normalMapping=False
        self.traceReflections=True
        self.traceRefractions=True
        self.reflectanceTexture = False
        self.transmittanceTexture = False
        self.roughnessTexture = None
        self.roughnesstrTexture = None
        self.anisotropyTexture = None
        self.rotationTexture = None
        self.bumpTexture = None
        self.microRoughnessEnable = False
        self.microRoughnessWidth = 10
        self.microRoughnessHeight = 0.25
        self.customCurve = Reflection90CurveList(0,0)
#        self.CustomCurve = False
#        self.CustomCurveList = []

    def setReflectanceTexture(self, texture):
        self.reflectanceTexture = texture
    def setReflect90Texture(self, texture):
        self.reflect90Texture = texture

    def setTransmittanceTexture(self, texture):
        self.transmittanceTexture = texture
    def setRoughnessTexture(self, texture):
        self.roughnessTexture = texture
    def setRoughnessTrTexture(self, texture):
        self.roughnesstrTexture = texture
    def setAnisotropyTexture(self, texture):
        self.anisotropyTexture = texture
    def setRotationTexture(self, texture):
        self.rotationTexture = texture
    def setBumpTexture(self, texture):
        self.bumpTexture = texture

    def setRoughness(self, v):
        self.roughness = v
    def setRoughnessTr(self, v):
        self.roughnessTr = v
    def setRoughnessTrEnable(self, v):
        self.roughnessTrEnable = v
    def setAnisotropy(self, v):
         self.anisotropy = v
    def setRotation(self, v):
        self.rotation = v
    def setBump(self, v):
        self.bump = v
    def setIndexOfRefraction(self, v):
        self.ior = v
    def setExtinctionCoefficient(self, v):
        self.kappa = v
    def setAbbeNumber(self, v):
        self.abbe = v
    def setAbbeNumberEnable(self, v):
        self.abbeEnable = v
        self.enableDispersion = v
    def setDispersion(self, enable):
        self.enableDispersion = enable
    def setNormalMapping(self, enable):
        self.normalMapping = enable
    def setTraceReflections(self, enable):
        self.traceReflections = enable
    def setTraceRefractions(self, enable):
        self.traceRefractions = enable
    def setAbsorptionColor(self, texture):
        self.absorptionColor = texture
    def setAbsorptionDensity(self, v):
        self.absorptionDensity = v
    def setMicroRoughnessEnable(self, enable):
        self.microRoughnessEnable = enable
    def setMicroRoughnessWidth(self, v):
        self.microRoughnessWidth = v
    def setMicroRoughnessHeight(self, v):
        self.microRoughnessHeight = v
    def setcustomCurve(self, v):
        self.customCurve = v

    def write(self, file, identifier):
        '''Write Glossy material object

            :param file: file handler
            :type file: file
            :param identifier: name
            :type identifier: string
        '''
        file.write('<Object Identifier=\"./%s/Glossy Material\" Label=\"Glossy Material\" Name=\"\" Type=\"Material\">\n' % identifier)
        if self.reflectanceTexture:
            self.reflectanceTexture.write(file,"Reflectance 0")
#            RgbTexture(1,1,1).write(file,"Reflectance 90")
            self.reflect90Texture.write(file,"Reflectance 90")
        if self.transmittanceTexture:
            self.transmittanceTexture.write(file,"Transmittance")
        if self.roughnessTexture:
            self.roughnessTexture.write(file,"Roughness Map")
        if self.roughnesstrTexture:
            self.roughnesstrTexture.write(file,"Roughness Tr. Map")
        if self.anisotropyTexture:
            self.anisotropyTexture.write(file,"Anisotropy Map")
        if self.rotationTexture:
            self.rotationTexture.write(file,"Rotation Map")
        if self.bumpTexture:
            self.bumpTexture.write(file,"Bump Map")
        if (self.absorptionColor.r()!=0) and (self.absorptionColor.b()!=0) and (self.absorptionColor.g()!=0) and (self.absorptionDensity > 0):
            file.write('<Parameter Name="Absorption Color" Type="RGB" Value=\"%s %s %s\"/>\n' % (self.absorptionColor.r(),self.absorptionColor.g(),self.absorptionColor.b()))
            file.write('<Parameter Name=\"Absorption Density\" Type=\"Real\" Value=\"%s\"/>\n' % self.absorptionDensity)
        file.write('<Parameter Name=\"Roughness\" Type=\"Real\" Value=\"%s\"/>\n' % self.roughness)
        if self.roughnessTrEnable:
            file.write('<Parameter Name=\"Roughness Tr.\" Type=\"Real\" Value=\"%s\"/>\n' % self.roughnessTr)
        file.write('<Parameter Name=\"Anisotropy\" Type=\"Real\" Value=\"%s\"/>\n' % self.anisotropy)
        file.write('<Parameter Name=\"Rotation\" Type=\"Real\" Value=\"%s\"/>\n' % self.rotation)
        file.write('<Parameter Name=\"Index of Refraction\" Type=\"Real\" Value=\"%s\"/>\n' % self.ior)
        file.write('<Parameter Name=\"Extinction Coefficient\" Type=\"Real\" Value=\"%s\"/>\n' % self.kappa)
        if self.abbeEnable:
            file.write('<Parameter Name=\"Abbe Number\" Type=\"Real\" Value=\"%s\"/>\n' % self.abbe)
        file.write('<Parameter Name=\"Bump Strength\" Type=\"Real\" Value=\"%s\"/>\n' % self.bump)
        if self.iorFilenameEnable:
            file.write('<Parameter Name=\"IOR File\" Type=\"String\" Value=\"%s\"/>\n' % self.iorFilename)
        iorSource = "Constant"
        if self.enableDispersion:
            iorSource = "Abbe"
        elif self.iorFilenameEnable:
            iorSource = "Spectral"
        file.write('<Parameter Name=\"IOR Source\" Type=\"String\" Value=\"%s\"/>\n' % iorSource)
        file.write('<Parameter Name=\"Normal Mapping\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.normalMapping else '0'))
        file.write('<Parameter Name=\"Rough Tr.\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.roughnessTrEnable else '0'))
        file.write('<Parameter Name=\"Trace Reflections\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.traceReflections else '0'))
        file.write('<Parameter Name=\"Trace Refractions\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.traceRefractions else '0'))
        self.customCurve.write(file, 1, 2)
        file.write('<Parameter Name=\"./Micro Roughness/Enable\" Type=\"Boolean\" Value=\"%s\"/>\n'% ('1' if self.microRoughnessEnable else '0'))
        file.write('<Parameter Name=\"./Micro Roughness/Width (um)\" Type=\"Real\" Value=\"%s\"/>\n' % self.microRoughnessWidth)
        file.write('<Parameter Name=\"./Micro Roughness/Height (um)\" Type=\"Real\" Value=\"%s\"/>\n' % self.microRoughnessHeight)
        file.write('</Object>\n')

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// ThinFilm
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class ThinFilm:
    '''Thin Film material component
    '''
    def __init__(self):
        self.bump=1.0
        self.transmittanceTexture = None
        self.bumpTexture = None
        self.ior = 1.52
        self.normal = False
        self.thickness = 500
        self.interference = False
        self.thinThicknessTexture = None
        self.customCurve = Reflection90CurveList(0,0)

    def setTransmittanceTexture(self, texture):
        self.transmittanceTexture = texture
    def setBumpTexture(self, texture):
        self.bumpTexture = texture
    def setThickness(self, v):
        self.thickness = v
    def setInterference(self, v):
        self.interference = v
    def setThinThicknessTexture(self, texture):
        self.thinThicknessTexture = texture

    def getThinThicknessTexture(self):
        return self.thinThicknessTexture

    def setBump(self, v):
        self.bump = v
    def setNormalMapping(self, v):
        self.normalMapping = v
    def setIndexOfRefraction(self, v):
        self.ior = v

    def write(self, file, identifier):
        '''Write Glossy material object

            :param file: file handler
            :type file: file
            :param identifier: name
            :type identifier: string
        '''
        file.write('<Object Identifier=\"Thin Film Material\" Label=\"Thin Film Material\" Name=\"\" Type=\"Material\">\n')
        if self.transmittanceTexture:
            self.transmittanceTexture.write(file,"Transmittance")
        if self.bumpTexture:
            self.bumpTexture.write(file,"Bump Map")
        file.write('<Parameter Name=\"Index of Refraction\" Type=\"Real\" Value=\"%s\"/>\n' % self.ior)
        file.write('<Parameter Name=\"Thickness\" Type=\"Real\" Value=\"%s\"/>\n' % self.thickness)
        file.write('<Parameter Name=\"Interference\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.interference else '0'))
#       CHANGED > Addded thickness texture
        if self.thinThicknessTexture:
            self.thinThicknessTexture.write(file,"Thickness Map")
        file.write('<Parameter Name=\"Bump Strength\" Type=\"Real\" Value=\"%s\"/>\n' % self.bump)
        file.write('<Parameter Name=\"Normal Mapping\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.normalMapping else '0'))
        file.write('</Object>\n')

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Matte BSDF
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class MatteBSDF:
    '''Old basic material definition, not used anymore
    '''
    def __init__(self):
        self.roughness=0.0
        self.bump=1.0
        self.reflectanceTexture = None
        self.transmittanceTexture = None
        self.roughnessTexture = None
        self.bumpTexture = None

    def setReflectanceTexture(self, texture):
        self.reflectanceTexture = texture
    def setTransmittanceTexture(self, texture):
        self.transmittanceTexture = texture
    def setRoughnessTexture(self, texture):
        self.roughnessTexture = texture
    def setBumpTexture(self, texture):
        self.bumpTexture = texture

    def setRoughness(self, v):
        self.roughness = v
    def setBump(self, v):
        self.bump = v

    def write(self, file, identifier):
        file.write('<Object Identifier=\"./%s/Matte Material\" Label=\"Matte Material\" Name=\"\" Type=\"Material\">\n' % identifier)
        if self.reflectanceTexture:
            self.reflectanceTexture.write(file,"Reflectance")
        if self.transmittanceTexture:
            self.transmittanceTexture.write(file,"Transmittance");
        if self.roughnessTexture:
            self.roughnessTexture.write(file,"Roughness Map")
        if self.bumpTexture:
            self.bumpTexture.write(file,"Bump Map")
        file.write('<Parameter Name=\"Roughness\" Type=\"Real\" Value=\"%s\"/>\n' % self.roughness)
        file.write('<Parameter Name=\"Bump Strength\" Type=\"Real\" Value=\"%s\"/>\n' % self.bump)
        file.write('</Object>\n')

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Basic BSDF
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class BasicBSDF:
    '''Basic material component
    '''
    def __init__(self):
        self.absorptionColor = RgbTexture(1,1,1)
        self.absorptionDensity = 0.0
        self.sigma = 0.0
        self.roughness=0.1
        self.anisotropy = 0
        self.rotation = 0
        self.bump=1.0
        self.ior = 1.5
        self.kappa = 0.0
        self.normalMapping = False
        self.traceReflections = True
        self.diffuseTexture = False
        self.translucentTexture = False
        self.reflectanceTexture = False
        self.reflect90Texture = False
        self.sigmaTexture = False
        self.roughnessTexture = False
        self.anisotropyTexture = False
        self.rotationTexture = False
        self.bumpTexture = None
        self.microRoughnessEnable = False
        self.microRoughnessWidth = 10
        self.microRoughnessHeight = 0.25
        self.customCurve = Reflection90CurveList(0,0)
#        self.CustomCurve = False
#        self.CustomCurveList = []

    def setAbsorptionColor(self, texture):
        self.absorptionColor = texture
    def setAbsorptionDensity(self, v):
        self.absorptionDensity = v
    def setDiffuseTexture(self, texture):
        self.diffuseTexture = texture
    def setTranslucentTexture(self, texture):
        self.translucentTexture = texture
    def setReflectanceTexture(self, texture):
        self.reflectanceTexture = texture
    def setReflect90Texture(self, texture):
        self.reflect90Texture = texture
    def setSigmaTexture(self, texture):
        self.sigmaTexture = texture
    def setRoughnessTexture(self, texture):
        self.roughnessTexture = texture
    def setAnisotropyTexture(self, texture):
        self.anisotropyTexture = texture
    def setRotationTexture(self, texture):
        self.rotationTexture = texture
    def setBumpTexture(self, texture):
        self.bumpTexture = texture
    def setSigma(self, v):
        self.sigma = v
    def setRoughness(self, v):
        self.roughness = v
    def setAnisotropy(self, v):
        self.anisotropy = v
    def setRotation(self, v):
        self.rotation = v
    def setBump(self, v):
        self.bump = v
    def setIndexOfRefraction(self, v):
        self.ior = v
    def setExtinctionCoefficient(self, v):
        self.kappa = v
    def setNormalMapping(self, enable):
        self.normalMapping = enable
    def setTraceReflections(self, enable):
        self.traceReflections = enable
    def setMicroRoughnessEnable(self, enable):
        self.microRoughnessEnable = enable
    def setMicroRoughnessWidth(self, v):
        self.microRoughnessWidth = v
    def setMicroRoughnessHeight(self, v):
        self.microRoughnessHeight = v
    def setcustomCurve(self, v):
        self.customCurve = v
#    def setCustomCurve(self, v):
#        self.CustomCurve = v
#    def setCustomCurveList(self, v):
#        self.CustomCurveList = v

    def write(self, file, identifier):
        '''Write Basic material object

            :param file: file handler
            :type file: file
            :param identifier: name
            :type identifier: string
        '''
        file.write('<Object Identifier=\"./%s/Basic Material\" Label=\"Basic Material\" Name=\"\" Type=\"Material\">\n' % identifier)
        if self.diffuseTexture:
            self.diffuseTexture.write(file,"Diffuse")
        if self.translucentTexture:
            self.translucentTexture.write(file,"Translucent")
        if self.reflectanceTexture:
            self.reflectanceTexture.write(file,"Reflectance 0")
#            if (self.reflectanceTexture.red>0 or self.reflectanceTexture.green>0 or self.reflectanceTexture.blue>0):
#                refTex = RgbTexture(1,1,1)
            self.reflect90Texture.write(file,"Reflectance 90")
#                refTex.write(file,"Reflectance 90")
#             else:
#                 refTex = RgbTexture(0,0,0)
#                 refTex.write(file,"Reflectance 90")
        if self.sigmaTexture:
            self.sigmaTexture.write(file,"Sigma Map")
        if self.roughnessTexture:
            self.roughnessTexture.write(file,"Roughness Map")
        if self.anisotropyTexture:
            self.anisotropyTexture.write(file,"Anisotropy Map")
        if self.rotationTexture:
            self.rotationTexture.write(file,"Rotation Map")
        if self.bumpTexture:
            self.bumpTexture.write(file,"Bump Map")
        if (self.absorptionColor.r()!=0) and (self.absorptionColor.b()!=0) and (self.absorptionColor.g()!=0) and (self.absorptionDensity > 0):
            file.write('<Parameter Name="Absorption Color" Type="RGB" Value=\"%s %s %s\"/>\n' % (self.absorptionColor.r(),self.absorptionColor.g(),self.absorptionColor.b()))
            file.write('<Parameter Name=\"Absorption Density\" Type=\"Real\" Value=\"%s\"/>\n' % self.absorptionDensity)
        file.write('<Parameter Name=\"Sigma\" Type=\"Real\" Value=\"%s\"/>\n' % self.sigma)
        file.write('<Parameter Name=\"Roughness\" Type=\"Real\" Value=\"%s\"/>\n' % self.roughness)
        file.write('<Parameter Name=\"Anisotropy\" Type=\"Real\" Value=\"%s\"/>\n' % self.anisotropy)
        file.write('<Parameter Name=\"Rotation\" Type=\"Real\" Value=\"%s\"/>\n' % self.rotation)
        file.write('<Parameter Name=\"Index of Refraction\" Type=\"Real\" Value=\"%s\"/>\n' % self.ior)
        file.write('<Parameter Name=\"Extinction Coefficient\" Type=\"Real\" Value=\"%s\"/>\n' % self.kappa)
        file.write('<Parameter Name=\"Bump Strength\" Type=\"Real\" Value=\"%s\"/>\n' % self.bump)
        file.write('<Parameter Name=\"Normal Mapping\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.normalMapping else '0'))
        file.write('<Parameter Name=\"Trace Reflections\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.traceReflections else '0'))

        self.customCurve.write(file, 1, 2)
#        file.write('<Parameter Name=\"Custom Curve\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.CustomCurve else '0'))
#        if self.CustomCurve:
#            file.write('<Parameter Name=\"Reflectance Curve\" Type=\"Fixed 2-Byte List\" Value=\"91\">\n')
#            for F in self.CustomCurveList.strip('[]').split(','):
#                file.write('<F x=\"%s\"/>\n' % F)
#        file.write('</Parameter>\n')

        file.write('<Parameter Name=\"./Micro Roughness/Enable\" Type=\"Boolean\" Value=\"%s\"/>\n'% ('1' if self.microRoughnessEnable else '0'))
        file.write('<Parameter Name=\"./Micro Roughness/Width (um)\" Type=\"Real\" Value=\"%s\"/>\n' % self.microRoughnessWidth)
        file.write('<Parameter Name=\"./Micro Roughness/Height (um)\" Type=\"Real\" Value=\"%s\"/>\n' % self.microRoughnessHeight)
        file.write('</Object>\n')

class Medium:
    '''Medium
    '''
    def __init__(self):
        self.scatteringColor = None
        self.scatteringDensity = 1.0
        self.scatteringDensityTexture = None
        self.absorptionColor = None
        self.absorptionDensity = 1.0
        self.absorptionDensityTexture = None
        self.coefficientFilename = False
        self.phaseFunction = "Isotropic"
        self.asymetry = 0.0



    def write(self, file):
        '''Write medium object

            :param file: file handler
            :type file: file
        '''
        file.write('<Object Identifier=\"./Standard Medium\" Label=\"Standard Medium\" Name=\"Standard Medium\" Type=\"Medium\">\n')
        if self.scatteringColor:
            self.scatteringColor.write(file,"Scatter Color")
        if self.absorptionColor:
            self.absorptionColor.write(file,"Absorption Color")
        if self.scatteringDensityTexture:
            self.scatteringDensityTexture.write(file,"Scatter Density")
        if self.absorptionDensityTexture:
            self.absorptionDensityTexture.write(file,"Absorption Density")
#         if (self.absorptionColor.r()!=0) and (self.absorptionColor.b()!=0) and (self.absorptionColor.g()!=0) and (self.absorptionDensity > 0):
#             file.write('<Parameter Name="Absorption Color" Type="RGB" Value=\"%s %s %s\"/>\n' % (self.absorptionColor.r(),self.absorptionColor.g(),self.absorptionColor.b()))
        file.write('<Parameter Name=\"Absorption Coefficient\" Type=\"Real\" Value=\"%s\"/>\n' % self.absorptionDensity)
#         if (self.scatteringColor.r()!=0) and (self.scatteringColor.b()!=0) and (self.scatteringColor.g()!=0) and (self.scatteringDensity > 0):
#             file.write('<Parameter Name="Scattering Color" Type="RGB" Value=\"%s %s %s\"/>\n' % (self.scatteringColor.r(),self.scatteringColor.g(),self.scatteringColor.b()))
        file.write('<Parameter Name=\"Scatter Coefficient\" Type=\"Real\" Value=\"%s\"/>\n' % self.scatteringDensity)
        if self.coefficientFilename:
            file.write('<Parameter Name=\"Coefficient File\" Type=\"String\" Value=\"%s\"/>\n' % self.coefficientFilename)
            file.write('<Parameter Name=\"User Colors\" Type=\"Boolean\" Value=\"0\"/>\n')
        file.write('<Parameter Name=\"Phase Function\" Type=\"String\" Value=\"%s\"/>\n' % self.phaseFunction)
        file.write('<Parameter Name=\"Asymmetry\" Type=\"String\" Value=\"%s\"/>\n' % self.asymetry)
        file.write('</Object>\n')

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Bidirectional Subsurface Scattering Distribution Function (BSSDF)
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class SSS:
    '''SSS material component
    '''
    def __init__(self):
        self.reflectanceTexture = None
        self.reflect90Texture = None
        self.roughnessTexture = None
        self.roughnesstrTexture = None
        self.anisotropyTexture = None
        self.rotationTexture = None
        self.bumpTexture = None
        self.scatteringColor = (1,1,1)
        self.scatteringDensity = 1000.0
        self.absorptionColor = (1,1,1)
        self.absorptionDensity = 100.0
        self.asymetry = 0.0
        self.roughness = 0.0
        self.roughnessTr = 10
        self.roughnessTrEnable=False
        self.anisotropy = 0
        self.rotation = 0
        self.bump = 1.0
        self.ior = 1.3
        self.normalMapping = False
        self.traceReflections = True
        self.traceRefractions = True
        self.microRoughnessEnable = False
        self.microRoughnessWidth = 10
        self.microRoughnessHeight = 0.25

        self.customCurve = Reflection90CurveList(0,0)

    def setReflectanceTexture(self, texture):
        self.reflectanceTexture = texture
    def setReflect90Texture(self, texture):
        self.reflect90Texture = texture
    def setRoughnessTexture(self, texture):
        self.roughnessTexture = texture
    def setRoughnessTrTexture(self, texture):
        self.roughnesstrTexture = texture
    def setAnisotropyTexture(self, texture):
        self.anisotropyTexture = texture
    def setRotationTexture(self, texture):
        self.rotationTexture = texture
    def setBumpTexture(self, texture):
        self.bumpTexture = texture

    def setRoughness(self, v):
        self.roughness = v
    def setRoughnessTr(self, v):
        self.roughnessTr = v
    def setRoughnessTrEnable(self, v):
        self.roughnessTrEnable = v
    def setAnisotropy(self, v):
         self.anisotropy = v
    def setRotation(self, v):
        self.rotation = v
    def setBump(self, v):
        self.bump = v
    def setIndexOfRefraction(self, v):
        self.ior = v
    def setAsymetry(self, v):
        self.asymetry = v
    def setExtinctionCoefficient(self, v):
        self.kappa = v

    def setNormalMapping(self, enable):
        self.normalMapping = enable
    def setTraceReflections(self, enable):
        self.traceReflections = enable
    def setTraceRefractions(self, enable):
        self.traceRefractions = enable

    def setAbsorptionColor(self, texture):
        self.absorptionColor = texture
    def setScatteringColor(self, texture):
        self.scatteringColor = texture
    def setAbsorptionDensity(self, v):
        self.absorptionDensity = v
    def setScatteringDensity(self, v):
        self.scatteringDensity = v
    def setMicroRoughnessEnable(self, enable):
        self.microRoughnessEnable = enable
    def setMicroRoughnessWidth(self, v):
        self.microRoughnessWidth = v
    def setMicroRoughnessHeight(self, v):
        self.microRoughnessHeight = v
    def setcustomCurve(self, v):
        self.customCurve = v


    def write(self, file, identifier):
        '''Write SSS material object

            :param file: file handler
            :type file: file
            :param identifier: name
            :type identifier: string
        '''
        #print("bsdf.absorptionColor: ", self.absorptionColor)
        file.write('<Object Identifier=\"./%s/SSS Material\" Label=\"SSS Material\" Name=\"\" Type=\"Material\">\n' % identifier)
        if self.reflectanceTexture:
            self.reflectanceTexture.write(file,"Reflectance")
#            RgbTexture(1,1,1).write(file,"Reflectance 90")
            self.reflect90Texture.write(file,"Reflectance 90")
        if self.roughnessTexture:
          self.roughnessTexture.write(file,"Roughness Map");
        if self.roughnesstrTexture:
          self.roughnesstrTexture.write(file,"Roughness Tr. Map");
        if self.anisotropyTexture:
            self.anisotropyTexture.write(file,"Anisotropy Map");
        if self.rotationTexture:
            self.rotationTexture.write(file,"Rotation Map");
        if self.bumpTexture:
            self.bumpTexture.write(file,"Bump Map");
        if (self.absorptionColor.r()!=0) and (self.absorptionColor.b()!=0) and (self.absorptionColor.g()!=0) and (self.absorptionDensity > 0):
            file.write('<Parameter Name="Absorption Color" Type="RGB" Value=\"%s %s %s\"/>\n' % (self.absorptionColor.r(),self.absorptionColor.g(),self.absorptionColor.b()))
            file.write('<Parameter Name=\"Absorption Density\" Type=\"Real\" Value=\"%s\"/>\n' % self.absorptionDensity)
        if (self.scatteringColor.r()!=0) and (self.scatteringColor.b()!=0) and (self.scatteringColor.g()!=0) and (self.scatteringDensity > 0):
            file.write('<Parameter Name="Scattering Color" Type="RGB" Value=\"%s %s %s\"/>\n' % (self.scatteringColor.r(),self.scatteringColor.g(),self.scatteringColor.b()))
            file.write('<Parameter Name=\"Scattering Density\" Type=\"Real\" Value=\"%s\"/>\n' % self.scatteringDensity)
        file.write('<Parameter Name=\"Roughness\" Type=\"Real\" Value=\"%s\"/>\n' % self.roughness)
        file.write('<Parameter Name=\"Rough Tr.\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.roughnessTrEnable else '0'))
        if self.roughnessTrEnable:
            file.write('<Parameter Name=\"Roughness Tr.\" Type=\"Real\" Value=\"%s\"/>\n' % self.roughnessTr)
        file.write('<Parameter Name=\"Anisotropy\" Type=\"Real\" Value=\"%s\"/>\n' % self.anisotropy)
        file.write('<Parameter Name=\"Rotation\" Type=\"Real\" Value=\"%s\"/>\n' % self.rotation)
        file.write('<Parameter Name=\"Index of Refraction\" Type=\"Real\" Value=\"%s\"/>\n' % self.ior)
        file.write('<Parameter Name=\"Bump Strength\" Type=\"Real\" Value=\"%s\"/>\n' % self.bump)
        file.write('<Parameter Name=\"Absorption Density\" Type=\"Real\" Value=\"%s\"/>\n' % self.absorptionDensity)
        file.write('<Parameter Name=\"Scattering Density\" Type=\"Real\" Value=\"%s\"/>\n' % self.scatteringDensity)
        file.write('<Parameter Name=\"Asymmetry\" Type=\"Real\" Value=\"%s\"/>\n' % self.asymetry)
        file.write('<Parameter Name=\"Normal Mapping\" Type=\"Boolean\" Value=\"%s\"/>\n' % self.normalMapping)
        file.write('<Parameter Name=\"Trace Reflections\" Type=\"Boolean\" Value=\"%s\"/>\n' % self.traceReflections)
        file.write('<Parameter Name=\"Trace Refractions\" Type=\"Boolean\" Value=\"%s\"/>\n' % self.traceRefractions)
        self.customCurve.write(file, 1, 2)
        file.write('<Parameter Name=\"./Micro Roughness/Enable\" Type=\"Boolean\" Value=\"%s\"/>\n'% ('1' if self.microRoughnessEnable else '0'))
        file.write('<Parameter Name=\"./Micro Roughness/Width (um)\" Type=\"Real\" Value=\"%s\"/>\n' % self.microRoughnessWidth)
        file.write('<Parameter Name=\"./Micro Roughness/Height (um)\" Type=\"Real\" Value=\"%s\"/>\n' % self.microRoughnessHeight)
        file.write('</Object>\n')

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Translucent BSDF
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class TranslucentBSDF:
    '''Translucent material component
    '''
    def __init__(self):
        self.bump=1.0
        self.reflectanceTexture = None
        self.bumpTexture = None

    def setReflectanceTexture(self, texture):
        self.reflectanceTexture = texture
    def setBumpTexture(self, texture):
        self.bumpTexture = texture

    def setBump(self, v):
        self.bump = v

    def write(self, file, identifier):
        '''Write Translucent material object

            :param file: file handler
            :type file: file
            :param identifier: name
            :type identifier: string
        '''
        file.write('<Object Identifier=\"./%s/Translucent Material\" Label=\"Translucent Material\" Name=\"\" Type=\"Material\">\n' % identifier)
        if self.reflectanceTexture:
            self.reflectanceTexture.write(file,"Reflectance")
        if self.bumpTexture:
            self.bumpTexture.write(file,"Bump Map")
        file.write('<Parameter Name=\"Bump Strength\" Type=\"Real\" Value=\"%s\"/>\n' % self.bump)
        file.write('</Object>\n')

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Glass BSDF
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class GlassBSDF:
    '''Old glass material component. Not used anymore
    '''
    def __init__(self):
        self.reflectanceTexture = None

    def setReflectanceTexture(self, texture):
        self.reflectanceTexture = texture


    def write(self, file, identifier):
        file.write('<Object Identifier=\"./%s/Thin Glass Material\" Label=\"Thin Glass Material\" Name=\"\" Type=\"Material\">\n' % identifier)
        if self.reflectanceTexture:
            self.reflectanceTexture.write(file,"Reflectance")
        file.write('</Object>\n')

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Coating BSDF
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class CoatingBSDF:
    '''Coating material component
    '''
    def __init__(self):
        self.roughness=0.1
        self.anisotropy=0
        self.rotation=0
        self.bump=1.0
        self.ior=1.5
        self.kappa=0.0
        self.thickness=100.0
        self.thicknessEnable=False
        self.thicknessTexture = None
#        CHANGED > Added Thickness absorption color
        self.absorptionEnable=False
        self.thicknessAbsorptionTexture = None
        self.normalMapping=False
        self.traceReflections=True
        self.reflectanceTexture = None
        self.reflect90Texture = None
        self.transmittanceTexture = None
        self.roughnessTexture = None
        self.anisotropyTexture = None
        self.rotationTexture = None
        self.bumpTexture = None
        self.weightTexture = None
        self.microRoughnessEnable = False
        self.microRoughnessWidth = 10
        self.microRoughnessHeight = 0.25
        self.customCurve = Reflection90CurveList(0,0)
#        self.CustomCurve = False
#        self.CustomCurveList = []

    def setReflectanceTexture(self, texture):
        self.reflectanceTexture = texture
    def setReflect90Texture(self, texture):
        self.reflect90Texture = texture
    def setWeightTexture(self, texture):
        self.weightTexture = texture
    def setThicknessTexture(self, texture):
        self.thicknessTexture = texture
#        CHANGED > Added Thickness absorption color
    def setThicknessAbsorptionTexture (self, texture):
        self.thicknessAbsorptionTexture = texture
#        thea_globals.log.debug("thicknessAbsorptionTexture: %s, %s" % (self.thicknessAbsorptionTexture, texture))

    def setTransmittanceTexture(self, texture):
        self.transmittanceTexture = texture
    def setRoughnessTexture(self, texture):
        self.roughnessTexture = texture
    def setAnisotropyTexture(self, texture):
        self.anisotropyTexture = texture
    def setRotationTexture(self, texture):
        self.rotationTexture = texture
    def setBumpTexture(self, texture):
        self.bumpTexture = texture
    def setThickness(self, v):
        self.thickness = v
    def setThicknessEnable(self, v):
        self.thicknessEnable = v
#CHANGED > Added enable function, default should be empty not black
    def setAbsorptionEnable(self, v):
        self.absorptionEnable = v
    def setRoughness(self, v):
        self.roughness = v
    def setAnisotropy(self, v):
        self.anisotropy = v
    def setRotation(self, v):
        self.rotation = v
    def setBump(self, v):
        self.bump = v
    def setIndexOfRefraction(self, v):
        self.ior = v
    def setExtinctionCoefficient(self, v):
        self.kappa = v
    def setNormalMapping(self, enable):
        self.normalMapping = enable
    def setTraceReflections(self, enable):
        self.traceReflections = enable
    def setMicroRoughnessEnable(self, enable):
        self.microRoughnessEnable = enable
    def setMicroRoughnessWidth(self, v):
        self.microRoughnessWidth = v
    def setMicroRoughnessHeight(self, v):
        self.microRoughnessHeight = v
    def setcustomCurve(self, v):
        self.customCurve = v


    def getWeightTexture(self):
        return self.weightTexture

    def write(self, file, identifier):
        '''Write Coating material object

            :param file: file handler
            :type file: file
            :param identifier: name
            :type identifier: string
        '''
        file.write('<Object Identifier=\"./%s/Glossy Coating Material\" Label=\"Glossy Coating Material\" Name=\"\" Type=\"Material\">\n' % identifier)
#         if self.weightTexture:
#             self.weightTexture.write(file,"Weight Map #0")
        if self.reflectanceTexture:
            self.reflectanceTexture.write(file,"Reflectance 0")
            self.reflect90Texture.write(file,"Reflectance 90")
        if self.thicknessTexture:
            self.thicknessTexture.write(file,"Thickness Map")
#        CHANGED > Added Thickness absorption color
#        thea_globals.log.debug("Check abs col enable: %s" % self.absorptionEnable)
        if self.thicknessAbsorptionTexture and self.absorptionEnable == 1:
            self.thicknessAbsorptionTexture.write(file,"Absorption Map")
            thea_globals.log.debug("thicknessAbsorptionTexture: %s" % self.thicknessAbsorptionTexture)
        if self.roughnessTexture:
            self.roughnessTexture.write(file,"Roughness Map")
        if self.anisotropyTexture:
            self.anisotropyTexture.write(file,"Anisotropy Map")
        if self.rotationTexture:
            self.rotationTexture.write(file,"Rotation Map")
        if self.bumpTexture:
            self.bumpTexture.write(file,"Bump Map")
        file.write('<Parameter Name=\"Roughness\" Type=\"Real\" Value=\"%s\"/>\n' % self.roughness)
        file.write('<Parameter Name=\"Coating Absorption\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.thicknessEnable else '0'))
        file.write('<Parameter Name=\"Thickness\" Type=\"Real\" Value=\"%s\"/>\n' % self.thickness)
        file.write('<Parameter Name=\"Anisotropy\" Type=\"Real\" Value=\"%s\"/>\n' % self.anisotropy)
        file.write('<Parameter Name=\"Rotation\" Type=\"Real\" Value=\"%s\"/>\n' % self.rotation)
        file.write('<Parameter Name=\"Index of Refraction\" Type=\"Real\" Value=\"%s\"/>\n' % self.ior)
        file.write('<Parameter Name=\"Extinction Coefficient\" Type=\"Real\" Value=\"%s\"/>\n' % self.kappa)
        file.write('<Parameter Name=\"Bump Strength\" Type=\"Real\" Value=\"%s\"/>\n' % self.bump)
        file.write('<Parameter Name=\"Normal Mapping\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.normalMapping else '0'))
        file.write('<Parameter Name=\"Trace Reflections\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.traceReflections else '0'))
        self.customCurve.write(file, 1, 2)
        file.write('<Parameter Name=\"./Micro Roughness/Enable\" Type=\"Boolean\" Value=\"%s\"/>\n'% ('1' if self.microRoughnessEnable else '0'))
        file.write('<Parameter Name=\"./Micro Roughness/Width (um)\" Type=\"Real\" Value=\"%s\"/>\n' % self.microRoughnessWidth)
        file.write('<Parameter Name=\"./Micro Roughness/Height (um)\" Type=\"Real\" Value=\"%s\"/>\n' % self.microRoughnessHeight)
        file.write('</Object>\n')

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Monolithic Substrate BSDF
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class BSDF:
    '''old BSDF material. Not used anymore
    '''
    def __init__(self, type):
        self.type = type
    def getType(self):
        return self.type.getType()

    def write(self, file, identifier):
        if self.type:
            self.type.write(file, identifier)


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Layered Coating - to be used by Layered BSDF
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class LayeredCoating:
    '''Layered Coating - to be used by Layered BSDF
    '''
    def __init__(self, coating, w=1, th=1):
        '''
        :param coating: Coating
        :type coating: CoatingBSDF
        :param w: Weight
        :type w: float
        :param th: Thickness
        :type th: float
        '''
        self.coating = coating
        self.weight = w
        self.thickness = th
        self.thicknessTexture = None
        self.weightTexture = None
##        CHANGED > Added Thickness absorption color
#        self.thicknessAbsorptionTexture = None

    def setWeightTexture(self, texture):
        self.weightTexture = texture
        self.coating.setWeightTexture(texture)
    def setThicknessTexture(self, texture):
        self.thicknessTexture = texture
##        CHANGED > Added Thickness absorption color
    def setThicknessAbsorptionTexture (self, texture):
        self.thicknessAbsorptionTexture = texture
    def getCoatingWeightTexture(self):
        return self.weightTexture
    def getThicknessTexture(self):
        return self.thicknessTexture
    def getThicknessAbsorptionTexture(self):
        return self.thicknessAbsorptionTexture
    def getWeight(self):
        return self.weight

    def write(self, file, identifier):
        '''Write Layered coating material object

            :param file: file handler
            :type file: file
            :param identifier: name
            :type identifier: string
        '''
        if self.coating:
            self.coating.write(file, identifier)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Layered Substrate - to be used by Layered BSDF
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class LayeredSubstrate:
    '''Layered Substrate - to be used by Layered BSDF
    '''
    def __init__(self, substrate, w=1, wTex=None):
        '''
        :param substrate: Substrate
        :type substrate: material component
        :param w: weight
        :type w: float
        :param wTex: weight Texture
        :type wTex: BitmapTexture
        '''
        self.substrate = substrate
        self.weight = w
        self.weightTexture=wTex
        self.order = 0

    def setWeightTexture(self, texture):
        self.weightTexture = texture
    def getWeightTexture(self):
        return self.weightTexture
    def getWeight(self):
        return self.weight

    def write(self, file, identifier):
        '''Write Layered substrate material object

            :param file: file handler
            :type file: file
            :param identifier: name
            :type identifier: string
        '''
        if self.substrate:
            self.substrate.write(file, identifier)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Layered BSDF
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class LayeredBSDF:
    '''LayeredBSDF material
    '''
    #def __init__(self, substrate):
    def __init__(self):
        self.coatings = []
        self.substrates = []
        #self.addSubstrate(substrate)
        self.name = random()
    def addCoating(self, coating):
        self.coatings.append(coating)
    def addSubstrate(self, substrate):
        self.substrates.append(substrate)
    def getCoatings(self):
        return len(self.coatings)
    def getSubstrates(self):
        return len(self.substrates)

    def write(self, file):
        '''Write Layered BSDF material object

            :param file: file handler
            :type file: file
        '''
        file.write('<Object Identifier=\"Physically Layered Material\" Label=\"Physically Layered Material\" Name=\"\" Type=\"Material\">\n')
        # write coating objects.
        k=0
        for coating in self.coatings:
            layerId = "Layer #"+str(k)
            coating.write(file, layerId)
            k+=1
        # write substrate objects.
        #k=0
        k=len(self.coatings)
        self.sortedSubstrates = sorted(self.substrates, key=lambda substrate: substrate.order)
        #for substrate in self.substrates:
        for substrate in self.sortedSubstrates:
            layerId = "Layer #"+str(k)
            substrate.write(file, layerId)
            k+=1
        # write textured thickness (for coatings only).
        k=0
        for coating in self.coatings:
            try:
                if coating.getThicknessTexture.getType():
                    layerId = "Thickness Map #"+str(k)
                    coating.getThicknessTexture().write(file,layerId)
            except:
                type = None
            k+=1
        # write textured absorption color/texture (for coatings only).
        k=0
        for coating in self.coatings:
            try:
                if coating.getThicknessAbsorptionTexture.getType():
                    layerId = "Absorption Map #"+str(k)
                    coating.getThicknessAbsorptionTexture().write(file,layerId)
            except:
                type = None
            k+=1
        # write textured weights for coatings.
        k=0
        for coating in self.coatings:
            try:
                if coating.getCoatingWeightTexture():
                    layerId = "Weight Map #"+str(k)
                    thea_globals.log.debug("coating: %s" % layerId)
                    coating.getCoatingWeightTexture().write(file,layerId)
            except:
                type = None
            k+=1
        # write textured weights for substrates
        k=0
        for substrate in self.sortedSubstrates:
#            if getattr(bpy.context.active_object.active_material, 'thea_Coating', False):
#                k = 0
            try:
                if coating.getCoatingWeightTexture():
                    k = 1
                if not coating.getCoatingWeightTexture():
                    k = 1
            except:
                pass
            if substrate.getWeightTexture():
                layerId = "Weight Map #"+str(k)
                thea_globals.log.debug("substrate: %s" % layerId)
                substrate.getWeightTexture().write(file,layerId)
            k+=1
        # write parameters.
        file.write('<Parameter Name=\"Coatings\" Type=\"Integer\" Value=\"%s\"/>\n' % len(self.coatings))
        # write thickness (for coatings only).
        k=0
        for coating in self.coatings:
            layerId = "Layer #"+str(k)
            file.write('<Parameter Name=\"./%s/Thickness\" Type=\"Real\" Value=\"%s\"/>\n' % (layerId, coating.thickness))
            k+=1
        # write scalar weights for coatings
        k=0
        for coating in self.coatings:
            layerId = "Weight #"+str(k)
            file.write('<Parameter Name=\"./%s/Weight\" Type=\"Real\" Value=\"%s\"/>\n' % (layerId, coating.weight))
            k+=1
        # write scalar weights for substrates.
        k=0
        stacks = len(self.substrates)-1
        prevSubstrateOrder = 999
        for substrate in self.sortedSubstrates:
            layerId = "Weight #"+str(len(self.coatings)+k)
            file.write('<Parameter Name=\"./%s/Weight\" Type=\"Real\" Value=\"%s\"/>\n' % (layerId, substrate.getWeight()))
            k+=1
            if substrate.order == prevSubstrateOrder:
                stacks-=1
            prevSubstrateOrder = substrate.order
        file.write('<Parameter Name="Stacks" Type="Integer" Value="%s"/>\n' % stacks)
        file.write('</Object>\n')


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// End of BSDF Definitions
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Begin of Light Definitions
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Area Light
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class AreaLight:
    '''Area Light
    '''
    def __init__(self):
        self.unit = "Watts"
        self.power  = 100
        self.efficacy = 20
        self.emitterTexture = False
        self.layer = 0
        self.passive = False
        self.ambient = False
        self.ambientLevel = 1;
    def setTexture(self,  t):
        self.emitterTexture = t
    def setUnit(self,  u):
        self.unit = u
    def setPower(self,  p):
        self.power = p
    def setEfficacy(self,  e):
        self.efficacy = e

    def write(self, file):
        '''Write AreaLight object

            :param file: file handler
            :type file: file
        '''
        file.write('<Object Identifier=\"Diffuse Light\" Label=\"Diffuse Light\" Name=\"\" Type=\"Emittance\">\n')
        self.emitterTexture.write(file,"Radiance");
        file.write('<Parameter Name=\"Attenuation\" Type=\"String\" Value=\"Inverse Square\"/>\n')
        file.write('<Parameter Name=\"Power\" Type=\"Real\" Value=\"%s\"/>\n' % self.power)
        file.write('<Parameter Name=\"Efficacy\" Type=\"Real\" Value=\"%s\"/>\n' % self.efficacy)
        file.write('<Parameter Name=\"Unit\" Type=\"String\" Value=\"%s\"/>\n' % self.unit)
        file.write('<Parameter Name=\"Layer\" Type=\"Integer\" Value=\"%s\"/>\n' % self.layer)
        file.write('</Object>\n')
        file.write('<Parameter Name=\"Ambient Level\" Type=\"Real\" Value=\"%s\"/>\n' % self.ambientLevel)
        file.write('<Parameter Name=\"Ambient Emitter\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.ambient else '0'))
        file.write('<Parameter Name=\"Passive Emitter\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.passive else '0'))

class IESLight:
    '''IESLight
    '''
    def __init__(self):
        self.multiplier  = 1
        self.emitterTexture = False
        self.layer = 0
        self.passive = False
        self.ambient = False
        self.ambientLevel = 1;
        self.iesfile = ""
        self.unit = "Watts"
    def setTexture(self,  t):
        self.emitterTexture = t
    def setIesFile(self,  f):
        self.iesfile = os.path.abspath(bpy.path.abspath(f))
    def setMultiplier(self,  p):
        self.multiplier = p

    def write(self, file):
        '''Write IESLight object

            :param file: file handler
            :type file: file
        '''
        file.write('<Object Identifier=\"IES Light\" Label=\"IES Light\" Name=\"\" Type=\"Emittance\">\n')
        self.emitterTexture.write(file,"Color");
        file.write('<Parameter Name=\"Attenuation\" Type=\"String\" Value=\"Inverse Square\"/>\n')
        file.write('<Parameter Name=\"Multiplier\" Type=\"Real\" Value=\"%s\"/>\n' % self.multiplier)
        file.write('<Parameter Name=\"Unit\" Type=\"String\" Value=\"%s"/>\n' % self.unit)
        file.write('<Parameter Name=\"IES File\" Type=\"File\" Value=\"%s\"/>\n' % self.iesfile)
        file.write('</Object>\n')
        file.write('<Parameter Name=\"Ambient Level\" Type=\"Real\" Value=\"%s\"/>\n' % self.ambientLevel)
        file.write('<Parameter Name=\"Ambient Emitter\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.ambient else '0'))
        file.write('<Parameter Name=\"Passive Emitter\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.passive else '0'))


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Point Light
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class PointLight:
    '''Point Light
    '''

    def __init__(self):
        self.name="Light"
#        CHANGED > changed to enableLamp, so we can turn it off as well
        self.enableLamp = False
        self.emitter = False
        self.type="Omni" # "Spot" "IES" "Projector"
        self.attenuation="Inverse Square" # "None" "Inverse"  "Inverse Square"
        self.efficacy = 85.352
#CHANGED > position in hierachie
        self.sun = True
        self.shadow=True
#        CHANGED > Added manual setting sun
        self.manualSun = False
        self.softshadow=False
        self.softradius=0.1
        self.hotspot=0.4
        self.falloff=0.5
        self.multiplier=1
        self.radiusMultiplier=1
        self.frame = Transform()
        self.iesfile = False
        self.width = 1
        self.height = 1
        self.layer = 0

        self.interpolatedMotion = InterpolatedMotion()
        self.unit = "Watts"
        self.globalPhotons = True
        self.causticPhotons = True
        self.minRays = 8
        self.maxRays = 100
        self.bufferIndex = 0

    def setEmitterTexture(self, texture):
        self.emitter = texture

    def setIesFile(self,  f):
        self.iesfile = os.path.abspath(bpy.path.abspath(f))

    def write(self, file):
        '''Write PointLight object

            :param file: file handler
            :type file: file
        '''
        file.write('<Object Identifier=\"./Lights/%s\" Label=\"Default Light\" Name=\"%s\" Type=\"Light\">\n' % (self.name, self.name))
        if self.type == "Omni":
            stype = "Omni Light"
        if self.type == "Spot":
            stype ="Spot Light"
        if self.type == "IES":
            stype ="IES Light"
        if self.type == "Projector":
            stype ="Projector Light"

        file.write('<Object Identifier=\"%s\" Label=\"%s\" Name=\"\" Type=\"Emittance\">\n' % (stype, stype))
        self.emitter.write(file,"Radiance");
        file.write('<Parameter Name=\"Attenuation\" Type=\"String\" Value=\"%s\"/>\n' % self.attenuation)
#        CHANGED > Added Efficacy for all lights
        file.write('<Parameter Name=\"Efficacy\" Type=\"Real\" Value=\"%s\"/>\n' % self.efficacy)
        file.write('<Parameter Name=\"Unit\" Type=\"String\" Value=\"%s"/>\n' % self.unit)
        file.write('<Parameter Name=\"Power\" Type=\"Real\" Value=\"%s\"/>\n' % self.multiplier)
        #if self.sun:
            #file.write('<Parameter Name=\"Unit\" Type=\"String\" Value=\"W/nm/sr\"/>\n')
        #    file.write('<Parameter Name=\"Power\" Type=\"Real\" Value=\"%s\"/>\n' % self.multiplier)
        if self.type == "Spot":
            file.write('<Parameter Name=\"Hot Spot\" Type=\"Real\" Value=\"%s\"/>\n' % self.hotspot)
            file.write('<Parameter Name=\"Fall Off\" Type=\"Real\" Value=\"%s\"/>\n' % self.falloff)
        if self.type == "Projector":
            file.write('<Parameter Name=\"Width\" Type=\"Real\" Value=\"%s\"/>\n' % self.width)
            file.write('<Parameter Name=\"Height\" Type=\"Real\" Value=\"%s\"/>\n' % self.height)
        if self.type == "IES":
            file.write('<Parameter Name=\"IES File\" Type=\"File\" Value=\"%s\"/>\n' % self.iesfile)
#            CHANGED > Added this backin, IES use multiplier as text not power
            file.write('<Parameter Name=\"Multiplier\" Type=\"Real\" Value=\"%s\"/>\n' % self.multiplier)
        file.write('</Object>\n')
#        CHANGED > changed to enableLamp, so we can turn it off as well. Wasnt working below identifier. Also Radiance doesnt do anything i think
        file.write('<Parameter Name=\"Enabled\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.enableLamp else '0'))
#CHANGED > added equal state to check for sun. all lamps where converted to a sun but did have some llamp controls
        if self.sun == True and stype == "Omni Light":
#            CHANGED > moved this under sun. All light would get sun assinged and caused error in studio
            file.write('<Parameter Name=\"Sun\" Type=\"Boolean\" Value=\"%s\"/>\n' % self.sun)
#    CHANGED > Moved this out of sun, would get soft radius else
        file.write('<Parameter Name=\"Radius Multiplier\" Type=\"Real\" Value=\"%s\"/>\n' % self.radiusMultiplier)
        file.write('<Parameter Name=\"Manual Sun\" Type=\"Boolean\" Value=\"%s\"/>\n' % self.manualSun)
        file.write('<Parameter Name=\"Shadow\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.shadow else '0'))
        file.write('<Parameter Name=\"Soft Shadow\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.softshadow else '0'))
        #file.write('<Parameter Name=\"Multiplier\" Type=\"Real\" Value=\"%s\"/>\n' % self.multiplier)
        file.write('<Parameter Name=\"Radius\" Type=\"Real\" Value=\"%s\"/>\n' % self.softradius)
        file.write('<Parameter Name=\"Layer\" Type=\"Integer\" Value=\"%s\"/>\n' % self.layer)

        file.write('<Parameter Name=\"Global Photons\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.globalPhotons else '0'))
        file.write('<Parameter Name=\"Caustic Photons\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.causticPhotons else '0'))
        file.write('<Parameter Name=\"Min Rays\" Type=\"Integer\" Value=\"%s\"/>\n' % self.minRays)
        file.write('<Parameter Name=\"Max Rays\" Type=\"Integer\" Value=\"%s\"/>\n' % self.maxRays)
        file.write('<Parameter Name=\"Light Buffer Index\" Type=\"Integer\" Value=\"%s\"/>\n' % self.bufferIndex)

        self.interpolatedMotion.write(file)
        self.frame.write(file)

        file.write('</Object>\n')

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// End of Light Definitions
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////





#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Begin of Modifier Definitions
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Clip Mapping
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Clipping:
    '''Clipping material modifier
    '''
    def __init__(self):
        self.threshold = 0.5
        self.soft = False

    def setTexture(self, texture):
        self.clipTexture=texture
    def setThreshold(self, v):
        self.threshold=v
    def setSoft(self, v):
        self.soft=v

    def write(self, file):
        '''Write Clipping material modifier object

            :param file: file handler
            :type file: file
        '''
        if self.clipTexture:
            file.write('<Object Identifier=\"Clip Mapping\" Label=\"Clip Mapping\" Name=\"\" Type=\"Acceptance Modifier\">\n')
            self.clipTexture.write(file,"Texture");
            file.write('<Parameter Name=\"Threshold\" Type=\"Real\" Value=\"%s\"/>\n' % self.threshold)
            file.write('<Parameter Name=\"Soft\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.soft else '0'))
            file.write('</Object>\n')

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Displacement Mapping
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Displacement:
    '''Displacement material modifier
    '''
    def __init__(self):
        self.subdivision = 2
        self.microbump = 0
        self.height = 0.02
        self.center = 0.5
        self.tightbounds = True
        self.normalsmoothing = True

    def setTexture(self, t):
        self.displaceTexture=t

    def setSubdivision(self, v):
        self.subdivision=v
    def setMicroBump(self, v):
        self.microbump=v
    def setHeight(self, v):
        self.height=v
    def setCenter(self, v):
        self.center=v
    def setTightBounds(self, v):
        self.tightbounds=v

    def write(self, file):
        '''Write Displacement material modifier object

            :param file: file handler
            :type file: file
        '''
        if self.displaceTexture:
            file.write('<Object Identifier=\"Displacement Mapping\" Label=\"Displacement Mapping\" Name=\"\" Type=\"Shape Modifier\">\n')
            self.displaceTexture.write(file,"Texture");
            file.write('<Parameter Name=\"Subdivision\" Type=\"Integer\" Value=\"%s\"/>\n' % self.subdivision)
        #              file.write('<Parameter Name=\"Micro-Bump\" Type=\"Integer\" Value=\"%s\"/>\n' % self.microbump)
            file.write('<Parameter Name=\"Height\" Type=\"Real\" Value=\"%s\"/>\n' % self.height)
            file.write('<Parameter Name=\"Center\" Type=\"Real\" Value=\"%s\"/>\n' % self.center)
            file.write('<Parameter Name=\"Normal Smoothing\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.normalsmoothing else '0'))
            file.write('<Parameter Name=\"Tight Bounds\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.tightbounds else '0'))
        file.write('</Object>\n')

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// End of Modifier Definitions
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Material
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class ThMaterial:
    '''Main material class. It defines whole material with LayeredBSDF and modifiers
    '''
    def __init__(self):
        self.shadowCatcher = False
        self.twosided = True
#        CHANGED > Added repaintable, dirt & desciption
        self.repaintable = False
        self.dirt = False
        self.description = ""
        self.areaLight= None
        self.layeredBsdf=LayeredBSDF()
        self.clipping=None
        self.displacement=None
        self.medium=None
        self.blenderMat = None
        self.link = False
        self.shadowOnly = False

    def setDisplacement(self, d):
        self.displacement=d
    def setAreaLight(self, a):
        self.areaLight=a
    def setMedium(self, a):
        self.medium=a
    def setLayeredBSDF(self, b):
        self.layeredBsdf=b
    def setBSDF(self, b,wh=1,wTex=None):
        self.layeredBsdf=LayeredBSDF(LayeredSubstrate(b,wh,wTex))
    def setClipping(self, c):
        self.clipping=c
    def getDisplacement(self, d):
        self.displacement=d

    def setTwoSided(self, v):
        self.twosided=v
    def getTwoSided(self):
        return self.twosided
#CHNAGED > Added repaintable, dirt & description
    def setRepaintable(self, v):
        self.repaintable=v
    def setDirt(self, v):
        self.dirt=v
    def setDescription(self, v):
        self.description=v

    def getName(self):
        return self.name
    def setName(self, n):
        self.name=n

    def write(self, file, preview=False):
        ''' Write whole material object

            :param file: file handler
            :type file: file
            :param preview: Write different header if material is used for preview scene
            :type preview: bool
        '''
        if self.link == False:
            if preview:
                file.write('<Root Label=\"Appearance\" Name=\"%s\" Type=\"Appearance\">\n' % self.name)
            else:
                file.write('<Object Identifier=\"./Proxies/Appearance/%s\" Label=\"Appearance\" Name=\"%s\" Type=\"Appearance\">\n' % (self.name, self.name))
            if self.medium:
                self.medium.write(file)
            if self.areaLight:
                self.areaLight.write(file)
            if self.layeredBsdf:
                self.layeredBsdf.write(file)
            if self.clipping:
                self.clipping.write(file)
            if self.displacement:
                self.displacement.write(file)
            if self.shadowOnly:
                file.write('<Parameter Name=\"Shadow-Only\" Type=\"Boolean\" Value=\"1\"/>\n')

            file.write('<Parameter Name=\"Shadow Catcher\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.shadowCatcher else '0'))
#            CHANGED > Added extra option for material settigns
            file.write('<Parameter Name=\"Two-Sided\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.twosided else '0'))
            file.write('<Parameter Name=\"Repaintable\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.repaintable else '0'))
            file.write('<Parameter Name=\"Dirt\" Type=\"Real\" Value=\"1\"/>\n')
            file.write('<Parameter Name=\"Description\" Type=\"String\" Value=\"%s\"/>\n' % self.description)
            file.write('<Parameter Name=\"Active Dirt\" Type=\"Boolean\" Value=\"0\"/>\n')
            file.write('<Parameter Name=\"Perceptual Level\" Type=\"Real\" Value=\"1\"/>\n')
            file.write('<Parameter Name=\"Emitter Accuracy\" Type=\"Real\" Value=\"0.9\"/>\n')
            file.write('<Parameter Name=\"Emitter Min Rays\" Type=\"Integer\" Value=\"8\"/>\n')
            file.write('<Parameter Name=\"Emitter Max Rays\" Type=\"Integer\" Value=\"100\"/>\n')
            file.write('<Parameter Name=\"Global Photons\" Type=\"Boolean\" Value=\"1\"/>\n')
            file.write('<Parameter Name=\"Caustic Photons\" Type=\"Boolean\" Value=\"1\"/>\n')
            file.write('<Parameter Name=\"Min Blurred Subdivs\" Type=\"String\" Value=\"Default\"/>\n')
            file.write('<Parameter Name=\"Max Blurred Subdivs\" Type=\"String\" Value=\"Default\"/>\n')
            file.write('<Parameter Name=\"Tracing Depth\" Type=\"String\" Value=\"Default\"/>\n')

            if preview:
                file.write('</Root>')
            else:
                file.write('</Object>\n')



#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Model - that is a geometric object
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Model:
    ''' Model - that is a geometric object. Not used in this implementation as binary mesh formatt is used.
    '''
    def __init__(self):
        self.pointList = []
        self.normalList = []
        self.indexList = []
        self.uvList = []
        smoothingAngle = 90
        self.materialName = None
        self.frame = Transform()
        self.visible = 1


    def write(self, file):
        '''Write model object

            :param file: file handler
            :type file: file
        '''
        file.write('<Object Identifier=\"./Models/%s\" Label=\"Default Model\" Name=\"%s\" Type=\"Model\">\n' % (self.name, self.name))
        file.write('<Object Identifier=\"Triangular Mesh\" Label=\"Triangular Mesh\" Name=\"\" Type=\"Surface\">\n')
        file.write('<Parameter Name=\"Smoothing Angle\" Type=\"Real\" Value=\"%s\"/>\n' % smoothingAngle)
        file.write('<Parameter Name=\"Vertex List\" Type=\"Point3D List\" Value=\"%s\">\n' % len(self.pointList))
        for p in self.pointList:
            file.write('<P xyz=\"%s %s %s\"/>\n' % (p.x, p.y, p.z))
        file.write('</Parameter>\n')

        file.write('<Parameter Name=\"Normal List\" Type=\"Point3D List\" Value=\"%s\">\n' % len(self.normalList))
        for n in self.normalList:
            file.write('<P xyz=\"%s %s %s\"/>\n' % (n.x, n.y, n.z))
        file.write('</Parameter>\n')

        file.write('<Parameter Name=\"Index List\" Type=\"Triangle Index List\" Value=\"%s\">\n' % len(self.indexList))
        for d in self.indexList:
            file.write('<F ijk=\"%s %s %s\"/>\n' % (d.i, d.j, d.k))
        file.write('</Parameter>\n')


        file.write('<Parameter Name=\"Map Channel\" Type=\"Point2D List\" Value=\"%s\">\n' % len(self.uvList))
        for p in self.uvList:
            file.write('<P xy=\"%s %s\"/>\n' % (p.u, p.v))
        file.write('</Parameter>\n')


        thea_globals.log.debug("*** Model custom normals: %s" % self.smoothingAngle)
#        if mesh.use_auto_smooth:
##                        modelSmooth = ""
#                        modelSmooth = ('<Parameter Name=\"Smoothing Angle\" Type=\"Real\" Value=\"%s\"/>\n' % (round (180 * mesh.auto_smooth_angle / 3.14159265359)))
#                        thea_globals.log.debug("*** Model custom normals: %s" % modelSmooth))
        file.write('<Parameter Name=\"Pivot\" Type=\"Transform\" Value=\"1 0 0 0 0 1 0 0 0 0 1 1.11423 \"/>\n')
        file.write('</Object>\n')
#        file.write('<Parameter Name=\"Smoothing Angle\" Type=\"Real\" Value=\"%s\"/>\n' % self.smoothingAngle)
#        file.write('<Parameter Name=\"Smoothing Angle\" Type=\"Real\" Value=\"%s\"/>\n' % (round (180 * self.auto_smooth_angle) / 3.14159265359))

        file.write('<Parameter Name=\"Appearance\" Type=\"String\" Value=\"%s\"/>\n' % self.materialName)
        file.write('<Parameter Name=\"Smoothing Angle\" Type=\"Real\" Value=\"%s\"/>\n' % smoothingAngle)
        self.frame.write(file);

        file.write('</Object>\n')


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Camera
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class ThCamera:
    '''Camera
    '''
    def __init__(self):
        self.name="Camera"
        self.focalLength=35
        self.filmHeight=25
        self.pixels=500
        self.lines=500
        self.focusDistance=1 #in meters
        self.shutterSpeed=500
        self.fNumber=5.6
#       CHANGED> Added DOF %
        self.enableDOFpercentage = False
        self.DOFpercentage = 30
#       CHANGED > Added new sharpness here
        self.sharpness=True
        self.sharpnessWeight=50
        self.autofocus=True
        self.shiftLensX=0 # in mm
        self.shiftLensY=0 # in mm
#       CHANGED > added new diaphgrama here
        self.diaphragm="Circular" # "Polygonal"
        self.blades=6
        self.projection="Planar" # "Spherical" : "Cylindrical"
        self.interpolatedMotion = InterpolatedMotion()
        self.frame = Transform()
        self.renderRegion = False
#        self.regionsettings = ""
        self.region = ""
        self.camLocked = 1
        self.zClippingNear = False
        self.zClippingFar = False
        self.zClippingNearDistance = 1
        self.zClippingFarDistance = 1000
        self.sectionFrame = False
        self.sectionFrameTrans = thea_globals.sectionFrameTrans

    def write(self, file):
        '''Write camera object

            :param file: file handler
            :type file: file
        '''
        file.write('<Object Identifier=\"./Cameras/%s\" Label=\"Standard Camera\" Name=\"%s\" Type=\"Camera\">\n' % (self.name, self.name))
        file.write('<Parameter Name=\"Focal Length (mm)\" Type=\"Real\" Value=\"%s\"/>\n' % self.focalLength)
        file.write('<Parameter Name=\"Film Height (mm)\" Type=\"Real\" Value=\"%s\"/>\n' % self.filmHeight)
        file.write('<Parameter Name=\"Shift X (mm)\" Type=\"Real\" Value=\"%s\"/>\n' % self.shiftLensX)
        file.write('<Parameter Name=\"Shift Y (mm)\" Type=\"Real\" Value=\"%s\"/>\n' % self.shiftLensY)
        file.write('<Parameter Name=\"Resolution\" Type=\"String\" Value=\"%sx%s\"/>\n' % (self.pixels, self.lines))
        file.write('<Parameter Name=\"Focus Distance\" Type=\"Real\" Value=\"%s\"/>\n' % self.focusDistance)
        file.write('<Parameter Name=\"Auto-Focus\" Type=\"Boolean\" Value=\"%s\"/>\n' % self.autofocus)
        file.write('<Parameter Name=\"Shutter Speed\" Type=\"Real\" Value=\"%s\"/>\n' % self.shutterSpeed)
        file.write('<Parameter Name=\"f-number\" Type=\"String\" Value=\"%s\"/>\n' % self.fNumber)
#        CHANGED> Added DOF %
        file.write('<Parameter Name=\"Depth of Field\" Type=\"Real\" Value=\"%s\"/>\n' % (self.DOFpercentage / 100))
        file.write('<Parameter Name=\"DOF Lock\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.enableDOFpercentage else '0'))
#       CHANGED > added blades and diaphgrama here
        file.write('<Parameter Name=\"Blades\" Type=\"Integer\" Value=\"%s\"/>\n' % self.blades)
        file.write('<Parameter Name=\"Diaphragm\" Type=\"String\" Value=\"%s\"/>\n' % self.diaphragm)
        file.write('<Parameter Name=\"Projection\" Type=\"String\" Value=\"%s\"/>\n' % self.projection)
        file.write('<Parameter Name=\"Region\" Type=\"String\" Value=\"%s\"/>\n' % self.region)
        file.write('<Parameter Name=\"Render Region\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.renderRegion else '0'))
#        CHANGED>Added camera lock (handy when its eported so you dont accidently move the camera)
        file.write('<Parameter Name=\"Locked\" Type=\"Boolean\" Value=\"%s\"/>\n' % self.camLocked)
        file.write('<Parameter Name=\"Z-Clipping Near\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.zClippingNear else '0'))
        file.write('<Parameter Name=\"Z-Clipping Far\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.zClippingFar else '0'))
        file.write('<Parameter Name=\"Z-Clipping Near Distance\" Type=\"Real\" Value=\"%s\"/>\n ' % self.zClippingNearDistance)
        file.write('<Parameter Name=\"Z-Clipping Far Distance\" Type=\"Real\" Value=\"%s\"/>\n' % self.zClippingFarDistance)
        self.interpolatedMotion.write(file)
        self.frame.write(file)
#        thea_globals.log.debug("Zclip Camera: %s - Exported Camera: %s" % (bpy.context.scene.camera.name, self.name))
        try:

            if self.name == bpy.context.scene.camera.name:

                if thea_globals.sectionFrameEnabled:
                    file.write(thea_globals.sectionFrameTrans)
#                    thea_globals.log.debug("Section Frame Trans: %s" % thea_globals.sectionFrameTrans)
                    thea_globals.sectionFrameEnabled = False
#            file.write('<Parameter Name=\"./Section #0/Frame\" Type=\"Transform\" Value=\"%s %s %s %s %s %s %s %s %s %s %s %s\"/>\n' % (thea_globals.sectionFrameTrans[0], thea_globals.sectionFrameTrans[1], thea_globals.sectionFrameTrans[2], thea_globals.sectionFrameTrans[3], thea_globals.sectionFrameTrans[4], thea_globals.sectionFrameTrans[5], thea_globals.sectionFrameTrans[6], thea_globals.sectionFrameTrans[7],thea_globals.sectionFrameTrans[8], thea_globals.sectionFrameTrans[9], thea_globals.sectionFrameTrans[10], thea_globals.sectionFrameTrans[11]))

        #        for i in thea_globals.sectionFrameTrans:
    #            thea_globals.log.debug("Section Frame Trans: %s" % i)
        except:
             pass
        file.write('</Object>\n')


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Environment (Global) Options
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class EnvironmentOptions:
    '''Environment options
    '''
    class IBLMap:
        def __init__(self):
            self.enabledParameter = False
            self.intensity = 1.0
            self.wrapping = "Spherical"
            self.iblType = "IBL Only"
            self.bitmapTexture = None
            self.rotation = 0
        def write(self, file, identifier, enabledParameter):
            file.write('<Parameter Name=\"./%s/Filename\" Type=\"File\" Value=\"%s\"/>\n' % (identifier, self.bitmapTexture.getFilename()))
            file.write('<Parameter Name=\"./%s/Wrapping\" Type=\"String\" Value=\"' % identifier)
            if self.wrapping == "Center":
                file.write("Center")
            if self.wrapping == "Tile":
                file.write("Tile")
            if self.wrapping == "Fit":
                file.write("Fit")
            if self.wrapping == "AngularProbe":
                file.write("Angular Probe")
            if self.wrapping == "Hemispherical":
                 file.write("Hemispherical")
            if self.wrapping == "Spherical":
                file.write("Spherical")
            file.write("\"/>\n")
            if identifier == "Illumination Mapping":
                file.write('<Parameter Name=\"IBL Type\" Type="String" Value=\"%s\"/>\n' % (self.iblType))
            file.write('<Parameter Name=\"./%s/Intensity\" Type=\"Real\" Value=\"%s\"/>\n' % (identifier,self.intensity))
            file.write('<Parameter Name=\"./%s/Rotation" Type=\"Real\" Value="%s"/>\n' % (identifier, self.rotation))
            if self.enabledParameter:
                file.write('<Parameter Name=\"./%s/Enable\" Type=\"Boolean\" Value=\"%s\"/>\n' % (identifier, ('1' if self.enabledParameter else '0')))

    def __init__(self):
        self.skyType = "Sun+Sky"
        self.turbidity = 2.5
        self.ozone = 0.35
        self.waterVapor = 2.0
        self.turbidityCoefficient = 0.046
        self.wavelengthExponent = 1.3
#        CHANGED> Added missing Abledo
        self.albedo = 0.5
        self.locEnable = True
        self.location = ""
        self.latitude = 0.0
        self.longitude = 0.0
        self.timezone = "GHANA - Acra"
        self.date = ""
        self.localtime = ""
        self.polarAngle = 22.992
        self.azimuthAngle = -177.906
        self.illumination = None
        self.backgroundColor = RgbTexture()
        self.illuminationMap = None
        self.backgroundMap = None
        self.reflectionMap = None
        self.refractionMap = None
        self.globalFrame  = None
        self.backgroundMapEnable = False
        self.overrideSun = False
        self.updateSky = True
        self.sunDirectionX = 0
        self.sunDirectionY = 0
        self.sunDirectionZ = 0
#        CHANGED > Added Global Medium Options
        self.GlobalMediumEnable = None
        self.GlobalMediumIOR = 1.0
        self.scatteringColor = (1,1,1)
        self.scatteringDensity = 1.0
        self.scatteringDensityTexture = None
        self.absorptionColor = (1,1,1)
        self.absorptionDensity = 1.0
        self.absorptionDensityTexture = None
        self.MediumCoefficentEnable = False
        self.coefficientFilename = False
        self.phaseFunction = "Isotropic"
        self.asymetry = 0.0

    def write(self, file):
        '''Write environment (global settings) object

            :param file: file handler
            :type file: file
        '''
        file.write('<Object Identifier=\"Global Settings\" Label=\"Global Settings\" Name=\"\" Type=\"Global Settings\">\n')

#        CHANGED > Added GLobal Medium here
#        thea_globals.log.info("Writting Global Mediuam options")
        if self.GlobalMediumEnable == True:
            file.write('<Object Identifier=\"./Medium/Standard Medium\" Label=\"Standard Medium\" Name=\"Standard Medium\" Type=\"Medium\">\n')

#            file.write('<Object Identifier=\"./Absorption Color/Constant Texture\" Label=\"Constant Texture\" Name=\"\" Type=\"Texture\">\n')
            if self.absorptionColor:
    #            self.absorptionColor.write(file,"Absorption Color")
#                file.write('<Parameter Name="Color" Type="RGB" Value=\"%s\"/>\n' % self.absorptionColor)
                RgbTexture(1,1,1).write(file,"Absorption Color")
#            file.write('</Object>\n')
            if self.absorptionDensityTexture:
                self.absorptionDensityTexture.write(file,"Absorption Density")
#            file.write('<Object Identifier=\"./Scatter Color/Constant Texture\" Label=\"Constant Texture\" Name=\"\" Type=\"Texture\">\n')
            if self.scatteringColor:
#                file.write('<Parameter Name="Color" Type="RGB" Value=\"%s\"/>\n' % self.scatteringColor)
                RgbTexture(1,1,1).write(file,"Scatter Color")
#            file.write('</Object>\n')
            if self.scatteringDensityTexture:
                self.scatteringDensityTexture.write(file,"Scatter Density")
            file.write('<Parameter Name=\"Absorption Coefficient\" Type=\"Real\" Value=\"%s\"/>\n' % self.absorptionDensity)
            file.write('<Parameter Name=\"Scatter Coefficient\" Type=\"Real\" Value=\"%s\"/>\n' % self.scatteringDensity)
            if self.MediumCoefficentEnable == True:
                file.write('<Parameter Name=\"Coefficient File\" Type=\"String\" Value=\"%s\"/>\n' % self.coefficientFilename)
                file.write('<Parameter Name=\"User Colors\" Type=\"Boolean\" Value=\"0\"/>\n')
            file.write('<Parameter Name=\"Phase Function\" Type=\"String\" Value=\"%s\"/>\n' % self.phaseFunction)
            file.write('<Parameter Name=\"Asymmetry\" Type=\"Real\" Value=\"%s\"/>\n' % self.asymetry)
            file.write('</Object>\n')

        self.globalFrame.write(file,"Sky Frame");
#        CHANGED > Added GLobal Medium IOR
        file.write('<Parameter Name=\"Index of Refraction\" Type=\"Real\" Value=\"%s\"/>\n' % self.GlobalMediumIOR)
        file.write('<Parameter Name=\"Turbidity" Type=\"Real\" Value=\"%s\"/>\n' % self.turbidity)
        file.write('<Parameter Name=\"Ozone\" Type=\"Real\" Value=\"%s\"/>\n' % self.ozone)
        file.write('<Parameter Name=\"Water Vapor\" Type=\"Real\" Value=\"%s\"/>\n' % self.waterVapor)
        file.write('<Parameter Name=\"Turbidity Coefficient\" Type=\"Real\" Value=\"%s\"/>\n' % self.turbidityCoefficient)
        file.write('<Parameter Name=\"Wavelength Exponent\" Type=\"Real\" Value=\"%s\"/>\n' % self.wavelengthExponent)
#        CHANGED > Added missing Albedo
        file.write('<Parameter Name=\"Albedo\" Type=\"Real\" Value=\"%s\"/>\n' % self.albedo)
#CHANGED> Only add location when ON otherwise we cant render sky only with manual sun
        if self.locEnable:
            thea_globals.log.debug("*** Locations Menu: %s" % self.locEnable)
            file.write('<Parameter Name=\"./Location/Location\" Type=\"String\" Value=\"%s\"/>\n' % self.location)
#            from TheaForBlender.thea_render_main import getLocMenu
#            locFile = getLocMenu()[int(getattr(bpy.context.scene, "thea_EnvLocationsMenu"))]
            file.write('<Parameter Name=\"./Location/Latitude\" Type=\"Real\" Value=\"%s\"/>\n' % self.latitude)
            file.write('<Parameter Name=\"./Location/Longitude\" Type=\"Real\" Value=\"%s\"/>\n' % self.longitude)
            file.write('<Parameter Name=\"./Location/Timezone\" Type=\"String\" Value=\"%s\"/>\n' % self.timezone)
            file.write('<Parameter Name=\"./Location/Date\" Type=\"String\" Value=\"%s\"/>\n' % self.date)
            file.write('<Parameter Name=\"./Location/Time\" Type=\"String\" Value=\"%s\"/>\n' % self.localtime)
            file.write('<Parameter Name=\"./Sun/Polar Angle (deg)\" Type=\"Real\" Value=\"%s\"/>\n' % self.polarAngle)
            file.write('<Parameter Name=\"./Sun/Azimuth (deg)" Type=\"Real\" Value=\"%s\"/>\n' % self.azimuthAngle)
        file.write('<Parameter Name=\"Background Color\" Type=\"RGB\" Value=\"%s %s %s\"/>\n' % (self.backgroundColor.r(), self.backgroundColor.g(), self.backgroundColor.b()))
        file.write('<Parameter Name=\"Illumination\" Type=\"String\" Value=\"')
        if self.illumination == "Dome":
            file.write('Dome\"/>\n')
        elif self.illumination == "IBL":
            file.write('Image Based Lighting\"/>\n')
        elif self.illumination == "PhysicalSky" or self.locEnable:
            file.write('Physical Sky\"/>\n')
            file.write('<Parameter Name="Sky Type" Type="String" Value="%s"/>\n' % self.skyType)
            file.write('<Parameter Name="Sun Direction" Type="String" Value="%s %s %s"/>\n' % (self.sunDirectionX, self.sunDirectionY, self.sunDirectionZ))
        else:
             file.write('None\"/>\n')
        if self.illuminationMap:
            self.illuminationMap.write(file,"Illumination Mapping",True)
        if self.backgroundMap:
            self.backgroundMap.write(file,"Background Mapping",True);
            file.write('<Parameter Name="./Background Mapping/Enable" Type="Boolean" Value="1"/>\n')
        if self.reflectionMap:
            self.reflectionMap.write(file,"Reflection Mapping",True);
        if self.refractionMap:
            self.refractionMap.write(file,"Refraction Mapping",True);

        file.write('</Object>\n')

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Display Options
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class DisplayOptions:
    '''Display options
    '''
    def __init__(self):
        self.iso = 100
        self.shutter = 250
        self.fNumber = 5.6
        self.gamma = 2.2
        self.brightness = 1.0
#       CHANGED > TYPO IN THE WORD SHARPNESS
        self.sharpness = True
        self.sharpnessWeight = 0.5
        self.burn = True
        self.burnWeight = 0.1
        self.vignetting = False
        self.vignettingWeight = 0.2
        self.chroma = False
        self.chromaWeight = 0.2
        self.contrast = False
        self.contrastWeight = 0.0
        self.balance = False
        self.temperature = 6500.0
        self.bloom = False
        self.bloomWeight = 0.2
        self.bloomItems = None
        self.glareRadius = 0.04
        self.minZ = 0.0
        self.maxZ = 10.0
        self.analysis = 0
        self.analysisMenu = "none"
        self.minIlLum = 1000.0
        self.maxIlLum = 15000.0

    def write(self, file):
        '''Write Display Options object

            :param file: file handler
            :type file: file
        '''
        global scn

        thea_globals.log.debug("dispay options: import")
        from TheaForBlender.thea_render_main import getTheaCRF
        thea_globals.log.debug("dispay options: write")
        file.write('<Object Identifier=\"Display\" Label=\"Display\" Name=\"\" Type=\"Display\">\n')
        file.write('<Parameter Name=\"ISO\" Type=\"Real\" Value=\"%s\"/>\n' % self.iso)
        file.write('<Parameter Name=\"Shutter Speed\" Type=\"Real\" Value=\"%s\"/>\n' % self.shutter)
        file.write('<Parameter Name=\"f-number\" Type=\"Real\" Value=\"%s\"/>\n' % self.fNumber)
        file.write('<Parameter Name=\"Gamma\" Type=\"Real\" Value=\"%s\"/>\n' % self.gamma)
        file.write('<Parameter Name=\"Brightness\" Type=\"Real\" Value=\"%s\"/>\n' % self.brightness)
#        CHANGED > TYPO IN THE WORD SHARPNESS added FILTER instead of sharpness
        file.write('<Parameter Name=\"Filter\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.sharpness else '0'))
        file.write('<Parameter Name=\"Sharpness\" Type=\"Real\" Value=\"%s\"/>\n' % self.sharpnessWeight)
#        file.write('<Parameter Name=\"HIER ZIT DE FOUT\" Type=\"Real\" Value=\"%s\"/>\n' % "KIJK HIER")
        file.write('<Parameter Name=\"Burn\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.burn else '0'))
        file.write('<Parameter Name=\"Burn Weight\" Type=\"Real\" Value=\"%s\"/>\n' % self.burnWeight)
        file.write('<Parameter Name=\"Vignetting\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.vignetting else '0'))
        file.write('<Parameter Name=\"Vignetting Weight\" Type=\"Real\" Value=\"%s\"/>\n' % self.vignettingWeight)
        file.write('<Parameter Name=\"Chroma\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.chroma else '0'))
        file.write('<Parameter Name=\"Chroma Weight\" Type=\"Real\" Value=\"%s\"/>\n' % self.chromaWeight)
        file.write('<Parameter Name=\"Contrast\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.contrast else '0'))
        file.write('<Parameter Name=\"Contrast Weight\" Type=\"Real\" Value=\"%s\"/>\n' % self.contrastWeight)
        file.write('<Parameter Name=\"Balance\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.balance else '0'))
        file.write('<Parameter Name=\"Temperature\" Type=\"Real\" Value=\"%s\"/>\n' % self.temperature)
        file.write('<Parameter Name=\"Bloom\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.bloom else '0'))
#       CHANGED > Added glare dropdown
        file.write('<Parameter Name=\"Glare\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.bloomItems else '0'))
        if self.bloomItems != "0":
            file.write('<Parameter Name=\"Glare Blades\" Type=\"Integer\" Value=\"%s\"/>\n' % self.bloomItems)
        file.write('<Parameter Name=\"Bloom Weight\" Type=\"Real\" Value=\"%s\"/>\n' % self.bloomWeight)
        file.write('<Parameter Name=\"Bloom Radius\" Type=\"Real\" Value=\"%s\"/>\n' % self.glareRadius)
        file.write('<Parameter Name=\"Min Z (m)\" Type=\"Real\" Value=\"%s\"/>\n' % self.minZ)
        file.write('<Parameter Name=\"Max Z (m)\" Type=\"Real\" Value=\"%s\"/>\n' % self.maxZ)
        file.write('<Parameter Name=\"False Color\" Type=\"Boolean\" Value=\"%s\"/>\n' % self.analysisMenu)
        file.write('<Parameter Name=\"Min Il-Lum\" Type=\"Real\" Value=\"%s\"/>\n' % self.minIlLum)
        file.write('<Parameter Name=\"Max Il-Lum\" Type=\"Real\" Value=\"%s\"/>\n' % self.maxIlLum)


        thea_globals.log.debug("dispay options: try")
        thea_globals.log.debug("dispay options: getTheaCRF")
        crf = getTheaCRF()
#         thea_globals.log.debug("crf: %s" % crf)
        crfFile = getattr(bpy.context.scene, 'thea_DispCRFMenu', 0)
        thea_globals.log.debug("crfFile: %s" % crfFile)
        if crfFile != "0":
            file.write('<Parameter Name=\"Enable CRF\" Type=\"Boolean\" Value=\"1\"/>\n')
            file.write('<Parameter Name=\"CRF File\" Type=\"File\" Value=\"%s\"/>\n' % crfFile)
        thea_globals.log.debug("dispay options: end of write")
        file.write('</Object>\n')



#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Display Options
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class AnimationOptions:
    '''Animation Options
    '''
    def __init__(self):
        self.currentFrame = 0
        self.endFrame = 0
        self.frameRate = 24



    def write(self, file):
        '''Write animation options parameters

            :param file: file handler
            :type file: file
        '''
        file.write('<Parameter Name=\"./Animation/Time\" Type=\"Real\" Value=\"%s\"/>\n' % self.currentFrame)
        file.write('<Parameter Name=\"./Animation/End Frame\" Type=\"Integer\" Value=\"%s\"/>\n' % self.endFrame)
        file.write('<Parameter Name=\"./Animation/Current Frame\" Type=\"Integer\" Value=\"%s\"/>\n' % self.currentFrame)
        file.write('<Parameter Name=\"./Animation/Frame Rate\" Type=\"Integer\" Value=\"%s\"/>\n' % self.frameRate)


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Render Options
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class RenderOptions:
    '''Render options
    '''
    def __init__(self):
        self.animationOptions = AnimationOptions()
        self.activeCamera = None
        self.engine = "Unbiased (TR1)"
        self.interactiveEngine = "Presto (MC)"
        self.supersampling = "DefaultSS"
#        CHANGED> Added adaptive bias +displacement
        self.adaptiveBias = "25"
        self.displacemScene = True
        self.maxPasses = 10000
        self.maxSamples = 10000
        self.maxRenderTime = 0
        self.motionBlur = True
        self.volumetricScattering = True
        self.lightBlending = False
        self.imageSaving = True
        self.clayrender = False
        self.clayrenderreflectance = 0
        self.filmSaving = True
        self.threads = 0
        self.priority = 0
        self.network = None
        self.serverport = 6200
        self.serveraddress = "127.0.0.1"
        self.checkChannels = False
        self.colorChannel = False
        self.normalChannel = False
        self.positionChannel = False
        self.uvChannel = False
        self.depthChannel = False
        self.alphaChannel = False
        self.objectIdChannel = False
        self.materialIdChannel = False
        self.shadowChannel = False
        self.maskChannel = False
        self.rawDiffuseColorChannel = False
        self.rawDiffuseLightingChannel = False
        self.rawDiffuseGIChannel = False
        self.selfIlluminationChannel = False
        self.directChannel = False
        self.AOChannel = False
        self.giChannel = False
        self.sssChannel = False
        self.reflectionChannel = False
        self.refractionChannel = False
        self.transparentChannel = False
        self.irradianceChannel = False
        self.separatePassesPerLightChannel = False
        self.invertMaskChannel = False
        self.rayTracingDepth = 5
        self.rayDiffuseDepth = 2
        self.rayGlossyDepth = 2
        self.rayTraceDispersion = False
        self.rayTraceReflections = True
        self.rayTraceRefractions = True
        self.rayTraceTransparencies = True
        self.rayTraceReflections = True
        self.rayTraceRefractions = True
        self.maxContrast = 0.02
        self.minAASubdivs = 0
        self.maxAASubdivs = 4
        self.directLighting = True
        self.perceptualBased = False
        self.maxDirectError = 0.02
        self.photonMapping = False
        self.finalGathering = True
        self.secondaryGather = False
        self.globalIllumination = True
        self.caustics = False
        self.leakCompensation = False
        self.causticSharpening = False
        self.subsurfaceScattering = False
        self.globalPhotonsCaptured = 1000000
        self.causticPhotonsCaptured = 10000
        self.globalEstimationPhotons = 400
        self.causticEstimationPhotons = 400
        self.globalEstimationRadius =  0.5
        self.causticEstimationRadius = 0.1
        self.gatherRays = 200
        self.maxGatherError = 0.15
        self.distanceThreshold = 0.1
        self.gatherDiffuseDepth = 3
        self.gatherTracingDepth = 2
        self.gatherGlossyDepth = 0
        self.gatherAdaptiveSteps = 3
        self.gatherTraceReflections = True
        self.gatherTraceRefractions = True
        self.gatherTraceTransparencies = True
        self.blurredReflections = True
        self.minBlurredSubdivs = 0
        self.maxBlurredSubdivs = 3
        self.glossyEvaluation = False
        self.causticEvaluation = False
        self.ICEnable = True
        self.ICAccuracy = 0.85
        self.ICForceInterpolation = True
        self.ICPrepass = "1/1"
        self.ICPrepassBoost = 0.5
        self.ICMinDistance = 4.0
        self.ICMaxDistance = 100.0
        self.AOEnable = False
        self.AOMultiply = False
        self.AOClamp = False
        self.AOSamples = 100
        self.AODistance = 10.0
        self.AOIntensity = 10.0
        self.AOLowColor = [0.0,0.0,0.0]
        self.AOHighColor = [1.0,1.0,1.0]
        self.FMEnable = False
        self.FMFieldDensity = 100000
        self.FMCellSize = 1000
        self.deviceMask = "GPU+CPU"
#        self.cpuDevice = "Low"
#        self.cpuThreadsEnable = True
#        self.cpuThreads = "MAX"
        self.bucketRendering = False
        self.bucketResolution = "64x64"
        self.extendedTracing = False
        self.transparencyDepth = 15
        self.internalReflectionDepth = 15
        self.SSSDepth = 15
        self.ClampLevelEnable = False
        self.ClampLevel = 1
        self.ImgTheaFile = False

    def write(self, file):
        '''Write render options parameters

            :param file: file handler
            :type file: file
        '''
        global scn

        from TheaForBlender.thea_render_main import getPresets
        presets = getPresets()

        file.write('<Parameter Name=\"./Cameras/Active\" Type=\"String\" Value=\"%s\"/>\n' % self.activeCamera)

        scn = bpy.context.scene
        self.animationOptions.write(file)
#         thea_globals.log.debug("thea_enablePresets: %s" % getattr(scn, "thea_enablePresets", False))
#         thea_globals.log.debug("thea_RenderPresetsMenu: %s " % getattr(scn, 'thea_RenderPresetsMenu'))
        if getattr(scn, "thea_enablePresets", False):
            if getattr(scn, 'thea_RenderPresetsMenu'):
                p = scn.get('thea_RenderPresetsMenu') - 1
#                 thea_globals.log.debug("presets: %s p: %s" % (presets, p))
#                 thea_globals.log.debug("presets[%s][1]: %s" % (p, presets[p][1]))
                if p < len(presets):
                    if os.path.exists(presets[p][1]):
                        presetsFile = open(presets[p][1])
                        l = 0
                        engine = "Unset"
                        for line in presetsFile:
                            if line.find('Value="Biased"/>')>0 and engine == "Unset":
                                engine = "Biased"
                                line = ""
                            if line.find('Value="Unbiased"/>')>0 and engine == "Unset":
                                engine = "Unbiased"
                                line = ""
    #                         if l > 0 and line[0:7] != "</Root>":
                            if line.startswith("<Parameter"):
                                lr = line.replace('<Parameter Name=\"','<Parameter Name=\"./Render/').replace('Render/.','Render')
    #                             thea_globals.log.debug("line: %s %s %s" % (line, lr.find("./Render/Biased/Engine Core"), engine))
                                if engine == "Biased" and lr.find("./Render/Biased/Engine Core") > 0:
                                    lr = lr.replace("./Render/Biased/Engine Core", "./Render/Engine Core")
                                elif engine == "Uniased" and lr.find("./Render/Unbiased/Engine Core") > 0:
                                    lr = lr.replace("./Render/Unbiased/Engine Core", "./Render/Engine Core").replace("./Render/Biased/Engine Core", "./Render/Engine Core")
                                file.write(lr)
                            l += 1
        else:
            file.write('<Parameter Name=\"./Render/Engine Core\" Type=\"String\" Value=\"%s\"/>\n' % self.engine)
            file.write('<Parameter Name=\"./Render/Interactive/Engine Core\" Type=\"String\" Value=\"%s\"/>\n' % self.interactiveEngine)
#            if self.engine == "AdaptiveBSD":
#                file.write('Adaptive (BSD)')
#            if self.engine == "UnbiasedTR1":
#                file.write('Unbiased (TR1)')
#            if self.engine == "UnbiasedTR1+":
#                file.write('Unbiased (TR1+)')
#            if self.engine == "UnbiasedTR2":
#                file.write('Unbiased (TR2)')
#            if self.engine == "UnbiasedTR2+":
#                file.write('Unbiased (TR2+)')
#             file.write(self.engine)
#             file.write('\"/>\n')
            file.write('<Parameter Name=\"./Render/Supersampling\" Type=\"String\" Value=\"')
            if self.supersampling == "DefaultSS":
                file.write('Default')
            if self.supersampling == "NoneSS":
                file.write('None')
            if self.supersampling == "NormalSS":
                file.write('Normal')
            if self.supersampling == "HighSS":
                file.write('High')
            file.write('\"/>\n')
#            CHNAGED> Added adaptive bias + displacement check
            file.write('<Parameter Name=\"./Render/Adaptive Bias\" Type=\"Real\" Value=\"%s" />\n' % self.adaptiveBias)
            file.write('<Parameter Name=\"./Render/Displacement\" Type=\"Boolean\" Value=\"%s" />\n' % ('1' if self.displacemScene else '0'))
            #file.write('<Parameter Name=\"./Render/Max Passes\" Type=\"Integer\" Value=\"%s\"/>\n' % self.maxPasses)
            file.write('<Parameter Name=\"./Render/Sample Limit\" Type=\"Integer\" Value=\"%s"/>\n' % self.maxSamples)
            file.write('<Parameter Name=\"./Render/Time (min)\" Type=\"Integer\" Value=\"%s\"/>\n' % self.maxRenderTime)
            file.write('<Parameter Name=\"./Render/Motion Blur\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.motionBlur else '0'))
            file.write('<Parameter Name=\"./Render/Volumetric Scattering\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.volumetricScattering else '0'))
            file.write('<Parameter Name=\"./Render/Relight\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.lightBlending else '0'))
#            CHANGED > Added clay render options
            file.write('<Parameter Name=\"./Render/Clay Render/Enable\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.clayrender else '0'))
            file.write('<Parameter Name=\"./Render/Clay Render/Reflectance\" Type=\"Real\" Value=\"%s\"/>\n' % (self.clayrenderreflectance / 100))
            file.write('<Parameter Name=\"./Render/Image Saving\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.imageSaving else '0'))
            file.write('<Parameter Name=\"./Render/Film Saving\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.filmSaving else '0'))
            file.write('<Parameter Name=\"./Render/Threads\" Type=\"String\" Value=\"')
            if self.threads==0:
                file.write('Max')
            else:
                file.write(str(self.threads))
            file.write('\"/>\n')
            if getattr(scn, "thea_distributionRender") != False:
                file.write('<Parameter Name=\"./Render/Priority\" Type=\"String\" Value=\"%s\"/>\n' % ('Low' if int(self.priority)==0 else 'Normal'))
                file.write('<Parameter Name=\"./Render/Network\" Type=\"String\" Value=\"')
                if self.network == "Client":
                    file.write('Client')
                elif self.network == "Server":
                    file.write('Server')
                elif self.network == "Pure Server":
                    file.write('Pure Server')
                else:
                    file.write('None')
                file.write('\"/>\n')
                file.write('<Parameter Name=\"./Render/Server Port\" Type=\"Integer\" Value=\"%s\"/>\n' % self.serverport)
                addr = str(self.serveraddress)
                addr = addr.replace('\'', '')
                file.write('<Parameter Name=\"./Render/Server Address\" Type=\"String\" Value=\"%s\"/>\n' % addr)

            file.write('<Parameter Name=\"./Render/Channels/Color\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.colorChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Normal\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.normalChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Position\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.positionChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/UV\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.uvChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Depth\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.depthChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Alpha\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.alphaChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Object Id\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.objectIdChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Material Id\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.materialIdChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Shadow\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.shadowChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Mask\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.maskChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Raw Diffuse Color\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.rawDiffuseColorChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Raw Diffuse Lighting\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.rawDiffuseLightingChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Raw Diffuse GI\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.rawDiffuseGIChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Self Illumination\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.selfIlluminationChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Direct\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.directChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/AO\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.AOChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/GI\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.giChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/SSS\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.sssChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Reflection\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.reflectionChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Refraction\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.refractionChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Transparent\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.transparentChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Irradiance\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.irradianceChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Separate Passes Per Light\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.separatePassesPerLightChannel else '0'))
            file.write('<Parameter Name=\"./Render/Channels/Invert Mask Channel\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.invertMaskChannel else '0'))

            file.write('<Parameter Name=\"./Render/Tracing Depth\" Type=\"Integer\" Value=\"%s\"/>\n' % self.rayTracingDepth)
            file.write('<Parameter Name=\"./Render/Progressive/Diffuse Depth\" Type=\"Integer\" Value=\"%s\"/>\n' % self.rayDiffuseDepth)
            file.write('<Parameter Name=\"./Render/Glossy Depth\" Type=\"Integer\" Value=\"%s\"/>\n' % self.rayGlossyDepth)
            file.write('<Parameter Name=\"./Render/Trace Reflections\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.rayTraceReflections else '0'))
            file.write('<Parameter Name=\"./Render/Trace Refractions\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.rayTraceRefractions else '0'))
            file.write('<Parameter Name=\"./Render/Trace Transparencies\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.rayTraceTransparencies else '0'))
            file.write('<Parameter Name=\"./Render/Trace Dispersion\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.rayTraceDispersion else '0'))
            file.write('<Parameter Name=\"./Render/Max Contrast\" Type=\"Real\" Value=\"%s\"/>\n' % self.maxContrast)
            file.write('<Parameter Name=\"./Render/Min AA Subdivs\" Type=\"Integer\" Value=\"%s\"/>\n' % self.minAASubdivs)
            file.write('<Parameter Name=\"./Render/Max AA Subdivs\" Type=\"Integer\" Value=\"%s\"/>\n' % self.maxAASubdivs)
            file.write('<Parameter Name=\"./Render/Direct Lighting/Enable\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.directLighting else '0'))
            file.write('<Parameter Name=\"./Render/Perceptual Based\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.perceptualBased else '0'))
            file.write('<Parameter Name=\"./Render/Max Direct Error\" Type=\"Real\" Value=\"%s\"/>\n' % self.maxDirectError)
            file.write('<Parameter Name=\"./Render/Photon Mapping/Enable\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.photonMapping else '0'))
            file.write('<Parameter Name=\"./Render/Field Mapping/Enable\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.FMEnable else '0'))
            file.write('<Parameter Name=\"./Render/Caustics\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.caustics else '0'))
            file.write('<Parameter Name=\"./Render/Field Mapping/Field Density\" Type=\"Integer\" Value=\"%s\"/>\n' % self.FMFieldDensity)
            file.write('<Parameter Name=\"./Render/Field Mapping/Cell Size\" Type=\"Integer\" Value=\"%s\"/>\n' % self.FMCellSize)
            file.write('<Parameter Name=\"./Render/Leak Compensation\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.leakCompensation else '0'))
            file.write('<Parameter Name=\"./Render/Caustics/Sharpening\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.causticSharpening else '0'))
            file.write('<Parameter Name=\"./Render/Subsurface Scattering/Enable\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.subsurfaceScattering else '0'))
            #file.write('<Parameter Name=\"./Render/Photons Captured\" Type=\"Integer\" Value=\"%s\"/>\n' % self.globalPhotonsCaptured)
            file.write('<Parameter Name=\"./Render/Caustics/Captured Photons\" Type=\"Integer\" Value=\"%s\"/>\n' % self.causticPhotonsCaptured)
            #file.write('<Parameter Name=\"./Render/Global Photons\" Type=\"Integer\" Value=\"%s\"/>\n' % self.globalEstimationPhotons)
            file.write('<Parameter Name=\"./Render/Caustics/Estimation Photons\" Type=\"Integer\" Value=\"%s\"/>\n' % self.causticEstimationPhotons)
            file.write('<Parameter Name=\"./Render/Global Radius\" Type=\"Real\" Value=\"%s\"/>\n' % self.globalEstimationRadius)
            file.write('<Parameter Name=\"./Render/Caustic Radius\" Type=\"Real\" Value=\"%s\"/>\n' % self.causticEstimationRadius)
            file.write('<Parameter Name=\"./Render/Gathering/Enable\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.finalGathering else '0'))
            file.write('<Parameter Name=\"./Render/Gathering/Secondary Gather\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.secondaryGather else '0'))
            file.write('<Parameter Name=\"./Render/Gathering/Distance Threshold (m)\" Type=\"Real\" Value=\"%s\"/>\n' % self.distanceThreshold)
            file.write('<Parameter Name=\"./Render/Gathering/Adaptive Steps\" Type=\"Integer\" Value=\"%s\"/>\n' % self.gatherAdaptiveSteps)
            file.write('<Parameter Name=\"./Render/Gathering/Diffuse Depth\" Type=\"Integer\" Value=\"%s\"/>\n' % self.gatherDiffuseDepth)
            file.write('<Parameter Name=\"./Render/Gathering/Tracing Depth\" Type=\"Integer\" Value=\"%s\"/>\n' % self.gatherTracingDepth)
            file.write('<Parameter Name=\"./Render/Gathering/Glossy Depth\" Type=\"Integer\" Value=\"%s\"/>\n' % self.gatherGlossyDepth)
            file.write('<Parameter Name=\"./Render/Gathering/Trace Reflections\" Type=\"Boolean\" Value=\"%s\"/>\n' % self.gatherTraceReflections)
            file.write('<Parameter Name=\"./Render/Gathering/Trace Refractions\" Type=\"Boolean\" Value=\"%s\"/>\n' % self.gatherTraceRefractions)
            file.write('<Parameter Name=\"./Render/Gathering/Trace Transparencies\" Type=\"Boolean\" Value=\"%s\"/>\n' % self.gatherTraceTransparencies)
            file.write('<Parameter Name=\"./Render/Gathering/Glossy Evaluation\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.glossyEvaluation else '0'))
            file.write('<Parameter Name=\"./Render/Gathering/Caustic Evaluation\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.causticEvaluation else '0'))
            file.write('<Parameter Name=\"./Render/Gathering/Samples\" Type=\"Integer\" Value=\"%s\"/>\n' % self.gatherRays)
            file.write('<Parameter Name=\"./Render/Blurred Reflections/Enable\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.blurredReflections else '0'))
            file.write('<Parameter Name=\"./Render/Min Blurred Subdivs\" Type=\"Integer\" Value=\"%s\"/>\n' % self.minBlurredSubdivs)
            file.write('<Parameter Name=\"./Render/Max Blurred Subdivs\" Type=\"Integer\" Value=\"%s\"/>\n' % self.maxBlurredSubdivs)
            file.write('<Parameter Name=\"./Render/IrrCache/Enable\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.ICEnable else '0'))
            file.write('<Parameter Name=\"./Render/IrrCache/Force Interpolation\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.ICForceInterpolation else '0'))
            file.write('<Parameter Name=\"./Render/IrrCache/Prepass Level\" Type=\"String\" Value=\"%s\"/>\n' % self.ICPrepass)
            file.write('<Parameter Name=\"./Render/IrrCache/Sample Density\" Type=\"Real\" Value=\"%s\"/>\n' % self.ICAccuracy)
            file.write('<Parameter Name=\"./Render/IrrCache/Density Boost\" Type=\"Real\" Value=\"%s\"/>\n' % self.ICPrepassBoost)
            file.write('<Parameter Name=\"./Render/IrrCache/Min Distance (px)\" Type=\"Real\" Value=\"%s\"/> \n' % (self.ICMinDistance*100))
            file.write('<Parameter Name=\"./Render/IrrCache/Max Distance (px)\" Type=\"Real\" Value=\"%s\"/> \n' % (self.ICMaxDistance*100))
            file.write('<Parameter Name=\"./Render/Device Mask\" Type=\"String\" Value=\"%s\"/> \n' % self.deviceMask)
#            file.write('<Parameter Name=\"./Device #0/Run Threads\" Type=\"String\" Value="%s"/>\n' % self.renderOptions.cpuThreads)
#            file.write('<Parameter Name=\"./Device #0/Enabled\" Type=\"Boolean\" Value=\"%s"/>\n' % ('1' if self.renderOptions.cpuThreadsEnable else '0'))
#            file.write('<Parameter Name=\"./Device #0/Priority\" Type=\"String\" Value="%s"/>\n' % self.renderOptions.cpuDevice)
            file.write('<Parameter Name=\"./Render/Bucket Rendering\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.bucketRendering else '0'))
            file.write('<Parameter Name=\"./Render/Bucket Resolution\" Type=\"String\" Value=\"%s\"/>\n' % self.bucketResolution)

            file.write('<Parameter Name=\"./Render/Extended Tracing\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.extendedTracing else '0'))
            file.write('<Parameter Name=\"./Render/Progressive/Transparency Depth\" Type=\"Integer\" Value=\"%s\"/>\n' % self.transparencyDepth)
            file.write('<Parameter Name=\"./Render/Progressive/Internal Reflection Depth\" Type=\"Integer\" Value=\"%s\"/>\n' % self.internalReflectionDepth)
            file.write('<Parameter Name=\"./Render/Progressive/SSS Depth\" Type=\"Integer\" Value=\"%s\"/>\n' % self.SSSDepth)
            if self.ClampLevelEnable:
                file.write('<Parameter Name=\"./Render/Clamping/Clamp Radiance\" Type=\"Boolean\" Value=\"%s\"/>\n' % self.ClampLevelEnable)
                file.write('<Parameter Name=\"./Render/Clamping/Clamp Level\" Type=\"Real\" Value=\"%s\"/>\n' % self.ClampLevel)
#            if self.AOEnable:
            file.write('<Parameter Name=\"./Render/Ambient Occlusion/Enable\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.AOEnable else '0'))
            file.write('<Parameter Name=\"./Render/Progressive/Ambient Occlusion/Enable\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.AOEnable else '0'))
            file.write('<Parameter Name=\"./Render/Ambient Occlusion/Multiply\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.AOMultiply else '0'))
            file.write('<Parameter Name=\"./Render/Ambient Occlusion/Clamp\" Type=\"Boolean\" Value=\"%s\"/>\n' % ('1' if self.AOClamp else '0'))
            file.write('<Parameter Name=\"./Render/Ambient Occlusion/Samples\" Type=\"Integer\" Value=\"%s\"/>\n' % self.AOSamples)
            file.write('<Parameter Name=\"./Render/Ambient Occlusion/Distance\" Type=\"Real\" Value=\"%s\"/>\n' % self.AODistance)
            file.write('<Parameter Name=\"./Render/Progressive/Ambient Occlusion/Distance\" Type=\"Real\" Value=\"%s\"/>\n' % self.AODistance)
            file.write('<Parameter Name=\"./Render/Progressive/Ambient Occlusion/Intensity\" Type=\"Real\" Value=\"%s\"/>\n' % self.AOIntensity)
            file.write('<Parameter Name=\"./Render/Ambient Occlusion/Low Color\" Type="RGB" Value="%s %s %s"/>\n' % (self.AOLowColor[0], self.AOLowColor[1],self.AOLowColor[2]))
            file.write('<Parameter Name=\"./Render/Ambient Occlusion/High Color\" Type="RGB" Value="%s %s %s"/>\n' % (self.AOHighColor[0], self.AOHighColor[1],self.AOHighColor[2]))


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Link
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Link:
    '''Link - used to link another xml file
    '''
    def __init__(self):
        self.overrideName = False

    def setName(self, name):
        self.name=name
        self.overrideName = True
    def setFilename(self, filename):
        self.filename = filename

    def write(self, file, identifier):
        '''Write link object

            :param file: file handler
            :type file: file
            :param identifier: identifier
            :type: indentifier: string
        '''
        if self.overrideName:
            file.write('<Link Identifier=\"./%s/%s\" Name=\"%s\" File=\"%s\"/>\n' % (identifier, self.name, self.name, self.filename))
        else:
            file.write('<Link Identifier=\"./%s/\" File=\"%s\"/>\n' % (identifier, self.filename))


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// Package
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class Package:
    '''Package
    '''
    def __init__(self):
        self.frames = []

    def setName(self, name):
        '''Set package name

            :param name: name
            :type: name: string
        '''
        self.name=name
        self.overrideName = True

    def addFrame(self, frame):
        '''Add transform to the transform list

            :param frame: transform
            :type frame: Transform
        '''
        self.frames.append(frame)

    def write(self, file):
        '''Write package object

            :param file: file handler
            :type file: file
        '''
        file.write('<Object Identifier=\"./Models/%s\" Label=\"Model Package\" Name=\"%s\" Type=\"Model\">\n' % (self.name, self.name))
        file.write('<Parameter Name=\"Alias\" Type=\"String\" Value=\"%s\"/>\n' % self.alias)
        file.write('<Parameter Name=\"Position\" Type=\"Transform List\" Value=\"%s\">\n' % len(self.frames))
        for frame in self.frames:
            file.write('<T r=\"%s %s %s %s %s %s %s %s %s %s %s %s\"/>\n' % (frame[0], frame[1], frame[2], frame[3], frame[4], frame[5], frame[6], frame[7], frame[8], frame[9], frame[10], frame[11]))
        file.write('</Parameter>\n')
        file.write('</Object>\n')

class exportObject:
    '''Definiton of the object to be exported
    It contains blenderObject, matrix, name, meshName, isProxy and subobjects list
    '''
    def __init__(self):
        self.blenderObject=None
        self.matrix=[]
        self.name=""
        self.meshName=""
        self.isProxy=False
        self.subobjects=[]

    def __unicode__(self):
        return str(self.name)

def is_Animated(ob):
    '''check if object is animated

        :param ob: object
        :type ob: bpy_types.Object
        :return: is animated
        :rtype: bool
    '''
    anim = ob.animation_data
    animated = False
    if anim is not None and anim.action is not None:
        animated = True
    if ob.parent is not None:
        animated = is_Animated(ob.parent)
    return animated

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#// XML Exporter
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
class XMLExporter:
    '''Main exporter class. It exports whole scene with materials, models, packages, lights, cameras, environment, display and render options
    '''
    global presets

    def __init__(self):
        self.materialList = []
        self.materialLinkList = []
        self.modelList = []
        self.modelFilesList = []
        self.packageList = []
        self.lightList = []
        self.cameraList = []
#        self.GlobalMediumOptions = None
        self.environmentOptions = None
        self.displayOptions = None
        self.renderOptions = None
        self.name = ""

    def addMaterial(self, material):
        self.materialList.append(material)
    def addMaterialLink(self, materialLink):
        self.materialLinkList.append(materialLink)
    def addModel(self, model):
        self.modelList.append(model)
    def addPackage(self, package):
        self.packageList.append(package)
    def addPointLight(self, light):
        self.lightList.append(light)
    def addCamera(self, cam):
        self.cameraList.append(cam)

    def setEnvironmentOptions(self, o):
        self.environmentOptions=o
    def getEnvironmentOptions(self):
        return self.environmentOptions

    def setDisplayOptions(self, o):
        self.displayOptions=o
    def getDisplayOptions(self):
        return self.displayOptions

    def setRenderOptions(self, o):
        self.renderOptions=o
    def getRenderOptions(self):
        return self.renderOptions

    def createFile(self, filename):
        self.file = open(filename, "w")

    def writeHeader(self):
       # // root object is kernel.
       self.file.write('<Root Label=\"Kernel\" Name=\"\" Type=\"Kernel\">\n')
       #// start of scene description.
       self.file.write('<Object Identifier=\"./Scenes/%s\" Label=\"Default Scene\" Name=\"%s\" Type=\"Scene\">\n' % (self.name, self.name))

    def writeFooter(self):
        #// end of scene description.
        self.file.write('</Object>\n')
        #// it is necessary to describe the primary/active modules as there might exist more than one!
        self.file.write('<Parameter Name=\"./Scenes/Active\" Type=\"String\" Value=\"%s\"/>\n' % self.name ) #// scene.
        # CHANGED needs to go after root in order to work
        #// issue a special "parameter command" to generate sun according to given parameters - if settings indicate physical sky.
        #// this special command should be at the very end - after activating scene - to work properly.
        if self.environmentOptions.illumination=="PhysicalSky" and self.environmentOptions.overrideSun == False: # and self.environmentOptions.skyType == "Sun+Sky":
            self.file.write('<Parameter Name=\"GenerateSun\" Type=\"Boolean\" Value=\"1\"/>\n')
        #// end of file.
        self.file.write('</Root>\n')
        # CHANGED needs to go after root in order to work
        #// issue a special "parameter command" to generate sun according to given parameters - if settings indicate physical sky.
        #// this special command should be at the very end - after activating scene - to work properly.
        if self.environmentOptions.illumination=="PhysicalSky" and self.environmentOptions.overrideSun == False: # and self.environmentOptions.skyType == "Sun+Sky":
            self.file.write('<Parameter Name=\"GenerateSun\" Type=\"Boolean\" Value=\"1\"/>\n')
#        self.file.write('</Root>\n')


    def findMaterial(self, name):
        '''find material in materialList

            :param name: material name
            :type name: string
            :return: material key, -1 if not found
            :rtype: int
        '''
        i = -1
        if len(self.materialList) > 0:
            for key, val in enumerate(self.materialList):
                if val.name == name:
                    i = key
        return i

    def findMaterialLink(self, name):
        '''find material link in materialLink List

            :param name: material name
            :type name: string
            :return: material key, -1 if not found
            :rtype: int
        '''
        i = -1
        if len(self.materialLinkList) > 0:
            for key, val in enumerate(self.materialLinkList):
                if val.name == name:
                    i = key
        return i


    def zipFile(self, fileName):
        zipFilename=fileName.replace('.xml','.tzx')
        zipFile = zipfile.ZipFile(zipFilename, 'w', compression=zipfile.ZIP_DEFLATED)
        zipFile.write(fileName, Blender.sys.basename(fileName), zipfile.ZIP_DEFLATED)
        zipFile.close()
        os.remove(fileName)

    def write(self,  fileName, sceneName):
        '''Write xml file with whole scene

            :param fileName: path for the filename to be saved
            :type fileName: string
            :param sceneName: scene name
            :type sceneName: string
        '''
        self.filename=fileName
        self.name=sceneName

        self.createFile(fileName)
        self.writeHeader()
        thea_globals.log.info ("Writting materials")
        for mat in self.materialList:
            mat.write(self.file)

        for link in self.materialLinkList:
            link.write(self.file, "Proxies/Appearance")

        if len(self.modelFilesList) == 0:
            for mod in self.modelList:
                mod.write(self.file)
        else:
            thea_globals.log.info ("Appending model files")
            for obFilename, obName, meshName, obFrame, isInstance in self.modelFilesList:
#                 ##print("obName, meshName, isInstance", obName, meshName, isInstance)
#                 ##print("bpy.data.groups.get(obName.split(:)[0]): ", bpy.data.groups.get(obName.split(":")[0]))
                if isInstance:
                    if( bpy.data.groups.get(obName.split(":")[0])):
#                         if( bpy.data.groups.get(obName.split(":")[0]).library):
                        self.file.write('<Link Identifier=\"./Proxies/Model/%s\" Name=\"%s\" File=\"%s\">\n' % (obName, obName, obFilename))
                    else:
                        self.file.write('<Link Identifier=\"./Proxies/Model/%s\" Name=\"%s\" File=\"%s\">\n' % (obName, meshName, obFilename))
                    #self.file.write('<Link Identifier=\"./Proxies/Model/%s\" Name=\"%s\" File=\"%s\">\n' % (meshName, meshName, obFilename))
                    #self.file.write('<Link Identifier=\"./Proxies/Model/%s\" Name=\"%s\" File=\"%s\">\n' % (obName, obName, obFilename))
                    #self.file.write('<Link Identifier=\"./Proxies/Model/%s\" Name=\"%s\" File=\"%s\">\n' % (meshName, obName, obFilename))

                else:
                    self.file.write('<Link Identifier=\"./Models/%s\" Name=\"%s\" File=\"%s\">\n' % (obName, obName, obFilename))
#                 try:
#                 thea_globals.log.debug("obName: *%s* %s %s" % (obName, bpy.context.scene, bpy.context.scene.objects.get(obName)))
                if bpy.context.scene.objects.get(obName):
                    ob = bpy.context.scene.objects.get(obName)
                    #if scn.objects.get(obName).thEnabled == 0:
#                     thea_globals.log.debug("ob.thEnabled: %s" % ob.thEnabled)
                    if ob.thSectionFrame == False:
                        self.file.write('<Parameter Name=\"Enabled\" Type=\"Boolean\" Value=\"%s\"/>\n' % ob.thEnabled)
                        #if scn.objects.get(obName).thVisible == 0:
                        self.file.write('<Parameter Name=\"Visible\" Type=\"Boolean\" Value=\"%s\"/>\n'% ob.thVisible)
                    else:
                        self.file.write('<Parameter Name=\"Enabled\" Type=\"Boolean\" Value="0"/>\n')
                        self.file.write('<Parameter Name=\"Visible\" Type=\"Boolean\" Value="0"/>\n')
                    #if scn.objects.get(obName).thShadowCaster == 0:
                    self.file.write('<Parameter Name=\"Shadow Caster\" Type=\"Boolean\" Value=\"%s\"/>\n'% ob.thShadowCaster)
                    #if scn.objects.get(obName).thShadowTight == 0:
                    self.file.write('<Parameter Name=\"Shadow Tight\" Type=\"Boolean\" Value=\"%s\"/>\n'% ob.thShadowTight)
                    #if scn.objects.get(obName).thShadowReceiver == 0:
                    self.file.write('<Parameter Name=\"Shadow Receiver\" Type=\"Boolean\" Value=\"%s\"/>\n'% ob.thShadowReceiver)
                    #if scn.objects.get(obName).thCausticsReceiver == 0:
                    self.file.write('<Parameter Name=\"Caustics Receiver\" Type=\"Boolean\" Value=\"%s\"/>\n' % ob.thCausticsReceiver)
                    #if scn.objects.get(obName).thCausticsTransmitter == 0:
                    self.file.write('<Parameter Name=\"Caustics Transmitter\" Type=\"Boolean\" Value=\"%s\"/>\n'% ob.thCausticsTransmitter)
#                    CHANGED> Added Mask ID
                    if ob.thMaskID == True:
                        self.file.write('<Parameter Name=\"Mask Index\" Type=\"Integer\" Value=\"%s\"/>\n'% ob.thMaskIDindex)
                    if ob.thSectionFrame:
                        thea_globals.sectionFrame = True
                        thea_globals.sectionFrameEnabled = True
                        ob.name = "ZClippingPlane"
                        zClipPlane = bpy.data.objects['ZClippingPlane'].matrix_world
#                        obD_mat = obSection
#                        thea_globals.log.debug("Section Frame matrix: %s" % obSection)
                        translist = ()
                        translist = Transform(\
                                    zClipPlane[0][0], zClipPlane[0][1], zClipPlane[0][2],
                                    zClipPlane[1][0], zClipPlane[1][1], zClipPlane[1][2],
                                    zClipPlane[2][0], zClipPlane[2][1], zClipPlane[2][2],
                                    zClipPlane[0][3], zClipPlane[1][3], zClipPlane[2][3])
                    else:
                        thea_globals.sectionFrame = False
#                    thea_globals.log.debug("Section Frame: %s - %s - %s" % (ob, thea_globals.sectionFrame, thea_globals.sectionFrameTrans))

                    if (len(ob.data.materials)<=1) and bpy.context.scene.thea_ExportAnimation == True and (ob.thExportAnimation == True or is_Animated(ob)):
                    #if ob.thExportAnimation == True and bpy.context.scene.thea_ExportAnimation == True:
                        #export animation data
                        obM = ob.matrix_world
#                         obFrame = Transform(\
#                         obM[0][0], -obM[0][1], -obM[0][2],
#                         obM[1][0], -obM[1][1], -obM[1][2],
#                         obM[2][0], -obM[2][1], -obM[2][2],
#                         obM[0][3],  obM[1][3],  obM[2][3])
#
#                         obFrame = Transform(\
#                         obM[0][0], obM[0][1], obM[0][2],
#                         obM[1][0], obM[1][1], obM[1][2],
#                         obM[2][0], obM[2][1], obM[2][2],
#                         obM[0][3],  obM[1][3],  obM[2][3])

#                         startObMatrixAssigned = mathutils.Matrix((\
#                         (obM[0][0], -obM[0][1], -obM[0][2], obM[0][3]),
#                         (obM[1][0], -obM[1][1], -obM[1][2], obM[1][3]),
#                         (obM[2][0], -obM[2][1], -obM[2][2], obM[2][3]),
#                         (0.0, 0.0, 0.0, 1.0)))

                        startObMatrixAssigned = mathutils.Matrix((\
                        (obM[0][0], obM[0][1], obM[0][2], obM[0][3]),
                        (obM[1][0], obM[1][1], obM[1][2], obM[1][3]),
                        (obM[2][0], obM[2][1], obM[2][2], obM[2][3]),
                        (0.0, 0.0, 0.0, 1.0)))

                        obMInverted = ob.matrix_world.inverted()
                        currFrame = bpy.context.scene.frame_current
                        startFrame = bpy.context.scene.frame_start
                        endFrame = bpy.context.scene.frame_end
                        im = InterpolatedMotion()
                        im.enabled = True
                        im.duration = endFrame+1-startFrame
                        bpy.context.scene.frame_set(startFrame)
                        prevObM = ob.matrix_world
                        if(bpy.context.scene.get('thea_AnimationEveryFrame')):
                            tolerance = 0
                        else:
                            tolerance = 10**-5
                        for frame in range(startFrame, endFrame+1, 1):
                            print ("\n\nExporting animation frame %s for object %s: " % (frame, obName))
                            bpy.context.scene.frame_set(frame)
                            obM = ob.matrix_world
#                             ob_matrix_world_Assigned = mathutils.Matrix((\
#                             (obM[0][0], -obM[0][1], -obM[0][2], obM[0][3]),
#                             (obM[1][0], -obM[1][1], -obM[1][2], obM[1][3]),
#                             (obM[2][0], -obM[2][1], -obM[2][2], obM[2][3]),
#                             (0.0, 0.0, 0.0, 1.0)))
                            ###print(obM)
                            sum = 0
                            for v in (prevObM-obM):
                                for i in v:
                                    sum += abs(i)
                            ###print(sum*100000000000000)

                            #if((obM != prevObM) or (frame == startFrame)):
                            if((sum>tolerance) or (frame == startFrame)):
                                ob_matrix_world_Assigned = mathutils.Matrix((\
                                (obM[0][0], obM[0][1], obM[0][2], obM[0][3]),
                                (obM[1][0], obM[1][1], obM[1][2], obM[1][3]),
                                (obM[2][0], obM[2][1], obM[2][2], obM[2][3]),
                                (0.0, 0.0, 0.0, 1.0)))

                                obM = startObMatrixAssigned.inverted() * ob_matrix_world_Assigned
                                frame = Transform(\
                                obM[0][0], obM[0][1], obM[0][2],
                                obM[1][0], obM[1][1], obM[1][2],
                                obM[2][0], obM[2][1], obM[2][2],
                                obM[0][3], obM[1][3], obM[2][3])
                                im.addNode(bpy.context.scene.frame_current, frame)
                            else:
                                thea_globals.log.debug("****no transform change on this frame")
                            prevObM = ob.matrix_world * 1.0
                        bpy.context.scene.frame_set(currFrame)
                        im.write(self.file)
#                 except:
#                     pass
                obFrame.write(self.file, identifier="Group Frame")
                self.file.write('</Link>\n')

        thea_globals.log.info ("Writting packages")
        for pkg in self.packageList:
            pkg.write(self.file)

        thea_globals.log.info ("Writting lights")
        for lit in self.lightList:
            lit.write(self.file)

        thea_globals.log.info ("Writting cameras")
        for cam in self.cameraList:
            cam.write(self.file)

#CHANGED > Added write GLobal Medium Options
#        thea_globals.log.info("Writting Global Mediuam options")
#        self.GlobalMediumOptions.write(self.file);

        thea_globals.log.info("Writting environment options")
        self.environmentOptions.write(self.file);

        thea_globals.log.info("Writting display options")
        self.displayOptions.write(self.file);

        thea_globals.log.info("Writting render options")
        self.renderOptions.write(self.file);

        thea_globals.log.debug("Writting footer")
        self.writeFooter();

        thea_globals.log.debug("Closing file")
        self.file.close()

    def mesh_triangulate(self, mesh):
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()

    def get_materials(self, mesh):
        materials = [0] * len(mesh.materials)
        materials_dict = {}

        for p in mesh.polygons:
            materials[p.material_index] += 1
        i = 0
        for m in materials:
            if m > 0:
                materials_dict[i] = {"name":mesh.materials[i].name, "face_count":m}
            i+=1
        return materials_dict

#    def writeModel(self, model, frame):
        '''write xml model, not used currently
        '''
        global exportPath
        frameS= "0000" + str(frame)
        tempDir = exportPath+"~thexport"
        if not os.path.isdir(tempDir):
            os.mkdir(tempDir)
        modelFilename = os.path.basename(currentBlendFile.replace('.blend', "."+model.name+'.xml'))
        self.modelFilesList.append(os.path.join(tempDir,modelFilename))
        modelFile = open(os.path.join(tempDir,modelFilename), "wb")
        model.write(modelFile)

#    def writeModelBinary(self, scn, expOb, frame, anim):
#        '''write model using binary mesh.thea format
#
#            :param scn: Blender scene
#            :type: scn: bpy_types.Scene
#            :param expOb: object to export
#            :type expOb: exportObject
#            :param frame: transformation matrix
#            :type frame: Transform
#            :param anim: is object animated
#            :type anim: bool
#        '''
#        from TheaForBlender.thea_render_main import getMatTransTable, setPaths
#
##         def mesh_triangulate(me):
##             import bmesh
##             bm = bmesh.new()
##             bm.from_mesh(me)
##             bmesh.ops.triangulate(bm, faces=bm.faces)
##             bm.to_mesh(me)
##             bm.free()
#
#        t1 = time.time()
#
#
#        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scn)
#
#        t2 = time.time()
##         thea_globals.log.debug("*t2-t1: %s" % (t2-t1))
#
#        matTransTable = getMatTransTable()
#
##         thea_globals.log.debug("ob: %s %s" % (expOb.name, expOb.blenderObject.name))
#
#
#        frameS= "0000" + str(frame)
#        tempDir = os.path.join(exportPath,"~thexport")
#        if not os.path.isdir(tempDir):
#            os.mkdir(tempDir)
#        if anim:
#            framesDir = os.path.join(tempDir,"frames")
#            if not os.path.isdir(framesDir):
#                os.mkdir(framesDir)
#        objects = []
#        exportedObjects = []
#        subObjects = False
#        if len(expOb.subobjects) > 0:
#            objects = expOb.subobjects
#            subObjects = True
#        else:
#            objects.append(expOb)
#
#
#        ##print("objects: ", len(objects), expOb.name)
#
#        for ob in objects:
##             ##print("ob: ", ob)
#            if(ob.blenderObject is None):
#                return
#            if getattr(ob.blenderObject, 'library'):
#            #if ob.blenderObject.library:
#                libObject = True
#                obName = ob.name
#                #obFileName = ob.meshName
##                 obFileName = ob.name.replace(":","_").replace("_\\",":\\")
#                obFileName = obName.replace(":","_").replace("_\\",":\\")
##                 obFileName = "".join([ c if c.isalnum() else "_" for c in obFileName ])
#                obFileName = re.sub('[^0-9a-zA-Z]+', '_', obFileName)
#                if anim:
##                    modelGroupFilename = os.path.basename(ob.blenderObject.library.filepath.replace('.blend', '_f'+frameS[-4:]))+"."+obFileName+".xml"
#                   modelGroupFilename = os.path.basename(ob.blenderObject.library.filepath.replace('.blend', '_f'+frameS[-4:]))+"."+os.path.basename(obFileName)+".xml"
#                else:
#                    modelGroupFilename = os.path.basename(ob.blenderObject.library.filepath.replace('.blend', "."+obFileName+'.xml'))
#            else:
#                obFileName = ob.meshName.replace(":","_").replace("_\\",":\\")
##                 obFileName = "".join([ c if c.isalnum() else "_" for c in obFileName ])
#                obFileName = re.sub('[^0-9a-zA-Z]+', '_', obFileName)
#                if anim:
#                   modelGroupFilename = os.path.basename(currentBlendFile.replace('.blend', '_f'+frameS[-4:]+"."+obFileName+'.xml'))
#                else:
#                    modelGroupFilename = os.path.basename(currentBlendFile.replace('.blend', "."+obFileName+'.xml'))
#                libObject = False
#                obName = ob.name#[3]
##                 obName = "".join([ c if c.isalnum() else "_" for c in obName ])
##                 obName = re.sub('[^0-9a-zA-Z]+', '_', obName)
#
#
#
#            object = ob.blenderObject
#            exportModel = Model()
##             exportModel.name = re.sub('[^0-9a-zA-Z]+', '_', ob.name)
#            exportModel.name = ob.name
#
#            obD_mat = ob.matrix
#            exportModel.frame = Transform(
#            obD_mat[0][0], obD_mat[0][1], obD_mat[0][2],
#            obD_mat[1][0], obD_mat[1][1], obD_mat[1][2],
#            obD_mat[2][0], obD_mat[2][1], obD_mat[2][2],
#            obD_mat[0][3], obD_mat[1][3], obD_mat[2][3])
#
#            t3 = time.time()
##             thea_globals.log.debug("*t3-t2: %s" % (t3-t2))
#
#            try:
#                if ob.blenderObject["thAnimated"]:
#                    animatedMesh = True
#                else:
#                    animatedMesh = False
#            except:
#                    animatedMesh = False
#
#            if (scn.thea_Reuse == 0):
#                if anim:
#                    if animatedMesh:
#                      exportGeometry = True
#                    else:
#                      exportGeometry = False
#                else:
#                    exportGeometry = True
#            elif animatedMesh:
#                exportGeometry = True
#            else:
#                exportGeometry = False
#
#            if not exportGeometry and thea_globals.forceExportGeometry:
#                exportGeometry = True
#
#            if exportGeometry:
#                mesh = ob.blenderObject.to_mesh(scn,True, 'RENDER',calc_tessface=True)
#            else:
#                mesh = ob.blenderObject.data
#
#            if mesh is None:
#                mesh = ob.blenderObject.data
#                exportGeometry = False
#
##             thea_globals.log.debug("mesh %s" % mesh.name)
#
#            t4 = time.time()
##             thea_globals.log.debug("*t4-t3: %s" % (t4-t3))
#
#
#
##             mesh.update(calc_tessface=True)
#            try:
#                if object.get('thNoRecalcNormals'):
#                    thea_globals.log.debug("Normal recalculation is disabled for this object!")
#
#                else:
##                    mesh.calc_normals_split()
#                    thea_globals.log.debug("Normal recalculation is ON for this object!")
##                 mesh.calc_normals()
#            except:
#                pass
#
#
#            try:
#                meshMaterials = mesh.materials
#            except:
#                meshMaterials = False
#
#
#            t5 = time.time()
##             thea_globals.log.debug("*t5-t4: %s" % (t5-t4))
#
#            if meshMaterials:
#
#                try:
#                    exportModel.materialName = meshMaterials[0].name
#                except:
#                    exportModel.materialName = "--None--"
#
#                from . import thea_render_main
#                lut = thea_render_main.getLUTarray()
#                for mat in meshMaterials:
#                    if mat:
#                        matName = mat.name
#                        madeLink = False
#                        if thea_globals.getUseLUT():#getattr(scn, 'thea_useLUT'):
#                            for trMat in matTransTable:
#                                t11 = time.time()
#                                try:
#                                    if thea_globals.getNameBasedLUT():
#                                        if trMat[0] == matName and (self.findMaterialLink(matName) < 0):
#                                            matLink = Link()
#                                            matLink.setName(trMat[0])
#                                            matLink.setFilename(trMat[1])
#                                            self.addMaterialLink(matLink)
#                                            madeLink = True
#                                    else:
#                                        if int(getattr(bpy.data.materials.get(matName), 'thea_LUT', 0)) > 0:
#                                            pass
#                                            if trMat[0] == lut[int(getattr(bpy.data.materials.get(matName), 'thea_LUT', 0))] and (self.findMaterialLink(matName) < 0):
#                                                matLink = Link()
#                                                matLink.setName(matName)
#                                                matLink.setFilename(trMat[1])
#                                                self.addMaterialLink(matLink)
#                                                madeLink = True
#                                    t12 = time.time()
##                                     thea_globals.log.debug("**t12-t11: %s" % (t12-t11))
#                                except:
#                                    emptyMat = True
#                        try:
#                            ##print("mat['thea_extMat']: ", mat['thea_extMat'], os.path.exists(os.path.abspath(bpy.path.abspath(mat['thea_extMat']))))
#                            #os.path.abspath(bpy.path.abspath(extMatFile)
#
#                            if os.path.exists(os.path.abspath(bpy.path.abspath(mat['thea_extMat']))) and (self.findMaterialLink(matName) < 0):
#                                matLink = Link()
#                                matLink.setName(matName)
#                                matLink.setFilename(os.path.abspath(bpy.path.abspath(mat['thea_extMat'])))
#                                self.addMaterialLink(matLink)
#                                madeLink = True
#                        except: pass
#
#
#
#                        if mat and (self.findMaterial(matName) < 0):
#                            ma = ThMaterial()
#                            ma.setName(matName)
#                            if madeLink:
#                                ma.link = True
#                            self.addMaterial(ma)
#                            self.materialList[self.findMaterial(matName)].blenderMat = mat
#                    else:
#                        #print("====Missing material for object %s. Object won't be exported!=====" % obName)
#                        scn['thea_Warning'] = ("Missing material for object %s" % obName)
#                        return
#            else:
#                #print("====No material assigned to object. Assigning basic_gray material====")
#                matName = "basic_gray"
#                ma = ThMaterial()
#                ma.setName(matName)
#                self.addMaterial(ma)
#                if(bpy.data.materials.get(matName)):
#                    mesh.materials.append(bpy.data.materials.get(matName))
#                else:
#                    bpy.data.materials.new(name=matName)
#                    mesh.materials.append(bpy.data.materials.get(matName))
#                self.materialList[self.findMaterial(matName)].blenderMat = bpy.data.materials.get(matName)
#                meshMaterials = mesh.materials
#
#
#            t6 = time.time()
##             thea_globals.log.debug("*t6-t5: %s" % (t6-t5))
#
#
#            materials_dict = {}
#
#
#
#
##             thea_globals.log.debug("exportGeometry1: %s" % exportGeometry)
#
#            uvLayer = None
#            meshUVs = []
#            modelUVs = []
#            uvNums = []
#            if exportGeometry:
#                if len(getattr(mesh, 'uv_layers', []))>0:
#                    for uvLayer in mesh.tessface_uv_textures:
#                        meshUV = []
#                        for uv in uvLayer.data:
#                            meshUV.append(uv.uv)
#                        meshUVs.append(meshUV)
#                        uvNums.append(0)
#                        modelUVs.append([])
#                ##print("modelUVs: ", modelUVs)
#                ##print("meshUVs: ", meshUVs)
#
#                try:
#                    uvLayer = mesh.tessface_uv_textures.active.data
#                except:
#                    pass
#                meshUV = []
#
#                if uvLayer:
#                    for uv in uvLayer:
#                            meshUV.append(uv.uv)
#                    ##print("meshUV: ", meshUV)
#
##             thea_globals.log.debug("*modelUVs: %s" % modelUVs)
#
#            t7 = time.time()
##             thea_globals.log.debug("*t7-t6: %s" % (t7-t6))
#
#
#            if exportGeometry:
#                for face in mesh.tessfaces:
#                        if len(meshMaterials):
#                            if face.material_index >= len(meshMaterials):
#                                materialName = None
#                            else:
#                                materialName = meshMaterials[face.material_index].name
#
#                                matKey = self.findMaterial(materialName)
#                                try:
#                                    materials_dict[matKey].append(face)
#                                except:
#                                    materials_dict[matKey] = [face]
##             else: #if we don't export geometry we don't really need loop over faces to get materials list.
#            for mat in mesh.materials:
#                matKey = self.findMaterial(mat.name)
#                if matKey not in materials_dict:
#                    materials_dict[matKey] = []
#
#
##             thea_globals.log.debug("materials_dict: %s" % materials_dict)
#
#            t8 = time.time()
##             thea_globals.log.debug("*t8-t7: %s" % (t8-t7))
#            #search if mesh is already exported
#            if anim:
#                filePath = os.path.join(framesDir,modelGroupFilename)
#            else:
#                filePath = os.path.join(tempDir,modelGroupFilename)
#            if ob.isProxy == True: #is instance
#                filePath = filePath.replace(".xml", "_proxy.xml")
#
#            filePath=filePath.replace(":","_").replace("_\\",":\\")
#
#
#            isInstance = ob.isProxy#[5]
#
#            for obFilenameL, obNameL, meshName, obFrameL, isInstance in self.modelFilesList:
#                if obFilenameL == filePath:
#                    exportGeometry = False
#
#            if subObjects:
#                exportedObjects.append((obName, filePath, exportModel.frame))
#            else:
#                self.modelFilesList.append((filePath,obName,ob.meshName, exportModel.frame, ob.isProxy))
#
#            modelGroupFile = open(filePath, "w")
#
#            if ob.isProxy: #if proxy
#                modelGroupFile.write('<Object Identifier=\"./Proxies/Model/%s\" Label=\"Model\" Name=\"%s\" Type=\"Model\">\n' % (obName, obName))
##                modelGroupFile.write('<Parameter Name=\"Smoothing Angle\" Type=\"Real\" Value=\"%s\"/>\n' % (round (180 * mesh.auto_smooth_angle) / 3.14159265359))
#            else:
#                modelGroupFile.write('<Object Identifier=\"./Models/%s\" Label=\"Model\" Name=\"%s\" Type=\"Model\">\n' % (obName, obName))
##                modelGroupFile.write('<Parameter Name=\"Smoothing Angle\" Type=\"Real\" Value=\"%s\"/>\n' % (round (180 * mesh.auto_smooth_angle) / 3.14159265359))
#
#            if thea_globals.forceExportGeometry:
#                exportGeometry = True
#
##             thea_globals.log.debug("exportGeometry2: %s, force: %s" % (exportGeometry, thea_globals.forceExportGeometry))
#
#            for matKey, matFaces in materials_dict.items():
#                currMatName = re.sub('[^0-9a-zA-Z]+', '_', self.materialList[matKey].name)
#                if animatedMesh:
#                   if ob.blenderObject.library:
#                       modelFilename = os.path.basename(ob.blenderObject.library.filepath.replace('.blend', '_f'+frameS[-4:]))+"."+os.path.basename(obFileName)+"_"+currMatName+'.mesh.thea'
#                   else:
#                       modelFilename = os.path.basename(currentBlendFile.replace('.blend', '_f'+frameS[-4:]+"."+obFileName+"_"+currMatName+'.mesh.thea'))
#                else:
#                    modelFilename = os.path.basename(currentBlendFile.replace('.blend', "."+obFileName+"_"+currMatName+'.mesh.thea'))
#                if len(materials_dict) > 1:
#                    modelGroupFile.write('<Object Identifier=\"./Models/%s\" Label=\"Model\" Name=\"%s (%s)\" Type=\"Model\">\n' % (obName, obName,currMatName))
##                    modelGroupFile.write('<Parameter Name=\"Smoothing Angle\" Type=\"Real\" Value=\"%s"/>\n' % mesh.auto_smoothing_angle)
##                    modelGroupFile.write('<Parameter Name=\"Smoothing Angle\" Type=\"Real\" Value=\"90"/>\n')
#                if anim and animatedMesh:
#                    modelPath = os.path.join(framesDir,modelFilename)
#                else:
#                    modelPath = os.path.join(tempDir,modelFilename)
#                modelPath = modelPath.replace(":","_").replace("_\\",":\\")
#
#                modelGroupFile.write('<Link Identifier=\"Triangular Mesh\" Name=\"\" File=\"%s\"/>\n' % modelPath)
##                modelGroupFile.write('<Parameter Name=\"Smoothing Angle\" Type=\"Real\" Value=\"%s"/>\n' % mesh.auto_smoothing_angle)
#                modelGroupFile.write('<Parameter Name=\"Appearance\" Type=\"String\" Value=\"%s\"/>\n' % self.materialList[matKey].name)
##               CHANGED > Added model properties if mesh is group, problem is all objects in the mesh group will get this. There is no workaournd or seperate the mesh which needs to have the property settings. But now it works in the whole group. In studio when you apply these settings everything in the group gets them, unless you uncheck the individually later. Perhaps this option should go to mesh object as well??? But you cant apply this per mesh object cause they all get the same name + material name as mesh.
#                if bpy.context.scene.objects.get(obName):
#                    modProp = bpy.context.scene.objects.get(obName)
#                    modelGroupFile.write('<Parameter Name=\"Enabled\" Type=\"Boolean\" Value=\"%s\"/>\n' % modProp.thEnabled)
#                    modelGroupFile.write('<Parameter Name=\"Visible\" Type=\"Boolean\" Value=\"%s\"/>\n'% modProp.thVisible)
#                    modelGroupFile.write('<Parameter Name=\"Shadow Caster\" Type=\"Boolean\" Value=\"%s\"/>\n'% modProp.thShadowCaster)
#                    modelGroupFile.write('<Parameter Name=\"Shadow Tight\" Type=\"Boolean\" Value=\"%s\"/>\n'% modProp.thShadowTight)
##                    print("CHeck Shadow Tight", modProp.thShadowTight)
##                    print("CHeck Shadow CAster", modProp.thShadowCaster)
#                    modelGroupFile.write('<Parameter Name=\"Shadow Receiver\" Type=\"Boolean\" Value=\"%s\"/>\n'% modProp.thShadowReceiver)
#                    modelGroupFile.write('<Parameter Name=\"Caustics Receiver\" Type=\"Boolean\" Value=\"%s\"/>\n' % modProp.thCausticsReceiver)
#                    modelGroupFile.write('<Parameter Name=\"Caustics Transmitter\" Type=\"Boolean\" Value=\"%s\"/>\n'% modProp.thCausticsTransmitter)
#                    modelGroupFile.write('<Parameter Name=\"Mask Index\" Type=\"Boolean\" Value=\"%s\"/>\n'% modProp.thMaskID)
#                else:
#                    pass
#
#                if ob.blenderObject.thExportAnimation == True and bpy.context.scene.thea_ExportAnimation == True:
#                        #export animation data
#                        obM = ob.blenderObject.matrix_world
#                        obFrame = Transform(\
#                        obM[0][0], -obM[0][1], -obM[0][2],
#                        obM[1][0], -obM[1][1], -obM[1][2],
#                        obM[2][0], -obM[2][1], -obM[2][2],
#                        obM[0][3],  obM[1][3],  obM[2][3])
#
#
#
##                         startObMatrixAssigned = mathutils.Matrix((\
##                         (obM[0][0], -obM[0][1], -obM[0][2], obM[0][3]),
##                         (obM[1][0], -obM[1][1], -obM[1][2], obM[1][3]),
##                         (obM[2][0], -obM[2][1], -obM[2][2], obM[2][3]),
##                         (0.0, 0.0, 0.0, 1.0)))
#
#                        startObMatrixAssigned = mathutils.Matrix((\
#                        (obM[0][0], obM[0][1], obM[0][2], obM[0][3]),
#                        (obM[1][0], obM[1][1], obM[1][2], obM[1][3]),
#                        (obM[2][0], obM[2][1], obM[2][2], obM[2][3]),
#                        (0.0, 0.0, 0.0, 1.0)))
#
#                        obMInverted = ob.blenderObject.matrix_world.inverted()
#                        currFrame = bpy.context.scene.frame_current
#                        startFrame = bpy.context.scene.frame_start
#                        endFrame = bpy.context.scene.frame_end
#                        im = InterpolatedMotion()
#                        im.enabled = True
#                        im.duration = endFrame+1-startFrame
#                        bpy.context.scene.frame_set(startFrame)
#                        prevObM = ob.blenderObject.matrix_world
#                        if(bpy.context.scene.get('thea_AnimationEveryFrame')):
#                            tolerance = 0
#                        else:
#                            tolerance = 10**-5
#                        for frame in range(startFrame, endFrame+1, 1):
#                            print ("\n\nExporting animation frame %s for mesh object %s: " % (frame, obName))
#                            bpy.context.scene.frame_set(frame)
#                            obM = ob.blenderObject.matrix_world
##                             ob_matrix_world_Assigned = mathutils.Matrix((\
##                             (obM[0][0], -obM[0][1], -obM[0][2], obM[0][3]),
##                             (obM[1][0], -obM[1][1], -obM[1][2], obM[1][3]),
##                             (obM[2][0], -obM[2][1], -obM[2][2], obM[2][3]),
##                             (0.0, 0.0, 0.0, 1.0)))
#                            sum = 0
#                            for v in (prevObM-obM):
#                                for i in v:
#                                    sum += abs(i)
#                            ##print(sum*100000000000000)
#
#                            #if((obM != prevObM) or (frame == startFrame)):
#                            if((sum>tolerance) or (frame == startFrame)):
#                            #if((obM != prevObM) or (frame == startFrame)):
#                                ob_matrix_world_Assigned = mathutils.Matrix((\
#                                (obM[0][0], obM[0][1], obM[0][2], obM[0][3]),
#                                (obM[1][0], obM[1][1], obM[1][2], obM[1][3]),
#                                (obM[2][0], obM[2][1], obM[2][2], obM[2][3]),
#                                (0.0, 0.0, 0.0, 1.0)))
#
#                                obM = startObMatrixAssigned.inverted() * ob_matrix_world_Assigned
#                                frame = Transform(\
#                                obM[0][0], obM[0][1], obM[0][2],
#                                obM[1][0], obM[1][1], obM[1][2],
#                                obM[2][0], obM[2][1], obM[2][2],
#                                obM[0][3], obM[1][3], obM[2][3])
#                                im.addNode(bpy.context.scene.frame_current, frame)
#                            else:
#                                thea_globals.log.debug("****no transform change on this frame")
#                            prevObM = ob.blenderObject.matrix_world * 1.0
#                        bpy.context.scene.frame_set(currFrame)
#                        im.write(modelGroupFile)
#
#                #obFrame.write(self.file, identifier="Group Frame")
#
#
#                if getattr(object, 'thea_Container') != "None":
#                    matInterface = getattr(object, 'thea_Container')
#                    modelGroupFile.write('<Parameter Name=\"Interface Appearance\" Type=\"String\" Value=\"%s\"/>\n' % matInterface)
#                else:
#                    matInterface = False
#
#
#                t9 = time.time()
##                 thea_globals.log.debug("*t9-t8: %s" % (t9-t8))
#
##                 thea_globals.log.debug("matFaces: %s %s" % (matFaces, len(matFaces)))
#                if exportGeometry and len(matFaces) > 0: #if we should export geometry too
#
#
#
#                    vertexNum = 0
#                    normalNum = 0
#                    faceNum = 0
#                    uvNum = 0
#                    modelP = []
#                    modelN = []
#                    modelF = []
#                    modelU = []
#                    modelV = []
#                    modelNN = []
#                    meshV = []
#                    vertN = []
#
#                    modelUVs = []
#                    if exportGeometry:
#                        if len(mesh.uv_layers)>0:
#                            for uvLayer in mesh.tessface_uv_textures:
#                                modelUVs.append([])
#
#                    for v in mesh.vertices:
#                        meshV.append(v.co)
#                        vertN.append(v.normal)
#
#                    for face in matFaces:
##                         thea_globals.log.debug("face.use_smooth: %s" % face.use_smooth)
#                        fIdx = face.index
#                        if len(face.vertices) >= 3:
#                            vi = []
#                            for vert in face.vertices:
#                                 vi.append(vert)
#                            for vert in [0,1,2]:
#                                 idx=vi[vert]
#                                 modelP.append(meshV[idx][0])
#                                 modelP.append(meshV[idx][1])
#                                 modelP.append(meshV[idx][2])
#                                 if face.use_smooth:
#                                    modelN.append(vertN[idx][0])
#                                    modelN.append(vertN[idx][1])
#                                    modelN.append(vertN[idx][2])
#                                 else:
#                                    faceNormal = face.normal
#                                    modelN.append(faceNormal[0])
#                                    modelN.append(faceNormal[1])
#                                    modelN.append(faceNormal[2])
#                            vertexNum += 3
#                            normalNum += 3
#                            modelF.append(vertexNum-3)
#                            modelF.append(vertexNum-2)
#                            modelF.append(vertexNum-1)
#                            faceNum += 1
#
#
#                            if len(meshUVs)>1:
#                                n = 0
#                                for mUV in meshUVs:
#                                    ##print("mUV: ", mUV)
#                                    ##print("mUV[fIdx][0][0]: ", mUV[fIdx])
#                                    modelUVs[n].append(mUV[fIdx][0][0])
#                                    modelUVs[n].append(1.0-mUV[fIdx][0][1])
#                                    modelUVs[n].append(mUV[fIdx][1][0])
#                                    modelUVs[n].append(1.0-mUV[fIdx][1][1])
#                                    modelUVs[n].append(mUV[fIdx][2][0])
#                                    modelUVs[n].append(1.0-mUV[fIdx][2][1])
#                                    uvNums[n] += 3
#                                    n+=1
#                            else:
#                                if uvLayer:
#                                    ##print("meshUV[fIdx]: ", meshUV[fIdx])
#                                    modelU.append(meshUV[fIdx][0][0])
#                                    modelU.append(1.0-meshUV[fIdx][0][1])
#                                    modelU.append(meshUV[fIdx][1][0])
#                                    modelU.append(1.0-meshUV[fIdx][1][1])
#                                    modelU.append(meshUV[fIdx][2][0])
#                                    modelU.append(1.0-meshUV[fIdx][2][1])
#                                    uvNum += 3
#
#                            if len(face.vertices) == 4:
#                                ##print("**********************4 faces ******************")
#                                vi = []
#                                for vert in face.vertices:
#                                     vi.append(vert)
#                                for vert in [0,2,3]:
#                                     idx=vi[vert]
#                                     modelP.append(meshV[idx][0])
#                                     modelP.append(meshV[idx][1])
#                                     modelP.append(meshV[idx][2])
#                                     if face.use_smooth:
#                                        modelN.append(vertN[idx][0])
#                                        modelN.append(vertN[idx][1])
#                                        modelN.append(vertN[idx][2])
#                                     else:
#                                        faceNormal = face.normal
#                                        modelN.append(faceNormal[0])
#                                        modelN.append(faceNormal[1])
#                                        modelN.append(faceNormal[2])
#                                vertexNum += 3
#                                normalNum += 3
#                                modelF.append(vertexNum-3)
#                                modelF.append(vertexNum-2)
#                                modelF.append(vertexNum-1)
#                                faceNum += 1
#
#
#                                if len(meshUVs)>1:
#                                    n = 0
#                                    for mUV in meshUVs:
#                                        modelUVs[n].append(mUV[fIdx][0][0])
#                                        modelUVs[n].append(1.0-mUV[fIdx][0][1])
#                                        modelUVs[n].append(mUV[fIdx][2][0])
#                                        modelUVs[n].append(1.0-mUV[fIdx][2][1])
#                                        modelUVs[n].append(mUV[fIdx][3][0])
#                                        modelUVs[n].append(1.0-mUV[fIdx][3][1])
#                                        uvNums[n] += 3
#                                        n+=1
#                                else:
#                                    if uvLayer:
#                                        modelU.append(meshUV[fIdx][0][0])
#                                        modelU.append(1.0-meshUV[fIdx][0][1])
#                                        modelU.append(meshUV[fIdx][2][0])
#                                        modelU.append(1.0-meshUV[fIdx][2][1])
#                                        modelU.append(meshUV[fIdx][3][0])
#                                        modelU.append(1.0-meshUV[fIdx][3][1])
#                                        uvNum += 3
#
##                     thea_globals.log.debug("*modelUVs: %s" % modelUVs)
##                     thea_globals.log.debug("*modelU: %s" % modelU)
#
#                    modelFile = open(modelPath, "wb")
##                     magicHeader = 0x54524d01
#                    if len(modelUVs)>1 :
#                        magicHeader = 0x54524d02
#                    else:
#                        magicHeader = 0x54524d01
#
#                    modelFile.write(struct.pack('<l',magicHeader))
#
#                    vertexCount = len(modelP)
#                    if vertexCount > 0:
#                        modelFile.write(struct.pack('<l',int(vertexCount/3)))
#                        modelFile.write(struct.pack("<%df" % (vertexCount), *modelP))
#
#                    normalCount = len(modelN)
#                    if normalCount > 0:
#                        modelFile.write(struct.pack('<l',int(normalCount/3)))
#                        modelFile.write(struct.pack("<%df" % (normalCount), *modelN))
#
#                    triangleCount = len(modelF)
#                    if triangleCount > 0:
#                        modelFile.write(struct.pack('<l',int(triangleCount/3)))
#                        modelFile.write(struct.pack("<%dl" % (triangleCount), *modelF))
#
##                     print("vertexCount: ", vertexCount)
##                     print("normalCount: ", normalCount)
##                     print("triangleCount: ", triangleCount)
#
##                     if vertexCount > 0:
##                     #print("len(meshUVs): ", len(meshUVs))
#                    if len(meshUVs)>1:
#                        modelFile.write(struct.pack('<l',len(modelUVs)))
#                        for modelU in modelUVs:
##                             #print("#########modelU: ", modelU)
#                            uvCount = len(modelU)
##                             #print("uvCount: ", uvCount)
#                            modelFile.write(struct.pack('<l',int(uvCount/2)))
#                            modelFile.write(struct.pack("<%df" % (uvCount), *modelU))
#                    else:
#                        # #                     #print("modelU: ", modelU)
#                        uvCount = len(modelU)
##                         #print("uvCount: ", uvCount)
#                        if vertexCount > 0:
#                            modelFile.write(struct.pack('<l',int(uvCount/2)))
#                            modelFile.write(struct.pack("<%df" % (uvCount), *modelU))
#                    modelFile.write(struct.pack('<l',0))
#
#
#
#                    modelFile.close()
##
#                    if len(materials_dict) > 1:
#                        modelGroupFile.write('</Object>\n')
#                elif exportGeometry: # just create empty file if there are no faces for the material
#                    modelFile = open(modelPath, "wb")
#                    magicHeader = 0x54524d01
#                    modelFile.write(struct.pack('<l',magicHeader))
#                    modelFile.write(struct.pack('<l',0))
#                    modelFile.write(struct.pack('<l',0))
#                    modelFile.write(struct.pack('<l',0))
#                    modelFile.write(struct.pack('<l',0))
#                    modelFile.close()
#
#            if exportGeometry:
#                bpy.data.meshes.remove(mesh)
#                del(mesh)
#
#            t10 = time.time()
##             thea_globals.log.debug("*t10-t9: %s" % (t10-t9))
#
#            i = 0
#            for layer in object.layers:
#               if layer:
#                   if i>9:
#                       modelGroupFile.write('<Parameter Name=\"Layer\" Type=\"Integer\" Value=\"%s\"/>\n' % (i-10))
#                   else:
#                       modelGroupFile.write('<Parameter Name=\"Layer\" Type=\"Integer\" Value=\"%s\"/>\n' % i)
#               i += 1
#            modelGroupFile.write('</Object>\n')
#            modelGroupFile.close()
#
#            del(object)
#            del(exportModel)
#
#        if subObjects: #if we have subobjects then we make group
#            object = expOb.blenderObject
#            obD_mat = expOb.matrix
#            exportModel = Model()
#            exportModel.frame = Transform(\
#            obD_mat[0][0], obD_mat[0][1], obD_mat[0][2],
#            obD_mat[1][0], obD_mat[1][1], obD_mat[1][2],
#            obD_mat[2][0], obD_mat[2][1], obD_mat[2][2],
#            obD_mat[0][3], obD_mat[1][3], obD_mat[2][3])
#
#            obFileName = expOb.name
#            if anim:
#               wholeGroupFilename = os.path.basename(currentBlendFile.replace('.blend', '_f'+frameS[-4:]+"."+obFileName+'.xml'))
#            else:
#                wholeGroupFilename = os.path.basename(currentBlendFile.replace('.blend', "."+obFileName+'.xml'))
#
#            if anim:
#                filePath = os.path.join(framesDir,wholeGroupFilename)
#            else:
#                filePath = os.path.join(tempDir,wholeGroupFilename)
#            filePath = filePath.replace(":","_").replace("_\\",":\\")
#
#            groupFile = open(filePath, "w")
#
#            groupFile.write('<Object Identifier=\"./Models/%s\" Label=\"Model\" Name=\"%s\" Type=\"Model\">\n' % (expOb.name, expOb.name))
#
#            for subObName, subFilePath, modelFrame in exportedObjects:
#                groupFile.write('<Object Identifier=\"./Models/%s\" Label=\"Model\" Name=\"%s\" Type=\"Model\">\n' % (subObName, subObName))
#                groupFile.write('<Link Identifier=\"./Models/%s\" Name=\"%s\" File=\"%s\">\n' % (subObName, subObName,subFilePath.replace(":","_").replace("_\\",":\\")))
#                groupFile.write('</Link>\n')
#                modelFrame.write(groupFile, identifier="Group Frame")
#                groupFile.write('</Object>\n')
#
#            groupFile.write('</Object>\n')
#            self.modelFilesList.append((filePath,expOb.name,ob.meshName,exportModel.frame, ob.isProxy))
#

    def writeModelBinaryNew(self, scn, expOb, frame, anim):
        '''write model using binary mesh.thea format - new version

            :param scn: Blender scene
            :type: scn: bpy_types.Scene
            :param expOb: object to export
            :type expOb: exportObject
            :param frame: transformation matrix
            :type frame: Transform
            :param anim: is object animated
            :type anim: bool
        '''
        from TheaForBlender.thea_render_main import getMatTransTable, setPaths


        t1 = time.time()


        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scn)

        t2 = time.time()
#         thea_globals.log.debug("*t2-t1: %s" % (t2-t1))

        matTransTable = getMatTransTable()

#         thea_globals.log.debug("ob: %s %s" % (expOb.name, expOb.blenderObject.name))


        frameS= "0000" + str(frame)
        tempDir = os.path.join(exportPath,"~thexport")
        if not os.path.isdir(tempDir):
            os.mkdir(tempDir)
        if anim:
            framesDir = os.path.join(tempDir,"frames")
            if not os.path.isdir(framesDir):
                os.mkdir(framesDir)
        objects = []
        exportedObjects = []
        subObjects = False
        if len(expOb.subobjects) > 0:
            objects = expOb.subobjects
            subObjects = True
        else:
            objects.append(expOb)



        for ob in objects:
#             ##print("ob: ", ob)
            if(ob.blenderObject is None):
                return
            if getattr(ob.blenderObject, 'library'):
            #if ob.blenderObject.library:
                libObject = True
                obName = ob.name
                #obFileName = ob.meshName
#                 obFileName = ob.name.replace(":","_").replace("_\\",":\\")
                obFileName = obName.replace(":","_").replace("_\\",":\\")
#                 obFileName = "".join([ c if c.isalnum() else "_" for c in obFileName ])
                obFileName = re.sub('[^0-9a-zA-Z]+', '_', obFileName)
                if anim:
#                    modelGroupFilename = os.path.basename(ob.blenderObject.library.filepath.replace('.blend', '_f'+frameS[-4:]))+"."+obFileName+".xml"
                   modelGroupFilename = os.path.basename(ob.blenderObject.library.filepath.replace('.blend', '_f'+frameS[-4:]))+"."+os.path.basename(obFileName)+".xml"
                else:
                    modelGroupFilename = os.path.basename(ob.blenderObject.library.filepath.replace('.blend', "."+obFileName+'.xml'))
            else:
                obFileName = ob.meshName.replace(":","_").replace("_\\",":\\")
#                 obFileName = "".join([ c if c.isalnum() else "_" for c in obFileName ])
                obFileName = re.sub('[^0-9a-zA-Z]+', '_', obFileName)
                if anim:
                   modelGroupFilename = os.path.basename(currentBlendFile.replace('.blend', '_f'+frameS[-4:]+"."+obFileName+'.xml'))
                else:
                    modelGroupFilename = os.path.basename(currentBlendFile.replace('.blend', "."+obFileName+'.xml'))
                libObject = False
                obName = ob.name#[3]
#                 obName = "".join([ c if c.isalnum() else "_" for c in obName ])
#                 obName = re.sub('[^0-9a-zA-Z]+', '_', obName)



            object = ob.blenderObject
            exportModel = Model()

#             exportModel.name = re.sub('[^0-9a-zA-Z]+', '_', ob.name)
            exportModel.name = ob.name

            obD_mat = ob.matrix
            exportModel.frame = Transform(\
            obD_mat[0][0], obD_mat[0][1], obD_mat[0][2],
            obD_mat[1][0], obD_mat[1][1], obD_mat[1][2],
            obD_mat[2][0], obD_mat[2][1], obD_mat[2][2],
            obD_mat[0][3], obD_mat[1][3], obD_mat[2][3])

            t3 = time.time()
#             thea_globals.log.debug("*t3-t2: %s" % (t3-t2))

            try:
                if ob.blenderObject["thAnimated"]:
                    animatedMesh = True
                else:
                    animatedMesh = False
            except:
                    animatedMesh = False

            if (scn.thea_Reuse == 0):
                if anim:
                    if animatedMesh:
                      exportGeometry = True
                    else:
                      exportGeometry = False
                else:
                    exportGeometry = True
            elif animatedMesh:
                exportGeometry = True
            else:
                exportGeometry = False

            if not exportGeometry and thea_globals.forceExportGeometry:
                exportGeometry = True

            mesh = ob.blenderObject.data

            try:
                meshMaterials = mesh.materials
            except:
                meshMaterials = False


            t5 = time.time()
#             thea_globals.log.debug("*t5-t4: %s" % (t5-t4))

            if meshMaterials:

                try:
                    exportModel.materialName = meshMaterials[0].name
                except:
                    exportModel.materialName = "--None--"

                from . import thea_render_main
                lut = thea_render_main.getLUTarray()
                for mat in meshMaterials:
                    if mat:
                        matName = mat.name
                        madeLink = False
                        if thea_globals.getUseLUT():#getattr(scn, 'thea_useLUT'):
                            for trMat in matTransTable:
                                t11 = time.time()
                                try:
                                    if thea_globals.getNameBasedLUT():
                                        if trMat[0] == matName and (self.findMaterialLink(matName) < 0):
                                            matLink = Link()
                                            matLink.setName(trMat[0])
                                            matLink.setFilename(trMat[1])
                                            self.addMaterialLink(matLink)
                                            madeLink = True
                                    else:
                                        if int(getattr(bpy.data.materials.get(matName), 'thea_LUT', 0)) > 0:
                                            pass
                                            if trMat[0] == lut[int(getattr(bpy.data.materials.get(matName), 'thea_LUT', 0))] and (self.findMaterialLink(matName) < 0):
                                                matLink = Link()
                                                matLink.setName(matName)
                                                matLink.setFilename(trMat[1])
                                                self.addMaterialLink(matLink)
                                                madeLink = True
                                    t12 = time.time()
#                                     thea_globals.log.debug("**t12-t11: %s" % (t12-t11))
                                except:
                                    emptyMat = True
                        try:
                            ##print("mat['thea_extMat']: ", mat['thea_extMat'], os.path.exists(os.path.abspath(bpy.path.abspath(mat['thea_extMat']))))
                            #os.path.abspath(bpy.path.abspath(extMatFile)

                            if os.path.exists(os.path.abspath(bpy.path.abspath(mat['thea_extMat']))) and (self.findMaterialLink(matName) < 0):
                                matLink = Link()
                                matLink.setName(matName)
                                matLink.setFilename(os.path.abspath(bpy.path.abspath(mat['thea_extMat'])))
                                self.addMaterialLink(matLink)
                                madeLink = True
                        except: pass



                        if mat and (self.findMaterial(matName) < 0):
                            ma = ThMaterial()
                            ma.setName(matName)
                            if madeLink:
                                ma.link = True
                            self.addMaterial(ma)
                            self.materialList[self.findMaterial(matName)].blenderMat = mat
                    else:
                        #print("====Missing material for object %s. Object won't be exported!=====" % obName)
                        scn['thea_Warning'] = ("Missing material for object %s" % obName)
                        return
            else:
                #print("====No material assigned to object. Assigning basic_gray material====")
                matName = "basic_gray"
                ma = ThMaterial()
                ma.setName(matName)
                self.addMaterial(ma)
                if(bpy.data.materials.get(matName)):
                    mesh.materials.append(bpy.data.materials.get(matName))
                else:
                    bpy.data.materials.new(name=matName)
                    mesh.materials.append(bpy.data.materials.get(matName))
                self.materialList[self.findMaterial(matName)].blenderMat = bpy.data.materials.get(matName)
                meshMaterials = mesh.materials

            if exportGeometry:
                mesh = ob.blenderObject.to_mesh(scn,True, 'RENDER',calc_tessface=True)
                self.mesh_triangulate(mesh)
            else:
                mesh = ob.blenderObject.data

            if mesh is None:
                mesh = ob.blenderObject.data
                exportGeometry = False

            # check if there are more material slots than 1
            # and we should do this before triangulating the mesh
            # and applying the modifiers to work with lower face number
            if len(mesh.materials) > 1:
                materials_dict = self.get_materials(mesh)
            elif len(mesh.materials) == 1:
                materials_dict = {0: {"name":mesh.materials[0].name, "face_count":1}}
            else:
                materials_dict = {None:{"name":None, "face_count":None}}




            thea_globals.log.debug("materials_dict %s" % materials_dict)


            t4 = time.time()
#             thea_globals.log.debug("*t4-t3: %s" % (t4-t3))



#             mesh.update(calc_tessface=True)
#            self.mesh_triangulate(mesh)
#             thea_globals.log.debug("mesh %s" % mesh)
            try:
                if getattr(object, 'thNoRecalcNormals', False):
                    thea_globals.log.debug("Normal recalculation is disabled for this object!")

                else:
                    mesh.calc_normals_split()
                    thea_globals.log.debug("calc normals")
#                 mesh.calc_normals()
            except:
                pass

#             thea_globals.log.debug("mesh %s" % mesh)


            t6 = time.time()
#             thea_globals.log.debug("*t6-t5: %s" % (t6-t5))


            t8 = time.time()
#             thea_globals.log.debug("*t8-t7: %s" % (t8-t7))
            #search if mesh is already exported
            if anim:
                filePath = os.path.join(framesDir,modelGroupFilename)
            else:
                filePath = os.path.join(tempDir,modelGroupFilename)
            if ob.isProxy == True: #is instance
                filePath = filePath.replace(".xml", "_proxy.xml")

            filePath=filePath.replace(":","_").replace("_\\",":\\")


            isInstance = ob.isProxy#[5]

            for obFilenameL, obNameL, meshName, obFrameL, isInstance in self.modelFilesList:
                if obFilenameL == filePath:
                    exportGeometry = False

            if subObjects:
                exportedObjects.append((obName, filePath, exportModel.frame))
            else:
                self.modelFilesList.append((filePath,obName,ob.meshName, exportModel.frame, ob.isProxy))

            modelGroupFile = open(filePath, "w")

            if ob.isProxy: #if proxy
                modelGroupFile.write('<Object Identifier=\"./Proxies/Model/%s\" Label=\"Model\" Name=\"%s\" Type=\"Model\">\n' % (obName, obName))
#                modelGroupFile.write('<Parameter Name=\"Smoothing Angle\" Type=\"Real\" Value=\"%s\"/>\n' % "90")
#                modelGroupFile.write('<Parameter Name=\"Smoothing Angle\" Type=\"Real\" Value=\"%s\"/>\n' % (round (180 * mesh.auto_smooth_angle) / 3.14159265359))
            else:
                modelGroupFile.write('<Object Identifier=\"./Models/%s\" Label=\"Model\" Name=\"%s\" Type=\"Model\">\n ' % (obName, obName))

#                modelGroupFile.write('<Parameter Name=\"Smoothing Angle\" Type=\"Real\" Value=\"%s\"/>\n' % (round (180 * mesh.auto_smooth_angle) / 3.14159265359))
#                modelGroupFile.write('<Parameter Name=\"Smoothing Angle\" Type=\"Real\" Value=\"%s\"/>\n' % "90")
            if thea_globals.forceExportGeometry:
                exportGeometry = True

#             thea_globals.log.debug("exportGeometry2: %s, force: %s" % (exportGeometry, thea_globals.forceExportGeometry))

            model = "S"
            mat_count = 0
            for mat_index, mat_desc in materials_dict.items():
                if mat_desc['face_count'] > 0:
                    mat_count += 1
            if mat_count > 1:
                model = "C"
            thea_globals.log.debug("model: %s", model)


            for matKey, mat_desc in materials_dict.items():
                thea_globals.log.debug("matKey: %s, name: %s, faces: %s" % (matKey, mat_desc['name'], mat_desc['face_count']))
#                 currMatName = re.sub('[^0-9a-zA-Z]+', '_', self.materialList[matKey].name)
                currMatName = re.sub('[^0-9a-zA-Z]+', '_', mat_desc['name'])
#                 thea_globals.log.debug("currMatName: %s" % currMatName)
                if animatedMesh:
                   if ob.blenderObject.library:
                       modelFilename = os.path.basename(ob.blenderObject.library.filepath.replace('.blend', '_f'+frameS[-4:]))+"."+os.path.basename(obFileName)+"_"+currMatName+'.mesh.thea'
                   else:
                       modelFilename = os.path.basename(currentBlendFile.replace('.blend', '_f'+frameS[-4:]+"."+obFileName+"_"+currMatName+'.mesh.thea'))
                else:
                    modelFilename = os.path.basename(currentBlendFile.replace('.blend', "."+obFileName+"_"+currMatName+'.mesh.thea'))
                if len(materials_dict) > 1:
                    modelGroupFile.write('<Object Identifier=\"./Models/%s\" Label=\"Model\" Name=\"%s (%s)\" Type=\"Model\">\n' % (obName, obName,currMatName))

                if anim and animatedMesh:
                    modelPath = os.path.join(framesDir,modelFilename)
                else:
                    modelPath = os.path.join(tempDir,modelFilename)
                modelPath = modelPath.replace(":","_").replace("_\\",":\\")

                modelGroupFile.write('<Link Identifier=\"Triangular Mesh\" Name=\"\" File=\"%s\">\n' % modelPath)
                modelGroupFile.write('<Parameter Name=\"Smoothing Angle\" Type=\"Real\" Value=\"45\"/>\n</Link>\n')
#                 modelGroupFile.write('<Parameter Name=\"Appearance\" Type=\"String\" Value=\"%s\"/>\n' % self.materialList[matKey].name)
                modelGroupFile.write('<Parameter Name=\"Appearance\" Type=\"String\" Value=\"%s\"/>\n' % mat_desc['name'])
                if bpy.context.scene.objects.get(obName):
                    modProp = bpy.context.scene.objects.get(obName)
                    modelGroupFile.write('<Parameter Name=\"Enabled\" Type=\"Boolean\" Value=\"%s\"/>\n' % modProp.thEnabled)
                    modelGroupFile.write('<Parameter Name=\"Visible\" Type=\"Boolean\" Value=\"%s\"/>\n'% modProp.thVisible)
                    modelGroupFile.write('<Parameter Name=\"Shadow Caster\" Type=\"Boolean\" Value=\"%s\"/>\n'% modProp.thShadowCaster)
                    modelGroupFile.write('<Parameter Name=\"Shadow Tight\" Type=\"Boolean\" Value=\"%s\"/>\n'% modProp.thShadowTight)
                    modelGroupFile.write('<Parameter Name=\"Shadow Receiver\" Type=\"Boolean\" Value=\"%s\"/>\n'% modProp.thShadowReceiver)
                    modelGroupFile.write('<Parameter Name=\"Caustics Receiver\" Type=\"Boolean\" Value=\"%s\"/>\n' % modProp.thCausticsReceiver)
                    modelGroupFile.write('<Parameter Name=\"Caustics Transmitter\" Type=\"Boolean\" Value=\"%s\"/>\n'% modProp.thCausticsTransmitter)
                else:
                    pass

                if ob.blenderObject.thExportAnimation == True and bpy.context.scene.thea_ExportAnimation == True:
                        #export animation data
                        obM = ob.blenderObject.matrix_world
                        obFrame = Transform(\
                        obM[0][0], -obM[0][1], -obM[0][2],
                        obM[1][0], -obM[1][1], -obM[1][2],
                        obM[2][0], -obM[2][1], -obM[2][2],
                        obM[0][3],  obM[1][3],  obM[2][3])



#                         startObMatrixAssigned = mathutils.Matrix((\
#                         (obM[0][0], -obM[0][1], -obM[0][2], obM[0][3]),
#                         (obM[1][0], -obM[1][1], -obM[1][2], obM[1][3]),
#                         (obM[2][0], -obM[2][1], -obM[2][2], obM[2][3]),
#                         (0.0, 0.0, 0.0, 1.0)))

                        startObMatrixAssigned = mathutils.Matrix((\
                        (obM[0][0], obM[0][1], obM[0][2], obM[0][3]),
                        (obM[1][0], obM[1][1], obM[1][2], obM[1][3]),
                        (obM[2][0], obM[2][1], obM[2][2], obM[2][3]),
                        (0.0, 0.0, 0.0, 1.0)))

                        obMInverted = ob.blenderObject.matrix_world.inverted()
                        currFrame = bpy.context.scene.frame_current
                        startFrame = bpy.context.scene.frame_start
                        endFrame = bpy.context.scene.frame_end
                        im = InterpolatedMotion()
                        im.enabled = True
                        im.duration = endFrame+1-startFrame
                        bpy.context.scene.frame_set(startFrame)
                        prevObM = ob.blenderObject.matrix_world
                        if(bpy.context.scene.get('thea_AnimationEveryFrame')):
                            tolerance = 0
                        else:
                            tolerance = 10**-5
                        for frame in range(startFrame, endFrame+1, 1):
                            print ("\n\nExporting animation frame %s for mesh object %s: " % (frame, obName))
                            bpy.context.scene.frame_set(frame)
                            obM = ob.blenderObject.matrix_world
                            sum = 0
                            for v in (prevObM-obM):
                                for i in v:
                                    sum += abs(i)

                            if((sum>tolerance) or (frame == startFrame)):
                                ob_matrix_world_Assigned = mathutils.Matrix((\
                                (obM[0][0], obM[0][1], obM[0][2], obM[0][3]),
                                (obM[1][0], obM[1][1], obM[1][2], obM[1][3]),
                                (obM[2][0], obM[2][1], obM[2][2], obM[2][3]),
                                (0.0, 0.0, 0.0, 1.0)))

                                obM = startObMatrixAssigned.inverted() * ob_matrix_world_Assigned
                                frame = Transform(\
                                obM[0][0], obM[0][1], obM[0][2],
                                obM[1][0], obM[1][1], obM[1][2],
                                obM[2][0], obM[2][1], obM[2][2],
                                obM[0][3], obM[1][3], obM[2][3])
                                im.addNode(bpy.context.scene.frame_current, frame)
                            else:
                                thea_globals.log.debug("****no transform change on this frame")
                            prevObM = ob.blenderObject.matrix_world * 1.0
                        bpy.context.scene.frame_set(currFrame)
                        im.write(modelGroupFile)


                if getattr(object, 'thea_Container') != "None":
                    matInterface = getattr(object, 'thea_Container')
                    modelGroupFile.write('<Parameter Name=\"Interface Appearance\" Type=\"String\" Value=\"%s\"/>\n' % matInterface)
                else:
                    matInterface = False


                t9 = time.time()
#                 thea_globals.log.debug("*t9-t8: %s" % (t9-t8))

#                 thea_globals.log.debug("matFaces: %s %s" % (matFaces, len(matFaces)))
#                 if exportGeometry and len(matFaces) > 0: #if we should export geometry too
                if exportGeometry and mat_desc['face_count'] > 0: #if we should export geometry too
#                     thea_globals.log.debug("mesh3 %s" % mesh)
                    t_co = [None] * len(mesh.vertices) * 3
                    mesh.vertices.foreach_get("co", t_co)
                    t_vi = [None] * len(mesh.loops)
                    mesh.loops.foreach_get("vertex_index", t_vi)
                    t_vn = [None] * len(mesh.loops) * 3
                    modelUVs = []
                    do_uvs = bool(mesh.uv_layers)
#                     print("do_uvs: ", do_uvs)


                    # NOTE: Here we assume that loops order matches polygons order!
                    mesh.loops.foreach_get("normal", t_vn)
#                     thea_globals.log.debug("t_co: %s, t_vi: %s, t_vn: %s" % (len(t_co), len(t_vi), len(t_vn)))

#                     print("model: %s, materials: %s" % (model, mat_count))
#                     thea_globals.log.debug("mesh.polygons: %s" % len(mesh.polygons))
                    if model == "C":
                        mat_index = matKey

                        index_num = 0
                        for p in mesh.polygons:
                            if p.material_index == mat_index:
                                index_num += 3


                        nt_no = [None] * index_num * 3
                        nt_vi = [None] * index_num
                        if do_uvs:
                            modelUVs = [None] * len(mesh.uv_layers)
                            for i in range(0, len(mesh.uv_layers)):
                                modelUVs[i] = [None] * index_num * 2

                        i=0
                        for p in mesh.polygons:
                            if p.material_index == mat_index:
                                n = 0
                                for j in p.loop_indices:
                    #                print(mesh.loops[j].normal, mesh.loops[j].vertex_index)
                                    nt_vi[i+n] = mesh.loops[j].vertex_index
                                    if do_uvs:
                    #                    for uv_layer in mesh.uv_layers:
                                        for u in range(0, len(modelUVs)):
                                            uv_layer = mesh.uv_layers[u].data
                    #                        print("    UV: %r" % uv_layer[j].uv)
                                            modelUVs[u][(i+n )*2+0] = uv_layer[j].uv[0]
                                            modelUVs[u][(i+n )*2+1] = 1-uv_layer[j].uv[1]
                                    for m in (0,1,2):
                                        nt_no[(i+n )*3+m] = mesh.loops[j].normal[m]
                                    n += 1
                                i += 3
#                         thea_globals.log.debug("nt_vi: %s", len(nt_vi))
#                         thea_globals.log.debug("nt_no: %s", len(nt_no))

                    else:
                        modelUVs = []
                        uvlayers = []
                        uvtextures = []
                        if do_uvs:
                            uvlayers = mesh.uv_layers
                            uvtextures = mesh.uv_textures
                            for uv_layer in mesh.uv_layers:
                                t_uv = [None] * len(mesh.loops) * 2
                                uv_layer.data.foreach_get("uv", t_uv)
                                x = np.array(t_uv[0::2])
                                y = np.array(t_uv[1::2])
                                n_y = 1-y
                                n_t_uv = np.insert(n_y, np.arange(len(x)),x)
                                modelUVs.append(n_t_uv)


                    modelFile = open(modelPath, "wb")


                    if len(modelUVs)>1 :
                        magicHeader = 0x54524d02
                    else:
                        magicHeader = 0x54524d01

                    modelFile.write(struct.pack('<l',magicHeader))

                    vertexCount = len(t_co)
                    if vertexCount > 0:
                        modelFile.write(struct.pack('<l',int(vertexCount/3)))
                        modelFile.write(struct.pack("<%df" % (vertexCount), *t_co))
                    #    print("t_co: ", len(t_co), t_co)


                    if model == "C":
                        normalCount = len(nt_no)
                        if normalCount > 0:
                            modelFile.write(struct.pack('<l',int(normalCount/3)))
                            modelFile.write(struct.pack("<%df" % (normalCount), *nt_no))
                    #        print("nt_no: ", len(t_co), t_co)

                        triangleCount = len(nt_vi)
                        if triangleCount > 0:
                            modelFile.write(struct.pack('<l',int(triangleCount/3)))
                            modelFile.write(struct.pack("<%dl" % (triangleCount), *nt_vi))
                    #        print("t_vi: ", len(nt_vi), nt_vi)
                    else:
                        normalCount = len(t_vn)
                        if normalCount > 0:
                            modelFile.write(struct.pack('<l',int(normalCount/3)))
                            modelFile.write(struct.pack("<%df" % (normalCount), *t_vn))

                        triangleCount = len(t_vi)
                        if triangleCount > 0:
                            modelFile.write(struct.pack('<l',int(triangleCount/3)))
                            modelFile.write(struct.pack("<%dl" % (triangleCount), *t_vi))

                    if len(modelUVs)>1:
                        modelFile.write(struct.pack('<l',len(modelUVs)))
                        for modelU in modelUVs:
                            uvCount = len(modelU)
                            modelFile.write(struct.pack('<l',int(uvCount/2)))
                            modelFile.write(struct.pack("<%df" % (uvCount), *modelU))
                    #        print("modelU: ", len(modelU), modelU)

                    elif len(modelUVs)==1:
                        uvCount = len(modelUVs[0])
                        if vertexCount > 0:
                            modelFile.write(struct.pack('<l',int(uvCount/2)))
                            modelFile.write(struct.pack("<%df" % (uvCount), *modelUVs[0]))

                    modelFile.write(struct.pack('<l',0))
                    modelFile.close()


                    if len(materials_dict) > 1:
                        modelGroupFile.write('</Object>\n')
                elif exportGeometry: # just create empty file if there are no faces for the material
                    modelFile = open(modelPath, "wb")
                    magicHeader = 0x54524d01
                    modelFile.write(struct.pack('<l',magicHeader))
                    modelFile.write(struct.pack('<l',0))
                    modelFile.write(struct.pack('<l',0))
                    modelFile.write(struct.pack('<l',0))
                    modelFile.write(struct.pack('<l',0))
                    modelFile.close()

            if exportGeometry:
                bpy.data.meshes.remove(mesh)
                del(mesh)

            t10 = time.time()
#             thea_globals.log.debug("*t10-t9: %s" % (t10-t9))

            i = 0
            for layer in object.layers:
               if layer:
                   if i>9:
                       modelGroupFile.write('<Parameter Name=\"Layer\" Type=\"Integer\" Value=\"%s\"/>\n' % (i-10))
                   else:
                       modelGroupFile.write('<Parameter Name=\"Layer\" Type=\"Integer\" Value=\"%s\"/>\n' % i)
               i += 1
            modelGroupFile.write('</Object>\n')
            modelGroupFile.close()

            del(object)
            del(exportModel)

        if subObjects: #if we have subobjects then we make group
            object = expOb.blenderObject
            obD_mat = expOb.matrix
            exportModel = Model()
            exportModel.frame = Transform(\
            obD_mat[0][0], obD_mat[0][1], obD_mat[0][2],
            obD_mat[1][0], obD_mat[1][1], obD_mat[1][2],
            obD_mat[2][0], obD_mat[2][1], obD_mat[2][2],
            obD_mat[0][3], obD_mat[1][3], obD_mat[2][3])

            obFileName = expOb.name
            if anim:
               wholeGroupFilename = os.path.basename(currentBlendFile.replace('.blend', '_f'+frameS[-4:]+"."+obFileName+'.xml'))
            else:
                wholeGroupFilename = os.path.basename(currentBlendFile.replace('.blend', "."+obFileName+'.xml'))

            if anim:
                filePath = os.path.join(framesDir,wholeGroupFilename)
            else:
                filePath = os.path.join(tempDir,wholeGroupFilename)
            filePath = filePath.replace(":","_").replace("_\\",":\\")

            groupFile = open(filePath, "w")
            groupFile.write('<Object Identifier=\"./Models/%s\" Label=\"Model\" Name=\"%s\" Type=\"Model\">\n' % (expOb.name, expOb.name))

            for subObName, subFilePath, modelFrame in exportedObjects:
                groupFile.write('<Object Identifier=\"./Models/%s\" Label=\"Model\" Name=\"%s\" Type=\"Model\">\n' % (subObName, subObName, ))
                groupFile.write('<Link Identifier=\"./Models/%s\" Name=\"%s\" File=\"%s\">\n' % (subObName, subObName,subFilePath.replace(":","_").replace("_\\",":\\")))
                groupFile.write('</Link>\n')
                modelFrame.write(groupFile, identifier="Group Frame")
                groupFile.write('</Object>\n')
            groupFile.write('</Object>\n')
            self.modelFilesList.append((filePath,expOb.name,ob.meshName,exportModel.frame, ob.isProxy))


##
# export Hair
##
#    def writeHairParticlesBinary(self, scn, ob, model, frame, anim):
#        '''Old version of hair particle export
#        '''
#
#
#
#        def vector_substract(a, b):
#            return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
#
#
#        def vector_cross_product(x, y):
#            v = [0, 0, 0]
#            v[0] = x[1]*y[2] - x[2]*y[1]
#            v[1] = x[2]*y[0] - x[0]*y[2]
#            v[2] = x[0]*y[1] - x[1]*y[0]
#            return v
#
#        def calc_normal(v0, v1, v2):
#            return vector_cross_product(vector_substract(v0, v1),vector_substract(v0, v2))
#
#        from TheaForBlender.thea_render_main import getMatTransTable, setPaths
#
#        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scn)
#        #exportPath = bpy.path.abspath(scn.render.filepath)
#        #currentBlendFile = bpy.data.filepath
#        #currentBlendDir = os.path.dirname(currentBlendFile)
#        matTransTable = getMatTransTable()
#
#        frameS= "0000" + str(frame)
#        tempDir = os.path.join(exportPath, "~thexport")
#        if not os.path.isdir(tempDir):
#            os.mkdir(tempDir)
#
#        if ob[0].library:
#            libObject = True
#            obName = ob.name+"_hair"
#            obFileName = ob[3]
#            modelGroupFilename = os.path.basename(currentBlendFile.replace('.blend', '_f'+frameS[-4:]+"."+obFileName+'_part.xml'))
#        else:
#            obFileName = ob[3   ]
#            modelGroupFilename = os.path.basename(currentBlendFile.replace('.blend', '_f'+frameS[-4:]+"."+obFileName+'_part.xml'))
#            libObject = False
#            obName = ob[3]+"_hair"
#
#        if ob[2]: #if there is parrent matrix
#            obD_mat = ob[2] * ob[1]
#            objectTransform = [[obD_mat[0][0],obD_mat[0][1],obD_mat[0][2]],[obD_mat[1][0],obD_mat[1][1],obD_mat[1][2]],[obD_mat[2][0],obD_mat[2][1],obD_mat[2][2]],[obD_mat[3][0],obD_mat[3][1],obD_mat[3][2]]]
#        else:
#            obD_mat = ob[1]
#            objectTransform = [[obD_mat[0][0],obD_mat[0][1],obD_mat[0][2]],[obD_mat[1][0],obD_mat[1][1],obD_mat[1][2]],[obD_mat[2][0],obD_mat[2][1],obD_mat[2][2]],[obD_mat[3][0],obD_mat[3][1],obD_mat[3][2]]]
#
#
#
#
#
#        model.frame = Transform(\
#        objectTransform[0][0], objectTransform[1][0], objectTransform[2][0],
#        objectTransform[0][1], objectTransform[1][1], objectTransform[2][1],
#        objectTransform[0][2], objectTransform[1][2], objectTransform[2][2],
#        objectTransform[3][0],  objectTransform[3][1],  objectTransform[3][2])
#
#
#        object = ob[0]
#        partSystem = ob[5]
#        partSettings = partSystem.settings
#        partMatIdx = partSettings.material
#        partMat = object.material_slots[partMatIdx-1].material
#        modifierName = ob[6]
#
#        if partMat:
##             if len(scn.get('thea_Warning'))<2:
##                 scn['thea_Warning'] = ""
#            # check if we should link this material name
#            matName = partMat.name
#            madeLink = False
#            for trMat in matTransTable:
#                try:
#                    if trMat[0] == matName and (self.findMaterialLink(matName) < 0):
#                        matLink = Link()
#                        matLink.setName(trMat[0])
#                        matLink.setFilename(trMat[1])
#                        self.addMaterialLink(matLink)
#                        madeLink = True
#                except:
#                    emptyMat = True
#            try:
#
#                if os.path.exists(mat['TheaMatLink']) and (self.findMaterialLink(matName) < 0):
#                    matLink = Link()
#                    matLink.setName(matName)
#                    matLink.setFilename(mat['TheaMatLink'])
#                    self.addMaterialLink(matLink)
#                    madeLink = True
#            except: pass
#
#            if partMat and (self.findMaterial(matName) < 0):
#                ma = ThMaterial()
#                ma.setName(matName)
#                if madeLink:
#                    ma.link = True
#                self.addMaterial(ma)
#                self.materialList[self.findMaterial(matName)].blenderMat = partMat
#        else:
#            #print("====Missing material for object %s. Object won't be exported!=====" % obName)
#            scn['thea_Warning'] = ("Missing material for object %s" % obName)
#            return
#
#        if scn.thea_Reuse == 0:
#            exportGeometry = True
#        else:
#            exportGeometry = False
#
#
#        matKey = self.findMaterial(partMat.name)
#
#        #search if mesh is already exported
#        for obFilenameL, obNameL, obFrameL, isInstance in self.modelFilesList:
#            if obFilenameL == os.path.join(tempDir,modelGroupFilename):
#                exportGeometry = False
#
#        self.modelFilesList.append((os.path.join(tempDir,modelGroupFilename),obName,obName,model.frame, False))
#        modelFilename = os.path.basename(currentBlendFile.replace('.blend', '_f'+frameS[-4:]+"."+obFileName+"_part.mesh.thea"))
#        modelGroupFile = open(os.path.join(tempDir,modelGroupFilename), "w")
#        modelGroupFile.write('<Object Identifier=\"./Models/%s\" Label=\"Model\" Name=\"%s\" Type=\"Model\">\n' % (obName, obName))
#
#
#
#        modelGroupFile.write('<Link Identifier=\"Triangular Mesh\" Name=\"\" File=\"%s\">\n' % (os.path.join(tempDir,modelFilename)))
#        # THIS LINE MAKES NO SENSE
#        modelGroupFile.write('<Message Name=\"./Smoothing/Smooth 180\"/>\n</Link>\n')
#        modelGroupFile.write('<Parameter Name=\"Appearance\" Type=\"String\" Value=\"%s\"/>\n' % self.materialList[matKey].name)
#
#
#        if exportGeometry: #if we should export geometry too
#            # remember list of selected and active objects
#            vertexNum = 0
#            normalNum = 0
#            faceNum = 0
#            uvNum = 0
#            modelP = []
#            modelN = []
#            modelF = []
#            modelU = []
#            modelV = []
#            modelNN = []
#            meshV = []
##             if self.materialList[matKey].blenderMat.get('thea_StrandRoot'):
##                 rootSize = self.materialList[matKey].blenderMat.get('thea_StrandRoot')
##             else:
##                 rootSize = 0.01
#            rootSize = self.materialList[matKey].blenderMat.thea_StrandRoot
#            tipSize = self.materialList[matKey].blenderMat.thea_StrandTip
##             if self.materialList[matKey].blenderMat.get('thea_StrandTip'):
##                 tipSize = self.materialList[matKey].blenderMat.get('thea_StrandTip')
##             else:
##                 tipSize = 0.001
#            hairKeysNum = partSystem.settings.hair_step
#            sizeStep = (rootSize - tipSize) / (hairKeysNum)
#            stepV = 1 / (hairKeysNum)
#            vertexNum = 0
#            faceNum = 0
#            rand = 1
#
#            for particle in partSystem.particles:
#                width = rootSize
#                vStart = vertexNum
#                mul = 1
#                #rand = random()
#                rand = -rand
#                if rand > 0.5:
#                    rWidthX = width
#                    sizeStepX = sizeStep
#                else:
#                    rWidthX = width*-1
#                    sizeStepX = sizeStep*-1
#                #rand = random()
#                if rand > 0.5:
#                    rWidthY = width
#                    sizeStepY = sizeStep
#                else:
#                    rWidthY = width*-1
#                    sizeStepY = sizeStep*-1
#
##                 rWidthX = width
##                 sizeStepX = sizeStep
##                 rWidthY = width
##                 sizeStepY = sizeStep
#
#                for pL in particle.hair_keys:
#                    pX, pY, pZ = pL.co
#                    modelP.append(pX-(rWidthX/2))
#                    modelP.append(pY-(rWidthX/2))
#                    modelP.append(pZ)
#                    modelP.append(pX+(rWidthX/2))
#                    modelP.append(pY+(rWidthY/2))
#                    modelP.append(pZ)
#                    mul *= -1
#                    width -= sizeStep
#                    rWidthX -= sizeStepX
#                    rWidthY -= sizeStepY
#                    vertexNum +=2
#
#
#
#                fStart = faceNum
#                V = 0
#                for v in range(vStart,vertexNum-2,2):
#                    modelF.append(v)
#                    modelF.append(v+1)
#                    modelF.append(v+2)
#                    modelF.append(v+1)
#                    modelF.append(v+2)
#                    modelF.append(v+3)
#                    # calc normals
#                    v1 = v
#                    v2 = v+1
#                    v3 = v+2
#                    v1X = modelP[v1*3]
#                    v1Y = modelP[v1*3+1]
#                    v1Z = modelP[v1*3+2]
#                    v2X = modelP[v2*3]
#                    v2Y = modelP[v2*3+1]
#                    v2Z = modelP[v2*3+2]
#                    v3X = modelP[v3*3]
#                    v3Y = modelP[v3*3+1]
#                    v3Z = modelP[v3*3+2]
#                    v1c = (v1X,v1Y,v1Z)
#                    v2c = (v2X,v2Y,v2Z)
#                    v3c = (v3X,v3Y,v3Z)
#                    normx = (v1Z-v2Z)*(v3Y-v2Y)-(v1Y-v2Y)*(v3Z-v2Z);
#                    normy = (v1X-v2X)*(v3Z-v2Z)-(v1Z-v2Z)*(v3X-v2X);
#                    normz = (v1Y-v2Y)*(v3X  -v2X)-(v1X-v2X)*(v3Y-v2Y);
#                    normlength = sqrt((normx*normx)+(normy*normy)+(normz*normz));
#                    normx /= normlength;
#                    normy /= normlength;
#                    normz /= normlength;
#                    modelN.append(normx)
#                    modelN.append(normy)
#                    modelN.append(normz)
#
#                    v1 = v+1
#                    v2 = v+2
#                    v3 = v+3
#                    v1X = modelP[v1*3]
#                    v1Y = modelP[v1*3+1]
#                    v1Z = modelP[v1*3+2]
#                    v2X = modelP[v2*3]
#                    v2Y = modelP[v2*3+1]
#                    v2Z = modelP[v2*3+2]
#                    v3X = modelP[v3*3]
#                    v3Y = modelP[v3*3+1]
#                    v3Z = modelP[v3*3+2]
#                    v1c = (v1X,v1Y,v1Z)
#                    v2c = (v2X,v2Y,v2Z)
#                    v3c = (v3X,v3Y,v3Z)
#                    normx = (v1Z-v2Z)*(v3Y-v2Y)-(v1Y-v2Y)*(v3Z-v2Z);
#                    normy = (v1X-v2X)*(v3Z-v2Z)-(v1Z-v2Z)*(v3X-v2X);
#                    normz = (v1Y-v2Y)*(v3X  -v2X)-(v1X-v2X)*(v3Y-v2Y);
#                    normlength = sqrt((normx*normx)+(normy*normy)+(normz*normz));
#                    normx /= normlength;
#                    normy /= normlength;
#                    normz /= normlength;
#                    modelN.append(normx)
#                    modelN.append(normy)
#                    modelN.append(normz)
#
#                    modelU.append(0)
#                    modelU.append(1-V)
#                    modelU.append(1)
#                    modelU.append(1-V)
#                    V += stepV
#                    modelU.append(0)
#                    modelU.append(1-V)
#                    V -= stepV
#                    modelU.append(1)
#                    modelU.append(1-V)
#                    V += stepV
#                    modelU.append(0)
#                    modelU.append(1-V)
#                    modelU.append(1)
#                    modelU.append(1-V)
#                    faceNum += 2
#
#
#
#
#            modelFile = open(os.path.join(tempDir,modelFilename), "wb")
#
#            magicHeader = 0x54524d01
#            modelFile.write(struct.pack('<l',magicHeader))
#
#            vertexCount = len(modelP)
#
#            if vertexCount > 0:
#                modelFile.write(struct.pack('<l',int(vertexCount/3)))
#                modelFile.write(struct.pack("<%df" % (vertexCount), *modelP))
#
#            normalCount = len(modelN)
#            if normalCount > 0:
#                modelFile.write(struct.pack('<l',int(normalCount/3)))
#                modelFile.write(struct.pack("<%df" % (normalCount), *modelN))
#
#            triangleCount = len(modelF)
#            if triangleCount > 0:
#                modelFile.write(struct.pack('<l',int(triangleCount/3)))
#                modelFile.write(struct.pack("<%dl" % (triangleCount), *modelF))
#
#            uvCount = len(modelU)
#            if vertexCount > 0:
#                modelFile.write(struct.pack('<l',int(uvCount/2)))
#                modelFile.write(struct.pack("<%df" % (uvCount), *modelU))
#
#            modelFile.close()
#
#        modelGroupFile.write('</Object>\n')
#        modelGroupFile.close()

    def writeHairParticlesBinaryNew(self, scn, ob, model, frame, anim):
        '''write hair particles using binary mesh.thea format

            :param scn: Blender scene
            :type: scn: bpy_types.Scene
            :param ob: mesh object
            :type ob: bpy_types.Object
            :param model: object to export
            :type model: exportObject
            :param frame: transformation matrix
            :type frame: Transform
            :param anim: is object animated
            :type anim: bool
        '''
        from mathutils import Vector

        def perpendicular_vector(CameraZAxis):

            a=CameraZAxis.cross((0,1,0))
            b=CameraZAxis.cross((0,0,1))
            #if (a.dot(a)>b.dot(b)):
            #   return a.normalized()
            #else:
            #   return b.normalized()

            return b.normalized()


        # vector substration
        def vector_substract(a, b):
            return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]

        def vector_cross_product(x, y):
            v = [0, 0, 0]
            v[0] = x[1]*y[2] - x[2]*y[1]
            v[1] = x[2]*y[0] - x[0]*y[2]
            v[2] = x[0]*y[1] - x[1]*y[0]
            return v

        def calc_normal(v0, v1, v2):
            return vector_cross_product(vector_substract(v0, v1),vector_substract(v0, v2))

        from TheaForBlender.thea_render_main import getMatTransTable, setPaths

        (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scn)
        #exportPath = bpy.path.abspath(scn.render.filepath)
        #currentBlendFile = bpy.data.filepath
        #currentBlendDir = os.path.dirname(currentBlendFile)
        matTransTable = getMatTransTable()

        frameS= "0000" + str(frame)
        tempDir = os.path.join(exportPath, "~thexport")
        if not os.path.isdir(tempDir):
            os.mkdir(tempDir)

        if ob[0].library:
            libObject = True
            obName = ob.name+"_hair"
            obFileName = ob[3]
            modelGroupFilename = os.path.basename(currentBlendFile.replace('.blend', '_f'+frameS[-4:]+"."+obFileName+'_part.xml'))
        else:
            obFileName = ob[3   ]
            modelGroupFilename = os.path.basename(currentBlendFile.replace('.blend', '_f'+frameS[-4:]+"."+obFileName+'_part.xml'))
            libObject = False
            obName = ob[3]+"_hair"

#         if ob[2]: #if there is parrent matrix
#             obD_mat = ob[2] * ob[1]
#             objectTransform = [[obD_mat[0][0],obD_mat[0][1],obD_mat[0][2]],[obD_mat[1][0],obD_mat[1][1],obD_mat[1][2]],[obD_mat[2][0],obD_mat[2][1],obD_mat[2][2]],[obD_mat[3][0],obD_mat[3][1],obD_mat[3][2]]]
#         else:
#             obD_mat = ob[1]
#             objectTransform = [[obD_mat[0][0],obD_mat[0][1],obD_mat[0][2]],[obD_mat[1][0],obD_mat[1][1],obD_mat[1][2]],[obD_mat[2][0],obD_mat[2][1],obD_mat[2][2]],[obD_mat[3][0],obD_mat[3][1],obD_mat[3][2]]]
#
        obD_mat =   ((1.0, 0.0, 0.0, 0.0), #export simple proxy matrix
                     (0.0, 1.0, 0.0, 0.0),
                     (0.0, 0.0, 1.0, 0.0),
                     (0.0, 0.0, 0.0, 1.0))

        #obD_mat = ob[1]
        objectTransform = [[obD_mat[0][0],obD_mat[0][1],obD_mat[0][2]],[obD_mat[1][0],obD_mat[1][1],obD_mat[1][2]],[obD_mat[2][0],obD_mat[2][1],obD_mat[2][2]],[obD_mat[3][0],obD_mat[3][1],obD_mat[3][2]]]


        model.frame = Transform(\
        objectTransform[0][0], objectTransform[1][0], objectTransform[2][0],
        objectTransform[0][1], objectTransform[1][1], objectTransform[2][1],
        objectTransform[0][2], objectTransform[1][2], objectTransform[2][2],
        objectTransform[3][0],  objectTransform[3][1],  objectTransform[3][2])


        object = ob[0]
        partSystem = ob[5]
        partSettings = partSystem.settings
        partMatIdx = partSettings.material
        partMat = object.material_slots[partMatIdx-1].material
        modifierName = ob[6]
        mod = object.modifiers[modifierName]
        if partMat:
            matName = partMat.name
            madeLink = False
            for trMat in matTransTable:
                try:
                    if trMat[0] == matName and (self.findMaterialLink(matName) < 0):
                        matLink = Link()
                        matLink.setName(trMat[0])
                        matLink.setFilename(trMat[1])
                        self.addMaterialLink(matLink)
                        madeLink = True
                except:
                    emptyMat = True
            try:

                if os.path.exists(mat['TheaMatLink']) and (self.findMaterialLink(matName) < 0):
                    matLink = Link()
                    matLink.setName(matName)
                    matLink.setFilename(mat['TheaMatLink'])
                    self.addMaterialLink(matLink)
                    madeLink = True
            except: pass

            if partMat and (self.findMaterial(matName) < 0):
                ma = ThMaterial()
                ma.setName(matName)
                if madeLink:
                    ma.link = True
                self.addMaterial(ma)
                self.materialList[self.findMaterial(matName)].blenderMat = partMat
        else:
            #print("====Missing material for object %s. Object won't be exported!=====" % obName)
            scn['thea_Warning'] = ("Missing material for object %s" % obName)
            return

        if scn.thea_Reuse == 0:
            exportGeometry = True
        else:
            exportGeometry = False


        matKey = self.findMaterial(partMat.name)
        #search if mesh is already exported
        for obFilenameL, obNameL, obMeshName, obFrameL, isInstance in self.modelFilesList:
            if obFilenameL == os.path.join(tempDir,modelGroupFilename):
                exportGeometry = False

        self.modelFilesList.append((os.path.join(tempDir,modelGroupFilename),obName,obName, model.frame, False))
        #modelFilename = os.path.basename(currentBlendFile.replace('.blend', '_f'+frameS[-4:]+"."+obFileName+"_part.mesh.thea"))
        modelFilename = os.path.basename(currentBlendFile.replace('.blend', "."+obFileName+"_part.mesh.thea"))
        modelGroupFile = open(os.path.join(tempDir,modelGroupFilename), "w")
        modelGroupFile.write('<Object Identifier=\"./Models/%s\" Label=\"Model\" Name=\"%s\" Type=\"Model\">\n' % (obName, obName))



        modelGroupFile.write('<Link Identifier=\"Triangular Mesh\" Name=\"\" File=\"%s\">\n' % (os.path.join(tempDir,modelFilename)))
        modelGroupFile.write('<Message Name=\"./Smoothing/Smooth 60\"/>\n</Link>\n')
        modelGroupFile.write('<Parameter Name=\"Appearance\" Type=\"String\" Value=\"%s\"/>\n' % self.materialList[matKey].name)


        if exportGeometry: #if we should export geometry too
            # remember list of selected and active objects
            vertexNum = 0
            normalNum = 0
            faceNum = 0
            uvNum = 0
            modelP = []
            modelN = []
            modelF = []
            modelU = []
            modelV = []
            modelNN = []
            meshV = []
            rootSize = self.materialList[matKey].blenderMat.thea_StrandRoot
#             #print("rootSize: ",rootSize)
            tipSize = self.materialList[matKey].blenderMat.thea_StrandTip
#             #print("tipSize: ",tipSize)
            width = rootSize
            hairKeysNum = partSystem.settings.draw_step
            stepV = 1 / (hairKeysNum)
            #why double declare variable
            stepV = 0.25
            vertexNum = 0
            faceNum = 0
            rand = 1

            ob_camera = bpy.context.scene.camera
            CameraZAxis = mathutils.Vector((ob_camera.matrix_world.to_3x3()[0][2], ob_camera.matrix_world.to_3x3()[1][2], ob_camera.matrix_world.to_3x3()[2][2]))

            ##print("CameraZAxis: ",CameraZAxis)
            ##print("perpendicular_vector: ", perpendicular_vector(CameraZAxis))

            steps = partSystem.settings.draw_step
            steps = 2**steps + 1
            stepV = 1 / (steps-1)
            sizeStep = (rootSize - tipSize) / (steps-1)
            num_parents = len(partSystem.particles)
            num_children = len(partSystem.child_particles)

            particleColors = False

#             #print("steps: ", steps)
#             #print("sizeStep: ", sizeStep)
#             #print("num parents: " + str(num_parents))
#             #print("num children: " + str(num_children))

            if getattr(partSystem.settings, "child_type")!="NONE":
                loop_start = 0 if getattr(partSystem.settings, "use_parent_particles", False) else num_parents
            else:
                loop_start = 0
            for pindex in range(loop_start,  num_children + num_parents):
                #uv_on_emitter works only with real particles, not with children
#                 thea_globals.log.debug("pindex: %s" % pindex)
#                 if getattr(partMat, 'thea_ColoredHair', False):
#                     particleColors = True
#                     if num_children == 0:
#                         p_uv = partSystem.uv_on_emitter(mod, partSystem.particles[pindex])
#                     else:
#                         particleColors = False
                if getattr(partMat, 'thea_ColoredHair', False):
                    if pindex >= num_parents:
                       particle = partSystem.particles[(pindex - num_parents) % num_parents]
                    else:
                       particle = partSystem.particles[pindex]
                    p_uv = partSystem.uv_on_emitter(mod, particle, pindex, 0)
#                     thea_globals.log.debug("particle: %s, uv: %s" % (particle, p_uv))
                    particleColors = True

                vStart = vertexNum
                mul = 1
                width = rootSize
                #rWidthX = width
                rWidthX = perpendicular_vector(CameraZAxis)[0]*width
                sizeStepX = sizeStep
                #rWidthY = width
                rWidthY = perpendicular_vector(CameraZAxis)[1]*width
                sizeStepY = sizeStep
                prevCo = Vector((0,0,0))
                for step in range(0, steps):
#                     #print("width: ",width)
                    #try:
                    #    co = partSystem.co_hair(object, mod, pindex, step)
                    #except:
                    co = partSystem.co_hair(object, pindex, step)
                    ##print("co: ", pindex, co)
                    if(co == Vector((0,0,0))):
                        co=prevCo
                        ##print("co1: ", co)
                    pX, pY, pZ = co
                    prevCo = co
                    modelP.append(pX-(rWidthX/2))
                    modelP.append(pY-(rWidthY/2))
                    modelP.append(pZ)
                    modelP.append(pX+(rWidthX/2))
                    modelP.append(pY+(rWidthY/2))
                    modelP.append(pZ)
                    vertexNum +=2
                    width -= sizeStep
                    rWidthX = perpendicular_vector(CameraZAxis)[0]*width
                    rWidthY = perpendicular_vector(CameraZAxis)[1]*width
                    #rWidthX -= sizeStepX
                    #rWidthY -= sizeStepY
                mul *= -1


                fStart = faceNum
                V = 0
                for v in range(vStart,vertexNum-2,2):
                    modelF.append(v)
                    modelF.append(v+1)
                    modelF.append(v+2)
                    modelF.append(v+1)
                    modelF.append(v+2)
                    modelF.append(v+3)
                    # calc normals
                    v1 = v
                    v2 = v+1
                    v3 = v+2
                    v1X = modelP[v1*3]
                    v1Y = modelP[v1*3+1]
                    v1Z = modelP[v1*3+2]
                    v2X = modelP[v2*3]
                    v2Y = modelP[v2*3+1]
                    v2Z = modelP[v2*3+2]
                    v3X = modelP[v3*3]
                    v3Y = modelP[v3*3+1]
                    v3Z = modelP[v3*3+2]
                    v1c = (v1X,v1Y,v1Z)
                    v2c = (v2X,v2Y,v2Z)
                    v3c = (v3X,v3Y,v3Z)
                    normal = calc_normal(v1c,v2c, v3c)
                    modelN.append(normal[0])
                    modelN.append(normal[1])
                    modelN.append(normal[2])
                    v1 = v+1
                    v2 = v+2
                    v3 = v+3
                    v1X = modelP[v1*3]
                    v1Y = modelP[v1*3+1]
                    v1Z = modelP[v1*3+2]
                    v2X = modelP[v2*3]
                    v2Y = modelP[v2*3+1]
                    v2Z = modelP[v2*3+2]
                    v3X = modelP[v3*3]
                    v3Y = modelP[v3*3+1]
                    v3Z = modelP[v3*3+2]
                    v1c = (v1X,v1Y,v1Z)
                    v2c = (v2X,v2Y,v2Z)
                    v3c = (v3X,v3Y,v3Z)
                    normal = calc_normal(v1c,v2c, v3c)
                    modelN.append(normal[0])
                    modelN.append(normal[1])
                    modelN.append(normal[2])

                    if particleColors:
                        for i in range(6):
                            modelU.append(p_uv[0])
                            modelU.append(1-p_uv[1])
                    else:
                        modelU.append(0)
                        modelU.append(1-V)
                        modelU.append(1)
                        modelU.append(1-V)
                        V += stepV
                        modelU.append(0)
                        modelU.append(1-V)
                        V -= stepV
                        ##print("V: ",V)
                        modelU.append(1)
                        modelU.append(1-V)
                        V += stepV
                        ##print("V: ",V)
                        modelU.append(0)
                        modelU.append(1-V)
                        modelU.append(1)
                        modelU.append(1-V)
                    faceNum += 2




            modelFile = open(os.path.join(tempDir,modelFilename), "wb")

            magicHeader = 0x54524d01
            modelFile.write(struct.pack('<l',magicHeader))

#             for p in modelP:
#                 #print("p: ", p)

            vertexCount = len(modelP)

            if vertexCount > 0:
                modelFile.write(struct.pack('<l',int(vertexCount/3)))
                modelFile.write(struct.pack("<%df" % (vertexCount), *modelP))

            normalCount = len(modelN)
            if normalCount > 0:
                modelFile.write(struct.pack('<l',int(normalCount/3)))
                modelFile.write(struct.pack("<%df" % (normalCount), *modelN))

            triangleCount = len(modelF)
            if triangleCount > 0:
                modelFile.write(struct.pack('<l',int(triangleCount/3)))
                modelFile.write(struct.pack("<%dl" % (triangleCount), *modelF))

            uvCount = len(modelU)
            if vertexCount > 0:
                modelFile.write(struct.pack('<l',int(uvCount/2)))
                modelFile.write(struct.pack("<%df" % (uvCount), *modelU))

            modelFile.close()

        modelGroupFile.write('</Object>\n')
        modelGroupFile.close()


    def generateMaterialNew(self,mat): #generate material based on it's blender definition
        '''Generate material based on it's blender definition

            :param mat: Thea material
            :type mat: ThMaterial
            :return: ThMaterial ready to export
            :rtype: ThMaterial

        '''

        global exporter
        import os

        def getFilename(texture): # returns texture image filename and tries to compute sequence texture filename
            scn = bpy.context.scene
            try:
                if texture.image.source == 'SEQUENCE':
                        frames = texture.image_user.frame_duration
                        startFrame = texture.image_user.frame_start
                        offset = texture.image_user.frame_offset
                        imNum = int(bpy.path.basename(texture.image.filepath).split(".")[0][-4:])
                        imNum += offset + (startFrame-1) + (scn.frame_current-1)
                        imNum = "0000"+str(imNum)
                        fileName = os.path.join(os.path.dirname(texture.image.filepath),("%s%s.%s" % (bpy.path.basename(texture.image.filepath).split(".")[0][:-4],imNum[-4:],bpy.path.basename(texture.image.filepath).split(".")[1])))
                else:
                   fileName = texture.image.filepath
            except:
                fileName = "error"

            fileName = bpy.path.abspath(fileName)
            return fileName

        def getTexture(type="Diffuse", component="thea_Basic"):
            propName = ('%s%sCol' % (component, type))
            try:
                texture = RgbTexture(getattr(mat.blenderMat, propName)[0],getattr(mat.blenderMat, propName)[1],getattr(mat.blenderMat, propName)[2])
            except:
                texture = 0
            if type=="Diffuse" and component=="thea_Basic":
                texture = RgbTexture(mat.blenderMat.diffuse_color[0],mat.blenderMat.diffuse_color[1],mat.blenderMat.diffuse_color[2])
            if type=="Emittance" and component=="thea_Emittance":
                propName = ('%sCol' % (component))
                try:
                    texture = RgbTexture(getattr(mat.blenderMat, propName)[0],getattr(mat.blenderMat, propName)[1],getattr(mat.blenderMat, propName)[2])
                except:
                    texture = 0

#             thea_globals.log.debug("\npropName: %s, %s, %s, %s" % (propName, texture, type, component))
            mtextures = mat.blenderMat.texture_slots

            if len(mtextures) > 0:
                for mtex in mtextures:
                    found = False

                    try:
                        texType = bpy.data.textures[mtex.name].type
                    except:
                        texType = None
                    try:
                        tname = '%s_%s%sFilename' % (mat.blenderMat.name, component, type)
#                        thea_globals.log.debug("tname: %s" % tname)
#                        CHANGED > Not sure why, emittance would get 2 times the name Emittance in its filename. Cant find from where this is passed
                        tname = tname.replace("EmittanceEmittance", "Emittance")
                        tname = tname.replace("ThinFilmThinFilmThicknessFilename", "ThinFilmThicknessFilename")
#                        CHANGED > Not sure why, coatin would get thickness in the file name added
                        tname = tname.replace("CoatingThicknessAbsorptionFilename", "CoatingAbsorptionFilename")
                        tname = tname.replace("Stencil", "Weight")
                        tname = tname.replace("ClippingAlpha", "Clipping")
#                         thea_globals.log.debug("tname: %s, %s, %s" % (tname, component, type))
#                         thea_globals.log.debug("tname mtexname: %s" % mtex.name)
                        if mat.blenderMat.texture_slots.get(tname, False) and tname == mtex.name:
                            found = True
#                            thea_globals.log.debug("tname: %s %s %s" % (tname, found, mat.blenderMat.texture_slots.get(tname, False)))
#                            thea_globals.log.debug("mtex.name: %s" % mtex.name)
#                         if bpy.data.textures[mtex.name].get(component) or component=="All":
#                             found = True
                    except:
                        pass

                    if (texType == 'IMAGE') and (found):
                        fileName = getFilename(bpy.data.textures[mtex.name])
#                         thea_globals.log.debug("tex name: %s, %s, %s" % (mtex.name, component, type))
#                         thea_globals.log.debug("fileName: %s" % fileName)
                        tex = BitmapTexture(fileName)
                        tex.invert = getattr(bpy.data.textures[mtex.name], 'thea_TexInvert')
                        tex.gamma = getattr(bpy.data.textures[mtex.name], 'thea_TexGamma')
                        tex.red = getattr(bpy.data.textures[mtex.name], 'thea_TexRed')
                        tex.green = getattr(bpy.data.textures[mtex.name], 'thea_TexGreen')
                        tex.blue = getattr(bpy.data.textures[mtex.name], 'thea_TexBlue')
                        tex.brightness = getattr(bpy.data.textures[mtex.name], 'thea_TexBrightness')
                        tex.contrast = getattr(bpy.data.textures[mtex.name], 'thea_TexContrast')
                        tex.saturation = getattr(bpy.data.textures[mtex.name], 'thea_TexSaturation')
                        tex.clampMax = getattr(bpy.data.textures[mtex.name], 'thea_TexClampMax')
                        tex.clampMin = getattr(bpy.data.textures[mtex.name], 'thea_TexClampMin')
                        tex.rotation = getattr(bpy.data.textures[mtex.name], "thea_TexRotation")
                        tex.Channel = getattr(bpy.data.textures[mtex.name], "thea_TexChannel")
#                        CHANGED > Added repeat function textures
                        tex.repeat = getattr(bpy.data.textures[mtex.name], "thea_TexRepeat")
                        tex.spatialX =  getattr(bpy.data.textures[mtex.name], "thea_TexSpatialXtex")
                        tex.spatialX = (tex.spatialX / tex.spatialX) / tex.spatialX
                        tex.spatialY =  getattr(bpy.data.textures[mtex.name], "thea_TexSpatialYtex")
                        tex.spatialY = (tex.spatialY / tex.spatialY) / tex.spatialY

                        tex.offsetX = mtex.offset[0]
                        tex.offsetY = mtex.offset[1]
                        tex.scaleX = mtex.scale[0]
                        tex.scaleY = mtex.scale[1]
                        tex.projection = getattr(bpy.data.textures[mtex.name],"thea_texture_coords")
                        if tex.projection == 'Camera Map':
                            tex.cameraMapName = getattr(bpy.data.textures[mtex.name],"thea_camMapName")
#                        thea_globals.log.debug("*** Texture Coordinates: %s" % tex.projection)
#                        thea_globals.log.debug("Repeat: %s" % tex.repeat)
                        if getattr(bpy.data.textures[mtex.name],"thea_texture_coords") == 'UV':
                            tex.projection = "UV"
                            tex.UVChannel = getattr(bpy.data.textures[mtex.name], "thea_TexUVChannel")
#                        if mtex.texture_coords == 'GLOBAL':
#                            if mtex.mapping == 'CUBE':
#                                tex.projection = "Cubic"
#                            if mtex.mapping == 'TUBE':
#                                tex.projection = "Cylindrical"
#                            if mtex.mapping == 'SPHERE':
#                                tex.projection = "Spherical"

                        if (type == "Stencil"):
                            if (mtex.use_stencil == 1):
                                texture = tex
                                return texture
                        if (type == "Diffuse"):
                            if (mtex.use_map_color_diffuse == 1):
                                texture = tex
                                return texture
                        if (type == "Reflectance"):
                            if (mtex.use_map_color_spec == 1):
                                texture = tex
                                return texture
                        if (type == "Reflect90"):
                            if (mtex.use_map_color_spec == 1):
                                texture = tex
                                return texture
                        if (type == "Translucent"):
                            if (mtex.use_map_translucency == 1):
                                texture = tex
                                return texture
                        if (type == "Transmittance"):
                            if (mtex.use_map_alpha == 1):
                                texture = tex
                                return texture
                        if (type == "ThinFilmThickness"):
                            if (mtex.texture.thea_ThinFilmThicknessTex == 1):
                                texture = tex
                                return texture
                        if (type == "Bump"):
                            if (mtex.use_map_normal == 1):
                                texture = tex
                                return texture
                        if (type == "Roughness"):
                            if (mtex.use_map_hardness == 1):
                                texture = tex
                                return texture
                        if (type == "RoughnessTr"):
                            if (mtex.texture.thea_RoughnessTrTex == 1):
                                texture = tex
                                return texture
                        if (type == "Sigma"):
                            if (mtex.texture.thea_StructureSigmaTex == 1):
                                texture = tex
                                return texture
#                            CHANGED> Added Anis and rotation
                        if (type == "Anisotropy"):
                            if (mtex.texture.thea_StructureAnisotropyTex == 1):
                                texture = tex
                                return texture
                            if (mtex.texture.thea_CoatingStructureAnisotropyTex == 1):
                                texture = tex
                                return texture
                        if (type == "Rotation"):
                            if (mtex.texture.thea_StructureRotationTex == 1):
                                texture = tex
                                return texture
                            if (mtex.texture.thea_CoatingStructureRotationTex == 1):
                                texture = tex
                                return texture
                        if (type == "Thickness"):
                            if (mtex.texture.thea_CoatingThicknessTex == 1):
                                texture = tex
                                return texture
#                       CHANEGED > Added so thickness absorption color/tex
                        if (type == "ThicknessAbsorption"):
                            thea_globals.log.debug("ThicknessAbsorption: %s" % mtex.texture.thea_CoatingAbsorptionTex)
                            if (mtex.texture.thea_CoatingAbsorptionTex):
                                texture = tex
                                return texture
#                            if (mtex.texture.thea_CoatingAbsorptionTex == 0):
#                                texture = tex
#                                return texture
                        if (type == "Absorption"):
                            if (mtex.texture.thea_MediumAbsorptionTex == 1):
                                texture = tex
                                return texture
                        if (type == "Scatter"):
                            if (mtex.texture.thea_MediumScatterTex == 1):
                                texture = tex
                                return texture
                        if (type == "AbsorptionDensity"):
                            if (mtex.texture.thea_MediumAbsorptionDensityTex == 1):
                                texture = tex
                                return texture
                        if (type == "ScatterDensity"):
                            if (mtex.texture.thea_MediumScatterDensityTex == 1):
                                texture = tex
                                return texture
                        if (type == "Alpha"):
                            if (mtex.use_map_alpha == 1):
                                texture = tex
                                return texture
                        if (type == "Displacement"):
                            if (mtex.use_map_displacement == 1):
                                texture = tex
                                return texture
                        if (type == "Emittance"):
                            if (mtex.texture.thea_Emittance == 1):
                                texture = tex
                                return texture

            return texture


        thea_globals.log.debug("Material %s" % mat.getName())

        if mat.blenderMat.use_only_shadow:
            mat.shadowOnly = True
        else:
            mat.shadowCatcher = getattr(mat.blenderMat, 'thea_ShadowCatcher', False)
            mat.twosided = getattr(mat.blenderMat, 'thea_twoSided', False)
            mat.repaintable = getattr(mat.blenderMat, 'thea_repaintable', False)
            mat.dirt = getattr(mat.blenderMat, 'thea_dirt', False)
            mat.description = getattr(mat.blenderMat, 'thea_description', False)
            layerAdded = False
            hasBasic = getattr(mat.blenderMat, 'thea_Basic', False)
            hasBasic2 = getattr(mat.blenderMat, 'thea_Basic2', False)
            hasGlossy = getattr(mat.blenderMat, 'thea_Glossy', False)
            hasGlossy2 = getattr(mat.blenderMat, 'thea_Glossy2', False)
            hasSSS = getattr(mat.blenderMat, 'thea_SSS', False)
            hasThinFilm = getattr(mat.blenderMat, 'thea_ThinFilm', False)
            hasCoating = getattr(mat.blenderMat, 'thea_Coating', False)
            hasDisplacement = getattr(mat.blenderMat, 'thea_Displacement', False)
            hasClipping = getattr(mat.blenderMat, 'thea_Clipping', False)
            hasEmittance = getattr(mat.blenderMat, 'thea_Emittance', False)
            hasMedium = getattr(mat.blenderMat, 'thea_Medium', False)

            if hasBasic:
                wtex = False
                bsdf = BasicBSDF()
                wtex = getTexture(type="Stencil", component="thea_Basic")
                if wtex:
                        laySubstrate = LayeredSubstrate(bsdf, 1)
                        laySubstrate.setWeightTexture(wtex)
                else:
                    try:
                        layerWeight = getattr(mat.blenderMat, 'thea_BasicWeight') / 100
                    except:
                        layerWeight = 1
                    laySubstrate = LayeredSubstrate(bsdf, layerWeight)

#                bsdf.setDiffuseTexture(getTexture(type="Diffuse", component="thea_Basic"))
                if (((getattr(mat.blenderMat, 'diffuse_color')[0], getattr(mat.blenderMat, 'diffuse_color')[1], getattr(mat.blenderMat, 'diffuse_color')[2])) != (0,0,0)) or len(getattr(mat.blenderMat, 'thea_BasicDiffuseFilename'))>1:
                    bsdf.setDiffuseTexture(getTexture(type="Diffuse", component="thea_Basic"))
                if (((getattr(mat.blenderMat, 'thea_BasicReflectanceCol')[0], getattr(mat.blenderMat, 'thea_BasicReflectanceCol')[1], getattr(mat.blenderMat, 'thea_BasicReflectanceCol')[2])) != (0,0,0)) or len(getattr(mat.blenderMat, 'thea_BasicReflectanceFilename'))>1:
                    bsdf.setReflectanceTexture(getTexture(type="Reflectance", component="thea_Basic"))
                    if getattr(mat.blenderMat,'thea_BasicReflectionCurve'):
                        bsdf.setcustomCurve(Reflection90CurveList(getattr(mat.blenderMat,'thea_BasicReflectionCurve'), getattr(mat.blenderMat,'thea_BasicReflectCurveList')))
#                thea_globals.log.debug("Reflectance 90 Texture: %s - File: %s" % ((len(getattr(mat.blenderMat, 'thea_BasicReflect90Filename'))>1), getattr(mat.blenderMat, 'thea_BasicDiffuseFilename')))
#                thea_globals.log.debug("Reflectance 90 Color: %s - File: %s" % ((((getattr(mat.blenderMat, 'thea_BasicReflect90Col')[0], getattr(mat.blenderMat, 'thea_BasicReflect90Col')[1], getattr(mat.blenderMat, 'thea_BasicReflect90Col')[2])) != (0,0,0)),(len(getattr(mat.blenderMat, 'thea_BasicReflect90Filename'))>1)))
                if (((getattr(mat.blenderMat, 'thea_BasicReflect90Col')[0], getattr(mat.blenderMat, 'thea_BasicReflect90Col')[1], getattr(mat.blenderMat, 'thea_BasicReflect90Col')[2])) != (0,0,0)) or len(getattr(mat.blenderMat, 'thea_BasicReflect90Filename'))>1:
                    bsdf.setReflect90Texture(getTexture(type="Reflect90", component="thea_Basic"))
                if (((getattr(mat.blenderMat, 'thea_BasicTranslucentCol')[0], getattr(mat.blenderMat, 'thea_BasicTranslucentCol')[1], getattr(mat.blenderMat, 'thea_BasicTranslucentCol')[2])) != (0,0,0)) or len(getattr(mat.blenderMat, 'thea_BasicTranslucentFilename'))>1:
                    bsdf.setTranslucentTexture(getTexture(type="Translucent", component="thea_Basic"))
                bsdf.setRoughnessTexture(getTexture(type="Roughness", component="thea_Basic"))
                bsdf.setBumpTexture(getTexture(type="Bump", component="thea_Basic"))
                bsdf.setSigmaTexture(getTexture(type="Sigma", component="thea_Basic"))
                bsdf.setAnisotropyTexture(getTexture(type="Anisotropy", component="thea_Basic"))
                bsdf.setRotationTexture(getTexture(type="Rotation", component="thea_Basic"))
                try:
                    bsdf.setAbsorptionColor(RgbTexture(getattr(mat.blenderMat, 'thea_BasicAbsorptionCol')[0],getattr(mat.blenderMat, 'thea_BasicAbsorptionCol')[1],getattr(mat.blenderMat, 'thea_BasicAbsorptionCol')[2]))
                except:
                    bsdf.setAbsorptionColor(RgbTexture(0,0,0))
                try:
                    bsdf.setAbsorptionDensity(getattr(mat.blenderMat, 'thea_BasicAbsorption'))
                except:
                    bsdf.setAbsorptionDensity(0.0)
                try:
                    if getattr(mat.blenderMat, 'thea_BasicIOR'):
                        bsdf.setIndexOfRefraction(getattr(mat.blenderMat, 'thea_BasicIOR'))
                    else:
                        bsdf.setIndexOfRefraction(1.5)
                except:
                    bsdf.setIndexOfRefraction(1.5)
                try:
                    bsdf.setExtinctionCoefficient(getattr(mat.blenderMat, 'thea_BasicEC'))
                except:
                    bsdf.setExtinctionCoefficient(0.0)
                try:
                    bsdf.setSigma(getattr(mat.blenderMat, 'thea_BasicStructureSigma')/100)
                except:
                    bsdf.setSigma(0.0)
                bsdf.setRoughness(getattr(mat.blenderMat,'thea_BasicStructureRoughness',10)/100)
                try:
                    bsdf.setAnisotropy(getattr(mat.blenderMat, 'thea_BasicStructureAnisotropy')/100)
                except:
                    bsdf.setAnisotropy(0.0)
                try:
                    bsdf.setRotation(getattr(mat.blenderMat, 'thea_BasicStructureRotation'))
                except:
                    bsdf.setRotation(0.0)
                try:
                    bsdf.setNormalMapping(getattr(mat.blenderMat, 'thea_BasicStructureNormal'))
                except:
                    bsdf.setNormalMapping(False)
                try:
                    bsdf.setBump(getattr(mat.blenderMat, 'thea_BasicStructureBump')/100)
                except:
                    bsdf.setBump(1.0)
                #try:
                bsdf.setTraceReflections(getattr(mat.blenderMat,'thea_BasicTrace'))
                bsdf.setMicroRoughnessEnable(getattr(mat.blenderMat,'thea_BasicMicroRoughness'))
                bsdf.setMicroRoughnessWidth(getattr(mat.blenderMat,'thea_BasicMicroRoughnessWidth'))
                bsdf.setMicroRoughnessHeight(getattr(mat.blenderMat,'thea_BasicMicroRoughnessHeight'))

                #except:
                #    bsdf.setTraceReflections(True)
                laySubstrate.order = getattr(mat.blenderMat, 'thea_BasicOrder', 0)
                mat.layeredBsdf.addSubstrate(laySubstrate)
            if hasBasic2:
                wtex = False
                bsdf = BasicBSDF()
#                bsdf.setDiffuseTexture(getTexture(type="Diffuse", component="thea_Basic2"))
                if (((getattr(mat.blenderMat, 'diffuse_color')[0], getattr(mat.blenderMat, 'diffuse_color')[1], getattr(mat.blenderMat, 'diffuse_color')[2])) != (0,0,0)) or len(getattr(mat.blenderMat, 'thea_Basic2DiffuseFilename'))>1:
                    bsdf.setDiffuseTexture(getTexture(type="Diffuse", component="thea_Basic2"))
                if (((getattr(mat.blenderMat, 'thea_Basic2ReflectanceCol')[0], getattr(mat.blenderMat, 'thea_Basic2ReflectanceCol')[1], getattr(mat.blenderMat, 'thea_Basic2ReflectanceCol')[2])) != (0,0,0)) or len(getattr(mat.blenderMat, 'thea_Basic2ReflectanceFilename'))>1:
                    bsdf.setReflectanceTexture(getTexture(type="Reflectance", component="thea_Basic2"))
                    if getattr(mat.blenderMat,'thea_Basic2ReflectionCurve'):
                        bsdf.setcustomCurve(Reflection90CurveList(getattr(mat.blenderMat,'thea_Basic2ReflectionCurve'), getattr(mat.blenderMat,'thea_Basic2ReflectCurveList')))
                if (((getattr(mat.blenderMat, 'thea_Basic2Reflect90Col')[0], getattr(mat.blenderMat, 'thea_Basic2Reflect90Col')[1], getattr(mat.blenderMat, 'thea_Basic2Reflect90Col')[2])) != (0,0,0)) or len(getattr(mat.blenderMat, 'thea_Basic2Reflect90Filename'))>1:
                    bsdf.setReflect90Texture(getTexture(type="Reflect90", component="thea_Basic"))
                if (((getattr(mat.blenderMat, 'thea_Basic2TranslucentCol')[0], getattr(mat.blenderMat, 'thea_Basic2TranslucentCol')[1], getattr(mat.blenderMat, 'thea_Basic2TranslucentCol')[2])) != (0,0,0)) or len(getattr(mat.blenderMat, 'thea_Basic2TranslucentFilename'))>1:
                    bsdf.setTranslucentTexture(getTexture(type="Translucent", component="thea_Basic2"))
                bsdf.setRoughnessTexture(getTexture(type="Roughness", component="thea_Basic2"))
                bsdf.setBumpTexture(getTexture(type="Bump", component="thea_Basic2"))
                bsdf.setSigmaTexture(getTexture(type="Sigma", component="thea_Basic2"))
                bsdf.setAnisotropyTexture(getTexture(type="Anisotropy", component="thea_Basic2"))
                bsdf.setRotationTexture(getTexture(type="Rotation", component="thea_Basic2"))
                try:
                    bsdf.setAbsorptionColor(RgbTexture(getattr(mat.blenderMat, 'thea_Basic2AbsorptionCol')[0],getattr(mat.blenderMat, 'thea_Basic2AbsorptionCol')[1],getattr(mat.blenderMat, 'thea_Basic2AbsorptionCol')[2]))
                except:
                    bsdf.setAbsorptionColor(RgbTexture(0,0,0))
                try:
                    bsdf.setAbsorptionDensity(getattr(mat.blenderMat, 'thea_Basic2Absorption'))
                except:
                    bsdf.setAbsorptionDensity(0.0)
                try:
                    if getattr(mat.blenderMat, 'thea_Basic2IOR'):
                        bsdf.setIndexOfRefraction(getattr(mat.blenderMat, 'thea_Basic2IOR'))
                    else:
                        bsdf.setIndexOfRefraction(1.5)
                except:
                    bsdf.setIndexOfRefraction(1.5)
                try:
                    bsdf.setExtinctionCoefficient(getattr(mat.blenderMat, 'thea_Basic2EC'))
                except:
                    bsdf.setExtinctionCoefficient(0.0)
                try:
                    bsdf.setSigma(getattr(mat.blenderMat, 'thea_Basic2StructureSigma')/100)
                except:
                    bsdf.setSigma(0.0)
                bsdf.setRoughness(getattr(mat.blenderMat,'thea_Basic2StructureRoughness',10)/100)
                try:
                    bsdf.setAnisotropy(getattr(mat.blenderMat, 'thea_Basic2StructureAnisotropy')/100)
                except:
                    bsdf.setAnisotropy(0.0)
                try:
                    bsdf.setRotation(getattr(mat.blenderMat, 'thea_Basic2StructureRotation'))
                except:
                    bsdf.setRotation(0.0)
                try:
                    bsdf.setNormalMapping(getattr(mat.blenderMat, 'thea_Basic2StructureNormal'))
                except:
                    bsdf.setNormalMapping(False)
                try:
                    bsdf.setBump(getattr(mat.blenderMat, 'thea_Basic2StructureBump')/100)
                except:
                    bsdf.setBump(1.0)
                bsdf.setTraceReflections(getattr(mat.blenderMat, 'thea_Basic2Trace'))
                bsdf.setMicroRoughnessEnable(getattr(mat.blenderMat,'thea_Basic2MicroRoughness'))
                bsdf.setMicroRoughnessWidth(getattr(mat.blenderMat,'thea_Basic2MicroRoughnessWidth'))
                bsdf.setMicroRoughnessHeight(getattr(mat.blenderMat,'thea_Basic2MicroRoughnessHeight'))
#                bsdf.setCustomCurve(getattr(mat.blenderMat,'thea_2ReflectionCurve'))
#                bsdf.setCustomCurveList(getattr(mat.blenderMat,'thea_BasicReflectCurveList'))

                wtex = getTexture(type="Stencil", component="thea_Basic2")
                thea_globals.log.debug("wtex: %s" % (wtex))
                #if layerAdded: #if already have layer

                if wtex:
                    laySubstrate = LayeredSubstrate(bsdf, 1)
                    laySubstrate.setWeightTexture(wtex)
                else:
                    try:
                        layerWeight = getattr(mat.blenderMat, 'thea_Basic2Weight') / 100
                    except:
                        layerWeight = 1
                    laySubstrate = LayeredSubstrate(bsdf, layerWeight)
                laySubstrate.order = getattr(mat.blenderMat, 'thea_Basic2Order', 0)
                mat.layeredBsdf.addSubstrate(laySubstrate)
#                 else:
#                     if wtex:
#                         mat.setBSDF(bsdf,wTex=wtex)
#                     else:
#                         mat.setBSDF(bsdf)
#                     mat.setBSDF(bsdf)
#                 layerAdded = True
            if hasGlossy:
                wtex = False
                bsdf = GlossyBSDF()
#                bsdf.setReflectanceTexture(getTexture(type="Reflectance", component="thea_Glossy"))
                if (((getattr(mat.blenderMat, 'thea_GlossyReflectanceCol')[0], getattr(mat.blenderMat, 'thea_GlossyReflectanceCol')[1], getattr(mat.blenderMat, 'thea_GlossyReflectanceCol')[2])) != (0,0,0)) or len(getattr(mat.blenderMat, 'thea_Glossy2ReflectanceFilename'))>1:
                    bsdf.setReflectanceTexture(getTexture(type="Reflectance", component="thea_Glossy"))
                    if getattr(mat.blenderMat,'thea_GlossyReflectionCurve'):
                        bsdf.setcustomCurve(Reflection90CurveList(getattr(mat.blenderMat,'thea_GlossyReflectionCurve'), getattr(mat.blenderMat,'thea_GlossyReflectCurveList')))
                if (((getattr(mat.blenderMat, 'thea_GlossyReflect90Col')[0], getattr(mat.blenderMat, 'thea_GlossyReflect90Col')[1], getattr(mat.blenderMat, 'thea_GlossyReflect90Col')[2])) != (0,0,0)) or len(getattr(mat.blenderMat, 'thea_GlossyReflect90Filename'))>1:
                    bsdf.setReflect90Texture(getTexture(type="Reflect90", component="thea_Glossy"))
                bsdf.setTransmittanceTexture(getTexture(type="Transmittance", component="thea_Glossy"))
                bsdf.setRoughnessTexture(getTexture(type="Roughness", component="thea_Glossy"))
                bsdf.setRoughnessTrTexture(getTexture(type="RoughnessTr", component="thea_Glossy"))
                bsdf.setBumpTexture(getTexture(type="Bump", component="thea_Glossy"))
                bsdf.setAnisotropyTexture(getTexture(type="Anisotropy", component="thea_Glossy"))
                bsdf.setRotationTexture(getTexture(type="Rotation", component="thea_Glossy"))
                try:
                    bsdf.setAbsorptionColor(RgbTexture(getattr(mat.blenderMat, 'thea_GlossyAbsorptionCol')[0],getattr(mat.blenderMat, 'thea_GlossyAbsorptionCol')[1],getattr(mat.blenderMat, 'thea_GlossyAbsorptionCol')[2]))
                except:
                    bsdf.setAbsorptionColor(RgbTexture(0,0,0))
                try:
                    bsdf.setAbsorptionDensity(getattr(mat.blenderMat, 'thea_GlossyAbsorption'))
                except:
                    bsdf.setAbsorptionDensity(0.0)
                try:
                    if getattr(mat.blenderMat, 'thea_GlossyIOR'):
                        bsdf.setIndexOfRefraction(getattr(mat.blenderMat, 'thea_GlossyIOR'))
                    else:
                        bsdf.setIndexOfRefraction(1.5)
                except:
                    bsdf.setIndexOfRefraction(1.5)
                try:
                    bsdf.setExtinctionCoefficient(getattr(mat.blenderMat, 'thea_GlossyEC'))
                except:
                    bsdf.setExtinctionCoefficient(0.0)
                try:
                    bsdf.setAbbeNumberEnable(getattr(mat.blenderMat, 'thea_GlossyAbbeNumberEnable'))
                except:
                    bsdf.setAbbeNumberEnable(False)
                try:
                    bsdf.setAbbeNumber(getattr(mat.blenderMat, 'thea_GlossyAbbeNumber'))
                except:
                    bsdf.setAbbeNumber(50.0)
                if getattr(mat.blenderMat, "thea_GlossyIORFileEnable"):
                    bsdf.iorFilenameEnable = True
                    from TheaForBlender.thea_render_main import getTheaIORMenuItems
                    bsdf.iorFilename = getTheaIORMenuItems()[int(getattr(mat.blenderMat, "thea_GlossyIORMenu"))-1][1]+".ior"
                bsdf.setRoughness(getattr(mat.blenderMat,'thea_GlossyStructureRoughness',10)/100)
                try:
                    bsdf.setRoughnessTrEnable(getattr(mat.blenderMat, 'thea_GlossyStructureRoughTrEn'))
                except:
                    bsdf.setRoughnessTrEnable(False)
                try:
                    bsdf.setRoughnessTr(getattr(mat.blenderMat, 'thea_GlossyStructureRoughnessTr')/100)
                except:
                    bsdf.setRoughnessTr(0.0)
                try:
                    bsdf.setAnisotropy(getattr(mat.blenderMat, 'thea_GlossyStructureAnisotropy')/100)
                except:
                    bsdf.setAnisotropy(0.0)
                try:
                    bsdf.setRotation(getattr(mat.blenderMat, 'thea_GlossyStructureRotation'))
                except:
                    bsdf.setRotation(0.0)
                try:
                    bsdf.setNormalMapping(getattr(mat.blenderMat, 'thea_GlossyStructureNormal'))
                except:
                    bsdf.setNormalMapping(False)
                try:
                    bsdf.setBump(getattr(mat.blenderMat, 'thea_GlossyStructureBump')/100)
                except:
                    bsdf.setBump(1.0)
                try:
                    if getattr(mat.blenderMat, 'thea_GlossyTraceReflections'):
                        bsdf.setTraceReflections(getattr(mat.blenderMat, 'thea_GlossyTraceReflections'))
                    else:
                        bsdf.setTraceReflections(True)
                except:
                    bsdf.setTraceReflections(True)
                try:
                    if getattr(mat.blenderMat, 'thea_GlossyTraceRefractions'):
                        bsdf.setTraceRefractions(getattr(mat.blenderMat, 'thea_GlossyTraceRefractions'))
                    else:
                        bsdf.setTraceRefractions(True)
                except:
                    bsdf.setTraceRefractions(True)
                bsdf.setMicroRoughnessEnable(getattr(mat.blenderMat,'thea_GlossyMicroRoughness'))
                bsdf.setMicroRoughnessWidth(getattr(mat.blenderMat,'thea_GlossyMicroRoughnessWidth'))
                bsdf.setMicroRoughnessHeight(getattr(mat.blenderMat,'thea_GlossyMicroRoughnessHeight'))
#                bsdf.setCustomCurve(getattr(mat.blenderMat,'thea_BasicReflectionCurve'))
#                bsdf.setCustomCurveList(getattr(mat.blenderMat,'thea_BasicReflectCurveList'))
                wtex = getTexture(type="Stencil", component="thea_Glossy")
                #print("wtex glossy: ", wtex)
#                 if layerAdded: #if already have layer
                if wtex:
                    laySubstrate = LayeredSubstrate(bsdf, 1)
                    laySubstrate.setWeightTexture(wtex)
                else:
                    try:
                        layerWeight = getattr(mat.blenderMat, 'thea_GlossyWeight') / 100
                    except:
                        layerWeight = 1
                    laySubstrate = LayeredSubstrate(bsdf, layerWeight)
                laySubstrate.order = getattr(mat.blenderMat, 'thea_GlossyOrder', 0)
                mat.layeredBsdf.addSubstrate(laySubstrate)
            if hasGlossy2:
                wtex = False
                bsdf = GlossyBSDF()
#                bsdf.setReflectanceTexture(getTexture(type="Reflectance", component="thea_Glossy2"))
                if (((getattr(mat.blenderMat, 'thea_Glossy2ReflectanceCol')[0], getattr(mat.blenderMat, 'thea_Glossy2ReflectanceCol')[1], getattr(mat.blenderMat, 'thea_Glossy2ReflectanceCol')[2])) != (0,0,0)) or len(getattr(mat.blenderMat, 'thea_Glossy2ReflectanceFilename'))>1:
                    bsdf.setReflectanceTexture(getTexture(type="Reflectance", component="thea_Glossy2"))
                    if getattr(mat.blenderMat,'thea_Glossy2ReflectionCurve'):
                        bsdf.setcustomCurve(Reflection90CurveList(getattr(mat.blenderMat,'thea_Glossy2ReflectionCurve'), getattr(mat.blenderMat,'thea_Glossy2ReflectCurveList')))
                if (((getattr(mat.blenderMat, 'thea_Glossy2Reflect90Col')[0], getattr(mat.blenderMat, 'thea_Glossy2Reflect90Col')[1], getattr(mat.blenderMat, 'thea_Glossy2Reflect90Col')[2])) != (0,0,0)) or len(getattr(mat.blenderMat, 'thea_Glossy2Reflect90Filename'))>1:
                    bsdf.setReflect90Texture(getTexture(type="Reflect90", component="thea_Glossy2"))

                bsdf.setTransmittanceTexture(getTexture(type="Transmittance", component="thea_Glossy2"))
                bsdf.setRoughnessTexture(getTexture(type="Roughness", component="thea_Glossy2"))
                bsdf.setRoughnessTrTexture(getTexture(type="RoughnessTr", component="thea_Glossy2"))
                bsdf.setBumpTexture(getTexture(type="Bump", component="thea_Glossy2"))
                bsdf.setAnisotropyTexture(getTexture(type="Anisotropy", component="thea_Glossy2"))
                bsdf.setRotationTexture(getTexture(type="Rotation", component="thea_Glossy2"))
                try:
                    bsdf.setAbsorptionColor(RgbTexture(getattr(mat.blenderMat, 'thea_Glossy2AbsorptionCol')[0],getattr(mat.blenderMat, 'thea_Glossy2AbsorptionCol')[1],getattr(mat.blenderMat, 'thea_Glossy2AbsorptionCol')[2]))
                except:
                    bsdf.setAbsorptionColor(RgbTexture(0,0,0))
                try:
                    bsdf.setAbsorptionDensity(getattr(mat.blenderMat, 'thea_Glossy2Absorption'))
                except:
                    bsdf.setAbsorptionDensity(0.0)
                try:
                    if getattr(mat.blenderMat, 'thea_Glossy2IOR'):
                        bsdf.setIndexOfRefraction(getattr(mat.blenderMat, 'thea_Glossy2IOR'))
                    else:
                        bsdf.setIndexOfRefraction(1.5)
                except:
                    bsdf.setIndexOfRefraction(1.5)
                try:
                    bsdf.setExtinctionCoefficient(getattr(mat.blenderMat, 'thea_Glossy2EC'))
                except:
                    bsdf.setExtinctionCoefficient(0.0)
                try:
                    bsdf.setAbbeNumberEnable(getattr(mat.blenderMat, 'thea_Glossy2AbbeNumberEnable'))
                except:
                    bsdf.setAbbeNumberEnable(False)
                try:
                    bsdf.setAbbeNumber(getattr(mat.blenderMat, 'thea_Glossy2AbbeNumber'))
                except:
                    bsdf.setAbbeNumber(50.0)
                if getattr(mat.blenderMat, "thea_Glossy2IORFileEnable"):
                    bsdf.iorFilenameEnable = True
                    bsdf.iorFilename = getTheaIORMenuItems()[int(getattr(mat.blenderMat, "thea_Glossy2IORMenu"))-1][1]+".ior"
                bsdf.setRoughness(getattr(mat.blenderMat,'thea_Glossy2StructureRoughness',10)/100)
                try:
                    bsdf.setRoughnessTrEnable(getattr(mat.blenderMat, 'thea_Glossy2StructureRoughTrEn'))
                except:
                    bsdf.setRoughnessTrEnable(False)
                try:
                    bsdf.setRoughnessTr(getattr(mat.blenderMat, 'thea_Glossy2StructureRoughnessTr')/100)
                except:
                    bsdf.setRoughnessTr(0.0)
                try:
                    bsdf.setAnisotropy(getattr(mat.blenderMat, 'thea_Glossy2StructureAnisotropy')/100)
                except:
                    bsdf.setAnisotropy(0.0)
                try:
                    bsdf.setRotation(getattr(mat.blenderMat, 'thea_Glossy2StructureRotation'))
                except:
                    bsdf.setRotation(0.0)
                try:
                    bsdf.setNormalMapping(getattr(mat.blenderMat, 'thea_Glossy2StructureNormal'))
                except:
                    bsdf.setNormalMapping(False)
                try:
                    bsdf.setBump(getattr(mat.blenderMat, 'thea_Glossy2StructureBump')/100)
                except:
                    bsdf.setBump(1.0)
                try:
                    if getattr(mat.blenderMat, 'thea_Glossy2TraceReflections'):
                        bsdf.setTraceReflections(getattr(mat.blenderMat, 'thea_Glossy2TraceReflections'))
                    else:
                        bsdf.setTraceReflections(True)
                except:
                    bsdf.setTraceReflections(True)
                try:
                    if getattr(mat.blenderMat, 'thea_Glossy2TraceRefractions'):
                        bsdf.setTraceRefractions(getattr(mat.blenderMat, 'thea_Glossy2TraceRefractions'))
                    else:
                        bsdf.setTraceRefractions(True)
                except:
                    bsdf.setTraceRefractions(True)
                bsdf.setMicroRoughnessEnable(getattr(mat.blenderMat,'thea_Glossy2MicroRoughness'))
                bsdf.setMicroRoughnessWidth(getattr(mat.blenderMat,'thea_Glossy2MicroRoughnessWidth'))
                bsdf.setMicroRoughnessHeight(getattr(mat.blenderMat,'thea_Glossy2MicroRoughnessHeight'))
#                bsdf.setCustomCurve(getattr(mat.blenderMat,'thea_2ReflectionCurve'))
#                bsdf.setCustomCurveList(getattr(mat.blenderMat,'thea_BasicReflectCurveList'))
                wtex = getTexture(type="Stencil", component="thea_Glossy2")
#                 if layerAdded: #if already have layer
                if wtex:
                    laySubstrate = LayeredSubstrate(bsdf, 1)
                    laySubstrate.setWeightTexture(wtex)
                else:
                    try:
                        layerWeight = getattr(mat.blenderMat, 'thea_Glossy2Weight') / 100
                    except:
                        layerWeight = 1
                    laySubstrate = LayeredSubstrate(bsdf, layerWeight)
                laySubstrate.order = getattr(mat.blenderMat, 'thea_Glossy2Order', 0)
                mat.layeredBsdf.addSubstrate(laySubstrate)
            if hasSSS:
                wtex = False
                bsdf = SSS()
#                bsdf.setReflectanceTexture(getTexture(type="Reflectance", component="thea_SSS"))
                if (((getattr(mat.blenderMat, 'thea_SSSReflectanceCol')[0], getattr(mat.blenderMat, 'thea_SSSReflectanceCol')[1], getattr(mat.blenderMat, 'thea_SSSReflectanceCol')[2])) != (0,0,0)) or len(getattr(mat.blenderMat, 'thea_SSSReflectanceFilename'))>1:
                    bsdf.setReflectanceTexture(getTexture(type="Reflectance", component="thea_SSS"))
                    if getattr(mat.blenderMat,'thea_SSSReflectionCurve'):
                        bsdf.setcustomCurve(Reflection90CurveList(getattr(mat.blenderMat,'thea_SSSReflectionCurve'), getattr(mat.blenderMat,'thea_SSSReflectCurveList')))
                if (((getattr(mat.blenderMat, 'thea_SSSReflect90Col')[0], getattr(mat.blenderMat, 'thea_SSSReflect90Col')[1], getattr(mat.blenderMat, 'thea_SSSReflect90Col')[2])) != (0,0,0)) or len(getattr(mat.blenderMat, 'thea_SSSReflect90Filename'))>1:
                    bsdf.setReflect90Texture(getTexture(type="Reflect90", component="thea_SSS"))

                bsdf.setRoughnessTexture(getTexture(type="Roughness", component="thea_SSS"))
                bsdf.setRoughnessTrTexture(getTexture(type="RoughnessTr", component="thea_SSS"))
                bsdf.setBumpTexture(getTexture(type="Bump", component="thea_SSS"))
                bsdf.setAnisotropyTexture(getTexture(type="Anisotropy", component="thea_SSS"))
                bsdf.setRotationTexture(getTexture(type="Rotation", component="thea_SSS"))
                try:
                    bsdf.setAbsorptionColor(RgbTexture(getattr(mat.blenderMat, 'thea_SSSAbsorptionCol')[0],getattr(mat.blenderMat, 'thea_SSSAbsorptionCol')[1],getattr(mat.blenderMat, 'thea_SSSAbsorptionCol')[2]))
                except:
                    bsdf.setAbsorptionColor(RgbTexture(0,0,0))
#                 try:
                bsdf.setAbsorptionDensity(getattr(mat.blenderMat, 'thea_SSSAbsorption'))
#                 except:
#                     bsdf.setAbsorptionDensity(0.0)
                try:
                    bsdf.setScatteringColor(RgbTexture(getattr(mat.blenderMat, 'thea_SSSScatteringCol')[0],getattr(mat.blenderMat, 'thea_SSSScatteringCol')[1],getattr(mat.blenderMat, 'thea_SSSScatteringCol')[2]))
                except:
                    bsdf.setScatteringColor(RgbTexture(0,0,0))
#                 try:
                bsdf.setScatteringDensity(getattr(mat.blenderMat, 'thea_SSSScattering'))
#                 except:
#                     bsdf.setScatteringDensity(0.0)
                try:
                    bsdf.setAsymetry(getattr(mat.blenderMat, 'thea_SSSAsymetry'))
                except:
                    bsdf.setAsymetry(0.0)
                try:
                    if getattr(mat.blenderMat, 'thea_SSSIOR'):
                        bsdf.setIndexOfRefraction(getattr(mat.blenderMat, 'thea_SSSIOR'))
                    else:
                        bsdf.setIndexOfRefraction(1.5)
                except:
                    bsdf.setIndexOfRefraction(1.5)
                bsdf.setRoughness(getattr(mat.blenderMat,'thea_SSSStructureRoughness',10)/100)
                try:
                    bsdf.setRoughnessTrEnable(getattr(mat.blenderMat, 'thea_SSSStructureRoughTrEn'))
                except:
                    bsdf.setRoughnessTrEnable(False)
                try:
                    bsdf.setRoughnessTr(getattr(mat.blenderMat, 'thea_SSSStructureRoughnessTr')/100)
                except:
                    bsdf.setRoughnessTr(0.0)
                try:
                    bsdf.setAnisotropy(getattr(mat.blenderMat, 'thea_SSSStructureAnisotropy')/100)
                except:
                    bsdf.setAnisotropy(0.0)
                try:
                    bsdf.setRotation(getattr(mat.blenderMat, 'thea_SSSStructureRotation'))
                except:
                    bsdf.setRotation(0.0)
                try:
                    bsdf.setNormalMapping(getattr(mat.blenderMat, 'thea_SSSStructureNormal'))
                except:
                    bsdf.setNormalMapping(False)
                try:
                    bsdf.setBump(getattr(mat.blenderMat, 'thea_SSSStructureBump')/100)
                except:
                    bsdf.setBump(1.0)
                try:
                    if getattr(mat.blenderMat, 'thea_SSSTraceReflections'):
                        bsdf.setTraceReflections(getattr(mat.blenderMat, 'thea_SSSTraceReflections'))
                    else:
                        bsdf.setTraceReflections(True)
                except:
                    bsdf.setTraceReflections(True)
                try:
                    if getattr(mat.blenderMat, 'thea_SSSTraceRefractions'):
                        bsdf.setTraceRefractions(getattr(mat.blenderMat, 'thea_SSSTraceRefractions'))
                    else:
                        bsdf.setTraceRefractions(True)
                except:
                    bsdf.setTraceRefractions(True)
                bsdf.setMicroRoughnessEnable(getattr(mat.blenderMat,'thea_SSSMicroRoughness'))
                bsdf.setMicroRoughnessWidth(getattr(mat.blenderMat,'thea_SSSMicroRoughnessWidth'))
                bsdf.setMicroRoughnessHeight(getattr(mat.blenderMat,'thea_SSSMicroRoughnessHeight'))
                wtex = getTexture(type="Stencil", component="thea_SSS")
#                 if layerAdded: #if already have layer
                if wtex:
                    laySubstrate = LayeredSubstrate(bsdf, 1)
                    laySubstrate.setWeightTexture(wtex)
                else:
                    try:
                        layerWeight = getattr(mat.blenderMat, 'thea_SSSWeight') / 100
                    except:
                        layerWeight = 1
                    laySubstrate = LayeredSubstrate(bsdf, layerWeight)
                laySubstrate.order = getattr(mat.blenderMat, 'thea_SSSOrder', 0)
                mat.layeredBsdf.addSubstrate(laySubstrate)
#                 else:
#                     if wtex:
#                         mat.setBSDF(bsdf,wTex=wtex)
#                     else:
#                         mat.setBSDF(bsdf)
#                     mat.setBSDF(bsdf)
#                 layerAdded = True

            if hasThinFilm:
                wtex = False
                bsdf = ThinFilm()
                bsdf.setTransmittanceTexture(getTexture(type="Transmittance", component="thea_ThinFilm"))
                bsdf.setBumpTexture(getTexture(type="Bump", component="thea_ThinFilm"))
                #bsdf.setThinThicknessTexture=getTexture(type="ThinFilmThickness", component="thea_ThinFilm")
                #print("NAme file:", bsdf.setThinThicknessTexture)
                try:
#                    CHANGED > Was set to GloddyIOR and got the wrong IOR number
                    if getattr(mat.blenderMat, 'thea_ThinFilmIOR'):
                        bsdf.setIndexOfRefraction(getattr(mat.blenderMat, 'thea_ThinFilmIOR'))
                    else:
                        bsdf.setIndexOfRefraction(1.5)
                except:
                    bsdf.setIndexOfRefraction(1.5)
                try:
                    bsdf.setInterference(getattr(mat.blenderMat, 'thea_ThinFilmInterference'))
                except:
                    bsdf.setInterference(False)
#                 try:
                if getattr(mat.blenderMat, 'thea_ThinFilmThickness', False):
                    bsdf.setThickness(getattr(mat.blenderMat, 'thea_ThinFilmThickness'))
                else:
                    bsdf.setThickness(500)
                if getattr(mat.blenderMat, "thea_ThinFilmThicknessFilename")!="":
                    bsdf.setThinThicknessTexture(getTexture(type="ThinFilmThickness", component="thea_ThinFilm"))
                try:
                    bsdf.setNormalMapping(getattr(mat.blenderMat, 'thea_GlossyStructureNormal'))
                except:
                    bsdf.setNormalMapping(False)
                try:
                    bsdf.setBump(getattr(mat.blenderMat, 'thea_GlossyStructureBump')/100)
                except:
                    bsdf.setBump(1.0)
                wtex = getTexture(type="Stencil", component="thea_ThinFilm")
#                 if layerAdded: #if already have layer
                if wtex:
                    laySubstrate = LayeredSubstrate(bsdf, 1)
                    laySubstrate.setWeightTexture(wtex)
                else:
                    try:
                        layerWeight = getattr(mat.blenderMat, 'thea_ThinFilmWeight') / 100
                    except:
                        layerWeight = 1
                    laySubstrate = LayeredSubstrate(bsdf, layerWeight)
                laySubstrate.order = getattr(mat.blenderMat, 'thea_ThinFilmOrder', 0)
                mat.layeredBsdf.addSubstrate(laySubstrate)
#                 else:
#                     if wtex:
#                         mat.setBSDF(bsdf,wTex=wtex)
#                     else:
#                         mat.setBSDF(bsdf)
#                     mat.setBSDF(bsdf)
#                 layerAdded = True


            if hasCoating:
                wtex = False
                coating = CoatingBSDF()
#                coating.setReflectanceTexture(getTexture(type="Reflectance", component="thea_Coating"))
                if (((getattr(mat.blenderMat, 'thea_CoatingReflectanceCol')[0], getattr(mat.blenderMat, 'thea_CoatingReflectanceCol')[1], getattr(mat.blenderMat, 'thea_CoatingReflectanceCol')[2])) != (0,0,0)) or len(getattr(mat.blenderMat, 'thea_CoatingReflectanceFilename'))>1:
                    coating.setReflectanceTexture(getTexture(type="Reflectance", component="thea_Coating"))
                    if getattr(mat.blenderMat,'thea_CoatingReflectionCurve'):
                        coating.setcustomCurve(Reflection90CurveList(getattr(mat.blenderMat,'thea_CoatingReflectionCurve'), getattr(mat.blenderMat,'thea_CoatingReflectCurveList')))
                if (((getattr(mat.blenderMat, 'thea_CoatingReflect90Col')[0], getattr(mat.blenderMat, 'thea_CoatingReflect90Col')[1], getattr(mat.blenderMat, 'thea_CoatingReflect90Col')[2])) != (0,0,0)) or len(getattr(mat.blenderMat, 'thea_CoatingReflect90Filename'))>1:
                    coating.setReflect90Texture(getTexture(type="Reflect90", component="thea_Coating"))

                coating.setRoughnessTexture(getTexture(type="Roughness", component="thea_Coating"))
#                CHANGED> ADDED anis and rotation
                coating.setAnisotropyTexture(getTexture(type="Anisotropy", component="thea_Coating"))
                coating.setRotationTexture(getTexture(type="Rotation", component="thea_Coating"))
                coating.setBumpTexture(getTexture(type="Bump", component="thea_Coating"))
                coating.setThicknessTexture(getTexture(type="Thickness", component="thea_Coating"))
#                CHANGED > Added enable state for absorption color
#                 try:
                if getattr(mat.blenderMat, 'thea_CoatingAbsorptionEnable', False):
                    coating.setAbsorptionEnable(True)
                    coating.setThicknessAbsorptionTexture(getTexture(type="ThicknessAbsorption", component="thea_Coating"))
                else:
                    coating.setAbsorptionEnable(False)
                    coating.setThicknessAbsorptionTexture(False)
#                 except:
#                     coating.setAbsorptionEnable(True)
                try:
                    if getattr(mat.blenderMat, 'thea_CoatingIOR'):
                        coating.setIndexOfRefraction(getattr(mat.blenderMat, 'thea_CoatingIOR'))
                    else:
                        coating.setIndexOfRefraction(1.5)
                except:
                    coating.setIndexOfRefraction(1.5)
                try:
                    coating.setExtinctionCoefficient(getattr(mat.blenderMat, 'thea_CoatingEC'))
                except:
                    coating.setExtinctionCoefficient(0.0)
                try:
                    coating.setThicknessEnable(getattr(mat.blenderMat, 'thea_CoatingThicknessEnable'))
                except:
                    coating.setThicknessEnable(False)
                try:
                    coating.setThickness(getattr(mat.blenderMat, 'thea_CoatingThickness'))
                except:
                    coating.setThickness(100.0)
                coating.setRoughness(getattr(mat.blenderMat,'thea_CoatingStructureRoughness',10)/100)

                try:
                    coating.setAnisotropy(getattr(mat.blenderMat, 'thea_CoatingStructureAnisotropy')/100)
                except:
                    coating.setAnisotropy(0.0)
                try:
                    coating.setRotation(getattr(mat.blenderMat, 'thea_CoatingStructureRotation'))
                except:
                    coating.setRotation(0.0)
                try:
                    coating.setNormalMapping(getattr(mat.blenderMat, 'thea_CoatingStructureNormal'))
                except:
                    coating.setNormalMapping(False)
                try:
                    coating.setBump(getattr(mat.blenderMat, 'thea_CoatingStructureBump')/100)
                except:
                    coating.setBump(1.0)
                try:
                    if getattr(mat.blenderMat, 'thea_CoatingTraceReflections'):
                        coating.setTraceReflections(getattr(mat.blenderMat, 'thea_CoatingTraceReflections'))
                    else:
                        coating.setTraceReflections(True)
                except:
                    coating.setTraceReflections(True)
                coating.setMicroRoughnessEnable(getattr(mat.blenderMat,'thea_CoatingMicroRoughness'))
                coating.setMicroRoughnessWidth(getattr(mat.blenderMat,'thea_CoatingMicroRoughnessWidth'))
                coating.setMicroRoughnessHeight(getattr(mat.blenderMat,'thea_CoatingMicroRoughnessHeight'))
#                coating.setCustomCurve(getattr(mat.blenderMat,'thea_ReflectionCurve'))
#                coating.setCustomCurveList(getattr(mat.blenderMat,'thea_BasicReflectCurveList'))

                wtex = getTexture(type="Stencil", component="thea_Coating")
                thea_globals.log.debug("wtex: %s" % (wtex))
#                 if layerAdded: #if already have layer
                if wtex:
                    layCoating = LayeredCoating(coating, 1, 1)
                    layCoating.setWeightTexture(wtex)
                else:
                    try:
                        layerWeight = getattr(mat.blenderMat, 'thea_CoatingWeight') / 100
                    except:
                        layerWeight = 1
                    layCoating = LayeredCoating(coating, layerWeight, 1)
                mat.layeredBsdf.addCoating(layCoating)
#                 else:
#                     if wtex:
#                         mat.setBSDF(bsdf,wTex=wtex)
#                     else:
#                         mat.setBSDF(bsdf)
#                     mat.setBSDF(bsdf)
#                 layerAdded = True

            if hasClipping:
                clip = Clipping()
                clip.setTexture(getTexture(type="Alpha", component="thea_Clipping"))
                try:
                    clip.setThreshold(getattr(mat.blenderMat, 'thea_ClippingThreshold')/100)
                except:
                    clip.setThreshold(0.5)
                try:
                    clip.setSoft(getattr(mat.blenderMat, 'thea_ClippingSoft'))
                except:
                    clip.setSoft = False
                mat.setClipping(clip)

            if hasMedium:
                medium = Medium()
                medium.absorptionColor=getTexture(type="Absorption", component="thea_Medium")
                medium.scatteringColor=getTexture(type="Scatter", component="thea_Medium")
                if getattr(mat.blenderMat, "thea_MediumAbsorptionDensityFilename")!="":
                    medium.absorptionDensityTexture=getTexture(type="AbsorptionDensity", component="thea_Medium")
                if getattr(mat.blenderMat, "thea_MediumScatterDensityFilename")!="":
                    medium.scatteringDensityTexture=getTexture(type="ScatterDensity", component="thea_Medium")
                medium.absorptionDensity=getattr(mat.blenderMat, "thea_MediumAbsorptionDensity")
                medium.scatteringDensity=getattr(mat.blenderMat, "thea_MediumScatterDensity")
                if getattr(mat.blenderMat, "thea_MediumCoefficient"):
                    from TheaForBlender.thea_render_main import getTheaMediumMenuItems
                    medium.coefficientFilename = getTheaMediumMenuItems()[int(getattr(mat.blenderMat, "thea_MediumMenu"))-1][1]+".med"
                medium.phaseFunction=getattr(mat.blenderMat, "thea_MediumPhaseFunction")
                medium.asymetry=getattr(mat.blenderMat, "thea_Asymetry")
                mat.setMedium(medium)

            if hasEmittance:
                if(getattr(mat.blenderMat, "thea_EmittanceIES")):
                    emit = IESLight()
                    emit.setTexture(getTexture(type="Emittance", component="thea_Emittance"))
                    emit.setMultiplier(getattr(mat.blenderMat, 'thea_EmittanceIESMultiplier'))
                    emit.setIesFile(getattr(mat.blenderMat, 'thea_EmittanceIESFilename'))
                    emit.passive=getattr(mat.blenderMat, 'thea_EmittancePassiveEmitter')
                    emit.ambient=getattr(mat.blenderMat, 'thea_EmittanceAmbientEmitter')
                    emit.ambientLevel=getattr(mat.blenderMat, 'thea_EmittanceAmbientLevel')/100
                    mat.setAreaLight(emit)

                else:
                    emit = AreaLight()
                    emit.setTexture(getTexture(type="Emittance", component="thea_Emittance"))
                    emit.setPower(mat.blenderMat.thea_EmittancePower)
                    emit.setEfficacy(getattr(mat.blenderMat, 'thea_EmittanceEfficacy'))
                    emit.setUnit(mat.blenderMat.thea_EmittanceUnit)
                    emit.passive=getattr(mat.blenderMat, 'thea_EmittancePassiveEmitter')
                    emit.ambient=getattr(mat.blenderMat, 'thea_EmittanceAmbientEmitter')
                    emit.ambientLevel=getattr(mat.blenderMat, 'thea_EmittanceAmbientLevel')/100
                    mat.setAreaLight(emit)

            if hasDisplacement:
                displ = Displacement()
                displ.setTexture(getTexture(type="Displacement", component="thea_"))
                try:
                    displ.setHeight(getattr(mat.blenderMat, 'thea_DisplacementHeight')/100)
                except:
                    displ.setHeight(0.02)
                try:
                    displ.subdivision= getattr(mat.blenderMat, 'thea_DispSub')
                except:
                    displ.subdivision = 2
#                 try:
#                     displ.microbump = getattr(mat.blenderMat, 'thea_DispBump')
#                 except:
#                     displ.microbump = 0
                try:
                    displ.center = getattr(mat.blenderMat, 'thea_DisplacementCenter')
                except:
                    displ.center = 0.5
                try:
                    displ.normalsmoothing = getattr(mat.blenderMat, 'thea_DisplacementNormalSmooth')
                except:
                    displ.normalsmoothing = True
                try:
                    displ.tightbounds = getattr(mat.blenderMat, 'thea_DisplacementTightBounds')
                except:
                    displ.tightbounds = True
                mat.setDisplacement(displ)
        return mat
