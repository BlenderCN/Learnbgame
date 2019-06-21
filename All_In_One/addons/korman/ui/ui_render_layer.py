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

class RenderLayerButtonsPanel:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render_layer"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == "PLASMA_GAME"


class BakePassUI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index=0, flt_flag=0):
        layout.prop(item, "display_name", emboss=False, text="", icon="RENDERLAYERS")


class PlasmaBakePassPanel(RenderLayerButtonsPanel, bpy.types.Panel):
    bl_label = "Plasma Bake Passes"

    def draw(self, context):
        layout = self.layout
        scene = context.scene.plasma_scene

        ui_list.draw_list(layout, "BakePassUI", "scene", scene, "bake_passes",
                          "active_pass_index",  name_prefix="Pass",
                          name_prop="display_name", rows=3, maxrows=3)

        active_pass_index = scene.active_pass_index
        try:
            bake_pass = scene.bake_passes[active_pass_index]
        except:
            pass
        else:
            box = layout.box()
            box.prop(bake_pass, "display_name")
            box.prop(bake_pass, "render_layers")
