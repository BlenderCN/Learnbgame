# coding=utf-8

""" A Grove is a group of trees, a small woodland or orchard. In The Grove, this is a list of branches,
    which are the trunks of the trees. Every branch in The Grove is treated equal, and so are trunks.

    This file contains a collection of starter functions.
    A starter function does preparation work, and afterwards runs a recursive function from Branch.py.

    The main simulation sequence is performed in simulate() - it calls the starter functions in the right order
    and grows the tree in steps.
    
    Copyright 2014 - 2018, Wybren van Keulen, The Grove """


import bpy
from mathutils import Matrix, Vector, bvhtree, Euler, Quaternion
from math import pi, sqrt
from random import random
from os.path import exists, join, dirname

from .Node import Node
from .TwigInstance import TwigInstance
from .Utils import *
from .Branch import Branch
from .Presets import read_preset
from .Translation import t


def simulate(settings, context):

    environment = None
    if settings.do_environment:
        environment = build_environment_bvh(settings)
    
    for i in range(settings.grow_years):
        settings.age += 1
        print('/ ' + t('simulate_year_message').format(settings.age))

        if settings.age != 1:
            bake_bend(settings)
            drop(settings)
            add_side_branches(settings, environment)
            add_regenerative(settings)

        grow(settings, environment)
        lateral_takeover(settings)
        smooth_kinks(settings)
        thicken(settings)
        weigh(settings)
        bend(settings)
        calculate_shade(settings)
        photosynthesize(settings)
        flow(settings)
        environment_prune(settings, environment)

    count_branches(settings)


def count_branches(settings):

    number = 0
    for trunk in settings.trunks:
        number += trunk.count_branches()
    settings.number_of_branches = number


def switch_presets(trunk, settings):

    if hasattr(trunk, "preset"):
        read_preset(trunk.preset, settings)
    else:
        return


def environment_prune(settings, environment):
    if settings.do_environment_block:
        print('  ' + t('environment_prune_message'))
        for trunk in settings.trunks:
            switch_presets(trunk, settings)

            trunk.prune(environment, False)


def flow(settings):
    print('  ' + t('flow_message'))
    for trunk in settings.trunks:
        switch_presets(trunk, settings)

        peak_height = trunk.nodes[0].pos.z + settings.peak_height

        if settings.favor_healthy <= 1.0:
            total_power = trunk.nodes[0].photosynthesis
            number_of_branches = trunk.count_branches()
            equal_power = total_power / number_of_branches

            equal_power = 1.0

            trunk.flow_bright(settings.favor_current, settings.shade_avoidance, settings.favor_healthy,
                              settings.grow_length / settings.grow_nodes, settings.favor_current_reach, peak_height,
                              trunk.nodes[0].photosynthesis, equal_power, 0, settings.branching_inefficiency)

        else:
            trunk.flow_exaggerate(settings.favor_current, settings.shade_avoidance, settings.favor_healthy,
                                  settings.grow_length / settings.grow_nodes, settings.favor_current_reach, peak_height,
                                  trunk.nodes[0].photosynthesis)


def bend(settings):
    print('  ' + t('bend_message'))
    for trunk in settings.trunks:
        switch_presets(trunk, settings)

        parent_diff = -trunk.nodes[0].direction.rotation_difference(trunk.nodes[0].direction)
        trunk.bend(trunk.nodes[0].pos, parent_diff, settings.fatigue)


def photosynthesize(settings):
    print('  ' + t('photosynthesize_message'))
    for trunk in settings.trunks:
        switch_presets(trunk, settings)

        trunk.photosynthesize(settings.favor_current, settings.shade_leaf_area, settings.photo_range)
        photo = trunk.nodes[0].photosynthesis


def weigh(settings):
    print('  ' + t('weigh_message'))
    for trunk in settings.trunks:
        switch_presets(trunk, settings)

        trunk.weigh(settings.leaf_weight, settings.lateral_twig_chance, settings.lateral_twig_limit,
                    settings.branch_weight)


def thicken(settings):
    print('  ' + t('thicken_message'))
    for trunk in settings.trunks:
        switch_presets(trunk, settings)

        exponent = settings.join_branches * -2 + 4
        trunk.thicken(exponent, settings.internode_gain, settings.tip_decrease)

        trunk.make_data_relative_to_root(trunk.nodes[0].thickness, trunk.nodes[0].photosynthesis)


def bake_bend(settings):
    print('  ' + t('bake_bend_message'))
    for trunk in settings.trunks:
        switch_presets(trunk, settings)

        trunk.bake_bend(settings.bake_bend)


def add_side_branches(settings, environment):

    print('  ' + t('add_branches_message'))
    for trunk in settings.trunks:
        switch_presets(trunk, settings)

        if trunk.offset > settings.age:
            print(t('time_offset_message'))
            continue

        trunk.add_side_branches(settings.grow_nodes, settings.bud_life, settings.branch_chance,
                                settings.branch_chance_only_terminal, settings.grow_length / settings.grow_nodes,
                                settings.favor_current_reach, settings.favor_current, settings.shade_avoidance,
                                settings.branch_angle, int(settings.branching), settings.twist,
                                settings.plagiotropism_buds, settings.do_environment_block,
                                environment, settings.branch_chance_light_required, settings.tip_thickness,
                                settings.gravitropism_buds, settings.gravitropism_buds_randomness)


def grow(settings, environment):

    print('  ' + t('grow_message'))
    for trunk in settings.trunks:
        switch_presets(trunk, settings)

        if trunk.offset > settings.age:
            print(t('time_offset_message'))
            continue

        trunk.grow(settings.grow_nodes, settings.grow_length / settings.grow_nodes, settings.shade_elongation,
                   settings.random_heading, settings.random_pitch, settings.gravitropism,
                   settings.gravitropism_shade, settings.plagiotropism, settings.phototropism,
                   settings.do_environment, settings.do_environment_block, settings.force, settings.force_radius,
                   settings.force_power, environment, settings.tip_thickness, settings.tip_decrease,
                   settings.grow_exponent, settings.favor_rising)


def lateral_takeover(settings):

    print('  ' + t('lateral_takeover_message'))
    for trunk in settings.trunks:
        switch_presets(trunk, settings)
        trunk.lateral_takeover()


def strip_environment(settings, vertices, polygons):
    
    environment_object = bpy.data.objects[settings.environment_name]
    environment_transform = environment_object.matrix_world
    
    for vertex in environment_object.data.vertices:
        vertices.append((environment_transform * vertex.co) / settings.scale_to_twig)
    
    for polygon in environment_object.data.polygons:
        polygons.append(polygon.vertices)


def build_environment_bvh(settings):

    vertices = []
    polygons = []
    strip_environment(settings, vertices, polygons)
    
    return bvhtree.BVHTree.FromPolygons(vertices, polygons, epsilon=0.02)


def build_strokes_bvh(settings, view):

    vertices = []
    polygons = []

    view_matrix = view.view_matrix
    view_origin = view_matrix.inverted().translation

    scale_compensation = settings.scale_to_twig

    if view.view_perspective == 'ORTHO':
        extrude_vector = view.view_rotation * Vector((0.0, 0.0, 20.0))
        for i, stroke in enumerate(settings.strokes):
            vertices.extend([stroke[0] / scale_compensation - extrude_vector,
                             stroke[0] / scale_compensation + extrude_vector,
                             stroke[1] / scale_compensation + extrude_vector,
                             stroke[1] / scale_compensation - extrude_vector])

            offset = i * 4
            polygons.append((offset + 0,
                             offset + 1,
                             offset + 2,
                             offset + 3))
    else:
        for i, stroke in enumerate(settings.strokes):
            vertices.extend([view_origin / scale_compensation,
                             (stroke[0] + (stroke[0] - view_origin) * 20.0) / scale_compensation,
                             (stroke[1] + (stroke[1] - view_origin) * 20.0) / scale_compensation])

            offset = i * 3
            polygons.append((offset + 0,
                             offset + 1,
                             offset + 2))

    return bvhtree.BVHTree.FromPolygons(vertices, polygons, epsilon=0.02)


def manual_prune(settings, view, shape):
        
    bvh = build_strokes_bvh(settings, view)

    for trunk in settings.trunks:
        trunk.prune(bvh, shape)


def manual_grow(settings, context, view):

    bvh = build_strokes_bvh(settings, view)

    environment = None
    if settings.do_environment:
        environment = build_environment_bvh(settings)

    for trunk in settings.trunks:
        trunk.mark(bvh, True)
        simulate(settings, context)
        trunk.unmark()


def build_twigs_shadow(settings, vertices, polygons, centers, vertex_index_offset):

    skip_lateral_twigs = True

    twigs = []
    for trunk in settings.trunks:
        trunk.distribute_twigs(settings.lateral_twig_limit, settings.branch_angle, int(settings.branching),
                               settings.twist, settings.plagiotropism_buds, settings.lateral_twig_chance,
                               twigs, twigs, True, skip_lateral_twigs, settings.random_heading, settings.random_pitch)

    radius = sqrt(settings.shade_leaf_area) / 10.0 / 2
    radius *= 1.4142

    shape = [Vector((0.0, 0.0, 0.0)),
             Vector((radius, radius, 0.0)),
             Vector((radius * 2.0, 0.0, 0.0)),
             Vector((radius, -radius, 0.0))]
             
    half_pi = 0.5 * pi

    vec_zero = Vector((0.0, 0.0, 0.0))
    vec_right = Vector((1.0, 0.0, 0.0))
    
    for twig in twigs:
        start = twig.matrix @ vec_zero
        end = twig.matrix @ vec_right
        target = end.copy()
        target.z = start.z
        twig.matrix = two_point_transform(start, target)

        if twig.twig_type == 1:
            direction = end - start
            flat_dir = direction.copy()
            flat_dir.z = 0.0
            vertical = abs(direction.angle(flat_dir, 0.0)) / half_pi
            shift = Vector((-radius * vertical, 0.0, 0.0))
        
        elif twig.twig_type == 0:
            shift = vec_zero
            
        vertices.extend(twig.matrix @ (v + shift) for v in shape)
        polygons.append((vertex_index_offset,
                         vertex_index_offset + 1,
                         vertex_index_offset + 2,
                         vertex_index_offset + 3))

        centers.append(twig.matrix @ shape[0])
        vertex_index_offset += 4


def build_twigs_shadow_v2(settings, vertices, polygons, centers, vertex_index_offset):

    skip_lateral_twigs = False

    twigs = []
    for trunk in settings.trunks:
        trunk.distribute_twigs(settings.lateral_twig_limit, settings.branch_angle, int(settings.branching),
                               settings.twist, settings.plagiotropism_buds, settings.lateral_twig_chance,
                               twigs, twigs, True, skip_lateral_twigs, settings.random_heading, settings.random_pitch)

    radius = sqrt(settings.shade_leaf_area) / 10.0 / 2
    radius *= 1.4142

    shape = [Vector((0.0, 0.0, 0.0)),
             Vector((radius, radius, 0.0)),
             Vector((radius * 2.0, 0.0, 0.0)),
             Vector((radius, -radius, 0.0)),

             Vector((0.0, 0.0, 0.0)),
             Vector((radius * 2.0, 0.0, 0.0)),
             Vector((radius, 0.0, -0.5 * radius)),

             Vector((radius, radius, 0.0)),
             Vector((radius, -radius, 0.0)),
             Vector((radius, 0.0, -0.5 * radius))]

    half_pi = 0.5 * pi

    vec_zero = Vector((0.0, 0.0, 0.0))
    vec_right = Vector((1.0, 0.0, 0.0))

    for twig in twigs:
        start = twig.matrix * vec_zero
        end = twig.matrix * vec_right
        target = end.copy()
        target.z = start.z
        twig.matrix = two_point_transform(start, target)

        if twig.twig_type == 1:
            direction = end - start
            flat_dir = direction.copy()
            flat_dir.z = 0.0
            vertical = abs(direction.angle(flat_dir, 0.0)) / half_pi
            shift = Vector((-radius * vertical, 0.0, 0.0))

        elif twig.twig_type == 0:
            shift = vec_zero

        vertices.extend(twig.matrix * (v + shift) for v in shape)
        polygons.append((vertex_index_offset,
                         vertex_index_offset + 1,
                         vertex_index_offset + 2,
                         vertex_index_offset + 3))
        polygons.append((vertex_index_offset + 4,
                         vertex_index_offset + 5,
                         vertex_index_offset + 6))
        polygons.append((vertex_index_offset + 7,
                         vertex_index_offset + 8,
                         vertex_index_offset + 9))

        centers.append(twig.matrix * shape[0])
        vertex_index_offset += 10


def build_shade_bvh(settings):

    vertices = []
    polygons = []

    if settings.environment_name != "" and settings.force == "7":
        strip_environment(settings, vertices, polygons)

    centers = []
    build_twigs_shadow(settings, vertices, polygons, centers, len(vertices))

    return bvhtree.BVHTree.FromPolygons(vertices, polygons)


def add_regenerative(settings):

    bvh = build_shade_bvh(settings)
    samples = phyllotaxis_samples(settings.shade_samples)

    number_of_regenerative = 0
    for trunk in settings.trunks:
        number_of_regenerative += trunk.add_regenerative(settings.shade_samples, settings.regenerative_branch_chance,
                                                         settings.regenerative_branch_chance_light_required,
                                                         settings.grow_length / settings.grow_nodes,
                                                         settings.branch_angle, int(settings.branching),
                                                         settings.twist, settings.plagiotropism_buds,
                                                         bvh, samples)

    print('  ' + t('added_regenerative_branches_message').format(number_of_regenerative))


def calculate_shade(settings):

    print('  ' + t('shade_message'))

    bvh = build_shade_bvh(settings)
    samples = phyllotaxis_samples(settings.shade_samples)

    s = settings.shade_sensitivity
    if s < 0.5:
        sensitivity_exponent = -4.0 * s + 3.0
    else:
        sensitivity_exponent = -1.4 * s + 1.7

    for trunk in settings.trunks:
        trunk.calculate_shade(settings.shade_samples, sensitivity_exponent, bvh, samples)


def shade_preview(settings, context):

    vertices = []
    polygons = []
    centers = []
    
    build_twigs_shadow(settings, vertices, polygons, centers, len(vertices))
    
    mesh = bpy.data.meshes.new("TheGroveShadePreview")
    mesh.from_pydata(vertices, [], polygons)
    shade_preview_object = bpy.data.objects.new("TheGroveShadePreview", mesh)
    shade_preview_object.scale = Vector((settings.scale_to_twig, settings.scale_to_twig, settings.scale_to_twig))
    context.scene.collection.objects.link(shade_preview_object)

    vertices = phyllotaxis_samples(settings.shade_samples)
            
    mesh = bpy.data.meshes.new("TheGroveShadeSamplesPreview")
    mesh.from_pydata(vertices, [], [])
    shade_samples_preview_object = bpy.data.objects.new("TheGroveShadeSamplesPreview", mesh)
    context.scene.collection.objects.link(shade_samples_preview_object)


def drop(settings):

    print('  ' + t('drop_message'))

    drop_dead_exponent = settings.keep_dead * 0.5 + 0.5
    if settings.keep_dead == 0.0:
        drop_dead_exponent = 0.0
    drop_dead_exponent = 1.0 - drop_dead_exponent

    drop_shaded_threshold = 1.0 - settings.drop_shaded

    for trunk in settings.trunks:
        count_dropped, count_dead_ends = trunk.drop(settings.drop_relatively_weak, drop_dead_exponent,
                                                    settings.apical_bud_fatality, settings.flower_power,
                                                    drop_shaded_threshold)

        if count_dropped > 0:
            counts = trunk.drop(settings.drop_relatively_weak, drop_dead_exponent,
                                settings.apical_bud_fatality, settings.flower_power, drop_shaded_threshold)

            count_dropped += counts[0]

            if counts[0] > 0:
                counts = trunk.drop(settings.drop_relatively_weak, drop_dead_exponent,
                                    settings.apical_bud_fatality, settings.flower_power, drop_shaded_threshold)
                count_dropped += counts[0]

        print('  ' + t('dropped_branches_message').format(count_dropped))
        print('  ' + t('ended_low_powered_branches_message').format(count_dead_ends))

        tree_height = trunk.find_highest_point(trunk.nodes[0].pos.z) * settings.scale_to_twig
        trim_height = tree_height / 3.0
        if trim_height > settings.drop_low:
            trim_height = settings.drop_low

        if tree_height > 3.0 * settings.drop_low:
            if settings.drop_low > 0.5:
                trim_height = 0.5

        if settings.drop_low < 0.0:
            trim_height = settings.drop_low

        trim_height_string = "%0.2f" % trim_height
        trim_height_string = trim_height_string.rstrip('0').rstrip('.')
        print('  ' + t('drop_low_message').format(trim_height_string))

        trim_height /= settings.scale_to_twig
        base = trunk.nodes[0].pos.z
        trim_height += base

        trunk.drop_low(trim_height, settings.keep_thick)


def smooth_kinks(settings):

    print('  ' + t('smooth_branches_message'))

    angle = settings.smoothing
    for trunk in settings.trunks:
        trunk.smooth_kinks(angle)


def set_viewport_detail(settings):

    twig_objects = []
    if settings.apical_twig != "":
        already_a_modifier = False
        ob = bpy.data.objects[settings.apical_twig]
        for modifier in ob.modifiers:
            if modifier.type == 'DECIMATE':
                modifier.ratio = settings.twig_viewport_detail
                already_a_modifier = True
        if not already_a_modifier:
            twig_objects.append(bpy.data.objects[settings.apical_twig])

    if settings.lateral_twig != "" and settings.apical_twig != settings.lateral_twig:
        already_a_modifier = False
        ob = bpy.data.objects[settings.lateral_twig]
        for modifier in ob.modifiers:
            if modifier.type == 'DECIMATE':
                modifier.ratio = settings.twig_viewport_detail
                already_a_modifier = True
        if not already_a_modifier:
            twig_objects.append(bpy.data.objects[settings.lateral_twig])

    for twig_object in twig_objects:
        if twig_object.type != 'MESH':
            continue
        decimate = twig_object.modifiers.new("Viewport Detail", 'DECIMATE')
        decimate.ratio = settings.twig_viewport_detail
        if len(ob.data.polygons) < 1500:
            decimate.ratio = 1.0
        decimate.show_viewport = True
        decimate.show_render = False


def pre_compute_circles(profile_resolution):

    two_pi = 2 * pi
    circles = []

    for i in range(profile_resolution + 1):
        circle = []
        for j in range(i):
            angle = j / i * two_pi
            circle.append(Vector((cos(angle), sin(angle), 0.0)))
        circles.append(circle)

    return circles


def determine_wind_direction(settings):

    wind_direction = Vector((1.0, 0.0, 0.0))

    if settings.wind_direction_n:
        if settings.wind_direction_e:
            wind_direction = Vector((-0.707, -0.707, 0.0))
        elif settings.wind_direction_w:
            wind_direction = Vector((0.707, -0.707, 0.0))
        else:
            wind_direction = Vector((0.0, -1.0, 0.0))

    elif settings.wind_direction_s:
        if settings.wind_direction_e:
            wind_direction = Vector((-0.707, 0.707, 0.0))
        elif settings.wind_direction_w:
            wind_direction = Vector((0.707, 0.707, 0.0))
        else:
            wind_direction = Vector((0.0, 1.0, 0.0))

    elif settings.wind_direction_e:
        wind_direction = Vector((-1.0, 0.0, 0.0))

    elif settings.wind_direction_w:
        wind_direction = Vector((1.0, 0.0, 0.0))

    return wind_direction


def build_placeholders(settings, context):

    for trunk in settings.trunks:
        ob = bpy.data.objects.new(str(settings.preset_name), None)
        ob.empty_display_type = 'SINGLE_ARROW'
        ob.location = trunk.nodes[0].pos * settings.scale_to_twig

        quat = (trunk.nodes[1].pos - trunk.nodes[0].pos).to_track_quat('Z', 'X')
        mat_rotation = quat.to_matrix()
        mat_rotation.resize_4x4()
        ob.matrix_world = Matrix.Translation(trunk.nodes[0].pos) @ mat_rotation

        bpy.context.scene.collection.objects.link(ob)


def build_branches_mesh(settings, context):

    print(t('build_branches_advanced_mesh_message'))

    if len(settings.trunks) == 0:
        restart(settings)

    settings.number_of_polygons = 0

    if exists(settings.textures_menu):
        im = bpy.data.images.load(settings.textures_menu, check_existing=True)
        texture_aspect_ratio = im.size[0] / im.size[1]
    else:
        im = None
        texture_aspect_ratio = 3.0

    for trunk in settings.trunks:
        vertices = []
        faces = []
        uvs = []
        shape = []

        simulation_data = {'layer_shade': [], 'layer_thickness': [], 'layer_weight': [],
                           'layer_power': [], 'layer_health': [], 'layer_generation': [],
                           'layer_dead': [], 'layer_pitch': [], 'layer_apical': [], 'layer_lateral': []}

        if (settings.do_update_only_twigs and settings.mesh_cache[0] is not None and
                len(settings.trunks) == 1 and settings.build_type != '4'):
            print(t('build_cached_message'))
            vertices = settings.mesh_cache[0]
            faces = settings.mesh_cache[1]
            uvs = settings.mesh_cache[2]
            simulation_data = settings.mesh_cache[3]
        else:
            trunk.build_branches_mesh(settings.build_type,
                                      settings.profile_resolution, settings.profile_resolution_reduction,
                                      settings.twist, settings.u_repeat, texture_aspect_ratio,
                                      settings.root_distribution, settings.root_shape,
                                      settings.root_scale, settings.root_bump,
                                      trunk.nodes[0].real_weight,
                                      None, None, None, 0,
                                      vertices, faces, uvs, shape, simulation_data,
                                      trunk.nodes[0].pos, pre_compute_circles(settings.profile_resolution), False,
                                      settings.lateral_twig_limit, settings.branch_angle, int(settings.branching),
                                      settings.plagiotropism_buds, 0.0)

        me = bpy.data.meshes.new(str(settings.preset_name))
        me.from_pydata(vertices, [], faces)
        #uvtex = me.uv_textures.new()
        #uvtex.name = "UV"
        #uvtex = me.uv_layers[uvtex.name].data
        #uvtex.foreach_set("uv", [uv for pair in uvs for uv in pair])

        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))

        bark_material = bpy.data.materials.new("TheGroveBranches")
        bark_material.diffuse_color = Vector((0.10, 0.10, 0.09,1)) 
        background_color = context.preferences.themes[0].view_3d.space.gradients.high_gradient
        background_brightness = (background_color[0] + background_color[1] + background_color[2]) / 3.0
        if background_brightness < 0.45:
            bark_material.diffuse_color = Vector((0.04, 0.04, 0.03,1))
        bark_material.specular_color = Vector((0.0, 0.0, 0.0))

        render_engine = bpy.context.scene.render.engine
        if render_engine != 'CYCLES':
            bpy.context.scene.render.engine = 'CYCLES'
        bark_material.use_nodes = True
        diffuse_node = bark_material.node_tree.nodes.get('Diffuse BSDF')
        texture_node = bark_material.node_tree.nodes.new('ShaderNodeTexImage')
        texture_node.name = 'Bark Texture'
        texture_node.label = 'Bark Texture'
        #texture_node.location = (diffuse_node.location[0] - 256.0, diffuse_node.location[1])
        #bark_material.node_tree.links.new(diffuse_node.inputs[0], texture_node.outputs[0])
        if im is not None:
            texture_node.image = im
        if render_engine != 'CYCLES':
            bpy.context.scene.render.engine = render_engine

        me.materials.append(bark_material)

        settings.number_of_polygons += len(faces)

        if not settings.do_update_only_twigs:
            settings.mesh_cache[0] = vertices
            settings.mesh_cache[1] = faces
            settings.mesh_cache[2] = uvs
            settings.mesh_cache[3] = simulation_data

        ob = bpy.data.objects.new(str(settings.preset_name), me)
        me = ob.data

        ob["the_grove_preset"] = str(settings.preset_name)

        print(t('build_layers_message'))

        if settings.show_dead_preview:
            settings.do_layer_dead = True

        material_indices = [0] * len(faces)
        for name, data in simulation_data.items():
            if getattr(settings, "do_" + str.lower(name)):
                vertex_group_layer_from_data(ob, name, data)

                if not vertex_colors_layer_from_data(ob, name, data):
                    settings.display_vertex_colors_warning = True
                    print(t('colors_limit_message').format(name))

                if name == "layer_apical" and settings.do_layer_apical:
                    if "TheGroveApicalTwigs" not in bpy.data.materials:
                        ma = bpy.data.materials.new("TheGroveApicalTwigs")
                        ma.diffuse_color = Vector((0.0, 0.0, 0.0,1))
                        ma.specular_color = Vector((0.0, 0.0, 0.0))
                    me.materials.append(bpy.data.materials["TheGroveApicalTwigs"])
                    index = me.materials.find("TheGroveApicalTwigs")
                    material_indices = [material_indices[i] + (index * int(data[face[0]]))
                                        for i, face in enumerate(faces)]

                if name == "layer_lateral" and settings.do_layer_lateral:
                    if "TheGroveLateralTwigs" not in bpy.data.materials:
                        ma = bpy.data.materials.new("TheGroveLateralTwigs")
                        ma.diffuse_color = Vector((0.0, 0.0, 0.0,1))
                        ma.specular_color = Vector((0.0, 0.0, 0.0))
                    me.materials.append(bpy.data.materials["TheGroveLateralTwigs"])
                    index = me.materials.find("TheGroveLateralTwigs")
                    material_indices = [material_indices[i] + (index * int(data[face[0]]))
                                        for i, face in enumerate(faces)]

                if name == "layer_dead" and settings.show_dead_preview:
                    if "TheGroveDeadBranches" not in bpy.data.materials:
                        ma = bpy.data.materials.new("TheGroveDeadBranches")
                        ma.diffuse_color = Vector((1.0, 0.0, 0.0,1))
                        ma.specular_color = Vector((0.0, 0.0, 0.0))
                    me.materials.append(bpy.data.materials["TheGroveDeadBranches"])
                    index = me.materials.find("TheGroveDeadBranches")
                    material_indices = [material_indices[i] + (index * int(data[face[0]]))
                                        for i, face in enumerate(faces)]

        me.polygons.foreach_set("material_index", material_indices)

        me['the_grove'] = 'Grown with The Grove'

        ob.location = trunk.nodes[0].pos * settings.scale_to_twig
        bpy.context.scene.collection.objects.link(ob)

        ob.scale = Vector((settings.scale_to_twig, settings.scale_to_twig, settings.scale_to_twig))

        if settings.twigs_menu != t('no_twigs'):
            set_viewport_detail(settings)

            if settings.apical_twig != "":
                modifier = ob.modifiers.new("Duplicate Apical Twigs", 'PARTICLE_SYSTEM')
                psystem = ob.particle_systems[-1]
                psystem.name = "Duplicate " + settings.apical_twig
                ps = psystem.settings
                ps.count = len([selection for selection in simulation_data['layer_apical'] if selection == 1.0]) / 3

                configure_particles(ps, psystem, modifier)

                ps.dupli_object = bpy.data.objects[settings.apical_twig]
                psystem.vertex_group_density = t('layer_apical')

            if settings.lateral_twig != "":
                modifier = ob.modifiers.new("Duplicate Lateral Twigs", 'PARTICLE_SYSTEM')
                psystem = ob.particle_systems[-1]
                psystem.name = "Duplicate " + settings.lateral_twig
                ps = psystem.settings
                ps.count = (len([selection for selection in simulation_data['layer_lateral'] if selection == 1.0]) / 3
                            * settings.lateral_twig_chance)

                configure_particles(ps, psystem, modifier)

                ps.dupli_object = bpy.data.objects[settings.lateral_twig]
                psystem.vertex_group_density = t('layer_lateral')

            do_dupli_groups = False
            if do_dupli_groups:
                from numpy import arange
                layer = array(simulation_data['layer_apical'])
                apical_state = layer == 1.0
                indices = arange(layer.shape[0])
                duplicators = indices[apical_state]
                duplicators.shape = (duplicators.shape[0] // 3, 3)
                for triangle in duplicators:
                    empty = bpy.data.objects.new("Empty", None)
                    empty.empty_draw_size = 0.1
                    empty.parent = ob
                    empty.parent_type = 'VERTEX_3'
                    empty.parent_vertices[0] = triangle[0]
                    empty.parent_vertices[1] = triangle[1]
                    empty.parent_vertices[2] = triangle[2]
                    context.scene.collection.objects.link(empty)

        if settings.calculate_wind:
            print(t('add_wind_message'))

            ob.shape_key_add(name='Base', from_mix=False)

            wind_direction = determine_wind_direction(settings)

            steps = settings.wind_shapes
            for j in range(steps):
                print(t('add_wind_shape_message').format(j + 1, steps))

                trunk.weigh(settings.leaf_weight, settings.lateral_twig_chance, settings.lateral_twig_limit,
                            settings.branch_weight, settings.turbulence, wind_vector=wind_direction)
                parent_diff = -trunk.nodes[0].direction.rotation_difference(trunk.nodes[0].direction)

                f = settings.wind_force + (random() * 0.5 * settings.wind_force)
                trunk.bend(trunk.nodes[0].pos, parent_diff, settings.fatigue, wind_force=f, wind_vector=wind_direction)

                vertices1 = []
                shape = []

                trunk.build_branches_mesh(settings.build_type,
                                          settings.profile_resolution, settings.profile_resolution_reduction,
                                          settings.twist, settings.u_repeat, texture_aspect_ratio,
                                          settings.root_distribution,
                                          settings.root_shape, settings.root_scale, settings.root_bump,
                                          trunk.nodes[0].real_weight,
                                          None, None, None, 0,
                                          vertices1, [], [], shape, {},
                                          trunk.nodes[0].pos, pre_compute_circles(settings.profile_resolution),
                                          True,
                                          settings.lateral_twig_limit, settings.branch_angle, int(settings.branching),
                                          settings.plagiotropism_buds,
                                          ((sin(j / 3.0) + 1) + sin(j*2)) * settings.wind_force)

                shape_key = ob.shape_key_add(name='WindShape', from_mix=False).data
                shape_key.foreach_set("co", shape)

                interval = 10
                width = 20
                height = 0.5

                channel = ob.data.shape_keys.key_blocks[-1]
                channel.value = 0.0
                channel.keyframe_insert("value", frame=j * interval - width)
                channel.keyframe_insert("value", frame=j * interval + width)
                channel.keyframe_insert("value", frame=(j * interval + interval * steps - width))
                channel.value = height
                channel.keyframe_insert("value", frame=j * interval + 1)

                if j < 2:
                    channel.value = 0.0
                    channel.keyframe_insert("value", frame=(j + steps) * interval - width)
                    channel.keyframe_insert("value", frame=(j + steps) * interval + width)
                    channel.keyframe_insert("value", frame=((j + steps) * interval + interval * steps - width))
                    channel.value = height
                    channel.keyframe_insert("value", frame=(j + steps) * interval + 1)
                if j == steps - 1:
                    channel.value = 0.0
                    channel.keyframe_insert("value", frame=-interval - width)
                    channel.keyframe_insert("value", frame=-interval + width)
                    channel.value = height
                    channel.keyframe_insert("value", frame=-interval + 1)

            for curve in ob.data.shape_keys.animation_data.action.fcurves:
                curve.modifiers.new('CYCLES')

            trunk.weigh(settings.leaf_weight, settings.lateral_twig_chance, settings.lateral_twig_limit,
                        settings.branch_weight)
            parent_diff = -trunk.nodes[0].direction.rotation_difference(trunk.nodes[0].direction)
            trunk.bend(trunk.nodes[0].pos, parent_diff, settings.fatigue)


def restart(settings):
    
    settings.age = 0
    settings.height = 0.0
    settings.number_of_branches = 1
    settings.trunks = []
    settings.mesh_cache = [None, None, None, None]
    
    if len(settings.empties) > 0:
        for i, empty_object in enumerate(settings.empties):
            print(t('plant_at_empty_message'))

            ob = bpy.data.objects[empty_object]
            mat = ob.matrix_world
            pos = ob.location

            direction = mat * Vector((0.0, 0.002, settings.grow_length / settings.grow_nodes))
            direction -= pos
            b = Branch(direction)
            b.nodes[0].pos = pos.copy()

            b.nodes.append(Node(direction))
            b.nodes[1].pos = pos + direction

            b.tip_thickness = settings.tip_thickness
            b.uv_offset_y = 0.0

            b.is_trunk = True
            settings.trunks.append(b)

            if "offset" in ob:
                b.offset = ob["offset"]

            if "preset" in ob:
                b.preset = ob["preset"]
                
            b.initial_phyllotaxic_angle = random() * 2.0 * pi
                
    else:
        samples = [Vector((0.0, 0.0, 0.0))]
        if settings.number_of_trees > 1:
            samples = phyllotaxis_samples_flat(settings.number_of_trees, settings.tree_space)

        for j, sample in enumerate(samples):
            print(t('plant_at_origin_message'))

            b = Branch(Vector((0.0, 0.0, settings.grow_length / settings.grow_nodes)))
            b.nodes[0].pos = sample
            b.is_trunk = True

            spread = (1.0 - settings.tree_space) * 0.07
            if spread < 0.0:
                spread = 0.0
            spread *= 1.0 - (j / len(samples))
            b.nodes[0].direction += sample.normalized() * spread
            b.offset = int(random() * 3)

            b.nodes.append(Node(Vector((0.0, 0.002, settings.grow_length / settings.grow_nodes))))
            b.nodes[1].direction += sample.normalized() * spread
            b.nodes[1].pos = b.nodes[0].pos + Vector((0.0, 0.0, settings.grow_length / settings.grow_nodes))
            b.tip_thickness = settings.tip_thickness
            b.initial_phyllotaxic_angle = random() * 2.0 * pi
            b.uv_offset_y = 0.0

            settings.trunks.append(b)

    for trunk in settings.trunks:
        trunk.weigh(0.0, 0.0, 0.0, 0.0, 0.0)
        exponent = settings.join_branches * -2 + 4
        trunk.thicken(exponent, 0.0, 0.0)

    for trunk in settings.trunks:
        for node in trunk.nodes:
            node.pos /= settings.scale_to_twig

    count_branches(settings)
