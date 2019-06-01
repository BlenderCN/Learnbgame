'''
mesh_check.py
Draw ngons and triangles with bgl - using bmesh in edit mode
Copyright (C) 2016 Pistiwique
Created by Pistiwique

The code is based on 3dview_border_lines_bmesh_edition.py
Copyright (C) 2015 Quentin Wenger

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {"name": "Mesh Check BGL edition",
           "description": "Display the triangles and ngons of the mesh",
           "author": "Pistiwique",
           "version": (1, 0, 0),
           "blender": (2, 75, 0),
           "location": "Panel N -> Mesh display",
           "category": "Learnbgame",
           }

import bpy

from bpy.props import FloatProperty, BoolProperty, FloatVectorProperty

from .mesh_check import (displayMeshCheckPanel,
                         MeshCheckCollectionGroup,
                         mesh_check_handle,
                         mesh_check_draw_callback,
                         )

# load and reload submodules
##################################

import importlib
from . import developer_utils

importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__,
                                              "bpy" in locals())


class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    edge_width = FloatProperty(
            name="Edge width",
            description="Edges width in pixels",
            min=1.0, max=10.0,
            default=3.0,
            subtype='PIXEL',
            )

    finer_lines_behind_use = BoolProperty(
            name="Finer Lines behind",
            description="Display partially hidden edges finer in non-occlude mode",
            default=True,
            )

    display_tris = BoolProperty(
            name="Tris",
            description="Display triangles",
            default=False,
            )

    tri_color = FloatVectorProperty(
            name="Tri Color",
            description="Custom color for the triangles",
            min=0.0, max=1.0,
            default=(0.7, 0.7, 0.05, 0.4),
            size=4,
            subtype='COLOR',
            )

    display_ngons = BoolProperty(
            name="Ngons",
            description="Display Ngons",
            default=True,
            )

    ngons_color = FloatVectorProperty(
            name="Ngons Color",
            description="custom color for the ngons",
            min=0.0, max=1.0,
            default=(0.7, 0.07, 0.06, 0.4),
            size=4,
            subtype='COLOR',
            )

    point_size = FloatProperty(
            name="Point Size",
            description="Point Size in pixels",
            min=1.0, max=20.0,
            default=10.0,
            subtype='PIXEL',
            )

    display_e_pole = BoolProperty(
            name="E Poles",
            description="Display E Pole",
            default=False,
            )

    e_pole_color = FloatVectorProperty(
            name="E Pole Color",
            description="Custom color for E Pole",
            min=0.0, max=1.0,
            default=(0.5, 0.625, 1, 1),
            size=4,
            subtype='COLOR',
            )

    display_n_pole = BoolProperty(
            name="N Poles",
            description="Display N Pole",
            default=False,
            )

    n_pole_color = FloatVectorProperty(
            name="N Pole Color",
            description="Custom color for N Pole",
            min=0.0, max=1.0,
            default=(0.5, 1, 0.5, 1),
            size=4,
            subtype='COLOR',
            )

    display_more_pole = BoolProperty(
            name="Pole more than 5",
            description="Display pole with more than 5 edges",
            default=False,
            )

    more_pole_color = FloatVectorProperty(
            name="More Pole Color",
            description="Custom color for Pole with more than 5 edges",
            min=0.0, max=1.0,
            default=(1, 0.145, 0.145, 1),
            size=4,
            subtype='COLOR',
            )

    display_non_manifold = BoolProperty(
            name="Non Manifold",
            description="Display Non Manifold edges",
            default=False,
            )

    non_manifold = FloatVectorProperty(
            name="Non Manifold",
            description="Custom color for non manifold edges",
            min=0.0, max=1.0,
            default=(0.5, 1, 0.5, 1),
            size=4,
            subtype='COLOR',
            )

    display_isolated_verts = BoolProperty(
            name="Isolated Verts",
            description="Display isolated vertices",
            default=True,
            )

    isolated_verts = FloatVectorProperty(
            name="Isolated verts",
            description="Custom color for isolated vertices",
            min=0.0, max=1.0,
            default=(1.0, 0.5, 0.5, 1),
            size=4,
            subtype='COLOR',
            )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label("Faces settings", icon='FACESEL')
        box.prop(self, 'edge_width')
        box.prop(self, 'finer_lines_behind_use')
        box.separator()
        row = box.row()
        split = row.split(percentage=0.2)
        split.prop(self, 'display_tris')
        split2 = split.split(percentage=0.2)
        split2.prop(self, 'tri_color', text="")
        row = box.row()
        split = row.split(percentage=0.2)
        split.prop(self, 'display_ngons')
        split2 = split.split(percentage=0.2)
        split2.prop(self, 'ngons_color', text="")
        row = box.row()
        split = row.split(percentage=0.2)
        split.prop(self, 'display_non_manifold')
        split2 = split.split(percentage=0.2)
        split2.prop(self, 'non_manifold', text="")

        box = layout.box()
        box.label("Points settings", icon='VERTEXSEL')
        box.prop(self, 'point_size')
        box.separator()
        row = box.row()
        split = row.split(percentage=0.25)
        split.prop(self, 'display_e_pole')
        split2 = split.split(percentage=0.2)
        split2.prop(self, 'e_pole_color', text="")
        row = box.row()
        split = row.split(percentage=0.25)
        split.prop(self, 'display_n_pole')
        split2 = split.split(percentage=0.2)
        split2.prop(self, 'n_pole_color', text="")
        row = box.row()
        split = row.split(percentage=0.25)
        split.prop(self, 'display_more_pole')
        split2 = split.split(percentage=0.2)
        split2.prop(self, 'more_pole_color', text="")
        row = box.row()
        split = row.split(percentage=0.25)
        split.prop(self, 'display_isolated_verts')
        split2 = split.split(percentage=0.2)
        split2.prop(self, 'isolated_verts', text="")


# register
##################################

import traceback


def register():
    try:
        bpy.utils.register_module(__name__)
    except:
        traceback.print_exc()

    print(
        "Registered {} with {} modules".format(bl_info["name"], len(modules)))

    bpy.utils.register_module(__name__)
    bpy.types.WindowManager.mesh_check = bpy.props.PointerProperty(
            type=MeshCheckCollectionGroup)
    bpy.types.VIEW3D_PT_view3d_meshdisplay.prepend(displayMeshCheckPanel)
    if mesh_check_handle:
        bpy.types.SpaceView3D.draw_handler_remove(mesh_check_handle[0],
                                                  'WINDOW')
    mesh_check_handle[:] = [
        bpy.types.SpaceView3D.draw_handler_add(mesh_check_draw_callback, (),
                                               'WINDOW', 'POST_VIEW')]


def unregister():
    try:
        bpy.utils.unregister_module(__name__)
    except:
        traceback.print_exc()

    print("Unregistered {}".format(bl_info["name"]))

    bpy.types.VIEW3D_PT_view3d_meshdisplay.remove(displayMeshCheckPanel)
    del bpy.types.WindowManager.mesh_check
    if mesh_check_handle:
        bpy.types.SpaceView3D.draw_handler_remove(mesh_check_handle[0],
                                                  'WINDOW')
        mesh_check_handle[:] = []

