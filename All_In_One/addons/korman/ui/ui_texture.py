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

from . import ui_list

class TextureButtonsPanel:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "texture"

    @classmethod
    def poll(cls, context):
        return context.texture and context.scene.render.engine == "PLASMA_GAME"


class PlasmaEnvMapPanel(TextureButtonsPanel, bpy.types.Panel):
    bl_label = "Plasma Environment Map"

    @classmethod
    def poll(cls, context):
        if super().poll(context):
            return context.texture.type == "ENVIRONMENT_MAP"
        return False

    def draw(self, context):
        texture = context.texture
        layer_props, envmap = texture.plasma_layer, texture.environment_map
        layout = self.layout

        if envmap.source in {"ANIMATED", "STATIC"}:
            layout.prop(layer_props, "envmap_color")
            layout.separator()

            layout.label("Visibility Sets:")
            ui_list.draw_list(layout, "VisRegionListUI", "texture", layer_props,
                              "vis_regions", "active_region_index", rows=2, maxrows=3)
            rgns = layer_props.vis_regions
            if layer_props.vis_regions:
                layout.prop(rgns[layer_props.active_region_index], "control_region")
        elif envmap.source == "IMAGE_FILE":
            op = layout.operator("image.plasma_build_cube_map",
                                 text="Build Cubemap from Cube Faces",
                                 icon="MATCUBE")
            op.texture_name = context.texture.name


class PlasmaLayerPanel(TextureButtonsPanel, bpy.types.Panel):
    bl_label = "Plasma Layer Options"

    def draw(self, context):
        texture, slot = context.texture, getattr(context, "texture_slot", None)
        use_stencil = slot.use_stencil if slot is not None else False
        layer_props = texture.plasma_layer
        layout = self.layout

        split = layout.split()
        col = split.column()
        col.label("Animation:")
        col.active = self._has_animation_data(context) and not use_stencil
        col.prop(layer_props, "anim_auto_start")
        col.prop(layer_props, "anim_loop")
        col.separator()
        col.label("SDL Animation:")
        col.prop(layer_props, "anim_sdl_var", text="")

        col = split.column()
        col.label("Miscellaneous:")
        col.active = not use_stencil
        col.prop(layer_props, "opacity", text="Opacity")
        col.separator()

        col = col.column()
        col.enabled = True
        col.label("Z Depth:")
        col.prop(layer_props, "alpha_halo")
        col.prop(layer_props, "skip_depth_write")
        col.prop(layer_props, "skip_depth_test")
        col.prop(layer_props, "z_bias")

        split = layout.split()
        col = split.column()
        col.active = texture.use_mipmap
        col.prop(layer_props, "is_detail_map", text="Detail Blending")
        col = col.column(align=True)
        col.active = texture.use_mipmap and layer_props.is_detail_map
        col.prop(layer_props, "detail_fade_start")
        col.prop(layer_props, "detail_fade_stop")
        col = split.column(align=True)
        col.active = texture.use_mipmap and layer_props.is_detail_map
        col.label(text="")
        col.prop(layer_props, "detail_opacity_start")
        col.prop(layer_props, "detail_opacity_stop")

    def _has_animation_data(self, context):
        tex = getattr(context, "texture", None)
        if tex is not None:
            if tex.animation_data is not None:
                return True

        mat = getattr(context, "material", None)
        if mat is not None:
            if mat.animation_data is not None:
                return True

        return False
