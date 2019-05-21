# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
bl_info = {
    "name": "Intersection",
    "author": "Witold Jaworski",
    "version": (1, 2, 0),
    "blender": (2, 6, 3),
    "location": "View 3D > Specials [W-key] > Intersection",
    "category": "Object",
    "description": "Adds to the mesh of active object its intersection with another mesh object",
    "warning": "",
    "wiki_url": "http://airplanes3d.net/scripts-253_e.xml",
    "tracker_url": "http://airplanes3d.net/track-253_e.xml"
    }
#----- updates
#2011-09-22 (Witold Jaworski): reversed sequence of Vector*Matrix multiplication to proper Matrix*Vector    
#2012-04-29 (Witold Jaworski): adaptation for Blender 2.63 (BMesh): using the tessfaces instead of faces collection. 
#2012-09-28 (Witold Jaworski): correction (edges of tessfaces have not normalized edge keys, as faces in 2.49). It lead to discarding
#                              most of the founded points as "diagonals".
#2012-09-29 (Witold Jaworski): Further corrections of other errors (concerned with "gluing" the cross points into edges)
#2012-11-05 (Witold Jaworski): Refactoring the Intersect* operators to enable self-intersection of selected and unselected
#                              faces of a single mesh (invoked from Edit Mode).
#----- imports
import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty
from bpy.utils import register_module, unregister_module
#from mathutils import Vector, Matrix
from mathutils.geometry import intersect_ray_tri
from time import time
####general comments-------------------------------------------------------
#The algorithm for the crossing calculation is following:
#1. Prepare the data - use meshes of selected objects to create two CMesh
#   instances. There no special assumptions about the topology of selected 
#   meshes - they can be a multi-piece mesh, closed or open.
#   Each CMesh stores a list of all faces of assigned object. They are converted
#   into world coordinates and eventually split from quads to triangles. They
#   are the CFace class instances. 
#    We will refer to the CMesh representing the first selected object as mesh A,
#   and the second as mesh B.  
#
#2. For each face from A: check intersection with every face of B faces. Store
#   the found cross points in A.cpoints list. The crossing points are searched
#   first crossing each A's edges (CEdge) with B face triangle. Then the B's 
#      edges are crossed with A's face triangle. There should be always be a zero 
#   or two crossing points (CPoint) found. They are referred to each other, to 
#   allow arrange them into proper loop at the next stage. 
#   (They are found randomly, now, so it is not right place to discover the loop)
#
#3. Arrange the found cross points into properly ordered loops. To find a loop,
#   select the arbitrary (in implementation: first) point from list of found
#   points. Using the references created at 2. find all the ancestors of the 
#   selected point. Then find all precedensors, and connect this two lists
#   to get a complete loop.
#
#
#   In this implementation, to minimize the intersection calculations, first 
#   test is a "box" test: the extents of two faces are compared. Further 
#   calculations are performed only for the faces that have the "box" test 
#   passed.
#      The face's edges (CEdge) are created "on demand", when there is a need to
#   cross them with a face. Many faces will never demand their edges, so they
#   will be never created. Edges, during creation, are referenced by both faces
#   that share it. 
#      This will reduce greatly the number of edges.
#   Each edge "remembers" result of the crossing with each face, so also the
#   calculations with negative result will not be performed twice.
#   In general, this implementation uses heavily the memory, and minimizes
#   the CPU usage as much, as possible. 
#   
#   Below - definitions of four object classes, that take part in the intersection: 
#        CMesh, 
#        CFace, 
#        CEdge, 
#        CPoint (it is the result - cross point, not vertex!)
####constants---------------------------------------------------------------
EPSILON    = 0.00000001 #the tolerance of crossing faces (in world units)
BOX_EPSILON = 0*EPSILON #the tolerance of comparing 'boxes', containing
                        #faces. Actually it seems to have no influence
                        #on the final result.
PIXELS_PER_ICON = 16    #used in the formatting the message popup
PIXELS_PER_CHAR = 6        #used in the formatting the message popup
DEBUG = 1 # Debug level. When nonzero, some diagnostics texts are placed at 
        #   output, during processing. Level = 1 generates some genral
        #   statements, Level = 5 - intermediate, while Level = 9 is the most 
        #   detailed
####globals-----------------------------------------------------------------
_cpoints = []         #The result list of cross points (CPoint) found 
                     #It is a reference to one global result list, 
                     #(it resolved some algorithm problems for printing the CPoint representation)    

####classes-----------------------------------------------------------------

class CMesh:
    """Represents a mesh, one of two used to find the intersection"""

    #private instance fields:
    #__src => Mesh:            Blender's mesh object
    #
    #    working dictionaries, used during intersection:
    #__verts => {Vector}:     a dictionary of mesh vectors - in global space
    #                        coordinates. The key is the Mesh vertex ordinal.
    #__edges => {Edge}:        dictionary of edges, that will be tested.
    #                        The key is a tuple of begin and end vertices 
    #                        ordinals. The smaller ordinal is always the first 
    #                        element    of the tuple key. Initially all values are
    #                        plain indices (integers) to self.__src.edges[] list.                         
    #                        Then, while processing, some of these indices -
    #                        edges that are "suspected" to have a cross
    #                        point with the second mesh - will be replaced with 
    #                        CEdge instances.
    #                        This "suspect" is based on face's spatial
    #                        position. (When they pass the "box" test)
    #__neighbours=>{Face}    dictionary of faces, that form the mesh. In this
    #                        dictionary every face is registered 3 times. (for 
    #                        every edge). The key is a tuple of two edge's 
    #                        vertices ordinals. The sequence of these ordinals 
    #                        matches the direction of the edge along assigned.
    #                        Thus some of these keys will be a reversed version 
    #                        of the keys in the __edges dictionary, the others  
    #                        will be identical.
    #                        For all non-boundary edges there always are two keys,
    #                        one for each face that shares this particular edge.
    #                        The value tuples of such keys are a reversion of 
    #                        each other.
    
    #public instance fields:
    #faces => {Face}        dictionary of faces, that forms the mesh. In this
    #                        dictionary the key is a tuple containing 3 ordinals
    #                        of face vertices. The sequence of these ordinals 
    #                        describes the face direction.
    
    #instance methods:
    def __init__(self, object, use_selected, skip_hidden):
        """Initializes a mesh instance
            Arguments:
                object:         a Blender's object - a Mesh object
                use_selected:   int or Boolean: -1 when use NOT selected faces, 0 (False) when use all, 
                                1 (True) when use selected faces
                skip_hidden:    True to exclude the hidden faces from the intersection 
        """
        def is_selected(select, hide, use_selected, skip_hidden):
            """Helper function to determine vertices and faces to be incorporated into this object
                Arguments:
                    select:    value of the .select flag of a vertex or face
                    hide:      value of the .hide flag of a vertex or face
                    use_selected: int or Boolean: -1 when use NOT selected, 0 (False) when use all, 1 (True) when use selected
                    skip_hidden: True to exclude the hidden faces from the intersection 
            """
            if skip_hidden:
                if use_selected == -1:
                    return (not select and not hide)
                else:
                    if use_selected:
                        return (select and not hide)
                    else:
                        return not hide
            else:
                if use_selected == -1:
                    return (not select)
                else:
                    if use_selected:
                        return (select)
                    else:
                        return True
                
        self.__src = object.data 
        self.__src.calc_tessface()  #force to update the n-gons tesseleation
        self.__neighbours = {}
        self.faces = {}
        #Fill the __edges: dictionary 
        self.__edges = {}
        #we have to use edge_keys, because edges.items() can return edge objects instead of edge indices 
        #(and it can be switched in the middle of the returned list!)
        index = 0 
        for e in self.__src.edge_keys:
            v = e
            if v[0] > v[1] : v = (v[1], v[0]) #normalize the key!
            self.__edges[v] = index #initially all values in this dictionary are edge indices
            index += 1
        
        #fill the __verts dictionary (translate points to worldspace):
        self.__verts = {}
        m = object.matrix_world
        if DEBUG > 8: print("\nVertices %s:" % object.name)
        for v in self.__src.vertices:
            self.__verts[v.index] = m * v.co
            if DEBUG > 8:    print("%s: %s;" % \
                                    (repr(v.index), \
                                    repr(self.__verts[v.index])))                
        
        #register faces:
        #try to find the faces selected, and determine the use_all flag:
        #(this line gives proper result in Object Mode, only!:)
        if use_selected or skip_hidden:
            #verification: do not stick onto use_selected, when nothing is selected!
            if use_selected and not list(filter(lambda f: f.select, self.__src.tessfaces)):
                use_selected = False
                
            selected = list(filter(lambda f: is_selected(f.select, f.hide, use_selected, skip_hidden), self.__src.tessfaces))
        else:
            selected = self.__src.tessfaces #all

        for f in selected:
            if f.area > EPSILON :
                keys = list(f.vertices) #list of 3 or 4 vertex indices (n-gons are tesselated into trangles or quads!)
                if len(keys) == 3: #a triangle - no cut needed
                    self.AddFace(f, (keys[0],keys[1],keys[2]))
                elif len(keys) == 4: #a quad - cut it into two triangles
                    #l0, l2: the lengths of the dialgonals
                    l0 = self.vert(keys[2]) - self.vert(keys[0])
                    l2 = self.vert(keys[3]) - self.vert(keys[1])
                    if l2.length < l0.length: #cut along (1, 3) edge
                        self.AddFace(f, (keys[0],keys[1],keys[3]))
                        self.AddFace(f, (keys[1],keys[2],keys[3]))
                    else: #cut along (0, 2) edge
                        self.AddFace(f, (keys[0],keys[1],keys[2]))
                        self.AddFace(f, (keys[0],keys[2],keys[3]))
                        
    def name(self):
        """Returns the name of wrapped Blender Mesh object
            (useful for diagnostic messages)
        """        
        return self.__src.name
    
    def vert(self, index):
        """Returns one of the mesh vertices (a Vector, in world coordinates)
            Arguments:
                index:    the vertex index in the mesh 
        """
        return self.__verts[index]

    def neighbour(self, edgekey):
        """Returns the face that uses the same edge, but in opposite direction 
            Arguments:
                edgekey:    the key of the edge, along face direction (i.e.
                            NOT normalized: as it is in CFace.__edges dictionary
        """
        #the neighbour HAS to be registered in __neighbours under the 
        #reversed key:
        key = (edgekey[1],edgekey[0])
        if key in self.__neighbours: return self.__neighbours[key]
        else: return None
        
    def cpindex(self,cpoint):
        """Returns index of given cross point (CPoint), or None if not registered
            Arguments:
                cpoint:    a cross point (a CPoint instance) that is chcecked
            
            Used for diagnostics and debbuging, not especially fast.
            For some cross points can return None, because they have been
            discarded during calculations.
        """
        global _cpoints
        if cpoint in _cpoints : return _cpoints.index(cpoint)
        else: return None
        
    def GetEdge(self,key):
        """Returns an edge (CEdge instance) that matches the given key
            Arguments:
                key:    a tuple of 2 integers - vertex ordinals
        """
        key = CEdge.Normalize(key)  #the key may come in non-canonical order
                                    #(smaller ordinal as the second element)
                                    #so we have to get rid of it.
        if key in self.__edges:
            value = self.__edges[key]
            if type(value) == int: #this edge exists in source mesh:
                edge = CEdge(self, self.__src.edges[value], key, \
                                        self.vert(key[0]), self.vert(key[1]))
            else: #edge already prepared:
                return value
        else: #no edge found - this is a diagonal temporary edge:
            edge = CEdge(self, None, key, \
                                    self.vert(key[0]), self.vert(key[1]))

        #add the edge to the edge dictionary:
        self.__edges[key] = edge

        #assign it to two neighbour faces:
        fcount = 0 #count of the faces that share this edge
        if edge.key in self.__neighbours:
            self.__neighbours[edge.key].Assign(edge)
            fcount += 1

        #The other face is registered at inverted the key tuple:
        if edge.altkey() in self.__neighbours:
            self.__neighbours[edge.altkey()].Assign(edge)
            fcount += 1
            
        #edge is a boundary edge, when it is not shared by two faces:
        edge.boundary = (fcount < 2)

        return edge
    
    def AddFace(self, mface, key):
        """    Appends to faces, __neighbours dictionary  (of CFace instances) 
            the newly created face, based on source mesh
            Arguments:
                mface:    a source data - the MFace (may be a quad)
                key:    a tuple of 3 integers - vertex ordinals
        """
        face = CFace(self, mface, key)
        self.faces[key] = face
        
        #in the __neighbour dictionary every face is represented 3 times-
        #by its edges oridnals:
        for k in [(key[0],key[1]),(key[1],key[2]),(key[2],key[0])]:
            self.__neighbours[k] = face
            
    def Intersect(self, key, face):
        """Intersects the face from this mesh, identified by a key, with another
            Arguments:
                key:    tuple (3 integers - vertex ordinals) that identifies 
                        a face in this mesh (in faces dictionary)
                face:    a face from another mesh (CFace)
            
            Returns a list of 2 cross points, or empty list
        """
        global _cpoints
        a,b = self.faces[key],face #a, b are just a shortcuts for the full names
        result = a.Intersect(b)    #store in the list the cross points from a...
        result.extend(b.Intersect(a)) #... together with b.
        if result:
            if DEBUG > 8:    print("\n%s %s x %s %s (%d points):" % \
                                        (a.mesh.name(), repr(a.key), \
                                         b.mesh.name(),repr(b.key),len(result)))
                                        
            #Normally there should be always 2 cross points in the result,
            #but sometimes, when edge from one mesh crosses exactly the edge 
            #from the other mesh, there may appear 1 or 3 points. There may
            #be also, theoretically, 4 (two triangles crossing each other edges)
            #but I have never seen such case. (I have try to obtain it, but
            #there always were 3, 2 or 1 points). 
                                        
            if len(result) == 4: #I have never seen such case 
                if DEBUG:
                    print("4 cross points at crossing %s (%s) with %s (%s)" % \
                          (self.name(), repr(key), face.mesh.name(), repr(face.key)))                                            
            elif len(result) == 3:    #3 cross points
                #points 0 and 1 or 1 and 2 are from the same face:
                #(because we first cross edges A with face B, and 
                #then face A with edges B).
                #
                #Heuristics: put the single point from the other face
                #between the two that belong to the same face.
                #(If we will not give this way a chance to this single
                #additional edge to be assigned, they will often break
                #the prev:next sequence, used to find topological sequence
                #of the found cross points):
                if result[0].edge.mesh is result[1].edge.mesh:
                    #points 0 and 1 are from the same face:
                    r = result[0].vert() - result[1].vert()
                    if r.length > EPSILON: #put this single in the middle:
                        result = [result[0],result[2],result[1]]
                else:
                    #points 1 and 2 are from the same face:
                    r = result[1].vert() - result[2].vert()
                    if r.length > EPSILON: #put this single in the middle:
                        result = [result[1],result[0],result[2]]
            else: pass #len in 1,2: nothing special

            if len(result) > 1: #we will not append the single point to results
            
                #assign the found points into a topological chain:
                prev = result[0]
                for cp in result[1:]:
                    prev.Assign(cp)
                    cp.Assign(prev)
                    prev = cp
                    
                #Special case, when we have 3 cross points:
                #we will try to start collecting data from it.
                #So - let's put it into the unusual place: as the first
                #because the getLoop() function always start with the first
                #all the other points are placed at the end of cpoints[]
                if len(result) == 3: 
                    cp = result[1]
                    if cp not in _cpoints: _cpoints.insert(0,cp)
                    #because result[1] is already on the list, it will be 
                    #discarded in the loop below, and only the items from
                    #the same face will be added at the end of cpoints...

                #store the normal pair in the cpoints list:p
                for cp in result:
                    if cp not in _cpoints: _cpoints.append(cp)
                            
            if DEBUG > 8: #beware tab position: this will print also the discarded ones 
                for cp in result: print(cp)

        return result
    
class CFace:
    """Represents a triangle face, element of the mesh"""
    #instance fields:
    #src => MFace:        the Blender's face object. Because it may be a 
    #                    quad - two CFaces may refer to the same MFace.
    #                    They will differ by the key value
    #mesh =>CMesh        the parent object, that:
    #                                     (mesh.faces[self.key] is self) == True
    #key => (3 int):    the face id (matches the key in CMesh.faces dictionary).
    #                    It is a tuple of face vertices ordinals. It determines
    #                    direction of the face.
    #min =>[3 floats]:    minimum x,y,z face coordinates
    #max =>[3 floats]:    maximum x,y,z face coordinates
    #
    #    private fields
    #__edges=>{3 Edges}:a dictionary of 3 Edge instances. The face edges.
    #                    The key of this dictionary is a tuple of 2 vertex
    #                    ordinals. It should match a key in the parent 
    #                    CMesh.__neigbours dictionary key.
    #                    At the begining all elements are set to None. It is 
    #                    filled with objects when face is suspected to have 
    #                    a cross section with a face from the other mesh.
    #__boundary=>Bool:    True, when face contains a boundary edge. Used by
    #                    HasBoundaryEdge() function, calculated on first demand
    #__normal=>Vector:    normal to this face. Used by normal() function, calcu-
    #                    lated on first demand
    def __init__(self, cmesh, mface, key):
        """Creates a new traingular face, representing a part of a MeshFace
            Arguments:
                cmesh:    parent object (CMesh)
                mface:    a source face, from the original mesh (MeshFace)
                key:    a tuple of 3 vertex ordinals. They should be
                        contained in mface.ed
        """
        self.src = mface
        self.mesh = cmesh
        self.key = key
        v0,v1,v2 = self.vert(0),self.vert(1),self.vert(2)
        self.min = [min(v0.x,v1.x,v2.x)-BOX_EPSILON, \
                    min(v0.y,v1.y,v2.y)-BOX_EPSILON, \
                    min(v0.z,v1.z,v2.z)-BOX_EPSILON]
        self.max = [max(v0.x,v1.x,v2.x)+BOX_EPSILON, \
                    max(v0.y,v1.y,v2.y)+BOX_EPSILON, \
                    max(v0.z,v1.z,v2.z)+BOX_EPSILON]
        #__edges - empty places, for begining. Just to keep their keys
        self.__edges = {}
        for k in [(key[0],key[1]),(key[1],key[2]),(key[2],key[0])]:
            self.__edges[k] = None
            
        #currently unused:
        self.__boundary = None #will be calculated on first demand
        self.__normal = None #will be calculated on first demand
        
    def vert(self, index):
        """Returns one of the face's vertices (a Vector, in world coordinates)
            Arguments:
                index:    the vertex index on the face (0, 1, or 2)
            
            The index==i selects the mesh vertex having ordinal==face.key[i] 
        """
        return self.mesh.vert(self.key[index])

    def Assign(self, edge):
        """Assigns an edge to the face
            Arguments:
                edge:    an edge (CEdge), that has be placed in previously 
                        empty place in face's edge dictionary
        """
        key = edge.key
        #one of two faces that uses this edge has it under reversed tuple key:
        if key not in self.__edges: key = edge.altkey()
        
        if self.__edges[key] is None:
            self.__edges[key] = edge
        elif self.__edges[key] is not edge: 
            if DEBUG > 5:
                print("Attempt to reassign edge %s, in face %s" % \
                                                    (repr(key), repr(self.key)))

    def Intersect(self, face):
        """Intersects a face with another face, from different mesh
            Arguments:
                face:    a face (CFace) from different mesh, to be tested
            
            Returns a list of found crossed points (CPoints). The list may be 
            empty, or contain 1 or 2 points. Points found are the intersections
            of this face EDGES with the surface of the other face, ONLY!
        """
        #first, discard operation when the spatial limits are separate:
        for i in range(0,2):
            if (self.min[i] > face.max[i] or self.max[i] < face.min[i]): 
                return [] #no cross points
        #if the faces are suspected to have a cross point - check every edge:
        cpoints = []
        for k in self.__edges.keys():
            if not self.__edges[k]: self.__edges[k] = self.mesh.GetEdge(k)
            result = self.__edges[k].Intersect(face)
            if result: 
                cpoints.append(result)
            
        return cpoints

    
class CEdge:
    """Represents an edge - element of the mesh"""
    #instance fields:
    #src => MEdge:        the Blender's edge object. This field may be == None
    #                    for the diagonal edges, created solely for this 
    #                    calculation for quad MeshFaces. Such temporary diagonal
    #                    join two triangle Faces. The src attribute of these
    #                    faces refers to the same quad MeshFace.
    #mesh =>CMesh        the parent object, that:
    #                                 (mesh.__edges[self.key] is self) == True
    #key => (2 int):    the edge id (matches the key in CMesh.__edges dictionary).
    #                    It is a tuple of edge vertices ordinals. It determines
    #                    direction of the edge.
    #org => Vector:        beginning of the edge (world coordinates)
    #ray =>    Vector:        a vector from beginning to the end of the edge
    #boundary => Bool:    True, when it is a boundary edge.
    #
    #private instance fields:
    #__results=>{CPoint}: a dictionary of calculation results, that were already
    #                    performed. Its keys are the keys of the tested faces.
    #                    Presumably, most of the values will be None.
    def __init__(self, mesh, medge, key, v1, v2):
        """Creates a new edge
            Arguments:
            mesh:    the mesh (CMesh) that contains this edge
            medge:    the source edge (a MeshEdge) - may be None for diagonals
            key:    the tuple of two mesh vertex ordinals (integers)
                    that is used as a key in parent's CMesh.__edges dictionary
            v1:        the begining of the edge (a Vector, in worldspace)
            v2:        the end of the edge (a Vector, in worldspace)
            Be sure, that v1 is really the vertex(key[0]), and v2 - vertex(key[1])
        """
        self.mesh = mesh
        self.src = medge
        self.key = key
        self.org = v1
        self.ray = v2 - v1
        self.__results = {}
        self.boundary = False
        
    @staticmethod
    def Normalize(key):
        """Returns a canonical form of a edge key - smaller ordinal first
            Arguments:
                key:    a tuple of two vertex ordinals. They may be in any
                        order
            
            This function is used by CMesh to unify the edge keys, requested
            in a reversed form by faces that share the edge.
        """
        if key[0] < key[1]:    return key
        else: return (key[1],key[0])
    
    def altkey(self):
        """Returns an alternated (reversed) form of the edge key.
        Required by CFace, because it stores their edges in a non-canonical
        form. The order of vertex ordinals in keys of their local edge dictionary
        reflects the local face direction, not the normalized edge key. 
        """
        return (self.key[1], self.key[0])

    def Intersect(self, face):
        """    Calculates the intersection point of this edge and a face.
            Arguments:
                face:    a triangular face (CFace), that belongs to another mesh
                
            Returns a CPoint, if suceeds, or None, when there is no cross point.
            Stores the result in the internal cpoints dictionary.
        """
        if self.ray.length < EPSILON : return None #this edge hardly exists!
        #if we have already meet this face: return the result
        if face.key in self.__results: 
            return self.__results[face.key]
            #if p is None or p.disconnected(): return None #skip over discarded points
            #else: return p
        else: #it has been not tested, yet
            result = None 
            p = intersect_ray_tri(face.vert(0),face.vert(1),face.vert(2), self.ray, self.org)
            if p:
                v = (p - self.org) #result vector
                if v * self.ray > 0: #the ray and the result in the same direction
                    #is the point inside the segment?
                    if v.length <= (self.ray.length + EPSILON) : 
                        result = CPoint(self,face, v.length/self.ray.length)
            #we will also remember the cases which have failed:
            #(just to not repeat them:)
            self.__results[face.key] = result
            return result
        
class CPoint:
    """Represents a cross point of an edge of mesh A and a face of mesh B"""
    #instance fields:
    #edge => Edge:        the edge that contains this cross point
    #face => Face:        the face that contains this cross point
    #                    Beware: the edge the face always belong to different
    #                    CMeshes!
    #t => float:        the location on the edge (0.0-at the beginning, 1.0-at
    #                    the end)
    #prev: CPoint        previous point on the crossing line
    #next: CPoint        next point on the crossing line
    #
    #Beware: during first phase of the calculations - finding the crossing 
    #points, some points may have the next or prev field set to None.
    #The general arrangement of prev->prev->prev or next->next->next between
    #the cross points may be reversed in some places. This is checked and fixed 
    #during second phase of the calculations - the cross point arrangement -
    #by the getTail() global function.
    #In fact, the names "prev" and "next" are somewhat improper, They are,
    #in fact, the references to the neighbors, but the direction is unknown for
    #most of the CPoint instance's "life".
    def __init__(self, edge, face, t):
        """Creates a new instance of cross point
            Arguments:
            edge:    the edge that has this cross point (a CEdge)
            face:    the face that has this cross point (a CFace)
            t:        placement of the cross point (float: 0.0 means
                    'at the begining of the edge', 1.0 means 'at the end')
        """
        self.edge = edge
        self.face = face
        self.t = t
        self.next = self.prev = None #it will be set later
    
    def index(self):
        """Returns an ordinal of this cross point, or None for not registered
            Use for diagnostics or debugging. Some points can be not registered
            in the prent CMesh.cpoints list, because they duplicated the ones
            that are already registered.
        """
        return self.edge.mesh.cpindex(self)
        
    def __repr__(self):
        """Represents content of the instance in a human-readable form
            For the diagnostics and debugging purposes
        """
        #some shortcuts, first
        v = self.vert()
        if self.prev : p = self.prev.index()
        else: p = None
        if self.next : n = self.next.index()
        else: n = None
        if self.edge.src : type = 'Norm'
        else: type = 'Diag'
        #and finally - the result
        result =     "%s: (%1.2f, %1.2f, %1.2f) at %1.2f of '%s' %s (%s) x '%s' %s," % \
                    (repr(self.index()), v.x, v.y, v.z, self.t, \
                     self.edge.mesh.name(), repr(self.edge.key), type, \
                     self.face.mesh.name(), repr(self.face.key))
        if p and n :
            result += "btw: (%s, %s)" % (repr(min(p,n)),repr(max(p,n)))
        else:
            result += "btw: (%s, %s)" % (repr(p),repr(n))
        return result
        
    def Assign(self, cpoint):
        """Assigns a cpoint at free connection point (prev or next)
            Arguments:
                cpoint:    another cross point (CPoint) that has to be connected
        """
        if not cpoint: return #nothing to do
        if self.next is cpoint or self.prev is cpoint: return #already done
        else:
            if not self.next: self.next = cpoint
            elif not self.prev: self.prev = cpoint
            elif DEBUG > 5:
                #sometimes it may happen, when edge from one mesh crosses exactly
                #edge from the other mesh 
                print("Attempt to reassign %s, already assigned to (%s, %s), to %s" % \
                                        (repr(self.index()), repr(self.prev.index()), \
                                         repr(self.next.index()), repr(cpoint.index())))
            else: pass
    
    def GetOpposite(self, cpoint):
        """Returns an opposite cross point to the given one
            Arguments:
                cpoint:    one of two cross points: next or prev
        """
        if cpoint is self.next : return self.prev
        elif cpoint is self.prev: return self.next
        else:    
            if DEBUG > 5: #can happen for points that cross an edge from second mesh
                print("Cross point %d is not referenced by %d" % \
                                                (self.index(), cpoint.index()))

    def vert(self):
        """Returns the location of this point (a Vector, in worldspace)"""
        return self.edge.org + (self.t * self.edge.ray)
    
    def IsTemporary(self):
        """    Returns True, when this point lies on a temporary edge
        
            Some edges of the CMesh do not exists in the source Mesh - they
            are face diagonals, artifically created on quad faces. Such edges
            are temporary - created only for this crossing calculation. 
            Such cross points are usually not wanted in the final result.
        """
        return (self.edge.src is None)  #such edges do not have the source 
                                        #MEdge assigned.
    
    def BelongsTo(self, cmesh):
        """    Returns True, when this point belongs to this mesh
            Arguments:
                cmesh:    mesh (CMesh) to be tested
            
            Cross point belongs to the mesh, that is the owner of the edge that
            has been crossed, not the face.
        """
        return (self.edge.mesh is cmesh)

####module functions--------------------------------------------------------
def show(text, kind='DEBUG'):
    """Shows a popup message
        Arguments:
            text:    message text
            kind:    optional. kind of the information
                    (enumeration like from bpy.types.Operator.report())
    """
    #implemented by MessageReporter class (see below):
    bpy.ops.help.report('INVOKE_DEFAULT', icon=kind, msg=text)
        
def getTail(cpoints, cpoint):
    """Returns a sequence of cross points, that begins with the given point
        Arguments:
            cpioints:    the list of the crosspoints that will be searched;
            cpoint:        the the begin of the sequence - MUST NOT be in cpoints,
                        but cpoint.next or cpoint.prev - should be
        
        This function returns a list containing all successors of the cpoint,
        that are - topologically - on the same side.
        The side does not need to be specified in parameters, because this
        function is    removing from cpoints every element, that is placed in 
        the result list.
        getTail() always tries to find the sequence that begins with the 
        cpoint.next. When you will call it second time - it has no choice, but
        return the sequence that begins with cpoint.prev. 
    """
    result = []
    next = None #if cpoint has no next nor prev in cpoints, this will ensure,
                #that an empty list will be the result
    
    #check out, which direction we will take:
    if cpoint.next in cpoints:         next = cpoint.next
    elif cpoint.prev in cpoints:     next = cpoint.prev
    
    #the cross points reference each other via next and prev without any
    #special order (because they were found randomly). It may happen that
    #the cpoint.prev is the cpoint.prev.prev - when two neighbour cross points
    #have been created at reverse. One thing is sure: the opposite cross point
    #is one of the prev,next pair, so we have utilize the GetOpposite() function
    #to obtain from the next a point that is not the cpoint!
    while next in cpoints:
        cpoints.remove(next) #ensure, that this point will not be used again.
        
        #discard multipled points (they may happen in regular shapes, where 
        #cross points are exactly on face's boundary. For example: crossing of  
        #two identical cubes, where one was moved away by half of their size) 
        #if (next.vert()-cpoint.vert()).length > EPSILON: 
        result.append(next)        
        #proceed to the next one:     
        #give me the next that is on the opposite side than the one (cpoint)
        #that we just have came, and mark actual next as the cpoint:
        cpoint,next = next,next.GetOpposite(cpoint)
    return result

def getLoop(cpoints):
    """Returns from the cpoints points, that forms a continous sequence
        Arguments:
            cpoints: the sequence (a list of CPoints) to be sought
            
        This function removes every matching point from the CPoints seqence, and
        places it in the result list. When it has finished its run, the cpoints
        sequence is empty or contains a bunch of points that belong to another 
        loop. You should repeat call to this function, until you will collect
        all the loops.
    """
    result = []
    if cpoints : #if there is anything to do:
        point = cpoints[0] #we will take an arbitrary point to start with:
        cpoints.remove(point) 
        result.append(point)
        left = (getTail(cpoints,point)) # the "next" part of the loop
        right = getTail(cpoints,point) # the "prev" part of the loop
        
        if left : result.extend(left)
        if right: 
            right.reverse()
            right.extend(result)
            result = right

    return result

def intersect(A,B):
    """Calculates intersection of two mesh objects
        Arguments:
            a:    the first mesh (CMesh)
            b:    the second mesh (CMesh)
        
        Returns a list of the cross points loops found. Every element is a list
        of cross points (CPoint) objects, that represent a single topological 
        loop. These loops may be opened or closed.
    """
    global _cpoints
    _cpoints = [] #reset this class collection...
    for i in A.faces.keys():
        for j in B.faces.keys():
            A.Intersect(i, B.faces[j])
    result = []        
    cpoints = _cpoints[:]
    while cpoints:
        result.append(getLoop(cpoints))
    return result

def create(loop, object, allEdges=False, omit=None):
    """creates a new edge loop in the mesh of given object
        Arguments:
            loop:        list of cross points (CPoint)
            object:        object, which mesh will be used to add the cross edge
            allEdges:    optional. Use all cross points, also the temporary 
                        points that    belong to diagonals of quad faces (Boolean)
            omit:        optional. Cross points that lie on edges of this CMesh
                        should be omitted during drawing
    """
    m = object.matrix_world.copy()
    m.invert() #transformation to object's space
    mesh = object.data #mesh, that will be extended by the new loop
    verts = [] #temporary list of vertices (Vector, object's local space)
    edges = [] #temporary list of edges = two element lists of vertex ordinals
    prev = None #helper: a previously processed CPoint.
    i = 0        #actual vertex number
    base = len(mesh.vertices)     #ordinal of the first vertex, that will be added
                                #to the mesh. (We have use the absolute ordinals)
    for cp in loop:
        #if it is not a point on a non-existant edge, or from mesh to be omitted:
        if     (not cp.IsTemporary() or allEdges) and not cp.BelongsTo(omit):
            vertex = m * cp.vert()
            if prev is None: #Init: we are looking for the first valid point
                r = loop[-1].vert() - cp.vert() #distance from loop ends
                                                #it is = 0 for one element list
                if r.length > EPSILON: #if end and start point do not overlap:
                    verts.append(vertex.to_tuple())
                    prev = cp
                    if DEBUG > 5: print(cp) 
                else: pass #loop ends overlap, proceed to the next cp
            else: #Normal: prev exists!
                r = prev.vert() - cp.vert() #distance from the previous point
                if r.length > EPSILON:
                    verts.append(vertex.to_tuple())
                    i += 1
                    edges.append((base+i-1, base+i))
                    prev = cp
                    if DEBUG > 5: print(cp)
    
    if len(verts) > 1: #if there is sany segment to create:
        #if the loop is a closed loop: add closing edge
        if not (loop[0].edge.boundary or loop[-1].edge.boundary):
            edges.append((base+i, base)) #add the closing segment
            
        #deselect previously selected vertices
        #for v in mesh.vertices: v.select = False
        #and, finally, add new edges:
        count = len(verts)
        mesh.vertices.add(count)
        for v in mesh.vertices[-count:]: 
            v.co = verts[v.index - base]
        count = len(edges)
        base = len(mesh.edges)
        mesh.edges.add(count)
        for e in mesh.edges[-count:]: 
            e.vertices = edges[e.index - base] 
        mesh.update()
        
    
#--- ### Blender Operators
class MessageReporter(bpy.types.Operator):
    ''' Operator created just to have a global method bpy.ops.help.report() 
        for displaying messages to the user in a popup.
    '''
    bl_idname = "help.report"
    bl_label = "Display Message"
    bl_description = "Displays a message on the Info area header"
    
    #--- parameters
    icon = EnumProperty(items = [('DEBUG', 'Debug', 'Debugging message'), 
                                ('INFO', 'Info', 'Informational message'), 
                                ('ERROR', 'Error', 'An error message')
                                ], name = "Type", description = "The kind of the message", default = "DEBUG")
    msg = StringProperty(name="Message", description="Text that will be displayed") #you can use the newline characters, there!
    
    
    #--- Blender interface methods
    def draw(self, context):
        layout = self.layout
        layout.label(self.bl_label + ":", icon=self.icon)
        for txt in self.msg.split("\n"):
            layout.label(txt)
        
    def invoke(self, context, event):
        if self.icon == 'DEBUG':
            return self.execute(context)
        else:
            span = max(list(map(len, self.msg.split("\n"))))*PIXELS_PER_CHAR #maximum length of single row
            span = max(len(self.bl_label)*PIXELS_PER_CHAR + PIXELS_PER_ICON, span) #estimate required popup size
            return context.window_manager.invoke_popup(self, width=span)
    
    def execute(self, context):
        if self.icon == 'DEBUG':
            print(self.bl_label + ":",self.msg)
        else:
            self.report(self.icon, self.msg)
        return {'FINISHED'}
    
#the only reason of existence for this operator is that the "interactive" operators,
#which displays its parametres in Tool Properties pane, have to finish in the same
#mode, in which it has started its execution. 
#In this case we start in Object Mode, but finish in Edit Mode.     
class IntersectObjects(bpy.types.Operator):
    ''' Create an edge of intersection of active object with another one 
    '''
    bl_idname = "object.intersection"
    bl_label = "Intersection"
    bl_description = "Adds to active object (to its mesh) an edge of intersection with another mesh object"
    #--- parameters (copy of the IntersectMeshes parameters)
    use_both = BoolProperty(name="Use both meshes", description="Include points found on the edges of the second mesh", default=True)
    use_selected = BoolProperty(name="Use selected faces", description="Restrict processed area to the selected faces, only (ignored, when nothing is selected)", default=True)
    use_diagonals = BoolProperty(name="Use diagonals", description="Include points found on the diagonals of quad faces", default=False)
        
    #--- Blender interface methods
    @classmethod
    def poll(cls,context):
        return (context.mode == 'OBJECT' and context.object and context.object.type == 'MESH')
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self,"use_selected")
        layout.prop(self,"use_both")
        layout.prop(self,"use_diagonals")
        
    def invoke(self, context, event):
        #similar check, like in IntersectMeshes, but different way of communication:
        sel = context.selected_objects
        
        if len(sel) != 2:
            msg = "Select two mesh objects ({0} selected)"
            msg = msg.format(len(sel))
            self.report(type={'ERROR'}, message=msg)
            return {'CANCELLED'}
        
        if sel[0].type == sel[1].type == 'MESH':    
            if DEBUG: print("\nObjects that will be crossed: \n%s \nand \n%s." % (sel[0].name,sel[1].name))            
            return bpy.context.window_manager.invoke_props_dialog(self, width = 160)
        else:
            self.report(type = {'ERROR'}, message="Select two meshes to get their intersection")
            return {'CANCELLED'}
    
    def execute(self, context):
        #bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.intersect_meshes('INVOKE_DEFAULT', use_both = self.use_both, use_selected = self.use_selected, use_diagonals = self.use_diagonals)
        return {'FINISHED'}
        
class IntersectMeshes(bpy.types.Operator):
    ''' Calculates intersection of two selected mesh objects or a single mesh 
        Places the result as a new edge(s) in the mesh of active object
    '''
    bl_idname = "mesh.intersect_meshes"
    bl_label = "Intersection"
    bl_description = "Create an intersection (one or more edge loops) of selected and unselected faces (hidden elements are omitted)"
    bl_options = {'REGISTER', 'UNDO'} #Set this options, if you want to edit in Tools pane the properties of this operator
    
    #--- parameters
    use_both = BoolProperty(name="Use both faces", description="Include points found on the edges of the unselected faces", default=True)
    use_selected = BoolProperty(name="Use selected faces", description="Restrict processed area to the selected faces, only (ignored, when invoked in Edit Mode)", options={'HIDDEN'}, default=True)
    use_diagonals = BoolProperty(name="Use diagonals", description="Include points found on the diagonals of quad faces", default=False)
    skip_hidden = BoolProperty(name="Skip hidden faces", description="True, when in Edit Mode (single mesh cut), False when in Object Mode (two objects cut)", options={'HIDDEN'}, default=True)
    
    #--- Blender interface methods
    @classmethod
    def poll(cls,context):
        return (context.mode == 'EDIT_MESH' or context.mode == 'OBJECT') #It is invoked in Object mode by the IntersectObjects operator 
    
    def invoke(self, context, event):
        #input validation:
        #list(filter(lambda f: f.select, a.data.polygons))
        if context.mode == 'EDIT_MESH':
            self.skip_hidden = True
            self.use_selected = True

            a = context.active_object
            bpy.ops.object.mode_set(mode='OBJECT')
            if not list(filter(lambda f: f.select, a.data.polygons)): #Nothing selected?
                self.report(type = {'ERROR'}, message="Select the faces you want to intersect with the unselected ones")
                return {'CANCELLED'}
            return self.execute(context)
        else:
            self.skip_hidden = False
            sel = context.selected_objects
            if len(sel) != 2:
                if len(sel) == 1:
                    verb = "is"
                else:
                    verb = "are"
                    
                msg = "This operation requires exactly two selected objects ({0} {1} selected).\n - Switch to Object mode, and select two objects (the 'tool' mesh and this one).\n - Switch back to Edit Mode, and call again this command."
                msg = msg.format(len(sel), verb)
                show(msg, kind='ERROR')
                return {'CANCELLED'}
    
            if sel[0].type == sel[1].type == 'MESH':
                if DEBUG: print("\nObjects that will be crossed: \n%s \nand \n%s." % (sel[0].name,sel[1].name))            
                return self.execute(context)
            else:
                msg = "This operation requires two mesh objects.\nThe second object, you have selected in Object Mode,\nis of different kind ({0})."
                if context.active_object == sel[0]:
                    msg = msg.format(sel[1].type)
                else:
                    msg = msg.format(sel[0].type)
                show(msg, kind='ERROR')
                return {'CANCELLED'}
        
        
    def execute(self, context):
        #fmt="properties: use_selected={0}, use_both={1}, use_diagonals={2}"
        #show(fmt.format(self.use_selected, self.use_both, self.use_diagonals))

        #if we are in the edit mode: switch into 'OBJECT' mode 
        #(execute() can be called continously from the Tool Properties pane):
        global _cpoints
        if context.mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')#bpy.ops.object.editmode_toggle()
            
        #in object mode we can idenify our objects:
        a = context.active_object
        
        if self.skip_hidden: #Invoked from IntersectMeshes (single mesh cut: selected faces against the unselected) 
            A = CMesh(a, 1, True)
            B = CMesh(a, -1, True)
        else: #Invoked from IntersectObjects 
            #b: the second one
            sel = context.selected_objects
            if a == sel[0]: b = sel[1] 
            else: b = sel[0]
                
            A = CMesh(a, self.use_selected, False)
            B = CMesh(b, self.use_selected, False)

        start = time()
        
        result = intersect(A,B) #main operation!
        
        if DEBUG: 
            seconds = time() - start
            print("\nIn %1.5f seconds created: %d edges, found: %d raw cross points\n" % \
                                        (seconds, len(A._CMesh__edges), len(_cpoints)))
        if DEBUG > 8: #let's look at the results:
            print("Raw result list:")
            for p in _cpoints:
                print(p)
            
            print("\nResult:")
        
        mesh = a.data #this mesh will be extended by the calls to create() function ....

        base = len(mesh.vertices) #first newly added vertex will have this index.
        i = 0
        
        for l in result:
            i += 1
            if DEBUG > 5: 
                print("Loop %d" % i)
                print("  all points ....")
                for p in l : print(p)
                print("  ... and points selected to create the edge:")
                
            #create a loop:    
            if self.use_both: 
                create(l, a, self.use_diagonals)
            else: 
                create(l, a, self.use_diagonals, B)
                
        if result: #any other method of unselecting did not work here: 
            bpy.ops.object.mode_set(mode='EDIT')#bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')#bpy.ops.object.editmode_toggle()
                
        #select the newly created vertices:
        for v in mesh.vertices: v.select = (v.index >= base)
                
        #enter edit mode (to let the user to evaluate the results):
        bpy.ops.object.mode_set(mode='EDIT')#bpy.ops.object.editmode_toggle()
            
        if not result:
            show("No intersection found between this and the other selected object.", kind='INFO')
                
        return {'FINISHED'}
    
def menu_object_draw(self, context):
    if (context.object and context.object.type == 'MESH'):
        self.layout.operator_context = 'INVOKE_REGION_WIN'
        self.layout.operator(IntersectObjects.bl_idname, "Intersect")
    
def menu_mesh_draw(self, context):
    if (context.object and context.object.type == 'MESH'):
        self.layout.operator_context = 'INVOKE_REGION_WIN'
        self.layout.operator(IntersectMeshes.bl_idname, "Intersect")

#--- ### Register
def register():
    register_module(__name__)
    #bpy.types.VIEW3D_MT_edit_mesh_edges.prepend(menu_draw)
    #bpy.types.VIEW3D_MT_object.prepend(menu_draw)
    bpy.types.VIEW3D_MT_object_specials.prepend(menu_object_draw)
    bpy.types.VIEW3D_MT_edit_mesh_specials.prepend(menu_mesh_draw)
    
def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_mesh_draw)
    bpy.types.VIEW3D_MT_object_specials.remove(menu_object_draw)
    #bpy.types.VIEW3D_MT_edit_mesh_edges.remove(menu_draw)
    #bpy.types.VIEW3D_MT_object.remove(menu_draw)
    unregister_module(__name__)
    
if DEBUG > 0:
    print("object_intersection.py: new version loaded!") #just to be sure, that we are testing what we should
    
if __name__ == '__main__':
    register()
