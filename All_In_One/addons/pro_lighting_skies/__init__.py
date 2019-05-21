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


bl_info = {
    "name": "Pro Lighting: Skies (Demo)",
    "author": "Blender Guru",
    "version": (1, 2, 1),
    "blender": (2, 76, 0),
    "location": "Properties > World > Pro Lighting: Skies",
    "description": "Lets you quickly and easily load HDR lighting setups to your scene",
    "warning": "",
    "wiki_url": "blenderguru.com",
    "tracker_url": "http://www.blenderguru.com/contact/",
    "category": "Node"
}


if "bpy" in locals():

    import importlib
    importlib.reload(environment_lighting)

else:

    from . import environment_lighting

import bpy


def register():
    bpy.utils.register_module(__name__)
    environment_lighting.register()


def unregister():
    bpy.utils.unregister_module(__name__)
    environment_lighting.unregister()


if __name__ == "__main__":
    register()
