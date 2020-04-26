# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Messy Things project organizer for Blender.
#  Copyright (C) 2017-2019  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


from bpy.types import Operator


class SCENE_OT_messythings_normalize(Operator):
    bl_label = "Messy Things Normalize Object Display"
    bl_description = (
        "Disable Double Sided and match render to viewport subdivision level "
        "in Subdivision modifier for all objects in the scene"
    )
    bl_idname = "scene.messythings_normalize"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for ob in context.scene.objects:
            ob.hide_viewport = False

            if ob.type == "MESH":
                ob.data.show_double_sided = False

            if ob.modifiers:
                for mod in ob.modifiers:
                    if mod.type == "SUBSURF":
                        mod.render_levels = mod.levels

        self.report({"INFO"}, "Objects display normalized")

        return {"FINISHED"}


class SCENE_OT_messythings_profile_render(Operator):
    bl_label = "Messy Things Apply Render Profile"
    bl_description = (
        "Resolution: 1080 x 1080\n"
        "Output format: PNG RGBA\n"
        "Device: GPU\n"
        "Samples: 100 (preview 10 samples)\n"
        "Tile order: Top to Bottom\n"
        "View transform: Filmic (Look: None)"
    )
    bl_idname = "scene.messythings_profile_render"
    bl_options = {"REGISTER", "UNDO"}

    # TODO props dialog

    # resolution_x = IntProperty(default=1080, options={"SKIP_SAVE"})
    # resolution_y = IntProperty(default=1080, options={"SKIP_SAVE"})
    # resolution_percentage = IntProperty(default=100, options={"SKIP_SAVE"})
    # file_format = StringProperty(default="PNG", options={"SKIP_SAVE"})
    # color_mode = StringProperty(default="RGBA", options={"SKIP_SAVE"})
    # compression = IntProperty(default=100, options={"SKIP_SAVE"})
    # display_mode = StringProperty(default="SCREEN", options={"SKIP_SAVE"})

    # film_transparent = BoolProperty(default=True, options={"SKIP_SAVE"})
    # device = StringProperty(default="GPU", options={"SKIP_SAVE"})
    # pixel_filter_type = StringProperty(default="BLACKMAN_HARRIS", options={"SKIP_SAVE"})
    # progressive = StringProperty(default="PATH", options={"SKIP_SAVE"})
    # use_square_samples = BoolProperty(default=False, options={"SKIP_SAVE"})
    # samples = IntProperty(default=100, options={"SKIP_SAVE"})
    # preview_samples = IntProperty(default=10, options={"SKIP_SAVE"})
    # sample_clamp_indirect = FloatProperty(default=10.0, options={"SKIP_SAVE"})
    # light_sampling_threshold = FloatProperty(default=0.01, options={"SKIP_SAVE"})
    # tile_order = StringProperty(default="TOP_TO_BOTTOM", options={"SKIP_SAVE"})

    # view_transform = StringProperty(default="Filmic", options={"SKIP_SAVE"})
    # look = StringProperty(default="None", options={"SKIP_SAVE"})

    def execute(self, context):
        scene = context.scene

        render = scene.render

        render.resolution_x = 1080
        render.resolution_y = 1080
        render.resolution_percentage = 100
        render.image_settings.file_format = "PNG"
        render.image_settings.color_mode = "RGBA"
        render.image_settings.compression = 100
        render.display_mode = "SCREEN"

        cycles = scene.cycles

        cycles.film_transparent = True
        cycles.device = "GPU"
        cycles.pixel_filter_type = "BLACKMAN_HARRIS"
        cycles.progressive = "PATH"
        cycles.use_square_samples = False
        cycles.samples = 100
        cycles.preview_samples = 10
        cycles.sample_clamp_indirect = 10.0
        cycles.light_sampling_threshold = 0.01
        cycles.tile_order = "TOP_TO_BOTTOM"

        scene.view_settings.view_transform = "Filmic"
        scene.view_settings.look = "None"

        self.report({"INFO"}, "Render profile applied")

        return {"FINISHED"}

    # TODO props dialog
    # def invoke(self, context, event):
    #     wm = context.window_manager
    #     return wm.invoke_props_dialog(self)
