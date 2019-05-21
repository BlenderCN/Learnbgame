approxPolyDP
============
.. image:: http://kube.pl/wp-content/uploads/2018/01/approxPolyDP_01.png


Functionality
-------------
Approximates a polygonal curve(s) with the specified precision.


Inputs
------
- closed_in – If true, the approximated curve is closed (its first and last vertices are connected). Otherwise, it is not closed.
- curve_in – Input vector of a 2D point stored in std::vector or Mat.
- epsilon_in – Parameter specifying the approximation accuracy. This is the maximum distance


Outputs
-------
- approxCurve_out – Result of the approximation. The type should match the type of the input curve.


Locals
------
- loc_from_findContours – If linked with findContour node switch to True


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/approxPolyDP_11.png


