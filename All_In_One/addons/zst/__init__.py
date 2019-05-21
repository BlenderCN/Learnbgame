# Setting for Working Copy Add-On Prooerties
# Setting for Add-On Prooerties
bl_info = {
    "name": "Zs Toos Add-On",
    "discription": "you can use all ZsTools only this addon",
    "author": "Zenryoku Service",
    "version": (0.1),
    "blender":(2, 78, 0),
    "location": "Tools>ZsTools",
    "warning":"", # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/ZenryokuService/BlenderPython/"
        "AddOnPython",
    "tracker_url": "https://wiki.blender.org/index.php/Dev:Py/Scripts/Guidelines/Addons/metainfo",
    "support": "COMMUNITY",
    "category":"Object"
}

import bpy, os, sys, importlib
print("ZsTools loading ...")

# append path to ZsTools Add-on
def appendZstPath():
    zstDir = os.path.dirname(os.path.abspath(__file__))
    zsDirList = os.listdir(zstDir)
    print("zstDir: %s" % zstDir)
    sys.path.append(zsDir)
    for dir1 in zsDirList:
        if os.path.isdir(zstDir + '/' + dir1) == True \
                and (dir1 != "__pycache__" and dir1 != ".DS_Store"):
            importPath = zstDir + '/' + dir1
            print("importPath: %s" % importPath)
            print("dir1 : %s" % dir1)
            pacs = "import zst." + dir1
            print(pacs + ".WorkingCopyTool")
            exec(pacs)
        ## end if
    ## end for
# end appendZstPath

# 1. load all py file at this directory
# -> py file define some classes inherit operator class or panel class and the other
#
# 2. registor and unregistor loaded classes
def register():
    print("*** Start Registor ***")
    appendZstPath()
    print("*** End Registor ***")

def unregister():
    print("*** Start UnRegistor ***")
    sys.path.remove(os.path.dirname(os.path.abspath(__file__)))
    print("*** End UnRegistor ***")

# find directory
#def findDir(path):
