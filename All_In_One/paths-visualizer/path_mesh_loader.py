import bpy
import bmesh
from mathutils import *
from math import *

from .gta import sapaths, ivpaths
from .ui_constants import *
from .mesh_layer import AddPathMeshLayers

def debugprintNode(msg, node):
    print('\n' + msg)

    print('area id:' + str(node[NODE_AREAID]))
    print('area id:' + str(node[NODE_ID]))
    print('x: ' + str(node['x']))
    print('y: ' + str(node['y']))
    print('z: ' + str(node['z']))

    print('\n')

def CopyAttributesFromNodeToBMVert(node, bm, bmvert, nodeType):
    bmvert[bm.verts.layers.float[NODE_WIDTH]]                = node[NODE_WIDTH]
    bmvert[bm.verts.layers.int[NODE_BAHAVIOUR]]              = node[NODE_BAHAVIOUR]
    bmvert[bm.verts.layers.int[NODE_ISDEADEND]]              = node[NODE_ISDEADEND]
    bmvert[bm.verts.layers.int[NODE_ISIGNORED]]              = node[NODE_ISIGNORED]
    bmvert[bm.verts.layers.int[NODE_ISROADBLOCK]]            = node[NODE_ISROADBLOCK]
    bmvert[bm.verts.layers.int[NODE_ISEMERGENCYVEHICLEONLY]] = node[NODE_ISEMERGENCYVEHICLEONLY]
    bmvert[bm.verts.layers.int[NODE_ISRESTRICTEDACCESS]]     = node[NODE_ISRESTRICTEDACCESS]
    bmvert[bm.verts.layers.int[NODE_ISDONTWANDER]]           = node[NODE_ISDONTWANDER]
    bmvert[bm.verts.layers.int[NODE_SPEEDLIMIT]]             = node[NODE_SPEEDLIMIT]
    bmvert[bm.verts.layers.int[NODE_SPAWNPROBABILITY]]       = node[NODE_SPAWNPROBABILITY]
    bmvert[bm.verts.layers.string[NODE_TYPE]]                = str.encode(nodeType)
    bmvert[bm.verts.layers.int[NODE_AREAID]]                 = node[NODE_AREAID]
    bmvert[bm.verts.layers.int[NODE_ID]]                     = node[NODE_ID]
    bmvert[bm.verts.layers.int[NODE_FLOOD]]                  = node[NODE_FLOOD]

def CopyAttributesFromLinkToBMEdge(carPathLink, bm, bmedge):
    bmedge[bm.edges.layers.float[EDGE_WIDTH]]                = carPathLink[EDGE_WIDTH]
    bmedge[bm.edges.layers.int[EDGE_NUMLEFTLANES]]           = carPathLink[EDGE_NUMLEFTLANES]
    bmedge[bm.edges.layers.int[EDGE_NUMRIGHTLANES]]          = carPathLink[EDGE_NUMRIGHTLANES]
    bmedge[bm.edges.layers.int[EDGE_ISTRAINCROSSING]]        = carPathLink[EDGE_ISTRAINCROSSING]
    bmedge[bm.edges.layers.int[EDGE_TRAFFICLIGHTDIRECTION]]  = carPathLink[EDGE_TRAFFICLIGHTDIRECTION]
    bmedge[bm.edges.layers.int[EDGE_TRAFFICLIGHTBEHAVIOUR]]  = carPathLink[EDGE_TRAFFICLIGHTBEHAVIOUR]

        
def loadVehicleMesh(ob, nodes):
    bm = bmesh.new()
    bm.from_mesh(ob.data)

    # add the properties
    AddPathMeshLayers(bm)
    
    # add all vertices
    for node in nodes:
        bmvert = bm.verts.new((node['x'], node['y'], node['z']))
        CopyAttributesFromNodeToBMVert(node, bm, bmvert, 'node')

    # add carpathlink vertex usually in the middle
    for node in nodes:
        for link in node['_links']:
            linkedNode = link['targetNode']
            linkedIndex = linkedNode['id']
            carpathlink = link['carpathlink']
            
            # carpathlinks point from higher id to lower id
            if node['id'] > linkedNode['id']:
                bmvert = bm.verts.new((carpathlink['x'], carpathlink['y'], (node['z'] + linkedNode['z']) / 2.0))
                CopyAttributesFromNodeToBMVert(node, bm, bmvert, 'link')

    bm.verts.index_update()
    bm.verts.ensure_lookup_table()

    # connect all the edge data
    k = len(nodes) # offset of carpathlink data
    markedVertexForDeletion = []
    for node in nodes:
        i = node['id']
        for link in node['_links']:
            linkedNode = link['targetNode']
            linkedIndex = linkedNode['id']
            carpathlink = link['carpathlink']
            
            # carpathlinks point from higher id to lower id
            # hence order is also guarenteed
            if node['id'] > linkedNode['id']:
                # from and to order needs to be preserved to hold lane information, make sure blender does not play around with these
                # TODO: check if link order is preserved by blender
                
                #ignore the carpathlink vertex if it lies between a straight line formed by end nodes
                a = (bm.verts[k].co - bm.verts[i].co).xy
                b = (bm.verts[linkedIndex].co - bm.verts[k].co).xy
                
                y_axis = Vector((0, 1))
                a_angle = degrees(y_axis.angle_signed(a))
                b_angle = degrees(y_axis.angle_signed(b))
                
                # these are only carpathlinks anyway
                # TODO: Try and fix these
                
                # don't delete carpathlink vertex at junctions
                if len(node['_links']) != 2 or len(linkedNode['_links']) != 2:
                    a_angle = 999.9
                
                if abs(a_angle - b_angle) < 4.0:
                    # link to carpathpath 
                    bmedge = bm.edges.new( (bm.verts[i], bm.verts[linkedIndex])) 
                    CopyAttributesFromLinkToBMEdge(carpathlink, bm, bmedge)
                    
                    markedVertexForDeletion.append(bm.verts[k])
                else:
                    # link to carpathpath 
                    bmedge = bm.edges.new( (bm.verts[i], bm.verts[k]))
                    CopyAttributesFromLinkToBMEdge(carpathlink, bm, bmedge)
                    # then to targetnode
                    bmedge = bm.edges.new( (bm.verts[k], bm.verts[linkedIndex])) 
                    CopyAttributesFromLinkToBMEdge(carpathlink, bm, bmedge)
                    # copy the carpathlink information
                
                
                k = k+1
    
    
    
    # delete the unrequired vertex
    print("Deleted", len(markedVertexForDeletion), " unrequired carpathlink vertices")
    for v in markedVertexForDeletion:
        bm.verts.remove(v)
    
    bm.to_mesh(ob.data)
    bm.free()
    
def loadPedPathMesh(ob, nodes):
    bm = bmesh.new()
    bm.from_mesh(ob.data)

    # add the properties
    AddPathMeshLayers(bm)
    
    # add all vertices
    for node in nodes:
        bmvert = bm.verts.new((node['x'], node['y'], node['z']))
        CopyAttributesFromNodeToBMVert(node, bm, bmvert, 'node')
        
    bm.verts.index_update()
    bm.verts.ensure_lookup_table()

    # connect all the edge data
    for node in nodes:
        i = node['id']
        for link in node['_links']:
            linkedNode = link['targetNode']
            linkedIndex = linkedNode['id']
            
            # for ped paths there is no carpathlink to check
            try:
                bm.edges.new((bm.verts[i], bm.verts[linkedIndex]))
                #CopyAttributesFromLinkToBMEdge(PEDLINK, bm, bmedge)
            except ValueError: # already exist
                continue
                

    bm.to_mesh(ob.data)
    bm.free()


def loadSAPathsAsMesh(nodesDir):
    paths = sapaths.SAPaths()
    paths.load_nodes_from_directory(nodesDir)    

    # Create object
    ob = bpy.data.objects.new('PathCars', bpy.data.meshes.new('PathMesh')) 
    bpy.context.scene.objects.link(ob)
    loadVehicleMesh(ob, paths.carnodes)

    # Create object
    ob = bpy.data.objects.new('PathBoats', bpy.data.meshes.new('PathMesh')) 
    bpy.context.scene.objects.link(ob)
    loadVehicleMesh(ob, paths.boatnodes)

    # Create object
    ob = bpy.data.objects.new('PathPeds', bpy.data.meshes.new('PathMesh')) 
    bpy.context.scene.objects.link(ob)
    #loadPedPathMesh(ob, paths.pednodes)
    
def loadivVehicleMesh(ob, nodes):
    bm = bmesh.new()
    bm.from_mesh(ob.data)

    # add the properties
    AddPathMeshLayers(bm)
    
    # add all vertices
    for node in nodes:
        bmvert = bm.verts.new((node['x'], node['y'], node['z']))
        CopyAttributesFromNodeToBMVert(node, bm, bmvert, 'node')

    bm.verts.index_update()
    bm.verts.ensure_lookup_table()

    # connect all the edge data
    k = len(nodes) # offset of carpathlink data
    for node in nodes:
        i = node['id']
        for link in node['_links']:
            linkedNode = link['targetNode']
            linkedIndex = linkedNode['id']

            try:
                bmedge = bm.edges.new( (bm.verts[i], bm.verts[linkedIndex]))
                #CopyAttributesFromLinkToBMEdge(carpathlink, bm, bmedge)
            except ValueError: # already exist
                continue

    bm.to_mesh(ob.data)
    bm.free()

def loadIVPathsAsMesh(nodesDir):
    paths = ivpaths.IVPaths()
    paths.load_nodes_from_directory(nodesDir)    

    # Create mesh 
    me = bpy.data.meshes.new('myMesh') 
    # Create object
    ob = bpy.data.objects.new('PathMeshCars', me) 
    bpy.context.scene.objects.link(ob)
    loadivVehicleMesh(ob, paths.carnodes)

    # Create object
    ob = bpy.data.objects.new('PathMeshBoats', bpy.data.meshes.new('myMesh')) 
    bpy.context.scene.objects.link(ob)
    loadivVehicleMesh(ob, paths.boatnodes)