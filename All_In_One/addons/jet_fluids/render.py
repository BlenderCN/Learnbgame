
import struct
import os

import bpy
import bgl

from . import create


handle_3d = None


def generate_particle_color(factor, jet_props):
    r = jet_props.color_1[0] + factor * (jet_props.color_2[0] - jet_props.color_1[0])
    g = jet_props.color_1[1] + factor * (jet_props.color_2[1] - jet_props.color_1[1])
    b = jet_props.color_1[2] + factor * (jet_props.color_2[2] - jet_props.color_1[2])
    return (r, g, b)


def draw_scene_particles():
    for obj in bpy.data.objects:
        if obj.jet_fluid.is_active:
            if obj.jet_fluid.show_particles:
                particles = create.get_gl_particles_cache().get(obj.name, None)
                if particles:
                    draw_particles(obj, particles)


def draw_particles(domain, particles):
    bgl.glPointSize(domain.jet_fluid.particle_size)
    bgl.glBegin(bgl.GL_POINTS)
    if domain.jet_fluid.color_type == 'VELOCITY':
        positions = particles[0]
        colors = particles[1]
        for index, pos in enumerate(positions):
            bgl.glColor4f(colors[index][0], colors[index][1], colors[index][2], 1.0)
            bgl.glVertex3f(pos[0], pos[2], pos[1])
    elif domain.jet_fluid.color_type == 'SINGLE_COLOR':
        color = domain.jet_fluid.color_1
        bgl.glColor4f(color[0], color[1], color[2], 1.0)
        for particle_position in particles:
            bgl.glVertex3f(
                particle_position[0],
                particle_position[2],
                particle_position[1]
            )
    elif domain.jet_fluid.color_type == 'PARTICLE_COLOR':
        positions = particles[0]
        colors = particles[1]
        for index, pos in enumerate(positions):
            bgl.glColor4f(colors[index][0], colors[index][1], colors[index][2], 1.0)
            bgl.glVertex3f(pos[0], pos[2], pos[1])
    bgl.glEnd()


def register():
    global handle_3d
    handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw_scene_particles, (), 'WINDOW', 'POST_VIEW')


def unregister():
    global handle_3d
    bpy.types.SpaceView3D.draw_handler_remove(handle_3d, 'WINDOW')
