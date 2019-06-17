import bpy


class HOPS_OT_MOD_Subdivision(bpy.types.Operator):
    bl_idname = "hops.mod_subdivision"
    bl_label = "Add Subdivision Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Add Subdivision Modifier
LMB + Shift - Use Simple Option
LMB + CTRL - Add new Subdivision Modifier

"""

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def invoke(self, context, event):
        for object in context.selected_objects:
            if event.ctrl:
                self.add_Subdivision_modifier(object, event)
            else:
                if not self.Subdivision_modifiers(object):
                    self.add_Subdivision_modifier(object, event)
        return {"FINISHED"}

    @staticmethod
    def Subdivision_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "SUBDIVISION"]

    def add_Subdivision_modifier(self, object, event):
        subsurf_mod = object.modifiers.new(name="Subdivision", type="SUBSURF")
        if event.shift:
            subsurf_mod.subdivision_type = 'SIMPLE'
        else:
            subsurf_mod.subdivision_type = 'CATMULL_CLARK'
            subsurf_mod.levels = 2
