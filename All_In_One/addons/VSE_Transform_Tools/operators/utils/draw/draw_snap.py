import bgl
from mathutils import Vector

from .draw_line import draw_line


def draw_snap(self, loc, orientation):
    """
    Draws the purple snap lines
    """
    color = (1.0, 0.0, 1.0, 0.5)
    thickness = 2

    if orientation == "VERTICAL":
        v1 = [loc, -10000]
        v2 = [loc, 10000]

    elif orientation == "HORIZONTAL":
        v1 = [-10000, loc]
        v2 = [10000, loc]
    
    draw_line(v1, v2, thickness, color)
