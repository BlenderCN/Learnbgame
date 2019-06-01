undistort
=========


Functionality
-------------
Transforms an image to compensate for lens distortion.


Inputs
------
- cameraMatrix_in – Input camera matrix
- distCoeffs_in – Input vector of distortion coefficients (k_1, k_2, p_1, p_2[, k_3[, k_4, k_5, k_6]]) of 4, 5, or 8 elements.
- image_in – Input (distorted) image.
- newCameraMatrix_in – Camera matrix of the distorted image. By default, it is the same as cameraMatrix but you may additionally scale and shift the result by using a different matrix.


Outputs
-------
- image_out – Output (corrected) image.


Locals
------


Examples
--------


