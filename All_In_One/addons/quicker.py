#
# Copyright 2018 rn9dfj3
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import bpy
import bgl
import math
from bpy.props import IntProperty, BoolProperty
from bpy.props import PointerProperty, FloatProperty
from bpy.props import FloatVectorProperty, EnumProperty
from bpy_extras.view3d_utils import region_2d_to_location_3d

bl_info = {
    "name": "Quicker",
    "author": "rn9dfj3",
    "version": (0, 1),
    "blender": (2, 79, 0),
    "location": "3D View > Object Mode > Tools > Create",
    "description": "Draw curve quick!",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/rn9dfj3/quicker/wiki",
    "tracker_url": "https://github.com/rn9dfj3/quicker/issues",
    "category": "Add Curve"
}
PI = math.pi
PI_H = PI * 0.5
PEN = "pen"
STAR = "star"
RECT = "rect"
CIRCLE = "circle"
DROPPER = "dropper"


def draw_pen_px(self, context):
    if len(self.strokes) < 1:
        return
    bgl.glEnable(bgl.GL_BLEND)
    width = context.scene.quicker_props.bevel_depth
    tool_setting = context.scene.tool_settings
    rad = 5 * tool_setting.curve_paint_settings.radius_max * width * 10
    pre = [stroke for stroke in self.strokes]
    a = []
    a.append(self.strokes[0])
    a.extend(pre)
    pre = a
    bgl.glLineWidth(1)
    bgl.glColor4f(0.75, 0.75, 0.75, 1.0)
    bgl.glBegin(bgl.GL_LINE_STRIP)
    for n, stroke in enumerate(self.strokes):  # Size line
        x, y = stroke["mouse"]
        pres = stroke["pressure"]
        p = pre[n]
        px, py = p["mouse"]
        ang = math.atan2(y - py, x - px)
        pos = ang + PI_H
        x = x + math.cos(pos) * rad * pres
        y = y + math.sin(pos) * rad * pres
        bgl.glVertex2i(int(x), int(y))
    bgl.glEnd()
    bgl.glBegin(bgl.GL_LINE_STRIP)
    for n, stroke in enumerate(self.strokes):  # Size line
        x, y = stroke["mouse"]
        pres = stroke["pressure"]
        p = pre[n]
        px, py = p["mouse"]
        ang = math.atan2(y - py, x - px)
        neg = ang - PI_H
        x = x + math.cos(neg) * rad * pres
        y = y + math.sin(neg) * rad * pres
        bgl.glVertex2i(int(x), int(y))
    bgl.glEnd()
    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


def draw_star_px(self, context):
    if len(self.strokes) < 2:
        return
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glLineWidth(1)
    bgl.glColor4f(0.75, 0.75, 0.75, 1.0)
    bgl.glBegin(bgl.GL_LINE_STRIP)
    sx, sy = self.strokes[0]["mouse"]
    ex, ey = self.strokes[-1]["mouse"]
    o = math.atan2(ey-sy, ex-sx)
    m = 5.0
    for n in range(int(m) + 1):
        ang = 2 * PI/m * n
        rad = math.sqrt((ex - sx) ** 2 + (ey - sy) ** 2)
        x = rad * math.cos(ang + o) + sx
        y = rad * math.sin(ang + o) + sy
        bgl.glVertex2i(int(x), int(y))
    bgl.glEnd()
    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


def draw_rect_px(self, context):
    if len(self.strokes) < 2:
        return
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glLineWidth(1)
    bgl.glColor4f(0.75, 0.75, 0.75, 1.0)
    bgl.glBegin(bgl.GL_LINE_STRIP)
    sx, sy = self.strokes[0]["mouse"]
    ex, ey = self.strokes[-1]["mouse"]
    bgl.glVertex2i(int(sx), int(sy))
    bgl.glVertex2i(int(sx), int(ey))
    bgl.glVertex2i(int(ex), int(ey))
    bgl.glVertex2i(int(ex), int(sy))
    bgl.glVertex2i(int(sx), int(sy))
    bgl.glEnd()
    #  restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


class QuickerProps(bpy.types.PropertyGroup):
    running = BoolProperty(options={'HIDDEN'})
    mode_items = [
        (PEN, "Pen", "Freehand pen", "GREASEPENCIL", 0),
        (STAR, "Star", "Star", "SOLO_ON", 1),
        (RECT, "Rect", "Rectangle", "MESH_PLANE", 2),
        (CIRCLE, "Circle", "Circle", "MESH_CIRCLE", 3),
        (DROPPER, "Dropper", "Dropper", "EYEDROPPER", 4)
        # ("camera", "Camera", "Camera","CAMERA_DATA", 2)
    ]
    mode = EnumProperty(items=mode_items,
                        name="", description="Draw mode",
                        default="pen")
    color = FloatVectorProperty(name="Color",
                                description="Color of curve",
                                subtype='COLOR', min=0.0,
                                max=1.0, default=(0.8, 0.8, 0.8))
    bevel_depth = FloatProperty(name="Width",
                                description="Width of curve",
                                min=0.0, default=0.1, unit="LENGTH")
    fill = BoolProperty(name="Fill",
                        description="Whether curve is fill or not")
    star_num = IntProperty(name="Number",
                           description="Corner number of star",
                           min=2, default=5)
    star_depth = FloatProperty(name="Depth",
                               description="Corner depth of star",
                               min=0.0, default=0.5, max=1.0, subtype="FACTOR")
    pen_smooth = FloatProperty(name="Smooth",
                               description="How smooth curve is",
                               default=0.1, min=0.0, max=10.0)
    shadeless = BoolProperty(name="Shadelss",
                             description="Whether curve is shadelss or not",
                             default=True)


class DrawCurve(bpy.types.Operator):
    bl_idname = "curve.quicker_draw_curve"
    bl_label = "Draw Curve Object"
    bl_description = "Draw Curve Object"
    bl_options = {'REGISTER', 'UNDO'}
    cursor = FloatVectorProperty(options={'HIDDEN'})
    mani = BoolProperty(options={'HIDDEN'})
    outline = BoolProperty(options={'HIDDEN'})
    strokes = []
    _handle = None

    def execute(self, context):
        props = context.scene.quicker_props
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=True,
                                                 view_align=True)
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.delete(type='VERT')
        context.object.data.dimensions = '2D'
        if not props.fill:
            context.object.data.fill_mode = 'NONE'
        context.object.data.bevel_depth = props.bevel_depth
        context.object.data.resolution_u = 24
        mat = bpy.data.materials.new('Material')
        context.object.data.materials.append(mat)
        mat.use_shadeless = props.shadeless
        mat.diffuse_color = props.color
        context.space_data.cursor_location = self.cursor
        strokes = [{"name": "", "location": stroke["location"],
                    "mouse": stroke["mouse"], "pressure": stroke["pressure"],
                    "pen_flip": False, "time": 0,
                    "is_start": False, "size": 0} for stroke in self.strokes]
        if bpy.ops.curve.draw.poll() and len(strokes) > 0:
            bpy.ops.curve.draw(error_threshold=props.pen_smooth,
                               stroke=strokes, use_cyclic=props.fill)
        self.strokes = []
        tool_setting = context.scene.tool_settings
        curve_type = tool_setting.curve_paint_settings.curve_type
        if props.fill and not curve_type == 'BEZIER':
            bpy.ops.curve.cyclic_toggle()
        if bpy.ops.object.editmode_toggle.poll():
            bpy.ops.object.editmode_toggle()
        return {'FINISHED'}

    def finish_draw(self, context):
        props = context.scene.quicker_props
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        context.space_data.show_manipulator = self.mani
        props.running = False
        context.space_data.show_outline_selected = self.outline

    def add_draw(self, context, event):
        mouse = (event.mouse_region_x, event.mouse_region_y)
        loc = region_2d_to_location_3d(context.region,
                                       context.space_data.region_3d,
                                       mouse, self.cursor)
        stroke = {"mouse": mouse, "pressure": event.pressure,
                  "location": loc}
        self.strokes.append(stroke)

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type in ("LEFTMOUSE", "RIGHTMOUSE", "MIDDLEMOUSE"):
            x = event.mouse_region_x
            y = event.mouse_region_y
            w = context.region.width
            h = context.region.height
            if event.value == 'PRESS' and (x < 0 or w < x or y < 0 or h < y):
                self.finish_draw(context)
                return {'FINISHED'}
        if event.type == "RIGHTMOUSE":
            if event.value == 'PRESS':
                self.finish_draw(context)
                return {'FINISHED'}
        if event.type == "LEFTMOUSE":
            if event.value == 'PRESS':
                self.add_draw(context, event)
            if event.value == 'RELEASE':
                self.add_draw(context, event)
                self.execute(context)
        if event.type == "MOUSEMOVE":  # Draw stroke
            mod = not (event.ctrl or event.alt or event.shift)
            if event.value == 'PRESS' and mod:
                self.add_draw(context, event)
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        props = context.scene.quicker_props
        if context.area.type == 'VIEW_3D' and not props.running:
            self.cursor = context.space_data.cursor_location
            args = (self, context)
            space = bpy.types.SpaceView3D
            self._handle = space.draw_handler_add(draw_pen_px, args,
                                                  'WINDOW',
                                                  'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            self.strokes = []
            props.running = True
            self.mani = context.space_data.show_manipulator
            context.space_data.show_manipulator = False
            self.outline = context.space_data.show_outline_selected
            context.space_data.show_outline_selected = False
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}


class DrawStar(bpy.types.Operator):
    bl_idname = "curve.quicker_draw_star"
    bl_label = "Draw Star Object"
    bl_description = "Draw Star Object"
    bl_options = {'REGISTER', 'UNDO'}
    cursor = FloatVectorProperty(options={'HIDDEN'})
    mani = BoolProperty(options={'HIDDEN'})
    outline = BoolProperty(options={'HIDDEN'})
    strokes = []
    _handle = None

    def execute(self, context):
        props = context.scene.quicker_props
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=True,
                                                 view_align=True)
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.delete(type='VERT')
        context.object.data.dimensions = '2D'
        context.object.data.bevel_depth = props.bevel_depth
        context.object.data.resolution_u = 24
        if not props.fill:
            context.object.data.fill_mode = 'NONE'
        mat = bpy.data.materials.new('Material')
        context.object.data.materials.append(mat)
        mat.use_shadeless = props.shadeless
        mat.diffuse_color = props.color
        context.space_data.cursor_location = self.cursor
        sx, sy = self.strokes[0]["mouse"]
        ex, ey = self.strokes[-1]["mouse"]
        o = math.atan2(ey-sy, ex-sx)
        m = props.star_num
        d = props.star_depth
        strokes = []
        for n in range(int(m)):
            ang = 2 * PI/m * n
            bet = 2 * PI/m * (n+0.5)
            rad = math.sqrt((ex-sx) ** 2 + (ey-sy) ** 2)
            x = rad * math.cos(ang + o) + sx
            y = rad * math.sin(ang + o) + sy
            mouse = (x, y)
            loc = region_2d_to_location_3d(context.region,
                                           context.space_data.region_3d,
                                           mouse, self.cursor)
            strokes.append({"name": "", "location": loc,
                            "mouse": mouse, "pressure": 1,
                            "pen_flip": False, "time": 0,
                            "is_start": False, "size": 0})
            x = d * rad * math.cos(bet + o) + sx
            y = d * rad * math.sin(bet + o) + sy
            mouse = (x, y)
            loc = region_2d_to_location_3d(context.region,
                                           context.space_data.region_3d,
                                           mouse, self.cursor)
            strokes.append({"name": "", "location": loc,
                            "mouse": mouse, "pressure": 1,
                            "pen_flip": False, "time": 0,
                            "is_start": False, "size": 0})
        if bpy.ops.curve.draw.poll() and len(strokes) > 0:
            bpy.ops.curve.draw(error_threshold=0.0,
                               use_cyclic=True,
                               stroke=strokes)
            tool_setting = context.scene.tool_settings
            if not tool_setting.curve_paint_settings.curve_type == 'BEZIER':
                bpy.ops.curve.cyclic_toggle()
        self.strokes = []
        if bpy.ops.object.editmode_toggle.poll():
            bpy.ops.object.editmode_toggle()
        return {'FINISHED'}

    def finish_draw(self, context):
        props = context.scene.quicker_props
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        context.space_data.show_manipulator = self.mani
        props.running = False
        context.space_data.show_outline_selected = self.outline

    def add_draw(self, context, event):
        mouse = (event.mouse_region_x, event.mouse_region_y)
        loc = region_2d_to_location_3d(context.region,
                                       context.space_data.region_3d,
                                       mouse, self.cursor)
        stroke = {"mouse": mouse, "pressure": event.pressure,
                  "location": loc}
        self.strokes.append(stroke)

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type in ("LEFTMOUSE", "RIGHTMOUSE", "MIDDLEMOUSE"):
            x = event.mouse_region_x
            y = event.mouse_region_y
            w = context.region.width
            h = context.region.height
            if event.value == 'PRESS' and (x < 0 or w < x or y < 0 or h < y):
                self.finish_draw(context)
                return {'FINISHED'}
        if event.type == "RIGHTMOUSE":
            if event.value == 'PRESS':
                self.finish_draw(context)
                return {'FINISHED'}
        if event.type == "LEFTMOUSE":
            if event.value == 'PRESS':
                self.add_draw(context, event)
            if event.value == 'RELEASE':
                self.add_draw(context, event)
                self.execute(context)
        if event.type == "MOUSEMOVE":  # Draw stroke
            mod = not (event.ctrl or event.alt or event.shift)
            if event.value == 'PRESS' and mod:
                self.add_draw(context, event)
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        props = context.scene.quicker_props
        if context.area.type == 'VIEW_3D' and not props.running:
            tool_setting = context.scene.tool_settings
            tool_setting.curve_paint_settings.use_pressure_radius = True
            self.cursor = context.space_data.cursor_location
            args = (self, context)
            space = bpy.types.SpaceView3D
            self._handle = space.draw_handler_add(draw_star_px, args,
                                                  'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            self.strokes = []
            props.running = True
            self.mani = context.space_data.show_manipulator
            context.space_data.show_manipulator = False
            self.outline = context.space_data.show_outline_selected
            context.space_data.show_outline_selected = False
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}


class DrawRect(bpy.types.Operator):
    bl_idname = "curve.quicker_draw_rect"
    bl_label = "Draw Rect Object"
    bl_description = "Draw Rectangle Object"
    bl_options = {'REGISTER', 'UNDO'}
    cursor = FloatVectorProperty(options={'HIDDEN'})
    mani = BoolProperty(options={'HIDDEN'})
    outline = BoolProperty(options={'HIDDEN'})
    strokes = []
    _handle = None

    def execute(self, context):
        props = context.scene.quicker_props
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=True,
                                                 view_align=True)
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.delete(type='VERT')
        context.object.data.dimensions = '2D'
        context.object.data.bevel_depth = props.bevel_depth
        context.object.data.resolution_u = 24
        if not props.fill:
            context.object.data.fill_mode = 'NONE'
        mat = bpy.data.materials.new('Material')
        context.object.data.materials.append(mat)
        mat.use_shadeless = props.shadeless
        mat.diffuse_color = props.color
        context.space_data.cursor_location = self.cursor
        sx, sy = self.strokes[0]["mouse"]
        ex, ey = self.strokes[-1]["mouse"]
        strokes = []
        mouse = (sx, sy)
        loc = region_2d_to_location_3d(context.region,
                                       context.space_data.region_3d,
                                       mouse, self.cursor)
        strokes.append({"name": "",
                        "location": loc, "mouse": mouse,
                        "pressure": 1, "pen_flip": False,
                        "time": 0, "is_start": False, "size": 0})
        mouse = (sx, ey)
        loc = region_2d_to_location_3d(context.region,
                                       context.space_data.region_3d,
                                       mouse, self.cursor)
        strokes.append({"name": "",
                        "location": loc, "mouse": mouse,
                        "pressure": 1, "pen_flip": False,
                        "time": 0, "is_start": False, "size": 0})
        mouse = (ex, ey)
        loc = region_2d_to_location_3d(context.region,
                                       context.space_data.region_3d,
                                       mouse, self.cursor)
        strokes.append({"name": "",
                        "location": loc, "mouse": mouse,
                        "pressure": 1, "pen_flip": False,
                        "time": 0, "is_start": False, "size": 0})
        mouse = (ex, sy)
        loc = region_2d_to_location_3d(context.region,
                                       context.space_data.region_3d,
                                       mouse, self.cursor)
        strokes.append({"name": "",
                        "location": loc, "mouse": mouse,
                        "pressure": 1, "pen_flip": False,
                        "time": 0, "is_start": False, "size": 0})
        if bpy.ops.curve.draw.poll() and len(strokes) > 0:
            bpy.ops.curve.draw(error_threshold=0.0,
                               use_cyclic=True, stroke=strokes)
            tool_setting = bpy.context.scene.tool_settings
            if not tool_setting.curve_paint_settings.curve_type == 'BEZIER':
                bpy.ops.curve.cyclic_toggle()
        self.strokes = []
        if bpy.ops.object.editmode_toggle.poll():
            bpy.ops.object.editmode_toggle()
        return {'FINISHED'}

    def finish_draw(self, context):
        props = context.scene.quicker_props
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        context.space_data.show_manipulator = self.mani
        props.running = False
        context.space_data.show_outline_selected = self.outline

    def add_draw(self, context, event):
        mouse = (event.mouse_region_x, event.mouse_region_y)
        loc = region_2d_to_location_3d(context.region,
                                       context.space_data.region_3d,
                                       mouse, self.cursor)
        stroke = {"mouse": mouse, "pressure": event.pressure, "location": loc}
        self.strokes.append(stroke)

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type in ("LEFTMOUSE", "RIGHTMOUSE", "MIDDLEMOUSE"):
            x = event.mouse_region_x
            y = event.mouse_region_y
            w = context.region.width
            h = context.region.height
            if event.value == 'PRESS' and (x < 0 or w < x or y < 0 or h < y):
                self.finish_draw(context)
                return {'FINISHED'}
        if event.type == "RIGHTMOUSE":
            if event.value == 'PRESS':
                self.finish_draw(context)
                return {'FINISHED'}
        if event.type == "LEFTMOUSE":
            if event.value == 'PRESS':
                self.add_draw(context, event)
            if event.value == 'RELEASE':
                self.add_draw(context, event)
                self.execute(context)
        if event.type == "MOUSEMOVE":  # Draw stroke
            mod = not (event.ctrl or event.alt or event.shift)
            if event.value == 'PRESS' and mod:
                self.add_draw(context, event)
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        props = context.scene.quicker_props
        if context.area.type == 'VIEW_3D' and not props.running:
            tool_setting = context.scene.tool_settings
            tool_setting.curve_paint_settings.use_pressure_radius = True
            self.cursor = context.space_data.cursor_location
            args = (self, context)
            space = bpy.types.SpaceView3D
            self._handle = space.draw_handler_add(draw_rect_px, args,
                                                  'WINDOW', 'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            self.strokes = []
            props.running = True
            self.mani = context.space_data.show_manipulator
            context.space_data.show_manipulator = False
            self.outline = context.space_data.show_outline_selected
            context.space_data.show_outline_selected = False
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}


class DrawCircle(bpy.types.Operator):
    bl_idname = "curve.quicker_draw_circle"
    bl_label = "Draw Circle Object"
    bl_description = "Draw Circle Object"
    bl_options = {'REGISTER', 'UNDO'}
    cursor = FloatVectorProperty(options={'HIDDEN'})
    smooth = FloatProperty(name="Smooth",
                           default=0.1, min=0.0, options={'HIDDEN'})
    mani = BoolProperty(options={'HIDDEN'})
    outline = BoolProperty(options={'HIDDEN'})
    strokes = []
    _handle = None

    def execute(self, context):
        props = context.scene.quicker_props
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
        sx, sy = self.strokes[0]["mouse"]
        ex, ey = self.strokes[-1]["mouse"]
        mouse = (sx, sy)
        ori = region_2d_to_location_3d(context.region,
                                       context.space_data.region_3d,
                                       mouse, self.cursor)
        mouse = (ex, ey)
        rad = region_2d_to_location_3d(context.region,
                                       context.space_data.region_3d,
                                       mouse, self.cursor)
        bpy.ops.curve.primitive_bezier_circle_add(radius=(rad - ori).magnitude,
                                                  view_align=True,
                                                  location=ori)
        context.object.data.dimensions = '2D'
        context.object.data.bevel_depth = props.bevel_depth
        context.object.data.resolution_u = 24
        if not props.fill:
            context.object.data.fill_mode = 'NONE'
        mat = bpy.data.materials.new('Material')
        context.object.data.materials.append(mat)
        mat.use_shadeless = props.shadeless
        mat.diffuse_color = props.color
        context.space_data.cursor_location = self.cursor
        self.strokes = []
        return {'FINISHED'}

    def finish_draw(self, context):
        props = context.scene.quicker_props
        bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
        context.space_data.show_manipulator = self.mani
        props.running = False
        context.space_data.show_outline_selected = self.outline

    def add_draw(self, context, event):
        mouse = (event.mouse_region_x, event.mouse_region_y)
        loc = region_2d_to_location_3d(context.region,
                                       context.space_data.region_3d,
                                       mouse, self.cursor)
        stroke = {"mouse": mouse,
                  "pressure": event.pressure, "location": loc}
        self.strokes.append(stroke)

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type in ("LEFTMOUSE", "RIGHTMOUSE", "MIDDLEMOUSE"):
            x = event.mouse_region_x
            y = event.mouse_region_y
            w = context.region.width
            h = context.region.height
            if event.value == 'PRESS' and (x < 0 or w < x or y < 0 or h < y):
                self.finish_draw(context)
                return {'FINISHED'}
        if event.type == "RIGHTMOUSE":
            if event.value == 'PRESS':
                self.finish_draw(context)
                return {'FINISHED'}
        if event.type == "LEFTMOUSE":
            if event.value == 'PRESS':
                self.add_draw(context, event)
            if event.value == 'RELEASE':
                self.execute(context)
        if event.type == "MOUSEMOVE":  # Draw stroke
            mod = not (event.ctrl or event.alt or event.shift)
            if event.value == 'PRESS' and mod:
                self.add_draw(context, event)
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        props = context.scene.quicker_props
        if context.area.type == 'VIEW_3D' and not props.running:
            tool_setting = context.scene.tool_settings
            tool_setting.curve_paint_settings.use_pressure_radius = True
            self.cursor = context.space_data.cursor_location
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_star_px,
                                                                  args,
                                                                  'WINDOW',
                                                                  'POST_PIXEL')
            context.window_manager.modal_handler_add(self)
            self.strokes = []
            props.running = True
            self.mani = context.space_data.show_manipulator
            context.space_data.show_manipulator = False
            self.outline = context.space_data.show_outline_selected
            context.space_data.show_outline_selected = False
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}


class DropColor(bpy.types.Operator):
    bl_idname = "curve.quicker_drop_color"
    bl_label = "Drop Color"
    bl_description = "Drop color to selects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.quicker_props
        objects = context.selected_objects
        for object in objects:
            mat = object.active_material
            if mat is not None:
                mat.diffuse_color = props.color
        return {'FINISHED'}


class DropMaterial(bpy.types.Operator):
    bl_idname = "curve.quicker_drop_material"
    bl_label = "Drop Material"
    bl_description = "Drop material from a active to selects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        objects = context.selected_objects
        active = context.active_object
        source = active.active_material
        if source is None:
            return {'CANCELLED'}
        for object in objects:
            object.active_material = source
        return {'FINISHED'}


class DropBevelDepth(bpy.types.Operator):
    bl_idname = "curve.quicker_drop_bevel_depth"
    bl_label = "Drop Width"
    bl_description = "Drop width to select curves"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.quicker_props
        objects = context.selected_objects
        for object in objects:
            data = object.data
            if isinstance(data, bpy.types.Curve):
                data.bevel_depth = props.bevel_depth
        return {'FINISHED'}


class OBJECT_PT_Quicker(bpy.types.Panel):
    bl_label = "Quicker"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'TOOLS'
    bl_category = "Create"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        props = context.scene.quicker_props
        layout.enabled = not props.running
        layout.prop(props, "mode")
        if props.mode == PEN:
            layout.operator(DrawCurve.bl_idname, text="Draw", icon="PLAY")
            col = layout.column(align=True)
            col.prop(context.scene.tool_settings.curve_paint_settings,
                     "use_pressure_radius")
            col.prop(props, "pen_smooth")
        if props.mode == STAR:
            layout.operator(DrawStar.bl_idname, text="Draw", icon="PLAY")
            col = layout.column(align=True)
            col.prop(props, "star_num")
            col.prop(props, "star_depth")
        if props.mode == RECT:
            layout.operator(DrawRect.bl_idname, text="Draw", icon="PLAY")
        if props.mode == CIRCLE:
            layout.operator(DrawCircle.bl_idname, text="Draw", icon="PLAY")
        if props.mode == DROPPER:
            layout.operator(DropColor.bl_idname, icon="COLOR")
            layout.operator(DropBevelDepth.bl_idname, icon="CURVE_DATA")
            layout.operator(DropMaterial.bl_idname, icon="MATERIAL_DATA")
        layout.separator()
        col = layout.column(align=True)
        col.template_color_picker(props, "color", value_slider=True)
        col.prop(props, "color", text="")
        col.prop(props, "fill")
        col.prop(props, "shadeless")
        col.separator()
        col.prop(context.scene.tool_settings.curve_paint_settings,
                 "curve_type", text="")
        col.prop(props, "bevel_depth")
        layout.separator()
        col = layout.column(align=True)
        col.prop(context.space_data.region_3d, "lock_rotation",
                 text="Lock View")


def register():
    bpy.utils.register_module(__name__)
    sc = bpy.types.Scene
    sc.quicker_props = PointerProperty(
        name="Quicker Props",
        description="Properties for Quicker",
        type=QuickerProps
    )


def unregister():
    del bpy.types.Scene.quicker_props
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
