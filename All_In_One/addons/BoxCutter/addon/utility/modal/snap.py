import bpy

from math import sqrt
from mathutils import Vector
from statistics import median

from .. import addon, screen, view3d


def test_select(ot, location):
    size = addon.preference().display.snap_dot_size * screen.dpi_factor() * 2
    location = Vector(location[:])
    within_x = ot.mouse.x > location[0] - size and ot.mouse.x < location[0] + size
    within_y = ot.mouse.y > location[1] - size and ot.mouse.y < location[1] + size

    return within_x and within_y

def collect(ot, snap):
    preference = addon.preference()
    bc = bpy.context.window_manager.bc
    snap.index = ot.index

    snap_face = preference.behavior.snap_face
    snap_vert = preference.behavior.snap_vert
    snap_edge = preference.behavior.snap_edge

    if not len(snap.mesh.polygons):
        return

    snap.points.clear()

    if preference.surface in {'CURSOR', 'CENTER'} or bc.snap.grid:
        if preference.behavior.snap_grid:
            for vert in snap.mesh.vertices:
                new = snap.points.add()
                new.location3d = vert.co
    else:

        if not snap.object:
            return

        face = snap.mesh.polygons[ot.index]
        matrix = snap.object.matrix_world.copy()

        if snap_face:
            new = snap.points.add()
            new.location3d = matrix @ face.center
            new.index = ot.index

            del new

        if snap_vert:
            for vert in face.vertices:
                new = snap.points.add()
                new.location3d = matrix @ snap.mesh.vertices[vert].co
                new.index = ot.index

        if snap_edge:
            for indices in face.edge_keys:
                new = snap.points.add()
                vert1 = snap.mesh.vertices[indices[0]]
                vert2 = snap.mesh.vertices[indices[1]]
                edge_center = (vert1.co + vert2.co) * 0.5
                new.location3d = matrix @ edge_center
                new.index = ot.index

        del face


def update(ot, snap):
    preference = addon.preference()
    bc = bpy.context.window_manager.bc

    ot.highlight = False
    ot.highlight_indices = []

    for index, point in enumerate(snap.points):
        location = view3d.location3d_to_location2d(point.location3d)
        point.location2d = location if location else (0, 0)
        point.highlight = False

        if bc.snap.grid:
            location = view3d.location2d_intersect3d(ot.mouse.x, ot.mouse.y, point.location3d, ot.normal)

            if not location:
                location = Vector()

            point_loc = Vector(point.location3d[:])
            distance = (location - point_loc).length
            fade_distance = preference.display.fade_distance
            inverse = distance * fade_distance * 0.5

            if inverse > 1:
                inverse = 1.0

            point.alpha = 1.0 - inverse
            point.display = inverse < 1.0

            highlight = test_select(ot, point.location2d)

            if highlight:
                ot.highlight = True
                ot.highlight_indices.append(index)

            continue

        matrix = snap.object.matrix_world.copy()

        area = snap.mesh.polygons[point.index].area
        normal = matrix.to_3x3() @ Vector((0, 0, 1))
        location = view3d.location2d_intersect3d(ot.mouse.x, ot.mouse.y, point.location3d, normal)

        if not location:
            location = Vector()

        point_loc = Vector(point.location3d[:])

        distance = (location - point_loc).length / (area)
        fade_distance = preference.display.fade_distance
        scale = median((snap.object.scale.x, snap.object.scale.y, snap.object.scale.z))
        inverse = distance * ((sqrt(area) / scale) * fade_distance)

        if inverse > 1:
            inverse = 1.0

        point.alpha = 1.0 - inverse
        point.display = inverse < 1.0

        highlight = test_select(ot, point.location2d)

        if highlight:
            ot.highlight = True
            ot.highlight_indices.append(index)

    if ot.highlight:
        closest = min([
            (ot.mouse - Vector(snap.points[point].location2d[:]), point)
            for point in ot.highlight_indices])

        ot.active_point = snap.points[closest[1]]
        point = ot.active_point
        point.highlight = True
        snap.hit = True
        snap.location = point.location3d

        if bc.snap.grid:
            snap.normal = ot.normal

        else:
            face = snap.mesh.polygons[point.index]
            snap.normal = face.normal.normalized() @ snap.object.matrix_world.inverted()

        del point
        del closest

    else:
        snap.hit = False
        snap.location = (0.0, 0.0, 0.0)
        snap.normal = Vector()
