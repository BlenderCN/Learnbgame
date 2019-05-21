# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Mitsuba Add-On
# --------------------------------------------------------------------------
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENSE BLOCK *****

bl_info = {
    "name": "Mitsuba",
    "author": "Wenzel Jakob, Bartosz Styperek, Francesc Juhe",
    "version": (0, 5, 1),
    "blender": (2, 80, 0),
    "category": "Learnbgame",
    "location": "Info header, render engine menu",
    "warning": "",
    "wiki_url": "http://www.mitsuba-renderer.org/docs.html",
    "tracker_url": "https://www.mitsuba-renderer.org/bugtracker/projects",
    "description": "Mitsuba Renderer integration for Blender"
}

if 'core' in locals():
    import imp
    imp.reload(core)

else:
    import bpy
    from bpy.types import AddonPreferences
    from bpy.props import StringProperty, EnumProperty
    from .extensions_framework import Addon
    import nodeitems_utils

    def find_mitsuba_path():
        from os import getenv
        from .extensions_framework import util as efutil

        return getenv(
            # Use the env var path, if set ...
            'MITSUBA_ROOT',
            # .. or load the last path from CFG file
            efutil.find_config_value('mitsuba', 'defaults', 'install_path', '')
        )

    class MitsubaAddonPreferences(AddonPreferences):
        # this must match the addon name
        bl_idname = __name__

        install_path = StringProperty(
                name="Path to Mitsuba Installation",
                description='Path to Mitsuba install directory',
                subtype='DIR_PATH',
                default=find_mitsuba_path(),
                )

        preview_export = EnumProperty(
                name="Preview Export Type",
                description='Export type to be used on material preview. Write file can be useful for debugging material preview settings.',
                items=[
                    ('API', 'Internal', 'API'),
                    ('FILE', 'Write File', 'FILE'),
                ],
                default='API',
                )

        def draw(self, context):
            layout = self.layout
            #layout.label(text="This is a preferences view for our addon")
            layout.prop(self, "install_path")
            layout.prop(self, "preview_export")

    MitsubaAddon = Addon(bl_info)

    def get_prefs():
        return bpy.context.user_preferences.addons[__name__].preferences

    # patch the MitsubaAddon class to make it easier to get the addon prefs
    MitsubaAddon.get_prefs = get_prefs

    addon_register, addon_unregister = MitsubaAddon.init_functions()

    def register():
        bpy.utils.register_class(MitsubaAddonPreferences)
        nodeitems_utils.register_node_categories("MITSUBA_SHADER_NODES", ui.space_node.mitsuba_shader_node_catagories)
        addon_register()

    def unregister():
        bpy.utils.unregister_class(MitsubaAddonPreferences)
        nodeitems_utils.unregister_node_categories("MITSUBA_SHADER_NODES")
        addon_unregister()

    # Importing the core package causes extensions_framework managed
    # RNA class registration via @MitsubaAddon.addon_register_class
    from . import core
