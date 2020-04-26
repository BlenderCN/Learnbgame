#====================== BEGIN GPL LICENSE BLOCK ======================
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
#======================= END GPL LICENSE BLOCK ========================

# <pep8 compliant>
bl_info = {
    "name": "Cork on Blender",
    "author": "Dalai Felinto, Cicero Moraes and Everton da Rosa",
    "version": (1, 0),
    "blender": (2, 7, 6),
    "location": "Tool Shelf",
    "description": "Interface to use Cork library for advanced boolean operations",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


import bpy
from bpy.props import StringProperty

from . import init


# Preferences
class CorkMeshSlicerPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    cork_filepath = StringProperty(
        name="Cork Executable",
        description="Location of cork binary file",
        subtype="FILE_PATH",
        default="",
        )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "cork_filepath")


def register():
    bpy.utils.register_class(CorkMeshSlicerPreferences)
    init.register()


def unregister():
    bpy.utils.unregister_class(CorkMeshSlicerPreferences)
    init.unregister()


if __name__ == '__main__':
    register()
