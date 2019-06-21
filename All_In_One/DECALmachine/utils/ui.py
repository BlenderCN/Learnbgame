import bpy
import blf
import rna_keymap_ui
from . registration import get_prefs


icons = None


def get_icon(name):
    global icons

    if not icons:
        from .. import icons

    return icons[name].icon_id


# HUD DRAWING

def draw_init(self):
    voffset = 20

    self.HUDx = self.mouse_x
    self.HUDy = self.mouse_y + voffset

    self.font_id = 1
    self.offset = 0


def draw_title(self, title, subtitle=None, subtitleoffset=125, HUDcolor=None, HUDalpha=0.5, shadow=True):
    if not HUDcolor:
        # HUDcolor = (1, 1, 1)
        HUDcolor = get_prefs().modal_hud_color
    shadow = (0, 0, 0)

    # scale = 1
    scale = bpy.context.preferences.view.ui_scale * get_prefs().modal_hud_scale

    if shadow:
        blf.color(self.font_id, *shadow, HUDalpha * 0.7)
        blf.position(self.font_id, self.HUDx - 7 + 1, self.HUDy - 1, 0)
        blf.size(self.font_id, int(20 * scale), 72)
        blf.draw(self.font_id, "» " + title)

    blf.color(self.font_id, *HUDcolor, HUDalpha)
    blf.position(self.font_id, self.HUDx - 7, self.HUDy, 0)
    blf.size(self.font_id, int(20 * scale), 72)
    blf.draw(self.font_id, "» " + title)

    if subtitle:
        if shadow:
            blf.color(self.font_id, *shadow, HUDalpha / 2 * 0.7)
            blf.position(self.font_id, self.HUDx - 7 + int(subtitleoffset * scale) + 1, self.HUDy - 1, 0)
            blf.size(self.font_id, int(15 * scale), 72)
            blf.draw(self.font_id, subtitle)

        blf.color(self.font_id, *HUDcolor, HUDalpha / 2)
        blf.position(self.font_id, self.HUDx - 7 + int(subtitleoffset * scale), self.HUDy, 0)
        blf.size(self.font_id, int(15 * scale), 72)
        blf.draw(self.font_id, subtitle)


def draw_prop(self, name, value, offset=0, decimal=2, active=True, HUDcolor=None, prop_offset=120, hint="", hint_offset=200, shadow=True):
    if not HUDcolor:
        # HUDcolor = (1, 1, 1)
        HUDcolor = get_prefs().modal_hud_color
    shadow = (0, 0, 0)

    if active:
        alpha = 1
    else:
        alpha = 0.4

    # scale = 1
    scale = bpy.context.preferences.view.ui_scale * get_prefs().modal_hud_scale

    offset = self.offset + int(offset * scale)
    self.offset = offset


    # NAME
    if shadow:
        blf.color(self.font_id, *shadow, alpha * 0.7)
        blf.position(self.font_id, self.HUDx + int(20 * scale) + 1, self.HUDy - int(20 * scale) - offset - 1, 0)
        blf.size(self.font_id, int(11 * scale), 72)
        blf.draw(self.font_id, name)

    blf.color(self.font_id, *HUDcolor, alpha)
    blf.position(self.font_id, self.HUDx + int(20 * scale), self.HUDy - int(20 * scale) - offset, 0)
    blf.size(self.font_id, int(11 * scale), 72)
    blf.draw(self.font_id, name)


    # VALUE


    # string
    if type(value) is str:
        if shadow:
            blf.color(self.font_id, *shadow, alpha * 0.7)
            blf.position(self.font_id, self.HUDx + int(prop_offset * scale) + 1, self.HUDy - int(20 * scale) - offset - 1, 0)
            blf.size(self.font_id, int(14 * scale), 72)
            blf.draw(self.font_id, value)

        blf.color(self.font_id, *HUDcolor, alpha)
        blf.position(self.font_id, self.HUDx + int(prop_offset * scale), self.HUDy - int(20 * scale) - offset, 0)
        blf.size(self.font_id, int(14 * scale), 72)
        blf.draw(self.font_id, value)

    # bool
    elif type(value) is bool:
        if shadow:
            blf.color(self.font_id, *shadow, alpha * 0.7)
            blf.position(self.font_id, self.HUDx + int(prop_offset * scale) + 1, self.HUDy - int(20 * scale) - offset - 1, 0)
            blf.size(self.font_id, int(14 * scale), 72)
            blf.draw(self.font_id, str(value))

        if value:
            blf.color(self.font_id, 0.5, 1, 0.5, alpha)
        else:
            blf.color(self.font_id, 1, 0.3, 0.3, alpha)

        blf.position(self.font_id, self.HUDx + int(prop_offset * scale), self.HUDy - int(20 * scale) - offset, 0)
        blf.size(self.font_id, int(14 * scale), 72)
        blf.draw(self.font_id, str(value))

    # int
    elif type(value) is int:
        if shadow:
            blf.color(self.font_id, *shadow, alpha * 0.7)
            blf.position(self.font_id, self.HUDx + int(prop_offset * scale) + 1, self.HUDy - int(20 * scale) - offset - 1, 0)
            blf.size(self.font_id, int(20 * scale), 72)
            blf.draw(self.font_id, "%d" % (value))

        blf.color(self.font_id, *HUDcolor, alpha)
        blf.position(self.font_id, self.HUDx + int(prop_offset * scale), self.HUDy - int(20 * scale) - offset, 0)
        blf.size(self.font_id, int(20 * scale), 72)
        blf.draw(self.font_id, "%d" % (value))

    # float
    elif type(value) is float:
        if shadow:
            blf.color(self.font_id, *shadow, alpha * 0.7)
            blf.position(self.font_id, self.HUDx + int(prop_offset * scale) + 1, self.HUDy - int(20 * scale) - offset - 1, 0)
            blf.size(self.font_id, int(16 * scale), 72)
            blf.draw(self.font_id, "%.*f" % (decimal, value))

        blf.color(self.font_id, *HUDcolor, alpha)
        blf.position(self.font_id, self.HUDx + int(prop_offset * scale), self.HUDy - int(20 * scale) - offset, 0)
        blf.size(self.font_id, int(16 * scale), 72)
        blf.draw(self.font_id, "%.*f" % (decimal, value))

    # HINTS

    if get_prefs().modal_hud_hints and hint:
        if shadow:
            blf.color(self.font_id, *shadow, 0.6 * 0.7)
            blf.position(self.font_id, self.HUDx + int(hint_offset * scale) + 1, self.HUDy - int(20 * scale) - offset - 1, 0)
            blf.size(self.font_id, int(11 * scale), 72)
            blf.draw(self.font_id, "%s" % (hint))

        blf.color(self.font_id, *HUDcolor, 0.6)
        blf.position(self.font_id, self.HUDx + int(hint_offset * scale), self.HUDy - int(20 * scale) - offset, 0)
        blf.size(self.font_id, int(11 * scale), 72)
        blf.draw(self.font_id, "%s" % (hint))


# MODAL MOUSE

def wrap_mouse(self, context, event, x=False, y=False):
    if x:
        if event.mouse_region_x > context.region.width - 2:
            context.window.cursor_warp(event.mouse_x - context.region.width + 2, event.mouse_y)
            self.last_mouse_x -= context.region.width

        elif event.mouse_region_x < 1:
            context.window.cursor_warp(event.mouse_x + context.region.width - 2, event.mouse_y)
            self.last_mouse_x += context.region.width

    if y:
        if event.mouse_region_y > context.region.height - 2:
            context.window.cursor_warp(event.mouse_x, event.mouse_y - context.region.height + 2)
            self.last_mouse_y -= context.region.height

        elif event.mouse_region_y < 1:
            context.window.cursor_warp(event.mouse_x, event.mouse_y + context.region.height - 2)
            self.last_mouse_y += context.region.height


# POPUPS

def popup_message(message, title="Info", icon="INFO", terminal=True):
    def draw_message(self, context):
        if isinstance(message, list):
            for m in message:
                self.layout.label(text=m)
        else:
            self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw_message, title=title, icon=icon)

    if terminal:
        if icon == "FILE_TICK":
            icon = "ENABLE"
        elif icon == "CANCEL":
            icon = "DISABLE"
        print(icon, title)

        if isinstance(message, list):
            print(" »", ", ".join(message))
        else:
            print(" »", message)


# LAYOUT DRAWING

def draw_pil_warning(layout, needed="for decal creation"):
    if get_prefs().pil:
        pass

    elif get_prefs().pilrestart:
        box = layout.box()
        column = box.column()

        column.label(text="PIL has been installed. Restart Blender now.", icon='INFO')

    else:
        box = layout.box()
        column = box.column()
        column.label(text="PIL is needed %s. Internet connection required." % (needed), icon_value=get_icon('error'))
        column.operator("machin3.install_pil", text="Install PIL", icon="PREFERENCES")


def draw_keymap_items(kc, name, keylist, layout):
    drawn = False

    for idx, item in enumerate(keylist):
        keymap = item.get("keymap")

        if keymap:
            km = kc.keymaps.get(keymap)

            kmi = None
            if km:
                idname = item.get("idname")

                for kmitem in km.keymap_items:
                    if kmitem.idname == idname:
                        properties = item.get("properties")

                        if properties:
                            if all([getattr(kmitem.properties, name, None) == value for name, value in properties]):
                                kmi = kmitem
                                break

                        else:
                            kmi = kmitem
                            break

            # draw keymap item

            if kmi:
                # multi kmi tools, will share a single box, created for the first kmi
                if idx == 0:
                    box = layout.box()

                # single kmi tools, get their label from the title
                if len(keylist) == 1:
                    label = name.title().replace("_", " ")

                # multi kmi tools, get it from the label tag, while the title is printed once, before the first item
                else:
                    if idx == 0:
                        box.label(text=name.title().replace("_", " "))

                    label = item.get("label")

                row = box.split(factor=0.15)
                row.label(text=label)

                # layout.context_pointer_set("keymap", km)
                rna_keymap_ui.draw_kmi(["ADDON", "USER", "DEFAULT"], kc, km, kmi, row, 0)

                # draw info, if available
                infos = item.get("info", [])
                for text in infos:
                    row = box.split(factor=0.15)
                    row.separator()
                    row.label(text=text, icon="INFO")

                drawn = True
    return drawn
