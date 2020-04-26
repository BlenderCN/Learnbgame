import bpy
from bpy.props import *


operators_edit = [
    ("EXTRUDE", "", ""),
    ("EXTRUDE_INDIVIDUAL", "", ""),
    ("SUBDIVIDE", "", ""),
    ("BEVEL", "", ""),
    ("INSET", "", ""),
    ("BRIDGE", "", ""),
    ("SelectModeEdge", "", ""),
    ("SelectModeFace", "", ""),
    ("SelectModeVert", "", ""),
    ("Shade_Smooth", "", ""),
    ("Shade_Flat", "", "")]


class FidgetMenuOperatorEdit(bpy.types.Operator):
    bl_idname = "fidget.operator_edit"
    bl_label = "Fidget Menu Edit Operator"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "execute menu operator"

    operator_types = EnumProperty(name="Operator Types", default={'EXTRUDE'},
                                  options={"ENUM_FLAG"}, items=operators_edit)

    def execute(self, context):

        if {"EXTRUDE"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Extrude'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.mesh.extrude_region_move('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"EXTRUDE_INDIVIDUAL"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Extrude Individual'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.mesh.extrude_faces_move('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"SUBDIVIDE"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Subdivide'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.mesh.subdivide()\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"Shade_Smooth"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Shade Smooth'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.mesh.faces_shade_smooth()\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"Shade_Flat"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Shade Flat'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.mesh.faces_shade_flat()\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"BRIDGE"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Bridge Loops'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.mesh.bridge_edge_loops()\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"INSET"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Inset'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.mesh.inset('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"BEVEL"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Bevel'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.mesh.bevel('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"SelectModeEdge"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Edge Mode'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.mesh.select_mode(type='EDGE')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"SelectModeFace"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Face Mode'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.mesh.select_mode(type='FACE')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"SelectModeVert"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Vert Mode'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.mesh.select_mode(type='VERT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        return {'FINISHED'}


class FidgetCustomEditMenu(bpy.types.Menu):
    bl_idname = "fidget.custom_edit_menu"
    bl_label = "Edit"

    def draw(self, context):
        layout = self.layout
        layout.operator("fidget.operator_edit", "Extrude").operator_types = {"EXTRUDE"}
        layout.operator("fidget.operator_edit", "Extrude individual").operator_types = {"EXTRUDE_INDIVIDUAL"}
        layout.operator("fidget.operator_edit", "Bevel").operator_types = {"BEVEL"}
        layout.operator("fidget.operator_edit", "Inset").operator_types = {"INSET"}
        layout.separator()
        layout.operator("fidget.operator_edit", "Shade Smooth").operator_types = {"Shade_Smooth"}
        layout.operator("fidget.operator_edit", "Shade Flat").operator_types = {"Shade_Flat"}
        layout.separator()
        layout.operator("fidget.operator_edit", "Subdivide").operator_types = {"SUBDIVIDE"}
        layout.operator("fidget.operator_edit", "Bridge Loops").operator_types = {"BRIDGE"}
        layout.separator()
        layout.operator("fidget.operator_edit", "Vert Mode").operator_types = {"SelectModeVert"}
        layout.operator("fidget.operator_edit", "Edge Mode").operator_types = {"SelectModeEdge"}
        layout.operator("fidget.operator_edit", "Face Mode").operator_types = {"SelectModeFace"}
