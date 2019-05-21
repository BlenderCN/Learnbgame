import bpy
import gpu
from gpu_extras.batch import batch_for_shader

width = bpy.context.area.width
size = 10
vertices = (
    (0, 0), (width, 0),
    (0, size), (width, size))

indices = (
    (0, 1, 2), (2, 1, 3))

shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)


def draw():
    shader.bind()
    shader.uniform_float("color", (0, 0.5, 0.5, 1.0))
    batch.draw(shader)


bpy.types.SpaceView3D.draw_handler_add(draw, (), 'WINDOW', 'POST_PIXEL')