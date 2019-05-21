# Setting for Working Copy Add-On Prooerties
# Setting for Add-On Prooerties
bl_info = {
    "name": "Working Copy Add-On",
    "discription": "push Start -> create working copy script file",
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

import bpy, os

# 1. load all py file at this directory
# -> py file define some classes inherit operator class or panel class and the other
#
# 2. registor and unregistor loaded classes
def register():
    print("*** Start Registor ***")
    print(os.path.dirname(os.path.abspath(__file__)))
    print("*** Start Registor ***")

def unregister():
    print("*** Start UnRegistor ***")
    print("*** End UnRegistor ***")
