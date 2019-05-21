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
    "name" : "File Browser Display Override",
    "author" : "chebhou, poor",
    "version" : (1, 1, 0),
    "blender" : (2, 78, 0),
    "location" : "File Browser",
    "description" : "Override File Browser Display Settings",
    "warning" : "",
    "wiki_url" : "https://blender.stackexchange.com/a/28054/935",
    "tracker_url" : "https://gist.github.com/p2or/59b2795f011f2f024f5e781d1a33a5da",
    "category" : "User Interface"
}

import bpy
from bpy.props import (BoolProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )

class OverrideFileBrowserSettingsPreferences(AddonPreferences):
    """Add-on Preferences"""

    bl_idname = __name__

    enable_panel = EnumProperty(
        name="Enable Panel per Operator",
        description="Enable Override Panel for certain Operators",
        items=(('ALL', "All Operators", "Always override the Settings", "RESTRICT_SELECT_OFF", 0),
               ('IMAGE_OT_open', "Open Image Operator", "When Opening an Image (Image Editor)", "IMAGE_DATA", 1),
               ('WM_OT_open_mainfile', "Open Blend Operator", "When Opening a Blend", "FILE_FOLDER", 2),
               ('WM_OT_recover_auto_save', "Recover Operator", "When Recovering a Blend", "RECOVER_LAST", 3),
               ('WM_OT_link', "Link Operator", "When Linking a Blend", "LINK_BLEND", 4),
               ('WM_OT_append', "Append Operator", "When Appending a Blend", "APPEND_BLEND", 5)),
        default='ALL'
        )

    enable_sort = BoolProperty(
        name="Sort Method",
        description="Enable Sort Method Override",
        default=True
        )

    enable_type = BoolProperty(
        name="Display Type",
        description="Enable Display Type Override",
        default=True
        )

    enable_size = BoolProperty(
        name="Display Size",
        description="Enable Display Size Override",
        default=True
        )

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, "enable_panel")
        row = layout.row(align=True)
        row.prop(self, "enable_sort", toggle=True)
        row.prop(self, "enable_type", toggle=True)
        row.prop(self, "enable_size", toggle=True)
        layout.operator("filebrowser_display_override.reset_preferences",
            icon='FILE_REFRESH')


class ResetOverrideFileBrowserSettings(Operator):
    """Reset Add-on Preferences"""

    bl_idname = "filebrowser_display_override.reset_preferences"
    bl_label = "Reset Preferences"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        scn = context.scene
        prefs = context.user_preferences.addons[__name__].preferences
        prefs.property_unset("enable_panel")
        prefs.property_unset("enable_sort")
        prefs.property_unset("enable_type")
        prefs.property_unset("enable_size")
        bpy.ops.wm.save_userpref() # Save
        return {'FINISHED'}


class OverrideFileBrowserSettingsProperties(PropertyGroup):
    """Add-on Properties"""

    override = bpy.props.BoolProperty(
        name="Override Display Settings",
        default=True
        )

    display_type = bpy.props.EnumProperty(
        name="Display Mode",
        items=(('LIST_SHORT', 'Short List', 'Display Short List', 'SHORTDISPLAY', 0),
               ('LIST_LONG', 'Long List', 'Display Short List', 'LONGDISPLAY', 1),
               ('THUMBNAIL', 'Thumbnails', 'Display Thumbnails', 'IMGDISPLAY', 2)),
        default='THUMBNAIL'
        )

    sort_method = bpy.props.EnumProperty(
        name="Sort Method",
        items=(('FILE_SORT_ALPHA', "Name", 'Sort by Name', 'SORTALPHA', 0),
               ('FILE_SORT_EXTENSION', "Extension", 'Sort by Name Extension', 'SORTBYEXT', 1),
               ('FILE_SORT_TIME', "Date", 'Sort by Date', 'SORTTIME', 2),
               ('FILE_SORT_SIZE', "Size", 'Sort by Size', 'SORTSIZE', 3)),
        default='FILE_SORT_TIME'
        )

    display_size = bpy.props.EnumProperty(
        name="Display Size",
        items=(('TINY', "Tiny", 'Tiny Items', 0),
               ('SMALL', "Small", 'Small Items', 1),
               ('NORMAL', "Normal", 'Normal Items', 2),
               ('LARGE', "Large", 'Large Items', 3)),
        default='TINY'
        )


class OverrideFileBrowserSettingsPanel(Panel):
    """Add-on Panel"""

    bl_idname = "FILEBROWSER_PT_settings_override"
    bl_label = "File Browser Display Settings"
    bl_space_type = "FILE_BROWSER"
    bl_region_type = 'TOOL_PROPS'

    @classmethod
    def poll(cls, context):
        prefs = context.user_preferences.addons[__name__].preferences
        if context.space_data.active_operator is not None:
            return context.space_data.active_operator.bl_idname == prefs.enable_panel or \
                prefs.enable_panel == 'ALL'
        else:
            return context.area.type == 'FILE_BROWSER'

    def draw(self, context):
            scn = context.scene
            browser = context.space_data
            props = scn.filebrowser_display_override
            prefs = context.user_preferences.addons[__name__].preferences

            layout = self.layout
            row = layout.row()
            row.prop(props, "override")

            if prefs.enable_sort:
                layout.row().prop(props, "sort_method", text="Sort by")
                if props.override:
                    if browser.params.sort_method != props.sort_method:
                        context.space_data.params.sort_method = props.sort_method

            if prefs.enable_type:
                layout.row().prop(props, "display_type", text="Display")
                if props.override:
                    if browser.params.display_type != props.display_type:
                        context.space_data.params.display_type = props.display_type

            if prefs.enable_size:
                layout.row().prop(props, "display_size", text="Size")
                if props.override:
                    if browser.params.display_size != props.display_size:
                        context.space_data.params.display_size = props.display_size


'''
# Menu does not update properly
class OverrideFileBrowserSettingsMenu(bpy.types.Menu):
    """Add-on Menu"""

    bl_label = "Override Display Settings"
    bl_idname = "FILE_BROWSER_MT_override"

    @classmethod
    def poll(cls, context):
        prefs = context.user_preferences.addons[__name__].preferences
        if context.space_data.active_operator is not None:
            return context.space_data.active_operator.bl_idname == prefs.enable_panel or \
                prefs.enable_panel == 'ALL'
        else:
            return context.area.type == 'FILE_BROWSER'

    def draw(self, context):
        scn = context.scene
        browser = context.space_data
        props = scn.filebrowser_display_override
        prefs = context.user_preferences.addons[__name__].preferences

        layout = self.layout
        layout.prop(props, "override")
        layout.prop_menu_enum(props, "sort_method")
        if props.override:
            if browser.params.sort_method != props.sort_method:
                context.space_data.params.sort_method = props.sort_method
                # update via context.area.tag_redraw() does not work

        layout.prop_menu_enum(props, "display_type")
        if props.override:
            if browser.params.display_type != props.display_type:
                context.space_data.params.display_type = props.display_type


def draw_filebrowser_override(self, context):
    layout = self.layout
    layout.menu(OverrideFileBrowserSettingsMenu.bl_idname)
'''


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.filebrowser_display_override = PointerProperty(
        type=OverrideFileBrowserSettingsProperties)
    #bpy.types.FILEBROWSER_HT_header.append(draw_filebrowser_override)

def unregister():
    #bpy.types.FILEBROWSER_HT_header.remove(draw_filebrowser_override)
    del bpy.types.Scene.filebrowser_display_override
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
