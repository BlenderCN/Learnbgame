
import struct
import os

import bpy

from . import pyjet


solvers = {
    'APIC': pyjet.ApicSolver3,
    'PIC': pyjet.PicSolver3,
    'FLIP': pyjet.FlipSolver3
}
advection_solvers = {
    'SEMI_LAGRANGIAN': pyjet.SemiLagrangian3,
    'CUBIC_SEMI_LAGRANGIAN': pyjet.CubicSemiLagrangian3
}
diffusion_solvers = {
    'FORWARD_EULER': pyjet.GridForwardEulerDiffusionSolver3,
    'BACKWARD_EULER': pyjet.GridBackwardEulerDiffusionSolver3
}
pressure_solvers = {
    'FRACTIONAL_SINGLE_PHASE': pyjet.GridFractionalSinglePhasePressureSolver3,
    'SINGLE_PHASE': pyjet.GridSinglePhasePressureSolver3
}


def read_particles(file_path):
    particles_file = open(file_path, 'rb')
    particles_data = particles_file.read()
    particles_file.close()
    p = 0
    particles_count = struct.unpack('I', particles_data[p : p + 4])[0]
    p += 4
    positions = []
    velocities = []
    forces = []
    colors = []
    for particle_index in range(particles_count):
        pos = struct.unpack('3f', particles_data[p : p + 12])
        p += 12
        positions.append(pos)
        vel = struct.unpack('3f', particles_data[p : p + 12])
        p += 12
        velocities.append(vel)
        force = struct.unpack('3f', particles_data[p : p + 12])
        p += 12
        forces.append(force)
        color = struct.unpack('3f', particles_data[p : p + 12])
        p += 12
        colors.append(color)
    return positions, velocities, forces, colors


def get_triangle_mesh(context, source, solver, domain_object):
    selected_objects_name = [o.name for o in context.selected_objects]
    active_object_name = context.scene.objects.active.name
    bpy.ops.object.select_all(action='DESELECT')
    source.select = True
    bpy.ops.object.duplicate()
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj = context.selected_objects[0]
    mesh = obj.data
    context.scene.objects.active = obj
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
    bpy.ops.object.mode_set(mode='OBJECT')
    print('generete Triangle Mesh')
    triangle_mesh = pyjet.TriangleMesh3(
        points=[[v.co.x, v.co.z, v.co.y] for v in mesh.vertices],
        pointIndices=[[p.vertices[0], p.vertices[2], p.vertices[1]] for p in mesh.polygons]
    )
    print('generete Implicit Triangle Mesh')
    imp_triangle_mesh = pyjet.ImplicitTriangleMesh3(
        mesh=triangle_mesh,
        resolutionX=int(round(
            solver.resolution.x * obj.dimensions[0] / domain_object.dimensions[0],
            0
        )),
        margin=0.2
    )
    print('remove objects')
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    for obj_name in selected_objects_name:
        bpy.data.objects[obj_name].select = True
    bpy.context.scene.objects.active = bpy.data.objects[active_object_name]
    return imp_triangle_mesh


def set_closed_domain_boundary_flag(obj, flag_type):
    jet = obj.jet_fluid
    if flag_type == 'domain_closed_boundary':
        bounds = [
            jet.bound_right,
            jet.bound_left,
            jet.bound_front,
            jet.bound_back,
            jet.bound_up,
            jet.bound_down
        ]
    elif flag_type == 'mesh_connectivity_boundary':
        bounds = [
            jet.con_right,
            jet.con_left,
            jet.con_front,
            jet.con_back,
            jet.con_up,
            jet.con_down
        ]
    elif flag_type == 'mesh_closed_boundary':
        bounds = [
            jet.close_right,
            jet.close_left,
            jet.close_front,
            jet.close_back,
            jet.close_up,
            jet.close_down
        ]
    else:
        raise 'Unsupported flag type'
    flags = [
        pyjet.DIRECTION_RIGHT,
        pyjet.DIRECTION_LEFT,
        pyjet.DIRECTION_FRONT,
        pyjet.DIRECTION_BACK,
        pyjet.DIRECTION_UP,
        pyjet.DIRECTION_DOWN
        
    ]

    bound_flag = 0
    for bound_index, bound in enumerate(bounds):
        if bound:
            bound_flag |= flags[bound_index]

    return bound_flag


def calc_res(self, obj, type='FLUID'):
    self.domain = obj
    domain_size_x = obj.bound_box[6][0] * obj.scale[0] - obj.bound_box[0][0] * obj.scale[0]
    domain_size_y = obj.bound_box[6][1] * obj.scale[1] - obj.bound_box[0][1] * obj.scale[1]
    domain_size_z = obj.bound_box[6][2] * obj.scale[2] - obj.bound_box[0][2] * obj.scale[2]
    domain_sizes = [
        domain_size_x,
        domain_size_y,
        domain_size_z
    ]
    self.domain_size_x = domain_size_x
    if type == 'FLUID':
        resolution = obj.jet_fluid.resolution
        grid_spacing = (0, 0, 0)
    elif type == 'MESH':
        resolution = obj.jet_fluid.resolution_mesh
        fluid_res = obj.jet_fluid.resolution
        grid_spacing_x = resolution
        grid_spacing_y = resolution
        grid_spacing_z = resolution
        grid_spacing = (grid_spacing_x, grid_spacing_z, grid_spacing_y)
    self.domain_max_size = max(domain_sizes)
    resolution_x = int(round((domain_size_x / self.domain_max_size) * resolution, 1))
    resolution_y = int(round((domain_size_y / self.domain_max_size) * resolution, 1))
    resolution_z = int(round((domain_size_z / self.domain_max_size) * resolution, 1))
    origin_x = obj.bound_box[0][0] * obj.scale[0] + obj.location[0]
    origin_y = obj.bound_box[0][1] * obj.scale[1] + obj.location[1]
    origin_z = obj.bound_box[0][2] * obj.scale[2] + obj.location[2]
    return resolution_x, resolution_y, resolution_z, origin_x, origin_y, origin_z, domain_size_x, grid_spacing
