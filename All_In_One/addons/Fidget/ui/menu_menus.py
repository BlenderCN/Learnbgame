import bpy
from bpy.props import *


operators_edit = [
    ("W", "", ""),
    ("FACES", "", ""),
    ("EDGES", "", ""),
    ("VERTS", "", ""),
    ("VIEW", "", ""),
    ("Select", "", ""),
    ("ADD", "", ""),
    ("OBJECT", "", ""),
    ("MIRROR", "", ""),
    ("EXTRUDE", "", ""),
    ("TRANSFORM", "", ""),
    ("HARDOPS", "", "")]


class FidgetMenuOperatorMenus(bpy.types.Operator):
    bl_idname = "fidget.operator_menus"
    bl_label = "Fidget Menu Menus Operator"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "execute menu operator"

    operator_types = EnumProperty(name="Operator Types", default={'W'},
                                  options={"ENUM_FLAG"}, items=operators_edit)

    def execute(self, context):

        if {"W"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'W'"}, {"name":"event_value", "value":"'RELEASE'"}, {"name":"command", "value":"\"bpy.ops.wm.call_menu(name='VIEW3D_MT_edit_mesh_specials')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"FACES"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Faces'"}, {"name":"event_value", "value":"'RELEASE'"}, {"name":"command", "value":"\"bpy.ops.wm.call_menu(name='VIEW3D_MT_edit_mesh_faces')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"EDGES"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Edges'"}, {"name":"event_value", "value":"'RELEASE'"}, {"name":"command", "value":"\"bpy.ops.wm.call_menu(name='VIEW3D_MT_edit_mesh_edges')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"VERTS"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Verts'"}, {"name":"event_value", "value":"'RELEASE'"}, {"name":"command", "value":"\"bpy.ops.wm.call_menu(name='VIEW3D_MT_edit_mesh_vertices')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"EXTRUDE"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Extrude'"}, {"name":"event_value", "value":"'RELEASE'"}, {"name":"command", "value":"\"bpy.ops.wm.call_menu(name='VIEW3D_MT_edit_mesh_extrude')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"TRANSFORM"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Transform'"}, {"name":"event_value", "value":"'RELEASE'"}, {"name":"command", "value":"\"bpy.ops.wm.call_menu(name='VIEW3D_MT_transform_object')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"MIRROR"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Mirror'"}, {"name":"event_value", "value":"'RELEASE'"}, {"name":"command", "value":"\"bpy.ops.wm.call_menu(name='VIEW3D_MT_mirror')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"HARDOPS"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'HARDOPS'"}, {"name":"event_value", "value":"'RELEASE'"}, {"name":"command", "value":"\"bpy.ops.wm.call_menu(name='hops_main_menu')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"VIEW"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'View'"}, {"name":"event_value", "value":"'RELEASE'"}, {"name":"command", "value":"\"bpy.ops.wm.call_menu(name='VIEW3D_MT_view')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"Select"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Select'"}, {"name":"event_value", "value":"'RELEASE'"}, {"name":"command", "value":"\"bpy.ops.wm.call_menu(name='VIEW3D_MT_select_object')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"ADD"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Add'"}, {"name":"event_value", "value":"'RELEASE'"}, {"name":"command", "value":"\"bpy.ops.wm.call_menu(name='INFO_MT_add')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        elif {"OBJECT"}.issubset(self.operator_types):
            bpy.ops.node.add_node(type="FidgetCommandNode", use_transform=True, settings=[{"name":"info_text", "value":"'Object'"}, {"name":"event_value", "value":"'RELEASE'"}, {"name":"command", "value":"\"bpy.ops.wm.call_menu(name='VIEW3D_MT_object')\""}])
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        return {'FINISHED'}


class FidgetCustomMenusMenu(bpy.types.Menu):
    bl_idname = "fidget.custom_menus_menu"
    bl_label = "Edit"

    def draw(self, context):
        layout = self.layout
        layout.operator("fidget.operator_menus", "W").operator_types = {"W"}
        layout.operator("fidget.operator_menus", "Faces").operator_types = {"FACES"}
        layout.operator("fidget.operator_menus", "Edges").operator_types = {"EDGES"}
        layout.operator("fidget.operator_menus", "Verts").operator_types = {"VERTS"}
        layout.separator()
        layout.operator("fidget.operator_menus", "View").operator_types = {"VIEW"}
        layout.operator("fidget.operator_menus", "Select").operator_types = {"Select"}
        layout.operator("fidget.operator_menus", "Add").operator_types = {"ADD"}
        layout.operator("fidget.operator_menus", "Object").operator_types = {"OBJECT"}
        layout.separator()
        layout.operator("fidget.operator_menus", "Extrude").operator_types = {"EXTRUDE"}
        layout.operator("fidget.operator_menus", "Transform").operator_types = {"TRANSFORM"}
        layout.operator("fidget.operator_menus", "Mirror").operator_types = {"MIRROR"}
        layout.separator()
        layout.operator("fidget.operator_menus", "Hardops").operator_types = {"HARDOPS"}
