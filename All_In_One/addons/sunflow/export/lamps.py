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
# Created on                          12-Aug-2013
# Author                              NodeBench
# --------------------------------------------------------------------------


import bpy
import math
import mathutils

from .services import tr_color_str
from .services import mix
from .services import file_exists
from .services import getObjectPos

from ..outputs import sunflowLog


mappings = {
            'HEMI': 'spherical',
            'AREA': 'meshlight',
            'SUN': 'sunsky',
            'POINT': 'point',
            'SPOT': 'directional',
            'world_texture': 'ibl',
            'mesh': 'meshlight'
            }

def getObjectLampSize(light):    
    obj_matrix = light.matrix_world.copy()    
    size_x = light.data.size  
    size_y = light.data.size_y  
    pts = [ (-size_x / 2.0 , size_y / 2.0), (size_x / 2.0 , size_y / 2.0), (size_x / 2.0 , -size_y / 2.0), (-size_x / 2.0 , -size_y / 2.0)]    
    trArea = []
    for vert in pts:
        trArea.append([ "%+0.4f" % point for point in (obj_matrix * mathutils.Vector([vert[0], vert[1], 0, 1])).to_tuple() ])
    trFaces = [[0, 1, 2], [2, 3, 0]]
    return(trArea, trFaces)
    

def create_lamp_block(lamp):    

    name = lamp.data.type
    sfname = mappings[name]
    act_lit = [] 
    indent = 0
    space = "        "
    
    act_lit.append("%s %s %s" % (space * indent , "light ", "{"))
    indent += 1
    if sfname == 'point':
        act_lit.append("%s %s %s" % (space * indent , "type  ", "point"))        
        
        act_lit.append("%s %s %s" % (space * indent , "color   ", "{")) 
        indent += 1
        act_lit.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(lamp.data.color))) 
        act_lit.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
        
        act_lit.append("%s %s %s" % (space * indent , "power", "%+0.4f" % lamp.data.sunflow_lamp.lightRadiance))
        pos = getObjectPos(lamp , as_matrix=False)[0]
        act_lit.append("%s %s %s" % (space * indent , "p    ", pos))         
    
    elif sfname == 'meshlight':
        act_lit.append("%s %s %s" % (space * indent , "type  ", "meshlight"))   
        act_lit.append("%s %s %s" % (space * indent , "name  ", "BlenderAreaLamp"))             
        
        act_lit.append("%s %s %s" % (space * indent , "emit   ", "{")) 
        indent += 1
        act_lit.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(lamp.data.color))) 
        act_lit.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
        
        act_lit.append("%s %s %s" % (space * indent , "radiance", "%+0.4f" % lamp.data.sunflow_lamp.lightRadiance))
        act_lit.append("%s %s %s" % (space * indent , "samples ", lamp.data.sunflow_lamp.lightSamples))
        (trArea, trFaces) = getObjectLampSize(lamp)
        act_lit.append("%s %s %s" % (space * indent , "points   ", "4"))  
        indent += 1
        act_lit.append("%s %s %s %s" % (space * indent , trArea[0][0] , trArea[0][1] , trArea[0][2]))
        act_lit.append("%s %s %s %s" % (space * indent , trArea[1][0] , trArea[1][1] , trArea[1][2]))
        act_lit.append("%s %s %s %s" % (space * indent , trArea[2][0] , trArea[2][1] , trArea[2][2]))
        act_lit.append("%s %s %s %s" % (space * indent , trArea[3][0] , trArea[3][1] , trArea[3][2]))
        indent -= 1
        act_lit.append("%s %s %s" % (space * indent , "triangles", "2"))  
        indent += 1
        act_lit.append("%s %s %s %s" % (space * indent , trFaces[0][0] , trFaces[0][1] , trFaces[0][2]))
        act_lit.append("%s %s %s %s" % (space * indent , trFaces[1][0] , trFaces[1][1] , trFaces[1][2]))
        indent -= 1
    
    elif sfname == 'spherical':
        act_lit.append("%s %s %s" % (space * indent , "type  ", "spherical"))   
        
        act_lit.append("%s %s %s" % (space * indent , "color  ", "{")) 
        indent += 1
        act_lit.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(lamp.data.color))) 
        act_lit.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
        
        act_lit.append("%s %s %s" % (space * indent , "radiance", "%+0.4f" % lamp.data.sunflow_lamp.lightRadiance))
        pos = getObjectPos(lamp , as_matrix=False)[0]
        act_lit.append("%s %s %s" % (space * indent , "center  ", pos))
        act_lit.append("%s %s %s" % (space * indent , "radius  ", "%+0.4f" % lamp.data.sunflow_lamp.lightShericalRadius))
        act_lit.append("%s %s %s" % (space * indent , "samples ", lamp.data.sunflow_lamp.lightSamples))
        
    elif sfname == 'directional':
        act_lit.append("%s %s %s" % (space * indent , "type  ", "directional"))   
        position = getObjectPos(lamp , as_matrix=False)
        act_lit.append("%s %s %s" % (space * indent , "source  ", position[0]))
        act_lit.append("%s %s %s" % (space * indent , "target  ", position[1]))
        #----- radius = 10 * math.tan(math.radians((lamp.data.spot_size)) / 2.0)
        #-------------- the incomming value is in radians so no need to convert.
        radius = 10 * math.tan(lamp.data.spot_size / 2.0)
        
        act_lit.append("%s %s %s" % (space * indent , "radius  ", "%+0.4f" % radius))
                
        act_lit.append("%s %s %s" % (space * indent , "emit  ", "{")) 
        indent += 1
        act_lit.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(lamp.data.color))) 
        act_lit.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
        
        act_lit.append("%s %s %s" % (space * indent , "intensity ", "%+0.4f" % lamp.data.sunflow_lamp.lightRadiance))
      
    elif ((sfname == 'sunsky') & (bpy.context.scene.sunflow_world.worldLighting == 'sunsky')):   
        act_lit.append("%s %s %s" % (space * indent , "type  ", "sunsky"))   
        act_lit.append("%s %s %s" % (space * indent , "up    ", "0  0  1"))  

        act_lit.append("%s %s %s" % (space * indent , "east  ", lamp.data.sunflow_lamp.lightSunEast)) 
        
        pos = getObjectPos(lamp , as_matrix=False)[0]
        act_lit.append("%s %s %s" % (space * indent , "sundir  ", pos)) 
        
        act_lit.append("%s %s %s" % (space * indent , "turbidity", lamp.data.sky.atmosphere_turbidity))
        act_lit.append("%s %s %s" % (space * indent , "samples ", lamp.data.sunflow_lamp.lightSamples))
        
    elif ((sfname == 'sunsky') & (bpy.context.scene.sunflow_world.worldLighting != 'sunsky')):        
        act_lit.append("%s %s %s" % (space * indent , "type  ", "directional"))   
        position = getObjectPos(lamp , as_matrix=False)
        act_lit.append("%s %s %s" % (space * indent , "source  ", position[0]))
        act_lit.append("%s %s %s" % (space * indent , "target  ", position[1]))
        radius = 10000        
        act_lit.append("%s %s %s" % (space * indent , "radius  ", "%+0.4f" % radius))                
        act_lit.append("%s %s %s" % (space * indent , "emit  ", "{")) 
        indent += 1
        act_lit.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', tr_color_str(lamp.data.color))) 
        act_lit.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1        
        act_lit.append("%s %s %s" % (space * indent , "intensity ", "%+0.4f" % lamp.data.sunflow_lamp.lightRadiance))
        
    act_lit.append("%s %s %s" % (space * indent , "}", "")) 
    indent -= 1
    return ({ 'lamp' : act_lit })
    


def world_ibl_lighting(scene):
    act_lit = []
    indent = 0
    space = "        "
    
    if scene.sunflow_world.worldLighting != 'ibl' :  
        return { 'world' : act_lit }   
     
    sfworld = scene.sunflow_world
    if sfworld.texturename is None:        
        return { 'world' : act_lit }
    
    if sfworld.texturename not in scene.world.texture_slots.keys():
        return { 'world' : act_lit }
    
    world_tex = scene.world.texture_slots[sfworld.texturename]
    if world_tex is None:        
        return { 'world' : act_lit }
    
    if world_tex.texture.type != 'IMAGE':        
        return { 'world' : act_lit }
    
    if world_tex.texture.image is None:        
        return { 'world' : act_lit }
    
    if world_tex.texture.image.filepath is None:        
        return { 'world' : act_lit }
    
    if not file_exists(world_tex.texture.image.filepath):
        return { 'world' : act_lit }
    
    image_path = world_tex.texture.image.filepath
    
    act_lit.append("%s %s %s" % (space * indent , "light ", "{"))
    indent += 1
    act_lit.append("%s %s %s" % (space * indent , "type  ", "ibl")) 
    act_lit.append("%s %s %s" % (space * indent , "image", '"' + image_path + '"'))
    coord = "%+0.4f %+0.4f %+0.4f" % sfworld.worldCenter.to_tuple() 
    act_lit.append("%s %s %s" % (space * indent , "center  ", coord)) 
    act_lit.append("%s %s %s" % (space * indent , "up  ", sfworld.worldUPString)) 
    act_lit.append("%s %s %s" % (space * indent , "lock   ", sfworld.iblLock)) 
    act_lit.append("%s %s %s" % (space * indent , "samples", sfworld.iblSamples)) 
    act_lit.append("%s %s %s" % (space * indent , "}", "")) 
    indent -= 1
    
    return { 'world' : act_lit }

#===============================================================================
# getLamps
#===============================================================================
def getLamps(scene):
    
    scene_lamps = [ lm for lm in scene.objects if lm.type == 'LAMP' ]
    SceneLamps = {}
    for lamp in scene_lamps:
        if not hasattr(lamp.data , 'sunflow_lamp'):
            sunflowLog("Not sunflow lamp")
            continue
        lamps = create_lamp_block(lamp)
        mix(SceneLamps , lamps , lamp.name)   
    
    world = world_ibl_lighting(scene)
    mix(SceneLamps , world , 'worldlight') 
    
    return SceneLamps

