import bpy
import sys
import os

print("BLENDER VERSION : " + bpy.app.version_string)
ADDON_PATH = (bpy.utils.user_resource('SCRIPTS', "addons"))

os.system("cp -r ../vispCAOImport " + ADDON_PATH)
print("Moved addon to " + ADDON_PATH)
# bpy.utils.script_paths()
