import math
from .draw_line import draw_line

def get_next_point(origin, angle, distance):
    """
    Get the next point given an origin, an angle, and a distance to go
    """
    v2_x = origin[0] + (math.cos(angle) * distance)
    v2_y = origin[1] + (math.sin(angle) * distance)
    
    return [v2_x, v2_y]


def draw_arrows(v1, v2, thickness, arrow_length, color, angle_offset=0):
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
    
    angle += math.radians(angle_offset)
    
    r_start = get_next_point(v2, angle, thickness * 3)
    r_end = get_next_point(r_start, angle, arrow_length)
    
    r_upper_ala_end = get_next_point(r_end, angle + math.radians(210), arrow_length * 0.667)
    r_lower_ala_end = get_next_point(r_end, angle + math.radians(-210), arrow_length * 0.667)
    
    
    angle += math.radians(180)
    
    l_start = get_next_point(v2, angle, thickness * 3)
    l_end = get_next_point(l_start, angle, arrow_length)
    
    l_upper_ala_end = get_next_point(l_end, angle + math.radians(-210), arrow_length * 0.667)
    l_lower_ala_end = get_next_point(l_end, angle + math.radians(210), arrow_length * 0.667)
    
    draw_line(r_start, r_end, thickness, color)
    draw_line(r_end, r_upper_ala_end, thickness, color)
    draw_line(r_end, r_lower_ala_end, thickness, color)

    draw_line(l_start, l_end, thickness, color)
    draw_line(l_end, l_upper_ala_end, thickness, color)
    draw_line(l_end, l_lower_ala_end, thickness, color)
