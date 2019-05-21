# Copyright (C) 2019 Christopher Gearhart
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
    "name"        : "AssemblMe",
    "author"      : "Christopher Gearhart <chris@bblanimation.com>",
    "version"     : (1, 2, 2),
    "blender"     : (2, 80, 0),
    "description" : "Iterative object assembly animations made simple",
    "location"    : "View3D > Tools > AssemblMe",
    "wiki_url"    : "https://www.blendermarket.com/products/assemblme",
    "tracker_url" : "https://github.com/bblanimation/assemblme/issues",
    "category"    : "Animation"}

# System imports
import os

# Blender imports
import bpy
from bpy.props import *
from bpy.types import Scene
from bpy.utils import register_class, unregister_class

# Addon import
from .ui import *
from .functions import getPresetTuples
from .functions.common import *
from .buttons.presets import *
from .lib.classesToRegister import classes
from . import addon_updater_ops


def register():
    for cls in classes:
        make_annotations(cls)
        register_class(cls)

    bpy.props.assemblme_module_name = __name__
    bpy.props.assemblme_version = str(bl_info["version"])[1:-1]

    Scene.assemblme_copy_from_id = IntProperty(default=-1)

    # items used by selection app handler
    Scene.assemblMe_runningOperation = BoolProperty(default=False)
    Scene.assemblMe_last_layers = StringProperty(default="")
    Scene.assemblMe_last_aglist_index = IntProperty(default=-2)
    Scene.assemblMe_active_object_name = StringProperty(default="")
    Scene.assemblMe_last_active_object_name = StringProperty(default="")

    Scene.newPresetName = StringProperty(
        name="Name of New Preset",
        description="Full name of new custom preset",
        default="")
    Scene.assemblme_default_presets = ["Explode", "Rain", "Standard Build", "Step-by-Step"]
    presetNames = getPresetTuples(transferDefaults=not bpy.app.background)
    Scene.animPreset = EnumProperty(
        name="Presets",
        description="Stored AssemblMe presets",
        items=presetNames,
        update=updateAnimPreset,
        default="None")
    Scene.animPresetToDelete = EnumProperty(
        name="Preset to Delete",
        description="Another list of stored AssemblMe presets",
        items=Scene.animPreset[1]['items'],
        default="None")

    Scene.visualizerScale = FloatProperty(
        name="Scale",
        description="Scale of layer orientation visualizer",
        precision=1,
        min=0.1, max=16,
        default=10)
    Scene.visualizerRes = FloatProperty(
        name="Resolution",
        description="Resolution of layer orientation visualizer",
        precision=2,
        min=0.05, max=1,
        default=0.25)

    # list properties
    Scene.aglist = CollectionProperty(type=ASSEMBLME_UL_animated_collections)
    Scene.aglist_index = IntProperty(default=-1)

    # Session properties
    bpy.props.z_upper_bound = None
    bpy.props.z_lower_bound = None
    bpy.props.objMinLoc = 0
    bpy.props.objMaxLoc = 0

    # register app handlers
    if b280():
        bpy.app.handlers.load_post.append(register_assemblme_timers)
        bpy.app.timers.register(handle_selections)
    else:
        bpy.app.handlers.scene_update_pre.append(handle_selections)
    bpy.app.handlers.load_post.append(convert_velocity_value)
    bpy.app.handlers.load_post.append(handle_upconversion)

    # addon updater code and configurations
    addon_updater_ops.register(bl_info)


def unregister():
    # addon updater unregister
    addon_updater_ops.unregister()

    # unregister app handlers
    bpy.app.handlers.load_post.remove(handle_upconversion)
    bpy.app.handlers.load_post.remove(convert_velocity_value)
    if b280():
        if bpy.app.timers.is_registered(handle_selections):
            bpy.app.timers.unregister(handle_selections)
        bpy.app.handlers.load_post.remove(register_assemblme_timers)
    else:
        bpy.app.handlers.scene_update_pre.remove(handle_selections)

    del bpy.props.z_upper_bound
    del bpy.props.z_lower_bound
    del bpy.props.objMinLoc
    del bpy.props.objMaxLoc

    del Scene.aglist_index
    del Scene.aglist

    del Scene.visualizerRes
    del Scene.visualizerScale

    del Scene.animPresetToDelete
    del Scene.animPreset
    del Scene.newPresetName

    del Scene.assemblMe_last_active_object_name
    del Scene.assemblMe_active_object_name
    del Scene.assemblMe_last_aglist_index
    del Scene.assemblMe_last_layers
    del Scene.assemblMe_runningOperation

    del Scene.assemblme_copy_from_id

    del bpy.props.assemblme_version
    del bpy.props.assemblme_module_name

    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()
