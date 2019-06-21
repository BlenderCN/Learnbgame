# Authors: Paulo de Castro Aguiar
#          Eduardo Conde-Sousa
# Date:    May 2015
# email:   pauloaguiar@ineb.up.pt

"""Functions to read and write reconstruction data in SWC format"""

from myconfig import *
from mytools import *

import numpy
from DataContainers import *
from DrawingFun import Draw_Tree_Mesh

#------------------------------------------------------------------------------------------


def Read_Tree_SWC( filename ) :
	"""
	Loads tree morphology file in SWC format. Returns a NEURON object with a single TREE with the loaded data.
	Example:
	nrn = Read_Tree_SWC( 'I:\\\\axon.swc' )
	Draw_Tree_Mesh( nrn, 0, [], 5 ) # draws the single tree, tree 0, in layer 5
	"""
	
	swc = numpy.loadtxt(filename, comments='#')
	
	nrn = NEURON()
	tree = TREE()
	
	ppid_list = []
	ptype = 'standard'
	
	# skip points which are neither axon or dend
	p0 = 0
	while swc[p0][1] != 2 and swc[p0][1] != 3 :
		p0 += 1
	
	# go through all points in SWC data
	offset = int( swc[0][0] )
	first_root_flag = True
	for p in range(p0, swc.shape[0]) :
		P = swc[p][2:5].tolist()
		r = swc[p][5]
		ppid = int( swc[p][6] ) - offset - p0
		if ppid < 0 :
			if first_root_flag :
				ppid = -1
				first_root_flag = False
			else : # this would not be needed if swc were indeed of a single tree
				ppid = 0
				print("Careful, this SWC file contains more than one tree.")
		ppid_list.append( ppid )
		tree.point.append(       POINT( P=P, r=r, n=None, ppid=ppid, level=None, ptype=ptype, active=1) )
		tree.rawpoint.append( RAWPOINT( P=P, r=r        , ppid=ppid, level=None, ptype=ptype, contact=None ) )
	
	tree.total_points    = len(ppid_list)
	tree.total_rawpoints = len(ppid_list)
	
	# identify point types
	for p in range(0, len(ppid_list)) :
		n = ppid_list.count(p)
		if n == 0 :
			ptype = 'endpoint'
		elif n == 1 :
			ptype = 'standard'
		else :
			ptype = 'node'
		tree.point[p].ptype = ptype
		tree.rawpoint[p].ptype = ptype	
	
	# calculate normals
	for p in range(1, tree.total_points) :
		n = numpy.array( tree.point[p].P ) - numpy.array( tree.point[ tree.point[p].ppid ].P )
		norm  = numpy.linalg.norm( n )
		if norm > 0 :
			tree.point[p].n = n / numpy.linalg.norm( n )
		else :
			print('overlaping point = ', p)
			if p > 1 :
				tree.point[p].n = tree.point[p-1].n
			else :
				tree.point[p].n = [0, 0, 1]
	
	tree.point[0].n = tree.point[1].n
	tree.point[0].ppid = -1
	
	nrn.tree.append( tree )
	nrn.total_trees = 1
	
	#Draw_Tree_Mesh( nrn, 0, [], 10 )
	
	return nrn


#------------------------------------------------------------------------------------------


def Write_Tree_SWC( tree, filename ) :
	"""
	Writes a neuron tree morphology (rawpoints) to file in SWC format.
	Example:
	Write_Tree_SWC( neuron[0].tree[0], 'I:\\\\axon.swc')
	"""
	
	fout = open(filename,"w")
	fout.write("# Exported tree: %s \n" % ( tree.type ) )
	fout.write("# This file was generated using py3DN\n")
	fout.write("# http://sourceforge.net/projects/py3dn/\n")
	fout.write("# P Aguiar, M Sousa, P Szucs (2013) Neuroinformatics 11 (4), 393-403\n\n" )	
	
	if tree.type == 'Axon' or tree.type == 'axon' :
		tree_type = 2 #axon
	else :
		tree_type = 3 #dend
	
	# go through all points in tree
	
	for pid in range(0, tree.total_rawpoints) :
		p = tree.rawpoint[pid]				
		ppid = p.ppid
		# instead of starting with pid=0, start with pid=1 (more common in swc files)
		if ppid != -1 :
			ppid += 1
		fout.write("%d %d %f %f %f %f %d\n" % ( pid+1, tree_type, p.P[0], p.P[1], p.P[2], p.r, p.ppid ) )
	
	fout.close()


#------------------------------------------------------------------------------------------


def Write_AllTrees_SWC( neuron, directory ) :
	"""Writes the morphology (rawpoints) of all trees in a neuron to files in SWC format (each tree in a file).
	Example:
	Write_AllTrees_SWC( neuron[0], 'I:\\MyOutputData\\')"""
	
	for tid in range( 0, neuron.total_trees ) :
		Write_Tree_SWC( neuron.tree[tid], directory+'\\Tree_'+str(tid)+'.swc' )

