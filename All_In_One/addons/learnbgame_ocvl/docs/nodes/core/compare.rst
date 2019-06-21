compare
=======


Functionality
-------------
Performs the per-element comparison of two arrays or an array and scalar value.


Inputs
------
- cmpop_in – A flag, that specifies correspondence between the arrays:

        CMP_EQ src1 is equal to src2.
        CMP_GT src1 is greater than src2.
        CMP_GE src1 is greater than or equal to src2.
        CMP_LT src1 is less than src2.
        CMP_LE src1 is less than or equal to src2.
        CMP_NE src1 is unequal to src2.
        
- src1_in – First input array or a scalar (in the case of cvCmp, cv.Cmp, cvCmpS, cv.CmpS it is always an array); when it is an array, it must have a single channel.
- src2_in – Second input array or a scalar (in the case of cvCmp and cv.Cmp it is always an array; in the case of cvCmpS, cv.CmpS it is always a scalar); when it is an array, it must have a single channel.


Outputs
-------
- dst_out – Output array that has the same size and type as the input arrays.


Locals
------


Examples
--------


