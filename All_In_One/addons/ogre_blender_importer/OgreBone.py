
try:
    import bpy;
    import mathutils;
except ImportError:
    print("This file need to be run with blender");


class OgreBone:
    """
    A bone in a skeleton.
    @remarks
        See Skeleton for more information about the principles behind skeletal animation.
        This class is a node in the joint hierarchy. Mesh vertices also have assignments
        to bones to define how they move in relation to the skeleton.
    """
    def __init__(self, name, handle, creator, blender_bone, bone_map):
        self.name = name;
        self.handle = handle;
        self.creator = creator;
        self.local_position = mathutils.Vector((0.0,0.0,0.0));
        self.local_rotation = mathutils.Quaternion((1.0,0.0,0.0,0.0));
        self.local_scale = mathutils.Vector((1.0,1.0,1.0));
        self.rotation = self.local_rotation;
        self.blender_bone = blender_bone;
        self.bone_map = bone_map;
        self.childs = [];
        self.parent = None;

        self.blender_bone.use_inherit_rotation = True;
        self.blender_bone.use_inherit_scale = True;
        self.blender_bone.use_local_location = True;

        self.blender_bone.head = mathutils.Vector((0.0,0.0,0.0));
        self.blender_bone.tail = self.local_position;


    def computeBlenderBone(self):
        if (self.parent is not None):
            self.parent.computeBlenderBone();
            self.rotation = self.parent.rotation * self.parent.local_rotation;
            self.blender_bone.head = self.parent.blender_bone.tail;
            self.blender_bone.tail = self.rotation * self.local_position + self.blender_bone.head;

    def addChild(self, child):
        assert(child.parent is None);
        child.parent = self;
        child.blender_bone.parent = self.blender_bone;
        child.blender_bone.use_connect = True;
        self.childs.append(child);
        child.computeBlenderBone();
