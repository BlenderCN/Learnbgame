import bpy
import ATOM_Types
import ctypes
from bpy.app.handlers import persistent
import Properties
import utils
import sys, os

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       FloatVectorProperty,
                       IntVectorProperty,
                       BoolVectorProperty,
                       CollectionProperty)
                       
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       Property,
                       AddonPreferences)

ROOT_PATH = os.path.dirname(__file__)
config = utils.Config(os.path.join(ROOT_PATH, "config.ini"), ADDON_ROOT=ROOT_PATH).config

############### ONLY FOR STANDALONE ADDON RELEASE ################

if config.standalone:

    from . import FileManager, Properties, Types, utils

    bl_info = {
        "name": "ATOM build platform : Windows",
        "author": "BluStroke®",
        "version": (1, 0),
        "blender": (2, 78, 0),
        "location": "",
        "description": "Build game for the windows platform",
        "warning": "",
        "wiki_url": "",
        "category": "System",
        }
    
    def register():
        
        FileManager.register()
        Properties.register()
        Types.register()
        utils.register()

    def unregister():

        FileManager.unregister()
        Properties.unregister()
        Types.unregister()
        utils.unregister()

    if __name__ == "__main__":
        
        register()


#atom_types = importlib.machinery.SourceFileLoader(ATOM_Editor.getModule("ATOM_io")).load_module()


# class WindowsPlatform(atom_types.Platform):

#     target_list = CollectionProperty( type = )
#     def build(self, context):

#         system.os(compiler + args)

#         scene = context.scene

        #scripts

        # if scene.WindowsPlatform.static_link:
        #     script_build = 
        # else:
        #     system.os(compiler + args + "")

#         MODE 		= "Debug"
# TARGET  	= "mingw"
# CXX 		= "../../Programmes/MinGW/bin/g++"
# PLATFORM	= "x86"
# OUT_NAME 	= "Sparkle_Engine"
# OUT_TYPE 	= "exe"
# BIN_PATH 	= MODE + "/bin"
# OBJ_PATH	= MODE + "/obj"
# SRC_PATH	= "Source"
# BIN			= BIN_PATH + "/" + OUT_NAME + "." + OUT_TYPE

# USE_LIBS 	= ["GLFW", "glew"]
# LIBS		= ["glew32.dll", "glfw3", "glfw3dll"]

# LIB_ROOT	= "../../Programmes/Lib/C++"
# LIBS_PATH	= [LIB_ROOT + "/" + i for i in USE_LIBS]

# INCLUDE_PATHS 	= [i + "/include" for i in LIBS_PATH]
# LIB_PATHS 		= [i + "/lib/" + TARGET + "/" + PLATFORM for i in LIBS_PATH]       
# DLLS            = []
# SRCS 	   		= [i for i in listdir(SRC_PATH) if isfile(SRC_PATH + "/" + i) and i[-4:] == ".cpp"]


# for i in LIBS_PATH:
#     bindir = i + "/bin/" + TARGET + "/" + PLATFORM
#     for file in listdir(bindir):
#         if isfile(bindir + "/" + file) and file[-4:] == ".dll":
#             DLLS.append(file)


# if MODE == "Debug":
#     DEBUG_FLAGS 		= ["-g", "-ggdb", "-mwindows"]
#     INCLUDE_PATH_FLAGS 	= ["-I" + i for i in INCLUDE_PATHS]
#     LIB_PATHS_FLAGS 	= ["-L" + i for i in LIB_PATHS]
#     LIBS_FLAGS			= ["-l" + i for i in LIBS]

# if MODE == "Release":
#     DEBUG_FLAGS 		= ["-mwindows"]
#     INCLUDE_PATH_FLAGS 	= ["-I" + i for i in INCLUDE_PATHS]
#     LIB_PATHS_FLAGS 	= ["-L" + i for i in LIB_PATHS]
#     LIBS_FLAGS			= ["-l" + i for i in LIBS]

# CFLAGS = DEBUG_FLAGS + INCLUDE_PATH_FLAGS
# LFLAGS = DEBUG_FLAGS + INCLUDE_PATH_FLAGS + LIB_PATHS_FLAGS + LIBS_FLAGS

# for i in SRCS:
#     os.system("%__cd__%{compiler} {flags} -c {source} -o {out}".format(compiler=CXX.replace("/", "\\"),
#                                                            flags=" ".join(CFLAGS),
#                                                            source=SRC_PATH + "/" + i,
#                                                            out=OBJ_PATH + "/" + i[:-4] + ".o"))

# os.system("%__cd__%{compiler} {flags} {source} -o {out}".format(compiler=CXX.replace("/", "\\"),
#                                                     flags=" ".join(LFLAGS), 
#                                                     source=" ".join(OBJ_PATH + "/" + i for i in listdir(OBJ_PATH) if isfile(OBJ_PATH + "/" + i) and i[-2:] == ".o"),
#                                                     out=BIN))


# BIN_DLLS = [i for i in listdir(BIN_PATH) if isfile(BIN_PATH + "/" + i) and i[-4:] == ".dll"]

# for i in LIBS_PATH:
#     bindir = i + "/bin/" + TARGET + "/" + PLATFORM
#     for file in listdir(bindir):
#         if isfile(bindir + "/" + file) and file[-4:] == ".dll":
#             if not file in BIN_DLLS:
#                 os.system('xcopy "%__cd__%{source}" "%__cd__%{dest}" /I'.format(source=bindir.replace("/", "\\") + "\\" + file, dest=BIN_PATH.replace("/", "\\")))

# os.system("start %s"%BIN)