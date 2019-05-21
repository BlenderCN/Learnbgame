import math
import gpu
from gpu_extras.batch import batch_for_shader

def draw_line(v1, v2, thickness, color):
    if (v2[0] == v1[0]):
        x = thickness
        y = 0
    elif (v2[1] == v1[1]):
        x = 0
        y = thickness

    else:
        angle = math.atan((v2[1] - v1[1]) / (v2[0] - v1[0]))
        x = thickness * math.sin(angle)
        y = thickness * math.cos(angle)
    
    vertices = (
        (v1[0] + x, v1[1] - y),
        (v2[0] + x, v2[1] - y),
        (v1[0] - x, v1[1] + y),
        (v2[0] - x, v2[1] + y),
    )
    
    indices = ((0, 1, 2), (2, 1, 3))
    
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
