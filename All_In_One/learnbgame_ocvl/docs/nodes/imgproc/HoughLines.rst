HoughLines
==========


Functionality
-------------
Finds lines in a binary image using the standard Hough transform.


Inputs
------
- image_in – Input image.
- max_theta_in – For standard and multi-scale Hough transform, maximum angle to check for lines.
- min_theta_in – For standard and multi-scale Hough transform, minimum angle to check for lines.
- rho_in – Distance resolution of the accumulator in pixels.
- srn_in – For the multi-scale Hough transform, it is a divisor for the distance resolution rho.
- stn_in – For the multi-scale Hough transform, it is a divisor for the distance resolution theta.
- theta_in – Angle resolution of the accumulator in radians.
- threshold_in – Accumulator threshold parameter.


Outputs
-------
- image_out – Output image.
- lines_out – Output vector of lines.


Locals
------
- loc_output_mode – Output mode.


Examples
--------


