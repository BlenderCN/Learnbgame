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

def swimregion(modifier, layout, context):
    split = layout.split()
    col = split.column()
    col.label("Detector Region:")
    col.prop(modifier, "region", text="")

    region_bo = modifier.region
    col = split.column()
    col.enabled = region_bo is not None
    bounds_src = region_bo if region_bo is not None else modifier.id_data
    col.label("Detector Bounds:")
    col.prop(bounds_src.plasma_modifiers.collision, "bounds", text="")

    split = layout.split()
    col = split.column(align=True)
    col.label("Buoyancy:")
    col.prop(modifier, "down_buoyancy", text="Down")
    col.prop(modifier, "up_buoyancy", text="Up")

    col = split.column()
    col.label("Current:")
    col.prop(modifier, "current_type", text="")
    if modifier.current_type == "CIRCULAR":
        col.prop(modifier, "rotation")

    if modifier.current_type != "NONE":
        split = layout.split()
        col = split.column(align=True)
        col.label("Distance:")
        col.prop(modifier, "near_distance", text="Near")
        col.prop(modifier, "far_distance", text="Far")

        col = split.column(align=True)
        col.label("Velocity:")
        col.prop(modifier, "near_velocity", text="Near")
        col.prop(modifier, "far_velocity", text="Far")

        layout.prop(modifier, "current")

def water_basic(modifier, layout, context):
    layout.prop(modifier, "wind_object")
    layout.prop(modifier, "envmap")

    row = layout.row()
    row.prop(modifier, "wind_speed")
    row.prop(modifier, "envmap_radius")
    layout.separator()

    split = layout.split()
    col = split.column()
    col.prop(modifier, "specular_tint")
    col.prop(modifier, "specular_alpha", text="Alpha")

    col.label("Specular:")
    col.prop(modifier, "specular_start", text="Start")
    col.prop(modifier, "specular_end", text="End")

    col.label("Misc:")
    col.prop(modifier, "noise")
    col.prop(modifier, "ripple_scale")

    col = split.column()
    col.label("Opacity:")
    col.prop(modifier, "zero_opacity", text="Start")
    col.prop(modifier, "depth_opacity", text="End")

    col.label("Reflection:")
    col.prop(modifier, "zero_reflection", text="Start")
    col.prop(modifier, "depth_reflection", text="End")

    col.label("Wave:")
    col.prop(modifier, "zero_wave", text="Start")
    col.prop(modifier, "depth_wave", text="End")

def _wavestate(modifier, layout, context):
    split = layout.split()
    col = split.column()
    col.label("Size:")
    col.prop(modifier, "min_length")
    col.prop(modifier, "max_length")
    col.prop(modifier, "amplitude")

    col = split.column()
    col.label("Behavior:")
    col.prop(modifier, "chop")
    col.prop(modifier, "angle_dev")

water_geostate = _wavestate
water_texstate = _wavestate

class ShoreListUI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index=0, flt_flag=0):
        layout.prop(item, "display_name", emboss=False, text="", icon="MOD_WAVE")


def water_shore(modifier, layout, context):
    ui_list.draw_modifier_list(layout, "ShoreListUI", modifier, "shores",
                               "active_shore_index", name_prefix="Shore",
                               name_prop="display_name", rows=2, maxrows=3)

    # Display the active shore
    if modifier.shores:
        shore = modifier.shores[modifier.active_shore_index]
        layout.prop(shore, "shore_object", icon="MESH_DATA")

    split = layout.split()
    col = split.column()
    col.label("Basic:")
    col.prop(modifier, "shore_tint")
    col.prop(modifier, "shore_opacity")
    col.prop(modifier, "wispiness")

    col = split.column()
    col.label("Advanced:")
    col.prop(modifier, "period")
    col.prop(modifier, "finger")
    col.prop(modifier, "edge_opacity")
    col.prop(modifier, "edge_radius")
