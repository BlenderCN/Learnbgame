'''
Copyright (C) 2017 MATTHIAS PATSCHEIDER
patscheider.matthias@gmail.com

Created by Matthias Patscheider

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
#The addon is currently able to
#       export ALL images to a csv. Procedural and images with no path are simply shown blank
#       it shows the current image resolution. this value can not be changed
#       create the material tree for all materials (DESTRUCTIVE)




# TODO: Make a list of materials that are supposed to be effected by the texture reload and creation for the shader tree
# TODO: Easily change the prefixes for the textures



bl_info = {
    "name": "Image Utilities",
    "description": "Export and import texture paths from csv files",
    "author": "Matthias Patscheider",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Learnbgame"
}


import bpy
from bpy.types import WindowManager, Scene

# load and reload submodules
##################################

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())



# register
##################################
import traceback

def register():

    WindowManager.csv_dir = bpy.props.StringProperty(
            name="Export Path",
            subtype='DIR_PATH',
            default=""
            )

    WindowManager.texture_dir = bpy.props.StringProperty(
            name="Texture Directory",
            subtype='DIR_PATH',
            default=""
            )

    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()

    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

def unregister():
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()

    print("Unregistered {}".format(bl_info["name"]))
