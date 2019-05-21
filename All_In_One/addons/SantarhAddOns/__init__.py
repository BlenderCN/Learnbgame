bl_info = {
    "name": "SantarhAddOns",
    "auther": "santarh",
    "category": "User"
}

import bpy
import os

from . import bone_constraints
from . import mirror_bone_constraints

def register():
    bpy.utils.register_class(bone_constraints.TheOthersBoneLocationConstraints)
    bpy.utils.register_class(mirror_bone_constraints.MirrorBoneConstraints)

def unregister():
    bpy.utils.unregister_class(bone_constraints.TheOthersBoneLocationConstraints)
    bpy.utils.register_class(mirror_bone_constraints.MirrorBoneConstraints)

if __name__ == "__main__":
    register()
