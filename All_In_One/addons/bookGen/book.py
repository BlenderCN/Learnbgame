# ====================== BEGIN GPL LICENSE BLOCK ======================
#    This file is part of the  bookGen-addon for generating books in Blender
#    Copyright (c) 2014 Oliver Weissbarth
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ======================= END GPL LICENSE BLOCK ========================

import bpy
import bmesh

from .utils import get_bookgen_collection 
from .data.verts import get_verts
from .data.faces import get_faces
from .data.uvs import get_seams


class Book:

    def __init__(self, cover_height, cover_thickness, cover_depth, page_height, page_depth, page_thickness, spline_curl, hinge_inset, hinge_width, spacing, book_width, lean, lean_angle, unwrap, subsurf, smooth):
        self.height = cover_height
        self.width = page_thickness + 2 * cover_thickness
        self.depth = cover_depth
        self.spacing = spacing
        self.lean_angle = lean_angle
        self.lean = lean
        self.smooth = smooth
        self.unwrap = unwrap
        self.subsurf = subsurf


        self.verts = get_verts(page_thickness, page_height, cover_depth, cover_height, cover_thickness, page_depth, hinge_inset, hinge_width, spline_curl)
        self.faces = get_faces()
        self.seams = get_seams()

    def to_object(self):
        def index_to_vert(face):
            lst = []
            for i in face:
                lst.append(vert_ob[i])
            return tuple(lst)

        mesh = bpy.data.meshes.new("book")

        self.obj = bpy.data.objects.new("book", mesh)


        bm = bmesh.new()
        bm.from_mesh(mesh)
        vert_ob = []
        for vert in self.verts:
            vert_ob.append(bm.verts.new(vert))

        bm.verts.index_update()
        bm.verts.ensure_lookup_table()


        if(self.unwrap):
            for seam in self.seams:
                edge = bm.edges.new((bm.verts[seam[0]], bm.verts[seam[1]]))
                edge.seam = True

        for face in self.faces:
            f = bm.faces.new(index_to_vert(face))
            if self.smooth:
                f.smooth = True

        bm.faces.index_update()
        bm.edges.ensure_lookup_table()

        bm.normal_update()
        bm.to_mesh(mesh)
        bm.free()

        """
        if(unwrap):
            bpy.context.view_layer.objects.active = self.obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.unwrap(method='CONFORMAL', margin=0.05)
            bpy.ops.object.editmode_toggle()
        """

        if(self.subsurf):
            self.obj.modifiers.new("subd", type='SUBSURF')
            self.obj.modifiers['subd'].levels = 1

        return self.obj


