
import os
import threading
import struct

import bpy
import mathutils

from . import pyjet
from . import bake


def create_solver(self, domain):
    res_x, res_y, res_z, orig_x, orig_y, orig_z, size_x, _ = bake.calc_res(
        self, domain
    )
    solv = bake.solvers[domain.jet_fluid.solver_type](
        resolution=(res_x, res_z, res_y),
        gridOrigin=(orig_x, orig_z, orig_y),
        domainSizeX=size_x
    )
    res_x, res_y, res_z, orig_x, orig_y, orig_z, size_x, _ = bake.calc_res(
        self, domain, type='MESH'
    )
    grid = pyjet.VertexCenteredScalarGrid3(
        resolution=(res_x, res_z, res_y),
        gridOrigin=(orig_x, orig_z, orig_y),
        domainSizeX=size_x
    )
    return solv, grid


def save_mesh(operator, surface_mesh, frame_index, particles, colors):
    print('save verts')
    domain = operator.domain
    coef = domain.jet_fluid.resolution / domain.jet_fluid.resolution_mesh
    bin_mesh_data = bytearray()
    points_count = surface_mesh.numberOfPoints()
    bin_mesh_data.extend(struct.pack('I', points_count))

    if domain.jet_fluid.use_colors:
        kdtree = mathutils.kdtree.KDTree(len(particles))
        for index, par in enumerate(particles):
            kdtree.insert((par[0], par[2], par[1]), index)
        kdtree.balance()

    offset = (
        domain.bound_box[0][0] * domain.scale[0] + domain.location[0],
        domain.bound_box[0][1] * domain.scale[1] + domain.location[1],
        domain.bound_box[0][2] * domain.scale[2] + domain.location[2]
    )

    for point_index in range(points_count):
        point = surface_mesh.point(point_index)
        bin_mesh_data.extend(struct.pack(
            '3f', point.x * coef, point.y * coef, point.z * coef
        ))
        if domain.jet_fluid.use_colors:
            _, index, _ = kdtree.find((
                point[0] * coef + offset[0],
                point[2] * coef + offset[1],
                point[1] * coef + offset[2]
            ))
            color = colors[index]
            bin_mesh_data.extend(struct.pack(
                '3f', *color
            ))
        else:
            bin_mesh_data.extend(struct.pack(
                '3f', 0.0, 0.0, 0.0
            ))

    print('save tris')
    triangles_count = surface_mesh.numberOfTriangles()
    bin_mesh_data.extend(struct.pack('I', triangles_count))
    for triangle_index in range(triangles_count):
        tris = surface_mesh.pointIndex(triangle_index)
        bin_mesh_data.extend(struct.pack('3I', tris.x, tris.y, tris.z))

    print('write file')
    file_path = '{}mesh_{}.bin'.format(
        bpy.path.abspath(domain.jet_fluid.cache_folder),
        frame_index
    )
    file = open(file_path, 'wb')
    file.write(bin_mesh_data)
    file.close()
    print('save mesh end')


def check_cache_file(domain, frame_index):
    file_path = '{}mesh_{}.bin'.format(
        bpy.path.abspath(domain.jet_fluid.cache_folder),
        frame_index
    )
    if os.path.exists(file_path):
        return True
    else:
        return False


def read_particles(domain, frame_index):
    points = []
    colors = []
    file_path = '{}particles_{}.bin'.format(
        bpy.path.abspath(domain.jet_fluid.cache_folder),
        frame_index
    )
    if not os.path.exists(file_path):
        print('can\'t find particles file in {} frame'.format(frame_index))
        return points, colors
    print('open particles file')
    particles_file = open(file_path, 'rb')
    particles_data = particles_file.read()
    particles_file.close()
    print('read particles')
    p = 0
    particles_count = struct.unpack('I', particles_data[p : p + 4])[0]
    p += 4
    for particle_index in range(particles_count):
        particle_position = struct.unpack('3f', particles_data[p : p + 12])
        p += 36    # skip velocities, forces
        color = struct.unpack('3f', particles_data[p : p + 12])
        p += 12
        points.append(particle_position)
        if domain.jet_fluid.use_colors:
            colors.append(color)
    return points, colors


def bake_mesh(domain, solv, grid, frame_index):
    print('frame', frame_index)
    points, colors = read_particles(domain, frame_index)
    if not points:
        return None, points, colors
    print('create converter')
    converter = pyjet.SphPointsToImplicit3(2.0 * solv.gridSpacing.x, 0.5)
    print('convert')
    converter.convert(points, grid)
    print('meshing')
    con_flag = bake.set_closed_domain_boundary_flag(domain, 'mesh_connectivity_boundary')
    close_flag = bake.set_closed_domain_boundary_flag(domain, 'mesh_closed_boundary')
    surface_mesh = pyjet.marchingCubes(
        grid,
        (solv.gridSpacing.x, solv.gridSpacing.y, solv.gridSpacing.z),
        (0, 0, 0),
        0.0,
        close_flag,
        con_flag
    )
    return surface_mesh, points, colors


class JetFluidBakeMesh(bpy.types.Operator):
    bl_idname = "jet_fluid.bake_mesh"
    bl_label = "Bake Mesh"
    bl_options = {'REGISTER'}

    def execute(self, context):
        pyjet.Logging.mute()
        scn = context.scene
        domain = scn.objects.active
        if not domain.jet_fluid.cache_folder:
            self.report({'WARNING'}, 'Cache Folder not Specified!')
            return {'FINISHED'}
        solv, grid = create_solver(self, domain)
        for frame_index in range(scn.frame_start, scn.frame_end + 1):
            has_cache = check_cache_file(domain, frame_index)
            if has_cache:
                print('skip frame', frame_index)
            else:
                surface_mesh, particles, colors = bake_mesh(domain, solv, grid, frame_index)
                if surface_mesh:
                    save_mesh(self, surface_mesh, frame_index, particles, colors)
        return {'FINISHED'}

    def invoke(self, context, event):
        thread = threading.Thread(target=self.execute, args=(context, ))
        thread.start()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(JetFluidBakeMesh)


def unregister():
    bpy.utils.unregister_class(JetFluidBakeMesh)
