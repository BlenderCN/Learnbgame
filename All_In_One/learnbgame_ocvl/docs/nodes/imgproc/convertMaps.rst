convertMaps
===========
.. image:: http://kube.pl/wp-content/uploads/2018/01/convertMaps_01.png


Functionality
-------------
Converts image transformation maps from one representation to another.


Inputs
------
- dstmap1type_in – Type of the first output map that should be.
- map1_in – The first input map of type CV_16SC2 , CV_32FC1 , or CV_32FC2 .
- map2_in – The second input map of type CV_16UC1 , CV_32FC1 , or none (empty matrix), respectively.
- nninterpolation_in – Flag indicating whether the fixed-point maps are used for the nearest-neighbor or for a more complex interpolation.


Outputs
-------
- dstmap1_out – The first output map that has the type dstmap1type and the same size as src .
- dstmap2_out – The second output map.


Locals
------


Examples
--------


