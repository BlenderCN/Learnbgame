import bpy
from mathutils import Matrix
from arnold import *

class BaseLight():
    def __init__(self, light):
        self.lightdata = light 
        self.light = bpy.context.scene.objects[light.name]
        self.alight = None

    def write(self):
        ld = self.lightdata
        bl = ld.BtoA
        # intensity and color
        AiNodeSetStr(self.alight,b"name",ld.name.encode('utf-8'))
        AiNodeSetFlt(self.alight,b"intensity",ld.energy)
        AiNodeSetFlt(self.alight,b"exposure",bl.exposure)
        AiNodeSetRGB(self.alight,b"color",ld.color.r,ld.color.g,ld.color.b)
        
        AiNodeSetBool(self.alight,b"mis",bl.mis)
        # bounces
        AiNodeSetInt(self.alight,b"bounces",bl.bounces)
        AiNodeSetFlt(self.alight,b"bounce_factor",bl.bounce_factor)

        # shadows
        if not self.lightdata.BtoA.shadow_enable:
            AiNodeSetBool(self.alight,b"cast_shadows",0)
        else:
            scol = self.lightdata.shadow_color
            AiNodeSetRGB(self.alight,b"shadow_color",scol.r,scol.g,scol.b)
            AiNodeSetFlt(self.alight,b"shadow_density",self.lightdata.BtoA.shadow_density)
            AiNodeSetFlt(self.alight,b"radius",self.lightdata.shadow_soft_size)
            AiNodeSetInt(self.alight,b"samples",self.lightdata.shadow_ray_samples)
            
            AiNodeSetBool(self.alight,b"affect_diffuse",self.lightdata.use_diffuse)
            AiNodeSetBool(self.alight,b"affect_specular",self.lightdata.use_specular)
        
