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
# Uso instrucciones: Exporta e importa camaras animadas en un formato muy facil de leer
# y ser re interpretado por cualquier software.
# Habilitar el addon y buscarlo en el search como Json Camera

bl_info = {
    "name": "Camera Json Exporter/Importer",
    "author": "Eugenio Pignataro Oscurart",
    "version": (1, 0),
    "blender": (2, 76, 0),
    "location": "Search > Export Json Camera",
    "description": "Import Export Camera in Json",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
    }




import bpy
import json
from math import degrees
from math import radians
from bpy_extras.io_utils import ImportHelper
from bpy_extras.io_utils import ExportHelper


def camExport(context, filepath):
    ob = bpy.context.object
    camdata = {}
    fs = bpy.context.scene.frame_start
    fe = bpy.context.scene.frame_end
    if ob.type == "CAMERA":
        camdata["name"] = ob.name
        camdata["draw_size"] = ob.data.draw_size
        camdata["location"] = {}
        camdata["rotation_euler"] = {}
        camdata["scale"] = {}
        camdata["lens"] = ob.data.lens
        camdata["sensor_width"] = ob.data.sensor_width
        camdata["sensor_height"] = ob.data.sensor_height
        camdata["shift_x"] = ob.data.shift_x
        camdata["shift_y"] = ob.data.shift_y
        # sequence
        for fr in range(fs,fe+1):
            bpy.context.scene.frame_set(fr)
            camdata["location"][fr] = (fr,ob.matrix_world.to_translation()[:])
            camdata["rotation_euler"][fr] = (fr,list(map(degrees,ob.matrix_world.to_euler()[:])))
            camdata["scale"][fr] = (fr,ob.matrix_world.to_scale()[:])
    else:
        print("Select Camera first") 
    #exporta    
    with open(filepath, "w") as file:
        json.dump(camdata, file, ensure_ascii=False) 
    return {'FINISHED'}

#importa -------------------------------------------   

def camImport(context, filepath):
    print(filepath)
    with open(filepath, "r") as file:
        ndata = json.load(file)        
    cam = bpy.data.cameras.new("camarita")
    object = bpy.data.objects.new("objetito",cam)
    bpy.context.scene.objects.link(object)
    #bake srt
    for frame in ndata['location']:
        bpy.context.scene.frame_set(int(frame))    
        object.location = ndata['location'][frame][1] 
        object.keyframe_insert("location", frame=int(frame))
        object.rotation_euler= list(map(radians,ndata['rotation_euler'][frame][1]))
        object.keyframe_insert("rotation_euler", frame=int(frame))   
        object.scale = ndata['scale'][frame][1] 
        object.keyframe_insert("scale", frame=int(frame))  
    #setcam especificaciones    
    object.name = ndata["name"]
    object.data.lens = ndata["lens"]   
    object.data.sensor_width = ndata["sensor_width"]   
    object.data.sensor_height = ndata["sensor_height"]
    object.data.shift_x = ndata["shift_x"]
    object.data.shift_y = ndata["shift_y"]
    object.data.draw_size = ndata["draw_size"]    
    return {'FINISHED'}

#clases ------------------------------------------------
class ExportSomeData(bpy.types.Operator, ExportHelper):
    bl_idname = "export_json.camera" 
    bl_label = "Export Json Camera"
    filename_ext = ".json"
    filter_glob = bpy.props.StringProperty(
            default="*.json",
            options={'HIDDEN'},
            )
    def execute(self, context):
        return camExport(context, self.filepath)

class ImportSomeData(bpy.types.Operator, ImportHelper):
    bl_idname = "import_json.camera" 
    bl_label = "Import Json Camera"
    filename_ext = ".json"
    filter_glob = bpy.props.StringProperty(
            default="*.json",
            options={'HIDDEN'},
            )
    def execute(self, context):
        return camImport(context, self.filepath)

def register():
    bpy.utils.register_module(__name__)
def unregister():
    bpy.utils.unregister_module(__name__)
if __name__ == "__main__":
    register()
