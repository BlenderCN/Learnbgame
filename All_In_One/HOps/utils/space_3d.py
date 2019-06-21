import math


def centroid(points):
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    z = [p[2] for p in points]
    centroid = (sum(x) / len(points), sum(y) / len(points), sum(z) / len(points))

    return centroid


def scale(origin, point, value):
        ox, oy, oz = origin
        px, py, pz = point

        px = (px-ox)*value+ox
        py = (py-oy)*value+oy
        pz = (pz-oz)*value+oz

        return px, py, pz


def transform3D(point, location1, location2):
        px, py, pz = point
        x = [0, 0, 0]

        x[0] = location1[0] - px
        x[1] = location1[1] - py
        x[2] = location1[2] - pz
        px = location2[0] - x[0]
        py = location2[1] - x[1]
        pz = location2[2] - x[2]

        return px, py, pz


def rotate_z(origin, point, angle):
    ox, oy, oz = origin
    px, py, pz = point

    # Z rotation
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    qz = pz

    return qx, qy, qz


def rotate_x(origin, point, angle):
    ox, oy, oz = origin
    px, py, pz = point

    # X rotation
    qx = px
    qz = oz + math.sin(angle) * (pz - oz) - math.cos(angle) * (py - oy)
    qy = oy + math.cos(angle) * (pz - oz) + math.sin(angle) * (py - oy)

    return qx, qy, qz


def rotate_y(origin, point, angle):
    ox, oy, oz = origin
    px, py, pz = point

    # Y rotation
    qy = py
    qx = ox + math.sin(angle) * (px - ox) - math.cos(angle) * (pz - oz)
    qz = oz + math.cos(angle) * (px - ox) + math.sin(angle) * (pz - oz)

    return qx, qy, qz
