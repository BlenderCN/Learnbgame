
import configparser
import bpy
import bmesh
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from mathutils import Vector, Matrix, Euler
from struct import unpack
import tempfile
import os
import subprocess
from os import listdir
from os.path import isfile, join
from ..config import writeConfig,initConfig,setInstallPath,setChunkPath
from ..dbg import dbg

(config,CHUNK_PATH,PATH) = initConfig()
    
def doImportTex(filePath):
    ScarletPath = "%s\\Scarlet" % PATH
    tempdir  = tempfile.mkdtemp()
    dbg("tempdir: %s" % tempdir)
    prm = ["%s\\ScarletTestApp.exe"%ScarletPath,filePath,"--output",tempdir]
    dbg("execute %s" % prm)
    FNULL = open(os.devnull, 'r')
    try:
        subprocess.check_call(prm,stdin=FNULL, shell=False)
    except:
        pass
    
    onlyfiles = [f for f in listdir(tempdir) if isfile(join(tempdir, f))]
    
    i = 0
    for f in onlyfiles:
        if "Image 0" in f:
            imgPath = "%s\\%s" % (tempdir,f)
            dbg("adding image %s" % imgPath)
            img = bpy.data.images.load(imgPath)
            material = bpy.data.materials.new("Mat%d" % i)
            material.use_shadeless = True
            material.use_face_texture = True
            imtex = bpy.data.textures.new('ImageTex%d' % i ,"IMAGE")
            slot = material.texture_slots.add()
            imtex.image = img
            slot.texture = imtex
            i += 1

class ImportTEX(Operator, ImportHelper):
    bl_idname = "custom_import.import_mhw_tex"
    bl_label = "Load MHW TEX file (.tex)"
    bl_options = {'PRESET'}
 
    filename_ext = ".tex"
 
    filter_glob = StringProperty(default="*.tex", options={'HIDDEN'}, maxlen=255)

    install_path = StringProperty(
            name="Install path.",
            description="Path the contains the Scarlet directory.",
            default=PATH,
    )
    def execute(self, context):
        global PATH,config_filepath,config
        PATH = self.install_path
        if not os.path.isdir(PATH):
            raise Exception("Install path %s not found!" % PATH)
            
        setInstallPath(PATH)
        writeConfig()

        filePath = self.filepath
        doImportTex(filePath)
        
        return {'FINISHED'}

# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportTEX.bl_idname, text="MHW TEX (.tex)")

