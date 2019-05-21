fitLine
=======
.. image:: http://kube.pl/wp-content/uploads/2018/01/fitLine_01.png


Functionality
-------------
Fits a line to a 2D or 3D point set.


Inputs
------
- aeps_in – Sufficient accuracy for the angle. 0.01 would be a good default value for reps and aeps.
- distType_in – Distance used by the M-estimator, see cv::DistanceTypes.
- param_in – Numerical parameter ( C ) for some types of distances. If it is 0, an optimal value is chosen.
- points_in – Input vector of 2D points, stored in std::vector\<\> or Mat
- reps_in – Sufficient accuracy for the radius (distance between the coordinate origin and the line).


Outputs
-------


Locals
------
- loc_from_findContours – If linked with findContour node switch to True


Examples
--------
.. image:: http://kube.pl/wp-content/uploads/2018/01/fitLine_11.png


