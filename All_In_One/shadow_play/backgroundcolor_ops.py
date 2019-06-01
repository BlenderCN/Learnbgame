import os
import sys
import math
import mathutils
from mathutils import Vector, Matrix, Euler
import bpy
from bgl import *
import bpy.utils.previews
import bmesh
from rna_prop_ui import PropertyPanel
from bpy.app.handlers import persistent
from bpy.types import (Panel, Operator, PropertyGroup, UIList, Menu)
from bpy.props import (StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty, PointerProperty)
from bpy_extras.view3d_utils import region_2d_to_location_3d, region_2d_to_vector_3d
from bpy.props import FloatVectorProperty
from bpy.app.handlers import persistent

# depends on sklean
import numpy as np
import random
import copy
from numpy import linalg as LA
from sklearn.decomposition import PCA

class BackgroundColorOperatorInstert(bpy.types.Operator):
    bl_idname = "background_color.insert"
    bl_label = "Insert Background Color Animation"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        current_frame = context.scene.frame_current
        world = context.scene.world
        world.keyframe_insert(data_path='horizon_color', frame=current_frame)

        return {'FINISHED'}
