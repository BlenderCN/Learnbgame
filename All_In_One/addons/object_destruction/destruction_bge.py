from bge import logic
import destruction_data as dd
import math
from mathutils import Vector, Matrix
from time import clock
#import bpy
from threading import Timer
import sys

import jsondata
import json


#this is the bge part of the destructability editor.
#it actually executes the destruction according to its definition.

#check if object  is destroyable

#if we take care about ground /hardpoint connection of registered grounds
#determine which cells are ground and at each impact check cell neighborhood (availability and integrity)

#then check for ground connection; if none, do collapse, activate all children(according to availability)
#and if desired the whole ascendancy tree.
#this is an additional flag -> how many hierarchy levels each destructor can destroy

#if there is ground connection inactivate all cell children.

#then wait for collision, if it is a registered destroyer, activate children according to speed an mass of destroyer (larger radius) for testing purposes create/register player balls as destroyer automatically. to each destroyable. 

#define Parameters for each object ! here defined for testing purposes
maxHierarchyDepth = 1 # this must be stored per destructor, how deep destruction shall be
doReturn = False
integrity = 0.5

children = {}
scene = logic.getCurrentScene()
gridValid = False
firstparent = []
firstShard = {}
#bpyObjs = {}
delay = 0
#alive_threshold = 5

#TODO, temporary hack
ground = None
#destructors = []
objectCount = 0
allInUse = False
tempLoc = Vector((0,0,0))
initswap = []
firstGround = None
isCollapsing = False

def getProp(name):
    return dd.DataStore.properties[name]

def project(p, n):
    
    #project point / plane by omitting coordinate which is the largest in the normal vector
    max = 0
    maxindex = 2
    for i in range(0, 3):
        co = math.fabs(n[i])
        if co > max:
            maxindex = i
            max = co
    
    if maxindex == 0:
        v1 = 1
        v2 = 2
    elif maxindex == 1:
        v1 = 0
        v2 = 2
    elif maxindex == 2:
        v1 = 0
        v2 = 1
    
 #   print(p)
    p1 = Vector((p[v1], p[v2]))
    
    return p1

def isLeft(a, b, p):
    
    return (b[0] - a[0]) * (p[1] - a[1]) - (p[0] - a[0]) * (b[1] - a[1]) 

def inside(p, n, obj):
    #print(obj)
    #verts = obj.data.vertices
    edges = getProp(obj.name).edges #obj.data.edges
    wn = 0
    for e in edges:
        v1 = e[0] #verts[e.vertices[0]]
        v2 = e[1] #verts[e.vertices[1]]
        
        vp1 = project(v1.co, n)
        vp2 = project(v2.co, n)
        p1 = project(p, n)
        
        if (vp1[1] <= p1[1]):                         # start y <= P.y
            if (vp2[1] > p1[1]):                      # an upward crossing
                if (isLeft( vp1, vp2, p1) > 0):       # P left of edge
                    wn += 1                           # have a valid up intersect
        
        else:                                         # start y > P.y (no test needed)
            if (vp2[1] <= p1[1]):                     # a downward crossing
                if (isLeft( vp1, vp2, p1) < 0):       # P right of edge
                    wn -= 1                           # have a valid down intersect
    return wn != 0
        
def distance(p, a, b, c, obj):
    n = (c-a).cross(b-a)
    
    f = -n.dot(p-a) / n.dot(n)
    q = p + f * n
    
    dist = sys.maxsize #10000000000
    if inside(q, n, obj):
        dist = (p - q).length
    return dist

def getFaceDistance(a, b):
    
    # hack
    #print(a, b)
    if isDestructor(a) and isGround(a):
        mindist = sys.maxsize# 10000000000
        #obj = bpy.data.objects[a.name]
        #for f in obj.data.polygons:
        #   v1 = obj.data.vertices[f.vertices[0]].co
        #   v2 = obj.data.vertices[f.vertices[1]].co
        #   v3 = obj.data.vertices[f.vertices[2]].co
        mesh = a.meshes[0]
        for m_index in range(mesh.materials):
            for p_index in range(mesh.numPolygons):
                p = mesh.getPolygon(p_index)
                v1 = Vector(mesh.getVertex(m_index, p.v1).XYZ)
                v2 = Vector(mesh.getVertex(m_index, p.v2).XYZ)
                v3 = Vector(mesh.getVertex(m_index, p.v3).XYZ)
           
               #print("ShardPos", b.localPosition)
                dist = distance(b.worldPosition, v1, v2, v3, a)
                   
                if dist < mindist:
                    dist = dist
                return mindist
    else:
        if b in scene.objects:
            return a.getDistanceTo(b)
        #else: ???? 
        #    return a.getDistanceTo(b.location)
        else:
            return sys.maxsize        

def descendants(p):
    ret = []
    ret.extend(p.children)
    for c in p.children:
        ret.extend(descendants(c))
    return ret 


#def decideDeactivation(obj):
#    if not obj.invalid and obj.getLinearVelocity() <= alive_threshold:
#        obj.suspendDynamics()               

def setupClusters():
    #setup clusters
    clusterchilds = {}
    parents = [p for p in scene.objects if p.name.startswith("P_")]
    
    #determine max level
    level = 0
    for p in parents:
        lev = int(p.name.split("_")[1])
        if lev > level:
            level = lev
            
    #compare with max level
    leafparents = []        
    for p in parents:
        lev = int(p.name.split("_")[1])
        if lev == level:
            leafparents.append(p)
            
    childs = [c for c in scene.objects if hasMyParent(c, leafparents)]
    
    for p in leafparents:
        #par = bpy.context.scene.objects[p.name]
        cluster = getProp(p.name).cluster
        if cluster:#par.destruction.cluster:
            for c in childs:
                ch = c #bpy.context.scene.objects[c.name]
                if not ch.name.startswith("P_") and ch.destruction.is_backup_for == "":  
                
                   bbox = getProp(ch.name).bbox    
                   #bboxX = ch.bound_box.data.dimensions[0]
                   #bboxY = ch.bound_box.data.dimensions[1]
                   #bboxZ = ch.bound_box.data.dimensions[2]
                   distVec = c.worldPosition - p.worldPosition
                   if distVec[0] <= par.destruction.cluster_dist[0] / 100 * bbox[0] and \
                       distVec[1] <= par.destruction.cluster_dist[1] / 100 * bbox[1] and \
                       distVec[2] <= par.destruction.cluster_dist[2] / 100 * bbox[2]:
                           c.setParent(p)
                           if p.name not in clusterchilds.keys():
                                clusterchilds[p.name] = []
                           clusterchilds[p.name].append(c.name)
                           
    #append to higher parents as well
    for p in parents:
        desc = descendants(p)
        for n in clusterchilds.keys():
            if scene.objects[n] in desc:
                for d in desc:
                    if d.name.startswith("P_"):
                        for c in clusterchilds[n]:
                            ch = scene.objects[c]
                            ch.setParent(d) #evtl verdoppeln der objekte....(mehrere Parents geht nicht....)
    

def hasMyParent(obj, leafparents):
    return "myParent" in obj.getPropertyNames() and \
    scene.objects[obj["myParent"]] in leafparents 
    

def loadBGEProps():
    #dd.DataStore.properties = json.loads(jsondata.data)
 #   print("Loaded:", len(dd.DataStore.properties))
    d = json.loads(jsondata.data, object_hook = dd.BGEProps.object_hook)
    dd.DataStore.properties = d
    #print("GROUNDD: ", d["Ground"].edges)

def setup():
    
    global firstparent
    global firstShard
    global ground
    global children
   # global destructors
    global firstGround
    print("setup")
    
    loadBGEProps()
    #temporarily parent
 
    for o in scene.objects:
        if o.name != "Player":
            if "myParent" in o.getPropertyNames():
                parentname = o["myParent"]
                           
                if getProp(scene.name).hideLayer != 1: #bpy.context.scene.hideLayer != 1:
                    if parentname not in scene.objects:
                        p = scene.addObject(parentname, parentname)
                    else:
                        p = scene.objects[parentname]    
                else:
                    p = scene.objects[parentname]
                
                if parentname.startswith("P_0") and p not in firstparent:
                    firstparent.append(p)   
                            
                #print("Setting temp parent", o, parentname)
                o.setParent(p)
                #bpyObjs[o.name] = bpy.data.objects[o.name]
                o["activated"] = False
                o["suspended"] = False
               # o["lastdist"] = sys.maxsize
        if isGround(o):# o.name == "Ground":
            if firstGround == None:
                firstGround = o.name
            #bpyObjs[o.name] = bpy.data.objects[o.name]
       # if isDestructor(o):
        #    destructors.append(o)
        #    bpyObjs[o.name] = bpy.context.scene.objects[o.name]
    
        
    setupClusters()
        
    for o in scene.objects:
        if "myParent" in o.getPropertyNames():  
            #print(o, o.parent, len(o.parent.children))
            if flattenHierarchy(o):
                for fp in firstparent:
                    desc = descendants(fp)
                    if getProp(o.name).use_collision_compound and o in desc:#bpyObjs[o.name].game.use_collision_compound and o in desc :
                        if fp.name not in firstShard.keys() and fp.name != getProp(scene.name).custom_ball:#bpy.context.scene.custom_ball:
                            print("Setting compound", o.name)
                            fp["compound"] = o.name
                            firstShard[fp.name] = o
                             
                    if fp.name not in children.keys() and o in desc and not o.name.startswith("P_"):
                        children[fp.name] = list()
                        children[fp.name].append(o.name)
                        
                    elif o in desc and not o.name.startswith("P_"):
                        children[fp.name].append(o.name)
                        
            else:
                if not o.name.startswith("P_"):
                    if o.parent.name not in children.keys():
                        children[o.parent.name] = list()
                    children[o.parent.name].append(o.name)
    
    for o in scene.objects:
        if "myParent" in o.getPropertyNames(): 
            o.removeParent()                   
            
    print(len(children))
        
         
    compounds = {}
    realcompounds = {}              
    start = None
    for i in children.items():
        parent = None
        oldPar = scene.objects[i[0]]  
        split = oldPar.name.split(".")
        temp = split[0]
        sp = temp.split("_")
        
        if len(sp) >= 4:
            start = sp[3]
        else:
            start = temp
         
        
        #backup = bpyObjs[oldPar.name].destruction.backup
        
        for c in i[1]:    
           
            if getProp(c).use_collision_compound or getProp(c).was_compound:#bpyObjs[c].game.use_collision_compound or \
            #bpyObjs[c].destruction.wasCompound:
                parent = c
                if start not in compounds.keys():
                    compounds[start] = list()
                compounds[start].append(c)
                print("Appending compound", c, start)
                
                if getProp(c).use_collision_compound:#bpyObjs[c].game.use_collision_compound:
                    realcompounds[start] = c
                    oldPar["compound"] = c
                
                 
        for c in i[1]:
            if c != parent:
                o = scene.objects[c]
               # if isDeformable(o):
                #    p = scene.objects[parent]
                #    print("PARENT", p)
                #    o.setSoftbodyLJoint(p) # joints must be set between adjacent(!) objects
                #    o["joint"] = parent
                #    o.suspendDynamics()
                #    p.suspendDynamics()
                     
                if flattenHierarchy(o) and o not in firstShard and oldPar.name != getProp(scene.name).custom_ball:#bpy.context.scene.custom_ball:
                    #if oldPar.name in firstShard: 
                    parent = firstShard[oldPar.name]
                    print("Setting parent", o, " -> ", parent)
                    o.setParent(parent, True, False)   
                elif c not in firstShard and oldPar.name != getProp(scene.name).custom_ball:#bpy.context.scene.custom_ball:
                    #if c != backup:
                   # print("Setting parent hierarchically", c, " -> ", parent)  
                    o.setParent(parent, True, False)
             
                #keep sticky if groundConnectivity is wanted
                if isGroundConnectivity(oldPar) and oldPar.name != getProp(scene.name).custom_ball:#bpy.context.scene.custom_ball:
                    o.suspendDynamics()
                    #parent.suspendDynamics()
                    ground = scene.objects[firstGround]
                    o.setParent(ground, True, False)
        
    if start in compounds.keys():
        print(compounds[start])                
        if len(compounds[start]) > 1: #TODO, what if there are no real compounds left... use other layers for correct substitution
            real = scene.objects[realcompounds[start]]
            for c in compounds[start]:
               # obj = bpy.context.scene.objects[c]
                par = getProp(c).is_backup_for# obj.destruction.is_backup_for
                if c != real.name and (par == "" or not par.startswith("P_0_")):
                    childs = [ob for ob in scene.objects[c].children]
                    for ch in childs:
                        print("Re-Setting compound 1", ch,  " -> ", real) 
                        ch.removeParent()
                        ch.setParent(real, True, False)
                        #ch["compound"] = c
                    
                    o = scene.objects[c]    
                    print("Re-Setting compound 2", o,  " -> ", real) 
                    o.setParent(real, True, False)

    #swap immediately
    if getProp(scene.name).hideLayer != 1: #should be in ANY object #bpy.context.scene.hideLayer != 1:
        for p in firstparent: 
            if p.name != getProp(scene.name).custom_ball:#bpy.context.scene.custom_ball:
                #par = bpy.context.scene.objects[p.name]
                initswap = swapBackup(scene.objects[getProp(p.name).backup], None)
    
    for first in firstparent:
        if first.name != getProp(scene.name).custom_ball:# bpy.context.scene.custom_ball:
            if isGroundConnectivity(first):
                calculateGrids()
                                           
def checkSpeed():
#    global gridValid
    #control = logic.getCurrentController()
   # owner = control.sensors["Always"].owner #name it correctly
    
    for owner in scene.objects:
        if owner.name.startswith("P_"):
            continue
        if not "activated" in owner.getPropertyNames():
            continue
    
  #  for p in children.keys():
#        for obj in children[p]:
            
 #           if p not in scene.objects:
  #              return
#            
#            if obj == owner.name and not isGroundConnectivity(scene.objects[p]):
#                return 
#        
        vel = owner.worldLinearVelocity
#    thresh = 0.001
#    if math.fabs(vel[0]) < thresh and math.fabs(vel[1]) < thresh and math.fabs(vel[2]) < thresh:
#        if not gridValid:
#            calculateGrids()
#            gridValid = True
        
        if not "suspended" in owner.getPropertyNames():
            continue 
        
        try: # if object has no physics controller, possible if object has no verts (error case)
            if vel.length < 0.5 and owner["activated"] and not owner["suspended"]:
                print("suspending", owner.name)
                owner["suspended"] = True
                #owner["lastdist"] = math.fabs((owner.worldPosition - scene.objects["Ground"].worldPosition)[2])
           #    print("d", owner["lastdist"])
                owner.suspendDynamics()
        except AttributeError:
            continue
        
def allChildren(name):
    
    ret = []
    for c in name.children:
        print("NAME", c.name)
        if c.name.startswith("P_"):
            ret.extend(allChildren(c))
        else:
           ret.append(c)
    return ret
            
def calculateGrids():
    
    #recalculate grid after movement
    global firstparent
    global firstShard
    global ground
    global children
    
    print("In Calculate Grids")
    
    
    for o in scene.objects:
        if isGroundConnectivity(o):# or (isGround(o) and not isDestructor(o)):
            print("ISGROUNDCONN")
            
          #  bbox = getFloats(o["gridbbox"])
        #    dim = getInts(o["griddim"])
            gridbbox = getProp(o.name).grid_bbox #bpy.context.scene.objects[o.name].destruction.gridBBox
            griddim = getProp(o.name).grid_dim #bpy.context.scene.objects[o.name].destruction.gridDim
            
            bbox = (gridbbox[0], gridbbox[1], gridbbox[2])
            dim = (griddim[0], griddim[1], griddim[2])
            
            groundnames = getProp(o.name).grounds
            groundObjs = [logic.getCurrentScene().objects[g] for g in groundnames]
            grounds = []
            
            for fp in firstparent:
                #fp = scene.objects[f]
                if o.name in fp.name:
                    [go.setParent(fp, False, False) for go in groundObjs]
                    
                    oldRot = Matrix(fp.worldOrientation)
                    fp.worldOrientation = Vector((0, 0, 0))
                    for g in groundObjs:
                        gr = dd.Ground()
                        gr.pos = Vector(g.worldPosition)
                       # print(gr.pos, g.worldPosition, g, groundObjs)
                        gr.edges = getProp(g.name).edges
                       # print(gr.edges)
                        grounds.append(gr)
                        
                    #ac = allChildren(o.name)
                    childs = [scene.objects[c] for c in children[o.name]]
                    grid = dd.Grid(dim, o.worldPosition, bbox, childs, grounds)
                    grid.buildNeighborhood()
                    grid.findGroundCells() 
                    dd.DataStore.grids[o.name] = grid
                    
                    fp.worldOrientation = oldRot
                    [g.removeParent() for g in groundObjs]
            
           # ground = groundObjs[0]
        
    print("Grids: ", dd.DataStore.grids) 

def modSpeed(owner, speed):
    #ownerBpy = bpy.data.objects[owner.name]
    hit = owner.sensors["Collision"].hitObject
    if hit != None and getProp(owner.name).individual_override and \
    isRegistered(findParent(hit), owner):
        #hitBpy = bpy.data.objects[hit.name]
        radius = getProp(hit.name).radius #hitBpy.destruction.radius
        modifier = getProp(hit.name).modifier #hitBpy.destruction.modifier
    else:
        radius = getProp(owner.name).radius #ownerBpy.destruction.radius
        modifier = getProp(owner.name).modifier#ownerBpy.destruction.modifier
        
    #1 + 0.025*speed        
    mSpeed = radius + modifier *speed
    return mSpeed    
        

def distSpeed(owner, obj, maxDepth, lastSpeed):
    speed = 0
    
    # only compound parents have a speed....
    try:
        tempSpeed = (owner.worldLinearVelocity - obj.worldLinearVelocity).length
    except AttributeError:
        tempSpeed = 0
        
    if owner.name != "Ball":
        if tempSpeed != 0:
            speed = tempSpeed
        else:
            speed = lastSpeed # only compound parents have a speed....
    else:
        speed = tempSpeed
    
    dist = getFaceDistance(owner, obj)
    
 #   print(owner, obj, dist, speed)
    #destruction radius constant or speed dependent, user specifyable
    mSpeed = modSpeed(owner, speed)
  #  if owner.name == "Ball": # and bpy.context.scene.hideLayer == 1:
#       modSpeed = math.sqrt(speed / 2)
    
    #the faster the smaller the parts but
    if mSpeed > 0:
        depth = math.ceil(maxDepth * 1.0 / mSpeed)
    else:
        depth = 1
    #not greater than maxDepth
    if depth > maxDepth:
        depth = maxDepth
   # print("DEPTH", depth) 
    #return dist < modSpeed
    return dist, mSpeed, depth
    
def collide():
    
   
    global maxHierarchyDepth
    global ground
    global firstparent
    global allInUse
    global children
    global firstGround
    global isCollapsing
    #colliders have collision sensors attached, which trigger for registered destructibles only
    
    #first the script controller brick, its sensor and owner are needed
    control = logic.getCurrentController()
    scene = logic.getCurrentScene()
    sensor = control.sensors["Collision"]
    owner = sensor.owner
    print("collide", owner)
   
    maxHierarchyDepth = hierarchyDepth(owner)
    
    gridValid = False
    
   # print("collide")
    cellsToCheck = []
    lastSpeed = 0
    isGroundConn = False 
    #low speed ball makes no damage, so ignore it in collision calculation
    #if owner.name == "Ball":
    #    if owner.worldLinearVelocity.length < 5:
    #        return
                
    isDynamic = False
    #if "inactive" in owner.getPropertyNames():
    #    return
    #owner["inactive"] = True
    if allInUse:
        return
    
    lastSpeed = 0
    
# DYNAMIC NOT SUPPORTED IN BLENDERPLAYER...      
#    hitObjs = [h for h in sensor.hitObjectList]    
#    for hitObj in hitObjs:
#        print(hitObj.name)
#        if "orig" in hitObj.getPropertyNames():
#            bpyObj = bpy.data.objects[hitObj["orig"]]
#        else:
#            bpyObj = bpy.data.objects[hitObj.name]
#                
#        if bpyObj.destruction.dynamic_mode == "D_DYNAMIC" and bpyObj.name != firstGround:
#            isDynamic = True 
#          
#            bpy.context.scene.objects.active = bpyObj
#            bpyObj.select = True
#            bpyObj.destruction.transmitMode = "T_SELF"
#            
#            vol = bpyObj.destruction.voro_volume
#            name = bpyObj.name 
#            if not "noFracture" in owner.getPropertyNames():
#                if "isShard" in hitObj.getPropertyNames() and "activated" in hitObj.getPropertyNames() and \
#                hitObj["activated"] == True:    
#                    bpyObj.destruction.voro_volume = ""
#                    bpy.ops.object.destroy()
#                    bpyObj.destruction.voro_volume = vol
#                    #owner["noFracture"] = True
#                else:
#                    bpy.ops.object.destroy(impactLoc = owner.worldPosition)
#                owner["noFracture"] = True
#            bpyObj.select = False
#            
#           objs = swapDynamic(name, hitObj)
#            if objs == None:
#                continue
#                #substitute parent with children.... maybe before convert ? is convert necessary at all ?
#            for o in objs:
#                o["isShard"] = True
#                
#                if compareSpeed(owner, o):
#                    o.restoreDynamics()
#                    o["activated"] = True
#            
#           # handle all other objects as well        
#            for o in scene.objects:
#                try:
#                    if compareSpeed(owner, o):
#                        o.restoreDynamics()
#                        o["activated"] = True
#                except AttributeError:
#                    print("AttributeError", o.name)
#                    continue
#                           
#    if isDynamic:
#        print("Returning")
#        return
    
            
    for fp in firstparent:
        if not isGroundConnectivity(fp):
            if "compound" in fp.getPropertyNames() and fp["compound"] in scene.objects:
                compound = scene.objects[fp["compound"]]
                if (compound.worldLinearVelocity.length < 0.05 and owner.name == firstGround):
                    return #if compound does not move, ignore collisions...
        else: # a quicker pre-test of cells (less than objects)
            isGroundConn = True
            if fp.name in dd.DataStore.grids.keys():
                grid = dd.DataStore.grids[fp.name] 
                for cell in grid.cells.values():
                    #modSpeed = math.sqrt(owner.worldLinearVelocity.length / 2)
                    speed = (owner.worldLinearVelocity).length # groundConn means obj has 0 speed
                    mSpeed = modSpeed(owner, speed)
                    celldist = (owner.worldPosition - Vector(cell.center)).length
                    if celldist < mSpeed:
                        cellsToCheck.append(cell)
                          
                
    objs = []
    restoreAll()
    
    #print(children)
    
    depth = getProp(owner.name).hierarchy_depth #bpy.context.scene.objects[owner.name].destruction.hierarchy_depth  
    #print("LEN", len(cellsToCheck))
    if not isGroundConn or isCollapsing or depth > 1:
        #without grid, check all objects (bad)
        #print("checking all")
        for p in children.keys():
            for objname in children[p]:
                #print("objname", p, objname)
                if not objname.startswith("P_"):
                    if objname in scene.objects:
                        objs.append(objname)
    else:
        for c in cellsToCheck:
            objs.extend(c.children)
    
    lastSpeed = 0 
   # print("LENOBJS", len(objs))       
    for ob in objs:
        if ob in scene.objects:
            obj = scene.objects[ob]
            dist, speed, depth =  distSpeed(owner, obj, maxHierarchyDepth, lastSpeed)
            if speed > 0:
                lastSpeed = speed
            
            strength = 0 #handle bomb here
            if "strength" in owner.getPropertyNames():
                strength = owner["strength"]
                depth = maxHierarchyDepth #blow all apart
            
            glue = getProp(obj.name).glue_threshold#bpy.data.objects[obj.name].destruction.glue_threshold 
            
            #print("Collide", owner, dist, speed)
            if (dist < speed and glue < speed) or (dist < strength and glue < strength):  
                dissolve(obj, depth, maxHierarchyDepth, owner)
            
            #if isDeformable(obj):
            #    obj.cutSoftbodyLink(owner.worldPosition, dist)
            #    child.setSoftbodyPose(True, True)

def checkGravityCollapse():
    #check for gravity collapse (with ground connectivity)
    global firstparent
    
    #print("checkGravityCollapse")
    checkSpeed()
   
    if not getProp(scene.name).use_gravity_collapse:#bpy.context.scene.useGravityCollapse:
        return 
    
    for first in firstparent:
        if isGroundConnectivity(first):
            if first.name in dd.DataStore.grids.keys():
                grid = dd.DataStore.grids[first.name]
                if grid.dim[2] > 1:
                    intPerLayer = 0.50 / (grid.cellCounts[2] - 1)
                    for layer in range(0, grid.cellCounts[2]):
                        if not grid.layerIntegrity(layer, 0.90 - layer * intPerLayer):
                            if not grid.layerDestroyed(layer):
                                #print("layer integrity low, destroying layer", layer)
                                cells = dict(grid.cells)
                            
                                #tilt building ?
                                #g = scene.objects["Ground"]
                                #g.worldOrientation = Matrix.Rotation(math.radians(15), 3, 'X')
                                [destroyCell(c, cells, None) for c in grid.cells.values() if grid.inLayer(c, layer)]
                            
                                for c in cells.values():
                                    destroyNeighborhood(c)
                 
                                for c in cells.values():
                                    c.visit = False
                                
                                #apply horizontal impulse according to cell distribution to make
                                #object rotate...
                                #g.worldOrientation = Matrix.Rotation(math.radians(0), 3, 'X')
                            
                                restoreAll()
                                break    
 
def findCompound(childs, parent):
    compound = None
    loc = None
    for c in childs:
        ob = c#bpy.context.scene.objects[c.name]
        par = parent#bpy.context.scene.objects[parent]
        parEnd = par.name.split(".")[1]
        obEnd = ob.name.split(".")[1]
        if getProp(ob.name).use_collision_compound and c.name not in getProp(par.name).ascendants and \
        parEnd != obEnd: #not c.name.endswith(".000"): ".000" = backup of original object
            mesh = getProp(ob.name).mesh_name #ob.data.name
            print("Adding compound", c.name)
            compound = scene.addObject(c.name, c.name)
            compound.worldPosition = ob.location.copy()
            print("POS", compound.worldPosition, ob.location)
            compound.replaceMesh(mesh, True, True)    
            return compound
        elif ob.destruction.was_compound:
            loc = ob.location.copy()
    if compound == None:
        for c in childs:
            ob = c# bpy.context.scene.objects[c.name]
            compound = getProp(ob.name).backup #.destruction.backup
           # mesh = bpy.context.scene.objects[compound].data.name
            print("Testing: ", compound)
            if compound != None and compound != "" and \
            getProp(compound).use_collision_compound:
                print("Adding compound(b)", compound)
                if compound not in scene.objects:
                    #mesh = bpy.context.scene.objects[compound].data.name
                    comp = scene.addObject(compound, compound)
                    if loc != None:
                        comp.worldPosition = loc
                    #comp.replaceMesh(mesh, True, True)
                    return comp
                comp = scene.objects[compound]
                if loc != None:
                    comp.worldPosition = loc
                #comp.replaceMesh(mesh, True, True)
                
                return comp 
        
        #descend if necessary
#        for c in childs:
#            ch= bpy.context.scene.objects[c.name].destruction.children
#            return findCompound(ch, c.name, True)
                

def findFirstParent(parent):
    #TODO: hack -> find first parent, ground connectivity on subparents is unsupported by now.
    #what about loose parts parents (they have another name mostly) ?
    #maybe store a reference to the firstparent directly.
    temp = parent.split(".")[0]
    pstart = temp.split("_")[3]
    
    for fp in firstparent:
        temp = fp.name.split(".")[0]
        fstart = temp.split("_")[3]
        if fstart == pstart:
            return fp
    return None

#def copy(mesh):
#    cp = mesh.copy()
#    cp.use_fake_user = True
#    return cp.name

def toStr(count):
    if count == 0:
        return ""
    if count < 10:
        return ".00" + str(count)
    if count < 100:
        return ".0" + str(count)
    return "." + str(count)

# DYNAMIC NOT SUPPORTED IN BLENDERPLAYER...
#def swapDynamic(objname, obj):
#    
#    global objectCount
#    global allInUse
#    global tempLoc
#    
#    print("swap dynamic")
#    obname = objname
#    if len(objname.split(".")) == 1:
#        obname = "S_" + objname + ".000"
#    bpyOb = bpy.data.objects[obname]
#    
#    print(bpyOb.name)    
#    parent = bpyOb.destruction.is_backup_for
#    if parent == "":
#        return
#    
#    #dynamic case, can only load meshes dynamically (not objects)
#    #use ball (always there on layer 2, assumption) as dummy, add it multiple times
#    if bpyOb.destruction.dynamic_mode == "D_DYNAMIC":
#        par = bpy.data.objects[parent]
#        
#        ch = allChildren(par)
#        #print("Par.children", par, par.children)
#        childs = [c.name for c in ch if c.destruction.is_backup_for == ""]
#        print(len(childs))
#        meshes = [bpy.data.objects[c].data.copy().name for c in childs]
#   #     meshes.reverse()
#        libname = meshes[0]
#        meshproxies = logic.LibNew(libname, "Mesh", meshes)
#        print("after lib new")
#        print(childs, meshproxies)
#        
#        compound = None
#        comp = None
#        for c in childs:
#            if bpy.data.objects[c].game.use_collision_compound:
#                compound = c
#                break
#        
#        ret = []
#        
#        obb = par
#        correction = obb.location.copy()
#        while obb.parent != None:
#            obb = obb.parent
#            correction += obb.location
#                
#        for i in range(0, len(childs)):
#            
#            child = bpy.data.objects[childs[i]]     
#            dummy = "Dummy" + toStr(objectCount)
#            objectCount += 1
#            try:
#                o = scene.addObject(dummy, dummy)
#            except ValueError:
#                # out of pool objects, return here
#                # if a default object was used, the physics mesh
#                # was shared, and a crash is very probable.
#                allInUse = True #prevent further subdivisions
#                return ret
#            
#            if "activated" not in obj.getPropertyNames() or not obj["activated"]: 
#               # o.linearVelocity = Vector((0,0,0))  
#                o.suspendDynamics()
#            o.replaceMesh(meshproxies[i], True, True)
#            #o.suspendDynamics() #IGNORED SILENTLY ????
#            #print("REPLACED", o.name)
#            
#            
#            
#        #    print("CORR", correction, obj.worldPosition, child.location)
#            
#        #    print("VELO", obj.linearVelocity)
#            
#            if "isShard" not in obj.getPropertyNames():
#                o.worldPosition = child.location + correction
#                tempLoc = Vector(bpyOb.destruction.origLoc)
#            elif "activated" in obj.getPropertyNames():
#                o.worldPosition = child.location + obj.worldPosition
#            else:
#                o.worldPosition = child.location + correction   
##            pos = obj.worldPosition + child.location
##            o["posx"] = pos[0]
##            o["posy"] = pos[1]
##            o["posz"] = pos[2]
#            nr = int(meshproxies[i].name.split(".")[1])
#            nr2 = int(compound.split(".")[1])
#            print("NR", nr, nr2)
#            
#            if (nr-len(childs)-1) == nr2:
#                comp = o
#                comp.suspendDynamics()
#            print(o.worldPosition, child.location, o.worldPosition - child.location)        
#            o["orig"] = childs[i]
#          #  o["lastProxy"] = meshproxies[0].name
#            ret.append(o)
#        
#          #  if comp != None:
#        #        for r in ret:
#        #            if r != comp:
#        #                r.setParent(comp, True, False)
#        #        comp.worldOrientation = obj.worldOrientation
#        #    
#        #        for r in ret:
#        #            if r != comp:
#        #                r.removeParent()
#                             
#        print("after replace mesh")
#        obj.endObject()
#       # logic.LibFree(meshes[0])
#        #bpy.context.scene.update()
#        return ret
#    
#    return None                    
                
def swapBackup(obj, owner):    
    
    global children
    global firstparent
    
    print("swap backup", obj)
    ret = []   
    
    obname = obj.name
    parent = getProp(obname).is_backup_for#bpy.context.scene.objects[obname].destruction.is_backup_for
    
    if parent == "":
        return ret
    
    if parent not in scene.objects:
       par = scene.addObject(parent, parent)
    else:
       par = scene.objects[parent]
    
    parents = {}  
    
    first = findFirstParent(parent)
          
    childs= getProp(parent).children#bpy.context.scene.objects[parent].destruction.children
    
    print("CHILDS", childs[0], len(childs))
    compound = findCompound(childs, obname)
    
    if compound != None:
        #if not isGroundConnectivity(first):   
        parents[compound.name] = parent    
        ret.append(compound)
        par["compound"] = compound.name
        #compound.suspendDynamics()
    else:
        return ret
                   
    for c in childs:
        if c.name != compound.name and c.name != obname:
            
            if c.name.startswith("P_"):
                
                if c.name in scene.objects:
                    cPar = scene.objects[c.name]
                else:
                    cPar = scene.addObject(c.name, c.name)
                
                name = getProp(c.name).backup#bpy.context.scene.objects[c.name].destruction.backup
                parents[name] = c.name
                parents[c.name] = parent
                ret.append(cPar)
                if name == compound.name or name == obname:
                    continue
            else:
                name = c.name
                parents[name] = parent
            
            #obb = bpy.context.scene.objects[c.name]    
            #if (owner != None and compareSpeed(owner, obb)) or owner == None:
            print("Adding children", name)
            mesh = getProp(name).mesh_name#bpy.context.scene.objects[name].data.name
            o = scene.addObject(name, name)
            o.replaceMesh(mesh, True, True)
            
            if not isGroundConnectivity(first):
           #     o.worldPosition = obj.worldPosition
                o.setParent(compound, True, False)
            else:
                
                if not o.invalid:
                    o.suspendDynamics()
                    o.setParent(ground, False, False)
                         
            ret.append(o)
    
    if not isGroundConnectivity(first):
        if not parent.startswith("P_0_"):
            compound.worldPosition = obj.worldPosition        
        compound.worldOrientation = obj.worldOrientation
        
        lin = obj.linearVelocity.copy()
        lin.rotate(obj.worldOrientation)
        compound.linearVelocity = lin
        
        ang = obj.angularVelocity.copy()
        ang.rotate(obj.worldOrientation)
        compound.angularVelocity = ang
    else:
        compound.setParent(ground, False, False)
    
    if parent in children.keys():
        if obname in children[parent]:
            children[parent].remove(obname)
    obj.endObject()
    
   # if objParent in children.keys():
    #    if parent in children[objParent]:
     #       children[objParent].remove(parent)
    #parent.endObject()
    
    for r in ret:
        p = parents[r.name]
        if p not in children.keys():
            children[p] = list()
        children[p].append(r.name)
    
   # print("SWAP:", ret, p, children[p])
    
    if isGroundConnectivity(first):
        calculateGrids()
      
    return ret

#def pChildren(parent):
#    childs = bpy.context.scene.objects[parent.name].destruction.children
#    ret = []
#    for c in childs:
#        if c.name in scene.objects:
#            ret.append(scene.objects[c.name])
#        else:
#            ret.append(scene.addObject(c.name, c.name))
#    return ret
   

def compareSpeed(owner, obj):
    lastSpeed = 0
    if isRegistered(findParent(obj), owner):
        maxHierarchyDepth = hierarchyDepth(obj)
    else:
        maxHierarchyDepth = hierarchyDepth(owner)
    dist, speed, depth =  distSpeed(owner, obj, maxHierarchyDepth , lastSpeed)
    if speed > 0:
        lastSpeed = speed
    
    try:
        glue = getProp(obj.name).glue_threshold#bpy.data.objects[obj.name].destruction.glue_threshold
    except KeyError: #catch some strange error with __default_cam__ in dynamic fracture
        glue = 0 
    finally:    
        return (dist < speed) and (glue < speed) 
    
def findParent(obj):
    global children
    
    parent = None
    for p in children.keys():
        if obj.name in children[p]:
            parent = p
            break
        
    par = None
    if parent != None:
        if parent in scene.objects:
            par = scene.objects[parent]
        else:
            par = scene.addObject(parent, parent)
    else:
        par = ground
    
    return par
    
   
#recursively destroy parent relationships    
def dissolve(obj, depth, maxdepth, owner):
    
    global initswap
    global children
    
    print("dissolve", obj, depth)
    parent = findParent(obj)
    owparent = findParent(owner)               
  
    print("Owner:", owner, obj, isRegistered(parent, owner), isRegistered(parent, owparent), isDestroyable(parent), parent.name)
     
    if isDestroyable(parent) and (isRegistered(parent, owner) or isRegistered(parent, owparent) or \
    isGround(parent)):
            
        grid = None
        if parent.name in dd.DataStore.grids.keys():
            grid = dd.DataStore.grids[parent.name]                
        
        #only activate objects at current depth
        if parent != None:# and par.name != "Ground":
            digitEnd = parent.name.split("_")[1]
            objDepth = int(digitEnd) 
            
            if obj.name.startswith("P_"):
                backup = getProp(obj.name).backup#bpy.context.scene.objects[obj.name].destruction.backup
                if backup in scene.objects:
                    obj = scene.objects[backup]
                else:
                    return
                
            bDepth = backupDepth(obj)
             
            #print(depth, objDepth+1, bDepth+1)
            first = findFirstParent(parent.name)
            if getProp(scene.name).hideLayer!= 1 and isBackup(obj) and ((depth == bDepth+1)):# \
           # or ((depth == bDepth) and (owner.name == "Ball")) \
            #and not isGroundConnectivity(first)):
                print(depth, bDepth, isGroundConnectivity(first))
                if getProp(obj.name).use_collision_compound:#bpy.context.scene.objects[obj.name].game.use_collision_compound:
                    for ch in obj.children:
                        ch.removeParent()
                        if isBackup(ch):
                            shards = swapBackup(ch, owner)
                            ch["swapped"] = True
                            [activate(s, owner, grid) for s in shards if compareSpeed(owner, s)]
                        #else:
                            activate(ch, owner, grid)
                                        
                objs = swapBackup(obj, owner)
                obj["swapped"] = True
                 
                #[activate(ob, owner, grid) for ob in objs if compareSpeed(owner, ob)]
                              
             #activate previously swapped shards    
            if (depth == objDepth+1):
                    
                [activate(ob, owner, grid) for ob in initswap if compareSpeed(owner, ob)]
                activate(obj, owner, grid)
                 
        if depth < maxdepth and parent != None:
            [dissolve(scene.objects[c], depth+1, maxdepth, owner) for c in children[parent.name] \
            if c in scene.objects and not c.startswith("P_")]

def activate(child, owner, grid):
   
     print("activated: ", child)
     global integrity
     global firstShard
     global delay
     
     delay = deadDelay(owner)
     
     parent = None
     for p in children.keys():
        if child.name in children[p]:
            parent = p
            break
    # print("PARENT", parent)
     #ground is parent when connectivity is used    
     if parent == None:
         par = ground
     else:
         par = scene.objects[parent]
         
     #remove all compound children if it is hit
    # if bpy.context.scene.objects[child.name].game.use_collision_compound:
    #     for ch in child.children:
    #         ch.removeParent()
    #         ch.restoreDynamics()     
                 
     #if isGroundConnectivity(par) or isGround(par) and gridValid:
     
     #sc = bpy.context.scene
     #gravity = not sc.useGravityCollapse or \
     #(sc.useGravityCollapse and sc.collapse_delay > 0.0)
     
     if isGroundConnectivity(par):
         if grid != None:
             cells = dict(grid.cells)
             gridPos = grid.getCellByName(child.name)
             
             if gridPos in cells.keys():
                 cell = cells[gridPos]
                 
                 if delay == 0:
                    if (child.name in cell.children):
                        cell.children.remove(child.name)
                
                 if not cell.integrity(integrity):
                    #print("Low Integrity, destroying cell!")
                    destroyCell(cell, cells, None)
                    
                    
                 for c in cells.values():
                    destroyNeighborhood(c)
                 
                 for c in cells.values():
                    c.visit = False
    
     #bpyOwner = bpy.data.objects[owner.name]
     dist = child.getDistanceTo(owner)
     maxRad = getProp(owner.name).radius #bpyOwner.destruction.radius
     minRad = getProp(owner.name).min_radius #bpyOwner.destruction.min_radius
         
     child.restoreDynamics()
     if getProp(owner.name).acceleration_factor != 1: #bpyOwner.destruction.acceleration_factor != 1:
         
         acceleration_factor = (dist - minRad) / (maxRad - minRad) * getProp(owner.name).acceleration_factor #bpyOwner.destruction.acceleration_factor
         child.setLinearVelocity(child.linearVelocity * acceleration_factor)
     
    
     if delay == 0:              
        child.removeParent()
        child["activated"] = True
        
        #if isDeformable(child):
        #   child.setSoftbodyPose(True, True)
        #   
        #   if "joint" in child.getPropertyNames():
        #       child.cutSoftbodyJoint(scene.objects[child["joint"]])
        #    
        #   if parent != None:
        #       if child.name in children[parent]:
        #            children[parent].remove(child.name)
     else:
        if not child.invalid:
            d = (dist - minRad) / (maxRad - minRad) * delay
            t = Timer(d, child.suspendDynamics)
            t.start()

#def isDeformable(obj):
#    if obj == None:
#        return False
#    return bpy.context.scene.objects[obj.name].destruction.deform
            
def isGroundConnectivity(obj):
    global children
    global firstGround
    
    if obj == None:
        return False
    if obj.name in children.keys() and firstGround != None: #valid parent
        groundConnectivity = getProp(obj.name).ground_connectivity #bpy.context.scene.objects[obj.name].destruction.groundConnectivity
        return groundConnectivity
    else:
        return False
#    if obj == None or "groundConnectivity" not in obj.getPropertyNames():
#        return False
#    return obj["groundConnectivity"]

def isDestroyable(obj):
    if obj == None:
        return False
    destroyable = getProp(obj.name).destroyable #bpy.context.scene.objects[obj.name].destruction.destroyable
    return destroyable
#    if destroyable == None or "destroyable" not in destroyable.getPropertyNames():
#        return False
#    return destroyable["destroyable"]

def isDestructor(obj):
    
    global children
    
    if obj == None:
        return False
    
#    if obj.name.startswith("P_"): #TODO find out compoundparent if not custom_ball!!
#        last = children[obj.name][-1]
#        destructor = bpy.context.scene.objects[last.name].destruction.destructor
#    else:
    destructor = getProp(obj.name).destructor #bpy.context.scene.objects[obj.name].destruction.destructor
    return destructor

def isGround(obj):
    
    if obj == None:
        return False
    #if obj.name in bpyObjs.keys():
    try:
        isground = getProp(obj.name).is_ground #bpy.context.scene.objects[obj.name].destruction.isGround
    except KeyError: #catch strange __default_cam__ error again ...
        isground = False
    finally:
        return isground
    #else:
    #    return False

def flattenHierarchy(obj):
    if obj == None:
        return False
    flatten = getProp(obj.name).flatten_hierarchy #bpy.context.scene.objects[obj.name].destruction.flatten_hierarchy
 #   print("Flatten: ", obj, flatten)
    return flatten

def hierarchyDepth(obj):
    if obj == None:
        return -1
    depth = getProp(obj.name).hierarchy_depth #bpy.context.scene.objects[obj.name].destruction.hierarchy_depth
    return depth

def deadDelay(obj):
    if obj == None:
        return 0
    delay = getProp(obj.name).dead_delay #bpy.context.scene.objects[obj.name].destruction.dead_delay
    return delay

def isRegistered(destroyable, destructor):
    
    if not isDestroyable(destroyable):
        return False
    if not isDestructor(destructor):
        return False
    
    global isCollapsing
    if isCollapsing:
        return True
     
    targets = getProp(destructor.name).destructor_targets #bpy.context.scene.objects[destructor.name].destruction.destructorTargets
    for t in targets:
        if t == destroyable.name:
            return True
        
    return False

def backupDepth(backup):
    parent = getProp(backup.name).is_backup_for #bpy.context.scene.objects[backup.name].destruction.is_backup_for
    if parent != "":
        split = parent.split("_")[1]
        return int(split)
    return -10

def isBackup(backup):
    swapped = "swapped" not in backup.getPropertyNames()
    return swapped
        

#def getFloats(str):
#    parts = str.split(" ")
#    return (float(parts[0]), float(parts[1]), float(parts[2]))
#
#def getInts(str):
#    parts = str.split(" ")
#    return (int(parts[0]), int(parts[1]), int(parts[2]))
#

#def getGrounds(obj):
#    grounds = bpy.context.scene.objects[obj.name].destruction.grounds
#    print(grounds)
#    ret = []
#    for ground in grounds:
#        g = dd.Ground()
#        g.name = ground.name
#        
#        bGround = bpy.context.scene.objects[ground.name].bound_box.data.to_mesh(bpy.context.scene, False, 'PREVIEW')
#        for e in bGround.edges:
#            vStart = bGround.vertices[e.vertices[0]].co
#            vEnd = bGround.vertices[e.vertices[1]].co
#            g.edges.append((vStart, vEnd))
#        ret.append(g)
#    print("RET", ret)
#    return ret
#    
#    if "grounds" not in obj.getPropertyNames():
#        return None
#    grounds = []
#    print(obj["grounds"])
#    parts = obj["grounds"].split(" ")
#    for part in parts:
#        p = part.split(";")
#        if p[0] == "" or p[0] == " ":
#            continue
#        ground = dd.Ground()
#        ground.name = p[0]
#  
#        vert = p[1]
#        verts = vert.split("_")
#        for coords in verts:
#            coord = coords.split(",")
# 
#            vertexStart = (float(coord[0]), float(coord[1]), float(coord[2]))
#            vertexEnd = (float(coord[3]), float(coord[4]), float(coord[5]))
#            edge = (vertexStart, vertexEnd)
#            ground.edges.append(edge)
#        grounds.append(ground)
#    return grounds

def restoreAll():
    for c in scene.objects:
        if "activated" in c.getPropertyNames() and c["activated"]:
            #if "lastdist" in c.getPropertyNames():
            #    dist = c["lastdist"]
            #    if dist > 0.01:
            c["suspended"] = False
            c.restoreDynamics()


def destroyFalling(children):
    print("destroyFalling")
    for c in reversed(children):
        c.restoreDynamics()
        c["suspended"] = False
        c["activated"] = True
        c.removeParent()
    restoreAll()   

def destroyNeighborhood(cell):
    
    global doReturn
    global integrity

    doReturn = False
    destlist = []
    destructionList(cell, destlist)
    
    cells = cell.grid.cells
    
    compound = None
    
    if getProp(scene.name).use_gravity_collapse:#bpy.context.scene.useGravityCollapse:
        for c in destlist:
            for ch in c.children:
                if getProp(ch).use_collision_compound: #bpyObjs[ch].game.use_collision_compound: #find highest compound!
                    compound = scene.objects[ch]
                    compound.removeParent()
                    break
            if compound != None:
                break
        
    children = []
    for c in destlist:
        children.extend(destroyCell(c, cells, compound))
    
    if compound != None:
        #STICKINESS DELAY HERE
        compound.restoreDynamics()
        global isCollapsing
        
        if getProp(scene.name).collapse_delay == 0: #bpy.context.scene.collapse_delay == 0:
            isCollapsing = True
        
        if getProp(scene.name).collapse_delay > 0:
            t = Timer(getProp(scene.name).collapse_delay, destroyFalling, args = [children])
            t.start()
    
     
def destroyCell(cell, cells, compound):
    
    global delay
    
    ret = []
    if delay == 0:
        for item in cells.items():
            if cell == item[1] and item[0] in cells:
                del cells[item[0]]
                break
        
   # print("Destroyed: ", cell.gridPos)
    childs = [c for c in cell.children]
    for child in cell.children:
      #  print("cell child: ", o)
        if child in scene.objects:
            o = scene.objects[child]
            
            if compound != None:
               o.setParent(compound, True, False)
               ret.append(o)
               childs.remove(child) 
            else:
                #STICKINESS DELAY HERE
                o.restoreDynamics()
                if delay == 0:
                    o.removeParent()
                    childs.remove(child)
                    o["activated"] = True
                else:
                    if not o.invalid:
                        t = Timer(delay, o.suspendDynamics)
                        t.start()
        else:
            childs.remove(child) #remove invalid child
                    
    cell.children = childs
    return ret      
    

def destructionList(cell, destList):
    
    global doReturn
    global integrity  
    
    
    if (cell.isGroundCell and cell.integrity(integrity)) or cell.visit:
        #print("GroundCell Found:", cell.gridPos)
        while len(destList) > 0:
            c = destList.pop()
            c.visit = True
        doReturn = True    
        return
    
    for neighbor in cell.neighbors:
        if doReturn:
            return    
        if neighbor != None: 
            if not neighbor in destList:
                destList.append(neighbor)
                if neighbor.integrity(integrity):
                    destructionList(neighbor, destList)
                        
    #append self to destlist ALWAYS (if not already there)          
    if cell not in destList:         
        destList.append(cell)
       
    #in a radius around collision check whether this are shards of a destructible /or 
    #whether it is a destructible at all if it is activate cell children and reduce integrity of
    #cells if ground connectivity is taken care of
