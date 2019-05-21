# ##### BEGIN GPL LICENSE BLOCK #####
#
#  3dview_objio_panel.py
#  Display Import/Export .obj buttons in the 3D view props
#  Copyright (C) 2016 Quentin Wenger
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



bl_info = {"name": ".obj I/O Panel",
           "description": "Display Import/Export .obj buttons in the 3D view props",
           "author": "Quentin Wenger (Matpi)",
           "version": (1, 0),
           "blender": (2, 75, 0),
           "location": "3D View(s) -> Properties -> Import/Export .obj",
           "warning": "",
           "wiki_url": "",
           "tracker_url": "",
           "category": "3D View"
           }



import bpy

class ObjIO(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Import/Export .obj"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("import_scene.obj")
        row.operator("export_scene.obj")
        
        
def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()
