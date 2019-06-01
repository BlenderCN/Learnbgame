warpPerspective
===============
.. image:: http://kube.pl/wp-content/uploads/2018/01/warpPerspective_01.png


Functionality
-------------
Applies a perspective transformation to an image.


Inputs
------
- M_in – Transformation matrix.
- borderMode_in – Pixel extrapolation method (BORDER_CONSTANT or BORDER_REPLICATE).
- borderValue_in – Value used in case of a constant border; by default, it equals 0.
- dsize_in – Size of the output image.
- flags_in – INTER_LINEAR, WARP_FILL_OUTLIERS
- image_in – Image input.


Outputs
-------
- image_out – Image output.


Locals
------


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/warpPerspective_11.png
.. image:: http://kube.pl/wp-content/uploads/2018/01/warpPerspective_12.png


