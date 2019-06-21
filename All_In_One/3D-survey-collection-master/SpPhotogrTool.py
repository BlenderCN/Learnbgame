import bpy
import os
import time

from mathutils import Vector
from bpy_extras.io_utils import ImportHelper

from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       CollectionProperty
                       )

import bmesh
from random import randint, choice


class ToolsPanel100(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
#    bl_context = "objectmode"
    bl_category = "3DSC"
    bl_label = "Spherical Photogrammetry tool (alpha)"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        obj = context.object
        row = layout.row()
        row.label(text="Folder with the oriented 360 collection")
        row = layout.row()
        row.prop(context.scene, 'BL_oriented360_path', toggle = True)
        row = layout.row()
        row.label(text="Painting Toolbox", icon='TPAINT_HLT')
        row = layout.row()
        self.layout.operator("paint.cam", icon="IMAGE_COL", text='Paint selected from cam')


# define path to undistorted image

    bpy.types.Scene.BL_oriented360_path = StringProperty(
      name = "Oriented 360 Path",
      default = "",
      description = "Define the root path of the oriented 360 collection",
      subtype = 'DIR_PATH'
      )