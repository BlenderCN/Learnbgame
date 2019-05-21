# ====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ======================= END GPL LICENSE BLOCK ========================

import bpy
import addon_utils
import json
import logging
import os
import shutil
import asyncio
import urllib.request
import zipfile
from bpy.props import StringProperty
from . classes import PackageManagerAddon

download_install_status = ""
log = logging.getLogger('networking')

INDEX_DOWNLOAD_URL = ("https://raw.githubusercontent.com/johnroper100/blender-package-manager-addon/master/addons/index.json")

class WM_OT_update_index(bpy.types.Operator):
    """Check for updated list of add-ons available for download"""
    bl_idname = "wm.update_index"
    bl_label = "Check for updated list of add-ons"
    
    _timer = None
    _redraw = False
    
    @classmethod
    def poll(self, context):
        """Run operator only if an asynchronous download is not in progress."""
        
        global download_install_status
        return (not download_install_status
                or download_install_status == "Install successful"
                or "failed" in download_install_status)
    
    def __init__ (self):
        """Init some variables and ensure proper states on run."""
        
        global download_install_status
        download_install_status = ""
        
        self._redraw = False
        
        self.loop = asyncio.get_event_loop()
        self.loop.stop()

    def execute(self, context):
        """Begin asynchronous execution and modal timer."""
        
        self.loop.stop()
        self.status("Starting")
        self.loop.run_in_executor(None, self.update_index)
        
        wm = context.window_manager
        wm.modal_handler_add(self)
        self._timer = wm.event_timer_add(0.0001, context.window)
        
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        """Check status of list update and terminate operator when complete."""
        
        global download_install_status
        
        if self._redraw:
            context.area.tag_redraw()
            self._redraw = False
        
        if "failed" in download_install_status:
            self.cancel(context)
            return {'CANCELLED'}
        
        if download_install_status == "":
            self.cancel(context)
            return {'FINISHED'}
        
        return {'PASS_THROUGH'}

    def cancel(self, context):
        """Ensure timer and loop are stopped before operator ends."""
        
        self.loop.stop()
        
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
    
    def status(self, text: str):
        """Change list update status for access from main thread, and redraw UI.
        
        Keyword arguments:
        text -- new status
        """
        
        global download_install_status
        
        download_install_status = text
        self._redraw = True
    
    def update_index(self):
        """Download index.json and update add-on list."""
        
        self.status("Downloading update")
        index_file = self.download_index()
        
        if index_file:
            self.status("Processing response")
            
            if self.parse_json(index_file):
                self.status("")
                return
            
            self.status("Processing failed")
            return
        
        self.status("Update failed")
    
    def download_index(self):
        """Download index.json and return it as a str, or return False if an
        error occurs.
        """
        
        try:
            req = urllib.request.urlopen(INDEX_DOWNLOAD_URL)
            index_file = req.read().decode('utf-8')
            req.close()
        except urllib.error.HTTPError as err:
            log.warning("Error requesting update: %s %s", err.code, err.reason)
            return False
        except urllib.error.URLError as err:
            log.warning("Download failed with URLError: %s", err)
            return False
        
        return index_file
    
    def parse_json(self, index_file: str) -> bool:
        """Parse JSON text and create add-on entries from data, return True on
        success or False when an error occurs during parsing.
        
        Keyword arguments:
        index_file -- JSON text
        """
        
        # Parse downloaded file
        try:
            addon_list = json.loads(index_file)
        except ValueError as err:
            log.warning("JSON file could not parse. ValueError: %s", err)
            return False
        
        # Get the add-on preferences
        prefs = bpy.context.user_preferences.addons.get("package_manager").preferences
            
        # Clear previous list of add-ons
        prefs.pm_addons.clear()
        prefs.pm_addons_index = 0
        
        user_path = bpy.utils.user_resource('SCRIPTS', path="addons")
        installed = addon_utils.modules()
        
        # Loop through every add-on in the parsed json
        for name, content in addon_list["addons"].items():
            # Skip add-ons not installed to USER path
            # TODO: support above later
            for a in set(installed):
                if name == a.__name__ and user_path not in a.__file__:
                    log.info("Not listing add-on %s, as it is installed to "
                                "location other than USER path", name)
                    break
            else:
                # Add new add-on to the list
                addon = prefs.pm_addons.add()

                self.load_addon_data(addon, name, content)
        
        return True
    
    def load_addon_data(self, addon: PackageManagerAddon, module_name: str,
                        content: dict):
        """Load interpreted JSON data into a PackageManagerAddon object
        
        Keyword arguments:
        addon -- PackageManagerAddon to populate
        module_name -- module name of add-on
        content -- dict with parsed JSON data
        """
        
        addon.name = content["name"]
        addon.blender = '.'.join(map(str, content["blender"]))
        addon.module_name = module_name
        addon.download_url = content["download_url"]
        
        optional_keys = ["author", "category", "description", "location",
                        "source", "support", "tracker_url", "warning", "wiki_url"]
        
        for key in optional_keys:
            if key in content:
                addon[key] = content[key]
        
        if "version" in content:
            # TODO: add multi-version functionality
            addon.version = '.'.join(map(str, content["version"]))


class WM_OT_addon_download_install(bpy.types.Operator):
    """Download and install add-on"""
    bl_idname = "wm.addon_download_install"
    bl_label = "Download and install selected add-on"
    
    addon = bpy.props.StringProperty()
    
    _timer = None
    _redraw = False
    
    @classmethod
    def poll(self, context):
        """Run operator only if an asynchronous download is not in progress."""
        
        global download_install_status
        return (not download_install_status
                or download_install_status == "Install successful"
                or "failed" in download_install_status)
    
    def __init__ (self):
        """Init some variables and ensure proper states on run."""
        
        global download_install_status
        download_install_status = ""
        
        self._redraw = False
        
        self.loop = asyncio.get_event_loop()
        self.loop.stop()

    def execute(self, context):
        """Perform verification on selected addon, then begin asynchronous
        execution and modal timer.
        """
        
        if self.addon is None:
            return {'CANCELLED'}
        
        # Get the add-on preferences
        prefs = bpy.context.user_preferences.addons.get("package_manager").preferences
        
        # Verify add-on is in list and find its download url
        download_url = ""
        for addon in prefs.pm_addons:
            if addon.module_name == self.addon:
                download_url = addon.download_url
                break
        else:
            return {'CANCELLED'}
        
        ext = os.path.splitext(download_url)[1]
        
        # Download and install the selected add-on
        self.loop.stop()
        
        self.status("Starting")
        
        self.loop.run_in_executor(None, self.download_and_install,
                                    self.addon, download_url, ext)
        
        wm = context.window_manager
        wm.modal_handler_add(self)
        self._timer = wm.event_timer_add(0.0001, context.window)
        
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        """Check status of download/install, and exit operator when complete."""
        
        global download_install_status
        
        if self._redraw:
            context.area.tag_redraw()
            self._redraw = False
        
        if "failed" in download_install_status:
            self.cancel(context)
            return {'CANCELLED'}
        
        if download_install_status == "Install successful":
            self.cancel(context)
            return {'FINISHED'}
        
        return {'PASS_THROUGH'}

    def cancel(self, context):
        """Ensure timer and loop are stopped before operator ends."""
        
        self.loop.stop()
        
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
    
    def status(self, text: str):
        """Change install/download status for access from main thread, and
        redraw UI.
        
        Keyword arguments:
        text -- new status
        """
        
        global download_install_status
        
        download_install_status = text
        self._redraw = True
    
    def download_and_install (self, addon: str, download_url: str,
                                filetype: str):
        """Download add-on of filetype from download_url and install it.
        
        Keyword arguments:
        addon -- module name of the add-on to install
        download_url -- the url to download add-on from 
        filetype -- the filetype of the add-on, .py or .zip
        """
        
        self.status("Downloading")
        if self.download(download_url):
            self.status("Installing")
            if self.install(addon, filetype):
                self.status("Install successful")
                return
            self.status("Install failed")
            return
        
        self.status("Download failed")
        self._redraw = True
    
    def download(self, download_url: str):
        """Download add-on from download_url and save it to disk. Return False
        on download error, or True if successful.
        
        Keyword arguments:
        download_url -- the url to download add-on from 
        """
        
        filetype = os.path.splitext(download_url)[1]
        
        download_path = bpy.utils.user_resource('SCRIPTS', path="addons/"
                                                "package_manager/download%s"
                                                % filetype)
        
        # Download add-on and save to disk
        try:
            req = urllib.request.urlopen(download_url)
            with open(download_path, 'wb') as download_file:
                shutil.copyfileobj(req, download_file)
            req.close()
        except urllib.error.HTTPError as err:
            log.warning("Download failed with HTTPError: %s %s", str(err.code),
                        err.reason)
            return False
        except urllib.error.URLError as err:
            log.warning("Download failed with URLError: %s", err)
            return False
        
        return True

    def install(self, addon: str, filetype: str):
        """Install downloaded add-on on disk to USER add-ons path. Return False
        on installation error, or True if successful.
        
        Keyword arguments:
        addon -- module name of the add-on to install
        filetype -- the filetype of the add-on, .py or .zip 
        """
        
        filename = addon + (filetype if filetype == ".py" else "")
        
        download_path = bpy.utils.user_resource('SCRIPTS', path="addons/"
                                                "package_manager/download%s"
                                                % filetype)
        addon_path = bpy.utils.user_resource('SCRIPTS', path="addons/%s" % filename)
        
        # Copy downloaded add-on to USER scripts path
        try:
            if filetype == ".py":
                shutil.move(download_path, addon_path)
            elif filetype == ".zip":
                # Remove existing add-on
                if os.path.exists(addon_path):
                    shutil.rmtree(addon_path)
                with zipfile.ZipFile(download_path,"r") as zipped_addon:
                    zipped_addon.extractall(bpy.utils.user_resource('SCRIPTS', path="addons"))
            else:
                return False
        except Exception as err:
            log.warning("Install failed: %s", err)
            return False
        
        return True


def register():
    """Register operators."""
    
    bpy.utils.register_class(WM_OT_update_index)
    bpy.utils.register_class(WM_OT_addon_download_install)

def unregister():
    """Unregister operators."""
    
    bpy.utils.unregister_class(WM_OT_update_index)
    bpy.utils.unregister_class(WM_OT_addon_download_install)