#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import zipfile
import json
import urllib.request
import addon_utils
import os
import shutil
import sys


def get_addon_name():
    return __package__.split(".")[0]


def addon_name_lowercase():
    return get_addon_name().lower()


def get_addon_preferences():
    return bpy.context.preferences.addons[get_addon_name()].preferences


def get_json_from_remonte():
    tags_url = 'https://dl.dropboxusercontent.com/s/fal8zbspa53v8js/garment_tool_releases.json?dl=0'
    response = urllib.request.urlopen(tags_url).read()
    tags_json = json.loads(response)
    return tags_json


def get_installed_version():
    installed_ver = ''
    addon_ver = sys.modules[__package__].bl_info.get('version')
    for a in addon_ver:
        installed_ver += str(a)+'.'
    return installed_ver[:-1]


def check_update_exist():
    tags_json = get_json_from_remonte()
    remonte_ver = tags_json[-1]['version']
    installed_ver = get_installed_version()
    return remonte_ver != installed_ver, remonte_ver


def get_latest_version_url():
    tags_json = get_json_from_remonte()
    if len(tags_json) == 0:
        print('Remonte releases list is empty')
        return None
    zip_url = tags_json[-1]['download_url']
    return zip_url


def get_current_version_url():
    tags_json = get_json_from_remonte()
    if len(tags_json) == 0:
        print('Remonte releases list is empty')
        return None
    installed_ver = get_installed_version()
    for i, release in enumerate(tags_json):
        if release['version'] == installed_ver:
            return tags_json[i]['download_url']
    return None


def get_previous_version_url():
    tags_json = get_json_from_remonte()
    if len(tags_json) == 0:
        print('Remonte releases list is empty')
        return None, None
    installed_ver = get_installed_version()
    for i, release in enumerate(tags_json):
        if release['version'] == installed_ver:
            if i >= 1:
                return tags_json[i-1]['download_url'], tags_json[i-1]['version']
            else:
                return None, None


def clean_dir(folder):
    for the_file in os.listdir(folder):
        if the_file.startswith(('.vscode', '.git')):
            continue
        if the_file in ('addon_update.zip'):  # do not remove downloadded update  # debug - 'update_addon.py'
            continue
        file_path = os.path.join(folder, the_file)
        print(f'Cleaning {the_file}')
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)


def reload_addon():
    print("Reloading addon...")
    addon_utils.modules(refresh=True)
    bpy.utils.refresh_script_paths()
    # not allowed in restricted context, such as register module
    # toggle to refresh
    # mod_name = __package__[:]
    # bpy.ops.wm.addon_disable(module=mod_name)
    # bpy.ops.wm.addon_refresh()
    # bpy.ops.wm.addon_enable(module=mod_name)


def get_update(zip_url):
    temp_zip_file_name = 'addon_update.zip'  # temp zip, should be removed later...

    current_dir = os.path.split(__file__)[0]
    zip_file_path = os.path.join(current_dir, temp_zip_file_name)
    urllib.request.urlretrieve(zip_url, zip_file_path)
    addon_zip_file = zipfile.ZipFile(zip_file_path, 'r')

    clean_dir(current_dir)  # remove old files before update

    # addon_zip_file.extractall(directory_to_extract_to) #we could do this but zip contains weird root folder name
    created_sub_dirs = []
    for name in addon_zip_file.namelist():
        if '/' not in name:
            continue
        top_folder = name[:name.index('/')+1]
        if name == top_folder:
            continue  # skip top level folder
        subpath = name[name.index('/')+1:]
        if subpath.startswith(('.vscode', '.git', '__pycache__')):
            continue
        if subpath.endswith(('.pyc')):
            continue
        sub_path, file_name = os.path.split(subpath)  # splits
        #bug - os.path.exists(os.path.join(current_dir, sub_path)) - dosent detect path created in previous iteraiton. Use created_sub_dirs, to store dirs
        if sub_path and sub_path not in created_sub_dirs and not os.path.exists(os.path.join(current_dir, sub_path)):
            try:
                os.mkdir(os.path.join(current_dir, sub_path))
                created_sub_dirs.append(sub_path)
                # print("Extract - mkdir: ", os.path.join(current_dir, subpath))
            except OSError as exc:
                print("Could not create folder from zip")
                return 'Install failed'
        with open(os.path.join(current_dir, subpath), "wb") as outfile:
            data = addon_zip_file.read(name)
            outfile.write(data)
            print("Extracting :", os.path.join(current_dir, subpath))
    addon_zip_file.close()
    os.remove(zip_file_path)
    reload_addon()
    return


class AddonCheckUpdateExist(bpy.types.Operator):
    bl_idname = addon_name_lowercase()+".check_for_update"
    bl_label = "Check for update"
    bl_description = "Check for update"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        addon_prefs = get_addon_preferences()
        update_exist, remonte_ver = check_update_exist()
        if update_exist:
            self.report({'INFO'}, f'Found new update: {remonte_ver}')
            addon_prefs.update_text = f'Found new update: {remonte_ver}'
            addon_prefs.update_exist = True
        else:
            self.report({'INFO'}, 'Nothing to update')
            addon_prefs.update_text = 'Nothing to update'
            addon_prefs.update_exist = False

        return {"FINISHED"}


class AddonUpdate(bpy.types.Operator):
    bl_idname = addon_name_lowercase()+".update_addon"
    bl_label = "Update addon"
    bl_description = "Download and install addon. May require blender restart"
    bl_options = {"REGISTER", "UNDO"}

    reinstall: bpy.props.BoolProperty(name='Reinstall', description='Force reinstalling curernt version', default=False)

    def execute(self, context):
        addon_prefs = get_addon_preferences()
        if self.reinstall:
            latest_zip_url = get_current_version_url()
        else:
            latest_zip_url = get_latest_version_url()

        if latest_zip_url:
            print('Downloading addon')
            addon_prefs.update_text = 'Downloading addon'
            get_update(latest_zip_url)
            text = 'reinstalled' if self.reinstall else 'updated'
            self.report({'INFO'}, f'Addon {text}')
            addon_prefs.update_text = f'Addon {text}. Consider restarting blender'
            addon_prefs.update_exist = False

        return {"FINISHED"}


class AddonRollBack(bpy.types.Operator):
    bl_idname = addon_name_lowercase()+".rollback_addon"
    bl_label = "Get previous version"
    bl_description = "Download and install previous version (if exist)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        addon_prefs = get_addon_preferences()
        prevous_version_url, prev_ver_id = get_previous_version_url()
        if prevous_version_url:
            print('Reverting addon')
            addon_prefs.update_text = f'Reverting addon to {prev_ver_id}'
            get_update(prevous_version_url)
            self.report({'INFO'}, 'Addon Reverted')
            addon_prefs.update_text = 'Addon reverted. Consider restarting blender'
            addon_prefs.update_exist = False
        else:
            addon_prefs.update_text = 'No previous version found!'
        return {"FINISHED"}
