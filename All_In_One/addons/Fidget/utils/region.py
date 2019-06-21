import bpy
import math
import numpy as np


def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def scale(origin, point, value):
    ox, oy = origin
    px, py = point

    px = (px-ox)*value+ox
    py = (py-oy)*value+oy

    return px, py


def inside_polygon(x, y, points):

    n = len(points)
    inside = False
    p1x, p1y = points[0]
    for i in range(1, n + 1):
        p2x, p2y = points[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

# ============ from dairin0d's library ============ #


def point_in_rect(p, r):
    return ((p[0] >= r.x) and (p[0] < r.x + r.width) and (p[1] >= r.y) and (p[1] < r.y + r.height))


def rv3d_from_region(area, region):
    if (area.type != 'VIEW_3D') or (region.type != 'WINDOW'): return None

    space_data = area.spaces.active
    try:
        quadviews = space_data.region_quadviews
    except AttributeError:
        quadviews = None # old API

    if not quadviews: return space_data.region_3d

    x_id = 0
    y_id = 0
    for r in area.regions:
        if (r.type == 'WINDOW') and (r != region):
            if r.x < region.x: x_id = 1
            if r.y < region.y: y_id = 1

    # 0: bottom left (Front Ortho)
    # 1: top left (Top Ortho)
    # 2: bottom right (Right Ortho)
    # 3: top right (User Persp)
    return quadviews[y_id | (x_id << 1)]

# areas can't overlap, but regions can


def ui_contexts_under_coord(x, y, window=None):
    point = int(x), int(y)
    if not window: window = bpy.context.window
    screen = window.screen
    scene = screen.scene
    tool_settings = scene.tool_settings
    for area in screen.areas:
        if point_in_rect(point, area):
            space_data = area.spaces.active
            for region in area.regions:
                if point_in_rect(point, region):
                    yield dict(window=window, screen=screen,
                               area=area, space_data=space_data, region=region,
                               region_data=rv3d_from_region(area, region),
                               scene=scene, tool_settings=tool_settings)
            break


def region_exists(r):
    wm = bpy.context.window_manager
    for window in wm.windows:
        for area in window.screen.areas:
            for region in area.regions:
                if region == r: return True
    return False


def calculate_angle(point_a, point_b):
    ang_a = np.arctan2(*point_a[::-1])
    ang_b = np.arctan2(*point_b[::-1])
    return np.rad2deg((ang_a - ang_b) % (2 * np.pi))
