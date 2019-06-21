#=============================================================================
# This source file is part of the Blender to Irrlicht Exporter (irrb)
# url: http://code.google.com/p/tubras/wiki/irrb
#
# This is free and unencumbered software released into the public domain.
# For the full text of the Unlicense, see the file "docs/unlicense.html".
# Additional Unlicense information may be found at http://unlicense.org.
#=============================================================================
bl_info = {
    'name': 'Irrlicht format',
    'description': 'Export Irrlicht Scene/Mesh Data (.irr/.irrmesh)',
    'author': 'Keith Murray (pc0de)',
    'version': (0, 6),
    'blender': (2, 6, 0),
    'api': 39685,
    'location': 'File > Import-Export',
    'warning': '',
    'wiki_url': 'http://code.google.com/p/tubras/wiki/irrb',
    'tracker_url' : '',
    "category": "Learnbgame",
}

import bpy
from bpy.props import *
import os
import mathutils
import math
import sys
import time
import subprocess
import shutil
import struct
import math
import copy
import configparser
import platform
import zipfile
import glob
import collections

# Notes:
#
# Coordinate Systems
# http://www.euclideanspace.com/maths/geometry/space/coordinates/index.htm
#
# Irrlicht uses a left-handed coordinate system:
#       +y up
#       +z away from the viewer
#       xyz -> rotation order
#
# If you rotate around Y, +Z into the viewer, +X points left.
#
#           +Y  +Z
#            |  /
#            | /
#            |/
#  -X--------0--------+X
#           /|
#          / |
#         /  |
#       -Z  -Y
#     Left Handed
#
# Blender uses a right-handed coordinate system:
#       +y up
#       +z into the viewer
#       ??? rotation order is controlled by the user
#
#           +Y  -Z                 +Z  +Y
#            |  /                   |  /
#            | /                    | /
#            |/                     |/
#  -X--------0--------+X  -X--------0---------+X
#           /|                     /|
#          / |                    / |
#         /  |                   /  |
#       +Z  -Y                 -Y  -Z
#     Right Handed        Blender 3d View rotates +Z up
#
#  Object Translation, Coordinate, & Scale Conversion:
#       irrlicht x,y,z = blender x,z,y
#
#
# http://www.gamedev.net/community/forums/topic.asp?topic_id=479892
# First, the rotation order is indeed YXZ (yes!). Second, the input matrix is
# in right-handed, row-major format (see "3D Computer Graphics" by Alan Watts
# (pp. 4 & 5)). Most other sources use a column-major format so the rotation
# extraction routines (Eberly) needed to consider the transposition of matrix
# elements. Third, instead of negating the z rotation, obviously :sarcasm:
# you have to negate the x and y rotations. Finally, the matrix determinant
# is then needed to negate these in the opposite direction (a positive
# determinant, multiply by -1, a negative determinant, multiply by 1).
#
# http://msdn.microsoft.com/en-us/library/bb204853%28VS.85%29.aspx
# Flip the order of triangle vertices so that the system traverses them
# clockwise from the front. In other words, if the vertices are v0, v1, v2,
# pass them to Direct3D as v0, v2, v1. Use the view matrix to scale world
# space by -1 in the z-direction. To do this, flip the sign of the _31, _32,
# _33, and _34 member of the D3DMATRIX structure that you use for your view
# matrix.
#
# http://www.geometrictools.com/Documentation/LeftHandedToRightHanded.pdf
# Also contains info on left->right.
#

gVersionList = (0, '1.6', '1.7')
gIrrlichtVersion = 2
sVersionList = '1.6 %x1|1.7 %x2'
gMeshCvtPath = None
gWalkTestPath = None
gWalkTestPath32 = None
gWalkTestPath64 = None
gHaveWalkTest = 'IWALKTEST' in os.environ
gUserConfig = os.path.expanduser('~') + os.sep + '.irrb'
gPlatform = platform.system()
gConfig = None

gWTCmdLine = ''
gWTDirectory = ''
gWTConfigParm = ''
gWTConfigParmGen = ''

iversion = '{}.{}'.format(bl_info['version'][0],
                            bl_info['version'][1])
_logFile = None

_StartMessages = []

# node types
NT_DEFAULT = 0
NT_BILLBOARD = 1
NT_SKYBOX = 2
NT_SKYDOME = 3
NT_VOLUMETRICLIGHT = 4
NT_WATERSURFACE = 5
NT_CUSTOM = 6

# property material types
EMT_SOLID = 0
EMT_SOLID_2_LAYER = 1
EMT_LIGHTMAP = 2
EMT_LIGHTMAP_ADD = 3
EMT_LIGHTMAP_M2 = 4
EMT_LIGHTMAP_M4 = 5
EMT_LIGHTMAP_LIGHTING = 6
EMT_LIGHTMAP_LIGHTING_M2 = 7
EMT_LIGHTMAP_LIGHTING_M4 = 8
EMT_DETAIL_MAP = 9
EMT_SPHERE_MAP = 10
EMT_REFLECTION_2_LAYER = 11
EMT_TRANSPARENT_ADD_COLOR = 12
EMT_TRANSPARENT_ALPHA_CHANNEL = 13
EMT_TRANSPARENT_ALPHA_CHANNEL_REF = 14
EMT_TRANSPARENT_VERTEX_ALPHA = 15
EMT_TRANSPARENT_REFLECTION_2_LAYER = 16
EMT_NORMAL_MAP_SOLID = 17
EMT_NORMAL_MAP_TRANSPARENT_ADD_COLOR = 18
EMT_NORMAL_MAP_TRANSPARENT_VERTEX_ALPHA = 19
EMT_PARALLAX_MAP_SOLID = 20
EMT_PARALLAX_MAP_TRANSPARENT_ADD_COLOR = 21
EMT_PARALLAX_MAP_TRANSPARENT_VERTEX_ALPHA = 22
EMT_ONETEXTURE_BLEND = 23
EMT_CUSTOM = 24

# hardware mapping hints
EHM_NEVER = 0
EHM_STATIC = 1
EHM_DYNAMIC = 2
EHM_STREAM = 3

EBT_NONE = 0
EBT_VERTEX = 1
EBT_INDEX = 2
EBT_VERTEX_AND_INDEX = 3

RAD2DEG = 180.0 / math.pi
DEG2RAD = math.pi / 180.0
EVT_STANDARD = 0
EVT_2TCOORDS = 1
EVT_TANGENTS = 2

E_COMPARISON_FUNC = {
    'ECFN_NEVER': 0,
    'ECFN_LESSEQUAL': 1,
    'ECFN_EQUAL': 2,
    'ECFN_LESS': 3,
    'ECFN_NOTEQUAL': 4,
    'ECFN_GREATEREQUAL': 5,
    'ECFN_GREATER': 6,
    'ECFN_ALWAYS': 7,
}

E_ANTI_ALIASING_MODE = {
    'EAAM_OFF': 0,
    'EAAM_SIMPLE': 1,
    'EAAM_QUALITY': 3,
    'EAAM_LINE_SMOOTH': 4,
    'EAAM_POINT_SMOOTH': 8,
    'EAAM_FULL_BASIC': 15,
    'EAAM_ALPHA_TO_COVERAGE': 16,
}

E_TEXTURE_CLAMP = {
    'ETC_REPEAT': 'texture_clamp_repeat',
    'ETC_CLAMP': 'texture_clamp_clamp',
    'ETC_CLAMP_TO_EDGE': 'texture_clamp_clamp_to_edge',
    'ETC_CLAMP_TO_BORDER': 'texture_clamp_clamp_to_border',
    'ETC_MIRROR': 'texture_clamp_mirror',
    'ETC_MIRROR_CLAMP': 'texture_clamp_mirror_clamp',
    'ETC_MIRROR_CLAMP_TO_EDGE': 'texture_clamp_mirror_clamp_to_edge',
    'ETC_MIRROR_CLAMP_TO_BORDER': 'texture_clamp_mirror_clamp_to_border',
}

irrBodyTypes = {
    'NO_COLLISION': 'none',
    'STATIC': 'static',
    'DYNAMIC': 'dynamic',
    'RIGID_BODY': 'rigid',
    'SOFT_BODY': 'soft',
    'OCCLUDE': 'occlude',
    'SENSOR': 'sensor',
}

# (blender prop enum, irr material name, expected texture count)
irrMaterialTypes = (
    ('EMT_SOLID', 'solid', 1, EVT_STANDARD),
    ('EMT_SOLID_2_LAYER', 'solid_2layer', 2, EVT_2TCOORDS),
    ('EMT_LIGHTMAP', 'lightmap', 2, EVT_2TCOORDS),
    ('EMT_LIGHTMAP_ADD', 'lightmap_add', 2, EVT_2TCOORDS),
    ('EMT_LIGHTMAP_M2', 'lightmap_m2', 2, EVT_2TCOORDS),
    ('EMT_LIGHTMAP_M4', 'lightmap_m4', 2, EVT_2TCOORDS),
    ('EMT_LIGHTMAP_LIGHTING', 'lightmap_light', 2, EVT_2TCOORDS),
    ('EMT_LIGHTMAP_LIGHTING_M2', 'lightmap_light_m2', 2, EVT_2TCOORDS),
    ('EMT_LIGHTMAP_LIGHTING_M4', 'lightmap_light_m4', 2, EVT_2TCOORDS),
    ('EMT_DETAIL_MAP', 'detail_map', 2, EVT_2TCOORDS),
    ('EMT_SPHERE_MAP', 'sphere_map', 1, EVT_STANDARD),
    ('EMT_REFLECTION_2_LAYER', 'reflection_2layer', 2, EVT_2TCOORDS),
    ('EMT_TRANSPARENT_ADD_COLOR', 'trans_add', 1, EVT_STANDARD),
    ('EMT_TRANSPARENT_ALPHA_CHANNEL', 'trans_alphach', 1, EVT_STANDARD),
    ('EMT_TRANSPARENT_ALPHA_CHANNEL_REF', 'trans_alphach_ref', 1, EVT_STANDARD),
    ('EMT_TRANSPARENT_VERTEX_ALPHA', 'trans_vertex_alpha', 1, EVT_STANDARD),
    ('EMT_TRANSPARENT_REFLECTION_2_LAYER', 'trans_reflection_2layer',
        2, EVT_2TCOORDS),
    ('EMT_NORMAL_MAP_SOLID', 'normalmap_solid', 2, EVT_TANGENTS),
    ('EMT_NORMAL_MAP_TRANSPARENT_ADD_COLOR', 'normalmap_trans_add',
        2, EVT_TANGENTS),
    ('EMT_NORMAL_MAP_TRANSPARENT_VERTEX_ALPHA', 'normalmap_trans_vertexalpha',
        2, EVT_TANGENTS),
    ('EMT_PARALLAX_MAP_SOLID', 'parallaxmap_solid', 2, EVT_TANGENTS),
    ('EMT_PARALLAX_MAP_TRANSPARENT_ADD_COLOR', 'parallaxmap_trans_add',
        2, EVT_TANGENTS),
    ('EMT_PARALLAX_MAP_TRANSPARENT_VERTEX_ALPHA',
        'parallaxmap_trans_vertexalpha',
        2, EVT_TANGENTS),
    ('EMT_ONETEXTURE_BLEND', 'onetexture_blend', 1, EVT_STANDARD),
    ('EMT_CUSTOM', 'custom', 2, EVT_2TCOORDS),
)

# default configuration properties
_G = {
    'export': {
        'scene': True,
        'selected': False,
        'lights': True,
        'cameras': True,
        'animations': True,
        'physics': False,
        'pack': False,
        'makeexec': False,
        'binary': False,
        'use_blender_materials': False,
        'debug': True,
        'walktest': True,
        'out_directory': '',
        'mdl_directory': 'mdl',
        'tex_directory': 'tex',
        'scene_directory': '.',
        'copy_images': True,
    },
    'scene': {
        'OccludesLight': 0,
    },
    'standard': {
        'Id': -1,
        'AutomaticCulling': 1,
        'Visible': 1,
        'DebugDataVisible': 0,
        'IsDebugObject': 0,
        'ReadOnlyMaterials': 0,
    },
}

defSceneAttributes = {
    'Exporter': 'irrb',
    'Exporter.Version': iversion,
    'OccludesLight': 0,
    }

defMeshAttributes = {
    # iwalktest uses
    #'HWHint':'static',
    #'HWType':'vertexindex'
    }

defCameraAttributes = {
    'Fovy': 0.857556,
    'Aspect': 1.25,
    'ZNear': 0.1,
    'ZFar': 100.0,
    }

defLightAttributes = {
    'LightType': 'Point',
    'AmbientColor': '255 255 255 255',
    'SpecularColor': '255 255 255 255',
    'Attenuation': 10.0,
    'Radius': 50.0,
    'CastShadows': 1,
    }

defBillboardAttributes = {
    'Shade_Top': '255 255 255 255',
    'Shade_Down': '255 255 255 255',
    }

defMaterialAttributes = {
    'Type': 'solid',
    'AmbientColor': '255 255 255 255',  # rgba
    'DiffuseColor': '255 255 255 255',
    'EmissiveColor': '0 0 0 255',
    'SpecularColor': '255 255 255 255',
    'Shininess': 0.0,
    'MaterialTypeParam': 0.0,
    'MaterialTypeParam2': 0.0,
    'Thickness': 1.0,
    'WireFrame': 0,
    'PointCloud': 0,
    'Lighting': 0,
    'GouraudShading': 1,
    'ZWriteEnable': 1,
    'BackfaceCulling': 1,
    'FrontfaceCulling': 0,
    'FogEnable': 1,
    'NormalizeNormals': 0,
    'UseMipMaps': 1,
    'ZBuffer': 1,
    'AntiAliasing': 5,  # EAAM_SIMPLE | EAAM_LINE_SMOOTH,
    'ColorMask': 15,  # ECP_ALL
    'Layer1': {
        'Texture': '',
        'TextureWrap': 'texture_clamp_repeat',   # <= 1.6
        'TextureWrapU': 'texture_clamp_repeat',  # 1.7
        'TextureWrapV': 'texture_clamp_repeat',  # 1.7
        'BilinearFilter': 1,
        'TrilinearFilter': 0,
        'AnisotropicFilter': 0,
        'LODBias': 0,
        },
    'Layer2': {
        'Texture': '',
        'TextureWrap': 'texture_clamp_repeat',
        'TextureWrapU': 'texture_clamp_repeat',
        'TextureWrapV': 'texture_clamp_repeat',
        'BilinearFilter': 1,
        'TrilinearFilter': 0,
        'AnisotropicFilter': 0,
        'LODBias': 0,
        },
    'Layer3': {
        'Texture': '',
        'TextureWrap': 'texture_clamp_repeat',
        'TextureWrapU': 'texture_clamp_repeat',
        'TextureWrapV': 'texture_clamp_repeat',
        'BilinearFilter': 1,
        'TrilinearFilter': 0,
        'AnisotropicFilter': 0,
        'LODBias': 0,
        },
    'Layer4': {
        'Texture': '',
        'TextureWrap': 'texture_clamp_repeat',
        'TextureWrapU': 'texture_clamp_repeat',
        'TextureWrapV': 'texture_clamp_repeat',
        'BilinearFilter': 1,
        'TrilinearFilter': 0,
        'AnisotropicFilter': 0,
        'LODBias': 0,
        }
    }

gWTOptions =\
{
'oiDebug': 4,
'obConsole': 'false',
'obShowHelp': 'true',
'obShowDebug': 'true',
'ofVelocity': 4.0,
'ofAVelocity': 100.0,
'ofVelocityDamp': 0.0,
'osDriver': 'EDT_OPENGL',
'osResolution': 'medium',
'obKeepAspect': 'false',
'oiColorDepth': 32,
'obFullScreen': 'false',
'obVSync': 'true',
'obStencilBuffer': 'false',
'oiAntiAlias': 4,
'osPhysicsSystem': 'Irrlicht',
'osBroadphase': 'btDbvt',
'oiSubSteps': 1,
'oiTimeStep': 60,
'ofCharWidth': 1.0,
'ofCharHeight': 2.5,
'ofCharStepHeight': 0.35,
'ofCharJumpSpeed': 1.5,
}

gWTConfig = "\
EDT_NULL = 0\n\
EDT_SOFTWARE = 1\n\
EDT_BURNINGSVIDEO = 2\n\
EDT_DIRECT3D8 = 3\n\
EDT_DIRECT3D9 = 4\n\
EDT_OPENGL = 5\n\
options =\n\
{{\n\
    debug = {oiDebug},\n\
    console = {obConsole},\n\
    velocity = {ofVelocity},\n\
    angularvelocity = {ofAVelocity},\n\
    maxvertangle = 80,\n\
    velocitydamp = {ofVelocityDamp},\n\
    defcampos = {{0, 5, -50}},\n\
    defcamtarget = {{0, 0, 0}},\n\
    showHelpGUI = {obShowHelp},\n\
    showDebugGUI = {obShowDebug},\n\
}}\n\
video =\n\
{{\n\
    driver = {osDriver},\n\
    resolution = {osResolution},\n\
    keepaspect = {obKeepAspect},\n\
    colordepth = {oiColorDepth},\n\
    fullscreen = {obFullScreen},\n\
    vsync = {obVSync},\n\
    stencilbuffer = {obStencilBuffer},\n\
    antialias = {oiAntiAlias},\n\
    bgcolor = {{25,25,25,255}},\n\
    guiskin = 'gui/tubras.cfg',\n\
    hwcursor = false,\n\
    guicursor = false,\n\
    centercursor = true,\n\
    debugNormalLength = 1.0,\n\
    debugNormalColor = {{34, 221, 221, 255}},\n\
}}\n\
physics = \n\
{{\n\
    library = '{osPhysicsSystem}',\n\
    broadphase = {osBroadphase},\n\
    maxSubSteps = {oiSubSteps},\n\
    fixedTimeStep = {oiTimeStep},\n\
    characterWidth = {ofCharWidth},\n\
    characterHeight = {ofCharHeight},\n\
    characterStepHeight = {ofCharStepHeight},\n\
    characterJumpSpeed = {ofCharJumpSpeed},\n\
}}\n\
keybindings =\n\
{{\n\
    ['input.key.down.w'] = 'frwd 1',\n\
    ['input.key.up.w'] = 'frwd',\n\
    ['input.key.down.a'] = 'left 1',\n\
    ['input.key.up.a'] = 'left',\n\
    ['input.key.down.s'] = 'back 1',\n\
    ['input.key.up.s'] = 'back',\n\
    ['input.key.down.d'] = 'rght 1',\n\
    ['input.key.up.d'] = 'rght',\n\
    ['input.key.down.e'] = 'mvup 1',\n\
    ['input.key.up.e'] = 'mvup',\n\
    ['input.key.down.c'] = 'mvdn 1',\n\
    ['input.key.up.c'] = 'mvdn',\n\
    ['input.key.down.right'] = 'rotr 1',\n\
    ['input.key.up.right'] = 'rotr',\n\
    ['input.key.down.left'] = 'rotl 1',\n\
    ['input.key.up.left'] = 'rotl',\n\
    ['input.key.down.up'] = 'rotf 1',\n\
    ['input.key.up.up'] = 'rotf',\n\
    ['input.key.down.down'] = 'rotb 1',\n\
    ['input.key.up.down'] = 'rotb',\n\
    ['input.key.down.lshift'] = 'avel 3.5',\n\
    ['input.key.up.lshift'] = 'avel 1.0',\n\
    ['input.key.down.lcontrol'] = 'avel 0.1',\n\
    ['input.key.up.lcontrol'] = 'avel 1.0',\n\
    ['input.key.down.i'] =  'invert-mouse',\n\
    ['input.key.down.space'] = 'jump 1',\n\
    ['input.key.down.l'] =  'ldbg',\n\
    ['input.key.down.m'] =  'mdbg',\n\
    ['input.key.down.f1'] = 'help',\n\
    ['input.key.down.f2'] = 'idbg',\n\
    ['input.key.down.f3'] = 'wire',\n\
    ['input.key.down.f4'] = 'pdbg',\n\
    ['input.key.down.f5'] = 'cdbg',\n\
    ['input.key.down.f6'] = 'xfrm',\n\
    ['input.key.down.f7'] = 'tgod',\n\
    ['input.key.down.f8'] = 'tcon',\n\
    ['input.key.down.f9'] = 'tanm',\n\
    ['input.key.down.f10'] = 'tgui',\n\
    ['input.key.down.tab'] = 'ccam',\n\
    ['input.key.up.prtscr'] = 'sprt',\n\
    ['input.key.down.esc'] = 'quit',\n\
}}\n\
"
# dropped to {out dir}/default.cfg
gWTConfigGen = "\
[options]\n\
debug = {oiDebug}\n\
console = {obConsole}\n\
velocity = {ofVelocity}\n\
angularvelocity = {ofAVelocity}\n\
maxvertangle = 80\n\
velocitydamp = {ofVelocityDamp}\n\
defcampos = {{0, 5, -50}}\n\
defcamtarget = {{0, 0, 0}}\n\
showHelpGUI = {obShowHelp}\n\
showDebugGUI = {obShowDebug}\n\
\n\
[video]\n\
driver = {osDriver}\n\
resolution = {osResolution}\n\
keepaspect = {obKeepAspect}\n\
colordepth = {oiColorDepth}\n\
fullscreen = {obFullScreen}\n\
vsync = {obVSync}\n\
stencilbuffer = {obStencilBuffer}\n\
antialias = {oiAntiAlias}\n\
\n\
[physics]\n\
library = {osPhysicsSystem}\n\
broadphase = {osBroadphase}\n\
maxSubSteps = {oiSubSteps}\n\
fixedTimeStep = {oiTimeStep}\n\
characterWidth = {ofCharWidth}\n\
characterHeight = {ofCharHeight}\n\
characterStepHeight = {ofCharStepHeight}\n\
characterJumpSpeed = {ofCharJumpSpeed}\n\
"

#=============================================================================
#                        g e t G U I I n t e r f a c e
#=============================================================================
def getGUIInterface(itype):
    if type == 'debug':
        return IGUIDebug()
    elif type == 'panel':
        return IGUIPanel()
    elif type == 'filepanel':
        return IGUIFilePanel()
    else:
        return IGUIDebug()

#=============================================================================
#                             _ z i p F i l e s
#=============================================================================
gMFData = ''
def _zipFiles(outFileName, files, sceneFile, createManifest=True):

    global gMFData

    def storeFile(filePath):
        global gMFData
        if os.path.isdir(filePath):
            for file in glob.glob(filePath + '/*'):
                storeFile(file)
        elif os.path.exists(filePath):
            zfile.write(filePath)
            gMFData += '   <file value="{}"/>\r\n'.format(filePath)

    gMFData = '<?xml version="1.0"?>\r\n' +\
             '<data>\r\n' +\
             '   <Manifest-Version value="1.0"/>\r\n' +\
             '   <Created-By value="irrb {}"/>\r\n'.format(iversion) +\
             '   <Scene-File value="{}"/>\r\n'.format(sceneFile) +\
             '</data>\r\n<files>\r\n'

    if os.path.exists(outFileName):
        os.unlink(outFileName)

    cwd = os.getcwd()
    outd = os.path.dirname(outFileName)
    os.chdir(outd)

    zfile = zipfile.ZipFile(outFileName, 'w', zipfile.ZIP_DEFLATED)

    for filePath in files:
        storeFile(filePath)

    gMFData += '</files>\r\n'
    if createManifest:
        zfile.writestr('manifest.xml', gMFData)

    zfile.close()

    os.chdir(cwd)

    return True

#=============================================================================
#                       _ m a k e E x e c u t a b l e
#=============================================================================
RT_ARCHIVE = 1
RT_CONFIG = 2
def _makeExecutable(outFileName, sourceExecutable, resources):

    def appendResource(ofile, resource):
        ifile = open(resource, 'rb')
        buf = ifile.read(1024)
        while len(buf):
            ofile.write(buf)
            buf = ifile.read(1024)
        ifile.close()

    if os.path.exists(outFileName):
        os.unlink(outFileName)

    # sig1, offset, count, crc32, sig2
    sigStruct = struct.Struct('<L L L L L')
    sigValues = [0x62726142, 0, 0, 0, 0x62727269]

    # sig, type, id, length, crc32
    datStruct = struct.Struct('<L L 256s L L')
    datValues = [0x62726142, 0, 'none'.encode('ascii'), 0, 0]
    datData = datStruct.pack(*datValues)

    shutil.copy2(sourceExecutable, outFileName)

    ofile = open(outFileName, 'r+b')

    ofile.seek(0, 2)
    sigValues[1] = ofile.tell()

    count = 0
    for resource in resources:
        datValues[1] = resource[1]
        datValues[2] = resource[0].encode('ascii')
        if datValues[1] == RT_ARCHIVE:
            datValues[3] = os.path.getsize(resource[0])
            datData = datStruct.pack(*datValues)
            ofile.write(datData)
            appendResource(ofile, resource[0])
        elif datValues[1] == RT_CONFIG:
            datValues[3] = len(resource[0])
            datValues[2] = 'default.cfg'.encode('ascii')
            datData = datStruct.pack(*datValues)
            ofile.write(datData)
            ofile.write(str.encode(resource[0]))
        count += 1

    sigValues[2] = count
    sigData = sigStruct.pack(*sigValues)
    ofile.write(sigData)
    ofile.close()

#=============================================================================
#                       _ g e t C o n f i g V a l u e
#=============================================================================
def _getConfigValue(v):
    tfdict = {'true': True, 'false': False}
    if v.lower() in tfdict.keys():
        return tfdict[v.lower()]

    if v.isdigit():
        return int(v)

    return v

#=============================================================================
#                         _ l o a d C o n f i g
#=============================================================================
def _loadConfig():
    global gConfig, _G

    gConfig = configparser.RawConfigParser()
    gConfig.optionxform = str   # enable case sensitivity
    gConfig.read(gUserConfig)

    for section in gConfig.sections():
        if not section in  _G.keys():
            _G[section] = {}
        for k, v in gConfig.items(section):
            _G[section][k] = _getConfigValue(v)

    if len(_G['export']['out_directory'].strip()) == 0:
        _G['export']['out_directory'] = '{}{}{}{}'.format(
            os.path.expanduser('~'), os.sep, 'irrb', os.sep)

#=============================================================================
#                         _ s a v e C o n f i g
#=============================================================================
def _saveConfig():
    for section in _G.keys():
        if not gConfig.has_section(section):
            gConfig.add_section(section)
        dict = _G[section]
        for k, v in dict.items():
            gConfig.set(section, k, v)

    fp = open(gUserConfig, 'w')
    gConfig.write(fp)
    fp.close()

#=============================================================================
#                         g e t I r r M a t e r i a l
#=============================================================================
def getIrrMaterial(name):
    try:
        lname = name.lower()
        for info in irrMaterialTypes:
            if lname == info[1]:
                return info
    except:
        pass

    return None

#=============================================================================
#                               w r i t e T G A
#=============================================================================
def writeTGA(bImage, outFilename, RLE=True, callBack=None):
    file = open(outFilename, 'wb')

    width, height = bImage.size
    bpp = bImage.depth

    if bpp < 24:
        file.close()
        print('writeTGA only handles 24 or 32 bit images')
        return 1

    header = [chr(0) for x in range(18)]
    if RLE:
        header[2] = chr(10)     # rle bgra image
    else:
        header[2] = chr(2)      # bgra image
    header[13] = chr(width / 256)
    header[12] = chr(width % 256)
    header[15] = chr(height / 256)
    header[14] = chr(height % 256)
    header[16] = chr(bpp)       # 24 or 32 bpp
    if bpp == 32:
        header[17] = chr(3)    # 00vhaaaa - useful alpha data

    #
    # write header
    #
    for byte in header:
        file.write(byte)

    #
    # write data
    #
    for y in range(height):
        if (callBack != None) and ((y % 10) == 0):
            callBack(y)
        runLength = 1
        first = True
        lastPixel = ''
        for x in range(width):
            p = bImage.getPixelI(x, y)   # rgba
            pixel = chr(p[2]) + chr(p[1]) + chr(p[0])
            if bpp == 32:
                pixel += chr(p[3])

            if not RLE:
                file.write(pixel)
            else:
                if first:
                    lastPixel = pixel
                    first = False
                else:
                    if (pixel != lastPixel) or (runLength == 128):
                        packet = chr(128 + runLength - 1)
                        rleData = packet + lastPixel
                        file.write(rleData)
                        lastPixel = pixel
                        runLength = 1
                    else:
                        runLength += 1
        #
        # write last run
        #
        if RLE:
            packet = chr(128 + runLength - 1)
            rleData = packet + lastPixel
            file.write(rleData)

    file.close()
    return 0

#=============================================================================
#                         a d d S t a r t M e s s a g e
#=============================================================================
def addStartMessage(msg):
    _StartMessages.append(msg)

#=============================================================================
#                           _ u p d a t e D i c t
#=============================================================================
def _updateDict(tdict, fdict):
    for a in fdict:
        if type(fdict[a]).__name__ == 'dict':
            _updateDict(fdict[a], tdict[a])
        else:
            tdict[a] = fdict[a]

#=============================================================================
#             _ a c t i o n C o n t a i n s L o c R o t S c a l e
#=============================================================================
def _actionContainsLocRotScale(bAction):
    for curve in bAction.fcurves:
        if curve.data_path in ('location', 'rotation', 'scale'):
            return True

    return False

#=============================================================================
#                       _ h a s N o d e A n i m a t i o n s
#=============================================================================
def _hasNodeAnimations(bObject):
    if not bObject.animation_data:
        return False

    # check the selected action if any
    if bObject.animation_data.action:
        if _actionContainsLocRotScale(bObject.animation_data.action):
            return True

    # check NLA Tracks
    if bObject.animation_data.nla_tracks:
        for track in bObject.animation_data.nla_tracks:
            for strip in track.strips:
                if _actionContainsLocRotScale(strip.action):
                    return True
    return False

#=============================================================================
#                     _ g e t C o n s t r a i n t C o u n t
#=============================================================================
def _getConstraintCount(bObject):
    result = 0

    for c in bObject.constraints:
        if c.type == 'RIGID_BODY_JOINT':
            result += 1
    return result

#=============================================================================
#                         _ f o r m a t F l o a t s
#=============================================================================
def _formatFloats(ftuple, prefix=', '):
    sfloats = []
    res = ''
    pre = ''
    for f in ftuple:
        sfloat = '{:.6f}'.format(f).rstrip('0')
        l, r = sfloat.split('.')
        if len(r) == 0:
            sfloat = l
           
        res += pre + sfloat
        pre = prefix
        
    return res            

#=============================================================================
#                               o p e n L o g
#=============================================================================
def openLog(fileName):
    global _logFile
    if os.path.exists(fileName):
        os.unlink(fileName)
    _logFile = open(fileName, 'w')

    return False

#=============================================================================
#                              c l o s e L o g
#=============================================================================
def closeLog():
    if _logFile != None:
        _logFile.close()

#=============================================================================
#                              w r i t e L o g
#=============================================================================
def writeLog(msg):
    data = msg + '\n'
    if _logFile != None:
        _logFile.write(data)

#=============================================================================
#                                d e b u g
#=============================================================================
def debug(msg):
    writeLog(msg)

#=============================================================================
#                                d e b u g
#=============================================================================
def addWarning(msg):
    writeLog(msg)

#=============================================================================
#                            c o l o u r 2 s t r
#=============================================================================
def colour2str(value):
    return '{:08x}'.format(value)

#=============================================================================
#                       d u m p S t a r t M e s s a g e s
#=============================================================================
def dumpStartMessages():
    if len(_StartMessages) == 0:
        return

    debug('\n[start messages]')
    for msg in _StartMessages:
        debug(msg)

#=============================================================================
#                            f u z z y Z e r o
#=============================================================================
def fuzzyZero(fval):
    v = math.fabs(fval)

    if v < 0.000001:
        return True

    return False

#=============================================================================
#                            r g b 2 S C o l o r
#=============================================================================
def rgb2SColor(value):
    a = 255
    r = int(value[0] * 255.0)
    g = int(value[1] * 255.0)
    b = int(value[2] * 255.0)
    if len(value) > 3:
        a = int(value[3] * 255.0)

    SColor = (a << 24) | (r << 16) | (g << 8) | b
    return SColor

#=============================================================================
#                            r g b 2 D e l S t r
#=============================================================================
def rgb2DelStr(value):
    r = int(value[0] * 255.0)
    g = int(value[1] * 255.0)
    b = int(value[2] * 255.0)
    return '{} {} {} 255'.format(r, g, b)

#=============================================================================
#                            d e l 2 S C o l o r
#=============================================================================
def del2SColor(value):
    vals = value.split()
    r, g, b, a = 0, 0, 0, 255
    try:
        r = int(vals[0])
        g = int(vals[1])
        b = int(vals[2])
        a = int(vals[3])
    except:
        pass

    value = (a << 24) | (r << 16) | (g << 8) | b
    return '{:08x}'.format(value)

#=============================================================================
#                             b c 2 S C o l o r
#=============================================================================
def bc2SColor(value, alpha):
    r, g, b, a = 0, 0, 0, 255
    try:
        r = int(value.r * 255.0)
        g = int(value.g * 255.0)
        b = int(value.b * 255.0)
        a = int(alpha * 255.0)
    except:
        pass

    value = (a << 24) | (r << 16) | (g << 8) | b
    return '{:08x}'.format(value)

#=============================================================================
#                              r g b 2 s t r
#=============================================================================
def rgb2str(value):
    ival = rgb2SColor(value)
    return colour2str(ival)

#=============================================================================
#                             f l o a t 2 s t r
#=============================================================================
def float2str(value):
    return _formatFloats((value, ))
    
#=============================================================================
#                               i n t 2 s t r
#=============================================================================
def int2str(value):
    rval = str(value)
    return rval

#=============================================================================
#                              b o o l 2 s t r
#=============================================================================
def bool2str(value):
    rval = 'false'
    if value:
        rval = 'true'
    return rval

#=============================================================================
#                           d a t e t i m e 2 s t r
#=============================================================================
def datetime2str(value):
    rval = 'mm/dd/yyyy hh:nn'
    yyyy = value[0]
    mm = value[1]
    dd = value[2]
    hh = value[3]
    nn = value[4]
    rval = '{:02d}/{:02d}/{} {:02d}:{:02d}'.format(mm, dd, yyyy, hh, nn)
    return rval

#=============================================================================
#                             g e t v e r s i o n
#=============================================================================
def getversion():
    return 'v' + iversion

#=============================================================================
#                             g e t I n d e n t
#=============================================================================
def getIndent(level, extra=0):
    indent = (level + 1) * '   '
    if extra > 0:
        indent += extra * ' '
    return indent

#=============================================================================
#                            f l a t t e n P a t h
#=============================================================================
def flattenPath(path):
    out = ''
    if path == None:
        return out
    path = path.strip()
    for c in path:
        if c == '/' or c == '\\':
            out = out + '/'
        else:
            out = out + c
    return out

#=============================================================================
#                            f i l t e r P a t h
#=============================================================================
def filterPath(path):
    out = flattenPath(path)
    if out[len(out) - 1] != '/':
        out = out + '/'
    return out

#=============================================================================
#                          f i l t e r D i r P a t h
#=============================================================================
def filterDirPath(path):
    out = ''
    path = path.strip()

    for c in path:
        if c == '/' or c == '\\':
            out = out + os.sep
        else:
            out = out + c
    if out[len(out) - 1] != os.sep:
        out = out + os.sep

    return out

#=============================================================================
#                           g e t P r o p e r t y
#=============================================================================
def getProperty(pname, bObject, caseSensitive=False):

    if pname in bObject.keys():
        return bObject[pname]

    if bObject.data and (pname in bObject.data.keys()):
        return bObject.data[pname]

    return None

#=============================================================================
#                             b 2 i S c a l e
#=============================================================================
# flip y <-> z
def b2iScale(bVector):
    return (bVector.x, bVector.z, bVector.y)

#=============================================================================
#                             b 2 i P o s i t i o n
#=============================================================================
# flip y <-> z
def b2iPosition(bObject):
    bVector = bObject.matrix_local.to_translation()

    if bObject.parent != None and hasattr(bObject, 'type') and bObject.parent.type == 'CAMERA':
        crot = mathutils.Matrix.Rotation(math.pi / 2.0, 3, 'X')
        bVector = bVector * crot

    return (bVector.x, bVector.z, bVector.y)

#=============================================================================
#                            b 2 i R o t a t i o n
#=============================================================================
def b2iRotation(bObject):
    x = 'X'
    y = 'Z'
    z = 'Y'
    bEuler = bObject.matrix_local.to_euler()
    crot = mathutils.Matrix().to_3x3()

    if hasattr(bObject, 'type'):
        if bObject.parent != None and bObject.parent.type == 'CAMERA':
            crot = mathutils.Matrix.Rotation(-math.pi / 2.0, 3, 'X')

        if bObject.type == 'CAMERA' or bObject.type == 'LAMP':
            crot = mathutils.Matrix.Rotation(math.pi / 2.0, 3, 'X')
            bEuler.z = -bEuler.z
            y = 'Y'
            z = 'Z'

    xrot = mathutils.Matrix.Rotation(-bEuler.x, 3, x)
    yrot = mathutils.Matrix.Rotation(-bEuler.y, 3, y)
    zrot = mathutils.Matrix.Rotation(-bEuler.z, 3, z)
    rot = crot * zrot * yrot * xrot

    bEuler = rot.to_euler()

    return (bEuler.x * RAD2DEG, bEuler.y * RAD2DEG,
        bEuler.z * RAD2DEG)

#=============================================================================
#                            b 2 i R o t a t i o n 2
#=============================================================================
def b2iRotation2(bObject):
    bEuler = bObject.matrix_local.to_euler()
    return (bEuler.x * RAD2DEG, bEuler.y * RAD2DEG,
        bEuler.z * RAD2DEG)

#=============================================================================
#                 _ u p d a t e D e f a u l t C o n f i g
#=============================================================================
def _updateDefaultConfig(bscene):
    if bscene.irrb_wt_debug:
        gWTOptions['obShowDebug'] = 'true'
    else:
        gWTOptions['obShowDebug'] = 'false'

    if bscene.irrb_wt_showhelp:
        gWTOptions['obShowHelp'] = 'true'
    else:
        gWTOptions['obShowHelp'] = 'false'

    if bscene.irrb_wt_vsync:
        gWTOptions['obVSync'] = 'true'
    else:
        gWTOptions['obVSync'] = 'false'

    if bscene.irrb_wt_antialias:
        gWTOptions['oiAntiAlias'] = 4
    else:
        gWTOptions['oiAntiAlias'] = 0

    if bscene.irrb_wt_stencilbuffer:
        gWTOptions['obStencilBuffer'] = 'true'
    else:
        gWTOptions['obStencilBuffer'] = 'false'

    if bscene.irrb_wt_fullscreen:
        gWTOptions['obFullScreen'] = 'true'
    else:
        gWTOptions['obFullScreen'] = 'false'

    gWTOptions['osDriver'] = 'EDT_OPENGL'
    if gPlatform == 'Windows':
        if bscene.irrb_wt_driver == 'DRIVER_D3D9':
            gWTOptions['osDriver'] = 'EDT_DIRECT3D9'

    if bscene.irrb_wt_resolution == 'RES_MINIMUM':
        gWTOptions['osResolution'] = '\'minimum\''
    elif bscene.irrb_wt_resolution == 'RES_MEDIUM':
        gWTOptions['osResolution'] = '\'medium\''
    elif bscene.irrb_wt_resolution == 'RES_MAXIMUM':
        gWTOptions['osResolution'] = '\'maximum\''
    else:  # custom
        gWTOptions['osResolution'] = '{{{}, {}}}'.format(
            bscene.irrb_wt_resx, bscene.irrb_wt_resy)

    if bscene.irrb_wt_keepaspect:
        gWTOptions['obKeepAspect'] = 'true'
    else:
        gWTOptions['obKeepAspect'] = 'false'
    gWTOptions['osPhysicsSystem'] = 'Irrlicht'
    gWTOptions['ofVelocity'] = bscene.irrb_wt_velocity
    gWTOptions['ofAVelocity'] = bscene.irrb_wt_avelocity
    gWTOptions['ofVelocityDamp'] = bscene.irrb_wt_velocitydamp
    gWTOptions['ofCharWidth'] = bscene.irrb_wt_char_width
    gWTOptions['ofCharHeight'] = bscene.irrb_wt_char_height
    gWTOptions['ofCharStepHeight'] = \
        bscene.irrb_wt_char_stepheight
    gWTOptions['ofCharJumpSpeed'] = bscene.irrb_wt_char_jumpspeed

    if bscene.irrb_wt_phycolsys == 'PCS_BULLET':
        gWTOptions['osPhysicsSystem'] = 'Bullet'

        if bscene.irrb_wt_bullet_broadphase == 'BROADPHASE_DBVT':
            gWTOptions['osBroadphase'] = 'btDbvt'
        elif bscene.irrb_wt_bullet_broadphase == 'BROADPHASE_AS':
            gWTOptions['osBroadphase'] = 'btAxisSweep3'
        elif bscene.irrb_wt_bullet_broadphase == \
            'BROADPHASE_AS3':
            gWTOptions['osBroadphase'] = 'bt32BitAxisSweep3'

        gWTOptions['oiSubSteps'] = bscene.irrb_wt_bullet_substeps
        gWTOptions['oiTimeStep'] = bscene.irrb_wt_bullet_timestep

    return (gWTConfig.format(**gWTOptions), gWTConfigGen.format(**gWTOptions))

#=============================================================================
#                          w r i t e A t t r i b u t e s
#=============================================================================
def writeAttributes(file, indent, target):
    for name in target.keys():
        # skip private & irrb properties
        if (name[0] == '_') or (name[:4] == 'irrb'):
            continue

        data = target[name]
        stype = None
        if isinstance(data, int):
            stype = 'int'
            svalue = str(data)
        elif isinstance(data, str):
            stype = 'string'
            svalue = data
        elif isinstance(data, float):
            stype = 'float'
            svalue = float2str(data)

        if name.lower().find('color') >= 0:
            stype = 'colorf'

        if stype != None:
            pout = '<{} name="{}" value="{}"/>\n'.format(stype, name,
                svalue)
            file.write(indent + pout)

#=============================================================================
#                           w r i t e U s e r D a t a
#=============================================================================
def writeUserData(file, i1, i2, bObject, writeClose=True):
    file.write(i1 + '<userData>\n')
    file.write(i2 + '<attributes>\n')
    i3 = i2 + '   '
    
    writeAttributes(file, i3, bObject)
    try:
        writeAttributes(file, i3, bObject.data)
    except:
        pass

    if writeClose:
        file.write(i2 + '</attributes>\n')
        file.write(i1 + '</userData>\n')
        
#=============================================================================
#                          c h e c k D i r e c t o r y
#=============================================================================
def checkDirectory(dirVal):
    tempDir = filterDirPath(dirVal)
    if not os.path.isdir(tempDir):
        os.makedirs(tempDir)
    return tempDir

#=============================================================================
#                          s e t D i r e c t o r y
#=============================================================================
def setDirectory(base, option):
    result = _G['export'][option]
    if (result[0] == '/') or (result.find(':') >= 0):  # absolute?
        result = filterDirPath(result)
    else:
        result = os.path.abspath(base + result)
    checkDirectory(result)
    return result

#=============================================================================
#                                   w r i t e
#=============================================================================
def write(filename, operator, context, OutDirectory, CreateSceneFile,
    SelectedOnly, ExportLights, ExportCameras, ExportAnimations,
     ExportAnimationTails, ExportPhysics, ExportPack, ExportExec, ExportBinary,
     runWalkTest, IrrlichtVersion):
    _saveConfig()

    if not filename.lower().endswith('.irr'):
        filename += '.irr'

    OutDirectory = filterDirPath(OutDirectory)
    checkDirectory(OutDirectory)

    # setup and check scene directory
    SceneDirectory = setDirectory(OutDirectory, 'scene_directory')
    MeshDirectory = setDirectory(OutDirectory, 'mdl_directory')
    ImageDirectory = setDirectory(OutDirectory, 'tex_directory')

    operator.report({'INFO'}, 'irrb Export')

    WalkTestPath = gWalkTestPath

    if gWalkTestPath64 and (context.scene.irrb_wt_bits == "BITS_64"):
        WalkTestPath = gWalkTestPath64

    exporter = iExporter(context, operator, getGUIInterface('filepanel'),
                CreateSceneFile, OutDirectory,
                SceneDirectory, MeshDirectory, ImageDirectory, SelectedOnly,
                ExportLights, ExportCameras, ExportAnimations, ExportAnimationTails, 
                ExportPhysics, ExportPack, ExportExec, ExportBinary,
                True, runWalkTest, gVersionList[IrrlichtVersion],
                gMeshCvtPath, WalkTestPath)

    exporter.doExport()
    operator.report({'INFO'}, 'irrb Export Done.')
    
#=============================================================================
#                _ r e g i s t e r I r r b P r o p e r t i e s
#=============================================================================
def _registerIrrbProperties():
    global gMeshCvtPath, gWalkTestPath, gWalkTestPath32, gWalkTestPath64
    emptySet = set([])

    # Scene properties
    bpy.types.Scene.irrb_outpath_win = StringProperty(name='Out Directory',
        description='Base output directory used for exporting ' \
            '.irr/irrmesh files.',
        maxlen=1024, default='', subtype='DIR_PATH')

    bpy.types.Scene.irrb_outpath = StringProperty(name='Out Directory',
        description='Base output directory used for exporting ' \
            '.irr/irrmesh files.',
        maxlen=1024, default='', subtype='DIR_PATH')

    bpy.types.Scene.irrb_export_scene = BoolProperty(name='Scene',
        description='Export scene (create .irr)', default=True,
        options=emptySet)

    bpy.types.Scene.irrb_export_lights = BoolProperty(name='Light(s)',
        description='Export lights(s)', default=True, options=emptySet)

    bpy.types.Scene.irrb_export_cameras = BoolProperty(name='Camera(s)',
        description='Export camera(s)', default=True, options=emptySet)

    bpy.types.Scene.irrb_export_animations = BoolProperty(name='Animation(s)',
        description='Export animation(s)', default=True, options=emptySet)

    bpy.types.Scene.irrb_export_animation_tails = BoolProperty(name='Tail Joint(s)',
        description='Export bone tail joints (for debugging)', default=False, options=emptySet)

    bpy.types.Scene.irrb_export_physics = BoolProperty(name='Physics',
        description='Export physics/collision data', default=False,
        options=emptySet)

    bpy.types.Scene.irrb_export_selected = BoolProperty(name='Selected Only',
        description='Export selected object(s) only', default=False,
        options=emptySet)

    bpy.types.Scene.irrb_export_pack = BoolProperty(name='Pack Files',
        description='Pack files into a single {scene}.zip file', default=False,
        options=emptySet)

    bpy.types.Scene.irrb_export_makeexec = BoolProperty(name='Make Executable',
        description='Make scene file executable', default=False,
        options=emptySet)

    bpy.types.Scene.irrb_export_debug = BoolProperty(name='Log Debug',
        description='Write debug data to irrb.log', default=True,
        options=emptySet)

    bpy.types.Scene.irrb_scene_vars_init = \
        BoolProperty(name='Internal Init Variable',
        description='Internal Use Only',
        default=False, options=emptySet)

    gMeshCvtPath = None
    if 'IMESHCVT' in os.environ:
        gMeshCvtPath = os.environ['IMESHCVT']
        bpy.types.Scene.irrb_export_binary = BoolProperty(name='Binary Meshes',
            description='Convert meshes to binary (.irrbmesh)',
            default=False, options=emptySet)

    gWalkTestPath = None
    if gHaveWalkTest:
        gWalkTestPath = os.environ['IWALKTEST']
        bpy.types.Scene.irrb_export_walktest = BoolProperty(name='Walktest',
            description='Walktest after export', default=True,
            options=emptySet)

        if len(gWalkTestPath.strip()) > 0:
            gWalkTestPath32 = gWalkTestPath
            wtBin = gWalkTestPath.split()[0]
            wtApp = os.path.basename(wtBin)
            wtDir = os.path.dirname(wtBin) + os.path.sep
            wtDir64 = wtDir + 'x64' + os.path.sep
            wtApp64 = wtDir64 + wtApp
            if os.path.exists(wtApp64):
                gWalkTestPath64 = '{} {}'.format(wtApp64, \
                    ' '.join(gWalkTestPath.split()[1:]))

    bpy.types.Scene.irrb_wt_bits = EnumProperty(name='Bits',
        items=(('BITS_32', '32bit', ''),
        ('BITS_64', '64bit', ''),
        ),
        default='BITS_32',
        description='Walktest arch target',
        options=emptySet)

    # scene walktest config parameters
    bpy.types.Scene.irrb_wt_showhelp = BoolProperty(name='Show Help',
        description='Show help window on startup', default=True,
        options=emptySet)

    bpy.types.Scene.irrb_wt_antialias = BoolProperty(name='Antialias',
        description='Use antialiasing', default=True,
        options=emptySet)

    bpy.types.Scene.irrb_wt_debug = BoolProperty(name='Debug',
        description='Show debug console', default=True,
        options=emptySet)

    bpy.types.Scene.irrb_wt_fullscreen = BoolProperty(name='Full Screen',
        description='Use full screen', default=False,
        options=emptySet)

    bpy.types.Scene.irrb_wt_vsync = BoolProperty(name='VSync',
        description='Use vertical synchronization', default=True,
        options=emptySet)

    bpy.types.Scene.irrb_wt_stencilbuffer = BoolProperty(name='Stencil Buffer',
        description='Enable stencil buffer', default=True,
        options=emptySet)

    bpy.types.Scene.irrb_wt_driver = EnumProperty(name='Video Driver',
        items=(('DRIVER_OGL', 'OpenGL', ''),
            ('DRIVER_D3D9', 'DirectX 9', ''),
        ),
        default='DRIVER_OGL',
        description='Video Driver',
        options=emptySet)

    bpy.types.Scene.irrb_wt_velocity = FloatProperty(name='Velocity',
        description='Camera/Character Velocity',
        default=gWTOptions['ofVelocity'],
        min=0.01, max=1024.0, soft_min=0.01, soft_max=1024.0,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Scene.irrb_wt_avelocity = FloatProperty(name='Angular Velocity',
        description='Camera/Character Angular Velocity',
        default=gWTOptions['ofAVelocity'],
        min=0.01, max=1024.0, soft_min=0.01, soft_max=1024.0,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Scene.irrb_wt_velocitydamp = FloatProperty(
        name='Velocity Damping',
        description='Camera/Character Velocity Damping',
        default=gWTOptions['ofVelocityDamp'],
        min=0.0, max=1024.0, soft_min=0.0, soft_max=1024.0,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Scene.irrb_wt_bullet_broadphase = EnumProperty(name='Broadphase',
        items=(('BROADPHASE_DBVT', 'btDbvt', ''),
        ('BROADPHASE_AS', 'btAxisSweep3', ''),
        ('BROADPHASE_AS32', 'bt32BitAxisSweep3', ''),
        ),
        default='BROADPHASE_DBVT',
        description='Bullet Broadphase Algorithm',
        options=emptySet)

    bpy.types.Scene.irrb_wt_bullet_substeps = IntProperty(name='SubSteps',
        min=1, max=5, default=gWTOptions['oiSubSteps'], options=emptySet)

    bpy.types.Scene.irrb_wt_bullet_timestep = IntProperty(name='TimeStep',
        min=1, max=250, default=gWTOptions['oiTimeStep'], options=emptySet)

    bpy.types.Scene.irrb_wt_char_width = FloatProperty(name='Char Width',
        description='Physics Character Width',
        default=gWTOptions['ofCharWidth'],
        min=0.1, max=1024.0, soft_min=0.0, soft_max=1024.0,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Scene.irrb_wt_char_height = FloatProperty(name='Char Height',
        description='Physics Character Height',
        default=gWTOptions['ofCharHeight'],
        min=0.1, max=1024.0, soft_min=0.0, soft_max=1024.0,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Scene.irrb_wt_char_stepheight = FloatProperty(
        name='Char Step Height',
        description='Physics Character Step Height',
        default=gWTOptions['ofCharStepHeight'],
        min=0.1, max=1024.0, soft_min=0.0, soft_max=1024.0,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Scene.irrb_wt_char_jumpspeed = FloatProperty(
        name='Char Jump Speed',
        description='Physics Character Jump Speed',
        default=gWTOptions['ofCharJumpSpeed'],
        min=0.1, max=1024.0, soft_min=0.0, soft_max=1024.0,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Scene.irrb_wt_resolution = EnumProperty(name='Resolution',
        items=(('RES_MINIMUM', 'Minimum', ''),
        ('RES_MEDIUM', 'Medium', ''),
        ('RES_MAXIMUM', 'Maximum', ''),
        ('RES_CUSTOM', 'Custom', ''),
        ),
        default='RES_MEDIUM',
        description='Screen resolution',
        options=emptySet)

    bpy.types.Scene.irrb_wt_resx = IntProperty(name='X Res',
        min=32, max=4096, default=640, options=emptySet)

    bpy.types.Scene.irrb_wt_resy = IntProperty(name='Y Res',
        min=32, max=4096, default=480, options=emptySet)

    bpy.types.Scene.irrb_wt_keepaspect = BoolProperty(name='Keep Aspect',
        description='Keep Screen Aspect', default=False,
        options=emptySet)

    bpy.types.Scene.irrb_wt_phycolsys = EnumProperty(name='Physics System',
        items=(('PCS_IRRLICHT', 'Irrlicht', ''),
        ('PCS_BULLET', 'Bullet', ''),
        ),
        default='PCS_IRRLICHT',
        description='Physics/Collision System',
        options=emptySet)

    # Object Properties
    bpy.types.Object.irrb_node_export = BoolProperty(name='Export',
        description='Export object to scene', default=True,
        options=emptySet)

    bpy.types.Object.irrb_node_id = IntProperty(name='Node ID',
        description='Object scene node id', default=-1,
        options=emptySet)

    bpy.types.Object.irrb_node_type = EnumProperty(name='Scene Node Type',
        items=(('DEFAULT', 'Standard Mesh', 'default mesh type'),
        ('BILLBOARD', 'Billboard', 'billboard type'),
        ('SKYBOX', 'Skybox', 'skybox type'),
        ('SKYDOME', 'Skydome', 'skydome type'),
        ('VOLLIGHT', 'Volumetric Light', 'volumetric light type'),
        ('WATERSURFACE', 'Water Surface', 'water surface'),
        ('CUSTOM', 'Custom', 'custom scene node'),
        ),
        default='DEFAULT',
        description='Irrlicht scene node type',
        options=emptySet)
    
    bpy.types.Object.irrb_custom_node_type = StringProperty(name='CustomNodeType',
        description='Custom node type',
        default='?', maxlen=64, options=emptySet, subtype='NONE')
    
    bpy.types.Object.irrb_node_culling = EnumProperty(name='Automatic Culling',
        items=(('CULL_OFF', 'Off', ''),
        ('CULL_BOX', 'Box', ''),
        ('CULL_FRUSTUM_BOX', 'Frustum Box', ''),
        ('CULL_FRUSTUM_SPHERE', 'Frustum Sphere', ''),
        ('CULL_OCCLUSION_QUERY', 'Occlusion Query', ''),
        ),
        default='CULL_FRUSTUM_BOX',
        description='Irrlicht scene node culling',
        options=emptySet)

    bpy.types.Object.irrb_node_hwhint = EnumProperty(name='Hardware Hint',
        items=(('EHM_NEVER', 'Never', ''),
        ('EHM_STATIC', 'Static', ''),
        ('EHM_DYNAMIC', 'Dynamic', ''),
        ('EHM_STREAM', 'Stream', ''),
        ),
        default='EHM_NEVER',
        description='Irrlicht hardware mapping hint',
        options=emptySet)

    bpy.types.Object.irrb_node_hwhint_bt = EnumProperty(
        name='Hint Buffer Type',
        items=(('EBT_NONE', 'None', ''),
        ('EBT_VERTEX', 'Vertex', ''),
        ('EHM_INDEX', 'Index', ''),
        ('EHM_VERTEX_AND_INDEX', 'Vertex & Index', ''),
        ),
        default='EHM_VERTEX_AND_INDEX',
        description='Irrlicht hardware mapping hint buffer type',
        options=emptySet)

    # Octree Object Properties
    bpy.types.Object.irrb_node_octree = BoolProperty(name='Octree Node',
        description='Export as Octree node', default=False,
        options=emptySet)

    bpy.types.Object.irrb_node_octree_polys = IntProperty(name='',
        description='Octree Minimum Poly Count',
        min=32, default=128, options=emptySet)

    # Skydome Object Properties
    bpy.types.Object.irrb_dome_hres = IntProperty(name='Horz Res',
        description='Horizontal Resolution',
        min=1, default=16, options=emptySet)

    bpy.types.Object.irrb_dome_vres = IntProperty(name='Vert Res',
        description='Vertical Resolution',
        min=1, default=8, options=emptySet)

    bpy.types.Object.irrb_dome_texpct = FloatProperty(name='Tex Pct',
        description='Texture Percentage', default=1.0,
        min=0.01, max=1.0, soft_min=0.01, soft_max=1.0,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Object.irrb_dome_spherepct = FloatProperty(name='Sphere Pct',
        description='Sphere Percentage', default=1.2,
        min=0.1, max=2.0, soft_min=0.1, soft_max=2.0,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Object.irrb_dome_radius = FloatProperty(name='Radius',
        description='Radius', default=10.0,
        min=1.0, max=1000.0, soft_min=1.0, soft_max=1000.0,
        step=3, precision=2,
        options=emptySet)

    # Water Surface Properties
    bpy.types.Object.irrb_water_wavelength = FloatProperty(name='Wave Length',
        description='Wave Length', default=10.0,
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Object.irrb_water_wavespeed = FloatProperty(name='Wave Speed',
        description='Wave Speed', default=300.0,
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Object.irrb_water_waveheight = FloatProperty(name='Wave Height',
        description='Wave Height', default=2.0,
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=3, precision=2,
        options=emptySet)

    # Volumetric Light Properties
    bpy.types.Object.irrb_volight_distance = FloatProperty(name='Distance',
        description='Wave Height', default=8.0,
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Object.irrb_volight_subu = IntProperty(name='U Subdivide',
        description='U Subdivide',
        min=1, default=100, options=emptySet)

    bpy.types.Object.irrb_volight_subv = IntProperty(name='V Subdivide',
        description='V Subdivide',
        min=1, default=100, options=emptySet)

    bpy.types.Object.irrb_volight_footcol = FloatVectorProperty(name='Foot',
        description='Foot color',
        default=(1.0, 1.0, 1.0),
        min=0.0, max=1.0,
        soft_min=0.0, soft_max=1.0,
        step=0.01, precision=2,
        options=emptySet, subtype='COLOR', size=3)

    bpy.types.Object.irrb_volight_tailcol = FloatVectorProperty(name='Tail',
        description='Tail color',
        default=(1.0, 1.0, 1.0),
        min=0.0, max=1.0,
        soft_min=0.0, soft_max=1.0,
        step=0.01, precision=2,
        options=emptySet, subtype='COLOR', size=3)

    bpy.types.Object.irrb_volight_dimension = FloatVectorProperty(
        name='Dimension',
        description='Dimension',
        default=(1.0, 1.0, 1.0),
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=1.0, precision=2,
        options=emptySet, size=3)
    
    # Billboard Properties
    bpy.types.Object.irrb_billboard_shade_top = FloatVectorProperty(name='ShadeTop',
        description='Shade Top',
        default=(1.0, 1.0, 1.0),
        min=0.0, max=1.0,
        soft_min=0.0, soft_max=1.0,
        step=0.01, precision=2,
        options=emptySet, subtype='COLOR', size=3)
    
    bpy.types.Object.irrb_billboard_shade_bot = FloatVectorProperty(name='ShadeBot',
        description='Shade Bottom',
        default=(1.0, 1.0, 1.0),
        min=0.0, max=1.0,
        soft_min=0.0, soft_max=1.0,
        step=0.01, precision=2,
        options=emptySet, subtype='COLOR', size=3)
    
    bpy.types.Object.irrb_billboard_width = FloatProperty(name='Width',
        description='Width', default=1.0,
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Object.irrb_billboard_height = FloatProperty(name='Height',
        description='Height', default=1.0,
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=3, precision=2,
        options=emptySet)
    
    # Light Object Properties
    bpy.types.Object.irrb_light_type = EnumProperty(name='Light Type',
        items=(('ILT_POINT', 'Point', ''),
        ('ILT_SPOT', 'Spot', ''),
        ('ILT_DIRECTIONAL', 'Directional', ''),
        ),
        default='ILT_POINT',
        description='Irrlicht light type',
        options=emptySet)
    
    bpy.types.Object.irrb_light_ambient = FloatVectorProperty(name='Ambient',
        description='Ambient color',
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
        soft_min=0.0, soft_max=1.0,
        step=0.01, precision=2,
        options=emptySet, subtype='COLOR', size=3)

    bpy.types.Object.irrb_light_specular = FloatVectorProperty(name='Specular',
        description='Specular color',
        default=(1.0, 1.0, 1.0),
        min=0.0, max=1.0,
        soft_min=0.0, soft_max=1.0,
        step=0.01, precision=2,
        options=emptySet, subtype='COLOR', size=3)
    
    bpy.types.Object.irrb_light_radius = FloatProperty(name='Radius',
        description='Radius', default=100.0,
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=3, precision=2,
        options=emptySet)
    
    bpy.types.Object.irrb_light_attenuation = FloatVectorProperty(
        name='Attenuation',
        description='Attenuation',
        default=(1.0, 0.0, 0.0),
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=1.0, precision=2,
        options=emptySet, size=3)
    
    bpy.types.Object.irrb_light_outercone = FloatProperty(name='OuterCone',
        description='Outer Cone', default=45.0,
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Object.irrb_light_innercone = FloatProperty(name='InnerCone',
        description='Inner Cone', default=0.0,
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Object.irrb_light_falloff = FloatProperty(name='FallOff',
        description='Fall off', default=2.0,
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=3, precision=2,
        options=emptySet)
    
    bpy.types.Object.irrb_light_castshadows = BoolProperty(name='CastShadows',
        description='Cast Shadows', default=True, options=emptySet)
    
    #Camera Object Properties
    bpy.types.Object.irrb_cam_target = FloatVectorProperty(
        name='Target',
        description='Target',
        default=(0.0, 0.0, 0.0),
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=1.0, precision=2,
        options=emptySet, size=3)
    
    bpy.types.Object.irrb_cam_upvector = FloatVectorProperty(
        name='Up Vector',
        description='Up Vector',
        default=(0.0, 1.0, 0.0),
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=1.0, precision=2,
        options=emptySet, size=3)
    
    bpy.types.Object.irrb_cam_fov = FloatProperty(name='FOV',
        description='FOV', default=0.85,
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=3, precision=2,
        options=emptySet)
    
    bpy.types.Object.irrb_cam_aspect = FloatProperty(name='Aspect',
        description='Aspect', default=1.25,
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=3, precision=2,
        options=emptySet)
    
    bpy.types.Object.irrb_cam_bindtarget = BoolProperty(name='BindTarget',
        description='Bind Target', default=False, options=emptySet)    
    
    
    # Material Properties
    bpy.types.Material.irrb_type = EnumProperty(name='Material Type',
        items=tuple([(mat[0], mat[1], '') for mat in irrMaterialTypes]),
        default='EMT_SOLID',
        description='Irrlicht material type',
        options=emptySet)

    bpy.types.Material.irrb_custom_name = StringProperty(name='CustomName',
        description='Custom material name',
        default='?', maxlen=64, options=emptySet, subtype='NONE')

    bpy.types.Material.irrb_diffuse = FloatVectorProperty(name='Diffuse',
        description='Diffuse color',
        default=(1.0, 1.0, 1.0),
        min=0.0, max=1.0,
        soft_min=0.0, soft_max=1.0,
        step=0.01, precision=2,
        options=emptySet, subtype='COLOR', size=3)

    bpy.types.Material.irrb_ambient = FloatVectorProperty(name='Ambient',
        description='Ambient color',
        default=(1.0, 1.0, 1.0),
        min=0.0, max=1.0,
        soft_min=0.0, soft_max=1.0,
        step=0.01, precision=2,
        options=emptySet, subtype='COLOR', size=3)

    bpy.types.Material.irrb_emissive = FloatVectorProperty(name='Emissive',
        description='Emissive color',
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
        soft_min=0.0, soft_max=1.0,
        step=0.01, precision=2,
        options=emptySet, subtype='COLOR', size=3)

    bpy.types.Material.irrb_lighting = BoolProperty(name='Lighting',
        description='Enable lighting', default=True, options=emptySet)

    bpy.types.Material.irrb_gouraud = BoolProperty(name='Gouraud',
        description='Enable gouraud shading', default=True, options=emptySet)

    bpy.types.Material.irrb_backcull = BoolProperty(name='Backface Culling',
        description='Enable backface culling', default=True, options=emptySet)

    bpy.types.Material.irrb_frontcull = BoolProperty(name='Frontface Culling',
        description='Enable frontface culling', default=False,
        options=emptySet)

    bpy.types.Material.irrb_zwrite_enable = BoolProperty(name='ZWriteEnable',
        description='Enable writing to the ZBuffer', default=True,
        options=emptySet)

    bpy.types.Material.irrb_normalize_normals = \
        BoolProperty(name='Normalize Normals',
        description='Normalize Normals', default=False, options=emptySet)

    bpy.types.Material.irrb_link_diffuse = \
        BoolProperty(name='Link Diffuse',
        description='Link Diffuse Color', default=True, options=emptySet)

    bpy.types.Material.irrb_use_mipmaps = BoolProperty(name='Use MipMaps',
        description='Use MipMaps if available', default=True, options=emptySet)

    bpy.types.Material.irrb_zbuffer = EnumProperty(name='ZBuffer',
        items=(('ECFN_NEVER', 'Never (Disable)', ''),
        ('ECFN_LESSEQUAL', 'Less or Equal', ''),
        ('ECFN_EQUAL', 'Equal', ''),
        ('ECFN_LESS', 'Less', ''),
        ('ECFN_NOTEQUAL', 'Not Equal', ''),
        ('ECFN_GREATOREQUAL', 'Greator or Equal', ''),
        ('ECFN_GREATOR', 'Greator', ''),
        ('ECFN_ALWAYS', 'Always', ''),
        ),
        default='ECFN_LESSEQUAL',
        description='ZBuffer comparison function for depth buffer test',
        options=emptySet)

    bpy.types.Material.irrb_color_material = \
        EnumProperty(name='Color Material',
        items=(('ECM_NONE', "Don't use vertex color", ''),
        ('ECM_DIFFUSE', 'Diffuse light', ''),
        ('ECM_AMBIENT', 'Ambient light', ''),
        ('ECM_EMISSIVE', 'Emissive light', ''),
        ('ECM_SPECULAR', 'Specular light', ''),
        ('ECM_DIFFUSE_AND_AMBIENT', 'Diffuse and Ambient light', ''),
        ),
        default='ECM_DIFFUSE',
        description='Interpretation of vertex color when lighting is enabled',
        options=emptySet)

    bpy.types.Material.irrb_antialiasing = \
        EnumProperty(name='Antialiasing Mode',
        items=(('EAAM_OFF', 'Disabled', ''),
        ('EAAM_SIMPLE', 'Simple', ''),
        ('EAAM_QUALITY', 'Quality', ''),
        ('EAAM_LINE_SMOOTH', 'Line smooth', ''),
        ('EAAM_POINT_SMOOTH', 'Point smooth', ''),
        ('EAAM_FULL_BASIC', 'Full basic', ''),
        ('EAAM_ALPHA_TO_COVERAGE', 'Enhanced (Transparent)', ''),
        ),
        default='EAAM_SIMPLE',
        description='Antiliasing Mode',
        options=emptySet)

    bpy.types.Material.irrb_color_mask_alpha = BoolProperty(name='Alpha',
        description='Enable alpha plane', default=True, options=emptySet)

    bpy.types.Material.irrb_color_mask_red = BoolProperty(name='Red',
        description='Enable red plane', default=True, options=emptySet)

    bpy.types.Material.irrb_color_mask_green = BoolProperty(name='Green',
        description='Enable green plane', default=True, options=emptySet)

    bpy.types.Material.irrb_color_mask_blue = BoolProperty(name='Blue',
        description='Enable blue plane', default=True, options=emptySet)

    bpy.types.Material.irrb_fog = BoolProperty(name='Fog',
        description='Enable fog', default=True, options=emptySet)

    bpy.types.Material.irrb_param1 = FloatProperty(name='Param1',
        description='Type param1', default=0.0,
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Material.irrb_param2 = FloatProperty(name='Param2',
        description='Type param2', default=0.0,
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Material.irrb_shininess = FloatProperty(name='Shininess',
        description='Specular shininess', default=0.0,
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=3, precision=2,
        options=emptySet)

    bpy.types.Material.irrb_thickness = FloatProperty(name='Thickness',
        description='Thickness of non-3dimensional elements such as lines ' \
        'and points.', default=1.0,
        min=sys.float_info.min, max=sys.float_info.max,
        soft_min=sys.float_info.min, soft_max=sys.float_info.max,
        step=3, precision=2,
        options=emptySet)

    wrap_options = (('ETC_REPEAT', 'Repeat', ''),
        ('ETC_CLAMP', 'Clamp', ''),
        ('ETC_CLAMP_TO_EDGE', 'Clamp To Edge', ''),
        ('ETC_CLAMP_TO_BORDER', 'Clamp To Border', ''),
        ('ETC_MIRROR', 'Mirror', ''),
        ('ETC_MIRROR_CLAMP', 'Mirror Clamp', ''),
        ('ETC_MIRROR_CLAMP_TO_EDGE', 'Mirror Clamp To Edge', ''),
        ('ETC_MIRROR_CLAMP_TO_BORDER', 'Mirror Clamp To Border', ''),
        )

    def createLayerProps(layer):
        setattr(bpy.types.Material, 'irrb_layer{}_wrapu'.format(layer),
            EnumProperty(name='U Clamp Mode',
            items=wrap_options,
            default='ETC_REPEAT',
            description='U texture coordinate clamp mode',
            options=emptySet))

        setattr(bpy.types.Material, 'irrb_layer{}_wrapv'.format(layer),
            EnumProperty(name='V Clamp Mode',
            items=wrap_options,
            default='ETC_REPEAT',
            description='V texture coordinate clamp mode',
            options=emptySet))

        setattr(bpy.types.Material, 'irrb_layer{}_filter'.format(layer),
            EnumProperty(name='Filter',
            items=(('FLT_NONE', 'None', ''),
            ('FLT_BILINEAR', 'Bilinear', ''),
            ('FLT_TRILINEAR', 'Trilinear', ''),
            ),
            default='FLT_BILINEAR',
            description='Filter',
            options=emptySet))

        setattr(bpy.types.Material,
            'irrb_layer{}_anisotropic_value'.format(layer),
            IntProperty(name='Anisotropic',
            description='Anisotropic filter value',
            default=0,
            min=0, max=16,
            soft_min=0, soft_max=16,
            step=1,
            options=emptySet))

        setattr(bpy.types.Material, 'irrb_layer{}_lodbias'.format(layer),
            IntProperty(name='LOD Bias',
            description='Bias for mipmap selection',
            default=0,
            min=-128, max=128,
            soft_min=-128, soft_max=128,
            step=1,
            options=emptySet))

    createLayerProps(1)
    createLayerProps(2)
    createLayerProps(3)
    createLayerProps(4)

#=============================================================================
#                            m e n u _ f u n c
#=============================================================================
# this is invoked everytime the "Export | Irrlicht" menu item is selected.
def menu_func(self, context):
    self.layout.operator(IrrbExportOp.bl_idname, text='Irrlicht (.irr/.irrmesh)')
        
#=============================================================================
#                              r e g i s t e r
#=============================================================================
def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)
    _loadConfig()
    _registerIrrbProperties()
    
#=============================================================================
#                            u n r e g i s t e r
#=============================================================================
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)

#=============================================================================
#                            I G U I D e b u g    
#=============================================================================
class IGUIDebug:

    def __init__(self):
        self.canceled = False

    def setStatus(self, status):
        print('GUI.setStatus()', status)

    def updateStatus(self, status):
        print('GUI.updateStatus()', status)

    def isExportCanceled(self):
        #print('GUI.isExportCanceled()')
        return self.canceled

#=============================================================================
#                            I G U I P a n e l    
#=============================================================================
class IGUIPanel(IGUIDebug):

    def __init__(self):
        pass

#=============================================================================
#                         I G U I F i l e P a n e l    
#=============================================================================
class IGUIFilePanel(IGUIDebug):

    def __init__(self):
        pass

#=============================================================================
#                            i F i l e N a m e
#=============================================================================
class iFilename:
    def __init__(self, fullPath):
        self.fullPath = fullPath
        self.dirPath = Blender.sys.dirname(fullPath)
        self.fileName = Blender.sys.basename(fullPath)
        self.file, self.ext = Blender.sys.splitext(self.fileName)
        if self.file == 'Untitled':
            self.file += self.ext
            self.ext = ''

        self.dirParts = []
        part = ''
        for c in self.dirPath:
            if (c == '/') or (c == '\\'):
                self.dirParts.append(part)
                part = ''
            else:
                part += c

    #=========================================================================
    #                              _ i w r i t e
    #=========================================================================
    def _iwrite(self, file, indent, tag, name, value):
        svalue = '?enum?'
        if tag == 'enum':
            svalue = value
        elif tag == 'color':
            svalue = del2SColor(value)
        elif tag == 'float':
            svalue = float2str(value)
        elif tag == 'texture':
            svalue = value
        elif tag == 'int':
            svalue = int2str(value)
        elif tag == 'bool':
            svalue = bool2str(value)

        out = indent + '<{} name="{}" value="{}"/>\n'.format(tag, name, svalue)
        file.write(out)

    def printDebug(self):
        print('fullPath', self.fullPath)
        print('dirPath', self.dirPath)
        print('fileName', self.fileName)
        print('file', self.file)
        print('ext', self.ext)
        print('dirParts', self.dirParts)

    def getBaseName(self):
        return self.file

    def setExtension(self, ext):
        self.ext = ext

#=============================================================================
#                              i M a t e r i a l
#=============================================================================
class iMaterial:

    #=========================================================================
    #                               _ i n i t _
    #=========================================================================
    def __init__(self, bobject, name, exporter, bmaterial, face=None):
        self.bobject = bobject
        self.bmesh = bobject.data
        self.bmaterial = bmaterial
        self.bimages = []
        self.name = name
        self.exporter = exporter
        self.useVertexColor = True
        self.vtCustom = None

        #
        # Default attributes
        #
        self.attributes = copy.deepcopy(defMaterialAttributes)

        self.attributes['FogEnable'] = False

        if exporter.gContext.scene.world and \
           exporter.gContext.scene.world.mist_settings.use_mist:
            self.attributes['FogEnable'] = True

        self._updateFromBlenderMaterial(self.bmaterial)

        if face:
            for i in range(0, 4):
                t = bmaterial.texture_slots[i]
                if t == None:
                    break
                if t.use and t.texture.type == 'IMAGE' and t.texture.image != None:
                    self.setTexture(t.texture.image, i + 1)

        if self.attributes['Type'].lower() == 'trans_alphach':
            self.attributes['MaterialTypeParam'] = 0.000001

    #=========================================================================
    #                              _ i w r i t e
    #=========================================================================
    def _iwrite(self, file, indent, tag, name, value):
        svalue = '?enum?'
        if tag == 'enum':
            svalue = value
        elif tag == 'color':
            svalue = del2SColor(value)
        elif tag == 'float':
            svalue = float2str(value)
        elif tag == 'texture':
            svalue = value
        elif tag == 'int':
            svalue = int2str(value)
        elif tag == 'bool':
            svalue = bool2str(value)

        out = indent + '<{} name="{}" value="{}"/>\n'.format(tag, name, svalue)
        file.write(out)
        
    #=========================================================================
    #            _ u p d a t e F r o m B l e n d e r M a t e r i a l
    #=========================================================================
    # Upon entry it is expected that "self.attributes" has already been
    # set to "Defaults".
    def _updateFromBlenderMaterial(self, bmat):
        if bmat == None:
            return

        self.useVertexColor = bmat.use_vertex_color_paint

        for mat in irrMaterialTypes:
            if mat[0] == bmat.irrb_type:
                self.attributes['Type'] = mat[1]
                break

        self.attributes['AmbientColor'] = rgb2DelStr(bmat.irrb_ambient)
        if bmat.irrb_link_diffuse:
            self.attributes['DiffuseColor'] = rgb2DelStr(bmat.diffuse_color)
        else:
            self.attributes['DiffuseColor'] = rgb2DelStr(bmat.irrb_diffuse)
            
        self.attributes['EmissiveColor'] = rgb2DelStr(bmat.irrb_emissive)
        self.attributes['SpecularColor'] = rgb2DelStr(bmat.specular_color)
        self.attributes['Lighting'] = int(bmat.irrb_lighting)
        self.attributes['Shininess'] = bmat.irrb_shininess
        self.attributes['MaterialTypeParam'] = bmat.irrb_param1
        self.attributes['MaterialTypeParam2'] = bmat.irrb_param2
        self.attributes['Thickness'] = bmat.irrb_thickness
        self.attributes['GouraudShading'] = int(bmat.irrb_gouraud)
        self.attributes['ZWriteEnable'] = int(bmat.irrb_zwrite_enable)
        self.attributes['BackfaceCulling'] = int(bmat.irrb_backcull)
        self.attributes['FrontfaceCulling'] = int(bmat.irrb_frontcull)
        self.attributes['FogEnable'] = bmat.irrb_fog
        self.attributes['NormalizeNormals'] = int(bmat.irrb_normalize_normals)
        self.attributes['UseMipMaps'] = int(bmat.irrb_use_mipmaps)
        self.attributes['ZBuffer'] = E_COMPARISON_FUNC[bmat.irrb_zbuffer]
        self.attributes['AntiAliasing'] = \
            E_ANTI_ALIASING_MODE[bmat.irrb_antialiasing]

        cmask = 0
        if bmat.irrb_color_mask_alpha:
            cmask = 1
        if bmat.irrb_color_mask_red:
            cmask |= 2
        if bmat.irrb_color_mask_green:
            cmask |= 4
        if bmat.irrb_color_mask_blue:
            cmask |= 8
        self.attributes['ColorMask'] = cmask

        for i in range(1, 5):
            l = 'Layer{}'.format(i)
            self.attributes[l]['TextureWrapU'] = \
                E_TEXTURE_CLAMP[getattr(bmat, 'irrb_layer{}_wrapu'.format(i))]
            self.attributes[l]['TextureWrapV'] = \
                E_TEXTURE_CLAMP[getattr(bmat, 'irrb_layer{}_wrapv'.format(i))]
            filter = getattr(bmat, 'irrb_layer{}_filter'.format(i))
            if filter == 'FLT_NONE':
                self.attributes[l]['BilinearFilter'] = 0
                self.attributes[l]['TrilinearFilter'] = 0
            elif filter == 'FLT_BILINEAR':
                self.attributes[l]['BilinearFilter'] = 1
                self.attributes[l]['TrilinearFilter'] = 0
            else:
                self.attributes[l]['BilinearFilter'] = 1
                self.attributes[l]['TrilinearFilter'] = 0

            self.attributes[l]['AnisotropicFilter'] = \
                getattr(bmat, 'irrb_layer{}_anisotropic_value'.format(i))

            self.attributes[l]['LODBias'] = \
                getattr(bmat, 'irrb_layer{}_lodbias'.format(i))

    #=========================================================================
    #                               g e t T y p e
    #=========================================================================
    def getType(self):
        return 'DefaultMaterial'

    #=========================================================================
    #                         g e t V e r t e x T y p e
    #=========================================================================
    def getVertexType(self):
        if self.vtCustom != None:
            return self.vtCustom

        info = getIrrMaterial(self.attributes['Type'])
        if info != None:
            return info[3]
        else:
            return EVT_STANDARD

    #=========================================================================
    #                             g e t D i f f u s e
    #=========================================================================
    def getDiffuse(self):
        return self.attributes['DiffuseColor']

    #=========================================================================
    #                             g e t I m a g e s
    #=========================================================================
    def getImages(self):
        return self.bimages

    #=========================================================================
    #                                w r i t e
    #=========================================================================
    def write(self, file, header='material', indent=6, textureCount=4):
        i1 = indent * ' '
        i2 = i1 + '   '
        file.write(i1 + '<{} bmat="{}">\n'.format(header, self.name))
        mtype = self.attributes['Type']
        if mtype == 'custom':
            mtype = self.bmaterial.irrb_custom_name
            
        self._iwrite(file, i2, 'enum', 'Type', mtype)
        self._iwrite(file, i2, 'color', 'Ambient',
            self.attributes['AmbientColor'])
        self._iwrite(file, i2, 'color', 'Diffuse',
            self.attributes['DiffuseColor'])
        self._iwrite(file, i2, 'color', 'Emissive',
            self.attributes['EmissiveColor'])
        self._iwrite(file, i2, 'color', 'Specular',
            self.attributes['SpecularColor'])
        self._iwrite(file, i2, 'float', 'Shininess',
            self.attributes['Shininess'])
        self._iwrite(file, i2, 'float', 'Param1',
            self.attributes['MaterialTypeParam'])
        self._iwrite(file, i2, 'float', 'Param2',
            self.attributes['MaterialTypeParam2'])
        self._iwrite(file, i2, 'bool', 'Wireframe',
            self.attributes['WireFrame'])
        self._iwrite(file, i2, 'bool', 'GouraudShading',
            self.attributes['GouraudShading'])
        self._iwrite(file, i2, 'bool', 'Lighting', self.attributes['Lighting'])
        self._iwrite(file, i2, 'bool', 'ZWriteEnable',
            self.attributes['ZWriteEnable'])
        self._iwrite(file, i2, 'int', 'ZBuffer', self.attributes['ZBuffer'])
        self._iwrite(file, i2, 'bool', 'BackfaceCulling',
            self.attributes['BackfaceCulling'])
        self._iwrite(file, i2, 'bool', 'FrontfaceCulling',
            self.attributes['FrontfaceCulling'])
        self._iwrite(file, i2, 'bool', 'FogEnable',
            self.attributes['FogEnable'])
        self._iwrite(file, i2, 'bool', 'NormalizeNormals',
            self.attributes['NormalizeNormals'])
        self._iwrite(file, i2, 'bool', 'UseMipMaps',
            self.attributes['UseMipMaps'])
        self._iwrite(file, i2, 'int', 'AntiAliasing',
            self.attributes['AntiAliasing'])
        self._iwrite(file, i2, 'int', 'ColorMask',
            self.attributes['ColorMask'])

        for i in range(1, textureCount + 1):
            lname = 'Layer{}'.format(i)
            tex = flattenPath(self.attributes[lname]['Texture'])
            self._iwrite(file, i2, 'texture', 'Texture{}'.format(i), tex)
            self._iwrite(file, i2, 'enum', 'TextureWrapU{}'.format(i),
                self.attributes[lname]['TextureWrapU'])
            self._iwrite(file, i2, 'enum', 'TextureWrapV{}'.format(i),
                self.attributes[lname]['TextureWrapV'])
            self._iwrite(file, i2, 'bool', 'BilinearFilter{}'.format(i),
                self.attributes[lname]['BilinearFilter'])
            self._iwrite(file, i2, 'bool', 'TrilinearFilter{}'.format(i),
                self.attributes[lname]['TrilinearFilter'])
            self._iwrite(file, i2, 'int', 'AnisotropicFilter{}'.format(i),
                self.attributes[lname]['AnisotropicFilter'])
            self._iwrite(file, i2, 'int', 'LODBias{}'.format(i),
                self.attributes[lname]['LODBias'])

        file.write(i1 + '</{}>\n'.format(header))

    #=========================================================================
    #                           s e t T e x t u r e
    #=========================================================================
    def setTexture(self, bImage, layerNumber):
        self.bimages.append(bImage)

        try:
            texFile = self.exporter.getImageFileName(bImage, 0)
        except:
            texFile = '** error accessing {} **'.format(bImage.name)

        layerName = 'Layer{}'.format(layerNumber)
        self.attributes[layerName]['Texture'] = texFile

#=============================================================================
#                                i S c e n e
#=============================================================================
class iScene:

    #=========================================================================
    #                               _ i n i t _
    #=========================================================================
    def __init__(self, exporter):
        self.exporter = exporter

    #=========================================================================
    #                              _ i w r i t e
    #=========================================================================
    def _iwrite(self, file, tag, name, value, indent):
        svalue = '?enum?'
        if tag == 'enum':
            svalue = value
        elif tag == 'color':
            svalue = del2SColor(value)
        elif tag == 'float':
            svalue = float2str(value)
        elif tag == 'texture':
            svalue = value
        elif tag == 'int':
            svalue = int2str(value)
        elif tag == 'bool':
            svalue = bool2str(value)

        out = indent + '<{} name="{}" value="{}"/>\n'.format(tag, name,
            svalue)
        file.write(out)

    #=========================================================================
    #                    _ w r i t e S B I m a g e A t t r i b u t e s
    #=========================================================================
    def _writeSBImageAttributes(self, file, indent, mat, bImage,
        lightingOverride=None):

        i2 = indent + '    '
        imageName = self.exporter.getImageFileName(bImage, 0)
        file.write(indent + '<attributes>\n')
        self._iwrite(file, 'enum', 'Type', mat.attributes['Type'], i2)
        self._iwrite(file, 'color', 'Ambient',
            mat.attributes['AmbientColor'], i2)
        self._iwrite(file, 'color', 'Diffuse',
            mat.attributes['DiffuseColor'], i2)
        self._iwrite(file, 'color', 'Emissive',
            mat.attributes['EmissiveColor'], i2)
        self._iwrite(file, 'color', 'Specular',
            mat.attributes['SpecularColor'], i2)
        self._iwrite(file, 'float', 'Shininess',
            mat.attributes['Shininess'], i2)
        self._iwrite(file, 'float', 'Param1',
            mat.attributes['MaterialTypeParam'], i2)
        self._iwrite(file, 'float', 'Param2',
            mat.attributes['MaterialTypeParam2'], i2)
        self._iwrite(file, 'bool', 'Wireframe',
            mat.attributes['WireFrame'], i2)
        self._iwrite(file, 'bool', 'GouraudShading',
            mat.attributes['GouraudShading'], i2)
        if lightingOverride == None:
            self._iwrite(file, 'bool', 'Lighting',
                mat.attributes['Lighting'], i2)
        else:
            self._iwrite(file, 'bool', 'Lighting', lightingOverride, i2)

        self._iwrite(file, 'bool', 'ZWriteEnable',
            mat.attributes['ZWriteEnable'], i2)
        self._iwrite(file, 'int', 'ZBuffer',
            mat.attributes['ZBuffer'], i2)
        self._iwrite(file, 'bool', 'BackfaceCulling',
            mat.attributes['BackfaceCulling'], i2)
        self._iwrite(file, 'bool', 'FogEnable',
            mat.attributes['FogEnable'], i2)
        self._iwrite(file, 'bool', 'NormalizeNormals',
            mat.attributes['NormalizeNormals'], i2)
        self._iwrite(file, 'int', 'ColorMask',
            mat.attributes['ColorMask'], i2)
        self._iwrite(file, 'int', 'AntiAliasing',
            mat.attributes['AntiAliasing'], i2)
        # override mipmaps for sky boxes/domes
        self._iwrite(file, 'bool', 'UseMipMaps', False, i2)

        self._iwrite(file, 'texture', 'Texture1', flattenPath(imageName), i2)
        self._iwrite(file, 'enum', 'TextureWrapU1',
            mat.attributes['Layer1']['TextureWrapU'], i2)
        self._iwrite(file, 'enum', 'TextureWrapV1',
            mat.attributes['Layer1']['TextureWrapV'], i2)
        self._iwrite(file, 'bool', 'BilinearFilter1',
            mat.attributes['Layer1']['BilinearFilter'], i2)
        self._iwrite(file, 'bool', 'TrilinearFilter1',
            mat.attributes['Layer1']['TrilinearFilter'], i2)
        if self.exporter.gIrrlichtVersion >= '1.7':
            self._iwrite(file, 'int', 'AnisotropicFilter1',
                mat.attributes['Layer1']['AnisotropicFilter'], i2)
        else:
            self._iwrite(file, 'bool', 'AnisotropicFilter1',
                mat.attributes['Layer1']['AnisotropicFilter'], i2)
        file.write(indent + '</attributes>\n')

    #=========================================================================
    #                       w r i t e S c e n e H e a d e r
    #=========================================================================
    def writeSceneHeader(self, file, scene, physicsEnabled):
        amb = (0.0, 0.0, 0.0)
        if scene.world:
            amb = scene.world.ambient_color

        scolor = _formatFloats(((amb[0],
            amb[1], amb[2], 1.0)))

        file.write('<?xml version="1.0"?>\n')
        file.write('<!-- Created {} by irrb {} - "Irrlicht/Blender ' \
                'Exporter" -->\n'.format(datetime2str(time.localtime()),
                getversion()))
        file.write('<irr_scene>\n')
        file.write('   <attributes>\n')
        file.write('      <string name="Name" value="root"/>\n')
        file.write('      <int name="Id" value="-1"/>\n')
        file.write('      <vector3d name="Position" value="0, ' \
                '0, 0"/>\n')
        file.write('      <vector3d name="Rotation" value="0, ' \
                '0, 0"/>\n')
        file.write('      <vector3d name="Scale" value="1, ' \
                '1, 1"/>\n')
        file.write('      <colorf name="AmbientLight" value="{}"/>\n'.format
            (scolor))
        file.write('      <bool name="AutomaticCulling" value="true"/>\n')
        file.write('      <bool name="DebugDataVisible" value="false"/>\n')
        file.write('      <bool name="IsDebugObject" value="false"/>\n')
        file.write('      <bool name="Visible" value="true"/>\n')

        # mist/fog enabled
        if scene.world and scene.world.mist_settings.use_mist:
            mist = scene.world.mist_settings
            mistType = mist.falloff
            if mistType == 'QUADRATIC':
                sMistType = 'FogExp'
            elif mistType == 'LINEAR':
                sMistType = 'FogLinear'
            else:  # 'INVERSE_QUADRATIC'
                sMistType = 'FogExp2'
            file.write('      <enum name="FogType" ' \
                'value="{}"/>\n'.format(sMistType))
            file.write('      <float name="FogStart" ' \
                'value="{:.6f}"/>\n'.format(mist.start))
            file.write('      <float name="FogEnd" ' \
                'value="{:.6f}"/>\n'.format(mist.depth))
            file.write('      <float name="FogHeight" ' \
                'value="{:.6f}"/>\n'.format(mist.height))
            file.write('      <float name="FogDensity" ' \
                'value="{:.6f}"/>\n'.format(mist.intensity))
            fcolor = scene.world.horizon_color
            file.write('      <colorf name="FogColor" ' \
                'value="{:.6f}, {:.6f}, {:.6f}, {:.6f}"/>' \
                '\n'.format(fcolor[0], fcolor[1], fcolor[2], 1.0))
            file.write('      <bool name="FogPixel" value="false"/>\n')
            file.write('      <bool name="FogRange" value="false"/>\n')

        file.write('   </attributes>\n')

        writeUserData(file, '   ', 6 * ' ', scene, False)
        if physicsEnabled:
            physicsEnabled = 'true'
        else:
            physicsEnabled = 'false'
        file.write('         <bool name="Physics.Enabled" ' \
            'value="{}"/>\n'.format(physicsEnabled))
        file.write('         <float name="Gravity" ' \
            'value="{}"/>\n'.format(_formatFloats((scene.gravity.z,))))

        col = (0.0, 0.0, 0.0)
        try:
            col = scene.world.horizon_color
        except:
            pass
        file.write('         <colorf name="BackgroundColor" ' \
            'value="{}"/>' \
            '\n'.format(_formatFloats((col[0], col[1], col[2], 1.0))))

        file.write('      </attributes>\n')
        file.write('   </userData>\n')

    #=========================================================================
    #                      w r i t e S c e n e F o o t e r
    #=========================================================================
    def writeSceneFooter(self, file):
        file.write('</irr_scene>\n')

    #=========================================================================
    #                     w r i t e S T D A t t r i b u t e s
    #=========================================================================
    def writeSTDAttributes(self, file, i1, i2, bObject, ipos, irot, iscale,
        cullDefault=None):
        cullopts = {'CULL_BOX': 'box', 'CULL_FRUSTUM_BOX': 'frustum_box',
            'CULL_FRUSTUM_SPHERE': 'sphere_box',
            'CULL_OCCLUSION_QUERY': 'occ_query'}

        culling = cullDefault
        if culling == None:
            culling = cullopts[bObject.irrb_node_culling]

        spos = _formatFloats(ipos)
        srot = _formatFloats(irot)
        sscale = _formatFloats(iscale)

        file.write(i1 + '<attributes>\n')

        file.write(i2 + '<string name="Name" ' \
            'value="{}"/>\n'.format(bObject.name))

        self._iwrite(file, 'int', 'Id', bObject.irrb_node_id, i2)

        self._iwrite(file, 'bool', 'Visible', 1, i2)
        
        file.write(i2 + '<vector3d name="Position" ' \
            'value="{}"/>\n'.format(spos))
        file.write(i2 + '<vector3d name="Rotation" ' \
            'value="{}"/>\n'.format(srot))

        if (bObject.type == 'MESH') or (bObject.type == 'EMPTY'):
            file.write(i2 + '<vector3d name="Scale" ' \
                'value="{}"/>\n'.format(sscale))

            self._iwrite(file, 'enum', 'AutomaticCulling', culling, i2)
            self._iwrite(file, 'bool', 'DebugDataVisible', 0, i2)
            self._iwrite(file, 'bool', 'IsDebugObject', 0, i2)
            self._iwrite(file, 'bool', 'ReadOnlyMaterials', 0, i2)

    #=========================================================================
    #                       w r i t e M e s h O b j e c t
    #=========================================================================
    def writeMeshObject(self, file, meshFileName, bObject, level,
        physicsEnabled, animated=False):
        i1 = getIndent(level, 3)
        i2 = getIndent(level, 6)
        i3 = getIndent(level, 9)

        ipos = b2iPosition(bObject)
        irot = b2iRotation(bObject)
        iscale = b2iScale(bObject.scale)

        self.writeSTDAttributes(file, i1, i2, bObject, ipos, irot, iscale)

        file.write(i2 + '<string name="Mesh" value="{0}"/>\n'.format
                (flattenPath(meshFileName)))

        if bObject.irrb_node_octree:
            file.write(i2 + '<int name="MinimalPolysPerNode" ' \
            'value="{}"/>\n'.format(bObject.irrb_node_octree_polys))

        itype = bObject.irrb_node_type
        if itype == NT_WATERSURFACE:
            sout = '<float name="WaveLength" ' \
                'value="{:.2f}"/>\n'.format(bObject.irrb_water_wavelength)
            file.write(i2 + sout)

            sout = '<float name="WaveSpeed" ' \
                'value="{:.2f}"/>\n'.format(bObject.irrb_water_wavespeed)
            file.write(i2 + sout)

            sout = '<float name="WaveHeight" ' \
                'value="{:.2f}"/>\n'.format(bObject.irrb_water_waveheight)
            file.write(i2 + sout)

        dict_hint = {'EHM_NEVER': 'never', 'EHM_STATIC': 'static',
            'EHM_DYNAMIC': 'dynamic', 'EHM_STREAM': 'stream'}
        hint = dict_hint[bObject.irrb_node_hwhint]

        dict_hintbt = {'EBT_NONE': 'none', 'EBT_VERTEX': 'vertex',
            'EHM_INDEX': 'index', 'EHM_VERTEX_AND_INDEX': 'vertexindex'}
        hintbt = dict_hintbt[bObject.irrb_node_hwhint_bt]

        sout = '<enum name="HardwareMappingHint" ' \
                'value="{}"/>\n'.format(hint)
        file.write(i2 + sout)

        sout = '<enum name="HardwareMappingBufferType" ' \
                'value="{}"/>\n'.format(hintbt)
        file.write(i2 + sout)

        file.write(i1 + '</attributes>\n')

        if physicsEnabled == 0:
            writeUserData(file, i1, i2, bObject, True)
            return

        writeUserData(file, i1, i2, bObject, False)
        ctype = 'none'

        ctype = bObject.game.physics_type
        if ctype in irrBodyTypes.keys():
            ctype = irrBodyTypes[ctype]
        else:
            ctype = 'none'

        sout = '<string name="Physics.BodyType" value="{}"/>\n'.format(ctype)
        file.write(i3 + sout)

        sShapeType = bObject.game.collision_bounds_type

        sout = '<string name="Physics.BodyShape" ' \
            'value="{}"/>\n'.format(sShapeType)
        file.write(i3 + sout)

        if bObject.hide_render:
            sout = '<bool name="Physics.Visible" value="false"/>\n'
        else:
            sout = '<bool name="Physics.Visible" value="true"/>\n'
        file.write(i3 + sout)

        mass = 0.0
        if ctype == 'dynamic' or ctype == 'rigid':
            mass = bObject.game.mass

        sout = '<float name="Physics.Mass" ' \
            'value="{:.2f}"/>\n'.format(mass)
        file.write(i3 + sout)

        sout = '<float name="Physics.Radius" ' \
            'value="{:.2f}"/>\n'.format(bObject.game.radius)
        file.write(i3 + sout)

        if bObject.game.use_ghost:
            sout = '<bool name="Physics.Ghost" value="true"/>\n'
            file.write(i3 + sout)

        if bObject.game.use_actor:
            sout = '<bool name="Physics.Actor" value="true"/>\n'
            file.write(i3 + sout)

        # extract friction & restitution from 1st material
        # may need to use bObject.game.material_physics...
        mesh = bObject.data
        if (mesh.materials != None) and (len(mesh.materials) > 0):
            try:
                mat = mesh.materials[0]
                if mat != None:
                    sout = '<float name="Physics.Friction" ' \
                        'value="{:.2f}"/>\n'.format(mat.physics.friction)
                    file.write(i3 + sout)

                    sout = '<float name="Physics.Restitution" ' \
                        'value="{:.2f}"/>\n'.format(mat.physics.elasticity)
                    file.write(i3 + sout)
            except:
                pass

        count = _getConstraintCount(bObject)
        if count > 0:
            sout = '<int name="Physics.Constraints" ' \
                'value="{}"/>\n'.format(count)
            file.write(i3 + sout)

            count = 1
            for c in bObject.constraints:
                if c.type == 'RIGID_BODY_JOINT':
                    sout = '<string name="Constraint{}.Name" ' \
                        'value="{}"/>\n'.format(count, c.name)
                    file.write(i3 + sout)
                    sout = '<string name="Constraint{}.Type" ' \
                        'value="{}"/>\n'.format(count, c.pivot_type)
                    file.write(i3 + sout)

                    if c.target:
                        sout = '<string name="Constraint{}.Target" ' \
                            'value="{}"/>\n'.format(count, c.target.name)
                        file.write(i3 + sout)

                    if c.child:
                        sout = '<string name="Constraint{}.Child" ' \
                            'value="{}"/>\n'.format(count, c.child.name)
                        file.write(i3 + sout)

                    satt = '{:.6f} {:.6f} {:.6f}'.format(c.pivot_x,
                    c.pivot_z, c.pivot_y)
                    file.write(i3 + '<vector3d name="Constraint{}.Pivot" ' \
                        'value="{}"/>\n'.format(count, satt))

                    satt = '{:.6f} {:.6f} {:.6f}'.format(c.axis_x,
                    c.axis_y, c.axis_z)
                    file.write(i3 + '<vector3d name="Constraint{}.Axis" ' \
                        'value="{}"/>\n'.format(count, satt))

                    limits = 0
                    if c.use_limit_x:
                        limits |= (1 << 0)
                    if c.use_limit_y:
                        limits |= (1 << 1)
                    if c.use_limit_z:
                        limits |= (1 << 2)
                    writeL = False
                    if limits > 0:
                        writeL = True

                    if c.use_angular_limit_x:
                        limits |= (1 << 4)
                    if c.use_angular_limit_y:
                        limits |= (1 << 5)
                    if c.use_angular_limit_z:
                        limits |= (1 << 6)

                    writeAL = False
                    if limits > 4:
                        writeAL = True

                    if limits > 0:
                        file.write(i3 + '<int name="Constraint{}.Limits" ' \
                        'value="{}"/>\n'.format(count, limits))

                    if writeL:
                        satt = '{:.6f} {:.6f} {:.6f}'.format(
                            c.limit_generic_min[0], c.limit_generic_min[1],
                            c.limit_generic_min[2])
                        file.write(i3 + '<vector3d name="Constraint{}.' \
                            'LimitsMin" value="{}"/>\n'.format(count, satt))

                        satt = '{:.6f} {:.6f} {:.6f}'.format(
                            c.limit_generic_max[0], c.limit_generic_max[1],
                            c.limit_generic_max[2])
                        file.write(i3 + '<vector3d name="Constraint{}.' \
                            'LimitsMax" value="{}"/>\n'.format(count, satt))

                    if writeAL:
                        satt = '{:.6f} {:.6f} {:.6f}'.format(
                            c.limit_generic_min[3], c.limit_generic_min[4],
                            c.limit_generic_min[5])
                        file.write(i3 + '<vector3d name="Constraint{}.' \
                            'LimitsAngularMin" value="{}"/>\n'.format(count,
                            satt))

                        satt = '{:.6f} {:.6f} {:.6f}'.format(
                            c.limit_generic_max[3], c.limit_generic_max[4],
                            c.limit_generic_max[5])
                        file.write(i3 + '<vector3d name="Constraint{}.' \
                            'LimitsAngularMax" value="{}"/>\n'.format(count,
                            satt))

                count += 1

        file.write(i2 + '</attributes>\n')
        file.write(i1 + '</userData>\n')

    #=========================================================================
    #                       w r i t e E m p t y O b j e c t
    #=========================================================================
    def writeEmptyObject(self, file, bObject, level):
        i1 = getIndent(level, 3)
        i2 = getIndent(level, 6)

        ipos = b2iPosition(bObject)
        irot = b2iRotation(bObject)
        iscale = b2iScale(bObject.scale)

        self.writeSTDAttributes(file, i1, i2, bObject, ipos, irot, iscale)

        file.write(i1 + '</attributes>\n')

        writeUserData(file, i1, i2, bObject)

    #=========================================================================
    #                     w r i t e N o d e H e a d
    #=========================================================================
    def writeNodeHead(self, file, level, ntype):
        indent = getIndent(level)
        file.write(indent + '<node type="{}">\n'.format(ntype))

    #=========================================================================
    #                     w r i t e N o d e T a i l
    #=========================================================================
    def writeNodeTail(self, file, level):
        indent = getIndent(level)
        file.write(indent + '</node>\n')

    #=========================================================================
    #                      w r i t e L i g h t N o d e D a t a
    #=========================================================================
    def writeLightNodeData(self, file, bObject, level):
        i1 = getIndent(level, 3)
        i2 = getIndent(level, 6)

        ipos = b2iPosition(bObject)
        irot = b2iRotation(bObject)
        iscale = b2iScale(bObject.scale)

        self.writeSTDAttributes(file, i1, i2, bObject, ipos, irot, iscale)

        light = bObject.data

        lightType = 'Point'
        if bObject.irrb_light_type == 'ILT_SPOT':
            lightType = 'Spot'
        elif bObject.irrb_light_type == 'ILT_DIRECTIONAL':
            lightType = 'Directional'

        file.write(i2 + '<enum name="LightType" ' \
            'value="{}"/>\n'.format(lightType))

        color = bObject.irrb_light_ambient
        tcolor = '{}'.format(_formatFloats((color[0],
            color[1], color[2], 1.0)))
        file.write(i2 + '<colorf name="AmbientColor" ' \
            'value="{}"/>\n'.format(tcolor))

        color = light.color        
        tcolor = '{}'.format(_formatFloats((color[0],
            color[1], color[2], 1.0)))
        file.write(i2 + '<colorf name="DiffuseColor" ' \
            'value="{}"/>\n'.format(tcolor))
        
        color = bObject.irrb_light_specular
        tcolor = '{}'.format(_formatFloats((color[0],
            color[1], color[2], 1.0)))
        file.write(i2 + '<colorf name="SpecularColor" ' \
            'value="{}"/>\n'.format(tcolor))

        attvalue = 0.0
        if light.energy != 0.000000:
            attvalue = 0.5 / light.energy
                        
        satt = _formatFloats(bObject.irrb_light_attenuation)
        file.write(i2 + '<vector3d name="Attenuation" ' \
            'value="{}"/>\n'.format(satt))

        file.write(i2 + '<float name="Radius" value="{:.2f}"/>\n'.format
                (bObject.irrb_light_radius))
        
        file.write(i2 + '<float name="OuterCone" value="{:.2f}"/>\n'.format
                (bObject.irrb_light_outercone))
        
        file.write(i2 + '<float name="InnerCone" value="{:.2f}"/>\n'.format
                (bObject.irrb_light_innercone))
        
        shadows = 'false'
        if bObject.irrb_light_castshadows:
            shadows = 'true'
        file.write(i2 + '<bool name="CastShadows" value="{}"/>\n'.format
                   (shadows))
        
        file.write(i1 + '</attributes>\n')

        writeUserData(file, i1, i2, bObject)

    #=========================================================================
    #                      w r i t e C a m e r a N o d e D a t a
    #=========================================================================
    def writeCameraNodeData(self, file, bObject, level):
        i1 = getIndent(level, 3)
        i2 = getIndent(level, 6)

        ipos = b2iPosition(bObject)
        irot = b2iRotation(bObject)
        iscale = b2iScale(bObject.scale)

        self.writeSTDAttributes(file, i1, i2, bObject, ipos, irot, iscale)

        #
        # calculate target based on x,z rotation
        #
        camera = bObject.data
        starget = _formatFloats(bObject.irrb_cam_target)
        supvector = _formatFloats(bObject.irrb_cam_upvector)

        #
        # override fov & aspect with logic properties if defined
        #
        fov = 2 * math.atan(16.0 / camera.lens)
        fov = bObject.irrb_cam_fov
        aspect = bObject.irrb_cam_aspect


        file.write(i2 + '<vector3d name="Target" ' \
            'value="{}"/>\n'.format(starget))
        file.write(i2 + '<vector3d name="UpVector" ' \
            'value="{}"/>\n'.format(supvector))
        file.write(i2 + '<float name="Fovy" value="{}"/>\n'.format(_formatFloats((fov,))))
        file.write(i2 + '<float name="Aspect" ' \
            'value="{}"/>\n'.format(_formatFloats((aspect,))))
        file.write(i2 + '<float name="ZNear" value="{}"/>\n'.format
                (_formatFloats((camera.clip_start,))))
        file.write(i2 + '<float name="ZFar" value="{}"/>\n'.format
                (_formatFloats((camera.clip_end,))))
        
        binding = 'false'
        if bObject.irrb_cam_bindtarget:
            binding = 'true'
        file.write(i2 + '<bool name="Binding" value="{}"/>\n'.format
                   (binding))

        file.write(i1 + '</attributes>\n')

        writeUserData(file, i1, i2, bObject)

    #=========================================================================
    #                     w r i t e S k y B o x N o d e D a t a
    #=========================================================================
    def writeSkyBoxNodeData(self, file, bObject, sImages, level):
        if bObject.type != 'MESH':
            return

        material = iMaterial(bObject, 'skybox', self.exporter, None)
        topImage = sImages['top'].image
        botImage = sImages['bottom'].image
        leftImage = sImages['left'].image
        rightImage = sImages['right'].image
        frontImage = sImages['front'].image
        backImage = sImages['back'].image

        i1 = getIndent(level, 3)
        i2 = getIndent(level, 6)

        ipos = (0.0, 0.0, 0.0)
        irot = (0.0, 0.0, 0.0)
        iscale = (1.0, 1.0, 1.0)
        self.writeSTDAttributes(file, i1, i2, bObject, ipos, irot, iscale,
            'false')

        file.write(i1 + '</attributes>\n')
        file.write(i1 + '<materials>\n')

        material.attributes['Type'] = 'solid'
        self._writeSBImageAttributes(file, i2, material, frontImage, False)
        self._writeSBImageAttributes(file, i2, material, rightImage, False)
        self._writeSBImageAttributes(file, i2, material, backImage, False)
        self._writeSBImageAttributes(file, i2, material, leftImage, False)
        self._writeSBImageAttributes(file, i2, material, topImage, False)
        self._writeSBImageAttributes(file, i2, material, botImage, False)

        file.write(i1 + '</materials>\n')

    #=========================================================================
    #                  w r i t e S k y D o m e N o d e D a t a
    #=========================================================================
    def writeSkyDomeNodeData(self, file, bObject, sImage, level):
        if bObject.type != 'MESH':
            return

        bMesh = bObject.data
        bMaterial = None
        if len(bMesh.materials) > 0:
            bMaterial = bMesh.materials[0]
        material = iMaterial(bObject, 'skydome', self.exporter, bMaterial)

        i1 = getIndent(level, 3)
        i2 = getIndent(level, 6)

        ipos = (0.0, 0.0, 0.0)
        irot = (0.0, 0.0, 0.0)
        iscale = (1.0, 1.0, 1.0)
        self.writeSTDAttributes(file, i1, i2, bObject, ipos, irot, iscale,
            'false')

        self._iwrite(file, 'int', 'HorizontalResolution',
            bObject.irrb_dome_hres, i2)

        self._iwrite(file, 'int', 'VerticalResolution',
            bObject.irrb_dome_vres, i2)

        self._iwrite(file, 'float', 'TexturePercentage',
            bObject.irrb_dome_texpct, i2)

        self._iwrite(file, 'float', 'SpherePercentage',
            bObject.irrb_dome_spherepct, i2)

        self._iwrite(file, 'float', 'Radius',
            bObject.irrb_dome_radius, i2)

        # warn if radius is larger than active camera far plane - skydome
        # won't be visible or only partially visible.
        if self.exporter.gContext.scene.camera and \
            (self.exporter.gContext.scene.camera.data.clip_end <= \
             bObject.irrb_dome_radius):
            self.exporter.gGUI.updateStatus('Warning: Skydome radius is ' \
                'larger than the camera far plane.')

        file.write(i1 + '</attributes>\n')
        file.write(i1 + '<materials>\n')

        self._writeSBImageAttributes(file, i2, material, sImage, False)
        file.write(i1 + '</materials>\n')

    #=========================================================================
    #              w r i t e V o l u m e L i g h t N o d e D a t a
    #=========================================================================
    def writeVolumeLightNodeData(self, file, bObject, level):
        if bObject.type != 'MESH':
            return

        #material = iMaterial(bObject, 'skydome', self.exporter, None)

        i1 = getIndent(level, 3)
        i2 = getIndent(level, 6)

        ipos = b2iPosition(bObject)
        irot = b2iRotation(bObject)
        iscale = b2iScale(bObject.scale)

        self.writeSTDAttributes(file, i1, i2, bObject, ipos, irot, iscale,
            'false')

        self._iwrite(file, 'float', 'lpDistance',
            bObject.irrb_volight_distance, i2)

        self._iwrite(file, 'int', 'subDivideU',
            bObject.irrb_volight_subu, i2)

        self._iwrite(file, 'int', 'subDivideV',
            bObject.irrb_volight_subv, i2)

        self._iwrite(file, 'color', 'footColor',
            rgb2DelStr(bObject.irrb_volight_footcol), i2)

        self._iwrite(file, 'color', 'tailColor',
            rgb2DelStr(bObject.irrb_volight_tailcol), i2)

        dim = bObject.irrb_volight_dimension
        sdim = '{:.6f}, {:.6f}, {:.6f}'.format(dim[0], dim[1], dim[2])

        file.write(i2 + '<vector3d name="lightDimension" ' \
            'value="{}"/>\n'.format(sdim))

        file.write(i1 + '</attributes>\n')

        # extract material type based on irrb UV layer rules
        file.write(i1 + '<materials>\n')
        bMesh = bObject.data

        bMaterial = None
        if len(bMesh.materials) > 0:
            bMaterial = bMesh.materials[0]

        material = iMaterial(bObject, 'volumelight', self.exporter,
            bMaterial)

        # override parm1
        material.attributes['MaterialTypeParam'] = 1.194e-041

        bImage = None
        if len(bMesh.uv_textures):
            bImage = bMesh.uv_textures[0].data[bMesh.faces[0].index].image

        self._writeSBImageAttributes(file, i2, material, bImage)

        file.write(i1 + '</materials>\n')

    #=========================================================================
    #                          w r i t e A n i m a t i o n
    #=========================================================================
    def writeAnimation(self, file, bAction):
        if bAction.name in self.exporter.gExportedNodeAnimations:
            return

        self.exporter.gExportedNodeAnimations.append(bAction.name)

        i1 = getIndent(0)
        i2 = getIndent(1)
        i3 = getIndent(2)

        file.write(i1 + '<animation name="{}" ' \
            'length="{:.6f}">\n'.format(bAction.name,
            self.exporter.gAnimationLength))

        parms = ('x', 'y', 'z', 'w')
        for curve in bAction.fcurves:
            dpath = curve.data_path
            target = 'unknown'
            if dpath in ('location', 'rotation_euler', 'scale'):
                target = '{}.{}'.format(dpath, parms[curve.array_index])
            else:
                target = '{}.{}'.format(dpath, curve.array_index)

            file.write(i2 + '<keyframes target="{}">\n'.format(target))

            for keyframe in curve.keyframe_points:
                file.write(i3 + '<keyframe time="{:.6f}" ' \
                    'value="{:.6f}" ipol="{}"/>\n'.format
                    ((keyframe.co.x - self.exporter.gBScene.frame_start) /
                    self.exporter.gBScene.render.fps,
                    keyframe.co.y, keyframe.interpolation))

            file.write(i2 + '</keyframes>\n')

        file.write(i1 + '</animation>\n')

    #=========================================================================
    #                   w r i t e B i l l b o a r d N o d e D a t a
    #=========================================================================
    def writeBillboardNodeData(self, file, bObject, bbImage, level):
        if bObject.type != 'MESH':
            return

        bMaterial = None
        mesh = bObject.data
        if len(mesh.materials) > 0:
            bMaterial = mesh.materials[0]

        material = iMaterial(bObject, 'billboard', self.exporter,
            bMaterial)
        i1 = getIndent(level, 3)
        i2 = getIndent(level, 6)

        ipos = b2iPosition(bObject)
        irot = (0.0, 0.0, 0.0)
        iscale = (1.0, 1.0, 1.0)

        self.writeSTDAttributes(file, i1, i2, bObject, ipos, irot, iscale,
            'false')

        # billboard quad vertex positions: ul:3, ur:0, lr:1, ll:2

        ul = mesh.vertices[3].co
        ur = mesh.vertices[0].co
        lr = mesh.vertices[1].co

        scale = bObject.scale
        dx = (ul.x - ur.x) * scale[0]
        dy = (ul.y - ur.y) * scale[1]
        dz = (ul.z - ur.z) * scale[2]
        width = math.fabs(math.sqrt((dx * dx) + (dy * dy) + (dz * dz)))

        dx = (ur.x - lr.x) * scale[0]
        dy = (ur.y - lr.y) * scale[1]
        dz = (ur.z - lr.z) * scale[2]
        height = math.fabs(math.sqrt((dx * dx) + (dy * dy) + (dz * dz)))

        file.write(i2 + '<int name="Width" ' \
            'value="{:.6f}" />\n'.format(bObject.irrb_billboard_width))
        file.write(i2 + '<int name="Height" ' \
            'value="{:.6f}" />\n'.format(bObject.irrb_billboard_height))
        file.write(i2 + '<color name="Shade_Top" value="{}" />\n'.format(rgb2str(bObject.irrb_billboard_shade_top)))
        file.write(i2 + '<color name="Shade_Down" value="{}" />\n'.format(rgb2str(bObject.irrb_billboard_shade_bot)))

        file.write(i1 + '</attributes>\n')
        file.write(i1 + '<materials>\n')

        self._writeSBImageAttributes(file, i2, material, bbImage)

        file.write(i1 + '</materials>\n')

#=============================================================================
#                               i M e s h
#=============================================================================
class iMesh:
    #=========================================================================
    #                               _ i n i t _
    #=========================================================================
    def __init__(self, bObject, exporter, debug):
        self.bObject = bObject
        self.name = bObject.name
        self.exporter = exporter
        self.gui = exporter.gGUI
        self.bKeyBlocks = None
        self.armatures = []
        self.shapes = []

        # get 'Mesh' 
        self.bMesh = bObject.data

        # get mesh shape keys
        self.bKey = self.bMesh.shape_keys
        if self.bKey:
            self.bKeyBlocks = self.bKey.keys

        # get mesh armatures - ignore parent armatures for now, currently when
        # an object is parented to an armature, it is also added to objects
        # modifier stack.
        mods = self.bObject.modifiers
        if mods:
            for mod in mods:
                if mod.type == 'ARMATURE':
                    try:
                        armature = mod.object
                        self.armatures.append(armature)
                    except:
                        pass

        self.meshBuffers = []

        # dict of {mangled material name, MeshBuffer()}
        self.materials = {}
        self.hasFaceUV = len(self.bMesh.uv_textures) > 0
        self.debug = debug

        self.uvMatName = None                # Irrlicht material name
        self.findMatName()
        
    #=========================================================================
    #                     _ w r i t e D e b u g I n f o
    #=========================================================================
    def _writeDebugInfo(self):
        if self.bObject.parent == None:
            debug('Parent: None')
        else:
            debug('Parent: {}'.format(self.bObject.parent.name))

        debug('Rotation Mode: {}'.format(self.bObject.rotation_mode))
        debug('Rotation Euler: {}'.format(self.bObject.rotation_euler))
        debug('Hide: ' + str(self.bObject.hide))
        debug('Hide Render: ' + str(self.bObject.hide_render))

        lnames = ''
        for uv in self.bMesh.uv_textures:
            if len(uv.name):
                lnames += ', '
            lnames += uv.name
        debug('UV Layers ({}): {}'.format(len(self.bMesh.uv_textures),
                lnames))
        mname = 'None'
        if self.uvMatName != None:
            mname = self.uvMatName
        debug('Primary UV Layer: ' + mname)
        val = 'False'
        if self.bMesh.show_double_sided:
            val = 'True'
        debug('Double Sided: ' + val)

        if len(self.bMesh.vertex_colors) > 0:
            val = 'True'
        else:
            val = 'False'
        debug('Mesh VertexColors: ' + val)

        if len(self.bObject.modifiers) > 0:
            debug('Modifiers:')
            for mod in self.bObject.modifiers:
                debug('   Name: {}, Type: {}'.format(mod.name, mod.type))
        else:
            debug('Modifiers: None')

        #
        # dump armatures
        #
        if len(self.armatures) > 0:
            debug('Armatures:')
            for arm in self.armatures:
                debug('   Name: {}, Bone Count: {}'.format
                        (arm.name, len(arm.pose.bones)))
        else:
            debug('Armatures: None')

        #
        # dump physics
        #
        debug('physics_type: ' + self.bObject.game.physics_type)
        debug('collision_bounds: ' +
            self.bObject.game.collision_bounds_type)
        debug('mass: {:.2f}'.format(self.bObject.game.mass))
        debug('radius: {:.2f}'.format(self.bObject.game.radius))

    #=========================================================================
    #                   r e l e a s e M e s h B u f f e r s
    #=========================================================================
    def releaseMeshBuffers(self):
        for meshBuffer in self.meshBuffers:
            meshBuffer.release()

        self.meshBuffers[:] = []
        self.materials.clear()

    #=========================================================================
    #                        f i n d M a t N a m e
    #=========================================================================
    def findMatName(self):
        if len(self.bMesh.uv_textures) == 0:
            return

        #
        # search for matching Irrlicht material name
        #
        for uv in self.bMesh.uv_textures:
            if getIrrMaterial(uv.name) != None:
                self.uvMatName = uv.name
                return

        #
        # if not found look for custom name: '$' prefix
        #
        for uv in self.bMesh.uv_textures:
            if uv.name[0] == '$':
                self.uvMatName = uv.name
                return

    #=========================================================================
    #                         g e t M a t e r i a l s
    #=========================================================================
    def getMaterials(self):
        return self.materials

    #=========================================================================
    #                       g e t V e r t e x C o u n t
    #=========================================================================
    def getVertexCount(self):
        count = 0

        for buf in self.meshBuffers:
            count += len(buf.vertices)

        return count

    #=========================================================================
    #                          g e t F a c e C o u n t
    #=========================================================================
    def getFaceCount(self):
        count = 0
        for buf in self.meshBuffers:
            count += len(buf.faces)

        return count

    #=========================================================================
    #                     _ g e t F a c e I m a g e N a m e s
    #=========================================================================
    def _getFaceImageNames(self, face):
        names = ''
        for uvlayer in self.bMesh.uv_textures:

            if uvlayer.data[face.index].image == None:
                names += 'none:'
            else:
                names += (uvlayer.data[face.index].image.name + ':')
        if names == '':
            names = 'none:'
        return names

    #=========================================================================
    #                    c r e a t e M e s h B u f f e r s
    #=========================================================================
    def createMeshBuffers(self):
        if self.debug:
            self._writeDebugInfo()
        #
        # Loop through faces and create a new "MeshBuffer" instance for each
        # unique material assigned to a face.  Also add the corresponding
        # face/vertex info into the MeshBuffer.
        #
        result = True
        faces = self.bMesh.faces
        hasMaterials = len(self.bMesh.materials) > 0

        fcount = 0
        tfaces = len(faces)
        mcount = 100

        #tangents = self.bMesh.getTangents()

        for face in faces:

            if self.gui.isExportCanceled():
                break

            fcount += 1
            if (fcount % mcount) == 0:
                self.gui.updateStatus('Analyzing Mesh Faces: {}, ({} ' \
                    'of {})'.format(self.bMesh.name, fcount, tfaces))

            #
            # 'matName' is assigned based on blender material name and
            # uv texture image data.  This allows for faces to be assigned
            # unique images within uv layers.
            #
            bMaterial = None
            matName = 'unassigned'
            if hasMaterials:
                bMaterial = self.bMesh.materials[face.material_index]
                if bMaterial:
                    matName = bMaterial.name

            # now append uv image info
            for layerNumber in range(len(self.bMesh.uv_textures)):
                uvFaceData = \
                    self.bMesh.uv_textures[layerNumber].data[face.index]
                if uvFaceData.image == None:
                    matName += ':0'
                else:
                    matName += ':{}'.format(uvFaceData.image.name)

            # check if we have already created a meshbuffer for this material
            if matName in self.materials:
                meshBuffer = self.materials[matName]
            else:
                material = iMaterial(self.bObject, matName, self.exporter,
                    bMaterial, face)

                # create the meshbuffer and update the material dict & mesh
                # buffer list
                meshBuffer = iMeshBuffer(self.exporter, self.bObject, material,
                        matName, len(self.meshBuffers), self.armatures)
                self.materials[matName] = meshBuffer
                self.meshBuffers.append(meshBuffer)

            #todo - figure if tangents exist or need to be calculated
            tangent = mathutils.Vector()
            tangents = [tangent, tangent, tangent, tangent]
            meshBuffer.addFace(face, tangents, self.bKeyBlocks)

        self.gui.updateStatus('Analyzing Mesh Faces: {}, Done.'.format
                        (self.bMesh.name))
        if self.debug:
            debug('\n[Buffers]')
            debug('Count: {}'.format(len(self.materials)))
            for k, v in self.materials.items():
                debug('   ' + k + ' : ' + v.getMaterialType())

        return result

    #=========================================================================
    #                       w r i t e M e s h D a t a
    #=========================================================================
    def writeMeshData(self, file):

        file.write('<?xml version="1.0"?>\n')
        file.write('<mesh xmlns="http://irrlicht.sourceforge.net/' \
            'IRRMESH_09_2007" version="1.0">\n')
        file.write('<!-- Created {} by irrb {} - ' \
                '"Irrlicht/Blender Exporter" ' \
                '-->\n'.format(datetime2str(time.localtime()), getversion()))

        for buffer in self.meshBuffers:
            buffer.writeBufferData(file)

        file.write('</mesh>\n')

#=============================================================================
#                                 i V e r t e x
#=============================================================================
class iVertex:
    #=========================================================================
    #                               _ i n i t _
    #=========================================================================
    def __init__(self, bVertex, irrIdx, bKeyBlocks, color, alpha, tangent):
        self.bVertex = bVertex
        self.index = bVertex.index
        self.irrIdx = irrIdx
        self.vcolor = color
        self.valpha = alpha
        self.UV1 = None
        self.UV2 = None
        #
        # if shape keys exist, use the position from the "basis" key.
        #
        self.pos = []
        if bKeyBlocks != None:
            self.pos = []
            for i in range(len(bKeyBlocks)):
                self.pos.append(bKeyBlocks[i].data[bVertex.index].co)
        else:
            self.pos.append(self.bVertex.co)
        n = self.bVertex.normal
        self.normal = mathutils.Vector((n.x, n.y, n.z))
        if tangent != None:
            self.tangent = mathutils.Vector((tangent.x, tangent.y, tangent.z))
        else:
            self.tangent = mathutils.Vector()

        self.binormal = self.normal.cross(self.tangent)
        self.binormal.normalize()

#=============================================================================
#                              i M e s h B u f f e r
#=============================================================================
class iMeshBuffer:
    #=========================================================================
    #                               _ i n i t _
    #=========================================================================
    def __init__(self, exporter, bObject, material, uvMatName, bufNumber,
        armatures):
        self.bObject = bObject
        self.bMesh = bObject.data

        #self.bKey = self.bMesh.key
        #self.bKeyBlocks = None
        #if self.bKey:
        #    self.bKeyBlocks = self.bKey.blocks

        self.vertexColorData = None
        if self.bMesh.vertex_colors.active:
            self.vertexColorData = self.bMesh.vertex_colors.active.data

        self.vertexColorAlpha = None
        if 'alpha' in self.bMesh.vertex_colors:
            self.vertexColorAlpha = self.bMesh.vertex_colors['alpha'].data

        self.bufNumber = bufNumber
        self.exporter = exporter
        self.gui = exporter.gGUI
        self.armatures = armatures

        self.material = material
        self.uvMatName = uvMatName
        self.vertref = {}   # vertex dict key: 'blender vertex index:vertex color'
        self.vertices = []
        self.faces = []     # list of irr indexes {{i0,i1,i2},{},...}
        self.hasUVTextures = len(self.bMesh.uv_textures) > 0

        self.relMeshDir = os.path.relpath(self.exporter.gMeshDir,
            self.exporter.gBaseDir) + '/'

    #=========================================================================
    #                        _ w r i t e V e r t e x
    #=========================================================================
    def _writeVertex(self, file, vert, vtype, idx=0):
        pos = vert.pos[idx]
        normal = vert.normal
        color = vert.vcolor
        alpha = vert.valpha
        uv1 = vert.UV1
        if uv1 == None:
            uv1 = (0.0, 0.0)
        uv2 = vert.UV2
        if uv2 == None:
            uv2 = uv1

        tangent = vert.tangent
        binormal = vert.binormal

        spos = '{} '.format(_formatFloats((pos.x, pos.z, pos.y), ' '))
        snormal = '{} '.format(_formatFloats((normal.x, normal.z,
            normal.y), ' '))

        if color != None and self.material.useVertexColor:
            scolor = bc2SColor(color, alpha) + ' '
        else:
            scolor = del2SColor(self.material.getDiffuse()) + ' '
        suv = '{} '.format(_formatFloats((uv1[0], 1 - uv1[1]), ' '))

        if vtype == EVT_STANDARD:
            file.write('         ' + spos + snormal + scolor + suv + '\n')
            return

        if vtype == EVT_2TCOORDS:
            suv2 = '{} '.format(_formatFloats((uv2[0], 1 - uv2[1]), ' '))
            file.write((9 * ' ') + spos + snormal + scolor + suv + suv2 + '\n')
            return

        stangent = '{} '.format(_formatFloats((tangent.x, tangent.z,
            tangent.y), ' '))
        sbinormal = '{} '.format(_formatFloats((binormal.x,
            binormal.z, binormal.y), ' '))
        file.write('{}{}{}{}{}{}{}\n'.format(9 * ' ', spos, snormal,
                   scolor, suv, stangent, sbinormal))

    #=========================================================================
    #                       _ w r i t e V e r t i c e s
    #=========================================================================
    def _writeVertices(self, file):
        vtype = self.material.getVertexType()

        if vtype == EVT_STANDARD:
            svtype = 'standard'
        elif vtype == EVT_2TCOORDS:
            svtype = '2tcoords'
        elif vtype == EVT_TANGENTS:
            svtype = 'tangents'

        file.write('      <vertices type="{}" vertexCount="{}">\n'.format
                (svtype, len(self.vertices)))

        meshName = self.bMesh.name
        tverts = len(self.vertices)
        vcount = 0
        mcount = 100
        bnum = self.bufNumber
        if tverts > 10000:
            mcount = 1000
        for vert in self.vertices:
            if self.gui.isExportCanceled():
                return

            self._writeVertex(file, vert, vtype)
            vcount += 1
            if (vcount % mcount) == 0:
                self.gui.updateStatus('Exporting Mesh: {}, buf: {} ' \
                    'writing vertices({} of {})'.format(meshName, bnum,
                    vcount, tverts))
        file.write('      </vertices>\n')

    #=========================================================================
    #                         _ w r i t e F a c e s
    #=========================================================================
    def _writeFaces(self, file):
        file.write('      <indices ' \
            'indexCount="{}">\n'.format(len(self.faces) * 3))
        line = 8 * ' '
        iCount = 0

        meshName = self.bMesh.name
        tfaces = len(self.faces)
        fcount = 0
        bnum = self.bufNumber
        for face in self.faces:
            if self.gui.isExportCanceled():
                return
            line += (' {} {} {}'.format(face[2], face[1], face[0]))
            iCount += 1
            if iCount == 12:
                file.write(line + '\n')
                line = 8 * ' '
                iCount = 0
            fcount += 1
            if (fcount % 100) == 0:
                self.gui.updateStatus('Exporting Mesh: {}, buf: {} ' \
                    'writing faces({} of {}'.format(meshName, bnum,
                    fcount, tfaces))

        if iCount > 0:
            file.write(line + '\n')

        file.write('      </indices>\n')

    #=========================================================================
    #                     _ w r i t e M o r p h T a r g e t
    #=========================================================================
    def _writeMorphTarget(self, file, idx):
        #
        # count the number of vertices we'll be writing
        #
        block = self.bKeyBlocks[idx]
        vidx = 0
        for vert in self.vertices:
            if iGUI.exportCancelled():
                return

            bvert = vert.pos[0]
            pos = vert.pos[idx]

            if (bvert.x != pos.x) or (bvert.y != pos.y) or (bvert.z != pos.z):
                vidx += 1

        file.write('      <morph-target name="{}" ' \
            'vertexCount="{}">\n'.format(block.name, vidx))

        meshName = self.bMesh.name
        tverts = len(self.vertices)
        vcount = 0
        mcount = 100
        bnum = self.bufNumber
        if tverts > 10000:
            mcount = 1000
        vidx = 0
        for vert in self.vertices:
            if iGUI.exportCancelled():
                return

            bvert = vert.pos[0]

            pos = vert.pos[idx]

            if (bvert.x != pos.x) or (bvert.y != pos.y) or (bvert.z != pos.z):
                spos = '{} {:.6f} {:.6f} {:.6f} '.format(vidx, pos.x,
                    pos.z, pos.y)
                file.write(9 * ' ' + spos + '\n')
            vidx += 1
            vcount += 1
            if (vcount % mcount) == 0:
                iGUI.updateStatus('Exporting Mesh: {}, buf: {} ' \
                    'writing vertices({} of {})'.format(meshName, bnum,
                    vcount, tverts))

        file.write('      </morph-target>\n')

    #=========================================================================
    #                   _ w r i t e S k i n W e i g h t s
    #=========================================================================
    def _writeSkinWeights(self, file):
        obj_vgroups = self.bObject.vertex_groups
        for aobj in self.armatures:
            arm = aobj.data

            bidx = 0
            boneDict = {}
            for bone in arm.bones:
                if bone.name in obj_vgroups and bone.use_deform:
                    boneDict[obj_vgroups[bone.name].index] = (bidx, bone.name)
                bidx += 1

            wcount = 0
            for v in self.vertices:
                for group in v.bVertex.groups:
                    if group.group in boneDict:
                        wcount += 1

            if wcount == 0:
                continue

            skelName = '{}.irrskel'.format(arm.name)
            file.write('      <skinWeights weightCount="{}" link="{}">\n'.format(wcount, skelName))
            oidx = 0

            for v in self.vertices:
                for group in v.bVertex.groups:
                    if group.group in boneDict:
                        bidx, bname = boneDict[group.group]
                        weight = group.weight
                        if weight == 1.0:
                            sweight = "1"
                        elif weight == 0.0:
                            sweight = "0"
                        else:
                            sweight = _formatFloats((weight,))
                        if oidx == 0:
                            line = '         {} {} {}'.format(v.irrIdx,
                                bidx, sweight)
                        else:
                            line += ' {} {} {}'.format(v.irrIdx,
                                bidx, sweight)
                        oidx += 1
                        if oidx == 5:
                            oidx = 0
                            line += '\n'
                            file.write(line)
            if oidx > 0:
                line += '\n'
                file.write(line)

            file.write('      </skinWeights>\n')

    #=========================================================================
    #               _ g e t A c t i o n s
    #=========================================================================
    def _getActions(self):

        objActions = []
        boneNames = []
        for m in self.bObject.modifiers:
            if m.type == 'ARMATURE':
                temp = [bone.name for bone in m.object.data.bones]
                for n in temp:
                    boneNames.append(n)

        if len(boneNames) == 0:
            return []

        for action in bpy.data.actions:
            curvePaths = [curve.data_path for curve in action.fcurves]
            for path in curvePaths:
                found = False
                for name in boneNames:
                    if path.find(name) >= 0:
                        objActions.append(action.name)
                        found = True
                        break
                if found:
                    break

        return objActions

    #=========================================================================
    #                        _ w r i t e A c t i o n s
    #=========================================================================
    def _writeAction(self, file, actionName):
        action = bpy.data.actions[actionName]

        fps = self.exporter.gBScene.render.fps_base * self.exporter.gBScene.render.fps
        aframes = action.frame_range[1] - action.frame_range[0]
        
        print('frame_range: ',action.frame_range)

        slength = _formatFloats(((aframes / fps),))
        file.write('    <animation name="{}" length="{}">\n'.format(actionName,
            slength))

        # reorganize bone and keyframe data
        # boneData = {bone : {frame number: {'loc'/'rot'/'scale': [x, y, z]}}}
        boneData = {}
        for curve in action.fcurves:
            path = curve.data_path.split('"')
            boneName = path[1]
            channel = path[2].split('.')[1]
            if boneName in boneData:
                frameData = boneData[boneName]
            else:
                frameData = {}
                boneData[boneName] = frameData

            for keyframe in curve.keyframe_points:
                frame = keyframe.co[0]
                if frame in frameData:
                    keyData = frameData[frame]
                else:
                    keyData = {'location': [None, None, None],
                        'rotation_quaternion': [None, None, None, None],
                        'scale': [None, None, None]}
                    frameData[frame] = keyData

                keyData[channel][curve.array_index] = keyframe.co[1]

        #file.write('      <curves>\n')
        i1 = ' ' * 6
        i2 = ' ' * 8
        i3 = ' ' * 10
        boneData = collections.OrderedDict(sorted(boneData.items(), key=lambda t: t[0]))

        for boneName in boneData.keys():
            file.write('{}<curve joint="{}">\n'.format(i1, boneName))
            frameData = collections.OrderedDict(sorted(boneData[boneName].items(), key=lambda t: t[0]))
            for frame in frameData:
                keyData = frameData[frame]
                skeytime = '{:.6f}'.format((frame-1) / fps)
                file.write('{}<keyframe time="{}" interpolation="{}">\n'.format(i2, skeytime, 'LINEAR'))

                dat = keyData['location']
                if (dat[0] != None) or (dat[1] != None) or (dat[2] != None):
                    sval = '{:.6f}, {:.6f}, {:.6f}'.format(dat[0], dat[1], -dat[2])
                    file.write(i3 + '<vector3d name="Position" ' \
                        'value="{}"/>\n'.format(sval))

                dat = keyData['rotation_quaternion']
                if (dat[0] != None) or (dat[1] != None) or (dat[2] != None):
                    sval = '{:.6f}, {:.6f}, {:.6f}, {:.6f}'.format(dat[1], dat[2], -dat[3], dat[0])
                    file.write(i3 + '<quaternion name="Rotation" ' \
                        'value="{}"/>\n'.format(sval))

                dat = keyData['scale']
                if (dat[0] != None) or (dat[1] != None) or (dat[2] != None):
                    sval = '{:.6f}, {:.6f}, {:.6f}'.format(dat[0], dat[1], dat[2])
                    file.write(i3 + '<vector3d name="Scale" ' \
                        'value="{}"/>\n'.format(sval))

                file.write('{}</keyframe>\n'.format(i2))
            file.write('{}</curve>\n'.format(i1))

        '''
        for curve in action.fcurves:
            path = curve.data_path.split('.')
            boneName = path[1].split('"')[1]
            channel = path[2]
            if curve.array_index == 0:
                channel += '.x'
            elif curve.array_index == 1:
                channel += '.y'
            else:
                channel += '.z'
                
            file.write('{}<curve joint="{}" channel="{}">\n'.format(i1, boneName, channel))

            for keyframe in curve.keyframe_points:
                skeytime = '{:.6f}'.format(keyframe.co[0] / fps)
                file.write('{}<keyframe time="{}" ipol="{}">\n'.format(i2, skeytime, 'LINEAR'))
                file.write('{}</keyframe>\n'.format(i2))


            file.write('{}</curve>\n'.format(i1))
        '''

        #file.write('      </curves>\n')

        file.write('    </animation>\n')

    #=========================================================================
    #                       _ w r i t e S k e l e t o n s
    #=========================================================================
    def _writeSkeletons(self, arm):
        skelFileName = '{}{}.irrskel'.format(self.exporter.gMeshDir, arm.name)

        if os.path.exists(skelFileName):
            os.unlink(skelFileName)

        relSkelName = os.path.relpath(skelFileName, self.exporter.gBaseDir)
        print('relSkeName: {}'.format(relSkelName))
        self.exporter._addSkelToExportedList(arm.name, skelFileName, relSkelName)

        file = open(skelFileName, 'w')
        file.write('<skeleton>\n')

        # write joints
        file.write('  <joints>\n')

        i1 = '      '
        for bone in arm.pose.bones:
            sparent = ''
            if bone.parent:
                sparent = bone.parent.name
            file.write('    <joint name="{}" parent="{}">\n'.format(bone.name, sparent))

            ipos = (bone.location.x, bone.location.z, bone.location.y)

            bEuler = bone.rotation_euler
            irot = (bEuler.x * RAD2DEG, bEuler.y * RAD2DEG,
                bEuler.z * RAD2DEG)
                
            iscale = b2iScale(bone.scale)

            spos = _formatFloats(ipos)
            srot = _formatFloats(irot)
            sscale = _formatFloats(iscale)

            file.write(i1 + '<vector3d name="Position" ' \
                'value="{}"/>\n'.format(spos))
            file.write(i1 + '<vector3d name="Rotation" ' \
                'value="{}"/>\n'.format(srot))
            file.write(i1 + '<vector3d name="Scale" ' \
                'value="{}"/>\n'.format(sscale))
                        
            file.write('    </joint>\n')

        # write tail joints for debugging purposes
        if self.exporter.gExportAnimationTails:

            for bone in arm.data.bones:
                if len(bone.children) > 0:
                    continue

                sparent = bone.name
                file.write('    <joint name="{}_tail" parent="{}">\n'.format(bone.name, sparent))

                ipos = (bone.tail_local.x, bone.tail_local.z, bone.tail_local.y)

                spos = _formatFloats(ipos)
                srot = '0, 0, 0'
                sscale = '1, 1, 1'

                file.write(i1 + '<vector3d name="Position" ' \
                    'value="{}"/>\n'.format(spos))
                file.write(i1 + '<vector3d name="Rotation" ' \
                    'value="{}"/>\n'.format(srot))

                file.write(i1 + '<vector3d name="Scale" ' \
                    'value="{}"/>\n'.format(sscale))

                file.write('    </joint>\n')


        file.write('  </joints>\n')

        # write animations
        actions = self._getActions()

        print('**actions:', actions)

        file.write('  <animations>\n')
        for action in actions:
            self._writeAction(file, action)

        file.write('  </animations>\n')

        file.write('</skeleton>\n')
        file.close()
        
    #=========================================================================
    #                              r e l e a s e
    #=========================================================================
    def release(self):
        self.vertref.clear()
        self.vertices[:] = []
        self.faces[:] = []

    #=========================================================================
    #                         g e t M a t e r i a l T y p e
    #=========================================================================
    def getMaterialType(self):
        return self.material.getType()

    #=========================================================================
    #                            g e t M a t e r i a l
    #=========================================================================
    def getMaterial(self):
        return self.material

    #=========================================================================
    #                             a d d V e r t e x
    #=========================================================================
    def addVertex(self, bVertex):
        vertex = Vertex(bVertex)
        self.vertices.append(vertex)
        # return our index
        return len(self.vertices)

    #=========================================================================
    #                           c r e a t e V e r t e x
    #=========================================================================
    def createVertex(self, bFace, idx, bKeyBlocks, tangent):
        #
        # extract the Blender vertex data
        #
        bVertex = self.bMesh.vertices[bFace.vertices[idx]]
        vColor = None
        vAlpha = 1.0
        if self.vertexColorData:
            vColor = getattr(self.vertexColorData[bFace.index],
                'color{}'.format(idx + 1))

            if self.vertexColorAlpha:
                color = getattr(self.vertexColorAlpha[bFace.index],
                    'color{}'.format(idx + 1))
                vAlpha = color.r

        UV1 = None
        UV2 = None
        suv1 = ''
        suv2 = ''
        uvLayerCount = len(self.bMesh.uv_textures)
        if uvLayerCount > 0:
            uvFaceData = self.bMesh.uv_textures[0].data[bFace.index]
            UV1 = tuple(uvFaceData.uv[idx])
            suv1 = '{:.6f}{:.6f}'.format(UV1[0], UV1[1])
        if uvLayerCount > 1:
            uvFaceData = self.bMesh.uv_textures[1].data[bFace.index]
            UV2 = tuple(uvFaceData.uv[idx])
            suv2 = '{:.6f}{:.6f}'.format(UV2[0], UV2[1])

        # differentiate unique vertex color & uv data.
        vKey = '{}{}{}{}{}'.format(bVertex.index, vColor,
            int(255 * vAlpha), suv1, suv2)

        if vKey in self.vertref:
            vertex = self.vertices[self.vertref[vKey]]
        else:
            irrIdx = len(self.vertices)
            self.vertref[vKey] = irrIdx
            vertex = iVertex(bVertex, irrIdx, bKeyBlocks, vColor,
                             vAlpha, tangent)
            vertex.UV1 = UV1
            vertex.UV2 = UV2
            self.vertices.append(vertex)

        return vertex

    #=========================================================================
    #                              a d d F a c e
    #=========================================================================
    def addFace(self, bFace, faceTangents, bKeyBlocks):
        if (len(bFace.vertices) == 3):
            v1 = self.createVertex(bFace, 0, bKeyBlocks, faceTangents[0])
            v2 = self.createVertex(bFace, 1, bKeyBlocks, faceTangents[1])
            v3 = self.createVertex(bFace, 2, bKeyBlocks, faceTangents[2])
            self.faces.append((v1.irrIdx, v2.irrIdx, v3.irrIdx))
        elif (len(bFace.vertices) == 4):
            v1 = self.createVertex(bFace, 0, bKeyBlocks, faceTangents[0])
            v2 = self.createVertex(bFace, 1, bKeyBlocks, faceTangents[1])
            v3 = self.createVertex(bFace, 2, bKeyBlocks, faceTangents[2])
            v4 = self.createVertex(bFace, 3, bKeyBlocks, faceTangents[3])
            self.faces.append((v1.irrIdx, v2.irrIdx, v3.irrIdx))
            self.faces.append((v4.irrIdx, v1.irrIdx, v3.irrIdx))
        else:
            print('Ignored face with {} edges.'.format(len(bFace.vertices)))

    #=========================================================================
    #                              w r i t e
    #=========================================================================
    def writeBufferData(self, file):
        file.write('   <buffer>\n')
        self.material.write(file)
        self._writeVertices(file)
        self._writeFaces(file)

        if self.exporter.gExportAnimations and (len(self.armatures) > 0):
            self._writeSkinWeights(file)

            for armature in self.armatures:
                self._writeSkeletons(armature)

        # todo
        #if self.bKeyBlocks:
        #    for i in range(1,len(self.bKeyBlocks)):
        #        self._writeMorphTarget(file,i)
        file.write('   </buffer>\n')

#=============================================================================
#                              i E x p o r t e r
#=============================================================================
class iExporter:

    #=========================================================================
    #                               _ i n i t _
    #=========================================================================
    def __init__(self, Context, Operator, GUIInterface,
            CreateScene, BaseDir, SceneDir, MeshDir, TexDir,
            SelectedObjectsOnly, ExportLights, ExportCameras,
            ExportAnimations, ExportAnimationTails, ExportPhysics, ExportPack,
            ExportExec, Binary, Debug, runWalkTest, IrrlichtVersion,
            MeshCvtPath, WalkTestPath):

        # Load the default/saved configuration values
        self.gOperator = Operator

        if len(BaseDir):
            if BaseDir[len(BaseDir) - 1] != os.path.sep:
                BaseDir += os.path.sep

        if len(MeshDir):
            if MeshDir[len(MeshDir) - 1] != os.path.sep:
                MeshDir += os.path.sep
        if len(TexDir):
            if TexDir[len(TexDir) - 1] != os.path.sep:
                TexDir += os.path.sep

        self.gCfgString = ''
        self.gContext = Context
        self.gGUI = GUIInterface
        self.gCreateScene = CreateScene
        self.gBaseDir = BaseDir
        self.gBlendFileName = bpy.data.filepath
        self.gBlendRoot = os.path.dirname(self.gBlendFileName)
        self.gMeshDir = MeshDir
        self.gTexDir = TexDir
        self.gSceneDir = SceneDir
        self.gTexExtension = '.???'
        self.gSelectedObjectsOnly = SelectedObjectsOnly
        self.gExportLights = ExportLights
        self.gExportCameras = ExportCameras
        self.gExportAnimations = ExportAnimations
        self.gExportAnimationTails = ExportAnimationTails
        self.gExportPhysics = ExportPhysics
        self.gExportPack = ExportPack
        self.gExportExec = ExportExec
        self.gRunWalkTest = runWalkTest

        if not gHaveWalkTest:
            self.gRunWalkTest = False
            self.gExportExec = False
        if self.gExportExec:
            self.gExportPack = True

        self.gCopyImages = _G['export']['copy_images']
        self.gBinary = Binary
        self.gDebug = Debug
        self.gMeshFileName = ''
        self.gSceneFileName = ''
        self.gScenePackName = ''
        self.gObjectLevel = 0
        self.gIrrlichtVersion = IrrlichtVersion
        self.gMeshCvtPath = MeshCvtPath
        self.gWalkTestPath = WalkTestPath
        self.gBScene = None
        self.gIScene = None
        self.sfile = None
        self.gAnimationLength = 0.0

    #=========================================================================
    #                           _ d u m p O p t i o n s
    #=========================================================================
    def _dumpOptions(self):
        debug('\n[options]')
        debug('     Create Scene: ' +
            ('True' if self.gCreateScene else 'False'))
        debug('   Base Directory: ' + self.gBaseDir)
        debug('  Scene Directory: ' + self.gSceneDir)
        debug('   Mesh Directory: ' + self.gMeshDir)
        debug('  Image Directory: ' + self.gTexDir)
        debug('    mdl Directory: ' + _G['export']['mdl_directory'])
        debug('    tex Directory: ' + _G['export']['tex_directory'])
        debug('           Binary: ' + ('True' if self.gBinary else 'False'))
        debug('   Export Cameras: ' +
            ('True' if self.gExportCameras else 'False'))
        debug('    Export Lights: ' +
            ('True' if self.gExportLights else 'False'))
        debug('   Export Physics: ' +
            ('True' if self.gExportPhysics else 'False'))
        debug('      Export Pack: ' +
            ('True' if self.gExportPack else 'False'))
        debug('Export Executable: ' +
            ('True' if self.gExportExec else 'False'))
        debug('      Copy Images: ' +
            ('True' if self.gCopyImages else 'False'))
        debug('     Run WalkTest: ' +
            ('True' if self.gRunWalkTest else 'False'))
        debug('  Image Extension: ' + ('Original' if self.gTexExtension ==
            '.???' else self.gTexExtension))
        debug('    Selected Only: ' +
            ('True' if self.gSelectedObjectsOnly else 'False'))
        debug('     Irrlicht Ver: ' + str(self.gIrrlichtVersion))
        debug('    iwalktest Env: {}'.format(self.gWalkTestPath))
        debug('     imeshcvt Env: {}'.format(self.gMeshCvtPath))
        if self.gWalkTestPath:
            debug('    iwalktest Cmd: ' + self.gWalkTestPath.replace('$1',
                flattenPath(self.gSceneFileName)).replace('$2',
                filterPath(self.gBaseDir)))

    #=========================================================================
    #                             _ d u m p S t a t s
    #=========================================================================
    def _dumpStats(self, stats):
        debug('\n[stats]')
        for stat in stats:
            debug(stat)

    #=========================================================================
    #                      _ d u m p G e n e r a l I n f o
    #=========================================================================
    def _dumpGeneralInfo(self):
        debug('\n[general info]')
        p = platform.uname()
        debug('               OS: {} {} {}'.format(p[0], p[2], p[3]))
        debug('  Blender Version: ' \
            '{0[0]}.{0[1]}.{0[2]}'.format(bpy.app.version))
        debug('      .blend File: {}'.format(self.gBlendFileName))
        debug('      .blend Root: {}'.format(self.gBlendRoot))
        debug('     .irrb Config: {}'.format(gUserConfig))
        debug('   Python Version: {}.{}.{} {}'.format(sys.version_info[0],
            sys.version_info[1], sys.version_info[2], sys.version_info[3]))

    #=========================================================================
    #                       _ d u m p S c e n e I n f o
    #=========================================================================
    def _dumpSceneInfo(self):
        debug('\n[scene info]')
        debug('Scene Name: {}'.format(self.gBScene.name))
        vlayers = [i for i in range(len(self.gSceneLayers)) \
            if self.gSceneLayers[i]]
        debug('Visible Layers: {}'.format((vlayers)))
        debug('Horizon Color: ' \
            '{}'.format(str(self.gBScene.world.horizon_color)))

    #=========================================================================
    #                         _ d u m p O b j e c t I n f o
    #=========================================================================
    def _dumpRootObjectInfo(self):
        idx = 0
        debug('\n[object info]')
        for bObject in self.gRootObjects:
            olayers = [i for i in range(len(bObject.layers)) \
                if bObject.layers[i]]
            ccount = _getConstraintCount(bObject)
            debug('Object ({}): ' \
                'Name={}, Type={}, Export={}, Layers={}, NodeAnim={}, ' \
                'Constraints={}'.format(idx,
                bObject.name, bObject.type, bObject.irrb_node_export,
                str(olayers), _hasNodeAnimations(bObject), ccount))
            if ccount > 0:
                ccount = 1
                for c in bObject.constraints:
                    if c.type == 'RIGID_BODY_JOINT':
                        debug('    Constraint ({}): Type={}'.format(ccount,
                        c.pivot_type))
                    ccount += 1

            idx += 1

    #=========================================================================
    #                       _ d u m p A n i m a t i o n I n f o
    #=========================================================================
    def _dumpAnimationInfo(self):
        debug('\n[animation info]')
        debug('fpsbase: {:.4f}'.format(self.gBScene.render.fps_base))
        debug('    fps: {}'.format(self.gBScene.render.fps))
        debug(' sFrame: {}'.format(self.gBScene.frame_start))
        debug(' eFrame: {}'.format(self.gBScene.frame_end))

    #=========================================================================
    #                           _ r u n W a l k T e s t
    #=========================================================================
    def _runWalkTest(self, executableName=None):
        global gWTDirectory, gWTCmdLine, gWTConfigParm, gWTConfigParmGen

        if executableName:
            gWTDirectory = os.path.dirname(executableName)
            gWTCmdLine = executableName
            gWTConfig = ''
        else:
            gWTDirectory = os.path.dirname(self.gWalkTestPath)
            if self.gExportPack:
                gWTCmdLine = '{}-p {}'.format(
                    self.gWalkTestPath[:self.gWalkTestPath.find('-i')],
                    self.gScenePackName)
            else:
                gWTCmdLine = self.gWalkTestPath.replace('$1',
                    flattenPath(self.gSceneFileName)).replace('$2',
                    filterPath(self.gBaseDir))

            gWTConfigParm = '{}{}default.cfg'.format(gWTDirectory, os.sep)
            if os.path.exists(gWTConfigParm):
                os.unlink(gWTConfigParm)
            f = open(gWTConfigParm, 'w')
            f.write(self.gCfgString)
            f.close()
            
            gWTConfigParmGen = os.path.splitext(self.gSceneFileName)[0] + '.cfg'
            if os.path.exists(gWTConfigParmGen):
                os.unlink(gWTConfigParmGen)
            f = open(gWTConfigParmGen, 'w')
            f.write(self.gCfgStringGen)
            f.close()

            gWTConfigParm = ' -c "{}"'.format(gWTConfigParm)

        subprocess.Popen(gWTCmdLine + gWTConfigParm, shell=True,
            cwd=gWTDirectory)

    #=========================================================================
    #                        _ g e t C h i l d r e n
    #=========================================================================
    def _getChildren(self, obj):
        obs = self.gBScene.objects
        return [ob for ob in obs if ob.parent == obj]

    #=========================================================================
    #                 _ o b j e c t I n V i s i b l e L a y e r
    #=========================================================================
    def _objectInVisibleLayer(self, obj):
        for l in range(len(obj.layers)):
            if obj.layers[l] and self.gSceneLayers[l]:
                return True
        return False

    #=========================================================================
    #                  _ e x p o r t N o d e A n i m a t i o n s
    #=========================================================================
    def _exportNodeAnimations(self, bObject):
        if not self._objectInVisibleLayer(bObject):
            return

        if self.gSelectedObjectsOnly == 1 and not bObject.select:
            return

        if not bObject.animation_data:
            return

        # export active
        if bObject.animation_data.action:
            if _actionContainsLocRotScale(bObject.animation_data.action):
                self.gIScene.writeAnimation(self.sfile,
                    bObject.animation_data.action)

        # export NLA Tracks
        if bObject.animation_data.nla_tracks:
            for track in bObject.animation_data.nla_tracks:
                for strip in track.strips:
                    if _actionContainsLocRotScale(strip.action):
                        self.gIScene.writeAnimation(self.sfile, strip.action)

    #=========================================================================
    #                       _ h a s A r m a t ur e
    #=========================================================================
    def _hasArmature(self, bObject):

        for m in bObject.modifiers:
            if m.type == 'ARMATURE':
                return True
        return False

    #=========================================================================
    #                     _ h a s A n i m a t i o n s
    #=========================================================================
    def _hasAnimations(self, bObject):

        boneNames = []
        for m in bObject.modifiers:
            if m.type == 'ARMATURE':
                temp = [bone.name for bone in m.object.data.bones]
                for n in temp:
                    boneNames.append(n)

        if len(boneNames) == 0:
            return False

        for action in bpy.data.actions:
            curvePaths = [curve.data_path for curve in action.fcurves]
            for path in curvePaths:
                found = False
                for name in boneNames:
                    if path.find(name) >= 0:
                        return True

        return False

    #=========================================================================
    #                          _ e x p o r t O b j e c t
    #=========================================================================
    def _exportObject(self, bObject):
        if not bObject.irrb_node_export or \
            not self._objectInVisibleLayer(bObject):
            return

        type = bObject.type

        writeObject = True
        if self.gSelectedObjectsOnly == 1 and not bObject.select:
            writeObject = False

        #
        # Use 'irrb_node_type' to determine the Irrlicht scene node type.
        # If NT_DEFAULT, set node type based on Blender object type.
        #
        itype = NT_DEFAULT
        if 'irrb_node_type' in bObject:
            itype = bObject['irrb_node_type']

        writeTail = True

        if writeObject:
            if itype != NT_DEFAULT:
                if itype == NT_SKYBOX:
                    if self.sfile:
                        sImages = self._validateSkyBox(bObject)
                        if sImages == None:
                            writeTail = False
                        else:
                            self.gIScene.writeNodeHead(self.sfile,
                                self.gObjectLevel, 'skyBox')
                            self.gIScene.writeSkyBoxNodeData(self.sfile,
                                bObject, sImages, self.gObjectLevel)
                            for image in sImages.keys():
                                self._saveImage(sImages[image].image)
                elif itype == NT_SKYDOME:
                    if self.sfile:
                        sImage = self._validateSkyDome(bObject)
                        if sImage == None:
                            writeTail = False
                        else:
                            self.gIScene.writeNodeHead(self.sfile,
                                self.gObjectLevel, 'skyDome')
                            self.gIScene.writeSkyDomeNodeData(self.sfile,
                                bObject, sImage, self.gObjectLevel)
                            self._saveImage(sImage)
                elif itype == NT_VOLUMETRICLIGHT:
                    if self.sfile:
                        sImage = self._validateVolumeLight(bObject)
                        self.gIScene.writeNodeHead(self.sfile,
                            self.gObjectLevel, 'volumeLight')
                        self.gIScene.writeVolumeLightNodeData(self.sfile,
                            bObject, self.gObjectLevel)
                        if sImage:
                            self._saveImage(sImage)
                elif itype == NT_WATERSURFACE:
                    if self.sfile:
                        self.gIScene.writeNodeHead(self.sfile,
                            self.gObjectLevel, 'waterSurface')
                    self._exportMesh(bObject)
                    self.gObjectCount += 1
                elif itype == NT_BILLBOARD:
                    if self.sfile:
                        bbImage = self._validateBillboard(bObject)
                        if bbImage == None:
                            writeTail = False
                        else:
                            self.gIScene.writeNodeHead(self.sfile,
                                self.gObjectLevel, 'billBoard')
                            self.gIScene.writeBillboardNodeData(self.sfile,
                                bObject, bbImage, self.gObjectLevel)
                            self._saveImage(bbImage)
                elif itype == NT_CUSTOM:
                    self.gIScene.writeNodeHead(self.sfile, self.gObjectLevel,
                        bObject.irrb_custom_node_type)
                    if type == 'MESH':
                        self._exportMesh(bObject)
                    else:
                        self.gIScene.writeEmptyObject(self.sfile, bObject,
                            self.gObjectLevel)                        
                    self.gObjectCount += 1                    
                else:
                    # display invalid "inodetype" warning
                    addWarning('Object "{}", has invalid ' \
                        '"inodetype."'.format(bObject.name))
                    writeTail = False
            elif type == 'MESH':
                if self.sfile:
                    #
                    # should check if mesh contains animations...
                    #
                    hasArmature = self._hasArmature(bObject)
                    ntype = 'mesh'
                    if hasArmature and self.gExportAnimations:
                        ntype = 'animatedMesh'
                    elif bObject.irrb_node_octree:
                        ntype = 'octTree'
                    self.gIScene.writeNodeHead(self.sfile, self.gObjectLevel,
                        ntype)
                self._exportMesh(bObject)
                self.gObjectCount += 1
            elif (type == 'LAMP'):
                if self.sfile and self.gExportLights:
                    self.gIScene.writeNodeHead(self.sfile, self.gObjectLevel,
                        'light')
                    self.gIScene.writeLightNodeData(self.sfile, bObject,
                        self.gObjectLevel)
                    self.gLightCount += 1
                else:
                    writeTail = False
            elif (type == 'CAMERA'):
                if self.sfile and self.gExportCameras:
                    self.gIScene.writeNodeHead(self.sfile, self.gObjectLevel,
                        'camera')
                    self.gIScene.writeCameraNodeData(self.sfile, bObject,
                        self.gObjectLevel)
                    self.gCameraCount += 1
                else:
                    writeTail = False
            elif type == 'EMPTY':
                if self.sfile:
                    self.gIScene.writeNodeHead(self.sfile, self.gObjectLevel,
                        'empty')
                    self.gIScene.writeEmptyObject(self.sfile, bObject,
                        self.gObjectLevel)
                else:
                    writeTail = False
            else:
                writeTail = False

        #
        # If the object contains children, then export using a recursive
        # call to _exportObject().  This effectively links the children in the
        # scene (.irr) file:
        #   <parent node header>
        #       <parent node data>
        #       <child node header>
        #           <child node data>
        #       <child node tail>
        #   <parent node tail>
        #
        self.gObjectLevel += 1
        cObjects = self._getChildren(bObject)
        for cObject in cObjects:
            self._exportObject(cObject)
        self.gObjectLevel -= 1

        if writeObject and (self.sfile != None) and writeTail:
            self.gIScene.writeNodeTail(self.sfile, self.gObjectLevel)

    #=========================================================================
    #                     _ v a l i d a t e B i l l b o a r d
    #=========================================================================
    def _validateBillboard(self, bObject):
        mesh = bObject.data

        if bObject.type != 'MESH':
            msg = 'Ignoring billboard: {}, ' \
                'not a mesh object.'.format(mesh.name)
            addWarning(msg)
            return None

        if len(mesh.uv_textures) == 0:
            msg = 'Ignoring billboard: {}, no UV Map.'.format(mesh.name)
            addWarning(msg)
            return None

        faces = mesh.faces
        if len(faces) != 1:
            msg = 'Ignoring billboard: {}, ' \
                'invalid face count: {}'.format(mesh.name, len(faces))
            addWarning(msg)
            return None

        bImage = mesh.uv_textures[0].data[faces[0].index].image
        return bImage
    
    
    #=========================================================================
    #                    _ g e t S k y B o x T e x t u r e s
    #=========================================================================
    def _getSkyBoxTextures(self, obj):
    
        if len(obj.material_slots) < 1:
            addWarning('SkyBox missing material')
            return None
    
        mat = obj.material_slots[0].material
        if not mat:
            addWarning('SkyBox missing material')
            return None
        
        tslots = [mat.texture_slots[i] for i in range(len(mat.texture_slots)) \
                  if mat.texture_slots[i]]

        if len(tslots) < 6:
            addWarning('SkyBox material "{}" missing required textures')
            return None

        tnames = ['left', 'right', 'top', 'bottom', 'front', 'back']    
    
        tcount = 0
    
        textures = {}
    
        for tslot in tslots:
            tex = tslot.texture
            tname = tex.name.lower()
            if (tex.type == 'IMAGE') and (tname in tnames):
                tcount += 1
                tnames.remove(tname)
                textures[tname] = tex
    
        if (tcount >= 6) and len(tnames) == 0:
            return textures
    
        addWarning('SkyBox material "{}" missing required textures')
        return None

    #=========================================================================
    #                        _ v a l i d a t e S k y B o x
    #=========================================================================
    def _validateSkyBox(self, bObject):
        mesh = bObject.data

        if bObject.type != 'MESH':
            msg = 'Ignoring skybox: {}, not a mesh object.'.format(mesh.name)
            addWarning(msg)
            return None
                
        return self._getSkyBoxTextures(bObject)


    #=========================================================================
    #                      _ v a l i d a t e S k y D o m e
    #=========================================================================
    def _validateSkyDome(self, bObject):
        mesh = bObject.data

        if bObject.type != 'MESH':
            msg = 'Ignoring skydome: {}, not a mesh object.'.format(mesh.name)
            addWarning(msg)
            return None
        
        mat = bObject.material_slots[0].material
        if not mat:
            addWarning('SkyDome missing material')
            return None
        
        tslots = [mat.texture_slots[i] for i in range(len(mat.texture_slots)) \
                  if mat.texture_slots[i]]

        if len(tslots) < 1:
            addWarning('SkyDome material "{}" missing required texture'.format(mat.name))
            return None
        
        tex = tslots[0].texture
        if tex.type == 'IMAGE':
            return tex.image
        
        addWarning('SkyDome textures slot not an image')
        return None

    #=========================================================================
    #                _ v a l i d a t e V o l u m e L i g h t
    #=========================================================================
    def _validateVolumeLight(self, bObject):
        mesh = bObject.data

        if bObject.type != 'MESH':
            msg = 'Ignoring volume light: {}, not a mesh object.'.format(mesh.name)
            addWarning(msg)
            return None

        if len(mesh.uv_textures) == 0:
            msg = 'Volume light: {}, '\
                'texture not assigned.'.format(mesh.name)
            addWarning(msg)
            return None

        faces = mesh.faces
        if len(faces) < 1:
            msg = 'Ignoring volume light: {}, ' \
                'invalid face count: {}'.format(mesh.name, len(faces))
            addWarning(msg)
            return None

        # use image assigned to 1st uv layer
        return mesh.uv_textures[0].data[faces[0].index].image

    #=========================================================================
    #                    _ h a s M e s h B e e n E x p o r t e d
    #=========================================================================
    # Blender treats object/datablock names that only differ in case as
    # NOT equal.  Therefore 'Cube' is not the same as 'cube'.  This doesn't
    # work for exporters running on windows without internally renaming the
    # mesh to Cube.001.  Our choice is to display an error message - the
    # generated scene/meshes will likely NOT be correct.
    #
    def _hasMeshBeenExported(self, meshName):
        result = meshName in self.gExportedMeshes
        if not result:
            result = meshName.lower() in self.gExportedMeshesLC
            if result:
                self.gMeshNameConflicts.append(meshName)
        return result

    #=========================================================================
    #                 _ a d d M e s h T o E x p o r t e d L i s t
    #=========================================================================
    def _addMeshToExportedList(self, meshName, orgPath, scenePath):
        if self._hasMeshBeenExported(meshName):
            return

        self.gExportedMeshes[meshName] = (orgPath, scenePath)
        self.gExportedMeshesLC.append(meshName.lower())

    #=========================================================================
    #                  _ h a s S k e l B e e n E x p o r t e d
    #=========================================================================
    def _hasSkelBeenExported(self, skelName):
        result = skelName in self.gExportedSkels
        if not result:
            result = skelName.lower() in self.gExportedSkelsLC
            if result:
                self.gSkelNameConflicts.append(skelName)
        return result
    #=========================================================================
    #                 _ a d d S k e l T o E x p o r t e d L i s t
    #=========================================================================
    def _addSkelToExportedList(self, skelName, skelFilePath, scenePath):
        if self._hasSkelBeenExported(skelName):
            return

        self.gExportedSkels[skelName] = (skelFilePath, scenePath)
        self.gExportedSkelsLC.append(skelName.lower())

    #=========================================================================
    #                           _ c o n v e r t M e s h
    #=========================================================================
    def _convertMesh(self, iname, oname):
        self.gGUI.updateStatus('Creating Binary Mesh: ' + oname)
        meshcvt = self.gMeshCvtPath
        directory = os.path.dirname(meshcvt)

        cmdline = '{} -v {} -i "{}" -o "{}" -a "{}"'.format(meshcvt,
            self.gIrrlichtVersion, iname, oname, filterPath(self.gBaseDir))

        try:
            subprocess.call(cmdline, shell=True, cwd=directory)
        except:
            self.gFatalError = 'Error Converting To Binary Mesh. ' \
                'Check imeshcvt setup.'

    #=========================================================================
    #                      _ s a v e P a c k e d T e x t u r e
    #=========================================================================
    def _savePackedTexture(self, bImage, filename):
        self.gGUI.updateStatus('Saving Packed Texture ' + filename + '...')

        if self.gTexExtension != '.???':
            iTGAWriter.writeTGA(bImage, filename, True)
        else:
            if os.path.exists(filename):
                os.unlink(filename)
            #
            # bImage.save_as(file_type='PNG',filepath=filename, copy=True)
            saveName = bImage.filepath
            bImage.filepath = filename
            bImage.save()
            bImage.filepath = saveName

    #=========================================================================
    #                      _ c o p y E x t e r n a l I m a g e
    #=========================================================================
    def _copyExternalImage(self, bImage, filename):
        ofilename = os.path.normpath(bpy.path.abspath(bImage.filepath))
        self.gGUI.updateStatus('Copying external image ;' \
            '{} to {}'.format(ofilename, filename))
        try:
            shutil.copy2(ofilename, filename)
        except:
            self.gGUI.updateStatus('Error copying external image ' \
                '{}'.format(ofilename))

    #=========================================================================
    #                            _ s a v e I m a g e
    #=========================================================================
    def _saveImage(self, bImage):
        if bImage in self.gExportedImages:
            return
        filename = self.getImageFileName(bImage, 1)
        filename0 = self.getImageFileName(bImage, 0)
        self.gExportedImages[bImage] = (filename, filename0)
        if filename == None:
            return
        if bImage.packed_file != None:
            self._savePackedTexture(bImage, filename)
        elif self.gCopyImages:
            self._copyExternalImage(bImage, filename)

    #=========================================================================
    #                            _ e x p o r t M e s h
    #=========================================================================
    def _exportMesh(self, bObject):
        meshData = bObject.data
        oName = bObject.name
        debug('\n[Mesh - ob:{}, me:{}]'.format(oName, meshData.name))

        self.gMeshFileName = self.gMeshDir + meshData.name + '.irrmesh'
        binaryMeshFileName = ''
        if self.gBinary:
            binaryMeshFileName = (self.gMeshDir +
                    meshData.name + '.irrbmesh')

        self.gGUI.updateStatus('Exporting Mesh: {}, ' \
            'Object: {}'.format(meshData.name, oName))
        alreadyExported = self._hasMeshBeenExported(meshData.name)
        if len(meshData.vertices) == 0:
            msg = 'ignoring mesh: {}, no vertices'.format(meshData.name)
            addWarning(msg)
            return

        #
        # write scene node data to scene (.irr) file
        #
        sceneMeshFileName = None
        meshFileName = self.gMeshFileName
        if self.sfile != None:
            meshFileName = os.path.relpath(self.gMeshFileName, self.gBaseDir)

            sceneMeshFileName = meshFileName
            if self.gBinary:
                fname, fext = os.path.splitext(meshFileName)
                sceneMeshFileName = fname + '.irrbmesh'

        #
        # have we already exported this mesh data block?
        #
        if not alreadyExported:

            try:
                file = open(self.gMeshFileName, 'w')
            except:
                pass

            irrMesh = iMesh(bObject, self, True)
            if irrMesh.createMeshBuffers() == True:
                if self.gGUI.isExportCanceled():
                    file.close()
                    return

                irrMesh.writeMeshData(file)
                self._addMeshToExportedList(meshData.name,
                    self.gMeshFileName, sceneMeshFileName)

                if self.gGUI.isExportCanceled():
                    file.close()
                    return

                self.gVertCount += irrMesh.getVertexCount()
                self.gFaceCount += irrMesh.getFaceCount()

                # write image(s) if any
                for k, v in irrMesh.getMaterials().items():
                    if self.gGUI.isExportCanceled():
                        file.close()
                        return

                    images = v.getMaterial().getImages()
                    for image in images:
                        self._saveImage(image)

                # release mesh buffer memory
                irrMesh.releaseMeshBuffers()

            file.close()
            file = None
            #
            # if requested, convert to binary (.irrbmesh) using "imeshcvt".
            #
            if self.gBinary:
                self._convertMesh(self.gMeshFileName, binaryMeshFileName)

        # write mesh scene node data to scene (.irr) file
        if self.sfile != None:
            self.gIScene.writeMeshObject(self.sfile, sceneMeshFileName,
                bObject, self.gObjectLevel, self.gExportPhysics)
            
    #=========================================================================
    #                              g e t T e x P a t h
    #=========================================================================
    def getTexPath(self):
        if self.gTexPath.strip() == '':
            return self.gTexDir
        return self.gTexPath

    #=========================================================================
    #                              g e t T e x E x t
    #=========================================================================
    def getTexExt(self):
        return self.gTexExtension

    #=========================================================================
    #                       g e t I m a g e F i l e N a m e
    #=========================================================================
    # which: 0-texture path, full filename
    def getImageFileName(self, bImage, which):
        if not bImage:
            return None

        imageName = bImage.name
        if imageName in self.gImageInfo:
            return self.gImageInfo[imageName][which]

        fullFileName = bImage.filepath
        #
        # check for relative path and expand if necessary
        #
        if fullFileName[0:2] == '//':
            fullFileName = os.path.normpath(bpy.path.abspath(fullFileName))
        dirname = os.path.dirname(fullFileName)
        exists = False
        try:
            file = open(fullFileName, 'r')
            file.close()
            exists = True
        except:
            pass

        #
        # it is possible that a blender gen'd image was saved without an
        # extension.  in this case the full filename won't contain the
        # extension but the image name will...
        #
        ext = os.path.splitext(fullFileName)[1]
        if not exists and (ext == ''):
            checkName = dirname + os.path.sep + imageName
            try:
                file = open(checkName, 'r')
                file.close()
                exists = True
                fullFileName = checkName
            except:
                pass

        if (bImage.packed_file != None) or not exists:
            fileName = bImage.name
            fileExt = ''
        else:
            fileName, fileExt = os.path.splitext( \
                os.path.basename(fullFileName))

        debug('\n[Image]')
        debug('imageName: ' + imageName)
        debug('org fullFileName: ' + bImage.filepath)
        debug('fullFileName: ' + fullFileName)
        debug('dirname: ' + dirname)
        debug('fileName: ' + fileName)
        debug('fileExt: ' + fileExt)

        try:
            debug('bImage.file_format: {}'.format(bImage.file_format))
            debug('bImage.depth: {}'.format(bImage.depth))
            debug('bImage.source: {}'.format(bImage.source))
            debug('bImage.packed_file: {}'.format(bImage.packed_file))
            debug('bImage.library: {}'.format(bImage.library))
            debug('exists on disk: {}'.format(exists))
        except:
            debug('error accessing image properties for: ' \
                '{}'.format(bImage.name))
            return None

        result = '???'
        ext = fileExt
        if self.gTexExtension != '.???':
            ext = self.gTexExtension

        if (bImage.packed_file != None) or self.gCopyImages:
            result = os.path.relpath(self.gTexDir + fileName + ext,
                     self.gBaseDir)
        else:
            result = ls.path.relpath(fullFileName, self.gBaseDir)

        result0 = result

        result = fullFileName
        if self.gTexExtension != '.???':
            result = self.gTexDir + fileName + ext
        else:
            result = self.gTexDir + fileName + fileExt
        debug('result0: {}'.format(result0))
        debug('result1: {}'.format(result))
        self.gImageInfo[imageName] = (result0, result)
        if which == 0:
            return result0
        return result

    #=========================================================================
    #                              d o E x p o r t
    #=========================================================================
    def doExport(self):
        self.gFatalError = None
        self.gImageInfo = {}

        self.gGUI.updateStatus('Exporting...')
        start = time.clock()

        # exit edit mode if necessary
        editMode = False
        active_obj = self.gContext.active_object
        if active_obj != None:
            editMode = (active_obj.mode == 'EDIT')
        if editMode:
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        #
        # init tracking variables
        #
        self.gActions = {}
        self.gRootObjects = []
        self.gExportedMeshes = {}
        self.gExportedMeshesLC = []
        self.gMeshNameConflicts = []
        self.gExportedSkels = {}
        self.gExportedSkelsLC = []
        self.gSkelNameConflicts = []
        self.gExportedImages = {}
        self.gExportedNodeAnimations = []

        #
        # export objects from the current scene
        #
        self.gBScene = self.gContext.scene
        self.gSceneLayers = self.gBScene.layers

        self.gAnimationLength = float(self.gBScene.frame_end -
            self.gBScene.frame_start) / self.gBScene.render.fps

        #self.gActions = Blender.Armature.NLA.GetActions()

        #
        # initialize .irr scene file if requested
        #
        logName = ''
        if self.gCreateScene:
            try:
                if not self.gSceneDir.endswith(os.path.sep):
                    self.gSceneDir += os.path.sep

                self.gSceneFileName = (self.gSceneDir +
                    self.gBScene.name + '.irr')
                self.gScenePackName = (self.gSceneDir +
                    self.gBScene.name + '.zip')
                self.sfile = open(self.gSceneFileName, 'w')
                self.gIScene = iScene(self)
                self.gIScene.writeSceneHeader(self.sfile, self.gBScene,
                    self.gExportPhysics)
            except:
                self.sfile = None
                self.gSceneFileName = None
                print('write Scene error:', sys.exc_info()[0])
                raise

        logName = self.gBaseDir
        if not logName.endswith(os.path.sep):
            logName += os.path.sep
        logName += 'irrb.log'

        try:
            openLog(logName)
        except:
            self.gFatalError = 'Error Opening (+w) ' \
                'Log File: {}'.format(logName)
            stats = ['Export Failed!']
            stats.append(self.gFatalError)
            self.gGUI.setStatus(stats)
            return

        debug('irrb log ' + iversion)

        self._dumpGeneralInfo()
        self._dumpOptions()
        self._dumpSceneInfo()
        dumpStartMessages()

        self._dumpAnimationInfo()

        for object in self.gBScene.objects:
            if object.parent is None:
                self.gRootObjects.append(object)

        self._dumpRootObjectInfo()

        self.gObjectLevel = 0
        self.gObjectCount = 0
        self.gLightCount = 0
        self.gCameraCount = 0
        self.gVertCount = 0
        self.gFaceCount = 0

        # export object/node animations (loc/rot/scale) to scene file.
        if self.gExportAnimations and self.gCreateScene and self.sfile:
            for bObject in self.gRootObjects:
                self._exportNodeAnimations(bObject)

        for bObject in self.gRootObjects:
            self._exportObject(bObject)
            if (self.gFatalError != None) or (self.gGUI.isExportCanceled()):
                break

        if self.sfile != None:
            self.gIScene.writeSceneFooter(self.sfile)
            self.sfile.close()
            self.sfile = None

        if editMode:
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

        end = time.clock()
        etime = time.strftime('%X %x')
        stats = ['Export Complete - {:.2f} seconds - {}'.format(end - start,
            etime)]
        stats.append('{} Object(s)'.format(self.gObjectCount))
        mcount = len(self.gExportedMeshes)
        if mcount == 1:
            temp = '{} Mesh'
        else:
            temp = '{} Meshes'
        stats.append(temp.format(mcount))
        stats.append('{} Light(s)'.format(self.gLightCount))
        stats.append('{} Image(s)'.format(len(self.gExportedImages)))
        stats.append('{}/{} Verts/Tris'.format(self.gVertCount,
            self.gFaceCount))
        if len(self.gMeshNameConflicts) > 0:
            stats.append('Error: The following meshes contained ' \
                'naming conflicts:')
            for name in self.gMeshNameConflicts:
                stats.append('   ' + name)

        if self.gFatalError != None:
            stats = ['Export Failed!']
            stats.append(self.gFatalError)

        self._dumpStats(stats)

        # setup walktest/executable config parms
        if self.gRunWalkTest:
            self.gCfgString, self.gCfgStringGen = _updateDefaultConfig(self.gBScene)

        if self.gExportPack:
            zipFileName = '{}{}.zip'.format(self.gSceneDir,
                self.gBScene.name)
            self.gGUI.updateStatus(
                'Packing files into "{}"'.format(zipFileName))
            files = [self.gBScene.name + '.irr']
            for name in self.gExportedMeshes.keys():
                files.append(self.gExportedMeshes[name][1])
            for name in self.gExportedSkels.keys():
                files.append(self.gExportedSkels[name][1])
            for name in self.gExportedImages.keys():
                files.append(self.gExportedImages[name][1])

            # delete original files
            if _zipFiles(zipFileName, files, self.gBScene.name + '.irr'):
                os.unlink(self.gSceneDir + self.gBScene.name + '.irr')
                for name in self.gExportedMeshes.keys():
                    meshFileName = self.gExportedMeshes[name][0]
                    os.unlink(meshFileName)
                    if self.gBinary:
                        fname, fext = os.path.splitext(meshFileName)
                        os.unlink(fname + '.irrbmesh')

                for name in self.gExportedImages.keys():
                    if os.path.exists(self.gExportedImages[name][0]):
                        os.unlink(self.gExportedImages[name][0])

        exeFileName = None
        if self.gExportExec:
            wtEnv = os.environ['IWALKTEST']
            # copy iwalktest data to scene directory & zip
            srcDatDir = '{}{}data'.format(os.path.dirname(wtEnv), os.sep)
            dstDatDir = self.gSceneDir + 'data'
            if os.path.exists(dstDatDir):
                shutil.rmtree(dstDatDir)
            shutil.copytree(srcDatDir, dstDatDir)

            datFileName = self.gSceneDir + 'data.zip'
            _zipFiles(datFileName, ['data'], '', False)
            #datFileName = self.gSceneDir + 'data' + os.sep + 'data.zip'
            #E_zipFiles(datFileName, ['fnt','gui','tex'], '', False)

            ext = os.path.splitext(os.path.basename(wtEnv).split()[0])[1]
            exeFileName = '{}{}{}'.format(self.gSceneDir,
                self.gBScene.name, ext)
            self.gGUI.updateStatus(
                'Generating executable "{}"'.format(exeFileName))

            srcFileName = '{}{}{}'.format(os.path.dirname(self.gWalkTestPath),
                os.sep, os.path.basename(self.gWalkTestPath).split()[0])
            resources = [(self.gCfgString, RT_CONFIG),
                (zipFileName, RT_ARCHIVE), (datFileName, RT_ARCHIVE)]
            _makeExecutable(exeFileName, srcFileName, resources)

            # clean up
            os.unlink(zipFileName)
            os.unlink(datFileName)
            shutil.rmtree(dstDatDir)

        closeLog()
        self.gGUI.setStatus(stats)
        self.gActions.clear()
        self.gRootObjects[:] = []
        self.gExportedMeshes = {}
        self.gExportedMeshesLC[:] = []
        self.gMeshNameConflicts[:] = []
        self.gExportedImages = {}
        self.gExportedNodeAnimations[:] = []

        if (self.gFatalError == None) and self.gRunWalkTest:
            self._runWalkTest(exeFileName)

#=============================================================================
#                           I r r b E x p o r t O p
#=============================================================================
class IrrbExportOp(bpy.types.Operator):
    '''Export scene and object info to the native Irrlicht scene (.irr) '''
    '''and mesh (.irrmesh) formats'''
    bl_idname = 'export.irrb'
    bl_label = 'Export'

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    filepath = StringProperty(name='File Path',
        description='File path used for exporting the .irr file',
        maxlen=1024, default='', subtype='DIR_PATH')

    #=========================================================================
    #                                p o l l
    #=========================================================================
    @classmethod
    def poll(cls, context):
        return {'PASS_THROUGH'}

    #=========================================================================
    #                              e x e c u t e
    #=========================================================================
    def execute(self, context):
        global _G

        if not self.properties.filepath:
            raise Exception('filepath not set')

        scene = context.scene

        # save irrb scene UI properties
        _G['export']['scene'] = scene.irrb_export_scene
        _G['export']['selected'] = scene.irrb_export_selected
        _G['export']['lights'] = scene.irrb_export_lights
        _G['export']['cameras'] = scene.irrb_export_cameras
        _G['export']['animations'] = scene.irrb_export_animations
        _G['export']['animation_tails'] = scene.irrb_export_animation_tails
        _G['export']['physics'] = scene.irrb_export_physics
        _G['export']['pack'] = scene.irrb_export_pack
        exportBinary = False
        if 'IMESHCVT' in os.environ:
            _G['export']['binary'] = scene.irrb_export_binary
            if scene.irrb_export_binary:
                exportBinary = True

        walktest = False
        if gHaveWalkTest:
            _G['export']['walktest'] = scene.irrb_export_walktest
            if scene.irrb_export_walktest:
                walktest = True

        if gPlatform == 'Windows':
            scene.irrb_outpath_win = \
                _G['export']['out_directory'] = '{}{}'.format(
                    os.path.dirname(self.properties.filepath), os.sep)
        else:
            scene.irrb_outpath = \
                _G['export']['out_directory'] = '{}{}'.format(
                    os.path.dirname(self.properties.filepath), os.sep)

        runWalkTest = False
        if gWalkTestPath != None:
            runWalkTest = walktest

        self.report({'INFO'}, 'irrb Exporter Start.')
        write(self.properties.filepath, self, context,
              _G['export']['out_directory'],
              scene.irrb_export_scene,
              scene.irrb_export_selected,
              scene.irrb_export_lights,
              scene.irrb_export_cameras,
              scene.irrb_export_animations,
              scene.irrb_export_animation_tails,
              scene.irrb_export_physics,
              scene.irrb_export_pack,
              scene.irrb_export_makeexec,
              exportBinary,
              runWalkTest,
              2,  # irrlicht version index
             )

        return {'FINISHED'}

    #=========================================================================
    #                              i n v o k e
    #=========================================================================
    def invoke(self, context, event):
        if gPlatform == 'Windows':
            self.properties.filepath = context.scene.irrb_outpath_win.strip()
        else:
            self.properties.filepath = context.scene.irrb_outpath.strip()

        if not os.path.exists(self.properties.filepath):
            self.properties.filepath = ''

        # pop the directory select dialog if:
        #     scene irrb_outpath is empty or
        #     coming from "File|Export|Irrlicht" menu or
        #     shift key is down when invoked
        if (self.properties.filepath == '') or (event.shift) or \
           (context.space_data.type == 'INFO'):
            self.properties.filepath = _G['export']['out_directory']
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
        else:
            if gPlatform == 'Windows':
                self.properties.filepath = context.scene.irrb_outpath_win
            else:
                self.properties.filepath = context.scene.irrb_outpath
            return self.execute(context)

#=============================================================================
#                       I r r b W a l k t e s t O p
#=============================================================================
class IrrbWalktestOp(bpy.types.Operator):
    '''Walktest last exported scene'''
    bl_idname = 'scene.irrb_walktest'
    bl_label = 'Walktest'

    @classmethod
    def poll(cls, context):
        return {'PASS_THROUGH'}

    def execute(self, context):
        if len(gWTCmdLine) > 0:
            # save updated walktest config settings
            cfgString, cfgStringGen = _updateDefaultConfig(context.scene)
            
            gWTConfigParm = '{}{}default.cfg'.format(gWTDirectory, os.sep)
            if os.path.exists(gWTConfigParm):
                os.unlink(gWTConfigParm)
            f = open(gWTConfigParm, 'w')
            f.write(cfgString)
            f.close()
            gWTConfigParm = ' -c "{}"'.format(gWTConfigParm)
                        
            if os.path.exists(gWTConfigParmGen):
                os.unlink(gWTConfigParmGen)
            f = open(gWTConfigParmGen, 'w')
            f.write(cfgStringGen)
            f.close()            

            subprocess.Popen(gWTCmdLine + gWTConfigParm, shell=True,
                cwd=gWTDirectory)

        return {'FINISHED'}

#=============================================================================
#                      I r r b S c e n e P r o p s
#=============================================================================
class IrrbSceneProps(bpy.types.Panel):
    bl_label = 'Irrlicht Exporter v{}'.format(iversion)
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, context):
        sceneEnabled = context.scene.irrb_export_scene

        layout = self.layout

        row = layout.row()
        row.operator('export.irrb', icon='RENDER_STILL')
        if len(gWTCmdLine) > 0:
            row = layout.row()
            layout.operator('scene.irrb_walktest', icon='RENDER_STILL')
        row = layout.row()
        if gPlatform == 'Windows':
            layout.prop(context.scene, 'irrb_outpath_win')
        else:
            layout.prop(context.scene, 'irrb_outpath')

        split = layout.split()
        lcol = split.column()
        lcol.prop(context.scene, 'irrb_export_scene')
        sub = lcol.column()
        sub.active = sceneEnabled
        sub.prop(context.scene, 'irrb_export_lights')
        sub = lcol.column()
        sub.active = sceneEnabled
        sub.prop(context.scene, 'irrb_export_cameras')
        lcol.prop(context.scene, 'irrb_export_selected')
        lcol.prop(context.scene, 'irrb_export_animations')
        if context.scene.irrb_export_animations:
            lcol.prop(context.scene, 'irrb_export_animation_tails')

        rcol = split.column()
        sub = rcol.column()
        sub.active = sceneEnabled
        sub.prop(context.scene, 'irrb_export_physics')

        sub = rcol.column()
        sub.active = sceneEnabled
        sub.prop(context.scene, 'irrb_export_pack')

        if gHaveWalkTest:
            sub = rcol.column()
            sub.active = sceneEnabled & gHaveWalkTest
            sub.prop(context.scene, 'irrb_export_makeexec')

        sub = rcol.column()
        sub.active = ('IMESHCVT' in os.environ) & sceneEnabled
        sub.prop(context.scene, 'irrb_export_binary')

        sub = rcol.column()
        sub.active = gHaveWalkTest & sceneEnabled
        sub.prop(context.scene, 'irrb_export_walktest')

        if (gHaveWalkTest and sceneEnabled and\
            context.scene.irrb_export_walktest) or\
            context.scene.irrb_export_makeexec:

            if gWalkTestPath64:
                row = layout.row()
                row.prop(context.scene, 'irrb_wt_bits', expand=True)

            row = layout.row()
            if context.scene.irrb_export_makeexec:
                row.label('Executable Options:')
            else:
                row.label('Walktest Options:')
            
            split = layout.split()
            lcol = split.column()

            sub = lcol.column()
            sub.prop(context.scene, 'irrb_wt_antialias')

            sub = lcol.column()
            sub.prop(context.scene, 'irrb_wt_vsync')

            sub = lcol.column()
            sub.prop(context.scene, 'irrb_wt_fullscreen')

            sub = lcol.column()
            sub.prop(context.scene, 'irrb_wt_keepaspect')

            rcol = split.column()
            sub = rcol.column()
            sub.prop(context.scene, 'irrb_wt_showhelp')

            sub = rcol.column()
            sub.prop(context.scene, 'irrb_wt_debug')

            sub = rcol.column()
            sub.prop(context.scene, 'irrb_wt_stencilbuffer')

            if gPlatform == 'Windows':
                row = layout.row()
                row.label('Video Driver')
                row.prop(context.scene, 'irrb_wt_driver', '')

            row = layout.row()
            row.label('Resolution')
            row.prop(context.scene, 'irrb_wt_resolution', '')

            if context.scene.irrb_wt_resolution == 'RES_CUSTOM':
                row = layout.row()
                split = layout.split()
                lcol = split.column()
                sub = lcol.column()
                sub.prop(context.scene, 'irrb_wt_resx')

                rcol = split.column()
                sub = rcol.column()
                sub.prop(context.scene, 'irrb_wt_resy')

            row = layout.row()
            row.label('Velocity')
            row.prop(context.scene, 'irrb_wt_velocity', '')

            row = layout.row()
            row.label('Angular Velocity')
            row.prop(context.scene, 'irrb_wt_avelocity', '')

            row = layout.row()
            row.label('Velocity Damping')
            row.prop(context.scene, 'irrb_wt_velocitydamp', '')

            if context.scene.irrb_export_physics:
                row = layout.row()
                row.label('Physics System')
                row.prop(context.scene, 'irrb_wt_phycolsys', '')

                row = layout.row()
                row.label('Character Width')
                row.prop(context.scene, 'irrb_wt_char_width', '')

                row = layout.row()
                row.label('Character Height')
                row.prop(context.scene, 'irrb_wt_char_height', '')

                row = layout.row()
                row.label('Character Step Height')
                row.prop(context.scene, 'irrb_wt_char_stepheight', '')

                row = layout.row()
                row.label('Character Jump Speed')
                row.prop(context.scene, 'irrb_wt_char_jumpspeed', '')

                if context.scene.irrb_wt_phycolsys == 'PCS_BULLET':
                    row = layout.row()
                    row.label('Broadphase Alogrithm')
                    row.prop(context.scene, 'irrb_wt_bullet_broadphase', '')

                    row = layout.row()
                    row.label('Maximum SubSteps')
                    row.prop(context.scene, 'irrb_wt_bullet_substeps', '')

                    row = layout.row()
                    row.label('Time Step')
                    row.prop(context.scene, 'irrb_wt_bullet_timestep', '')

#=============================================================================
#                     I r r b M a t e r i a l P r o p s
#=============================================================================
class IrrbMaterialProps(bpy.types.Panel):
    bl_label = 'Irrlicht'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    @classmethod
    def poll(cls, context):
        return context.material

    def draw(self, context):
        layout = self.layout

        mat = context.material

        row = layout.row()
        row.operator('export.irrb', icon='RENDER_STILL')

        row = layout.row()
        row.label(text='Type')
        row.prop(mat, 'irrb_type', '')

        mtype = EMT_SOLID
        if 'irrb_type' in mat:
            mtype = mat['irrb_type']

        if mtype == EMT_CUSTOM:
            row = layout.row()
            row.label(text='Custom Name')
            row.prop(mat, 'irrb_custom_name', '')

        row = layout.row()
        row.prop(mat, 'irrb_lighting')
        row.prop(mat, 'irrb_gouraud')

        row = layout.row()
        row.prop(mat, 'irrb_backcull')
        row.prop(mat, 'irrb_frontcull')

        row = layout.row()
        row.prop(mat, 'irrb_zwrite_enable')
        row.prop(mat, 'irrb_fog')

        row = layout.row()
        row.prop(mat, 'irrb_normalize_normals')
        row.prop(mat, 'irrb_use_mipmaps')

        row = layout.row()
        row.prop(mat, 'irrb_link_diffuse')
        
        row = layout.row()
        row.label('ZBuffer')
        row.prop(mat, 'irrb_zbuffer', '')

        row = layout.row()
        row.label('Antialiasing')
        row.prop(mat, 'irrb_antialiasing', '')

        row = layout.row()
        row.label('Color Material')
        row.prop(mat, 'irrb_color_material', '')

        row = layout.row()
        row.label(text='Ambient')
        row.prop(mat, 'irrb_ambient', '')
        row.label(text='Diffuse')
        if mat.irrb_link_diffuse:
            row.prop(mat, 'diffuse_color', '')
        else:
            row.prop(mat, 'irrb_diffuse', '')

        row = layout.row()
        row.label(text='Emissive')
        row.prop(mat, 'irrb_emissive', '')
        row.label(text='Specular')
        row.prop(mat, 'specular_color', '')

        row = layout.row()
        row.label('Color Mask:')
        row = layout.row()
        row.prop(mat, 'irrb_color_mask_red')
        row.prop(mat, 'irrb_color_mask_green')
        row = layout.row()
        row.prop(mat, 'irrb_color_mask_blue')
        row.prop(mat, 'irrb_color_mask_alpha')

        row = layout.row()
        row.prop(mat, 'irrb_param1')
        row.prop(mat, 'irrb_param2')

        row = layout.row()
        row.prop(mat, 'irrb_shininess')
        row.prop(mat, 'irrb_thickness')

        def layoutLayer(layer):
            layout.separator()
            row = layout.row()
            row.label('Layer{}:'.format(layer))
            row = layout.row()
            row.label('U Wrap Mode')
            row.prop(mat, 'irrb_layer{}_wrapu'.format(layer), '')
            row = layout.row()
            row.label('V Wrap Mode')
            row.prop(mat, 'irrb_layer{}_wrapv'.format(layer), '')
            row = layout.row()
            row.label('Filter')
            row.prop(mat, 'irrb_layer{}_filter'.format(layer), '')

            row = layout.row()
            row.label('Anisotropic')
            row.prop(mat, 'irrb_layer{}_anisotropic_value'.format(layer), '')

            row = layout.row()
            row.label('LOD Bias')
            row.prop(mat, 'irrb_layer{}_lodbias'.format(layer), '')

        layoutLayer(1)
        layoutLayer(2)
        layoutLayer(3)
        layoutLayer(4)

#=============================================================================
#                       I r r b O b j e c t P r o p s
#=============================================================================
class IrrbObjectProps(bpy.types.Panel):
    bl_label = 'Irrlicht'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.operator('export.irrb', icon='RENDER_STILL')
        #row = layout.row()
        #row.label(text='Active object is: ' + obj.name, icon='OBJECT_DATA')
        
        split = layout.split()
        lcol = split.column()
        sub = lcol.column()
        sub.label(text='Export Object')
        rcol = split.column()
        sub = rcol.column()
        sub.prop(obj, 'irrb_node_export', text='')

        if not obj.irrb_node_export:
            return

        row = layout.row()
        row.label(text='ID')
        row.prop(obj, 'irrb_node_id')

        if obj.type in ('MESH', 'EMPTY'):
            row = layout.row()
            row.label(text='Node Type')
            row.prop(obj, 'irrb_node_type', '')
            row = layout.row()
            
            if ('irrb_node_type' in obj) and (obj['irrb_node_type'] == NT_CUSTOM):
                row.label(text='Custom Type')
                row.prop(obj, 'irrb_custom_node_type', '')
                row = layout.row()
            
            row.label(text='Automatic Culling')
            row.prop(obj, 'irrb_node_culling', '')
            row = layout.row()
            row.label(text='Hardware Hint')
            row.prop(obj, 'irrb_node_hwhint', '')
            row = layout.row()
            row.label(text='Hint Buffer Type')
            row.prop(obj, 'irrb_node_hwhint_bt', '')
        elif obj.type == 'CAMERA':
            row = layout.row()
            row.label(text='Target')
            row.prop(obj, 'irrb_cam_target', '')
            row = layout.row()
            
            row.label(text='Up Vector')
            row.prop(obj, 'irrb_cam_upvector', '')
            row = layout.row()
            
            row.label(text='FOV')
            row.prop(obj, 'irrb_cam_fov', '')
            row = layout.row()
            
            row.label(text='Aspect')
            row.prop(obj, 'irrb_cam_aspect', '')
            row = layout.row()
            
            row.label(text='ZNear')
            row.prop(obj.data, 'clip_start', '')
            row = layout.row()
            
            row.label(text='ZFax')
            row.prop(obj.data, 'clip_end', '')
            row = layout.row()
                        
            row.label(text='Bind Target')
            row.prop(obj, 'irrb_cam_bindtarget', '')
            row = layout.row()
            
        elif obj.type == 'LAMP':
            row = layout.row()
            row.label(text='Light Type')
            row.prop(obj, 'irrb_light_type', '')
            row = layout.row()
                   
            row.label(text='Ambient')
            row.prop(obj, 'irrb_light_ambient', '')
            row = layout.row()

            row.label(text='Diffuse')
            row.prop(obj.data, 'color', '')
            row = layout.row()

            row.label(text='Specular')
            row.prop(obj, 'irrb_light_specular', '')
            row = layout.row()

            row.label(text='Radius')
            row.prop(obj, 'irrb_light_radius', '')
            row = layout.row()

            row.label(text='Outer Cone')
            row.prop(obj, 'irrb_light_outercone', '')
            row = layout.row()

            row.label(text='Inner Cone')
            row.prop(obj, 'irrb_light_innercone', '')
            row = layout.row()

            row.label(text='Fall Off')
            row.prop(obj, 'irrb_light_falloff', '')
            row = layout.row()

            row.label(text='Cast Shadows')
            row.prop(obj, 'irrb_light_castshadows', '')
            row = layout.row()
            
            row.label(text='Attenuation')
            row.prop(obj, 'irrb_light_attenuation', '')
            row = layout.row()
            
        if obj.type == 'MESH':
            split = layout.split()
            lcol = split.column()
            sub = lcol.column()
            sub.label(text='Octree Node')
            rcol = split.column()
            sub = rcol.column()
            sub.prop(obj, 'irrb_node_octree', text='')

            if obj.irrb_node_octree:
                row = layout.row()
                row.label(text='Octree Min Poly Count')
                row.prop(obj, 'irrb_node_octree_polys')

        if 'irrb_node_type' in obj:
            itype = obj['irrb_node_type']
            if itype == NT_SKYDOME:
                row = layout.row()
                row.label('Sky Dome Options:')
                row = layout.row()
                row.prop(obj, 'irrb_dome_hres')
                row.prop(obj, 'irrb_dome_vres')
                row = layout.row()
                row.prop(obj, 'irrb_dome_texpct')
                row.prop(obj, 'irrb_dome_spherepct')
                row = layout.row()
                row.prop(obj, 'irrb_dome_radius')
            elif itype == NT_WATERSURFACE:
                row = layout.row()
                row.label('Water Surface Options:')
                row = layout.row()
                row.prop(obj, 'irrb_water_wavelength')
                row = layout.row()
                row.prop(obj, 'irrb_water_wavespeed')
                row = layout.row()
                row.prop(obj, 'irrb_water_waveheight')
            elif itype == NT_VOLUMETRICLIGHT:
                row = layout.row()
                row.label('Volumetric Light Options:')
                row = layout.row()
                row.prop(obj, 'irrb_volight_distance')
                row = layout.row()
                row.prop(obj, 'irrb_volight_subu')
                row = layout.row()
                row.prop(obj, 'irrb_volight_subv')
                row = layout.row()
                row.prop(obj, 'irrb_volight_footcol')
                row = layout.row()
                row.prop(obj, 'irrb_volight_tailcol')
                row = layout.row()
                row.prop(obj, 'irrb_volight_dimension')
            elif itype == NT_BILLBOARD:
                row = layout.row()
                row.label('Billboard Options:')
                row = layout.row()
                row.prop(obj, 'irrb_billboard_shade_top')
                row = layout.row()
                row.prop(obj, 'irrb_billboard_shade_bot')
                row = layout.row()
                row.prop(obj, 'irrb_billboard_width')
                row = layout.row()
                row.prop(obj, 'irrb_billboard_height')

if __name__ == '__main__':
    register()
