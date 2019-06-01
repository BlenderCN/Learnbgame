
import os
import struct

import bpy

from . import render


GL_PARTICLES_CACHE = {}


def remove_par_object(domain):
    if domain.jet_fluid.particles_object:
        par_object = bpy.data.objects[domain.jet_fluid.particles_object]
        old_mesh = par_object.data
        materials = [m for m in old_mesh.materials]
        mesh = bpy.data.meshes.new('temp_name')
        for mat in materials:
            mesh.materials.append(mat)
        par_object.data = mesh
        bpy.data.meshes.remove(old_mesh)
        mesh.name = 'jet_fluid_particles'


def remove_mesh_object(domain):
    if domain.jet_fluid.mesh_object:
        mesh_object = bpy.data.objects.get(domain.jet_fluid.mesh_object, None)
        if not mesh_object:
            return
        old_mesh = mesh_object.data
        materials = [m for m in old_mesh.materials]
        mesh = bpy.data.meshes.new('temp_name')
        for mat in materials:
            mesh.materials.append(mat)
        mesh_object.data = mesh
        bpy.data.meshes.remove(old_mesh)
        mesh.name = 'jet_fluid_mesh'


def update_mesh_object(self, context):
    obj_names = {obj.name for obj in bpy.data.objects}
    for obj_name in obj_names:
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            continue
        if obj.jet_fluid.is_active:
            if obj.jet_fluid.create_mesh:
                create_mesh(obj)
            else:
                remove_mesh_object(obj)


def update_par_object(self, context):
    obj_names = {obj.name for obj in bpy.data.objects}
    for obj_name in obj_names:
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            continue
        if obj.jet_fluid.is_active:
            if obj.jet_fluid.create_particles:
                create_particles(obj)
            else:
                remove_par_object(obj)


def create_particles(domain):
    file_path = '{}particles_{}.bin'.format(
        bpy.path.abspath(domain.jet_fluid.cache_folder),
        bpy.context.scene.frame_current
    )
    if not os.path.exists(file_path):
        remove_par_object(domain)
        return
    particles_file = open(file_path, 'rb')
    particles_data = particles_file.read()
    particles_file.close()
    p = 0
    particles_count = struct.unpack('I', particles_data[p : p + 4])[0]
    p += 4
    vertices = []
    for particle_index in range(particles_count):
        pos = struct.unpack('3f', particles_data[p : p + 12])
        p += 48    # skip velocities, forces and colors
        vertices.append((pos[0], pos[2], pos[1]))

    par_mesh = bpy.data.meshes.new('temp_name')
    if not domain.jet_fluid.particles_object:
        par_object = bpy.data.objects.new('jet_fluid_particles', par_mesh)
        domain.jet_fluid.particles_object = par_object.name
        bpy.context.scene.objects.link(par_object)
    else:
        if bpy.data.objects.get(domain.jet_fluid.particles_object):
            par_object = bpy.data.objects[domain.jet_fluid.particles_object]
            old_par_mesh = par_object.data
            par_object.data = par_mesh
            materials = [m for m in old_par_mesh.materials]
            for mat in materials:
                par_mesh.materials.append(mat)
            bpy.data.meshes.remove(old_par_mesh)
        else:
            par_object = bpy.data.objects.new(domain.jet_fluid.particles_object, par_mesh)
            bpy.context.scene.objects.link(par_object)
    par_mesh.from_pydata(vertices, (), ())
    par_mesh.name = 'jet_fluid_particles'


def create_mesh(domain):
    file_path = '{}mesh_{}.bin'.format(
        bpy.path.abspath(domain.jet_fluid.cache_folder),
        bpy.context.scene.frame_current
    )
    if not os.path.exists(file_path):
        remove_mesh_object(domain)
        return
    mesh_file = open(file_path, 'rb')
    mesh_data = mesh_file.read()
    mesh_file.close()
    p = 0
    vertices_count = struct.unpack('I', mesh_data[p : p + 4])[0]
    p += 4
    vertices = []
    colors = []
    for vertex_index in range(vertices_count):
        pos = struct.unpack('3f', mesh_data[p : p + 12])
        p += 12
        col = struct.unpack('3f', mesh_data[p : p + 12])
        p += 12
        vertices.append((pos[0], pos[2], pos[1]))
        colors.append(col)

    triangles_count = struct.unpack('I', mesh_data[p : p + 4])[0]
    p += 4
    triangles = []
    for tris_index in range(triangles_count):
        tris = struct.unpack('3I', mesh_data[p : p + 12])
        p += 12
        triangles.append((tris[0], tris[2], tris[1]))

    mesh = bpy.data.meshes.new('temp_name')
    if not domain.jet_fluid.mesh_object:
        mesh_object = bpy.data.objects.new('jet_fluid_mesh', mesh)
        domain.jet_fluid.mesh_object = mesh_object.name
        bpy.context.scene.objects.link(mesh_object)
    else:
        if not bpy.data.objects.get(domain.jet_fluid.mesh_object):
            mesh_object = bpy.data.objects.new(domain.jet_fluid.mesh_object, mesh)
            bpy.context.scene.objects.link(mesh_object)
        else:
            mesh_object = bpy.data.objects[domain.jet_fluid.mesh_object]
            old_mesh = mesh_object.data
            mesh_object.data = mesh
            materials = [m for m in old_mesh.materials]
            for mat in materials:
                mesh.materials.append(mat)
            bpy.data.meshes.remove(old_mesh)

    mesh.from_pydata(vertices, (), triangles)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    mesh.name = 'jet_fluid_mesh'
    mesh_object.location = (
        domain.bound_box[0][0] * domain.scale[0] + domain.location[0],
        domain.bound_box[0][1] * domain.scale[1] + domain.location[1],
        domain.bound_box[0][2] * domain.scale[2] + domain.location[2]
    )
    vertex_colors = mesh.vertex_colors.new('jet_fluid_color')
    i = 0
    for face in mesh.polygons:
        for loop_index in face.loop_indices:
            loop = mesh.loops[loop_index]
            vertex_index = mesh.vertices[loop.vertex_index].index
            color = colors[vertex_index]
            vertex_colors.data[i].color = color
            i += 1


def get_gl_particles_cache():
    global GL_PARTICLES_CACHE
    return GL_PARTICLES_CACHE


def update_particles_cache(self, context):
    global GL_PARTICLES_CACHE
    obj_names = {obj.name for obj in bpy.data.objects}
    for obj_name in obj_names:
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            continue
        if obj.jet_fluid.show_particles:
            file_path = '{}particles_{}.bin'.format(
                bpy.path.abspath(obj.jet_fluid.cache_folder),
                bpy.context.scene.frame_current
            )
            if os.path.exists(file_path):
                particles_file = open(file_path, 'rb')
                particles_data = particles_file.read()
                particles_file.close()
                p = 0
                particles_count = struct.unpack('I', particles_data[p : p + 4])[0]
                p += 4
                if obj.jet_fluid.color_type == 'VELOCITY':
                    positions = []
                    colors = []
                    for particle_index in range(particles_count):
                        particle_position = struct.unpack('3f', particles_data[p : p + 12])
                        p += 12
                        positions.append(particle_position)
                        vel = struct.unpack('3f', particles_data[p : p + 12])
                        p += 36    # skip forces and colors
                        color_factor = (vel[0]**2 + vel[1]**2 + vel[2]**2) ** (1/2) / obj.jet_fluid.max_velocity
                        color = render.generate_particle_color(color_factor, obj.jet_fluid)
                        colors.append(color)
                    GL_PARTICLES_CACHE[obj.name] = [positions, colors]
                elif obj.jet_fluid.color_type == 'SINGLE_COLOR':
                    positions = []
                    for particle_index in range(particles_count):
                        particle_position = struct.unpack('3f', particles_data[p : p + 12])
                        p += 48    # skip velocities, forces and colors
                        positions.append(particle_position)
                    GL_PARTICLES_CACHE[obj.name] = positions
                elif obj.jet_fluid.color_type == 'PARTICLE_COLOR':
                    positions = []
                    colors = []
                    for particle_index in range(particles_count):
                        particle_position = struct.unpack('3f', particles_data[p : p + 12])
                        p += 12
                        positions.append(particle_position)
                        vel = struct.unpack('3f', particles_data[p : p + 12])
                        p += 24    # skip forces
                        color = struct.unpack('3f', particles_data[p : p + 12])
                        p += 12
                        colors.append(color)
                    GL_PARTICLES_CACHE[obj.name] = [positions, colors]


@bpy.app.handlers.persistent
def import_geometry(scene):
    obj_names = {obj.name for obj in bpy.data.objects}
    for obj_name in obj_names:
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            continue
        if obj.jet_fluid.is_active:
            if obj.jet_fluid.create_particles:
                create_particles(obj)
            if obj.jet_fluid.create_mesh:
                create_mesh(obj)
    global GL_PARTICLES_CACHE
    GL_PARTICLES_CACHE = {}
    update_particles_cache(None, bpy.context)


def register():
    bpy.app.handlers.frame_change_pre.append(import_geometry)


def unregister():
    bpy.app.handlers.frame_change_pre.remove(import_geometry)
