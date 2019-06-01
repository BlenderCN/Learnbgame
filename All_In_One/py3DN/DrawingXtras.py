# Author: Paulo de Castro Aguiar	
# Date: Apr 2013
# email: pauloaguiar@fc.up.pt

"""Blender Xtra drawing functions"""

import numpy
import sys
import time

import bpy
from mathutils import *

import DataContainers
import DrawingFun
from InterpolateFun import Normalize_Vector

import myconfig
import GUI


OPS_LAYER = 0


# LIST OF FUNCTIONS
# -----------------
# *morphometric functions with spatial dependence*
# Draw_Varicosity_Density_Voxels
# Draw_Varicosity_Density_Voxels_L
# Draw_Tree_Delay_Map
# Analyse_VaricositySpine_Match

# *functions providing visualization support*
# Draw_CellBody_Box
# Blow_Contour_Balloon
# Draw_User_Mesh
# Draw_Tree_CrossSection_Normals
# Draw_RawTree_Skeleton

# *geometric transformation functions*
# Transform_Neuron
# Transform_Point
# Transform_Point_RotMat




#------------------------------------------------------------------------------------------



def Draw_Varicosity_Density_Voxels(axon, bins_X, bins_Y, bins_Z):
    """Function to calculate the spatial distribution of varicosities density"""

    # to make things more readable
    X = 0
    Y = 1
    Z = 2

    # get border box

    min_P = list( axon.rawpoint[0].P )
    max_P = list( axon.rawpoint[0].P )
    for p in range(1, axon.total_rawpoints):
        for i in range(0, 3):
            if axon.rawpoint[p].P[i] < min_P[i]:
                min_P[i] = axon.rawpoint[p].P[i]
            if axon.rawpoint[p].P[i] > max_P[i]:
                max_P[i] = axon.rawpoint[p].P[i]
    LX = ( max_P[X] - min_P[X] ) / bins_X
    LY = ( max_P[Y] - min_P[Y] ) / bins_Y
    LZ = ( max_P[Z] - min_P[Z] ) / bins_Z

    # create voxels array
    varico = axon.varicosity
    voxels = numpy.zeros([bins_X, bins_Y, bins_Z], float)
    for v in range(0, axon.total_varicosities):
        i = numpy.int( (varico[v].P[X] - min_P[X]) / LX )
        j = numpy.int( (varico[v].P[Y] - min_P[Y]) / LY )
        k = numpy.int( (varico[v].P[Z] - min_P[Z]) / LZ )
        # catch the (max-min)/bins situation
        if i == bins_X:
            i = bins_X - 1
        if j == bins_Y:
            j = bins_Y - 1
        if k == bins_Z:
            k = bins_Z - 1
        voxels[i][j][k] = voxels[i][j][k] + 1

    #print( str(voxels) )
    norm = 1.0/numpy.max(voxels)

    # draw all voxels
    for i in range(0, bins_X):
        for j in range(0, bins_Y):
            for k in range(0, bins_Z):

                v = voxels[i][j][k]
                if v > 0:

                    min_X = min_P[X] + i * LX
                    min_Y = min_P[Y] + j * LY
                    min_Z = min_P[Z] + k * LZ
                    max_X = min_X + LX
                    max_Y = min_Y + LY
                    max_Z = min_Z + LZ
                    
                    voxel_verts = [ [min_X, min_Y, min_Z], [max_X, min_Y, min_Z], [min_X, max_Y, min_Z], [max_X, max_Y, min_Z], [min_X, min_Y, max_Z], [max_X, min_Y, max_Z], [min_X, max_Y, max_Z], [max_X, max_Y, max_Z] ]
                    voxel_faces = [ [0,1,3,2], [4,5,7,6], [0,1,5,4], [1,3,7,5], [3,2,6,7], [2,0,4,6] ]

                    # Draw
                    # ----------------------------------------------------
                    name = 'vox'
                    mesh = bpy.data.meshes.new( name + '_Mesh' )
                    obj  = bpy.data.objects.new( name, mesh )
                    bpy.context.scene.objects.link( obj )
                    mesh.from_pydata( voxel_verts, [], voxel_faces)
                    mesh.update( calc_edges = True )
                    # apply material
                    mat = bpy.data.materials.new( name + '_Mat')
                    mat.diffuse_color = [v * norm, 0.0, 0.0]
                    mat.diffuse_shader = 'LAMBERT'
                    mat.diffuse_intensity = 1.0
                    mat.specular_color = [0.0, 0.0, 0.0]
                    mat.specular_shader = 'COOKTORR'
                    mat.specular_intensity = 1.0
                    mat.alpha = v * norm * 0.5
                    mat.ambient = 1.0
                    #mat.transparency_method = 'Z_TRANSPARENCY'
                    obj.data.materials.append(mat)

                    # set layers
                    layers = [False]*20
                    layers[ (bpy.context.scene['MyDrawTools_BaseLayer'] + OPS_LAYER ) % 20 ] = True
                    obj.layers = layers
                 
    return


#------------------------------------------------------------------------------------------



def Draw_Varicosity_Density_Voxels_L(axon, L_X, L_Y, L_Z):
    """Function to calculate the spatial distribution of varicosities density. Distances are in um"""

    # to make things more readable
    X = 0
    Y = 1
    Z = 2

    # get border box

    min_P = list( axon.rawpoint[0].P )
    max_P = list( axon.rawpoint[0].P )
    for p in range(1, axon.total_rawpoints):
        for i in range(0, 3):
            if axon.rawpoint[p].P[i] < min_P[i]:
                min_P[i] = axon.rawpoint[p].P[i]
            if axon.rawpoint[p].P[i] > max_P[i]:
                max_P[i] = axon.rawpoint[p].P[i]

    bins_X = int( ( max_P[X] - min_P[X] ) / L_X ) + 1
    bins_Y = int( ( max_P[Y] - min_P[Y] ) / L_Y ) + 1
    bins_Z = int( ( max_P[Z] - min_P[Z] ) / L_Z ) + 1

    # create voxels array
    varico = axon.varicosity
    voxels = numpy.zeros([bins_X, bins_Y, bins_Z], float)
    for v in range(0, axon.total_varicosities):
        i = numpy.int( (varico[v].P[X] - min_P[X]) / L_X )
        j = numpy.int( (varico[v].P[Y] - min_P[Y]) / L_Y )
        k = numpy.int( (varico[v].P[Z] - min_P[Z]) / L_Z )
        # catch the (max-min)/bins situation
        if i == bins_X:
            i = bins_X - 1
        if j == bins_Y:
            j = bins_Y - 1
        if k == bins_Z:
            k = bins_Z - 1
        voxels[i][j][k] = voxels[i][j][k] + 1

    norm = 1.0/numpy.max(voxels)

    # draw all voxels
    for i in range(0, bins_X):
        for j in range(0, bins_Y):
            for k in range(0, bins_Z):

                v = voxels[i][j][k]
                if v > 0:

                    min_X = min_P[X] + i * L_X
                    min_Y = min_P[Y] + j * L_Y
                    min_Z = min_P[Z] + k * L_Z
                    max_X = min_X + L_X
                    max_Y = min_Y + L_Y
                    max_Z = min_Z + L_Z
                    
                    voxel_verts = [ [min_X, min_Y, min_Z], [max_X, min_Y, min_Z], [min_X, max_Y, min_Z], [max_X, max_Y, min_Z], [min_X, min_Y, max_Z], [max_X, min_Y, max_Z], [min_X, max_Y, max_Z], [max_X, max_Y, max_Z] ]
                    voxel_faces = [ [0,1,3,2], [4,5,7,6], [0,1,5,4], [1,3,7,5], [3,2,6,7], [2,0,4,6] ]

                    # Draw
                    # ----------------------------------------------------
                    name = 'vox'
                    mesh = bpy.data.meshes.new( name + '_Mesh' )
                    obj  = bpy.data.objects.new( name, mesh )
                    bpy.context.scene.objects.link( obj )
                    mesh.from_pydata( voxel_verts, [], voxel_faces)
                    mesh.update( calc_edges = True )
                    # apply material
                    mat = bpy.data.materials.new( name + '_Mat')
                    mat.diffuse_color = [v * norm, 0.0, 0.0]
                    mat.diffuse_shader = 'LAMBERT'
                    mat.diffuse_intensity = 1.0
                    mat.specular_color = [0.0, 0.0, 0.0]
                    mat.specular_shader = 'COOKTORR'
                    mat.specular_intensity = 1.0
                    mat.alpha = v * norm * 0.5
                    mat.ambient = 1.0
                    #mat.transparency_method = 'Z_TRANSPARENCY'
                    obj.data.materials.append(mat)

                    # set layers
                    layers = [False]*20
                    layers[ (bpy.context.scene['MyDrawTools_BaseLayer'] + OPS_LAYER ) % 20 ] = True
                    obj.layers = layers
                 
                        
    return



#------------------------------------------------------------------------------------------



def Draw_CellBody_Box( contour ):
    """Draws a box enclosing the cellbody contour, with the minimal radius as half-height"""
    #ATTENTION!!!!! THIS IS ASSUMING THAT THE CONTOUR HAS CONSTANT Z VALUES

    X = 0 #these are definitions, to avoid using 0,1,2 in vertices index calls
    Y = 1
    Z = 2

    total_cps = contour.total_points
    cp = contour.point


    # STEP 1 - calculate the centroid, radiusoid and ranges in X and Y
    # ----------------------------------------------------------------
    centroid = Vector( [0,0,0] )
    min_X = cp[0][X]
    max_X = cp[0][X]
    min_Y = cp[0][Y]
    max_Y = cp[0][Y]

    for p in range( 0, total_cps ):	      
        centroid = centroid + Vector( [ cp[p][X], cp[p][Y], cp[p][Z] ] )
        if min_X > cp[p][X] :
            min_X = cp[p][X]
        if max_X < cp[p][X] :
            max_X = cp[p][X]
        if min_Y > cp[p][Y] :
            min_Y = cp[p][Y]
        if max_Y < cp[p][Y] :
            max_Y = cp[p][Y]

    centroid = centroid / total_cps
    radiusoid = Vector( centroid - Vector( [ cp[0][X], cp[0][Y], cp[0][Z] ] ) ).length # initialize value with a sample distance
    for p in range( 0, total_cps ):        
        dist = ( Vector( [ cp[p][X], cp[p][Y], cp[p][Z] ] ) - centroid ).length
        if dist < radiusoid :
            radiusoid = dist
    min_Z = -radiusoid + centroid[Z] 
    max_Z = radiusoid + centroid[Z]


    # STEP 2 - Set vertices and faces
    # -------------------------------

    contour_verts = [ [min_X, min_Y, min_Z], [max_X, min_Y, min_Z], [min_X, max_Y, min_Z], [max_X, max_Y, min_Z], [min_X, min_Y, max_Z], [max_X, min_Y, max_Z], [min_X, max_Y, max_Z], [max_X, max_Y, max_Z] ]
    contour_faces = [ [0,1,3,2], [4,5,7,6], [0,1,5,4], [1,3,7,5], [3,2,6,7], [2,0,4,6] ]

    # STEP 3 - Draw
    # -------------
    name = 'ContourBox'
    mesh = bpy.data.meshes.new( name + '_Mesh' )
    obj  = bpy.data.objects.new( name, mesh )
    bpy.context.scene.objects.link( obj )
    mesh.from_pydata( contour_verts, [], contour_faces)
    mesh.update( calc_edges = True )
    # apply material
    mat = bpy.data.materials.new( name + '_Mat')
    mat.diffuse_color = [0.0, 0.0, 0.0]
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = [0.0, 0.0, 0.0]
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 1.0
    mat.alpha = 1.0
    mat.ambient = 1.0
    #mat.transparency_method = 'Z_TRANSPARENCY'
    obj.data.materials.append(mat)

    # set layers
    layers = [False]*20
    layers[ (bpy.context.scene['MyDrawTools_BaseLayer'] + OPS_LAYER ) % 20 ] = True
    obj.layers = layers


    return

    

#------------------------------------------------------------------------------------------



def Draw_Tree_Delay_Map( tree, object_name, myelin_min_diam, myelin_k, unmyelin_k ):
    """Calculates the delay map for an axonal tree. Units: space in um; time in ms. Parameter k is the velocity [um/ms] in a segment with a diameter of 1 um. Parameter 'object_name' is the name in Blender of the tree object - usually 'Axon' (but you can check Blender's outliner panel). IMPORTANT - Before you run this function you must select the tree structure and select 'Vertex Paint' on the Blender 'mode' drop button allow nonhomogenous surface color."""

    # create lists to hold cumulative delays and color codes
    cumdelay   = [0.0]*tree.total_points
    cumdelay   = numpy.array( cumdelay )
    colorcodes = [[0.0, 0.0, 0.0]]*tree.total_points
    colorcodes = numpy.array( colorcodes )

    N = bpy.context.scene.MyDrawTools_TreesDetail

    # go through all points in tree (except the first)
    for pid in range( 1, tree.total_points ) :
        
        # calculate distance between this point and the previous one
        ppid = tree.point[pid].ppid
        P1 = tree.point[pid]
        P0 = tree.point[ppid]
        L = numpy.array( P1.P ) - numpy.array( P0.P )
        L = numpy.sqrt( L.dot(L) )
        
        # calculate mean diameter
        diam = 0.5 * ( P1.r + P0.r )
        
        # decide if this is a myelinated or unmyelinated segment
        if diam < myelin_min_diam :
            # unmyelinated segment
            delay = L / ( unmyelin_k * numpy.sqrt( diam ) )
        else :
            # myelinated segment
            delay = L / ( myelin_k * diam )
        
        # add this delay to the parent point delay and place it in the point id location in the cumdelay list
        cumdelay[pid] = delay + cumdelay[ppid]
    
    # get range of delays
    delay_min = cumdelay.min()
    delay_max = cumdelay.max()
    
    # build normalized delay list
    colorfactor = ( cumdelay - delay_min ) / ( delay_max - delay_min )
    
    # create color scale : goes from pure blue to pure red as the delay increases
    for pid in range( 0, tree.total_points ) :
        colorcodes[pid][0] = colorfactor[pid]
        colorcodes[pid][2] = 1.0 - colorfactor[pid]
    
    # Now create a mesh with color information for each vertice
    #DrawingFun.Draw_Tree_Mesh(neuron, tid, colorcodes )
    my_object = bpy.data.objects[object_name].data
    color_map_collection = my_object.vertex_colors
    if len(color_map_collection) == 0:
        color_map_collection.new()
    color_map = color_map_collection['Col'] #let us assume for sake of brevity that there is now a vertex color map called  'Col'
    # or you could avoid using the vertex color map name
    # color_map = color_map_collection.active
    
    for pid in range( 0, tree.total_points-1 ):
        for i in range( 0, N):
            color_map.data[pid*N+i].color = [ colorcodes[pid][0], colorcodes[pid][1], colorcodes[pid][2] ]
    mate = bpy.data.materials.new('vertex_material')
    mate.use_vertex_color_paint = True
    mate.use_vertex_color_light = True  # material affected by lights
    my_object.materials.append(mate)
    
    # set to vertex paint mode to see the result
    bpy.ops.object.mode_set(mode='VERTEX_PAINT')
    print( '\nDelay Map:\n\tpure blue is {0:.2f} ms;\n\tpure red is {1:.2f} ms;'.format( delay_min, delay_max) )
    
    
    # export delay data:
    export_file = open('varicosities_time_delays.dat', 'w')
    export_file.write( 'ONLY VALID IN THE ABSENCE OF INTERPOLATION!!! (so that rawpoints list = draw points list )\n' )
    export_file.write( 'varicosity_id cumulative_delay_[ms] pos_x_[um] pos_y_[um] pos_z_[um]\n' )
    for vid in range( 0, tree.total_varicosities-1 ):
        rawpid = tree.varicosity[vid].rawppid
        export_file.write( str(vid) + ' ' + str( cumdelay[rawpid] ) + ' ' + str( tree.point[rawpid].P[0] ) + ' ' + str( tree.point[rawpid].P[1] ) + ' ' + str( tree.point[rawpid].P[2] ) + '\n' )
    
    export_file.close()
    
    return



#------------------------------------------------------------------------------------------



def Blow_Contour_Balloon( contour, detail, neuron, tree_attraction_bool ):
    """Function which reads a 2D soma contour and produces a 3D mesh. Ex: >>> Blow_Contour_Balloon(neuron[0].cellbody.contour[0], 16, neuron[0], 1)"""

    # This function is not optimized! It is however easy to read/understand

    # IMPORTANT: This function assumes that the countour is a closed convex polygon in plane z=0!!!
    # 1 - calculate the centroid and minimum distance centroid-vertice
    # 2 - create two equal spider nets (mesh) with center in the centroid
    # 3 - inflate the two spider nets (for z>0 and z<0)
    # 4 - draw

    # cell body cross-section will have N vertices (must be multiple of 4 and >=8)
    if detail < 1.0 :
        detail = 1.0
    if detail > 64.0 :
        detail = 64.0

    N = int( detail + 0.1 ) * 4 

    X = 0 #these are definitions, to avoid using 0,1,2 in vertices index calls
    Y = 1
    Z = 2
    
    verts = [] # all tree mesh vertices will be held here... ohh yeah!
    faces = [] # all tree mesh surfaces will be held here... ohh yeah x 2!
    
    cp        = contour.point
    total_cps = contour.total_points

    # STEP 1 - calculate the centroid and radiusoid :)
    # ------------------------------------------------
    #centroid = Vector( [0,0,0] )
    #for p in range( 0, total_cps ):	      
    #    centroid = centroid + Vector( [ cp[p][X], cp[p][Y], cp[p][Z] ] )
    #centroid = centroid / total_cps
    #contour.centroid = centroid
    centroid = Vector( contour.centroid )

    # initialize value with a sample distance
    radiusoid = ( Vector([ cp[0][X], cp[0][Y], cp[0][Z] ]) - centroid ).length

    for p in range( 1, total_cps ):        
        dist = ( Vector( [ cp[p][X], cp[p][Y], cp[p][Z] ] ) - centroid ).length
        if dist < radiusoid :
            radiusoid = dist


    # STEP 2 - knit the spider web (love this mental imagery)
    # -------------------------------------------------------

    S = 2 * int( N/4.0 + 0.5) - 1   # number of stacks for contour (does not include the isolated vertices in top and bottom)

    # create interpolation rings in the spider web (stacks)
    stacks_below = []
    stacks_below.append( [ centroid[X], centroid[Y], centroid[Z] ] )
    U = int( (S-1)/2 + 1 )
    for s in range(1, U):
        alpha = numpy.pi * s / (S+1) 
        K = numpy.sin( alpha )
        ring = []
        for p in range( 0, total_cps ):
            r = Vector([ cp[p][X], cp[p][Y], cp[p][Z] ]) - centroid
            v = centroid + r * K
            ring.append( [ v[X], v[Y], v[Z] ] )
        stacks_below.extend( ring )

    
    # assemble all verts together
    verts.extend( stacks_below )  # lower sections
    verts.extend( cp )            # contour line

    stacks_above = []
    # need new list with the same values, nor references, of stacks_below; tried new=list(stacks_below) and new=stacks_below[:]; neither worked
    stacks_below_copy = []
    for s in range(len(stacks_below)):
        stacks_below_copy.append( list( stacks_below[s] ) )

    U = int( (S-1)/2 )
    for s in range(U, -1, -1):
        stacks_above.extend( stacks_below_copy[ 1 + total_cps * s : 1 + total_cps * (s+1)] )

    stacks_above.append( stacks_below_copy[0] )
    verts.extend( stacks_above )   #upper sections
   
    # fun part!: knit the web... honestly, this stuff is cool!
    TV = len(verts)
    for p in range( 0, total_cps ):     
        faces.append( [ 0   , p%total_cps+1   , (p+1)%total_cps+1    ] ) # knit bottom
        faces.append( [ TV-1, TV-2-p%total_cps, TV-2-(p+1)%total_cps ] ) # knit top
    
    for s in range(1,S): # knit the rest
        for p in range( 0, total_cps ):
            a = (s-1)*total_cps + p%total_cps+1
            b = (s-1)*total_cps + (p+1)%total_cps+1
            c = s * total_cps + (p+1)%total_cps+1
            d = s * total_cps + (p)%total_cps+1
            faces.append( [a, b, c, d] )


    # STEP 3 - inflate the cell body balloon using elipse sections; eh eh eh
    # ----------------------------------------------------------------------

    verts[0][2] = -radiusoid + centroid[Z]
    verts[-1][2] = radiusoid + centroid[Z]

    for s in range(1, S+1): # go through all stacks (top and bottom vertices already corrected above)
        alpha = numpy.pi * s / (S+1) 
        z = -radiusoid * numpy.cos( alpha )  + centroid[Z]
        for p in range( 0, total_cps ):           
            vid = (s-1)*total_cps + 1 + p
            verts[vid][2] = z


    # STEP 3.5 - Z-adjust
    # -------------------
    if tree_attraction_bool == True :

        total_verts = len( verts )
        for t in range(0, neuron.total_trees):
            x0 = neuron.tree[t].rawpoint[0].P[0] #x
            y0 = neuron.tree[t].rawpoint[0].P[1] #y
            z0 = neuron.tree[t].rawpoint[0].P[2] #z
            for v in range(0, total_verts):
                x1 = verts[v][0]
                y1 = verts[v][1]
                z1 = verts[v][2]
                d = numpy.sqrt( (x0-x1)*(x0-x1) + (y0-y1)*(y0-y1) )
                delta_z = (z0-z1) * numpy.exp( -d / radiusoid ) # notice that the space constant is set by radiusoid
                verts[v][2] += delta_z
        # re-inflate after Z-adjust
        verts[0][2] += -0.5 * radiusoid
        verts[-1][2] += 0.5 * radiusoid
        for s in range(1, S+1): # go through all stacks (top and bottom vertices already corrected above)
            alpha = numpy.pi * s / (S+1) 
            z = -radiusoid * numpy.cos( alpha )
            for p in range( 0, total_cps ):           
                vid = (s-1)*total_cps + 1 + p
                verts[vid][2] += 0.5 * z

        contour.centroid = 0.5 * ( Vector(verts[0]) + Vector(verts[total_verts-1]) ) 


    # STEP 4 - Draw
    # -------------
    # create mesh and object
    name = 'BlownContour'
    mesh = bpy.data.meshes.new( name + '_Mesh' )
    obj  = bpy.data.objects.new( name, mesh )
    bpy.context.scene.objects.link( obj )
    mesh.from_pydata(verts, [], faces)
    mesh.update( calc_edges = True )
    # apply material
    mat = bpy.data.materials.new( name + '_Mat')
    mat.diffuse_color = [ 0.0, 0.0, 1.0 ]
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = [0.0, 0.0, 0.0]
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 1.0
    mat.alpha = 1.0
    mat.ambient = 1.0
    obj.data.materials.append(mat)

    # set layers
    layers = [False]*20
    layers[ (bpy.context.scene['MyDrawTools_BaseLayer'] + OPS_LAYER ) % 20 ] = True
    obj.layers = layers

    return



#------------------------------------------------------------------------------------------



def Draw_User_Mesh( verts, faces, name='MyMesh', color=[1.0,1.0,1.0], layer=0 ):
    """Function for drawing a user-defined mesh from lists of vertices and faces. Parameters: verts, list with vertices coordinates (ex, a pyramid: [[-1,-1,-1], [1,-1,-1], [1,1,-1], [-1,1,-1], [0,0,1]]); faces, list with faces, in sets of 3 or 4 vertices ids (pyramid ex: [[3,2,1,0], [0,1,4], [1,2,4], [2,3,4], [3,0,4]]); name, string with mesh name; color, RGB list; layer, output layer for drawing"""

    # create mesh and object
    mesh = bpy.data.meshes.new( name + '_Mesh' )
    obj  = bpy.data.objects.new( name, mesh )
    bpy.context.scene.objects.link( obj )
    mesh.from_pydata(verts, [], faces)
    mesh.update( calc_edges = True )
	
    # apply material
    mat = bpy.data.materials.new( name + '_Mat')
    mat.diffuse_color = color
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = [0.0, 0.0, 0.0]
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 1.0
    mat.alpha = 1.0
    mat.ambient = 1.0
    obj.data.materials.append(mat)

    # set layers
    layers = [False]*20
    layers[ layer % 20 ] = True
    obj.layers = layers

    return


	
#------------------------------------------------------------------------------------------



def Draw_Tree_CrossSection_Normals( tree, size ):
    """Debug function which draws the cross-section normals for a specific tree"""

    verts = []
    edges = []

    for pid in range( 0, tree.total_points ) :       
        verts.append( tree.point[pid].P )
        verts.append( numpy.array(tree.point[pid].P) + size * numpy.array(tree.point[pid].n) )
        edges.append( [2*pid+0, 2*pid+1] )
        

    # Draw
    # ----
    name = 'TreeNormals'
    mesh = bpy.data.meshes.new( name + '_Mesh' )
    obj  = bpy.data.objects.new( name, mesh )
    bpy.context.scene.objects.link( obj )
    mesh.from_pydata( verts, edges, [] )
    # apply material
    mat = bpy.data.materials.new( name + '_Mat')
    mat.diffuse_color = [1.0, 0.5, 0.5]
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = [0.0, 0.0, 0.0]
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 1.0
    mat.alpha = 1.0
    mat.ambient = 1.0
    obj.data.materials.append(mat)

    # set layers
    layers = [False]*20
    layers[ (bpy.context.scene['MyDrawTools_BaseLayer'] + OPS_LAYER ) % 20 ] = True
    obj.layers = layers


    return

    

#------------------------------------------------------------------------------------------



def Draw_RawTree_Skeleton( tree, layer ):
    """Draw wireframe passing through all rawpoints - no mesh is produced."""
    """Important function for debugging strange points since it allows identification of raw points from 3D view."""

    # geometry containers
    tree_verts = []
    tree_edges = []

    # get vertices and edges
    tree_verts.append( tree.rawpoint[0].P )
    for pid in range( 1, tree.total_points):        
        tree_verts.append( tree.rawpoint[pid].P )
        tree_edges.append( [ pid, tree.rawpoint[pid].ppid ] )     

    # assemble mesh and object
    name = 'Tree_Skeleton'
    mesh = bpy.data.meshes.new( name + '_Mesh' )
    obj  = bpy.data.objects.new( name, mesh )
    bpy.context.scene.objects.link( obj )
    mesh.from_pydata( tree_verts, tree_edges, [])

    # apply material    
    mat = bpy.data.materials.new( name + '_Mat')
    mat.diffuse_color = [1.0, 0.0, 1.0]
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = [0.0, 0.0, 0.0]
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 1.0
    mat.alpha = 1.0
    mat.ambient = 1.0
    obj.data.materials.append(mat)

    # set layers
    layers = [False]*20
    layers[ layer % 20 ] = True
    obj.layers = layers

    return



#------------------------------------------------------------------------------------------



def Analyse_VaricositySpine_Match( neuron4varicosities_id, neuron4spines_id, attach_dist, max_steps, T_step, R_step, noise ):
    """Test function to estimate synaptic matching between two neurons, or more precisely, between to clouds: a spine cloud and a varicosity cloud. Neuron providing the varicosities is considered to be fixed while neuron providing spines will move (translate and rotate) in order to minimize an energy cost function (gravitation-like field)"""

    print( '\nRelax and grab a cup of coffee; dependening on the number of steps this will take a while...\n\n' )
    sys.stdout.flush()
	
    # useful constants and parameters
    deltaR = R_step   # rotation step [rad];   new variable is created to keep record of base value
    deltaT = T_step   # translation step [um]; new variable is created to keep record of base value

    # create clouds repositories
    varicos_cloud = []
    total_varicos = 0
    spines_cloud  = []
    total_spines  = 0
    spines_ids    = []

    # fill in data
    neuron4varicosities = myconfig.neuron[ neuron4varicosities_id ]
    neuron4spines       = myconfig.neuron[ neuron4spines_id ]

    # get varicosities from neuron neuron4varicosities
    for tid in range(0, neuron4varicosities.total_trees ) :
        tree = neuron4varicosities.tree[tid]
        total_varicos += tree.total_varicosities
        for vid in range(0, tree.total_varicosities ) :
            varicos_cloud.append( numpy.array( tree.varicosity[vid].P ) )

    # get spines from neuron neuron4spines
    spines_CM = numpy.array( [0.0, 0.0, 0.0] )
    for tid in range(0, neuron4spines.total_trees ) :
        tree = neuron4spines.tree[tid]
        total_spines += tree.total_spines
        for sid in range(0, tree.total_spines ) :
            spines_cloud.append(  numpy.array( tree.spine[sid].Q ) )
            spines_CM = spines_CM + numpy.array( tree.spine[sid].Q )
            spines_ids.append( [tid, sid] )
    spines_CM = spines_CM / total_spines 
    #print( 'spines cloud CM = ' + str( spines_CM ) )

    # store initial configurations of the spines cloud; orientation is provided by vector between spine0 and CM
    CM_pos_0 = spines_CM
    CM_rot_0 = Normalize_Vector( spines_cloud[0] - spines_CM ) 


    # initiate dynamics:
    # ------------------
    step = 0
    old_E = 0.0
    spines_attach = numpy.array( [0] * total_spines ) # necessary to allow code to work if max_steps = 0
    history = []

    #signal which type of step (R or T) was being used
    if deltaT > 0.1 :
        updating_R = False
        deltaT_effective = deltaT
        deltaR_effective = 0.0
    else :
        updating_R = True
        deltaT_effective = 0.0
        deltaR_effective = deltaR

    sys.stdout.flush()

    # value used for setting the force and potential when d=0 (no, I don't catch total_varicos=0)
    epsilon = 1.0# 1.0 / total_varicos

    # keep track of spines cloud
    out_SCloud = open('out_VaricositySpine_Match_SCloud.dat', 'w')
    for s in range( 0, total_spines ) :
        out_SCloud.write( '{0}\t{1}\t{2}\t'.format( spines_cloud[s][0], spines_cloud[s][1], spines_cloud[s][2] ) )
    out_SCloud.write( '\n' )

    # ----- CORE CYCLE -----------------------------------------------------------------
    while step < max_steps :

        print('\nstep =', step )

        # initializations
        spines_attach = numpy.array( [0] * total_spines )
        F_CM = numpy.array( [0.0, 0.0, 0.0] )
        F    = numpy.array( [ numpy.array( [0.0, 0.0, 0.0] ) ] * total_spines )
        T_CM = numpy.array( [0.0, 0.0, 0.0] )
        E    = numpy.array( [0.0] * total_varicos )
        weight = numpy.array( [0.0] * total_spines )

        # STEP 1 - calculate total Forces, Torques and Potential
        for s in range( 0, total_spines ) :
            # calculate total VS-Force applied on each spine
            for v in range( 0, total_varicos ) :
                n  = varicos_cloud[v] - spines_cloud[s]
                d2 = numpy.dot(n,n)
                d  = numpy.sqrt( d2 )
                F[s] += 1.0 / ( epsilon + d2 ) * n / d
                # signal which spines are withing the attach_dist radius form a varicosity
                if d < attach_dist :
                    spines_attach[s] = 1

                # calculate Potential associated with present location
                E[v] -= 1.0 / ( epsilon + d )

            # update weights
            weight[s] = numpy.sqrt( numpy.dot( F[s], F[s] ) )
            # calculate total VS-Force  applied on the spines cloud Center of Mass
            F_CM += F[s]

        # set weight vector
        weight = weight / weight.sum()

        # recalculate CM weighted by the force magnitude applied on each spine
        spines_CM = numpy.array( [0.0, 0.0, 0.0] )
        for s in range( 0, total_spines ) :
            spines_CM += weight[s] * spines_cloud[s] #uncomment two lines below if you comment this line!
            #spines_CM += spines_cloud[s] #uncomment line below if you uncomment this line!
        #spines_CM = spines_CM / total_spines 

        # calculate total VS-Torque applied on the spines cloud Center of Mass
        for s in range( 0, total_spines ) :
            r = spines_cloud[s] - spines_CM
            d = numpy.sqrt( numpy.dot(r,r) )
            if d > attach_dist : #only "disconnected" spines contribute to the torque
                T_CM += numpy.cross( r, F[s] )

        F_CM_n  = Normalize_Vector( F_CM )
        T_CM_n  = Normalize_Vector( T_CM )
        E_total = E.sum()
        total_spines_attach = spines_attach.sum()
        history.append( [ spines_CM, F_CM, T_CM, E_total, total_spines_attach ] )


        # STEP 2 - stop condition
        if numpy.fabs( (E_total - old_E) / E_total ) < 1.0e-9 :
            print( 'Stop condition reatched: Energy is not changing' )
            break


        # STEP 3 - add noise
        if noise > 0.0 :
            F_CM_n = Normalize_Vector( F_CM_n + noise * numpy.random.normal( 0.0, 1.0, 3 ) )
            T_CM_n = Normalize_Vector( T_CM_n + noise * numpy.random.normal( 0.0, 1.0, 3 ) )


        # STEP 4 - adjust step
        if E_total < old_E :
            #nice, last transformation decreased potential energy; maintain deltas
            print('deltaT and deltaR maintained; deltaT = ', deltaT, '; deltaR = ', deltaR)
        else :
            #oops, last transformation increased potential energy; reduce delta
            if updating_R == True:
                #we were rotating
                deltaR = 0.5 * deltaR
                print('deltaR adjusted: ', deltaR)
                if deltaT > 0.1 :
                    deltaT_effective = deltaT
                    deltaR_effective = 0.0
                else :
                    deltaT_effective = 0.0
                    deltaR_effective = deltaR
            else :
                #we were translating
                deltaT = 0.5 * deltaT
                print('deltaT adjusted: ', deltaT)
                if deltaR > 0.001 :
                    deltaT_effective = 0.0
                    deltaR_effective = deltaR
                else :
                    deltaT_effective = deltaT
                    deltaR_effective = 0.0


        old_E = E_total

        if deltaR_effective < 0.0001 :
            updating_R = False
        else :
            updating_R = True


        # STEP 5 - apply rotation and translation to the spines cloud
        #ATTENTION!!! critical point : be sure you're doing the right thing
        M   = numpy.array( Matrix.Rotation( deltaR_effective, 3, T_CM_n ) ) 
        w   = deltaT_effective * F_CM_n

        for s in range( 0, total_spines ) :
            spines_cloud[s] = Transform_Point_RotMat( spines_cloud[s], spines_CM, spines_CM + w, M, 1.0 )
            # dump spines cloud to a file
            out_SCloud.write( '{0}\t{1}\t{2}\t'.format( spines_cloud[s][0], spines_cloud[s][1], spines_cloud[s][2] ) )
        out_SCloud.write( '\n' )


        sys.stdout.flush()

        step += 1


    # ----- CORE CYCLE -----------------------------------------------------------------
    out_SCloud.close()
    print('\nA file with the spine cloud as a function of step number has been writen: out_VaricositySpine_Match_SCloud.dat\n')


    # mark resulting "attachments"
    spines_attach = numpy.array( [0] * total_spines )
    for s in range( 0, total_spines ) :
        for v in range( 0, total_varicos ) :
            n  = varicos_cloud[v] - spines_cloud[s]
            d2 = numpy.dot(n,n)
            d  = numpy.sqrt( d2 )
            if d < attach_dist :
                spines_attach[s] = 1
                break #I'm happy with just one varicosity close enough to the spine


    # dump history to a file
    out_Energy = open('out_VaricositySpine_Match_Energy.dat', 'w')
    N = len( history )
    for i in range(0,N) :
        # history -> [ spines_CM, F_CM, T_CM, E_total ]
        #out_Energy.write( '{0}\tspines_CM={1}\tF_CM={2}\tT_CM={3}\tE_total={4}\tspines_attach={5}\n'.format( i, history[i][0], history[i][1], history[i][2], history[i][3], history[i][4] ) )
        out_Energy.write( '{0}\n'.format( history[i][3] ) )
    out_Energy.close()

    print('\nA file with the varicosity-Spine clouds convergence has been writen: out_VaricositySpine_Match_Energy.dat\n')


    # keep track of varicosities cloud
    out_VCloud = open('out_VaricositySpine_Match_VCloud.dat', 'w')
    for v in range( 0, total_varicos ) :
        out_VCloud.write( '{0}\t{1}\t{2}\t'.format( varicos_cloud[v][0], varicos_cloud[v][1], varicos_cloud[v][2] ) )
    out_VCloud.write( '\n' )
    out_VCloud.close()

    # recalculate CM
    spines_CM = numpy.array( [0.0, 0.0, 0.0] )
    for s in range( 0, total_spines ) :
        spines_CM += spines_cloud[s]
    spines_CM = spines_CM / total_spines

    # calculate translation and rotation vector associated with the spines cloud movement
    CM_pos_1 = spines_CM
    CM_rot_1 = Normalize_Vector( spines_cloud[0] - spines_CM )
    CM_translation  = CM_pos_1 - CM_pos_0
    a = numpy.dot( CM_rot_0, CM_rot_1 )
    # what am I doing wrong? shouldn't arccos and dot be robust to this numerical epsilons?
    if a > 1.0 :
        a = 1.0
    if a < -1.0 :
        a = -1.0
    CM_rotation_ang = numpy.arccos( a ) # ATTENTION HERE!
    CM_rotation_vec = Normalize_Vector( numpy.cross( CM_rot_0, CM_rot_1 ) )

    print( '\nTranslation and Rotation operators' )
    print( 'CM_pos_0 = ', CM_pos_0 )
    print( 'CM_rot_0 = ', CM_rot_0 )
    print( 'CM_pos_1 = ', CM_pos_1 )
    print( 'CM_rot_1 = ', CM_rot_1 )
    print( 'CM_translation = ', CM_translation )
    print( 'CM_rotation_ang = ', CM_rotation_ang )
    print( 'CM_rotation_vec = ', CM_rotation_vec )

    # now draw skeleton version of neuron4spines, rotate and translate EVERYTHING and then draw neuron4varicos
    print('\nVERY IMPORTANT: all points from neuron4spines are translated and rotated! Original data HAS BEEN MODIFIED!\n')

    #ATTENTION!!! critical point : be sure you're doing the right thing
    M = numpy.array( Matrix.Rotation( -CM_rotation_ang, 3, CM_rotation_vec ) )
    Transform_Neuron( neuron4spines_id, CM_pos_0, CM_pos_1, CM_rotation_vec, CM_rotation_ang, 1.0 )

    # set layer
    layer = bpy.context.scene['MyDrawTools_BaseLayer']

    # draw neuron4spines
    print('Drawing schematics of neuron4spines: trees and spines only!')
    neuron = neuron4spines
    for tid in range( neuron.total_trees ):   
        # trees
        Draw_RawTree_Skeleton( neuron.tree[tid], layer )       
        # spines
        DrawingFun.Draw_Tree_Spines( neuron.tree[tid], layer )

    # draw neuron4varicosities
    print('Drawing schematics of neuron4varicosities: trees and varicosities only!')
    neuron = neuron4varicosities
    for tid in range( neuron.total_trees ):   
        # trees
        Draw_RawTree_Skeleton( neuron.tree[tid], (layer+1)%20 )   
        # varicos
        DrawingFun.Draw_Tree_Varicosities( neuron.tree[tid], (layer+1)%20 )


    # Mark regions of potential contacts between spines and varicosities
    # -----------------------------------------------------------------------
    print('Marking regions where spines and varicosities are within the attach_dist range')
    name = 'PotentialSynapse'
    # set layers
    layers = [False]*20
    layers[ (layer+2) % 20 ] = True
    # set material
    mat = bpy.data.materials.new( name + '_Mat')
    mat.diffuse_color = [1.0, 0.0, 0.0]
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = [0.0, 0.0, 0.0]
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 1.0
    mat.use_transparency = True
    mat.transparency_method = 'Z_TRANSPARENCY'
    mat.alpha = 0.2
    mat.ambient = 1.0
    # draw
    for s in range( 0, total_spines ) :
        if spines_attach[s] == 1 :
            # mark this spine!
            tid = spines_ids[s][0]
            sid = spines_ids[s][1]
            pos = neuron4spines.tree[tid].spine[sid].Q
            mesh = bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=16, size=2.0*attach_dist, location=pos)

    for obj in bpy.data.objects :
        if obj.name.find('Sphere') != -1 :
            # apply material
            obj.data.materials.append(mat)        
            # set layers
            obj.layers = layers


    #spines_final_cloud = []
    #s = 0
    #print( 'check locations' )
    #for tid in range(0, neuron4spines.total_trees ) :
    #    tree = neuron4spines.tree[tid]
    #    total_spines += tree.total_spines
    #    for sid in range(0, tree.total_spines ) :
    #        spines_final_cloud.append(  numpy.array( tree.spine[sid].Q ) )
    #        n  = numpy.array( tree.spine[sid].Q ) - spines_cloud[s]
    #        d2 = numpy.dot(n,n)
    #        d  = numpy.sqrt( d2 )
    #        s  = s + 1
    #        print(d, n)


    return



#------------------------------------------------------------------------------------------



#DrawingXtras.Transform_Neuron( 0, [0,0,0], [0,0,0], [0,0,1], 3.14/2, 1.0 )
def Transform_Neuron( neuron_id, origin_vec, target_vec, rot_vec, rot_ang, scale ) :
    """Test function that applies a translation, rotation and scale operation to a neuron"""
    """Order of operations are: subtract origin; scale, rotate; add back origin and translate"""

    neuron     = myconfig.neuron[ neuron_id ]
    morphology = myconfig.morphology[ neuron_id ]

    M = numpy.array( Matrix.Rotation( rot_ang, 3, rot_vec ) )

    # go to all morphology structures
    for sid in range(0, morphology.total_structures ) :
        structure = morphology.structure[sid]
        structure.centroid = Transform_Point_RotMat( structure.centroid, origin_vec, target_vec, M, scale )
        # go to all contours
        for cid in range(0, structure.total_contours ) :
            # go to all rawpoints
            rawcontour = structure.rawcontour[cid]
            rawcontour.centroid = Transform_Point_RotMat( rawcontour.centroid, origin_vec, target_vec, M, scale )
            for pid in range(0, rawcontour.total_points ) :
                rawcontour.point[pid] = Transform_Point_RotMat( rawcontour.point[pid], origin_vec, target_vec, M, scale )
            # go to all points
            contour = structure.contour[cid]
            contour.centroid = Transform_Point_RotMat( contour.centroid, origin_vec, target_vec, M, scale )
            for pid in range(0, contour.total_points ) :
                contour.point[pid] = Transform_Point_RotMat( contour.point[pid], origin_vec, target_vec, M, scale )

    # go to all trees
    for tid in range(0, neuron.total_trees ) :
        tree = neuron.tree[tid]
        # go to all rawpoints
        for pid in range(0, tree.total_rawpoints ) :
            tree.rawpoint[pid].P = Transform_Point_RotMat( tree.rawpoint[pid].P, origin_vec, target_vec, M, scale )
            tree.rawpoint[pid].r = scale * tree.rawpoint[pid].r
        # go to all points
        for pid in range(0, tree.total_points ) :
            tree.point[pid].P = Transform_Point_RotMat( tree.point[pid].P, origin_vec, target_vec, M, scale )
            tree.point[pid].n = Transform_Point_RotMat( tree.point[pid].n, [0,0,0], [0,0,0], M, 1.0 )
            tree.point[pid].r = scale * tree.point[pid].r
        # go to all spines
        for sid in range(0, tree.total_spines ) :
            tree.spine[sid].P = Transform_Point_RotMat( tree.spine[sid].P, origin_vec, target_vec, M, scale )
            tree.spine[sid].Q = Transform_Point_RotMat( tree.spine[sid].Q, origin_vec, target_vec, M, scale )
            tree.spine[sid].r = scale * tree.spine[sid].r
        # go to all varicosities
        for vid in range(0, tree.total_varicosities ) :
            tree.varicosity[vid].P = Transform_Point_RotMat( tree.varicosity[vid].P, origin_vec, target_vec, M, scale )
            tree.varicosity[vid].r = scale * tree.varicosity[vid].r


    return



#------------------------------------------------------------------------------------------



def Transform_Point( point_vec, origin_vec, target_vec, rot_vec, rot_ang, scale ):
    """Test function that applies a translation, rotation and scale operation to a point in 3D"""
    """Order of operations are: subtract origin; scale, rotate; add back origin and translate"""

    # move to origin
    point_vec = numpy.array( point_vec ) - origin_vec

    # scale, rotate and then translate and add back origin
    M = numpy.array( Matrix.Rotation( rot_ang, 3, rot_vec ) )    
    return M.dot( scale * point_vec ) + target_vec



#------------------------------------------------------------------------------------------



def Transform_Point_RotMat( point_vec, origin_vec, target_vec, M, scale ):
    """Test function that applies a translation, rotation and scale operation to a point in 3D"""
    """Order of operations are: subtract origin; scale, rotate; add back origin and translate"""

    # move to origin
    point_vec = numpy.array( point_vec ) - origin_vec

    # scale, rotate and then translate and add back origin
    return M.dot( scale * point_vec ) + target_vec



#------------------------------------------------------------------------------------------



def Draw_Spines_Density( neuron, R ):
    """Draw spines density. R (in microns) is the radius of the sphere around each spine"""
    # allocate spines from all dendrites
    layers = [False]*20
    layers[ (bpy.context.scene['MyDrawTools_BaseLayer'] + OPS_LAYER ) % 20 ] = True
    neuron_spines = []
    S = 0
    for i in range(1,neuron.total_trees):
        S = S + neuron.tree[i].total_spines
        for s in range(0,neuron.tree[i].total_spines):
            neuron_spines.append(neuron.tree[i].spine[s])
    # allocate number of spines around R
    window_spines = []
    for a in range(0,S):
        window_spines.append(0)
        for b in range(0,S):
            d = mytools.Get_LineDistance_Between_Points( neuron_spines[a].P, neuron_spines[b].P)
            if d < R:
                window_spines[a] = window_spines[a] + 1
    window_spines = numpy.array( window_spines )
    max_spines = window_spines.max()
    min_spines = window_spines.min()
    # Draw spheres
    for sp in range(0,S):
        r = window_spines[sp] #r = numpy.log(window_spines[sp]) #sphere radius is the logarithm of the number of spines in a radius R
        bpy.ops.surface.primitive_nurbs_surface_sphere_add(radius = r,location=(neuron_spines[sp].P[0], neuron_spines[sp].P[1], neuron_spines[sp].P[2]), layers=layers)
        alpha = ( window_spines[sp] - min_spines ) / ( max_spines - min_spines )
        setMaterial( bpy.context.object, makeMaterial('SpinesDensity_Mat', (0, alpha, 0), (0,0,0), alpha ) )

        
#------------------------------------------------------------------------------------------


def makeMaterial(name, diffuse, specular, alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT' 
    mat.diffuse_intensity = 1.0 
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 1.0
    mat.alpha = alpha
    mat.ambient = 1
    mat.use_transparency = 1
    mat.transparency_method = 'Z_TRANSPARENCY'
    return mat


#------------------------------------------------------------------------------------------

	
def setMaterial(ob, mat):
    me = ob.data
    me.materials.append(mat)
 

 #------------------------------------------------------------------------------------------