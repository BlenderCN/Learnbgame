import bpy
from . objects import set_active

class ExecutionContext:
    def __init__(self, mode, active_object):
        self.context_mode = mode
        self.active_object = active_object

    def __enter__(self):
        set_active(self.active_object)
        self.old_mode = get_mode()
        if self.old_mode != self.context_mode:
            bpy.ops.object.mode_set(mode = self.context_mode)

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.old_mode != self.context_mode:
            bpy.ops.object.mode_set(mode = self.old_mode)

def get_mode():
    return getattr(bpy.context.active_object, "mode", "OBJECT")
