# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
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


bl_info = {
    "name": "Rigs of Rods Tools",
    "author": "Ulteq, Petr Ohlidal",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "category": "Learnbgame",
    }

if "bpy" in locals():  # Handle reload of Blender addon
    import importlib
    importlib.reload(truck_data)
    importlib.reload(truck_import)
    importlib.reload(truck_export)
    importlib.reload(truck_ui_beam_presets)
    importlib.reload(truck_ui_node_presets)
    importlib.reload(truck_ui_nodes)    
else:
    from . import truck_data
    from . import truck_import
    from . import truck_export
    from . import truck_ui_beam_presets
    from . import truck_ui_node_presets
    from . import truck_ui_nodes    

import bpy

# See: https://wiki.blender.org/wiki/Reference/Release_Notes/2.80/Python_API/Addons
classes = (
    truck_import.ROR_OT_truck_import,
    truck_export.ROR_OT_truck_export,
    # Beams
    truck_ui_beam_presets.ROR_PT_beam_presets, # UI panel
    truck_ui_beam_presets.ROR_UL_beam_presets, # UI list
    truck_ui_beam_presets.ROR_OT_beam_presets, # Operator
    # Nodes
    truck_ui_node_presets.ROR_PT_node_presets, # UI panel
    truck_ui_node_presets.ROR_UL_node_presets, # UI list
    truck_ui_node_presets.ROR_OT_node_presets, # Operator
    truck_ui_nodes.ROR_OT_node_options, # Operator    
    truck_ui_nodes.ROR_PT_node_options, # UI panel
    # Truckfile
    truck_data.RoR_BeamPreset,
    truck_data.RoR_NodePreset,
    truck_data.RoR_TruckLine,
    truck_data.RoR_Truck,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)

def register():
    bpy.app.debug = True
    reg_classes()
    bpy.types.TOPBAR_MT_file_import.append(truck_import.import_menu_func)
    bpy.types.TOPBAR_MT_file_export.append(truck_export.export_menu_func)

def unregister():
    unreg_classes()
    bpy.types.TOPBAR_MT_file_import.remove(truck_import.import_menu_func)
    bpy.types.TOPBAR_MT_file_export.remove(truck_export.export_menu_func)

if __name__ == "__main__":
    register()
