# -*- coding: utf-8 -*-

'''
2012/11/06 v0.17, t26
  + updated to work on Blender 2.64 in which mesh and face system has 
    been changed drastically.
  + changed simply "mesh.faces" to "mesh.tessfaces".
    (This information was provided kindly from BuildingTheWorld in 
    YouTube, special thanks.)
2012/01/08 v0.16, t25
  + added a GUI in Scene tab.
  + added extra log feature to log the code line in which an error 
    happened.
2012/01/07 v0.15, t24
  + a really rush job to update the script for Blender 2.6x.
  + the detail change points are:
    + updated to work on Python 3.2.
    + removed the old GUI part.
    + updated to use mesh.vertices of Blender 2.6x.
    + use sort(key=lambda x: x[0]) for sorting.
    + use new Vector, Matrix, .cross, .normalized, and .angle in mathutils 
      module.
    + updated PointsGridManager and FaceAddingManager completely.
  + it still depends on Blender Vertex deeply.
  + it doesn't have GUI yet.
2009/01/18 v0.14, t23
  + added a new UI mode which allows you to use the script from the 
    menu Mesh in Blender. You can set the parameters quickly in the new  
    popup block. 
  + can switch the UI mode. The popup UI will be display if the 3D 
    window is in EditMode, and the script GUI will be display in 
    otherwise.
2009/01/11 v0.13, t21
  + Corrected the function CalcAverageNormal. The algorithm is based 
    on Lagrange's Lambda Method minimizing of sum(ax+by+cz)^2, which 
    is the real minimization of the distances between vertices and the 
    center, instead of least squares using ax+by+cz=1 in v0.12 or older.
2008/11/16 v0.12, t19
  + The script name was changed and it's going to be called Point 
    Cloud Skinner 1 Umbrella instead of Point Cloud to 3D Mesh, 
    because another way of skinning has been created and it's called 
    Point Cloud Skinner 2 Carapace.
  + A GUI was added to make it easy to setup, using the module Blender
    GUI Provider. The module code has been appended to t15 simply.
  + TimeProfiler was created to measure process time, and the code 
    was included into t19.
  + PointsGridManager has been improved to collect vertices faster by
    using hash values for keys of the dictionary that contains the 
    grid cells.
2008/02/03 v0.11, t15
  + created PointsGridManager class to manage a lot of vertices with a 
    meshed grid. It allows you to gather vertices that are located in 
    a distance with less time consumption.
  + changed the process of checking the internal angles. Now it can 
    check more correctly if the triangle outside has shaper angle than 
    the triangle around center, and can avoid discarding the vertices.
2008/01/18 v0.10, t14
  + changed the script to use average normal and added a new parameter
    gb["MaxDistForAxis"] to set the distance in which it gathers 
    vertices to decide the average normal.
  + fixed the bug that causes an error in the process of checking the 
    internal angles. It was solved by checking the length of NeigVert2
    - NeigVert1.
2008/01/17 v0.9, t13
  + The upgrade for checking the internal angles in t12 has two
    problems and they could make a shape triangle because of missing
    to reduce unnecessary vertices, and it has been fixed in t13. (One
    of two was solved by enabling the vertex if its neighbor vertex is
    in unable region in SomeEndVerts state, and the other was by 
    enabling the vertex if it and its both neighbor vertices form a 
    shaper triangle.)
  + It has been found that the fixes above cause another problem near
    the edges of the surface with making a shape triangle, and it has
    been also fixed.
2008/01/16 v0.8, t12
  + upgraded the functionality of checking the adjacent 2 triangles and
    can reorganize the triangles into good shapes.
  + modified the way of checking the internal angles using a new concept.
    It can avoid the intersection of faces that will come from reducing
    the vertices by the checking.
2008/01/06 v0.7, t10
  + upgraded the functionality of checking the internal angles and can 
    check if the angle is too small or large.
2007/12/10 v0.6, t7
  + added the functionality to avoid making intersection of faces, but 
    some faces still have intersection in a noisy point cloud.
    (To avoid the intersection, it looks at faces that have been already 
    made, and such a face is called a face-end face in the script. First 
    it searches for face-end edges that are just connected to the center 
    vertex and groups the vertices by the edges. Next in each group it 
    searches for the other face-end edges and discards the vertices that 
    are hidden by the edges. And it makes faces out of the left vertices.)
  + haven't yet upgraded the functionality of checking the internal 
    angles for the new version, so removed the previous codes.
  + haven't yet upgraded the functionality of checking the adjacent
    triangles for the new version, so commented out the codes now.
2007/11/29 v0.5, t6
  + created FacesManager class to manage faces. It provides you with an 
    easy way to find the faces that include a specified vertex. The 
    purpose is to find the already made faces to avoid making overlapping 
    faces. 
2007/11/29 v0.4, t5
  + separated the algorithm code in MakeFacesAround into some smaller 
    methods because the code length started to be long. Also changed the 
    way to send data to those methods and now use Data class to send it.
2007/11/22 v0.3, t4
  + can check if angles between adjacent 2 vertices are acceptable.
  + can check if adjacent 2 triangles have appropriate shapes.
  + changed the way of sending faces' information to downward 
    functionalities in the algorithm and now treat it in the same unified 
    data structure everywhere.
2007/11/18 v0.2, t3
  + the algorithm has not changed but a few codes changed to make it easy 
    to read, for example changing into gb["*"] style, compacting for loop
    codes.
2007/11/16 v0.1, t2
  + t1 code was separated and t2 started newly to concentrate on the 
    development for skinning a point cloud.
  + implemented a simple algorithm to make faces around each vertex.
'''

bl_info = {
    "name": "Point Cloud Skinner",
    "author": "Hans.P.G.",
    "version": (0, 17, 26),
    "blender": (2, 6, 4),
    "api": 35853,
    "location": "Properties space > Scene tab > Point Cloud Skinner panel",
    "description": "Skin a point cloud.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


#******************************
#---===Parameter Settings (for Temporary Use)===
#******************************

ui = {}
ui["TargetObject"] = "Plane"
ui["DistForSearch"] = 1.0
ui["DistForAxis/d"] = 2.0
ui["GridSize/d"] = 3.0


#******************************
#---===Import declarations===
#******************************

from math import *
from copy import *

import bpy
from mathutils import *


def main():
    
    gb["TargetObject"] = ui["TargetObject"]
    gb["MaxAroundDist"] = ui["DistForSearch"]
    gb["MaxDistForAxis"] = ui["DistForAxis/d"] * gb["MaxAroundDist"]
    gb["GridSize"] = [ui["GridSize/d"] * gb["MaxAroundDist"]] * 3
    gb["IgnoreErrors"] = True
    
    print("-----Start-----")
    SkinVerts() # main function of skinning
    print("-----Log-----")
    print(gbLog)
    print("(If you have trouble, please send this log to the developer.)")


#******************************
#---===Global parameters===
#******************************

gb = {}
gb["TargetObject"] = "Plane" # Object name
gb["MaxAroundDist"] = 0.1
gb["MaxDistForAxis"] = 0.2
gb["MaxAroundCount"] = 10
gb["MinVertsAngle"] = 25
gb["MaxVertsAngle"] = 135
gb["GridSize"] = [0.3] * 3
gb["PrecisionLevel"] = 2
gb["TargetVertsMode"] = True # F: skin all vertices, T: skin selected vertices
gb["IgnoreErrors"] = True

gbLog = {}


#******************************
#---===Skin vertices===
#******************************

def SkinVerts():
    
    # Reset log data
    gbLog["TargetVerts"] = 0
    gbLog["MadeFaces"] = 0
    gbLog["FewVertsCases"] = 0
    gbLog["FullFacesCases"] = 0
    gbLog["TooSmallVertsAngles"] = 0
    gbLog["TooLargeVertsAngles"] = 0
    gbLog["ModifiedTriangles"] = 0
    gbLog["Errors"] = 0
    gbLog["ErrorLine"] = []
    gbLog["Warnings"] = {"NZ1": 0, "NZ2": 0, "NZ3": 0}

    # Get mesh instance
    try:
        object = bpy.data.objects[gb["TargetObject"]]
        lcMesh = object.data
    except:
        raise AttributeError("Please specify the name of a Mesh object.")
    
    if object.mode != 'OBJECT':
        raise AttributeError("Please toggle to Object Mode.")

    # PointsGridManager initializes Grid from the existing vertices
    lcGridMana = PointsGridManager(gb["GridSize"])
    lcGridMana.import_many(lcMesh.vertices)
    lcGridMana.precision_level = gb["PrecisionLevel"]
    
    # FacesManager initializes Verts from the existing faces
    lcFaceMana = FaceAddingManager()
    lcFaceMana.import_from_mesh(lcMesh)
    
    # Process all vertices
    for enVert in lcMesh.vertices:
        enIndex = enVert.index
        
        if gb["TargetVertsMode"]:
            if not lcMesh.vertices[enIndex].select:
                continue
        
        lcData = ProcessingDataTransfer()
        lcData.Mesh = lcMesh
        lcData.CenterVert = enVert
        lcData.FacesManager = lcFaceMana
        lcData.GridManager = lcGridMana
        
        # Make faces around center vertex
        if gb["IgnoreErrors"]:
            try:
                lcMesh.vertices[enIndex].select = False
                MakeFacesAroundCenterVert(lcData)
                
            except Exception as ex:
                
                gbLog["Errors"] += 1
                
                tb = ex.__traceback__
                while True:
                    if tb.tb_next is None:
                        break
                    tb = tb.tb_next
                gbLog["ErrorLine"].append(tb.tb_lineno)
                
                lcMesh.vertices[enIndex].select = True
                
        else:
            MakeFacesAroundCenterVert(lcData)
        
        gbLog["TargetVerts"] += 1
        
    poly_list = tuple(lcFaceMana.get_faces_to_add_etor())
    FaceCreater.add_by_vertices_raw(lcMesh, poly_list)

class ProcessingDataTransfer:
    def __init__(self):
        self.Mesh = None
        self.CenterVert = None # In form of MVert
        self.GridManager = None
        self.FacesManager = None
        self.VertsAround = None # In form of [MVert, ...]
        self.VertsForAxis = None # In form of [MVert, ...]
        self.ZAxis = None # In form of 3x1 Blender.Vector
        self.XYTransMat = None # In form of 3x3 Blender.Matrix
        self.XYZTransMat = None # In form of 3x3 Blender.Matrix
        self.EndVerts = None # In form of [EndVert, ...]
        self.EndState = None # In form of string
        self.VertGroups = None # In form of [VertsAround, ...]
        self.EndEdges = None # In form of [[MVert, MVert], ...]
        self.MakeFace = None # In form of [T or F, ...]
        self.FaceGroups = None # In form of [Faces, ...]
        self.Faces = None # In form of [[Index, Index, Index], ...]

# Make faces around center vertex
def MakeFacesAroundCenterVert(inData):
    
    # Gather closer vertices around
    if not GatherCloserVertsAroundCenter(inData): return True
    
    # Gather closer vertices around to decide axis
    if not GatherCloserVertsForAxis(inData): return True
    
    # Defind frame to measure angles
    DefindFrameToMeasureAngles(inData)
    
    # Get face-end vertices around and sort them
    if not GetFaceEndVertsAroundCenterAndSort(inData): return True
    
    # Do additional search for vertices outside
    DoAdditionalSearch(inData)
    
    # Sort vertices gathered around
    SortVertsGatheredAround(inData)
    
    # Separate vertices by already existing faces
    GroupVertsByFaceEndVerts(inData)
    
    inData.FaceGroups = []
    for enVertGroup in inData.VertGroups:
        
        # Initialize lcData
        lcData = copy(inData)
        lcData.VertsAround = enVertGroup
        lcData.MakeFace = [True] * len(enVertGroup)
        
        # Gather all face-end edges in each group
        GatherAllFaceEndEdges(lcData)
        
        # Check if angles between adjacent 2 vertices are too small
        CheckIfAnglesAreTooSmall(lcData)
        
        # Discard vertices hidden by face-end edges
        DiscardVertsHiddenByFaceEnds(lcData)
        
        # Check if angles between adjacent 2 vertices are too large
        CheckIfAnglesAreTooLarge(lcData)
        
        # Make faces around simply
        MakeFacesAroundSimply(lcData)
        
        inData.FaceGroups.append(lcData.Faces)
    
    # Combine all of faces that have been made in each group
    CombineFacesInAllVertGroups(inData)
    
    # Check if adjacent 2 triangles have good shapes
    CheckIfTrianglesHaveGoodShapes(inData)
    
    # Extend faces in faces manager
    RegisterFacesToFacesManager(inData)
    
    return True

# Gather closer vertices around
def GatherCloserVertsAroundCenter(inData):
    inCenterVert = inData.CenterVert
    lcGridMana = inData.GridManager
    
    # Gather closer vertices around
    lcVertsAround = lcGridMana.get_vertices_in_distance(inCenterVert.co, gb["MaxAroundDist"])
    # Sort vertices by distance
    lcDists = [((enVert.co - inCenterVert.co).length, enVert) for enVert in lcVertsAround]
    lcDists.sort(key=lambda x: x[0])
    outVertsAround = [enVert for tmpDist, enVert in lcDists]
    # Gather closer vertices if VertsAround has a lot of vertices
    if len(outVertsAround) < 2:
        gbLog["FewVertsCases"] += 1
        return False
    elif len(outVertsAround) >= gb["MaxAroundCount"]:
        outVertsAround = outVertsAround[:gb["MaxAroundCount"]]
    
    inData.VertsAround = outVertsAround
    return True

# Gather closer vertices around to decide axis
def GatherCloserVertsForAxis(inData):
    inCenterVert = inData.CenterVert
    lcGridMana = inData.GridManager
    
    # Gather closer vertices around
    outVertsForAxis = lcGridMana.get_vertices_in_distance(inCenterVert.co, gb["MaxDistForAxis"])
    if len(outVertsForAxis) < 2:
        gbLog["FewVertsCases"] += 1
        return False
    
    inData.VertsForAxis = outVertsForAxis
    return True
    
# Defind frame to measure angles
def DefindFrameToMeasureAngles(inData):
    # Assume: CalcAverageNormal returns a normalized vector for the axis
    inCenterVert = inData.CenterVert
    inVertsForAxis = inData.VertsForAxis

    # Calculate z-axis to measure angles
    outZAxis = CalcAverageNormal(inCenterVert, inVertsForAxis)
    # Decide a vertex as direction of x-axis
    for enVert in inVertsForAxis:
        lcXAxis = enVert.co - inCenterVert.co
        # Calculate y-axis by crossing z,x-axes
        lcYAxis = outZAxis.cross(lcXAxis)
        if lcYAxis.length != 0: break # x,z-axes must not be parallel
    lcYAxis = lcYAxis.normalized()
    lcXAxis = lcYAxis.cross(outZAxis)
    outXYTransMat = Matrix((lcXAxis, lcYAxis, [0, 0, 0])) # 3x3
    outXYZTransMat = Matrix((lcXAxis, lcYAxis, outZAxis)) # 3x3

    inData.ZAxis = outZAxis
    inData.XYTransMat = outXYTransMat
    inData.XYZTransMat = outXYZTransMat
    return True

class MEndVert:
    def __init__(self, inMVert):
        self.Vert = inMVert
        self.co = inMVert.co
        self.index = inMVert.index
        self.Order = None
        self.Outside = None
        self.Opposite = None
        self.Direction = None
    
    def __repr__(self):
        return "[EndVert" + repr(self.Vert)[6:]
    
    def MEndVert(self): pass

def Is_MEndVert(o):
    try:
        o.MEndVert
        return True
    except AttributeError:
        return False

# Get face-end vertices around a given vertex
def GetFaceEndVerts(inData, inCenterVert):
    inMesh = inData.Mesh
    inMana = inData.FacesManager
    inVertsAround = inData.VertsAround
    
    # Gather vertices that make faces around center vertex, and sort it
    lcVertIndices = []
    lcCenterIndex = inCenterVert.index
    for enFace in inMana.get_faces_around_vertex(lcCenterIndex):
        enFace = list(enFace) # need to copy
        enFace.remove(lcCenterIndex)
        # Add (index, opposite index)
        lcVertIndices.append((enFace[0], enFace[1]))
        lcVertIndices.append((enFace[1], enFace[0]))
    lcVertIndices.sort()
    # Gather face-end vertices by checking vertex duplication
    outEndVerts = []
    n = len(lcVertIndices)
    for i in range(n):
        lcPrevIndex, tmpIndex = lcVertIndices[(i - 1) % n]
        lcIndex, lcOpposite = lcVertIndices[(i + 0) % n]
        lcNextIndex, tmpIndex = lcVertIndices[(i + 1) % n]
        if lcIndex == lcPrevIndex: continue # Ignore duplicated vertices
        if lcIndex == lcNextIndex: continue # Ignore duplicated vertices

        enVert = inMesh.vertices[lcIndex]
        # Create EndVert instead of MVert to give additional info
        lcEndVert = MEndVert(enVert)
        for j, enVertAround in enumerate(inVertsAround):
            if enVertAround.index == enVert.index: # Have to compare index because VertsAround migth have both of MVert and EdVert
                lcEndVert.Order = j
                lcEndVert.Outside = False
                break
        if lcEndVert.Outside != False: # It means case where enVert wasn't found in VertsAround
            lcEndVert.Outside = True
        lcEndVert.Opposite = lcOpposite
        outEndVerts.append(lcEndVert)
    
    # Assign current state of EndVerts (T: some EndVerts, N: no EndVerts, F: full faces)
    if len(outEndVerts) > 0:
        outEndState = "SomeEndVerts"
    elif len(inMana.get_faces_around_vertex(lcCenterIndex)) == 0:
        outEndState = "NoEndVerts"
    else:
        outEndState = "FullFaces"

    return outEndVerts, outEndState

# Get face-end vertices around center vertex, and sort them
def GetFaceEndVertsAroundCenterAndSort(inData):
    inMesh = inData.Mesh
    inCenterVert = inData.CenterVert
    inMana = inData.FacesManager
    inVertsAround = inData.VertsAround
    inZAxis = inData.ZAxis
    
    # Gather face-end vertices
    outEndVerts, outEndState = GetFaceEndVerts(inData, inCenterVert)
    if outEndState == "FullFaces":
        gbLog["FullFacesCases"] += 1
        return False
    # Replace MVert with EndVert and add direction info
    for enEndVert in outEndVerts:
        enOppoVert = inMesh.vertices[enEndVert.Opposite]
        # Replace MVert with EndVert in VertsAround
        if enEndVert.Outside:
            inVertsAround.append(enEndVert) # Have to add it because it is outside
        else:
            inVertsAround[enEndVert.Order] = enEndVert
        # Add direction that shows which side of face-end edge has face
        lcVert2, lcOppoVert2 = (enVert.co - inCenterVert.co for enVert in [enEndVert, enOppoVert])
        lcAngle = VecsAngle2(lcVert2, lcOppoVert2, inZAxis)
        enEndVert.Direction = sign(lcAngle - 180)

    # Sort face-end vertices
    outEndVerts = SortVertsAroundZAxis(inData, outEndVerts)

    inData.EndVerts = outEndVerts
    inData.EndState = outEndState
    return True

# Do additional search for vertices outside
def DoAdditionalSearch(inData):
    # Assume: EndVerts has been setup and sorted around ZAxis.
    inCenterVert = inData.CenterVert
    lcGridMana = inData.GridManager
    inVertsAround = inData.VertsAround
    inXYZTransMat = inData.XYZTransMat
    inEndVerts = inData.EndVerts
    
    # Do additional search if either or both EndVerts are outside
    n = len(inEndVerts)
    for i in range(n):
        lcEndVerts = [inEndVerts[j % n] for j in [i, i + 1]]
        if not lcEndVerts[0].Direction > 0: continue
        if not lcEndVerts[0].Outside and not lcEndVerts[1].Outside: continue
        lcBase2 = [inXYZTransMat * (lcEndVerts[j].co - inCenterVert.co) for j in range(2)]
        lcMat = Matrix((
            [lcBase2[0] * lcBase2[0], lcBase2[0] * lcBase2[1]],
            [lcBase2[1] * lcBase2[0], lcBase2[1] * lcBase2[1]])).inverted() # 2x2
        lcZAxis = lcBase2[0].cross(lcBase2[1]).normalized()
        # Gather vertices for additional search
        lcSearchLength = max((lcEndVerts[j].co - inCenterVert.co).length for j in range(2))
        lcSearchVerts = lcGridMana.get_vertices_in_distance(inCenterVert.co, lcSearchLength, 1)
        # Search for additional vertices
        for enVert in lcSearchVerts:
            lcVert = enVert.co - inCenterVert.co
            if lcVert.length < gb["MaxAroundDist"]: continue
            lcVert2 = inXYZTransMat * lcVert
            lcVec = Vector((lcBase2[0] * lcVert2, lcBase2[1] * lcVert2)) # 2x1
            lcAns = lcMat * lcVec
            lcAns = [lcAns[0], lcAns[1], lcZAxis * lcVert2]
            if lcAns[0] <= 0 or lcAns[1] <= 0 or lcAns[0] + lcAns[1] >= 1: continue
            if abs(lcAns[2]) >= gb["MaxAroundDist"]: continue
            inVertsAround.append(enVert)
    
    return True

# Sort vertices around z-axis
def SortVertsAroundZAxis(inData, inVerts):
    inCenterVert = inData.CenterVert
    inXYTransMat = inData.XYTransMat

    # Transform vertices to defined frame
    lcVerts2 = [(inXYTransMat * (enVert.co - inCenterVert.co), enVert) for enVert in inVerts]
    # Measure angles and sort vertices by angle around z-axis
    lcAngles = [(PointAngleOnXY(enVert2), enVert) for enVert2, enVert in lcVerts2]
    lcAngles.sort(key=lambda x: x[0])
    # Pull out sorted vertices
    outVertsAround = [enVert for tmpAngle, enVert in lcAngles]

    return outVertsAround

# Sort vertices gathered around
def SortVertsGatheredAround(inData):
    inData.VertsAround = SortVertsAroundZAxis(inData, inData.VertsAround)
    return True

# Separate vertices by faces that already exist around center vertex and make groups
def GroupVertsByFaceEndVerts(inData):
    # Assume: VertsAround has been sorted around ZAxis.
    # Assume: VertsAround has some MEndVerts, which shows the search for face-end vertices has been finished.
    inVertsAround = inData.VertsAround
    inEndVerts = inData.EndVerts
    inEndState = inData.EndState
    
    # Assign array straight or empty if EndVerts are not found
    if inEndState == "NoEndVerts":
        inData.VertGroups = [inVertsAround]
        return True
    
    # Find face-end vertex that has plus direction
    for i, enVert in enumerate(inVertsAround):
        if Is_MEndVert(enVert) and enVert.Direction > 0:
            lcStart = i
    # Group vertices from face-end vertex to another
    outVertGroups = []
    lcIsInGroup = False
    n = len(inVertsAround)
    for i in range(lcStart, lcStart + n): # Error will happen here when intersection of faces exists
        enVert = inVertsAround[i % n]
        if Is_MEndVert(enVert):
            if enVert.Direction > 0:
                lcVertGroup = []
                lcIsInGroup = True
            else:
                lcVertGroup.append(enVert) # Have to add last one because of turning flag to false
                outVertGroups.append(lcVertGroup)
                lcIsInGroup = False
        if lcIsInGroup:
            lcVertGroup.append(enVert)
    
    inData.VertGroups = outVertGroups
    return True

# Gather all face-end edges in each group
def GatherAllFaceEndEdges(inData):
    inCenterVert = inData.CenterVert
    inVertsAround = inData.VertsAround
    inEndState = inData.EndState
    
    # Gather all face-end edges in VertsAround
    outEndEdges = []
    for i, enVert in enumerate(inVertsAround):
        # Get face-end vertices around each vertex
        lcEndVerts, lcState = GetFaceEndVerts(inData, enVert)
        if not lcState == "SomeEndVerts": continue
        # Gather face-end edges in edges connected to enVert
        lcEndEdges = []
        for enEndVert in lcEndVerts:
            if enEndVert.Outside: continue
            if enEndVert.Order < i: continue
            lcEndEdges.append([enVert, enEndVert])
        outEndEdges.extend(lcEndEdges)
    if inEndState == "SomeEndVerts":
        # Add edges including center vertex
        outEndEdges.append([inCenterVert, inVertsAround[ +0]])
        outEndEdges.append([inCenterVert, inVertsAround[ -1]])
    
    inData.EndEdges = outEndEdges
    return True

# Discard vertices hidden by face-end edges
def DiscardVertsHiddenByFaceEnds(inData):
    inCenterVert = inData.CenterVert
    inVertsAround = inData.VertsAround
    inXYTransMat = inData.XYTransMat
    inEndEdges = inData.EndEdges
    
    # Add flags that represent whether or not vertex should be discarded
    lcIsHidden = [False] * len(inVertsAround)
    # Check if each vertex is hidden by each face-end edge
    for enEndEdge in inEndEdges:
        lcVec2 = [inXYTransMat * (enVert.co - inCenterVert.co) for enVert in enEndEdge]
        try:
            lcInv = Matrix((
                [lcVec2[0] * lcVec2[0], lcVec2[0] * lcVec2[1]],
                [lcVec2[1] * lcVec2[0], lcVec2[1] * lcVec2[1]])).inverted() # 2x2
        except ValueError: # Matrix doesn't have inverse becuase vectors in Vec2 are parallel or its length is 0
            continue
        for i, enVert in enumerate(inVertsAround):
            enHidden = lcIsHidden[i]
            if enHidden: continue
            if enVert.index == enEndEdge[0].index: continue # Must compare with index because MVert and EndVert are mixed
            if enVert.index == enEndEdge[1].index: continue
            # Check if vertex is hidden by shadow made from face-end edge
            lcVert2 = inXYTransMat * (enVert.co - inCenterVert.co)
            lcAns = lcInv * Vector((lcVec2[0] * lcVert2, lcVec2[1] * lcVert2)) # 2x1
            if lcAns[0] < 0 or lcAns[1] < 0 or lcAns[0] + lcAns[1] < 1: continue
            # Trun on flag to discard this vertex
            lcIsHidden[i] = True
    # Pull out left vertices all
    outVertsAround = [enVert for i, enVert in enumerate(inVertsAround) if not lcIsHidden[i]]

    inData.VertsAround = outVertsAround
    return True

# Check if angles between adjacent 2 vertices are too small
def CheckIfAnglesAreTooSmall(inData):
    # Assume: VertsAround has been sorted around ZAxis.
    inCenterVert = inData.CenterVert
    inVertsAround = inData.VertsAround
    inZAxis = inData.ZAxis
    inEndState = inData.EndState
    
    n = len(inVertsAround)
    lcEnables = [False] * n
    # Measure all distances between vertices and z-axis and sort vertices by them
    lcLengths = []
    if inEndState == "SomeEndVerts":
        lcRange = range(1, n - 1)
    else:
        lcRange = range(n)
    for i in lcRange:
        enVert = inVertsAround[i]
        lcVec = enVert.co - inCenterVert.co
        # Measure distance between vertex and z-axis
        lcLength = sqrt(lcVec.length ** 2 - (lcVec * inZAxis) ** 2)
        lcLengths.append([lcLength, i])
    # Sort vertices by distance
    lcLengths.sort(key=lambda x: x[0])
    
    # Get both adjacent vertices that has been enabled
    def GetAdjacentEnabledVerts(inIndex):
        for i in range(inIndex + 1, inIndex + n, +1):
            if not lcEnables[i % n]: continue
            lcVertL = inVertsAround[i % n]
            break
        for i in range(inIndex - 1, inIndex - n, -1):
            if not lcEnables[i % n]: continue
            lcVertR = inVertsAround[i % n]
            break
        return lcVertL, lcVertR
    
    # Check if vertex is in unable region and return True if it is in
    def CheckIfItIsInUnableRegion(inVert, inRegion):
        lcVec = inVert.co - inRegion["Vec0"]
        lcAns = inRegion["Inv"] * Vector((inRegion["Vec1"] * lcVec, inRegion["Vec2"] * lcVec)) # 2x1
        if lcAns[0] == 0 or lcAns[1] == 0:
            gbLog["Warnings"]["NZ1"] += 1
#            print "!!Near zero 1!!", inVert.index, lcAns
        return lcAns[0] >= 0 and lcAns[1] >= 0    
    
    if inEndState == "SomeEndVerts":
        # Set True to enable both face-end vertices because it can't be ignored
        lcEnables[ +0], lcEnables[ -1] = True, True
    elif inEndState == "NoEndVerts":
        # Set True to enable closest vertex because more than one enabled vertex is needed to start to check
        lcEnables[lcLengths[0][1]] = True
        del lcLengths[0]
    # Check angles between enabled adjacent vertices in order of closer vertex
    lcUnableRegions = []
    for tmpLength, i in lcLengths:
        enVert = inVertsAround[i]
        # Ignore vertex if it is in unable regions
        lcInUnableRegion = False
        for enRegion in lcUnableRegions:
            if CheckIfItIsInUnableRegion(enVert, enRegion):
                lcInUnableRegion = True
                break
        if lcInUnableRegion: continue
        
        # Get both adjacent vertices that has been enabled
        lcVertL, lcVertR = GetAdjacentEnabledVerts(i)
        # Measure angles and get smaller one
        lcAngleL = VertsAngle3(inCenterVert, enVert, lcVertL, inZAxis)
        lcAngleR = VertsAngle3(inCenterVert, enVert, lcVertR, inZAxis)
        lcSortArray = [[lcAngleL, lcVertL], [lcAngleR, lcVertR]]
        lcSortArray.sort(key=lambda x: x[0])
        [lcMinAngle, lcNeigVert1], [tmpAngle, lcNeigVert2] = lcSortArray
        # Enable vertex if angle is large
        if lcMinAngle > gb["MinVertsAngle"]:
            lcEnables[i] = True
            continue
        
        # Make unable region that is defined using vectors and inverce matrix
        lcVec1 = lcNeigVert1.co - inCenterVert.co
        lcVec2 = enVert.co - lcNeigVert1.co
        try:
            lcInv = Matrix((
                [lcVec1 * lcVec1, lcVec1 * lcVec2],
                [lcVec1 * lcVec2, lcVec2 * lcVec2])).inverted() # 2x2
        except ValueError:
            gbLog["Warnings"]["NZ3"] += 1
#            print "!!Near parallel 3!!", lcVec1, lcVec2
            continue
        lcRegion = {"Vec0": lcNeigVert1.co, "Vec1": lcVec1, "Vec2": lcVec2, "Inv": lcInv, "Vert": enVert}
        # Enable vertex if its neighbor vertex is in unable region that has been made right now, when it is in SomeEndVerts state
        if inEndState == "SomeEndVerts" and CheckIfItIsInUnableRegion(lcNeigVert2, lcRegion):
            lcEnables[i] = True
            continue
        
        lcUnableRegions.append(lcRegion)
    
    # Check if the triangle outside has shaper angle than the triangle around center
    for tmpLength, i in lcLengths:
        if lcEnables[i]: continue
        enVert = inVertsAround[i]
        # Ignore vertex if it is in unable regions
        lcInUnableRegion = False
        lcRegionIndex = None
        for j, enRegion in enumerate(lcUnableRegions):
            # Don't check enVert because it is going to be an enable vertex
            if enVert == enRegion["Vert"]:
                lcRegionIndex = j
                continue
            if CheckIfItIsInUnableRegion(enVert, enRegion):
                lcInUnableRegion = True
                break
        if lcInUnableRegion: continue
        
        # Get both adjacent vertices that has been enabled
        lcVertL, lcVertR = GetAdjacentEnabledVerts(i)
        # Measure angles around center and get smaller one
        lcAngleL = VertsAngle3(inCenterVert, enVert, lcVertL, inZAxis)
        lcAngleR = VertsAngle3(inCenterVert, enVert, lcVertR, inZAxis)
        lcSortArray = [[lcAngleL, lcVertL], [lcAngleR, lcVertR]]
        lcSortArray.sort(key=lambda x: x[0])
        [lcMinAngle, lcNeigVert1], [tmpAngle, lcNeigVert2] = lcSortArray
        # Measure angle around lcNeigVert2
        lcNeigAngle2 = VertsAngle3(lcNeigVert2, enVert, lcNeigVert1, inZAxis)
        
        # Enable vertex if the triangle outside has shaper angle than the triangle around center
        if lcNeigAngle2 < lcMinAngle:
            lcEnables[i] = True
            # Delete the region because enVert has become an enable vertex
            del lcUnableRegions[lcRegionIndex]
    
    # Pull out only enabled vertices
    outVertsAround = [inVertsAround[i] for i in range(n) if lcEnables[i]]
    # Add vertex if only one vertex has been gathered
    if inEndState == "NoEndVerts" and len(outVertsAround) < 2:
        outVertsAround.append(inVertsAround[lcLengths[1][1]])
    gbLog["TooSmallVertsAngles"] += len(inVertsAround) - len(outVertsAround)

    inData.VertsAround = outVertsAround
    return True

# Check if angles between adjacent 2 vertices are too large
def CheckIfAnglesAreTooLarge(inData):
    # Assume: VertsAround has been sorted around ZAxis.
    inCenterVert = inData.CenterVert
    inVertsAround = inData.VertsAround
    inZAxis = inData.ZAxis
    inEndState = inData.EndState
    inMakeFace = inData.MakeFace

    n = len(inVertsAround)
    for i in range(n - 1):
        # Measure angle between i and i+1 vertices
        lcAngle = VertsAngle2(inCenterVert, inVertsAround[i + 0], inVertsAround[i + 1], inZAxis)
        if 360 - lcAngle < 1e-5:
            gbLog["Warnings"]["NZ2"] += 1
#            print "!!Near zero 2!!", lcAngle
        if lcAngle >= gb["MaxVertsAngle"]:
            inMakeFace[i + 0] = False
            gbLog["TooLargeVertsAngles"] += 1
    if inEndState == "NoEndVerts":
        # Measure angle between first and end vertices
        lcAngle = VertsAngle2(inCenterVert, inVertsAround[ -1], inVertsAround[ +0], inZAxis)
        if lcAngle >= gb["MaxVertsAngle"]:
            inMakeFace[ -1] = False
            gbLog["TooLargeVertsAngles"] += 1

    return True

# Make faces around simply
def MakeFacesAroundSimply(inData):
    inCenterVert = inData.CenterVert
    inVertsAround = inData.VertsAround
    inEndState = inData.EndState
    inMakeFace = inData.MakeFace
    
    # Make face-sets including sets of 3 vertex indices
    outFaces = []
    for i in range(len(inVertsAround) - 1):
        if not inMakeFace[i]: continue
        lcVert0 = inVertsAround[i + 0]
        lcVert1 = inVertsAround[i + 1]
        # Register set of 3 vertex indices of face to make
        outFaces.append([lcVert0.index, lcVert1.index, inCenterVert.index])

    # Connect first and last with face if EndVerts are not found
    if inEndState == "NoEndVerts" and inMakeFace[ -1]:
        lcVert0 = inVertsAround[ -1]
        lcVert1 = inVertsAround[ +0]
        # Register set of 3 vertex indices of face to make
        outFaces.append([lcVert0.index, lcVert1.index, inCenterVert.index])

    inData.Faces = outFaces
    return True

# Combine all of faces that have been made in each group
def CombineFacesInAllVertGroups(inData):
    inEndState = inData.EndState
    inFaceGroups = inData.FaceGroups
    
    # Assign group straight if EndVerts are not found
    if inEndState == "NoEndVerts":
        inData.Faces = inFaceGroups[0]
        return True
    
    # Combine face-sets in each group
    outFaces = []
    for enFaceGroup in inFaceGroups:
        outFaces.extend(enFaceGroup)
#        outFaces.append(None)
    
    inData.Faces = outFaces
    return True

# Check if adjacent 2 triangles have good shapes
def CheckIfTrianglesHaveGoodShapes(inData):
    # Assume: Adjacent 2 faces have sequential indices in Faces array.
    # Assume: All items of Faces have the same form as [AroundVert1, AroundVert2, CenterVert].
    # Assume: AroundVert1, 2 must be sorted around ZAxis.
    inMesh = inData.Mesh
    inFaces = inData.Faces

    lcMaxMinAngles = []
    n = len(inFaces)
    for i in range(n):
        lcFace0, lcFace1 = inFaces[(i + 0) % n], inFaces[(i + 1) % n]
        # Add None and go to next if no faces are created in next side
        if lcFace0[1] != lcFace1[0]:
            lcMaxMinAngles.append(None)
            continue
        # Measure max internal angles in case of current and modified form
        lcMax1, tmpMin = TriangleMaxMinAngle([inMesh.vertices[x] for x in lcFace0])
        lcMax2, tmpMin = TriangleMaxMinAngle([inMesh.vertices[x] for x in lcFace1])
        lcCurrMax = max(lcMax1, lcMax2)
        lcMax1, tmpMin = TriangleMaxMinAngle([inMesh.vertices[x] for x in [lcFace0[0], lcFace0[1], lcFace1[1]]])
        lcMax2, tmpMin = TriangleMaxMinAngle([inMesh.vertices[x] for x in [lcFace0[0], lcFace1[1], lcFace0[2]]])
        lcModiMax = max(lcMax1, lcMax2)
        lcMaxMinAngles.append([lcCurrMax, lcModiMax])
    
    # Gather only angles of modified form and sort them by angles
    lcModiArray = []
    for i, enAngles in enumerate(lcMaxMinAngles):
        if enAngles == None: continue
        lcCurrMax, lcModiMax = enAngles
        if lcCurrMax > lcModiMax:
            lcModiArray.append([lcModiMax, i])
    lcModiArray.sort(key=lambda x: x[0])
    
    # Change into modofied form if appropriate
    lcIsModified = [False] * n
    for tmpAngle, i in lcModiArray:
        if lcIsModified[i]: continue
        lcFace0, lcFace1 = inFaces[(i + 0) % n], inFaces[(i + 1) % n]
        # Measure angle between 2 triangles of modified form
        lcFacesAngle = FacesAngleAroundEdge(
            inMesh.vertices[lcFace0[0]], inMesh.vertices[lcFace1[1]],
            inMesh.vertices[lcFace0[1]], inMesh.vertices[lcFace0[2]])
        # Don't change if 2 triangles are reentrant
        if lcFacesAngle < 90: continue
        # Change into modofied form
        lcFace0, lcFace1 = lcFace0[:], lcFace1[:] # [:] is needed to copy array
        inFaces[(i + 0) % n] = [lcFace0[0], lcFace0[1], lcFace1[1]]
        inFaces[(i + 1) % n] = [lcFace0[0], lcFace1[1], lcFace0[2]]
        lcIsModified[(i - 1) % n], lcIsModified[(i + 0) % n], lcIsModified[(i + 1) % n] = True, True, True
        gbLog["ModifiedTriangles"] += 1

    return True

# Extend faces in faces manager
def RegisterFacesToFacesManager(inData):
    inFaces = inData.Faces
    inMana = inData.FacesManager
    
    # Get rid of all None from Faces
    tmpFaces = [enSet for enSet in inFaces if enSet != None]
    inMana.add_many(tmpFaces)
    gbLog["MadeFaces"] += len(tmpFaces)        
    
    return True


#******************************
#---===Basic functions 1===
#******************************

def sign(x):
    if x > 0: return 1
    if x < 0: return -1
    return 0

def yorn(inBool, inTrue, inFalse):
    if inBool:
        return inTrue
    else:
        return inFalse
    
#******************************
#---===Basic functions 2===
#******************************

def SmallerAngle(inAngle):
    if inAngle > 180: # it can't calculate with "% 180"
        return 360 - inAngle
    else:
        return inAngle

def PointAngleOnXY(inPoint):
    if inPoint.length == 0: return 360
    return atan2(inPoint.y, inPoint.x) / pi * 180 % 360

def VertsAngle(inSharedVert, inVert1, inVert2):
    v1, v2 = inVert1.co - inSharedVert.co, inVert2.co - inSharedVert.co
    return v1.angle(v2) * 180 / pi

def VecsAngle2(inVec1, inVec2, inAxis):
    v1, v2 = inVec1, inVec2
    return v1.angle(v2) * 180 / pi * sign(v1.cross(v2) * inAxis) % 360
    
def VertsAngle2(inSharedVert, inVert1, inVert2, inAxis):
    v1, v2 = inVert1.co - inSharedVert.co, inVert2.co - inSharedVert.co
    return VecsAngle2(v1, v2, inAxis)

def VertsAngle3(inSharedVert, inVert1, inVert2, inAxis):
    return SmallerAngle(VertsAngle2(inSharedVert, inVert1, inVert2, inAxis))
    
def TriangleMaxMinAngle(inVerts):
    lcAngles = [VertsAngle(inVerts[(i + 0) % 3], inVerts[(i - 1) % 3], inVerts[(i + 1) % 3]) for i in range(3)]
    return max(lcAngles), min(lcAngles)

def FacesAngleAroundEdge(inSharedVert1, inSharedVert2, inVert1, inVert2):
    lcZAxis = inSharedVert2.co - inSharedVert1.co
    lcXAxis = inVert1.co - inSharedVert1.co
    lcYAxis = lcZAxis.cross(lcXAxis).normalized()
    lcXAxis = lcYAxis.cross(lcZAxis).normalized()
    lcXYTransMat = Matrix((lcXAxis, lcYAxis, [0, 0, 0])) # 3x3
    lcVert2 = lcXYTransMat * (inVert2.co - inSharedVert1.co)
    return SmallerAngle(PointAngleOnXY(lcVert2))


#******************************
#---===Normal Manager===
#******************************

class NormalManager:
    
    def __init__(self):
        self.Distance = None # In form of float
        self.Normals = None # In form of {MVert.index = BVec, ...}
    
    # Calculate average normal for the specified vertices collecting vertices in the specified distance
    def Calculate(self, inGridMana, inVerts, inDistance):
        inNormals = {}
        
        for enVert in inVerts:

            # Collect closer vertices around the center
            lcVerts = inGridMana.GetVertsInDistance(enVert.co, inDistance)
            if len(lcVerts) < 1:
                inNormals[enVert.index] = None
#                gbLog["NormMana.FewVertsCases"] += 1
                continue
            
            # Calculate z-axis to measure angles
            inNormals[enVert.index] = CalcAverageNormal(enVert, lcVerts)
        
        self.Distance = inDistance
        self.Normals = inNormals
    
    def __getitem__(self, inMVertIndex):
        return self.Normals[inMVertIndex]

# Solve a cubic equation based on Cardano Method
def SolveCubicEquation(a3210):
    
    def pow_ex(x, p):
        if x < 0:
            return -((-x) ** p)
        else:
            return x ** p

    (a3, a2, a1, a0) = (float(x) for x in a3210)
    A2, A1, A0 = a2 / a3, a1 / a3, a0 / a3
    p, q = A1 - 1.0 / 3.0 * A2 ** 2, A0 - 1.0 / 3.0 * A1 * A2 + 2.0 / 27.0 * A2 ** 3
    D3 = (q / 2.0) ** 2 + (p / 3.0) ** 3
    
    if D3 <= 0:
        r = sqrt((q / 2.0) ** 2 + -D3)
        th = atan2(sqrt(-D3), -q / 2)
        y = [r ** (1.0 / 3.0) * 2.0 * cos(2.0 * pi / 3.0 * k + th / 3.0) for k in range(3)]
    else:
        B1, B2 = pow_ex(-q / 2.0 + sqrt(D3), 1.0 / 3.0), pow_ex(-q / 2.0 - sqrt(D3), 1.0 / 3.0)
        y = [B1 + B2, -(B1 + B2) / 2.0 + sqrt(3) * (B1 - B2) / 2.0 * 1j, -(B1 + B2) / 2.0 + sqrt(3) * (-B1 + B2) / 2.0 * 1j]
    ans = [x - A2 / 3.0 for x in y]
        
    return ans
# Test code
#def main():
#    ans = SolveCubicEquation([1, - 9, 26, - 24])
#    print "The result is %s, which should be [2.0, 3.0, 4.0]" % ans
#    ans = SolveCubicEquation([1, 2, 3, 4])
#    print "The result is %s, which should be [-1.6506291914393882, (-0.17468540428030588+1.5468688872313963j), (-0.17468540428030588-1.5468688872313963j)]" % ans

# Calculate average normal based on Lagrange's Lambda Method minimizing of sum(ax+by+cz)^2, in which ax+by+cz represents the distance between a vertex and the zero center
def CalcAverageNormal(inCenterVert, inVerts):
    
#    def b2py_float(x):
#        return round(x * 1e+6) * 1e-6
#    def b2py_vec(x):
#        for i in range(3): vec[i] = b2py_float(vec[i])
    NearZero = 1e-5
    
    # Summation vertex coordinates and obtain A matrix 
    Axx, Ayy, Azz, Axy, Ayz, Azx = (0,) * 6
    for enVert in inVerts:
        vec = enVert.co - inCenterVert.co
#        b2py_vec(vec)
        Axx += vec.x ** 2
        Ayy += vec.y ** 2
        Azz += vec.z ** 2
        Axy += vec.x * vec.y
        Ayz += vec.y * vec.z
        Azx += vec.z * vec.x
    
    # Solve det(A - lambda*I) = 0 for three patterns of lambda
    lambs = SolveCubicEquation([ -1, Axx + Ayy + Azz, Axy ** 2 + Ayz ** 2 + Azx ** 2 - Axx * Ayy - Axx * Azz - Ayy * Azz, -Azz * Axy ** 2 + 2 * Axy * Ayz * Azx - Axx * Ayz ** 2 - Ayy * Azx ** 2 + Axx * Ayy * Azz])
    lamb = lambs[1] # Always the second lambda minimizes sum(ax+by+cz)^2, according to many experiments
    
    def EvalFunc(inNorm):
        a, b, c = inNorm
        return Axx * a ** 2 + Ayy * b ** 2 + Azz * c ** 2 + 2 * Axy * a * b + 2 * Ayz * b * c + 2 * Azx * c * a
    def FindProperNorm(inNorm1, inNorm2):
        e1 = EvalFunc(inNorm1)
        e2 = EvalFunc(inNorm2)
        if e1 < e2:
            return inNorm1
        else:
            return inNorm2

    # Calculate the ratio of a, b, c from lambda
    Axy_abs, Ayz_abs, Azx_abs = abs(Axy), abs(Ayz), abs(Azx)
    if Axy_abs < NearZero and Ayz_abs < NearZero and Azx_abs < NearZero: # when two of a, b, c are zero
        A_min = min([Axx, Ayy, Azz])
        if A_min == Axx:
            outNorm = [1.0, 0.0, 0.0]
        elif A_min == Ayy:
            outNorm = [0.0, 1.0, 0.0]
        else:
            outNorm = [0.0, 0.0, 1.0]
            
    elif Axy_abs < NearZero and Azx_abs < NearZero: # when a is zero
        lcNorm1 = [0.0, -Ayz, Ayy - lamb]
        lcNorm2 = [1.0, 0.0, 0.0]
        outNorm = FindProperNorm(lcNorm1, lcNorm2)
    elif Axy_abs < NearZero and Ayz_abs < NearZero: # when b is zero
        lcNorm1 = [ -Azx, 0.0, Axx - lamb]
        lcNorm2 = [0.0, 1.0, 0.0]
        outNorm = FindProperNorm(lcNorm1, lcNorm2)
    elif Ayz_abs < NearZero and Azx_abs < NearZero: # when c is zero
        lcNorm1 = [ -Axy, Axx - lamb, 0.0]
        lcNorm2 = [0.0, 0.0, 1.0]
        outNorm = FindProperNorm(lcNorm1, lcNorm2)
    
    else:
        a1 = Azx * (Ayy - lamb) - Ayz * Axy
        a2 = Axy * (Azz - lamb) - Ayz * Azx
        b1 = c2 = Ayz * (Axx - lamb) - Azx * Axy
        if abs(a1) > NearZero and abs(a2) > NearZero:
            outNorm = [a1 * a2, a2 * b1, a1 * c2]
        else:
            print("This case is uncertain, not implemented yet. (Err:200901111206)")
            outNorm = [0.0, 0.0, 1.0] # Incorrect values
    
    return Vector(outNorm).normalized() # 3x1
# Test code
#def main():
#    lcMesh = B.Mesh.Get("Mesh1") # You need a mesh object which mesh name is Mesh1.
#    lcCenter = lcMesh.verts[0]
#    lcNorm = CalcAverageNormal(lcCenter, lcMesh.verts)
#    print "The result is %s." % lcNorm
#
#    # Draw the result normal with a line in Blender
#    lcNormMesh = B.Mesh.New("NormMesh1")
#    B.Scene.GetCurrent().objects.new(lcNormMesh, "NormMesh1")
#    lcNormMesh.verts.extend([lcCenter.co + lcNorm, lcCenter.co - lcNorm])
#    lcNormMesh.edges.extend([0, 1])

# Draw normals / Test function
def DrawNormalVector(inNormMana, inVerts=None, inVecLen=0.1):
    if inVerts == None:
        inVerts = inNormMana.Verts
    
    # Create mesh and object
    lcMesh = B.Mesh.New("NormMesh1")
    B.Scene.GetCurrent().objects.new(lcMesh, "NormMesh1")
    
    lcVerts = []
    lcEdges = []
    for enVert in inVerts:
        lcCenterVec = Vector(enVert.co) # 3x1
        lcNormal = inNormMana[enVert.index]
        
        lcNormalVec1 = lcCenterVec + lcNormal * -inVecLen # setting for normal looks
        lcNormalVec2 = lcCenterVec + lcNormal * inVecLen # setting for normal looks
        lcVerts.extend([lcNormalVec1, lcNormalVec2])
        lcEdges.append([len(lcVerts) - 2, len(lcVerts) - 1])
    
    lcMesh.verts.extend(lcVerts)
    lcMesh.edges.extend(lcEdges)
    
# Code to test Normal Manager feature
#def Main():
#    lcPGM = PointsGridManager([0.5] * 3)
#    lcPGM.PositionGetter = GetPositionFromMVert
#    lcPGM.Add(B.Mesh.Get("Mesh1").verts)
#    lcNM = NormalManager()
#    lcNM.Calculate(lcPGM, B.Mesh.Get("Mesh1").verts, 1.0)
#    print "The normal of the vertex Mesh.verts[0] is: ", lcNM[0]
#    DrawNormalVector(lcNM, None, 0.5)


#******************************
#---===Faces Manager===
#******************************

class FaceAddingManager:
    
    def __init__(self):
        self.__db_face_poly = {}
        '''
        def: {(0,1,3): False, (0,1,2,3): True, ...}
        use: __db_face_poly[(i_vert, ...)] = True or False
        it's a dictionary of vertex indices for a face, indices are ordered,  
        value has False if its face already exists in mesh and True if you 
        add its face newly.
        '''
        self.__db_around_vert = {}
        '''
        def: {[ref of (0,1,3), ...], ...}
        use: __db_around_vert[i_vert][*] = ref of (i_vert, ...)
        it's a dictionary to collect all the faces that exists around a vertex.
        '''
    
    def import_many(self, face_poly_enumerator=None):
        '''
        assume: face_poly_enumerator enumerates like (0,1,3) or (0,2,1,3)
        assume: when face_poly_enumerator is None, you use subscriber to import.
        '''
        if face_poly_enumerator is None:
            return self.import_by_sber()
        else:
            self.import_by_etor(face_poly_enumerator)
        
    def import_by_etor(self, face_poly_enumerator):
        for poly in face_poly_enumerator:
            self.__add_one(poly, False)
        
    def import_by_sber(self):
        class FaceSubscriber:
            def __next__(_self, poly): #@NoSelf
                self.import_one(poly)
        return FaceSubscriber()
    
    def import_one(self, poly):
        self.__add_one(poly, False)

    def import_from_mesh(self, mesh):
        for face in mesh.tessfaces:
            self.__add_one(face.vertices, False)
        
    def add_many(self, face_poly_enumerator=None):
        '''
        assume: face_poly_enumerator enumerates like (0,1,3) or (0,2,1,3)
        assume: when face_poly_enumerator is None, you use subscriber to add.
        '''
        if face_poly_enumerator is None:
            return self.add_by_sber()
        else:
            self.add_by_etor(face_poly_enumerator)
        
    def add_by_etor(self, face_poly_enumerator):
        for poly in face_poly_enumerator:
            self.add_one(poly)
        
    def add_by_sber(self):
        class FaceSubscriber:
            def __next__(_self, poly): #@NoSelf
                self.add_one(poly)
        return FaceSubscriber()
    
    def add_one(self, poly):
        self.__add_one(poly, True)
        
    def __add_one(self, poly, exist_or_not):
        '''
        register faces to inner database.
        assume: poly is like (0,1,3) or (0,2,1,3)
        '''
        
        poly = self.__sort(poly) # got ordered tuple like (0,1,3)
        if poly in self.__db_face_poly: # if: it already exists
            return
        
        # add to __db_face_poly
        self.__db_face_poly[poly] = exist_or_not
        
        # add to __db_around_vert
        for i_vert in poly:
            poly_list = self.__db_around_vert.get(i_vert, None)
            if poly_list is None:
                self.__db_around_vert[i_vert] = [poly]
            else:
                poly_list.append(poly)
    
    @classmethod
    def __sort(cls, poly):
        '''
        sort vertex indices for a face and make the order always the same.
        assume: poly is like (0,1,3) or (0,2,1,3)
        '''
        
        poly = list(poly) # MUST copy of array to sort
        
        if len(poly) == 4:
            is_0123 = cls.__is_0123_or_0213(poly)
        
        poly.sort()
        
        if len(poly) == 4 and not is_0123: # if: it's 0213 pattern
            temp_i = poly[1]
            poly[1] = poly[2]
            poly[2] = temp_i
        
        return tuple(poly)
    
    @staticmethod
    def __is_0123_or_0213(poly):
        
        count = 0
        if poly[0] > poly[1]:
            count += 1
        if poly[1] > poly[2]:
            count += 1
        if poly[2] > poly[3]:
            count += 1
        if poly[3] > poly[0]:
            count += 1
    
        return count == 1 or count == 3 # if: it's 0123 pattern
    
    def remove(self, poly_list):
        
        for poly in poly_list:
            
            poly = self.__sort(poly)
            value = self.__db_face_poly.get(poly, None)
            if value is None:
                continue
            
            del self.__db_face_poly[poly]
            
            for i_vert in poly:
                poly_list = self.__db_around_vert[i_vert]
                poly_list.remove(poly)
                if len(poly_list) == 0:
                    del self.__db_around_vert[i_vert]
    
    def get_faces_around_vertex(self, vertex_index):
        return self.__db_around_vert.get(vertex_index, [])

    def get_faces_to_add_etor(self):
        return (poly for poly, value in self.__db_face_poly.items() if value == True)

    def debug_get_db_face_poly(self):
        return self.__db_face_poly

    def debug_get_db_around_vert(self):
        return self.__db_around_vert

class FaceCreater:
    
    @staticmethod
    def add_by_from_pydata(mesh, poly_list):
        '''
        add faces to Blender Mesh.
        assume: poly_list is a list of vertex index tuple which defines a face like [(0,1,3), ...]
        '''
        
        if hasattr(poly_list, "__len__"):
            faces = poly_list
        else:
            faces = tuple(poly_list) # use tuple for performance

        mesh.from_pydata([], [], faces)
        # above: you can see the source code: 
        # Mesh.from_pydata in Blender\2.61\scripts\modules\bpy_types.py
        # you'll find out it uses vertices_raw inside to add faces.
        mesh.update(calc_edges=True)
    
    @classmethod
    def add_by_vertices_raw(cls, mesh, poly_list):
        '''
        add faces to Blender Mesh.
        assume: poly_list is a list of vertex index tuple which defines a face like [(0,1,3), ...]
        '''
        
        i_begin = len(mesh.tessfaces)
        if hasattr(poly_list, "__len__"): # if: length is known
            mesh.tessfaces.add(len(poly_list))
            for i, poly in enumerate(poly_list, i_begin):
                mesh.tessfaces[i].vertices_raw = cls.__adjust_poly(poly)
        
        else: # if: it's enumerator
            for i, poly in enumerate(poly_list, i_begin):
                mesh.tessfaces.add(1)
                mesh.tessfaces[i].vertices_raw = cls.__adjust_poly(poly)
                
        mesh.update(calc_edges=True)
    
    @staticmethod
    def __adjust_poly(poly):
        '''
        get it appropriate to follow vertices_raw data rule
        assume: poly is in form of (0,2,1,3) etc
        '''
        
        n = len(poly)
        if n == 3:
            poly = (poly[0], poly[1], poly[2], 0)
            
        elif n == 4:
            if poly[3] == 0:
                poly = (0, poly[0], poly[1], poly[2])
                
        else:
            raise "Unexpected"
            
        return poly


#******************************
#---===Points Grid Manager===
#******************************

class PointsGridManager:
    
    def __init__(self, xyz_size=[1.0] * 3, xyz_offset=[0.0] * 3):
        self.size = xyz_size # In form of [float, float, float]
        self.offset = xyz_offset # In form of [float, float, float]
        self.__db_grid = {}
        '''
        def: {(i_x, i_y, i_z): [PcsVertex, ...], ...}
        use: __db_grid[(i_x, i_y, i_z)][*] = PcsVertex
        i_x, i_y, i_z are normalized grid position index (int).
        '''
        self.precision_level = 2 # 0: Cube, 1: Cell sphere, 2: Complete sphere
        
    def import_many(self, vertex_enumerator=None):
        '''
        Import vertices to manage by grid.
        assume: vertex_enumerator returns PcsVertex or object containing .co, .index
        assume: when vertex_enumerator is None, you use subscriber to import.
        '''
        if vertex_enumerator is None:
            return self.import_by_sber()
        else:
            self.import_by_etor(vertex_enumerator)
        
    def import_by_etor(self, vertex_enumerator):
        for vertex in vertex_enumerator:
            self.import_one(vertex)

    def import_by_sber(self):
        class VertexSubscriber:
            def __next__(_self, vertex): #@NoSelf
                self.import_one(vertex)
        return VertexSubscriber()
        
    def import_one(self, vertex):
        '''
        assume: vertex is PcsVertex or object containing .co, .index
        '''

        # Get key name from vertex position
        key_name = self.get_cell_index(vertex.co)
        
        # Import vertices to the dictionary grid
        vert_list = self.__db_grid.get(key_name, None)
        if vert_list is None:
            self.__db_grid[key_name] = [vertex]
        else:
            vert_list.append(vertex)

    @staticmethod
    def to_PcsVertex(vertex):
        '''
        assume: vertex is Blender Vertex
        '''
        return PcsVertex(PcsVector(vertex.co), vertex.index)

    def clear(self):
        self.__db_grid = {}
    
    def get_cell_index(self, position):
        '''
        Get cell index for the dictionary from specified position.
        assume: position must be array like [x,y,z], not Blender Vertex
        '''
        return tuple(int((position[i] - self.offset[i]) // self.size[i]) for i in range(3))
        # above: when self.size=1 and self.offset=0, the result will be:
        # ... [-1 -1+d -0.5 0-d]->-1 [0 0+d 0.5 1-d]->0 [1 1+d 1.5 2-d]->1 ...
    
    def get_cell_position(self, cell_index):
        '''
        assume: cell_index must be enumerable like (x,y,z)
        '''
        return list(cell_index[i] * self.size[i] + self.offset[i] for i in range(3))
    
    def get_vertices_in_distance(self, position_center, distance=0, precision_level=None):
        '''
        Get vertices that are located in the specified distance.
        assume: position must be array like [x,y,z], not Blender Vertex
        '''

        pos_c = position_center
        dist = distance
        if precision_level is None:
            precision_level = self.precision_level
        
        cell_index_c = self.get_cell_index(pos_c)
        # Calculate how many cells exist in the distance
        cell_index_upper = self.get_cell_index([pos_c[i] + dist for i in range(3)])
        cell_index_lower = self.get_cell_index([pos_c[i] - dist for i in range(3)])
        
        # Get grid cells that are located in cube
        grid_cells = []
        for i_x in range(cell_index_lower[0], cell_index_upper[0] + 1):
            for i_y in range(cell_index_lower[1], cell_index_upper[1] + 1):
                for i_z in range(cell_index_lower[2], cell_index_upper[2] + 1):
                    grid_cells.append((i_x, i_y, i_z))
        
        # Get grid cells that are located in sphere
        if precision_level == 1:
            # assume: x,y,z of grid size are all the same value
            # note: radius_cell_ave is sometimes longer than necessary
            
            grid_cells_new = []
            radius_cell_ave = sqrt(sum(self.size[i] ** 2 for i in range(3)))
            dist_p2 = (dist + 0.5 * radius_cell_ave) ** 2
            for cell_index_en in grid_cells:
                
                if cell_index_en == cell_index_c:
                    grid_cells_new.append(cell_index_en)
                    continue
                
                # Check if the next plus end of the cell cell_index_en is closer to pos_c in each coordinate of xyz and set 1
                pos_cell_en = self.get_cell_position(cell_index_en)
                pos_cent_en = [pos_cell_en[i] + 0.5 * self.size[i] for i in range(3)]
                dist_en_c_p2 = sum((pos_cent_en[i] - pos_c[i]) ** 2 for i in range(3))
                if dist_en_c_p2 <= dist_p2:
                    grid_cells_new.append(cell_index_en)
                    
            grid_cells = grid_cells_new
        
        # Get vertices from key names
        vertices_out = []
        for cell_index_en in grid_cells:
            
            # Discard vertices that have the same position as pos_c
            if cell_index_en == cell_index_c: # if: it's the same cell
                
                vertices = self.__db_grid.get(cell_index_en, None)
                if vertices is not None:
                    vertices = vertices[:] # [:] is needed to copy array
                    for i, vertex_en in enumerate(vertices):
                        dist_en_c = sum((vertex_en.co[j] - pos_c[j]) ** 2 for j in range(3))
                        if dist_en_c == 0:
                            del vertices[i]
                    vertices_out.extend(vertices)
                    
                continue
            
            # Gather vertices that cell has
            vertices = self.__db_grid.get(cell_index_en, None)
            if vertices is not None:
                vertices_out.extend(vertices)
        
        # Get vertices that are located in the real distance
        if precision_level == 2:
            
            vertices_new = []
            dist_p2 = dist ** 2
            for vertex_en in vertices_out:
                
                dist_en_c_p2 = sum((vertex_en.co[i] - pos_c[i]) ** 2 for i in range(3))
                if dist_en_c_p2 < dist_p2:
                    vertices_new.append(vertex_en)
                    
            vertices_out = vertices_new
        
        return vertices_out
    
    def debug_get_grid(self):
        return self.__db_grid


#******************************
#---===GUI===
#******************************

class UIConfig(bpy.types.PropertyGroup):
    
    target_object = bpy.props.StringProperty(name="Target Object", default="Plane", description="Target object")
    skin_only_selected = bpy.props.BoolProperty(name="Skin Only Selected Vertices", default=True, description="Skin only selected vertices in a point cloud")
    ignore_error = bpy.props.BoolProperty(name="Ignore Errors", default=True, description="Ignore any errors and continue the skinning")
    dist_for_skin = bpy.props.FloatProperty(name="Dist for Skin", subtype='DISTANCE', min=0.0001, max=10000, default=1, description="Distance for skin (= s)")
    ratio_for_axis = bpy.props.FloatProperty(name="Ratio for Axis", subtype='FACTOR', min=0.1, max=10, default=2, description="Ratio a*s (Distance for axis = a, Distance for skin = s)")
    ratio_for_grid = bpy.props.FloatProperty(name="Ratio for Grid", subtype='FACTOR', min=0.1, max=10, default=3, description="Ratio g*s (Grid size = g, Distance for skin = s)")

class OBJECT_PT_PointCloudSkinner(bpy.types.Panel):
    
    bl_label = "Point Cloud Skinner"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    
    def draw(self, context):

        config = bpy.data.scenes[0].CONFIG_PointCloudSkinner
        layout = self.layout
        layout_col = layout.column()
        
        layout_col.operator("scene.point_cloud_skinner_skin", text="Skin")
        
        layout_col.label("Settings:")
        layout_col.prop_search(config, "target_object", bpy.data, "objects")
        layout_col.prop(config, "dist_for_skin")
        layout_col.prop(config, "ratio_for_axis")
        layout_col.prop(config, "ratio_for_grid")
        layout_col.prop(config, "skin_only_selected")
        layout_col.prop(config, "ignore_error")

        if "Errors" in gbLog:
            if gbLog["Errors"] == 0:
                layout_col.label("Result: skinned successfully with no errors.")
            elif gbLog["Errors"] > 0:
                layout_col.label("Result: occurred %d errors." % gbLog["Errors"])
                layout_col.label("The error log has been output to your ")
                layout_col.label("clipboard. Please send it to the developer ")
                layout_col.label("if you have a trouble. The vertices in ")
                layout_col.label("which an error happened are selected.")
        
class OBJECT_OP_PointCloudSkinner_Skin(bpy.types.Operator):
    
    bl_idname = "scene.point_cloud_skinner_skin"
    bl_label = "Skin a point cloud (Point Cloud Skinner)"
    bl_description = "Skin a point cloud."
    
    @classmethod
    def poll(cls, context):
        return True
        
    def execute(self, context):
        
        config = bpy.data.scenes[0].CONFIG_PointCloudSkinner
        
        gb["TargetObject"] = config.target_object
        gb["MaxAroundDist"] = config.dist_for_skin
        gb["MaxDistForAxis"] = config.ratio_for_axis * config.dist_for_skin
        gb["GridSize"] = [config.ratio_for_grid * config.dist_for_skin] * 3
        gb["TargetVertsMode"] = config.skin_only_selected
        gb["IgnoreErrors"] = config.ignore_error
        
        print("-----Start-----")
        SkinVerts() # main function of skinning
        print("-----Log-----")
        print(gbLog)
        print("(If you have trouble, please send this log to the developer.)")
        
        bpy.context.window_manager.clipboard = str(gbLog)
        
        return {'FINISHED'}


#******************************
#---===Register===
#******************************

def register():
    
    bpy.utils.register_module(__name__)
    bpy.types.Scene.CONFIG_PointCloudSkinner = bpy.props.PointerProperty(type=UIConfig)
    
def unregister():
    
    bpy.utils.unregister_module(__name__)

    if bpy.context.scene.get('CONFIG_PointCloudSkinner') != None:
        del bpy.context.scene['CONFIG_PointCloudSkinner']
    try:
        del bpy.types.Scene.CONFIG_PointCloudSkinner
    except:
        pass

if __name__ == '__main__':
    main()
