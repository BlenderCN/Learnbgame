#############################################
# THPS4 SCENE (.scn/.mdl/skin) IMPORT
#############################################
import bpy
import bmesh
import struct
import mathutils
import math
import os, sys
from bpy.props import *
from . constants import *
from . helpers import *

# METHODS
#############################################
def read_skeleton(filepath, set_rotation=False):
    from mathutils import Vector, Quaternion, Matrix
    with open(filepath, "rb") as inp:
        r = Reader(inp.read())
    p = Printer()

    p("version: {}", r.i32())
    p("flags: {}", r.u32())
    num_bones = p("num bones: {}", r.i32())

    bpy.ops.object.armature_add()
    bpy.ops.object.editmode_toggle()

    armature = bpy.context.object
    eb = armature.data.edit_bones
    eb.remove(eb["Bone"])

    name_to_idx = {}
    bones = []
    for i in range(num_bones):
        bone_name = r.u32()
        name_to_idx[bone_name] = str(i)
        bone = eb.new(str(i))
        bones.append(bone)

    for bone in bones:
        parent_name = r.u32()
        if parent_name:
            bone.parent = eb[name_to_idx[parent_name]]
            # bone.use_connect = True

    for bone in bones:
        r.u32() # flip bone?

    mats = {}
    quats = []
    for bone in bones:
        print(bone.name)
        q = r.read("4f")  # xyzw
        quat = Quaternion((q[3], q[0], q[1], q[2]))  # wxyz
        # quat = Quaternion(q)
        quats.append(quat)
        vec = Vector(r.read("4f"))
        vec = Vector((vec[0], -vec[2], vec[1], vec[3]))

        if bone.parent:
            bone.parent.tail = bone.parent.head + vec.to_3d()
            bone.head = bone.parent.tail
            bone.tail = bone.parent.head
        else:
            bone.head = vec.to_3d()

        """
        if bone.parent:
            bone.head = bone.parent.tail
        bone.tail = bone.head + vec.to_3d()
        """

        """
        transMat = Matrix.Translation(vec)
        rotMat = quat.to_matrix().to_4x4()
        mat = rotMat * transMat.inverted()

        if bone.parent:
            mat *= mats[bone.parent]

        mats[bone] = mat
        bone.transform(mat)
        """

    bpy.ops.object.mode_set(mode="OBJECT")

    if set_rotation:
        pb = armature.pose.bones
        for quat, bone in zip(quats, bones):
            pbone = pb.get(bone.name)
            if pbone:
                pbone.rotation_quaternion = quat



# OPERATORS
#############################################
class THUGImportSkeleton(bpy.types.Operator):
    bl_idname = "io.import_thug_skeleton"
    bl_label = "THUG Skeleton (.ske.xbx)"
    # bl_options = {'REGISTER', 'UNDO'}

    filter_glob = StringProperty(default="*.ske.xbx", options={"HIDDEN"})
    filename = StringProperty(name="File Name")
    directory = StringProperty(name="Directory")
    set_rotation = BoolProperty(name="Set Rotation", default=False)

    def execute(self, context):
        import os
        filename = self.filename
        directory = self.directory

        read_skeleton(os.path.join(directory, filename))

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = bpy.context.window_manager
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"
