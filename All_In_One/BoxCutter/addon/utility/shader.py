import bpy
import bmesh
import gpu

from bgl import *
from gpu_extras.batch import batch_for_shader

from . import addon


def logo():
    pass


class shape:
    batch = None
    verts: tuple
    indice_edges: tuple
    indice_tri_loop: tuple


    def __init__(self, ot, context):
        preference = addon.preference()

        dat = ot.datablock['shape'].to_mesh(context.depsgraph, apply_modifiers=True)
        dat.calc_loop_triangles()

        self.verts = tuple(ot.datablock['lattice'].matrix_world @ vert.co for vert in dat.vertices)
        self.indice_edges = tuple(dat.edge_keys)
        self.indice_tri_loop = tuple(loop.vertices for loop in dat.loop_triangles)

        self.geometry(ot, context, color=getattr(preference, F'{ot.mode.lower()}_color'))

        if ot.shape == 'CIRCLE':
            d = ot.datablock['shape_d'].to_mesh(context.depsgraph, apply_modifiers=True)
            self.verts = tuple(ot.datablock['lattice'].matrix_world @ vert.co for vert in d.vertices)
            self.indice_edges = tuple(d.edge_keys)

        self.wires(ot, context, color=preference.wire_color)
        
        if preference.show_bounds:
            self.bounds(ot, context)

        bpy.data.meshes.remove(dat)
        del dat

        if ot.shape == 'CIRCLE':
            bpy.data.meshes.remove(d)
            del d


    def geometry(self, ot, context, color=tuple()):
        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {'pos': self.verts}, indices=self.indice_tri_loop)

        shader.bind()
        shader.uniform_float('color', color)

        glEnable(GL_BLEND)
        glDepthFunc(GL_ALWAYS)
        batch.draw(shader)
        glDisable(GL_BLEND)


    def wires(self, ot, context, color=tuple()):
        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {'pos': self.verts}, indices=self.indice_edges)

        shader.bind()
        shader.uniform_float('color', color)

        glEnable(GL_BLEND)
        batch.draw(shader)
        glDisable(GL_BLEND)


    def bounds(self, ot, context):
        pass