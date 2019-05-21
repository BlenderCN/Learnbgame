# Setting for Add-On Prooerties
bl_info = {
    "name": "ZsTools Add-On",
    "discription": "push Start -> create working copy script file",
    "author": "Zenryoku Service",
    "version": (0,1),
    "blender":(2, 79, 0),
    "location": "Tools>ZsTools",
    "warning":"", # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/ZenryokuService/BlenderPython/"
        "AddOnPython",
    "tracker_url": "https://wiki.blender.org/index.php/Dev:Py/Scripts/Guidelines/Addons/metainfo",
    "support": "COMMUNITY",
    "category":"Object"
}

import bpy, sys, os, glob, importlib
from . import RootOperator, RootPanel

############################################
# Public Methods
############################################

# 1. load all py file at this directory
# -> py file define some classes inherit operator class or panel class and the other
#
# 2. registor loaded classes
def register():
    print("*** init Register ***")
    modList = getZstPackageNameList(addZstToPythonPath(True))
    print("==> modList %s" % modList)
    for modName in modList:
        impModule(modName)
#        print("*** call rester_module ***")
#        bpy.utils.register_module(modName)


# unload registered modules
def unregister():
    print("*** init Unregister ***")
    addZstToPythonPath(False)

############################################
# Private Methods
############################################

# Add CurrentDir to pythonPath
def addZstToPythonPath(appendFlg):
    currentDir = os.path.dirname(os.path.abspath(__file__))
    print("==> CurrentDir is: %s" % currentDir)
    if appendFlg == True:
        print("Add Path")
        sys.path.append(currentDir)
    else:
        print("Remove Path")
        sys.path.remove(currentDir)
    return currentDir

# Get ZstTools dir
def getZstPackageNameList(currentDir):
    list = []
    print("==> CurrentDir is: %s" % currentDir + "/*.py")
    # get py fileNames
    fileNames = glob.glob(currentDir + "/*.py")
    for name in fileNames:
        pyFile = os.path.splitext(os.path.basename(name))
        print("*** %s *** " % pyFile[0])
        if pyFile[0] == "__init__":
            print("next!!")
            continue
        list.append(pyFile[0])

    return list

###########################################
# import module from string(className)
###########################################
def impModule(modName):
    print("*** import %s ***" % modName)
    importlib.import_module(modName)
    obj = globals()[modName]
    importlib.reload(obj)
#    bpy.utils.register_module(obj)

###########################################
# use for print __name__
###########################################
def printName():
    print(locals())
    print("---------- __name__ -----------------")
    print(__name__)
#    print("---------- ____ -----------------")
