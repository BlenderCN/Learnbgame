contourArea
===========
.. image:: http://kube.pl/wp-content/uploads/2018/01/contourArea_01.png


Functionality
-------------
Calculates a contour area.


Inputs
------
- contour_in – Input vector of 2D points (contour vertices), stored in std::vector or Mat.


Outputs
-------
- area_out – Area of contour.
- oriented_out – Oriented area flag. If it is true, the function returns a signed area value, depending on the contour orientation (clockwise or counter-clockwise).


Locals
------
- loc_from_findContours – If linked with findContour node switch to True


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/contourArea_11.png


