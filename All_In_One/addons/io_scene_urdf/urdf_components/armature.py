import bpy, math
from mathutils import Vector, Matrix, Euler
import copy
from io_scene_urdf.urdf_components.joint import URDFJoint
from io_scene_urdf.urdf_components.link import URDFLink

# from morse.builder.urdf_components.joint import URDFJoint
# from morse.builder.urdf_components.link import URDFLink
class URDFArmature:

    def __init__(self, option = 'ROBOT'):


        self.name = urdf.name
        self.urdf = urdf
        self.links = []
        # Lists of joints, and their children
        self.joints = [] 
        self.root_link = None
        self.type = option
        # # Find all links and create a frame for each link  (no placement of link yet)
        # for link in self.urdf.links:
        #     self.links.append(URDFLink(link))
     

    
    def build(self):
        # Put the joints and links together
        ### Start with the base link, if there is multiple roots, do nothing
        try: 
            print('Establishing joints/links dependency...')
            self.root_link = URDFLink(self.urdf.link_map[self.urdf.get_root()])   
        except:
            print('Multiple roots detected, robot will not be built, exiting...')
            return 
        
        if self.type == 'ROBOT':
            self.root_link.set_physics('RIGID_BODY')
        else:
            self.root_link.set_physics('STATIC')
        
        temp_list = []
        temp_list.append(self.root_link) 
        self.links.append(self.root_link)
        while len(temp_list)>0:
            parent_link = temp_list[0]

            # If there is only 1 link 
            if parent_link.name in self.urdf.child_map:
                for (joint_name, child_link_name) in self.urdf.child_map[parent_link.name]:
                    
                    child_link = URDFLink(self.urdf.link_map[child_link_name])
                    self.link.append(child_link)
                    if child_link_name in self.urdf.child_map:
                        temp_list.append(child_link)
                    
                    # Call function to do parenting
                    urdf_joint = URDFJoint(self.urdf.joint_map[joint_name], self.urdf)
                    self.joints.append(urdf_joint)
                    urdf_joint.build(parent_link,child_link)
                temp_list.pop(0)
            else:
                temp_list.pop(0)

        # Create an armature at base link
        # bpy.ops.object.add(
        #     type='ARMATURE', 
        #     enter_editmode=True,
        #     location=(0,0,0))
        # ob = bpy.context.object
        # ob.show_x_ray = True
        # ob.name = self.name
        # armature = ob.data
        # armature.name = self.name+'_armature'
        # armature.show_axes = True

        # bpy.ops.object.mode_set(mode='EDIT')
        # Place frames and meshes at their origin

        # Create a bone

        # Find its child link

        # Place the link origin at the joint


    # def _walk_urdf(self, link, parent_joint = None):
    #     ''' Recursively build up bone structure starting from base link
    #     Input: parent_link, parent_bone
    #     Output: List of URDFJoints (bones) defined by the joint and its child_link
    #     (A bone is made up of a joint and its child_link)
    #     '''
    #     bones = []
    #     for joint in self._get_urdf_connections(link):
    #         if parent_joint:
    #             # be careful: if joint is a zero-length joint,
    #             # it gets merged into parent bone (because Blender does not
    #             # support 0-length joints)! so bone and parent_bone
    #             # may be equal.
    #             bone = parent_joint.add_child(joint, child_link)
    #         else:
    #             bone = URDFJoint(joint, child_link)

    #         self._walk_urdf(child_link, bone)
    #         bones.append(bone)
    #     return bones

    # def _get_urdf_connections(self, link):
    #     ''' Find joint and child link of the provided link
    #     Input: link <Type: URDFLink>
    #     Output: (joint, child_link) (<Type: URDFJoint>, <Type: URDFLink>)
    #     '''
    #     joint_list = []
    #     joints = [joint for joint in self.urdf.joints if joint.parent == link.name]
    #     for joint in joints:
    #         joint_list.append(URDFJoint(joint, self.urdf.link_map[joint.child]))
    #     return  joint_list 






