import imp
from mathutils import Matrix
from arnold import *

if "bpy" in locals():
    imp.reload(BaseLight)
else:
    import bpy
    from . import BaseLight

class PointLight(BaseLight.BaseLight):
    def __init__(self, light):
        super(PointLight,self).__init__(light)
         
    def write(self):
        self.alight = AiNode(b"point_light")
        AiNodeSetStr(self.alight,b"name",self.lightdata.name.encode('utf-8'))
        # set position
        # fist apply the matrix
        lmatrix = Matrix.Rotation(math.radians(-90),4,'X') * self.light.matrix_world
        lpos = lmatrix.to_translation()
        positions = AiArrayAllocate(1,1,AI_TYPE_POINT)
        AiArraySetPnt(positions,0,AtPoint(lpos.x,lpos.y,lpos.z))
        AiNodeSetArray(self.alight,b'position',positions)

        # Write common attributes
        super(PointLight,self).write()


