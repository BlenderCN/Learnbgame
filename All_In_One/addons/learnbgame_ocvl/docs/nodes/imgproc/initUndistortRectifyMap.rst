initUndistortRectifyMap
=======================


Functionality
-------------
Computes the undistortion and rectification transformation map.


Inputs
------
- R_in – Optional rectification transformation in the object space (3x3 matrix). R1 or R2 , computed by stereoRectify() can be passed here.
- cameraMatrix_in – Input camera matrix A
- distCoeffs_in – Input vector of distortion coefficients (k_1, k_2, p_1, p_2[, k_3[, k_4, k_5, k_6]]) of 4, 5, or 8 elements. If the vector is NULL/empty, the zero distortion coefficients are assumed.
- m1type_in – Type of the first output map that can be CV_32FC1 or CV_16SC2.
- size_in – Undistorted image size.


Outputs
-------
- map1_out – First output map
- map2_out – Second output map


Locals
------


Examples
--------


