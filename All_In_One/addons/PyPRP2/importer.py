#    This file is part of PyPRP2.
#    
#    Copyright (C) 2010 PyPRP2 Project Team
#    See the file AUTHORS for more info about the team.
#    
#    PyPRP2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    PyPRP2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with PyPRP2.  If not, see <http://www.gnu.org/licenses/>.


import bpy
import mathutils
import os
from PyHSPlasma import *
from bpy.props import *


boneinclusion = ["handle","BookHandle","Convergence"]

class BoneIntermediate:
    def __init__(self):
        self.matrix = None
        self.parent = None

class PlasmaImport(bpy.types.Operator):
    bl_idname = "import.plasmaimport"
    bl_label = "Plasma Import"
    type = EnumProperty(items=(
                                  ("arm_f", "Female Armature", ""),
                                  ("arm_m", "Male Armature", "")
                              ),
                              name="Import Type",
                              description="Import Type")
    def execute(self, context):
        cfg = PlasmaConfigParser()
        importpath = cfg.get('Paths', 'importpath')
        if self.properties.type == "arm_f":
            importAvatarArmatureSystem(os.path.join(importpath,"GlobalAvatars_District_Female.prp"))
        elif self.properties.type == "arm_m":
            importAvatarArmatureSystem(os.path.join(importpath,"GlobalAvatars_District_Male.prp"))
        return {'FINISHED'}

def is_armature_bone(name):
    return (name.startswith("Bone") or name in boneinclusion) #nasty starts with "Bone" hack

def importAvatarArmatureSystem(path):
    bones = {}
    bpy.ops.object.armature_add()
    blArm_obj = bpy.context.scene.objects.active
    blArm_obj.name = "PlasmaArmature"
    blArm = blArm_obj.data
    blArm.name = "PlasmaArmature"
    bpy.ops.object.mode_set(mode='EDIT')

    #clear out the default bone
    blArm.edit_bones.remove(blArm.edit_bones[0])

    #read the prp file
    rm = plResManager()
    page = rm.ReadPage(path)
    node = rm.getSceneNode(page.location)
    for key in node.sceneObjects:
        sobj = key.object
        if sobj.coord.object and is_armature_bone(key.name): 
            ci = sobj.coord.object
            if not key.name in bones.keys():
                bones[key.name] = BoneIntermediate()
            bones[key.name].matrix = ci.localToWorld.mat
            for child in ci.children:
                if is_armature_bone(child.name): #only add children who are part of the armature
                    if child.name not in bones.keys():
                        bones[child.name] = BoneIntermediate()
                    bones[child.name].parent = key.name
    #by the end of all the hard to read code we should have a dict full of filled BoneIntermediate instances

    #actually create the bones now
    print(bones)
    for name in bones.keys():
        blArm.edit_bones.new(name)
    #now fill in the info
    for name in bones.keys():
        print("Processing",name)
        bone = bones[name]
        blbone = blArm.edit_bones[name]
        blbone.tail = mathutils.Vector((bone.matrix[0][3],bone.matrix[1][3],bone.matrix[2][3]))
        #head connects to tail of parent
        if bone.parent:
            blbone.use_connect = True
            blbone.head = mathutils.Vector((bones[bone.parent].matrix[0][3],bones[bone.parent].matrix[1][3],bones[bone.parent].matrix[2][3]))
            blbone.parent = blArm.edit_bones[bone.parent]
        else:
            blbone.head = blbone.tail
    bpy.ops.object.mode_set(mode='OBJECT')

def register():
    bpy.utils.register_class(PlasmaImport)

def unregister():
    bpy.utils.unregister_class(PlasmaImport)
