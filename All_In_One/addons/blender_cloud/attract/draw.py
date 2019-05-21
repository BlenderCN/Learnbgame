# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
import logging
import collections

log = logging.getLogger(__name__)

strip_status_colour = {
    None: (0.7, 0.7, 0.7),
    'approved': (0.6392156862745098, 0.8784313725490196, 0.30196078431372547),
    'final': (0.9058823529411765, 0.9607843137254902, 0.8274509803921568),
    'in_progress': (1.0, 0.7450980392156863, 0.0),
    'on_hold': (0.796078431372549, 0.6196078431372549, 0.08235294117647059),
    'review': (0.8941176470588236, 0.9607843137254902, 0.9764705882352941),
    'todo': (1.0, 0.5019607843137255, 0.5019607843137255)
}

CONFLICT_COLOUR = (0.576, 0.118, 0.035)  # RGB tuple


def get_strip_rectf(strip):
    # Get x and y in terms of the grid's frames and channels
    x1 = strip.frame_final_start
    x2 = strip.frame_final_end
    y1 = strip.channel + 0.2
    y2 = strip.channel - 0.2 + 1

    return x1, y1, x2, y2


def draw_underline_in_strip(strip_coords, pixel_size_x, color):
    from bgl import glColor4f, glRectf, glEnable, glDisable, GL_BLEND
    import bgl

    context = bpy.context

    # Strip coords
    s_x1, s_y1, s_x2, s_y2 = strip_coords

    # be careful not to draw over the current frame line
    cf_x = context.scene.frame_current_final

    bgl.glPushAttrib(bgl.GL_COLOR_BUFFER_BIT | bgl.GL_LINE_BIT)

    glColor4f(*color)
    glEnable(GL_BLEND)
    bgl.glLineWidth(2)
    bgl.glBegin(bgl.GL_LINES)

    bgl.glVertex2f(s_x1, s_y1)
    if s_x1 < cf_x < s_x2:
        # Bad luck, the line passes our strip
        bgl.glVertex2f(cf_x - pixel_size_x, s_y1)
        bgl.glVertex2f(cf_x + pixel_size_x, s_y1)
    bgl.glVertex2f(s_x2, s_y1)

    bgl.glEnd()
    bgl.glPopAttrib()


def draw_strip_conflict(strip_coords, pixel_size_x):
    """Draws conflicting states between strips."""

    import bgl

    s_x1, s_y1, s_x2, s_y2 = strip_coords
    bgl.glPushAttrib(bgl.GL_COLOR_BUFFER_BIT | bgl.GL_LINE_BIT)

    # Always draw the full rectangle, the conflict should be resolved and thus stand out.
    bgl.glColor3f(*CONFLICT_COLOUR)
    bgl.glLineWidth(2)

    bgl.glBegin(bgl.GL_LINE_LOOP)
    bgl.glVertex2f(s_x1, s_y1)
    bgl.glVertex2f(s_x2, s_y1)
    bgl.glVertex2f(s_x2, s_y2)
    bgl.glVertex2f(s_x1, s_y2)
    bgl.glEnd()

    bgl.glPopAttrib()


def draw_callback_px():
    context = bpy.context

    if not context.scene.sequence_editor:
        return

    from . import shown_strips

    region = context.region
    xwin1, ywin1 = region.view2d.region_to_view(0, 0)
    xwin2, ywin2 = region.view2d.region_to_view(region.width, region.height)
    one_pixel_further_x, one_pixel_further_y = region.view2d.region_to_view(1, 1)
    pixel_size_x = one_pixel_further_x - xwin1

    strips = shown_strips(context)

    for strip in strips:
        if not strip.atc_object_id:
            continue

        # Get corners (x1, y1), (x2, y2) of the strip rectangle in px region coords
        strip_coords = get_strip_rectf(strip)

        # check if any of the coordinates are out of bounds
        if strip_coords[0] > xwin2 or strip_coords[2] < xwin1 or strip_coords[1] > ywin2 or \
                        strip_coords[3] < ywin1:
            continue

        # Draw
        status = strip.atc_status
        if status in strip_status_colour:
            color = strip_status_colour[status]
        else:
            color = strip_status_colour[None]

        alpha = 1.0 if strip.atc_is_synced else 0.5

        draw_underline_in_strip(strip_coords, pixel_size_x, color + (alpha,))
        if strip.atc_is_synced and strip.atc_object_id_conflict:
            draw_strip_conflict(strip_coords, pixel_size_x)


def tag_redraw_all_sequencer_editors():
    context = bpy.context

    # Py cant access notifiers
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'SEQUENCE_EDITOR':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()


# This is a list so it can be changed instead of set
# if it is only changed, it does not have to be declared as a global everywhere
cb_handle = []


def callback_enable():
    if cb_handle:
        return

    cb_handle[:] = bpy.types.SpaceSequenceEditor.draw_handler_add(
        draw_callback_px, (), 'WINDOW', 'POST_VIEW'),

    tag_redraw_all_sequencer_editors()


def callback_disable():
    if not cb_handle:
        return

    try:
        bpy.types.SpaceSequenceEditor.draw_handler_remove(cb_handle[0], 'WINDOW')
    except ValueError:
        # Thrown when already removed.
        pass
    cb_handle.clear()

    tag_redraw_all_sequencer_editors()
