import bpy
from bpy.props import FloatProperty
import bgl
import blf
from . import MACHIN3 as m3



def popup_message(message, title="Info", icon="INFO", terminal=True):
    def draw_message(self, context):
        if isinstance(message, list):
            for m in message:
                self.layout.label(m)
        else:
            self.layout.label(message)
    bpy.context.window_manager.popup_menu(draw_message, title=title, icon=icon)

    if terminal:
        if icon == "FILE_TICK":
            icon = "ENABLE"
        elif icon == "CANCEL":
            icon = "DISABLE"
        print(icon, title)
        print(" » ", message)


def step_enum(current, items, step, loop=True):
    item_list = [item[0] for item in items]
    item_idx = item_list.index(current)

    step_idx = item_idx + step

    if step_idx >= len(item_list):
        if loop:
            step_idx = 0
        else:
            step_idx = len(item_list) - 1
    elif step_idx < 0:
        if loop:
            step_idx = len(item_list) - 1
        else:
            step_idx = 0

    return item_list[step_idx]


def step_collection(object, currentitem, itemsname, indexname, step):
    item_list = [item for item in getattr(object, itemsname)]
    item_idx = item_list.index(currentitem)

    step_idx = item_idx + step

    if step_idx >= len(item_list):
        # step_idx = 0
        step_idx = len(item_list) - 1
    elif step_idx < 0:
        # step_idx = len(item_list) - 1
        step_idx = 0

    setattr(object, indexname, step_idx)

    return getattr(object, itemsname)[step_idx]


def draw_init(self, args):
    self, context = args

    voffset = 20

    self.HUDx = self.mouse_x
    self.HUDy = self.mouse_y + voffset

    self.font_id = 1
    self.offset = 0

    bgl.glEnable(bgl.GL_BLEND)


def draw_end():
    bgl.glEnd()
    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glEnable(bgl.GL_DEPTH_TEST)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


def draw_title(self, title, subtitle=None, subtitleoffset=125, HUDcolor=None, HUDalpha=0.5):
    if not HUDcolor:
        HUDcolor = m3.MM_prefs().modal_hud_color

    scale = bpy.context.user_preferences.view.ui_scale * m3.MM_prefs().modal_hud_scale

    bgl.glColor4f(*HUDcolor, HUDalpha)

    blf.position(self.font_id, self.HUDx - 7, self.HUDy, 0)
    blf.size(self.font_id, int(20 * scale), 72)
    blf.draw(self.font_id, "» " + title)

    if subtitle:
        bgl.glColor4f(*HUDcolor, HUDalpha / 2)
        blf.position(self.font_id, self.HUDx - 7 + int(subtitleoffset * scale), self.HUDy, 0)
        blf.size(self.font_id, int(15 * scale), 72)
        blf.draw(self.font_id, subtitle)


def draw_prop(self, name, value, offset=0, decimal=2, active=True, HUDcolor=None, key=""):
    if not HUDcolor:
        HUDcolor = m3.MM_prefs().modal_hud_color

    if active:
        alpha = 1
    else:
        alpha = 0.4

    scale = bpy.context.user_preferences.view.ui_scale * m3.MM_prefs().modal_hud_scale

    offset = self.offset + int(offset * scale)
    self.offset = offset

    bgl.glColor4f(*HUDcolor, alpha)

    # NAME

    blf.position(self.font_id, self.HUDx + int(20 * scale), self.HUDy - int(20 * scale) - offset, 0)
    blf.size(self.font_id, int(11 * scale), 72)
    blf.draw(self.font_id, name)

    # VALUE

    blf.position(self.font_id, self.HUDx + int(120 * scale), self.HUDy - int(20 * scale) - offset, 0)

    # string
    if type(value) is str:
        blf.size(self.font_id, int(14 * scale), 72)
        blf.draw(self.font_id, value)

    # bool
    elif type(value) is bool:
        if value:
            bgl.glColor4f(0.5, 1.0, 0.5, alpha)
        else:
            bgl.glColor4f(1.0, 0.3, 0.3, alpha)
        blf.size(self.font_id, int(14 * scale), 72)
        blf.draw(self.font_id, str(value))

    # int
    elif type(value) is int:
        blf.size(self.font_id, int(20 * scale), 72)
        blf.draw(self.font_id, "%d" % (value))

    # float
    elif type(value) is float:
        blf.size(self.font_id, int(16 * scale), 72)
        blf.draw(self.font_id, "%.*f" % (decimal, value))

    # HINTS

    if m3.MM_prefs().modal_hud_hints and key:
        bgl.glColor4f(*HUDcolor, 0.6)
        blf.position(self.font_id, self.HUDx + int(200 * scale), self.HUDy - int(20 * scale) - offset, 0)
        blf.size(self.font_id, int(11 * scale), 72)
        blf.draw(self.font_id, "%s" % (key))


def wrap_mouse(self, context, event, x=False, y=False):
    if x:
        if event.mouse_region_x > context.region.width - 2:
            bpy.context.window.cursor_warp(event.mouse_x - context.region.width + 2, event.mouse_y)
            self.init_mouse_x -= context.region.width

        elif event.mouse_region_x < 1:
            bpy.context.window.cursor_warp(event.mouse_x + context.region.width - 2, event.mouse_y)
            self.init_mouse_x += context.region.width

    if y:
        if event.mouse_region_y > context.region.height - 2:
            bpy.context.window.cursor_warp(event.mouse_x, event.mouse_y - context.region.height + 2)
            self.init_mouse_y -= context.region.height

        elif event.mouse_region_y < 1:
            bpy.context.window.cursor_warp(event.mouse_x, event.mouse_y + context.region.height - 2)
            self.init_mouse_y += context.region.height


def negate_string(floatstring):
    if floatstring.startswith("-"):
        return floatstring[1:]
    else:
        return "-" + floatstring
