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
    "name": "Propagate Render Settings",
    "author": "Bastien Montagne",
    "version": (0, 0, 1),
    "blender": (2, 5, 6),
    "api": 34317,
    "location": "Render buttons (Properties window)",
    "description": "Allows to copy some performance-related render settings from current scene to all others.",
    "warning": "beta",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
                "Scripts/Render/Propagate Render Settings",
    "tracker_url": "http://projects.blender.org/tracker/index.php?"\
                   "func=detail&aid=25832",
    "category": "Learnbgame"
}


if "bpy" in locals():
    import imp
    imp.reload(operator)
    imp.reload(panel)

else:
    import bpy
    from propagate_render_settings import operator
    from propagate_render_settings import panel

def register():
    pass

def unregister():
    pass

if __name__ == "__main__":
    register()

