# This file is part of Hypermesh.
#
# Hypermesh is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hypermesh is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hypermesh.  If not, see <http://www.gnu.org/licenses/>.

import bpy


class HypermeshPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    debugging = bpy.props.BoolProperty(
        name="Debugging",
        default=False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "debugging")


def debug_message(msg):
    try:
        if bpy.context.user_preferences.addons[__package__].preferences.debugging:
            print("Hypermesh: " + msg)
    except KeyError:
        pass
