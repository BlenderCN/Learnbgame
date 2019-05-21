import math
from math import sqrt
import gpu
from gpu_extras.batch import batch_for_shader

from .draw_line import draw_line

def distance_formula(p1, p2):
    """
    Calculate the distance between 2 points on a 2D Cartesian coordinate plane

    Parameters
    ----------
    p1: list of int
        The x and y of a point, ie: [1, 0]
    p2: list of int
        The x and y of a point, ie: [2, 3]

    Returns
    -------
    distance: float
        The distance between the 2 points
    """
    x = p2[0] - p1[0]
    y = p2[1] - p1[1]

    distance = sqrt(x**2 + y**2)
    return distance

def get_next_point(origin, angle, distance):
    """
    Get the next point given an origin, an angle, and a distance to go
    """
    v2_x = origin[0] + (math.cos(angle) * distance)
    v2_y = origin[1] + (math.sin(angle) * distance)
    
    return [v2_x, v2_y]
    
def draw_stippled_line(v1, v2, thickness, stipple_length, color):
    distance = distance_formula(v1, v2)
    
    count = int(distance / (stipple_length + (thickness * 3)))
    
    if v2[0] == v1[0]:
        if v2[1] > v1[1]:
            angle = math.radians(-90)
        else:
            angle = math.radians(90)
    else:
        angle = math.atan((v2[1] - v1[1]) / (v2[0] - v1[0]))
    
    if v2[0] > v1[0]:
        pass
    elif v2[1] < v1[1]:
        angle -= math.radians(180)
    
    else:
        angle += math.radians(180)
    
    pairs = []
    
    last_point = v1
    for i in range(count):
        new_point = get_next_point(last_point, angle, stipple_length)
        pairs.append([last_point, new_point])
        last_point = get_next_point(new_point, angle, (thickness * 3))
    
    for pair in pairs:
        draw_line(pair[0], pair[1], thickness, color)
    
    
    
