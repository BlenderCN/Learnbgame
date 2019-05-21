# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Mitsuba Add-On
# --------------------------------------------------------------------------
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENSE BLOCK *****

import struct
import array
import zlib


def write_serialized_mesh(ser_path, mesh_name, mesh, ffaces_mats):
    uv_textures = mesh.tessface_uv_textures

    if len(uv_textures) > 0:
        if mesh.uv_textures.active and uv_textures.active.data:
            uv_layer = uv_textures.active.data

    else:
        uv_layer = None

    vertex_color = mesh.tessface_vertex_colors.active

    if vertex_color:
        vertex_color_layer = vertex_color.data

    else:
        vertex_color_layer = None

    # Export data
    points = array.array('d', [])
    normals = array.array('d', [])
    uvs = array.array('d', [])
    vtx_colors = array.array('d', [])
    ntris = 0
    face_vert_indices = array.array('I', [])  # list of face vert indices

    # Caches
    vert_vno_indices = {}       # mapping of vert index to exported vert index for verts with vert normals
    vert_use_vno = set()        # Set of vert indices that use vert normals

    vert_index = 0              # exported vert index
    for face in ffaces_mats:
        fvi = []
        for j, vertex in enumerate(face.vertices):
            v = mesh.vertices[vertex]

            if vertex_color_layer:
                if j == 0:
                    vert_col = vertex_color_layer[face.index].color1

                elif j == 1:
                    vert_col = vertex_color_layer[face.index].color2

                elif j == 2:
                    vert_col = vertex_color_layer[face.index].color3

                elif j == 3:
                    vert_col = vertex_color_layer[face.index].color4

            if uv_layer:
                # Flip UV Y axis. Blender UV coord is bottom-left, Mitsuba is top-left.
                uv_coord = (uv_layer[face.index].uv[j][0], 1.0 - uv_layer[face.index].uv[j][1])

            if face.use_smooth:

                if uv_layer:
                    if vertex_color_layer:
                        vert_data = (v.co[:], v.normal[:], uv_coord[:], vert_col[:])

                    else:
                        vert_data = (v.co[:], v.normal[:], uv_coord[:])

                else:
                    if vertex_color_layer:
                        vert_data = (v.co[:], v.normal[:], vert_col[:])

                    else:
                        vert_data = (v.co[:], v.normal[:])

                if vert_data not in vert_use_vno:
                    vert_use_vno.add(vert_data)

                    points.extend(vert_data[0])
                    normals.extend(vert_data[1])

                    if uv_layer:
                        uvs.extend(vert_data[2])

                        if vertex_color_layer:
                            vtx_colors.extend(vert_data[3])

                    else:
                        if vertex_color_layer:
                            vtx_colors.extend(vert_data[2])

                    vert_vno_indices[vert_data] = vert_index
                    fvi.append(vert_index)

                    vert_index += 1

                else:
                    fvi.append(vert_vno_indices[vert_data])

            else:
                # all face-vert-co-no-uv-color are unique, we cannot
                # cache them
                points.extend(v.co[:])
                normals.extend(face.normal[:])

                if uv_layer:
                    uvs.extend(uv_coord[:])

                if vertex_color_layer:
                    vtx_colors.extend(vert_col[:])

                fvi.append(vert_index)

                vert_index += 1

        # For Mitsuba, we need to triangulate quad faces
        face_vert_indices.extend(fvi[0:3])
        ntris += 3

        if len(fvi) == 4:
            face_vert_indices.extend((fvi[0], fvi[2], fvi[3]))
            ntris += 3

    del vert_vno_indices
    del vert_use_vno

    with open(ser_path, 'wb') as ser:
        # create mesh flags
        flags = 0
        # turn on double precision
        flags = flags | 0x2000
        # turn on vertex normals
        flags = flags | 0x0001

        # turn on uv layer
        if uv_layer:
            flags = flags | 0x0002

        if vertex_color_layer:
            flags = flags | 0x0008

        # begin serialized mesh data
        ser.write(struct.pack('<HH', 0x041C, 0x0004))

        # encode serialized mesh
        encoder = zlib.compressobj()
        ser.write(encoder.compress(struct.pack('<I', flags)))
        ser.write(encoder.compress(bytes(mesh_name + "_serialized\0", 'latin-1')))
        ser.write(encoder.compress(struct.pack('<QQ', vert_index, int(ntris / 3))))
        ser.write(encoder.compress(points.tostring()))
        ser.write(encoder.compress(normals.tostring()))

        if uv_layer:
            ser.write(encoder.compress(uvs.tostring()))

        if vertex_color_layer:
            ser.write(encoder.compress(vtx_colors.tostring()))

        ser.write(encoder.compress(face_vert_indices.tostring()))
        ser.write(encoder.flush())

        ser.write(struct.pack('<Q', 0))
        ser.write(struct.pack('<I', 1))
        ser.close()
