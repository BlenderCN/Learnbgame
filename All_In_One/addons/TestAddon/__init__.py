# ##### BEGIN GPL LICENSE BLOCK #####
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

bl_info = {
    "name": "Test Add-on",
    "author": "Andrew Peel",
    "version": (2, 1, 2),
    "blender": (2, 7, 0),
    "location": "Tools Shelf",
    "description": "This is a test add-on",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}

import bpy

from . import addon_updater_ops

class PANEL_Test_Panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Test Panel"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = "TEST"
    
    def draw(self, context):
        layout = self.layout
        layout.label("This is a test interface")
        layout.label(str(bl_info["version"]))

class DemoPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    auto_check_update = bpy.props.BoolProperty(
        name = "Auto-check for Update",
        description = "If enabled, auto-check for updates using an interval",
        default = False,
        )
    
    updater_intrval_months = bpy.props.IntProperty(
        name='Months',
        description = "Number of months between checking for updates",
        default=0,
        min=0
        )
    updater_intrval_days = bpy.props.IntProperty(
        name='Days',
        description = "Number of days between checking for updates",
        default=7,
        min=0,
        )
    updater_intrval_hours = bpy.props.IntProperty(
        name='Hours',
        description = "Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
        )
    updater_intrval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description = "Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
        )

    def draw(self, context):
        addon_updater_ops.update_settings_ui(self,context)

def register():
    addon_updater_ops.register(bl_info)
    bpy.utils.register_class(DemoPreferences)
    bpy.utils.register_class(PANEL_Test_Panel)
    
def unregister():
    addon_updater_ops.unregister(bl_info)
    bpy.utils.unregister_class(PANEL_Test_Panel)
    bpy.utils.unregister_class(DemoPreferences)
    
if __name__ == "__main__":
    register()
