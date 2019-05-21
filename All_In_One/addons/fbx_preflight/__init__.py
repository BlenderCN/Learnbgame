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

from . import helpers
from . ui import (ExportObjectUIList)

from . properties import (
    PreflightMeshGroup,
    PreflightExportGroup,
    PreflightExportOptionsGroup,
    PreflightOptionsGroup
)

from . operators import (
    AddSelectionToPreflightGroup,
    AddPreflightObjectOperator,
    RemovePreflightObjectOperator,
    AddPreflightExportGroupOperator,
    RemovePreflightExportGroupOperator,
    ExportMeshGroupsOperator,
    ResetExportOptionsOperator,
    MigratePreflightGroups
)

from . panels import (PF_PT_preflight_panel,
                      PF_PT_preflight_export_options_panel)

from .menus import (
    PF_MT_preflight_menu,
    PF_MT_add_selection_menu,
    PF_MT_remove_export_group_menu
)

import bpy

bl_info = {
    "name": "FBX Preflight",
    "author": "Apsis Labs",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "category": "Import-Export",
    "description": "Define export groups to be output as FBX files."
}


classes = (
    ExportObjectUIList,
    MigratePreflightGroups,
    AddSelectionToPreflightGroup,
    AddPreflightObjectOperator,
    RemovePreflightObjectOperator,
    AddPreflightExportGroupOperator,
    RemovePreflightExportGroupOperator,
    ResetExportOptionsOperator,
    ExportMeshGroupsOperator,
    PreflightMeshGroup,
    PreflightExportGroup,
    PreflightExportOptionsGroup,
    PreflightOptionsGroup,
    PF_PT_preflight_panel,
    PF_PT_preflight_export_options_panel,
    PF_MT_preflight_menu,
    PF_MT_add_selection_menu,
    PF_MT_remove_export_group_menu
)

addon_keymaps = []


def register():
    # import addon_utils
    # addon_utils.enable("io_scene_fbx", default_set=True, persistent=True)

    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.preflight_props = bpy.props.PointerProperty(
        type=PreflightOptionsGroup)

    # Add Keymaps
    kcfg = bpy.context.window_manager.keyconfigs.addon
    if kcfg:
        km = kcfg.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi_mnu = km.keymap_items.new("wm.call_menu", "M", "PRESS", alt=True)
        kmi_mnu.properties.name = PF_MT_preflight_menu.bl_idname
        addon_keymaps.append((km, kmi_mnu))


def unregister():
    del bpy.types.Scene.preflight_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # Remove Keymaps
    for km, shortcut in addon_keymaps:
        km.keymap_items.remove(shortcut)

    addon_keymaps.clear()


if __name__ == "__main__":
    register()
