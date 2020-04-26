import imp
from arnold import *
from bpy.props import CollectionProperty,StringProperty, BoolProperty, IntProperty, FloatProperty, FloatVectorProperty, EnumProperty, PointerProperty

if "bpy" in locals():
    pass
else:
    import bpy

from bl_ui import properties_texture
pm = properties_texture

for member in dir(pm):
    subclass = getattr(pm, member)
    try:
        #print (subclass.bl_label)
        if subclass.bl_label not in ["xxxreview"]:
            subclass.COMPAT_ENGINES.add('BtoA')
            pass
    except:
        pass

def writeImage(tex):
    outnode = AiNode(b"image")
    AiNodeSetStr(outnode,b"filename",tex.filepath.encode('utf-8'))
    return outnode

#STRING        filename                          
#BOOL          sflip                             false
#BOOL          tflip                             false
#BOOL          swap_st                           false
#FLOAT         sscale                            1
#FLOAT         tscale                            1
#ENUM          filter                            smart_bicubic
#BOOL          single_channel                    false
#INT           mipmap_bias                       0
#ENUM          swrap                             periodic
#ENUM          twrap                             periodic
#POINT2        uvcoords                          0, 0
#STRING        name                              default_name

class Textures:
    def __init__(self, scene):
        self.scene = scene
        self.texturesDict = {}

    def writeTextures(self):
        for tex in bpy.data.textures:
            self.writeTexture(tex)

    def writeTexture(self,tex):
        outtex = None
        if tex.type == "IMAGE":
            outtex = writeImage(tex.image)

        AiNodeSetStr(outtex,b"name",tex.name.encode('utf-8'))
        self.texturesDict[tex.as_pointer()] = {'name':tex.name,'pointer':outtex}
        return outtex
