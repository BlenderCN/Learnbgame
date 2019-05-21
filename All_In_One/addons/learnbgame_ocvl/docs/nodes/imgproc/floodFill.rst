floodFill
=========
.. image:: http://kube.pl/wp-content/uploads/2018/01/floodFill_01.png


Functionality
-------------
Fills a connected component with the given color.


Inputs
------
- flag_fixed_range_in – If set, the difference between the current pixel and seed pixel is considered. Otherwise, the difference between neighbor pixels is considered (that is, the range is floating).
- flag_mask_only_in – If set, the function does not change the image ( newVal is ignored), and only fills the mask with the value specified in bits 8-16 of flags as described above.
- image_in – Source 8-bit single-channel image.
- loDiff_in – Maximal lower brightness/color difference between the currently observed pixel and one of its neighbors belonging to the component, or a seed pixel being added to the component.
- newVal_in – New value of the repainted domain pixels.
- seedPoint_in – Starting point.
- upDiff_in – Maximal upper brightness/color difference between the currently observed pixel and one of its neighbors belonging to the component, or a seed pixel being added to the component.


Outputs
-------
- image_out – Destination image of the same size and the same type as src.
- rect_out – Rect output.


Locals
------


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/floodFill_11.png
.. image:: http://kube.pl/wp-content/uploads/2018/01/floodFill_12.png


