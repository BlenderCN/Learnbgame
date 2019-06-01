# Orox uses Animated or MoCap walkcycles to generate footstep driven walks
# Copyright (C) 2012  Bassam Kurdali
#
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
    "name": "Orox Parambulator",
    "author": "Bassam Kurdali",
    "version": (0, 6),
    "blender": (2, 7, 1),
    "location": "View3D",
    "description": "Footstep Driven Autowalker based on walkcycles",
    "warning": "",
    "wiki_url": "http://wiki.tube.freefac.org/wiki/Orox",
    "tracker_url": "",
    "category": "Learnbgame",
}

if "bpy" in locals():
    import imp
    imp.reload(ui_injest)
    imp.reload(ui_main)
else:
    from . import ui_injest
    from . import ui_main

import bpy


def register():
    ui_injest.register()
    ui_main.register()


def unregister():
    ui_main.unregister()
    ui_injest.unregister()

if __name__ == "__main__":
    register()
