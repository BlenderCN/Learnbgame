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
# ***** END GPL LICENCE BLOCK *****

import mathutils

from ..extensions_framework import util as efutil

from ..export import Instance
from ..export.geometry import GeometryExporter
from ..export.materials import export_material
from ..export.environment import export_world_environment


def preview_scene(scene, export_ctx, obj=None, mat=None, tex=None):
    xres, yres = scene.camera.data.mitsuba_camera.mitsuba_film.resolution(scene)

    film = {
        'type': 'ldrfilm',
        'width': xres,
        'height': yres,
        'fileFormat': 'png',
        'pixelFormat': 'rgb',
        'tonemapMethod': 'gamma',
        'gamma': -1.0,
        'exposure': 0.0,
        'banner': False,
        'highQualityEdges': False,
        'rfilter': {
            'type': 'gaussian',
            'stddev': 0.5,
        },
    }

    if obj is not None and mat is not None:
        preview_spp = int(efutil.find_config_value('mitsuba', 'defaults', 'preview_spp', '16'))
        preview_depth = int(efutil.find_config_value('mitsuba', 'defaults', 'preview_depth', '2'))

        # Integrator
        export_ctx.data_add({
            'type': 'volpath',
            'maxDepth': preview_depth,
        })

        # Camera
        export_ctx.data_add({
            'type': 'perspective',
            'toWorld': export_ctx.transform_lookAt([0, -27.931367, 1.800838], [-0.006218, 0.677149, 1.801573], [0, 0, 1]),
            'sampler': {
                'type': 'independent',
                'sampleCount': preview_spp,
            },
            'film': film,
        })

        # Checkerboard texture
        export_ctx.data_add({
            'type': 'diffuse',
            'id': 'checkers',
            'reflectance': {
                'type': 'checkerboard',
                'color0': export_ctx.spectrum(0.2),
                'color1': export_ctx.spectrum(0.4),
                'uscale': 10.0,
                'vscale': 10.0,
                'uoffset': 0.0,
                'voffset': 0.0,
            },
        })

        export_ctx.data_add({
            'type': 'rectangle',
            'id': 'plane-floor',
            'toWorld': export_ctx.transform_matrix(mathutils.Matrix(((40, 0, 0, 0), (0, -40, 0, 0), (0, 0, 1, -2.9), (0, 0, 0, 1)))),
            'bsdf': {
                'type': 'ref',
                'id': 'checkers',
            },
        })

        export_ctx.data_add({
            'type': 'rectangle',
            'id': 'plane-back',
            'toWorld': export_ctx.transform_matrix(mathutils.Matrix(((40, 0, 0, 0), (0, 0, -1, 10), (0, 40, 0, 17.1), (0, 0, 0, 1)))),
            'bsdf': {
                'type': 'ref',
                'id': 'checkers',
            },
        })

        # preview object
        pv_export_shape = True
        emitter = False

        if mat.preview_render_type == 'HAIR':
            # Hair
            pv_export_shape = False

        elif mat.preview_render_type == 'SPHERE_A':
            # Sphere A
            pv_export_shape = False

        if pv_export_shape:  # Any material, texture, light, or volume definitions created from the node editor do not exist before this conditional!
            GE = GeometryExporter(export_ctx, scene)
            GE.is_preview = True
            GE.geometry_scene = scene

            for mesh_mat, mesh_name, mesh_type, mesh_params, seq in GE.writeMesh(obj, file_format='serialized'):
                if tex is not None:
                    # Tex
                    pass

                else:
                    shape = {
                        'type': mesh_type,
                        'id': '%s_%s-shape' % (obj.name, mesh_name),
                        'toWorld': export_ctx.transform_matrix(obj.matrix_world.copy())
                    }
                    shape.update(mesh_params)

                    mat_params = export_material(export_ctx, mat)

                    if mat_params:
                        shape.update(mat_params)

                        if 'emitter' in mat_params:
                            emitter = True

                    export_ctx.data_add(shape)

        if emitter:
            return

        # Emitters
        export_ctx.data_add({
            'type': 'sunsky',
            'scale': 2.0,
            'sunRadiusScale': 15.0,
            'extend': True,
            'toWorld': export_ctx.transform_matrix(
                mathutils.Euler((0, 0, 20)).to_matrix().to_4x4() * mathutils.Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
            )
        })

    else:
        # Integrator
        export_ctx.data_add({
            'type': 'direct',
            'maxDepth': 1,
        })

        # Camera
        export_ctx.data_add({
            'type': 'spherical',
            'toWorld': export_ctx.transform_lookAt([0, 0, 0], [0, -1, 0], [0, 0, 1]),
            'sampler': {
                'type': 'independent',
                'sampleCount': 1,
            },
            'film': film,
        })

        world_environment = Instance(scene.world, None)
        export_world_environment(export_ctx, world_environment, is_preview=True)
