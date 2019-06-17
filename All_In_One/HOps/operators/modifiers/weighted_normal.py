import bpy


class HOPS_OT_MOD_Weighted_Normal(bpy.types.Operator):
    bl_idname = "hops.mod_weighted_normal"
    bl_label = "Add Weighted Normal Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Add Weighted Normal Modifier
LMB + CTRL - Add new Weighted Normal Modifier

"""

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def invoke(self, context, event):
        for object in context.selected_objects:
            if event.ctrl:
                self.add_normal_modifier(object)
            else:
                if not self.normal_modifiers(object):
                    self.add_normal_modifier(object)
        return {"FINISHED"}

    @staticmethod
    def normal_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "WEIGHTED_NORMAL"]

    def add_normal_modifier(self, object):
        object.modifiers.new(name="Weighted Normal", type="WEIGHTED_NORMAL")
        object.modifiers["Weighted Normal"].keep_sharp = True
