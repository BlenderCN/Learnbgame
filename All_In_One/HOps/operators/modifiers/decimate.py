import bpy
import math


class HOPS_OT_MOD_Decimate(bpy.types.Operator):
    bl_idname = "hops.mod_decimate"
    bl_label = "Add decimate Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Add decimate Modifier
LMB + CTRL - Add new decimate Modifier
"""

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def invoke(self, context, event):
        for object in context.selected_objects:
            if event.ctrl:
                self.add_decimate_modifier(context, object)
            else:
                if not self.decimate_modifiers(object):
                    self.add_decimate_modifier(context, object)
        return {"FINISHED"}

    @staticmethod
    def decimate_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "DECIMATE"]

    def add_decimate_modifier(self, context, object):
        decim_mod = object.modifiers.new(name="decimate", type="DECIMATE")
        decim_mod.decimate_type = 'DISSOLVE'
        decim_mod.angle_limit = math.radians(.05)
        #decim_mod.angle_limit = 0.000872665
        decim_mod.delimit = {'NORMAL', 'SHARP'}
        if context.mode == 'EDIT_MESH':
            decim_mod.decimate_type = 'COLLAPSE'
            vg = object.vertex_groups.new(name='HardOps')
            bpy.ops.object.vertex_group_assign()
            decim_mod.vertex_group = vg.name
