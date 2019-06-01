# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2
#  of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy

from . import global_def
from . import operator_manager

##############
#   UI
##############


class IMAGE_PT_align_distribute(bpy.types.Panel):
    bl_label = "Align\\Distribute"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "Tools"

    @classmethod
    def poll(cls, context):
        sima = context.space_data
        return sima.show_uvedit and not context.tool_settings.use_uv_sculpt

    def draw(self, context):
        scn = context.scene
        layout = self.layout
        # load icons ID
        pcoll = global_def.preview_collections["main"]

        if context.scene.tool_settings.use_uv_select_sync:
            box = layout.box()
            box.label("You must disable uv sync selection")
            return
            
        layout.prop(scn, "relativeItems")
        layout.prop(scn, "selectionAsGroup")

        layout.separator()
        layout.label(text="Align:")

        box = layout.box()
        row = box.row(True)
        row.operator("uv.align_left_margin", "Left",
                     icon_value=pcoll["align_left"].icon_id)
        row.operator("uv.align_vertical_axis", "VCenter",
                     icon_value=pcoll["align_center_hor"].icon_id)
        row.operator("uv.align_right_margin", "Right",
                     icon_value=pcoll["align_right"].icon_id)

        row = box.row(True)
        row.operator("uv.align_top_margin", "Top",
                     icon_value=pcoll["align_top"].icon_id)
        row.operator("uv.align_horizontal_axis", "HCenter",
                     icon_value=pcoll["align_center_ver"].icon_id)
        row.operator("uv.align_low_margin", "Bottom",
                     icon_value=pcoll["align_bottom"].icon_id)

        row = layout.row()
        row.operator("uv.align_rotation", "Rotation",
                     icon_value=pcoll["align_rotation"].icon_id)
        row.operator("uv.equalize_scale", "Eq. Scale")

        layout.separator()
        # Another Panel??
        layout.label(text="Distribute:")

        box = layout.box()

        row = box.row(True)
        row.operator("uv.distribute_ledges_horizontally", "Left",
                     icon_value=pcoll["distribute_left"].icon_id)

        row.operator("uv.distribute_center_horizontally", "Center",
                     icon_value=pcoll["distribute_hcentre"].icon_id)

        row.operator("uv.distribute_redges_horizontally", "Right",
                     icon_value=pcoll["distribute_right"].icon_id)

        row = box.row(True)
        row.operator("uv.distribute_tedges_vertically", "TEdges",
                     icon_value=pcoll["distribute_top"].icon_id)
        row.operator("uv.distribute_center_vertically", "VCenters",
                     icon_value=pcoll["distribute_vcentre"].icon_id)
        row.operator("uv.distribute_bedges_vertically", "BEdges",
                     icon_value=pcoll["distribute_bottom"].icon_id)

        row = layout.row(True)
        row.operator("uv.equalize_horizontal_gap", "Eq. HGap",
                     icon_value=pcoll["distribute_hdist"].icon_id)
        row.operator("uv.equalize_vertical_gap", "Eq. VGap",
                     icon_value=pcoll["distribute_vdist"].icon_id)
        #
        # # wip
        # # row = layout.row(True)
        # # row.operator("uv.remove_overlaps", "Remove Overlaps")
        #
        # # TODO organize these
        layout.separator()
        layout.label("Others:")
        row = layout.row()
        layout.operator("uv.snap_islands")

        row = layout.row()
        layout.operator("uv.match_islands")

        # WIP
        # row = layout.row()
        # layout.operator("uv.pack_pile_islands")


#################################
#################################
# REGISTRATION
#################################
#################################
_om = operator_manager.om
_om.addOperator(IMAGE_PT_align_distribute)
