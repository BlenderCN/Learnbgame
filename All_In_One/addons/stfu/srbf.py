import math
import random
from math import pi as PI
from math import sin, cos
from mathutils import Vector

from .shared import rsign, optionalKey, randomOnUnitSphere

class SRBF:
    
    def __init__(self, position, width, amplitude):
        self.position = position.normalized()
        self.width = width
        self.amplitude = amplitude
    
    def eval(self, dist):
        raise NotImplementedError("Child class must implement this function.")
    
    def __call__(self, position):
        return self.amplitude * self.eval( self.position.angle(position)/(PI*self.width) )

##########

class Gaussian(SRBF):
    ID = 0
    
    def eval(self, dist):
        return math.exp(-dist**2)
    
    OCL_CODE = """
        return exp(-dist*dist);
    """

##########

class Plateau(SRBF):
    ID = 1
    
    def eval(self, dist):
        if dist <= .5:
            return 1
        if dist <= 1:
            x = (1-dist)/.5
            return x * x * (3 - 2 * x) # smoothing
        return 0
    
    OCL_CODE = """
        return 1 - smoothstep(0.5f, 1, dist);
    """

##########

class Gabor(SRBF):
    ID = 2
    
    def eval(self, dist):
        dist /= 2
        return math.exp(-dist**2) * cos(dist*2*PI)
    
    OCL_CODE = """
        dist /= 2;
        return exp(-dist*dist) * cos(dist * M_2_PI_F);
    """

##########

class DOG(SRBF): # rather a Mexican hat wavelet, than actual DoG
    ID = 3
    
    def eval(self, dist):
        return (1-2*dist**2)*math.exp(-dist**2)
        
    OCL_CODE = """
        float tmp = dist*dist;
        return (1-2*tmp) * exp(-tmp);
    """

#############################################

class SRBFCollection:
    
    def __init__(self):
        self.coll = []
    
    def add(self, *srbfs):
        self.coll.extend(srbfs)
    
    def __call__(self, position):
        return sum( srbf(position) for srbf in self.coll )

#############################################

ALL_SRBFS = [Gaussian, Plateau, DOG, Gabor]

# actual ratios for the earth
kmHigh = 1/6350 # 1km/earth.radius
kmWide = 1/40000 # 1km/earth.circumference

def randomSRBF(**kwargs):
    func = random.choice(ALL_SRBFS)
    position = optionalKey(kwargs, "position", randomOnUnitSphere())
    width = optionalKey(kwargs, "width", random.uniform(100, 1000)*kmWide)
    sign = optionalKey(kwargs, "sign", rsign())
    amplitude = optionalKey(kwargs, "amplitude", sign*random.uniform(50, 100)*kmHigh)
    return func(position, width, amplitude)