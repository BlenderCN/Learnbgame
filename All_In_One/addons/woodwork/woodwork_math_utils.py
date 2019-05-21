

class MathUtils:

    ZERO_TOLERANCE = 0.00001
    ABSOLUTE_ERROR_THRESHOLD = 1.e-8
    RELATIVE_ERROR_THRESHOLD = 1.e-5

    VECTOR_MAX_FLOAT_VALUE = 3.40282347E+38

    # Don't work, don't know why...
    #VECTOR_MIN_FLOAT_VALUE = 1.17549435E-38

    VECTOR_MIN_FLOAT_VALUE = -99999999999999999.0


    # See http://randomascii.wordpress.com/2012/02/25/
    # comparing-floating-point-numbers-2012-edition/
    # - If you are comparing against zero, then relative epsilons and ULPs based
    #   comparisons are usually meaningless. You’ll need to use an absolute
    #   epsilon, whose value might be some small multiple of FLT_EPSILON and the
    #   inputs to your calculation. Maybe.
    # - If you are comparing against a non-zero number then relative epsilons or
    #   ULPs based comparisons are probably what you want. You’ll probably want
    #   some small multiple of FLT_EPSILON for your relative epsilon, or some small
    #   number of ULPs. An absolute epsilon could be used if you knew exactly what
    #   number you were comparing against.
    # - If you are comparing two arbitrary numbers that could be zero or non-zero
    #   then you need the kitchen sink. Good luck and God speed.
    @staticmethod
    def almost_equal_relative_or_absolute(a,
                                          b,
                                          max_relative_error=RELATIVE_ERROR_THRESHOLD,
                                          max_absolute_error=ABSOLUTE_ERROR_THRESHOLD):
        almost_equal = False
        if a == b:
            almost_equal = True
        else:
            #  Check if the numbers are really close
            # -- needed when comparing numbers near zero.
            abs_diff = abs(a - b)

            if abs_diff <= max_absolute_error:
                almost_equal = True
            else:
                abs_a = abs(a)
                abs_b = abs(b)

                if abs_b > abs_a:
                    largest = abs_b
                else:
                    largest = abs_a

                if abs_diff <= largest * max_relative_error:
                    almost_equal = True
    
        return almost_equal

    @staticmethod
    def almost_equal_absolute(a,
                              b,
                              max_absolute_error=ABSOLUTE_ERROR_THRESHOLD):
        almost_equal = False
        if a == b:
            almost_equal = True
        else:
            abs_diff = abs(a - b)

            if abs_diff <= max_absolute_error:
                almost_equal = True
            else:
                almost_equal = False
        return almost_equal

    @staticmethod
    def almost_zero(a, zero_tolerance=ZERO_TOLERANCE):
        return abs(a) < zero_tolerance
