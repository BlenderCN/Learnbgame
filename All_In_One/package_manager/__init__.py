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

bl_info = {
    "name": "Package Manager",
    "author": "Peter Cassetta, John Roper",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "User Preferences > Add-ons > System: Package Manager",
    "description": "Download new add-ons and update current ones",
    "support": 'TESTING',
    "warning": "Early development",
    "wiki_url": "",
    "category": "Learnbgame",
    }


import bpy
import addon_utils
from bpy.types import AddonPreferences
from bpy.props import StringProperty, IntProperty, CollectionProperty

from . classes import PackageManagerAddon
from . import networking

""" Support reloading
if "bpy" in locals():
    import imp
    try:
        imp.reload(networking)
    except NameError:
        from . import networking
else:
    from . import networking
"""


class PackageManagerPreferences(AddonPreferences):
    """Package Manager's add-on preferences.
    
    Entire add-on functionality is available from its preferences panel.
    """
    bl_idname = __name__
    
    pm_addons = CollectionProperty(type=PackageManagerAddon)
    pm_addons_index = IntProperty()
    
    def draw(self, context):
        """Draw preferences UI."""
        
        layout = self.layout
        
        split = layout.split(percentage=1.0/3)
        if (len(self.pm_addons) == 0 or networking.download_install_status in
            ("Processing response", "Downloading update",
            "Processing failed", "Update failed")):
            split.label(text=networking.download_install_status or
                        "Update add-on list.")
        else:
            split.label(text="Available add-ons:")
        split.separator()
        split.operator("wm.update_index", text="Update List",  icon='FILE_REFRESH')
        
        rows = 1 if len(self.pm_addons) == 0 else 4
        layout.template_list("UI_UL_list", "addons_list", self, "pm_addons",
            self, "pm_addons_index", rows=rows)
        
        if len(self.pm_addons) == 0:
            # No add-ons, return
            return
        
        # Display selected add-on
        addon = self.pm_addons[self.pm_addons_index]
        
        installed = any(module.__name__ == addon.module_name for module in addon_utils.modules())
        
        col_box = layout.column()
        box = col_box.box()
        colsub = box.column()
        
        split = colsub.row().split(percentage=0.25)
        if installed and addon.version is not None:
            split.label(text="Installed: Yes, v%s" % addon.version)
        else:
            split.label(text="Installed: No")
        split.separator()
        
        if (networking.download_install_status not in
            ("Processing response", "Downloading update",
            "Processing failed", "Update failed")):
            split.label(text=networking.download_install_status)
        else:
            split.separator()
        
        split.operator("wm.addon_download_install",
                        text="Install from Web",
                        icon='URL').addon = addon.module_name
        
        if addon.description:
            split = colsub.row().split(percentage=0.15)
            split.label(text="Description:")
            split.label(text=addon.description)
        if addon.location:
            split = colsub.row().split(percentage=0.15)
            split.label(text="Location:")
            split.label(text=addon.location)
        if addon.author:
            split = colsub.row().split(percentage=0.15)
            split.label(text="Author:")
            split.label(text=addon.author, translate=False)
        if addon.version:
            split = colsub.row().split(percentage=0.15)
            split.label(text="Version:")
            split.label(text=addon.version, translate=False)
        if addon.warning:
            split = colsub.row().split(percentage=0.15)
            split.label(text="Warning:")
            split.label(text='  ' + addon.warning, icon='ERROR')

        tot_row = bool(addon.wiki_url)

        if tot_row:
            split = colsub.row().split(percentage=0.15)
            split.label(text="Internet:")
            if addon.wiki_url:
                split.operator("wm.url_open", text="Documentation", icon='HELP').url = addon.wiki_url
            split.operator("wm.url_open", text="Report a Bug", icon='URL').url = addon.get(
                    "tracker_url",
                    "http://developer.blender.org/maniphest/task/create/?project=3&type=Bug")
            
            for i in range(4 - tot_row):
                split.separator()


def register():
    """Register classes, operators, and preferences."""
    
    networking.register()
    bpy.utils.register_class(PackageManagerAddon)
    bpy.utils.register_class(PackageManagerPreferences)


def unregister():
    """Unregister classes, operators, and preferences."""
    
    networking.unregister()
    bpy.utils.unregister_class(PackageManagerAddon)
    bpy.utils.unregister_class(PackageManagerPreferences)


if __name__ == "__main__":
    register()