bilateralFilter
===============
.. image:: http://kube.pl/wp-content/uploads/2018/01/bilateralFilter_01.png


Functionality
-------------
Applies the bilateral filter to an image.


Inputs
------
- borderType_in – Border mode used to extrapolate pixels outside of the image, see cv::BorderTypes.
- d_in – Diameter of each pixel neighborhood that is used during filtering. If it is non-positive, it is computed from sigmaSpace.
- sigmaColor_in – Filter sigma in the color space.
- sigmaSpace_in – Filter sigma in the coordinate space.


Outputs
-------
- image_out – Output image.


Locals
------


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/bilateralFilter_11.png


