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

# System imports
import bpy
from bpy.props import *
from bpy.types import Panel

# updater import
from .app_handlers import *
from ..functions.common import *
from .. import addon_updater_ops

class PROPERTIES_PT_abs_plastic_materials(Panel):
    bl_space_type  = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context     = "material"
    bl_label       = "ABS Plastic Materials"
    bl_idname      = "PROPERTIES_PT_abs_plastic_materials"
    # bl_category    = "ABS Plastic Materials"
    # COMPAT_ENGINES = {"CYCLES", "BLENDER_EEVEE"}

    # @classmethod
    # def poll(cls, context):
    #     """ ensures operator can execute (if not, returns false) """
    #     return True

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        # Call to check for update in background
        # Internally also checks to see if auto-check enabled
        # and if the time interval has passed
        addon_updater_ops.check_for_update_background()
        # draw auto-updater update box
        addon_updater_ops.update_notice_box_ui(self, context)

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("abs.append_materials", text="Import ABS Plastic Materials", icon="IMPORT")
        # row = col.row(align=True)
        # row.operator("abs.mark_outdated", text="Mark Materials as Outdated", icon="LIBRARY_DATA_OVERRIDE" if b280() else "GO_LEFT")

        # material settings
        col = layout.column(align=True)
        col.label(text="Properties:")
        row = col.row(align=True)
        row.prop(scn, "abs_subsurf")
        row = col.row(align=True)
        row.prop(scn, "abs_roughness")
        row = col.row(align=True)
        row.prop(scn, "abs_randomize")


        row = col.row(align=True)
        row.label(text="UV Details:")
        row = col.row(align=True)
        row.prop(scn, "uv_detail_quality", text="Quality")
        row = col.row(align=True)
        row.prop(scn, "abs_fingerprints")
        row = col.row(align=True)
        row.prop(scn, "abs_displace")
        # row = col.row(align=True)
        # row.prop(scn, "abs_uv_scale")
        row = col.row(align=True)
        row.prop(scn, "save_datablocks")
        if b280():
            row = col.row(align=True)
            row.prop(scn, "abs_viewport_transparency")
