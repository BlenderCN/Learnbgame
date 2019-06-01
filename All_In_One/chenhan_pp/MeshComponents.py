'''
Created on Jun 30, 2016

@author: ashok
'''
from chenhan_pp.stl_classes import Pair, make_pair;


class CFace():
    verts = [];
    
    def __init__(self, x =None,y = None, z = None):
        self.verts = [0,0,0];
        if(x):
            self.verts[0] = x;
        
        if(y):
            self.verts[1] = y;
        
        if(z):
            self.verts[2] = z;
        
    def __getitem__(self, index):
        return self.verts[index];
    
    def __setitem__(self, index, value ):
        self.verts[index] = value;
        

class CEdge():
    indexOfLeftVert = -1;
    indexOfRightVert = -1;
    indexOfOppositeVert = -1;
    indexOfLeftEdge = -1;
    indexOfRightEdge = -1;
    indexOfReverseEdge = -1;
    indexOfFrontFace = -1;
    edge_length = 0;
    coordOfOppositeVert = None;
    matrixRotatedToLeftEdge = None;
    matrixRotatedToRightEdge = None;
    
    def __init__(self):
        self.indexOfLeftVert = -1;
        self.indexOfRightVert = -1;
        self.indexOfOppositeVert = -1;
        self.indexOfLeftEdge = -1;
        self.indexOfRightEdge = -1;
        self.indexOfReverseEdge = -1;
        self.indexOfFrontFace = -1;
        self.edge_length = 0;
        self.coordOfOppositeVert = make_pair(0.0, 0.0);
        self.matrixRotatedToLeftEdge = make_pair(0.0, 0.0);
        self.matrixRotatedToRightEdge = make_pair(0.0, 0.0);
        
class EdgePoint():
    index = -1;
    proportion = 0.0; #/[0 --> left endpoint; 1 --> right endpoint]
    isVertex = False;
    
    def __init__(self, *, model=None,index=-1,proportion=-1, isVertex=False, leftVert=-1, rightVert=-1):
        #Overloading condition 1, index is the only argument supplied
        if(index != -1 and not model and not isVertex):
            self.index = index;
            if(proportion == -1):
                self.isVertex = True;
            else:
                self.isVertex = False;
                self.proportion = proportion;
        
        elif(index == -1 and model):
            self.index = model.GetEdgeIndexFromTwoVertices(leftVert, rightVert);
            self.proportion = proportion;
            self.isVertex = False;
            
        
    
    def Get3DPoint(self, model):
        if (self.isVertex):
            return model.Vert(self.index);
        return (1 - self.proportion) * model.Vert(model.Edge(self.index).indexOfLeftVert) + self.proportion * model.Vert(model.Edge(self.index).indexOfRightVert);

    def __lt__(self, other):
        assert(type(self) == type(other));   
        if (self.isVertex == False and other.isVertex == True):
            return True;
        if (self.isVertex == True and other.isVertex == False):
            return False;
        if (self.index < other.index):
            return True;
        if (self.index > other.index):
            return False;
        if (self.proportion < other.proportion):
            return True;
        if (self.proportion > other.proportion):
            return False;
        return False;
    
