LUT
===


Functionality
-------------
Performs a look-up table transform of an array.


Inputs
------
- image_in – Input array of 8-bit elements.
- lut_in – Look-up table of 256 elements; in case of multi-channel input array, the table should either have a single channel (in this case the same table is used for all channels) or the same number of channels as in the input array.


Outputs
-------
- image_out – Output array of the same size and number of channels as src, and the same depth as lut.


Locals
------


Examples
--------


