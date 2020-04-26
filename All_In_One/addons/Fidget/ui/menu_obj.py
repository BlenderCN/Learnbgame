import bpy
from bpy.props import *

operators_object = [
    ("SCALE", "", ""),
    ("ROTATE", "", ""),
    ("TRANSFORM", "", ""),
    ("TRANSFORM_X", "", ""),
    ("TRANSFORM_Y", "", ""),
    ("TRANSFORM_Z", "", ""),
    ("TRANSFORM_N", "", "")]


class FidgetMenuOperatorObject(bpy.types.Operator):
    bl_idname = "fidget.operator_object"
    bl_label = "Fidget Menu Object Operator"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "execute menu operator"

    operator_types = EnumProperty(name="Operator Types", default={'TRANSFORM'},
                                  options={"ENUM_FLAG"}, items=operators_object)

    def execute(self, context):

        if {"TRANSFORM"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Transform'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.transform.translate('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"TRANSFORM_X"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Transform x'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=(True, False, False))\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"TRANSFORM_Y"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Transform y'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=(False, True, False))\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"TRANSFORM_Z"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Transform z'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.transform.translate('INVOKE_DEFAULT', constraint_axis=(False, False, True))\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"SCALE"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Scale'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.transform.resize('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"ROTATE"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Rotate'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.transform.rotate('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        return {'FINISHED'}


class FidgetCustomObjectMenu(bpy.types.Menu):
    bl_idname = "fidget.custom_object_menu"
    bl_label = "Object"

    def draw(self, context):
        layout = self.layout
        layout.operator("fidget.operator_object", "Transform").operator_types = {"TRANSFORM"}
        layout.operator("fidget.operator_object", "Transform x").operator_types = {"TRANSFORM_X"}
        layout.operator("fidget.operator_object", "Transform y").operator_types = {"TRANSFORM_Y"}
        layout.operator("fidget.operator_object", "Transform z").operator_types = {"TRANSFORM_Z"}
        layout.separator()
        layout.operator("fidget.operator_object", "Scale").operator_types = {"SCALE"}
        layout.operator("fidget.operator_object", "Rotate").operator_types = {"ROTATE"}
