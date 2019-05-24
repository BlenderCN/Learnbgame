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
    'name': 'Rotate all selected objects on the z axis randomly',
    'author': 'Samuel Nicholas',
    'version': (0,1),
    "blender": (2, 6, 3),
    'location': '3D View -> Tool Shelf -> Object Tools Panel',
    'description': 'Randomize z rotation values for selected objects',
    'warning': '',
    'wiki_url': '',
    "tracker_url": "",
    "category": "Learnbgame",
}

import bpy,random


def main(context):
    for ob in context.selected_objects:
        ob.rotation_euler.z = random.random() * 3.141592 * 2

class SimpleOperator(bpy.types.Operator):
    """Randomize zrots"""
    bl_idname = "object.randomise_zr"
    bl_label = "Randomise Z rotations"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(SimpleOperator)


def unregister():
    bpy.utils.unregister_class(SimpleOperator)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.simple_operator()
