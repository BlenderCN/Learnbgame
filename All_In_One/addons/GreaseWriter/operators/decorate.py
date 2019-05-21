import bpy
import math
import numpy as np
from .utils import draw_glyph
from .utils import process_stroke_verts_linearly

def ellipse(t, a, b):
    return [a * math.cos(t), b * math.sin(t), 0]


def ellipse_points(origin_x, origin_y, a, b, count=100):
    """
    Return the points that make up an ellipse with radii of a & b
    """
    points = []
    for t in np.linspace(0, 2 * math.pi, count):
        points.append(ellipse(t, a, b))
    for point in points:
        point[0] += origin_x
        point[1] += origin_y
    return points


def get_glyph_size(gpencil):
    """
    Get the size of a grease_pencil object
    """
    layer = gpencil.layers[0]
    frame = layer.frames[-1]

    x_points = []
    y_points = []
    for stroke in frame.strokes:
        for point in stroke.points:
            x_points.append(point.co.x)
            y_points.append(point.co.y)

    min_x = min(x_points)
    max_x = max(x_points)

    min_y = min(y_points)
    max_y = max(y_points)

    return min_x, max_x, min_y, max_y


class GREASEPENCIL_OT_decorate(bpy.types.Operator):
    bl_label = "Decorate"
    bl_idname = "grease_writer.decorate"
    bl_description = "Decorates the selected grease pencil layer"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        obj = bpy.context.view_layer.objects.active
        gpencil = obj.data
        if (len(gpencil.layers) > 0 and
            len(gpencil.layers[0].frames) > 0):
                return True
        else:
            return False

    def execute(self, context):
        scene = context.scene

        obj = bpy.context.view_layer.objects.active
        gpencil = obj.data

        obj_name = obj.name
        speed = scene.gw_speed
        thickness = scene.gw_thickness
        line_height = scene.gw_line_height

        color = scene.gw_color

        left, right, bottom, top = get_glyph_size(gpencil)
        width = right - left
        height = top - bottom

        style = gpencil.decorator_style

        glyph_strokes = []

        padding_fac = 0.125

        origin_x = (width / 2) + left
        origin_y = (height / 2) + bottom

        if style == "underline":
            v1 = [left - (line_height * padding_fac * 2) - origin_x, bottom - (line_height * padding_fac * 2) - origin_y, 0]
            v2 = [right + (line_height * padding_fac * 2) - origin_x, bottom - (line_height * padding_fac * 2) - origin_y, 0]
            glyph_strokes.append([v1, v2])

        elif style == "over-underline":
            v1 = [left - (line_height * padding_fac * 2) - origin_x, top + (line_height * padding_fac * 2) - origin_y, 0]
            v2 = [right + (line_height * padding_fac * 2) - origin_x, top + (line_height * padding_fac * 2) - origin_y, 0]
            glyph_strokes.append([v1, v2])

            v1 = [left - (line_height * padding_fac * 2) - origin_x, bottom - (line_height * padding_fac * 2) - origin_y, 0]
            v2 = [right + (line_height * padding_fac * 2) - origin_x, bottom - (line_height * padding_fac * 2) - origin_y, 0]
            glyph_strokes.append([v1, v2])

        elif style == "x-out":
            v1 = [left - (line_height * padding_fac * 2) - origin_x, top + (line_height * padding_fac * 2) - origin_y, 0]
            v2 = [right + (line_height * padding_fac * 2) - origin_x, top + (line_height * padding_fac * 2) - origin_y, 0]
            v3 = [right + (line_height * padding_fac * 2) - origin_x, bottom - (line_height * padding_fac * 2) - origin_y, 0]
            v4 = [left - (line_height * padding_fac * 2) - origin_x, bottom - (line_height * padding_fac * 2) - origin_y, 0]
            glyph_strokes.append([v1, v3])
            glyph_strokes.append([v2, v4])

        elif style == "strike-through":
            v1 = [left - (line_height * padding_fac * 2) - origin_x, bottom + (height / 2) - origin_y, 0]
            v2 = [right + (line_height * padding_fac * 2) - origin_x, bottom + (height / 2) - origin_y, 0]
            glyph_strokes.append([v1, v2])

        elif style == "box":
            v1 = [left - (line_height * padding_fac * 2) - origin_x, top + (line_height * padding_fac * 2) - origin_y, 0]
            v2 = [right + (line_height * padding_fac * 2) - origin_x, top + (line_height * padding_fac * 2) - origin_y, 0]
            v3 = [right + (line_height * padding_fac * 2) - origin_x, bottom - (line_height * padding_fac * 2) - origin_y, 0]
            v4 = [left - (line_height * padding_fac * 2) - origin_x, bottom - (line_height * padding_fac * 2) - origin_y, 0]
            glyph_strokes.append([v1, v2, v3, v4, v1])

        elif style == "ellipse":
            w_fac = height / width
            h_fac = width / height

            a = (width / 2) + (width * (padding_fac * 3) * w_fac)
            b = (height / 2) + (height * (padding_fac * 3) * h_fac)
            glyph_strokes.append(ellipse_points(0, 0, a, b))

        elif style == "circle":
            if width > height:
                longer = width
            elif height > width:
                longer = height
            a = (longer / 2) + (longer * padding_fac)
            b = (longer / 2) + (longer * padding_fac)
            glyph_strokes.append(ellipse_points(0, 0, a, b))

        elif style == "helioid":
            if width > height:
                w_fac = height / width
                h_fac = width / height
            a = (width / 2) + (width * (padding_fac * 3) * w_fac)
            b = (height / 2) + (height * (padding_fac * 3) * h_fac)
            glyph_strokes.append(ellipse_points(0, 0, a, b))

            longer = max([a, b])

            starts = ellipse_points(0, 0, a * (1 + padding_fac * 2), b * (1 + padding_fac * 2), count=12)
            ends = ellipse_points(0, 0, a * (1 + padding_fac * 2) + (longer / 3), b * (1 + padding_fac * 2) + (longer / 3), count=12)

            for i in range(len(starts)):
                glyph_strokes.append([starts[i], ends[i]])


        last_point = gpencil.layers[0].frames[-1].strokes[-1].points[-1]
        last_vert = [last_point.co.x, last_point.co.y, 0]
        new_vert = glyph_strokes[0][0]
        count = len(process_stroke_verts_linearly([last_vert, new_vert], speed)) - 1

        bpy.context.scene.frame_current = gpencil.layers[0].frames[-1].frame_number + count

        new_gpencil = bpy.data.grease_pencil.new('gpencil')
        color = scene.gw_color
        new_mat = bpy.data.materials.new('decorator')
        bpy.data.materials.create_gpencil_data(new_mat)
        new_mat.grease_pencil.color[0] = color[0]
        new_mat.grease_pencil.color[1] = color[1]
        new_mat.grease_pencil.color[2] = color[2]

        new_obj = bpy.data.objects.new(obj_name + '_' + style, new_gpencil)
        bpy.context.scene.collection.objects.link(new_obj)
        bpy.context.view_layer.objects.active = new_obj
        new_obj.select_set(True)

        new_obj.data.materials.append(new_mat)

        new_obj.location[0] = origin_x
        new_obj.location[1] = origin_y

        new_obj.empty_display_size = 0.2
        new_obj.parent = obj

        draw_glyph(new_obj, glyph_strokes)

        return {"FINISHED"}
