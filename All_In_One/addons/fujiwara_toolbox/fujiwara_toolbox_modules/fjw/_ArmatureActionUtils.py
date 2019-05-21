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


class ArmatureActionUtils():
    def __init__(self, armature):
        self.armature = armature
        self.action = armature.pose_library
        return

    def new_action(self, name):
        action = bpy.data.actions.new(name)
        self.armature.pose_library = action
        self.action = self.armature.pose_library
        pass

    def get_action(self):
        self.action = self.armature.pose_library
        return self.action

    def set_action(self,name):
        #nameが現在のポーズに含まれていればそれを返す
        if self.action is not None:
            if name in self.action.name:
                return self.action

        #なければ作成する
        self.new_action(name)
        return self.action

    

    def get_poselist(self):
        if self.get_action() is None:
            return None
        return self.action.pose_markers

    def store_pose(self,frame,name):
        mode("POSE")
        bpy.ops.poselib.pose_add(frame=frame, name=name)
        pass

    def apply_pose(self, name):
        if name not in self.action.pose_markers:
            print("no pose found")
            return
        for index, pose in enumerate(self.action.pose_markers):
            if pose.name == name:
                bpy.ops.poselib.apply_pose(pose_index=index)
                break

    def delete_pose(self, name):
        if name in self.action.pose_markers:
            bpy.ops.poselib.pose_remove(pose=name)
        pass
