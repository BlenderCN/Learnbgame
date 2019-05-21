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

bl_info = {
    "name": "Export Camera Matrices",
    "author": "Marc-Stefan Cassola (maccesch)",
    "version": (1, 0),
    "blender": (2, 6, 0),
    "api": 41113,
    "location": "File > Export > Camera Matrices",
    "description": "Export the current camera's matrices as JSON",
    "warning": "",
    "wiki_url": "http://suedsicht.de",
    "tracker_url": "http://suedsicht.de",
    "category": "Import-Export",
}

import bpy
from bpy.props import BoolProperty
from bpy_extras.io_utils import ExportHelper
from mathutils import *
from math import *
import json

class ExportCamMats(bpy.types.Operator, ExportHelper):
    '''
    Exports the current camera's matrices P and MV as JSON.
    A given vector v = (x, y, z, 1.0) can be projected into normalized device coordinates:
        p = P * MV * v
        p /= v.w
    '''
    bl_idname = "export_camera_mats.json"
    bl_label = "Export Camera Matrices"

    filename_ext = ".json"
    

    @classmethod
    def poll(cls, context):
        return context.active_object.type == 'CAMERA'
    
    def execute(self, context):
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        P, MV = self.get_matrices(context)
        
        json_file = open(filepath, 'w')
        json.dump({
            'P': serialize_matrix(P),
            'MV': serialize_matrix(MV),
        }, json_file, indent=4)
        json_file.flush()
        json_file.close()
        
        return {'FINISHED'}
        
                
    def get_matrices(self, context):

        camobj = context.active_object
        cam = camobj.data
        
        if not type(cam) == bpy.types.Camera:
            raise "Selected object is not a camera"
            
        scn = context.scene
        w = scn.render.resolution_x*scn.render.resolution_percentage/100.0
        h = scn.render.resolution_y*scn.render.resolution_percentage/100.0
        ratio = w/h
        
        # Camera Projection Matrix
        tancam = 1.0/tan(cam.angle/2.0)
        P = Matrix((
            (-tancam,        0.0     ,  0.0,   0.0),
            (  0.0  , -tancam * ratio,  0.0,   0.0),
            (  0.0  ,        0.0     ,  1.0,  -1.0),
            (  0.0  ,        0.0     ,  0.0,   0.0),
        ))
                
        # Camera ModelView Matrix
        MV = camobj.matrix_world.inverted()
        
        switchM = Matrix((
            (-1.0, 0.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, -1.0, 0.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        ))
        
        MV = MV * switchM
    
        return (P, MV)
    

def serialize_matrix(M):
    return [item for sublist in M for item in sublist]
    

### REGISTER ###

def menu_func(self, context):
    self.layout.operator(ExportCamMats.bl_idname, text=bl_info['name'])


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_export.remove(menu_func)
    
if __name__ == "__main__":
    register()