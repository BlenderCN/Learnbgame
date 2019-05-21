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

class SketchOperatorCleanStrokes(bpy.types.Operator):
    bl_idname = 'sketch.cleanstrokes'
    bl_label = 'Cleaning strokes'
    bl_options = {'REGISTER','UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.scene.grease_pencil != None)

    def invoke(self, context, event):
        g = context.scene.grease_pencil
        for l in g.layers:
            if l.active_frame!=None:
                for s in l.active_frame.strokes:
                    l.active_frame.strokes.remove(s)
        return {'FINISHED'}
