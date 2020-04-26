import bpy
from .. contexts.driver import evaluate_drivers
from .. contexts.mesh_modifier import evaluate_modifiers

class ModalRunnerOperator(bpy.types.Operator):
    bl_idname = "en.modal_runner"
    bl_label = "Modal Runner"

    def invoke(self, context, event):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.01, window = context.window)
        wm.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == "TIMER":
            evaluate_drivers()
            evaluate_modifiers()

        if event.type == "ESC":
            self.finish(context)
            return {"CANCELLED"}

        return {"PASS_THROUGH"}

    def finish(self, context):
        context.window_manager.event_timer_remove(self._timer)

