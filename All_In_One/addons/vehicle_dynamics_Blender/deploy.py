#!/usr/bin/env python3

import importlib
import os
import shutil
import zipfile


def zipdir(path, ziph):
    """ Utility routine to zip directory recursively
    :param path: string path of directory to compress
    :param ziph : zipfile handle
    """

    # 'walk' inside directory tree listing directories and files into them
    for root, dirs, files in os.walk(path):
        # for each file in current walked dir
        for file in files:
            # add file to zip
            ziph.write(os.path.join(root, file))


if __name__ == "__main__":
    # get project root
    my_path = os.path.abspath(os.path.dirname(__file__))
    # path of a temp directory to zip
    path = os.path.join(my_path, "blender_inertial")
    # prepare other path strings
    addon_updater_path = os.path.join(my_path, "blender-addon-updater", "addon_updater.py")
    src_full_path = os.path.join(my_path, "src")
    blender_utils_full_path = os.path.join(my_path,"blender")
    init_full_path = os.path.join(my_path, "__init__.py")
    requirements_full_path = os.path.join(my_path, "production_requirements.py")
    car_full_path = os.path.join(my_path, "camaro_for_link.blend")
    addon_updater_ops_path = os.path.join(my_path, "my_addon_updater_ops.py")
    new_src = os.path.join(path, "src")
    new_blender_utils = os.path.join(path,"blender")
    addon_updater_ops_new_path = os.path.join(path, "addon_updater_ops.py")
    # TODO if dir exist remove it
    os.makedirs(path, exist_ok=True)
    # copy necessary project file to temp directory
    shutil.copytree(src_full_path, new_src)
    shutil.copytree(blender_utils_full_path,new_blender_utils)
    shutil.copy(init_full_path, path)
    shutil.copy(addon_updater_ops_path, addon_updater_ops_new_path)
    shutil.copy(addon_updater_path, path)
    shutil.copy(requirements_full_path, path)
    shutil.copy(car_full_path,path)
    # final path of zip file
    zip_path = os.path.join(my_path, "blender_inertial.zip")
    # crete zip file object
    # check what zip algorithms modules are installed
    # priority to algorithms that create smaller zip (time doesn't matter)
    if importlib.util.find_spec("lzma"):
        # use lzma
        addon_zip = zipfile.ZipFile(zip_path, mode='w', compression=zipfile.ZIP_LZMA)
    elif importlib.util.find_spec("bz2"):
        # use bz2
        addon_zip = zipfile.ZipFile(zip_path, mode='w', compression=zipfile.ZIP_BZIP2)
    elif importlib.util.find_spec("zlib"):
        # use zlib
        addon_zip = zipfile.ZipFile(zip_path, mode='w', compression=zipfile.ZIP_DEFLATED)
    else:
        # no compression, default option
        addon_zip = zipfile.ZipFile(zip_path, mode='w')
    # zip directory
    zipdir("blender_inertial", addon_zip)
    # close zip file handle
    addon_zip.close()
    # remove temporary directory
    shutil.rmtree(path)
