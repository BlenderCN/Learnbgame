import bpy
import os
import platform
from .. utils.registration import get_prefs, get_path
from .. utils.system import makedir, write_log, get_python_paths, install_pip, update_pip, install_PIL, easy_install_PIL, test_import_PIL, remove_PIL


version = None
# version = "5.4.1"
version = "6.0.0"


class InstallPIL(bpy.types.Operator):
    bl_idname = "machin3.install_pil"
    bl_label = "MACHIN3: Install PIL"
    bl_description = "Install pip and PIL on the User Level"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global version

        log = []
        logspath = makedir(os.path.join(get_path(), "logs"))

        print("\nDECALmachine: Installing PIL %s\n" % version)
        print("Platform:", platform.system())

        log.append("\nDECALmachine: Installing PIL %s\n" % version)
        log.append("Platform: %s" % (platform.system()))

        # get/contruct paths
        pythonbinpath, pythonlibpath, ensurepippath, modulespaths, sitepackagespath, usersitepackagespath, _, _ = get_python_paths(log)

        # before anything is done, check if there are existing PIL/Pillow installatinos, that may prevent our current attempt
        remove_PIL(sitepackagespath, usersitepackagespath, modulespaths, log)

        print()
        log.append("\n")

        # install pip - in user site-package
        installed = install_pip(pythonbinpath, ensurepippath, log, mode='USER')

        # update pip and install PIL - in user site-packages
        if installed:
            installed = update_pip(pythonbinpath, log, mode='USER')

            installed = install_PIL(pythonbinpath, log, version=version, mode='USER')

            # if PIL installed, update sys.path with the user site-packages path and check if Image can be imported
            get_prefs().pil, get_prefs().pilrestart = test_import_PIL(installed, log, usersitepackagespath)

        # write the log
        logpath = os.path.join(logspath, "pil.log")
        write_log(logpath, log)

        return {'FINISHED'}


class InstallPILAdmin(bpy.types.Operator):
    bl_idname = "machin3.install_pil_admin"
    bl_label = "MACHIN3: Install PIL (Admin)"
    bl_description = "Install pip and PIL for Blender's Python"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        if platform.system() == "Darwin" and "AppTranslocation" in bpy.app.binary_path:
            return False
        return True

    def execute(self, context):
        global version

        log = []
        logspath = makedir(os.path.join(get_path(), "logs"))

        print("\nDECALmachine: Installing PIL %s (Admin)\n" % version)
        print("Platform:", platform.system())

        log.append("\nDECALmachine: Installing PIL %s (Admin)\n" % version)
        log.append("Platform: %s" % (platform.system()))

        # get/contruct paths
        pythonbinpath, pythonlibpath, ensurepippath, modulespaths, sitepackagespath, usersitepackagespath, _, _ = get_python_paths(log)

        # before anything is done, check if there are existing PIL/Pillow installatinos, that may prevent our current attempt
        remove_PIL(sitepackagespath, usersitepackagespath, modulespaths, log)

        print()
        log.append("\n")

        # install pip - in site-packages
        installed = install_pip(pythonbinpath, ensurepippath, log, mode='ADMIN')

        # update pip and install PIL - in site-packages
        if installed:
            installed = update_pip(pythonbinpath, log, mode='ADMIN')

            installed = install_PIL(pythonbinpath, log, version=version, mode='ADMIN')

            # if PIL installed, check if Image can be imported
            get_prefs().pil, get_prefs().pilrestart = test_import_PIL(installed, log)

        # write the log
        logpath = os.path.join(logspath, "pil.log")
        write_log(logpath, log)

        return {'FINISHED'}


class EasyInstallPILAdmin(bpy.types.Operator):
    bl_idname = "machin3.easy_install_pil_admin"
    bl_label = "MACHIN3: Easy Install PIL (Admin)"
    bl_description = "Easy Installs PIL for Blender's Python"
    bl_options = {'REGISTER'}


    @classmethod
    def poll(cls, context):
        if platform.system() == "Darwin" and "AppTranslocation" in bpy.app.binary_path:
            return False
        return True


    def execute(self, context):
        global version

        log = []
        logspath = makedir(os.path.join(get_path(), "logs"))

        print("\nDECALmachine: Easy Installing PIL %s (Admin)\n" % version)
        print("Platform:", platform.system())

        log.append("\nDECALmachine: Easy Installing PIL %s (Admin)\n" % version)
        log.append("Platform: %s" % (platform.system()))

        # get/contruct paths
        pythonbinpath, pythonlibpath, ensurepippath, modulespaths, sitepackagespath, usersitepackagespath, easyinstallpath, easyinstalluserpath = get_python_paths(log)

        # before anything is done, check if there are existing PIL/Pillow installatinos, that may prevent our current attempt
        remove_PIL(sitepackagespath, usersitepackagespath, modulespaths, log)

        print()
        log.append("\n")

        # install pip - in site-packages
        installed = install_pip(pythonbinpath, ensurepippath, log, mode='ADMIN')

        # update pip and install PIL - in site-packages
        if installed:
            installed = update_pip(pythonbinpath, log, mode='ADMIN')

            installed = easy_install_PIL(pythonbinpath, easyinstallpath, easyinstalluserpath, log, version=version, mode='ADMIN')

            # if PIL installed, check if Image can be imported
            get_prefs().pil, get_prefs().pilrestart = test_import_PIL(installed, log)

        # write the log
        logpath = os.path.join(logspath, "pil.log")
        write_log(logpath, log)

        return {'FINISHED'}


class PurgePIL(bpy.types.Operator):
    bl_idname = "machin3.purge_pil"
    bl_label = "MACHIN3: Purge PIL"
    bl_description = "Attempt to remove PIL from the current user profile and Blender Python's site-packages."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        log = []
        logspath = makedir(os.path.join(get_path(), "logs"))

        print("\nDECALmachine: Purging PIL\n")
        print("Platform:", platform.system())

        log.append("\nDECALmachine: Purging PIL\n")
        log.append("Platform: %s" % (platform.system()))

        # get/contruct paths
        _, _, _, modulespaths, sitepackagespath, usersitepackagespath, _, _ = get_python_paths(log)

        remove_PIL(sitepackagespath, usersitepackagespath, modulespaths, log)

        get_prefs().pil = False
        get_prefs().pilrestart = False

        # write the log
        logpath = os.path.join(logspath, "pil.log")
        write_log(logpath, log)

        return {'FINISHED'}
