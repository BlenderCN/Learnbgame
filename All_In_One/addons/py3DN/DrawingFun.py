# Author: Paulo de Castro Aguiar	
# Date: July 2012
# email: pauloaguiar@fc.up.pt

"""Blender drawing functions"""

import numpy
import sys
import time

import bpy
from mathutils import *

import DataContainers
import DrawingXtras

import myconfig
import GUI


pi = 3.14159265359


# LIST OF FUNCTIONS
# -----------------
# *mesh calculation functions*
# Draw_Objects
# Draw_MorphStruct_Mesh
# Draw_Tree_Varicosities
# Draw_Tree_Spines
# Draw_Tree_Mesh

# *support functions*
# Draw_Xtras
# Get_NPoly_Vertices
# PointID2VertID
# Get_Minimal_Twist
# Color_Hex2RGB



#------------------------------------------------------------------------------------------



def Draw_Xtras( neuron ):
    """Use this function to automatically call visualization/analysis functions coupled with the draw button"""

    #DrawingXtras.Draw_Varicosity_Density_Voxels( neuron.tree[0], 40, 10, 10)        

    return


#------------------------------------------------------------------------------------------



def Draw_Objects( neuron, morphology ):
    """Gateway to draw all neuron\morphology structures in the mighty Blender"""

    print( ' ' )
    print( 'Drawing neuron ' + neuron.label )
    bpy.context.scene['MyDrawTools_Status'] = 'drawing structures... (check console!)'


    # Usage of Layers:
    # ----------------
    # soma/cellbody contours : base_layer + 0
    # trees                  : base_layer + 1
    # varicosities           : base_layer + 2
    # spines                 : base_layer + 3
    # other contours         : base_layer + 4


    # Go through all CONTOURS
    # -----------------------
    if bpy.context.scene.MyDrawTools_ContoursDraw == True:

        print( 'Drawing contours' )
        t0 = time.clock()
        
        for s in range( 0, morphology.total_structures ):

            morph_struct = morphology.structure[s]
            name = morph_struct.name
            print( '\t- taking care of contours named: ' + name )

            # set layer
            if name == 'Cell Body' or name == 'CellBody' or morph_struct.name == 'Soma Contour' :
                layer = bpy.context.scene.MyDrawTools_BaseLayer % 20
            else :
                layer = ( bpy.context.scene.MyDrawTools_BaseLayer + 4 ) % 20
            # draw
            Draw_MorphStruct_Mesh( morph_struct, layer )
        
        print( '{0:.2f} seconds processing time'.format( time.clock() - t0 ) )
    

    # Go through all TREES
    # --------------------
    for tid in range( neuron.total_trees ):   
 
        # Draw the tree mesh
        # ------------------
        if bpy.context.scene.MyDrawTools_TreesDraw == True:
            print( 'Drawing ' + str(neuron.tree[tid].type) + ', ' + str(tid) )
            t0 = time.clock()
            # set layer
            layer = ( bpy.context.scene.MyDrawTools_BaseLayer + 1 ) % 20
            # draw
            Draw_Tree_Mesh( neuron, tid, [], layer )       
            print( '{0:.2f} seconds processing time'.format( time.clock() - t0 ) )
    
        # Deal with VARICOSITIES
        # ----------------------
        if bpy.context.scene.MyDrawTools_VaricosDraw == True:
            print( 'Drawing ' + str(neuron.tree[tid].total_varicosities) + ' varicosities for ' + str(neuron.tree[tid].type) + ', ' + str(tid) )
            t0 = time.clock()
            # set layer
            layer = ( bpy.context.scene.MyDrawTools_BaseLayer + 2 ) % 20
            # draw
            Draw_Tree_Varicosities( neuron.tree[tid], layer )
            print( '{0:.2f} seconds processing time'.format( time.clock() - t0 ) )    
    
        # Deal with SPINES
        # ----------------
        if bpy.context.scene.MyDrawTools_SpinesDraw == True:
            print( 'Drawing ' + str(neuron.tree[tid].total_spines) + ' spines for ' + str(neuron.tree[tid].type) + ', ' + str(tid) )
            t0 = time.clock()
            # set layer
            layer = ( bpy.context.scene.MyDrawTools_BaseLayer + 3 ) % 20
            # draw
            Draw_Tree_Spines( neuron.tree[tid], layer )
            print( '{0:.2f} seconds processing time'.format( time.clock() - t0 ) )    



    ##############################################################################################

    # EXTRA STUFF!!!

    Draw_Xtras( neuron )

    ##############################################################################################


    bpy.context.scene['MyDrawTools_Status'] = 'drawing complete!'

    return



#------------------------------------------------------------------------------------------



def Draw_MorphStruct_Mesh( morph_struct, layer ):
    """Calculates and draws a 3D mesh for a specific morphology structure"""
    # IMPORTANT: This function assumes that all countours are CLOSED CONVEX POLYGONS
    # It is also assumed that all contours appear in the xml in their spatial order: in Z-order!

    if morph_struct.total_contours == 0 :
        return

    # number of points in each contour
    N = morph_struct.contour[0].total_points

    # put in Z order
    listofzis = [0.0]*morph_struct.total_contours
    for cid in range( 0, morph_struct.total_contours ) :
        listofzis[cid] = morph_struct.contour[cid].centroid[2]
    listofzis = numpy.array( listofzis )
    sortedzis = listofzis.argsort()


    # containers for 3D data
    verts = [] # all mesh vertices will be held here... ohh yeah!
    faces = [] # all mesh surfaces will be held here... ohh yeah x 2!
    edges = [] # all mesh surfaces will be held here... ohh yeah x 2!


    # start by adding the centroid of the first contour
    cid = sortedzis[0]
    centroid = morph_struct.contour[cid].centroid
    verts.append( centroid )
    # now add all points from the contours
    for i in range( 0, morph_struct.total_contours ) :
        cid = sortedzis[i]
        verts.extend( morph_struct.contour[cid].point )
    # finish it with the centroid of the last contour
    cid = sortedzis[-1]
    verts.append( morph_struct.contour[cid].centroid )

    # vertices Done! now lets take care of the faces
    # 1 - start with bottom
    c = 0    
    for pid in range( 0, N ) :
        a = 1 +   pid   % N
        b = 1 + (pid+1) % N
        faces.append( [a, b, c] )

    # 2 - now go through all contours and knit them together in pairs
    for i in range( 0, morph_struct.total_contours - 1) :
        cid    = sortedzis[i]
        cidnxt = sortedzis[i+1]        
        PA     = morph_struct.contour[cid].centroid
        PB     = morph_struct.contour[cidnxt].centroid
        vertA  = morph_struct.contour[cid].point[0]
        vertsB = morph_struct.contour[cidnxt].point
        offset =  Get_Minimal_Twist( PA, PB, vertA, vertsB, N )
        # now knit the spider web (love this mental imagery)
        for pid in range( 0, N ) :            
            a = pid              +   i   * N + 1
            b = (pid+1)%N        +   i   * N + 1
            c = (pid+offset+1)%N + (i+1) * N + 1
            d = (pid+offset)%N   + (i+1) * N + 1
            faces.append( [a, b, c, d] )
            edges.append( [a, b] ) # also store the edges
        edges.append( [N*(i+1), N*i+1] ) # complete with the last edge to close the contour

    # 3 - finish with the top
    c = N * morph_struct.total_contours + 2 - 1
    for pid in range( 0, N ) :
        a = c - 1 -   pid   % N
        b = c - 1 - (pid-1) % N
        faces.append( [a, b, c] )          



    # All done - now Draw!
    # --------------------
    # create mesh and object
    name = morph_struct.name
    mesh = bpy.data.meshes.new( name + '_Mesh' )
    obj  = bpy.data.objects.new( name, mesh )
    bpy.context.scene.objects.link( obj )

    if morph_struct.name == 'Cell Body' or morph_struct.name == 'CellBody' or morph_struct.name == 'Soma Contour' :
        # WOULD BE NICIER IF APPLIED TO ALL BUT MANY CONTOURS ARE HIGHLY IRREGULAR AND THE RESULT LOOKS BAD
        mesh.from_pydata(verts, [], faces)
        mesh.update( calc_edges = True )
    else :
        #mesh.from_pydata(verts, [], faces)
        #mesh.update( calc_edges = True )
        # USE THE EDGES METHOD
        mesh.from_pydata(verts, edges, [])

    # apply material
    mat = bpy.data.materials.new( name + '_Mat')
    mat.diffuse_color = Color_Hex2RGB( morph_struct.color )
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = [0.0, 0.0, 0.0]
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 1.0
    mat.alpha = 1.0
    mat.ambient = 1.0
    obj.data.materials.append(mat)


    layers = [False]*20
    layers[ layer % 20 ] = True
    obj.layers = layers


    return
    


#------------------------------------------------------------------------------------------



def Draw_Tree_Varicosities( tree, layer ):
    """Calculates and draws a 3D mesh for a specific tree structure"""

    # check first if there are varicosities in this tree
    if tree.total_varicosities == 0 :
        return

    # geometry repository
    verts = []
    faces = []

    # create material to be applied to all varicosities
    name = 'Varicos'
    mat = bpy.data.materials.new( name + '_Mat')
    mat.diffuse_color = [0.0, 0.0, 1.0]
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = [0.0, 0.0, 0.0]
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 1.0
    mat.alpha = 1.0
    mat.ambient = 1.0

    N = bpy.context.scene.MyDrawTools_VaricosDetail
    ez = Vector( [0.0, 0.0, 1.0] )

    for v in range( 0, tree.total_varicosities):

        varico = tree.varicosity[v]

        if bpy.context.scene.MyDrawTools_VaricosForceDiam == True :
            r = 0.5 * bpy.context.scene.MyDrawTools_VaricosDiam
        else:
            r = varico.r

        P0 = Vector( varico.P )

        # create cross-section and add two vertices, bottom and top
        cross_section = Get_NPoly_Vertices( r, N ) 
        verts.extend( cross_section ) # middle section
        verts.append( -r*ez + P0 ) # add bottom vertice
        verts.append( +r*ez + P0 ) # add top vertice

        # do not rotate; just translate (top and bottom vertices are already translated)
        # set all faces in the double cone
        for i in range( 0, N ):   # go through all vertices in the NPolys
            M = (N+2)*v
            verts[M+i] = Vector(verts[M+i]) + P0
            faces.append( [ M+N   , M+i, M+(i+1)%N ] ) # lower faces
            faces.append( [ M+N+1 , M+i, M+(i+1)%N ] ) # upper faces

    # draw
    mesh = bpy.data.meshes.new( name + '_Mesh' )
    obj  = bpy.data.objects.new( name, mesh )
    bpy.context.scene.objects.link( obj )
    mesh.from_pydata( verts, [], faces)
    mesh.update( calc_edges = True )

    # apply material
    obj.data.materials.append(mat)        

    # set layers
    layers = [False]*20
    layers[ layer % 20 ] = True
    obj.layers = layers


    return



#------------------------------------------------------------------------------------------

    

def Draw_Tree_Spines( tree, layer ):
    """Calculates and draws a 3D mesh for the spines in a specific tree structure"""

    # geometry repository
    verts = []
    faces = []

    # create material to be applied to all spines
    name = 'Spines'
    mat = bpy.data.materials.new( name + '_Mat')
    mat.diffuse_color = [0.0, 1.0, 0.0]
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = [0.0, 0.0, 0.0]
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 1.0
    mat.alpha = 1.0
    mat.ambient = 1.0

    N = bpy.context.scene.MyDrawTools_SpinesDetail

    ez = Vector([0,0,1])

    for s in range( 0, tree.total_spines):

        local_verts = []

        spine = tree.spine[s]

        if bpy.context.scene.MyDrawTools_SpinesForceDiam == True :
            r = 0.5 * bpy.context.scene.MyDrawTools_SpinesDiam
        else :
            r = spine.r

        cross_section = Get_NPoly_Vertices( r, N ) 
        local_verts.extend( cross_section ) # bottom section
        local_verts.extend( cross_section ) #  top   section

        # rotate and translate both cross-sections

        P0 = Vector( spine.P )
        P1 = Vector( spine.Q )
                    
        n = P1 - P0
        # stupid way to catch null normal vectors that arise from double raw points
        if n.dot(n) < 0.001 : # in units of um
            n = ez
        else :
            n.normalize()
        ang = n.angle(ez)

        if numpy.fabs(ang) > 0.05: # only perform cross product if n and ez are not colinear; angle is in radians!
            rotaxis = -n.cross(ez)
            rotmat = Matrix.Rotation(ang, 3, rotaxis)
            for i in range( 0, N ):   # go through all vertices in the NPolys
                local_verts[i]   = rotmat * Vector(local_verts[i]  ) + P0
                local_verts[i+N] = rotmat * Vector(local_verts[i+N]) + P1
                L = (Vector(local_verts[i]) - Vector(local_verts[i+N])).length

        else:
            for i in range( 0, N ):   # go through all vertices in the NPolys
                local_verts[i]   = Vector(local_verts[i]  ) + P0
                local_verts[i+N] = Vector(local_verts[i+N]) + P1

        # knit mesh surfaces
        local_faces = []
        secA_vert  = local_verts[0]
        secB_local_verts = local_verts[N:2*N]              
        offset = Get_Minimal_Twist( spine.P, spine.Q, secA_vert, secB_local_verts, N) # same stupid way to avoid twists

        for j in range( 0, N ): # go through all points in the NPoly
            a = PointID2VertID( 0, j%N           , N)
            b = PointID2VertID( 0, (j+1)%N       , N)
            c = PointID2VertID( 1, (j+1+offset)%N, N)
            d = PointID2VertID( 1, (j+offset)%N  , N)            
            local_faces.append( [a+2*N*s, b+2*N*s, c+2*N*s, d+2*N*s] )

        verts.extend( local_verts )
        faces.extend( local_faces )


    # draw
    mesh = bpy.data.meshes.new( name + '_Mesh' )
    obj  = bpy.data.objects.new( name, mesh )
    bpy.context.scene.objects.link( obj )
    mesh.from_pydata( verts, [], faces)
    mesh.update( calc_edges = True )

    # apply material
    obj.data.materials.append(mat)        

    # set layers
    layers = [False]*20
    layers[ layer % 20 ] = True
    obj.layers = layers


    return


#------------------------------------------------------------------------------------------



def Draw_Tree_Mesh(neuron, tid, colorcodes, layer ):
    """Calculates and draws a 3D mesh for a specific tree structure"""
    # This function has many cycles... it could surely be optimized

    tree = neuron.tree[tid]

    N = bpy.context.scene.MyDrawTools_TreesDetail

    # STEP 1 - create all mesh vertices
    # ---------------------------------
    # all tree mesh vertices will be held here... ohh yeah!
    tree_verts = []
    for pid in range( 0, tree.total_points):        
        tree_verts.extend( Get_NPoly_Vertices( tree.point[pid].r, N) )        
    

    # STEP 2 - rotate and translate all cross-sections
    # ------------------------------------------------
    # At this state all cross-sections are in centered in (0,0,0) and have n=(0,0,1)

    ex = Vector([1,0,0])
    ey = Vector([0,1,0])
    ez = Vector([0,0,1])

    for pid in range( 0, tree.total_points):
        n = Vector( tree.point[pid].n )        
        # not very smart way to catch null normal vectors that arise from successive equal raw points
        if n.length < 0.001: # units in um
            n = Vector( tree.point[ tree.point[pid].ppid ].n )
            print('\n\nWARNING: problem with 0 length normal in point ' + str(pid) + ' in tree ' + str(tid) + '; may be originated by duplicated consecutive raw points; correct manually or consider applying minimal distance point removal')

        ang = ez.angle(n) #blender angle is in radians!

        # this correction of the torcion should be improved...:
        # at this stage it will rely on Get_Minimal_Twist() function (applyed when defining the mesh faces)
        if ang > pi/2.0 / 100.0: # only perform cross product if n and u are not colinear;
            rotaxis = ez.cross(n)
            rotmat = Matrix.Rotation( ang, 3, rotaxis )
            #torcion = RotationMatrix(-angtor, 3, 'r' , n)
            for i in range( 0, N ): # go through all vertices in the NPoly
                #tree_verts[ i + N * pid ] = torcion * rotmat * Vector(tree_verts[i + N * pid ]) + tree.point[pid].P
                tree_verts[ i + N * pid ] = rotmat * Vector(tree_verts[i + N * pid ]) + Vector( tree.point[pid].P )
        else:
            for i in range( 0, N ): # go through all vertices in the NPoly
                tree_verts[ i + N * pid ] = Vector(tree_verts[i + N * pid ]) + Vector( tree.point[pid].P )


    # STEP 3 - setup all mesh surfaces
    # ----------------------------------------------------
    tree_faces = []
    for pid in range( 1, tree.total_points):
        
        ppid = tree.point[pid].ppid
  
        # slow way to avoid twists - not proud of it... :( [something beter should be done at the rotation matrix]
        secA_vert  = tree_verts[ ppid * N]
        secB_verts = tree_verts[ pid  * N: (pid + 1) * N]              
        offset = Get_Minimal_Twist( tree.point[ppid].P, tree.point[pid].P, secA_vert, secB_verts, N)

        for j in range( 0, N ): # go through all points in the NPoly
            a = PointID2VertID( ppid, j%N           , N)
            b = PointID2VertID( ppid, (j+1)%N       , N)
            c = PointID2VertID( pid , (j+1+offset)%N, N)
            d = PointID2VertID( pid , (j+offset)%N  , N)            
            tree_faces.append( [a, b, c, d] )



    # STEP 3.1 - Attach to Cellbody
    # ----------------------------------------------------
    if bpy.context.scene['MyDrawTools_TreeSomaAttach'] == True :
        if bpy.context.scene.MyDrawTools_ContoursDraw == True and ( tree.type != 'Axon' or tree.type != 'axon' ) :
            if neuron.cellbody != [] :
                if neuron.cellbody.total_contours > 0 :
                    # finally...
                    mc = int( 0.5 * neuron.cellbody.total_contours )
                    tree_verts.append( neuron.cellbody.rawcontour[mc].centroid )
                    # connect first section with centroid
                    last_vert = len(tree_verts) - 1        
                    for j in range( 0, N ): 
                        tree_faces.append( [last_vert, j%N, (j+1)%N] )



    # STEP 4 - Draw
    # ----------------------------------------------------
    if colorcodes == [] :
        name = tree.type
    else :
        name = 'DelayMap'
    mesh = bpy.data.meshes.new( name + '_Mesh' )
    obj  = bpy.data.objects.new( name, mesh )
    bpy.context.scene.objects.link( obj )
    mesh.from_pydata( tree_verts, [], tree_faces)
    mesh.update( calc_edges = True )

    # apply material    
    mat = bpy.data.materials.new( name + '_Mat')
    if colorcodes == [] :
        mat.diffuse_color = Color_Hex2RGB( tree.color )
    else :
        mat.diffuse_color = [0.0, 0.0, 0.0]
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = [0.0, 0.0, 0.0]
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 1.0
    mat.alpha = 1.0
    mat.ambient = 1.0
    obj.data.materials.append(mat)

    # perform vertex paint if requested
    if colorcodes == [] :
        l = 1
    else :
        l = 5
        mat.use_vertex_color_paint = True
        bpy.ops.object.select_by_layer(layers = -1)
        obj.select = True
        bpy.ops.mesh.vertex_color_add()
        for pid in range( 0, tree.total_points) :
            for i in range( 0, N):
                bpy.data.objects[name].data.vertex_colors[0].data[pid*N+i].color1 = colorcodes[pid]
                bpy.data.objects[name].data.vertex_colors[0].data[pid*N+i].color2 = colorcodes[pid]
                bpy.data.objects[name].data.vertex_colors[0].data[pid*N+i].color3 = colorcodes[pid]
                bpy.data.objects[name].data.vertex_colors[0].data[pid*N+i].color4 = colorcodes[pid]


    # set layers
    layers = [False]*20
    layers[ layer % 20 ] = True
    obj.layers = layers


    return



#------------------------------------------------------------------------------------------



def Get_NPoly_Vertices(r, N):
    """Returns a NPoly approximating a circle with radius r"""
  
    vertices = []
    for i in range(0,N):
        theta = 2.0 * i/N * numpy.pi
        vertices.append( [ r * numpy.cos(theta), r * numpy.sin(theta), 0 ] )

    return vertices



#------------------------------------------------------------------------------------------



def PointID2VertID( point_number, n, N):
    """Convert a point index to a vertice index"""

    return point_number * N + n



#------------------------------------------------------------------------------------------



def Get_Minimal_Twist( PA, PB, vertA, vertsB, N ) :
    """Calculates the pairwise sellection of vertices which minimizes mesh twist"""

    VPA = Vector( PA ) 
    VPB = Vector( PB ) 

    # get reference vector
    vA = Vector( vertA ) - VPA
    vA.normalize()

    # get candidate target
    vB = Vector( vertsB[0] ) - VPB
    vB.normalize()

    # initial conditions
    max_dot = vA.dot( vB )  
    best_id = 0;

    rising = False

    # check which vertice in surface B should be connected to vertice 
    for i in range(1,N):

        # get new candidate
        vB = Vector( vertsB[i] ) - VPB
        vB.normalize()

        new_max_dot = vA.dot( vB ) 

        if new_max_dot > max_dot :
            max_dot = new_max_dot
            best_id = i
            rising = True
        else: 
            if rising == True:
                break            # don't waist more time as the maximum has been found
            rising = False
            
    # shame on me... should be at the rotation matrix ...
    return best_id   



#------------------------------------------------------------------------------------------



def Color_Hex2RGB( c ):
    """Converts a color Hex code to a RGB format"""

    # color c if a string of the type '#FFFFFF'
    split = (c[1:3], c[3:5], c[5:7])

    foo = [int(x, 16) for x in split]

    return numpy.array( foo ) / 255



#------------------------------------------------------------------------------------------
