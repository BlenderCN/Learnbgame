arcLength
=========
.. image:: http://kube.pl/wp-content/uploads/2018/01/arcLength_01.png


Functionality
-------------
Calculates a contour perimeter or a curve length.


Inputs
------
- closed_in – Flag indicating whether the curve is closed or not.
- curve_in – Input vector of 2D points, stored in std::vector or Mat.


Outputs
-------
- length_out – Length of contour.


Locals
------
- loc_from_findContours – If linked with findContour node switch to True.


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/arcLength_11.png


