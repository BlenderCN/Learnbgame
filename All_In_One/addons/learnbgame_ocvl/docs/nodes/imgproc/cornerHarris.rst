cornerHarris
============
.. image:: http://kube.pl/wp-content/uploads/2018/01/cornerHarris_01.png


Functionality
-------------
Harris corner detector.


Inputs
------
- blockSize_in – Neighborhood size (see the details on cornerEigenValsAndVecs ).
- borderType_in – Pixel extrapolation method. See cv::BorderTypes.
- image_in – Input single-channel 8-bit or floating-point image.
- k_in – Harris detector free parameter. See the formula below.
- ksize_in – Aperture parameter for the Sobel operator.


Outputs
-------
- image_out – Image to store the Harris detector responses.


Locals
------


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/cornerHarris_11.png


