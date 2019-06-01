import bmesh
from mathutils import Vector

from .ui_constants import *
    
# TODO: complete some fields

# export VC PED PATH FOR NOW
def exportPedPaths(filepath, ob):
    print("Exporting to: " + filepath)
    print("Exporting Object: " + ob.name)
    file = open(filepath, 'w')
    file.write("path\n")
    me = ob.data
    
    # Get Bmesh representation
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    
    tagVerts = []
    tagEdges = []
    for i in range(len(bm.verts)):
        tagVerts.append({})
        tagVerts[i]['read'] = False
        tagVerts[i]['group'] = -1
        
    NumGroup = 0
    for i in range(len(bm.edges)):
        tagEdges.append({})
        tagEdges[i]['type'] = "none" # interna/external
        
    for v in bm.verts:
        if tagVerts[v.index]['read']:
            continue
            
        currentIndex = v.index
        internalNodes = []
        visitedNextNodes = []
        g = 0
        while True:
            assert len(bm.verts[currentIndex].link_edges) > 0
            
            nLinked = 0
            for link in bm.verts[currentIndex].link_edges:
                linkVert = link.other_vert( bm.verts[currentIndex] ).index
                  
                if tagVerts[linkVert]['group'] != NumGroup: 
                    nLinked += 1
                    
                    if tagVerts[linkVert]['group'] == -1:
                        visitedNextNodes.append(linkVert)
            
            if (g + nLinked + 1 <= 12):
                tagVerts[currentIndex]['group'] = NumGroup
                tagVerts[currentIndex]['read'] = True
            
                if currentIndex not in internalNodes:
                    internalNodes.append(currentIndex)
                    
                # values might be in the visited Next Nodes
                if currentIndex in visitedNextNodes:
                    visitedNextNodes.remove(currentIndex)
                    
                g += 1
                g = g + nLinked - 1
                if len(visitedNextNodes) == 0:
                    print("Failed LOL by " + str(currentIndex))
                    #Add search again? 
                    #if g < 12 search from a list
                    #TEST CODE
                    
                    #END TEST CODE
                    break
                else:
                    currentIndex = visitedNextNodes.pop()
            else:
                break
                
        print(internalNodes)
        #make sure list is unique
        assert len(internalNodes) == len(set(internalNodes))
        
        groupNodes = []
        for i in range(len(internalNodes)):
            groupNodes.append({})
            
            groupNodes[i]['realIndex'] = internalNodes[i]
            groupNodes[i]['xyz'] = bm.verts[internalNodes[i]].co
            groupNodes[i]['type'] = 2
            groupNodes[i]['next'] = -1
          
        for i in range(len(internalNodes)):
            for link in bm.verts[internalNodes[i]].link_edges:
                linkVert = link.other_vert( bm.verts[internalNodes[i]]).index
                    
                if tagVerts[linkVert]['group'] != NumGroup:
                    #externalNodes
                    externalNode = {}
                    externalNode['realIndex'] = linkVert
                    externalNode['xyz'] = (bm.verts[linkVert].co + bm.verts[internalNodes[i]].co)/2
                    externalNode['type'] = 1
                    externalNode['next'] = i
                    groupNodes.append(externalNode)
                else:
                    if groupNodes[internalNodes.index(linkVert)]['next'] != i and groupNodes[i]['next'] != internalNodes.index(linkVert):
                        groupNodes[internalNodes.index(linkVert)]['next'] = i
            
        # Adding padded nodes
        while len(groupNodes) != 12:
            ignoredNode = {}
            ignoredNode['type'] = 0
            ignoredNode['next'] = -1
            ignoredNode['xyz'] = Vector((0,0,0))
            groupNodes.append(ignoredNode)
            
        file.write("0, -1\n")
        #write relation
        for node in groupNodes:
            file.write( "\t{}, {}, {}, {:.2f}, {:.2f}, {:.2f}, {}, {}, {}, {}, {}, {}\n".format(
                node['type'], 
                node['next'], 
                0,
                node['xyz'].x * 16,
                node['xyz'].x * 16,
                node['xyz'].x * 16,
                2,
                1,
                1,
                1,
                0,
                1
                )
            )
            
        NumGroup += 1
                    
    bm.to_mesh(me)
    bm.free()
    file.write("end\n")
    file.close()
    
def getIgnoredNode():
    ignoredNode = {}
    ignoredNode['type'] = 0
    ignoredNode['next'] = -1
    ignoredNode['xyz'] = Vector((0,0,0))
    ignoredNode['median'] = 0
    ignoredNode['speedlimit'] = 0
    ignoredNode['flags'] = 0
    ignoredNode['spawnrate'] = 0
    ignoredNode['median'] = 0
    ignoredNode['rightLanes'] = 0
    ignoredNode['leftLanes'] = 0
    ignoredNode['realIndex'] = -1
    return ignoredNode
    
def PrepareCentreJunctionOrSingleConnectionGroup(bm, groupNodes, tagVerts) : 
    internalNode = groupNodes[0]
    internalNode['next'] = -1 # first node as internal
    internalNode['type'] = 2 # first node as internal
    internalNode['speedlimit'] = bm.verts[internalNode['realIndex']][bm.verts.layers.int[NODE_SPEEDLIMIT]]
    internalNode['flags'] = 0
    internalNode['spawnrate'] = bm.verts[internalNode['realIndex']][bm.verts.layers.int[NODE_SPAWNPROBABILITY]] / 15.0
    
    internalNode['median'] = 0 #these are ignored anyway
    internalNode['rightLanes'] = 0 #these are ignored anyway
    internalNode['leftLanes'] = 0 #these are ignored anyway
    
    # loop through all external nodes
    for i in range(1, len(groupNodes)):
        bm_edge = bm.edges.get(( bm.verts[ internalNode['realIndex'] ], bm.verts[ groupNodes[i]['realIndex'] ] ))
        toVert = bm_edge.verts[0]
        fromVert = bm_edge.verts[1]
        
        # external Nodes has to reflect line segment
        externalNode = groupNodes[i]
        if externalNode['realIndex'] == fromVert.index:
            externalNode['leftLanes'] = bm_edge[bm.edges.layers.int[EDGE_NUMLEFTLANES]]
            externalNode['rightLanes'] = bm_edge[bm.edges.layers.int[EDGE_NUMRIGHTLANES]]
        else: 
            externalNode['leftLanes'] = bm_edge[bm.edges.layers.int[EDGE_NUMRIGHTLANES]]
            externalNode['rightLanes'] = bm_edge[bm.edges.layers.int[EDGE_NUMLEFTLANES]]
        
        # reflect the lanes to point to beginning of the line segment
        if tagVerts[externalNode['realIndex']]['type'] != "connectedsegmentEnd":
            if externalNode['rightLanes'] != externalNode['leftLanes'] :
                print("Check for bugs at: ", groupNodes[i])
            externalNode['rightLanes'], externalNode['leftLanes'] = externalNode['leftLanes'], externalNode['rightLanes']
        
        externalNode['next'] = 0
        externalNode['type'] = 1
        externalNode['median'] = bm_edge[bm.edges.layers.float[EDGE_WIDTH]]
        externalNode['speedlimit'] = bm.verts[externalNode['realIndex']][bm.verts.layers.int[NODE_SPEEDLIMIT]]
        externalNode['flags'] = 0
        externalNode['spawnrate'] = bm.verts[externalNode['realIndex']][bm.verts.layers.int[NODE_SPAWNPROBABILITY]] / 15.0
        
        
    while len(groupNodes) != 12:
        groupNodes.append(getIgnoredNode())

# tempGroupNodes: line with first and last nodes as external nodes
def PrepareVehicleLineSegmentsGroup(bm, tempGroupNodes):
    assert len(tempGroupNodes) > 2
    groupNodes = []
    
    # add all the internal nodes
    for i in range(len(tempGroupNodes)):
        node = {}
        node['realIndex'] = tempGroupNodes[i]
        if i == 0 or i == len(tempGroupNodes) - 1:
            node['type'] = 1
        else:
            node['type'] = 2
            
        node['speedlimit'] = bm.verts[node['realIndex']][bm.verts.layers.int[NODE_SPEEDLIMIT]]
        node['flags'] = 0
        node['spawnrate'] = bm.verts[node['realIndex']][bm.verts.layers.int[NODE_SPAWNPROBABILITY]] / 15.0
        node['speedlimit'] = bm.verts[node['realIndex']][bm.verts.layers.int[NODE_SPEEDLIMIT]]
        node['xyz'] = bm.verts[node['realIndex']].co
        
        
        if i == len(tempGroupNodes) - 1: # last
            node['next'] = -1
            node['type'] = 1
            
            # End external node's lane must point to other connected line segment
            nextVert = bm.verts[tempGroupNodes[i]].link_edges[0].other_vert(bm.verts[tempGroupNodes[i]]).index
            if nextVert == tempGroupNodes[i-1]:
                nextVert = bm.verts[tempGroupNodes[i]].link_edges[1].other_vert(bm.verts[tempGroupNodes[i]]).index
                    
            bm_edge = bm.edges.get(( bm.verts[ nextVert], bm.verts[ tempGroupNodes[i] ] ))
            toVert = bm_edge.verts[0]
            fromVert = bm_edge.verts[1]
            
            if fromVert.index == tempGroupNodes[i]:
                node['leftLanes'] = bm_edge[bm.edges.layers.int[EDGE_NUMLEFTLANES]]
                node['rightLanes'] = bm_edge[bm.edges.layers.int[EDGE_NUMRIGHTLANES]]
            else: 
                node['rightLanes'] = bm_edge[bm.edges.layers.int[EDGE_NUMLEFTLANES]]
                node['leftLanes'] = bm_edge[bm.edges.layers.int[EDGE_NUMRIGHTLANES]]
            
            node['median'] = bm_edge[bm.edges.layers.float[EDGE_WIDTH]]
        else:
            node['next'] = i + 1
            bm_edge = bm.edges.get(( bm.verts[ tempGroupNodes[i] ], bm.verts[ tempGroupNodes[i+1] ] ))
            toVert = bm_edge.verts[0]
            fromVert = bm_edge.verts[1]
            
            node['median'] = bm_edge[bm.edges.layers.float[EDGE_WIDTH]]
            
            if fromVert.index == tempGroupNodes[i]:
                node['leftLanes'] = bm_edge[bm.edges.layers.int[EDGE_NUMLEFTLANES]]
                node['rightLanes'] = bm_edge[bm.edges.layers.int[EDGE_NUMRIGHTLANES]]
            else: 
                node['rightLanes'] = bm_edge[bm.edges.layers.int[EDGE_NUMLEFTLANES]]
                node['leftLanes'] = bm_edge[bm.edges.layers.int[EDGE_NUMRIGHTLANES]]
        
        groupNodes.append(node)
        
    # sort groupNodes, external Nodes at last  
    firstExternalNode = groupNodes[0]
    groupNodes.remove(firstExternalNode)
    
    for i in range(len(groupNodes) - 1 ):
        groupNodes[i]['next'] = i + 1
        
    firstExternalNode['next'] = 0
    groupNodes.append(firstExternalNode)
        
    while len(groupNodes) != 12:
        groupNodes.append(getIgnoredNode())
    
    return groupNodes
    
    
def exportVehiclePaths(filepath, ob, bIsWater):
    print("Exporting to: " + filepath)
    print("Exporting Object: " + ob.name)
    file = open(filepath, 'w')
    file.write("path\n")
    me = ob.data
    
    # Get Bmesh representation
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    
    tagVerts = []
    tagEdges = []
    for i in range(len(bm.verts)):
        tagVerts.append({})
        tagVerts[i]['read'] = False
        tagVerts[i]['type'] = "none" #center, connectedsegmentStart, connectedsegmentEnd, connectedsegmentMiddle
        
    for i in range(len(bm.edges)):
        tagEdges.append({})
        tagEdges[i]['split'] = False
        
    NumGroup = 0
        
        
    
    # find all junctions and single linked connections first
    for v in bm.verts:
        if tagVerts[v.index]['type'] == "center":
            continue
            
        assert len(v.link_edges) > 0
        
        # skip all lines
        if len(v.link_edges) == 2:
            continue
        
        tagVerts[v.index]['type'] = "center"
        
        
        lineSegments = []
        
        junctionOrSingleCenter = {}
        junctionOrSingleCenter['realIndex'] = v.index
        junctionOrSingleCenter['xyz'] = v.co
        
        groupNodes = []
        groupNodes.append(junctionOrSingleCenter)
        
        for link in v.link_edges:
            linkVert = link.other_vert(v).index
                
            # if link is part of a line, mark it as external node and not part of 2 lines nodes saga (extra added external nodes)
            if len(bm.verts[linkVert].link_edges) == 2 and tagEdges[link.index]['split'] == False:  
                assert tagVerts[linkVert]['type'] != "connectedsegmentStart"
                lineSegments.append(linkVert)
                
                extNode = {}
                extNode['xyz'] = bm.verts[linkVert].co
                extNode['realIndex'] = linkVert

                groupNodes.append(extNode)
            else:
                # this could be another junction or single linked node
                # in this case, get the middle point as external Node
                extNode = {}
                extNode['xyz'] = (bm.verts[linkVert].co + bm.verts[v.index].co)/2
                extNode['realIndex'] = linkVert
                
                groupNodes.append(extNode)
         
        # Now write the junction or singly linked connection
        PrepareCentreJunctionOrSingleConnectionGroup(bm, groupNodes, tagVerts)
        file.write(str(2 if bIsWater else 1) + ", -1\n")
        for node in groupNodes:
            file.write( "\t{}, {}, {}, {:.2f}, {:.2f}, {:.2f}, {}, {}, {}, {}, {}, {}\n".format(
                node['type'], 
                node['next'], 
                0,
                node['xyz'].x * 16,
                node['xyz'].y * 16,
                node['xyz'].z * 16,
                node['median'],
                node['leftLanes'],
                node['rightLanes'],
                node['speedlimit'],
                node['flags'],
                node['spawnrate']
                )
            )
        
        # now start exporting all the line segments for that junction/single connection
        while len(lineSegments) > 0:
            lineStart = lineSegments.pop()
            
            # check if line was already traversed
            if tagVerts[lineStart]['type'] == "connectedsegmentStart" or tagVerts[lineStart]['type'] == "connectedsegmentEnd":
                continue
            
            # keep on adding until a junction or singly connection has been reached
            lineNodes = []
            
            prevNode = v.index
            currentNode = lineStart
            
            while True:
                if len(bm.verts[currentNode].link_edges) != 2:
                    break
                else:
                    lineNodes.append(currentNode)
                    
                    # Also mark the nodes as middle point of connected segment
                    tagVerts[currentNode]['type'] = "connectedsegmentMiddle"
                    
                nextVert = bm.verts[currentNode].link_edges[0].other_vert(bm.verts[currentNode]).index
                if nextVert == prevNode:
                    nextVert = bm.verts[currentNode].link_edges[1].other_vert(bm.verts[currentNode]).index
                
                prevNode = currentNode
                currentNode = nextVert
            
            # discard only one vertex line (in between 2 junctions or singlely linked)
            if len(lineNodes) == 1:
                continue
                
            #print ("line:", lineNodes)
            assert len(lineNodes) >= 2
            
            # mark first and last as external
            tagVerts[lineNodes[0]]['type'] = "connectedsegmentStart"
            tagVerts[lineNodes[ len(lineNodes) -1 ]]['type'] = "connectedsegmentEnd"
            
            # Insert an external node if only 2 nodes in a line because one has to be internal
            if len(lineNodes) == 2:
                print ("line:", lineNodes)
                groupNodes = []
                
                internalNode = {}
                internalNode['realIndex'] = lineNodes[1]
                internalNode['xyz'] = bm.verts[lineNodes[1]].co
                groupNodes.append(internalNode)
                
                externalNode = {}
                externalNode['realIndex'] = lineNodes[0]
                externalNode['xyz'] = bm.verts[lineNodes[0]].co
                groupNodes.append(externalNode)
                
                nextVert = bm.verts[lineNodes[1]].link_edges[0].other_vert(bm.verts[lineNodes[1]]).index
                if nextVert == lineNodes[0]:
                    nextVert = bm.verts[lineNodes[1]].link_edges[1].other_vert(bm.verts[lineNodes[1]]).index
                
                externalNode2 = {}
                externalNode2['realIndex'] = nextVert
                externalNode2['xyz'] = (bm.verts[lineNodes[1]].co + bm.verts[nextVert].co)/2.0
                groupNodes.append(externalNode2)
                
                bm_edge = bm.edges.get(( bm.verts[ lineNodes[1] ], bm.verts[ nextVert ] ))
                tagEdges[bm_edge.index]['split'] = True
                
                # Now write the junction or singly linked connection
                PrepareCentreJunctionOrSingleConnectionGroup(bm, groupNodes, tagVerts)
                file.write(str(2 if bIsWater else 1) + ", -1\n")
                for node in groupNodes:
                    file.write( "\t{}, {}, {}, {:.2f}, {:.2f}, {:.2f}, {}, {}, {}, {}, {}, {}\n".format(
                        node['type'], 
                        node['next'], 
                        0,
                        node['xyz'].x * 16,
                        node['xyz'].y * 16,
                        node['xyz'].z * 16,
                        node['median'],
                        node['leftLanes'],
                        node['rightLanes'],
                        node['speedlimit'],
                        node['flags'],
                        node['spawnrate']
                        )
                    )
                continue
            
            assert len(lineNodes) == len(set(lineNodes))
            
            lineGroups = []
            
            # start break down into group segments and write to the file
            tempGroupNodes = []
            for i in range(len(lineNodes)):         
                node = lineNodes[i]
                
                tempGroupNodes.append(node) 
                if len(tempGroupNodes) == 12:
                    lineGroups.append(tempGroupNodes.copy())
                    tempGroupNodes.clear()
                    tempGroupNodes.append(node)
            
            if len(tempGroupNodes) > 1:
                lineGroups.append(tempGroupNodes)
                
            lastGroup = lineGroups[len(lineGroups) -1]
            
            # fix the node count on last group
            if len(lastGroup) == 2:
                assert len(lineGroups) >= 2
                secondlastGroup = lineGroups[len(lineGroups) - 2]
                secondlastGroup.pop() # discard the external node
                
                newExternal = secondlastGroup[len(secondlastGroup) - 1]
                lastGroup.insert(0, newExternal)
            
            # remove the one linered
            for lineG in lineGroups:
                assert len(lineG) != 1
                
                groupNodes = PrepareVehicleLineSegmentsGroup(bm, lineG)
                
                file.write(str(2 if bIsWater else 1) + ", -1\n")
                for node in groupNodes:
                    file.write( "\t{}, {}, {}, {:.2f}, {:.2f}, {:.2f}, {}, {}, {}, {}, {}, {}\n".format(
                        node['type'], 
                        node['next'], 
                        0,
                        node['xyz'].x * 16,
                        node['xyz'].y * 16,
                        node['xyz'].z * 16,
                        node['median'],
                        node['leftLanes'],
                        node['rightLanes'],
                        node['speedlimit'],
                        node['flags'],
                        node['spawnrate']
                        )
                    )
                
            #TESTCODE
            #END TEST CODE
            
        
        #TEST CODE
        #END TEST 
                    
    bm.to_mesh(me)
    bm.free()
    file.write("end\n")
    file.close()
