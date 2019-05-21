bl_info = {
    "name":        "Nibus Vis Tools",
    "description": "Tools for real time visuals and animation",
    "author":      "Tessera Skye",
    "version":     (0, 0, 2),
    "blender":     (2, 80, 0),
    "location":    "Various",
    "category": "Learnbgame",
    "warning":     "In development!"
}

#validation

import os
import sys
import import_libs

library_tools.regPath()

if addonName != "nimbus_vis":
    message = ("\n"
        "The folder containing this addon must be named 'nimbus_vis'\n")
    if __name__ != "__main__":
        raise Exception(message)

import auto_load


if "auto_load" not in globals():
    message = ("\n"
        "Nimbus has not registered properly / yet.\n")
    raise Exception(message + " " + globals())

# registration

def register():
    auto_load.register()
    print("Nimbus Registered!")

def unregister():
    auto_load.unregister()
    print("Nimbus Unregistered.")





#enables standalone support    
if __name__ == "__main__":
    register()
