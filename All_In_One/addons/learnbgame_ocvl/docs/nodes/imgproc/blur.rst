blur
====
.. image:: http://kube.pl/wp-content/uploads/2018/01/blur_01.png


Functionality
-------------
Blurs an image using the normalized box filter.


Inputs
------
- anchor_in – Bnchor point; default value Point(-1,-1) means that the anchor is at the kernel center.
- borderType_in – Border mode used to extrapolate pixels outside of the image, see cv::BorderTypes.
- image_in – Input image.
- ksize_in – Blurring kernel size.


Outputs
-------
- image_out – Output image.


Locals
------


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/blur_11.png


