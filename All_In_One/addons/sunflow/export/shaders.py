# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Version                     2.68
# Exporter Version                    0.0.4
# Created on                          10-Aug-2013
# Author                              NodeBench
# --------------------------------------------------------------------------

import os
import bpy
import math

from .services import tr_color_str
from .services import make_path_real
from .services import mix
from ..outputs import sunflowLog
    
def texture_path(mat, mat_slot):
    return make_path_real(mat.texture_slots[mat_slot - 1].texture.image.filepath)
        
def texture_found(mat, mat_type):
    slots = len(mat.texture_slots)
    if slots <= 0:
        return 0
    for mat_slot in range(slots):
        slot = mat.texture_slots[mat_slot]
        # sunflowLog (slot)
        if not slot:
            continue
        if not (hasattr(slot , 'texture') & (slot.texture is not None)):
            continue
        if not ((slot.texture_coords == 'UV') & (slot.texture.type == 'IMAGE')):
            continue
        if not (hasattr(slot.texture , 'image') & (slot.texture.image is not None)):
            continue
        if not (slot.texture.image.packed_file is None):
            continue
        if (slot.texture.image.filepath is None):
            continue
        path = mat.texture_slots[mat_slot].texture.image.filepath
        path = make_path_real(path)
        
        if not os.path.exists(path):
            continue
        if (slot.use_map_color_diffuse & (mat_type == 0)):
            return mat_slot + 1
        if (slot.use_map_color_spec & (mat_type == 1)):
            return mat_slot + 1
        if (slot.use_map_normal & (mat_type == 2)):
            return mat_slot + 1
        if (slot.use_map_displacement & (mat_type == 3)):
            return mat_slot + 1
    return 0


def create_shader_block(mat):
    sfmat = mat.sunflow_material
    name = mat.name
    act_mat = [] 
    indent = 0
    space = "        "
    type_meshlight = False 
    type_shader = False
    type_modifier = False
    
    act_mat.append("%s %s %s" % (space * indent , "shader", "{"))
    indent += 1
    act_mat.append("%s %s %s" % (space * indent , "name", '"' + name + '"'))
    act_mat.append("%s %s %s" % (space * indent , "type", sfmat.type))
    if sfmat.type == 'constant':        
        act_mat.append("%s %s %s" % (space * indent , "color  ", "{")) 
        indent += 1
        act_mat.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(sfmat.constantEmit * sfmat.diffuseColor))) 
        act_mat.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
        type_shader = True
    elif sfmat.type == 'diffuse':   
        if texture_found(mat , 0):  # 0 means diffuse channel
            texpath = '"' + texture_path(mat , texture_found(mat , 0)) + '"'
            act_mat.append("%s %s %s" % (space * indent , "texture ", texpath))      
        else:
            act_mat.append("%s %s %s" % (space * indent , "diff ", "{")) 
            indent += 1
            act_mat.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(sfmat.diffuseColor))) 
            act_mat.append("%s %s %s" % (space * indent , "}", "")) 
            indent -= 1
        type_shader = True
    elif sfmat.type == 'phong':     
        if texture_found(mat , 0):  # 0 means diffuse channel
            texpath = '"' + texture_path(mat , texture_found(mat , 0)) + '"'
            act_mat.append("%s %s %s" % (space * indent , "texture ", texpath))    
        else:
            act_mat.append("%s %s %s" % (space * indent , "diff  ", "{")) 
            indent += 1
            act_mat.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(sfmat.diffuseColor))) 
            act_mat.append("%s %s %s" % (space * indent , "}", "")) 
            indent -= 1
        
        # spec channel
        act_mat.append("%s %s %s" % (space * indent , "spec  ", "{")) 
        indent += 1
        act_mat.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(sfmat.specularColor))) 
        act_mat.append("%s %s %s" % (space * indent , "}", sfmat.phongSpecHardness)) 
        indent -= 1
        
        act_mat.append("%s %s %s" % (space * indent , "samples", sfmat.phongSamples)) 
        type_shader = True
    elif sfmat.type == 'shiny':  
        if texture_found(mat , 0):  # 0 means diffuse channel
            texpath = '"' + texture_path(mat , texture_found(mat , 0)) + '"'
            act_mat.append("%s %s %s" % (space * indent , "texture ", texpath))        
        else:
            act_mat.append("%s %s %s" % (space * indent , "diff  ", "{")) 
            indent += 1
            act_mat.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(sfmat.diffuseColor))) 
            act_mat.append("%s %s %s" % (space * indent , "}", "")) 
            indent -= 1           
           
        if sfmat.shinyExponent :
            act_mat.append("%s %s %s" % (space * indent , "refl  ", "%+0.4f" % math.pow(10, 4 * sfmat.shinyReflection)))     
        else:
            act_mat.append("%s %s %s" % (space * indent , "refl  ", "%+0.4f" % sfmat.shinyReflection))     
        
        type_shader = True
    elif sfmat.type == 'glass':        

        act_mat.append("%s %s %s" % (space * indent , "eta  ", "%+0.4f" % sfmat.glassETA)) 

        act_mat.append("%s %s %s" % (space * indent , "color ", "{")) 
        indent += 1
        act_mat.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(sfmat.diffuseColor))) 
        act_mat.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
   
        act_mat.append("%s %s %s" % (space * indent , "absorbtion.distance", "%+0.4f" % sfmat.glassAbsDistance)) 
        
        act_mat.append("%s %s %s" % (space * indent , "absorbtion.color", "{")) 
        indent += 1
        act_mat.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(sfmat.glassAbsColor))) 
        act_mat.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
        type_shader = True        
    elif sfmat.type == 'mirror':
        
        act_mat.append("%s %s %s" % (space * indent , "refl  ", "{")) 
        indent += 1
        act_mat.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(sfmat.mirrorReflection))) 
        act_mat.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
        type_shader = True
    elif sfmat.type == 'ward':     
        if texture_found(mat , 0):  # 0 means diffuse channel
            texpath = '"' + texture_path(mat , texture_found(mat , 0)) + '"'
            act_mat.append("%s %s %s" % (space * indent , "texture ", texpath))    
        else:
            act_mat.append("%s %s %s" % (space * indent , "diff  ", "{")) 
            indent += 1
            act_mat.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(sfmat.diffuseColor))) 
            act_mat.append("%s %s %s" % (space * indent , "}", "")) 
            indent -= 1
        
        # spec channel
        act_mat.append("%s %s %s" % (space * indent , "spec  ", "{")) 
        indent += 1
        act_mat.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(sfmat.specularColor)))        
        act_mat.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
        
        act_mat.append("%s %s %s" % (space * indent , "rough ", "%+0.4f   %+0.4f" % (sfmat.wardRoughX  , sfmat.wardRoughY))) 
        act_mat.append("%s %s %s" % (space * indent , "samples", sfmat.wardSamples)) 
    
        type_shader = True
        
    elif sfmat.type == 'amb-occ':   
        if texture_found(mat , 0):  # 0 means diffuse channel
            texpath = '"' + texture_path(mat , texture_found(mat , 0)) + '"'
            act_mat.append("%s %s %s" % (space * indent , "texture ", texpath))      
        else:
            act_mat.append("%s %s %s" % (space * indent , "bright  ", "{")) 
            indent += 1
            act_mat.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(sfmat.ambientBright))) 
            act_mat.append("%s %s %s" % (space * indent , "}", "")) 
            indent -= 1
        
        # spec channel
        act_mat.append("%s %s %s" % (space * indent , "dark   ", "{")) 
        indent += 1
        act_mat.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(sfmat.ambientDark)))
        act_mat.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
        
        act_mat.append("%s %s %s" % (space * indent , "samples", sfmat.ambientSamples)) 
        act_mat.append("%s %s %s" % (space * indent , "dist  ", "%+0.4f" % (sfmat.ambientDistance))) 
        type_shader = True   
        
    elif sfmat.type == 'uber':        
        # diffuse channel
        act_mat.append("%s %s %s" % (space * indent , "diff  ", "{")) 
        indent += 1
        act_mat.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(sfmat.diffuseColor))) 
        act_mat.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
        # diffuse texture
        if  texture_found(mat , 0):  # 0 means diffuse channel
            texpath = '"' + texture_path(mat , texture_found(mat , 0)) + '"'
            act_mat.append("%s %s %s" % (space * indent , "diff.texture ", texpath)) 
            
        act_mat.append("%s %s %s" % (space * indent , "diff.blend", "%+0.4f" % (sfmat.uberDiffBlend)))
    
        # spec channel
        act_mat.append("%s %s %s" % (space * indent , "spec  ", "{")) 
        indent += 1
        act_mat.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(sfmat.specularColor)))        
        act_mat.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
        
        # spec texture
        if  texture_found(mat , 1):  # 1 means spec channel
            texpath = '"' + texture_path(mat , texture_found(mat , 1)) + '"'
            act_mat.append("%s %s %s" % (space * indent , "spec.texture ", texpath)) 
            
        act_mat.append("%s %s %s" % (space * indent , "spec.blend", "%+0.4f" % (sfmat.uberSpecBlend))) 
    
    
        act_mat.append("%s %s %s" % (space * indent , "glossy ", "%+0.4f" % (sfmat.uberGlossy))) 
        act_mat.append("%s %s %s" % (space * indent , "samples", sfmat.uberSamples)) 
    
        type_shader = True
    act_mat.append("%s %s %s" % (space * indent , "}", "")) 
    indent -= 1
        
    # special types -- not directly found in sunflow usual;
    if sfmat.type == "janino" :
        act_mat = []
        path = '"' + sfmat.janinoPath + '"'
        act_mat.append("%s %s %s" % (space * indent , "include", path)) 
        
    elif sfmat.type == "light" :
        act_mat = []
                
        indent += 1
        # diffuse channel        
        act_mat.append("%s %s %s" % (space * indent , "emit  ", "{")) 
        indent += 1
        act_mat.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(sfmat.diffuseColor))) 
        act_mat.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
        
        act_mat.append("%s %s %s" % (space * indent , "radiance", "%+0.4f" % (sfmat.lightRadiance))) 
        act_mat.append("%s %s %s" % (space * indent , "samples ", sfmat.lightSamples)) 
        indent -= 1
        type_meshlight = True
    

    act_mod = []
    if  texture_found(mat , 2) :        
        act_mod.append("%s %s %s" % (space * indent , "modifier", "{"))
        indent += 1
        act_mod.append("%s %s %s" % (space * indent , "name ", '"' + name + '.m"'))
        act_mod.append("%s %s %s" % (space * indent , "type", "bump"))
        act_mod.append("%s %s %s" % (space * indent , "texture ", '"' + texture_path(mat , texture_found(mat , 2)) + '"'))
        act_mod.append("%s %s %s" % (space * indent , "scale", "%+0.4f" % (10.0 * mat.texture_slots[texture_found(mat , 2) - 1].normal_factor)))
        act_mod.append("%s %s %s" % (space * indent , "}", ""))
        indent -= 1
        type_modifier = True
    elif  texture_found(mat , 3)  :        
        act_mod.append("%s %s %s" % (space * indent , "modifier", "{"))
        indent += 1
        act_mod.append("%s %s %s" % (space * indent , "name ", '"' + name + '.m"'))
        act_mod.append("%s %s %s" % (space * indent , "type", "normalmap"))
        act_mod.append("%s %s %s" % (space * indent , "texture ", '"' + texture_path(mat , texture_found(mat , 3)) + '"'))
        act_mod.append("%s %s %s" % (space * indent , "scale", "%+0.4f" % (10.0 * mat.texture_slots[texture_found(mat , 3) - 1].displacement_factor)))
        act_mod.append("%s %s %s" % (space * indent , "}", ""))
        indent -= 1
        type_modifier = True
        
    report = {}
        
    if type_shader:
        report['Shader'] = act_mat[:]
    else:
        report['Shader'] = []    
    
    if type_meshlight:
        report['Shaderlight'] = act_mat[:]
    else:
        report['Shaderlight'] = []
    
    if type_modifier:
        report['Shadermodifier'] = act_mod[:]
    else:
        report['Shadermodifier'] = []
    
    del act_mat
    
    return report
        

#===============================================================================
# getShadersInScene
#===============================================================================
def getShadersInScene(scene):
    
    scene_mat = bpy.data.materials
    SceneMaterials = {}
    for mat in scene_mat:
        if mat.users <= 0 :
            sunflowLog("Material has no owner")
            continue
        if not hasattr(mat , 'sunflow_material'):
            sunflowLog("Not sunflow material")
            continue
        shaders = create_shader_block(mat)
        mix(SceneMaterials , shaders , mat.name)   
    return SceneMaterials    
