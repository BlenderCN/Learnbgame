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

# <pep8 compliant>

bl_info = {
    "name": "Export Camera and Lights to Vue",
    "author": "Ruchir Shah", #based on Export Cameras & Markers export script by Campbell Barton
    "version": (0, 1),
    "blender": (2, 5, 6),
    "api": 34076,
    "location": "File > Export > Vue Camera and Lights Export",
    "description": "Export Blender Cameras and Lights to a Vue Python Script including animation",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}


import bpy
import mathutils
from mathutils import *
from math import *


def writeCameras(context, filepath, frame_start, frame_end, scaling_factor, only_selected=False):

    data_attrs = ['lens', 'shift_x', 'shift_y', 'dof_distance', 'clip_start', 'clip_end', 'draw_size']
    obj_attrs = ['hide_render']

    fw = open(filepath, 'w').write

    scene = bpy.context.scene

    objs = []

    for obj in scene.objects:
        if only_selected and not obj.select:
            continue
        if obj.type != 'CAMERA' and obj.type != 'LAMP':
            continue
        objs.append((obj, obj.data))         
        
        
    frame_range = range(frame_start, frame_end + 1)
    print("objs=",objs)
    
    print("scaling factor %s" % scaling_factor)

#set up scene
    fw("SetFrameRate(%d)\n" % scene.render.fps)
    fw("SetRenderOutput(VuePython.RO_Screen,'')\n")
    fw("SetPictureSize(%d,%d)\n" % (scene.render.resolution_x,scene.render.resolution_y))
    fw("\n")

    for obj, obj_data in objs:
        print(obj.name)
        fw("SetCurrentFrame(%d)\n" % frame_start)
        
#Basic camera attributes
        if obj.type == 'CAMERA':
            fw("# Camera = '%s'\n" % obj.name)
            fw("DeselectAll()\n")
            fw("camX=StoreCamera()\n")
            fw("SwitchCamera (camX)\n")
            fw("SelectByType(VuePython.VOT_Camera)\n")
            fw("cam = GetSelectedObjectByIndex(0)\n")
            fw("cam.SetName(\"%s\")\n" % obj.name)
            
            fw("thisobj=cam.ToCamera()\n")
            
            focal=obj_data.lens
            fw("thisobj.SetFocal(%s)\n" % focal)
            
#Basic lamp attributes
        if obj.type == 'LAMP':
            fw("# Lamp = '%s'\n" % obj.name)
            fw("DeselectAll()\n")
            fw("lampX=AddSpotLight()\n")
            fw("lampX.SetName(\"%s\")\n" % obj.name)
            
            col=obj_data.color
            fw("lampX.SetColor((%d, %d, %d))\n" % (col[0]*255,col[1]*255,col[2]*255))

            energy=obj_data.energy*50
            fw("lampX.SetPower(%d)\n" % energy)
            
            
            fw("thisobj=lampX\n")
               
#Frame based object settings
        for f in frame_range:
            scene.frame_set(f)
            

            posx=obj.location[0]*scaling_factor
            posy=obj.location[1]*scaling_factor
            posz=obj.location[2]*scaling_factor
            
            rotx=180-(obj.rotation_euler[0]*180/pi)
            roty=-1*(obj.rotation_euler[1]*180/pi)
            rotz=(obj.rotation_euler[2]*180/pi)-180
            
            fw("# new frame\n")
            fw("SetCurrentFrame(%d)\n" % f)
            fw("thisobj.SetRotationAngles(%s, %s, %s)\n" % (rotx,roty,rotz))
            fw("thisobj.SetPosition(%s, %s, %s)\n" % (posx,posy,posz))



        fw("#------------------\n\n")
#--------------------------     

from bpy.props import *
from bpy_extras.io_utils import ExportHelper


class CameraExporter(bpy.types.Operator, ExportHelper):
    '''Save a python script which exports camera to vue'''
    bl_idname = "export_animation.cameras"
    bl_label = "Export Camera and Lights to Vue"

    filename_ext = ".py"
    filter_glob = StringProperty(default="*.py", options={'HIDDEN'})

    scaling_factor = FloatProperty(name="Scaling factor",
            description="Multiply camera position by this factor",
            default=2, min=0.0001, max=100000)


    frame_start = IntProperty(name="Start Frame",
            description="Start frame for export",
            default=0, min=0, max=300000)
    frame_end = IntProperty(name="End Frame",
            description="End frame for export",
            default=250, min=1, max=300000)
    only_selected = BoolProperty(name="Only Selected",
            default=True)
            


    def execute(self, context):
        writeCameras(context, self.filepath, self.frame_start, self.frame_end, self.scaling_factor, self.only_selected)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end

        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_export(self, context):
    import os
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".py"
    self.layout.operator(CameraExporter.bl_idname, text="Vue Camera Export (.py)").filepath = default_path


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_export)


if __name__ == "__main__":
    register()