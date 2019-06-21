import bpy
from ... utility import collections

class HOPS_OT_MOD_Hook(bpy.types.Operator):
    bl_idname = "hops.mod_hook"
    bl_label = "Add hook Modifier"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """LMB - Add hook Modifier
LMB + CTRL - Add new hook Modifier
"""

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        for obj in selected:
            return getattr(obj, "type", "") == "MESH"

    def invoke(self, context, event):
        cursor_loc = context.scene.cursor.location.copy()

        for object in context.selected_objects:
            if event.ctrl:
                self.add_hook_modifier(context, object)

            else:
                if not self.hook_modifiers(object):
                    self.add_hook_modifier(context, object)

        context.scene.cursor.location = cursor_loc
        return {"FINISHED"}

    @staticmethod
    def hook_modifiers(object):
        return [modifier for modifier in object.modifiers if modifier.type == "HOOK"]

    def add_hook_modifier(self, context, object):
        hook_mod = object.modifiers.new(name="Hook", type="HOOK")

        empty = bpy.data.objects.new("hook", None)
        collections.link_obj(context, empty, "Collection")
        empty.empty_display_size = 0.5
        empty.empty_display_type = 'PLAIN_AXES'
        bpy.ops.view3d.snap_cursor_to_selected()
        empty.location = context.scene.cursor.location
        hook_mod.object = empty

        if context.mode == 'EDIT_MESH':
            vg = object.vertex_groups.new(name='HardOps')
            bpy.ops.object.vertex_group_assign()
            hook_mod.vertex_group = vg.name
            bpy.ops.object.hook_reset(modifier=hook_mod.name)
