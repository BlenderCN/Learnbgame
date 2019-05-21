import logging; log = logging.getLogger(__name__)
import bmesh
import bpy
import bpy_extras
import struct
import math
from mathutils import Matrix, Vector

class SkeletonImporter:
    """Imports skeleton from FMDL."""

    def __init__(self, parent, fmdl):
        self.fmdl     = fmdl
        self.operator = parent.operator
        self.context  = parent.context


    def importSkeleton(self, fskl):
        """Import specified skeleton."""
        name = self.fmdl.name

        # This is completely stupid. We basically automate the UI
        # to create the bones manually.
        # There is a better way (which still involves the UI, but
        # less so), but it of course doesn't work. (The created
        # bones fail to actually exist.)
        bpy.context.scene.cursor_location = (0.0, 0.0, 0.0)

        # Create armature and object
        bpy.ops.object.add(
            type='ARMATURE',
            enter_editmode=True)

        armObj = bpy.context.object
        #armObj.show_x_ray = True
        armObj.name = name
        amt = armObj.data
        amt.name = name+'.Armature'
        #amt.show_axes  = True
        amt.layers[0]  = True
        amt.show_names = True

        bpy.ops.object.mode_set(mode='EDIT')
        boneObjs = {}
        for i, bone in enumerate(fskl.bones):
            boneObj = amt.edit_bones.new(bone.name)
            boneObjs[i] = boneObj
            #boneObj.use_relative_parent = True
            #boneObj.use_local_location = True
            xfrm = bone.computeTransform().transposed()
            # rotate to make Z the up axis
            boneObj.matrix = Matrix.Rotation(
                math.radians(90), 4, (1,0,0)) * xfrm

            if bone.parent:
                boneObj.parent = boneObjs[bone.parent_idx]
                boneObj.head   = boneObj.parent.tail
                boneObj.use_connect = True
            else:
                boneObj.head = (0,0,0)

        bpy.ops.object.mode_set(mode='OBJECT')
        return armObj
