ellipse
=======
.. image:: http://kube.pl/wp-content/uploads/2018/01/ellipse_01.png


Functionality
-------------
Draws a simple or thick elliptic arc or fills an ellipse sector.


Inputs
------
- angle_in – Ellipse rotation angle in degrees.
- axes_in – Half of the size of the ellipse main axes.
- box_in – Alternative ellipse representation via RotatedRect. This means that the function draws an ellipse inscribed in the rotated rectangle.
- center_in – Center of the ellipse.
- color_in – Ellipse color.
- endAngle_in – Ending angle of the elliptic arc in degrees
- image_in – Input image.
- lineType_in – Type of the ellipse boundary. See the line description.
- startAngle_in – Starting angle of the elliptic arc in degrees.
- thickness_in – Thickness of the ellipse arc outline, if positive. Otherwise, this indicates that a filled ellipse sector is to be drawn.


Outputs
-------
- image_out – Output image.


Locals
------
- loc_input_mode – Input mode.


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/ellipse_11.png
.. image:: http://kube.pl/wp-content/uploads/2018/01/ellipse_12.png
.. image:: http://kube.pl/wp-content/uploads/2018/01/ellipse_13.png


