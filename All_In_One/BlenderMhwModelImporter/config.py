import base64
import zlib 
import bpy
import bmesh
import os
import configparser
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from mathutils import Vector, Matrix, Euler
from struct import unpack, pack
from .dbg import dbg

def setInstallPath(s):
    global config
    config['DEFAULT']['INSTALL_PATH'] = s

def setChunkPath(cp):
    global config
    config['DEFAULT']['CHUNK_PATH'] = cp

def writeConfig():
    global config_path,config
    f = open(config_filepath,"w+")
    f.write("[DEFAULT]\n")
    for x in config['DEFAULT']:
        f.write("%s=%s\n" % (x,config['DEFAULT'][x]))
    f.close()
    dbg("write config:")
    dbg({section: dict(config[section]) for section in config.sections()})

def initConfig():
    global config_filepath,config,PATH,CHUNK_PATH
    config = configparser.ConfigParser()
    config_path = bpy.utils.user_resource('CONFIG', path='scripts', create=True)
    config_filepath = os.path.join(config_path, "mhw_importer.config")
    dbg("config_filepath: %s" % config_filepath)
    if not os.path.isfile(config_filepath):
        config['DEFAULT']['INSTALL_PATH'] = "d:\\tmp\\test"
        config['DEFAULT']['CHUNK_PATH']   = "d:\\tmp\\chunk"
        writeConfig()
    config.read(config_filepath)
    if 'INSTALL_PATH' in config['DEFAULT']:
        PATH = config['DEFAULT']['INSTALL_PATH']
    else:
        PATH = "d:\\tmp\\test"
    if 'CHUNK_PATH' in config['DEFAULT']:
        CHUNK_PATH = config['DEFAULT']['CHUNK_PATH']
    else:
        CHUNK_PATH = "d:\\tmp\\chunk"
    BMHWI_FOLDER = None
    if "BMHWI_FOLDER" in os.environ:
        BMHWI_FOLDER = os.environ["BMHWI_FOLDER"]
    if BMHWI_FOLDER is None:
        testPath = bpy.utils.user_resource('SCRIPTS', "addons")
        pathToCheck = "%s\\%s" % (testPath,"BlenderMhwModelImporter")
        dbg("checking folder: %s" % pathToCheck)
        if(os.path.isdir(pathToCheck)):
            BMHWI_FOLDER = pathToCheck
    dbg("BMHWI_FOLDER: %s" % BMHWI_FOLDER)
    if not BMHWI_FOLDER is None:
        BMHWI_FOLDER = BMHWI_FOLDER.replace('"','')
        if(not os.path.isdir("%s\\Scarlet" % PATH)):
            PATH = BMHWI_FOLDER
        if(not os.path.isdir(CHUNK_PATH)):
            CHUNK_PATH = BMHWI_FOLDER
    res = (config,CHUNK_PATH,PATH)
    dbg(res)
    return res