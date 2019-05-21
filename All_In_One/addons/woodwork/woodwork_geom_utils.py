from enum import Enum
from math import pi

from mathutils import Vector
from mathutils.geometry import intersect_point_line

from . woodwork_math_utils import MathUtils


class Position(Enum):
    in_front = 1
    behind = 2
    on_plane = 3
    intersecting = 4


class GeomUtils:
    POINT_ON_SIDE_ABSOLUTE_ERROR_THRESHOLD = 1.e-4
    POINTS_ARE_NEAR_ABSOLUTE_ERROR_THRESHOLD = 1.e-5
    POINTS_ARE_SAME_ABSOLUTE_ERROR_THRESHOLD = 1.e-6

    @staticmethod
    def is_face_planar(face):
        position = GeomUtils.face_position(face, face.verts[0].co, face.normal)
        return position == Position.on_plane

    @staticmethod
    def is_face_rectangular(face, error=0.0005):
        for loop in face.loops:
            perp_angle = loop.calc_angle() - (pi / 2)
            if perp_angle < -error or perp_angle > error:
                return False
        return True

    @staticmethod
    def distance_point_edge(pt, edge):
        line_p1 = edge.verts[0].co
        line_p2 = edge.verts[1].co
        ret = intersect_point_line(pt, line_p1, line_p2)
        closest_point_on_line = ret[0]
        distance_vector = closest_point_on_line - pt
        return distance_vector.length

    @staticmethod
    def face_position(face, plane_co, plane_no) -> Position:
        vert_positions = set()
        # plane equation with normal vector plane_no = (a, b, c) through the
        # point plane_co = (x0, y0, z0) is
        # a x + b y + c z + d = 0 where d = -a x0 -b y0 -c z0
        d = -(plane_no * plane_co)
        for vert in face.verts:

            pseudo_distance = plane_no * vert.co + d

            if MathUtils.almost_zero(
                    pseudo_distance,
                    GeomUtils.POINT_ON_SIDE_ABSOLUTE_ERROR_THRESHOLD):
                vert_position = Position.on_plane
            elif pseudo_distance > 0.0:
                vert_position = Position.in_front
            else:
                vert_position = Position.behind

            vert_positions.add(vert_position)
        if len(vert_positions) == 1:
            face_position = next(iter(vert_positions))
        else:
            face_position = Position.intersecting
        return face_position

    @staticmethod
    def distance_point_to_plane(vert_co, plane_co, plane_no):
        d = -(plane_no * plane_co)

        return plane_no * vert_co + d

    @staticmethod
    def point_position(vert, plane_co, plane_no) -> Position:

        dist = GeomUtils.distance_point_to_plane(
            vert.co, plane_co, plane_no)

        if MathUtils.almost_zero(
                dist,
                GeomUtils.POINT_ON_SIDE_ABSOLUTE_ERROR_THRESHOLD):
            vert_position = Position.on_plane
        elif dist > 0.0:
            vert_position = Position.in_front
        else:
            vert_position = Position.behind

        return vert_position

    @staticmethod
    def points_are_same(vector0, vector1):
        same = False
        dist = vector0[0] - vector1[0]
        if (dist > -GeomUtils.POINTS_ARE_SAME_ABSOLUTE_ERROR_THRESHOLD) and (
            dist < GeomUtils.POINTS_ARE_SAME_ABSOLUTE_ERROR_THRESHOLD):
            dist = vector0[1] - vector1[1]
            if (
                dist > -GeomUtils.POINTS_ARE_SAME_ABSOLUTE_ERROR_THRESHOLD) \
                    and (
                dist < GeomUtils.POINTS_ARE_SAME_ABSOLUTE_ERROR_THRESHOLD):
                dist = vector0[2] - vector1[2]
                if (
                    dist > -GeomUtils.POINTS_ARE_SAME_ABSOLUTE_ERROR_THRESHOLD) and (
                    dist < GeomUtils.POINTS_ARE_SAME_ABSOLUTE_ERROR_THRESHOLD):
                    same = True
        return same

    @staticmethod
    def rotation_and_scale_matrix(space):
        return space.copy().to_3x3()

    @staticmethod
    def rotation_matrix(space):
        return space.copy().to_3x3().normalized()


class VectorUtils:
    PARALLEL_VECTORS_ABSOLUTE_ERROR_THRESHOLD = 1.e-5

    @staticmethod
    def are_parallel(vector0, vector1):
        dir1 = vector0.normalized()
        dir2 = vector1.normalized()
        d = abs(dir1.dot(dir2))
        return MathUtils.almost_equal_absolute(
            d, 1.0, VectorUtils.PARALLEL_VECTORS_ABSOLUTE_ERROR_THRESHOLD)

    @staticmethod
    def same_direction(vector0, vector1):
        return MathUtils.almost_zero(vector0.angle(vector1))

    @staticmethod
    def is_zero(vector, tolerance=MathUtils.ZERO_TOLERANCE):
        return abs(vector[0]) < tolerance and \
            abs(vector[1]) < tolerance and \
            abs(vector[2]) < tolerance


class BBox:
    def __init__(self, min_values: Vector, max_values: Vector):
        self.min = min_values
        self.max = max_values

    def __repr__(self):
        return "<{}({}), min={}, max={}>".format(self.__class__.__name__,
                                                 hex(id(self)), self.min,
                                                 self.max)

    @staticmethod
    def from_face(face):
        min_values = Vector.Fill(3, MathUtils.VECTOR_MAX_FLOAT_VALUE)
        max_values = Vector.Fill(3, MathUtils.VECTOR_MIN_FLOAT_VALUE)

        for v in face.verts:
            co = v.co
            for i, axe_co in enumerate(co):
                min_values[i] = min(min_values[i], axe_co)
                max_values[i] = max(max_values[i], axe_co)
        return BBox(min_values, max_values)

    @staticmethod
    def from_faces(faces):
        min_values = Vector.Fill(3, MathUtils.VECTOR_MAX_FLOAT_VALUE)
        max_values = Vector.Fill(3, MathUtils.VECTOR_MIN_FLOAT_VALUE)
        for face in faces:
            for v in face.verts:
                co = v.co
                for i, axe_co in enumerate(co):
                    min_values[i] = min(min_values[i], axe_co)
                    max_values[i] = max(max_values[i], axe_co)
        return BBox(min_values, max_values)

    def intersect(self, bbox):
        possible_intersection = True
        for axe_index in range(0, 3):
            if self.min[axe_index] > bbox.max[axe_index]:
                possible_intersection = False
                break
            if self.max[axe_index] < bbox.min[axe_index]:
                possible_intersection = False
                break

        return possible_intersection

    def point_inside(self, point):
        point_inside = True
        for axe_index in range(0, 3):
            if point[axe_index] < self.min[axe_index] or \
               point[axe_index] > self.max[axe_index]:
                point_inside = False
                break
        return point_inside

    def face_inside(self, face):
        face_inside = True
        for vert in face.verts:
            if not self.point_inside(vert.co):
                face_inside = False
                break
        return face_inside

    def inside_faces(self, faces):
        inside_faces = []
        for face in faces:
            if self.face_inside(face):
                inside_faces.append(face)
        return inside_faces

    def center(self):
        return (self.min + self.max) * 0.5
