import bpy
import blf
import bgl
from bpy.props import (
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    StringProperty,
)
from time import time
from .addon import prefs


class Timer:
    def __init__(self, t):
        self.reset(t)

    def update(self):
        t1 = time()
        self.t -= t1 - self.t0
        self.t0 = t1

        return self.t <= 0

    def reset(self, t):
        self.t = t
        self.t0 = time()

    def finished(self):
        return self.t <= 0


class SpaceGroup:
    def __init__(self, bl_type):
        self.type = bl_type
        self.handler = None
        self.bl_timer = None
        self.timer = Timer(1)
        self.text = None
        self.alignment = 'TOP'
        self.offset_x = 10
        self.offset_y = 10
        self.shadow = True


space_groups = dict(
    CLIP_EDITOR = SpaceGroup(bpy.types.SpaceClipEditor),
    CONSOLE = SpaceGroup(bpy.types.SpaceConsole),
    DOPESHEET_EDITOR = SpaceGroup(bpy.types.SpaceDopeSheetEditor),
    FILE_BROWSER = SpaceGroup(bpy.types.SpaceFileBrowser),
    GRAPH_EDITOR = SpaceGroup(bpy.types.SpaceGraphEditor),
    IMAGE_EDITOR = SpaceGroup(bpy.types.SpaceImageEditor),
    INFO = SpaceGroup(bpy.types.SpaceInfo),
    LOGIC_EDITOR = SpaceGroup(bpy.types.SpaceLogicEditor),
    NLA_EDITOR = SpaceGroup(bpy.types.SpaceNLA),
    NODE_EDITOR = SpaceGroup(bpy.types.SpaceNodeEditor),
    OUTLINER = SpaceGroup(bpy.types.SpaceOutliner),
    PROPERTIES = SpaceGroup(bpy.types.SpaceProperties),
    SEQUENCE_EDITOR = SpaceGroup(bpy.types.SpaceSequenceEditor),
    TEXT_EDITOR = SpaceGroup(bpy.types.SpaceTextEditor),
    TIMELINE = SpaceGroup(bpy.types.SpaceTimeline),
    USER_PREFERENCES = SpaceGroup(bpy.types.SpaceUserPreferences),
    VIEW_3D = SpaceGroup(bpy.types.SpaceView3D)
)


class Overlay(bpy.types.PropertyGroup):
    overlay = BoolProperty(
        name="Overlay", default=True)
    size = IntProperty(
        name="Font Size", description="Font size",
        default=18, min=10, max=50, options={'SKIP_SAVE'})
    color = FloatVectorProperty(
        name="Color", description="Color",
        default=(1, 1, 1, 1), subtype='COLOR', size=4, min=0, max=1)
    color2 = FloatVectorProperty(
        name="Color", description="Secondary color",
        default=(1, 1, 0, 1), subtype='COLOR', size=4, min=0, max=1)
    alignment = EnumProperty(
        name="Alignment",
        description="Alignment",
        items=(
            ('TOP', "Top", ""),
            ('TOP_LEFT', "Top Left", ""),
            ('TOP_RIGHT', "Top Right", ""),
            ('BOTTOM', "Bottom", ""),
            ('BOTTOM_LEFT', "Bottom Left", ""),
            ('BOTTOM_RIGHT', "Bottom Right", ""),
        ),
        default='BOTTOM')
    duration = FloatProperty(
        name="Duration (sec)", description="Duration (sec)",
        subtype='TIME', min=1, max=10, default=2, step=10)
    offset_x = IntProperty(
        name="Offset X", description="Offset X",
        subtype='PIXEL', default=10)
    offset_y = IntProperty(
        name="Offset Y", description="Offset Y",
        subtype='PIXEL', default=10)
    shadow = BoolProperty(
        name="Use Shadow", description="Use shadow", default=True)

    def draw(self, layout):
        if not self.overlay:
            layout.prop(self, "overlay", toggle=True)
        else:
            layout = layout.column(True)
            layout.prop(self, "overlay", toggle=True)

            row = layout.split(0.3, True)
            row1 = row.row(True)
            row1.prop(self, "color", "")
            row1.prop(self, "color2", "")
            row1.prop(self, "shadow", "", icon='META_BALL')

            row.prop(self, "size")
            row.prop(self, "duration")

            row = layout.split(0.3, True)
            row.prop(self, "alignment", "")
            row.prop(self, "offset_x")
            row.prop(self, "offset_y")


class Table():
    def __init__(self, text, space):
        self.width = 0
        self.height = 0
        self.data = data = []
        self.border_x = 10
        self.border_y = 4

        rows = text.split("\n")
        if "BOTTOM" in space.alignment:
            rows.reverse()

        for i, row in enumerate(rows):
            blf.size(0, round(space.size * (1.3 if i == 0 else 1)), 72)
            row_w, row_h = 0, 0
            data.append([0, 0, 0])
            cells = row.split("\t")
            cell_x = 0
            for j, cell in enumerate(cells):
                w, h = blf.dimensions(0, cell)
                row_w += w
                row_h = max(row_h, h)
                data[i].append(cell)
                data[i].append(w)
                data[i].append(cell_x)
                cell_x += w
                if j > 0:
                    cell_x += self.border_x
                    row_w += self.border_x

            data[i][0] = row_w
            data[i][1] = row_h
            data[i][2] = (0 if "BOTTOM" in space.alignment else row_h) \
                if i == 0 else data[i - 1][2] + data[i - 1][1] + self.border_y

            self.width = max(self.width, row_w)
            self.height += row_h
            if i > 0:
                self.height += self.border_y

    def size(self, i, j):
        return self.data[i][3 * j + 4]

    def text(self, i, j):
        return self.data[i][3 * j + 3]

    def num_cols(self, i):
        return (len(self.data[i]) - 3) // 3

    def num_rows(self):
        return len(self.data)

    def row_y(self, i):
        return self.data[i][2]

    def col_x(self, i, j):
        row = self.data[i]
        num_cols = self.num_cols(i)
        if num_cols == 1:
            return (self.width - row[3 + 3 * j + 1]) // 2
        elif j == num_cols - 1:
            return self.width - row[3 + 3 * j + 1]
        return row[3 + 3 * j + 2]


def _draw_table(space, table, i, j, r, g, b, a):
    ctx = bpy.context

    if "LEFT" in space.alignment:
        x = space.offset_x + table.col_x(i, j)
    elif "RIGHT" in space.alignment:
        x = ctx.region.width - table.width - space.offset_x + table.col_x(i, j)
    else:
        x = 0.5 * ctx.region.width - 0.5 * table.width + table.col_x(i, j)

    if "TOP" in space.alignment:
        y = ctx.region.height - space.offset_y - table.row_y(i)
    else:
        y = space.offset_y + table.row_y(i)

    blf.position(0, x, y, 0)
    blf.size(0, round(space.size * (1.3 if i == 0 else 1)), 72)
    bgl.glColor4f(r, g, b, a)
    blf.draw(0, table.text(i, j))


def _draw_text(space):
    p = 1 if space.timer.t >= 0.3 else space.timer.t / 0.3

    if space.shadow:
        blf.enable(0, blf.SHADOW)
        blf.shadow_offset(0, 1, -1)

    if space.text:
        table = Table(space.text, space)

        for i in range(0, table.num_rows()):
            for j in range(0, table.num_cols(i)):
                r, g, b, a = space.color if j % 2 == 0 else space.color2
                if space.shadow:
                    blf.shadow(0, 5, 0.0, 0.0, 0.0, a * 0.4 * p)
                _draw_table(space, table, i, j, r, g, b, a * p)

    blf.disable(0, blf.SHADOW)


class SUV_OT_overlay(bpy.types.Operator):
    bl_idname = "suv.overlay"
    bl_label = ""
    bl_options = {'INTERNAL'}

    is_running = False

    text = StringProperty(options={'SKIP_SAVE'}, maxlen=1024)

    def modal(self, context, event):
        if event.type == 'TIMER':
            num_handlers = 0
            active_areas = set()
            for name, space in space_groups.items():
                if not space.handler:
                    continue

                active_areas.add(name)

                if space.timer.update():
                    space.type.draw_handler_remove(
                        space.handler, 'WINDOW')
                    space.handler = None
                else:
                    num_handlers += 1

            for area in context.screen.areas:
                if area.type in active_areas:
                    area.tag_redraw()

            if not num_handlers:
                context.window_manager.event_timer_remove(self.timer)
                self.timer = None
                SUV_OT_overlay.is_running = False
                return {'FINISHED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        if context.area.type not in space_groups:
            return {'CANCELLED'}

        pr = prefs()

        if not pr.overlay.overlay:
            return {'CANCELLED'}

        space = space_groups[context.area.type]
        space.timer.reset(pr.overlay.duration)
        space.text = self.text
        space.size = pr.overlay.size
        space.alignment = pr.overlay.alignment
        space.offset_x = pr.overlay.offset_x
        space.offset_y = pr.overlay.offset_y
        space.shadow = pr.overlay.shadow
        space.color = list(pr.overlay.color)
        space.color2 = list(pr.overlay.color2)

        if space.handler:
            return {'CANCELLED'}

        space.handler = space.type.draw_handler_add(
            _draw_text, (space,), 'WINDOW', 'POST_PIXEL')

        if not SUV_OT_overlay.is_running:
            SUV_OT_overlay.is_running = True
            context.window_manager.modal_handler_add(self)
            self.timer = context.window_manager.event_timer_add(
                0.1, bpy.context.window)

        return {'RUNNING_MODAL'}
