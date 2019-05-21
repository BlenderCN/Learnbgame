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

from ..export import get_worldscale


def lookAt(matrix):
    '''
    Derive a list describing 3 points for a Mitsuba LookAt statement

    Returns     3 tuple(3) (floats)
    '''

    ws = get_worldscale()
    matrix *= ws
    ws = get_worldscale(as_scalematrix=False)
    matrix[0][3] *= ws
    matrix[1][3] *= ws
    matrix[2][3] *= ws
    # transpose to extract columns
    matrix = matrix.transposed()
    pos = matrix[3]
    forwards = -matrix[2]
    target = (pos + forwards)
    up = matrix[1]

    return (pos, target, up)


def export_camera_instance(export_ctx, instance, scene):
    cam = instance.obj
    mcam = cam.data.mitsuba_camera

    params = mcam.api_output(scene)

    if params and 'type' in params:
        motion = instance.motion
        lookat = []
        scale_factor = 1.0

        if not motion:
            cam_trafo = (cam.matrix_world.copy(),
                cam.ortho_scale / 2.0 if cam.type == 'ORTHO' else None)
            motion = [(0.0, cam_trafo)]

        if cam.type == 'ORTHO':
            aspect = params['film']['width'] / params['film']['height']

            if params['film']['fitHorizontal'] and aspect < 1.0:
                scale_factor /= aspect

            elif not params['film']['fitHorizontal'] and aspect > 1.0:
                scale_factor *= aspect

        for (seq, (trafo, scale)) in motion:
            origin, target, up = lookAt(trafo)

            if scale is not None:
                scale *= scale_factor

            lookat.append((seq, (origin, target, up, scale)))

        params['toWorld'] = export_ctx.animated_lookAt(lookat)

        export_ctx.data_add(params)
