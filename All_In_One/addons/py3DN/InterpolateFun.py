# Author: Paulo de Castro Aguiar	
# Date: July 2012
# email: pauloaguiar@fc.up.pt

"""Tree interpolation functions"""


import sys
import time
import copy

import numpy
from numpy import *

import scipy 
from scipy import interpolate, dot

import DataContainers
from DataContainers import *

import myconfig



#------------------------------------------------------------------------------------------



def Interpolate_Objects( neuron, morphology, contours_detail, interpolation_degree, minimal_diam ):
    """
	Interpolate raw points in neuron structure
	"""

    print( 'Interpolating raw points in all structures. This may take a while...' )

    t0 = time.clock()

    for sid in range( 0, morphology.total_structures ):
        Interpolate_Structure( morphology.structure[sid], contours_detail )

    for tid in range(0, neuron.total_trees):
        # first clear any existing interpolation, allowing the Draw button to work more than once
        tree = neuron.tree[tid]
        tree.total_points = 0
        tree.point = []
        # now interpolate
        Interpolate_Tree( neuron, tid, interpolation_degree, minimal_diam )

    Signal_Possible_Mesh_Folding( neuron )

    print( 'Interpolation finished! Total of {0:.2f} seconds processing time'.format( time.clock() - t0 ) )    

    return



#------------------------------------------------------------------------------------------



def Interpolate_Tree( neuron, tid, interpolation_degree, minimal_diam ):
    """Interpolate rawpoints to get nice curves from boring straigth segments"""

    tree = neuron.tree[tid]

    # do not waist time if interpolation_degree == 0; just calculate cross-section normals with row points
    if interpolation_degree == 0 :
        for pid in range(0, tree.total_rawpoints) :
            P      = tree.rawpoint[pid].P[:]
            r      = tree.rawpoint[pid].r
            n      = [0.0, 0.0, 0.0]  # normals will be properly calculated at the end
            ppid   = tree.rawpoint[pid].ppid
            level  = tree.rawpoint[pid].level
            ptype  = tree.rawpoint[pid].ptype
            active = True
            tree.point.append( POINT( P, r, n, ppid, level, ptype, active) )
        tree.total_points = tree.total_rawpoints
        Calculate_Tree_Normals( neuron, tid )
        return


    # now, do all of this if interpolation_degree > 0

    if tree.total_rawpoints < 4 :
        print( '\n\nERROR - each tree must have, at least, four points (including ROOT)! In addition, between ROOT and any endpoint there should be 2 points!' )
        print( '\t\tTree with error:' + str(neuron.tree[tid].type) + ', ' + str(tid) + '\n\n' )
        sys.exit()    


    # always add first point - ROOT
    p0 = array( tree.rawpoint[0].P )    
    p1 = array( tree.rawpoint[1].P )
    n = Normalize_Vector( p1 - p0 )
    if numpy.sqrt( numpy.dot(n,n) ) < 1.0e-6 :
        print( "ERROR: two first point in tree " + str(tid) + " are overlapping! Consider reloading the xml file with the 'apply point removal' option selected" )
        sys.exit()

    rawpoint = tree.rawpoint[0]
    tree.point.append( POINT( p0, rawpoint.r, n, -1, 0, rawpoint.ptype, True) )
    tree.total_points += 1

    # as new interpolated points are added, an offset is introduced to the ppid's; this variable accounts for this offset 
    pid_offset = 0;
    points_added = [0] # only for debugging purposes
    old2new_pid = [0]  # pid's of the first two points do not change from tree.rawpoint to point conversion

    for pid in range(3, tree.total_rawpoints):

        P3ppid = tree.rawpoint[  pid   ].ppid
        P2ppid = tree.rawpoint[ P3ppid ].ppid
        P1ppid = tree.rawpoint[ P2ppid ].ppid

        if P3ppid == -1 or P2ppid == -1 or P1ppid == -1:
            # Not good; we're in the situation where before the first node there's less than 4 points!
            print( '\n\nWarning: at least 3 points should follow the ROOT point before a node!' )
            print( '         in addition, between ROOT and any endpoint there should be 2 points!' )
            print( '         Problem in tree:' + str(neuron.tree[tid].type) + ', ' + str(tid) )
            print( '         -> parents:' + str(P3ppid) + ', ' + str(P2ppid) + ', ' + str(P1ppid) )
            print( '         -> points:' + str(pid) + ', ' + str(P3ppid) + ', ' + str(P2ppid) + ', ' + str(P1ppid) )
            print( '         -> last point coords:' + str(tree.rawpoint[pid].P) )
            break

        P3 = tree.rawpoint[  pid  ]
        P2 = tree.rawpoint[ P3ppid]
        P1 = tree.rawpoint[ P2ppid]
        P0 = tree.rawpoint[ P1ppid]

        # GET INTERPOLATED POINTS
        # -----------------------
        if P3ppid == pid - 1:
            start_ppid = tree.total_points - 1    # on sequence
        else:
            start_ppid = old2new_pid[P1ppid]      # off sequence

        new_interpolated_points = Get_Interpolated_Points(P0, P1, P2, P3, start_ppid, tree.total_points - 1, interpolation_degree, minimal_diam)
        total_new_points_added = len( new_interpolated_points )

        pid_offset += total_new_points_added
        old2new_pid.append( pid_offset )
        points_added.append( total_new_points_added )

        tree.point.extend( new_interpolated_points )
        tree.total_points += total_new_points_added

    
    # not very smart/efficient but... be sure of what points are indeed nodes in the new interpolated tree
    ppid_list = [0] * tree.total_points
    for pid in range(0, tree.total_points) :
        ppid_list[pid] = tree.point[pid].ppid
    ppid_list.sort()
    node_counter = 0
    for i in range(1, tree.total_points) :
        if ppid_list[i] == ppid_list[i-1] :
            pid = ppid_list[i]
            tree.point[pid].ptype = 'node'
            node_counter += 1

    print('Total effective node points in tree ' + str(tid) + ' is : ' + str(node_counter) )

    return



#------------------------------------------------------------------------------------------



def Calculate_Tree_Normals( neuron, tid ):
    """ calculate all cross-section normals in raw points """

    tree = neuron.tree[tid]

    # for P0 use the cellbody centroid
    if neuron.cellbody != [] :
        if neuron.cellbody.total_contours > 0 :
            mc = int( 0.5 * neuron.cellbody.total_contours )
            n = numpy.array( tree.point[0].P ) - numpy.array( neuron.cellbody.contour[ mc ].centroid )
            n = Normalize_Vector(n)
            tree.point[0].n = n
    else :
        n = numpy.array( tree.point[1].P ) - numpy.array( tree.point[0].P )
        n = Normalize_Vector(n) 
        tree.point[0].n = n

    if n.dot(n) == 0.0:
        tree.point[0].n = numpy.array( [0.0, 0.0, 1.0] )
        print('WARNING: the two first points in tree ' + str(tid) + ' have the same coordinates! The normal vector will be incorrectely calculated!')

    for pid in range(2, tree.total_points):

        P2ppid = tree.point[ pid  ].ppid
        P1ppid = tree.point[P2ppid].ppid
        P2 = tree.point[ pid  ]
        P1 = tree.point[P2ppid]
        P0 = tree.point[P1ppid]

        # set P1 normal
        n = numpy.array( P2.P ) - numpy.array( P0.P )
        n = Normalize_Vector(n)
        new_pid = P1ppid
        while n.dot(n) == 0.0 and new_pid > 0:
            new_pid = tree.point[new_pid].ppid
            n = numpy.array( P2.P ) - numpy.array( tree.point[new_pid].P )
            n = Normalize_Vector(n)
        tree.point[P2ppid].n = n
        
        # if P2 is an endpoint, set its normal too
        if P2.ptype == 'endpoint' :
            n = numpy.array( P2.P ) - numpy.array( P1.P )
            n = Normalize_Vector(n)
            new_pid = P2ppid
            while n.dot(n) == 0.0 and new_pid > 0:
                new_pid = tree.point[new_pid].ppid
                n = numpy.array( P2.P ) - numpy.array( tree.point[new_pid].P )
                n = Normalize_Vector(n)
            tree.point[pid].n = n


    return



#------------------------------------------------------------------------------------------



def Get_Interpolated_Points(P0, P1, P2, P3, start_pid, ptotal, interpolation_degree, minimal_diam): # returns interpolating points between P0 and P3

    N = interpolation_degree + 1 # number of interpolated points between each raw points pair - GET THIS PARAMETER FROM THE GUI

    r_min = 0.5 * minimal_diam
    new_points = []
    ez = numpy.array([0,0,1]) 

    # calculate interpolated points for the Bezier curve: A, P1, B; where P1 is already known
    x = [ P0.P[0], P1.P[0], P2.P[0], P3.P[0] ] 
    y = [ P0.P[1], P1.P[1], P2.P[1], P3.P[1] ] 
    z = [ P0.P[2], P1.P[2], P2.P[2], P3.P[2] ] 
    r = [ P0.r, P1.r, P2.r, P3.r ]
    a = [ 0.0, 1.0, 2.0, 3.0 ] # used to solve a fitpack.py limitation: the first vector must have strictly increasing values 

    tck,u = interpolate.splprep([a,x,y,z,r], s=0, k=3)


    if P3.ptype == 'endpoint':

        # ENDPOINT OPERATION: P3 is an end point and the whole branch P0,P1,P2,P3 gets interpolated
        dt = u[1] / N
        for i in range(1, N):        
            t = i * dt
            out = interpolate.splev( t, tck, der=0 )  # [1:4] returns [x,y,z] and [4] returns r
            n = interpolate.splev( t, tck, der=1 )
            n = Normalize_Vector( numpy.array(n[1:4]) ) # [1:4] returns [x,y,z] and [4] returns r
            if out[4] < r_min:
                out[4] = r_min  # avoid interpolated radius smaller than gui's minimal_diameter
            if i == 1:
                ppid = start_pid
            else:
                ppid = ptotal
            new_points.append( POINT( numpy.array(out[1:4]), out[4], n, ppid, P0.level, 'standard', True ) )
            ptotal += 1
        # complete sequence with point P1
        if N < 2:
            ppid = start_pid
        else:
            ppid = ptotal
        n = interpolate.splev( u[1], tck, der=1 )
        n = Normalize_Vector( numpy.array(n[1:4]) ) # [1:4] returns [x,y,z] and [4] returns r         
        new_points.append( POINT( numpy.array(P1.P), P1.r, n, ppid, P1.level, P1.ptype, True ) )
        ptotal += 1

        dt = ( u[2] - u[1] ) / N
        for i in range(1, N):        
            t = i * dt + u[1]
            out = interpolate.splev( t, tck, der=0 )  # [1:4] returns [x,y,z] and [4] returns r
            n = interpolate.splev( t, tck, der=1 )
            n = Normalize_Vector( numpy.array(n[1:4]) ) # [1:4] returns [x,y,z] and [4] returns r     
            if out[4] < r_min:
                out[4] = r_min
            new_points.append( POINT( numpy.array(out[1:4]), out[4], n, ptotal, P2.level, 'standard', True ) )
            ptotal += 1
        # complete sequence with point P2
        n = interpolate.splev( u[2], tck, der=1 )
        n = Normalize_Vector( numpy.array(n[1:4]) ) # [1:4] returns [x,y,z] and [4] returns r     
        new_points.append( POINT( numpy.array(P2.P), P2.r, n, ptotal, P2.level, P2.ptype, True ) )
        ptotal += 1

        dt = ( u[3] - u[2] ) / N
        for i in range(1, N):        
            t = i * dt + u[2]
            out = interpolate.splev( t, tck, der=0 )  # [1:4] returns [x,y,z] and [4] returns r
            n = interpolate.splev( t, tck, der=1 )
            n = Normalize_Vector( numpy.array(n[1:4]) ) # [1:4] returns [x,y,z] and [4] returns r     
            if out[4] < r_min:
                out[4] = r_min
            new_points.append( POINT( numpy.array(out[1:4]), out[4], n, ptotal, P2.level, 'standard', True ) )
            ptotal += 1
        # complete sequence with point P3
        n = interpolate.splev( u[3], tck, der=1 )
        n = Normalize_Vector( numpy.array(n[1:4]) ) # [1:4] returns [x,y,z] and [4] returns r   
        new_points.append( POINT( numpy.array(P3.P), P3.r, n, ptotal, P3.level, 'endpoint', True ) )


    else:             
        # STANDARD OPERATION: only interval between rawpoints P0-P1 gets interpolated        
        dt = u[1] / N

        # if fiber is almost straight, don't waist time interpolating
        n0 = Normalize_Vector( numpy.array(P1.P) - numpy.array(P0.P) )
        n1 = Normalize_Vector( numpy.array(P2.P) - numpy.array(P1.P) )
        if numpy.dot(n0,n1) > 0.999: # condition 0.999 means that theta is less than 2.6 degrees
            N = 0

        for i in range(1,N):        
            out = interpolate.splev( i * dt, tck, der=0 )  # [1:4] returns [x,y,z] and [4] returns r
            n = interpolate.splev( i * dt, tck, der=1 )
            n = Normalize_Vector( numpy.array(n[1:4]) ) # [1:4] returns [x,y,z] and [4] returns r     
            if out[4] < r_min:
                out[4] = r_min
            if i == 1:
                ppid = start_pid
            else:
                ppid = ptotal
            new_points.append( POINT( numpy.array(out[1:4]), out[4], n, ppid, P0.level, 'standard', True ) )
            ptotal += 1
        # complete with point P1
        if N < 2:
            ppid = start_pid
        else:
            ppid = ptotal
        n = interpolate.splev( u[1], tck, der=1 )
        n = Normalize_Vector( numpy.array(n[1:4]) ) # [1:4] returns [x,y,z] and [4] returns r  
        new_points.append( POINT( numpy.array(P1.P), P1.r, n, ppid, P1.level, 'standard', True ) )


    # the ptype flag will be corrected afterwards, after the interpolation is completed

    return new_points



#------------------------------------------------------------------------------------------



def Normalize_Vector( n ):

    norm = numpy.sqrt( numpy.dot(n,n) )
    if numpy.fabs( norm ) < 1.0e-69 :
        return numpy.array( [0.0, 0.0, 0.0] )
    else :
        return n / norm



#------------------------------------------------------------------------------------------



def Interpolate_Structure( morph_struct, detail ): # returns interpolation for morph_struct contours

    # choose N, the number of points in each new contour
    max_total_points = 0
    for cid in range(0, morph_struct.total_contours):
        if morph_struct.rawcontour[cid].total_points > max_total_points :
            max_total_points = morph_struct.rawcontour[cid].total_points
    N = max_total_points * detail

    # first clear any existing interpolation, allowing the Draw button to work more than once
    morph_struct.contour = []
    morph_struct_centroid = numpy.array( [0.0]*3 )

    for cid in range(0, morph_struct.total_contours):

        rawcontour = morph_struct.rawcontour[cid]
        rawcentroid = numpy.array( [0.0]*3 )
        x = []
        y = []
        z = []
        a = []
        for pid in range(0, rawcontour.total_points):
            point = rawcontour.point[pid]
            x.append( point[0] ) 
            y.append( point[1] ) 
            z.append( point[2] ) 
            a.append( 1.0 * pid )
            rawcentroid += numpy.array( point[0:3] )
        rawcentroid = rawcentroid / rawcontour.total_points

        # update morph_struct centroid (uses rawcontour centroids)
        morph_struct_centroid += rawcentroid

        # close contour
        point = rawcontour.point[0]
        x.append( point[0] )
        y.append( point[1] )
        z.append( point[2] )
        a.append( 1.0 * rawcontour.total_points )

        if len(x) > 3 :
            tck,u = interpolate.splprep([a,x,y,z], s=0, k=3)
        else :
            tck,u = interpolate.splprep([a,x,y,z], s=0, k=1)

       
        contour = CONTOUR()
        centroid = numpy.array( [0.0]*3 )

        dt = 1.0  / N 
        for i in range(0, N):        
            t = i * dt
            new_point = interpolate.splev( t, tck )
            contour.point.append( new_point[1:4] )   # [1:4] returns [x,y,z]       
            centroid += numpy.array( new_point[1:4] )
            contour.total_points += 1

        contour.centroid = centroid / N
        contour.color = rawcontour.color
        morph_struct.contour.append( contour )

        # also update centroid in rawcontour
        rawcontour.centroid = rawcentroid


    # update morph_struct centroid (notice that it was calculated with raw contours centroids )
    morph_struct.centroid = morph_struct_centroid / morph_struct.total_contours

    # If this is a CellBody structure it will be automatically updated in the neuron data structure
    # (since they point to the same address)

    return



#------------------------------------------------------------------------------------------



def Signal_Possible_Mesh_Folding( neuron ):
    """Mark all tree points, in all trees, which will give rise to mesh folding"""

    for tid in range(0, neuron.total_trees):

        tree = neuron.tree[tid]
        tree.total_activepoints = tree.total_points

        for pid in range(1, tree.total_points):

            active_ppid = Get_Closest_Active_Parent(tree, pid)
            P1 = tree.point[ pid         ]
            P0 = tree.point[ active_ppid ]

            v = numpy.array( P1.P ) - numpy.array( P0.P )
            dist = numpy.sqrt( numpy.dot(v,v) )        
            n1 = P1.n
            n0 = P0.n
            D = numpy.dot(n0, n1)
            if numpy.fabs(D) > 1.0 : # cope with numerical instability....
                D = 1.0 * numpy.sign(D)
            ang = numpy.arccos( D )
            if P1.r * numpy.sin( ang ) < dist:
                P1.active = True
            else:
                P1.active = False
                tree.total_activepoints -= 1


    return



#------------------------------------------------------------------------------------------



def Get_Closest_Active_Parent(tree, pid):

    closest_active_pid = tree.point[pid].ppid

    while tree.point[closest_active_pid].active == False:
        closest_active_pid = tree.point[closest_active_pid].ppid

    return closest_active_pid



#------------------------------------------------------------------------------------------
