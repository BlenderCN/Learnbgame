cvtColor
========
.. image:: http://kube.pl/wp-content/uploads/2018/01/cvtColor_01.png


Functionality
-------------
Converts an image from one color space to another.


Inputs
------
- code_in – Color space conversion code (see cv::ColorConversionCodes).
- dstCn_in – Number of channels in the destination image; if the parameter is 0, the number of the channels is derived automatically from input image and code.
- image_in – Input image: 8-bit unsigned, 16-bit unsigned ( CV_16UC... ), or single-precision floating-point.


Outputs
-------
- image_out – Output image of the same size and depth as input image.


Locals
------


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/cvtColor_11.png
.. image:: http://kube.pl/wp-content/uploads/2018/01/cvtColor_12.png
.. image:: http://kube.pl/wp-content/uploads/2018/01/cvtColor_13.png


