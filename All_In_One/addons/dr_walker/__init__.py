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
# Copyright 2015 Bassam Kurdali 

bl_info = {
    "name": "Dr Walker",
    "author": "Bassam Kurdali",
    "version": (0, 0),
    "blender": (2, 73, 0),
    "location": "NLA Editor",
    "description": "Transform path animation into walks",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame"
}    

"""
Replaces old 'stride' based walkcycles in 2.4x, but without the need for 
a stride bone. Walkcycle actions can be 'in place' or 'forward' actions,
however, rigs must be tagged before using.
"""

if "bpy" in locals():
    import importlib
    importlib.reload(tag)
    importlib.reload(path)
    importlib.reload(strider)

else:
    from . import tag
    from . import path
    from . import strider

import bpy


def register():
    tag.register()
    strider.register()


def unregister():
    tag.unregister()
    strider.unregister()

if __name__ == '__main__':
    register()

