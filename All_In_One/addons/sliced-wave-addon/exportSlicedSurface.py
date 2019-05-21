import bpy
from bpy_extras.io_utils import ExportHelper
import numpy as np
import random
from math import ceil
from mathutils import Vector

try:
    import generators
except ImportError:
    from . import generators


def number_as_lines(num, w=2, h=4, offset=0.2):
    digits = [int(x) for x in str(num)]

    points = [(0, h), (w, h), (0, h/2), (w, h/2), (0, 0), (w, 0)]
    points = [Vector(p) for p in points]
    edges  = [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5)]
    edge_dict = {0 : [0, 1, 2, 4, 5, 6],
                 1 : [2, 5],
                 2 : [0, 2, 3, 4, 6],
                 3 : [0, 2, 3, 5, 6],
                 4 : [1, 2, 3, 5],
                 5 : [0, 1, 3, 5, 6],
                 6 : [0, 1, 3, 4, 5, 6],
                 7 : [0, 2, 5],
                 8 : [0, 1, 2, 3, 4, 5, 6],
                 9 : [0, 1, 2, 3, 5, 6]}

    number_points, number_edges, idx = [], [], 0
    for k, digit in enumerate(reversed(digits)):
        for edge_idx in edge_dict[digit]:
            edge0, edge1 = edges[edge_idx]
            p0 = points[edge0] - Vector((k*2*w + h, -h))
            p1 = points[edge1] - Vector((k*2*w + h, -h))

            number_points.append(p0*offset + p1*(1 - offset))
            number_points.append(p0*(1 - offset) + p1*offset)
            number_edges.append((idx, idx + 1))
            idx += 2

    return number_points, number_edges


XML_HEADER = """<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="{0}mm" height="{1}mm"  viewBox="0 0 {0} {1}" xmlns="http://www.w3.org/2000/svg">
    <title>Sliced Surface</title>
    <desc>Exported Sliced Surface from Blender</desc>
"""
XML_PATH = """<path style="fill:none;stroke:#000000;stroke-width:0.1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1" d="{}"/>
"""
XML_PATH_NUMBER = """<path style="fill:none;stroke:#FF0000;stroke-width:0.1;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1" d="{}"/>
"""
XML_END = "</svg>"

MOVE_COMMAND = 'M{},{} '
LINE_COMMAND = 'L{},{} '
CURVE_COMMAND = 'C{},{} {},{} {},{} '
JOIN_COMMAND = 'Z '


class ExportSlicedSurfaces(bpy.types.Operator, ExportHelper):
    """Export sliced surface as SVG"""
    bl_idname = 'mesh.export_sliced_surface'
    bl_label = 'Export Sliced Surface'
    bl_options = {'PRESET'}
    filename_ext = ".svg"

    @classmethod
    def poll(self, context):
        return (context.mode == 'OBJECT'
                and (context.active_object is not None)
                and (context.active_object.sliced_surface is not None)
                and context.active_object.sliced_surface.sliced_surface)

    def execute(self, context):
        print('export sliced surface')
        prop = context.object.sliced_surface

        xOffset, yOffset = 2, 2

        random.seed(prop.seed)
        surface = generators.SlicedWaveSurfaceGenerator(numWaves=prop.numWaves,
                                                        maxFreq=prop.maxFreq)

        rows = int((prop.canvasHeight - 2*yOffset) / prop.height)
        cols = int((prop.canvasWidth - 2*xOffset) / prop.width)
        rows = min(rows, int(ceil(prop.nSlices / cols)))
        nSlices = min(rows*cols, prop.nSlices)

        paths = []
        numbers = []
        for nSlice, u in enumerate(np.linspace(0, 1, nSlices, endpoint=True)):
            row, col = int(nSlice / cols), nSlice % cols
            x0, y0 = xOffset + col*prop.width, yOffset + row*prop.height


            path = ""
            for i, v in enumerate(np.linspace(0, 1, prop.nRes, endpoint=True)):
                x = v*prop.width
                y = surface.getValue(u, v, prop.offset)*prop.amplitude + 0.5*prop.height

                if i == 0:
                    path += MOVE_COMMAND.format((x0 + x), (y0 + y))
                else:
                    path += LINE_COMMAND.format((x0 + x), (y0 + y))
            paths.append(path)


            number = ""
            w, h = 0.02*prop.width, 2*0.02*prop.width
            points, edges = number_as_lines(nSlice, w, h)
            for i, (idx0, idx1) in enumerate(edges):
                p0, p1 = points[idx0], points[idx1]

                num_x0 = x0 + p0.x + prop.width
                num_y0 = y0 + (1 - p0.y) + prop.height
                num_x1 = x0 + p1.x + prop.width
                num_y1 = y0 + (1 - p1.y) + prop.height

                number += MOVE_COMMAND.format(num_x0, num_y0)
                number += LINE_COMMAND.format(num_x1, num_y1)
            numbers.append(number)


        for row in range(rows + 1):
            path = MOVE_COMMAND.format(xOffset, yOffset + row*prop.height)
            path += LINE_COMMAND.format(xOffset + cols*prop.width, yOffset + row*prop.height)
            paths.append(path)

        for col in range(cols + 1):
            path = MOVE_COMMAND.format(xOffset + col*prop.width, yOffset)
            path += LINE_COMMAND.format(xOffset + col*prop.width, yOffset + rows*prop.height)
            paths.append(path)

        #path = MOVE_COMMAND.format(0, prop.canvasHeight)
        #path += LINE_COMMAND.format(prop.canvasWidth, prop.canvasHeight)
        #paths.append(path)

        print("Export to : " + self.filepath)
        print("{} slices".format(nSlices))
        with open(self.filepath, 'w') as f:
            f.write(XML_HEADER.format(prop.canvasWidth, prop.canvasHeight))
            for path in paths:
                f.write(XML_PATH.format(path))
            for number in numbers:
                f.write(XML_PATH_NUMBER.format(number))
            f.write(XML_END)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(ExportSlicedSurfaces)
    print('exportSlicedSurface.py registered')

def unregister():
    bpy.utils.unregister_class(ExportSlicedSurfaces)
    print('exportSlicedSurface.py unregistered')
