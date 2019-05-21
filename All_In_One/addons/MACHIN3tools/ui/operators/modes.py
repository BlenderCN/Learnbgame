import bpy
from bpy.props import StringProperty
from ... utils.registration import get_prefs
from ... utils.view import set_xray, reset_xray


user_cavity = True


class EditMode(bpy.types.Operator):
    bl_idname = "machin3.edit_mode"
    bl_label = "Edit Mode"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        global user_cavity

        shading = context.space_data.shading
        toggle_cavity = get_prefs().toggle_cavity

        if context.mode == "OBJECT":
            set_xray(context)

            bpy.ops.object.mode_set(mode="EDIT")

            if toggle_cavity:
                user_cavity = shading.show_cavity
                shading.show_cavity = False


        elif context.mode == "EDIT_MESH":
            reset_xray(context)

            bpy.ops.object.mode_set(mode="OBJECT")

            if toggle_cavity and user_cavity:
                shading.show_cavity = True
                user_cavity = True

        return {'FINISHED'}


class VertexMode(bpy.types.Operator):
    bl_idname = "machin3.vertex_mode"
    bl_label = "Vertex Mode"
    bl_description = "Vertex Select\nCTRL + Click: Expand Selection"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        global user_cavity
        shading = context.space_data.shading
        toggle_cavity = get_prefs().toggle_cavity

        if context.mode == "OBJECT":
            set_xray(context)

            bpy.ops.object.mode_set(mode="EDIT")

            if toggle_cavity:
                user_cavity = shading.show_cavity
                shading.show_cavity = False

        expand = True if event.ctrl else False

        bpy.ops.mesh.select_mode(use_extend=False, use_expand=expand, type='VERT')

        return {'FINISHED'}


class EdgeMode(bpy.types.Operator):
    bl_idname = "machin3.edge_mode"
    bl_label = "Edge Mode"
    bl_description = "Edge Select\nCTRL + Click: Expand Selection"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        global user_cavity
        shading = context.space_data.shading
        toggle_cavity = get_prefs().toggle_cavity

        if context.mode == "OBJECT":
            set_xray(context)

            bpy.ops.object.mode_set(mode="EDIT")

            if toggle_cavity:
                user_cavity = shading.show_cavity
                shading.show_cavity = False


        expand = True if event.ctrl else False

        bpy.ops.mesh.select_mode(use_extend=False, use_expand=expand, type='EDGE')

        return {'FINISHED'}


class FaceMode(bpy.types.Operator):
    bl_idname = "machin3.face_mode"
    bl_label = "Face Mode"
    bl_description = "Face Select\nCTRL + Click: Expand Selection"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        global user_cavity
        shading = context.space_data.shading
        toggle_cavity = get_prefs().toggle_cavity

        if context.mode == "OBJECT":
            set_xray(context)

            bpy.ops.object.mode_set(mode="EDIT")

            if toggle_cavity:
                user_cavity = shading.show_cavity
                shading.show_cavity = False

        expand = True if event.ctrl else False

        bpy.ops.mesh.select_mode(use_extend=False, use_expand=expand, type='FACE')

        return {'FINISHED'}


class ImageMode(bpy.types.Operator):
    bl_idname = "machin3.image_mode"
    bl_label = "MACHIN3: Image Mode"
    bl_options = {'REGISTER'}

    mode: StringProperty()

    def execute(self, context):
        view = context.space_data
        active = context.active_object

        view.mode = self.mode

        if self.mode == "UV" and active:
            if active.mode == "OBJECT":
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.mesh.select_all(action="SELECT")

        return {'FINISHED'}


class UVMode(bpy.types.Operator):
    bl_idname = "machin3.uv_mode"
    bl_label = "MACHIN3: UV Mode"
    bl_options = {'REGISTER'}

    mode: StringProperty()

    def execute(self, context):
        toolsettings = context.scene.tool_settings
        view = context.space_data

        if view.mode != "UV":
            view.mode = "UV"

        if toolsettings.use_uv_select_sync:
            bpy.ops.mesh.select_mode(type=self.mode.replace("VERTEX", "VERT"))

        else:
            toolsettings.uv_select_mode = self.mode

        return {'FINISHED'}
