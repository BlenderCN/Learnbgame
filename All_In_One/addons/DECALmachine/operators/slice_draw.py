import bpy
import bgl
import blf
from bpy.props import StringProperty
from . init_base_material import init_base_material
from .. import M3utils as m3


class DrawSlice(bpy.types.Operator):
    bl_idname = "machin3.draw_slice"
    bl_label = "MACHIN3: Draw Slice"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        selection = m3.selected_objects()

        args = (self, context)
        self.handle = bpy.types.SpaceView3D.draw_handler_add(draw_overlays, args, 'WINDOW', 'POST_PIXEL')

        m3.unselect_all("OBJECT")

        self.target = m3.get_active()

        if len(selection) == 1:  # draw mode
            panelsourcemesh = bpy.data.meshes.new(name="panel_source_mesh")
            panelsource = bpy.data.objects.new(name="panel_source", object_data=panelsourcemesh)
            bpy.context.scene.objects.link(panelsource)

            # initialise the target material
            init_base_material([self.target])

            m3.make_active(panelsource)
            panelsource.select = True

            m3.set_mode("EDIT")
            m3.set_mode("VERT")

            bpy.context.scene.tool_settings.snap_element = 'FACE'
            bpy.context.scene.tool_settings.use_snap = True
            bpy.context.space_data.use_occlude_geometry = False

            self.panel = panelsource

            wm = context.window_manager
            wm.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        return {'FINISHED'}

    def modal(self, context, event):
        if event.type == 'TAB':
            m3.select_all("MESH")

            bpy.context.scene.tool_settings.use_snap = False
            m3.set_mode("OBJECT")
            self.target.select = True
            m3.make_active(self.target)

            # either push it manually, or add 'UNDO' to the bl_options(which then also makes an unusable propeties panel available)
            bpy.ops.ed.undo_push(message=self.bl_label)

            bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
            return {'FINISHED'}
        return {'PASS_THROUGH'}


def draw_overlays(self, context):
    region = context.region
    draw_border(self, context)
    draw_text(self, context, text="Decal Slice (Draw)", size=20, x=region.width - 190, y=50)

    if bpy.context.user_preferences.inputs.select_mouse == "LEFT":
        actionmouse = "RMB"
    else:
        actionmouse = "LMB"

    draw_text(self, context, text="Extrude vertices to draw an edge line by pressing 'CTRL' + '%s'" % (actionmouse), size=12, x=region.width - 370, y=30)
    draw_text(self, context, text="Press 'TAB' when done, then 'df' to create the panel strip", size=12, x=region.width - 325, y=13)


def draw_text(self, context, text="ABC123", size=16, x=0, y=0):
    font_id = 0

    blf.position(font_id, x, y, 0)
    bgl.glColor4f(1, 1, 1, 0.75)
    blf.size(font_id, size, 72)
    blf.draw(font_id, text)


def draw_border(self, context):
    region = context.region

    bgl.glEnable(bgl.GL_BLEND)
    bgl.glEnable(bgl.GL_LINE_SMOOTH)
    bgl.glColor4f(1, 1, 1, 0.75)
    lw = 2
    bgl.glLineWidth(lw)

    bgl.glBegin(bgl.GL_LINE_STRIP)
    bgl.glVertex2i(lw, lw)
    bgl.glVertex2i(region.width - lw, lw)
    bgl.glVertex2i(region.width - lw, region.height - lw)
    bgl.glVertex2i(lw, region.height - lw)
    bgl.glVertex2i(lw, lw)
    bgl.glEnd()
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glDisable(bgl.GL_LINE_SMOOTH)
