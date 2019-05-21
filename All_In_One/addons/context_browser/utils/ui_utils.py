import bpy
from ..addon import ic, uprefs_eid

SEPARATOR_SCALE_Y = 11 / 18


def tag_redraw(all=False):
    wm = bpy.context.window_manager
    if not wm:
        return

    for w in wm.windows:
        for a in w.screen.areas:
            if all or a.type == uprefs_eid() or not a.type:
                for r in a.regions:
                    if all or r.type == 'WINDOW':
                        r.tag_redraw()


def operator(
        layout, bl_idname, text_="", icon_='NONE',
        emboss_=True, icon_value_=0,
        **kwargs):
    properties = layout.operator(
        bl_idname, text=text_, icon=ic(icon_),
        emboss=emboss_, icon_value=icon_value_)

    for k, v in kwargs.items():
        setattr(properties, k, v)

    return properties


def split(layout, factor=None, align=False):
    if bpy.app.version < (2, 80, 0):
        return layout.split(align=align) if factor is None else \
            layout.split(percentage=factor, align=align)

    return layout.split(align=align) if factor is None else \
        layout.split(factor=factor, align=align)

