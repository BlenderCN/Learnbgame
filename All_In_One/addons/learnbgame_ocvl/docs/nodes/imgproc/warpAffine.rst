warpAffine
==========
.. image:: http://kube.pl/wp-content/uploads/2018/01/warpAffine_01.png


Functionality
-------------
Applies an affine transformation to an image.


Inputs
------
- M_in – Transformation matrix.
- borderMode_in – Border mode used to extrapolate pixels outside of the image, see cv::BorderTypes
- borderValue_in – Border mode used to extrapolate pixels outside of the image, see cv::BorderTypes
- dsize_in – Size of the output image.
- flags_in – INTER_LINEAR, INTER_NEAREST, WARP_INVERSE_MAP
- image_in – Input image.


Outputs
-------
- image_out – Output image.


Locals
------


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/warpAffine_11.png


