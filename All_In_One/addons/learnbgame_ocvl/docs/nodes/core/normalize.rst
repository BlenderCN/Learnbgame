normalize
=========
.. image:: http://kube.pl/wp-content/uploads/2018/01/normalize_01.png


Functionality
-------------
Normalizes the norm or value range of an array.


Inputs
------
- alpha_in – Norm value to normalize to or the lower range boundary in case of the range normalization.
- beta_in – Upper range boundary in case of the range normalization; it is not used for the norm normalization.
- dtype_in – Channels as src and the depth =CV_MAT_DEPTH(dtype).
- image_in – Input array.
- norm_type_in – Normalization type (see cv::NormTypes).


Outputs
-------
- image_out – Output array.


Locals
------


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/normalize_11.png


