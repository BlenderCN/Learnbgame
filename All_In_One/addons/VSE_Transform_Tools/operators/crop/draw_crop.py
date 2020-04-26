import gpu
from gpu_extras.batch import batch_for_shader

from .set_corners import set_corners
from .set_quads import set_quads

from ..utils.draw import draw_line

def draw_crop(self, context):
    active_strip = context.scene.sequence_editor.active_strip

    #theme = context.user_preferences.themes['Default']
    #active_color = theme.view_3d.object_active

    #active_color = (active_color[0], active_color[1], active_color[2], 1.0)
    active_color = (1.0, 0.5, 0, 1)
    color = (0, 1.0, 1.0, 1.0)

    set_corners(self, context)
    set_quads(self, context)

    vertices = []
    for corner in self.corners:
        vertices.append([corner[0], corner[1]])

    draw_line(vertices[0], vertices[1], 1, color)
    draw_line(vertices[1], vertices[2], 1, color)
    draw_line(vertices[2], vertices[3], 1, color)
    draw_line(vertices[3], vertices[0], 1, color)

    for i in range(len(self.corner_quads)):
        quad = self.corner_quads[i]

        bl = quad[0]
        tl = quad[1]
        tr = quad[2]
        br = quad[3]

        vertices = [bl, br, tl, tr]

        indices = ((0, 1, 2), (2, 1, 3))

        shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
        batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)

        shader.bind()

        if self.clicked_quad == i:
            shader.uniform_float("color", active_color)

        else:
            shader.uniform_float("color", color)

        batch.draw(shader)
