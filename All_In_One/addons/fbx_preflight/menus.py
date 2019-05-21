# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
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


class PF_MT_preflight_menu(bpy.types.Menu):
    bl_idname = "PF_MT_preflight_menu"
    bl_label = "FBX Preflight"

    def draw(self, context):
        layout = self.layout
        layout.operator("preflight.add_export_group",
                        text="Add Export Group")
        layout.menu(PF_MT_remove_export_group_menu.bl_idname)
        layout.separator()
        layout.menu(PF_MT_add_selection_menu.bl_idname)
        layout.separator()
        layout.operator("preflight.export_groups", icon="EXPORT")

        layout.separator()
        layout.operator('preflight.migrate_groups')


class PF_MT_remove_export_group_menu(bpy.types.Menu):
    bl_idname = "PF_MT_remove_export_group_menu"
    bl_label = "Remove Export Group..."

    def draw(self, context):
        layout = self.layout

        groups = context.scene.preflight_props.fbx_export_groups

        for group_idx, group in enumerate(groups):
            layout.operator("preflight.remove_export_group",
                            text='Remove ' + group.name).group_idx = group_idx


class PF_MT_add_selection_menu(bpy.types.Menu):
    bl_idname = "PF_MT_add_selection_menu"
    bl_label = "Add Selection to Export Group..."

    def draw(self, context):
        layout = self.layout

        groups = context.scene.preflight_props.fbx_export_groups

        for group_idx, group in enumerate(groups):
            layout.operator("preflight.add_selection_to_group",
                            text='Add to ' + group.name).group_idx = group_idx
