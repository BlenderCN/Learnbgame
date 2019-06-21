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
# Isosurface function
# =============================================================================

import numpy as np
import time 

def generate(voxelarray, isorange, min_):
    """
    Generate isosurface

    voxelarray: 3x3 voxel volume matrix
    isorange: length 2 array [min, max] range

    Returns vertices, faces as 2D numpy array
    """
    start = time.time()
    
    verts, faces = _get_lists(voxelarray, isorange, min_)
    
    print ('Iso. Run Time: ', time.time()-start, ' s') 
    return verts, faces




def get_frac(from_value, to_value, isorange):
    if (to_value == from_value):
        ans = 0
    else:  
        ans = ((isorange[0] - from_value) / (to_value - from_value))
        
    return ans

def _append_tris(face_list, index, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10, e11, e12):
#Recursion for duplicated planes to conserve code
    if (index == 1):
        # front lower left corner
        face_list.append([e1, e4, e9])
    elif (index == 2):
        # front lower right corner
        face_list.append([e10, e2, e1])
    elif (index == 3):
        # front lower plane
        face_list.append([e2, e4, e9])
        face_list.append([e2, e9, e10])
    elif (index == 4):
        # front upper right corner
        face_list.append([e12, e3, e2])
    elif (index == 5):
        # lower left, upper right corners
        _append_tris(face_list, 1, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 4, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 6):
        # front right plane
        face_list.append([e12, e3, e1])
        face_list.append([e12, e1, e10])
    elif (index == 7):
        # Shelf including v1, v2, v3
        face_list.append([e3, e4, e12])
        face_list.append([e4, e9, e12])
        face_list.append([e12, e9, e10])
    elif (index == 8):
        # front upper left corner
        face_list.append([e3, e11, e4])
    elif (index == 9):
        # front left plane
        face_list.append([e3, e11, e9])
        face_list.append([e3, e9, e1])
    elif (index == 10):
        # upper left, lower right corners
        _append_tris(face_list, 2, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 8, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 11):
        # Shelf including v4, v1, v2
        face_list.append([e3, e11, e2])
        face_list.append([e11, e10, e2])
        face_list.append([e11, e9, e10])
    elif (index == 12):
        # front upper plane
        face_list.append([e11, e4, e12])
        face_list.append([e2, e4, e12])
    elif (index == 13):
        # Shelf including v1, v4, v3
        face_list.append([e11, e9, e12])
        face_list.append([e12, e9, e1])
        face_list.append([e12, e1, e2])
    elif (index == 14):
        # Shelf including v2, v3, v4
        face_list.append([e11, e10, e12])
        face_list.append([e11, e4, e10])
        face_list.append([e4, e1, e10])
    elif (index == 15):
        # Plane parallel to x-axis through middle
        face_list.append([e11, e9, e12])
        face_list.append([e12, e9, e10])
    elif (index == 16):
        # back lower left corner
        face_list.append([e8, e9, e5])
    elif (index == 17):
        # lower left plane
        face_list.append([e4, e1, e8])
        face_list.append([e8, e1, e5])
    elif (index == 18):
        # lower left back, lower right front corners
        _append_tris(face_list, 16, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 2, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 19):
        # Shelf including v1, v2, v5
        face_list.append([e8, e4, e2])
        face_list.append([e8, e2, e10])
        face_list.append([e8, e10, e5])
    elif (index == 20):
        # lower left back, upper right front corners
        _append_tris(face_list, 16, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 4, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 21):
        # lower left plane + upper right front corner, v1, v3, v5
        _append_tris(face_list, 17, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 4, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 22):
        # front right plane + lower left back corner, v2, v3, v5
        _append_tris(face_list, 16, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 6, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 23):
        # Rotated case 14 in the paper
        face_list.append([e3, e10, e8])
        face_list.append([e3, e10, e12])
        face_list.append([e8, e10, e5])
        face_list.append([e3, e4, e8])
    elif (index == 24):
        # upper front left, lower back left corners
        _append_tris(face_list, 16, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 8, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 25):
        # Shelf including v1, v4, v5
        face_list.append([e1, e5, e3])
        face_list.append([e3, e8, e11])
        face_list.append([e3, e5, e8])
    elif (index == 26):
        # Three isolated corners
        _append_tris(face_list, 2, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 8, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 16, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 27):
        # Full corner v1, index 9 in paper: (v1, v2, v4, v5)
        face_list.append([e11, e3, e2])
        face_list.append([e11, e2, e10])
        face_list.append([e10, e11, e8])
        face_list.append([e8, e5, e10])
    elif (index == 28):
        # upper front plane + corner v5
        _append_tris(face_list, 16, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 12, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 29):
        # special case of 11 in the paper: (v1, v3, v4, v5)
        face_list.append([e11, e5, e2])
        face_list.append([e11, e12, e2])
        face_list.append([e11, e5, e8])
        face_list.append([e2, e1, e5])
    elif (index == 30):
        # Shelf (v2, v3, v4) and lower left back corner
        _append_tris(face_list, 14, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 16, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 31):
        # Shelf: (v6, v7, v8) by inversion
        face_list.append([e11, e12, e10])
        face_list.append([e11, e8, e10])
        face_list.append([e8, e10, e5])
    elif (index == 32):
        # lower right back corner
        face_list.append([e6, e5, e10])
    elif (index == 33):
        # lower right back, lower left front corners
        _append_tris(face_list, 1, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 32, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 34):
        # lower right plane
        face_list.append([e1, e2, e5])
        face_list.append([e2, e6, e5])
    elif (index == 35):
        # Shelf: v1, v2, v6
        face_list.append([e4, e2, e6])
        face_list.append([e4, e9, e6])
        face_list.append([e6, e9, e5])
    elif (index == 36):
        # upper right front, lower right back corners
        _append_tris(face_list, 32, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 4, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 37):
        # lower left front, upper right front, lower right back corners
        _append_tris(face_list, 32, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 4, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 1, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 38):
        # Shelf: v2, v3, v6
        face_list.append([e3, e1, e5])
        face_list.append([e3, e5, e12])
        face_list.append([e12, e5, e6])
    elif (index == 39):
        # Full corner v2: (v1, v2, v3, v6)
        face_list.append([e3, e4, e5])
        face_list.append([e4, e9, e5])
        face_list.append([e3, e5, e6])
        face_list.append([e3, e12, e6])
    elif (index == 40):
        # upper left front, lower right back corners
        _append_tris(face_list, 32, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 8, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 41):
        # front left plane, lower right back corner
        _append_tris(face_list, 32, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 9, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 42):
        # lower right plane, upper front left corner
        _append_tris(face_list, 8, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 34, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 43):
        # Rotated index 11 in paper
        face_list.append([e11, e3, e9])
        face_list.append([e3, e9, e6])
        face_list.append([e3, e2, e6])
        face_list.append([e9, e5, e6])
    elif (index == 44):
        # upper front plane, lower right back corner
        _append_tris(face_list, 12, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 32, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 45):
        # Shelf: (v1, v3, v4) + lower right back corner
        _append_tris(face_list, 13, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 32, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 46):
        # Rotated case 14 in paper
        face_list.append([e4, e11, e12])
        face_list.append([e4, e12, e5])
        face_list.append([e12, e5, e6])
        face_list.append([e4, e5, e1])
    elif (index == 47):
        # Shelf: (v5, v8, v7) by inversion
        face_list.append([e11, e9, e12])
        face_list.append([e12, e9, e5])
        face_list.append([e12, e5, e6])
    elif (index == 48):
        # Back lower plane
        face_list.append([e9, e10, e6])
        face_list.append([e9, e6, e8])
    elif (index == 49):
        # Shelf: (v1, v5, v6)
        face_list.append([e4, e8, e6])
        face_list.append([e4, e6, e1])
        face_list.append([e6, e1, e10])
    elif (index == 50):
        # Shelf: (v2, v5, v6)
        face_list.append([e8, e6, e2])
        face_list.append([e8, e2, e1])
        face_list.append([e8, e9, e1])
    elif (index == 51):
        # Plane through middle of cube, parallel to x-z axis
        face_list.append([e4, e8, e2])
        face_list.append([e8, e2, e6])
    elif (index == 52):
        # Back lower plane, and front upper right corner
        _append_tris(face_list, 48, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 4, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 53):
        # Shelf (v1, v5, v6) and front upper right corner
        _append_tris(face_list, 49, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 4, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 54):
        # Rotated case 11 from paper (v2, v3, v5, v6)
        face_list.append([e1, e9, e3])
        face_list.append([e9, e3, e6])
        face_list.append([e9, e8, e6])
        face_list.append([e12, e3, e6])
    elif (index == 55):
        # Shelf: (v4, v8, v7) by inversion
        face_list.append([e4, e8, e6])
        face_list.append([e4, e6, e3])
        face_list.append([e6, e3, e12])
    elif (index == 56):
        # Back lower plane + upper left front corner
        _append_tris(face_list, 48, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 8, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 57):
        # Rotated index 14 from paper (v4, v1, v5, v6)
        face_list.append([e3, e11, e8])
        face_list.append([e3, e8, e10])
        face_list.append([e10, e6, e8])
        face_list.append([e3, e1, e10])
    elif (index == 58):
        # Shelf: (v2, v6, v5) + upper left front corner
        _append_tris(face_list, 50, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 8, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 59):
        # Shelf: (v3, v7, v8) by inversion
        face_list.append([e2, e6, e8])
        face_list.append([e8, e2, e3])
        face_list.append([e8, e3, e11])
    elif (index == 60):
        # AMBIGUOUS case: parallel planes (front upper, back lower)
        _append_tris(face_list, 48, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 12, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 61):
        # Upper back plane + lower right front corner by inversion
        _append_tris(face_list, 63, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 2, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 62):
        # Upper back plane + lower left front corner by inversion
        _append_tris(face_list, 63, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 1, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 63):
        # Upper back plane
        face_list.append([e11, e12, e6])
        face_list.append([e11, e8, e6])
    elif (index == 64):
        # Upper right back corner
        face_list.append([e12, e7, e6])
    elif (index == 65):
        # upper right back, lower left front corners
        _append_tris(face_list, 64, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 1, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 66):
        # upper right back, lower right front corners
        _append_tris(face_list, 64, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 2, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 67):
        # lower front plane + upper right back corner
        _append_tris(face_list, 64, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 3, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 68):
        # upper right plane
        face_list.append([e3, e2, e6])
        face_list.append([e3, e7, e6])
    elif (index == 69):
        # Upper right plane, lower left front corner
        _append_tris(face_list, 68, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 1, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 70):
        # Shelf: (v2, v3, v7)
        face_list.append([e1, e3, e7])
        face_list.append([e1, e10, e7])
        face_list.append([e7, e10, e6])
    elif (index == 71):
        # Rotated version of case 11 in paper (v1, v2, v3, v7)
        face_list.append([e10, e7, e4])
        face_list.append([e4, e3, e7])
        face_list.append([e10, e4, e9])
        face_list.append([e7, e10, e6])
    elif (index == 72):
        # upper left front, upper right back corners
        _append_tris(face_list, 64, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 8, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 73):
        # front left plane, upper right back corner
        _append_tris(face_list, 64, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 9, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 74):
        # Three isolated corners, exactly case 7 in paper
        _append_tris(face_list, 64, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 8, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 2, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 75):
        # Shelf: (v1, v2, v4) + upper right back corner
        _append_tris(face_list, 64, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 11, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 76):
        # Shelf: (v4, v3, v7)
        face_list.append([e4, e2, e6])
        face_list.append([e4, e11, e7])
        face_list.append([e4, e7, e6])
    elif (index == 77):
        # Rotated case 14 in paper (v1, v4, v3, v7)
        face_list.append([e11, e9, e1])
        face_list.append([e11, e1, e6])
        face_list.append([e1, e6, e2])
        face_list.append([e11, e6, e7])
    elif (index == 78):
        # Full corner v3: (v2, v3, v4, v7)
        face_list.append([e1, e4, e7])
        face_list.append([e1, e7, e6])
        face_list.append([e4, e11, e7])
        face_list.append([e1, e10, e6])
    elif (index == 79):
        # Shelf: (v6, v5, v8) by inversion
        face_list.append([e9, e11, e10])
        face_list.append([e11, e7, e10])
        face_list.append([e7, e10, e6])
    elif (index == 80):
        # lower left back, upper right back corners (v5, v7)
        _append_tris(face_list, 64, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 16, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 81):
        # lower left plane, upper right back corner
        _append_tris(face_list, 64, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 17, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 82):
        # isolated corners (v2, v5, v7)
        _append_tris(face_list, 64, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 16, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 2, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 83):
        # Shelf: (v1, v2, v5) + upper right back corner
        _append_tris(face_list, 64, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 19, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 84):
        # upper right plane, lower left back corner
        _append_tris(face_list, 16, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 68, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 85):
        # AMBIGUOUS index: upper right and lower left parallel planes
        _append_tris(face_list, 17, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 68, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 86):
        # Shelf: (v2, v3, v7) + lower left back corner
        _append_tris(face_list, 70, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 16, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 87):
        # Upper left plane + lower right back corner, by inversion
        _append_tris(face_list, 119, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 32, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 88):
        # Isolated corners v4, v5, v7
        _append_tris(face_list, 64, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 16, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 8, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 89):
        # Shelf: (v1, v4, v5) + isolated corner v7
        _append_tris(face_list, 25, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 64, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 90):
        # Four isolated corners v2, v4, v5, v7
        _append_tris(face_list, 2, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 8, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 16, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 64, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 91):
        # Three isolated corners, v3, v6, v8 by inversion
        _append_tris(face_list, 4, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 32, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 127, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 92):
        # Shelf (v4, v3, v7) + isolated corner v5
        _append_tris(face_list, 76, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 16, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 93):
        # Lower right plane + isolated corner v8 by inversion
        _append_tris(face_list, 127, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 34, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 94):
        # Isolated corners v1, v6, v8 by inversion
        _append_tris(face_list, 1, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 32, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 127, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 95):
        # Isolated corners v6, v8 by inversion
        _append_tris(face_list, 32, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 127, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 96):
        # back right plane
        face_list.append([e7, e12, e5])
        face_list.append([e5, e10, e12])
    elif (index == 97):
        # back right plane + isolated corner v1
        _append_tris(face_list, 96, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 1, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 98):
        # Shelf: (v2, v6, v7)
        face_list.append([e1, e7, e5])
        face_list.append([e7, e1, e12])
        face_list.append([e1, e12, e2])
    elif (index == 99):
        # Rotated index 14 in paper: (v1, v2, v6, v7)
        face_list.append([e9, e2, e7])
        face_list.append([e9, e2, e4])
        face_list.append([e2, e7, e12])
        face_list.append([e7, e9, e5])
    elif (index == 100):
        # Shelf: (v3, v6, v7)
        face_list.append([e3, e7, e5])
        face_list.append([e3, e5, e2])
        face_list.append([e2, e5, e10])
    elif (index == 101):
        # Shelf: (v3, v6, v7) + isolated corner v1
        _append_tris(face_list, 100, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 1, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 102):
        # Plane bisecting left-right halves of cube
        face_list.append([e1, e3, e7])
        face_list.append([e1, e7, e5])
    elif (index == 103):
        # Shelf: (v4, v5, v8) by inversion
        face_list.append([e3, e7, e5])
        face_list.append([e3, e5, e4])
        face_list.append([e4, e5, e9])
    elif (index == 104):
        # Back right plane + isolated corner v4
        _append_tris(face_list, 8, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 96, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 105):
        # AMBIGUOUS case: back right and front left planes
        _append_tris(face_list, 96, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 9, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 106):
        # Shelf: (v2, v6, v7) + isolated corner v4
        _append_tris(face_list, 98, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 8, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 107):
        # Back left plane + isolated corner v3 by inversion
        _append_tris(face_list, 4, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 111, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 108):
        # Rotated case 11 from paper: (v4, v3, v7, v6)
        face_list.append([e4, e10, e7])
        face_list.append([e4, e10, e2])
        face_list.append([e4, e11, e7])
        face_list.append([e7, e10, e5])
    elif (index == 109):
        # Back left plane + isolated corner v2 by inversion
        _append_tris(face_list, 111, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 2, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 110):
        # Shelf: (v1, v5, v8) by inversion
        face_list.append([e1, e5, e7])
        face_list.append([e1, e7, e11])
        face_list.append([e1, e11, e4])
    elif (index == 111):
        # Back left plane
        face_list.append([e11, e9, e7])
        face_list.append([e9, e7, e5])
    elif (index == 112):
        # Shelf: (v5, v6, v7)
        face_list.append([e9, e10, e12])
        face_list.append([e9, e12, e7])
        face_list.append([e9, e7, e8])
    elif (index == 113):
        # Exactly case 11 from paper: (v1, v5, v6, v7)
        face_list.append([e1, e8, e12])
        face_list.append([e1, e8, e4])
        face_list.append([e8, e7, e12])
        face_list.append([e12, e1, e10])
    elif (index == 114):
        # Full corner v6: (v2, v6, v7, v5)
        face_list.append([e1, e9, e7])
        face_list.append([e1, e7, e12])
        face_list.append([e1, e12, e2])
        face_list.append([e9, e8, e7])
    elif (index == 115):
        # Shelf: (v3, v4, v8)
        face_list.append([e2, e4, e8])
        face_list.append([e2, e12, e7])
        face_list.append([e2, e8, e7])
    elif (index == 116):
        # Rotated case 14 in paper: (v5, v6, v7, v3)
        face_list.append([e9, e2, e7])
        face_list.append([e9, e2, e10])
        face_list.append([e9, e8, e7])
        face_list.append([e2, e3, e7])
    elif (index == 117):
        # upper left plane + isolated corner v2 by inversion
        _append_tris(face_list, 2, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 119, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 118):
        # Shelf: (v1, v4, v8)
        face_list.append([e1, e3, e7])
        face_list.append([e7, e1, e8])
        face_list.append([e1, e8, e9])
    elif (index == 119):
        # Upper left plane
        face_list.append([e4, e3, e7])
        face_list.append([e4, e8, e7])
    elif (index == 120):
        # Shelf: (v5, v6, v7) + isolated corner v4
        _append_tris(face_list, 112, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 8, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 121):
        # Front right plane + isolated corner v8
        _append_tris(face_list, 6, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 127, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 122):
        # Isolated corners v1, v3, v8
        _append_tris(face_list, 1, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 4, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 127, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 123):
        # Isolated corners v3, v8
        _append_tris(face_list, 4, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 127, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 124):
        # Front lower plane + isolated corner v8
        _append_tris(face_list, 3, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 127, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 125):
        # Isolated corners v2, v8
        _append_tris(face_list, 2, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 127, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 126):
        # Isolated corners v1, v8
        _append_tris(face_list, 1, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 127, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 127):
        # Isolated corner v8
        face_list.append([e11, e7, e8])
    elif (index == 150):
        # AMBIGUOUS case: back right and front left planes
        # In these index > 127 indexs, the vertices are identical BUT
        # they are connected in the opposite fashion.
        _append_tris(face_list, 6, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 111, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 170):
        # AMBIGUOUS case: upper left and lower right planes
        # In these index > 127 indexs, the vertices are identical BUT
        # they are connected in the opposite fashion.
        _append_tris(face_list, 119, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 34, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
    elif (index == 195):
        # AMBIGUOUS case: back upper and front lower planes
        # In these index > 127 indexs, the vertices are identical BUT
        # they are connected in the opposite fashion.
        _append_tris(face_list, 63, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)
        _append_tris(face_list, 3, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10,
                     e11, e12)

    return

def _marching_cubes(voxelvolume, isorange):
    
    #Checks
    if voxelvolume.ndim != 3:
        raise ValueError("A 3D matrix required as input.")
    if voxelvolume.shape[0] < 2 or voxelvolume.shape[1] < 2 or voxelvolume.shape[2] < 2:
        raise ValueError("The 3D matrix must contain 2 or more voxels.")


    """
    ISOSURFACES via the MARCHING CUBES ALGORITHM
    Original paper by W.E.Lorensen & H.E. Cline, 1987.

    Our marching cube of 2x2x2 voxels:


               v8 ------ v7
              / |       / |        z
             /  |      /  |        ^  y
           v4 ------ v3   |        | /
            |  v5 ----|- v6        |/          (note: right handed)
            |  /      |  /          ----> x
            | /       | /
            v1 ------ v2


    CONVENTIONS:
    To differentiate from voxel index ijk, marching cube coordinates are in xyz,
    s.t. currentcoord = [x,y,z].
    x,y,z=0,0,0 refers to the voxelvalue stored in 0i,0j,0k and xyz:ijk.
    
    Right-handed convention used throughout code -
    In voxelisation, voxelvalue = voxelvolume[j,k,i] as a result of Python's ordering,
    so the voxelvalue is called here in 'voxelvolume[y,z,x]'.

    """

    #Place the first marching cube so v1 is at the bottom left of Voxel Volume [0, 0, 0]
    currentcoord = np.array([0, 0, 0]) #x, y, z

    #Calculate no of iterations needed
    no_marches = (voxelvolume.shape[0] -1)*(voxelvolume.shape[1] -1)*(voxelvolume.shape[2] -1)

    #Declaring variables before march     
    e5, e6, e7, e8 = [0,0,0], [0,0,0], [0,0,0], [0,0,0]
    face_list = []
    

    for n in range(no_marches): #begin march, starting at zero

        #Set local coordinates
        x0, y0, z0 = currentcoord[0], currentcoord[1], currentcoord[2]
        x1, y1, z1 = x0+1, y0+1, z0+1

        r0, c0, d0, r1, c1, d1 = x0, y0, z0, x1, y1, z1

        
        #Stores the Voxel Volume's value # at v1, v2, v3, v4, v5, v6, v7 & v8
        v_coord = np.array([voxelvolume[y0,z0,x0], voxelvolume[y0,z0,x1], voxelvolume[y0,z1,x1], voxelvolume[y0,z1,x0], voxelvolume[y1,z0,x0], voxelvolume[y1,z0,x1],voxelvolume[y1,z1,x1],voxelvolume[y1,z1,x0]])

        #Calculate cube index
        index=0
        for i in np.arange(8):
            if isorange[0] <= v_coord[i] :
                index = index + (2**i)

        """
        There are 2^8=256 unique vertex selection combinations.
        The first state (0) occurs when none of the vertices are within the isorange.
        The last state (255) occurs when all the vertices are within the isorange.

        By considering complementary cases, the number of states can be halved to 128 - 
        vertices left out become vertices included.
        Furthermore, by considering rotational symmetry, the number of states is reduced to 15.
        """
            
        if index!=0 and index !=255: #if a plane intersects the cube
            
            if index > 127:
                if index != 150 and index != 170 and index != 195:
                    index = 255 - index #reverse the cube
                                    
            e1=r0 + get_frac(v_coord[0], v_coord[1], isorange), c0, d0 #v1, v2
            e2=r1, c0 + get_frac(v_coord[1], v_coord[5], isorange), d0 #v2, v6
            e3=r0 + get_frac(v_coord[4], v_coord[5], isorange), c1, d0 #v5, v6
            e4=r0, c0 + get_frac(v_coord[0], v_coord[4], isorange), d0 #v1, v5                 
            e5= r0 + get_frac(v_coord[3], v_coord[2], isorange), c0, d1 #v4, v3
            e6= r1, c0 + get_frac(v_coord[2], v_coord[6], isorange), d1 #v3, v7
            e7= r0 + get_frac(v_coord[7], v_coord[6], isorange), c1, d1 #v8, v7
            e8= r0, c0 + get_frac(v_coord[3], v_coord[7], isorange), d1 #v4, v8
            e9= r0, c0, d0 + get_frac(v_coord[0], v_coord[3], isorange) #v1, v4
            e10= r1, c0, d0 + get_frac(v_coord[1], v_coord[2], isorange) #v2, v3
            e11= r0, c1, d0 + get_frac(v_coord[4], v_coord[7], isorange) #v5, v8
            e12= r1, c1, d0 + get_frac(v_coord[5], v_coord[6], isorange) #v6, v7
            
            _append_tris(face_list, index, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10, e11, e12)
            

        #Advance to the next cube
            
        if currentcoord[2] < voxelvolume.shape[1] -2: #if z is within Voxel Volume's z-dimension
            currentcoord[2] += 1 #advance z (x y z+1)
            
            #"001, 002, 003, ..."
            
        elif currentcoord[1] < voxelvolume.shape[0] -2: # then when z hits max, move to (x y+1 0)
            currentcoord[1] += 1
            currentcoord[2] =0
            
            #"010, 011, 012, 013...; 020, ..."
            
        else:
            currentcoord[0] += 1 #when both z and y hit max, move to (x+1 0 0) and repeat z and y iterations.
            currentcoord[1] = 0
            currentcoord[2] = 0
            
            #"100, 101, 102, 103...; 111, 112, 113..., 121, ...; 200, ..."

    return face_list

def _uniqueverts(tri_list,min_):
    
    #Check face data for error (ie face bigger than voxel)    
    no_tris = len(tri_list)
    
    dist1= np.zeros(no_tris)
    dist2= np.zeros(no_tris)
    dist3= np.zeros(no_tris)
    
    error_list = []
    for n in np.arange(no_tris):
        
        dist1[n] = ((tri_list[n][0][0]-tri_list[n][1][0])**2+ (tri_list[n][0][1]-tri_list[n][1][1])**2 +(tri_list[n][0][2]-tri_list[n][0][2])**2) **0.5
        dist2[n] = ((tri_list[n][0][0]-tri_list[n][2][0])**2+ (tri_list[n][0][1]-tri_list[n][2][1])**2 +(tri_list[n][0][2]-tri_list[n][2][2])**2) **0.5
        dist3[n] = ((tri_list[n][1][0]-tri_list[n][2][0])**2+ (tri_list[n][1][1]-tri_list[n][2][1])**2 +(tri_list[n][1][2]-tri_list[n][2][2])**2) **0.5
        
        if dist1[n]>1.74 or dist2[n] >1.74 or dist3[n]>1.74:        
            error_list.append(n)
        
    try:
        data_error = len(error_list)/no_tris*100
        print('Data % Error: ', data_error,'%')  
    except ZeroDivisionError:
        print()        
       
    error_list.reverse()
    
    for index in error_list:
        tri_list.pop(index)
    
    
    #Create list of unique vertices and faces   
    vert_index = {}
    vert_list = []
    face_list = []
    no_tris = len(tri_list)
    idx=0

    for i in np.arange(no_tris): #Iterate
        templist =[]

        #Parse vertices from non-degenerate triangles only
        if not ((tri_list[i][0] == tri_list[i][1]) or (tri_list[i][0] == tri_list[i][2]) or (tri_list[i][1] == tri_list[i][2])):
            for j in np.arange(3): #For each vertex within a triangle
                vert = tri_list[i][j]

                if vert not in vert_index: #check if a unique vertex is found
                    vert_index[vert] = idx
                    templist.append(idx)
                    vert_list.append(vert)
                    idx +=1
                else:
                    templist.append(vert_index[vert])
            
            templist = (int(templist[0]),int(templist[1]),int(templist[2]))
            face_list.append(templist)  
    
    #Translate vetices by min    
    vert_list = vert_list +min_             

    return vert_list, face_list


def _get_lists(voxelvolume, isorange,_min):
    """
    Return list of length-3 lists. Each sublist contains three tuples:
    (x,y,z) coords for all triangle vertices, including repeats.
    """
    raw_faces = _marching_cubes(voxelvolume, isorange)
    """
    Finds and collects unique vertices, storing as indices.
    Returns a true mesh with no degenerate faces.
    """
    verts, faces = _uniqueverts(raw_faces,_min)
    
    #Conver face data from int32 to int    
    face_int = []
    face_list = []
        
    for cc in range(len(faces)):        
        face_int = (int(faces[cc][0]),int(faces[cc][1]),int(faces[cc][2]))
        face_list.append(face_int)
        
    faces = face_list     

    return verts, faces


