'''
Created on Jun 30, 2016

@author: ashok
'''
import sys, math, gc;
from collections import deque;
import chenhan_pp.Constants as Constants;
from chenhan_pp.GeodesicComponents import QuoteWindow, QuoteInfoAtVertex, InfoAtVertex, InfoAtAngle, Window
from chenhan_pp.ExactMethodForDGP import ExactMethodForDGP
from queue import Queue;

class PreviousCH(ExactMethodForDGP):
    m_QueueForWindows = None;#A Queue object
    m_QueueForPseudoSources = None;#A Queue object
    m_InfoAtAngles = None;#A simple list object
    
    def __init__(self, *, inputModel=None, indexOfSourceVerts=None):
        super().__init__(inputModel=inputModel, indexOfSourceVerts=indexOfSourceVerts);
        self.nameOfAlgorithm = "CH";        
    
    def InitContainers(self):
#         self.m_QueueForPseudoSources = deque();
#         self.m_QueueForWindows = deque();
        self.m_QueueForPseudoSources = Queue();
        self.m_QueueForWindows = Queue();
        self.m_InfoAtAngles = [InfoAtAngle() for i in range(self.model.GetNumOfEdges())];
        self.memory += float(self.model.GetNumOfEdges()) * sys.getsizeof(InfoAtAngle) / 1024 / 1024;
    
    def BuildSequenceTree(self):
        self.ComputeChildrenOfSource();
        fFromQueueOfPseudoSources = self.UpdateTreeDepthBackWithChoice();
        
        while (self.depthOfResultingTree < self.model.GetNumOfFaces() and not (self.m_QueueForPseudoSources.empty() and self.m_QueueForWindows.empty())):
#             print('------------------------------------------------------------');
#             print('DEPTHOFRESULTINGTREE, QUEUEFORPSEUDOSOURCES, QUEUEFORWINDOWS');
#             print(self.depthOfResultingTree, len(self.m_QueueForPseudoSources), len(self.m_QueueForWindows));
#             print('BEFORE UPDATING FROMQUEUOFPSEUDOSOURCES', int(fFromQueueOfPseudoSources));
            
            if (self.m_QueueForWindows.qsize() > self.nMaxLenOfWindowQueue):
                self.nMaxLenOfWindowQueue = self.m_QueueForWindows.qsize();
                
            if (self.m_QueueForPseudoSources.qsize() > self.nMaxLenOfPseudoSources):
                self.nMaxLenOfPseudoSources = self.m_QueueForPseudoSources.qsize();
                
            if (fFromQueueOfPseudoSources):
                item = self.m_QueueForPseudoSources.get();
                indexOfVert = item.indexOfVert;         
                self.ComputeChildrenOfPseudoSource(indexOfVert);

            else:
                quoteW = self.m_QueueForWindows.get();
                self.ComputeChildrenOfWindow(quoteW);
                quoteW.pWindow = None;

            fFromQueueOfPseudoSources = self.UpdateTreeDepthBackWithChoice();
#             print('AFTER UPDATING FROMQUEUOFPSEUDOSOURCES', int(fFromQueueOfPseudoSources));
#             print('------------------------------------------------------------');

    
    def FillExperimentalResults(self):
        self.NPE = 1;
    
    def ClearContainers(self):
        self.m_QueueForWindows = Queue();
        self.m_QueueForPseudoSources = Queue();    
    
    def AddIntoQueueOfPseudoSources(self, quoteOfPseudoSource):
#         self.m_QueueForPseudoSources.append(quoteOfPseudoSource);
        self.m_QueueForPseudoSources.put(quoteOfPseudoSource);
    
    def AddIntoQueueOfWindows(self, quoteW):
        self.m_QueueForWindows.put(quoteW);
        self.nCountOfWindows += 1;
    
    def UpdateTreeDepthBackWithChoice(self):
        while (not self.m_QueueForPseudoSources.empty() and (self.m_QueueForPseudoSources.queue[0].birthTime != self.m_InfoAtVertices[self.m_QueueForPseudoSources.queue[0].indexOfVert].birthTime)):
            self.m_QueueForPseudoSources.get();
    
        while (not self.m_QueueForWindows.empty()):
            quoteW = self.m_QueueForWindows.queue[0];
            if (quoteW.pWindow.fParentIsPseudoSource):
                if (quoteW.pWindow.birthTimeOfParent != self.m_InfoAtVertices[quoteW.pWindow.indexOfParent].birthTime):
                    quoteW.pWindow = None;
                    self.m_QueueForWindows.get();
                else:
                    break;
            else:
                if (quoteW.pWindow.birthTimeOfParent == self.m_InfoAtAngles[quoteW.pWindow.indexOfParent].birthTime):
                    break;
                elif (quoteW.pWindow.fIsOnLeftSubtree == (quoteW.pWindow.entryPropOfParent < self.m_InfoAtAngles[quoteW.pWindow.indexOfParent].entryProp)):
                    break;
                else:
                    quoteW.pWindow = None;
                    self.m_QueueForWindows.get();
    
        fFromQueueOfPseudoSources = False;        
        if (self.m_QueueForWindows.empty()):
            if (not self.m_QueueForPseudoSources.empty()):
                infoOfHeadElemOfPseudoSources = self.m_InfoAtVertices[self.m_QueueForPseudoSources.queue[0].indexOfVert];
                self.depthOfResultingTree = max(self.depthOfResultingTree, infoOfHeadElemOfPseudoSources.level);
                fFromQueueOfPseudoSources = True;
        else:
            if (self.m_QueueForPseudoSources.empty()):
                infoOfHeadElemOfWindows = self.m_QueueForWindows.queue[0].pWindow;
                self.depthOfResultingTree = max(self.depthOfResultingTree, infoOfHeadElemOfWindows.level);
                fFromQueueOfPseudoSources = False;
            else:
                infoOfHeadElemOfPseudoSources = self.m_InfoAtVertices[self.m_QueueForPseudoSources.queue[0].indexOfVert];
                infoOfHeadElemOfWindows = self.m_QueueForWindows.queue[0].pWindow;
                
                if (infoOfHeadElemOfPseudoSources.level <= infoOfHeadElemOfWindows.level):
                    self.depthOfResultingTree = max(self.depthOfResultingTree, infoOfHeadElemOfPseudoSources.level);
                    fFromQueueOfPseudoSources = True;
                else:
                    self.depthOfResultingTree = max(self.depthOfResultingTree, infoOfHeadElemOfWindows.level);
                    fFromQueueOfPseudoSources = False;
        
        return fFromQueueOfPseudoSources;
    
    def CheckValidityOfWindow(self, w):
        return True;
    
    def IsTooNarrowWindow(self, w):
        return ((w.proportions[1] - w.proportions[0]) < Constants.LENGTH_EPSILON_CONTROL);
    
    def ComputeChildrenOfSource(self, indexOfSourceVert=-1):
        if(indexOfSourceVert != -1):
            self.m_InfoAtVertices[indexOfSourceVert].birthTime += 1;
            self.m_InfoAtVertices[indexOfSourceVert].level = 0;
            self.m_InfoAtVertices[indexOfSourceVert].disUptodate = 0.0;
            degree = len(self.model.Neigh(indexOfSourceVert));
            
            for i in range(degree):
                self.FillVertChildOfPseudoSource(indexOfSourceVert, i);
            
            for i in range(degree):
                self.CreateIntervalChildOfPseudoSource(indexOfSourceVert, i);
        else:
            for it in self.indexOfSourceVerts:
                if (it >= self.model.GetNumOfVerts()):
                    continue;
                self.ComputeChildrenOfSource(indexOfSourceVert=it);
                
    
    def ComputeChildrenOfPseudoSourceFromPseudoSource(self, indexOfParentVertex):        
        degree = len(self.model.Neigh(indexOfParentVertex));
        neighs = self.model.Neigh(indexOfParentVertex);
        indexOfParentOfParent = self.m_InfoAtVertices[indexOfParentVertex].indexOfParent;
        subIndex = self.model.GetSubindexToVert(indexOfParentVertex, indexOfParentOfParent);
        angleSum = 0.0;
        indexPlus = subIndex;
        
        while(indexPlus != ((subIndex - 1 + degree) % degree)):
            angleSum += neighs[indexPlus].second;
            if (angleSum > (Constants.M_PI - Constants.ToleranceOfConvexAngle)):
                break;
            indexPlus = (indexPlus + 1) % degree;        
        
        angleSum = 0.0;
        indexMinus = (subIndex - 1 + degree) % degree;
        
        while((indexMinus == (subIndex - 1 + degree) % degree) or (indexMinus != (indexPlus - 1 + degree) % degree)):            
            angleSum += neighs[indexMinus].second;
            if (angleSum > (Constants.M_PI - Constants.ToleranceOfConvexAngle)):
                break;
            indexMinus = (indexMinus - 1 + degree) % degree;

        if (indexMinus == ((indexPlus - 1 + degree) % degree)):
            return;
        
        #vertices;
        i = (indexPlus + 1) % degree;
        while(i != (indexMinus + 1) % degree):
            self.FillVertChildOfPseudoSource(indexOfParentVertex, i);
            i = (i + 1) % degree
        
        #windows
        i = indexPlus;
        while(i != (indexMinus + 1) % degree):
            self.CreateIntervalChildOfPseudoSource(indexOfParentVertex, i);
            i = (i + 1) % degree;
    
    def ComputeChildrenOfPseudoSourceFromWindow(self, indexOfParentVertex):
        degree = len(self.model.Neigh(indexOfParentVertex));
        neighs = self.model.Neigh(indexOfParentVertex);
        indexOfParentOfParent = self.m_InfoAtVertices[indexOfParentVertex].indexOfParent;
        leftVert = self.model.m_Edges[indexOfParentOfParent].indexOfLeftVert;
        rightVert = self.model.m_Edges[indexOfParentOfParent].indexOfRightVert;
        subIndexLeft = self.model.GetSubindexToVert(indexOfParentVertex, leftVert);
        subIndexRight = (subIndexLeft + 1) % degree;
        
        x1 = self.m_InfoAtVertices[indexOfParentVertex].entryProp * self.model.m_Edges[indexOfParentOfParent].edge_length;
        y1 = 0.0;
        x2 = self.model.m_Edges[indexOfParentOfParent].edge_length;
        y2 = 0.0;
        x1 -= self.model.m_Edges[indexOfParentOfParent].coordOfOppositeVert.first;
        y1 -= self.model.m_Edges[indexOfParentOfParent].coordOfOppositeVert.second;
        x2 -= self.model.m_Edges[indexOfParentOfParent].coordOfOppositeVert.first;
        y2 -= self.model.m_Edges[indexOfParentOfParent].coordOfOppositeVert.second;
        
        try:
            anglePlus = ((x1 * x2) + (y1 * y2)) / ((x1**2 + y1**2) * (x2**2 + y2**2))**0.5;
        except ZeroDivisionError:            
            anglePlus = 0.0;
            
        anglePlus = math.acos(max(-1.0, min(1.0, anglePlus)));
        angleSum = anglePlus;
        indexPlus = subIndexRight;
        
        while(indexPlus != subIndexLeft):
            angleSum += neighs[indexPlus].second;
            if (angleSum > (Constants.M_PI - Constants.ToleranceOfConvexAngle)):
                break;
            indexPlus = (indexPlus + 1) % degree;

        angleSum = neighs[subIndexLeft].second - anglePlus;
        indexMinus = (subIndexLeft - 1 + degree) % degree;
        
        while(indexMinus != (indexPlus - 1 + degree) % degree):
            angleSum += neighs[indexMinus].second;
            
            if (angleSum > (Constants.M_PI - Constants.ToleranceOfConvexAngle)):
                break;
            indexMinus = (indexMinus - 1 + degree) % degree;

        if (indexMinus == (indexPlus - 1 + degree) % degree):
            return;
        
        for i in range(degree):
            self.FillVertChildOfPseudoSource(indexOfParentVertex, i);
            
        #windows
        i = indexPlus;
        while(i != (indexMinus + 1) % degree):
            self.CreateIntervalChildOfPseudoSource(indexOfParentVertex, i);
            i = (i + 1) % degree;
     
    def ComputeChildrenOfWindow(self, quoteParentWindow):
        w = quoteParentWindow.pWindow;
        edge = self.model.m_Edges[w.indexOfCurEdge];
        entryProp = self.model.ProportionOnEdgeByImage(w.indexOfCurEdge, w.coordOfPseudoSource);
#         print("ENTRYPROP, PROPORTION 0, PROPOTION 1 ", entryProp, w.proportions[0], w.proportions[1]);
        if (entryProp >= w.proportions[1]):
            self.ComputeTheOnlyLeftChild(w);
            return;

        if (entryProp <= w.proportions[0]):
            self.ComputeTheOnlyRightChild(w);
            return;
        
        disToAngle = self.model.DistanceToIncidentAngle(w.indexOfCurEdge, w.coordOfPseudoSource);
        incidentVertex = edge.indexOfOppositeVert;
        fLeftChildToCompute = False;
        fRightChildToCompute = False;
        fWIsWinning = False;
        totalDis = w.disToRoot + disToAngle;
     
        if (self.m_InfoAtAngles[w.indexOfCurEdge].birthTime == -1):
            fLeftChildToCompute = True;
            fRightChildToCompute = True;
            fWIsWinning = True;
        else:
            if (totalDis < (self.m_InfoAtAngles[w.indexOfCurEdge].disUptodate - Constants.LENGTH_EPSILON_CONTROL)):
                fLeftChildToCompute = True;
                fRightChildToCompute = True;
                fWIsWinning = True;
            else:
                fLeftChildToCompute = (entryProp < self.m_InfoAtAngles[w.indexOfCurEdge].entryProp);
                fRightChildToCompute = not fLeftChildToCompute;
                fWIsWinning = False;

        if (not fWIsWinning):
            if (fLeftChildToCompute):
                self.ComputeTheOnlyLeftTrimmedChild(w);
            if (fRightChildToCompute):
                self.ComputeTheOnlyRightTrimmedChild(w);
            return;
     
        self.m_InfoAtAngles[w.indexOfCurEdge].disUptodate = totalDis;
        self.m_InfoAtAngles[w.indexOfCurEdge].entryProp = entryProp;
        self.m_InfoAtAngles[w.indexOfCurEdge].birthTime += 1;
     
        self.ComputeLeftTrimmedChildWithParent(w);
        self.ComputeRightTrimmedChildWithParent(w);    
        
        if (totalDis < (self.m_InfoAtVertices[incidentVertex].disUptodate - Constants.LENGTH_EPSILON_CONTROL)):
            self.m_InfoAtVertices[incidentVertex].fParentIsPseudoSource = False;
            self.m_InfoAtVertices[incidentVertex].birthTime += 1;
            self.m_InfoAtVertices[incidentVertex].indexOfParent = w.indexOfCurEdge;
            self.m_InfoAtVertices[incidentVertex].indexOfRootVertOfParent = w.indexOfRoot;
            self.m_InfoAtVertices[incidentVertex].level = w.level + 1;
            self.m_InfoAtVertices[incidentVertex].disUptodate = totalDis;
            self.m_InfoAtVertices[incidentVertex].entryProp = entryProp;
             
            if (not self.model.IsConvexVert(incidentVertex)):
                self.AddIntoQueueOfPseudoSources(QuoteInfoAtVertex(birthTime = self.m_InfoAtVertices[incidentVertex].birthTime, indexOfVert = incidentVertex, disUptodate = totalDis));
     
    def ComputeChildrenOfPseudoSource(self, indexOfParentVertex):
        if (self.m_InfoAtVertices[indexOfParentVertex].fParentIsPseudoSource):
            self.ComputeChildrenOfPseudoSourceFromPseudoSource(indexOfParentVertex);
        else:
            self.ComputeChildrenOfPseudoSourceFromWindow(indexOfParentVertex);
            
            
    def CreateIntervalChildOfPseudoSource(self, source, subIndexOfIncidentEdge):
        indexOfIncidentEdge = self.model.Neigh(source)[subIndexOfIncidentEdge].first;
        
        if (self.model.IsExtremeEdge(indexOfIncidentEdge)):
            return;
        
        edge = self.model.m_Edges[indexOfIncidentEdge];
        edgeIndex = edge.indexOfRightEdge;
        
        if (self.model.IsExtremeEdge(edgeIndex)):
            return;
        
        quoteW = QuoteWindow();
        quoteW.pWindow = Window();
        quoteW.pWindow.fParentIsPseudoSource = True;
        quoteW.pWindow.fDirectParenIsPseudoSource = True;
        quoteW.pWindow.birthTimeOfParent = self.m_InfoAtVertices[source].birthTime;
        quoteW.pWindow.indexOfParent = source;
        quoteW.pWindow.indexOfRoot = source;
        quoteW.pWindow.indexOfCurEdge = edgeIndex;
        quoteW.pWindow.level = self.m_InfoAtVertices[source].level + 1;
        quoteW.pWindow.disToRoot = self.m_InfoAtVertices[source].disUptodate;
        quoteW.pWindow.proportions[0] = 0.0;
        quoteW.pWindow.proportions[1] = 1.0;
        quoteW.pWindow.entryPropOfParent;
        reverseEdge = self.model.m_Edges[edgeIndex].indexOfReverseEdge;
        quoteW.pWindow.coordOfPseudoSource = self.model.GetNew2DCoordinatesByReversingCurrentEdge(reverseEdge,self.model.m_Edges[reverseEdge].coordOfOppositeVert);
        self.AddIntoQueueOfWindows(quoteW);
      
    def FillVertChildOfPseudoSource(self,  source, subIndexOfVert):
        edge = self.model.m_Edges[self.model.Neigh(source)[subIndexOfVert].first];
        index = edge.indexOfRightVert;        
        dis = (self.m_InfoAtVertices[source].disUptodate + edge.edge_length);
        
        if (dis >= (self.m_InfoAtVertices[index].disUptodate - Constants.LENGTH_EPSILON_CONTROL)):
            return;
        
        self.m_InfoAtVertices[index].fParentIsPseudoSource = True;
        self.m_InfoAtVertices[index].birthTime += 1;
        self.m_InfoAtVertices[index].indexOfParent = source;
        self.m_InfoAtVertices[index].level = self.m_InfoAtVertices[source].level + 1;
        self.m_InfoAtVertices[index].disUptodate = dis;
        
        if (not self.model.IsConvexVert(index)):
            self.AddIntoQueueOfPseudoSources(QuoteInfoAtVertex(birthTime=self.m_InfoAtVertices[index].birthTime, indexOfVert=index, disUptodate=dis));
      
      
    def ComputeTheOnlyLeftChild(self, w):
        if (self.model.IsExtremeEdge(self.model.m_Edges[w.indexOfCurEdge].indexOfLeftEdge)):
            return;
        
#         print('COMPUTE THE ONLY LEFT CHILD');
        quoteW = QuoteWindow();
        quoteW.pWindow = Window();
        quoteW.pWindow.proportions[0] = self.model.ProportionOnLeftEdgeByImage(w.indexOfCurEdge, w.coordOfPseudoSource, w.proportions[0]);
        quoteW.pWindow.proportions[0] = max(0.0, quoteW.pWindow.proportions[0]);
        quoteW.pWindow.proportions[1] = self.model.ProportionOnLeftEdgeByImage(w.indexOfCurEdge, w.coordOfPseudoSource, w.proportions[1]);
        quoteW.pWindow.proportions[1] = min(1.0, quoteW.pWindow.proportions[1]);
        if (self.IsTooNarrowWindow(quoteW.pWindow)):
            quoteW.pWindow = None;
            return;
        
        
        quoteW.pWindow.fParentIsPseudoSource = w.fParentIsPseudoSource;
        quoteW.pWindow.fDirectParenIsPseudoSource = False;
        quoteW.pWindow.fDirectParentEdgeOnLeft = True;
        quoteW.pWindow.indexOfCurEdge = self.model.m_Edges[w.indexOfCurEdge].indexOfLeftEdge;
        quoteW.pWindow.disToRoot = w.disToRoot;
      
        quoteW.pWindow.coordOfPseudoSource = self.model.GetNew2DCoordinatesByRotatingAroundLeftChildEdge(w.indexOfCurEdge, w.coordOfPseudoSource);
        if (not self.CheckValidityOfWindow(quoteW.pWindow)):
            quoteW.pWindow = None;
            return;
        
        quoteW.pWindow.fIsOnLeftSubtree = w.fIsOnLeftSubtree;
        quoteW.pWindow.level = w.level + 1;    
        quoteW.pWindow.entryPropOfParent = w.entryPropOfParent;
        quoteW.pWindow.birthTimeOfParent = w.birthTimeOfParent;
        quoteW.pWindow.indexOfParent = w.indexOfParent;
        quoteW.pWindow.indexOfRoot = w.indexOfRoot;
        self.AddIntoQueueOfWindows(quoteW);

      
    def ComputeTheOnlyRightChild(self, w):
        if (self.model.IsExtremeEdge(self.model.m_Edges[w.indexOfCurEdge].indexOfRightEdge)):
            return;
        
#         print('COMPUTE THE ONLY RIGHT CHILD');
        
        quoteW = QuoteWindow();
        quoteW.pWindow = Window();
        quoteW.pWindow.proportions[0] = self.model.ProportionOnRightEdgeByImage(w.indexOfCurEdge, w.coordOfPseudoSource, w.proportions[0]);
        quoteW.pWindow.proportions[0] = max(0.0, quoteW.pWindow.proportions[0]);
        quoteW.pWindow.proportions[1] = self.model.ProportionOnRightEdgeByImage(w.indexOfCurEdge, w.coordOfPseudoSource, w.proportions[1]);
        quoteW.pWindow.proportions[1] = min(1.0, quoteW.pWindow.proportions[1]);
        
        if (self.IsTooNarrowWindow(quoteW.pWindow)):
            quoteW.pWindow = None;
            return;
        
        quoteW.pWindow.fParentIsPseudoSource = w.fParentIsPseudoSource;
        quoteW.pWindow.fDirectParenIsPseudoSource = False;
        quoteW.pWindow.fDirectParentEdgeOnLeft = False;
        quoteW.pWindow.indexOfCurEdge = self.model.m_Edges[w.indexOfCurEdge].indexOfRightEdge;
        quoteW.pWindow.disToRoot = w.disToRoot;
        quoteW.pWindow.coordOfPseudoSource = self.model.GetNew2DCoordinatesByRotatingAroundRightChildEdge(w.indexOfCurEdge, w.coordOfPseudoSource);
        
        if (not self.CheckValidityOfWindow(quoteW.pWindow)):
            quoteW.pWindow = None;
            return;
        
        quoteW.pWindow.level = w.level + 1;    
        quoteW.pWindow.birthTimeOfParent = w.birthTimeOfParent;
        quoteW.pWindow.indexOfParent = w.indexOfParent;
        quoteW.pWindow.indexOfRoot = w.indexOfRoot;
        quoteW.pWindow.fIsOnLeftSubtree = w.fIsOnLeftSubtree;
        quoteW.pWindow.entryPropOfParent = w.entryPropOfParent;
        self.AddIntoQueueOfWindows(quoteW);

      
    def ComputeTheOnlyLeftTrimmedChild(self, w):
        if (self.model.IsExtremeEdge(self.model.m_Edges[w.indexOfCurEdge].indexOfLeftEdge)):
            return;
#         print('COMPUTE THE ONLY LEFT TRIMMED CHILD');
        quoteW = QuoteWindow();
        quoteW.pWindow = Window();
        quoteW.pWindow.proportions[0] = self.model.ProportionOnLeftEdgeByImage(w.indexOfCurEdge, w.coordOfPseudoSource, w.proportions[0]);
        quoteW.pWindow.proportions[0] = max(0.0, quoteW.pWindow.proportions[0]);
        quoteW.pWindow.proportions[1] = 1;
        if (self.IsTooNarrowWindow(quoteW.pWindow)):
            quoteW.pWindow = None;
            return;

        quoteW.pWindow.fParentIsPseudoSource = w.fParentIsPseudoSource;
        quoteW.pWindow.fDirectParenIsPseudoSource = False;
        quoteW.pWindow.fDirectParentEdgeOnLeft = True;
        quoteW.pWindow.indexOfCurEdge = self.model.m_Edges[w.indexOfCurEdge].indexOfLeftEdge;
        quoteW.pWindow.disToRoot = w.disToRoot;
        quoteW.pWindow.coordOfPseudoSource = self.model.GetNew2DCoordinatesByRotatingAroundLeftChildEdge(w.indexOfCurEdge, w.coordOfPseudoSource);
        if ( not self.CheckValidityOfWindow(quoteW.pWindow)):
            quoteW.pWindow = None;
            return;
        
        quoteW.pWindow.level = w.level + 1;    
        quoteW.pWindow.birthTimeOfParent = w.birthTimeOfParent;
        quoteW.pWindow.indexOfParent = w.indexOfParent;
        quoteW.pWindow.indexOfRoot = w.indexOfRoot;
        quoteW.pWindow.fIsOnLeftSubtree = w.fIsOnLeftSubtree;
        quoteW.pWindow.entryPropOfParent = w.entryPropOfParent;
        self.AddIntoQueueOfWindows(quoteW);
      
    def ComputeTheOnlyRightTrimmedChild(self, w):
        if (self.model.IsExtremeEdge(self.model.m_Edges[w.indexOfCurEdge].indexOfRightEdge)):
            return;
#         print('COMPUTE THE ONLY RIGHT TRIMMED CHILD');
        quoteW = QuoteWindow();
        quoteW.pWindow = Window();
        quoteW.pWindow.proportions[0] = 0.0;
        quoteW.pWindow.proportions[1] = self.model.ProportionOnRightEdgeByImage(w.indexOfCurEdge, w.coordOfPseudoSource, w.proportions[1]);
        quoteW.pWindow.proportions[1] = min(1.0, quoteW.pWindow.proportions[1]);
        if (self.IsTooNarrowWindow(quoteW.pWindow)):
            quoteW.pWindow = None;
            return;

        quoteW.pWindow.fParentIsPseudoSource = w.fParentIsPseudoSource;
        quoteW.pWindow.fDirectParenIsPseudoSource = False;
        quoteW.pWindow.fDirectParentEdgeOnLeft = False;
        quoteW.pWindow.indexOfCurEdge = self.model.m_Edges[w.indexOfCurEdge].indexOfRightEdge;
        quoteW.pWindow.disToRoot = w.disToRoot;
        quoteW.pWindow.coordOfPseudoSource = self.model.GetNew2DCoordinatesByRotatingAroundRightChildEdge(w.indexOfCurEdge, w.coordOfPseudoSource);
        if (not self.CheckValidityOfWindow(quoteW.pWindow)):
            quoteW.pWindow = None;
            return;

        quoteW.pWindow.level = w.level + 1;    
        quoteW.pWindow.birthTimeOfParent = w.birthTimeOfParent;
        quoteW.pWindow.indexOfParent = w.indexOfParent;
        quoteW.pWindow.indexOfRoot = w.indexOfRoot;
        quoteW.pWindow.fIsOnLeftSubtree = w.fIsOnLeftSubtree;
        quoteW.pWindow.entryPropOfParent = w.entryPropOfParent;
        self.AddIntoQueueOfWindows(quoteW);
      
    def ComputeLeftTrimmedChildWithParent(self, w):
        if (self.model.IsExtremeEdge(self.model.m_Edges[w.indexOfCurEdge].indexOfLeftEdge)):
            return;
        
#         print('COMPUTE THE ONLY LEFT TRIMMED CHILD WITH PARENT');
        quoteW = QuoteWindow();
        quoteW.pWindow = Window();
        quoteW.pWindow.proportions[0] = self.model.ProportionOnLeftEdgeByImage(w.indexOfCurEdge, w.coordOfPseudoSource, w.proportions[0]);
        quoteW.pWindow.proportions[0] = max(0.0, quoteW.pWindow.proportions[0]);
        quoteW.pWindow.proportions[1] = 1;
        if (self.IsTooNarrowWindow(quoteW.pWindow)):
            quoteW.pWindow = None;
            return;
        
        quoteW.pWindow.fParentIsPseudoSource = False;
        quoteW.pWindow.fDirectParenIsPseudoSource = False;
        quoteW.pWindow.fDirectParentEdgeOnLeft = True;
        quoteW.pWindow.indexOfCurEdge = self.model.m_Edges[w.indexOfCurEdge].indexOfLeftEdge;
        quoteW.pWindow.disToRoot = w.disToRoot;
        quoteW.pWindow.coordOfPseudoSource = self.model.GetNew2DCoordinatesByRotatingAroundLeftChildEdge(w.indexOfCurEdge, w.coordOfPseudoSource);
        if (not self.CheckValidityOfWindow(quoteW.pWindow)):
            quoteW.pWindow = None;
            return;
        
        quoteW.pWindow.level = w.level + 1;    
        quoteW.pWindow.birthTimeOfParent = self.m_InfoAtAngles[w.indexOfCurEdge].birthTime;
        quoteW.pWindow.indexOfParent = w.indexOfCurEdge;
        quoteW.pWindow.indexOfRoot = w.indexOfRoot;
        quoteW.pWindow.fIsOnLeftSubtree = True;
        quoteW.pWindow.entryPropOfParent = self.m_InfoAtAngles[w.indexOfCurEdge].entryProp;
        self.AddIntoQueueOfWindows(quoteW);
     
    def ComputeRightTrimmedChildWithParent(self, w):
        if (self.model.IsExtremeEdge(self.model.m_Edges[w.indexOfCurEdge].indexOfRightEdge)):
            return;
#         print('COMPUTE THE ONLY RIGHT TRIMMED CHILD WITH PARENT');
        quoteW = QuoteWindow();
        quoteW.pWindow = Window();
        quoteW.pWindow.proportions[0] = 0.0;
        quoteW.pWindow.proportions[1] = self.model.ProportionOnRightEdgeByImage(w.indexOfCurEdge, w.coordOfPseudoSource, w.proportions[1]);
        quoteW.pWindow.proportions[1] = min(1.0, quoteW.pWindow.proportions[1]);
        
        if (self.IsTooNarrowWindow(quoteW.pWindow)):
            quoteW.pWindow = None;
            return;

        quoteW.pWindow.fParentIsPseudoSource = False;
        quoteW.pWindow.fDirectParenIsPseudoSource = False;
        quoteW.pWindow.fDirectParentEdgeOnLeft = False;
        quoteW.pWindow.indexOfCurEdge = self.model.m_Edges[w.indexOfCurEdge].indexOfRightEdge;
        quoteW.pWindow.disToRoot = w.disToRoot;
        quoteW.pWindow.coordOfPseudoSource = self.model.GetNew2DCoordinatesByRotatingAroundRightChildEdge(w.indexOfCurEdge, w.coordOfPseudoSource);
        if (not self.CheckValidityOfWindow(quoteW.pWindow)):
            quoteW.pWindow = None;
            return;
        
        quoteW.pWindow.fIsOnLeftSubtree = False;
        quoteW.pWindow.birthTimeOfParent = self.m_InfoAtAngles[w.indexOfCurEdge].birthTime;
        quoteW.pWindow.indexOfParent = w.indexOfCurEdge;
        quoteW.pWindow.indexOfRoot = w.indexOfRoot;
        quoteW.pWindow.level = w.level + 1;    
        quoteW.pWindow.entryPropOfParent = self.m_InfoAtAngles[w.indexOfCurEdge].entryProp;
        self.AddIntoQueueOfWindows(quoteW);
     
