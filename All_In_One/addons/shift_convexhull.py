# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, Python File Format Interface
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the Python File Format Interface
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****


####------------------------------------------------------------------------------------------------------------------------------------------------------
#### HEADER
####------------------------------------------------------------------------------------------------------------------------------------------------------

bl_info = {
    "name"              : "SHIFT - Convex Hull",
    "author"            : "BBC",
    "version"           : (1,0),
    "blender"           : (2, 5, 3),
    "api"               : 31236,
    "category"          : "Object",
    "location"          : "Tool Shelf",
    "warning"           : '',
    "wiki_url"          : "",
    "tracker_url"       : "",
    "description"       : "Create convex hull"}


import bpy
import time
import operator
import mathutils

from math       import *
from bpy.props  import *

def vecDotProduct(vec1, vec2):
    """The vector dot product (any dimension).

    >>> vecDotProduct((1,2,3),(4,-5,6))
    12"""
    return sum(x1 * x2 for x1, x2 in zip (vec1, vec2))

def vecSub(vec1, vec2):
    """Vector substraction."""    
    return tuple(x - y for x, y in zip (vec1, vec2))

def vecDistance(vec1, vec2):
    """Return distance between two vectors (any dimension).

    >>> vecDistance((1,2,3),(4,-5,6)) # doctest: +ELLIPSIS
    8.185...
    """
    return vecNorm(vecSub(vec1, vec2))

def vecNorm(vec):
    """Norm of a vector (any dimension).

    >>> vecNorm((2,3,4)) # doctest: +ELLIPSIS
    5.3851648...
    """
    return vecDotProduct(vec, vec) ** 0.5

def vecCrossProduct(vec1, vec2):
    """The vector cross product (in 3d).

    >>> vecCrossProduct((1,0,0),(0,1,0))
    (0, 0, 1)
    >>> vecCrossProduct((1,2,3),(4,5,6))
    (-3, 6, -3)
    """
    return (vec1[1] * vec2[2] - vec1[2] * vec2[1],
            vec1[2] * vec2[0] - vec1[0] * vec2[2],
            vec1[0] * vec2[1] - vec1[1] * vec2[0])

def vecNormal(vec1, vec2, vec3):
    """Returns a vector that is orthogonal on C{triangle}."""
    return vecCrossProduct(vecSub(vec2, vec1), vecSub(vec3, vec1))

def vecDistanceAxis(axis, vec):
    """Return distance between the axis spanned by axis[0] and axis[1] and the
    vector v, in 3 dimensions. Raises ZeroDivisionError if the axis points
    coincide.

    >>> vecDistanceAxis([(0,0,0), (0,0,1)], (0,3.5,0))
    3.5
    >>> vecDistanceAxis([(0,0,0), (1,1,1)], (0,1,0.5)) # doctest: +ELLIPSIS
    0.70710678...
    """
    return vecNorm(vecNormal(axis[0], axis[1], vec)) / vecDistance(*axis)

def vecDistanceTriangle(triangle, vert):
    """Return (signed) distance between the plane spanned by triangle[0],
    triangle[1], and triange[2], and the vector v, in 3 dimensions.

    >>> vecDistanceTriangle([(0,0,0),(1,0,0),(0,1,0)], (0,0,1))
    1.0
    >>> vecDistanceTriangle([(0,0,0),(0,1,0),(1,0,0)], (0,0,1))
    -1.0
    """
    normal = vecNormal(*triangle)
    return vecDotProduct(normal, vecSub(vert, triangle[0])) / vecNorm(normal)

def basesimplex3d (vertices, precision):
    
    """Find four extreme points, to be used as a starting base for the
    quick hull algorithm L{qhull3d}.

    The algorithm tries to find four points that are
    as far apart as possible, because that speeds up the quick hull
    algorithm. The vertices are ordered so their signed volume is positive.

    If the volume zero up to C{precision} then only three vertices are
    returned. If the vertices are colinear up to C{precision} then only two
    vertices are returned. Finally, if the vertices are equal up to C{precision}
    then just one vertex is returned.

    >>> import random
    >>> cube = [(0,0,0),(0,0,1),(0,1,0),(1,0,0),(0,1,1),(1,0,1),(1,1,0),(1,1,1)]
    >>> for i in range(200):
    ...     cube.append((random.random(), random.random(), random.random()))
    >>> base = basesimplex3d(cube)
    >>> len(base)
    4
    >>> (0,0,0) in base
    True
    >>> (1,1,1) in base
    True

    :param vertices: The vertices to construct extreme points from.
    :param precision: Distance used to decide whether points coincide,
        are colinear, or coplanar.
    :return: A list of one, two, three, or four vertices, depending on the
        the configuration of the vertices.
    """
        
    # sort axes by their extent in vertices
    extents = sorted (range (3), key = lambda i: max (vert [i] for vert in vertices) - min (vert [i] for vert in vertices))    
    
    # extents[0] has the index with largest extent etc.
    # so let us minimize and maximize vertices with key
    # (vert[extents[0]], vert[extents[1]], vert[extents[2]])
    # which we can write as operator.itemgetter(*extents)(vert)
    vert0 = min (vertices, key = operator.itemgetter (*extents))
    vert1 = max (vertices, key = operator.itemgetter (*extents))
    
    # check if all vertices coincide
    if vecDistance (vert0, vert1) < precision:
        return [ vert0 ]
    
    # as a third extreme point select that one which maximizes the distance
    # from the vert0 - vert1 axis
    vert2 = max (vertices, key = lambda vert: vecDistanceAxis ((vert0, vert1), vert))
    
    #check if all vertices are colinear
    if vecDistanceAxis ((vert0, vert1), vert2) < precision:        return [ vert0, vert1 ]
    
    # as a fourth extreme point select one which maximizes the distance from
    # the v0, v1, v2 triangle
    vert3 = max (vertices, key = lambda vert: abs (vecDistanceTriangle ((vert0, vert1, vert2), vert)))
    
    # ensure positive orientation and check if all vertices are coplanar
    orientation = vecDistanceTriangle ((vert0, vert1, vert2), vert3)
    
    if   orientation >  precision:  return [ vert0, vert1, vert2, vert3 ]
    elif orientation < -precision:  return [ vert1, vert0, vert2, vert3 ]
    
    # coplanar
    else:        return [ vert0, vert1, vert2 ]


def qhull3d (vertices, precision):
    
    """Return the triangles making up the convex hull of C{vertices}.
    Considers distances less than C{precision} to be zero (useful to simplify
    the hull of a complex mesh, at the expense of exactness of the hull).

    :param vertices: The vertices to find the hull of.
    :param precision: Distance used to decide whether points lie outside of
        the hull or not. Larger numbers mean fewer triangles, but some vertices
        may then end up outside the hull, at a distance of no more than
        C{precision}.
    :param verbose: Print information about what the algorithm is doing. Only
        useful for debugging.
    :return: A list cointaining the extreme points of C{vertices}, and
        a list of triangle indices containing the triangles that connect
        all extreme points.
    """
    
    # find a simplex to start from
    hull_vertices = basesimplex3d (vertices, precision)

    # handle degenerate cases
    if len (hull_vertices) <= 3:
        
        ## BULLSHIT OUT
        return hull_vertices, []

    # construct list of triangles of this simplex
    hull_triangles = set ([operator.itemgetter (i,j,k) (hull_vertices) for i, j, k in ((1,0,2), (0,1,3), (0,3,2), (3,1,2))])

    # construct list of outer vertices for each triangle
    outer_vertices = {}
    
    for triangle in hull_triangles:
        
        outer = [(dist, vert) for dist, vert in zip ((vecDistanceTriangle (triangle, vert) for vert in vertices), vertices) if dist > precision ]
        
        if outer:   outer_vertices [triangle] = outer

    # as long as there are triangles with outer vertices
    while outer_vertices:
        
        # grab a triangle and its outer vertices
        tmp_iter = outer_vertices.items ()

        # tmp_iter trick to make 2to3 work
        triangle, outer = next (iter (tmp_iter))
        
        # calculate pivot point
        pivot = max (outer)[1]
        
        # add it to the list of extreme vertices
        hull_vertices.append (pivot)
        
        # and update the list of triangles:
        # 1. calculate visibility of triangles to pivot point
        visibility = [vecDistanceTriangle (othertriangle, pivot) > precision for othertriangle in iter (outer_vertices.keys ())]
        
        # 2. get list of visible triangles
        visible_triangles = [othertriangle for othertriangle, visible in zip (iter (outer_vertices.keys ()), visibility) if visible ]
        
        # 3. find all edges of visible triangles
        visible_edges = []
        for visible_triangle in visible_triangles:
            visible_edges += [operator.itemgetter (i, j)(visible_triangle) for i, j in ((0,1),(1,2),(2,0))]
            
        # 4. construct horizon: edges that are not shared with another triangle
        horizon_edges = [ edge for edge in visible_edges if not tuple (reversed (edge)) in visible_edges ]
        
        # 5. remove visible triangles from list
        # this puts a hole inside the triangle list
        visible_outer = set ()
        for outer_verts in iter (outer_vertices.values ()):
            visible_outer |= set (map (operator.itemgetter (1), outer_verts))
            
        for triangle in visible_triangles:
            hull_triangles.remove (triangle)
            del outer_vertices [triangle]
                        
        # 6. close triangle list by adding cone from horizon to pivot
        # also update the outer triangle list as we go
        for edge in horizon_edges:
            
            newtriangle = edge + (pivot, )
            
            newouter = [(dist, vert) for dist, vert in zip((vecDistanceTriangle (newtriangle, vert) for vert in visible_outer), visible_outer) if dist > precision ]
            
            hull_triangles.add (newtriangle)
            
            if newouter: outer_vertices [newtriangle] = newouter

    # clear dictionary
    outer_vertices.clear ()

    # no triangle has outer vertices anymore
    # so the convex hull is complete!
    # remap the triangles to indices that point into hull_vertices
    return hull_vertices, [tuple (hull_vertices.index (vert) for vert in triangle) for triangle in hull_triangles ]

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### FORMATTING NAMES - PARSE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def formatNameParse (format_string, keyword):

    literals = []

    literals.append (('l0', '%>'    + keyword))
    literals.append (('l1', '%>>'   + keyword))
    literals.append (('l2', '%>>>'  + keyword))
    literals.append (('l3', '%>>>>' + keyword))
    literals.append (('r3', '%'     + keyword + '<<<<'))
    literals.append (('r2', '%'     + keyword + '<<<'))
    literals.append (('r1', '%'     + keyword + '<<'))
    literals.append (('r0', '%'     + keyword + '<'))

    fstr = str (format_string)

    replaces = []

    fl = len (fstr)

    for lt in literals :

        ltok  = lt [0]
        ltstr = lt [1];     ll = len (ltstr)

        index = fstr.find (ltstr)

        while index >= 0:
            
            delimiter = ''; index += ll
            
            while ((index < fl) and (fstr [index] != '%')):
                
                delimiter += fstr [index]; index += 1

            if delimiter != '':

                replaces.append ((ltok, ltstr + delimiter + '%', delimiter))

                fstr = fstr.replace (ltstr + delimiter + '%', '')
                
                index = fstr.find (ltstr)
                
            else: break

    if (fstr.find ('%' + keyword + '%') >= 0):
        
        replaces.append ((None, '%' + keyword + '%', None))

    literals [:] = []

    return replaces

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### FORMATTING NAMES - SUBSTITUTE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def formatName (format_string, substition_string, replaces):

    result = format_string
    for r in replaces:
        if not  r [0]:  result = format_string.replace (r [1], substition_string)
        elif    r [0][0] == 'l':
            try:    i = int (r[0][1]);  result = format_string.replace (r [1], substition_string.split  (r [2], i + 1)[i + 1])
            except: pass
        elif    r [0][0] == 'r':
            try:    i = int (r[0][1]);  result = format_string.replace (r [1], substition_string.rsplit (r [2], i + 1)[0])
            except: pass

    return (result)

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS
####------------------------------------------------------------------------------------------------------------------------------------------------------

def process ():

    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    # save list
    selected = list (bpy.context.selected_objects)

    # anything selected ?
    if len (selected) == 0: return

    # log
    print ('\nConvex Hull starting... \n\n\tObjects (', len (selected), ') :')
    print ('')

    # object mode
    bpy.ops.object.mode_set (mode = 'OBJECT')

    # deselect all objects
    bpy.ops.object.select_all (action = 'DESELECT')

    # naming ..
    nameo = bpy.context.scene.shift_ch_nameo
    named = bpy.context.scene.shift_ch_named

    # parsing formatting string
    replo = formatNameParse (nameo, 'name')
    repld = formatNameParse (named, 'name')
            
    # process all objects
    for i, obj in enumerate (selected):

        # is it mesh ?
        if obj and obj.type == 'MESH':

            if scene.shift_ch_particles:

                psystem = obj.particle_systems.active
                
                if psystem and psystem.settings.dupli_object and psystem.settings.dupli_object.type == 'MESH':

                    # bounding box of dupli_object

                    mesh = psystem.settings.dupli_object.data
                    
                    minco = [ 99999999,  99999999,  99999999]
                    maxco = [-99999999, -99999999, -99999999]

                    for v in mesh.vertices :
                        
                        if v.co [0] < minco [0]:    minco [0] = v.co [0]
                        if v.co [1] < minco [1]:    minco [1] = v.co [1]
                        if v.co [2] < minco [2]:    minco [2] = v.co [2]
                        if v.co [0] > maxco [0]:    maxco [0] = v.co [0]
                        if v.co [1] > maxco [1]:    maxco [1] = v.co [1]
                        if v.co [2] > maxco [2]:    maxco [2] = v.co [2]

                    points = [mathutils.Vector ((minco [0], minco [1], minco [2])),
                              mathutils.Vector ((maxco [0], minco [1], minco [2])),
                              mathutils.Vector ((minco [0], maxco [1], minco [2])),
                              mathutils.Vector ((maxco [0], maxco [1], minco [2])),
                              mathutils.Vector ((minco [0], minco [1], maxco [2])),
                              mathutils.Vector ((maxco [0], minco [1], maxco [2])),
                              mathutils.Vector ((minco [0], maxco [1], maxco [2])),
                              mathutils.Vector ((maxco [0], maxco [1], maxco [2]))]
                    
                    minco [:] = []
                    maxco [:] = []
                    
                else:
                    
                    print ('ERROR | Object \'', obj.name, '\' is missing particle system/dupli_object/mesh !')
                    continue

                verts = []

                for p in psystem.particles:

                    # build matrix for particle
                    matrix = mathutils.Matrix ().identity ()
                    
                    # rotation and scale from dupli object
                    #matrix = obj.matrix_world.rotation_part ().to_4x4 () * matrix
                    
                    # scale
                    matrix = mathutils.Matrix.Scale (p.size, 4) * matrix
                            
                    # rotation
                    matrix = p.rotation.to_matrix ().resize4x4 () * matrix
                    
                    # translation
                    matrix = mathutils.Matrix.Translation (p.location) * matrix

                    for point in points:
                        pointn = point * matrix            
                        
                        verts.append ((pointn [0], pointn [1], pointn [2]))

            else:

                # list for qhull
                verts = list ((v.co [0], v.co [1], v.co [2]) for v in obj.data.vertices)
  
            # generating convex hull
            vertices, triangles = qhull3d (verts, bpy.context.scene.shift_ch_precision)

            # clean up
            verts [:] = []

            # new mesh
            meshn = bpy.data.meshes.new (formatName (named, obj.data.name, repld))
            
            # make a mesh from a list of verts/edges/faces
            meshn.from_pydata (vertices, [], triangles)

            minx = 99999999.0; maxx = -99999999.0
            miny = 99999999.0; maxy = -99999999.0
            minz = 99999999.0; maxz = -99999999.0

            # bounding box
            for v in meshn.vertices:

                if v.co [0] < minx :    minx = v.co [0]
                if v.co [1] < miny :    miny = v.co [1]
                if v.co [2] < minz :    minz = v.co [2]
                
                if v.co [0] > maxx :    maxx = v.co [0]
                if v.co [1] > maxy :    maxy = v.co [1]
                if v.co [2] > maxz :    maxz = v.co [2]

            # bbox center
            center = mathutils.Vector ((minx + maxx, miny + maxy, minz + maxz)) * 0.5

            # apply scale
            for v in meshn.vertices:

                v.co [0] = (v.co [0] - center [0]) * bpy.context.scene.shift_ch_scale + center [0]
                v.co [1] = (v.co [1] - center [1]) * bpy.context.scene.shift_ch_scale + center [1]
                v.co [2] = (v.co [2] - center [2]) * bpy.context.scene.shift_ch_scale + center [2]

            # clean up
            triangles [:] = []
            vertices [:] = []

            # update mesh geometry after adding stuff
            meshn.update ()

            # new object
            objn = bpy.data.objects.new (formatName (nameo, obj.name, replo), meshn)

            # matrix
            objn.matrix_world = obj.matrix_world

            # link to scene
            bpy.context.scene.objects.link (objn)

            # set active object
            scene.objects.active = objn

            # edit mode
            bpy.ops.object.mode_set (mode = 'EDIT')

            # face selection mode
            bpy.context.tool_settings.mesh_select_mode = (False, False, True)

            # select all faces
            bpy.ops.mesh.select_all (action = 'SELECT')

            # set smooth shading
            bpy.ops.mesh.faces_shade_smooth ()

            # edit mode
            bpy.ops.object.mode_set (mode = 'OBJECT')
            
            # select new object
            objn.select = True
            
            # log
            print (i + 1,"Convex Hull : \'",obj.name,"' -> '", objn.name,"'")

        else:
            
            print ('ERROR | Object \'', obj.name, '\' is not mesh !')

    # log            
    print ('')
    print ('\nConvex Hull finished in %.4f sec.' % (time.clock () - start_time))

    # clean up
    selected [:] = []
                
####------------------------------------------------------------------------------------------------------------------------------------------------------
#### CHECK NAMES
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processCheckNames ():

    print ('Check names : ')
    print ('')

    # naming ..
    nameo = bpy.context.scene.shift_ch_nameo
    named = bpy.context.scene.shift_ch_named

    # parsing formatting string
    replo = formatNameParse (nameo, 'name')
    repld = formatNameParse (named, 'name')

    for obj in bpy.context.selected_objects:

        # is it mesh ?
        if obj and obj.type == 'MESH':

            nameoo = formatName (nameo, obj.name, replo)
            namedd = formatName (named, obj.data.name, repld)

            print ("Object : '", nameoo, " \tData : ", namedd)
    print ('')
            
    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### INTEGRATION AND GUI
####------------------------------------------------------------------------------------------------------------------------------------------------------

class ConvexHullOp (bpy.types.Operator):

    bl_idname   = "object.convexhull_operator"
    bl_label    = "SHIFT - Convex Hull"
    bl_register = True
    bl_undo     = True
    
    def execute (self, context):

        if bpy.context.scene.shift_ch_nameo != '' and \
           bpy.context.scene.shift_ch_named != '' :

            process ()

        return {'FINISHED'}

class ConvexHullOpCheck (bpy.types.Operator):

    bl_idname       = "object.convexhull_operator_check"
    bl_label        = "SHIFT - Convex Hull"
    bl_description  = "Prints formatted name(s)"
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        if bpy.context.scene.shift_ch_nameo != '' and \
           bpy.context.scene.shift_ch_named != '' :

            processCheckNames ()

        return {'FINISHED'}
        
class ConvexHullPanel (bpy.types.Panel):
     
    bl_idname   = "object.convexhull_panel"
    bl_label    = "SHIFT - Convex Hull"
    bl_context  = "objectmode"
    bl_register = True
    bl_undo     = True

    bl_space_type   = 'VIEW_3D'
    bl_region_type  = 'TOOLS'

    def draw (self, context):
            
        layout = self.layout
        
        box = layout.box()
        box.operator       ('object.convexhull_operator', 'Generate')

        box1 = box.box ()
        
        split = box1.split (percentage = 0.95, align = True)
        split.prop          (context.scene, 'shift_ch_nameo')
        split.operator      ('object.convexhull_operator_check', 'C')
        
        split = box1.split (percentage = 0.95, align = True)
        split.prop          (context.scene, 'shift_ch_named')
        split.operator      ('object.convexhull_operator_check', 'C')

        box1 = box.box ()
        box1.prop           (context.scene, 'shift_ch_precision')
        box1.prop           (context.scene, 'shift_ch_scale')
        
        box1 = box.box ()
        box1.prop           (context.scene, 'shift_ch_particles')
                
def register ():

    # options
        
    # ----------------------------------------------------------
    bpy.types.Scene.shift_ch_precision = FloatProperty (
        name        = "Precision",
        description = "Distance used to decide whether points lie outside of the hull or not.",
        min         = 0.0001,
        max         = 10.0,
        precision   = 4,
        step        = 1,
        subtype     = 'DISTANCE',
        default     = 0.1)

    # ----------------------------------------------------------
    bpy.types.Scene.shift_ch_scale = FloatProperty (
        name        = "Scale",
        description = "Scale vertex positions from bbox center by factor",
        min         = 1.0,
        max         = 10.0,
        precision   = 1,
        step        = 1,
        subtype     = 'FACTOR',
        default     = 1.0)
    
    # ----------------------------------------------------------
    bpy.types.Scene.shift_ch_nameo = StringProperty (
        name        = "Object",
        description = "Formatting string determining name of created object(s)",
        default     = "%name%_chull",
        subtype     = 'NONE')
    bpy.types.Scene.shift_ch_named = StringProperty (
        name        = "Data",
        description = "Formatting string determining name of created datablock(s)",
        default     = "%name%_chull",
        subtype     = 'NONE')

    # ----------------------------------------------------------
    bpy.types.Scene.shift_ch_particles = BoolProperty (
        name        = "Particles",
        description = "Creates convex hull on active particles of dupli objects, using their bounding boxes",
        default     = False)
    
    
    try:
        bpy.types.register (ConvexHullOp)
        bpy.types.register (ConvexHullOpCheck)
        bpy.types.register (ConvexHullPanel)
        
    except: pass
     
def unregister ():

    try:
        bpy.types.unregister (ConvexHullOp)
        bpy.types.unregister (ConvexHullOpCheck)
        bpy.types.unregister (ConvexHullPanel)

        del bpy.types.Scene.shift_ch_nameo
        del bpy.types.Scene.shift_ch_named
        del bpy.types.Scene.shift_ch_scale
        del bpy.types.Scene.shift_ch_precision
        del bpy.types.Scene.shift_ch_particles
        
    except: pass
     
if __name__ == "__main__":
    
    try:        
        register ()
        
    except: pass;
