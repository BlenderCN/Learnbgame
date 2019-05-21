import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, IntProperty
import bgl
from ... utils.ui import draw_end
from ... utils import MACHIN3 as m3
# import time


class DrawSymmetrize(bpy.types.Operator):
    bl_idname = "machin3.draw_symmetrize"
    bl_label = "MACHIN3: Draw Symmetrize"

    countdown = FloatProperty(default=2)

    alpha = FloatProperty(name="Alpha", default=0.5, min=0.1, max=1)
    pointsize = IntProperty(default=10)
    xray = BoolProperty(name="XRay", default=False)


    def draw_VIEW3D(self, args):
        color = (1, 1, 1)
        alpha = self.countdown / self.time * self.alpha
        pointcolor = (*color, alpha)

        mx = self.active.matrix_world

        # offset amount depends on size of active object
        offset = sum([d for d in self.active.dimensions]) / 3 * 0.001

        bgl.glEnable(bgl.GL_BLEND)

        if self.xray:
            bgl.glDisable(bgl.GL_DEPTH_TEST)

        bgl.glColor4f(*pointcolor)
        bgl.glPointSize(self.pointsize)
        bgl.glBegin(bgl.GL_POINTS)

        for v in self.mirror_verts:
            # bring the coordinates into world space, and push the verts out a bit
            vco = mx * (v.co + v.normal * offset)

            bgl.glVertex3f(*vco)

        draw_end()


    def modal(self, context, event):
        context.area.tag_redraw()

        # FINISH when countdown is 0

        if self.countdown < 0:
            # print("Countdown of %d seconds finished" % (self.time))

            # remove time handler
            context.window_manager.event_timer_remove(self.TIMER)

            # remove draw handlers
            bpy.types.SpaceView3D.draw_handler_remove(self.VIEW3D, 'WINDOW')
            return {'FINISHED'}

        # COUNT DOWN

        if event.type == 'TIMER':
            self.countdown -= 0.1

        return {'PASS_THROUGH'}


    def execute(self, context):
        # self.stopwatch = time.time()

        self.active = m3.get_active()

        # get the verts to draw:
        from .. symmetrize import vertids
        self.mirror_verts = [self.active.data.vertices[idx] for idx in vertids]

        # draw handler
        args = (self, context)
        self.VIEW3D = bpy.types.SpaceView3D.draw_handler_add(self.draw_VIEW3D, (args, ), 'WINDOW', 'POST_VIEW')

        # time handler
        self.TIMER = context.window_manager.event_timer_add(0.1, context.window)

        # initial time
        self.time = self.countdown

        context.window_manager.modal_handler_add(self)
        # print("time:", time.time() - self.stopwatch)
        return {'RUNNING_MODAL'}
