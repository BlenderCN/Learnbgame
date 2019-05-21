Canny
=====
.. image:: http://kube.pl/wp-content/uploads/2018/01/Canny_01.png


Functionality
-------------
Finds edges in an image using the [Canny86] algorithm.


Inputs
------
- L2gradient_in – Flag, indicating whether a more accurate.
- apertureSize_in – Aperture size for the Sobel operator.
- image_in – 8-bit input image.
- threshold1_in – First threshold for the hysteresis procedure.
- threshold2_in – Second threshold for the hysteresis procedure.


Outputs
-------
- edges_out – Output edge map. Single channels 8-bit image, which has the same size as image.


Locals
------


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/Canny_11.png


