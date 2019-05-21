# --------------------------------------------------------------------------
# Copyright (C) 2015: Martin Froehlich (maybites.ch), Matthew Ready (craxic.com)
#
# based on code from the defunct export script by jm soler, jmsoler_at_free.fr
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# --------------------------------------------------------------------------

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.types import BezierSplinePoint

XML_HEADER = """<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20010904//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
<svg width="{0}mm" height="{1}mm"  viewBox="0 0 {0} {1}" xmlns="http://www.w3.org/2000/svg">
    <title>Bezier Curve : {2}</title>
    <desc>This is an exported Bezier xml_path from Blender, using the ExportScript by maybites.ch and Craxic</desc>
"""
XML_PATH = """<path style="fill:none;stroke:#000000;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1" d="{}"/>
"""
XML_END = "</svg>"

MOVE_COMMAND = 'M{},{} '
LINE_COMMAND = 'L{},{} '
CURVE_COMMAND = 'C{},{} {},{} {},{} '
JOIN_COMMAND = 'Z '


class CoordinateContext:
    def __init__(self, min_x, min_y, max_x, max_y):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    def cx(self, x):
        return x - self.min_x

    def cy(self, y):
        return self.max_y - y


def make_curve_command(previous, point, ctx, scale, translation):
    return CURVE_COMMAND.format(
        ctx.cx(previous.handle_right[0] * scale[0] + translation[0]),
        ctx.cy(previous.handle_right[1] * scale[1] + translation[1]),
        ctx.cx(point.handle_left[0] * scale[0] + translation[0]),
        ctx.cy(point.handle_left[1] * scale[1] + translation[1]),
        ctx.cx(point.co[0] * scale[0] + translation[0]),
        ctx.cy(point.co[1] * scale[1] + translation[1]))


def point_str(point, scale, translation):
    if isinstance(point, BezierSplinePoint):
        return "[x: {}, y: {}, z: {},\n" \
               " x: {}, y: {}, z: {},\n" \
               " x: {}, y: {}, z: {}]".format(point.handle_left[0] * scale[0] + translation[0],
                                              point.handle_left[1] * scale[1] + translation[1],
                                              point.handle_left[2] * scale[2] + translation[2],
                                              point.co[0] * scale[0] + translation[0],
                                              point.co[1] * scale[1] + translation[1],
                                              point.co[2] * scale[2] + translation[2],
                                              point.handle_right[0] * scale[0] + translation[0],
                                              point.handle_right[1] * scale[1] + translation[1],
                                              point.handle_right[2] * scale[2] + translation[2])
    else:
        return "[x: {}, y: {}, z: {}]".format(point.co[0] * scale[0] + translation[0],
                                              point.co[1] * scale[1] + translation[1],
                                              point.co[2] * scale[2] + translation[2])


class Exporter(bpy.types.Operator, ExportHelper):
    bl_idname = "export_svg_format.svg"
    bl_label = "Inkscape SVG Exporter"
    bl_options = {'PRESET'}
    filename_ext = ".svg"

    def execute(self, context):
        # Ensure Blender is currently in OBJECT mode to allow data access.
        bpy.ops.object.mode_set(mode='OBJECT')

        # Set the default return state to FINISHED
        result = {'FINISHED'}

        # Check that the currently selected object contains mesh data for
        # exporting
        curve = bpy.context.selected_objects[0]
        if not curve or curve.type != 'CURVE':
            raise NameError("Cannot export: object %s is not a curve" % curve)

		# this scales from blender to svg (blender 1.0 = 1m while svg 1.0 = 1mm)
        scale = [1000, 1000, 1000]; #curve.dimensions * 1000;

        # consider unit settings
        unit = context.scene.unit_settings
        if unit.system == 'METRIC':
            scale[:] = [s * unit.scale_length for s in scale]
        elif unit.system == 'IMPERIAL':
            self.report({'WARNING'}, "Imperial units not implemented! Scale of output is most probably incorrect!")

        # bound_box[0] == [left, bottom, down]
        # bound_box[7] == [right, top, up]
        # bound_box[i] == [x, y, z], 0 <= i <= 7
        min_x = curve.bound_box[0][0]
        max_x = curve.bound_box[7][0]
        min_y = curve.bound_box[0][1]
        max_y = curve.bound_box[7][1]

        ctx = CoordinateContext(min_x, min_y, max_x, max_y)

		# this calculates the documents size
        width = (max_x - min_x) * scale[0]
        height = (max_y - min_y) * scale[1]

		# this centers the object inside the document
        translation = [- scale[0] * curve.bound_box[0][0], scale[1] * curve.bound_box[0][1], scale[2] * curve.bound_box[0][2]]

        paths = []
        for spline in curve.data.splines:
            path = ""
            if spline.type == 'BEZIER':
                print("Exporting BEZIER curve.")
                first_curve_point = None
                previous = None
                for n, point in enumerate(spline.bezier_points):
                    print("Point: " + point_str(point, scale, translation))

                    if n == 0:
                        first_curve_point = point
                        path += MOVE_COMMAND.format(ctx.cx(point.co[0] * scale[0] + translation[0]),
                                                    ctx.cy(point.co[1] * scale[1] + translation[1]))
                    else:
                        path += make_curve_command(previous, point, ctx, scale, translation)
                    previous = point

                if spline.use_cyclic_u == 1:
                    path += make_curve_command(previous, first_curve_point, ctx, scale, translation)
                    path += JOIN_COMMAND
            elif spline.type == 'POLY':
                print("Exporting POLY curve.")
                for n, point in enumerate(spline.points):
                    command = MOVE_COMMAND if n == 0 else LINE_COMMAND
                    path += command.format(ctx.cx(point.co[0] * scale[0] + translation[0]),
                                           ctx.cy(point.co[1] * scale[1] + translation[1]))
                    print("Point: " + point_str(point, scale, translation))

                if spline.use_cyclic_u == 1:
                    path += JOIN_COMMAND
            paths.append(path)

        # Open the file for writing
        with open(self.filepath, 'w') as f:
            f.write(XML_HEADER.format(width, height, curve.name))
            for path in paths:
                f.write(XML_PATH.format(path))
            f.write(XML_END)

        return result
