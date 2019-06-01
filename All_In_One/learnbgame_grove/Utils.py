# coding=utf-8

""" Library of miscellaneous functionality for The Grove.

    Copyright (c) 2016 - 2018, Wybren van Keulen, The Grove. """


from mathutils import Matrix, Vector, Quaternion
from math import sin, cos, acos, sqrt
from numpy import take, repeat, empty, ones
from numpy import arange, column_stack, argsort, split, where, diff
from numpy import concatenate, array
from .Translation import t

from bpy import app

add_alpha_to_vertex_colors = False
if app.version[1] > 2.78 and app.version[2] > 0:
    add_alpha_to_vertex_colors = True


def two_point_transform(origin, target):

    quat = (target - origin).to_track_quat('X', 'Z')
    mat_rotation = quat.to_matrix()
    mat_rotation.resize_4x4()

    return Matrix.Translation(origin) @ mat_rotation


def deviate(branch_angle, branching, twist, initial_phyllotaxic_angle, plagiotropism_buds, gravitropism_buds, parent_direction, i, j):

    direction = parent_direction.normalized()

    axis = direction.to_track_quat('X', 'Z') @ Vector((0.0, 0.0, 1.0))

    deviate_dir = Quaternion(axis, branch_angle) @ direction

    offset = 0.0
    if branching == 1:
        offset = 2.4
    elif branching == 2:
        offset = 1.5708 + twist
    elif branching == 3:
        offset = 2.4
    elif branching == 4:
        offset = 0.7854 + twist
    elif branching == 5:
        offset = 0.6283
    elif branching == 6:
        offset = 0.5236

    phyllotaxis_angle = initial_phyllotaxic_angle + offset * i
    phyllotaxis_angle += 6.2832 * j / branching
    phyllotaxis_angle %= 6.2832

    flat_dir = parent_direction.copy()
    flat_dir.z = 0.0
    horizontal = 1.0 - (abs(parent_direction.angle(flat_dir, 0.0)) / 1.5708)
    if parent_direction.x == 0.0 and parent_direction.y == 0.0:
        horizontal = 0.0

    plagio = plagiotropism_buds * horizontal
    if plagio > 1.0:
        plagio = 1.0

    if phyllotaxis_angle < 1.5708:
        phyllotaxis_angle = (1.0 - plagio) * phyllotaxis_angle
    elif phyllotaxis_angle < 4.7124:
        phyllotaxis_angle = plagio * 3.1416 + (1.0 - plagio) * phyllotaxis_angle
    else:
        phyllotaxis_angle = plagio * 6.2832 + (1.0 - plagio) * phyllotaxis_angle

    deviate_dir = Quaternion(direction, phyllotaxis_angle) @ deviate_dir

    flat_deviate_dir = deviate_dir.copy()
    flat_deviate_dir.z = 0.0
    strength = (1.0 - horizontal) * plagiotropism_buds
    deviate_dir = deviate_dir.lerp(flat_deviate_dir, strength)

    if gravitropism_buds < 0.0:
        vector_up = Vector((0.0, 0.0, 1.0))
        deviate_dir = deviate_dir.lerp(vector_up, -gravitropism_buds)
    else:
        vector_down = Vector((0.0, 0.0, -1.0))
        deviate_dir = deviate_dir.lerp(vector_down, gravitropism_buds)

    return deviate_dir


def phyllotaxis_samples(number_of_samples):

    samples = []
    for i in range(0, number_of_samples):
        x = acos(1 - (i / number_of_samples))
        y = i * 2.4
        samples.append(Vector((sin(x) * cos(y),
                               sin(x) * sin(y),
                               cos(x))))

    return samples


def phyllotaxis_samples_flat(number_of_samples, space):

    from random import random

    samples = []
    for i in range(0, number_of_samples):
        x = i * 2.4
        y = sqrt(number_of_samples - i)
        scale = space / 2.0
        randomness = space * 0.5
        samples.append(Vector((cos(x) * y * scale + randomness * (0.5 - random()),
                               sin(x) * y * scale + randomness * (0.5 - random()),
                               0.0)))

    return samples


def vertex_group_layer_from_data(ob, name, data):

    vertex_group = ob.vertex_groups.new(name=t(name))
    add = vertex_group.add

    indices = arange(0, len(data))
    a = column_stack((indices, data))
    a = a[argsort(a[:, 1])]
    a = split(a, where(diff(a[:, 1]))[0] + 1)

    for chunk in a:
        if chunk[0][1] == 0.0:
            continue
        add(chunk[:, 0].astype(int).tolist(), chunk[0][1], 'REPLACE')


def vertex_colors_layer_from_data(ob, name, data):

    vertex_colors = ob.data.vertex_colors.new(name=t(name))

    if vertex_colors is None:
        return False
    
    indices = empty([len(vertex_colors.data)], dtype=int)
    ob.data.loops.foreach_get("vertex_index", indices)

    cs = take(data, indices)
    cs = repeat(cs, 3)

    if add_alpha_to_vertex_colors:
        cs.shape = (cs.shape[0] // 3, 3)
        alphas = ones(cs.shape[0])
        alphas.shape = (1, alphas.shape[0])

        cs = concatenate((cs, alphas.T), axis=1)
        cs = cs.flatten()

    vertex_colors.data.foreach_set("color", cs)

    return True


def zoom(settings, context):

    context.space_data.lens = 50.0

    lower_left = settings.trunks[0].nodes[0].pos.copy()
    upper_right = settings.trunks[0].nodes[0].pos.copy()
    if len(settings.trunks) > 1:
        for trunk in settings.trunks[1:]:
            p = trunk.nodes[0].pos
            for i in range(3):
                if p[i] < lower_left[i]:
                    lower_left[i] = p[i] * 1.0
                if p[i] > upper_right[i]:
                    upper_right[i] = p[i] * 1.0
    mid_point = (lower_left + upper_right) / 2.0
    radius = upper_right.y - lower_left.x

    radius *= settings.scale_to_twig

    view = context.region_data
    view_dimensions = context.area.regions[-1]
    if view_dimensions.type != 'WINDOW':
        for region in context.area.regions:
            if region.type == 'WINDOW':
                view_dimensions = region
                break

    tree_height = settings.height * settings.scale_to_twig + 0.3
    if tree_height < 1.8:
        tree_height = 1.8
    if radius > tree_height:
        tree_height = radius
        tree_height += settings.height / 2.0
    view.view_distance = tree_height / 1.1
    if view_dimensions.width > view_dimensions.height:
        view.view_distance = tree_height / 1.1 * (view_dimensions.width / view_dimensions.height)
    view.view_location.x = mid_point.x
    view.view_location.y = mid_point.y
    view.view_location.z = tree_height / 2.0


def invoke_user_preferences():

    import bpy
    import addon_utils

    bpy.ops.screen.userpref_show("INVOKE_DEFAULT")
    bpy.context.preferences.active_section = "ADDONS"

    from os.path import dirname, basename
    name = basename(dirname(__file__))
    addon_utils.module_bl_info(addon_utils.addons_fake_modules.get(name))["show_expanded"] = True


def configure_particles(ps, psystem, modifier):
    no_hair = True

    ps.frame_start = 0.0
    ps.frame_end = 0.0
    ps.lifetime = 10000.0
    ps.use_emit_random = False
    ps.use_even_distribution = False
    ps.userjit = 1
    ps.physics_type = 'NO'
    ps.use_rotations = True
    ps.rotation_mode = 'VEL'
    ps.phase_factor_random = 0.1
    ps.use_render_emitter = True
    ps.render_type = 'OBJECT'
    ps.use_rotation_dupli = True
    ps.particle_size = 1.0
    ps.type = 'HAIR'
    ps.hair_step = 2
    ps.hair_length = 1.0
    ps.use_advanced_hair = True
    psystem.use_hair_dynamics = True
    ps.physics_type = 'NEWTON'
    ps.tangent_factor = 1.0

    psystem.cloth.settings.mass = 0.1
    psystem.cloth.settings.bending_stiffness = 2.0
    psystem.cloth.settings.air_damping = 0.5
    psystem.cloth.settings.bending_damping = 0.5
    psystem.cloth.settings.quality = 1
    modifier.particle_system.cloth.settings.bending_stiffness = 0.1

    if no_hair:
        ps.type = 'EMITTER'
        ps.physics_type = 'NO'
