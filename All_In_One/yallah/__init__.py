import bpy

import os


from yallah.vertex_utils import LoadVertexGroups
from yallah.vertex_utils import SaveVertexGroups

from yallah.mblab_tools import is_male
from yallah.mblab_tools import is_female
from yallah.mblab_tools import is_mblab_body
from yallah.mblab_tools import SetupMBLabCharacter

from yallah.mblab_tools import RemoveAnimationFromFingers
from yallah.mblab_tools import SetRelaxedPoseToFingers
from yallah.mblab_tools import ResetCharacterPose
from yallah.anim_utils import SetDummyUserToAllActions
from yallah.anim_utils import CreateAPoseAction



import yallah.shape_key_utils
import yallah.vertex_utils
import yallah.anim_utils


bl_info = {
    "name": "YALLAH (Yet Another Low-Level Avatar Handler)",
    "description": "Blender support scripts for the YALLAH project.",
    "author": "Fabrizio Nunnari",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Toolbar",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

# Package version in x.y.z string form.
YALLAH_VERSION = ".".join([str(n) for n in bl_info["version"]])

YALLAH_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
YALLAH_FEATURES_DIR = os.path.join(os.path.dirname(__file__), "features")


class YallahPanel(bpy.types.Panel):
    bl_label = "YALLAH"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    # bl_context = 'objectmode'
    bl_category = "Yallah"

    def draw(self, context):
        layout = self.layout

        obj = context.active_object

        #
        # NOTHING
        if obj is None:
            layout.label("Nothing active")

        #
        # MESH
        elif obj.type == 'MESH':
            if not is_mblab_body(mesh_obj=obj):
                layout.row().label("The MESH must be a _finalized_ MBLab character")
                return

            if is_female(mesh_obj=obj):
                layout.row().label("MBLab Female Character")
                clothes_mask_file = "ClothesMasks-F_CA01.json"
            elif is_male(mesh_obj=obj):
                layout.row().label("MBLab Male Character")
                clothes_mask_file = "ClothesMasks-M_CA01.json"
            else:
                layout.label("Not an MBLab supported phenotype (male or female)")
                return

            #
            # SETUP
            row = layout.row()
            box = row.box()
            box.label("Setup:")
            if obj.yallah_setup_done:
                box.label("Setup already performed.")
            else:
                box.operator(SetupMBLabCharacter.bl_idname, text="Setup a MBLab character")

            #
            # CLOTHES
            row = layout.row()
            box = row.box()
            box.label("Clothes:")
            # box.label(text="Load Clothes Vertex Groups")
            op = box.operator(LoadVertexGroups.bl_idname, text="Load Clothes Vertex Groups")
            op.vertex_groups_filename = os.path.join(YALLAH_DATA_DIR, clothes_mask_file)
            op.replace_existing = True

        #
        # ARMATURE
        elif obj.type == 'ARMATURE':

            row = layout.row()
            box = row.box()
            box.label("Animation:")
            box.operator(RemoveAnimationFromFingers.bl_idname, text="Remove Fingers Animation")
            box.operator(SetRelaxedPoseToFingers.bl_idname, text="Set Relaxed Fingers Keyframe")
            box.operator(ResetCharacterPose.bl_idname, text="Reset Character Pose")
            box.operator(SetDummyUserToAllActions.bl_idname)

        #
        # No ops
        else:
            layout.label("Please, select an MBLab armature or body.")


#
# (UN)REGISTER
#
def register():

    mblab_tools.register()
    shape_key_utils.register()
    vertex_utils.register()
    anim_utils.register()

    bpy.utils.register_class(YallahPanel)


def unregister():

    bpy.utils.unregister_class(YallahPanel)

    anim_utils.unregister()
    vertex_utils.unregister()
    shape_key_utils.unregister()
    mblab_tools.unregister()
