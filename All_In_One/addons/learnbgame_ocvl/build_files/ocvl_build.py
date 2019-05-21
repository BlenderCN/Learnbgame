#!/usr/bin/env python3
"""
Script to full build and release OpenCV Laboratory on base updated Blender

Structure of directories

* - blender-build
* -- ocvl-addon
* -- blender
* -- lib
* -- build_darwin
* -- build_darwin_lite

"""
import functools
import json
import os
import re
from pprint import pprint

import shutil
import sys
import platform
import subprocess
import os.path

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

from build_files.build_utils.linux import make_tar_gz_from_release
from build_files.build_utils.common import cmd, get_blender_build_path, recursive_overwrite
from build_files.build_utils.windows import nsis_installer_build


def update_build_number():
    build_version_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "BUILD_NUMBER")
    with open(build_version_file, "r") as fp:
        build_number = int(fp.readline().replace("\n", "")) + 1
    with open(build_version_file, "w") as fp:
        fp.write(str(build_number) + "\n")
    return build_number


BUILD_NUMBER = update_build_number()


# -----  Settings
DEBUG = bool(os.environ.get("DEBUG")) or True
PLATFORM = platform.system()
OCVL_VERSION = f"1.2.0.{BUILD_NUMBER}"
BLENDER_BUILD_DIR_NAME = "blender-build"
WORK_DIR = os.path.normpath(get_blender_build_path(BLENDER_BUILD_DIR_NAME, os.path.dirname(os.path.realpath(__file__))))
OCVL_ADDON_DIR_NAME = "ocvl-addon"
BLENDER_SOURCE_DIR_NAME = "blender"
GET_PIP_FILE_NAME = "get-pip.py"
GET_PIP_URL = f"https://bootstrap.pypa.io/{GET_PIP_FILE_NAME}"
OCVL_REQUIREMENTS_PATH = os.path.join(WORK_DIR, OCVL_ADDON_DIR_NAME, "requirements.txt")
OCVL_PATCHES_PATH = os.path.join(WORK_DIR, OCVL_ADDON_DIR_NAME, "build_files", "patches")
MAKE_COMMAND_MAP = {"Windows": "make.bat", "Linux": "make", "Darwin": "make"}
MAKE_COMMAND = MAKE_COMMAND_MAP[PLATFORM]

BUILD_VERSION = 'lite'
BUILD_RELEASE_DIRNAME_TEMPLATE_MAP = {
    "Windows": "build_windows_{}_x64_vc15_Release".format(BUILD_VERSION.capitalize()),
    "Linux": f"build_linux_{BUILD_VERSION}",
    "Darwin": f"build_darwin_{BUILD_VERSION}"}
BUILD_RELEASE_DIRNAME = BUILD_RELEASE_DIRNAME_TEMPLATE_MAP[PLATFORM]

BIN_RELEASE_MAP = {
    "Windows": os.path.join("bin", "Release"),
    "Linux": "bin",
    "Darwin": os.path.join("bin", "OpenCVLaboratory.app", "Contents", "Resources"),
}
BIN_RELEASE = BIN_RELEASE_MAP[PLATFORM]
PYTHON_PACKAGES = "site-packages" if PLATFORM is 'Windows' else os.path.join("python3.7", "dist-packages")
BLENDER_PYTHON_BIN_MAP = {
    "Windows": os.path.join(WORK_DIR, BUILD_RELEASE_DIRNAME, BIN_RELEASE, "2.80", "python", "bin", "python"),
    "Linux": os.path.join(WORK_DIR, BUILD_RELEASE_DIRNAME, BIN_RELEASE, "2.80", "python", "bin", "python3.7m"),
    "Darwin": os.path.join(WORK_DIR, BUILD_RELEASE_DIRNAME, BIN_RELEASE, "2.80", "python", "bin", "python3.7m")
}
BLENDER_PYTHON_BIN = BLENDER_PYTHON_BIN_MAP[PLATFORM]

BLENDER_PIP_BIN_MAP = {
    "Windows": os.path.join(WORK_DIR, BUILD_RELEASE_DIRNAME, BIN_RELEASE, "2.80", "python", "Scripts", "pip"),
    "Linux": os.path.join(WORK_DIR, BUILD_RELEASE_DIRNAME, BIN_RELEASE, "2.80", "python", "local", "bin", "pip"),
    "Darwin": os.path.join(WORK_DIR, BUILD_RELEASE_DIRNAME, BIN_RELEASE, "2.80", "python", "bin", "pip"),
}
BLENDER_PIP_BIN = BLENDER_PIP_BIN_MAP[PLATFORM]
PREPARE_ARTIFACT_FN_MAP = {
    "Windows": functools.partial(
        nsis_installer_build,
        version_display=OCVL_VERSION,
        build_blender_path=WORK_DIR,
        bf_build_dir=BUILD_RELEASE_DIRNAME,
        rel_dir=os.path.join(WORK_DIR, OCVL_ADDON_DIR_NAME, "build_files", "release", "windows")
    ),
    "Linux": make_tar_gz_from_release,
    "Darwin": lambda *args, **kwargs: print(args),
    #create-dmg OpenCVLaboratory.app
}

PREPARE_ARTIFACT_FN = PREPARE_ARTIFACT_FN_MAP[PLATFORM]

def update_blender(branch='master'):
    """
    Update Blender
    :return:
    """
    os.chdir(os.path.join(WORK_DIR, BLENDER_SOURCE_DIR_NAME))
    cmd(f"git reset --hard")
    cmd(f"git checkout {branch}")
    cmd(f"git pull", accepted_status_code=[0, 1])
    os.chdir(WORK_DIR)


def update_blender_submodule(branch='master'):
    """
    Update Blender submodules
    :param branch:
    :return:
    """
    os.chdir(os.path.join(WORK_DIR, BLENDER_SOURCE_DIR_NAME))
    cmd(f"git submodule foreach git checkout {branch}")
    cmd(f"git submodule foreach git pull --rebase origin {branch}")
    os.chdir(WORK_DIR)


def update_ocvl_addon(branch='master'):
    """
    Update OCVL ADDON
    :return:
    """
    if DEBUG:
        return
    os.chdir(os.path.join(WORK_DIR, OCVL_ADDON_DIR_NAME))
    cmd(f"git resert --hard")
    cmd(f"git checkout {branch}")
    cmd(f"git pull")
    os.chdir(WORK_DIR)


def build_blender(build_version=BUILD_VERSION):
    os.chdir(os.path.join(WORK_DIR, BLENDER_SOURCE_DIR_NAME))
    cmd(f"{MAKE_COMMAND} {build_version}")
    os.chdir(WORK_DIR)


def get_get_pip_script():
    """
    Get get-pip file from remote server
    :return:
    """
    os.chdir(WORK_DIR)
    get_pip_filepath = os.path.join(WORK_DIR, GET_PIP_FILE_NAME)
    if not os.path.isfile(f"{get_pip_filepath}"):
        cmd(f"curl {GET_PIP_URL} -o {GET_PIP_FILE_NAME}")

    cmd(f"{BLENDER_PYTHON_BIN} {get_pip_filepath}")
    os.chdir(WORK_DIR)


def install_ocvl_requirements():
    """
    Install requirements.txt in Blender Python
    :return:
    """
    def remove_old_numpy():
        cmd(f"{BLENDER_PIP_BIN} uninstall -y numpy")
        destination_path = os.path.join(WORK_DIR, BUILD_RELEASE_DIRNAME, BIN_RELEASE, "2.80", "python", "lib",
                                        PYTHON_PACKAGES, "numpy")
        if os.path.exists(destination_path):
            print(f"Remove old version Numpy from: {destination_path}")
            shutil.rmtree(destination_path)
    if PLATFORM != "Darwin":
        remove_old_numpy()
    cmd(f"{BLENDER_PIP_BIN} install -r {OCVL_REQUIREMENTS_PATH}")
    os.chdir(WORK_DIR)


def copy_ocvl_to_addons():
    """
    Copy(and overwrite) OCVL addon to Blender scripts directory
    :return:
    """
    print("Copy OCVL addon to Blender...")
    source_path = os.path.join(WORK_DIR, OCVL_ADDON_DIR_NAME)
    destination_path = os.path.join(WORK_DIR, BUILD_RELEASE_DIRNAME, BIN_RELEASE, "2.80", "scripts", "addons", "ocvl-addon")
    print(f"Copy OCVL addon to Blender. From: {source_path} to {destination_path}...")
    if os.path.exists(destination_path):
        print("Remove old version OCVL addon")
        shutil.rmtree(destination_path)
    shutil.copytree(source_path, destination_path)
    os.chdir(WORK_DIR)
    print("Success!")


def make_patches():
    """
    Override some original blender files for OCVL
    :return:
    """
    FILES_TO_CLEAN = [
        "tests/python/CMakeLists.txt"
    ]

    def clean_up_tests():
        for file in FILES_TO_CLEAN:
            with open(file, 'w') as fp:
                pass


    def check_hash(patch):
        with open(patch, 'r') as fp:
            match = re.match(r"diff --git a/(.*) b/", str(fp.readline()))
        path = match.groups()[0]
        out, _ = cmd(f"git ls-files -s {path}", stdout=subprocess.PIPE)
        new_hash = str(out).split(" ")[1]
        match = re.match(r".*build_files/patches/(.*)-.*", str(patch))
        old_hash = match.groups()[0]
        if old_hash != new_hash:
            print(f"WARNING: Update files patches - {patch}")

    os.chdir(os.path.join(WORK_DIR, BLENDER_SOURCE_DIR_NAME))
    patch_names = os.listdir(OCVL_PATCHES_PATH)
    for patch_name in patch_names:
        patch = os.path.join(OCVL_PATCHES_PATH, patch_name)
        try:
            check_hash(patch)
        except Exception as e:
            print(f"WARNING: Can not check hashes - {e}")
        cmd(f"git apply {patch}")

    clean_up_tests()
    os.chdir(WORK_DIR)


def print_bin():
    """
    Create link to quick lunch Blender
    :return:
    """
    if PLATFORM == "Darwin":
        destination_path = os.path.join(WORK_DIR, BUILD_RELEASE_DIRNAME, "bin", "OpenCVLaboratory.app", "Contents", "MacOS", "OpenCVLaboratory")
    elif PLATFORM == "Linux":
        destination_path = os.path.join(WORK_DIR, BUILD_RELEASE_DIRNAME, "bin", "OpenCVLaboratory")
    elif PLATFORM == "Windows":
        destination_path = os.path.join(WORK_DIR, BUILD_RELEASE_DIRNAME, "bin", "Release", "OpenCVLaboratory.exe")
    print(destination_path)


def override_blender_release():
    src = os.path.join(WORK_DIR, OCVL_ADDON_DIR_NAME, "build_files", "release")
    dst = os.path.join(WORK_DIR, "blender", "release")
    recursive_overwrite(src, dst)


def delete_dirs():
    src = os.path.join(WORK_DIR, "blender", "release", "scripts", "startup", "bl_app_templates_system")
    for app in os.listdir(src):
        del_dir = os.path.join(src, app)
        print(f"Deleting directory: {del_dir}")
        shutil.rmtree(del_dir)
    os.chdir(WORK_DIR)


def get_release_details(version=None):
    if not version:
        raise ValueError("Version is required")
    release_version_path = os.path.join(WORK_DIR, OCVL_ADDON_DIR_NAME, "build_files", "RELEASE_NUMBER.json")
    with open(release_version_path, 'r') as fh:
        versions_dict = json.load(fh)

    version_details = versions_dict.get(version)
    if not version_details:
        raise IndexError(f"Version {version} not exists")

    print(f"-----Version: {version}-----")
    pprint(version_details)
    return version_details


def check_permission_protected_dir():
    permission_protected_path = os.path.join(WORK_DIR, BUILD_RELEASE_DIRNAME, "bin", "Release", "2.80", "scripts", "addons", "ocvl-addon")
    if os.path.isdir(permission_protected_path):
        raise PermissionError(f"""
        Protected path: {permission_protected_path} exists, delete it before build.\nTIP: runas /user:Administrator "powershell -c rmdir /s {permission_protected_path}"""
                              )


if __name__ == "__main__":

    version = "1.2.0"

    try:
        version_details = get_release_details(version)
        check_permission_protected_dir()
        update_blender(version_details["git_state_blender"])
        update_blender_submodule()
        # update_ocvl_addon()
        make_patches()
        delete_dirs()
        override_blender_release()
        build_blender()
        get_get_pip_script()
        install_ocvl_requirements()
        copy_ocvl_to_addons()
        PREPARE_ARTIFACT_FN(kwargs=locals())
        print_bin()

        pass
    finally:
        os.chdir(WORK_DIR)



