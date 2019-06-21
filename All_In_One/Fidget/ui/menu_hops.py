import bpy
from bpy.props import *


operators_hops = [
    ("slash", "", ""),
    ("adjust_bevel", "", ""),
    ("2d_bevel", "", ""),
    ("adjust_curve", "", ""),
    ("adjust_tthick", "", ""),
    ("complex_sharpen", "", ""),
    ("soft_sharpen", "", ""),
    ("finish_setup", "", ""),
    ("copy_merge", "", ""),
    ("remove_merge", "", ""),
    ("parent_merge", "", ""),
    ("simple_parent_merge", "", ""),
    ("bevel_weight", "", ""),
    ("bool_union", "", ""),
    ("bool_intersect", "", ""),
    ("bool_difference", "", "")]


class FidgetMenuOperatorHops(bpy.types.Operator):
    bl_idname = "fidget.operator_hops"
    bl_label = "Fidget Menu Hops Operator"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "execute menu operator"

    operator_types = EnumProperty(name="Operator Types", default={'slash'},
                                  options={"ENUM_FLAG"}, items=operators_hops)

    def execute(self, context):

        if {"slash"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Slash'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.hops.slash('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"adjust_bevel"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Adjust bevel'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.hops.adjust_bevel('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"2d_bevel"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'2d bevel'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.hops.2d_bevel('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"adjust_curve"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Adjust curve'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.hops.adjust_curve('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"adjust_tthick"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Adjust tthick'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.hops.adjust_tthick('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"complex_sharpen"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Complex sharpen'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.hops.complex_sharpen('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"soft_sharpen"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Soft sharpen'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.hops.soft_sharpen('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"finish_setup"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Finish merge'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.hops.finish_setup('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"copy_merge"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Copy merge'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.hops.copy_merge('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"remove_merge"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Remove merge'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.hops.remove_merge('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"parent_merge"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Parent merge'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.hops.parent_merge('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"simple_parent_merge"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Simple parent merge'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.hops.simple_parent_merge('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"bevel_weight"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Bevel weight'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.hops.bevel_weight('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"bool_union"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Boolean union'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.hops.bool_union('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"bool_intersect"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Boolean intersect'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.hops.bool_intersect('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"bool_difference"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Boolean difference'"}, {"name":"event_value", "value":"'PRESS'"}, {"name":"command", "value":"\"bpy.ops.hops.bool_difference('INVOKE_DEFAULT')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        return {'FINISHED'}


class FidgetCustomHopsMenu(bpy.types.Menu):
    bl_idname = "fidget.custom_hops_menu"
    bl_label = "Hops"

    def draw(self, context):
        layout = self.layout
        layout.operator("fidget.operator_hops", "Adjust bevel").operator_types = {"adjust_bevel"}
        layout.operator("fidget.operator_hops", "Adjust 2d bevel").operator_types = {"2d_bevel"}
        layout.operator("fidget.operator_hops", "Adjust curve").operator_types = {"adjust_curve"}
        layout.operator("fidget.operator_hops", "Adjust Tthick").operator_types = {"adjust_tthick"}
        layout.separator()
        layout.operator("fidget.operator_hops", "C Sharpen").operator_types = {"complex_sharpen"}
        layout.operator("fidget.operator_hops", "S Sharpen").operator_types = {"soft_sharpen"}
        layout.operator("fidget.operator_hops", "Slash").operator_types = {"slash"}
        layout.separator()
        layout.operator("fidget.operator_hops", "Finish Merge").operator_types = {"finish_setup"}
        layout.operator("fidget.operator_hops", "Copy Merge").operator_types = {"copy_merge"}
        layout.operator("fidget.operator_hops", "Remove Merge").operator_types = {"remove_merge"}
        layout.operator("fidget.operator_hops", "Parent Merge").operator_types = {"parent_merge"}
        layout.operator("fidget.operator_hops", "Simple Parent Merge").operator_types = {"simple_parent_merge"}
        layout.separator()
        layout.operator("fidget.operator_hops", "Adjust Weight").operator_types = {"bevel_weight"}
        layout.separator()
        layout.operator("fidget.operator_hops", "Boolean Union").operator_types = {"bool_union"}
        layout.operator("fidget.operator_hops", "Boolean Intersect").operator_types = {"bool_intersect"}
        layout.operator("fidget.operator_hops", "Boolean Difference").operator_types = {"bool_difference"}
