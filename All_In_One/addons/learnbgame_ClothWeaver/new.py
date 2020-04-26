import bpy

import os
import webbrowser
from urllib import request
from bpy.types import Panel, Operator, EnumProperty, WindowManager, PropertyGroup

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       )
import bpy.utils.previews

def uvs(text):
    #bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    bpy.ops.mesh.select_all(action='DESELECT')
    #bpy.ops.object.editmode_toggle()
    return "--" + text + "--"
def markseams(text):
    bpy.ops.mesh.mark_seam()
    return "--" + text + "--"
def reflect(text):
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.resize(value=(-1, 1, 1), constraint_axis=(True, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.editmode_toggle()
    return "--" + text + "--"