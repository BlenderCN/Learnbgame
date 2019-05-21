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
    "name"              : "SHIFT - Texture Tools",
    "author"            : "BBC",
    "version"           : (1,0),
    "blender"           : (2, 5, 3),
    "api"               : 31236,
    "category"          : "Object",
    "location"          : "Image Editor > Properties",
    "warning"           : '',
    "wiki_url"          : "",
    "tracker_url"       : "",
    "description"       : "Various texture operations"}

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
#### PROCESS DECOMPOSE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processDecompose ():

    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    # check path
    if (scene.shift_tt_maskcomposite == ''):
        
        print ("ERROR | Invalid composite file path")
        return -1

    # check path
    if (scene.shift_tt_decompose == ''):
        
        print ("ERROR | Invalid destination path")
        return -1
    
    # log
    print ('\nDecompose starting... \n')
    print ('')

    # toolkit dll
    toolkit = windll.LoadLibrary (sys.path [0] + '\shift_toolkit.dll')

    # DECOMPOSE
    r = toolkit.processDecompose (ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_maskcomposite).encode ('ascii')), ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_decompose).encode ('ascii')))

    # unload dll
    del toolkit

    if (r < 0):
        print ('ERROR | Decompose failed (check external images and read/write permissions)')
    
    # log            
    print ('')
    print ('Decompose finished in %.4f sec.' % (time.clock () - start_time))
    
    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS GENERATE WEIGHTS
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processGenerateWeights ():

    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    # shortcut
    selected = bpy.context.selected_objects

    # check path        
    if (scene.shift_tt_weightspath == ''):
        
        print ("ERROR | Invalid weights file path")
        return -1

    # log
    print ('\nGenerate starting... \n')
    print ('')

    names = (scene.shift_tt_mask1,
             scene.shift_tt_mask2,
             scene.shift_tt_mask3,
             scene.shift_tt_mask4,
             scene.shift_tt_mask5,
             scene.shift_tt_mask6,
             scene.shift_tt_mask7,
             scene.shift_tt_mask8,
             scene.shift_tt_mask9,
             scene.shift_tt_mask10,
             scene.shift_tt_mask11,
             scene.shift_tt_mask12,
             scene.shift_tt_mask13,
             scene.shift_tt_mask14,
             scene.shift_tt_mask15,
             scene.shift_tt_mask16)

    # array of names
    narraytype = ctypes.c_char_p * 16;  narray = narraytype ()
    
    for i in range (16):

        if (names [i] != ''):   filep = bpy.path.abspath (names [i]);    print (filep)
        else:                   filep = ''

        narray [i] = ctypes.c_char_p (filep.encode ('ascii'))
      
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

    print ("")

    # PROCESS OBJECTS

    # toolkit dll
    toolkit = windll.LoadLibrary (sys.path [0] + '\shift_toolkit.dll')

    # GENERATE
    r = toolkit.processWeightsGenerate (narray, ctypes.c_char_p (scene.shift_tt_weightspath.rpartition ('.')[0].encode ('ascii')))

    # unload dll
    del toolkit

    if (r < 0):
        print ('ERROR | Generate failed (check external images and read/write permissions)')
    
    # log            
    print ('')
    print ('Generate finished in %.4f sec.' % (time.clock () - start_time))
    
    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS GENERATE COMPOSITE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processGenerateComposite ():

    start_time = time.clock ()

    # shortcut
    scene = bpy.context.scene

    # shortcut
    selected = bpy.context.selected_objects

    # check input   
    if (scene.shift_tt_composite == ''):
        
        print ("ERROR | Invalid composite file path")
        return -1
    
    # log
    print ('\nGenerate starting... \n')
    print ('')    

    # PROCESS OBJECTS

    # toolkit dll
    toolkit = windll.LoadLibrary (sys.path [0] + '\shift_toolkit.dll')

    if (scene.shift_tt_atlas_mode != 'A'):

        if   (scene.shift_tt_atlas_mode == 'B'):  atlasrange = scene.shift_tt_atlas2x2
        elif (scene.shift_tt_atlas_mode == 'C'):  atlasrange = scene.shift_tt_atlas4x4

        narraystr   = ctypes.c_char_p * atlasrange;
        narrayfloat = ctypes.c_float  * atlasrange;

        diffuse_array        = narraystr ();     normal_array        = narraystr ();     gloss_array         = narraystr ();     shininess_array         = narraystr ()
        diffuse_factor_array = narrayfloat ();   normal_factor_array = narrayfloat ();   gloss_factor_array  = narrayfloat ();   shininess_factor_array  = narrayfloat ()

        transition = (scene.shift_tt_channel_red + scene.shift_tt_channel_green + scene.shift_tt_channel_blue + scene.shift_tt_channel_alpha).encode ('ascii');
        
        while (1):
            if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse1     == ""):   print ('ERROR | 1. Diffuse field is empty');      return
            if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal1      == ""):   print ('ERROR | 1. Normal field is empty');       return
            if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss1       == ""):   print ('ERROR | 1. Gloss field is empty');        return
            if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess1   == ""):   print ('ERROR | 1. Shininess field is empty');    return
            diffuse_array           [ 0] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse1    ).encode ('ascii'))
            diffuse_factor_array    [ 0] = ctypes.c_float                    (scene.shift_tt_factor_diffuse1    )
            normal_array            [ 0] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal1     ).encode ('ascii'))
            normal_factor_array     [ 0] = ctypes.c_float                    (scene.shift_tt_factor_normal1     )
            shininess_array         [ 0] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess1  ).encode ('ascii'))            
            shininess_factor_array  [ 0] = ctypes.c_float                    (scene.shift_tt_factor_shininess1  )
            gloss_array             [ 0] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss1      ).encode ('ascii'))
            gloss_factor_array      [ 0] = ctypes.c_float                    (scene.shift_tt_factor_gloss1      )
            if (atlasrange ==  1): break
            if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse2     == ""):   print ('ERROR | 2. Diffuse field is empty');      return
            if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal2      == ""):   print ('ERROR | 2. Normal field is empty');       return
            if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss2       == ""):   print ('ERROR | 2. Gloss field is empty');        return
            if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess2   == ""):   print ('ERROR | 2. Shininess field is empty');    return
            diffuse_array           [ 1] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse2    ).encode ('ascii'))
            diffuse_factor_array    [ 1] = ctypes.c_float                    (scene.shift_tt_factor_diffuse2    )
            normal_array            [ 1] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal2     ).encode ('ascii'))
            normal_factor_array     [ 1] = ctypes.c_float                    (scene.shift_tt_factor_normal2     )
            shininess_array         [ 1] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess2  ).encode ('ascii'))            
            shininess_factor_array  [ 1] = ctypes.c_float                    (scene.shift_tt_factor_shininess2  )
            gloss_array             [ 1] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss2      ).encode ('ascii'))
            gloss_factor_array      [ 1] = ctypes.c_float                    (scene.shift_tt_factor_gloss2      )
            if (atlasrange ==  2): break            
            if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse3     == ""):   print ('ERROR | 3. Diffuse field is empty');      return
            if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal3      == ""):   print ('ERROR | 3. Normal field is empty');       return
            if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss3       == ""):   print ('ERROR | 3. Gloss field is empty');        return
            if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess3   == ""):   print ('ERROR | 3. Shininess field is empty');    return
            diffuse_array           [ 2] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse3    ).encode ('ascii'))
            diffuse_factor_array    [ 2] = ctypes.c_float                    (scene.shift_tt_factor_diffuse3    )
            normal_array            [ 2] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal3     ).encode ('ascii'))
            normal_factor_array     [ 2] = ctypes.c_float                    (scene.shift_tt_factor_normal3     )
            shininess_array         [ 2] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess3  ).encode ('ascii'))            
            shininess_factor_array  [ 2] = ctypes.c_float                    (scene.shift_tt_factor_shininess3  )
            gloss_array             [ 2] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss3      ).encode ('ascii'))
            gloss_factor_array      [ 2] = ctypes.c_float                    (scene.shift_tt_factor_gloss3      )
            if (atlasrange ==  3): break            
            if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse4     == ""):   print ('ERROR | 4. Diffuse field is empty');      return
            if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal4      == ""):   print ('ERROR | 4. Normal field is empty');       return
            if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss4       == ""):   print ('ERROR | 4. Gloss field is empty');        return
            if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess4   == ""):   print ('ERROR | 4. Shininess field is empty');    return
            diffuse_array           [ 3] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse4    ).encode ('ascii'))
            diffuse_factor_array    [ 3] = ctypes.c_float                    (scene.shift_tt_factor_diffuse4    )
            normal_array            [ 3] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal4     ).encode ('ascii'))
            normal_factor_array     [ 3] = ctypes.c_float                    (scene.shift_tt_factor_normal4     )
            shininess_array         [ 3] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess4  ).encode ('ascii'))            
            shininess_factor_array  [ 3] = ctypes.c_float                    (scene.shift_tt_factor_shininess4  )
            gloss_array             [ 3] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss4      ).encode ('ascii'))
            gloss_factor_array      [ 3] = ctypes.c_float                    (scene.shift_tt_factor_gloss4      )
            if (atlasrange ==  4): break            
            if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse5     == ""):   print ('ERROR | 5. Diffuse field is empty');      return
            if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal5      == ""):   print ('ERROR | 5. Normal field is empty');       return
            if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss5       == ""):   print ('ERROR | 5. Gloss field is empty');        return
            if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess5   == ""):   print ('ERROR | 5. Shininess field is empty');    return
            diffuse_array           [ 4] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse5    ).encode ('ascii'))
            diffuse_factor_array    [ 4] = ctypes.c_float                    (scene.shift_tt_factor_diffuse5    )
            normal_array            [ 4] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal5     ).encode ('ascii'))
            normal_factor_array     [ 4] = ctypes.c_float                    (scene.shift_tt_factor_normal5     )
            shininess_array         [ 4] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess5  ).encode ('ascii'))            
            shininess_factor_array  [ 4] = ctypes.c_float                    (scene.shift_tt_factor_shininess5  )
            gloss_array             [ 4] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss5      ).encode ('ascii'))
            gloss_factor_array      [ 4] = ctypes.c_float                    (scene.shift_tt_factor_gloss5      )
            if (atlasrange ==  5): break            
            if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse6     == ""):   print ('ERROR | 6. Diffuse field is empty');      return
            if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal6      == ""):   print ('ERROR | 6. Normal field is empty');       return
            if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss6       == ""):   print ('ERROR | 6. Gloss field is empty');        return
            if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess6   == ""):   print ('ERROR | 6. Shininess field is empty');    return
            diffuse_array           [ 5] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse6    ).encode ('ascii'))
            diffuse_factor_array    [ 5] = ctypes.c_float                    (scene.shift_tt_factor_diffuse6    )
            normal_array            [ 5] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal6     ).encode ('ascii'))
            normal_factor_array     [ 5] = ctypes.c_float                    (scene.shift_tt_factor_normal6     )
            shininess_array         [ 5] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess6  ).encode ('ascii'))            
            shininess_factor_array  [ 5] = ctypes.c_float                    (scene.shift_tt_factor_shininess6  )
            gloss_array             [ 5] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss6      ).encode ('ascii'))
            gloss_factor_array      [ 5] = ctypes.c_float                    (scene.shift_tt_factor_gloss6      )
            if (atlasrange ==  6): break
            if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse7     == ""):   print ('ERROR | 7. Diffuse field is empty');      return
            if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal7      == ""):   print ('ERROR | 7. Normal field is empty');       return
            if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss7       == ""):   print ('ERROR | 7. Gloss field is empty');        return
            if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess7   == ""):   print ('ERROR | 7. Shininess field is empty');    return
            diffuse_array           [ 6] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse7    ).encode ('ascii'))
            diffuse_factor_array    [ 6] = ctypes.c_float                    (scene.shift_tt_factor_diffuse7    )
            normal_array            [ 6] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal7     ).encode ('ascii'))
            normal_factor_array     [ 6] = ctypes.c_float                    (scene.shift_tt_factor_normal7     )
            shininess_array         [ 6] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess7  ).encode ('ascii'))            
            shininess_factor_array  [ 6] = ctypes.c_float                    (scene.shift_tt_factor_shininess7  )
            gloss_array             [ 6] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss7      ).encode ('ascii'))
            gloss_factor_array      [ 6] = ctypes.c_float                    (scene.shift_tt_factor_gloss7      )
            if (atlasrange ==  7): break            
            if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse8     == ""):   print ('ERROR | 8. Diffuse field is empty');      return
            if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal8      == ""):   print ('ERROR | 8. Normal field is empty');       return
            if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss8       == ""):   print ('ERROR | 8. Gloss field is empty');        return
            if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess8   == ""):   print ('ERROR | 8. Shininess field is empty');    return
            diffuse_array           [ 7] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse8    ).encode ('ascii'))
            diffuse_factor_array    [ 7] = ctypes.c_float                    (scene.shift_tt_factor_diffuse8    )
            normal_array            [ 7] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal8     ).encode ('ascii'))
            normal_factor_array     [ 7] = ctypes.c_float                    (scene.shift_tt_factor_normal8     )
            shininess_array         [ 7] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess8  ).encode ('ascii'))            
            shininess_factor_array  [ 7] = ctypes.c_float                    (scene.shift_tt_factor_shininess8  )
            gloss_array             [ 7] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss8      ).encode ('ascii'))
            gloss_factor_array      [ 7] = ctypes.c_float                    (scene.shift_tt_factor_gloss8      )
            if (atlasrange ==  8): break            
            if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse9     == ""):   print ('ERROR | 9. Diffuse field is empty');      return
            if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal9      == ""):   print ('ERROR | 9. Normal field is empty');       return
            if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss9       == ""):   print ('ERROR | 9. Gloss field is empty');        return
            if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess9   == ""):   print ('ERROR | 9. Shininess field is empty');    return
            diffuse_array           [ 8] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse9    ).encode ('ascii'))
            diffuse_factor_array    [ 8] = ctypes.c_float                    (scene.shift_tt_factor_diffuse9    )
            normal_array            [ 8] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal9     ).encode ('ascii'))
            normal_factor_array     [ 8] = ctypes.c_float                    (scene.shift_tt_factor_normal9     )
            shininess_array         [ 8] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess9  ).encode ('ascii'))            
            shininess_factor_array  [ 8] = ctypes.c_float                    (scene.shift_tt_factor_shininess9  )
            gloss_array             [ 8] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss9      ).encode ('ascii'))
            gloss_factor_array      [ 8] = ctypes.c_float                    (scene.shift_tt_factor_gloss9      )
            if (atlasrange ==  9): break            
            if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse10    == ""):   print ('ERROR | 10. Diffuse field is empty');     return
            if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal10     == ""):   print ('ERROR | 10. Normal field is empty');      return
            if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss10      == ""):   print ('ERROR | 10. Gloss field is empty');       return
            if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess10  == ""):   print ('ERROR | 10. Shininess field is empty');   return
            diffuse_array           [ 9] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse10   ).encode ('ascii'))
            diffuse_factor_array    [ 9] = ctypes.c_float                    (scene.shift_tt_factor_diffuse10    )
            normal_array            [ 9] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal10    ).encode ('ascii'))
            normal_factor_array     [ 9] = ctypes.c_float                    (scene.shift_tt_factor_normal10     )
            shininess_array         [ 9] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess10 ).encode ('ascii'))            
            shininess_factor_array  [ 9] = ctypes.c_float                    (scene.shift_tt_factor_shininess10  )
            gloss_array             [ 9] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss10     ).encode ('ascii'))
            gloss_factor_array      [ 9] = ctypes.c_float                    (scene.shift_tt_factor_gloss10      )
            if (atlasrange == 10): break            
            if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse11    == ""):   print ('ERROR | 11. Diffuse field is empty');     return
            if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal11     == ""):   print ('ERROR | 11. Normal field is empty');      return
            if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss11      == ""):   print ('ERROR | 11. Gloss field is empty');       return
            if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess11  == ""):   print ('ERROR | 11. Shininess field is empty');   return
            diffuse_array           [10] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse11   ).encode ('ascii'))
            diffuse_factor_array    [10] = ctypes.c_float                    (scene.shift_tt_factor_diffuse11   )
            normal_array            [10] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal11    ).encode ('ascii'))
            normal_factor_array     [10] = ctypes.c_float                    (scene.shift_tt_factor_normal11    )
            shininess_array         [10] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess11 ).encode ('ascii'))            
            shininess_factor_array  [10] = ctypes.c_float                    (scene.shift_tt_factor_shininess11 )
            gloss_array             [10] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss11     ).encode ('ascii'))
            gloss_factor_array      [10] = ctypes.c_float                    (scene.shift_tt_factor_gloss11     )
            if (atlasrange == 11): break            
            if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse12    == ""):   print ('ERROR | 12. Diffuse field is empty');     return
            if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal12     == ""):   print ('ERROR | 12. Normal field is empty');      return
            if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss12      == ""):   print ('ERROR | 12. Gloss field is empty');       return
            if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess12  == ""):   print ('ERROR | 12. Shininess field is empty');   return
            diffuse_array           [11] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse12   ).encode ('ascii'))
            diffuse_factor_array    [11] = ctypes.c_float                    (scene.shift_tt_factor_diffuse12   )
            normal_array            [11] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal12    ).encode ('ascii'))
            normal_factor_array     [11] = ctypes.c_float                    (scene.shift_tt_factor_normal12    )
            shininess_array         [11] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess12 ).encode ('ascii'))            
            shininess_factor_array  [11] = ctypes.c_float                    (scene.shift_tt_factor_shininess12 )
            gloss_array             [11] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss12     ).encode ('ascii'))
            gloss_factor_array      [11] = ctypes.c_float                    (scene.shift_tt_factor_gloss12     )
            if (atlasrange == 12): break            
            if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse13    == ""):   print ('ERROR | 13. Diffuse field is empty');     return
            if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal13     == ""):   print ('ERROR | 13. Normal field is empty');      return
            if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss13      == ""):   print ('ERROR | 13. Gloss field is empty');       return
            if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess13  == ""):   print ('ERROR | 13. Shininess field is empty');   return
            diffuse_array           [12] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse13   ).encode ('ascii'))
            diffuse_factor_array    [12] = ctypes.c_float                    (scene.shift_tt_factor_diffuse13   )
            normal_array            [12] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal13    ).encode ('ascii'))
            normal_factor_array     [12] = ctypes.c_float                    (scene.shift_tt_factor_normal13    )
            shininess_array         [12] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess13 ).encode ('ascii'))
            shininess_factor_array  [12] = ctypes.c_float                    (scene.shift_tt_factor_shininess13 )
            gloss_array             [12] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss13     ).encode ('ascii'))
            gloss_factor_array      [12] = ctypes.c_float                    (scene.shift_tt_factor_gloss13     )
            if (atlasrange == 13): break            
            if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse14    == ""):   print ('ERROR | 14. Diffuse field is empty');     return
            if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal14     == ""):   print ('ERROR | 14. Normal field is empty');      return
            if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss14      == ""):   print ('ERROR | 14. Gloss field is empty');       return
            if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess14  == ""):   print ('ERROR | 14. Shininess field is empty');   return
            diffuse_array           [13] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse14   ).encode ('ascii'))
            diffuse_factor_array    [13] = ctypes.c_float                    (scene.shift_tt_factor_diffuse14   )
            normal_array            [13] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal14    ).encode ('ascii'))
            normal_factor_array     [13] = ctypes.c_float                    (scene.shift_tt_factor_normal14    )
            shininess_array         [13] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess14 ).encode ('ascii'))            
            shininess_factor_array  [13] = ctypes.c_float                    (scene.shift_tt_factor_shininess14 )
            gloss_array             [13] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss14     ).encode ('ascii'))
            gloss_factor_array      [13] = ctypes.c_float                    (scene.shift_tt_factor_gloss14     )
            if (atlasrange == 14): break            
            if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse15    == ""):   print ('ERROR | 15. Diffuse field is empty');     return
            if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal15     == ""):   print ('ERROR | 15. Normal field is empty');      return
            if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss15      == ""):   print ('ERROR | 15. Gloss field is empty');       return
            if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess15  == ""):   print ('ERROR | 15. Shininess field is empty');   return
            diffuse_array           [14] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse15   ).encode ('ascii'))
            diffuse_factor_array    [14] = ctypes.c_float                    (scene.shift_tt_factor_diffuse15   )
            normal_array            [14] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal15    ).encode ('ascii'))
            normal_factor_array     [14] = ctypes.c_float                    (scene.shift_tt_factor_normal15    )
            shininess_array         [14] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess15 ).encode ('ascii'))            
            shininess_factor_array  [14] = ctypes.c_float                    (scene.shift_tt_factor_shininess15 )
            gloss_array             [14] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss15     ).encode ('ascii'))
            gloss_factor_array      [14] = ctypes.c_float                    (scene.shift_tt_factor_gloss15     )
            if (atlasrange == 15): break            
            if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse16    == ""):   print ('ERROR | 16. Diffuse field is empty');     return
            if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal16     == ""):   print ('ERROR | 16. Normal field is empty');      return
            if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss16      == ""):   print ('ERROR | 16. Gloss field is empty');       return
            if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess16  == ""):   print ('ERROR | 16. Shininess field is empty');   return
            diffuse_array           [15] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse16   ).encode ('ascii'))
            diffuse_factor_array    [15] = ctypes.c_float                    (scene.shift_tt_factor_diffuse16   )
            normal_array            [15] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal16    ).encode ('ascii'))
            normal_factor_array     [15] = ctypes.c_float                    (scene.shift_tt_factor_normal16    )
            shininess_array         [15] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess16 ).encode ('ascii'))            
            shininess_factor_array  [15] = ctypes.c_float                    (scene.shift_tt_factor_shininess16 )
            gloss_array             [15] = ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss16     ).encode ('ascii'))
            gloss_factor_array      [15] = ctypes.c_float                    (scene.shift_tt_factor_gloss16     )            

        if   (scene.shift_tt_atlas_mode == 'B'):  mode = 2
        elif (scene.shift_tt_atlas_mode == 'C'):  mode = 4
                            
        # GENERATE
        r = toolkit.processGenerateCompositeAtlas (ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_composite).encode ('ascii')), ctypes.c_char_p (transition),
                                                   diffuse_array,        normal_array,        gloss_array,        shininess_array,
                                                   diffuse_factor_array, normal_factor_array, gloss_factor_array, shininess_factor_array, mode, atlasrange)

        if (r == 0):
            
            scene.shift_tt_history_composite.add ()
            scene.shift_tt_history_composite [-1].name = scene.shift_tt_composite;
        
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse1;
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse2;
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse3;
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse4;
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse5;
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse6;
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse7;
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse8;
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse9;
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse10;
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse11;
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse12;
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse13;
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse14;
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse15;
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse16;
            
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal1;
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal2;
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal3;
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal4;
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal5;
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal6;
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal7;
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal8;
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal9;
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal10;
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal11;
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal12;
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal13;
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal14;
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal15;
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal16;
            
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss1;
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss2;
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss3;
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss4;
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss5;
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss6;
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss7;
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss8;
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss9;
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss10;
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss11;
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss12;
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss13;
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss14;
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss15;
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss16;
            
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess1;
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess2;
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess3;
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess4;
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess5;
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess6;
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess7;
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess8;
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess9;
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess10;
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess11;
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess12;
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess13;
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess14;
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess15;
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess16;
    else:

        transition = (scene.shift_tt_channel_red + scene.shift_tt_channel_green + scene.shift_tt_channel_blue + scene.shift_tt_channel_alpha).encode ('ascii');

        if (transition [0] in ['A', 'B', 'C']) and (scene.shift_tt_diffuse == ""):      print ('ERROR | Diffuse field is empty');   return
        if (transition [1] in ['D', 'E', 'F']) and (scene.shift_tt_normal == ""):       print ('ERROR | Normal field is empty');    return
        if (transition [2] in ['G', 'H', 'I']) and (scene.shift_tt_gloss == ""):        print ('ERROR | Gloss field is empty');     return
        if (transition [3] in ['J', 'K', 'L']) and (scene.shift_tt_shininess == ""):    print ('ERROR | Shininess field is empty'); return
        
        # GENERATE
        r = toolkit.processGenerateComposite (ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_composite).encode ('ascii')), ctypes.c_char_p (transition), 
                                              ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_diffuse)  .encode ('ascii')),
                                              ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_normal)   .encode ('ascii')),
                                              ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_gloss)    .encode ('ascii')),
                                              ctypes.c_char_p (bpy.path.abspath (scene.shift_tt_shininess).encode ('ascii')),
                                              ctypes.c_float (scene.shift_tt_factor_diffuse),
                                              ctypes.c_float (scene.shift_tt_factor_normal),
                                              ctypes.c_float (scene.shift_tt_factor_gloss),
                                              ctypes.c_float (scene.shift_tt_factor_shininess))

        if (r == 0):
            
            scene.shift_tt_history_composite.add ()
            scene.shift_tt_history_composite [-1].name = scene.shift_tt_composite;
        
            scene.shift_tt_history_diffuse.add ();      scene.shift_tt_history_diffuse      [-1].name = scene.shift_tt_diffuse;
            scene.shift_tt_history_normal.add ();       scene.shift_tt_history_normal       [-1].name = scene.shift_tt_normal;
            scene.shift_tt_history_gloss.add ();        scene.shift_tt_history_gloss        [-1].name = scene.shift_tt_gloss;
            scene.shift_tt_history_shininess.add ();    scene.shift_tt_history_shininess    [-1].name = scene.shift_tt_shininess;

    # unload dll
    del toolkit

    if (r < 0):
        print ('ERROR | Generate failed (check external images and read/write permissions)')
    
    # log            
    print ('')
    print ('Generate finished in %.4f sec.' % (time.clock () - start_time))
    
    return

######------------------------------------------------------------------------------------------------------------------------------------------------------
###### PROCESS TEXTURE BACKUP
######------------------------------------------------------------------------------------------------------------------------------------------------------
##
##def processBackup ():
##    
##    start_time = time.clock ()
##
##    # shortcut
##    scene = bpy.context.scene
##
##    # log
##    print ('\nBackup starting... \n')
##    print ('')
##
##    names = (scene.shift_tt_tex0,
##             scene.shift_tt_tex1,
##             scene.shift_tt_tex2,
##             scene.shift_tt_tex3,
##             scene.shift_tt_tex4,
##             scene.shift_tt_tex5,
##             scene.shift_tt_tex6,
##             scene.shift_tt_tex7,
##             scene.shift_tt_tex8,
##             scene.shift_tt_tex9,
##             scene.shift_tt_texA,
##             scene.shift_tt_texB,
##             scene.shift_tt_texC,
##             scene.shift_tt_texD,
##             scene.shift_tt_texE,
##             scene.shift_tt_texF)
##    
##    for n in names :
##        
##        if (n != '') :
##            try: tex = bpy.data.textures [n]
##            except:
##                print ("ERROR | Cannot find texture : '" + n + "'")
##                return -1
##
##            try :   tex.image.filepath
##            except :
##                print ("ERROR | Texture : '" + n + "' is not an image")
##                return -1
##            
##            if (tex.image.filepath == ''):
##                print ("ERROR | Texture : '" + n + "' is not external image")
##                return -1
##
##            filepath = bpy.path.abspath (tex.image.filepath)
##
##            shutil.copy (filepath, filepath + '.bak')
##
##            print (filepath + '.bak')
##
##    # log
##    print ('')
##    print ('Backup finished in %.4f sec.' % (time.clock () - start_time))
##
##    return
##
######------------------------------------------------------------------------------------------------------------------------------------------------------
###### PROCESS TEXTURE RESTORE
######------------------------------------------------------------------------------------------------------------------------------------------------------
##
##def processRestore ():
##    
##    start_time = time.clock ()
##
##    # shortcut
##    scene = bpy.context.scene
##
##    # log
##    print ('\nRestore starting... \n')
##    print ('')
##
##    names = (scene.shift_tt_tex0,
##             scene.shift_tt_tex1,
##             scene.shift_tt_tex2,
##             scene.shift_tt_tex3,
##             scene.shift_tt_tex4,
##             scene.shift_tt_tex5,
##             scene.shift_tt_tex6,
##             scene.shift_tt_tex7,
##             scene.shift_tt_tex8,
##             scene.shift_tt_tex9,
##             scene.shift_tt_texA,
##             scene.shift_tt_texB,
##             scene.shift_tt_texC,
##             scene.shift_tt_texD,
##             scene.shift_tt_texE,
##             scene.shift_tt_texF)
##    
##    for n in names :
##        
##        if (n != '') :
##            try: tex = bpy.data.textures [n]
##            except:
##                print ("ERROR | Cannot find texture : '" + n + "'")
##                return -1
##
##            try :   tex.image.filepath
##            except :
##                print ("ERROR | Texture : '" + n + "' is not an image")
##                return -1
##            
##            if (tex.image.filepath == ''):
##                print ("ERROR | Texture : '" + n + "' is not external image")
##                return -1
##
##            filepath = bpy.path.abspath (tex.image.filepath)
##
##            try:    shutil.copy (filepath + '.bak', filepath);  print (filepath)
##            except: print (filepath, " : ERROR | Restore failed")
##
##            tex.image.reload ()
##
##            #os.remove (filepath + '.bak')
##
##    # update views
##    for scr in bpy.data.screens:
##        for area in scr.areas:
##            area.tag_redraw ()
##
##    # log
##    print ('')
##    print ('Restore finished in %.4f sec.' % (time.clock () - start_time))
##
##    return

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### INTEGRATION AND GUI
####------------------------------------------------------------------------------------------------------------------------------------------------------
    
##class TextureToolsBackupOp (bpy.types.Operator):
##
##    bl_idname       = "object.texturetools_backup_operator"
##    bl_label        = "SHIFT - Texture Tools"
##    bl_description  = "Make a copy of all images in their source directory adding '.bak' extension."
##    bl_register     = True
##    bl_undo         = False
##    
##    def execute (self, context):
##
##        processBackup ()
##
##        return {'FINISHED'}
##    
##class TextureToolsRestoreOp (bpy.types.Operator):
##
##    bl_idname       = "object.texturetools_restore_operator"
##    bl_label        = "SHIFT - Texture Tools"
##    bl_description  = "Restore backuped images (from '.bak' files)"
##    bl_register     = True
##    bl_undo         = False
##    
##    def execute (self, context):
##
##        processRestore ()
##
##        return {'FINISHED'}
    
class TextureToolsDecomposeOp (bpy.types.Operator):

    bl_idname       = "object.texturetools_decompose_operator"
    bl_label        = "SHIFT - Texture Tools"
    bl_description  = "Decompose individual masks identified by unique color (max 32)"
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        processDecompose ()
    
        return {'FINISHED'}
    
class TextureToolsWeightsOp (bpy.types.Operator):

    bl_idname       = "object.texturetools_weights_operator"
    bl_label        = "SHIFT - Texture Tools"
    bl_description  = "Generate weights and mask map"
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        processGenerateWeights ()
    
        return {'FINISHED'}
    
class TextureToolsMask1ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_mask1_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_mask1);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsMask2ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_mask2_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_mask2);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsMask3ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_mask3_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_mask3);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsMask4ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_mask4_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_mask4);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsMask5ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_mask5_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_mask5);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsMask6ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_mask6_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_mask6);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsMask7ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_mask7_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_mask7);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsMask8ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_mask8_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_mask8);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsMask9ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_mask9_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_mask9);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsMask10ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_mask10_view_operator";  bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_mask10);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsMask11ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_mask11_view_operator";  bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_mask11);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsMask12ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_mask12_view_operator";  bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_mask12);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsMask13ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_mask13_view_operator";  bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_mask13);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsMask14ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_mask14_view_operator";  bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_mask14);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsMask15ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_mask15_view_operator";  bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_mask15);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsMask16ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_mask16_view_operator";  bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_mask16);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
    
class TextureToolsCompositeOp (bpy.types.Operator):

    bl_idname       = "object.texturetools_composite_operator"
    bl_label        = "SHIFT - Texture Tools"
    bl_description  = "Generate weights and mask map"
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        processGenerateComposite ()

        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_composite);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: pass
    
        return {'FINISHED'}
    
class TextureToolsCompositeViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_composite_view_operator";  bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_composite);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
    
class TextureToolsDiffuseViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsNormalViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal_view_operator";     bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal);       image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsGlossViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss_view_operator";      bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss);        image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsShininessViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess_view_operator";  bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}

class TextureToolsDiffuse1ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse1_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse1);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsDiffuse2ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse2_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse2);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsDiffuse3ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse3_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse3);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsDiffuse4ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse4_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse4);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsDiffuse5ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse5_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse5);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsDiffuse6ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse6_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse6);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsDiffuse7ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse7_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse7);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsDiffuse8ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse8_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse8);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsDiffuse9ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse9_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse9);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsDiffuse10ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse10_view_operator";  bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse10);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsDiffuse11ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse11_view_operator";  bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse11);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsDiffuse12ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse12_view_operator";  bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse12);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsDiffuse13ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse13_view_operator";  bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse13);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsDiffuse14ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse14_view_operator";  bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse14);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsDiffuse15ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse15_view_operator";  bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse15);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsDiffuse16ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse16_view_operator";  bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_diffuse16);    image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}

class TextureToolsNorma1lViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal1_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal1);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsNorma2lViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal2_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal2);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsNorma3lViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal3_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal3);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsNorma4lViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal4_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal4);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsNorma5lViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal5_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal5);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsNorma6lViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal6_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal6);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsNorma7lViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal7_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal7);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsNorma8lViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal8_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal8);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsNorma9lViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal9_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal9);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsNorma10lViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal10_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal10);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsNorma11lViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal11_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal11);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsNorma12lViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal12_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal12);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsNorma13lViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal13_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal13);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsNorma14lViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal14_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal14);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsNorma15lViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal15_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal15);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsNorma16lViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_normal16_view_operator";   bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_normal16);     image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}

class TextureToolsGloss1ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss1_view_operator";     bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss1);       image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsGloss2ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss2_view_operator";     bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss2);       image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsGloss3ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss3_view_operator";     bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss3);       image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsGloss4ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss4_view_operator";     bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss4);       image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsGloss5ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss5_view_operator";     bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss5);       image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsGloss6ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss6_view_operator";     bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss6);       image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsGloss7ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss7_view_operator";     bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss7);       image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsGloss8ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss8_view_operator";     bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss8);       image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsGloss9ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss9_view_operator";     bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss9);       image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsGloss10ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss10_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss10);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsGloss11ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss11_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss11);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsGloss12ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss12_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss12);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsGloss13ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss13_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss13);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsGloss14ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss14_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss14);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsGloss15ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss15_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss15);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsGloss16ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_gloss16_view_operator";    bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_gloss16);      image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}

class TextureToolsShininess1ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess1_view_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess1);   image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsShininess2ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess2_view_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess2);   image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsShininess3ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess3_view_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess3);   image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsShininess4ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess4_view_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess4);   image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsShininess5ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess5_view_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess5);   image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsShininess6ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess6_view_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess6);   image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsShininess7ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess7_view_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess7);   image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsShininess8ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess8_view_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess8);   image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsShininess9ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess9_view_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess9);   image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsShininess10ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess10_view_operator";bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess10);  image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsShininess11ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess11_view_operator";bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess11);  image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsShininess12ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess12_view_operator";bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess12);  image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsShininess13ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess13_view_operator";bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess13);  image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsShininess14ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess14_view_operator";bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess14);  image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsShininess15ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess15_view_operator";bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess15);  image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}
class TextureToolsShininess16ViewOp (bpy.types.Operator):
    bl_idname = "object.texturetools_shininess16_view_operator";bl_label = "SHIFT - Texture Tools"; bl_description = "View image in image editor"; bl_register = True; bl_undo = True;    
    def execute (self, context):        
        bpy.context.area.type = 'IMAGE_EDITOR'        
        try:    image = bpy.data.images.load (context.scene.shift_tt_shininess16);  image.reload ();    bpy.context.area.active_space.image = image;    image.user_clear ()
        except: return {'CANCELLED'}
        return {'FINISHED'}

    
class TextureToolsCompositeBrowseOp(bpy.types.Operator):    
    bl_idname = "object.texturetools_composite_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_composite = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}

class TextureToolsDiffuseBrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsNormalBrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal = self.filepath;      return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsGlossBrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss = self.filepath;       return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsShininessBrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}

class TextureToolsDiffuse1BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse1_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse1  = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsDiffuse2BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse2_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse2  = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsDiffuse3BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse3_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse3  = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsDiffuse4BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse4_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse4  = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsDiffuse5BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse5_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse5  = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsDiffuse6BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse6_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse6  = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsDiffuse7BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse7_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse7  = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsDiffuse8BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse8_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse8  = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsDiffuse9BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse9_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse9  = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsDiffuse10BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse10_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse10 = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsDiffuse11BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse11_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse11 = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsDiffuse12BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse12_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse12 = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsDiffuse13BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse13_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse13 = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsDiffuse14BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse14_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse14 = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsDiffuse15BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse15_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse15 = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsDiffuse16BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_diffuse16_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_diffuse16 = self.filepath;   return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}

class TextureToolsNormal1BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal1_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal1 = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsNormal2BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal2_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal2 = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsNormal3BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal3_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal3 = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsNormal4BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal4_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal4 = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsNormal5BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal5_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal5 = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsNormal6BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal6_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal6 = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsNormal7BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal7_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal7 = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsNormal8BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal8_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal8 = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsNormal9BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal9_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal9 = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsNormal10BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal10_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal10 = self.filepath;    return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsNormal11BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal11_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal11 = self.filepath;    return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsNormal12BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal12_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal12 = self.filepath;    return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsNormal13BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal13_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal13 = self.filepath;    return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsNormal14BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal14_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal14 = self.filepath;    return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsNormal15BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal15_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal15 = self.filepath;    return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsNormal16BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_normal16_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_normal16 = self.filepath;    return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}

class TextureToolsGloss1BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss1_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss1 = self.filepath;      return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsGloss2BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss2_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss2 = self.filepath;      return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsGloss3BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss3_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss3 = self.filepath;      return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsGloss4BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss4_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss4 = self.filepath;      return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsGloss5BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss5_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss5 = self.filepath;      return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsGloss6BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss6_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss6 = self.filepath;      return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsGloss7BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss7_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss7 = self.filepath;      return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsGloss8BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss8_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss8 = self.filepath;      return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsGloss9BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss9_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss9 = self.filepath;      return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsGloss10BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss10_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss10 = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsGloss11BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss11_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss11 = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsGloss12BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss12_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss12 = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsGloss13BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss13_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss13 = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsGloss14BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss14_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss14 = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsGloss15BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss15_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss15 = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsGloss16BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_gloss16_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_gloss16 = self.filepath;     return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}

class TextureToolsShininess1BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess1_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess1 = self.filepath;  return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsShininess2BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess2_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess2 = self.filepath;  return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsShininess3BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess3_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess3 = self.filepath;  return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsShininess4BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess4_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess4 = self.filepath;  return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsShininess5BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess5_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess5 = self.filepath;  return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsShininess6BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess6_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess6 = self.filepath;  return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsShininess7BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess7_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess7 = self.filepath;  return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsShininess8BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess8_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess8 = self.filepath;  return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsShininess9BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess9_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess9 = self.filepath;  return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsShininess10BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess10_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess10 = self.filepath; return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsShininess11BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess11_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess11 = self.filepath; return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsShininess12BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess12_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess12 = self.filepath; return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsShininess13BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess13_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess13 = self.filepath; return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsShininess14BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess14_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess14 = self.filepath; return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsShininess15BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess15_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess15 = self.filepath; return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}
class TextureToolsShininess16BrowseOp(bpy.types.Operator):
    bl_idname = "object.texturetools_shininess16_browse_operator"; bl_label = "SHIFT - Texture Tools"; bl_description = "Browse files"; filepath = bpy.props.StringProperty (subtype = "FILE_PATH");
    def execute (self, context):        context.scene.shift_tt_shininess16 = self.filepath; return {'FINISHED'}
    def invoke  (self, context, event): context.window_manager.fileselect_add (self);       return {'RUNNING_MODAL'}

        
class TextureToolsPanel (bpy.types.Panel):
     
    bl_idname   = "object.texturetools_panel"
    bl_label    = "SHIFT - Texture Tools"
    bl_context  = "objectmode"
    bl_register = True
    bl_undo     = True

    bl_space_type   = 'IMAGE_EDITOR'    #'VIEW_3D'
    bl_region_type  = 'UI'              #'TOOLS'

    def draw (self, context):
            
        layout = self.layout
        
        box = layout.box    ()
        box.operator        ('object.texturetools_decompose_operator',  'Decompose')
        split = box.split   (align = True, percentage = 0.2)
        split.label         ('Composite :')
        split.prop          (context.scene, 'shift_tt_maskcomposite')
        split = box.split   (align = True, percentage = 0.2)
        split.label         ('Destination :')
        split.prop          (context.scene, 'shift_tt_decompose')
        
        layout.separator    ()

        box = layout.box    ()
        box.operator        ('object.texturetools_weights_operator',  'Generate Weights')

        split = box.split   (align = True, percentage = 0.2)
        split.label         ('Weights :')
        split.prop          (context.scene, 'shift_tt_weightspath')

        box = box.box       ();     boxs = box;
                
        split = box.split   (align = True, percentage = 0.2)
        col = split.column  (align = True)
        
        for n in range (16):
            col.label           ('Texture '+ str (n + 1) +' :')
            
        col = split.column  (align = True)

        for n in range (16):

            split = col.split (align = True, percentage = 0.9)            
            
            split.prop          (context.scene, 'shift_tt_mask' + str (n + 1))
            split.operator      ('object.texturetools_mask' + str (n + 1) + '_view_operator', '', icon = 'FILE_IMAGE')
                
##        box_ = box.box      ()
##        box_.operator       ('object.texturetools_backup_operator',    'Backup')
##        box_.operator       ('object.texturetools_restore_operator',   'Restore')

        layout.separator    ()

        box = layout.box    ()
        box.operator        ('object.texturetools_composite_operator', 'Generate Composite')

        split = box.split   (align = True, percentage = 0.3)
        split.label         ('Composite :')
        split = split.split (align = True, percentage = 0.1)
        split.operator      ('object.texturetools_composite_browse_operator', '', icon = 'FILE_FOLDER')        
        split = split.split (align = True, percentage = 0.9)
        split.prop_search   (context.scene, 'shift_tt_composite', context.scene, 'shift_tt_history_composite', icon = 'TRIA_DOWN')
        split.operator      ('object.texturetools_composite_view_operator', '', icon = 'FILE_IMAGE')

        headerbox = box.box ()

        if (context.scene.shift_tt_atlas_mode != 'A'):

            split = headerbox.split (align = False, percentage = 0.6)
            split.prop          (context.scene, 'shift_tt_atlas_mode')
            row = split.row     ()            

            if   (context.scene.shift_tt_atlas_mode == 'B'):  atlasrange = context.scene.shift_tt_atlas2x2; row.prop (context.scene, 'shift_tt_atlas2x2')
            elif (context.scene.shift_tt_atlas_mode == 'C'):  atlasrange = context.scene.shift_tt_atlas4x4; row.prop (context.scene, 'shift_tt_atlas4x4')

            headerbox = headerbox.box ()

            col = headerbox.column (align = True)
            row = col.row (align = True)
            row.label ('Red')
            row.label ('Green')
            row.label ('Blue')
            row.label ('Alpha')
            row = col.row (align = True)
            row.prop (context.scene, 'shift_tt_channel_red')
            row.prop (context.scene, 'shift_tt_channel_green')
            row.prop (context.scene, 'shift_tt_channel_blue')
            row.prop (context.scene, 'shift_tt_channel_alpha')

            for n in range (atlasrange):

                index = str (n + 1)
                
                split = box.box ().split   (align = True, percentage = 0.2)
                
                col = split.column  (align = True)
                col.label           (index + '. Diffuse :')
                col.label           (index + '. Normal :')
                col.label           (index + '. Gloss :')
                col.label           (index + '. Shininess :')
                col = split.column  (align = True)
                split = col.split   (align = True, percentage = 0.1)
                split.operator      ('object.texturetools_diffuse'              + index +'_browse_operator',    '', icon = 'FILE_FOLDER')
                split = split.split (align = True, percentage = 0.7)
                split.prop_search   (context.scene, 'shift_tt_diffuse'          + index, context.scene, 'shift_tt_history_diffuse',     icon = 'TRIA_DOWN')
                split = split.split (align = True, percentage = 0.7)
                split.prop          (context.scene, 'shift_tt_factor_diffuse'   + index)
                split.operator      ('object.texturetools_diffuse'              + index +'_view_operator',      '', icon = 'FILE_IMAGE')
                split = col.split   (align = True, percentage = 0.1)
                split.operator      ('object.texturetools_normal'               + index +'_browse_operator',    '', icon = 'FILE_FOLDER')
                split = split.split (align = True, percentage = 0.7)
                split.prop_search   (context.scene, 'shift_tt_normal'           + index, context.scene, 'shift_tt_history_normal',      icon = 'TRIA_DOWN')
                split = split.split (align = True, percentage = 0.7)
                split.prop          (context.scene, 'shift_tt_factor_normal'    + index)
                split.operator      ('object.texturetools_normal'               + index +'_view_operator',      '', icon = 'FILE_IMAGE')
                split = col.split   (align = True, percentage = 0.1)
                split.operator      ('object.texturetools_gloss'                + index +'_browse_operator',    '', icon = 'FILE_FOLDER')
                split = split.split (align = True, percentage = 0.7)                
                split.prop_search   (context.scene, 'shift_tt_gloss'            + index, context.scene, 'shift_tt_history_gloss',       icon = 'TRIA_DOWN')
                split = split.split (align = True, percentage = 0.7)
                split.prop          (context.scene, 'shift_tt_factor_gloss'     + index)
                split.operator      ('object.texturetools_gloss'                + index +'_view_operator',      '', icon = 'FILE_IMAGE')
                split = col.split   (align = True, percentage = 0.1)
                split.operator      ('object.texturetools_shininess'            + index +'_browse_operator',    '', icon = 'FILE_FOLDER')
                split = split.split (align = True, percentage = 0.7)                
                split.prop_search   (context.scene, 'shift_tt_shininess'        + index, context.scene, 'shift_tt_history_shininess',   icon = 'TRIA_DOWN')
                split = split.split (align = True, percentage = 0.7)
                split.prop          (context.scene, 'shift_tt_factor_shininess' + index)
                split.operator      ('object.texturetools_shininess'            + index +'_view_operator',      '', icon = 'FILE_IMAGE')
                
        else:

            headerbox.prop (context.scene, 'shift_tt_atlas_mode')
            
            headerbox = headerbox.box ()

            col = headerbox.column (align = True)
            row = col.row (align = True)
            row.label ('Red')
            row.label ('Green')
            row.label ('Blue')
            row.label ('Alpha')
            row = col.row (align = True)
            row.prop (context.scene, 'shift_tt_channel_red')
            row.prop (context.scene, 'shift_tt_channel_green')
            row.prop (context.scene, 'shift_tt_channel_blue')
            row.prop (context.scene, 'shift_tt_channel_alpha')
            
            split = box.box ().split    (align = True, percentage = 0.2)
            
            col = split.column  (align = True)
            col.label           ('Diffuse :')
            col.label           ('Normal :')
            col.label           ('Gloss :')
            col.label           ('Shininess :')
            col = split.column  (align = True)
            split = col.split   (align = True, percentage = 0.1)
            split.operator      ('object.texturetools_diffuse_browse_operator', '',     icon = 'FILE_FOLDER')
            split = split.split (align = True, percentage = 0.7)
            split.prop_search   (context.scene, 'shift_tt_diffuse',      context.scene, 'shift_tt_history_diffuse',     icon = 'TRIA_DOWN')
            split = split.split (align = True, percentage = 0.7)            
            split.prop          (context.scene, 'shift_tt_factor_diffuse')
            split.operator      ('object.texturetools_diffuse_view_operator', '',       icon = 'FILE_IMAGE')            
            split = col.split   (align = True, percentage = 0.1)            
            split.operator      ('object.texturetools_normal_browse_operator', '',      icon = 'FILE_FOLDER')
            split = split.split (align = True, percentage = 0.7)
            split.prop_search   (context.scene, 'shift_tt_normal',       context.scene, 'shift_tt_history_normal',      icon = 'TRIA_DOWN')
            split = split.split (align = True, percentage = 0.7)            
            split.prop          (context.scene, 'shift_tt_factor_normal')
            split.operator      ('object.texturetools_normal_view_operator', '',        icon = 'FILE_IMAGE')
            split = col.split   (align = True, percentage = 0.1)
            split.operator      ('object.texturetools_gloss_browse_operator', '',       icon = 'FILE_FOLDER')
            split = split.split (align = True, percentage = 0.7)
            split.prop_search   (context.scene, 'shift_tt_gloss',        context.scene, 'shift_tt_history_gloss',       icon = 'TRIA_DOWN')
            split = split.split (align = True, percentage = 0.7)            
            split.prop          (context.scene, 'shift_tt_factor_gloss')
            split.operator      ('object.texturetools_gloss_view_operator', '',         icon = 'FILE_IMAGE')
            split = col.split   (align = True, percentage = 0.1)
            split.operator      ('object.texturetools_shininess_browse_operator', '',   icon = 'FILE_FOLDER')
            split = split.split (align = True, percentage = 0.7)
            split.prop_search   (context.scene, 'shift_tt_shininess',    context.scene, 'shift_tt_history_shininess',   icon = 'TRIA_DOWN')
            split = split.split (align = True, percentage = 0.7)            
            split.prop          (context.scene, 'shift_tt_factor_shininess')
            split.operator      ('object.texturetools_shininess_view_operator', '',     icon = 'FILE_IMAGE')

class FileNames (bpy.types.PropertyGroup):
    
    name = StringProperty (name='filepath', description='filepath', maxlen = 512, default='', subtype = 'FILE_NAME')
    
def register ():

    bpy.utils.register_module (__name__)

    # ----------------------------------------------------------    
    bpy.types.Scene.shift_tt_maskcomposite = StringProperty (
        name        = "",
        description = "File name with full path",
        default     = "",
        subtype     = 'FILE_PATH')

    # ----------------------------------------------------------    
    bpy.types.Scene.shift_tt_decompose = StringProperty (
        name        = "",
        description = "Destination path",
        default     = "",
        subtype     = 'DIR_PATH')
    
    # options
        
    # ----------------------------------------------------------
    bpy.types.Scene.shift_tt_mask1  = StringProperty (name = "", description = "Texture mask (file name with full path)", default = "", subtype = 'FILE_PATH')
    bpy.types.Scene.shift_tt_mask2  = StringProperty (name = "", description = "Texture mask (file name with full path)", default = "", subtype = 'FILE_PATH')
    bpy.types.Scene.shift_tt_mask3  = StringProperty (name = "", description = "Texture mask (file name with full path)", default = "", subtype = 'FILE_PATH')
    bpy.types.Scene.shift_tt_mask4  = StringProperty (name = "", description = "Texture mask (file name with full path)", default = "", subtype = 'FILE_PATH')
    bpy.types.Scene.shift_tt_mask5  = StringProperty (name = "", description = "Texture mask (file name with full path)", default = "", subtype = 'FILE_PATH')
    bpy.types.Scene.shift_tt_mask6  = StringProperty (name = "", description = "Texture mask (file name with full path)", default = "", subtype = 'FILE_PATH')
    bpy.types.Scene.shift_tt_mask7  = StringProperty (name = "", description = "Texture mask (file name with full path)", default = "", subtype = 'FILE_PATH')
    bpy.types.Scene.shift_tt_mask8  = StringProperty (name = "", description = "Texture mask (file name with full path)", default = "", subtype = 'FILE_PATH')
    bpy.types.Scene.shift_tt_mask9  = StringProperty (name = "", description = "Texture mask (file name with full path)", default = "", subtype = 'FILE_PATH')
    bpy.types.Scene.shift_tt_mask10 = StringProperty (name = "", description = "Texture mask (file name with full path)", default = "", subtype = 'FILE_PATH')
    bpy.types.Scene.shift_tt_mask11 = StringProperty (name = "", description = "Texture mask (file name with full path)", default = "", subtype = 'FILE_PATH')
    bpy.types.Scene.shift_tt_mask12 = StringProperty (name = "", description = "Texture mask (file name with full path)", default = "", subtype = 'FILE_PATH')
    bpy.types.Scene.shift_tt_mask13 = StringProperty (name = "", description = "Texture mask (file name with full path)", default = "", subtype = 'FILE_PATH')
    bpy.types.Scene.shift_tt_mask14 = StringProperty (name = "", description = "Texture mask (file name with full path)", default = "", subtype = 'FILE_PATH')
    bpy.types.Scene.shift_tt_mask15 = StringProperty (name = "", description = "Texture mask (file name with full path)", default = "", subtype = 'FILE_PATH')
    bpy.types.Scene.shift_tt_mask16 = StringProperty (name = "", description = "Texture mask (file name with full path)", default = "", subtype = 'FILE_PATH')

    # ----------------------------------------------------------    
    bpy.types.Scene.shift_tt_weightspath = StringProperty (
        name        = "",
        description = "File name with full path",
        default     = "",
        subtype     = 'FILE_PATH')
    
    # ----------------------------------------------------------    
    bpy.types.Scene.shift_tt_composite = StringProperty (
        name        = "",
        description = "File name and path",
        default     = "",
        subtype     = 'FILE_NAME')
    
    # ----------------------------------------------------------
    bpy.types.Scene.shift_tt_atlas2x2 = IntProperty (
        description = "Number of input textures for texture atlas (2x2)",
        min         = 1,
        max         = 4,
        step        = 1,
        default     = 1)
    bpy.types.Scene.shift_tt_atlas4x4 = IntProperty (
        description = "Number of input textures for texture atlas (4x4)",
        min         = 1,
        max         = 16,
        step        = 1,
        default     = 1)
    
    # ----------------------------------------------------------
    bpy.types.Scene.shift_tt_atlas_mode = EnumProperty(
        name="",
        description="Generate mode",
        items=[("0","Owner","Select mode"),
               ("A","No Atlas","Not generating texture atlas"),
               ("B","2x2 Atlas","Produce 2x2 texture atlas"),
               ("C","4x4 Atlas","Produce 4x4 texture atlas"),
              ],
        default='A')
        
    # ----------------------------------------------------------
    bpy.types.Scene.shift_tt_channel_red = EnumProperty(
        name="",
        description="Composite red channel is taken from ..",
        items=[("0","Red",""),
               ("A","Diffuse Red",""),
               ("B","Diffuse Green",""),
               ("C","Diffuse Blue",""),
               ("D","Normal Red",""),
               ("E","Normal Green",""),
               ("F","Normal Blue",""),
               ("G","Gloss Red",""),
               ("H","Gloss Green",""),
               ("I","Gloss Blue",""),
               ("J","Shininess Red",""),
               ("K","Shininess Green",""),
               ("L","Shininess Blue",""),
              ],
        default='A')
    bpy.types.Scene.shift_tt_channel_green = EnumProperty(
        name="",
        description="Composite green channel is taken from ..",
        items=[("0","Red",""),
               ("A","Diffuse Red",""),
               ("B","Diffuse Green",""),
               ("C","Diffuse Blue",""),
               ("D","Normal Red",""),
               ("E","Normal Green",""),
               ("F","Normal Blue",""),
               ("G","Gloss Red",""),
               ("H","Gloss Green",""),
               ("I","Gloss Blue",""),
               ("J","Shininess Red",""),
               ("K","Shininess Green",""),
               ("L","Shininess Blue",""),
              ],
        default='B')
    bpy.types.Scene.shift_tt_channel_blue = EnumProperty(
        name="",
        description="Composite blue channel is taken from ..",
        items=[("0","Red",""),
               ("A","Diffuse Red",""),
               ("B","Diffuse Green",""),
               ("C","Diffuse Blue",""),
               ("D","Normal Red",""),
               ("E","Normal Green",""),
               ("F","Normal Blue",""),
               ("G","Gloss Red",""),
               ("H","Gloss Green",""),
               ("I","Gloss Blue",""),
               ("J","Shininess Red",""),
               ("K","Shininess Green",""),
               ("L","Shininess Blue",""),
              ],
        default='C')
    bpy.types.Scene.shift_tt_channel_alpha = EnumProperty(
        name="",
        description="Composite alpha channel is taken from ..",
        items=[("0","Red",""),
               ("A","Diffuse Red",""),
               ("B","Diffuse Green",""),
               ("C","Diffuse Blue",""),
               ("D","Normal Red",""),
               ("E","Normal Green",""),
               ("F","Normal Blue",""),
               ("G","Gloss Red",""),
               ("H","Gloss Green",""),
               ("I","Gloss Blue",""),
               ("J","Shininess Red",""),
               ("K","Shininess Green",""),
               ("L","Shininess Blue",""),
               ("X","None",""),
              ],
        default='X')
    
    # ----------------------------------------------------------
    bpy.types.Scene.shift_tt_diffuse            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_normal             = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_gloss              = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_shininess          = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    
    # ----------------------------------------------------------
    bpy.types.Scene.shift_tt_factor_diffuse     = FloatProperty (name = "", description = "Diffuse map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_normal      = FloatProperty (name = "", description = "Normal map factor",    min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_gloss       = FloatProperty (name = "", description = "Gloss map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_shininess   = FloatProperty (name = "", description = "Shininess map factor", min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    
    # ----------------------------------------------------------
    bpy.types.Scene.shift_tt_diffuse1           = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_diffuse2           = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_diffuse3           = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_diffuse4           = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_diffuse5           = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_diffuse6           = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_diffuse7           = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_diffuse8           = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_diffuse9           = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_diffuse10          = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_diffuse11          = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_diffuse12          = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_diffuse13          = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_diffuse14          = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_diffuse15          = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_diffuse16          = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    
    bpy.types.Scene.shift_tt_normal1            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_normal2            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_normal3            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_normal4            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_normal5            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_normal6            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_normal7            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_normal8            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_normal9            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_normal10           = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_normal11           = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_normal12           = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_normal13           = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_normal14           = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_normal15           = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_normal16           = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
        
    bpy.types.Scene.shift_tt_gloss1             = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_gloss2             = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_gloss3             = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_gloss4             = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_gloss5             = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_gloss6             = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_gloss7             = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_gloss8             = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_gloss9             = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_gloss10            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_gloss11            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_gloss12            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_gloss13            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_gloss14            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_gloss15            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_gloss16            = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
        
    bpy.types.Scene.shift_tt_shininess1         = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_shininess2         = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_shininess3         = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')    
    bpy.types.Scene.shift_tt_shininess4         = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')    
    bpy.types.Scene.shift_tt_shininess5         = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')    
    bpy.types.Scene.shift_tt_shininess6         = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_shininess7         = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')    
    bpy.types.Scene.shift_tt_shininess8         = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')    
    bpy.types.Scene.shift_tt_shininess9         = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')    
    bpy.types.Scene.shift_tt_shininess10        = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_shininess11        = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')    
    bpy.types.Scene.shift_tt_shininess12        = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')    
    bpy.types.Scene.shift_tt_shininess13        = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')    
    bpy.types.Scene.shift_tt_shininess14        = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
    bpy.types.Scene.shift_tt_shininess15        = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')    
    bpy.types.Scene.shift_tt_shininess16        = StringProperty (name = "", description = "File name and path", default = "", subtype = 'FILE_NAME')
        
    # ----------------------------------------------------------
    bpy.types.Scene.shift_tt_factor_diffuse1    = FloatProperty (name = "", description = "Diffuse map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_diffuse2    = FloatProperty (name = "", description = "Diffuse map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_diffuse3    = FloatProperty (name = "", description = "Diffuse map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_diffuse4    = FloatProperty (name = "", description = "Diffuse map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_diffuse5    = FloatProperty (name = "", description = "Diffuse map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_diffuse6    = FloatProperty (name = "", description = "Diffuse map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_diffuse7    = FloatProperty (name = "", description = "Diffuse map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_diffuse8    = FloatProperty (name = "", description = "Diffuse map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_diffuse9    = FloatProperty (name = "", description = "Diffuse map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_diffuse10   = FloatProperty (name = "", description = "Diffuse map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_diffuse11   = FloatProperty (name = "", description = "Diffuse map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_diffuse12   = FloatProperty (name = "", description = "Diffuse map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_diffuse13   = FloatProperty (name = "", description = "Diffuse map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_diffuse14   = FloatProperty (name = "", description = "Diffuse map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_diffuse15   = FloatProperty (name = "", description = "Diffuse map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_diffuse16   = FloatProperty (name = "", description = "Diffuse map factor",     min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    
    bpy.types.Scene.shift_tt_factor_normal1     = FloatProperty (name = "", description = "Normal map factor",      min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_normal2     = FloatProperty (name = "", description = "Normal map factor",      min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_normal3     = FloatProperty (name = "", description = "Normal map factor",      min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_normal4     = FloatProperty (name = "", description = "Normal map factor",      min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_normal5     = FloatProperty (name = "", description = "Normal map factor",      min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_normal6     = FloatProperty (name = "", description = "Normal map factor",      min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_normal7     = FloatProperty (name = "", description = "Normal map factor",      min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_normal8     = FloatProperty (name = "", description = "Normal map factor",      min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_normal9     = FloatProperty (name = "", description = "Normal map factor",      min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_normal10    = FloatProperty (name = "", description = "Normal map factor",      min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_normal11    = FloatProperty (name = "", description = "Normal map factor",      min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_normal12    = FloatProperty (name = "", description = "Normal map factor",      min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_normal13    = FloatProperty (name = "", description = "Normal map factor",      min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_normal14    = FloatProperty (name = "", description = "Normal map factor",      min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_normal15    = FloatProperty (name = "", description = "Normal map factor",      min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_normal16    = FloatProperty (name = "", description = "Normal map factor",      min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    
    bpy.types.Scene.shift_tt_factor_gloss1      = FloatProperty (name = "", description = "Gloss map factor",       min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_gloss2      = FloatProperty (name = "", description = "Gloss map factor",       min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_gloss3      = FloatProperty (name = "", description = "Gloss map factor",       min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_gloss4      = FloatProperty (name = "", description = "Gloss map factor",       min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_gloss5      = FloatProperty (name = "", description = "Gloss map factor",       min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_gloss6      = FloatProperty (name = "", description = "Gloss map factor",       min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_gloss7      = FloatProperty (name = "", description = "Gloss map factor",       min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_gloss8      = FloatProperty (name = "", description = "Gloss map factor",       min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_gloss9      = FloatProperty (name = "", description = "Gloss map factor",       min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_gloss10     = FloatProperty (name = "", description = "Gloss map factor",       min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_gloss11     = FloatProperty (name = "", description = "Gloss map factor",       min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_gloss12     = FloatProperty (name = "", description = "Gloss map factor",       min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_gloss13     = FloatProperty (name = "", description = "Gloss map factor",       min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_gloss14     = FloatProperty (name = "", description = "Gloss map factor",       min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_gloss15     = FloatProperty (name = "", description = "Gloss map factor",       min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_gloss16     = FloatProperty (name = "", description = "Gloss map factor",       min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    
    bpy.types.Scene.shift_tt_factor_shininess1  = FloatProperty (name = "", description = "Shininess map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_shininess2  = FloatProperty (name = "", description = "Shininess map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_shininess3  = FloatProperty (name = "", description = "Shininess map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_shininess4  = FloatProperty (name = "", description = "Shininess map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_shininess5  = FloatProperty (name = "", description = "Shininess map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_shininess6  = FloatProperty (name = "", description = "Shininess map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_shininess7  = FloatProperty (name = "", description = "Shininess map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_shininess8  = FloatProperty (name = "", description = "Shininess map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_shininess9  = FloatProperty (name = "", description = "Shininess map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_shininess10 = FloatProperty (name = "", description = "Shininess map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_shininess11 = FloatProperty (name = "", description = "Shininess map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_shininess12 = FloatProperty (name = "", description = "Shininess map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_shininess13 = FloatProperty (name = "", description = "Shininess map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_shininess14 = FloatProperty (name = "", description = "Shininess map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_shininess15 = FloatProperty (name = "", description = "Shininess map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)
    bpy.types.Scene.shift_tt_factor_shininess16 = FloatProperty (name = "", description = "Shininess map factor",   min = 0.0, max = 1.0, precision = 3, step = 0.1, subtype = 'FACTOR', default = 1.0)

    # ----------------------------------------------------------
    bpy.types.Scene.shift_tt_history_composite  = CollectionProperty (
        type        = FileNames,
        name        = 'History',
        description = 'Composite file name history')
    bpy.types.Scene.shift_tt_history_diffuse    = CollectionProperty (
        type        = FileNames,
        name        = 'History',
        description = 'Diffuse map file name history')
    bpy.types.Scene.shift_tt_history_normal     = CollectionProperty (
        type        = FileNames,
        name        = 'History',
        description = 'Normal map file name history')
    bpy.types.Scene.shift_tt_history_gloss      = CollectionProperty (
        type        = FileNames,
        name        = 'History',
        description = 'Gloss map file name history')
    bpy.types.Scene.shift_tt_history_shininess  = CollectionProperty (
        type        = FileNames,
        name        = 'History',
        description = 'Shininess map file name history')
    
def unregister ():

    bpy.utils.unregister_module (__name__)
     
if __name__ == "__main__":
    
    register ()
