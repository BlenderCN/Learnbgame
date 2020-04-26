
# blender -b --python InstallPresentation.py

import os.path
import bpy
import zipfile
import sys
import shutil, errno

def writeZip(files, to):
    with zipfile.ZipFile(to, 'x') as myzip:
        for file in files:
            myzip.write(file)
blender_VERSION = "2.79"
ver = "001"
install_lights = True
if sys.platform == "win32":
    basepath = os.getcwd() #os.path.dirname(os.path.realpath(__file__))
    blender_version_path = "C:\\Users\\mephisto\\AppData\\Roaming\\Blender Foundation\Blender\\" + blender_VERSION #os.path.join("blender-2.77a-linux-glibc211-x86_64", "2.77")
else:
    basepath =  "/" + os.path.join("home","ubuntu")# os.path.expanduser("~")
    blender_version_path = os.path.join(os.path.expanduser("~"),".config","blender", blender_VERSION)
    
print("Install presentation addons")
# location = "D:\\dev\\Python\\Blender\\Presentation\\PresenationBlender.py"
# location = os.path.join(basepath, "PresenationBlender.py")
location = os.path.join(basepath, "PresentationBlender.zip")


if os.path.isfile(location):
    os.remove(location)

writeZip(["PresentationBlender.py", "CompositeRecipes.py", "CompositeWriter.py", "BlenderToJson.py", "Constants.py", "Util.py", "config.json"], location)

# bpy.ops.wm.addon_install(overwrite=True, target='DEFAULT', filepath="", filter_folder=True, filter_python=True, filter_glob="*.py;*.zip")
bpy.ops.wm.addon_install(overwrite=True, target='DEFAULT', filepath=location, filter_folder=True, filter_python=True, filter_glob="*.py;*.zip")


def unzipToLocation(file, to):
    fh = open(file, 'rb')
    z = zipfile.ZipFile(fh)
    for name in z.namelist():
        outpath = to
        z.extract(name, outpath)
    fh.close()



print("enabling PresentationBlender")
bpy.ops.wm.addon_enable(module="PresentationBlender")   
bpy.ops.wm.addon_enable(module="CompositeRecipes")   
    

print("save user settings")
bpy.ops.wm.save_userpref()