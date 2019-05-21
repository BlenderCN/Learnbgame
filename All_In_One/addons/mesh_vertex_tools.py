################################################################################
#                                                                              #
#    GNU GPL LICENSE                                                           #
#    ---------------                                                           #
#                                                                              #
#    Copyright (C) 2006-2009: Guillaume Englert                                #
#                                                                              #
#    This program is free software; you can redistribute it and/or modify it   #
#    under the terms of the GNU General Public License as published by the     #
#    Free Software Foundation; either version 2 of the License, or (at your    #
#    option) any later version.                                                #
#                                                                              #
#    This program is distributed in the hope that it will be useful,           #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#    GNU General Public License for more details.                              #
#                                                                              #
#    You should have received a copy of the GNU General Public License         #
#    along with this program; if not, write to the Free Software Foundation,   #
#    Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.           #
#                                                                              #
################################################################################
#    Adaptation for Blender 2.5: Witold Jaworski (2011)
#    The code below is a fragment of original Geom Tools for Blender 2.4x
################################################################################
# ---------------- mesh_geom_tool_math.py (fragments) --------------------------
################################################################################
from mathutils import Vector
#CONSTANTS--------------------------------------------------

EPSILON = 0.001
DEBUG = 1 #set it to 0, for the "productive version"
#Functions--------------------------------------------------
def XYZvertexsort(verts):
    """ Sort a list of vertex with the most appropriate coordinate (x, y or z).
        Arguments:
        @verts (list): a list of vertices (MeshVertex instances).
        returns: the sorted list.
        NB: verts is modified.
    """
    ##sort the vertices to get a list of aligned point (normally :)
    verts.sort(key=lambda v: v.co.x)    #X coord sort
    vertstmp = list(verts)
    vertstmp.sort(key=lambda v: v.co.y) #Y coord sort

    #compare the x diff and the y diff
    diff  = abs(verts[0].co.x - verts[-1].co.x)
    diffy = abs(vertstmp[0].co.y - vertstmp[-1].co.y)
    if diff < diffy:
        verts, vertstmp = vertstmp, verts
        diff = diffy

    vertstmp.sort(key=lambda v: v.co.z) #Z coord sort

    #compare the x|y diff and the z diff
    if diff < abs((vertstmp[0].co.z - vertstmp[-1].co.z)):
        verts = vertstmp

    return verts

def project_point_vect(point, o, vect):
    """ Projection of a point on an 'affine vector'.
        Arguments:
        @point(Vector): the projected point
        @o (Vector): start extremity of the vector 
        @vect (Vector): direction vector 
        returns: the projected vector (Vector object)
    """
    t = (point - o)
    return o + t.project(vect)
# Classes -------------------------------------------------
class BezierInterpolator:
    """Interpolate a vertex loop/string with a bezier curve."""
    def __init__(self, vertloop):
        """Constructor.
            Arguments:
            @vertloop (list): the vertex loop a list of vertices (MeshVertex objects).
                              If it's a true loop (and not a simple string), the first and the last
                              vertices are the same vertex.
        """
        nodes = [None, None] #2 first nodes

        it = (v.co for v in vertloop)
        p0 = next(it)
        p1 = next(it)

        for p2 in it:
            vect = p2 - p0
            vect.normalize()

            nodes.append(p1 - (abs(vect.dot(p1-p0)) / 3.0) * vect)
            nodes.append(Vector(p1))
            nodes.append(p1 + (abs(vect.dot(p2-p1)) / 3.0) * vect)

            p0 = p1
            p1 = p2


        if vertloop[0].index == vertloop[-1].index: #it's a true loop
            p0 = vertloop[-2].co
            p1 = vertloop[0].co
            p2 = vertloop[1].co

            vect = p2 - p0
            vect.normalize()

            nodes[1] =   p1 + (abs(vect.dot(p2-p1)) / 3.0) * vect
            nodes.append(p1 - (abs(vect.dot(p1-p0)) / 3.0) * vect)

            tmpvect  = Vector(p0)
            nodes[0] = tmpvect
            nodes.append(tmpvect)

        else: #it's a 'false' loop: a simple edge string
            #1rst intermediate node
            p0  = vertloop[0].co
            p1  = vertloop[1].co
            p01 = nodes[2]

            nodes[0] = Vector(p0)
            nodes[1] = p0 - 2.0*project_point_vect(p01, p1, p0-p1) + p1 + p01

            #last one
            p0  = vertloop[-1].co
            p1  = vertloop[-2].co
            p01 = nodes[-1]

            nodes.append(p0 - 2.0*project_point_vect(p01, p1, p0-p1) + p1 + p01)
            nodes.append(Vector(p0))

        self._nodes = nodes

    def interpolate(self, t, vind):
        """ Interpolates 2 vertices of the original vertex loop.
            Arguments:
            @t (float): parameter for the bezier curve - between 0.0 and 1.0.
            @vind (int): the index of the first vertex, in the original loop
            returns Vector object (interpolation between vertloop[vind] and vertloop[vind+1])
        """
        _1_t  = 1.0 - t
        i     = 3 * vind
        nodes = self._nodes

        return nodes[i]                * (_1_t**3) + \
               nodes[i+1] * 3 *  t     * (_1_t**2) + \
               nodes[i+2] * 3 * (t**2) *  _1_t     + \
               nodes[i+3] *     (t**3)
################################################################################
# ---------------- mesh_geom_tool.py (fragments) -------------------------------
################################################################################
import bpy
from itertools import islice
from sys import exc_info
from bpy.utils import register_module, unregister_module
# general code -------------------------------------------------
def get_selected_vertices(mesh):
    """ Returns the list of selected vertices (there is nothing like this in current API)
        Arguments:
        @mesh (Mesh): the edited mesh datablock
    """
    return list(filter(lambda v: v.select, mesh.vertices))

def get_selected_edges(mesh):
    """ Returns the list of selected edges (there is nothing like this in current API)
        Arguments:
        @mesh (Mesh): the edited mesh datablock
    """
    return list(filter(lambda e: e.select, mesh.edges))

# align vertices --------------------------------------

def align_vertices(mesh, distr):
    """Distribute vertices regularly or align them.
        Arguments:
        @mesh (Mesh): the edited mesh datablock
        @distr (Bool): True, when to perform align & distribute
    """
    vsel = get_selected_vertices(mesh)

    if len(vsel) < 3:
        raise Exception("need 3 vertices at least")


    vsel  = XYZvertexsort(vsel)
    point = vsel[0].co
    vect  = (vsel[-1].co - point) * (1.0/(len(vsel)-1))

    if vect.length < EPSILON: return

    if distr == True: #align & distribute
        for mult, vert in enumerate(islice(vsel, 1, len(vsel)-1)):
            v = vert.co
            finalv = (mult+1) * vect + point
            v.x = finalv.x
            v.y = finalv.y
            v.z = finalv.z

    else: #align only
        for vert in islice(vsel, 1, len(vsel)-1):
            v = vert.co
            finalv = project_point_vect(v, point, vect)
            v.x = finalv.x
            v.y = finalv.y
            v.z = finalv.z

    mesh.update()

# distribute vertices ------------------------------------------
class EdgeVert(object):
    """Helper structure: a vertex of an edge."""
    __slots__ = ('edge', 'vind')

    def __init__(self, edge, vind):
        self.edge = edge  #MeshEdge object
        self.vind = vind  #index of vertex for the edge (1 or 2)

def vertex_string(edict, vert):
    """ Builds a list of edge-connected vertex indices.
        Arguments:
        @edict (dict): edge dictionary {vextex_index, [list_of_EdgeVert_linked_to_this_vertex]}
        @vert (int): the index of 1rst vertex of the vertex string.
        returns: the list of vertex indices.
    """
    vlist = [vert]
    vind  = vert

    try:
        while True:
            convert = edict[vind].pop() #connected vertex
            edge    = convert.edge

            if convert.vind == 1: v2add = edge.vertices[1]
            else:                 v2add = edge.vertices[0]

            vind = v2add
            vlist.append(v2add)

            lst = edict[vind]

            for i, elt in enumerate(lst):
                if elt.edge.index == edge.index:
                    del lst[i]
                    break
    except KeyError:   pass #edict[vind] with vind not a valid key
    except IndexError: pass #pop() on an empty list

    return vlist

def get_loop(edges, verts):
    """ Return a 'loop' of vertices edge-connected (loop[N] and loop[N+1] are edge-connected).
        Arguments:
        @edges(list): list of selected edges (MeshEdge objects).
        @verts(list): list of selected vertices (MeshVertex objects).
        returns: a list of MeshVertex objects
        NB: if the loop is a 'true loop' (and not a simple string), the first
        and the last vertex of the list are the same.
    """
    e = edges.pop() #we need an edge to begin
    
    edict = dict((v.index, []) for v in verts)
    for edge in edges:
        edict[edge.vertices[0]].append(EdgeVert(edge, 1))
        edict[edge.vertices[1]].append(EdgeVert(edge, 2))

    looptmp = vertex_string(edict, e.vertices[0])
    loop    = vertex_string(edict, e.vertices[1])

    for val in edict.values():
        if val: raise Exception("need an edge loop")

    loop.reverse()
    loop.extend(looptmp)
    
    vdict = dict((v.index, v) for v in verts) #dictionary of vertices, by their index
    
    return list(vdict[i] for i in loop) #build the list of vertex objects...

def loop_size(loop):
    """ Get the geometric length of a vertex loop.
        Arguments:
        @loop(list): vertices (MeshVertex objects).
        returns: the length (float).
    """
    size = 0.0
    vects = (v.co for v in loop)
    v1    = next(vects)

    for v2 in vects:
        size += (v2-v1).length
        v1 = v2

    return size

def distribute_vertices(mesh):
    """ Distribute vertices regularly on a curve.
        Arguments:
        @mesh (Mesh): the mesh datablock, containing the vertices
    """
    vsel = get_selected_vertices(mesh)

    if len(vsel) < 3:
        raise Exception("need 3 vertices at least")
    
    loop   = get_loop(get_selected_edges(mesh), vsel)
    interp = BezierInterpolator(loop)

    new_coords = []
    average    = loop_size(loop) / (len(loop)-1)

    vects = (v.co for v in loop)
    v1    = next(vects)
    v2    = next(vects)
    index = 0

    size_acc = 0.0             #size accumulator
    vec_len  = (v2-v1).length

    for coeff in (average*i for i in range(1, len(loop)-1)):
        while coeff > (size_acc+vec_len):
            size_acc += vec_len
            v1 = v2
            v2 = next(vects)
            index += 1
            vec_len = (v2-v1).length

        #here we have: size_acc < coeff < (size_acc+vec_len)
        # ~~> coeff 'between' v1 & v2
        new_coords.append(interp.interpolate((coeff-size_acc)/vec_len, index))


    it = iter(loop)
    next(it) #begin with the 2nd vertex
    for coord in new_coords:
        v   = next(it).co
        v.x = coord.x
        v.y = coord.y
        v.z = coord.z

    mesh.update()
################################################################################
# ---------------- Add-On implementation ---------------------------------------
################################################################################
bl_info = {
    "name": "Vertex Tools",
    "author": "Guillaume Englert, Witold Jaworski",
    "version": (1, 0, 1),
    "blender": (2, 5, 7),
    "api": 36147,
    "location": "View 3D > Mesh > Vertex >Align & Distribute",
    "category": "Mesh",
    "description": "Align or distribute selected vertices (from the old Geom Tool)",
    "warning": "",
    "tracker_url": "http://airplanes3d.net/track-254_e.xml",
    "wiki_url": "http://airplanes3d.net/scripts-254_e.xml"
    }

#common base for operators:
#just to not implement the same checks twice
class VertexOperator:
    #--- methods to override:
    def action(self,mesh):
        """Override this function in the children classes
            Arguments:
            @mesh (Mesh): the mesh datablock with selected vertices
            NB: this method can throw exceptions!
        """
        pass #default implementation: empty
    
    def show(self, msg): 
        """Override this function to use the Operator.report method
            Arguments:
            @msg (str): the message to be displayed 
        """
        print(msg)
        
    #--- common implementation of the Operator interface: 
    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')
    
    def invoke(self, context, event):
        return self.execute(context)
        
    def execute(self, context):
        mesh = context.object.data
        bpy.ops.object.editmode_toggle()
        result = 'FINISHED'
        try:
            self.action(mesh)
            
        except Exception as e:
            if len(e.args) > 0 :
                msg = e.args[0]
            else:
                msg = "Error: " + exc_info()[1]
                
            self.show(msg)
            
            result = 'CANCELLED'
        bpy.ops.object.editmode_toggle()
        return {result}
    
# operators --------------------------------------------------------------------
class DistributeVertices(bpy.types.Operator, VertexOperator):
    ''' Distribute vertices evenly along interpolated shape of their polyline 
    '''
    bl_idname = "mesh.vertex_distribute"
    bl_label = "Vertex Distribute"
    bl_description = "Distribute selected vertices evenly along their loop"
    
    def show(self, msg):
        self.report('ERROR', message = msg) 
    
    def action(self, mesh):
        distribute_vertices(mesh)

class AlignVertices(bpy.types.Operator, VertexOperator):
    ''' Project vertices onto the line between the first and last selected vertex 
    '''
    bl_idname = "mesh.vertex_align"
    bl_label = "Vertex Align"
    bl_description = "Project vertices onto the line between the first and last selected vertex"
    
    def show(self, msg):
        self.report('ERROR', message = msg) 
    
    def action(self, mesh):
        align_vertices(mesh,False)

class InlineVertices(bpy.types.Operator, VertexOperator):
    ''' Place vertices evenly along straight line 
    '''
    bl_idname = "mesh.vertex_inline"
    bl_label = "Vertex Align & Distribute"
    bl_description = "Distribute vertices evenly along a straight line"
    
    def show(self, msg):
        self.report('ERROR', message = msg) 
    
    def action(self, mesh):
        align_vertices(mesh,True)

def menu_draw(self, context):
        self.layout.operator_context = 'INVOKE_REGION_WIN'
        self.layout.separator()
        self.layout.operator(DistributeVertices.bl_idname, "Distribute")
        self.layout.operator(AlignVertices.bl_idname, "Align")
        self.layout.operator(InlineVertices.bl_idname, "Align & Distribute")

#--- ### Register
def register():
    register_module(__name__)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.append(menu_draw)
    
def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(menu_draw)
    unregister_module(__name__)
    
if DEBUG > 0:
    print("mesh_vertex_tools.py: new version loaded!") #just to be sure, that we are testing what we should
    
if __name__ == '__main__':
    register()