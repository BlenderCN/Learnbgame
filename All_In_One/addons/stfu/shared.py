import random
import math
from math import sin, cos
from math import pi as PI
from mathutils import Vector

# http://mathworld.wolfram.com/SpherePointPicking.html
def randomOnUnitSphere():
    u = random.uniform(-1, 1)
    theta = random.random()*2*PI
    return Vector( (math.sqrt(1-u**2)*cos(theta), math.sqrt(1-u**2)*sin(theta), u ) )

def optionalKey(obj, id, default):
    try:
       return obj[id]
    except KeyError:
        return default

def getOrCreateProp(propCollection, name):
    try:
       return propCollection[name]
    except KeyError:
        return propCollection.new(name)

def rsign(val=1): return random.choice([-1,+1]) * val

# height and colour to assign up to it
COLOUR_MAP = [
    (-.040, Vector((0, 0, .2))),
    (-.025, Vector((0, 0, .35))),
    (-.015, Vector((0, 0, .5))),    # dark blue
    (-.005, Vector((0, 0, 1))),     # blue
    (+.000, Vector((.4, .5, .9))),  # light blue
    (+.005, Vector((.8, .7, .25))), # yellow-ish
    (+.015, Vector((0, 1, 0))),     # green
    (+.021, Vector((.3, .1, 0))),   # brown
    (+.041, Vector((.5, .5, .5))),  # grey
    (+.999, Vector((1, 1, 1))),     # white
]
