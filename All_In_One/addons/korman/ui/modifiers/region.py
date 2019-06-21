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
from .. import ui_camera

def camera_rgn(modifier, layout, context):
    layout.prop(modifier, "camera_type")
    if modifier.camera_type == "manual":
        layout.prop(modifier, "camera_object", icon="CAMERA_DATA")
    else:
        cam_type = modifier.camera_type[5:]
        cam_props = modifier.auto_camera

        def _draw_props(layout, cb):
            for i in cb:
                layout.separator()
                i(layout, cam_type, cam_props)

        _draw_props(layout, (ui_camera.draw_camera_mode_props,
                             ui_camera.draw_camera_poa_props,
                             ui_camera.draw_camera_pos_props,
                             ui_camera.draw_camera_manipulation_props))

def footstep(modifier, layout, context):
    layout.prop(modifier, "bounds")
    layout.prop(modifier, "surface")

def paniclink(modifier, layout, context):
    phys_mod = context.object.plasma_modifiers.collision
    layout.prop(phys_mod, "bounds")
    layout.prop(modifier, "play_anim")

def softvolume(modifier, layout, context):
    row = layout.row()
    row.prop(modifier, "use_nodes", text="", icon="NODETREE")
    if modifier.use_nodes:
        row.prop(modifier, "node_tree")
    else:
        row.label("Simple Soft Volume")

        split = layout.split()
        col = split.column()
        col.prop(modifier, "inside_strength")
        col.prop(modifier, "outside_strength")
        col = split.column()
        col.prop(modifier, "invert")
        col.prop(modifier, "soft_distance")

def subworld_rgn(modifier, layout, context):
    layout.prop(modifier, "subworld")
    collision_mod = modifier.id_data.plasma_modifiers.collision
    layout.prop(collision_mod, "bounds")
    layout.prop(modifier, "transition")
