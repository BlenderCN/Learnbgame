#ManuelbastioniLAB - Copyright (C) 2015-2018 Manuel Bastioni
#Official site: www.manuelbastioni.com
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

import deeva.pictures_renderer
import deeva.generation_gui

bl_info = {
    "name": "Deeva",
    "author": "Fabrizio Nunnari",
    "version": (1, 0, 0),
    "blender": (2, 7, 9),
    "location": "View3D > Tools > DeEvA",
    "description": "The DeEvA toolkit for the creation of avatars from personality traits.",
    "warning": "",
    'wiki_url': "https://github.com/fnunnari/deeva",
    "category": "Learnbgame"
}


DEEVA_VERSION = ".".join([str(n) for n in bl_info["version"]])
DEEVA_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def register():
    # bpy.utils.register_module(__name__)
    pictures_renderer.register()
    generation_gui.register()


def unregister():
    # bpy.utils.unregister_module(__name__)
    generation_gui.unregister()
    pictures_renderer.unregister()


if __name__ == "__main__":
    register()
