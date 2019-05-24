import bpy
import mathutils
import math
import random

from math import pi as PI
from mathutils import Vector
from .spline import HermiteInterpolator, screw, bevelCircle
from .util import optional, optionalKey, logTime, makeDiffuseMaterial, mergeMeshPydata, clip
from notnum import linspace

class MushroomProps:
    h0 = bpy.props.FloatProperty(
        name        = "Center Thickness",
        description = "Thickness of the hat in the center",
        default     = .2,
        min         = 0,
        soft_min    = 0.01, soft_max     = .5
    )
    h1 = bpy.props.FloatProperty(
        name        = "Rim Height",
        description = "Height of the outer rim relative to the hat center bottom",
        default     = .2,
        soft_min    = -.5, soft_max     = .5
    )
    radius = bpy.props.FloatProperty(
        name        = "Radius",
        description = "Radius of the hat",
        default     = .2,
        min         = 0,
        soft_min    = .01, soft_max     = .5
    )
    
    aUpper0 = bpy.props.FloatProperty(
        name        = "Upper Inner Angle",
        description = "Angle of the upper spline at the center",
        default     = 0,
        soft_min    = 0, soft_max     = .375*PI
    )
    aUpper1 = bpy.props.FloatProperty(
        name        = "Upper Outer Angle",
        description = "Angle of the upper spline at the rim",
        default     = 0,
        soft_min    = -PI/2, soft_max    = 0
    )
    aLower0 = bpy.props.FloatProperty(
        name        = "Lower Inner Angle",
        description = "Angle of the lower spline at the center",
        default     = 0,
        soft_min    = -.375*PI, soft_max     = .375*PI
    )
    aLower1 = bpy.props.FloatProperty(
        name        = "Lower Outer Angle",
        description = "Angle of the lower spline at the rim",
        default     = 0,
        soft_min    = 0, soft_max     = PI/2
    )
    
    shaftHeight = bpy.props.FloatProperty(
        name        = "Shaft Height",
        description = "Height of the shaft from the hat center",
        default     = .25,
        min         = 0,
        soft_min    = .05, soft_max = .5
    )
    shaftRadius = bpy.props.FloatProperty(
        name        = "Radius of the Shaft",
        description = "Radius of the shaft",
        default     = .05,
        min         = 0,
        soft_min    = .025, soft_max = .1
    )
    bulgePosition = bpy.props.FloatProperty(
        name        = "Bulge Position",
        description = "Position of the bulge in the shaft (normalised to [0,1])",
        default     = .5,
        min         = 0, max = 1,
        soft_min    = .2, soft_max   = .8
    )
    bulgeWidth = bpy.props.FloatProperty(
        name        = "Bulge Width",
        description = "Width of the bulge relative to the shaft radius",
        default     = 0,
        min         = 0,
        soft_max    = .3
    )
    
    upColor = bpy.props.FloatVectorProperty(
        name        = "Top Color",
        description = "Color of the upper side of the hat",
        size        = 3,
        default     = (.1, .02, 0),
        min         = 0, max = 1
    )
    downColor = bpy.props.FloatVectorProperty(
        name        = "Bottom Color",
        description = "Color of the lower side of the hat",
        size        = 3,
        default     = (1., .9, .3),
        min         = 0, max = 1
    )
    shaftColor = bpy.props.FloatVectorProperty(
        name        = "Shaft Color",
        description = "Color of the shaft",
        size        = 3,
        default     = (1, 1, .6),
        min         = 0, max = 1
    )

#############################################

class MushroomPG(bpy.types.PropertyGroup, MushroomProps):
    pass

#############################################

class Mushroom:
    
    def __init__(self, **kwargs):
        props = properties(MushroomProps)
        for name, params in props.items():
            self.__setattr__(name, params["default"])
            
        for kw in kwargs:
            self.__setattr__(kw, propClamp(kwargs[kw], props[kw]))

    def store(self, obj):
        for name in properties(MushroomProps).keys():
            obj.__setattr__(name, self.__getattribute__(name))

    @staticmethod
    def load(obj):
        return Mushroom(**dict( filter(lambda p: p[1] is not None, 
            map(lambda n: (n, optionalKey(obj, n)), properties(MushroomProps).keys())) ))

    def upperHat(self):
        return self._shroomSpline(self.h0, self.aUpper0, self.aUpper1)
        
    def lowerHat(self):
        return self._shroomSpline(0, self.aLower0, self.aLower1)
        
    def _shroomSpline(self, h0, a0, a1):
        def angle2Vec(a):
            return Vector((math.cos(a), 0, math.sin(a)))
        
        x = 0, self.radius
        y = Vector((0, 0, h0)), Vector((self.radius, 0, self.h1))
        dy = angle2Vec(a0), angle2Vec(a1)
        return HermiteInterpolator(x, y, dy)
    
    def _shaftContactPoint(self):
        return self.lowerHat()(.2*self.radius)
    
    def shaft(self):
        contact = self._shaftContactPoint()
        return HermiteInterpolator([0, self.shaftHeight],
            [Vector([0, 0, contact.z-self.shaftHeight]), Vector([0, 0, contact.z])],
            [Vector([0, 0, 1]), Vector([0, 0, 1])])
    
    def shaftRadiusSpline(self):
        contact = self._shaftContactPoint()
        return HermiteInterpolator([0, self.bulgePosition*self.shaftHeight, self.shaftHeight],
            [ self.shaftRadius, self.shaftRadius*(1+self.bulgeWidth), contact.to_2d().length ],
            [ 0, 0, 0 ])
    
    def hatHeight(self):
        return max( self.h0, self.h1, self.h0-self.h1 )
    
    @logTime
    def toMeshObject(self, LODr, LODp, withNoise=False):
        if withNoise: # construct radial noise for the hat
            rnLOD = 8 #LODp//2
            r_noise = [random.uniform(.9, 1.1) for _ in range(rnLOD-1)]
            r_noise.append(r_noise[0])
            r_noise = HermiteInterpolator(linspace(0, 2*PI, rnLOD), r_noise, (0,)*rnLOD)
        else:
            r_noise = None
        
        verts, faces = mergeMeshPydata(
            screw(self.upperHat(), LODr, LODp, rScale=r_noise),
            screw(self.lowerHat(), LODr, LODp, normalsDown=True, rScale=r_noise),
            bevelCircle(self.shaft(), self.shaftRadiusSpline(), LODp, LODr)
        )
        fiu = LODp*(LODr-1) # number of faces per component
        
        newMesh = bpy.data.meshes.new("Mushroom")
        newMesh.from_pydata(verts, [], faces)
        newMesh.update()
        newMesh.transform(mathutils.Matrix.Translation( (0, 0, max(-self.shaft()(0).z, -self.h1)) ))
        
        newMesh.materials.append(makeDiffuseMaterial(self.upColor))
        newMesh.materials.append(makeDiffuseMaterial(self.downColor))
        newMesh.materials.append(makeDiffuseMaterial(self.shaftColor))
        for i in range(3):
            for p in range(i*fiu, (i+1)*fiu):
                newMesh.polygons[p].material_index = i
        
        obj = bpy.data.objects.new("Mushroom", newMesh)
        self.store(obj.mushroom)
        return obj
    
    def mutate(self, radiation): # currently works for FloatProperties only
        """mutate a new mushroom from this one. parameter radiation must be positive and should not be larger than 100 """
        assert(radiation >= 0)
        
        props = properties(MushroomProps)
        nprops = len(props)
        
        nmutations = clip(round(random.gauss(nprops*radiation/200, math.sqrt(nprops))), 1, nprops)
        mutatingProps = random.sample(props.items(), nmutations)
        radiation /= math.sqrt(nmutations) # the more aspects change, the less each of them changes
        
        descendant = Mushroom.load(self)
        for name, params in mutatingProps:
            current = descendant.__getattribute__(name)
            if params["type"] is bpy.props.BoolProperty:
                newVal = (not current) if radiation/100 < random.random() else current
            else:
                span = optionalKey(params, "soft_max", optionalKey(params, "max")) - optionalKey(params, "soft_min", optionalKey(params, "min"))
                span *= radiation/100 # percent to factor
                
                def fuzzyClamp(val, curr): # clamp that allows flowing over soft min/max with some probability
                    val = propClamp(val, params)
                    # if val exceeds the soft bounds, chances decrease to go further away
                    if optionalKey(params, "soft_min") is not None and val < params["soft_min"] and val < curr:
                        if random.random() < span/(span + params["soft_min"] - val):
                            return val
                        return curr if curr < params["soft_min"] else params["soft_min"]
                    if optionalKey(params, "soft_max") is not None and val > params["soft_max"] and val > curr:
                        if random.random() < span/(span + val - params["soft_max"]):
                            return val
                        return curr if curr > params["soft_max"] else params["soft_max"]
                    return val

                if params["type"] is bpy.props.FloatProperty:
                    newVal = fuzzyClamp(random.gauss(current, span), current)
                if params["type"] is bpy.props.FloatVectorProperty:
                    i = random.randrange(params["size"]) # evolve only one entry of the vector
                    newVal = current.copy()
                    newVal[i] = fuzzyClamp(random.gauss(current[i], span), current[i])
            #TODO handle other property types
            descendant.__setattr__(name, newVal)
        
        return descendant
    
    @classmethod
    def procreate(cls, *geneSeeds):
        """
        Creates a new mushroom from given examples. Specify at least 2 examples.
        Each property of the result will either be taken from an example or averaged over all examples.
        """
        assert len(geneSeeds) > 1, "Specify at least 2 seeds"
        # None gene leads to averaging; it occurs less often with many seeds to keep diversity
        genePool = geneSeeds + (None,)
        child = cls()
        for name, prop in properties(MushroomProps).items():
            gene = random.choice(genePool)
            if gene is None:
                if prop["type"] is bpy.props.FloatVectorProperty:
                    val = [0]*prop['size']
                    for i in range(prop['size']):
                        val[i] = sum(optionalKey(p, name, prop['default'])[i] for p in geneSeeds)/len(genePool)
                    child.__setattr__(name, val)
                else: # TODO other prop types will need special treatment too
                    child.__setattr__(name, sum(optionalKey(p, name, prop['default']) for p in geneSeeds)/len(genePool))
            else:
                child.__setattr__(name, optionalKey(gene, name, prop['default']))
        return child

#############################################

def colorNoise(power=.05):
    return mathutils.Color([random.gauss(0, power) for _ in range(3)])

def addColor(shroom):
    c = mathutils.Color((0,0,0))
    c.hsv = random.choice([
        [ random.gauss(0, .05)%1, random.gauss(.9, .2), random.uniform(.5, 1) ], # red
        [ random.gauss(.16, .05), random.gauss(.9, .2), random.uniform(.5, 1) ], # yellow
        [ random.gauss(.33, .05), random.gauss(.9, .2), random.uniform(.5, 1) ], # green
        [ random.gauss(.66, .05), random.gauss(.9, .2), random.uniform(.5, 1) ], # blue
        [ random.uniform(0, 1),   random.gauss(0, .2),  random.uniform(.7, 1) ], # white
        [ random.uniform(0, 1),   random.uniform(0, 1), random.gauss(0, .1) ],   # black
    ])
    shroom.upColor = c[:]
    
    # small chance to keep similar color, but mostly use a light yellowish color
    if random.random() > .1:
        c[:] = 1., .9, .3
    c += colorNoise()
    shroom.downColor = c[:]
    
     # again, small chance of keeping the color
    if random.random() > .1:
        c[:] = 1, 1, .6
    c += colorNoise()
    shroom.shaftColor = c[:]

#############################################

def generic():
    "first try, quite random"
    m = Mushroom()
    m.h0 = random.uniform(.03, .3)
    m.h1 = random.gauss(1, .5) * m.h0
    m.radius = random.uniform(.1, .5)
    m.aUpper0 = max(0, random.uniform(-PI/2, PI/2))
    m.aUpper1 = random.uniform(0, - PI/2)
    m.aLower0 = random.uniform(- PI/2, PI/2)
    m.aLower1 = random.uniform(0, PI/2)
    
    m.shaftHeight = random.uniform(1, 2.5) * m.hatHeight()
    m.shaftRadius = random.uniform(.1, .2) * m.radius
    m.bulgePosition = random.uniform(.0, .5)
    m.bulgeWidth = random.uniform(0, .4)

    addColor(m)
    return m

def cup():
    "funnel-like shapes"
    m = Mushroom()
    m.h0 = random.uniform(.03, .3)
    m.h1 = m.h0 + random.uniform(.03, .3)
    m.radius = random.uniform(.1, .5)
    m.aUpper0 = random.uniform(0, PI/2)
    m.aUpper1 = random.uniform(0, -PI/4)
    m.aLower0 = random.uniform(0, PI/2-.3)
    m.aLower1 = random.uniform(0, PI/2)
    
    m.shaftHeight = random.uniform(.5, 1) * m.hatHeight()
    m.shaftRadius = random.uniform(.1, .2) * m.radius
    m.bulgePosition = .5
    m.bulgeWidth = 0
    
    addColor(m)
    return m

def cap():
    "cap-like shapes"
    m = Mushroom()
    m.h0 = random.uniform(.03, .3)
    m.h1 = -random.uniform(.03, .6)
    m.radius = random.uniform(.1, .25)
    m.aUpper0 = 0
    m.aUpper1 = random.uniform(-PI/4, -PI*3/4)
    m.aLower0 = random.uniform(0, -PI/4)
    m.aLower1 = random.uniform(0, PI/2)
    
    m.shaftHeight = random.uniform(1, 2.5) * m.hatHeight()
    m.shaftRadius = random.uniform(.1, .2) * m.radius
    m.bulgePosition = random.uniform(.0, .2)
    m.bulgeWidth = random.uniform(0, .25)

    addColor(m)
    return m

def cop():
    "bulgy shapes"
    m = Mushroom()
    m.h0 = random.uniform(.03, .3)
    m.h1 = m.h0 * random.uniform(.4, .6)
    m.radius = random.uniform(.1, .5)
    m.aUpper0 = 0
    m.aUpper1 = random.uniform(-PI/4, -PI*3/4)
    m.aLower0 = random.uniform(0, -PI/4)
    m.aLower1 = random.uniform(0, PI/2)
    
    m.shaftHeight = random.uniform(.5, 2) * max( m.hatHeight(), m.radius)
    m.shaftRadius = random.uniform(.1, .2) * m.radius
    m.bulgePosition = random.uniform(.0, .5)
    m.bulgeWidth = random.uniform(0, .5)
    
    addColor(m)
    return m

generatorFuncs = generic, cup, cap, cop
generatorMap = {f.__name__ : f for f in generatorFuncs}
generatorEnums = [(f.__name__, f.__name__, optional(f.__doc__, ""), i+1) for i, f in enumerate(generatorFuncs)]

#############################################
# utils
#############################################

def mergeTypeInfo(propTuple):
    result = propTuple[1].copy()
    result["type"] = propTuple[0]
    return result

def properties(propGroup):
    return dict( map( lambda p: (p[0], mergeTypeInfo(p[1])), filter( lambda v: type(v[1]) == tuple, propGroup.__dict__.items() ) ) )

def propClamp(value, prop, soft=False):
    from numbers import Integral, Real
    minv = optionalKey(prop, "soft_min" if soft else "min", value)
    maxv = optionalKey(prop, "soft_max" if soft else "max", value)
    if isinstance(value, Integral):
        return clip(value, minv, maxv)
    if isinstance(value, Real):
        return clip(value, minv, maxv)
    if prop["type"] is bpy.props.FloatVectorProperty:
        return list(clip(val, minv, maxv) for val in value)
    raise Exception("Property type "+str(type(value))+" not yet supported.")