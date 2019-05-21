import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from bgl import *
from .. utils.blender_ui import get_3d_view_tools_panel_overlay_width, get_dpi_factor
from .. preferences import Hops_logo_color, Hops_logo_size, Hops_logo_y_position, Hops_logo_x_position, Hops_logo_color_cstep, Hops_logo_color_csharp, Hops_logo_color_boolshape, Hops_logo_color_boolshape2, get_preferences


def draw_logo_hops():
    object = bpy.context.active_object

    if object is not None:

        if object.hops.status == "CSHARP":
            color = Hops_logo_color_csharp()[:]
        elif object.hops.status == "CSTEP":
            color = Hops_logo_color_cstep()[:]
        elif object.hops.status == "BOOLSHAPE":
            color = Hops_logo_color_boolshape()[:]
        elif object.hops.status == "BOOLSHAPE2":
            color = Hops_logo_color_boolshape2()[:]
        else:
            color = Hops_logo_color()[:]
    else:
        color = Hops_logo_color()[:]

    bgR = color[0]
    bgG = color[1]
    bgB = color[2]
    bgA = color[3]
    factor = get_dpi_factor()

    rw = rw = bpy.context.region.width - get_3d_view_tools_panel_overlay_width(bpy.context.area, "right")
    rh = bpy.context.region.height - 50 * factor
    d = Hops_logo_size() * factor
    x = Hops_logo_x_position() * factor
    if bpy.context.space_data.show_gizmo is True:
        if bpy.context.space_data.show_gizmo_navigate is True:
            x = Hops_logo_x_position() * factor - 180 * factor
    y = Hops_logo_y_position() * factor
    
    vertices = (
        (rw + 0*d + x, rh + (0*d + y)),
        (rw + 4*d + x, rh + (0*d + y)),
        (rw + 4*d + x, rh + (1*d + y)),
        (rw + 1*d + x, rh + (1*d + y)),
        (rw + 1*d + x, rh + (4*d + y)),
        (rw + 0*d + x, rh + (4*d + y)),

        (rw + 10*d + x, rh + (0*d + y)),
        (rw + 10*d + x, rh + (4*d + y)),
        (rw + 9*d + x, rh + (4*d + y)),
        (rw + 9*d + x, rh + (1*d + y)),
        (rw + 6*d + x, rh + (1*d + y)),
        (rw + 6*d + x, rh + (0*d + y)),

        (rw + 0*d + x, rh + (10*d + y)),
        (rw + 0*d + x, rh + (6*d + y)),
        (rw + 1*d + x, rh + (6*d + y)),
        (rw + 1*d + x, rh + (9*d + y)),
        (rw + 4*d + x, rh + (9*d + y)),
        (rw + 4*d + x, rh + (10*d + y)),

        (rw + 9*d + x, rh + (9*d + y)),
        (rw + 9*d + x, rh + (6*d + y)),
        (rw + 10*d + x, rh + (6*d + y)),
        (rw + 10*d + x, rh + (10*d + y)),
        (rw + 6*d + x, rh + (10*d + y)),
        (rw + 6*d + x, rh + (9*d + y)),

        (rw + 2.5*d + x, rh + (2*d + y)),
        (rw + 2.5*d + x, rh + (4*d + y)),
        (rw + 4*d + x, rh + (3.5*d + y)),
        (rw + 4*d + x, rh + (2*d + y)),

        (rw + 2.5*d + x, rh + (4*d + y)),
        (rw + 6*d + x, rh + (7.5*d + y)),
        (rw + 6.5*d + x, rh + (6*d + y)),
        (rw + 4*d + x, rh + (3.5*d + y)),

        (rw + 6*d + x, rh + (7.5*d + y)),
        (rw + 8*d + x, rh + (7.5*d + y)),
        (rw + 8*d + x, rh + (6*d + y)),
        (rw + 6.5*d + x, rh + (6*d + y))

        )

    indices = (
        (0, 1, 2), (2, 3, 0), (0, 4, 3), (0, 5, 4),
        (6, 7, 8), (8, 9, 6), (6, 10, 9), (6, 11, 10),
        (12, 13, 14), (14, 15, 12), (12, 16, 15), (12, 17, 16),
        (18, 19, 20), (20, 21, 18), (18, 22, 21), (18, 23, 22),
        (24, 25, 26), (26, 27, 24),
        (28, 29, 30), (30, 31, 28),
        (32, 33, 34), (34, 35, 32))

    shader = gpu.shader.from_builtin('2D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos" : vertices}, indices=indices)

    shader.bind()
    shader.uniform_float("color", color)
    glEnable(GL_BLEND)
    batch.draw(shader)
    glDisable(GL_BLEND)

def draw_logo_hops_old():

    object = bpy.context.active_object

    if object is not None:

        if object.hops.status == "CSHARP":
            color = Hops_logo_color_csharp()[:]
        elif object.hops.status == "CSTEP":
            color = Hops_logo_color_cstep()[:]
        elif object.hops.status == "BOOLSHAPE":
            color = Hops_logo_color_boolshape()[:]
        elif object.hops.status == "BOOLSHAPE2":
            color = Hops_logo_color_boolshape2()[:]
        else:
            color = Hops_logo_color()[:]
    else:
        color = Hops_logo_color()[:]

    bgR = color[0]
    bgG = color[1]
    bgB = color[2]
    bgA = color[3]

    rw = rw = bpy.context.region.width - get_3d_view_tools_panel_overlay_width(bpy.context.area, "right")
    rh = bpy.context.region.height - 50
    d = Hops_logo_size()
    x = Hops_logo_x_position()
    y = Hops_logo_y_position()

    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)

    glColor4f(bgR, bgG, bgB, bgA)

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(rw + 0*d + x, rh + (0*d + y))
    glVertex2f(rw + 4*d + x, rh + (0*d + y))
    glVertex2f(rw + 4*d + x, rh + (1*d + y))
    glVertex2f(rw + 1*d + x, rh + (1*d + y))
    glVertex2f(rw + 1*d + x, rh + (4*d + y))
    glVertex2f(rw + 0*d + x, rh + (4*d + y))
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(rw + 10*d + x, rh + (0*d + y))
    glVertex2f(rw + 10*d + x, rh + (4*d + y))
    glVertex2f(rw + 9*d + x, rh + (4*d + y))
    glVertex2f(rw + 9*d + x, rh + (1*d + y))
    glVertex2f(rw + 6*d + x, rh + (1*d + y))
    glVertex2f(rw + 6*d + x, rh + (0*d + y))
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(rw + 0*d + x, rh + (10*d + y))
    glVertex2f(rw + 0*d + x, rh + (6*d + y))
    glVertex2f(rw + 1*d + x, rh + (6*d + y))
    glVertex2f(rw + 1*d + x, rh + (9*d + y))
    glVertex2f(rw + 4*d + x, rh + (9*d + y))
    glVertex2f(rw + 4*d + x, rh + (10*d + y))
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(rw + 9*d + x, rh + (9*d + y))
    glVertex2f(rw + 9*d + x, rh + (6*d + y))
    glVertex2f(rw + 10*d + x, rh + (6*d + y))
    glVertex2f(rw + 10*d + x, rh + (10*d + y))
    glVertex2f(rw + 6*d + x, rh + (10*d + y))
    glVertex2f(rw + 6*d + x, rh + (9*d + y))
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(rw + 2.5*d + x, rh + (2*d + y))
    glVertex2f(rw + 2.5*d + x, rh + (4*d + y))
    glVertex2f(rw + 4*d + x, rh + (3.5*d + y))
    glVertex2f(rw + 4*d + x, rh + (2*d + y))
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(rw + 2.5*d + x, rh + (4*d + y))
    glVertex2f(rw + 6*d + x, rh + (7.5*d + y))
    glVertex2f(rw + 6.5*d + x, rh + (6*d + y))
    glVertex2f(rw + 4*d + x, rh + (3.5*d + y))
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(rw + 6*d + x, rh + (7.5*d + y))
    glVertex2f(rw + 8*d + x, rh + (7.5*d + y))
    glVertex2f(rw + 8*d + x, rh + (6*d + y))
    glVertex2f(rw + 6.5*d + x, rh + (6*d + y))
    glEnd()

    glDisable(GL_BLEND)
    glDisable(GL_LINE_SMOOTH)
