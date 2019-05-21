#    This file is part of Korman.
#
#    Korman is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Korman is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Korman.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from PyHSPlasma import *
from math import fabs
import weakref

from ..exporter.logger import ExportProgressLogger
from . import explosions
from .. import helpers
from . import material
from . import utils

_MAX_VERTS_PER_SPAN = 0xFFFF
_WARN_VERTS_PER_SPAN = 0x8000

_VERTEX_COLOR_LAYERS = {"col", "color", "colour"}

class _RenderLevel:
    MAJOR_OPAQUE = 0
    MAJOR_FRAMEBUF = 1
    MAJOR_DEFAULT = 2
    MAJOR_BLEND = 4
    MAJOR_LATE = 8

    _MAJOR_SHIFT = 28
    _MINOR_MASK = ((1 << _MAJOR_SHIFT) - 1)

    def __init__(self, bo, hsgmat, pass_index, blendSpan=False):
        self.level = 0

        if blendSpan:
            self.major = self.MAJOR_DEFAULT

        # We use the blender material's pass index (which we stashed in the hsGMaterial) to increment
        # the render pass, just like it says...
        self.level += pass_index

    def __eq__(self, other):
        return self.level == other.level

    def __hash__(self):
        return hash(self.level)

    def _get_major(self):
        return self.level >> self._MAJOR_SHIFT
    def _set_major(self, value):
        self.level = ((value << self._MAJOR_SHIFT) & 0xFFFFFFFF) | self.minor
    major = property(_get_major, _set_major)

    def _get_minor(self):
        return self.level & self._MINOR_MASK
    def _set_minor(self, value):
        self.level = ((self.major << self._MAJOR_SHIFT) & 0xFFFFFFFF) | value
    minor = property(_get_minor, _set_minor)


class _DrawableCriteria:
    def __init__(self, bo, hsgmat, pass_index):
        self.blend_span = bool(hsgmat.layers[0].object.state.blendFlags & hsGMatState.kBlendMask)
        self.criteria = 0

        if self.blend_span:
            for mod in bo.plasma_modifiers.modifiers:
                if mod.requires_face_sort:
                    self.criteria |= plDrawable.kCritSortFaces
                if mod.requires_span_sort:
                    self.criteria |= plDrawable.kCritSortSpans
        self.render_level = _RenderLevel(bo, hsgmat, pass_index, self.blend_span)

    def __eq__(self, other):
        if not isinstance(other, _DrawableCriteria):
            return False
        for i in ("blend_span", "render_level", "criteria"):
            if getattr(self, i) != getattr(other, i):
                return False
        return True

    def __hash__(self):
        return hash(self.render_level) ^ hash(self.blend_span) ^ hash(self.criteria)

    @property
    def span_type(self):
        if self.blend_span:
            return "BlendSpans"
        else:
            return "Spans"


class _GeoData:
    def __init__(self, numVtxs):
        self.blender2gs = [{} for i in range(numVtxs)]
        self.triangles = []
        self.vertices = []



class _MeshManager:
    def __init__(self, report=None):
        if report is not None:
            self._report = report
        self._overrides = {}

    @staticmethod
    def add_progress_presteps(report):
        report.progress_add_step("Applying Blender Mods")

    def _build_prop_dict(self, bstruct):
        props = {}
        for i in bstruct.bl_rna.properties:
            ident = i.identifier
            if ident == "rna_type":
                continue
            props[ident] = getattr(bstruct, ident) if getattr(i, "array_length", 0) == 0 else tuple(getattr(bstruct, ident))
        return props

    def __enter__(self):
        scene = bpy.context.scene
        self._report.progress_advance()
        self._report.progress_range = len(scene.objects)

        # Some modifiers like "Array" will procedurally generate new geometry that will impact
        # lightmap generation. The Blender Internal renderer does not seem to be smart enough to
        # take this into account. Thus, we temporarily apply modifiers to ALL meshes (even ones that
        # are not exported) such that we can generate proper lighting.
        mesh_type = bpy.types.Mesh
        for i in scene.objects:
            if isinstance(i.data, mesh_type) and i.is_modified(scene, "RENDER"):
                # Remember, storing actual pointers to the Blender objects can cause bad things to
                # happen because Blender's memory management SUCKS!
                self._overrides[i.name] = { "mesh": i.data.name, "modifiers": [] }
                i.data = i.to_mesh(scene, True, "RENDER", calc_tessface=False)

                # If the modifiers are left on the object, the lightmap bake can break under some
                # situations. Therefore, we now cache the modifiers and clear them away...
                if i.plasma_object.enabled:
                    cache_mods = self._overrides[i.name]["modifiers"]
                    for mod in i.modifiers:
                        cache_mods.append(self._build_prop_dict(mod))
                    i.modifiers.clear()
            self._report.progress_increment()
        return self

    def __exit__(self, type, value, traceback):
        data_bos, data_meshes = bpy.data.objects, bpy.data.meshes
        for obj_name, override in self._overrides.items():
            bo = data_bos.get(obj_name)

            # Reapply the old mesh
            trash_mesh, bo.data = bo.data, data_meshes.get(override["mesh"])
            data_meshes.remove(trash_mesh)

            # If modifiers were removed, reapply them now.
            for cached_mod in override["modifiers"]:
                mod = bo.modifiers.new(cached_mod["name"], cached_mod["type"])
                for key, value in cached_mod.items():
                    if key in {"name", "type"}:
                        continue
                    setattr(mod, key, value)


class MeshConverter(_MeshManager):
    def __init__(self, exporter):
        self._exporter = weakref.ref(exporter)
        self.material = material.MaterialConverter(exporter)

        self._dspans = {}
        self._mesh_geospans = {}

        # _report is a property on this subclass
        super().__init__()

    def _calc_num_uvchans(self, bo, mesh):
        max_user_texs = plGeometrySpan.kUVCountMask
        num_user_texs = len(mesh.tessface_uv_textures)
        total_texs = num_user_texs

        # Bump Mapping requires 2 magic channels
        if self.material.get_bump_layer(bo) is not None:
            total_texs += 2
            max_user_texs -= 2

        # Lightmapping requires its own LIGHTMAPGEN channel
        # NOTE: the LIGHTMAPGEN texture has already been created, so it is in num_user_texs
        lm = bo.plasma_modifiers.lightmap
        if lm.enabled and lm.bake_type == "lightmap":
            num_user_texs -= 1
            max_user_texs -= 1

        return (num_user_texs, total_texs, max_user_texs)

    def _create_geospan(self, bo, mesh, bm, hsgmatKey):
        """Initializes a plGeometrySpan from a Blender Object and an hsGMaterial"""
        geospan = plGeometrySpan()
        geospan.material = hsgmatKey

        # GeometrySpan format
        # For now, we really only care about the number of UVW Channels
        user_uvws, total_uvws, max_user_uvws = self._calc_num_uvchans(bo, mesh)
        if total_uvws > plGeometrySpan.kUVCountMask:
            raise explosions.TooManyUVChannelsError(bo, bm, user_uvws, max_user_uvws)
        geospan.format = total_uvws

        # Begin total guesswork WRT flags
        mods = bo.plasma_modifiers
        if mods.lightmap.enabled:
            geospan.props |= plGeometrySpan.kLiteVtxNonPreshaded
        if mods.lighting.rt_lights:
            geospan.props |= plGeometrySpan.kPropRunTimeLight

        # Harvest lights
        permaLights, permaProjs = self._exporter().light.find_material_light_keys(bo, bm)
        for i in permaLights:
            geospan.addPermaLight(i)
        for i in permaProjs:
            geospan.addPermaProj(i)

        # If this object has a CI, we don't need xforms here...
        if self._exporter().has_coordiface(bo):
            geospan.localToWorld = hsMatrix44()
            geospan.worldToLocal = hsMatrix44()
        else:
            geospan.localToWorld = utils.matrix44(bo.matrix_basis)
            geospan.worldToLocal = geospan.localToWorld.inverse()
        return geospan

    def finalize(self):
        """Prepares all baked Plasma geometry to be flushed to the disk"""
        self._report.progress_advance()
        self._report.progress_range = len(self._dspans)
        inc_progress = self._report.progress_increment
        log_msg = self._report.msg

        log_msg("\nFinalizing Geometry")
        for loc in self._dspans.values():
            for dspan in loc.values():
                log_msg("[DrawableSpans '{}']", dspan.key.name, indent=1)

                # This mega-function does a lot:
                # 1. Converts SourceSpans (geospans) to Icicles and bakes geometry into plGBuffers
                # 2. Calculates the Icicle bounds
                # 3. Builds the plSpaceTree
                # 4. Clears the SourceSpans
                dspan.composeGeometry(True, True)
            inc_progress()

    def _export_geometry(self, bo, mesh, materials, geospans):
        geodata = [_GeoData(len(mesh.vertices)) for i in materials]
        bumpmap = self.material.get_bump_layer(bo)

        # Locate relevant vertex color layers now...
        lm = bo.plasma_modifiers.lightmap
        color, alpha = None, None
        for vcol_layer in mesh.tessface_vertex_colors:
            name = vcol_layer.name.lower()
            if name in _VERTEX_COLOR_LAYERS:
                color = vcol_layer.data
            elif name == "autocolor" and color is None and not lm.bake_lightmap:
                color = vcol_layer.data
            elif name == "alpha":
                alpha = vcol_layer.data

        # Convert Blender faces into things we can stuff into libHSPlasma
        for i, tessface in enumerate(mesh.tessfaces):
            data = geodata[tessface.material_index]
            face_verts = []
            use_smooth = tessface.use_smooth
            dPosDu = hsVector3(0.0, 0.0, 0.0)
            dPosDv = hsVector3(0.0, 0.0, 0.0)

            # Unpack the UV coordinates from each UV Texture layer
            # NOTE: Blender has no third (W) coordinate
            tessface_uvws = [uvtex.data[i].uv for uvtex in mesh.tessface_uv_textures]

            # Unpack colors
            if color is None:
                tessface_colors = ((1.0, 1.0, 1.0), (1.0, 1.0, 1.0), (1.0, 1.0, 1.0), (1.0, 1.0, 1.0))
            else:
                src = color[i]
                tessface_colors = (src.color1, src.color2, src.color3, src.color4)

            # Unpack alpha values
            if alpha is None:
                tessface_alphas = (1.0, 1.0, 1.0, 1.0)
            else:
                src = alpha[i]
                # average color becomes the alpha value
                tessface_alphas = (((src.color1[0] + src.color1[1] + src.color1[2]) / 3),
                                   ((src.color2[0] + src.color2[1] + src.color2[2]) / 3),
                                   ((src.color3[0] + src.color3[1] + src.color3[2]) / 3),
                                   ((src.color4[0] + src.color4[1] + src.color4[2]) / 3))

            if bumpmap is not None:
                gradPass = []
                gradUVWs = []

                if len(tessface.vertices) != 3:
                    gradPass.append([tessface.vertices[0], tessface.vertices[1], tessface.vertices[2]])
                    gradPass.append([tessface.vertices[0], tessface.vertices[2], tessface.vertices[3]])
                    gradUVWs.append((tuple((uvw[0] for uvw in tessface_uvws)),
                                     tuple((uvw[1] for uvw in tessface_uvws)),
                                     tuple((uvw[2] for uvw in tessface_uvws))))
                    gradUVWs.append((tuple((uvw[0] for uvw in tessface_uvws)),
                                     tuple((uvw[2] for uvw in tessface_uvws)),
                                     tuple((uvw[3] for uvw in tessface_uvws))))
                else:
                    gradPass.append(tessface.vertices)
                    gradUVWs.append((tuple((uvw[0] for uvw in tessface_uvws)),
                                     tuple((uvw[1] for uvw in tessface_uvws)),
                                     tuple((uvw[2] for uvw in tessface_uvws))))

                for p, vids in enumerate(gradPass):
                    dPosDu += self._get_bump_gradient(bumpmap[1], gradUVWs[p], mesh, vids, bumpmap[0], 0)
                    dPosDv += self._get_bump_gradient(bumpmap[1], gradUVWs[p], mesh, vids, bumpmap[0], 1)
                dPosDv = -dPosDv

            # Convert to per-material indices
            for j, vertex in enumerate(tessface.vertices):
                uvws = tuple([uvw[j] for uvw in tessface_uvws])

                # Grab VCols
                vertex_color = (int(tessface_colors[j][0] * 255), int(tessface_colors[j][1] * 255),
                                int(tessface_colors[j][2] * 255), int(tessface_alphas[j] * 255))

                # Now, we'll index into the vertex dict using the per-face elements :(
                # We're using tuples because lists are not hashable. The many mathutils and PyHSPlasma
                # types are not either, and it's entirely too much work to fool with all that.
                coluv = (vertex_color, uvws)
                if coluv not in data.blender2gs[vertex]:
                    source = mesh.vertices[vertex]
                    geoVertex = plGeometrySpan.TempVertex()
                    geoVertex.position = hsVector3(*source.co)

                    # If this face has smoothing, use the vertex normal
                    # Otherwise, use the face normal
                    if use_smooth:
                        geoVertex.normal = hsVector3(*source.normal)
                    else:
                        geoVertex.normal = hsVector3(*tessface.normal)

                    geoVertex.color = hsColor32(*vertex_color)
                    uvs = [hsVector3(uv[0], 1.0 - uv[1], 0.0) for uv in uvws]
                    if bumpmap is not None:
                        uvs.append(dPosDu)
                        uvs.append(dPosDv)
                    geoVertex.uvs = uvs

                    idx = len(data.vertices)
                    data.blender2gs[vertex][coluv] = idx
                    data.vertices.append(geoVertex)
                    face_verts.append(idx)
                else:
                    # If we have a bump mapping layer, then we need to add the bump gradients for
                    # this face to the vertex's magic channels
                    if bumpmap is not None:
                        num_user_uvs = len(uvws)
                        geoVertex = data.vertices[data.blender2gs[vertex][coluv]]

                        # Unfortunately, PyHSPlasma returns a copy of everything. Previously, editing
                        # in place would result in silent failures; however, as of python_refactor,
                        # PyHSPlasma now returns tuples to indicate this.
                        geoUVs = list(geoVertex.uvs)
                        geoUVs[num_user_uvs] += dPosDu
                        geoUVs[num_user_uvs+1] += dPosDv
                        geoVertex.uvs = geoUVs
                    face_verts.append(data.blender2gs[vertex][coluv])

            # Convert to triangles, if need be...
            if len(face_verts) == 3:
                data.triangles += face_verts
            elif len(face_verts) == 4:
                data.triangles += (face_verts[0], face_verts[1], face_verts[2])
                data.triangles += (face_verts[0], face_verts[2], face_verts[3])

        # Time to finish it up...
        for i, data in enumerate(geodata):
            geospan = geospans[i][0]
            numVerts = len(data.vertices)
            numUVs = geospan.format & plGeometrySpan.kUVCountMask

            # There is a soft limit of 0x8000 vertices per span in Plasma, but the limit is
            # theoretically 0xFFFF because this field is a 16-bit integer. However, bad things
            # happen in MOUL when we have over 0x8000 vertices. I've also received tons of reports
            # of stack dumps in PotS when modifiers are applied, so we're going to limit to 0x8000.
            #     TODO: consider busting up the mesh into multiple geospans?
            #           or hack plDrawableSpans::composeGeometry to do it for us?
            if numVerts > _WARN_VERTS_PER_SPAN:
                raise explosions.TooManyVerticesError(bo.data.name, geospan.material.name, numVerts)

            # If we're bump mapping, we need to normalize our magic UVW channels
            if bumpmap is not None:
                for vtx in data.vertices:
                    uvMap = vtx.uvs
                    uvMap[numUVs - 2].normalize()
                    uvMap[numUVs - 1].normalize()
                    vtx.uvs = uvMap

            # If we're still here, let's add our data to the GeometrySpan
            geospan.indices = data.triangles
            geospan.vertices = data.vertices


    def _get_bump_gradient(self, xform, uvws, mesh, vIds, uvIdx, iUV):
        v0 = hsVector3(*mesh.vertices[vIds[0]].co)
        v1 = hsVector3(*mesh.vertices[vIds[1]].co)
        v2 = hsVector3(*mesh.vertices[vIds[2]].co)

        uv0 = (uvws[0][uvIdx][0], uvws[0][uvIdx][1], 0.0)
        uv1 = (uvws[1][uvIdx][0], uvws[1][uvIdx][1], 0.0)
        uv2 = (uvws[2][uvIdx][0], uvws[2][uvIdx][1], 0.0)

        notUV = int(not iUV)
        _REAL_SMALL = 0.000001

        delta = uv0[notUV] - uv1[notUV]
        if fabs(delta) < _REAL_SMALL:
            return v1 - v0 if uv0[iUV] - uv1[iUV] < 0 else v0 - v1

        delta = uv2[notUV] - uv1[notUV]
        if fabs(delta) < _REAL_SMALL:
            return v1 - v2 if uv2[iUV] - uv1[iUV] < 0 else v2 - v1

        delta = uv2[notUV] - uv0[notUV]
        if fabs(delta) < _REAL_SMALL:
            return v0 - v2 if uv2[iUV] - uv0[iUV] < 0 else v2 - v0

        # On to the real fun...
        delta = uv0[notUV] - uv1[notUV]
        delta = 1.0 / delta
        v0Mv1 = v0 - v1
        v0Mv1 *= delta
        v0uv = (uv0[iUV] - uv1[iUV]) * delta

        delta = uv2[notUV] - uv1[notUV]
        delta = 1.0 / delta
        v2Mv1 = v2 - v1
        v2Mv1 *= delta
        v2uv = (uv2[iUV] - uv1[iUV]) * delta

        return v0Mv1 - v2Mv1 if v0uv > v2uv else v2Mv1 - v0Mv1

    def export_object(self, bo):
        # If this object has modifiers, then it's a unique mesh, and we don't need to try caching it
        # Otherwise, let's *try* to share meshes as best we can...
        if bo.modifiers:
            drawables = self._export_mesh(bo)
        else:
            drawables = self._mesh_geospans.get(bo.data, None)
            if drawables is None:
                drawables = self._export_mesh(bo)

        # Create the DrawInterface
        if drawables:
            diface = self._mgr.find_create_object(plDrawInterface, bl=bo)
            for dspan_key, idx in drawables:
                diface.addDrawable(dspan_key, idx)

    def _export_mesh(self, bo):
        # Previously, this called bo.to_mesh to apply modifiers. However, due to limitations in the
        # lightmap generation, this is now done for all modified mesh objects before any Plasma data
        # is exported.
        mesh = bo.data
        mesh.calc_tessface()

        # Step 0.8: Figure out which materials are attached to this object. Because Blender is backwards,
        #           we can actually have materials that are None. gotdawgit!!!
        materials = [i for i in mesh.materials if i is not None]
        if not materials:
            return None

        # Step 1: Export all of the doggone materials.
        geospans = self._export_material_spans(bo, mesh, materials)

        # Step 2: Export Blender mesh data to Plasma GeometrySpans
        self._export_geometry(bo, mesh, materials, geospans)

        # Step 3: Add plGeometrySpans to the appropriate DSpan and create indices
        _diindices = {}
        for geospan, pass_index in geospans:
            dspan = self._find_create_dspan(bo, geospan.material.object, pass_index)
            self._report.msg("Exported hsGMaterial '{}' geometry into '{}'",
                             geospan.material.name, dspan.key.name, indent=1)
            idx = dspan.addSourceSpan(geospan)
            diidx = _diindices.setdefault(dspan, [])
            diidx.append(idx)

        # Step 3.1: Harvest Span indices and create the DIIndices
        drawables = []
        for dspan, indices in _diindices.items():
            dii = plDISpanIndex()
            dii.indices = indices
            idx = dspan.addDIIndex(dii)
            drawables.append((dspan.key, idx))
        return drawables

    def _export_material_spans(self, bo, mesh, materials):
        """Exports all Materials and creates plGeometrySpans"""
        waveset_mod = bo.plasma_modifiers.water_basic
        if waveset_mod.enabled:
            if len(materials) > 1:
                msg = "'{}' is a WaveSet -- only one material is supported".format(bo.name)
                self._exporter().report.warn(msg, indent=1)
            matKey = self.material.export_waveset_material(bo, materials[0])
            geospan = self._create_geospan(bo, mesh, materials[0], matKey)

            # FIXME: Can some of this be generalized?
            geospan.props |= (plGeometrySpan.kWaterHeight | plGeometrySpan.kLiteVtxNonPreshaded |
                              plGeometrySpan.kPropReverseSort | plGeometrySpan.kPropNoShadow)
            geospan.waterHeight = bo.location[2]
            return [(geospan, 0)]
        else:
            geospans = [None] * len(materials)
            for i, blmat in enumerate(materials):
                matKey = self.material.export_material(bo, blmat)
                geospans[i] = (self._create_geospan(bo, mesh, blmat, matKey), blmat.pass_index)
            return geospans

    def _find_create_dspan(self, bo, hsgmat, pass_index):
        location = self._mgr.get_location(bo)
        if location not in self._dspans:
            self._dspans[location] = {}

        # This is where we figure out which DSpan this goes into. To vaguely summarize the rules...
        # BlendSpans: anything with an alpha blended layer
        # SortSpans: means we should sort the spans in this DSpan with all other span in this pass
        # SortFaces: means we should sort the faces in this span only
        # We're using pass index to do just what it was designed for. Cyan has a nicer "depends on"
        # draw component, but pass index is the Blender way, so that's what we're doing.
        crit = _DrawableCriteria(bo, hsgmat, pass_index)

        if crit not in self._dspans[location]:
            # AgeName_[District_]_Page_RenderLevel_Crit[Blend]Spans
            # Just because it's nice to be consistent
            node = self._mgr.get_scene_node(location=location)
            name = "{}_{:08X}_{:X}{}".format(node.name, crit.render_level.level, crit.criteria, crit.span_type)
            dspan = self._mgr.add_object(pl=plDrawableSpans, name=name, loc=location)

            criteria = crit.criteria
            dspan.criteria = criteria
            if criteria & plDrawable.kCritSortFaces:
                dspan.props |= plDrawable.kPropSortFaces
            if criteria & plDrawable.kCritSortSpans:
                dspan.props |= plDrawable.kPropSortSpans
            dspan.renderLevel = crit.render_level.level
            dspan.sceneNode = node # AddViaNotify

            self._dspans[location][crit] = dspan
            return dspan
        else:
            return self._dspans[location][crit]

    @property
    def _mgr(self):
        return self._exporter().mgr

    @property
    def _report(self):
        return self._exporter().report
