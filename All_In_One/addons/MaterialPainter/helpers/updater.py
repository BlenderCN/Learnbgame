from libs.addon_updater.addon_updater import Updater as updater
"""
    This file contains all the customizations and code needed for making the addon updater (which is an external lib)
    working within your blender module
"""

# More info at https://github.com/CGCookie/blender-addon-updater
def checkedForUpdates(res):
    print("CHECK FOR UPDATESFINISHED", res)
    if updater.update_ready == True:
        res = updater.run_update(force=False, revert_tag=None, callback=None)
        if res == 0:
            print("Update ran successfully, restart blender")
        else:
            print("Updater returned " + str(res) + ", error occurred")
    elif updater.update_ready == False:
        print("No update available")
    elif updater.update_ready == None:
        print("You need to check for an update first")

def init(bl_info):
    """
    This function initializes updater addon as the operator defined in libs/addon_updater/addon_updater_ops.py does.
    Hence you do not need to amend the config in the above operator

    The default configuration will run and update the addon at startup

    :param bl_info:
    :return: None
    """
    updater.user = "gnuton"
    updater.repo = "MaterialPainter"
    updater.website = "https://github.com/gnuton/MaterialPainter/"
    updater.current_version = bl_info["version"]
    #updater.showpopups = True
    updater.verbose = True
    updater.backup_current = False
    updater.fake_install = True #FIXME Actually DISABLES this plugin
    updater.subfolder_path = "libs/addon_updater/"
    updater.check_for_update_now(callback=checkedForUpdates)