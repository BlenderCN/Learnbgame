convexHull
==========
.. image:: http://kube.pl/wp-content/uploads/2018/01/convexHull_01.png


Functionality
-------------
Finds the convex hull of a point set.


Inputs
------
- clockwise_in – Orientation flag. If it is true, the output convex hull is oriented clockwise.
- points_in – Input 2D point set, stored in std::vector or Mat.
- returnPoints_in – Operation flag. In case of a matrix, when the flag is true, the function returns convex hull points.


Outputs
-------
- hull_out – Output convex hull. It is either an integer vector of indices or vector of points.


Locals
------
- loc_from_findContours – If linked with findContour node switch to True


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/convexHull_11.png
.. image:: http://kube.pl/wp-content/uploads/2018/01/convexHull_12.png


