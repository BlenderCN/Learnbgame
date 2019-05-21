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
# Created on                          13-Aug-2013
# Author                              NodeBench
# --------------------------------------------------------------------------

import bpy
from ..outputs import sunflowLog
from .services import getObjectPos
from .services import tr_color_str
from .services import mix


def occlu_select_color(scene):
    occlu_color = {}
    occlu_color['horizon'] = tr_color_str(scene.world.horizon_color)
    occlu_color['zenith'] = tr_color_str(scene.world.zenith_color)
    occlu_color['ambient'] = tr_color_str(scene.world.ambient_color)
    return occlu_color


def scene_gi():
    
    act_Illum = [] 
    indent = 0
    space = "        "
    
    scene = bpy.context.scene
    sunflow_integrator = scene.sunflow_integrator
    gi = sunflow_integrator.globalIllumination
    if gi == 'none':
        return { 'gi' : act_Illum }
    
    act_Illum.append("%s %s %s" % (space * indent , "gi    ", "{"))
    indent += 1
    if gi == 'finalgathering':        
        act_Illum.append("%s %s %s" % (space * indent , "type", "irr-cache"))
        act_Illum.append("%s %s %s" % (space * indent , "samples", sunflow_integrator.fgSamples))
        act_Illum.append("%s %s %s" % (space * indent , "tolerance", "%+0.4f" % sunflow_integrator.fgTolerance))
        spacing = "%+0.4f  %+0.4f" % (sunflow_integrator.fgSpacingMin , sunflow_integrator.fgSpacingMax)
        act_Illum.append("%s %s %s" % (space * indent , "spacing", spacing))
        
        if sunflow_integrator.secondaryBounces:
            globalphmap = "%s %s %s %+0.4f" % (sunflow_integrator.globalPhotons,
                                     sunflow_integrator.globalMapping,
                                     sunflow_integrator.globalPhotonsEstimate,
                                     sunflow_integrator.globalPhotonsRadius,)
            act_Illum.append("%s %s %s" % (space * indent , "global", globalphmap))        
        
    elif gi == 'instantgi':
        b = float(sunflow_integrator.instantPercentBias) / 100.0
        act_Illum.append("%s %s %s" % (space * indent , "type", "igi"))
        act_Illum.append("%s %s %s" % (space * indent , "samples", sunflow_integrator.instantSamples))
        act_Illum.append("%s %s %s" % (space * indent , "sets", sunflow_integrator.instantSets))
        act_Illum.append("%s %s %s" % (space * indent , "b", "%+0.4f" % b))
        act_Illum.append("%s %s %s" % (space * indent , "bias-samples", sunflow_integrator.instantBiasSamples))
        
    elif gi == 'pathtracing':
        act_Illum.append("%s %s %s" % (space * indent , "type", "path"))
        act_Illum.append("%s %s %s" % (space * indent , "samples", sunflow_integrator.pathTracingSamples))
        
        
    elif gi == 'ambientocclusion':        
        act_Illum.append("%s %s %s" % (space * indent , "type", "ambocc"))
        
        occlu_color = occlu_select_color(scene)
        
        act_Illum.append("%s %s %s" % (space * indent , "bright", "{")) 
        indent += 1
        act_Illum.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', occlu_color[sunflow_integrator.occlusionBright])) 
        act_Illum.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
        
        act_Illum.append("%s %s %s" % (space * indent , "dark", "{")) 
        indent += 1
        act_Illum.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', occlu_color[sunflow_integrator.occlusionDark])) 
        act_Illum.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
        
        act_Illum.append("%s %s %s" % (space * indent , "samples", sunflow_integrator.occlusionSamples))
        act_Illum.append("%s %s %s" % (space * indent , "maxdist", "%+0.4f" % sunflow_integrator.occlusionDistance))
        
    elif gi == 'fakeambient':
        act_Illum.append("%s %s %s" % (space * indent , "type", "fake"))        
        
        obj = scene.objects[sunflow_integrator.upVectorEmpty]        
        pos = getObjectPos(obj , as_matrix=False)[0]
        act_Illum.append("%s %s %s" % (space * indent , "up", pos)) 
        
        occlu_color = occlu_select_color(scene)
        
        act_Illum.append("%s %s %s" % (space * indent , "sky", "{")) 
        indent += 1
        act_Illum.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', occlu_color[sunflow_integrator.fakeAOSky])) 
        act_Illum.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
        
        act_Illum.append("%s %s %s" % (space * indent , "ground", "{")) 
        indent += 1
        act_Illum.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', occlu_color[sunflow_integrator.fakeAOGround])) 
        act_Illum.append("%s %s %s" % (space * indent , "}", "")) 
        indent -= 1
            
    act_Illum.append("%s %s %s" % (space * indent , "}", "")) 
    indent -= 1
    return ({ 'gi' : act_Illum })


def scene_tracedepths():       
    act_Illum = [] 
    indent = 0
    space = "        "
    
    scene = bpy.context.scene
    sunflow_tracing = scene.sunflow_tracing
      
    act_Illum.append("%s %s %s" % (space * indent , "trace-depths", "{"))
    indent += 1
    act_Illum.append("%s %s %s" % (space * indent , "diff", sunflow_tracing.diffuseBounces))
    act_Illum.append("%s %s %s" % (space * indent , "refl", sunflow_tracing.reflectionDepth))
    act_Illum.append("%s %s %s" % (space * indent , "refr", sunflow_tracing.refractionDepth))    
    
    act_Illum.append("%s %s %s" % (space * indent , "}", "")) 
    indent -= 1
    return ({ 'trace' : act_Illum })


def scene_caustics():       
    act_Illum = [] 
    indent = 0
    space = "        "
     
    scene = bpy.context.scene
    sunflow_tracing = scene.sunflow_tracing
    
    if not sunflow_tracing.useCaustics :
        return ({ 'caustics' : act_Illum })
    act_Illum.append("%s %s %s" % (space * indent , "photons", "{"))
    indent += 1
    caustics = " %s %s %s %+0.4f" % (sunflow_tracing.causticPhotons , "kd" , sunflow_tracing.estimationPhotons , sunflow_tracing.estimationRadius)
    act_Illum.append("%s %s %s" % (space * indent , "caustics", caustics))    
    
    act_Illum.append("%s %s %s" % (space * indent , "}", "")) 
    indent -= 1
    return ({ 'caustics' : act_Illum })


def scene_output():
    act_Illum = [] 
    indent = 0
    space = "        "
     
    scene = bpy.context.scene

    act_Illum.append("%s %s %s" % (space * indent , "image", "{"))
    indent += 1
    
    resolution_width = scene.render.resolution_x * scene.render.resolution_percentage / 100.0
    resolution_height = scene.render.resolution_y * scene.render.resolution_percentage / 100.0
    resolution = "%d  %d" % (resolution_width , resolution_height)
    act_Illum.append("%s %s %s" % (space * indent , "resolution", resolution))    
    
    
    aa = "%s  %s" % (scene.sunflow_antialiasing.adaptiveAAMin , scene.sunflow_antialiasing.adaptiveAAMax)
    act_Illum.append("%s %s %s" % (space * indent , "aa", aa))   
    
    
    act_Illum.append("%s %s %s" % (space * indent , "samples", scene.sunflow_antialiasing.samplesAA))   
    act_Illum.append("%s %s %s" % (space * indent , "filter", scene.sunflow_antialiasing.imageFilter))   
    act_Illum.append("%s %s %s" % (space * indent , "jitter", scene.sunflow_antialiasing.jitterAA))   
    
    
    act_Illum.append("%s %s %s" % (space * indent , "}", "")) 
    indent -= 1
    return ({ 'output' : act_Illum })
    


def scene_bucket():    
    act_Illum = [] 
    indent = 0
    space = "        "     
    scene = bpy.context.scene
    bucket = "%s %s" % (scene.sunflow_performance.bucketSize , scene.sunflow_performance.bucketOrder)
    act_Illum.append("%s %s %s" % (space * indent , "bucket", bucket))        
    return ({ 'bucket' : act_Illum })



def scene_background():
    act_Illum = []
    indent = 0
    space = "        "
    
    scene = bpy.context.scene
    if scene.sunflow_world.worldLighting != 'papersky' :  
        return { 'background' : act_Illum }   
    
    act_Illum.append("%s %s %s" % (space * indent , "background", "{"))
    indent += 1
    
    act_Illum.append("%s %s %s" % (space * indent , "color", "{")) 
    indent += 1
    act_Illum.append("%s %s %s" % (space * indent , '"sRGB nonlinear"', occlu_select_color(scene)['horizon'])) 
    act_Illum.append("%s %s %s" % (space * indent , "}", "")) 
    indent -= 1

    act_Illum.append("%s %s %s" % (space * indent , "}", "")) 
    indent -= 1
    return ({ 'background' : act_Illum })


def scene_override():
    
    act_Illum = []
    indent = 0
    space = "        "
    
    scene = bpy.context.scene
    if scene.sunflow_integrator.giOverride == 'fullrender' :  
        return { 'background' : act_Illum } 
    elif scene.sunflow_integrator.giOverride == 'gionly' :
        act_Illum.append("%s %s %s" % (space * indent , "shader", "{"))
        indent += 1
        act_Illum.append("%s %s %s" % (space * indent , "name", "debug_gi"))
        act_Illum.append("%s %s %s" % (space * indent , "type", "view-irradiance"))
        act_Illum.append("%s %s %s" % (space * indent , "}", ""))
        indent -= 1
        act_Illum.append("%s %s %s" % (space * indent , "override", "debug_gi false"))
        
    elif scene.sunflow_integrator.giOverride == 'photonsonly' :   
        act_Illum.append("%s %s %s" % (space * indent , "shader", "{"))
        indent += 1
        act_Illum.append("%s %s %s" % (space * indent , "name", "debug_globals"))
        act_Illum.append("%s %s %s" % (space * indent , "type", "view-global"))
        act_Illum.append("%s %s %s" % (space * indent , "}", ""))
        indent -= 1
        act_Illum.append("%s %s %s" % (space * indent , "override", "debug_globals false"))
        
    else:
        pass
    return ({ 'override' : act_Illum })
    

#===============================================================================
# getIlluminationSettings
#===============================================================================
def getIlluminationSettings(scene): 
    
    IllumSettings = {}
    mix(IllumSettings , scene_gi() , 'illumination')    
    mix(IllumSettings , scene_tracedepths() , 'trace')    
    mix(IllumSettings , scene_caustics() , 'caustics') 
    mix(IllumSettings , scene_output() , 'output')
    mix(IllumSettings , scene_bucket() , 'bucket')
    mix(IllumSettings , scene_background() , 'background')
    mix(IllumSettings , scene_override() , 'override')
        
    return IllumSettings

