matchTemplate
=============


Functionality
-------------
Compares a template against overlapped image regions.


Inputs
------
- image_in – Image where the search is running. It must be 8-bit or 32-bit floating-point.
- mask_in – Input mask.
- method_in – Parameter specifying the comparison method, see cv::TemplateMatchModes.
- templ_in – Searched template. It must be not greater than the source image and have the same data type.


Outputs
-------
- image_out – Output image.
- result_out – Map of comparison results. It must be single-channel 32-bit floating-point.


Locals
------


Examples
--------


