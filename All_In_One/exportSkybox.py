##########################################################################
#
#  Quick and dirty addon, exports Scene to Urho3D-friendly Skybox images.
#  based on Blender's operator_file_export.py example.
#
#  Copyright (c) 2017 Alex Piola
#
#  Portions: Copyright (c) https://www.blender.org 
#            ( see https://www.blender.org/about/license/ )
#
# License
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##########################################################################

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty, FloatProperty

bl_info = {
    "name": "Export Skybox",
    "description": "Export skybox-ready images of a scene",
    "author": "Alex Piola",
    "version": (0, 2),
    "blender": (2, 78, 0),
    "location": "File -> Export",
    "warning": "Might contain bugs, use at your own risk",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

def createCamera(camName):
    cam = bpy.data.cameras.new("cam")
    camObj = bpy.data.objects.new(camName,cam)
    bpy.context.scene.objects.link(camObj)
    return camObj

def deleteCamera(camNode):
    bpy.ops.object.select_all(action='DESELECT')
    camNode.select = True
    bpy.ops.object.delete()

def run(context, filepath, resolution, focusDist, clipStart, clipEnd):
    
    if bpy.context.mode != 'OBJECT':
       bpy.ops.set_mode('OBJECT')
    
    front = createCamera("front")
    front.rotation_euler = [1.57079,0.0,0.0]
    back = createCamera("back")
    back.rotation_euler = [1.57079,0.0,3.141592]

    right = createCamera("right")
    right.rotation_euler = [1.57079,0.0,-1.57079]
    left = createCamera("left")
    left.rotation_euler = [1.57079,0.0,1.57079]
    
    top = createCamera("top")
    top.rotation_euler = [3.141592,0.0,0.0]
    bottom = createCamera("bottom")
    bottom.rotation_euler = [0.0,0.0,0.0]
    
    cameras = [front,back,left,right,top,bottom]
    
    for cam in cameras:
        print(cam.data.angle)
        cam.data.angle = 1.5708
        cam.data.dof_distance = focusDist
        cam.data.clip_end = clipEnd
        cam.data.clip_start = clipStart
    
    prevY = context.scene.render.resolution_y
    prevX = context.scene.render.resolution_x
    prevPerc = context.scene.render.resolution_percentage
    prevPath = context.scene.render.filepath
    prevUseNodes = context.scene.use_nodes
    
    context.scene.render.resolution_y = resolution
    context.scene.render.resolution_x = resolution
    context.scene.render.resolution_percentage = 100
    context.scene.use_nodes = True
    
    path = filepath.split(".")

    #Workaround for sky blend bug when looking up
    world = bpy.data.worlds[0]
    horizonColor = world.horizon_color
    
    for cam in cameras:
       context.scene.camera = cam
       if cam.name == "top":
          world.horizon_color = world.zenith_color;
       else:
          world.horizon_color = horizonColor;
       context.scene.render.filepath = path[0]+"_"+cam.name+"."+path[1]
       context.scene.render.use_compositing = True
       bpy.ops.render.render(write_still=True)
       deleteCamera(cam)

    context.scene.render.resolution_y = prevY
    context.scene.render.resolution_x = prevX
    context.scene.render.resolution_percentage = prevPerc
    context.scene.render.filepath = prevPath
    context.scene.use_nodes = prevUseNodes
    
    return {'FINISHED'}


class ExportSkybox(Operator, ExportHelper):
    """Exports the scene as skybox images while using Compositing nodes too."""
    bl_idname = "export_skybox.data"
    bl_label = "Export Skybox Images"

    filename_ext = ".png"

    filter_glob = StringProperty(
            default="*.png",
            options={'HIDDEN'},
            maxlen=255,
            )

    resolution = IntProperty(
            name="Resolution",
            description="Resolution for the images",
            min=16,max=16384,
            default=1024,
            )

    focusDist = FloatProperty(
            name="Focal Distance",
            description="Distance for the focus point for DOF",
            min=0.0000,
            default=0.0,
            )

    clipStart = FloatProperty(
            name="Clip Start",
            description="Camera clip start distance",
            min=0.0000,
            default=0.100,
            )

    clipEnd = FloatProperty(
            name="Clip End",
            description="Camera clip end distance",
            min=0.0000,
            default=100.0,
            )

    def execute(self, context):
        return run(context, self.filepath, self.resolution, self.focusDist, self.clipStart, self.clipEnd)


def menu_func_export(self, context):
    self.layout.operator(ExportSkybox.bl_idname, text="Export Skybox")


def register():
    bpy.utils.register_class(ExportSkybox)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSkybox)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

