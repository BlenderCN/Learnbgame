import bpy
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        StringProperty,
        )

from bpy.types import (
        Operator,
        Panel,
        )

from bpy_extras.io_utils import (
        ImportHelper,
        )

import bmesh

from .exceptions import *

from .lib import (
        get_cork_filepath,
        validate_executable,
        )

from .cork import (
        slice_out,
        )


# ############################################################
# User Interface
# ############################################################

class CorkMeshSlicerPanel(Panel):
    bl_label = "Cork Mesh Slice"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Boolean'

    @staticmethod
    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.operator("view3d.cork_mesh_slicer", text="Union").method="UNION"
        col.operator("view3d.cork_mesh_slicer", text="Difference").method="DIFF"
        col.operator("view3d.cork_mesh_slicer", text="Intersect").method="INTERSECT"
        col.operator("view3d.cork_mesh_slicer", text="XOR").method="XOR"
        col.operator("view3d.cork_mesh_slicer", text="Resolve").method="RESOLVE"
        col.separator()
        col.operator("view3d.cork_mesh_slicer", text="", icon='QUESTION', emboss=False).show_help = True


# ############################################################
# Operators
# ############################################################

class CorkMeshSlicerOperator(Operator):
    """"""
    bl_idname = "view3d.cork_mesh_slicer"
    bl_label = "Mesh Slicer"
    bl_description = ""

    method = EnumProperty(
        description="",
        items=(("UNION", "Union", "A + B"),
               ("DIFF", "Difference", "A - B"),
               ("INTERSECT", "Intersection", "A n B"),
               ("XOR", "XOR", "A xor B"),
               ("RESOLVE", "Resolve", "Intersect and connect"),
               ),
        default="DIFF",
        options={'SKIP_SAVE'},
        )

    show_help = bpy.props.BoolProperty(
            name="Help",
            description="",
            default=False,
            options={'HIDDEN', 'SKIP_SAVE'},
            )

    _commands = {
            'UNION':'-union',
            'DIFF':'-diff',
            'INTERSECT':'-isct',
            'XOR':'-xor',
            'RESOLVE':'-resolve',
            }

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.select

    def exec(self, context):
        try:
            slice_out(context, self._cork, self._method, self._base, self._plane)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        if self.show_help:
            context.window_manager.popup_menu(self.help_draw, title='Help', icon='QUESTION')
            return {'CANCELLED'}

        cork = get_cork_filepath(context)

        try:
            validate_executable(cork)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        try:
            self.check_errors(context.selected_objects, self.method)
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        self._cork = cork
        self._plane = context.active_object
        self._base = context.selected_objects[0] if context.selected_objects[0] != self._plane else context.selected_objects[1]
        self._method = self._commands.get(self.method)

        return self.exec(context)

    def check_errors(self, objects, method):
        """"""
        if len(objects) != 2:
            raise NumberSelectionException

        for obj in objects:
            if obj.type != 'MESH':
                raise NonMeshSelectedException(obj)

    def help_draw(self, _self, context):
        layout = _self.layout
        col = layout.column()

        col.label(text="This operator works from the selected to the active objects")
        col.label(text="The active must be a single plane")

        col.separator()
        col.label(text="Union")
        col.label(text="Compute the Boolean union of in0 and in1, and output the result")

        col.separator()
        col.label(text="Difference")
        col.label(text="Compute the Boolean difference of in0 and in1, and output the result")

        col.separator()
        col.label(text="Intersect")
        col.label(text="Compute the Boolean intersection of in0 and in1, and output the result")

        col.separator()
        col.label(text="XOR")
        col.label(text="Compute the Boolean XOR of in0 and in1, and output the result")

        col.separator()
        col.label(text="Resolve")
        col.label(text="Intersect the two meshes in0 and in1, and output the connected mesh with those")
        col.label(text="intersections made explicit and connected")


# ############################################################
# Registration
# ############################################################

def register():
    # the order here determines the UI order
    bpy.utils.register_class(CorkMeshSlicerOperator)
    bpy.utils.register_class(CorkMeshSlicerPanel)


def unregister():
    bpy.utils.unregister_class(CorkMeshSlicerPanel)
    bpy.utils.unregister_class(CorkMeshSlicerOperator)

