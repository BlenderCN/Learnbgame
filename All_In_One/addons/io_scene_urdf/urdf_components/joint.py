import bpy, math
from mathutils import Vector, Matrix, Euler
import copy
from io_scene_urdf.urdf_components.link import URDFLink
# from morse.builder.urdf_components.link import URDFLink
class URDFJoint:

    # cf urdf_parser_py.urdf.Joint.TYPES
    FIXED = "fixed"
    PRISMATIC = "prismatic"
    REVOLUTE = "revolute"

    def __init__(self, urdf_joint, urdf):
        '''
        Initilize an instance of URDFJoint with 
            urdf_joint: joint data parsed from the .urdf file, type: list
            urdf: result from parsed URDF file
        '''
        self.urdf = urdf
        self.name = urdf_joint.name
        self.type = urdf_joint.type

        # If origin information is available
        if urdf_joint.origin:
            self.xyz = Vector(urdf_joint.origin.xyz)
            if urdf_joint.origin.rpy:
                self.rot = Euler(urdf_joint.origin.rpy, 'XYZ').to_quaternion()
            else:
                self.rot = Euler((0, 0, 0)).to_quaternion()
        else:
            self.xyz = Vector(0,0,0)
            self.rot = Euler((0, 0, 0)).to_quaternion()

        self.parent_link = None
        self.child_link = None
        self.parent_frame = None
        self.child_frame = None
        # self._add_parent(urdf_joint)
        # self._add_child(urdf_joint)
        # self.abs_xyz = None
   

 
        
        # print('Joint ' + self.name + ' has PARENT = ' + self.parent.name + ' and CHILD = ' +self.child.name)
        
    def _add_parent(self, urdf_joint):
        '''
        Find joint's parent link 
        '''
        if urdf_joint.parent:
            for link in self.urdf.links:            
                if link.name == urdf_joint.parent:
                    print('Found parent link of joint ' + self.name)
                    self.parent = self.urdf.link_map[urdf_joint.parent]
                else:
                    pass
        else:
            print('Invalid URDF file, joint ' + self.name + ' has no parent')
        if self.parent == None:
            print('Invalid URDF file, couldn not find link ' + link.name + ' that is parent of joint ' + self.name)
        
    def _add_child(self, urdf_joint):
        '''
        Find joint's child link 
        '''
        if urdf_joint.child:
            for link in self.urdf.links:
                if link.name == urdf_joint.child:
                    self.child = self.urdf.link_map[urdf_joint.child]
                    print('Found child link of joint ' + self.name)
                else:
                    pass
        else:
            print('Invalid URDF file, joint ' + self.name + ' has no child')
        if self.child == None:
            print('Invalid URDF file, couldn not find link ' + link.name + ' that is child of joint ' + self.name)

    def build(self, parent_link, child_link):

        # Get according Blender objects
        self.parent_link = parent_link
        self.child_link = child_link
        self.parent_frame = bpy.data.objects[parent_link.name]
        self.child_frame = bpy.data.objects[child_link.name]


        # Make parental relationship
        self.child_frame.parent = self.parent_frame

        # Transform child using joint origin
        self.child_frame.location = self.xyz
        self.child_frame.rotation_quaternion = self.rot

        if self.type == FIXED:
            self.child_link.set_physics('STATIC')
            
        else:
            self.child_link.set_physics('RIGID_BODY')

        

        


    def build_edit_bone(self, child_frame, parent_bone=None) :

        self.child_bone = armature.data.edit_bones.new(self.name + '_bone')
        if not parent_bone:
            self.child_bone.head = (0,0,0)
            self.child_bone.tail_local = self.child_frame.location
            self.child_bone.parent = None
            self.parent_bone = None
        else:
            self.parent_bone = parent_bone
            self.child_bone.parent = self.parent_bone
            self.child_bone.head = self.parent_bone.tail
            self.child_bone.tail_local = self.child_frame.location
            







    # def build_editmode(self, armature, parent = None):
    #     if not self.child:
    #         print("Processing %s as a static frame at the end of the armature. Do not create bone for it" % self.name)
    #         return

    #     print("Building %s..." % self.name)
    #     # Add new bone 
    #     self.editbone = armature.data.edit_bones.new(self.name)
    #     if parent:
    #         self.editbone.use_inherit_rotation = True
    #         self.editbone.parent = parent.editbone
    #         parent.editbone.tail = parent.editbone.head + parent.rot*self.xyz
        
    #     else:
    #         self.editbone.head = (0,0,0)
        

    #     IMPORTANT NOTE: double check the method of computing parent tail / children's head.
    #     Whether to use self.rot or parent.rot

    #     '''
        

    #     if parent: # If this is not the base joint
    #         self.editbone.use_inherit_rotation = True
    #         self.editbone.parent = parent.editbone

    #         if len(parent.children) == 1:

    #             # this joint is the only child of the parent joint: connect
    #             # them with parent's tail
    #             # parent.editbone.tail = self.rot * self.xyz + parent.editbone.head ???????????????????????????
    #             parent.editbone.tail = parent.rot * self.xyz + parent.editbone.head


    #             self.editbone.use_connect = True
    #         else:
    #             print('DEBUG:::::::Joint ' + self.name + ' has %d children', len(parent.children)    )
    #             # self.editbone.head = self.rot * self.xyz + parent.editbone.head  ??????????????????????????????????????????
    #             self.editbone.head = parent.rot * self.xyz + parent.editbone.head    
    #     else:
    #         self.editbone.head = (0, 0, 0)

    #     if self.subjoints:
    #         # if we have subjoints, we place the tail of the bone at the origin of the last joint's link.
    #         offset = self.subjoints[-1].link.xyz
    #     else:
    #         offset = self.link.xyz
        
    #     if offset == Vector((0,0,0)):
    #         #TODO: compute an offset based on the joint axis direction
    #         offset = parent.editbone.tail - parent.editbone.head
    #     self.editbone.tail = self.editbone.head + offset

    #     for child in self.children:
    #         child.build_editmode(armature, self)

    # def build_objectmode(self, armature, parent = None):

    #     if not self.children and self.type == self.FIXED:
    #         assert(parent)
    #         target = self.add_link_frame(armature, parent, self.xyz, self.rot)
            
    #         # Disabled generation of IK targets for now: would require one
    #         # armature per 'kinematic group' to work well (currently, it creates 
    #         # cycles
    #         #
    #         ## if the parent has only one such 'end frame', use it as IK target
    #         ## TODO: if more than one, select one randomly?
    #         #if len(parent.children) == 1:
    #         #    ik = parent.posebone.constraints.new("IK")
    #         #    ik.use_rotation = True
    #         #    ik.use_tail = True
    #         #    ik.target = target
    #         ####################################################################

    #         return

    #     self.posebone = armature.pose.bones[self.name]

    #     # Prevent moving or rotating bones that are not end-effectors (outside of IKs)
    #     if self.children:
    #         self.posebone.lock_location = (True, True, True)
    #         self.posebone.lock_rotation = (True, True, True)
    #         self.posebone.lock_scale = (True, True, True)

    #     # initially, lock the IK
    #     self.posebone.lock_ik_x = True
    #     self.posebone.lock_ik_y = True
    #     self.posebone.lock_ik_z = True


    #     if self.subjoints:
    #         print("Configuring multi-DoF joint %s" % self.name)
    #         for j in self.subjoints:
    #             j.configure_joint(self.posebone)
    #     else:
    #          self.configure_joint(self.posebone)

    #     self.add_link_frame(armature)

    #     for child in self.children:
    #         child.build_objectmode(armature, self)

    # def configure_joint(self, posebone):

    #     # First, configure joint axis
    #     if not self.axis:
    #         return

    #     print("Joint axis for <%s> (%s): %s" % (self.name, self.type, self.axis))


    #     # Then, IK limits
    #     if self.axis[0]:
    #         posebone.lock_ik_x = False
    #         posebone.use_ik_limit_x = True
    #         posebone.ik_max_x = self.limit.upper
    #         posebone.ik_min_x = self.limit.lower
    #     elif self.axis[1]:
    #         posebone.lock_ik_y = False
    #         posebone.use_ik_limit_y = True
    #         posebone.ik_max_y = self.limit.upper
    #         posebone.ik_min_y = self.limit.lower
    #     elif self.axis[2]:
    #         posebone.lock_ik_z = False
    #         posebone.use_ik_limit_z = True
    #         posebone.ik_max_z = self.limit.upper
    #         posebone.ik_min_z = self.limit.lower

    # def add_link_frame(self, armature, joint = None, xyz = None, rot = None):
    #     """
    #     :param joint: if the link has no proper bone (case for fixed joints at
    #     the end of an armature), we need to specify the joint we want to attach
    #     the link to (typically, the parent joint)
    #     """
    #     if not joint:
    #         joint = self

    #     bpy.ops.object.add(type = "EMPTY")

    #     #empty = bpymorse.get_first_selected_object()
    #     empty = bpy.context.selected_objects[0]
    #     empty.name = self.link.name

    #     empty.matrix_local = armature.data.bones[joint.name].matrix_local
    #     empty.scale = [0.01, 0.01, 0.01]

    #     if xyz and rot:
    #         empty.location += rot * xyz
    #     elif xyz:
    #         empty.location += xyz
    #     # parent the empty to the armature
    #     # !!!!!!!!!
    #     # armature.data.bones[joint.name].use_relative_parent = True
    #     empty.parent = armature
    #     empty.parent_bone = joint.name
    #     empty.parent_type = "BONE"

    #     # returns the empty that may be used as an IK target
    #     return empty
