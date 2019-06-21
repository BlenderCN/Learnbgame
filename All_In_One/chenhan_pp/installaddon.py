import os, sys;
import subprocess;
import zipfile;
from platform import platform

print(sys.argv);

BLENDER_ADDON_PREFIX = os.path.abspath(sys.argv[3].strip());
BLENDER_VERSION = sys.argv[4].strip();
BLENDER_ADDON_LOCATION = "%s/%s/scripts/addons/"%(BLENDER_ADDON_PREFIX,BLENDER_VERSION);
BLENDER_ADDON_LOCATION = os.path.abspath(BLENDER_ADDON_LOCATION);
PROJECT_FOLDER = os.path.abspath(sys.argv[1].strip());
PROJECT_NAME = sys.argv[2].strip();

print("Prefix: %s\nVERSION: %s\nADDON_LOCATION_FULL: %s\n"%(BLENDER_ADDON_PREFIX, BLENDER_VERSION, BLENDER_ADDON_LOCATION));

def zipdir(path, zipper):
    for root, dirs, files in os.walk(path):
        for file in files:
            if("." not in file[0] and not file.endswith('.zip') and "installaddon.py" not in file):
                file_path = os.path.abspath(os.path.join(root, file));
                parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir));
                rel_path = os.path.relpath(file_path, parent_dir);
                zipper.write(file_path, rel_path);
    
    return zipper;
    
if __name__ == "__main__":
    zipper = zipfile.ZipFile(PROJECT_NAME+".zip", 'w', zipfile.ZIP_DEFLATED);
    zipper = zipdir(PROJECT_FOLDER, zipper);
    zipper.close();
    zip_file_path = os.path.abspath(PROJECT_FOLDER+"/"+PROJECT_NAME+".zip");
    zipper = zipfile.ZipFile(zip_file_path, "r");
    
    zipper.extractall(BLENDER_ADDON_LOCATION);
    zipper.close();
    
#     out = subprocess.check_call(['blender.exe']);