import bpy

from bpy.props import StringProperty, PointerProperty, IntProperty
from bpy.props import BoolProperty, FloatProperty, CollectionProperty
from bpy.props import FloatVectorProperty, EnumProperty

prim_extrude = [('TITLE', 'Extrusion Types', ""),
                ("LINEAR", "Linear", ""),
                ("CIRCULAR", "Circular", "")]

class B2RexPrimProps(bpy.types.PropertyGroup):
    extrapolationType = EnumProperty(items=prim_extrude, default='LINEAR', description='')
    sides = IntProperty(name="sides", min=3, max=50)
    hollowSides = IntProperty(name="hollowSides", min=3, max=50)
    profile = FloatVectorProperty(name="profile", size=2, min=0.0, max=1.0,
                                  default=(0.0, 1.0), description='profile start/end')

    hollow = FloatProperty(name="hollow", min=0.0, max=1.0)
    radius = FloatProperty(name="radius", min=-1.0, max=1.0, default=0.0)

    twist = FloatVectorProperty(name="twist", size=2, min=-1.0, max=1.0,
                                  default=(0.0, 0.0), description='twist start/end')

    topShear= FloatVectorProperty(name="shear", size=2, min=-0.5, max=0.5,
                                  default=(0.0, 0.0),
                                  description='shear x/y')


    pathCut = FloatVectorProperty(name="path", size=2, min=0.0, max=1.0,
                                  default=(0.0, 1.0),
                                  description="path start/end")
    #dimpleBegin = FloatProperty(name="dimpleBegin", min=0.0, max=1.0)
    #dimpleEnd = FloatProperty(name="dimpleEnd", min=0.0, max=1.0)
    skew = FloatProperty(name="skew", min=0.0, max=0.95)
    holeSize= FloatVectorProperty(name="pathScale", size=2, min=0.0, max=1.0,
                                  default=(1.0, 0.25),
                                  description='pathScale x/y')
    taper = FloatVectorProperty(name="taper", size=2, min=-1.0, max=1.0,
                                default=(0.0, 0.0),
                                description='taper x/y')
    revolutions = FloatProperty(name="revolutions", min=0.1, max=3.0,
                                default=1.0)
    stepsPerRevolution = IntProperty(name="stepsPerRevolution", min=1, max=100,
                                    default=24)



