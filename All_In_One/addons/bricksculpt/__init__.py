# Copyright (C) 2018 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name"        : "BrickSculpt (Bricker Addon)",
    "author"      : "Christopher Gearhart <chris@bblanimation.com>",
    "version"     : (1, 0, 0),
    "blender"     : (2, 80, 0),
    "description" : "Brick Sculpting Tools for Bricker",
    "location"    : "View3D > Tools > Bricker > Customize Model",
    "warning"     : "",  # used for warning icon and text in addons panel
    "wiki_url"    : "https://www.blendermarket.com/products/bricksculpt/",
    "tracker_url" : "https://github.com/bblanimation/bricksculpt/issues",
    "category": "Learnbgame",
   }

# System imports
# NONE!

# Blender imports
import bpy
from bpy.props import *

# Addon imports
from . import addon_updater_ops
from .lib.preferences import *
from .functions.common import *

classes = [
    BRICKSCULPT_AP_preferences,
]


def register():
    # register classes
    for cls in classes:
        make_annotations(cls)
        bpy.utils.register_class(cls)

    bpy.props.bricksculpt_module_name = __name__
    bpy.props.bricksculpt_version = str(bl_info["version"])[1:-1].replace(", ", ".")

    # addon updater code and configurations
    addon_updater_ops.register(bl_info)


def unregister():
    # addon updater unregister
    addon_updater_ops.unregister()

    del bpy.props.bricksculpt_module_name
    del bpy.props.bricksculpt_version

    # unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
