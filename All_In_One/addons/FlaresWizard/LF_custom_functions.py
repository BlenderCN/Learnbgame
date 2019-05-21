# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy,random
from mathutils import *
from math import sqrt
from mathutils.bvhtree import BVHTree as tree

###############################################################################
####################### Obstacles detection ###################################
###############################################################################

def get_distance(loc1, loc2):    
    """ Get the distance between two locations"""
    l = [loc1, loc2]
    distance = sqrt((l[0][0] - l[1][0])**2 + (l[0][1] - l[1][1])**2 + (l[0][2] - l[1][2])**2)    
    return distance

def RayCast(obj, start, end):
    """ Ray cast wraper """ 
    scn = bpy.context.scene    
    bvh = tree.FromObject(obj, scn)    
    localStart = obj.matrix_world.inverted() * start
    localEnd = obj.matrix_world.inverted() * end
    direction = localEnd- localStart
    ray = bvh.ray_cast(localStart, direction, get_distance(localEnd, localStart))
    return(ray[2])    

# Additional points to send ray to, deppanding on the distance and samples given by the user
def points(dis,samples,i):    
    points = [(dis/samples*i, 0.0, 0.0),(-dis/samples*i, 0.0, 0.0),
              (0.0, dis/samples*i, 0.0),(0.0, -dis/samples*i, 0.0),
              (dis/samples*i, dis/samples*i, 0.0),(-dis/samples*i, -dis/samples*i, 0.0),
              (dis/samples*i, -dis/samples*i, 0.0),(-dis/samples*i, dis/samples*i, 0.0)]              
    return points 

# The main function    
def Hit(target, controller):
    scn = bpy.context.scene
    obj = scn.objects    
    list = obj[controller]['opstacles']
    list2 = []
    list3 = []
    V = 1
    distance = obj[controller]['ops_distance']
    samples = obj[controller]['ops_samples']
    
    if obj[target] != None and scn.camera != None:
        a= scn.camera.location
        b = obj[target].location
        # check if there is a direct hit
        for ob in list:
            if bpy.data.objects.get(ob) != None:
                check = obj[ob]
                index = RayCast(check, a,b )                
                if index != None :
                    V = 0
                    break
                    return V       
                else:
                    list2.append(check)                    
        # if there is no direct hit then look for the closer objects        
        if len(list)==len(list2):
            for ob in list:
                if bpy.data.objects.get(ob) != None:
                    check = obj[ob]
                    for d in [1, 1.3333333, 2, 4]:
                        for p in points(distance,d,1):
                            index = RayCast(check, a,b+Vector(p))
                            if (index != None) and (ob not in list3):
                                list3.append(ob)
        
        # now deppanding on the samples loop throught the closer object(s) and adjust the intensity                     
        if len(list3)>0:
            for ob in list3:
                if bpy.data.objects.get(ob) != None:
                    check = obj[ob]                                   
                    for d in range(1, samples+1):
                        for p in points(distance,samples,d):
                            index = RayCast(check, a,b+Vector(p))
                            if index !=None:
                                V = 1/samples*d
                                return V              
                              
    return V

###############################################################################
############################### Blinking ######################################
###############################################################################

def blink(ob):
    
    scn = bpy.context.scene
    obj = scn.objects
    frame = scn.frame_current
    ob = obj[ob]
    seed = ob['blk_seed']
    min = ob['blk_min']
    randomize = ob['blk_randomize'] 
    delay = ob['blk_delay']
    V = 1
    
    if frame/delay -frame//delay < 0.5:
        V = max((frame/delay -frame//delay)*2, min)
    else:
        V = max((1-(frame/delay -frame//delay))*2, min)             
    random.seed(seed+frame)
    random_factor = random.uniform(1-randomize,1)
    
    return V*random_factor

###############################################################################
############################## Randomize ######################################
###############################################################################

def randomize(min, seed, max = 1):
    random.seed(seed)
    random_factor = random.uniform(min, max)
    return random_factor
        



# Add to drivers functions
bpy.app.driver_namespace["Hit"] = Hit
bpy.app.driver_namespace["blink"] = blink
bpy.app.driver_namespace["randomize"] = randomize



    