#
# Automatically add top of the head to bones to a Manuel Bastioni Lab 1.5.0 Character.
#
#
# Fabrizio Nunnari <fab.nunnari@gmail.com>
#
# Usage:
# - Create a fresh new MBLab character
# - Be sure you are in object mode
# - Select the mesh (child of the armature)
# - Run the script
#
# The script will not create bones  if they are already there.
# Prevents messing up in case of accidental re-run ;-)


import bpy
from mathutils import Vector


# Check if the selected object os a MESH
mesh_obj = bpy.context.active_object
assert mesh_obj.type == 'MESH'

arm_obj = mesh_obj.parent
assert arm_obj.type == 'ARMATURE'

arm = arm_obj.data
assert isinstance(arm, bpy.types.Armature)

bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.scene.objects.active = arm_obj

# Create the bone
bpy.ops.object.mode_set(mode='EDIT')  # switches to armature-edit
if 'head_top' not in arm.edit_bones:
    # add single bone (Shift-A)
    head_top = arm.edit_bones.new('head_top')
    # set bone.parent to 'neck'
    head_top.parent = arm.edit_bones['head']
    # set bone.head to the eye center
    head_top.head = Vector(arm.edit_bones['head'].tail)
    head_top.tail = Vector(head_top.head) + Vector((0,0, 0.01))

bpy.ops.object.mode_set(mode='OBJECT')







