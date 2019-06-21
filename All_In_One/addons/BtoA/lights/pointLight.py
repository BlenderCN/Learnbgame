import imp
from arnold import *
from ..GuiUtils import pollLight
from ..BaseLight import BaseLight

from mathutils import Matrix
from bpy.props import (CollectionProperty,StringProperty, BoolProperty,
                       IntProperty, FloatProperty, FloatVectorProperty,
                       EnumProperty, PointerProperty)
from bl_ui import properties_data_lamp
pm = properties_data_lamp

if "bpy" not in locals():
    import bpy

enumValue = ("POINTLIGHT","Point","")
blenderType = "POINT"

# There must be one class that inherits from bpy.types.PropertyGroup
# Here we place all the parameters for the Material
class BtoAPointLightSettings(bpy.types.PropertyGroup):
    opacity = FloatProperty(name="Opacity",default=1)

className = BtoAPointLightSettings
bpy.utils.register_class(className)

def write(li):
    blight = BaseLight(li)    
    blight.alight = AiNode(b"point_light")
    AiNodeSetStr(blight.alight,b"name",blight.lightdata.name.encode('utf-8'))
    # set position
    # fist apply the matrix
    lmatrix = Matrix.Rotation(math.radians(-90),4,'X') * blight.light.matrix_world
    lpos = lmatrix.to_translation()
    positions = AiArrayAllocate(1,1,AI_TYPE_POINT)
    AiArraySetPnt(positions,0,AtPoint(lpos.x,lpos.y,lpos.z))
    AiNodeSetArray(blight.alight,b'position',positions)
    # write all common attributes
    blight.write()

