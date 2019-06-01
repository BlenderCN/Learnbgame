'''
Created on Jun 30, 2016

@author: ashok
'''
from collections import deque;
import bpy, bmesh, math;
from mathutils import Vector

import chenhan_pp.Constants as Constants;
# from basics.MeshToolBox import ensurelookuptable;
from chenhan_pp.MeshTools import ensurelookuptable;
from chenhan_pp.stl_classes import Pair, make_pair;
from chenhan_pp.MeshComponents import CEdge, CFace;



def CombinePointAndNormalTo(pt, normal):
    return pt + normal * Constants.RateOfNormalShift;

def CombineTwoNormalsTo(pt1, coef1, pt2, coef2):
    return coef1 * pt1 + coef2 * pt2;


class BaseModel():
    
    m_omesh = None;#The blender mesh object
    m_bmesh = None;#The blender bmesh object
    m_Verts = None;#Collection of Verts of type BMVert
    m_Faces = None;#Collection of Faces of type BMFace
    m_NormalsToVerts = None;#Collection of Normals of type Vector3 (Blender python datatype)
    m_scale = 1;
    m_center = Vector((0.0, 0.0, 0.0));
    m_ptUp = Vector((0.0, 0.0, 0.0));
    m_ptDown = Vector((0.0, 0.0, 0.0));
    
    def __init__(self, bm, meshobject):
        self.m_omesh = meshobject;#The blender mesh object
        self.m_bmesh = bm;#The blender bmesh object
        self.m_Verts = [];#Collection of Verts of type BMVert
        self.m_Faces = [];#Collection of Faces of type BMFace
        self.m_NormalsToVerts = [];#Collection of Normals of type Vector3 (Blender python datatype)
        self.m_scale = 1;
        ensurelookuptable(self.m_bmesh);
        
        dim_mesh = meshobject.dimensions;
        
        maxEdgeLenOfBoundingBox = max([dim_mesh.x, dim_mesh.y, dim_mesh.z]);
        cx = (dim_mesh.x / 2.0) + meshobject.location.x;
        cy = (dim_mesh.x / 2.0) + meshobject.location.x;
        cz = (dim_mesh.x / 2.0) + meshobject.location.x;
        
        self.m_scale = 2.0 / maxEdgeLenOfBoundingBox;
        self.m_center = Vector((cx, cy, cz));
        
        for v in self.m_bmesh.verts:
            self.m_Verts.append(v.co);
            self.m_NormalsToVerts.append(v.normal);
        
        for f in self.m_bmesh.faces:
            face = CFace(f.verts[0].index, f.verts[1].index, f.verts[2].index);
            self.m_Faces.append(face); 
            

    def GetNumOfVerts(self):
        return len(self.m_Verts);
    
    def GetNumOfFaces(self):
        return len(self.m_Faces);
    
    def Vert(self, index):
        return self.m_Verts[index];
    
    def Normal(self, index):
        return self.m_NormalsToVerts[index];
    
    def Face(self, index):
        return self.m_Faces[index];
    


class RichModel(BaseModel):
    m_nBoundaries = 0;#Total number of boundaries
    m_nIsolatedVerts = 0;#Total number of isolatedverts
    m_nComponents = 0;#
    m_NeighsAndAngles = None;#Angles of neibhours for each vertices
    m_FlagsForCheckingConvexVerts = None;#List of booleans for showing if a vertex is convex or not
    m_Edges = None;#List of Edges containing isntance of CEDGE
    fBePreprocessed = False;
    fLocked = True;
    
    def __init__(self, bm, meshobject):
        super().__init__(bm, meshobject);
        self.m_nBoundaries = -1;#Total number of boundaries
        self.m_nIsolatedVerts = -1;#Total number of isolatedverts
        self.m_nComponents = -1;#
        self.m_NeighsAndAngles = None;#Angles of neibhours for each vertices
        self.m_FlagsForCheckingConvexVerts = None;#List of booleans for showing if a vertex is convex or not
        self.m_Edges = None;#List of Edges containing isntance of CEDGE
        self.fBePreprocessed = False;
        self.fLocked = True;
        
    def CreateEdgesFromVertsAndFaces(self):
        pondOfUndeterminedEdges = {};
        
        sZFaces = self.GetNumOfFaces();
        
        for i in range(sZFaces):
            threeindices = [None, None, None];
                  
            for j in range(3):
                post = (j + 1) % 3;
                pre = (j + 2) % 3;   
                             
                leftVert = self.Face(i)[pre];
                rightVert = self.Face(i)[j];
                
                it = pondOfUndeterminedEdges.get(make_pair(leftVert, rightVert));
                
                if(it):
                    posInEdgeList = it;
                    
                    if(self.m_Edges[posInEdgeList].indexOfOppositeVert != -1):
                        raise ValueError('Repeated Edges!')
                    
                    threeindices[j] = posInEdgeList;
                    self.m_Edges[posInEdgeList].indexOfOppositeVert = self.Face(i)[post];
                    self.m_Edges[posInEdgeList].indexOfFrontFace = i;
                    
                else:
                    edge = CEdge();
                    edge.edge_length = max(Constants.FLT_EPSILON, (self.Vert(leftVert) - self.Vert(rightVert)).length);
                    edge.indexOfLeftVert = leftVert;
                    edge.indexOfRightVert = rightVert;
                    edge.indexOfReverseEdge = len(self.m_Edges) + 1;
                    edge.indexOfFrontFace = i;
                    edge.indexOfOppositeVert = self.Face(i)[post];
                    self.m_Edges.append(edge);
                    
                    pairofvert = make_pair(leftVert, rightVert);
                    pondOfUndeterminedEdges[pairofvert] = len(self.m_Edges) - 1;
                    threeindices[j] = len(self.m_Edges) - 1;
                    
                    edge = CEdge();
                    edge.edge_length = max(Constants.FLT_EPSILON, (self.Vert(leftVert) - self.Vert(rightVert)).length);
                        
                    edge.indexOfLeftVert = rightVert;
                    edge.indexOfRightVert = leftVert;
                    edge.indexOfReverseEdge = len(self.m_Edges) - 1;
                    edge.indexOfFrontFace = -1;
                    edge.indexOfOppositeVert = -1;                    
                    self.m_Edges.append(edge);
                    pondOfUndeterminedEdges[make_pair(rightVert, leftVert)] = len(self.m_Edges) - 1;
                
            for j in range(3):
                self.m_Edges[threeindices[j]].indexOfLeftEdge = self.Edge(threeindices[(j + 2) % 3]).indexOfReverseEdge;
                self.m_Edges[threeindices[j]].indexOfRightEdge = self.Edge(threeindices[(j + 1) % 3]).indexOfReverseEdge;
        
        
    def CollectAndArrangeNeighs(self):
        self.m_nIsolatedVerts = 0;
        sequenceOfDegrees = [0 for it in range(self.GetNumOfVerts())];
        #The below should be a resize operation essentially. But the below statement is okay
        #because this is the first time the list itself is created
        self.m_NeighsAndAngles = [ [] for i in range(self.GetNumOfVerts())];
        for i in range(len(self.m_NeighsAndAngles)):
            self.m_NeighsAndAngles[i].extend([make_pair(-1, 0)]);

        
        for i in range(self.GetNumOfEdges()):
            edge = self.Edge(i);
            sequenceOfDegrees[edge.indexOfLeftVert] += 1;
            indexOfStartEdge = self.m_NeighsAndAngles[edge.indexOfLeftVert][0].first;
            
            if(indexOfStartEdge == -1 or not self.IsStartEdge(indexOfStartEdge)):
                indexOfStartEdge = i;
                self.m_NeighsAndAngles[edge.indexOfLeftVert][0].first = i;
            
            elif(self.IsStartEdge(i)):
                self.m_NeighsAndAngles[edge.indexOfLeftVert].append(make_pair(i, 0));
                
#         print('SEQUENCE OF DEGREES ::: ', sequenceOfDegrees);
        
        for i in range(self.GetNumOfVerts()):
            
            if(self.m_NeighsAndAngles[i][0].first == -1):
                self.m_NeighsAndAngles[i] = [];
                self.m_nIsolatedVerts += 1;
                continue;
            
            startEdges = [];
            
            for j in range(len(self.Neigh(i))):
                startEdges.append(self.Neigh(i)[j].first);
            
            #The below is typically the resize operation equivalent of C++
            #In the C++ if the list is already of a size given in resize with
            #existing elements, then it does not touch the elements nor changes anything
            #But if the resizing size is higher than the current size then it will append 
            #new elements to the difference of old size and new size;
            if(sequenceOfDegrees[i] > len(self.m_NeighsAndAngles[i])):
                difflen = sequenceOfDegrees[i] - len(self.m_NeighsAndAngles[i]);
                self.m_NeighsAndAngles[i].extend([make_pair(0,0) for j in range(difflen)]);  
                
                          
            num = 0;            
            for j in range(len(startEdges)):                
                curEdge = startEdges[j];
                while(True):
                    self.m_NeighsAndAngles[i][num].first = curEdge;                    
                    num += 1;
                    
                    if(num >= sequenceOfDegrees[i]):
                        break;
                    
                    if(self.IsExtremeEdge(curEdge)):
                        break;
                    
                    curEdge = self.Edge(curEdge).indexOfLeftEdge;
                    
                    if(curEdge == startEdges[j]):
                        break;
            
            if(num != sequenceOfDegrees[i]):
                raise ValueError("Complex vertices");
    
    def ComputeAnglesAroundVerts(self):
        self.m_FlagsForCheckingConvexVerts = [False for i in range(self.GetNumOfVerts())];
        
        for i in range(len(self.m_NeighsAndAngles)):
            neighSize = len(self.Neigh(i));
            if(neighSize > len(self.m_NeighsAndAngles[i])):
                diffLen = neighSize - len(self.m_NeighsAndAngles[i]);
                self.m_NeighsAndAngles[i].extend([make_pair(0,0)] for j in range(diffLen));
    
        
        for i in range(len(self.m_NeighsAndAngles)):
            angleSum = 0;
            
            for j in range(len(self.m_NeighsAndAngles[i])):
                
                if(self.IsExtremeEdge(self.Neigh(i)[j].first)):
                    self.m_NeighsAndAngles[i][j].second = 2 * math.pi + 0.1;
                
                else:
                    next = j + 1;
                    
                    if(next >= len(self.m_NeighsAndAngles[i])):
                        next = 0;
                    
                    #Essentially left, right, and bottom
                    l = self.Edge(self.Neigh(i)[j].first).edge_length;
                    r = self.Edge(self.Neigh(i)[next].first).edge_length;
                    b = self.Edge(self.Edge(self.Neigh(i)[j].first).indexOfRightEdge).edge_length;
                    
                    try:
                        costheta = (l**2 + r**2 - b**2) / (2 * l * r);
                        self.m_NeighsAndAngles[i][j].second = math.acos(min(1.0, max(-1.0, costheta)));
                    except ZeroDivisionError:
                        self.m_NeighsAndAngles[i][j].second = 0;

                angleSum += self.m_NeighsAndAngles[i][j].second;
            
            self.m_FlagsForCheckingConvexVerts[i] = (angleSum < ((2 * math.pi) - Constants.ToleranceOfConvexAngle));
            
#         print("SIZE OF MAIN ARRAY ::: ", len(self.m_NeighsAndAngles));
#     
#         for item in self.m_NeighsAndAngles:
#             print('SIZE OF INNER ARRAY ::: ', len(item));
#             for pair in item:
#                 print(pair.first, pair.second);
            
    def ComputePlanarCoordsOfIncidentVertForEdges(self):
        for i in range(self.GetNumOfEdges()):
            if(self.IsExtremeEdge(i)):
                continue;
            
            bottom = self.Edge(i).edge_length;
            leftLen = self.Edge(self.Edge(i).indexOfLeftEdge).edge_length;
            squareOfLeftLen = leftLen**2;
            rightLen = self.Edge(self.Edge(i).indexOfRightEdge).edge_length;
            if(bottom < Constants.FLT_EPSILON):
                bottom = Constants.FLT_EPSILON;
            x = (squareOfLeftLen - rightLen**2 ) / bottom + bottom;
            x /= 2.0;
            self.m_Edges[i].coordOfOppositeVert = make_pair(x, (max(0.0, squareOfLeftLen - x**2))**0.5);
        
        
        for i in range(self.GetNumOfEdges()):
            if(self.IsExtremeEdge(i)):
                continue;
            
            reverseEdge = self.m_Edges[self.m_Edges[i].indexOfLeftEdge].indexOfReverseEdge;
            coord = self.GetNew2DCoordinatesByReversingCurrentEdge(reverseEdge, self.m_Edges[reverseEdge].coordOfOppositeVert);
            scale = abs(coord.first) + abs(coord.second);
            if(scale < Constants.FLT_EPSILON):
                scale = Constants.FLT_EPSILON;
            coord.first *= (1.0 / scale);
            coord.second *= (1.0 / scale);            
            leng = (coord.first**2 + coord.second**2)**0.5;
            
            if(leng < Constants.FLT_EPSILON):
                leng = Constants.FLT_EPSILON;
            
            self.m_Edges[i].matrixRotatedToLeftEdge = make_pair(coord.first / leng , coord.second / leng);
            
            
            reverseEdge = self.m_Edges[self.m_Edges[i].indexOfRightEdge].indexOfReverseEdge;
            rightX = self.m_Edges[reverseEdge].edge_length;
            rightY = 0;
            leftX = self.m_Edges[reverseEdge].edge_length - self.m_Edges[reverseEdge].coordOfOppositeVert.first;
            leftY = -self.m_Edges[reverseEdge].coordOfOppositeVert.second;

            detaX = rightX - leftX;
            detaY = rightY - leftY;
            scale = abs(detaX) + abs(detaY);
            
            if(scale < Constants.FLT_EPSILON):
                scale = Constants.FLT_EPSILON;
                
#             if(scale != 0.0):
            detaX *= (1.0 / scale);
            detaY *= (1.0 / scale);
            leng = (detaX**2 + detaY**2)**0.5;
            if(leng < Constants.FLT_EPSILON):
                leng = Constants.FLT_EPSILON;
            self.m_Edges[i].matrixRotatedToRightEdge = make_pair(detaX / leng, detaY / leng);
                
#             else:
#                 detaX = detaY = 0;
#                 self.m_Edges[i].matrixRotatedToRightEdge = make_pair(detaX, detaY);
            
    
    def Preprocess(self):
        self.ClearEdges();
        self.CreateEdgesFromVertsAndFaces();
        self.CollectAndArrangeNeighs();
        self.ComputeNumOfHoles();
        self.ComputeNumOfComponents();
        self.ComputeAnglesAroundVerts();
        self.ComputePlanarCoordsOfIncidentVertForEdges();
        
#         for ce in self.m_Edges:
#             print(ce.coordOfOppositeVert.first, ce.coordOfOppositeVert.second);
    
    def ComputeNumOfHoles(self):
        
        self.m_nBoundaries = 0;
        
        if(self.IsClosedModel()):
            return;
        
        extremeEdges = set();
        
        for i in range(self.GetNumOfEdges()):
            if(self.Edge(i).indexOfOppositeVert != -1):
                continue;            
            extremeEdges.add(i);
        #This is where python sucks despite being a beautiful language, no do-while. 
        #Can be implemented with a work around but not in a straight-forward fashion
        #No girlfriend for a boy, nor no boyfriend of a girl will be ever perfect
        #But I am still happy with my girlfriend python, she is the best ever....
        while(len(extremeEdges)):
            self.m_nBoundaries += 1;
            firstEdge = min(extremeEdges);
            edge = firstEdge;
            try:
                extremeEdges.remove(edge);
                root = self.Edge(edge).indexOfRightVert;
                index = self.GetSubindexToVert(root, self.Edge(edge).indexOfLeftVert);
                edge = self.Neigh(root)[(index - 1 + len(self.Neigh(root))) % len(self.Neigh(root)) ].first;
            except KeyError:
                pass;            
            
            while(edge != firstEdge and len(extremeEdges)):
                try:
                    extremeEdges.remove(edge);
                    root = self.Edge(edge).indexOfRightVert;
                    index = self.GetSubindexToVert(root, self.Edge(edge).indexOfLeftVert);
                    edge = self.Neigh(root)[(index - 1 + len(self.Neigh(root))) % len(self.Neigh(root)) ].first;
                except KeyError:
                    pass;      
                
    def ComputeNumOfComponents(self):
        self.m_nComponents = 0;
        
        flags = [False for i in range(self.GetNumOfVerts())];
        cnt = 0;
        
        while(cnt < self.GetNumOfVerts()):
            v = -1;
            
            for i in range(len(flags)):
                if(not flags[i]):
                    v = i;
                    break;
                
            Que = deque();
            Que.append(v);
            
            while(len(Que)):
                v = Que[0];
                Que.popleft();
                if(flags[v]):
                    continue;
                flags[v] = True;
                cnt += 1;
                for i in range(len(self.Neigh(v))):
                    if(not flags[self.Edge(self.Neigh(v)[i].first).indexOfRightVert]):
                        Que.append(self.Edge(self.Neigh(v)[i].first).indexOfRightVert);
            
            
            self.m_nComponents += 1;            
            
                    
    def ClearEdges(self):
        self.m_nBoundaries = 0;
        self.m_nIsolatedVerts = 0;
        self.m_NeighsAndAngles = [];
        self.m_FlagsForCheckingConvexVerts = [];
        self.m_Edges = [];
    
    def Edge(self, index):
        return self.m_Edges[index];
    
    def Neigh(self, rootindex):
        return self.m_NeighsAndAngles[rootindex]
    
    def IsExtremeEdge(self, edgeindex):
        return (self.m_Edges[edgeindex].indexOfOppositeVert == -1);
    
    def IsStartEdge(self, edgeindex):
        return self.m_Edges[self.Edge(edgeindex).indexOfReverseEdge].indexOfOppositeVert == -1;
    
    def IsClosedModel(self):
        return (self.GetNumOfValidDirectedEdges() == self.GetNumOfEdges());
    
    def GetNumOfValidDirectedEdges(self):
        return len(self.m_Faces) * 3;
    
    def GetNumOfEdges(self):
        return len(self.m_Edges);
    
    def GetSubindexToVert(self, root, neigh):        
        for i in range(len(self.Neigh(root))):
            if(self.Edge(self.Neigh(root)[i].first).indexOfRightVert == neigh):
                return i;            
        return -1;
        
    def GetNumOfTotalUndirectedEdges(self):
        return len(self.m_Edges) / 2;
    
    def GetNumOfGenera(self):
        return ((self.GetNumOfTotalUndirectedEdges() - (self.GetNumOfVerts() - self.m_nIsolatedVerts) - self.GetNumOfFaces() - self.GetNumOfBoundries()) / 2) + 1;
    
    def GetNumOfComponents(self):
        return self.m_nComponents;
    
    def GetNumOfBoundries(self):
        return self.m_nBoundries;
    
    def GetNumOfIsolated(self):
        return self.m_nIsolatedVerts;
    
    def isBoundaryVert(self, index):
        return self.IsStartEdge(self.Neigh(index)[0].first);
    
    def IsConvexVert(self, index):
        return self.m_FlagsForCheckingConvexVerts[index];
    
    def ProportionOnEdgeByImage(self, edgeIndex, coord=None, x11=None, y11=None, x22=None, y22=None):
        if(coord):
#             res = self.Edge(edgeIndex).coordOfOppositeVert.first * coord.second - self.Edge(edgeIndex).coordOfOppositeVert.second * coord.first;
            res = self.m_Edges[edgeIndex].coordOfOppositeVert.first * coord.second - self.m_Edges[edgeIndex].coordOfOppositeVert.second * coord.first;
            denominator = ((coord.second - self.m_Edges[edgeIndex].coordOfOppositeVert.second) * self.m_Edges[edgeIndex].edge_length);
            if(denominator > 0.0):
                return res / denominator;
            elif(denominator < 0.0):
                return res * denominator**-1.0;
            else:
                res * Constants.FLT_EPSILON_INV;
        else:
            x1 = x11;
            x2 = x22;
            y1 = y11;
            y2 = y22;      
            res = x1 * y2 - x2 * y1;
            denominator = ((y2 - y1) * self.m_Edges[edgeIndex].edge_length);
            if(denominator > 0.0):
                return res / denominator;
            elif(denominator < 0.0):
                return res * denominator**-1.0;
            else:
                return res * Constants.FLT_EPSILON_INV;
    
    def ProportionOnLeftEdgeByImage(self,  edgeIndex, coord, proportion):
        xBalance = float(proportion) * self.m_Edges[edgeIndex].edge_length;
        res = self.m_Edges[edgeIndex].coordOfOppositeVert.first * coord.second - self.m_Edges[edgeIndex].coordOfOppositeVert.second * (coord.first - xBalance);
        if(res > 0.0):
            return xBalance * coord.second / res;
        elif(res < 0.0):
            return xBalance * coord.second * res**-1.0;
        else:
            return (xBalance * coord.second * Constants.FLT_EPSILON_INV);
    
    def ProportionOnRightEdgeByImage(self,  edgeIndex, coord, proportion):
        part1 = self.m_Edges[edgeIndex].edge_length * coord.second;
        part2 = proportion * self.m_Edges[edgeIndex].edge_length * self.m_Edges[edgeIndex].coordOfOppositeVert.second;
        part3 = self.m_Edges[edgeIndex].coordOfOppositeVert.second * coord.first - self.m_Edges[edgeIndex].coordOfOppositeVert.first * coord.second;    
        
        denominator = part3 + part1 - part2;
        if(denominator > 0.0):
            return (part3 + proportion * part1 - part2) / denominator;
        elif(denominator < 0.0):
            return (part3 + proportion * part1 - part2) * denominator**-1.0;
        else:
#             print("ZERO DIVISION ERROR ::: " , part1, part2, part3, (part1 - part2) ,(part3 + part1 - part2));
            return (part3 + proportion * part1 - part2) * Constants.FLT_EPSILON_INV;
#         try:
#             return (part3 + proportion * part1 - part2) / (part3 + part1 - part2);
#         except ZeroDivisionError:
#             print("ZERO DIVISION ERROR ::: " , part1, part2, part3, (part1 - part2) ,(part3 + part1 - part2));
#             return (part3 + proportion * part1 - part2) / Constants.FLT_EPSILON;
    
    def GetNew2DCoordinatesByRotatingAroundLeftChildEdge(self, edgeIndex, input2DCoordinates):
        
        return make_pair(
                         self.m_Edges[edgeIndex].matrixRotatedToLeftEdge.first * input2DCoordinates.first - self.m_Edges[edgeIndex].matrixRotatedToLeftEdge.second * input2DCoordinates.second, 
                         self.m_Edges[edgeIndex].matrixRotatedToLeftEdge.second * input2DCoordinates.first + self.m_Edges[edgeIndex].matrixRotatedToLeftEdge.first * input2DCoordinates.second);
    
    def GetNew2DCoordinatesByRotatingAroundRightChildEdge(self,  edgeIndex, input2DCoordinates):
        reverseEdge = self.m_Edges[self.m_Edges[edgeIndex].indexOfRightEdge].indexOfReverseEdge;
        coordOfLeftEnd = self.GetNew2DCoordinatesByReversingCurrentEdge(reverseEdge, self.m_Edges[reverseEdge].coordOfOppositeVert);
        
        return make_pair(
                         self.m_Edges[edgeIndex].matrixRotatedToRightEdge.first * input2DCoordinates.first - self.m_Edges[edgeIndex].matrixRotatedToRightEdge.second * input2DCoordinates.second + coordOfLeftEnd.first,
                         self.m_Edges[edgeIndex].matrixRotatedToRightEdge.second * input2DCoordinates.first + self.m_Edges[edgeIndex].matrixRotatedToRightEdge.first * input2DCoordinates.second + coordOfLeftEnd.second);
    
    def GetNew2DCoordinatesByReversingCurrentEdge(self, edgeIndex, input2DCoordinates):
        return make_pair(self.m_Edges[edgeIndex].edge_length - input2DCoordinates.first, -input2DCoordinates.second);
    
    def HasBeenProcessed(self):
        return self.fBePreprocessed;
    
    def ComputeShiftPoint(self, indexOfVert, epsilon=None):
        if(epsilon):
            return self.Vert(indexOfVert) +  self.Normal(indexOfVert) * epsilon;
        
        return (self.Vert(indexOfVert) + (self.Normal(indexOfVert) * Constants.RateOfNormalShift)) / self.m_scale;
    
    def AngleSum(self, vertIndex):
        angleSum = 0;
        
        for j in range(len(self.m_NeighsAndAngles[vertIndex])):
            angleSum += self.m_NeighsAndAngles[vertIndex][j].second;

        return angleSum;
    
    def DistanceToIncidentAngle(self, edgeIndex, coord):
        detaX = coord.first - self.m_Edges[edgeIndex].coordOfOppositeVert.first;
        detaY = coord.second - self.m_Edges[edgeIndex].coordOfOppositeVert.second;
        return (detaX**2 + detaY**2)**0.5;
    
    
    def GetEdgeIndexFromTwoVertices(self, leftVert, rightVert):
        subIndex = self.GetSubindexToVert(leftVert, rightVert);
        assert (subIndex != -1);
        return self.Neigh(leftVert)[subIndex].first;
    
    
    
        
        
        
        
    