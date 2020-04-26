
# blender -b --python PresentationInstall.py
# ./blender -b --python /home/ubuntu/PresentationInstall.py

import os.path
import bpy
import zipfile
import sys
import shutil, errno

argv = sys.argv
try:
    index = argv.index("--") + 1
except:
    index = len(argv)

argv = argv[index:]
print(argv)
blendPath = False
if(argv[0]):
	blendPath = argv[0]

blender_VERSION = "2.79"
if(argv[1]):
	blender_VERSION = argv[1]

ver = "001"
use_resources = False
use_rail = False
use_ffmpeg = False
install_lights = False
use_uber = False
if sys.platform == "win32":
    basepath = os.getcwd() #os.path.dirname(os.path.realpath(__file__))
    blender_version_path = "C:\\Users\\mephisto\\AppData\\Roaming\\Blender Foundation\Blender\\"+blender_VERSION #os.path.join("blender-2.77a-linux-glibc211-x86_64", "2.77")
    blender_resources_path= os.path.join(basepath, "PresentationMaterials.zip")
    blender_resources_path_target= os.path.join(basepath, "blender_resources")
    ffmpeg_path = os.path.join(basepath, "ffmpeg.exe")
    ffmpeg_path_target = os.path.join(basepath,"uber","ffmpeg.exe")
    rail_resources_path = os.path.join(basepath, "RailEnvironments") # "D:\\UberRailEnvironments\\"#
    rail_resources_target_path = os.path.join(basepath, "blender_rail_resources")
    uber_path_file = os.path.join(basepath, "uber-" + ver + ".zip")
    uber_path_target = os.path.join(basepath, "uber")
else:
    basepath =  "/" + os.path.join("home","ubuntu")# os.path.expanduser("~")
    blender_version_path = os.path.join(os.path.expanduser("~"),".config","blender", blender_VERSION)
    blender_resources_path= os.path.join(basepath, "PresentationMaterials.zip")
    blender_resources_path_target= os.path.join(basepath, "blender_resources")
    rail_resources_path = os.path.join(basepath, "RailEnvironments")
    rail_resources_target_path = os.path.join(basepath, "blender_rail_resources")
    ffmpeg_path = os.path.join(basepath, "ffmpeg")
    ffmpeg_path_target = os.path.join(basepath,"uber","ffmpeg")
    uber_path_file = os.path.join(basepath, "uber-" + ver + ".zip")
    uber_path_target = os.path.join(basepath, "uber")
    
print("Install presentation addons")

# hdriZip = "D:\\Uber\\hdris.zip"
hdriZip = os.path.join(basepath, "hdris.zip")

# pro_lighting_library = "D:\\Uber\\library.zip"
pro_lighting_library = os.path.join(basepath, "library.zip")

# location = "D:\\dev\\Python\\Blender\\Presentation\\PresenationBlender.py"
# location = os.path.join(basepath, "PresenationBlender.py")
location = os.path.join(basepath, "Fleet.zip")

# pro_skies_location = "D:\\Blender\\Addons\\pro_lighting_skies_ultimate_v1.2.zip"
pro_skies_location = os.path.join(basepath, "pro_lighting_skies_ultimate_v1.2.zip")

# pro_lighting_studio_location = "D:\\Blender\\Addons\\pro_lighting_studio.zip"
pro_lighting_studio_location = os.path.join(basepath, "pro_lighting_studio.zip")

# pro_skies_hdri_location = "C:\\Users\\mephisto\\AppData\\Roaming\\Blender Foundation\\Blender\\2.76\\scripts\\addons\\pro_lighting_skies_ultimate"
pro_skies_hdri_location = os.path.join(blender_version_path, "scripts", "addons", "pro_lighting_skies_ultimate")

# pro_lighting_studio_location_libs = "C:\\Users\\mephisto\\AppData\\Roaming\\Blender Foundation\\Blender\\2.76\\scripts\\addons\\pro_lighting_studio"
pro_lighting_studio_location_libs = os.path.join(blender_version_path, "scripts", "addons", "pro_lighting_studio")

# bpy.ops.wm.addon_install(overwrite=True, target='DEFAULT', filepath="", filter_folder=True, filter_python=True, filter_glob="*.py;*.zip")
bpy.ops.wm.addon_install(overwrite=True, target='DEFAULT', filepath=location, filter_folder=True, filter_python=True, filter_glob="*.py;*.zip")

if install_lights:
    bpy.ops.wm.addon_install(overwrite=True, target='DEFAULT', filepath=pro_skies_location, filter_folder=True, filter_python=True, filter_glob="*.py;*.zip")
    bpy.ops.wm.addon_install(overwrite=True, target='DEFAULT', filepath=pro_lighting_studio_location, filter_folder=True, filter_python=True, filter_glob="*.py;*.zip")

def unzipToLocation(file, to):
    fh = open(file, 'rb')
    z = zipfile.ZipFile(fh)
    for name in z.namelist():
        outpath = to
        z.extract(name, outpath)
    fh.close()


def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

if use_uber:
    unzipToLocation(uber_path_file, uber_path_target)
if use_resources:
    unzipToLocation(blender_resources_path, blender_resources_path_target)
if use_rail:
    copyanything(rail_resources_path, rail_resources_target_path)
if use_ffmpeg:
    copyanything(ffmpeg_path, ffmpeg_path_target)

if install_lights:
    unzipToLocation(hdriZip, pro_skies_hdri_location)
    unzipToLocation(pro_lighting_library, pro_lighting_studio_location_libs)
# fh = open(hdriZip, 'rb')
# z = zipfile.ZipFile(fh)
# for name in z.namelist():
#     outpath = pro_skies_hdri_location
#     z.extract(name, outpath)
# fh.close()

# fh = open(pro_lighting_library, 'rb')
# z = zipfile.ZipFile(fh)
# for name in z.namelist():
#     outpath = pro_lighting_studio_location_libs
#     z.extract(name, outpath)
# fh.close()

print("enabling FleetMaker")
bpy.ops.wm.addon_enable(module="FleetMaker")   
print("enabling pro_lighting_skies_ultimate")
#bpy.ops.wm.addon_enable(module="pro_lighting_skies_ultimate")     
print("enabling pro_lighting_studio")
#bpy.ops.wm.addon_enable(module="pro_lighting_studio")
print("enabling io_import_images_as_planes")
bpy.ops.wm.addon_enable(module="io_import_images_as_planes")
    

print("save user settings")
bpy.ops.wm.save_userpref()