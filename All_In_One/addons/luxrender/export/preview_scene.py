# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 LuxRender Add-On
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
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
# ***** END GPL LICENCE BLOCK *****
#
import bpy

from ..export import ParamSet
from ..export.geometry import GeometryExporter
from ..export.materials import ExportedTextures, convert_texture, get_material_volume_defs, get_preview_flip, \
    get_preview_zoom
from ..outputs import LuxLog, LuxManager
from ..outputs.pure_api import LUXRENDER_VERSION
from ..properties import find_node
from ..properties.node_material import luxrender_texture_maker


def export_preview_texture(lux_context, texture):
    texture_name = texture.name
    if texture.luxrender_texture.type != 'BLENDER':
        tex_luxrender_texture = texture.luxrender_texture
        lux_tex_variant, paramset = tex_luxrender_texture.get_paramset(LuxManager.CurrentScene, texture)
        lux_tex_name = tex_luxrender_texture.type
    else:
        lux_tex_variant, lux_tex_name, paramset = convert_texture(LuxManager.CurrentScene, texture,
                                                                  variant_hint='color')
        if texture.type in ('OCEAN', 'IMAGE'):
            texture_name = texture_name + "_" + lux_tex_variant

            # running bonds shown from the side in tex-preview
    if texture.luxrender_texture.type == 'brick' and texture.luxrender_texture.luxrender_tex_brick.brickbond in (
            'running', 'flemish'):
        brick_rot = texture.luxrender_texture.luxrender_tex_transform.rotate[:]
        paramset.add_vector('rotate', [brick_rot[0] + 90, brick_rot[1], brick_rot[2]])

    # if lux_tex_variant == 'color':
    ExportedTextures.texture(lux_context, texture_name, lux_tex_variant, lux_tex_name, paramset)
    if lux_tex_variant == 'float':
        mix_params = ParamSet() \
            .add_texture('amount', texture_name) \
            .add_color('tex1', [0.05, 0.05, 0.05]) \
            .add_color('tex2', [0.85, 0.85, 0.85])

        texture_name += "_color"
        ExportedTextures.texture(lux_context, texture_name, 'color', 'mix', mix_params)

    elif lux_tex_variant != 'color':
        LuxLog('WARNING: Texture %s is wrong variant; needed %s, got %s' % (texture_name, 'color', lux_tex_variant))

    return texture_name


def preview_scene(scene, lux_context, obj=None, mat=None, tex=None):
    mat_preview_xz = get_preview_flip(mat)
    preview_zoom = get_preview_zoom(mat)

    # Camera
    if tex is not None:  # texture preview is always topview
        lux_context.lookAt(0.0, 0.0, 4.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        camera_params = ParamSet().add_float('fov', 22.5)
    elif mat.preview_render_type == 'FLAT' and not mat_preview_xz and tex is None:  # mat preview XZ-flip
        lux_context.lookAt(0.0, 0.0, 4.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        camera_params = ParamSet().add_float('fov', 22.5 / preview_zoom)
    else:
        lux_context.lookAt(0.0, -3.0, 0.5, 0.0, -2.0, 0.5, 0.0, 0.0, 1.0)  # standard sideview
        camera_params = ParamSet().add_float('fov', 22.5 / preview_zoom)

    lux_context.camera('perspective', camera_params)

    # Film
    xr, yr = scene.camera.data.luxrender_camera.luxrender_film.resolution(scene)

    film_params = ParamSet() \
        .add_integer('xresolution', xr) \
        .add_integer('yresolution', yr) \
        .add_string('filename', 'luxblend25-preview') \
        .add_bool('write_exr_ZBuf', True) \
        .add_bool('write_exr_applyimaging', True) \
        .add_string('write_exr_channels', 'RGBA') \
        .add_bool('write_exr_halftype', False) \
        .add_bool('write_png', False) \
        .add_bool('write_tga', False) \
        .add_bool('write_resume_flm', False) \
        .add_integer('displayinterval', 300) \
        .add_float('haltthreshold', 0.005) \
        .add_integer('halttime', 30) \
        .add_string('tonemapkernel', 'linear') \
        .add_string('ldr_clamp_method', 'hue') \
        .add_integer('tilecount', 2) \
        .add_float('convergencestep', 4)

    if tex is not None:
        film_params.add_float('haltthreshold', 0.999)  # testcommit to reduce texture flat rendertimes

    film_params.add_float('gamma', 1.0)
    film_params.add_float('linear_exposure', 1.25)

    film_params \
        .add_bool('write_exr', False) \
        .add_integer('writeinterval', 2)
    lux_context.film('fleximage', film_params)

    # Pixel Filter
    pixelfilter_params = ParamSet() \
        .add_float('xwidth', 1.5) \
        .add_float('ywidth', 1.5) \
        .add_float('B', 0.333) \
        .add_float('C', 0.333) \
        .add_bool('supersample', True)
    lux_context.pixelFilter('mitchell', pixelfilter_params)

    # Sampler
    sampler_params = ParamSet() \
        .add_bool('usecooldown', False) \
        .add_float('largemutationprob', 0.25) \
        .add_integer('maxconsecrejects', 1024) \
        .add_bool('noiseaware', True)
    lux_context.sampler('metropolis', sampler_params)

    # Surface Integrator	# 'powerimp' crashes alot on fast multicores, so changed to 'all' for now
    surfaceintegrator_params = ParamSet() \
        .add_string('lightstrategy', 'all') \
        .add_string('lightpathstrategy', 'all') \
        .add_integer('eyedepth', 12) \
        .add_integer('lightdepth', 8) \
        .add_integer('lightraycount', 1) \
        .add_integer('shadowraycount', 1)
    lux_context.surfaceIntegrator('bidirectional', surfaceintegrator_params)

    # Volume Integrator
    lux_context.volumeIntegrator('multi', ParamSet())

    # Accelerator
    lux_context.accelerator('qbvh', ParamSet())
    lux_context.worldBegin()
    bl_scene = LuxManager.CurrentScene  # actual blender scene keeping default volumes

    # Collect volumes from all scenes *sigh*
    for scn in bpy.data.scenes:
        LuxManager.SetCurrentScene(scn)

        for volume in scn.luxrender_volumes.volumes:
            if volume.type == 'heterogeneous':
                vol_param = ParamSet().add_color('sigma_s', (1.0, 1.0, 1.0))
                lux_context.makeNamedVolume(volume.name, 'heterogeneous', vol_param)
            else:
                lux_context.makeNamedVolume(volume.name, *volume.api_output(lux_context))

    LuxManager.SetCurrentScene(scene)  # for preview context

    # Light
    # For usability, previev_scale is not an own property but calculated from the object dimensions
    # A user can directly judge mappings on an adjustable object_size, we simply scale the whole preview
    preview_scale = bl_scene.luxrender_world.preview_object_size / 2
    lux_context.attributeBegin()
    if mat.preview_render_type == 'FLAT' and mat_preview_xz:
        lux_context.transform([
            0.5, 0.0, 0.0, 0.0,
            0.0, 0.5, 0.0, 0.0,
            0.0, 0.0, 0.5, 0.0,
            2.5, -2.5, 2.5, 1.0
        ])
        light_bb_params = ParamSet().add_float('temperature', 6500.0)
        lux_context.texture('pL', 'color', 'blackbody', light_bb_params)
        light_params = ParamSet() \
            .add_texture('L', 'pL') \
            .add_float('gain', 1.5 / preview_scale) \
            .add_float('importance', 1.0)
    elif mat.preview_render_type == 'FLAT' and not mat_preview_xz:
        lux_context.transform([
            0.5, 0.0, 0.0, 0.0,
            0.0, 0.5, 0.0, 0.0,
            0.0, 0.0, 0.5, 0.0,
            2.5, -2.5, 4.5, 0.3
        ])
        lux_context.translate(-2, 1, 5)
        light_bb_params = ParamSet().add_float('temperature', 6500.0)
        lux_context.texture('pL', 'color', 'blackbody', light_bb_params)
        light_params = ParamSet() \
            .add_texture('L', 'pL') \
            .add_float('gain', 7.0 / preview_scale) \
            .add_float('importance', 1.0)
    else:
        lux_context.transform([
            0.5996068120002747, 0.800294816493988, 2.980232594040899e-08, 0.0,
            -0.6059534549713135, 0.45399996638298035, 0.6532259583473206, 0.0,
            0.5227733850479126, -0.3916787803173065, 0.7571629285812378, 0.0,
            4.076245307922363, -3.0540552139282227, 5.903861999511719, 1.0
        ])
        light_bb_params = ParamSet().add_float('temperature', 6500.0)
        lux_context.texture('pL', 'color', 'blackbody', light_bb_params)
        light_params = ParamSet() \
            .add_texture('L', 'pL') \
            .add_float('gain', 1.0 / preview_scale) \
            .add_float('importance', 1.0)

    if bl_scene.luxrender_world.default_exterior_volume:
        lux_context.exterior(bl_scene.luxrender_world.default_exterior_volume)

    lux_context.areaLightSource('area', light_params)
    areax = 1
    areay = 1
    points = [-areax / 2.0, areay / 2.0, 0.0, areax / 2.0, areay / 2.0, 0.0, areax / 2.0, -areay / 2.0, 0.0,
              -areax / 2.0, -areay / 2.0, 0.0]

    shape_params = ParamSet()
    shape_params.add_integer('ntris', 6)
    shape_params.add_integer('nvertices', 4)
    shape_params.add_integer('indices', [0, 1, 2, 0, 2, 3])
    shape_params.add_point('P', points)

    if tex is None:
        lux_context.shape('trianglemesh', shape_params)

    lux_context.attributeEnd()

    # Add a background color (light)
    if bl_scene.luxrender_world.default_exterior_volume:
        lux_context.exterior(bl_scene.luxrender_world.default_exterior_volume)

    if tex is None:
        inf_gain = 0.1
    else:
        inf_gain = 1.2

    lux_context.lightSource('infinite', ParamSet().add_float('gain', inf_gain).add_float('importance', inf_gain))

    # back drop
    if mat.preview_render_type == 'FLAT' and mat_preview_xz and tex is None:
        lux_context.attributeBegin()
        lux_context.transform([
            5.0, 0.0, 0.0, 0.0,
            0.0, 5.0, 0.0, 0.0,
            0.0, 0.0, 5.0, 0.0,
            0.0, 10.0, 0.0, 1.0
        ])
        lux_context.scale(4, 1, 1)
        lux_context.rotate(90, 1, 0, 0)
        checks_pattern_params = ParamSet() \
            .add_integer('dimension', 2) \
            .add_string('mapping', 'uv') \
            .add_float('uscale', 36.8) \
            .add_float('vscale', 36.0 * 4)
        lux_context.texture('checks::pattern', 'float', 'checkerboard', checks_pattern_params)
        checks_params = ParamSet() \
            .add_texture('amount', 'checks::pattern') \
            .add_color('tex1', [0.75, 0.75, 0.75]) \
            .add_color('tex2', [0.05, 0.05, 0.05])
        lux_context.texture('checks', 'color', 'mix', checks_params)
        mat_params = ParamSet().add_texture('Kd', 'checks')
        lux_context.material('matte', mat_params)
        bd_shape_params = ParamSet() \
            .add_integer('ntris', 6) \
            .add_integer('nvertices', 4) \
            .add_integer('indices', [0, 1, 2, 0, 2, 3]) \
            .add_point('P', [
                1.0, 1.0, 0.0,
                -1.0, 1.0, 0.0,
                -1.0, -1.0, 0.0,
                1.0, -1.0, 0.0,
        ]) \
            .add_normal('N', [
                0.0, 0.0, 1.0,
                0.0, 0.0, 1.0,
                0.0, 0.0, 1.0,
                0.0, 0.0, 1.0,
        ]) \
            .add_float('uv', [
                0.333334, 0.000000,
                0.333334, 0.333334,
                0.000000, 0.333334,
                0.000000, 0.000000,
        ])
        lux_context.shape('loopsubdiv', bd_shape_params)
    else:  # sideview
        lux_context.attributeBegin()
        lux_context.transform([
            5.0, 0.0, 0.0, 0.0,
            0.0, 5.0, 0.0, 0.0,
            0.0, 0.0, 5.0, 0.0,
            0.0, 0.0, 0.0, 1.0
        ])

        if mat.preview_render_type == 'FLAT':
            lux_context.translate(-0.31, -0.22, -1.2)

        lux_context.scale(4, 1, 1)
        checks_pattern_params = ParamSet() \
            .add_integer('dimension', 2) \
            .add_string('mapping', 'uv') \
            .add_float('uscale', 36.8) \
            .add_float('vscale', 36.0 * 4)  # .add_string('aamode', 'supersample') \
        lux_context.texture('checks::pattern', 'float', 'checkerboard', checks_pattern_params)
        checks_params = ParamSet() \
            .add_texture('amount', 'checks::pattern') \
            .add_color('tex1', [0.75, 0.75, 0.75]) \
            .add_color('tex2', [0.05, 0.05, 0.05])
        lux_context.texture('checks', 'color', 'mix', checks_params)
        mat_params = ParamSet().add_texture('Kd', 'checks')
        lux_context.material('matte', mat_params)
        bd_shape_params = ParamSet() \
            .add_integer('nlevels', 3) \
            .add_bool('dmnormalsmooth', True) \
            .add_bool('dmsharpboundary', False) \
            .add_integer('ntris', 18) \
            .add_integer('nvertices', 8) \
            .add_integer('indices', [0, 1, 2, 0, 2, 3, 1, 0, 4, 1, 4, 5, 5, 4, 6, 5, 6, 7]) \
            .add_point('P', [
                1.0, 1.0, 0.0,
                -1.0, 1.0, 0.0,
                -1.0, -1.0, 0.0,
                1.0, -1.0, 0.0,
                1.0, 3.0, 0.0,
                -1.0, 3.0, 0.0,
                1.0, 3.0, 2.0,
                -1.0, 3.0, 2.0,
        ]) \
            .add_normal('N', [
                0.0, 0.000000, 1.000000,
                0.0, 0.000000, 1.000000,
                0.0, 0.000000, 1.000000,
                0.0, 0.000000, 1.000000,
                0.0, -0.707083, 0.707083,
                0.0, -0.707083, 0.707083,
                0.0, -1.000000, 0.000000,
                0.0, -1.000000, 0.000000,
        ]) \
            .add_float('uv', [
                0.333334, 0.000000,
                0.333334, 0.333334,
                0.000000, 0.333334,
                0.000000, 0.000000,
                0.666667, 0.000000,
                0.666667, 0.333333,
                1.000000, 0.000000,
                1.000000, 0.333333,
        ])
        lux_context.shape('loopsubdiv', bd_shape_params)

    if bl_scene.luxrender_world.default_interior_volume:
        lux_context.interior(bl_scene.luxrender_world.default_interior_volume)

    if bl_scene.luxrender_world.default_exterior_volume:
        lux_context.exterior(bl_scene.luxrender_world.default_exterior_volume)

    lux_context.attributeEnd()

    if obj is not None and mat is not None:
        # preview object
        lux_context.attributeBegin()
        lux_context.identity()
        pv_transform = [
            0.5, 0.0, 0.0, 0.0,
            0.0, 0.5, 0.0, 0.0,
            0.0, 0.0, 0.5, 0.0,
            0.0, 0.0, 0.5, 1.0
        ]
        pv_export_shape = True

        if mat.preview_render_type == 'FLAT':
            if tex is None:
                if mat_preview_xz:
                    lux_context.scale(1, 1, 8)
                    lux_context.rotate(90, 1, 0, 0)
                    pv_transform = [
                        0.1, 0.0, 0.0, 0.0,
                        0.0, 0.1, 0.0, 0.0,
                        0.0, 0.0, 0.2, 0.0,
                        0.0, 0.06, -1, 1.0
                    ]
                else:
                    lux_context.scale(0.25, 2.0, 2.0)
                    lux_context.translate(0, 0, -0.99)
            else:
                lux_context.rotate(90, 0, 0, 1)  # keep tex pre always same
                lux_context.scale(2.0, 2.0, 2.0)
                lux_context.translate(0, 0, -1)

        if mat.preview_render_type == 'SPHERE':
            pv_transform = [
                0.1, 0.0, 0.0, 0.0,
                0.0, 0.1, 0.0, 0.0,
                0.0, 0.0, 0.1, 0.0,
                0.0, 0.0, 0.5, 1.0
            ]

        if mat.preview_render_type == 'CUBE':
            lux_context.scale(0.8, 0.8, 0.8)
            lux_context.rotate(-35, 0, 0, 1)

        if mat.preview_render_type == 'MONKEY':
            pv_transform = [
                1.0573405027389526, 0.6340668201446533, 0.0, 0.0,
                -0.36082395911216736, 0.601693332195282, 1.013795018196106, 0.0,
                0.5213892459869385, -0.8694445490837097, 0.7015902996063232, 0.0,
                0.0, 0.0, 0.5, 1.0
            ]

        if mat.preview_render_type == 'HAIR':
            pv_export_shape = False

        if mat.preview_render_type == 'SPHERE_A':
            pv_export_shape = False

        lux_context.concatTransform(pv_transform)

        # Any material, texture, light, or volume definitions created from the node
        # editor do not exist before this conditional!
        if pv_export_shape:
            GE = GeometryExporter(lux_context, scene)
            GE.is_preview = True
            GE.geometry_scene = scene

            for mesh_mat, mesh_name, mesh_type, mesh_params in GE.buildNativeMesh(obj):
                if tex is not None:
                    lux_context.transformBegin()
                    lux_context.identity()
                    texture_name = export_preview_texture(lux_context, tex)
                    lux_context.transformEnd()

                    lux_context.material('matte', ParamSet().add_texture('Kd', texture_name))
                else:
                    mat.luxrender_material.export(scene, lux_context, mat, mode='direct')
                    int_v, ext_v = get_material_volume_defs(mat)

                    if int_v or ext_v:
                        if int_v:
                            lux_context.interior(int_v)

                        if ext_v:
                            lux_context.exterior(ext_v)

                    if not int_v and bl_scene.luxrender_world.default_interior_volume:
                        lux_context.interior(bl_scene.luxrender_world.default_interior_volume)

                    if not ext_v and bl_scene.luxrender_world.default_exterior_volume:
                        lux_context.exterior(bl_scene.luxrender_world.default_exterior_volume)

                    output_node = find_node(mat, 'luxrender_material_output_node')

                    if mat.luxrender_material.nodetree:
                        object_is_emitter = False

                        if output_node is not None:
                            light_socket = output_node.inputs[3]

                            if light_socket.is_linked:
                                light_node = light_socket.links[0].from_node
                                object_is_emitter = light_socket.is_linked
                    else:
                        object_is_emitter = hasattr(mat, 'luxrender_emission') and mat.luxrender_emission.use_emission

                    if object_is_emitter:
                        if not mat.luxrender_material.nodetree:
                            # lux_context.lightGroup(mat.luxrender_emission.lightgroup, [])
                            lux_context.areaLightSource(*mat.luxrender_emission.api_output(obj))
                        else:
                            tex_maker = luxrender_texture_maker(lux_context, mat.luxrender_material.nodetree)
                            lux_context.areaLightSource(*light_node.export(tex_maker.make_texture))

                lux_context.shape(mesh_type, mesh_params)
        else:
            lux_context.shape('sphere', ParamSet().add_float('radius', 1.0))

        lux_context.attributeEnd()

    # Default 'Camera' Exterior, just before WorldEnd
    if bl_scene.luxrender_world.default_exterior_volume:
        lux_context.exterior(bl_scene.luxrender_world.default_exterior_volume)

    return int(xr), int(yr)

