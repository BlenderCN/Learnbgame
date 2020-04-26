import bpy
from .. graphics.drawing2d import draw_text, set_drawing_dpi
from .. utils.blender_ui import get_dpi, get_dpi_factor, get_3d_view_tools_panel_overlay_width
from .. graphics.logo import draw_logo_hops
from .. preferences import Hops_display_logo 


def draw_hud():
    set_drawing_dpi(get_dpi())
    dpi_factor = get_dpi_factor()

    if Hops_display_logo():
        draw_logo_hops()


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
