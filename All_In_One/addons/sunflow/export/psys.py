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
# Created on                          23-Aug-2013
# Author                              NodeBench
# --------------------------------------------------------------------------

import math
import mathutils
# Framework libs
from extensions_framework import util as efutil

from .services import mix
from ..outputs import sunflowLog

def getPos(obj , as_matrix=True):
    obj_mat = obj.matrix.copy()
    obj_mat = obj_mat * obj.matrix_original.inverted()
    matrix_rows = [ "%+0.4f" % element for rows in obj_mat for element in rows ]
    return (matrix_rows)


def ParticleInstancing(scene , objname , motion_blur , mblur_steps):
    
    if not motion_blur:
        dupli_list = {}
        
        obj = scene.objects[objname]
        if not hasattr(obj, 'modifiers'):
            return dupli_list
        
        for mod in obj.modifiers :
            if mod.type == 'PARTICLE_SYSTEM':
                
                psys = mod.particle_system
                
                if psys.settings.type in [ 'HAIR' , 'EMITTER']:   
                    if psys.settings.render_type not in ['OBJECT', 'GROUP']:
                        continue
                    
                    obj.dupli_list_create(scene)
                    
                    for ob in obj.dupli_list:
                        if ob.hide :
                            continue
                        ins = {}  
                        pos = getPos(ob, as_matrix=True) 
                        ins['iname'] = "%s.inst.%s.%03d" % (obj.name, ob.object.name, ob.index)
                        ins['index'] = ob.index
                        ins['pname'] = ob.object.name
                        ins['trans'] = [pos]
                        dupli_list[ ins['iname'] ] = ins
                    obj.dupli_list_clear()
                    
        return dupli_list
    
# TODO: motion blur for particle instances.


#     else:
#         dupli_list = {}
#         
#         obj = scene.objects[objname]
#         if not hasattr(obj, 'modifiers'):
#             return dupli_list
#         
#         for mod in obj.modifiers :
#             if mod.type == 'PARTICLE_SYSTEM':
#                 
#                 psys = mod.particle_system
#                 
#                 if psys.settings.type in [ 'HAIR' , 'EMITTER']:   
#                     if psys.settings.render_type not in ['OBJECT', 'GROUP']:
#                         continue
#                     
#                     obj.dupli_list_create(scene)
#                     
#                     num_dupli = len(obj.dupli_list)
#                     for obj in obj.dupli_list :
#                         ins = {}  
#                         ins['iname'] = "%s.inst.%03d" % (obj.name, obj.index)
#                         ins['index'] = obj.index
#                         ins['pname'] = obj.object.name
#                         ins['trans'] = None
#                         dupli_list[ ins['iname'] ] = ins
#                     obj.dupli_list_clear()
#         
#                     current_frame , current_subframe = (scene.frame_current, scene.frame_subframe)
#                     mb_start = current_frame - math.ceil(mblur_steps / 2) + 1
#                     frame_steps = [ mb_start + n for n in range(0, mblur_steps) ]
#                     transform = [ [] for dummy_i in range(num_dupli)] 
#                     for sub_frame in frame_steps:
#                         scene.frame_set(sub_frame, current_subframe) 
#                         obj.dupli_list_create(scene)
#                         for objindx in range(num_dupli) :
#                             xpos = getPos(obj.dupli_list[objindx], as_matrix=True , grp=(obj.dupli_type == 'GROUP'))
#                             transform[objindx].append(xpos)
#                         obj.dupli_list_clear()
#                     scene.frame_set(current_frame, current_subframe)
#                     
#                     for dup in dupli_list.values():
#                         dup['trans'] = transform[dup['index']]            
#                     return dupli_list

                    
        
def getHairs(ob, mod, psys , hair_name):
    
    steps = psys.settings.draw_step
    steps = 2 ** steps + 1
    width = psys.settings.particle_size / 10.0
    num_parents = len(psys.particles)
    num_children = len(psys.child_particles)    
    
    act_hair = [] 
    indent = 0
    space = "        "
    
    
    act_hair.append("%s %s %s" % (space * indent , "object", "{"))
    indent += 1
    
    materials = ob.data.materials[:]
    material_names = [m.name if m else 'None' for m in materials]
    
    num_of_shaders = len(material_names)
    if  num_of_shaders > 1:
        act_hair.append("%s %s %s" % (space * indent , "shaders", num_of_shaders))
        indent += 1
        for each_shdr in material_names:
            act_hair.append("%s %s %s" % (space * indent , "", each_shdr))
        indent -= 1
    else:
        act_hair.append("%s %s %s" % (space * indent , "shader", material_names[0])) 
    
    act_hair.append("%s %s %s" % (space * indent , "type", "hair"))
    act_hair.append("%s %s %s" % (space * indent , "name", hair_name))
    act_hair.append("%s %s %s" % (space * indent , "segments", steps - 1))
    act_hair.append("%s %s %s" % (space * indent , "width", "%+0.5f" % width))
    
    points = 3 * steps * (num_parents + num_children)
    act_hair.append("%s %s %s" % (space * indent , "points", points))  
        
    tmpfile = efutil.temp_file(hair_name + ".sc")
    outfile = open(tmpfile, 'w')
    for lines in act_hair :
        outfile.write("\n%s" % lines)
    
    indent += 1
    for pindex in range(0, num_parents + num_children):
        # sunflowLog("particle " + str(pindex))
        lines = ''
        for step in range(0, steps):
            co = psys.co_hair(ob, mod, pindex, step)
            # sunflowLog("step " + str(step) + ": " + str(co))
            lines += "%+0.4f  %+0.4f  %+0.4f   " % (co.x , co.y , co.z)
        outfile.write("\n%s" % lines)

    outfile.write("\n}")
    outfile.close()    
    dictionary = {}
    dictionary['path'] = tmpfile
    dictionary['parent'] , dictionary['psys'] = hair_name.split('.hair.')
    dictionary['showemitter'] = psys.settings.use_render_emitter
    return { 'hair' : dictionary }

def getHairParticles(scene):        
    SceneHairs = {}
    for obj in scene.objects:
        objname = obj.name
        if not hasattr(obj, 'modifiers'):
            continue         
        for mod in obj.modifiers :
            if mod.type == 'PARTICLE_SYSTEM':                 
                psys = mod.particle_system                 
                if psys.settings.type not in [ 'HAIR' ] and psys.settings.render_type not in ['PATH']:
                    continue
                hair_name = "%s.hair.%s" % (objname, psys.name)
                hair = getHairs(obj , mod , psys , hair_name)
                mix(SceneHairs , hair , hair_name)
    return SceneHairs
                
