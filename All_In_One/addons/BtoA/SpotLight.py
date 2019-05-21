import imp
import math
from arnold import *
from . import utils

if "bpy" in locals():
    imp.reload(BaseLight)
else:
    import bpy
    from . import BaseLight


class SpotLight(BaseLight.BaseLight):
    
    def __init__(self, light):
        super(SpotLight,self).__init__(light)
         
    def write(self):
        self.alight = AiNode(b"spot_light")
        # set the matrix
        # fist apply the matrix
        matrices = AiArrayAllocate(1, 1, AI_TYPE_MATRIX);
        lmatrix = self.light.matrix_world
        matrix = utils.getYUpMatrix(lmatrix)
        AiArraySetMtx(matrices,  0 , matrix)
        AiNodeSetArray(self.alight, b"matrix", matrices)
        
        # Write common attributes
        super(SpotLight,self).write()

        # Write spotlight attrs
        AiNodeSetFlt(self.alight,b"cone_angle",math.degrees(self.lightdata.spot_size))
        AiNodeSetFlt(self.alight,b"penumbra_angle",
                    math.degrees(self.lightdata.BtoA_penumbra_angle))
        AiNodeSetFlt(self.alight,b"aspect_ratio",self.lightdata.BtoA_aspect_ratio)
