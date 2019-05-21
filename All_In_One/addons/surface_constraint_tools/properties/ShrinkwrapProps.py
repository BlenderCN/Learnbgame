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

# <pep8-80 compliant>

import bpy

class ShrinkwrapProps(bpy.types.PropertyGroup):
    data_path =(
        "user_preferences.addons['{0}'].preferences.shrinkwrap"
    ).format(__package__.split(".")[0])

    # Shrinkwrap Settings
    only_selected_are_affected = bpy.props.BoolProperty(
        name = "Selected Only",
        description = (
            "Limit the shrinkwrap operation's effect to the selected " +
            "vertices only."
        ),
        default = False
    )

    # UI Visibility
    settings_ui_is_visible = bpy.props.BoolProperty(
        name = "Settings UI Visibility",
        description = "Show/hide the Settings UI.",
        default = False
    )
