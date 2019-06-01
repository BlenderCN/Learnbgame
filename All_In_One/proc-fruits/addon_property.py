import bpy

from math import pi as PI
from mathutils import Vector

from bpy.utils import (
    previews,
    register_class,
    unregister_class
    )

from bpy.types import (
    Panel, 
    Operator,
    Menu,
    PropertyGroup,
    SpaceView3D,
    WindowManager,
    )

from bpy.props import (
    EnumProperty,
    PointerProperty,
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    )

class FlowerResidueProps(PropertyGroup):
    # prefix fr_ for flower residue and to avoid name clashes
    
    fr_present : BoolProperty(
        name        = "Has flower residue",
        description = "Adds some decorations that look like the remains of the flower",
        default     = True
    )
    
    fr_openingAngle : FloatProperty(
        name        = "Residue Angle",
        description = "Where the petal remains should point",
        subtype     = 'ANGLE',
        default     = 0,
        soft_min    = -.1*PI, soft_max   = .25*PI
    )
    
    fr_radius : FloatProperty(
        name        = "Flower Residue Position",
        description = "Where to place the FR along the fruit",
        default     = .02,
        min         = 0,
        soft_max    = .05
    )
    
    fr_length : FloatProperty(
        name        = "Flower Residue Length",
        description = "Length of the FR, relative to fruit size",
        default     = .05,
        min         = 0,
        soft_min    = 0.01, soft_max     = .1
    )
    
    fr_petals : IntProperty(
        name        = "Num Petals",
        description = "Number of petal remains",
        default     = 5,
        min         = 3,
        soft_max    = 13
    )

#############################################

class StemProps(PropertyGroup):
    
    stem_present : BoolProperty(
        name        = "Add stem",
        description = "Whether to add a stem to the model",
        default     = True
    )
    
    stem_radius : FloatProperty(
        name        = "Stem Radius",
        description = "Determines where the stem meets the fruit and thus also the radius",
        default     = .01,
        min         = 0,
        soft_min    = .005, soft_max    = .02
    )
    
    stem_length : FloatProperty(
        name        = "Stem Length",
        description = "Length of the stem, relative to fruit length",
        default     = .15,
        min         = 0,
        soft_min    = 0.1, soft_max     = .25
    )
    
    stem_bending : FloatProperty(
        name        = "Stem Bending",
        description = "How strongly the stem bends sideways",
        default     = 0,
        min         = 0,
        soft_max    = 1
    )

#############################################

class FruitProperties(PropertyGroup):
        
    length : FloatProperty(
        name        = "Length",
        description = "Length of the fruit",
        default     = .5,
        min         = 0,
        soft_min    = 0.2, soft_max     = 1
    )
    
    upperAngle : FloatProperty(
        name        = "Upper angle",
        description = "How broad or narrow the fruit is at the top",
        subtype     = 'ANGLE',
        default     = 0,
        min         = -PI/2,
        soft_min    = -.375*PI, soft_max    = .375*PI
    )
    
    middleAngle : FloatProperty(
        name        = "Middle Angle",
        description = "Inclination at the girdle",
        subtype     = 'ANGLE',
        default     = 0,
        soft_min    = -.125*PI, soft_max     = .125*PI
    )
    
    lowerAngle : FloatProperty(
        name        = "Lower angle",
        description = "How broad or narrow the fruit is at the bottom",
        subtype     = 'ANGLE',
        default     = 0,
        soft_min    = -.375*PI, soft_max    = .375*PI,
    )
    
    radius : FloatProperty(
        name        = "Width",
        description = "Horizontal radius of the fruit at the girdle",
        default     = .1,
        min         = 0,
        soft_min    = 0.05, soft_max     = .2
    )
    
    girdlePosition : FloatProperty(
        name        = "Girdle Position",
        description = "Relative positioning of the girdle along the length of the fruit",
        default     = .6,
        min         = .1, max = .9,
        soft_min    = 0.4, soft_max     = .8
    )
    
    colour : FloatVectorProperty(
        name        = "Colour",
        description = "Colour of the fruit",
        size        = 3,
        subtype     = 'COLOR',
        default     = (0, 0, 0),
        min         = 0, max = 1
    )
    
    grooves : IntProperty(
        name        = "Grooves",
        description = "The fruit will have this many grooves",
        default     = 2,
        min         = 0,
        soft_max    = 10
    )
    
    groovepower : FloatProperty(
        name        = "Groove Shape",
        description = "How sharp the grooves are",
        default     = 1,
        min         = 0,
        soft_max    = 8
    )
    
    grooveDepth : FloatProperty(
        name        = "Groove Depth",
        description = "How deep the grooves are. Expressed as relative offset around base radius, so negative values invert the grooves",
        default     = .25,
        soft_min    = -.5, soft_max    = .5
    )
    
    curved : BoolProperty(
        name        = "Is Curved",
        description = "Whether to apply the curve parameters",
        default     = False
    )
    
    curvePosVertical : FloatProperty(
        name        = "Curve Height",
        description = "Vertical position of the curvature",
        default     = .5,
        min         = 0, max = 1,
        soft_min    = .1, soft_max = .9
    )
    
    curveEccentricity : FloatProperty(
        name        = "Curve Eccentricity",
        description = "Intensity of curvature",
        default     = 0,
        min         = 0,
        soft_max = .75
    )

classes = (
    FlowerResidueProps,
    StemProps,
    FruitProperties,
    )

def register():
    for cla in classes:
        register_class(cla)
def unregister():
    for cla in classes:
        unregister_class(cla)

