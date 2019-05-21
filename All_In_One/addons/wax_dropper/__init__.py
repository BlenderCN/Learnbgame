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
    "name"        : "Wax Dropper",
    "author"      : "Christopher Gearhart <chris@bblanimation.com>",
    "version"     : (1, 0, 0),
    "blender"     : (2, 79, 0),
    "description" : "",
    "location"    : "View3D > Tools > Wax Dropper",
    "warning"     : "",  # used for warning icon and text in addons panel
    "wiki_url"    : "",
    "tracker_url" : "",
    "category"    : "Object"}

# System imports
# NONE!

# Blender imports
import bpy
from bpy.types import Scene

# Addon imports
from .operators import *
from .ui import *
from .lib.classesToRegister import classes
from . import addon_updater_ops

def register():
    # register classes
    for cls in classes:
        bpy.utils.register_class(cls)

    # # register app handlers
    # bpy.app.handlers.load_post.append(handle_something)

    # addon updater code and configurations
    addon_updater_ops.register(bl_info)

def unregister():
    # addon updater unregister
    addon_updater_ops.unregister()

    # # unregister app handlers
    # bpy.app.handlers.load_post.remove(handle_something)

    # unregister classes
    for cls in classes:
        bpy.utils.unregister_class(cls)
