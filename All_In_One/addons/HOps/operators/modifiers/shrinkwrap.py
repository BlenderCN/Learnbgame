import bpy


class HOPS_OT_MOD_Shrinkwrap(bpy.types.Operator):
    bl_idname = "hops.mod_shrinkwrap"
    bl_label = "Add shrinkwrap Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Add shrinkwrap Modifier
LMB + CTRL - Add new shrinkwrap Modifier

"""

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def invoke(self, context, event):
        active = context.active_object
        for object in context.selected_objects:
            if object is not active:
                if event.ctrl:
                    self.add_shrinkwrap_modifier(object, active)
                else:
                    if not self.shrinkwrap_modifiers(object):
                        self.add_shrinkwrap_modifier(object, active)
        return {"FINISHED"}

    @staticmethod
    def shrinkwrap_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "SHRINKWRAP"]

    def add_shrinkwrap_modifier(self, object, obj):
        shrink_mod = object.modifiers.new(name="shrinkwrap", type="SHRINKWRAP")
        shrink_mod.cull_face = 'BACK'
        shrink_mod.offset = 0
        shrink_mod.target = obj
        shrink_mod.wrap_method = 'PROJECT'
        shrink_mod.wrap_mode = 'ON_SURFACE'
        shrink_mod.cull_face = 'OFF'
        shrink_mod.use_negative_direction = True
        shrink_mod.use_positive_direction = True
        shrink_mod.use_invert_cull = True
