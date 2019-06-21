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

class View3DOperatorSide(bpy.types.Operator):
    """Translate the view using mouse events"""
    bl_idname = "view3d.view3d_side"
    bl_label = "Turn to Side View"

    offset = FloatVectorProperty(name="Offset", size=3)

    def execute(self, context):
        v3d = context.space_data
        rv3d = v3d.region_3d

        rv3d.view_rotation.rotate(Euler((0, 0, self.angle)))
        # rv3d.view_location = self._initial_location + Vector(self.offset)

    def modal(self, context, event):
        v3d = context.space_data
        rv3d = v3d.region_3d

        if event.type == 'MOUSEMOVE':
            self.angle = (self._pre_mouse[0] - event.mouse_region_x) * 0.002
            self.execute(context)
            self._pre_mouse = Vector((event.mouse_region_x, event.mouse_region_y, 0.0))
            # context.area.header_text_set("Offset %.4f %.4f %.4f" % tuple(self.offset))

        elif event.type == 'LEFTMOUSE':
            # context.area.header_text_set()
            return {'FINISHED'}

        # elif event.type in {'RIGHTMOUSE', 'ESC'}:
        #     rv3d.view_location = self._initial_location
        #     context.area.header_text_set()
        #     return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        if context.space_data.type == 'VIEW_3D':
            v3d = context.space_data
            rv3d = v3d.region_3d

            if rv3d.view_perspective == 'CAMERA':
                rv3d.view_perspective = 'PERSP'

            self._pre_mouse = Vector((event.mouse_region_x, event.mouse_region_y, 0.0))
            self._initial_location = rv3d.view_location.copy()

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}

class View3DOperatorCamera(bpy.types.Operator):
    bl_idname = "view3d.view3d_camera"
    bl_label = "Turn to Camera View"

    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            v3d = context.space_data
            rv3d = v3d.region_3d
            if rv3d.view_perspective == 'PERSP':
                rv3d.view_perspective = 'CAMERA'
            return {'FINISHED'}
