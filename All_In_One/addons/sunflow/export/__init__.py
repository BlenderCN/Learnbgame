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
# Created on                          14-Aug-2013
# Author                              NodeBench
# --------------------------------------------------------------------------

import bpy

from .camera import getSceneCamera
from .shaders import getShadersInScene
from .lamps import getLamps
from .illumination import getIlluminationSettings
from .instances import InstanceExporter
from .psys import ParticleInstancing
from .psys import getHairParticles
from .meshes import write_mesh_file
from .makescfiles import SunflowSCFileSerializer
from .services import dmix
from .services import dict_merge

from ..outputs import sunflowLog


#===============================================================================
# getExporter
#===============================================================================
def getExporter(filepath , scenename='', framenumber=1):
    
    ObjectsRepository = {
                'MotionBlurObjects':{},
                'MeshLightObjects':{},
                'ExportedObjects':{},
                'Instances':{},
                'Instantiated':{},
                         }
    
    scene = bpy.context.scene   
    Export_instances = scene.render.use_instances
    
    # CAMERA EXPORT    
    xportdict = getSceneCamera(scene)
    ObjectsRepository = dict_merge(ObjectsRepository , xportdict)
    del xportdict 
    
    # MATERIAL EXPORT 
    xportdict = getShadersInScene(scene)
    ObjectsRepository = dict_merge(ObjectsRepository , xportdict)
    del xportdict 
        
    # LIGHT EXPORT 
    xportdict = getLamps(scene)
    ObjectsRepository = dict_merge(ObjectsRepository , xportdict)
    del xportdict
    
    # RENDER SETTINGS 
    xportdict = getIlluminationSettings(scene)
    ObjectsRepository = dict_merge(ObjectsRepository , xportdict)
    del xportdict
    
    # HAIR PARTICLES
    xportdict = getHairParticles(scene)
    ObjectsRepository = dict_merge(ObjectsRepository , xportdict)
    del xportdict
    
    # MESH EXPORT 
    ObjectsExporter(scene , ObjectsRepository, Export_instances)
    
    # SERIALIZING DICTIONARY OBJECT TO FILE
    Serializer = SunflowSCFileSerializer(ObjectsRepository, filepath, scenename, framenumber)
    retCode = Serializer.makeSunflowSCFiles()
    
    # FREE MEMORY
    del Serializer
    del ObjectsRepository
    return retCode

#===============================================================================
# ObjectsExporter
#===============================================================================
def ObjectsExporter(scene , ObjectsRepository={}, Export_instances=False): 
    
    # filter objects - avoid camera , lamp
    obj_lst = [ obj.name  for obj in scene.objects if obj.type not in ['CAMERA', 'LAMP'] ]
    
    # filter objects - avoid meshlights ; these are not objects but lights    
    # nonlights = [obj for obj in obj_lst if obj not in ObjectsRepository['MeshLightObjects'].keys() ]
    # obj_lst = nonlights
    
    MotionBlurList = [ key for key in ObjectsRepository['MotionBlurObjects'].keys()]
    if Export_instances:
        proxy_list = {}
        
        for objname in obj_lst:
            turn_on_motion_blur = False
            mblur_steps = 0
            if objname in MotionBlurList :
                mblur_steps = scene.camera.data.sunflow_camera.shutterTime
                turn_on_motion_blur = True        
            cur_object = scene.objects[objname]
            
            dupli_list = None
            
            if (
                (cur_object.is_duplicator) & 
                (cur_object.children != ()) & 
                (cur_object.dupli_type in ['VERTS' , 'FACES' ]) 
                ):
                dupli_list = InstanceExporter(scene , objname , turn_on_motion_blur , mblur_steps)
                dmix(ObjectsRepository, dupli_list, 'Instances')
                proxy_list[objname] = [cur_object.dupli_type]
                sunflowLog ("Instantiated>> %s" % objname)
                if objname in  MotionBlurList:
                    MotionBlurList.pop(MotionBlurList.index(objname))
            if (
                (cur_object.is_duplicator) & 
                (cur_object.children == ()) & 
                (cur_object.dupli_type in ['GROUP' , 'FRAMES']) 
                ):
                dupli_list = InstanceExporter(scene , objname , turn_on_motion_blur , mblur_steps)
                dmix(ObjectsRepository, dupli_list, 'Instances')
                proxy_list[objname] = [cur_object.dupli_type]
                sunflowLog ("Instantiated>> %s" % objname)
                if objname in  MotionBlurList:
                    MotionBlurList.pop(MotionBlurList.index(objname))
            # Particle system only with OBJECT or GROUP which means instancing to sunflow. 
            # Hair will be handled separately
            if (
                (cur_object.is_duplicator) & 
                (len(cur_object.particle_systems) > 0)
                ):
                sunflowLog('trying ParticleInstancing')
                dupli_list = ParticleInstancing(scene , objname , turn_on_motion_blur , mblur_steps)
                dmix(ObjectsRepository, dupli_list, 'Instances')
                proxy_list[objname] = [cur_object.dupli_type]
                sunflowLog ("Instantiated>> %s" % objname)
                if objname in  MotionBlurList:
                    MotionBlurList.pop(MotionBlurList.index(objname))
            
            del dupli_list
            dmix(ObjectsRepository, proxy_list, 'Instantiated')
            
            
        # filter objects - avoid instances ; 
               
        noninst = [obj for obj in obj_lst if obj not in ObjectsRepository['Instantiated'].keys() ]
        xlist = [obj for obj in ObjectsRepository['Instantiated'].keys() if ObjectsRepository['Instantiated'][obj][0] in ['GROUP' , 'FRAMES']]
          
        u = set(noninst)
        v = set(xlist)
        diff = v - u
        noninst.extend([uniq for uniq in diff])
          
        obj_lst = noninst

    ObjectsRepository['ExportedObjects'] = write_mesh_file(obj_lst, scene, not Export_instances , MotionBlurList , scene.camera.data.sunflow_camera.shutterTime)
    
