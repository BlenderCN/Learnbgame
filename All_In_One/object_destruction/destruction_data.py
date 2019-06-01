#cell contains: pieces of parent in range of cell size
# a cell size, a cell location(x,y,z), neighbors for quick access, retrieved from grid

#grid provides access to cells via x,y,z indexing, has a size and cell count to calculate cell sizes
#

#each object has a destruction dataset in context, to get it to game engine store it externally or maybe all custom properties will be converted ? could even work like that
#but for standalone mode no bpy may be used !
#and here no bge may be used, need to be clean data objects
startclock = 0
import json
import mathutils
from mathutils import geometry, Vector

class Cell:

   
    import math
        
    def __init__(self, gridPos, grid):
        self.gridPos = gridPos
        self.grid = grid
        cellDim = grid.cellDim
        self.dim = cellDim
        self.visit = False
      #  print("CELL DIM: ",self.dim, cellDim)
        self.center = ((gridPos[0] + 0.5) * cellDim[0] + grid.pos[0], 
                       (gridPos[1] + 0.5) * cellDim[1] + grid.pos[1], 
                       (gridPos[2] + 0.5) * cellDim[2] + grid.pos[2]) 
                       
        self.range = [(self.center[0] - cellDim[0] / 2, self.center[0] + cellDim[0] / 2),
                      (self.center[1] - cellDim[1] / 2, self.center[1] + cellDim[1] / 2),
                      (self.center[2] - cellDim[2] / 2, self.center[2] + cellDim[2] / 2)] 
                                         
        self.children = [c.name for c in grid.children if self.isInside(c.worldPosition, 0)]
        [self.assign(grid.cellCoord, c, self.gridPos) for c in self.children]
        self.count = len(self.children)
    #    print("Cell created: ", self.center, self.count)
    #    print("W/L Orientation: " self.worldOrientation)
        self.isGroundCell = False
    
    def assign(self, dict, name, coord):
        dict[name] = coord
    
    def integrity(self, intgr):
        if self.count == 0:
            return False
        return len(self.children) / self.count > intgr     
            
    def isInside(self, pos, percentage):
      #  print("Cell center / pos / percentage: ", self.center, pos, percentage) 
        
        if pos[0] >= self.range[0][0] and pos[0] <= self.range[0][1] and \
           pos[1] >= self.range[1][0] and pos[1] <= self.range[1][1] and \
           pos[2] >= self.range[2][0] and pos[2] <= self.range[2][1] and \
           percentage >= 0 and percentage <= 1:
               return True
           
        return False
    
    def findNeighbors(self):
        
        
        #  2---3
        #0-+-1 |
        #| 6-+-7
        #4---5
        back = None
        if self.gridPos[1] < self.grid.cellCounts[1] - 1:
            back = self.grid.cells[(self.gridPos[0], self.gridPos[1] + 1, self.gridPos[2])]
         
        front = None
        if self.gridPos[1] > 0:
            front = self.grid.cells[(self.gridPos[0], self.gridPos[1] - 1, self.gridPos[2])]
            
        left = None
        if self.gridPos[0] < self.grid.cellCounts[0] - 1:
            left = self.grid.cells[(self.gridPos[0] + 1, self.gridPos[1], self.gridPos[2])]
         
        right = None
        if self.gridPos[0] > 0:
            bottom = self.grid.cells[(self.gridPos[0] - 1, self.gridPos[1], self.gridPos[2])]
            
        top  = None
        if self.gridPos[2] < self.grid.cellCounts[2] - 1:
            top = self.grid.cells[(self.gridPos[0], self.gridPos[1], self.gridPos[2] + 1)]
         
        bottom = None
        if self.gridPos[2] > 0:
            bottom = self.grid.cells[(self.gridPos[0], self.gridPos[1], self.gridPos[2] - 1)]
       
        #corners 
        c0 = None
        if self.gridPos[0] > 0 and self.gridPos[1] > 0 and self.gridPos[2] < self.grid.cellCounts[2] - 1:
            c0 = self.grid.cells[(self.gridPos[0] - 1, self.gridPos[1] - 1, self.gridPos[2] + 1)]
        
        c1 = None
        if self.gridPos[0] < self.grid.cellCounts[0] - 1 and self.gridPos[1] > 0 and \
           self.gridPos[2] < self.grid.cellCounts[2] - 1:
            c1 = self.grid.cells[(self.gridPos[0] + 1, self.gridPos[1] - 1, self.gridPos[2] + 1)]
            
        c2 = None
        if self.gridPos[0] > 0 and self.gridPos[1] < self.grid.cellCounts[1] - 1 and \
           self.gridPos[2] < self.grid.cellCounts[2] - 1:
            c2 = self.grid.cells[(self.gridPos[0] - 1, self.gridPos[1] + 1, self.gridPos[2] + 1)]
            
        c3 = None
        if self.gridPos[0] < self.grid.cellCounts[0] - 1  and self.gridPos[1] < self.grid.cellCounts[1] - 1 and \
           self.gridPos[2] < self.grid.cellCounts[2] - 1:
            c3 = self.grid.cells[(self.gridPos[0] + 1, self.gridPos[1] + 1, self.gridPos[2] + 1)]
         
        c4 = None
        if self.gridPos[0] > 0 and self.gridPos[1] > 0 and self.gridPos[2] > 0:
            c4 = self.grid.cells[(self.gridPos[0] - 1, self.gridPos[1] - 1, self.gridPos[2] - 1)]
         
        c5 = None
        if self.gridPos[0] < self.grid.cellCounts[0] - 1 and self.gridPos[1] > 0 and self.gridPos[2] > 0:
            c5 = self.grid.cells[(self.gridPos[0] + 1 , self.gridPos[1] - 1, self.gridPos[2] - 1)]
            
        c6 = None
        if self.gridPos[0] > 0 and self.gridPos[1] < self.grid.cellCounts[1] - 1 and \
           self.gridPos[2] > 0:
            c6 = self.grid.cells[(self.gridPos[0] - 1, self.gridPos[1] + 1, self.gridPos[2] - 1)]
         
        c7 = None
        if self.gridPos[0] < self.grid.cellCounts[0] - 1 and self.gridPos[1] < self.grid.cellCounts[1] - 1 and \
           self.gridPos[2] > 0:
            c7 = self.grid.cells[(self.gridPos[0] + 1 , self.gridPos[1] + 1, self.gridPos[2] - 1)]
       
       
        #between corners 
        #b01
        #b02
        #b13
        #b23
        
        b01 = None
        if self.gridPos[1] > 0 and self.gridPos[2] < self.grid.cellCounts[2] - 1:
            b01 = self.grid.cells[(self.gridPos[0], self.gridPos[1] - 1, self.gridPos[2] + 1)]
            
        b02 = None
        if self.gridPos[0] > 0 and self.gridPos[2] < self.grid.cellCounts[2] - 1:
            b02 = self.grid.cells[(self.gridPos[0] - 1 , self.gridPos[1], self.gridPos[2] + 1)]
         
        b13 = None
        if self.gridPos[0] < self.grid.cellCounts[0] - 1 and self.gridPos[2] < self.grid.cellCounts[2] - 1:
            b13 = self.grid.cells[(self.gridPos[0] + 1 , self.gridPos[1], self.gridPos[2] + 1)]
          
        b23 = None
        if self.gridPos[1] < self.grid.cellCounts[1] - 1 and self.gridPos[2] < self.grid.cellCounts[2] - 1:
           b23 = self.grid.cells[(self.gridPos[0] , self.gridPos[1] + 1, self.gridPos[2] + 1)]
        
      #  b45
      #  b46
      #  b57
      #  b67
        
        b45 = None
        if self.gridPos[1] > 0 and self.gridPos[2] > 0:
            b45 = self.grid.cells[(self.gridPos[0] , self.gridPos[1] - 1, self.gridPos[2] - 1)]
            
        b46 = None
        if self.gridPos[0] > 0 and self.gridPos[2] > 0:
            b46 = self.grid.cells[(self.gridPos[0] - 1 , self.gridPos[1], self.gridPos[2] - 1)]
            
        b57 = None
        if self.gridPos[0] < self.grid.cellCounts[0] - 1 and self.gridPos[2] > 0:
            b57 = self.grid.cells[(self.gridPos[0] + 1 , self.gridPos[1], self.gridPos[2] - 1)]
            
        b67 = None
        if self.gridPos[1] < self.grid.cellCounts[1] - 1 and self.gridPos[2] > 0:
            b67 = self.grid.cells[(self.gridPos[0], self.gridPos[1] + 1, self.gridPos[2] - 1)]
        
    #    b04
    #    b15
    #    b26
    #    b37 
        
        b04 = None
        if self.gridPos[0] > 0 and self.gridPos[1] > 0:
            b04 = self.grid.cells[(self.gridPos[0] - 1 , self.gridPos[1] - 1, self.gridPos[2])]
            
        b15 = None
        if self.gridPos[0] < self.grid.cellCounts[0] - 1 and self.gridPos[1] > 0:
            b15 = self.grid.cells[(self.gridPos[0] + 1 , self.gridPos[1] - 1, self.gridPos[2])]
            
        b26 = None
        if self.gridPos[0] > 0 and self.gridPos[1] < self.grid.cellCounts[1] - 1:
            b26 = self.grid.cells[(self.gridPos[0] - 1 , self.gridPos[1] + 1, self.gridPos[2])]
            
        b37 = None
        if self.gridPos[0] < self.grid.cellCounts[0] - 1 and self.gridPos[1] < self.grid.cellCounts[1] - 1:
            b37 = self.grid.cells[(self.gridPos[0] + 1 , self.gridPos[1] + 1, self.gridPos[2])]
            
        self.neighbors = [back, front, left, right, top, bottom, c0, c1, c2, c3, c4, c5, c6, c7,
                          b01, b02, b13, b23, b45, b46, b57, b67, b04, b15, b26, b37]
        
    def testGroundCell(self):   
        #test distance of closest point on poly to cell center,
        #if it is in range, cell becomes groundcell
        #if neighbors opposite to each other both are groundcells, cell itself
        #becomes groundcell too
        
        #print ("In testGroundCell") 
        if self.grid.grounds == None:
            return None
               
        for ground in self.grid.grounds:
            #print ("GROUND/EDGE: ", ground, ground.edges)
            for edge in ground.edges:
                closest = mathutils.geometry.intersect_point_line(Vector(self.center), 
                          Vector(edge[0]), Vector(edge[1]))
                vec = closest[0]
                percentage = closest[1]
               # print(vec.to_tuple(), self.center, self.gridPos)
                if self.isInside(vec.to_tuple(), percentage) and not self.isGroundCell:
                    print("Found Ground Cell: ", self.gridPos, vec, percentage)
                    self.isGroundCell = True                        
                   
class Grid:
    
    cellCoord = {}
    
    def __init__(self, cellCounts, pos, dim, children, grounds):
        self.cells = {}
        self.grounds = grounds
        #must start at upper left corner of bbox, that is the "origin" of the grid
        self.center = pos
        self.pos = (pos[0] - dim[0] / 2, pos[1] - dim[1] / 2, pos[2] - dim[2] / 2)
        self.dim = dim #from objects bbox
        self.children = children
        self.cellCounts = cellCounts
    
        self.cellDim = [ dim[0] / cellCounts[0], dim[1] / cellCounts[1], 
                         dim[2] / cellCounts[2]]
                         
        print("cell/grid dimension/center: ", self.cellDim, self.dim, self.center)
        
        #build cells
        for x in range(0, cellCounts[0]):
            for y in range(0, cellCounts[1]):
                for z in range(0, cellCounts[2]):
                   self.cells[(x,y,z)] = Cell((x,y,z), self)
                   
        self.children = None
    
    def buildNeighborhood(self):
        [c.findNeighbors() for c in self.cells.values()]
        
    def findGroundCells(self):
        gcells = [c.testGroundCell() for c in self.cells.values()]
        gcellsPos = [c.gridPos for c in gcells if c != None]
        return gcellsPos    
        
    def setGroundCells(self, gcellsPos):
        for pos in gcellsPos:
            self.cells[pos].isGroundCell = True
            
    def __str__(self):
        return str(self.pos) + " " + str(self.dim) + " " + str(len(self.children))
    
    def getCellByName(self, name):
        return self.cellCoord[name]
    
    def inLayer(self, cell, layer):
        return cell.gridPos[2] == layer
    
    def aboveLayer(self, cell, layer):
        return cell.gridPos[2] >= layer
    
    def layerIntegrity(self, layer, integr):
       # if layer > self.cellCounts[2]:
      #        return False
       # print("Integrity", layer, integr)
        layercells = [c for c in self.cells.values() if self.inLayer(c, layer)]
        layercount = 0
        layerchilds = 0
        for c in layercells:
            layerchilds += len(c.children)
            layercount += c.count
            
        if layercount == 0:
            return False
        print(layerchilds, layercount)
        return (layerchilds / layercount) > integr
    
    def layerDestroyed(self, layer):
        return not self.layerIntegrity(layer, 0)
    
    def weightOnLayer(self, layer):
        weight = [c.children for c in self.cells.values() if self.aboveLayer(c, layer)]
        return len(weight)
    
#    def cellDistribution(self, layer):
#        left = 0
#        right = 0
#        front = 0
#        rear = 0
#        
#        if weightOnLayer(layer) > 0:
#            layercells = [c for c in self.cells.values() if self.inLayer(c, layer)]
#            for c in layercells:
#                layerchilds += len(c.children)
#            
#            for c in layercells:
#                if dim[0] % 2 == 0: 
#                    if c.gridPos[0] <= cellCounts[0] / 2:
#                        left += len(c.children)
#                    elif c.gridPos[0] > cellCounts[0] / 2:
#                        right += len(c.children)
#                elif dim[0] % 2 == 1:
#                    if c.gridPos[0] <= math.floor(cellCounts[0] / 2):
#                        left += len(c.children)
#                    elif c.gridPos[0] > math.ceil(cellCounts[0] / 2):
#                        right += len(c.children) 
#                
#                if dim[1] % 2 == 0: 
#                    if c.gridPos[1] <= cellCounts[1] / 2:
#                        front += len(c.children)
#                    elif c.gridPos[1] > cellCounts[1] / 2:
#                        rear += len(c.children)
#                elif dim[1] % 2 == 1:
#                    if c.gridPos[1] <= math.floor(cellCounts[1] / 2):
#                        front += len(c.children)
#                    elif c.gridPos[1] > math.ceil(cellCounts[1] / 2):
#                        rear += len(c.children)
#                          
#            left = left / layerchilds
#            right = right / layerchilds
#            front = front / layerchilds
#            rear = rear / layerchilds
#            
#        return left, right, front, rear   

class BGEProps(json.JSONEncoder, json.JSONDecoder):
     
     def default(self, o):
         o.__dict__["BGEProps"] = True;
         return o.__dict__;
     
     def object_hook(dct):
         if "BGEProps" in dct:
            props = BGEProps()
            props.__dict__ = dct
            return props
         else:
            return dct
 
#    cluster_dist = []
#    cluster = False
#    is_backup_for = ""
#    hideLayer = 1
#    use_collision_compound = False
#    custom_ball = ""
#    wasCompound = False
#    grid_bbox = (0, 0, 0)
#    grid_dim = (1, 1, 1)
#    individual_override = False
#    radius = 0
#    min_radius = 0
#    modifier = 0
#    hierarchy_depth = 1
#    glue_threshold = 0
#    use_gravity_collapse = False
#    backup = ""
#    children = []
#    ascendants = []
#    origLoc = (0, 0, 0)
#    mesh_name = ""
#    acceleration_factor = 1
#    ground_connectivity = False
#    destroyable = False
#    destructor = False
#    is_ground = False
#    flatten_hierarchy = False
#    dead_delay = 0
#    destructor_targets = []
#    grounds = []
#    grounds_bbox = []
#    collapse_delay = 0
#    edges = []
#    bbox = []
                        
class DataStore:
    
    from mathutils import Vector
    
    grids = {}
    impactLocation = Vector((0,0,0))
    properties = {}

class Ground:
    edges = []
    