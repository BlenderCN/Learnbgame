"""
.. module:: thea_globals
   :platform: OS X, Windows, Linux
   :synopsis: Global variables, logger and functions to read/write the config file

.. moduleauthor:: Grzegorz Rakoczy <grzegorz.rakoczy@solidiris.com>


"""

import bpy
import os
from configparser import SafeConfigParser


IrIsRunning  = False
IrIsPaused  = False
IrPreviewFileName = "ir.bmp"
materialUpdated = False
materialUpdatesNumber = 0
worldUpdated = False
engineUpdated = False
sceneUpdated = False
objectsUpdated = []
displayUpdated = False
displayPreset = False
displayReset = -2
displaySet = "None"
lampUpdated = False
sectionFrame = False
sectionFrameEnabled = False
#sectionFrameTrans = (0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1, 0.027856)
sectionFrameTrans = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
preview3DAlpha = 0.0
timerDelay = 0.1
showMatGui = True
frame_px = False
minIRpreviewSize = 2000
useLUT = False
nameBasedLUT = False
panelMatPreview = True
panelMatHeight = 800
unbiasedPreview = False
previewScene = "Addon"
matTransTable = []
s = None # socket
pixels = None
resX = 0
resY = 0
resolutionDivider = 1
drawText = ""
currentArea = None
currentRegion = None
forceExportGeometry=False
remapIRKeys = False

exportPath = None
theaPath = None
theaDir = None
dataPath = None
currentBlendDir = None
currentBlendFile = None

mainExpObject = ""

#log = None #logger is created while importing thea_render_main module

# import os
# import logging
# from logging import handlers
# import tempfile
#
# log = logging.getLogger('TheaForBlender')
# fh = logging.handlers.RotatingFileHandler(filename=os.path.join(tempfile.gettempdir(), 'TheaForBlender.log'), maxBytes=100000)
# fh.setLevel(logging.DEBUG)
# log.addHandler(fh)
# logging.basicConfig(level=logging.INFO)


def setConfig():
    '''Save configuration file
    '''
    config = SafeConfigParser()
    log.debug("setConfig")

    for path in bpy.utils.script_paths():
        if  os.path.isdir(os.path.join(path,"addons","TheaForBlender")):
            theaConfigFile = os.path.join(path,"addons","TheaForBlender","config.ini")
            config.read(theaConfigFile)
            if not config.has_section('main'):
                config.add_section('main')
            config.set('main', 'useLUT', str(useLUT))
            config.set('main', 'nameBasedLUT', str(nameBasedLUT))
            config.set('main', 'remapIRKeys', str(remapIRKeys))

            with open(theaConfigFile, 'w') as f:
                config.write(f)

def getConfig():
    '''Load configuration to the file
    '''
    config = SafeConfigParser()

    for path in bpy.utils.script_paths():
        theaConfigFile = os.path.join(path,"addons","TheaForBlender","config.ini")
        if os.path.exists(theaConfigFile):
            config.read(theaConfigFile)
            try:
                useLUT = config.getboolean('main', 'useLUT')
                bpy.context.scene.thea_IRFontSize = config.getint('main', 'irfontsize')
            except:
                useLUT = False



def getUseLUT():
    '''get useLUT value from configuration file

        :return: useLUT
        :rtype: bool
    '''

    useLUT = False

    try:
        if getattr(bpy.context, "scene", False):
            return getattr(bpy.context.scene, 'thea_useLUT')
        else:
            return False

        config = SafeConfigParser()
        for path in bpy.utils.script_paths():
            theaConfigFile = os.path.join(path,"addons","TheaForBlender","config.ini")
            if os.path.exists(theaConfigFile):
                config.read(theaConfigFile)
                try:
                    useLUT = config.getboolean('main', 'useLUT')
                except:
                    useLUT = False
    except:
        pass
    return useLUT

def getNameBasedLUT():
    '''get nameBasedLUT value from configuration file

        :return: nameBasedLUT
        :rtype: bool
    '''

    nameBasedLUT = False

    return getattr(bpy.context.scene, 'thea_nameBasedLUT')

    config = SafeConfigParser()
    for path in bpy.utils.script_paths():
        theaConfigFile = os.path.join(path,"addons","TheaForBlender","config.ini")
        if os.path.exists(theaConfigFile):
            config.read(theaConfigFile)
            try:
                nameBasedLUT = config.getboolean('main', 'nameBasedLUT')
            except:
                nameBasedLUT = False
    return nameBasedLUT


def getRemapIRKeys():
    '''get remapIRKeys value from configuration file

        :return: remapIRKeys
        :rtype: bool
    '''

#     log.debug("getRemapIRKeys()")
    remapIRKeys = False


    config = SafeConfigParser()
    for path in bpy.utils.script_paths():
        theaConfigFile = os.path.join(path,"addons","TheaForBlender","config.ini")
        if os.path.exists(theaConfigFile):
            config.read(theaConfigFile)
            try:
                remapIRKeys = config.getboolean('main', 'remapIRKeys')
            except:
                remapIRKeys = False
    return remapIRKeys
