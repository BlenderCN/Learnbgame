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
    "name": "Create html documentation",
    "author": "Antonio Vazquez (antonioya)",
    "location": "File > Import-Export / Tool Panel",
    "version": (1, 1),
    "blender": (2, 7, 3),
    "description": "Create html documentation for blend files, including storyboards, images and linked assets.",
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
    if "doc_scenes" in item:
        flag = True
if flag is False:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'doc_scenes'))
    print("doc_scenes: added to phytonpath")

# ----------------------------------------------
# Import modules
# ----------------------------------------------
if "bpy" in locals():
    import imp

    imp.reload(html_maker)
    imp.reload(main_panel)
    print("doc_scenes: Reloaded multifiles")
else:
    import html_maker
    import main_panel

    print("doc_scenes: Imported multifiles")

# noinspection PyUnresolvedReferences
import bpy

# noinspection PyUnresolvedReferences
from bpy.props import *


# ----------------------------------------------------------
# Registration
# ----------------------------------------------------------
# noinspection PyUnusedLocal
def menu_func_export(self, context):
    self.layout.operator(main_panel.ExportHtmlDoc.bl_idname, text="Create scene documentation (.htm)", icon='URL')


def register():
    bpy.utils.register_class(main_panel.RunActionOn)
    bpy.utils.register_class(main_panel.RunActionOff)
    bpy.utils.register_class(main_panel.MainPanel)
    bpy.utils.register_class(main_panel.ExportHtmlDoc)

    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(main_panel.RunActionOn)
    bpy.utils.unregister_class(main_panel.RunActionOff)
    bpy.utils.unregister_class(main_panel.MainPanel)
    bpy.utils.unregister_class(main_panel.ExportHtmlDoc)

    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
