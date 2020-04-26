import gpu
from gpu_extras.batch import batch_for_shader

def draw_square(vertex, thickness, color):
    """
    Draws a square
    """
    r = thickness / 2
    
    vertices = (
        (vertex[0] - r, vertex[1] - r),
        (vertex[0] + r, vertex[1] - r),
        (vertex[0] - r, vertex[1] + r),
        (vertex[0] + r, vertex[1] + r)
    )
    
    indices = ((0, 1, 2), (2, 1, 3))
    
    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
