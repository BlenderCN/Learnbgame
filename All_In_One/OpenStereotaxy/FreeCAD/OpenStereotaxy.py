# -*- coding: utf-8 -*-
"""
===================== OpenStereotaxy module for FreeCAD =======================
This Python module for FreeCAD allows the user to calculate the chamber-centered
coordinates of the target structure(s). Based on this data, the module will
generate surface meshes (exported in .stl format ready for 3D-printing) of the
following custom parts:
    1) a drill guide for performing craniotomy
    2) a guide tube guide grid
    3) a microdrive system

Written by Aidan Murphy, PhD (murphyap@nih.gov)
"""

import numpy as np
from scipy.io import loadmat


# ================= Load data from Slicer files
def LoadChamberCoords(TransformFile, TargetsFile):

    x                   = loadmat(TransformFile, squeeze_me=True)   # Load transform matrix
    data                = x['AffineTransform_double_3_3']
    TransformMatrix     = np.reshape(data[0:9], [3,3])              # Reshape array
    TransformMatrix     = np.append(TransformMatrix, [0,0,0,1])
    Ras2lps                     = [-1,-1,1,1]
    Tform      	                = TransformMatrix.*Ras2lps          # Convert transfrom matrix from LPS to RAS
    fid     = open(TargetsFile, 'r')                                # Load target coordinate data
    for line in fid.readlines()[3:]:                                # For each target...
        Coords                  = line.split(",")
        Coords(f).Name          = Coords[11]
        Coords(f).Description   = Coords[12]
        Coords(f).TformFile     = TransformFile
        Coords(f).TformMatrix   = Tform
        Coords(f).XYZ_RAS       = Coords[1:4]                       # Get the raw MR-volume coordinates
        XYZ_Chamber             = Tform*[Coords(f).XYZ_RAS,1]'      # Apply transform
        ChamberCoords[n]        = -XYZ_Chamber(1:3)'                # Return chamber-centered coordinates

    return ChamberCoords

# ================= Move electrode holes
def UpdateHoleLocations(ChamberCoords):





TransformFile   = '/Volumes/RAWDATA/murphya/MRI/StevieRay/Surgery2_Plan/ManualTransform_LH_V2.mat'
TargetsFile     = '/Volumes/RAWDATA/murphya/MRI/StevieRay/Surgery2_Plan/SurgicalTargets.fcsv'

ChamberCoords   = LoadChamberCoords(TransformFile, TargetsFile)
