import bpy
from bpy.props import *


operators_bc = [
    ("SET_NGON", "", ""),
    ("SET_BOX", "", ""),
    ("SET_CIRCLE", "", ""),
    ("RED_BOX", "", ""),
    ("YELLOW_BOX", "", ""),
    ("PURPLE_BOX", "", ""),
    ("GRAY_BOX", "", ""),
    ("BLUE_BOX", "", "")]


class FidgetMenuOperatorBC(bpy.types.Operator):
    bl_idname = "fidget.operators_bc"
    bl_label = "Fidget Menu BC Operator"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "execute menu operator"

    operator_types = EnumProperty(name="Operator Types", default={'RED_BOX'},
                                  options={"ENUM_FLAG"}, items=operators_bc)

    def execute(self, context):

        if {"RED_BOX"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Red Box'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.boxcutter.invoke_operators('INVOKE_DEFAULT', mode='CUT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"YELLOW_BOX"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Yellow Box'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.boxcutter.invoke_operators('INVOKE_DEFAULT', mode='SLICE')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"PURPLE_BOX"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Purple Box'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.boxcutter.invoke_operators('INVOKE_DEFAULT', mode='PANEL')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"GRAY_BOX"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Gray Box'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.boxcutter.invoke_operators('INVOKE_DEFAULT', mode='MAKE')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"BLUE_BOX"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Blue Box'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.boxcutter.invoke_operators('INVOKE_DEFAULT', mode='KNIFE')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"SET_NGON"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Ngon Shape'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.boxcutter.set_ngon_shape()\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"SET_CIRCLE"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Circle Shape'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.boxcutter.set_circle_shape()\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"SET_BOX"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Box Shape'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.boxcutter.set_box_shape()\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        return {'FINISHED'}


class FidgetCustomBCMenu(bpy.types.Menu):
    bl_idname = "fidget.custom_bc_menu"
    bl_label = "BC"

    def draw(self, context):
        layout = self.layout
        layout.operator("fidget.operators_bc", "Red Box").operator_types = {"RED_BOX"}
        layout.operator("fidget.operators_bc", "Yellow Box").operator_types = {"YELLOW_BOX"}
        layout.operator("fidget.operators_bc", "Purple Box").operator_types = {"PURPLE_BOX"}
        layout.operator("fidget.operators_bc", "Gray Box").operator_types = {"GRAY_BOX"}
        layout.operator("fidget.operators_bc", "Blue Box").operator_types = {"BLUE_BOX"}
        layout.separator()
        layout.operator("fidget.operators_bc", "Box shape").operator_types = {"SET_BOX"}
        layout.operator("fidget.operators_bc", "Ngon shape").operator_types = {"SET_NGON"}
        layout.operator("fidget.operators_bc", "Circle shape").operator_types = {"SET_CIRCLE"}