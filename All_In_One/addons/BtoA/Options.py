import bpy
from arnold import *

class Options:
    def __init__(self,render):
        self.scene = bpy.context.scene
        self.options = AiUniverseGetOptions()
        self.render = render
    
    def setOutput(self,filter,driver,outType="RGBA"):    
        outStr= "%s %s %s %s"%(outType,outType,filter,driver)
        outs = AiArray(1, 1, AI_TYPE_STRING, outStr.encode('utf-8'))
        AiNodeSetArray(self.options,b"outputs",outs)
   
    def setCamera(self,camera):
        AiNodeSetPtr(self.options,b"camera",camera)
    
    def writeOptions(self):
        AiNodeSetStr(self.options,b"name",b"options")
        AiNodeSetInt(self.options,b"xres",self.render.size_x)
        AiNodeSetInt(self.options,b"yres",self.render.size_y)
        #AiNodeSetFlt(self.options,b"aspect_ratio",self.render.size_y/self.render.size_x)
        
        #AiNodeSetFlt(self.options,b"AA_sample_clamp",0.5)
        
        # bucketing
        AiNodeSetInt(self.options,b"bucket_scanning",int(self.scene.BtoA.bucket_scanning))
        AiNodeSetInt(self.options,b"bucket_size",self.scene.BtoA.bucket_size)
        # AA Settings
        AiNodeSetInt(self.options,b"AA_samples",self.scene.BtoA.AA_samples)
        AiNodeSetInt(self.options,b"AA_seed",self.scene.BtoA.AA_seed)
        AiNodeSetInt(self.options,b"AA_pattern",int(self.scene.BtoA.AA_pattern))
        AiNodeSetInt(self.options,b"AA_motionblur_pattern",
                    int(self.scene.BtoA.AA_motionblur_pattern))
        AiNodeSetFlt(self.options,b"AA_sample_clamp",self.scene.BtoA.AA_sample_clamp)
        AiNodeSetBool(self.options,b"AA_sample_clamp_affects_aovs",
                    self.scene.BtoA.AA_clamp_affect_aovs)
        AiNodeSetInt(self.options,b"AA_sampling_dither",
                    self.scene.BtoA.AA_sampling_dither)
        
        # Ray Samples
        AiNodeSetInt(self.options,b"GI_diffuse_samples",self.scene.BtoA.GI_diffuse_samples)

        # Ray Depth
        AiNodeSetInt(self.options,b"GI_diffuse_depth",self.scene.BtoA.GI_diffuse_depth)
        AiNodeSetInt(self.options,b"GI_glossy_depth",self.scene.BtoA.GI_glossy_depth)
        AiNodeSetInt(self.options,b"GI_reflection_depth",self.scene.BtoA.GI_reflection_depth)
        AiNodeSetInt(self.options,b"GI_refraction_depth",self.scene.BtoA.GI_refraction_depth)


