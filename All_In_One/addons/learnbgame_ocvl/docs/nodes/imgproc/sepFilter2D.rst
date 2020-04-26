sepFilter2d
===========


Functionality
-------------
Applies a separable linear filter to an image.


Inputs
------
- anchor_in – Anchor position within the kernel. The default value $(-1,-1)$ means that the anchor is at the kernel center.
- borderType_in – Pixel extrapolation method, see cv::BorderTypes
- ddepth_in – Destination image depth, see @ref filter_depths 'combinations'
- delta_in – Value added to the filtered results before storing them.
- image_in – Input image.
- kernel_size_in – Coefficients for filtering each row and column.


Outputs
-------
- image_out – Output image


Locals
------


Examples
--------


