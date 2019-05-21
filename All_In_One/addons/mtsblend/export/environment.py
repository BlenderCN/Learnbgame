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

import mathutils


# TODO: convert blender and cycles environment to mitsuba dict
def world_dict_to_nodes(ntree, params):
    return None


def blender_world_to_dict(export_ctx, world):
    return None


def blender_world_to_nodes(ntree, world):
    params = blender_world_to_dict(None, world)

    if params:
        return world_dict_to_nodes(ntree, params)

    return None
# TODO: all of the above


def get_environment_trafo(world):
    try:
        ntree = world.mitsuba_nodes.get_node_tree()
        world_node = ntree.find_node('MtsNodeWorldOutput')
        environment = world_node.inputs['Environment'].get_linked_node()

        return environment.get_environment_transform()

    except:
        return None


def export_world_environment(export_ctx, world_environment, is_preview=False):
    if world_environment.obj is None:
        return

    world = world_environment.obj
    ntree = world.mitsuba_nodes.get_node_tree()
    params = {}

    if ntree:
        params = ntree.get_nodetree_dict(export_ctx, world)

    #if not params:
        #params = blender_world_to_dict(export_ctx, world)

        #return

    if params and 'type' in params:

        if params['type'] in {'envmap', 'sun', 'sky', 'sunsky'}:
            motion = world_environment.motion

            if not motion:
                trafo = get_environment_trafo(world)

                if trafo is not None:
                    motion = [(0.0, trafo)]

                else:
                    motion = [(0.0, mathutils.Matrix())]

            params.update({
                'toWorld': export_ctx.animated_transform(
                    [(t, m * mathutils.Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))) for (t, m) in motion]
                )
            })

            if 'sunDirection' in params:
                direction = mathutils.Vector(params['sunDirection'])
                direction.rotate(motion[0][1])
                params.update({
                    'sunDirection': export_ctx.vector(direction[0], direction[1], direction[2]),
                })

        export_ctx.data_add(params)

    elif is_preview:
        export_ctx.data_add({'type': 'constant', 'radiance': export_ctx.spectrum(0)})
