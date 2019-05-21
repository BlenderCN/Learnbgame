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

import bpy
import os
import sys

from . import fbx
from . import fbx_token
from . import fbx_data
from . import fbx_mesh
from . import fbx_armature
from . import fbx_material
from . import fbx_object
from . import fbx_scene
          

def importFbxFile(context, filepath, scale):
    fbx.settings.scale = scale
    fbx.setCsysChangers()
    fbx.activeFolder = os.path.dirname(filepath)
    fbx.message('Import "%s"' % filepath)
    proot = fbx_token.tokenizeFbxFile(filepath)
    fbx.message("  File tokenized")
    fbx_data.parseNodes(proot)    
    fbx.message("  Tree parsed")
    fbx_data.buildObjects(context)          
    fbx.message('File "%s" imported' % filepath)
    

