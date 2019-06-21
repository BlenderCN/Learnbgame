# -*- coding: utf8 -*-
# Blender WCP IFF mesh import/export script by Kevin Caccamo
# Copyright © 2013-2016 Kevin Caccamo
# E-mail: kevin@ciinet.org
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
# <pep8-80 compliant>

# Classes for WCP/SO IFF Meshes
from . import iff


def colour_texnum(colour):
    "Convert a colour from Blender/floating point format to bytes"
    import struct

    # Make Blender mathutils import optional
    try:
        # Using Blender imports
        import mathutils
        if not isinstance(colour, mathutils.Color):
            raise TypeError("The colour you want to convert must be a valid "
                            "Blender colour!")
    except ImportError:
        # Not using Blender imports
        if not isinstance(colour, list) or not isinstance(colour, tuple):
            raise TypeError("The colour you want to convert must be a valid "
                            "colour!")
    for cc in colour:
        if not isinstance(cc, float):
            raise TypeError("The colour you want to convert must be a valid "
                            "Blender colour!")

    def clamp_byte(x):
        if x <= 0: return 0
        elif x >= 256: return 255
        else: return x

    clrbytes = [round(cc * 256) for cc in colour]
    clrbytes = tuple(map(clamp_byte, clrbytes))
    tnbytes = struct.pack("<BBBB", 0x7F, *clrbytes)
    tnint = struct.unpack(">I", tnbytes)[0]
    return tnint


def texnum_colour(texnum):
    "Convert a flat colour from bytes to Blender/floating point format."
    # Texnum format: 0xFFrrggbb

    colour = [0.0, 0.0, 0.0]
    try:
        import mathutils
        colour = mathutils.Color((0.0, 0.0, 0.0))
    except ImportError:
        pass

    def byte_float(x):
        return 1.0 if x == 255 else x / 256.0

    colour[0] = byte_float((texnum & 0x00ff0000) >> 16)  # Red
    colour[1] = byte_float((texnum & 0x0000ff00) >> 8)  # Green
    colour[2] = byte_float(texnum & 0x000000ff)  # Blue

    return colour


# =========================== Other model metadata ===========================


class Collider:
    "Collision sphere or BSP tree"

    COLLIDER_TYPES = ("sphere", "bsp", "bsp+region")

    def __init__(self, col_type, *data):
        if col_type not in self.COLLIDER_TYPES:
            raise ValueError("Invalid collider type %s!" % col_type)

        if not isinstance(data[0], Sphere):
            raise TypeError("A collider must have a boundary sphere!")

        # if ((col_type == "bsp" or col_type == "bsp+region") and
        #         not isinstance(data[1], bsp.BSPTree)):
        #     raise TypeError("Collider data for a BSP collider must have a "
        #                     "sphere and a BSP tree!")
        #
        # if (col_type == "bsp+region" and
        #         not isinstance(data[2], bsp.Blockmap)):
        #     raise TypeError("Collider data for a BSP collider must have a "
        #                     "sphere and a BSP tree!")

        if col_type == "bsp" or col_type == "bsp+region":
            raise TypeError("BSP trees are not yet supported!")

        self.col_type = col_type
        self.data = data

    def to_coll_form(self):
        "Convert this Collider to a COLL form."
        coll_form = iff.IffForm("COLL")
        sphr_chnk = self.data[0].to_collsphr_chunk()
        coll_form.add_member(sphr_chnk)

        if self.col_type == "bsp":
            if self.data[1] is not None:
                extn_form = iff.IffForm("EXTN")
                coll_form.add_member(extn_form)
            else:
                raise TypeError("data[1] must be a BSP tree!")

        return coll_form

    def __str__(self):
        strr = "{} collider: (".format(self.col_type.capitalize())
        for didx in range(len(self.data)):
            strr += "{!s}".format(self.data[didx])
            if didx < len(self.data) - 1: strr += ", "
        strr += ")"
        return strr


class Sphere:
    """CNTR/RADI chunks for each LOD, or SPHR chunk for collider.

    Position data is represented internally in WCSO format
    (vertical Y, front/back Z)."""

    def __init__(self, x, y, z, r):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.r = float(r)

    def to_tuple(self):
        "Get the data for this sphere in tuple format"
        return (self.x, self.y, self.z, self.r)

    def to_cntr_chunk(self):
        """Make a CNTR chunk using the data for this sphere.

        The RADI chunk is used in LOD meshes."""
        cntr_chunk = iff.IffChunk("CNTR")
        cntr_chunk.add_member(self.x)
        cntr_chunk.add_member(self.y)
        cntr_chunk.add_member(self.z)
        return cntr_chunk

    def to_radi_chunk(self):
        """Make a RADI chunk using the data for this sphere.

        The RADI chunk is used in LOD meshes."""
        radi_chunk = iff.IffChunk("RADI")
        radi_chunk.add_member(self.r)
        return radi_chunk

    def to_collsphr_chunk(self):
        """Make a SPHR chunk using the data for this sphere.

        The SPHR chunk is used to define a Collider's boundaries."""
        collsphr_chunk = iff.IffChunk("SPHR")
        collsphr_chunk.add_member(self.x)
        collsphr_chunk.add_member(self.y)
        collsphr_chunk.add_member(self.z)
        collsphr_chunk.add_member(self.r)
        return collsphr_chunk

    def to_chunks(self):
        "Get the CNTR and RADI chunks for this Sphere."
        return self.to_cntr_chunk(), self.to_radi_chunk()

    def to_bl_obj(self, name="cntradi"):
        "Convert this sphere to a Blender object."
        import bpy
        bl_obj = bpy.data.objects.new(name, None)
        bl_obj.empty_draw_type = "SPHERE"

        bl_obj.location.x = self.x
        bl_obj.location.y = self.z
        bl_obj.location.z = self.y
        bl_obj.scale = self.r, self.r, self.r

        return bl_obj

    @staticmethod
    def from_cntradi_chunks(cntr_data, radi_data):
        "Convert CNTR and RADI data to a Sphere."
        import struct

        x, y, z = struct.unpack("<fff", cntr_data)
        r = struct.unpack("<f", radi_data)[0]

        return Sphere(x, y, z, r)

    @staticmethod
    def from_sphr_chunk(sphr_data):
        "Convert a SPHR data to a Sphere."
        import struct

        x, y, z, r = struct.unpack("<ffff", sphr_data)

        return Sphere(x, y, z, r)

    def __str__(self):
        return "Sphere ({0.x:.4f}, {0.y:.4f}, {0.z:.4f}:{0.r:.4f})".format(
            self)


class Hardpoint:
    """A hardpoint of a model.

    Position data is represented internally in WCSO format
    (vertical Y, front/back Z)."""

    def __init__(self, rot_matrix, location, name):
        # rot_matrix should be a mathutils.Matrix(3x3) or compatible value
        # location should be a mathutils.Vector or compatible value

        self.rot_matrix = rot_matrix
        self.location = location
        self.name = name

    def to_chunk(self):
        "Convert this hardpoint to a HARD chunk."
        hard_chunk = iff.IffChunk("HARD")
        hard_chunk.add_member(self.rot_matrix[0][0])
        hard_chunk.add_member(self.rot_matrix[0][1])
        hard_chunk.add_member(self.rot_matrix[0][2])
        hard_chunk.add_member(self.location[0])
        hard_chunk.add_member(self.rot_matrix[1][0])
        hard_chunk.add_member(self.rot_matrix[1][1])
        hard_chunk.add_member(self.rot_matrix[1][2])
        hard_chunk.add_member(self.location[1])
        hard_chunk.add_member(self.rot_matrix[2][0])
        hard_chunk.add_member(self.rot_matrix[2][1])
        hard_chunk.add_member(self.rot_matrix[2][2])
        hard_chunk.add_member(self.location[2])
        hard_chunk.add_member(self.name)
        return hard_chunk

    def to_bl_obj(self):
        "Convert this hardpoint to a Blender object."
        import bpy
        from mathutils import Matrix, Vector
        bl_obj = bpy.data.objects.new("hp-" + self.name, None)
        bl_obj.empty_draw_type = "ARROWS"

        matrix_rot = Matrix(self.rot_matrix).to_4x4()

        # Convert position/rotation from WC
        euler_rot = matrix_rot.to_euler("XYZ")
        euler_rot.y, euler_rot.z = -euler_rot.z, -euler_rot.y
        euler_rot.x *= -1

        matrix_rot = euler_rot.to_matrix().to_4x4()
        vector_loc = Vector(self.location)
        vector_loc.y, vector_loc.z = vector_loc.z, vector_loc.y
        matrix_loc = Matrix.Translation(vector_loc)

        bl_obj.matrix_basis = matrix_loc * matrix_rot
        return bl_obj

    @staticmethod
    def from_chunk(chunk_data):
        "Convert a HARD chunk to a hardpoint."
        import struct

        def read_cstring(data, ofs):
            cstring = bytearray()
            while data[ofs] != 0:
                if data[ofs] == 0: break
                cstring.append(data[ofs])
                ofs += 1
            return cstring.decode("ascii")

        hardpt_data = struct.unpack_from("<ffffffffffff", chunk_data, 0)

        hardpt_rot = (
            (hardpt_data[0], hardpt_data[1], hardpt_data[2]),
            (hardpt_data[4], hardpt_data[5], hardpt_data[6]),
            (hardpt_data[8], hardpt_data[9], hardpt_data[10])
        )

        hardpt_loc = (hardpt_data[3], hardpt_data[7], hardpt_data[11])

        hardpt_name_ofs = 48
        hardpt_name = read_cstring(chunk_data, hardpt_name_ofs)

        return Hardpoint(hardpt_rot, hardpt_loc, hardpt_name)

    def __str__(self):
        return "Hardpoint \"{0}\" ({1.x:.4f}, {1.y:.4f}, {1.z:.4f})".format(
            self.name, self.location
        )


# ================================= LOD Info =================================


class MeshLODForm(iff.IffForm):
    "A LOD mesh."

    def __init__(self, lod_lev, version=12):
        self._version = int(version)
        self._mesh_form = iff.IffForm("MESH")
        self._geom_form = iff.IffForm("{!s:0>4}".format(version))
        self._name_chunk = iff.IffChunk("NAME")
        self._vert_chunk = iff.IffChunk("VERT")
        if self._version <= 11:
            self._norm_chunk = iff.IffChunk("NORM")
        self._vtnm_chunk = iff.IffChunk("VTNM")
        self._fvrt_chunk = iff.IffChunk("FVRT")
        self._face_chunk = iff.IffChunk("FACE")
        self._cntr_chunk = iff.IffChunk("CNTR")
        self._radi_chunk = iff.IffChunk("RADI")
        self._geom_form.add_member(self._name_chunk)
        self._geom_form.add_member(self._vert_chunk)
        self._geom_form.add_member(self._vtnm_chunk)
        self._geom_form.add_member(self._fvrt_chunk)
        self._geom_form.add_member(self._face_chunk)
        self._geom_form.add_member(self._cntr_chunk)
        self._geom_form.add_member(self._radi_chunk)
        self._mesh_form.add_member(self._geom_form)

        self.lod_lev = lod_lev
        form_name = "{!s:0>4}".format(self.lod_lev)
        super().__init__(form_name, [self._mesh_form])

    def set_name(self, name):
        "Set the name of this LOD mesh."
        # Check data types before adding to respective chunks
        if self._name_chunk.has_members():
            self._name_chunk.clear_members()
        if isinstance(name, str):
            self._name_chunk.add_member(name)
        else:
            raise TypeError("Name of this mesh LOD must be a string!")

    def add_vertex(self, vx, vy, vz):
        "Add a vertex to this LOD mesh."
        self._vert_chunk.add_member(float(vx))
        self._vert_chunk.add_member(float(vy))
        self._vert_chunk.add_member(float(vz))

    def add_vert_normal(self, nx, ny, nz):
        "Add a vertex normal to this LOD mesh."
        self._vtnm_chunk.add_member(float(nx))
        self._vtnm_chunk.add_member(float(ny))
        self._vtnm_chunk.add_member(float(nz))

    def add_face_normal(self, nx, ny, nz):
        "Add a face normal to this LOD mesh."
        if self._version >= 12:
            self.add_vert_normal(nx, ny, nz)
        else:
            self._norm_chunk.add_member(float(nx))
            self._norm_chunk.add_member(float(ny))
            self._norm_chunk.add_member(float(nz))

    def add_fvrt(self, vert_idx, vtnm_idx, uv_x, uv_y):
        """Add a "face vertex" to this LOD mesh.

        A "face vertex" consists of a vertex index, a normal index, and X/Y UV
        coordinates. They are somewhat analogous to Blender's BMesh loops."""

        if vert_idx < 0:
            raise ValueError("Vertex index must not be negative!")
        if vtnm_idx < 0:
            raise ValueError("Vertex normal index must not be negative!")

        self._fvrt_chunk.add_member(int(vert_idx))
        self._fvrt_chunk.add_member(int(vtnm_idx))
        self._fvrt_chunk.add_member(float(uv_x))
        self._fvrt_chunk.add_member(float(uv_y))

    def add_face(self, norm_idx, dplane, texnum,
                 fvrt_idx, num_verts, light_flags, alt_mat=0x7F0096FF):
        """Add a face to this LOD mesh."""
        if norm_idx < 0:
            raise ValueError("Face normal index must not be negative!")
        if fvrt_idx < 0:
            raise ValueError("FVRT index must not be negative!")
        if num_verts < 0:
            raise ValueError("Number of vertices must not be negative!")

        self._face_chunk.add_member(int(norm_idx))
        self._face_chunk.add_member(float(dplane))  # D-Plane
        self._face_chunk.add_member(int(texnum))  # Texture number
        self._face_chunk.add_member(int(fvrt_idx))  # Index of first FVRT
        self._face_chunk.add_member(int(num_verts))  # Number of vertices/edges
        self._face_chunk.add_member(int(light_flags))  # Lighting flags
        self._face_chunk.add_member(int(alt_mat))  # Alternate/flat colour MAT

    def set_cntradi(self, sphere):
        "Set the center and radius of this LOD mesh."

        if not isinstance(sphere, Sphere):
            raise TypeError("You must use a valid Sphere object to set the "
                            "center location and radius for this LOD.")

        self._cntr_chunk.clear_members()
        self._radi_chunk.clear_members()

        self._cntr_chunk.add_member(sphere.x)
        self._cntr_chunk.add_member(sphere.y)
        self._cntr_chunk.add_member(sphere.z)
        self._radi_chunk.add_member(sphere.r)


class EmptyLODForm(iff.IffForm):
    "An empty LOD. (no geometry)"

    def __init__(self, lod_lev):
        self.lod_lev = lod_lev

        empty_form = iff.IffForm("EMPT")
        form_name = "{!s:0>4}".format(lod_lev)
        super().__init__(form_name, [empty_form])


# ============================== IFF Model File ==============================


class ModelIff(iff.IffFile):
    "Manages the IFF data for a VISION engine 3D model."

    def __init__(self, filename, include_far_chunk):

        if not isinstance(include_far_chunk, bool):
            raise TypeError("include_far_chunk must be a boolean value!")

        # Initialize an empty mesh IFF file, initialize data structures, etc.
        super().__init__("DETA", filename)

        self._num_lods = 0

        self._mrang = iff.IffChunk("RANG")
        self.root_form.add_member(self._mrang)

        self._mlods = iff.IffForm("MESH")
        self.root_form.add_member(self._mlods)

        self._mhard = iff.IffForm("HARD")
        self.root_form.add_member(self._mhard)

        self._mcoll = iff.IffForm("COLL")
        self.root_form.add_member(self._mcoll)

        if include_far_chunk:
            self._mfar = iff.IffChunk("FAR ", [float(0), float(900000)])
            self.root_form.add_member(self._mfar)

    def set_collider(self, collider):
        """Set/replace the collider for this model."""
        if not isinstance(collider, Collider):
            raise TypeError("collider must be a valid Collider in order to "
                            "use it for this model!")

        collform = collider.to_coll_form()
        self.root_form.replace_member(self._mcoll, collform)
        self._mcoll = collform

    def add_hardpt(self, hardpt):
        """Add a hardpoint to this model."""
        if not isinstance(hardpt, Hardpoint):
            raise TypeError("The hardpoint must be a Hardpoint object!")

        self._mhard.add_member(hardpt.to_chunk())

    def remove_hardpt(self, hp_idx):
        "Remove a hardpoint from this model."
        self._mhard.remove_member(hp_idx)

    def remove_hardpts(self):
        "Clear all hardpoints from this model."
        self._mhard.clear_members()

    def add_lod(self, lod, lod_range=0):
        """Add a LOD to this model.

        A LOD can be an empty LOD form, or a LOD mesh form."""
        if isinstance(lod, MeshLODForm) or isinstance(lod, EmptyLODForm):
            if lod.lod_lev >= 0:
                self._mrang.add_member(float(lod_range))
            else:
                raise ValueError("LOD level cannot be negative!")

            if lod_range < 0:
                raise ValueError("LOD range cannot be negative!")

            self._num_lods += 1
            self._mlods.add_member(lod)
        else:
            raise TypeError("A LOD must be an instance of MeshLODForm or"
                            "EmptyLODForm!")

    def set_dranges(self, dranges):
        """Set the LOD ranges for this model.

        Validates the list of LOD ranges before making any changes."""
        if isinstance(dranges, list) or isinstance(dranges, tuple):
            for drange in dranges:
                if not isinstance(drange, float):
                    raise TypeError("Each LOD range must be a float!")
        else:
            raise TypeError("dranges must be a list or tuple!")

        if len(dranges) != self._num_lods:
            raise ValueError("You must have the same number of LOD ranges as "
                             "the number of LODs!")

        if dranges[0] != 0.0:
            raise ValueError("The first LOD range must be 0.")

        for drange in dranges:
            if drange < 0:
                raise ValueError("The LOD ranges must not be negative!")

        self._mrang.clear_members()
        for drange in dranges:
            self._mrang.add_member(drange)

    def set_dranges_force(self, dranges):
        """Set the LOD ranges for this model.

        Does not validate the list of LOD ranges before making any changes. Use
        at your own risk!"""
        if isinstance(dranges, list) or isinstance(dranges, tuple):
            for drange in dranges:
                if not isinstance(drange, float):
                    raise TypeError("Each LOD range must be a float!")
        else:
            raise TypeError("dranges must be a list or tuple!")

        self._mrang.clear_members()
        for drange in dranges:
            self._mrang.add_member(drange)
