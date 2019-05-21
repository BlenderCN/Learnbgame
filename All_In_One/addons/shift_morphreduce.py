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
####======================================================================================================================================================
#### HEADER
####======================================================================================================================================================
####------------------------------------------------------------------------------------------------------------------------------------------------------

bl_info = {
    "name"              : "SHIFT - Morphreduce",
    "author"            : "BBC",
    "version"           : (1,0),
    "blender"           : (2, 5, 3),
    "api"               : 31236,
    "category"          : "Object",
    "location"          : "Tool Shelf",
    "warning"           : '',
    "wiki_url"          : "",
    "tracker_url"       : "",
    "description"       : "Polygon reduction with morphing"}

import bpy
import math
import time
import random
import mathutils

from math       import *
from bpy.props  import *

####------------------------------------------------------------------------------------------------------------------------------------------------------
####======================================================================================================================================================
#### OPTIMIZE
####======================================================================================================================================================
####------------------------------------------------------------------------------------------------------------------------------------------------------

def optimize (obj, arealimit, edgelimit, uvlimit, preserve):

    # shortcut
    scene = bpy.context.scene

    if preserve:

        # saving vertices positions and their normals
        normals = [(mathutils.Vector ((v.co [0], v.co [1], v.co [2])), \
                    mathutils.Vector ((v.normal [0], v.normal [1], v.normal [2]))) for v in obj.data.vertices]

    # active object
    scene.objects.active = obj
    
    # object mode
    bpy.ops.object.mode_set (mode = 'OBJECT')

    # deselect all
    bpy.ops.object.select_all (action = 'DESELECT');    obj.select = True

    # active object
    scene.objects.active = obj

    ##----------------------------------------------------------------------------
    ## DELETING DEGENERATED FACES
    ##----------------------------------------------------------------------------

    # edit mode
    bpy.ops.object.mode_set (mode = 'EDIT')

    # unhide all faces
    bpy.ops.mesh.reveal ()
        
    # deselect all
    bpy.ops.mesh.select_all (action = 'DESELECT')

    # face selection mode
    bpy.context.tool_settings.mesh_select_mode = (False, False, True)

    # object mode
    bpy.ops.object.mode_set (mode = 'OBJECT')
    
    # select zero area faces
    for f in obj.data.faces:
        
        # select degenerated face
        if (f.area < arealimit):   f.select = True
    
    # edit mode again
    bpy.ops.object.mode_set (mode = 'EDIT')
    
    # delete degenerated faces
    bpy.ops.mesh.delete (type = 'FACE')

    # object mode
    bpy.ops.object.mode_set (mode = 'OBJECT')

    ##----------------------------------------------------------------------------
    ## MERGING VERTICES
    ##----------------------------------------------------------------------------

    # edit mode
    bpy.ops.object.mode_set (mode = 'EDIT')

    # vertex selection mode
    bpy.context.tool_settings.mesh_select_mode = (True, False, False)

    # select all vertices
    bpy.ops.mesh.select_all (action = 'SELECT')

    # merge dobules
    bpy.ops.mesh.remove_doubles (limit = edgelimit)
    
    # object mode
    bpy.ops.object.mode_set (mode = 'OBJECT')

    ##----------------------------------------------------------------------------
    ## REMOVING ISOLATED VERTICES
    ##----------------------------------------------------------------------------

    # edit mode
    bpy.ops.object.mode_set (mode = 'EDIT')

    # vertex selection mode
    bpy.context.tool_settings.mesh_select_mode = (True, False, False)

    # select isolated vertices
    bpy.ops.mesh.select_by_number_vertices (type = 'OTHER')

    # deleting vertices
    bpy.ops.mesh.delete (type = 'VERT')    

    # object mode
    bpy.ops.object.mode_set (mode = 'OBJECT')
    
    ##----------------------------------------------------------------------------
    ## STITCHING UVs
    ##----------------------------------------------------------------------------

    # edit mode
    bpy.ops.object.mode_set (mode = 'EDIT')

    # vertex selection mode
    bpy.context.tool_settings.mesh_select_mode = (True, False, False)

    # select all vertices
    bpy.ops.mesh.select_all (action = 'SELECT')

    # stitching
    bpy.ops.uv.stitch (use_limit = True, limit = uvlimit)
    
    # object mode
    bpy.ops.object.mode_set (mode = 'OBJECT')
    
    ##----------------------------------------------------------------------------
    ## NORMALS
    ##----------------------------------------------------------------------------

    if preserve:

        # restore vertex normals
        for v in obj.data.vertices:

            for n in normals:
                
                if (n [0] - v.co).length < edgelimit:
                    
                    v.normal [0] = n [1][0]
                    v.normal [1] = n [1][1]
                    v.normal [2] = n [1][2]

        # clean up
        normals [:] = []
        
    else:

        # we need new normals
        obj.data.calc_normals ()

        # update mesh
        obj.data.update ()

    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
####======================================================================================================================================================
#### MORPH
####======================================================================================================================================================
####------------------------------------------------------------------------------------------------------------------------------------------------------

def morph (obj, preserve):

    # shortcut
    scene = bpy.context.scene

    # set object active
    scene.objects.active = obj

    # original object
    objo = obj

    # original mesh
    mesho = objo.data

    ##----------------------------------------------------------------------------
    ## CHECK DATA
    ##----------------------------------------------------------------------------
    
    try :   morph_layer             = mesho ['morph_layer']
    except: print ("ERROR | Missing 'morph_layer' mesh custom property"); return
    
    try :   morph_scale_position    = mesho ['morph_position']
    except: print ("ERROR | Missing 'morph_scale_position' mesh custom property"); return

    try :   morph_scale_normal      = mesho ['morph_normal']
    except: print ("ERROR | Missing 'morph_scale_normal' mesh custom property"); return
    
    try :   morph_scale_uv          = mesho ['morph_uv']
    except: print ("ERROR | Missing 'morph_scale_uv' mesh custom property"); return

    if   (morph_layer == 1):
        try:
            layer_1 = mesho.uv_textures ['main1a']
            layer_2 = mesho.uv_textures ['main1b']        
        except: print ("ERROR | Missing 'main1a' & 'main1b' uv layers"); return        
    elif (morph_layer == 2):
        try:
            layer_1 = mesho.uv_textures ['main2a']
            layer_2 = mesho.uv_textures ['main2b']        
        except: print ("ERROR | Missing 'main2a' & 'main2b' uv layers"); return        
    elif (morph_layer == 3):
        try:
            layer_1 = mesho.uv_textures ['main3a']
            layer_2 = mesho.uv_textures ['main3b']        
        except: print ("ERROR | Missing 'main3a' & 'main3b' uv layers"); return        
    elif (morph_layer == 4):
        try:
            layer_1 = mesho.uv_textures ['main4a']
            layer_2 = mesho.uv_textures ['main4b']        
        except: print ("ERROR | Missing 'main4a' & 'main4b' uv layers"); return        
    else: print ("ERROR | Missing invalid 'morph_layer' mesh custom property"); return

    ##----------------------------------------------------------------------------
    ## SAVEING NORMALS
    ##----------------------------------------------------------------------------
    
    if preserve:

        # saving vertices positions and their normals
        normals = [mathutils.Vector ((v.normal [0], v.normal [1], v.normal [2])) for v in obj.data.vertices]

    ##----------------------------------------------------------------------------
    ## STICKY UVs
    ##----------------------------------------------------------------------------

    uvdata = mesho.uv_textures.active.data

    uvsticky = [mathutils.Vector ((0.0, 0.0)) for v in mesho.vertices]

    for i, f in enumerate (mesho.faces):
        uvsticky [f.vertices [0]] = uvdata [i].uv1
        uvsticky [f.vertices [1]] = uvdata [i].uv2
        uvsticky [f.vertices [2]] = uvdata [i].uv3
        
##    counters = [0 for v in mesho.vertices]
##    uvsticky = [mathutils.Vector ((0.0, 0.0)) for v in mesho.vertices]
##
##    for i, f in enumerate (mesho.faces):
##        uvsticky [f.vertices [0]] += uvdata [i].uv1;    counters [f.vertices [0]] += 1
##        uvsticky [f.vertices [1]] += uvdata [i].uv2;    counters [f.vertices [1]] += 1
##        uvsticky [f.vertices [2]] += uvdata [i].uv3;    counters [f.vertices [2]] += 1
##    for i, uv in enumerate (uvsticky):
##        if counters [i] > 0:
##            uv [0] /= counters [i]
##            uv [1] /= counters [i]
##
##    counters [:] = []
    
    ##----------------------------------------------------------------------------
    ## DUPLICATE
    ##----------------------------------------------------------------------------

    # object mode
    bpy.ops.object.mode_set (mode = 'OBJECT')

    # duplicate object with mesh
    bpy.ops.object.duplicate (linked = False)

    # duplicated object (selected)
    obj = bpy.context.object

    # new mesh
    mesh = obj.data

    ##----------------------------------------------------------------------------
    ## RESTORE NORMALS
    ##----------------------------------------------------------------------------
    
    if preserve:
        for v in obj.data.vertices:
            v.normal [0] = normals [v.index][0]
            v.normal [1] = normals [v.index][1]
            v.normal [2] = normals [v.index][2]
        normals [:] = []
    
    ##----------------------------------------------------------------------------
    ## MORPH
    ##----------------------------------------------------------------------------

    # we change each vertex only once
    tags = [False for v in mesh.vertices]

    # uv layer
    uvdata = mesh.uv_textures.active.data

    # morphing ..
    for i, f in enumerate (mesh.faces):

        data1 = layer_1.data [i]
        data2 = layer_2.data [i]

        # decoding data ..

        def floorToShortVec2 (vec):
            return mathutils.Vector ((max (- 32767, min (32767, math.floor (vec [0]))),
                                      max (- 32767, min (32767, math.floor (vec [1])))))

        # input is in range <-10.0, 10.0>

        uv1a  = floorToShortVec2 (mathutils.Vector (data1.uv1) * 32767.0 * 0.1)
        uv2a  = floorToShortVec2 (mathutils.Vector (data1.uv2) * 32767.0 * 0.1)
        uv3a  = floorToShortVec2 (mathutils.Vector (data1.uv3) * 32767.0 * 0.1)
        uv1b  = floorToShortVec2 (mathutils.Vector (data2.uv1) * 32767.0 * 0.1)
        uv2b  = floorToShortVec2 (mathutils.Vector (data2.uv2) * 32767.0 * 0.1)
        uv3b  = floorToShortVec2 (mathutils.Vector (data2.uv3) * 32767.0 * 0.1)

        # now we got <-32767, 32767> the same way we export it

        uv1a  = (mathutils.Vector ((32767.0, 32767.0)) + uv1a) / 256.0
        uv2a  = (mathutils.Vector ((32767.0, 32767.0)) + uv2a) / 256.0
        uv3a  = (mathutils.Vector ((32767.0, 32767.0)) + uv3a) / 256.0
        uv1b  = (mathutils.Vector ((32767.0, 32767.0)) + uv1b) / 256.0
        uv2b  = (mathutils.Vector ((32767.0, 32767.0)) + uv2b) / 256.0
        uv3b  = (mathutils.Vector ((32767.0, 32767.0)) + uv3b) / 256.0

        # now we got it in <0, 65534> / 256.0

        def floorVec2 (vec):    return mathutils.Vector ((math.floor (vec [0]),     math.floor (vec [1])))
        def fractVec2 (vec):    return mathutils.Vector ((math.modf  (vec [0])[0],  math.modf  (vec [1])[0]))
        
        uv1am = 2.0 * fractVec2 (uv1a) * 256.0 / 255.0 - mathutils.Vector ((1.0, 1.0))
        uv2am = 2.0 * fractVec2 (uv2a) * 256.0 / 255.0 - mathutils.Vector ((1.0, 1.0))
        uv3am = 2.0 * fractVec2 (uv3a) * 256.0 / 255.0 - mathutils.Vector ((1.0, 1.0))
        uv1bm = 2.0 * fractVec2 (uv1b) * 256.0 / 255.0 - mathutils.Vector ((1.0, 1.0))
        uv2bm = 2.0 * fractVec2 (uv2b) * 256.0 / 255.0 - mathutils.Vector ((1.0, 1.0))
        uv3bm = 2.0 * fractVec2 (uv3b) * 256.0 / 255.0 - mathutils.Vector ((1.0, 1.0))
        
        uv1a  = 2.0 * (floorVec2 (uv1a) / 255.0) - mathutils.Vector ((1.0, 1.0))
        uv2a  = 2.0 * (floorVec2 (uv2a) / 255.0) - mathutils.Vector ((1.0, 1.0))
        uv3a  = 2.0 * (floorVec2 (uv3a) / 255.0) - mathutils.Vector ((1.0, 1.0))
        uv1b  = 2.0 * (floorVec2 (uv1b) / 255.0) - mathutils.Vector ((1.0, 1.0))
        uv2b  = 2.0 * (floorVec2 (uv2b) / 255.0) - mathutils.Vector ((1.0, 1.0))
        uv3b  = 2.0 * (floorVec2 (uv3b) / 255.0) - mathutils.Vector ((1.0, 1.0))

        # values are in range <-1.0,1.0>

        vec1v = mathutils.Vector ((uv1a  [0], uv1am [0], uv1a  [1]))
        vec1n = mathutils.Vector ((uv1am [1], uv1b  [0], uv1bm [0]))
        vec1u = mathutils.Vector ((uv1b  [1], uv1bm [1]))

        vec2v = mathutils.Vector ((uv2a  [0], uv2am [0], uv2a  [1]))
        vec2n = mathutils.Vector ((uv2am [1], uv2b  [0], uv2bm [0]))
        vec2u = mathutils.Vector ((uv2b  [1], uv2bm [1]))
        
        vec3v = mathutils.Vector ((uv3a  [0], uv3am [0], uv3a  [1]))
        vec3n = mathutils.Vector ((uv3am [1], uv3b  [0], uv3bm [0]))
        vec3u = mathutils.Vector ((uv3b  [1], uv3bm [1]))

        if not tags [f.vertices [0]] :
            v1 = mesh.vertices [f.vertices [0]]
            v1.co     += vec1v * morph_scale_position
            v1.normal += vec1n * morph_scale_normal
            tags [v1.index] = True
            
        if not tags [f.vertices [1]] :
            v2 = mesh.vertices [f.vertices [1]]
            v2.co     += vec2v * morph_scale_position
            v2.normal += vec2n * morph_scale_normal
            tags [v2.index] = True
            
        if not tags [f.vertices [2]] :
            v3 = mesh.vertices [f.vertices [2]]
            v3.co     += vec3v * morph_scale_position
            v3.normal += vec3n * morph_scale_normal
            tags [v3.index] = True

        uvdata [i].uv1 += vec1u * morph_scale_uv
        uvdata [i].uv2 += vec2u * morph_scale_uv
        uvdata [i].uv3 += vec3u * morph_scale_uv
        
        # transformed to real size vector the same way we do in shader
    
    # clean up
    uvsticky [:] = []

    return obj

####------------------------------------------------------------------------------------------------------------------------------------------------------
####======================================================================================================================================================
#### GENERATE
####======================================================================================================================================================
####------------------------------------------------------------------------------------------------------------------------------------------------------
    
def generate (obj):

    # shortcut
    scene = bpy.context.scene

    # set object active
    scene.objects.active = obj

    mesh_src = obj.data

    try:    mesh_dst = bpy.data.meshes [obj.data ['morph_destination']]    
    except:
        
        print ("ERROR | Mesh : ", mesh_src.name, " have invalid 'morph_destination' custom property ")
        return -1
    
    if len (mesh_src.vertices) != len (mesh_dst.vertices) :

        print ("ERROR | Mesh : ", mesh_src.name, " have different number of vertices than destination mesh")
        return -1

    ##----------------------------------------------------------------------------
    ## DATA LAYERS
    ##----------------------------------------------------------------------------

    uvlevel = 0

    try :
        layer_1 = mesh_src.uv_textures ['main1'];  uvlevel = 1
    except :
        try :
            layer_1 = mesh_src.uv_textures ['main1a']
            layer_2 = mesh_src.uv_textures ['main1b'];  uvlevel = 1
        except : pass

    try :
        layer_1 = mesh_src.uv_textures ['main2'];  uvlevel = 2
    except :
        try :
            layer_1 = mesh_src.uv_textures ['main2a']
            layer_2 = mesh_src.uv_textures ['main2b'];  uvlevel = 2
        except : pass
    
    try :
        layer_1 = mesh_src.uv_textures ['main3'];  uvlevel = 3
    except :
        try :
            layer_1 = mesh_src.uv_textures ['main3a']
            layer_2 = mesh_src.uv_textures ['main3b'];  uvlevel = 3
        except : pass
    
    try :
        layer_1 = mesh_src.uv_textures ['main4'];  uvlevel = 4
    except :
        try :
            layer_1 = mesh_src.uv_textures ['main4a']
            layer_2 = mesh_src.uv_textures ['main4b'];  uvlevel = 4
        except : pass
        
    ##----------------------------------------------------------------------------
    ## STICKY UVs
    ##----------------------------------------------------------------------------

    uvdata_src = mesh_src.uv_textures.active.data
    uvdata_dst = mesh_dst.uv_textures.active.data

    uvsticky_src = [mathutils.Vector ((0.0, 0.0)) for v in mesh_src.vertices]
    uvsticky_dst = [mathutils.Vector ((0.0, 0.0)) for v in mesh_dst.vertices]
    
    for i, f in enumerate (mesh_dst.faces):
        uvsticky_dst [f.vertices [0]] = uvdata_dst [i].uv1
        uvsticky_dst [f.vertices [1]] = uvdata_dst [i].uv2
        uvsticky_dst [f.vertices [2]] = uvdata_dst [i].uv3
        
##    for i, f in enumerate (mesh_src.faces):
##        uvsticky_src [f.vertices [0]] = uvdata_src [i].uv1
##        uvsticky_src [f.vertices [1]] = uvdata_src [i].uv2
##        uvsticky_src [f.vertices [2]] = uvdata_src [i].uv3

    # sticky UVs
    counters = [0 for v in mesh_src.vertices]

    # our per-vertex UVs are averaged from face data
    for i, f in enumerate (mesh_src.faces):
        uvsticky_src [f.vertices [0]] += uvdata_src [i].uv1;    counters [f.vertices [0]] += 1
        uvsticky_src [f.vertices [1]] += uvdata_src [i].uv2;    counters [f.vertices [1]] += 1
        uvsticky_src [f.vertices [2]] += uvdata_src [i].uv3;    counters [f.vertices [2]] += 1
    for i, uv in enumerate (uvsticky_src):
        if counters [i] > 0:
            uv [0] /= counters [i]
            uv [1] /= counters [i]

    # clean up
    counters [:] = []
        
##    uvdata_src = mesh_src.uv_textures.active.data
##    uvdata_dst = mesh_dst.uv_textures.active.data
##
##    counters_src = [0 for v in mesh_src.vertices]
##    uvsticky_src = [mathutils.Vector ((0.0, 0.0)) for v in mesh_src.vertices]
##
##    counters_dst = [0 for v in mesh_dst.vertices]
##    uvsticky_dst = [mathutils.Vector ((0.0, 0.0)) for v in mesh_dst.vertices]
##    
##    for i, f in enumerate (mesh_src.faces):
##        uvsticky_src [f.vertices [0]] += uvdata_src [i].uv1;    counters_src [f.vertices [0]] += 1
##        uvsticky_src [f.vertices [1]] += uvdata_src [i].uv2;    counters_src [f.vertices [1]] += 1
##        uvsticky_src [f.vertices [2]] += uvdata_src [i].uv3;    counters_src [f.vertices [2]] += 1
##    for i, uv in enumerate (uvsticky_src):
##        if counters_src [i] > 0:
##            uv [0] /= counters_src [i]
##            uv [1] /= counters_src [i]
##
##    for i, f in enumerate (mesh_dst.faces):
##        uvsticky_dst [f.vertices [0]] += uvdata_dst [i].uv1;    counters_dst [f.vertices [0]] += 1
##        uvsticky_dst [f.vertices [1]] += uvdata_dst [i].uv2;    counters_dst [f.vertices [1]] += 1
##        uvsticky_dst [f.vertices [2]] += uvdata_dst [i].uv3;    counters_dst [f.vertices [2]] += 1
##    for i, uv in enumerate (uvsticky_dst):
##        if counters_dst [i] > 0:
##            uv [0] /= counters_dst [i]
##            uv [1] /= counters_dst [i]
            
    ##----------------------------------------------------------------------------
    ## EVALUEATE VERTEX DATA
    ##----------------------------------------------------------------------------

    tmp_dco = []
    tmp_dno = []
    tmp_dtc = []

    maxl_vertex = 0.0
    maxl_normal = 0.0
    maxl_uv     = 0.0
    
    for i, f in enumerate (mesh_src.faces):
        
        v1_src = mesh_src.vertices [f.vertices [0]];    tc1_src = uvsticky_src [f.vertices [0]]
        v2_src = mesh_src.vertices [f.vertices [1]];    tc2_src = uvsticky_src [f.vertices [1]]
        v3_src = mesh_src.vertices [f.vertices [2]];    tc3_src = uvsticky_src [f.vertices [2]]
        
        v1_dst = mesh_dst.vertices [f.vertices [0]];    tc1_dst = uvsticky_dst [f.vertices [0]]
        v2_dst = mesh_dst.vertices [f.vertices [1]];    tc2_dst = uvsticky_dst [f.vertices [1]]
        v3_dst = mesh_dst.vertices [f.vertices [2]];    tc3_dst = uvsticky_dst [f.vertices [2]]
        
        vec1 = v1_dst.co - v1_src.co
        vec2 = v2_dst.co - v2_src.co
        vec3 = v3_dst.co - v3_src.co
        
        if (abs (vec1 [0]) > maxl_vertex): maxl_vertex = abs (vec1 [0])
        if (abs (vec1 [1]) > maxl_vertex): maxl_vertex = abs (vec1 [1])
        if (abs (vec1 [2]) > maxl_vertex): maxl_vertex = abs (vec1 [2])
        if (abs (vec2 [0]) > maxl_vertex): maxl_vertex = abs (vec2 [0])
        if (abs (vec2 [1]) > maxl_vertex): maxl_vertex = abs (vec2 [1])
        if (abs (vec2 [2]) > maxl_vertex): maxl_vertex = abs (vec2 [2])
        if (abs (vec3 [0]) > maxl_vertex): maxl_vertex = abs (vec3 [0])
        if (abs (vec3 [1]) > maxl_vertex): maxl_vertex = abs (vec3 [1])
        if (abs (vec3 [2]) > maxl_vertex): maxl_vertex = abs (vec3 [2])

        tmp_dco.append ((vec1, vec2, vec3))
        
        vec1 = v1_dst.normal - v1_src.normal
        vec2 = v2_dst.normal - v2_src.normal
        vec3 = v3_dst.normal - v3_src.normal

        if (abs (vec1 [0]) > maxl_normal): maxl_normal = abs (vec1 [0])
        if (abs (vec1 [1]) > maxl_normal): maxl_normal = abs (vec1 [1])
        if (abs (vec1 [2]) > maxl_normal): maxl_normal = abs (vec1 [2])
        if (abs (vec2 [0]) > maxl_normal): maxl_normal = abs (vec2 [0])
        if (abs (vec2 [1]) > maxl_normal): maxl_normal = abs (vec2 [1])
        if (abs (vec2 [2]) > maxl_normal): maxl_normal = abs (vec2 [2])
        if (abs (vec3 [0]) > maxl_normal): maxl_normal = abs (vec3 [0])
        if (abs (vec3 [1]) > maxl_normal): maxl_normal = abs (vec3 [1])
        if (abs (vec3 [2]) > maxl_normal): maxl_normal = abs (vec3 [2])

        tmp_dno.append ((vec1, vec2, vec3))
        
        vec1 = tc1_dst - tc1_src
        vec2 = tc2_dst - tc2_src
        vec3 = tc3_dst - tc3_src

        if (abs (vec1 [0]) > maxl_uv): maxl_uv = abs (vec1 [0])
        if (abs (vec1 [1]) > maxl_uv): maxl_uv = abs (vec1 [1])
        if (abs (vec2 [0]) > maxl_uv): maxl_uv = abs (vec2 [0])
        if (abs (vec2 [1]) > maxl_uv): maxl_uv = abs (vec2 [1])
        if (abs (vec3 [0]) > maxl_uv): maxl_uv = abs (vec3 [0])
        if (abs (vec3 [1]) > maxl_uv): maxl_uv = abs (vec3 [1])

        tmp_dtc.append ((vec1, vec2, vec3))

    ##----------------------------------------------------------------------------
    ## EMCODING INTO UV LAYERS
    ##----------------------------------------------------------------------------

    maxl_vertex_inv = 1.0 / max (maxl_vertex,   0.0000000001)
    maxl_normal_inv = 1.0 / max (maxl_normal,   0.0000000001)
    maxl_uv_inv     = 1.0 / max (maxl_uv,       0.0000000001)

    # new properties
    
    if   uvlevel == 0:
        layer_1 = mesh_src.uv_textures.new (name = 'main1a')
        layer_2 = mesh_src.uv_textures.new (name = 'main1b');   mesh_src ['uv1_precision'] = 'lo'        
    elif uvlevel == 1:
        layer_1 = mesh_src.uv_textures.new (name = 'main2a')
        layer_2 = mesh_src.uv_textures.new (name = 'main2b');   mesh_src ['uv2_precision'] = 'lo'
    elif uvlevel == 2:
        layer_1 = mesh_src.uv_textures.new (name = 'main3a')
        layer_2 = mesh_src.uv_textures.new (name = 'main3b');   mesh_src ['uv3_precision'] = 'lo'
    elif uvlevel == 3:
        layer_1 = mesh_src.uv_textures.new (name = 'main4a')
        layer_2 = mesh_src.uv_textures.new (name = 'main4b');   mesh_src ['uv4_precision'] = 'lo'
    else:
        print ("ERROR | Mesh : ", mesh_src.name, " and ", mesh_dst.name, " have reached maximum supported uv layers (4)")
        return

    # generate    
    for i, f in enumerate (mesh_src.faces):

        def codeToByte2 (vector, scale):

            # vector values clamped into <-1.0, 1.0>
            # output vector is in range <0, 255>
            
            return mathutils.Vector ((math.floor (127.5 + 127.5 * max (- 1.0, min (1.0, scale * vector [0]))),
                                      math.floor (127.5 + 127.5 * max (- 1.0, min (1.0, scale * vector [1])))))
        
        def codeToByte3 (vector, scale):

            # vector values clamped into <-1.0, 1.0>
            # output vector is in range <0, 255>

            return mathutils.Vector ((math.floor (127.5 + 127.5 * max (- 1.0, min (1.0, scale * vector [0]))),
                                      math.floor (127.5 + 127.5 * max (- 1.0, min (1.0, scale * vector [1]))),
                                      math.floor (127.5 + 127.5 * max (- 1.0, min (1.0, scale * vector [2])))))

        dco = tmp_dco [i]
        dno = tmp_dno [i]
        dtc = tmp_dtc [i]
        
        data1 = layer_1.data [i]
        data2 = layer_2.data [i]

        # coding data ..

        vec1v = codeToByte3 (dco [0], maxl_vertex_inv)
        vec2v = codeToByte3 (dco [1], maxl_vertex_inv)
        vec3v = codeToByte3 (dco [2], maxl_vertex_inv)

        vec1n = codeToByte3 (dno [0], maxl_normal_inv)
        vec2n = codeToByte3 (dno [1], maxl_normal_inv)
        vec3n = codeToByte3 (dno [2], maxl_normal_inv)

        vec1u = codeToByte2 (dtc [0], maxl_uv_inv)
        vec2u = codeToByte2 (dtc [1], maxl_uv_inv)
        vec3u = codeToByte2 (dtc [2], maxl_uv_inv)

        # vectors values are coded into range <0, 255>
        
        data1.uv1 = mathutils.Vector ((256 * vec1v [0] + vec1v [1], 256 * vec1v [2] + vec1n [0])) - mathutils.Vector ((32768.0, 32768.0))
        data2.uv1 = mathutils.Vector ((256 * vec1n [1] + vec1n [2], 256 * vec1u [0] + vec1u [1])) - mathutils.Vector ((32768.0, 32768.0))
        
        data1.uv2 = mathutils.Vector ((256 * vec2v [0] + vec2v [1], 256 * vec2v [2] + vec2n [0])) - mathutils.Vector ((32768.0, 32768.0))
        data2.uv2 = mathutils.Vector ((256 * vec2n [1] + vec2n [2], 256 * vec2u [0] + vec2u [1])) - mathutils.Vector ((32768.0, 32768.0))
        
        data1.uv3 = mathutils.Vector ((256 * vec3v [0] + vec3v [1], 256 * vec3v [2] + vec3n [0])) - mathutils.Vector ((32768.0, 32768.0))
        data2.uv3 = mathutils.Vector ((256 * vec3n [1] + vec3n [2], 256 * vec3u [0] + vec3u [1])) - mathutils.Vector ((32768.0, 32768.0))

        # vectors coded into short values in range <-32768, 32767>
        
        data1.uv1 = 10.0 * data1.uv1 / 32768.0
        data2.uv1 = 10.0 * data2.uv1 / 32768.0
        
        data1.uv2 = 10.0 * data1.uv2 / 32768.0
        data2.uv2 = 10.0 * data2.uv2 / 32768.0
        
        data1.uv3 = 10.0 * data1.uv3 / 32768.0
        data2.uv3 = 10.0 * data2.uv3 / 32768.0
        
        # output values are in range <-10.0, 9.99)
        
    ##----------------------------------------------------------------------------
    ## ADDING SCALE PROPERTIES
    ##----------------------------------------------------------------------------

    mesh_src ['morph_layer']      = uvlevel + 1
    mesh_src ['morph_position']   = maxl_vertex
    mesh_src ['morph_normal']     = maxl_normal
    mesh_src ['morph_uv']         = maxl_uv

    # clean up

    uvsticky_src [:] = []
    uvsticky_dst [:] = []
    
    return 0

####------------------------------------------------------------------------------------------------------------------------------------------------------
####======================================================================================================================================================
#### REDUCE
####======================================================================================================================================================
####------------------------------------------------------------------------------------------------------------------------------------------------------

def reduce (obj, nameo, named, edgemin, edgemax, angle, size, uvoff, factor, iterations, preserve, select):

    objo = obj

    # shortcut
    scene = bpy.context.scene

    # set active object
    scene.objects.active = obj;     obj.select = True

    # edit mode
    bpy.ops.object.mode_set (mode = 'OBJECT')

    # deselect all
    bpy.ops.object.select_all (action = 'DESELECT')

    # set active object
    scene.objects.active = obj;     obj.select = True

    # select all ?
    if (select):

        # edit mode
        bpy.ops.object.mode_set (mode = 'EDIT')

        # unhide all faces
        bpy.ops.mesh.reveal ()
        
        # select all
        bpy.ops.mesh.select_all (action = 'SELECT')
            
        # object mode
        bpy.ops.object.mode_set (mode = 'OBJECT')
        
    # saving selected vertices
    selected = [v.select for v in objo.data.vertices]

    # check                
    if (len (selected) == 0):

        print ("ERROR | Object : ", obj.name, " have zero selected vertices, nothing to do")
        return

    if preserve :

        # saving vertex normals
        normals = [mathutils.Vector ((v.normal [0], v.normal [1], v.normal [2])) for v in objo.data.vertices]

    ##----------------------------------------------------------------------------
    ## CONVERT QUADS TO TRIANGLES
    ##----------------------------------------------------------------------------
    
    # edit mode
    bpy.ops.object.mode_set (mode = 'EDIT')

    # unhide all faces
    bpy.ops.mesh.reveal ()
    
    # select all
    bpy.ops.mesh.select_all (action = 'SELECT')

    # conversion
    bpy.ops.mesh.quads_convert_to_tris ()

    # object mode
    bpy.ops.object.mode_set (mode = 'OBJECT')

    ##----------------------------------------------------------------------------
    ## CONVERT QUADS TO TRIANGLES FINISHED
    ##----------------------------------------------------------------------------

    # edit mode
    bpy.ops.object.mode_set (mode = 'EDIT')

    # vertex selection mode
    bpy.context.tool_settings.mesh_select_mode = (True, False, False)

    # deselect all vertices
    bpy.ops.mesh.select_all (action = 'DESELECT')

    # object mode
    bpy.ops.object.mode_set (mode = 'OBJECT')

    # restoring selections
    for v in objo.data.vertices:    v.select = selected [v.index]

    if preserve :

        # restoring normals
        for v in objo.data.vertices:    v.normal = normals [v.index]

        # clean up 
        normals [:] = []
    
    # duplicate object with mesh
    bpy.ops.object.duplicate (linked = False)

    # duplicated object (selected)
    obj = bpy.context.object

    # setting new name
    obj.name = nameo

    # setting new data name
    obj.data.name = named

    # original mesh
    mesho = bpy.data.meshes [objo.data.name]

    # new mesh
    mesh  = bpy.data.meshes [obj.data.name]

    # list of tags
    tags  = [False for v in mesh.vertices]
    
    # edges of our mesh containing length of edge
    edges = [[0.0, e] for e in mesh.edges]    

    # sticky UVs
    counters = [0 for v in mesh.vertices]
    uvsticky = [mathutils.Vector ((0.0, 0.0)) for v in mesh.vertices]

    # our per-vertex UVs are averaged from face data
    uv_data = mesh.uv_textures.active.data
    
    for i, f in enumerate (mesh.faces):
        uvsticky [f.vertices [0]] += uv_data [i].uv1;    counters [f.vertices [0]] += 1
        uvsticky [f.vertices [1]] += uv_data [i].uv2;    counters [f.vertices [1]] += 1
        uvsticky [f.vertices [2]] += uv_data [i].uv3;    counters [f.vertices [2]] += 1
    for i, uv in enumerate (uvsticky):
        if counters [i] > 0:
            uv [0] /= counters [i]
            uv [1] /= counters [i]
        
    # cleanup
    counters [:] = []

    # neighbour vertices
    neighbours = [[] for v in mesh.vertices]

    for e in mesh.edges:
        
        v1 = mesh.vertices [e.vertices [0]]
        v2 = mesh.vertices [e.vertices [1]]
        
        neighbours [e.vertices [0]].append (v2)
        neighbours [e.vertices [1]].append (v1)

##    # edges of each vertex
##    vedges = [[] for v in mesh.vertices]
##
##    for e in mesh.edges:
##
##        vedges [e.vertices [0]].append (e)
##        vedges [e.vertices [1]].append (e)

    # faces of each vertex
    vfaces = [[] for v in mesh.vertices]

    for f in mesh.faces:

        vfaces [f.vertices [0]].append (f)
        vfaces [f.vertices [1]].append (f)
        vfaces [f.vertices [2]].append (f)

##    # boundary planes of each vertex
##    vboundary = [[] for v in mesh.vertices]
##
##    for v in mesh.vertices:
##        for f in vfaces [v.index]:
##            if (v.index == f.vertices [0]):
##
##                v1 = mesh.vertices [f.vertices [1]]
##                v2 = mesh.vertices [f.vertices [2]]
##
##                planevec = (f.normal.cross (v1.co - v2.co)).normalize ()
##
##                if planevec.dot (v.co - v1.co) < 0.0:  planevec = - planevec
##
##                vboundary [v.index].append ((planevec, - planevec.dot (v1.co)))
##                
##            elif (v.index == f.vertices [1]):
##
##                v1 = mesh.vertices [f.vertices [0]]
##                v2 = mesh.vertices [f.vertices [2]]
##
##                planevec = (f.normal.cross (v1.co - v2.co)).normalize ()
##
##                if planevec.dot (v.co - v1.co) < 0.0:  planevec = - planevec
##                    
##                vboundary [v.index].append ((planevec, - planevec.dot (v1.co)))
##                
##            elif (v.index == f.vertices [2]):
##                
##                v1 = mesh.vertices [f.vertices [0]]
##                v2 = mesh.vertices [f.vertices [1]]
##
##                planevec = (f.normal.cross (v1.co - v2.co)).normalize ()
##
##                if planevec.dot (v.co - v1.co) < 0.0:  planevec = - planevec
##                    
##                vboundary [v.index].append ((planevec, - planevec.dot (v1.co)))

    def faceDimension (face):

        v1 = mesh.vertices [f.vertices [0]]
        v2 = mesh.vertices [f.vertices [1]]
        v3 = mesh.vertices [f.vertices [2]]

        a = (v3.co - v2.co).length
        b = (v3.co - v1.co).length
        c = (v2.co - v1.co).length

        if (a * b * c) == 0.0:  return (0.0)

        l1 = ((v1.co - v2.co).cross (v1.co - v3.co)).length / a
        l2 = ((v2.co - v1.co).cross (v2.co - v3.co)).length / b
        l3 = ((v3.co - v1.co).cross (v3.co - v2.co)).length / c

        return min (l1, l2, l3)

##    def faceArea (face):
##
##        v1 = mesh.vertices [f.vertices [0]]
##        v2 = mesh.vertices [f.vertices [1]]
##        v3 = mesh.vertices [f.vertices [2]]
##
##        a = (v1.co - v2.co).length
##        b = (v1.co - v3.co).length
##        c = (v2.co - v3.co).length
##
##        if (a * b * c) == 0.0:  return (0.0)
##
##        return (c * sin ((math.pi * a) / (a + b + c)) * b / 2)
##    
##    # face areas
##    fareas = [faceArea (f) for f in mesh.faces]

    def faceNormal (face):

        v1 = mesh.vertices [face.vertices [0]]
        v2 = mesh.vertices [face.vertices [1]]
        v3 = mesh.vertices [face.vertices [2]]

        v = mathutils.Vector ((v1.co - v2.co))

        v = v.cross (v1.co - v3.co)

        v.normalize ()

        v = - v

        return (v)
    
    # face normals
    fnormals = [faceNormal (f) for f in mesh.faces]

    ##----------------------------------------------------------------------------
    ## ITERATING
    ##----------------------------------------------------------------------------
        
    for n in range (iterations):

        # calculate maximum dimensions of faces of each vertex
        vmaxdims = [0.0 for v in mesh.vertices]
        for v in mesh.vertices:
            maxdim = 0.0
            for f in vfaces [v.index]:
                dim = faceDimension (f)
                if (dim > maxdim):  maxdim = dim
            vmaxdims [v.index] = maxdim

        # initializing tags
        for i in range (len (tags)): tags [i] = False

        # initializing edge lengths
        for e in edges:
            v1 = mesh.vertices [e [1].vertices [0]]
            v2 = mesh.vertices [e [1].vertices [1]]
            e [0] = (v1.co - v2.co).length
        
        # sorting edges by length
        edges.sort (key = lambda edges: edges [0])

        ##----------------------------------------------------------------------------
        ## MERGEING VERTEX DATA
        ##----------------------------------------------------------------------------

        for l, e in edges:

            def setVertex (vsrc, vdst, level, plist):

                plist.append (vsrc)
                
                if (vsrc == vdst): return

                vsrc.co [0]               = vdst.co [0]
                vsrc.co [1]               = vdst.co [1]
                vsrc.co [2]               = vdst.co [2]
                vsrc.normal [0]           = vdst.normal [0]
                vsrc.normal [1]           = vdst.normal [1]
                vsrc.normal [2]           = vdst.normal [2]
                uvsticky [vsrc.index][0]  = uvsticky [vdst.index][0]
                uvsticky [vsrc.index][1]  = uvsticky [vdst.index][1]

                tags [vsrc.index]   = True

                level += 1
                
                if level >= iterations : return

                for v in neighbours [vsrc.index] :

                    if (v not in plist) and v.co == vsrc.co :

                        setVertex (v, vdst, level, plist)
            
            # degenerated edge
            if l == 0.0: continue
            
            # edges are sorted so this is the end
            if l > edgemax: break            
            if l < edgemin: continue

            if tags [e.vertices [0]]:   continue
            if tags [e.vertices [1]]:   continue

            v1 = mesh.vertices [e.vertices [0]]
            v2 = mesh.vertices [e.vertices [1]]

            diff1 = abs (uvsticky [v1.index][0] - uvsticky [v2.index][0])
            diff2 = abs (uvsticky [v1.index][1] - uvsticky [v2.index][1])

            if ((diff1 > uvoff) or (diff2 > uvoff)):    continue

            # other way to select direcion ?
            
            if (v1.select):
                
                problem = False

                sx = v1.co [0]
                sy = v1.co [1]
                sz = v1.co [2]

                v1.co [0] = v2.co [0]
                v1.co [1] = v2.co [1]
                v1.co [2] = v2.co [2]

##                zero_areas = 0

                for i, f in enumerate (vfaces [v1.index]):

##                    area        = faceArea (f)
                    normal      = faceNormal (f)
                    dimension   = faceDimension (f)

##                    if area == 0.0 or (normal [0] == 0.0 and normal [1] == 0.0 and normal [2] == 0.0):  continue

##                    if   (area == 0.0):
##                        zero_areas += 1
##                        if (zero_areas > 2):
##                            problem = True
##                            break
                    if   (dimension == 0.0):    continue
                    elif (dimension < size):
                        problem = True
                        break                        
                    elif (dimension < (vmaxdims [v1.index] * factor)):
                        problem = True
                        break                        
##                    elif (area < fareas [f.index]):
##                        problem = True
##                        break
                    elif (math.acos (max (- 1.0, min (1.0, normal.dot (fnormals [f.index])))) > angle):
                        problem = True
                        break

                # check if destionation vertex is inside of
                # convex space of surrounding face opposite edges

##                if not problem:
##                    for b in vboundary [v1.index]:
##                        if ((b [0][0] * v2.co [0] + b [0][1] * v2.co [1] + b [0][2] * v2.co [2] + b [1]) < 0.0):
##                            problem = True
##                            break

                if not problem:

                    plist = []

                    setVertex (v1, v2, 0, plist)

                    plist [:] = []

##                    for vv in neighbours [v1.index]:    v1.normal += vv.normal
##                    for vv in neighbours [v2.index]:    v1.normal += vv.normal
##                    v1.normal = v1.normal.normalize ()

##                    for ee in vedges [v1.index]:
##
##                        vv1 = mesh.vertices [ee.vertices [0]]
##                        vv2 = mesh.vertices [ee.vertices [1]]
##
##                        edges [e.index][0] = (vv1.co - vv2.co).length
                    
##                    for f in vfaces [v1.index]:
##
##                        area    = faceArea (f)
##                        fareas      [f.index] = area
                    
                    tags [v2.index]   = True
                    continue
                else:
                    v1.co [0] = sx
                    v1.co [1] = sy
                    v1.co [2] = sz                    
                                
            if (v2.select):

                problem = False

                sx = v2.co [0]
                sy = v2.co [1]
                sz = v2.co [2]

                v2.co [0] = v1.co [0]
                v2.co [1] = v1.co [1]
                v2.co [2] = v1.co [2]

##                zero_areas = 0

                for i, f in enumerate (vfaces [v2.index]):

##                    area        = faceArea (f)
                    normal      = faceNormal (f)
                    dimension   = faceDimension (f)

##                    if area == 0.0 or (normal [0] == 0.0 and normal [1] == 0.0 and normal [2] == 0.0):  continue

##                    if   (area == 0.0):
##                        zero_areas += 1
##                        if (zero_areas > 2):
##                            problem = True
##                            break
                    if   (dimension == 0.0):    continue
                    elif (dimension < size):
                        problem = True
                        break
                    elif (dimension < (vmaxdims [v1.index] * factor)):
                        problem = True
                        break
##                    elif (area < fareas [f.index]):
##                        problem = True
##                        break
                    elif (math.acos (max (- 1.0, min (1.0, normal.dot (fnormals [f.index])))) > angle):
                        problem = True
                        break

                # check if destionation vertex is inside of
                # convex space of surrounding face opposite edges

##                if not problem:
##                    for b in vboundary [v2.index]:
##                        if ((b [0][0] * v1.co [0] + b [0][1] * v1.co [1] + b [0][2] * v1.co [2] + b [1]) < 0.0):
##                            problem = True
##                            break
                
                if not problem:

                    plist = []
                    
                    setVertex (v2, v1, 0, plist)

                    plist [:] = []

##                    for vv in neighbours [v2.index]:    v2.normal += vv.normal
##                    for vv in neighbours [v1.index]:    v2.normal += vv.normal
##                    v2.normal = v2.normal.normalize ()
                    
##                    for ee in vedges [v2.index]:
##
##                        vv1 = mesh.vertices [ee.vertices [0]]
##                        vv2 = mesh.vertices [ee.vertices [1]]
##
##                        edges [e.index][0] = (vv1.co - vv2.co).length

##                    for f in vfaces [v2.index]:
##
##                        area    = faceArea (f)
##                        fareas      [f.index] = area
                    
                    tags [v1.index]   = True
                    continue
                else:
                    v2.co [0] = sx
                    v2.co [1] = sy
                    v2.co [2] = sz

    # clean up
    edges       [:] = []
    tags        [:] = []

    ##----------------------------------------------------------------------------
    ## SETTING NEW UVs
    ##----------------------------------------------------------------------------

    for i, f in enumerate (mesh.faces):

        uv1 = uvsticky [f.vertices [0]]
        uv2 = uvsticky [f.vertices [1]]
        uv3 = uvsticky [f.vertices [2]]

        uv_data [i].uv1 = mathutils.Vector (uv1)
        uv_data [i].uv2 = mathutils.Vector (uv2)
        uv_data [i].uv3 = mathutils.Vector (uv3)

    ##----------------------------------------------------------------------------
    ## SETTING REFERENCE
    ##----------------------------------------------------------------------------
        
    objo.data ['morph_destination'] = obj.data.name

    # clean up
    neighbours  [:] = []
    selected  [:] = []
    uvsticky [:] = []
    vfaces [:] = []
##    vedges [:] = []

    return obj

####------------------------------------------------------------------------------------------------------------------------------------------------------
####======================================================================================================================================================
#### PROCESS OPTIMIZE
####======================================================================================================================================================
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processOptimize ():

    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    # shortcut
    selected = list (bpy.context.selected_objects)

    # log
    print ('\nOptimizing starting... \n\n\tObjects (', len (selected), ') :')
    print ('')

    for i, obj in enumerate (selected):

        # is it mesh ?
        if obj and obj.type == 'MESH':

            # optimize
            optimize (obj, scene.shift_mr_alimit, scene.shift_mr_elimit, scene.shift_mr_uvlimit, scene.shift_mr_preserve)
            
            # log
            print ("%-2i" % (i + 1), "Object : %-20s" % ("'" + obj.name + "'"))
            
        else:
            
            # log
            print ("%-2i" % (i + 1), ("Object : %-20s" % ("'" + obj.name + "'")) + " is not a mesh")

    # deselect all
    bpy.ops.object.select_all (action = 'DESELECT')

    # selecting new objects
    for o in selected: o.select = True
        
    # log            
    print ('')
    print ('Optimizing finished in %.4f sec.' % (time.clock () - start_time))

    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
####======================================================================================================================================================
#### PROCESS CLEAR
####======================================================================================================================================================
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processClear ():

    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    # shortcut
    selected = list (bpy.context.selected_objects)

    # log
    print ('\nClear starting... \n\n\tObjects (', len (selected), ') :')
    print ('')

    for i, obj in enumerate (selected):

        # is it mesh ?
        if obj and obj.type == 'MESH':

            # set active object
            scene.objects.active = obj

            try:
                        morph_layer = obj.data ['morph_layer']
            except:     morph_layer = -1

            try:    del obj.data ['morph_layer']
            except: pass
            try:    del obj.data ['morph_destination']
            except: pass
            try:    del obj.data ['morph_position']
            except: pass
            try:    del obj.data ['morph_normal']
            except: pass
            try:    del obj.data ['morph_uv']
            except: pass

            if (morph_layer > 0):

                layer1 = None
                layer2 = None
                
                try:

                    if   (morph_layer == 1):
                        layer1 = obj.data.uv_textures ['main1a']
                        layer2 = obj.data.uv_textures ['main1b']
                    elif (morph_layer == 2):
                        layer1 = obj.data.uv_textures ['main2a']
                        layer2 = obj.data.uv_textures ['main2b']
                    elif (morph_layer == 3):
                        layer1 = obj.data.uv_textures ['main3a']
                        layer2 = obj.data.uv_textures ['main3b']
                    elif (morph_layer == 4):
                        layer1 = obj.data.uv_textures ['main4a']
                        layer2 = obj.data.uv_textures ['main4b']

                except: pass;

                if (layer1 and layer2):

                    # saving vertex normals
                    if scene.shift_mr_preserve :
                        
                        normals = [mathutils.Vector ((v.normal [0], v.normal [1], v.normal [2])) for v in obj.data.vertices]

                    # set active layer
                    obj.data.uv_textures.active = layer1

                    # edit mode
                    bpy.ops.object.mode_set (mode = 'EDIT')

                    # remove uv layer
                    bpy.ops.mesh.uv_texture_remove ()
                        
                    # object mode
                    bpy.ops.object.mode_set (mode = 'OBJECT')

                    # set active layer
                    obj.data.uv_textures.active = layer2

                    # edit mode
                    bpy.ops.object.mode_set (mode = 'EDIT')

                    # remove uv layer
                    bpy.ops.mesh.uv_texture_remove ()
                        
                    # object mode
                    bpy.ops.object.mode_set (mode = 'OBJECT')

                    try:
                        if   (morph_layer == 1):    del obj.data ['uv1_precision']
                        elif (morph_layer == 2):    del obj.data ['uv2_precision']
                        elif (morph_layer == 3):    del obj.data ['uv3_precision']
                        elif (morph_layer == 4):    del obj.data ['uv4_precision']
                    except: pass
                                        
                    if scene.shift_mr_preserve :

                        # restoring normals
                        for v in obj.data.vertices:    v.normal = normals [v.index]

                        # clean up                
                        normals [:] = []
            
            # log
            print ("%-2i" % (i + 1), "Object : %-20s" % ("'" + obj.name + "'"))
            
        else:
            
            # log
            print ("%-2i" % (i + 1), ("Object : %-20s" % ("'" + obj.name + "'")) + " is not a mesh")
        
    # log            
    print ('')
    print ('Clear finished in %.4f sec.' % (time.clock () - start_time))

    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
####======================================================================================================================================================
#### PROCESS MORPH
####======================================================================================================================================================
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processMorph ():

    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    # shortcut
    selected = list (bpy.context.selected_objects)

    # list of created objects
    listo = []

    # log
    print ('\nMorphing starting... \n\n\tObjects (', len (selected), ') :')
    print ('')

    for i, obj in enumerate (selected):

        # is it mesh ?
        if obj and obj.type == 'MESH':

            # morph
            objn = morph (obj, scene.shift_mr_preserve)

            if objn :
                
                # add to the list of objects
                listo.append (objn)

                # log
                print ("%-2i" % (i + 1), "Object : %-20s" % ("'" + obj.name + "'"))
            
        else:
            
            # log
            print ("%-2i" % (i + 1), ("Object : %-20s" % ("'" + obj.name + "'")) + " is not a mesh")

    # deselect all
    bpy.ops.object.select_all (action = 'DESELECT')

    # selecting new objects
    for o in listo: o.select = True        
        
    # log            
    print ('')
    print ('Morphing finished in %.4f sec.' % (time.clock () - start_time))

    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
####======================================================================================================================================================
#### PROCESS GENERATE
####======================================================================================================================================================
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processGenerate ():

    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    # shortcut
    selected = list (bpy.context.selected_objects)

    # log
    print ('\nGenerating starting... \n\n\tObjects (', len (selected), ') :')
    print ('')

    for i, obj in enumerate (selected):

        # is it mesh ?
        if obj and obj.type == 'MESH':

            # generate
            if (generate (obj) == 0):

                # log
                print ("%-2i" % (i + 1), "Object : %-20s" % ("'" + obj.name + "'"))
            
        else:
            
            # log
            print ("%-2i" % (i + 1), ("Object : %-20s" % ("'" + obj.name + "'")) + " is not a mesh")
        
    # log            
    print ('')
    print ('Generating finished in %.4f sec.' % (time.clock () - start_time))

    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
####======================================================================================================================================================
#### PROCESS REDUCE
####======================================================================================================================================================
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processReduce ():

    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    if not (scene.shift_mr_edgemin < scene.shift_mr_edgemax):

        print ("ERROR | Edge min. should be less than edge max. Rule is : min < max !")
        return

    # shortcut
    selected = list (bpy.context.selected_objects)

    # list of created objects
    listo = []

    # log
    print ('\nReduce starting... \n\n\tObjects (', len (selected), ') :')
    print ('')

    for i, obj in enumerate (selected):

        # is it mesh ?
        if obj and obj.type == 'MESH':

            # reduce
            objn = reduce (obj, obj.name + '_reduced', obj.data.name + '_reduced', scene.shift_mr_edgemin,
                                                                                   scene.shift_mr_edgemax,
                                                                                   scene.shift_mr_angle,
                                                                                   scene.shift_mr_size,
                                                                                   scene.shift_mr_uvoff,
                                                                                   scene.shift_mr_factor,
                                                                                   scene.shift_mr_iterations,
                                                                                   scene.shift_mr_preserve,
                                                                                   not scene.shift_mr_selected)
            if objn :
                
                # add to the list of objects
                listo.append (objn)

                # delete original ?                    
                if bpy.context.scene.shift_mr_delete:

                    scene.objects.unlink (obj);    bpy.data.objects.remove (obj);

                # log
                print ("%-2i" % (i + 1), "Object : %-20s" % ("'" + obj.name + "'"))
            
        else:
            
            # log
            print ("%-2i" % (i + 1), ("Object : %-20s" % ("'" + obj.name + "'")) + " is not a mesh")

    # deselect all
    bpy.ops.object.select_all (action = 'DESELECT')

    # selecting new objects
    for o in listo: o.select = True
        
    # log
    print ('')
    print ('Reduce finished in %.4f sec.' % (time.clock () - start_time))

    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
####======================================================================================================================================================
#### INTEGRATION AND GUI
####======================================================================================================================================================
####------------------------------------------------------------------------------------------------------------------------------------------------------
    
class MorphreduceOp1 (bpy.types.Operator):

    bl_idname   = "object.morphreduce_operator1"
    bl_label    = "SHIFT - Morphreduce"
    bl_register = True
    bl_undo     = True
    
    def execute (self, context):

        processReduce ()
        
        return {'FINISHED'}

class MorphreduceOp2 (bpy.types.Operator):

    bl_idname   = "object.morphreduce_operator2"
    bl_label    = "SHIFT - Morphreduce"
    bl_register = True
    bl_undo     = True
    
    def execute (self, context):

        processGenerate ()
        
        return {'FINISHED'}

class MorphreduceOp3 (bpy.types.Operator):

    bl_idname   = "object.morphreduce_operator3"
    bl_label    = "SHIFT - Morphreduce"
    bl_register = True
    bl_undo     = True
    
    def execute (self, context):

        processMorph ()
        
        return {'FINISHED'}
    
class MorphreduceOp4 (bpy.types.Operator):

    bl_idname   = "object.morphreduce_operator4"
    bl_label    = "SHIFT - Morphreduce"
    bl_register = True
    bl_undo     = True
    
    def execute (self, context):

        processClear ()
        
        return {'FINISHED'}
    
class MorphreduceOp5 (bpy.types.Operator):

    bl_idname   = "object.morphreduce_operator5"
    bl_label    = "SHIFT - Morphreduce"
    bl_register = True
    bl_undo     = True
    
    def execute (self, context):

        processOptimize ()
        
        return {'FINISHED'}
    
class MorphreducePanel (bpy.types.Panel):
     
    bl_idname   = "object.morphreduce_panel"
    bl_label    = "SHIFT - Morphreduce"
    bl_context  = "objectmode"
    bl_register = True
    bl_undo     = True

    bl_space_type   = 'VIEW_3D'
    bl_region_type  = 'TOOLS'

    def draw (self, context):

        # shortcut
        scene = bpy.context.scene

        # shortcut
        selected = bpy.context.selected_objects

        # check input data
        if len (selected) > 0:

            emorph    = True
            egenerate = True
            
            for obj in selected:
                if obj and obj.type == 'MESH':
                    try:    obj.data ['morph_destination']
                    except: egenerate = False;  break
                                    
            for obj in selected:
                if obj and obj.type == 'MESH':
                    try :
                        obj.data ['morph_position']
                        obj.data ['morph_normal']
                        obj.data ['morph_uv']

                        layer = obj.data ['morph_layer']

                        if   (layer == 1):                        
                            obj.data.uv_textures ['main1a']
                            obj.data.uv_textures ['main1b']
                        elif (layer == 2):                        
                            obj.data.uv_textures ['main2a']
                            obj.data.uv_textures ['main2b']
                        elif (layer == 3):                        
                            obj.data.uv_textures ['main3a']
                            obj.data.uv_textures ['main3b']
                        elif (layer == 4):                        
                            obj.data.uv_textures ['main4a']
                            obj.data.uv_textures ['main4b']
                            
                    except: emorph = False;  break                    
        else:
            emorph    = False
            egenerate = False

        layout = self.layout
        
        box = layout.box    ()
        box.operator        ('object.morphreduce_operator1', 'Reduce')
        
        split = (box.box ()).split (align = True, percentage = 0.35)
        
        col = split.column  (align = True)
        col.label           ('Iterations :')
        col.label           ('Size :')
        col.label           ('Edge min. :')
        col.label           ('Edge max. :')
        col.label           ('Angle :')
        col.label           ('Factor :')
        col.label           ('UV off :')
        col = split.column  (align = True)
        col.prop            (context.scene, 'shift_mr_iterations')
        col.prop            (context.scene, 'shift_mr_size')
        col.prop            (context.scene, 'shift_mr_edgemin')
        col.prop            (context.scene, 'shift_mr_edgemax')
        col.prop            (context.scene, 'shift_mr_angle')
        col.prop            (context.scene, 'shift_mr_factor')
        col.prop            (context.scene, 'shift_mr_uvoff')

        col = box.box       ().column (align = True)        
        col.prop            (context.scene, 'shift_mr_delete')
        col.prop            (context.scene, 'shift_mr_selected')
                
        box = layout.box    ()
        box = box.box       ()
        
        col = box.column    (align = False);    col.enabled = egenerate
        col.operator        ('object.morphreduce_operator2', 'Generate')
        
        col = box.column    (align = True);     col.enabled = emorph
        col.operator        ('object.morphreduce_operator3', 'Morph')
        
        col = box.column    (align = True)
        col.operator        ('object.morphreduce_operator4', 'Clear')
                        
        box = layout.box    ()
        box.operator        ('object.morphreduce_operator5', 'Optimize')

        split = (box.box    ()).split (align = True, percentage = 0.35)
        
        col = split.column  (align = False)
        col.label           ('min. Edge :')
        col.label           ('min. Area :')
        col.label           ('min. UV :')
        
        col = split.column  (align = True)        
        col.prop            (context.scene, 'shift_mr_elimit')
        col.prop            (context.scene, 'shift_mr_alimit')
        col.prop            (context.scene, 'shift_mr_uvlimit')
        
        box = layout.box    ()
        box.prop            (context.scene, 'shift_mr_preserve')
        
def register ():

    bpy.utils.register_module (__name__)
    
    # options

    # ----------------------------------------------------------
    bpy.types.Scene.shift_mr_iterations = IntProperty (
        description = "Number of iterations in reduction process (lead to recucing more polygons)",
        min         = 1,
        max         = 32,
        step        = 1,
        default     = 1)
        
    # ----------------------------------------------------------
    bpy.types.Scene.shift_mr_edgemin = FloatProperty (
        description = "COLLAPSE IF : All changed edges lengths are greater than this value",
        min         = 0.0,
        max         = 100.0,
        precision   = 3,
        step        = 0.01,
        subtype     = 'DISTANCE',
        default     = 0.01)
    bpy.types.Scene.shift_mr_edgemax = FloatProperty (
        description = "COLLAPSE IF : All changed edges lengths are less than this value",
        min         = 0.0,
        max         = 100.0,
        precision   = 3,
        step        = 0.01,
        subtype     = 'DISTANCE',
        default     = 0.1)
    bpy.types.Scene.shift_mr_angle = FloatProperty (
        description = "COLLAPSE IF : All changed faces angles between their new and original normal is less then this value",
        min         = 0.0,
        max         = math.pi / 2.0,
        precision   = 1,
        step        = math.pi / 180.0,
        subtype     = 'ANGLE',
        default     = math.pi * 0.5)
    bpy.types.Scene.shift_mr_size = FloatProperty (
        description = "COLLAPSE IF : All changed faces 'size' is greater than this value",
        min         = 0.0,
        max         = 100.0,
        precision   = 3,
        step        = 0.1,
        subtype     = 'DISTANCE',
        default     = 0.01)
    bpy.types.Scene.shift_mr_factor = FloatProperty (
        description = "COLLAPSE IF : All changed faces 'size' is greater than factor * (biggest size of local faces)",
        min         = 0.0,
        max         = 1.0,
        precision   = 2,
        step        = 0.1,
        subtype     = 'FACTOR',
        default     = 0.5)
    bpy.types.Scene.shift_mr_uvoff = FloatProperty (
        description = "COLLAPSE IF : Moved vertex UV difference is less than this value",
        min         = 0.0,
        max         = 100.0,
        precision   = 3,
        step        = 0.01,
        subtype     = 'NONE',
        default     = 0.25)
    
    # ----------------------------------------------------------
    bpy.types.Scene.shift_mr_delete = BoolProperty (
        name        = "Delete Original",
        description = "Delete original object",
        default     = False)
    bpy.types.Scene.shift_mr_selected = BoolProperty (
        name        = "Selected",
        description = "Process reduction on selected vertices",
        default     = False)

    # ----------------------------------------------------------
    bpy.types.Scene.shift_mr_elimit = FloatProperty (
        description = "Merge threshold, minimum distance between merged vertices",
        min         = 0.001,
        max         = 10.0,
        precision   = 4,
        step        = 0.001,
        subtype     = 'DISTANCE',
        default     = 0.1)
    bpy.types.Scene.shift_mr_alimit = FloatProperty (
        description = "Face area threshold, minimum face area",
        min         = 0.0,
        max         = 100.0,
        precision   = 3,
        step        = 1,
        default     = 0.0)
    bpy.types.Scene.shift_mr_uvlimit = FloatProperty (
        description = "Stitch threshold, minimum distance between merged UVs in normalized coords",
        min         = 0.0,
        max         = 1.0,
        precision   = 3,
        step        = 0.1,
        subtype     = 'NONE',
        default     = 0.01)

    # ----------------------------------------------------------
    bpy.types.Scene.shift_mr_preserve = BoolProperty (
        name        = "Preserve Vertex Normals",
        description = "Result vertices will hold their original normal vectors (no recalculation)",
        default     = False)
     
def unregister ():
    
    bpy.utils.unregister_module (__name__)

    del bpy.types.Scene.shift_mr_size
    del bpy.types.Scene.shift_mr_angle
    del bpy.types.Scene.shift_mr_factor
    del bpy.types.Scene.shift_mr_uvoff
    del bpy.types.Scene.shift_mr_edgemin
    del bpy.types.Scene.shift_mr_edgemax
    del bpy.types.Scene.shift_mr_delete
    del bpy.types.Scene.shift_mr_flimit
    del bpy.types.Scene.shift_mr_alimit
    del bpy.types.Scene.shift_mr_uvlimit
    del bpy.types.Scene.shift_mr_selected
    del bpy.types.Scene.shift_mr_iterations
     
if __name__ == "__main__":
    
    register ()
