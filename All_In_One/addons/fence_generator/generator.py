
import math
import random

import bpy
import bmesh
import mathutils


def duplicate_mesh(operator, b_mesh, random_width):
    faces = list(b_mesh.faces)
    for offset_y in random_width:
        result = bmesh.ops.duplicate(b_mesh, geom=faces)
        geometry = result['geom']
        vertices = [element for element in geometry if isinstance(element, bmesh.types.BMVert)]
        bmesh.ops.translate(
            b_mesh,
            vec=mathutils.Vector((0.0, offset_y, 0.0)),
            verts=vertices
        )


def generate_fence(operator, random_width):
    fence_mesh = bmesh.new()

    last_offset_y = 0.0
    for width in random_width:
        # generate vertices coordinates
        coordinate_x = operator.fence_offset_x
        coordinate_y_1 = last_offset_y
        coordinate_y_2 = width
        coordinate_z_1 = operator.fence_offset_z
        coordinate_z_2 = operator.fence_offset_z + operator.fence_height
        last_offset_y = coordinate_y_2

        # create vertices
        vertex_1 = fence_mesh.verts.new((
            coordinate_x, coordinate_y_1, coordinate_z_1
        ))
        vertex_2 = fence_mesh.verts.new((
            coordinate_x, coordinate_y_1, coordinate_z_2
        ))
        vertex_3 = fence_mesh.verts.new((
            coordinate_x, coordinate_y_2, coordinate_z_2
        ))
        vertex_4 = fence_mesh.verts.new((
            coordinate_x, coordinate_y_2, coordinate_z_1
        ))

        # create face
        face = fence_mesh.faces.new((vertex_4, vertex_3, vertex_2, vertex_1))

    bmesh.ops.remove_doubles(fence_mesh, verts=fence_mesh.verts, dist=0.0001)

    # create mesh and object
    bpy_mesh = bpy.data.meshes.new('Fence')
    fence_mesh.to_mesh(bpy_mesh)
    bpy_object = bpy.data.objects.new('Fence', bpy_mesh)
    bpy.context.scene.objects.link(bpy_object)
    bpy_object.select = True
    bpy.context.scene.objects.active = bpy_object
    if operator.fence_material:
        bpy_mesh.materials.append(bpy.data.materials[operator.fence_material])

    return bpy_object


def generate_column(operator, width, column_mesh):
    base_z_coordinates = [
        operator.column_offset_z,
        operator.column_offset_z + operator.column_height
    ]

    # top vertices, bottom vertices
    base_vertices = [[], []]
    angle = 360 / operator.column_segments
    for base_index in range(2):
        coordinate_z = base_z_coordinates[base_index]
        if base_index == 1:
            coordinate_z -= operator.column_random_height * coordinate_z * random.random()
        for base_vertex_index in range(operator.column_segments):
            coordinate_x = operator.column_radius * math.cos(math.radians(angle * base_vertex_index + operator.column_rotate_z))
            coordinate_y = width + operator.column_radius * math.sin(math.radians(angle * base_vertex_index + operator.column_rotate_z))
            bmesh_vertex = column_mesh.verts.new((coordinate_x, coordinate_y, coordinate_z))
            base_vertices[base_index].append(bmesh_vertex)

    # create top face
    column_mesh.faces.new(base_vertices[1])

    # create side faces
    vertices_count = len(base_vertices[0])
    vertex_index_current = vertices_count - 1
    for vertex_index in range(vertices_count):
        vertex_1 = base_vertices[0][vertex_index_current - 1]
        vertex_2 = base_vertices[0][vertex_index_current]
        vertex_3 = base_vertices[1][vertex_index_current]
        vertex_4 = base_vertices[1][vertex_index_current - 1]
        vertex_index_current -= 1
        column_mesh.faces.new((
            vertex_1,
            vertex_2,
            vertex_3,
            vertex_4
        ))


def generate_columns(operator, random_width):
    column_mesh = bmesh.new()
    random_width.insert(0, 0.0)    # first column in 0.0 position
    for width in random_width:
        generate_column(operator, width, column_mesh)
    # create mesh and object
    bpy_mesh = bpy.data.meshes.new('Column')
    column_mesh.to_mesh(bpy_mesh)
    bpy_object = bpy.data.objects.new('Column', bpy_mesh)
    bpy.context.scene.objects.link(bpy_object)
    bpy_object.select = True
    bpy.context.scene.objects.active = bpy_object
    if operator.column_material:
        bpy_mesh.materials.append(bpy.data.materials[operator.column_material])

    return bpy_object


def generate_curve(operator, random_width, reference_curve):
    curve_mesh = bmesh.new()
    for width in random_width:
        bmesh_vertex = curve_mesh.verts.new((0.0, width, 0.0))
    curve_mesh.verts.ensure_lookup_table()
    for edge_index in range(len(curve_mesh.verts) - 2):
        bmesh_vertex_1 = curve_mesh.verts[edge_index]
        bmesh_vertex_2 = curve_mesh.verts[edge_index + 1]
        bmesh_edge = curve_mesh.edges.new((bmesh_vertex_1, bmesh_vertex_2))
    # create mesh and object
    bpy_mesh = bpy.data.meshes.new('Curve')
    curve_mesh.to_mesh(bpy_mesh)
    bpy_object = bpy.data.objects.new('Curve', bpy_mesh)
    bpy.context.scene.objects.link(bpy_object)
    bpy_object.select = True
    bpy.context.scene.objects.active = bpy_object

    curve_modifer = bpy_object.modifiers.new('Curve', 'CURVE')
    curve_modifer.deform_axis = 'POS_Y'
    curve_modifer.object = reference_curve
    bpy.ops.object.select_all(action='DESELECT')
    bpy_object.select = True
    bpy.ops.object.convert(target='CURVE')
    reference_curve.select = True
    bpy_object.data.splines[0].use_cyclic_u = reference_curve.data.splines[0].use_cyclic_u
    bpy_object.data.splines[0].use_cyclic_v = reference_curve.data.splines[0].use_cyclic_v

    return bpy_object


def fence(operator, context):
    curve_object = bpy.data.objects.get(operator.curve, None)
    has_curve = False
    if curve_object:
        if curve_object.type == 'CURVE':
            has_curve = True
            bpy.ops.object.select_all(action='DESELECT')
            curve_object.select = True
            bpy.ops.object.duplicate()
            duplicate_curve_object = context.selected_objects[0]
            context.scene.objects.active = duplicate_curve_object
            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.convert(target='CURVE')
            spline = duplicate_curve_object.data.splines[0]
            points = spline.points
            points_count = len(points)
            curve_length = 0.0

            def calculate_length(point_1, point_2):
                distance = math.sqrt(
                    (point_1.co.x - point_2.co.x) ** 2 + \
                    (point_1.co.y - point_2.co.y) ** 2 + \
                    (point_1.co.z - point_2.co.z) ** 2
                )
                return distance

            for point_id in range(points_count - 1, 0, -1):
                point_1 = points[point_id]
                point_2 = points[point_id - 1]
                distance = calculate_length(point_1, point_2)
                curve_length += distance

            if spline.use_cyclic_u:
                point_1 = points[0]
                point_2 = points[-1]
                distance = calculate_length(point_1, point_2)
                curve_length += distance

            random_width = []
            last_offset = 0.0
            while last_offset + operator.fence_width < curve_length:
                random_value_y = operator.fence_width - operator.fence_width * random.random() * operator.fence_random_width
                random_width.append(last_offset + random_value_y)
                last_offset += random_value_y
            column_object = generate_columns(operator, random_width)
            random_width.append(curve_length)
            fence_object = generate_fence(operator, random_width)
            curve_object = generate_curve(operator, random_width, duplicate_curve_object)

            for point in curve_object.data.splines[0].points:
                random_angle = random.random() * operator.curve_random_tilt
                point.tilt = math.radians(operator.curve_tilt - operator.curve_random_tilt / 2 + random_angle)

            def add_curve_modifer(object):
                curve_modifer = object.modifiers.new('Curve', 'CURVE')
                curve_modifer.deform_axis = 'POS_Y'
                curve_modifer.object = curve_object

            add_curve_modifer(column_object)
            add_curve_modifer(fence_object)
            fence_object.select = True
            column_object.select = True
            bpy.ops.object.convert(target='MESH')

            duplicate_curve_data = duplicate_curve_object.data
            bpy.data.objects.remove(duplicate_curve_object)
            bpy.data.meshes.remove(duplicate_curve_data)

            curve_data = curve_object.data
            bpy.data.objects.remove(curve_object)
            bpy.data.meshes.remove(curve_data)

    if not has_curve:
        random_width = []
        last_offset = 0.0
        for segment_index in range(operator.segments_count):
            random_value_y = operator.fence_width - operator.fence_width * random.random() * operator.fence_random_width
            random_width.append(last_offset + random_value_y)
            last_offset += random_value_y
        column_object = generate_columns(operator, random_width)
        fence_object = generate_fence(operator, random_width)
