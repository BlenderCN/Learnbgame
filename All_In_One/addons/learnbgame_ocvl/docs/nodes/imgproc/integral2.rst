integral2
=========


Functionality
-------------
Calculates the integral of an image.


Inputs
------
- image_in – Input image as W x H, 8-bit or floating-point (32f or 64f).
- sdepth_in – Desired depth of the integral and the tilted integral images, CV_32S, CV_32F, or CV_64F.
- sqdepth_in – Desired depth of the integral and the tilted integral images, CV_32S, CV_32F, or CV_64F.


Outputs
-------
- sqsum_out – integral image for squared pixel values; it is (W+1) x (H+1), double-precision floating-point (64f) array.
- sum_out – Integral image as (W+1) x (H+1) , 32-bit integer or floating-point (32f or 64f).


Locals
------


Examples
--------


