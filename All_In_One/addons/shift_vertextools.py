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
    "name"              : "SHIFT - Vertex Tools",
    "author"            : "BBC",
    "version"           : (1,0),
    "blender"           : (2, 5, 3),
    "api"               : 31236,
    "category"          : "Mesh",
    "location"          : "Tool Shelf",
    "warning"           : '',
    "wiki_url"          : "",
    "tracker_url"       : "",
    "description"       : "Various vertex operations"}

import os
import bpy
import sys
import time
import math
import ctypes
import operator
import mathutils

from math       import *
from ctypes     import *
from bpy.props  import *

class VertexToolsInplodeOp (bpy.types.Operator):

    bl_idname       = "object.vertextools_inplode_operator"
    bl_label        = "SHIFT - Mesh Tools"
    bl_description  = "Implode selected vertices into their center"
    bl_register     = True
    bl_undo         = True

    @classmethod
    def poll (cls, context):
        
        return context.active_object
    
    def execute (self, context):

        obj = context.scene.objects.active

        if (obj and obj.type == 'MESH'):

            bpy.ops.object.editmode_toggle ()

            center = mathutils.Vector ((0.0, 0.0, 0.0));    c = 0
            for v in obj.data.vertices:
                if v.select:
                    center [0] += v.co [0]
                    center [1] += v.co [1]
                    center [2] += v.co [2]
                    c += 1

            if c > 0:
                center [0] /= c
                center [1] /= c
                center [2] /= c

                for v in obj.data.vertices:
                    if v.select:
                        v.co [0] = center [0]
                        v.co [1] = center [1]
                        v.co [2] = center [2]

            obj.data.update ()

            bpy.ops.object.editmode_toggle ()

        return {'FINISHED'}

class VertexToolsPanel (bpy.types.Panel):
     
    bl_idname   = "object.vertextools__panel"
    bl_label    = "SHIFT - Vertex Tools"
    bl_context  = "mesh_edit"
    bl_register = True
    bl_undo     = True

    bl_space_type   = 'VIEW_3D'
    bl_region_type  = 'TOOLS'

    def draw (self, context):
            
        layout = self.layout
        
        box = layout.box ()
        box.operator    ('object.vertextools_inplode_operator', 'Implode')
        
def register ():

    bpy.utils.register_module (__name__)

def unregister ():

    bpy.utils.unregister_module (__name__)
     
if __name__ == "__main__":
    
    register ()
