from math import pi
from sys import float_info
from collections import namedtuple

import bmesh
import bpy
from mathutils import Vector
from mathutils.geometry import (intersect_point_line,
                                distance_point_to_plane,
                                intersect_line_plane,
                                tessellate_polygon,
                                normal,
                                intersect_ray_tri)
from enum import Enum, IntEnum, unique
from . woodwork_math_utils import MathUtils
from . woodwork_geom_utils import (GeomUtils,
                                   VectorUtils,
                                   BBox,
                                   Position)

#TODO : handle mortise with 0 length shoulder (sort of inverted max)
# Used to retrieve faces when geometry has been deleted and faces reordered
@unique
class ReferenceGeometry(IntEnum):
    firstHeightShoulder = 1
    secondHeightShoulder = 2
    firstThicknessShoulder = 3
    secondThicknessShoulder = 4
    extruded = 5
    tenonHaunchAdjacentFace = 6
    edgeToRaise = 7
    haunchAdjacentEdge = 8
    tenonFace = 9
    tenonAdjacentFaces = 100


# Use bmesh layers to retrieve faces
class GeometryRetriever:
    def __init__(self):
        self.bm = None
        self.face_retriever = None
        self.edge_retriever = None

    def create(self, bm):
        self.bm = bm
        self.face_retriever = bm.faces.layers.int.new("face_retriever")
        self.edge_retriever = bm.edges.layers.int.new("edge_retriever")

    def save_face(self, face, reference_geometry):
        face[self.face_retriever] = int(reference_geometry)

    def retrieve_face(self, reference_geometry, remove_ref=True):
        found = None
        for f in self.bm.faces:
            if f[self.face_retriever] == int(reference_geometry):
                found = f
                if remove_ref:
                    f[self.face_retriever] = 0
                break
        return found

    def save_faces(self, faces, reference_geometry_start):
        for idx, face in enumerate(faces):
            face[self.face_retriever] = int(reference_geometry_start) + idx

    def retrieve_faces(self, reference_geometry_start,
                             max_count):
        found_faces = dict()
        min_int = int(reference_geometry_start)
        max_int = min_int + max_count
        for f in self.bm.faces:
            val = f[self.face_retriever]
            if int(reference_geometry_start) <= val < max_int:
                found_faces[val - min_int] = f
                f[self.face_retriever] = 0
        result_list = []
        for key in sorted(found_faces):
            result_list.append(found_faces[key])
        return result_list

    def save_edge(self, edge, reference_geometry):
        edge[self.edge_retriever] = int(reference_geometry)

    def retrieve_edge(self, reference_geometry, remove_ref=True):
        found = None
        for e in self.bm.edges:
            if e[self.edge_retriever] == int(reference_geometry):
                found = e
                if remove_ref:
                    e[self.edge_retriever] = 0
                break
        return found

    def destroy(self):
        self.bm.faces.layers.int.remove(self.face_retriever)
        self.bm.edges.layers.int.remove(self.edge_retriever)


# TODO: merge thickness and height into a TenonMortiseBuilderSideProperties or something like that
class TenonMortiseBuilderThickness:
    def __init__(self):
        self.haunch_first_side = TenonMortiseBuilderHaunch()
        self.haunch_second_side = TenonMortiseBuilderHaunch()


class TenonMortiseBuilderHaunch:
    pass


class TenonMortiseBuilderHeight:
    def __init__(self):
        self.haunch_first_side = TenonMortiseBuilderHaunch()
        self.haunch_second_side = TenonMortiseBuilderHaunch()


class TenonMortiseBuilderProps:
    def __init__(self):
        self.height_properties = TenonMortiseBuilderHeight()
        self.thickness_properties = TenonMortiseBuilderThickness()


# This describes the initial face where the tenon will be created
class FaceToBeTransformed:
    def __init__(self, face):
        self.face = face

        self.median = None
        self.normal = None
        self.longest_side_tangent = None
        self.shortest_side_tangent = None
        self.longest_edges = None
        self.shortest_edges = None
        self.shortest_length = None
        self.longest_length = None

    def extract_features(self, matrix_world):
        face = self.face

        self.median = face.calc_center_median()
        self.normal = face.normal.copy()

        # Get largest and smallest edge to find resize axes
        l0 = face.loops[0]
        e0 = l0.edge
        l1 = face.loops[1]
        e1 = l1.edge

        v0 = matrix_world * e0.verts[0].co
        v1 = matrix_world * e0.verts[1].co
        length0 = (v0 - v1).length
        v0 = matrix_world * e1.verts[0].co
        v1 = matrix_world * e1.verts[1].co
        length1 = (v0 - v1).length

        if length0 > length1:
            self.longest_side_tangent = e0.calc_tangent(l0)
            self.shortest_side_tangent = e1.calc_tangent(l1)
            self.longest_edges = [e0, face.loops[2].edge]
            self.shortest_edges = [e1, face.loops[3].edge]
            self.shortest_length = length1
            self.longest_length = length0
        else:
            self.longest_side_tangent = e1.calc_tangent(l1)
            self.shortest_side_tangent = e0.calc_tangent(l0)
            self.longest_edges = [e1, face.loops[3].edge]
            self.shortest_edges = [e0, face.loops[2].edge]
            self.shortest_length = length0
            self.longest_length = length1

    # Subdivide given edges and return created faces
    @staticmethod
    def __subdivide_edges(bm, edges_to_subdivide, cuts=2):
        ret = bmesh.ops.subdivide_edges(
            bm,
            edges=edges_to_subdivide,
            cuts=cuts,
            use_grid_fill=True)

        # Get the new faces

        # Can't rely on Faces as certain faces are not tagged when only two
        # edges are subdivided
        # see  source / blender / bmesh / operators / bmo_subdivide.c
        new_edges = [bmesh_type
                     for bmesh_type in ret["geom_inner"]
                     if type(bmesh_type) is bmesh.types.BMEdge]
        del ret
        subdivided_faces = set()
        for new_edge in new_edges:
            for linked_face in new_edge.link_faces:
                subdivided_faces.add(linked_face)
        return subdivided_faces

    # Subdivide face to be transformed to a tenon
    def subdivide_face(self, bm, height_properties, thickness_properties):
        edges_to_subdivide = []

        max_height_centered = bool(
            height_properties.type == "max" and
            height_properties.centered is True)
        max_thickness_centered = bool(
            thickness_properties.type == "max" and
            thickness_properties.centered is True)

        if max_height_centered:
            # if tenon height set to maximum, select shortest side edges
            # to subdivide only in this direction
            for edge in self.shortest_edges:
                edges_to_subdivide.append(edge)

        elif max_thickness_centered:
            # if tenon thickness set to maximum, select longest side edges
            # to subdivide only in this direction
            for edge in self.longest_edges:
                edges_to_subdivide.append(edge)

        else:
            edges_to_subdivide = self.face.edges

        return FaceToBeTransformed.__subdivide_edges(bm, edges_to_subdivide)

    # Used by "remove wood" tenon option
    def translate_along_normal(self, bm, matrix_world, depth):
        rot_mat = GeomUtils.rotation_matrix(matrix_world)
        normal_world = rot_mat * self.face.normal
        normal_world = normal_world * depth

        bmesh.ops.translate(bm,
                            verts=self.face.verts,
                            vec=normal_world,
                            space=matrix_world)


# This structure keep info about the newly created tenon face
class TenonFace:
    def __init__(self, face):
        self.face = face
        self.thickness_faces = []
        self.height_faces = []

    # find tenon adjacent faces to be translated or resized given user's values
    # - height_faces[] are the faces which follows the direction of the
    # longest side
    # - thickness_faces[] are the faces which follows the direction of the
    # shortest side
    def find_adjacent_faces(self,
                            face_to_be_transformed,
                            height_properties,
                            thickness_properties):
        tenon = self.face

        self.thickness_faces.append(tenon)
        self.height_faces.append(tenon)

        longest_side_tangent = face_to_be_transformed.longest_side_tangent

        max_height_centered = bool(
            height_properties.type == "max" and
            height_properties.centered is True)
        max_thickness_centered = bool(
            thickness_properties.type == "max" and
            thickness_properties.centered is True)

        # Find faces to resize to obtain tenon base
        for tenon_edge in tenon.edges:
            connected_faces = tenon_edge.link_faces
            for connected_face in connected_faces:
                if connected_face != tenon:
                    # Face adjacent to tenon
                    connected_loops = tenon_edge.link_loops
                    for connected_loop in connected_loops:
                        if connected_loop.face == connected_face:

                            tangent = tenon_edge.calc_tangent(connected_loop)

                            if VectorUtils.are_parallel(tangent,
                                                        longest_side_tangent):
                                # faces to set height
                                if not max_thickness_centered:
                                    self.height_faces.append(connected_face)

                            else:
                                # faces to set thickness
                                if not max_height_centered:
                                    self.thickness_faces.append(connected_face)

    def get_vector_to_be_resized(self, resize_direction):
        vector_to_be_resized = None
        tenon = self.face
        nearest_angle = 2 * pi
        for loop in tenon.loops:
            edge = loop.edge
            tangent = edge.calc_tangent(loop)
            angle = tangent.angle(resize_direction)
            if MathUtils.almost_equal_relative_or_absolute(angle, pi/2) or \
                    MathUtils.almost_equal_relative_or_absolute(angle, 1.5 * pi):
                pt1 = edge.verts[1]
                pt0 = edge.verts[0]

                vector_to_be_resized = pt1.co - pt0.co
                break
            else:
                if abs(angle - (pi / 2.0)) < nearest_angle or \
                        abs(angle - (1.5 * pi)) < nearest_angle:
                    if abs(angle - (pi / 2.0)) < nearest_angle:
                        nearest_angle = abs(angle - (pi / 2.0))
                    else:
                        nearest_angle = abs(angle - (1.5 * pi))
                    nearest_edge = edge

        if vector_to_be_resized is None:
            # very small vector (shoulder is on tenon end)
            pt1 = nearest_edge.verts[1]
            pt0 = nearest_edge.verts[0]
            vector_to_be_resized = pt1.co - pt0.co
        return vector_to_be_resized

    @staticmethod
    def get_scale_factor(vector_to_be_resized, matrix_world, resize_value):
        rotate_scale_world = GeomUtils.rotation_and_scale_matrix(matrix_world)
        world_vector = rotate_scale_world * vector_to_be_resized

        if VectorUtils.is_zero(world_vector):
            scale_factor = resize_value
        else:
            scale_factor = resize_value / world_vector.length

        return scale_factor

    @staticmethod
    def compute_translation_vector(local_vector_to_be_resized,
                                   direction,
                                   scale_factor,
                                   matrix_world,
                                   shoulder_beyond_tenon):
        rotate_scale_world = GeomUtils.rotation_and_scale_matrix(matrix_world)
        vector_to_be_resized = rotate_scale_world * local_vector_to_be_resized

        if VectorUtils.is_zero(vector_to_be_resized):
            world_direction = rotate_scale_world * direction
            translate_vector = world_direction.normalized() * scale_factor
        else:
            same_direction = VectorUtils.same_direction(local_vector_to_be_resized,
                                                        direction)
            if shoulder_beyond_tenon:
                # shoulder size is larger than actual tenon end
                if same_direction:
                    vector_to_be_resized.negate()
                vector_to_be_resized_inverted = vector_to_be_resized.copy()
                vector_to_be_resized_inverted.negate()

                final_vector = vector_to_be_resized_inverted * scale_factor

                translate_vector = final_vector + vector_to_be_resized_inverted
            else:
                if not same_direction:
                    vector_to_be_resized.negate()
                final_vector = vector_to_be_resized * scale_factor

                translate_vector = final_vector - vector_to_be_resized

        return translate_vector

    @staticmethod
    def find_verts_to_translate(tenon_faces, shoulder_verts):
        tenon_verts = set()
        for face in tenon_faces:
            verts = face.verts
            for vert in verts:
                tenon_verts.add(vert)

        return tenon_verts.difference(shoulder_verts)


# This describes a shoulder adjacent to the tenon face
class ShoulderFace:
    def __init__(self, has_neighbor_faces):
        self.face = None
        self.vector_to_be_resized = None
        self.has_neighbor_faces = has_neighbor_faces

    # gets the shoulder : it's a face in tenon_adjacent_faces that is not
    # the tenon itself
    def get_from_tenon(self,
                       tenon,
                       tenon_adjacent_faces,
                       shoulder_direction):
        tenon_face = tenon.face
        tenon_edges = set(tenon_face.edges)
        for face in tenon_adjacent_faces:
            if face != tenon_face:
                # Find joint edge between face and tenon face and look for a
                # match with wanted direction
                common_edges = tenon_edges.intersection(face.edges)
                common_edge = common_edges.pop()
                loops = common_edge.link_loops
                tenon_loop = next(
                    loop for loop in loops if loop.face is tenon_face)
                direction = common_edge.calc_tangent(tenon_loop)
                if VectorUtils.same_direction(direction, shoulder_direction):
                    self.face = face
                    break

    # Find verts used to size the shoulder on the given side : those are the
    # verts in common between tenon faces (on the middle of the subdivision)
    # and shoulder faces (on one border)
    def find_verts_to_translate(self,
                                up_down_direction,
                                tenon_faces):

        tenon_verts = set()
        for face in tenon_faces:
            verts = face.verts
            for vert in verts:
                tenon_verts.add(vert)

        # find shoulder faces to scale
        shoulder_face = self.face
        shoulder_faces = [shoulder_face]

        if self.has_neighbor_faces:
            for edge in shoulder_face.edges:
                connected_faces = edge.link_faces

                for connected_face in connected_faces:
                    if connected_face != shoulder_face:
                        connected_loops = edge.link_loops

                        shoulder_loop = next(loop for loop in connected_loops if
                                             loop.face is shoulder_face)
                        tangent = edge.calc_tangent(shoulder_loop)

                        if VectorUtils.are_parallel(tangent,
                                                    up_down_direction):
                            shoulder_faces.append(connected_face)

                            if self.vector_to_be_resized is None:
                                pt1 = edge.verts[1]
                                pt0 = edge.verts[0]
                                if pt1 in tenon_verts:
                                    self.vector_to_be_resized = pt1.co - pt0.co
                                else:
                                    self.vector_to_be_resized = pt0.co - pt1.co

        # when height or thickness set to the max and tenon is centered,
        # this could happen...
        if self.vector_to_be_resized is None:
            l0 = shoulder_face.loops[0]
            e0 = l0.edge
            l1 = shoulder_face.loops[1]
            e1 = l1.edge

            tangent0 = e0.calc_tangent(l0)

            if VectorUtils.are_parallel(tangent0, up_down_direction):
                edge_to_resize = e0
            else:
                edge_to_resize = e1
            pt1 = edge_to_resize.verts[1]
            pt0 = edge_to_resize.verts[0]
            if pt1 in tenon_verts:
                self.vector_to_be_resized = pt1.co - pt0.co
            else:
                self.vector_to_be_resized = pt0.co - pt1.co

        # find vertices to move
        shoulder_verts = set()
        for face in shoulder_faces:
            verts = face.verts
            for vert in verts:
                shoulder_verts.add(vert)

        return shoulder_verts.intersection(tenon_verts)

    def compute_translation_vector(self, shoulder_value, matrix_world):
        rotate_scale_world = GeomUtils.rotation_and_scale_matrix(matrix_world)
        edge_vector = rotate_scale_world * self.vector_to_be_resized
        shoulder_length_to_resize = edge_vector.length
        scale_factor = shoulder_value / shoulder_length_to_resize
        final_vector = edge_vector * scale_factor
        return final_vector - edge_vector


class ThroughMortiseIntersection:

    def __init__(self, bm, top_face):
        self.bm = bm
        self.top_face = top_face

    def __find_possible_intersection_triangles(self,
                                               intersect_faces,
                                               intersect_faces_bbox,
                                               face_to_be_transformed,
                                               not_intersecting_faces):
        tri_faces = []
        TriFace = namedtuple('TriFace', 'orig_face, v0, v1, v2, normal')
        for face in self.bm.faces:
            if not (face in intersect_faces or
                    face is self.top_face or
                    face in not_intersecting_faces):
                possible_intersection = False
                # Check possible intersection with boundary boxes
                for intersect_face_bbox in intersect_faces_bbox:
                    face_bbox = BBox.from_face(face)
                    if intersect_face_bbox.intersect(face_bbox):
                        possible_intersection = True
                        break

                # Check if face is behind reference face
                if possible_intersection:
                    face_position = GeomUtils.face_position(
                        face,
                        face_to_be_transformed.median,
                        face_to_be_transformed.normal)
                    if face_position is Position.in_front or \
                            face_position is Position.on_plane:
                        possible_intersection = False

                if possible_intersection:
                    if len(face.verts) > 3:
                        co_list = [vert.co for vert in face.verts]
                        tris = tessellate_polygon((co_list,))
                        for tri in tris:
                            v0 = co_list[tri[0]]
                            v1 = co_list[tri[1]]
                            v2 = co_list[tri[2]]
                            tri_normal = normal(v0, v1, v2)

                            tri_face = TriFace(face,
                                               v0=v0,
                                               v1=v1,
                                               v2=v2,
                                               normal=tri_normal)
                            tri_faces.append(tri_face)
                    else:
                        verts = face.verts
                        v0 = verts[0].co
                        v1 = verts[1].co
                        v2 = verts[2].co
                        tri_face = TriFace(face,
                                           v0=v0,
                                           v1=v1,
                                           v2=v2,
                                           normal=face.normal)
                        tri_faces.append(tri_face)
        return tri_faces

    @staticmethod
    def __find_intersection_points(intersect_edges, tri_faces):
        IntersectionPt = namedtuple('IntersectionPt',
                                    'intersection_pt, tri, edge')
        intersection_pts = []
        for edge in intersect_edges:
            for tri in tri_faces:
                v1 = edge.verts[0].co
                v2 = edge.verts[1].co
                ray = v2 - v1
                intersection_pt = intersect_ray_tri(tri.v0,
                                                    tri.v1,
                                                    tri.v2,
                                                    ray,
                                                    v1)
                if intersection_pt is not None:
                    intersection = IntersectionPt(intersection_pt, tri, edge)
                    intersection_pts.append(intersection)
        return intersection_pts

    # faces are connected (they form a box) when at least two edges are
    # connected with the others
    @staticmethod
    def __faces_are_box_connected(faces):
        connected = True
        if len(faces) > 4:
            connected = False
        elif len(faces) > 1:
            for face in faces:
                linked_count = 0
                for edge in face.edges:
                    linked_faces = edge.link_faces
                    for linked_face in linked_faces:
                        if linked_face is not face:
                            if linked_face in faces:
                                linked_count += 1
                if linked_count < 2:
                    connected = False
                    break

        return connected

    @staticmethod
    def __outer_edge_loop(faces):
        outer_edges = set()
        for face in faces:
            for edge in face.edges:
                link_faces = edge.link_faces
                for link_face in link_faces:
                    if not link_face in faces:
                        outer_edges.add(edge)
        return outer_edges

    def __translate_top_face_to_intersection(self, intersection_pts):
        for intersection in intersection_pts:
            intersection_pt = intersection.intersection_pt
            edge = intersection.edge
            vert = edge.verts[0]
            if not self.top_face in vert.link_faces:
                vert = edge.verts[1]
            translation_vector = intersection_pt - vert.co
            bmesh.ops.translate(self.bm, vec=translation_vector, verts=[vert])

    def __create_hole(self, intersection_pts):
        # remove intersected faces
        faces_to_delete = set()
        for intersection in intersection_pts:
            tri = intersection.tri
            faces_to_delete.add(tri.orig_face)

        # find external loop in faces to be deleted
        if not ThroughMortiseIntersection.__faces_are_box_connected(
                faces_to_delete):
            # There are faces in between intersected faces
            # Compute bounding box and select faces inside
            faces_to_delete_bbox = BBox.from_faces(faces_to_delete)
            inside_faces = faces_to_delete_bbox.inside_faces(self.bm.faces)
            faces_to_delete.update(inside_faces)

        edges_to_fill = ThroughMortiseIntersection.__outer_edge_loop(
            faces_to_delete)

        # delete top face too (now it's a hole)
        faces_to_delete.add(self.top_face)
        for edge in self.top_face.edges:
            edges_to_fill.add(edge)

        delete_faces = 5
        bmesh.ops.delete(self.bm,
                         geom=list(faces_to_delete),
                         context=delete_faces)
        bmesh.ops.bridge_loops(self.bm, edges=list(edges_to_fill))
        #TODO: do a clean-up / limited dissolve

    # Calculate edge intersection with opposite face
    # Used for through mortise
    def create_hole_in_opposite_faces(self,
                                      face_to_be_transformed,
                                      not_intersecting_faces):
        # Get face perpendicular edges
        top_face_normal = self.top_face.normal
        intersect_edges = []
        intersect_faces = set()
        for vert in self.top_face.verts:
            for edge in vert.link_edges:
                edge_vect = edge.verts[0].co - edge.verts[1].co
                if VectorUtils.are_parallel(edge_vect, top_face_normal):
                    intersect_edges.append(edge)
                    edge_faces = edge.link_faces
                    for edge_face in edge_faces:
                        intersect_faces.add(edge_face)

        # Compute bounding box for faces
        intersect_faces_bbox = []
        for face in intersect_faces:
            bbox = BBox.from_face(face)
            intersect_faces_bbox.append(bbox)

        # Map each original face index to one or more triangle if needed
        tri_faces = self.__find_possible_intersection_triangles(
            intersect_faces,
            intersect_faces_bbox,
            face_to_be_transformed,
            not_intersecting_faces)

        # Try to intersect with triangles
        intersection_pts = \
            ThroughMortiseIntersection.__find_intersection_points(
                intersect_edges,
                tri_faces)

        intersections_count = len(intersection_pts)
        if intersections_count == 4:
            self.__translate_top_face_to_intersection(intersection_pts)
            self.__create_hole(intersection_pts)

        elif intersections_count > 4:
            print("Too many intersections for through mortise")


class ShouldersOnOneSide:
    def __init__(self,
                 first_shoulder: ShoulderFace,
                 second_shoulder: ShoulderFace):
        self.first_shoulder = first_shoulder
        self.second_shoulder = second_shoulder


# Data about mesh being processed
class MeshObjectData:
    def __init__(self, bm, matrix_world):
        self.bm = bm
        self.matrix_world = matrix_world


# Set height and thickness on shoulders and tenon/mortise
class HeightAndThicknessSetup:
    def __init__(self, geometry_retriever):
        self.geometry_retriever = geometry_retriever

        self.height_shoulders = None
        self.thickness_shoulders = None

        self.height_shoulder_resize_settings = None
        self.thickness_shoulder_resize_settings = None

    # resize centered faces
    @staticmethod
    def __resize_faces(bm, faces, direction, scale_factor):
        verts_to_translate_side_neg = set()
        verts_to_translate_side_pos = set()
        translate_vector_pos = None
        translate_vector_neg = None
        for faceToResize in faces:
            for edge in faceToResize.edges:
                v0 = edge.verts[0]
                v1 = edge.verts[1]
                edge_vector = v1.co - v0.co
                if VectorUtils.are_parallel(edge_vector, direction):

                    center = (v1.co + v0.co) * 0.5
                    signed_distance = distance_point_to_plane(v0.co, center,
                                                              direction)
                    if signed_distance < 0.0:
                        verts_to_translate_side_neg.add(v0)
                        verts_to_translate_side_pos.add(v1)
                    else:
                        verts_to_translate_side_pos.add(v0)
                        verts_to_translate_side_neg.add(v1)

                    if translate_vector_pos is None:
                        if signed_distance < 0.0:
                            vector_to_translate_neg = v0.co - center
                            vector_to_translate_pos = v1.co - center
                        else:
                            vector_to_translate_neg = v1.co - center
                            vector_to_translate_pos = v0.co - center
                        final_vector_neg = vector_to_translate_neg * \
                            scale_factor
                        final_vector_pos = vector_to_translate_pos * \
                            scale_factor
                        translate_vector_neg = final_vector_neg - \
                            vector_to_translate_neg
                        translate_vector_pos = final_vector_pos - \
                            vector_to_translate_pos

        bmesh.ops.translate(
            bm,
            vec=translate_vector_pos,
            verts=list(verts_to_translate_side_pos))
        bmesh.ops.translate(
            bm,
            vec=translate_vector_neg,
            verts=list(verts_to_translate_side_neg))

    @staticmethod
    def __get_shoulder_faces_on_given_side(tenon: TenonFace,
                                           tenon_faces_on_side,
                                           has_neighbor_faces,
                                           first_shoulder_side):

        first_shoulder = ShoulderFace(has_neighbor_faces)
        first_shoulder.get_from_tenon(
            tenon,
            tenon_faces_on_side,
            first_shoulder_side)

        second_shoulder_side = first_shoulder_side.copy()
        second_shoulder_side.negate()

        second_shoulder = ShoulderFace(has_neighbor_faces)
        second_shoulder.get_from_tenon(
            tenon,
            tenon_faces_on_side,
            second_shoulder_side)

        return ShouldersOnOneSide(first_shoulder, second_shoulder)

    @staticmethod
    def __set_shoulder_size_on_given_side(mesh_object_data: MeshObjectData,
                                          shoulders: ShouldersOnOneSide,
                                          reversed,
                                          tenon_faces_on_perpendicular_side,
                                          origin_face_tangent,
                                          shoulder_value):

        if reversed:
            shoulder_to_resize = shoulders.second_shoulder
        else:
            shoulder_to_resize = shoulders.first_shoulder

        shoulder_verts_to_translate = \
            shoulder_to_resize.find_verts_to_translate(
                origin_face_tangent,
                tenon_faces_on_perpendicular_side)

        translate_vector = shoulder_to_resize.compute_translation_vector(
            shoulder_value,
            mesh_object_data.matrix_world)

        bmesh.ops.translate(
            mesh_object_data.bm,
            vec=translate_vector,
            space=mesh_object_data.matrix_world,
            verts=list(shoulder_verts_to_translate))

        return shoulder_to_resize, shoulder_verts_to_translate

    def __set_shoulder_size(self,
                            mesh_object_data: MeshObjectData,
                            tenon: TenonFace,
                            face_to_be_transformed,
                            height_properties,
                            thickness_properties):

        max_height_centered = bool(
            height_properties.type == "max" and
            height_properties.centered is True)
        max_thickness_centered = bool(
            thickness_properties.type == "max" and
            thickness_properties.centered is True)

        if not height_properties.centered:
            self.height_shoulders = \
                HeightAndThicknessSetup.__get_shoulder_faces_on_given_side(
                    tenon,
                    tenon.thickness_faces,
                    not max_thickness_centered,
                    face_to_be_transformed.shortest_side_tangent)

            # Set tenon shoulder on height side
            self.height_shoulder_resize_settings = \
                HeightAndThicknessSetup.__set_shoulder_size_on_given_side(
                    mesh_object_data,
                    self.height_shoulders,
                    height_properties.reverse_shoulder,
                    tenon.height_faces,
                    face_to_be_transformed.longest_side_tangent,
                    height_properties.shoulder_value)

        if not thickness_properties.centered:
            self.thickness_shoulders = \
                HeightAndThicknessSetup.__get_shoulder_faces_on_given_side(
                    tenon,
                    tenon.height_faces,
                    not max_height_centered,
                    face_to_be_transformed.longest_side_tangent)

            # Set tenon shoulder on width side
            self.thickness_shoulder_resize_settings = \
                HeightAndThicknessSetup.__set_shoulder_size_on_given_side(
                    mesh_object_data,
                    self.thickness_shoulders,
                    thickness_properties.reverse_shoulder,
                    tenon.thickness_faces,
                    face_to_be_transformed.shortest_side_tangent,
                    thickness_properties.shoulder_value)

    def __set_tenon_or_mortise_size_on_given_side(
            self,
            mesh_object_data: MeshObjectData,
            faces_to_resize,
            direction,
            max,
            centered,
            size,
            shoulder_resize_settings,
            tenon: TenonFace):

        if not (max and centered):
            vector_to_be_resized = tenon.get_vector_to_be_resized(direction)
            scale_factor = TenonFace.get_scale_factor(
                vector_to_be_resized,
                mesh_object_data.matrix_world,
                size)

            if centered:
                # centered
                HeightAndThicknessSetup.__resize_faces(
                    mesh_object_data.bm,
                    faces_to_resize,
                    direction,
                    scale_factor)
            else:
                # shouldered
                shoulder, shoulder_verts_to_translate = shoulder_resize_settings

                verts_to_translate = TenonFace.find_verts_to_translate(
                    faces_to_resize,
                    shoulder_verts_to_translate)

                shoulder_normal = shoulder.face.normal
                tenon_normal = tenon.face.normal
                if VectorUtils.same_direction(shoulder_normal, tenon_normal):
                    shoulder_beyond_tenon = False
                else:
                    shoulder_beyond_tenon = True

                translate_vector = \
                    TenonFace.compute_translation_vector(
                        vector_to_be_resized,
                        shoulder.vector_to_be_resized,
                        scale_factor,
                        mesh_object_data.matrix_world,
                        shoulder_beyond_tenon)

                bmesh.ops.translate(mesh_object_data.bm,
                                    vec=translate_vector,
                                    space=mesh_object_data.matrix_world,
                                    verts=list(verts_to_translate))

                # if shouldered and tenon size set to the max, delete
                # shoulder on the other side. This operation re-order faces ids
                # (tenon and adjacent faces on given side).
                if max:
                    merge_threshold = \
                        GeomUtils.POINTS_ARE_NEAR_ABSOLUTE_ERROR_THRESHOLD
                    bmesh.ops.automerge(mesh_object_data.bm,
                                        verts=list(verts_to_translate),
                                        dist=merge_threshold)

    def __set_tenon_or_mortise_size(self,
                                    mesh_object_data: MeshObjectData,
                                    tenon: TenonFace,
                                    face_to_be_transformed,
                                    height_properties,
                                    thickness_properties):
        # Set tenon thickness
        max = thickness_properties.type == "max"
        centered = thickness_properties.centered
        if not centered and not max:
            shoulder_and_tenon_length = thickness_properties.shoulder_value + \
                thickness_properties.value
            if MathUtils.almost_equal_relative_or_absolute(
                    shoulder_and_tenon_length,
                    face_to_be_transformed.shortest_length
            ):
                max = True
        if max and not centered:
            size = face_to_be_transformed.shortest_length - \
                thickness_properties.shoulder_value
        else:
            size = thickness_properties.value

        if max:
            self.geometry_retriever.save_faces(
                tenon.height_faces,
                ReferenceGeometry.tenonAdjacentFaces
            )
            if not height_properties.centered:
                shoulder, shoulder_verts_to_translate = self.height_shoulder_resize_settings
                self.geometry_retriever.save_face(
                    shoulder.face,
                    ReferenceGeometry.firstHeightShoulder
                )
        self.__set_tenon_or_mortise_size_on_given_side(
            mesh_object_data,
            tenon.thickness_faces,
            face_to_be_transformed.longest_side_tangent,
            max,
            centered,
            size,
            self.thickness_shoulder_resize_settings,
            tenon
        )
        if max:
            tenon.height_faces = self.geometry_retriever.retrieve_faces(
                ReferenceGeometry.tenonAdjacentFaces, 3)
            tenon.face = tenon.height_faces[0]
            if not height_properties.centered:
                shoulder.face = self.geometry_retriever.retrieve_face(
                    ReferenceGeometry.firstHeightShoulder
                )

        # Set tenon height
        max = height_properties.type == "max"
        centered = height_properties.centered
        if not centered and not max:
            shoulder_and_tenon_length = height_properties.shoulder_value + \
                height_properties.value
            if MathUtils.almost_equal_relative_or_absolute(
                    shoulder_and_tenon_length,
                    face_to_be_transformed.longest_length
            ):
                max = True
        if max and not centered:
            size = face_to_be_transformed.longest_length - \
                height_properties.shoulder_value
        else:
            size = height_properties.value

        if max:
            self.geometry_retriever.save_face(
                tenon.face,
                ReferenceGeometry.tenonFace
            )
        self.__set_tenon_or_mortise_size_on_given_side(
            mesh_object_data,
            tenon.height_faces,
            face_to_be_transformed.shortest_side_tangent,
            max,
            centered,
            size,
            self.height_shoulder_resize_settings,
            tenon
        )
        if max:
            tenon.face = self.geometry_retriever.retrieve_face(
                ReferenceGeometry.tenonFace)

    def set_size(self,
                 mesh_object_data: MeshObjectData,
                 tenon: TenonFace,
                 face_to_be_transformed,
                 height_properties,
                 thickness_properties):

        # Find faces to be resized
        tenon.find_adjacent_faces(face_to_be_transformed,
                                  height_properties,
                                  thickness_properties)

        # Set shoulder size on one side
        self.__set_shoulder_size(mesh_object_data,
                                 tenon,
                                 face_to_be_transformed,
                                 height_properties,
                                 thickness_properties)

        # Set tenon height and thickness
        self.__set_tenon_or_mortise_size(mesh_object_data,
                                         tenon,
                                         face_to_be_transformed,
                                         height_properties,
                                         thickness_properties)


class DepthSetup:
    def __init__(self, geometry_retriever, builder_properties):
        self.geometry_retriever = geometry_retriever
        self.builder_properties = builder_properties

    def set_depth(self,
                  mesh_object_data: MeshObjectData,
                  tenon: TenonFace,
                  face_to_be_transformed: FaceToBeTransformed,
                  height_shoulders: ShouldersOnOneSide,
                  thickness_shoulders: ShouldersOnOneSide):
        is_haunched = False
        builder_properties = self.builder_properties
        height_properties = builder_properties.height_properties
        thickness_properties = builder_properties.thickness_properties
        if not height_properties.centered and (
                height_properties.haunched_first_side or
                height_properties.haunched_second_side):
            is_haunched = True
        if not thickness_properties.centered and (
                thickness_properties.haunched_first_side or
                thickness_properties.haunched_second_side):
            is_haunched = True
        if is_haunched:
            self.__raise_haunched_tenon(mesh_object_data,
                                        tenon,
                                        face_to_be_transformed,
                                        height_shoulders,
                                        thickness_shoulders)
        else:
            self.__raise_simple_tenon(mesh_object_data,
                                      tenon,
                                      face_to_be_transformed)

    # Extrude and fatten to set face length
    @staticmethod
    def __set_face_depth(mesh_object_data: MeshObjectData,
                         face,
                         depth):
        ret = bmesh.ops.extrude_discrete_faces(mesh_object_data.bm,
                                               faces=[face])

        extruded_face = ret['faces'][0]
        del ret

        # apply rotation to the normal
        matrix_world = mesh_object_data.matrix_world
        rot_mat = GeomUtils.rotation_matrix(matrix_world)
        normal_world = rot_mat * extruded_face.normal
        normal_world = normal_world * depth

        bmesh.ops.translate(mesh_object_data.bm,
                            vec=normal_world,
                            space=matrix_world,
                            verts=extruded_face.verts)

        return extruded_face

    # Extrude and translate an edge of the face to set it sloped
    def __set_face_sloped(self,
                          mesh_object_data: MeshObjectData,
                          face_to_extrude,
                          depth,
                          still_edge_tangent):

        bm = mesh_object_data.bm
        matrix_world = mesh_object_data.matrix_world

        face_normal = face_to_extrude.normal

        # Extrude face
        ret = bmesh.ops.extrude_discrete_faces(bm, faces=[face_to_extrude])
        extruded_face = ret['faces'][0]
        del ret

        # apply rotation to the normal
        rot_mat = GeomUtils.rotation_matrix(matrix_world)
        normal_world = rot_mat * face_normal
        normal_world = normal_world * depth

        # Delete created face on still edge
        for loop in extruded_face.loops:
            edge = loop.edge
            tangent = edge.calc_tangent(loop)
            angle = tangent.angle(still_edge_tangent)
            if MathUtils.almost_zero(angle):
                still_edge = edge
            elif MathUtils.almost_equal_relative_or_absolute(angle, pi):
                edge_to_raise = edge

        for face in still_edge.link_faces:
            if face is not extruded_face:
                face_to_remove = face
                break

        # remove only face and bottom edge (because there's no face bellow
        # due tu extrude discrete faces)
        self.geometry_retriever.save_face(extruded_face,
                                          ReferenceGeometry.extruded)
        self.geometry_retriever.save_edge(edge_to_raise,
                                          ReferenceGeometry.edgeToRaise)

        delete_faces = 5
        bmesh.ops.delete(bm, geom=[face_to_remove], context=delete_faces)

        extruded_face = self.geometry_retriever.retrieve_face(
            ReferenceGeometry.extruded, remove_ref=False)

        # collapse remaining edges on the sides
        edges_to_collapse = []
        for loop in extruded_face.loops:
            edge = loop.edge
            tangent = edge.calc_tangent(loop)
            if VectorUtils.same_direction(tangent, still_edge_tangent):
                # find edge not in extruded_face
                for vert in edge.verts:
                    link_edges = vert.link_edges
                    for link_edge in link_edges:
                        if not link_edge is edge:
                            has_linked_extruded_face = False
                            link_faces = link_edge.link_faces
                            for f in link_faces:
                                if f is extruded_face:
                                    has_linked_extruded_face = True
                            if not has_linked_extruded_face:
                                edges_to_collapse.append(link_edge)

        for edge in edges_to_collapse:
            verts = edge.verts
            merge_co = verts[0].co
            bmesh.ops.pointmerge(bm, verts=verts, merge_co=merge_co)

        extruded_face = self.geometry_retriever.retrieve_face(
            ReferenceGeometry.extruded)
        edge_to_raise = self.geometry_retriever.retrieve_edge(
            ReferenceGeometry.edgeToRaise)

        # Translate edge up
        bmesh.ops.translate(bm,
                            vec=normal_world,
                            space=matrix_world,
                            verts=edge_to_raise.verts)

        return extruded_face

    # Find tenon face adjacent to haunch
    def __find__tenon_haunch_adjacent_face(self,
                                           side_tangent,
                                           tenon_top):
        builder_properties = self.builder_properties
        is_mortise = builder_properties.depth_value < 0.0

        adjacent_face = None

        for edge in tenon_top.edges:
            for face in edge.link_faces:
                if face != tenon_top:
                    normal = face.normal.copy()
                    if is_mortise:
                        normal.negate()
                    angle = side_tangent.angle(normal)
                    if MathUtils.almost_equal_relative_or_absolute(angle, pi):
                        adjacent_face = face
                        break
            if adjacent_face is not None:
                break
        return adjacent_face

    # Find vertices in haunch touching tenon face
    @staticmethod
    def __find_haunch_adjacent_edge(adjacent_face, haunch_top):
        adjacent_edge = None
        best_dist = float_info.max
        for edge in haunch_top.edges:
            # find edge in plane adjacent_face
            median = (edge.verts[0].co + edge.verts[1].co) * 0.5

            dist = distance_point_to_plane(median, adjacent_face.verts[0].co,
                                           adjacent_face.normal)

            if abs(dist) < best_dist:
                adjacent_edge = edge
                best_dist = abs(dist)

        return adjacent_edge

    @staticmethod
    def __find_linked_faces_by_opposite_direction(face_to_be_transformed,
                                                  reference_face,
                                                  direction):
        perpendicular_direction = direction.cross(
            face_to_be_transformed.normal)
        found = []
        for edge in reference_face.edges:
            for face in edge.link_faces:
                if face != reference_face:
                    if VectorUtils.are_parallel(perpendicular_direction,
                                                face.normal):
                        found.append(face)
                        break
        return found

    # clean tenon : remove face adjacent to the haunch (visible with mortise)
    def __beautify_haunched_tenon(self,
                                  bm,
                                  face_to_be_transformed,
                                  tenon_top,
                                  haunch_top,
                                  side_tangent,
                                  dissolve_faces):

        # 1. Find tenon face adjacent to haunch
        adjacent_face = self.__find__tenon_haunch_adjacent_face(
            side_tangent, tenon_top)
        geometry_retriever_type = ReferenceGeometry.tenonHaunchAdjacentFace
        self.geometry_retriever.save_face(adjacent_face,
                                          geometry_retriever_type)

        # 2. Find vertices in haunch touching tenon face
        adjacent_edge = DepthSetup.__find_haunch_adjacent_edge(
            adjacent_face,
            haunch_top)
        self.geometry_retriever.save_edge(adjacent_edge,
                                          ReferenceGeometry.haunchAdjacentEdge)

        # 3. Split tenon edges at vertices
        connections = []

        for vert in adjacent_edge.verts:

            nearest_edge = None
            best_distance = float_info.max
            for edge in adjacent_face.edges:
                # find nearest edge
                dist = GeomUtils.distance_point_edge(vert.co, edge)
                if dist < best_distance:
                    nearest_edge = edge
                    best_distance = dist
            connection = dict()
            connection['haunch_vert'] = vert
            connection['tenon_edge'] = nearest_edge
            connections.append(connection)

        for connection in connections:
            tenon_edge = connection['tenon_edge']
            edge_start = tenon_edge.verts[0]
            edge_end = tenon_edge.verts[1]
            haunch_vert = connection['haunch_vert']
            ret = intersect_point_line(haunch_vert.co, edge_start.co,
                                       edge_end.co)
            dist_in_percentage = ret[1]
            ret = bmesh.utils.edge_split(tenon_edge, edge_start,
                                         dist_in_percentage)
            connection['new_vert'] = ret[1]
            del ret

        # 4. Merge created vertices from split edge with those of haunch top
        # face
        verts_to_merge = []
        for connection in connections:
            new_vert = connection['new_vert']
            verts_to_merge.append(new_vert)

        merge_threshold = GeomUtils.POINTS_ARE_NEAR_ABSOLUTE_ERROR_THRESHOLD
        bmesh.ops.automerge(bm,
                            verts=verts_to_merge,
                            dist=merge_threshold)

        # Geometry has changed from now on so all old references may be wrong
        #  (adjacent_edge, adjacent_face ...)
        adjacent_face = self.geometry_retriever.retrieve_face(
            ReferenceGeometry.tenonHaunchAdjacentFace)
        adjacent_edge = self.geometry_retriever.retrieve_edge(
            ReferenceGeometry.haunchAdjacentEdge)

        # 5. Remove face connecting haunch and tenon
        geom_to_delete = []
        for face in adjacent_edge.link_faces:
            if not face is haunch_top:
                geom_to_delete.append(face)

        delete_only_faces = 3
        bmesh.ops.delete(bm, geom=geom_to_delete, context=delete_only_faces)

        # 6. Remove old tenon face and unneeded edge below haunch
        delete_faces = 5
        bmesh.ops.delete(bm, geom=[adjacent_face], context=delete_faces)

        # 7. Rebuild tenon face using new vertices
        face_vertices = [adjacent_edge.verts[0], adjacent_edge.verts[1]]
        for edge in tenon_top.edges:
            for loop in edge.link_loops:
                if loop.face == tenon_top:
                    tangent = edge.calc_tangent(loop)
                    if VectorUtils.same_direction(tangent, side_tangent):
                        face_vertices.append(edge.verts[0])
                        face_vertices.append(edge.verts[1])
                        break
            if len(face_vertices) > 2:
                break

        bm.faces.new(face_vertices, tenon_top)

        # 9. Dissolve faces on tenon sides
        if dissolve_faces:
            faces_to_dissolve = \
                DepthSetup.__find_linked_faces_by_opposite_direction(
                    face_to_be_transformed, tenon_top, side_tangent)
            faces_to_dissolve.extend(
                DepthSetup.__find_linked_faces_by_opposite_direction(
                    face_to_be_transformed, haunch_top, side_tangent))
            bmesh.ops.dissolve_faces(bm, faces=faces_to_dissolve)

    # Find hole face
    @staticmethod
    def __find_external_face(top, side_tangent):
        hole_face = None
        for edge in top.edges:
            #TODO: is_convex don't tell if normals are inside !! Should compare with another normal
            if not edge.is_convex:
                # deal only with faces with normals inside
                for face in edge.link_faces:
                    if face is not top:
                        if VectorUtils.same_direction(side_tangent, face.normal):
                            hole_face = face
                            break
                if hole_face is not None:
                    break
        return hole_face

    @staticmethod
    def __make_hole_on_side_face(bm,
                                 face_to_be_transformed,
                                 top_face,
                                 side_tangent):
        # This is the face to transform to an hole
        hole_face = DepthSetup.__find_external_face(
            top_face, side_tangent)

        # Get top edge
        top_edge_to_dissolve = None
        nearest_dist = float_info.max
        for edge in hole_face.edges:
            v0 = edge.verts[0]
            v1 = edge.verts[1]
            center = (v1.co + v0.co) * 0.5
            distance = GeomUtils.distance_point_to_plane(
                center,
                face_to_be_transformed.median,
                face_to_be_transformed.normal)

            if abs(distance) < nearest_dist:
                top_edge_to_dissolve = edge
                nearest_dist = abs(distance)

        # keep adjacent face flat projecting bottom edge on it
        linked_faces = top_edge_to_dissolve.link_faces
        if len(linked_faces) == 2:
            adjacent_face = None
            for face in linked_faces:
                if face is not hole_face:
                    adjacent_face = face
                    break

            plane_co = adjacent_face.verts[0].co
            adjacent_normal = adjacent_face.normal

            could_intersect = True
            for loop in top_face.loops:
                edge = loop.edge
                tangent = edge.calc_tangent(loop)
                if not VectorUtils.are_parallel(tangent, side_tangent):
                    v0 = loop.vert
                    v1 = loop.link_loop_next.vert

                    intersection_pt = intersect_line_plane(v0.co, v1.co,
                                                           plane_co,
                                                           adjacent_normal)
                    if intersection_pt is None:
                        could_intersect = False
                        break

                    v0_distance = abs(distance_point_to_plane(v0.co, plane_co,
                                                              adjacent_normal))
                    v1_distance = abs(distance_point_to_plane(v1.co, plane_co,
                                                              adjacent_normal))
                    if v0_distance < v1_distance:
                        origin_pt = v0
                    else:
                        origin_pt = v1
                    translate_vec = intersection_pt - origin_pt.co

                    if not GeomUtils.points_are_same(intersection_pt,
                                                     origin_pt.co):
                        bmesh.ops.translate(bm,
                                            verts=[origin_pt],
                                            vec=translate_vec)
            # dissolve top edge
            if could_intersect:
                bmesh.ops.dissolve_edges(bm, edges=[top_edge_to_dissolve])

    def __raise_haunched_tenon_side(self,
                                    mesh_object_data: MeshObjectData,
                                    face_to_be_transformed,
                                    tenon_top,
                                    side_tangent,
                                    shoulder: ShoulderFace,
                                    haunch_properties,
                                    dissolve_faces):

        if haunch_properties.angle == "sloped":
            haunch_top = self.__set_face_sloped(
                mesh_object_data,
                shoulder.face,
                haunch_properties.depth_value,
                side_tangent)
        else:
            haunch_top = DepthSetup.__set_face_depth(
                mesh_object_data,
                shoulder.face,
                haunch_properties.depth_value,)

            if haunch_properties.depth_value < 0.0:
                DepthSetup.__make_hole_on_side_face(
                    mesh_object_data.bm,
                    face_to_be_transformed,
                    haunch_top,
                    side_tangent)

        self.__beautify_haunched_tenon(mesh_object_data.bm,
                                       face_to_be_transformed,
                                       tenon_top,
                                       haunch_top, side_tangent,
                                       dissolve_faces)

        return haunch_top

    # Raise tenon haunches
    def __raise_haunches(self,
                         mesh_object_data: MeshObjectData,
                         face_to_be_transformed,
                         tenon_top,
                         shoulders: ShouldersOnOneSide,
                         side_tangent,
                         properties,
                         dissolve_faces):

        haunches_faces = []
        # First shoulder
        if properties.haunched_first_side:
            haunch_properties = properties.haunch_first_side
            haunch_top = self.__raise_haunched_tenon_side(
                mesh_object_data,
                face_to_be_transformed,
                tenon_top,
                side_tangent,
                shoulders.first_shoulder,
                haunch_properties,
                dissolve_faces)
            haunches_faces.append(haunch_top)

        # Second shoulder
        if properties.haunched_second_side:
            side_tangent.negate()
            haunch_properties = properties.haunch_second_side
            haunch_top = self.__raise_haunched_tenon_side(
                mesh_object_data,
                face_to_be_transformed,
                tenon_top,
                side_tangent,
                shoulders.second_shoulder,
                haunch_properties,
                dissolve_faces)
            haunches_faces.append(haunch_top)

        return haunches_faces

    # Raise a haunched tenon
    def __raise_haunched_tenon(self,
                               mesh_object_data: MeshObjectData,
                               tenon,
                               face_to_be_transformed,
                               height_shoulders: ShouldersOnOneSide,
                               thickness_shoulders: ShouldersOnOneSide):
        builder_properties = self.builder_properties
        height_properties = builder_properties.height_properties
        thickness_properties = builder_properties.thickness_properties

        # save some faces
        if height_properties.haunched_first_side:
            self.geometry_retriever.save_face(
                height_shoulders.first_shoulder.face,
                ReferenceGeometry.firstHeightShoulder)
        if height_properties.haunched_second_side:
            self.geometry_retriever.save_face(
                height_shoulders.second_shoulder.face,
                ReferenceGeometry.secondHeightShoulder)
        if thickness_properties.haunched_first_side:
            self.geometry_retriever.save_face(
                thickness_shoulders.first_shoulder.face,
                ReferenceGeometry.firstThicknessShoulder)
        if thickness_properties.haunched_second_side:
            self.geometry_retriever.save_face(
                thickness_shoulders.second_shoulder.face,
                ReferenceGeometry.secondThicknessShoulder)

        tenon_top = DepthSetup.__set_face_depth(
            mesh_object_data,
            tenon.face,
            builder_properties.depth_value)

        # extrude used by __set_face_depth could reorder faces (destructive op)
        # so retrieve saved faces
        if height_properties.haunched_first_side:
            height_shoulders.first_shoulder.face = \
                self.geometry_retriever.retrieve_face(
                    ReferenceGeometry.firstHeightShoulder)
        if height_properties.haunched_second_side:
            height_shoulders.second_shoulder.face = \
                self.geometry_retriever.retrieve_face(
                    ReferenceGeometry.secondHeightShoulder)
        if thickness_properties.haunched_first_side:
            thickness_shoulders.first_shoulder.face = \
                self.geometry_retriever.retrieve_face(
                    ReferenceGeometry.firstThicknessShoulder)
        if thickness_properties.haunched_second_side:
            thickness_shoulders.second_shoulder.face = \
                self.geometry_retriever.retrieve_face(
                    ReferenceGeometry.secondThicknessShoulder)

        if height_properties.haunched_first_side or \
                height_properties.haunched_second_side:
            height_has_haunch = True
        else:
            height_has_haunch = False
        if thickness_properties.haunched_first_side or \
                thickness_properties.haunched_second_side:
            thickness_has_haunch = True
        else:
            thickness_has_haunch = False
        if height_has_haunch and thickness_has_haunch:
            dissolve_faces = False
        else:
            dissolve_faces = True

        side_tangent = face_to_be_transformed.shortest_side_tangent.copy()
        haunches_faces = self.__raise_haunches(mesh_object_data,
                                               face_to_be_transformed,
                                               tenon_top,
                                               height_shoulders,
                                               side_tangent,
                                               height_properties,
                                               dissolve_faces)

        side_tangent = face_to_be_transformed.longest_side_tangent.copy()
        haunches_faces.extend(self.__raise_haunches(mesh_object_data,
                                                    face_to_be_transformed,
                                                    tenon_top,
                                                    thickness_shoulders,
                                                    side_tangent,
                                                    thickness_properties,
                                                    dissolve_faces))

        if builder_properties.depth_value < 0.0:
            through_mortise_hole_builder = ThroughMortiseIntersection(
                mesh_object_data.bm,
                tenon_top)
            through_mortise_hole_builder.create_hole_in_opposite_faces(
                face_to_be_transformed,
                haunches_faces)
        else:
            bpy.ops.mesh.select_all(action="DESELECT")
            tenon_top.select = True

    # Raise a not haunched tenon
    def __raise_simple_tenon(self,
                             mesh_object_data: MeshObjectData,
                             tenon: TenonFace,
                             face_to_be_transformed):
        builder_properties = self.builder_properties
        height_properties = builder_properties.height_properties
        thickness_properties = builder_properties.thickness_properties

        tenon_top = DepthSetup.__set_face_depth(
            mesh_object_data,
            tenon.face,
            builder_properties.depth_value)

        if builder_properties.depth_value < 0.0:
            through_mortise_hole_builder = ThroughMortiseIntersection(
                mesh_object_data.bm,
                tenon_top)
            through_mortise_hole_builder.create_hole_in_opposite_faces(
                face_to_be_transformed, [])

            max = thickness_properties.type == "max"
            centered = thickness_properties.centered

            if not centered and not max:
                shoulder_and_tenon_length = thickness_properties.shoulder_value + \
                    thickness_properties.value
                if MathUtils.almost_equal_relative_or_absolute(
                        shoulder_and_tenon_length,
                        face_to_be_transformed.shortest_length
                ):
                    max = True

            if max:
                side_tangent = \
                    face_to_be_transformed.longest_side_tangent.copy()

                if centered:
                    # make hole on both sides
                    DepthSetup.__make_hole_on_side_face(
                        mesh_object_data.bm,
                        face_to_be_transformed,
                        tenon_top,
                        side_tangent)

                    side_tangent.negate()

                    DepthSetup.__make_hole_on_side_face(
                        mesh_object_data.bm,
                        face_to_be_transformed,
                        tenon_top,
                        side_tangent)
                else:
                    # make hole on tenon side
                    if not thickness_properties.reverse_shoulder:
                        side_tangent.negate()

                    DepthSetup.__make_hole_on_side_face(
                        mesh_object_data.bm,
                        face_to_be_transformed,
                        tenon_top,
                        side_tangent)

            max = height_properties.type == "max"
            centered = height_properties.centered

            if not centered and not max:
                shoulder_and_tenon_length = height_properties.shoulder_value + \
                    height_properties.value
                if MathUtils.almost_equal_relative_or_absolute(
                        shoulder_and_tenon_length,
                        face_to_be_transformed.longest_length
                ):
                    max = True

            if max:
                side_tangent = \
                    face_to_be_transformed.shortest_side_tangent.copy()
                if centered:
                    # make hole on both sides
                    DepthSetup.__make_hole_on_side_face(
                        mesh_object_data.bm,
                        face_to_be_transformed,
                        tenon_top,
                        side_tangent)

                    side_tangent.negate()

                    DepthSetup.__make_hole_on_side_face(
                        mesh_object_data.bm,
                        face_to_be_transformed,
                        tenon_top,
                        side_tangent)
                else:
                    # make hole on tenon side
                    if not height_properties.reverse_shoulder:
                        side_tangent.negate()

                    DepthSetup.__make_hole_on_side_face(
                        mesh_object_data.bm,
                        face_to_be_transformed,
                        tenon_top,
                        side_tangent)
        else:
            bpy.ops.mesh.select_all(action="DESELECT")
            tenon_top.select = True


# Build a tenon or a mortise on a face
class TenonMortiseBuilder:
    def __init__(self, builder_properties):
        self.builder_properties = builder_properties
        self.geometry_retriever = GeometryRetriever()
        self.height_and_thickness_setup = HeightAndThicknessSetup(
            self.geometry_retriever)
        self.depth_setup = DepthSetup(self.geometry_retriever,
                                      builder_properties)

    def create(self, bm, matrix_world, face_to_be_transformed):

        mesh_object_data = MeshObjectData(bm, matrix_world)

        builder_properties = self.builder_properties
        thickness_properties = builder_properties.thickness_properties
        height_properties = builder_properties.height_properties

        # Create layers to retrieve geometry when data are deleted (this will
        # reorder face so face_to_be_transformed is not valid anymore ...)
        for face in bm.faces:
            face.tag = False
        for edge in bm.edges:
            edge.tag = False
        face_to_be_transformed.face.tag = True
        self.geometry_retriever.create(bm)
        tagged_faces = [f for f in bm.faces if f.tag]
        face_to_be_transformed.face = tagged_faces[0]
        face_to_be_transformed.face.tag = False
        face_to_be_transformed.extract_features(matrix_world)

        if builder_properties.depth_value > 0:
            if builder_properties.remove_wood:
                face_to_be_transformed.translate_along_normal(
                    bm,
                    matrix_world,
                    -builder_properties.depth_value)

        # Subdivide face
        subdivided_faces = face_to_be_transformed.subdivide_face(
            bm,
            height_properties,
            thickness_properties)

        # Find tenon face (face containing median center)
        if len(subdivided_faces) == 0:
            # when max height centered and max thickness centered
            # (stupid choice but should handle this case too...)
            tenon = TenonFace(face_to_be_transformed.face)

        for f in subdivided_faces:
            if bmesh.geometry.intersect_face_point(
                    f,
                    face_to_be_transformed.median):
                tenon = TenonFace(f)
                break

        # Set shoulder and tenon height and thickness
        self.height_and_thickness_setup.set_size(mesh_object_data,
                                                 tenon,
                                                 face_to_be_transformed,
                                                 height_properties,
                                                 thickness_properties)

        # Raise tenon / dig mortise
        self.depth_setup.set_depth(mesh_object_data,
                                   tenon,
                                   face_to_be_transformed,
                                   self.height_and_thickness_setup.height_shoulders,
                                   self.height_and_thickness_setup.thickness_shoulders)

        self.geometry_retriever.destroy()
