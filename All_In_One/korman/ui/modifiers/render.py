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
from ...exporter.mesh import _VERTEX_COLOR_LAYERS

def fademod(modifier, layout, context):
    layout.prop(modifier, "fader_type")

    if modifier.fader_type == "DistOpacity":
        col = layout.column(align=True)
        col.prop(modifier, "near_trans")
        col.prop(modifier, "near_opaq")
        col.prop(modifier, "far_opaq")
        col.prop(modifier, "far_trans")
    elif modifier.fader_type == "FadeOpacity":
        col = layout.column(align=True)
        col.prop(modifier, "fade_in_time")
        col.prop(modifier, "fade_out_time")
        col.separator()
        col.prop(modifier, "bounds_center")
    elif modifier.fader_type == "SimpleDist":
        col = layout.column(align=True)
        col.prop(modifier, "far_opaq")
        col.prop(modifier, "far_trans")

    if not (modifier.near_trans <= modifier.near_opaq <= modifier.far_opaq <= modifier.far_trans):
        # Warn the user that the values are not recommended.
        layout.label("Distance values must be equal or increasing!", icon="ERROR")

def followmod(modifier, layout, context):
    layout.row().prop(modifier, "follow_mode", expand=True)
    layout.prop(modifier, "leader_type")
    if modifier.leader_type == "kFollowObject":
        layout.prop(modifier, "leader", icon="OUTLINER_OB_MESH")

def lighting(modifier, layout, context):
    split = layout.split()
    col = split.column()
    col.prop(modifier, "force_rt_lights")
    col = split.column()
    col.active = modifier.allow_preshade
    col.prop(modifier, "force_preshade")
    layout.separator()

    lightmap = modifier.id_data.plasma_modifiers.lightmap
    have_static_lights = lightmap.enabled or modifier.preshade
    def yes_no(val):
        return "Yes" if val else "No"

    col = layout.column(align=True)
    col.label("Plasma Lighting Summary:")
    if modifier.rt_lights and have_static_lights:
        col.label(" You have unleashed Satan!", icon="GHOST_ENABLED")
    else:
        col.label(" Satan remains ensconced deep in the abyss...", icon="GHOST_ENABLED")
    col.label("Animated lights will be cast at runtime.", icon="LAYER_USED")
    col.label("Projection lights will be cast at runtime.", icon="LAYER_USED")
    col.label("Specular lights will be cast to specular materials at runtime.", icon="LAYER_USED")
    col.label("Other Plasma lights {} be cast at runtime.".format("will" if modifier.rt_lights else "will NOT"),
              icon="LAYER_USED")

    map_type = "a lightmap" if lightmap.enabled and lightmap.bake_type == "lightmap" else "vertex colors"
    if lightmap.enabled and lightmap.lights:
            col.label("All '{}' lights will be baked to {}".format(lightmap.lights.name, map_type),
                      icon="LAYER_USED")
    elif have_static_lights:
        light_type = "Blender-only" if modifier.rt_lights else "unanimated"
        col.label("Other {} lights will be baked to {}.".format(light_type, map_type), icon="LAYER_USED")
    else:
        col.label("No static lights will be baked.", icon="LAYER_USED")

def lightmap(modifier, layout, context):
    pl_scene = context.scene.plasma_scene
    is_texture = modifier.bake_type == "lightmap"

    layout.prop(modifier, "bake_type")
    if modifier.bake_type == "vcol":
        col_layer = next((i for i in modifier.id_data.data.vertex_colors if i.name.lower() in _VERTEX_COLOR_LAYERS), None)
        if col_layer is not None:
            layout.label("Mesh color layer '{}' will override this lighting.".format(col_layer.name), icon="ERROR")

    col = layout.column()
    col.active = is_texture
    col.prop(modifier, "quality")
    layout.prop_search(modifier, "bake_pass_name", pl_scene, "bake_passes", icon="RENDERLAYERS")
    layout.prop(modifier, "lights")
    col = layout.column()
    col.active = is_texture
    col.prop_search(modifier, "uv_map", context.active_object.data, "uv_textures")

    # Lightmaps can only be applied to objects with opaque materials.
    if is_texture and any((i.use_transparency for i in modifier.id_data.data.materials if i is not None)):
        layout.label("Transparent objects cannot be lightmapped.", icon="ERROR")
    else:
        col = layout.column()
        col.active = is_texture
        operator = col.operator("object.plasma_lightmap_preview", "Preview Lightmap", icon="RENDER_STILL")

        # Kind of clever stuff to show the user a preview...
        # We can't show images, so we make a hidden ImageTexture called LIGHTMAPGEN_PREVIEW. We check
        # the backing image name to see if it's for this lightmap. If so, you have a preview. If not,
        # well... It was nice knowing you!
        tex = bpy.data.textures.get("LIGHTMAPGEN_PREVIEW")
        if tex is not None and tex.image is not None:
            im_name = "{}_LIGHTMAPGEN.png".format(context.active_object.name)
            if tex.image.name == im_name:
                layout.template_preview(tex, show_buttons=False)

def rtshadow(modifier, layout, context):
    split = layout.split()
    col = split.column()
    col.prop(modifier, "blur")
    col.prop(modifier, "boost")
    col.prop(modifier, "falloff")

    col = split.column()
    col.prop(modifier, "limit_resolution")
    col.prop(modifier, "self_shadow")

def viewfacemod(modifier, layout, context):
    layout.prop(modifier, "preset_options")

    if modifier.preset_options == "Custom":
        layout.row().prop(modifier, "follow_mode")
        if modifier.follow_mode == "kFaceObj":
            layout.prop(modifier, "target", icon="OUTLINER_OB_MESH")
            layout.separator()

        layout.prop(modifier, "pivot_on_y")
        layout.separator()

        split = layout.split()
        col = split.column()
        col.prop(modifier, "offset")
        row = col.row()
        row.enabled = modifier.offset
        row.prop(modifier, "offset_local")

        col = split.column()
        col.enabled = modifier.offset
        col.prop(modifier, "offset_coord")

class VisRegionListUI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index=0, flt_flag=0):
        if item.control_region is None:
            layout.label("[No Object Specified]", icon="ERROR")
        else:
            layout.label(item.control_region.name, icon="OBJECT_DATA")
        layout.prop(item, "enabled", text="")


def visibility(modifier, layout, context):
    ui_list.draw_modifier_list(layout, "VisRegionListUI", modifier, "regions",
                               "active_region_index", rows=2, maxrows=3)

    if modifier.regions:
        layout.prop(modifier.regions[modifier.active_region_index], "control_region")

def visregion(modifier, layout, context):
    layout.prop(modifier, "mode")

    # Only allow SoftVolume spec if this is not an FX and this object is not an SV itself
    sv = modifier.id_data.plasma_modifiers.softvolume
    if modifier.mode != "fx" and not sv.enabled:
        layout.prop(modifier, "soft_region")

    # Other settings
    layout.prop(modifier, "replace_normal")
