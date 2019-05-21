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

bl_info = {
    "name": "GTA Path Tools",
    "author": "Swoorup Joshi",
    "version": (2, 0, 1),
    "blender": (2, 72, 0),
    "location": "Search > BOOM & Add > LALALA",
    "description": "Fractured Object, Bomb, Projectile, Recorder",
    "warning": "",
    "url": "http://swoorupjoshi.xyz/blog/blender-addon-for-creating-waypoints/",
    "category": "Object",
}

if "init_data" in locals():
    import importlib
    importlib.reload(ui_main_panel)
    importlib.reload(path_mesh_loader)
    importlib.reload(path_mesh_exporter)
    importlib.reload(mesh_layer)
    importlib.reload(mesh_layer_gl)
    importlib.reload(gta)
else:
    from . import ui_main_panel
    from . import path_mesh_loader
    from . import path_mesh_exporter
    from . import mesh_layer
    from . import mesh_layer_gl
    from . import gta

init_data = True

import bpy

def register():
    bpy.utils.register_module(__name__) 
    ui_main_panel.setupProps()
    mesh_layer.setupProps()
    
def unregister():
    ui_main_panel.removeProps()
    mesh_layer.removeProps()
    bpy.utils.unregister_module(__name__) 
    
if __name__ == "__main__":
    register()
