rectangle
=========
.. image:: http://kube.pl/wp-content/uploads/2018/01/rectangle_01.png


Functionality
-------------
Draws a simple, thick, or filled up-right rectangle.


Inputs
------
- color_in – Rectangle color or brightness (grayscale image).
- h_in – Height of rectangle.
- image_in – Input image.
- lineType_in – Type of the line. See the line description.
- pt1_in – Vertex of the rectangle.
- pt2_in – Vertex of the rectangle opposite to pt1.
- rect_in – X, Y, Weight, Height in one vector.
- shift_in – Number of fractional bits in the point coordinates.
- thickness_in – Thickness of lines that make up the rectangle. Negative values, like CV_FILLED, mean that the function has to draw a filled rectangle.
- w_in – Weight of rectangle.
- x_in – X for point of top left corner.
- y_in – Y for point of top left corner.


Outputs
-------
- image_out – Output image.


Locals
------
- loc_input_mode – Loc input mode.


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/rectangle_11.png


