#    This file is part of Korman.
#
#    Korman is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Korman is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Korman.  If not, see <http://www.gnu.org/licenses/>.

import bpy

from .. import ui_list

def _check_for_anim(layout, modifier):
    try:
        action = modifier.blender_action
    except:
        layout.label("Object has no animation data", icon="ERROR")
        return None
    else:
        return action if action is not None else False

def animation(modifier, layout, context):
    action = _check_for_anim(layout, modifier)
    if action is None:
        return

    split = layout.split()
    col = split.column()
    col.prop(modifier, "auto_start")
    col = split.column()
    col.prop(modifier, "loop")

    if action:
        layout.prop_search(modifier, "initial_marker", action, "pose_markers", icon="PMARKER")
        col = layout.column()
        col.enabled = modifier.loop
        col.prop_search(modifier, "loop_start", action, "pose_markers", icon="PMARKER")
        col.prop_search(modifier, "loop_end", action, "pose_markers", icon="PMARKER")

def animation_filter(modifier, layout, context):
    split = layout.split()

    col = split.column()
    col.label("Translation:")
    col.prop(modifier, "no_transX", text="Filter X")
    col.prop(modifier, "no_transY", text="Filter Y")
    col.prop(modifier, "no_transZ", text="Filter Z")

    col = split.column()
    col.label("Rotation:")
    col.prop(modifier, "no_rotation", text="Filter Rotation")

class GroupListUI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index=0, flt_flag=0):
        label = item.child_anim.name if item.child_anim is not None else "[No Child Specified]"
        icon = "ACTION" if item.child_anim is not None else "ERROR"
        layout.label(text=label, icon=icon)


def animation_group(modifier, layout, context):
    action = _check_for_anim(layout, modifier)
    if action is None:
        return

    ui_list.draw_modifier_list(layout, "GroupListUI", modifier, "children",
                               "active_child_index", rows=3, maxrows=4)
    if modifier.children:
        layout.prop(modifier.children[modifier.active_child_index], "child_anim", icon="ACTION")


class LoopListUI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index=0, flt_flag=0):
        layout.prop(item, "loop_name", emboss=False, text="", icon="PMARKER_ACT")


def animation_loop(modifier, layout, context):
    action = _check_for_anim(layout, modifier)
    if action is False:
        layout.label("Object must be animated, not ObData", icon="ERROR")
        return
    elif action is None:
        return

    ui_list.draw_modifier_list(layout, "LoopListUI", modifier, "loops",
                               "active_loop_index", name_prefix="Loop",
                               name_prop="loop_name", rows=2, maxrows=3)
    # Modify the loop points
    if modifier.loops:
        loop = modifier.loops[modifier.active_loop_index]
        layout.prop_search(loop, "loop_start", action, "pose_markers", icon="PMARKER")
        layout.prop_search(loop, "loop_end", action, "pose_markers", icon="PMARKER")
