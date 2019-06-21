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
    "name": "Debug Pose",
    "author": "Thomas Larsson",
    "version": "0.1",
    "blender": (2, 6, 3),
    "api": 40000,
    "location": "View3D > Properties > Debug MH Pose",
    "description": "Debug pose for MakeHuman",
    "warning": "",
    'wiki_url': "http://www.makehuman.org/node/xxx",
    "category": "Learnbgame",
}
    

import bpy
import os
import math
from mathutils import *

D = math.pi/180

thePoseBoneFile = os.path.expanduser("~/documents/makehuman/posebones.txt")
thePosesFile = os.path.expanduser("~/documents/makehuman/poses_blender.txt")

def readBoneList(ob):
    fp = open(thePoseBoneFile, "rU")        
    readBones = []
    setBones = []
    for line in fp:
        words = line.split()
        if len(words) == 0:
            continue
        elif len(words) == 1:
            pb = ob.pose.bones[words[0]]
            readBones.append(pb)
        elif len(words) == 4:
            pb = ob.pose.bones[words[0]]
            coords = (float(words[1])*D, float(words[2])*D, float(words[3])*D)
            setBones.append((pb, coords))
            readBones.append(pb)
    fp.close()
    return readBones, setBones
    
        
def debugPose(context):    
    ob = bpy.context.object
    readBones, setBones = readBoneList(ob)    

    head = {}
    tail = {}
    roll = {}

    bpy.ops.object.mode_set(mode='EDIT')
    for eb in ob.data.edit_bones:
        head[eb.name] = eb.head.copy()
        tail[eb.name] = eb.tail.copy()
        roll[eb.name] = eb.roll
    bpy.ops.object.mode_set(mode='POSE')

    for pb, coords in setBones:
        euler = Euler((coords[0], coords[1], coords[2]), 'ZYX')
        loc,rot,scale = pb.matrix_basis.decompose()
        pb.matrix_basis = Matrix.Translation(loc) * euler.to_matrix().to_4x4()

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')

    fp = open(thePosesFile, "w")    
    for pb in readBones:
        b = pb.bone
        if pb.parent:
            pose = b.matrix_local.inverted() * b.parent.matrix_local * pb.parent.matrix.inverted() * pb.matrix
        else:
            pose = b.matrix_local.inverted() * pb.matrix

        fp.write("\n" +
            "%s, %s\n" % (pb.name, roll[pb.name]) +
            "Rest\n%s\n" % pb.bone.matrix_local +
            "Global\n%s\n" % pb.matrix +
            "Pose\n%s\n" % pose +
            "%s\n" % pose.to_euler('XYZ') +
            "%s\n" % pose.to_euler('ZYX')
            )
        #fp.write("Basis\n%s\n" % pb.matrix_basis)

    fp.close()

#
#   User interface
#

class MakeRigPanel(bpy.types.Panel):
    bl_label = "Debug MH Pose"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        scn = context.scene
        layout.label("Files:")
        layout.label(thePoseBoneFile)
        layout.label(thePosesFile)
        layout.operator("debug.pose")


class OBJECT_OT_DebugPoseButton(bpy.types.Operator):
    bl_idname = "debug.pose"
    bl_label = "Debug Pose"

    def execute(self, context):
        debugPose(context)
        return{'FINISHED'}    

#
#    Init and register
#

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

