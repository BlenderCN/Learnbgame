from math import radians
from random import random

import bpy
import bmesh

from mathutils import Vector, Matrix, Euler


class lattice:

    samples = 1000
    interpolation_type = None
    method = 'ALIGN'
    minimum_matrix = Matrix()

    def __init__(self, operator, context):

        # TODO: optimize/cleanup oop; this is a direct conversion from edit mode support and has not been optimized for latest features
        origin_active_object = context.active_object
        origin_mode = origin_active_object.mode

        self.samples = int(self.samples * context.window_manager.fast_lattice.accuracy)
        self.interpolation_type = context.window_manager.fast_lattice.interpolation_type
        self.method = context.window_manager.fast_lattice.method

        bpy.ops.object.mode_set(mode='OBJECT')

        if origin_mode == 'OBJECT':

            for object in context.selected_objects:

                if object.type == 'MESH':

                    object.update_from_editmode()
        else:

            origin_active_object.update_from_editmode()

        context.scene.update()

        if origin_mode == 'EDIT':
            vertices = [(vertex, origin_active_object.matrix_world * vertex.co) for vertex in origin_active_object.data.vertices if vertex.select]
            indices = [vertex[0].index for vertex in vertices]
        else:
            vertices = []
            for object in context.selected_objects:
                vertices += [(vertex, origin_active_object.matrix_world * vertex.co) for vertex in origin_active_object.data.vertices]
                if object != origin_active_object:
                    vertices += [(vertex, object.matrix_world * vertex.co) for vertex in object.data.vertices]

        if origin_mode == 'OBJECT':

            data = bpy.data.meshes.new(name='point_data')
            data.from_pydata(vertices=[vertex[1] for vertex in vertices], edges=[], faces=[])
            object = bpy.data.objects.new(name='point_data', object_data=data)
            context.scene.objects.link(object)
            object.update_from_editmode()

        else:

            data = bpy.data.meshes.new(name='point_data')
            data.from_pydata(vertices=[vertex[1] for vertex in vertices], edges=[], faces=[])
            object = bpy.data.objects.new(name='point_data', object_data=data)
            context.scene.objects.link(object)
            object.update_from_editmode()

        mesh = bmesh.new()
        mesh.from_mesh(data)

        convex_hull = bmesh.ops.convex_hull(mesh, input=[vertex for vertex in mesh.verts if vertex.select] if origin_mode == 'EDIT' else [vertex for vertex in mesh.verts], use_existing_faces=False)
        coordinates = [vertex.co for vertex in convex_hull['geom'] if hasattr(vertex, 'co')]

        if origin_mode == 'EDIT':

            vertex_group = origin_active_object.vertex_groups.new(name='fast-lattice')
            vertex_group.add(indices, 1.0, 'ADD')

        self.minimum_matrix = object.matrix_world
        lattice_object = self.add_lattice(coordinates)

        mesh.free()
        bpy.data.objects.remove(object, do_unlink=True)
        bpy.data.meshes.remove(data, do_unlink=True)

        if origin_mode == 'OBJECT':

            for object in context.selected_objects:

                if object.type == 'MESH':

                    lattice_modifier = object.modifiers.new(name='fast-lattice', type='LATTICE')
                    lattice_modifier.object = lattice_object
        else:

            lattice_modifier = origin_active_object.modifiers.new(name='fast-lattice', type='LATTICE')
            lattice_modifier.object = lattice_object
            lattice_modifier.vertex_group = vertex_group.name

        context.scene.objects.link(object=lattice_object)
        context.scene.objects.active = lattice_object

        lattice_object['fast-lattice'] = "{}:{}:{}:{}:{}:{}:{}:{}:{}".format(origin_active_object.name if origin_mode == 'EDIT' else [object.name for object in context.selected_objects if object.type == 'MESH'], vertex_group.name if origin_mode == 'EDIT' else None, lattice_modifier.name, lattice_object.name, lattice_object.data.name, origin_active_object.show_wire if origin_mode == 'EDIT' else [object.show_wire for object in context.selected_objects if object.type == 'MESH'], origin_active_object.show_all_edges if origin_mode == 'EDIT' else [object.show_all_edges for object in context.selected_objects if object.type == 'MESH'], origin_active_object.name, origin_mode)

        context.scene.update()

        for i in range(0, 3):

            if lattice_object.dimensions[i] < 0.001:

                lattice_object.dimensions[i] = 0.1

        bpy.ops.object.mode_set(mode='EDIT')


    def add_lattice(self, coordinates):

        lattice_data = bpy.data.lattices.new(name='fast-lattice')
        lattice_object = bpy.data.objects.new(name='fast-lattice', object_data=lattice_data)

        lattice_object.rotation_euler = self.rotation(coordinates).to_euler()
        lattice_object.location = self.location(coordinates)
        lattice_object.scale = self.scale(coordinates, self.minimum_matrix)

        lattice_object.show_x_ray = True

        lattice_data.interpolation_type_u = self.interpolation_type
        lattice_data.interpolation_type_v = self.interpolation_type
        lattice_data.interpolation_type_w = self.interpolation_type
        lattice_data.use_outside = True

        return lattice_object


    def rotation(self, coordinates):

        control = self.scale(coordinates, self.minimum_matrix)

        if self.method != 'WORLD':

            angle_samples = [radians(angle) for angle in range(0, 180)]
            vector_samples = [Vector((sample * 0.1 * random(), sample * 0.1 * random(), sample * 0.1 * random())) for sample in range(0, 10)]

            for sample in vector_samples:

                for angle in angle_samples:

                    matrix = Matrix.Rotation(angle, 4, sample)
                    test = self.scale(coordinates, matrix)

                    if test < control:

                        control = test
                        self.minimum_matrix = matrix

            for _ in range(int(self.samples*0.1)):

                vector_samples = [Vector((sample * 0.1 * random(), sample * 0.1 * random(), sample * 0.1 * random())) for sample in range(0, 10)]

                for sample in vector_samples:

                    for angle in angle_samples:

                        matrix = Matrix.Rotation(angle, 4, sample)
                        test = self.scale(coordinates, matrix)

                        if test < control:

                            control = test
                            self.minimum_matrix = matrix

        return self.minimum_matrix.inverted()


    def location(self, coordinates):

        vertices = [self.minimum_matrix * vertex for vertex in coordinates]

        x = [vertex.x for vertex in vertices]
        y = [vertex.y for vertex in vertices]
        z = [vertex.z for vertex in vertices]

        return self.minimum_matrix.inverted() * (sum(self.bounds(x, y, z), Vector()) / len(self.bounds(x, y, z)))


    @staticmethod
    def scale(coordinates, matrix):

        vertices = [matrix * coordinate for coordinate in coordinates]

        x = [vertex.x for vertex in vertices]
        y = [vertex.y for vertex in vertices]
        z = [vertex.z for vertex in vertices]

        maximum = Vector((max(x), max(y), max(z)))
        minimum = Vector((min(x), min(y), min(z)))

        return maximum - minimum


    @staticmethod
    def bounds(x, y, z):

        return [
            Vector((min(x), min(y), min(z))),
            Vector((min(x), min(y), max(z))),

            Vector((min(x), max(y), min(z))),
            Vector((min(x), max(y), max(z))),

            Vector((max(x), min(y), min(z))),
            Vector((max(x), min(y), max(z))),

            Vector((max(x), max(y), min(z))),
            Vector((max(x), max(y), max(z))),
        ]

def cleanup(context):

    bpy.ops.object.mode_set(mode='OBJECT')

    prop = context.object['fast-lattice'].split(':')

    for index, object_name in enumerate(list(prop[0].strip('[]').split(', '))):
        context.scene.objects.active = bpy.data.objects[object_name[1:-1]] if prop[8] == 'OBJECT' else bpy.data.objects[object_name]
        context.active_object.show_wire = True if list(prop[5])[index] == 'True' else False
        context.active_object.show_all_edges = True if list(prop[6])[index] == 'True' else False
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=context.active_object.modifiers[prop[2]].name)

    context.scene.objects.active = bpy.data.objects[prop[7]]

    if len(prop[0]) == 1:
        context.active_object.vertex_groups.remove(group=context.active_object.vertex_groups[prop[1]])

    bpy.data.objects.remove(object=bpy.data.objects[prop[3]], do_unlink=True)
    bpy.data.lattices.remove(lattice=bpy.data.lattices[prop[4]], do_unlink=True)

    bpy.ops.object.mode_set(mode=prop[8])


def update(operator, context):

    for object in context.selected_objects:
        if object.type == 'MESH':
            object.show_wire = operator.show_wire
            object.show_all_edges = operator.show_all_edges
