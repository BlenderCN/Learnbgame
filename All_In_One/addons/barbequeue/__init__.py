# BEGIN GPL LICENSE BLOCK #####
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
# END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Barbequeue",
    "description": "A simple render queing system.",
    "author": "Nicolas Lemery Nantel",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "",
    "warning": "",
    "wiki_url": "", # Github Wiki
    "tracker_url": "", # Github issues
    "category": "Learnbgame",
}

if "bpy" in locals():
    import imp
    imp.reload(ui)
else:
    from . import ui

import bpy

def register():
    bpy.utils.register_module(__name__)
    # bpy.types.Scene.bbqueue = bpy.props.PointerProperty(type=BBQueueSettings)

def unregister():
    bpy.utils.unregister_module(__name__)
    # del bpy.types.Scene.bbqueue

if __name__ == '__main__':
    register()
