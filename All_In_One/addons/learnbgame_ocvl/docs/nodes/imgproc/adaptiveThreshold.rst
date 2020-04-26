adaptiveThreshold
=================
.. image:: http://kube.pl/wp-content/uploads/2018/01/adaptiveThreshold_01.png


Functionality
-------------
Applies an adaptive threshold to an array.


Inputs
------
- C_in – Constant subtracted from the mean or weighted mean.
- adaptiveMethod_in – Adaptive thresholding algorithm to use, see cv::AdaptiveThresholdTypes .
- blockSize_in – Size of a pixel neighborhood that is used to calculate a threshold value for the pixel.
- image_in – Source 8-bit single-channel image.
- maxValue_in – Non-zero value assigned to the pixels for which the condition is satisfied.
- thresholdType_in – Thresholding type that must be either THRESH_BINARY or THRESH_BINARY_INV, etc.


Outputs
-------
- image_out – Destination image of the same size and the same type as src.


Locals
------


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/adaptiveThreshold_11.png
.. image:: http://kube.pl/wp-content/uploads/2018/01/adaptiveThreshold_12.png


