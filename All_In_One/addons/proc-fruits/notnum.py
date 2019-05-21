# Replication of some numpy functionality, to remove the dependency.


def linspace(start, stop, count, endpoint=True):
    count = int(count)
    assert count >= 2, "use two samples at least"
    if endpoint:
        return [start * (count-1-i)/(count-1) + stop * i/(count-1) for i in range(count)]
    else:    
        return [start * (count-i)/count + stop * i/count for i in range(count)]

#############################################

class poly1d:
    
    def __init__(self, coeffs):
        assert coeffs, "no coefficients given"
        self.coeffs = coeffs[::-1] # store constant coefficient first
    
    def __call__(self, x):
        return sum( c*pow(x,n) for n, c in enumerate(self.coeffs) )
    
    def deriv(self, m):
        m = int(m)
        assert m >= 0, "only non-negative derivation allowed"
        if m == 0:
            return self
        elif len(self.coeffs) <= m:
            return poly1d([0.])
        else:
            coeffs = self.coeffs
            for i in range(m):
                coeffs = [c*n for n, c in enumerate(coeffs[1:], 1)]
            return poly1d(coeffs[::-1])
