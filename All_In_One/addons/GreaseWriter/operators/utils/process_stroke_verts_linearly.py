import math
import copy
from .distance_formula import distance_formula

def process_stroke_verts_linearly(original_stroke_verts, speed, remaining=0, stipple=False):
    """
    We have a group of vertices that represents a stroke,
    but we need to know how much of that stroke to draw on each frame.

    We use the given draw speed to calculate how much more of the stroke
    to draw with each frame. The result is a list of vertex-groups to be
    drawn with each frame

    This algorithm also works for stippling

    Parameters
    ----------
    stroke_verts: list of vertices (integer pairs of x and y)
    speed: float that is > 0.0

    Returns
    -------
    framed_strokes: list of lists of vertices (x & y coordinate pairs)
    """
    stroke_verts = copy.deepcopy(original_stroke_verts)
    framed_strokes = [[stroke_verts[0]]]

    remaining = speed + remaining
    i = 1
    while i < len(stroke_verts):
        v1 = stroke_verts[i - 1]
        v2 = stroke_verts[i]
        distance = distance_formula(v1, v2)

        x = v2[0] - v1[0]
        y = v2[1] - v1[1]
        z = v2[2] - v1[2]

        if distance > remaining:
            new_x = ((remaining / distance) * x) + v1[0]
            new_y = ((remaining / distance) * y) + v1[1]
            new_z = ((remaining / distance) * z) + v1[2]

            framed_strokes[-1].append([new_x, new_y, new_z])
            if stipple == False:
                framed_strokes.append(copy.deepcopy(framed_strokes[-1]))
            else:
                framed_strokes.append([[new_x, new_y, new_z]])

            stroke_verts[i - 1] = [new_x, new_y, new_z]
            remaining = speed

        else:
            framed_strokes[-1].append(v2)
            remaining -= distance
            i += 1

    return framed_strokes, remaining


