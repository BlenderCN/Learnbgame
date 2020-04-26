import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, IntProperty
import bgl
from ... utils.ui import draw_end
from ... utils import MACHIN3 as m3
# import time

drawHandlers = []
timeHandlers = []

# NOTE: study How do you remove a draw handler after it's been added?
# ####: maybe its better do create them via  an extra class? does this prevent the issues of them being tied to the operator?


class DrawPlug(bpy.types.Operator):
    bl_idname = "machin3.draw_plug"
    bl_label = "MACHIN3: Draw Plug"

    countdown = FloatProperty(default=2)

    alpha = FloatProperty(name="Alpha", default=0.5, min=0.1, max=1)
    edgewidth = IntProperty(name="Edge Width", default=1, min=1)


    def draw_VIEW3D(self, args):
        color = (1, 1, 1)
        alpha = self.countdown / self.time * self.alpha
        edgecolor = (*color, alpha)

        mx = self.active.matrix_world

        # offset amount depends on size of active object
        offset = sum([d for d in self.active.dimensions]) / 3 / sum([s for s in self.active.scale]) / 3 * 0.001

        bgl.glEnable(bgl.GL_BLEND)

        bgl.glLineWidth(self.edgewidth)
        bgl.glColor4f(*edgecolor)

        # for co1, co2 in self.coords:
        for v1, v2 in self.edges:
            bgl.glBegin(bgl.GL_LINES)

            bgl.glVertex3f(*(mx * (v1.co + v1.normal * offset)))
            bgl.glVertex3f(*(mx * (v2.co + v2.normal * offset)))

            # bgl.glEnd()

        draw_end()


    def modal(self, context, event):
        context.area.tag_redraw()

        # FINISH when countdown is 0

        if self.countdown < 0:
            # print("Countdown of %d seconds finished" % (self.time))

            # remove time handler
            try:
                context.window_manager.event_timer_remove(self.TIMER)
            except:
                pass

            # remove draw handlers
            try:
                bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            except:
                pass

            return {'FINISHED'}

        # COUNT DOWN

        if event.type == 'TIMER':
            self.countdown -= 0.1

        return {'PASS_THROUGH'}


    def execute(self, context):
        self.active = m3.get_active()

        # collect previous draw handerls and attempt to remove them, before adding a new one
        # this seems to prevent crashes when calling draw_plug() frequently in a short time span, as you do when you drag a prop in the redo panel
        global drawHandlers, timeHandlers

        while drawHandlers:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(drawHandlers[0], 'WINDOW')
                drawHandlers.remove(drawHandlers[0])
            except:
                drawHandlers.remove(drawHandlers[0])


        # doing the same for the time handlers prevents a weird bug where if you drag values in the redo panel of Plugs(), the value will jump down once
        # a side effect of this is, the fading wire seems to stick arround occasionally, and doens't fade away until a few objects have been selected, edit mode switches or toggling xray, ssao, etc
        while timeHandlers:
            try:
                context.window_manager.event_timer_remove(timeHandlers[0])
                timeHandlers.remove(timeHandlers[0])
            except:
                timeHandlers.remove(timeHandlers[0])


        # get the edge coords to draw
        from .. plugs import draw_edges

        self.edges = [(self.active.data.vertices[idx1], self.active.data.vertices[idx2]) for idx1, idx2 in draw_edges]

        # draw handler
        args = (self, context)
        self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (args, ), 'WINDOW', 'POST_VIEW')
        drawHandlers.append(self.VIEW3D)

        # time handler
        self.TIMER = context.window_manager.event_timer_add(0.1, context.window)
        timeHandlers.append(self.TIMER)

        # initial time
        self.time = self.countdown

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
