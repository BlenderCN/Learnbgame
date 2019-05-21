findContours
============
.. image:: http://kube.pl/wp-content/uploads/2018/01/findContours_01.png


Functionality
-------------
Finds contours in a binary image.


Inputs
------
- image_in – Input image.
- method_in – Contour approximation method, see cv::ContourApproximationModes
- mode_in – Contour retrieval mode, see cv::RetrievalModes
- offset_in – Optional offset by which every contour point is shifted. This is useful if the.


Outputs
-------
- contours_out – Detected contours. Each contour is stored as a vector of points.
- hierarchy_out – Optional output vector, containing information about the image topology. It has as many elements as the number of contours.
- image_out – Output image.


Locals
------


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/findContours_11.png
.. image:: http://kube.pl/wp-content/uploads/2018/01/findContours_12.png
.. image:: http://kube.pl/wp-content/uploads/2018/01/findContours_13.png
.. image:: http://kube.pl/wp-content/uploads/2018/01/findContours_14.png


