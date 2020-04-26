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

import bpy
import struct
import array
from . import iff_read, iff_mesh, mat_read
from mathutils import Matrix
from itertools import starmap, count
from os import sep as dirsep, listdir
from collections import OrderedDict

MAX_NUM_LODS = 7
# MAIN_LOD_NAMES = ["detail-" + str(lod) for lod in range(MAX_NUM_LODS)]
CHLD_LOD_NAMES = ["{{0}}-lod{0:d}".format(lod) for lod in range(MAX_NUM_LODS)]


class ValueWarning(Warning):
    pass


class MaterialManager:

    instance = None
    mfilepath = ""

    def __init__(self):
        self.mtimages = {}  # Texnum -> Blender image
        self.mtexs = {}  # Texnum -> Blender texture
        self.materials = {}  # texnum, lf -> Blender material

    @classmethod
    def set_mfilepath(self, mfilepath):
        self.mfilepath = mfilepath

    @classmethod
    def get_instance(self):
        if self.instance is None:
            self.instance = MaterialManager()
        return self.instance

    def look_for(self, fname, in_dir, par_dir=True):
        from os.path import join, normpath, isfile, isdir
        mfiledir = self.mfilepath[:self.mfilepath.rfind(dirsep)]
        if par_dir:
            abs_dir = normpath(join(mfiledir, ".."))
            dirents = listdir(abs_dir)
            # Enter in_dir
            for dirent in dirents:
                if (dirent.lower() == in_dir.lower() and
                        isdir(join(abs_dir, dirent))):
                    abs_dir = normpath(join(abs_dir, dirent))
                    break
        else:
            # Enter in_dir
            abs_dir = normpath(join(mfiledir, in_dir))

        # Get the file
        dirents = listdir(abs_dir)
        for dirent in dirents:
            if (dirent.lower() == fname.lower() and
                    isfile(join(abs_dir, dirent))):
                return normpath(join(abs_dir, dirent))

    def get_teximg(self, texnum):
        from os.path import join
        if texnum in self.mtimages:
            return self.mtimages[texnum]

        texfname = "{:0>8d}".format(texnum)
        mfiledir = self.mfilepath[:self.mfilepath.rfind(dirsep)]

        # Search directory of mesh file for textures
        img_extns = ("bmp", "png", "jpg", "jpeg", "tga", "gif",
                     "dds", "mat")
        # print("Searching", mfiledir, "for textures...")

        # Look in current directory
        filelist = listdir(mfiledir)
        for extn in img_extns:
            mat_fname = texfname + "." + extn
            # A map object cannot be iterated over more than once.
            fileidx = 0
            for fname in filelist:
                if fname.lower() == mat_fname:
                    mat_fname = join(mfiledir, fname)
                    break
                fileidx += 1
            if fileidx != len(filelist):
                break

            # Look in MAT directory
            mat_fname = self.look_for(mat_fname, "mat")
            if mat_fname is not None:
                break
        else:
            print("Image not found for texture {:0>8d}!".format(texnum))
            self.mtimages[texnum] = None
            return None

        if mat_fname.lower().endswith("mat"):
            mat_reader = mat_read.MATReader(mat_fname)
            mat_reader.read()
            mat_reader.flip_y()
            bl_img = bpy.data.images.new(
                mat_fname[mat_fname.rfind(dirsep):],
                mat_reader.img_width,
                mat_reader.img_height,
                True
            )
            bl_img.pixels = [
                x / 255 for x in mat_reader.pixels]
            self.mtimages[texnum] = bl_img
        else:
            # mat_fname is not a MAT.
            bl_img = bpy.data.images.load(mat_fname)
            self.mtimages[texnum] = bl_img

        return bl_img

    def get_material(self, texnum, light_flags):
        if (texnum, light_flags) in self.materials:
            return self.materials[(texnum, light_flags)]

        texfname = "{:0>8d}".format(texnum)
        bmtl_name = "{}_{}".format(texfname, light_flags)

        bl_mat = bpy.data.materials.new(bmtl_name)
        bl_img = None

        if self.is_flat(texnum):
            # Flat colour material
            bl_mat.diffuse_color = iff_mesh.texnum_colour(texnum)
        else:
            bl_mtexslot = bl_mat.texture_slots.add()
            bl_mtexslot.texture_coords = "UV"
            bl_mtexslot.uv_layer = "UVMap"

            if texnum in self.mtexs:
                bl_mtex = self.mtexs[texnum]
            else:
                bl_mtex = bpy.data.textures.new(texfname, "IMAGE")
                bl_mtex.image = self.get_teximg(texnum)
                self.mtexs[texnum] = bl_mtex
            bl_mtexslot.texture = bl_mtex

        if light_flags == 2:
            bl_mat.use_shadeless = True
        elif light_flags != 0 and light_flags != 2:
            if light_flags & 2 == 2:
                bl_mat.use_shadeless = True
            bl_mat["light_flags"] = light_flags

        self.materials[(texnum, light_flags)] = bl_mat
        return self.materials[(texnum, light_flags)]

    def is_flat(self, texnum):
        return texnum & 0xff000000 == 0x7f000000


class ImportBackend:

    def __init__(self,
                 filepath,
                 texname,
                 reorient_matrix,
                 # import_all_lods=False,
                 # use_facetex=False,
                 import_bsp=False):

        self.mfilepath = filepath
        self.texmats = {}

        self.reorient_matrix = reorient_matrix
        # self.import_all_lods = import_all_lods
        # self.use_facetex = use_facetex
        self.import_bsp = import_bsp
        # self.read_mats = read_mats
        self.dranges = None
        self.lod0_obj = None
        self.lod_meshes = []
        self.base_name = filepath[filepath.rfind(dirsep) + 1:-4]
        MaterialManager.set_mfilepath(filepath)  # Setup MaterialManager


class LODMesh:

    def __init__(self, version, name, vert_data, vtnm_data, fvrt_data,
                 face_data):
        self._name = name
        self.mtlinfo = OrderedDict()
        self.version = version  # Used for FACE struct handling.

        # Vertices
        structlen = 12  # 4 bytes * 3 floats (XYZ)
        structstr = "<fff"
        num_verts = len(vert_data) // structlen
        self._verts = [None] * num_verts
        for idx in range(num_verts):
            self._verts[idx] = struct.unpack_from(
                structstr, vert_data, idx * structlen)

        # Vertex Normals
        structlen = 12  # 4 bytes * 3 floats (XYZ)
        structstr = "<fff"
        num_norms = len(vtnm_data) // structlen
        self._norms = [None] * num_norms
        for idx in range(num_norms):
            self._norms[idx] = struct.unpack_from(
                structstr, vtnm_data, idx * structlen)

        # Face vertices
        structstr = "<iiff"
        structlen = 16  # 4 bytes * (2 ints + 2 floats)
        num_fvrts = len(fvrt_data) // structlen
        self._fvrts = [None] * num_fvrts
        for idx in range(num_fvrts):
            self._fvrts[idx] = struct.unpack_from(
                structstr, fvrt_data, idx * structlen)

        # Faces
        structstr = "<ifiiii" if version >= 11 else "<ifiii"  # No light flags.
        structlen = 28 if version >= 11 else 24  # 4 bytes * (6 ints + 1 float)
        num_faces = len(face_data) // structlen
        self._faces = [None] * num_faces
        for idx in range(num_faces):
            self._faces[idx] = struct.unpack_from(
                structstr, face_data, idx * structlen)

    def set_name(self, name):
        """Set the name of this mesh."""
        self._name = name.strip()

    def edges_from_verts(self, verts):
        """Generates vertex reference tuples for edges."""
        for idx in range(len(verts)):
            first_idx = verts[idx]
            if (idx + 1) >= len(verts):
                next_idx = verts[0]
            else:
                next_idx = verts[idx + 1]
            yield (first_idx, next_idx)

    def to_bl_mesh(self):
        """Take the WC mesh data and convert it to Blender mesh data."""
        matman = MaterialManager.get_instance()
        assert(
            len(self._verts) > 0 and len(self._norms) > 0 and
            len(self._fvrts) > 0 and len(self._faces) > 0 and
            self._name != "")

        bl_mesh = bpy.data.meshes.new(self._name)
        bl_mesh.vertices.add(len(self._verts))

        for vidx, v in enumerate(self._verts):
            bl_mesh.vertices[vidx].co = v
            bl_mesh.vertices[vidx].co[0] *= -1

        face_edge_sets = {}  # The edges (sets of indices of two verts)
        face_edges = array.array("I")  # Same, but as a flat array
        face_edge_counts = array.array("I")  # Edge counts per face
        edge_refs = array.array("I")  # Face edge indices, as pairs per face

        for fidx, f in enumerate(self._faces):
            cur_face_verts = array.array("I")

            for fvrt_ofs in range(f[4]):  # f[4] is number of FVRTS of the face

                cur_fvrt = f[3] + fvrt_ofs  # f[3] is index of first FVRT
                cur_face_verts.append(self._fvrts[cur_fvrt][0])

                bl_mesh.vertices[self._fvrts[cur_fvrt][0]].normal = (
                    self._norms[self._fvrts[cur_fvrt][1]])

                bl_mesh.vertices[self._fvrts[cur_fvrt][0]].normal[0] *= -1

            face_edge_counts.append(len(cur_face_verts))
            cur_face_verts.reverse()

            for ed in self.edges_from_verts(cur_face_verts):
                eset = frozenset(ed)
                if eset in face_edge_sets:
                    eidx = face_edge_sets[eset]
                else:
                    eidx = len(face_edge_sets)
                    face_edge_sets[eset] = eidx
                    face_edges.extend(ed)
                edge_refs.append(eidx)

        edge_count = len(face_edges) // 2
        bl_mesh.edges.add(edge_count)
        for eidx in range(edge_count):
            bl_mesh.edges[eidx].vertices = face_edges[eidx*2:eidx*2+2]

        bl_mesh.polygons.add(len(self._faces))
        bl_mesh.uv_textures.new("UVMap")
        bl_mesh.loops.add(len(edge_refs))
        loop_num = 0

        for fidx, f in enumerate(self._faces):

            cur_face_fvrts = self._fvrts[f[3]:f[3] + f[4]]
            f_verts = [fvrt[0] for fvrt in cur_face_fvrts]
            f_uvs = [
                (fvrt[2], 1 - fvrt[3]) for fvrt in reversed(cur_face_fvrts)]
            f_edgerefi = sum(face_edge_counts[0:fidx])
            f_edgerefc = face_edge_counts[fidx]
            f_edgerefs = edge_refs[f_edgerefi:f_edgerefi+f_edgerefc]
            f_startloop = loop_num

            bl_mesh.polygons[fidx].vertices = f_verts

            if self.version >= 11:
                # f[2] and f[5] are texnum and light flags, respectively.
                visinfo = f[2], f[5]
            else:
                visinfo = f[2], 0

            if visinfo not in self.mtlinfo:
                self.mtlinfo[visinfo] = matman.get_material(*visinfo)
                bl_mesh.materials.append(matman.get_material(*visinfo))
            # Assign corresponding material to polygon
            bl_mesh.polygons[fidx].material_index = (
                list(self.mtlinfo).index(visinfo))
            # Face texture (Visible in Multitexture shading mode)
            if not matman.is_flat(f[2]):
                bl_mesh.uv_textures["UVMap"].data[fidx].image = (
                    matman.get_teximg(f[2]))

            assert(len(f_verts) == len(f_edgerefs) == f[4])

            # print("Face", fidx, "loop_total:", f[4])

            # The edges were generated from a set of vertices in reverse order.
            # Since we're getting the vertices from the FVRTs in forward order,
            # only reverse the vertices.
            for fvidx, vrt, edg in zip(
                    count(), reversed(f_verts), f_edgerefs):
                bl_mesh.loops[loop_num].edge_index = edg
                bl_mesh.loops[loop_num].vertex_index = vrt

                # print("Loop", loop_num, "vertex index:", vrt)
                # print("Loop", loop_num, "edge index:", edg)
                # print("Edge", edg, "vertices",
                #       bl_mesh.edges[edg].vertices[0],
                #       bl_mesh.edges[edg].vertices[1])

                bl_mesh.uv_layers["UVMap"].data[loop_num].uv = (
                    f_uvs[fvidx])
                loop_num += 1

            bl_mesh.polygons[fidx].loop_start = f_startloop
            bl_mesh.polygons[fidx].loop_total = f[4]

        return bl_mesh


class IFFImporter(ImportBackend):

    def read_rang_chunk(self, rang_chunk):
        if rang_chunk["length"] % 4 != 0:
            raise ValueError("RANG chunk has an invalid length!")
        num_dranges = rang_chunk["length"] // 4
        dranges = struct.unpack("<" + ("f" * num_dranges), rang_chunk["data"])
        return dranges

    def parse_major_mesh_form(self, mesh_form):
        mjrmsh_read = 4
        # Read all LODs
        while mjrmsh_read < mesh_form["length"]:
            lod_form = self.iff_reader.read_data()
            lod_lev = int(lod_form["name"].decode("ascii"))

            mnrmsh = self.iff_reader.read_data()
            if mnrmsh["type"] == "form" and mnrmsh["name"] == b"MESH":
                # Mesh LOD form
                self.parse_minor_mesh_form(mnrmsh, lod_lev)
            elif mnrmsh["type"] == "form" and mnrmsh["name"] == b"EMPT":
                # Empty LOD Form - no mesh
                if self.base_name != "":
                    bl_obname = CHLD_LOD_NAMES[lod_lev].format(self.base_name)
                else:
                    bl_obname = "detail-{}".format(lod_lev)
                bl_ob = bpy.data.objects.new(bl_obname, None)
                bpy.context.scene.objects.link(bl_ob)

            mjrmsh_read += 8 + lod_form["length"]
            print("mjrmsh_read:", mjrmsh_read, "of", mesh_form["length"])

    def parse_minor_mesh_form(self, mesh_form, lod_lev=0):
        # lodm = LODMesh()

        mnrmsh_read = 4

        vers_form = self.iff_reader.read_data()
        mesh_vers = int(vers_form["name"].decode("ascii"))
        mnrmsh_read += 12

        print("---------- LOD {} (version {}) ----------".format(
            lod_lev, mesh_vers
        ))

        # Use 28 to skip the "unknown2" value, present in mesh versions 11+
        face_size = 28 if mesh_vers >= 11 else 24
        mesh_name = ""
        vert_data = None
        vtnm_data = None
        fvrt_data = None
        face_data = None
        cntr_data = None
        radi_data = None

        while mnrmsh_read < mesh_form["length"]:
            geom_data = self.iff_reader.read_data()
            mnrmsh_read += 8 + geom_data["length"]
            print("mnrmsh_read:", mnrmsh_read, "of", mesh_form["length"])

            # NORM chunk is ignored

            # Internal name of "minor" mesh/LOD mesh
            if geom_data["name"] == b"NAME":
                mesh_name = self.read_cstring(geom_data["data"], 0)
                if self.base_name == "":
                    self.base_name = mesh_name

            # Vertices
            elif geom_data["name"] == b"VERT":
                vert_data = geom_data["data"]

            # Vertex normals.
            elif geom_data["name"] == b"VTNM" and mesh_vers != 9:
                vtnm_data = geom_data["data"]

            # Vertex normals (mesh version 9).
            elif geom_data["name"] == b"NORM" and mesh_vers == 9:
                vtnm_data = geom_data["data"]

            # Vertices for each face
            elif geom_data["name"] == b"FVRT":
                fvrt_data = geom_data["data"]

            # Face info
            elif geom_data["name"] == b"FACE":
                face_data = geom_data["data"]

            # Center point
            elif geom_data["name"] == b"CNTR":
                cntr_data = geom_data["data"]

            elif geom_data["name"] == b"RADI":
                radi_data = geom_data["data"]

            # print(
            #     "geom length:", geom["length"],
            #     "geom read:", geom_bytes_read,
            #     "current position:", self.iff_file.tell()
            # )

        lodm = LODMesh(mesh_vers, mesh_name, vert_data, vtnm_data,
                       fvrt_data, face_data)
        bl_obname = CHLD_LOD_NAMES[lod_lev].format(self.base_name, lod_lev)
        bl_mesh = lodm.to_bl_mesh()
        bl_mesh.transform(self.reorient_matrix)
        bl_ob = bpy.data.objects.new(bl_obname, bl_mesh)

        if lod_lev == 0:
            self.lod0_obj = bl_ob
        elif lod_lev > 0:
            # Set drange custom property
            try:
                bl_ob["drange"] = self.dranges[lod_lev]
            except IndexError:
                try:
                    del bl_ob["drange"]
                except KeyError:
                    pass

        bpy.context.scene.objects.link(bl_ob)

        # Make and link cntradi object
        cntradi_sph = iff_mesh.Sphere.from_cntradi_chunks(cntr_data, radi_data)
        cntradi_ob = cntradi_sph.to_bl_obj()

        bpy.context.scene.objects.link(cntradi_ob)
        cntradi_ob.parent = bl_ob

    def read_hard_data(self, major_form):
        mjrf_bytes_read = 4
        while mjrf_bytes_read < major_form["length"]:
            hardpt_chunk = self.iff_reader.read_data()
            mjrf_bytes_read += hardpt_chunk["length"] + 8

            hardpt = iff_mesh.Hardpoint.from_chunk(hardpt_chunk["data"])
            bl_ob = hardpt.to_bl_obj()

            bpy.context.scene.objects.link(bl_ob)
            bl_ob.parent = self.lod0_obj

    def read_coll_data(self):
        coll_data = self.iff_reader.read_data()
        if coll_data["name"] == b"SPHR":
            coll_sphere = iff_mesh.Sphere.from_sphr_chunk(coll_data["data"])

            bl_obj = coll_sphere.to_bl_obj("collsphr")
            bpy.context.scene.objects.link(bl_obj)
            bl_obj.parent = self.lod0_obj

    def read_cstring(self, data, ofs):
        cstring = bytearray()
        the_byte = 1
        while the_byte != 0:
            the_byte = data[ofs]
            if the_byte == 0:
                break
            cstring.append(the_byte)
            ofs += 1
        return cstring.decode("iso-8859-1")

    def load(self):
        self.iff_reader = iff_read.IffReader(self.mfilepath)
        root_form = self.iff_reader.read_data()
        if root_form["type"] == "form":
            print("Root form is:", root_form["name"])
            if root_form["name"] == b"DETA":
                mjrfs_read = 4
                while mjrfs_read < root_form["length"]:
                    major_form = self.iff_reader.read_data()
                    mjrfs_read += major_form["length"] + 8
                    # print("Reading major form:", major_form["name"])
                    if major_form["name"] == b"RANG":
                        self.dranges = self.read_rang_chunk(major_form)
                    elif major_form["name"] == b"MESH":
                        self.parse_major_mesh_form(major_form)
                    elif major_form["name"] == b"HARD":
                        self.read_hard_data(major_form)
                    elif major_form["name"] == b"COLL":
                        self.read_coll_data()
                    elif major_form["name"] == b"FAR ":
                        pass  # FAR data is useless to Blender.
                    else:
                        # print("Unknown major form:", major_form["name"])
                        pass

                    # print(
                    #     "root form length:", root_form["length"],
                    #     "root form bytes read:", mjrfs_read
                    # )
            elif root_form["name"] == b"MESH":
                self.parse_minor_mesh_form(root_form)
            else:
                self.iff_reader.close()
                raise TypeError(
                    "This file isn't a mesh! (root form is {})".format(
                        root_form["name"].decode("iso-8859-1")))
        else:
            self.iff_reader.close()
            raise TypeError("This file isn't a mesh! (root is not a form)")
        self.iff_reader.close()
