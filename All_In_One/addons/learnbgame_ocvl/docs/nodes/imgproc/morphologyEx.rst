morphologyEx
============


Functionality
-------------
Performs advanced morphological transformations.


Inputs
------
- anchor_in – Position of the anchor within the element.
- borderType_in – Border mode used to extrapolate pixels outside of the image, see cv::BorderTypes
- image_in – Source image. The number of channels can be arbitrary. The depth should be one of CV_8U, CV_16U, CV_16S, CV_32F` or ``CV_64F.
- iterations_in – Number of times erosion is applied.
- ksize_in – Structuring element used for erosion.
- op_in – Type of a morphological operation, see cv::MorphTypes.


Outputs
-------
- image_out – Destination image of the same size and type as src .


Locals
------


Examples
--------


