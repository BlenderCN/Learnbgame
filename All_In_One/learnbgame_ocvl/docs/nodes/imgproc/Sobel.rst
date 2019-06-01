Sobel
=====
.. image:: http://kube.pl/wp-content/uploads/2018/01/Sobel_01.png


Functionality
-------------
Calculates the first, second, third, or mixed image derivatives using an extended Sobel operator.


Inputs
------
- borderType_in – Pixel extrapolation method, see cv::BorderTypes.
- ddepth_in – Desired depth of the destination image.
- delta_in – Optional delta value that is added to the results prior to storing them in dst.
- dx_in – Order of the derivative x.
- dy_in – Order of the derivative y.
- image_in – Input image.
- ksize_in – Aperture size used to compute the second-derivative filters.
- scale_in – Optional scale factor for the computed Laplacian values.


Outputs
-------
- image_out – Output image.


Locals
------


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/Sobel_11.png
.. image:: http://kube.pl/wp-content/uploads/2018/01/Sobel_12.png
.. image:: http://kube.pl/wp-content/uploads/2018/01/Sobel_13.png
.. image:: http://kube.pl/wp-content/uploads/2018/01/Sobel_14.png


