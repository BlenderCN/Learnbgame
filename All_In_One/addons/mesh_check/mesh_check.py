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

import bpy
from bgl import glBegin, glEnd, glEnable, glDisable, glColor3f, glColor4f, \
    glLineWidth, glPointSize, glVertex3f, GL_LINES, GL_DEPTH_TEST, GL_BLEND, \
    GL_POLYGON, GL_POINTS
from mathutils.geometry import tessellate_polygon as tessellate
import bmesh
from mathutils import Vector
from .icons.icons import load_icons
from bpy.props import BoolProperty

mesh_check_handle = []
draw_enabled = [False]
bm_old = [None]


def draw_poly(points):
    for i in range(len(points)):
        glVertex3f(points[i][0], points[i][1], points[i][2])


def get_offset(obj):
    if obj.modifiers:
        for mod in obj.modifiers:
            if mod.type == 'SHRINKWRAP':
                return 0.001 + obj.modifiers[mod.name].offset

    return 0.001


def draw_poles(color, point_size, datas):
    glColor4f(*color)
    glEnable(GL_BLEND)
    glPointSize(point_size)
    glBegin(GL_POINTS)
    draw_poly(datas)
    glEnd()


def mesh_check_draw_callback():
    obj = bpy.context.object

    if obj and obj.type == 'MESH':
        key = __package__.split(".")[0]
        prefs = bpy.context.user_preferences.addons[key].preferences

        if draw_enabled[0]:
            mesh = obj.data
            matrix_world = obj.matrix_world

            glLineWidth(prefs.edge_width)

            if bpy.context.mode == 'EDIT_MESH':

                use_occlude = True

                if bm_old[0] is None or not bm_old[0].is_valid:
                    bm = bm_old[0] = bmesh.from_edit_mesh(mesh)

                else:
                    bm = bm_old[0]

                no_depth = not bpy.context.space_data.use_occlude_geometry

                if no_depth:
                    glDisable(GL_DEPTH_TEST)

                    if prefs.finer_lines_behind_use:
                        glLineWidth(prefs.edge_width / 2.0)

                if prefs.display_non_manifold:
                    for edge in bm.edges:
                        if edge.is_valid and not edge.is_manifold:
                            edges = [matrix_world * vert.co for vert in
                                     edge.verts]
                            glColor4f(*prefs.non_manifold)
                            glBegin(GL_LINES)
                            draw_poly(edges)
                            glEnd()

                if prefs.display_e_pole or prefs.display_n_pole or prefs.display_more_pole or prefs.display_isolated_verts:
                    pole_dict = {0: [], 3: [], 5: [], 6: []}

                    pole_attributs = {
                        'display_isolated_verts': [prefs.isolated_verts,
                                                   pole_dict[0]],
                        'display_n_pole': [prefs.n_pole_color, pole_dict[3]],
                        'display_e_pole': [prefs.e_pole_color, pole_dict[5]],
                        'display_more_pole': [prefs.more_pole_color,
                                              pole_dict[6]],
                        }

                    for vert in bm.verts:
                        pole = len(vert.link_edges)
                        if pole in [0, 3, 5] or pole > 5:
                            verts_co = ((matrix_world * vert.co)[
                                            0] + vert.normal.x * 0.008,
                                        (matrix_world * vert.co)[
                                            1] + vert.normal.y * 0.008,
                                        (matrix_world * vert.co)[
                                            2] + vert.normal.z * 0.008)

                            if pole > 5:
                                pole_dict[6].append(verts_co)
                            else:
                                pole_dict[pole].append(verts_co)

                    for attr, options in pole_attributs.items():
                        if getattr(prefs, attr) and options[1]:
                            draw_poles(options[0], prefs.point_size,
                                       options[1])

                for face in bm.faces:
                    if not face.hide:
                        verts_count = len([verts for verts in face.verts])
                        if prefs.display_tris and verts_count == 3:
                            faces = []
                            for vert in face.verts:
                                vert_face = matrix_world * vert.co
                                faces.append((vert_face[
                                                  0] + face.normal.x * get_offset(
                                    obj),
                                              vert_face[
                                                  1] + face.normal.y * get_offset(
                                                  obj),
                                              vert_face[
                                                  2] + face.normal.z * get_offset(
                                                  obj))
                                             )

                            glColor4f(*prefs.tri_color)
                            glEnable(GL_BLEND)
                            glBegin(GL_POLYGON)
                            draw_poly(faces)
                            glEnd()

                            for edge in face.edges:
                                if edge.is_valid:
                                    edges = []
                                    for vert in edge.verts:
                                        vert_edge = matrix_world * vert.co
                                        edges.append((vert_edge[
                                                          0] + face.normal.x * get_offset(
                                            obj),
                                                      vert_edge[
                                                          1] + face.normal.y * get_offset(
                                                          obj),
                                                      vert_edge[
                                                          2] + face.normal.z * get_offset(
                                                          obj))
                                                     )
                                    glColor3f(*prefs.tri_color[:3])
                                    glBegin(GL_LINES)
                                    draw_poly(edges)
                                    glEnd()

                        if prefs.display_ngons and verts_count > 4:
                            new_faces = []
                            faces = []
                            coords = [v.co for v in face.verts]
                            indices = [v.index for v in face.verts]
                            for pol in tessellate([coords]):
                                new_faces.append([indices[i] for i in pol])

                            for f in new_faces:
                                faces.append([((matrix_world * bm.verts[i].co)[
                                                   0] + face.normal.x * get_offset(
                                    obj),
                                               (matrix_world * bm.verts[i].co)[
                                                   1] + face.normal.y * get_offset(
                                                   obj),
                                               (matrix_world * bm.verts[i].co)[
                                                   2] + face.normal.z * get_offset(
                                                   obj))
                                              for i in f])

                            for f in faces:
                                glColor4f(*prefs.ngons_color)
                                glEnable(GL_BLEND)
                                glBegin(GL_POLYGON)
                                draw_poly(f)
                                glEnd()

                            for edge in face.edges:
                                if edge.is_valid:
                                    edges = []
                                    for vert in edge.verts:
                                        vert_edge = matrix_world * vert.co
                                        edges.append((vert_edge[
                                                          0] + face.normal.x * get_offset(
                                            obj),
                                                      vert_edge[
                                                          1] + face.normal.y * get_offset(
                                                          obj),
                                                      vert_edge[
                                                          2] + face.normal.z * get_offset(
                                                          obj))
                                                     )
                                    glColor3f(*prefs.ngons_color[:3])
                                    glBegin(GL_LINES)
                                    draw_poly(edges)
                                    glEnd()

                glDisable(GL_BLEND)
                glColor4f(0.0, 0.0, 0.0, 1.0)


def updateBGLData(self, context):
    if self.mesh_check_use:
        bpy.ops.object.mode_set(mode='EDIT')
        draw_enabled[0] = True
        return

    draw_enabled[0] = False


class FaceTypeSelect(bpy.types.Operator):
    bl_idname = "object.face_type_select"
    bl_label = "Face type select"
    bl_options = {'REGISTER', 'UNDO'}

    face_type = bpy.props.EnumProperty(
            items=(('tris', 'Tris', ""),
                   ('ngons', 'Ngons', "")),
            default='ngons'
            )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        bpy.ops.mesh.select_all(action='DESELECT')

        if self.face_type == "tris":
            bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL')
            context.tool_settings.mesh_select_mode = (False, False, True)
        else:
            bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')

        return {'FINISHED'}


class MeshCheckCollectionGroup(bpy.types.PropertyGroup):
    mesh_check_use = bpy.props.BoolProperty(
            name="Mesh Check",
            description="Display Mesh Check options",
            default=False,
            update=updateBGLData,
            )

    display_options = BoolProperty(
            name="Options",
            default=False,
            )


def displayMeshCheckPanel(self, context):
    layout = self.layout
    icons = load_icons()
    tris = icons.get("triangles")
    ngons = icons.get("ngons")

    mesh_check = context.window_manager.mesh_check
    key = __package__.split(".")[0]
    prefs = bpy.context.user_preferences.addons[key].preferences

    row = layout.row(align=True)
    row.prop(mesh_check, 'mesh_check_use')
    if mesh_check.mesh_check_use:
        row.prop(mesh_check, 'display_options', text="", icon='SCRIPTWIN')
    split = layout.split(percentage=0.1)
    split.separator()
    split2 = split.split()
    row = split2.row(align=True)
    row.operator('object.face_type_select', text="Tris",
                 icon_value=tris.icon_id).face_type = 'tris'
    row.operator('object.face_type_select', text="Ngons",
                 icon_value=ngons.icon_id).face_type = 'ngons'

    if mesh_check.mesh_check_use:
        options = ['display_ngons', 'display_tris',
                   'display_e_pole', 'display_n_pole',
                   'display_more_pole', 'display_isolated_verts',
                   'display_non_manifold',
                   ]
        if mesh_check.display_options:
            for attr in options:
                split = layout.split(percentage=0.1)
                split.separator()
                split2 = split.split()
                row = split2.row(align=True)
                row.prop(prefs, attr)