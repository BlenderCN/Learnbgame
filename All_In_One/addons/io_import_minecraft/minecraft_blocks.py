import bpy

#minecraft_blocks.py - define data structures to
#define and represent all the minecraft block types.


#this import would work as a namespace...

mcblocks = {}

#if name is __... not main.... initialise()


class MCBlock:
    
    def __init__(self, bid, bname, ):
        self.blockID = -1   #instance var (many are just colour/texture variant basic blocks)
        self.name = None    #the full name of the substance (blocktype)
        self.texFaceIDs = [0,0,0,0,0,0] # TRBLFB (top right back left front bottom) (TroubleFub)
        #extra bits are defined in extended blocktypes
        
    def buildMesh(self):
        """Creates a master mesh (for dupliverting) to represent this Type"""
        
        #create cube. scale down, etc...
        



class MCMeshMaker:
    
    #Define some kind of interface for similar behaviour,then have a list of functions,
    #and just call them by array index??
    
    
    def mcMakeMushroom():
        pass
    
    def mcMakeFlower():
        pass
    
    def mcMakeTorch():
        pass