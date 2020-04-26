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
import mathutils
import warnings
import re
import array
import time
from os import sep as dirsep
from . import iff_mesh
from math import radians
from collections import OrderedDict
from itertools import repeat, starmap

LFLAG_UNKNOWN1 = 1
LFLAG_FULLBRIGHT = 2
LFLAG_UNKNOWN2 = 8

# Name pattern for LOD objects. Largely deprecated in favour of named LOD
# object models. Mostly present for backwards compatibility.
# Group 1 is the prefix.
# Group 2 is the LOD level number.
# Group 3 is the suffix.
MAIN_LOD_RE = re.compile(r"^(detail-?)(\d+)(\.\d+)?$")

# Name pattern for LOD objects, grouped by name.
# Group 1 is the prefix object name.
# Group 2 is the LOD level number.
# Group 3 is the suffix.
CHLD_LOD_RE = re.compile(r"^([\w#]+-lod)(\d+)(\.\d+)?$")

# Name pattern for hardpoints. Group 1 is the hardpoint name, group 2 is
# the suffix appended by Blender to objects with conflicting names.
HARDPOINT_RE = re.compile(r"^hp-(\w+)(?:\.\d*)?$")

# One of the asteroid models I've looked at (AST_G_01.IFF) has 7 LODs
MAX_NUM_LODS = 7

# Non-critical warnings will be reported to Blender. Critical errors will be
# exceptions.


class KeyWarning(Warning):
    pass


class TypeWarning(Warning):
    pass


class ValueWarning(Warning):
    pass


class ModelManager:
    # Manages the LODs for a mesh to export.
    # Each instance of this class should be exportable to a mesh IFF.
    # Scans for a base LOD mesh and other related LODs in a given scene.

    # Name pattern for LOD range info. Group 1 is the range, group 2 is the
    # suffix appended by Blender to objects with conflicting names.
    DRANGE_RE = re.compile(r"^drang=([0-9,]+)(?:\.\d*)?$")

    # prefix for CNTR/RADI spheres
    CNTRADI_PFX = "cntradi"

    # prefix for spherical collider definition objects
    COLLSPHR_PFX = "collsphr"

    # prefix for BSP collider definition objects
    COLLMESH_PFX = "collmesh"

    # Transformation to convert hardpoints to WC orientation.
    HP_WC_XFM = mathutils.Euler((radians(90), 0, radians(180)), "XYZ")

    def __init__(self, base_name, base_obj, use_facetex, drang_increment,
                 far_chunk, modeldir, gen_bsp, scene_name, wc_matrix,
                 test_run):

        if not isinstance(base_name, str):
            raise TypeError("Model name must be a string!")
        if scene_name not in bpy.data.scenes:
            raise TypeError("scene must be the name of a Blender scene!")
        if base_obj not in bpy.data.scenes[scene_name].objects:
            raise TypeError("base_obj must be the name of a Blender mesh "
                            "object in the given scene!")

        self.scene = scene_name  # Name of the scene to use
        # self.base_name = base_name
        self._exp_fname = base_name  # Export filename
        # self.name_scheme = 0  # See LOD_NSCHEME constants above
        self.modelname = base_name  # Model name (NAME chunk, ex. "Duhiky")
        self.modeldir = modeldir  # Folder to write the model file in.

        # Reorientation matrix (Blender -> VISION coordinates)
        self.wc_matrix = wc_matrix

        # Base object stuff
        self.base_obj = base_obj  # Name of base object (ex. "Duhiky-lod0")
        self.base_prefix = ""  # Prefix before LOD level number.
        self.base_suffix = ""  # Object name suffix (.000, .001, etc.)
        self.base_parent = str(
            bpy.data.scenes[scene_name].objects[base_obj].parent)
        self.base_lod = self._get_lod(base_obj, True)  # Get base object LOD

        # Names of LOD objects
        self.lods = [None for x in range(MAX_NUM_LODS)]
        self.lodms = []  # LOD object meshes (converted from objects)
        self.lods[self.base_lod] = base_obj
        self.lod_empty = [False for x in range(MAX_NUM_LODS)]  # Empty LODs

        # Hardpoint stuff
        self.hardpoints = []  # Hardpoints
        self.hpobnames = []  # Hardpoint Blender object names

        # LOD ranges (RANG chunk)
        self.dranges = [None for x in range(MAX_NUM_LODS)]
        self.dranges[0] = 0.0
        self.drang_increment = drang_increment
        self.far_chunk = far_chunk

        # CNTR/RADI spheres for each LOD.
        self.dsphrs = [None for x in range(MAX_NUM_LODS)]
        # Collider (Collision sphere/BSP stuff)
        self.gen_bsp = gen_bsp
        self.collider = None  # COLL form

        # Material/texture stuff
        self.use_mtltex = not use_facetex
        self.mtltexs = OrderedDict()  # Material -> texnum dict
        self.image_txns = OrderedDict()  # Images used by face textures.

        # Misc fields
        self.test_run = test_run
        self.setup_complete = False

    def _get_lod(self, lod_obj, base=False):
        lod_match = MAIN_LOD_RE.match(lod_obj)
        if lod_match:
            if base:
                # self.name_scheme = self.LOD_NSCHEME_DETAIL
                self.base_prefix = lod_match.group(1)
                self.base_suffix = lod_match.group(3) or ""
                # if self.base_suffix is None: self.base_suffix = ""
                warnings.warn("detail-x LOD naming scheme is deprecated.",
                              DeprecationWarning)
            lod_lev = int(lod_match.group(2))
            return lod_lev

        lod_match = CHLD_LOD_RE.match(lod_obj)
        if lod_match:
            if base:
                # self.name_scheme = self.LOD_NSCHEME_CHLD
                base_prefix = lod_match.group(1)
                self.modelname = base_prefix[:base_prefix.rindex("-")]
                self.base_prefix = base_prefix
                self.base_suffix = lod_match.group(3) or ""
            lod_lev = int(lod_match.group(2))
            return lod_lev

        # Assume LOD 0, and "child" LOD naming scheme
        if base:
            if self.modelname.rfind(".") > 0:
                self.base_suffix = self.modelname[self.modelname.rfind("."):]
                self.modelname = self.modelname[:self.modelname.rfind(".")]
            self.base_prefix = self.modelname + "-lod"
        return 0

    def texs_for_mtl(self, material):
        if not isinstance(material, bpy.types.Material):
            raise TypeError("You must provide a Blender material in order to "
                            "get its valid textures!")

        filled_slots = 0
        valid_slots = []
        for ts in material.texture_slots:
            if ts is not None:
                filled_slots += 1
                if (isinstance(ts, bpy.types.MaterialTextureSlot) and
                    ts.texture_coords == "UV" and
                    isinstance(ts.texture, bpy.types.ImageTexture) and
                        ts.texture.image is not None):
                    valid_slots.append(ts.texture)

        if filled_slots > 0 and len(valid_slots) == 0:
            raise ValueError(
                "Found no valid texture slots for the material '{}' out of "
                "the ones that were filled! In order for a texture slot to be "
                "valid, it must be a UV-mapped image texture."
                .format(material.name))

        return valid_slots

    def setup(self):
        print(banner(self.modelname))
        # Scan for valid LOD objects related to the base LOD object
        for lod in range(MAX_NUM_LODS):
            lod_name = "{}{}{}".format(self.base_prefix, lod, self.base_suffix)

            lobj = None
            try:
                lobj = bpy.data.scenes[self.scene].objects[lod_name]
            except KeyError:
                lobj = None
                if lod > 0:
                    del self.dranges[-1]
                    del self.dsphrs[-1]
                    del self.lod_empty[-1]
            if lobj is not None and lod_name != self.base_obj:
                if self.lods[lod] is None:
                    if lobj.type == "MESH" or lobj.type == "EMPTY":
                        if lobj.hide is False:

                            if str(lobj.parent) != self.base_parent:
                                raise ValueError(
                                    "LOD {} ({}) has a different parent than "
                                    "LOD {} ({})!".format(
                                        lod, lobj,
                                        self.base_lod, self.base_parent))

                            self.lods[lod] = lod_name
                        else:
                            # Don't export hidden LODs.
                            del self.dranges[-1]
                            del self.dsphrs[-1]
                            del self.lod_empty[-1]

                    else:
                        raise TypeError("Object {} is not a mesh or empty!"
                                        .format(lod_name))
                else:
                    raise ValueError(
                        "Tried to set LOD {} to object {}, but it was already "
                        "set to object {}!".format(lod, lod_name,
                                                   self.lods[lod]))

        # Ensure the LODs array is consistent
        if self.lods[0] is None:
            raise TypeError("The first LOD (LOD 0) of the model must exist!")

        no_lod_idx = None  # Index for first blank LOD

        for lod_idx, lod_obj in enumerate(self.lods):
            if no_lod_idx is None:
                if lod_obj is None:
                    no_lod_idx = lod_idx
            else:
                if lod_obj is not None:
                    raise TypeError(
                        "Inconsistent LODs. A LOD object was found after lod "
                        "{} ({}).".format(no_lod_idx, lod_obj))

        if no_lod_idx is not None:
            self.lods = self.lods[:no_lod_idx]

        del no_lod_idx

        print("LOD object names:", self.lods)

        # The collider for the lowest (most detailed) LOD takes precedence over
        # colliders for other LODs, and a model can only have one collider.
        collider_lod = MAX_NUM_LODS + 1

        # LOD ranges can be either a custom property of the LOD object, or the
        # name of an empty object parented to said LOD object. The custom
        # property takes precedence, however.
        drange_prop = [False for x in range(len(self.lods))]

        for lod, lobj_name in enumerate(self.lods):
            cur_lobj = bpy.context.scene.objects[lobj_name]
            if lod > 0:  # LOD Range custom property 'drange'
                drange = cur_lobj.get("drange")
                if drange is not None:
                    self.dranges[lod] = drange
                    drange_prop[lod] = True
            for cobj in cur_lobj.children:
                if cobj.type == "EMPTY" and cobj.hide is False:

                    if self.DRANGE_RE.match(cobj.name) and lod > 0:
                        # LOD Range object
                        if drange_prop[lod] is False:
                            drange = self.DRANGE_RE.match(cobj.name).group(1)
                            # A comma is used in place of a period in the
                            # drange object name because Blender likes to add
                            # .000, .001, etc. to objects with duplicate names.
                            drange = float(drange.translate({44: 46}))
                            self.dranges[lod] = drange

                    elif (cobj.name.lower().startswith(self.CNTRADI_PFX) and
                          cobj.empty_draw_type == "SPHERE"):
                        # CNTR/RADI object
                        cntr_vec = cobj.location.copy()
                        cntr_vec.rotate(self.wc_matrix)
                        x, y, z = cntr_vec
                        x *= -1
                        self.dsphrs[lod] = iff_mesh.Sphere(
                            x, z, y, max(cobj.scale)
                        )

                    elif (cobj.name.lower().startswith(self.COLLSPHR_PFX) and
                          cobj.empty_draw_type == "SPHERE"):
                        # COLLSPHR object
                        if lod < collider_lod:
                            cntr_vec = cobj.location.copy()
                            cntr_vec.rotate(self.wc_matrix)
                            x, y, z = cntr_vec
                            x *= -1
                            self.collider = iff_mesh.Collider(
                                "sphere",
                                iff_mesh.Sphere(x, z, y, max(cobj.scale))
                            )
                            collider_lod = lod

                    elif HARDPOINT_RE.match(cobj.name):
                        # Hardpoint object
                        hp_name = HARDPOINT_RE.match(cobj.name).group(1)
                        hp_euler = cobj.rotation_euler.copy()
                        hp_euler.rotate(self.wc_matrix)
                        hp_euler.rotate(self.HP_WC_XFM)
                        hp_euler.x *= -1
                        hp_euler.y, hp_euler.z = -hp_euler.z, -hp_euler.y
                        hp_matrix = hp_euler.to_matrix()
                        hp_loc = cobj.location.copy()
                        hp_loc.rotate(self.wc_matrix)
                        hp_loc.x *= -1
                        hardpt = iff_mesh.Hardpoint(hp_matrix, hp_loc, hp_name)
                        self.hardpoints.append(hardpt)
                        self.hpobnames.append(cobj.name)

        del collider_lod
        del drange_prop

        print("dranges (b4):", self.dranges)

        # Fill in blank LOD ranges
        for dr_idxa in range(len(self.dranges)):
            if self.dranges[dr_idxa] is None:
                drange_before = self.dranges[dr_idxa - 1]
                empty_dranges = 0

                # Find closest value for drange_after
                for dr_idxb in range(dr_idxa, len(self.dranges)):
                    if self.dranges[dr_idxb] is not None:
                        break
                    else:
                        empty_dranges += 1

                try:
                    drange_after = self.dranges[dr_idxa + empty_dranges]
                except IndexError:
                    # There's no known detail ranges after this one,
                    # so generate them
                    drange_after = (self.drang_increment *
                                    (empty_dranges + 1) + drange_before)

                if drange_after < drange_before:
                    raise ValueError("Each detail range must be greater than "
                                     "the one before it!")

                # Find interval and index of last detail range
                drange_interval = (
                    (drange_after - drange_before) /
                    (empty_dranges + 1))

                dridx_end = dr_idxa + empty_dranges

                # Fill in the missing values
                # Best list comprehension ever LOL.
                self.dranges[dr_idxa:dridx_end] = [
                    x * n + drange_before for x, n in zip(
                        repeat(drange_interval, empty_dranges),
                        range(1, empty_dranges + 1)
                    )]

        print("dranges (after):", self.dranges)

        # Generate CNTR/RADI data for each LOD where it does not exist.
        for lod_idx in range(len(self.dsphrs)):
            if self.dsphrs[lod_idx] is None:
                lod_obj = (bpy.data.scenes[self.scene]
                           .objects[self.lods[lod_idx]])

                dsphr_vec = lod_obj.location.copy()
                dsphr_vec.rotate(self.wc_matrix)

                x, y, z = dsphr_vec
                x *= -1
                r = max(lod_obj.dimensions) / 2
                self.dsphrs[lod_idx] = iff_mesh.Sphere(x, z, y, r)

            print("LOD {} CNTR/RADI: {}".format(lod_idx, self.dsphrs[lod_idx]))

        # Ensure there are no hardpoint name conflicts
        hpnames = []
        for hp in self.hardpoints:
            if hp.name in hpnames:
                raise ValueError(
                    "Two or more hardpoints of the object {} have the same "
                    "name ({})! (Hardpoint name is stripped of numeric "
                    "suffix)".format(self.modelname, hp.name))
            hpnames.append(hp.name)
        del hpnames

        print("========== Hardpoints ==========")
        for hp, hpob in zip(self.hardpoints, self.hpobnames):
            print(hp, ": ({})".format(hpob))

        # Generate the collider for this model if it doesn't exist.
        if self.collider is None:
            lod_obj = bpy.data.scenes[self.scene].objects[self.lods[0]]
            coll_vec = lod_obj.location.copy()
            coll_vec.rotate(self.wc_matrix)

            x, y, z = coll_vec
            x *= -1
            r = max(lod_obj.dimensions) / 2
            self.collider = iff_mesh.Collider(
                "sphere", iff_mesh.Sphere(x, z, y, r)
            )

        print("Collider:", self.collider)

        # Convert all LOD objects to meshes to populate the LOD mesh list.
        for lidx, lod in enumerate(self.lods):
            try:
                self.lodms.append(
                    bpy.data.scenes[self.scene].objects[lod].to_mesh(
                        bpy.data.scenes[self.scene], True, "PREVIEW")
                )
            except RuntimeError:
                print("Object {} is an empty.".format(lod))
                self.lod_empty[lidx] = True

        # Get the textures used by all LODs for this model
        used_materials = []
        for lodm in self.lodms:
            lodm.transform(self.wc_matrix.to_4x4())
            lodm.calc_normals()
            lodm.calc_tessface()
            # tf_mtl = None  # The material for this tessface
            # tf_mlf = 0  # The light flags for this tessface
            # tf_mtf = False  # Is the material a flat colour
            for tf in lodm.tessfaces:
                # Ensure material for this face exists
                try:
                    tf_mtl = lodm.materials[tf.material_index]
                except IndexError:
                    raise ValueError("You must have a valid material "
                                     "assigned to each face!")

                if tf_mtl not in used_materials:
                    used_materials.append(tf_mtl)

        # Get information about materials.
        for tf_mtl in used_materials:

            # Get light flags for this material
            tf_mlf = 0
            if tf_mtl.get("light_flags") is not None:
                tf_mlf = int(tf_mtl.get("light_flags"))
            elif tf_mtl.use_shadeless:
                tf_mlf |= LFLAG_FULLBRIGHT

            tf_mtexs = self.texs_for_mtl(tf_mtl)  # Valid texture slots

            if len(tf_mtexs) == 0 or not self.use_mtltex:
                # Flat colour material; Use the colour of the material.
                tf_img = iff_mesh.colour_texnum(tf_mtl.diffuse_color)
            else:
                # Textured material; Use first valid texture slot.
                tf_img = tf_mtexs[0].image.filepath

            tf_txnm = tf_img if isinstance(tf_img, int) else None

            mtldata = [tf_mlf, tf_img, tf_txnm]
            if tf_mtl.name not in self.mtltexs:
                self.mtltexs[tf_mtl.name] = mtldata

        del used_materials

        if not self.use_mtltex:
            for lodm in self.lodms:
                for tf, tfuv in zip(lodm.tessfaces,
                                    lodm.tessface_uv_textures.active.data):
                    if (tfuv.image is not None and tfuv.image.filepath not in
                            self.image_txns):
                        self.image_txns[tfuv.image.filepath] = None

        print("Materials used by this model:")
        for mtl, mtx in self.mtltexs.items():
            print("{}: {} (Light flags: {})".format(mtl, mtx[1], mtx[0]))

        self.setup_complete = True

    def get_materials(self):
        if not self.setup_complete:
            raise ValueError("You must set the model up first!")

        if self.use_mtltex:
            used_textures = []
            for mtex in self.mtltexs.values():
                if (not isinstance(mtex[1], int) and
                        mtex[1] not in used_textures):
                    used_textures.append(mtex[1])

            return used_textures
        else:
            return self.image_txns.keys()

    def mtls_for_img(self, img_fname):
        for mtl, mtldata in self.mtltexs.items():
            if img_fname == mtldata[1]:
                yield mtl

    def assign_mtltxns(self, mtltxns):
        print("Assigning texture numbers to {}...".format(self.modelname))
        if self.use_mtltex:
            for img, txnm in mtltxns.items():
                for mtl in self.mtls_for_img(img):
                    print("Assigning {} to {}...".format(txnm, mtl))
                    self.mtltexs[mtl][2] = txnm
        else:
            for img, txnm in mtltxns.items():
                if img in self.image_txns.keys():
                    print("Assigning {} to {}...".format(txnm, img))
                    self.image_txns[img] = txnm

    def calc_dplane(self, vert, facenrm):
        """Calculate the D-Plane of the face.

        vert refers to the first vertex of the face
        facenrm refers to the face normal
        The D-Plane is used by the VISION engine for backface culling
        Thanks to gr1mre4per from CIC for the algorithm!
        """
        dplane = -((facenrm[0] * vert[0]) +
                   (facenrm[1] * vert[1]) +
                   (facenrm[2] * vert[2]))
        return dplane

    @property
    def exp_fname(self):
        """The export filename.

        The model is written to disk with this filename, suffixed by '.iff'
        For example, if the export filename is 'Duhiky', the file for this
        model will be 'Duhiky.iff'"""
        return self._exp_fname

    @exp_fname.setter
    def exp_fname(self, value):
        if not isinstance(value, str):
            raise TypeError("Export filename must be a string!")

        self._exp_fname = value

    @exp_fname.deleter
    def exp_fname(self):
        self._exp_fname = self.modelname

    def export(self):
        modelfile = iff_mesh.ModelIff(self.modeldir + dirsep + self._exp_fname,
                                      self.far_chunk)

        modelfile.set_collider(self.collider)
        for hardpt in self.hardpoints:
            modelfile.add_hardpt(hardpt)

        for drange, lodi in zip(self.dranges, range(len(self.lods))):
            if self.lod_empty[lodi] is False:
                ilodm = iff_mesh.MeshLODForm(lodi)
                ilodm.set_name(self.modelname)
                ilodm.set_cntradi(self.dsphrs[lodi])

                cur_lodm = self.lodms[lodi]

                for vert in cur_lodm.vertices:
                    ilodm.add_vertex(vert.co.x * -1, vert.co.y, vert.co.z)

                unique_normals = {}
                norm_idx = 0
                fvrt_idx = 0
                for tf, tfuv in zip(
                        cur_lodm.tessfaces,
                        cur_lodm.tessface_uv_textures.active.data):

                    # Get vertex normals. This depends on whether or not the
                    # faces are smooth or flat shaded.
                    if tf.use_smooth:
                        # Smooth - use individual vertex normals
                        for vert in tf.vertices:
                            nx, ny, nz = cur_lodm.vertices[vert].normal
                            nx *= -1
                            vnrm = array.array("f", (nx, ny, nz)).tobytes()
                            if vnrm not in unique_normals:
                                unique_normals[vnrm] = norm_idx
                                ilodm.add_vert_normal(nx, ny, nz)
                                norm_idx += 1

                    # Flat - use face normal. This normal will be added anyway,
                    # since it is referenced by the FACE chunk.
                    nx, ny, nz = tf.normal
                    nx *= -1
                    fnrm = array.array("f", (nx, ny, nz)).tobytes()
                    if fnrm not in unique_normals:
                        unique_normals[fnrm] = norm_idx
                        ilodm.add_face_normal(nx, ny, nz)
                        norm_idx += 1

                    # Add the FVRTs for the face
                    uv_idx = len(tf.vertices) - 1
                    for fvrt in reversed(tf.vertices):
                        vtnm_idx = None
                        if tf.use_smooth:
                            nx, ny, nz = cur_lodm.vertices[fvrt].normal
                            nx *= -1
                            vnrm = array.array("f", (nx, ny, nz)).tobytes()
                            vtnm_idx = unique_normals[vnrm]
                        else:
                            nx, ny, nz = tf.normal
                            nx *= -1
                            vnrm = array.array("f", (nx, ny, nz)).tobytes()
                            vtnm_idx = unique_normals[vnrm]
                        ilodm.add_fvrt(fvrt, vtnm_idx, tfuv.uv[uv_idx][0],
                                       1 - tfuv.uv[uv_idx][1])
                        uv_idx -= 1
                    del uv_idx

                    # Get the texnum and light flags
                    if self.use_mtltex:
                        texnum = self.mtltexs[
                            cur_lodm.materials[tf.material_index].name][2]
                    else:
                        if tfuv.image is not None:
                            texnum = self.image_txns[tfuv.image.filepath]
                        else:
                            # This should be a flat colour
                            texnum = self.mtltexs[
                                cur_lodm.materials[tf.material_index].name][2]
                    light_flags = self.mtltexs[
                        cur_lodm.materials[tf.material_index].name][0]

                    first_vert = cur_lodm.vertices[tf.vertices[-1]].co.copy()
                    first_vert.x *= -1

                    face_nrm = tf.normal.copy()
                    face_nrm.x *= -1

                    # Add the face
                    ilodm.add_face(
                        unique_normals[fnrm],
                        self.calc_dplane(first_vert, face_nrm),
                        texnum, fvrt_idx, len(tf.vertices), light_flags)
                    fvrt_idx += len(tf.vertices)
            else:
                ilodm = iff_mesh.EmptyLODForm(lodi)

            modelfile.add_lod(ilodm, drange)
        if not self.test_run:
            modelfile.write_file_bin()


class ExportBackend:

    def __init__(self,
                 filepath,
                 start_texnum=22000,
                 apply_modifiers=True,
                 export_active_only=True,
                 use_facetex=False,
                 wc_matrix=None,
                 include_far_chunk=True,
                 drang_increment=500.0,
                 generate_bsp=False,
                 test_run=False):
        self.filepath = filepath
        self.start_texnum = start_texnum
        self.apply_modifiers = apply_modifiers
        self.export_active_only = export_active_only
        self.use_facetex = use_facetex
        self.wc_matrix = wc_matrix
        self.include_far_chunk = include_far_chunk
        self.drang_incval = drang_increment
        self.generate_bsp = generate_bsp
        self.test_run = test_run
        self.modelname = ""

    def get_texnums(self, textures):
        """Convert all of the named textures to texture numbers.

        Returns a mapping from texture filenames to texture numbers."""
        RE_NUMERIC_TX = re.compile(r"\b(\d{1,8})(?:\.\w+)?$")

        # Keep track of which textures are numeric, and which ones are not.
        numeric_txs = [None for x in range(len(textures))]

        # Associate each texture filename with a texture number,
        # beginning at the user's specified starting texture number.
        texnums = OrderedDict()
        last_txnum = self.start_texnum

        # See which numeric textures are being used.
        for idx, txfname in enumerate(textures):
            numtx_match = RE_NUMERIC_TX.search(txfname)
            if numtx_match:
                numeric_txs[idx] = int(numtx_match.group(1))

        for idx, txfname in enumerate(textures):
            if numeric_txs[idx] is not None:
                texnums[txfname] = numeric_txs[idx]
            else:
                curr_txnum = last_txnum
                while curr_txnum in numeric_txs:
                    curr_txnum += 1
                texnums[txfname] = curr_txnum
                last_txnum = curr_txnum + 1

        return texnums

    def fmt_txinfo(self, mtl_texnums, as_comment=False):
        """Gets a string showing the Image Filename->Texture number"""
        # Used to make the Image Filename->Material Number list
        # easier to read.
        # max_width = len(max(mtl_texnums.keys(), key=len))
        # Print Image Filename->Material Number information for the
        # user to use as a guide for converting textures.
        tx_info = ""
        for img_fname, texnum in sorted(
                mtl_texnums.items(),
                key=lambda mattex: mattex[1]):
            if as_comment:
                tx_info += "// "
            maxlen = max(map(len, mtl_texnums.keys()))
            tx_info += (
                "{:" + str(maxlen) +
                "} --> {!s:0>8}.mat\n").format(img_fname, texnum)
        return tx_info


class HierarchyManager:
    """A valid object, and its valid children."""

    def __init__(self, root_obj, modelname, modeldir, use_facetex, far_chunk,
                 drang_increment, generate_bsp, scene_name, wc_matrix,
                 test_run):

        self.root_obj = root_obj
        self.root_lods = self.lods_of(root_obj.name)

        self.modelname = modelname  # The filename the user specified.
        self.modeldir = modeldir
        self.use_facetex = use_facetex
        self.far_chunk = far_chunk
        self.drang_incval = drang_increment
        self.generate_bsp = generate_bsp
        self.scene_name = scene_name
        self.wc_matrix = wc_matrix
        self.test_run = test_run
        self.managers = []
        self.mgrtexs = []

        self.main_lods_used = set()
        self.hierarchy_objects = self.get_children(root_obj)

    def is_valid_obj(self, obj, parent=None):
        """Ensure the object in question is valid for exporting.

        In order for an object to be exportable, it must:
        1. Have the given parent.
        2. Be named such that MAIN_LOD_RE or CHLD_LOD_RE matches its name.
        3. Be visible in Blender's viewport."""
        if not (str(obj.parent) == str(parent) and obj.hide is False and
                (obj.type == "MESH" or obj.type == "EMPTY")):
            return False

        if CHLD_LOD_RE.match(obj.name):
            return True
        elif MAIN_LOD_RE.match(obj.name):
            lod_lev = int(MAIN_LOD_RE.match(obj.name).group(2))
            if lod_lev in self.main_lods_used:
                raise ValueError("You cannot have more than one detail-x "
                                 "object in a hierarchy tree!")
            elif len(self.main_lods_used) > 0:
                return False
            self.main_lods_used.add(lod_lev)
            print("main_lods_used:", self.main_lods_used)
            return True

    def lods_of(self, obj_name, root=False):
        """Gets the names of the LOD objects for the object with the given
        name."""

        main_match = MAIN_LOD_RE.match(obj_name)
        if main_match:
            prefix = main_match.group(1)
            suffix = main_match.group(3) or ""
            return ["{}{}{}".format(prefix, lod, suffix)
                    for lod in range(MAX_NUM_LODS)]

        chld_match = CHLD_LOD_RE.match(obj_name)
        if chld_match:
            prefix = chld_match.group(1)
            suffix = chld_match.group(3) or ""
            return ["{}{}{}".format(prefix, lod, suffix)
                    for lod in range(MAX_NUM_LODS)]

        if root:
            prefix = "{}-lod".format(obj_name)
            rv = ["{}{}".format(prefix, lod)
                  for lod in range(1, MAX_NUM_LODS)]
            rv.insert(0, obj_name)
            return rv
        else:
            return None

    def get_children(self, obj):
        """Get a list of the object, and all of its exportable children."""
        # List containing an object and its children.
        objects = [obj]
        obj_main = MAIN_LOD_RE.match(obj.name)
        if obj_main:
            self.main_lods_used.add(int(obj_main.group(2)))

        def is_valid_hp(obj, parent=None):
            return (str(obj.parent) == str(parent) and obj.hide is False and
                    obj.type == "EMPTY" and HARDPOINT_RE.match(obj.name))

        def children_of(parent_obj, root):
            """Get the valid child objects for a parent object.

            Child objects may be parented directly to the object, or to one of
            the hardpoints."""
            childnames = []
            children = []
            parent_hps = []
            parent_lods = self.lods_of(parent_obj.name, root)
            parent_lobjs = [None for lod in range(len(parent_lods))]
            for lod in reversed(range(len(parent_lobjs))):
                try:
                    parent_lobjs[lod] = (
                        bpy.data.scenes[self.scene_name]
                        .objects[parent_lods[lod]])
                except KeyError:
                    del parent_lobjs[lod]

            del parent_lods
            # print("[L787] parent_lobjs:", parent_lobjs)

            for plobj in parent_lobjs:
                for obj in plobj.children:
                    if self.is_valid_obj(obj, plobj):
                        obj_bname = CHLD_LOD_RE.match(obj.name)
                        if obj_bname:
                            obj_bname = obj_bname.group(1)
                        else:
                            obj_bname = self.modelname
                        if obj_bname not in childnames:
                            childnames.append(obj_bname)
                            children.append(obj)
                    if is_valid_hp(obj, plobj) and obj not in parent_hps:
                        parent_hps.append(obj)

            for hp in parent_hps:
                for obj in hp.children:
                    if self.is_valid_obj(obj, hp):
                        obj_bname = CHLD_LOD_RE.match(obj.name)
                        if obj_bname:
                            obj_bname = obj_bname.group(1)
                        else:
                            obj_bname = self.modelname
                        if obj_bname not in childnames:
                            childnames.append(obj_bname)
                            children.append(obj)

            if len(children) == 0:
                return children
            else:
                for obj in children:
                    children.extend(children_of(obj, False))

                return children

        objects.extend(children_of(obj, True))

        return objects

    def hierarchy_str_for(self, obj):
        """Get the export filename for the object.

        This function should be called after objects have been selected for
        export."""

        def parents_of(obj):
            rv = [obj]

            if (obj.name == self.root_obj.name):
                return rv

            elif (obj.parent is not None and (obj.parent.type == "MESH" or
                  obj.parent.type == "EMPTY") and
                  (MAIN_LOD_RE.match(obj.parent.name) or
                   CHLD_LOD_RE.match(obj.parent.name)) and
                  obj.parent.hide is False):
                rv.extend(parents_of(obj.parent))

            elif (obj.parent is not None and obj.parent.type == "EMPTY" and
                  HARDPOINT_RE.match(obj.parent.name) and
                  obj.parent.hide is False):
                rv.extend(parents_of(obj.parent.parent))

            return rv

        def name_of(obj, first):
            if obj is not None:
                obj_ch_name = CHLD_LOD_RE.match(obj.name)

                if MAIN_LOD_RE.match(obj.name):
                    return self.modelname

                elif obj_ch_name:
                    if (first and obj.name in self.root_lods and
                            not self.main_lods_used):
                        return self.modelname
                    else:
                        obj_mname = obj_ch_name.group(1)
                        obj_mname = obj_mname[:obj_mname.rindex("-")]
                        return obj_mname

                else:
                    if first:
                        return self.modelname
                    obj_mname = obj.name
                    if obj_mname.rfind(".") > 0:
                        return obj_mname[:obj_mname.rfind(".")]
                    else:
                        return obj_mname

        if obj.parent is not None:
            hierarchy = parents_of(obj)
            hierarchy = [(ob, idx == 0) for idx, ob in
                         enumerate(reversed(hierarchy))]
            return "_".join(starmap(name_of, hierarchy))
        else:
            return name_of(obj, True)

    def setup(self):
        for hobj in self.hierarchy_objects:
            cur_manager = ModelManager(
                self.modelname, hobj.name, self.use_facetex,
                self.drang_incval, self.far_chunk, self.modeldir,
                self.generate_bsp, self.scene_name, self.wc_matrix,
                self.test_run)
            cur_manager.exp_fname = self.hierarchy_str_for(hobj)
            print("Export filename for {}: {}.iff".format(
                hobj.name, cur_manager.exp_fname))
            self.managers.append(cur_manager)

        for manager in self.managers:
            manager.setup()

        self.mgrtexs = [mgr.get_materials() for mgr in self.managers]

    def get_materials(self):
        mats = []

        # Flatten matlsts
        for mtlst in self.mgrtexs:
            for mat in mtlst:
                if mat not in mats:
                    mats.append(mat)

        return mats

    def assign_mtltxns(self, mtltxns):
        for manager in self.managers:
            manager.assign_mtltxns(mtltxns)

    def export(self):
        for manager in self.managers:
            manager.export()


class IFFExporter(ExportBackend):

    def export(self):
        """
        Export .iff files from the Blender scene.
        The model is exported as an .iff file, which can be used in
        Wing Commander: Prophecy/Secret Ops.

        Preconditions for a model to be exported:
        1. It must be named according to MAIN_LOD_RE or CHLD_LOD_RE
        2. All of its LODs must be Blender mesh objects.
        3. It must have a LOD 0
        4. All LODs that are to be exported, especially LOD 0, must be visible
           in Blender's viewport.
        """
        export_start = time.perf_counter()

        # Get directory path of output file, plus filename without extension
        modeldir = self.filepath[:self.filepath.rfind(dirsep)]
        modelname = bpy.path.display_name_from_filepath(self.filepath)

        managers = []
        used_materials = []
        used_names = set()

        if self.export_active_only:
            if bpy.context.active_object is None:
                raise TypeError("You must have an object selected to export "
                                "only the active object!")

            managers.append(HierarchyManager(
                bpy.context.active_object, modelname, modeldir,
                self.use_facetex, self.include_far_chunk, self.drang_incval,
                self.generate_bsp, bpy.context.scene.name,
                self.wc_matrix, self.test_run))

        else:
            for obj in bpy.context.scene.objects:
                if obj.parent is None and not obj.hide:
                    if MAIN_LOD_RE.match(obj.name):
                        managers.append(HierarchyManager(
                            obj, modelname, modeldir, self.use_facetex,
                            self.include_far_chunk, self.drang_increment,
                            self.generate_bsp, bpy.context.scene.name,
                            self.wc_matrix, self.test_run
                        ))
                        warnings.warn("detail-x LOD naming scheme is "
                                      "deprecated.", DeprecationWarning)
                    else:
                        obj_match = CHLD_LOD_RE.match(obj.name)
                        if obj_match.group(1) not in used_names:
                            managers.append(HierarchyManager(
                                obj, modelname, modeldir, self.use_facetex,
                                self.include_far_chunk, self.drang_increment,
                                self.generate_bsp, bpy.context.scene.name,
                                self.wc_matrix, self.test_run
                            ))
                            used_names.add(obj_match.group(1))

        for manager in managers:
            manager.setup()
            for mngr_mat in manager.get_materials():
                if mngr_mat not in used_materials:
                    used_materials.append(mngr_mat)
        print(banner("Texture images for all models that will be exported:"))
        print(used_materials)

        mtltexnums = self.get_texnums(used_materials)

        print(banner("Texture numbers:", 70))
        print(mtltexnums)

        for manager in managers:
            manager.assign_mtltxns(mtltexnums)
            manager.export()

        print("Export took {} seconds.".format(
            time.perf_counter() - export_start))


def banner(text, width=50):
    str_length = len(text)
    banner_topbtm = "=" * width
    if str_length > width:
        return banner_topbtm + "\n" + text + "\n" + banner_topbtm
    num_sideqs = width // 2 - (str_length + 2) // 2
    banner_mid = (
        "=" * num_sideqs + " " + text + " " + "=" * num_sideqs)
    return banner_topbtm + "\n" + banner_mid + "\n" + banner_topbtm
