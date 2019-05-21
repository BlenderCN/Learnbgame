
from . import wmo_format
from .wmo_format import *

from . import Collision
from .Collision import *

import mathutils
from mathutils import *

import sys

class BSP_Tree:
    def __init__(self):
        self.Nodes = []
        self.Faces = []
        pass
    
    # split box in two smaller, at dist calculated internally
    def SplitBox(self, box, facesInBox, vertices, indices, axis):
        # compute average of vertice positions
        """count = 0
        sum = 0
        for iFace in range(len(facesInBox)):
            sum += vertices[indices[facesInBox[iFace] * 3]][axis]
            sum += vertices[indices[facesInBox[iFace] * 3 + 1]][axis]
            sum += vertices[indices[facesInBox[iFace] * 3 + 2]][axis]
            count += 1
        splitDist = sum / count

        # if split is out of box, just split in half
        if(splitDist <= box[0][axis] or splitDist >= box[1][axis]):"""
        splitDist = (box[0][axis] + box[1][axis]) / 2
            
        newBox1 = (Vector((box[0][0], box[0][1], box[0][2])), Vector((box[1][0], box[1][1], box[1][2])))
        newBox1[1][axis] = splitDist

        newBox2 = (Vector((box[0][0], box[0][1], box[0][2])), Vector((box[1][0], box[1][1], box[1][2])))
        newBox2[0][axis] = splitDist

        # split dist absolute coordinate on split axis
        #ret_splitDist = splitDist - ((box[0][axis] + box[1][axis]) / 2)
        return (splitDist, newBox1, newBox2)

    # return index of add
    def AddNode(self, box, facesInBox, vertices, indices, maxFaceCount):
        
        node = BSP_Node()

        iNode = len(self.Nodes)
        self.Nodes.append(node)
        
        # part contain less than 30 polygons, lets end this, add final node
        if(len(facesInBox) <= maxFaceCount):
            node.PlaneType = BSP_PLANE_TYPE.Leaf
            node.Childrens = (-1, -1)
            node.NumFaces = len(facesInBox)
            node.FirstFace = len(self.Faces)
            node.Dist = 0

            self.Faces.extend(facesInBox)
            return iNode

        # split bigger side
        box_size_x = box[1][0] - box[0][0]
        box_size_y = box[1][1] - box[0][1]
        box_size_z = box[1][2] - box[0][2]


        if box_size_x > box_size_y and box_size_x > box_size_z:
            # split on axis X (YZ plane)
            planeType = BSP_PLANE_TYPE.YZ_plane
        elif box_size_y > box_size_x and box_size_y > box_size_z:
            #split on axis Y (XZ plane)
            planeType = BSP_PLANE_TYPE.XZ_plane
        else:
            # split on axis Z (XY plane)
            planeType = BSP_PLANE_TYPE.XY_plane
            

        splitResult = self.SplitBox(box, facesInBox, vertices, indices, planeType)

        splitDist = splitResult[0]

        child1_box = splitResult[1]
        child1_faces = []

        # calculate faces in child1 box
        for f in facesInBox:
            v0 = Vector((vertices[indices[f * 3]]))
            v1 = Vector((vertices[indices[f * 3 + 1]]))
            v2 = Vector((vertices[indices[f * 3 + 2]]))
            tri = (v0, v1, v2)
            if(CollideBoxTri(child1_box, tri)):
                child1_faces.append(f)

        child2_box = splitResult[2]
        child2_faces = []

        # calculate faces in child2 box
        for f in facesInBox:
            v0 = Vector((vertices[indices[f * 3]]))
            v1 = Vector((vertices[indices[f * 3 + 1]]))
            v2 = Vector((vertices[indices[f * 3 + 2]]))
            tri = (v0, v1, v2)
            if(CollideBoxTri(child2_box, tri)):
                child2_faces.append(f)

        # dont add child if there is no faces inside
        if(len(child1_faces) == 0):
            iChild1 = -1
        else:
            iChild1 = self.AddNode(child1_box, child1_faces, vertices, indices, maxFaceCount)
            
        if(len(child2_faces) == 0):
            iChild2 = -1
        else:
            iChild2 = self.AddNode(child2_box, child2_faces, vertices, indices, maxFaceCount)

        #node = BSP_Node()
        node.PlaneType = planeType
        node.Childrens = (iChild1, iChild2)
        node.NumFaces = 0
        node.FirstFace = 0
        node.Dist = splitDist
        
        return iNode

    def GenerateBSP(self, vertices, indices, maxFaceCount):
        resursLimit = sys.getrecursionlimit()
        sys.setrecursionlimit(2000)

        faces = []
        for iFace in range(len(indices) // 3):
            faces.append(iFace)

        box = CalculateBoundingBox(vertices)
        self.AddNode(box, faces, vertices, indices, maxFaceCount)

        sys.setrecursionlimit(resursLimit)
        return