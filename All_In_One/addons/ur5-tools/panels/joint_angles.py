import bpy
from math import degrees
import math
'''
Adds a panel to main 3D View screen that shows the angles of each joint
'''

'''
Calculates the orientation/angle of a given bone
In respect to global orientation or the motherbone in 3D

Returns a tuple the angles(radians) of rotation in 3 axis
'''
def _get_local_orientation(pose_bone):
    local_orientation = pose_bone.matrix_channel.to_euler()
 
    if pose_bone.parent is None:
        return (local_orientation.x, local_orientation.y, local_orientation.z)
    else:
        my_orientation = pose_bone.matrix_channel.copy()
        parent_orientation = pose_bone.parent.matrix_channel.copy()
 
        my_orientation.invert()
        orientation = (my_orientation * parent_orientation).to_euler()
 
    return (orientation.x, orientation.y, orientation.z)
 
'''
Calculates the angles of each joint

Returns the list of angles of the joints in radians
'''
def _get_joint_angles(context):
    arm = context.scene.objects['Armature']
    pose = arm.pose
    bones = pose.bones
    joint_names = ['Base','Shoulder','Elbow','Wrist1','Wrist2','Wrist3']
    #The axis of each bone corresponding to a joint
    axis_index = {
       'Base': 2,
       'Shoulder': 1,
       'Elbow': 1,
       'Wrist1': 1,
       'Wrist2': 2,
       'Wrist3': 1,
      }
    #Offset based on how each bone was created
    axis_correction = {
        'Base': (1, 0),
        'Shoulder': (-1, -math.pi/2),
        'Elbow': (-1, 0),
        'Wrist1': (-1, -math.pi/2),
        'Wrist2': (-1, 0),
        'Wrist3': (-1, 0),
      }
    joint_angles_by_name = {}
    for bone in bones:
        joint_angles_by_name[bone.name] = _get_local_orientation(bone)
 
    joint_angles = []
    for name in joint_names:
        bl_angle = joint_angles_by_name[name][axis_index[name]]
        direction, offset = axis_correction[name]
        joint_angle = direction * bl_angle + offset
        joint_angles.append(joint_angle)
 
    return joint_angles
 
 
'''
Panel to display the angles of each joint
Allows for easier humans to correct IK contraints
'''
class SimpleBoneAnglesPanel(bpy.types.Panel):
    bl_label = "Joint Angles"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
	joint_names = ['Base','Shoulder','Elbow','Wrist1','Wrist2','Wrist3']
	joint_angles = _get_joint_angles(bpy.context)
    def draw(self, context):
        SimpleBoneAnglesPanel.joint_angles = _get_joint_angles(context)
        row = self.layout.row()
        for z in range(len(SimpleBoneAnglesPanel.joint_angles)):
            row = self.layout.row()
            row.label(text = SimpleBoneAnglesPanel.joint_names[z] + ': {}'.format(degrees(SimpleBoneAnglesPanel.joint_angles[z])))


bpy.utils.register_class(SimpleBoneAnglesPanel)