bl_info = {
    "name": "Dual Polyhedron",
    "author": "Addam Dominec",
    "version": (0, 2),
    "blender": (2, 70, 0),
    "location": "Add -> Mesh -> Dual Polyhedron",
    "warning": "",
    "description": "Create a dual polyhedron of the active mesh",
    "category": "Learnbgame",
    "wiki_url": "",
    "tracker_url": ""
}


import bpy
import bmesh
import numpy
import mathutils
import random
from collections import defaultdict
from bpy_extras import object_utils


def pairs(sequence):
    """Generate consecutive pairs throughout the given sequence; at last, it gives elements last, first."""
    i = iter(sequence)
    previous = first = next(i)
    for this in i:
        yield previous, this
        previous = this
    yield this, first


def triplets(sequence):
    """Generate consecutive triplets throughout the given sequence"""
    it = iter(sequence)
    l = first = next(it)
    c = second = next(it)
    for r in it:
        yield l, c, r
        l, c = c, r
    yield l, c, first
    yield c, first, second


def get_smoothened_normals(faces):
    incidence = defaultdict(list)
    for face in faces:
        for vertex in face.vertices:
            incidence[vertex].append(face)
    neighbors = dict()
    for face in faces:
        neighbors[face] = [other for vertex in face.vertices for other in incidence[vertex] if other is not face]
    normals = {face: face.normal for face in faces}
    randfaces = [face for face in faces if len(neighbors[face]) >= 3]
    for iteration in range(5):
        random.shuffle(randfaces)
        for face in randfaces:
            nor = normals[face]
            nearest = [normals[neighbor] for neighbor in neighbors[face]]
            nearest.sort(key=lambda other_normal: (other_normal - nor).length_squared)
            normals[face] = sum(nearest[:3], mathutils.Vector((0, 0, 0))).normalized()
    return normals


def planarize(vertices, orig_coords, faces, normals, rigidity=1.0):
    planes = defaultdict(list)
    for face in faces:
        if len(face.vertices) == 3:
            continue
        plane_pair = normals[face], normals[face].dot(face.center)
        for vertex_index in face.vertices:
            planes[vertex_index].append(plane_pair)
    for vertex in vertices:
        alpha = rigidity if len(planes[vertex.index]) >= 3 else max(rigidity, 1e-3)
        A = (alpha * numpy.eye(3)).tolist()
        b = list(alpha * orig_coords[vertex])
        for (nor, plane_c) in planes[vertex.index]:
            A.append(nor)
            b.append(plane_c)
        coords, residuals, rank, singular = numpy.linalg.lstsq(A, b)
        vertex.co = coords


class Planarize(bpy.types.Operator):
    """Flattens all polygons of the active mesh"""
    bl_idname = "mesh.planarize"
    bl_label = "Planarize"
    bl_options = {'REGISTER', 'UNDO'}
    rigidity = bpy.props.FloatProperty(name="Rigidity",
        description="Slows down the planarization effect", default=1, min=0)
    iterations = bpy.props.IntProperty(name="Steps",
        description="Repeats the calculation to get a better result", default=5, min=1)
    do_smoothen = bpy.props.BoolProperty(name="Smoothen Normals",
        description="Distributes normals evenly across the surface", default=True)

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'

    def execute(self, context):
        recall_mode = context.object.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        mesh = context.active_object.data
        orig_coords = {vertex: vertex.co for vertex in mesh.vertices}
        normals = {face: face.normal for face in mesh.polygons}
        for iteration in range(self.iterations):
            if self.do_smoothen:
                normals = get_smoothened_normals(mesh.polygons)
            planarize(mesh.vertices, orig_coords, mesh.polygons, normals, self.rigidity/2**iteration)

        bpy.ops.object.mode_set(mode=recall_mode)
        return {'FINISHED'}


class AddDual(bpy.types.Operator):
    """Create a dual polyhedron of the active mesh"""
    bl_idname = "mesh.dual_add"
    bl_label = "Add Dual Polyhedron"
    bl_options = {'REGISTER', 'UNDO'}
    planarization = bpy.props.IntProperty(name="Planarize Steps",
        description="If nonzero, flattens each of the resulting faces into a plane", default=0, subtype='UNSIGNED')
    
    @classmethod
    def poll(self, context):
        return context.active_object and context.active_object.type == 'MESH'

    def execute(self, context):
        ob = context.active_object
        new_mesh = bpy.data.meshes.new(ob.name + "Dual")
        bm = bmesh.new()

        loops = dict()
        for face in ob.data.polygons:
            vertex = bm.verts.new(face.center)
            for a, b, c in triplets(face.vertices):
                print(a, b, c)
                loops[c, b] = vertex, (a, b)
        print(sorted((l, r) for (l, (v, r)) in loops.items()))
        while loops:
            first, (vertex, link) = loops.popitem()
            vertices = [vertex]
            while link in loops:
                vertex, link = loops.pop(link)
                vertices.append(vertex)
            if len(vertices) > 2:
                bm.faces.new(vertices)

        bm.to_mesh(new_mesh)
        new_mesh.update()
        
        if self.planarization > 0:
            orig_coords = {vertex: vertex.co for vertex in new_mesh.vertices}
            for iteration in range(self.planarization):
                normals = get_smoothened_normals(new_mesh.polygons)
                planarize(new_mesh.vertices, orig_coords, new_mesh.polygons, normals, 1/2**iteration)
        
        # add the mesh as an object into the scene
        new_ob = object_utils.object_data_add(context, new_mesh)
        new_ob.object.location = ob.location
        new_ob.object.rotation_euler = ob.rotation_euler
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddDual.bl_idname, text="Dual Polyhedron", icon='MESH_ICOSPHERE')


def register():
    bpy.utils.register_class(AddDual)
    bpy.utils.register_class(Planarize)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddDual)
    bpy.utils.unregister_class(Planarize)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()
    bpy.ops.mesh.dual_add()
