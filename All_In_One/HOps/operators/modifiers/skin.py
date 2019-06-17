import bpy


class HOPS_OT_MOD_Skin(bpy.types.Operator):
    bl_idname = "hops.mod_skin"
    bl_label = "Add skin Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Add skin Modifier
LMB + CTRL - Add new skin Modifier

"""

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def invoke(self, context, event):
        for object in context.selected_objects:
            if event.ctrl:
                self.add_skin_modifier(object)
            else:
                if not self.skin_modifiers(object):
                    self.add_skin_modifier(object)
        return {"FINISHED"}

    @staticmethod
    def skin_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "SKIN"]

    def add_skin_modifier(self, object):
        skin_mod = object.modifiers.new(name="skin", type="SKIN")
        skin_mod.branch_smoothing = 0
        skin_mod.use_smooth_shade = True
        skin_mod.use_x_symmetry = False
        skin_mod.use_y_symmetry = False
        skin_mod.use_z_symmetry = False
