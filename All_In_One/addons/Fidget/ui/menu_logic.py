import bpy
from bpy.props import *

operators = [
    ("TRANSFORM", "", ""),
    ("TRANSFORM_X", "", ""),
    ("TRANSFORM_Y", "", ""),
    ("TRANSFORM_Z", "", ""),
    ("TRANSFORM_N", "", "")]


class FidgetMenuOperatorLogic(bpy.types.Operator):
    bl_idname = "fidget.operator_logic"
    bl_label = "Fidget Menu Logic Operator"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "logic menu operator"

    operator_types = EnumProperty(name="Operator Types", default={'TRANSFORM'},
                                  options={"ENUM_FLAG"}, items=operators)

    def execute(self, context):

        return {'FINISHED'}


class FidgetCustomLogicMenu(bpy.types.Menu):
    bl_idname = "fidget.custom_logic_menu"
    bl_label = "Logic"

    def draw(self, context):
        layout = self.layout
