"""
Copyright (C) 2017 Bricks Brought to Life
http://bblanimation.com/
chris@bblanimation.com

Created by Christopher Gearhart
"""

# Addon imports
from .preferences import *
from .reportError import *
from ..ui import *
from ..buttons import *
from .. import addon_updater_ops


classes = [
    # assemblme/buttons
    createBuildAnimation.ASSEMBLME_OT_create_build_animation,
    infoRestorePreset.ASSEMBLME_OT_info_restore_preset,
    newGroupFromSelection.ASSEMBLME_OT_new_group_from_selection,
    presets.ASSEMBLME_OT_anim_presets,
    refreshBuildAnimationLength.ASSEMBLME_OT_refresh_anim_length,
    startOver.ASSEMBLME_OT_start_over,
    visualizer.ASSEMBLME_OT_visualizer,
    # assemblme/ui/aglist_attrs
    ASSEMBLME_UL_animated_collections,
    # assemblme/ui/aglist_actions
    AGLIST_OT_list_action,
    AGLIST_OT_copy_settings_to_others,
    AGLIST_OT_copy_settings,
    AGLIST_OT_paste_settings,
    AGLIST_OT_set_to_active,
    AGLIST_OT_print_all_items,
    AGLIST_OT_clear_all_items,
    ASSEMBLME_UL_items,
    # assemblme/ui
    ASSEMBLME_MT_copy_paste_menu,
    ASSEMBLME_PT_animations,
    ASSEMBLME_PT_actions,
    ASSEMBLME_PT_settings,
    ASSEMBLME_PT_interface,
    ASSEMBLME_PT_preset_manager,
    # assemblme/lib
    ASSEMBLME_PT_preferences,
    SCENE_OT_report_error,
    SCENE_OT_close_report_error,
]
