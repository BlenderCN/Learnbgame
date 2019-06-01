Scharr
======


Functionality
-------------
Calculates the first x- or y- image derivative using Scharr operator.


Inputs
------
- borderType_in – Pixel extrapolation method, see cv::BorderTypes
- ddepth_in – Output image depth, see @ref filter_depths 'combinations'.
- delta_in – Optional delta value that is added to the results prior to storing them in dst.
- dx_in – Order of the derivative x.
- dy_in – Order of the derivative y.
- image_in – Input image.
- scale_in – Optional scale factor for the computed Laplacian values.


Outputs
-------
- image_out – Output image.


Locals
------


Examples
--------


