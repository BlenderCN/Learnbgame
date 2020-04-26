import bpy


class HOPS_OT_MOD_Triangulate(bpy.types.Operator):
    bl_idname = "hops.mod_triangulate"
    bl_label = "Add Triangulate Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Add Triangulate Modifier
LMB + CTRL - Add new Triangulate Modifier
"""

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def invoke(self, context, event):
        for object in context.selected_objects:
            if event.ctrl:
                self.add_triangulate_modifier(object)
            else:
                if not self.triangulate_modifiers(object):
                    self.add_triangulate_modifier(object)
        return {"FINISHED"}

    @staticmethod
    def triangulate_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "TRIANGULATE"]

    def add_triangulate_modifier(self, object):
        tri_mod = object.modifiers.new(name="Triangulate", type="TRIANGULATE")
        tri_mod.min_vertices = 5
