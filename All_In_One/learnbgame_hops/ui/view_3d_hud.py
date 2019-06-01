import bpy
from .. graphics.drawing2d import draw_text, set_drawing_dpi
from .. utils.blender_ui import get_dpi, get_dpi_factor, get_3d_view_tools_panel_overlay_width
from .. graphics.logo import draw_logo_hops
from .. preferences import Hops_display_logo, Hops_display_undefined_status, Hops_display_text_status, Hops_hud_text_color


def draw_hud():
    set_drawing_dpi(get_dpi())
    dpi_factor = get_dpi_factor()

    if Hops_display_logo():
        draw_logo_hops()


def draw_object_status(object, dpi_factor):
    text = "SStatus: {}".format(object.hops.status)
    x = get_3d_view_tools_panel_overlay_width(bpy.context.area, "left") + 20 * dpi_factor
    y = bpy.context.region.height - get_vertical_offset() * dpi_factor
    color = bpy.context.preferences.themes[0].user_interface.wcol_pie_menu.text
    draw_text(text, x, y, size=10, color=(Hops_hud_text_color()))


def get_vertical_offset():
    if bpy.context.scene.unit_settings.system == "NONE":
        return 40
    else:
        return 60

# Register
################################################################################

draw_handler = None


def register():
    global draw_handler
    draw_handler = bpy.types.SpaceView3D.draw_handler_add(draw_hud, tuple(), "WINDOW", "POST_PIXEL")


def unregister():
    global draw_handler
    bpy.types.SpaceView3D.draw_handler_remove(draw_handler, "WINDOW")
    draw_handler = None
