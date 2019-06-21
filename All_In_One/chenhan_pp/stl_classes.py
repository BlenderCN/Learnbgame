'''
Created on Jun 30, 2016

@author: ashok
'''
class Pair():
    first = None;
    second = None;
    
    def __init__(self, left, right):            
        self.first = left;
        self.second = right;
    
    def __eq__(self, other):
        if(type(self) !=  type(other)):
            return False;
        return (self.first == other.first and self.second == other.second);
    
    def __hash__(self):
        return hash((self.first, self.second));
    
    
    def __str__(self):
        if(self.first and self.second):
            return str(self.first)+", "+str(self.second);
        else:
            return 'None, None';
                
    def __repr__(self):
        if(self.first and self.second):
            return str(self.first)+", "+str(self.second);
        elif(self.first and not self.second):
            return str(self.first) + ', None';
        elif(not self.first and self.second):
            return 'None, '+str(self.second);
        else:
            return 'None';


def make_pair(id1, id2):
    return Pair(id1, id2);