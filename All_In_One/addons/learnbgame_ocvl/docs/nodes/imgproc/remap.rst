remap
=====


Functionality
-------------
Applies a generic geometrical transformation to an image.


Inputs
------
- borderMode_in – Border mode used to extrapolate pixels outside of the image, see cv::BorderTypes.
- borderValue_in – Value used in case of a constant border; by default, it equals 0.
- image_in – Input image.
- interpolation_in – Interpolation method.
- map1_in – The first map of either (x,y) points or just x values having the type CV_16SC2 , CV_32FC1 , or CV_32FC2 .
- map2_in – The second map of y values having the type CV_16UC1 , CV_32FC1 , or none (empty map if map1 is (x,y) points), respectively.


Outputs
-------
- image_out – Output image. It has the same size as map1 and the same type as src .


Locals
------


Examples
--------


