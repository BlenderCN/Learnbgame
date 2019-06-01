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
import math
from pathlib import Path
from PyHSPlasma import *
import weakref

from .explosions import *
from .. import helpers
from ..korlib import *
from . import utils

_MAX_STENCILS = 6

# Blender cube map mega image to libHSPlasma plCubicEnvironmap faces mapping...
# See https://blender.stackexchange.com/questions/46891/how-to-render-an-environment-to-a-cube-map-in-cycles
BLENDER_CUBE_MAP = ("leftFace", "backFace", "rightFace",
                    "bottomFace", "topFace", "frontFace")

class _Texture:
    _DETAIL_BLEND = {
        TEX_DETAIL_ALPHA: "AL",
        TEX_DETAIL_ADD: "AD",
        TEX_DETAIL_MULTIPLY: "ML",
    }

    def __init__(self, **kwargs):
        texture, image = kwargs.get("texture"), kwargs.get("image")
        assert texture or image

        if texture is not None:
            if image is None:
                image = texture.image
            self.calc_alpha = getattr(texture, "use_calculate_alpha", False)
            self.mipmap = texture.use_mipmap
        else:
            self.layer = kwargs.get("layer")
            self.calc_alpha = False
            self.mipmap = kwargs.get("mipmap", False)

        if kwargs.get("is_detail_map", False):
            self.is_detail_map = True
            self.mipmap = True
            self.detail_blend = kwargs["detail_blend"]
            self.detail_fade_start = kwargs["detail_fade_start"]
            self.detail_fade_stop = kwargs["detail_fade_stop"]
            self.detail_opacity_start = kwargs["detail_opacity_start"]
            self.detail_opacity_stop = kwargs["detail_opacity_stop"]
            self.calc_alpha = False
            self.use_alpha = True
            self.allowed_formats = {"DDS"}
            self.is_cube_map = False
        else:
            self.is_detail_map = False
            use_alpha = kwargs.get("use_alpha")
            if kwargs.get("force_calc_alpha", False) or self.calc_alpha:
                self.calc_alpha = True
                self.use_alpha  = True
            elif use_alpha is None:
                self.use_alpha = (image.channels == 4 and image.use_alpha)
            else:
                self.use_alpha = use_alpha
            self.allowed_formats = kwargs.get("allowed_formats",
                                              {"DDS"} if self.mipmap else {"PNG", "JPG"})
            self.is_cube_map = kwargs.get("is_cube_map", False)

        # Basic format sanity
        if self.mipmap:
            assert "DDS" in self.allowed_formats

        if len(self.allowed_formats) == 1:
            self.auto_ext = next(iter(self.allowed_formats)).lower()
        elif self.mipmap:
            self.auto_ext = "dds"
        else:
            self.auto_ext = "hsm"
        self.extension = kwargs.get("extension", self.auto_ext)
        self.ephemeral = kwargs.get("ephemeral", False)
        self.image = image
        self.tag = kwargs.get("tag", None)

    def __eq__(self, other):
        if not isinstance(other, _Texture):
            return False

        # Yeah, the string name is a unique identifier. So shoot me.
        if str(self) == str(other) and self.tag == other.tag:
            self._update(other)
            return True
        return False

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        if self.extension is None:
            name = self.image.name
        else:
            name = str(Path(self.image.name).with_suffix(".{}".format(self.extension)))
        if self.calc_alpha:
            name = "ALPHAGEN_{}".format(name)

        if self.is_detail_map:
            name = "DETAILGEN_{}-{}-{}-{}-{}_{}".format(self._DETAIL_BLEND[self.detail_blend],
                                                        self.detail_fade_start, self.detail_fade_stop,
                                                        self.detail_opacity_start, self.detail_opacity_stop,
                                                        name)
        return name

    def _update(self, other):
        """Update myself with any props that might be overridable from another copy of myself"""
        # NOTE: detail map properties should NEVER be overridden. NEVER. EVER. kthx.
        if other.use_alpha:
            self.use_alpha = True
        if other.mipmap:
            self.mipmap = True


class MaterialConverter:
    def __init__(self, exporter):
        self._obj2mat = {}
        self._bump_mats = {}
        self._exporter = weakref.ref(exporter)
        self._pending = {}
        self._alphatest = {}
        self._tex_exporters = {
            "ENVIRONMENT_MAP": self._export_texture_type_environment_map,
            "IMAGE": self._export_texture_type_image,
            "NONE": self._export_texture_type_none,
        }
        self._animation_exporters = {
            "opacityCtl": self._export_layer_opacity_animation,
            "transformCtl": self._export_layer_transform_animation,
        }

    def _can_export_texslot(self, slot):
        if slot is None or not slot.use:
            return False
        texture = slot.texture
        if texture is None or texture.type not in self._tex_exporters:
            return False

        # Per-texture type rules
        if texture.type == "ENVIRONMENT_MAP":
            envmap = texture.environment_map
            # If this is a static, image based cube map, then we will allow it
            # to be exported anyway. Note that as of the writing of this code,
            # that is kind of pointless because CEMs are not yet implemented...
            if envmap.source == "IMAGE_FILE":
                return True

            # Now for the ruelz
            method, ver = self._exporter().envmap_method, self._mgr.getVer()
            if method == "skip":
                return False
            elif method == "dcm2dem":
                return True
            elif method == "perengine":
                return (ver >= pvMoul and envmap.mapping == "PLANE") or envmap.mapping == "CUBE"
            else:
                raise NotImplementedError(method)
        else:
            return True

    def export_material(self, bo, bm):
        """Exports a Blender Material as an hsGMaterial"""

        # Sometimes, a material might need to be single-use. Right now, the most apparent example
        # of that situation is when a lightmap image is baked. Wavesets are in the same boat, but
        # that's a special case as of the writing of this code.
        single_user = self._requires_single_user_material(bo, bm)
        if single_user:
            mat_name = "{}_AutoSingle".format(bm.name) if bo.name == bm.name else "{}_{}".format(bo.name, bm.name)
            self._report.msg("Exporting Material '{}' as single user '{}'", bm.name, mat_name, indent=1)
            hgmat = None
        else:
            mat_name = bm.name
            self._report.msg("Exporting Material '{}'", mat_name, indent=1)
            hsgmat = self._mgr.find_key(hsGMaterial, name=mat_name, bl=bo)
            if hsgmat is not None:
                return hsgmat

        hsgmat = self._mgr.add_object(hsGMaterial, name=mat_name, bl=bo)
        slots = [(idx, slot) for idx, slot in enumerate(bm.texture_slots) if self._can_export_texslot(slot)]

        # There is a major difference in how Blender and Plasma handle stencils.
        # In Blender, the stencil is on top and applies to every layer below is. In Plasma, the stencil
        # is below the SINGLE layer it affects. The main texture is marked BindNext and RestartPassHere.
        # The pipeline indicates that we can render 8 layers simultaneously, so we will collect all
        # stencils and apply this arrangement. We're going to limit to 6 stencils however. 1 layer for
        # main texture and 1 piggyback.
        num_stencils = sum((1 for i in slots if i[1].use_stencil))
        if num_stencils > _MAX_STENCILS:
            raise ExportError("Material '{}' uses too many stencils. The maximum is {}".format(bm.name, _MAX_STENCILS))
        stencils = []
        restart_pass_next = False

        # Loop over layers
        for idx, slot in slots:
            # Prepend any BumpMapping magic layers
            if slot.use_map_normal:
                if bo in self._bump_mats:
                    raise ExportError("Material '{}' has more than one bumpmap layer".format(bm.name))
                du, dw, dv = self.export_bumpmap_slot(bo, bm, hsgmat, slot, idx)
                hsgmat.addLayer(du.key) # Du
                hsgmat.addLayer(dw.key) # Dw
                hsgmat.addLayer(dv.key) # Dv

            if slot.use_stencil:
                stencils.append((idx, slot))
            else:
                tex_layer = self.export_texture_slot(bo, bm, hsgmat, slot, idx)
                if restart_pass_next:
                    tex_layer.state.miscFlags |= hsGMatState.kMiscRestartPassHere
                    restart_pass_next = False
                hsgmat.addLayer(tex_layer.key)
                if slot.use_map_normal:
                    self._bump_mats[bo] = (tex_layer.UVWSrc, tex_layer.transform)
                    # After a bumpmap layer(s), the next layer *must* be in a
                    # new pass, otherwise it gets added in non-intuitive ways
                    restart_pass_next = True
                if stencils:
                    tex_state = tex_layer.state
                    if not tex_state.blendFlags & hsGMatState.kBlendMask:
                        tex_state.blendFlags |= hsGMatState.kBlendAlpha
                    tex_state.miscFlags |= hsGMatState.kMiscRestartPassHere | hsGMatState.kMiscBindNext
                    curr_stencils = len(stencils)
                    for i in range(curr_stencils):
                        stencil_idx, stencil = stencils[i]
                        stencil_name = "STENCILGEN_{}@{}_{}".format(stencil.name, bm.name, slot.name)
                        stencil_layer = self.export_texture_slot(bo, bm, hsgmat, stencil, stencil_idx, name=stencil_name)
                        if i+1 < curr_stencils:
                            stencil_layer.state.miscFlags |= hsGMatState.kMiscBindNext
                        hsgmat.addLayer(stencil_layer.key)

        # Plasma makes several assumptions that every hsGMaterial has at least one layer. If this
        # material had no Textures, we will need to initialize a default layer
        if not hsgmat.layers:
            layer = self._mgr.find_create_object(plLayer, name="{}_AutoLayer".format(bm.name), bl=bo)
            self._propagate_material_settings(bm, layer)
            hsgmat.addLayer(layer.key)

        # Cache this material for later
        mat_list = self._obj2mat.setdefault(bo, [])
        mat_list.append(hsgmat.key)

        # Looks like we're done...
        return hsgmat.key

    def export_waveset_material(self, bo, bm):
        self._report.msg("Exporting WaveSet Material '{}'", bm.name, indent=1)

        # WaveSets MUST have their own material
        unique_name = "{}_WaveSet7".format(bm.name)
        hsgmat = self._mgr.add_object(hsGMaterial, name=unique_name, bl=bo)

        # Materials MUST have one layer. Wavesets need alpha blending...
        layer = self._mgr.add_object(plLayer, name=unique_name, bl=bo)
        self._propagate_material_settings(bm, layer)
        layer.state.blendFlags |= hsGMatState.kBlendAlpha
        hsgmat.addLayer(layer.key)

        # Wasn't that easy?
        return hsgmat.key

    def export_bumpmap_slot(self, bo, bm, hsgmat, slot, idx):
        name = "{}_{}".format(bm.name if bm is not None else bo.name, slot.name)
        self._report.msg("Exporting Plasma Bumpmap Layers for '{}'", name, indent=2)

        # Okay, now we need to make 3 layers for the Du, Dw, and Dv
        du_layer = self._mgr.find_create_object(plLayer, name="{}_DU_BumpLut".format(name), bl=bo)
        dw_layer = self._mgr.find_create_object(plLayer, name="{}_DW_BumpLut".format(name), bl=bo)
        dv_layer = self._mgr.find_create_object(plLayer, name="{}_DV_BumpLut".format(name), bl=bo)

        for layer in (du_layer, dw_layer, dv_layer):
            layer.ambient = hsColorRGBA(1.0, 1.0, 1.0, 1.0)
            layer.preshade = hsColorRGBA(0.0, 0.0, 0.0, 1.0)
            layer.runtime = hsColorRGBA(0.0, 0.0, 0.0, 1.0)
            layer.specular = hsColorRGBA(0.0, 0.0, 0.0, 1.0)

            state = layer.state
            state.ZFlags = hsGMatState.kZNoZWrite
            state.clampFlags = hsGMatState.kClampTexture
            state.miscFlags = hsGMatState.kMiscBindNext
            state.blendFlags = hsGMatState.kBlendAdd

        if not slot.use_map_specular:
            du_layer.state.blendFlags = hsGMatState.kBlendMADD

        du_layer.state.miscFlags |= hsGMatState.kMiscBumpDu | hsGMatState.kMiscRestartPassHere
        dw_layer.state.miscFlags |= hsGMatState.kMiscBumpDw
        dv_layer.state.miscFlags |= hsGMatState.kMiscBumpDv

        du_uv = len(bo.data.uv_layers)
        du_layer.UVWSrc = du_uv
        dw_layer.UVWSrc = du_uv | plLayerInterface.kUVWNormal
        dv_layer.UVWSrc = du_uv + 1

        page = self._mgr.get_textures_page(du_layer.key)
        LUT_key = self._mgr.find_key(plMipmap, loc=page, name="BumpLutTexture")

        if LUT_key is None:
            bumpLUT = plMipmap("BumpLutTexture", 16, 16, 1, plBitmap.kUncompressed, plBitmap.kRGB8888)
            create_bump_LUT(bumpLUT)
            self._mgr.AddObject(page, bumpLUT)
            LUT_key = bumpLUT.key

        du_layer.texture = LUT_key
        dw_layer.texture = LUT_key
        dv_layer.texture = LUT_key

        return (du_layer, dw_layer, dv_layer)

    def export_texture_slot(self, bo, bm, hsgmat, slot, idx, name=None, blend_flags=True):
        if name is None:
            name = "{}_{}".format(bm.name if bm is not None else bo.name, slot.name)
        self._report.msg("Exporting Plasma Layer '{}'", name, indent=2)
        layer = self._mgr.find_create_object(plLayer, name=name, bl=bo)
        if bm is not None and not slot.use_map_normal:
            self._propagate_material_settings(bm, layer)

        # UVW Channel
        if slot.texture_coords == "UV":
            for i, uvchan in enumerate(bo.data.uv_layers):
                if uvchan.name == slot.uv_layer:
                    layer.UVWSrc = i
                    self._report.msg("Using UV Map #{} '{}'", i, name, indent=3)
                    break
            else:
                self._report.msg("No UVMap specified... Blindly using the first one, maybe it exists :|", indent=3)

        # Transform
        xform = hsMatrix44()
        xform.setTranslate(hsVector3(*slot.offset))
        xform.setScale(hsVector3(*slot.scale))
        layer.transform = xform

        wantStencil, canStencil = slot.use_stencil, slot.use_stencil and bm is not None and not slot.use_map_normal
        if wantStencil and not canStencil:
            self._exporter().report.warn("{} wants to stencil, but this is not a real Material".format(slot.name))

        state = layer.state
        if canStencil:
            hsgmat.compFlags |= hsGMaterial.kCompNeedsBlendChannel
            state.blendFlags |= hsGMatState.kBlendAlpha | hsGMatState.kBlendAlphaMult | hsGMatState.kBlendNoTexColor
            if slot.texture.type == "BLEND":
                state.clampFlags |= hsGMatState.kClampTexture
            state.ZFlags |= hsGMatState.kZNoZWrite
            layer.ambient = hsColorRGBA(1.0, 1.0, 1.0, 1.0)
        elif blend_flags:
            # Standard layer flags ahoy
            if slot.blend_type == "ADD":
                state.blendFlags |= hsGMatState.kBlendAddColorTimesAlpha
            elif slot.blend_type == "MULTIPLY":
                state.blendFlags |= hsGMatState.kBlendMult

        # Check if this layer uses diffuse/runtime lighting
        if not slot.use_map_color_diffuse:
            layer.preshade = hsColorRGBA(0.0, 0.0, 0.0, 1.0)
            layer.runtime = hsColorRGBA(0.0, 0.0, 0.0, 1.0)

        # Check if this layer uses specular lighting
        if slot.use_map_color_spec:
            state.shadeFlags |= hsGMatState.kShadeSpecular
        else:
            layer.specular = hsColorRGBA(0.0, 0.0, 0.0, 1.0)
            layer.specularPower = 1.0

        texture = slot.texture

        # Apply custom layer properties
        if slot.use_map_normal:
            state.blendFlags = hsGMatState.kBlendDot3
            state.miscFlags = hsGMatState.kMiscBumpLayer
            strength = max(min(1.0, slot.normal_factor), 0.0)
            layer.ambient = hsColorRGBA(0.0, 0.0, 0.0, 1.0)
            layer.preshade = hsColorRGBA(0.0, 0.0, 0.0, 1.0)
            layer.runtime = hsColorRGBA(strength, 0.0, 0.0, 1.0)
            layer.specular = hsColorRGBA(0.0, 0.0, 0.0, 1.0)
        else:
            layer_props = texture.plasma_layer
            layer.opacity = layer_props.opacity / 100
            if layer_props.opacity < 100 and not state.blendFlags & hsGMatState.kBlendMask:
                state.blendFlags |= hsGMatState.kBlendAlpha
            if layer_props.alpha_halo:
                state.blendFlags |= hsGMatState.kBlendAlphaTestHigh
            if layer_props.z_bias:
                state.ZFlags |= hsGMatState.kZIncLayer
            if layer_props.skip_depth_test:
                state.ZFlags |= hsGMatState.kZNoZRead
            if layer_props.skip_depth_write:
                state.ZFlags |= hsGMatState.kZNoZWrite

        # Export the specific texture type
        self._tex_exporters[texture.type](bo, layer, slot)

        # Export any layer animations
        # NOTE: animated stencils and bumpmaps are nonsense.
        if not slot.use_stencil and not slot.use_map_normal:
            layer = self._export_layer_animations(bo, bm, slot, idx, layer)
        return layer

    def _export_layer_animations(self, bo, bm, tex_slot, idx, base_layer):
        """Exports animations on this texture and chains the Plasma layers as needed"""

        def harvest_fcurves(bl_id, collection, data_path=None):
            if bl_id is None:
                return None

            anim = bl_id.animation_data
            if anim is not None:
                action = anim.action
                if action is not None:
                    if data_path is None:
                        collection.extend(action.fcurves)
                    else:
                        collection.extend((i for i in action.fcurves if i.data_path.startswith(data_path)))
                    return action
            return None

        fcurves = []
        texture = tex_slot.texture
        mat_action = harvest_fcurves(bm, fcurves, "texture_slots[{}]".format(idx))
        tex_action = harvest_fcurves(texture, fcurves)
        if not fcurves:
            return base_layer

        # Okay, so we have some FCurves. We'll loop through our known layer animation converters
        # and chain this biotch up as best we can.
        layer_animation = None
        for attr, converter in self._animation_exporters.items():
            ctrl = converter(tex_slot, base_layer, fcurves)
            if ctrl is not None:
                if layer_animation is None:
                    name = "{}_LayerAnim".format(base_layer.key.name)
                    layer_animation = self.get_texture_animation_key(bo, bm, texture).object
                setattr(layer_animation, attr, ctrl)

        # Alrighty, if we exported any controllers, layer_animation is a plLayerAnimation. We need to do
        # the common schtuff now.
        if layer_animation is not None:
            layer_animation.underLay = base_layer.key

            fps = bpy.context.scene.render.fps
            atc = layer_animation.timeConvert
            if tex_action is not None:
                start, end = tex_action.frame_range
            else:
                start, end = mat_action.frame_range
            atc.begin = start / fps
            atc.end = end / fps

            layer_props = tex_slot.texture.plasma_layer
            if not layer_props.anim_auto_start:
                atc.flags |= plAnimTimeConvert.kStopped
            if layer_props.anim_loop:
                atc.flags |= plAnimTimeConvert.kLoop
                atc.loopBegin = atc.begin
                atc.loopEnd = atc.end
            if layer_props.anim_sdl_var:
                layer_animation.varName = layer_props.anim_sdl_var
            return layer_animation

        # Well, we had some FCurves but they were garbage... Too bad.
        return base_layer

    def _export_layer_opacity_animation(self, tex_slot, base_layer, fcurves):
        for i in fcurves:
            if i.data_path == "plasma_layer.opacity":
                base_layer.state.blendFlags |= hsGMatState.kBlendAlpha
                ctrl = self._exporter().animation.make_scalar_leaf_controller(i)
                return ctrl
        return None

    def _export_layer_transform_animation(self, tex_slot, base_layer, fcurves):
        path = tex_slot.path_from_id()
        pos_path = "{}.offset".format(path)
        scale_path = "{}.scale".format(path)

        # Plasma uses the controller to generate a matrix44... so we have to produce a leaf controller
        ctrl = self._exporter().animation.make_matrix44_controller(fcurves, pos_path, scale_path, tex_slot.offset, tex_slot.scale)
        return ctrl

    def _export_texture_type_environment_map(self, bo, layer, slot):
        """Exports a Blender EnvironmentMapTexture to a plLayer"""

        texture = slot.texture
        bl_env = texture.environment_map
        if bl_env.source in {"STATIC", "ANIMATED"}:
            # NOTE: It is assumed that if we arrive here, we are at lease dcm2dem on the
            #       environment map export method. You're welcome!
            if bl_env.mapping == "PLANE" and self._mgr.getVer() >= pvMoul:
                pl_env = plDynamicCamMap
            else:
                pl_env = plDynamicEnvMap
            pl_env = self.export_dynamic_env(bo, layer, texture, pl_env)
        elif bl_env.source == "IMAGE_FILE":
            pl_env = self.export_cubic_env(bo, layer, texture)
        else:
            raise NotImplementedError(bl_env.source)
        layer.state.shadeFlags |= hsGMatState.kShadeEnvironMap
        if pl_env is not None:
            layer.texture = pl_env.key

    def export_cubic_env(self, bo, layer, texture):
        width, height = texture.image.size

        # Sanity check: the image here should be 3x2 faces, so we should not have any
        #               dam remainder...
        if width % 3 != 0:
            raise ExportError("CubeMap '{}' width must be a multiple of 3".format(image.name))
        if height % 2 != 0:
            raise ExportError("CubeMap '{}' height must be a multiple of 2".format(image.name))

        # According to PlasmaMAX, we don't give a rip about UVs...
        layer.UVWSrc = plLayerInterface.kUVWReflect
        layer.state.miscFlags |= hsGMatState.kMiscUseReflectionXform

        # Well, this is kind of sad...
        # Back before the texture cache existed, all the image work was offloaded
        # to a big "finalize" save step to prevent races. The texture cache would
        # prevent that as well, so we could theoretically slice-and-dice the single
        # image here... but... meh. Offloading taim.
        self.export_prepared_image(texture=texture, owner=layer, indent=3,
                                   use_alpha=False, mipmap=True, allowed_formats={"DDS"},
                                   is_cube_map=True, tag="cubemap")


    def export_dynamic_env(self, bo, layer, texture, pl_class):
        bl_env = texture.environment_map
        viewpt = bl_env.viewpoint_object
        if viewpt is None:
            viewpt = bo
        name = "{}_DynEnvMap".format(texture.name)
        pl_env = self._mgr.find_object(pl_class, bl=bo, name=name)

        # Ensure POT
        oRes = bl_env.resolution
        eRes = helpers.ensure_power_of_two(oRes)
        if oRes != eRes:
            self._report.msg("Overriding EnvMap size to ({}x{}) -- POT", eRes, eRes, indent=3)

        # And now for the general ho'hum-ness
        pl_env = self._mgr.find_create_object(pl_class, bl=bo, name=name)
        pl_env.hither = bl_env.clip_start
        pl_env.yon = bl_env.clip_end
        pl_env.refreshRate = 0.01 if bl_env.source == "ANIMATED" else 0.0
        pl_env.incCharacters = True

        # Perhaps the DEM/DCM fog should be separately configurable at some point?
        pl_fog = bpy.context.scene.world.plasma_fni
        pl_env.color = utils.color(texture.plasma_layer.envmap_color)
        pl_env.fogStart = pl_fog.fog_start

        # EffVisSets
        # Whoever wrote this PyHSPlasma binding didn't follow the convention. Sigh.
        visregions = []
        for region in texture.plasma_layer.vis_regions:
            rgn = region.control_region
            if rgn is None:
                raise ExportError("'{}': Has an invalid Visibility Control".format(texture.name))
            if not rgn.plasma_modifiers.visregion.enabled:
                raise ExportError("'{}': '{}' is not a VisControl".format(texture.name, rgn.name))
            visregions.append(self._mgr.find_create_key(plVisRegion, bl=rgn))
        pl_env.visRegions = visregions

        if isinstance(pl_env, plDynamicCamMap):
            faces = (pl_env,)

            # It matters not whether or not the viewpoint object is a Plasma Object, it is exported as at
            # least a SceneObject and CoordInterface so that we can touch it...
            # NOTE: that harvest_actor makes sure everyone alread knows we're going to have a CI
            if isinstance(viewpt.data, bpy.types.Camera):
                pl_env.camera = self._mgr.find_create_key(plCameraModifier, bl=viewpt)
            else:
                pl_env.rootNode = self._mgr.find_create_key(plSceneObject, bl=viewpt)

            pl_env.addTargetNode(self._mgr.find_key(plSceneObject, bl=bo))
            pl_env.addMatLayer(layer.key)

            # This is really just so we don't raise any eyebrows if anyone is looking at the files.
            # If you're disabling DCMs, then you're obviuously trolling!
            # Cyan generates a single color image, but we'll just set the layer colors and go away.
            fake_layer = self._mgr.find_create_object(plLayer, bl=bo, name="{}_DisabledDynEnvMap".format(texture.name))
            fake_layer.ambient = layer.ambient
            fake_layer.preshade = layer.preshade
            fake_layer.runtime = layer.runtime
            fake_layer.specular = layer.specular
            pl_env.disableTexture = fake_layer.key

            if pl_env.camera is None:
                layer.UVWSrc = plLayerInterface.kUVWPosition
                layer.state.miscFlags |= (hsGMatState.kMiscCam2Screen | hsGMatState.kMiscPerspProjection)
        else:
            faces = pl_env.faces + (pl_env,)

            # If the user specifies a camera object, this might be worthy of a notice.
            if viewpt.type == "CAMERA":
                warn = self._report.port if bl_env.mapping == "PLANE" else self._report.warn
                warn("Environment Map '{}' is exporting as a cube map. The viewpoint '{}' is a camera, but only its position will be used.",
                     bl_env.id_data.name, viewpt.name, indent=5)

            # DEMs can do just a position vector. We actually prefer this because the WaveSet exporter
            # will probably want to steal it for diabolical purposes...
            pl_env.position = hsVector3(*viewpt.location)

            # We'll also export it as a Root though, where supported (MOUL)
            root = self._mgr.find_create_key(plSceneObject, bl=viewpt)
            pl_env.rootNode = root

            if layer is not None:
                layer.UVWSrc = plLayerInterface.kUVWReflect
                layer.state.miscFlags |= hsGMatState.kMiscUseReflectionXform

        # Because we might be working with a multi-faced env map. It's even worse than have two faces...
        for i in faces:
            i.setConfig(plBitmap.kRGB8888)
            i.flags |= plBitmap.kIsTexture
            i.flags &= ~plBitmap.kAlphaChannelFlag
            i.width = eRes
            i.height = eRes
            i.proportionalViewport = False
            i.viewportLeft = 0
            i.viewportTop = 0
            i.viewportRight = eRes
            i.viewportBottom = eRes
            i.ZDepth = 24

        return pl_env

    def _export_texture_type_image(self, bo, layer, slot):
        """Exports a Blender ImageTexture to a plLayer"""
        texture = slot.texture
        layer_props = texture.plasma_layer
        mipmap = texture.use_mipmap

        # Does the image have any alpha at all?
        if texture.image is not None:
            has_alpha = texture.use_calculate_alpha or slot.use_stencil or self._test_image_alpha(texture.image)
            if (texture.image.use_alpha and texture.use_alpha) and not has_alpha:
                warning = "'{}' wants to use alpha, but '{}' is opaque".format(texture.name, texture.image.name)
                self._exporter().report.warn(warning, indent=3)
        else:
            has_alpha = True

        # First, let's apply any relevant flags
        state = layer.state
        if not slot.use_stencil and not slot.use_map_normal:
            # mutually exclusive blend flags
            if texture.use_alpha and has_alpha:
                if slot.blend_type == "ADD":
                    state.blendFlags |= hsGMatState.kBlendAlphaAdd
                elif slot.blend_type == "MULTIPLY":
                    state.blendFlags |= hsGMatState.kBlendAlphaMult
                else:
                    state.blendFlags |= hsGMatState.kBlendAlpha

            if texture.invert_alpha and has_alpha:
                state.blendFlags |= hsGMatState.kBlendInvertAlpha

        if texture.extension in {"CLIP", "EXTEND"}:
            state.clampFlags |= hsGMatState.kClampTexture

        # Now, let's export the plBitmap
        # If the image is None (no image applied in Blender), we assume this is a plDynamicTextMap
        # Otherwise, we toss this layer and some info into our pending texture dict and process it
        #     when the exporter tells us to finalize all our shit
        if texture.image is None:
            dtm = self._mgr.find_create_object(plDynamicTextMap, name="{}_DynText".format(layer.key.name), bl=bo)
            dtm.hasAlpha = texture.use_alpha
            # if you have a better idea, let's hear it...
            dtm.visWidth, dtm.visHeight = 1024, 1024
            layer.texture = dtm.key
        else:
            detail_blend = TEX_DETAIL_ALPHA
            if layer_props.is_detail_map and mipmap:
                if slot.blend_type == "ADD":
                    detail_blend = TEX_DETAIL_ADD
                elif slot.blend_type == "MULTIPLY":
                    detail_blend = TEX_DETAIL_MULTIPLY

            # Herp, derp... Detail blends are all based on alpha
            if layer_props.is_detail_map and not state.blendFlags & hsGMatState.kBlendMask:
                state.blendFlags |= hsGMatState.kBlendDetail

            allowed_formats = {"DDS"} if mipmap else {"PNG", "BMP"}
            self.export_prepared_image(texture=texture, owner=layer,
                                       use_alpha=has_alpha, force_calc_alpha=slot.use_stencil,
                                       is_detail_map=layer_props.is_detail_map,
                                       detail_blend=detail_blend,
                                       detail_fade_start=layer_props.detail_fade_start,
                                       detail_fade_stop=layer_props.detail_fade_stop,
                                       detail_opacity_start=layer_props.detail_opacity_start,
                                       detail_opacity_stop=layer_props.detail_opacity_stop,
                                       mipmap=mipmap, allowed_formats=allowed_formats,
                                       indent=3)

    def _export_texture_type_none(self, bo, layer, texture):
        # We'll allow this, just for sanity's sake...
        pass

    def export_prepared_image(self, **kwargs):
        """This exports an externally prepared image and an optional owning layer.
           The following arguments are typical:
           - texture: (co-required) the image texture datablock to export
           - image: (co-required) the image datablock to export
           - owner: (required) the Plasma object using this image
           - mipmap: (optional) should the image be mipmapped?
           - allowed_formats: (optional) set of string *hints* for desired image export type
                              valid options: BMP, DDS, JPG, PNG
           - extension: (optional) file extension to use for the image object
                        to use the image datablock extension, set this to None
           - indent: (optional) indentation level for log messages
                     default: 2
           - ephemeral: (optional) never cache this image
           - tag: (optional) an optional identifier hint that allows multiple images with the
                             same name to coexist in the cache
           - is_cube_map: (optional) indicates the provided image contains six cube faces
                                     that must be split into six separate images for Plasma
        """
        owner = kwargs.pop("owner", None)
        indent = kwargs.pop("indent", 2)
        key = _Texture(**kwargs)
        image = key.image

        if key not in self._pending:
            self._report.msg("Stashing '{}' for conversion as '{}'", image.name, key, indent=indent)
            self._pending[key] = [owner.key,]
        else:
            self._report.msg("Found another user of '{}'", key, indent=indent)
            self._pending[key].append(owner.key)

    def finalize(self):
        self._report.progress_advance()
        self._report.progress_range = len(self._pending)
        inc_progress = self._report.progress_increment
        mgr = self._mgr

        # This with statement causes the texture cache to hold open a
        # read stream for the cache file, preventing spurious open-close
        # spin washing during this tight loop. Note that the cache still
        # has to actually be loaded ^_^
        with self._texcache as texcache:
            texcache.load()

            for key, owners in self._pending.items():
                name = str(key)
                pClassName = "CubicEnvironmap" if key.is_cube_map else "Mipmap"
                self._report.msg("\n[{} '{}']", pClassName, name)

                image = key.image

                # Now we try to use the pile of hints we were given to figure out what format to use
                allowed_formats = key.allowed_formats
                if key.mipmap:
                    compression = plBitmap.kDirectXCompression
                elif "PNG" in allowed_formats and self._mgr.getVer() == pvMoul:
                    compression = plBitmap.kPNGCompression
                elif "DDS" in allowed_formats:
                    compression = plBitmap.kDirectXCompression
                elif "JPG" in allowed_formats:
                    compression = plBitmap.kJPEGCompression
                elif "BMP" in allowed_formats:
                    compression = plBitmap.kUncompressed
                else:
                    raise RuntimeError(allowed_formats)
                dxt = plBitmap.kDXT5 if key.use_alpha or key.calc_alpha else plBitmap.kDXT1

                # Mayhaps we have a cached version of this that has already been exported
                cached_image = texcache.get_from_texture(key, compression)

                if cached_image is None:
                    numLevels, width, height, data = self._finalize_cache(texcache, key, image, name, compression, dxt)
                    self._finalize_bitmap(key, owners, name, numLevels, width, height, compression, dxt, data)
                else:
                    width, height = cached_image.export_size
                    data = cached_image.image_data
                    numLevels = cached_image.mip_levels

                    # If the cached image data is junk, PyHSPlasma will raise a RuntimeError,
                    # so we'll attempt a recache...
                    try:
                        self._finalize_bitmap(key, owners, name, numLevels, width, height, compression, dxt, data)
                    except RuntimeError:
                        self._report.warn("Cached image is corrupted! Recaching image...", indent=1)
                        numLevels, width, height, data = self._finalize_cache(texcache, key, image, name, compression, dxt)
                        self._finalize_bitmap(key, owners, name, numLevels, width, height, compression, dxt, data)

                inc_progress()

    def _finalize_bitmap(self, key, owners, name, numLevels, width, height, compression, dxt, data):
        mgr = self._mgr

        # Now we poke our new bitmap into the pending layers. Note that we have to do some funny
        # business to account for per-page textures
        pages = {}

        self._report.msg("Adding to...", indent=1)
        for owner_key in owners:
            owner = owner_key.object
            self._report.msg("[{} '{}']", owner.ClassName()[2:], owner_key.name, indent=2)
            page = mgr.get_textures_page(owner_key) # Layer's page or Textures.prp

            # If we haven't created this texture in the page (either layer's page or Textures.prp),
            # then we need to do that and stuff the level data. This is a little tedious, but we
            # need to be careful to manage our resources correctly
            if page not in pages:
                mipmap = plMipmap(name=name, width=width, height=height, numLevels=numLevels,
                                  compType=compression, format=plBitmap.kRGB8888, dxtLevel=dxt)
                if key.is_cube_map:
                    assert len(data) == 6
                    texture = plCubicEnvironmap(name)
                    for face_name, face_data in zip(BLENDER_CUBE_MAP, data):
                        for i in range(numLevels):
                            mipmap.setLevel(i, face_data[i])
                        setattr(texture, face_name, mipmap)
                else:
                    assert len(data) == 1
                    for i in range(numLevels):
                        mipmap.setLevel(i, data[0][i])
                    texture = mipmap

                mgr.AddObject(page, texture)
                pages[page] = texture
            else:
                texture = pages[page]

            # The object that references this image can be either a layer (will appear
            # in the 3d world) or an image library (will appear in a journal or in another
            # dynamic manner in game)
            if isinstance(owner, plLayerInterface):
                owner.texture = texture.key
            elif isinstance(owner, plImageLibMod):
                owner.addImage(texture.key)
            else:
                raise NotImplementedError(owner.ClassName())

    def _finalize_cache(self, texcache, key, image, name, compression, dxt):
        if key.is_cube_map:
            numLevels, width, height, data = self._finalize_cube_map(key, image, name, compression, dxt)
        else:
            numLevels, width, height, data = self._finalize_single_image(key, image, name, compression, dxt)
        texcache.add_texture(key, numLevels, (width, height), compression, data)
        return numLevels, width, height, data

    def _finalize_cube_map(self, key, image, name, compression, dxt):
        oWidth, oHeight = image.size
        if oWidth == 0 and oHeight == 0:
            raise ExportError("Image '{}' could not be loaded.".format(image.name))

        # Non-DXT images are BGRA in Plasma
        bgra = compression != plBitmap.kDirectXCompression

        # Grab the cube map data from OpenGL and prepare to begin...
        with GLTexture(key, bgra=bgra) as glimage:
            cWidth, cHeight, data = glimage.image_data

        # On some platforms, Blender will be "helpful" and scale the image to a POT.
        # That's great, but we have 3 faces as a width, which will certainly be NPOT
        # in the case of POT faces. So, we will scale the image AGAIN, if Blender did
        # something funky.
        if oWidth != cWidth or oHeight != cHeight:
            self._report.warn("Image was resized by Blender to ({}x{})--resizing the resize to ({}x{})",
                              cWidth, cHeight, oWidth, oHeight, indent=1)
            data = scale_image(data, cWidth, cHeight, oWidth, oHeight)

        # Face dimensions
        fWidth, fHeight = oWidth // 3, oHeight // 2

        # Copy each of the six faces into a separate image buffer.
        # NOTE: At present, I am well pleased with the speed of this functionality.
        #       According to my profiling, it takes roughly 0.7 seconds to process a
        #       cube map whose faces are 1024x1024 (3072x2048 total). Maybe a later
        #       commit will move this into korlib. We'll see.
        face_num = len(BLENDER_CUBE_MAP)
        face_images = [None] * face_num
        for i in range(face_num):
            col_id = i if i < 3 else i - 3
            row_start = 0 if i < 3 else fHeight
            row_end = fHeight if i < 3 else oHeight

            face_data = bytearray(fWidth * fHeight * 4)
            for row_current in range(row_start, row_end, 1):
                src_start_idx = (row_current * oWidth * 4) + (col_id * fWidth * 4)
                src_end_idx = src_start_idx + (fWidth * 4)
                dst_start_idx = (row_current - row_start) * fWidth * 4
                dst_end_idx = dst_start_idx + (fWidth * 4)
                face_data[dst_start_idx:dst_end_idx] = data[src_start_idx:src_end_idx]
            face_images[i] = bytes(face_data)

        # Now that we have our six faces, we'll toss them into the GLTexture helper
        # to generate mipmaps, if needed...
        for i, face_name in enumerate(BLENDER_CUBE_MAP):
            glimage = GLTexture(key)
            glimage.image_data = fWidth, fHeight, face_images[i]
            eWidth, eHeight = glimage.size_pot
            name = face_name[:-4].upper()
            if compression == plBitmap.kDirectXCompression:
                numLevels = glimage.num_levels
                self._report.msg("Generating mip levels for cube face '{}'", name, indent=1)

                # If we're compressing this mofo, we'll need a temporary mipmap to do that here...
                mipmap = plMipmap(name=name, width=eWidth, height=eHeight, numLevels=numLevels,
                                  compType=compression, format=plBitmap.kRGB8888, dxtLevel=dxt)
            else:
                numLevels = 1
                self._report.msg("Compressing single level for cube face '{}'", name, indent=1)

            face_images[i] = [None] * numLevels
            for j in range(numLevels):
                level_data = glimage.get_level_data(j, key.calc_alpha, report=self._report)
                if compression == plBitmap.kDirectXCompression:
                    mipmap.CompressImage(j, level_data)
                    level_data = mipmap.getLevel(j)
                face_images[i][j] = level_data
        return numLevels, eWidth, eHeight, face_images

    def _finalize_single_image(self, key, image, name, compression, dxt):
        oWidth, oHeight = image.size
        if oWidth == 0 and oHeight == 0:
            raise ExportError("Image '{}' could not be loaded.".format(image.name))

        # Non-DXT images are BGRA in Plasma
        bgra = compression != plBitmap.kDirectXCompression

        # Grab the image data from OpenGL and stuff it into the plBitmap
        with GLTexture(key, bgra=bgra) as glimage:
            eWidth, eHeight = glimage.size_pot
            if compression == plBitmap.kDirectXCompression:
                numLevels = glimage.num_levels
                self._report.msg("Generating mip levels", indent=1)

                # If this is a DXT-compressed mipmap, we need to use a temporary mipmap
                # to do the compression. We'll then steal the data from it.
                mipmap = plMipmap(name=name, width=eWidth, height=eHeight, numLevels=numLevels,
                                  compType=compression, format=plBitmap.kRGB8888, dxtLevel=dxt)
            else:
                numLevels = 1
                self._report.msg("Compressing single level", indent=1)

            # Hold the uncompressed level data for now. We may have to make multiple copies of
            # this mipmap for per-page textures :(
            data = [None] * numLevels
            for i in range(numLevels):
                level_data = glimage.get_level_data(i, key.calc_alpha, report=self._report)
                if compression == plBitmap.kDirectXCompression:
                    mipmap.CompressImage(i, level_data)
                    level_data = mipmap.getLevel(i)
                data[i] = level_data
        return numLevels, eWidth, eHeight, [data,]

    def get_materials(self, bo):
        return self._obj2mat.get(bo, [])

    def get_bump_layer(self, bo):
        return self._bump_mats.get(bo, None)

    def get_texture_animation_key(self, bo, bm, texture):
        """Finds or creates the appropriate key for sending messages to an animated Texture"""

        tex_name = texture.name
        if not tex_name in bm.texture_slots:
            raise ExportError("Texture '{}' not used in Material '{}'".format(bm.name, tex_name))

        name = "{}_{}_LayerAnim".format(bm.name, tex_name)
        layer = texture.plasma_layer
        pClass = plLayerSDLAnimation if layer.anim_sdl_var else plLayerAnimation
        return self._mgr.find_create_key(pClass, bl=bo, name=name)

    @property
    def _mgr(self):
        return self._exporter().mgr

    def _propagate_material_settings(self, bm, layer):
        """Converts settings from the Blender Material to corresponding plLayer settings"""
        state = layer.state

        # Shade Flags
        if not bm.use_mist:
            state.shadeFlags |= hsGMatState.kShadeNoFog # Dead in CWE
            state.shadeFlags |= hsGMatState.kShadeReallyNoFog

        if bm.use_shadeless:
            state.shadeFlags |= hsGMatState.kShadeWhite

        # Colors
        layer.ambient = utils.color(bpy.context.scene.world.ambient_color)
        layer.preshade = utils.color(bm.diffuse_color)
        layer.runtime = utils.color(bm.diffuse_color)
        layer.specular = utils.color(bm.specular_color)

        layer.specularPower = min(100.0, float(bm.specular_hardness))
        layer.LODBias = -1.0 # Seems to be the Plasma default

        if bm.emit > 0.0:
            # Use the diffuse colour as the emit, scaled by the emit amount
            # (maximum 2.0, so we'll also scale that by 0.5)
            emit_scale = bm.emit * 0.5
            layer.ambient = hsColorRGBA(bm.diffuse_color.r * emit_scale,
                                        bm.diffuse_color.g * emit_scale,
                                        bm.diffuse_color.b * emit_scale,
                                        1.0)

    @property
    def _report(self):
        return self._exporter().report

    def _requires_single_user_material(self, bo, bm):
        modifiers = bo.plasma_modifiers
        if modifiers.lightmap.bake_lightmap:
            return True
        if modifiers.water_basic.enabled:
            return True
        return False

    def _test_image_alpha(self, image):
        """Tests to see if this image has any alpha data"""

        # In the interest of speed, let's see if we've already done this one...
        result = self._alphatest.get(image, None)
        if result is not None:
            return result

        if image.channels != 4:
            result = False
        elif not image.use_alpha:
            result = False
        else:
            # Using bpy.types.Image.pixels is VERY VERY VERY slow...
            key = _Texture(image=image)
            with GLTexture(key, fast=True) as glimage:
                result = glimage.has_alpha

        self._alphatest[image] = result
        return result

    @property
    def _texcache(self):
        return self._exporter().image
