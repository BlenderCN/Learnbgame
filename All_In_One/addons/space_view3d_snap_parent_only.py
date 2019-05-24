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
    "name": "Snap: Selection To Cursor (Parent Only)",
    "author": "Buerbaum Martin (Pontiac)",
    "version": (0, 1),
    "blender": (2, 5, 6),
    "api": 35131,
    "location": "View3D > Object > Snap > Selection To Cursor (Parent Only)",
    "description": "Snap the selected object to the 3D cursor,"\
        " but keep children in place.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

"""Selection To Cursor (Parent Only)"""

import bpy
from mathutils import Matrix


# Returns a single selected object.
# Returns None if more than one (or nothing) is selected.
# Note: Ignores the active object.
def getSingleObject(context):
    if len(context.selected_objects) == 1:
        return context.selected_objects[0]

    return None


def selection_to_cursor_parent_only(context):
    sce = context.scene
    cur_loc = sce.cursor_location
    obj = context.active_object

    if (obj):
        # Store original locations of children.
        children_worldpos = []
        for c in obj.children:
            children_worldpos.append(c.matrix_world.copy())

        # Translate parent object
        cur_mat = Matrix.Translation(cur_loc)
        obj.matrix_world = cur_mat

        # Translate all child objects to their original location.
        i = 0
        for c in obj.children:
            c.matrix_world = children_worldpos[i]
            i = i + 1

    return


class SnapParentOnly_Operator(bpy.types.Operator):
    ''''''
    bl_idname = "object.snap_selection_to_cursor_parent_only"
    bl_label = "Snap Selection To Cursor (Parent Only)"

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        selection_to_cursor_parent_only(context)
        return {'FINISHED'}


# Define the menu
def menu_func(self, context):
    self.layout.operator("object.snap_selection_to_cursor_parent_only",
        icon="PLUGIN",
        text="Selection To Cursor (Parent Only)")


def register():
    bpy.utils.register_module(__name__)

    # Add the menu entry to the "Snap" menu.
    bpy.types.VIEW3D_MT_snap.append(menu_func)

    pass


def unregister():
    bpy.utils.unregister_module(__name__)

    # Remove menu entry from the "Snap" menu.
    bpy.types.INFO_MT_snap.remove(menu_func)
    pass

if __name__ == "__main__":
    register()
