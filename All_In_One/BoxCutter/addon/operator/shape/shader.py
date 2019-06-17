import bpy
import bmesh
import gpu

from math import cos, sin

from bgl import *
from gpu_extras.batch import batch_for_shader

from mathutils import *

from ... utility import addon, screen


class snap:


    def __init__(self, ot, context):
        preference = addon.preference()

        if preference.behavior.snap:
            self.points(ot, context)


    def points(self, ot, context):
        bc = context.window_manager.bc

        if bc.snap.display and not bc.running:
            for point in bc.snap.points:
                if point.display:
                    self.point(point)


    def point(self, point):
        preference = addon.preference()
        size = addon.preference().display.snap_dot_size * 0.5 * screen.dpi_factor()

        vertices = (
            (point.location2d[0] - size, point.location2d[1] - size),
            (point.location2d[0] + size, point.location2d[1] - size),
            (point.location2d[0] - size, point.location2d[1] + size),
            (point.location2d[0] + size, point.location2d[1] + size))

        indices = ((0, 1, 2), (2, 1, 3))

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {'pos': vertices}, indices=indices)

        shader.bind()
        col = Vector(preference.color.snap_point[:]) if not point.highlight else Vector(preference.color.snap_point_highlight[:])

        if not point.highlight:
            col[3] = point.alpha * preference.color.snap_point[3]

        shader.uniform_float('color', col)

        glEnable(GL_BLEND)
        batch.draw(shader)
        glDisable(GL_BLEND)

        del shader
        del batch


class shape:
    verts: tuple
    indice_edges: tuple
    indice_tri_loop: tuple


    def __init__(self, ot, context):
        bc = context.window_manager.bc

        preference = addon.preference()

        try:
            dat = bc.shape.to_mesh(context.depsgraph, apply_modifiers=True)
        except:
            print('BC: Not recieving shader input (Missing Data)')
            return

        bm = bmesh.new()
        bm.from_mesh(dat)

        if ot.shape_type == 'CIRCLE':
            bmesh.ops.dissolve_limit(bm, angle_limit=0.0175, use_dissolve_boundaries=True, verts=bm.verts, edges=bm.edges)

        bm.to_mesh(dat)
        bm.free()

        dat.update()
        dat.calc_loop_triangles()

        self.verts = tuple(bc.shape.matrix_world @ vert.co for vert in dat.vertices)
        self.indice_edges = tuple(dat.edge_keys)
        self.indice_tri_loop = tuple(loop.vertices for loop in dat.loop_triangles)

        color = Vector(getattr(preference.color, ot.mode.lower()))
        color[3] = color[3] * 1.75 if ot.shape_type == 'NGON' and not ot.extruded else color[3]

        for mod in bc.shape.modifiers:
            if mod.type == 'SOLIDIFY':
                color[3] = color[3] * 0.5
                break

        wire_color = preference.color.wire
        if preference.display.wire_only:
            wire_color = (color[0], color[1], color[2], wire_color[3])
            self.wires(ot, context, color=wire_color)

        else:
            self.geometry(ot, context, color=color)
            self.wires(ot, context, color=wire_color)

        bpy.data.meshes.remove(dat)

        del dat


    def geometry(self, ot, context, color=tuple()):
        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {'pos': self.verts}, indices=self.indice_tri_loop)

        shader.bind()
        shader.uniform_float('color', color)

        glEnable(GL_BLEND)
        glDepthFunc(GL_ALWAYS)
        batch.draw(shader)
        glDisable(GL_BLEND)

        del shader
        del batch


    def wires(self, ot, context, color=tuple()):
        preference = addon.preference()

        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'LINES', {'pos': self.verts}, indices=self.indice_edges)

        shader.bind()
        shader.uniform_float('color', color)

        width = preference.display.wire_width * screen.dpi_factor()
        if preference.display.wire_only and preference.display.thick_wire:
            width *= preference.display.wire_size_factor

        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)

        if preference.display.wire_only:
            glDepthFunc(GL_ALWAYS)

        glLineWidth(width)
        batch.draw(shader)
        glDisable(GL_LINE_SMOOTH)
        glDisable(GL_BLEND)

        del shader
        del batch


    def bounds(self, ot, context):
        pass
