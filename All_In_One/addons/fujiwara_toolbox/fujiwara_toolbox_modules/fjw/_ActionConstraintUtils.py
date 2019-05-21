import bpy
import sys
import inspect
import os.path
import os
import bmesh
import datetime
import math
import subprocess
import shutil
import time
import copy
import random
from collections import OrderedDict
from mathutils import *

from .main import *


class ActionConstraintUtils():
    def __init__(self, obj):
        self.armature = obj
        self.constraint_name = "ActionforConstraint"
        self.action_frame = 60

    def make_action(self):
        action = bpy.data.actions.new(self.constraint_name)
        self.armature.pose_library = action
        mode("POSE")
        bpy.ops.poselib.pose_add(frame=self.action_frame, name="EndPose")
        bpy.ops.pose.transforms_clear()
        bpy.ops.poselib.pose_add(frame=1, name="StartPose")
        bpy.ops.poselib.apply_pose(pose_index=1)
        return action

    def add_pose(self,frame,name):
        action = self.armature.pose_library
        mode("POSE")
        bpy.ops.poselib.pose_add(frame=frame, name=name)
        bpy.ops.pose.transforms_clear()

    def set_action_constraint(self, action):
        armu = ArmatureUtils(self.armature)
        active_pbone = armu.poseactive()

        for pbone in armu.pose_bones:
            if not armu.is_selected(pbone):
                continue
            if pbone.name == active_pbone.name:
                continue
            #コンストレイントを設定する
            constraint = pbone.constraints.new("ACTION")
            constraint.target = self.armature
            constraint.subtarget = active_pbone.name
            constraint.transform_channel = 'SCALE_Z'
            constraint.target_space = 'LOCAL_WITH_PARENT'
            constraint.min = 0.5
            constraint.max = 1
            constraint.frame_start = 60
            constraint.frame_end = 1
            constraint.action = action
        pass
    def auto_execute(self):
        action = self.make_action()
        self.set_action_constraint(action)
        pass

