import bpy
from ..addon import prefs

# @staticmethod
# def context_menu(menu, context):
#     menu.layout


def register():
    func = getattr(prefs(), "context_menu", None)
    if not func:
        return

    if not hasattr(bpy.types, "WM_MT_button_context"):
        tp = type(
            "WM_MT_button_context", (bpy.types.Menu,), dict(
                bl_label="Context Menu",
                draw=lambda s, c: s.layout.separator()
            ))
        bpy.utils.register_class(tp)

    bpy.types.WM_MT_button_context.append(func)


def unregister():
    func = getattr(prefs(), "context_menu", None)
    if not func:
        return

    if hasattr(bpy.types, "WM_MT_button_context"):
        bpy.types.WM_MT_button_context.remove(func)
