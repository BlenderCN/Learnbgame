"""
Name:    hul_out
Purpose: Exports hull collision files.

Description:


"""

if "bpy" in locals():
    import imp
    imp.reload(common)
    imp.reload(rvstruct)

import bpy
import bmesh
import mathutils

from . import common
from . import rvstruct
from . import prm_in

from .rvstruct import Hull
from .common import *
from mathutils import Color, Vector


def get_plane(x, y, z):
    vector1 = [x[1] - x[0], y[1] - y[0], z[1] - z[0]]
    vector2 = [x[2] - x[0], y[2] - y[0], z[2] - z[0]]

    normal = vector1.cross(vector2)

    distance = - (normal[0] * x[0] + normal[1] * y[0] + normal[2] * z[0])


def export_hull(filepath, scene):

    objs = [obj for obj in scene.objects if obj.revolt.is_hull_convex]

    hull = rvstruct.Hull()
    hull.chull_count = len(objs)

    # Creates convex hulls

    for obj in objs:

        chull = rvstruct.ConvexHull()
    
        bm = bmesh.new()
        bm.from_mesh(obj.data)

        # Applies rotation and scale
        apply_trs(obj, bm, transform=False)

        for face in bm.faces:

            plane = rvstruct.Plane()

            normal = rvstruct.Vector(data=to_revolt_axis(face.normal))
            normal.normalize()

            vec = rvstruct.Vector(data=to_revolt_coord(face.verts[0].co))
            distance = -normal.dot(vec)

            plane.normal = normal
            plane.distance = distance

            chull.faces.append(plane)
            chull.face_count += 1

        # Many custom hulls don't have data for vertices and edges but we'll do it anyway!
        ind = 0
        for edge in bm.edges:
            rvedge = rvstruct.Edge()
            for vert in edge.verts:
                rvvert = rvstruct.Vector(data=to_revolt_coord(vert.co))
                
                # Checks if a vertex with the same coordinate already exists
                existing_vertex = None
                for rvv in chull.vertices:
                    if rvv.data == rvvert.data:
                        existing_vertex = rvv

                # Appends the index of the existing vertex
                if existing_vertex:
                    rvedge.vertices.append(chull.vertices.index(existing_vertex))
                
                # Appends the new vertex, indices
                else:
                    chull.vertices.append(rvvert)
                    rvedge.vertices.append(ind)
                    ind += 1
            chull.edges.append(rvedge)

        chull.vertex_count = len(chull.vertices)
        chull.edge_count = len(chull.edges)

        # Defines bounding box
        bbox = rvstruct.BoundingBox(data=rvbbox_from_verts(bm.verts))

        chull.bbox_offset = rvstruct.Vector(data=(
                (bbox.xlo + bbox.xhi) / 2,
                (bbox.ylo + bbox.yhi) / 2,
                (bbox.zlo + bbox.zhi) / 2
            )
        ) 

        bbox.xlo -= chull.bbox_offset[0]
        bbox.xhi -= chull.bbox_offset[0]
        bbox.ylo -= chull.bbox_offset[1]
        bbox.yhi -= chull.bbox_offset[1]
        bbox.zlo -= chull.bbox_offset[2]
        bbox.zhi -= chull.bbox_offset[2]

        chull.bbox = bbox

        bm.free()
        
        hull.chulls.append(chull)

    # Creates interior

    objs = [obj for obj in scene.objects if obj.revolt.is_hull_sphere]
    hull.interior.sphere_count = len(objs)

    for obj in objs:
        sphere = rvstruct.Sphere()

        sphere.center = rvstruct.Vector(data=to_revolt_coord(obj.location))
        sphere.radius = to_revolt_scale(sum(list(obj.scale))/3)

        hull.interior.spheres.append(sphere)

    with open(filepath, "wb") as f:
        hull.write(f)



def export_file(filepath, scene):
    return export_hull(filepath, scene)
