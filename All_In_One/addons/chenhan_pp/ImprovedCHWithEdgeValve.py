'''
Created on Jun 30, 2016

@author: ashok
'''
from chenhan_pp.PreviousCH import PreviousCH

class ImprovedCHWithEdgeValve(PreviousCH):
    
    def __init__(self, *, inputModel=None, indexOfSourceVerts=None):
        super().__init__(inputModel=inputModel, indexOfSourceVerts=indexOfSourceVerts);
        self.nameOfAlgorithm = "ImprovedCHWithEdgeValve";
    
    
    def CheckValidityOfWindow(self, w):
        if (w.fDirectParenIsPseudoSource):
            return True;
        
        edge = self.model.Edge(w.indexOfCurEdge);
        
        leftVert = edge.indexOfLeftVert;
        detaX = w.coordOfPseudoSource.first - w.proportions[1] * edge.edge_length;
        rightLen = (detaX**2 + w.coordOfPseudoSource.second**2)**0.5;
        
        if ((self.m_InfoAtVertices[leftVert].disUptodate < (10000.0  / self.model.m_scale)) and (self.m_InfoAtVertices[leftVert].disUptodate + w.proportions[1] * edge.edge_length < w.disToRoot + rightLen)):
            return False;

        rightVert = edge.indexOfRightVert;
        detaX = w.coordOfPseudoSource.first - w.proportions[0] * edge.edge_length;
        leftLen = (detaX**2 + w.coordOfPseudoSource.second**2)**0.5;
        
        if (self.m_InfoAtVertices[rightVert].disUptodate < (10000  / self.model.m_scale) and (self.m_InfoAtVertices[rightVert].disUptodate + (1 - w.proportions[0]) * edge.edge_length < w.disToRoot + leftLen)):
            return False;
        
        oppositeEdge = self.model.Edge(edge.indexOfReverseEdge);
        xOfVert = edge.edge_length - oppositeEdge.coordOfOppositeVert.first;
        yOfVert = -oppositeEdge.coordOfOppositeVert.second;
        
        if (self.m_InfoAtVertices[oppositeEdge.indexOfOppositeVert].disUptodate < (10000  / self.model.m_scale)):
            if (w.fDirectParentEdgeOnLeft):
                deta = w.disToRoot + leftLen - self.m_InfoAtVertices[oppositeEdge.indexOfOppositeVert].disUptodate;
                if (deta <= 0):
                    return True;
                detaX = xOfVert - w.proportions[0] * edge.edge_length;
                if (detaX * detaX + yOfVert * yOfVert < deta * deta):
                    return False;
            else:
                deta = w.disToRoot + rightLen - self.m_InfoAtVertices[oppositeEdge.indexOfOppositeVert].disUptodate;
                if (deta <= 0):
                    return True;
                detaX = xOfVert - w.proportions[1] * edge.edge_length;
                if (detaX**2 + yOfVert**2 < deta**2):
                    return False;
        return True;
 
    
    