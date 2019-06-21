'''
Created on Jun 30, 2016

@author: ashok
'''
import sys, time;
import chenhan_pp.Constants as Constants;
from chenhan_pp.GeodesicComponents import InfoAtVertex, QuoteInfoAtVertex;
from chenhan_pp.MeshData import CombinePointAndNormalTo, CombineTwoNormalsTo;
from chenhan_pp.MeshComponents import EdgePoint;

class ExactMethodForDGP():
    fComputationCompleted = False;
    fLocked = False;
    totalLen = Constants.MAX_VAL;
    nTotalCurves = Constants.MAX_VAL;
    
    indexOfSourceVerts = set();
    nCountOfWindows = 0;
    nTotalMilliSeconds = 0;
    nMaxLenOfWindowQueue = 0;
    nMaxLenOfPseudoSources = 0;
    depthOfResultingTree = 0;
    NPE = 0;
    memory = 0;
    farthestDis = 0;
    m_tableOfResultingPaths = [];
    model = None; #Instance of the RichModel
    nameOfAlgorithm = "--";
    m_InfoAtVertices = [];#Collection of InfoAtVertex instances
    
    def __init__(self, *, inputModel=None, indexOfSourceVerts=None):
        self.nameOfAlgorithm = "ExactMethodForDGP"
        self.model = inputModel;
        self.indexOfSourceVerts = indexOfSourceVerts;
        self.nCountOfWindows = 0;
        self.nMaxLenOfPseudoSources = 0;
        self.nMaxLenOfWindowQueue = 0;
        self.depthOfResultingTree = 0;
        self.totalLen = 0;
        self.fComputationCompleted = False;
        self.fLocked = False;
        self.NPE = 0;
        self.memory = 0;
        self.nTotalCurves = 0;
        self.nameOfAlgorithm = "";
        self.m_InfoAtVertices = [InfoAtVertex() for i in range(self.model.GetNumOfVerts())];
        self.memory += float(self.model.GetNumOfVerts()) * sys.getsizeof(InfoAtVertex) / 1024 / 1024;
    
    def PickShortestPaths(self, num):
        if(num >= self.model.GetNumOfVerts()):
            num = self.model.GetNumOfVerts();
            
        self.nTotalCurves = num;
        self.m_tableOfResultingPaths.clear();
        
        if(num == 0):
            return;
        print('PICKING SHORTEST PATHS ', (self.model.GetNumOfFaces() * num), ((self.model.GetNumOfFaces() * num) < 4e16));
        if(self.model.GetNumOfFaces() * num < 4e16):
            
            if(num >= self.model.GetNumOfVerts()):
#                 self.m_tableOfResultingPaths = [[] for i in range(self.model.GetNumOfVerts())];
                self.m_tableOfResultingPaths = [];
                
                for i in range(self.model.GetNumOfVerts()):
                    self.BackTrace(i);
            
            else:
                step = float(self.model.GetNumOfVerts()) / float(num);
                step = max(1.0, step);
                reservesize = int(self.model.GetNumOfVerts() / step) + 1;
                self.m_tableOfResultingPaths = [[] for i in range(reservesize)];
                
                i = Constants.FLT_EPSILON;
                while(i < self.model.GetNumOfVerts()):
                    self.BackTrace(int(i));
                    i += step;
                                
    
    def BackTrace(self, indexOfVert):
        if(self.m_InfoAtVertices[indexOfVert].birthTime == -1):
            assert(self.model.GetNumOfComponents() != -1 or len(self.model.Neigh(indexOfVert)) != 0);
            print('RETURN EMPTY HANDED, SORRY!');
            return;
        
        self.m_tableOfResultingPaths.append([]);
        vertexNodes = [];
        index = indexOfVert;
        vertexNodes.append(index);
        
        while(self.m_InfoAtVertices[index].disUptodate > Constants.FLT_EPSILON):            
            indexOfParent = self.m_InfoAtVertices[index].indexOfParent;          
            if(self.m_InfoAtVertices[index].fParentIsPseudoSource):
                index = indexOfParent;
            else:
                index = self.m_InfoAtVertices[index].indexOfRootVertOfParent;   
                             
            vertexNodes.append(index);
        
        indexOfSourceVert = index;
        posOfTable = len(self.m_tableOfResultingPaths) - 1;
        
        for i in range(len(vertexNodes) - 1):
            lastVert = vertexNodes[i];
            pt = self.model.ComputeShiftPoint(lastVert);
            self.m_tableOfResultingPaths[posOfTable].append(pt);
            
            if(self.m_InfoAtVertices[lastVert].fParentIsPseudoSource):
                continue;
            
            parentEdgeIndex = self.m_InfoAtVertices[lastVert].indexOfParent;
            edgeIndex = self.model.Edge(parentEdgeIndex).indexOfReverseEdge;
            coord = self.model.GetNew2DCoordinatesByReversingCurrentEdge(parentEdgeIndex, self.model.Edge(parentEdgeIndex).coordOfOppositeVert);
            
            proportion = 1.0 - self.m_InfoAtVertices[lastVert].entryProp;
            
            while(1):
                pt1 = self.model.ComputeShiftPoint(self.model.Edge(edgeIndex).indexOfLeftVert);
                pt2 = self.model.ComputeShiftPoint(self.model.Edge(edgeIndex).indexOfRightVert);
                ptIntersection = CombineTwoNormalsTo(pt1, 1.0 - proportion, pt2, proportion);
                self.m_tableOfResultingPaths[posOfTable].append(ptIntersection);
                
                if(self.model.Edge(edgeIndex).indexOfOppositeVert == vertexNodes[i + 1]):
                    break;
        
                oldProportion = proportion;
                proportion = self.model.ProportionOnLeftEdgeByImage(edgeIndex, coord, oldProportion);
                
                if(proportion >= -Constants.LENGTH_EPSILON_CONTROL and proportion <= 1):
                    proportion = max(proportion, 0.0);
                    coord = self.model.GetNew2DCoordinatesByRotatingAroundLeftChildEdge(edgeIndex, coord);
                    edgeIndex = self.model.Edge(edgeIndex).indexOfLeftEdge;
                
                else:
                    proportion = self.model.ProportionOnRightEdgeByImage(edgeIndex, coord, oldProportion);
                    proportion = max(proportion, 0.0);
                    proportion = min(proportion, 1.0);
                    coord = self.model.GetNew2DCoordinatesByRotatingAroundRightChildEdge(edgeIndex, coord);
                    edgeIndex = self.model.Edge(edgeIndex).indexOfRightEdge;
        
        self.m_tableOfResultingPaths[posOfTable].append(self.model.ComputeShiftPoint(indexOfSourceVert));
#         print('SELF.M_TABLEOFRESULTING PATHS FOR POS OF TABLE ::: ', len(self.m_tableOfResultingPaths[posOfTable]));
    
    
    def FindSourceVertex(self, indexOfVert):
        resultingPath = [];
        
        if(self.m_InfoAtVertices[indexOfVert].birthTime == -1 or self.m_InfoAtVertices[indexOfVert].disUptodate > Constants.FLT_MAX):
            assert(self.model.GetNumOfComponents() != -1 or len(self.model.Neigh(indexOfVert)) != 0);
        
        vertexNodes = [];
        index = indexOfVert;
        vertexNodes.append(index);
        
        while(self.m_InfoAtVertices[index].disUptodate > Constants.FLT_EPSILON):
            indexOfParent = self.m_InfoAtVertices[index].indexOfParent;
            if(self.m_InfoAtVertices[index].fParentIsPseudoSource):
                index = indexOfParent;
            
            else:
                index = self.m_InfoAtVertices[index].indexOfRootVertOfParent;
            
            vertexNodes.append(index);
        
        indexOfSourceVert = index;
        
        for i in range(len(vertexNodes) - 1):
            lastVert = vertexNodes[i];
            resultingPath.append(EdgePoint(index=lastVert));
            
            if(self.m_InfoAtVertices[lastVert].fParentIsPseudoSource):
                continue;
            
            parentEdgeIndex = self.m_InfoAtVertices[lastVert].indexOfParent;
            edgeIndex = self.model.Edge(parentEdgeIndex).indexOfReverseEdge;
            coord = self.model.GetNew2DCoordinatesByReversingCurrentEdge(parentEdgeIndex, self.model.Edge(parentEdgeIndex).coordOfOppositeVert);
            
            proportion = 1.0 - self.m_InfoAtVertices[lastVert].entryProp;
            
            while(1):
                resultingPath.append(EdgePoint(index=edgeIndex, proportion=proportion));
                
                if(self.model.Edge(edgeIndex).indexOfOppositeVert == vertexNodes[i + 1]):
                    break;
                
                oldProportion = proportion;
                proportion = self.model.ProportionOnLeftEdgeByImage(edgeIndex, coord, oldProportion);
                if(self.model.Edge(edgeIndex).indexOfLeftEdge == -1 or self.model.Edge(edgeIndex).indexOfRightEdge == -1):
                    break;
                
                if(proportion >= -Constants.LENGTH_EPSILON_CONTROL and proportion <= 1):
                    proportion = max(proportion, 0.0);
                    coord = self.model.GetNew2DCoordinatesByRotatingAroundLeftChildEdge(edgeIndex, coord);
                    edgeIndex = self.model.Edge(edgeIndex).indexOfLeftEdge;
                
                else:
                    proportion = self.model.ProportionOnRightEdgeByImage(edgeIndex, coord, oldProportion);
                    proportion = max(proportion, 0.0);
                    proportion = min(proportion, 1.0);
                    coord = self.model.GetNew2DCoordinatesByRotatingAroundRightChildEdge(edgeIndex, coord);
                    edgeIndex = self.model.Edge(edgeIndex).indexOfRightEdge;
            
        resultingPath.append(EdgePoint(index=indexOfSourceVert));
        
        return resultingPath, indexOfSourceVert;
            
    
    
    
    def Execute(self):
        if(self.fComputationCompleted):
            return;
        
        if(not self.fLocked):
            self.fLocked = True;
            self.nCountOfWindows = 0;
            self.nMaxLenOfWindowQueue = 0;
            self.depthOfResultingTree = 0;
            
            self.InitContainers();
            
            self.nTotalMilliSeconds = self.GetTickCount();
#             profiler = pprofile.Profile();
#             with profiler:
            self.BuildSequenceTree();
            
#             profiler.print_stats();
            
            
            self.nTotalMilliSeconds = self.GetTickCount() - self.nTotalMilliSeconds;
            
            self.FillExperimentalResults();
            self.ClearContainers();
            
            self.fComputationCompleted = True;
            self.fLocked = False;
    
    
    def GetTickCount(self):
        tb = time.time();
        millis = int(round(tb * 1000));
        nCount = millis + (tb * 0xFFFFFF) * 1000;
        return nCount;
    
    def BuildSequenceTree(self):
        print('ABSTRACT BUILD SEQUENCE TREE');
    
    def FillExperimentalResults(self):
        print('ABSTRAT FILL EXPERIMENTAL RESULTS');
    
    def ClearContainers(self):
        print('ABSTRACT CLEAR CONTAINERS');
    
    def InitContainers(self):
        print('ABSTRACT INIT CONTAINERS');
    
    def GetRunTime(self):
        return self.nTotalMilliSeconds;
    
    def GetMemoryCost(self):
        return self.memory;
    
    def GetWindowNum(self):
        return self.nCountOfWindows;
    
    def GetMaxLenOfQue(self):
        return self.nMaxLenOfWindowQueue;
    
    def GetDepthOfSequenceTree(self):
        return self.depthOfResultingTree;
    
    def GetNPE(self):
        return self.NPE;
    
    def GetAlgorithmName(self):
        return self.nameOfAlgorithm;
    
    def HasBeenCompleted(self):
        return self.fComputationCompleted;
    
    def GetRootSourceOfVert(self, index):
        if (self.m_InfoAtVertices[index].disUptodate > Constants.FLT_MAX):
            return index;
    
        while (self.m_InfoAtVertices[index].disUptodate > Constants.FLT_EPSILON):
            indexOfParent = self.m_InfoAtVertices[index].indexOfParent;
            if (self.m_InfoAtVertices[index].fParentIsPseudoSource):
                index = indexOfParent;
            else:
                index = self.m_InfoAtVertices[index].indexOfRootVertOfParent;
                
        return index;

    