'''
Created on Jun 30, 2016

@author: ashok
'''
# import gc;
from chenhan_pp.ImprovedCHWithEdgeValve import ImprovedCHWithEdgeValve
from queue import PriorityQueue
from chenhan_pp.GeodesicComponents import InfoAtAngle
import chenhan_pp.Constants as Constants;

class CICHWithFurtherPriorityQueue(ImprovedCHWithEdgeValve):
    
    def __init__(self, *, inputModel=None, indexOfSourceVerts=None):
        super().__init__(inputModel=inputModel, indexOfSourceVerts=indexOfSourceVerts);
        self.nameOfAlgorithm = "ImprovedCHWithPriorityQueue";
        
    def InitContainers(self):
        self.m_QueueForPseudoSources = PriorityQueue();
        self.m_QueueForWindows = PriorityQueue();
        self.m_InfoAtAngles = [InfoAtAngle() for i in range(self.model.GetNumOfEdges())];
    
    def ClearContainers(self):
        self.m_QueueForWindows = PriorityQueue();
        self.m_QueueForPseudoSources = PriorityQueue();
        
    def BuildSequenceTree(self):
        self.ComputeChildrenOfSource();
        fFromQueueOfPseudoSources = self.UpdateTreeDepthBackWithChoice();
        runcounter = 0;
        while (not self.m_QueueForPseudoSources.empty() or not self.m_QueueForWindows.empty()):            
            if (self.m_QueueForWindows.qsize() > self.nMaxLenOfWindowQueue):
                self.nMaxLenOfWindowQueue = self.m_QueueForWindows.qsize();
                
            if (self.m_QueueForPseudoSources.qsize() > self.nMaxLenOfPseudoSources):
                self.nMaxLenOfPseudoSources = self.m_QueueForPseudoSources.qsize();
                
            if (fFromQueueOfPseudoSources):#If PseudoSource
                item = self.m_QueueForPseudoSources.get()
                indexOfVert = item.indexOfVert;     
                self.ComputeChildrenOfPseudoSource(indexOfVert);
            else:
                quoteW = self.m_QueueForWindows.get();
                self.ComputeChildrenOfWindow(quoteW);        
                quoteW.pWindow = None;
                quoteW = None;

            fFromQueueOfPseudoSources = self.UpdateTreeDepthBackWithChoice();
            runcounter += 1;
        print('SEQUENCE TREE BUILT!, RAN FOR ITERATIONS ::: ', runcounter);

    def GetMinDisOfWindow(self, w):
        projProp = w.coordOfPseudoSource.first / self.model.m_Edges[w.indexOfCurEdge].edge_length;
        if (projProp <= w.proportions[0]):
            detaX = w.coordOfPseudoSource.first - w.proportions[0] * self.model.m_Edges[w.indexOfCurEdge].edge_length;
            return w.disToRoot + (detaX**2 + w.coordOfPseudoSource.second**2)**0.5;

        if (projProp >= w.proportions[1]):
            detaX = w.coordOfPseudoSource.first - w.proportions[1] * self.model.m_Edges[w.indexOfCurEdge].edge_length;
            return w.disToRoot + (detaX**2 + w.coordOfPseudoSource.second**2)**0.5;
        
        return w.disToRoot - w.coordOfPseudoSource.second;
    
    def AddIntoQueueOfWindows(self, quoteW):        
        quoteW.disUptodate = self.GetMinDisOfWindow(quoteW.pWindow);
        self.m_QueueForWindows.put(quoteW);
        self.nCountOfWindows += 1;
    
    def UpdateTreeDepthBackWithChoice(self):
        while (not self.m_QueueForPseudoSources.empty() and self.m_QueueForPseudoSources.queue[0].birthTime != self.m_InfoAtVertices[self.m_QueueForPseudoSources.queue[0].indexOfVert].birthTime):
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
                headElemOfPseudoSources = self.m_QueueForPseudoSources.queue[0];
                headElemOfWindows = self.m_QueueForWindows.queue[0];
                if (headElemOfPseudoSources.disUptodate <= headElemOfWindows.disUptodate):
                    self.depthOfResultingTree = max(self.depthOfResultingTree, self.m_InfoAtVertices[headElemOfPseudoSources.indexOfVert].level);
                    fFromQueueOfPseudoSources = True;
                else:
                    self.depthOfResultingTree = max(self.depthOfResultingTree, headElemOfWindows.pWindow.level);
                    fFromQueueOfPseudoSources = False;
        return fFromQueueOfPseudoSources;
    
    
    
    