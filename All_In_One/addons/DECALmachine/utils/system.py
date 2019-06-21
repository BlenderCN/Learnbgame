import bpy
import os
import sys
import json
import platform
import site
import subprocess
import shutil
import re


def abspath(path):
    return os.path.abspath(bpy.path.abspath(path))


def relpath(path):
    return bpy.path.relpath(path)


def splitpath(path):
    path = os.path.normpath(path)
    return path.split(os.sep)


def quotepath(path):
    if " " in path:
        path = '"%s"' % (path)
    return path


def makedir(pathstring):
    if not os.path.exists(pathstring):
        os.makedirs(pathstring)
    return pathstring


def load_json(pathstring):
    with open(pathstring, 'r') as f:
        jsondict = json.load(f)
    return jsondict


def save_json(jsondict, pathstring):
    try:
        with open(pathstring, 'w') as f:
            json.dump(jsondict, f, indent=4)
    except PermissionError:
        import traceback
        print()
        traceback.print_exc()

        print(80 * "-")
        print()
        print(" ! FOLLOW THE INSTALLATION INSTRUCTIONS ! ")
        print()
        print("You are not supposed to put DECALmachine into C:\Program Files\Blender Foundation\... etc.")
        print()
        print("https://machin3.io/DECALmachine/docs/installation/")
        print()
        print(80 * "-")


def open_folder(path):
    import platform
    import subprocess

    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        # subprocess.Popen(["xdg-open", pathstring])
        os.system('xdg-open "%s" %s &' % (path, "> /dev/null 2> /dev/null"))  # > sends stdout,  2> sends stderr


def get_new_directory_index(path):
    dirs = [f for f in sorted(os.listdir(path)) if os.path.isdir(os.path.join(path, f))]

    index = "001"

    while dirs:
        last = dirs.pop(-1)
        try:
            index = str(int(last[:3]) + 1).zfill(3)
            break
        except:
            pass

    return index


# PIP, EASY_INSTALL, PIL

def get_python_paths(log):
    pythonbinpath = bpy.app.binary_path_python

    if platform.system() == "Windows":
        pythonlibpath = os.path.join(os.path.dirname(os.path.dirname(pythonbinpath)), "lib")

    else:
        pythonlibpath = os.path.join(os.path.dirname(os.path.dirname(pythonbinpath)), "lib", os.path.basename(pythonbinpath)[:-1])

    ensurepippath = os.path.join(pythonlibpath, "ensurepip")
    sitepackagespath = os.path.join(pythonlibpath, "site-packages")
    usersitepackagespath = site.getusersitepackages()

    easyinstallpath = os.path.join(sitepackagespath, "easy_install.py")
    easyinstalluserpath = os.path.join(usersitepackagespath, "easy_install.py")

    modulespaths = [os.path.join(path, 'modules') for path in bpy.utils.script_paths() if path.endswith('scripts')]

    print("Python Binary: %s %s" % (pythonbinpath, os.path.exists(pythonbinpath)))
    print("Python Library: %s %s" % (pythonlibpath, os.path.exists(pythonlibpath)))
    print("Ensurepip: %s %s\n" % (ensurepippath, os.path.exists(ensurepippath)))

    for path in modulespaths:
        print("Modules: %s %s" % (path, os.path.exists(path)))

    print("Site-Packages: %s %s" % (sitepackagespath, os.path.exists(sitepackagespath)))
    print("User Site-Packages: %s %s" % (usersitepackagespath, os.path.exists(usersitepackagespath)))
    print("EasyInstall Path: %s %s" % (easyinstallpath, os.path.exists(easyinstallpath)))
    print("EasyInstall User Path: %s %s\n" % (easyinstalluserpath, os.path.exists(easyinstalluserpath)))

    log.append("Python Binary: %s %s" % (pythonbinpath, os.path.exists(pythonbinpath)))
    log.append("Python Library: %s %s" % (pythonlibpath, os.path.exists(pythonlibpath)))
    log.append("Ensurepip: %s %s\n" % (ensurepippath, os.path.exists(ensurepippath)))

    for path in modulespaths:
        log.append("Modules: %s %s" % (path, os.path.exists(path)))

    log.append("Site-Packages: %s %s" % (sitepackagespath, os.path.exists(sitepackagespath)))
    log.append("User Site-Packages: %s %s" % (usersitepackagespath, os.path.exists(usersitepackagespath)))
    log.append("EasyInstall Path: %s %s" % (easyinstallpath, os.path.exists(easyinstallpath)))
    log.append("EasyInstall User Path: %s %s\n" % (easyinstalluserpath, os.path.exists(easyinstalluserpath)))

    return pythonbinpath, pythonlibpath, ensurepippath, modulespaths, sitepackagespath, usersitepackagespath, easyinstallpath, easyinstalluserpath


def remove_PIL(sitepackagespath, usersitepackagespath, modulespaths, log):
    for sitepath in [sitepackagespath, usersitepackagespath] + modulespaths:
        if os.path.exists(sitepath):
            folders = [(f, os.path.join(sitepath, f)) for f in os.listdir(sitepath)]

            for folder, path in folders:
                msg = "Existing PIL/Pillow found, removing: %s" % (path)

                if (folder.startswith("Pillow") and folder.endswith("egg")) or folder.startswith("Pillow") or folder == "PIL":
                    print(msg)
                    log.append(msg)

                    # on windows, you can't remove it completely, while it is imported. so ignore errors, to avoid an exception.
                    shutil.rmtree(path, ignore_errors=True)


def install_pip(pythonbinpath, ensurepippath, log, mode='USER'):
    if mode == 'USER':
        cmd = [pythonbinpath, ensurepippath, "--upgrade", "--user"]

    elif mode == 'ADMIN':
        cmd = [pythonbinpath, ensurepippath, "--upgrade"]

    pip = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    pipout = [out.strip() for out in pip.stdout.decode('utf-8').split("\n") if out]
    piperr = [err.strip() for err in pip.stderr.decode('utf-8').split("\n") if err]

    log += pipout
    log += piperr

    if pip.returncode == 0:
        for out in pipout + piperr:
            print(" »", out)

        print("Sucessfully installed pip!\n")
        return True

    else:
        for out in pipout + piperr:
            print(" »", out)

        print("Failed to install pip!\n")
        return False, pipout + piperr


def update_pip(pythonbinpath, log, mode='USER'):
    if mode == 'USER':
        cmd = [pythonbinpath, "-m", "pip", "install", "--upgrade", "--user", "pip"]

    elif mode == 'ADMIN':
        cmd = [pythonbinpath, "-m", "pip", "install", "--upgrade", "pip"]

    update = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    updateout = [out.strip() for out in update.stdout.decode('utf-8').split("\n") if out]
    updateerr = [err.strip() for err in update.stderr.decode('utf-8').split("\n") if err]

    log += updateout
    log += updateerr

    if update.returncode == 0:
        for out in updateout + updateerr:
            print(" »", out)

        print("Sucessfully updated pip!\n")
        return True
    else:
        for out in updateout + updateerr:
            print(" »", out)

        print("Failed to update pip!\n")
        return False


def install_PIL(pythonbinpath, log, version=None, mode='USER'):
    if mode == 'USER':
        if version:
            cmd = [pythonbinpath, "-m", "pip", "install", "--upgrade", "--user", "Pillow==%s" % (version)]
        else:
            cmd = [pythonbinpath, "-m", "pip", "install", "--upgrade", "--user", "Pillow"]

    else:
        if version:
            cmd = [pythonbinpath, "-m", "pip", "install", "--upgrade", "Pillow==%s" % (version)]
        else:
            cmd = [pythonbinpath, "-m", "pip", "install", "--upgrade", "Pillow"]

    pil = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    pilout = [out.strip() for out in pil.stdout.decode('utf-8').split("\n") if out]
    pilerr = [err.strip() for err in pil.stderr.decode('utf-8').split("\n") if err]

    log += pilout
    log += pilerr

    if pil.returncode == 0:
        for out in pilout + pilerr:
            print(" »", out)

        print("Sucessfully installed PIL!\n")
        return True
    else:
        for out in pilout + pilerr:
            print(" »", out)

        print("Failed to install PIL!\n")
        return False


def easy_install_PIL(pythonbinpath, easyinstallpath, easyinstalluserpath, log, version=None, mode='USER'):
    """
    https://setuptools.readthedocs.io/en/latest/easy_install.html
    """

    easypath = easyinstallpath if os.path.exists(easyinstallpath) else easyinstalluserpath if os.path.exists(easyinstalluserpath) else None

    if easypath:
        if mode == 'USER':
            if version:
                cmd = [pythonbinpath, easypath, "--user", "Pillow==%s" % (version)]
            else:
                cmd = [pythonbinpath, easypath, "--user", "Pillow"]

        elif mode == 'ADMIN':
            if version:
                cmd = [pythonbinpath, easypath, "Pillow==%s" % (version)]
            else:
                cmd = [pythonbinpath, easypath, "Pillow"]

        pil = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        pilout = [out.strip() for out in pil.stdout.decode('utf-8').split("\n") if out]
        pilerr = [err.strip() for err in pil.stderr.decode('utf-8').split("\n") if err]

        log += pilout
        log += pilerr

        if pil.returncode == 0:
            print("Sucessfully installed PIL!\n")

            for out in pilout + pilerr:
                print(" »", out)

            return True
        else:
            print("Failed to install pip!\n")

            for out in pilout + pilerr:
                print(" »", out)

            return False
    else:
        print("Easy install could not be found!\n")

        return False


def update_sys_path(usersitepackagespath, log):
    if usersitepackagespath in sys.path:
        print("\nFound %s in sys.path." % (usersitepackagespath))
        log.append("\nFound %s in sys.path." % (usersitepackagespath))

    else:
        sys.path.append(usersitepackagespath)

        print("\nAdded %s to sys.path" % (usersitepackagespath))
        log.append("\nAdded %s to sys.path" % (usersitepackagespath))


def test_import_PIL(installed, log, usersitepackagespath=None):
    if installed:
        if usersitepackagespath:
            update_sys_path(usersitepackagespath, log)

        bpy.utils.refresh_script_paths()

        # try to import Image - if it does, PIL is ready to go
        try:
            from PIL import Image

            print("Successfully imported PIL's Image module. PIL is ready to go.")
            log.append("Successfully imported PIL's Image module. PIL is ready to go.")

            return True, False

        # if it fails, a restart may be required, or an Admin installation may required
        except:
            print("Failed to import PIL's Image module. Restart is required.")
            log.append("Failed to import PIL's Image module. Restart is required.")

            return False, True

    else:
        return False, False


def get_PIL_image_module_path(Image=None):
    try:
        if not Image:
            from PIL import Image

        # module 'PIL._imaging' from '/home/x/.local/lib/python3.7/site-packages/PIL/_imaging.cpython-37m-x86_64-linux-gnu.so'>
        PILRegex = re.compile(r"<module 'PIL._imaging' from '([^']+)'>")

        mo = PILRegex.match(str(Image.core))

        return mo.group(1)

    except:
        return None


# LOGGING

def get_env():
    log = ["\nENVIRONMENT\n"]

    for key, value in os.environ.items():
        log.append("%s: %s\n" % (key, value))

    return log


def write_log(path, log):
    oldlog = []
    env = get_env()

    # read existing log file
    if os.path.exists(path):
        with open(path, mode="r") as f:
            oldlog = f.readlines()

    # write log file
    with open(os.path.join(path), mode="w") as f:
        f.writelines(oldlog + [l + "\n" for l in log] + env)


# LIRARY VALIDATION

def validate_zip_library(names):
    splitnames = [splitpath(name) for name in names]

    # get maxdepth
    maxdepth = max([len(split) for split in splitnames])

    # get entries with a depth of 1
    depth1s = [split[0] for split in splitnames if len(split) == 1]

    # check for .is280 file
    is280s = [split for split in splitnames if len(split) == 2 and split[1] == ".is280"]

    # return the main folder name if all checks pass
    if maxdepth == 3 and len(depth1s) == 1 and len(is280s) == 1:
        return depth1s[0]
