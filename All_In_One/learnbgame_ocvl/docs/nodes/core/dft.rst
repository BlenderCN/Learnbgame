dft
===


Functionality
-------------
Performs a forward or inverse Discrete Fourier transform of a 1D or 2D floating-point array.


Inputs
------
- flags_in – DFT_INVERSE, DFT_SCALE, DFT_ROWS, DFT_COMPLEX_OUTPUT, DFT_REAL_OUTPUT
- nonzeroRows_in – When the parameter is not zero, the function assumes that only the first nonzeroRows rows of the input array (DFT_INVERSE is not set) or only the first nonzeroRows of the output array (DFT_INVERSE is set) contain non-zeros.
- src_in – Input array that could be real or complex.


Outputs
-------
- array_out – Output array whose size and type depends on the flags.


Locals
------


Examples
--------


