# =============================================================================
# (C) Copyright 2014
# Australian Centre for Microscopy & Microanalysis
# The University of Sydney
# =============================================================================
# File:   analysis/voxelisation.py
# Date:   2014-11-05
# Author: Clara Tan
#
# Description:
# Voxelisation function
# =============================================================================

import numpy as np
import time


def voxelise(coords, bin=1):
            
    """
    Voxelise the data in XYZ and return the volume in each voxel
    as a 3D matrix of Ni x Nj x Nk.
    
    Input - 'coords': The pointcloud as [x1 y1 z1; x2 y2 z2; ...] where each row is
    the xyz coordinate of each point
          - 'bin'   : Bin (division) size in nanometres. Must be greater than
          or equal to the smallest measurable division of XYZ (ie: one atom
          cannot be in two voxels)
    
    Output - 'voxelarray': Voxelized pointcloud as a 3D matrix, tallying the number of
    points per voxel (bin) across the volume of the pointcloud
    """
    start = time.time()        
    
    if coords.shape[1] != 3:
        raise ValueError("voxelisation.generate: Positions not entered as columns X, Y, Z.")
    
    # Calculate min, max and range of XYZ
    min_ = np.empty(3)
    max_ = np.empty(3)
    range_ = np.empty(3)
    
    for i in np.arange(3):
        min_[i] = np.nanmin(coords[:,i])
        max_[i] = np.nanmax(coords[:,i])
        range_[i] = max_[i] - min_[i]
    
    # Calculate the number of voxels in IJK via rounding range in XYZ up
    # to an integer value
    N = np.zeros(3)
    for x in np.arange(3):
        N[x] = (range_[x]//bin) + 1 # IJK
    
    
    # Create the voxel volume (3D matrix)
    voxelarray = np.zeros((N[0], N[2], N[1]))
    
    #Calculate for each cordinate which voxel it belongs to and store in a n x 3 matrix
    #Then iterate through the voxelid and increase count of each respective voxel
    
    voxelID = ((coords-min_)// bin)
    voxelID = voxelID.astype(int)
    
    for record in np.arange(coords.shape[0]):
                          
            voxelarray[voxelID[record,0],voxelID[record,2], voxelID[record,1]] = voxelarray[voxelID[record,0], voxelID[record,2], voxelID[record,1]] +1
          
    print ('Min\\Max Voxel value: ',np.min(voxelarray),'\\',np.max(voxelarray))
    print ('Vox. Run Time: ', time.time()-start, ' s') 
    print ()
        
    return voxelarray, min_
