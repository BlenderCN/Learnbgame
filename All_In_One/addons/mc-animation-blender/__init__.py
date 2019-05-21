'''
Copyright (C) 2019 Sam54123
thesam54123@gmail.com

Created by Sam54123

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Minecraft Animation Addon",
    "description": "",
    "author": "Sam54123",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Learnbgame"
}


import importlib

if "developer_utils" in locals():
	importlib.reload(developer_utils)
else:
	from . import developer_utils

import bpy


def register():
	bpy.utils.register_module(__name__)
	developer_utils.register(bl_info)


def unregister():
	bpy.utils.unregister_module(__name__)
	developer_utils.unregister(bl_info)


if __name__ == "__main__":
	register()
