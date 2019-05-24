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
#  Author: Dealga McArdle (@zeffii)
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Push Face Boolean",
    "author": "Dealga McArdle",
    "version": (0, 0, 2),
    "blender": (2, 7, 4),
    "location": "3dview, key combo",
    "description": "Adds degenerate free face extrusion into mesh.",
    "wiki_url": "",
    "tracker_url": "",
    "keywords": ("extrude", "face", "boolean", "clean"),
    "category": "Learnbgame",
}

if 'bpy' in globals():
    print('{0}: detected reload event! cool.'.format(__package__))

    if 'boolean_main' in globals():
        import imp
        imp.reload(boolean_main)
        imp.reload(bmesh_extras)
        print('{0}: reloaded.'.format(__package__))

else:
    import bpy
    from . import boolean_main
    from . import bmesh_extras

Scene = bpy.types.Scene


def register():
    Scene.BGL_DEMO_PROP_THICKNESS = bpy.props.IntProperty(default=1, max=5)
    Scene.BGL_OFFSET_SCALAR = bpy.props.FloatProperty(
        min=-5.0, max=5.0, default=0.0)
    Scene.BGL_FUDGE_FACTOR = bpy.props.FloatProperty(min=0.0, max=0.001, step=0.00001, default=0.0001)
    Scene.BGL_OPERATOR_RUNNING = bpy.props.BoolProperty(default=False)

    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
    del Scene.BGL_OFFSET_SCALAR
    del Scene.BGL_DEMO_PROP_THICKNESS
    del Scene.BGL_FUDGE_FACTOR
    del Scene.BGL_OPERATOR_RUNNING
