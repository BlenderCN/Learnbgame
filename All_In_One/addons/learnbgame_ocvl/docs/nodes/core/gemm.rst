gemm
====


Functionality
-------------
Performs generalized matrix multiplication.


Inputs
------
- alpha_in – Weight of the matrix product.
- beta_in – Weight of src3.
- flags_in – GEMM_1_T, GEMM_2_T, GEMM_3_T
- src_1_in – First multiplied input matrix that could be real(CV_32FC1, CV_64FC1) or complex(CV_32FC2, CV_64FC2).
- src_2_in – Second multiplied input matrix of the same type as src1.
- src_3_in – Third optional delta matrix added to the matrix product; it should have the same type as src1 and src2.


Outputs
-------
- dst_out – Output matrix; it has the proper size and the same type as input matrices.


Locals
------


Examples
--------


