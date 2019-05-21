# Blender EdgeTools
#
# This is a toolkit for edge manipulation based on several of mesh manipulation
# abilities of several CAD/CAE packages, notably CATIA's Geometric Workbench
# from which most of these tools have a functional basis based on the paradims
# that platform enables.  These tools are a collection of scripts that I needed
# at some point, and so I will probably add and improve these as I continue to
# use and model with them.
#
# It might be good to eventually merge the tinyCAD VTX tools for unification
# purposes, and as these are edge-based tools, it would make sense.  Or maybe
# merge this with tinyCAD instead?
#
# The GUI and Blender add-on structure shamelessly coded in imitation of the
# LoopTools addon.
#
# Examples:
#   - "Ortho" inspired from CATIA's line creation tool which creates a line of a
#       user specified length at a user specified angle to a curve at a chosen
#       point.  The user then selects the plane the line is to be created in.
#   - "Shaft" is inspired from CATIA's tool of the same name.  However, instead
#       of a curve around an axis, this will instead shaft a line, a point, or
#       a fixed radius about the selected axis.
#   - "Slice" is from CATIA's ability to split a curve on a plane.  When
#       completed this be a Python equivalent with all the same basic
#       functionality, though it will sadly be a little clumsier to use due
#       to Blender's selection limitations.
#
# Tasks:
#   - Figure out how to do a GUI for "Shaft", especially for controlling radius.
#
# Paul "BrikBot" Marshall
# Created: January 28, 2012
# Last Modified: March 14, 2012
# Homepage (blog): http://post.darkarsenic.com/
#                       //blog.darkarsenic.com/
#
# Coded in IDLE, tested in Blender 2.62.
# Search for "@todo" to quickly find sections that need work.
#
# Remeber -
#   Functional code comes before fast code.  Once it works, then worry about
#   making it faster/more efficient.
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  The Blender Rock Creation tool is for rapid generation of mesh rocks.
#  Copyright (C) 2011  Paul Marshall
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>
# ^^ Maybe. . . . :P

bl_info = {
    'name': "EdgeTools",
    'author': "Paul Marshall",
    'version': (0, 6),
    'blender': (2, 6, 2),
    'location': "View3D > Toolbar and View3D > Specials (W-key)",
    'warning': "",
    'description': "CAD style edge manipulation tools",
    'wiki_url': "http://blenderartists.org/forum/showthread.php?245137-Blender-EdgeTools",
    'tracker_url': "",
    'category': 'Mesh'}

import bpy, bmesh, mathutils
from math import radians
from mathutils import Matrix, Vector
from mathutils.geometry import (distance_point_to_plane,
                                interpolate_bezier,
                                intersect_point_line,
                                intersect_line_line,
                                intersect_line_plane)
from bpy.props import (BoolProperty,
                       BoolVectorProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty)

# Quick an dirty method for getting the sign of a number:
def sign(number):
    return (number > 0) - (number < 0)


# is_parallel
# Checks to see if two lines are parallel
def is_parallel(v1, v2, v3, v4):
    result = intersect_line_line(v1, v2, v3, v4) 
    return result == None


# is_axial
# This is for the special case where the edge is parallel to an axis.  In this
# the projection onto the XY plane will fail so it will have to be handled
# differently.  This tells us if and how:
def is_axial(v1, v2):
    error = 0.000002
    vector = v2 - v1
    # Don't need to store, but is easier to read:
    vec0 = vector[0] > -error and vector[0] < error
    vec1 = vector[1] > -error and vector[1] < error
    vec2 = vector[2] > -error and vector[2] < error
    if (vec0 or vec1) and vec2:
        return 'Z'
    elif vec0 and vec1:
        return 'Y'
    return None


# is_same_co
# For some reason "Vector = Vector" does not seem to look at the actual
# coordinates.  This provides a way to do so.
def is_same_co(v1, v2):
    if len(v1) != len(v2):
        return False
    else:
        for co1, co2 in zip(v1, v2):
            if co1 != co2:
                return False
    return True


# distance_point_line
# I don't know why the mathutils.geometry API does not already have this, but
# it is trivial to code using the structures already in place.  Instead of
# returning a float, I also want to know the direction vector defining the
# distance.
def distance_point_line(pt, line_p1, line_p2):
    int_co = intersect_point_line(pt, line_p1, line_p2)
    distance_vector = int_co[0] - pt
    return distance_vector


# interpolate_line_line
# This is an experiment into a cubic Hermite spline (c-spline) for connecting
# two edges with edges that obey the general equation.
# This will return a set of point coordinates (Vectors).
#
# A good, easy to read background on the mathematics can be found at:
# http://cubic.org/docs/hermite.htm
#
# Right now this is . . . less than functional :P
# @todo
#   - C-Spline and Bezier curves do not end on p2_co as they are supposed to.
#   - B-Spline just fails.  Epically.
#   - Add more methods as I come across them.  Who said flexibility was bad?
def interpolate_line_line(p1_co, p1_dir, p2_co, p2_dir, segments, tension = 1,
                          typ = 'BEZIER', include_ends = False):
    pieces = []
    fraction = 1 / segments
    # Form: p1, tangent 1, p2, tangent 2
    if typ == 'HERMITE':
        poly = [[2, -3, 0, 1], [1, -2, 1, 0],
                [-2, 3, 0, 0], [1, -1, 0, 0]]
    elif typ == 'BEZIER':
        poly = [[-1, 3, -3, 1], [3, -6, 3, 0],
                [1, 0, 0, 0], [-3, 3, 0, 0]]
        p1_dir = p1_dir + p1_co
        p2_dir = -p2_dir + p2_co
    elif typ == 'BSPLINE':
##        Supposed poly matrix for a cubic b-spline:
##        poly = [[-1, 3, -3, 1], [3, -6, 3, 0],
##                [-3, 0, 3, 0], [1, 4, 1, 0]]
        # My own invention to try to get something that somewhat acts right.
        # This is semi-quadratic rather than fully cubic:
        poly = [[0, -1, 0, 1], [1, -2, 1, 0],
                [0, -1, 2, 0], [1, -1, 0, 0]]
    if include_ends:
        pieces.append(p1_co)
    # Generate each point:
    for i in range(segments - 1):
        t = fraction * (i + 1)
        if bpy.app.debug:
            print(t)
        s = [t ** 3, t ** 2, t, 1]
        h00 = (poly[0][0] * s[0]) + (poly[0][1] * s[1]) + (poly[0][2] * s[2]) + (poly[0][3] * s[3])
        h01 = (poly[1][0] * s[0]) + (poly[1][1] * s[1]) + (poly[1][2] * s[2]) + (poly[1][3] * s[3])
        h10 = (poly[2][0] * s[0]) + (poly[2][1] * s[1]) + (poly[2][2] * s[2]) + (poly[2][3] * s[3])
        h11 = (poly[3][0] * s[0]) + (poly[3][1] * s[1]) + (poly[3][2] * s[2]) + (poly[3][3] * s[3])
        pieces.append((h00 * p1_co) + (h01 * p1_dir) + (h10 * p2_co) + (h11 * p2_dir))
    if include_ends:
        pieces.append(p2_co)
    # Return:
    if len(pieces) == 0:
        return None
    else:
        if bpy.app.debug:
            print(pieces)
        return pieces


# Extends an "edge" in two directions:
#   - Requires two vertices to be selected.  They do not have to form an edge.
#   - Extends "length" in both directions
class Extend(bpy.types.Operator):
    bl_idname = "mesh.edgetools_extend"
    bl_label = "Extend"
    bl_description = "Extend the selected edges of vertice pair."
    bl_options = {'REGISTER', 'UNDO'}

    di1 = BoolProperty(name = "Forwards",
                       description = "Extend the edge forwards",
                       default = True)
    di2 = BoolProperty(name = "Backwards",
                       description = "Extend the edge backwards",
                       default = False)
    length = FloatProperty(name = "Length",
                           description = "Length to extend the edge",
                           min = 0.0, max = 1024.0,
                           default = 1.0)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "di1")
        layout.prop(self, "di2")
        layout.prop(self, "length")
    

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return(ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')


    def invoke(self, context, event):
        return self.execute(context)

    
    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        bm = bmesh.new()
        bm.from_mesh(bpy.context.active_object.data)

        bEdges = bm.edges
        bVerts = bm.verts

        edges = []
        verts = []

        for e in bEdges:
            if e.select:
                edges.append(e)

        if len(edges) > 0:
            for e in edges:
                vector = e.verts[0].co - e.verts[1].co
                vector.length = self.length
                
                if self.di1:
                    v = bVerts.new()
                    if (vector[0] + vector[1] + vector[2]) < 0:
                        v.co = e.verts[1].co - vector
                        newE = bEdges.new((e.verts[1], v))
                    else:
                        v.co = e.verts[0].co + vector
                        newE = bEdges.new((e.verts[0], v))
                if self.di2:
                    v = bVerts.new()
                    if (vector[0] + vector[1] + vector[2]) < 0:
                        v.co = e.verts[0].co + vector
                        newE = bEdges.new((e.verts[0], v))
                    else:
                        v.co = e.verts[1].co - vector
                        newE = bEdges.new((e.verts[1], v))
        else:
            for v in bVerts:
                if v.select:
                    verts.append(v)

            vector = verts[0].co - verts[1].co
            vector.length = self.length

            if self.di1:
                v = bVerts.new()
                if (vector[0] + vector[1] + vector[2]) < 0:
                    v.co = verts[1].co - vector
                    e = bEdges.new((verts[1], v))
                else:
                    v.co = verts[0].co + vector
                    e = bEdges.new((verts[0], v))
            if self.di2:
                v = bVerts.new()
                if (vector[0] + vector[1] + vector[2]) < 0:
                    v.co = verts[0].co + vector
                    e = bEdges.new((verts[0], v))
                else:
                    v.co = verts[1].co - vector
                    e = bEdges.new((verts[1], v))

        bm.to_mesh(bpy.context.active_object.data)
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}


# Creates a series of edges between two edges using spline interpolation.
# This basically just exposes existing functionality in addition to some
# other common methods: Hermite (c-spline), Bezier, and b-spline.  These
# alternates I coded myself after some extensive research into spline
# theory.
#
# @todo Figure out what's wrong with the Blender bezier interpolation.
class Spline(bpy.types.Operator):
    bl_idname = "mesh.edgetools_spline"
    bl_label = "Spline"
    bl_description = "Create a spline interplopation between two edges"
    bl_options = {'REGISTER', 'UNDO'}
    
    alg = EnumProperty(name = "Spline Algorithm",
                       items = [('Blender', 'Blender', 'Interpolation provided through \"mathutils.geometry\"'),
                                ('Hermite', 'C-Spline', 'C-spline interpolation'),
                                ('Bezier', 'Bézier', 'Bézier interpolation'),
                                ('B-Spline', 'B-Spline', 'B-Spline interpolation')],
                       default = 'Bezier')
    segments = IntProperty(name = "Segments",
                           description = "Number of segments to use in the interpolation",
                           min = 2, max = 4096,
                           soft_max = 1024,
                           default = 32)
    flip1 = BoolProperty(name = "Flip Edge",
                         description = "Flip the direction of the spline on edge 1",
                         default = False)
    flip2 = BoolProperty(name = "Flip Edge",
                         description = "Flip the direction of the spline on edge 2",
                         default = False)
    ten1 = FloatProperty(name = "Tension",
                         description = "Tension on edge 1",
                         min = 0.0, max = 4096.0,
                         soft_max = 8.0,
                         default = 1.0)
    ten2 = FloatProperty(name = "Tension",
                         description = "Tension on edge 2",
                         min = 0.0, max = 4096.0,
                         soft_max = 8.0,
                         default = 1.0)

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "alg")
        layout.prop(self, "segments")
        layout.label("Edge 1:")
        layout.prop(self, "ten1")
        layout.prop(self, "flip1")
        layout.label("Edge 2:")
        layout.prop(self, "ten2")
        layout.prop(self, "flip2")


    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return(ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')


    def invoke(self, context, event):
        return self.execute(context)

    
    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        bm = bmesh.new()
        bm.from_mesh(bpy.context.active_object.data)

        bEdges = bm.edges
        bVerts = bm.verts
        
        seg = self.segments
        edges = []
        verts = []

        for e in bEdges:
            if e.select:
                edges.append(e)

        for v in range(4):
            verts.append(edges[v // 2].verts[v % 2])

        if self.flip1:
            v1 = verts[1]
            p1_co = verts[1].co
            p1_dir = verts[1].co - verts[0].co
        else:
            v1 = verts[0]
            p1_co = verts[0].co
            p1_dir = verts[0].co - verts[1].co
        p1_dir.length = self.ten1

        if self.flip2:
            v2 = verts[3]
            p2_co = verts[3].co
            p2_dir = verts[2].co - verts[3].co
        else:
            v2 = verts[2]
            p2_co = verts[2].co
            p2_dir = verts[3].co - verts[2].co
        p2_dir.length = self.ten2

        # Get the interploted coordinates:
        if self.alg == 'Blender':
            pieces = interpolate_bezier(p1_co, p1_dir, p2_dir, p2_co, self.segments)
        elif self.alg == 'Hermite':
            pieces = interpolate_line_line(p1_co, p1_dir, p2_co, p2_dir, self.segments, 1, 'HERMITE')
        elif self.alg == 'Bezier':
            pieces = interpolate_line_line(p1_co, p1_dir, p2_co, p2_dir, self.segments, 1, 'BEZIER')
        elif self.alg == 'B-Spline':
            pieces = interpolate_line_line(p1_co, p1_dir, p2_co, p2_dir, self.segments, 1, 'BSPLINE')

        verts = []
        verts.append(v1)
        # Add vertices and set the points:
        for i in range(seg - 1):
            v = bVerts.new()
            v.co = pieces[i]
            verts.append(v)
        verts.append(v2)
        # Connect vertices:
        for i in range(seg):
            e = bEdges.new((verts[i], verts[i + 1]))

        bm.to_mesh(bpy.context.active_object.data)
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}


# Creates edges normal to planes defined between each of two edges and the
# normal or the plane defined by those two edges.
#   - Select two edges.  The must form a plane.
#   - On running the script, eight edges will be created.  Delete the
#     extras that you don't need.
#   - The length of those edges is defined by the variable "length"
#
# @todo Change method from a cross product to a rotation matrix to make the
#   angle part work.
#   --- todo completed Feb 4th, but still needs work ---
# @todo Figure out a way to make +/- predictable
#   - Maybe use angel between edges and vector direction definition?
#   --- TODO COMPLETED ON 2/9/2012 ---
class Ortho(bpy.types.Operator):
    bl_idname = "mesh.edgetools_ortho"
    bl_label = "Angle off Edge"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    vert1 = BoolProperty(name = "Vertice 1",
                         description = "Enable edge creation for vertice 1.",
                         default = True)
    vert2 = BoolProperty(name = "Vertice 2",
                         description = "Enable edge creation for vertice 2.",
                         default = True)
    vert3 = BoolProperty(name = "Vertice 3",
                         description = "Enable edge creation for vertice 3.",
                         default = True)
    vert4 = BoolProperty(name = "Vertice 4",
                         description = "Enable edge creation for vertice 4.",
                         default = True)
    pos = BoolProperty(name = "+",
                       description = "Enable positive direction edges.",
                       default = True)
    neg = BoolProperty(name = "-",
                       description = "Enable negitive direction edges.",
                       default = True)
    angle = FloatProperty(name = "Angle",
                          description = "Angle off of the originating edge",
                          min = 0.0, max = 180.0,
                          default = 90.0)
    length = FloatProperty(name = "Length",
                           description = "Length of created edges.",
                           min = 0.0, max = 1024.0,
                           default = 1.0)

    # For when only one edge is selected (Possible feature to be testd):
    plane = EnumProperty(name = "Plane",
                         items = [("XY", "X-Y Plane", "Use the X-Y plane as the plane of creation"),
                                  ("XZ", "X-Z Plane", "Use the X-Z plane as the plane of creation"),
                                  ("YZ", "Y-Z Plane", "Use the Y-Z plane as the plane of creation")],
                         default = "XY")

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "vert1")
        layout.prop(self, "vert2")
        layout.prop(self, "vert3")
        layout.prop(self, "vert4")
        row = layout.row(align = False)
        row.alignment = 'EXPAND'
        row.prop(self, "pos")
        row.prop(self, "neg")
        layout.prop(self, "angle")
        layout.prop(self, "length")
    
    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return(ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')


    def invoke(self, context, event):
        return self.execute(context)

    
    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        bm = bmesh.new()
        bm.from_mesh(bpy.context.active_object.data)

        bVerts = bm.verts
        bEdges = bm.edges
        edges = []
        vectors = []

        for e in bEdges:
            if e.select:
                edges.append(e)

        # Until I can figure out a better way of handeling it:
        if len(edges) < 2:
            bpy.ops.object.editmode_toggle()
            self.report({'ERROR_INVALID_INPUT'}, "You must select two edges.")
            return {'CANCELLED'}

        verts = [edges[0].verts[0],
                 edges[0].verts[1],
                 edges[1].verts[0],
                 edges[1].verts[1]]

        cos = intersect_line_line(verts[0].co, verts[1].co, verts[2].co, verts[3].co)

        # If the two edges are parallel:
        if cos == None:
            self.report({'WARNING'}, "Selected lines are parallel: results may be unpredictable.")
            vectors.append(verts[0].co - verts[1].co)
            vectors.append(verts[0].co - verts[2].co)
            vectors.append(vectors[0].cross(vectors[1]))
            vectors.append(vectors[2].cross(vectors[0]))
            vectors.append(-vectors[3])
        else:
            # Warn the user if they have not chosen two planar edges:
            if not is_same_co(cos[0], cos[1]):
                self.report({'WARNING'}, "Selected lines are not planar: results may be unpredictable.")

            # This makes the +/- behavior predictable:
            if (verts[0].co - cos[0]).length < (verts[1].co - cos[0]).length:
                verts[0], verts[1] = verts[1], verts[0]
            if (verts[2].co - cos[0]).length < (verts[3].co - cos[0]).length:
                verts[2], verts[3] = verts[3], verts[2]

            vectors.append(verts[0].co - verts[1].co)
            vectors.append(verts[2].co - verts[3].co)
            
            # Normal of the plane formed by vector1 and vector2:
            vectors.append(vectors[0].cross(vectors[1]))

            # Possible directions:
            vectors.append(vectors[2].cross(vectors[0]))
            vectors.append(vectors[1].cross(vectors[2]))

        # Set the length:
        vectors[3].length = self.length
        vectors[4].length = self.length

        # Perform any additional rotations:
        matrix = Matrix.Rotation(radians(90 + self.angle), 3, vectors[2])
        vectors.append(matrix * -vectors[3]) # vectors[5]
        matrix = Matrix.Rotation(radians(90 - self.angle), 3, vectors[2])
        vectors.append(matrix * vectors[4]) # vectors[6]
        vectors.append(matrix * vectors[3]) # vectors[7]
        matrix = Matrix.Rotation(radians(90 + self.angle), 3, vectors[2])
        vectors.append(matrix * -vectors[4]) # vectors[8]

        # Perform extrusions and displacements:
        # There will be a total of 8 extrusions.  One for each vert of each edge.
        # It looks like an extrusion will add the new vert to the end of the verts
        # list and leave the rest in the same location.
        # ----------- EDIT -----------
        # It looks like I might be able to do this with in "bpy.data" with the ".add"
        # function.
        # ------- BMESH UPDATE -------
        # BMesh uses ".new()"

        for v in range(len(verts)):
            vert = verts[v]
            if (v == 0 and self.vert1) or (v == 1 and self.vert2) or (v == 2 and self.vert3) or (v == 3 and self.vert4):
                if self.pos:
                    new = bVerts.new()
                    new.co = vert.co - vectors[5 + (v // 2) + ((v % 2) * 2)]
                    bEdges.new((vert, new))
                if self.neg:
                    new = bVerts.new()
                    new.co = vert.co + vectors[5 + (v // 2) + ((v % 2) * 2)]
                    bEdges.new((vert, new))

        bm.to_mesh(bpy.context.active_object.data)
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}


# Usage:
# Select an edge and a point or an edge and specify the radius (default is 1 BU)
# You can select two edges but it might be unpredicatble which edge it revolves
# around so you might have to play with the switch.
class Shaft(bpy.types.Operator):
    bl_idname = "mesh.edgetools_shaft"
    bl_label = "Shaft"
    bl_description = "Create a shaft mesh around an axis"
    bl_options = {'REGISTER', 'UNDO'}

    shaftType = 0
    edge = IntProperty(name = "Edge",
                       description = "Edge to shaft around.",
                       min = 0, max = 1,
                       default = 0)
    flip = BoolProperty(name = "Flip Second Edge",
                        description = "Flip the percieved direction of the second edge.",
                        default = False)
    radius = FloatProperty(name = "Radius",
                           description = "Shaft Radius",
                           min = 0.0, max = 1024.0,
                           default = 1.0)
    start = FloatProperty(name = "Starting Angle",
                          description = "Angle to start the shaft at.",
                          min = -360.0, max = 360.0,
                          default = 0.0)
    finish = FloatProperty(name = "Ending Angle",
                           description = "Angle to end the shaft at.",
                           min = -360.0, max = 360.0,
                           default = 360.0)
    segments = IntProperty(name = "Shaft Segments",
                           description = "Number of sgements to use in the shaft.",
                           min = 1, max = 4096,
                           soft_max = 512,
                           default = 32)


    def draw(self, context):
        layout = self.layout

        if self.shaftType == 0:
            layout.prop(self, "edge")
            layout.prop(self, "flip")
        elif self.shaftType == 2:
            layout.prop(self, "radius")
        layout.prop(self, "segments")
        layout.prop(self, "start")
        layout.prop(self, "finish")


    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return(ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')


    def invoke(self, context, event):
        return self.execute(context)

    
    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        bm = bmesh.new()
        bm.from_mesh(bpy.context.active_object.data)

        bFaces = bm.faces
        bEdges = bm.edges
        bVerts = bm.verts

        edges = []
        verts = []

        # Pre-caclulated values:
        
        # Selects which edge to use
        if self.edge == 0:
            edge = [0, 1]
        else:
            edge = [1, 0]
        rotRange = [radians(self.start), radians(self.finish)]
        rads = radians((self.finish - self.start) / self.segments)

        numV = self.segments + 1
        numE = self.segments

        for e in bEdges:
            if e.select:
                edges.append(e)
                e.select = False

        verts.append(edges[edge[0]].verts[0])
        verts.append(edges[edge[0]].verts[1])

        if len(edges) > 1:
            if self.flip:
                verts.append(edges[edge[1]].verts[1])
                verts.append(edges[edge[1]].verts[0])
            else:
                verts.append(edges[edge[1]].verts[0])
                verts.append(edges[edge[1]].verts[1])
            self.shaftType = 0
        else:
            for v in bVerts:
                if v.select and verts.count(v) == 0:
                    verts.append(v)
                v.select = False
            if len(verts) == 2:
                self.shaftType = 2
            else:
                self.shaftType = 1

        # The vector denoting the axis of rotation:
        axis = verts[1].co - verts[0].co

        # We will need a series of rotation matrices.  We could use one which would be
        # faster but also might cause propagation of error.
        matrices = []
        for i in range(numV):
            matrices.append(Matrix.Rotation((rads * i) + rotRange[0], 3, axis))

        # New vertice coordinates:
        verts_out = []

        # If two edges were selected:
        #   - If the lines are not parallel, then it will create a cone-like shaft
        if len(edges) > 1:
            for i in range(2):
                init_vec = distance_point_line(verts[i + 2].co, verts[0].co, verts[1].co)
                co = init_vec + verts[i + 2].co
                for j in range(numV):
                    # These will be rotated about the orgin so will need to be shifted:
                    verts_out.append(co - (matrices[j] * init_vec))
        # Else if a line and a point was selected:    
        elif len(verts) == 3:
            init_vec = distance_point_line(verts[2].co, verts[0].co, verts[1].co)
            for i in range(2):
                for j in range(numV):
                    # These will be rotated about the orgin so will need to be shifted:
                    verts_out.append(verts[i].co - (matrices[j] * init_vec))
        # Else the above are not possible, so we will just use the edge:
        #   - The vector defined by the edge is the normal of the plane for the shaft
        #   - The shaft will have radius "radius".
        else:
            if is_axial(verts[0].co, verts[1].co) == None:
                proj = (verts[1].co - verts[0].co)
                proj[2] = 0
                norm = proj.cross(verts[1].co - verts[0].co)
                vec = norm.cross(verts[1].co - verts[0].co)
                vec.length = self.radius
            elif is_axial(verts[0].co, verts[1].co) == 'Z':
                vec = verts[0].co + Vector((0, 0, self.radius))
            else:
                vec = verts[0].co + Vector((0, self.radius, 0))
            init_vec = distance_point_line(vec, verts[0].co, verts[1].co)
            for i in range(2):
                for j in range(numV):
                    # These will be rotated about the orgin so will need to be shifted:
                    verts_out.append(verts[i].co - (matrices[j] * init_vec))

        # We should have the coordinates for a bunch of new verts.  Now add the verts
        # and build the edges and then the faces.

        newVerts = []

        # Vertices:
        for i in range(numV * 2):
            new = bVerts.new()
            new.co = verts_out[i]
            new.select = True
            newVerts.append(new)

        # Edges:
        for i in range(numE):
            e = bEdges.new((newVerts[i], newVerts[i + 1]))
            e.select = True
            e = bEdges.new((newVerts[i + numV], newVerts[i + numV + 1]))
            e.select = True
        for i in range(numV):
            e = bEdges.new((newVerts[i], newVerts[i + numV]))
            e.select = True

        # Faces:
        for i in range(numE):
            f = bFaces.new((newVerts[i], newVerts[i + 1],
                            newVerts[i + numV + 1], newVerts[i + numV]))
            f.normal_update()

        bm.to_mesh(bpy.context.active_object.data)
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}


# "Slices" edges crossing a plane defined by a face.
class Slice(bpy.types.Operator):
    bl_idname = "mesh.edgetools_slice"
    bl_label = "Slice"
    bl_description = "Cuts edges at the plane defined by a selected face."
    bl_options = {'REGISTER', 'UNDO'}

    pos = BoolProperty(name = "Positive",
                       description = "Remove the portion on the side of the face normal",
                       default = False)
    neg = BoolProperty(name = "Negative",
                       description = "Remove the portion on the side opposite of the face normal",
                       default = False)

    def draw(self, context):
        layout = self.layout

        layout.label("Remove Side:")
        layout.prop(self, "pos")
        layout.prop(self, "neg")


    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return(ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')


    def invoke(self, context, event):
        return self.execute(context)

    
    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        bm = bmesh.new()
        bm.from_mesh(context.active_object.data)

        # For easy access to verts, edges, and faces:
        bVerts = bm.verts
        bEdges = bm.edges
        bFaces = bm.faces

        fVerts = []
        normal = None

        # Find the selected face.  This will provide the plane to project onto:
        for f in bFaces:
            if f.select:
                for v in f.verts:
                    fVerts.append(v)
                f.normal_update()
                normal = f.normal
                f.select = False
                break

        for e in bEdges:
            if e.select:
                v1 = e.verts[0]
                v2 = e.verts[1]
                if v1 in fVerts and v2 in fVerts:
                    e.select = False
                    continue
                intersection = intersect_line_plane(v1.co, v2.co, fVerts[0].co, normal)
                if intersection != None:
                    d1 = distance_point_to_plane(v1.co, fVerts[0].co, normal)
                    d2 = distance_point_to_plane(v2.co, fVerts[0].co, normal)
                    # If they have different signs, then the edge crosses the plane:
                    if abs(d1 + d2) < abs(d1 - d2):
                        # Make the first vertice the positive vertice:
                        if d1 < d2:
                            v2, v1 = v1, v2
                        new = list(bmesh.utils.edge_split(e, v1, 0.5))
                        new[1].co = intersection
                        e.select = False
                        new[0].select = False
                        if self.pos:
                            bEdges.remove(new[0])
                        if self.neg:
                            bEdges.remove(e)

        bm.to_mesh(context.active_object.data)
        bpy.ops.object.editmode_toggle()
##        bpy.ops.mesh.remove_doubles()
        return {'FINISHED'}


class Project(bpy.types.Operator):
    bl_idname = "mesh.edgetools_project"
    bl_label = "Project"
    bl_description = "Projects the selected vertices/edges onto the selected plane."
    bl_options = {'REGISTER', 'UNDO'}

    make_copy = BoolProperty(name = "Make Copy",
                             description = "Make a duplicate of the vertices instead of moving it",
                             default = False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "make_copy")

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return(ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')


    def invoke(self, context, event):
        return self.execute(context)


    def execute(self, context):
        bpy.ops.object.editmode_toggle()

        bm = bmesh.new()
        bm.from_mesh(context.active_object.data)

        bFaces = bm.faces
        bEdges = bm.edges
        bVerts = bm.verts

        fVerts = []

        # Find the selected face.  This will provide the plane to project onto:
        for f in bFaces:
            if f.select:
                for v in f.verts:
                    fVerts.append(v)
                f.normal_update()
                normal = f.normal
                f.select = False
                break

        for v in bVerts:
            if v.select:
                if v in fVerts:
                    v.select = False
                    continue
                d = distance_point_to_plane(v.co, fVerts[0].co, normal)
                if self.make_copy:
                    temp = v
                    v = bVerts.new()
                    v.co = temp.co
                vector = normal
                vector.length = abs(d)
                v.co = v.co - (vector * sign(d))
                v.select = False

        bm.to_mesh(context.active_object.data)
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}


# Project_End is for projecting/extending an edge to meet a plane.
# This is used be selecting a face to define the plane then all the edges.
# The add-on will then move the vertices in the edge that is closest to the
# plane to the coordinates of the intersection of the edge and the plane.
class Project_End(bpy.types.Operator):
    bl_idname = "mesh.edgetools_project_end"
    bl_label = "Project (End Point)"
    bl_description = "Projects the vertice of the selected edges closest to a plane onto that plane."
    bl_options = {'REGISTER', 'UNDO'}

    make_copy = BoolProperty(name = "Make Copy",
                             description = "Make a duplicate of the vertice instead of moving it",
                             default = False)
    use_force = BoolProperty(name = "Use opposite vertices",
                             description = "Force the usage of the other end of the vertices",
                             default = False)
    use_normal = BoolProperty(name = "Project along mormal",
                              description = "Use the plane's normal as the projection direction",
                              default = False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "use_normal")
        layout.prop(self, "make_copy")
        layout.prop(self, "use_force")


    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return(ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')


    def invoke(self, context, event):
        return self.execute(context)


    def execute(self, context):
        bpy.ops.object.editmode_toggle()

        bm = bmesh.new()
        bm.from_mesh(context.active_object.data)

        bFaces = bm.faces
        bEdges = bm.edges
        bVerts = bm.verts

        fVerts = []

        # Find the selected face.  This will provide the plane to project onto:
        for f in bFaces:
            if f.select:
                for v in f.verts:
                    fVerts.append(v)
                f.normal_update()
                normal = f.normal
                f.select = False
                break

        for e in bEdges:
            if e.select:
                v1 = e.verts[0]
                v2 = e.verts[1]
                if v1 in fVerts or v2 in fVerts:
                    e.select = False
                    continue
                intersection = intersect_line_plane(v1.co, v2.co, fVerts[0].co, normal)
                if intersection != None:
                    print("Made it this far: intersection != None")
                    # Use abs because we don't care what side of plane we're on:
                    d1 = distance_point_to_plane(v1.co, fVerts[0].co, normal)
                    d2 = distance_point_to_plane(v2.co, fVerts[0].co, normal)
                    # If d1 is closer than we use v1 as our vertice:
                    # "xor" with 'use_force':
                    if (abs(d1) < abs(d2)) is not self.use_force:
                        print("Made it this far: (abs(d1) < abs(d2)) xor force")
                        if self.make_copy:
                            v1 = bVerts.new()
                            v1.co = e.verts[0].co
                        if self.use_normal:
                            vector = normal
                            vector.length = abs(d1)
                            v1.co = v1.co - (vector * sign(d1))
                        else:
                            print("New coordinate", end = ": ")
                            print(intersection)
                            v1.co = intersection
                    else:
                        if self.make_copy:
                            v2 = bVerts.new()
                            v2.co = e.verts[1].co
                        if self.use_normal:
                            vector = normal
                            vector.length = abs(d2)
                            v2.co = v2.co - (vector * sign(d2))
                        else:
                            v2.co = intersection
                e.select = False

        bm.to_mesh(context.active_object.data)
        bpy.ops.object.editmode_toggle()
        return {'FINISHED'}


class VIEW3D_MT_edit_mesh_edgetools(bpy.types.Menu):
    bl_label = "EdgeTools"
    
    def draw(self, context):
        layout = self.layout
        
        layout.operator("mesh.edgetools_extend")
        layout.operator("mesh.edgetools_spline")
        layout.operator("mesh.edgetools_ortho")
        layout.operator("mesh.edgetools_shaft")
        layout.operator("mesh.edgetools_slice")
        layout.operator("mesh.edgetools_project")
        layout.operator("mesh.edgetools_project_end")


def menu_func(self, context):
    self.layout.menu("VIEW3D_MT_edit_mesh_edgetools")
    self.layout.separator()


# define classes for registration
classes = [VIEW3D_MT_edit_mesh_edgetools,
    Extend,
    Spline,
    Ortho,
    Shaft,
    Slice,
    Project,
    Project_End]


# registering and menu integration
def register():
    if int(bpy.app.build_revision[0:5]) < 44800:
        print("Error in Edgetools:")
        print("This version of Blender does not support the necessary BMesh API.")
        print("Please download a newer build at http://www.graphicall.org")
        return {'ERROR'}
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.VIEW3D_MT_edit_mesh_specials.prepend(menu_func)


# unregistering and removing menus
def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_func)


if __name__ == "__main__":
    register()
    
