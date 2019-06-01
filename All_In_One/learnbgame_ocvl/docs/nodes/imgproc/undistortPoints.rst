undistortPoints
===============


Functionality
-------------
Computes the ideal point coordinates from the observed point coordinates.


Inputs
------
- P_in – New camera matrix (3x3) or new projection matrix (3x4). P1 or P2 computed by stereoRectify() can be passed here. If the matrix is empty, the identity new camera matrix is used.
- R_in – Rectification transformation in the object space (3x3 matrix). R1 or R2 computed by stereoRectify() can be passed here. If the matrix is empty, the identity transformation is used.
- cameraMatrix_in – Camera matrix
- distCoeffs_in – Input vector of distortion coefficients (k_1, k_2, p_1, p_2[, k_3[, k_4, k_5, k_6]]) of 4, 5, or 8 elements.
- src_in – Observed point coordinates, 1xN or Nx1 2-channel (CV_32FC2 or CV_64FC2).


Outputs
-------
- dst_out – Output ideal point coordinates after undistortion and reverse perspective transformation. If matrix P is identity or omitted, dst will contain normalized point coordinates.


Locals
------


Examples
--------


