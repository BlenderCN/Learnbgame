'''
Created on Jun 30, 2016

@author: ashok
'''
import chenhan_pp.Constants as Constants;
from chenhan_pp.stl_classes import Pair;

class InfoAtVertex():
    fParentIsPseudoSource = False;
    birthTime = -1;
    indexOfParent = -1;
    indexOfRootVertOfParent = -1;
    level = 0;
    disUptodate = Constants.FLT_MAX;
    entryProp = Constants.CPP_DOUBLE;
    
    def __init__(self):
#         self.fParentIsPseudoSource = False;
        self.birthTime = -1;
#         self.indexOfParent = -1;
#         self.indexOfRootVertOfParent = -1;
#         self.level = -1;
        self.disUptodate = Constants.FLT_MAX;
#         self.entryProp = Constants.FLT_MAX;
        
class QuoteInfoAtVertex():
    birthTime = -1;
    indexOfVert = -1;
    disUptodate = Constants.CPP_DOUBLE;
    
    def __lt__(self, other):
        assert(type(self) == type(other));        
#         return (self.disUptodate > other.disUptodate);#Original idea for cpp priority_queue
        return (self.disUptodate < other.disUptodate);
    
    def __init__(self, *, birthTime = -1, indexOfVert = -1, disUptodate = -1.0):
        if(birthTime != -1):
            self.birthTime = birthTime;
        if(indexOfVert != -1):
            self.indexOfVert = indexOfVert;
        if(disUptodate != -1.0):
            self.disUptodate = disUptodate;

class InfoAtAngle():
    birthTime = -1;
    disUptodate = Constants.FLT_MAX;
    entryprop = Constants.CPP_DOUBLE;
    
    def __init__(self):
        self.birthTime  = -1;
        self.disUptodate = Constants.FLT_MAX;

class Window():
    fIsOnLeftSubtree = False;
    fParentIsPseudoSource = False;
    fDirectParentEdgeOnLeft = False;
    fDirectParenIsPseudoSource = False;
    birthTimeOfParent = -1;
    indexOfParent = -1;
    indexOfRoot = -1;
    indexOfCurEdge = -1;
    level = -1;
    disToRoot = Constants.FLT_MAX;
    proportions = [-1.0, -1.0];
    entryPropOfParent = Constants.CPP_DOUBLE;    
    coordOfPseudoSource = Pair(-1.0, -1.0);
    
    def __init__(self):        
        self.fIsOneLeftSubTree = False;
        self.fParentIsPseudoSource = False;
        self.fDirectParentEdgeOnLeft = False;
        self.fDirectParenIsPseudoSource = False;
        self.birthTimeOfParent = 0;
        self.indexOfParent = -1;
        self.indexOfRoot = -1;
        self.indexOfCurEdge = -1;
        self.level = 0;
        self.disToRoot = Constants.CPP_DOUBLE;
        self.proportions = [Constants.CPP_DOUBLE, Constants.CPP_DOUBLE];
        self.entryPropOfParent = Constants.CPP_DOUBLE;        
        self.coordOfPseudoSource = Pair(Constants.CPP_DOUBLE, Constants.CPP_DOUBLE);
    
class QuoteWindow():
    
    pWindow = None;
    disUptodate = Constants.CPP_DOUBLE;
    
    def __init__(self):
        self.pWindow = None;
        self.disUptodate = Constants.FLT_MAX;
    
    def __lt__(self, other):
#         return (self.disUptodate > other.disUptodate);
        return (self.disUptodate < other.disUptodate);
    

    