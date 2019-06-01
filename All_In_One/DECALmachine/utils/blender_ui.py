import bpy


def open_error_message(message="", title="Error", icon="ERROR"):
    def draw_error_message(self, context):
        self.layout.label(message)
    bpy.context.window_manager.popup_menu(draw_error_message, title=title, icon=icon)


def get_dpi_factor():
    return get_dpi() / 72


def get_dpi():
    systempreferences = bpy.context.user_preferences.system
    retinafactor = getattr(systempreferences, "pixel_size", 1)
    return int(systempreferences.dpi * retinafactor)
