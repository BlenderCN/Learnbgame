import bpy
from ... utils import MACHIN3 as m3


axis_x = True
axis_y = True
axis_z = False


class ToggleGrid(bpy.types.Operator):
    bl_idname = "machin3.toggle_grid"
    bl_label = "Toggle Grid"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global axis_x, axis_y, axis_z

        overlay = context.space_data.overlay

        grid = context.space_data.overlay.show_floor

        if grid:
            # get axes states
            axis_x = overlay.show_axis_x
            axis_y = overlay.show_axis_y
            axis_z = overlay.show_axis_z

            # turn grid OFF
            overlay.show_floor = False

            # turn axes OFF
            overlay.show_axis_x = False
            overlay.show_axis_y = False
            overlay.show_axis_z = False

        else:
            # turn grid ON
            overlay.show_floor = True

            # turn axes ON (according to previous states)
            overlay.show_axis_x = axis_x
            overlay.show_axis_y = axis_y
            overlay.show_axis_z = axis_z

        return {'FINISHED'}


class ToggleWireframe(bpy.types.Operator):
    bl_idname = "machin3.toggle_wireframe"
    bl_label = "Toggle Wireframe"
    bl_options = {'REGISTER'}

    def execute(self, context):
        overlay = context.space_data.overlay

        if context.mode == "OBJECT":
            sel = context.selected_objects

            if sel:
                for obj in sel:
                    obj.show_wire = not obj.show_wire
                    obj.show_all_edges = obj.show_wire
            else:
                overlay.show_wireframes = not overlay.show_wireframes


        elif context.mode == "EDIT_MESH":
            context.scene.M3.show_edit_mesh_wire = not context.scene.M3.show_edit_mesh_wire

        return {'FINISHED'}


class ToggleOutline(bpy.types.Operator):
    bl_idname = "machin3.toggle_outline"
    bl_label = "Toggle Outline"
    bl_options = {'REGISTER'}

    def execute(self, context):
        shading = context.space_data.shading

        shading.show_object_outline = not shading.show_object_outline

        return {'FINISHED'}


class ToggleCavity(bpy.types.Operator):
    bl_idname = "machin3.toggle_cavity"
    bl_label = "Toggle Cavity"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene

        scene.M3.show_cavity = not scene.M3.show_cavity

        return {'FINISHED'}


class ToggleCurvature(bpy.types.Operator):
    bl_idname = "machin3.toggle_curvature"
    bl_label = "Toggle Curvature"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene

        scene.M3.show_curvature = not scene.M3.show_curvature

        return {'FINISHED'}
