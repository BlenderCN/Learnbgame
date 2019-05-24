# ***** BEGIN GPL LICENSE BLOCK *****
#
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
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# PEP8 compliant (https://www.python.org/dev/peps/pep-0008)

# ----------------------------------------------------------
# File: __init__.py
# Author: Antonio Vazquez (antonioya)
# ----------------------------------------------------------

# ----------------------------------------------
# Define Addon info
# ----------------------------------------------
bl_info = {
    "name": "Window Generator 3 (continuous editable parameters)",
    "author": "SayPRODUCTION, Antonio Vazquez (antonioya)",
    "version": (3, 0),
    "blender": (2, 7, 3),
    "location": "View3D > Toolshelf > Add Window",
    "description": "Window Generator with continuous editing and cycles materials",
    "category": "Learnbgame",
}

import sys
import os

# ----------------------------------------------
# Add to Phyton path (once only)
# ----------------------------------------------
path = sys.path
flag = False
for item in path:
    if "add_window" in item:
        flag = True
if flag is False:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'add_window'))
    print("add_window: added to phytonpath")

# ----------------------------------------------
# Import modules
# ----------------------------------------------
if "bpy" in locals():
    import imp

    imp.reload(window_panel)
    print("add window: Reloaded multifiles")
else:
    import window_panel
    print("add window: Imported multifiles")

# noinspection PyUnresolvedReferences
import bpy
# noinspection PyUnresolvedReferences
from bpy.props import *


# --------------------------------------------------------------
# Register all operators and panels
# --------------------------------------------------------------
# noinspection PyUnusedLocal
def menu_options(self, context):
    self.layout.operator(window_panel.RunAction.bl_idname, text="Window (editable)", icon="MOD_LATTICE")


def register():
    bpy.utils.register_class(window_panel.WindowMainPanel)
    bpy.utils.register_class(window_panel.RunAction)
    bpy.utils.register_class(window_panel.WindowEditPanel)
    bpy.types.INFO_MT_mesh_add.append(menu_options)


def unregister():
    bpy.utils.unregister_class(window_panel.WindowMainPanel)
    bpy.utils.unregister_class(window_panel.RunAction)
    bpy.utils.unregister_class(window_panel.WindowEditPanel)
    bpy.types.INFO_MT_mesh_add.remove(menu_options)

if __name__ == '__main__':
    register()
