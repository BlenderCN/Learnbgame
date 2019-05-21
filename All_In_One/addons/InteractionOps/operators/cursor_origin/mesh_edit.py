import bpy
import blf
import math
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector, Matrix
from bpy.props import (IntProperty,
                       FloatProperty,
                       BoolProperty,
                       StringProperty,
                       FloatVectorProperty)
from mathutils import Vector, Matrix
from ..iops import IOPS


class IOPS_OT_CursorOrigin_Mesh_Edit(IOPS):
    bl_idname = "iops.cursor_origin_mesh_edit"
    bl_label ="MESH: Edit mode - Origin to selected"

    @classmethod
    def poll (self, context):
        return (context.area.type == "VIEW_3D" and
                context.mode == "EDIT_MESH")

    def execute(self, context):
        scene = bpy.context.scene
        objs = bpy.context.selected_objects
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        return{"FINISHED"}