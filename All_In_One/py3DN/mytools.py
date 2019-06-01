# Authors: Paulo de Castro Aguiar
#          Maria Mafalda Sousa
# Date:    May 2015
# email:   pauloaguiar@fc.up.pt

"""Basic collection of tools, including simple morphometric analysis"""

import numpy

import myconfig
from myconfig import *

# LIST OF FUNCTIONS
# -----------------
# *functions for showing data in text mode*
# Show_RawPoint
# Show_Tree
# Show_Tree_RawTopology
# Show_Tree_Topology
# Show_Tree_RawPoints
# Show_Tree_Points
# Show_Neuron
# Show_Morphology

# *functions for basic morphometric analysis*
# Get_LineDistance_Between_Points
# Get_FiberDistance_Between_RawPoints
# Get_Tree_Length
# Get_Tree_Surface
# Get_Tree_Volume
# Get_CellBody_Surface

# *output functions*
# LineDistance
# FiberDistance
# Dump_Axon

# *visualization support functions*
# Find_PointID_In_Tree
# Find_PointID_In_Space




#------------------------------------------------------------------------------------------


def Show_Point( point ):
    """Show point data"""
    print( 'P      = ' + str(point.P) )
    print( 'r      = ' + str(point.r) )
    print( 'n      = ' + str(point.n) ) 
    print( 'ppid   = ' + str(point.ppid) )
    print( 'level  = ' + str(point.level) )
    print( 'ptype  = ' + str(point.ptype) )
    print( 'active = ' + str(point.active) )
    return


#------------------------------------------------------------------------------------------


def Show_RawPoint( rawpoint ):
    """Show raw point data"""
    print( 'P       = ' + str(rawpoint.P) )
    print( 'r       = ' + str(rawpoint.r) )
    print( 'ppid    = ' + str(rawpoint.ppid) )
    print( 'level   = ' + str(rawpoint.level) )
    print( 'ptype   = ' + str(rawpoint.ptype) )
    print( 'contact = ' + str(rawpoint.contact) )
    return


#------------------------------------------------------------------------------------------


def Show_Tree( tree ):
    """Show tree data"""
    print( 'total_points       = ' + str(tree.total_points) )
    print( 'total_rawpoints    = ' + str(tree.total_rawpoints) )
    print( 'total_spines       = ' + str(tree.total_spines) )
    print( 'total_varicosities = ' + str(tree.total_varicosities) )
    print( 'leaf               = ' + str(tree.leaf) )
    print( 'type               = ' + str(tree.type) )
    print( 'color              = ' + str(tree.color) )


#------------------------------------------------------------------------------------------


def Show_Tree_RawTopology( tree ):
    """Show the raw tree topology in text mode"""
    for i in range(0, tree.total_rawpoints):
        P = tree.rawpoint[i]
        offset = ''
        for c in range(0, P.level):
            offset = offset + ' '
        if P.ptype == 'standard':
            flag = '|'
        if P.ptype == 'node':
            flag = '\\'
        if P.ptype == 'endpoint':
            flag = 'X'

        # check presence of varicosities
        if P.contact == True:
            flag = flag + 'o'

        print( str(offset) + str(flag) + '\t\t' + str(i) + ', ppid =' + str(tree.rawpoint[i].ppid) + ', level =' + str(tree.rawpoint[i].level) + ', ' + str(tree.rawpoint[i].P) )


#------------------------------------------------------------------------------------------


def Show_Tree_Topology( tree ):
    """Show the tree topology in text mode"""
    for i in range(0, tree.total_points):
        P = tree.point[i]
        offset = ''
        for c in range(0, P.level):
            offset = offset + ' '
        if P.ptype == 'standard':
            flag = '|'
        if P.ptype == 'node':
            flag = '\\'
        if P.ptype == 'endpoint':
            flag = 'X'

        print( str(offset) + str(flag) + '\t\t' + str(i) + ', ppid =' + str(tree.point[i].ppid) + ', level =' + str(tree.point[i].level) + ', ' + str(tree.point[i].P) )


#------------------------------------------------------------------------------------------


def Show_Tree_RawPoints( tree ):
    """Show tree raw points data"""
    for pid in range(0, tree.total_rawpoints):
        P = tree.rawpoint[pid]
        print( str(pid) + '\tppid =' + str(P.ppid) + '\tP =' + str(P.P) + '\tr =' + str(P.r) + '\tlevel =' + str(P.level) + '\tptype =' + str(P.ptype) )


#------------------------------------------------------------------------------------------


def Show_Tree_Points( tree ):
    """Show tree points data"""
    for pid in range(0, tree.total_points):
        P = tree.point[pid]
        print( str(pid) + '\tppid =' + str(P.ppid) + '\tP =' + str(P.P) + '\tr =' + str(P.r) + '\tn =' + str(P.n) + '\tlevel =' + str(P.level) + '\tactive =' + str(P.active) )


#------------------------------------------------------------------------------------------


def Show_Neuron( neuron ):
    """Show data in neuron structure"""
    print( 'neuron data:' )
    print( 'label       = ' + neuron.label )
    print( 'cellbody    = ' + str( neuron.cellbody ) )
    print( 'total_trees = ' + str( neuron.total_trees ) )
    print( 'tree        = ' + str( neuron.tree ) )
    

#------------------------------------------------------------------------------------------


def Show_Morphology( morphology ):               
    """Show data in morphology structure"""
    print( 'morphology data:' )
    print( 'total_structures = ' + str( morphology.total_structures ) )
    print( 'structure        = ' + str( morphology.structure ) )


#------------------------------------------------------------------------------------------


def Get_LineDistance_Between_Points( pointA, pointB ):
    """Calculate straight line distance between two points (in [x,y,z] format)"""
    a = numpy.array(pointA)
    b = numpy.array(pointB)
    d = a-b
    return numpy.sqrt(numpy.vdot(d,d))


#------------------------------------------------------------------------------------------


def Get_FiberDistance_Between_RawPoints( tree, pid0, pid1 ):
    """Calculate distance, traveled over the fiber, between two points"""
    # assign A and B to the pid's, making B the point with the lowest pid
    if pid0 > pid1 :
        A = pid0
        B = pid1
    else :
        A = pid1
        B = pid0        

    # now trace back all B's parents until the tree's first point
    B_backtrace = numpy.zeros( B + 1, dtype=numpy.int32 ) # allocate space for faster processing
    B_backtrace[0] = B
    ppid = tree.rawpoint[B].ppid
    B_threadsize = 1
    while ppid != -1 :
        B_backtrace[ B_threadsize ] = ppid
        ppid = tree.rawpoint[ppid].ppid # get the father's father a.k.a. grandad
        B_threadsize += 1
    
    # now move along A's parents until we find a point match
    A_length = 0.0
    pid  = A
    ppid = A # discards first point in length calculation
    while ppid > -1 :

        # check if pid is present in B_backtrace vector
        k = numpy.nonzero( B_backtrace == ppid )[0]

        if len(k) == 1 :
            # got a common point... Hurray!
            i = k[0]
            A_length += Get_LineDistance_Between_Points( tree.rawpoint[pid].P, tree.rawpoint[ppid].P)
            # now calculate B_length
            B_length = 0.0
            for j in range(0,i) :
                pid = B_backtrace[j]
                ppid = B_backtrace[j+1]
                B_length += Get_LineDistance_Between_Points( tree.rawpoint[pid].P, tree.rawpoint[ppid].P )
            # finally add both lengths together and return the result
            return A_length + B_length

        else :
            # match not yet found: update lengths and go up one parent in A
            A_length += Get_LineDistance_Between_Points( tree.rawpoint[pid].P, tree.rawpoint[ppid].P)
            pid  = ppid
            ppid = tree.rawpoint[pid].ppid
 
    # Hum... if you arrived here empty handed this is bad news!
    # You haven't been able to connect both points in the tree.
    # Signal this with an invalid -1 distance return
    return -1.0


#------------------------------------------------------------------------------------------


def Varicosities_LineDistance( tree ):
    """Calculates pairwise distances between varicosities (straight line distance) and writes output to file out_Varicosities_LineDistances.dat"""
    out = open('out_Varicosities_LineDistances.dat', 'w')

    N = tree.total_varicosities
    d = numpy.zeros( (int) ((N-1)*N*0.5) )
    k = 0
    for i in range(1,N-1) :
        if (N-1-i)%100 == 0 :
            print( str(N-1-i) )
        for j in range(0,i) :
            d[ k ] = Get_LineDistance_Between_Points( tree.varicosity[i].P, tree.varicosity[j].P )
            out.write( str(d[k]) + '\n' )
            k += 1

    out.close()
    

#------------------------------------------------------------------------------------------


def Varicosities_FiberDistance( tree ):
    """Calculates pairwise distances between varicosities (distance over the fiber) and writes output to file out_Varicosities_FiberDistances.dat"""
    out = open('out_Varicosities_FiberDistances.dat', 'w')

    N = tree.total_varicosities
    d = numpy.zeros( (int) ((N-1)*N*0.5) )
    k = 0
    for i in range(1,N-1) :
        if (N-1-i)%10 == 0 :
            print( str(N-1-i) )
        for j in range(0,i) :
            d[ k ] = Get_FiberDistance_Between_RawPoints( tree, tree.varicosity[i].rawppid, tree.varicosity[j].rawppid )
            out.write( str(d[k]) + '\n' )
            k += 1

    out.close()


#------------------------------------------------------------------------------------------


def Dump_Axon( tree ) :
    """Dumps the axon raw points to file out_tree_rawpoints.dat and the varicosities locations to out_tree_varicosities.dat"""
    out = open('out_tree_rawpoints.dat', 'w')

    N = tree.total_rawpoints    
    for i in range(0,N) :
        P = tree.rawpoint[i]
        out.write( "%ld\t%.3f\t%.3f\t%.3f\t%.3f\t%ld\t%d\t%d\n" % ( i, P.P[0],P.P[1],P.P[2], P.r, P.ppid, P.level, P.ptype ) )

    out.close()


    out = open('out_tree_varicosities.dat', 'w')

    N = tree.total_varicosities    
    for i in range(0,N) :
        V = tree.varicosity[i]
        out.write( "%ld\t%.3f\t%.3f\t%.3f\t%.3f\t%ld\n" % ( i, V.P[0], V.P[1], V.P[2], V.r, V.rawppid ) )

    out.close()


#------------------------------------------------------------------------------------------


def Change_Selected_Neuron( neuron_index ):               
    """Support function for the GUI"""
    if neuron_index < 0 or neuron_index > myconfig.total_neurons - 1 :
        print( 'Your neuron index is invalid. It needs to be an integer in the interval {0,...,total_neurons-1}, where total_neurons is the total number of neurons loaded (' + str( myconfig.total_neurons ) + '). No changes have been produced and your selected neuron is still ' + str( myconfig.selected_neuron ) + '.' )
    else : 
        myconfig.selected_neuron = neuron_index


#------------------------------------------------------------------------------------------


def Reload() :
    """Function used for debugging DrawingXtras functions"""
    from imp import reload
    #Blender.Registry.RemoveKey('regMyGlobals')
    reload( DrawingXtras )


#------------------------------------------------------------------------------------------


def Get_Tree_Length( tree, start_point_id = 0):
    """Calculates the total length of the (sub)tree after the specified node id (default=0, i.e. root node). Units in um."""
    # start_point_id is an optional argument to specify a starting tree point id
    N = tree.total_rawpoints
    tree_length = 0.0
    if start_point_id == 0:
        # in case of no second argument, calculate length for complete tree
        for i in range(1,N) :
            pid = tree.rawpoint[i].ppid
            dist = Get_LineDistance_Between_Points( tree.rawpoint[i].P, tree.rawpoint[pid].P)
            tree_length =  tree_length + dist
    else :
        # calculate length tree from a starting point
        l = tree.rawpoint[start_point_id].level
        pty = tree.rawpoint[start_point_id].ptype
        i = start_point_id + 1
        while i < N:
            pid = tree.rawpoint[i].ppid
            l1 = tree.rawpoint[i].level
            if  pid < start_point_id or l1 < l:
                break
            dist = Get_LineDistance_Between_Points( tree.rawpoint[i].P, tree.rawpoint[pid].P)
            tree_length =  tree_length + dist
            i += 1
    return tree_length
  
  
            
#------------------------------------------------------------------------------------------


def Get_Tree_Surface( tree, start_point_id = 0):
    """Calculates the total surface of the (sub)tree after the specified node id (default=0, i.e. root node). Units in square um."""
    # start_point_id is an optional argument to specify a starting tree point id
    
    N = tree.total_rawpoints
    tree_surface = 0.0
    if start_point_id == 0:
        # in case of no second argument, calculate complete tree surface area 
        for i in range(1,N) :
            pid = tree.rawpoint[i].ppid
            r = tree.rawpoint[i].r
            R = tree.rawpoint[pid].r
            h = Get_LineDistance_Between_Points( tree.rawpoint[i].P, tree.rawpoint[pid].P)
            g = numpy.sqrt(h*h + (R-r)*(R-r))
            area = numpy.pi * g * (R + r)
            tree_surface =  tree_surface + area
    else:
        # calculate tree surface area from a starting point
        l = tree.rawpoint[start_point_id].level
        pty = tree.rawpoint[start_point_id].ptype
        i = start_point_id + 1
        while i < N:
            pid = tree.rawpoint[i].ppid
            l1 = tree.rawpoint[i].level
            if  pid < start_point_id or l1 < l:
                break
            r = tree.rawpoint[i].r
            R = tree.rawpoint[pid].r
            h = Get_LineDistance_Between_Points( tree.rawpoint[i].P, tree.rawpoint[pid].P)
            g = numpy.sqrt(h*h + (R-r)*(R-r))
            area = numpy.pi * g * (R + r)
            tree_surface =  tree_surface + area
            i += 1
    return tree_surface

            
#------------------------------------------------------------------------------------------


def Get_Tree_Volume( tree, start_point_id = 0 ):
    """Calculates the total volume of the (sub)tree after the specified node id (default=0, i.e. root node). Units in cubic um."""
    # start_point_id is an optional argument to specify a starting tree point id
    N = tree.total_rawpoints
    tree_volume = 0.0
    if start_point_id == 0:
        # in case of no second argument, calculate complete tree volume
        for i in range(1,N) :
            pid = tree.rawpoint[i].ppid
            r = tree.rawpoint[i].r
            R = tree.rawpoint[pid].r
            h = Get_LineDistance_Between_Points( tree.rawpoint[i].P, tree.rawpoint[pid].P)
            volume = numpy.pi * h / 3 * (R*R + r*r + R*r)
            tree_volume =  tree_volume + volume
    else:
        # calculate tree volume from a starting point
        l = tree.rawpoint[start_point_id].level
        pty = tree.rawpoint[start_point_id].ptype
        i = start_point_id + 1
        while i < N:
            pid = tree.rawpoint[i].ppid
            l1 = tree.rawpoint[i].level
            if  pid < start_point_id or l1 < l:
                break
            r = tree.rawpoint[i].r
            R = tree.rawpoint[pid].r
            h = Get_LineDistance_Between_Points( tree.rawpoint[i].P, tree.rawpoint[pid].P)
            volume = numpy.pi * h / 3 * (R*R + r*r + R*r)
            tree_volume =  tree_volume + volume
            i += 1
    return tree_volume


#------------------------------------------------------------------------------------------


def Get_2DCellBody_Surface( contour ):
    """Calculates the contour surface of the cell body represented by a single contour. Units in square um."""
    # returns cell body contour area
    N = contour.total_points
    contour_surface = 0.0
    for i in range(1,N) :
        a = Get_LineDistance_Between_Points( contour.point[i], contour.point[i-1])
        b = Get_LineDistance_Between_Points( contour.point[i-1], contour.centroid)
        c = Get_LineDistance_Between_Points( contour.point[i], contour.centroid)
        p = (a + b + c)/2
        area = numpy.sqrt( p*(p-a)*(p-b)*(p-c))
        contour_surface = contour_surface + area
    return contour_surface


#------------------------------------------------------------------------------------------

def Find_PointID_In_Tree(point_x, point_y, point_z, tree):
    """Get the Point ID from point coordinates. This function assumes that the tree has been drawn with the Draw_RawTree_Skeleton function (DrawingXtras.py)"""
    P0 = numpy.array( [point_x, point_y, point_z] )
    N = tree.total_rawpoints
    point_dist = [0]*N
    for i in range(0,N):
       P1 = numpy.array(tree.rawpoint[i].P)
       if tree.rawpoint[i].P ==[point_x, point_y, point_z]:
           return i
       d = P1-P0           
       point_dist[i] = numpy.vdot(d,d)
    return numpy.argmin(point_dist)
    

#------------------------------------------------------------------------------------------

 
def Find_PointID_In_Space(point_x, point_y, point_z):
    """Get the Point ID from point coordinates. The function returns an array with the index ids of the neuron, tree and point which are closest to the provided coodinates: [neuron_id, tree_id, point_id].""" 
    P0 = numpy.array( [point_x, point_y, point_z] )
    min_n = 0
    min_t = 0
    min_p = 0
    min_d = 1E10
    for n in range(0, len(neuron)):
        for t in range (0, neuron[n].total_trees):
            tree=neuron[n].tree[t]
            point_dist = [0]*tree.total_rawpoints
            for p in range(0,tree.total_rawpoints):
                P1 = numpy.array(tree.rawpoint[p].P)
                if tree.rawpoint[p].P == [point_x, point_y, point_z]:
                   return [n, t, p]
                d = P1-P0           
                point_dist[p] = numpy.vdot(d,d)
            min_temp = numpy.min(point_dist)
            if min_temp < min_d:
                min_n = n
                min_t = t
                min_p = numpy.argmin(point_dist)
                min_d = min_temp
    return [min_n, min_t, min_p]
                

#------------------------------------------------------------------------------------------













def Spines_FiberDistance_Histogram( neuron ) :
    """Saves spines fiber distance in a data file (MS, September2013)"""
    print('VALIDATE!')	
    out = open('Spines_FiberDistances.dat', 'w')


    total_trees = neuron.total_trees
    aux = 0
    for t in range (0,total_trees):
        N = neuron.tree[t].total_spines
        if N != 0:
            for u in range (t,total_trees):
                M =neuron.tree[u].total_spines
                d = []
                if M !=0:
                    if u!=t:
                        d = numpy.zeros((int)((N-1)*N*0.5)*M)
                    else :
                        d = numpy.zeros((int)((N-1)*N*0.5))  
                    k = 0
                    if t == u:
                        for i in range(1,N) :
                            for j in range(0,i) :
                                d[ k ] = Get_FiberDistance_Between_RawPoints( neuron.tree[u], neuron.tree[u].spine[j].rawppid, neuron.tree[u].spine[i].rawppid )
                                out.write(str(d[k]) + '\n')
                                k += 1
                                aux+=1
                    if t!=u:
                        for i in range(0,M-1) :
                            d_i = Get_FiberDistance_Between_RawPoints( neuron.tree[u], neuron.tree[u].spine[i].rawppid, 0)
                            for j in range(1, N):
                                for l in range(0,j):
                                        d[ k ] = Get_FiberDistance_Between_RawPoints( neuron.tree[t], neuron.tree[t].spine[j].rawppid, neuron.tree[t].spine[l].rawppid )+ d_i
                                        out.write(str(d[k]) + '\n')
                                        k += 1
                                        aux+=1
    print(aux)
                           
    out.close()	

	
#------------------------------------------------------------------------------------------


def Spines_location_data( neuron ):
    """Saves spines position in a data file to open in Neuron (Mafalda, June2013)"""
    print('VALIDATE!')
    out = open('spines_location.dat', 'w')
    T = neuron.total_trees
    S = 0
    for i in range(1,T) :
        S = S + neuron.tree[i].total_spines
    out.write(str(S)+ '  ' + str(3) + '\n')
    for i in range(1,T) :
        S = neuron.tree[i].total_spines
        for j in range(0,S) :
            coord = neuron.tree[i].spine[j].P
            head = neuron.tree[i].spine[j].Q
            out.write( str(coord[0]) + ' ' + str(coord[1]) + ' ' + str(coord[2]) + '\n')
            #out.write( str(head[0]) + ' ' + str(head[1]) + ' ' + str(head[2]) + ' ' + str(neuron.tree[i].spine[j].r) + '\n' )
    out.close()


#---------------------------------------------------------------------


def DumpAllDendriticPoints( neuron ):
    """Dump 3d coordinates of all points in dendrites (exclude axon, which is assumed to be tree[0]"""
    print('VALIDATE!')
    out = open('out_all_dendrites_points.dat', 'w')
    
    for t in range( 1, neuron.total_trees ):
        tree = neuron.tree[t]
        for p in range( 0, tree.total_rawpoints ):
            out.write( str( tree.rawpoint[p].P[0]) + '\t' + str( tree.rawpoint[p].P[1]) + '\t' + str( tree.rawpoint[p].P[2]) +'\n' )
    
    out.close()


#---------------------------------------------------------------------


def Get_Fiber_Distance_Between_RandomSpines( neuron ):
	print('VALIDATE!')

	import numpy as np
	from random import randint

	pos = np.loadtxt('I:\\Random_spines_position.dat', skiprows=1 ) # read data
	N = pos.shape[0] # get number of spines
	dads = np.zeros((N,2), dtype=numpy.int) # variable to hold tree and pid of points co-localized with spines

	# fill in dads
	shit = False
	for s in range(0,N):
		done = False
		for t in range(1,neuron.total_trees): #CAREFUL, assumes axon is tree[0] and skips it
			tree = neuron.tree[t]
			for p in range(0,tree.total_rawpoints):
				if tree.rawpoint[p].P[0] == pos[s,0] and tree.rawpoint[p].P[1] == pos[s,1] and tree.rawpoint[p].P[2] == pos[s,2] :
					dads[s,:] = [t,p]
					done = True
					break
				if p == tree.total_rawpoints - 1 and t == neuron.total_trees - 1:
					print("OOPS!... Spine not located in tree. ABORT!")
					print(p,t,s)
					shit = True
			if done or shit :
				break
		if shit :
			break

	# choose filename to store all pairwise fibre dists
	d = np.zeros(N*(N-1)*0.5, dtype=np.float )
	counter = 0
	for s1 in range(0,N):
		for s2 in range(s1+1,N):
			if dads[s1,0] == dads[s2,0] : # in the same tree			
				pdist = Get_FiberDistance_Between_RawPoints( neuron.tree[ dads[s1,0] ], dads[s1,1], dads[s2,1] )
			else:
				pdist1 = Get_FiberDistance_Between_RawPoints( neuron.tree[ dads[s1,0] ], dads[s1,1], 0 )
				pdist2 = Get_FiberDistance_Between_RawPoints( neuron.tree[ dads[s2,0] ], dads[s2,1], 0 )
				pdist = pdist1 + pdist2
			d[counter] = pdist
			counter += 1			
	np.savetxt('I:\\all_pdists.dat', d)    



#------------------------------------------------------------------------------------------



def Export_NeuronSpines( neuron, filename ):
	"""Dump 3d coordinates of all spines in neuron. Example: Export_NeuronSpines( neuron[0], 'D:\\spines.txt' )"""	
	total_spines = 0
	for t in range(0, neuron.total_trees):
		total_spines += neuron.tree[t].total_spines		
	M = numpy.zeros( (total_spines, 8) )
	sp = 0
	for t in range(0, neuron.total_trees):
		for s in range(0, neuron.tree[t].total_spines):
			M[sp,1]   = t
			M[sp,1:4] = neuron.tree[t].spine[s].P
			M[sp,4:7] = neuron.tree[t].spine[s].Q
			M[sp,7]   = neuron.tree[t].spine[s].r
			sp += 1			
	numpy.savetxt(filename, M)
	
	
	
#------------------------------------------------------------------------------------------
