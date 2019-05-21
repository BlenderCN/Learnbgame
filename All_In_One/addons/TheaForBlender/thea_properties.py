"""
.. module:: thea_properties
   :platform: OS X, Windows, Linux
   :synopsis: Scene properties definitions along with helper functions called on property update

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

from math import *
from random import random
from TheaForBlender.thea_render_main import *
import bpy
import os
import platform
import struct
import subprocess
import sys
import time
from . import thea_globals
from inspect import getcomments
import configparser


FloatProperty= bpy.types.FloatProperty
IntProperty= bpy.types.IntProperty
BoolProperty= bpy.types.BoolProperty
EnumProperty= bpy.types.EnumProperty
CollectionProperty= bpy.types.CollectionProperty
StringProperty= bpy.types.StringProperty

Scene = bpy.types.Scene
Mat = bpy.types.Material
Tex = bpy.types.Texture
Obj = bpy.types.Object
Cam = bpy.types.Camera
WM  = bpy.types.WindowManager
Part = bpy.types.ParticleSettings
Lamp = bpy.types.Lamp

#(exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(bpy.context.scene)

dataPath = ""
try:
    if bpy.context.scene:
        sceneLoaded = True
except:
    dataPath = ""

Scene.thea_sdkIsRunning = bpy.props.BoolProperty(default= False)
Scene.thea_sdkProcess = bpy.props.IntProperty()

def engineUpdated(self, context):
    '''Sets thea_globals.engineUpdated = True when engine property is updated
    '''
    from . import thea_globals
    thea_globals.engineUpdated = True

def TheaPathUpdated(self, context, origin=""):
    '''Save PATHS section in config file when one of the Thea paths properties are updated

        :param context: context
        :param origin: parameter name to save
        :type origin: string
    '''
    print("path: ",  context, origin, context.scene.get(origin),bpy.path.abspath(context.scene.get(origin)))
    config = configparser.ConfigParser()
    configPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.ini")
    config.read(configPath)
    if not config.has_section("PATHS"):
        config.add_section('PATHS')
    config.set('PATHS',origin,os.path.abspath(bpy.path.abspath(context.scene.get(origin))))
    with open(configPath, 'w') as configfile:
        config.write(configfile)



Scene.thea_ApplicationPath = bpy.props.StringProperty(
    name = "Thea Application path",
    default = "",
    description = "Path to Thea executable",
    subtype = 'FILE_PATH',
    update=lambda a,b: TheaPathUpdated(a,b,"thea_ApplicationPath")
    )

Scene.thea_DataPath = bpy.props.StringProperty(
    name = "Thea Data path",
    default = "",
    description = "Path to Thea data directory",
    subtype = 'FILE_PATH',
    update=lambda a,b: TheaPathUpdated(a,b,"thea_DataPath")
    )

def items_engineMenu(self,context):
    '''set list engineMenu

        :return: list of tuples with files and paths
        :rtype: [(str, str, str)]
    '''
    items1 = [("Render & Export", "Render & Export", "Render & Export settings"),
            ("Engines", "Engines", "Engines Settings"),
            ("Channels", "Channels", "Channels per render engine")]
    items2 = [("Render & Export", "Render & Export", "Render & Export settings"),
            ("Channels", "Channels", "Channels per render engine")]
    scene = context.scene
    engineMenuItems = []
    if scene.thea_enablePresets !=True:
        i = 0
        for i in range(0,3):
            engineMenuItems.append(items1[i])
            i+=1
    else:
        i = 0
        for i in range(0,2):
            engineMenuItems.append(items2[i])
            i+=1
#    thea_globals.log.debug("EngineMenu Items: %s" % engineMenuItems)
    return engineMenuItems

Scene.thea_enginesMenu = bpy.props.EnumProperty(
    items=(items_engineMenu),
    name="Engine Menu",
    description="Choose engine with Settings & Channels for that engine ",
    )


#CHANGED > Added more info on description from manual
Scene.thea_RenderEngineMenu = bpy.props.EnumProperty(
                items=(("Adaptive (BSD)","Adaptive (BSD)","Adaptive BSD engine stands for the biased engine of Thea. The abbreviation \"BSD\" comes from the word \"biased\" and we use this term here as an identifier of this engine that uses interpolation schemes (like irradiance cache) to render in shorter times. The word \"Adaptive\" on the other hand means that we implemented the engine so that more effort is put where it is needed most. Furthermore, this effort is driven by perceptual criteria in order to arrive to a high quality result according to the human perception. Biased engine settings consist of three tabs: General, Biased RT (Ray Tracing) and Biased GI (Global Illumination)."),("Unbiased (TR1)","Unbiased (TR1)","With the term \"unbiased\" we mean that rendering, seen as a simulation process, converges always to the ground truth, computing all ways of lighting transfer without any artifacts. The unbiased engines have essentially no parameters, thus rendering can start right away without worrying about render setup. Unbiased engine TR1 should be preferred in exterior renders and interiors where direct lighting is the most dominant in the scene while unbiased engine TR2 should be preferred in cases of ultra-difficult lighting. In practice, TR1 can handle very difficult indirect lighting scenes and even \"sun pool caustics\", thus TR2 should be actually used in extremely difficult light transfer situations (like in the case of caustics lighting a scene)."),("Unbiased (TR2)","Unbiased (TR2)", "With the term \"unbiased\" we mean that rendering, seen as a simulation process, converges always to the ground truth, computing all ways of lighting transfer without any artifacts. The unbiased engines have essentially no parameters, thus rendering can start right away without worrying about render setup. Unbiased engine TR1 should be preferred in exterior renders and interiors where direct lighting is the most dominant in the scene while unbiased engine TR2 should be preferred in cases of ultra-difficult lighting. In practice, TR1 can handle very difficult indirect lighting scenes and even \"sun pool caustics\", thus TR2 should be actually used in extremely difficult light transfer situations (like in the case of caustics lighting a scene)."),("Adaptive (AMC)","Adaptive (AMC)","Progressive Engine, which uses the logic of an unbiased engine, but with some extra tuning which reduces render time but also adds a bias in the final result. Llets the user specify the tracing depth of the scene (in unbiased methods, this goes indefinitely)."),("Presto (AO)","Presto (AO)","Progressive (AO) engine, is very simplified and does not take into account many settings, so it is very fast, although adds much noise (the use of Ambient occlusion which is enabled for this engine helps reducing this noise)."),("Presto (MC)","Presto (MC)","Progressive Engine, which uses the logic of an unbiased engine, but with some extra tuning which reduces render time but also adds a bias in the final result. Llets the user specify the tracing depth of the scene (in unbiased methods, this goes indefinitely).")),
                #items=(("Adaptive (BSD)","Adaptive (BSD)","Adaptive (BSD)"),("Progressive (BSD)","Progressive (BSD)","Progressive (BSD)"),("Unbiased (TR1)","Unbiased (TR1)","Unbiased (TR1)"),("Unbiased (TR2)","Unbiased (TR2)", "Unbiased (TR2)"),("Unbiased* (MC)","Unbiased* (MC)","Unbiased* (MC)"),("Adaptive (AMC)","Adaptive (AMC)","Adaptive (AMC)"),("Presto (AO)","Presto (AO)","Presto (AO)"),("Presto (MC)","Presto (MC)","Presto (MC)")),
#                items=(("BSD","Adaptive (BSD)","Adaptive (BSD)"),("TR1","Unbiased (TR1)","Unbiased (TR1)"),("TR1+","Unbiased (TR1+)","Unbiased (TR1+)"),("TR2","Unbiased (TR2)", "Unbiased (TR2)"),("TR2+","Unbiased (TR2+)", "Unbiased (TR2+)")),
                name="Engine Core",
                description="Engine Core",
                default="Presto (AO)",
                update=engineUpdated)

Scene.thea_IRRenderEngineMenu = bpy.props.EnumProperty(
                items=(("Presto (AO)","Presto (AO)","Presto (AO)"),("Presto (MC)","Presto (MC)","Presto (MC)"),("Adaptive (AMC)","Adaptive (AMC)","Adaptive (AMC)")),
                #items=(("Progressive (BSD)","Progressive (BSD)","Progressive (BSD)"),("Adaptive (AMC)","Adaptive (AMC)","Adaptive (AMC)"),("Presto (AO)","Presto (AO)","Presto (AO)"),("Presto (MC)","Presto (MC)","Presto (MC)")),
                name="Engine Core",
                description="Engine Core",
                default="Presto (AO)",
                update=engineUpdated)
#CHANGED > Added correct naming and more info on description from manual
Scene.thea_AASamp = bpy.props.EnumProperty(
                items=(("0","Default","Default"),("1","None","None"),("2","Normal", "Normal"),("3", "High", "High")),
                name="SuperSampling",
                description="Value None corresponds to no supersampling at all, Normal to 2x2 and High to 3x3. Auto corresponds to 2x2 for unbiased engines. Setting supersampling to a higher level will generally improve antialiasing of the output but will increase memory demands for storing the image (4 times in Normal level and 9 times in High level)",
                default="0",
                update=engineUpdated)

#CHANGED > Added missgin Adaptive Bias added Updatefunction
Scene.thea_adaptiveBias = bpy.props.IntProperty(
                min=0,
                max=100,
                default=25,
                name="Adaptive Bias (%)",
                description="Adds Bias to render",
                update=engineUpdated)

#CHANGED > Added correct naming and more info on description from manual added Updatefunction
Scene.thea_RenderTime = bpy.props.IntProperty(
                min=0,
                max=1000,
                default=0,
                name="Time Limit (min)",
                description="Terminate the render process by specifying the render time",
                update=engineUpdated)

Scene.thea_RenderMaxPasses = bpy.props.IntProperty(
                min=1,
                max=1000000,
                default=10000,
                name="Max Passes",
                description="Max Passes",
                update=engineUpdated)

#CHANGED > Added correct naming and more info on description from manual
Scene.thea_RenderMaxSamples = bpy.props.IntProperty(
                min=1,
                max=1000000,
                default=512,
                name="Sample Limit",
                description="Max Samples, terminate the render by defining the maximum amount of samples",
                update=engineUpdated)

Scene.thea_RenderMBlur = bpy.props.BoolProperty(
                name="Motion Blur",
                description="If enabled will show up for all visible animated objects. The actual blur amount depends on camera shutter speed and animation properties of the objects",
                default= True,
                update=engineUpdated)
#CHANGED> Added displacement
Scene.thea_displacemScene = bpy.props.BoolProperty(
                name="Displacement",
                description="By enabling Displacement, materials that have a displacement will be normally rendered; otherwise, they will be rendered as if they had no displacement.",
                default= True,
                update=engineUpdated)

Scene.thea_RenderVolS = bpy.props.BoolProperty(
                name="Volumetric Scattering",
                description="It corresponds to rendering participating media. If disabled, volumetric (Medium) and sub-surface (SSS) scattering won't be rendered by unbiased engines.",
                default= True,
                update=engineUpdated)

Scene.thea_RenderLightBl = bpy.props.BoolProperty(
                name="Relight",
                description="This parameter corresponds to rendering light groups in separate image buffers for relighting post-process. Due to the allocation of an image buffer per light, the number of lights has a direct impact on memory demands and rendering high resolution images with a lot of lights may require a lot of Gb Ram. Please note that clearing all image buffers separately takes more time than clearing one merged buffer, although this is easily amortized by reusing the render output in a relight animation.",
                default= False,
                update=engineUpdated)

Scene.thea_ImgTheaFile = bpy.props.BoolProperty(
                name="Save img.thea",
                description="Save img.thea for use with relight",
                default= False,
                update=engineUpdated)
#            CHANGED > Added clay render options
Scene.thea_clayRender = bpy.props.BoolProperty(
                name="Clay Render",
                description="By enabling this option, all materials in the scene will be rendered as diffuse gray, giving the final image a clay effect.",
                default= False,
                update=engineUpdated)

Scene.thea_clayRenderReflectance = bpy.props.IntProperty(
                min=0,
                max=100,
                default=50,
                name="Reflectance (%)",
                description="By changing the Reflectance percentage you can decrease/increase the diffuse material reflectance (from black to white).",
                update=engineUpdated)
#CHANGED> Added regionrender
Scene.thea_regionRender = bpy.props.BoolProperty(
                name="Render Region",
                description="By enabling this option, the image wil be rendered in a grid manner in Thea studio. The number of images generated in a grid of 2x2, 3x3, 4x4 or 8x8. Saves memory, when memory limit is reached use this option.",
                default= False,
                update=engineUpdated)

Scene.thea_regionDarkroom = bpy.props.BoolProperty(
                name="Darkoom Mode",
                description="By enabling this option, region render will be rendered in Darkroom mode only. This doesnt load Thea's GUI and therefor takes even less memory.",
                default= False,
                update=engineUpdated)

Scene.thea_regionSettings = bpy.props.EnumProperty(
                items=(("0", "2x2", "2x2"),("1","3x3","3x3"),("2","4x4","4x4"),("3","5x5","5x5"),("4","6x6","6x6"),("5","7x7","4x4"),("6","8x8", "8x8")),
                name="Render region settings",
                description="Region render settings. the number of images generated in a grid of 2x2, 3x3, 4x4 or 8x8. Saves memory, when memory limit is reached use this option.",
                default="0")

#CHANGED > Added markernaming + Custom naming
Scene.thea_markerName = bpy.props.BoolProperty(
                name="Marker naming",
                description="Enables filenaming according to current marker.",
                default= False)
# CHANGED added export save only
Scene.thea_save2Export = bpy.props.BoolProperty(
                name="Save to export folder",
                description="Prevents saving with frame numbers. Leave OFF for animation rendering.",
                default= False)

Scene.thea_customOutputName = bpy.props.BoolProperty(
                name="Custom output naming",
                description="Enables custom output file naming.",
                default= False)

Scene.thea_customName = bpy.props.StringProperty(
                name="Output name",
                description="Replace file output naming with custom naming.",
                default= "")

Scene.thea_RenderRefreshResult = bpy.props.BoolProperty(
                name="Auto Refresh result",
                description="Auto refresh render result",
                default= True)

Scene.thea_ExportAnimation = bpy.props.BoolProperty(
                name="Export Animation data of objects",
                description="Export Animation data of objects.",
                default= True)

Scene.thea_AnimationEveryFrame = bpy.props.BoolProperty(
                name="Export every animation key frame",
                description="Export every animation key frame",
                default= False)

Scene.thea_Reuse = bpy.props.BoolProperty(
                name="Reuse Meshes",
                description="Reuse already exported meshes",
                default= False)

Scene.thea_ExitAfterRender = bpy.props.BoolProperty(
                name="Exit Thea after render",
                description="Exit Thea after render",
                default= False)

Scene.thea_stopOnErrors = bpy.props.BoolProperty(
                name="Stop on errors",
                description="Stop on errors",
                default= True)


Scene.thea_Selected = bpy.props.BoolProperty(
                name="Selected only",
                description="Export only selected objects",
                default= False)

Scene.thea_HideThea = bpy.props.BoolProperty(
                name="Hide Thea while rendering",
                description="Hide Thea while rendering",
                default= True)

Scene.thea_RenderLightBl = bpy.props.BoolProperty(
                name="Relight",
                description="Relight",
                default= False)

#Scene.thea_ImgTheaFile = bpy.props.BoolProperty(
#                name="Save img.thea",
#                description="Save img.thea for use with relight",
#                default= False)
Scene.thea_distributionRender = bpy.props.BoolProperty(
                name="Distribution Render:",
                description="Distribution Render, renders the image over a network using Nodes.",
                default= False)

Scene.thea_DistTh = bpy.props.EnumProperty(
                items=(("0", "Max", "Max"),("1","1","1"),("2","2","2"),("4","4", "4"),("8", "8", "8")),
                name="Threads",
                description="Threads",
                default="0")

Scene.thea_DistPri = bpy.props.EnumProperty(
                items=(("0","Lower","Lower"),("1","Low","Low"),("2","Normal","Normal")),
                name="Priority",
                description="Priority",
                default="0")

Scene.thea_DistNet = bpy.props.EnumProperty(
                items=(("0","None","None"),("1","Client","Client"), ("2", "Server", "Server"), ("3", "Pure Server", "Pure Server")),
                name="Network",
                description="Network",
                default="0")

Scene.thea_DistPort = bpy.props.IntProperty(
                min=1001,
                max=65000,
                default=6200,
                name="Server Port",
                description="Server Port")

Scene.thea_DistAddr = bpy.props.StringProperty(
                maxlen=15,
                default="127.0.0.1",
                name="Server Address",
                description="Server Address")

Scene.thea_BucketRendering = bpy.props.BoolProperty(
                name="Bucket rendering",
                description="Bucket rendering",
                default= False)

Scene.thea_ExtendedTracing = bpy.props.BoolProperty(
                name="Extended Tracing",
                description="By enabling Extended Tracing Depth we can efficiently render scenes with transparent objects or materials with Subsurface Scattering, with lower Tracing Depth values and better render times.",
                default= False,
                update=engineUpdated)

Scene.thea_TransparencyDepth = bpy.props.IntProperty(
                min=0,
                max=100,
                default=15,
                name="Transparency Depth",
                description="Determines the Extended Tracing Depth for all transparent materials like Thin Film, Glossy Glass and Clip Map. It only affects transparency.",
                update=engineUpdated)

Scene.thea_InternalReflectionDepth = bpy.props.IntProperty(
                min=0,
                max=100,
                default=15,
                name="Internal Reflection Depth",
                description="Depth determines the Extended Tracing Depth for transparent materials that have refraction and total internal reflection. These materials are created with the use of Thea Glossy material (for example solid glass or water). If you notice that you get dark areas on solid glass, the cause is often because of too low Internal Reflection Depth and not due to the Transparency Depth.",
                update=engineUpdated)

Scene.thea_ClampLevelEnable = bpy.props.BoolProperty(
                name="Clamp Level",
                description="By enabling Extended Tracing Depth we can efficiently render scenes with transparent objects or materials with Subsurface Scattering, with lower Tracing Depth values and better render times.",
                default= True,
                update=engineUpdated)

Scene.thea_ClampLevel = bpy.props.FloatProperty(
                min=0,
                max=5,
                precision=3,
                default=1,
                name="Clamp Level",
                description="this parameter is used to clamp the evaluation of a pixel, improving antialiasing. The number corresponds to the clamping limit. Higher than 1, clamping becomes less effective for antialiasing while less than 1 it becomes more effective but also lowering the brightness of the image more aggressively.",
                update=engineUpdated)

Scene.thea_SSSDepth = bpy.props.IntProperty(
                min=0,
                max=100,
                default=15,
                name="SSS Depth",
                description="Determines the Extended Tracing Depth for Subsurface Scattering (SSS) materials. In some cases increasing this value is needed to increase the brightness of bright colored dense SSS materials.",
                update=engineUpdated)

Scene.thea_RTTracingDepth = bpy.props.IntProperty(
                min=0,
                max=100,
                default=5,
                name="Tracing Depth",
                description="It is an important parameter for Progressive engines. Increasing this parameter may be needed for certain cases where there are a lot of mirrors or dielectrics in the scene but it has a direct impact on render times.",
                update=engineUpdated)

Scene.thea_RTDiffuseDepth = bpy.props.IntProperty(
                min=0,
                max=100,
                default=1,
                name="Diffuse Depth",
                description="This is a separate value to control tracing depth for diffused surfaces",
                update=engineUpdated)

Scene.thea_RTGlossyDepth = bpy.props.IntProperty(
                min=0,
                max=100,
                default=2,
                name="Glossy Depth",
                description="Glossy Depth",
                update=engineUpdated)

Scene.thea_RTTraceDispersion = bpy.props.BoolProperty(
                name="Trace Dispersion",
                description="Trace Dispersion",
                default= False)

Scene.thea_RTTraceReflections = bpy.props.BoolProperty(
                name="Trace Reflections",
                description="Trace Reflections",
                default= True)

Scene.thea_RTTraceRefractions = bpy.props.BoolProperty(
                name="Trace Refractions",
                description="Trace Refractions",
                default= True)

Scene.thea_RTTraceTransparencies = bpy.props.BoolProperty(
                name="Trace Transparencies",
                description="Trace Transparencies",
                default= True)

Scene.thea_AACont = bpy.props.FloatProperty(
                min=0.000,
                max=10.000,
                precision=3,
                default=0.020,
                name="Max Contrast",
                description="Max Contrast")

Scene.thea_AAMinSub = bpy.props.EnumProperty(
                items=(("0","0","0"),("1","1","1"), ("2", "2", "2"), ("3", "3", "3"), ("4", "4", "4"), ("5", "5", "5"), ("6", "6", "6"), ("7", "7", "7")),
                name="Min AA Subdivs",
                description="Min AA Subdivs",
                default="0")

Scene.thea_AAMaxSub = bpy.props.EnumProperty(
                items=(("0","0","0"),("1","1","1"), ("2", "2", "2"), ("3", "3", "3"), ("4", "4", "4"), ("5", "5", "5"), ("6", "6", "6"), ("7", "7", "7")),
                name="Max AA Subdivs",
                description="Max AA Subdivs",
                default="4")

Scene.thea_DLEnable = bpy.props.BoolProperty(
                name="Enable",
                description="Enable",
                default= True)

Scene.thea_DLPerceptualBased = bpy.props.BoolProperty(
                name="Perceptual Based",
                description="Perceptual Based",
                default= False)

Scene.thea_DLMaxError = bpy.props.FloatProperty(
                min=0.000,
                max=100,
                precision=3,
                default=2,
                name="Max Direct Error %",
                description="Max Direct Error %")

Scene.thea_BREnable = bpy.props.BoolProperty(
                name="Enable",
                description="Enable",
                default= True)

Scene.thea_BRMinSub = bpy.props.EnumProperty(
                items=(("0","0","0"),("1","1","1"), ("2", "2", "2"), ("3", "3", "3"), ("4", "4", "4"), ("5", "5", "5"), ("6", "6", "6"), ("6", "6", "6")),
                name="Min Blurred Subdivs",
                description="Min Blurred Subdivs",
                default="0")

Scene.thea_BRMaxSub = bpy.props.EnumProperty(
                items=(("0","0","0"),("1","1","1"), ("2", "2", "2"), ("3", "3", "3"), ("4", "4", "4"), ("5", "5", "5"), ("6", "6", "6"), ("6", "6", "6")),
                name="Max Blurred Subdivs",
                description="Max Blurred Subdivs",
                default="3")

Scene.thea_GIEnable = bpy.props.BoolProperty(
                name="Enable",
                description="Enable",
                default= False)

Scene.thea_FMEnable = bpy.props.BoolProperty(
                name="Enable",
                description="Enable",
                default= False)

Scene.thea_FMFieldDensity = bpy.props.IntProperty(
                min=0,
                max=1000000000,
                default=100000,
                name="Field Density",
                description="Field Density")

Scene.thea_FMCellSize = bpy.props.IntProperty(
                min=0,
                max=1000000000,
                default=1000,
                name="Cell Size",
                description="Cell Size")

Scene.thea_GICaustics = bpy.props.BoolProperty(
                name="Caustics",
                description="Caustics",
                default= False)

Scene.thea_GITotPh = bpy.props.IntProperty(
                min=0,
                max=1000000000,
                default=1000000,
                name="Photons Captured",
                description="Photons Captured")

Scene.thea_GICausticCaptured = bpy.props.IntProperty(
                min=0,
                max=1000000000,
                default=10000,
                name="Captured Photons",
                description="Captured Photons")

Scene.thea_GICausPh = bpy.props.IntProperty(
                min=0,
                max=1000,
                default=200,
                name="Estimation Photons",
                description="Estimation Photons")

Scene.thea_GILeakComp = bpy.props.BoolProperty(
                name="Leak Compensation",
                description="Leak Compensation",
                default= False)

Scene.thea_GICausticSharp = bpy.props.BoolProperty(
                name="Caustic Sharpening",
                description="Caustic Sharpening",
                default= False)

Scene.thea_GIGlobPh = bpy.props.IntProperty(
                min=0,
                max=1000000,
                default=400,
                name="Global Photons",
                description="Global Photons")

Scene.thea_GIGlobalRadius = bpy.props.FloatProperty(
                min=0.0001,
                max=1000,
                precision=4,
                default=0.50,
                name="Global Radius",
                description="Global Radius")

Scene.thea_GICausticRadius = bpy.props.FloatProperty(
                min=0.000,
                max=100,
                precision=4,
                default=0.10,
                name="Caustic Radius",
                description="Caustic Radius")

Scene.thea_CausticLock = bpy.props.BoolProperty(
                name="Lock Cache",
                description="Lock Cache",
                default= False)

Scene.thea_FGEnable = bpy.props.BoolProperty(
                name="Enable",
                description="Enable",
                default= True)

Scene.thea_FGDiffuseDepth = bpy.props.IntProperty(
                min=0,
                max=100,
                default=1,
                name="Diffuse Depth",
                description="Diffuse Depth")

Scene.thea_GIRays = bpy.props.IntProperty(
                min=1,
                max=10000,
                default=200,
                name="Samples",
                description="Samples")

Scene.thea_GIError = bpy.props.FloatProperty(
                min=0.01,
                max=100,
                precision=3,
                default=15,
                name="Max Gather Error (%)",
                subtype='PERCENTAGE',
                description="Max Gather Error (%)")

Scene.thea_FGEnableSecondary = bpy.props.BoolProperty(
                name="Secondary Gather",
                description="Secondary Gather",
                default= False)

Scene.thea_FGDistanceThreshold = bpy.props.FloatProperty(
                min=0.001,
                max=100,
                precision=3,
                default=0.100,
                name="Distance Threshold (m)",
                description="Distance Threshold (m)")

Scene.thea_GITracingDepth = bpy.props.IntProperty(
                min=1,
                max=100,
                default=1,
                name="Tracing Depth",
                description="Tracing Depth")

Scene.thea_FGGlossyDepth = bpy.props.IntProperty(
                min=0,
                max=100,
                default=0,
                name="Glossy Depth",
                description="Glossy Depth")

Scene.thea_FGAdaptiveSteps = bpy.props.IntProperty(
                min=0,
                max=100,
                default=3,
                name="Adaptive Steps",
                description="Adaptive Steps")

Scene.thea_FGGlossyEvaluation = bpy.props.BoolProperty(
                name="Glossy Evaluation",
                description="Glossy Evaluation",
                default= False)

Scene.thea_FGCausticEvaluation = bpy.props.BoolProperty(
                name="Caustic Evaluation",
                description="Caustic Evaluation",
                default= False)

Scene.thea_GITraceReflections = bpy.props.BoolProperty(
                name="Trace Reflections",
                description="Trace Reflections",
                default= True)

Scene.thea_GITraceRefractions = bpy.props.BoolProperty(
                name="Trace Refractions",
                description="Trace Refractions",
                default= True)

Scene.thea_GITraceTransparencies = bpy.props.BoolProperty(
                name="Trace Transparencies",
                description="Trace Transparencies",
                default= True)

Scene.thea_GIEnableSS = bpy.props.BoolProperty(
                name="Enable",
                description="Enable",
                default= False)

Scene.thea_UseZip = bpy.props.BoolProperty(
                name="Compress",
                description="Compress",
                default= False)


def worldUpdated(self, context):
    '''Sets thea_globals.worldUpdated = True when one of the world properties are updated
    '''

    from . import thea_globals
    thea_globals.worldUpdated = True
    scene = context.scene
    scn = scene
    (exportPath, theaPath, theaDir, dataPath, currentBlendDir, currentBlendFile) = setPaths(scn)

    for sunOb in bpy.data.objects:
       if sunOb.type == 'LAMP' and sunOb.data.type == 'SUN':
           sunName = sunOb.data.name
#           sunObj = sunOb.object
       try:
#           if getattr(context.scene,"thea_IBLEnable"):
#               setattr(bpy.data.scenes["Scene"],"thea_EnvPSEnable", False)
#           if getattr(context.scene,"thea_EnvPSEnable"):
#               setattr(bpy.data.scenes["Scene"],"thea_IBLEnable", False)

           if (getattr(context.scene,"thea_IBLTypeMenu") == 'IBL Only') and getattr(context.scene,"thea_IBLEnable") or getattr(context.scene,"thea_locationEnable"):
               setattr(bpy.data.lamps[sunName], "thea_enableLamp", False)
           else:
               setattr(bpy.data.lamps[sunName], "thea_enableLamp", True)
#           if (getattr(context.scene,"thea_SkyTypeMenu") == 'Sun+Sky') and getattr(context.scene,"thea_EnvPSEnable", False):
#               setattr(bpy.data.scenes["Scene"],"thea_SkyTypeMenu", 'Sky Only')
#
           if (getattr(context.scene,"thea_SkyTypeMenu") == 'Sky Only') and getattr(context.scene,"thea_EnvPSEnable") or getattr(context.scene,"thea_locationEnable"):
               setattr(bpy.data.lamps[sunName], "thea_enableLamp", False)
           if (getattr(context.scene,"thea_SkyTypeMenu") == 'Sun+Sky') and getattr(context.scene,"thea_EnvPSEnable"):
               setattr(bpy.data.lamps[sunName], "thea_enableLamp", True)
           if getattr(context.scene,"thea_locationEnable") and getattr(context.scene,"thea_EnvPSEnable"):
               bpy.data.objects[sunName].hide = True
           else:
               bpy.data.objects[sunName].hide = False

       except:
           pass

    #    def makeImg():
#    #    import bpy
#        img = "IBL-color.png"
#        img2 = "/Users/romboutversluijs/Desktop/"+img
#        try:
#            img = bpy.data.images['IBL Color']
#        except:
#            img = False
#            thea_globals.log.debug("img: %s" % img)
#        if not img:
#        #image_object = bpy.data.images.new(name="pixeltest", width=40, height=30)
#            img = bpy.data.images.new('IBL Color', width=2, height=2)
#        num_pixels = len(img.pixels)
#        thea_globals.log.debug("Iimg Pixels: %s" % num_pixels)
#        # drawing a pixel, changing pixel content
#        for px in range(0, num_pixels, 2):
#            cols = (0,0,6,6,0,0,5,5,0,0,1,1) #okeryellow
#            leng = len(cols)
##            cols = (mat.thea_BasicReflectanceCol[0], mat.thea_BasicReflectanceCol[1] , mat.thea_BasicReflectanceCol[2])
#            for i in range(2):
#                thea_globals.log.debug("creating coor img:%s %s" % (px, img.pixels[px+i]))
#                img.pixels[px] = cols[i]
#            img.filepath_raw = img2
#            img.file_format = 'PNG'
#            img.save()
#            img.reload()

    def makeIBLcolorFile():
        size = 2, 2
        fileName = 'IBL-color'

#        image = None
#        image = bpy.data.images.get("IBL-color")
#        if image == None:
#            try:
#                image = bpy.data.images.load(imageFile)
#                image.name = "IBL-color"
#                thea_globals.log.debug("IBL-color Image: %s" % imageFile)
#            except:
#                image = None
##                                       CHANGED> Added reload, new renders wont reload otherwise
#        img = bpy.data.images["IBL-color"].reload()

        try:
            image = bpy.data.images[fileName]
        except:
            image = False
        if not image:
            image = bpy.data.images.new(fileName, width=size[0], height=size[1])
        image.filepath_raw = os.path.join(currentBlendDir, fileName+".png")
        ## For white image
        # pixels = [1.0] * (4 * size[0] * size[1])

        pixels = [None] * size[0] * size[1]
        for x in range(size[0]):
            for y in range(size[1]):
                # assign RGBA to something useful
#                r = x / size[0]
#                g = y / size[1]
#                b = (1 - r) * g
#                a = 1.0
                r = scene.thea_IBLColorFilename[0]
                g = scene.thea_IBLColorFilename[1]
                b = scene.thea_IBLColorFilename[2]
                a = 1.0

                pixels[(y * size[0]) + x] = [r, g, b, a]

        # flatten list
        pixels = [chan for px in pixels for chan in px]

        # assign pixels
        image.pixels = pixels

        # write image
        image.file_format = 'PNG'
        image.save()
        old = scene.thea_IBLFilename
        if old[-3:] == "hdr" or old[-3:] == "exr":
            global oldFile
            oldFile = scene.thea_IBLFilename

        if image.save:
            if scene.thea_IBLEnableColor:
                scene.thea_IBLFilename = os.path.join(currentBlendDir, fileName+".png")

        if scene.thea_IBLEnableColor<1:
            if old[-3:] == "png":
                scene.thea_IBLFilename = oldFile
#                oldFileCheck = False
    #                oldFile = True

    if thea_globals.worldUpdated:
        makeIBLcolorFile()

def worldFilenameUpdated(self, context, origin=""):
    '''Create texture and set it when one of the world filename properties are updated

        :param context: context
        :param origin: filename parameter which has been updated
        :type origin: string
    '''
    from . import thea_globals
    thea_globals.worldUpdated = True
#    lampFilenameUpdated
    imgName = context.scene.get(origin)
    texName = "IBL_"+origin
    world = context.scene.world
    print("worldFilenameUpdated: ",self, context, origin, context.scene.get(origin))
    exists = False
    try:
        if world.texture_slots[texName]:
            exists = True
            slot = world.texture_slots[texName]
            tex = slot.texture
    except:
        pass

    if exists:
        try:
            if imgName:
                img = bpy.data.images.load(imgName)
                tex.image = img
            else:
                print("removing texture: ", slot, tex)
                world.texture_slots[texName].texture = None
        except:
            pass
    else:
        img = bpy.data.images.load(imgName)
        tex = bpy.data.textures.new(name=texName, type='IMAGE')
        tex.image = img
        tex.name = texName
        slot = world.texture_slots.add()
        slot.texture = tex

Scene.thea_GlobalMediumEnable = bpy.props.BoolProperty(
                name="Enable Global Medium",
                description="Enable Global Medium",
                default= False,
                update=worldUpdated)

Scene.thea_GlobalMediumIOR = bpy.props.FloatProperty(
                min=0,
                max=10,
                precision=2,
                default=1.0,
                name="Index of Refraction (n)",
                description="Index of Refraction (n)",
                update=worldUpdated)

Scene.thea_Medium = bpy.props.BoolProperty(
                name="Medium",
                description="Medium",
                default= False,
                update=worldUpdated)


Scene.thea_MediumAbsorptionCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Absorption Color",
                default=(1,1,1),
                description="Color",
                subtype="COLOR",
                update=worldUpdated)

#Tex.thea_MediumAbsorptionTex = bpy.props.BoolProperty(
#                name="Absorption Texture",
#                description="Absorption Texture",
#                default= False,
#                update=worldUpdated)

Scene.thea_MediumAbsorptionFilename = bpy.props.StringProperty(
                  name = "Absorption texture",
                  default = "",
                  description = "Absorption texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: worldFilenameUpdated(a,b,"thea_MediumAbsorptionFilename")
                  )

Scene.thea_MediumScatterCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Scatter Color",
                default=(1,1,1),
                description="Color",
                subtype="COLOR",
                update=worldUpdated)

#Scene.thea_MediumScatterTex = bpy.props.BoolProperty(
#                name="Scatter Texture",
#                description="Scatter Texture",
#                default= False,
#                update=worldUpdated)

Scene.thea_MediumScatterFilename = bpy.props.StringProperty(
                  name = "Scatter texture",
                  default = "",
                  description = "Scatter texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: worldFilenameUpdated(a,b,"thea_MediumScatterFilename")
                  )

Scene.thea_MediumAbsorptionDensity = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=6,
                default=0.000001,
                name="Absorption Density",
                description="Absorption Density",
                update=worldUpdated)

#Tex.thea_MediumAbsorptionDensityTex = bpy.props.BoolProperty(
#                name="Absorption Density Texture",
#                description="Absorption Density Texture",
#                default= False,
#                update=worldUpdated)

Scene.thea_MediumAbsorptionDensityFilename = bpy.props.StringProperty(
                  name = "Absorption Density texture",
                  default = "",
                  description = "Absorption Density texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: worldFilenameUpdated(a,b,"thea_MediumAbsorptionDensityFilename")
                  )

Scene.thea_MediumScatterDensity = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=6,
                default=0.00001,
                name="Scatter Density",
                description="Scatter Density",
                update=worldUpdated)

#tex.thea_MediumScatterDensityTex = bpy.props.BoolProperty(
#                name="Scatter Density Texture",
#                description="Scatter Density Texture",
#                default= False,
#                update=worldUpdated)

Scene.thea_MediumScatterDensityFilename = bpy.props.StringProperty(
                  name = "Scatter Density texture",
                  default = "",
                  description = "Scatter Density texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: worldFilenameUpdated(a,b,"thea_MediumScatterDensityFilename")
                  )

Scene.thea_MediumCoefficient = bpy.props.BoolProperty(
                name="Coefficient",
                description="Coefficient",
                default= False,
                update=worldUpdated)

Scene.thea_MediumMenu = bpy.props.EnumProperty(
                items=getTheaMediumMenuItems(),
                name="File",
                description="File",
                update=worldUpdated)

Scene.thea_MediumPhaseFunction = bpy.props.EnumProperty(
                items=(("Isotropic","Isotropic","Isotropic"),("Rayleigh","Rayleigh","Rayleigh"),("Mie Hazy","Mie Hazy","Mie Hazy"), ("Mie Murky", "Mie Murky", "Mie Murky"), ("Mie Retro", "Mie Retro", "Mie Retro"), ("Henyey Greenstein", "Henyey Greenstein", "Henyey Greenstein")),
                name="Phase Function",
                description="Phase Function",
                default="Isotropic",
                update=worldUpdated)

Scene.thea_Asymetry = bpy.props.FloatProperty(
                min=-1,
                max=1,
                precision=3,
                default=0.0,
                name="Asymetry",
                description="Asymetry",
                update=worldUpdated)


Scene.thea_IBLEnable = bpy.props.BoolProperty(
                name="Enable Image Based Lighting",
                description="Enable Image Based Lighting",
                default= False,
                update=worldUpdated)

Scene.thea_IBLTypeMenu = bpy.props.EnumProperty(
                items=(("IBL Only","IBL Only","IBL Only"),("Sun+IBL","Sun+IBL","Sun+IBL")),
                name="IBL Type",
                description="IBL type",
                default="IBL Only",
                update=worldUpdated)

Scene.thea_IBLWrappingMenu = bpy.props.EnumProperty(
                items=(("AngularProbe","AngularProbe","AngularProbe"),("Hemispherical","Hemispherical","Hemispherical"), ("Spherical","Spherical","Spherical")),
                name="Wrapping",
                description="Wrapping",
                default="Spherical",
                update=worldUpdated)

Scene.thea_BackroundWrappingMenu = bpy.props.EnumProperty(
                items=(("AngularProbe","AngularProbe","AngularProbe"),("Hemispherical","Hemispherical","Hemispherical"), ("Spherical","Spherical","Spherical")),
                name="Wrapping",
                description="Wrapping",
                default="Spherical",
                update=worldUpdated)



Scene.thea_IBLFilename = bpy.props.StringProperty(
                  name = "Filename",
                  default = "",
                  description = "IBL map file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: worldFilenameUpdated(a,b,"thea_IBLFilename")
                  )

Scene.thea_IBLRotation = bpy.props.FloatProperty(
                min=-10000000.00,
                max=10000000,
                precision=2,
                default=0,
                name="Rotation (deg)",
                description="Rotation (deg)",
                update=worldUpdated)

#Scene.thea_IBLIntensity = bpy.props.FloatProperty(
#                min=0.00,
#                max=10000000,
#                precision=2,
#                default=1,
#                name="Intensity",
#                description="Intensity",
#                update=worldUpdated)

Scene.thea_BackgroundMappingEnable = bpy.props.BoolProperty(
                name="Enable Background Mapping",
                description="Enable Background Mapping",
                default= False,
                update=worldUpdated)

Scene.thea_BackgroundMappingTypeMenu = bpy.props.EnumProperty(
                items=(("IBL Only","IBL Only","IBL Only"),("Sun+IBL","Sun+IBL","Sun+IBL")),
                name="IBL Type",
                description="IBL type",
                default="IBL Only",
                update=worldUpdated)

Scene.thea_BackgroundMappingWrappingMenu = bpy.props.EnumProperty(
                items=(("AngularProbe","AngularProbe","AngularProbe"),("Hemispherical","Hemispherical","Hemispherical"), ("Spherical","Spherical","Spherical"), ("Center", "Center", "Center"), ("Tile", "Tile", "Tile"), ("Fit", "Fit", "Fit")),
                name="Wrapping",
                description="Wrapping",
                default="Spherical",
                update=worldUpdated)

Scene.thea_BackgroundMappingFilename = bpy.props.StringProperty(
                name="Filename",
                description="Background map file path",
                default= "",
                subtype = 'FILE_PATH',
                update=lambda a,b: worldFilenameUpdated(a,b,"thea_BackgroundMappingFilename"))

Scene.thea_BackgroundMappingRotation = bpy.props.FloatProperty(
                min=-10000000.00,
                max=10000000,
                precision=2,
                default=0,
                name="Rotation (deg)",
                description="Rotation (deg)",
                update=worldUpdated)

Scene.thea_BackgroundMappingIntensity = bpy.props.FloatProperty(
                min=0.00,
                max=10000000,
                precision=2,
                default=1,
                name="Intensity",
                description="Intensity",
                update=worldUpdated)

Scene.thea_ReflectionMappingEnable = bpy.props.BoolProperty(
                name="Enable Reflection Mapping",
                description="Enable Reflection Mapping",
                default= False,
                update=worldUpdated)

Scene.thea_ReflectionMappingTypeMenu = bpy.props.EnumProperty(
                items=(("IBL Only","IBL Only","IBL Only"),("Sun+IBL","Sun+IBL","Sun+IBL")),
                name="IBL Type",
                description="IBL type",
                default="IBL Only",
                update=worldUpdated)

Scene.thea_ReflectionMappingWrappingMenu = bpy.props.EnumProperty(
                items=(("AngularProbe","AngularProbe","AngularProbe"),("Hemispherical","Hemispherical","Hemispherical"), ("Spherical","Spherical","Spherical")),
                name="Wrapping",
                description="Wrapping",
                default="Spherical",
                update=worldUpdated)

Scene.thea_ReflectionMappingFilename = bpy.props.StringProperty(
                name="Filename",
                description="Reflection map file path",
                default= "",
                subtype = 'FILE_PATH',
                update=lambda a,b: worldFilenameUpdated(a,b,"thea_ReflectionMappingFilename"))

Scene.thea_ReflectionMappingRotation = bpy.props.FloatProperty(
                min=-10000000.00,
                max=10000000,
                precision=2,
                default=0,
                name="Rotation (deg)",
                description="Rotation (deg)",
                update=worldUpdated)

Scene.thea_ReflectionMappingIntensity = bpy.props.FloatProperty(
                min=0.00,
                max=10000000,
                precision=2,
                default=1,
                name="Intensity",
                description="Intensity",
                update=worldUpdated)

Scene.thea_RefractionMappingEnable = bpy.props.BoolProperty(
                name="Enable Refraction Mapping",
                description="Enable Refraction Mapping",
                default= False,
                update=worldUpdated)

Scene.thea_RefractionMappingTypeMenu = bpy.props.EnumProperty(
                items=(("IBL Only","IBL Only","IBL Only"),("Sun+IBL","Sun+IBL","Sun+IBL")),
                name="IBL Type",
                description="IBL type",
                default="IBL Only",
                update=worldUpdated)

Scene.thea_RefractionMappingWrappingMenu = bpy.props.EnumProperty(
                items=(("AngularProbe","AngularProbe","AngularProbe"),("Hemispherical","Hemispherical","Hemispherical"), ("Spherical","Spherical","Spherical")),
                name="Wrapping",
                description="Wrapping",
                default="Spherical",
                update=worldUpdated)

Scene.thea_RefractionMappingFilename = bpy.props.StringProperty(
                name="Filename",
                description="Refraction map file path",
                default= "",
                subtype = 'FILE_PATH',
                update=lambda a,b: worldFilenameUpdated(a,b,"thea_RefractionMappingFilename"))

Scene.thea_RefractionMappingRotation = bpy.props.FloatProperty(
                min=-10000000.00,
                max=10000000,
                precision=2,
                default=0,
                name="Rotation (deg)",
                description="Rotation (deg)",
                update=worldUpdated)

Scene.thea_RefractionMappingIntensity = bpy.props.FloatProperty(
                min=0.00,
                max=10000000,
                precision=2,
                default=1,
                name="Intensity",
                description="Intensity",
                update=worldUpdated)

Scene.thea_IBLEnable = bpy.props.BoolProperty(
                name="Enable Image Based Lighting",
                description="Enable Image Based Lighting",
                default= False,
                update=worldUpdated)

Scene.thea_IBLTypeMenu = bpy.props.EnumProperty(
                items=(("IBL Only","IBL Only","IBL Only"),("Sun+IBL","Sun+IBL","Sun+IBL")),
                name="IBL Type",
                description="IBL type",
                default="IBL Only",
                update=worldUpdated)

Scene.thea_IBLWrappingMenu = bpy.props.EnumProperty(
                items=(("AngularProbe","AngularProbe","AngularProbe"),("Hemispherical","Hemispherical","Hemispherical"), ("Spherical","Spherical","Spherical")),
                name="Wrapping",
                description="Wrapping",
                default="Spherical",
                update=worldUpdated)

Scene.thea_IBLFilePath = bpy.props.StringProperty(
                name="Filename",
                description="Filename",
                default= "")

Scene.thea_IBLRotation = bpy.props.FloatProperty(
                min=-10000000.00,
                max=10000000,
                precision=2,
                default=0,
                name="Rotation (deg)",
                description="Rotation (deg)",
                update=worldUpdated)

Scene.thea_IBLIntensity = bpy.props.FloatProperty(
                min=0.00,
                max=10000000,
                precision=2,
                default=1,
                name="Intensity",
                description="Intensity",
                update=worldUpdated)
#CHANGED> Added IBL color input
Scene.thea_IBLEnableColor = bpy.props.BoolProperty(
                name="Color Based Lighting",
                description="Enables Color Based Lighting",
                default= False,
                update=worldUpdated)

Scene.thea_IBLColorFilename = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="IBL Color",
                default=(0, 0, 0),
                description="IBL Color Filename",
                subtype="COLOR",
                update=worldUpdated)

Scene.thea_EnvPSEnable = bpy.props.BoolProperty(
                name="Enable Physical Sky",
                description="Enable Physical Sky",
                default= False,
                update=worldUpdated)

Scene.thea_SkyTypeMenu = bpy.props.EnumProperty(
                items=(("Sky Only","Sky Only","Sky Only"),("Sun+Sky","Sun+Sky","Sun+Sky")),
                name="Sky Type",
                description="Sky type",
                default="Sun+Sky",
                update=worldUpdated)
#CHANGED > Added description and editted default settings and max settings
Scene.thea_EnvPSTurb = bpy.props.FloatProperty(
                min=0.00,
                max=15,
                precision=3,
                default=2.500,
                name="Turbidity",
                description="Turbidity is a term used to describe the scattering of the atmosphere that is caused by haze. The term haze refers to an atmosphere that scatters more than molecules alone, but less than fog. Haze is often referred to as a haze aerosol because the extra scattering is due to particles suspended in the molecular gas. Because the haze particles typically scatter more uniformly than molecules for all wavelengths, haze causes a whitening of the sky. The actual particles come from many sources such as volcanic eruptions, forest fires, cosmic bombardment, the oceans etc. A default value of this parameter is 2.5 Values should be kept under 10",
                update=worldUpdated)

Scene.thea_EnvPSOzone = bpy.props.FloatProperty(
                min=0.00,
                max=15,
                precision=3,
                default=0.350,
                name="Ozone",
                description="This parameter defines the amount of ozone gas in the atmosphere. The standard way to determine the amount of total ozone is by measuring the amount of ozone gas in a column of air and is expressed in Dobson units. One Dobson unit indicates 0.01 millimeter thickness of ozone gas in a column. The default value in Thea is 0.350 cm. Higher values give the sky and the scene a blue color.",
                update=worldUpdated)

Scene.thea_EnvPSWatVap = bpy.props.FloatProperty(
                min=0.00,
                max=15,
                precision=3,
                default=2.000,
                name="Water Vapor",
                description="User can define here the amount of water vapor in the atmosphere. In the same way as ozone, it is measured in centimeters. Default value is set to 2.0.",
                update=worldUpdated)

Scene.thea_EnvPSTurbCo = bpy.props.FloatProperty(
                min=0.00,
                max=1,
                precision=3,
                default=0.046,
                name="Turbidity Coefficient",
                description="Turbidity coefficient is the power for exponential transmittance for atmospheric aerosol.",
                update=worldUpdated)

Scene.thea_EnvPSWaveExp = bpy.props.FloatProperty(
                min=0.00,
                max=25,
                precision=3,
                default=1.300,
                name="Wavelenght Exponent",
                description="At this point the wavelength exponent can be defined. The default value is set to 1.3. This number shows the average size of the particles in the atmosphere.",
                update=worldUpdated)
#Changed> Added missing albedo
Scene.thea_EnvPSalbedo = bpy.props.FloatProperty(
                min=0.00,
                max=1,
                precision=3,
                default=0.500,
                name="Albedo",
                description="Albedo option can influence the overall appearance of the sky. High albedo values can occur for example in winter scenes by the snow reflectance while small values occur at environment with grass. Especially in cases with high turbidity settings, changing the albedo value changes the overall brightness of the sky.",
                update=worldUpdated)

def locationUpdated(self, context):
    '''Update location and timezone properties when location was selected from the menu
    '''
    scene = context.scene
    loc = getLocation(scene.thea_EnvLocationsMenu, getLocations2(), scene)
    if loc[0] != "":
        scene.thea_EnvLat = loc[0]
        scene.thea_EnvLong = loc[1]
        scene.thea_EnvTZ = str(loc[2])

Scene.thea_locationEnable = bpy.props.BoolProperty(
                name="Location/Time",
                description="Location/Time",
                default= False,
                update=locationUpdated)

Scene.thea_EnvLocationsMenu = bpy.props.EnumProperty(
#                items=getLocations()[0],
                items=getLocMenu(),
                name="Location",
                description="Location",
                default="3",
                update=locationUpdated)

Scene.thea_Envlocation = bpy.props.StringProperty(
                maxlen=25,
                default="",
                name="Location:",
                description="Environment Location",
                update=worldUpdated)

Scene.thea_Interface = bpy.props.EnumProperty(
                 name="Materials List",
                 description="Materials List",
                 items=(("0","None","0"),("0","None","0")),
                 default="0")


Scene.thea_EnvLat = bpy.props.StringProperty(
                maxlen=15,
                default="0",
                name="Latitude",
                description="Latitude",
                update=worldUpdated)

Scene.thea_EnvLong = bpy.props.StringProperty(
                maxlen=15,
                default="0",
                name="Longitude",
                description="Longitude",
                update=worldUpdated)

Scene.thea_EnvTZ = bpy.props.EnumProperty(
                items=(('-12','GT-12',''),('-11','GT-11',''),('-10','GT-10',''),('-9','GT-09',''),('-8','GT-08',''),('-7','GT-07',''),('-6','GT-06',''),('-5','GT-05',''),('-4','GT-04',''),('-3','GT-03',''),('-2','GT-02',''),('-1','GT-01',''),('0','GT+00',''),('1','GT+01',''),('2','GT+02',''),('3','GT+03',''),('4','GT+04',''),('5','GT+05',''),('6','GT+06',''),('7','GT+07',''),('8','GT+08',''),('9','GT+09',''),('10','GT+10',''),('11','GT+11',''),('12','GT+12','')),
                name="Timezone",
                description="Timezone",
                default="0",
                update=worldUpdated)

Scene.thea_EnvTime = bpy.props.StringProperty(
                maxlen=8,
                default="12:00:00",
                name="Time",
                description="Time",
                update=worldUpdated)

Scene.thea_EnvDate = bpy.props.StringProperty(
                maxlen=10,
                default="1/6/2016",
                name="Date",
                description="Date",
                update=worldUpdated)

Scene.thea_EnvUpdateSky = bpy.props.BoolProperty(
                name="Update Sky",
                description="Update Sky",
                default= True)


def getViewChannelMenuItems(scene, context):
    '''get list with menu items of the channels to preview in Displaysettings

        :return: list of tuples with channel type
        :rtype: [(str, str, str)]
    '''

    channels = ('Normal','Position','UV','Depth','Alpha','Object_Id','Material_Id','Shadow','Mask','Raw_Diffuse_Color','Raw_Diffuse_Lighting','Raw_Diffuse_GI','Self_Illumination','Direct','AO','GI','SSS','Separate_Passes_Per_Light','Reflection','Refraction','Transparent','Irradiance')
    channelMenuItems = []
    channelMenuItems.append(("Color","Color",""))
    sceneLoaded = False
    try:
        if bpy.context.scene:
#            scene = bpy.context.scene
            sceneLoaded = True
    except:
        pass
    if sceneLoaded:
#        thea_globals.log.debug("DisplayUpdated: %s" % (getattr(scene,"thea_channel" + "Normal")))
#        scene = bpy.context.scene
        i = 1
        for entry in sorted(channels):
#            thea_globals.log.debug("CHannels: %s" % entry)
    #        if bpy.context.scene.get('thea_channelNormal') == channels:
            if getattr(scene,"thea_channel" + entry) == True:
#                thea_globals.log.debug("Channel View: %s" % getattr(scene,"thea_channel" + entry))
    #                channel.append((entry,channels)
                channelMenuItems.append((entry.replace("_"," "),entry.replace("_"," "),""))
                i+=1
    else:
        channelMenuItems.append(("1","Please install Thea Studio to use channel presets",""))

    return channelMenuItems

def displayUpdated(self, context):
    '''Set thea_globals.displayUpdated = True when one of the display properties are updated
    '''
    thea_globals.displayUpdated = True

Scene.thea_DisplayMenuEnable = bpy.props.BoolProperty(
                name="Enable",
                description="Enable",
                default= False)

Scene.thea_DisplayMenu = bpy.props.EnumProperty(
                items=getTheaDisplayMenuItems(),
                name="Display Presets",
                description="Display Presets",
                default="0",
                update=displayUpdated)

Scene.thea_viewChannel = bpy.props.EnumProperty(
                items=getViewChannelMenuItems, #[int(getattr(scene, "thea_Channel"))][1],
                name="View Channel",
                description="View Channel")


Scene.thea_DispISO = bpy.props.IntProperty(
                min=1,
                max=1000000,
                default=100,
                name="ISO",
                description="ISO",
                update=displayUpdated)

Scene.thea_DispShutter = bpy.props.IntProperty(
                min=1,
                max=1000000,
                default=250,
                name="Shutter Speed",
                description="Shutter Speed",
                update=displayUpdated)

Scene.thea_DispFNumber = bpy.props.FloatProperty(
                min=0.1,
                max=100,
                precision=1,
                default=5.6,
                name="f-number",
                description="f-number",
                update=displayUpdated)

Scene.thea_DispGamma = bpy.props.FloatProperty(
                min=0.1,
                max=10,
                precision=3,
                default=2.200,
                name="Gamma",
                description="Gamma",
                update=displayUpdated)

Scene.thea_DispBrightness = bpy.props.FloatProperty(
                min=0.1,
                max=100,
                precision=3,
                default=1.000,
                name="Brightness",
                description="Brightness",
                update=displayUpdated)

Scene.thea_DispContrast = bpy.props.BoolProperty(
                name="Contrast",
                description="Contrast",
                default= False,
                update=displayUpdated)

Scene.thea_DispContrastWeight = bpy.props.FloatProperty(
                min=0.0,
                max=100,
                precision=3,
                default=0.000,
                name="Contrast",
                description="Contrast",
                subtype='PERCENTAGE',
                update=displayUpdated)

Scene.thea_DispChroma = bpy.props.BoolProperty(
                name="Chroma",
                description="Chroma",
                default= False,
                update=displayUpdated)

Scene.thea_DispChromaWeight = bpy.props.FloatProperty(
                min=0.0,
                max=100,
                precision=3,
                default=0.000,
                subtype='PERCENTAGE',
                name="Chroma",
                description="Chroma",
                update=displayUpdated)
#CHANGED > Correct naming
Scene.thea_DispTemperature = bpy.props.BoolProperty(
                name="White Balance",
                description="White Balance",
                default= False,
                update=displayUpdated)

Scene.thea_DispTemperatureWeight = bpy.props.FloatProperty(
                min=0.1,
                max=100000,
                precision=1,
                default=6500,
                name="WB",
                description="White Balance",
                update=displayUpdated)

#   CHANGED > Added these display options here, these didnt updated before
Scene.thea_DispSharpness = bpy.props.BoolProperty(
                name="Sharpness",
                description="Sharpness",
                default= True,
                update=displayUpdated)

Scene.thea_DispSharpnessWeight = bpy.props.FloatProperty(
                min=-100,
                max=200,
                soft_min=0,
                soft_max=100,
                precision=1,
                default=50,
                name="Sharpness",
                description="Sharpness weight",
                subtype='PERCENTAGE',
                update=displayUpdated)

Scene.thea_DispBurn = bpy.props.BoolProperty(
                name="Burn",
                description="Burn",
                default= True,
                update=displayUpdated)

Scene.thea_DispBurnWeight = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=1,
                default=10,
                name="Burn",
                description="Burn",
                subtype='PERCENTAGE',
                update=displayUpdated)

Scene.thea_DispCRFMenu = bpy.props.EnumProperty(
                items=getTheaCRFMenuItems(),
                name="CRF",
                description="CRF",
                default="0",
                update=displayUpdated)

#      CHANGED > Z-depth from camera clipping
Scene.thea_ZdepthClip = bpy.props.BoolProperty(
                name="Use Camera Clipping",
                description="Use camera clipping for Z-depth numbers",
                default= False,
                update=displayUpdated)

#Scene.thea_zdepthObj = bpy.props.StringProperty(
#                name="Distance",
#                description="Distonce for Zdepth",
#                default= "",
#                update=displayUpdated)

#      CHANGED > Z-depth from ODF
Scene.thea_ZdepthDOF = bpy.props.BoolProperty(
                name="Use Camera DOF",
                description="Use camera DOF for Z-depth numbers",
                default= False,
                update=displayUpdated)

Scene.thea_ZdepthDOFmargin = bpy.props.FloatProperty(
                min=-10000,
                max=10000,
                precision=1,
                default=10,
                name="Falloff (m)",
                description="Use the fall as the min or max for Z-depth",
                update=displayUpdated)

#CHANGED > Added minus number for falloff Zdepth object
Scene.thea_DispMinZ = bpy.props.FloatProperty(
                min=-10000,
                max=100000000,
                precision=3,
                default=0.000,
                name="Min Z (m)",
                description="Min Z (m)",
                update=displayUpdated)

#CHANGED > Added minus number for falloff Zdepth object
Scene.thea_DispMaxZ = bpy.props.FloatProperty(
                min=-10000,
                max=100000000,
                precision=3,
                default=10.000,
                name="Max Z (m)",
                description="Max Z (m)",
                update=displayUpdated)

#CHANGED > added Bloom/glare dropdownlist
Scene.thea_DispBloom = bpy.props.BoolProperty(
                name="Glare",
                description="Glare",
                default= False,
                update=displayUpdated)

Scene.thea_DispBloomItems = bpy.props.EnumProperty(
                items=(('0', 'Radial', ''),('1', '5 Blades', '5'), ('2', '6 Blades','6'),('3', '8 Blades', '8'), ('4', '12 Blades', '12')),
                name="",
                description="Glare",
                default="0",
                update=displayUpdated)


Scene.thea_DispBloomWeight = bpy.props.FloatProperty(
                min=0,
                max=300,
                precision=1,
                default=20,
                name="Weight",
                description="Glare Weight",
                subtype='PERCENTAGE',
                update=displayUpdated)

Scene.thea_DispGlareRadius = bpy.props.FloatProperty(
                min=0,
                max=300,
                precision=1,
                default=4,
                name="Radius",
                description="Glare radius",
                update=displayUpdated)

Scene.thea_DispVignetting = bpy.props.BoolProperty(
                name="Vignetting",
                description="Vignetting",
                default= False,
                update=displayUpdated)

Scene.thea_DispVignettingWeight = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=1,
                default=20,
                name="Vignetting",
                description="Vignetting weight",
                subtype='PERCENTAGE',
                update=displayUpdated)

Scene.thea_analysis = bpy.props.BoolProperty(
                name="Analysis",
                description="Analysis",
                default= False,
                update=displayUpdated)

Scene.thea_analysisMenu = bpy.props.EnumProperty(
                items=(('0', 'None', ''),('1', 'Photometric', '')),
                name="",
                description="Analysis",
                default="0",
                update=displayUpdated)


Scene.thea_minIlLum = bpy.props.FloatProperty(
                min=-10000,
                max=500000,
                precision=0,
                default=0,
                name="Min Il-Lum",
                description="Min Il-Lum",
                update=displayUpdated)

Scene.thea_maxIlLum = bpy.props.FloatProperty(
                min=-10000,
                max=500000,
                precision=0,
                default=15000,
                name="Max Il-Lum",
                description="Max Il-Lum",
                update=displayUpdated)


Scene.thea_MerModels = bpy.props.EnumProperty(
                items=(('0', 'Keep Current - Throw Away New', ''),('1', 'Replace With New - Throw Away Current', ''), ('2', 'Merge - Add New To Current',''),('3', 'Merge - Name Collision: Keep', ''), ('4', 'Merge - Name Collision: Replace', ''), ('5', 'Merge - Name Collision: Replace Mesh', ''), ('6', 'Merge - Name Collision: Replace Material', '')),
                name="Models",
                description="How to merge models",
                default="0")

Scene.thea_MerLights = bpy.props.EnumProperty(
                items=(('0', 'Keep Current - Throw Away New', ''),('1', 'Replace With New - Throw Away Current', ''), ('2', 'Merge - Add New To Current',''),('3', 'Merge - Name Collision: Keep', ''), ('4', 'Merge - Name Collision: Replace', ''), ('5', 'Merge - Name Collision: Replace Possition', ''), ('6', 'Merge - Name Collision: Replace Emitter', '')),
                name="Lights",
                description="How to merge lights",
                default="0")

Scene.thea_MerCameras = bpy.props.EnumProperty(
                items=(('0', 'Keep Current - Throw Away New', ''),('1', 'Replace With New - Throw Away Current', ''), ('2', 'Merge - Add New To Current',''),('3', 'Merge - Name Collision: Keep', ''), ('4', 'Merge - Name Collision: Replace', ''), ('5', 'Merge - Name Collision: Replace Mesh', ''), ('6', 'Merge - Name Collision: Replace Lens', '')),
                name="Cameras",
                description="How to merge cameras",
                default="0")

Scene.thea_MerEnv = bpy.props.EnumProperty(
                items=(('0', 'Keep Current - Throw Away New', ''),('1', 'Replace With New - Throw Away Current', '')),
                name="Environment",
                description="How to merge environment",
                default="0")

Scene.thea_MerRender = bpy.props.EnumProperty(
                items=(('0', 'Keep Current - Throw Away New', ''),('1', 'Replace With New - Throw Away Current', '')),
                name="Render",
                description="How to merge render settings",
                default="0")

Scene.thea_MerMaterials = bpy.props.EnumProperty(
                items=(('0', 'Add new to Current', ''),('1', 'Merge - Name Collision: Keep', ''), ('2', 'Merge - Name Collision: Replace', '')),
                name="Materials",
                description="How to merge materials",
                default="0")

Scene.thea_MerSurfaces = bpy.props.EnumProperty(
                items=(('0', 'Add new to Current', ''),('1', 'Merge - Name Collision: Keep', ''), ('2', 'Merge - Name Collision: Replace', '')),
                name="Surfaces",
                description="How to merge surfaces",
                default="0")

Scene.thea_ICEnable = bpy.props.BoolProperty(
                name="Enable",
                description="Enable",
                default= True)

Scene.thea_ICLock = bpy.props.BoolProperty(
                name="Lock Cache",
                description="Lock Cache",
                default= False)

Scene.thea_ICAccuracy = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=3,
                default=85,
                name="Sample Density",
                description="Sample Density")

Scene.thea_ICMinDistance = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=3,
                default=0.2,
                name="Min Distance",
                description="Min Distance")

Scene.thea_ICMaxDistance = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=3,
                default=10,
                name="Max Distance",
                description="Max Distance")

Scene.thea_ICMinDistance = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=3,
                default=4,
                name="Min Distance",
                description="Min Distance")

Scene.thea_ICPrepass = bpy.props.EnumProperty(
                items=(('0', 'None', ''),('1', '1/1', ''),('2', '1/2', ''),('3', '1/4', ''),('4', '1/8', '')),
                name="Prepass",
                description="Prepass",
                default="1")

Scene.thea_ICPrepassBoost = bpy.props.FloatProperty(
                min=0,
                max=10,
                precision=3,
                default=0.5,
                name="Prepass Boost",
                description="Prepass Boost")

Scene.thea_ICForceInterpolation = bpy.props.BoolProperty(
                name="ForceInterpolation",
                description="ForceInterpolation",
                default= True)

Scene.thea_Warning = bpy.props.StringProperty(
                maxlen=15,
                default="0",
                name="Warning",
                description="Warning")

Scene.thea_RenderPresetsMenu = bpy.props.EnumProperty(
                items=getTheaPresets(),
                name="Render Presets",
                description="Render Presets",
                default="0")

Scene.thea_maxLines = bpy.props.IntProperty(
                min=200,
                max=2000,
                default=200,
                name="maxLines",
                description="maxLines")

Scene.thea_dataPath = bpy.props.StringProperty(
                maxlen=1024,
                default="",
                name="Thea data path",
                description="Thea data path")

Scene.thea_channelNormal = bpy.props.BoolProperty(
                name="Normal",
                description="Normal",
                default= False)

Scene.thea_channelPosition = bpy.props.BoolProperty(
                name="Position",
                description="Position",
                default= False)

Scene.thea_channelUV = bpy.props.BoolProperty(
                name="UV",
                description="UV",
                default= False)

Scene.thea_channelDepth = bpy.props.BoolProperty(
                name="Depth",
                description="Depth",
                default= False)

Scene.thea_channelAlpha = bpy.props.BoolProperty(
                name="Alpha",
                description="Alpha",
                default= False)

Scene.thea_channelObject_Id = bpy.props.BoolProperty(
                name="Object Id",
                description="Object Id",
                default= False)

Scene.thea_channelMaterial_Id = bpy.props.BoolProperty(
                name="Material Id",
                description="Material Id",
                default= False)

Scene.thea_channelShadow = bpy.props.BoolProperty(
                name="Shadow",
                description="Shadow",
                default= False)

Scene.thea_channelMask = bpy.props.BoolProperty(
                name="Mask",
                description="Mask",
                default= False)

Scene.thea_channelRaw_Diffuse_Color = bpy.props.BoolProperty(
                name="Raw Diffuse Color",
                description="Raw Diffuse Color",
                default= False)

Scene.thea_channelRaw_Diffuse_Lighting = bpy.props.BoolProperty(
                name="Raw Diffuse Lighting",
                description="Raw Diffuse Lighting",
                default= False)

Scene.thea_channelRaw_Diffuse_GI = bpy.props.BoolProperty(
                name="Raw Diffuse GI",
                description="Raw Diffuse GI",
                default= False)

Scene.thea_channelSelf_Illumination = bpy.props.BoolProperty(
                name="Self Illumination",
                description="Self Illumination",
                default= False)

Scene.thea_channelDirect = bpy.props.BoolProperty(
                name="Direct",
                description="Direct",
                default= False)

Scene.thea_channelAO = bpy.props.BoolProperty(
                name="AO",
                description="AO",
                default= False)

Scene.thea_channelGI = bpy.props.BoolProperty(
                name="GI",
                description="GI",
                default= False)


Scene.thea_channelSSS = bpy.props.BoolProperty(
                name="SSS",
                description="SSS",
                default= False)

Scene.thea_channelSeparate_Passes_Per_Light = bpy.props.BoolProperty(
                name="Separate Passes Per Light",
                description="Separate Passes Per Light",
                default= False)

Scene.thea_channelReflection = bpy.props.BoolProperty(
                name="Reflection",
                description="Reflection",
                default= False)

Scene.thea_channelRefraction = bpy.props.BoolProperty(
                name="Refraction",
                description="Refraction",
                default= False)

Scene.thea_channelTransparent = bpy.props.BoolProperty(
                name="Transparent",
                description="Transparent",
                default= False)

Scene.thea_channelIrradiance = bpy.props.BoolProperty(
                name="Irradiance",
                description="Irradiance",
                default= False)

Scene.thea_channelInvert_Mask = bpy.props.BoolProperty(
                name="Invert Mask Channel",
                description="Invert Mask Channel",
                default= False)

Scene.thea_startTheaAfterExport = bpy.props.BoolProperty(
                name="start Thea after export",
                description="start Thea after export",
                default= False)

#CHANGED > Made the dropdown menu like studio

Scene.thea_mergeFilePath = bpy.props.StringProperty(
                name="Merge scene",
                description="Merge Thea scene",
                default= "")

Scene.thea_SceneMerModels = bpy.props.EnumProperty(
                items=(('0', 'Keep Current - Throw Away New', ''),('1', 'Replace With New - Throw Away Current', ''), ('2', 'Merge - Add New To Current',''),('3', 'Merge - Name Collision: Keep', ''), ('4', 'Merge - Name Collision: Replace', ''), ('5', 'Merge - Name Collision: Replace Mesh', ''), ('6', 'Merge - Name Collision: Replace Material', '')),
                name="Models",
                description="How to merge models",
                default="0")

Scene.thea_SceneMerLights = bpy.props.EnumProperty(
                items=(('0', 'Keep Current - Throw Away New', ''),('1', 'Replace With New - Throw Away Current', ''), ('2', 'Merge - Add New To Current',''),('3', 'Merge - Name Collision: Keep', ''), ('4', 'Merge - Name Collision: Replace', ''), ('5', 'Merge - Name Collision: Replace Possition', ''), ('6', 'Merge - Name Collision: Replace Emitter', '')),
                name="Lights",
                description="How to merge lights",
                default="0")

Scene.thea_SceneMerCameras = bpy.props.EnumProperty(
                items=(('0', 'Keep Current - Throw Away New', ''),('1', 'Replace With New - Throw Away Current', ''), ('2', 'Merge - Add New To Current',''),('3', 'Merge - Name Collision: Keep', ''), ('4', 'Merge - Name Collision: Replace', ''), ('5', 'Merge - Name Collision: Replace Mesh', ''), ('6', 'Merge - Name Collision: Replace Lens', '')),
                name="Cameras",
                description="How to merge cameras",
                default="0")

Scene.thea_SceneMerRender = bpy.props.EnumProperty(
                items=(('0', 'Keep Current - Throw Away New', ''),('1', 'Replace With New - Throw Away Current', '')),
                name="Render",
                description="How to merge render settings",
                default="0")

Scene.thea_SceneMerMaterials = bpy.props.EnumProperty(
                items=(('0', 'Keep Current - Throw Away New', ''),('1', 'Merge - Name Collision: Keep', ''), ('2', 'Merge - Name Collision: Replace', '')),
                name="Materials",
                description="How to merge materials",
                default="0")

Scene.thea_SceneMerEnv = bpy.props.EnumProperty(
                items=(('0', 'Keep Current - Throw Away New', ''),('1', 'Replace With New - Throw Away Current', '')),
                name="Environment",
                description="How to merge environment",
                default="0")

Scene.thea_SceneMerReverseOrder = bpy.props.BoolProperty(
                name="Load Thea scene first",
                description="Load Thea scene first",
                default= False)

Scene.thea_AOEnable = bpy.props.BoolProperty(
                name="Enable",
                description="Enable AO",
                default= True,
                update=engineUpdated)

Scene.thea_AOLowColor = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Low Color",
                description="AO Low Color",
                subtype="COLOR")

Scene.thea_AOHighColor = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="High Color",
                description="AO Low Color",
                subtype="COLOR",
                default=(1.0,1.0,1.0))

Scene.thea_AOMultiply = bpy.props.BoolProperty(
                name="Multiply",
                description="Multiply",
                default= False)

Scene.thea_AOClamp = bpy.props.BoolProperty(
                name="Clamp",
                description="Clamp",
                default= False)

Scene.thea_AOSamples = bpy.props.IntProperty(
                min=1,
                max=1000,
                default=100,
                name="Samples",
                description="Samples")

Scene.thea_AODistance = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=2,
                default=10,
                name="Distance",
                description="This is the maximum distance that the sample may be evaluated to an intermediate (gray) color. After that distance, the sample is evaluated to white color.",
                update=engineUpdated)

Scene.thea_AOIntensity = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=2,
                default=10,
                name="Intensity",
                description="This value defines the intensity of the Ambient Occlusion used.",
                update=engineUpdated)

def materialLutUpdated(self, context):
    '''Change material name according to LUT when name based LUT is used and update diffuse color based on material preview

        :param context: context
    '''
    lut = getLUTarray()
    mat = context.material
    print("mat.get('thea_LUT')", mat.get('thea_LUT'))
    if mat.use_cubic:
       mat.use_cubic = False
    else:
       mat.use_cubic = True
    if thea_globals.getNameBasedLUT() and mat.get('thea_LUT') > 0:
       mat.name = lut[mat.get('thea_LUT')]
       thea_globals.log.debug("Mat LUT start: %s - index: %s" % (lut[mat.get('thea_LUT')], mat.get('thea_LUT')))
    updateActiveMaterialColor()



def materialUpdated(self, context):
    '''Set thea_globals.materialUpdated = True when material has been updated
    '''

    mat = context.material
    thea_globals.materialUpdated = True
    print("updated")
    if thea_globals.materialUpdatesNumber<10:
        thea_globals.materialUpdatesNumber += 2

    mat.thea_MaterialLayoutVersion = 2.0;
    # change some unused value to force material preview render
    if mat.use_object_color:
        mat.use_object_color = False
    else:
        mat.use_object_color = True

    updateCurveMaterial(self, context)

def diffuseColorUpdated(self, context):
    '''Update diffuse color
    '''
    mat = context.material
    mat.diffuse_color = getattr(mat, "thea_BasicDiffuseCol")
    materialUpdated(context)


def materialFilenameUpdated(self, context, origin=""):
    '''Create texture and set it when one of the material filename properties are updated

        :param context: context
        :param origin: filename parameter which has been updated
        :type origin: string
    '''

    thea_globals.log.debug("materialFilenameUpdated: %s, %s, %s, %s" % (self, context, origin, context.material.get(origin)))
    mat = context.material
    imgName = context.material.get(origin)
    texName = mat.name+"_"+origin
    exists = False
    try:
        if mat.texture_slots[texName]:
            exists = True
            slot = mat.texture_slots[texName]
            tex = slot.texture
    except:
        pass

    if exists:
        try:
            if imgName:
                img = bpy.data.images.load(imgName)
                tex.image = img
            else:
                print("removing texture: ", slot, tex)
                mat.texture_slots[texName].texture = None
        except:
            pass
    else:
        img = bpy.data.images.load(imgName)
        tex = bpy.data.textures.new(name=texName, type='IMAGE')
#        if (img.mode == 'RGBA'):
#        thea_globals.log.debug("### Texture has alpha ###")
#        thea_globals.log.debug("### Texture Type: %s - ALpha:###" % img.file_format)
#        for i in range(0, len(bpy.data.images[img.name].pixels), 4):

        tex.image = img
        tex.name = texName
        slot = mat.texture_slots.add()
        slot.texture = tex
        slot.texture_coords='UV'
        if 'Diffuse' in tex.name:
            slot.use_map_color_diffuse=True
        if 'Reflectance' in tex.name:
            slot.use_map_color_spec=True
            slot.use_map_color_diffuse=False
        if 'Reflect90' in tex.name:
            slot.use_map_color_spec=True
            slot.use_map_color_diffuse=False
        if 'Translucent' in tex.name:
            slot.use_map_translucency=True
            slot.use_map_color_diffuse=False
        if 'Bump' in tex.name:
            slot.use_map_normal=True
            slot.use_map_color_diffuse=False
            slot.use_map_color_diffuse=False
        if 'Weight' in tex.name:
            slot.use_stencil=True
            slot.use_map_color_diffuse=False
        if 'Roughness' in tex.name:
            slot.use_map_hardness=True
            slot.use_map_color_diffuse=False
        if 'RoughnessTr' in tex.name:
            slot.texture.thea_RoughnessTrTex=True
            slot.use_map_color_diffuse=False
        if 'Sigma' in tex.name:
            slot.texture.thea_StructureSigmaTex=True
            slot.use_map_color_diffuse=False
        if 'Anisotropy' in tex.name:
            slot.texture.thea_StructureAnisotropyTex=True
            slot.texture.thea_CoatingStructureAnisotropyTex=True
            slot.use_map_color_diffuse=False
        if 'Rotation' in tex.name:
            slot.texture.thea_StructureRotationTex=True
            slot.texture.thea_CoatingStructureRotationTex=True
            slot.use_map_color_diffuse=False
        if 'MediumAbsorption' in tex.name:
            slot.texture.thea_MediumAbsorptionTex=True
            slot.texture.thea_Medium=True
            slot.use_map_color_diffuse=False
        if 'Scatter' in tex.name:
            slot.texture.thea_MediumScatterTex=True
            slot.texture.thea_Medium=True
            slot.use_map_color_diffuse=False
        if 'AbsorptionDensity' in tex.name:
            slot.texture.thea_MediumAbsorptionDensityTex=True
            slot.texture.thea_Medium=True
            slot.use_map_color_diffuse=False
        if 'ScatterDensity' in tex.name:
            slot.texture.thea_MediumScatterDensityTex=True
            slot.texture.thea_Medium=True
            slot.use_map_color_diffuse=False
        if 'Transmittance' in tex.name:
            slot.use_map_alpha=True
            slot.use_map_color_diffuse=False
        if 'Thickness' in tex.name:
            slot.texture.thea_CoatingThicknessTex=True
            slot.use_map_color_diffuse=False
        if 'CoatingAbsorption' in tex.name:
            slot.texture.thea_CoatingAbsorptionTex=True
            #print("check IntTex is true")
#       CHANGED > Tried to catch interference thickness here
        if 'ThinFilmThickness' in tex.name:
            slot.texture.thea_ThinFilmThicknessTex=True
            slot.use_map_color_diffuse=False
            #print("check IntTex is true")
        if 'Basic' in tex.name:
            slot.texture.thea_Basic=True
        if 'Basic2' in tex.name:
            slot.texture.thea_Basic2=True
        if 'Glossy' in tex.name:
            slot.texture.thea_Glossy=True
        if 'Glossy2' in tex.name:
            slot.texture.thea_Glossy=True
        if 'SSS' in tex.name:
            slot.texture.thea_SSS=True
        if 'ThinFilm' in tex.name:
            slot.texture.thea_ThinFilm=True
            slot.texture.thea_ThinFilmThicknessTex=True
        if 'Coating' in tex.name:
            slot.texture.thea_Coating=True
        if 'Clipping' in tex.name:
            slot.texture.thea_Clipping=True
            slot.use_map_alpha=True
        if 'Displacement' in tex.name:
            #slot.texture.thea_Displacement=True
            slot.use_map_displacement=True
        if 'Emittance' in tex.name:
            slot.texture.thea_Emittance=True

    if thea_globals.materialUpdatesNumber<10:
        thea_globals.materialUpdatesNumber += 1
    mat.thea_MaterialLayoutVersion = 2.0;
    thea_globals.materialUpdate = True
    updateCurveMaterial(self, context)
    #materialUpdated(context)


Mat.thea_OldLayout = bpy.props.BoolProperty(
                name="Old layout",
                description="Show old material layout",
                default= False)

def updateUnbiasedPreview(self, context):
    '''Set thea_globals.unbiasedPreview when thea_EnableUnbiasedPreview property is updated

        :param context: context
    '''
    mat = context.material
    # Dirty trick to update when scene i picked :)
    mat.diffuse_color = mat.diffuse_color
    thea_globals.unbiasedPreview = getattr(mat, "thea_EnableUnbiasedPreview")

Mat.thea_EnableUnbiasedPreview = bpy.props.BoolProperty(
#    CHANGED > Shorter button description
    name="Unbiased",
    description="Use unbiased engine for rendering preview",
    default= False,
    update=updateUnbiasedPreview)

def updatePreviewScene(self, context):
    '''Set thea_globals.previewScene when preview scene property is updated

        :param context: context
    '''
    mat = context.material
    # Dirty trick to update when scene i picked :)
    mat.diffuse_color = mat.diffuse_color
    thea_globals.previewScene = getTheaPreviewScenesMenuItems()[int(getattr(mat, "thea_PreviewScenesMenu"))][1]+".scn.thea"
#     print("thea_globals.previewScene: ", thea_globals.previewScene)


def getMaterialExtras(self, context):
    '''Return extras list menu entries

        :param context: context
        :return: list of tuples (component, component, component, icon, i)
        :rtype: [(str, str, str, str, int)]
    '''
    components = ("Coating", "Clipping", "Displacement", "Emittance", "Medium")
    items = []
    i=0
    for component in components:
        #icon="RADIOBUT_OFF"
        icon="RADIOBUT_OFF" #"CHECKBOX_DEHLT"
        if hasattr(bpy.context, 'active_object'):
            if getattr(bpy.context.active_object.active_material, "thea_"+component):
                #icon="RADIOBUT_ON"
                icon="RADIOBUT_ON"# "CHECKBOX_HLT"
        items.append((component, component, component, icon, i))
        i+=1
    return items


Mat.thea_materialExtras = bpy.props.EnumProperty(
                items=getMaterialExtras,
                name="Material Extra's Menu",
                description="Edit material extra's")

Mat.thea_PreviewScenesMenu = bpy.props.EnumProperty(
                items=getTheaPreviewScenesMenuItems(),
#                CHANGED > Shorter name liek studio
                name="Room",
                description="Thea preview scene",
                update=updatePreviewScene)

Mat.thea_MaterialLayoutVersion = bpy.props.FloatProperty(
                min=0,
                max=100,
                default=0,
                name="Material Layout Version",
                description="Material Layout Version")

Mat.thea_LUT = bpy.props.EnumProperty(
                items=getLUT(),
                name="Thea Material",
                description="Material from LUT file",
                default="0",
                update=materialLutUpdated)

Mat.thea_ShadowCatcher = bpy.props.BoolProperty(
                name="Shadow Catcher",
                description="Shadow Catcher",
                default= False,
                update=materialUpdated)

Mat.thea_twoSided = bpy.props.BoolProperty(
                name="Two-Sided",
                description="Two-Sided",
                default= True,
                update=materialUpdated)

Mat.thea_repaintable = bpy.props.BoolProperty(
                name="Repaintable",
                description="Repaintable",
                default= False,
                update=materialUpdated)

Mat.thea_dirt = bpy.props.BoolProperty(
                name="Dirt",
                description="Dirt",
                default= False,
                update=materialUpdated)

Mat.thea_description = bpy.props.StringProperty(
                name="Description",
                description="Description",
                default= "")

Mat.thea_Basic = bpy.props.BoolProperty(
                name="Basic",
                description="Enable Basic material component",
                default= True,
                update=materialUpdated)

Mat.thea_BasicOrder = bpy.props.IntProperty(
                min=0,
                max=10,
                default=0,
                name="Order",
                description="Order",
                update=materialUpdated)

Mat.thea_BasicWeight = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=100.0,
                name="Layer Weight",
                description="Layer Weight",
                update=materialUpdated)

Mat.thea_BasicWeightFilename = bpy.props.StringProperty(
                  name = "Weight texture",
                  default = "",
                  description = "Weight texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_BasicWeightFilename")
                  )

Mat.thea_BasicDiffuseCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                default=(0.5, 0.5, 0.5),
                name="Diffuse",
                description="Diffuse Color",
                subtype="COLOR",
                update=diffuseColorUpdated)

Mat.thea_BasicDiffuseEnable = bpy.props.BoolProperty(
                name = "Enable texture",
                default = False,
                description = "Enable diffuse Color texture file path")

Mat.thea_BasicDiffuseFilename = bpy.props.StringProperty(
                  name = "Diffuse Color texture",
                  default = "",
                  description = "Diffuse Color texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_BasicDiffuseFilename")
                  )

Mat.thea_BasicReflectanceCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Reflectance",
                default=(0, 0, 0),
                description="Reflectance Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_BasicReflectanceFilename = bpy.props.StringProperty(
                  name = "Reflectance Color texture",
                  default = "",
                  description = "Reflectance Color texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_BasicReflectanceFilename")
                  )

Mat.thea_BasicReflect90Col = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Reflect 90",
                default=(1, 1, 1),
                description="Reflectance 90 Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_BasicReflect90Filename = bpy.props.StringProperty(
                name = "Reflect 90",
                default = "",
                description = "Reflect 90 texture file path",
                subtype = 'FILE_PATH',
                update=lambda a,b: materialFilenameUpdated(a,b,"thea_BasicReflect90Filename"))


Mat.thea_BasicTranslucentCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Translucent",
                description="Translucent Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_BasicTranslucentFilename = bpy.props.StringProperty(
                  name = "Translucent Color texture",
                  default = "",
                  description = "Translucent Color texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_BasicTranslucentFilename")
                  )

Mat.thea_BasicAbsorptionCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Absorption",
                description="Absorption Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_BasicAbsorption = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=2,
                default=0.0,
                name="Absorption",
                description="Absorption",
                update=materialUpdated)

Mat.thea_BasicIOR = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=3,
                default=1.5,
                name="Index of Refraction (n)",
                description="Index of Refraction (n)",
                update=materialUpdated)

Mat.thea_BasicEC = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=3,
                default=0.0,
                name="Extinction Coefficient (k)",
                description="Extinction Coefficient (k)",
                update=materialUpdated)

Mat.thea_BasicTrace = bpy.props.BoolProperty(
                name="Trace Reflections",
                description="Trace Reflections",
                default= True,
                update=materialUpdated)

Mat.thea_BasicStructureSigma = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Sigma (%)",
                subtype='PERCENTAGE',
                description="Sigma (%)",
                update=materialUpdated)

Mat.thea_BasicStructureRoughness = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=10.0,
                name="Roughness (%)",
                description="Roughness (%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_BasicStructureAnisotropy = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Anisotropy (%)",
                description="Anisotropy (%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_BasicStructureRotation = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Rotation (deg)",
                description="Rotation (deg)",
                update=materialUpdated)

Mat.thea_BasicStructureBump = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=100.0,
                name="Bump (%)",
                description="Bump (%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_BasicBumpFilename = bpy.props.StringProperty(
                  name = "Bumpmap texture",
                  default = "",
                  description = "Bumpmap texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_BasicBumpFilename")
                  )

Mat.thea_BasicSigmaFilename = bpy.props.StringProperty(
                  name = "Sigma texture",
                  default = "",
                  description = "Sigma texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_BasicSigmaFilename")
                  )

Mat.thea_BasicRoughnessFilename = bpy.props.StringProperty(
                  name = "Roughness texture",
                  default = "",
                  description = "Roughness texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_BasicRoughnessFilename")
                  )

Mat.thea_BasicAnisotropyFilename = bpy.props.StringProperty(
                  name = "Anisotropy texture",
                  default = "",
                  description = "Anisotropy texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_BasicAnisotropyFilename")
                  )

Mat.thea_BasicRotationFilename = bpy.props.StringProperty(
                  name = "Rotation texture",
                  default = "",
                  description = "Rotation texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_BasicRotationFilename")
                  )

Mat.thea_BasicStructureNormal = bpy.props.BoolProperty(
                name="Normal mapping",
                description="Enable normal mapping",
                default= False,
                update=materialUpdated)

Mat.thea_BasicMicroRoughness = bpy.props.BoolProperty(
                name="Micro Roughness",
                description="Enable MicroRoughness",
                default= False,
                update=materialUpdated)

Mat.thea_BasicMicroRoughnessWidth = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=2,
                default=10.0,
                name="Width (um)",
                description="Width (um)",
                update=materialUpdated)

Mat.thea_BasicMicroRoughnessHeight = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=3,
                default=0.25,
                name="Height (um)",
                description="Height (um)",
                update=materialUpdated)


def updateCurveMaterial(self, context):
    mat = context.material
#    def myfunction(input, a=False, b=False, c=False, d=False):
#    if filter(None,[a, b, c, d]) != [True]:
#        print("Please specify only one of 'a', 'b', 'c', 'd'.)")
    checkItems  = ("thea_BasicReflectionCurve", "thea_Basic2ReflectionCurve", "thea_GlossyReflectionCurve", "thea_Glossy2ReflectionCurve",  "thea_CoatingReflectionCurve", "thea_SSSReflectionCurve")
    for item in checkItems:
        try:
            if mat[item]:
                setattr(mat, item, True)
            else:
                pass

        except:
            pass
#    try:
#        mat.thea_BasicReflectionCurve = mat.thea_Basic2ReflectionCurve = mat.theaGlossyReflectionCurve = mat.thea_Glossy2ReflectionCurve = mat.thea_SSSReflectionCurve = mat.thea_CoatingReflectionCurve = True # update curve list manual
#    except:
#        pass


def CustomCurveUpdate(self, context, origin=""):
    mat = context.material
    mat.use_nodes = True
    mat.use_nodes = False
    curveName = mat.name
    nodes = mat.node_tree.nodes

    if curveName+"_"+origin not in mat.node_tree.nodes:
        cn = nodes.new('ShaderNodeRGBCurve')
        nodes['RGB Curves'].name = curveName+"_"+origin
    c = nodes[curveName+"_"+origin].mapping.curves[3]
    d = nodes[curveName+"_"+origin].mapping
    d.initialize()
    curve = c
    # curve is the curve map, it has an evaluate function, that returns the y value of the curve at point x
    point = curve.evaluate(0) #gives the value of the curve at x=0
    points = str([round((curve.evaluate(i/91)*255)*257) for i in range(91)]) # gives what you want.
    if origin == "thea_BasicReflectCurve":
        setattr(mat,"thea_BasicReflectCurveList", points)
        setattr(mat,"thea_BasicReflectCurve", curveName+"_"+origin)
    if origin == "thea_Basic2ReflectCurve":
        setattr(mat,"thea_Basic2ReflectCurveList", points)
        setattr(mat,"thea_Basic2ReflectCurve", curveName+"_"+origin)
    if origin == "thea_GlossyReflectCurve":
        setattr(mat,"thea_GlossyReflectCurveList", points)
        setattr(mat,"thea_GlossyReflectCurve", curveName+"_"+origin)
    if origin == "thea_Glossy2ReflectCurve":
        setattr(mat,"thea_Glossy2ReflectCurveList", points)
        setattr(mat,"thea_Glossy2ReflectCurve", curveName+"_"+origin)
    if origin == "thea_SSSReflectCurve":
        setattr(mat,"thea_SSSReflectCurveList", points)
        setattr(mat,"thea_SSSReflectCurve", curveName+"_"+origin)
    if origin == "thea_CoatingReflectCurve":
        setattr(mat,"thea_CoatingReflectCurveList", points)
        setattr(mat,"thea_CoatingReflectCurve", curveName+"_"+origin)


Mat.thea_BasicReflectionCurve = bpy.props.BoolProperty(
                name="Custom Reflection Curve",
                description="Enable custom reflecion curve",
                default= False,
                update=lambda a,b: CustomCurveUpdate(a,b,"thea_BasicReflectCurve"))

Mat.thea_BasicReflectCurve = bpy.props.StringProperty(
                name = "Custom Curve",
                default = "",
                description = "Custom Curve")

Mat.thea_BasicReflectCurveList = bpy.props.StringProperty(
                name = "Custom Curve List",
                default = "",
                description = "Custom Curve List")

Mat.thea_Basic2 = bpy.props.BoolProperty(
                name="Basic2",
                description="Enable second Basic material component",
                default= False,
                update=materialUpdated)

Mat.thea_Basic2Order = bpy.props.IntProperty(
                min=0,
                max=10,
                default=0,
                name="Order",
                description="Order",
                update=materialUpdated)

Mat.thea_Basic2Weight = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=100.0,
                name="Layer Weight",
                description="Layer Weight",
                update=materialUpdated)

Mat.thea_Basic2WeightFilename = bpy.props.StringProperty(
                  name = "Weight texture",
                  default = "",
                  description = "Weight texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Basic2WeightFilename")
                  )

Mat.thea_Basic2DiffuseCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Diffuse",
                default=(0.5, 0.5, 0.5),
                description="Diffuse Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_Basic2DiffuseFilename = bpy.props.StringProperty(
                  name = "Diffuse Color texture",
                  default = "",
                  description = "Diffuse Color texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Basic2DiffuseFilename")
                  )

Mat.thea_Basic2ReflectanceCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Reflectance",
                default=(0, 0, 0),
                description="Reflectance Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_Basic2ReflectanceFilename = bpy.props.StringProperty(
                  name = "Reflectance Color texture",
                  default = "",
                  description = "Reflectance Color texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Basic2ReflectanceFilename")
                  )

Mat.thea_Basic2Reflect90Col = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Reflect 90",
                default=(1, 1, 1),
                description="Reflectance 90 Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_Basic2Reflect90Filename = bpy.props.StringProperty(
                name = "Reflect 90",
                default = "",
                description = "Reflect 90 texture file path",
                subtype = 'FILE_PATH',
                update=lambda a,b: materialFilenameUpdated(a,b,"thea_Basic2Reflect90Filename"))


Mat.thea_Basic2TranslucentCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Translucent",
                description="Translucent Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_Basic2TranslucentFilename = bpy.props.StringProperty(
                  name = "Translucent Color texture",
                  default = "",
                  description = "Translucent Color texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Basic2TranslucentFilename")
                  )

Mat.thea_Basic2AbsorptionCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Absorption",
                description="Absorption Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_Basic2Absorption = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=2,
                default=0.0,
                name="Absorption",
                description="Absorption",
                update=materialUpdated)

Mat.thea_Basic2IOR = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=3,
                default=1.5,
                name="Index of Refraction (n)",
                description="Index of Refraction (n)",
                update=materialUpdated)

Mat.thea_Basic2EC = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=3,
                default=0.0,
                name="Extinction Coefficient (k)",
                description="Extinction Coefficient (k)",
                update=materialUpdated)

Mat.thea_Basic2Trace = bpy.props.BoolProperty(
                name="Trace Reflections",
                description="Trace Reflections",
                default= True,
                update=materialUpdated)

Mat.thea_Basic2StructureSigma = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Sigma (%)",
                subtype='PERCENTAGE',
                description="Sigma (%)",
                update=materialUpdated)

Mat.thea_Basic2StructureRoughness = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=10.0,
                name="Roughness (%)",
                subtype='PERCENTAGE',
                description="Roughness (%)",
                update=materialUpdated)

Mat.thea_Basic2StructureAnisotropy = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Anisotropy (%)",
                subtype='PERCENTAGE',
                description="Anisotropy (%)",
                update=materialUpdated)

Mat.thea_Basic2StructureRotation = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Rotation (deg)",
                description="Rotation (deg)")

Mat.thea_Basic2StructureBump = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=100.0,
                name="Bump (%)",
                subtype='PERCENTAGE',
                description="Bump (%)",
                update=materialUpdated)

Mat.thea_Basic2BumpFilename = bpy.props.StringProperty(
                  name = "Bumpmap texture",
                  default = "",
                  description = "Bumpmap texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Basic2BumpFilename")
                  )

Mat.thea_Basic2SigmaFilename = bpy.props.StringProperty(
                  name = "Sigma texture",
                  default = "",
                  description = "Sigma texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Basic2SigmaFilename")
                  )

Mat.thea_Basic2RoughnessFilename = bpy.props.StringProperty(
                  name = "Roughness texture",
                  default = "",
                  description = "Roughness texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Basic2RoughnessFilename")
                  )

Mat.thea_Basic2AnisotropyFilename = bpy.props.StringProperty(
                  name = "Anisotropy texture",
                  default = "",
                  description = "Anisotropy texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Basic2AnisotropyFilename")
                  )

Mat.thea_Basic2RotationFilename = bpy.props.StringProperty(
                  name = "Rotation texture",
                  default = "",
                  description = "Rotation texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Basic2RotationFilename")
                  )

Mat.thea_Basic2StructureNormal = bpy.props.BoolProperty(
                name="Normal mapping",
                description="Enable normal mapping",
                default= False,
                update=materialUpdated)

Mat.thea_Basic2MicroRoughness = bpy.props.BoolProperty(
                name="Micro Roughness",
                description="Enable MicroRoughness",
                default= False,
                update=materialUpdated)

Mat.thea_Basic2MicroRoughnessWidth = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=2,
                default=10.0,
                name="Width (um)",
                description="Width (um)",
                update=materialUpdated)

Mat.thea_Basic2MicroRoughnessHeight = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=3,
                default=0.25,
                name="Height (um)",
                description="Height (um)",
                update=materialUpdated)

Mat.thea_Basic2ReflectionCurve = bpy.props.BoolProperty(
                name="Custom Reflection Curve",
                description="Enable custom reflecion curve",
                default= False,
                update=lambda a,b: CustomCurveUpdate(a,b,"thea_Basic2ReflectCurve"))

Mat.thea_Basic2ReflectCurve = bpy.props.StringProperty(
                name = "Custom Curve",
                default = "",
                description = "Custom Curve")

Mat.thea_Basic2ReflectCurveList = bpy.props.StringProperty(
                name = "Custom Curve List",
                default = "",
                description = "Custom Curve List")



Mat.thea_Glossy = bpy.props.BoolProperty(
                name="Glossy",
                description="Enable Glossy material component",
                default= False,
                update=materialUpdated)

Mat.thea_GlossyOrder = bpy.props.IntProperty(
                min=0,
                max=10,
                default=0,
                name="Order",
                description="Order",
                update=materialUpdated)

Mat.thea_GlossyWeight = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=100.0,
                name="Layer Weight",
                description="Layer Weight",
                update=materialUpdated)

Mat.thea_GlossyWeightFilename = bpy.props.StringProperty(
                  name = "Weight texture",
                  default = "",
                  description = "Weight texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_GlossyWeightFilename")
                  )

Mat.thea_GlossyReflectanceCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                default=(1, 1, 1),
                name="Reflectance",
                description="Reflectance Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_GlossyReflectanceFilename = bpy.props.StringProperty(
                  name = "Reflectance texture",
                  default = "",
                  description = "Reflectance texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_GlossyReflectanceFilename")
                  )

Mat.thea_GlossyReflect90Col = bpy.props.FloatVectorProperty(
                min=0, max=1,
                default=(1, 1, 1),
                name="Reflectance 90",
                description="Reflectance 90 Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_GlossyReflect90Filename = bpy.props.StringProperty(
                  name = "Reflectance 90 texture",
                  default = "",
                  description = "Reflectance 90 texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_GlossyReflect90Filename")
                  )

Mat.thea_GlossyTransmittanceCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Transmittance",
                description="Transmittance Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_GlossyTransmittanceFilename = bpy.props.StringProperty(
                  name = "Transmittance texture",
                  default = "",
                  description = "Transmittance texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_GlossyTransmittanceFilename")
                  )

Mat.thea_GlossyAbsorptionCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Absorption",
                description="Absorption Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_GlossyAbsorption = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=2,
                default=0.0,
                name="Absorption",
                description="Absorption",
                update=materialUpdated)

Mat.thea_GlossyIOR = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=3,
                default=1.5,
                name="Index of Refraction (n)",
                description="Index of Refraction (n)",
                update=materialUpdated)

Mat.thea_GlossyEC = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=3,
                default=0.0,
                name="Extinction Coefficient (k)",
                description="Extinction Coefficient (k)",
                update=materialUpdated)

Mat.thea_GlossyAbbeNumberEnable = bpy.props.BoolProperty(
                name="Abbe",
                description="Abbe",
                default= False,
                update=materialUpdated)

Mat.thea_GlossyAbbeNumber = bpy.props.FloatProperty(
                min=0,
                max=200,
                precision=3,
                default=50.0,
                name="Number",
                description="Number",
                update=materialUpdated)

Mat.thea_GlossyIORFileEnable = bpy.props.BoolProperty(
                name="IOR file",
                description="IOR file (Turn Off Abbe if ON)",
                default= False,
                update=materialUpdated)

Mat.thea_GlossyIORMenu = bpy.props.EnumProperty(
                items=getTheaIORMenuItems(),
                name="File",
                description="File",
                update=materialUpdated)

Mat.thea_GlossyTraceReflections = bpy.props.BoolProperty(
                name="Trace Reflections",
                description="Trace Reflections",
                default= True,
                update=materialUpdated)

Mat.thea_GlossyTraceRefractions = bpy.props.BoolProperty(
                name="Trace Refractions",
                description="Trace Refractions",
                default= True,
                update=materialUpdated)

Mat.thea_GlossyStructureRoughness = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Roughness (%)",
                subtype='PERCENTAGE',
                description="Roughness (%)",
                update=materialUpdated)

Mat.thea_GlossyStructureRoughTrEn = bpy.props.BoolProperty(
                name="Roughness Tr (%)",
                subtype='PERCENTAGE',
                description="Roughness Tr (%)",
                default= False,
                update=materialUpdated)


Mat.thea_GlossyStructureRoughnessTr = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=10.0,
                name="(%)",
                subtype='PERCENTAGE',
                description="(%)",
                update=materialUpdated)

Mat.thea_GlossyRoughnessTrFilename = bpy.props.StringProperty(
                name = "Glossy Roughness TR Texture",
                default = "",
                description = "Glossy Roughness Tr file path",
                subtype = 'FILE_PATH',
                update=lambda a,b: materialFilenameUpdated(a,b,"thea_GlossyRoughnessTrFilename")
                )

Mat.thea_GlossyStructureAnisotropy = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Anisotropy (%)",
                description="Anisotropy (%)",
                update=materialUpdated)

Mat.thea_GlossyStructureRotation = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Rotation (deg)",
                description="Rotation (deg)",
                update=materialUpdated)

Mat.thea_GlossyStructureBump = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=100.0,
                name="Bump (%)",
                description="Bump (%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_GlossySigmaFilename = bpy.props.StringProperty(
                  name = "Sigma texture",
                  default = "",
                  description = "Sigma texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_GlossySigmaFilename")
                  )

Mat.thea_GlossyRoughnessFilename = bpy.props.StringProperty(
                  name = "Roughness texture",
                  default = "",
                  description = "Roughness texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_GlossyRoughnessFilename")
                  )

Mat.thea_GlossyAnisotropyFilename = bpy.props.StringProperty(
                  name = "Anisotropy texture",
                  default = "",
                  description = "Anisotropy texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_GlossyAnisotropyFilename")
                  )

Mat.thea_GlossyRotationFilename = bpy.props.StringProperty(
                  name = "Rotation texture",
                  default = "",
                  description = "Rotation texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_GlossyRotationFilename")
                  )

Mat.thea_GlossyBumpFilename = bpy.props.StringProperty(
                  name = "Bump texture",
                  default = "",
                  description = "Bump texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_GlossyBumpFilename")
                  )

Mat.thea_GlossyStructureNormal = bpy.props.BoolProperty(
                name="Normal mapping",
                description="Enable normal mapping",
                default= False,
                update=materialUpdated)

Mat.thea_GlossyMicroRoughness = bpy.props.BoolProperty(
                name="Micro Roughness",
                description="Enable MicroRoughness",
                default= False,
                update=materialUpdated)

Mat.thea_GlossyMicroRoughnessWidth = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=2,
                default=10.0,
                name="Width (um)",
                description="Width (um)",
                update=materialUpdated)

Mat.thea_GlossyMicroRoughnessHeight = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=3,
                default=0.25,
                name="Height (um)",
                description="Height (um)",
                update=materialUpdated)

Mat.thea_GlossyReflectionCurve = bpy.props.BoolProperty(
                name="Custom Reflection Curve",
                description="Enable custom reflecion curve",
                default= False,
                update=lambda a,b: CustomCurveUpdate(a,b,"thea_GlossyReflectCurve"))

Mat.thea_GlossyReflectCurve = bpy.props.StringProperty(
                name = "Custom Curve",
                default = "",
                description = "Custom Curve")

Mat.thea_GlossyReflectCurveList = bpy.props.StringProperty(
                name = "Custom Curve List",
                default = "",
                description = "Custom Curve List")



Mat.thea_Glossy2 = bpy.props.BoolProperty(
                name="Glossy2",
                description="Enable Glossy2 material component",
                default= False,
                update=materialUpdated)

Mat.thea_Glossy2Order = bpy.props.IntProperty(
                min=0,
                max=10,
                default=0,
                name="Order",
                description="Order",
                update=materialUpdated)

Mat.thea_Glossy2Weight = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=100.0,
                name="Layer Weight",
                description="Layer Weight",
                update=materialUpdated)

Mat.thea_Glossy2WeightFilename = bpy.props.StringProperty(
                  name = "Weight texture",
                  default = "",
                  description = "Weight texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Glossy2WeightFilename")
                  )

Mat.thea_Glossy2ReflectanceCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                default=(1, 1, 1),
                name="Reflectance",
                description="Reflectance Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_Glossy2ReflectanceFilename = bpy.props.StringProperty(
                  name = "Reflectance texture",
                  default = "",
                  description = "Reflectance texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Glossy2ReflectanceFilename")
                  )

Mat.thea_Glossy2Reflect90Col = bpy.props.FloatVectorProperty(
                min=0, max=1,
                default=(1, 1, 1),
                name="Reflectance 90",
                description="Reflectance 90 Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_Glossy2Reflect90Filename = bpy.props.StringProperty(
                  name = "Reflectance 90 texture",
                  default = "",
                  description = "Reflectance 90 texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Glossy2Reflect90Filename")
                  )

Mat.thea_Glossy2TransmittanceCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Transmittance",
                description="Transmittance Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_Glossy2TransmittanceFilename = bpy.props.StringProperty(
                  name = "Transmittance texture",
                  default = "",
                  description = "Transmittance texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Glossy2TransmittanceFilename")
                  )

Mat.thea_Glossy2AbsorptionCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Absorption",
                description="Absorption Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_Glossy2Absorption = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=2,
                default=0.0,
                name="Absorption",
                description="Absorption",
                update=materialUpdated)

Mat.thea_Glossy2IOR = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=3,
                default=1.5,
                name="Index of Refraction (n)",
                description="Index of Refraction (n)",
                update=materialUpdated)

Mat.thea_Glossy2EC = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=3,
                default=0.0,
                name="Extinction Coefficient (k)",
                description="Extinction Coefficient (k)",
                update=materialUpdated)

Mat.thea_Glossy2AbbeNumberEnable = bpy.props.BoolProperty(
                name="Abbe",
                description="Abbe",
                default= False,
                update=materialUpdated)

Mat.thea_Glossy2AbbeNumber = bpy.props.FloatProperty(
                min=0,
                max=200,
                precision=3,
                default=50.0,
                name="Number",
                description="Number",
                update=materialUpdated)

Mat.thea_Glossy2IORFileEnable = bpy.props.BoolProperty(
                name="IOR file",
                description="IOR file",
                default= False,
                update=materialUpdated)

Mat.thea_Glossy2IORMenu = bpy.props.EnumProperty(
                items=getTheaIORMenuItems(),
                name="File",
                description="File",
                update=materialUpdated)

Mat.thea_Glossy2TraceReflections = bpy.props.BoolProperty(
                name="Trace Reflections",
                description="Trace Reflections",
                default= True,
                update=materialUpdated)

Mat.thea_Glossy2TraceRefractions = bpy.props.BoolProperty(
                name="Trace Refractions",
                description="Trace Refractions",
                default= True,
                update=materialUpdated)

Mat.thea_Glossy2StructureRoughness = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Roughness (%)",
                description="Roughness (%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_Glossy2StructureRoughTrEn = bpy.props.BoolProperty(
                name="Roughness Tr (%)",
                description="Roughness Tr (%)",
                default= False,
                update=materialUpdated)


Mat.thea_Glossy2StructureRoughnessTr = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=10.0,
                name="(%)",
                description="(%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_Glossy2RoughnessTrFilename = bpy.props.StringProperty(
                name = "Glossy 2 Roughness TR Texture",
                default = "",
                description = "Glossy 2 Roughness Tr file path",
                subtype = 'FILE_PATH',
                update=lambda a,b: materialFilenameUpdated(a,b,"thea_Glossy2RoughnessTrFilename")
                )

Mat.thea_Glossy2StructureAnisotropy = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Anisotropy (%)",
                description="Anisotropy (%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_Glossy2StructureRotation = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Rotation (deg)",
                description="Rotation (deg)",
                update=materialUpdated)

Mat.thea_Glossy2StructureBump = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=100.0,
                name="Bump (%)",
                description="Bump (%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_Glossy2SigmaFilename = bpy.props.StringProperty(
                  name = "Sigma texture",
                  default = "",
                  description = "Sigma texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Glossy2SigmaFilename")
                  )

Mat.thea_Glossy2RoughnessFilename = bpy.props.StringProperty(
                  name = "Roughness texture",
                  default = "",
                  description = "Roughness texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Glossy2RoughnessFilename")
                  )

Mat.thea_Glossy2AnisotropyFilename = bpy.props.StringProperty(
                  name = "Anisotropy texture",
                  default = "",
                  description = "Anisotropy texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Glossy2AnisotropyFilename")
                  )

Mat.thea_Glossy2RotationFilename = bpy.props.StringProperty(
                  name = "Rotation texture",
                  default = "",
                  description = "Rotation texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Glossy2RotationFilename")
                  )

Mat.thea_Glossy2BumpFilename = bpy.props.StringProperty(
                  name = "Bump texture",
                  default = "",
                  description = "Bump texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_Glossy2BumpFilename")
                  )

Mat.thea_Glossy2StructureNormal = bpy.props.BoolProperty(
                name="Normal mapping",
                description="Enable normal mapping",
                default= False,
                update=materialUpdated)

Mat.thea_Glossy2MicroRoughness = bpy.props.BoolProperty(
                name="Micro Roughness",
                description="Enable MicroRoughness",
                default= False,
                update=materialUpdated)

Mat.thea_Glossy2MicroRoughnessWidth = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=2,
                default=10.0,
                name="Width (um)",
                description="Width (um)",
                update=materialUpdated)

Mat.thea_Glossy2MicroRoughnessHeight = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=3,
                default=0.25,
                name="Height (um)",
                description="Height (um)",
                update=materialUpdated)

Mat.thea_Glossy2ReflectionCurve = bpy.props.BoolProperty(
                name="Custom Reflection Curve",
                description="Enable custom reflecion curve",
                default= False,
                update=lambda a,b: CustomCurveUpdate(a,b,"thea_Glossy2ReflectCurve"))

Mat.thea_Glossy2ReflectCurve = bpy.props.StringProperty(
                name = "Custom Curve",
                default = "",
                description = "Custom Curve")

Mat.thea_Glossy2ReflectCurveList = bpy.props.StringProperty(
                name = "Custom Curve List",
                default = "",
                description = "Custom Curve List")


Mat.thea_Displacement = bpy.props.BoolProperty(
                name="Displacement",
                description="Displacement",
                default= False,
                update=materialUpdated)

Mat.thea_DisplacementFilename = bpy.props.StringProperty(
                  name = "Displacement texture",
                  default = "",
                  description = "Displacement texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_DisplacementFilename")
                  )

Mat.thea_DispSub = bpy.props.IntProperty(
                min=0,
                max=100,
                default=2,
                name="Subdivision",
                description="Subdivision",
                update=materialUpdated)

Mat.thea_DispBump = bpy.props.IntProperty(
                min=0,
                max=100,
                default=0,
                name="Micro-Bump",
                description="Micro-Bump",
                update=materialUpdated)

Mat.thea_DisplacementHeight = bpy.props.FloatProperty(
                min=0,
                max=10000,
                precision=2,
                default=2,
                name="Height (cm)",
                description="Height (cm)",
                update=materialUpdated)

Mat.thea_DisplacementCenter = bpy.props.FloatProperty(
                min=0,
                max=10,
                precision=2,
                default=0.5,
                name="Center",
                description="Center",
                update=materialUpdated)

Mat.thea_DisplacementNormalSmooth = bpy.props.BoolProperty(
                name="Normal Smoothing",
                description="Normal Smoothing",
                default= True,
                update=materialUpdated)

Mat.thea_DisplacementTightBounds = bpy.props.BoolProperty(
                name="Tight Bounds",
                description="Tight Bounds",
                default= True,
                update=materialUpdated)

Mat.thea_Clipping = bpy.props.BoolProperty(
                name="Clipping",
                description="Clipping",
                default= False,
                update=materialUpdated)

Mat.thea_ClippingFilename = bpy.props.StringProperty(
                  name = "Clipping texture",
                  default = "",
                  description = "Clipping texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_ClippingFilename")
                  )

Mat.thea_ClippingThreshold = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=50,
                name="Threshold (%)",
                description="Threshold (%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_ClippingSoft = bpy.props.BoolProperty(
                name="Soft",
                description="Soft",
                default= False,
                update=materialUpdated)

Mat.thea_ClippingAuto = bpy.props.BoolProperty(
                name="Auto clipping",
                description="Auto clipping, sets clipping for PNG with alpha automatically",
                default= False,
                update=materialUpdated)

Mat.thea_Emittance = bpy.props.BoolProperty(
                name="Emittance",
                description="Emittance",
                default= False,
                update=materialUpdated)

Mat.thea_EmittancePower = bpy.props.FloatProperty(
                min=0,
                max=1000000000,
                precision=3,

                default=100.0,
                name="Power",
                description="Power",
                update=materialUpdated)

Mat.thea_EmittanceEfficacy = bpy.props.FloatProperty(
                min=0,
                max=1000000000,
                precision=3,
                default=20.0,
                name="Efficacy (lm/W)",
                description="Efficacy (lm/W)",
                update=materialUpdated)

Mat.thea_EmittanceCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Color",
                default=(1,1,1),
                description="Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_EmittanceFilename = bpy.props.StringProperty(
                  name = "Emittance texture",
                  default = "",
                  description = "Emittance texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_EmittanceFilename")
                  )

Mat.thea_EmittanceIES = bpy.props.BoolProperty(
                name="IES File",
                description="IES File",
                default= False,
                update=materialUpdated)

Mat.thea_EmittanceIESFilename = bpy.props.StringProperty(
                  name = "IES File",
                  default = "",
                  description = "IES file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_EmittanceFilename")
                  )

Mat.thea_EmittanceIESMultiplier = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=3,
                default=1,
                name="Multiplier",
                description="Multiplier",
                update=materialUpdated)

Mat.thea_EmittanceUnit = bpy.props.EnumProperty(
                items=(("Lumens","Lumens","Lumens"),("lm/m2","lm/m2","lm/m2"),("Candelas","Candelas","Candelas"),("cd/m2","cd/m2","cd/m2"),("Watts","Watts","Watts"),("W/m2","W/m2","W/m2"),("W/sr","W/sr","W/sr"),("W/sr/m2","W/sr/m2","W/sr/m2"),("W/nm","W/nm","W/nm"),("W/nm/m2","W/nm/m2","W/nm/m2"),("W/nm/sr","W/nm/sr","W/nm/sr"),("W/nm/sr/m2","W/nm/sr/m2","W/nm/sr/m2")),
                name="Unit",
                description="Unit",
                default="Watts",
                update=materialUpdated)


Mat.thea_EmittancePassiveEmitter = bpy.props.BoolProperty(
                name="Passive Emitter",
                description="Passive Emitter",
                default= False,
                update=materialUpdated)

Mat.thea_EmittanceAmbientEmitter = bpy.props.BoolProperty(
                name="Ambient Emitter",
                description="Ambient Emitter",
                default= False,
                update=materialUpdated)

Mat.thea_EmittanceAmbientLevel = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=3,
                default=100.0,
                name="Level",
                description="Level",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_extMat = bpy.props.StringProperty(
                       maxlen=500,
                       default="",
                       name="Thea material file",
                       description="Thea material file",
                       subtype='FILE_PATH',
                update=materialUpdated)

Mat.thea_Medium = bpy.props.BoolProperty(
                name="Medium",
                description="Medium",
                default= False,
                update=materialUpdated)


Mat.thea_MediumAbsorptionCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Absorption Color",
                default=(1,1,1),
                description="Color",
                subtype="COLOR",
                update=materialUpdated)

Tex.thea_MediumAbsorptionTex = bpy.props.BoolProperty(
                name="Absorption Texture",
                description="Absorption Texture",
                default= False,
                update=materialUpdated)

Mat.thea_MediumAbsorptionFilename = bpy.props.StringProperty(
                  name = "Absorption texture",
                  default = "",
                  description = "Absorption texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_MediumAbsorptionFilename")
                  )

Mat.thea_MediumScatterCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Scatter Color",
                default=(1,1,1),
                description="Color",
                subtype="COLOR",
                update=materialUpdated)

Tex.thea_MediumScatterTex = bpy.props.BoolProperty(
                name="Scatter Texture",
                description="Scatter Texture",
                default= False,
                update=materialUpdated)

Mat.thea_MediumScatterFilename = bpy.props.StringProperty(
                  name = "Scatter texture",
                  default = "",
                  description = "Scatter texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_MediumScatterFilename")
                  )

Mat.thea_MediumAbsorptionDensity = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=3,
                default=1,
                name="Absorption Density",
                description="Absorption Density",
                update=materialUpdated)

Tex.thea_MediumAbsorptionDensityTex = bpy.props.BoolProperty(
                name="Absorption Density Texture",
                description="Absorption Density Texture",
                default= False,
                update=materialUpdated)

Mat.thea_MediumAbsorptionDensityFilename = bpy.props.StringProperty(
                  name = "Absorption Density texture",
                  default = "",
                  description = "Absorption Density texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_MediumAbsorptionDensityFilename")
                  )

Mat.thea_MediumScatterDensity = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=3,
                default=1,
                name="Scatter Density",
                description="Scatter Density",
                update=materialUpdated)

Tex.thea_MediumScatterDensityTex = bpy.props.BoolProperty(
                name="Scatter Density Texture",
                description="Scatter Density Texture",
                default= False,
                update=materialUpdated)

Mat.thea_MediumScatterDensityFilename = bpy.props.StringProperty(
                  name = "Scatter Density texture",
                  default = "",
                  description = "Scatter Density texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_MediumScatterDensityFilename")
                  )

Mat.thea_MediumCoefficient = bpy.props.BoolProperty(
                name="Coefficient",
                description="Coefficient",
                default= False,
                update=materialUpdated)

Mat.thea_MediumMenu = bpy.props.EnumProperty(
                items=getTheaMediumMenuItems(),
                name="File",
                description="File",
                update=materialUpdated)

Mat.thea_MediumPhaseFunction = bpy.props.EnumProperty(
                items=(("Isotropic","Isotropic","Isotropic"),("Rayleigh","Rayleigh","Rayleigh"),("Mie Hazy","Mie Hazy","Mie Hazy"), ("Mie Murky", "Mie Murky", "Mie Murky"), ("Mie Retro", "Mie Retro", "Mie Retro"), ("Henyey Greenstein", "Henyey Greenstein", "Henyey Greenstein")),
                name="Phase Function",
                description="Phase Function",
                default="Isotropic",
                update=materialUpdated)

Mat.thea_Asymetry = bpy.props.FloatProperty(
                min=-1,
                max=1,
                precision=3,
                default=0.0,
                name="Asymetry",
                description="Asymetry",
                update=worldUpdated)

Tex.thea_Basic = bpy.props.BoolProperty(
                name="Basic",
                description="Use with Basic component",
                default= False)

Tex.thea_Basic2 = bpy.props.BoolProperty(
                name="Basic2",
                description="Use with second Basic component",
                default= False)

Tex.thea_Glossy = bpy.props.BoolProperty(
                name="Glossy",
                description="Use with Glossy component",
                default= False)

Tex.thea_Coating = bpy.props.BoolProperty(
                name="Coating",
                description="Use with coating component",
                default= False)

Tex.thea_ThinFilm = bpy.props.BoolProperty(
                name="Thin Film",
                description="Use with ThinFilm component",
                default= False)

Tex.thea_SSS = bpy.props.BoolProperty(
                name="SSS",
                description="Use with SSS component",
                default= False)

Tex.thea_Clipping = bpy.props.BoolProperty(
                name="Clipping",
                description="Use with Clipping component",
                default= False)

Tex.thea_Medium = bpy.props.BoolProperty(
                name="Medium",
                description="Use with Medium component",
                default= False)

Tex.thea_Emittance = bpy.props.BoolProperty(
                name="Emittance",
                description="Use with Emittance component",
                default= False)

#def updateToneMenu(self, context):
#    from TheaForBlender.thea_operators import callToneMenu
#    callToneMenu()
#    bpy.ops.wm.call_tonemenu(origin="thea_BasicDiffuseFilename")
#    layout.operator("wm.call_tonemenu", text= "", icon='SETTINGS')#.origin ='thea_'+label+"WeightFilename"

Tex.thea_mappingtoneMenu = bpy.props.EnumProperty(
                items=(('Mapping', 'Mapping', 'Mapping'),('Tone', 'Tone', 'Tone')),
                name="Mapping - Tone Menu",
                description="Choose to edit: texture mapping / toning")#,
#                update=updateToneMenu)

#CHANGED> Added better coordinates input
Tex.thea_texture_coords = bpy.props.EnumProperty(
                items=(('UV', 'UV', 'UV'),('Cubic', 'Cubic', 'Cubic'),('Cylindrical', 'Cylindrical', 'Cylindrical'),('Spherical', 'Spherical', 'Spherical'),('Flat', 'Flat', 'Flat'),('Front', 'Front', 'Front'),('Camera Map', 'Camera Map', 'Camera Map'),('Shrink Wrap', 'Shrink Wrap', 'Shrink Wrap'),('Cubic (Centered)', 'Cubic (Centered)', 'Cubic (Centered)'),('Flat (Centered)', 'Flat (Centered)', 'Flat (Centered)')),
                name="",
                description="Select method for mapping textures",
                default="UV",
                update=materialUpdated)

#CHANGED> Added Camera mapping
Tex.thea_camMapName = bpy.props.StringProperty(
                name="",
                description="FIle in camera name. Use IR view for active IR viewport test",
                default= "",
                update=materialUpdated)


Tex.thea_TexUVChannel = bpy.props.EnumProperty(
                items=(('0', '0', '0'),('1', '1', '1'),('2', '2', '2'),('3', '3', '3'),('4', '4', '4'),('5', '5', '5'),('6', '6', '6'),('7', '7', '7')),
                name="UV Channel",
                description="UV Channel",
                default="0",
                update=materialUpdated)

Tex.thea_TexInvert = bpy.props.BoolProperty(
                name="Invert",
                description="Invert",
                default= False,
                update=materialUpdated)

Tex.thea_TexGamma = bpy.props.FloatProperty(
                min=-100,
                max=100,
                precision=2,
                default=0,
                name="Gamma",
                description="Gamma",
                update=materialUpdated)

Tex.thea_TexRed = bpy.props.FloatProperty(
                min=-100,
                max=100,
                precision=2,
                default=0,
                name="Red",
                description="Red",
                update=materialUpdated)

Tex.thea_TexGreen = bpy.props.FloatProperty(
                min=-100,
                max=100,
                precision=2,
                default=0,
                name="Green",
                description="Green",
                update=materialUpdated)

Tex.thea_TexBlue = bpy.props.FloatProperty(
                min=-100,
                max=100,
                precision=2,
                default=0,
                name="Blue",
                description="Blue",
                update=materialUpdated)

Tex.thea_TexSaturation = bpy.props.FloatProperty(
                min=-100,
                max=100,
                precision=2,
                default=0,
                name="Saturation",
                description="Saturation",
                update=materialUpdated)

Tex.thea_TexBrightness = bpy.props.FloatProperty(
                min=-100,
                max=100,
                precision=2,
                default=0,
                name="Brightness",
                description="Brightness",
                update=materialUpdated)

Tex.thea_TexContrast = bpy.props.FloatProperty(
                min=-100,
                max=100,
                precision=2,
                default=0,
                name="Contrast",
                description="Contrast",
                update=materialUpdated)

Tex.thea_TexClampMin = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0,
                name="Clamp Min %",
                description="Clamp Min %",
                update=materialUpdated)

Tex.thea_TexClampMax = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=100,
                name="Clamp Max %",
                description="Clamp Max %",
                update=materialUpdated)

Tex.thea_TexRotation = bpy.props.FloatProperty(
                min=-10000,
                max=10000,
                precision=2,
                default=0,
                name="Rotation",
                description="Rotation",
                update=materialUpdated)
#CHANGED> Added repeat
Tex.thea_TexRepeat = bpy.props.BoolProperty(
                name="Repeat",
                description="Set texture to repeat or not",
                default= True,
                update=materialUpdated)

Tex.thea_TexSpatialXtex = bpy.props.FloatProperty(
                min=-1000,
                max=1000,
                precision=3,
                default=1,
                name="Spatial X",
                description="Spatial Size is used to correctly account for scaling when changing from UV to Cubic coordinates, while UV Scaling affects the scaling once UV projection is used.",
                update=materialUpdated)

Tex.thea_TexSpatialYtex = bpy.props.FloatProperty(
                min=-1000,
                max=1000,
                precision=3,
                default=1,
                name="Spatial Y",
                description="Spatial Size is used to correctly account for scaling when changing from UV to Cubic coordinates, while UV Scaling affects the scaling once UV projection is used.",
                update=materialUpdated)

Tex.thea_TexScaleXtex = bpy.props.BoolProperty(
#                thea_TexScaleXtex= mat.blenderMat.texture_slots.scale,
                name="Scale X",
                description="Scale X",
                update=materialUpdated)

Tex.thea_StructureSigmaTex = bpy.props.BoolProperty(
                name="Sigma Texture",
                description="Sigma Texture",
                default= False,
                update=materialUpdated)

Tex.thea_StructureAnisotropyTex = bpy.props.BoolProperty(
                name="Anisotropy Texture",
                description="Anisotropy Texture",
                default= False,
                update=materialUpdated)

Tex.thea_StructureRotationTex = bpy.props.BoolProperty(
                name="Rotation Texture",
                description="Rotation Texture",
                default= False,
                update=materialUpdated)

Tex.thea_TransmittanceTex = bpy.props.BoolProperty(
                name="Transmittance Texture",
                description="Transmittance Texture",
                default= False,
                update=materialUpdated)

Tex.thea_RoughnessTrTex = bpy.props.BoolProperty(
                name="Roughness Tr Texture",
                description="Rougness Tr Texture",
                default= False,
                update=materialUpdated)

Tex.thea_TexChannel = bpy.props.EnumProperty(
                items=(('RGB', 'RGB', 'RGB'),('Alpha', 'Alpha', 'Alpha')),
                name="Channel",
                description="Channel",
                default="RGB",
                update=materialUpdated)
#CHANGED> Added coating anis and rotation
Tex.thea_CoatingStructureAnisotropyTex = bpy.props.BoolProperty(
                name="Anisotropy Texture",
                description="Anisotropy Texture",
                default= False,
                update=materialUpdated)

Tex.thea_CoatingStructureRotationTex = bpy.props.BoolProperty(
                name="Rotation Texture",
                description="Rotation Texture",
                default= False,
                update=materialUpdated)

Mat.thea_Coating = bpy.props.BoolProperty(
                name="Coating",
                description="Enable Coating material component",
                default= False,
                update=materialUpdated)

Mat.thea_CoatingWeight = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=100.0,
                name="Layer Weight",
                description="Layer Weight",
                update=materialUpdated)

Mat.thea_CoatingWeightFilename = bpy.props.StringProperty(
                  name = "Weight texture",
                  default = "",
                  description = "Weight texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_CoatingWeightFilename")
                  )

Mat.thea_CoatingReflectanceCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                default=(1, 1, 1),
                name="Reflectance",
                description="Reflectance Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_CoatingReflectanceFilename = bpy.props.StringProperty(
                  name = "Reflectance texture",
                  default = "",
                  description = "Reflectance texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_CoatingReflectanceFilename")
                  )

Mat.thea_CoatingReflect90Col = bpy.props.FloatVectorProperty(
                min=0, max=1,
                default=(1, 1, 1),
                name="Reflectance 90",
                description="Reflectance 90 Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_CoatingReflect90Filename = bpy.props.StringProperty(
                  name = "Reflectance 90 texture",
                  default = "",
                  description = "Reflectance 90 texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_CoatingReflect90Filename")
                  )

Mat.thea_CoatingIOR = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=3,
                default=1.5,
                name="Index of Refraction (n)",
                description="Index of Refraction (n)",
                update=materialUpdated)

Mat.thea_CoatingEC = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=3,
                default=0.0,
                name="Extinction Coefficient (k)",
                description="Extinction Coefficient (k)",
                update=materialUpdated)

Mat.thea_CoatingThicknessEnable = bpy.props.BoolProperty(
                name="Thickness (um)",
                description="Thickness (um)",
                default= False,
                update=materialUpdated)

Mat.thea_CoatingThickness = bpy.props.FloatProperty(
                min=0,
                max=20000,
                precision=3,
                default=100.0,
                name="Number",
                description="Number",
                update=materialUpdated)

Mat.thea_CoatingThicknessFilename = bpy.props.StringProperty(
                  name = "Thickness texture",
                  default = "",
                  description = "Thickness texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_CoatingThicknessFilename")
                  )

Tex.thea_CoatingThicknessTex = bpy.props.BoolProperty(
                name="Thickness Texture",
                description="Thickness Texture",
                default= False,
                update=materialUpdated)
#CHANGED > Added below 5 items for thickness absorption color / texture
#I dont know how to set default value of color to be empty, thats why i added enable for absorption color. Else it would add black as default which is not good.
Mat.thea_CoatingAbsorptionEnable = bpy.props.BoolProperty(
                name="Absorption Color",
                description="Absorption Color",
                default= False,
                update=materialUpdated)

Mat.thea_CoatingThicknessAbsorptionCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
#                default=("", "", ""),
                name="Absorption",
                description="Absorption Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_CoatingAbsorptionFilename = bpy.props.StringProperty(
                  name = "Absorption texture",
                  default = "",
                  description = "Absorption texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_CoatingAbsorptionFilename")
                  )

Tex.thea_CoatingAbsorptionTex = bpy.props.BoolProperty(
                name="Absorption Texture",
                description="Absorption Texture",
                default= False,
                update=materialUpdated)

Mat.thea_CoatingTraceReflections = bpy.props.BoolProperty(
                name="Trace Reflections",
                description="Trace Reflections",
                default= True,
                update=materialUpdated)

Mat.thea_CoatingStructureRoughness = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Roughness (%)",
                description="Roughness (%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_CoatingStructureAnisotropy = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Anisotropy (%)",
                description="Anisotropy (%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_CoatingStructureRotation = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Rotation (deg)",
                description="Rotation (deg)")

Mat.thea_CoatingStructureBump = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=100.0,
                name="Bump (%)",
                description="Bump (%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_CoatingStructureNormal = bpy.props.BoolProperty(
                name="Normal mapping",
                description="Enable normal mapping",
                default= False,
                update=materialUpdated)

Mat.thea_CoatingRoughnessFilename = bpy.props.StringProperty(
                  name = "Roughness texture",
                  default = "",
                  description = "Roughness texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_CoatingRoughnessFilename")
                  )

Mat.thea_CoatingAnisotropyFilename = bpy.props.StringProperty(
                  name = "Anisotropy texture",
                  default = "",
                  description = "Anisotropy texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_CoatingAnisotropyFilename")
                  )

Mat.thea_CoatingRotationFilename = bpy.props.StringProperty(
                  name = "Rotation texture",
                  default = "",
                  description = "Rotation texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_CoatingRotationFilename")
                  )

Mat.thea_CoatingBumpFilename = bpy.props.StringProperty(
                  name = "Bump texture",
                  default = "",
                  description = "Bump texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_CoatingBumpFilename")
                  )

Mat.thea_CoatingMicroRoughness = bpy.props.BoolProperty(
                name="Micro Roughness",
                description="Enable MicroRoughness",
                default= False,
                update=materialUpdated)

Mat.thea_CoatingMicroRoughnessWidth = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=2,
                default=10.0,
                name="Width (um)",
                description="Width (um)",
                update=materialUpdated)

Mat.thea_CoatingMicroRoughnessHeight = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=3,
                default=0.25,
                name="Height (um)",
                description="Height (um)",
                update=materialUpdated)

Mat.thea_CoatingReflectionCurve = bpy.props.BoolProperty(
                name="Custom Reflection Curve",
                description="Enable custom reflecion curve",
                default= False,
                update=lambda a,b: CustomCurveUpdate(a,b,"thea_CoatingReflectCurve"))

Mat.thea_CoatingReflectCurve = bpy.props.StringProperty(
                name = "Custom Curve",
                default = "",
                description = "Custom Curve")

Mat.thea_CoatingReflectCurveList = bpy.props.StringProperty(
                name = "Custom Curve List",
                default = "",
                description = "Custom Curve List")



Mat.thea_SSS = bpy.props.BoolProperty(
                name="SSS",
                description="Enable SSS material component",
                default= False,
                update=materialUpdated)

Mat.thea_SSSOrder = bpy.props.IntProperty(
                min=0,
                max=10,
                default=0,
                name="Order",
                description="Order",
                update=materialUpdated)

Mat.thea_SSSWeight = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=100.0,
                name="Layer Weight",
                description="Layer Weight",
                update=materialUpdated)

Mat.thea_SSSWeightFilename = bpy.props.StringProperty(
                  name = "Weight texture",
                  default = "",
                  description = "Weight texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_SSSWeightFilename")
                  )

Mat.thea_SSSReflectanceCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                default=(1, 1, 1),
                name="Reflectance",
                description="Reflectance Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_SSSReflectanceFilename = bpy.props.StringProperty(
                  name = "Reflectance texture",
                  default = "",
                  description = "Reflectance texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_SSSReflectanceFilename")
                  )

Mat.thea_SSSReflect90Col = bpy.props.FloatVectorProperty(
                min=0, max=1,
                default=(1, 1, 1),
                name="Reflectance 90",
                description="Reflectance 90 Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_SSSReflect90Filename = bpy.props.StringProperty(
                  name = "Reflectance 90 texture",
                  default = "",
                  description = "Reflectance 90 texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_SSSReflect90Filename")
                  )

Mat.thea_SSSAbsorptionCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Absorption",
                description="Absorption Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_SSSAbsorption = bpy.props.FloatProperty(
                min=0,
                max=10000,
                precision=2,
                default=100,
                name="Absorption",
                description="Absorption",
                update=materialUpdated)

Mat.thea_SSSScatteringCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                name="Scattering",
                description="Scattering Color",
                subtype="COLOR",
                update=materialUpdated)

Mat.thea_SSSScattering = bpy.props.FloatProperty(
                min=0,
                max=100000,
                precision=2,
                default=100.0,
                name="Scattering",
                description="Scattering",
                update=materialUpdated)

Mat.thea_SSSAsymetry = bpy.props.FloatProperty(
                min=0,
                max=1,
                precision=3,
                default=0.0,
                name="Asymetry",
                description="Asymetry",
                update=materialUpdated)

Mat.thea_SSSIOR = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=3,
                default=1.3,
                name="Index of Refraction (n)",
                description="Index of Refraction (n)",
                update=materialUpdated)

Mat.thea_SSSTraceReflections = bpy.props.BoolProperty(
                name="Trace Reflections",
                description="Trace Reflections",
                default= True,
                update=materialUpdated)

Mat.thea_SSSTraceRefractions = bpy.props.BoolProperty(
                name="Trace Refractions",
                description="Trace Refractions",
                default= True,
                update=materialUpdated)

Mat.thea_SSSStructureRoughness = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Roughness (%)",
                description="Roughness (%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_SSSStructureRoughTrEn = bpy.props.BoolProperty(
                name="Roughness Tr (%)",
                description="Roughness Tr (%)",
                default= False,
                update=materialUpdated)


Mat.thea_SSSStructureRoughnessTr = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=10.0,
                name="(%)",
                description="(%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_SSSRoughnessTrFilename = bpy.props.StringProperty(
                name = "SSS Roughness TR Texture",
                default = "",
                description = "SSS Roughness Tr file path",
                subtype = 'FILE_PATH',
                update=lambda a,b: materialFilenameUpdated(a,b,"thea_SSSRoughnessTrFilename")
                )

Mat.thea_SSSStructureAnisotropy = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Anisotropy (%)",
                description="Anisotropy (%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_SSSStructureRotation = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=0.0,
                name="Rotation (deg)",
                description="Rotation (deg)",
                update=materialUpdated)

Mat.thea_SSSStructureBump = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=100.0,
                name="Bump (%)",
                description="Bump (%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_SSSBumpFilename = bpy.props.StringProperty(
                  name = "Bump texture",
                  default = "",
                  description = "Bump texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_SSSBumpFilename")
                  )


Mat.thea_SSSRoughnessFilename = bpy.props.StringProperty(
                  name = "Roughness texture",
                  default = "",
                  description = "Roughness texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_SSSRoughnessFilename")
                  )

Mat.thea_SSSAnisotropyFilename = bpy.props.StringProperty(
                  name = "Anisotropy texture",
                  default = "",
                  description = "Anisotropy texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_SSSAnisotropyFilename")
                  )

Mat.thea_SSSRotationFilename = bpy.props.StringProperty(
                  name = "Rotation texture",
                  default = "",
                  description = "Rotation texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_SSSRotationFilename")
                  )

Mat.thea_SSSStructureNormal = bpy.props.BoolProperty(
                name="Normal mapping",
                description="Enable normal mapping",
                default= False,
                update=materialUpdated)

Mat.thea_SSSMicroRoughness = bpy.props.BoolProperty(
                name="Micro Roughness",
                description="Enable MicroRoughness",
                default= False,
                update=materialUpdated)

Mat.thea_SSSMicroRoughnessWidth = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=2,
                default=10.0,
                name="Width (um)",
                description="Width (um)",
                update=materialUpdated)

Mat.thea_SSSMicroRoughnessHeight = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=3,
                default=0.25,
                name="Height (um)",
                description="Height (um)",
                update=materialUpdated)

Mat.thea_SSSReflectionCurve = bpy.props.BoolProperty(
                name="Custom Reflection Curve",
                description="Enable custom reflecion curve",
                default= False,
                update=lambda a,b: CustomCurveUpdate(a,b,"thea_SSSReflectCurve"))

Mat.thea_SSSReflectCurve = bpy.props.StringProperty(
                name = "Custom Curve",
                default = "",
                description = "Custom Curve")

Mat.thea_SSSReflectCurveList = bpy.props.StringProperty(
                name = "Custom Curve List",
                default = "",
                description = "Custom Curve List")



Mat.thea_ThinFilm = bpy.props.BoolProperty(
                name="ThinFilm Component",
                description="Enable ThinFilm material component",
                default= False,
                update=materialUpdated)

Mat.thea_ThinFilmOrder = bpy.props.IntProperty(
                min=0,
                max=10,
                default=0,
                name="Order",
                description="Order",
                update=materialUpdated)

Mat.thea_ThinFilmWeight = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=100.0,
                name="Layer Weight",
                description="Layer Weight",
                update=materialUpdated)

Mat.thea_ThinFilmWeightFilename = bpy.props.StringProperty(
                  name = "Weight texture",
                  default = "",
                  description = "Weight texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: materialFilenameUpdated(a,b,"thea_ThinFilmWeightFilename")
                  )
#CHANGED > Default color wasnt set
Mat.thea_ThinFilmTransmittanceCol = bpy.props.FloatVectorProperty(
                min=0, max=1,
                default=(1, 1, 1),
                name="Transmittance",
                description="Transmittance Color",
                subtype="COLOR",
                update=materialUpdated)

#CHANGED > Added texture option
Mat.thea_ThinFilmTransmittanceFilename = bpy.props.StringProperty(
                name = "Transmittance texture",
                default = "",
                description = "Transmittance texture file path",
                subtype = 'FILE_PATH',
                update=lambda a,b: materialFilenameUpdated(a,b,"thea_ThinFilmTransmittanceFilename")
                )

Tex.thea_ThinFilmTransmittanceTex = bpy.props.BoolProperty(
                name="Transmittance Texture",
                description="Transmittance Texture",
                default= False,
                update=materialUpdated)

Mat.thea_ThinFilmIOR = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=3,
                default=1.5,
                name="Index of Refraction (n)",
                description="Index of Refraction (n)",
                update=materialUpdated)

Mat.thea_ThinFilmInterference = bpy.props.BoolProperty(
                name="Interference",
                description="Interference",
                default= False,
                update=materialUpdated)

Mat.thea_ThinFilmThickness = bpy.props.FloatProperty(
                min=0,
                max=20000,
                precision=3,
                default=500.0,
                name="Thickness (nm)",
                description="Thickness (nm)",
                update=materialUpdated)
#CHANEGD > added thickness file
Mat.thea_ThinFilmThicknessFilename = bpy.props.StringProperty(
                name = "Thickness texture",
                default = "",
                description = "Thickness texture file path",
                subtype = 'FILE_PATH',
                update=lambda a,b: materialFilenameUpdated(a,b,"thea_ThinFilmThicknessFilename")
                )

Tex.thea_ThinFilmThicknessTex = bpy.props.BoolProperty(
                name="Thickness Texture",
                description="Thickness Texture",
                default= False,
                update=materialUpdated)

Mat.thea_ThinFilmStructureBump = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=2,
                default=100.0,
                name="Bump (%)",
                description="Bump (%)",
                subtype='PERCENTAGE',
                update=materialUpdated)

Mat.thea_ThinFilmBumpFilename = bpy.props.StringProperty(
                name = "Bump texture",
                default = "",
                description = "Bump texture file path",
                subtype = 'FILE_PATH',
                update=lambda a,b: materialFilenameUpdated(a,b,"thea_ThinFilmBumpFilename")
                )

Mat.thea_ThinFilmStructureNormal = bpy.props.BoolProperty(
                name="Normal mapping",
                description="Enable normal mapping",
                default= False,
                update=materialUpdated)

Mat.thea_StrandRoot = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=3,
                default=0.01,
                name="Root [m]",
                description="Strand root size[m]",
                update=materialUpdated)

Mat.thea_StrandTip = bpy.props.FloatProperty(
                min=0,
                max=100,
                precision=3,
                default=0.001,
                name="Tip [m]",
                description="Strand tip size [m]",
                update=materialUpdated)

Mat.thea_FastHairExport = bpy.props.BoolProperty(
                name="Fast export",
                description="Enable fast hair export, but no UV mapping",
                default= False,
                update=materialUpdated)

Mat.thea_ColoredHair = bpy.props.BoolProperty(
                name="Colored Hair",
                description="Enable colored hair",
                default= False,
                update=materialUpdated)


Obj.aperture = bpy.props.FloatProperty(
                min=0,
#               CHANGED > to lower max setting and better precision
                max=100,
                precision=2,
                default=5.6,
                name="f-number",
                description="Focal lenght/lens diameter, the higher the sharper the image")
#,update=cameraUpdated)
#CHANGED> Added DOF distance %
Obj.thea_enableDOFpercentage = bpy.props.BoolProperty(
                name="Depth of Field (%)",
                description="Describes the relative space that stays sharp in the image",
                default= False)

Obj.thea_DOFpercentage = bpy.props.FloatProperty(
                min=0,
#               CHANGED > to lower max setting and better precision
                max=100,
                precision=1,
                default=20,
                name="DOF (%)",
                description="Describes the relative space that stays sharp in the image")

#CHANGED> Added distance (= double bu makes more logic here)
Obj.dof_distance = bpy.props.FloatProperty(
                min=0,
#               CHANGED > to lower max setting and better precision
                max=10000,
                precision=4,
                default=0,
                name="Distance",
                description="Distance to the focal point for depth of field")

Obj.shutter_speed = bpy.props.FloatProperty(
                min=0,
                max=1000000,
                precision=0,
                default=500,
                name="Shutter speed",
                description="Shutter speed (1/s), the inverse of exposure, counted in fr/s")

Obj.autofocus = bpy.props.BoolProperty(
                name="Autofocus",
                description="Autofocus",
                default= True)

Obj.thea_pinhole = bpy.props.BoolProperty(
                name="Pinhole",
                description="Pinhole",
                default= True)

Obj.thea_zClippingNearDistance = bpy.props.FloatProperty(
                min=0,
                max=10000,
                precision=2,
                default=1,
                name="Z-Clipping Near Distance",
                description="Z-Clipping Near Distance")

Obj.thea_zClippingFarDistance = bpy.props.FloatProperty(
                min=0,
                max=10000,
                precision=2,
                default=1000,
                name="Z-Clipping Far Distance",
                description="Z-Clipping Far Distance")

Obj.thea_zClippingNear = bpy.props.BoolProperty(
                name="Z-Clipping Near",
                description="Z-Clipping Near",
                default= False)

Obj.thea_zClippingFar = bpy.props.BoolProperty(
                name="Z-Clipping Far",
                description="Z-Clipping Far",
                default= False)

#      CHANGED > Z-Clip from DOF
Obj.thea_ZclipDOF = bpy.props.BoolProperty(
                name="Use Camera DOF",
                description="Use camera DOF for Z-clipping Near",
                default= False)

Obj.thea_ZclipDOFmargin = bpy.props.FloatProperty(
                min=-10000,
                max=10000,
                precision=1,
                default=10,
                name="Falloff (m)",
                description="Use the fall as the min or max for Z-clipping Far")
#CHANGED > Removed label
Obj.thea_diaphragma = bpy.props.EnumProperty(
                items=(("Circular","Circular","Circular"),("Polygonal","Polygonal","Polygonal")),
                name="",
                description="The generic shape of the lens",
                default="Circular")

Obj.thea_diapBlades = bpy.props.IntProperty(
                min=0,
                max=100,
#                precision=2,
                default=6,
                name="Blades",
                description="The order of the polygon lens, normally 5-6")

Obj.thea_projection = bpy.props.EnumProperty(
                items=(("Perspective","Perspective","Perspective"),("Cylindrical","Cylindrical","Cylindrical"),("Spherical","Spherical", "Spherical"),("Parallel", "Parallel", "Parallel")),
                name="Projection",
                description="The generic lens projection on the film/image",
                default="Perspective")

Obj.thEnabled = bpy.props.BoolProperty(
                name="Enabled",
                description="Enable",
                default= True)

Obj.thExportAnimation = bpy.props.BoolProperty(
                name="Export Animation data of object",
                description="Export Animation data of object",
                default= False)

Obj.thShadowCaster = bpy.props.BoolProperty(
                name="Shadow Caster",
                description="Shadow Caster",
                default= True)

Obj.thVisible = bpy.props.BoolProperty(
                name="Visible",
                description="Visible",
                default= True)

Obj.thShadowTight = bpy.props.BoolProperty(
                name="Shadow Tight",
                description="Shadow Tight",
                default= True)

Obj.thShadowReceiver = bpy.props.BoolProperty(
                name="Shadow Receiver",
                description="Shadow Receiver",
                default= True)

Obj.thCausticsTransmitter = bpy.props.BoolProperty(
                name="Caustics Transmitter",
                description="Caustics Transmitter",
                default= True)

Obj.thCausticsReceiver = bpy.props.BoolProperty(
                name="Caustics Receiver",
                description="Caustics Receiver",
                default= True)

Obj.thNoRecalcNormals = bpy.props.BoolProperty(
                name="Don't recalculate Normals while exporting",
                description="Don't recalculate Normals while exporting",
                default= False)

Obj.thMaskID = bpy.props.BoolProperty(
                name="Mask Index",
                description="Mask Index",
                default= False)

Obj.thMaskIDindex = bpy.props.IntProperty(
                min=1,
                max=1000,
                default=1,
                name="Index",
                description="Index")

Obj.thSectionFrame = bpy.props.BoolProperty(
                name="Z-clipping Plane",
                description="Z-clipping plane let's you a plane for clipping the scene. Instead of using Camera Z-clipping. Only works when this is enabled on a plane",
                default= False)

items_store = []
def materialsList(scene, context):
    '''Return materials for object container

        :param context: context
        :return: list of tuples (mat.name, mat.name, mat.name)
        :rtpe: [(str, str, str)]
    '''

    items = []
    items.append(("None","None","None"))
    maxid = -1
    id = -1
    found = False
    if hasattr(bpy.data, "materials"):
        for mat in bpy.data.materials:
            for idrec in items_store:
                id = idrec[0]
                if id > maxid:
                    maxid = id
                if idrec[1] == mat.name:
                    found = True
                    break
            if not found:
                items_store.append((maxid+1, mat.name))
#            items.append((mat.name, mat.name, mat.name))
            items.append( (mat.name, mat.name,"", id) )
    return items

Obj.thea_Container = bpy.props.EnumProperty(
                 name="Materials List",
                 description="Materials List",
                 items=materialsList)

def updateLUT(self, context):
    '''Update thea_globals.useLUT, thea_globals.nameBasedLUT and save config when LUT property has changed
    '''
    thea_globals.useLUT = getattr(context.scene, 'thea_useLUT')
    thea_globals.nameBasedLUT = getattr(context.scene, 'thea_nameBasedLUT')
    thea_globals.setConfig()
    print("thea_globals.useLUT: ", thea_globals.useLUT)
    try:
        bpy.ops.thea.refresh_diffuse_color()
    except:
        pass

Scene.thea_useLUT = bpy.props.BoolProperty(
                name="Use LUT",
                description="Use LUT file",
                default= False,
                #default=thea_globals.getUseLUT(),
                update=updateLUT)

Scene.thea_nameBasedLUT = bpy.props.BoolProperty(
                name="Material name based LUT",
                description="Material name based LUT",
                default=False,
                #default= thea_globals.getNameBasedLUT(),
                update=updateLUT)

Scene.thea_overwriteLUT = bpy.props.BoolProperty(
                name="Overwrite LUT",
                description="Overwrite existing LUT file",
                default= False)

Scene.thea_LUTScanSubdirectories = bpy.props.BoolProperty(
                name="Scan subdirectories for material files",
                description="Scan subdirectories for material files",
                default= True)

Scene.thea_materialsPath = bpy.props.StringProperty(
                name="Thea materials path",
                description="Thea materials path",
                default= os.path.join(dataPath, "Materials"))

Scene.thea_lutMessage = bpy.props.StringProperty(
                maxlen=40,
                default=" ",
                name="LUT",
                description="LUT")

Scene.thea_SDKPort = bpy.props.IntProperty(
                min=10000,
                max=60000,
                default=30000,
                name="Port",
                description="Port")

Scene.thea_PreviewSDKPort = bpy.props.IntProperty(
                min=10000,
                max=60000,
                default=30001,
                name="Preview port",
                description="Preview port")

Scene.thea_RefreshDelay = bpy.props.FloatProperty(
                min=0.01,
                max=20,
                precision=1,
                default=0.1,
                name="Refresh delay",
                description="Refresh delay")

Scene.thea_StartTheaDelay = bpy.props.FloatProperty(
                min=0.2,
                max=5,
                precision=1,
                default=2,
                name="Delay after Thea start",
                description="Delay after Thea start")

Scene.thea_IRIdleTimeout = bpy.props.IntProperty(
                min=10,
                max=600,
                default=120,
                name="Idle timeout",
                description="How long to keep remote darkroom app running after rendering is finished")


Scene.thea_IRAlpha = bpy.props.FloatProperty(
                min=0.0,
                max=1,
                precision=1,
                default=1,
                name="IR preview alpha",
                description="IR preview alpha")

Scene.thea_IRMessage = bpy.props.StringProperty(
                  name = "Message",
                  default = "",
                  description = "IR Message",
                  )

Scene.thea_IRBlendAlpha = bpy.props.BoolProperty(
                name="Blend 3D view to IR ",
                description="Smooth blend 3D view to IR result after scene update.",
                default= True)

def IRFontSizeUpdated(self, context):
    '''Save IR font size section in config file when property is updated

        :param context: context
    '''
    font_size = getattr(context.scene, 'thea_IRFontSize', 12)
    config = configparser.ConfigParser()
    configPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.ini")
    config.read(configPath)
    if not config.has_section("main"):
        config.add_section('main')
    config.set('main', 'IRFontSize', str(font_size))
    with open(configPath, 'w') as configfile:
        config.write(configfile)

Scene.thea_IRFontSize = bpy.props.IntProperty(
                min=10,
                max=100,
                default=12,
                name="IR status font size",
                description="IR status font size. Change it in case of using HDPI screens",
                update=IRFontSizeUpdated)


def updateFullExportSelected(self, context):
    '''It does nothing right now
    '''
    return
#     if getattr(context.scene, 'thea_IRFullExportSelected', False):
#         context.scene.thea_Reuse = True

Scene.thea_IRFullExportSelected = bpy.props.BoolProperty(
                name="Always full export selected objects when starting IR",
                description="Always full export selected objects when starting IR",
                default= False,
                update=updateFullExportSelected)

Scene.thea_WasExported = bpy.props.BoolProperty(
                name="Has scene exported",
                description="Has scene exported",
                default= False)

updateTime = time.time()



def updateShowIR(self, context):
    '''Set correct valuse for  context.scene.thea_DrawPreviewto3dView, context.scene.thea_SavePreviewtoImage, context.scene.thea_IRShowTheaWindow

        :param context: context
    '''
    global updateTime
    if (time.time()-updateTime) > 1:
        updateTime = time.time()
#         port = getattr(context.scene, 'thea_SDKPort')
#         data = sendSocketMsg('localhost', port, b'version')
        if getattr(context.scene, 'thea_IRShowTheaWindow'):
            context.scene.thea_DrawPreviewto3dView = False
            context.scene.thea_SavePreviewtoImage = False
            context.scene.thea_IRShowTheaWindow = True
#             if data.find('v'):
#                 message = b'message "./UI/Show" '
#                 data = sendSocketMsg('localhost', port, message)
        else:
            context.scene.thea_DrawPreviewto3dView = True
            context.scene.thea_SavePreviewtoImage = True
            context.scene.thea_IRShowTheaWindow = False
    updateTime = time.time()





def updateDrawIR(self, context):
    ''' Set context.scene.thea_IRShowTheaWindow = False and context.scene.thea_SavePreviewtoImage = True properties when draw IR propert has changed
    '''
    global updateTime
    if (time.time()-updateTime) > 1:
        updateTime = time.time()
#         port = getattr(context.scene, 'thea_SDKPort')
#         data = sendSocketMsg('localhost', port, b'version')
        if getattr(context.scene, 'thea_DrawPreviewto3dView'):
            context.scene.thea_IRShowTheaWindow = False
#             context.scene.thea_DrawPreviewto3dView = True
            context.scene.thea_SavePreviewtoImage = True
#             if data.find('v'):
#                 message = b'message "./UI/Hide"'
#                 data = sendSocketMsg('localhost', port, message)
#         else:
#             context.scene.thea_IRShowTheaWindow = True
#             context.scene.thea_DrawPreviewto3dView = False
            #context.scene.thea_SavePreviewtoImage = False
    updateTime = time.time()

def updateSaveIR(self, context):
    '''It does nothing currently
    '''
    global updateTime
#     if (time.time()-updateTime) > 1:
#         updateTime = time.time()
#         port = getattr(context.scene, 'thea_SDKPort')
#         data = sendSocketMsg('localhost', port, b'version')
#         if getattr(context.scene, 'thea_SavePreviewtoImage'):
#             context.scene.thea_IRShowTheaWindow = False
#             if data.find('v'):
#                 message = b'message "./UI/Hide"'
#                 data = sendSocketMsg('localhost', port, message)
#         else:
#             context.scene.thea_IRShowTheaWindow = True
#             context.scene.thea_SavePreviewtoImage = False
#             context.scene.thea_DrawPreviewto3dView = False
    updateTime = time.time()

def updateRemapIRKeys(self, context):
    '''Set thea_globals.remapIRKeys and save confing when key mapping property is changed
    '''
    if getattr(context.scene, 'thea_IRRemapIRKeys', False):
        thea_globals.remapIRKeys = True
    else:
        thea_globals.remapIRKeys = False
    thea_globals.setConfig()



Scene.thea_IRShowTheaWindow = bpy.props.BoolProperty(
                name="Show IR window",
                description="Show separate window with IR result",
                default= False,
                update=updateShowIR)

Scene.thea_DrawPreviewto3dView = bpy.props.BoolProperty(
                name="Draw to 3D view",
                description="Draw IR preview to 3dView",
                default= True,
                update=updateDrawIR)

Scene.thea_Fit3dView = bpy.props.BoolProperty(
                name="Fit image in 3D view",
                description="Fit image in 3D view",
                default= True,
                update=updateDrawIR)

Scene.thea_SavePreviewtoImage = bpy.props.BoolProperty(
                name="Save IR result to image",
                description="Save IR to image so it can be displayed as ir.bmp in Image Editor window or displayed in 3D view",
                default= True,
                update=updateSaveIR)

Scene.thea_IRFullUpdate = bpy.props.BoolProperty(
                name="Full Auto refresh",
                description="Do full scene refresh after any update ((may take long to export)",
                default= False)

Scene.thea_IRExportAnimation = bpy.props.BoolProperty(
                name="Export Animation data of objects",
                description="Export Animation data of objects",
                default= False)

Scene.thea_IRDevice = bpy.props.EnumProperty(
                items=(("GPU+CPU","GPU+CPU","GPU+CPU"),("GPU","GPU","GPU"),("CPU","CPU","CPU")),
                name="Device Mask",
                description="Device Mask",
                default="GPU+CPU")

#Scene.thea_cpuDevice = bpy.props.EnumProperty(
#                items=(("Lowest","Lowest","Lowest"),("Lower","Lower","Lower"),("Low","Low","Low"),("Normal","Normal","Normal"),("High","High","High")),
#                name="CPU",
#                description="CPU",
#                default="Low")
#
#Scene.thea_cpuThreadsEnable = bpy.props.BoolProperty(
#                name="CPU Threads",
#                description="CPU Threads",
#                default= True)
#
#Scene.thea_cpuThreads = bpy.props.EnumProperty(
#                items=(("Auto","Auto","Auto"),("MAX","MAX","MAX"),("Max-1","Max-1","Max-1"),("Max-2","Max-2","Max-2"),("Max-GPUs","Max-GPUs","Max-GPUs"),("Max-GPUs-1","Max-GPUs-1","Max-GPUs-1"),("Max-GPUs-2","Max-GPUs-2","Max-GPUs-2"),("1","1","1"),("2","2","2"),("4","4","4"),("8","8","8")),
#                name="CPU Threads",
#                description="CPU Threads",
#                default="MAX")


Scene.thea_IRResolution = bpy.props.EnumProperty(
                items=(("Full 3D view size", "Full 3D view size", "Full 3D view size"),("Half size", "Half size", "Half size"),("Quarter size", "Quarter size", "Quarter size")),
                name="Render resulution",
                description="Resoultion of IR render",
                default="Half size")

Scene.thea_IRAdvancedSettings = bpy.props.BoolProperty(
                name="Advanced",
                description="Advanced",
                default= False)

Scene.thea_IRAdvancedIR = bpy.props.BoolProperty(
                name="AdvancedIR",
                description="Advanced IR Control",
                default= False)

Scene.thea_IRRemapIRKeys = bpy.props.BoolProperty(
                name="Use F11&F12 keys for IR",
                description="Use F11&F12 keys for IR",
                default= thea_globals.getRemapIRKeys(),
                update=updateRemapIRKeys)


Scene.thea_ir_running = bpy.props.BoolProperty(default=False)
Scene.thea_ir_update = bpy.props.BoolProperty(default=False)
Scene.thea_lastIRUpdate = bpy.props.IntProperty()

Part.thea_ApplyModifier = bpy.props.BoolProperty(
                name="Apply modifier before export",
                description="Apply modifier before export",
                default= False)

def materialComponentChanged(self, context):
    '''It does nothing currently
    '''

    mat = context.material
#    mat.thea_MaterialComponent.items=getMaterialComponents()
#     if mat.thea_MaterialComponent == "Basic":
#         mat.thea_Basic = True
#         mat.thea_Glossy = False
#         mat.thea_SSS = False
#         mat.thea_ThinFilm = False
#     if mat.thea_MaterialComponent == "Glossy":
#         mat.thea_Basic = False
#         mat.thea_Glossy = True
#         mat.thea_SSS = False
#         mat.thea_ThinFilm = False
#     if mat.thea_MaterialComponent == "SSS":
#         mat.thea_Basic = False
#         mat.thea_Glossy = False
#         mat.thea_SSS = True
#         mat.thea_ThinFilm = False
#     if mat.thea_MaterialComponent == "ThinFilm":
#         mat.thea_Basic = False
#         mat.thea_Glossy = False
#         mat.thea_SSS = False
#         mat.thea_ThinFilm = True

def getMaterialComponents(self, context):
    '''Return component list menu entries

        :param context: context
        :return: list of tuples (component, component, component, icon, i)
        :rtype: [(str, str, str, str, int)]
    '''
    components = ("Basic", "Basic2", "Glossy", "Glossy2",  "SSS", "ThinFilm")
    items = []
    i=0
    for component in components:
        #icon="RADIOBUT_OFF"
        icon="RADIOBUT_OFF" #"CHECKBOX_DEHLT"
        if hasattr(bpy.context, 'active_object'):
            if getattr(bpy.context.active_object.active_material, "thea_"+component):
                #icon="RADIOBUT_ON"
                icon="RADIOBUT_ON"# "CHECKBOX_HLT"
        items.append((component, component, component, icon, i))
        i+=1
    return items

Mat.thea_MaterialComponent = bpy.props.EnumProperty(
                #items=(("Basic","Basic","Basic", "RADIOBUT_OFF", 0),("Basic2","Basic2","Basic2", "RADIOBUT_OFF", 0),("Glossy","Glossy","Glossy", "RADIOBUT_OFF", 0),("Glossy2","Glossy2","Glossy2", "RADIOBUT_OFF", 0),("SSS","SSS","SSS", "RADIOBUT_OFF", 0),("ThinFilm","ThinFilm","ThinFilm", "RADIOBUT_OFF", 0)),
                items=getMaterialComponents,
                name="Material",
                description="Material",
                #default="Basic",
                update=materialComponentChanged)



Scene.thea_showTools = bpy.props.BoolProperty(
                name="Show",
                description="Show",
                default= False)

Scene.thea_showSetup = bpy.props.BoolProperty(
                name="Show",
                description="Show",
                default= False)

Scene.thea_showRemoteSetup = bpy.props.BoolProperty(
                name="Show",
                description="Show",
                default= False)

Scene.thea_showMerge = bpy.props.BoolProperty(
                name="Show",
                description="Show",
                default= False)

Scene.thea_showChannels = bpy.props.BoolProperty(
                name="Show",
                description="Show",
                default= False)

Scene.thea_enablePresets = bpy.props.BoolProperty(
                name="Enable",
                description="Enable",
                default= False)

def lampUpdated(self, context):
    '''Set thea_globals.lampUpdated = True when lamp property is updated
    '''
    thea_globals.lampUpdated = True

def lampFilenameUpdated(self, context, origin=""):
    '''Create texture and set it when one of the lamp filename properties are updated

        :param context: context
        :param origin: filename parameter which has been updated
        :type origin: string
    '''
    imgName = context.lamp.get(origin)
    texName = "LAMP_"+origin
    lamp = context.lamp
    print("lampFilenameUpdated: ",self, context, origin, context.lamp.get(origin))
    exists = False
    try:
        if lamp.texture_slots[texName]:
            exists = True
            slot = lamp.texture_slots[texName]
            tex = slot.texture
    except:
        pass

    if exists:
        try:
            if imgName:
                img = bpy.data.images.load(imgName)
                tex.image = img
            else:
                print("removing texture: ", slot, tex)
                lamp.texture_slots[texName].texture = None
        except:
            pass
    else:
        img = bpy.data.images.load(imgName)
        tex = bpy.data.textures.new(name=texName, type='IMAGE')
        tex.image = img
        tex.name = texName
        slot = lamp.texture_slots.add()
        slot.texture = tex
        update=lampUpdated(context)

Lamp.thea_EmittancePower = bpy.props.EnumProperty(
                items=(("Lumens","Lumens","Lumens"),("Candelas","Candelas","Candelas"),("Watts","Watts","Watts"),("W/sr","W/sr","W/sr"),("W/nm","W/nm","W/nm"),("W/nm/sr","W/nm/sr","W/nm/sr")),
                name="Unit",
                description="Unit",
                default="Watts",
                update=lampUpdated)

Lamp.thea_EmittancePower = bpy.props.FloatProperty(
                min=0,
                max=1000000000,
                precision=3,
#    CHANGED DEFAULT to 1
                default=1.0,
                name="Power",
                description="Power",
                update=lampUpdated)

Lamp.thea_EmittanceEfficacy = bpy.props.FloatProperty(
                min=0,
                max=1000000000,
                precision=3,
                default=20.0,
                name="Efficacy (lm/W)",
                description="Efficacy (lm/W)",
                update=lampUpdated)

Lamp.thea_SunAttenuation = bpy.props.EnumProperty(
                items=(("Inverse Square","Inverse Square","Inverse Square"),("Inverse","Inverse","Inverse"),("None","None","None")),
                name="Attenuation",
                description="Attenuation",
                default="None",
                update=lampUpdated)

Lamp.thea_EmittanceAttenuation = bpy.props.EnumProperty(
                items=(("Inverse Square","Inverse Square","Inverse Square"),("Inverse","Inverse","Inverse"),("None","None","None")),
                name="Attenuation",
                description="Attenuation",
                default="Inverse Square",
                update=lampUpdated)

Lamp.thea_SunEmittanceUnit = bpy.props.EnumProperty(
                items=(("Lumens","Lumens","Lumens"),("lm/m2","lm/m2","lm/m2"),("Candelas","Candelas","Candelas"),("cd/m2","cd/m2","cd/m2"),("Watts","Watts","Watts"),("W/m2","W/m2","W/m2"),("W/sr","W/sr","W/sr"),("W/sr/m2","W/sr/m2","W/sr/m2"),("W/nm","W/nm","W/nm"),("W/nm/m2","W/nm/m2","W/nm/m2"),("W/nm/sr","W/nm/sr","W/nm/sr"),("W/nm/sr/m2","W/nm/sr/m2","W/nm/sr/m2")),
                name="Unit",
                description="Unit",
                default="W/nm/sr",
                update=lampUpdated)

Lamp.thea_TextureFilename = bpy.props.StringProperty(
                  name = "Lamp Texture",
                  default = "",
                  description = "Lamp texture file path",
                  subtype = 'FILE_PATH',
                  update=lambda a,b: lampFilenameUpdated(a,b,"thea_TextureFilename")
                  )

#CHANGED > Added IES checkbox
Lamp.thea_enableIES = bpy.props.BoolProperty(
                name="Enable IES",
                description="Enable IES",
                default= False,
                update=lampUpdated)

Lamp.thea_IESFilename = bpy.props.StringProperty(
                  name = "IES file",
                  default = "",
                  description = "IES file path",
                  subtype = 'FILE_PATH',
                  update=lampUpdated)

Lamp.thea_IESMultiplier = bpy.props.FloatProperty(
                min=0,
                max=1000,
                precision=3,
                default=1.0,
                name="Multiplier",
                description="Multiplier IES Strength",
                update=lampUpdated)

#CHANGED > Added Projector checkbox
Lamp.thea_enableProjector = bpy.props.BoolProperty(
                name="Enable Projector",
                description="Enable Projector",
                default= False,
                update=lampUpdated)

Lamp.thea_ProjectorFilename = bpy.props.StringProperty(
                  name = "IES file",
                  default = "",
                  description = "IES file path",
                  subtype = 'FILE_PATH',
                  update=lampUpdated)

Lamp.thea_ProjectorWidth = bpy.props.FloatProperty(
                min=0,
                max=100000,
                precision=3,
                default=1.0,
                name="Width",
                description="Projector Width",
                update=lampUpdated)

Lamp.thea_ProjectorHeight = bpy.props.FloatProperty(
                min=0,
                max=100000,
                precision=3,
                default=1.0,
                name="Height",
                description="Projector Height",
                update=lampUpdated)

Lamp.thea_enableLamp = bpy.props.BoolProperty(
                name="Enable",
                description="Enable",
                default= True,
                update=lampUpdated)

Lamp.thea_enableShadow = bpy.props.BoolProperty(
                name="Shadow",
                description="Shadow",
                default= True,
                update=lampUpdated)
#            CHANGED > Added manual sun
Lamp.thea_manualSun = bpy.props.BoolProperty(
                name="Manual Sun",
                description="Manual Sun",
                default= False,
                update=lampUpdated)

Lamp.thea_enableSoftShadow = bpy.props.BoolProperty(
                name="Soft Shadow (m)",
                description="Enables Soft Shadow, Soft radius size (m). Use low numbers, this represents bulb size",
                default= True,
                update=lampUpdated)

Lamp.thea_softRadius = bpy.props.FloatProperty(
                min=0,
                max=100000,
                precision=3,
                default=0.050,
                name="",
                description="Soft radius size (m). Use low numbers, this represents bulb size",
                update=lampUpdated)

Lamp.thea_radiusMultiplier = bpy.props.FloatProperty(
                min=0,
                max=100000,
                precision=3,
                default=1,
                name="",
                description="Radius Multiplier",
                update=lampUpdated)

Lamp.thea_minRays = bpy.props.IntProperty(
                min=0,
                max=1000,
                default=8,
                name="Min Rays",
                description="Min Rays",
                update=lampUpdated)

Lamp.thea_maxRays = bpy.props.IntProperty(
                min=0,
                max=1000,
                default=100,
                name="Max Rays",
                description="Max Rays",
                update=lampUpdated)

Lamp.thea_globalPhotons = bpy.props.BoolProperty(
                name="Global photons",
                description="Global photons",
                default= True,
                update=lampUpdated)

Lamp.thea_causticPhotons = bpy.props.BoolProperty(
                name="Caustic photons",
                description="Caustic photons",
                default= True,
                update=lampUpdated)

Lamp.thea_bufferIndex = bpy.props.IntProperty(
                min=0,
                max=1000,
                default=0,
                name="Light Buffer Index",
                description="Light Buffer Index",
                update=lampUpdated)

Lamp.thea_EmittanceUnit = bpy.props.EnumProperty(
                items=(("Lumens","Lumens","Lumens"),("Candelas","Candelas","Candelas"),("Watts","Watts","Watts"),("W/sr","W/sr","W/sr"),("W/nm","W/nm","W/nm"),("W/nm/sr","W/nm/sr","W/nm/sr")),
                name="Unit",
                description="Unit",
                default="Watts",
                update=lampUpdated)

Lamp.thea_EmittanceEfficacy = bpy.props.FloatProperty(
                min=0,
                max=1000000000,
                precision=3,
                default=20.0,
                name="Efficacy (lm/W)",
                description="Efficacy (lm/W)",
                update=lampUpdated)


def logLevelUpdated(self, context):
    '''Set log level
    '''
    print("logLevelUpdated: ", getattr(bpy.context.scene, 'thea_LogLevel'))
    import logging


    if getattr(bpy.context.scene, 'thea_LogLevel') == "Debug":
        thea_globals.log.setLevel(logging.DEBUG)
        thea_globals.fh.setLevel(logging.DEBUG)
    else:
        thea_globals.log.setLevel(logging.INFO)
        thea_globals.fh.setLevel(logging.INFO)



Scene.thea_LogLevel = bpy.props.EnumProperty(
                items=(("Debug","Debug","Debug"),("Basic","Basic","Basic")),
                name="Log level",
                description="Log level",
                default="Basic",
                update=logLevelUpdated)


