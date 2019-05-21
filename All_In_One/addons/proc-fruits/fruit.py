import bpy
import mathutils
import math
import random

from math import pi as PI
from mathutils import Vector
from .spline import HermiteInterpolator, Bezier, screw, bevelCircle, curvedScrew
from .util import optional, makeDiffuseMaterial, MeshMerger, clip
from .evolution import Evolvable
from .notnum import linspace


class FlowerResidueProps:
    # prefix fr_ for flower residue and to avoid name clashes
    
    fr_present = bpy.props.BoolProperty(
        name        = "Has flower residue",
        description = "Adds some decorations that look like the remains of the flower",
        default     = True
    )
    
    fr_openingAngle = bpy.props.FloatProperty(
        name        = "Residue Angle",
        description = "Where the petal remains should point",
        subtype     = 'ANGLE',
        default     = 0,
        soft_min    = -.1*PI, soft_max   = .25*PI
    )
    
    fr_radius = bpy.props.FloatProperty(
        name        = "Flower Residue Position",
        description = "Where to place the FR along the fruit",
        default     = .02,
        min         = 0,
        soft_max    = .05
    )
    
    fr_length = bpy.props.FloatProperty(
        name        = "Flower Residue Length",
        description = "Length of the FR, relative to fruit size",
        default     = .05,
        min         = 0,
        soft_min    = 0.01, soft_max     = .1
    )
    
    fr_petals = bpy.props.IntProperty(
        name        = "Num Petals",
        description = "Number of petal remains",
        default     = 5,
        min         = 3,
        soft_max    = 13
    )

#############################################

class StemProps:
    
    stem_present = bpy.props.BoolProperty(
        name        = "Add stem",
        description = "Whether to add a stem to the model",
        default     = True
    )
    
    stem_radius = bpy.props.FloatProperty(
        name        = "Stem Radius",
        description = "Determines where the stem meets the fruit and thus also the radius",
        default     = .01,
        min         = 0,
        soft_min    = .005, soft_max    = .02
    )
    
    stem_length = bpy.props.FloatProperty(
        name        = "Stem Length",
        description = "Length of the stem, relative to fruit length",
        default     = .15,
        min         = 0,
        soft_min    = 0.1, soft_max     = .25
    )
    
    stem_bending = bpy.props.FloatProperty(
        name        = "Stem Bending",
        description = "How strongly the stem bends sideways",
        default     = 0,
        min         = 0,
        soft_max    = 1
    )

#############################################

class FruitProperties(FlowerResidueProps, StemProps):
        
    length = bpy.props.FloatProperty(
        name        = "Length",
        description = "Length of the fruit",
        default     = .5,
        min         = 0,
        soft_min    = 0.2, soft_max     = 1
    )
    
    upperAngle = bpy.props.FloatProperty(
        name        = "Upper angle",
        description = "How broad or narrow the fruit is at the top",
        subtype     = 'ANGLE',
        default     = 0,
        min         = -PI/2,
        soft_min    = -.375*PI, soft_max    = .375*PI
    )
    
    middleAngle = bpy.props.FloatProperty(
        name        = "Middle Angle",
        description = "Inclination at the girdle",
        subtype     = 'ANGLE',
        default     = 0,
        soft_min    = -.125*PI, soft_max     = .125*PI
    )
    
    lowerAngle = bpy.props.FloatProperty(
        name        = "Lower angle",
        description = "How broad or narrow the fruit is at the bottom",
        subtype     = 'ANGLE',
        default     = 0,
        soft_min    = -.375*PI, soft_max    = .375*PI,
    )
    
    radius = bpy.props.FloatProperty(
        name        = "Width",
        description = "Horizontal radius of the fruit at the girdle",
        default     = .1,
        min         = 0,
        soft_min    = 0.05, soft_max     = .2
    )
    
    girdlePosition = bpy.props.FloatProperty(
        name        = "Girdle Position",
        description = "Relative positioning of the girdle along the length of the fruit",
        default     = .6,
        min         = .1, max = .9,
        soft_min    = 0.4, soft_max     = .8
    )
    
    colour = bpy.props.FloatVectorProperty(
        name        = "Colour",
        description = "Colour of the fruit",
        size        = 3,
        subtype     = 'COLOR',
        default     = (0, 0, 0),
        min         = 0, max = 1
    )
    
    grooves = bpy.props.IntProperty(
        name        = "Grooves",
        description = "The fruit will have this many grooves",
        default     = 2,
        min         = 0,
        soft_max    = 10
    )
    
    groovepower = bpy.props.FloatProperty(
        name        = "Groove Shape",
        description = "How sharp the grooves are",
        default     = 1,
        min         = 0,
        soft_max    = 8
    )
    
    grooveDepth = bpy.props.FloatProperty(
        name        = "Groove Depth",
        description = "How deep the grooves are. Expressed as relative offset around base radius, so negative values invert the grooves",
        default     = .25,
        soft_min    = -.5, soft_max    = .5
    )
    
    curved = bpy.props.BoolProperty(
        name        = "Is Curved",
        description = "Whether to apply the curve parameters",
        default     = False
    )
    
    curvePosVertical = bpy.props.FloatProperty(
        name        = "Curve Height",
        description = "Vertical position of the curvature",
        default     = .5,
        min         = 0, max = 1,
        soft_min    = .1, soft_max = .9
    )
    
    curveEccentricity = bpy.props.FloatProperty(
        name        = "Curve Eccentricity",
        description = "Intensity of curvature",
        default     = 0,
        min         = 0,
        soft_max = .75
    )
    
#############################################

class Fruit(Evolvable, FruitProperties):
    
    # the label is used in the bl_label of the operators provided by Evolvable
    label = "Fruit"

    # the identifier is used in the bl_idname of the operators provided by Evolvable
    # also, the data bpy.types.Object.<identifier> will be used for loading/storing instances of this Evolvable
    identifier = "fruit"
    
    # you should call Evolvable.__init__ to init all properties with their default value
    # if you need your own __init__, make sure it has no required parameters and accepts kwargs like Evolvable.__init__
    __init__ = Evolvable.__init__


    def _outerSpline(self):
        def angle2Vec(a):
            return Vector((math.cos(a), 0, math.sin(a)))
        
        x = 0, self.length*self.girdlePosition, self.length
        y = Vector((0, 0, 1)), Vector((self.radius, 0, (1-self.girdlePosition))), Vector((0, 0, 0))
        dy = angle2Vec(self.upperAngle), Vector((math.sin(self.middleAngle), 0, -math.cos(self.middleAngle))), angle2Vec(self.lowerAngle + PI)
        
        return HermiteInterpolator(x, y, dy)
    
    def _spine(self):
        if not self.curved or self.curveEccentricity == 0:
            return Bezier( (Vector(), Vector((0, 0, self.length))) ) 
        return Bezier( (Vector(), Vector((self.curveEccentricity*self.length, 0, self.curvePosVertical*self.length)), Vector((0, 0, self.length))) ) 
    
    def _makeFlowerResidue(self):
        petals = self.fr_petals
        rPoint = self._outerSpline()((1-self.fr_radius)*self.length)
        vertices = [rPoint, rPoint.copy(), rPoint.copy() - Vector((0, 0, self.fr_length*self.length))]
        vertices[0].rotate(mathutils.Euler((0, 0, -PI/petals)))
        vertices[1].rotate(mathutils.Euler((0, 0, PI/petals)))
        vertices[2].rotate(mathutils.Euler((0, -self.fr_openingAngle, 0)))
        
        for i in range(1, petals):
            vtmp = [v.copy() for v in vertices[0:3]]
            for v in vtmp:
                v.rotate( mathutils.Euler((0, 0, i*2*PI/petals)) )
            vertices.extend(vtmp)
        for v in vertices:
            v.rotate( Vector((0,0,1)).rotation_difference(self._spine().derive(1)(0)) )
            v += self._spine()(self.fr_radius) # FIXME inaccurate
        
        faces = [ (i, i+1, i+2) for i in range(0, 3*petals, 3)]
        return vertices, faces

    def _buildStem(self):
        radius = self._outerSpline()(self.stem_radius).x
        zbase = self._spine()(1-self.stem_radius).z # FIXME inaccurate
        length = self.length*self.stem_length
        zDir = self._spine().derive(1)(1-self.stem_radius).normalized()
        bendDir = zDir.copy()
        bendDir.rotate( mathutils.Quaternion(Vector((0,1,0)), PI/2) )
        
        x = 0, length
        #y = Vector((0, 0, zbase)), Vector((-length*self.stem_bending*2/3, 0, zbase)) + length*zDir
        y = Vector((0, 0, zbase)), Vector((0, 0, zbase)) + length*zDir -bendDir*length*self.stem_bending*(1-self.curveEccentricity)
        angle = clip(self.stem_bending, 0, 1)*PI/2*(1 + self.curveEccentricity/2) # at the upper stem
        dy = zDir, Vector((-math.sin(angle), 0, math.cos(angle)))
        
        stem = HermiteInterpolator(x, y, dy)
        return bevelCircle(stem, radius, closeEnds=True)
    
    def _grooveFunction(self, angle):
        def fib(x): # interpolated fibonacci
            n = math.floor(x)
            frac = x - n
            arr = [1] + [2]*(n+1)
            for i in range(2, n+2):
                arr[i] = arr[i-2] + arr[i-1]
            return (1-frac)*arr[n] + frac*arr[n+1]
        
        s = math.sin(self.grooves*angle/2)
        return ( .5 - (abs(s))**fib(self.groovepower) ) * self.grooveDepth + 1

    def toMesh(self, LOD=16):
        """
        Create a bpy.data.meshes instance from this Evolvable. Here you define how the properties translate into a mesh.
        The method must be callable without parameters, so provide meaningful default values (except for self, of course).
        LOD (level of detail) is just an example and can be omitted.
        It is usually called through Evolvable.toMeshObject, which does some decoration.
        """
        
        mm = MeshMerger()
        mm.add(*curvedScrew(self._outerSpline(), self._spine(), LODr=LOD, LODp=max(LOD, self.grooves*4*max(2, int(self.groovepower))), rScale=self._grooveFunction), 
            makeDiffuseMaterial(self.colour))
        
        brown = [.12,.06,0] # use a fixed color for now
        if self.fr_present:
            mm.add(*self._makeFlowerResidue(), makeDiffuseMaterial(brown))
        if self.stem_present:
            mm.add(*self._buildStem(), makeDiffuseMaterial(brown))
        
        return mm.buildMesh("Fruit")

#############################################

# the generators are processed for use in an EnumProperty
generatorFuncs = []
generatorMap = {f.__name__ : f for f in generatorFuncs}
generatorEnums = [(f.__name__, f.__name__, optional(f.__doc__, "")) for f in generatorFuncs]
