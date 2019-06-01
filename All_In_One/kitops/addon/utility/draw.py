import blf

from bgl import *
from mathutils import *

from . import addon, dpi, insert

handler = None
font_id = 0

def border(op, context):
    region = context.region
    color = addon.preference().border_color
    width = addon.preference().border_size * dpi.factor()
    offset = addon.preference().border_offset * dpi.factor()

    #FIX: behaves incorrectly with both shelves open on a narrow 3d view
    t_panel = [region for region in context.area.regions if region.type == 'TOOLS'][0]
    n_panel = [region for region in context.area.regions if region.type == 'UI'][0]

    l_offset = 0
    r_offset = 0

    if t_panel.width > 1:
        if t_panel.x == region.x:
            l_offset = t_panel.width
        else:
            r_offset = t_panel.width

    if n_panel.width > 1:
        if n_panel.x == region.x or (n_panel.x - region.x == t_panel.width and t_panel.x == region.x):
            l_offset += n_panel.width
        else:
            r_offset += n_panel.width

    if not context.space_data.region_quadviews and (insert.operator or insert.authoring()):
        points = (
            Vector((offset + l_offset, offset)),
            Vector((offset + l_offset, region.height - offset)),
            Vector((region.width - offset - r_offset - 1, region.height - offset)),
            Vector((region.width - offset - r_offset - 1, offset)))

        glLineWidth(width)

        glEnable(GL_BLEND)
        glBegin(GL_LINE_LOOP)

        glColor4f(*color)

        for point in points:
            glVertex2f(*point)

        glEnd()

        glDisable(GL_BLEND)

        if insert.operator:
            help_text(region, width, offset, r_offset)

    logo(context, region, width, offset, r_offset)

def logo(context, region, width, offset, r_offset):
    active = context.active_object
    color = addon.preference().logo_color if insert.operator or active and active.kitops.insert_target and not active.kitops.applied else addon.preference().off_color
    size = addon.preference().logo_size * dpi.factor()
    offset += 2
    x_offset = addon.preference().logo_padding_x
    y_offset = addon.preference().logo_padding_y

    if addon.preference().logo_auto_offset:
        hard_ops_name = [addon for addon in context.user_preferences.addons.keys() if addon in ('HardOps', 'HOps', 'HOps-master')]

        if len(hard_ops_name):
            hard_ops_name = hard_ops_name[0]
            hops_logo_size = context.user_preferences.addons[hard_ops_name].preferences.Hops_logo_size
            x_offset += int(6 * hops_logo_size * dpi.factor())

        boxcutter_name = [addon for addon in context.user_preferences.addons.keys() if addon in ('BoxCutter', 'BC', 'BC-master')]

        if len(boxcutter_name):
            boxcutter_name = boxcutter_name[0]
            bc_logo_size = context.user_preferences.addons[boxcutter_name].preferences.BC_indicator_size
            from BoxCutter.graphic.drawingbuttons import DrawBooleanLayout
            if DrawBooleanLayout.running_boxcutters:
                x_offset += int(6 * bc_logo_size * dpi.factor())

    glEnable(GL_BLEND)

    glColor4f(*color)

    glBegin(GL_POLYGON)
    glVertex2f(region.width - size - offset - r_offset - x_offset, region.height - size - offset - y_offset)
    glVertex2f(region.width - size - offset - r_offset - x_offset, region.height - offset - y_offset)
    glVertex2f(region.width - int(size * 0.9) - offset - r_offset - x_offset, region.height - int(size * 0.1) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.9) - offset - r_offset - x_offset, region.height - int(size * 0.9) - offset - y_offset)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex2f(region.width - int(size * 0.9) - offset - r_offset - x_offset, region.height - int(size * 0.1) - offset - y_offset)
    glVertex2f(region.width - size - offset - r_offset - x_offset, region.height - offset - y_offset)
    glVertex2f(region.width - offset - r_offset - x_offset, region.height - offset - y_offset)
    glVertex2f(region.width - int(size * 0.1) - offset - r_offset - x_offset, region.height - int(size * 0.1) - offset - y_offset)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex2f(region.width - int(size * 0.1) - offset - r_offset - x_offset, region.height - int(size * 0.9) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.1) - offset - r_offset - x_offset, region.height - int(size * 0.1) - offset - y_offset)
    glVertex2f(region.width - offset - r_offset - x_offset, region.height - offset - y_offset)
    glVertex2f(region.width - offset - r_offset - x_offset, region.height - size - offset - y_offset)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex2f(region.width - size - offset - r_offset - x_offset, region.height - size - offset - y_offset)
    glVertex2f(region.width - int(size * 0.9) - offset - r_offset - x_offset, region.height - int(size * 0.9) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.1) - offset - r_offset - x_offset, region.height - int(size * 0.9) - offset - y_offset)
    glVertex2f(region.width - offset - r_offset - x_offset, region.height - size - offset - y_offset)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex2f(region.width - int(size * 0.55) - offset - r_offset - x_offset, region.height - int(size * 0.4675) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.55) - offset - r_offset - x_offset, region.height - int(size * 0.3675) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.45) - offset - r_offset - x_offset, region.height - int(size * 0.3675) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.45) - offset - r_offset - x_offset, region.height - int(size * 0.4675) - offset - y_offset)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex2f(region.width - int(size * 0.65) - offset - r_offset - x_offset, region.height - int(size * 0.4675) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.65) - offset - r_offset - x_offset, region.height - int(size * 0.3675) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.55) - offset - r_offset - x_offset, region.height - int(size * 0.3675) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.55) - offset - r_offset - x_offset, region.height - int(size * 0.4675) - offset - y_offset)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex2f(region.width - int(size * 0.55) - offset - r_offset - x_offset, region.height - int(size * 0.3675) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.55) - offset - r_offset - x_offset, region.height - int(size * 0.2675) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.45) - offset - r_offset - x_offset, region.height - int(size * 0.2675) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.45) - offset - r_offset - x_offset, region.height - int(size * 0.3675) - offset - y_offset)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex2f(region.width - int(size * 0.45) - offset - r_offset - x_offset, region.height - int(size * 0.4675) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.45) - offset - r_offset - x_offset, region.height - int(size * 0.3675) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.35) - offset - r_offset - x_offset, region.height - int(size * 0.3675) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.35) - offset - r_offset - x_offset, region.height - int(size * 0.4675) - offset - y_offset)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex2f(region.width - int(size * 0.55) - offset - r_offset - x_offset, region.height - int(size * 0.5675) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.55) - offset - r_offset - x_offset, region.height - int(size * 0.4675) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.45) - offset - r_offset - x_offset, region.height - int(size * 0.4675) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.45) - offset - r_offset - x_offset, region.height - int(size * 0.5675) - offset - y_offset)
    glEnd()

    glBegin(GL_POLYGON)
    glVertex2f(region.width - int(size * 0.65) - offset - r_offset - x_offset, region.height - int(size * 0.7175) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.65) - offset - r_offset - x_offset, region.height - int(size * 0.6175) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.35) - offset - r_offset - x_offset, region.height - int(size * 0.6175) - offset - y_offset)
    glVertex2f(region.width - int(size * 0.35) - offset - r_offset - x_offset, region.height - int(size * 0.7175) - offset - y_offset)
    glEnd()

    glDisable(GL_BLEND)

def help_text(region, width, offset, r_offset):
    global font_id

    color = addon.preference().text_color
    icon_size = addon.preference().logo_size * dpi.factor() + 24
    y_offset = addon.preference().logo_padding_y

    blf.size(font_id, 9, dpi.system())

    label = 'ESC | EXIT'
    dimension = Vector(blf.dimensions(font_id, label))
    location = Vector((region.width - dimension.x - offset * 2 - r_offset, region.height - dimension.y - offset * 2 - icon_size - y_offset))
    text(location, label, size=9, color=color)
    last_y = dimension.y * 2

    label = 'INSERT | {}'.format(insert.operator.main.kitops.label.upper())
    dimension = Vector(blf.dimensions(font_id, label))
    location = Vector((region.width - dimension.x - offset * 2 - r_offset, region.height - dimension.y - offset * 2 - icon_size - y_offset))
    location.y -= last_y
    text(location, label, size=9, color=color)
    last_y += dimension.y * 1.5

    label = 'COLLECTION | {}'.format(insert.operator.main.kitops.collection.upper())
    dimension = Vector(blf.dimensions(font_id, label))
    location = Vector((region.width - dimension.x - offset * 2 - r_offset, region.height - dimension.y - offset * 2 - icon_size - y_offset))
    location.y -= last_y
    text(location, label, size=9, color=color)
    last_y += dimension.y * 1.5

    if insert.operator.main.kitops.author:
        label = 'AUTHOR | {}'.format(insert.operator.main.kitops.author.upper())
        dimension = Vector(blf.dimensions(font_id, label))
        location = Vector((region.width - dimension.x - offset * 2 - r_offset, region.height - dimension.y - offset * 2 - icon_size - y_offset))
        location.y -= last_y
        text(location, label, size=9, color=color)

def text(location, label, size=12, color=(0.95, 0.95, 0.95, 1.0)):
    global font_id

    blf.size(font_id, size, dpi.system())

    glEnable(GL_BLEND)

    blf.position(font_id, location.x, location.y, 0)

    glColor4f(*color)

    blf.draw(font_id, label)

    glDisable(GL_BLEND)
