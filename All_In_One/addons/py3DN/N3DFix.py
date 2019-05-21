# N3DFix - automatic removal of swelling artifacts in neuronal 2D/3D reconstructions
# last update: Mar 2016
# VERSION 2.0
#
# Authors: Paulo de Castro Aguiar
#          Eduardo Conde-Sousa
# Date:    Mar 2016
# email:   pauloaguiar@ineb.up.pt
#
# N3DFix v2.0 is described in the following manuscript (UNDER REVIEW)
# Conde-Sousa E, Szucs P, Peng H, Aguiar P - Neuroinformatics, 2016
#
#    Disclaimer
#    ----------
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You can view a copy of the GNU General Public License at
#    <http://www.gnu.org/licenses/>.


"""N3DFix - automatic removal of swelling artifacts from neuronal 2D/3D reconstructions
N3DFix v2.0 is described in the following manuscript (UNDER REVIEW)
Conde-Sousa E, Szucs P, Peng H, Aguiar P - Neuroinformatics, 2016"""


from myconfig import *
from DrawingFun import *

import numpy



#------------------------------------------------------------------------------------------



def Split_Tree2DendSections( tree ) :
	"""Split a tree into a list of dendritic sections (set of points between nodes, or endpoints) - for compatibility with NEURON simulation environment sections (so that N3DFix works the same way in all implementations).
	Parameters
	----------
	
	Returns
	-------
	
	Examples
	--------
	dend_sections = Split_Tree2DendSections( neuron[0].tree[1] )"""
	
	# 1) Create list with all nodes and endpoints
	nodes = []
	for pid in range(0,tree.total_rawpoints) :
		if tree.rawpoint[pid].ptype == 'node' or tree.rawpoint[pid].ptype == 'endpoint':
			nodes.append(pid)
			
	# 2) go through all points and create dends lists
	dend_sections = []
	dsection = []
	for pid in range(0,tree.total_rawpoints) :
		rawpoint = tree.rawpoint[pid]
		dsection.append( [ pid, rawpoint.P[0], rawpoint.P[1], rawpoint.P[2], rawpoint.r ] )
		if pid in nodes :
			if len( dend_sections ) > 0 :
				# same as NEURON: 1st point in a dendritic section is a copy of the previous node but with the radius of the next point
				rawppoint = tree.rawpoint[ round( dsection[0][0] ) ]
				dsection.insert(0, [ rawppoint.ppid , rawppoint.P[0], rawppoint.P[1], rawppoint.P[2], rawppoint.r ] ) # r will be replaced in next line
				dsection[0][4] = dsection[1][4] # just as NEURON, radius of 1st point (node) is the same as 2nd point

			dend_sections.append( dsection );
			dsection = []
	
	return dend_sections



#------------------------------------------------------------------------------------------



def Calculate_Baseline( arc, r ) :
	"""
	Calculates 2rd order polyfit to the radius profile.
	N3DFix does not use this to smooth the fibera radius profile!
	Instead it is used to define the baseline profile which is then used to detect swellings.
	Parameters
	----------
	arc : 1D array with fiber distances [um]
	r : 1D array with radius profile [um]
	
	Returns
	-------
	out : baseline and outliers concatenated
	
	Examples
	--------
	out = Calculate_Baseline( [0, 1, 2, 3, 4, 5, 6, 7], [ 3, 2, 2, 1.5, 1, 1, 0.5 ] )
	"""
	
	polyfit_order = 2
	w = numpy.ones( len(r) )
	
	# ADJUST THE CUTOFF IF NEEDED
	outlier_cutoff = 3.0
	
	# Median Absolute Deviation to find possible outliers
	# http://eurekastatistics.com/using-the-median-absolute-deviation-to-find-outliers
	mad = numpy.median( numpy.abs( r - numpy.median(r) ) )
	
	# let fitting weights exclude the outliers
	if mad > 1.0e-6 : 
		r_mad = numpy.abs( r - numpy.median(r) ) / mad
		Loutliers = r_mad > outlier_cutoff
		w[ Loutliers ] = 0
	else :
		# will end up here if more than 50% of the data points have the same value; and it's not that rare
		# add 1% noise to r profile, and recalculate MAD
		r_noisy = r + 0.01 * r.min() * numpy.random.uniform(-1.0,1.0,len(r))
		mad = numpy.median( numpy.abs( r_noisy - numpy.median(r_noisy) ) )
		if mad > 1.0e-6 : 
			r_mad = numpy.abs( r_noisy - numpy.median(r_noisy) ) / mad
			Loutliers = r_mad > outlier_cutoff
			w[ Loutliers ] = 0
		else :
			# not able to remove outliers using MAD
			m = numpy.median(r)
			s = numpy.std(r)
			Loutliers = numpy.abs(r-m) > 2.0*s
			w[ Loutliers ] = 0
	
	# get baseline from 2nd order polyfit
	if len(r) - w.sum() > 2 :
		coef = numpy.polyfit( arc, r, polyfit_order, w=w )
		r_fit = numpy.poly1d( coef )
		baseline = r_fit( arc )
	else :
		# problematic section (usually consequence of very few points) - can't use 2nd order polyfit
		# use r profile's median for uniform baseline
		baseline = numpy.median(r) * numpy.ones( len(r) )
	
	#do not allow the baseline to go below the minimal radius, or above maximal radius - truncate
	rmin = r.min()
	baseline[ baseline < rmin ] = rmin
	rmax = r.max()
	baseline[ baseline > rmax ] = rmax	
	
	return [baseline, 1-w]



#------------------------------------------------------------------------------------------



def N3DFix_Tree( nrn, tid, bump_rnorm = 0.56, rmin = 0.1, DoNodes = True, filename = 'C:\\Users\\Paulo\\Desktop\\N3DFix_tree.txt' ) :
	"""
	Algorithm for swelling artifact removal
	Parameters
	----------
	nrn: NEURON object
	tid: tree id
	bump_rnorm: normalized radius trigger - minimal r normalized to baseline [1]
	rmin: minimum radius, in micrometers and larger than 1.0e-6, used to correct points with "zero" radius [um]
	DoNodes: boolean for swelling artifact removal in nodes
	filename: complete name and location of file to store output tree with corrections report
	
	Returns
	-------
	Updates "points" values in the nrn NEURON object ("rawpoints" are left unchanged!). Use the "Draw 3D Reconstruction" and the "base layer" buttons in Py3DN GUI interface to draw the corrected tree
	
	Examples
	--------
	N3DFix_Tree( neuron[0], 1, bump_rnorm = 0.56, rmin = 0.1, DoNodes = True, filename = 'C:\\\\Users\\\\Paulo\\\\Desktop\\\\N3DFix_tree.txt' )
	After issuing the command use the GUI button 'Draw 3D Reconstruction' to visualize the corrections
	"""
	
	# Set Parameters
	bump_slope = 0.10 # slope trigger - not a sensitive parameter; basically okay as long as bump_slope > 0.01 (detect non-horizontal segments)
	
	tree = nrn.tree[tid]
	
	fout = open(filename,"w")
	foo = fout.write("# N3DFix ")
	foo = fout.write("dsection arc[um] r[um] r_new[um] slope rnorm, baseline[um] outlier_flag correction_flag\n")
	
	# Split tree into dendritic sections (portions between bifurcation nodes)
	dend_sections = Split_Tree2DendSections( tree )
	
	# Go through all dend_sections
	# ----------------------------
	for ds in range(0, len(dend_sections) ) :
		
		dsection = numpy.array( dend_sections[ds] )
		Npoints = len( dsection )
		
		# Correct points with "zero" radius ( r < rmin )
		r = dsection[:,4]
		r[ r < rmin ] = rmin

		if Npoints <= 2 : # dodgy reconstruction file with consecutive node points
			print("dodgy section with 2 or less points, ds =", ds, " in tree tid = ", tid )
			continue # jump to next dsection; don't do anything else beside rmin correction			
		
		# Calculate fibre/arc distance of all points in dsection
		arc = numpy.zeros( Npoints )
		for p in range(1, Npoints ) :
			dist = dsection[p][1:4] - dsection[p-1][1:4]
			dist = numpy.linalg.norm( dist )
			arc[p] = dist
		
		arc = arc.cumsum()
		
		# CALCULATE TRIGGERS
		# Trigger 1: r, baseline radius
		res_baseline_outliers = Calculate_Baseline( arc, r )
		baseline = res_baseline_outliers[0]
		outliers = res_baseline_outliers[1]
		
		# Trigger 2: delta_r / delta_x, slope
		slope = numpy.zeros( Npoints )
		# Trigger 3: rnorm = r / baseline, normalized radius
		rnorm = numpy.zeros( Npoints )
		for p in range(1, Npoints ) : # slope and rchange are not defined for p=0
			# rnorm
			rnorm[p] = r[p] / baseline[p]
			# slope
			if abs( arc[p] - arc[p-1] ) < 1.0e-6 :
				if abs( r[p] - r[p-1] ) < 1.0e-6 :
					slope[p] = 0.0 # ATENTION!!! equal points are not removed! slope is set to zero! 
				else :
					sign = ( r[p] - r[p-1] ) / abs( r[p] - r[p-1] )
					slope[p] = 2.0 * sign * bump_slope # ATENTION!!! same (x,y,z) but abrupt change in r! give the slope trigger
			else : # normal case
				slope[p] = ( r[p] - r[p-1] ) / ( arc[p] - arc[p-1] )
		
		# Identify locations to correct
		signal_cor = numpy.ones( Npoints, dtype=numpy.int8 )
		signal_cor[0] = 0
		for p in range(1, Npoints ) :
			if abs( slope[p] ) < bump_slope and abs( rnorm[p] - 1 ) < bump_rnorm :
				signal_cor[p] = 0
		
		# Correct points using linear interpolation, whenever necessary
		r_new = r.copy()
		p = 1
		while p < Npoints :
			# search for sequence of points to correct
			if signal_cor[p] == 1 :
				p1 = p - 1	# start point
				p += 1
				while p < Npoints and signal_cor[p] == 1 :
					p += 1
				#p2 = min( p, Npoints - 1 )	# stop point
				p2 = p - 1	# stop point (last point with signal_cor = 1)
				delta_x = arc[p2] - arc[p1]
				if abs( delta_x ) > 1.0e-6 :
					# this is a bump; remove it using linear interpolation: r = m*x + r0
					
					# choose r0 according to the location of p1
					if p1 != 0 :
						# p1 is not a node
						r0 = r[p1]
					else : # p1 is a node
						if round( dsection[p1][0] ) != 0 and DoNodes == True :
							# p1 is not the 1st point in tree - go upstream and check radius profiles in the father section
							ppid = tree.rawpoint[ int( dsection[0][0] ) ].ppid
							r_father = tree.rawpoint[ppid].r							
							r0 = r_father
							if r_father > baseline[p1] : # chose this option if it generates less steepness at edge
								r0 = baseline[p1]
						else :
							# p1 is either the 1st point in tree or DoNodes is False
							r0 = r[p1]
					
					# now choose m according to the location of p2
					if p2 != Npoints-1 :
						# p2 is not a node
						m  = ( r[p2] - r0 ) / delta_x
					else : # p2 is a node
						# force end radius to baseline level (which has the outliers removed)
						m  = ( baseline[p2] - r0 ) / delta_x
						if m > bump_slope or abs( r[p2]/baseline[p2] - 1.0 ) > bump_rnorm :	# avoid high slopes at the edges
							m  = ( numpy.median(r) - r0 ) / delta_x
					
					# INTERPOLATE swelling artifact using linear interpolation: r = m*x + r0
					for i in range(p1, p2+1) :
						r_new[i] = m * ( arc[i] - arc[p1] ) + r0						
				
				else : # delta_x is below 1.0e-6 
					for i in range(p1+1, p2+1) : # assume that problematic point is p2
						r_new[i] = baseline[i] # alternatively: r_new[i] = 0.5 * ( r[p1] + r[p2] )
			
			else :
				p += 1
		
		for p in range(0, Npoints ) :
			# signal_cor identify regions to correct, but is not equivalent to which points have been modified
			correction_flag = 0
			if abs( r[p] - r_new[p] ) > 1.0e-6 :
				correction_flag = 1
			foo = fout.write("%d %f %f %f %f %f %f %d %d\n" % ( ds, arc[p], r[p], r_new[p], slope[p], rnorm[p], baseline[p], outliers[p], correction_flag  ) )
			tree.point[ int( dsection[p][0] ) ].r = r_new[p]
	
	fout.close()



#------------------------------------------------------------------------------------------



def N3DFix_Neuron( nrn, bump_rnorm = 0.56, rmin = 0.1, DoNodes = True, directory = 'C:\\Users\\Paulo\\Desktop\\N3DFix_output' ) :
	"""
	Algorithm for swelling artifact removal
	Parameters
	----------
	nrn: NEURON object
	tid: tree id
	bump_rnorm: normalized radius trigger - minimal r normalized to baseline [%]
	rmin: minimum radius, in micrometers and larger than 1.0e-6, used to correct points with "zero" radius [um]
	DoNodes: boolean for swelling artifact removal in nodes
	directory: location store output trees
	
	Returns
	-------
	Updates "points" values in the nrn NEURON object ("rawpoints" are left unchanged). Use the "Draw 3D Reconstruction" and the "base layer" buttons in Py3DN GUI interface to draw the corrected neuron	
	
	Examples
	--------
	N3DFix_Neuron( neuron[0], bump_rnorm = 0.56, rmin = 0.1, DoNodes = True, directory = 'C:\\Users\\Paulo\\Desktop\\N3DFix_output' )
	After issuing the command use the GUI button 'Draw 3D Reconstruction' to visualize the corrections
	"""	
	
	for tid in range( 1, nrn.total_trees ) :
		print('\n\nTaking care of tree =', tid,'with label', nrn.tree[tid].type)
		N3DFix_Tree( nrn, tid, bump_rnorm, rmin, DoNodes, directory+'\\N3DFix_tree_'+str(tid)+'.txt' )



#------------------------------------------------------------------------------------------


