bl_info = {
    "name": "Space Colonisation Trees",
    "category": "Mesh",
    "author": "Leafar",
    }

# Based on the paper 'Modeling Trees with a Space Colonization Algorithm'
# by Adam Runions, Brendan Lane, and Przemyslaw Prusinkiewicz

import math
import bpy
import mathutils
from mathutils import Vector

import random
from functools import reduce
from time import time

import numpy as np


def logTime(f):
    def wrapped(*args, **kwargs):
        return Debug.logTime(f, *args, **kwargs)
    return wrapped

#############################################

class Node:
    """
    A node in the skeleton graph of a tree.
    It stores:
        - its position
        - its parent node (None for a root node)
        - the list of its children
        - the collection of AttractionPoints that influence it
          (i.e. those AP, to which it is the closest node)
    """
    
    def __init__(self, position, parent):
        self.position = position
        self.parent = parent
        self.children = []
        self.influencingAttractors = []
        self.radius = None
    
    def grow(self, growthStep, bias=Vector()):
        """
        If this node is influenced by AttractionPoints, spawn a new child node.
        The direction is determined by the Ap, while growthStep determines the distance.
        bias can be used to influence the direction.
        Returns the new child node, or None if no child is created.
        """
        # only grow, if there is an attractor
        if len(self.influencingAttractors) == 0:
            return None
        # find the average direction of attractors
        direction = Vector()
        for ap in self.influencingAttractors:
            direction += (ap.position - self.position).normalized()
        direction.normalize()
        # apply bias
        direction = (direction+bias).normalized()
        # new childnode with distance determined by growthStep
        newPosition = self.position+(growthStep*direction)
        if any(child.position == newPosition for child in self.children) or newPosition == self.position:
            # if the AP lie 'opposed' to each other, the child can be actually further away from them, than this node
            # then the same child (w.r.t. position) would be grown again and again
            return None
        newChild = Node(newPosition, self)
        self.children.append(newChild)
        return newChild
    
    def refreshRadius(self, r_0, r_dl, power):
        "all nodes start with undefined radius. this function sets the radius in this node and all of its child nodes."
        for c in self.children:
            c.refreshRadius(r_0, r_dl, power)
        
        def radiusComingFromChild(child):
            return child.radius + r_dl*(self.position-child.position).length
        
        if len(self.children) == 0:
            self.radius = r_0
        elif len(self.children) == 1:
            self.radius = radiusComingFromChild(self.children[0])
        else: # r^n = sum(r_i^n)
            self.radius = sum(map(lambda c: radiusComingFromChild(c)**power, self.children))**(1/power)
            
    def posRad(self):
        "return a 4d Vector with xyz being the position and w the radius (may be None!) of this node."
        tmp = self.position.to_4d()
        tmp.w = self.radius
        return tmp
    
    def __len__(self):
        "Total number of (transitive) children"
        return sum(map(len, self.children)) + len(self.children)

#############################################

class AttractionPoint:
    """
    An attraction point. It stores:
        - its position
        - its radius of influence
        - the node closest to it (None if all nodes are outside the radius of infleunce)
        - its kill distance (the AP will be removed, when a node is closer than the kill distance)
    """
    
    def __init__(self, position, killDist, radiusInfluence):
        self.position = position
        self.radiusInfluence = radiusInfluence
        self.killDistance = killDist
        self.closestNode = None
        
    def updateClosest(self, newNodes):
        if len(newNodes) == 0:
            return
        # find closest of newNodes first
        newNode = min(newNodes, key=lambda n: distance(n, self))
        newDist = distance(newNode, self)
        
        if newDist < self.radiusInfluence and ( self.closestNode == None or newDist < distance(self.closestNode, self) ):
            if self.closestNode != None:
                self.closestNode.influencingAttractors.remove(self)
            self.closestNode = newNode
            self.closestNode.influencingAttractors.append(self)
    
    def checkKill(self):
        if self.closestNode == None:
            return False
        return distance(self.closestNode, self) <= self.killDistance
    
    def kill(self):
        if not self.closestNode == None:
            self.closestNode.influencingAttractors.remove(self)

#############################################

class Skeleton:
    """
    Skeleton graph of a tree.
    It holds the list of its nodes and a separate reference to its root node.
    """
    
    def __init__(self, rootPosition):
        self.rootNode = Node(rootPosition, None)
        self.nodes = [self.rootNode]
    
    @logTime
    def grow(self, growthStep, biasFun = lambda s, n: Vector()):
        newNodes = []
        for n in self.nodes:
            nn = n.grow(growthStep, biasFun(self,n))
            if nn != None:
                newNodes.append(nn)
        self.nodes.extend(newNodes)
        return newNodes
    
    @logTime
    def decimate(self, threshold=.1):
        # error from connecting n1 to n2 directly and dropping the nodes in dropped
        # uses sum of squared distance of the dropped nodes
        def approxError(n1, n2, dropped):
            err = 0
            for d in dropped:
                projection, _ = mathutils.geometry.intersect_point_line(d.position, n1.position, n2.position)
                err += (projection-d.position).length_squared
            return err
        
        def nextBestNode(node):
            origin = node.parent
            curNode = node
            droppedNodes = []
            
            while len(curNode.children) == 1: # for now, do not remove branching nodes or leaves
                if approxError(origin, curNode.children[0], droppedNodes) > threshold:
                    break
                droppedNodes.append(curNode)
                curNode = curNode.children[0]
            
            return curNode, droppedNodes
        
        stack = [self.rootNode]
        totalDropped = 0
        
        while len(stack) != 0:
            curNode = stack.pop()
            for child in curNode.children.copy(): # copy, s.t. we can modify the original list
                replacement, droppedNodes = nextBestNode(child)
                # replace original child with next approximation and update link
                curNode.children.remove(child)
                curNode.children.append(replacement)
                replacement.parent = curNode
                # remove intermediate nodes
                for n in droppedNodes:
                    self.nodes.remove(n)
                totalDropped += len(droppedNodes)
                # continue decimation from new child
                stack.append(replacement)
        Debug.log("dropped", totalDropped, "nodes,", len(self.nodes), "remaining")
        
    @logTime
    def rootSmooth(self, strength=.5):
        """
        From the paper, page 2:
            Moving each remaining node in parallel half way toward its more basal neighbor
            reduces the branching angles (...) and can have a significant impact on the
            overall appearance of the tree.
        """
        def smoothNode(node):
            for c in node.children:
                smoothNode(c)
            if node.parent != None:
                node.position =  (1-strength)*node.position + strength*node.parent.position
        smoothNode(self.rootNode)

    @logTime
    def toBlenderSkeleton(self):
        """
        Create a new Blender mesh object from this skeleton.
        Does not link the object to the scene.
        """
        vertices = [self.rootNode.position]
        edges = []
        stack = [(0, self.rootNode)]
        
        while len(stack) != 0:
            curIdx, curNode = stack.pop()
            for childNode in curNode.children:
                vertices.append(childNode.position)
                edges.append([curIdx, len(vertices)-1])
                stack.append((len(vertices)-1, childNode))
        
        newMesh = bpy.data.meshes.new("Tree Skeleton")
        newMesh.from_pydata(vertices, edges, [])
        newMesh.update()
        Debug.log("New Skeleton with %i verts and %i edges" % (len(vertices), len(edges)))
        return bpy.data.objects.new("Tree Skeleton", newMesh)

    
    @classmethod
    @logTime
    def fromBlenderSkeleton(cls, bskel):
        """
        Re-create a Skeleton object from a given Blender mesh.
        The edge graph of the mesh needs to be a tree.
        For a given edge it is assumed, that the node with the lower index is the parent node.
        Accordingly the vertex with index 0 is used as the root for this Skeleton.
        """
        assertMesh(bskel)
        skel = Skeleton(Vector())
        nodes = [ Node(Vector(v.co), None) for v in bskel.data.vertices.values()]
        for e in bskel.data.edges.values():
            parent = nodes[min(e.vertices)]
            child = nodes[max(e.vertices)]
            if child.parent != None:
                raise Exception("Mesh is no edge tree or vertices are not correctly ordered.")
            child.parent = parent
            parent.children.append(child)
        skel.rootNode = nodes[0]
        skel.nodes = nodes
        return skel
    
    @logTime
    def toCylinderMesh(self):
        """
        Simply wraps cone stumps aroung each segment of the skeleton.
        """
        NUM_POINTS = 8 # LOD for the top/bottom circles of the cone stumps
        
        vertices = []
        faces = []
        stack = []
        stack.extend(self.rootNode.children)
        
        while len(stack) != 0:
            curNode = stack.pop()
            parent = curNode.parent
            
            while True:
                direction = curNode.position - parent.position
                
                i1 = len(vertices)
                vertices.extend(circlePoints(parent.position, direction, parent.radius, NUM_POINTS))
                i2 = len(vertices)
                vertices.extend(circlePoints(curNode.position, direction, curNode.radius, NUM_POINTS))
                
                for f in range(NUM_POINTS):
                    faces.append((i1+f, i1+(f+1)%NUM_POINTS, i2+(f+1)%NUM_POINTS, i2+f))

                if len(curNode.children) != 1:
                    break;
                parent = curNode
                curNode = curNode.children[0]
                
            stack.extend(curNode.children)
            
        newMesh = bpy.data.meshes.new("Tree")
        newMesh.from_pydata(vertices, [], faces)
        newMesh.update()
        return bpy.data.objects.new("Tree", newMesh)

#############################################

class ChangeNumTree(bpy.types.Operator):
    """
    Operator with the sole purpose of setting the number of trees.
    Needed, as the UI cannot change dynamically.
    """
    bl_idname = "mesh.change_num_trees"
    bl_label = "Generate Tree"
    
    rootCount = bpy.props.IntProperty(
        name="Number of Trees",
        description="How many root points to use",
        default=1, min=1
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        GrowTree.rootCount = self.rootCount
        bpy.ops.mesh.grow_tree('INVOKE_DEFAULT')
        return {'FINISHED'}

#############################################

class RootPropertyGroup(bpy.types.PropertyGroup):
    position = bpy.props.FloatVectorProperty(
        name = "Position",
        description = "The world space position from which a tree will start to grow",
        default=(0,0,0), size=3, precision=3
    )
    
    def show(self, layout):
        layout.row().prop(self, "position")

class GrowTree(bpy.types.Operator):
    bl_idname = "mesh.grow_tree"
    bl_label = "Generate Tree Skeleton"
    bl_options = {'INTERNAL'}
    
    roots = bpy.props.CollectionProperty(
        name = "Roots",
        description = "The world space positions from which trees will start to grow",
        type = RootPropertyGroup
    )
    rootCount = 1

    density = bpy.props.FloatProperty(
        name="Density",
        description="Density of attraction points",
        default=100, min=0
    )
    radiusInfluence = bpy.props.FloatProperty(
        name="Radius of Influence",
        description="Maximum distance up to which a node is influenced by an attraction point",
        default=float("inf"), min=0, precision=4
    )
    killDist = bpy.props.FloatProperty(
        name="Kill Distance",
        description="If a node is closer than this distance to an attraction point, the AP will be removed",
        default=.2, min=0
    )
    step = bpy.props.FloatProperty(
        name="Growth Step",
        description="The distance a newly grown node starts away from its parent",
        default=.1, min=0
    )
    bias = bpy.props.FloatVectorProperty(
        name = "Growth Bias",
        description = "Bias applied to the growth direction induced by the attraction points. Its length determines the relative weight",
        default=(0,0,0), size=3, precision=3
    )
    wind = bpy.props.FloatVectorProperty(
        name = "Wind",
        description = "Wind is applied to the attraction points after each growth step",
        default=(0,0,0), size=3, precision=3
    )
    iterations = bpy.props.IntProperty(
        name="Iterations",
        description="Maximum number of iterations to perform",
        default=100, min=1
    )
    
    smoothingStrength = bpy.props.FloatProperty(
        name="Smoothing Strength",
        description="All nodes will be moved towards their more basal neighbour by the given factor",
        default=.5, min=0, max=1
    )
    decimationThreshold = bpy.props.FloatProperty(
        name="Decimation Threshold",
        description="The maximum allowed error per new segment. (The skeleton is simplified by removing nodes. The squared distance of removed nodes to the new segment is used as error.)",
        default=.01, min=0
    )

    baseSkeleton = bpy.props.BoolProperty(name="Create Base Skeleton", default=False)
    smoothedSkeleton = bpy.props.BoolProperty(name="Create smooth Skeleton", default=True)
    meshing = bpy.props.BoolProperty(name="Continue with Meshing", default=True)
    
    @logTime
    def spawnAttractionPoints(self, meshObject):
        bbox = BBOX(meshObject.bound_box)
        Debug.log("BBox: ", bbox.center, bbox.dim)
        Debug.log("Scale: ", meshObject.scale)
        volume = bbox.dim.x*meshObject.scale.x * bbox.dim.y*meshObject.scale.y * bbox.dim.z*meshObject.scale.z
        Debug.log("Volume: ", volume)
        Debug.log("Num APs: ", int(volume*self.density))
        points = []
        for n in range(int(volume*self.density)):
            p = bbox.randomPoint()
            if isPointInside(meshObject, p):
                # we have been working in object space so far
                p = meshObject.matrix_world*p
                points.append(AttractionPoint(p, self.killDist, self.radiusInfluence))
        return points

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)
    
    def logReport(self, msg):
        self.report({'INFO'}, msg)
        Debug.log(msg)
    
    def draw(self, context):
        col = self.layout.column()
        
        col.prop(self, "rootCount")
        while len(self.roots) > self.rootCount:
            self.roots.remove()
        while len(self.roots) < self.rootCount:
            self.roots.add()
        
        for r in self.roots:
            r.show(col)
            col.separator()
        
        row = col.row()
        col1, col2 = row.column(), row.column()
        col1.scale_x=2 # higher weight, s.t. labels don't get cut
        def showProp(prop):
            col1.label(prop[1]["name"])
            col2.row().prop(self, prop[1]["attr"], text="")
        
        showProp(GrowTree.density)
        showProp(GrowTree.radiusInfluence)
        showProp(GrowTree.killDist)
        showProp(GrowTree.step)
        showProp(GrowTree.bias)
        showProp(GrowTree.wind)
        showProp(GrowTree.iterations)
        col1.separator() ; col2.separator()
        
        showProp(GrowTree.smoothingStrength)
        showProp(GrowTree.decimationThreshold)
        col1.separator() ; col2.separator()
        
        showProp(GrowTree.baseSkeleton)
        showProp(GrowTree.smoothedSkeleton)
        showProp(GrowTree.meshing)
    
    def execute(self, context):
        assertMesh(context.object)
        
        trees = [Skeleton(Vector(r.position)) for r in self.roots]
        attrPoints = self.spawnAttractionPoints(context.object)
        Debug.log("Generated %i APs" % (len(attrPoints)))
        for ap in attrPoints:
            ap.updateClosest([t.rootNode for t in trees])
        biasFun = lambda s, n: Vector(self.bias)
        
        growstart = time()
        for i in range(self.iterations):
            newGrowths = reduce(lambda x,y: x+y, [tree.grow(self.step, biasFun) for tree in trees])
            # abort if nothing grows anymore
            Debug.log("Round %i: %i new growths" % (i, len(newGrowths)))
            if len(newGrowths) == 0:
                break
            # apply wind
            for ap in attrPoints:
                ap.position += Vector(self.wind)
            # update the closest nodes to the attraction points
            # and check if any need to be removed
            deadAttrPoints = []
            for ap in attrPoints:
                ap.updateClosest(newGrowths)
                if ap.checkKill():
                    ap.kill()
                    deadAttrPoints.append(ap)
            for ap in deadAttrPoints:
                attrPoints.remove(ap)
            self.logReport("Round %i: %i APs removed, %i remaining" % (i, len(deadAttrPoints), len(attrPoints)))
            # abort if all attraction points are reached
            if len(attrPoints) == 0:
                Debug.log("All APs reached in round %i" % (i))
                break;
        
        self.logReport("Creating trees took %f seconds" % (time()-growstart))
        
        treeCreated = False
        for tree in trees:
            if len(tree.nodes) == 1: #skip trees that did not grow
                Debug.log("tree at", tree.rootNode.position, "did not grow")
                continue
            
            if self.baseSkeleton:
                treeCreated = True
                linkAndSelect(tree.toBlenderSkeleton(), context)
            
            tree.rootSmooth(self.smoothingStrength)
            tree.decimate(self.decimationThreshold)
            
            if self.smoothedSkeleton:
                treeCreated = True
                linkAndSelect(tree.toBlenderSkeleton(), context)
            
        if not treeCreated:
            self.logReport("No tree was created. Check the parameters.")
        
        # for now only mesh one of the produced trees, otherwise all dialogues would appear at once
        if (self.baseSkeleton or self.smoothedSkeleton) and self.meshing and treeCreated:
            bpy.ops.mesh.tree_mesh('INVOKE_DEFAULT')
        else:
            Debug.asTextBlock()
            Debug.clear()
        
        return {'FINISHED'}

#############################################

class SplineNode:
    
    def __init__(self, spline, children):
        self.spline = spline
        self.parent = None
        self.children = children
        for c in children:
            c[1].parent = self
    
    def sampleSpline(self, spacing=.1, nu=0):
        """
        returns an array of Vector samples along the spline.
        the samples are roughly spacing apart in parameter space.
        at least two samples are returned.
        """
        xmin, xmax = min(self.spline.x), max(self.spline.x)
        return map(Vector, [self.spline( x, nu ) for x in np.linspace(xmin, xmax, max(int((xmax-xmin)/spacing), 2))])

class SplineSkeleton:
    
    def __init__(self, skeleton):
        """converts the given 'normal' Skeleton (of line segments) into a Spline based representation"""
        self.nodes = []
        
        def toSplineBranch(node, next=None):
            x = [0]
            y = [node.posRad()]
            children = []
            
            if next != None:
                x.append(distance(node, next))
                y.append(next.posRad())
                node = next
                y[0].w = y[0].w*.2+y[1].w*.8 # when branching off, the parent radius is likely too large
            
            while len(node.children) != 0: # while the branch has not reached its end
                # continue with a node of large radius and going in a similar direction
                maxChild = max(node.children,
                        key=lambda c: c.radius/node.radius 
                            + (0 if node.parent==None else (node.position-node.parent.position).normalized().dot((c.position-node.position).normalized())) )
                x.append(x[-1] + distance(node, maxChild))
                y.append(maxChild.posRad())
                for c in node.children: # all other child nodes at this point
                    if c != maxChild: # are considered 'side shoots'
                        children.append( (x[-2], toSplineBranch(node, c)) )
                node = maxChild
            
            dy = [y[1]-y[0]]
            # finite difference approach for tangent approximation
            dy.extend( ( (y[i+1]-y[i])/(x[i+1]-x[i]) + (y[i+2]-y[i+1])/(x[i+2]-x[i+1]) )/2 for i in range(len(y)-2) )
            dy.append(y[-1]-y[-2])
            
            # TODO find a way to allow user-controlled tension (i.e. boundary conditions)
            newNode = SplineNode(
                HermiteInterpolator(x, y, dy), 
                children)
            self.nodes.append(newNode)
            return newNode
        
        self.rootNode = toSplineBranch(skeleton.rootNode)
        Debug.log("New Spline Skeleton of {} splines".format(len(self.nodes)))
    
    @logTime
    def toBlenderSkeleton(self, sampleDistance):
        """
        Create a new Blender mesh object from this skeleton.
        Does not link the object to the scene.
        """
        vertices = []
        edges = []
        
        for node in self.nodes:
            idx = len(vertices)
            vertices.extend( map(lambda vec: vec.xyz, node.sampleSpline(sampleDistance)) ) # remove radius information
            edges.extend( zip(range(idx, len(vertices)-1), range(idx+1, len(vertices))) )
        
        newMesh = bpy.data.meshes.new("Tree Spline Skeleton")
        newMesh.from_pydata(vertices, edges, [])
        newMesh.update()
        Debug.log("Created %i verts and %i edges from spline skeleton" % (len(vertices), len(edges)))
        return bpy.data.objects.new("Tree Spline Skeleton", newMesh)

    @logTime
    def toMesh(self, NUM_POINTS, sampleDistance):
        vertices = []
        faces = []
        
        for node in self.nodes:
            # TODO generate ramiforms
            i1 = None
            s_pre = None
            for s, dsdx, dsdx2 in zip(node.sampleSpline(sampleDistance), node.sampleSpline(sampleDistance, nu=1), node.sampleSpline(sampleDistance, nu=2)):
                i2 = len(vertices)
                
                if s.w < 1e-9: # vanishing radius -> branch tip; assumption: this may not happen on first sample, where i1==None
                    vertices.append(s.xyz)
                    for f in range(NUM_POINTS):
                        faces.append((i1 + f, i1 + (f+1)%NUM_POINTS, i2))
                    break

                vertices.extend( circlePoints(s.xyz, dsdx.xyz, s.w, NUM_POINTS) )
                if i1 != None: # nothing to connect for first points
                    # reduce twist by minimizing angle between the side edges and the center line
                    tmp = [(vertices[i2+o]-vertices[i1]).angle((s-s_pre).xyz)  for o in range(NUM_POINTS)]
                    offset = int(np.argmin( tmp ))
                    
                    for f in range(NUM_POINTS):
                        faces.append((i1 + f, i1 + (f+1)%NUM_POINTS, i2 + (f+offset+1)%NUM_POINTS, i2 + (f+offset)%NUM_POINTS))
                i1 = i2
                s_pre = s
            
        newMesh = bpy.data.meshes.new("Spline Tree")
        newMesh.from_pydata(vertices, [], faces)
        newMesh.materials.append(barkMaterial())
        newMesh.update()
        return bpy.data.objects.new("Spline Tree", newMesh)

#############################################

class MeshTree(bpy.types.Operator):
    bl_idname = "mesh.tree_mesh"
    bl_label = "Mesh Tree"
    
    baseRadius = bpy.props.FloatProperty(
        name="Start Width",
        description="Radius of a branch at its tip",
        default=.001, min=0, precision=4
    )
    radiusIncrease = bpy.props.FloatProperty(
        name="Radius Increase",
        description="By how much the branch width increases over one unit length",
        default=.015, min=0, precision=4
    )
    radiusPower = bpy.props.FloatProperty(
        name="PM Exponent",
        description="Exponent for the pipe model formula determining combined branch radius: r**x=sum(r_c**x for c in children)",
        default=2.5, min=1, soft_min=2, soft_max=3, precision=4
    )
    
    circleLOD = bpy.props.IntProperty(
        name="#Points per Circle",
        description="How many points to use for each circle along the mesh",
        default=8, min=3
    )
    samplingStep = bpy.props.FloatProperty(
        name="Sampling Step",
        description="How detailed to sample the branch splines. Corresponds to the approximate length of cone sections in the mesh",
        default=.1, min=.0001, precision=4
    )
    
    splineSkeleton = bpy.props.BoolProperty(name="Create Spline Skeleton", default=False)
    splineMesh = bpy.props.BoolProperty(name="Create Spline Mesh", default=True)
    
    doGrowLeaves = bpy.props.BoolProperty(name="Grow Leaves", default=True)
    leafDensity = bpy.props.FloatProperty(
        name="Leaf Distance",
        description="At what interval to place leaves along branches",
        default=.02, min=0, precision=3
    )
    leafSize = bpy.props.FloatProperty(
        name="Leaf Size",
        description="Size of the generated leaves",
        default=.05, min=0, precision=3
    )
    minRadius = bpy.props.FloatProperty(
        name="Min Width",
        description="Minimum width a branch needs to support leaves",
        default=0, min=0, precision=3
    )
    maxRadius = bpy.props.FloatProperty(
        name="Max Width",
        description="Maximum width a branch may have to support leaves",
        default=.1, min=0, precision=3
    )
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        assertMesh(context.object)
        tree = Skeleton.fromBlenderSkeleton(context.object)
        
        tree.rootNode.refreshRadius(self.baseRadius, self.radiusIncrease, self.radiusPower)
        Debug.log("Trunk base radius: {}".format(tree.rootNode.radius))
        
        splineTree = SplineSkeleton(tree)
        if self.splineSkeleton:
            linkAndSelect(splineTree.toBlenderSkeleton(self.samplingStep), context)
        if self.splineMesh:
            linkAndSelect(splineTree.toMesh(self.circleLOD, self.samplingStep), context)
        if self.doGrowLeaves:
            self.growLeaves(context, splineTree)
        
        Debug.asTextBlock()
        Debug.clear()
        
        return {'FINISHED'}
    
    @logTime
    def growLeaves(self, context, splineTree):
        verts = []
        faces = []
        for node in splineTree.nodes:
            for sample, ds in zip(node.sampleSpline(self.leafDensity), node.sampleSpline(self.leafDensity, nu=1)):
                if sample.w <= self.maxRadius and sample.w >= self.minRadius:
                    verts.extend(
                        leafVertices(
                            position=sample.xyz + ds.xyz.normalized().orthogonal()*sample.w,
                            rotation=mathutils.Quaternion(ds.xyz, random.uniform(0, 2*math.pi)),
                            size=self.leafSize)
                    )
                    faces.append(range(len(verts)-4, len(verts)))
        
        Debug.log(len(verts)//4, "leaves grown")
        newMesh = bpy.data.meshes.new("Leaves")
        newMesh.from_pydata(verts, [], faces)
        newMesh.materials.append(leafMaterial())
        newMesh.update()
        newObj = bpy.data.objects.new("Leaves", newMesh)
        context.scene.objects.link(newObj)
                    
    
def leafVertices(position=Vector(), rotation=mathutils.Euler(Vector()), size=.05):
    verts = [Vector((0, 0, 0)), Vector((size, size/2, 0)), Vector((size*2, 0 ,0)), Vector((size, -size/2, 0))]
    for v in verts:
        v.rotate(rotation)
    return [v+position for v in verts]
    

def leafMaterial():
    _leafMaterialName = "LeafMat"
    mat = bpy.data.materials.get(_leafMaterialName)
    if mat is None:
        mat = bpy.data.materials.new(_leafMaterialName)
        mat.diffuse_color = (0.02, 0.42, 0.01)
        mat.specular_intensity = 0.2
    return mat

#############################################
# un-/register and formalities
#############################################

def register():
    bpy.utils.register_class(RootPropertyGroup)
    bpy.utils.register_class(GrowTree)
    bpy.utils.register_class(MeshTree)
    bpy.utils.register_class(ChangeNumTree)

def unregister():
    bpy.utils.unregister_class(GrowTree)
    bpy.utils.unregister_class(MeshTree)
    bpy.utils.unregister_class(RootPropertyGroup)
    bpy.utils.unregister_class(ChangeNumTree)
  
if __name__ == "__main__":
    register()

#############################################
# utils
#############################################

def isPointInside(meshObject, point):
    closestPoint, normal, _ = meshObject.closest_point_on_mesh(point)
    direction = closestPoint - point
    if direction.dot(normal) > 0:
        return True
    return False

def distance(a, b):
    return (a.position - b.position).length

def assertMesh(obj):
    if type(obj) != bpy.types.Object:
        raise Exception("Not a Blender object!")
    if obj.type != 'MESH':
        raise Exception("Expected a mesh object.")

class BBOX:
    def __init__(self, bpyBbox):
        x = [v[0] for v in bpyBbox[:]]
        y = [v[1] for v in bpyBbox[:]]
        z = [v[2] for v in bpyBbox[:]]
        self.min = Vector([min(x), min(y), min(z)])
        self.max = Vector([max(x), max(y), max(z)])
        self.dim = self.max - self.min
        self.center = (self.max + self.min) / 2

    def randomPoint(self):
        return Vector([random.uniform(self.min[i], self.max[i]) for i in range(3)])

def orthogonals(vector):
    o1 = vector.orthogonal()
    return o1.normalized(), vector.cross(o1).normalized()

def circlePoints(center, normal, radius, number):
    o1, o2 = orthogonals(normal)
    return [ center + radius* ( math.sin(2*math.pi*i/number)*o1 + math.cos(2*math.pi*i/number)*o2 ) for i in range(number) ]

def circlePoints2(center, o1, o2, radius, number):
    return [ center + radius* ( math.sin(2*math.pi*i/number)*o1 + math.cos(2*math.pi*i/number)*o2 ) for i in range(number) ]

def linkAndSelect(obj, context):
    context.scene.objects.link(obj)
    bpy.ops.object.select_all(action = "DESELECT")
    obj.select = True
    context.scene.objects.active = obj

def barkMaterial():
    _barkMaterialName = "TreeBark"
    mat = bpy.data.materials.get(_barkMaterialName)
    if mat is None:
        mat = bpy.data.materials.new(_barkMaterialName)
        mat.diffuse_color = (0.13, 0.02, 0.00)
        mat.specular_intensity = 0
    return mat

#############################################

# cubic hermite basis functions
H30 = np.poly1d([ 2, -3, 0, 1])
H31 = np.poly1d([ 1, -2, 1, 0])
H32 = np.poly1d([ 1, -1, 0, 0])
H33 = np.poly1d([-2,  3, 0, 0])

class HermiteInterpolator:
    
    def __init__(self, x, y, dy):
        if len(x) != len(y) or len(y) != len(dy):
            raise ValueError
        self.x = x
        self.y = y
        self.dy = dy
    
    def __call__(self, xval, nu=0):
        i, t = self.locate(xval)
        tangentScale = self.x[i+1]-self.x[i] # necessary, as we do not generally interpolate over unit intervals
        return ( float(H30.deriv(nu)(t)) * self.y [i] +
                 float(H31.deriv(nu)(t)) * tangentScale * self.dy[i] +
                 float(H32.deriv(nu)(t)) * tangentScale * self.dy[i+1] +
                 float(H33.deriv(nu)(t)) * self.y [i+1] )
    
    def locate(self, xval):
        """ find index and normalised parameter t for the given x. clamps to the range of x. """
        for i, xi in enumerate(self.x, -1):
            if xval < xi:
                if i == -1:
                    return 0, 0
                return i, (xval-self.x[i])/(xi-self.x[i])
        return len(self.x)-2, 1

#############################################

class Debug:
    
    msg = []
    
    @classmethod
    def log(cls, *args):
        print(args)
        cls.msg.append(" ".join(map(str, args)))
    
    @classmethod
    def logTime(cls, func, *args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        cls.log(func.__name__, "took", t2-t1, "seconds")
        return result
     
    @classmethod
    def showAsPopup(cls):
        def draw(self, context):
            for m in cls.msg:
                self.layout.label(m)
        bpy.context.window_manager.popup_menu(draw, title="Log", icon='INFO')
    
    @classmethod
    def asTextBlock(cls, name="Debug_Log"):
        if len(cls.msg) == 0:
            return # do not write empty log
        
        textBlock = bpy.data.texts.get(name)
        if textBlock == None:
            textBlock = bpy.data.texts.new(name)
        textBlock.from_string("\n".join(cls.msg))
    
    @classmethod
    def clear(cls):
        cls.msg = []
