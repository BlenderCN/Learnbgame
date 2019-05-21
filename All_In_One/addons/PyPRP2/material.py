#    This file is part of PyPRP2.
#    
#    Copyright (C) 2010 PyPRP2 Project Team
#    See the file AUTHORS for more info about the team.
#    
#    PyPRP2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    PyPRP2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with PyPRP2.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from PyHSPlasma import *
import utils
import os
import hashlib
import buildplmipmap

def SetLayerColorToBlMat(layer, material):
    dcolor = material.diffuse_color
    layer.runtime = hsColorRGBA(dcolor[0],dcolor[1],dcolor[2],1.0)
    layer.preshade = hsColorRGBA(dcolor[0],dcolor[1],dcolor[2],1.0)
    layer.ambient = hsColorRGBA.kBlack
    scolor = material.specular_color
    layer.specular = hsColorRGBA(scolor[0],scolor[1],scolor[2],1.0)
    return layer

def SetLayerFlagsAlpha(layer):
    if layer.state.blendFlags & hsGMatState.kBlendAddColorTimesAlpha:
        layer.state.blendFlags |= hsGMatState.kBlendAlphaAdd
    elif layer.state.blendFlags & hsGMatState.kBlendMult:
        layer.state.blendFlags |= hsGMatState.kBlendAlphaMult
    else:
        layer.state.blendFlags |= hsGMatState.kBlendAlpha
        
def SetLayerFlags(slot,layer,material):
    #blendflags
    if slot.blend_type == "ADD":
        layer.state.blendFlags |= hsGMatState.kBlendAddColorTimesAlpha
    elif slot.blend_type == "MULTIPLY":
        layer.state.blendFlags |= hsGMatState.kBlendMult
    elif slot.blend_type == "SUBTRACT":
        layer.state.blendFlags |= hsGMatState.kBlendSubtract
    #miscflags
    if material.type == "WIRE":
        layer.state.miscFlags |= hsGMatState.kMiscWireFrame

def HandleMipmap(texture):
    srcpath = bpy.path.abspath(texture.image.filepath)
    cachepath = os.path.join(bpy.path.abspath(bpy.context.scene.world.plasma_age.export_dir), "texcache")
    imagename = os.path.split(srcpath)[1]
    cachename = os.path.splitext(imagename)[0]
    cachefilepathfull = os.path.join(cachepath,cachename)

    mipmap = plMipmap(cachename)
    imgsstream = hsFileStream()
    files_exist = False
    src_checksum = None
    have_to_process = True
    
    if not os.path.exists(cachepath):
        os.mkdir(cachepath)     # mkdirs isn't necessary - the exporter will have guaranteed the parent exists by now

    try:
        open(cachefilepathfull)#this shouldn't create a memory leak
        src_checksum = open(cachefilepathfull+"_src.md5")#this shouldn't create a memory leak                        
        files_exist = True
    except:
        pass
    if files_exist: #we still need to check the sum
        srctex = open(srcpath,"rb")
        if hashlib.md5(srctex.read()).hexdigest() == src_checksum.read():
            print("Texture %s is the same as last time"%imagename)
            have_to_process = False
        else:
            print("Texture %s has been changed.  Recompressing..."%imagename)
        srctex.close()
        src_checksum.close()
    if have_to_process:
        #create checksum
        src_checksum = open(cachefilepathfull+"_src.md5","w")
        srctex = open(srcpath,"rb")
        src_checksum.write(hashlib.md5(srctex.read()).hexdigest())
        srctex.close()
        src_checksum.close()
        #compress texture
        if texture.use_alpha:
            compresstype = 5
        else:
            compresstype = 1
        buildplmipmap.build(srcpath, cachefilepathfull, "mipmap", compresstype)

    imgsstream.open(cachefilepathfull, fmRead)
    mipmap.readData(imgsstream)
    imgsstream.close()
    return mipmap

                    
def ExportMaterial(rm, loc, material):
    mat = hsGMaterial(material.name)
    rm.AddObject(loc,mat)

    for slot in material.texture_slots:
        if slot:
            texture = slot.texture
            layer = plLayer(texture.name)
            SetLayerFlags(slot,layer, material)
            SetLayerColorToBlMat(layer,material)
            
            if texture.type == "NONE":
                pass
            elif texture.type == "IMAGE":
                if texture.image.source == "FILE":
                    mm = HandleMipmap(texture)
                    rm.AddObject(loc,mm)
                    layer.texture = mm.key
            else:
                continue #we do not support the selected layer type
            
            rm.AddObject(loc,layer)
            mat.addLayer(layer.key)

    if len(mat.layers) == 0: #save the day with an autogenerated layer
        layer = plLayer("%s_auto_layer"%material.name)
        SetLayerColorToBlMat(layer,material)
        rm.AddObject(loc,layer)
        mat.addLayer(layer.key)

    return mat


