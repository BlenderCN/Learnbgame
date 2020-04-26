import bpy
import bmesh
import gpu
import bgl
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d, region_2d_to_location_3d
from gpu_extras import batch
from mathutils import Vector
from math import cos, sin, pi
import blf
from .multifile import register_class


def screen_space_to_3d(location, distance, context):
    region = context.region
    data = context.space_data.region_3d
    if data.is_perspective:
        vec = region_2d_to_vector_3d(region, data, location)
        origin = region_2d_to_origin_3d(region, data, location, distance)
    else:
        vec = data.view_rotation @ Vector((0, 0, -1))
        origin = region_2d_to_location_3d(region, data, location, -vec * data.view_distance)
    print(origin)
    location = vec * distance + origin
    print(location)
    print(data.view_distance)
    return location


class DrawCallbackPx:
    def __init__(self):
        self.vertices = []
        self.colors = []
        self.text = []
        self.thickness = 2
        self.font_shadow = (0, 0, 0, 0.5)
        self.shader = gpu.shader.from_builtin("2D_FLAT_COLOR")
        self.batch_redraw = False
        self.batch = None
        self.handler = None

    def __call__(self):
        self.draw()

    def add_text(self, text, location, size, color=(0, 0, 0, 1), dpi=72):
        self.text.append((text, location, size, color, dpi))

    def add_circle(self, center, radius, resolution, color=(1, 0, 0, 1)):
        self.batch_redraw = True
        for i in range(resolution):
            line_point_a = (sin(i / resolution * 2 * pi) * radius + center[0],
                            cos(i / resolution * 2 * pi) * radius + center[1])
            line_point_b = (sin((i + 1) / resolution * 2 * pi) * radius + center[0],
                            cos((i + 1) / resolution * 2 * pi) * radius + center[1])
            self.add_line(line_point_a, line_point_b, color)

    def add_line(self, point_a, point_b, color_a=(1, 0, 0, 1), color_b=None):
        self.batch_redraw = True
        self.vertices.append(point_a)
        self.vertices.append(point_b)
        self.colors.append(color_a)
        self.colors.append(color_b if color_b else color_a)

    def remove_last_line(self):
        self.vertices.pop(-1)
        self.vertices.pop(-1)

    def remove_last_text(self):
        self.text.pop(-1)

    def clear(self):
        self.vertices.clear()
        self.colors.clear()
        self.text.clear()

    def update_batch(self):
        self.batch_redraw = False
        self.batch = batch.batch_for_shader(self.shader, "LINES",
                                                       {"pos": self.vertices, "color": self.colors})

    def setup_handler(self):
        self.handler = bpy.types.SpaceView3D.draw_handler_add(self, (), "WINDOW", "POST_PIXEL")

    def remove_handler(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.handler, "WINDOW")

    def draw(self):
        bgl.glEnable(bgl.GL_BLEND)
        if self.batch_redraw or not self.batch:
            self.update_batch()
        bgl.glLineWidth(self.thickness)
        self.shader.bind()
        self.batch.draw(self.shader)
        bgl.glLineWidth(1)

        for text, location, size, color, dpi in self.text:
            blf.position(0, location[0], location[1], 0)
            blf.size(0, size, dpi)
            blf.color(0, *color)
            blf.shadow(0, 3, *self.font_shadow)
            blf.draw(0, text)

        bgl.glDisable(bgl.GL_BLEND)


@register_class
class Slash(bpy.types.Operator):
    bl_idname = "sculpt_tool_kit.slash"
    bl_label = "Slash Cuter"
    bl_description = "Draw lines to slice"
    bl_options = {"REGISTER", "UNDO"}
    last_location = None
    _timer = None
    _points = []

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == "MESH"

    def invoke(self, context, event):
        self._points = []
        self.draw_callback_px = DrawCallbackPx()
        self.draw_callback_px.setup_handler()
        self.left = False
        self.right = False
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):

        if event.type == "LEFTMOUSE":
            self.left = True if event.value == "PRESS" else False
        if event.type == "LEFTMOUSE":
            self.right = True if event.value == "PRESS" else False

        wire_color = list(context.preferences.themes['Default'].view_3d.wire) + [1]
        active_color = list(context.preferences.themes['Default'].view_3d.object_active) + [1]
        seam_color = list(context.preferences.themes['Default'].view_3d.edge_seam) + [1]
        confirm_distance = 20
        mouse_location = Vector((event.mouse_region_x, event.mouse_region_y, 0)).to_2d()
        distance = float("+inf")
        if self._points:
            distance = (mouse_location - self._points[-1]).length
        fade = max(0, min(1, 1 - (distance / confirm_distance) ** 2))

        # handle orthogonal mode
        if event.ctrl and self._points:
            delta = mouse_location - self._points[-1]
            vecs = [Vector((x, y)).to_2d().normalized() for x in (-1, 0, 1) for y in (-1, 0, 1) if abs(x) + abs(y) != 0]
            best = max((delta.project(vec) for vec in vecs), key=lambda v: v.length_squared)
            mouse_location = best + self._points[-1]

        # If click, add a point
        if self.right and not distance < confirm_distance:
            self._points.append(mouse_location)
            return {"RUNNING_MODAL"}

        # handle undo
        elif event.type == "Z" and event.value == "PRESS" and event.ctrl and not event.shift:
            if self._points:
                self._points.pop(-1)
            return {"RUNNING_MODAL"}

        # handle drawing
        elif event.type in {"LEFTMOUSE", "MOUSEMOVE"} or event.value in {"PRESS", "RELEASE"}:
            active_line_color = [seam_color[i] * fade + active_color[i] * (1 - fade) for i in range(4)]
            confirm_circle_color = active_line_color.copy()
            confirm_circle_color[3] = fade
            circle_color = active_line_color.copy()
            circle_color[3] = 1 - fade
            text_color = circle_color.copy()
            text_color[3] = fade

            self.draw_callback_px.clear()

            self.draw_callback_px.add_circle(mouse_location, 5, 6, color=circle_color)

            if self._points:
                self.draw_callback_px.add_circle(self._points[-1], 5, 6, color=circle_color)
                self.draw_callback_px.add_line(self._points[-1], mouse_location, color_a=active_line_color)

            for i in range(len(self._points) - 1):
                self.draw_callback_px.add_line(self._points[i], self._points[i + 1], color_a=wire_color)

            if distance < confirm_distance:
                text_location = mouse_location + Vector((5, 5))
                self.draw_callback_px.add_text("Left mouse to confirm", text_location, color=text_color, size=14)
                center = (mouse_location + self._points[-1]) / 2
                self.draw_callback_px.add_circle(center, 10 - distance / 2, 10, color=confirm_circle_color)
            context.area.tag_redraw()

        if event.type in {"RIGHTMOUSE", "ESC"}:
            self.draw_callback_px.remove_handler()
            return {"CANCELLED"}

        elif event.type == "RET" or \
                (event.type == "LEFTMOUSE" and event.value == "PRESS" and distance < confirm_distance):
            self.cut(context)
            self.draw_callback_px.remove_handler()
            return {"FINISHED"}

        return {"PASS_THROUGH"}

    def cut(self, context, thickness=0.0001, distance_multiplier=10):
        origin = screen_space_to_3d((0, 0), 0, context)
        dist = context.region_data.view_distance
        end = context.space_data.clip_end
        bm = bmesh.new()
        last_v1 = None
        last_v2 = None
        for point in self._points:
            p1 = screen_space_to_3d(point, 0.0005, context)
            p2 = screen_space_to_3d(point, dist * distance_multiplier, context)
            v1 = bm.verts.new(p1)
            v2 = bm.verts.new(p2)
            if last_v1 and last_v2:
                bm.faces.new((last_v1, last_v2, v2, v1))
            last_v1, last_v2 = v1, v2
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bmesh.ops.solidify(bm, geom=list(bm.faces), thickness=thickness)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        mesh = bpy.data.meshes.new(name="cuter_mesh")
        bm.to_mesh(mesh)
        cuter = bpy.data.objects.new(name="cuter_object", object_data=mesh)
        context.scene.collection.objects.link(cuter)

        for ob in context.view_layer.objects.selected:
            context.view_layer.objects.active = ob
            md = ob.modifiers.new(type="BOOLEAN", name="Cut")
            md.object = cuter
            md.operation = "DIFFERENCE"
            bpy.ops.object.modifier_apply(modifier=md.name)
            bm = bmesh.new()
            bm.from_mesh(ob.data)
            bmesh.ops.holes_fill(bm, edges=bm.edges)
            bmesh.ops.triangulate(bm, faces=[face for face in bm.faces if len(face.verts) > 4])
            bm.to_mesh(ob.data)
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.mesh.separate(type="LOOSE")
            bpy.ops.object.mode_set(mode="OBJECT")

        bpy.data.objects.remove(cuter)
        bpy.data.meshes.remove(mesh)
