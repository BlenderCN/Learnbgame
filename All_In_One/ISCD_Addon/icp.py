"""
Python implementation of 3D iterative closest point. Includes an SVD-based least-squared best-fit algorithm.
https://github.com/ClayFlannigan/icp
"""
import numpy as np
from scipy.spatial.distance import cdist
import os

def best_fit_transform(A, B):
    '''
    Calculates the least-squares best-fit transform between corresponding 3D points A->B
    Input:
      A: Nx3 numpy array of corresponding 3D points
      B: Nx3 numpy array of corresponding 3D points
    Returns:
      T: 4x4 homogeneous transformation matrix
      R: 3x3 rotation matrix
      t: 3x1 column vector
    '''

    assert len(A) == len(B)

    # translate points to their centroids
    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)
    AA = A - centroid_A
    BB = B - centroid_B

    # rotation matrix
    H = np.dot(AA.T, BB)
    U, S, Vt = np.linalg.svd(H)
    R = np.dot(Vt.T, U.T)

    # special reflection case
    if np.linalg.det(R) < 0:
       Vt[2,:] *= -1
       R = np.dot(Vt.T, U.T)

    # translation
    t = centroid_B.T - np.dot(R,centroid_A.T)

    # homogeneous transformation
    T = np.identity(4)
    T[0:3, 0:3] = R
    T[0:3, 3] = t

    return T, R, t

def nearest_neighbor(src, dst):
    '''
    Find the nearest (Euclidean) neighbor in dst for each point in src
    Input:
        src: Nx3 array of points
        dst: Nx3 array of points
    Output:
        distances: Euclidean distances of the nearest neighbor
        indices: dst indices of the nearest neighbor
    '''

    all_dists = cdist(src, dst, 'euclidean')
    indices = all_dists.argmin(axis=1)
    distances = all_dists[np.arange(all_dists.shape[0]), indices]
    return distances, indices

def icp(A, B, init_pose=None, max_iterations=100, tolerance=0.001):
    '''
    The Iterative Closest Point method
    Input:
        A: Nx3 numpy array of source 3D points
        B: Nx3 numpy array of destination 3D point
        init_pose: 4x4 homogeneous transformation
        max_iterations: exit algorithm after max_iterations
        tolerance: convergence criteria
    Output:
        T: final homogeneous transformation
        distances: Euclidean distances (errors) of the nearest neighbor
    '''
    A = np.array(A)
    B = np.array(B)
    # make points homogeneous, copy them so as to maintain the originals
    src = np.ones((4,A.shape[0]))
    dst = np.ones((4,B.shape[0]))
    src[0:3,:] = np.copy(A.T)
    dst[0:3,:] = np.copy(B.T)

    # apply the initial pose estimation
    if init_pose is not None:
        src = np.dot(init_pose, src)

    prev_error = 0

    for i in range(max_iterations):
        # find the nearest neighbours between the current source and destination points
        distances, indices = nearest_neighbor(src[0:3,:].T, dst[0:3,:].T)

        # compute the transformation between the current source and nearest destination points
        T,R,t = best_fit_transform(src[0:3,:].T, dst[0:3,indices].T)

        # update the current source
        src = np.dot(T, src)

        # check error
        mean_error = np.sum(distances) / distances.size
        print("Iteration", i+1, ", error = ", mean_error)

        if abs(prev_error-mean_error) < tolerance:
            break
        prev_error = mean_error


    # calculate final transformation
    T,rot,trans = best_fit_transform(A, src[0:3,:].T)
    return T


def align_data(d, ref, offset=None, write=False):
    aD = np.zeros((len(d),len(d[0]),3))
    for i,x in enumerate(d):
        if offset==None:
            T,D = icp(x, ref)
            aD[i] = np.array( [ np.dot( T,np.append(pt,[1]) )[:3] for pt in x])
        else:
            T,D = icp(offset+x, offset+ref)
            aD[i] = np.array( [ np.dot( T,np.append(pt,[1]) )[:3] for pt in offset+x]) - np.array(offset)
        if write:
            with open("data_aligned/MassDispAlign."+str(i+1)+".sol.txt","w") as f:
                for z in aD[i]:
                    f.write(str(z[0]) + " " + str(z[1]) + " " + str(z[2]) + "\n")
    return aD
