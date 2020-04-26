'''
Copyright (C) 2018 YOUR NAME
YOUR@MAIL.com

Created by YOUR NAME

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
    "name": "Per Camera Resolution",
    "description": "Set render size per camera, and define paper size, resolution, and scale",
    "author": "Kevan Cress",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Properties",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Learnbgame",
    }


import bpy


# load and reload submodules
##################################

import importlib
from . import developer_utils
from bpy.utils import register_class, unregister_class

from .initialize_camera_properties import Initialize_Camera_Properties
from .panels import CAMERA_PX_Presets, AddPixelResPreset, CAMERA_PX_SCALE_Presets, AddPixelScalePreset, CAMERA_PAPER_Presets, AddPaperResPreset, CAMERA_PAPER_SCALE_Presets, AddPaperScalePreset, My_Panel
from .bind_marker import Bind_Marker

importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())


# register
##################################

classes = (CAMERA_PX_Presets,
    AddPixelResPreset,
    CAMERA_PX_SCALE_Presets,
    AddPixelScalePreset,
    CAMERA_PAPER_Presets,
    AddPaperResPreset,
    CAMERA_PAPER_SCALE_Presets,
    AddPaperScalePreset,
    My_Panel,
    Bind_Marker)

import traceback

def register():
    for cls in classes:
        register_class(cls)

    bpy.app.handlers.frame_change_pre.append(Initialize_Camera_Properties.update_manager)
    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))
    
def unregister():
    for cls in reversed(classes):
        unregister_class(cls)

    bpy.app.handlers.frame_change_pre.remove(Initialize_Camera_Properties.update_manager)
    print("Unregistered {}".format(bl_info["name"]))
