from ..utils.draw import draw_line
from ..utils.draw import draw_square

import blf

def draw_pixelate_controls(self, context):
    """
    Draws the line, 2 boxes, and the control square
    """
    w = context.region.width
    h = context.region.height
    line_width = 2 * (w / 10)
    offset_x = (line_width / 2) - (line_width * self.pixel_factor)
    x = self.first_mouse.x + offset_x
    y = self.first_mouse.y + self.pos.y

    v1 = [(-w / 10) + x, y]
    v2 = [(w / 10) + x, y]

    color = (0, 0.75, 1, 1)

    draw_line(v1, v2, 1, color)
    
    vertex = [x - (w / 10) + self.pos.x, y]
    draw_square(vertex, 10, color)

    # Numbers
    font_id = 0
    blf.position(font_id, vertex[0] - 20, vertex[1] + 10, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, str(self.fac))
