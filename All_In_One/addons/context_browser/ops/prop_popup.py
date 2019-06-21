import bpy
from ..addon import prefs, temp_prefs


class CB_OT_prop_popup(bpy.types.Operator):
    bl_idname = "cb.prop_popup"
    bl_label = "Prop Popup"

    data_path = bpy.props.StringProperty()
    prop = bpy.props.StringProperty()

    def check(self, context):
        return True

    def draw(self, context):
        layout = self.layout.column()
        layout.prop(self.data, self.prop)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        C = context
        self.data = eval(self.data_path)
        return context.window_manager.invoke_popup(self)
