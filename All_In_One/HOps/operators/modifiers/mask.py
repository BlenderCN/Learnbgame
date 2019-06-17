import bpy


class HOPS_OT_MOD_Mask(bpy.types.Operator):
    bl_idname = "hops.mod_mask"
    bl_label = "Add mask Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Add mask Modifier
LMB + CTRL - Add new mask Modifier
"""

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def invoke(self, context, event):
        for object in context.selected_objects:
            if event.ctrl:
                self.add_mask_modifier(context, object)
            else:
                if not self.mask_modifiers(object):
                    self.add_mask_modifier(context, object)
        return {"FINISHED"}

    @staticmethod
    def mask_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "MASK"]

    def add_mask_modifier(self, context, object):
        mask_mod = object.modifiers.new(name="Mask", type="MASK")
        mask_mod.invert_vertex_group = True

        if context.mode == 'EDIT_MESH':
            vg = object.vertex_groups.new(name='HardOps')
            bpy.ops.object.vertex_group_assign()
            mask_mod.vertex_group = vg.name
