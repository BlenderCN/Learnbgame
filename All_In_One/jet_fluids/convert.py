
import os
import struct

import bpy


def save_blender_particles_cache_times(folder, times, frame_end):
    indices = list(times.keys())
    indices.sort()

    file = open(folder + 'fluid_{:0>6}_00.bphys'.format(0), 'wb')
    file.write(b'BPHYSICS')
    file.write(struct.pack('I', 1))    # cache type (1 - particles)
    file.write(struct.pack('I', indices[-1]))    # particles count
    file.write(struct.pack('I', 0b1000000))    # particles data types

    io = struct.Struct('3f')
    for index in indices:
        time = times[index]
        file.write(io.pack(time, frame_end, frame_end))

    file.close()

    particles_count = indices[-1]
    return particles_count


def save_blender_particles_cache(frame_index, folder, par_file, times):
    file = open(folder + 'fluid_{:0>6}_00.bphys'.format(frame_index), 'wb')
    particles_count = struct.unpack('I', par_file.read(4))[0]
    file.write(b'BPHYSICS')
    file.write(struct.pack('I', 1))    # cache type (1 - particles)
    file.write(struct.pack('I', particles_count))
    file.write(struct.pack('I', 0b10111))    # particles data types
    unpacker = struct.Struct('12f')
    packer = struct.Struct('9f')

    for particle_index in range(particles_count):

        file.write(struct.pack('I', particle_index))

        (pos_x, pos_z, pos_y,
        vel_x, vel_z, vel_y,
        for_x, for_z, for_y,
        col_r, col_g, col_b) = unpacker.unpack(par_file.read(48))

        file.write(packer.pack(
            pos_x, pos_y, pos_z,
            vel_x, vel_y, vel_z,
            col_r, col_g, col_b
        ))

        if not times.get(particle_index):
            times[particle_index] = frame_index

    file.close()

    return times


def convert_particles_to_standart_particle_system(context, domain):
    times = {}
    folder = bpy.path.abspath(domain.jet_fluid.cache_folder)
    frame_end = context.scene.frame_end + 1

    for frame_index in range(0, frame_end):
        file_path = '{}particles_{}.bin'.format(folder, frame_index)
        if not os.path.exists(file_path):
            continue
        particles_file = open(file_path, 'rb')
        times = save_blender_particles_cache(frame_index, folder, particles_file, times)
        particles_file.close()

    if times:
        particles_count = save_blender_particles_cache_times(folder, times, frame_end)

        if domain.particle_systems.get('fluid'):
            par_sys = domain.particle_systems['fluid']
        else:
            bpy.ops.object.particle_system_add()
            par_sys = domain.particle_systems.active
            par_sys.name = 'fluid'

        par_sys.point_cache.use_external = True
        par_sys.point_cache.filepath = domain.jet_fluid.cache_folder
        par_sys.point_cache.name = 'fluid'
        par_sys.point_cache.index = 0
        par_sys.settings.count = particles_count
        par_sys.settings.draw_color = 'VELOCITY'
        par_sys.settings.color_maximum = 10.0
