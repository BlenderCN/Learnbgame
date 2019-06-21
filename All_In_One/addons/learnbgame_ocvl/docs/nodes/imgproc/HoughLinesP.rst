HoughLinesP
===========


Functionality
-------------
Finds line segments in a binary image using the probabilistic Hough transform.


Inputs
------
- image_in – Input image.
- maxLineGap_in – Maximum allowed gap between points on the same line to link them.
- minLineLength_in – Minimum line length. Line segments shorter than that are rejected.
- rho_in – Distance resolution of the accumulator in pixels.
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


