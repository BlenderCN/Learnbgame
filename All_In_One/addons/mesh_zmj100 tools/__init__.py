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
# Contributed to by
# meta-androcto #

bl_info = {
    "name": "zmj100 mesh Tools",
    "author": "zmj100",
    "version": (0, 1),
    "blender": (2, 6, 3),
    "location": "View3D > Toolbar and View3D > Specials (W-key)",
    "description": "Add extra curve object types",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


if "bpy" in locals():
    import imp

else:
    from . import zmj100_face_inset_fillet
    from . import zmj100_mesh_face_inset

import bpy


class VIEW3D_MT_edit_mesh_zmj100(bpy.types.Menu):
    # Define the "Extras" menu
    bl_idname = "VIEW3D_MT_edit_mesh_zmj100"
    bl_label = "zmj100 Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("fi.op0_id",
            text="Face Inset")
        layout.operator("fif.op00_id",
            text="Face Inset Fillet")

# Register all operators and panels

# Define "Extras" menu
def menu_func(self, context):
    self.layout.menu("VIEW3D_MT_edit_mesh_zmj100", icon="PLUGIN")


def register():
    bpy.utils.register_module(__name__)

    # Add "Extras" menu to the "Add Mesh" menu
    bpy.types.VIEW3D_MT_edit_mesh_specials.prepend(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    # Remove "Extras" menu from the "Add Mesh" menu.
    bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_func)

if __name__ == "__main__":
    register()
