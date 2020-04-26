import bpy
from ... utils import MACHIN3 as m3



class ShadeSmooth(bpy.types.Operator):
    bl_idname = "machin3.shade_smooth"
    bl_label = "Shade Smooth"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.shade_smooth()
        elif context.mode == "EDIT_MESH":
            bpy.ops.mesh.faces_shade_smooth()

        return {'FINISHED'}


class ShadeFlat(bpy.types.Operator):
    bl_idname = "machin3.shade_flat"
    bl_label = "Shade Flat"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.mode == "OBJECT":
            bpy.ops.object.shade_flat()
        elif context.mode == "EDIT_MESH":
            bpy.ops.mesh.faces_shade_flat()

        return {'FINISHED'}


class ToggleAutoSmooth(bpy.types.Operator):
    bl_idname = "machin3.toggle_auto_smooth"
    bl_label = "Toggle Auto Smooth"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active = m3.get_active()

        if active:
            sel = m3.selected_objects()
            if active not in sel:
                sel.append(active)

            autosmooth = not active.data.use_auto_smooth

            for obj in sel:
                obj.data.use_auto_smooth = autosmooth

        return {'FINISHED'}
