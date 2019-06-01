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
    "name"        : "Bricker",
    "author"      : "Christopher Gearhart <chris@bblanimation.com>",
    "version"     : (1, 6, 3),
    "blender"     : (2, 80, 0),
    "description" : "Turn any mesh into a 3D brick sculpture or simulation with the click of a button",
    "location"    : "View3D > Tools > Bricker",
    "warning"     : "",  # used for warning icon and text in addons panel
    "wiki_url"    : "https://www.blendermarket.com/products/bricker/",
    "tracker_url" : "https://github.com/bblanimation/bricker/issues",
    "category": "Learnbgame",
   }

developer_mode = 1  # NOTE: Set to 0 for release, 1 for exposed dictionary
# NOTE: Disable "LEGO Logo" for releases
# NOTE: Disable "Slopes" brick type for releases

# System imports
# NONE!

# Blender imports
import bpy
from bpy.props import *
from bpy.types import WindowManager, Object, Scene, Material
from bpy.utils import register_class, unregister_class

# Addon imports
from .ui import *
from .buttons import *
from .buttons.customize import *
from .lib import keymaps, preferences, classesToRegister
from .lib.Brick.legal_brick_sizes import getLegalBrickSizes
from .ui.timers import *
from .ui.cmlist_attrs import CreatedModelProperties
from . import addon_updater_ops

# store keymaps here to access after registration
addon_keymaps = []


def register():
    for cls in classesToRegister.classes:
        make_annotations(cls)
        bpy.utils.register_class(cls)

    bpy.props.bricker_module_name = __name__
    bpy.props.bricker_version = str(bl_info["version"])[1:-1].replace(", ", ".")

    bpy.props.bricker_initialized = b280()  # automatically initialized (uses timer) in b280
    bpy.props.bricker_updating_undo_states = False
    bpy.props.Bricker_developer_mode = developer_mode
    bpy.props.running_bricksculpt_tool = False
    bpy.props.bricker_last_selected = []
    bpy.props.bricker_trans_and_anim_data = []

    Object.protected = BoolProperty(name='protected', default=False)
    Object.isBrickifiedObject = BoolProperty(name='Is Brickified Object', default=False)
    Object.isBrick = BoolProperty(name='Is Brick', default=False)
    Object.cmlist_id = IntProperty(name='Custom Model ID', description="ID of cmlist entry to which this object refers", default=-1)
    if b280():
        Object.stored_parents = CollectionProperty(type=BRICKER_UL_collections_tuple)
    Material.num_averaged = IntProperty(name='Colors Averaged', description="Number of colors averaged together", default=0)

    WindowManager.Bricker_runningBlockingOperation = BoolProperty(default=False)

    Scene.Bricker_last_layers = StringProperty(default="")
    Scene.Bricker_last_cmlist_index = IntProperty(default=-2)
    Scene.Bricker_active_object_name = StringProperty(default="")
    Scene.Bricker_last_active_object_name = StringProperty(default="")

    Scene.Bricker_copy_from_id = IntProperty(default=-1)

    # define legal brick sizes (key:height, val:[width,depth])
    bpy.props.Bricker_legal_brick_sizes = getLegalBrickSizes()

    # Add attribute for Bricker Instructions addon
    Scene.isBrickerInstalled = BoolProperty(default=True)

    Scene.include_transparent = BoolProperty(
        name="Include Transparent",
        description="Include transparent ABS Plastic materials",
        default=False)
    Scene.include_uncommon = BoolProperty(
        name="Include Uncommon",
        description="Include uncommon ABS Plastic materials",
        default=False)

    # Scene.Bricker_snapping = BoolProperty(
    #     name="Bricker Snap",
    #     description="Snap to brick dimensions",
    #     default=False)
    # bpy.types.VIEW3D_HT_header.append(Bricker_snap_button)

    # other things (UI List)
    Scene.cmlist = CollectionProperty(type=CreatedModelProperties)
    Scene.cmlist_index = IntProperty(default=-1)

    # handle the keymaps
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon: # check this to avoid errors in background case
        km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
        keymaps.addKeymaps(km)
        addon_keymaps.append(km)

    # register app handlers
    bpy.app.handlers.frame_change_pre.append(handle_animation)
    if b280():
        bpy.app.handlers.load_post.append(register_bricker_timers)
    else:
        bpy.app.handlers.scene_update_pre.append(handle_selections)
    bpy.app.handlers.load_pre.append(clear_bfm_cache)
    bpy.app.handlers.load_post.append(handle_loading_to_light_cache)
    bpy.app.handlers.save_pre.append(handle_storing_to_deep_cache)
    bpy.app.handlers.save_pre.append(safe_link_parent)
    bpy.app.handlers.save_post.append(safe_unlink_parent)
    bpy.app.handlers.load_post.append(safe_unlink_parent)
    bpy.app.handlers.load_post.append(handle_upconversion)
    bpy.app.handlers.load_post.append(reset_undo_stack)

    # addon updater code and configurations
    addon_updater_ops.register(bl_info)


def unregister():
    # addon updater unregister
    addon_updater_ops.unregister()

    # unregister app handlers
    bpy.app.handlers.load_post.remove(reset_undo_stack)
    bpy.app.handlers.load_post.remove(handle_upconversion)
    bpy.app.handlers.load_post.remove(safe_unlink_parent)
    bpy.app.handlers.save_post.remove(safe_unlink_parent)
    bpy.app.handlers.save_pre.remove(safe_link_parent)
    bpy.app.handlers.save_pre.remove(handle_storing_to_deep_cache)
    bpy.app.handlers.load_post.remove(handle_loading_to_light_cache)
    bpy.app.handlers.load_pre.remove(clear_bfm_cache)
    if b280():
        if bpy.app.timers.is_registered(handle_selections):
            bpy.app.timers.unregister(handle_selections)
        if bpy.app.timers.is_registered(handle_undo_stack):
            bpy.app.timers.unregister(handle_undo_stack)
        bpy.app.handlers.load_post.remove(register_bricker_timers)
    else:
        bpy.app.handlers.scene_update_pre.remove(handle_selections)
    bpy.app.handlers.frame_change_pre.remove(handle_animation)

    # handle the keymaps
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()

    del Scene.cmlist_index
    del Scene.cmlist
    # bpy.types.VIEW3D_HT_header.remove(Bricker_snap_button)
    # del Scene.Bricker_snapping
    del Scene.include_uncommon
    del Scene.include_transparent
    del Scene.isBrickerInstalled
    del Scene.Bricker_copy_from_id
    del Scene.Bricker_last_active_object_name
    del Scene.Bricker_active_object_name
    del Scene.Bricker_last_cmlist_index
    del Scene.Bricker_last_layers
    del WindowManager.Bricker_runningBlockingOperation
    del Material.num_averaged
    if hasattr(Object, "stored_parents"):
        del Object.stored_parents
    del Object.cmlist_id
    del Object.isBrick
    del Object.isBrickifiedObject
    del Object.protected
    del bpy.props.bricker_trans_and_anim_data
    del bpy.props.bricker_last_selected
    del bpy.props.running_bricksculpt_tool
    del bpy.props.Bricker_developer_mode
    del bpy.props.bricker_updating_undo_states
    del bpy.props.bricker_initialized
    del bpy.props.bricker_version
    del bpy.props.bricker_module_name

    for cls in reversed(classesToRegister.classes):
        bpy.utils.unregister_class(cls)
