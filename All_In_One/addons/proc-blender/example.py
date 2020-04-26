import bpy
import mathutils
import math
import random

from math import pi as PI
from mathutils import Vector
from .spline import Bezier, screw
from .util import optional, makeDiffuseMaterial
from .evolution import Evolvable


class ExampleProperties:
    """
    The parameters of your Evolvable are defined as bpy.props .
    Currently, float, int and bool properties are supported (including their vector variants).
    You don't have to define the properties in a separate class like this, but it might improve code structure.
    
    For every property you must define name, description and a default value.
    Vector props also require a size.
    
    For float and int props you need to define min or soft_min (you can define both).
    min is a hard lower bound to the range of valid values. It is best used for technical restrictions.
    soft_min is a limit to the range of reasonable values, though outliers are possible. It is best used for aestethical (e.g. scale) restrictions.
    The analogue applies to max and soft_max.
    """
    
    radius = bpy.props.FloatProperty(
        name        = "radius",
        description = "Lorem ipsum dolor sit",
        default     = .2,
        min         = 0,
        soft_min    = 0.01, soft_max     = .5
    )
    
    fvEx = bpy.props.FloatVectorProperty(
        name        = "FooBar",
        description = "Lorem ipsum dolor sit",
        size        = 3,
        default     = (1, 1, 1),
        min         = 0,    max = 10
    )
    
    iEx = bpy.props.IntProperty(
        name        = "FooBar",
        description = "Lorem ipsum dolor sit",
        default     = 2,
        min         = 0,    max = 10
    )
    
    ivEx = bpy.props.IntVectorProperty(
        name        = "FooBar",
        description = "Lorem ipsum dolor sit",
        size        = 3,
        default     = (1, 1, 1),
        min         = 0,    max = 10
    )
    
    bEx = bpy.props.BoolProperty(
        name        = "FooBar",
        description = "Lorem ipsum dolor sit",
        default     = True
    )
    
    bvEx = bpy.props.BoolVectorProperty(
        name        = "FooBar",
        description = "Lorem ipsum dolor sit",
        size        = 3,
        default     = (False, True, False)
    )

#############################################

class Example(Evolvable, ExampleProperties):
    
    # the label is used in the bl_label of the operators provided by Evolvable
    label = "Example"

    # the identifier is used in the bl_idname of the operators provided by Evolvable
    # also, the data bpy.types.Object.<identifier> will be used for loading/storing instances of this Evolvable
    identifier = "example"
    
    # you should call Evolvable.__init__ to init all properties with their default value
    # if you need your own __init__, make sure it has no required parameters and accepts kwargs like Evolvable.__init__
    __init__ = Evolvable.__init__

    def toMesh(self, LOD=10):
        """
        Create a bpy.data.meshes instance from this Evolvable. Here you define how the properties translate into a mesh.
        The method must be callable without parameters, so provide meaningful default values (except for self, of course).
        LOD (level of detail) is just an example and can be omitted.
        It is usually called through Evolvable.toMeshObject, which does some decoration.
        """
        # this example just creates a circle
        verts, faces = screw(Bezier([Vector([0,0,0]), Vector([self.radius, 0, 0])]), LODr=2, LODp=LOD)
        
        newMesh = bpy.data.meshes.new("Circle")
        newMesh.from_pydata(verts, [], faces)
        newMesh.update()
        
        # add some colour, why not?
        newMesh.materials.append(makeDiffuseMaterial([1,1,0]))
        for p in range(len(faces)):
                newMesh.polygons[p].material_index = 0
        
        return newMesh

#############################################

# example generation functions

def gen1():
    "first generator"
    circle = Example()
    circle.radius = random.uniform(.1, .5) # !! when setting properties directly, min/max are not checked !!
    return circle

def gen2():
    "second generator"
    circle = Example()
    circle.radius = random.uniform(.2, .4)
    return circle

# the generators are processed for use in an EnumProperty
generatorFuncs = gen1, gen2
generatorMap = {f.__name__ : f for f in generatorFuncs}
generatorEnums = [(f.__name__, f.__name__, optional(f.__doc__, "")) for f in generatorFuncs]
