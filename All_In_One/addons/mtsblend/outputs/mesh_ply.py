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


def write_ply_mesh(ply_path, mesh_name, mesh, ffaces_mats):
    uv_textures = mesh.tessface_uv_textures

    if len(uv_textures) > 0:
        if uv_textures.active and uv_textures.active.data:
            uv_layer = uv_textures.active.data

    else:
        uv_layer = None

    # Here we work out exactly which vert+normal combinations
    # we need to export. This is done first, and the export
    # combinations cached before writing to file because the
    # number of verts needed needs to be written in the header
    # and that number is not known before this is done.

    # Export data
    ntris = 0
    co_no_uv_cache = []
    face_vert_indices = []      # mapping of face index to list of exported vert indices for that face

    # Caches
    vert_vno_indices = {}       # mapping of vert index to exported vert index for verts with vert normals
    vert_use_vno = set()        # Set of vert indices that use vert normals

    vert_index = 0              # exported vert index

    for face in ffaces_mats:
        fvi = []

        for j, vertex in enumerate(face.vertices):
            v = mesh.vertices[vertex]

            if uv_layer:
                # Flip UV Y axis. Blender UV coord is bottom-left, Mitsuba is top-left.
                uv_coord = (uv_layer[face.index].uv[j][0], 1.0 - uv_layer[face.index].uv[j][1])

            if face.use_smooth:

                if uv_layer:
                    vert_data = (v.co[:], v.normal[:], uv_coord)

                else:
                    vert_data = (v.co[:], v.normal[:])

                if vert_data not in vert_use_vno:
                    vert_use_vno.add(vert_data)

                    co_no_uv_cache.append(vert_data)

                    vert_vno_indices[vert_data] = vert_index
                    fvi.append(vert_index)

                    vert_index += 1

                else:
                    fvi.append(vert_vno_indices[vert_data])

            else:

                if uv_layer:
                    vert_data = (v.co[:], face.normal[:], uv_layer[face.index].uv[j][:])

                else:
                    vert_data = (v.co[:], face.normal[:])

                # All face-vert-co-no are unique, we cannot
                # cache them
                co_no_uv_cache.append(vert_data)

                fvi.append(vert_index)

                vert_index += 1

        # For Mitsuba, we need to triangulate quad faces
        face_vert_indices.append(fvi[0:3])
        ntris += 3

        if len(fvi) == 4:
            face_vert_indices.append((fvi[0], fvi[2], fvi[3]))
            ntris += 3

    del vert_vno_indices
    del vert_use_vno

    with open(ply_path, 'wb') as ply:
        ply.write(b'ply\n')
        ply.write(b'format binary_little_endian 1.0\n')
        ply.write(b'comment Created by MtsBlend 2.5 exporter for Mitsuba - www.mitsuba.net\n')

        # vert_index == the number of actual verts needed
        ply.write(('element vertex %d\n' % vert_index).encode())
        ply.write(b'property float x\n')
        ply.write(b'property float y\n')
        ply.write(b'property float z\n')

        ply.write(b'property float nx\n')
        ply.write(b'property float ny\n')
        ply.write(b'property float nz\n')

        if uv_layer:
            ply.write(b'property float s\n')
            ply.write(b'property float t\n')

        ply.write(('element face %d\n' % int(ntris / 3)).encode())
        ply.write(b'property list uchar uint vertex_indices\n')

        ply.write(b'end_header\n')

        # dump cached co/no/uv
        if uv_layer:
            for co, no, uv in co_no_uv_cache:
                ply.write(struct.pack('<3f', *co))
                ply.write(struct.pack('<3f', *no))
                ply.write(struct.pack('<2f', *uv))

        else:
            for co, no in co_no_uv_cache:
                ply.write(struct.pack('<3f', *co))
                ply.write(struct.pack('<3f', *no))

        # dump face vert indices
        for face in face_vert_indices:
            ply.write(struct.pack('<B', 3))
            ply.write(struct.pack('<3I', *face))

        del co_no_uv_cache
        del face_vert_indices
