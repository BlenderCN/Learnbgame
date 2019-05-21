#
# Automatically add eye bones to a Manuel Bastioni Lab 1.5.0 Character.
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
# The script will not create bones or vertex groups if they are already there.
# Prevents messing up in case of accidental re-run ;-)
#
# TODO:
# - vertex selection is messy. Requires many edit mode switches.
#   Alternative solution, to investigate:
#   https://blender.stackexchange.com/questions/23113/select-vertices-of-mesh-in-python

import bpy
from mathutils import Vector

from typing import List

from yallah import mblab_tools

EYE_NAME_R = 'eye_R'
EYE_NAME_L = 'eye_L'
EYES_PARENT_NAME = 'head'

# To discover the ids of the eye vertices, select the vertices in MESH mode,
# go back to object mdde and then run this small script
# mesh = mesh_obj.data
#
# for v in mesh.vertices:
#     if v.select:
#         print(v.index)


# EYE_PUPIL_CENTER_VERTEX_ID_R = 6941
# EYE_BALL_CENTER_VERTEX_ID_R = 6670
# EYE_PUPIL_CENTER_VERTEX_ID_L = 593
# EYE_BALL_CENTER_VERTEX_ID_L = 322

# For each character mesh type, we list the indices of the vertices to select when calculating the center of the eyes.
# There are normally two indices: pupil center and eye-ball center
# Indices updated for MBLab 1.6.1a
FEMALE_LEFT_EYE_INDICES = [593, 322]
FEMALE_RIGHT_EYE_INDICES = [6941, 6670]

MALE_LEFT_EYE_INDICES = [1214, 943]
MALE_RIGHT_EYE_INDICES = [7166, 6895]


# Check if the selected object os a MESH
mesh_obj = bpy.context.active_object
assert mesh_obj.type == 'MESH'

arm_obj = mesh_obj.parent
assert arm_obj.type == 'ARMATURE'

arm = arm_obj.data
assert isinstance(arm, bpy.types.Armature)


def compute_center(vertices: List[bpy.types.MeshVertex]) -> Vector:
    # TODO -- Weird!!! I need to re-import the Vector here, otherwise it is unknown!
    from mathutils import Vector

    n_vertices = len(vertices)
    accu = Vector((0, 0, 0))
    for v in vertices:
        accu += v.co  # Accumulates the sum

    return accu / n_vertices  # really compute the average


if mblab_tools.is_female(mesh_obj=mesh_obj):
    leye_indices = FEMALE_LEFT_EYE_INDICES
    reye_indices = FEMALE_RIGHT_EYE_INDICES
elif mblab_tools.is_male(mesh_obj=mesh_obj):
    leye_indices = MALE_LEFT_EYE_INDICES
    reye_indices = MALE_RIGHT_EYE_INDICES
else:
    raise Exception("Mesh type for object '{}' is not supported.".format(mesh_obj.name))


# For each of the two eyes: select the vertices and create a bone for them.
for eye_name, eye_vertex_ids in zip([EYE_NAME_L, EYE_NAME_R],
                                    [leye_indices, reye_indices]):

    print("Working on eye {}, vertex ids {}...".format(eye_name, eye_vertex_ids))

    # Select the MESH
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = mesh_obj

    # Deselect all vertices
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    # Select a vertex pertaining to the eye.
    #
    # We have to select/unselect vertices in OBJECT mode!!!
    # "The mesh object in python reflects the state of the mesh as it was, the last time it was in object-mode."
    # See: https://blenderartists.org/forum/showthread.php?207542-Selecting-a-face-through-the-API&highlight=ow%20do%20I%20select/deselect%20vertices/edges/faces%20with%20python
    for vtx_id in eye_vertex_ids:
        mesh_obj.data.vertices[vtx_id].select = True

    # Select all vertices of the eye
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_linked()
    bpy.ops.object.mode_set(mode='OBJECT')

    # Create a vertex group (if not there, yet)
    bpy.ops.object.mode_set(mode='EDIT')
    if not eye_name in mesh_obj.vertex_groups:
        bpy.ops.object.vertex_group_add()
        vertex_group = mesh_obj.vertex_groups.active
        # Name it
        vertex_group.name = eye_name
        # Assign vertices to this group
        bpy.ops.object.vertex_group_assign()

    # Computer the center of the eyes
    eye_center = compute_center([v for v in mesh_obj.data.vertices if v.select])
    print("eye {} center: {}".format(eye_name, eye_center))

    # Select ARMATURE
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = arm_obj

    # Create the bone
    bpy.ops.object.mode_set(mode='EDIT')  # switches to armature-edit
    if eye_name not in arm.edit_bones:
        # add single bone (Shift-A)
        eye_bone = arm.edit_bones.new(eye_name)
        # set bone.parent to 'neck'
        eye_bone.parent = arm.edit_bones[EYES_PARENT_NAME]
        # set bone.head to the eye center
        eye_bone.head = Vector(eye_center)
        eye_bone.tail = Vector(eye_center)
        # shift the bone.tail.y a bit forward, to the direction of gaze
        eye_bone.tail.y -= 0.025

# We are in edit mode. The last eye is still selected. Deselect it.
bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.scene.objects.active = mesh_obj
bpy.ops.object.mode_set(mode='EDIT')  # switches to mesh-edit
bpy.ops.mesh.select_all(action='DESELECT')
# Go back to Object mode.
bpy.ops.object.mode_set(mode='OBJECT')
