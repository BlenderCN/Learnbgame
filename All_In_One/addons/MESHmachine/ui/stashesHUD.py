import bpy
import bgl
import blf
from bpy.app.handlers import persistent
from .. utils.ui import draw_end
from .. utils import MACHIN3 as m3


stashesHUD = None
oldactive = None
oldstasheslen = 0
oldinvalidstasheslen = 0


def draw_stashes_HUD(context, stasheslen, invalidstasheslen):
    if stasheslen > 0 and len(context.selected_objects) > 0:
        width = context.region.width
        height = context.region.height
        # tpanel = context.area.regions[1].width
        # npanel = context.area.regions[3].width

        center = (width) / 2

        color = m3.MM_prefs().modal_hud_color
        invalidcolor = (1, 0.25, 0.25)
        alpha = 0.5
        font = 1
        fontsize = 12

        bgl.glEnable(bgl.GL_BLEND)
        bgl.glColor4f(*color, alpha)

        blf.size(font, fontsize, 72)
        blf.position(font, center - 60, height - 15, 0)
        blf.draw(font, "Stashes:")

        alpha = 1
        bgl.glColor4f(*color, alpha)
        blf.position(font, center, height - 15, 0)
        blf.draw(font, "%d" % (stasheslen))

        if invalidstasheslen:
            alpha = 1
            bgl.glColor4f(*invalidcolor, alpha)
            blf.position(font, center + 20, height - 15, 0)
            blf.draw(font, "%d" % (invalidstasheslen))



@persistent
def scene_update_handler(scene):
    global stashesHUD, oldactive, oldstasheslen, oldinvalidstasheslen

    active = bpy.context.active_object

    if active:
        stasheslen = len(active.MM.stashes)
        invalidstasheslen = sum([not stash.obj for stash in active.MM.stashes])

        if not stashesHUD:
            stashesHUD = bpy.types.SpaceView3D.draw_handler_add(draw_stashes_HUD, (bpy.context, stasheslen, invalidstasheslen), 'WINDOW', 'POST_PIXEL')

        if active != oldactive or stasheslen != oldstasheslen or invalidstasheslen != oldinvalidstasheslen:
            oldactive = active
            oldstasheslen = stasheslen
            oldinvalidstasheslen = invalidstasheslen

            bpy.types.SpaceView3D.draw_handler_remove(stashesHUD, 'WINDOW')
            stashesHUD = bpy.types.SpaceView3D.draw_handler_add(draw_stashes_HUD, (bpy.context, stasheslen, invalidstasheslen), 'WINDOW', 'POST_PIXEL')
    else:
        if stashesHUD:
            bpy.types.SpaceView3D.draw_handler_remove(stashesHUD, 'WINDOW')
            stashesHUD = None
