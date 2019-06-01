import os
import bpy
from pathlib import Path
from .. trees import ActionsTree

class InteractiveModeOperator(bpy.types.Operator):
    bl_idname = "en.start_interactive_mode"
    bl_label = "Start Interactive Mode"

    def invoke(self, context, event):
        if not bpy.data.is_saved:
            self.report({"ERROR"}, "File has to be saved first")
            return {"CANCELLED"}

        save_current_state()
        bpy.ops.en.modal_runner("INVOKE_DEFAULT")
        wm = context.window_manager
        wm.modal_handler_add(self)
        self._timer = wm.event_timer_add(0.01, window = context.window)
        self.setup_view(context)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == "ESC":
            self.reset_window(context)
            context.window_manager.event_timer_remove(self._timer)
            load_last_saved_state()
            return {"FINISHED"}

        handle_event(event)
        return {"RUNNING_MODAL"}

    def setup_view(self, context):
        self.was_full_screen = context.screen.show_fullscreen
        context.area.type = "VIEW_3D"
        if not self.was_full_screen:
            bpy.ops.screen.screen_full_area()

    def reset_window(self, context):
        if not self.was_full_screen:
            bpy.ops.screen.screen_full_area()

def save_current_state():
    bpy.ops.wm.save_mainfile(filepath = bpy.data.filepath)

def load_last_saved_state():
    bpy.ops.wm.open_mainfile(filepath = bpy.data.filepath)

def handle_event(event):
    for tree in bpy.data.node_groups:
        if isinstance(tree, ActionsTree):
            tree.handle_event(event)