#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#  ***** GPL LICENSE BLOCK *****


####------------------------------------------------------------------------------------------------------------------------------------------------------
#### HEADER
####------------------------------------------------------------------------------------------------------------------------------------------------------

bl_info = {
    "name"              : "SHIFT - Mesh Tools",
    "author"            : "BBC",
    "version"           : (1,0),
    "blender"           : (2, 5, 3),
    "api"               : 31236,
    "category"          : "Object",
    "location"          : "Tool Shelf",
    "warning"           : '',
    "wiki_url"          : "",
    "tracker_url"       : "",
    "description"       : "Various mesh operations"}

import os
import bpy
import sys
import time
import math
import shutil
import ctypes
import operator
import mathutils

from math       import *
from ctypes     import *
from bpy.props  import *

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS TRIANGULATE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processTriangulate ():

    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    # shortcut
    selected = bpy.context.selected_objects

    # log
    print ('\nTriangulate starting... \n\n\tObjects (', len (selected), ') :')
    print ('')

    for i, obj in enumerate (selected):

        # is it mesh ?
        if obj and obj.type == 'MESH':

            # set active object
            scene.objects.active = obj

            # saving vertex normals
            if scene.shift_mt_preserve :
                
                normals = [mathutils.Vector ((v.normal [0], v.normal [1], v.normal [2])) for v in obj.data.vertices]
            
            # edit mode
            bpy.ops.object.mode_set (mode = 'EDIT')
        
            # face selection mode
            bpy.context.tool_settings.mesh_select_mode = (False, False, True)
        
            # select all
            bpy.ops.mesh.select_all (action = 'SELECT')
        
            # unhide all faces
            bpy.ops.mesh.reveal ()
        
            # conversion
            bpy.ops.mesh.quads_convert_to_tris ()
        
            # object mode
            bpy.ops.object.mode_set (mode = 'OBJECT')

            if scene.shift_mt_preserve :

                # restoring normals
                for v in obj.data.vertices:    v.normal = normals [v.index]

                # clean up                
                normals [:] = []

            # log
            print (i + 1, "Object : '", obj.name, "'")
            
        else:
            
            # log
            print (i + 1, "Object : '", obj.name, "' is not a mesh")
        
    # log            
    print ('')
    print ('Triangulate finished in %.4f sec.' % (time.clock () - start_time))

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS SPLIT GRID
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processSplitGrid (obj):

    start_time = time.clock ()

    # shortcut
    mesh = obj.data
    
    # shortcut
    scene = bpy.context.scene

    # active object
    scene.objects.active = obj;     obj.select = True

    # is it mesh ?
    if not obj or obj.type != 'MESH':  return

    # log
    print ('\nSplit starting... \n')
    print ('')

    # check mesh
    for f in mesh.faces:
        
        try:    f.vertices [3]
        except: continue

        print ('ERROR | Mesh :', mesh.name, ' containts one or more quads.')
        return -1

    # log
    start_time_ = time.clock ();    print ('Prepare ..')

    # save group name
    gname = "tmp_group"

    # create temporary group
    bpy.ops.group.create (name = gname)

    # our group
    group = bpy.data.groups [gname]

    # saving vertex data
    if scene.shift_mt_preserve :

        layer = mesh.vertex_colors.new (name = gname)

        mesh.vertex_colors.active = layer

        for i, col in enumerate (layer.data) :

            f = mesh.faces [i]

            v = mesh.vertices [f.vertices [0]]
            col.color1 [0] = 0.5 + 0.5 * v.normal [0]
            col.color1 [1] = 0.5 + 0.5 * v.normal [1]
            col.color1 [2] = 0.5 + 0.5 * v.normal [2]
            
            v = mesh.vertices [f.vertices [1]]
            col.color2 [0] = 0.5 + 0.5 * v.normal [0]
            col.color2 [1] = 0.5 + 0.5 * v.normal [1]
            col.color2 [2] = 0.5 + 0.5 * v.normal [2]

            v = mesh.vertices [f.vertices [2]]
            col.color3 [0] = 0.5 + 0.5 * v.normal [0]
            col.color3 [1] = 0.5 + 0.5 * v.normal [1]
            col.color3 [2] = 0.5 + 0.5 * v.normal [2]
                        
    # edit mode
    bpy.ops.object.mode_set (mode = 'EDIT')
        
    # face selection mode
    bpy.context.tool_settings.mesh_select_mode = (False, False, True)

    # unhide all
    bpy.ops.mesh.reveal ()

    # deselect
    bpy.ops.mesh.select_all (action = 'DESELECT')

    # object mode
    bpy.ops.object.mode_set (mode = 'OBJECT')

    # deselect
    bpy.ops.object.select_all (action = 'DESELECT')

    # evaluating bounding box
    minv    = mathutils.Vector (( 999999999.0,  999999999.0,  999999999.0))
    maxv    = mathutils.Vector ((-999999999.0, -999999999.0, -999999999.0))

    for v in obj.data.vertices:

        if v.co [0] < minv [0]: minv [0] = v.co [0]
        if v.co [1] < minv [1]: minv [1] = v.co [1]
        if v.co [2] < minv [2]: minv [2] = v.co [2]
        
        if v.co [0] > maxv [0]: maxv [0] = v.co [0]
        if v.co [1] > maxv [1]: maxv [1] = v.co [1]
        if v.co [2] > maxv [2]: maxv [2] = v.co [2]
    
    if (scene.shift_mt_spatial):

        clusterx = scene.shift_mt_clusterx
        clustery = scene.shift_mt_clustery
        clusterz = scene.shift_mt_clusterz

        dividex  = math.ceil (abs (maxv [0] - minv [0]) / clusterx)
        dividey  = math.ceil (abs (maxv [1] - minv [1]) / clustery)
        dividez  = math.ceil (abs (maxv [2] - minv [2]) / clusterz)
        
    else:
        
        clusterx = abs (maxv [0] - minv [0]) / scene.shift_mt_subdivisionx
        clustery = abs (maxv [1] - minv [1]) / scene.shift_mt_subdivisiony
        clusterz = abs (maxv [2] - minv [2]) / scene.shift_mt_subdivisionz

        dividex  = scene.shift_mt_subdivisionx
        dividey  = scene.shift_mt_subdivisiony
        dividez  = scene.shift_mt_subdivisionz

    print ('\nPossible elements : ', dividex * dividey * dividez, '\n')
    print ('')

    # particles
    if (scene.shift_mt_particles):

        # array of face vertices
        facestype = ctypes.c_float * (len (obj.data.faces) * 9);    faces = facestype ()

        # internal copies of particle systems
        particles  = [None for s in obj.particle_systems]
        particlesi = [None for s in obj.particle_systems]

        # particle data
        data_particles = [None for s in obj.particle_systems]

        # counters
        particlec = [0 for s in obj.particle_systems]

        for i, s in enumerate (obj.particle_systems):

            if (s.settings.type == 'HAIR'):

                # active system
                obj.particle_systems.active_index = i

                bpy.ops.particle.particle_edit_toggle ()
                bpy.ops.particle.particle_edit_toggle ()
                
                # shortcut
                obj_particles = s.particles
                
                # array of particle positions and their indices
                particlestype   = ctypes.c_float * (len (obj_particles) * 3);   particles  [i] = particlestype ()
                particlestype   = ctypes.c_uint  *  len (obj_particles);        particlesi [i] = particlestype ()
        
                # saving particle data
                data_particles [i] = [[] for p in obj_particles]

                # shortcuts
                data_particless = data_particles [i]
                particless      = particles [i]

                c = 0
                for j, p in enumerate (obj_particles):

                    particless [c    ] = ctypes.c_float (p.is_hair [0].co [0])
                    particless [c + 1] = ctypes.c_float (p.is_hair [0].co [1])
                    particless [c + 2] = ctypes.c_float (p.is_hair [0].co [2]);  c += 3
                    
                    data_particless [j] = [ p.alive_state, \
                                            p.location [0], \
                                            p.location [1], \
                                            p.location [2], \
                                            p.rotation [0], \
                                            p.rotation [1], \
                                            p.rotation [2], \
                                            p.rotation [3], p.size, \
                                            p.velocity [0], \
                                            p.velocity [1], \
                                            p.velocity [2], \
                                            p.angular_velocity [0], \
                                            p.angular_velocity [1], \
                                            p.angular_velocity [2], \
                                            p.prev_location [0], \
                                            p.prev_location [1], \
                                            p.prev_location [2], \
                                            p.prev_rotation [0], \
                                            p.prev_rotation [1], \
                                            p.prev_rotation [2], \
                                            p.prev_rotation [3], \
                                            p.prev_velocity [0], \
                                            p.prev_velocity [1], \
                                            p.prev_velocity [2], \
                                            p.prev_angular_velocity [0], \
                                            p.prev_angular_velocity [1], \
                                            p.prev_angular_velocity [2], \
                                            p.lifetime,   p.birth_time,   p.die_time, \
                                            len (p.is_hair),  [], \
                                            len (p.keys),     []]
                    
                    data = data_particless [j][32]
                    for pp in p.is_hair:
                        data.append (pp.co [0])
                        data.append (pp.co [1])
                        data.append (pp.co [2])
                        data.append (pp.co_hair_space [0])
                        data.append (pp.co_hair_space [1])
                        data.append (pp.co_hair_space [2])
                        data.append (pp.time)
                        data.append (pp.weight)
                
                    data = data_particless [j][34]
                    for k in p.keys:
                        data.append (angular_velocity [0])
                        data.append (angular_velocity [1])
                        data.append (angular_velocity [2])
                        data.append (location [0])
                        data.append (location [1])
                        data.append (location [2])
                        data.append (rotation [0])
                        data.append (rotation [1])
                        data.append (rotation [2])
                        data.append (rotation [3])
                        data.append (velocity [0])
                        data.append (velocity [1])
                        data.append (velocity [2])
                        data.append (time)
        
                # free memory
                s.settings.count = 0

                bpy.ops.particle.edited_clear ()
                
                bpy.ops.particle.particle_edit_toggle ()
                bpy.ops.particle.particle_edit_toggle ()

                # save count
                particlec [i] = c
        
    # log
    print ('Prepare done in %.4f sec' % (time.clock () - start_time_))

    print ('')        
    print ('Splitting ..')

    # shortcut
    minfaces = scene.shift_mt_minfaces
    
    if (dividex > 1):
        
        for obj in group.objects:

            # active object
            scene.objects.active = obj; obj.select = True
                    
            # deselect faces
            for f in obj.data.faces: f.select = False
            
            position = minv [0]
            for x in range (dividex - 1):

                # end positiom
                end = position + clusterx

                count = 0
                
                # taking whole faces
                for f in obj.data.faces:
                    if f.center [0] >= position and f.center [0] <= end :   f.select = True;    count += 1

                if ((len (obj.data.faces) - count) < minfaces):   break

                if (count >= minfaces):

                    # edit mode
                    bpy.ops.object.mode_set (mode = 'EDIT')

                    # separate
                    bpy.ops.mesh.separate ()
                    
                    # object mode
                    bpy.ops.object.mode_set (mode = 'OBJECT')

                    # log
                    print ("Split ", len (group.objects))
                                                                    
                # advance
                position += clusterx
                
            # unselect
            obj.select = False

    if (dividey > 1):
        
        for obj in group.objects:

            # active object
            scene.objects.active = obj; obj.select = True
        
            # deselect faces
            for f in obj.data.faces: f.select = False
            
            position = minv [1]
            for y in range (dividey - 1):

                # end positiom
                end = position + clustery
                
                count = 0
            
                # taking whole faces
                for f in obj.data.faces:
                    if f.center [1] >= position and f.center [1] <= end :   f.select = True;    count += 1
                
                if ((len (obj.data.faces) - count) < minfaces):   break
                
                if (count >= minfaces):
                
                    # edit mode
                    bpy.ops.object.mode_set (mode = 'EDIT')
                    
                    # separate
                    bpy.ops.mesh.separate ()
                    
                    # object mode
                    bpy.ops.object.mode_set (mode = 'OBJECT')
                    
                    # log
                    print ("Split ", len (group.objects))
                                    
                # advance
                position += clustery
                
            # unselect
            obj.select = False

    if (dividez > 1):

        for obj in group.objects:

            # active object
            scene.objects.active = obj; obj.select = True
        
            # deselect faces
            for f in obj.data.faces: f.select = False
            
            position = minv [2]
            for z in range (dividez - 1):

                # end positiom
                end = position + clusterz
                
                count = 0

                # taking whole faces
                for f in obj.data.faces:
                    if f.center [2] >= position and f.center [2] <= end :   f.select = True;    count += 1

                if ((len (obj.data.faces) - count) < minfaces):   break
                
                if (count >= minfaces):
                
                    # edit mode
                    bpy.ops.object.mode_set (mode = 'EDIT')

                    # separate
                    bpy.ops.mesh.separate ()

                    # object mode
                    bpy.ops.object.mode_set (mode = 'OBJECT')
                                    
                    # log
                    print ("Split ", len (group.objects))
                
                # advance
                position += clusterz
                
            # unselect
            obj.select = False

    # object mode
    bpy.ops.object.mode_set (mode = 'OBJECT')
    
    # deselect
    bpy.ops.object.select_all (action = 'DESELECT')

    # particles
    if (scene.shift_mt_particles):
        
        print ('')        
        print ('Splitting particles ..')

    # delete degenerated objects
    for obji, obj in enumerate (group.objects):

        if len (obj.data.faces) == 0 or len (obj.data.vertices) == 0:

            scene.objects.unlink (obj)

    # select new objects
    for obji, obj in enumerate (group.objects):

        # set active object
        scene.objects.active = obj;     obj.select = True

        # particles
        if (scene.shift_mt_particles):

            facec = 0

            # toolkit dll
            toolkit = windll.LoadLibrary (sys.path [0] + '\shift_toolkit.dll')

            for f in obj.data.faces:
                
                v1 = obj.data.vertices [f.vertices [0]]
                v2 = obj.data.vertices [f.vertices [1]]
                v3 = obj.data.vertices [f.vertices [2]]

                faces [facec    ] = v1.co [0]
                faces [facec + 1] = v1.co [1]
                faces [facec + 2] = v1.co [2]
                
                faces [facec + 3] = v2.co [0]
                faces [facec + 4] = v2.co [1]
                faces [facec + 5] = v2.co [2]
                
                faces [facec + 6] = v3.co [0]
                faces [facec + 7] = v3.co [1]
                faces [facec + 8] = v3.co [2]

                facec += 9

            for si, s in enumerate (obj.particle_systems):

                if (s.settings.type == 'HAIR'):

                    # active system
                    obj.particle_systems.active_index = si

                    # cut particles
                    count = toolkit.processParticlesCut (particlesi [si], particles [si], faces, particlec [si], facec)

                    # create new settings
                    s.settings = \
                    s.settings.copy ()
                    s.settings.count = count

                    # refresh
                    bpy.ops.object.mode_set (mode = 'EDIT')
                    bpy.ops.object.mode_set (mode = 'OBJECT')

                    # shortcut
                    obj_particles = s.particles

                    # shortcut
                    data = data_particles [si]

                    for i, p in enumerate (obj_particles):

                        index = particlesi [si][i]

                        p.alive_state               = data [index][ 0]
                        p.location [0]              = data [index][ 1]
                        p.location [1]              = data [index][ 2]
                        p.location [2]              = data [index][ 3]
                        p.rotation [0]              = data [index][ 4]
                        p.rotation [1]              = data [index][ 5]
                        p.rotation [2]              = data [index][ 6]
                        p.rotation [3]              = data [index][ 7]
                        p.size                      = data [index][ 8]
                        p.velocity [0]              = data [index][ 9]
                        p.velocity [1]              = data [index][10]
                        p.velocity [2]              = data [index][11]
                        p.angular_velocity [0]      = data [index][12]
                        p.angular_velocity [1]      = data [index][13]
                        p.angular_velocity [2]      = data [index][14]
                        p.prev_location [0]         = data [index][15]
                        p.prev_location [1]         = data [index][16]
                        p.prev_location [2]         = data [index][17]
                        p.prev_rotation [0]         = data [index][18]
                        p.prev_rotation [1]         = data [index][19]
                        p.prev_rotation [2]         = data [index][20]
                        p.prev_rotation [3]         = data [index][21]
                        p.prev_velocity [0]         = data [index][22]
                        p.prev_velocity [1]         = data [index][23]
                        p.prev_velocity [2]         = data [index][24]
                        p.prev_angular_velocity [0] = data [index][25]
                        p.prev_angular_velocity [1] = data [index][26]
                        p.prev_angular_velocity [2] = data [index][27]
                        p.lifetime                  = data [index][28]
                        p.birth_time                = data [index][29]
                        p.die_time                  = data [index][30]

                        c = min (data [index][31], len (p.is_hair))

                        keys = data [index][32];  k = 0

                        for j in range (c):

                            h = p.is_hair [j]
                        
                            h.co [0]            = keys [k    ]
                            h.co [1]            = keys [k + 1]
                            h.co [2]            = keys [k + 2]

                            # WRITING ON THESE CAUSE INVALID DATA
##                            h.co_hair_space [0] = keys [k + 3]
##                            h.co_hair_space [1] = keys [k + 4]
##                            h.co_hair_space [2] = keys [k + 5]
                            
                            h.time              = keys [k + 6]
                            h.weight            = keys [k + 7]
                            
                            k += 8

                        c = min (data [index][33], len (p.keys))

                        keys = data [index][34];  k = 0
                        for j in range (c):

                            key = p.keys [j]

                            key.angular_velocity [0]    = keys [k     ]
                            key.angular_velocity [1]    = keys [k +  1]
                            key.angular_velocity [2]    = keys [k +  2]
                            key.location [0]            = keys [k +  3]
                            key.location [1]            = keys [k +  4]
                            key.location [2]            = keys [k +  5]
                            key.rotation [0]            = keys [k +  6]
                            key.rotation [1]            = keys [k +  7]
                            key.rotation [2]            = keys [k +  8]
                            key.rotation [3]            = keys [k +  9]
                            key.velocity [0]            = keys [k + 10]
                            key.velocity [1]            = keys [k + 11]
                            key.velocity [2]            = keys [k + 12]
                            key.time                    = keys [k + 13]

                            k += 14

            # log
            print ("Split ", obji + 1)

    # particles clean up
    if (scene.shift_mt_particles):

        data_particles [:] = []
        
        particles  [:] = []
        particlesi [:] = []

        particlec [:] = []

        del faces
        
    # restoring normals
    if scene.shift_mt_preserve :
        
        for obj in group.objects:

            scene.objects.active = obj

            mesh = obj.data
            data = obj.data.vertex_colors.active.data

            tags = [True for v in mesh.vertices]

            for i, col in enumerate (data) :

                f = mesh.faces [i]

                i1 = f.vertices [0]
                i2 = f.vertices [1]
                i3 = f.vertices [2]
                
                if tags [i1] :
                    v = mesh.vertices [i1]
                    v.normal [0] = 2.0 * col.color1 [0] - 1.0
                    v.normal [1] = 2.0 * col.color1 [1] - 1.0
                    v.normal [2] = 2.0 * col.color1 [2] - 1.0
                    tags [i1] = False
                
                if tags [i2] :
                    v = mesh.vertices [i2]
                    v.normal [0] = 2.0 * col.color2 [0] - 1.0
                    v.normal [1] = 2.0 * col.color2 [1] - 1.0
                    v.normal [2] = 2.0 * col.color2 [2] - 1.0
                    tags [i2] = False
                
                if tags [i3] :
                    v = mesh.vertices [i3]
                    v.normal [0] = 2.0 * col.color3 [0] - 1.0
                    v.normal [1] = 2.0 * col.color3 [1] - 1.0
                    v.normal [2] = 2.0 * col.color3 [2] - 1.0
                    tags [i3] = False
                    
            # remove color layer
            try:

                # active color layer
                obj.data.vertex_colors.active = obj.data.vertex_colors [gname]
                
                # edit mode
                bpy.ops.object.mode_set (mode = 'EDIT')

                # remove uv layer
                bpy.ops.mesh.vertex_color_remove ()
                    
                # object mode
                bpy.ops.object.mode_set (mode = 'OBJECT')
                
            except: pass
                
            # clean up
            tags [:] = []

    # remove group
    bpy.data.groups.remove (group)

    # particles
    if (scene.shift_mt_particles):
        
        # unload dll
        del toolkit    
            
    # log            
    print ('')
    print ('Splitting finished in %.4f sec.' % (time.clock () - start_time))
        
    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS SPLIT/UNVEIL TEXTURE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processSplitTex (mode):

    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    # shortcut
    obj = bpy.context.object

    # set active object
    scene.objects.active = obj

    # shortcut
    mesh = obj.data

    # is it mesh ?
    if not obj or obj.type != 'MESH':

        print ("ERROR | Selected object is not mesh")
        return -1        

    # does it have UV coords ?
    if not mesh.uv_textures.active:

        print ("ERROR | Selected object do not have UV texture layer")
        return -1        
    
    if mode == 'SPLIT':
        
        # log
        print ('\nSplit starting... ')
        print ('')
        
    elif mode == 'UNVEIL':

        # log
        print ('\nUnveil starting... ')
        print ('')
        
    elif mode == 'POLISH':

        # log
        print ('\nPolish starting... ')
        print ('')
        
    names = (scene.shift_mt_tex0,
             scene.shift_mt_tex1,
             scene.shift_mt_tex2,
             scene.shift_mt_tex3,
             scene.shift_mt_tex4,
             scene.shift_mt_tex5,
             scene.shift_mt_tex6,
             scene.shift_mt_tex7,
             scene.shift_mt_tex8,
             scene.shift_mt_tex9,
             scene.shift_mt_texA,
             scene.shift_mt_texB,
             scene.shift_mt_texC,
             scene.shift_mt_texD,
             scene.shift_mt_texE,
             scene.shift_mt_texF)
    
    textures = []

    for n in names :
        
        if (n != '') :
            try: tex = bpy.data.textures [n]
            except:
                print ("ERROR | Cannot find texture : '" + n + "'")
                return -1

            try :   tex.image.filepath
            except :
                print ("ERROR | Texture : '" + n + "' is not image")
                return -1

            if not (tex.image.filepath == ''):  textures.append ([tex])
            else:
                print ("ERROR | Texture : '" + n + "' is not external image")
                return -1

    if len (textures) == 0 : return

    if mode == 'SPLIT':

        # group name
        gname = "tmp_" + obj.name

        # create temporary group
        bpy.ops.group.create (name = gname)

    convert = False

    # check mesh
    for f in mesh.faces:
        
        try:    f.vertices [3]
        except: continue

        convert = True

    # convert into triangles
    if (convert):
        
        # edit mode
        bpy.ops.object.mode_set (mode = 'EDIT')
    
        # face selection mode
        bpy.context.tool_settings.mesh_select_mode = (False, False, True)
    
        # select all
        bpy.ops.mesh.select_all (action = 'SELECT')
    
        # unhide all faces
        bpy.ops.mesh.reveal ()
    
        # conversion
        bpy.ops.mesh.quads_convert_to_tris ()
    
        # object mode
        bpy.ops.object.mode_set (mode = 'OBJECT')

####    # save area
####    otype = bpy.context.area.type
####
####    # image context
####    bpy.context.area.type = 'IMAGE_EDITOR'
####
####    # array of names
####    narraytype = ctypes.c_char_p * len (textures);  narray = narraytype ()
####    
####    for i, t in enumerate (textures):
####
####        filep = bpy.path.abspath ('//') + 'tmp_' + str (i) + '.tga'
####
####        narray [i] = ctypes.c_char_p (filep.encode ('ascii'));  t.append (filep)
####
####        bpy.context.area.active_space.image = t [0].image
####
####        bpy.ops.image.save_as (file_type = 'TARGA RAW', filepath = filep, relative_path = False, copy = True)
####
####    # restore area
####    bpy.context.area.type = otype


    # array of names
    narraytype = ctypes.c_char_p * len (textures);  narray = narraytype ()
    
    for i, t in enumerate (textures):

        filep = bpy.path.abspath (t [0].image.filepath)

        narray [i] = ctypes.c_char_p (filep.encode ('ascii'));  t.append (filep)

        # ADD HERE OPTION TO SAVE EDITED EXTERNAL FILES
    
    # toolkit dll
    toolkit = windll.LoadLibrary (sys.path [0] + '\shift_toolkit.dll')
    
    # file
    filep = bpy.path.abspath ('//') + 'tmp_err.tga';    fileb = filep.encode ('ascii')

    # BEGIN
    r = toolkit.processTexSplitBegin (narray, ctypes.c_char_p (fileb), len (textures),
                                      ctypes.c_uint  (scene.shift_mt_overlap),
                                      ctypes.c_uint  (scene.shift_mt_kernel_antialias),
                                      ctypes.c_uint  (scene.shift_mt_kernel_scan),
                                      ctypes.c_float (scene.shift_mt_tolerancyt / 100.0),
                                      ctypes.c_float (scene.shift_mt_tolerancyf / 100.0))

    # result ..
    if (r < 0.0):
        
        # END
        toolkit.processTexSplitEnd (0, 0)

        # cleanup
        del toolkit

        if   (r == -1): print ("ERROR | Cannot open external image files (Only uncompressed RGB targa are supported). \n")
        elif (r == -2): print ("ERROR | Images have inconsistent dimensions. \n")
        elif (r == -3): print ("ERROR | Only uncompressed RGB targa are supported. \n")
        else:           print ("ERROR | There are some problems acessing image files. \n")
                
        return -1

    if mode == 'SPLIT':

        # active UV texture layer
        layer = mesh.uv_textures.active

        # face selection mode
        bpy.context.tool_settings.mesh_select_mode = (False, False, True)
        
        # object mode
        bpy.ops.object.mode_set (mode = 'OBJECT')
                
        # masks are saved into texture coords
        mlayer = mesh.uv_textures.new ('tmp_masks')

        # set active UVs
        mesh.uv_textures.active = mlayer

        # list of masks
        lmasks = []

        # errors
        err  = False

        for i, f in enumerate (mesh.faces) :    f.select = False


        # ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
        for i, f in enumerate (mesh.faces):

            uv1 = layer.data [i].uv1
            uv2 = layer.data [i].uv2
            uv3 = layer.data [i].uv3
            
            r = toolkit.processTexMaskTriangle (ctypes.c_float (uv1 [0]),
                                                ctypes.c_float (uv1 [1]),
                                                ctypes.c_float (uv2 [0]),
                                                ctypes.c_float (uv2 [1]),
                                                ctypes.c_float (uv3 [0]),
                                                ctypes.c_float (uv3 [1]))
    
        # PROCESS
        for i, f in enumerate (mesh.faces) :

            uv1 = layer.data [i].uv1
            uv2 = layer.data [i].uv2
            uv3 = layer.data [i].uv3
            
            r = toolkit.processTexSplitTriangle (ctypes.c_float (uv1 [0]),
                                                 ctypes.c_float (uv1 [1]),
                                                 ctypes.c_float (uv2 [0]),
                                                 ctypes.c_float (uv2 [1]),
                                                 ctypes.c_float (uv3 [0]),
                                                 ctypes.c_float (uv3 [1]))

            if   (r == 0):  f.select = True;    err = True; continue
            else:           f.select = False

            mlayer.data [i].uv1 [0] = r
            mlayer.data [i].uv2 [0] = r
            mlayer.data [i].uv3 [0] = r

            found = False
            for mask in lmasks:
                if mask == r:
                    found = True;
                    break
                
            if not found: lmasks.append (r)
            
        if (err):

            # END
            toolkit.processTexSplitEnd (0, 1)

            # reload images
            for t in textures:  t [0].image.reload ()
            
            # update views
            for scr in bpy.data.screens:
                for area in scr.areas:
                    area.tag_redraw ()

            # cleanup
            del toolkit
                        
            # active layer
            obj.data.uv_textures.active = mlayer

            # remove
            try: bpy.ops.mesh.uv_texture_remove ()
            except: pass

            # exclude from group
            bpy.ops.object.group_remove ()

            # remove group
            bpy.data.groups.remove (bpy.data.groups [gname])
                        
            print ("ERROR | There are some faces that use more then maximum overlapping layers (" + str (scene.shift_mt_overlap) + ") \n")
            print ("   Problematic faces are selected.")
            
            return -1

        # our group
        group = bpy.data.groups [gname]

        # separate parts
        for i, m in enumerate (lmasks):

            data = obj.data.uv_textures ['tmp_masks'].data
            
            for j, f in enumerate (mesh.faces):
                if (data [j].uv1 [0] == m):  f.select = True

            # edit mode
            bpy.ops.object.mode_set (mode = 'EDIT')

            # separate
            bpy.ops.mesh.separate ()

            # object mode
            bpy.ops.object.mode_set (mode = 'OBJECT')

            # add mask to new mesh
            group.objects [0].data ['texmask'] = m


        # remove empty object from group
        bpy.ops.group.objects_remove_active ()
    
        # clean up
        scene.objects.unlink (obj)        

        # deselect
        bpy.ops.object.select_all (action = 'DESELECT')

        # select new objects
        for obj in group.objects:

            scene.objects.active = obj; obj.select = True

            # mask
            m = obj.data ['texmask']

            # delete temporary bit-mask
            del obj.data ['texmask']

            j = 0
            for i in range (32):
                
                if (m & (1 << i)):
                    if   (j == 0):  obj.data ['splittexA'] = i;  j += 1
                    elif (j == 1):  obj.data ['splittexB'] = i;  j += 1
                    elif (j == 2):  obj.data ['splittexC'] = i;  j += 1
                    elif (j == 3):  obj.data ['splittexD'] = i;  j += 1
                    else: break
            
            # active layer
            obj.data.uv_textures.active = obj.data.uv_textures ['tmp_masks']

            # remove
            try: bpy.ops.mesh.uv_texture_remove ()        
            except: pass
            
        # remove group
        bpy.data.groups.remove (group)

        # END
        toolkit.processTexSplitEnd (0, 0)
        

    elif mode == 'UNVEIL':
        
        # active UV texture layer
        layer = mesh.uv_textures.active

        toolkit.processTexUnveilUpdate ()

        if (scene.shift_mt_selectedfaces):
                        
            for i, f in enumerate (mesh.faces):

                if (f.select):

                    uv1 = layer.data [i].uv1
                    uv2 = layer.data [i].uv2
                    uv3 = layer.data [i].uv3
                    
                    r = toolkit.processTexUnveilFaceTriangle (ctypes.c_float (uv1 [0]),
                                                              ctypes.c_float (uv1 [1]),
                                                              ctypes.c_float (uv2 [0]),
                                                              ctypes.c_float (uv2 [1]),
                                                              ctypes.c_float (uv3 [0]),
                                                              ctypes.c_float (uv3 [1]), ctypes.c_int (0))
        else:
                                
            for i, f in enumerate (mesh.faces):

                uv1 = layer.data [i].uv1
                uv2 = layer.data [i].uv2
                uv3 = layer.data [i].uv3
                
                r = toolkit.processTexUnveilFaceTriangle (ctypes.c_float (uv1 [0]),
                                                          ctypes.c_float (uv1 [1]),
                                                          ctypes.c_float (uv2 [0]),
                                                          ctypes.c_float (uv2 [1]),
                                                          ctypes.c_float (uv3 [0]),
                                                          ctypes.c_float (uv3 [1]), ctypes.c_int (0))
                
        # END
        toolkit.processTexSplitEnd (1, 0)

        # reload images
        for t in textures:  t [0].image.reload ()

        # update views
        for scr in bpy.data.screens:
            for area in scr.areas:
                area.tag_redraw ()

    elif mode == 'POLISH':

        # active UV texture layer
        layer = mesh.uv_textures.active

        toolkit.processTexUnveilUpdate ()

        for i, f in enumerate (mesh.faces):

            uv1 = layer.data [i].uv1
            uv2 = layer.data [i].uv2
            uv3 = layer.data [i].uv3
            
            r = toolkit.processTexUnveilFaceTriangle (ctypes.c_float (uv1 [0]),
                                                      ctypes.c_float (uv1 [1]),
                                                      ctypes.c_float (uv2 [0]),
                                                      ctypes.c_float (uv2 [1]),
                                                      ctypes.c_float (uv3 [0]),
                                                      ctypes.c_float (uv3 [1]), ctypes.c_int (0))

##        for i, f in enumerate (mesh.faces):
##
##            uv1 = layer.data [i].uv1
##            uv2 = layer.data [i].uv2
##            uv3 = layer.data [i].uv3
##            
##            r = toolkit.processTexMaskTriangle (ctypes.c_float (uv1 [0]),
##                                                ctypes.c_float (uv1 [1]),
##                                                ctypes.c_float (uv2 [0]),
##                                                ctypes.c_float (uv2 [1]),
##                                                ctypes.c_float (uv3 [0]),
##                                                ctypes.c_float (uv3 [1]))

        if (scene.shift_mt_selectedfaces):
                        
            for i, f in enumerate (mesh.faces):

                if (f.select):

                    uv1 = layer.data [i].uv1
                    uv2 = layer.data [i].uv2
                    uv3 = layer.data [i].uv3
                    
                    r = toolkit.processTexPolishFaceTriangle (ctypes.c_float (uv1 [0]),
                                                              ctypes.c_float (uv1 [1]),
                                                              ctypes.c_float (uv2 [0]),
                                                              ctypes.c_float (uv2 [1]),
                                                              ctypes.c_float (uv3 [0]),
                                                              ctypes.c_float (uv3 [1]), ctypes.c_int (50))
                    
        else:
                    
            for i, f in enumerate (mesh.faces):

                uv1 = layer.data [i].uv1
                uv2 = layer.data [i].uv2
                uv3 = layer.data [i].uv3
                
                r = toolkit.processTexPolishFaceTriangle (ctypes.c_float (uv1 [0]),
                                                          ctypes.c_float (uv1 [1]),
                                                          ctypes.c_float (uv2 [0]),
                                                          ctypes.c_float (uv2 [1]),
                                                          ctypes.c_float (uv3 [0]),
                                                          ctypes.c_float (uv3 [1]), ctypes.c_int (50))

##        for i, f in enumerate (mesh.faces):
##
##            uv1 = layer.data [i].uv1
##            uv2 = layer.data [i].uv2
##            uv3 = layer.data [i].uv3
##            
##            r = toolkit.processTexMaskTriangle (ctypes.c_float (uv1 [0]),
##                                                ctypes.c_float (uv1 [1]),
##                                                ctypes.c_float (uv2 [0]),
##                                                ctypes.c_float (uv2 [1]),
##                                                ctypes.c_float (uv3 [0]),
##                                                ctypes.c_float (uv3 [1]))


        # END
        toolkit.processTexSplitEnd (1, 0)

        # reload images
        for t in textures:  t [0].image.reload ()

        # update views
        for scr in bpy.data.screens:
            for area in scr.areas:
                area.tag_redraw ()
        
    # unload dll
    del toolkit

    if   mode == 'SPLIT':
        
        # log            
        print ('')
        print ('Split finished in %.4f sec.' % (time.clock () - start_time))
        
    elif mode == 'UNVEIL':
            
        # log            
        print ('')
        print ('Unveil finished in %.4f sec.' % (time.clock () - start_time))
        
    elif mode == 'POLISH':
            
        # log            
        print ('')
        print ('Polish finished in %.4f sec.' % (time.clock () - start_time))
        
    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS SPLIT TEXTURE MERGE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processSplitTexMerge ():

    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    # shortcut
    selected = bpy.context.selected_objects

    # deselect invalid objects
    for obj in selected:        

        # is it mesh ?
        if not (obj and obj.type == 'MESH'):

            obj.select = False

    # shortcut
    selected = bpy.context.selected_objects
    
    # check
    if (len (selected) < 2):  return -1
    
    # create temporary group from selected objects
    bpy.ops.group.create (name = "tmp_group");      group = bpy.data.groups ["tmp_group"]
    
    # log
    print ('\nMergeing starting... \n\n\tObjects (', len (selected), ') :')
    print ('')
    
    while (len (group.objects) > 1):
        
        # list of textures
        textures = []

        # init
        reduced = False

        # list of objects sorted by poly-count
        sselected = sorted ([[obj, len (obj.data.faces)] for obj in group.objects], key=lambda objt: objt [1], reverse = False)

        # set active object
        scene.objects.active = sselected [0][0]

        # object mode
        bpy.ops.object.mode_set (mode = 'OBJECT')

        # deselect all
        bpy.ops.object.select_all (action = 'DESELECT')

        for i, (obj, l) in enumerate (sselected):

            # make copy
            backup = list (textures)
                        
            try:
                textures.append (obj.data ['splittexA'])
                try:
                    textures.append (obj.data ['splittexB'])
                    try:
                        textures.append (obj.data ['splittexC'])
                        try:
                            textures.append (obj.data ['splittexD'])
                        except: pass
                    except: pass
                except: pass
            except: pass

            # sort textures and remove doubles

            textures.sort ()

            ltextures = len (textures);   tprev = None
            
            n = 0
            while (n < ltextures):
                t = textures [n]
                if (t == tprev):
                    del textures [n];  ltextures -= 1
                    continue
                tprev = t;  n += 1

            ltextures = len (textures)

            if (ltextures <= scene.shift_mt_overlap):

                # select
                obj.select = True

                # join 2 meshes
                if len (bpy.context.selected_objects) == 2:

                    # join meshes
                    bpy.ops.object.join (); reduced = True

                    # we set new object for print out
                    obj = bpy.context.object
                    
                # log
                print (i + 1, "Object : '", obj.name, "'")
                
            else:

                # restore texture list
                textures [:] = [];  textures = list (backup)
                
                # log
                print (i + 1, "Object : '", obj.name, "' off ")

            # clean up
            backup [:] = []

        # set new props
        try:    bpy.context.object.data ['splittexA'] = textures [0]
        except: pass;
        try:    bpy.context.object.data ['splittexB'] = textures [1]
        except: pass;
        try:    bpy.context.object.data ['splittexC'] = textures [2]
        except: pass;
        try:    bpy.context.object.data ['splittexD'] = textures [3]
        except: pass;

        # remove doubles
        if scene.shift_mt_mdouble :

            #### THIS WILL FUCK UP NORMALS !!!!!!                

            # edit mode
            bpy.ops.object.mode_set (mode = 'EDIT')

            # vertex selection mode
            bpy.context.tool_settings.mesh_select_mode = (True, False, False)

            # select all vertices
            bpy.ops.mesh.select_all (action = 'SELECT')

            # merge dobules
            bpy.ops.mesh.remove_doubles ()
            
            # object mode
            bpy.ops.object.mode_set (mode = 'OBJECT')

        # clean up
        sselected [:] = []
        textures  [:] = []
    
        # nothing changed ?
        if (not reduced):

            bpy.ops.group.objects_remove_active ()
    
    # remove group
    bpy.data.groups.remove (group)
                
    # log            
    print ('')
    print ('Merge finished in %.4f sec.' % (time.clock () - start_time))
    
    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS SPLIT TEXTURE GENERATE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processSplitTexGenerate ():

    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    # shortcut
    selected = bpy.context.selected_objects

    # check path
    if (scene.shift_mt_generate_path == ''):
        
        print ("ERROR | Invalid file path")
        return -1

    # log
    print ('\nGenerate starting... \n\n\tObjects (', len (selected), ') :')
    print ('')

    names = (scene.shift_mt_tex0,
             scene.shift_mt_tex1,
             scene.shift_mt_tex2,
             scene.shift_mt_tex3,
             scene.shift_mt_tex4,
             scene.shift_mt_tex5,
             scene.shift_mt_tex6,
             scene.shift_mt_tex7,
             scene.shift_mt_tex8,
             scene.shift_mt_tex9,
             scene.shift_mt_texA,
             scene.shift_mt_texB,
             scene.shift_mt_texC,
             scene.shift_mt_texD,
             scene.shift_mt_texE,
             scene.shift_mt_texF)

    # CHECK INPUT
    
    textures = []

    for n in names :
        
        if (n != '') :
            try: tex = bpy.data.textures [n]
            except:
                print ("ERROR | Cannot find texture : '" + n + "'")
                return -1

            try :   tex.image.filepath
            except :
                print ("ERROR | Texture : '" + n + "' is not an image")
                return -1
            
            if (tex.image.filepath == ''):
                print ("ERROR | Texture : '" + n + "' is not external image")
                return -1
            
            textures.append ([tex])

    if len (textures) == 0 : return

    # array of names
    narraytype = ctypes.c_char_p * len (textures);  narray = narraytype ()
    
    for i, t in enumerate (textures):

        filep = bpy.path.abspath (t [0].image.filepath);    print (filep)

        narray [i] = ctypes.c_char_p (filep.encode ('ascii'));  t.append (filep)

        # ADD HERE OPTION TO SAVE EDITED EXTERNAL FILES

    print ("")


####    # SAVE TEMPORARY IMAGES
####
####    # save area
####    otype = bpy.context.area.type
####
####    # image context
####    bpy.context.area.type = 'IMAGE_EDITOR'
####    
####    narraytype = ctypes.c_char_p * len (textures);  narray = narraytype ()
####    
####    for i, t in enumerate (textures):
####
####        filep = scene.shift_mt_generate_path + 'tmp_' + str (i) + '.tga'
####
####        narray [i] = ctypes.c_char_p (filep.encode ('ascii'));  t.append (filep)
####
####        bpy.context.area.active_space.image = t [0].image
####
####        bpy.ops.image.save_as (file_type = 'TARGA RAW', filepath = filep, relative_path = False, copy = True)
####
####    # restore area
####    bpy.context.area.type = otype

    # PROCESS OBJECTS

    # toolkit dll
    toolkit = windll.LoadLibrary (sys.path [0] + '\shift_toolkit.dll')

    texset = []
    
    for obj in selected:

        # is it mesh ?
        if obj and obj.type == 'MESH':

            texA = -1
            texB = -1
            texC = -1
            texD = -1

            count = 0

            try: texA = obj.data ['splittexA']; count += 1
            except: pass
            try: texB = obj.data ['splittexB']; count += 1
            except: pass
            try: texC = obj.data ['splittexC']; count += 1
            except: pass
            try: texD = obj.data ['splittexD']; count += 1
            except: pass

            texset.append ((count, texA, texB, texC, texD))

    # sort and remove duplicates
    texset.sort ()
    
    tprev = None;    l = len (texset)
    
    i = 0
    while (i < l):
        t = texset [i]
        if (t == tprev):
            del texset [i];   l -= 1
            continue
        tprev = t;            i += 1

    # array of indices
    iarraytype = ctypes.c_ubyte * 4;  iarray = iarraytype ()

    for t in texset:

        count = t [0]

        if (count == 2):
            iarray [0] = t [1]
            iarray [1] = t [2]

            # file
            tname = 'mask-' + str (t [1]) + '-' + str (t [2])
            fileout = scene.shift_mt_generate_path + tname + '.tga'
            fileout = fileout.encode ('ascii')
            
        elif (count == 3):
            iarray [0] = t [1]
            iarray [1] = t [2]
            iarray [2] = t [3]

            # file
            tname = 'mask-' + str (t [1]) + '-' + str (t [2]) + '-' + str (t [3])
            fileout = scene.shift_mt_generate_path + tname + '.tga'
            fileout = fileout.encode ('ascii')
            
        elif (count == 4):
            iarray [0] = t [1]
            iarray [1] = t [2]
            iarray [2] = t [3]
            iarray [3] = t [4]

            # file
            tname = 'mask-' + str (t [1]) + '-' + str (t [2]) + '-' + str (t [3]) + '-' + str (t [4])
            fileout = scene.shift_mt_generate_path + tname + '.tga'
            fileout = fileout.encode ('ascii')
            
        else : continue

        # GENERATE
        r = toolkit.processTexSplitGenerate (narray, ctypes.c_char_p (fileout), iarray, count)

        if (r < 0):
            print ('ERROR | Cannot open/access images')

        # load new image
        img = bpy.data.images.load (fileout)

        # create new texture
        tex = bpy.data.textures.new (name = tname, type = 'IMAGE'); tex.image = img
            
    # unload dll    
    del toolkit

    # generate materials
    if scene.shift_mt_generate_mat:

        for obj in selected:
            
            # is it mesh ?
            if obj and obj.type == 'MESH' and obj.active_material:

                count = 0

                try:    texA = obj.data ['splittexA']; count += 1
                except: texA
                try:    texB = obj.data ['splittexB']; count += 1
                except: texB
                try:    texC = obj.data ['splittexC']; count += 1
                except: texC
                try:    texD = obj.data ['splittexD']; count += 1
                except: texD

                scene.objects.active = obj

                if   (count == 2):  name = '-' + str (texA) + '-' + str (texB)
                elif (count == 3):  name = '-' + str (texA) + '-' + str (texB) + '-' + str (texC)
                elif (count == 4):  name = '-' + str (texA) + '-' + str (texB) + '-' + str (texC) + '-' + str (texD)
                else: continue                

                # original material
                originalmat = obj.active_material

                # new material name
                matname = originalmat.name + name

                exist = False

                try:    obj.active_material = bpy.data.materials [matname];  exist = True
                except: pass

                # create material copy
                if (not exist):

                    mat = originalmat.copy ();  mat.name = matname; obj.active_material = mat

                # create custom property
                if scene.shift_mt_generate_prop != '':

                    obj.active_material [scene.shift_mt_generate_prop] = 'mask' + name

    # log            
    print ('')
    print ('Generate finished in %.4f sec.' % (time.clock () - start_time))
    
    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS SPLIT TEXTURE BACKUP
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processSplitTexBackup ():
    
    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    # log
    print ('\nBackup starting... \n')
    print ('')

    names = (scene.shift_mt_tex0,
             scene.shift_mt_tex1,
             scene.shift_mt_tex2,
             scene.shift_mt_tex3,
             scene.shift_mt_tex4,
             scene.shift_mt_tex5,
             scene.shift_mt_tex6,
             scene.shift_mt_tex7,
             scene.shift_mt_tex8,
             scene.shift_mt_tex9,
             scene.shift_mt_texA,
             scene.shift_mt_texB,
             scene.shift_mt_texC,
             scene.shift_mt_texD,
             scene.shift_mt_texE,
             scene.shift_mt_texF)
    
    for n in names :
        
        if (n != '') :
            try: tex = bpy.data.textures [n]
            except:
                print ("ERROR | Cannot find texture : '" + n + "'")
                return -1

            try :   tex.image.filepath
            except :
                print ("ERROR | Texture : '" + n + "' is not an image")
                return -1
            
            if (tex.image.filepath == ''):
                print ("ERROR | Texture : '" + n + "' is not external image")
                return -1

            filepath = bpy.path.abspath (tex.image.filepath)

            shutil.copy (filepath, filepath + '.bak')

            print (filepath + '.bak')

    # log
    print ('')
    print ('Backup finished in %.4f sec.' % (time.clock () - start_time))

    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS SPLIT TEXTURE RESTORE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processSplitTexRestore ():
    
    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    # log
    print ('\nRestore starting... \n')
    print ('')

    names = (scene.shift_mt_tex0,
             scene.shift_mt_tex1,
             scene.shift_mt_tex2,
             scene.shift_mt_tex3,
             scene.shift_mt_tex4,
             scene.shift_mt_tex5,
             scene.shift_mt_tex6,
             scene.shift_mt_tex7,
             scene.shift_mt_tex8,
             scene.shift_mt_tex9,
             scene.shift_mt_texA,
             scene.shift_mt_texB,
             scene.shift_mt_texC,
             scene.shift_mt_texD,
             scene.shift_mt_texE,
             scene.shift_mt_texF)
    
    for n in names :
        
        if (n != '') :
            try: tex = bpy.data.textures [n]
            except:
                print ("ERROR | Cannot find texture : '" + n + "'")
                return -1

            try :   tex.image.filepath
            except :
                print ("ERROR | Texture : '" + n + "' is not an image")
                return -1
            
            if (tex.image.filepath == ''):
                print ("ERROR | Texture : '" + n + "' is not external image")
                return -1

            filepath = bpy.path.abspath (tex.image.filepath)

            try:    shutil.copy (filepath + '.bak', filepath);  print (filepath)
            except: print (filepath, " : ERROR | Restore failed")

            tex.image.reload ()

            #os.remove (filepath + '.bak')

    # update views
    for scr in bpy.data.screens:
        for area in scr.areas:
            area.tag_redraw ()

    # log
    print ('')
    print ('Restore finished in %.4f sec.' % (time.clock () - start_time))

    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS NONMANIFOLD
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processNonmanifold ():

    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    # shortcut
    selected = bpy.context.selected_objects

    # log
    print ('\nSelection starting... \n\n\tObjects (', len (selected), ') :')
    print ('')

    for i, obj in enumerate (selected):

        # is it mesh ?
        if obj and obj.type == 'MESH':

            # set active object
            scene.objects.active = obj

            # object mode
            bpy.ops.object.mode_set (mode = 'OBJECT')

            # saving vertex normals
            if scene.shift_mt_preserve :
                
                normals = [mathutils.Vector ((v.normal [0], v.normal [1], v.normal [2])) for v in obj.data.vertices]
            
            # edit mode
            bpy.ops.object.mode_set (mode = 'EDIT')
        
            # vertex selection mode
            bpy.context.tool_settings.mesh_select_mode = (True, False, False)

            # unhide all faces
            bpy.ops.mesh.reveal ()
        
            # deselect all
            bpy.ops.mesh.select_all (action = 'DESELECT')

            # select non-manifold
            bpy.ops.mesh.select_non_manifold ()

            # invert selection
            if scene.shift_mt_invert :

                bpy.ops.mesh.select_all (action = 'INVERT')
                   
            # object mode
            bpy.ops.object.mode_set (mode = 'OBJECT')

            if scene.shift_mt_preserve :

                # restoring normals
                for v in obj.data.vertices:    v.normal = normals [v.index]

                # clean up                
                normals [:] = []

            # log
            print (i + 1, "Object : '", obj.name, "'")
            
        else:
            
            # log
            print (i + 1, "Object : '", obj.name, "' is not a mesh")
        
    # log            
    print ('')
    print ('Selection finished in %.4f sec.' % (time.clock () - start_time))

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS MERGE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processMerge ():

    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    # shortcut
    selected = bpy.context.selected_objects

    # do nothing
    if len (selected) < 2:

        return

    # set active object
    if not bpy.context.object:

        scene.objects.active = selected [0]

    # object mode
    bpy.ops.object.mode_set (mode = 'OBJECT')

    # join objects
    bpy.ops.object.join ()

##    # save all hair particles
##    if scene.shift_mt_mhair :
##
##        # save hair here
        
    # remove doubles
    if scene.shift_mt_mdouble :
        
        # edit mode
        bpy.ops.object.mode_set (mode = 'EDIT')

        # vertex selection mode
        bpy.context.tool_settings.mesh_select_mode = (True, False, False)

        # unhide all faces
        bpy.ops.mesh.reveal ()

        # select all
        bpy.ops.mesh.select_all (action = 'SELECT')

        # remove doubles
        bpy.ops.mesh.remove_doubles ()

##    # restore particles
##    if scene.shift_mt_mhair :
##
##        # restore hair here

    # object mode
    bpy.ops.object.mode_set (mode = 'OBJECT')
        
    # log            
    print ('')
    print ('Merge finished in %.4f sec.' % (time.clock () - start_time))
    
####------------------------------------------------------------------------------------------------------------------------------------------------------
#### INTEGRATION AND GUI
####------------------------------------------------------------------------------------------------------------------------------------------------------

class MeshToolsTriangulateOp (bpy.types.Operator):

    bl_idname       = "object.meshtools_triangulate_operator"
    bl_label        = "SHIFT - Mesh Tools"
    bl_description  = "Convert mesh quads to triangles on selected objects"
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        processTriangulate ()

        return {'FINISHED'}

class MeshToolsGridSplitterOp (bpy.types.Operator):

    bl_idname       = "object.meshtools_gridsplitter_operator"
    bl_label        = "SHIFT - Mesh Tools"
    bl_description  = "Split selected mesh to multiple meshes by uniform grid"
    bl_register     = True
    bl_undo         = False
    
    def execute (self, context):

        result = []

        selected = list (bpy.context.selected_objects)

        if (len (selected) >= 1):

            # set some active object
            bpy.context.scene.objects.active = selected [0]

            # object mode
            bpy.ops.object.mode_set (mode = 'OBJECT')
                        
            for obj in selected:

                # deselect all
                bpy.ops.object.select_all (action = 'DESELECT')

                # split
                processSplitGrid (obj)

                # add created objects to the list ..
                sel = bpy.context.selected_objects
                
                for o in sel:   result.append (o)

            # select created objects
            for obj in result:  obj.select = True

            # clean up
            selected [:] = []
            result [:] = []

        return {'FINISHED'}

class MeshToolsTexSplitterSplitOp (bpy.types.Operator):

    bl_idname       = "object.meshtools_texsplitter_split_operator"
    bl_label        = "SHIFT - Mesh Tools"
    bl_description  = "Split selected mesh to multiple meshes by texture overlapping areas"
    bl_register     = True
    bl_undo         = False
    
    def execute (self, context):

        processSplitTex (mode = 'SPLIT')

        return {'FINISHED'}
    
class MeshToolsTexSplitterUnveilOp (bpy.types.Operator):

    bl_idname       = "object.meshtools_texsplitter_unveil_operator"
    bl_label        = "SHIFT - Mesh Tools"
    bl_description  = "Unveil over-overlapped areas of mask textures"
    bl_register     = True
    bl_undo         = False
    
    def execute (self, context):

        processSplitTex (mode = 'UNVEIL')

        return {'FINISHED'}
    
class MeshToolsTexSplitterPolishOp (bpy.types.Operator):

    bl_idname       = "object.meshtools_texsplitter_polish_operator"
    bl_label        = "SHIFT - Mesh Tools"
    bl_description  = "Polish 'weak' parts and remove holes by neighbour interpolation"
    bl_register     = True
    bl_undo         = False
    
    def execute (self, context):

        processSplitTex (mode = 'POLISH')

        return {'FINISHED'}
    
class MeshToolsTexSplitterMergeOp (bpy.types.Operator):

    bl_idname       = "object.meshtools_texsplitter_merge_operator"
    bl_label        = "SHIFT - Mesh Tools"
    bl_description  = "Merges multiple meshes with compatible tex. mask until max. ovelapping value is reached"
    bl_register     = True
    bl_undo         = False
    
    def execute (self, context):

        processSplitTexMerge ()

        return {'FINISHED'}
    
class MeshToolsTexSplitterGenerateOp (bpy.types.Operator):

    bl_idname       = "object.meshtools_texsplitter_generate_operator"
    bl_label        = "SHIFT - Mesh Tools"
    bl_description  = "Generate RGB/RGBA images that are combinations of input textures using 'splittex*' custom properties of selected objects."
    bl_register     = True
    bl_undo         = False
    
    def execute (self, context):

        processSplitTexGenerate ()

        return {'FINISHED'}
    
class MeshToolsTexSplitterBackupOp (bpy.types.Operator):

    bl_idname       = "object.meshtools_texsplitter_backup_operator"
    bl_label        = "SHIFT - Mesh Tools"
    bl_description  = "Make a copy of all images in their source directory adding '.bak' extension."
    bl_register     = True
    bl_undo         = False
    
    def execute (self, context):

        processSplitTexBackup ()

        return {'FINISHED'}
    
class MeshToolsTexSplitterRestoreOp (bpy.types.Operator):

    bl_idname       = "object.meshtools_texsplitter_restore_operator"
    bl_label        = "SHIFT - Mesh Tools"
    bl_description  = "."
    bl_register     = True
    bl_undo         = False
    
    def execute (self, context):

        processSplitTexRestore ()

        return {'FINISHED'}
    
class MeshToolsNonmanifoldOp (bpy.types.Operator):

    bl_idname       = "object.meshtools_nonmanifold_operator"
    bl_label        = "SHIFT - Mesh Tools"
    bl_description  = "Selects nonmanifold vertices on multiple meshes"
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        processNonmanifold ()

        return {'FINISHED'}
    
class MeshToolsMergeOp (bpy.types.Operator):

    bl_idname       = "object.meshtools_merge_operator"
    bl_label        = "SHIFT - Mesh Tools"
    bl_description  = "Merges mesh objects performing some special operations"
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        processMerge ()

        return {'FINISHED'}
    
class MeshToolsPanel (bpy.types.Panel):
     
    bl_idname   = "object.meshtools__panel"
    bl_label    = "SHIFT - Mesh Tools"
    bl_context  = "objectmode"
    bl_register = True
    bl_undo     = True

    bl_space_type   = 'VIEW_3D'
    bl_region_type  = 'TOOLS'

    def draw (self, context):
            
        layout = self.layout
        
        box = layout.box    ()
        box.operator        ('object.meshtools_triangulate_operator', 'Triangulate')

        box = layout.box    ()
        box.operator        ('object.meshtools_merge_operator', 'Merge')
        box = box.box       ()
        box.prop            (context.scene, 'shift_mt_mhair')
        
        box = layout.box    ()
        box.operator        ('object.meshtools_gridsplitter_operator', 'Split')
        
        split = (box.box ()).split   (align = True, percentage = 0.5)
        
        if (context.scene.shift_mt_spatial):
            
            col = split.column  (align = False)
            col.label           ('Cluster Size X :')
            col.label           ('Cluster Size Y :')
            col.label           ('Cluster Size Z :')
            col = split.column  (align = True)
            col.prop            (context.scene, 'shift_mt_clusterx')
            col.prop            (context.scene, 'shift_mt_clustery')
            col.prop            (context.scene, 'shift_mt_clusterz')
            
        else:
            col = split.column  (align = False)
            col.label           ('Subdivision X :')
            col.label           ('Subdivision Y :')
            col.label           ('Subdivision Z :')
            col = split.column  (align = True)
            col.prop            (context.scene, 'shift_mt_subdivisionx')
            col.prop            (context.scene, 'shift_mt_subdivisiony')
            col.prop            (context.scene, 'shift_mt_subdivisionz')
        
        box.box ().prop     (context.scene, 'shift_mt_minfaces')
        
        box = box.box       ()
        box.prop            (context.scene, 'shift_mt_spatial')
        box.prop            (context.scene, 'shift_mt_particles')

        box = layout.box    ()
        box.operator        ('object.meshtools_texsplitter_split_operator',  'Split')

        split = box.split   (align = True, percentage = 0.5)
        col = split.column  (align = False)
        col.label           ('max. Overlapping :')
        col = split.column  (align = True)
        col.prop            (context.scene, 'shift_mt_overlap')

        box = box.box       ();     boxs = box;
        
        if (bpy.context.object) and (bpy.context.object.type == 'MESH'):

            if (bpy.context.object.data.uv_textures.active):
            
                (box.box ()).label  ('UV : ' + bpy.context.object.data.uv_textures.active.name)
        
        split = box.split   (align = True, percentage = 0.35)
        col = split.column  (align = True)
        col.label           ('Texture 0 :')
        col.label           ('Texture 1 :')
        col.label           ('Texture 2 :')
        col.label           ('Texture 3 :')
        col.label           ('Texture 4 :')
        col.label           ('Texture 5 :')
        col.label           ('Texture 6 :')
        col.label           ('Texture 7 :')
        col.label           ('Texture 8 :')
        col.label           ('Texture 9 :')
        col.label           ('Texture A :')
        col.label           ('Texture B :')
        col.label           ('Texture C :')
        col.label           ('Texture D :')
        col.label           ('Texture E :')
        col.label           ('Texture F :')
        col = split.column  (align = True)
        col.prop            (context.scene, 'shift_mt_tex0')
        col.prop            (context.scene, 'shift_mt_tex1')
        col.prop            (context.scene, 'shift_mt_tex2')
        col.prop            (context.scene, 'shift_mt_tex3')
        col.prop            (context.scene, 'shift_mt_tex4')
        col.prop            (context.scene, 'shift_mt_tex5')
        col.prop            (context.scene, 'shift_mt_tex6')
        col.prop            (context.scene, 'shift_mt_tex7')
        col.prop            (context.scene, 'shift_mt_tex8')
        col.prop            (context.scene, 'shift_mt_tex9')
        col.prop            (context.scene, 'shift_mt_texA')
        col.prop            (context.scene, 'shift_mt_texB')
        col.prop            (context.scene, 'shift_mt_texC')
        col.prop            (context.scene, 'shift_mt_texD')
        col.prop            (context.scene, 'shift_mt_texE')
        col.prop            (context.scene, 'shift_mt_texF')
        
        box_ = box.box      ()        
        box_.operator       ('object.meshtools_texsplitter_backup_operator',    'Backup')
        box_.operator       ('object.meshtools_texsplitter_restore_operator',   'Restore')

        box_ = box.box      ()        
        box_.operator       ('object.meshtools_texsplitter_merge_operator',     'Merge')
        
        box = box.box       ()
        box.operator        ('object.meshtools_texsplitter_unveil_operator',    'Unveil')
        box.operator        ('object.meshtools_texsplitter_polish_operator',    'Polish')
        col = box.column    (align = False)
        split = col.split   (align = True, percentage = 0.5)
        split.label         ("Antialiasing :")
        split.prop          (context.scene, 'shift_mt_kernel_antialias',    text = "")
        split = col.split   (align = True, percentage = 0.5)
        split.label         ("Scan :")
        split.prop          (context.scene, 'shift_mt_kernel_scan',         text = "")
        col.separator       ()
        split = col.split   (align = True, percentage = 0.45)
        split.label         ("texel Tolerancy :");                  split.enabled = False
        split.prop          (context.scene, 'shift_mt_tolerancyt',  text = "")
        split = col.split   (align = True, percentage = 0.45)
        split.label         ("face Tolerancy :");                   split.enabled = False
        split.prop          (context.scene, 'shift_mt_tolerancyf',  text = "")
        box_ = box.box      ()
        col = box_.column   (); col.enabled = False
        col.prop            (context.scene, 'shift_mt_saveimages')
        box_.prop           (context.scene, 'shift_mt_selectedfaces')

        box = boxs.box      ()
        box.operator        ('object.meshtools_texsplitter_generate_operator', 'Generate')
        box.prop            (context.scene, 'shift_mt_generate_path')
        box = box.box       ()
        box.prop            (context.scene, 'shift_mt_generate_prop')
        box = box.box       ()
        box.prop            (context.scene, 'shift_mt_generate_mat')

        box = layout.box    ()
        split = box.split   (align = True, percentage = 0.7)
        split.operator      ('object.meshtools_nonmanifold_operator', 'Select Non - Manifold')
        split.prop          (context.scene, 'shift_mt_invert')

        box = layout.box    ()
        box.prop            (context.scene, 'shift_mt_preserve')
        box.prop            (context.scene, 'shift_mt_mdouble')
        
def register ():

    bpy.utils.register_module (__name__)

    # options

    # ----------------------------------------------------------
    bpy.types.Scene.shift_mt_subdivisionx = IntProperty (
        name        = "",
        description = "Subdivision level",
        min         = 1,
        max         = 16,
        step        = 1,
        default     = 1)
    bpy.types.Scene.shift_mt_subdivisiony = IntProperty (
        name        = "",
        description = "Subdivision level",
        min         = 1,
        max         = 16,
        step        = 1,
        default     = 1)    
    bpy.types.Scene.shift_mt_subdivisionz = IntProperty (
        name        = "",
        description = "Subdivision level",
        min         = 1,
        max         = 16,
        step        = 1,
        default     = 1)
    
    # ----------------------------------------------------------
    bpy.types.Scene.shift_mt_clusterx = FloatProperty (
        name        = "",
        description = "Cluster X size",
        min         = 0.01,
        max         = 1000.0,
        precision   = 2,
        step        = 0.1,
        subtype     = 'DISTANCE',
        default     = 1.0)
    bpy.types.Scene.shift_mt_clustery = FloatProperty (
        name        = "",
        description = "Cluster Y size",
        min         = 0.01,
        max         = 1000.0,
        precision   = 2,
        step        = 0.1,
        subtype     = 'DISTANCE',
        default     = 1.0)    
    bpy.types.Scene.shift_mt_clusterz = FloatProperty (
        name        = "",
        description = "Cluster Z size",
        min         = 0.01,
        max         = 1000.0,
        precision   = 2,
        step        = 0.1,
        subtype     = 'DISTANCE',
        default     = 1.0)    
    
    # ----------------------------------------------------------s
    bpy.types.Scene.shift_mt_overlap = IntProperty (
        name        = "",
        description = "Maximum overlaping textures",
        min         = 2,
        max         = 4,
        step        = 1,
        default     = 1)

    # ----------------------------------------------------------s
    bpy.types.Scene.shift_mt_tolerancyt = FloatProperty (
        name        = "texel tolerancy",
        description = "tolerancy factor to ignore subtle over-overlapped texels",
        min         = 0.0,
        max         = 100.0,
        precision   = 2,
        step        = 1.0,
        subtype     = 'PERCENTAGE',
        default     = 0.0)
    bpy.types.Scene.shift_mt_tolerancyf = FloatProperty (
        name        = "face tolarancy",
        description = "tolerancy factor to ignore subtle over-overlapped texels within face",
        min         = 0.0,
        max         = 100.0,
        precision   = 2,
        step        = 1.0,
        subtype     = 'PERCENTAGE',
        default     = 0.0)
    bpy.types.Scene.shift_mt_kernel_antialias = IntProperty (
        name        = "antialiasing kernel",
        description = "specifies how much are neighbour texels blurred (antialiased) when ignored texel are set to zero",
        min         = 0,
        max         = 32,
        step        = 1,
        default     = 1)
    bpy.types.Scene.shift_mt_kernel_scan = IntProperty (
        name        = "scanning kernel",
        description = "specifies how much are neighbour texels are taking into consideration while choosing right layer to shape out",
        min         = 0,
        max         = 32,
        step        = 1,
        default     = 1)
    
    # ----------------------------------------------------------s
    bpy.types.Scene.shift_mt_tex0 = StringProperty (
#        name        = "Texture 0.",
        description = "Texture mask",
        default     = "")
    bpy.types.Scene.shift_mt_tex1 = StringProperty (
#        name        = "Texture 1.",
        description = "Texture mask",
        default     = "")
    bpy.types.Scene.shift_mt_tex2 = StringProperty (
#        name        = "Texture 2.",
        description = "Texture mask",
        default     = "")
    bpy.types.Scene.shift_mt_tex3 = StringProperty (
#        name        = "Texture 3.",
        description = "Texture mask",
        default     = "")
    bpy.types.Scene.shift_mt_tex4 = StringProperty (
#        name        = "Texture 4.",
        description = "Texture mask",
        default     = "")
    bpy.types.Scene.shift_mt_tex5 = StringProperty (
#        name        = "Texture 5.",
        description = "Texture mask",
        default     = "")
    bpy.types.Scene.shift_mt_tex6 = StringProperty (
#        name        = "Texture 6.",
        description = "Texture mask",
        default     = "")
    bpy.types.Scene.shift_mt_tex7 = StringProperty (
#        name        = "Texture 7.",
        description = "Texture mask",
        default     = "")
    bpy.types.Scene.shift_mt_tex8 = StringProperty (
#        name        = "Texture 8.",
        description = "Texture mask",
        default     = "")
    bpy.types.Scene.shift_mt_tex9 = StringProperty (
#        name        = "Texture 9.",
        description = "Texture mask",
        default     = "")
    bpy.types.Scene.shift_mt_texA = StringProperty (
#        name        = "Texture A.",
        description = "Texture mask",
        default     = "")
    bpy.types.Scene.shift_mt_texB = StringProperty (
#        name        = "Texture B.",
        description = "Texture mask",
        default     = "")
    bpy.types.Scene.shift_mt_texC = StringProperty (
#        name        = "Texture C.",
        description = "Texture mask",
        default     = "")
    bpy.types.Scene.shift_mt_texD = StringProperty (
#        name        = "Texture D.",
        description = "Texture mask",
        default     = "")
    bpy.types.Scene.shift_mt_texE = StringProperty (
#        name        = "Texture E.",
        description = "Texture mask",
        default     = "")
    bpy.types.Scene.shift_mt_texF = StringProperty (
#        name        = "Texture F.",
        description = "Texture mask",
        default     = "")

    # ----------------------------------------------------------
    bpy.types.Scene.shift_mt_minfaces = IntProperty (
        name        = "min. faces",
        description = "Minimum face-count for new objects",
        min         = 1,
        max         = 10000,
        step        = 1,
        default     = 32)

    # ----------------------------------------------------------
    bpy.types.Scene.shift_mt_invert = BoolProperty (
        name        = "Invert",
        description = "Invert Selection",
        default     = False)
    bpy.types.Scene.shift_mt_preserve = BoolProperty (
        name        = "Preserve Vertex Normals",
        description = "Preserves vertex normals",
        default     = False)
    bpy.types.Scene.shift_mt_particles = BoolProperty (
        name        = "Split Hair",
        description = "Creates new particles system settings and restore original particle positions",
        default     = False)
    bpy.types.Scene.shift_mt_spatial = BoolProperty (
        name        = "Spatial Grid",
        description = "Using spatial grid insead of division grid, parameters define grid element dimensions",
        default     = True)
    bpy.types.Scene.shift_mt_saveimages = BoolProperty (
        name        = "Save Edited Images",
        description = "Save all edits into original image files (DESTRUCTIVE !)",
        default     = False)
    bpy.types.Scene.shift_mt_selectedfaces = BoolProperty (
        name        = "Unveil Selected Faces",
        description = "Use face selection within selected mesh",
        default     = False)
    
    # ----------------------------------------------------------
    bpy.types.Scene.shift_mt_mhair = BoolProperty (
        name        = "Merge Hair",
        description = "Merge hair particles systems preserving particles",
        default     = False)
    bpy.types.Scene.shift_mt_mdouble = BoolProperty (
        name        = "Remove Doubles",
        description = "Remove vertex duplicity after merge",
        default     = True)

    # ----------------------------------------------------------
    bpy.types.Scene.shift_mt_generate_mat = BoolProperty (
        name        = "Generate Materials",
        description = "Duplicates original material for each split with new appropriate name",
        default     = True)
    bpy.types.Scene.shift_mt_generate_path = StringProperty (
        name        = "",
        description = "Full path or destination directory",
        default     = "",
        subtype     = 'FILE_PATH')
    bpy.types.Scene.shift_mt_generate_prop = StringProperty (
        name        = "Property",
        description = "If not empty contains the name of custom property to be filled with new mask texture name within generated material",
        default     = "")
    
    
def unregister ():

    bpy.utils.unregister_module (__name__)
     
if __name__ == "__main__":
    
    register ()
