#add-on name = Bmh2
#id name = bmh.2
#category = Rigging
#author = ishidourou

####################################
# Bmh2(BoneModelingHelper2)
#       v.2.0
#  (c)ishidourou 2014
####################################

#!BPY
import bpy
from bpy.props import *

bl_info = {
    "name": "Bone Modelling Helper",
    "author": "ishidourou",
    "version": (1, 0),
    "blender": (2, 65, 0),
    "location": "View3D > Toolbar and View3D",
    "description": "Create an armature from the selected mesh",
    "wiki_url": "http://stonefield.cocolog-nifty.com/higurashi/2014/05/bone-modeling-h.html",
    "tracker_url": "http://stonefield.cocolog-nifty.com/higurashi/2014/05/bone-modeling-h.html",
    "category": "Learnbgame",
}

#    メッセージ（英語,日本語）
class mes():
    title = ('Bone Modeling Helper','ボーンモデリングヘルパー')
    btn01 = ('Create Bones from Selected Mesh','選択メッシュからボーンを作成')
    btn02 = ('Connect Selected Bones','選択ボーンを接続')

def lang():
    system = bpy.context.user_preferences.system
    if system.use_international_fonts:
        if system.language == 'ja_JP':
            return 1
    return 0


#    Menu in tools region
class Bmh2Panel(bpy.types.Panel):
    lng = lang()
    bl_category = "Tools"
    bl_label = mes.title[lng]
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        self.layout.operator("create.bones")
        self.layout.operator("connect.bones")

#---- main ------

def createArmature(loc,eindex,vpos):
    bpy.ops.object.add(type='ARMATURE',enter_editmode=True,location=loc)
    ob = bpy.context.object
    ob.show_x_ray = True
    amt = ob.data

    ct = 0
    for i in eindex:
        bone = amt.edit_bones.new('abone')
        bone.head = vpos[eindex[ct][0]]
        bone.tail = vpos[eindex[ct][1]]
        ct += 1
    bpy.ops.armature.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob

class CreateBones(bpy.types.Operator):
    lng = lang()
    bl_idname = "create.bones"
    bl_label = mes.btn01[lng]
    bl_options = {'REGISTER'}

    def execute(self, context):

        vtdat = []
        egdat = []
        pos = []
        cobj = bpy.context.object
        cloc = cobj.location
        mesh = cobj.data
        vts = mesh.vertices
        eds = mesh.edges

        bpy.ops.object.mode_set(mode='OBJECT')

        for i in vts:
            pos.append(i.co.x)
            pos.append(i.co.y)
            pos.append(i.co.z)
            vtdat.append(pos)
            pos = []

        for i in eds:
            if i.select:
                pos.append(i.vertices[0])
                pos.append(i.vertices[1])
                egdat.append(pos)
                pos = []

        createArmature(cloc,egdat,vtdat)

        return{'FINISHED'}


#---------- ConnectBones -------------

def connectbones():
    cobj = bpy.context.object
    amt = cobj.data
    bones = amt.edit_bones

    bpy.ops.object.mode_set(mode='EDIT')

    for i in bones:
        if i.select:
            for ii in bones:
                if i != ii:
                    if i.head == ii.tail:
                        i.parent = ii
                        i.use_connect = True

    return 1

class ConnectBones(bpy.types.Operator):
    lng = lang()
    bl_idname = "connect.bones"
    bl_label = mes.btn02[lng]
    bl_options = {'REGISTER'}

    def execute(self, context):
        connectbones()

        return{'FINISHED'}

#======== Registration ==========

def register():
    bpy.utils.register_class(Bmh2Panel)
    bpy.utils.register_class(CreateBones)
    bpy.utils.register_class(ConnectBones)

def unregister():
    bpy.utils.unregister_class(Bmh2Panel)
    bpy.utils.unregister_class(CreateBones)
    bpy.utils.unregister_class(ConnectBones)

if __name__ == "__main__":
    register()
