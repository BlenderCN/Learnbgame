GetDerivKernels
===============


Functionality
-------------
Returns filter coefficients for computing spatial image derivatives.


Inputs
------
- dx_in – Derivative order in respect of x.
- dy_in – Derivative order in respect of y.
- ksize_in – Aperture size. It can be CV_SCHARR, 1, 3, 5, or 7.
- ktype_in – Type of filter coefficients. It can be CV_32f or CV_64F.
- normalize_in – Flag indicating whether to normalize (scale down) the filter coefficients or not.


Outputs
-------
- kernel_out – Output kernel.
- kx_out – Output matrix of row filter coefficients. It has the type ktype .
- ky_out – Output matrix of column filter coefficients. It has the type ktype .


Locals
------


Examples
--------


